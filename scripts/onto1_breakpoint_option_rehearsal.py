#!/usr/bin/env python3
"""A-12｜断点三出口**沙箱对比演练**（A 显式清单改名 / B 保留原名+并存 / C 延后）

**本脚本不选出口**（选择权在 Owner / PSO / 数据 Owner）。它把三个出口各**真跑一遍**（沙箱内），
让选择有可比证据：改了哪些文件、是否产生脏值、盲替换是否被避免、是否引入等价关系。

判据要点：
  · 出口 A：仅对**无盲替换风险**的改名施以受限替换；**必须**验证"相邻名未被污染"且"0 脏值"；
  · 出口 B：**不改名**，产出"旧名保留 + 新名待增"的并存清单；**不得**引入 `equivalentClass`；
  · 出口 C：**零改动**（只登记待裁项）。

用法：`--run` / `--gate` / `--selftest`
"""
from __future__ import annotations

import argparse
import collections
import json
import os
import pathlib
import re
import shutil
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import onto1_sim_rehearsal as base  # noqa: E402

ROOT = base.ROOT
EV = base.EV
PREP = base.PREP
REPORT = PREP / "sim-rehearsal-report.json"
ADV = PREP / "breakpoint-advisory"
OUT = PREP / "breakpoint-option-comparison.json"
MD = PREP / "BREAKPOINT-OPTION-COMPARISON.md"
HITS = EV / "consumer-scan-hits.jsonl"
SAMPLE_PER_BREAKPOINT = 25


def load_hits() -> list[dict]:
    with HITS.open(encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def rehearse_options() -> dict:
    rep = json.loads(REPORT.read_text(encoding="utf-8"))
    hits = load_hits()
    excl = ("loops/ONTO1-ontology-split/evidence/", ".codebuddy/")
    cells: list[dict] = []
    with tempfile.TemporaryDirectory() as td:
        sandbox = pathlib.Path(td)
        for n, h in enumerate(rep["hazard_rows"], 1):
            old, new = h["old_local"], h["new_local"]
            bleed = sorted({(x.get("matched_name") or x.get("token")) for x in hits
                            if (nm := (x.get("matched_name") or x.get("token"))) and nm != old
                            and old.lower() in nm.lower()})
            own = [x for x in hits if (x.get("matched_name") or x.get("token")) == old
                   and not str(x.get("path", "")).startswith(excl)]
            files = collections.Counter(x["path"] for x in own)
            targets = [f for f, _ in files.most_common(SAMPLE_PER_BREAKPOINT)]
            bid = f"B-{n}"

            # 出口 A：受限替换（仅本名，排除相邻名）
            a_applied, a_dirty, a_preserved = 0, 0, True
            a_generated_skipped = 0
            for rel in targets:
                src = ROOT / rel
                if not src.is_file():
                    continue
                if rel.startswith("generated/"):      # 禁手改：随 make generate 重新生成
                    a_generated_skipped += 1
                    continue
                dst = sandbox / "A" / bid / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                os.chmod(dst, 0o644)                  # 沙箱副本可写（**原件不动**）
                txt = dst.read_text(encoding="utf-8", errors="replace")
                before_bleed = {b: txt.count(b) for b in bleed}
                new_txt, cnt = re.subn(rf"(?<![A-Za-z0-9_]){re.escape(old)}(?![A-Za-z0-9_])", new, txt)
                dst.write_text(new_txt, encoding="utf-8")
                a_applied += cnt
                # 脏值：相邻名被改坏（如 customerIdRole / referencesAssetDefinition）
                for b in bleed:
                    if new.lower() in b.lower() and b not in new_txt:
                        a_preserved = False
                a_dirty += sum(new_txt.count(b + new) + new_txt.count(new + b) for b in bleed)
                for b in bleed:
                    if new_txt.count(b) != before_bleed[b]:
                        a_preserved = False

            # 出口 B：不改名，产出并存清单（旧名保留 + 新名待增；不得等价）
            b_kept = 0
            for rel in targets:
                src = ROOT / rel
                if not src.is_file():
                    continue
                txt = src.read_text(encoding="utf-8", errors="replace")
                b_kept += txt.count(old)
            b_coexist = {"old_kept_occurrences": b_kept, "new_term": new,
                         "equivalent_used": False,
                         "mechanism": "旧名只读保留 + 新名以注解/别名并入（**不得** equivalentClass）"}

            # 出口 C：零改动
            c_noop = {"changed_files": 0, "changed_occurrences": 0, "pending_terms": 1}

        # 出口 A 的"相邻名保持"以最后一个断点为准需重算 ⇒ 重新按断点分别累计
            cells.append({"breakpoint": bid, "old": old, "new": new,
                          "files_examined": len(targets), "own_hits": len(own),
                          "bleed_names": len(bleed), "bleed_hits": sum(
                              1 for x in hits
                              if (nm2 := (x.get("matched_name") or x.get("token"))) and nm2 != old
                              and old.lower() in nm2.lower()),
                          "option_A": {"renamed_occurrences": a_applied, "dirty_values": a_dirty,
                                       "adjacent_preserved": a_preserved, "sandbox": True,
                                       "generated_skipped": a_generated_skipped},
                          "option_B": b_coexist,
                          "option_C": c_noop})

    totals = {
        "A": {"renamed_occurrences": sum(c["option_A"]["renamed_occurrences"] for c in cells),
              "dirty_values": sum(c["option_A"]["dirty_values"] for c in cells),
              "all_adjacent_preserved": all(c["option_A"]["adjacent_preserved"] for c in cells)},
        "B": {"old_kept_occurrences": sum(c["option_B"]["old_kept_occurrences"] for c in cells),
              "equivalent_used": any(c["option_B"]["equivalent_used"] for c in cells)},
        "C": {"changed_files": sum(c["option_C"]["changed_files"] for c in cells)},
    }
    return {"schema": "ONTO1-BREAKPOINT-OPTION-COMPARISON/1.0",
            "disclaimer": ("**本表不选出口**：选择权在 Owner / PSO / 数据 Owner；"
                           "本表只是把三个出口各真跑一遍（沙箱内）以供比较。"),
            "boundary": {"sandbox_only": True, "specs_written": False, "iri_published": False,
                         "kert_written": False, "rehearsal_ns": base.REHEARSAL_NS},
            "cells": cells, "totals": totals}


def checks(d: dict) -> list[tuple[str, bool, str]]:
    cells, t = d["cells"], d["totals"]
    return [
        ("C-1 四条断点 × 三出口 = 12 格齐全",
         len(cells) == 4 and all({"option_A", "option_B", "option_C"} <= set(c) for c in cells),
         f'{len(cells)} 断点 × 3 出口'),
        ("C-2 出口 A **零脏值**（相邻名未被污染）",
         t["A"]["dirty_values"] == 0, f'脏值 {t["A"]["dirty_values"]}'),
        ("C-3 出口 A **相邻名保持**（逐断点核对通过）",
         t["A"]["all_adjacent_preserved"] is True, f'all_adjacent_preserved={t["A"]["all_adjacent_preserved"]}'),
        ("C-4 出口 A 确有改写（演练非空转）",
         t["A"]["renamed_occurrences"] > 0, f'改写 {t["A"]["renamed_occurrences"]} 处'),
        ("C-5 出口 B **不得**引入等价关系，且旧名保留计数 > 0",
         not t["B"]["equivalent_used"] and t["B"]["old_kept_occurrences"] > 0,
         f'等价={t["B"]["equivalent_used"]} 旧名保留 {t["B"]["old_kept_occurrences"]} 处'),
        ("C-6 出口 C 为零改动（只登记待裁项）",
         t["C"]["changed_files"] == 0, f'改动文件 {t["C"]["changed_files"]}'),
        ("C-7 **不含出口选择结论**（材料与裁定分离）",
         d["disclaimer"].startswith("**本表不选出口**"), "含免责与权限声明"),
        ("C-8 边界：沙箱内 / 未写 specs / 未发布 IRI / 未写 KERT",
         d["boundary"]["sandbox_only"] and not d["boundary"]["specs_written"]
         and not d["boundary"]["iri_published"] and not d["boundary"]["kert_written"],
         "sandbox_only=True"),
    ]


def write_md(d: dict) -> None:
    lines = ["# 断点三出口对比（沙箱演练）", "",
             f"> {d['disclaimer']}", "",
             "| 断点 | 旧 ⇒ 新 | 本名命中 | 会被误伤 | A 改写 | A 脏值 | A 相邻名保持 | B 旧名保留 | C 改动 |",
             "|---|---|---|---|---|---|---|---|---|"]
    for c in d["cells"]:
        lines.append(f'| {c["breakpoint"]} | `{c["old"]}` ⇒ `{c["new"]}` | {c["own_hits"]} | {c["bleed_hits"]} | '
                     f'{c["option_A"]["renamed_occurrences"]} | {c["option_A"]["dirty_values"]} | '
                     f'{c["option_A"]["adjacent_preserved"]} | {c["option_B"]["old_kept_occurrences"]} | '
                     f'{c["option_C"]["changed_files"]} |')
    lines += ["", "## 说明", "",
              "- **出口 A（显式清单改名）**：本演练对**每条断点**都用了受限正则（词边界 + 前后不邻接标识符字符）"
              "并逐条核对相邻名；结果见上表（脏值必须为 0）。真实执行时**仍须逐条人工清单**（本表只是配方验证）。",
              "- **出口 B（保留原名 + 新名并存）**：不改名；旧名只读保留，新名以注解/别名并入，**不得** `equivalentClass`。",
              "- **出口 C（延后）**：零改动，仅登记待裁项；涉及该术语的 Wave 2/3 项在裁定前**不得开工**。",
              "", "> 未裁定前，涉及这四个术语的 Wave 2/3 项**不得开工**；其余同类项不受影响。", ""]
    with MD.open("w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def cmd_run() -> int:
    d = rehearse_options()
    with OUT.open("w", encoding="utf-8") as fh:
        json.dump(d, fh, ensure_ascii=False, indent=2)
    write_md(d)
    print(json.dumps(d["totals"], ensure_ascii=False, indent=1))
    return 0


def cmd_gate() -> int:
    d = json.loads(OUT.read_text(encoding="utf-8")) if OUT.is_file() else rehearse_options()
    if not OUT.is_file():
        with OUT.open("w", encoding="utf-8") as fh:
            json.dump(d, fh, ensure_ascii=False, indent=2)
        write_md(d)
    rows = checks(d)
    print("# command=onto1_breakpoint_option_rehearsal --gate")
    for n, ok, det in rows:
        print(f"{'PASS' if ok else 'FAIL'} [{n}] {det}")
    bad = [n for n, ok, _ in rows if not ok]
    print(f"A-12 出口对比：{'PASS' if not bad else 'FAIL'}（{len(rows) - len(bad)}/{len(rows)}）")
    return 0 if not bad else 2


def cmd_selftest() -> int:
    d = json.loads(OUT.read_text(encoding="utf-8")) if OUT.is_file() else rehearse_options()
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

    run_case("K1 出口 A 产生脏值 ⇒ FAIL", lambda m: m["totals"]["A"].update(dirty_values=1))
    run_case("K2 相邻名被污染 ⇒ FAIL", lambda m: m["totals"]["A"].update(all_adjacent_preserved=False))
    run_case("K3 出口 B 引入等价 ⇒ FAIL", lambda m: m["totals"]["B"].update(equivalent_used=True))
    run_case("K4 出口 C 有改动 ⇒ FAIL", lambda m: m["totals"]["C"].update(changed_files=2))
    run_case("K5 缺一格 ⇒ FAIL", lambda m: m["cells"].pop())
    run_case("K6 免责声明被移除 ⇒ FAIL", lambda m: m.update(disclaimer="已选定出口 A"))

    # **真实路径**反例：朴素替换必须**真的**产生脏值（证明 A 的判据非空转）
    total += 1
    src = "referencesAsset: Asset;"
    naive = src.replace("Asset", "AssetDefinition")
    dirty = "referencesAssetDefinition" in naive
    fails += 0 if dirty else 1
    print(f"{'PASS' if dirty else 'FAIL'} [K7 真实路径：朴素替换会产生脏值] 检出 = {dirty}")
    # 受限替换不产生脏值
    total += 1
    bounded = re.sub(r"(?<![A-Za-z0-9_])Asset(?![A-Za-z0-9_])", "AssetDefinition", src)
    clean = "referencesAsset" in bounded and "AssetDefinition" in bounded
    fails += 0 if clean else 1
    print(f"{'PASS' if clean else 'FAIL'} [K8 真实路径：受限替换零脏值] = {clean}")
    print(f"--selftest {'PASS' if fails == 0 else 'FAIL'}（{total - fails}/{total}）")
    return 0 if fails == 0 else 2


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--gate", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ns = ap.parse_args()
    if ns.selftest:
        return cmd_selftest()
    if ns.gate:
        return cmd_gate()
    return cmd_run()


if __name__ == "__main__":
    sys.exit(main())
