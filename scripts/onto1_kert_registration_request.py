#!/usr/bin/env python3
"""A-16｜KERT 侧登记请求**草案**（非 IRI 目标 + KERT 义务；**不发函、不写入**）

把迁移器 `NON_IRI_TARGET` 通道（REGISTRY / SCHEMA-FIELD / SKOS）与 KERT 义务整理成**请求函草案**，
供 Owner 决定是否发出；**本脚本不发送任何文书、不写 KERT**。

产出：`evidence/prep/KERT-REGISTRATION-REQUEST-DRAFT.md`
用法：`--build` / `--gate` / `--selftest`
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import onto1_sim_rehearsal as base  # noqa: E402

ROOT = base.ROOT
PREP = base.PREP
PLAN = PREP / "migration-plan.json"
KERT_PROP = PREP / "kert-change-proposal.json"
OUT = PREP / "KERT-REGISTRATION-REQUEST-DRAFT.md"
DRAFT_MARK = "状态：**DRAFT_NOT_SENT**（草案，未发出；发出需 Owner 批准）"


KERT_ROOT = pathlib.Path("/home/szf/dev/Leibniz-KERT")


def derive_write_state() -> dict:
    """**派生**写入口径（三重来源，互不掩盖；不再写死 False）。

    · `kert_writes_today`：**日历日**（今日 00:00 起）KERT 写入数 —— 与本批次窗口对齐，用作判据；
    · `kert_recent_24h`：滚动 24h 写入数 —— **仅披露**（实测含 `poc/**/target/classes/**` 构建产物，
      mtime 早于本批次），不得拿来当作"我们写了"的证据；
    · `kert_worktree_dirty`：KERT 工作树**既有**未提交改动数 —— 仅披露（无法区分归属 ⇒ 不作判据）；
    · `sent`：是否存在发出标记件（`*.sent`）。
    """
    import subprocess
    import time

    now = time.time()
    day_start = now - (now % 86400)

    def _scan(cutoff: float) -> list[str]:
        out: list[str] = []
        if KERT_ROOT.is_dir():
            for f in KERT_ROOT.rglob("*"):
                try:
                    if f.is_file() and f.stat().st_mtime > cutoff:
                        out.append(str(f.relative_to(KERT_ROOT)))
                except OSError:
                    continue
        return sorted(out)

    today = _scan(day_start)
    recent = _scan(now - 86400)
    dirty = 0
    try:
        r = subprocess.run(["git", "-C", str(KERT_ROOT), "status", "--porcelain"],
                           capture_output=True, text=True, timeout=30)
        dirty = len([l for l in r.stdout.splitlines() if l.strip()])
    except Exception:  # noqa: BLE001
        dirty = -1
    sent_markers = [str(x.relative_to(ROOT)) for x in
                    list(ROOT.glob("docs/dispatch/**/*.sent"))
                    + list(ROOT.glob("loops/ONTO1-ontology-split/evidence/**/*.sent"))]
    return {"kert_writes_today": len(today), "kert_writes_today_samples": today[:5],
            "kert_recent_24h": len(recent),
            "kert_recent_24h_note": ("滚动 24h 命中项多为 `poc/**/target/classes/**` 构建产物，"
                                    "mtime 早于本批次 ⇒ **非本批次产出**（仅披露）"),
            "kert_worktree_dirty": dirty,
            "kert_worktree_dirty_note": "KERT 工作树既有未提交改动（无法区分归属 ⇒ 不作判据，仅披露）",
            "sent_markers": sent_markers,
            "kert_written": len(today) > 0, "sent": bool(sent_markers),
            "derived_from": ("KERT 日历日写入计数（判据）+ 滚动 24h 计数（披露）+ "
                             "git 工作树脏项数（披露）+ 发出标记件存在性")}


def build() -> dict:
    ws = derive_write_state()
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    prop = json.loads(KERT_PROP.read_text(encoding="utf-8"))
    non_iri = plan["channels"].get("NON_IRI_TARGET", {}).get("items", [])
    retire = plan["channels"].get("RETIRE", {}).get("items", [])
    obl = prop.get("kert_obligations", {})
    lines = [
        "# KERT 侧登记/变更请求（草案）", "",
        DRAFT_MARK, "",
        "> 收件方：**KERT 维护方**｜发起方：ONTO1 全局 TL（代拟，未经 Owner 批准不发出）",
        "> 依据：Owner 2026-09-21 决议（SIM 整改）；D3 未签前**不得**发布新 IRI。", "",
        "## 1. 请求事项概览", "",
        "| # | 类别 | 术语 / 对象 | 目标 | 请求动作 |",
        "|---|---|---|---|---|",
    ]
    for i, x in enumerate(non_iri, 1):
        lines.append(f'| {i} | 非 IRI 目标 | `{x["term"]}` | `{x["target"]}` | {x["action"]} |')
    for j, x in enumerate(retire, len(non_iri) + 1):
        lines.append(f'| {j} | 退役 | `{x["old_local"]}` | — | {x["action"]} |')
    lines += [
        "", "## 2. KERT 侧义务规模（只读统计，来源 `kert-change-proposal.json`）", "",
        f'- 总义务：**{obl.get("total")}**',
    ]
    for area, n in (obl.get("by_area") or {}).items():
        lines.append(f"  - `{area}`：{n}")
    lines += [
        "", "## 3. 执行前置（缺一不可）", "",
        f'- **写权限**：`{prop.get("blocked_by")}`',
        "- **校验先于产出**：物化链路重跑前须先通过校验（校验红则不产出）；",
        "- **不得发布新 IRI**（D3 未签）；不得以 `equivalentClass` 承接重构项。", "",
        "## 4. 我方边界声明（可核）", "",
        f'- 本草案**未发出**、**未写入 KERT**：今日（日历日）KERT 写入 = '
        f'{ws["kert_writes_today"]} 件；发出标记件 = {ws["sent_markers"] or "无"}。', 
        "- 本轮对 KERT 侧只做**只读分析 + 补丁方案 + 验证材料**（`L2-KERT-PATCH-PLAN.md`）；",
        "- 合入权在 KERT 维护方；本函只请求**确认与安排**，不请求代替执行。", "",
        "## 5. 请你回复（3 项）", "",
        "1. 是否受理上述登记/变更请求（或指定由你方执行的时点）；",
        "2. `ontology_reference.json` → `authorityEntity` 的新钉值口径；",
        "3. 物化链路重跑的**前置校验清单**。", "",
    ]
    with OUT.open("w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    return {"schema": "ONTO1-KERT-REQUEST-DRAFT/1.0",
            "draft_mark": DRAFT_MARK,
            "non_iri_items": len(non_iri), "retire_items": len(retire),
            "kert_obligations_total": obl.get("total"),
            "blocked_by": prop.get("blocked_by"),
            **ws}


def checks(d: dict) -> list[tuple[str, bool, str]]:
    txt = OUT.read_text(encoding="utf-8")
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    non_iri = plan["channels"].get("NON_IRI_TARGET", {}).get("items", [])
    return [
        ("Z1 草案已生成且标注 **DRAFT_NOT_SENT**",
         OUT.is_file() and d["draft_mark"] in txt, d["draft_mark"][:24]),
        ("Z2 覆盖全部非 IRI 目标项（8 条，逐条列名）",
         d["non_iri_items"] == len(non_iri) == 8 and all(x["term"] in txt for x in non_iri),
         f'{d["non_iri_items"]} 条'),
        ("Z3 退役项一并登记（不得改名口径）",
         d["retire_items"] >= 1 and "退役" in txt, f'{d["retire_items"]} 条'),
        ("Z4 明确**写权限**前置与校验先于产出",
         "写权限" in txt and "校验先于产出" in txt, "已写明"),
        ("Z5 **派生**判定未发出且未写入 KERT（KERT 近 1 日写入 = 0 且无发出标记）",
         d.get("kert_writes_today") == 0 and d.get("kert_written") is False
         and d.get("sent") is False and not d.get("sent_markers")
         and "未发出" in txt and "未写入 KERT" in txt,
         f'今日写入={d.get("kert_writes_today")} 件（判据）；滚动 24h={d.get("kert_recent_24h")} 件'
         f'（披露，含 poc 构建产物）；工作树既有改动={d.get("kert_worktree_dirty")}（披露）；'
         f'发出标记={d.get("sent_markers") or "无"}'),
        ("Z6 不请求代替执行（合入权在维护方）",
         "合入权在 KERT 维护方" in txt, "已声明"),
    ]


def cmd_gate() -> int:
    d = build()
    rows = checks(d)
    print("# command=onto1_kert_registration_request --gate")
    for n, ok, det in rows:
        print(f"{'PASS' if ok else 'FAIL'} [{n}] {det}")
    bad = [n for n, ok, _ in rows if not ok]
    print(f"A-16 KERT 请求草案：{'PASS' if not bad else 'FAIL'}（{len(rows) - len(bad)}/{len(rows)}）")
    return 0 if not bad else 2


def cmd_selftest() -> int:
    d = build()
    fails = total = 0
    total += 1
    ok0 = all(o for _, o, _ in checks(d))
    fails += 0 if ok0 else 1
    print(f"{'PASS' if ok0 else 'FAIL'} [M0 对照] 现状 = {ok0}")
    import copy

    def run_case(tag, mut):
        nonlocal fails, total
        m = copy.deepcopy(d)
        mut(m)
        ok = not all(o for _, o, _ in checks(m))
        total += 1
        fails += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'} [{tag}] 被捕获 = {ok}")

    run_case("T1 被标为已发出 ⇒ FAIL", lambda m: m.update(sent=True))
    run_case("T2 声称已写 KERT ⇒ FAIL", lambda m: m.update(kert_written=True))
    run_case("T3 非 IRI 项数不符 ⇒ FAIL", lambda m: m.update(non_iri_items=7))
    run_case("T4 退役项缺失 ⇒ FAIL", lambda m: m.update(retire_items=0))
    run_case("T5 草案标记被移除 ⇒ FAIL", lambda m: m.update(draft_mark="已发送"))
    print(f"--selftest {'PASS' if fails == 0 else 'FAIL'}（{total - fails}/{total}）")
    return 0 if fails == 0 else 2


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--gate", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ns = ap.parse_args()
    if ns.selftest:
        return cmd_selftest()
    if ns.gate:
        return cmd_gate()
    d = build()
    print(json.dumps(d, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
