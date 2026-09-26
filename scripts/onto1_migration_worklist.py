#!/usr/bin/env python3
"""A-14｜Wave 2/3 **施工清单**（把 A-11 的 462 条演练结果固化为逐文件工作单）

复用 `onto1_sim_rehearsal_full.rehearse_one`（唯一实现），逐文件给出：
仓库 / 文件 / 批次 / 责任 Wave / 该走哪条通道 / IRI 级替换数 / 受限改名数 / 是否因盲替换风险跳过 / 处理口径。
**只读仓内文件 + 沙箱写入**；不写 `specs/**`、不写 KERT。

制品：`evidence/prep/migration-worklist.{csv,md}`
用法：`--build` / `--gate` / `--selftest`
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import onto1_construction_plan as cp  # noqa: E402
import onto1_sim_rehearsal as base  # noqa: E402
import onto1_sim_rehearsal_full as full  # noqa: E402
import onto1_sim_rehearsal_multibatch as mb  # noqa: E402

ROOT = base.ROOT
PREP = base.PREP
CSV_OUT = PREP / "migration-worklist.csv"
MD_OUT = PREP / "migration-worklist.md"
JSON_OUT = PREP / "migration-worklist.json"


def build() -> dict:
    dyn = base.build()
    mig, retired = dyn["rows"], [m for m in dyn["rows"] if m["kind"] == "RETIRE"]
    ob = cp.load_obligations()
    rows = []
    results = []
    with tempfile.TemporaryDirectory() as td:
        sandbox = pathlib.Path(td)
        for r in ob:
            b = cp.batch_of(r)
            if b not in mb.SIM_BATCHES:
                continue
            res = full.rehearse_one(r["repo"], r["path"], sandbox, mig, retired)
            ap = res.get("applied", {})
            action = res["action"]
            if action == "GENERATED_DERIVED":
                handling = "随 make generate 重新生成（禁手改）"
            elif ap.get("ambiguous_skipped"):
                handling = "含盲替换风险术语 ⇒ **须显式清单后再改**（本轮未盲改）"
            elif ap.get("bounded_rename"):
                handling = "受限改名（词边界）+ IRI 级替换"
            elif ap.get("iri_swap"):
                handling = "IRI 级替换（同名保留）"
            else:
                handling = "无术语命中（仅随命名空间迁移）"
            rows.append({"repo": r["repo"], "file": r["path"], "batch": b,
                         "wave": r.get("responsible_wave", ""), "tier": r.get("tier", ""),
                         "signal": r.get("signal", ""), "action": action, "handling": handling,
                         "iri_swap": ap.get("iri_swap", 0),
                         "bounded_rename": ap.get("bounded_rename", 0),
                         "ambiguous_skipped": ap.get("ambiguous_skipped", 0),
                         "retire_skipped": ap.get("retire_skipped", 0),
                         "parse_ok": res.get("parse_ok", None),
                         "retired_untouched": res.get("retired_untouched", None)})
            results.append(res)
    csv_cols = ["repo", "file", "batch", "wave", "tier", "signal", "action", "handling",
                "iri_swap", "bounded_rename", "ambiguous_skipped", "retire_skipped"]
    with CSV_OUT.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=csv_cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    by_batch = collections.Counter(r["batch"] for r in rows)
    by_handling = collections.Counter(r["handling"] for r in rows)
    md = ["# Wave 2/3 施工清单（由 A-11 演练结果固化）", "",
          f'- 条目 **{len(rows)}**：' + " · ".join(f"{k} {v}" for k, v in by_batch.items()),
          f'- 处理口径分布：' + " · ".join(f"{k}（{v}）" for k, v in by_handling.items()), "",
          "| 仓库 | 文件 | 批次 | 责任 Wave | 处理口径 | IRI 替换 | 受限改名 | 盲风险跳过 |",
          "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f'| {r["repo"]} | `{r["file"]}` | {r["batch"].split("_")[0]} | {r["wave"]} | '
                  f'{r["handling"]} | {r["iri_swap"]} | {r["bounded_rename"]} | {r["ambiguous_skipped"]} |')
    md += ["", "> **使用方式**：按 `handling` 分派 —— 『随 make generate』的交由制品流水线；"
               "『须显式清单』的**不得批处理**（见 `breakpoint-advisory/`）；其余可按通道机械执行。",
           "> 未裁定四条断点出口前，涉及 `Customer / Product / Skill / Asset` 的项**不得开工**。", ""]
    with MD_OUT.open("w", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")
    data = {"schema": "ONTO1-MIGRATION-WORKLIST/1.0",
            "rows_total": len(rows), "by_batch": dict(by_batch), "by_handling": dict(by_handling),
            "by_action": dict(collections.Counter(r["action"] for r in rows)),
            "parse_failures": [x["file"] for x in results
                               if x.get("rehearsed") and x.get("parse_ok") is False],
            "retired_violations": [x["file"] for x in results if x.get("retired_untouched") is False],
            "reason": [{"file": x["file"], "reason": x.get("reason")} for x in results
                       if x.get("action") == "GENERATED_DERIVED"][:5]}
    with JSON_OUT.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    return data


def checks(d: dict) -> list[tuple[str, bool, str]]:
    return [
        ("W1 条目数 = 462（与 A-11 一致）", d["rows_total"] == 462, f'{d["rows_total"]}'),
        ("W2 四批次齐全且与计划计数一致",
         all(d["by_batch"].get(f"{b}_{suffix}", 0) > 0 for b, suffix in
             (("B2", "L1_L2_语义规格层"), ("B4", "L3_运行本体"), ("B7", "导入级耦合（代码导入本体包）"),
              ("B8", "内容级重绑（IRI/词表/哈希）"))),
         d["by_batch"]),
        ("W3 处理口径**非空且逐类计数为正**（原先字典为空时恒真，已修）",
         len(d["by_handling"]) > 0 and all(v > 0 for v in d["by_handling"].values()),
         f'口径种类 {len(d["by_handling"])}：{d["by_handling"]}'),
        ("W4 演练后 TTL 全可解析（0 失败）", not d["parse_failures"],
         f'失败 {len(d["parse_failures"])}'),
        ("W5 退役项 0 违例", not d["retired_violations"], f'违例 {len(d["retired_violations"])}'),
        ("W6 `generated/**` 项数与原因记录**一致**（原为 `>=0` 同义反复，已修）",
         len(d["reason"]) == d["by_action"].get("GENERATED_DERIVED", 0)
         and all(r.get("reason") for r in d["reason"]),
         f'generated 项 {d["by_action"].get("GENERATED_DERIVED", 0)} / 原因记录 {len(d["reason"])}'),
    ]


def cmd_gate() -> int:
    d = build()
    rows = checks(d)
    print("# command=onto1_migration_worklist --gate")
    for n, ok, det in rows:
        print(f"{'PASS' if ok else 'FAIL'} [{n}] {det}")
    bad = [n for n, ok, _ in rows if not ok]
    print(f"A-14 施工清单：{'PASS' if not bad else 'FAIL'}（{len(rows) - len(bad)}/{len(rows)}）")
    return 0 if not bad else 2


def cmd_selftest() -> int:
    d = json.loads(JSON_OUT.read_text(encoding="utf-8")) if JSON_OUT.is_file() else build()
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

    run_case("V1 条目数不符 ⇒ FAIL", lambda m: m.update(rows_total=400))
    run_case("V2 批次缺失 ⇒ FAIL", lambda m: m["by_batch"].pop("B7_导入级耦合（代码导入本体包）"))
    run_case("V3 TTL 解析失败 ⇒ FAIL", lambda m: m.update(parse_failures=["x.ttl"]))
    run_case("V4 退役项被改 ⇒ FAIL", lambda m: m.update(retired_violations=["y.java"]))
    run_case("V5 处理口径为空 ⇒ FAIL", lambda m: m.update(by_handling={}))
    run_case("V6 口径计数为非正 ⇒ FAIL", lambda m: m.update(by_handling={"x": 0}))
    run_case("V7 generated 项数 > 原因记录 ⇒ FAIL",
             lambda m: (m["by_action"].update(GENERATED_DERIVED=2), m.update(reason=[])))
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
    print(json.dumps({k: d[k] for k in ("rows_total", "by_batch", "by_handling")}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
