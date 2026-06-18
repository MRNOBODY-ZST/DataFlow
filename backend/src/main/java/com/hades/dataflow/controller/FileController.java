package com.hades.dataflow.controller;

import com.hades.dataflow.domain.dto.FileMetadata;
import com.hades.dataflow.service.MinioService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.util.List;
import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/files")
@RequiredArgsConstructor
public class FileController {

    private final MinioService minioService;

    private Long getUserId(Authentication auth) {
        return (Long) auth.getDetails();
    }

    private String userPrefix(Long userId) {
        return "u/" + userId + "/";
    }

    @PostMapping("/presign-upload")
    public Mono<Map<String, String>> presignUpload(@RequestParam String filename, Authentication auth) {
        String scoped = userPrefix(getUserId(auth)) + filename;
        return minioService.ensureBucketsExist()
                .then(minioService.presignedUploadUrl(minioService.getInputBucket(), scoped))
                .map(url -> Map.of("url", url, "key", scoped));
    }

    @GetMapping("/presign-download")
    public Mono<Map<String, String>> presignDownload(@RequestParam String key,
                                                      @RequestParam(defaultValue = "output") String bucket,
                                                      Authentication auth) {
        String scoped = userPrefix(getUserId(auth)) + key;
        return minioService.presignedDownloadUrl(resolveBucket(bucket), scoped)
                .map(url -> Map.of("url", url));
    }

    @GetMapping
    public Flux<FileMetadata> list(@RequestParam(defaultValue = "input") String bucket,
                                   @RequestParam(defaultValue = "") String prefix,
                                   Authentication auth) {
        String resolvedBucket = resolveBucket(bucket);
        String scopedPrefix = userPrefix(getUserId(auth)) + prefix;
        String strip = userPrefix(getUserId(auth));
        return minioService.ensureBucketsExist()
                .thenMany(minioService.listObjects(resolvedBucket, scopedPrefix)
                        .map(file -> new FileMetadata(
                                file.getKey().substring(strip.length()),
                                file.getSize(), file.getLastModified(), bucket)));
    }

    @GetMapping("/stat")
    public Mono<FileMetadata> stat(@RequestParam String bucket,
                                   @RequestParam String key,
                                   Authentication auth) {
        String resolvedBucket = resolveBucket(bucket);
        String scoped = userPrefix(getUserId(auth)) + key;
        return minioService.ensureBucketsExist()
                .then(minioService.statObject(resolvedBucket, scoped)
                        .map(file -> new FileMetadata(key, file.getSize(), file.getLastModified(), bucket)));
    }

    @DeleteMapping
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public Mono<Void> delete(@RequestParam String bucket,
                             @RequestParam String key,
                             Authentication auth) {
        String scoped = userPrefix(getUserId(auth)) + key;
        return minioService.deleteObject(resolveBucket(bucket), scoped);
    }

    @PostMapping("/move")
    public Mono<Map<String, String>> move(@RequestParam String bucket,
                                          @RequestParam String srcKey,
                                          @RequestParam String destKey,
                                          Authentication auth) {
        if (!"input".equals(bucket)) {
            return Mono.error(new ResponseStatusException(HttpStatus.BAD_REQUEST, "Only input bucket files can be moved"));
        }
        String resolved = resolveBucket(bucket);
        String prefix = userPrefix(getUserId(auth));
        String scopedSrc = prefix + srcKey;
        String scopedDest = prefix + destKey;
        return minioService.copyObject(resolved, scopedSrc, scopedDest)
                .then(minioService.deleteObject(resolved, scopedSrc))
                .thenReturn(Map.of("key", destKey));
    }

    @PostMapping("/batch-move")
    public Flux<Map<String, String>> batchMove(@RequestParam String bucket,
                                               @RequestBody List<Map<String, String>> moves,
                                               Authentication auth) {
        if (!"input".equals(bucket)) {
            return Flux.error(new ResponseStatusException(HttpStatus.BAD_REQUEST, "Only input bucket files can be moved"));
        }
        String resolved = resolveBucket(bucket);
        String prefix = userPrefix(getUserId(auth));
        return Flux.fromIterable(moves)
                .concatMap(m -> {
                    String src = prefix + m.get("srcKey");
                    String dest = prefix + m.get("destKey");
                    return minioService.copyObject(resolved, src, dest)
                            .then(minioService.deleteObject(resolved, src))
                            .thenReturn(Map.of("srcKey", m.get("srcKey"), "destKey", m.get("destKey")));
                });
    }

    private String resolveBucket(String bucket) {
        return switch (bucket) {
            case "input" -> minioService.getInputBucket();
            case "output" -> minioService.getOutputBucket();
            case "temp" -> minioService.getTempBucket();
            default -> throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "Unsupported bucket: " + bucket);
        };
    }
}
