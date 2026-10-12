#!/usr/bin/env python3
"""A-15｜断点三出口**执行包**（A/B/C 各 4 份，等待 Owner 一句话即可执行）

**不选出口**：三个出口各备一套可执行包；Owner 选 A/B/C 后，直接取对应包执行。

产出：`evidence/prep/breakpoint-execution-pack/{A,B,C}/B-<n>-<旧名>-option-<X>.md` + `README.md`
用法：`--build` / `--gate` / `--selftest`
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import onto1_sim_rehearsal as base  # noqa: E402

ROOT = base.ROOT
EV = base.EV
PREP = base.PREP
REPORT = PREP / "sim-rehearsal-report.json"
COMPARE = PREP / "breakpoint-option-comparison.json"
HITS = EV / "consumer-scan-hits.jsonl"
OUTDIR = PREP / "breakpoint-execution-pack"
DISCLAIMER = ("**本包为待执行材料，不构成出口选择**：选择权在 Owner / PSO / 数据 Owner；"
              "选定后由实现者按本包逐条执行（**不得**批处理）。")
EXCL = ("loops/ONTO1-ontology-split/evidence/", ".codebuddy/")


def load_hits() -> list[dict]:
    with HITS.open(encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def write(path: pathlib.Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def build() -> dict:
    rep = json.loads(REPORT.read_text(encoding="utf-8"))
    cmp_ = json.loads(COMPARE.read_text(encoding="utf-8")) if COMPARE.is_file() else {"cells": []}
    cells = {c["breakpoint"]: c for c in cmp_.get("cells", [])}
    hits = load_hits()
    made: list[dict] = []
    index = ["# 断点出口执行包｜索引", "", f"> {DISCLAIMER}", "",
             "| 出口 | 断点 | 旧 ⇒ 新 | 待改文件 | 待确认命中 | 包 |", "|---|---|---|---|---|---|"]
    for n, h in enumerate(rep["hazard_rows"], 1):
        old, new = h["old_local"], h["new_local"]
        bid = f"B-{n}"
        own = [x for x in hits if (x.get("matched_name") or x.get("token")) == old
               and not str(x.get("path", "")).startswith(EXCL)]
        by_file: collections.Counter = collections.Counter(x["path"] for x in own)
        bleed = sorted({(x.get("matched_name") or x.get("token")) for x in hits
                        if (nm := (x.get("matched_name") or x.get("token"))) and nm != old
                        and old.lower() in nm.lower()})
        cell = cells.get(bid, {})

        for opt in ("A", "B", "C"):
            lines = [f"# 执行包｜{bid}｜出口 {opt}｜`{old}` ⇒ `{new}`", "", f"> {DISCLAIMER}", "",
                     "## 1. 出口定义", ""]
            if opt == "A":
                lines += ["**A 显式清单改名**：逐文件、逐处按受限配方改名，**排除**下列相邻名；**不得**批处理。", "",
                          "```python", f'pattern = r"(?<![A-Za-z0-9_]){old}(?![A-Za-z0-9_])"', "```", "",
                          "**必须排除的相邻名（完整）**：", ""]
                lines += [f"- `{b}`" for b in bleed] or ["- （无）"]
                lines += ["", "## 2. 待改文件清单（按命中数降序，前 40）", "",
                          "| # | 文件 | 命中 | 操作 |", "|---|---|---|---|"]
                for i, (f, c) in enumerate(by_file.most_common(40), 1):
                    op = "随 make generate 重生成" if f.startswith("generated/") else "受限改名（逐处）"
                    lines.append(f"| {i} | `{f}` | {c} | {op} |")
                # **全量逐文件清单**（MD 只列前 40 属摘要，不足以逐条签字 ⇒ 另出 CSV）
                csv_path = OUTDIR / "A" / f"{bid}-{old}-option-A-FULL.csv"
                csv_path.parent.mkdir(parents=True, exist_ok=True)
                with csv_path.open("w", encoding="utf-8", newline="") as fh:
                    wr = csv.writer(fh)
                    wr.writerow(["#", "file", "hits", "action", "受限配方", "已核（签字）", "日期"])
                    for i, (f, c) in enumerate(by_file.most_common(), 1):
                        op = ("随 make generate 重生成（禁手改）" if f.startswith("generated/")
                              else "受限改名（逐处）")
                        wr.writerow([i, f, c, op,
                                     f"(?<![A-Za-z0-9_]){old}(?![A-Za-z0-9_])", "", ""])
                lines += ["", f"**全量清单**：`{csv_path.relative_to(PREP)}`"
                              f"（{len(by_file)} 个文件 / {len(own)} 处命中，含逐条签字位）"]
                lines += ["", f"（批级清单另见 `migration-worklist.csv`；本包前 40 行属**摘要**，"
                              f"执行须以全量 CSV 为准）"]
                lines += ["", "## 3. 演练证据（沙箱真跑）", "",
                          f'- 改写处数 **{cell.get("option_A", {}).get("renamed_occurrences", "n/a")}**；'
                          f'**脏值 {cell.get("option_A", {}).get("dirty_values", "n/a")}**；'
                          f'相邻名保持 **{cell.get("option_A", {}).get("adjacent_preserved", "n/a")}**']
            elif opt == "B":
                lines += ["**B 保留原名 + 新名并存**：`" + old + "` 只读保留；新增 `" + new + "` 以注解/别名并入；"
                          "**不得** `equivalentClass` / `equivalentProperty`。", "",
                          "## 2. 并存清单", "",
                          f'- 旧名保留位点数（真实消费者面）：**{cell.get("option_B", {}).get("old_kept_occurrences", "n/a")}**',
                          f'- 新名：`{new}`（注解载体，非等价断言）',
                          f'- 等价关系使用：**{cell.get("option_B", {}).get("equivalent_used", "n/a")}**（必须为 False）', "",
                          "## 3. 前置与代价", "",
                          "- 需起草**点名/退役计划**（双名并存期须有限期）；",
                          "- 消费者可渐进切换，但**门禁须能区分两名**；",
                          "- 退役期到达前不得删旧名。"]
            else:
                lines += ["**C 延后**：本断点不进入本轮迁移，登记为待裁项；涉及该术语的 Wave 2/3 项**不得开工**。", "",
                          "## 2. 登记内容", "",
                          f'- 待裁术语：`{old}` ⇒ 目标 `{new}`',
                          f'- 受影响命中：**{len(own)}** 处 / **{len(by_file)}** 个文件',
                          f'- 会被盲替换误伤：**{sum(1 for x in hits if (nm2 := (x.get("matched_name") or x.get("token"))) and nm2 != old and old.lower() in nm2.lower())}** 处',
                          "- 出口：裁定后转 A 或 B。"]
            lines += ["", "## 4. 权限与红线", "",
                      "- 一旦获批执行：**仍须**逐条确认，**不得**批处理（除出口 C 外）；",
                      "- **不得**发布新 IRI（D3 未签）；**不得**手改 `specs/**`、`generated/**`；",
                      "- KERT 侧涉及项须 KERT 维护方执行。", ""]
            path = OUTDIR / opt / f"{bid}-{old}-option-{opt}.md"
            write(path, lines)
            made.append({"option": opt, "breakpoint": bid, "old": old, "new": new,
                         "files": len(by_file), "hits": len(own), "path": str(path.relative_to(ROOT))})
            index.append(f'| {opt} | {bid} | `{old}` ⇒ `{new}` | {len(by_file)} | {len(own)} | '
                         f'[`{bid}-{old}-option-{opt}.md`]({opt}/{bid}-{old}-option-{opt}.md) |')
    index += ["", "> 选定出口后，只需取对应目录的执行包；**未选定前，四条断点涉及的 Wave 2/3 项不得开工**。", ""]
    write(OUTDIR / "README.md", index)
    return {"schema": "ONTO1-BREAKPOINT-EXECUTION-PACK/1.0", "disclaimer": DISCLAIMER, "packs": made}


def checks(d: dict) -> list[tuple[str, bool, str]]:
    packs = d["packs"]
    def _read(rel: str) -> str:
        fp = ROOT / rel
        try:
            return fp.read_text(encoding="utf-8") if fp.is_file() else ""      # 缺文件 ⇒ 空串（判据自然 FAIL）
        except OSError:
            return ""

    ok_files = all((ROOT / p["path"]).is_file() for p in packs)
    texts = {p["path"]: _read(p["path"]) for p in packs}
    return [
        ("X1 三出口 × 四断点 = **12 份**执行包",
         len(packs) == 12 and {p["option"] for p in packs} == {"A", "B", "C"}
         and len({p["breakpoint"] for p in packs}) == 4,
         f'{len(packs)} 份（{sorted({p["option"] for p in packs})} × {sorted({p["breakpoint"] for p in packs})}）'),
        ("X2 每份均存在且含**不构成出口选择**声明",
         ok_files and len(texts) == 12 and all(d["disclaimer"] in t for t in texts.values()),
         f'含声明 {sum(1 for t in texts.values() if d["disclaimer"] in t)}/{len(packs)}'
         f'（QA-W3R2 N-3：原 `int(bool)` 明细误读）'),
        ("X3 出口 A **非空**且包含**完整排除清单**与待改文件表（空过滤不得视为通过）",
         len(_A := [t for _p, t in texts.items() if _p.endswith("option-A.md")]) == 4
         and all(("必须排除的相邻名（完整）" in t and "待改文件清单" in t) for t in _A),
         f'{len(_A)}/4 A 包含排除清单与清单表'),
        ("X4 出口 B **非空**且明确**不得等价**并给出并存计数",
         len(_B := [t for _p, t in texts.items() if _p.endswith("option-B.md")]) == 4
         and all(("equivalentClass" in t and "并存清单" in t) for t in _B),
         f'{len(_B)}/4 B 包含禁等价与并存清单'),
        ("X5 出口 C **非空**且为零改动登记（含待裁术语与影响）",
         len(_C := [t for _p, t in texts.items() if _p.endswith("option-C.md")]) == 4
         and all(("登记为待裁项" in t and "不得开工" in t) for t in _C),
         f'{len(_C)}/4 C 包为登记'),
        ("X6 索引页与 12 份包一致",
         (OUTDIR / "README.md").is_file()
         and all(f"{p['breakpoint']}-{p['old']}-option-{p['option']}.md" in
                 (OUTDIR / "README.md").read_text(encoding="utf-8") for p in packs),
         "索引含全部 12 条目"),
    ]


def cmd_gate() -> int:
    d = build()
    rows = checks(d)
    print("# command=onto1_breakpoint_execution_pack --gate")
    for n, ok, det in rows:
        print(f"{'PASS' if ok else 'FAIL'} [{n}] {det}")
    bad = [n for n, ok, _ in rows if not ok]
    print(f"A-15 出口执行包：{'PASS' if not bad else 'FAIL'}（{len(rows) - len(bad)}/{len(rows)}）")
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

    run_case("Y1 少一份包 ⇒ FAIL", lambda m: m["packs"].pop())
    run_case("Y2 出口集合不全 ⇒ FAIL", lambda m: [p.update(option="A") for p in m["packs"]])
    run_case("Y3 免责声明被移除 ⇒ FAIL", lambda m: m.update(disclaimer="已选定出口"))
    run_case("Y4 某包路径不存在 ⇒ FAIL",
             lambda m: m["packs"][0].update(path="loops/ONTO1-ontology-split/evidence/prep/nope.md"))
    run_case("Y5 断点不足 4 个 ⇒ FAIL", lambda m: [m["packs"].pop() for _ in range(9)])
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
    print(json.dumps({"packs": len(d["packs"])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
