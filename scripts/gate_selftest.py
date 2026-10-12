#!/usr/bin/env python3
"""门禁自检：**对分类器注入已知故障，要求它给出正确分类**。

动因（Owner 要求：不能只写方法论，要回到源代码动手加固）：
    实测 18 个门禁 **0 个**有可复现的负例测试。
    "没有负例测试的门禁，其 PASS 不予采信" —— 故先给**分类器**建负例测试，
    因为所有门禁的结论都要经过它。

本脚本只覆盖 `run_gates.classify()` 与工具故障路径。
**其余门禁的负例测试尚未建立** —— 本脚本的 [COVERAGE] 段如实报告覆盖缺口，
**不得**把"部分覆盖"读作"全部已测"。

退出码：任一用例不符预期即非零（fail-closed）。
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("rg", ROOT / "scripts" / "run_gates.py")
rg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rg)

CASES = [
    # (标签, rc, 输出片段, 期望分类)
    ("正常通过", 0, "all good", "PASS"),
    # 新契约：门禁以**专用 token 行**声明结论（见 run_gates.VERDICT_RE）。
    # 旧用例用散文词/null-token 测，已随契约变更更新——
    # 这正是负例测试**应当**发生的事：契约一变，测试立即报错。
    ("token 声明无法判定", 0, "\n__GATE_VERDICT__=INCONCLUSIVE\n", "INCONCLUSIVE"),
    ("token 声明未达成", 0, "\n__GATE_VERDICT__=FAIL\n", "FAIL"),
    # 反向：散文里出现词，**不得**被当作结论（防误命中）
    ("散文含词不应命中", 0, "本项无法判定，但未声明 token", "PASS"),
    ("显式 BLOCKED", 1, "BLOCKED xxx", "BLOCKED"),
    ("真失败", 1, "assertion failed", "FAIL"),
    # ★ 关键用例：工具故障必须归 BLOCKED，**不得**归 FAIL
    ("缺依赖(ModuleNotFoundError)", 1,
     "Traceback...\nModuleNotFoundError: No module named 'jsonschema'", "BLOCKED"),
    ("缺模块(No module named)", 1, "No module named 'pyarrow'", "BLOCKED"),
    ("导入错误(ImportError)", 1, "ImportError: cannot import name 'x'", "BLOCKED"),
    ("语法错误", 1, "SyntaxError: invalid syntax", "BLOCKED"),
]

# 覆盖缺口：如实登记尚未建立负例测试的门禁
COVERAGE_UNCOVERED = [
    "contract-check", "loop-guard", "secret-scan", "enum-consistency",
    "semantic-rule-gate", "contract-examples", "contract-coverage",
    "registry-contract", "probe-mutation-tests", "metric-definitions",
    "product-card", "dataset-v2", "acceptance-pack",
    "capability-probe", "counterfactual-test", "chain-trace",
    "semantic-consumption", "plan-compiler",
]


def main() -> int:
    # **本脚本绝不能打印它自己所注入的标记文本。**
    # 分类器靠扫描输出去识别标记；若本脚本把标记词打进自己的 stdout，
    # 分类器会把**本脚本的用例内容**当成**本脚本的结论**。
    # 2026-09-13 实测：该问题在本次任务内**连续命中三次**
    # （中文散文词 → 英文 token → 工具故障标记），
    # 故此处只打印**序号与判定**，一切标记以 *** 遮蔽。
    REDACT = ("ModuleNotFoundError", "ImportError", "No module named", "SyntaxError",
              "IndentationError", "command not found", "BLOCKED", "INCONCLUSIVE",
              "NOT_MET", "未达成")
    print("gate-selftest（负例测试）")
    bad = 0
    for i, (label, rc, out, want) in enumerate(CASES, 1):
        got = rg.classify(rc, out)
        ok = got == want
        bad += 0 if ok else 1
        safe = label
        for m in REDACT:
            safe = safe.replace(m, "***")
        print(f"  {'OK ' if ok else 'BAD'} case{i:02d} {safe:26s} "
              f"rc={rc} → {got:12s} (期望 {want})")
    total, passed = len(CASES), len(CASES) - bad
    print(f"  分类器用例: {passed}/{total}")

    print()
    print("  [COVERAGE] **尚未建立负例测试的门禁**（其 PASS 不予采信）：")
    for name in COVERAGE_UNCOVERED:
        print(f"      - {name}")
    print(f"    合计 {len(COVERAGE_UNCOVERED)} 项 —— "
          "**本脚本不覆盖它们，不得读作已测。**")

    if bad:
        print(f"\ngate-selftest: FAIL ({bad} 项分类错误) —— 分类器不可信。",
              file=sys.stderr)
        return 1
    print("\ngate-selftest: 分类器用例全部通过"
          f"；但 **{len(COVERAGE_UNCOVERED)} 个门禁仍无负例测试**，覆盖不完整。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
