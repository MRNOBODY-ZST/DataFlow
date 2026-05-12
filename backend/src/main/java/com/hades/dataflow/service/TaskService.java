package com.hades.dataflow.service;

import com.hades.dataflow.domain.dto.TaskProgressEvent;
import com.hades.dataflow.domain.dto.TaskResponse;
import com.hades.dataflow.domain.dto.TaskSubmitRequest;
import com.hades.dataflow.domain.entity.Task;
import com.hades.dataflow.kafka.TaskProducer;
import com.hades.dataflow.repository.PipelineRepository;
import com.hades.dataflow.repository.TaskRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.redis.core.ReactiveRedisTemplate;
import org.springframework.data.redis.listener.ChannelTopic;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;
import com.fasterxml.jackson.databind.ObjectMapper;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

@Slf4j
@Service
@RequiredArgsConstructor
public class TaskService {

    private final TaskRepository taskRepository;
    private final PipelineRepository pipelineRepository;
    private final TaskProducer taskProducer;
    private final ReactiveRedisTemplate<String, String> redisTemplate;
    private final ObjectMapper objectMapper;

    public Mono<TaskResponse> submitTask(TaskSubmitRequest req, Long userId) {
        return pipelineRepository.findById(req.getPipelineId())
                .switchIfEmpty(Mono.error(new ResponseStatusException(HttpStatus.NOT_FOUND, "Pipeline not found")))
                .filter(p -> p.getUserId().equals(userId))
                .switchIfEmpty(Mono.error(new ResponseStatusException(HttpStatus.FORBIDDEN)))
                .flatMap(pipeline -> {
                    Task task = Task.builder()
                            .pipelineId(req.getPipelineId())
                            .userId(userId)
                            .status("PENDING")
                            .progress(0)
                            .inputPath(req.getInputKey())
                            .build();
                    return taskRepository.save(task)
                            .flatMap(saved ->
                                    taskProducer.dispatchTask(
                                            saved.getId(),
                                            saved.getPipelineId(),
                                            pipeline.getGraphId(),
                                            req.getInputKey()
                                    ).thenReturn(toResponse(saved))
                            );
                });
    }

    public Flux<TaskResponse> listByUser(Long userId) {
        return taskRepository.findByUserIdOrderByCreatedAtDesc(userId)
                .map(this::toResponse);
    }

    public Mono<TaskResponse> getById(Long id, Long userId) {
        return taskRepository.findById(id)
                .switchIfEmpty(Mono.error(new ResponseStatusException(HttpStatus.NOT_FOUND)))
                .filter(t -> t.getUserId().equals(userId))
                .switchIfEmpty(Mono.error(new ResponseStatusException(HttpStatus.FORBIDDEN)))
                .map(this::toResponse);
    }

    public Flux<TaskProgressEvent> subscribeProgress(Long taskId, Long userId) {
        // Verify ownership first
        return taskRepository.findById(taskId)
                .filter(t -> t.getUserId().equals(userId))
                .switchIfEmpty(Mono.error(new ResponseStatusException(HttpStatus.FORBIDDEN)))
                .flatMapMany(task -> {
                    // If already terminal, emit final state immediately
                    if ("SUCCESS".equals(task.getStatus()) || "FAILED".equals(task.getStatus())) {
                        return Flux.just(new TaskProgressEvent(
                                taskId, null, task.getProgress(), task.getStatus(), task.getErrorMsg()));
                    }
                    // Subscribe to Redis pub/sub channel
                    return redisTemplate.listenTo(ChannelTopic.of("progress:" + taskId))
                            .map(msg -> {
                                try {
                                    return objectMapper.readValue(msg.getMessage(), TaskProgressEvent.class);
                                } catch (Exception e) {
                                    log.error("Failed to deserialize progress event", e);
                                    return new TaskProgressEvent(taskId, null, 0, "ERROR", e.getMessage());
                                }
                            })
                            .takeUntil(e -> "SUCCESS".equals(e.getStatus()) || "FAILED".equals(e.getStatus()));
                });
    }

    private TaskResponse toResponse(Task t) {
        return new TaskResponse(
                t.getId(), t.getPipelineId(), t.getStatus(), t.getProgress(),
                t.getInputPath(), t.getOutputPath(), t.getErrorMsg(),
                t.getCreatedAt(), t.getFinishedAt());
    }
}
