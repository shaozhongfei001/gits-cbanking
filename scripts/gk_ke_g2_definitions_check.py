#!/usr/bin/env python3
"""GK-KE L0-2 G2 受控目标定义核验与指纹计算（GK-KE-OWNER-003 §7.2）。

职责：
  1. 核验 specs/gk-ke/v1/definitions/ 下三份受控目标定义存在且符合结构要求。
  2. 核验定义内嵌 instance 通过对应 gk-ke/v1 JSON Schema 校验。
  3. 核验 GK-KE-OWNER-003 的关键约束落地（不得声称已发布/已实现）。
  4. **计算并回填真实文件字节 SHA-256 + 内嵌对象 canonical hash**（§7.2 E-4）。
     hash 只能由本脚本按真实字节计算，禁止手工填造。

用法：
  python3 scripts/gk_ke_g2_definitions_check.py           # 核验并报告（不写文件）
  python3 scripts/gk_ke_g2_definitions_check.py --write   # 核验并回填 hash

退出码：全部通过 0；否则非 0 并打印失败明细。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
DEFS = ROOT / "specs" / "gk-ke" / "v1" / "definitions"
SCHEMAS = ROOT / "specs" / "gk-ke" / "v1" / "schemas"
REGISTRY = DEFS / "_registry.json"

# definitionId -> (definition file, instance schema, required owner-resolution item)
SPEC = {
    "DEF-SIM-ASSET-P001": ("SIM-ASSET-P001.json", "AssetVersion.schema.json", "Q1"),
    "DEF-SIM-MAP-FINANCE": ("SIM-MAP-FINANCE.json", "KnowledgeMap.schema.json", "Q3"),
    "DEF-SIM-ROUTE-001": ("SIM-ROUTE-001.json", None, "Q2"),
}

RESOLUTION_ID = "GK-KE-OWNER-003"

HTTP_METHODS = {"get", "post", "put", "patch", "delete", "options", "head"}


def canonical_hash(obj) -> str:
    """对 JSON 对象计算确定性 canonical hash（键排序 + 紧凑分隔符 + UTF-8）。"""
    blob = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="回填 contentSha256 到定义文件")
    args = parser.parse_args()

    failures: list[str] = []
    report: list[tuple[str, str, str]] = []
    computed: dict[str, dict] = {}

    if not DEFS.is_dir():
        print(f"FAIL: definitions dir missing: {DEFS}", file=sys.stderr)
        return 2

    for definition_id, (filename, schema_name, q_item) in SPEC.items():
        path = DEFS / filename
        if not path.is_file():
            failures.append(f"[{definition_id}] definition file missing: {path}")
            continue

        doc = json.loads(path.read_text(encoding="utf-8"))

        # 1. identity / authority / origin
        if doc.get("definitionId") != definition_id:
            failures.append(f"[{definition_id}] definitionId mismatch: {doc.get('definitionId')!r}")
        authority = doc.get("authority", {})
        if authority.get("semanticOwner") != "KERT":
            failures.append(f"[{definition_id}] semanticOwner must be KERT: {authority.get('semanticOwner')!r}")
        if authority.get("physicalArchive") != "gits-cbanking":
            failures.append(f"[{definition_id}] physicalArchive must be gits-cbanking")
        if "noSecondAuthority" not in authority:
            failures.append(f"[{definition_id}] missing noSecondAuthority declaration")

        # 2. owner resolution binding
        resolution = doc.get("ownerResolution", {})
        if resolution.get("resolutionId") != RESOLUTION_ID:
            failures.append(f"[{definition_id}] must bind {RESOLUTION_ID}: {resolution.get('resolutionId')!r}")
        if q_item not in resolution.get("items", []):
            failures.append(f"[{definition_id}] must bind owner resolution item {q_item}")

        # 3. must NOT claim published / implemented
        current = doc.get("currentStatus", {})
        if current.get("contentPublished") is True:
            failures.append(f"[{definition_id}] must not claim contentPublished=true")
        if current.get("serviceReady") is True:
            failures.append(f"[{definition_id}] must not claim serviceReady=true")
        claim = doc.get("claimSeparation", {})
        if claim.get("implemented") is True:
            failures.append(f"[{definition_id}] must not claim implemented=true")
        instance = doc.get("instance", {})
        if instance.get("lifecycle") == "PUBLISHED":
            failures.append(f"[{definition_id}] instance.lifecycle must not be PUBLISHED")

        # 4. simulationOnly hardening
        if instance and instance.get("simulationOnly") is not True:
            failures.append(f"[{definition_id}] instance.simulationOnly must be true")
        if doc.get("contractVersion") != "gk-ke/v1":
            failures.append(f"[{definition_id}] contractVersion must be gk-ke/v1")

        # 5. instance must validate against its gk-ke/v1 schema
        if schema_name:
            schema_path = SCHEMAS / schema_name
            if not schema_path.is_file():
                failures.append(f"[{definition_id}] schema missing: {schema_path}")
            elif instance:
                try:
                    jsonschema.validate(instance=instance, schema=json.loads(schema_path.read_text(encoding="utf-8")))
                except jsonschema.ValidationError as exc:
                    failures.append(f"[{definition_id}] instance fails {schema_name}: {exc.message}")

        # 6. route policy specifics (GK-KE-OWNER-003 §4.2)
        if definition_id == "DEF-SIM-ROUTE-001":
            rej = doc.get("targetPolicy", {}).get("rejectionRules", {})
            if "noMatch" not in rej or "ambiguity" not in rej:
                failures.append(f"[{definition_id}] must define noMatch and ambiguity SEPARATELY (§4.2)")
            if rej.get("ambiguity", {}).get("decision") != "ROUTE_AMBIGUOUS":
                failures.append(f"[{definition_id}] ambiguity decision must be ROUTE_AMBIGUOUS")
            excluded = doc.get("targetPolicy", {}).get("excludedFromFirstSlice", {})
            if "AC-NOT-IN-P20" not in excluded.get("placeholderRefs", []):
                failures.append(f"[{definition_id}] must exclude AC-NOT-IN-P20 placeholder")
            if "ONTOLOGY_THEN_MAP" != doc.get("targetPolicy", {}).get("routeMode", {}).get("name"):
                failures.append(f"[{definition_id}] routeMode must retain ONTOLOGY_THEN_MAP intent")

        # 7. product-card granularity (GK-KE-OWNER-003 §3.1)
        if definition_id == "DEF-SIM-ASSET-P001":
            rule = doc.get("selectionRule", {})
            if rule.get("sourceGranularity") != "COLLECTION":
                failures.append(f"[{definition_id}] sourceGranularity must be COLLECTION")
            if rule.get("notIdentityEquivalent") is not True:
                failures.append(f"[{definition_id}] must declare notIdentityEquivalent=true")
            if rule.get("relation") != "SELECT_OR_CONSTRUCT":
                failures.append(f"[{definition_id}] relation must be SELECT_OR_CONSTRUCT")

        # 8. map projection specifics (GK-KE-OWNER-003 §5)
        if definition_id == "DEF-SIM-MAP-FINANCE":
            proj = doc.get("projectionRelation", {})
            if proj.get("relation") != "SCENARIO_PROJECTION":
                failures.append(f"[{definition_id}] relation must be SCENARIO_PROJECTION")
            if proj.get("lossy") is not True:
                failures.append(f"[{definition_id}] must declare lossy=true")
            boundary = doc.get("sourceEvidenceBoundary", {})
            if "whatItDoesNotProve" not in boundary:
                failures.append(f"[{definition_id}] must record whatItDoesNotProve (§5.1)")

        # 9. hash: file must NOT contain its own hash (see FAIL-2026-09-12-03).
        #     Hashes live in a sidecar registry, never inside the hashed file.
        declared = doc.get("origin", {}).get("contentSha256", "__MISSING__")
        if declared is not None:
            failures.append(
                f"[{definition_id}] origin.contentSha256 must be null (self-reference guard, "
                f"see FAIL-2026-09-12-03); got {declared!r}"
            )
        embedded = doc.get("instance")
        embedded_hash = canonical_hash(embedded) if embedded else None
        computed[definition_id] = {
            "path": str(path.relative_to(ROOT)),
            "fileSha256": file_hash(path),
            "canonicalInstanceSha256": embedded_hash,
        }
        report.append((definition_id, file_hash(path), embedded_hash or "-"))

    if failures:
        print("gk-ke-g2-definitions-check: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    registry_ok = True
    if args.write:
        registry = {
            "$comment": (
                "GK-KE L0-2 G2 受控目标定义指纹登记（侧车清单）。"
                "由 scripts/gk_ke_g2_definitions_check.py --write 按真实文件字节计算并写入；"
                "禁止手工编辑。定义文件自身不得包含自己的 hash（FAIL-2026-09-12-03）。"
            ),
            "resolutionId": RESOLUTION_ID,
            "hashMethod": "sha256(raw file bytes)",
            "canonicalHashMethod": "sha256(canonical json: sorted keys, compact separators, utf-8) of the definition file",
            "definitions": computed,
        }
        REGISTRY.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    else:
        # read-only verification: registry values must match the real bytes
        if not REGISTRY.is_file():
            failures.append(f"registry missing: {REGISTRY} (run with --write to create)")
            registry_ok = False
        else:
            stored = json.loads(REGISTRY.read_text(encoding="utf-8")).get("definitions", {})
            for definition_id, current in computed.items():
                previous = stored.get(definition_id, {})
                if previous.get("fileSha256") != current["fileSha256"]:
                    failures.append(
                        f"[{definition_id}] registry fileSha256 mismatch: "
                        f"stored={previous.get('fileSha256')!r} actual={current['fileSha256']!r}"
                    )
                    registry_ok = False
                if previous.get("canonicalInstanceSha256") != current["canonicalInstanceSha256"]:
                    failures.append(f"[{definition_id}] registry canonicalInstanceSha256 mismatch")
                    registry_ok = False

    if failures:
        print("gk-ke-g2-definitions-check: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    print("gk-ke-g2-definitions-check: PASS")
    print(f"  resolution bound: {RESOLUTION_ID}")
    print(f"  definitions: {len(SPEC)}")
    for definition_id, fhash, ihash in report:
        print(f"  {definition_id}: file_sha256={fhash} canonical_instance={ihash}")
    print(f"  registry: {REGISTRY.relative_to(ROOT)} ({'written' if args.write else 'verified'})")
    if args.write:
        print("  note: definition files keep origin.contentSha256=null by design")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
