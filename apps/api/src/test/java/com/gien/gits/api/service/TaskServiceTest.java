package com.gien.gits.api.service;

import com.gien.gits.action.domain.Task;
import com.gien.gits.action.port.WritableTaskRepository;
import org.junit.jupiter.api.Test;
import java.util.List;
import java.util.Optional;
import static org.assertj.core.api.Assertions.*;
import static org.mockito.Mockito.*;

class TaskServiceTest {
    private final WritableTaskRepository repo = mock(WritableTaskRepository.class);
    private final TaskService svc = new TaskService(repo);

    @Test void nullRepoRejected() {
        assertThatThrownBy(() -> new TaskService(null)).isInstanceOf(NullPointerException.class);
    }

    @Test void delegatesFinders() {
        Task t = mock(Task.class);
        when(repo.findByTaskId("k")).thenReturn(Optional.of(t));
        when(repo.findByInteractionId("i")).thenReturn(List.of(t));
        when(repo.findByCustomerId("c")).thenReturn(List.of(t));
        when(repo.findByOperatingCaseId("o")).thenReturn(List.of(t));
        when(repo.findByStatus("s")).thenReturn(List.of(t));
        when(repo.findByAssignedTo("a")).thenReturn(List.of(t));
        when(repo.findOverdue()).thenReturn(List.of(t));
        when(repo.findAll()).thenReturn(List.of(t));
        assertThat(svc.findById("k")).contains(t);
        assertThat(svc.findByInteractionId("i")).containsExactly(t);
        assertThat(svc.findByCustomerId("c")).containsExactly(t);
        assertThat(svc.findByOperatingCaseId("o")).containsExactly(t);
        assertThat(svc.findByStatus("s")).containsExactly(t);
        assertThat(svc.findByAssignedTo("a")).containsExactly(t);
        assertThat(svc.findOverdue()).containsExactly(t);
        assertThat(svc.findAll()).containsExactly(t);
    }

    @Test void createSavesAndReturns() {
        Task t = mock(Task.class);
        assertThat(svc.create(t)).isSameAs(t);
        verify(repo).save(t);
    }

    @Test void updateStatusDelegatesAndReloads() {
        Task t = mock(Task.class);
        when(repo.findByTaskId("k")).thenReturn(Optional.of(t));
        assertThat(svc.updateStatus("k","DONE")).contains(t);
        verify(repo).updateStatus("k","DONE");
    }
}
