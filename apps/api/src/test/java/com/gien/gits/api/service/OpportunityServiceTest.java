package com.gien.gits.api.service;

import com.gien.gits.ontology.domain.Opportunity;
import com.gien.gits.ontology.port.WritableOpportunityRepository;
import org.junit.jupiter.api.Test;
import java.util.List;
import java.util.Optional;
import static org.assertj.core.api.Assertions.*;
import static org.mockito.Mockito.*;

class OpportunityServiceTest {
    private final WritableOpportunityRepository repo = mock(WritableOpportunityRepository.class);
    private final OpportunityService svc = new OpportunityService(repo);

    @Test void nullRepoRejected() {
        assertThatThrownBy(() -> new OpportunityService(null)).isInstanceOf(NullPointerException.class);
    }

    @Test void delegatesFinders() {
        Opportunity o = mock(Opportunity.class);
        when(repo.findByOpportunityId("k")).thenReturn(Optional.of(o));
        when(repo.findByCustomerId("c")).thenReturn(List.of(o));
        when(repo.findByStatus("s")).thenReturn(List.of(o));
        when(repo.findByOpportunityType("t")).thenReturn(List.of(o));
        when(repo.findByAssignedTo("a")).thenReturn(List.of(o));
        when(repo.findActiveByCustomerId("c")).thenReturn(List.of(o));
        when(repo.findAll()).thenReturn(List.of(o));
        assertThat(svc.findById("k")).contains(o);
        assertThat(svc.findByCustomerId("c")).containsExactly(o);
        assertThat(svc.findByStatus("s")).containsExactly(o);
        assertThat(svc.findByOpportunityType("t")).containsExactly(o);
        assertThat(svc.findByAssignedTo("a")).containsExactly(o);
        assertThat(svc.findActiveByCustomerId("c")).containsExactly(o);
        assertThat(svc.findAll()).containsExactly(o);
    }

    @Test void createSavesAndReturns() {
        Opportunity o = mock(Opportunity.class);
        assertThat(svc.create(o)).isSameAs(o);
        verify(repo).save(o);
    }

    @Test void updateStatusDelegatesAndReloads() {
        Opportunity o = mock(Opportunity.class);
        when(repo.findByOpportunityId("k")).thenReturn(Optional.of(o));
        assertThat(svc.updateStatus("k","WON")).contains(o);
        verify(repo).updateStatus("k","WON");
    }
}
