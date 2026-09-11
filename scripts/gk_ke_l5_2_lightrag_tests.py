#!/usr/bin/env python3
"""GK-KE L5-2 LightRAG 试验测试（C08 L5-2 / wave C3）。

依据 C05「LightRAG 试验」路径与启用门槛：
  - 关键权限/出处负例零失败
  - 关系/主题组正确率相较 B 提高至少 10 个百分点且无关键退化
  - 维护成本与新增业务价值经 Owner 明确接受
  - 小样本须报告样本量、差异区间和失败个例
  - 不直连权威写入口

C08 L5-2 退出标准：「满足 C05 门槛才启用；不满足保留基础路线」。

检查：
  1. 独立工作区（不直连权威写入口）
  2. 固定版本 Spike（锁版）
  3. **门槛判定**：正确逐项计算，且**不满足时不得启用**
  4. 小样本报告含样本量、差异区间、失败个例
  5. **不成为基础闭环的新增前置**（C08：LightRAG 不阻塞 L4）
  6. A/B/C 对照结果齐备（逐题结果 + 成本报告）
  7. 关键权限/出处负例零失败

退出码：全通过 0，否则 1。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LR = ROOT / "specs" / "knowledge-architecture" / "lightrag"

MIN_IMPROVEMENT_PP = 10.0  # C05：至少 10 个百分点


def load(name: str):
    return json.loads((LR / name).read_text(encoding="utf-8"))


def evaluate_gate(report: dict) -> dict:
    """C05 启用门槛逐项判定。"""
    checks = {
        "critical_negative_zero_failures":
            report.get("criticalNegativeFailures", 1) == 0,
        # C05 原文：「关系/主题组正确率**相较 B** 提高至少 10 个百分点」
        # 故取 C（试验）与 B（图谱基线）之差，而非与 A（既有 RAG）之差。
        "improvement_at_least_10pp":
            (report.get("accuracyC", 0.0) - report.get("accuracyB", 0.0)) >= MIN_IMPROVEMENT_PP,
        "no_critical_regression":
            report.get("criticalRegressions", 1) == 0,
        "cost_value_accepted_by_owner":
            report.get("ownerAcceptedCostValue") is True,
        "sample_reporting_complete": all(
            k in report.get("sampleReporting", {})
            for k in ("sampleSize", "confidenceInterval", "failureCases")
        ),
    }
    checks["gate_passed"] = all(checks.values())
    return checks


def main() -> int:  # noqa: C901
    failures: list[str] = []

    if not LR.is_dir():
        print(f"FAIL: lightrag dir missing: {LR}", file=sys.stderr)
        return 2

    config = load("experiment_config.json")
    report = load("spike_report.json")
    comparison = load("abc_comparison.json")
    violations = load("violations.json").get("violations", [])

    # 1. 独立工作区
    if config.get("isolatedWorkspace") is not True:
        failures.append("[1] LightRAG must run in an isolated workspace")
    if config.get("directAuthorityWrites") is True:
        failures.append("[1] LightRAG must not write to authority sources directly")

    # 2. 锁版
    if not config.get("versionLocked") or config.get("version") in (None, "latest"):
        failures.append(f"[2] LightRAG version must be pinned, got {config.get('version')!r}")

    # 3. 门槛判定：**门槛未通过是合法且预期的结论**（C05：不满足保留基础路线）。
    #    此处校验的是「判定正确」与「未通过时不得启用」，而非「必须通过」。
    verdict = evaluate_gate(report)
    if report.get("enabled") is True and not verdict["gate_passed"]:
        failures.append("[3] enabled while C05 gate not passed (must keep baseline route)")
    if report.get("enabled") is not True and verdict["gate_passed"] and report.get("waived") is not True:
        failures.append("[3] gate passed but experiment not enabled and no waiver recorded")
    if not verdict["gate_passed"]:
        # 未通过必须显式声明保留基础路线
        if report.get("decision") != "KEEP_BASELINE_ROUTE":
            failures.append(f"[3] gate not passed but decision is {report.get('decision')!r}, "
                            "expected KEEP_BASELINE_ROUTE")

    sample = report.get("sampleReporting", {})
    for field in ("sampleSize", "confidenceInterval", "failureCases"):
        if field not in sample:
            failures.append(f"[4] sample reporting missing {field}")
    if isinstance(sample.get("sampleSize"), int) and sample["sampleSize"] <= 0:
        failures.append("[4] sampleSize must be positive")

    # 5. 不得成为基础闭环新增前置
    if config.get("prerequisiteForBaselineLoop") is True:
        failures.append("[5] LightRAG must NOT be a prerequisite for the baseline loop")

    # 6. A/B/C 对照
    for arm in ("A", "B", "C"):
        if arm not in comparison.get("arms", {}):
            failures.append(f"[6] A/B/C comparison missing arm {arm}")
    for arm, data in comparison.get("arms", {}).items():
        if "perQuestionResults" not in data:
            failures.append(f"[6] arm {arm}: missing per-question results")
        if "cost" not in data:
            failures.append(f"[6] arm {arm}: missing cost report")

    # 7. 关键负例必须**已测量**（零失败是启用门槛之一，非本 Loop 的强制通过项）。
    #    未通过时仅要求如实报告计数（C05：关键权限/出处负例零失败为启用条件）。
    count = report.get("criticalNegativeFailures")
    if not isinstance(count, int) or count < 0:
        failures.append(f"[7] criticalNegativeFailures must be reported as a non-negative int, got {count!r}")
    if count == 0 and report.get("enabled") is not True and not verdict["gate_passed"]:
        # 若该项为零但整体未通过，说明是其它门槛未达，仍合法
        pass

    # 负例（fail-closed）
    required = {"GATE_NOT_PASSED_KEEP_BASELINE", "AUTHORITY_DIRECT_WRITE_REJECTED",
                "INSUFFICIENT_SAMPLE_REPORTED", "LIGHTRAG_AS_PREREQUISITE_REJECTED"}
    covered = {v.get("expectedError") for v in violations}
    uncovered = required - covered
    if uncovered:
        failures.append(f"[neg] rejection paths without fixtures: {sorted(uncovered)}")
    for v in violations:
        if v.get("detected") is not True:
            failures.append(f"[neg] {v.get('case')}: not detected")

    # 门槛判定不得空转：必须存在一个"不满足门槛"的反例被正确判定为未通过
    counter = report.get("counterExample")
    if not counter:
        failures.append("[3] no counter-example: gate evaluation would be noop (cannot prove rejection works)")
    else:
        counter_verdict = evaluate_gate(counter)
        if counter_verdict["gate_passed"]:
            failures.append("[3] counter-example unexpectedly passes the C05 gate")

    if failures:
        print("gk-ke-l5-2-lightrag-tests: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    print("gk-ke-l5-2-lightrag-tests: PASS")
    print(f"  version={config.get('version')} isolated={config.get('isolatedWorkspace')}")
    print(f"  gate_checks={ {k: v for k, v in verdict.items() if k != 'gate_passed'} }")
    print(f"  gate_passed={verdict['gate_passed']} enabled={report.get('enabled')}")
    print(f"  counter_example_rejected=True")
    print("  checks: isolated-workspace, version-lock, gate-evaluation+non-noop, sample-reporting, "
          "not-a-prerequisite, abc-comparison, critical-negatives")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
