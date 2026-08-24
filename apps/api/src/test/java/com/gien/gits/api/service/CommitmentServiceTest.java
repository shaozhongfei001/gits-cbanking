package com.gien.gits.api.service;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

import java.time.Instant;
import java.time.LocalDate;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

import com.gien.gits.ontology.Commitment;
import com.gien.gits.ontology.port.WritableCommitmentRepository;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

class CommitmentServiceTest {

    @Mock private WritableCommitmentRepository commitmentRepo;

    private AutoCloseable mocks;
    private CommitmentService service;

    @BeforeEach
    void setUp() {
        mocks = MockitoAnnotations.openMocks(this);
        service = new CommitmentService(commitmentRepo);
    }

    private Commitment commitment(String id, String customerId) {
        return new Commitment(
            UUID.fromString("00000000-0000-0000-0000-000000000001"),
            "CASE-1", "J-1", Commitment.CommitmentType.CUSTOMER_COMMITMENT,
            "承诺提交材料", "RM-1", LocalDate.of(2026, 9, 1),
            Commitment.CommitmentStatus.OPEN, "EV-1", Instant.now(), null);
    }

    @Test
    void findById_delegatesToRepository() {
        Commitment c = commitment("C-1", "CUST-001");
        when(commitmentRepo.findByCommitmentId("C-1")).thenReturn(Optional.of(c));
        assertEquals(Optional.of(c), service.findById("C-1"));
        verify(commitmentRepo).findByCommitmentId("C-1");
    }

    @Test
    void findById_notFound_returnsEmpty() {
        when(commitmentRepo.findByCommitmentId("C-X")).thenReturn(Optional.empty());
        assertTrue(service.findById("C-X").isEmpty());
    }

    @Test
    void findByInteractionId_delegates() {
        when(commitmentRepo.findByInteractionId("INT-1")).thenReturn(List.of(commitment("C-1", "CUST-001")));
        assertEquals(1, service.findByInteractionId("INT-1").size());
    }

    @Test
    void findByCustomerId_delegates() {
        when(commitmentRepo.findByCustomerId("CUST-001")).thenReturn(List.of(commitment("C-1", "CUST-001")));
        assertEquals(1, service.findByCustomerId("CUST-001").size());
    }

    @Test
    void findByStatus_delegates() {
        when(commitmentRepo.findByStatus("OPEN")).thenReturn(List.of(commitment("C-1", "CUST-001")));
        assertEquals(1, service.findByStatus("OPEN").size());
    }

    @Test
    void findByCommitmentType_delegates() {
        when(commitmentRepo.findByCommitmentType("CUSTOMER_COMMITMENT"))
            .thenReturn(List.of(commitment("C-1", "CUST-001")));
        assertEquals(1, service.findByCommitmentType("CUSTOMER_COMMITMENT").size());
    }

    @Test
    void findOverdue_delegates() {
        when(commitmentRepo.findOverdue()).thenReturn(List.of(commitment("C-1", "CUST-001")));
        assertEquals(1, service.findOverdue().size());
    }

    @Test
    void findAll_delegates() {
        when(commitmentRepo.findAll()).thenReturn(List.of(commitment("C-1", "CUST-001")));
        assertEquals(1, service.findAll().size());
    }

    @Test
    void create_savesAndReturns() {
        Commitment c = commitment("C-1", "CUST-001");
        assertEquals(c, service.create(c));
        verify(commitmentRepo).save(c);
    }

    @Test
    void updateStatus_updatesThenFetches() {
        Commitment updated = commitment("C-1", "CUST-001");
        when(commitmentRepo.findByCommitmentId("C-1")).thenReturn(Optional.of(updated));
        Optional<Commitment> result = service.updateStatus("C-1", "FULFILLED", "QA-1");
        assertTrue(result.isPresent());
        verify(commitmentRepo).updateStatus("C-1", "FULFILLED", "QA-1");
        verify(commitmentRepo).findByCommitmentId("C-1");
    }
}