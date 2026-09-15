package com.gien.gits.adapter.persistence.foundation.journey.mapper;

import com.gien.gits.customerjourney.CustomerJourney;
import com.gien.gits.customerjourney.InsightClaim;
import com.gien.gits.customerjourney.JourneyPhase;
import com.gien.gits.customerjourney.PostvisitAnalysis;
import com.gien.gits.customerjourney.PrevisitReport;
import com.gien.gits.customerjourney.ProductCandidateClaim;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * 客户旅程 Mapper — foundation/journey 层
 */
@Mapper
public interface CustomerJourneyMapper {

    // ── CustomerJourney ──

    void insertJourney(CustomerJourney journey);

    Optional<CustomerJourney> findJourneyById(@Param("journeyId") UUID journeyId);

    List<CustomerJourney> findJourneysByCaseId(@Param("caseId") UUID caseId);

    List<CustomerJourney> findJourneysByCustomerId(@Param("customerId") String customerId);

    void updateJourneyPhase(@Param("journeyId") UUID journeyId,
                            @Param("phase") JourneyPhase phase);

    // ── InsightClaim ──

    void insertInsight(InsightClaim insight);

    Optional<InsightClaim> findInsightById(@Param("insightId") UUID insightId);

    List<InsightClaim> findInsightsByCaseId(@Param("caseId") UUID caseId);

    // ── ProductCandidateClaim ──

    void insertProductCandidate(ProductCandidateClaim candidate);

    Optional<ProductCandidateClaim> findProductCandidateById(@Param("candidateId") UUID candidateId);

    // ── PrevisitReport ──

    void insertPrevisitReport(PrevisitReport report);

    Optional<PrevisitReport> findPrevisitReportById(@Param("reportId") UUID reportId);

    // ── PostvisitAnalysis ──

    void insertPostvisitAnalysis(PostvisitAnalysis analysis);

    Optional<PostvisitAnalysis> findPostvisitAnalysisById(@Param("analysisId") UUID analysisId);
}
