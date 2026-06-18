package com.hades.dataflow.repository;

import com.hades.dataflow.domain.entity.Notification;
import org.springframework.data.r2dbc.repository.Modifying;
import org.springframework.data.r2dbc.repository.Query;
import org.springframework.data.repository.reactive.ReactiveCrudRepository;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

public interface NotificationRepository extends ReactiveCrudRepository<Notification, Long> {

    Flux<Notification> findByUserIdOrderByCreatedAtDesc(Long userId);

    Mono<Long> countByUserIdAndRead(Long userId, Boolean read);

    @Modifying
    @Query("UPDATE notifications SET `read` = true WHERE user_id = :userId AND `read` = false")
    Mono<Long> markAllReadByUserId(Long userId);
}
