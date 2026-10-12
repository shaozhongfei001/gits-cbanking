#!/usr/bin/env python3
"""生成 GK-KE L5-2 LightRAG 试验夹具（C08 L5-2 / wave C3）。

依据 C05「LightRAG 试验」路径与启用门槛。
本包结论：**门槛未满足 → 不启用，保留基础路线**（C05：不满足保留基础路线）。
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "specs" / "knowledge-architecture" / "lightrag"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    experiment_config = {
        "simulationOnly": True,
        "adapter": "LightRagAdapter",
        "isolatedWorkspace": True,
        "workspacePath": "specs/knowledge-architecture/lightrag/workspace",
        "directAuthorityWrites": False,
        "version": "1.4.0",
        "versionLocked": True,
        "prerequisiteForBaselineLoop": False,
        "note": "LightRAG 为可关闭试验，不得成为基础闭环的新增前置（C08 L5-2 / L0-2 规划规则 6）。",
    }

    # 受测 Spike 报告：门槛未满足
    spike_report = {
        "simulationOnly": True,
        "spikeId": "SIM-LR-SPIKE-001",
        "sampleReporting": {
            "sampleSize": 40,
            "confidenceInterval": "95% CI 为 ±6.2 个百分点（小样本）",
            "failureCases": [
                {"case": "F-01", "reason": "跨文档实体归一对齐错误"},
                {"case": "F-02", "reason": "主题组边界过宽，包含无权来源"},
            ],
        },
        "criticalNegativeFailures": 1,       # 关键负例未零失败
        "accuracyBaseline": 72.5,            # A（既有 RAG）
        "accuracyB": 78.0,                   # B（图谱基线）
        "accuracyC": 82.5,                   # C（LightRAG 试验）
        "criticalRegressions": 1,            # 存在关键退化
        "ownerAcceptedCostValue": False,     # 成本/价值未获接受
        "improvementOverBaselinePP": 10.0,
        "improvementOverBPP": 4.5,           # 相较 B 仅 +4.5pp，未达 10pp
        "enabled": False,
        "waived": False,
        "decision": "KEEP_BASELINE_ROUTE",
        "decisionBasis": "C05 门槛未满足：关键负例非零失败、相较 B 未达 10pp、存在关键退化、成本价值未获接受",
        # 反例夹具：证明门槛判定真实可拒
        "counterExample": {
            "criticalNegativeFailures": 2,
            "accuracyBaseline": 70.0,
            "accuracyB": 72.0,
            "criticalRegressions": 3,
            "ownerAcceptedCostValue": False,
            "sampleReporting": {"sampleSize": 5, "confidenceInterval": "n/a", "failureCases": []},
        },
    }

    abc_comparison = {
        "simulationOnly": True,
        "arms": {
            "A": {"name": "既有向量 RAG（ExistingRagAdapter）", "accuracy": 72.5,
                  "perQuestionResults": [{"q": "Q1", "correct": True}, {"q": "Q2", "correct": False}],
                  "cost": {"indexingHours": 2, "queryMs": 120, "storageMB": 40}},
            "B": {"name": "图谱基线（KuzuGraphAdapter）", "accuracy": 78.0,
                  "perQuestionResults": [{"q": "Q1", "correct": True}, {"q": "Q2", "correct": True}],
                  "cost": {"indexingHours": 6, "queryMs": 200, "storageMB": 120}},
            "C": {"name": "LightRAG 试验", "accuracy": 82.5,
                  "perQuestionResults": [{"q": "Q1", "correct": True}, {"q": "Q2", "correct": True}],
                  "cost": {"indexingHours": 18, "queryMs": 480, "storageMB": 640}},
        },
        "note": "C05：该阈值是待签合同目标，未报告为实际结果；本包按实际测值登记且未启用。",
    }

    violations = {
        "simulationOnly": True,
        "violations": [
            {"case": "gate_not_passed_keep_baseline", "expectedError": "GATE_NOT_PASSED_KEEP_BASELINE",
             "description": "门槛未满足必须保留基础路线", "detected": True},
            {"case": "authority_direct_write", "expectedError": "AUTHORITY_DIRECT_WRITE_REJECTED",
             "description": "禁止直连权威写入口", "detected": True},
            {"case": "insufficient_sample", "expectedError": "INSUFFICIENT_SAMPLE_REPORTED",
             "description": "样本量不足须如实报告", "detected": True},
            {"case": "lightrag_as_prerequisite", "expectedError": "LIGHTRAG_AS_PREREQUISITE_REJECTED",
             "description": "LightRAG 不得成为基础闭环前置", "detected": True},
        ],
    }

    for name, doc in (("experiment_config", experiment_config), ("spike_report", spike_report),
                      ("abc_comparison", abc_comparison), ("violations", violations)):
        (OUT / f"{name}.json").write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("L5-2 lightrag fixtures generated")
    print("  decision=KEEP_BASELINE_ROUTE (C05 gate not met)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
