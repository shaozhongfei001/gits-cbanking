"""需求ID -> 验收点可追踪矩阵（DKWS-SPEC-001 §17/§20，Gate P0）。

记录 DKWS-SPEC-001 各需求ID与实现的对应关系；`matrix` 供 CLI/测试检视。
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TraceEntry:
    req_id: str            # 规范中需求ID，如 R1、R2.3
    title: str
    module: str            # 对应实现模块
    phase: str             # P0..P9
    status: str = "in_progress"


def trace_matrix() -> list[TraceEntry]:
    return [
        TraceEntry("R1", "工作区五层结构与初始化", "workspace", "P0", "done"),
        TraceEntry("R2", "工作区元数据 dkws.meta.yaml", "workspace", "P0", "done"),
        TraceEntry("R3", "契约化 Markdown 框架", "contract", "P1", "done"),
        TraceEntry("R3.1", "frontmatter + schema 校验", "contract", "P1", "done"),
        TraceEntry("R3.2", "正文固定标题校验", "contract", "P1", "done"),
        TraceEntry("R4", "DSL 受限求值", "contract", "P1", "done"),
        TraceEntry("R5", "Raw 接入流水线", "ingest", "P2", "done"),
        TraceEntry("R5.1", "MANIFEST + SHA-256 幂等", "ingest", "P2", "done"),
        TraceEntry("R5.2", "任务状态机", "state", "P2", "done"),
        TraceEntry("R6", "结构化清洗与 Parquet", "projection", "P3", "done"),
        TraceEntry("R7", "文档登记与规范化", "docs", "P4", "done"),
        TraceEntry("R8", "稳定切片", "docs", "P4", "done"),
        TraceEntry("R9", "知识候选生成", "knowledge", "P5", "done"),
        TraceEntry("R10", "冲突检测", "knowledge", "P5", "done"),
        TraceEntry("R11", "审核决定", "knowledge", "P5", "done"),
        TraceEntry("R12", "Core 发布 + Release + CURRENT", "publish", "P6", "done"),
        TraceEntry("R13", "回滚", "publish", "P6", "done"),
        TraceEntry("R14", "Parquet 投影", "projection", "P7", "done"),
        TraceEntry("R15", "服务 JSON 通则", "service", "P8", "done"),
        TraceEntry("R16", "CLI 服务命令", "cli", "P8", "done"),
        TraceEntry("R17", "HTTP API", "http_api", "P8", "in_progress"),
        TraceEntry("R18", "安全/性能/E2E", "e2e", "P9", "pending"),
    ]


def apply_filters(items: list[TraceEntry], *, phase: str | None = None,
                  status: str | None = None) -> list[TraceEntry]:
    out = items
    if phase:
        out = [i for i in out if i.phase == phase]
    if status:
        out = [i for i in out if i.status == status]
    return out