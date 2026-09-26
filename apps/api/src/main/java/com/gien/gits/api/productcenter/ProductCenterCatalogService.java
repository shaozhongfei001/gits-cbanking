package com.gien.gits.api.productcenter;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;
import com.gien.gits.api.productknowledge.KnowledgeSourceUnavailableException;
import com.gien.gits.api.productknowledge.ProductCardCatalogService;
import com.gien.gits.api.productknowledge.ProductCardDetail;
import com.gien.gits.api.productknowledge.ProductCardSummary;
import com.gien.gits.api.productknowledge.ProductKnowledgeRetrievalPort;
import com.gien.gits.api.productknowledge.RetrievalCitation;
import com.gien.gits.api.productknowledge.RetrievalEntity;
import com.gien.gits.api.productknowledge.RetrievalRelation;
import com.gien.gits.api.productknowledge.RetrievalRequest;
import com.gien.gits.api.productknowledge.RetrievalResponse;
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
    private final ProductKnowledgeRetrievalPort retrievalPort;
    private final ObjectMapper yamlMapper = new ObjectMapper(new YAMLFactory());

    public ProductCenterCatalogService(
            @Value("${gits.product-center.taxonomy-path:specs/product-knowledge/product-taxonomy.yaml}") String taxonomyPath,
            @Value("${gits.product-center.environment:DEMO}") String environment,
            @Value("${gits.product-center.is-demo:true}") boolean demo,
            ProductCardCatalogService cardCatalog,
            ProductCenterSectionProjectionAdapter sectionProjection,
            ProductKnowledgeRetrievalPort retrievalPort) {
        this.taxonomyPath = resolveRepoRelative(taxonomyPath);
        this.environment = environment;
        this.demo = demo;
        this.cardCatalog = cardCatalog;
        this.sectionProjection = sectionProjection;
        this.retrievalPort = retrievalPort;
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
        long t0 = System.currentTimeMillis();
        List<RetrievalTrace.TraceStep> traceSteps = new ArrayList<>();

        // ── Step 1: 加载分类法 ──
        long s1 = System.currentTimeMillis();
        Taxonomy taxonomy = loadTaxonomy();
        TaxonomyProduct product = taxonomy.products().stream()
                .filter(p -> productId.equals(p.productId()))
                .findFirst()
                .orElseThrow(() -> new ProductNotFoundException(productId));
        traceSteps.add(new RetrievalTrace.TraceStep(
                "taxonomy", "加载受控分类法", System.currentTimeMillis() - s1, "OK"));

        // ── Step 2: 加载产品卡 ──
        long s2 = System.currentTimeMillis();
        ProductCardDetail card = cardCatalog.loadDetail(productId)
                .orElseThrow(() -> new NoPublishedVersionException(
                        productId, "受控分类法已登记，但无产品卡内容可供呈现"));
        ProductCardSummary cardSummary = cardIndex().get(productId);
        traceSteps.add(new RetrievalTrace.TraceStep(
                "product-card", "加载产品卡原始材料", System.currentTimeMillis() - s2, "OK"));

        // ── Step 3: 加载 KERT 章节投影 ──
        long s3 = System.currentTimeMillis();
        Map<String, Object> proj = sectionProjection.load(productId).orElse(Map.of());
        Map<String, Object> pSummary = ProductCenterSectionProjectionAdapter.map(proj, "summary");
        traceSteps.add(new RetrievalTrace.TraceStep(
                "section-projection", "加载 KERT 章节投影", System.currentTimeMillis() - s3, "OK"));

        // ── Step 4: LightRAG 检索 → 填充 productPurpose / usageMode / interestSummary / eligibleEntitySummary ──
        String productPurpose = null;
        String usageMode = null;
        String interestSummary = null;
        String eligibleEntitySummary = null;
        RetrievalTrace.LightRagTrace lightragTrace = null;

        long s4 = System.currentTimeMillis();
        try {
            String productName = product.nameZh();
            // 第一次查询：local 模式（精确匹配），获取当前产品的实体
            RetrievalResponse retrieval1 = retrievalPort.retrieve(productId, new RetrievalRequest(
                    productName + " 产品目的 使用方式", "local", null));
            // 第二次查询：hybrid 模式（广度覆盖），获取更多上下文
            RetrievalResponse retrieval2 = retrievalPort.retrieve(productId, new RetrievalRequest(
                    productName + " 产品目的 使用方式 计息口径 适用主体", "hybrid", null));
            long retrievalMs = System.currentTimeMillis() - s4;

            // 合并两次查询的实体（去重，优先保留 retrieval1/local 的结果——更精确）
            Map<String, RetrievalEntity> mergedEntities = new LinkedHashMap<>();
            if (retrieval1 != null && retrieval1.entities() != null) {
                for (RetrievalEntity e : retrieval1.entities()) {
                    if (e.name() != null) {
                        mergedEntities.put(e.name(), e);
                    }
                }
            }
            if (retrieval2 != null && retrieval2.entities() != null) {
                for (RetrievalEntity e : retrieval2.entities()) {
                    if (e.name() != null) {
                        mergedEntities.putIfAbsent(e.name(), e);
                    }
                }
            }

            // 构建合并后的 RetrievalResponse
            List<RetrievalEntity> allEntities = new ArrayList<>(mergedEntities.values());
            List<RetrievalRelation> allRelations = new ArrayList<>();
            List<RetrievalCitation> allCitations = new ArrayList<>();
            if (retrieval1 != null) {
                if (retrieval1.relations() != null) allRelations.addAll(retrieval1.relations());
                if (retrieval1.citations() != null) allCitations.addAll(retrieval1.citations());
            }
            if (retrieval2 != null) {
                if (retrieval2.relations() != null) allRelations.addAll(retrieval2.relations());
                if (retrieval2.citations() != null) allCitations.addAll(retrieval2.citations());
            }

            // 使用 retrieval2 作为基础（保留 rawResponse 等），替换 entities
            RetrievalResponse retrieval = retrieval2 != null ? retrieval2 : retrieval1;
            if (retrieval != null) {
                retrieval = new RetrievalResponse(
                        retrieval.productId(), retrieval.query(), retrieval.mode(),
                        allEntities, allRelations, allCitations,
                        retrieval.evidenceClass(), retrieval.provenanceState(),
                        retrieval.simulationOnly(), retrieval.generatedAt(),
                        retrieval.rawResponse());
            }

            // 构建 LightRag trace
            lightragTrace = new RetrievalTrace.LightRagTrace(
                    productName + " 产品目的 使用方式 计息口径 适用主体",
                    "hybrid",
                    allEntities.size(),
                    allRelations.size(),
                    allCitations.size(),
                    retrieval != null ? retrieval.evidenceClass() : null,
                    retrieval != null ? retrieval.provenanceState() : null,
                    retrieval != null ? retrieval.simulationOnly() : null,
                    retrievalMs,
                    allEntities.stream().map(RetrievalEntity::name).limit(10).toList());

            if (retrieval != null && retrieval.entities() != null) {
                // 从检索实体中提取四类字段
                // 三级匹配优先级：
                // 1. 实体名包含产品名（如"现金池_产品目的"）→ 精确匹配
                // 2. 描述中包含产品名 → 语义匹配
                // 3. 任意匹配 → 回退
                String productPurposeDescMatch = null;
                String usageModeDescMatch = null;
                String interestSummaryDescMatch = null;
                String eligibleEntitySummaryDescMatch = null;
                String productPurposeFallback = null;
                String usageModeFallback = null;
                String interestSummaryFallback = null;
                String eligibleEntitySummaryFallback = null;

                for (RetrievalEntity entity : retrieval.entities()) {
                    String name = entity.name();
                    String desc = entity.description();
                    if (name == null || desc == null) {
                        continue;
                    }
                    String nameLower = name.toLowerCase(Locale.ROOT);
                    boolean nameMatchesProduct = nameLower.contains(productName.toLowerCase(Locale.ROOT));
                    boolean descMatchesProduct = desc.contains(productName);

                    if (nameLower.contains("产品目的") || nameLower.contains("product_purpose")) {
                        if (nameMatchesProduct) {
                            productPurpose = desc;
                        } else if (descMatchesProduct && productPurposeDescMatch == null) {
                            productPurposeDescMatch = desc;
                        } else if (productPurposeFallback == null) {
                            productPurposeFallback = desc;
                        }
                    } else if (nameLower.contains("使用方式") || nameLower.contains("usage_mode")) {
                        if (nameMatchesProduct) {
                            usageMode = desc;
                        } else if (descMatchesProduct && usageModeDescMatch == null) {
                            usageModeDescMatch = desc;
                        } else if (usageModeFallback == null) {
                            usageModeFallback = desc;
                        }
                    } else if (nameLower.contains("计息口径") || nameLower.contains("interest")) {
                        if (nameMatchesProduct) {
                            interestSummary = desc;
                        } else if (descMatchesProduct && interestSummaryDescMatch == null) {
                            interestSummaryDescMatch = desc;
                        } else if (interestSummaryFallback == null) {
                            interestSummaryFallback = desc;
                        }
                    } else if (nameLower.contains("适用主体") || nameLower.contains("eligible")) {
                        if (nameMatchesProduct) {
                            eligibleEntitySummary = desc;
                        } else if (descMatchesProduct && eligibleEntitySummaryDescMatch == null) {
                            eligibleEntitySummaryDescMatch = desc;
                        } else if (eligibleEntitySummaryFallback == null) {
                            eligibleEntitySummaryFallback = desc;
                        }
                    }
                }
                // 回退：精确匹配 → 描述匹配 → 任意匹配
                if (productPurpose == null) productPurpose = productPurposeDescMatch != null ? productPurposeDescMatch : productPurposeFallback;
                if (usageMode == null) usageMode = usageModeDescMatch != null ? usageModeDescMatch : usageModeFallback;
                if (interestSummary == null) interestSummary = interestSummaryDescMatch != null ? interestSummaryDescMatch : interestSummaryFallback;
                if (eligibleEntitySummary == null) eligibleEntitySummary = eligibleEntitySummaryDescMatch != null ? eligibleEntitySummaryDescMatch : eligibleEntitySummaryFallback;
                // 如果实体名没匹配到全部四类字段，尝试从 rawResponse 文本中按标题提取
                if (productPurpose == null || usageMode == null
                        || interestSummary == null || eligibleEntitySummary == null) {
                    String rawText = retrieval.rawResponse();
                    if (rawText != null) {
                        productPurpose = extractSection(rawText, "产品目的", productPurpose);
                        usageMode = extractSection(rawText, "使用方式", usageMode);
                        interestSummary = extractSection(rawText, "计息口径", interestSummary);
                        eligibleEntitySummary = extractSection(rawText, "适用主体", eligibleEntitySummary);
                    }
                }
            }
            traceSteps.add(new RetrievalTrace.TraceStep(
                    "lightrag-retrieval",
                    String.format("LightRAG 检索（%d 实体, %d 关系, %d 引用, %dms）",
                            retrieval != null && retrieval.entities() != null ? retrieval.entities().size() : 0,
                            retrieval != null && retrieval.relations() != null ? retrieval.relations().size() : 0,
                            retrieval != null && retrieval.citations() != null ? retrieval.citations().size() : 0,
                            retrievalMs),
                    retrievalMs, "OK"));
        } catch (KnowledgeSourceUnavailableException ex) {
            long retrievalMs = System.currentTimeMillis() - s4;
            log.warn("[PC-DETAIL] LightRAG 检索不可用（productId={}）: {}", productId, ex.getMessage());
            traceSteps.add(new RetrievalTrace.TraceStep(
                    "lightrag-retrieval", "LightRAG 检索不可用: " + ex.getMessage(), retrievalMs, "UNAVAILABLE"));
        } catch (Exception ex) {
            long retrievalMs = System.currentTimeMillis() - s4;
            log.warn("[PC-DETAIL] LightRAG 检索异常（productId={}）: {}", productId, ex.getMessage());
            traceSteps.add(new RetrievalTrace.TraceStep(
                    "lightrag-retrieval", "LightRAG 检索异常: " + ex.getMessage(), retrievalMs, "ERROR"));
        }

        // ── 组装版本信息 ──
        String changeSummary = "产品卡原始材料镜像 + LightRAG 检索增强；尚未形成受控知识版本（KERT Release 接入见 PC2）";
        ProductCenterVersionSummary version = new ProductCenterVersionSummary(
                "MIRROR-" + productId,
                "产品卡镜像（未发布）",
                "DRAFT",
                null,
                null,
                null,
                null,
                null,
                List.of(),
                null,
                null,
                changeSummary,
                null,
                null,
                environment,
                demo);

        // ── 组装摘要（LightRAG 检索结果优先，投影次之，产品卡兜底） ──
        ProductCenterSummary summary = new ProductCenterSummary(
                strOr(pSummary.get("oneSentenceDefinition"), card.summary()),
                strOr(pSummary.get("boundaryStatement"), BOUNDARY_NO_PROMISE),
                productPurpose,
                usageMode,
                interestSummary,
                eligibleEntitySummary,
                ProductCenterSectionProjectionAdapter.joinForDisplay(pSummary.get("solves")),
                ProductCenterSectionProjectionAdapter.joinForDisplay(pSummary.get("isNot")),
                strOr(pSummary.get("nearestDifference"), null));

        long totalMs = System.currentTimeMillis() - t0;
        RetrievalTrace trace = new RetrievalTrace(traceSteps, lightragTrace, totalMs);

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
                new ProductCenterDetail.ProductCenterAssistant(false, List.of()),
                trace);
    }

    /** 从 LightRAG 返回文本中按标题提取章节内容。 */
    private static String extractSection(String text, String heading, String existing) {
        if (existing != null || text == null) {
            return existing;
        }
        // 匹配 "## 标题" 或 "# 标题" 后的内容，直到下一个标题或文本结束
        Pattern pat = Pattern.compile("##\\s*" + Pattern.quote(heading) + "\\s*\\n(.+?)(?=\\n#|$)",
                Pattern.DOTALL);
        java.util.regex.Matcher m = pat.matcher(text);
        if (m.find()) {
            String content = m.group(1).trim();
            return content.isBlank() ? null : content;
        }
        return null;
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
