package dataflow.utils;

import io.minio.*;
import io.minio.http.Method;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import dataflow.config.MinioConfig;
//import yzzw.pojo.File;

import java.io.InputStream;

@Component
public class MinioUtils {

    public MinioClient minioClient;
    public MinioConfig minioConfig;
    private final String bucketName;


    @Autowired
    private MinioUtils(MinioClient minioClient, MinioConfig minioConfig) {
        this.minioClient = minioClient;
        this.minioConfig = minioConfig;
        bucketName = minioConfig.getBucketName();
    }

//    private String getParentId(String objectName) {
//        //        int lastSlashIndex = objectName.lastIndexOf('/');
//        //        return lastSlashIndex == -1 ? "" : objectName.substring(0, lastSlashIndex);
//        return "0";
//    }

//    public File uploadFile(String objectName, MultipartFile file) throws Exception {
//        minioClient.putObject(
//                PutObjectArgs.builder()
//                        .bucket(bucketName)
//                        .object(objectName)
//                        .stream(file.getInputStream(), file.getSize(), -1)
//                        .contentType(file.getContentType())
//                        .build()
//        );
//
//        StatObjectResponse stat = minioClient.statObject(
//                StatObjectArgs.builder()
//                        .bucket(bucketName)
//                        .object(objectName)
//                        .build()
//        );
//
//        return new File(
//                null,
//                ThreadUtils.getUserId(),
//                getParentId(objectName),
//                bucketName,
//                objectName,
//                stat.etag(),
//                (int) file.getSize(),
//                file.getContentType(),
//                objectName.endsWith("/"),
//                LocalDateTime.now(),
//                LocalDateTime.ofInstant(stat.lastModified().toInstant(), ZoneId.systemDefault()),
//                1
//        );
//    }


    public InputStream downloadFile(String bucketName, String objectName) throws Exception {
        return minioClient.getObject(
                GetObjectArgs.builder()
                        .bucket(bucketName)
                        .object(objectName)
                        .build()
        );
    }

    public String generatePresignedUrl(String bucketName, String objectName) throws Exception {
        return minioClient.getPresignedObjectUrl(
                GetPresignedObjectUrlArgs.builder()
                        .method(Method.GET)
                        .bucket(bucketName)
                        .object(objectName)
                        .expiry(60 * 60) // URL expires in 1 hour
                        .build());
    }

}
