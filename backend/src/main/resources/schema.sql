-- DataFlow MySQL schema for Spring SQL initialization

CREATE TABLE IF NOT EXISTS users (
    id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    username     VARCHAR(64)  UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    email        VARCHAR(128),
    created_at   DATETIME DEFAULT NOW(),
    updated_at   DATETIME DEFAULT NOW() ON UPDATE NOW()
);

CREATE TABLE IF NOT EXISTS pipelines (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id     BIGINT       NOT NULL,
    name        VARCHAR(128) NOT NULL,
    description TEXT,
    graph_id    VARCHAR(36)  NOT NULL COMMENT 'MongoDB document _id',
    created_at  DATETIME DEFAULT NOW(),
    updated_at  DATETIME DEFAULT NOW() ON UPDATE NOW(),
    INDEX idx_pipelines_user (user_id)
);

CREATE TABLE IF NOT EXISTS tasks (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    pipeline_id BIGINT NOT NULL,
    user_id     BIGINT NOT NULL,
    status      ENUM('PENDING','RUNNING','SUCCESS','FAILED','CANCELLED') NOT NULL DEFAULT 'PENDING',
    progress    INT    NOT NULL DEFAULT 0 COMMENT '0-100',
    input_path  VARCHAR(512) COMMENT 'MinIO object key for input',
    output_path VARCHAR(512) COMMENT 'MinIO object key for output',
    error_msg   TEXT,
    created_at  DATETIME DEFAULT NOW(),
    finished_at DATETIME,
    INDEX idx_tasks_user (user_id),
    INDEX idx_tasks_pipeline (pipeline_id),
    INDEX idx_tasks_status (status)
);

CREATE TABLE IF NOT EXISTS notifications (
    id         BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id    BIGINT       NOT NULL,
    type       ENUM('success','error','info') NOT NULL DEFAULT 'info',
    title      VARCHAR(256) NOT NULL,
    message    TEXT,
    `read`     BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at DATETIME     DEFAULT NOW(),
    INDEX idx_notifications_user (user_id),
    INDEX idx_notifications_user_read (user_id, `read`)
);
