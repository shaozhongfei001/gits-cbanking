package com.gien.gits.adapter.skill;

/**
 * DKWS 异步作业轮询快照 — {@code GET /v1/jobs/{jobId}} 单次响应。
 *
 * @param status      job 状态：PENDING | RUNNING | COMPLETED | FAILED
 * @param skillResult COMPLETED 时 {@code data.skill_result}（完整 execute 响应）的 JSON 文本；否则 null
 */
public record JobStatusRecord(String status, String skillResult) {
}
