package com.gien.gits.knowledge.gkke.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.List;

/**
 * GK-KE v1 激活计划步骤（CTR-GKKE-005 / C06 §2）。
 *
 * @param stepId      步骤 ID
 * @param executorRef 执行器引用（能力或查询 ID）
 * @param dependencies 依赖步骤 ID
 * @param sideEffect  副作用级别（READ_ONLY/SUGGESTION/WRITE）
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public record PlanStep(
        String stepId,
        String executorRef,
        List<String> dependencies,
        String sideEffect) {
}
