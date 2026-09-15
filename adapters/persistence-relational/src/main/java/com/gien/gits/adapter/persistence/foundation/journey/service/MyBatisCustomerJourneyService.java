package com.gien.gits.adapter.persistence.foundation.journey.service;

import com.gien.gits.adapter.persistence.foundation.journey.mapper.CustomerJourneyMapper;
import com.gien.gits.customerjourney.CustomerJourney;
import com.gien.gits.customerjourney.InsightClaim;
import com.gien.gits.customerjourney.JourneyPhase;
import com.gien.gits.customerjourney.PostvisitAnalysis;
import com.gien.gits.customerjourney.PrevisitReport;
import com.gien.gits.customerjourney.ProductCandidateClaim;
import com.gien.gits.customerjourney.port.WritableCustomerJourneyRepository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

/**
 * MyBatis 客户旅程仓储实现 — foundation/journey 层
 */
public class MyBatisCustomerJourneyService implements WritableCustomerJourneyRepository {

    private final CustomerJourneyMapper mapper;

    public MyBatisCustomerJourneyService(CustomerJourneyMapper mapper) {
        this.mapper = mapper;
    }

    // ── CustomerJourney ──

    @Override
    public void saveJourney(CustomerJourney journey) {
        mapper.insertJourney(journey);
    }

    @Override
    public void updateJourneyPhase(UUID journeyId, JourneyPhase phase) {
        mapper.updateJourneyPhase(journeyId, phase);
    }

    @Override
    public Optional<CustomerJourney> findJourneyById(UUID journeyId) {
        return mapper.findJourneyById(journeyId);
    }

    @Override
    public List<CustomerJourney> findJourneysByCaseId(UUID caseId) {
        return mapper.findJourneysByCaseId(caseId);
    }

    @Override
    public List<CustomerJourney> findJourneysByCustomerId(String customerId) {
        return mapper.findJourneysByCustomerId(customerId);
    }

    // ── InsightClaim ──

    @Override
    public void saveInsight(InsightClaim insight) {
        mapper.insertInsight(insight);
    }

    @Override
    public Optional<InsightClaim> findInsightById(UUID insightId) {
        return mapper.findInsightById(insightId);
    }

    @Override
    public List<InsightClaim> findInsightsByCaseId(UUID caseId) {
        return mapper.findInsightsByCaseId(caseId);
    }

    // ── ProductCandidateClaim ──

    @Override
    public void saveProductCandidate(ProductCandidateClaim candidate) {
        mapper.insertProductCandidate(candidate);
    }

    @Override
    public Optional<ProductCandidateClaim> findProductCandidateById(UUID candidateId) {
        return mapper.findProductCandidateById(candidateId);
    }

    // ── PrevisitReport ──

    @Override
    public void savePrevisitReport(PrevisitReport report) {
        mapper.insertPrevisitReport(report);
    }

    @Override
    public Optional<PrevisitReport> findPrevisitReportById(UUID reportId) {
        return mapper.findPrevisitReportById(reportId);
    }

    // ── PostvisitAnalysis ──

    @Override
    public void savePostvisitAnalysis(PostvisitAnalysis analysis) {
        mapper.insertPostvisitAnalysis(analysis);
    }

    @Override
    public Optional<PostvisitAnalysis> findPostvisitAnalysisById(UUID analysisId) {
        return mapper.findPostvisitAnalysisById(analysisId);
    }
}
