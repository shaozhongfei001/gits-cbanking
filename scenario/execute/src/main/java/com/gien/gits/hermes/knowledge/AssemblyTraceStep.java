package com.gien.gits.hermes.knowledge;

import java.util.Objects;

/**
 * 知识条目装配轨迹步骤 — 供前端模拟控制台逐 KI 打印。
 *
 * <p>每个知识条目（KI）在"读图 → 取数 → 装配 → 完成"过程中产生多步轨迹；
 * 前端据此渲染实时滚动控制台（状态图标 + 时间戳 + 消息）。</p>
 *
 * @param kiId       知识条目 ID（如 KI-FRONT-001）
 * @param phase      阶段：READ_MAP / RESOLVE_BINDING / LOAD_DATA / ASSEMBLE / DONE / SKIPPED
 * @param dataAsset  绑定的数据资产（可为空）
 * @param dataPath   数据相对路径（可为空）
 * @param status     OK / EMPTY / FAILED
 * @param message    人类可读的步骤说明
 */
public record AssemblyTraceStep(String kiId, String phase, String dataAsset,
                                String dataPath, String status, String message) {

    public AssemblyTraceStep {
        Objects.requireNonNull(kiId, "kiId");
        Objects.requireNonNull(phase, "phase");
        status = status == null ? "OK" : status;
        message = message == null ? "" : message;
    }

    /** 该类完成步骤的快捷构造。 */
    public static AssemblyTraceStep done(String kiId, String message) {
        return new AssemblyTraceStep(kiId, "DONE", null, null, "OK", message);
    }

    public static AssemblyTraceStep skip(String kiId, String message) {
        return new AssemblyTraceStep(kiId, "SKIPPED", null, null, "EMPTY", message);
    }

    public static AssemblyTraceStep load(String kiId, String dataAsset, String dataPath,
                                         String message) {
        return new AssemblyTraceStep(kiId, "LOAD_DATA", dataAsset, dataPath, "OK", message);
    }
}