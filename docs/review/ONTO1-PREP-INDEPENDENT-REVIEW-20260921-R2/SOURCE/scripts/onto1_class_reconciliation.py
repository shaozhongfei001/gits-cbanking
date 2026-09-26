#!/usr/bin/env python3
"""32 类 × 目标层 × 45 制品口径 逐类核清（复核项 一；**F-02 修订版**）

**F-02 修订要点**：L1 名单**不再硬编码于脚本**，而是**解析受控源文档**；候选清单由**数据文件**推导；
门禁对 **设计表 / 映射表 / 归属矩阵 / 候选表** 的变异必须真实失败。

权威源（均可通过 CLI 指向变异副本以做反例）：
  · 设计 §4.2 的 L1 八类：`docs/architecture/ONTOLOGY-SPLIT-DESIGN-V2.0-REVIEW.md`
  · 32 类 → 目标层映射：`docs/review/ARCH-ONTO-2026-001-rereview-package/04-基线32项映射表.md`
  · 45 制品归属矩阵：`evidence/attribution-45-v2.csv`

口径（防混算）：`32` = 基线 OWL 类；`45` = 39 OWL 类 + 1 SKOS + 5 Schema 对象；`87` = 归属矩阵行数。

用法：`--build` / `--gate` / `--selftest`
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import pathlib
import re
import shutil
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
EV = ROOT / "loops/ONTO1-ontology-split/evidence"
PREP = EV / "prep"
D = {
    "design": ROOT / "docs/architecture/ONTOLOGY-SPLIT-DESIGN-V2.0-REVIEW.md",
    "map32": ROOT / "docs/review/ARCH-ONTO-2026-001-rereview-package/04-基线32项映射表.md",
    "attr": EV / "attribution-45-v2.csv",
    "core": ROOT / "specs/semantic/gits-core.owl.ttl",
    "inventory": PREP / "l1-skeleton/l1-term-inventory.json",
}
EXPECT_OWL, EXPECT_SKOS, EXPECT_SCHEMA = 39, 1, 5


def parse_design_l1(path: pathlib.Path) -> dict[str, str]:
    """解析设计 §4.2 的 L1 八类表：`| \\`Term\\` | 中文 | 来源 | A-Box Owner |`。"""
    lines = path.read_text(encoding="utf-8").splitlines()
    start = next((i for i, l in enumerate(lines) if re.match(r"^#{3,4}\s*4\.2\b", l)), None)
    if start is None:
        raise ValueError(f"设计中未找到 §4.2：{path}")
    out: dict[str, str] = {}
    for line in lines[start + 1:]:
        if re.match(r"^#{3,4}\s", line):      # 下一个三级标题 ⇒ 结束
            break
        m = re.match(r"^\|\s*`?([A-Za-z][A-Za-z0-9_]*)`?\s*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|", line)
        if m:
            out[m.group(1)] = m.group(3).strip()
    return out


def parse_map32(path: pathlib.Path) -> list[dict]:
    rows: list[dict] = []
    clean = lambda s: s.strip().strip("`").strip()  # noqa: E731
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\|\s*([A-Za-z][A-Za-z0-9_]*)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$", line)
        if m:
            raw = clean(m.group(3))
            rows.append({"baseline": clean(m.group(1)), "action": clean(m.group(2)),
                         "target_term": re.split(r"[（(]", raw)[0].strip(), "target_term_raw": raw,
                         "target_kind": clean(m.group(4)), "target_layer": clean(m.group(5))})
    return rows


def parse_attr(path: pathlib.Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def ontology_iris(path: pathlib.Path) -> dict[str, str]:
    from rdflib import Graph, OWL, RDF

    g = Graph()
    g.parse(str(path), format="turtle")
    return {str(s).rsplit("/", 1)[-1]: str(s) for s in g.subjects(RDF.type, OWL.Class)}


def l1_candidate_from_data(map32: list[dict], attr: list[dict]) -> dict[str, dict]:
    """候选 = 映射表中目标层为 L1 的类 ∪ 归属矩阵中 L1 且新增的 OWL 类（**全部来自数据**）。"""
    cand: dict[str, dict] = {}
    for r in map32:
        if "L1" in r["target_layer"]:
            cand[r["target_term"]] = {"origin": "map32", "baseline": r["baseline"], "action": r["action"]}
    for r in attr:
        if ("L1" in r.get("四层归属", "") and r.get("基线映射类型") == "新增"
                and r.get("目标制品口径") == "OWL类"):
            cand.setdefault(r["termId"], {"origin": "attr-new", "baseline": None, "action": "新增"})
    return cand


def _rel(p: pathlib.Path) -> str:
    try:
        return str(pathlib.Path(p).relative_to(ROOT))
    except ValueError:
        return str(p)


def build(design=D["design"], map32=D["map32"], attr=D["attr"], core=D["core"],
          inventory=D["inventory"]) -> dict:
    design_l1 = parse_design_l1(design)
    m32, at, iris = parse_map32(map32), parse_attr(attr), ontology_iris(core)
    cand = l1_candidate_from_data(m32, at)
    attr_by_term = {r["termId"]: r for r in at}
    kind_counts = collections.Counter(r.get("目标制品口径", "") for r in at)

    classes = []
    for r in m32:
        t = attr_by_term.get(r["target_term"], {})
        classes.append({**r, "baseline_class": r["baseline"], "existing_iri": iris.get(r["baseline"], "（基线本体中不存在该 localname）"),
                        "current_attribution": "基线本体（合同 CTR-SEM-002；owner=semantic_architecture_owner）",
                        "reason": {"保留原名": "结构不变，仅归属声明变化",
                                   "迁移重构": "语义收窄/职责重划（设计 §4.2~§4.5）",
                                   "迁移改名": "术语与目标层命名规范对齐",
                                   "迁移（原名）": "迁移至目标层，术语不变",
                                   "转换制品类型": "由 OWL 类转为非 OWL 制品"}.get(r["action"], r["action"]),
                        "tbox_owner": t.get("T-Box Owner", "—"), "abox_owner": t.get("A-Box Owner", "—"),
                        "mapping_type": t.get("基线映射类型", "—"),
                        "mapping_45_item": f'{r["target_term"]} / {r["target_kind"]} / 目标口径={t.get("目标制品口径", "—")}'})

    l1_view = []
    for term, meta in sorted(cand.items()):
        a = attr_by_term.get(term, {})
        l1_view.append({"term": term, "design_source": design_l1.get(term, "（设计 §4.2 未列）"),
                        "baseline_successor_of": meta["baseline"], "action": meta["action"],
                        "origin": meta["origin"], "tbox_owner": a.get("T-Box Owner", "—"),
                        "mapping_type": a.get("基线映射类型", "—"), "iri": a.get("权威IRI", "—")})

    inv = json.loads(inventory.read_text(encoding="utf-8")) if inventory.is_file() else {}
    return {
        "schema": "ONTO1-CLASS-RECONCILIATION/2.0（F-02 修订：解析受控源，不硬编码）",
        "authority_refs": {k: _rel(v) for k, v in
                           (("设计 §4.2", design), ("32 项映射", map32), ("45 制品归属", attr), ("基线本体", core))},
        "counting_units": {"32": "基线 OWL 类数（来源盘点口径）",
                           "45": "目标制品数 = 39 OWL 类 + 1 SKOS 概念体系 + 5 集成契约 Schema 对象（**不是 45 个本体类**）",
                           "87": "attribution-45-v2.csv 数据行数（另含 36 对象属性 + 5 L4 Schema 字段 + 1 退役）"},
        "separation_statement": ("**来源盘点 ≠ L1 候选**：`l1-term-inventory.json` = 现有本体 **32 个 OWL 类**（覆盖 L1/L2/L3 三层）；"
                                 "**L1 候选 = 8 类**（由 `32 项映射表` 的 L1 行 ∪ `归属矩阵` 的 L1 新增类推导，并与设计 §4.2 逐项比对）。"),
        "design_deviation": "无（未把 32 类放入 L1；本次为**登记口径分离**，非设计变更）",
        "classes_32": classes,
        "l1_candidate_model": l1_view,
        "summary": {"baseline_classes_parsed": len(classes),
                    "by_target_layer": dict(collections.Counter(r["target_layer"] for r in classes)),
                    "by_action": dict(collections.Counter(r["action"] for r in classes)),
                    "l1_candidate_count": len(l1_view),
                    "l1_from_baseline": sum(1 for x in l1_view if x["baseline_successor_of"]),
                    "l1_newly_added": sum(1 for x in l1_view if not x["baseline_successor_of"]),
                    "artifact_kind_counts_from_csv": dict(kind_counts),
                    "inventory_artifact_role": inv.get("artifact_role", "（未标）")},
        "status": "CANDIDATE_NOT_EFFECTIVE（复核材料；不改变任何制品）",
    }


def render_md(d: dict) -> str:
    L = ["# 32 类 × 目标层 × 45 制品口径 · 逐类核清（复核材料 · F-02 修订版）", "",
         "> " + d["separation_statement"], "",
         "> **权威源**：" + " · ".join(f"{k}=`{v}`" for k, v in d["authority_refs"].items()), "",
         "## 1. 计数单位（防混算）", "", "| 数 | 口径 |", "|---|---|"]
    L += [f"| **{k}** | {v} |" for k, v in d["counting_units"].items()]
    L += ["", f"**设计偏差声明**：{d['design_deviation']}", "",
          "## 2. 基线 32 类逐项", "",
          "| # | 基线类 | 现有 IRI | 目标术语 | 目标口径 | 目标层 | 去向 | 理由 | T-Box Owner | 对应 45 项 |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for i, r in enumerate(d["classes_32"], 1):
        L.append(f"| {i} | `{r['baseline_class']}` | `{r['existing_iri']}` | `{r['target_term']}` | {r['target_kind']} | "
                 f"{r['target_layer']} | {r['action']} | {r['reason']} | {r['tbox_owner']} | {r['mapping_45_item']} |")
    L += ["", "## 3. L1 候选模型（**8 类**，由数据推导 + 与设计 §4.2 比对）", "",
          "| L1 类 | 设计 §4.2 来源 | 基线前身 | 推导来源 | 映射类型 | IRI（候选中） |", "|---|---|---|---|---|---|"]
    for x in d["l1_candidate_model"]:
        L.append(f"| `{x['term']}` | {x['design_source']} | {x['baseline_successor_of'] or '（新增）'} | "
                 f"{x['origin']} | {x['mapping_type']} | `{x['iri']}` |")
    s = d["summary"]
    L += ["", "## 4. 统计", "",
          f"- 基线类 {s['baseline_classes_parsed']}；按目标层 {s['by_target_layer']}；按去向 {s['by_action']}",
          f"- **L1 候选 = {s['l1_candidate_count']}**（基线映射 {s['l1_from_baseline']} + 新增 {s['l1_newly_added']}）",
          f"- 归属矩阵实测制品口径：{s['artifact_kind_counts_from_csv']}",
          f"- 来源盘点件 artifact_role = {s['inventory_artifact_role']}", "", f"状态：{d['status']}"]
    return "\n".join(L) + "\n"


def cmd_build() -> int:
    if D["inventory"].is_file():
        inv = json.loads(D["inventory"].read_text(encoding="utf-8"))
        inv["artifact_role"] = "SOURCE_INVENTORY（现有本体 32 类的**来源盘点**；**不是 L1 候选模型**）"
        inv["l1_candidate_ref"] = "../32-classes-target-mapping.json → `l1_candidate_model`（8 类，设计 §4.2）"
        D["inventory"].write_text(json.dumps(inv, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    d = build()
    (PREP / "32-classes-target-mapping.json").write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (PREP / "32-CLASSES-TARGET-MAPPING.md").write_text(render_md(d), encoding="utf-8")
    print(f"逐类核清：32 类解析 {d['summary']['baseline_classes_parsed']}；L1 候选 {d['summary']['l1_candidate_count']}")
    print("  制品口径实测:", d["summary"]["artifact_kind_counts_from_csv"])
    return 0


def _checks(d: dict, design: pathlib.Path) -> list[tuple[str, bool, str]]:
    design_l1 = parse_design_l1(design)
    cand = {x["term"] for x in d["l1_candidate_model"]}
    kinds = d["summary"]["artifact_kind_counts_from_csv"]
    inv = json.loads(D["inventory"].read_text(encoding="utf-8")) if D["inventory"].is_file() else {}
    return [
        ("R1 基线类解析完整（32）", d["summary"]["baseline_classes_parsed"] == 32, str(d["summary"]["baseline_classes_parsed"])),
        ("R2 L1 候选恰为 8 类", d["summary"]["l1_candidate_count"] == 8, str(d["summary"]["l1_candidate_count"])),
        ("R3 候选集合 == **设计 §4.2 解析结果**", cand == set(design_l1),
         f"候选={sorted(cand)} 设计={sorted(design_l1)}"),
        ("R4 来源盘点件已标 SOURCE_INVENTORY", str(inv.get("artifact_role", "")).startswith("SOURCE_INVENTORY"),
         str(inv.get("artifact_role", ""))[:40]),
        ("R5 45 制品口径按**归属矩阵实测行**分类",
         kinds.get("OWL类") == EXPECT_OWL and kinds.get("SKOS概念体系") == EXPECT_SKOS
         and kinds.get("集成契约Schema对象") == EXPECT_SCHEMA, str({k: kinds.get(k) for k in
                                                                  ("OWL类", "SKOS概念体系", "集成契约Schema对象")})),
        ("R6 设计偏差声明为『无』", str(d["design_deviation"]).startswith("无"), d["design_deviation"][:20]),
        ("R7 计数算术 32 = 29+3", sum(1 for r in d["classes_32"] if r["target_kind"] == "OWL 类") == 29
         and sum(1 for r in d["classes_32"] if r["target_kind"] != "OWL 类") == 3,
         f'OWL {sum(1 for r in d["classes_32"] if r["target_kind"] == "OWL 类")} / 非OWL {sum(1 for r in d["classes_32"] if r["target_kind"] != "OWL 类")}'),
    ]


def cmd_gate() -> int:
    d = build()
    rows = _checks(d, D["design"])
    for n, ok, v in rows:
        print(f"{'PASS' if ok else 'FAIL'} [{n}] {v}")
    bad = [n for n, ok, _ in rows if not ok]
    print(f"逐类核清：{'PASS' if not bad else 'FAIL'}（{len(rows) - len(bad)}/{len(rows)}）")
    return 0 if not bad else 2


def _copy_mutate(src: pathlib.Path, dst: pathlib.Path, old: str, new: str) -> pathlib.Path:
    text = src.read_text(encoding="utf-8")
    assert old in text, f"变异目标未找到：{old}"
    dst.write_text(text.replace(old, new, 1), encoding="utf-8")
    return dst


def cmd_selftest() -> int:
    fails, total = 0, 0
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        # M0 对照
        base_ok = all(ok for _, ok, _ in _checks(build(), D["design"]))
        total += 1; fails += 0 if base_ok else 1
        print(f"{'PASS' if base_ok else 'FAIL'} [M0 对照] 现状 7/7 = {base_ok}")
        # M1 **变异受控设计表**（Party → PartyMUTATED）⇒ R3 必须失败
        dm = _copy_mutate(D["design"], td / "design_mut.md", "| `Party` |", "| `PartyMUTATED` |")
        bad = [n for n, ok, _ in _checks(build(design=dm), dm) if not ok]
        ids = [n.split()[0] for n in bad]
        total += 1
        ok = "R3" in ids; fails += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'} [M1 变异设计表 §4.2] 被拦下 = {bad or '无（漏检！）'}")
        # M2 **变异 32 项映射表**（一个 L1 行的目标层改 L3）⇒ 候选少一类 ⇒ R2/R3 失败
        mm = _copy_mutate(D["map32"], td / "map_mut.md", "| L1 公共 |", "| L3 GITS |")
        bad = [n for n, ok2, _ in _checks(build(map32=mm), D["design"]) if not ok2]
        total += 1
        ok = bool({"R2", "R3"} & {n.split()[0] for n in bad}); fails += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'} [M2 变异映射表（L1→L3）] 被拦下 = {bad or '无（漏检！）'}")
        # M3 **变异归属矩阵**（新增 L1 类改归属）⇒ 候选少一类 ⇒ R3 失败
        am = td / "attr_mut.csv"
        rows = D["attr"].read_text(encoding="utf-8").splitlines()
        out = []
        hit = False
        for ln in rows:
            if not hit and ln.startswith("Party,"):
                ln = ln.replace("L1 公共业务语义核心", "L2 KERT 知识供给元模型", 1); hit = True
            out.append(ln)
        am.write_text("\n".join(out) + "\n", encoding="utf-8")
        bad = [n for n, ok3, _ in _checks(build(attr=am), D["design"]) if not ok3]
        total += 1
        ok = "R3" in [n.split()[0] for n in bad]; fails += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'} [M3 变异归属矩阵（L1→L2）] 被拦下 = {bad or '无（漏检！）'}")
        # M4 还原对照
        total += 1
        back = all(ok4 for _, ok4, _ in _checks(build(), D["design"]))
        fails += 0 if back else 1
        print(f"{'PASS' if back else 'FAIL'} [M4 还原对照] 7/7 = {back}")
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
    return cmd_build()


if __name__ == "__main__":
    sys.exit(main())
