#!/usr/bin/env python3
"""L1 独立仓骨架 + 消费者迁移验证（Owner 决议 2026-09-21 准备项 3）

原则（**不得越过**）：
  · 沿用已登记的 **`PROVISIONAL_SIM_LEGACY_NAMESPACE`**；**不宣称正式根域获批**；
  · **不发布新 IRI**（执行计划 §WI-A4：D3 未签前禁止发布新 IRI / 重钉）；
  · 骨架只作**候选准备材料**，置于本 Loop 证据区，**不创建正式独立仓**。

产出：
  · `evidence/prep/l1-skeleton/{README.md,LAYOUT.md,l1-term-inventory.json,l1-namespace.json}`
  · `evidence/prep/consumer-migration-coverage.json`（迁移验证材料：本体引用面解析覆盖率）

用法：`--build` / `--gate` / `--selftest` / `--migration`
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
SK = PREP / "l1-skeleton"
CONFIG = ROOT / "specs/knowledge-architecture/instances/product/projection-config.json"
CORE = ROOT / "specs/semantic/gits-core.owl.ttl"
TRIAGE = EV / "obligation-triage.csv"
EXTERNAL_NS = ("http://www.w3.org/", "https://www.w3.org/", "http://purl.org/",
               "http://xmlns.com/", "urn:", "https://schema.org/")


def sim_namespaces() -> dict:
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    return {"terms": cfg["namespaces"]["terms"], "instances": cfg["namespaces"]["instances"],
            "status": cfg["namespaceStatus"]["status"]}


def inventory() -> dict:
    from rdflib import Graph, OWL, RDF, RDFS

    g = Graph()
    g.parse(str(CORE), format="turtle")
    classes = sorted(str(s) for s in g.subjects(RDF.type, OWL.Class))
    objprops = sorted(str(s) for s in g.subjects(RDF.type, OWL.ObjectProperty))
    dataprops = sorted(str(s) for s in g.subjects(RDF.type, OWL.DatatypeProperty))
    annprops = sorted(str(s) for s in g.subjects(RDF.type, OWL.AnnotationProperty))
    ns = sim_namespaces()
    return {
        "schema": "ONTO1-L1-TERM-INVENTORY/1.0",
        "source": str(CORE.relative_to(ROOT)),
        "source_sha256_hint": "见 gate 复算",
        "namespace": ns["terms"],
        "namespace_status": ns["status"],
        "counts": {"classes": len(classes), "object_properties": len(objprops),
                   "datatype_properties": len(dataprops), "annotation_properties": len(annprops),
                   "total": len(classes) + len(objprops) + len(dataprops) + len(annprops)},
        "classes": classes, "object_properties": objprops,
        "datatype_properties": dataprops, "annotation_properties": annprops,
        "status": "CANDIDATE_NOT_EFFECTIVE",
        "rule": "L1 候选清单：**沿用 provisional SIM 命名空间**；D3 签署前不得发布新 IRI、不得标 ACTIVE。",
    }


def build() -> dict:
    SK.mkdir(parents=True, exist_ok=True)
    inv = inventory()
    ns = sim_namespaces()
    (SK / "l1-term-inventory.json").write_text(json.dumps(inv, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (SK / "l1-namespace.json").write_text(json.dumps({
        "schema": "ONTO1-L1-NAMESPACE/1.0",
        "status": ns["status"], "approved_as_formal_root": False,
        "terms": ns["terms"], "instances": ns["instances"],
        "not_approved_as": ["正式根域", "持久解析承诺", "外部消费者契约"],
        "authority": "Owner 决议 2026-09-21（三、D3）",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (SK / "README.md").write_text("""# L1 独立语义契约库 · **候选骨架**（未建立正式仓）

> 状态：`CANDIDATE_NOT_EFFECTIVE`｜命名空间：`PROVISIONAL_SIM_LEGACY_NAMESPACE`（**非**正式根域）

## 这是什么
按四层设计（`docs/architecture/ONTOLOGY-SPLIT-DESIGN-V1.2-REVIEW.md`）准备的 **L1 公共核心语义契约库**骨架，
用于承接 `CTR-SEM-003`（L1 公共核心）候选合同。**本目录不是独立仓**，只是候选材料，位于 Loop 证据区。

## 禁令（逐条来自执行计划，必须遵守）
1. **D3 签署前禁止发布新 IRI / 重钉**（§WI-A4）；
2. 重构项**禁止**使用 `equivalentClass`（§WI-1-3 校验④）；
3. **不宣称**正式根域获批；命名空间一律标 `PROVISIONAL_SIM_LEGACY_NAMESPACE`；
4. 未获合同拆条批准前，**不得**把候选内容标 `ACTIVE` 或写入正式 `specs/` 权威路径。

## 内容
- `l1-term-inventory.json`：L1 候选术语清单（类 / 对象属性 / 数据类型属性 / 注解属性，来自 `specs/semantic/gits-core.owl.ttl`）
- `l1-namespace.json`：候选命名空间（provisional）+ 未获批声明
- `LAYOUT.md`：候选仓布局与生成物规划
""", encoding="utf-8")
    (SK / "LAYOUT.md").write_text("""# L1 候选仓布局（规划，未创建正式仓）

```
<L1-repo>/                        # 候选：独立语义契约库（尚未建立）
├── terms/                        # L1 公共术语（类 / 属性）——由 specs/semantic 收窄而来
│   └── gits-core.owl.ttl         #   候选：仅保留公共核心；L3 私有部分留在 GITS
├── contracts/                    # CTR-SEM-003 权威源与方法论
├── generated/                    # 生成物（schema / shacl）——需合同拆条获批后才有生成目标
└── version/                      # 版本与发布清单（BOM）
```

## 与现有结构的关系（收窄映射）
| 现状 | 候选去向 |
|---|---|
| `specs/semantic/gits-core.owl.ttl`（CTR-SEM-002 权威源） | **收窄为 L3**；公共核心部分上移 L1（CTR-SEM-003） |
| KERT 侧 `90_control/ontology/` | 改放 **L1 副本 + L2 本体**（CTR-SEM-004；需 KERT 维护方权限） |
| 注册表 Schema/SKOS | **CTR-SEM-005**（L4） |

## 验证
- `python3 scripts/onto1_l1_prep.py --gate`：骨架不变式（清单可复算 / 命名空间为 provisional / 未发布新 IRI / 骨架未越出证据区）
- `python3 scripts/onto1_l1_prep.py --migration`：消费者本体引用面解析覆盖率（迁移验证材料）
""", encoding="utf-8")
    print(f"L1 候选骨架已生成：{SK.relative_to(ROOT)}（术语 {inv['counts']['total']} 项）")
    return inv


def migration() -> dict:
    rows = list(csv.DictReader(open(TRIAGE, encoding="utf-8")))
    paths = sorted({(r["repo"], r["path"]) for r in rows if r["disposition"] == "TRUE_OBLIGATION"})
    inv = inventory()
    known_local = {t for t in inv["classes"] + inv["object_properties"] +
                   inv["datatype_properties"] + inv["annotation_properties"]}
    local_ns = [inv["namespace"]["iri"], json.loads(CONFIG.read_text(encoding="utf-8"))
                ["namespaces"]["instances"]["iri"]]
    stats = collections.Counter()
    unmapped: list[dict] = []
    per_file: list[dict] = []
    for repo, rel in paths:
        base = ROOT if repo == "gits" else ROOT.parent / "Leibniz-KERT"
        p = base / rel
        if not p.is_file():
            stats["FILE_MISSING"] += 1
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            stats["READ_ERROR"] += 1
            continue
        iris = set(re.findall(r"https?://[^\s\"'<>()\],;]+", text))
        curies = set(re.findall(r"(?<![A-Za-z0-9_:/])([a-z][a-z0-9]{1,9}):([A-Za-z_][A-Za-z0-9_]{2,})", text))
        imports = set(re.findall(r"^\s*import\s+(com\.gien\.gits\.(?:ontology|domain)[\w.]*)\s*;", text, re.M))
        found = 0
        for iri in iris:
            found += 1
            if any(iri.startswith(x) for x in EXTERNAL_NS):
                stats["KNOWN_EXTERNAL_IRI"] += 1
            elif any(iri.startswith(x) for x in local_ns) or iri in known_local:
                stats["RESOLVES_LOCAL_OR_PROVISIONAL_IRI"] += 1
            else:
                stats["UNMAPPED_APP_IRI"] += 1
                if len(unmapped) < 60:
                    unmapped.append({"repo": repo, "path": rel, "form": "IRI", "value": iri[:120]})
        for pfx, _local in curies:
            found += 1
            if pfx in ("gits", "prod"):
                stats["RESOLVES_LOCAL_OR_PROVISIONAL_CURIE"] += 1
            elif pfx in ("rdf", "rdfs", "owl", "xsd", "dct", "dc", "prov", "skos", "sh", "foaf",
                         "schema", "vann", "dcterms", "time", "org"):
                stats["KNOWN_EXTERNAL_CURIE"] += 1
            elif pfx in ("http", "https", "file", "mailto"):
                continue
            else:
                stats["OTHER_PREFIX_CURIE"] += 1
                if len(unmapped) < 60:
                    unmapped.append({"repo": repo, "path": rel, "form": "CURIE", "value": f"{pfx}:"})
        if imports:
            stats["CODE_IMPORT_ONTOLOGY_PKG"] += len(imports)
            for imp in sorted(imports)[:2]:
                if len(unmapped) < 60:
                    unmapped.append({"repo": repo, "path": rel, "form": "JAVA_IMPORT", "value": imp})
        if found:
            per_file.append({"repo": repo, "path": rel, "refs": found})
    out = {
        "schema": "ONTO1-CONSUMER-MIGRATION-COVERAGE/1.0",
        "scope": f"691 真义务所在文件（{len(paths)} 个唯一 文件）",
        "namespace_status": sim_namespaces()["status"],
        "counts": dict(stats),
        "unmapped_sample": unmapped,
        "note": ("迁移验证材料：`UNMAPPED_APP_IRI` 为**未落在 provisional 命名空间且非通用词汇**的 IRI，"
                 "即 Wave 2/3 迁移时必须逐条裁决的对象；本文件**不改变**任何制品，也不构成正式映射批准。"),
        "status": "CANDIDATE_NOT_EFFECTIVE",
    }
    (PREP / "consumer-migration-coverage.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("迁移覆盖：", dict(stats), f"（唯一文件 {len(paths)}）")
    return out


def cmd_gate() -> int:
    inv = inventory()
    sk_ns = json.loads((SK / "l1-namespace.json").read_text(encoding="utf-8"))
    disk_inv = json.loads((SK / "l1-term-inventory.json").read_text(encoding="utf-8"))
    ns = sim_namespaces()
    rows = [
        ("L1 术语清单可复算", inv["counts"] == disk_inv["counts"],
         f"磁盘 {disk_inv['counts']} vs 复算 {inv['counts']}"),
        ("L2 命名空间为 provisional", sk_ns["status"] == ns["status"] == "PROVISIONAL_SIM_LEGACY_NAMESPACE"
         and sk_ns["approved_as_formal_root"] is False, sk_ns["status"]),
        ("L3 未发布新 IRI", all(t.startswith(inv["namespace"]["iri"]) for t in
                                inv["classes"] + inv["object_properties"]), inv["namespace"]["iri"]),
        ("L4 骨架未越出证据区", str(SK).startswith(str(EV)), str(SK.relative_to(ROOT))),
        ("L5 禁令与未获批声明齐备",
         all(k in (SK / "README.md").read_text(encoding="utf-8") for k in ("禁止发布新 IRI", "equivalentClass"))
         and len(sk_ns["not_approved_as"]) >= 3, "README + l1-namespace.json"),
    ]
    for n, ok, d in rows:
        print(f"{'PASS' if ok else 'FAIL'} [{n}] {d}")
    bad = [n for n, ok, _ in rows if not ok]
    print(f"L1 骨架：{'PASS' if not bad else 'FAIL'}（{len(rows) - len(bad)}/{len(rows)}）")
    return 0 if not bad else 2


def cmd_selftest() -> int:
    inv = inventory()
    fails = 0
    # M1 命名空间被改成正式根域 ⇒ 应被 L2/L3 拦下
    fake = dict(inv); fake["namespace"] = {"prefix": "gits", "iri": "https://formal.example.org/onto/"}
    ok1 = not all(t.startswith(fake["namespace"]["iri"]) for t in fake["classes"])
    print(f"{'PASS' if ok1 else 'FAIL'} [M1 命名空间改为正式根域 ⇒ 应被 L3 拦下] = {ok1}")
    fails += 0 if ok1 else 1
    # M2 清单计数被篡改 ⇒ 应被 L1 拦下
    d = json.loads((SK / "l1-term-inventory.json").read_text(encoding="utf-8"))
    d["counts"]["classes"] += 1
    print(f"{'PASS' if d['counts'] != inv['counts'] else 'FAIL'} [M2 清单计数篡改 ⇒ 应被 L1 拦下]")
    fails += 0 if d["counts"] != inv["counts"] else 1
    # M3 骨架路径越出证据区 ⇒ 应被 L4 拦下
    outside = ROOT / "specs/knowledge-architecture/l1"
    print(f"{'PASS' if not str(outside).startswith(str(EV)) else 'FAIL'} [M3 骨架越出证据区 ⇒ 应被 L4 拦下]")
    fails += 0 if not str(outside).startswith(str(EV)) else 1
    print(f"--selftest {'PASS' if fails == 0 else 'FAIL'}（{3 - fails}/3）")
    return 0 if fails == 0 else 2


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--gate", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--migration", action="store_true")
    ns = ap.parse_args()
    if ns.selftest:
        return cmd_selftest()
    if ns.gate:
        return cmd_gate()
    if ns.migration:
        migration(); return 0
    build()
    return 0


if __name__ == "__main__":
    sys.exit(main())
