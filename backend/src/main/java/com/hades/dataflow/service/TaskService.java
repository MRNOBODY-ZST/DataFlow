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

import java.time.Duration;
import java.time.LocalDateTime;
import java.util.Set;

@Slf4j
@Service
@RequiredArgsConstructor
public class TaskService {

    private static final Set<String> TERMINAL_STATUSES = Set.of("SUCCESS", "FAILED", "CANCELLED");
    private static final Set<String> CANCELLABLE_STATUSES = Set.of("PENDING", "RUNNING");

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
                            .inputPath(null)
                            .build();
                    return taskRepository.save(task)
                            .flatMap(saved ->
                                    taskProducer.dispatchTask(
                                            saved.getId(),
                                            saved.getPipelineId(),
                                            pipeline.getGraphId(),
                                            userId
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

    public Mono<TaskResponse> cancelTask(Long id, Long userId) {
        return taskRepository.findById(id)
                .switchIfEmpty(Mono.error(new ResponseStatusException(HttpStatus.NOT_FOUND)))
                .filter(t -> t.getUserId().equals(userId))
                .switchIfEmpty(Mono.error(new ResponseStatusException(HttpStatus.FORBIDDEN)))
                .flatMap(task -> {
                    if (!CANCELLABLE_STATUSES.contains(task.getStatus())) {
                        return Mono.error(new ResponseStatusException(HttpStatus.BAD_REQUEST, "Task is not cancellable"));
                    }
                    task.setStatus("CANCELLED");
                    task.setFinishedAt(LocalDateTime.now());
                    return taskRepository.save(task);
                })
                .flatMap(task -> {
                    // Signal worker to stop via Redis key
                    Mono<Boolean> setCancel = redisTemplate.opsForValue()
                            .set("cancel:" + id, "1", Duration.ofHours(1));
                    // Notify SSE subscribers
                    TaskProgressEvent event = new TaskProgressEvent(id, null, task.getProgress(), "CANCELLED", "Task cancelled by user", null);
                    Mono<Long> publish;
                    try {
                        String json = objectMapper.writeValueAsString(event);
                        publish = redisTemplate.convertAndSend("progress:" + id, json);
                    } catch (Exception e) {
                        log.error("Failed to serialize cancel event", e);
                        publish = Mono.empty();
                    }
                    return Mono.when(setCancel, publish).thenReturn(toResponse(task));
                });
    }

    public Mono<Void> deleteTask(Long id, Long userId) {
        return taskRepository.findById(id)
                .switchIfEmpty(Mono.error(new ResponseStatusException(HttpStatus.NOT_FOUND)))
                .filter(t -> t.getUserId().equals(userId))
                .switchIfEmpty(Mono.error(new ResponseStatusException(HttpStatus.FORBIDDEN)))
                .flatMap(task -> {
                    if (!TERMINAL_STATUSES.contains(task.getStatus())) {
                        return Mono.error(new ResponseStatusException(HttpStatus.BAD_REQUEST, "Only finished tasks can be deleted"));
                    }
                    return taskRepository.delete(task)
                            .then(redisTemplate.delete("cancel:" + id))
                            .then();
                });
    }

    public Flux<TaskProgressEvent> subscribeProgress(Long taskId, Long userId) {
        // Verify ownership first
        return taskRepository.findById(taskId)
                .filter(t -> t.getUserId().equals(userId))
                .switchIfEmpty(Mono.error(new ResponseStatusException(HttpStatus.FORBIDDEN)))
                .flatMapMany(task -> {
                    // If already terminal, emit final state immediately
                    if (TERMINAL_STATUSES.contains(task.getStatus())) {
                        return Flux.just(new TaskProgressEvent(
                                taskId, null, task.getProgress(), task.getStatus(), task.getErrorMsg(), task.getOutputPath()));
                    }
                    // Subscribe to Redis pub/sub channel
                    return redisTemplate.listenTo(ChannelTopic.of("progress:" + taskId))
                            .map(msg -> {
                                try {
                                    return objectMapper.readValue(msg.getMessage(), TaskProgressEvent.class);
                                } catch (Exception e) {
                                    log.error("Failed to deserialize progress event", e);
                                    return new TaskProgressEvent(taskId, null, 0, "ERROR", e.getMessage(), null);
                                }
                            })
                            .takeUntil(e -> TERMINAL_STATUSES.contains(e.getStatus()));
                });
    }

    private TaskResponse toResponse(Task t) {
        return new TaskResponse(
                t.getId(), t.getPipelineId(), t.getStatus(), t.getProgress(),
                t.getInputPath(), t.getOutputPath(), t.getErrorMsg(),
                t.getCreatedAt(), t.getFinishedAt());
    }
}
