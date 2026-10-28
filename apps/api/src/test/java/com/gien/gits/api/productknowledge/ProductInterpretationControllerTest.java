package com.gien.gits.api.productknowledge;

import static org.assertj.core.api.Assertions.assertThat;

import java.nio.file.Files;
import java.nio.file.Path;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

/**
 * 产品卡只读端点测试。
 *
 * <p>2026-10-28「产品知识」解读页下线后，本文件只覆盖产品中心仍在使用的卡片链路：
 * 目录列表（集合不返回 null、未配置 card-dir 不本地兜底）、卡片详情、
 * 统一错误结构（400/404），以及基础路径 404 而非 500（F-L13-07）。
 * 原三视图解读与 LightRAG 检索端点的用例已随端点一并删除。</p>
 */
class ProductInterpretationControllerTest {

    private MockMvc mvc(String cardDir) {
        ProductInterpretationController ctrl =
                new ProductInterpretationController(new ProductCardCatalogService(cardDir));
        return MockMvcBuilders.standaloneSetup(ctrl)
                .setControllerAdvice(ctrl)
                .setMessageConverters(new org.springframework.http.converter.json.MappingJackson2HttpMessageConverter())
                .build();
    }

    /** 最小产品卡夹具：与 KERT {@code 03_core/**}{@code /product-cards/PROD-*.md} 同构。 */
    private static final String CARD = """
            ---
            schema: product_card/v1
            product_id: PROD-CM-001
            name: 现金池
            product_family: CASH_MANAGEMENT
            product_family_name: 现金管理
            owner: 公司金融产品管理部
            capabilities: [FUND_POOLING]
            applicable_scenarios: [GROUP_FUND_CENTRALIZATION]
            risk_notes: [REGULATORY_COMPLIANCE]
            ---

            # 产品卡：现金池（PROD-CM-001）

            ## 1. 产品概览与客户价值

            集团资金集中管理。
            """;

    @Test
    void basePathReturns404Not500() throws Exception {
        // F-L13-07：基础路径无 handler 时 Spring 曾抛 500 INTERNAL_ERROR
        mvc("").perform(
                        org.springframework.test.web.servlet.request.MockMvcRequestBuilders
                                .get("/api/v1/product-knowledge")
                                .accept(MediaType.APPLICATION_JSON))
                .andExpect(org.springframework.test.web.servlet.result.MockMvcResultMatchers
                        .status().isNotFound());
    }

    // ── 产品卡目录（/cards）此前完全无测试，随合同登记（API First）一并补齐 ──

    @Test
    void cardsWithUnconfiguredCardDirReturnsEmptyArrayNotNull() throws Exception {
        String body = mvc("").perform(
                        org.springframework.test.web.servlet.request.MockMvcRequestBuilders
                                .get("/api/v1/product-knowledge/cards")
                                .accept(MediaType.APPLICATION_JSON))
                .andExpect(org.springframework.test.web.servlet.result.MockMvcResultMatchers
                        .status().isOk())
                .andReturn().getResponse().getContentAsString();
        // 仓库规则 §3：集合返回空数组，不返回 null；未配置 card-dir 不本地兜底
        assertThat(body).isEqualTo("[]");
    }

    @Test
    void cardsListsParsedProductCards(@TempDir Path root) throws Exception {
        Path dir = root.resolve("cash-management/version=2026.09.01.1/product-cards");
        Files.createDirectories(dir);
        Files.writeString(dir.resolve("PROD-CM-001.md"), CARD);

        String body = mvc(root.toString()).perform(
                        org.springframework.test.web.servlet.request.MockMvcRequestBuilders
                                .get("/api/v1/product-knowledge/cards")
                                .accept(MediaType.APPLICATION_JSON))
                .andExpect(org.springframework.test.web.servlet.result.MockMvcResultMatchers
                        .status().isOk())
                .andReturn().getResponse().getContentAsString();

        assertThat(body).contains("PROD-CM-001");
        assertThat(body).contains("现金池");
        assertThat(body).contains("现金管理");
        // interpretable 字段已随解读功能下线移除，响应不得再出现该键
        assertThat(body).doesNotContain("interpretable");
    }

    @Test
    void cardDetailReturnsSectionsAndRawMarkdown(@TempDir Path root) throws Exception {
        Path dir = root.resolve("cash-management/version=2026.09.01.1/product-cards");
        Files.createDirectories(dir);
        Files.writeString(dir.resolve("PROD-CM-001.md"), CARD);

        String body = mvc(root.toString()).perform(
                        org.springframework.test.web.servlet.request.MockMvcRequestBuilders
                                .get("/api/v1/product-knowledge/cards/PROD-CM-001")
                                .accept(MediaType.APPLICATION_JSON))
                .andExpect(org.springframework.test.web.servlet.result.MockMvcResultMatchers
                        .status().isOk())
                .andReturn().getResponse().getContentAsString();

        assertThat(body).contains("产品概览与客户价值");
        assertThat(body).contains("rawMarkdown");
        assertThat(body).contains("version=2026.09.01.1");
    }

    @Test
    void cardDetailMissingReturns404WithUnifiedErrorBody() throws Exception {
        mvc("").perform(
                        org.springframework.test.web.servlet.request.MockMvcRequestBuilders
                                .get("/api/v1/product-knowledge/cards/PROD-CM-999")
                                .accept(MediaType.APPLICATION_JSON))
                .andExpect(org.springframework.test.web.servlet.result.MockMvcResultMatchers
                        .status().isNotFound())
                .andExpect(org.springframework.test.web.servlet.result.MockMvcResultMatchers
                        .jsonPath("$.status").value(404))
                .andExpect(org.springframework.test.web.servlet.result.MockMvcResultMatchers
                        .jsonPath("$.code").value("NOT_FOUND"))
                .andExpect(org.springframework.test.web.servlet.result.MockMvcResultMatchers
                        .jsonPath("$.path").exists())
                .andExpect(org.springframework.test.web.servlet.result.MockMvcResultMatchers
                        .jsonPath("$.timestamp").exists());
    }

    @Test
    void cardDetailMalformedProductIdReturns400() throws Exception {
        mvc("").perform(
                        org.springframework.test.web.servlet.request.MockMvcRequestBuilders
                                .get("/api/v1/product-knowledge/cards/BAD-ID")
                                .accept(MediaType.APPLICATION_JSON))
                .andExpect(org.springframework.test.web.servlet.result.MockMvcResultMatchers
                        .status().isBadRequest())
                .andExpect(org.springframework.test.web.servlet.result.MockMvcResultMatchers
                        .jsonPath("$.code").value("BAD_REQUEST"));
    }
}
