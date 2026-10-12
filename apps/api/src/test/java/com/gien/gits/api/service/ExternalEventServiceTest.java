package com.gien.gits.api.service;

import com.gien.gits.ontology.ExternalEvent;
import com.gien.gits.ontology.port.WritableExternalEventRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.*;

class ExternalEventServiceTest {

    private WritableExternalEventRepository repo;
    private ExternalEventService service;
    private ExternalEvent sample;

    @BeforeEach
    void setUp() {
        repo = mock(WritableExternalEventRepository.class);
        service = new ExternalEventService(repo);
        sample = new ExternalEvent("EVT-1", LocalDate.of(2026, 9, 1),
                ExternalEvent.SourceType.REGULATORY, "银保监", "C-1",
                "监管新规", "内容", ExternalEvent.Confidence.HIGH,
                ExternalEvent.Reliability.VERIFIED, true,
                List.of("合规"), "signal", null, "ref-1");
    }

    @Test void findById() {
        when(repo.findByEventId("EVT-1")).thenReturn(Optional.of(sample));
        assertThat(service.findByEventId("EVT-1")).isPresent();
    }

    @Test void findById_missing() {
        when(repo.findByEventId("X")).thenReturn(Optional.empty());
        assertThat(service.findByEventId("X")).isEmpty();
    }

    @Test void findByEventType() {
        when(repo.findByEventType("REGULATORY")).thenReturn(List.of(sample));
        assertThat(service.findByEventType("REGULATORY")).hasSize(1);
    }

    @Test void findByAffectedCustomerId() {
        when(repo.findByAffectedCustomerId("C-1")).thenReturn(List.of(sample));
        assertThat(service.findByAffectedCustomerId("C-1")).hasSize(1);
    }

    @Test void findByAffectedIndustry() {
        when(repo.findByAffectedIndustry("制造业")).thenReturn(List.of(sample));
        assertThat(service.findByAffectedIndustry("制造业")).hasSize(1);
    }

    @Test void findBySeverity() {
        when(repo.findBySeverity("HIGH")).thenReturn(List.of(sample));
        assertThat(service.findBySeverity("HIGH")).hasSize(1);
    }

    @Test void findRecent() {
        when(repo.findRecent(10)).thenReturn(List.of(sample));
        assertThat(service.findRecent(10)).hasSize(1);
    }

    @Test void findAll() {
        when(repo.findAll()).thenReturn(List.of(sample));
        assertThat(service.findAll()).hasSize(1);
    }

    @Test void create() {
        ExternalEvent result = service.create(sample);
        assertThat(result).isSameAs(sample);
        verify(repo).save(sample);
    }
}
