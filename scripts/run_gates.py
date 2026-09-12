#!/usr/bin/env python3
"""GK-KE 门禁套件执行器。

【为什么需要它】
原 `make check` 以 `@$(PYTHON) script.py` 逐条串行执行，**在第一个失败处即停止**，
导致后续门禁结果被隐藏 —— 一个失败会掩盖其余全部结论。

本执行器改为：
  1. **跑完全部门的检查**，不因单个失败中断；
  2. 汇总输出一张结果表；
  3. 若任一门禁失败，整体退出非零，并**明确列出失败项**。

【设计约束】
  - 不修改任何门禁脚本的判定逻辑，只改变"如何执行与汇总"；
  - 每项门禁的退出码即其真实结论（BLOCKED 类门禁亦返回非零）；
  - 输出中显式区分「通过 / 失败 / 阻断」，避免把"阻断"读成"失败"或反之。

用法：
  python3 scripts/run_gates.py            # 运行全部门禁
  python3 scripts/run_gates.py --json     # 机器可读
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable

# (名称, 命令, 类别)
# 类别：integrity=合同与制品完整性 / readiness=就绪度 / security=安全基线
GATES = [
    ("contract-check",          ["bash", "scripts/check-contracts.sh"], "integrity"),
    ("loop-guard",              [PY, "scripts/loop_guard.py", "--template-check"], "integrity"),
    ("secret-scan",             [PY, "scripts/secret_scan.py", "--root", ".", "--quiet"], "security"),
    ("enum-consistency",        [PY, "scripts/enum_consistency_check.py", "--root", ".", "--quiet"], "integrity"),
    ("semantic-rule-gate",      [PY, "scripts/semantic_rule_gate.py"], "integrity"),
    ("contract-examples",       [PY, "scripts/gk_ke_contract_examples.py"], "integrity"),
    ("registry-contract",       [PY, "scripts/gk_ke_l2_2_registry_tests.py"], "integrity"),
    ("probe-mutation-tests",    [PY, "scripts/gk_ke_capability_probe_tests.py"], "integrity"),
    ("metric-definitions",      [PY, "scripts/gk_ke_metric_definitions_check.py"], "integrity"),
    ("product-card",            [PY, "scripts/gk_ke_product_card_check.py"], "integrity"),
    ("dataset-v2",              [PY, "scripts/generate_gk_ke_dataset_v2.py", "--verify"], "integrity"),
    ("acceptance-pack",         [PY, "scripts/gk_ke_acceptance_pack.py"], "integrity"),
    ("capability-probe",        [PY, "scripts/gk_ke_capability_probe.py"], "readiness"),
    ("counterfactual-test",     [PY, "scripts/gk_ke_counterfactual_test.py"], "readiness"),
    ("chain-trace",             [PY, "scripts/gk_ke_chain_trace.py"], "readiness"),
    ("semantic-consumption",    [PY, "scripts/gk_ke_semantic_consumption.py"], "readiness"),
    ("plan-compiler",           [PY, "scripts/gk_ke_plan_compiler.py"], "readiness"),
]


def run(cmd: list[str]) -> tuple[int, str]:
    try:
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=600)
        out = (proc.stdout or "") + (proc.stderr or "")
        return proc.returncode, out.strip()
    except subprocess.TimeoutExpired:
        return 124, "TIMEOUT"
    except Exception as exc:  # noqa: BLE001
        return 125, f"EXEC_ERROR {type(exc).__name__}: {exc}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--only", help="只跑名称匹配的门禁（子串匹配）")
    args = parser.parse_args()

    gates = GATES
    if args.only:
        gates = [g for g in gates if args.only in g[0]]

    results = []
    t0 = time.time()
    for name, cmd, kind in gates:
        rc, out = run(cmd)
        # 取最后一行有意义输出作为摘要
        lines = [l for l in out.splitlines() if l.strip()]
        summary = lines[0][:110] if lines else ""
        verdict = "PASS" if rc == 0 else ("BLOCKED" if "BLOCKED" in out else "FAIL")
        results.append({"name": name, "kind": kind, "exitCode": rc,
                        "verdict": verdict, "summary": summary, "output": out})
        mark = {"PASS": "PASS   ", "BLOCKED": "BLOCKED", "FAIL": "FAIL   "}[verdict]
        print(f"  [{mark}] {name:22s} exit={rc}")
        if verdict != "PASS" and summary:
            print(f"           {summary}")

    elapsed = time.time() - t0
    failed = [r for r in results if r["exitCode"] != 0]
    readiness_failed = [r for r in failed if r["kind"] == "readiness"]
    integrity_failed = [r for r in failed if r["kind"] != "readiness"]

    print()
    print(f"gk-ke-gates: {len(results) - len(failed)}/{len(results)} passed "
          f"in {elapsed:.1f}s")
    if integrity_failed:
        print(f"  INTEGRITY FAILURES: {[r['name'] for r in integrity_failed]}")
    if readiness_failed:
        # 就绪度未达成**必须被打印**（不得静默），但**不计入门禁失败**。
        # 理由见 docs/architecture/GK-KE-门禁语义与fail-closed边界-V1.0.md §1.2：
        # 若把未达成计入门禁失败，会制造"为让门禁变绿而把未达成改写成通过"的诱因，
        # 而这正是本项目已经发生过的错误模式。
        print(f"  READINESS NOT MET:  {[r['name'] for r in readiness_failed]}")
        print("  NOTE: 就绪度未达成**不计入本门禁失败**，但**必须**被如实声明。")
        print("        结论由收口文档明确写出，门禁只负责暴露事实。")
        print("        单独自查请运行: make readiness")

    if integrity_failed:
        print()
        print(f"gk-ke-gates: FAIL ({len(integrity_failed)} 项完整性失败) — "
              "见上表；不得声称制品完整。", file=sys.stderr)
        rc = 1
    else:
        rc = 0

    if args.json:
        print(json.dumps(
            {"total": len(results), "failed": [r["name"] for r in failed],
             "integrityFailed": [r["name"] for r in integrity_failed],
             "readinessNotMet": [r["name"] for r in readiness_failed],
             "gateExitCode": rc,
             "semantics": ("退出码只反映完整性；就绪度未达成仅报告不计入。"
                           "make check 通过不等于一切就绪。"),
             "results": [{k: v for k, v in r.items() if k != "output"} for r in results]},
            ensure_ascii=False, indent=2))

    return rc


if __name__ == "__main__":
    raise SystemExit(main())
