package com.hades.dataflow.repository;

import com.hades.dataflow.domain.document.PipelineGraph;
import org.springframework.data.mongodb.repository.ReactiveMongoRepository;

public interface PipelineGraphRepository extends ReactiveMongoRepository<PipelineGraph, String> {
}
