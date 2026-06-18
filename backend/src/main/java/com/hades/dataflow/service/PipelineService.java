package com.hades.dataflow.service;

import com.hades.dataflow.domain.document.PipelineGraph;
import com.hades.dataflow.domain.dto.PipelineCreateRequest;
import com.hades.dataflow.domain.dto.PipelineResponse;
import com.hades.dataflow.domain.entity.Pipeline;
import com.hades.dataflow.repository.PipelineGraphRepository;
import com.hades.dataflow.repository.PipelineRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class PipelineService {

    private final PipelineRepository pipelineRepository;
    private final PipelineGraphRepository graphRepository;

    public Flux<PipelineResponse> listByUser(Long userId) {
        return pipelineRepository.findByUserId(userId)
                .flatMap(p -> graphRepository.findById(p.getGraphId())
                        .map(g -> toResponse(p, g)));
    }

    public Mono<PipelineResponse> getById(Long id, Long userId) {
        return pipelineRepository.findById(id)
                .switchIfEmpty(Mono.error(new ResponseStatusException(HttpStatus.NOT_FOUND)))
                .filter(p -> p.getUserId().equals(userId))
                .switchIfEmpty(Mono.error(new ResponseStatusException(HttpStatus.FORBIDDEN)))
                .flatMap(p -> graphRepository.findById(p.getGraphId())
                        .map(g -> toResponse(p, g)));
    }

    public Mono<PipelineResponse> create(PipelineCreateRequest req, Long userId) {
        String graphId = UUID.randomUUID().toString();
        PipelineGraph graph = PipelineGraph.builder()
                .id(graphId)
                .nodes(req.getNodes() != null ? req.getNodes() : List.of())
                .edges(req.getEdges() != null ? req.getEdges() : List.of())
                .version(1)
                .updatedAt(LocalDateTime.now())
                .build();

        return graphRepository.save(graph)
                .flatMap(savedGraph -> {
                    Pipeline pipeline = Pipeline.builder()
                            .userId(userId)
                            .name(req.getName())
                            .description(req.getDescription())
                            .graphId(savedGraph.getId())
                            .build();
                    return pipelineRepository.save(pipeline)
                            .map(saved -> toResponse(saved, savedGraph));
                });
    }

    public Mono<PipelineResponse> update(Long id, PipelineCreateRequest req, Long userId) {
        return pipelineRepository.findById(id)
                .switchIfEmpty(Mono.error(new ResponseStatusException(HttpStatus.NOT_FOUND)))
                .filter(p -> p.getUserId().equals(userId))
                .switchIfEmpty(Mono.error(new ResponseStatusException(HttpStatus.FORBIDDEN)))
                .flatMap(pipeline -> graphRepository.findById(pipeline.getGraphId())
                        .flatMap(graph -> {
                            if (req.getNodes() != null) graph.setNodes(req.getNodes());
                            if (req.getEdges() != null) graph.setEdges(req.getEdges());
                            graph.setVersion(graph.getVersion() + 1);
                            graph.setUpdatedAt(LocalDateTime.now());
                            if (req.getName() != null) pipeline.setName(req.getName());
                            if (req.getDescription() != null) pipeline.setDescription(req.getDescription());
                            return graphRepository.save(graph)
                                    .flatMap(savedGraph -> pipelineRepository.save(pipeline)
                                            .map(saved -> toResponse(saved, savedGraph)));
                        }));
    }

    public Mono<Void> delete(Long id, Long userId) {
        return pipelineRepository.findById(id)
                .switchIfEmpty(Mono.error(new ResponseStatusException(HttpStatus.NOT_FOUND)))
                .filter(p -> p.getUserId().equals(userId))
                .switchIfEmpty(Mono.error(new ResponseStatusException(HttpStatus.FORBIDDEN)))
                .flatMap(p -> graphRepository.deleteById(p.getGraphId())
                        .then(pipelineRepository.delete(p)));
    }

    private PipelineResponse toResponse(Pipeline p, PipelineGraph g) {
        return new PipelineResponse(
                p.getId(), p.getName(), p.getDescription(), p.getGraphId(),
                g.getNodes(), g.getEdges(), p.getCreatedAt(), p.getUpdatedAt());
    }
}
