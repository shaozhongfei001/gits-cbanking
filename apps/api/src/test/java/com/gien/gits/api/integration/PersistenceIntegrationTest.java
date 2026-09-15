package com.gien.gits.api.integration;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.context.TestPropertySource;

import com.gien.gits.customerjourney.port.WritableCustomerJourneyRepository;
import com.gien.gits.ontology.port.WritableClaimRepository;
import com.gien.gits.ontology.port.WritableInteractionRepository;
import com.gien.gits.ontology.port.WritableOperatingCaseRepository;
import com.gien.gits.customerjourney.CustomerJourney;
import com.gien.gits.customerjourney.InsightClaim;
import com.gien.gits.customerjourney.JourneyPhase;
import com.gien.gits.customerjourney.PostvisitAnalysis;
import com.gien.gits.customerjourney.PrevisitReport;
import com.gien.gits.customerjourney.ProductCandidateClaim;
import com.gien.gits.ontology.CaseStatus;
import com.gien.gits.ontology.CaseType;
import com.gien.gits.ontology.Channel;
import com.gien.gits.ontology.Claim;
import com.gien.gits.ontology.ClaimStatus;
import com.gien.gits.ontology.ClaimType;
import com.gien.gits.ontology.Interaction;
import com.gien.gits.ontology.Interaction.Direction;
import com.gien.gits.ontology.Interaction.InteractionOutcome;
import com.gien.gits.ontology.Interaction.InteractionType;
import com.gien.gits.ontology.Interaction.Participant;
import com.gien.gits.ontology.OperatingCase;

/**
 * Spring Boot integration test: Flyway V001+V002 + JDBC repositories round-trip.
 * Exercises H2 in-memory persistence for M17→M22 chain entities.
 */
@SpringBootTest
@TestPropertySource(properties = {
    "spring.datasource.url=jdbc:h2:mem:integration-test;DB_CLOSE_DELAY=-1;MODE=MySQL",
    "spring.flyway.clean-disabled=false"
})
class PersistenceIntegrationTest {

    @Autowired private JdbcTemplate jdbcTemplate;
    @Autowired private WritableOperatingCaseRepository caseRepo;
    @Autowired private WritableInteractionRepository interactionRepo;
    @Autowired private WritableClaimRepository claimRepo;
    @Autowired private WritableCustomerJourneyRepository journeyRepo;

    private OperatingCase sampleCase() {
        Instant now = Instant.now();
        return new OperatingCase(UUID.randomUUID(), CaseType.CONTINUOUS_ENGAGEMENT,
                CaseStatus.OPEN, "integration-test", now, null, now, "test-runner");
    }

    @Test
    void flywayMigrationCreatesAllTables() {
        List<String> tables = jdbcTemplate.queryForList(
                "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'PUBLIC'",
                String.class);
        assertTrue(tables.contains("OPERATING_CASE"), "V001 operating_case");
        assertTrue(tables.contains("INTERACTION"), "V002 interaction");
        assertTrue(tables.contains("CLAIM"), "V002 claim");
        assertTrue(tables.contains("EVIDENCE"), "V002 evidence");
        assertTrue(tables.contains("CUSTOMER_JOURNEY"), "V002 customer_journey");
        assertTrue(tables.contains("INSIGHT_CLAIM"), "V002 insight_claim");
        assertTrue(tables.contains("PRODUCT_CANDIDATE_CLAIM"), "V002 product_candidate");
        assertTrue(tables.contains("PREVISIT_REPORT"), "V002 previsit_report");
        assertTrue(tables.contains("POSTVISIT_ANALYSIS"), "V002 postvisit_analysis");
    }

    @Test
    void operatingCaseCrudRoundTrip() {
        OperatingCase oc = sampleCase();
        caseRepo.save(oc);

        var found = caseRepo.findById(oc.caseId());
        assertTrue(found.isPresent());
        assertEquals(CaseType.CONTINUOUS_ENGAGEMENT, found.get().caseType());
        assertEquals(CaseStatus.OPEN, found.get().status());
    }

    @Test
    void interactionRoundTrip() {
        OperatingCase oc = sampleCase();
        caseRepo.save(oc);
        UUID journeyId = UUID.randomUUID();

        Participant ai = new Participant("AI-INSIGHT-01",
                Participant.Role.AI_AGENT, "AI洞察引擎");
        Participant rm = new Participant("RM-WANG-LEI",
                Participant.Role.RELATIONSHIP_MANAGER, "王磊");

        Interaction interaction = new Interaction(
                UUID.randomUUID(), oc.caseId(), journeyId,
                InteractionType.AI_INSIGHT_PUSH, Direction.OUTBOUND, Channel.SYSTEM_PUSH,
                ai, List.of(ai, rm),
                "跨境结算量增长42%，有套期保值需求",
                List.of(), InteractionOutcome.INFORMATION_GATHERED,
                Instant.now(), null, "sha256:abc123");

        interactionRepo.save(interaction);

        var found = interactionRepo.findById(interaction.interactionId());
        assertTrue(found.isPresent());
        assertEquals(InteractionType.AI_INSIGHT_PUSH, found.get().type());
        assertEquals(Direction.OUTBOUND, found.get().direction());
        assertNotNull(found.get().initiator());
        assertEquals("AI-INSIGHT-01", found.get().initiator().participantId());

        var byCase = interactionRepo.findByCaseId(oc.caseId());
        assertEquals(1, byCase.size());

        var all = interactionRepo.findAll();
        assertTrue(all.stream().anyMatch(item -> item.interactionId().equals(interaction.interactionId())));
    }

    @Test
    void claimCrudRoundTrip() {
        OperatingCase oc = sampleCase();
        caseRepo.save(oc);

        Claim claim = new Claim(UUID.randomUUID(), oc.caseId(), ClaimType.OPPORTUNITY,
                ClaimStatus.CANDIDATE, "跨境结算增长42%触发KYC",
                Instant.now(), null, Instant.now(), null);
        claimRepo.save(claim);

        var found = claimRepo.findById(claim.claimId());
        assertTrue(found.isPresent());
        assertEquals(ClaimStatus.CANDIDATE, found.get().status());

        claimRepo.updateStatus(claim.claimId(), ClaimStatus.VERIFIED_FACT);
        var updated = claimRepo.findById(claim.claimId());
        assertTrue(updated.isPresent());
        assertEquals(ClaimStatus.VERIFIED_FACT, updated.get().status());
    }

    @Test
    void customerJourneyFullChainRoundTrip() {
        OperatingCase oc = sampleCase();
        caseRepo.save(oc);

        // M17: 开户
        UUID journeyId = UUID.randomUUID();
        Instant now = Instant.now();
        CustomerJourney journey = new CustomerJourney(journeyId, oc.caseId(),
                "CUST-XINDA-001", "鑫达贸易有限公司",
                JourneyPhase.KYC_COLLECT, now, now);
        journeyRepo.saveJourney(journey);

        var foundJourney = journeyRepo.findJourneyById(journeyId);
        assertTrue(foundJourney.isPresent());
        assertEquals("鑫达贸易有限公司", foundJourney.get().customerName());

        // M18: 洞察
        UUID claimId = UUID.randomUUID();
        claimRepo.save(new Claim(claimId, oc.caseId(), ClaimType.OPPORTUNITY,
                ClaimStatus.CANDIDATE, "远期结售汇需求", now, null, now, null));
        UUID insightId = UUID.randomUUID();
        InsightClaim insight = new InsightClaim(insightId, claimId, oc.caseId(),
                "OPPORTUNITY", "客户有套期保值需求", now);
        journeyRepo.saveInsight(insight);

        var foundInsight = journeyRepo.findInsightById(insightId);
        assertTrue(foundInsight.isPresent());
        assertEquals("OPPORTUNITY", foundInsight.get().insightCategory());

        // M20: 产品候选
        UUID productClaimId = UUID.randomUUID();
        claimRepo.save(new Claim(productClaimId, oc.caseId(), ClaimType.PRODUCT_CANDIDATE,
                ClaimStatus.CANDIDATE, "推荐远期结售汇", now, null, now, null));
        UUID productId = UUID.randomUUID();
        ProductCandidateClaim product = new ProductCandidateClaim(productId,
                productClaimId, insightId, oc.caseId(),
                "FX-HEDGE-01", "远期结售汇", "匹配跨境结算+套期保值需求", now);
        journeyRepo.saveProductCandidate(product);

        var foundProduct = journeyRepo.findProductCandidateById(productId);
        assertTrue(foundProduct.isPresent());
        assertEquals("FX-HEDGE-01", foundProduct.get().productCode());

        // M21: 访前报告
        UUID reportId = UUID.randomUUID();
        PrevisitReport report = new PrevisitReport(reportId, oc.caseId(), journeyId,
                List.of(insightId), List.of(productId),
                "建议拜访客户讨论远期结售汇方案", now);
        journeyRepo.savePrevisitReport(report);

        var foundReport = journeyRepo.findPrevisitReportById(reportId);
        assertTrue(foundReport.isPresent());
        assertEquals(1, foundReport.get().insightIds().size());

        // M22: 访后分析
        UUID analysisId = UUID.randomUUID();
        PostvisitAnalysis analysis = new PostvisitAnalysis(analysisId, oc.caseId(),
                journeyId, reportId, "客户同意试用远期结售汇产品", "跟进签约流程", now);
        journeyRepo.savePostvisitAnalysis(analysis);

        var foundAnalysis = journeyRepo.findPostvisitAnalysisById(analysisId);
        assertTrue(foundAnalysis.isPresent());
        assertEquals("客户同意试用远期结售汇产品", foundAnalysis.get().outcome());
    }
}
