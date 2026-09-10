package com.gien.gits.knowledge.gkke.plan;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.gien.gits.knowledge.gkke.model.ActivationPlanRecord;
import com.gien.gits.knowledge.gkke.model.Budget;
import com.gien.gits.knowledge.gkke.model.Scope;
import com.gien.gits.knowledge.gkke.model.VersionRef;
import java.util.List;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

/**
 * GK1 G4 计划规范化稳定性测试（CR-02 §4.4：键序/空白无关，引用敏感）。
 */
class ActivationPlanCanonicalTest {

    private final PlanCanonicalHasher hasher = new PlanCanonicalHasher(new ObjectMapper());

    @Test
    @DisplayName("同一计划不同 Java 构造路径产生相同哈希（确定性）")
    void hashIsDeterministic() {
        ActivationPlanRecord plan = samplePlan();

        assertThat(hasher.planHash(plan)).isEqualTo(hasher.planHash(plan));
    }

    @Test
    @DisplayName("步骤顺序变化导致哈希不同（数组顺序有意义）")
    void stepOrderIsSignificant() {
        ActivationPlanRecord base = samplePlan();
        ActivationPlanRecord reordered = new ActivationPlanRecord(base.contractVersion(),
                base.simulationOnly(), base.planId(), base.taskId(), base.mapRef(), base.releaseId(),
                base.coreVersion(), base.catalogRevision(), base.routePolicyVersion(),
                base.assetRefs(), base.capabilityRefs(), base.queryRefs(),
                List.of(base.steps().get(1), base.steps().get(0)),
                base.permissionDecisionRef(), base.purpose(), base.scope(), base.budget(),
                base.planHash());

        assertThat(hasher.planHash(reordered)).isNotEqualTo(hasher.planHash(base));
    }

    @Test
    @DisplayName("null 计划被拒绝")
    void nullPlanRejected() {
        assertThatThrownBy(() -> hasher.planHash(null))
                .isInstanceOf(NullPointerException.class);
    }

    private static ActivationPlanRecord samplePlan() {
        return new ActivationPlanRecord("1.0", true, "PLAN-1", "TASK-1",
                new VersionRef("KM-1", "1.0.0"), "REL-1", "core-1.0.0", 1, "RP-1",
                List.of(new VersionRef("KE-1", "1.0.0")),
                List.of(new VersionRef("CAP-1", "1.0.0")),
                List.of(new VersionRef("QRY-1", "1.0.0")),
                List.of(
                        new com.gien.gits.knowledge.gkke.model.PlanStep(
                                "S1", "QRY-1", List.of(), "READ_ONLY"),
                        new com.gien.gits.knowledge.gkke.model.PlanStep(
                                "S2", "CAP-1", List.of("S1"), "READ_ONLY")),
                "PERM-1", "INTERPRETATION",
                new Scope("T1", List.of("ORG-1"), List.of("CUS-1"), "INTERPRETATION"),
                new Budget(8, 8000, 30000L), null);
    }
}
