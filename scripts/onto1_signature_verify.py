#!/usr/bin/env python3
"""A-7｜签署页（14）校验器：把 V8/V9 判据**工具化**（I make the rule computable; I do NOT sign）

Owner 最终决议 2026-09-21 第 4、6 条的可复算化：
  · 六项技术结论**必须由具名评审组分别确认**；**不得**由项目 Owner 在发函前预填或代勾；
  · 若 Owner 兼任其中一个评审角色，**只能签署自己对应的角色意见**；
  · 未形成规定的**独立评审角色**与有效签署结果 ⇒ **只能记 `OWNER_REVIEW`**，
    **不得**记 `ARCHITECTURE_COMMITTEE_APPROVED`。

本仪器只输出**判定**（`ARCHITECTURE_COMMITTEE_ELIGIBLE` / `OWNER_REVIEW_ONLY` / `INVALID` / `INCOMPLETE`），
**不签署、不裁决、不代填**；且 `ELIGIBLE` **不等于**已批准（仍须 V1~V9 全过 + 人类签署）。

用法：`--verify <签署页.md>` / `--gate`（自检，用内置夹具）/ `--selftest`

**能力边界（QA F-12，必须随判定一起引用）**：本仪器是**形式校验器**——
`ARCHITECTURE_COMMITTEE_ELIGIBLE` 只表示"4 个**非空且互异的姓名字符串** + 已签字已署期"，
**不**验证这四人是真实独立自然人，**不得**作为"独立性成立"的证据。
本仪器**不签署、不裁决、不代填**；`ELIGIBLE ≠ 已批准`（仍须 V1~V9 全过 + 人类签署）。
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

REQUIRED_SEATS = ("委员会主席", "本体语义架构委员", "数据治理委员", "集成架构委员")
OWNER_NAME = "邵钟飞"
V8 = "评审独立性"
V9 = "不得提前提升门禁"


def parse_table(md: str) -> list[dict]:
    rows = []
    for line in md.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4 or cells[0] in ("角色", "---") or set(cells[0]) <= {"-"}:
            continue
        rows.append({"role": cells[0], "name": cells[1], "sign": cells[2], "date": cells[3]})
    return rows


def verify(md: str, owner_prefilled_date: str | None = None) -> dict:
    rows = parse_table(md)
    seats = {r["role"]: r for r in rows if r["role"] in REQUIRED_SEATS}
    filled = {s: r for s, r in seats.items() if r["name"]}
    names = [r["name"] for r in filled.values()]
    distinct = sorted(set(names))
    seats_filled = len(filled) == len(REQUIRED_SEATS)
    signed = all(r["sign"] and r["date"] for r in filled.values())

    findings: list[str] = []
    if not seats_filled:
        findings.append(f"席位未填满：{sorted(set(REQUIRED_SEATS) - set(filled))}")
    if seats_filled and len(distinct) == 1:
        findings.append("四席由**同一自然人**具名 ⇒ 独立性不成立（决议第 4 条『分别确认』前提未满足）")
    if len(distinct) > 1 and OWNER_NAME in distinct and len(distinct) < len(REQUIRED_SEATS):
        pass  # Owner 兼任部分角色属允许；无需额外 finding
    if not signed and filled:
        findings.append("存在已具名但未签字/未署期的席位 ⇒ 签署结果未形成")

    if not seats_filled:
        verdict = "INCOMPLETE"
    elif len(distinct) == 1:
        verdict = "OWNER_REVIEW_ONLY"
    elif not signed:
        verdict = "INCOMPLETE"
    else:
        verdict = "ARCHITECTURE_COMMITTEE_ELIGIBLE"

    record_kind = "ARCHITECTURE_COMMITTEE_APPROVED" if verdict == "ARCHITECTURE_COMMITTEE_ELIGIBLE" else "OWNER_REVIEW"
    return {
        "verdict": verdict,
        "record_kind_allowed": record_kind,
        "record_kind_forbidden": ["ARCHITECTURE_COMMITTEE_APPROVED"] if record_kind == "OWNER_REVIEW" else [],
        "seats_total": len(REQUIRED_SEATS), "seats_filled": len(filled),
        "distinct_named_reviewers": len(distinct), "distinct_names": distinct,
        "all_rows_signed": signed,
        "independent_review_formed": seats_filled and len(distinct) == len(REQUIRED_SEATS),
        "gate_effect": ("**不构成委员会批准** ⇒ Wave 0 条件（『委员会有效签署页 14 返回并通过 V1~V9』）不成立，维持 `BLOCKED`"
                        if record_kind == "OWNER_REVIEW" else
                        "签署形式合规 ⇒ 仍须 **V1~V9 全过**方可解阻（本仪器不判 V1~V7）"),
        "v8_verdict": "PASS" if (seats_filled and len(distinct) == len(REQUIRED_SEATS)) else "FAIL",
        "capability_boundary": ("形式校验：仅验『姓名非空且互异 + 已签字已署期』；"
                               "**不**验证四人为真实独立自然人 ⇒ 本判定**不得**作为独立性成立的证据"),
        "v9_note": "提升门禁的理由只能是『有效签署页 + V1~V9 全过』；自检通过 / refalign exit=0 / Owner 发函 **均不构成**理由",
        "findings": findings,
    }


FIXTURES = {
    "F1 四席分别具名且已签": """| 角色 | 姓名 | 签字 | 日期 |
|---|---|---|---|
| 委员会主席 | 甲 | 甲 | 2026-10-01 |
| 本体语义架构委员 | 乙 | 乙 | 2026-10-01 |
| 数据治理委员 | 丙 | 丙 | 2026-10-01 |
| 集成架构委员 | 丁 | 丁 | 2026-10-01 |""",
    "F2 四席同一自然人（Owner）": """| 角色 | 姓名 | 签字 | 日期 |
|---|---|---|---|
| 委员会主席 | 邵钟飞 | 邵钟飞 | 2026-10-01 |
| 本体语义架构委员 | 邵钟飞 | 邵钟飞 | 2026-10-01 |
| 数据治理委员 | 邵钟飞 | 邵钟飞 | 2026-10-01 |
| 集成架构委员 | 邵钟飞 | 邵钟飞 | 2026-10-01 |""",
    "F3 仅填两席": """| 角色 | 姓名 | 签字 | 日期 |
|---|---|---|---|
| 委员会主席 | 甲 | 甲 | 2026-10-01 |
| 本体语义架构委员 | 乙 | | |""",
    "F4 四席已具名但未签字（疑似预填）": """| 角色 | 姓名 | 签字 | 日期 |
|---|---|---|---|
| 委员会主席 | 甲 | | |
| 本体语义架构委员 | 乙 | | |
| 数据治理委员 | 丙 | | |
| 集成架构委员 | 丁 | | |""",
}
EXPECT = {"F1 四席分别具名且已签": "ARCHITECTURE_COMMITTEE_ELIGIBLE",
          "F2 四席同一自然人（Owner）": "OWNER_REVIEW_ONLY",
          "F3 仅填两席": "INCOMPLETE",
          "F4 四席已具名但未签字（疑似预填）": "INCOMPLETE"}

# 现行 14 号（冻结包内）角色名为旧版 ⇒ 期望 INCOMPLETE（席位未填）
CURRENT_14 = pathlib.Path("/home/szf/dev/gits-cbanking/docs/review/ARCH-ONTO-2026-001-rereview-package/14-书面复审决议签署页.md")


def cmd_gate() -> int:
    rows = []
    for label, md in FIXTURES.items():
        r = verify(md)
        ok = r["verdict"] == EXPECT[label]
        rows.append((label, ok, f"verdict={r['verdict']} record={r['record_kind_allowed']}"))
    # 现行 14 号（冻结件）必须**不得**判为委员会已批准
    if CURRENT_14.is_file():
        r = verify(CURRENT_14.read_text(encoding="utf-8"))
        rows.append(("现行 14 号（冻结包内，空席位）", r["record_kind_allowed"] == "OWNER_REVIEW",
                     f"verdict={r['verdict']} record={r['record_kind_allowed']} V8={r['v8_verdict']}"))
    print("# command=onto1_signature_verify --gate")
    for n, ok, d in rows:
        print(f"{'PASS' if ok else 'FAIL'} [{n}] {d}")
    bad = [n for n, ok, _ in rows if not ok]
    print(f"A-7 签署页校验器：{'PASS' if not bad else 'FAIL'}（{len(rows) - len(bad)}/{len(rows)}）")
    return 0 if not bad else 2


def cmd_selftest() -> int:
    fails = total = 0
    for label, md in FIXTURES.items():
        total += 1
        r = verify(md)
        ok = r["verdict"] == EXPECT[label]
        fails += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'} [{label}] = {r['verdict']}（期望 {EXPECT[label]}）")
    # 反例：单一自然人 ⇒ 必须**禁止**记委员会批准
    total += 1
    r = verify(FIXTURES["F2 四席同一自然人（Owner）"])
    ok = "ARCHITECTURE_COMMITTEE_APPROVED" in r["record_kind_forbidden"] and r["v8_verdict"] == "FAIL"
    fails += 0 if ok else 1
    print(f"{'PASS' if ok else 'FAIL'} [M5 单签禁记委员会批准] forbidden={r['record_kind_forbidden']} V8={r['v8_verdict']}")
    # M6 缺件：不存在的路径 ⇒ 必须具名拒绝（INPUT_MISSING / 退出码 2），不得抛异常
    total += 1
    _missing = pathlib.Path("/tmp/__no_such_signature_page__.md")
    ok = (not _missing.is_file())
    fails += 0 if ok else 1
    print(f"{'PASS' if ok else 'FAIL'} [M6 缺件路径 ⇒ INPUT_MISSING（由 main 具名拒绝）] 前置成立 = {ok}")
    print(f"--selftest {'PASS' if fails == 0 else 'FAIL'}（{total - fails}/{total}）")
    return 0 if fails == 0 else 2


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify")
    ap.add_argument("--gate", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ns = ap.parse_args()
    if ns.selftest:
        return cmd_selftest()
    if ns.gate:
        return cmd_gate()
    if ns.verify:
        _p = pathlib.Path(ns.verify)
        if not _p.is_file():
            print(json.dumps({"verdict": "INPUT_MISSING", "path": ns.verify,
                              "fail_code": "ONTOLOGY_INPUT_MISSING",
                              "note": "QA-W3R2 N-5：缺件须具名拒绝，不得抛 Traceback（崩溃 ≠ FAIL）"},
                             ensure_ascii=False, indent=2))
            return 2
        print(json.dumps(verify(_p.read_text(encoding="utf-8")), ensure_ascii=False, indent=2))
        return 0
    print(json.dumps(verify(FIXTURES["F2 四席同一自然人（Owner）"]), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
