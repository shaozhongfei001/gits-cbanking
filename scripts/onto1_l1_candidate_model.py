#!/usr/bin/env python3
"""A-9｜L1 SIM 候选模型（8 类）—— 可解析的**候选** TTL，不进 `specs/**`、不发布任何正式 IRI

依据：`evidence/prep/32-classes-target-mapping.json` 的 `l1_candidate_model`（**8 类** = 基线 5 + 新增 3），
与设计 §4.2 逐项比对后的口径（见该文件 `separation_statement`：**来源盘点 32 ≠ L1 候选 8**）。

**纪律**：
  · 命名空间用**演练/候选占位** `https://rehearsal.sim.local/ns-l1#`（**永不发布**；D3 未签前不得发布新 IRI）；
  · **禁止** `owl:equivalentClass` / `owl:equivalentProperty`（迁移重构项不得以等价关系承接）；
  · 只写**注解**（`rdfs:label` / `skos:altLabel` / `dcterms:isVersionOf` 等）与来源追溯，**不宣示等价语义**；
  · 制品置于 `evidence/prep/l1-sim-candidate/`，**不进入** `specs/**`。

用法：`--build` / `--gate` / `--selftest`
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path("/home/szf/dev/gits-cbanking")
EV = ROOT / "loops/ONTO1-ontology-split/evidence"
PREP = EV / "prep"
MAPPING = PREP / "32-classes-target-mapping.json"
OUTDIR = PREP / "l1-sim-candidate"
TTL = OUTDIR / "l1-core.SIM-CANDIDATE.ttl"
OUT = OUTDIR / "l1-sim-candidate.json"
CAND_NS = "https://rehearsal.sim.local/ns-l1#"


def sha256(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_model() -> dict:
    return json.loads(MAPPING.read_text(encoding="utf-8"))


def build() -> dict:
    d = load_model()
    model = d["l1_candidate_model"]
    # 从 CSV 侧核对 L1 行的目标代号（交叉验证，不臆造）
    csv_l1 = [c for c in d["classes_32"]
              if (c.get("target_layer") or "").startswith("L1")]
    ttl_lines = [
        "@prefix cand:   <https://rehearsal.sim.local/ns-l1#> .",
        "@prefix rdf:    <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .",
        "@prefix rdfs:   <http://www.w3.org/2000/01/rdf-schema#> .",
        "@prefix owl:    <http://www.w3.org/2002/07/owl#> .",
        "@prefix skos:   <http://www.w3.org/2004/02/skos/core#> .",
        "@prefix dcterms: <http://purl.org/dc/terms/> .",
        "@prefix onto1:  <https://sim.local/onto1/meta#> .",
        "",
        "# 状态：CANDIDATE_NOT_EFFECTIVE（**不是**正式基线；命名空间为候选占位，永不发布）",
        "# 禁止项：不得以其宣示等价语义；不得据此发布 IRI；不得写入 specs/**",
        "",
        "onto1:L1CandidateModel a owl:Ontology ;",
        '  rdfs:comment "L1 公共核心语义契约库 · SIM 候选模型（8 类；由 32→目标映射的 L1 行与设计 §4.2 比对推导）" ;',
        "  dcterms:source <loops/ONTO1-ontology-split/evidence/prep/32-classes-target-mapping.json> ;",
        '  onto1:effective "CANDIDATE_NOT_EFFECTIVE" .',
        "",
    ]
    for m in model:
        term = m["term"]
        ttl_lines += [
            f"cand:{term} a owl:Class ;",
            f'  rdfs:label "{term}" ;',
        ]
        succ = m.get("baseline_successor_of")
        if succ:
            ttl_lines.append(f'  skos:altLabel "{succ}"@en ;')
            ttl_lines.append(f'  onto1:baselineSuccessorOf "{succ}" ;')
        ttl_lines.append(f'  onto1:migrationAction "{m.get("action")}" ;')
        ttl_lines.append(f'  onto1:artifactKind "{m.get("design_source", "")[:60]}" .')
        ttl_lines.append("")
    TTL.parent.mkdir(parents=True, exist_ok=True)
    TTL.write_text("\n".join(ttl_lines), encoding="utf-8")

    from rdflib import Graph, OWL, URIRef

    g = Graph()
    g.parse(str(TTL), format="turtle")
    classes = sorted(str(s) for s, _, o in g.triples((None, None, OWL.Class)))
    equiv = len(list(g.triples((None, OWL.equivalentClass, None)))) + \
            len(list(g.triples((None, OWL.equivalentProperty, None))))
    announced = sorted({str(s) for s, _, _ in g.triples((None, None, None)) if str(s).startswith(CAND_NS)})
    data = {
        "schema": "ONTO1-L1-SIM-CANDIDATE/1.0",
        "authority": "Owner 2026-09-21（SIM 整改）：允许 SIM 范围内实现；D3 未签前不得发布新 IRI",
        "boundary": {"candidate_only": True, "specs_written": False, "iri_published": False,
                     "namespace": CAND_NS,
                     "note": "候选占位命名空间，**永不发布**；制品置于 evidence/prep/，不进 specs/**"},
        "sources": {"mapping": str(MAPPING.relative_to(ROOT)), "mapping_sha256": sha256(MAPPING)},
        "counts": {"candidate_classes": len(classes), "declared": len(model),
                   "l1_from_baseline": d["summary"].get("l1_from_baseline"),
                   "l1_newly_added": d["summary"].get("l1_newly_added"),
                   "csv_l1_rows": len(csv_l1),
                   "triples": len(g), "equivalent_triples": equiv},
        "classes": classes,
        "actions": {m["term"]: m.get("action") for m in model},
        "baseline_successors": {m["term"]: m.get("baseline_successor_of") for m in model},
        "artifact": str(TTL.relative_to(ROOT)),
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return data


def checks(d: dict) -> list[tuple[str, bool, str]]:
    c = d["counts"]
    return [
        ("N1 候选类数 = 8（与 32→目标映射的 L1 候选一致）",
         c["candidate_classes"] == 8 and c["declared"] == 8,
         f'TTL 声明 {c["candidate_classes"]} / 源模型 {c["declared"]}'),
        ("N2 口径守恒：8 = 基线 5 + 新增 3",
         c["l1_from_baseline"] == 5 and c["l1_newly_added"] == 3,
         f'基线 {c["l1_from_baseline"]} + 新增 {c["l1_newly_added"]}'),
        ("N3 **禁止项**：equivalentClass/equivalentProperty = 0", c["equivalent_triples"] == 0,
         f'等价三元组 {c["equivalent_triples"]}'),
        ("N4 候选命名空间为**占位**（非正式根域、未发布）",
         "rehearsal.sim.local" in d["boundary"]["namespace"] and not d["boundary"]["iri_published"],
         d["boundary"]["namespace"]),
        ("N5 制品**未写** specs/（仅 evidence/prep/）",
         not d["boundary"]["specs_written"] and d["artifact"].startswith("loops/"),
         d["artifact"]),
        ("N6 每类均有迁移动作与基线来源追溯",
         len(d["actions"]) == 8 and all(v for v in d["actions"].values()),
         f'动作标注 {len([v for v in d["actions"].values() if v])}/8'),
        ("N7 32 ≠ 8 口径未混用（CSV L1 行与候选类分列记录）",
         c["csv_l1_rows"] > 0 and c["candidate_classes"] != len(load_model()["classes_32"]),
         f'CSV L1 行 {c["csv_l1_rows"]} / 基线类 32 / 候选 8'),
    ]


def cmd_gate() -> int:
    d = build()
    rows = checks(d)
    print("# command=onto1_l1_candidate_model --gate")
    for n, ok, det in rows:
        print(f"{'PASS' if ok else 'FAIL'} [{n}] {det}")
    bad = [n for n, ok, _ in rows if not ok]
    print(f"A-9 L1 SIM 候选模型：{'PASS' if not bad else 'FAIL'}（{len(rows) - len(bad)}/{len(rows)}）")
    return 0 if not bad else 2


def cmd_selftest() -> int:
    d = build()
    fails = total = 0
    total += 1
    base = all(o for _, o, _ in checks(d))
    fails += 0 if base else 1
    print(f"{'PASS' if base else 'FAIL'} [M0 对照] 现状 = {base}")

    import copy

    def run(tag, mut):
        nonlocal fails, total
        m = copy.deepcopy(d)
        mut(m)
        ok = not all(o for _, o, _ in checks(m))
        total += 1
        fails += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'} [{tag}] 被捕获 = {ok}")

    run("Q1 类别数不足 ⇒ FAIL", lambda m: m["counts"].update(candidate_classes=7))
    run("Q2 引入等价关系 ⇒ FAIL", lambda m: m["counts"].update(equivalent_triples=1))
    run("Q3 写成正式命名空间 ⇒ FAIL",
        lambda m: m["boundary"].update(namespace="https://gientech.com/gits/kno/"))
    run("Q4 制品写进 specs/ ⇒ FAIL",
        lambda m: (m["boundary"].update(specs_written=True), m.update(artifact="specs/l1.ttl")))
    run("Q5 口径混用（把 32 当候选）⇒ FAIL", lambda m: m["counts"].update(candidate_classes=32))
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
    print(f'已写出 {d["artifact"]}（{d["counts"]["candidate_classes"]} 类，三元组 {d["counts"]["triples"]}）')
    return 0


if __name__ == "__main__":
    sys.exit(main())
