package com.gien.gits.api.service;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

import com.gien.gits.ontology.ExternalEvent;
import com.gien.gits.ontology.port.WritableExternalEventRepository;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

class ExternalEventServiceTest {

    @Mock private WritableExternalEventRepository eventRepo;

    private AutoCloseable mocks;
    private ExternalEventService service;

    @BeforeEach
    void setUp() {
        mocks = MockitoAnnotations.openMocks(this);
        service = new ExternalEventService(eventRepo);
    }

    private ExternalEvent event(String id) {
        return new ExternalEvent(id, LocalDate.of(2026, 8, 20), ExternalEvent.SourceType.REGULATORY,
                "监管发布", "工信部", "新规", "内容", ExternalEvent.Confidence.HIGH,
                ExternalEvent.Reliability.VERIFIED, true, List.of("theme"), "信号", "禁行", "ref-1");
    }

    @Test
    void findByEventId_delegates() {
        ExternalEvent e = event("E-1");
        when(eventRepo.findByEventId("E-1")).thenReturn(Optional.of(e));
        assertEquals(Optional.of(e), service.findByEventId("E-1"));
    }

    @Test
    void findByEventId_notFound_returnsEmpty() {
        when(eventRepo.findByEventId("E-X")).thenReturn(Optional.empty());
        assertTrue(service.findByEventId("E-X").isEmpty());
    }

    @Test
    void findByEventType_delegates() {
        when(eventRepo.findByEventType("REGULATORY")).thenReturn(List.of(event("E-1")));
        assertEquals(1, service.findByEventType("REGULATORY").size());
    }

    @Test
    void findByAffectedCustomerId_delegates() {
        when(eventRepo.findByAffectedCustomerId("CUST-001")).thenReturn(List.of(event("E-1")));
        assertEquals(1, service.findByAffectedCustomerId("CUST-001").size());
    }

    @Test
    void findByAffectedIndustry_delegates() {
        when(eventRepo.findByAffectedIndustry("制造业")).thenReturn(List.of(event("E-1")));
        assertEquals(1, service.findByAffectedIndustry("制造业").size());
    }

    @Test
    void findBySeverity_delegates() {
        when(eventRepo.findBySeverity("HIGH")).thenReturn(List.of(event("E-1")));
        assertEquals(1, service.findBySeverity("HIGH").size());
    }

    @Test
    void findRecent_delegates() {
        when(eventRepo.findRecent(5)).thenReturn(List.of(event("E-1")));
        assertEquals(1, service.findRecent(5).size());
    }

    @Test
    void findAll_delegates() {
        when(eventRepo.findAll()).thenReturn(List.of(event("E-1")));
        assertEquals(1, service.findAll().size());
    }

    @Test
    void create_savesAndReturns() {
        ExternalEvent e = event("E-1");
        assertEquals(e, service.create(e));
        verify(eventRepo).save(e);
    }
}