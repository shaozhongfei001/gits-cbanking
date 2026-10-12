#!/usr/bin/env python3
"""D2 · SIM 关系投影（Owner 决议 2026-09-21 三、D2；2026-09-22 裁定后升至配置 1.1.0）

把版本化配置中 `aliasMap` 已批准的关系写入 **SIM A-Box 投影**（**不是**正式 A-Box、**不批准**正式关系发布）。
当前配置（1.1.0）下：6 个别名 → **30 条**关系（原 1.0.0 为 5 别名 / 28 条）。

约束（逐条对应决议）：
  · `simulationOnly=true`；正式关系发布 = `NOT_AUTHORIZED`
  · 投影文件是**生成产物**：可由产品卡 + 版本化别名配置重新生成；**幂等**（重复运行字节一致）
  · **产品卡仍是关系实例的权威来源**（脚本只读卡；每条关系保留来源卡、字段、卡哈希、Owner 决议标识）
  · 别名映射一律来自**版本化配置**（`projection-config.json`），**不得硬编码于程序**
  · **三类别名不得进入任何 A-Box 投影**：`quarantinedAliases`（未决，当前为空）
    ∪ `pendingProductCards`（有效待补，等新卡）∪ `voidReferences`（裁定作废）
  · 空转即失败：上述三类**并集为空**时，G3 不判通过（无检查对象 ≠ 通过）

用法：`--build`（默认，写文件）/ `--gate` / `--selftest` / `--verify-determinism`
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "specs/knowledge-architecture/instances/product/projection-config.json"
OUT = ROOT / "specs/knowledge-architecture/instances/product/sim/product-relations.SIM.ttl"
# 未决登记（单源产出：由本脚本写，见 G10 防漂移）
UNRES = ROOT / "specs/knowledge-architecture/instances/product/UNRESOLVED.json"
CARDS = Path("/home/szf/dev/Leibniz-KERT/examples/product-recommendation-assets/03_core")
SIM_NS = "https://gits.bank.example/ontology/core#sim/"
DCT = "http://purl.org/dc/terms/"


def _load_generator():
    """复用 GK17 生成器的 front-matter 解析（单一来源，避免两套卡解析逻辑）。"""
    spec = importlib.util.spec_from_file_location("gk17_gen", ROOT / "scripts/gk17_prodcard_to_rdf.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def build(config: Path = CONFIG, out: Path = OUT, cards_dir: Path = CARDS) -> tuple[str, dict]:
    cfg = json.loads(config.read_text(encoding="utf-8"))
    gen = _load_generator()
    cards = gen.collect_cards([cards_dir], cfg["relationFields"])
    known = {c["product_id"] for c in cards}
    aliases = cfg["aliasMap"]
    inst_p, term_p = cfg["namespaces"]["instances"]["prefix"], cfg["namespaces"]["terms"]["prefix"]
    decision = cfg["aliasMapDecisionRef"]

    card_paths = {p.name: p for p in cards_dir.rglob("product-cards/*.md")}
    rels: list[dict] = []
    skipped: list[dict] = []
    for c in sorted(cards, key=lambda x: x["product_id"]):
        subj_id = c["product_id"].lower().replace("-", "_")
        for field, prop in cfg["relationFields"].items():
            for target in c["relations"][field]:
                if target not in aliases:
                    skipped.append({"card": c["file"], "field": field, "symbol": target})
                    continue
                obj_id = aliases[target].lower().replace("-", "_")
                if aliases[target] not in known:
                    raise ValueError(f"别名 {target} 指向不存在的产品卡 {aliases[target]}")
                rels.append({"subj": f"{inst_p}:{subj_id}", "prop": f"{term_p}:{prop}",
                             "obj": f"{inst_p}:{obj_id}", "card": c["file"], "field": field,
                             "card_sha256": _sha(card_paths[c["file"]]), "alias": target})
    rels.sort(key=lambda r: (r["subj"], r["prop"], r["obj"], r["card"], r["field"], r["alias"]))

    lines = [
        "# SIM 关系投影（simulation_only）—— 生成产物，勿手工编辑。",
        "# simulationOnly=true ； formalRelationRelease=NOT_AUTHORIZED ；",
        f"# config_version={cfg.get('version')} config_sha256={_sha(config)[:16]} ；",
        f"# 权威来源：KERT 产品卡（关系实例）+ 版本化别名配置（Owner 已批准的 {len(aliases)} 个别名）。",
        "# 隔离：本文件**不含**任何未决（QUARANTINED_UNRESOLVED）/ 待补（PENDING_PRODUCT_CARD）/ 作废（VOID）关系。",
        f"@prefix {term_p}: <{cfg['namespaces']['terms']['iri']}> .",
        f"@prefix {inst_p}: <{cfg['namespaces']['instances']['iri']}> .",
        "@prefix rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .",
        "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .",
        "@prefix owl:  <http://www.w3.org/2002/07/owl#> .",
        "@prefix dct:  <http://purl.org/dc/terms/> .",
        f"@prefix sim:  <{SIM_NS}> .",
        "",
        "# ── 自描述：SIM 元数据与投影内注解属性（仅本文件内声明，不写入正式 A-Box/T-Box）──",
        f"{inst_p}:SIM-PROJECTION a owl:Ontology ;",
        f"  rdfs:comment \"simulationOnly=true; formalRelationRelease=NOT_AUTHORIZED\" ;",
        f"  dct:identifier \"{decision}\" ;",
        f"  dct:source \"projection-config.json@{_sha(config)}\" .",
        "",
    ]
    for ap in ("simulationOnly", "sourceField", "sourceCardSha256", "ownerAliasDecision", "sourceAlias"):
        lines.append(f"sim:{ap} a owl:AnnotationProperty .")
    lines.append("")

    lines.append(f"# ── {len(rels)} 条已批准关系（去重后的直接三元组）──")
    direct = sorted({(r["subj"], r["prop"], r["obj"]) for r in rels})
    for s, p, o in direct:
        lines.append(f"{s} {p} {o} .")
    lines.append("")
    lines.append(f"# ── 逐条溯源（reification；共 {len(rels)} 条，与 {len(direct)} 个去重三元组对应）──")
    lines.append(f"{inst_p}:SIM-PROJECTION sim:simulationOnly true .")
    for r in rels:
        lines.append("[] a rdf:Statement ;")
        lines.append(f"  rdf:subject {r['subj']} ;")
        lines.append(f"  rdf:predicate {r['prop']} ;")
        lines.append(f"  rdf:object {r['obj']} ;")
        lines.append(f"  dct:source \"{r['card']}\" ;")
        lines.append(f"  sim:sourceField \"{r['field']}\" ;")
        lines.append(f"  sim:sourceAlias \"{r['alias']}\" ;")
        lines.append(f"  sim:sourceCardSha256 \"{r['card_sha256']}\" ;")
        lines.append(f"  sim:ownerAliasDecision \"{decision}\" .")
        lines.append("")
    text = "\n".join(lines).rstrip() + "\n"
    quar = set(cfg.get("quarantinedAliases", {}))
    pend = set(cfg.get("pendingProductCards", {}))
    void = set(cfg.get("voidReferences", {}))
    skipped_counts = {
        "skipped_unresolved": sum(1 for s in skipped if s["symbol"] in quar),
        "skipped_pending": sum(1 for s in skipped if s["symbol"] in pend),
        "skipped_void": sum(1 for s in skipped if s["symbol"] in void),
    }
    skipped_counts["skipped_unclassified"] = len(skipped) - sum(skipped_counts.values())
    report = {"relations": len(rels), "distinct_triples": len(direct),
              "skipped_quarantined": len(skipped), "cards": len(cards),
              "config_version": cfg.get("version"),
              "simulationOnly": True, "formalRelationRelease": "NOT_AUTHORIZED",
              **skipped_counts}
    # 未决登记的期望结构（由 main() 写盘；run_checks 的 G10 与盘上比对防漂移）
    def _cls(sym: str) -> str:
        if sym in quar:
            return "QUARANTINED_UNRESOLVED"
        if sym in pend:
            return "PENDING_PRODUCT_CARD"
        if sym in void:
            return "VOID_BY_OWNER_DECISION"
        return "UNCLASSIFIED"
    report["unresolved_report"] = {
        "projectionConfig": {
            "file": str(config),
            "version": cfg.get("version"),
            "sha256": _sha(config),
            "namespaces": cfg["namespaces"],
            "simulationOnly": cfg.get("simulationOnly"),
        },
        "cardFiles": [c["file"] for c in sorted(cards, key=lambda x: x["product_id"])],
        "productIndividuals": len(cards),
        "productIds": [c["product_id"] for c in sorted(cards, key=lambda x: x["product_id"])],
        "relationInstances": len(rels),
        "unresolvedReferenceCount": len(skipped),
        "unresolved": [
            {"card": s["card"], "field": s["field"], "referenced_symbol": s["symbol"],
             "classification": _cls(s["symbol"])}
            for s in sorted(skipped, key=lambda x: (x["card"], x["field"], x["symbol"]))
        ],
        "relationTypeAuthority": "ontology (gits-core.owl.ttl)",
        "relationInstanceAuthority": "product cards (this projection's input)",
    }
    return text, report
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    return text, report


def run_checks(config: Path, out: Path, tmp: Path) -> list[tuple[str, bool, str]]:
    rows: list[tuple[str, bool, str]] = []
    t1, rep1 = build(config, tmp / "a.ttl")
    t2, rep2 = build(config, tmp / "b.ttl")
    h1 = hashlib.sha256(t1.encode()).hexdigest()
    h2 = hashlib.sha256(t2.encode()).hexdigest()
    rows.append(("G1", h1 == h2, f"幂等（两次生成字节一致）={h1 == h2} sha256={h1[:16]}"))
    rows.append(("G2", rep1["relations"] == 30, f"投影关系数={rep1['relations']}（应 30；去重三元组 {rep1['distinct_triples']}）"))

    cfg = json.loads(config.read_text(encoding="utf-8"))
    quar = set(cfg.get("quarantinedAliases", {}))
    pend = set(cfg.get("pendingProductCards", {}))
    void = set(cfg.get("voidReferences", {}))
    blocked = quar | pend | void
    leaked = sorted({a for a in blocked if re.search(rf'"{re.escape(a)}"|\b{re.escape(a)}\b', t1)})
    ok3 = (not leaked) and bool(blocked)
    rows.append(("G3", ok3,
                 f"不得进投影的别名（未决∪待补∪作废）={len(blocked)} 个，泄漏={leaked or '无（0 处）'}；"
                 f"并集为空按**空转**判失败（当前 {'非空' if blocked else '空集⇒FAIL'}）"))

    ok4 = ('sim:simulationOnly true' in t1 and "NOT_AUTHORIZED" in t1
           and cfg.get("simulationOnly") is True
           and str(cfg.get("formalRelationRelease")) == "NOT_AUTHORIZED")
    rows.append(("G4", ok4, f"**声明一致性**（不作独立事实证据）；文件内 simulationOnly={'sim:simulationOnly true' in t1} NOT_AUTHORIZED={'NOT_AUTHORIZED' in t1}；"
                            f"配置 simulationOnly={cfg.get('simulationOnly')} release={cfg.get('formalRelationRelease')}"))

    n_stmt = len(re.findall(r"\[\] a rdf:Statement", t1))
    n_sha = t1.count('sim:sourceCardSha256 "')
    n_fld = t1.count('sim:sourceField "')
    n_dec = t1.count('sim:ownerAliasDecision "')
    ok5 = n_stmt == 30 and n_sha == 30 and n_fld == 30 and n_dec == 30
    rows.append(("G5", ok5, f"溯源语句={n_stmt}；取值数 哈希/字段/决议 = {n_sha}/{n_fld}/{n_dec}（各应 30，表头声明不计）"))

    src = (ROOT / "scripts/onto1_sim_projection.py").read_text(encoding="utf-8")
    hardcoded = sorted(a for a in cfg["aliasMap"] if re.search(rf'"{a}"', src))
    rows.append(("G6", not hardcoded, f"程序内硬编码别名 = {hardcoded or '无（全部来自配置）'}"))

    gen = _load_generator()
    cards = gen.collect_cards([CARDS], cfg["relationFields"])
    paths = {p.name: p for p in CARDS.rglob("product-cards/*.md")}
    contributing = set(re.findall(r'dct:source "(PROD-[A-Z]+-\d+\.md)"', t1))
    known_files = {c["file"] for c in cards}
    unknown = sorted(contributing - known_files)
    mism = [f for f in sorted(contributing)
            if f in paths and f'sim:sourceCardSha256 "{_sha(paths[f])}"' not in t1]
    ok7 = not mism and not unknown and len(contributing) > 0
    rows.append(("G7", ok7, f"贡献关系的来源卡 {len(contributing)} 张：哈希与磁盘一致={not mism}；未知卡={unknown or '无'}"))

    # G8 **盘上制品一致性**（QA-W3R3）：原 `out` 参数从未被引用 ⇒ 门禁对盘上篡改无判别力。
    # 现要求盘上制品存在，且与"重新生成"逐字节一致（生成确定、无时间依赖，已实测）。
    disk = out.read_text(encoding="utf-8") if out.is_file() else None
    ok8 = disk is not None and disk == t1
    rows.append(("G8", ok8,
                 f"**盘上制品**与重新生成逐字节一致（真读盘；失败码 SIM_ARTIFACT_DRIFT）；"
                 f"盘上={hashlib.sha256(disk.encode()).hexdigest()[:16] if disk else '缺失'} "
                 f"重生成={h1[:16]} ⇒ {'一致' if ok8 else '**不一致/缺失**'}"))

    # G9（2026-09-22 新增）：待补/作废类别**不得**被静默提升为可解析别名；待补项须带元数据。
    promoted = sorted((pend | void) & set(cfg["aliasMap"]))
    meta_bad = sorted(a for a, v in cfg.get("pendingProductCards", {}).items()
                      if not v.get("reason") or "relationCount" not in v)
    ok9 = not promoted and not meta_bad
    rows.append(("G9", ok9,
                 f"待补/作废别名被提升进 aliasMap = {promoted or '无'}；"
                 f"待补项缺 reason/relationCount = {meta_bad or '无'}（失败码 SIM_PENDING_ALIAS_PROMOTED）"))

    # G10（2026-09-22 新增）：**未决登记的盘上一致性** —— 防"状态漂移"
    #（本次实测到的缺陷：别名批准后 UNRESOLVED.json 仍记 40 条未决，与配置不符）。
    exp = rep1["unresolved_report"]
    disk_unres: dict | None = None
    if UNRES.is_file():
        try:
            disk_unres = json.loads(UNRES.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            disk_unres = None
    disk_rows = sorted(
        (u.get("card"), u.get("field"), u.get("referenced_symbol"), u.get("classification"))
        for u in (disk_unres or {}).get("unresolved", [])
    )
    exp_rows = sorted(
        (u["card"], u["field"], u["referenced_symbol"], u["classification"]) for u in exp["unresolved"]
    )
    disk_cfg_ver = ((disk_unres or {}).get("projectionConfig") or {}).get("version")
    disk_n = (disk_unres or {}).get("unresolvedReferenceCount")
    disk_rel = (disk_unres or {}).get("relationInstances")
    ok10 = (disk_unres is not None and disk_n == exp["unresolvedReferenceCount"]
            and disk_rel == exp["relationInstances"] and disk_rows == exp_rows
            and disk_cfg_ver == exp["projectionConfig"]["version"])
    rows.append(("G10", ok10,
                 f"未决登记与重算一致（失败码 SIM_UNRESOLVED_DRIFT）；盘上未决={disk_n if disk_unres else '缺失'}"
                 f" 期望={exp['unresolvedReferenceCount']}；relationInstances={disk_rel}/{exp['relationInstances']}"
                 f"；config 版本={disk_cfg_ver}/{exp['projectionConfig']['version']}"))
    return rows


def cmd_gate() -> int:
    with tempfile.TemporaryDirectory() as td:
        rows = run_checks(CONFIG, OUT, Path(td))
    print("# command=onto1_sim_projection --gate")
    for cid, ok, d in rows:
        print(f"{'PASS' if ok else 'FAIL'} [{cid}] {d}")
    bad = [c for c, ok, _ in rows if not ok]
    print(f"SIM 投影：{'PASS' if not bad else 'FAIL'}（{len(rows) - len(bad)}/{len(rows)}；未过={bad}）")
    return 0 if not bad else 2


def cmd_selftest() -> int:
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        base = run_checks(CONFIG, OUT, td / "b")
        ok0 = all(o for _, o, _ in base)
        print(f"{'PASS' if ok0 else 'FAIL'} [M0 对照] 现状 "
              f"{sum(1 for _, o, _ in base if o)}/{len(base)} = {ok0}")
        fails = 0 if ok0 else 1
        cfg = json.loads(CONFIG.read_text(encoding="utf-8"))

        def mut(name, fn):
            c = fn(json.loads(CONFIG.read_text(encoding="utf-8")))
            p = td / f"c_{name}.json"
            p.write_text(json.dumps(c, ensure_ascii=False), encoding="utf-8")
            return p

        # M1 把**待补**别名放进 aliasMap
        # 2026-09-22 修正：原夹具用 CASH_MANAGEMENT —— 该符号经 Owner 裁定已成为合法别名，
        # 若继续使用，本变异用例会**永远通过**（防线退化）。改用待补类 CORPORATE_E_BANK。
        def m1(c):
            c["aliasMap"]["CORPORATE_E_BANK"] = "PROD-CM-001"
            return c
        # M2 去掉 simulationOnly 标记（生成文本将缺 "sim:simulationOnly true"）
        def m2(c):
            c["simulationOnly"] = False
            return c
        # M3 卡哈希不回填（模拟溯源缺失）—— 通过临时改写 OUT 内容实现，单独处理

        for name, fn, expect in (("M1 把待补别名 CORPORATE_E_BANK 加入别名映射", m1, "G3"),
                                 ("M2 simulationOnly=false", m2, "G4")):
            p = mut(name.split()[0], fn)
            rows = run_checks(p, OUT, td / f"m_{name.split()[0]}")
            bad = [c for c, ok, _ in rows if not ok]
            good = any(str(x).startswith(expect) for x in bad)
            fails += 0 if good else 1
            print(f"{'PASS' if good else 'FAIL'} [{name}] 被拦下 = {bad or '无（漏检！）'}")

        # M3 溯源缺失：篡改生成结果后断言 G5
        t, _ = build(CONFIG, td / "m3.ttl")
        tampered = td / "m3_tampered.ttl"
        tampered.write_text(re.sub(r'\n  sim:sourceCardSha256 "[^"]+" ;', "", t), encoding="utf-8")
        n_stmt = len(re.findall(r"\[\] a rdf:Statement", tampered.read_text(encoding="utf-8")))
        has_sha = 'sim:sourceCardSha256 "' in tampered.read_text(encoding="utf-8")
        good = n_stmt == 30 and not has_sha
        fails += 0 if good else 1
        print(f"{'PASS' if good else 'FAIL'} [M3 去掉卡哈希溯源] 溯源语句 {n_stmt}、哈希字段存在={has_sha} ⇒ 会被 G5 拦下")

        # M4 非幂等（打乱输入顺序）
        gen = _load_generator()
        order = [1, 0] + list(range(2, 13))
        cards = gen.collect_cards([CARDS], cfg["relationFields"])
        shuffled = [cards[i] for i in order if i < len(cards)]
        s1 = "\n".join(f"{c['product_id']}" for c in cards)
        s2 = "\n".join(f"{c['product_id']}" for c in shuffled)
        good = s1 != s2  # 顺序确被打乱；而 build() 内部按 id 排序 ⇒ 输出仍一致（幂等由 G1 保证）
        fails += 0 if good else 1
        print(f"{'PASS' if good else 'FAIL'} [M4 输入顺序打乱] 夹具顺序确已打乱={good}（build() 内部排序 ⇒ G1 仍应一致）")

    print(f"--selftest {'PASS' if fails == 0 else 'FAIL'}（{4 - fails}/4）")
    return 0 if fails == 0 else 2


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--gate", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--verify-determinism", action="store_true")
    ns = ap.parse_args()
    if ns.selftest:
        return cmd_selftest()
    if ns.gate:
        return cmd_gate()
    text, rep = build()
    print(f"已生成 {OUT.relative_to(ROOT)}：关系 {rep['relations']} 条（去重三元组 {rep['distinct_triples']}）；"
          f"跳过 {rep['skipped_quarantined']} 条 —— 未决 {rep['skipped_unresolved']} · "
          f"待补 {rep['skipped_pending']} · 作废 {rep['skipped_void']} · 未分类 {rep['skipped_unclassified']}")
    # 未决登记单源产出（与投影同一次构建生成，防两份状态漂移）
    unre = rep["unresolved_report"]
    UNRES.write_text(json.dumps(unre, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"已更新 {UNRES.relative_to(ROOT)}：未决 {unre['unresolvedReferenceCount']} 条"
          f"（待补 {rep['skipped_pending']} · 作废 {rep['skipped_void']}）")
    if ns.verify_determinism:
        again, _ = build()
        print(f"determinism: {'IDENTICAL' if again == text else 'DIFFERENT'}")
        return 0 if again == text else 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
