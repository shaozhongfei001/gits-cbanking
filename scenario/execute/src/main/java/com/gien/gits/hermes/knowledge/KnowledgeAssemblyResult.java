package com.gien.gits.hermes.knowledge;

import java.util.List;
import java.util.Objects;

/**
 * 知识装配结果 — 模拟访问知识的数据提供者输出。
 *
 * <p>对应 P23 生产 {@code KnowledgeAssembler.assemble} 的语义：输入 scope（知识地图）、
 * 知识条目（KI）列表与业务上下文，输出 LLM 可读的知识上下文 Markdown。本 record 是
 * scenario 影子/演示层的同构产物，供演示环境复用"先读图 → 按地图任务装配知识条目(KI→KE)"。</p>
 *
 * @param scope            知识地图/域范围（如 KM-CORP-RM-PREVISIT-DEMO）
 * @param assembledKiIds   实际装配到的知识条目 ID（非空）
 * @param knowledgeContext 装配后的知识上下文 Markdown
 * @param ruleRefs         本次装配引用的规则（RUL）列表
 * @param sourcePaths      本次装配读取的演示资产相对路径
 * @param trace            逐知识条目的装配轨迹（供前端模拟控制台打印）
 */
public record KnowledgeAssemblyResult(
        String scope,
        List<String> assembledKiIds,
        String knowledgeContext,
        List<String> ruleRefs,
        List<String> sourcePaths,
        List<AssemblyTraceStep> trace) {

    public KnowledgeAssemblyResult {
        Objects.requireNonNull(scope, "scope");
        Objects.requireNonNull(knowledgeContext, "knowledgeContext");
        assembledKiIds = List.copyOf(assembledKiIds != null ? assembledKiIds : List.of());
        ruleRefs = List.copyOf(ruleRefs != null ? ruleRefs : List.of());
        sourcePaths = List.copyOf(sourcePaths != null ? sourcePaths : List.of());
        trace = List.copyOf(trace != null ? trace : List.of());
    }

    /** 兼容旧 5 参构造（trace 置空）。 */
    public KnowledgeAssemblyResult(String scope, List<String> kiIds, String ctx,
                                   List<String> rules, List<String> sources) {
        this(scope, kiIds, ctx, rules, sources, List.of());
    }

    /**
     * 是否装配到了任何知识条目。
     */
    public boolean hasAssembledKi() {
        return !assembledKiIds.isEmpty();
    }
}