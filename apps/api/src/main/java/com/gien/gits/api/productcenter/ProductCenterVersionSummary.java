package com.gien.gits.api.productcenter;

import java.util.List;

/**
 * 知识版本摘要（CTR-PKC-DOM-001 · PkcVersionSummary）。
 *
 * <p>诚实性原则（PI-FR-002 / AT-002 / AT-060）：</p>
 * <ul>
 *   <li>{@code knowledgeAsOf} 缺失时返回 null，前端显示「基准日待维护」，<b>不得</b>用系统当前日期冒充；</li>
 *   <li>{@code versionStatus} 为 DRAFT 时表示该版本尚未成为「已发布受控知识版本」，
 *       页面必须显式区分，不得呈现为正式口径；</li>
 *   <li>已审核（APPROVED 及以上）状态必须带 {@code reviewedBy} / {@code reviewRecordId}，
 *       缺失即为不实状态（AT-060）。</li>
 * </ul>
 *
 * @param versionId       版本 ID
 * @param versionLabel    版本标签（如「产品卡镜像 v2026.09.01.1」）
 * @param versionStatus   版本状态（见 CTR-PKC-API-001 PkcVersionStatus 枚举）
 * @param knowledgeAsOf   知识基准日（null = 待维护）
 * @param effectiveFrom   生效日（null = 未设定）
 * @param effectiveTo     失效日（null = 未设定，不等于永久有效）
 * @param publishedAt     发布时间（null = 未发布）
 * @param publishedBy     发布人/系统（null = 未发布）
 * @param reviewedBy      审核记录（空列表 = 无审核；APPROVED 及以上不得为空）
 * @param reviewRecordId  审核流水号
 * @param nextReviewAt    下次复审日（null = 未设定）
 * @param changeSummary   版本变更摘要
 * @param changeReason    变更原因
 * @param evidenceSnapshotId 证据快照 ID（下游引用三要素之一）
 * @param environment     环境（DEMO / UAT / PROD）
 * @param isDemo          DEMO 数据标记
 */
public record ProductCenterVersionSummary(
        String versionId,
        String versionLabel,
        String versionStatus,
        String knowledgeAsOf,
        String effectiveFrom,
        String effectiveTo,
        String publishedAt,
        String publishedBy,
        List<String> reviewedBy,
        String reviewRecordId,
        String nextReviewAt,
        String changeSummary,
        String changeReason,
        String evidenceSnapshotId,
        String environment,
        boolean isDemo) {
}
