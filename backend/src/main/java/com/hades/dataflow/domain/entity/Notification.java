package com.hades.dataflow.domain.entity;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.springframework.data.annotation.CreatedDate;
import org.springframework.data.annotation.Id;
import org.springframework.data.relational.core.mapping.Column;
import org.springframework.data.relational.core.mapping.Table;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
@Table("notifications")
public class Notification {

    @Id
    private Long id;

    @Column("user_id")
    private Long userId;

    private String type;  // success, error, info

    private String title;

    private String message;

    @Column("read")
    private Boolean read;

    @CreatedDate
    @Column("created_at")
    private LocalDateTime createdAt;
}
