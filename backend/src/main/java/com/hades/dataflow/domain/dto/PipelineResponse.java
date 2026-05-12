package com.hades.dataflow.domain.dto;

import com.hades.dataflow.domain.document.PipelineGraph;
import lombok.AllArgsConstructor;
import lombok.Data;

import java.time.LocalDateTime;
import java.util.List;

@Data
@AllArgsConstructor
public class PipelineResponse {
    private Long id;
    private String name;
    private String description;
    private String graphId;
    private List<PipelineGraph.FlowNode> nodes;
    private List<PipelineGraph.FlowEdge> edges;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;
}
