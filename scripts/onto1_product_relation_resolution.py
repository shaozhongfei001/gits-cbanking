#!/usr/bin/env python3
"""D2 产品关系分流 · 投影/隔离机制与反例（Owner 决议 2026-09-21 四、D2）

背景：40 条产品关系引用原先**全部** `QUARANTINED_UNRESOLVED`。Owner 已批准 5 个别名映射
（`SETTLEMENT_ACCOUNT`/`CASH_POOL`/`WORKING_CAPITAL_LOAN`/`CROSS_BORDER_RMB_SETTLEMENT`/
`BANK_ACCEPTANCE_DRAFT`）⇒ 28 条登记为 `RESOLVED_BY_OWNER_APPROVED_ALIAS`；其余 12 条保持
`QUARANTINED_UNRESOLVED`。**CQ3 只能报「28 已解析、12 隔离」，不得宣称全量通过。**

检查项：
  G1 计数闭合：resolved + quarantined == 源登记 40，且 relations 逐条双向一致
  G2 目标存在：每个已解析别名的目标产品实例存在于 A-Box（`<ABox>+id` 为 subject）
  G3 隔离未越界：隔离别名**不得**出现在 A-Box 断言（RDF 层，注释不算）
  G4 无虚构产品卡：目标产品必须有 KERT 侧真实产品卡（`CARD_GLOBS`）
  G5 明确否决项：`CASH_MANAGEMENT` 必须仍隔离；denials 齐备
  G6 CQ3 口径：须含 28 与 12，且不得出现「全量通过/全部解析/全部关闭」
  G7 SIM 边界：`sim_only=True` 且 `formal_abox_write=False`

用法：--gate / --selftest（9 反例：M1/M2/M4/M5/M7/M8/M9 mutate ⇒ FAIL，M3 A-Box 越界，M6 还原 ⇒ PASS）
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKSPACE = ROOT.parent
KERT = WORKSPACE / "Leibniz-KERT"
CARD_GLOBS = ["examples/**/product-cards/PROD-*.md", "examples/**/PROD-*.md"]

ABOX = "https://gits.bank.example/ontology/core#"
ABOX_FILE = ROOT / "specs/knowledge-architecture/instances/product/products.ttl"
QUARANTINE = ROOT / "loops/ONTO1-ontology-split/evidence/product-relations-quarantine.json"
ALIAS_REG = ROOT / "loops/ONTO1-ontology-split/evidence/product-alias-resolution.json"

BANNED_CLAIMS = ["全量通过", "全部解析", "全部关闭", "全部解决", "100% 解析"]
EXPECTED_RESOLVED = {"SETTLEMENT_ACCOUNT", "CASH_POOL", "WORKING_CAPITAL_LOAN",
                     "CROSS_BORDER_RMB_SETTLEMENT", "BANK_ACCEPTANCE_DRAFT"}
# A-3 新增：SIM 通道输出面 / 版本化投影配置 / Owner 批准的目标集合
SIM_OUT_DIR = ROOT / "specs/knowledge-architecture/instances/product/sim"
PROJ_CONFIG = ROOT / "specs/knowledge-architecture/instances/product/projection-config.json"
APPROVED_TARGET_IDS = {"prod_set_001", "prod_cm_001", "prod_fin_001", "prod_cb_001", "prod_tf_001"}


def _cards() -> dict[str, Path]:
    found: dict[str, Path] = {}
    for pat in CARD_GLOBS:
        for p in KERT.glob(pat):
            if p.is_file():
                found.setdefault(p.stem.upper(), p)
    return found


def _card_name(instance_id: str) -> str:
    m = re.fullmatch(r"prod_([a-z]+)_(\d+)", instance_id)
    return f"PROD-{m.group(1).upper()}-{m.group(2)}" if m else instance_id.upper()


def _abox_subjects(path: Path) -> set[str]:
    from rdflib import Graph, RDF

    g = Graph()
    g.parse(str(path), format="turtle")
    return {str(s) for s in g.subjects(RDF.type, None)}


def _abox_text_terms(path: Path) -> list[str]:
    from rdflib import Graph

    g = Graph()
    g.parse(str(path), format="turtle")
    out: list[str] = []
    for s, p, o in g:
        out.extend([str(s), str(p), str(o)])
    return out


def run_checks(abox: Path, quarantine: Path, registry: Path,
               sim_dir: Path | None = None, config: Path | None = None) -> list[tuple[str, bool, str]]:
    sim_dir = sim_dir if sim_dir is not None else SIM_OUT_DIR
    config = config if config is not None else PROJ_CONFIG
    res: list[tuple[str, bool, str]] = []
    q = json.loads(quarantine.read_text(encoding="utf-8"))
    r = json.loads(registry.read_text(encoding="utf-8"))
    entries = q["entries"]

    resolved = r.get("resolved_by_owner_approved_alias", [])
    quarantined = r.get("quarantined_unresolved", [])
    src_by_alias: dict[str, set[str]] = {}
    for e in entries:
        sym = e["value"]
        src_by_alias.setdefault(sym, set()).add(f'{e["card"]}[{e["field"]}] -> {sym}')

    # G1 计数闭合 + 逐条双向一致
    reg_map: dict[str, set[str]] = {}
    for item in resolved + quarantined:
        reg_map[item["alias"]] = set(item.get("relations", []))
    n_res = sum(i.get("relation_count", 0) for i in resolved)
    n_qua = sum(i.get("relation_count", 0) for i in quarantined)
    mismatched = {a: (len(v), len(src_by_alias.get(a, set()))) for a, v in reg_map.items()
                  if v != src_by_alias.get(a, set())}
    ok1 = (n_res + n_qua == len(entries) == 40 and n_res == 28 and n_qua == 12
           and not mismatched and set(reg_map) == set(src_by_alias)
           and r.get("counts", {}).get("total") == len(entries))
    res.append(("G1", ok1, f"resolved={n_res} quarantined={n_qua} 源={len(entries)} "
                           f"不一致={list(mismatched)[:3] or '无'} 别名覆盖={set(reg_map) == set(src_by_alias)}"))

    # G2 目标存在（A-Box subject）
    subjects = _abox_subjects(abox)
    missing = [i["alias"] for i in resolved if i["target_iri"] not in subjects]
    res.append(("G2", not missing and len(resolved) == 5,
                f"已解析 {len(resolved)} 别名；目标缺失={missing or '无'}（A-Box 实例 {len(subjects)} 个）"))

    # G3 隔离未越界（RDF 层）
    terms = _abox_text_terms(abox)
    leaked = sorted({a for a in src_by_alias if a not in EXPECTED_RESOLVED and any(a in t for t in terms)})
    res.append(("G3", not leaked, f"隔离别名出现在 A-Box 断言中 = {leaked or '无（0 处越界）'}"))

    # G4 无虚构产品卡
    cards = _cards()
    missing_cards = [i["target_product_id"] for i in resolved
                     if _card_name(i["target_product_id"]) not in cards]
    res.append(("G4", not missing_cards and len(cards) == 13,
                f"KERT 卡 {len(cards)} 张；已解析目标缺卡={missing_cards or '无'}"))

    # G5 明确否决项
    resolved_aliases = {i["alias"] for i in resolved}
    cm_still_quarantined = "CASH_MANAGEMENT" not in resolved_aliases
    denials = " ".join(r.get("explicit_denials", []))
    ok5 = cm_still_quarantined and "CASH_MANAGEMENT" in denials and "虚构" in denials
    res.append(("G5", ok5, f"CASH_MANAGEMENT 保持隔离={cm_still_quarantined}；否决项条数={len(r.get('explicit_denials', []))}"))

    # G6 CQ3 口径
    cq3 = str(q.get("cq3_status", ""))
    bad_claims = [c for c in BANNED_CLAIMS if c in cq3]
    ok6 = ("28" in cq3 and "12" in cq3 and not bad_claims)
    res.append(("G6", ok6, f"cq3_status={cq3!r}；越权声称={bad_claims or '无'}"))

    # G7 SIM 边界（F-2 修正：原仅读制品**自声明**字段 ⇒ 真实路径恒真）。
    # **正确派生口径**：SIM 通道里使用的关系**谓词**不得同时作为 A-Box 的谓词出现
    # （即"28 条关系只存在于 SIM 通道"，而非被写进正式 A-Box）。
    # 注意：A-Box 中出现**别名作为字面值**是产品卡源数据，属预期，不在本条判定范围。
    def _local(term: str) -> str:
        return term.rsplit("#", 1)[-1].rsplit("/", 1)[-1]

    # 只比较**领域命名空间**谓词（排除 rdf/rdfs/owl/xsd/skos 等通用词汇：两侧都会合法出现）
    GENERIC_NS = ("http://www.w3.org/1999/02/22-rdf-syntax-ns#", "http://www.w3.org/2000/01/rdf-schema#",
                  "http://www.w3.org/2002/07/owl#", "http://www.w3.org/2001/XMLSchema#",
                  "http://www.w3.org/2004/02/skos/core#")
    DOMAIN_NS = ("https://gientech.com/gits/kno/", "https://gits.bank.example/ontology/core#")

    def _domain_preds(path: pathlib.Path) -> set[str]:
        out: set[str] = set()
        try:
            from rdflib import Graph as _G

            g = _G()
            g.parse(str(path), format="turtle")
            for _, p, _ in g:
                sp = str(p)
                if sp.startswith(DOMAIN_NS) and not sp.startswith(GENERIC_NS):
                    out.add(_local(sp))
        except Exception:  # noqa: BLE001
            return set()
        return out

    sim_preds: set[str] = set()
    if SIM_OUT_DIR.is_dir():
        for f in SIM_OUT_DIR.rglob("*.ttl"):
            sim_preds |= _domain_preds(f)
    abox_preds = _domain_preds(abox) if abox.is_file() else set()
    leaked_preds = sorted(sim_preds & abox_preds)
    sim_under_simdir = SIM_OUT_DIR.is_dir() and any(SIM_OUT_DIR.rglob("*"))
    declared_ok = r.get("sim_only") is True and r.get("formal_abox_write") is False
    derived_ok = not leaked_preds and sim_under_simdir
    ok7 = declared_ok and derived_ok
    res.append(("G7", ok7,
                f"声明 sim_only={r.get('sim_only')}/formal_abox_write={r.get('formal_abox_write')}；"
                f"**派生**：SIM 领域谓词 {len(sim_preds)} 个，其中作为 A-Box 领域谓词出现 = {leaked_preds or '无'}；"
                f"SIM 目录非空={sim_under_simdir}"))

    quar_aliases = [x.get("alias") for x in r.get("quarantined_unresolved", [])]

    # G8 隔离别名不得出现在 **SIM 通道任何输出**
    sim_files = [f for f in sorted(sim_dir.rglob("*")) if f.is_file()] if sim_dir.is_dir() else []
    leaked_sim: list[str] = []
    for f in sim_files:
        try:
            txt = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        leaked_sim += [f"{f.name}:{a}" for a in quar_aliases if a and a in txt]
    rel_sum = sum(int(x.get("relation_count", 0)) for x in r.get("quarantined_unresolved", []))
    ok8 = not leaked_sim and rel_sum == 12 and len(quar_aliases) == 7
    res.append(("G8", ok8, f"SIM 输出 {len(sim_files)} 文件；隔离别名越界={leaked_sim or '0 处'}；"
                            f"隔离 {len(quar_aliases)} 别名 / {rel_sum} 关系（期望 7/12）"))

    # G9 目标集合与别名集合必须与 Owner 批准 5 项**完全一致**
    targets = {x.get("target_product_id") for x in r.get("resolved_by_owner_approved_alias", [])}
    aliases = {x.get("alias") for x in r.get("resolved_by_owner_approved_alias", [])}
    ok9 = targets == APPROVED_TARGET_IDS and aliases == EXPECTED_RESOLVED
    res.append(("G9", ok9,
                f"目标{'一致' if ok9 else '不一致'}：多出={sorted(targets - APPROVED_TARGET_IDS)} "
                f"缺失={sorted(APPROVED_TARGET_IDS - targets)} 别名差={sorted(aliases ^ EXPECTED_RESOLVED)}"))

    # G10 账本**新鲜度**：登记的源哈希必须等于**当前**隔离表哈希（陈旧账本即 FAIL）
    src_sha = hashlib.sha256(quarantine.read_bytes()).hexdigest()
    ok10 = r.get("source_sha256") == src_sha
    res.append(("G10", ok10, f"账本源哈希{'= 当前隔离表' if ok10 else '≠ 当前隔离表（陈旧账本）'}"))

    # G11 隔离别名不得进入**版本化投影配置**
    cfg_alias: set[str] = set()
    if config.is_file():
        cfg = json.loads(config.read_text(encoding="utf-8"))
        cfg_alias = {str(k).upper() for k in (cfg.get("aliasMap") or {})}
    leaked_cfg = sorted(set(quar_aliases) & cfg_alias)
    res.append(("G11", not leaked_cfg, f"配置 aliasMap 键数={len(cfg_alias)}；隔离别名越界={leaked_cfg or '0 处'}"))

    return res


def cmd_gate() -> int:
    rows = run_checks(ABOX_FILE, QUARANTINE, ALIAS_REG)
    print("# command=onto1_product_relation_resolution --gate")
    for cid, ok, d in rows:
        print(f"{'PASS' if ok else 'FAIL'} [{cid}] {d}")
    bad = [c for c, ok, _ in rows if not ok]
    print(f"D2 分流：{'PASS' if not bad else 'FAIL'}（{len(rows) - len(bad)}/{len(rows)}；未过={bad}）")
    print("CQ3 口径：28 条已解析 / 12 条隔离（**不得宣称全量通过**）")
    return 0 if not bad else 2


def _mutants(reg: dict, q: dict):
    def m1(r, qq):
        r = copy.deepcopy(r)
        r["resolved_by_owner_approved_alias"].append(
            {"alias": "CASH_MANAGEMENT", "target_product_id": "prod_cm_001",
             "target_iri": ABOX + "prod_cm_001", "relation_count": 2, "relations": []})
        return r, qq
    def m2(r, qq):
        r = copy.deepcopy(r)
        r["resolved_by_owner_approved_alias"][0]["target_product_id"] = "prod_zzz_999"
        r["resolved_by_owner_approved_alias"][0]["target_iri"] = ABOX + "prod_zzz_999"
        return r, qq
    def m4(r, qq):
        qq = copy.deepcopy(qq)
        qq["cq3_status"] = "全量通过"
        return r, qq
    def m5(r, qq):
        r = copy.deepcopy(r)
        r["resolved_by_owner_approved_alias"][0]["relation_count"] += 1
        return r, qq
    def m9(r, qq):
        qq = copy.deepcopy(qq)
        qq["entries"] = qq.get("entries", []) + [{"card": "X", "field": "y", "value": "Z"}]
        return r, qq
    return {"M1 把 CASH_MANAGEMENT 映射为产品": m1,
            "M2 目标改为不存在的产品实例": m2,
            "M4 CQ3 声称全量通过": m4,
            "M5 已解析计数被篡改": m5}


def cmd_selftest() -> int:
    base = run_checks(ABOX_FILE, QUARANTINE, ALIAS_REG)
    ok0 = all(o for _, o, _ in base)
    print(f"{'PASS' if ok0 else 'FAIL'} [M0 对照] 现状 {sum(1 for _, o, _ in base if o)}/{len(base)} = {ok0}")
    fails = 0 if ok0 else 1
    total = 1   # 计数口径：**动态累加**（原先硬编码 6 与实际 7 项不符，已按 C5 口径统一修正）
    reg = json.loads(ALIAS_REG.read_text(encoding="utf-8"))
    q = json.loads(QUARANTINE.read_text(encoding="utf-8"))
    orig_abox = ABOX_FILE.read_text(encoding="utf-8")

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        for name, mutate in _mutants(reg, q).items():
            total += 1
            r2, q2 = mutate(reg, q)
            rp, qp = td / "reg.json", td / "q.json"
            rp.write_text(json.dumps(r2, ensure_ascii=False), encoding="utf-8")
            qp.write_text(json.dumps(q2, ensure_ascii=False), encoding="utf-8")
            bad = [c for c, ok, _ in run_checks(ABOX_FILE, qp, rp) if not ok]
            good = bool(bad)
            fails += 0 if good else 1
            print(f"{'PASS' if good else 'FAIL'} [{name}] 被拦下 = {bad or '无（漏检！）'}")

        # M7 隔离别名写入 **SIM 通道输出** ⇒ G8 必须 FAIL
        sim = td / "sim"; sim.mkdir()
        (sim / "leak.ttl").write_text('prod:prod_cm_001 gits:note "CORPORATE_E_BANK" .\n', encoding="utf-8")
        bad = [c for c, ok, _ in run_checks(ABOX_FILE, QUARANTINE, ALIAS_REG, sim_dir=sim) if not ok]
        good = "G8" in bad
        fails += 1 if not good else 0; total += 1
        print(f"{'PASS' if good else 'FAIL'} [M7 隔离别名写入 SIM 输出] 被拦下 = {bad}")

        # M8 隔离别名进入**版本化配置 aliasMap** ⇒ G11 必须 FAIL
        cfg_p = td / "cfg.json"
        cfg_p.write_text(json.dumps({"aliasMap": {"CASH_MANAGEMENT": "PROD-CM-001"}}), encoding="utf-8")
        bad = [c for c, ok, _ in run_checks(ABOX_FILE, QUARANTINE, ALIAS_REG, config=cfg_p) if not ok]
        good = "G11" in bad
        fails += 1 if not good else 0; total += 1
        print(f"{'PASS' if good else 'FAIL'} [M8 隔离别名进入投影配置] 被拦下 = {bad}")

        # M9 **陈旧账本**（源哈希失配）⇒ G10 必须 FAIL
        q_old = td / "q_old.json"
        q_old.write_text(json.dumps({"entries": []}), encoding="utf-8")
        bad = [c for c, ok, _ in run_checks(ABOX_FILE, q_old, ALIAS_REG) if not ok]
        good = "G10" in bad
        fails += 1 if not good else 0; total += 1
        print(f"{'PASS' if good else 'FAIL'} [M9 陈旧账本（源哈希失配）] 被拦下 = {bad}")

        # M3 把隔离别名写进 A-Box（RDF 层）⇒ G3 必须 FAIL
        mut = td / "abox.ttl"
        mut.write_text(orig_abox + '\nprod:prod_cm_001 rdfs:comment "CORPORATE_E_BANK" .\n', encoding="utf-8")
        bad = [c for c, ok, _ in run_checks(mut, QUARANTINE, ALIAS_REG) if not ok]
        good = "G3" in bad
        fails += 0 if good else 1
        total += 1
        print(f"{'PASS' if good else 'FAIL'} [M3 隔离别名写入 A-Box] 被拦下 = {bad}")

    back = run_checks(ABOX_FILE, QUARANTINE, ALIAS_REG)
    okr = all(o for _, o, _ in back) and ABOX_FILE.read_text(encoding="utf-8") == orig_abox
    fails += 0 if okr else 1
    total += 1
    print(f"{'PASS' if okr else 'FAIL'} [M6 还原对照] 全绿 且 A-Box 逐字节未变 = {okr}")
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
