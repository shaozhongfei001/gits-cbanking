package com.gien.gits.knowledge.gkke.plan;

import static org.assertj.core.api.Assertions.assertThat;

import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.gien.gits.knowledge.gkke.model.ActivationPlanRecord;
import java.io.IOException;
import java.net.URISyntaxException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

/**
 * GK1 G4 激活计划规范化哈希黄金测试（CR-02 §4.4，验收 T20）。
 *
 * <p>黄金字节由 Python 造数侧算法生成（{@code json.dumps(sort_keys=True,
 * separators=(',',':'), ensure_ascii=False)} + NFC + SHA-256），
 * 与候选包 build_contract_examples 严格对齐。
 */
class PlanHashGoldenTest {

    private static final ObjectMapper MAPPER =
            new ObjectMapper().configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);

    private static ActivationPlanRecord goldenPlan;
    private static String goldenCanonical;
    private static String goldenHash;
    private static PlanCanonicalHasher hasher;

    @BeforeAll
    static void loadGolden() throws Exception {
        goldenPlan = MAPPER.readValue(resource("gk-ke-registry/plans/activation-plan.golden.json").toFile(),
                ActivationPlanRecord.class);
        goldenCanonical = Files.readString(
                resource("gk-ke-registry/plans/activation-plan.canonical.json")).trim();
        goldenHash = Files.readString(
                resource("gk-ke-registry/plans/activation-plan.sha256")).trim();
        hasher = new PlanCanonicalHasher(MAPPER);
    }

    @Test
    @DisplayName("Java 规范化 JSON 与 Python 黄金字节逐字节一致")
    void canonicalJsonMatchesGoldenBytes() {
        assertThat(hasher.canonicalJson(goldenPlan)).isEqualTo(goldenCanonical);
    }

    @Test
    @DisplayName("Java SHA-256 与 Python 黄金哈希一致（64 位小写十六进制）")
    void planHashMatchesGolden() {
        String hash = hasher.planHash(goldenPlan);

        assertThat(hash).isEqualTo(goldenHash);
        assertThat(hash).hasSize(64).matches("[0-9a-f]{64}");
    }

    @Test
    @DisplayName("planHash 自引用字段不参与哈希载荷")
    void planHashFieldExcludedFromPayload() {
        assertThat(hasher.canonicalJson(goldenPlan)).doesNotContain("planHash");
    }

    @Test
    @DisplayName("withComputedHash 派生带哈希副本，verify 校验通过")
    void withComputedHashAndVerify() {
        ActivationPlanRecord signed = hasher.withComputedHash(goldenPlan);

        assertThat(signed.planHash()).isEqualTo(goldenHash);
        assertThat(hasher.verify(signed)).isTrue();
    }

    @Test
    @DisplayName("篡改任一引用后哈希变化，verify 失败")
    void tamperedPlanFailsVerification() {
        ActivationPlanRecord signed = hasher.withComputedHash(goldenPlan);
        ActivationPlanRecord tampered = new ActivationPlanRecord(signed.contractVersion(),
                signed.simulationOnly(), signed.planId(), signed.taskId(), signed.mapRef(),
                "REL-TAMPERED", signed.coreVersion(), signed.catalogRevision(),
                signed.routePolicyVersion(), signed.assetRefs(), signed.capabilityRefs(),
                signed.queryRefs(), signed.steps(), signed.permissionDecisionRef(),
                signed.purpose(), signed.scope(), signed.budget(), signed.planHash());

        assertThat(hasher.verify(tampered)).isFalse();
        assertThat(hasher.planHash(tampered)).isNotEqualTo(goldenHash);
    }

    @Test
    @DisplayName("缺失 planHash 的计划 verify 返回 false")
    void missingHashFailsVerification() {
        assertThat(hasher.verify(goldenPlan)).isFalse();
    }

    private static Path resource(String name) throws URISyntaxException {
        return Paths.get(PlanHashGoldenTest.class.getResource("/" + name).toURI());
    }
}
