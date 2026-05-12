package com.hades.dataflow.kafka;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.hades.dataflow.config.KafkaConfig;
import com.hades.dataflow.domain.dto.TaskProgressEvent;
import com.hades.dataflow.repository.TaskRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.ReactiveRedisTemplate;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;

@Slf4j
@Component
@RequiredArgsConstructor
public class ProgressConsumer {

    private final TaskRepository taskRepository;
    private final ReactiveRedisTemplate<String, String> redisTemplate;
    private final ObjectMapper objectMapper;

    @KafkaListener(topics = KafkaConfig.TOPIC_TASK_PROGRESS, groupId = "dataflow-backend")
    public void onProgress(TaskProgressEvent event) {
        log.debug("Progress event: taskId={} progress={} status={}", event.getTaskId(), event.getProgress(), event.getStatus());

        // 1. Update MySQL task record
        taskRepository.findById(event.getTaskId())
                .flatMap(task -> {
                    task.setProgress(event.getProgress());
                    task.setStatus(event.getStatus());
                    if ("SUCCESS".equals(event.getStatus()) || "FAILED".equals(event.getStatus())) {
                        task.setFinishedAt(LocalDateTime.now());
                        if ("FAILED".equals(event.getStatus())) {
                            task.setErrorMsg(event.getMessage());
                        }
                    }
                    return taskRepository.save(task);
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
