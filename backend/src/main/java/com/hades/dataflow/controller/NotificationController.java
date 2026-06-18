package com.hades.dataflow.controller;

import com.hades.dataflow.domain.dto.NotificationResponse;
import com.hades.dataflow.service.NotificationService;
import lombok.RequiredArgsConstructor;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

@RestController
@RequestMapping("/api/notifications")
@RequiredArgsConstructor
public class NotificationController {

    private final NotificationService notificationService;

    @GetMapping
    public Flux<NotificationResponse> list(Authentication auth) {
        return notificationService.listByUser(getUserId(auth));
    }

    @GetMapping("/unread-count")
    public Mono<Long> unreadCount(Authentication auth) {
        return notificationService.unreadCount(getUserId(auth));
    }

    @PatchMapping("/{id}/read")
    public Mono<NotificationResponse> markRead(@PathVariable Long id, Authentication auth) {
        return notificationService.markRead(id, getUserId(auth));
    }

    @PatchMapping("/read-all")
    public Mono<Void> markAllRead(Authentication auth) {
        return notificationService.markAllRead(getUserId(auth));
    }

    @DeleteMapping("/{id}")
    public Mono<Void> delete(@PathVariable Long id, Authentication auth) {
        return notificationService.delete(id, getUserId(auth));
    }

    @DeleteMapping
    public Mono<Void> clearAll(Authentication auth) {
        return notificationService.clearAll(getUserId(auth));
    }

    private Long getUserId(Authentication auth) {
        return (Long) auth.getDetails();
    }
}
