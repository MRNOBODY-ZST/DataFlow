package com.hades.dataflow.config;

import org.apache.kafka.clients.admin.NewTopic;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.kafka.config.TopicBuilder;

@Configuration
public class KafkaConfig {

    public static final String TOPIC_TASK_DISPATCH = "task.dispatch";
    public static final String TOPIC_TASK_PROGRESS = "task.progress";

    @Bean
    public NewTopic taskDispatchTopic() {
        return TopicBuilder.name(TOPIC_TASK_DISPATCH)
                .partitions(4)
                .replicas(1)
                .build();
    }

    @Bean
    public NewTopic taskProgressTopic() {
        return TopicBuilder.name(TOPIC_TASK_PROGRESS)
                .partitions(4)
                .replicas(1)
                .build();
    }
}
