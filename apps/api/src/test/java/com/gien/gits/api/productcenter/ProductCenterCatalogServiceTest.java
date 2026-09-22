package com.gien.gits.api.productcenter;

import com.gien.gits.api.productknowledge.ProductCardCatalogService;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * 产品中心目录服务测试（CTR-PKC-API-001 · Loop PC1）。
 *
 * <p>覆盖三件事：① 目录计数口径；② PC1 详情子集的诚实性（DRAFT / knowledgeAsOf=null /
 * 固定边界语句 / 章节集合为空）；③ fail-closed 受控失败矩阵（未登记 / 无有效版本 / 源不可读）。</p>
 */
class ProductCenterCatalogServiceTest {

    @TempDir
    Path tmp;

    // ── 夹具 ─────────────────────────────────────────────────────────────────

    private Path writeTaxonomy(String content) throws IOException {
        Path path = tmp.resolve("product-taxonomy.yaml");
        Files.writeString(path, content);
        return path;
    }

    private Path writeCard(String productId, String nameZh, String family) throws IOException {
        Path cards = tmp.resolve("cards").resolve("cash-management").resolve("product-cards");
        Files.createDirectories(cards);
        Path card = cards.resolve(productId + ".md");
        Files.writeString(card, """
                ---
                product_id: %s
                name: %s
                product_family: %s
                product_family_name: 现金管理
                owner: 交易银行部
                capabilities: ["资金集中"]
                applicable_scenarios: ["日常周转"]
                ---

                # %s

                ## 产品概览与客户价值
                用于满足企业日常经营周转的短期资金需求。

                ## 适用客户与适用场景
                适用于符合准入条件的企业法人。
                """.formatted(productId, nameZh, family, nameZh));
        return tmp.resolve("cards");
    }

    private static final String TAXONOMY = """
            schema_version: "1.0.0"
            domains:
              - id: TRANSACTION_BANKING
                name_zh: 交易银行
            families:
              - id: CASH_MANAGEMENT
                name_zh: 现金管理
                domain: TRANSACTION_BANKING
                reserved_only: false
              - id: GUARANTEE_COMMITMENT
                name_zh: 担保承诺
                domain: CORPORATE_FINANCE
                reserved_only: true
            products:
              - product_id: PROD-CM-001
                name_zh: 现金池
                family: CASH_MANAGEMENT
                taxonomy_registration_status: CANDIDATE
              - product_id: PROD-CM-003
                name_zh: 法人账户透支
                family: CASH_MANAGEMENT
                taxonomy_registration_status: CANDIDATE
              - product_id: PROD-CM-009
                name_zh: 某未出卡产品
                family: CASH_MANAGEMENT
                taxonomy_registration_status: CANDIDATE
            """;

    private ProductCenterCatalogService service(Path taxonomyPath, Path cardDir) {
        return new ProductCenterCatalogService(
                taxonomyPath.toString(),
                "DEMO",
                true,
                // PC8 F-PC8-08：ProductCardCatalogService 现需解读投影端口（interpretable 由其判定）
                new ProductCardCatalogService(cardDir == null ? "" : cardDir.toString(),
                        productId -> java.util.Optional.empty()));
    }

    // ── 目录 ─────────────────────────────────────────────────────────────────

    @Nested
    @DisplayName("目录：族与产品计数")
    class Catalog {

        @Test
        @DisplayName("预留族不进目录；已出卡=可呈现，未出卡=待维护")
        void familiesExcludeReservedAndCountHonestly() throws IOException {
            Path cards = writeCard("PROD-CM-001", "现金池", "CASH_MANAGEMENT");
            writeCard("PROD-CM-003", "法人账户透支", "CASH_MANAGEMENT");
            ProductCenterCatalogService svc = service(writeTaxonomy(TAXONOMY), cards);

            List<ProductCenterFamily> families = svc.listFamilies();

            assertEquals(1, families.size(), "reserved_only 族不得进目录");
            ProductCenterFamily cm = families.get(0);
            assertEquals("CASH_MANAGEMENT", cm.familyId());
            assertEquals("现金管理", cm.familyName());
            assertEquals("交易银行", cm.domainName());
            assertEquals(2, cm.activeProductCount(), "已出卡产品数");
            assertEquals(1, cm.unclassifiedCount(), "族内未出卡产品数（不得静默丢弃）");
        }

        @Test
        @DisplayName("产品目录按族过滤，并列出未出卡产品（标为无有效版本）")
        void productsFilterByFamily() throws IOException {
            Path cards = writeCard("PROD-CM-001", "现金池", "CASH_MANAGEMENT");
            ProductCenterCatalogService svc = service(writeTaxonomy(TAXONOMY), cards);

            List<ProductCenterProductEntry> all = svc.listProducts(null, null);
            assertEquals(3, all.size(), "登记产品全部列出（含未出卡）");
            assertTrue(all.stream().noneMatch(ProductCenterProductEntry::hasPublishedVersion),
                    "PC1 无已发布受控知识版本 ⇒ hasPublishedVersion 必须为 false");

            assertEquals(3, svc.listProducts("CASH_MANAGEMENT", null).size());
            assertEquals(0, svc.listProducts("NOT_EXIST_FAMILY", null).size());
            assertEquals(1, svc.listProducts(null, "透支").size(), "关键词命中产品名");
            assertEquals(1, svc.listProducts(null, "PROD-CM-001").size(), "关键词命中产品编号");
        }

        @Test
        @DisplayName("产品卡存在但未登记 ⇒ 计入待归类，不进目录")
        void unregisteredCardIsReported() throws IOException {
            Path cards = writeCard("PROD-CM-001", "现金池", "CASH_MANAGEMENT");
            writeCard("PROD-CM-777", "未登记产品", "CASH_MANAGEMENT");
            ProductCenterCatalogService svc = service(writeTaxonomy(TAXONOMY), cards);

            assertEquals(List.of("PROD-CM-777"), svc.unregisteredCardProductIds());
            assertEquals(3, svc.listProducts(null, null).size(), "未登记产品卡不得进目录");
        }
    }

    // ── 详情（PC1 子集） ──────────────────────────────────────────────────────

    @Nested
    @DisplayName("详情：PC1 子集与诚实性")
    class Detail {

        @Test
        @DisplayName("版本为 DRAFT；基准日 null（不得用系统日期冒充）；章节集合为空")
        void detailIsHonestAndEmpty() throws IOException {
            Path cards = writeCard("PROD-CM-003", "法人账户透支", "CASH_MANAGEMENT");
            ProductCenterCatalogService svc = service(writeTaxonomy(TAXONOMY), cards);

            ProductCenterDetail detail = svc.loadDetail("PROD-CM-003");

            assertEquals("PROD-CM-003", detail.productId());
            assertEquals("法人账户透支", detail.productName());
            assertEquals("DEMO-PROD-CM-003", detail.productCode(), "DEMO 前缀只落 product_code");
            assertEquals("DRAFT", detail.publishStatus());
            assertNotNull(detail.version());
            assertEquals("DRAFT", detail.version().versionStatus());
            assertNull(detail.version().knowledgeAsOf(), "基准日缺失必须为 null，不得用系统日期");
            assertNull(detail.version().publishedAt());
            assertTrue(detail.version().reviewedBy().isEmpty(), "未审核状态不得带审核人");
            assertTrue(detail.version().isDemo());
            assertEquals("DEMO", detail.version().environment());

            // PC1：章节对象一律空集合（契约就绪、内容未接入），不得填示意数据
            assertTrue(detail.terms().isEmpty());
            assertTrue(detail.materialGroups().isEmpty());
            assertTrue(detail.faqs().isEmpty());
            assertNull(detail.comparison());

            // 固定边界语句必须始终存在（不得折叠隐藏、不得由配置关闭）
            assertEquals(2, detail.fixedBoundaryStatements().size());
            assertTrue(detail.fixedBoundaryStatements().stream()
                    .anyMatch(s -> s.contains("不等于具体客户的适配或推荐结论")));

            assertFalse(detail.assistant().enabled(), "PC1 助手未实现 ⇒ enabled=false");
        }

        @Test
        @DisplayName("摘要缺口显式为 null（待核验），不得臆造")
        void summaryGapsAreNull() throws IOException {
            Path cards = writeCard("PROD-CM-003", "法人账户透支", "CASH_MANAGEMENT");
            ProductCenterCatalogService svc = service(writeTaxonomy(TAXONOMY), cards);

            ProductCenterSummary summary = svc.loadDetail("PROD-CM-003").summary();

            assertNotNull(summary.oneSentenceDefinition(), "一句话定义来自产品卡概览节");
            assertNull(summary.productPurpose());
            assertNull(summary.usageMode());
            assertNull(summary.interestSummary());
            assertNull(summary.eligibleEntitySummary());
        }
    }

    // ── 受控失败矩阵（fail-closed） ──────────────────────────────────────────

    @Nested
    @DisplayName("受控失败：未登记 / 无有效版本 / 源不可读 / 非法编号")
    class FailClosed {

        @Test
        @DisplayName("未登记产品 ⇒ ProductNotFoundException")
        void unregisteredProduct() throws IOException {
            Path cards = writeCard("PROD-CM-001", "现金池", "CASH_MANAGEMENT");
            ProductCenterCatalogService svc = service(writeTaxonomy(TAXONOMY), cards);

            assertThrows(ProductNotFoundException.class, () -> svc.loadDetail("PROD-CM-888"));
        }

        @Test
        @DisplayName("已登记无产品卡 ⇒ NoPublishedVersionException（与未登记严格区分）")
        void registeredWithoutCard() throws IOException {
            Path cards = writeCard("PROD-CM-001", "现金池", "CASH_MANAGEMENT");
            ProductCenterCatalogService svc = service(writeTaxonomy(TAXONOMY), cards);

            assertThrows(NoPublishedVersionException.class, () -> svc.loadDetail("PROD-CM-009"));
        }

        @Test
        @DisplayName("非法产品编号 ⇒ IllegalArgumentException（400）")
        void invalidProductId() throws IOException {
            Path cards = writeCard("PROD-CM-001", "现金池", "CASH_MANAGEMENT");
            ProductCenterCatalogService svc = service(writeTaxonomy(TAXONOMY), cards);

            assertThrows(IllegalArgumentException.class, () -> svc.loadDetail("CM-003"));
            assertThrows(IllegalArgumentException.class, () -> svc.loadDetail("DEMO-PROD-CM-003"));
        }

        @Test
        @DisplayName("分类骨架不可读 ⇒ 503 语义（fail-closed，不本地兜底生成目录）")
        void taxonomyMissingFailsClosed() {
            ProductCenterCatalogService svc = service(tmp.resolve("no-such-taxonomy.yaml"), null);

            assertFalse(svc.isTaxonomyAvailable());
            assertThrows(ProductCenterSourceUnavailableException.class, svc::listFamilies);
            assertThrows(ProductCenterSourceUnavailableException.class, () -> svc.listProducts(null, null));
            assertThrows(ProductCenterSourceUnavailableException.class, () -> svc.loadDetail("PROD-CM-003"));
        }
    }

    // ── 仓库级契约断言（真实分类法） ────────────────────────────────────────

    @Nested
    @DisplayName("仓库级断言：真实分类法规模")
    class RealTaxonomy {

        @Test
        @DisplayName("受控分类法 = 6 有效族 / 13 登记产品（漂移必须红）")
        void realTaxonomyScale() {
            Path taxonomy = Path.of("specs/product-knowledge/product-taxonomy.yaml").toAbsolutePath();
            Path dir = Path.of("").toAbsolutePath();
            while (dir != null && !Files.exists(dir.resolve("specs/product-knowledge/product-taxonomy.yaml"))) {
                dir = dir.getParent();
            }
            Path resolved = dir == null ? taxonomy : dir.resolve("specs/product-knowledge/product-taxonomy.yaml");

            ProductCenterCatalogService svc = service(resolved, null);

            List<ProductCenterFamily> families = svc.listFamilies();
            List<ProductCenterProductEntry> products = svc.listProducts(null, null);

            assertEquals(6, families.size(), "有效族应为 6（7 族含 1 预留）");
            assertEquals(13, products.size(), "受控分类法登记产品应为 13");
            assertEquals("法人账户透支", products.stream()
                    .filter(p -> "PROD-CM-003".equals(p.productId()))
                    .findFirst().orElseThrow().productName());
        }
    }
}
