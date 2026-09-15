package com.gien.gits.api.productknowledge;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.List;
import java.util.Map;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

/**
 * 产品解读控制器测试（L13 · CTR-PK-INT-001）。
 *
 * <p>重点验证受控失败路径：未发布、用途不允许、源不可达、无投影，
 * 以及集合不返回 null、非就绪字段 displayValue 恒 null。</p>
 */
class ProductInterpretationControllerTest {

    private MockMvc mvc(ProductKnowledgeInterpretationPort port) {
        return MockMvcBuilders.standaloneSetup(new ProductInterpretationController(port)).build();
    }

    private InterpretationProjection projection(String lifecycle) {
        InterpretationProjection p = new InterpretationProjection();
        p.setProductId("PROD-CM-001");
        p.setReleaseId("RLS-2026.09.06.1");
        p.setBundleHash("a".repeat(64));
        p.setLifecycleState(lifecycle);
        p.setIsStale(false);
        p.setProvenanceState("DEMO");
        p.setPurposeAllowed(Map.of("INTERPRETATION", true, "RECOMMENDATION", false));
        p.setGeneratedAt("2026-09-06T12:00:00+08:00");

        InterpretationProjection.ProjectionEvidence ev =
                new InterpretationProjection.ProjectionEvidence();
        ev.setEvidenceId("EVS-SRCCM001-11111111");
        ev.setSourceId("SRC-CM-001");
        ev.setSourceVersionId("SV-SRCCM001-20260906-5879e814");
        ev.setAuthorityLevel("INTERNAL_POLICY");
        ev.setLocatorHint("第十条");
        ev.setQuoteExcerpt("现金池主账户每日最低留存余额为人民币 50 万元");

        InterpretationProjection.ProjectionField unknown =
                new InterpretationProjection.ProjectionField();
        unknown.setFieldPath("pricing.serviceFee");
        unknown.setDisplayValue("120 元");
        unknown.setKnowledgeState("UNKNOWN");
        unknown.setEvidenceSummaries(List.of());

        InterpretationProjection.ProjectionField conflict =
                new InterpretationProjection.ProjectionField();
        conflict.setFieldPath("eligibility.minAccountBalance");
        conflict.setDisplayValue(null);
        conflict.setKnowledgeState("CONFLICT");
        conflict.setConflictId("CNF-PRODCM001-757c6c3b");
        conflict.setEvidenceSummaries(List.of(ev));

        p.setViews(Map.of("PRICING", List.of(unknown), "ELIGIBILITY", List.of(conflict)));
        return p;
    }

    @Test
    void publishedReleaseReturnsFieldsWithEvidenceBacklinks() throws Exception {
        String body = mvc(port -> Optional.of(projection("PUBLISHED"))).perform(
                        org.springframework.test.web.servlet.request.MockMvcRequestBuilders
                                .get("/api/v1/product-knowledge/PROD-CM-001/interpretation")
                                .param("view", "ELIGIBILITY")
                                .param("purpose", "INTERPRETATION")
                                .accept(MediaType.APPLICATION_JSON))
                .andExpect(org.springframework.test.web.servlet.result.MockMvcResultMatchers
                        .status().isOk())
                .andReturn().getResponse().getContentAsString();

        assertThat(body).contains("RLS-2026.09.06.1");
        assertThat(body).contains("CNF-PRODCM001-757c6c3b");
        assertThat(body).contains("EVS-SRCCM001-11111111");
        // CONFLICT 字段不得显示值
        assertThat(body).contains("\"knowledgeState\":\"CONFLICT\"");
    }

    @Test
    void unpublishedReleaseReturns404NotPublished() throws Exception {
        mvc(port -> Optional.of(projection("DRAFT"))).perform(
                        org.springframework.test.web.servlet.request.MockMvcRequestBuilders
                                .get("/api/v1/product-knowledge/PROD-CM-001/interpretation")
                                .param("view", "ELIGIBILITY")
                                .param("purpose", "INTERPRETATION")
                                .accept(MediaType.APPLICATION_JSON))
                .andExpect(org.springframework.test.web.servlet.result.MockMvcResultMatchers
                        .status().isNotFound())
                .andExpect(org.springframework.test.web.servlet.result.MockMvcResultMatchers
                        .jsonPath("$.code").value("PRODUCT_KNOWLEDGE_NOT_PUBLISHED"));
    }

    @Test
    void missingProjectionReturns404() throws Exception {
        mvc(port -> Optional.empty()).perform(
                        org.springframework.test.web.servlet.request.MockMvcRequestBuilders
                                .get("/api/v1/product-knowledge/PROD-CM-013/interpretation")
                                .param("view", "OVERVIEW")
                                .param("purpose", "INTERPRETATION")
                                .accept(MediaType.APPLICATION_JSON))
                .andExpect(org.springframework.test.web.servlet.result.MockMvcResultMatchers
                        .status().isNotFound());
    }

    @Test
    void recommendationPurposeNotAllowedReturns422() throws Exception {
        mvc(port -> Optional.of(projection("PUBLISHED"))).perform(
                        org.springframework.test.web.servlet.request.MockMvcRequestBuilders
                                .get("/api/v1/product-knowledge/PROD-CM-001/interpretation")
                                .param("view", "PRICING")
                                .param("purpose", "RECOMMENDATION")
                                .accept(MediaType.APPLICATION_JSON))
                .andExpect(org.springframework.test.web.servlet.result.MockMvcResultMatchers
                        .status().isUnprocessableEntity())
                .andExpect(org.springframework.test.web.servlet.result.MockMvcResultMatchers
                        .jsonPath("$.code").value("PURPOSE_NOT_ALLOWED"));
    }

    @Test
    void knowledgeSourceUnavailableReturns503FailedClosed() throws Exception {
        mvc(port -> {
            throw new KnowledgeSourceUnavailableException("KERT 解读快照目录未配置");
        }).perform(org.springframework.test.web.servlet.request.MockMvcRequestBuilders
                        .get("/api/v1/product-knowledge/PROD-CM-001/interpretation")
                        .param("view", "OVERVIEW")
                        .param("purpose", "INTERPRETATION")
                        .accept(MediaType.APPLICATION_JSON))
                .andExpect(org.springframework.test.web.servlet.result.MockMvcResultMatchers
                        .status().isServiceUnavailable())
                .andExpect(org.springframework.test.web.servlet.result.MockMvcResultMatchers
                        .jsonPath("$.code").value("FAILED_CLOSED"));
    }

    @Test
    void invalidViewAndPurposeReturn400() throws Exception {
        mvc(port -> Optional.of(projection("PUBLISHED"))).perform(
                        org.springframework.test.web.servlet.request.MockMvcRequestBuilders
                                .get("/api/v1/product-knowledge/PROD-CM-001/interpretation")
                                .param("view", "BOGUS")
                                .param("purpose", "INTERPRETATION")
                                .accept(MediaType.APPLICATION_JSON))
                .andExpect(org.springframework.test.web.servlet.result.MockMvcResultMatchers
                        .status().isBadRequest())
                .andExpect(org.springframework.test.web.servlet.result.MockMvcResultMatchers
                        .jsonPath("$.code").value("BAD_REQUEST"));

        mvc(port -> Optional.of(projection("PUBLISHED"))).perform(
                        org.springframework.test.web.servlet.request.MockMvcRequestBuilders
                                .get("/api/v1/product-knowledge/PROD-CM-001/interpretation")
                                .param("view", "OVERVIEW")
                                .param("purpose", "BOGUS")
                                .accept(MediaType.APPLICATION_JSON))
                .andExpect(org.springframework.test.web.servlet.result.MockMvcResultMatchers
                        .status().isBadRequest())
                .andExpect(org.springframework.test.web.servlet.result.MockMvcResultMatchers
                        .jsonPath("$.code").value("BAD_REQUEST"));
    }

    @Test
    void missingRequiredParamReturnsUnifiedErrorBody() throws Exception {
        mvc(port -> Optional.of(projection("PUBLISHED"))).perform(
                        org.springframework.test.web.servlet.request.MockMvcRequestBuilders
                                .get("/api/v1/product-knowledge/PROD-CM-001/interpretation")
                                .param("view", "OVERVIEW")
                                .accept(MediaType.APPLICATION_JSON))
                .andExpect(org.springframework.test.web.servlet.result.MockMvcResultMatchers
                        .status().isBadRequest())
                .andExpect(org.springframework.test.web.servlet.result.MockMvcResultMatchers
                        .jsonPath("$.status").value(400))
                .andExpect(org.springframework.test.web.servlet.result.MockMvcResultMatchers
                        .jsonPath("$.code").value("BAD_REQUEST"))
                .andExpect(org.springframework.test.web.servlet.result.MockMvcResultMatchers
                        .jsonPath("$.path").exists())
                .andExpect(org.springframework.test.web.servlet.result.MockMvcResultMatchers
                        .jsonPath("$.timestamp").exists());
    }

    @Test
    void basePathReturns404Not500() throws Exception {
        // F-L13-07：基础路径无 handler 时 Spring 曾抛 500 INTERNAL_ERROR
        mvc(port -> Optional.empty()).perform(
                        org.springframework.test.web.servlet.request.MockMvcRequestBuilders
                                .get("/api/v1/product-knowledge")
                                .accept(MediaType.APPLICATION_JSON))
                .andExpect(org.springframework.test.web.servlet.result.MockMvcResultMatchers
                        .status().isNotFound());
    }

    @Test
    void invalidProductIdReturns400() throws Exception {
        mvc(port -> Optional.empty()).perform(
                        org.springframework.test.web.servlet.request.MockMvcRequestBuilders
                                .get("/api/v1/product-knowledge/BAD-ID/interpretation")
                                .param("view", "OVERVIEW")
                                .param("purpose", "INTERPRETATION")
                                .accept(MediaType.APPLICATION_JSON))
                .andExpect(org.springframework.test.web.servlet.result.MockMvcResultMatchers
                        .status().isBadRequest());
    }
}
