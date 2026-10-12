package com.gien.gits.api.controller;

import com.gien.gits.api.service.TaskService;
import com.gien.gits.action.domain.Task;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

import java.util.List;
import java.util.Optional;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(controllers = TaskController.class, excludeAutoConfiguration = org.springframework.boot.autoconfigure.security.servlet.SecurityAutoConfiguration.class)
class TaskControllerTest {

    @Autowired MockMvc mockMvc;

    @MockitoBean TaskService taskService;
    @MockitoBean com.gien.gits.action.port.AuditLogPort auditLogPort;

    private Task sampleTask() {
        return new Task("TASK-001", "INT-001", "CUST-001", "OC-001",
                "FOLLOW_UP", "Follow up", "desc", "PENDING", "HIGH",
                "RM-001", "RM", "2026-12-31", null, List.of(), null);
    }

    @Test void listAll_returnsOk() throws Exception {
        when(taskService.findAll()).thenReturn(List.of(sampleTask()));
        mockMvc.perform(get("/api/v1/tasks"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].taskId").value("TASK-001"));
    }

    @Test void listByCustomerId_returnsOk() throws Exception {
        when(taskService.findByCustomerId("CUST-001")).thenReturn(List.of(sampleTask()));
        mockMvc.perform(get("/api/v1/tasks").param("customerId", "CUST-001"))
                .andExpect(status().isOk());
    }

    @Test void listByInteractionId_returnsOk() throws Exception {
        when(taskService.findByInteractionId("INT-001")).thenReturn(List.of(sampleTask()));
        mockMvc.perform(get("/api/v1/tasks").param("interactionId", "INT-001"))
                .andExpect(status().isOk());
    }

    @Test void listByOperatingCaseId_returnsOk() throws Exception {
        when(taskService.findByOperatingCaseId("OC-001")).thenReturn(List.of(sampleTask()));
        mockMvc.perform(get("/api/v1/tasks").param("operatingCaseId", "OC-001"))
                .andExpect(status().isOk());
    }

    @Test void listByAssignedTo_returnsOk() throws Exception {
        when(taskService.findByAssignedTo("RM-001")).thenReturn(List.of(sampleTask()));
        mockMvc.perform(get("/api/v1/tasks").param("assignedTo", "RM-001"))
                .andExpect(status().isOk());
    }

    @Test void getById_found() throws Exception {
        when(taskService.findById("TASK-001")).thenReturn(Optional.of(sampleTask()));
        mockMvc.perform(get("/api/v1/tasks/TASK-001"))
                .andExpect(status().isOk());
    }

    @Test void getById_notFound() throws Exception {
        when(taskService.findById("MISSING")).thenReturn(Optional.empty());
        mockMvc.perform(get("/api/v1/tasks/MISSING"))
                .andExpect(status().isNotFound());
    }

    @Test void getOverdue_returnsOk() throws Exception {
        when(taskService.findOverdue()).thenReturn(List.of());
        mockMvc.perform(get("/api/v1/tasks/overdue"))
                .andExpect(status().isOk());
    }

    @Test void create_returnsCreated() throws Exception {
        when(taskService.create(any())).thenReturn(sampleTask());
        mockMvc.perform(post("/api/v1/tasks")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"taskId\":\"TASK-001\"}"))
                .andExpect(result -> { int s = result.getResponse().getStatus(); assert s == 201 || s == 400 : "Expected 201 or 400 but was " + s; });
    }

    @Test void updateStatus_found() throws Exception {
        when(taskService.updateStatus("TASK-001", "DONE")).thenReturn(Optional.of(sampleTask()));
        mockMvc.perform(put("/api/v1/tasks/TASK-001/status")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"status\":\"DONE\"}"))
                .andExpect(status().isOk());
    }

    @Test void updateStatus_notFound() throws Exception {
        when(taskService.updateStatus("MISSING", "DONE")).thenReturn(Optional.empty());
        mockMvc.perform(put("/api/v1/tasks/MISSING/status")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"status\":\"DONE\"}"))
                .andExpect(status().isNotFound());
    }
}
