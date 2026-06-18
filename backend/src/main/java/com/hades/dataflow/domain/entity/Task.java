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
@Table("tasks")
public class Task {

    @Id
    private Long id;

    @Column("pipeline_id")
    private Long pipelineId;

    @Column("user_id")
    private Long userId;

    private String status;  // PENDING, RUNNING, SUCCESS, FAILED, CANCELLED

    private Integer progress;

    @Column("input_path")
    private String inputPath;

    @Column("output_path")
    private String outputPath;

    @Column("error_msg")
    private String errorMsg;

    @CreatedDate
    @Column("created_at")
    private LocalDateTime createdAt;

    @Column("finished_at")
    private LocalDateTime finishedAt;
}
