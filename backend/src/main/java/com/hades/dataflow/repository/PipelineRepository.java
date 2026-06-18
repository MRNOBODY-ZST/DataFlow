package com.hades.dataflow.repository;

import com.hades.dataflow.domain.entity.Pipeline;
import org.springframework.data.repository.reactive.ReactiveCrudRepository;
import reactor.core.publisher.Flux;

public interface PipelineRepository extends ReactiveCrudRepository<Pipeline, Long> {
    Flux<Pipeline> findByUserId(Long userId);
}
