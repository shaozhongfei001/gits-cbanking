#!/usr/bin/env python3
"""GK-KE 全程序变异回归（proof that gate assertions are NOT noop）。

对每个 Loop 的关键门禁执行**变异测试**：故意破坏其判定逻辑，
要求门禁**必须转为失败**。若破坏后仍通过 → 该门禁断言空转（noop），视为失败。

这是本程序方法论的核心（见 evidence/L6/INDEPENDENT_QA_PACKAGE-L6.md §2）：
本程序共捕获 8 个空转/口径缺陷，全部由变异测试暴露。

用法：python3 scripts/gk_ke_mutation_regression.py
退出码：全部变异被正确捕获返回 0；任一变异未被捕获返回 1。
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# (名称, 门禁脚本, 变异 (old, new), 说明[, 被变异文件])
# 第 5 项省略时 = 变异门禁脚本自身；提供时 = 变异该文件（用于跨文件缺陷，
# 例如 GK13 的界面缺陷位于 index.html 而门禁在脚本中）。
MUTATIONS = [
    ("L1-1", "gk_ke_l1_1_semantics_tests.py",
     ('    if any(count > 1 for count in seen.values()):\n        violated.append("TYPEID_UNIQUE")',
      '    if False:\n        violated.append("TYPEID_UNIQUE")'),
     "disable homonym invariant"),
    ("L1-2", "gk_ke_l1_2_simulation_tests.py",
     ('    avg = (total / D(period_days)).quantize(D("0.01"), rounding=ROUND_HALF_UP)',
      '    avg = (total / D(len(by_date) * 2)).quantize(D("0.01"), rounding=ROUND_HALF_UP)'),
     "break C001 averaging formula"),
    ("L2-2", "gk_ke_l2_2_registry_tests.py",
     ('        stale = str(item["casExpectedVersion"]) != str(item["currentVersion"])',
      '        stale = False'),
     "disable stale-CAS detection"),
    ("L2-1", "gk_ke_l2_1_semantic_query_tests.py",
     ('        if field in request:\n            # 独立错误码',
      '        if False:\n            # 独立错误码'),
     "disable explicit forbidden-field guard"),
    ("L3-1", "gk_ke_l3_1_factory_tests.py",
     ('            if span.get("fragmentId") not in frag_by_id:\n                dangling_detected = True',
      '            if False:\n                dangling_detected = True'),
     "disable dangling evidence-span detection"),
    ("L3-2", "gk_ke_l3_2_release_tests.py",
     ('        if proj.get("published") is True and proj.get("ready") is not True:\n            found.add("HALF_PUBLISH")',
      '        if False:\n            found.add("HALF_PUBLISH")'),
     "disable half-publish detection"),
    ("L4-1", "gk_ke_l4_1_map_activation_tests.py",
     ('    if len(winners) > 1:', '    if False:'),
     "disable same-priority ambiguity detection"),
    ("L5-2", "gk_ke_l5_2_lightrag_tests.py",
     ('(report.get("accuracyC", 0.0) - report.get("accuracyB", 0.0)) >= MIN_IMPROVEMENT_PP',
      'True'),
     "defeat C05 improvement threshold (B vs C comparison)"),
    ("L4-2", "gk_ke_l4_2_closed_loop_tests.py",
     ('        if action_type in FORBIDDEN_ACTIONS:\n            found.add("FORBIDDEN_ACTION_REJECTED")',
      '        if False:\n            found.add("FORBIDDEN_ACTION_REJECTED")'),
     "disable forbidden-action (safety redline) detection"),
    ("GK13b", "gk_ke_oc04_map_breadth_tests.py",
     ('"maps": "KI-RULE-002"', '"maps": "KI-RULE-DISABLED"'),
     "drop the product-admission rule mapping (the customer admission condition the Owner named)",
     "specs/knowledge-architecture/activation/map_spec.json"),
    ("GK13c", "gk_ke_oc04_capability_tests.py",
     ('"kertSide": "DESIGN_ONLY"', '"kertSide": "IMPLEMENTED"'),
     "over-claim KERT readiness for a path-A capability",
     "specs/knowledge-architecture/capabilities/SIM-CAP-KYC-GAP.json"),
    ("GK13", "gk_ke_console_tests.py",
     ('  // 重新绑定结论表（工具区重绘后仍需保留已填答案）\n  renderConclusion();\n}',
      '}'),
     "drop renderConclusion() re-bind (form answers visually lost on re-render)",
     "tools/gk-ke-console/index.html"),
    ("L6", "gk_ke_l6_runtime_acceptance_tests.py",
     ('        if f.get("silentlyDegradedTo200Empty") is True:\n            found.add("SILENT_DEGRADE_REJECTED")',
      '        if False:\n            found.add("SILENT_DEGRADE_REJECTED")'),
     "disable silent-degradation detection"),
]


def run(script: Path) -> int:
    return subprocess.run([sys.executable, str(script)], cwd=ROOT,
                          capture_output=True).returncode


def main() -> int:
    results: list[tuple[str, str, str, int, int]] = []
    failures: list[str] = []

    for entry in MUTATIONS:
        name, script_name, (old, new), description = entry[0], entry[1], entry[2], entry[3]
        target_rel = entry[4] if len(entry) > 4 else f"scripts/{script_name}"
        script = ROOT / "scripts" / script_name
        target = ROOT / target_rel
        if not script.is_file():
            failures.append(f"{name}: gate script missing {script_name}")
            continue
        if not target.is_file():
            failures.append(f"{name}: mutation target missing {target_rel}")
            continue
        original = target.read_text(encoding="utf-8")
        if old not in original:
            failures.append(f"{name}: mutation anchor not found in {target_rel}")
            continue

        baseline = run(script)
        backup = Path(tempfile.mkstemp()[1])
        shutil.copyfile(target, backup)
        try:
            target.write_text(original.replace(old, new, 1), encoding="utf-8")
            mutated = run(script)
        finally:
            shutil.copyfile(backup, target)
            backup.unlink()

        restored = run(script)
        results.append((name, description, script_name, baseline, mutated))

        if baseline != 0:
            failures.append(f"{name}: baseline not passing (exit {baseline})")
        if mutated == 0:
            failures.append(f"{name}: MUTATION NOT CAUGHT -> assertion is noop ({description})")
        if restored != 0:
            failures.append(f"{name}: restore not passing (exit {restored})")

    print("=" * 78)
    print("GK-KE 全程序变异回归（断言非空转证明）")
    print("=" * 78)
    print(f"{'Loop':8s} {'baseline':>9s} {'mutated':>8s} {'restored':>9s}  变异")
    for name, description, _script, baseline, mutated in results:
        print(f"{name:8s} {baseline:9d} {mutated:8d} {'0':>9s}  {description}")

    if failures:
        print("\ngk-ke-mutation-regression: FAIL", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print(f"\ngk-ke-mutation-regression: PASS ({len(results)}/{len(MUTATIONS)} mutations caught)")
    print("  each mutation -> gate FAILS; each restore -> gate PASSES")
    print("  => no gate assertion is noop")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
