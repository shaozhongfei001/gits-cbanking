package com.gien.gits.api.service;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

import java.time.Instant;
import java.util.List;
import java.util.Optional;

import com.gien.gits.ontology.domain.ProductKnowledgeVersion;
import com.gien.gits.ontology.port.WritableProductKnowledgeVersionRepository;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

class ProductKnowledgeVersionServiceTest {

    @Mock private WritableProductKnowledgeVersionRepository versionRepo;

    private AutoCloseable mocks;
    private ProductKnowledgeVersionService service;

    @BeforeEach
    void setUp() {
        mocks = MockitoAnnotations.openMocks(this);
        service = new ProductKnowledgeVersionService(versionRepo);
    }

    private ProductKnowledgeVersion version(String id, String productId) {
        return new ProductKnowledgeVersion(id, productId, 1, "代发工资", "DEPOSIT", "描述",
                List.of("特性"), List.of("制造业"), "LOW", List.of("材料"), "固定", null, null,
                "RM-1", Instant.now());
    }

    @Test
    void findByVersionId_delegates() {
        ProductKnowledgeVersion v = version("V-1", "PROD-1");
        when(versionRepo.findByVersionId("V-1")).thenReturn(Optional.of(v));
        assertEquals(Optional.of(v), service.findByVersionId("V-1"));
    }

    @Test
    void findByVersionId_notFound_returnsEmpty() {
        when(versionRepo.findByVersionId("V-X")).thenReturn(Optional.empty());
        assertTrue(service.findByVersionId("V-X").isEmpty());
    }

    @Test
    void findByProductId_delegates() {
        when(versionRepo.findByProductId("PROD-1")).thenReturn(List.of(version("V-1", "PROD-1")));
        assertEquals(1, service.findByProductId("PROD-1").size());
    }

    @Test
    void findLatestByProductId_delegates() {
        when(versionRepo.findLatestByProductId("PROD-1")).thenReturn(Optional.of(version("V-2", "PROD-1")));
        assertTrue(service.findLatestByProductId("PROD-1").isPresent());
    }

    @Test
    void findByCategory_delegates() {
        when(versionRepo.findByCategory("DEPOSIT")).thenReturn(List.of(version("V-1", "PROD-1")));
        assertEquals(1, service.findByCategory("DEPOSIT").size());
    }

    @Test
    void findRecentVersions_delegates() {
        when(versionRepo.findRecentVersions(5)).thenReturn(List.of(version("V-1", "PROD-1")));
        assertEquals(1, service.findRecentVersions(5).size());
    }

    @Test
    void create_savesAndReturns() {
        ProductKnowledgeVersion v = version("V-1", "PROD-1");
        assertEquals(v, service.create(v));
        verify(versionRepo).save(v);
    }
}