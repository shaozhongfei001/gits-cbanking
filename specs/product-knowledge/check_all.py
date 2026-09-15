#!/usr/bin/env python3
"""
产品解读专题统一门禁入口

Loop L03 W9 交付。把分散的子门禁编排为单一命令，任一失败则整体非零退出。

编排的子门禁：
  1. check_contracts.py          PI-0 基线合同（taxonomy / evidence-ref）
  2. check_l02_candidates.py     L02+L03 候选合同（7 份）
  3. check_invariants.py         不变式执行测试（42 条，正反例）
  4. check_pr_contracts.py       CTR-PR 增补向后兼容
  5. KERT: check_registry_consistency.py   源登记表一致性
  6. KERT: check_legacy_cards.py           legacy card 台账

KERT 侧门禁在跨仓路径可达时执行，不可达时标 SKIP 并说明（不静默通过）。

用法:
    python3 specs/product-knowledge/check_all.py
    python3 specs/product-knowledge/check_all.py --gits-only
"""

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
PK = REPO / "specs" / "product-knowledge"
KERT = Path("/home/szf/dev/Leibniz-KERT/examples/product-recommendation-assets")

GITS_GATES = [
    ("PI-0 基线合同", PK / "check_contracts.py"),
    ("L02/L03 候选合同", PK / "check_l02_candidates.py"),
    ("不变式执行测试", PK / "check_invariants.py"),
    ("CTR-PR 增补兼容", PK / "check_pr_contracts.py"),
    ("解读 API 契约测试", PK / "check_interpretation_api.py"),
]

KERT_GATES = [
    ("KERT 源登记一致性", KERT / "tools" / "check_registry_consistency.py"),
    ("KERT legacy card 台账", KERT / "tools" / "check_legacy_cards.py"),
    ("KERT L10 源版本/片段", KERT / "tools" / "check_l10_sources.py"),
    ("KERT L11 证据/断言", KERT / "tools" / "check_l11_spans.py"),
    ("KERT L12 冲突/体检/候选卡", KERT / "tools" / "check_l12_conflicts.py"),
    ("KERT L13 发布/投影", KERT / "tools" / "check_l13_release.py"),
]


def run(name, script, cwd):
    if not script.exists():
        print(f"SKIP | {name} | 脚本不存在: {script}")
        return "SKIP"
    r = subprocess.run([sys.executable, str(script)], cwd=str(cwd),
                       capture_output=True, text=True)
    tail = [l for l in r.stdout.strip().splitlines() if l.strip()]
    summary = tail[-1] if tail else "(no output)"
    if r.returncode == 0:
        print(f"PASS | {name} | {summary}")
        return "PASS"
    print(f"FAIL | {name} | exit={r.returncode}")
    for line in tail[-12:]:
        print(f"       {line}")
    return "FAIL"


def main():
    gits_only = "--gits-only" in sys.argv
    print("=" * 64)
    print("产品解读专题统一门禁 (L03 W9)")
    print("=" * 64)

    outcomes = []

    print("\n--- GITS 侧 ---")
    for name, s in GITS_GATES:
        outcomes.append((name, run(name, s, REPO)))

    print("\n--- KERT 侧 ---")
    if gits_only:
        for name, _ in KERT_GATES:
            print(f"SKIP | {name} | --gits-only")
            outcomes.append((name, "SKIP"))
    elif not KERT.exists():
        for name, _ in KERT_GATES:
            print(f"SKIP | {name} | KERT 仓库路径不可达: {KERT}")
            outcomes.append((name, "SKIP"))
    else:
        for name, s in KERT_GATES:
            outcomes.append((name, run(name, s, KERT)))

    n_pass = sum(1 for _, o in outcomes if o == "PASS")
    n_fail = sum(1 for _, o in outcomes if o == "FAIL")
    n_skip = sum(1 for _, o in outcomes if o == "SKIP")

    print("\n" + "=" * 64)
    print(f"统一门禁汇总：PASS {n_pass} · FAIL {n_fail} · SKIP {n_skip}")
    if n_fail:
        print("失败门禁：")
        for n, o in outcomes:
            if o == "FAIL":
                print(f"  - {n}")
    if n_skip:
        print("跳过门禁（非通过，需人工确认原因）：")
        for n, o in outcomes:
            if o == "SKIP":
                print(f"  - {n}")
    print("=" * 64)
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
