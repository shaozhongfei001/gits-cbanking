#!/usr/bin/env python3
"""CTR-PKC-API-001 / CTR-PKC-DOM-001 消费者契约测试（Loop PC0，REQ-PI-01）。

设计原则（本仓 GK 系列实证教训：否定式断言必须做变异复验，否则“断言空转”）：
- fail-closed：合同源 / 登记表缺失、字段缺失一律 FAIL；
- 单一真值函数 detect(...)：返回违规清单，空=PASS；
- --self-test：对检测器注入 6 类已知故障，要求全部被捕获（mutate→FAIL），
  恢复后 detect 为空（restore→PASS）。任一变异未被捕获即退出码 1。

用法：
    python3 scripts/pkc_contract_tests.py              # 常规检查
    python3 scripts/pkc_contract_tests.py --self-test  # 变异复验
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "specs/CONTRACT_INDEX.yaml"
API_SPEC = ROOT / "specs/product-center/product-center-api.openapi.json"
DOMAIN_SPEC = ROOT / "specs/product-center/product-center-domain.schema.json"

EXPECTED_OPERATIONS = {
    "listProductCenterFamilies",
    "listProductCenterProducts",
    "getProductCenterDetail",
    "getProductCenterSection",
    "searchProductCenterKnowledge",
    "listProductCenterProductVersions",
    "getProductCenterVersionDiff",
    "getProductCenterCoverage",
    "putProductCenterFavorite",
    "deleteProductCenterFavorite",
    "downloadProductCenterInternalNote",
    "generateProductCenterOutline",
    "askProductCenterAssistant",
    "locateProductCenterEvidence",
    "createProductCenterFeedback",
}

REQUIRED_ERROR_CODES = {
    "PRODUCT_NOT_FOUND", "NO_PUBLISHED_VERSION", "VERSION_EXPIRED", "VERSION_CONFLICT",
    "EVIDENCE_NOT_FOUND", "EVIDENCE_EXPIRED", "EVIDENCE_ACCESS_DENIED", "PRODUCT_ACCESS_DENIED",
    "GENERATION_UNAVAILABLE", "ANSWER_WITHOUT_EVIDENCE", "DOWNLOAD_FAILED", "SEARCH_TIMEOUT",
    "SOURCES_UNAVAILABLE",
    "BAD_REQUEST",
}

CERTAINTY_STATES = {
    "VERIFIED", "PENDING_VERIFICATION", "APPROVAL_VARIABLE", "PRICING_VARIABLE",
    "CONFLICTING", "EXPIRED", "NOT_APPLICABLE",
}

# OD-PI-03 受控假设：既有 CTR-PK-INT-001 5 态 → 产品中心 7 态的单向映射（必须逐态可追溯）。
LEGACY_STATE_MAPPING = {
    "SUPPORTED": "VERIFIED",
    "UNKNOWN": "PENDING_VERIFICATION",
    "CONFLICT": "CONFLICTING",
    "STALE": "EXPIRED",
    "NOT_APPLICABLE": "NOT_APPLICABLE",
}

FORBIDDEN_COMPARISON_FIELDS = {
    "recommendation_score", "fit_score", "ranking", "win_rate", "next_best_action",
}

AUDIT_EVENT_TYPES = {
    "PRODUCT_VIEWED", "VERSION_HISTORY_VIEWED", "EVIDENCE_OPENED", "INTERNAL_NOTE_DOWNLOADED",
    "OUTLINE_GENERATED", "ASSISTANT_ASKED", "FAVORITE_CHANGED", "KNOWLEDGE_FEEDBACK_CREATED",
}

HTTP_METHODS = {"get", "post", "put", "patch", "delete", "options", "head"}


def _load_json(path: Path) -> dict:
    if not path.is_file():
        raise FileNotFoundError(f"missing contract source: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _load_registry_contracts() -> list[dict]:
    text = REGISTRY.read_text(encoding="utf-8")
    start = text.index("{")
    data = json.loads(text[start:])
    return data.get("contracts", [])


def _walk_refs(node: object) -> list[str]:
    found: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "$ref" and isinstance(value, str):
                found.append(value)
            else:
                found.extend(_walk_refs(value))
    elif isinstance(node, list):
        for item in node:
            found.extend(_walk_refs(item))
    return found


def _error_response_refs(api: dict, response: object) -> list[str]:
    """解析一个响应对象的 $ref 链，返回其中引用到的 schema 名。

    支持：响应内直接 $ref schema；以及响应级 $ref（#/components/responses/X）
    的一级解引（FAIL-2026-09-20-01 根因）。
    """
    refs: list[str] = []
    if not isinstance(response, dict):
        return refs
    direct = response.get("$ref")
    if isinstance(direct, str) and direct.startswith("#/components/responses/"):
        component_name = direct.rsplit("/", 1)[-1]
        component = api.get("components", {}).get("responses", {}).get(component_name)
        return _walk_refs(component)
    return _walk_refs(response)


def detect(api: dict, domain: dict, contracts: list[dict]) -> list[str]:
    """单一真值函数：返回违规清单；空列表 = PASS。"""
    problems: list[str] = []

    # ---- 登记表（fail-closed） ----
    by_id = {item.get("id"): item for item in contracts}
    for contract_id, generated_target in (
        ("CTR-PKC-API-001", "generated/openapi/product-center.normalized.json"),
        ("CTR-PKC-DOM-001", "generated/product-center/product-center-domain.schema.json"),
    ):
        entry = by_id.get(contract_id)
        if entry is None:
            problems.append(f"registry: missing {contract_id}")
            continue
        if generated_target not in entry.get("generated", []):
            problems.append(f"registry: {contract_id} generated target must contain {generated_target}")
        if not (ROOT / entry.get("authority_source", "")).is_file():
            problems.append(f"registry: {contract_id} authority_source missing on disk")

    # ---- OpenAPI ----
    if api.get("openapi") != "3.1.1":
        problems.append("api: openapi version must be 3.1.1")
    operations: set[str] = set()
    for _path, path_item in api.get("paths", {}).items():
        for method, operation in path_item.items():
            if method.lower() not in HTTP_METHODS:
                continue
            operation_id = operation.get("operationId")
            if not operation_id:
                problems.append(f"api: operation missing operationId ({method} {_path})")
                continue
            operations.add(operation_id)
            for status, response in operation.get("responses", {}).items():
                if status.startswith("4") or status.startswith("5"):
                    refs = _error_response_refs(api, response)
                    if "#/components/schemas/PkcError" not in refs:
                        problems.append(f"api: {operation_id} {status} must reference PkcError")
    missing_ops = EXPECTED_OPERATIONS - operations
    extra_ops = operations - EXPECTED_OPERATIONS
    if missing_ops:
        problems.append(f"api: missing operations {sorted(missing_ops)}")
    if extra_ops:
        problems.append(f"api: unexpected operations {sorted(extra_ops)}")

    schemas = api.get("components", {}).get("schemas", {})
    error_schema = schemas.get("PkcError", {})
    codes = set(error_schema.get("properties", {}).get("code", {}).get("enum", []))
    if codes != REQUIRED_ERROR_CODES:
        problems.append(f"api: PkcError.code enum mismatch: missing={sorted(REQUIRED_ERROR_CODES - codes)} extra={sorted(codes - REQUIRED_ERROR_CODES)}")

    certainty = schemas.get("PkcCertaintyType", {}).get("enum", [])
    if set(certainty) != CERTAINTY_STATES:
        problems.append(f"api: PkcCertaintyType enum mismatch: {sorted(set(certainty) ^ CERTAINTY_STATES)}")

    product_id = schemas.get("PkcProductId", {})
    if product_id.get("pattern") != r"^PROD-[A-Z]+-[0-9]{3}$":
        problems.append("api: PkcProductId pattern must stay ^PROD-[A-Z]+-[0-9]{3}$ (OD-PI-05)")

    comparison = schemas.get("PkcComparisonSet", {})
    if comparison.get("additionalProperties") is not False:
        problems.append("api: PkcComparisonSet.additionalProperties must be false (forbidden fields must fail validation)")
    if set(comparison.get("x-forbidden-fields", [])) != FORBIDDEN_COMPARISON_FIELDS:
        problems.append("api: PkcComparisonSet.x-forbidden-fields must list the 5 recommendation fields")
    for forbidden in FORBIDDEN_COMPARISON_FIELDS:
        if forbidden in comparison.get("properties", {}):
            problems.append(f"api: PkcComparisonSet must not declare forbidden field {forbidden}")

    assistant = schemas.get("PkcAssistantAnswer", {})
    for required in ("refused", "citations", "boundaryStatement", "traceId"):
        if required not in assistant.get("required", []):
            problems.append(f"api: PkcAssistantAnswer must require {required} (evidence-first / audit)")
    if "answerText" in assistant.get("required", []):
        problems.append("api: PkcAssistantAnswer must NOT require answerText (refusal must be representable)")

    outline = schemas.get("PkcOutlineResult", {})
    for required in ("boundaryStatement", "citations", "traceId"):
        if required not in outline.get("required", []):
            problems.append(f"api: PkcOutlineResult must require {required}")

    evidence = schemas.get("PkcEvidenceRef", {})
    if evidence.get("x-aligned-contract") != "CTR-PK-EVR-001":
        problems.append("api: PkcEvidenceRef must declare x-aligned-contract CTR-PK-EVR-001 (no parallel model)")

    # ---- 领域对象 ----
    if domain.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
        problems.append("domain: $schema must be draft 2020-12")
    if domain.get("type") != "object":
        problems.append("domain: root must be object")
    defs = domain.get("$defs", {})
    certainty_def = defs.get("CertaintyType", {}).get("enum", [])
    if set(certainty_def) != CERTAINTY_STATES:
        problems.append("domain: CertaintyType enum mismatch")
    for legacy, target in LEGACY_STATE_MAPPING.items():
        if target not in CERTAINTY_STATES:
            problems.append(f"domain: mapping target {legacy}->{target} not in CertaintyType enum")
    domain_comparison = defs.get("ComparisonSet", {})
    if domain_comparison.get("additionalProperties") is not False:
        problems.append("domain: ComparisonSet.additionalProperties must be false")
    if set(domain_comparison.get("x-forbidden-fields", [])) != FORBIDDEN_COMPARISON_FIELDS:
        problems.append("domain: ComparisonSet.x-forbidden-fields must list the 5 recommendation fields")
    if domain_comparison.get("properties") and any(
        forbidden in domain_comparison.get("properties", {}) for forbidden in FORBIDDEN_COMPARISON_FIELDS
    ):
        problems.append("domain: ComparisonSet must not declare forbidden fields")
    audit_events = set(defs.get("AuditEvent", {}).get("properties", {}).get("eventType", {}).get("enum", []))
    if audit_events != AUDIT_EVENT_TYPES:
        problems.append(f"domain: AuditEvent.eventType enum mismatch: {sorted(audit_events ^ AUDIT_EVENT_TYPES)}")
    version_status = set(defs.get("VersionStatus", {}).get("enum", []))
    if "PUBLISHED" not in version_status or "CONFLICT_BLOCKED" not in version_status:
        problems.append("domain: VersionStatus must contain PUBLISHED and CONFLICT_BLOCKED")
    domain_evidence = defs.get("EvidenceRef", {})
    if domain_evidence.get("x-aligned-contract") != "CTR-PK-EVR-001":
        problems.append("domain: EvidenceRef must declare x-aligned-contract CTR-PK-EVR-001")

    # 深校验（可选）：若环境提供 jsonschema，则证明“禁字段实例真的会被拒绝”。
    try:
        import jsonschema  # noqa: PLC0415

        validator_cls = jsonschema.Draft202012Validator
        good = {
            "comparisonSetId": "CS-1", "comparisonAsOf": "2026-09-20",
            "dimensions": [{"dimensionId": "d1", "dimensionName": "主要用途"}],
            "rows": [{"productId": "PROD-CM-003", "versionId": "V1", "values": {"d1": "x"}}],
            "reviewState": "PUBLISHED",
        }
        validator = validator_cls({"$ref": "#/$defs/ComparisonSet", "$defs": domain["$defs"]})
        validator.validate(good)
        for forbidden in FORBIDDEN_COMPARISON_FIELDS:
            bad = copy.deepcopy(good)
            bad[forbidden] = 0.99
            try:
                validator.validate(bad)
            except jsonschema.ValidationError:
                continue
            problems.append(f"domain: ComparisonSet instance with {forbidden} was ACCEPTED (guard is vacuous)")
    except ImportError:
        problems.append("environment: jsonschema not installed; deep instance validation skipped (structural checks only)")

    return problems


def _mutants(api: dict, domain: dict, contracts: list[dict]) -> list[tuple[str, dict, dict, list[dict]]]:
    """注入已知故障：每个变异必须让 detect 非空，否则断言空转。"""
    cases: list[tuple[str, dict, dict, list[dict]]] = []

    m_api = copy.deepcopy(api)
    m_api["paths"]["/product-center/products"]["get"]["responses"]["403"] = {
        "description": "broken response without PkcError",
        "content": {"application/json": {"schema": {"type": "object"}}},
    }
    cases.append(("M1: 403 response loses PkcError ref", m_api, domain, contracts))

    m_api = copy.deepcopy(api)
    m_api["components"]["schemas"]["PkcComparisonSet"]["additionalProperties"] = True
    cases.append(("M2: ComparisonSet allows extra fields", m_api, domain, contracts))

    m_api = copy.deepcopy(api)
    m_api["components"]["schemas"]["PkcCertaintyType"]["enum"].remove("NOT_APPLICABLE")
    cases.append(("M3: certainty enum drops NOT_APPLICABLE", m_api, domain, contracts))

    m_api = copy.deepcopy(api)
    m_api["components"]["schemas"]["PkcProductId"]["pattern"] = r"^DEMO-.*$"
    cases.append(("M4: productId pattern rewritten to DEMO-*", m_api, domain, contracts))

    m_domain = copy.deepcopy(domain)
    m_domain["$defs"]["AuditEvent"]["properties"]["eventType"]["enum"].remove("ASSISTANT_ASKED")
    cases.append(("M5: audit event ASSISTANT_ASKED removed", api, m_domain, contracts))

    m_contracts = [c for c in contracts if c.get("id") != "CTR-PKC-DOM-001"]
    cases.append(("M6: registry entry CTR-PKC-DOM-001 removed", api, domain, m_contracts))

    return cases


def self_test(api: dict, domain: dict, contracts: list[dict]) -> list[str]:
    baseline = detect(api, domain, contracts)
    if baseline:
        return [f"self-test: baseline must be clean before mutation, got {baseline}"]
    for name, m_api, m_domain, m_contracts in _mutants(api, domain, contracts):
        if not detect(m_api, m_domain, m_contracts):
            return [f"self-test: mutation NOT caught → {name} (detector is vacuous)"]
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="mutation re-verification (prove detector is not vacuous)")
    args = parser.parse_args()

    try:
        api = _load_json(API_SPEC)
        domain = _load_json(DOMAIN_SPEC)
        contracts = _load_registry_contracts()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"pkc-contract-tests: FAIL (fail-closed): {exc}")
        return 1

    if args.self_test:
        problems = self_test(api, domain, contracts)
        label = "self-test"
    else:
        problems = detect(api, domain, contracts)
        label = "check"

    if problems:
        print(f"pkc-contract-tests: {label} FAIL ({len(problems)})")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    print(f"pkc-contract-tests: {label} PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
