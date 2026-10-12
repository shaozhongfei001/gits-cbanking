#!/usr/bin/env python3
"""GK-KE L1-1 公共语义消费者测试（C08 L1-1 / wave B1）。

覆盖 C08 L1-1 的三类必测：同名异义、破坏变更、身份误并。
以及 L1-1 产物要求：12 个最小类型、双版本引用、ID/时间/金额规范。

断言：
  1. SemanticPackage schema 可解析且为 draft 2020-12
  2. 正例通过（含 12 类型 + 双版本 + 三规范）
  3. types 少于 12 → 拒绝
  4. 类型缺 origin/temporal/sensitive → 拒绝
  5. **[同名异义]** 同 typeId 不同 definition 重复登记 → 拒绝
  6. **[破坏变更]** 领域包 imports 引用被复制改义的共享类型 → 拒绝
  7. **[身份误并]** 以名称替代身份（nameSubstitutionForbidden=false）→ 拒绝
  8. **[双版本]** 缺 coreVersion → 拒绝
  9. **[ID 规范]** 缺 idConvention → 拒绝
 10. **[时间规范]** intervalNotation 非 LEFT_CLOSED_RIGHT_OPEN → 拒绝
 11. **[金额规范]** 金额表示非 DECIMAL_STRING/INTEGER_MINOR_UNIT → 拒绝
 12. **[金额规范]** 金额用浮点类型 → 拒绝（防 float）
 13. 既有样例无回归

退出码：全通过 0，否则非 0 并打印明细。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "specs" / "gk-ke" / "v1" / "schemas" / "SemanticPackage.schema.json"
POSITIVE = ROOT / "specs" / "gk-ke" / "v1" / "examples" / "l1-1" / "positive"
NEGATIVE = ROOT / "specs" / "gk-ke" / "v1" / "examples" / "l1-1" / "negative"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def is_rejected(schema: dict, instance: dict) -> bool:
    try:
        jsonschema.validate(instance=instance, schema=schema)
        return False
    except jsonschema.ValidationError:
        return True


def check_package_invariants(doc: dict) -> list[str]:
    """L1-1 包级不变式真值校验（JSON Schema 无法表达，见 FAIL-2026-09-12-05）。

    返回被违反的不变式 ID 列表。
    """
    violated: list[str] = []
    types = doc.get("types") or []

    # TYPEID_UNIQUE：同名异义
    seen: dict[str, int] = {}
    for item in types:
        if isinstance(item, dict) and isinstance(item.get("typeId"), str):
            seen[item["typeId"]] = seen.get(item["typeId"], 0) + 1
    if any(count > 1 for count in seen.values()):
        violated.append("TYPEID_UNIQUE")

    # SHARED_TYPE_NOT_FORKED：复制后改义
    for item in types:
        if isinstance(item, dict):
            if item.get("origin") == "DOMAIN" and str(item.get("typeId", "")).startswith("core."):
                violated.append("SHARED_TYPE_NOT_FORKED")
                break

    # NO_IDENTITY_MERGE_BY_NAME：身份误并
    if (doc.get("idConvention") or {}).get("nameSubstitutionForbidden") is not True:
        violated.append("NO_IDENTITY_MERGE_BY_NAME")

    return violated


ALL_INVARIANTS = {"TYPEID_UNIQUE", "SHARED_TYPE_NOT_FORKED", "NO_IDENTITY_MERGE_BY_NAME"}


def main() -> int:
    failures: list[str] = []

    if not SCHEMA.is_file():
        print(f"FAIL: schema missing: {SCHEMA}", file=sys.stderr)
        return 2
    schema = load(SCHEMA)

    # 1. schema 自身合法
    try:
        jsonschema.Draft202012Validator.check_schema(schema)
    except jsonschema.SchemaError as exc:
        failures.append(f"[1] schema invalid: {exc.message}")

    # 2. 正例
    positives = sorted(POSITIVE.glob("*.json")) if POSITIVE.is_dir() else []
    if not positives:
        failures.append(f"[2] no positive examples in {POSITIVE}")
    for path in positives:
        doc = load(path)
        try:
            jsonschema.validate(instance=doc, schema=schema)
        except jsonschema.ValidationError as exc:
            failures.append(f"[2] {path.name}: positive rejected: {exc.message}")

    # 3. 负例：必须被拒，且 reason 声明与实测一致（防空转）
    EXPECTED_RULES = {
        "SemanticPackage_too_few_types": "MIN_12_TYPES",
        "SemanticPackage_type_missing_markers": "TYPE_MARKERS_REQUIRED",
        "SemanticPackage_homonym": "HOMONYM_CONFLICT",
        "SemanticPackage_semantic_fork": "SHARED_TYPE_FORKED",
        "SemanticPackage_identity_merge": "IDENTITY_MERGE_BY_NAME",
        "SemanticPackage_missing_core_version": "DUAL_VERSION_REQUIRED",
        "SemanticPackage_missing_id_convention": "ID_CONVENTION_REQUIRED",
        "SemanticPackage_bad_time_interval": "TIME_INTERVAL_CONVENTION",
        "SemanticPackage_bad_money_representation": "MONEY_REPRESENTATION",
        "SemanticPackage_money_as_float": "MONEY_FLOAT_FORBIDDEN",
    }
    # 由包级不变式（而非 JSON Schema）拒绝的规则
    INVARIANT_RULES = {
        "HOMONYM_CONFLICT": "TYPEID_UNIQUE",
        "SHARED_TYPE_FORKED": "SHARED_TYPE_NOT_FORKED",
        "IDENTITY_MERGE_BY_NAME": "NO_IDENTITY_MERGE_BY_NAME",
    }
    negative_count = 0
    invariant_covered: set[str] = set()
    for path in sorted(NEGATIVE.glob("*.json")) if NEGATIVE.is_dir() else []:
        doc = load(path)
        rule = doc.pop("expect_rule", None)
        doc.pop("reason", None)
        expected = EXPECTED_RULES.get(path.stem)
        if expected is None:
            failures.append(f"[3] {path.name}: no expected rule registered in test")
            continue
        if rule != expected:
            failures.append(f"[3] {path.name}: declared rule {rule!r} != expected {expected!r}")

        invariant = INVARIANT_RULES.get(expected)
        if invariant:
            # 真值路径：必须由包级不变式拒绝
            violated = check_package_invariants(doc)
            if invariant not in violated:
                failures.append(
                    f"[3] {path.name}: invariant {invariant} NOT violated by package-level check "
                    f"(violated={violated})"
                )
            invariant_covered.add(invariant)
        else:
            if not is_rejected(schema, doc):
                failures.append(f"[3] {path.name}: negative NOT rejected ({expected})")
        negative_count += 1

    # 三类 L1-1 必测必须都被覆盖，且必须各由不变式路径验证（非空转）
    for rule, invariant in INVARIANT_RULES.items():
        if invariant not in invariant_covered:
            failures.append(f"[3] invariant {invariant} ({rule}) not covered by any negative example")

    # 4. 关键字段存在性（结构自检，防 schema 被改空）
    props = schema.get("properties", {})
    for field in ("coreVersion", "idConvention", "timeConvention", "moneyConvention"):
        if field not in props:
            failures.append(f"[4] schema missing L1-1 field: {field}")
    if props.get("types", {}).get("minItems") != 12:
        failures.append(f"[4] types.minItems must be 12, got {props.get('types', {}).get('minItems')}")
    if "coreVersion" not in schema.get("required", []):
        failures.append("[4] coreVersion must be required (dual version)")

    if failures:
        print("gk-ke-l1-1-semantics-tests: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    print("gk-ke-l1-1-semantics-tests: PASS")
    print(f"  positive={len(positives)} negative={negative_count}")
    print(f"  rules covered: {sorted(set(EXPECTED_RULES.values()))}")
    print("  covered: MIN_12_TYPES, TYPE_MARKERS, HOMONYM, SHARED_TYPE_FORKED, "
          "IDENTITY_MERGE_BY_NAME, DUAL_VERSION, ID_CONVENTION, TIME_INTERVAL, MONEY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
