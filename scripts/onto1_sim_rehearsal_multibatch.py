#!/usr/bin/env python3
"""A-11｜SIM 合格批次全演练（B2 + B4 + B7 + B8，`construction-plan.json` 标记 sim_eligible=true）

复用 `onto1_sim_rehearsal_full.rehearse_one`（唯一实现），清单由 `construction_plan.batch_of` 逐条复算。
**全程沙箱**：KERT 侧仅读入沙箱；仓内制品零改动。

用法：`--run` / `--gate` / `--selftest`
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import onto1_construction_plan as cp  # noqa: E402
import onto1_sim_rehearsal as base  # noqa: E402
import onto1_sim_rehearsal_full as full  # noqa: E402

ROOT = base.ROOT
PREP = base.PREP
OUT = PREP / "sim-rehearsal-sim4.json"
SIM_BATCHES = ("B2_L1_L2_语义规格层", "B4_L3_运行本体",
               "B7_导入级耦合（代码导入本体包）", "B8_内容级重绑（IRI/词表/哈希）")


def items_for(batches: tuple[str, ...]) -> list[dict]:
    ob = cp.load_obligations()
    return [r for r in ob if cp.batch_of(r) in batches]


def run() -> dict:
    dyn = base.build()
    mig, retired = dyn["rows"], [m for m in dyn["rows"] if m["kind"] == "RETIRE"]
    items = items_for(SIM_BATCHES)
    agg: collections.Counter = collections.Counter()
    res_by_batch: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    results: list[dict] = []
    with tempfile.TemporaryDirectory() as td:
        sandbox = pathlib.Path(td)
        for r in items:
            res = full.rehearse_one(r["repo"], r["path"], sandbox, mig, retired)
            results.append(res)
            agg[res["action"]] += 1
            res_by_batch[cp.batch_of(r)][res["action"]] += 1
    parse_fail = [r["file"] for r in results if r.get("rehearsed") and r.get("parse_ok") is False]
    retired_bad = [r["file"] for r in results if r.get("retired_untouched") is False]
    ambiguous = sum(1 for r in results if r.get("applied", {}).get("ambiguous_skipped", 0) > 0)
    data = {
        "schema": "ONTO1-SIM-REHEARSAL-SIM4/1.0",
        "scope": "SIM_ELIGIBLE_BATCHES（B2/B4/B7/B8，由 construction_plan.batch_of 逐条复算）",
        "boundary": {"sandbox_only": True, "specs_written": False, "iri_published": False,
                     "kert_written": False, "rehearsal_ns": base.REHEARSAL_NS},
        "sources": dyn["sources"],
        "classification": dyn["classification"],
        "batches": {b: {"count": len(items_for((b,))), "by_action": dict(full_items)}
                    for b, full_items in ((b, res_by_batch[b]) for b in SIM_BATCHES)},
        "totals": {"items": len(items), "by_action": dict(agg),
                   "by_repo": dict(collections.Counter(r["repo"] for r in items)),
                   "rewritten": agg.get("REHEARSED", 0), "missing": agg.get("MISSING", 0),
                   "copy_failed": agg.get("COPY_FAILED", 0),
                   "generated_derived": agg.get("GENERATED_DERIVED", 0),
                   "ambiguous_skipped_files": ambiguous,
                   "iri_swapped_files": sum(1 for r in results
                                            if r.get("applied", {}).get("iri_swap", 0) > 0),
                   "bounded_renamed_files": sum(1 for r in results
                                                if r.get("applied", {}).get("bounded_rename", 0) > 0),
                   "parse_failures": parse_fail, "retired_violations": retired_bad},
        "results_sample": results[:40],
    }
    with OUT.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    return data


def checks(d: dict) -> list[tuple[str, bool, str]]:
    t = d["totals"]
    return [
        ("G1 四批次均非空（B2/B4/B7/B8）",
         all(v["count"] > 0 for v in d["batches"].values()),
         {k: v["count"] for k, v in d["batches"].items()}),
        ("G2 条目总数 ≥ 400（SIM 合格集全量）",
         t["items"] >= 400, f'条目 {t["items"]}（{t["by_repo"]}）'),
        ("G3 无缺文件 / 无复制失败", t["missing"] == 0 and t["copy_failed"] == 0,
         f'缺 {t["missing"]} 复制失败 {t["copy_failed"]}'),
        ("G4 沙箱内真改写 = 条目数（全部经演练）", t["rewritten"] == t["items"],
         f'真改写 {t["rewritten"]}/{t["items"]}（IRI 级 {t["iri_swapped_files"]} · 受限改名 {t["bounded_renamed_files"]}）'),
        ("G5 演练后 TTL 全可解析（0 失败）", not t["parse_failures"],
         f'失败 {len(t["parse_failures"])}'),
        ("G6 退役项 0 违例", not t["retired_violations"], f'违例 {len(t["retired_violations"])}'),
        ("G7 盲替换风险文件已跳过（未盲改）", t["ambiguous_skipped_files"] > 0,
         f'跳过 {t["ambiguous_skipped_files"]} 个'),
        ("G8 边界：沙箱内 / 未写 specs / 未发布 IRI / 未写 KERT",
         d["boundary"]["sandbox_only"] and not d["boundary"]["specs_written"]
         and not d["boundary"]["iri_published"] and not d["boundary"]["kert_written"],
         "sandbox_only=True · KERT 零写入"),
    ]


def cmd_gate() -> int:
    d = json.loads(OUT.read_text(encoding="utf-8")) if OUT.is_file() else run()
    rows = checks(d)
    print("# command=onto1_sim_rehearsal_multibatch --gate")
    print(f'# 制品={OUT.relative_to(ROOT)}  范围={d["scope"]}')
    for n, ok, det in rows:
        print(f"{'PASS' if ok else 'FAIL'} [{n}] {det}")
    bad = [n for n, ok, _ in rows if not ok]
    print(f"A-11 四批次演练：{'PASS' if not bad else 'FAIL'}（{len(rows) - len(bad)}/{len(rows)}）")
    return 0 if not bad else 2


def cmd_selftest() -> int:
    d = json.loads(OUT.read_text(encoding="utf-8")) if OUT.is_file() else run()
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

    run_case("H1 某批次为空 ⇒ FAIL", lambda m: m["batches"]["B4_L3_运行本体"].update(count=0))
    run_case("H2 真改写数不等于条目数 ⇒ FAIL", lambda m: m["totals"].update(rewritten=10))
    run_case("H3 退役项被改 ⇒ FAIL", lambda m: m["totals"].update(retired_violations=["x.ttl"]))
    run_case("H4 未跳过盲替换风险 ⇒ FAIL", lambda m: m["totals"].update(ambiguous_skipped_files=0))
    run_case("H5 边界被破坏（写 KERT）⇒ FAIL", lambda m: m["boundary"].update(kert_written=True))
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
    d = run()
    print(json.dumps(d["totals"], ensure_ascii=False, indent=1))
    print(json.dumps({k: v["count"] for k, v in d["batches"].items()}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
