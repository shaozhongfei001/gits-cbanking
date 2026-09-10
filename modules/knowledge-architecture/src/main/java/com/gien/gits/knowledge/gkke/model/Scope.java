package com.gien.gits.knowledge.gkke.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.util.List;

/**
 * GK-KE v1 授权范围（CR-02 §4.1，C06 scope）。
 *
 * @param tenantId    租户 ID
 * @param orgIds      机构 ID 列表
 * @param customerIds 客户 ID 列表
 * @param purpose     用途（INTERPRETATION/RECOMMENDATION/RESEARCH 等）
 */
@JsonIgnoreProperties(ignoreUnknown = true)
public record Scope(String tenantId, List<String> orgIds, List<String> customerIds, String purpose) {
}
