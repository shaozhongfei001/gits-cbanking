package com.gien.gits.knowledge.gkke.permission;

import java.util.List;

/**
 * GK-KE v1 运行时权限上下文（CR-02 §4.1 scope + C06 purpose）。
 *
 * @param tenantId    调用方租户 ID
 * @param orgIds      调用方被授权的机构 ID
 * @param customerIds 调用方被授权的客户 ID
 * @param purpose     调用目的（INTERPRETATION/RECOMMENDATION/RESEARCH 等）
 */
public record PermissionContext(String tenantId, List<String> orgIds, List<String> customerIds,
                                String purpose) {

    public PermissionContext {
        orgIds = orgIds == null ? List.of() : List.copyOf(orgIds);
        customerIds = customerIds == null ? List.of() : List.copyOf(customerIds);
    }
}
