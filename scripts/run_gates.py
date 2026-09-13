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

import re
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
    # 门禁分类器自身的负例测试：**必须最先跑**——
    # 其余门禁的结论都要经过 classify()，分类器不可信则一切不可信。
    ("gate-selftest", [PY, "scripts/gate_selftest.py"], "integrity"),
    # 判据两项审计（此前只在 make verify，未纳入 GATES → 无法被注入测试覆盖）
    ("criteria-key-audit",   [PY, "scripts/gk_ke_criteria_key_audit.py"],   "integrity"),
    ("criteria-line-audit",  [PY, "scripts/gk_ke_criteria_line_audit.py"],  "integrity"),
    # 逐门禁注入真实缺陷，要求被检出
    ("gate-injection-tests", [PY, "scripts/gate_injection_tests.py"],       "integrity"),
    ("contract-check",          ["bash", "scripts/check-contracts.sh"], "integrity"),
    # **实例合规棘轮**（终结 T-06）：`loop-guard` 门禁原先只跑 `--template-check`，
    # **从不校验任何 loop 实例**（实测 58 个中 30 个不合规而门禁全绿）。
    # 本门禁拦截**新增**不合规实例；历史欠账冻结在 `loops/_instance_baseline.json`。
    ("loop-instances",          [PY, "scripts/loop_guard.py", "--instances-check"], "integrity"),
    ("loop-guard",              [PY, "scripts/loop_guard.py", "--template-check"], "integrity"),
    ("secret-scan",             [PY, "scripts/secret_scan.py", "--root", ".", "--quiet"], "security"),
    # **去掉 --quiet**（2026-09-13 反角色攻击命中）：
    # `--quiet` 下失败**完全无声**（exit=1 但 stdout/stderr 全空），
    # 门禁链里只看到一个 FAIL，**失败原因不可见** ——
    # 与 FAIL-22/36「静默跳过」同族：**失败必须可诊断**。
    # 实测非静默模式会打印 `V001__....sql: 非法受控枚举值 'D01_FAKE_X'`。
    ("enum-consistency",        [PY, "scripts/enum_consistency_check.py", "--root", "."], "integrity"),
    ("semantic-rule-gate",      [PY, "scripts/semantic_rule_gate.py"], "integrity"),
    ("contract-examples",       [PY, "scripts/gk_ke_contract_examples.py"], "integrity"),
    ("contract-coverage",       [PY, "scripts/gk_ke_contract_coverage.py"], "integrity"),
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


# 第四态：脚本以"无法判定"告终时的输出标记。
# 例：semantic-consumption 在无真实 LLM 时无法验证语义消费 ——
# 这**不是**通过，也**不是**失败，而是"当前环境不具备验证条件"。
# 若不单独建模，它会被 run_gates 按 exit=0 归为 [PASS]，
# 使**最核心的缺口在门禁层被静默显示为通过** ——
# 这与"门禁不得静默"直接矛盾（见 GK-KE-门禁语义与fail-closed边界）。
# **标记必须是机器 token，不能是散文词**（2026-09-13 实测教训）：
#   原实现把 "无法判定"/"未达成" 也当标记。接入 gate-selftest 后立刻出错 ——
#   selftest 输出的**用例标签**里含"未达成"三个字，
#   于是 classify() **把 selftest 自己的测试用例内容当成了门禁结论**，
#   判它 FAIL（而它实际 exit=0）。
# → 散文词会出现在**任何**提及它的输出里（说明文字、测试标签、文档片段），
#   作标记必然误命中。**机器标记应当是不可出现在散文中的英文 token。**
INCONCLUSIVE_MARKERS = ("INCONCLUSIVE",)
# 已确定未达成（强于无法判定）：如判据中出现 FAIL。
# 必须**先于** INCONCLUSIVE 判定 —— 否则"确定未达成"会被降级显示为"无法判定"，
# 弱化了结论（与"不得把未达成说成无法判定"的纪律一致）。
NOT_MET_MARKERS = ("NOT_MET",)   # 仅英文 token；中文散文词不得作标记（同上原因）

# **门禁结论的专用通道**：门禁若要表达"无法判定/未达成"，
# 必须在**独占一行**上前缀 `__GATE_VERDICT__=<PASS|INCONCLUSIVE|FAIL|BLOCKED>`。
#
# 为什么必须是专用通道（2026-09-13 两次实测教训）：
#   ① 用散文词（"未达成"/"无法判定"）→ gate-selftest 的**用例标签**含这些词，
#      导致 classify 把 selftest 的测试内容当成门禁结论；
#   ② 改用英文 token（"INCONCLUSIVE"）→ selftest 输出里**"期望 INCONCLUSIVE"** 又命中。
#   **只要标记是"输出里出现的某段文本"，任何提及它的输出都会误命中。**
#   故：标记必须是**不可能出现在散文中的专用行**。
VERDICT_RE = re.compile(r"^__GATE_VERDICT__=(PASS|INCONCLUSIVE|FAIL|BLOCKED)\s*$", re.M)

# 门禁**自身跑不起来**的证据（缺依赖 / 解释器不兼容 / 语法错误）。
# 动因（2026-09-13 实测）：3.12 venv 缺 jsonschema 时，`contract-examples` 以
# ImportError 退出 → 被本脚本归类为 **integrity FAIL** →
# 汇总行输出「INTEGRITY FAILURES … 不得声称制品完整」。
# **即：把"工具缺依赖"报成了"制品不完整"。** 二者处置完全不同：
#   · 制品不完整 → 必须修制品，且**不得声称完整**；
#   · 工具跑不起来 → 环境问题，**该门禁的结论未产生**（既非通过也非失败）。
# 混淆的后果是：真制品缺陷与工具故障不可区分，门禁的**可信度被自己摧毁**。
TOOLBROKEN_MARKERS = (
    "ModuleNotFoundError", "ImportError", "No module named",
    "SyntaxError", "IndentationError",
    "command not found", "No such file or directory: 'python",
)


def classify(rc: int, out: str) -> str:
    """四态分类：PASS / INCONCLUSIVE / BLOCKED / FAIL。

    判定顺序（不可调换）：
      1. 非零退出：
         a. 工具自身故障（缺依赖/导入错/语法错） → BLOCKED（**未产生结论**）
         b. 显式 BLOCKED 标记                     → BLOCKED
         c. 其余                                  → FAIL
      2. 含 NOT_MET 标记 → FAIL（**确定未达成强于无法判定**）
      3. 含 INCONCLUSIVE 标记 → INCONCLUSIVE
      4. 否则 → PASS

    **1.a 必须 先于 1.c**：否则"门禁没跑起来"会被当成"门禁判定失败"。
    """
    if rc != 0:
        if any(m in out for m in TOOLBROKEN_MARKERS):
            return "BLOCKED"
        m2 = VERDICT_RE.search(out)
        if m2:
            return m2.group(1)
        if "BLOCKED" in out:      # 显式门禁标记（刻意的，非散文）
            return "BLOCKED"
        return "FAIL"
    # 退出码 0：**只认专用 token 通道**，不再扫描散文词。
    m = VERDICT_RE.search(out)
    if m:
        return m.group(1)
    return "PASS"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--only", help="只跑名称匹配的门禁（子串匹配）")
    parser.add_argument("--kind", choices=["integrity", "readiness"],
                        help="只跑指定类别（用于 make integrity-check / readiness）")
    parser.add_argument("--strict", action="store_true",
                        help=("严格模式：就绪度未达成 / 无法判定时**非零退出**。"
                              "供发布前把关使用；常规 make check 不加此参数，"
                              "以免制造『为让门禁变绿而把未达成改写成通过』的诱因。"))
    args = parser.parse_args()

    gates = GATES
    if args.only:
        gates = [g for g in gates if args.only in g[0]]
    if args.kind:
        gates = [g for g in gates if g[2] == args.kind]
    if not gates:
        print("gk-ke-gates: FAIL — 无匹配门禁（--only/--kind 组合为空）",
              file=sys.stderr)
        return 1

    results = []
    t0 = time.time()
    for name, cmd, kind in gates:
        rc, out = run(cmd)
        lines = [l for l in out.splitlines() if l.strip()]
        summary = lines[0][:110] if lines else ""
        verdict = classify(rc, out)
        results.append({"name": name, "kind": kind, "exitCode": rc,
                        "verdict": verdict, "summary": summary, "output": out})
        mark = {"PASS": "PASS        ", "INCONCLUSIVE": "INCONCLUSIVE",
                "BLOCKED": "BLOCKED     ", "FAIL": "FAIL        "}[verdict]
        print(f"  [{mark}] {name:22s} exit={rc}")
        if verdict != "PASS" and summary:
            print(f"                {summary}")

    elapsed = time.time() - t0
    failed = [r for r in results if r["verdict"] in ("FAIL", "BLOCKED")]
    inconclusive = [r for r in results if r["verdict"] == "INCONCLUSIVE"]
    # **工具故障（BLOCKED）与制品失败（FAIL）必须分开。**
    # BLOCKED = 该门禁**未产生结论**（缺依赖/导入失败）；它既不是"通过"，
    # 也**不是"制品不完整"**。若混入 integrity_failed，汇总行会输出
    # 「不得声称制品完整」——那是**对制品的指控，而事实是工具没跑起来**。
    tools_blocked = [r for r in failed if r["verdict"] == "BLOCKED"]
    not_met = [r for r in failed if r["verdict"] == "FAIL"] + inconclusive
    readiness_not_met = [r for r in not_met if r["kind"] == "readiness"]
    integrity_failed = [r for r in failed
                        if r["kind"] != "readiness" and r["verdict"] == "FAIL"]

    print()
    print(f"gk-ke-gates: {len(results) - len(failed)}/{len(results)} 通过"
          f"（其中 {len(inconclusive)} 项**无法判定**，不计入通过）"
          f"，耗时 {elapsed:.1f}s")
    if tools_blocked:
        # **工具故障 ≠ 制品缺陷**。此栏若缺失，缺依赖会被读成"制品不完整"。
        print(f"  TOOLS NOT RUNNABLE (BLOCKED): {[r['name'] for r in tools_blocked]}")
        print("    这些门禁**未产生结论**（多为缺依赖/导入失败），既非通过也非失败。")
        print("    它们**不构成对制品的指控**；但**其覆盖范围内的事项处于未验证状态**。")
        print("    修复示例: .venv/bin/python -m pip install -r requirements-tooling.txt jsonschema")
    if integrity_failed:
        print(f"  INTEGRITY FAILURES: {[r['name'] for r in integrity_failed]}")
    if readiness_not_met:
        # 就绪度未达成（含 INCONCLUSIVE）**必须被打印**，但**不计入门禁失败**。
        # 理由见 docs/architecture/GK-KE-门禁语义与fail-closed边界-V1.0.md §1.2：
        # 若把未达成计入门禁失败，会制造"为让门禁变绿而把未达成改写成通过"的诱因。
        print(f"  READINESS NOT MET:  {[r['name'] for r in readiness_not_met]}")
        if inconclusive:
            print(f"    其中**无法判定（INCONCLUSIVE）**："
                  f"{[r['name'] for r in inconclusive]}")
            print("    INCONCLUSIVE ≠ 通过；它表示当前环境不具备验证条件。")
        print("  NOTE: 就绪度未达成**不计入本门禁失败**，但**必须**被如实声明。")
        print("        结论由收口文档明确写出，门禁只负责暴露事实。")
        print("        单独自查请运行: make readiness")

    if inconclusive:
        print()
        print("  ⚠️  有下列检查**无法判定**，不得在汇报中计为通过：")
        for r in inconclusive:
            print(f"      - {r['name']}")

    if integrity_failed:
        print()
        print(f"gk-ke-gates: FAIL ({len(integrity_failed)} 项完整性失败) — "
              "见上表；不得声称制品完整。", file=sys.stderr)
        rc = 1
    elif args.strict and readiness_not_met:
        # 严格模式：发布前把关，就绪度未达成即非零退出。
        print()
        print(f"gk-ke-gates: READINESS NOT MET (--strict) "
              f"({len(readiness_not_met)} 项) — "
              f"{[r['name'] for r in readiness_not_met]}", file=sys.stderr)
        print("  严格模式用于发布前把关；常规 make check 不加 --strict，"
              "以免制造『为让门禁变绿而把未达成改写成通过』的诱因。",
              file=sys.stderr)
        rc = 1
    else:
        rc = 0

    if args.json:
        print(json.dumps(
            {"total": len(results),
             "passed": [r["name"] for r in results if r["verdict"] == "PASS"],
             "failed": [r["name"] for r in failed],
             "inconclusive": [r["name"] for r in inconclusive],
             "integrityFailed": [r["name"] for r in integrity_failed],
             "readinessNotMet": [r["name"] for r in readiness_not_met],
             "strictMode": bool(args.strict),
             "gateExitCode": rc,
             "semantics": ("四态：PASS / INCONCLUSIVE（无法判定，非通过）/ "
                           "BLOCKED / FAIL。常规模式退出码只反映完整性；"
                           "就绪度未达成与无法判定仅报告不计入。"
                           "--strict 模式下就绪度未达成亦非零退出。"
                           "make check 通过不等于一切就绪。"),
             "results": [{k: v for k, v in r.items() if k != "output"}
                         for r in results]},
            ensure_ascii=False, indent=2))

    return rc


if __name__ == "__main__":
    raise SystemExit(main())
