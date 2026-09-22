package com.gien.gits.api.productcenter;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertInstanceOf;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.gien.gits.api.productknowledge.ProductCardCatalogService;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

/**
 * PI · O-1：产品中心 8 章内容取 <b>KERT 章节投影</b>（只读消费）与 fail-closed 口径。
 *
 * <p>分域红线：GITS <b>不</b>本地兜底生成内容 —— 无投影 ⇒ 空集合 / 404；源不可达 ⇒ 503。</p>
 */
class ProductCenterSectionProjectionTest {

    @TempDir
    Path tmp;

    private static final String PRODUCT_ID = "PROD-CM-001";

    /** 造一份最小但形状完整的章节投影（字段名与 KERT 侧产出/契约一致）。 */
    private Path writeProjection() throws IOException {
        Path dir = tmp.resolve("sections");
        Files.createDirectories(dir);
        Files.writeString(dir.resolve(PRODUCT_ID + ".json"), """
                {
                  "schema": "product_center_sections/v1",
                  "productId": "PROD-CM-001",
                  "versionId": "1.0.0",
                  "summary": {"oneSentenceDefinition": "定义句。", "boundaryStatement": "边界句。",
                              "solves": ["能力A", "能力B"], "isNot": ["不适用A"], "nearestDifference": "替代：X。"},
                  "terms": [{"termId": "T1", "termKey": "PURPOSE", "businessDefinition": "用途",
                             "explanationForRm": "用途", "certaintyType": "VERIFIED", "displayOrder": 1}],
                  "boundaries": [{"boundaryId": "B1", "boundaryType": "TYPICAL_USE",
                                  "scenarioName": "场景", "scenarioDescription": "描述"}],
                  "prerequisites": [], "processSteps": [],
                  "materialGroups": [{"groupType": "BASIC_REQUIRED",
                                      "items": [{"materialId": "M1", "materialName": "营业执照",
                                                 "requirementLevel": "REQUIRED", "purpose": "（卡片未给）"}]}],
                  "pricingItems": [], "agreementClauses": [], "salesBoundaries": [],
                  "comparison": {"comparisonSetId": "CMP-1", "comparisonAsOf": "2026-09-01",
                                 "dimensions": [{"dimensionId": "RELATION", "dimensionName": "关系"}],
                                 "rows": [{"productId": "PROD-SET-001", "versionId": "",
                                           "values": {"RELATION": "前置产品"}}],
                                 "reviewState": "DRAFT"},
                  "faqs": [],
                  "evidenceRefs": [{"evidenceId": "EVR-1", "sourceRef": "03_core/x.md#S02"}]
                }
                """);
        return dir;
    }

    private ProductCenterCatalogService service(Path sectionDir) {
        return new ProductCenterCatalogService(
                tmp.resolve("taxonomy.yaml").toString(), "DEMO", true,
                new ProductCardCatalogService(tmp.resolve("cards").toString(),
                        productId -> java.util.Optional.empty()),
                new ProductCenterSectionProjectionAdapter(
                        sectionDir == null ? "" : sectionDir.toString(), new ObjectMapper()));
    }

    @Test
    @DisplayName("章节分片：内容来自投影，且带 productId/versionId/sectionKey/evidenceRefs")
    void sectionPayloadComesFromProjection() throws IOException {
        Map<String, Object> payload = service(writeProjection()).loadSection(PRODUCT_ID, "TERMS");

        assertEquals(PRODUCT_ID, payload.get("productId"));
        assertEquals("1.0.0", payload.get("versionId"));
        assertEquals("TERMS", payload.get("sectionKey"));
        assertEquals(1, ((List<?>) payload.get("terms")).size());
        assertFalse(((List<?>) payload.get("evidenceRefs")).isEmpty());
    }

    @Test
    @DisplayName("PRICING / FAQ 无内容时**如实返回空集合**（不编造）")
    void emptySectionsStayEmpty() throws IOException {
        ProductCenterCatalogService svc = service(writeProjection());

        assertTrue(((List<?>) svc.loadSection(PRODUCT_ID, "PRICING").get("pricingItems")).isEmpty());
        assertTrue(((List<?>) svc.loadSection(PRODUCT_ID, "FAQ").get("faqs")).isEmpty());
    }

    @Test
    @DisplayName("COMPARE 返回对象（含 dimensions/rows 与 reviewState=DRAFT）")
    void comparisonIsObject() throws IOException {
        Object comparison = service(writeProjection()).loadSection(PRODUCT_ID, "COMPARE").get("comparison");

        Map<?, ?> cmp = assertInstanceOf(Map.class, comparison);
        assertEquals("DRAFT", cmp.get("reviewState"));
        assertEquals(1, ((List<?>) cmp.get("rows")).size());
    }

    @Test
    @DisplayName("sectionKey 非法 ⇒ IllegalArgumentException（控制器转 400）")
    void invalidSectionKeyRejected() throws IOException {
        ProductCenterCatalogService svc = service(writeProjection());

        assertThrows(IllegalArgumentException.class, () -> svc.loadSection(PRODUCT_ID, "BOGUS"));
        assertThrows(IllegalArgumentException.class, () -> svc.loadSection("坏ID", "TERMS"));
    }

    @Test
    @DisplayName("该产品无投影 ⇒ 空 Map（控制器转 404），**不**本地兜底生成内容")
    void noProjectionYieldsEmpty() throws IOException {
        Path dir = writeProjection();

        assertTrue(service(dir).loadSection("PROD-TF-002", "TERMS").isEmpty());
    }

    @Test
    @DisplayName("fail-closed：section-dir 未配置 / 目录不可达 ⇒ ProductCenterSourceUnavailableException（503）")
    void sourceUnavailableIsFailClosed() throws IOException {
        assertThrows(ProductCenterSourceUnavailableException.class,
                () -> service(null).loadSection(PRODUCT_ID, "TERMS"));
        assertThrows(ProductCenterSourceUnavailableException.class,
                () -> service(tmp.resolve("not-exist-dir")).loadSection(PRODUCT_ID, "TERMS"));
    }
}
