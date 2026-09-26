#!/usr/bin/env python3
"""A-5（L3 部分）｜运行本体加载夹具（SIM 通道，只读）

目的：在不触碰正式基线的前提下，验证"SIM 通道能否**完整加载**修复后的 A-Box + 术语层并保持一致"。
Owner 允许「SIM 范围内的后续实现」；D3 临时口径 `PROVISIONAL_SIM_LEGACY_NAMESPACE` 允许继续使用两命名空间。

夹具断言（全部只读，不写任何 `specs/**`）：
  L1 三个制品均可解析（T-Box / 实例 A-Box / SIM 关系投影）；
  L2 13 个产品实例的类型**命中 T-Box 已声明类**（无孤儿实例）；
  L3 SIM 投影 **30** 条关系（Owner 2026-09-22 裁定后）的**两端均在本体/实例层可解析**（无悬空）；
  L4 SIM 投影**不含**任何隔离别名（12 关系对应的 7 个别名）；
  L5 两次加载的**规范化图哈希一致**（可复算、幂等）；
  L6 边界：未发布新 IRI、未写 specs（由 A-4 装置与本夹具共同声明）。

用法：`--gate` / `--selftest`
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path("/home/szf/dev/gits-cbanking")
TBOX = ROOT / "specs/semantic/gits-core.owl.ttl"
ABOX = ROOT / "specs/knowledge-architecture/instances/product/products.ttl"
SIM = ROOT / "specs/knowledge-architecture/instances/product/sim/product-relations.SIM.ttl"
CONFIG_L3 = ROOT / "specs/knowledge-architecture/instances/product/projection-config.json"
REG = ROOT / "loops/ONTO1-ontology-split/evidence/product-alias-resolution.json"
KERT_PROP = ROOT / "loops/ONTO1-ontology-split/evidence/prep/kert-change-proposal.json"
L2_PLAN = ROOT / "loops/ONTO1-ontology-split/evidence/prep/L2-KERT-PATCH-PLAN.md"
CORE_NS = "https://gits.bank.example/ontology/core#"


def load_all() -> tuple:
    from rdflib import Graph, URIRef

    tbox, abox, sim = Graph(), Graph(), Graph()
    tbox.parse(str(TBOX), format="turtle")
    abox.parse(str(ABOX), format="turtle")
    sim.parse(str(SIM), format="turtle")
    declared = {str(o) for s, p, o in tbox.triples((None, None, None))
                if str(p).endswith("#type") or str(o).endswith(("Class", "ObjectProperty", "DatatypeProperty"))}
    declared_classes = {str(s) for s, _, o in tbox.triples((None, None, None))
                        if "Class" in str(o) and str(s).startswith("https://")}
    declared_classes |= {str(o) for _, _, o in tbox.triples((None, None, None))
                         if str(o).startswith("https://gientech.com/gits/kno/")}
    return tbox, abox, sim, declared_classes, URIRef


def canonical_hash(g) -> str:
    """规范化哈希：**排除含空节点的三元组**（溯源语句的 bnode 标识在每次解析中不同，
    不排除会导致"同图不同哈希"的假失败；被排除项数单独计数以便审计）。"""
    from rdflib import BNode

    triples, skipped = [], 0
    for s, p, o in g:
        if isinstance(s, BNode) or isinstance(o, BNode):
            skipped += 1
            continue
        triples.append(f"{s} {p} {o}")
    payload = "\n".join(sorted(triples)) + f"\n#bnode_skipped={skipped}"
    return hashlib.sha256(payload.encode()).hexdigest()


def boundary_probe(extra_files: list[pathlib.Path] | None = None) -> dict:
    """F-2 修正：边界由**实际探测**派生（禁止文件存在性 + SIM 目录规模），不再写死布尔值。"""
    forbidden = [ROOT / "namespaces.json", ROOT / "specs/knowledge-architecture/namespaces.json"]
    forbidden += list(extra_files or [])
    present = [str(f) for f in forbidden if pathlib.Path(f).is_file()]
    sim_dir = SIM.parent          # SIM 是文件路径；其父目录才是 SIM 通道输出面
    sim_files = [f.name for f in sim_dir.rglob("*") if f.is_file()] if sim_dir.is_dir() else []
    return {"probe_files": [str(f) for f in forbidden], "forbidden_present": present,
            "sim_dir_files": sim_files, "derived_ok": not present and len(sim_files) == 1,
            "declaration_only": "SIM 通道标识来自制品自声明（**声明项，不构成验证**）"}


def inspect() -> dict:
    tbox, abox, sim, declared_classes, URIRef = load_all()
    RDF_TYPE = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"

    instances = sorted({str(s) for s in abox.subjects() if str(s).startswith(CORE_NS + "prod_")})
    typed = {}
    orphans = []
    for i in instances:
        types = [str(o) for o in abox.objects(URIRef(i), URIRef(RDF_TYPE))]
        typed[i] = types
        if not types or not any(t in declared_classes for t in types):
            orphans.append(i)

    rel_triples = [(str(s), str(p), str(o)) for s, p, o in sim
                   if str(s).startswith(CORE_NS) and str(o).startswith(CORE_NS)]
    unresolved = []
    known = set(instances) | declared_classes
    for s, p, o in rel_triples:
        if s not in known or o not in known:
            unresolved.append(f"{s} {p} {o}")

    # OA-W3R3/口径传播修复：状态源改为**版本化配置**（`projection-config.json`），
    # 并检「待补 ∪ 作废 ∪ 隔离」——只检 `quarantinedAliases` 会在其清空后恒绿（空转）。
    # 依据：配置自带的 `quarantineRule`（"空集本身不构成通过依据：泄漏检查须并检"）。
    cfg = json.loads(CONFIG_L3.read_text(encoding="utf-8"))
    pend, void, quar = (set(cfg.get("pendingProductCards", {})),
                        set(cfg.get("voidReferences", {})),
                        set(cfg.get("quarantinedAliases", {})))
    watch = pend | void | quar
    sim_text = SIM.read_text(encoding="utf-8")
    leaked = sorted(a for a in watch if a in sim_text)

    h1 = canonical_hash(sim)
    h2 = canonical_hash(load_all()[2])
    # F-10 修正：L1 由**实际解析结果**派生（原为写死 True）
    parse_counts = {"tbox": len(tbox), "abox": len(abox), "sim": len(sim)}
    return {
        "parse": {"ok": all(v > 0 for v in parse_counts.values()), **parse_counts},
        "counts": {"instances": len(instances), "orphan_instances": len(orphans),
                   "sim_relations": len(rel_triples), "unresolved_relations": len(unresolved),
                   "declared_classes": len(declared_classes), "quarantine_leak": len(leaked),
                   "watch_aliases": len(watch), "watch_breakdown": {"pending": len(pend),
                                                                   "void": len(void),
                                                                   "quarantine": len(quar)}},
        "orphan_instances": orphans[:5],
        "unresolved_relations": unresolved[:5],
        "quarantine_leak": leaked[:5],
        "graph_hash": h1, "graph_hash_idempotent": h1 == h2,
        "boundary": boundary_probe(),
    }


def checks(d: dict) -> list[tuple[str, bool, str]]:
    c = d["counts"]
    return [
        ("L1 三制品均可解析（**由实际三元组数派生**）",
         bool(d.get("parse", {}).get("ok")),
         f'三元组 T-Box={d.get("parse", {}).get("tbox")} A-Box={d.get("parse", {}).get("abox")} '
         f'SIM={d.get("parse", {}).get("sim")}'),
        ("L2 13 个产品实例类型命中 T-Box 已声明类（0 孤儿）",
         c["instances"] == 13 and c["orphan_instances"] == 0,
         f'实例 {c["instances"]} / 孤儿 {c["orphan_instances"]}'),
        ("L3 SIM 投影 **30** 条关系两端可解析（0 悬空）",
         c["sim_relations"] == 30 and c["unresolved_relations"] == 0,
         f'关系 {c["sim_relations"]} / 悬空 {c["unresolved_relations"]}'),
        ("L4 SIM 投影不含**待补∪作废∪隔离**别名（三类并检；并集为空按空转判 FAIL）",
         c["watch_aliases"] > 0 and c["quarantine_leak"] == 0,
         f'并检 {c["watch_aliases"]} 个别名 {c.get("watch_breakdown")}；'
         f'越界={d["quarantine_leak"] or "无"}；'
         f'{"**空转 ⇒ 不得给绿**" if c["watch_aliases"] == 0 else "非空转 OK"}'),
        ("L5 两次加载规范化图哈希一致（幂等可复算）",
         d["graph_hash_idempotent"], f'hash={d["graph_hash"][:16]}'),
        ("L6 边界**派生**探测（禁止文件不存在 + SIM 目录规模符合预期）",
         d["boundary"]["derived_ok"] and bool(d["boundary"]["probe_files"]),
         f'禁止文件命中={d["boundary"]["forbidden_present"] or "无"}；SIM 目录={d["boundary"]["sim_dir_files"]}'),
    ]


def cmd_gate() -> int:
    d = inspect()
    rows = checks(d)
    print("# command=onto1_l3_load_fixture --gate")
    for n, ok, det in rows:
        print(f"{'PASS' if ok else 'FAIL'} [{n}] {det}")
    bad = [n for n, ok, _ in rows if not ok]
    print(f"A-5/L3 加载夹具：{'PASS' if not bad else 'FAIL'}（{len(rows) - len(bad)}/{len(rows)}）")
    return 0 if not bad else 2


def cmd_selftest() -> int:
    d = inspect()
    fails = total = 0

    def run(tag, mut):
        nonlocal fails, total
        import copy
        m = copy.deepcopy(d)
        mut(m)
        ok = not all(o for _, o, _ in checks(m))
        total += 1
        fails += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'} [{tag}] 被捕获 = {ok}")

    total += 1
    base = all(o for _, o, _ in checks(d))
    fails += 0 if base else 1
    print(f"{'PASS' if base else 'FAIL'} [M0 对照] 现状 = {base}")
    run("P1 实例类型变孤儿 ⇒ FAIL", lambda m: m["counts"].update(orphan_instances=1))
    run("P2 关系悬空 ⇒ FAIL", lambda m: m["counts"].update(unresolved_relations=1))
    run("P3 隔离别名泄入 SIM ⇒ FAIL", lambda m: m["counts"].update(quarantine_leak=1))
    run("P4 非幂等（两次哈希不同）⇒ FAIL", lambda m: m.update(graph_hash_idempotent=False))
    run("P5 边界派生值被破坏 ⇒ FAIL", lambda m: m["boundary"].update(derived_ok=False))
    # **真实路径**反例：实际创建被禁止的 namespaces.json ⇒ 探测必须失败（QA F-2：内存变异不足以证明真实路径有判别力）
    import tempfile as _tf
    with _tf.TemporaryDirectory() as _td:
        _p = pathlib.Path(_td) / "namespaces.json"
        _p.write_text("{}", encoding="utf-8")
        _probe = boundary_probe(extra_files=[_p])
        total += 1
        _ok = bool(_probe["forbidden_present"]) and not _probe["derived_ok"]
        fails += 0 if _ok else 1
        print(f"{'PASS' if _ok else 'FAIL'} [P6 真实路径：根域文件存在 ⇒ 探测失败] = {_ok}")
    print(f"--selftest {'PASS' if fails == 0 else 'FAIL'}（{total - fails}/{total}）")
    return 0 if fails == 0 else 2


def plan_build() -> dict:
    """由 KERT 候选方案 JSON **派生** L2 补丁方案文档（不手写、可复算）。"""
    d = json.loads(KERT_PROP.read_text(encoding="utf-8"))
    lines = ["# L2｜KERT 元模型适配补丁方案（候选材料）", "",
             f"> 状态：`{d.get('status')}`｜依据：`{d.get('authority')}`｜"
             f"**本方案不涉及任何写入**，合入权在 KERT 维护方", "",
             "## 1. 义务规模（只读统计）", ""]
    ko = d.get("kert_obligations", {})
    lines += [f"- 总义务：**{ko.get('total')}**", ""]
    for area, n in (ko.get("by_area") or {}).items():
        lines.append(f"  - `{area}`：{n}")
    for wave, n in (ko.get("by_wave") or {}).items():
        lines.append(f"  - {wave}：{n}")
    lines += ["", "## 2. 候选变更（逐条含依据与前置）", "",
              "| # | 目标 | 变更 | 依据 | 所需前置 |", "|---|---|---|---|---|"]
    for i, c in enumerate(d.get("candidate_changes", []), 1):
        lines.append(f"| {i} | `{c.get('target')}` | {c.get('change')} | {c.get('basis')} | {c.get('needs')} |")
    lines += ["", "## 3. 验证材料", ""]
    for v in (d.get("verification_materials") or []):
        lines.append(f"- {v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)}")
    lines += ["", "## 4. 阻塞与写入声明", "", f"- 阻塞：`{d.get('blocked_by')}`",
              f"- 写入声明：{json.dumps(d.get('no_write_declaration', {}), ensure_ascii=False)}", "",
              "## 5. 边界（不得越过）", "",
              "- **不得**写入 KERT 仓（本环境只读）；",
              "- **不得**发布新 IRI（D3 未签）；",
              "- 合入须由 **KERT 维护方**执行，并**校验先于产出**。", ""]
    L2_PLAN.write_text("\n".join(lines), encoding="utf-8")
    return {"plan": str(L2_PLAN.relative_to(ROOT)), "targets": [c.get("target") for c in d.get("candidate_changes", [])],
            "candidates": len(d.get("candidate_changes", [])), "blocked_by": d.get("blocked_by"),
            "no_write": bool(d.get("no_write_declaration"))}


def plan_rows_for(target: pathlib.Path, info: dict | None = None) -> list[tuple[str, bool, str]]:
    info = info or plan_build()
    txt = target.read_text(encoding="utf-8")
    rows = [
        ("P1 补丁方案已生成（由 JSON 派生，含全部候选变更）",
         all(t in txt for t in info["targets"]) and info["candidates"] > 0,
         f'候选 {info["candidates"]} 条；目标 {info["targets"]}'),
        ("P2 方案明确前置（blocked_by / KERT 写权限）",
         bool(info["blocked_by"]) and "KERT 维护方" in txt, f'blocked_by={str(info["blocked_by"])[:40]}'),
        ("P3 方案声明**不写入 KERT** 且合入权在维护方",
         info["no_write"] and "不涉及任何写入" in txt and "不得**写入 KERT" in txt, "已声明"),
        ("P4 边界表述齐备（**要求两项同时出现**：不发布新 IRI + 校验先于产出）",
         ("发布新 IRI" in txt) and ("校验先于产出" in txt),
         f'含"发布新 IRI"={"发布新 IRI" in txt} 含"校验先于产出"={"校验先于产出" in txt}'),
    ]
    return rows


def plan_gate(path: pathlib.Path | None = None) -> int:
    rows = plan_rows_for(path or L2_PLAN)
    print("# command=onto1_l3_load_fixture --plan-gate")
    for n, ok, det in rows:
        print(f"{'PASS' if ok else 'FAIL'} [{n}] {det}")
    bad = [n for n, ok, _ in rows if not ok]
    print(f"A-5/L2 补丁方案：{'PASS' if not bad else 'FAIL'}（{len(rows) - len(bad)}/{len(rows)}）")
    # F-3 修正配套：**真实路径**反例 —— 缺任一表述的文档必须 FAIL
    if path is None:
        import tempfile as _tf
        with _tf.TemporaryDirectory() as _td:
            bad_doc = pathlib.Path(_td) / "plan.md"
            bad_doc.write_text("本方案不得写入 KERT 仓；其余从略。", encoding="utf-8")
            b2 = [n for n, ok, _ in plan_rows_for(bad_doc) if not ok]
            print(f"{'PASS' if 'P4 边界表述齐备（**要求两项同时出现**：不发布新 IRI + 校验先于产出）' in b2 else 'FAIL'} "
                  f"[P4 真实路径反例：缺边界表述 ⇒ 被拦下] {b2}")
            if "P4 边界表述齐备（**要求两项同时出现**：不发布新 IRI + 校验先于产出）" not in b2:
                return 2
    return 0 if not bad else 2


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan-build", action="store_true")
    ap.add_argument("--plan-gate", action="store_true")
    ap.add_argument("--gate", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ns = ap.parse_args()
    if ns.selftest:
        return cmd_selftest()
    if ns.plan_gate:
        return plan_gate()
    if ns.plan_build:
        print(json.dumps(plan_build(), ensure_ascii=False, indent=2))
        return 0
    if ns.gate:
        return cmd_gate()
    d = inspect()
    print(json.dumps(d, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
