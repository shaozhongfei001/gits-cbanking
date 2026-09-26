package com.gien.gits.api.productcenter;

import java.util.List;

/**
 * 产品详情（CTR-PKC-DOM-001 · PkcProductDetail 的 PC1 子集）。
 *
 * <p><b>PC1 范围说明</b>：三栏骨架需要「产品首屏 + 版本 + 固定边界语句」，
 * 因此本记录先落地这部分字段。八个章节的内容对象
 * （{@code terms} / {@code boundaries} / {@code prerequisites} / {@code processSteps} /
 * {@code materialGroups} / {@code pricingItems} / {@code agreementClauses} /
 * {@code salesBoundaries} / {@code faqs} / {@code comparison} / {@code evidenceRefs}）
 * 在 PC1 一律返回<b>空集合</b>，由 PC2–PC4 按合同对象类型逐章接入。
 * 空集合表示「契约已就绪、内容未接入」，前端必须显示明确的未接入状态，
 * <b>不得</b>以示意数据填充。</p>
 *
 * @param productId      产品标识
 * @param productCode    产品代码（DEMO 使用 DEMO-* 前缀）
 * @param productName    产品中文名
 * @param aliases        别名
 * @param familyId       族 ID
 * @param familyName     族中文名
 * @param tags           标签（来源：产品卡 capabilities，仅客观能力词）
 * @param publishStatus  发布状态（PkcVersionStatus）
 * @param version        当前可呈现版本（PC1 为产品卡镜像 DRAFT 版本）
 * @param summary        产品摘要；null 字段表示待核验
 * @param fixedBoundaryStatements 固定边界语句（需求强制展示，不得折叠隐藏 PI-FR-049/095）
 * @param assistant      产品知识助手能力声明（PC5 实现；PC1 为 disabled）
 * @param retrievalTrace LightRAG 检索跟踪信息（请求链路、检索过程、耗时等）
 */
public record ProductCenterDetail(
        String productId,
        String productCode,
        String productName,
        List<String> aliases,
        String familyId,
        String familyName,
        List<String> tags,
        String publishStatus,
        ProductCenterVersionSummary version,
        ProductCenterSummary summary,
        List<Object> terms,
        List<Object> boundaries,
        List<Object> prerequisites,
        List<Object> processSteps,
        List<Object> materialGroups,
        List<Object> pricingItems,
        List<Object> agreementClauses,
        List<Object> salesBoundaries,
        List<Object> faqs,
        Object comparison,
        List<Object> evidenceRefs,
        List<String> fixedBoundaryStatements,
        ProductCenterAssistant assistant,
        RetrievalTrace retrievalTrace) {

    /**
     * 助手能力声明（CTR-PKC-API-001 · PkcProductDetail.assistant）。
     *
     * @param enabled       助手服务是否可用；不可用时核心页面必须完整可用（PI-NFR-002）
     * @param quickQuestions 快捷问题（来源为契约，PC5 接入；PC1 为空）
     */
    public record ProductCenterAssistant(boolean enabled, List<String> quickQuestions) {
    }
}
