package com.gien.gits.knowledge.gkke.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

/**
 * GK-KE v1 执行预算（CTR-GKKE-005）。
 *
 * @param maxSteps  最大步骤数
 * @param maxTokens 最大 token 数
 * @param timeoutMs 超时毫秒
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public record Budget(Integer maxSteps, Integer maxTokens, Long timeoutMs) {
}
