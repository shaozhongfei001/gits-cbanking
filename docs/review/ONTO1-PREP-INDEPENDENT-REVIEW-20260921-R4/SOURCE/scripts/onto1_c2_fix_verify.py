#!/usr/bin/env python3
"""C-2 兼容修复 · 验收仪器（Owner 授权 2026-09-21）

验收项（缺一不可）：
  V1  两个 TTL 文件均可成功解析（rdflib）
  V2  13 个产品实例的 **IRI 集合**修复前后逐字相同（未发生实例身份迁移）
  V3  13 个实例的 rdf:type 全部解析为 T-Box 中**已声明**的 owl:Class
  V4  T-Box 内 https://gientech.com/gits/kno/Product 确为 owl:Class
  V5  原错误类 IRI（.../core#Product）**不再被任何实例引用**
  V6  未新增 owl:equivalentClass（约束 3）
  V7  前缀绑定：gits: -> T-Box 命名空间；prod: -> 既有 A-Box 命名空间

用  法：
  python3 scripts/onto1_c2_fix_verify.py --gate      # 验收（exit 0 = 全过；2 = 有 FAIL）
  python3 scripts/onto1_c2_fix_verify.py --selftest  # 4 个反例：mutate ⇒ FAIL；restore ⇒ PASS
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AFTER = ROOT / "specs/knowledge-architecture/instances/product/products.ttl"
BEFORE = ROOT / "loops/ONTO1-ontology-split/evidence/c2-before-products.ttl"
TBOX = ROOT / "specs/semantic/gits-core.owl.ttl"

NS_TBOX = "https://gientech.com/gits/kno/"
NS_ABOX = "https://gits.bank.example/ontology/core#"
IRI_PRODUCT_TBOX = NS_TBOX + "Product"
IRI_PRODUCT_WRONG = NS_ABOX + "Product"
EXPECTED_INSTANCES = 13


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8")


def _prefix_of(text: str, pfx: str) -> str | None:
    m = re.search(rf"(?m)^@prefix\s+{re.escape(pfx)}\s*:\s*<([^>]+)>", text)
    return m.group(1) if m else None


def _parse(p: Path):
    from rdflib import Graph, RDF

    g = Graph()
    g.parse(str(p), format="turtle")
    return g, RDF


def run_checks(after: Path, before: Path, tbox: Path) -> list[tuple[str, bool, str]]:
    from rdflib import RDF, OWL

    res: list[tuple[str, bool, str]] = []

    # V1 解析
    try:
        g_after, _ = _parse(after)
        g_before, _ = _parse(before)
        g_tbox, _ = _parse(tbox)
        res.append(("V1", True, f"三文件均可解析（after {len(g_after)} / before {len(g_before)} / tbox {len(g_tbox)} 三元组）"))
    except Exception as exc:  # noqa: BLE001
        res.append(("V1", False, f"解析失败：{type(exc).__name__}: {exc}"))
        return res

    typed_before = {s for s, _, _ in g_before.triples((None, RDF.type, None))}
    typed_after = {s for s, _, _ in g_after.triples((None, RDF.type, None))}

    # V2 实例 IRI 集合逐字相同
    if typed_after == typed_before and len(typed_after) == EXPECTED_INSTANCES:
        res.append(("V2", True, f"实例 IRI 集合逐字相同且 = {EXPECTED_INSTANCES} 个"))
    else:
        only_a = sorted(map(str, typed_after - typed_before))[:3]
        only_b = sorted(map(str, typed_before - typed_after))[:3]
        res.append(("V2", False, f"实例集合不一致：after={len(typed_after)} before={len(typed_before)} 新增={only_a} 丢失={only_b}"))

    # V3 类型 = T-Box 已声明的 owl:Class
    declared = {s for s in g_tbox.subjects(RDF.type, OWL.Class)}
    bad_types: list[str] = []
    for s in typed_after:
        types = set(g_after.objects(s, RDF.type))
        for t in types:
            if t not in declared:
                bad_types.append(f"{s} -> {t}")
    if typed_after and not bad_types:
        res.append(("V3", True, f"实例类型 {len(typed_after)}/{EXPECTED_INSTANCES} 全部命中 T-Box 已声明的 owl:Class"))
    else:
        res.append(("V3", False, f"存在未声明类型引用：{bad_types[:3]}"))

    # V4 T-Box 声明 Product 为 owl:Class
    ok4 = (OWL.Class is not None) and any(
        str(s) == IRI_PRODUCT_TBOX for s in g_tbox.subjects(RDF.type, OWL.Class)
    )
    res.append(("V4", ok4, f"T-Box 内 {IRI_PRODUCT_TBOX} 是 owl:Class = {ok4}"))

    # V5 原错误类 IRI 不再被实例引用
    wrong_refs = [(str(s), str(o)) for s, _, o in g_after.triples((None, RDF.type, None)) if str(o) == IRI_PRODUCT_WRONG]
    res.append(("V5", not wrong_refs, f"错误类 IRI {IRI_PRODUCT_WRONG} 被引用次数 = {len(wrong_refs)}"))

    # V6 未新增 equivalentClass
    n_eq = _read(after).count("equivalentClass") + _read(tbox).count("equivalentClass")
    res.append(("V6", n_eq == 0, f"equivalentClass 出现次数 = {n_eq}（约束 3：必须 0）"))

    # V7 前缀绑定
    p_gits = _prefix_of(_read(after), "gits")
    p_prod = _prefix_of(_read(after), "prod")
    ok7 = p_gits == NS_TBOX and p_prod == NS_ABOX
    res.append(("V7", ok7, f"gits: -> {p_gits} ；prod: -> {p_prod}"))

    return res


def cmd_gate() -> int:
    rows = run_checks(AFTER, BEFORE, TBOX)
    print("# command=onto1_c2_fix_verify --gate")
    print(f"# after={AFTER.relative_to(ROOT)}")
    print(f"# before={BEFORE.relative_to(ROOT)}")
    print(f"# tbox={TBOX.relative_to(ROOT)}")
    for cid, ok, detail in rows:
        print(f"{'PASS' if ok else 'FAIL'} [{cid}] {detail}")
    bad = [cid for cid, ok, _ in rows if not ok]
    print(f"C-2 验收：{'PASS' if not bad else 'FAIL'}（{len(rows) - len(bad)}/{len(rows)}；未过 = {bad}）")
    return 0 if not bad else 2


MUTATIONS = {
    "M1 类型改回错误类（prod:Product）": lambda t: t.replace("a gits:Product", "a prod:Product"),
    "M2 改一个实例 IRI（prod_cb_001→prod_cb_999）": lambda t: t.replace("prod:prod_cb_001", "prod:prod_cb_999", 1),
    "M3 类型改为未声明类（gits:ProductOffering）": lambda t: t.replace("a gits:Product", "a gits:ProductOffering"),
    "M4 注入 owl:equivalentClass": lambda t: t.replace(
        "@prefix rdfs:", "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n@prefix rdfs:", 1
    ).replace("prod:prod_cb_001", "prod:prod_cb_001\n  owl:equivalentClass gits:Product ;", 1),
}


def cmd_selftest() -> int:
    base = run_checks(AFTER, BEFORE, TBOX)
    base_ok = all(ok for _, ok, _ in base)
    print(f"{'PASS' if base_ok else 'FAIL'} [M0 对照] 现状 7/7 全过 = {base_ok}")
    failures = 0
    original = _read(AFTER)
    try:
        for name, mutate in MUTATIONS.items():
            with tempfile.TemporaryDirectory() as td:
                tmp = Path(td) / "products.ttl"
                tmp.write_text(mutate(original), encoding="utf-8")
                rows = run_checks(tmp, BEFORE, TBOX)
                bad = [cid for cid, ok, _ in rows if not ok]
                ok = bool(bad)
                failures += 0 if ok else 1
                print(f"{'PASS' if ok else 'FAIL'} [{name}] 被拦下的检查 = {bad or '无（漏检！）'}")
        AFTER.write_text(original, encoding="utf-8")
        restored = run_checks(AFTER, BEFORE, TBOX)
        ok_r = all(o for _, o, _ in restored)
        failures += 0 if ok_r else 1
        print(f"{'PASS' if ok_r else 'FAIL'} [M5 还原对照] 7/7 全过 = {ok_r}")
    finally:
        AFTER.write_text(original, encoding="utf-8")
    total = len(MUTATIONS) + 2
    print(f"--selftest {'PASS' if failures == 0 else 'FAIL'}（{total - failures}/{total}）")
    return 0 if failures == 0 else 2


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ns = ap.parse_args()
    if ns.selftest:
        return cmd_selftest()
    if ns.gate:
        return cmd_gate()
    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
