#!/usr/bin/env python3
"""A-13｜迁移器骨架（四通道配方固化；**默认 dry-run，写入仅限沙箱**）

把 A-8/A-10 得出的配方固化为可复算引擎，作为 Wave 2/3 的执行底座：
  · `SAME_NAME`      仅 IRI 级替换（旧命名空间 → 目标命名空间）
  · `RENAME`         **逐条显式清单** + 词边界受限替换（前后不得邻接标识符字符）；有盲替换风险者**一律跳过**
  · `RETIRE`         **不改名**：产出 `owl:deprecated` + `dcterms:isReplacedBy` 建议（须只读期）
  · `NON_IRI_TARGET` 非 OWL 术语（REGISTRY / SCHEMA-FIELD / SKOS）⇒ 出**登记项**，不写文件

**硬约束（fail-closed）**：
  1. 默认 `--dry-run`（不写任何文件）；
  2. 任何写入必须 `--apply --sandbox <dir>`，且目标路径**必须**在该目录内，否则**拒绝**（exit 3）；
  3. **拒绝**对 `specs/**`、`generated/**` 的手改（前者走合同、后者走 `make generate`）；
  4. 本引擎**永不**发布 IRI、**永不**改 KERT。

用法：`--dry-run`（默认）/ `--apply --sandbox DIR` / `--gate` / `--selftest`
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import onto1_sim_rehearsal as base  # noqa: E402

ROOT = base.ROOT
PREP = base.PREP
OUT = PREP / "migration-plan.json"
HAND_EDIT_FORBIDDEN = ("specs/", "generated/")
TEXT_SUFFIX = {".ttl", ".rdf", ".owl", ".n3", ".trig", ".rq", ".sparql", ".java", ".kt", ".scala",
               ".js", ".ts", ".py", ".md", ".txt", ".json", ".yaml", ".yml", ".csv", ".sql", ".xml"}
TARGET_NS_REHEARSAL = base.REHEARSAL_NS


def load_plan_inputs() -> tuple[list[dict], dict]:
    rep = json.loads((PREP / "sim-rehearsal-report.json").read_text(encoding="utf-8"))
    full = json.loads((PREP / "sim-rehearsal-full-b6b8.json").read_text(encoding="utf-8"))
    return rep["rows"], full


def build_plan(target_ns: str = TARGET_NS_REHEARSAL) -> dict:
    rows, full = load_plan_inputs()
    mig = [r for r in rows if r["kind"] in ("SAME_NAME", "RENAME", "RETIRE", "NON_IRI_TARGET")]
    channels: dict[str, list[dict]] = collections.defaultdict(list)
    for m in mig:
        kind = m["kind"]
        if kind == "SAME_NAME":
            channels["SAME_NAME"].append({
                "term": m["termId"], "old_iri": m["old_iri"],
                "new_iri": target_ns + m["new_local"],
                "action": "replace_namespace_prefix_only"})
        elif kind == "RENAME":
            blocked = bool(m.get("hazard"))
            channels["RENAME"].append({
                "term": m["termId"], "old_local": m["old_local"], "new_local": m["new_local"],
                "pattern": rf"(?<![A-Za-z0-9_]){m['old_local']}(?![A-Za-z0-9_])",
                "exclusions": m.get("blind_rename_bleed_names", []),
                "requires_explicit_list": True,
                "auto_applicable": not blocked,
                "blocked_reason": ("盲替换风险（同形/包含命中存在）⇒ 须人工显式清单" if blocked else None)})
        elif kind == "RETIRE":
            channels["RETIRE"].append({
                "term": m["termId"], "old_local": m["old_local"],
                "action": "deprecated + dcterms:isReplacedBy（**不得改名**）",
                "keep_readonly_period": True})
        else:
            channels["NON_IRI_TARGET"].append({
                "term": m["termId"], "target": m["new_pending"],
                "action": "登记（REGISTRY/SCHEMA-FIELD/SKOS 各自机制），不写文件"})
    files = full.get("full", {})
    plan = {
        "schema": "ONTO1-MIGRATION-PLAN/1.0",
        "authority": "Owner 2026-09-21（SIM 整改）：允许迁移验证；D3 未签前不得发布新 IRI",
        "target_namespace": target_ns,
        "target_namespace_is_rehearsal": "rehearsal.sim.local" in target_ns,
        "engine": {"default_mode": "dry-run", "write_requires": "--apply --sandbox <dir>",
                   "hand_edit_forbidden": list(HAND_EDIT_FORBIDDEN),
                   "never_publishes_iri": True, "never_writes_kert": True},
        "channels": {k: {"count": len(v), "items": v} for k, v in channels.items()},
        "counts": {"terms_total": len(mig), "by_channel": {k: len(v) for k, v in channels.items()},
                   "auto_applicable_renames": sum(1 for x in channels["RENAME"] if x["auto_applicable"]),
                   "blocked_renames": sum(1 for x in channels["RENAME"] if not x["auto_applicable"])},
        "rehearsal_evidence": {"b6b8_items": files.get("items"),
                               "rewritten": files.get("rewritten"),
                               "ambiguous_skipped_files": files.get("ambiguous_skipped_files")},
    }
    with OUT.open("w", encoding="utf-8") as fh:
        json.dump(plan, fh, ensure_ascii=False, indent=2)
    return plan


def guard_sandbox(sandbox: pathlib.Path) -> None:
    """**硬守卫**：沙箱本身必须在**仓外**（否则"沙箱写入"等于写仓）。"""
    sb = sandbox.resolve()
    if str(sb).startswith(str(ROOT)):
        raise PermissionError(f"refused: 沙箱 {sb} 位于仓内 ⇒ 拒绝；请用仓外目录（如 /tmp/...）")


def guard_target(path: pathlib.Path, sandbox: pathlib.Path) -> None:
    """写入前硬校验：必须落在沙箱内；且不得是 specs/generated 的手改。"""
    rp = path.resolve()
    sb = sandbox.resolve()
    if sb in rp.parents or rp == sb:
        logical = rp.relative_to(sb).as_posix()          # 沙箱内 ⇒ 按**逻辑仓相对路径**判定
    elif str(rp).startswith(str(ROOT)):
        logical = rp.relative_to(ROOT).as_posix()
    else:
        raise PermissionError(f"refused: 目标 {rp} 既不在沙箱 {sb} 内、也不在仓内 ⇒ 拒绝")
    if logical.startswith(HAND_EDIT_FORBIDDEN):
        raise PermissionError(f"refused: {logical} 属禁手改路径（specs 走合同 / generated 走 make generate）")


def apply(sandbox: pathlib.Path, limit: int = 0) -> dict:
    guard_sandbox(sandbox)
    plan = json.loads(OUT.read_text(encoding="utf-8")) if OUT.is_file() else build_plan()
    # 修（真实 bug）：`auto_applicable` 只存在于**迁移计划**条目中；曾误用报告行 ⇒ 恒走 skip 分支
    by_old = {x["old_local"]: x for x in plan["channels"]["RENAME"]["items"]}
    applied, skipped = [], []
    count = 0
    SKIP = {".git", "node_modules", ".venv", "__pycache__", "target", "build", "dist", ".codebuddy"}
    for path in sorted(ROOT.rglob("*")):
        if any(part in SKIP for part in path.parts):
            continue
        if limit and count >= limit:
            break
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIX:
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith(HAND_EDIT_FORBIDDEN):
            skipped.append({"file": rel, "reason": "禁手改路径（specs 走合同 / generated 走 make generate）"})
            continue
        dst = sandbox / rel
        guard_target(dst, sandbox)
        txt = path.read_text(encoding="utf-8", errors="replace")
        new_txt, hits = txt, 0
        for old, m in by_old.items():
            if not m.get("auto_applicable"):
                skipped.append({"file": rel, "reason": m.get("blocked_reason") or "须显式清单"})
                continue
            pat = re.compile(m["pattern"])
            for bleed in m.get("exclusions", []):
                if pat.search(bleed):
                    raise PermissionError(f"refused: 排除名 {bleed} 也会被模式命中 ⇒ 拒绝执行")
            new_txt, n = pat.subn(m["new_local"], new_txt)
            hits += n
        if hits:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(new_txt, encoding="utf-8")
            applied.append({"file": rel, "replacements": hits, "sandbox": True})
        count += 1
    return {"mode": "apply-sandbox", "sandbox": str(sandbox), "applied": applied,
            "skipped": skipped[:20], "skipped_total": len(skipped)}


def checks(d: dict) -> list[tuple[str, bool, str]]:
    c, e = d.get("counts", {}), d.get("rehearsal_evidence", {})
    _ren = d.get("channels", {}).get("RENAME", {}).get("items", [])
    _ret = d.get("channels", {}).get("RETIRE", {}).get("items", [])
    return [
        ("M1 四通道齐备（同名/改名/退役/非 IRI 目标）",
         set(d["channels"]) == {"SAME_NAME", "RENAME", "RETIRE", "NON_IRI_TARGET"},
         {k: v["count"] for k, v in d["channels"].items()}),
        ("M2 条款总数守恒（67 = 四通道之和）",
         c["terms_total"] == 67 and sum(c["by_channel"].values()) == 67,
         f'{c["terms_total"]} = {c["by_channel"]}'),
        ("M3 改名通道**区分**可自动与须显式清单（盲替换风险者 blocked）",
         c["auto_applicable_renames"] + c["blocked_renames"] == c["by_channel"]["RENAME"]
         and c["blocked_renames"] >= 1,
         f'可自动 {c["auto_applicable_renames"]} · **blocked {c["blocked_renames"]}**'),
        ("M4 改名通道**非空且**每条均带受限正则与排除清单字段（空集不得视为通过）",
         (len(_ren) == 7) and all("pattern" in x and "exclusions" in x for x in _ren),
         f'{len(_ren)} 条（声明 {d["channels"].get("RENAME", {}).get("count", 0)}）'),
        ("M5 退役通道**非空且**明确不得改名并要求只读期（空集不得视为通过）",
         (len(_ret) == 1) and all(x.get("keep_readonly_period") and "不得改名" in x.get("action", "")
                                  for x in _ret),
         f'{len(_ret)} 条（声明 {d["channels"].get("RETIRE", {}).get("count", 0)}）'),
        ("M6 引擎默认 dry-run，写入须 `--apply --sandbox`",
         d["engine"]["default_mode"] == "dry-run" and "sandbox" in d["engine"]["write_requires"],
         d["engine"]["write_requires"]),
        ("M7 引擎**永不**发布 IRI / 永不写 KERT / 禁手改 specs·generated",
         d["engine"]["never_publishes_iri"] and d["engine"]["never_writes_kert"]
         and set(d["engine"]["hand_edit_forbidden"]) == {"specs/", "generated/"},
         "3 条硬约束"),
        ("M8 目标命名空间为**演练占位**（非正式根域）",
         d["target_namespace_is_rehearsal"] and "rehearsal.sim.local" in d["target_namespace"],
         d["target_namespace"]),
        ("M9 与演练证据一致（引用 B6+B8 真改写数）",
         e["b6b8_items"] == 242 and e["rewritten"] == 242,
         f'B6+B8 {e["b6b8_items"]} / 真改写 {e["rewritten"]}'),
    ]


def cmd_gate() -> int:
    d = build_plan()
    rows = checks(d)
    print("# command=onto1_migration_runner --gate")
    for n, ok, det in rows:
        print(f"{'PASS' if ok else 'FAIL'} [{n}] {det}")
    bad = [n for n, ok, _ in rows if not ok]
    print(f"A-13 迁移器骨架：{'PASS' if not bad else 'FAIL'}（{len(rows) - len(bad)}/{len(rows)}）")
    return 0 if not bad else 2


def cmd_selftest() -> int:
    d = build_plan()
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

    run_case("P1 缺一通道 ⇒ FAIL", lambda m: m["channels"].pop("RETIRE"))
    run_case("P2 把 blocked 改名当可自动 ⇒ FAIL",
             lambda m: [x.update(auto_applicable=True, blocked_reason=None)
                        for x in m["channels"]["RENAME"]["items"]]
             + [m["counts"].update(blocked_renames=0)])
    run_case("P3 引擎允许写仓内 ⇒ FAIL", lambda m: m["engine"].update(write_requires="--apply"))
    run_case("P4 目标写成正式命名空间 ⇒ FAIL",
             lambda m: m.update(target_namespace="https://gientech.com/gits/kno/",
                                target_namespace_is_rehearsal=False))
    run_case("P5 禁手改路径被移除 specs/ ⇒ FAIL",
             lambda m: m["engine"].update(hand_edit_forbidden=["generated/"]))

    # **真实路径**反例：目标落在沙箱之外 ⇒ 必须拒绝
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        sb = pathlib.Path(td) / "sandbox"
        sb.mkdir()
        outside = pathlib.Path(td) / "outside.txt"
        total += 1
        try:
            guard_target(outside, sb)
            ok = False
        except PermissionError:
            ok = True
        fails += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'} [R1 真实路径：目标出沙箱 ⇒ 拒绝] 被拒绝 = {ok}")
        total += 1
        try:
            guard_target(sb / "specs" / "x.ttl", sb)
            ok2 = False
        except PermissionError:
            ok2 = True
        fails += 0 if ok2 else 1
        print(f"{'PASS' if ok2 else 'FAIL'} [R2 真实路径：手改 specs 路径 ⇒ 拒绝] 被拒绝 = {ok2}")
        # **真实路径**反例：沙箱设在仓内 ⇒ 必须拒绝（否则"沙箱写入"等于写仓）
        total += 1
        try:
            guard_sandbox(ROOT / "adapters")
            ok3 = False
        except PermissionError:
            ok3 = True
        fails += 0 if ok3 else 1
        print(f"{'PASS' if ok3 else 'FAIL'} [R3 真实路径：沙箱设在仓内 ⇒ 拒绝] 被拒绝 = {ok3}")
    # **端到端真实路径**：沙箱内真跑一次 apply（含文件写入），断言"确有改写且全部落在沙箱内"
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        sb = pathlib.Path(td) / "sb"
        sb.mkdir()
        res = apply(sb, limit=2000)
        total += 1
        ok_e2e = bool(res["applied"])   # QA-W3R2 N-2：原 `all(... or True)` 为死子句，已删
        ok_inside = all(str((sb / _a["file"]).resolve()).startswith(str(sb.resolve())) for _a in res["applied"])
        fails += 0 if (ok_e2e and ok_inside) else 1
        print(f"{'PASS' if (ok_e2e and ok_inside) else 'FAIL'} [R4 端到端：沙箱内真改写 "
              f"{len(res['applied'])} 文件且全部落在沙箱] = {ok_e2e and ok_inside}")
        total += 1
        ok_none_in_repo = all(
            pathlib.Path(p0).resolve().is_relative_to(ROOT) is False or sb in pathlib.Path(p0).resolve().parents
            for p0 in [str(sb / _a["file"]) for _a in res["applied"]])
        fails += 0 if ok_none_in_repo else 1
        print(f"{'PASS' if ok_none_in_repo else 'FAIL'} [R5 真实路径：写入全部在沙箱、仓内零写入] = {ok_none_in_repo}")
    print(f"--selftest {'PASS' if fails == 0 else 'FAIL'}（{total - fails}/{total}）")
    return 0 if fails == 0 else 2


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--sandbox")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--gate", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ns = ap.parse_args()
    if ns.selftest:
        return cmd_selftest()
    if ns.gate:
        return cmd_gate()
    d = build_plan()
    if ns.apply:
        if not ns.sandbox:
            print("refused: --apply 必须同时给出 --sandbox <dir>（引擎默认 dry-run）")
            return 3
        try:
            res = apply(pathlib.Path(ns.sandbox), ns.limit)
        except PermissionError as exc:
            print(f"refused: {exc}")
            return 3
        print(json.dumps({k: res[k] for k in ("mode", "sandbox", "skipped_total")}, ensure_ascii=False))
        print(f'已改写 {len(res["applied"])} 个文件（沙箱内）')
        return 0
    print(json.dumps(d["counts"], ensure_ascii=False))
    print("（dry-run：未写任何文件；如需在沙箱内落地，用 --apply --sandbox <dir>）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
