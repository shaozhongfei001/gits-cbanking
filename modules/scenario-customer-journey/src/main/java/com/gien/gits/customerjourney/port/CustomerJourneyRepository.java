package com.gien.gits.customerjourney.port;

import com.gien.gits.customerjourney.CustomerJourney;
import com.gien.gits.customerjourney.InsightClaim;
import com.gien.gits.customerjourney.PostvisitAnalysis;
import com.gien.gits.customerjourney.PrevisitReport;
import com.gien.gits.customerjourney.ProductCandidateClaim;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * 客户旅程仓储端口 — 只读操作。
 *
 * <p>定义对客户旅程相关聚合（{@link CustomerJourney}、{@link InsightClaim}、
 * {@link ProductCandidateClaim}、{@link PrevisitReport}、{@link PostvisitAnalysis}）
 * 的查询契约，由适配器层实现。
 * 写操作见 {@link WritableCustomerJourneyRepository}。</p>
 */
public interface CustomerJourneyRepository {

    // ── CustomerJourney 查询 ──

    /**
     * 根据旅程ID查找客户旅程。
     *
     * @param journeyId 旅程唯一标识
     * @return 找到的客户旅程，若不存在则返回空
     */
    Optional<CustomerJourney> findJourneyById(UUID journeyId);

    /**
     * 根据运营案例ID查找其关联的所有客户旅程。
     *
     * @param caseId 运营案例唯一标识
     * @return 关联的客户旅程列表
     */
    List<CustomerJourney> findJourneysByCaseId(UUID caseId);

    /**
     * 根据客户ID查找其所有客户旅程。
     *
     * @param customerId 客户唯一标识
     * @return 该客户的旅程列表，按启动时间倒序
     */
    List<CustomerJourney> findJourneysByCustomerId(String customerId);

    // ── InsightClaim 查询 ──

    /**
     * 根据洞察ID查找洞察声明。
     *
     * @param insightId 洞察唯一标识
     * @return 找到的洞察声明，若不存在则返回空
     */
    Optional<InsightClaim> findInsightById(UUID insightId);

    /**
     * 根据运营案例ID查找其关联的所有洞察声明。
     *
     * @param caseId 运营案例唯一标识
     * @return 关联的洞察声明列表
     */
    List<InsightClaim> findInsightsByCaseId(UUID caseId);

    // ── ProductCandidateClaim 查询 ──

    /**
     * 根据产品候选ID查找产品候选声明。
     *
     * @param candidateId 产品候选唯一标识
     * @return 找到的产品候选声明，若不存在则返回空
     */
    Optional<ProductCandidateClaim> findProductCandidateById(UUID candidateId);

    // ── PrevisitReport 查询 ──

    /**
     * 根据访前报告ID查找访前报告。
     *
     * @param reportId 报告唯一标识
     * @return 找到的访前报告，若不存在则返回空
     */
    Optional<PrevisitReport> findPrevisitReportById(UUID reportId);

    // ── PostvisitAnalysis 查询 ──

    /**
     * 根据访后分析ID查找访后分析。
     *
     * @param analysisId 分析唯一标识
     * @return 找到的访后分析，若不存在则返回空
     */
    Optional<PostvisitAnalysis> findPostvisitAnalysisById(UUID analysisId);
}
