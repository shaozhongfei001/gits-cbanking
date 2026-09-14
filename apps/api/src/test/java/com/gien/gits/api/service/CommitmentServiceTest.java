package com.gien.gits.api.service;

import com.gien.gits.ontology.Commitment;
import com.gien.gits.ontology.port.WritableCommitmentRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.time.Instant;
import java.time.LocalDate;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.*;

class CommitmentServiceTest {

    private WritableCommitmentRepository repo;
    private CommitmentService service;
    private Commitment sample;

    @BeforeEach
    void setUp() {
        repo = mock(WritableCommitmentRepository.class);
        service = new CommitmentService(repo);
        sample = new Commitment(
                UUID.randomUUID(), "OC-1", "J-1",
                Commitment.CommitmentType.CUSTOMER_COMMITMENT, "Deliver report",
                "RM-1", LocalDate.of(2026, 12, 31),
                Commitment.CommitmentStatus.OPEN, null,
                Instant.now(), null,
                UUID.randomUUID(), UUID.randomUUID(),
                null, "RM-1", null,
                Instant.now(), Instant.now());
    }

    @Test void findById() {
        String id = sample.commitmentId().toString();
        when(repo.findByCommitmentId(id)).thenReturn(Optional.of(sample));
        assertThat(service.findById(id)).isPresent();
    }

    @Test void findById_missing() {
        when(repo.findByCommitmentId("X")).thenReturn(Optional.empty());
        assertThat(service.findById("X")).isEmpty();
    }

    @Test void findByInteractionId() {
        when(repo.findByInteractionId("INT-1")).thenReturn(List.of(sample));
        assertThat(service.findByInteractionId("INT-1")).hasSize(1);
    }

    @Test void findByCustomerId() {
        when(repo.findByCustomerId("C-1")).thenReturn(List.of(sample));
        assertThat(service.findByCustomerId("C-1")).hasSize(1);
    }

    @Test void findByStatus() {
        when(repo.findByStatus("OPEN")).thenReturn(List.of(sample));
        assertThat(service.findByStatus("OPEN")).hasSize(1);
    }

    @Test void findByCommitmentType() {
        when(repo.findByCommitmentType("CUSTOMER_COMMITMENT")).thenReturn(List.of(sample));
        assertThat(service.findByCommitmentType("CUSTOMER_COMMITMENT")).hasSize(1);
    }

    @Test void findOverdue() {
        when(repo.findOverdue()).thenReturn(List.of(sample));
        assertThat(service.findOverdue()).hasSize(1);
    }

    @Test void findAll() {
        when(repo.findAll()).thenReturn(List.of(sample));
        assertThat(service.findAll()).hasSize(1);
    }

    @Test void create() {
        Commitment result = service.create(sample);
        assertThat(result).isSameAs(sample);
        verify(repo).save(sample);
    }

    @Test void updateStatus() {
        String id = sample.commitmentId().toString();
        when(repo.findByCommitmentId(id)).thenReturn(Optional.of(sample));
        service.updateStatus(id, "FULFILLED", "RM-1");
        verify(repo).updateStatus(id, "FULFILLED", "RM-1");
    }
}
