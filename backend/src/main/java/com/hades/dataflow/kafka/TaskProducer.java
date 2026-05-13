package com.hades.dataflow.kafka;

import com.hades.dataflow.config.KafkaConfig;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Component;
import reactor.core.publisher.Mono;
import reactor.core.scheduler.Schedulers;

import java.util.Map;

@Slf4j
@Component
@RequiredArgsConstructor
public class TaskProducer {

    private final KafkaTemplate<String, Object> kafkaTemplate;

    public Mono<Void> dispatchTask(Long taskId, Long pipelineId, String graphId) {
        Map<String, Object> payload = Map.of(
                "taskId", taskId,
                "pipelineId", pipelineId,
                "graphId", graphId
        );
        return Mono.fromFuture(() ->
                        kafkaTemplate.send(KafkaConfig.TOPIC_TASK_DISPATCH, taskId.toString(), payload)
                                .toCompletableFuture()
                )
                .subscribeOn(Schedulers.boundedElastic())
                .doOnSuccess(r -> log.info("Dispatched task {} to Kafka", taskId))
                .doOnError(e -> log.error("Failed to dispatch task {}", taskId, e))
                .then();
    }
}
