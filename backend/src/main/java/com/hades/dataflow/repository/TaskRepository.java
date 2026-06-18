package com.hades.dataflow.repository;

import com.hades.dataflow.domain.entity.Task;
import org.springframework.data.repository.reactive.ReactiveCrudRepository;
import reactor.core.publisher.Flux;

public interface TaskRepository extends ReactiveCrudRepository<Task, Long> {
    Flux<Task> findByUserIdOrderByCreatedAtDesc(Long userId);
}
