package com.gien.gits.knowledge.gkke.plan;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.gien.gits.knowledge.gkke.model.ActivationPlanRecord;
import com.gien.gits.knowledge.hash.CanonicalHash;
import com.gien.gits.knowledge.hash.CanonicalJson;
import java.util.Map;
import java.util.Objects;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * GK-KE v1 激活计划规范化哈希器（CR-02 §4.4，验收 T20）。
 *
 * <p>哈希载荷为排除自引用字段 {@code planHash} 后的完整计划对象，规范化规则与
 * 造数侧 Python 严格对齐（C08/T35）：NFC + 键排序 + 紧凑分隔符 + 非 ASCII 原样，
 * 再做 UTF-8 SHA-256。
 */
public final class PlanCanonicalHasher {

    private static final Logger LOG = LoggerFactory.getLogger(PlanCanonicalHasher.class);
    private static final String PLAN_HASH_FIELD = "planHash";

    private final ObjectMapper objectMapper;

    public PlanCanonicalHasher() {
        this(new ObjectMapper());
    }

    public PlanCanonicalHasher(ObjectMapper objectMapper) {
        this.objectMapper = Objects.requireNonNull(objectMapper, "objectMapper must not be null");
    }

    /** 计算计划的规范化 JSON（不含 planHash 自引用字段）。 */
    public String canonicalJson(ActivationPlanRecord plan) {
        Objects.requireNonNull(plan, "plan must not be null");
        Map<String, Object> payload = objectMapper.convertValue(plan, Map.class);
        payload.remove(PLAN_HASH_FIELD);
        return CanonicalJson.canonicalize(payload);
    }

    /** 计算计划规范化 SHA-256（64 位小写十六进制）。 */
    public String planHash(ActivationPlanRecord plan) {
        return CanonicalHash.sha256Hex(canonicalJson(plan));
    }

    /** 返回带计算哈希的新计划记录（不可变记录的派生副本）。 */
    public ActivationPlanRecord withComputedHash(ActivationPlanRecord plan) {
        return new ActivationPlanRecord(plan.contractVersion(), plan.simulationOnly(), plan.planId(),
                plan.taskId(), plan.mapRef(), plan.releaseId(), plan.coreVersion(),
                plan.catalogRevision(), plan.routePolicyVersion(), plan.assetRefs(),
                plan.capabilityRefs(), plan.queryRefs(), plan.steps(), plan.permissionDecisionRef(),
                plan.purpose(), plan.scope(), plan.budget(), planHash(plan));
    }

    /** 校验计划内嵌 planHash 与重算值一致。 */
    public boolean verify(ActivationPlanRecord plan) {
        String expected = plan.planHash();
        if (expected == null || expected.isBlank()) {
            return false;
        }
        boolean valid = expected.equals(planHash(plan));
        if (!valid) {
            LOG.info("Plan hash verification failed: planId={}", plan.planId());
        }
        return valid;
    }
}
