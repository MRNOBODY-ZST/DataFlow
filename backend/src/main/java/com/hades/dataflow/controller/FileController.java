package com.hades.dataflow.controller;

import com.hades.dataflow.service.MinioService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;
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
        return minioService.presignedUploadUrl(minioService.getInputBucket(), key)
                .map(url -> Map.of("url", url, "key", key));
    }

    @GetMapping("/presign-download")
    public Mono<Map<String, String>> presignDownload(@RequestParam String key,
                                                      @RequestParam(defaultValue = "output") String bucket) {
        String targetBucket = "output".equals(bucket)
                ? minioService.getOutputBucket()
                : minioService.getInputBucket();
        return minioService.presignedDownloadUrl(targetBucket, key)
                .map(url -> Map.of("url", url));
    }
}
