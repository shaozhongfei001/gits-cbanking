#!/usr/bin/env python3
"""GK-KE 验收包（A4 / WP07）。

依据建议书 §14.3（三阶段交互与验收目标）、§14.4（评测样本与独立性）、
§14.1（三种验收分别作结论）。

本脚本**不模拟被测系统**，只做三件事：
  1. 校验评测案例集的结构完整性（60 例、三类分布、20 例排除调优）
  2. 校验**答案隔离**：world_truth 与 evaluation 不被 observation 污染
  3. 产出**逐例结果模板**，并区分「定义验收 / 运行验收 / 业务效果验收」

关键纪律（§14.4 原文）：
  - 关键条款、数值和严重边界**不由同一个生成模型自评分独立通过**
  - 规则效果须同时报告 **TP / FP / FN 和拒绝/不可评估数量**
  - **系统不能通过"全部 UNKNOWN"获得高准确率**

用法：
  python3 scripts/gk_ke_acceptance_pack.py            # 校验并报告
  python3 scripts/gk_ke_acceptance_pack.py --json     # 机器可读
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "scenario" / "seed" / "18_gk_ke_dataset_v2"
CASES = BASE / "evaluation" / "evaluation_cases.csv"
WORLD_TRUTH = BASE / "world_truth" / "world_truth.json"
OBSERVATION = BASE / "observation"
OUT = ROOT / "evidence" / "gk-ke-acceptance-pack"

REQUIRED_CATEGORIES = {
    "NORMAL_OR_OPPORTUNITY": 20,
    "ANOMALY_OR_LEGAL_EXPLANATION": 20,
    "BOUNDARY": 20,
}
MIN_TUNING_EXCLUDED = 20

# §14.3 要求的分类报告维度
REPORT_DIMENSIONS = [
    "正常", "缺资料", "不可比", "合法解释", "事件", "越权", "无答案", "版本失效",
]


def load_cases() -> list[dict]:
    if not CASES.is_file():
        return []
    with CASES.open(encoding="utf-8") as fh:
        return [r for r in csv.DictReader(fh)]


def check_structure(cases: list[dict]) -> list[str]:
    failures: list[str] = []
    if len(cases) != 60:
        failures.append(f"案例数应为 60，实为 {len(cases)}")

    dist = Counter(c["category"] for c in cases)
    for cat, expected in REQUIRED_CATEGORIES.items():
        if dist.get(cat, 0) != expected:
            failures.append(f"类别 {cat} 应 {expected} 例，实为 {dist.get(cat, 0)}")

    excluded = sum(1 for c in cases if c.get("tuningExcluded") == "True")
    if excluded < MIN_TUNING_EXCLUDED:
        failures.append(f"排除调优的案例应≥{MIN_TUNING_EXCLUDED}，实为 {excluded}")

    # 每个案例必须有禁止结论（防止只能"通过"的软答案）
    for c in cases:
        if not c.get("forbiddenConclusions"):
            failures.append(f"{c['caseId']} 缺 forbiddenConclusions")
            break

    # 场景族不得跨开发/验收重复（§14.4）
    fam_dev = {c["scenarioFamily"] for c in cases if c.get("tuningExcluded") != "True"}
    fam_eval = {c["scenarioFamily"] for c in cases if c.get("tuningExcluded") == "True"}
    overlap = fam_dev & fam_eval
    if overlap:
        failures.append(f"场景族跨越开发与验收集: {sorted(overlap)[:3]}")

    return failures


def check_isolation() -> list[str]:
    """答案隔离检查（§12.1）。"""
    failures: list[str] = []
    if not WORLD_TRUTH.is_file():
        failures.append("world_truth.json 缺失")
        return failures
    wt = json.loads(WORLD_TRUTH.read_text(encoding="utf-8"))

    if wt.get("accessPolicy") != "CONSTRUCTOR_AND_EVALUATOR_ONLY":
        failures.append("world_truth.accessPolicy 必须为 CONSTRUCTOR_AND_EVALUATOR_ONLY")
    if wt.get("mustNotBeVisibleTo") != "SYSTEM_UNDER_TEST":
        failures.append("world_truth.mustNotBeVisibleTo 必须为 SYSTEM_UNDER_TEST")

    # observation 层不得含答案字段
    secret_tokens = ["trueHiddenGaps", "trueLegalExplanations", "trueStandardCalculations"]
    for path in sorted(OBSERVATION.glob("*")):
        text = path.read_text(encoding="utf-8")
        for token in secret_tokens:
            if token in text:
                failures.append(f"observation/{path.name} 泄漏答案字段 {token}")
    return failures


def anti_degenerate_check() -> list[str]:
    """防退化假通过（§14.4：系统不能通过'全部 UNKNOWN'获得高准确率）。"""
    failures: list[str] = []
    cases = load_cases()
    # 每类至少有一例要求产出"实际结论"（allowedConclusions 非空且非 UNKNOWN 型）
    for cat in REQUIRED_CATEGORIES:
        subset = [c for c in cases if c["category"] == cat]
        productive = [
            c for c in subset
            if c.get("allowedConclusions") and "UNKNOWN" not in c["allowedConclusions"][0]
        ]
        if not productive:
            failures.append(f"类别 {cat} 无任何要求产出实际结论的案例 → 可被全 UNKNOWN 绕过")
    return failures


def build_result_template(cases: list[dict]) -> list[dict]:
    """逐例结果模板：含 TP/FP/FN 与拒绝/不可评估计数位（§14.4）。"""
    return [
        {
            "caseId": c["caseId"],
            "category": c["category"],
            "tuningExcluded": c.get("tuningExcluded") == "True",
            "expectedSignals": c.get("expectedSignals", ""),
            "forbiddenConclusions": c.get("forbiddenConclusions", ""),
            "actualSignals": None,
            "actualConclusions": None,
            "verdict": None,
            "tp": None, "fp": None, "fn": None,
            "refused": None,
            "notEvaluable": None,
            "note": "须由独立 QA 填写；禁止由生成模型自评分通过（§14.4）",
        }
        for c in cases
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    cases = load_cases()
    failures = []
    failures += check_structure(cases)
    failures += check_isolation()
    failures += anti_degenerate_check()

    dist = Counter(c["category"] for c in cases) if cases else Counter()
    excluded = sum(1 for c in cases if c.get("tuningExcluded") == "True")

    summary = {
        "caseCount": len(cases),
        "distribution": dict(dist),
        "tuningExcluded": excluded,
        "tuningIncluded": len(cases) - excluded,
        "isolationOk": not check_isolation(),
        "reportDimensions": REPORT_DIMENSIONS,
        "antiDegenerateOk": not anti_degenerate_check(),
        "acceptanceLayers": {
            "A_definition": "任务/知识/指标/规则/能力/接口可测试且业务含义明确",
            "B_runtime": "指定地图在指定环境真实调用所需能力，输入输出及失败行为可复核",
            "C_business": "客户经理在规定案例集上减少准备工作且保持质量",
            "rule": "三层分别作结论，不得互相替代（§14.1）",
        },
        "currentLayerStatus": {
            "A_definition": "PARTIAL",
            "B_runtime": "NOT_STARTED",
            "C_business": "NOT_STARTED",
        },
    }

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print("gk-ke-acceptance-pack: report")
        print(f"  cases: {len(cases)} | excluded from tuning: {excluded}")
        print(f"  distribution: {dict(dist)}")
        print(f"  isolation: {'OK' if summary['isolationOk'] else 'FAIL'}")
        print(f"  anti-degenerate: {'OK' if summary['antiDegenerateOk'] else 'FAIL'}")
        print("  layers: A=PARTIAL B=NOT_STARTED C=NOT_STARTED")

    if failures:
        print("gk-ke-acceptance-pack: FAIL", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result_template.json").write_text(
        json.dumps({
            "$comment": ("A4/WP07 逐例结果模板。须由独立 QA 填写；"
                         "禁止由生成模型自评分独立通过（§14.4）。"),
            "authority": "建议书 §14.1 / §14.3 / §14.4",
            "caseCount": len(cases),
            "results": build_result_template(cases),
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"  wrote: evidence/gk-ke-acceptance-pack/{{result_template,summary}}.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
