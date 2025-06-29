package dataflow.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;
import dataflow.dto.WorkflowRequest;
import dataflow.producer.KafkaProducerService;

import java.io.IOException;
import java.util.*;
import java.util.concurrent.TimeUnit;

@Service
public class WorkflowManagerService {

    @Autowired
    private StringRedisTemplate redisTemplate;

    @Autowired
    private KafkaProducerService kafkaProducer;

    private final ObjectMapper objectMapper = new ObjectMapper();

    private static final String TASK_EXECUTION_TOPIC = "task-execution-topic";
    private static final String TASK_COMPLETION_TOPIC = "task-completion-topic";

    // Key-building helper methods
    private String tasksKey(String workflowId) { return "workflow:" + workflowId + ":tasks"; }
    private String adjKey(String workflowId) { return "workflow:" + workflowId + ":adj"; }
    private String inDegreeKey(String workflowId) { return "workflow:" + workflowId + ":inDegree"; }
    private String completedCountKey(String workflowId) { return "workflow:" + workflowId + ":completedCount"; }
    private String totalTasksKey(String workflowId) { return "workflow:" + workflowId + ":totalTasks"; }

    /**
     * Starts a new workflow instance.
     * @param request The workflow definition.
     */
    public void startWorkflow(WorkflowRequest request) throws JsonProcessingException {
        String workflowId = request.getWorkflowId();

        // 1. Initialize data structures
        initializeWorkflowState(request);

        // 2. Find all initial tasks (in-degree == 0) and dispatch them
        Map<Object, Object> inDegrees = redisTemplate.opsForHash().entries(inDegreeKey(workflowId));
        for (Map.Entry<Object, Object> entry : inDegrees.entrySet()) {
            if ("0".equals(entry.getValue().toString())) {
                String initialTaskId = (String) entry.getKey();
                dispatchTask(workflowId, initialTaskId);
            }
        }
    }

    /**
     * Listens for task completion messages from workers.
     * @param completionMessage Message in format "workflowId:taskId:status"
     */
    @KafkaListener(topics = TASK_COMPLETION_TOPIC, groupId = "workflow-manager-group")
    public void handleTaskCompletion(String completionMessage) throws IOException {
        String[] parts = completionMessage.split(":");
        if (parts.length < 3) return; // Ignore malformed messages

        String workflowId = parts[0];
        String completedTaskId = parts[1];
        String status = parts[2];

        // Update task status in Redis
        updateTaskStatus(workflowId, completedTaskId, status);

        if ("COMPLETED".equalsIgnoreCase(status)) {
            // Increment completed count
            long completedCount = redisTemplate.opsForValue().increment(completedCountKey(workflowId));

            // Get successors and decrement their in-degree
            List<String> successors = getSuccessors(workflowId, completedTaskId);
            for (String successorId : successors) {
                long newInDegree = redisTemplate.opsForHash().increment(inDegreeKey(workflowId), successorId, -1);
                if (newInDegree == 0) {
                    dispatchTask(workflowId, successorId);
                }
            }
            
            checkWorkflowCompletion(workflowId, completedCount);
        } else if ("FAILED".equalsIgnoreCase(status)) {
            // Handle workflow failure (e.g., mark workflow as failed, notify user)
            System.err.println("Workflow " + workflowId + " failed at task " + completedTaskId);
        }
    }

    private void initializeWorkflowState(WorkflowRequest request) throws JsonProcessingException {
        String workflowId = request.getWorkflowId();
        Map<String, List<String>> adjMap = new HashMap<>();
        Map<String, Integer> inDegreeMap = new HashMap<>();

        // Initialize all tasks with in-degree 0 and empty adjacency list
        for (WorkflowRequest.TaskDefinition task : request.getTasks()) {
            inDegreeMap.put(task.getTaskId(), 0);
            adjMap.put(task.getTaskId(), new ArrayList<>());
            updateTaskStatus(workflowId, task.getTaskId(), "PENDING"); // Also stores task details
        }
        
        // Populate adjacency list and calculate in-degrees from edges
        for (WorkflowRequest.Edge edge : request.getEdges()) {
            adjMap.get(edge.getFrom()).add(edge.getTo());
            inDegreeMap.compute(edge.getTo(), (k, v) -> (v == null ? 0 : v) + 1);
        }

        // Persist to Redis
        redisTemplate.opsForHash().putAll(inDegreeKey(workflowId), inDegreeMap.entrySet().stream()
                .collect(Collectors.toMap(Map.Entry::getKey, e -> e.getValue().toString())));

        for (Map.Entry<String, List<String>> entry : adjMap.entrySet()) {
            redisTemplate.opsForHash().put(adjKey(workflowId), entry.getKey(), objectMapper.writeValueAsString(entry.getValue()));
        }

        int totalTasks = request.getTasks().size();
        redisTemplate.opsForValue().set(totalTasksKey(workflowId), String.valueOf(totalTasks));
        redisTemplate.opsForValue().set(completedCountKey(workflowId), "0");

        // Set an expiration for workflow data to auto-clean old workflows
        long expirationDays = 7;
        redisTemplate.expire(tasksKey(workflowId), expirationDays, TimeUnit.DAYS);
        redisTemplate.expire(adjKey(workflowId), expirationDays, TimeUnit.DAYS);
        redisTemplate.expire(inDegreeKey(workflowId), expirationDays, TimeUnit.DAYS);
        redisTemplate.expire(totalTasksKey(workflowId), expirationDays, TimeUnit.DAYS);
        redisTemplate.expire(completedCountKey(workflowId), expirationDays, TimeUnit.DAYS);
    }
    
    private void dispatchTask(String workflowId, String taskId) {
        // 1. Update status to RUNNING
        updateTaskStatus(workflowId, taskId, "RUNNING");
        
        // 2. Send message to Kafka to trigger the worker
        String message = workflowId + ":" + taskId;
        kafkaProducer.sendMessage(TASK_EXECUTION_TOPIC, message);
        System.out.println("Dispatched task: " + message);
    }

    private void updateTaskStatus(String workflowId, String taskId, String status) {
        try {
            String taskDetailsJson = (String) redisTemplate.opsForHash().get(tasksKey(workflowId), taskId);
            Map<String, Object> taskDetails;
            if (taskDetailsJson != null) {
                taskDetails = objectMapper.readValue(taskDetailsJson, new TypeReference<>() {});
            } else {
                taskDetails = new HashMap<>(); // Should be populated from request first
            }
            taskDetails.put("status", status);
            redisTemplate.opsForHash().put(tasksKey(workflowId), taskId, objectMapper.writeValueAsString(taskDetails));
        } catch (IOException e) {
            // Handle JSON processing error
            e.printStackTrace();
        }
    }

    private List<String> getSuccessors(String workflowId, String taskId) throws IOException {
        String successorsJson = (String) redisTemplate.opsForHash().get(adjKey(workflowId), taskId);
        if (successorsJson == null || successorsJson.isEmpty()) {
            return Collections.emptyList();
        }
        return objectMapper.readValue(successorsJson, new TypeReference<List<String>>() {});
    }
    
    private void checkWorkflowCompletion(String workflowId, long completedCount) {
        String totalTasksStr = redisTemplate.opsForValue().get(totalTasksKey(workflowId));
        if (totalTasksStr != null) {
            long totalTasks = Long.parseLong(totalTasksStr);
            if (completedCount >= totalTasks) {
                System.out.println("Workflow " + workflowId + " completed successfully.");
                // Optional: perform cleanup or send a final notification
            }
        }
    }
} 