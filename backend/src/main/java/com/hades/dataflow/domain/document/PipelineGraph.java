package com.hades.dataflow.domain.document;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Document(collection = "pipeline_graphs")
public class PipelineGraph {

    @Id
    private String id;

    private Long pipelineId;

    private List<FlowNode> nodes;

    private List<FlowEdge> edges;

    private int version;

    private LocalDateTime updatedAt;

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class FlowNode {
        private String id;
        private String type;
        private Position position;
        private Map<String, Object> data;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class FlowEdge {
        private String id;
        private String source;
        private String target;
        private String sourceHandle;
        private String targetHandle;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class Position {
        private double x;
        private double y;
    }
}
