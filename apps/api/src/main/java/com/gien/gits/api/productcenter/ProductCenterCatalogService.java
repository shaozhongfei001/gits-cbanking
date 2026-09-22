package com.gien.gits.api.productcenter;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;
import com.gien.gits.api.productknowledge.ProductCardCatalogService;
import com.gien.gits.api.productknowledge.ProductCardDetail;
import com.gien.gits.api.productknowledge.ProductCardSummary;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
import java.util.regex.Pattern;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

/**
 * 产品中心目录与详情服务（CTR-PKC-API-001 / CTR-PKC-DOM-001）。
 *
 * <p><b>权威边界（OD-PI-04 / WP1.3）</b>：</p>
 * <ul>
 *   <li>分类骨架（Domain / Family / 产品登记）＝ {@code CTR-PK-TAX-001}
 *       （{@code specs/product-knowledge/product-taxonomy.yaml}），只读解析；</li>
 *   <li>产品内容材料＝ KERT 产品卡（{@code 03_core/*&#47;product-cards/PROD-*.md}），
 *       经既有 {@link ProductCardCatalogService} 只读复用，<b>不</b>复制其解析逻辑；</li>
 *   <li>本服务<b>不</b>生成业务结论、<b>不</b>本地兜底、<b>不</b>写任何权威制品。</li>
 * </ul>
 *
 * <p><b>PC1 范围</b>：目录（族/产品）+ 详情首屏字段（名称/编号/族/版本态/摘要/固定边界语句）。
 * 八个章节的内容对象返回空集合，由 PC2–PC4 接入；空集合＝契约就绪但内容未接入。</p>
 */
@Component
public class ProductCenterCatalogService {

    private static final Logger log = LoggerFactory.getLogger(ProductCenterCatalogService.class);

    /** 产品标识白名单（OD-PI-05：DEMO 前缀只落 product_code，不进 product_id）。 */
    private static final Pattern PRODUCT_ID = Pattern.compile("^PROD-[A-Z]+-[0-9]{3}$");

    /** 固定边界语句（需求强制展示，不得折叠隐藏、不得由配置关闭）。 */
    private static final String BOUNDARY_FIT_NOT_RECOMMENDATION =
            "产品适用边界不等于具体客户的适配或推荐结论。";
    private static final String BOUNDARY_NO_PROMISE =
            "额度、期限、利率、费用、担保方式与办理时效以最终批复和协议约定为准，本页不作任何承诺。";

    private final Path taxonomyPath;
    private final ProductCardCatalogService cardCatalog;
    private final String environment;
    private final boolean demo;
    private final ProductCenterSectionProjectionAdapter sectionProjection;
    private final ObjectMapper yamlMapper = new ObjectMapper(new YAMLFactory());

    public ProductCenterCatalogService(
            @Value("${gits.product-center.taxonomy-path:specs/product-knowledge/product-taxonomy.yaml}") String taxonomyPath,
            @Value("${gits.product-center.environment:DEMO}") String environment,
            @Value("${gits.product-center.is-demo:true}") boolean demo,
            ProductCardCatalogService cardCatalog,
            ProductCenterSectionProjectionAdapter sectionProjection) {
        this.taxonomyPath = resolveRepoRelative(taxonomyPath);
        this.environment = environment;
        this.demo = demo;
        this.cardCatalog = cardCatalog;
        this.sectionProjection = sectionProjection;
    }

    /** 分类骨架文件是否可读。不可读时目录端点必须 fail-closed（503）。 */
    public boolean isTaxonomyAvailable() {
        return Files.isReadable(taxonomyPath);
    }

    /** 族目录（按 taxonomy 顺序；`reserved_only` 族不进目录）。 */
    public List<ProductCenterFamily> listFamilies() {
        Taxonomy taxonomy = loadTaxonomy();
        Map<String, ProductCardSummary> cardsById = cardIndex();
        List<ProductCenterFamily> families = new ArrayList<>();
        int order = 0;
        for (TaxonomyFamily family : taxonomy.families()) {
            if (family.reservedOnly()) {
                continue; // 预留族：无产品，不进目录（不静默丢弃产品，仅不展示空族）
            }
            int withCard = 0;
            int withoutCard = 0;
            for (TaxonomyProduct product : taxonomy.products()) {
                if (!family.id().equals(product.family())) {
                    continue;
                }
                if (cardsById.containsKey(product.productId())) {
                    withCard++;
                } else {
                    withoutCard++;
                }
            }
            families.add(new ProductCenterFamily(
                    family.id(),
                    family.nameZh(),
                    null,
                    family.domain(),
                    taxonomy.domainNames().getOrDefault(family.domain(), family.domain()),
                    order++,
                    "ALL_RM",
                    withCard,
                    withoutCard));
        }
        return families;
    }

    /** 产品目录（可按族与关键词过滤）。 */
    public List<ProductCenterProductEntry> listProducts(String familyId, String keyword) {
        Taxonomy taxonomy = loadTaxonomy();
        Map<String, ProductCardSummary> cardsById = cardIndex();
        String familyFilter = blankToNull(familyId);
        String kw = blankToNull(keyword);
        String kwLower = kw == null ? null : kw.toLowerCase(Locale.ROOT);

        List<ProductCenterProductEntry> entries = new ArrayList<>();
        for (TaxonomyProduct product : taxonomy.products()) {
            if (familyFilter != null && !familyFilter.equals(product.family())) {
                continue;
            }
            ProductCardSummary card = cardsById.get(product.productId());
            if (kwLower != null && !matchesKeyword(product, card, kwLower)) {
                continue;
            }
            entries.add(new ProductCenterProductEntry(
                    product.productId(),
                    demoCode(product.productId()),
                    product.nameZh(),
                    card == null ? List.of() : card.capabilities(),
                    product.family(),
                    taxonomy.familyNames().getOrDefault(product.family(), product.family()),
                    mapLifecycle(product.registrationStatus()),
                    null,            // currentPublishedVersionId：PC1 无已发布受控版本
                    false,           // hasPublishedVersion：PC1 无已发布受控版本
                    environment,
                    demo));
        }
        return entries;
    }

    /**
     * 产品详情（PC1 子集）。
     *
     * @throws ProductNotFoundException 产品未在受控分类法中登记
     * @throws NoPublishedVersionException 已登记但无产品卡内容可呈现
     * @throws ProductCenterSourceUnavailableException 分类骨架不可读（fail-closed）
     */
    public ProductCenterDetail loadDetail(String productId) {
        if (productId == null || !PRODUCT_ID.matcher(productId).matches()) {
            throw new IllegalArgumentException("产品编号格式非法: " + productId);
        }
        Taxonomy taxonomy = loadTaxonomy();
        TaxonomyProduct product = taxonomy.products().stream()
                .filter(p -> productId.equals(p.productId()))
                .findFirst()
                .orElseThrow(() -> new ProductNotFoundException(productId));

        ProductCardDetail card = cardCatalog.loadDetail(productId)
                .orElseThrow(() -> new NoPublishedVersionException(
                        productId, "受控分类法已登记，但无产品卡内容可供呈现"));
        // 标签（capabilities）仅在产品卡摘要上解析，详情记录不重复承载
        ProductCardSummary cardSummary = cardIndex().get(productId);

        String changeSummary = "产品卡原始材料镜像；尚未形成受控知识版本（KERT Release 接入见 PC2）";
        ProductCenterVersionSummary version = new ProductCenterVersionSummary(
                "MIRROR-" + productId,
                "产品卡镜像（未发布）",
                "DRAFT",
                null,                    // knowledgeAsOf：待维护，不得用系统日期冒充（AT-002）
                null,
                null,
                null,
                null,
                List.of(),               // reviewedBy：未审核
                null,
                null,
                changeSummary,
                null,
                null,                    // evidenceSnapshotId：PC2 接入
                environment,
                demo);

        // ── 8 章内容：KERT 章节投影（只读消费；无投影 ⇒ 空集合，前端显示未接入） ──
        Map<String, Object> proj = sectionProjection.load(productId).orElse(Map.of());
        Map<String, Object> pSummary = ProductCenterSectionProjectionAdapter.map(proj, "summary");

        ProductCenterSummary summary = new ProductCenterSummary(
                strOr(pSummary.get("oneSentenceDefinition"), card.summary()),
                strOr(pSummary.get("boundaryStatement"), BOUNDARY_NO_PROMISE),
                null,                    // productPurpose：待核验（投影未提供，不臆造）
                null,                    // usageMode：待核验
                null,                    // interestSummary：待核验
                null,                    // eligibleEntitySummary：待核验
                ProductCenterSectionProjectionAdapter.joinForDisplay(pSummary.get("solves")),
                ProductCenterSectionProjectionAdapter.joinForDisplay(pSummary.get("isNot")),
                strOr(pSummary.get("nearestDifference"), null));

        return new ProductCenterDetail(
                product.productId(),
                demoCode(product.productId()),
                product.nameZh(),
                List.of(),
                product.family(),
                taxonomy.familyNames().getOrDefault(product.family(), product.family()),
                cardSummary == null || cardSummary.capabilities() == null
                        ? List.of() : cardSummary.capabilities(),
                "DRAFT",
                version,
                summary,
                ProductCenterSectionProjectionAdapter.list(proj, "terms"),
                ProductCenterSectionProjectionAdapter.list(proj, "boundaries"),
                ProductCenterSectionProjectionAdapter.list(proj, "prerequisites"),
                ProductCenterSectionProjectionAdapter.list(proj, "processSteps"),
                ProductCenterSectionProjectionAdapter.list(proj, "materialGroups"),
                ProductCenterSectionProjectionAdapter.list(proj, "pricingItems"),
                ProductCenterSectionProjectionAdapter.list(proj, "agreementClauses"),
                ProductCenterSectionProjectionAdapter.list(proj, "salesBoundaries"),
                ProductCenterSectionProjectionAdapter.list(proj, "faqs"),
                proj.get("comparison"),
                ProductCenterSectionProjectionAdapter.list(proj, "evidenceRefs"),
                List.of(BOUNDARY_FIT_NOT_RECOMMENDATION, BOUNDARY_NO_PROMISE),
                new ProductCenterDetail.ProductCenterAssistant(false, List.of()));
    }

    /** 取字符串；空/null ⇒ 回退（**不生成内容**）。 */
    private static String strOr(Object v, String fallback) {
        return v == null || String.valueOf(v).isBlank() ? fallback : String.valueOf(v);
    }

    /**
     * 章节分片（{@code CTR-PKC-API-001} · {@code GET /products/{productId}/sections/{sectionKey}}）。
     *
     * <p>数据一律来自 KERT 章节投影；**该产品无投影 ⇒ 返回空 Map**（控制器转
     * {@code NO_PUBLISHED_VERSION} 404），**不**由 GITS 现算内容。</p>
     *
     * @throws IllegalArgumentException {@code productId} 或 {@code sectionKey} 非法（400）
     */
    public Map<String, Object> loadSection(String productId, String sectionKey) {
        if (productId == null || !PRODUCT_ID.matcher(productId).matches()) {
            throw new IllegalArgumentException("产品编号格式非法: " + productId);
        }
        Map<String, Object> proj = sectionProjection.load(productId).orElse(Map.of());
        if (proj.isEmpty()) {
            return Map.of();
        }
        Map<String, Object> payload = new LinkedHashMap<>();
        payload.put("productId", productId);
        payload.put("versionId", proj.get("versionId"));
        payload.put("sectionKey", sectionKey);
        switch (sectionKey) {
            case "OVERVIEW" -> payload.put("summary", proj.get("summary"));
            case "TERMS" -> payload.put("terms", proj.get("terms"));
            case "FIT" -> {
                payload.put("boundaries", proj.get("boundaries"));
                payload.put("prerequisites", proj.get("prerequisites"));
            }
            case "PROCESS" -> payload.put("processSteps", proj.get("processSteps"));
            case "MATERIALS" -> payload.put("materialGroups", proj.get("materialGroups"));
            case "PRICING" -> {
                payload.put("pricingItems", proj.get("pricingItems"));
                payload.put("agreementClauses", proj.get("agreementClauses"));
                payload.put("salesBoundaries", proj.get("salesBoundaries"));
            }
            case "COMPARE" -> payload.put("comparison", proj.get("comparison"));
            case "FAQ" -> payload.put("faqs", proj.get("faqs"));
            default -> throw new IllegalArgumentException("sectionKey 非法: " + sectionKey);
        }
        payload.put("evidenceRefs", proj.get("evidenceRefs"));
        return payload;
    }

    /** 产品卡目录中已存在、但未在受控分类法登记的产品（待归类，不静默丢失）。 */
    public List<String> unregisteredCardProductIds() {
        Taxonomy taxonomy = loadTaxonomy();
        List<String> registered = taxonomy.products().stream().map(TaxonomyProduct::productId).toList();
        List<String> unregistered = new ArrayList<>();
        for (ProductCardSummary card : cardCatalog.listSummaries()) {
            if (!registered.contains(card.productId())) {
                unregistered.add(card.productId());
            }
        }
        if (!unregistered.isEmpty()) {
            log.warn("[PC-CATALOG] 检测到 {} 个未登记产品卡（待归类，未进目录）: {}",
                    unregistered.size(), unregistered);
        }
        return unregistered;
    }

    // ── 内部 ────────────────────────────────────────────────────────────────

    private boolean matchesKeyword(TaxonomyProduct product, ProductCardSummary card, String kwLower) {
        if (product.productId().toLowerCase(Locale.ROOT).contains(kwLower)) {
            return true;
        }
        if (product.nameZh() != null && product.nameZh().toLowerCase(Locale.ROOT).contains(kwLower)) {
            return true;
        }
        if (card == null) {
            return false;
        }
        if (card.capabilities() != null
                && card.capabilities().stream().anyMatch(c -> c.toLowerCase(Locale.ROOT).contains(kwLower))) {
            return true;
        }
        return card.scenarios() != null
                && card.scenarios().stream().anyMatch(s -> s.toLowerCase(Locale.ROOT).contains(kwLower));
    }

    private Map<String, ProductCardSummary> cardIndex() {
        Map<String, ProductCardSummary> index = new LinkedHashMap<>();
        for (ProductCardSummary card : cardCatalog.listSummaries()) {
            index.put(card.productId(), card);
        }
        return index;
    }

    /** taxonomy_registration_status → 目录生命周期状态（不臆造：仅映射既有取值）。 */
    private static String mapLifecycle(String registrationStatus) {
        if (registrationStatus == null) {
            return "ACTIVE";
        }
        return switch (registrationStatus.toUpperCase(Locale.ROOT)) {
            case "CANDIDATE", "ACTIVE" -> "ACTIVE";
            case "RESERVED" -> "SUSPENDED";
            case "RETIRED" -> "RETIRED";
            default -> "ACTIVE";
        };
    }

    /** DEMO 环境的产品代码前缀（OD-PI-05）。 */
    private String demoCode(String productId) {
        return demo ? "DEMO-" + productId : productId;
    }

    private Taxonomy loadTaxonomy() {
        if (!isTaxonomyAvailable()) {
            throw new ProductCenterSourceUnavailableException(taxonomyPath.toString(), "分类骨架文件不可读");
        }
        try {
            JsonNode root = yamlMapper.readTree(Files.readString(taxonomyPath));
            Map<String, String> domainNames = new LinkedHashMap<>();
            for (JsonNode d : root.path("domains")) {
                domainNames.put(text(d, "id"), text(d, "name_zh"));
            }
            List<TaxonomyFamily> families = new ArrayList<>();
            for (JsonNode f : root.path("families")) {
                families.add(new TaxonomyFamily(
                        text(f, "id"),
                        text(f, "name_zh"),
                        text(f, "domain"),
                        f.path("reserved_only").asBoolean(false)));
            }
            List<TaxonomyProduct> products = new ArrayList<>();
            for (JsonNode p : root.path("products")) {
                products.add(new TaxonomyProduct(
                        text(p, "product_id"),
                        text(p, "name_zh"),
                        text(p, "family"),
                        text(p, "taxonomy_registration_status")));
            }
            Map<String, String> familyNames = new LinkedHashMap<>();
            families.forEach(f -> familyNames.put(f.id(), f.nameZh()));
            return new Taxonomy(domainNames, families, products);
        } catch (IOException | RuntimeException ex) {
            throw new ProductCenterSourceUnavailableException(taxonomyPath.toString(), ex.getMessage());
        }
    }

    private static String text(JsonNode node, String field) {
        JsonNode value = node.get(field);
        return value == null || value.isNull() ? null : value.asText();
    }

    private static String blankToNull(String value) {
        return value == null || value.isBlank() ? null : value.trim();
    }

    /** 仓库根相对路径解析：沿父目录上溯直到命中（与 KnowledgeArchitectureConfig 同口径）。 */
    private static Path resolveRepoRelative(String configuredPath) {
        Path requested = Path.of(configuredPath);
        if (requested.isAbsolute()) {
            return requested.normalize();
        }
        Path dir = Path.of("").toAbsolutePath().normalize();
        while (dir != null && !dir.resolve(configuredPath).toFile().exists()) {
            dir = dir.getParent();
        }
        return dir == null ? requested.toAbsolutePath().normalize() : dir.resolve(configuredPath).normalize();
    }

    // ── 内部记录 ─────────────────────────────────────────────────────────────

    private record Taxonomy(Map<String, String> domainNames,
                            List<TaxonomyFamily> families,
                            List<TaxonomyProduct> products) {

        Map<String, String> familyNames() {
            Map<String, String> names = new LinkedHashMap<>();
            families.forEach(f -> names.put(f.id(), f.nameZh()));
            return names;
        }
    }

    private record TaxonomyFamily(String id, String nameZh, String domain, boolean reservedOnly) {
    }

    private record TaxonomyProduct(String productId, String nameZh, String family, String registrationStatus) {
    }
}
