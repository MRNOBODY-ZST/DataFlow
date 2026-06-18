package com.hades.dataflow.controller;

import com.hades.dataflow.domain.dto.TaskProgressEvent;
import com.hades.dataflow.domain.dto.TaskResponse;
import com.hades.dataflow.domain.dto.TaskSubmitRequest;
import com.hades.dataflow.service.TaskService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.MediaType;
import org.springframework.http.codec.ServerSentEvent;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

@RestController
@RequestMapping("/api/tasks")
@RequiredArgsConstructor
public class TaskController {

    private final TaskService taskService;

    @PostMapping
    public Mono<TaskResponse> submit(@RequestBody TaskSubmitRequest req, Authentication auth) {
        return taskService.submitTask(req, getUserId(auth));
    }

    @GetMapping
    public Flux<TaskResponse> list(Authentication auth) {
        return taskService.listByUser(getUserId(auth));
    }

    @GetMapping("/{id}")
    public Mono<TaskResponse> get(@PathVariable Long id, Authentication auth) {
        return taskService.getById(id, getUserId(auth));
    }

    @PostMapping("/{id}/cancel")
    public Mono<TaskResponse> cancel(@PathVariable Long id, Authentication auth) {
        return taskService.cancelTask(id, getUserId(auth));
    }

    @DeleteMapping("/{id}")
    public Mono<Void> delete(@PathVariable Long id, Authentication auth) {
        return taskService.deleteTask(id, getUserId(auth));
    }

    @GetMapping(value = "/{id}/progress", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<ServerSentEvent<TaskProgressEvent>> progress(
            @PathVariable Long id, Authentication auth) {
        return taskService.subscribeProgress(id, getUserId(auth))
                .map(event -> ServerSentEvent.<TaskProgressEvent>builder()
                        .id(String.valueOf(event.getProgress()))
                        .event("progress")
                        .data(event)
                        .build());
    }

    private Long getUserId(Authentication auth) {
        return (Long) auth.getDetails();
    }
}
