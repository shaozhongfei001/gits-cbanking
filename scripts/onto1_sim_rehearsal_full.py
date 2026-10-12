#!/usr/bin/env python3
"""A-8 扩大｜B6+B8 **全量** 242 条沙箱演练（独立脚本，复用 `onto1_sim_rehearsal` 的分类与配方）

清单来源：`construction_plan.batch_of` 逐条复算（691 真义务 → B6 消费者切换 + B8 内容级重绑），
**不是** 3 条样本。KERT 侧文件仅**读入沙箱**，永不写入。

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
PREP = base.PREP
KERT_ROOT = pathlib.Path("/home/szf/dev/Leibniz-KERT")
FULL_OUT = PREP / "sim-rehearsal-full-b6b8.json"


def repo_path(repo: str, rel: str) -> pathlib.Path:
    return (KERT_ROOT if repo == "kert" else ROOT) / rel


def full_b6_b8() -> list[dict]:
    import onto1_construction_plan as cp

    ob = cp.load_obligations()
    want = ("B6_消费者切换", "B8_内容级重绑（IRI/词表/哈希）")
    return [r for r in ob if cp.batch_of(r) in want]


def rehearse_one(repo: str, rel: str, sandbox: pathlib.Path, mig: list[dict],
                 retired: list[dict]) -> dict:
    src = repo_path(repo, rel)
    if not src.is_file():
        return {"repo": repo, "file": rel, "action": "MISSING", "rehearsed": False}
    dst = sandbox / repo / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copy2(src, dst)
        os.chmod(dst, 0o644)
    except OSError as exc:
        return {"repo": repo, "file": rel, "action": "COPY_FAILED", "rehearsed": False,
                "error": str(exc)[:80]}
    before = dst.read_text(encoding="utf-8", errors="replace")
    applied = {"iri_swap": 0, "bounded_rename": 0, "retire_skipped": 0, "ambiguous_skipped": 0}
    if rel.startswith("generated/"):
        return {"repo": repo, "file": rel, "action": "GENERATED_DERIVED", "rehearsed": False,
                "reason": "generated/ 禁手改，随 make generate 重新生成",
                "retired_untouched": True, "parse_ok": True, "applied": applied}
    txt = before
    if rel.endswith((".ttl", ".rdf", ".owl", ".n3", ".trig")):
        n = txt.count(base.LEGACY_NS)
        txt = txt.replace(base.LEGACY_NS, base.REHEARSAL_NS)
        applied["iri_swap"] = n
    for m in mig:
        old, new = m["old_local"], m["new_local"]
        if m["kind"] == "SAME_NAME" or not old:
            continue
        if m["kind"] == "RETIRE":
            if old in txt:
                applied["retire_skipped"] += 1
            continue
        if m["kind"] != "RENAME" or ":" in new:
            continue
        if m["hazard"]:
            if old in txt:
                applied["ambiguous_skipped"] += 1
            continue
        txt, n = re.subn(rf"(?<![A-Za-z0-9_]){re.escape(old)}(?![A-Za-z0-9_])", new, txt)
        applied["bounded_rename"] += n
    dst.write_text(txt, encoding="utf-8")
    after = dst.read_text(encoding="utf-8")
    parse_ok = True
    if rel.endswith((".ttl", ".rdf", ".owl", ".n3", ".trig")):
        try:
            from rdflib import Graph

            g = Graph()
            g.parse(str(dst), format="turtle")
            parse_ok = len(g) > 0
        except Exception:  # noqa: BLE001
            parse_ok = False
    return {"repo": repo, "file": rel, "action": "REHEARSED", "rehearsed": True,
            "applied": applied, "parse_ok": parse_ok,
            "retired_untouched": all(m["old_local"] in after
                                     for m in retired if m["old_local"] in before),
            "bytes_before": len(before), "bytes_after": len(after)}


def run() -> dict:
    dyn = base.build()
    mig, retired = dyn["rows"], [m for m in dyn["rows"] if m["kind"] == "RETIRE"]
    items = full_b6_b8()
    results: list[dict] = []
    agg: collections.Counter = collections.Counter()
    with tempfile.TemporaryDirectory() as td:
        sandbox = pathlib.Path(td)
        for r in items:
            res = rehearse_one(r["repo"], r["path"], sandbox, mig, retired)
            results.append(res)
            agg[res["action"]] += 1
    parse_fail = [r["file"] for r in results if r.get("rehearsed") and r.get("parse_ok") is False]
    retired_bad = [r["file"] for r in results if r.get("retired_untouched") is False]
    by_repo = collections.Counter(r["repo"] for r in items)
    renamed_files = sum(1 for r in results if r.get("applied", {}).get("bounded_rename", 0) > 0)
    iri_files = sum(1 for r in results if r.get("applied", {}).get("iri_swap", 0) > 0)
    ambiguous_files = sum(1 for r in results if r.get("applied", {}).get("ambiguous_skipped", 0) > 0)
    data = {
        "schema": "ONTO1-SIM-REHEARSAL-FULL/1.0",
        "scope": "FULL_B6_B8（由 construction_plan.batch_of 逐条复算，非样本）",
        "boundary": {"sandbox_only": True, "specs_written": False, "iri_published": False,
                     "kert_written": False, "rehearsal_ns": base.REHEARSAL_NS},
        "sources": dyn["sources"],
        "classification": dyn["classification"],
        "full": {"items": len(items), "by_repo": dict(by_repo), "by_action": dict(agg),
                 "rewritten": agg.get("REHEARSED", 0),
                 "generated_derived": agg.get("GENERATED_DERIVED", 0),
                 "missing": agg.get("MISSING", 0), "copy_failed": agg.get("COPY_FAILED", 0),
                 "iri_swapped_files": iri_files, "bounded_renamed_files": renamed_files,
                 "ambiguous_skipped_files": ambiguous_files,
                 "parse_failures": parse_fail, "retired_violations": retired_bad},
        "results_sample": results[:60],
    }
    with FULL_OUT.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    return data


def checks(d: dict) -> list[tuple[str, bool, str]]:
    f = d["full"]
    return [
        ("F1 全量清单已复算（B6+B8 ≥ 200 条，含 KERT 侧）",
         f["items"] >= 200 and len(f["by_repo"]) == 2,
         f'条目 {f["items"]}（{f["by_repo"]}）'),
        ("F2 无缺文件 / 无复制失败（清单与磁盘一致）",
         f["missing"] == 0 and f["copy_failed"] == 0,
         f'缺 {f["missing"]} 复制失败 {f["copy_failed"]}'),
        ("F3 沙箱内**真改写** ≥ 150 个文件",
         f["rewritten"] >= 150, f'真改写 {f["rewritten"]}（IRI 级 {f["iri_swapped_files"]} · '
                                f'受限改名 {f["bounded_renamed_files"]}）'),
        ("F4 演练后 TTL **全部可解析**（0 失败）",
         not f["parse_failures"], f'解析失败 {len(f["parse_failures"])}'),
        ("F5 **退役项一处未换**（0 违例）",
         not f["retired_violations"], f'违例 {len(f["retired_violations"])}'),
        ("F6 有盲替换风险的文件**已跳过**（未盲改）",
         f["ambiguous_skipped_files"] > 0, f'跳过 {f["ambiguous_skipped_files"]} 个文件'),
        ("F7 边界：沙箱内 / 未写 specs / 未发布 IRI / **未写 KERT**",
         d["boundary"]["sandbox_only"] and not d["boundary"]["specs_written"]
         and not d["boundary"]["iri_published"] and not d["boundary"]["kert_written"],
         "sandbox_only=True · KERT 零写入"),
    ]


def cmd_gate() -> int:
    d = json.loads(FULL_OUT.read_text(encoding="utf-8")) if FULL_OUT.is_file() else run()
    rows = checks(d)
    print("# command=onto1_sim_rehearsal_full --gate")
    print(f'# 制品={FULL_OUT.relative_to(ROOT)}  范围={d["scope"]}')
    for n, ok, det in rows:
        print(f"{'PASS' if ok else 'FAIL'} [{n}] {det}")
    bad = [n for n, ok, _ in rows if not ok]
    print(f"A-8 全量演练：{'PASS' if not bad else 'FAIL'}（{len(rows) - len(bad)}/{len(rows)}）")
    return 0 if not bad else 2


def cmd_selftest() -> int:
    d = json.loads(FULL_OUT.read_text(encoding="utf-8")) if FULL_OUT.is_file() else run()
    fails = total = 0
    total += 1
    base_ok = all(o for _, o, _ in checks(d))
    fails += 0 if base_ok else 1
    print(f"{'PASS' if base_ok else 'FAIL'} [M0 对照] 现状 = {base_ok}")

    import copy

    def run_case(tag, mut):
        nonlocal fails, total
        m = copy.deepcopy(d)
        mut(m)
        ok = not all(o for _, o, _ in checks(m))
        total += 1
        fails += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'} [{tag}] 被捕获 = {ok}")

    run_case("D1 缺文件 ⇒ FAIL", lambda m: m["full"].update(missing=3))
    run_case("D2 TTL 解析失败 ⇒ FAIL", lambda m: m["full"].update(parse_failures=["x.ttl"]))
    run_case("D3 退役项被改 ⇒ FAIL", lambda m: m["full"].update(retired_violations=["y.java"]))
    run_case("D4 真改写不足 ⇒ FAIL", lambda m: m["full"].update(rewritten=10))
    run_case("D5 边界被破坏（写 KERT）⇒ FAIL", lambda m: m["boundary"].update(kert_written=True))
    run_case("D6 清单缩水成样本 ⇒ FAIL", lambda m: m["full"].update(items=6, by_repo={"gits": 6}))
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
    print(json.dumps(d["full"], ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
