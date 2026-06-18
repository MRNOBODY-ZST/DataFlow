package com.hades.dataflow.kafka;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.hades.dataflow.config.KafkaConfig;
import com.hades.dataflow.domain.dto.TaskProgressEvent;
import com.hades.dataflow.repository.TaskRepository;
import com.hades.dataflow.service.NotificationService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.ReactiveRedisTemplate;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

import reactor.core.publisher.Mono;

import java.time.LocalDateTime;

@Slf4j
@Component
@RequiredArgsConstructor
public class ProgressConsumer {

    private final TaskRepository taskRepository;
    private final ReactiveRedisTemplate<String, String> redisTemplate;
    private final ObjectMapper objectMapper;
    private final NotificationService notificationService;

    @KafkaListener(topics = KafkaConfig.TOPIC_TASK_PROGRESS, groupId = "dataflow-backend")
    public void onProgress(TaskProgressEvent event) {
        log.debug("Progress event: taskId={} progress={} status={}", event.getTaskId(), event.getProgress(), event.getStatus());

        // 1. Update MySQL task record and create notification on completion
        taskRepository.findById(event.getTaskId())
                .flatMap(task -> {
                    task.setProgress(event.getProgress());
                    task.setStatus(event.getStatus());
                    if ("SUCCESS".equals(event.getStatus()) || "FAILED".equals(event.getStatus())) {
                        task.setFinishedAt(LocalDateTime.now());
                        if ("SUCCESS".equals(event.getStatus()) && event.getOutputKey() != null && !event.getOutputKey().isBlank()) {
                            task.setOutputPath(event.getOutputKey());
                        }
                        if ("FAILED".equals(event.getStatus())) {
                            task.setErrorMsg(event.getMessage());
                        }
                    }
                    return taskRepository.save(task);
                })
                .flatMap(task -> {
                    if ("SUCCESS".equals(event.getStatus())) {
                        return notificationService.create(
                                task.getUserId(), "success",
                                "Task #" + task.getId(),
                                event.getMessage() != null ? event.getMessage() : "Completed successfully"
                        ).thenReturn(task);
                    } else if ("FAILED".equals(event.getStatus())) {
                        return notificationService.create(
                                task.getUserId(), "error",
                                "Task #" + task.getId(),
                                event.getMessage() != null ? event.getMessage() : "Task failed"
                        ).thenReturn(task);
                    }
                    return Mono.just(task);
                })
                .subscribe();

        // 2. Publish to Redis channel for SSE consumers
        try {
            String json = objectMapper.writeValueAsString(event);
            redisTemplate.convertAndSend("progress:" + event.getTaskId(), json)
                    .subscribe();
        } catch (Exception e) {
            log.error("Failed to publish progress to Redis", e);
        }
    }
}
