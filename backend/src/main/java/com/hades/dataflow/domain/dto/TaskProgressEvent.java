package com.hades.dataflow.domain.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class TaskProgressEvent {
    private Long taskId;
    private String nodeId;
    private int progress;       // 0-100
    private String status;      // RUNNING, SUCCESS, FAILED, CANCELLED
    private String message;
    private String outputKey;
}
