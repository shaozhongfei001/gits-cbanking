package com.gien.gits.api.productcenter;

import java.util.List;

/**
 * LightRAG 检索跟踪信息：记录请求链路、检索过程与耗时。
 *
 * <p>前端在右侧栏下方展示请求跟踪控制带，使检索过程可观测。</p>
 *
 * @param steps       请求链路步骤（按时间顺序）
 * @param lightrag    LightRAG 检索详情（null 表示未调用 LightRAG）
 * @param totalMs     总耗时（毫秒）
 */
public record RetrievalTrace(
        List<TraceStep> steps,
        LightRagTrace lightrag,
        long totalMs) {

    /** 请求链路步骤。 */
    public record TraceStep(
            String name,
            String description,
            long durationMs,
            String status) {
    }

    /** LightRAG 检索详情。 */
    public record LightRagTrace(
            String query,
            String mode,
            int entityCount,
            int relationCount,
            int citationCount,
            String evidenceClass,
            String provenanceState,
            Boolean simulationOnly,
            long retrievalMs,
            List<String> entityNames) {
    }
}
