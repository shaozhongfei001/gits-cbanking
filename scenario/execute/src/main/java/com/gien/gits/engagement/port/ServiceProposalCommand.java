package com.gien.gits.engagement.port;

import java.util.Map;
import java.util.Objects;

/**
 * SP-20 服务建议书生成命令。
 *
 * @param requestId 幂等请求 ID（gits 侧生成）
 * @param customerId 客户 ID
 * @param context    ContextPackage（契约 v1.4 §2.1；enterpriseData/interactionMemories/previousReports 等）
 */
public record ServiceProposalCommand(
        String requestId,
        String customerId,
        Map<String, Object> context) {

    public ServiceProposalCommand {
        Objects.requireNonNull(requestId, "requestId");
        Objects.requireNonNull(customerId, "customerId");
        context = context == null ? Map.of() : Map.copyOf(context);
    }
}
