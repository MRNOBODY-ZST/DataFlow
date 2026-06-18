package com.hades.dataflow.controller;

import com.hades.dataflow.domain.dto.PipelineCreateRequest;
import com.hades.dataflow.domain.dto.PipelineResponse;
import com.hades.dataflow.service.PipelineService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

@RestController
@RequestMapping("/api/pipelines")
@RequiredArgsConstructor
public class PipelineController {

    private final PipelineService pipelineService;

    @GetMapping
    public Flux<PipelineResponse> list(Authentication auth) {
        return pipelineService.listByUser(getUserId(auth));
    }

    @GetMapping("/{id}")
    public Mono<PipelineResponse> get(@PathVariable Long id, Authentication auth) {
        return pipelineService.getById(id, getUserId(auth));
    }

    @PostMapping
    public Mono<PipelineResponse> create(@RequestBody PipelineCreateRequest req, Authentication auth) {
        return pipelineService.create(req, getUserId(auth));
    }

    @PutMapping("/{id}")
    public Mono<PipelineResponse> update(@PathVariable Long id,
                                          @RequestBody PipelineCreateRequest req,
                                          Authentication auth) {
        return pipelineService.update(id, req, getUserId(auth));
    }

    @DeleteMapping("/{id}")
    public Mono<Void> delete(@PathVariable Long id, Authentication auth) {
        return pipelineService.delete(id, getUserId(auth));
    }

    private Long getUserId(Authentication auth) {
        return (Long) auth.getDetails();
    }
}
