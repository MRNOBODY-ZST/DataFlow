package com.hades.dataflow.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Data;

import java.time.LocalDateTime;

@Data
@AllArgsConstructor
public class TaskResponse {
    private Long id;
    private Long pipelineId;
    private String status;
    private Integer progress;
    private String inputPath;
    private String outputPath;
    private String errorMsg;
    private LocalDateTime createdAt;
    private LocalDateTime finishedAt;
}
