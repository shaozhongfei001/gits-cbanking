package com.gien.gits.engagement.port;

import java.util.Map;
import java.util.Objects;

/**
 * SKILL 执行命令 — 描述一次对 dsh SKILL 运行平台的激活请求。
 *
 * @param skillId    dsh 上的 Skill id（如 skill-customer-previsit-report）
 * @param requestId  幂等请求 ID（gits 侧生成）
 * @param customerId 客户 ID
 * @param request    业务请求上下文（字段随 Skill 不同；契约见跨端联调文档）
 * @param async      true 时走 202+jobId 异步作业（SP-20 长任务必须 async；缺省 false 同步）
 * @param context    ContextPackage（SP-20/SP-21 专用，契约 v1.4 §2.1；顶层 context 与
 *                   request.context 二选一，request.context 优先；缺省空 map）
 */
public record SkillExecutionCommand(
        String skillId,
        String requestId,
        String customerId,
        Map<String, Object> request,
        boolean async,
        Map<String, Object> context) {

    public SkillExecutionCommand {
        Objects.requireNonNull(skillId, "skillId");
        Objects.requireNonNull(requestId, "requestId");
        Objects.requireNonNull(customerId, "customerId");
        request = request == null ? Map.of() : Map.copyOf(request);
        context = context == null ? Map.of() : Map.copyOf(context);
    }

    /** 兼容 v1.3 调用点：同步执行、无 context。 */
    public SkillExecutionCommand(String skillId, String requestId, String customerId, Map<String, Object> request) {
        this(skillId, requestId, customerId, request, false, Map.of());
    }
}