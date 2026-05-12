package com.hades.dataflow.domain.dto;

import lombok.Data;

@Data
public class TaskSubmitRequest {
    private Long pipelineId;
    private String inputKey;
}
