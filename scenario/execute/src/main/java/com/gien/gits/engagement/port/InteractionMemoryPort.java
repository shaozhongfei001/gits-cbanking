package com.gien.gits.engagement.port;

/**
 * SP-21 交互记忆端口（契约 v1.4 §3）。
 *
 * <p>生命周期归属 GITS：DKWS 只产出候选/更新/取代，不存记忆；确认、衰减、取代决策全在 GITS。</p>
 */
public interface InteractionMemoryPort {

    /**
     * 抽取交互记忆（同步，≤60s）。
     *
     * @param interactionId   交互 ID（GITS 生成）
     * @param customerId      客户 ID
     * @param interactionContent 交互纪要原文
     * @param existingMemories 既有记忆快照（memoryId/category/content/confidence）
     * @return 强类型抽取结果
     * @throws SkillExecutionException 抽取失败（网络/超时/422）
     */
    InteractionMemoryExtraction extract(
            String interactionId,
            String customerId,
            String interactionContent,
            java.util.List<java.util.Map<String, Object>> existingMemories);

    /**
     * 应用抽取结果到 GITS 记忆库（候选入 CANDIDATE、更新应用增量、取代置 SUPERSEDED）。
     * 生命周期归属 GITS，DKWS 无感知。
     *
     * @param extraction 抽取结果
     */
    void apply(InteractionMemoryExtraction extraction);
}
