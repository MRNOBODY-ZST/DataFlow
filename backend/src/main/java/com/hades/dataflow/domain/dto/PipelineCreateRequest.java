package com.hades.dataflow.domain.dto;

import com.hades.dataflow.domain.document.PipelineGraph;
import lombok.Data;

import java.util.List;

@Data
public class PipelineCreateRequest {
    private String name;
    private String description;
    private List<PipelineGraph.FlowNode> nodes;
    private List<PipelineGraph.FlowEdge> edges;
}
