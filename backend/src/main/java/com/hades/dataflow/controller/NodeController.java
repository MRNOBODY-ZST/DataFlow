package com.hades.dataflow.controller;

import com.hades.dataflow.domain.dto.NodeSchemaDTO;
import com.hades.dataflow.service.NodeSchemaService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Flux;

@RestController
@RequestMapping("/api/nodes")
@RequiredArgsConstructor
public class NodeController {

    private final NodeSchemaService nodeSchemaService;

    @GetMapping("/schema")
    public Flux<NodeSchemaDTO> schema() {
        return Flux.fromIterable(nodeSchemaService.getAll());
    }
}
