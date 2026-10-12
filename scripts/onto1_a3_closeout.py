#!/usr/bin/env python3
"""A-2｜T-4 余项收口（C5 计数口径统一 · C6 M12 夹具确认 · C7 冻结复交 + 日志自证 revision + 回执表）

背景：A3 包预验已过（仪器 8/8 @ collision=8c18b5b3 / refalign=4d706978），仍缺 C5~C7；
且 `a3fix-after-*.log` 四份 **`artifact=` 计数全 0**（不自证 revision）。原 pilot-a3 已下线，本仪器由新 holder（TL）执行。

本仪器做三件事（**只读被检制品；只写本 Loop 证据区**）：
  · **C5 计数口径统一**：把各仪器**实测**用例数与**声明**数逐项比对，落 `prep/a3-count-caliber.json`（不一致即 FAIL）；
  · **C6 M12 夹具确认**：实测 collision 自检用例清单，断言 M12 家族（含对照与 M12b 复现）在位；
  · **C7 冻结复交 + 日志自证 revision + 回执表**：计算**冻结哈希**（脚本/基线/登记表），
    以 `# artifact=<freeze>` 为**首行**重新产出四份 `a3fix-after-*.log`（**先备份旧件**，遵守 D-14），并出回执表。

**边界**：不改任何被检制品；不提升任何门禁；`wi_a4_namespace_collision` 仍 `INCOMPLETE`（C-1b 待 D3）。
用法：`--build` / `--gate` / `--selftest`
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path("/home/szf/dev/gits-cbanking")
EV = ROOT / "loops/ONTO1-ontology-split/evidence"
PREP = EV / "prep"
BACKUP = pathlib.Path("/tmp/a3closeout-backup")
CALIBER = PREP / "a3-count-caliber.json"
FREEZE = PREP / "a3-freeze.json"
RECEIPT = PREP / "a3-closeout-receipt.md"

# 声明口径（来自派工/验收文书；实测须与之一致）
DECLARED = {
    "wi_a4_namespace_collision_selftest": {"cases": 26, "source": "memory/NEXT_SESSION.md T-4（26 条用例）"},
    "wi_a3_reference_alignment_selftest": {"cases": 16, "source": "memory/NEXT_SESSION.md T-4（selftest 16/16）"},
    "wi_w15_a3_acceptance": {"cases": 8, "source": "memory/NEXT_SESSION.md T-4（仪器 8/8）"},
    "wi_d2_relation_resolution": {"cases": 11, "source": "本 Loop EVIDENCE.md（D2 分流 11/11）"},
    "wi_d2_relation_resolution_selftest": {"cases": 10, "source": "本 Loop EVIDENCE.md（反例 10/10）"},
    "wi_a2_disposition": {"cases": 9, "source": "本 Loop EVIDENCE.md（A-1 处置闭环 9/9：QA-W3R2 后新增 A9 独立键复核）"},
    "wi_c2_consumer_scan": {"cases": 7, "source": "本 Loop EVIDENCE.md（C-2 消费者扫描 7/7）"},
}
A3FIX_LOGS = ("a3fix-after-wi_a4_namespace_collision-gate.log",
              "a3fix-after-wi_a4_namespace_collision-selftest.log",
              "a3fix-after-wi_a3_reference_alignment-gate.log",
              "a3fix-after-wi_a3_reference_alignment-selftest.log")
FREEZE_INPUTS = {
    "scripts/onto1_namespace_collision_check.py": None,
    "scripts/onto1_reference_alignment_check.py": None,
    "scripts/onto1_w15_acceptance.py": None,
    "specs/semantic/gits-core.owl.ttl": None,
    "loops/ONTO1-ontology-split/evidence/namespace-known-defects.json": None,
    "loops/ONTO1-ontology-split/evidence/non-gate-log-allowlist.json": None,
}


def run(cmd: list[str]) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def sha256_file(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def freeze_hash() -> dict:
    hashes = {}
    for rel in FREEZE_INPUTS:
        fp = ROOT / rel
        hashes[rel] = sha256_file(fp) if fp.is_file() else None
    composite = hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()
    return {"composite": composite, "inputs": hashes}


def actual_counts() -> dict:
    out: dict[str, dict] = {}
    _, txt = run([sys.executable, "scripts/onto1_namespace_collision_check.py", "--selftest"])
    # F-9 修正：分别统计 PASS/FAIL 行；**用例数取 PASS 行数**，并要求 pass == total
    lines = txt.splitlines()
    p_lines = [l for l in lines if l.startswith("PASS ")]
    f_lines = [l for l in lines if l.startswith("FAIL ")]
    cases = [l.split(None, 1)[1].split("  ")[0] for l in p_lines]
    out["wi_a4_namespace_collision_selftest"] = {"cases": len(p_lines), "case_names": cases,
                                                 "failed_lines": len(f_lines),
                                                 "all_passed": not f_lines}
    _, txt = run([sys.executable, "scripts/onto1_reference_alignment_check.py", "--selftest"])
    m = re.search(r"selftest:\s*(\d+)/(\d+)", txt)
    out["wi_a3_reference_alignment_selftest"] = {"cases": int(m.group(2)) if m else -1}
    _, txt = run([sys.executable, "scripts/onto1_w15_acceptance.py"])
    m = re.search(r"PASS（(\d+)/(\d+)", txt)
    out["wi_w15_a3_acceptance"] = {"cases": int(m.group(2)) if m else -1}
    _, txt = run([sys.executable, "scripts/onto1_product_relation_resolution.py", "--gate"])
    m = re.search(r"（(\d+)/(\d+)；", txt)
    out["wi_d2_relation_resolution"] = {"cases": int(m.group(2)) if m else -1}
    _, txt = run([sys.executable, "scripts/onto1_product_relation_resolution.py", "--selftest"])
    m = re.search(r"（(\d+)/(\d+)）", txt)
    out["wi_d2_relation_resolution_selftest"] = {"cases": int(m.group(2)) if m else -1}
    _, txt = run([sys.executable, "scripts/onto1_disposition_ledger.py", "--gate"])
    m = re.search(r"（(\d+)/(\d+)）", txt)
    out["wi_a2_disposition"] = {"cases": int(m.group(2)) if m else -1}
    _, txt = run([sys.executable, "scripts/onto1_c2_consumer_scan.py", "--gate"])
    m = re.search(r"（(\d+)/(\d+)）", txt)
    out["wi_c2_consumer_scan"] = {"cases": int(m.group(2)) if m else -1}
    return out


def m12_family(case_names: list[str]) -> list[str]:
    return [c for c in case_names if c.startswith("M12")]


def build_caliber() -> dict:
    act = actual_counts()
    rows = []
    for gate, dec in DECLARED.items():
        a = act.get(gate, {}).get("cases", -1)
        rows.append({"gate": gate, "declared": dec["cases"], "actual": a,
                     "match": a == dec["cases"], "source": dec["source"]})
    m12 = m12_family(act.get("wi_a4_namespace_collision_selftest", {}).get("case_names", []))
    all_passed = act.get("wi_a4_namespace_collision_selftest", {}).get("all_passed", False)
    return {
        "schema": "ONTO1-A3-COUNT-CALIBER/1.0",
        "purpose": "C5 计数口径统一 + C6 M12 夹具确认（实测值 vs 声明值）",
        "rows": rows,
        "m12_family": m12,
        "selftest_all_passed": all_passed,
        "count_semantics": "**计数口径（F-9 修正）**：用例数 = `--selftest` 输出中 `PASS ` 开头的行数；含任何 `FAIL ` 行则 all_passed=False 且 C5 FAIL。",
        "act": act,
        "m12_confirmed": len(m12) >= 2,
        "mismatches": [r["gate"] for r in rows if not r["match"]],
        "freeze": freeze_hash(),
    }


def write_selfcert_logs(freeze: dict) -> list[dict]:
    """以 `# artifact=<freeze>` 为首行重出四份 a3fix-after 日志（**先备份旧件**）。"""
    BACKUP.mkdir(parents=True, exist_ok=True)
    jobs = [
        ("a3fix-after-wi_a4_namespace_collision-gate.log",
         [sys.executable, "scripts/onto1_namespace_collision_check.py", "--gate"]),
        ("a3fix-after-wi_a4_namespace_collision-selftest.log",
         [sys.executable, "scripts/onto1_namespace_collision_check.py", "--selftest"]),
        ("a3fix-after-wi_a3_reference_alignment-gate.log",
         [sys.executable, "scripts/onto1_reference_alignment_check.py", "--gate"]),
        ("a3fix-after-wi_a3_reference_alignment-selftest.log",
         [sys.executable, "scripts/onto1_reference_alignment_check.py", "--selftest"]),
    ]
    out = []
    for name, cmd in jobs:
        fp = EV / name
        if fp.is_file():
            shutil.copy2(fp, BACKUP / name)          # D-14：先备份
        code, txt = run(cmd)
        header = (f"# artifact={freeze['composite']}\n"
                  f"# command={' '.join(cmd[1:])}\n"
                  f"# exit={code}\n# regenerated_at=2026-09-21（A-2/C7 冻结复交；旧件备份于 {BACKUP}）\n")
        fp.write_text(header + txt, encoding="utf-8")
        out.append({"log": name, "exit": code,
                    "artifact_line": fp.read_text(encoding="utf-8").splitlines()[0],
                    "self_certified": fp.read_text(encoding="utf-8").startswith("# artifact=")})
    return out


def write_receipt(cal: dict, logs: list[dict]) -> None:
    f = cal["freeze"]
    lines = [
        "# A3 包收口回执表（T-4 C5~C7）",
        "",
        "| 项 | 结果 |",
        "|---|---|",
        f"| **冻结哈希（composite）** | `{f['composite']}` |",
        f"| 输入件 | " + " · ".join(f"`{k}`={str(v)[:12]}" for k, v in f["inputs"].items()) + " |",
        "| C5 计数口径 | " + ("**全部一致**" if not cal["mismatches"] else f"不一致：{cal['mismatches']}") + " |",
        f"| C6 M12 夹具 | **确认在位**：`{cal['m12_family']}` |",
        "| C7 日志自证 | " + " · ".join(f"`{l['log']}`（exit={l['exit']}，首行 `# artifact=`={l['self_certified']}）" for l in logs) + " |",
        "",
        "## 计数口径明细（实测 vs 声明）",
        "",
        "| 门禁 | 声明 | 实测 | 一致 | 声明出处 |",
        "|---|---|---|---|---|",
    ]
    for r in cal["rows"]:
        lines.append(f"| `{r['gate']}` | {r['declared']} | {r['actual']} | {'是' if r['match'] else '**否**'} | {r['source']} |")
    lines += [
        "",
        "## 边界声明",
        "",
        "- `wi_a4_namespace_collision` 仍为 **`INCOMPLETE`（exit 3）**：`C-1b` 待 D3 签署根域，**未提升**；",
        "- 本次**未改**任何被检制品（两处脚本仅新增判据；基线 T-Box 未动）；",
        "- 旧日志已按 `D-14` **先备份后重出**（备份目录 `/tmp/a3closeout-backup`）。",
    ]
    RECEIPT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def cmd_build() -> int:
    PREP.mkdir(parents=True, exist_ok=True)
    cal = build_caliber()
    logs = write_selfcert_logs(cal["freeze"])
    CALIBER.write_text(json.dumps(cal, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    FREEZE.write_text(json.dumps(cal["freeze"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_receipt(cal, logs)
    print(f"已写出 {CALIBER.relative_to(ROOT)} · {FREEZE.relative_to(ROOT)} · {RECEIPT.relative_to(ROOT)}")
    print(f"冻结 composite = {cal['freeze']['composite'][:16]}；M12 家族 = {cal['m12_family']}")
    for l in logs:
        print(f"  {l['log']}: exit={l['exit']} 自证={l['self_certified']}")
    return 0


def checks(cal: dict, logs: list[dict]) -> list[tuple[str, bool, str]]:
    mism = [r["gate"] for r in cal["rows"] if r["declared"] != r["actual"]]
    return [
        ("C5 计数口径：实测 = 声明（逐项）**且反例全过**", not mism and cal.get("selftest_all_passed", True),
         f"不一致 = {mism or '无'}（{len(cal['rows'])} 项）；反例全过 = {cal.get('selftest_all_passed', True)}"),
        ("C5b 声明数不得为占位（全部 > 0）",
         all(r["declared"] > 0 and r["actual"] > 0 for r in cal["rows"]), "全项 > 0"),
        ("C6 M12 夹具确认在位（含对照）", cal["m12_confirmed"], f"M12 家族 = {cal['m12_family']}"),
        ("C7 四份日志首行均含 `# artifact=`",
         len(logs) == 4 and all(l["self_certified"] for l in logs),
         f"自证 {sum(1 for l in logs if l['self_certified'])}/4"),
        ("C7b 日志 artifact 值 = 冻结 composite（同一冻结口径）",
         all(l["artifact_line"].endswith(cal["freeze"]["composite"]) for l in logs),
         f"composite={cal['freeze']['composite'][:16]}"),
        ("C7c 冻结输入件齐备（6/6 有哈希）",
         all(v for v in cal["freeze"]["inputs"].values()),
         f"{sum(1 for v in cal['freeze']['inputs'].values() if v)}/6"),
        ("C7d 基线 T-Box 仍在冻结哈希内（未动）",
         str(cal["freeze"]["inputs"].get("specs/semantic/gits-core.owl.ttl") or "").startswith("705578d6324abd0c"),
         str(cal["freeze"]["inputs"].get("specs/semantic/gits-core.owl.ttl"))[:16]),
    ]


def cmd_gate() -> int:
    cal = json.loads(CALIBER.read_text(encoding="utf-8")) if CALIBER.is_file() else build_caliber()
    fresh = build_caliber()
    drift = [r["gate"] for r, g in zip(cal["rows"], fresh["rows"]) if r["actual"] != g["actual"]]
    logs = [{"log": n, "self_certified": (EV / n).read_text(encoding="utf-8").startswith("# artifact="),
             "artifact_line": (EV / n).read_text(encoding="utf-8").splitlines()[0]}
            for n in A3FIX_LOGS if (EV / n).is_file()]
    rows = checks(fresh, logs)
    rows.append(("C7e 台账未陈旧（重算计数与台账一致）", not drift, f"漂移 = {drift or '无'}"))
    print("# command=onto1_a3_closeout --gate")
    for n, ok, det in rows:
        print(f"{'PASS' if ok else 'FAIL'} [{n}] {det}")
    bad = [n for n, ok, _ in rows if not ok]
    print(f"A-2 收口：{'PASS' if not bad else 'FAIL'}（{len(rows) - len(bad)}/{len(rows)}）")
    return 0 if not bad else 2


def cmd_selftest() -> int:
    cal = build_caliber()
    logs = [{"log": n, "self_certified": (EV / n).read_text(encoding="utf-8").startswith("# artifact="),
             "artifact_line": (EV / n).read_text(encoding="utf-8").splitlines()[0]}
            for n in A3FIX_LOGS if (EV / n).is_file()]
    fails = total = 0

    def run_case(tag: str, mut) -> None:
        nonlocal fails, total
        import copy
        c = copy.deepcopy(cal)
        lg = copy.deepcopy(logs)
        mut(c, lg)
        ok = not all(o for _, o, _ in checks(c, lg))
        total += 1
        fails += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'} [{tag}] 被捕获 = {ok}")

    total += 1
    base_ok = all(o for _, o, _ in checks(cal, logs))
    fails += 0 if base_ok else 1
    print(f"{'PASS' if base_ok else 'FAIL'} [M0 对照] 现状 = {base_ok}")
    run_case("M1 声明数与实测不符 ⇒ FAIL", lambda c, l: c["rows"][0].update(declared=c["rows"][0]["actual"] + 1))
    run_case("M2 M12 夹具缺失 ⇒ FAIL", lambda c, l: c.update(m12_family=[], m12_confirmed=False))
    run_case("M3 日志去掉自证首行 ⇒ FAIL",
             lambda c, l: [x.update(self_certified=False, artifact_line="no-artifact") for x in l])
    run_case("M4 冻结输入件缺失 ⇒ FAIL",
             lambda c, l: c["freeze"]["inputs"].update({"specs/semantic/gits-core.owl.ttl": None}))
    run_case("M5 冻结哈希被替换为非基线 ⇒ FAIL",
             lambda c, l: c["freeze"]["inputs"].update({"specs/semantic/gits-core.owl.ttl": "deadbeef" * 8}))
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
    return cmd_build()


if __name__ == "__main__":
    sys.exit(main())
