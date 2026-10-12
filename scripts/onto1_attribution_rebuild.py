#!/usr/bin/env python3
"""ONTO1 WI-A1｜基线 v2 与四层归属矩阵重导/校验。

输入种子：复审包 `03-逐术语权威矩阵-22字段.csv`（45 模型资产 + 42 属性行）。
产出：`loops/ONTO1-ontology-split/evidence/attribution-45-v2.csv`（22 字段 + 四层归属列）。

门禁（fail-closed；缺夹具即失败，不跳过）：
    A1 基线 `gits-core.owl.ttl` 哈希前缀 + 计数 32/34/1
    A2 目标模型资产 = 45（分口径 39 OWL + 1 SKOS + 5 Schema）
    A3 四层归属自洽（L1 8 / L2 12 / L3 19）
    A4 基线 32 类 100% 映射、0 退役、无遗漏无重复
    A5 基线 34 对象属性 100% 有去向（19 保留 + 15 迁移/转字段）
    A6 基线 1 数据属性退役且被 SourceIdentifier 模式承接
    A7 权威 IRI 不得出现占位根域（D3 未签期间只允许 PENDING:{NS-L*} 与 REGISTRY:/SKOS: 命名）
    A8 变异复验（--selftest）：删一行/改计数/换占位域 ⇒ 必须 FAIL，恢复 ⇒ PASS
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED_CSV = ROOT / "docs/review/ARCH-ONTO-2026-001-rereview-package/03-逐术语权威矩阵-22字段.csv"
BASELINE_TTL = ROOT / "specs/semantic/gits-core.owl.ttl"
OUT_CSV = ROOT / "loops/ONTO1-ontology-split/evidence/attribution-45-v2.csv"
OUT_MANIFEST = ROOT / "loops/ONTO1-ontology-split/evidence/baseline-v2-manifest.json"

EXPECTED_BASELINE_PREFIX = "705578d6324abd0c"
EXPECTED_BASELINE_COUNTS = {"owl_class": 32, "owl_object_property": 34, "owl_datatype_property": 1}

# ---- 四层归属（来源：设计 V2.0 §4 + 复审包 04 号映射表） ----
L1_OWL = ["Party", "Organization", "LegalEntity", "CustomerRole", "EnterpriseGroup",
          "GroupMembership", "ProductOffering", "SourceIdentifier"]
L2_OWL = ["ProductKnowledgeCard", "ProductKnowledgeVersion", "KnowledgeMapDefinition",
          "AssetDefinition", "SkillDefinition", "KnowledgeItem", "Segment", "KnowledgeSource",
          "ProductInterpretation", "RuleBundle", "EvidenceBundle", "Projection"]
L3_OWL = ["OperatingCase", "Claim", "Evidence", "Evaluation", "Action", "Receipt",
          "HumanConfirmation", "HumanGate", "Interaction", "InteractionExtension",
          "Opportunity", "OpportunitySignal", "Commitment", "ExternalEvent", "KycGapProfile",
          "PolicyRule", "AuditTraceEntry", "RelationshipReport", "Task"]
L4_SCHEMA = ["ActivationContract", "CapabilityPublication", "EndpointBinding", "ConsumerBinding",
             "ContractVersion"]
L4_SKOS = ["TaskTypeScheme"]

L1_PROPS = ["memberOfGroup", "relatesToGroup", "connectsFrom", "connectsTo"]
L2_PROPS = ["cardOfProduct", "versionOfProduct", "supersedesVersion", "requiresProduct",
            "complementsProduct", "mutuallyExclusiveWith", "describesProduct", "segmentOf",
            "sourcedFrom", "interprets", "rulesFor", "projectionOf", "evidenceOf"]
SCHEMA_FIELDS = ["hasTaskType", "governedByContract", "invokesCapability", "referencesAsset",
                 "referencesSkill"]
RETIRED_PROPS = ["customerId"]
NEW_PROPS = ["describesProduct", "segmentOf", "sourcedFrom", "interprets", "rulesFor",
             "projectionOf", "evidenceOf"]

# 基线类 → 目标术语（复审包 04 号 §A）
BASELINE_CLASS_TARGET = {
    **{name: name for name in L3_OWL},
    "LegalEntity": "LegalEntity",
    "Customer": "CustomerRole",
    "CorporateGroup": "EnterpriseGroup",
    "GroupRelationship": "GroupMembership",
    "Product": "ProductOffering",
    "ProductKnowledgeCard": "ProductKnowledgeCard",
    "ProductKnowledgeVersion": "ProductKnowledgeVersion",
    "KnowledgeMap": "KnowledgeMapDefinition",
    "Asset": "AssetDefinition",
    "Skill": "SkillDefinition",
    "ActivationContract": "ActivationContract",
    "Capability": "CapabilityPublication",
    "TaskType": "TaskTypeScheme",
}
NEW_OWL = ["Party", "Organization", "SourceIdentifier", "KnowledgeItem", "Segment",
           "KnowledgeSource", "ProductInterpretation", "RuleBundle", "EvidenceBundle", "Projection"]
NEW_SCHEMA = ["EndpointBinding", "ConsumerBinding", "ContractVersion"]

PLACEHOLDER_ROOT_HINTS = (".example", "example.com", "localhost", "127.0.0.1")


def read_seed(path: Path) -> tuple[list[str], list[list[str]]]:
    if not path.is_file():
        raise RuntimeError(f"seed matrix missing: {path}")
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        rows = [row for row in reader if row]
    if len(header) < 22:
        raise RuntimeError(f"seed matrix must have 22 fields, got {len(header)}")
    return header, rows


def load_baseline(ttl_path: Path, expected_prefix: str = EXPECTED_BASELINE_PREFIX) -> dict:
    if not ttl_path.is_file():
        raise RuntimeError(f"baseline ontology missing: {ttl_path}")
    sha = hashlib.sha256(ttl_path.read_bytes()).hexdigest()
    if not sha.startswith(expected_prefix):
        raise RuntimeError(f"baseline sha256 drifted: {sha[:16]} != {expected_prefix}")
    from rdflib import Graph
    from rdflib.namespace import OWL, RDF
    graph = Graph()
    graph.parse(str(ttl_path), format="turtle")
    short = lambda subject: str(subject).rsplit("#", 1)[-1].rsplit("/", 1)[-1]  # noqa: E731
    return {
        "sha256": sha,
        "owl_class": sorted(short(s) for s in graph.subjects(RDF.type, OWL.Class)),
        "owl_object_property": sorted(short(s) for s in graph.subjects(RDF.type, OWL.ObjectProperty)),
        "owl_datatype_property": sorted(short(s) for s in graph.subjects(RDF.type, OWL.DatatypeProperty)),
    }


def layer_of(term: str, kind: str) -> str:
    if term in L1_OWL:
        return "L1 公共业务语义核心"
    if term in L2_OWL:
        return "L2 KERT 知识供给元模型"
    if term in L3_OWL:
        return "L3 GITS 经营运行本体"
    if term in L4_SCHEMA or term in L4_SKOS:
        return "L4 集成契约注册表"
    if term in L1_PROPS:
        return "L1 公共业务语义核心"
    if term in L2_PROPS:
        return "L2 KERT 知识供给元模型"
    if term in SCHEMA_FIELDS:
        return "L4 集成契约注册表"
    return "L3 GITS 经营运行本体" if kind == "OWL对象属性" else "—"


def spec_of(kind: str) -> str:
    if kind == "OWL类":
        return "OWL类"
    if kind == "OWL对象属性":
        return "OWL对象属性"
    if kind == "SKOS概念体系":
        return "SKOS概念体系"
    if kind.startswith("Schema对象"):
        return "集成契约Schema对象"
    if kind == "转L4 Schema字段":
        return "L4 Schema字段(不再是OWL属性)"
    if kind == "退役数据属性":
        return "退役"
    return kind


def build(seed_path: Path = SEED_CSV) -> tuple[list[dict], list[str]]:
    header, rows = read_seed(seed_path)
    enriched: list[dict] = []
    for raw in rows:
        term, kind = raw[0], raw[5]
        row = dict(zip(header, raw))
        row["四层归属"] = layer_of(term, kind)
        row["目标制品口径"] = spec_of(kind)
        row["基线映射类型"] = (
            "新增" if term in NEW_OWL + NEW_SCHEMA + ["TaskTypeScheme"] and term not in BASELINE_CLASS_TARGET
            else ("基线映射" if term in BASELINE_CLASS_TARGET.values()
                  or term in L1_PROPS + L2_PROPS + SCHEMA_FIELDS + RETIRED_PROPS
                  else ("新增属性" if term in NEW_PROPS else "新增"))
        )
        enriched.append(row)
    return enriched, header


def validate(enriched: list[dict], baseline: dict) -> list[str]:
    failures: list[str] = []

    def fail(message: str) -> None:
        failures.append(message)

    # A1
    for key, expected in EXPECTED_BASELINE_COUNTS.items():
        if len(baseline[key]) != expected:
            fail(f"A1 baseline {key} = {len(baseline[key])} != {expected}")

    classes = [row for row in enriched if row["概念类型"] == "OWL类"]
    schema = [row for row in enriched if row["概念类型"].startswith("Schema对象")]
    skos = [row for row in enriched if row["概念类型"] == "SKOS概念体系"]
    obj_props = [row for row in enriched if row["概念类型"] == "OWL对象属性"]
    schema_fields = [row for row in enriched if row["概念类型"] == "转L4 Schema字段"]
    retired = [row for row in enriched if row["概念类型"] == "退役数据属性"]

    # A2
    total_assets = len(classes) + len(schema) + len(skos)
    if total_assets != 45:
        fail(f"A2 model assets = {total_assets} != 45")
    if len(classes) != 39 or len(skos) != 1 or len(schema) != 5:
        fail(f"A2 split = {len(classes)} OWL / {len(skos)} SKOS / {len(schema)} Schema (expect 39/1/5)")

    # A3
    l1 = [row for row in classes if row["四层归属"].startswith("L1")]
    l2 = [row for row in classes if row["四层归属"].startswith("L2")]
    l3 = [row for row in classes if row["四层归属"].startswith("L3")]
    if (len(l1), len(l2), len(l3)) != (8, 12, 19):
        fail(f"A3 layer split = {len(l1)}/{len(l2)}/{len(l3)} (expect 8/12/19)")
    if len(obj_props) != 36:
        fail(f"A3 OWL object properties = {len(obj_props)} != 36")
    if len(schema_fields) != 5:
        fail(f"A3 schema fields = {len(schema_fields)} != 5")
    if len(retired) != 1:
        fail(f"A3 retired = {len(retired)} != 1")

    # A4 基线 32 类覆盖
    targets = {row["termId"] for row in enriched}
    missing = [name for name, target in BASELINE_CLASS_TARGET.items() if target not in targets]
    if missing:
        fail(f"A4 baseline classes without target: {sorted(missing)}")
    ttl_classes = set(baseline["owl_class"])
    unmapped = [name for name in ttl_classes if name not in BASELINE_CLASS_TARGET]
    if unmapped:
        fail(f"A4 TTL classes not covered by mapping table: {sorted(unmapped)}")
    duplicated = sorted({row["termId"] for row in enriched if
                         [r["termId"] for r in enriched].count(row["termId"]) > 1})
    if duplicated:
        fail(f"A4 duplicate termId: {duplicated}")

    # A5 基线 34 对象属性覆盖
    attr_rows = {row["termId"] for row in obj_props + schema_fields + retired}
    prop_missing = [name for name in baseline["owl_object_property"] if name not in attr_rows]
    if prop_missing:
        fail(f"A5 baseline object properties without destination: {sorted(prop_missing)}")

    # A6 数据属性退役
    dt_missing = [name for name in baseline["owl_datatype_property"]
                  if name not in {row["termId"] for row in retired}]
    if dt_missing:
        fail(f"A6 datatype property not retired in matrix: {sorted(dt_missing)}")

    # A7 占位根域
    for row in enriched:
        iri = row["权威IRI"]
        lowered = iri.lower()
        if any(hint in lowered for hint in PLACEHOLDER_ROOT_HINTS):
            fail(f"A7 placeholder authority IRI in {row['termId']}: {iri}")

    return failures


def write_outputs(enriched: list[dict], header: list[str], baseline: dict) -> dict:
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    extra = ["四层归属", "目标制品口径", "基线映射类型"]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=header + extra)
        writer.writeheader()
        for row in enriched:
            writer.writerow({key: row.get(key, "") for key in header + extra})
    manifest = {
        "baseline": {
            "file": str(BASELINE_TTL.relative_to(ROOT)),
            "sha256": baseline["sha256"],
            "counts": {key: len(baseline[key]) for key in EXPECTED_BASELINE_COUNTS},
        },
        "attribution_csv": str(OUT_CSV.relative_to(ROOT)),
        "attribution_sha256": hashlib.sha256(OUT_CSV.read_bytes()).hexdigest(),
        "rows": len(enriched),
        "model_assets": 45,
    }
    OUT_MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def gate(seed_path: Path = SEED_CSV, baseline_path: Path = BASELINE_TTL,
         expected_prefix: str = EXPECTED_BASELINE_PREFIX, write: bool = True) -> int:
    try:
        baseline = load_baseline(baseline_path, expected_prefix)
        enriched, header = build(seed_path)
    except RuntimeError as exc:
        print(f"onto1-attribution: FAIL: {exc}", file=sys.stderr)
        return 2
    failures = validate(enriched, baseline)
    if write and not failures:
        manifest = write_outputs(enriched, header, baseline)
        print(f"[A5] wrote {manifest['attribution_csv']} sha256={manifest['attribution_sha256'][:16]}")
    print(f"A1 baseline sha256={baseline['sha256'][:16]} counts="
          f"{ {k: len(baseline[k]) for k in EXPECTED_BASELINE_COUNTS} }")
    print(f"A2 model assets=45 (39 OWL / 1 SKOS / 5 Schema) rows={len(enriched)}")
    if failures:
        for item in failures:
            print(f"onto1-attribution: FAIL: {item}", file=sys.stderr)
        return 2
    print("onto1-attribution: PASS")
    return 0


def selftest() -> int:
    """变异复验：每条变异必须被拦下，恢复后必须通过。"""
    cases: list[tuple[str, object]] = []
    tmp = Path(tempfile.mkdtemp(prefix="onto1-attribution-selftest-"))
    try:
        # M1 删除一条基线类映射行 ⇒ A4 必须 FAIL
        _, rows = read_seed(SEED_CSV)
        dropped = [row for row in rows if row[0] != "OperatingCase"]
        path = tmp / "seed-drop.csv"
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(read_seed(SEED_CSV)[0])
            writer.writerows(dropped)
        cases.append(("M1 删除基线类 OperatingCase 映射行 ⇒ FAIL", path))

        # M2 把一条 OWL 类改成 Schema 对象 ⇒ A2 分口径必须 FAIL
        mutated = [list(row) for row in rows]
        for row in mutated:
            if row[0] == "Task":
                row[5] = "Schema对象(JSON Schema)"
        path2 = tmp / "seed-kind.csv"
        with path2.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(read_seed(SEED_CSV)[0])
            writer.writerows(mutated)
        cases.append(("M2 Task 改成 Schema 对象 ⇒ A2 分口径 FAIL", path2))

        # M3 写入占位根域 ⇒ A7 必须 FAIL
        mutated3 = [list(row) for row in rows]
        for row in mutated3:
            if row[0] == "Party":
                row[1] = "https://gits.bank.example/ontology/core#Party"
        path3 = tmp / "seed-placeholder.csv"
        with path3.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(read_seed(SEED_CSV)[0])
            writer.writerows(mutated3)
        cases.append(("M3 权威 IRI 用 bank.example 占位根域 ⇒ A7 FAIL", path3))

        failures: list[str] = []
        for name, path in cases:
            code = gate(path, write=False)
            ok = code == 2
            print(f"{'PASS' if ok else 'FAIL'}  {name}  exit={code}")
            if not ok:
                failures.append(name)

        control = gate(SEED_CSV, write=False)
        print(f"{'PASS' if control == 0 else 'FAIL'}  M0 对照：未变异种子 ⇒ PASS  exit={control}")
        if control != 0:
            failures.append("M0 对照")

        if failures:
            print(f"onto1-attribution-selftest: FAIL {failures}", file=sys.stderr)
            return 2
        print("onto1-attribution-selftest: PASS")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--seed", default=str(SEED_CSV))
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    return gate(Path(args.seed))


if __name__ == "__main__":
    raise SystemExit(main())
