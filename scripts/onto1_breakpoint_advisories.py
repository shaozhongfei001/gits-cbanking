#!/usr/bin/env python3
"""A-10｜断点逐条裁定材料（4 条"盲替换风险"断点各一页）

**本脚本只产材料，不产裁定**：命名与语义由 **PSO / 数据 Owner** 裁定；我只提供
事实（命中数、受影响文件）、**受限替换正则**、**排除清单**与三个可选出口及其影响。

依据：`evidence/prep/sim-rehearsal-report.json` 的 `hazard_rows` + `consumer-scan-hits.jsonl`。

产出：`evidence/prep/breakpoint-advisory/B-<n>-<旧名>.md`（每条一页）+ `README.md` 索引。
用法：`--build` / `--gate` / `--selftest`
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import sys

ROOT = pathlib.Path("/home/szf/dev/gits-cbanking")
EV = ROOT / "loops/ONTO1-ontology-split/evidence"
PREP = EV / "prep"
REPORT = PREP / "sim-rehearsal-report.json"
HITS = EV / "consumer-scan-hits.jsonl"
OUTDIR = PREP / "breakpoint-advisory"
FULL = PREP / "sim-rehearsal-full-b6b8.json"

DISCLAIMER = ("**本页为裁定材料，不构成裁定**：命名与语义由 **PSO / 数据 Owner** 裁定；"
              "TL 只提供事实、正则、排除清单与可选出口。")


def load_hits() -> list[dict]:
    with HITS.open(encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def write_lines(path: pathlib.Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def build() -> dict:
    rep = json.loads(REPORT.read_text(encoding="utf-8"))
    hazards = rep["hazard_rows"]
    hits = load_hits()
    full = json.loads(FULL.read_text(encoding="utf-8")) if FULL.is_file() else {"full": {}}

    index_lines = [
        "# 断点裁定材料｜索引",
        "",
        "| # | 旧名 → 新名 | 本名命中 | 会被误伤 | 文件数 | 材料 |",
        "|---|---|---|---|---|---|",
    ]
    advisories = []
    for n, h in enumerate(hazards, 1):
        old, new = h["old_local"], h["new_local"]
        # 排除**扫描器自身产物与工具配置**（处置词表：SCAN_INSTRUMENT / TOOLING_CONFIG）
        EXCL = ("loops/ONTO1-ontology-split/evidence/", ".codebuddy/")
        own_all = [x for x in hits if (x.get("matched_name") or x.get("token")) == old]
        own = [x for x in own_all if not str(x.get("path", "")).startswith(EXCL)]
        self_excluded = len(own_all) - len(own)
        bleed = [x for x in hits
                 if (nm := (x.get("matched_name") or x.get("token"))) and nm != old
                 and old.lower() in nm.lower()]
        by_file: collections.Counter = collections.Counter(f'{x["repo"]}:{x["path"]}' for x in own)
        top = by_file.most_common(10)
        bleed_names = sorted({(x.get("matched_name") or x.get("token")) for x in bleed})
        sample_lines = [f'{x["path"]}:{x["line"]}' for x in own[:8]]

        lines = [
            f"# 断点 B-{n}｜`{old}` → `{new}`",
            "",
            f"> {DISCLAIMER}",
            "",
            "## 1. 事实（可复算）",
            "",
            f"- **本名命中（真实消费者面）**：{len(own)} 处（{len(by_file)} 个文件）",
            f"- 已排除**扫描器自身产物/工具配置**命中：{self_excluded} 处（不计入受影响面）",
            f"- **会被朴素替换误伤的同形/包含命中**：{len(bleed)} 处",
            f'- 误伤名样例：{", ".join("`" + x + "`" for x in bleed_names[:10])}',
            f'- 本名命中样例：{", ".join("`" + x + "`" for x in sample_lines[:5])}',
            f'- 全量演练（B6+B8 {full.get("full", {}).get("items", "n/a")} 条）中"含本词但被跳过"的文件：见 §4',
            "",
            "## 2. 受影响面（Top 10 文件）",
            "",
            "| 文件 | 命中 |",
            "|---|---|",
        ]
        for f, c in top:
            lines.append(f"| `{f}` | {c} |")
        lines += [
            "",
            "## 3. 受限替换配方（**仅供引用，须经裁定后使用**）",
            "",
            "```python",
            f'pattern = r"(?<![A-Za-z0-9_]){old}(?![A-Za-z0-9_])"   # 词边界 + 前后不邻接标识符字符',
            "```",
            "",
            "**必须排除的相邻名**（否则会产出 `customerIdRole`、`referencesAssetDefinition` 之类脏值）：",
            "",
        ]
        if bleed_names:
            lines.append(f"（共 {len(bleed_names)} 个）")
            for b in bleed_names:
                lines.append(f"- `{b}`")
        else:
            lines.append("- （本名词形下未检出相邻名 ⇒ 仍需逐条回源确认）")
        lines += [
            "",
            "## 4. 三个可选出口（**各有代价，须裁定**）",
            "",
            "| 出口 | 做法 | 代价 / 前置 |",
            "|---|---|---|",
            f"| **A 显式清单改名** | 逐文件、逐行按受限配方改名 `{old}` → `{new}`，排除上列相邻名 | 需逐条人工确认；{len(own)} 处命中须全部核对；**不得批处理** |",
            f"| **B 保留原名 + 新名并存** | `{old}` 保持只读，新增 `{new}` 并以注解标注继承关系（**不得** `equivalentClass`） | 双名并存期需点名与退役计划；消费者可渐进切换 |",
            f"| **C 延后** | 本断点不进入本轮迁移，登记为待裁项 | 阻塞该术语相关的 Wave 2/3 项；须在退出前补齐 |",
            "",
            "## 5. 与全量演练的一致性",
            "",
            f'- 演练范围：B6+B8 **{full.get("full", {}).get("items", "n/a")}** 条；真改写 '
            f'**{full.get("full", {}).get("rewritten", "n/a")}**；含盲替换风险被**跳过**的文件 '
            f'**{full.get("full", {}).get("ambiguous_skipped_files", "n/a")}** 个 ⇒ 本断点的改名在演练中**未被自动执行**（设计如此）。',
            "",
            "## 6. 我不做什么",
            "",
            "- 不替你选定出口（名称与语义属 PSO / 数据 Owner 权限）；",
            "- 不把本页当作已完成的迁移；",
            "- 不在 `specs/**` 写入任何对应改动。",
            "",
        ]
        fname = f"B-{n}-{old}.md"
        write_lines(OUTDIR / fname, lines)
        page_text = (OUTDIR / fname).read_text(encoding="utf-8")
        advisories.append({"id": f"B-{n}", "old": old, "new": new, "own_hits": len(own),
                           "bleed_hits": len(bleed), "files": len(by_file),
                           "bleed_names": len(bleed_names),
                           "exclusions_complete": all(b in page_text for b in bleed_names),
                           "self_excluded": self_excluded,
                           "path": str((OUTDIR / fname).relative_to(ROOT))})
        index_lines.append(f'| B-{n} | `{old}` → `{new}` | {len(own)} | {len(bleed)} | {len(by_file)} | '
                           f'[`{fname}`]({fname}) |')

    index_lines += [
        "",
        "> **给 Owner 的一句**：四条断点各自只差一个选择（A 显式清单改名 / B 并存 / C 延后）。",
        "> 未裁定前，Wave 2/3 涉及这四个术语的项**不得开工**；其余同类项不受影响。",
        "",
    ]
    write_lines(OUTDIR / "README.md", index_lines)
    return {"schema": "ONTO1-BREAKPOINT-ADVISORY/1.0",
            "disclaimer": DISCLAIMER, "advisories": advisories,
            "full_scope": full.get("full", {})}


def checks(d: dict) -> list[tuple[str, bool, str]]:
    rows = d["advisories"]
    ok_all = []
    for a in rows:
        txt = (ROOT / a["path"]).read_text(encoding="utf-8")
        ok_all.append(all(x in txt for x in [
            a["old"], a["new"], "可复算", "受限替换配方", "必须排除的相邻名",
            "A 显式清单改名", "B 保留原名 + 新名并存", "C 延后", "不构成裁定"]))
    return [
        ("A10-1 四条断点各出一页材料（B-1~B-4）",
         len(rows) == 4 and sorted(a["id"] for a in rows) == ["B-1", "B-2", "B-3", "B-4"],
         f'条目 {[a["id"] for a in rows]}'),
        ("A10-2 每页含：事实 / 受限正则 / 排除清单 / 三个出口 / **不构成裁定**声明",
         all(ok_all), f'合格页 {sum(ok_all)}/{len(rows)}'),
        ("A10-3 每页排除清单**完整**（页内列全，无截断）",
         all(a["exclusions_complete"] for a in rows),
         f'各页排除名数 {[a["bleed_names"] for a in rows]}；全部列全 = '
         f'{all(a["exclusions_complete"] for a in rows)}'),
        ("A10-4 索引页与全量演练口径一致（条目数引用同一制品）",
         (OUTDIR / "README.md").is_file() and d["full_scope"].get("items", 0) >= 200,
         f'全量条目 {d["full_scope"].get("items")}'),
        ("A10-5 **不含裁定结论**（材料与裁定分离）",
         d["disclaimer"].startswith("**本页为裁定材料") and all("不构成裁定" in
                                                          (ROOT / a["path"]).read_text(encoding="utf-8")
                                                          for a in rows),
         "每页均含免责与权限声明"),
    ]


def cmd_gate() -> int:
    d = build()
    rows = checks(d)
    print("# command=onto1_breakpoint_advisories --gate")
    for n, ok, det in rows:
        print(f"{'PASS' if ok else 'FAIL'} [{n}] {det}")
    bad = [n for n, ok, _ in rows if not ok]
    print(f"A-10 断点材料：{'PASS' if not bad else 'FAIL'}（{len(rows) - len(bad)}/{len(rows)}）")
    return 0 if not bad else 2


def cmd_selftest() -> int:
    d = build()
    fails = total = 0
    total += 1
    base = all(o for _, o, _ in checks(d))
    fails += 0 if base else 1
    print(f"{'PASS' if base else 'FAIL'} [M0 对照] 现状 = {base}")
    import copy

    def run_case(tag, mut):
        nonlocal fails, total
        m = copy.deepcopy(d)
        mut(m)
        ok = not all(o for _, o, _ in checks(m))
        total += 1
        fails += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'} [{tag}] 被捕获 = {ok}")

    run_case("E1 少一页材料 ⇒ FAIL", lambda m: m["advisories"].pop())
    run_case("E2 排除清单不完整 ⇒ FAIL", lambda m: m["advisories"][0].update(exclusions_complete=False))
    run_case("E3 免责声明被移除 ⇒ FAIL", lambda m: m.update(disclaimer="已裁定"))
    run_case("E4 全量口径不一致 ⇒ FAIL", lambda m: m.update(full_scope={}))
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
    print(json.dumps(d["advisories"], ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
