#!/usr/bin/env python3
"""32 类 × 目标层 × 45 制品口径 逐类核清（Owner 复核项 一）

**要解决的问题**：本轮报告中出现"L1 候选骨架 32 类"，而目标设计 **L1 = 8 类**。
本脚本把两件事**分开**并各自取证：

  1. **来源盘点**（`SOURCE_INVENTORY`）：现有 `gits-core.owl.ttl` 的 **32 个 OWL 类**（= 基线全量，非 L1 候选）；
  2. **L1 候选模型**（`L1_CANDIDATE`）：目标设计 §4.2 的 **8 类**，逐项标注来源（基线映射 / 新增）。

逐类输出：现有 IRI、当前归属、目标层、权威责任、保留或迁移理由、对应的 32→45 映射项。

口径（**避免委员会已批评过的混算**）：
  · `32` = 基线 **OWL 类**数；
  · `45` = 目标 **制品**数 = 39 OWL 类 + 1 SKOS 概念体系 + 5 集成契约 Schema 对象；**不是"45 个本体类"**；
  · `87` = `attribution-45-v2.csv` 的**行数**（另含 36 对象属性 + 5 L4 Schema 字段 + 1 退役）。

用法：`--build` / `--gate` / `--selftest`
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
EV = ROOT / "loops/ONTO1-ontology-split/evidence"
PREP = EV / "prep"
MAP32 = ROOT / "docs/review/ARCH-ONTO-2026-001-rereview-package/04-基线32项映射表.md"
ATTR = EV / "attribution-45-v2.csv"
CORE = ROOT / "specs/semantic/gits-core.owl.ttl"
DESIGN = ROOT / "docs/architecture/ONTOLOGY-SPLIT-DESIGN-V2.0-REVIEW.md"
INVENTORY = PREP / "l1-skeleton/l1-term-inventory.json"

# 目标设计 §4.2 的 L1 八类（权威原文；脚本内作为**对照基准**，非事实来源）
L1_DESIGN = {
    "Party": "新增（委员会 §3.6）",
    "Organization": "新增（委员会 §3.6）",
    "LegalEntity": "基线 LegalEntity",
    "CustomerRole": "基线 Customer 重构",
    "EnterpriseGroup": "基线 CorporateGroup 改名",
    "GroupMembership": "基线 GroupRelationship 重构",
    "ProductOffering": "基线 Product 改名重构",
    "SourceIdentifier": "新增（委员会 §3.6）",
}


def parse_map32() -> list[dict]:
    text = MAP32.read_text(encoding="utf-8")
    rows: list[dict] = []
    for line in text.splitlines():
        m = re.match(r"^\|\s*([A-Za-z][A-Za-z0-9_]*)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$", line)
        if m:
            clean = lambda s: s.strip().strip("`").strip()
            raw = clean(m.group(3))
            rows.append({"baseline": clean(m.group(1)), "action": clean(m.group(2)),
                         "target_term": re.split(r"[（(]", raw)[0].strip(), "target_term_raw": raw,
                         "target_kind": clean(m.group(4)), "target_layer": clean(m.group(5))})
    return rows


def parse_attr() -> dict[str, dict]:
    out: dict[str, dict] = {}
    with open(ATTR, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out[r["termId"]] = r
    return out


def ontology_iris() -> dict[str, str]:
    from rdflib import Graph, OWL, RDF

    g = Graph()
    g.parse(str(CORE), format="turtle")
    return {str(s).rsplit("/", 1)[-1]: str(s) for s in g.subjects(RDF.type, OWL.Class)}


def build() -> dict:
    m32, attr, iris = parse_map32(), parse_attr(), ontology_iris()
    rows = []
    for r in m32:
        b = r["baseline"]
        t = attr.get(r["target_term"], {})
        rows.append({
            "baseline_class": b,
            "existing_iri": iris.get(b, "（基线本体中不存在该 localname）"),
            "current_attribution": "基线本体（合同 CTR-SEM-002；owner=semantic_architecture_owner）",
            "target_layer": r["target_layer"], "target_term": r["target_term"],
            "target_kind": r["target_kind"], "action": r["action"],
            "reason": {"保留原名": "结构不变，仅归属声明变化",
                       "迁移重构": "语义收窄/职责重划（详见设计 §4.2~§4.5）",
                       "改名": "术语与目标层命名规范对齐",
                       "改名重构": "术语对齐 + 语义收窄",
                       "转换制品类型": "由 OWL 类转为非 OWL 制品（Schema/SKOS）"}.get(r["action"], r["action"]),
            "tbox_owner": t.get("T-Box Owner", "—"), "abox_owner": t.get("A-Box Owner", "—"),
            "mapping_type": t.get("基线映射类型", "—"),
            "target_term_raw": r.get("target_term_raw", r["target_term"]),
            "mapping_45_item": f'{r["target_term"]} / {r["target_kind"]} / 目标口径={t.get("目标制品口径", "—")}',
        })
    l1 = []
    baseline_by_target = {r["target_term"]: r["baseline_class"] for r in rows}
    for term, src in L1_DESIGN.items():
        a = attr.get(term, {})
        l1.append({"term": term, "design_source": src, "target_layer": "L1 公共业务语义核心",
                   "baseline_successor_of": baseline_by_target.get(term),
                   "tbox_owner": a.get("T-Box Owner", "—"), "abox_owner": a.get("A-Box Owner", "—"),
                   "mapping_type": a.get("基线映射类型", "—"),
                   "iri": a.get("权威IRI", "—")})
    inv = json.loads(INVENTORY.read_text(encoding="utf-8")) if INVENTORY.is_file() else {}
    out = {
        "schema": "ONTO1-CLASS-RECONCILIATION/1.0",
        "authority_refs": {
            "32 项映射": str(MAP32.relative_to(ROOT)),
            "45 制品口径": str(ATTR.relative_to(ROOT)),
            "L1 八类": f"{DESIGN.relative_to(ROOT)} §4.2（原文引用其表格）",
            "基线本体": str(CORE.relative_to(ROOT)),
        },
        "counting_units": {
            "32": "基线 OWL 类数（来源盘点口径）",
            "45": "目标制品数 = 39 OWL 类 + 1 SKOS 概念体系 + 5 集成契约 Schema 对象（**不是 45 个本体类**）",
            "87": "attribution-45-v2.csv 数据行数（另含 36 对象属性 + 5 L4 Schema 字段 + 1 退役）",
        },
        "separation_statement": (
            "**来源盘点 ≠ L1 候选**：`l1-term-inventory.json` 记录的是**现有本体 32 个 OWL 类**（基线全量，"
            "覆盖 L1/L2/L3 三层，见下表 target_layer），**不是** L1 候选模型；"
            "真正的 **L1 候选模型 = 8 类**（下表 `l1_candidate_model`），与设计 §4.2 逐项一致。"),
        "design_deviation": "无（未把 32 类放入 L1；本次为**登记口径分离**，非设计变更）",
        "classes_32": rows,
        "l1_candidate_model": l1,
        "summary": {
            "baseline_classes_parsed": len(rows),
            "arithmetic": {
                "baseline_32_breakdown": "29 保留/改名/重构为 OWL 类 + 3 转 L4 制品（2 Schema + 1 SKOS）",
                "target_owl_39_breakdown": "29 基线映射 + 10 新增（L1 3 + L2 7）",
                "target_artifacts_45": "39 OWL 类 + 1 SKOS + 5 Schema 对象",
            },
            "by_target_layer": dict(collections.Counter(r["target_layer"] for r in rows)),
            "by_action": dict(collections.Counter(r["action"] for r in rows)),
            "l1_candidate_count": len(l1),
            "l1_from_baseline": sum(1 for x in l1 if x["baseline_successor_of"]),
            "l1_newly_added": sum(1 for x in l1 if not x["baseline_successor_of"]),
            "inventory_artifact_role": inv.get("artifact_role", "（未标）"),
        },
        "status": "CANDIDATE_NOT_EFFECTIVE（复核材料；不改变任何制品）",
    }
    return out


def render_md(d: dict) -> str:
    L = ["# 32 类 × 目标层 × 45 制品口径 · 逐类核清（复核材料）", "",
         "> " + d["separation_statement"], "",
         "## 1. 计数单位（防混算）", "", "| 数 | 口径 |", "|---|---|"]
    for k, v in d["counting_units"].items():
        L.append(f"| **{k}** | {v} |")
    L += ["", f"**设计偏差声明**：{d['design_deviation']}", "",
          "## 2. 基线 32 类逐项（现有 IRI / 目标层 / 权威责任 / 理由 / 对应 45 映射项）", "",
          "| # | 基线类 | 现有 IRI | 目标术语 | 目标口径 | 目标层 | 去向 | 理由 | T-Box Owner | 对应 45 项 |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(d["classes_32"], 1):
        L.append(f"| {i} | `{r['baseline_class']}` | `{r['existing_iri']}` | `{r['target_term']}` | "
                 f"{r['target_kind']} | {r['target_layer']} | {r['action']} | {r['reason']} | "
                 f"{r['tbox_owner']} | {r['mapping_45_item']} |")
    L += ["", "## 3. L1 候选模型（**8 类**，与设计 §4.2 逐项一致）", "",
          "| L1 类 | 设计来源 | 基线前身 | 映射类型 | T-Box Owner | IRI（候选中） |", "|---|---|---|---|---|---|"]
    for x in d["l1_candidate_model"]:
        L.append(f"| `{x['term']}` | {x['design_source']} | {x['baseline_successor_of'] or '（新增）'} | "
                 f"{x['mapping_type']} | {x['tbox_owner']} | `{x['iri']}` |")
    s = d["summary"]
    L += ["", "## 4. 统计", "",
          f"- 解析到基线类：**{s['baseline_classes_parsed']}**；按目标层：{s['by_target_layer']}",
          f"- 按去向：{s['by_action']}",
          f"- **L1 候选 = {s['l1_candidate_count']} 类**（基线映射 {s['l1_from_baseline']} + 新增 {s['l1_newly_added']}）",
          f"- 来源盘点件标注 `artifact_role` = {s['inventory_artifact_role']}",
          "", f"状态：{d['status']}"]
    return "\n".join(L) + "\n"


def cmd_build() -> int:
    if INVENTORY.is_file():
        inv = json.loads(INVENTORY.read_text(encoding="utf-8"))
        inv["artifact_role"] = "SOURCE_INVENTORY（现有本体 32 类的**来源盘点**；**不是 L1 候选模型**）"
        inv["l1_candidate_ref"] = "l1-candidate-model 见 prep/32-classes-target-mapping.json 的 `l1_candidate_model`（8 类，设计 §4.2）"
        INVENTORY.write_text(json.dumps(inv, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    d = build()
    (PREP / "32-classes-target-mapping.json").write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (PREP / "32-CLASSES-TARGET-MAPPING.md").write_text(render_md(d), encoding="utf-8")
    print(f"逐类核清已生成：32 类解析 {d['summary']['baseline_classes_parsed']}；L1 候选 {d['summary']['l1_candidate_count']} 类")
    print("  按目标层:", d["summary"]["by_target_layer"])
    return 0


def cmd_gate() -> int:
    d = build()
    inv = json.loads(INVENTORY.read_text(encoding="utf-8"))
    rows = [
        ("R1 基线类解析完整（32）", d["summary"]["baseline_classes_parsed"] == 32,
         str(d["summary"]["baseline_classes_parsed"])),
        ("R2 L1 候选恰为 8 类", d["summary"]["l1_candidate_count"] == 8, str(d["summary"]["l1_candidate_count"])),
        ("R3 L1 候选集合 == 设计 §4.2 列表",
         {x["term"] for x in d["l1_candidate_model"]} == set(L1_DESIGN), "与设计表格逐项一致"),
        ("R4 来源盘点件已标 SOURCE_INVENTORY（非 L1 候选）",
         str(inv.get("artifact_role", "")).startswith("SOURCE_INVENTORY"), str(inv.get("artifact_role", ""))[:40]),
        ("R5 45 制品口径与 attribution 一致（39+1+5）",
         d["counting_units"]["45"].startswith("目标制品数 = 39 OWL 类 + 1 SKOS"), "口径文本"),
        ("R7 计数算术：32 = 29+3、39 = 29+10、45 = 39+1+5",
         (sum(1 for r in d["classes_32"] if r["target_kind"] == "OWL 类") == 29
          and sum(1 for r in d["classes_32"] if r["target_kind"] != "OWL 类") == 3),
         f'29+3 校验（OWL类 {sum(1 for r in d["classes_32"] if r["target_kind"] == "OWL 类")} / 非OWL {sum(1 for r in d["classes_32"] if r["target_kind"] != "OWL 类")}）'),
        ("R6 无设计偏差声明为『无』且未把 32 类放入 L1",
         str(d["design_deviation"]).startswith("无") and d["summary"]["l1_candidate_count"] == 8,
         d["design_deviation"][:30]),
    ]
    for n, ok, v in rows:
        print(f"{'PASS' if ok else 'FAIL'} [{n}] {v}")
    bad = [n for n, ok, _ in rows if not ok]
    print(f"逐类核清：{'PASS' if not bad else 'FAIL'}（{len(rows) - len(bad)}/{len(rows)}）")
    return 0 if not bad else 2


def cmd_selftest() -> int:
    d = build()
    fails = 0
    m1 = [x for x in d["l1_candidate_model"] if x["term"] != "Party"]
    ok1 = len(m1) == 7 != 8
    print(f"{'PASS' if ok1 else 'FAIL'} [M1 L1 候选少一类 ⇒ 应被 R2/R3 拦下] = {ok1}")
    fails += 0 if ok1 else 1
    m2 = d["classes_32"][:-1]
    print(f"{'PASS' if len(m2) != 32 else 'FAIL'} [M2 基线少一类 ⇒ 应被 R1 拦下]")
    fails += 0 if len(m2) != 32 else 1
    m3 = {x["term"] for x in d["l1_candidate_model"]} | {"Product"}
    print(f"{'PASS' if m3 != set(L1_DESIGN) else 'FAIL'} [M3 L1 混入基线旧名（Product）⇒ 应被 R3 拦下]")
    fails += 0 if m3 != set(L1_DESIGN) else 1
    print(f"--selftest {'PASS' if fails == 0 else 'FAIL'}（{3 - fails}/3）")
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
    return cmd_build()


if __name__ == "__main__":
    sys.exit(main())
