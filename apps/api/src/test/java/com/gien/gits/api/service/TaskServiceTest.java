package com.gien.gits.api.service;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

import java.time.Instant;
import java.util.List;
import java.util.Optional;

import com.gien.gits.action.domain.Task;
import com.gien.gits.action.port.WritableTaskRepository;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

class TaskServiceTest {

    @Mock private WritableTaskRepository taskRepo;

    private AutoCloseable mocks;
    private TaskService service;

    @BeforeEach
    void setUp() {
        mocks = MockitoAnnotations.openMocks(this);
        service = new TaskService(taskRepo);
    }

    private Task task(String id, String customerId) {
        return new Task(id, "INT-1", customerId, "CASE-1", "FOLLOW_UP", "标题", "描述",
                "TODO", "HIGH", "RM-1", "RM", "2026-09-01", null, List.of("tag"), null,
                Instant.now(), Instant.now());
    }

    @Test
    void findById_delegatesToRepository() {
        Task t = task("T-1", "CUST-001");
        when(taskRepo.findByTaskId("T-1")).thenReturn(Optional.of(t));
        assertEquals(Optional.of(t), service.findById("T-1"));
        verify(taskRepo).findByTaskId("T-1");
    }

    @Test
    void findById_notFound_returnsEmpty() {
        when(taskRepo.findByTaskId("T-X")).thenReturn(Optional.empty());
        assertTrue(service.findById("T-X").isEmpty());
    }

    @Test
    void findByInteractionId_delegates() {
        when(taskRepo.findByInteractionId("INT-1")).thenReturn(List.of(task("T-1", "CUST-001")));
        assertEquals(1, service.findByInteractionId("INT-1").size());
    }

    @Test
    void findByCustomerId_delegates() {
        when(taskRepo.findByCustomerId("CUST-001")).thenReturn(List.of(task("T-1", "CUST-001")));
        assertEquals(1, service.findByCustomerId("CUST-001").size());
    }

    @Test
    void findByOperatingCaseId_delegates() {
        when(taskRepo.findByOperatingCaseId("CASE-1")).thenReturn(List.of(task("T-1", "CUST-001")));
        assertEquals(1, service.findByOperatingCaseId("CASE-1").size());
    }

    @Test
    void findByStatus_delegates() {
        when(taskRepo.findByStatus("TODO")).thenReturn(List.of(task("T-1", "CUST-001")));
        assertEquals(1, service.findByStatus("TODO").size());
    }

    @Test
    void findByAssignedTo_delegates() {
        when(taskRepo.findByAssignedTo("RM-1")).thenReturn(List.of(task("T-1", "CUST-001")));
        assertEquals(1, service.findByAssignedTo("RM-1").size());
    }

    @Test
    void findOverdue_delegates() {
        when(taskRepo.findOverdue()).thenReturn(List.of(task("T-1", "CUST-001")));
        assertEquals(1, service.findOverdue().size());
    }

    @Test
    void findAll_delegates() {
        when(taskRepo.findAll()).thenReturn(List.of(task("T-1", "CUST-001")));
        assertEquals(1, service.findAll().size());
    }

    @Test
    void create_savesAndReturnsTask() {
        Task t = task("T-1", "CUST-001");
        Task result = service.create(t);
        assertEquals(t, result);
        verify(taskRepo).save(t);
    }

    @Test
    void updateStatus_updatesThenFetches() {
        Task updated = task("T-1", "CUST-001");
        when(taskRepo.findByTaskId("T-1")).thenReturn(Optional.of(updated));
        Optional<Task> result = service.updateStatus("T-1", "DONE");
        assertTrue(result.isPresent());
        verify(taskRepo).updateStatus("T-1", "DONE");
        verify(taskRepo).findByTaskId("T-1");
    }
}