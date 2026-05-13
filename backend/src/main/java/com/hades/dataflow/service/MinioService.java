package com.hades.dataflow.service;

import com.hades.dataflow.domain.dto.FileMetadata;
import io.minio.*;
import io.minio.http.Method;
import io.minio.messages.Item;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;
import reactor.core.scheduler.Schedulers;

import java.time.LocalDateTime;
import java.time.ZoneId;
import java.util.concurrent.TimeUnit;

@Slf4j
@Service
@RequiredArgsConstructor
public class MinioService {

    private final MinioClient minioClient;

    @Value("${minio.bucket.input}")
    private String inputBucket;

    @Value("${minio.bucket.output}")
    private String outputBucket;

    @Value("${minio.bucket.temp}")
    private String tempBucket;

    @Value("${minio.presign-expiry-minutes}")
    private int presignExpiryMinutes;

    public Mono<Void> ensureBucketsExist() {
        return Mono.fromCallable(() -> {
            ensureBucket(inputBucket);
            ensureBucket(outputBucket);
            ensureBucket(tempBucket);
            return null;
        }).subscribeOn(Schedulers.boundedElastic()).then();
    }

    private void ensureBucket(String bucket) {
        try {
            boolean exists = minioClient.bucketExists(BucketExistsArgs.builder().bucket(bucket).build());
            if (!exists) {
                minioClient.makeBucket(MakeBucketArgs.builder().bucket(bucket).build());
                log.info("Created MinIO bucket: {}", bucket);
            }
        } catch (Exception e) {
            throw new RuntimeException("Failed to ensure bucket: " + bucket, e);
        }
    }

    public Mono<String> presignedUploadUrl(String bucket, String objectKey) {
        return Mono.fromCallable(() ->
                minioClient.getPresignedObjectUrl(GetPresignedObjectUrlArgs.builder()
                        .method(Method.PUT)
                        .bucket(bucket)
                        .object(objectKey)
                        .expiry(presignExpiryMinutes, TimeUnit.MINUTES)
                        .build())
        ).subscribeOn(Schedulers.boundedElastic());
    }

    public Mono<String> presignedDownloadUrl(String bucket, String objectKey) {
        return Mono.fromCallable(() ->
                minioClient.getPresignedObjectUrl(GetPresignedObjectUrlArgs.builder()
                        .method(Method.GET)
                        .bucket(bucket)
                        .object(objectKey)
                        .expiry(presignExpiryMinutes, TimeUnit.MINUTES)
                        .build())
        ).subscribeOn(Schedulers.boundedElastic());
    }

    public Flux<FileMetadata> listObjects(String bucket, String prefix) {
        return Flux.defer(() -> Flux.fromIterable(
                        minioClient.listObjects(ListObjectsArgs.builder()
                                .bucket(bucket)
                                .prefix(prefix == null ? "" : prefix)
                                .recursive(true)
                                .build())
                ))
                .subscribeOn(Schedulers.boundedElastic())
                .map(result -> toFileMetadata(result, bucket))
                .filter(file -> !file.getKey().endsWith("/"));
    }

    public Mono<FileMetadata> statObject(String bucket, String objectKey) {
        return Mono.fromCallable(() -> {
                    var stat = minioClient.statObject(StatObjectArgs.builder()
                            .bucket(bucket)
                            .object(objectKey)
                            .build());
                    return new FileMetadata(
                            objectKey,
                            stat.size(),
                            LocalDateTime.ofInstant(stat.lastModified().toInstant(), ZoneId.systemDefault()),
                            bucket
                    );
                })
                .subscribeOn(Schedulers.boundedElastic());
    }

    public Mono<Void> deleteObject(String bucket, String objectKey) {
        return Mono.fromRunnable(() -> {
                    try {
                        minioClient.removeObject(RemoveObjectArgs.builder()
                                .bucket(bucket)
                                .object(objectKey)
                                .build());
                    } catch (Exception e) {
                        throw new RuntimeException("Failed to delete object: " + objectKey, e);
                    }
                })
                .subscribeOn(Schedulers.boundedElastic())
                .then();
    }

    private FileMetadata toFileMetadata(Result<Item> result, String bucket) {
        try {
            var item = result.get();
            return new FileMetadata(
                    item.objectName(),
                    item.size(),
                    LocalDateTime.ofInstant(item.lastModified().toInstant(), ZoneId.systemDefault()),
                    bucket
            );
        } catch (Exception e) {
            throw new RuntimeException("Failed to read MinIO object metadata", e);
        }
    }

    public String getInputBucket() { return inputBucket; }
    public String getOutputBucket() { return outputBucket; }
    public String getTempBucket() { return tempBucket; }
}
