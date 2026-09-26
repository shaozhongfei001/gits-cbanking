#!/usr/bin/env python3
"""C-2 生成器根因检查（Owner 授权跨 GK17 限定整改，2026-09-21）

背景：只修生成物不修生成器 ⇒ 根因未关闭（C-2 记 `CONDITIONALLY_CLOSED`）。本检查器验证
`scripts/gk17_prodcard_to_rdf.py` **在配置驱动下**重新生成 `products.ttl` 时：

  G1 连续两次生成**字节级一致**（幂等）
  G2 13 个产品个体使用 `prod:` 前缀，类型为已声明的 `gits:Product`
  G3 命名空间分离：`gits:` → 术语命名空间、`prod:` → 实例命名空间（均来自配置）
  G4 错误的类引用 `core#Product` = 0
  G5 **不得**生成 `owl:equivalentClass`
  G6 13 个实例 IRI 与修复前基线**逐字一致**（未发生实例身份迁移）
  G7 配置缺失 ⇒ fail-closed（退出码 3，不得静默沿用旧口径）

用法：--gate / --selftest（4 反例：命名空间对调 / productType 指向错误类 / 去掉 prod 前缀 / 配置缺失）
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GEN = ROOT / "scripts/gk17_prodcard_to_rdf.py"
CONFIG = ROOT / "specs/knowledge-architecture/instances/product/projection-config.json"
BASE = ROOT / "loops/ONTO1-ontology-split/evidence/c2-before-products.ttl"
CARDS = Path("/home/szf/dev/Leibniz-KERT/examples/product-recommendation-assets/03_core")
NS_TERMS = "https://gientech.com/gits/kno/"
NS_INST = "https://gits.bank.example/ontology/core#"


def _generate(out_dir: Path, config: Path) -> tuple[int, str]:
    r = subprocess.run(
        [sys.executable, str(GEN), "--root", str(ROOT), "--cards-dir", str(CARDS),
         "--out-dir", str(out_dir), "--allow-unresolved", "--config", str(config)],
        cwd=ROOT, text=True, capture_output=True)
    return r.returncode, (r.stdout + r.stderr)


def _instances(text: str) -> set[str]:
    return set(re.findall(r"(?m)^prod:(prod_[a-z0-9_]+)$", text))


def run_checks(tmp: Path, config: Path) -> list[tuple[str, bool, str]]:
    rows: list[tuple[str, bool, str]] = []
    d1, d2 = tmp / "g1", tmp / "g2"
    rc1, out1 = _generate(d1, config)
    rc2, out2 = _generate(d2, config)
    if rc1 != 0 or rc2 != 0:
        rows.append(("G0", False, f"生成失败 rc1={rc1} rc2={rc2}：{out1.strip()[:160]}"))
        return rows
    t1 = (d1 / "products.ttl").read_text(encoding="utf-8")
    t2 = (d2 / "products.ttl").read_text(encoding="utf-8")
    h1, h2 = hashlib.sha256(t1.encode()).hexdigest(), hashlib.sha256(t2.encode()).hexdigest()

    rows.append(("G1", h1 == h2, f"连续两次字节一致={h1 == h2} sha256={h1[:16]}"))
    inst = _instances(t1)
    n_type = len(re.findall(r"a gits:Product ;", t1))
    rows.append(("G2", len(inst) == 13 and n_type == 13, f"prod: 个体={len(inst)} 类型断言={n_type}（应为 13/13）"))
    p_gits = re.search(r"(?m)^@prefix gits:\s*<([^>]+)>", t1)
    p_prod = re.search(r"(?m)^@prefix prod:\s*<([^>]+)>", t1)
    ok3 = bool(p_gits and p_prod) and p_gits.group(1) == NS_TERMS and p_prod.group(1) == NS_INST
    rows.append(("G3", ok3, f"gits:→{(p_gits.group(1) if p_gits else None)} ；prod:→{(p_prod.group(1) if p_prod else None)}"))
    wrong = len(re.findall(r"core#Product\b|prod:Product\b", t1))
    rows.append(("G4", wrong == 0, f"错误类引用 = {wrong}"))
    eq = t1.count("equivalentClass")
    rows.append(("G5", eq == 0, f"equivalentClass = {eq}"))
    try:
        from rdflib import Graph

        base_i = {str(s) for s in Graph().parse(str(BASE), format="turtle").subjects()}
        new_i = set()
        for name in sorted(inst):
            new_i.add(NS_INST + name)
        same = new_i == base_i and len(new_i) == 13
    except Exception as exc:  # noqa: BLE001
        same, exc_msg = False, str(exc)
        rows.append(("G6", False, f"基线比对失败：{exc_msg[:120]}"))
    else:
        rows.append(("G6", same, f"实例 IRI 与修复前基线逐字一致={same}（{len(inst)} 个）"))

    missing = tmp / "no-config.json"
    rc3, _ = _generate(tmp / "g3", missing)
    rows.append(("G7", rc3 == 3, f"配置缺失 ⇒ exit={rc3}（应 3 = fail-closed）"))
    return rows


def cmd_gate() -> int:
    with tempfile.TemporaryDirectory() as td:
        rows = run_checks(Path(td), CONFIG)
    print("# command=onto1_c2_generator_check --gate")
    print(f"# generator={GEN.relative_to(ROOT)}  config={CONFIG.relative_to(ROOT)}")
    for cid, ok, d in rows:
        print(f"{'PASS' if ok else 'FAIL'} [{cid}] {d}")
    bad = [c for c, ok, _ in rows if not ok]
    print(f"C-2 生成器根因：{'CLOSED' if not bad else 'STILL OPEN'}（{len(rows) - len(bad)}/{len(rows)}；未过={bad}）")
    return 0 if not bad else 2


def _mutants() -> dict:
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))

    def m1(c):
        c = copy.deepcopy(c)
        c["namespaces"]["terms"]["iri"], c["namespaces"]["instances"]["iri"] = (
            c["namespaces"]["instances"]["iri"], c["namespaces"]["terms"]["iri"])
        return c

    def m2(c):
        c = copy.deepcopy(c)
        c["productType"] = "prod:Product"
        return c

    def m3(c):
        c = copy.deepcopy(c)
        c["namespaces"]["instances"]["prefix"] = "gits"  # 前缀塌回一个 ⇒ 分离失效
        return c

    return {"M1 两个命名空间对调": m1, "M2 productType 指向错误类": m2, "M3 实例前缀塌回 gits": m3}


def cmd_selftest() -> int:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        base = run_checks(td / "base", CONFIG)
        ok0 = all(o for _, o, _ in base)
        print(f"{'PASS' if ok0 else 'FAIL'} [M0 对照] 现状 7/7 = {ok0}")
        fails = 0 if ok0 else 1
        for name, mutate in _mutants().items():
            cfg = td / f"{abs(hash(name)) % 10000}.json"
            cfg.write_text(json.dumps(mutate(json.loads(CONFIG.read_text(encoding="utf-8"))),
                                      ensure_ascii=False), encoding="utf-8")
            rows = run_checks(td / f"m{abs(hash(name)) % 10000}", cfg)
            bad = [c for c, ok, _ in rows if not ok]
            good = bool(bad)
            fails += 0 if good else 1
            print(f"{'PASS' if good else 'FAIL'} [{name}] 被拦下 = {bad or '无（漏检！）'}")
    total = 4
    print(f"--selftest {'PASS' if fails == 0 else 'FAIL'}（{total - fails}/{total}）")
    return 0 if fails == 0 else 2


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
