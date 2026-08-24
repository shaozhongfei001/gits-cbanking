package com.gien.gits.api.service;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

import java.time.Instant;
import java.util.List;
import java.util.Optional;

import com.gien.gits.ontology.domain.Opportunity;
import com.gien.gits.ontology.port.WritableOpportunityRepository;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

class OpportunityServiceTest {

    @Mock private WritableOpportunityRepository opportunityRepo;

    private AutoCloseable mocks;
    private OpportunityService service;

    @BeforeEach
    void setUp() {
        mocks = MockitoAnnotations.openMocks(this);
        service = new OpportunityService(opportunityRepo);
    }

    private Opportunity opportunity(String id, String customerId) {
        return new Opportunity(id, customerId, "INT-1", "CASE-1", "CROSS_SELL", "PROD-1",
                "对公服务", "描述", "IDENTIFIED", "100000", "HIGH", "RM-1", "INTERACTION",
                List.of("下一步"), "2026-10-01", Instant.now(), Instant.now());
    }

    @Test
    void findById_delegates() {
        Opportunity o = opportunity("O-1", "CUST-001");
        when(opportunityRepo.findByOpportunityId("O-1")).thenReturn(Optional.of(o));
        assertEquals(Optional.of(o), service.findById("O-1"));
    }

    @Test
    void findById_notFound_returnsEmpty() {
        when(opportunityRepo.findByOpportunityId("O-X")).thenReturn(Optional.empty());
        assertTrue(service.findById("O-X").isEmpty());
    }

    @Test
    void findByCustomerId_delegates() {
        when(opportunityRepo.findByCustomerId("CUST-001")).thenReturn(List.of(opportunity("O-1", "CUST-001")));
        assertEquals(1, service.findByCustomerId("CUST-001").size());
    }

    @Test
    void findByStatus_delegates() {
        when(opportunityRepo.findByStatus("IDENTIFIED")).thenReturn(List.of(opportunity("O-1", "CUST-001")));
        assertEquals(1, service.findByStatus("IDENTIFIED").size());
    }

    @Test
    void findByOpportunityType_delegates() {
        when(opportunityRepo.findByOpportunityType("CROSS_SELL")).thenReturn(List.of(opportunity("O-1", "CUST-001")));
        assertEquals(1, service.findByOpportunityType("CROSS_SELL").size());
    }

    @Test
    void findByAssignedTo_delegates() {
        when(opportunityRepo.findByAssignedTo("RM-1")).thenReturn(List.of(opportunity("O-1", "CUST-001")));
        assertEquals(1, service.findByAssignedTo("RM-1").size());
    }

    @Test
    void findActiveByCustomerId_delegates() {
        when(opportunityRepo.findActiveByCustomerId("CUST-001")).thenReturn(List.of(opportunity("O-1", "CUST-001")));
        assertEquals(1, service.findActiveByCustomerId("CUST-001").size());
    }

    @Test
    void findAll_delegates() {
        when(opportunityRepo.findAll()).thenReturn(List.of(opportunity("O-1", "CUST-001")));
        assertEquals(1, service.findAll().size());
    }

    @Test
    void create_savesAndReturns() {
        Opportunity o = opportunity("O-1", "CUST-001");
        assertEquals(o, service.create(o));
        verify(opportunityRepo).save(o);
    }

    @Test
    void updateStatus_updatesThenFetches() {
        Opportunity updated = opportunity("O-1", "CUST-001");
        when(opportunityRepo.findByOpportunityId("O-1")).thenReturn(Optional.of(updated));
        Optional<Opportunity> result = service.updateStatus("O-1", "WON");
        assertTrue(result.isPresent());
        verify(opportunityRepo).updateStatus("O-1", "WON");
        verify(opportunityRepo).findByOpportunityId("O-1");
    }
}