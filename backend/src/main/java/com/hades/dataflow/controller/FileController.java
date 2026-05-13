package com.hades.dataflow.controller;

import com.hades.dataflow.domain.dto.FileMetadata;
import com.hades.dataflow.service.MinioService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/files")
@RequiredArgsConstructor
public class FileController {

    private final MinioService minioService;

    @PostMapping("/presign-upload")
    public Mono<Map<String, String>> presignUpload(@RequestParam String filename) {
        String key = "input/" + UUID.randomUUID() + "/" + filename;
        return minioService.ensureBucketsExist()
                .then(minioService.presignedUploadUrl(minioService.getInputBucket(), key))
                .map(url -> Map.of("url", url, "key", key));
    }

    @GetMapping("/presign-download")
    public Mono<Map<String, String>> presignDownload(@RequestParam String key,
                                                      @RequestParam(defaultValue = "output") String bucket) {
        return minioService.presignedDownloadUrl(resolveBucket(bucket), key)
                .map(url -> Map.of("url", url));
    }

    @GetMapping
    public Flux<FileMetadata> list(@RequestParam(defaultValue = "input") String bucket,
                                   @RequestParam(defaultValue = "") String prefix) {
        String resolvedBucket = resolveBucket(bucket);
        return minioService.ensureBucketsExist()
                .thenMany(minioService.listObjects(resolvedBucket, prefix)
                        .map(file -> new FileMetadata(file.getKey(), file.getSize(), file.getLastModified(), bucket)));
    }

    @GetMapping("/stat")
    public Mono<FileMetadata> stat(@RequestParam String bucket,
                                   @RequestParam String key) {
        String resolvedBucket = resolveBucket(bucket);
        return minioService.ensureBucketsExist()
                .then(minioService.statObject(resolvedBucket, key)
                        .map(file -> new FileMetadata(file.getKey(), file.getSize(), file.getLastModified(), bucket)));
    }

    @DeleteMapping
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public Mono<Void> delete(@RequestParam String bucket,
                             @RequestParam String key) {
        if (!"input".equals(bucket)) {
            return Mono.error(new ResponseStatusException(HttpStatus.BAD_REQUEST, "Only input bucket files can be deleted"));
        }
        return minioService.deleteObject(resolveBucket(bucket), key);
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
