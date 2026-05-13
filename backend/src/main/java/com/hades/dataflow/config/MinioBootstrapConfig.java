package com.hades.dataflow.config;

import com.hades.dataflow.service.MinioService;
import lombok.RequiredArgsConstructor;
import org.springframework.boot.ApplicationRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
@RequiredArgsConstructor
public class MinioBootstrapConfig {

    private final MinioService minioService;

    @Bean
    public ApplicationRunner minioBootstrapRunner() {
        return args -> minioService.ensureBucketsExist().block();
    }
}
