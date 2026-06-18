package com.hades.dataflow.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@AllArgsConstructor
public class FileMetadata {
    private String key;
    private Long size;
    private LocalDateTime lastModified;
    private String bucket;
}
