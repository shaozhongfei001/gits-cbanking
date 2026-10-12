package com.gien.gits.api.service;

import com.gien.gits.ontology.domain.ProductKnowledgeVersion;
import com.gien.gits.ontology.port.WritableProductKnowledgeVersionRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.*;

class ProductKnowledgeVersionServiceTest {

    private WritableProductKnowledgeVersionRepository repo;
    private ProductKnowledgeVersionService service;
    private ProductKnowledgeVersion sample;

    @BeforeEach
    void setUp() {
        repo = mock(WritableProductKnowledgeVersionRepository.class);
        service = new ProductKnowledgeVersionService(repo);
        sample = new ProductKnowledgeVersion("PV-1", "PROD-1", 1,
                "集团现金池", "CASH_MANAGEMENT", "desc",
                List.of("f1"), List.of("制造业"), "LOW",
                List.of("营业执照"), "固定费率", null, "初始版本", "system");
    }

    @Test void findByVersionId() {
        when(repo.findByVersionId("PV-1")).thenReturn(Optional.of(sample));
        assertThat(service.findByVersionId("PV-1")).isPresent();
    }

    @Test void findByVersionId_missing() {
        when(repo.findByVersionId("X")).thenReturn(Optional.empty());
        assertThat(service.findByVersionId("X")).isEmpty();
    }

    @Test void findByProductId() {
        when(repo.findByProductId("PROD-1")).thenReturn(List.of(sample));
        assertThat(service.findByProductId("PROD-1")).hasSize(1);
    }

    @Test void findLatestByProductId() {
        when(repo.findLatestByProductId("PROD-1")).thenReturn(Optional.of(sample));
        assertThat(service.findLatestByProductId("PROD-1")).isPresent();
    }

    @Test void findByCategory() {
        when(repo.findByCategory("CASH_MANAGEMENT")).thenReturn(List.of(sample));
        assertThat(service.findByCategory("CASH_MANAGEMENT")).hasSize(1);
    }

    @Test void findRecentVersions() {
        when(repo.findRecentVersions(20)).thenReturn(List.of(sample));
        assertThat(service.findRecentVersions(20)).hasSize(1);
    }

    @Test void create() {
        ProductKnowledgeVersion result = service.create(sample);
        assertThat(result).isSameAs(sample);
        verify(repo).save(sample);
    }
}
