#!/usr/bin/env python3
"""Fail-closed P20 knowledge architecture contract validator (stdlib only)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ASSET_TYPES = {
    "FOUNDATIONAL_DATA",
    "KNOWLEDGE_RULE",
    "PROCESS_TOOL",
    "RUNTIME_FEEDBACK",
}
ROUTE_MODES = {
    "MAP_FIRST",
    "ONTOLOGY_FIRST",
    "MAP_THEN_ONTOLOGY",
    "ONTOLOGY_THEN_MAP",
}
IN_SCOPE_CONTRACTS = {
    "AC-PREVISIT-001",
    "AC-FACT-RECONCILIATION-001",
    "AC-PRODUCT-RECOMMEND-001",
}


def fail(message: str) -> None:
    raise ValueError(message)


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"{path}: invalid JSON: {exc}")
    if not isinstance(value, dict):
        fail(f"{path}: root object required")
    return value


def read_jsonl(path: Path) -> list[dict]:
    values = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            fail(f"{path}:{line_no}: invalid JSONL: {exc}")
        if not isinstance(value, dict):
            fail(f"{path}:{line_no}: object required")
        values.append(value)
    if not values:
        fail(f"{path}: at least one JSONL record required")
    return values


def read_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    if len(lines) < 4 or lines[0].strip() != "---":
        fail(f"{path}: opening frontmatter delimiter required")
    try:
        closing = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
    except StopIteration:
        fail(f"{path}: closing frontmatter delimiter required")
    raw = "\n".join(lines[1:closing]).strip()
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        fail(f"{path}: frontmatter must be JSON-compatible YAML: {exc}")
    if not isinstance(value, dict):
        fail(f"{path}: frontmatter object required")
    if not "\n".join(lines[closing + 1:]).strip():
        fail(f"{path}: human-readable markdown body required")
    return value


def require(obj: dict, fields: tuple[str, ...], path: Path) -> None:
    missing = [field for field in fields if field not in obj]
    if missing:
        fail(f"{path}: missing required fields {missing}")


def unique_index(values: list[tuple[str, dict, Path]], label: str) -> dict[str, tuple[dict, Path]]:
    result: dict[str, tuple[dict, Path]] = {}
    for item_id, value, path in values:
        if not item_id:
            fail(f"{path}: {label} ID required")
        if item_id in result:
            fail(f"duplicate {label} ID {item_id}: {result[item_id][1]} and {path}")
        result[item_id] = (value, path)
    return result


def validate(root: Path) -> dict:
    base = root / "specs" / "knowledge-architecture"
    if not base.is_dir():
        fail(f"knowledge architecture directory missing: {base}")

    schema_paths = sorted((base / "schemas").glob("*.json"))
    required_schemas = [
        "knowledge-map.schema.json",
        "asset-manifest.schema.json",
        "activation-contract.schema.json",
        "route-policy.schema.json",
        "activation-plan.schema.json",
        "skill-descriptor.schema.json",
    ]
    schema_names = {p.name for p in schema_paths}
    missing = [name for name in required_schemas if name not in schema_names]
    if missing:
        fail(f"required schema contracts missing: {missing}")
    for path in schema_paths:
        schema = read_json(path)
        if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            fail(f"{path}: JSON Schema 2020-12 required")
        if schema.get("type") != "object":
            fail(f"{path}: root object schema required")

    maps_raw = []
    for path in sorted((base / "maps").rglob("*.md")):
        value = read_frontmatter(path)
        require(value, ("schemaVersion", "mapId", "version", "mapType", "entrypoints", "defaultPolicy", "routePolicyRef"), path)
        if value["defaultPolicy"] != "DENY":
            fail(f"{path}: defaultPolicy must be DENY")
        maps_raw.append((value["mapId"], value, path))
    maps = unique_index(maps_raw, "map")
    if "KM-GITS-ROOT" not in maps:
        fail("KM-GITS-ROOT is required")

    assets_raw = []
    type_counts = {key: 0 for key in ASSET_TYPES}
    for path in sorted((base / "assets").rglob("*.md")):
        value = read_frontmatter(path)
        require(value, ("schemaVersion", "assetId", "assetType", "version", "source", "governance", "activation", "evidence"), path)
        if value["assetType"] not in ASSET_TYPES:
            fail(f"{path}: unsupported assetType {value['assetType']}")
        type_counts[value["assetType"]] += 1
        governance = value["governance"]
        require(governance, ("owner", "classification", "permissionInherit", "allowedActions"), path)
        if governance["classification"] in {"SENSITIVE", "RESTRICTED"} and governance["permissionInherit"] not in {"CALLER", "EXPLICIT"}:
            fail(f"{path}: sensitive assets must inherit CALLER or EXPLICIT permission")
        evidence = value["evidence"]
        if not all(evidence.get(key) is True for key in ("citationRequired", "sourceVersionRequired", "contentHashRequired")):
            fail(f"{path}: citation, source version and content hash are mandatory in P20")
        assets_raw.append((value["assetId"], value, path))
    assets = unique_index(assets_raw, "asset")
    # 20 → 21：2026-09-07 依 ADR-PK-PRODUCT-RULES-ASSET 路径 A 新增
    # ASSET-KNOW-PRODUCT-RULES（SP-15 早已声明该依赖，资产从未注册）
    if len(assets) != 21:
        fail(f"exactly 21 P20 asset manifests required, found {len(assets)}")
    if any(count == 0 for count in type_counts.values()):
        fail(f"all four asset classes are required: {type_counts}")

    skills_raw = []
    for path in sorted((base / "skills").glob("*.json")):
        value = read_json(path)
        require(value, ("schemaVersion", "skillId", "version", "assetDependencies", "semanticDependencies", "ruleDependencies", "sideEffectPolicy"), path)
        for asset_id in value["assetDependencies"]:
            if asset_id not in assets:
                fail(f"{path}: unknown asset dependency {asset_id}")
        skills_raw.append((value["skillId"], value, path))
    skills = unique_index(skills_raw, "skill")
    if set(skills) != {"SP-02", "SP-05", "SP-07", "SP-10", "SP-15"}:
        fail(f"unexpected P20 skill set: {sorted(skills)}")

    activations_raw = []
    for path in sorted((base / "activations").glob("*.json")):
        value = read_json(path)
        require(value, ("schemaVersion", "contractId", "version", "taskType", "routeMode", "preconditions", "activations", "semanticQueries", "ruleChecks", "skills", "context", "humanGates", "failurePolicy"), path)
        if value["routeMode"] not in ROUTE_MODES:
            fail(f"{path}: invalid routeMode")
        if not value["preconditions"].get("permissionDecisionRequired"):
            fail(f"{path}: permissionDecisionRequired must be true")
        seen_sequences = set()
        for activation in value["activations"]:
            asset_id = activation.get("assetId")
            if asset_id not in assets:
                fail(f"{path}: unknown activation asset {asset_id}")
            sequence = activation.get("sequence")
            if sequence in seen_sequences:
                fail(f"{path}: duplicate activation sequence {sequence}")
            seen_sequences.add(sequence)
        for skill_id in value["skills"]:
            if skill_id not in skills:
                fail(f"{path}: unknown skill {skill_id}")
        activations_raw.append((value["contractId"], value, path))
    activations = unique_index(activations_raw, "activation contract")
    if set(activations) != IN_SCOPE_CONTRACTS:
        fail(f"unexpected P20 activation set: {sorted(activations)}")

    routes = []
    route_rules_by_task = {}
    for path in sorted((base / "routes").glob("*.json")):
        value = read_json(path)
        require(value, ("schemaVersion", "policyId", "version", "defaultDecision", "rules"), path)
        if value["defaultDecision"] != "DENY_UNMAPPED_TASK":
            fail(f"{path}: defaultDecision must fail closed")
        for rule in value["rules"]:
            if rule.get("mode") not in ROUTE_MODES:
                fail(f"{path}: invalid route mode in rule")
            task_type = rule.get("taskType")
            if not task_type or task_type in route_rules_by_task:
                fail(f"{path}: taskType must be present and unique: {task_type}")
            route_rules_by_task[task_type] = rule
            ref = rule.get("activationContractRef")
            if ref != "AC-NOT-IN-P20" and ref not in activations:
                fail(f"{path}: unknown activation contract {ref}")
            if ref in activations:
                contract = activations[ref][0]
                if contract["taskType"] != task_type or contract["routeMode"] != rule["mode"]:
                    fail(f"{path}: route rule and activation contract disagree for {task_type}")
        routes.append(value)
    if len(routes) != 1 or routes[0]["policyId"] != "RP-CORP-RM-001":
        fail("exactly RP-CORP-RM-001 route policy is required")

    for _, value, path in maps_raw:
        for asset_id in value.get("assetRefs", []):
            if asset_id not in assets:
                fail(f"{path}: unknown assetRef {asset_id}")
        for skill_id in value.get("skillRefs", []):
            if skill_id not in skills:
                fail(f"{path}: unknown skillRef {skill_id}")
        for contract_id in value.get("activationContractRefs", []):
            if contract_id not in activations:
                fail(f"{path}: unknown activationContractRef {contract_id}")
        if value["routePolicyRef"] != "RP-CORP-RM-001":
            fail(f"{path}: routePolicyRef must be RP-CORP-RM-001")

    examples = []
    for path in sorted((base / "examples").glob("*.json")):
        value = read_json(path)
        require(value, ("schemaVersion", "planId", "taskType", "routeMode", "versions", "selectedAssets", "skills", "permissionDecisionId", "trace"), path)
        if value["permissionDecisionId"] in {"", "PENDING"}:
            fail(f"{path}: golden plan must have an ALLOW permission decision")
        for selection in value["selectedAssets"]:
            if selection.get("assetId") not in assets:
                fail(f"{path}: unknown selected asset {selection.get('assetId')}")
        for skill_id in value["skills"]:
            if skill_id not in skills:
                fail(f"{path}: unknown plan skill {skill_id}")
        contract_ref = value["versions"].get("activationContract", "").split("@", 1)[0]
        if contract_ref not in activations:
            fail(f"{path}: unknown activation contract version ref {contract_ref}")
        contract = activations[contract_ref][0]
        if value["taskType"] != contract["taskType"] or value["routeMode"] != contract["routeMode"]:
            fail(f"{path}: golden plan disagrees with activation contract")
        if value["skills"] != contract["skills"]:
            fail(f"{path}: golden plan skill order must match activation contract")
        examples.append(value)
    if len(examples) != 2:
        fail(f"exactly 2 golden ActivationPlans required, found {len(examples)}")

    test_counts = {}
    for path in sorted((base / "tests").glob("*.jsonl")):
        test_counts[path.name] = len(read_jsonl(path))
    required_tests = {
        "routing_cases.jsonl",
        "activation_plan_golden_cases.jsonl",
        "negative_security_cases.jsonl",
    }
    if set(test_counts) != required_tests:
        fail(f"required JSONL test sets missing or extra: {test_counts}")

    return {
        "schemas": len(schema_paths),
        "maps": len(maps),
        "assets": len(assets),
        "asset_type_counts": type_counts,
        "skills": len(skills),
        "activations": len(activations),
        "routes": len(routes),
        "examples": len(examples),
        "test_cases": sum(test_counts.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        summary = validate(args.root.resolve())
        print("knowledge-architecture-check: PASS")
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
        return 0
    except (OSError, ValueError) as exc:
        print(f"knowledge-architecture-check: FAIL: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
