package com.gien.gits.api.controller;

import com.gien.gits.api.dto.UpdateStatusRequest;
import com.gien.gits.api.service.TaskService;
import com.gien.gits.action.domain.Task;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Objects;

/**
 * 任务控制器 — 跟进任务管理
 */
@RestController
@RequestMapping("/api/v1/tasks")
public class TaskController {

    private final TaskService taskService;

    public TaskController(TaskService taskService) {
        this.taskService = Objects.requireNonNull(taskService);
    }

    @GetMapping("/{taskId}")
    public ResponseEntity<Task> getById(@PathVariable String taskId) {
        return taskService.findById(taskId)
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }

    @GetMapping
    public ResponseEntity<List<Task>> list(@RequestParam(required = false) String interactionId,
                                            @RequestParam(required = false) String customerId,
                                            @RequestParam(required = false) String operatingCaseId,
                                            @RequestParam(required = false) String assignedTo) {
        if (interactionId != null) {
            return ResponseEntity.ok(taskService.findByInteractionId(interactionId));
        }
        if (customerId != null) {
            return ResponseEntity.ok(taskService.findByCustomerId(customerId));
        }
        if (operatingCaseId != null) {
            return ResponseEntity.ok(taskService.findByOperatingCaseId(operatingCaseId));
        }
        if (assignedTo != null) {
            return ResponseEntity.ok(taskService.findByAssignedTo(assignedTo));
        }
        return ResponseEntity.ok(taskService.findAll());
    }

    @GetMapping("/overdue")
    public ResponseEntity<List<Task>> getOverdue() {
        return ResponseEntity.ok(taskService.findOverdue());
    }

    @PostMapping
    public ResponseEntity<Task> create(@RequestBody Task task) {
        return ResponseEntity.status(HttpStatus.CREATED).body(taskService.create(task));
    }

    @PutMapping("/{taskId}/status")
    public ResponseEntity<Task> updateStatus(@PathVariable String taskId, @RequestBody UpdateStatusRequest request) {
        return taskService.updateStatus(taskId, request.status())
            .map(ResponseEntity::ok)
            .orElse(ResponseEntity.notFound().build());
    }
}
