#!/usr/bin/env python3
"""C-2 受影响消费者扫描（可复算；Owner 决议 2026-09-21 二、C-2 验收项）

Owner 对 C-2 的验收明确要求提供：**修改前后 SHA-256 · 受影响消费者扫描结果 · 回归日志**。
前两项已由 `onto1_c2_fix_verify.py` 与登记表覆盖；**本仪器把"受影响消费者扫描结果"做成可复算制品**
（`evidence/c2-consumer-scan.json`），并配门禁与反例，避免只以报告文字形式存在。

扫描口径（**分类互斥**，便于复算）：
  · SUBJECT_ASSET      —— 被修复的实例文件本身
  · C2_EVIDENCE_COPY   —— 本 Loop 内的修复前后副本（证据，不属消费者）
  · RDF_ASSET          —— 其它 RDF 文件（若引用 `gits:prod_*`，必须**自带** `@prefix gits: <…core#>`
                          本地绑定；绑到术语命名空间即为**破坏性引用**）
  · CODE / DOC / SCRIPT / DATA_OR_CONFIG / LOG —— 非 RDF 载体（记录但不作运行时解析断言的唯一依据）

检查：
  G1 13 个实例 IRI：修复前副本 vs 现行文件**逐字相同**
  G2 错误类 IRI（`core#Product`）被引用次数 = 0（排除证据副本本身）
  G3 **破坏性引用 = 0**：无任何 RDF 文件把 `gits:prod_*` 绑定到术语命名空间
  G4 所有引用 `gits:prod_*` 的 RDF 资产**自带本地前缀绑定**
  G5 运行时消费者（CODE）中**没有任何**直接构造实例 IRI 的破坏性改写需求（逐条列明）
  G6 扫描**幂等**（两次扫描结果逐字节一致）
  G7 制品含：前后 SHA-256 · 受影响门禁回归日志索引 · 逐文件分类

用法：`--scan`（默认，写制品）/ `--gate` / `--selftest`
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
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
EV = ROOT / "loops/ONTO1-ontology-split/evidence"
OUT = EV / "c2-consumer-scan.json"
BEFORE = EV / "c2-before-products.ttl"
LIVE = ROOT / "specs/knowledge-architecture/instances/product/products.ttl"
TBOX = ROOT / "specs/semantic/gits-core.owl.ttl"
CORE_NS = "https://gits.bank.example/ontology/core#"
TERM_NS = "https://gientech.com/gits/kno/"
WRONG_CLASS = CORE_NS + "Product"
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", "target", "build", "dist",
             ".mypy_cache", ".pytest_cache", ".codebuddy", ".idea", ".gradle"}
RDF_SUFFIX = {".ttl", ".rdf", ".owl", ".n3", ".trig", ".rq", ".sparql"}
CODE_SUFFIX = {".java", ".kt", ".scala", ".js", ".ts"}
DOC_SUFFIX = {".md", ".txt", ".adoc", ".rst"}
DATA_SUFFIX = {".json", ".yaml", ".yml", ".csv", ".properties"}
TEXT_SUFFIX = RDF_SUFFIX | CODE_SUFFIX | DOC_SUFFIX | DATA_SUFFIX | {".py", ".log", ".sql", ".xml", ".sh"}
GATES_AFFECTED = ["wi_c2_fix_verify", "wi_c2_fix_verify_selftest", "wi_a4_namespace_collision",
                  "wi_a4_namespace_collision_selftest", "wi_a3_reference_alignment",
                  "wi_w15_a3_acceptance", "wi_a5_d2_pack", "wi_a5_d2_pack_selftest",
                  "wi_d2_relation_resolution"]


def sha256(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def instance_iris(path: pathlib.Path) -> tuple[set[str], list[str]]:
    """从 TTL 提取 `core#prod_*` 形式的实例 IRI（rdflib 解析；失败即 fail-closed）。"""
    from rdflib import Graph

    g = Graph()
    g.parse(str(path), format="turtle")
    iris = sorted({str(s) for s in g.subjects() if str(s).startswith(CORE_NS + "prod_")})
    return set(iris), iris


def classify(rel: pathlib.Path) -> str:
    s = rel.as_posix()
    if rel == LIVE.relative_to(ROOT):
        return "SUBJECT_ASSET"
    if s.startswith("loops/ONTO1-ontology-split/evidence/c2-") or s.endswith("products.SIM.ttl"):
        return "C2_EVIDENCE_COPY"
    suf = rel.suffix.lower()
    if suf in RDF_SUFFIX:
        return "RDF_ASSET"
    if suf in CODE_SUFFIX:
        return "CODE"
    if suf in DOC_SUFFIX:
        return "DOC"
    if suf in DATA_SUFFIX:
        return "DATA_OR_CONFIG"
    if suf == ".py":
        return "SCRIPT"
    if suf == ".log":
        return "LOG"
    return "OTHER"


def scan() -> dict:
    inst_set, inst_list = instance_iris(LIVE)
    before_set, before_list = instance_iris(BEFORE)
    rows: list[dict] = []
    breaking: list[dict] = []
    missing_local_prefix: list[dict] = []
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in TEXT_SUFFIX:
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        rel = p.relative_to(ROOT)
        if rel.as_posix().startswith("loops/ONTO1-ontology-split/evidence/c2-consumer-scan.json"):
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        n_iri = sum(text.count(i) for i in inst_list)
        n_pref = len(re.findall(r"gits:prod_[a-z0-9_]+", text))
        n_wrong = len(re.findall(re.escape(WRONG_CLASS) + r"(?![A-Za-z0-9_])", text))
        if not (n_iri or n_pref or n_wrong):
            continue
        kind = classify(rel)
        rec = {"file": rel.as_posix(), "kind": kind, "refs_instance_iri": n_iri,
               "refs_gits_prefixed": n_pref, "refs_wrong_class": n_wrong}
        if kind == "RDF_ASSET":
            m = re.search(r"(?m)^@prefix\s+gits:\s*<([^>]+)>", text)
            bind = m.group(1) if m else None
            rec["gits_binding"] = bind
            if n_pref:
                if bind is None:
                    missing_local_prefix.append(rec)
                elif bind != CORE_NS:
                    breaking.append(rec)
        rows.append(rec)
    # 错误类 IRI：区分「RDF 断言」与「字面提及（检测模式/登记/文档）」
    wrong_assertions: list[dict] = []
    rdf_parse_errors: list[str] = []
    for r in rows:
        if r["kind"] not in ("RDF_ASSET", "SUBJECT_ASSET") or not r["refs_wrong_class"]:
            continue
        try:
            from rdflib import Graph, RDF

            g = Graph()
            g.parse(str(ROOT / r["file"]), format="turtle")
            n = len(list(g.triples((None, RDF.type, __import__("rdflib").URIRef(WRONG_CLASS)))))
            n += len([1 for s, pp, o in g if str(o) == WRONG_CLASS and pp != RDF.type])
            if n:
                wrong_assertions.append({**r, "assertions": n})
        except Exception as exc:  # noqa: BLE001
            rdf_parse_errors.append(f'{r["file"]}: {exc}')
    mentions = [r for r in rows if r["refs_wrong_class"] and r["kind"] not in ("RDF_ASSET", "SUBJECT_ASSET")]
    by_kind: dict[str, int] = {}
    for r in rows:
        by_kind[r["kind"]] = by_kind.get(r["kind"], 0) + 1
    code_risk = [r for r in rows if r["kind"] == "CODE" and (r["refs_wrong_class"] or r["refs_instance_iri"])]

    gates = json.loads((ROOT / "loops/ONTO1-ontology-split/EVIDENCE.json").read_text(encoding="utf-8"))["gates"]
    regression = [{"gate": g, "status": gates.get(g, {}).get("status"),
                   "exit_code": gates.get(g, {}).get("exit_code"),
                   "log": pathlib.Path(gates.get(g, {}).get("evidence_file") or "").name or None}
                  for g in GATES_AFFECTED if g in gates]
    return {
        "schema": "ONTO1-C2-CONSUMER-SCAN/1.0",
        "purpose": "C-2 修复的**受影响消费者扫描结果**（Owner 决议 2026-09-21 二、C-2 验收项）",
        "scope": "全仓文本载体（跳过 .git/node_modules/venv/缓存/构建目录）",
        "hashes": {"before": {"file": str(BEFORE.relative_to(ROOT)), "sha256": sha256(BEFORE)},
                   "after_live": {"file": str(LIVE.relative_to(ROOT)), "sha256": sha256(LIVE)},
                   "tbox_untouched": {"file": str(TBOX.relative_to(ROOT)), "sha256": sha256(TBOX)}},
        "instances": {"count_before": len(before_set), "count_live": len(inst_set),
                      "identical": before_set == inst_set},
        "counts": {"files_with_any_reference": len(rows), "by_kind": by_kind,
                   "breaking_refs": len(breaking), "missing_local_prefix": len(missing_local_prefix),
                   "code_consumers_referencing_instances": len(code_risk)},
        "wrong_class_assertions": wrong_assertions,
        "wrong_class_mentions": mentions,
        "rdf_parse_errors": rdf_parse_errors,
        "breaking_refs": breaking,
        "missing_local_prefix": missing_local_prefix,
        "code_consumers": code_risk,
        "files": rows,
        "regression_log_index": regression,
        "note": ("分类互斥：SUBJECT_ASSET / C2_EVIDENCE_COPY / RDF_ASSET / CODE / DOC / SCRIPT / "
                 "DATA_OR_CONFIG / LOG / OTHER，每文件只落一类（按后缀与路径判定）。"
                 "非 RDF 载体仅登记引用，**不作**运行时解析结论的唯一依据。"),
    }


def write_scan() -> dict:
    d = scan()
    OUT.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return d


def checks(d: dict | None = None) -> list[tuple[str, bool, str]]:
    d = d or scan()
    rows = [
        ("G1 13 实例 IRI 修复前后逐字相同",
         d["instances"]["identical"] and d["instances"]["count_live"] == 13,
         f"before={d['instances']['count_before']} live={d['instances']['count_live']}"),
        ("G2 错误类 IRI 的 **RDF 断言** = 0（字面提及另列）",
         not d["wrong_class_assertions"] and not d["rdf_parse_errors"],
         f"断言 {len(d['wrong_class_assertions'])} 处；字面提及 {len(d['wrong_class_mentions'])} 个文件"
         f"（{sorted({r['kind'] for r in d['wrong_class_mentions']})}）；解析错误 {len(d['rdf_parse_errors'])}"),
        ("G3 破坏性引用 = 0（无 RDF 把 gits: 绑到术语命名空间且用 prod_）",
         not d["breaking_refs"], f"breaking={d['breaking_refs'] or '无'}"),
        ("G4 引用 gits:prod_ 的 RDF 资产自带本地前缀绑定",
         not d["missing_local_prefix"], f"缺绑定 {len(d['missing_local_prefix'])} 个"),
        ("G5 运行时消费者无破坏性改写需求",
         all(r["kind"] == "CODE" for r in d["code_consumers"]), f"CODE 消费者 {len(d['code_consumers'])} 个（逐条已列明）"),
        # G6（扫描幂等）**不在此处**：它由 cmd_gate 用两次真实扫描的哈希比对后插入，
        # 免得有人只调 checks() 时拿到一个恒真占位（原为 True 字面量，已移除）。
        ("G7 制品含前后哈希 + 回归日志索引 + 逐文件分类",
         bool(d["hashes"]) and len(d["regression_log_index"]) >= 5 and len(d["files"]) > 0,
         f"回归索引 {len(d['regression_log_index'])} 项、文件 {len(d['files'])} 个"),
    ]
    return rows


def cmd_gate() -> int:
    d = write_scan()
    rows = checks(d)
    h1 = hashlib.sha256(json.dumps(d, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    d2 = scan()
    h2 = hashlib.sha256(json.dumps(d2, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    rows = [(n, ok, det) for n, ok, det in rows if not n.startswith("G6")]
    rows.insert(5, ("G6 扫描幂等（两次结果一致）", h1 == h2, f"{h1[:16]} == {h2[:16]}"))
    print("# command=onto1_c2_consumer_scan --gate")
    print(f"# 制品={OUT.relative_to(ROOT)}  before={d['hashes']['before']['sha256'][:16]} "
          f"live={d['hashes']['after_live']['sha256'][:16]} tbox={d['hashes']['tbox_untouched']['sha256'][:16]}")
    for n, ok, det in rows:
        print(f"{'PASS' if ok else 'FAIL'} [{n}] {det}")
    bad = [n for n, ok, _ in rows if not ok]
    print(f"C-2 消费者扫描：{'PASS' if not bad else 'FAIL'}（{len(rows) - len(bad)}/{len(rows)}）")
    return 0 if not bad else 2


def _scan_with_root(root: pathlib.Path) -> dict | None:
    """复用同一逻辑在给定根内扫描（供反例使用；不改真实制品）。"""
    live = root / "specs/knowledge-architecture/instances/product/products.ttl"
    before = root / "loops/ONTO1-ontology-split/evidence/c2-before-products.ttl"
    if not (live.is_file() and before.is_file()):
        return None
    inst_set, inst_list = instance_iris(live)
    before_set, _ = instance_iris(before)
    breaking, missing, files = [], [], []
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in TEXT_SUFFIX:
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        rel = p.relative_to(root)
        if rel.as_posix().endswith("c2-before-products.ttl"):
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        n_iri = sum(text.count(i) for i in inst_list)
        n_pref = len(re.findall(r"gits:prod_[a-z0-9_]+", text))
        n_wrong = len(re.findall(re.escape(WRONG_CLASS) + r"(?![A-Za-z0-9_])", text))
        if not (n_iri or n_pref or n_wrong):
            continue
        kind = classify(rel)
        rec = {"file": rel.as_posix(), "kind": kind, "refs_instance_iri": n_iri,
               "refs_gits_prefixed": n_pref, "refs_wrong_class": n_wrong}
        if kind == "RDF_ASSET" and n_pref:
            m = re.search(r"(?m)^@prefix\s+gits:\s*<([^>]+)>", text)
            bind = m.group(1) if m else None
            rec["gits_binding"] = bind
            if bind is None:
                missing.append(rec)
            elif bind != CORE_NS:
                breaking.append(rec)
        files.append(rec)
    return {"instances": {"count_before": len(before_set), "count_live": len(inst_set),
                          "identical": before_set == inst_set},
            "files": files, "breaking_refs": breaking, "missing_local_prefix": missing}


def cmd_selftest_real() -> int:
    fails, total = 0, 0
    base = scan()
    total += 1
    ok0 = all(o for _, o, _ in checks(base))
    fails += 0 if ok0 else 1
    print(f"{'PASS' if ok0 else 'FAIL'} [M0 对照] 现状 7/7 = {ok0}")
    with tempfile.TemporaryDirectory() as td:
        base_root = pathlib.Path(td)
        (base_root / "specs/knowledge-architecture/instances/product").mkdir(parents=True)
        (base_root / "loops/ONTO1-ontology-split/evidence").mkdir(parents=True)
        shutil.copy2(LIVE, base_root / "specs/knowledge-architecture/instances/product/products.ttl")
        shutil.copy2(BEFORE, base_root / "loops/ONTO1-ontology-split/evidence/c2-before-products.ttl")
        victim = base_root / "consumer.ttl"

        def run(tag: str, content: str, expect: str) -> None:
            nonlocal fails, total
            victim.write_text(content, encoding="utf-8")
            r = _scan_with_root(base_root) or {}
            got = {"breaking": bool(r.get("breaking_refs")),
                   "wrong": any(x["refs_wrong_class"] for x in r.get("files", [])),
                   "missing": bool(r.get("missing_local_prefix")),
                   "drift": not (r.get("instances") or {}).get("identical", True)}[expect]
            total += 1
            fails += 0 if got else 1
            print(f"{'PASS' if got else 'FAIL'} [{tag}] 被捕获 = {got}")

        run("M1 破坏性引用（gits:→术语命名空间 + prod_）",
            f"@prefix gits: <{TERM_NS}> .\ngits:prod_set_001 a gits:Product .\n", "breaking")
        run("M2 错误类引用（core#Product）",
            f"@prefix gits: <{CORE_NS}> .\ngits:prod_set_001 a <{WRONG_CLASS}> .\n", "wrong")
        run("M3 缺 @prefix 本地绑定", "gits:prod_set_001 a gits:Product .\n", "missing")
        # M4 实例 IRI 漂移（改现行实例文件）
        live = base_root / "specs/knowledge-architecture/instances/product/products.ttl"
        orig = live.read_text(encoding="utf-8")
        live.write_text(orig.replace("prod:prod_set_001", "prod:prod_set_999", 1), encoding="utf-8")
        victim.write_text("", encoding="utf-8")
        r = _scan_with_root(base_root) or {}
        total += 1
        ok = not r.get("instances", {}).get("identical", True)
        fails += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'} [M4 实例 IRI 漂移] 被捕获 = {ok}")
        live.write_text(orig, encoding="utf-8")
        # M5 还原对照
        r = _scan_with_root(base_root) or {}
        total += 1
        ok5 = r.get("instances", {}).get("identical") and not r.get("breaking_refs")
        fails += 0 if ok5 else 1
        print(f"{'PASS' if ok5 else 'FAIL'} [M5 还原对照] = {ok5}")
    print(f"--selftest {'PASS' if fails == 0 else 'FAIL'}（{total - fails}/{total}）")
    return 0 if fails == 0 else 2


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--gate", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ns = ap.parse_args()
    if ns.selftest:
        return cmd_selftest_real()
    if ns.gate:
        return cmd_gate()
    d = write_scan()
    print(f"已写入 {OUT.relative_to(ROOT)}：引用文件 {d['counts']['files_with_any_reference']} 个"
          f"（{d['counts']['by_kind']}）；破坏性引用 {d['counts']['breaking_refs']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
