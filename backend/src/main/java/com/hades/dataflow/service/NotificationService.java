package com.hades.dataflow.service;

import com.hades.dataflow.domain.dto.NotificationResponse;
import com.hades.dataflow.domain.entity.Notification;
import com.hades.dataflow.repository.NotificationRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

@Service
@RequiredArgsConstructor
public class NotificationService {

    private final NotificationRepository notificationRepository;

    public Mono<NotificationResponse> create(Long userId, String type, String title, String message) {
        Notification n = Notification.builder()
                .userId(userId)
                .type(type)
                .title(title)
                .message(message)
                .read(false)
                .build();
        return notificationRepository.save(n).map(this::toResponse);
    }

    public Flux<NotificationResponse> listByUser(Long userId) {
        return notificationRepository.findByUserIdOrderByCreatedAtDesc(userId)
                .map(this::toResponse);
    }

    public Mono<Long> unreadCount(Long userId) {
        return notificationRepository.countByUserIdAndRead(userId, false);
    }

    public Mono<NotificationResponse> markRead(Long id, Long userId) {
        return notificationRepository.findById(id)
                .switchIfEmpty(Mono.error(new ResponseStatusException(HttpStatus.NOT_FOUND)))
                .filter(n -> n.getUserId().equals(userId))
                .switchIfEmpty(Mono.error(new ResponseStatusException(HttpStatus.FORBIDDEN)))
                .flatMap(n -> {
                    n.setRead(true);
                    return notificationRepository.save(n);
                })
                .map(this::toResponse);
    }

    public Mono<Void> markAllRead(Long userId) {
        return notificationRepository.markAllReadByUserId(userId).then();
    }

    public Mono<Void> delete(Long id, Long userId) {
        return notificationRepository.findById(id)
                .switchIfEmpty(Mono.error(new ResponseStatusException(HttpStatus.NOT_FOUND)))
                .filter(n -> n.getUserId().equals(userId))
                .switchIfEmpty(Mono.error(new ResponseStatusException(HttpStatus.FORBIDDEN)))
                .flatMap(notificationRepository::delete);
    }

    public Mono<Void> clearAll(Long userId) {
        return notificationRepository.findByUserIdOrderByCreatedAtDesc(userId)
                .flatMap(notificationRepository::delete)
                .then();
    }

    private NotificationResponse toResponse(Notification n) {
        return new NotificationResponse(
                n.getId(), n.getType(), n.getTitle(),
                n.getMessage(), n.getRead(), n.getCreatedAt());
    }
}
