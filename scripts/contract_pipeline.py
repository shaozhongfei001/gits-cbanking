#!/usr/bin/env python3
"""Compile and verify the repository's multi-contract registry without soft passes."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat

try:
    import yaml
except ImportError:  # pragma: no cover - 环境缺失时由 bootstrap-check 拦截
    yaml = None
import sys
import tempfile
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "specs/CONTRACT_INDEX.yaml"
GENERATED = ROOT / "generated"
PLACEHOLDERS = ("{{", "TEMPLATE-", "Replace with", "TODO:")
RANGE_MAP = {
    "string": {"type": "string"},
    "datetime": {"type": "string", "format": "date-time"},
    "date": {"type": "string", "format": "date"},
    "uri": {"type": "string", "format": "uri"},
    "integer": {"type": "integer"},
    "boolean": {"type": "boolean"},
    "decimal": {"type": "number"},
}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    value.update(path.read_bytes())
    return value.hexdigest()


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid JSON/YAML-JSON source {path}: {exc}") from exc


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def reject_placeholders(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    found = [token for token in PLACEHOLDERS if token in text]
    if found:
        raise ValueError(f"placeholder tokens in contract source {path}: {found}")


def validate_json_schema(source: dict, path: Path) -> None:
    if source.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        raise ValueError(f"{path}: JSON Schema 2020-12 declaration required")
    if source.get("type") != "object":
        raise ValueError(f"{path}: root object schema required")


def validate_openapi(source: dict, path: Path) -> None:
    if source.get("openapi") != "3.1.1":
        raise ValueError(f"{path}: OpenAPI 3.1.1 required")
    if not source.get("info", {}).get("version") or not source.get("paths"):
        raise ValueError(f"{path}: info.version and paths are required")
    operation_ids = []
    for operations in source["paths"].values():
        for method, operation in operations.items():
            if method.lower() not in {"get", "post", "put", "patch", "delete", "options", "head"}:
                continue
            operation_id = operation.get("operationId")
            if not operation_id:
                raise ValueError(f"{path}: every operation requires operationId")
            operation_ids.append(operation_id)
    if len(operation_ids) != len(set(operation_ids)):
        raise ValueError(f"{path}: duplicate operationId")


def validate_asyncapi(source: dict, path: Path) -> None:
    if source.get("asyncapi") not in {"3.0.0", "3.1.0"}:
        raise ValueError(f"{path}: supported AsyncAPI version is 3.0.0 or 3.1.0")
    if not source.get("channels") or not source.get("operations"):
        raise ValueError(f"{path}: channels and operations are required")


def validate_dmn(path: Path) -> None:
    root = ET.parse(path).getroot()
    if not root.tag.endswith("definitions"):
        raise ValueError(f"{path}: DMN definitions root required")
    decisions = [item for item in root.iter() if item.tag.endswith("decision")]
    if not decisions:
        raise ValueError(f"{path}: at least one DMN decision required")


def validate_turtle(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if "@prefix" not in text or not text.rstrip().endswith("."):
        raise ValueError(f"{path}: basic Turtle prefix and terminating period required")
    if text.count("[") != text.count("]") or text.count("(") != text.count(")"):
        raise ValueError(f"{path}: unbalanced Turtle delimiters")


def validate_source_contract_instance(instance: dict, path: Path) -> None:
    """Fail-closed structural validation against CTR-DATA-001 required shape."""
    required = ("sourceContractId", "version", "system", "owner", "classification", "objects", "effectiveFrom")
    missing = [key for key in required if key not in instance]
    if missing:
        raise ValueError(f"{path}: missing required Source Contract fields: {missing}")
    classification = instance.get("classification")
    if classification not in {"PUBLIC", "INTERNAL", "SENSITIVE", "RESTRICTED"}:
        raise ValueError(f"{path}: invalid classification {classification}")
    objects = instance.get("objects")
    if not isinstance(objects, list) or not objects:
        raise ValueError(f"{path}: objects must be a non-empty array")
    for index, obj in enumerate(objects):
        if not isinstance(obj, dict):
            raise ValueError(f"{path}: objects[{index}] must be an object")
        for key in ("schema", "name", "authority", "fields"):
            if key not in obj:
                raise ValueError(f"{path}: objects[{index}] missing {key}")
        if obj.get("authority") not in {"AUTHORITATIVE", "REFERENCE", "DERIVED"}:
            raise ValueError(f"{path}: objects[{index}] invalid authority")
        if not isinstance(obj.get("fields"), list):
            raise ValueError(f"{path}: objects[{index}].fields must be an array")


def linkml_json_schema(profile: dict) -> dict:
    definitions = {}
    for class_name, class_def in sorted(profile.get("classes", {}).items()):
        attributes = class_def.get("attributes", {})
        properties = {}
        required = []
        for attr_name, attr in sorted(attributes.items()):
            attr_range = attr.get("range", "string")
            if attr_range not in RANGE_MAP:
                raise ValueError(f"unsupported LinkML bootstrap range: {class_name}.{attr_name}={attr_range}")
            properties[attr_name] = dict(RANGE_MAP[attr_range])
            if attr.get("description"):
                properties[attr_name]["description"] = attr["description"]
            if attr.get("required") or attr.get("identifier"):
                required.append(attr_name)
        schema = {
            "type": "object",
            "additionalProperties": False,
            "description": class_def.get("description", ""),
            "properties": properties,
        }
        if required:
            schema["required"] = sorted(set(required))
        definitions[class_name] = schema
    if not definitions:
        raise ValueError("LinkML profile contains no classes")
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": profile["id"] + "/schema.json",
        "title": profile["name"],
        "version": profile.get("version"),
        "$defs": definitions,
    }


def linkml_shacl(profile: dict) -> str:
    lines = [
        "@prefix gits: <https://gientech.com/gits/kno/> .",
        "@prefix sh: <http://www.w3.org/ns/shacl#> .",
        "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .",
        "",
    ]
    xsd = {"string": "xsd:string", "datetime": "xsd:dateTime", "date": "xsd:date", "uri": "xsd:anyURI", "integer": "xsd:integer", "boolean": "xsd:boolean", "decimal": "xsd:decimal"}
    for class_name, class_def in sorted(profile["classes"].items()):
        lines.extend([f"gits:{class_name}Shape a sh:NodeShape ;", f"  sh:targetClass gits:{class_name} ;"])
        attributes = sorted(class_def.get("attributes", {}).items())
        for index, (attr_name, attr) in enumerate(attributes):
            suffix = " ;" if index < len(attributes) - 1 else " ."
            min_count = " ; sh:minCount 1" if attr.get("required") or attr.get("identifier") else ""
            lines.append(f"  sh:property [ sh:path gits:{attr_name} ; sh:datatype {xsd[attr.get('range', 'string')]}{min_count} ]{suffix}")
        if not attributes:
            lines[-1] = lines[-1][:-1] + "."
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def validate_index(index: dict) -> list[dict]:
    contracts = index.get("contracts")
    if not isinstance(contracts, list) or not contracts:
        raise ValueError("contract index must contain a non-empty contracts array")
    ids = [item.get("id") for item in contracts]
    if None in ids or len(ids) != len(set(ids)):
        raise ValueError("contract IDs are missing or duplicated")
    for item in contracts:
        for key in ("kind", "authority_source", "owner", "compatibility", "consumers", "generated"):
            if key not in item:
                raise ValueError(f"{item['id']}: missing {key}")
        if not item["owner"] or not item["consumers"]:
            raise ValueError(f"{item['id']}: owner and consumers are required")
    return contracts


def compile_all(destination: Path) -> dict:
    index = load_json(INDEX)
    contracts = validate_index(index)
    source_hashes = {}
    catalog = []
    for item in contracts:
        source_path = ROOT / item["authority_source"]
        if not source_path.is_file():
            raise ValueError(f"{item['id']}: authority source missing: {source_path}")
        reject_placeholders(source_path)
        source_hashes[item["id"]] = digest(source_path)
        kind = item["kind"]
        parsed = None
        if kind == "yaml_taxonomy":
            if yaml is None:
                raise ValueError("yaml_taxonomy requires PyYAML")
            parsed = yaml.safe_load(source_path.read_text(encoding="utf-8"))
        elif kind in {"openapi", "openapi_paths", "asyncapi", "json_schema", "linkml_subset", "source_contract_instance", "seed_claims"}:
            parsed = load_json(source_path)
        if kind == "openapi":
            validate_openapi(parsed, source_path)
        elif kind == "openapi_paths":
            validate_openapi(parsed, source_path)
        elif kind == "asyncapi":
            validate_asyncapi(parsed, source_path)
        elif kind == "json_schema":
            validate_json_schema(parsed, source_path)
        elif kind == "linkml_subset":
            if not parsed.get("id") or not parsed.get("name") or not parsed.get("classes"):
                raise ValueError(f"{source_path}: id, name and classes are required")
        elif kind == "source_contract_instance":
            validate_source_contract_instance(parsed, source_path)
        elif kind == "dmn":
            validate_dmn(source_path)
        elif kind == "turtle":
            validate_turtle(source_path)
        elif kind == "yaml_taxonomy":
            if not parsed.get("domains") or not parsed.get("families"):
                raise ValueError(f"{source_path}: domains and families are required")
        elif kind == "seed_claims":
            pass  # data file, no schema validation
        else:
            raise ValueError(f"{item['id']}: unsupported contract kind {kind}")

        generated_targets = [Path(raw).relative_to("generated") for raw in item["generated"]]
        if kind in {"openapi", "openapi_paths", "asyncapi", "json_schema", "source_contract_instance", "yaml_taxonomy"}:
            if len(generated_targets) != 1:
                raise ValueError(f"{item['id']}: exactly one normalized target required")
            write_json(destination / generated_targets[0], parsed)
        elif kind == "dmn":
            if len(generated_targets) != 1:
                raise ValueError(f"{item['id']}: exactly one normalized DMN target required")
            target = destination / generated_targets[0]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source_path.read_bytes())
        elif kind == "linkml_subset":
            if len(generated_targets) != 2:
                raise ValueError(f"{item['id']}: JSON Schema and SHACL targets required")
            write_json(destination / generated_targets[0], linkml_json_schema(parsed))
            shacl_target = destination / generated_targets[1]
            shacl_target.parent.mkdir(parents=True, exist_ok=True)
            shacl_target.write_text(linkml_shacl(parsed), encoding="utf-8")
        elif kind == "seed_claims":
            if len(generated_targets) != 1:
                raise ValueError(f"{item['id']}: exactly one seed_claims target required")
            target = destination / generated_targets[0]
            target.parent.mkdir(parents=True, exist_ok=True)
            write_json(target, parsed)

        catalog.append({key: item[key] for key in ("id", "kind", "authority_source", "owner", "compatibility", "consumers", "generated")})

    write_json(destination / "contract-catalog.json", {"registry_id": index["registry_id"], "contracts": catalog})
    generated_hashes = {}
    for path in sorted(destination.rglob("*")):
        if path.is_file() and path.name != "manifest.json":
            generated_hashes[path.relative_to(destination).as_posix()] = digest(path)
    manifest = {
        "registry_id": index["registry_id"],
        "source_hashes": source_hashes,
        "generated_hashes": generated_hashes,
        "compiler": "GITS_BOOTSTRAP_LINKML_SUBSET_0.1",
        "limitations": ["OFFICIAL_LINKML_AND_JENA_VALIDATION_REQUIRED_BEFORE_PRODUCTION_BASELINE"],
    }
    write_json(destination / "manifest.json", manifest)
    return manifest


def replace_generated(staged: Path) -> None:
    if GENERATED.exists():
        for path in GENERATED.rglob("*"):
            if path.is_file():
                path.chmod(path.stat().st_mode | stat.S_IWUSR)
        shutil.rmtree(GENERATED)
    os.replace(staged, GENERATED)
    for path in GENERATED.rglob("*"):
        if path.is_file():
            path.chmod(0o444)
        elif path.is_dir():
            path.chmod(0o755)


def generate() -> None:
    parent = GENERATED.parent
    with tempfile.TemporaryDirectory(prefix=".contract-build-", dir=parent) as raw:
        temp_root = Path(raw)
        staged = temp_root / "generated"
        staged.mkdir()
        compile_all(staged)
        publish = parent / f".generated-publish-{os.getpid()}"
        if publish.exists():
            shutil.rmtree(publish)
        shutil.copytree(staged, publish)
        replace_generated(publish)


def check() -> None:
    if not GENERATED.is_dir():
        raise ValueError("generated directory missing; run make generate")
    with tempfile.TemporaryDirectory(prefix="contract-check-") as raw:
        expected = Path(raw) / "generated"
        expected.mkdir()
        compile_all(expected)
        expected_files = {p.relative_to(expected).as_posix(): digest(p) for p in expected.rglob("*") if p.is_file()}
        actual_files = {p.relative_to(GENERATED).as_posix(): digest(p) for p in GENERATED.rglob("*") if p.is_file()}
        if expected_files != actual_files:
            missing = sorted(set(expected_files) - set(actual_files))
            extra = sorted(set(actual_files) - set(expected_files))
            changed = sorted(key for key in set(expected_files) & set(actual_files) if expected_files[key] != actual_files[key])
            raise ValueError(f"generated drift detected: missing={missing}, extra={extra}, changed={changed}")
    writable = [p.relative_to(ROOT).as_posix() for p in GENERATED.rglob("*") if p.is_file() and p.stat().st_mode & 0o222]
    if writable:
        raise ValueError(f"generated files must be read-only: {writable}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("generate", "check"))
    args = parser.parse_args()
    try:
        generate() if args.mode == "generate" else check()
        print(f"contract-{args.mode}: PASS")
        return 0
    except (OSError, ValueError, ET.ParseError) as exc:
        print(f"contract-{args.mode}: FAIL: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
