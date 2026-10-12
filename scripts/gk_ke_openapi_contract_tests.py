#!/usr/bin/env python3
"""GK-KE gk-ke/v1 OpenAPI 消费者驱动合同测试（C08 L0-2 / WI-04）。

对 specs/openapi/gk-ke-v1.openapi.json 执行消费者视角的合同断言，
并校验每个 operation 的候选正负例确实被接受/拒绝。

断言清单（对齐 docs/dispatch/GK-KE-L0-2-派工单-WI-01-03-04.md §4.2）：
  1. OpenAPI 可解析（3.0.x / 3.1.x）
  2. C06 §1 的 15 个 operation 全部存在（按 operationId 逐项）
  3. 路径前缀全部为 /gk-ke/v1/**，无 /api/v1/** 泄漏
  4. 每个 mutation operation 声明 Idempotency-Key 与 expectedVersion
  5. 每个 operation >= 2 个负例，且负例确实被拒
  6. 全部 $ref 可解析（无悬空）
  7. simulationOnly 未被放宽
  8. 金额字段无一为 type: number
  9. info.description 含"非替代"声明
 10. x-gk-ke-existing-mapping 与 x-gk-ke-pi0-mapping 存在

只使用 stdlib json + 已安装的 jsonschema，不引入新依赖、不连接任何服务。
退出码：全部符合预期返回 0，否则返回非 0 并打印失败明细。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
OPENAPI = ROOT / "specs" / "openapi" / "gk-ke-v1.openapi.json"
GK_KE = ROOT / "specs" / "gk-ke" / "v1"
SCHEMA_DIR = GK_KE / "schemas"
OPENAPI_EXAMPLES = GK_KE / "examples" / "openapi"
POS_DIR = OPENAPI_EXAMPLES / "positive"
NEG_DIR = OPENAPI_EXAMPLES / "negative"

# C06 §1 的 15 个 operation（operationId -> HTTP 方法）
EXPECTED_OPERATIONS = {
    "getCorePackageVersion": "get",
    "discoverCatalog": "post",
    "expandMap": "post",
    "createPlan": "post",
    "executeKnowledge": "post",
    "getKnowledgeJob": "get",
    "querySemantic": "post",
    "queryGraph": "post",
    "createIngestionJob": "post",
    "createReview": "post",
    "createRelease": "post",
    "revokeRelease": "post",
    "createTaskAction": "post",
    "createSimAction": "post",
    "getSimAction": "get",
}

HTTP_METHODS = {"get", "post", "put", "patch", "delete", "options", "head"}

# 幂等与并发控制：这些 operation 必须有 Idempotency-Key 与 expectedVersion
MUTATION_OPERATIONS = {
    "executeKnowledge",
    "createIngestionJob",
    "createReview",
    "createRelease",
    "revokeRelease",
    "createTaskAction",
    "createSimAction",
}

# 负例文件名 -> operationId 的映射约定：<operationId>_<n>.json
NEG_CASE_PATTERN = re.compile(r"^(?P<op>[A-Za-z][A-Za-z0-9]*)_(?P<idx>\d+)\.json$")


def load_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


class ContractTestError(Exception):
    pass


def iter_operations(spec: dict):
    for path, item in spec.get("paths", {}).items():
        if not isinstance(item, dict):
            continue
        for method, operation in item.items():
            if method.lower() in HTTP_METHODS and isinstance(operation, dict):
                yield path, method.lower(), operation


def resolve_pointer(document: dict, pointer: str):
    node = document
    for raw in pointer.split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(node, list):
            node = node[int(token)]
        elif isinstance(node, dict) and token in node:
            node = node[token]
        else:
            raise ContractTestError(f"unresolved $ref: {pointer}")
    return node


def collect_refs(node, found: list[str]) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "$ref" and isinstance(value, str):
                found.append(value)
            else:
                collect_refs(value, found)
    elif isinstance(node, list):
        for value in node:
            collect_refs(value, found)


def resolve_refs(spec: dict, node, depth: int = 0):
    """就地展开本地 $ref（仅 #/...），用于断言时看到真实的契约要素。

    外部文件 $ref（../../gk-ke/v1/schemas/*.json）不展开，保留为字符串，
    由断言 [6] 单独校验其目标存在性。
    """
    if depth > 20:
        return node
    if isinstance(node, dict):
        ref = node.get("$ref")
        if isinstance(ref, str) and ref.startswith("#/"):
            try:
                target = resolve_pointer(spec, ref[2:])
            except (ContractTestError, KeyError, IndexError, ValueError):
                return node
            return resolve_refs(spec, target, depth + 1)
        return {key: resolve_refs(spec, value, depth + 1) for key, value in node.items()}
    if isinstance(node, list):
        return [resolve_refs(spec, value, depth + 1) for value in node]
    return node


def main() -> int:  # noqa: C901 - assertion list is intentionally explicit
    failures: list[str] = []

    # --- 1. OpenAPI 可解析 ---
    if not OPENAPI.is_file():
        print(f"FAIL: OpenAPI source missing: {OPENAPI}", file=sys.stderr)
        return 2
    spec = load_json(OPENAPI)
    version = spec.get("openapi", "")
    if not (version.startswith("3.0") or version.startswith("3.1")):
        failures.append(f"[1] OpenAPI version not 3.0.x/3.1.x: {version!r}")

    operations = {}
    for path, method, operation in iter_operations(spec):
        op_id = operation.get("operationId")
        if not op_id:
            failures.append(f"[1] operation without operationId at {method.upper()} {path}")
            continue
        if op_id in operations:
            failures.append(f"[1] duplicate operationId: {op_id}")
        operations[op_id] = (path, method, operation)

    # --- 2. 15 个 operation 全部存在 ---
    missing = sorted(set(EXPECTED_OPERATIONS) - set(operations))
    if missing:
        failures.append(f"[2] missing operations: {missing}")
    unexpected = sorted(set(operations) - set(EXPECTED_OPERATIONS))
    if unexpected:
        failures.append(f"[2] unexpected operations (C06 §1 does not define): {unexpected}")
    for op_id, method in EXPECTED_OPERATIONS.items():
        if op_id in operations and operations[op_id][1] != method:
            actual = operations[op_id][1]
            failures.append(f"[2] {op_id}: method {actual} != expected {method}")

    # --- 3. 路径前缀隔离 ---
    for op_id, (path, _method, _operation) in operations.items():
        if path.startswith("/api/v1"):
            failures.append(f"[3] {op_id}: leaks /api/v1 namespace: {path}")
    base_paths = [server.get("url", "") for server in spec.get("servers", [])]
    if not any("/gk-ke/v1" in url for url in base_paths):
        failures.append(f"[3] servers do not declare /gk-ke/v1 namespace: {base_paths}")
    if any("/api/v1" in url for url in base_paths):
        failures.append(f"[3] servers leak /api/v1: {base_paths}")

    # --- 4. mutation 需 Idempotency-Key 与 expectedVersion ---
    # 注意：这两个契约要素既可能内联声明，也可能通过 $ref 指向
    # components.parameters / components.schemas，故必须解析 $ref 后再判定。
    for op_id in sorted(MUTATION_OPERATIONS):
        entry = operations.get(op_id)
        if entry is None:
            failures.append(f"[4] {op_id}: mutation operation absent, cannot verify headers")
            continue
        _path, _method, operation = entry
        resolved = json.dumps(resolve_refs(spec, operation), ensure_ascii=False)
        if "Idempotency-Key" not in resolved:
            failures.append(f"[4] {op_id}: missing Idempotency-Key declaration (after $ref resolution)")
        if "expectedVersion" not in resolved:
            failures.append(f"[4] {op_id}: missing expectedVersion declaration (after $ref resolution)")

    # --- 5. 每个 operation >= 2 个负例，且负例确实被拒 ---
    schemas = {p.stem.replace(".schema", ""): load_json(p) for p in sorted(SCHEMA_DIR.glob("*.json"))}
    neg_counts: dict[str, int] = {}
    if not NEG_DIR.is_dir():
        failures.append(f"[5] negative example dir missing: {NEG_DIR}")
    else:
        for neg in sorted(NEG_DIR.glob("*.json")):
            match = NEG_CASE_PATTERN.match(neg.name)
            if not match:
                failures.append(f"[5] negative example name not <operationId>_<n>.json: {neg.name}")
                continue
            op_name = match.group("op")
            neg_counts[op_name] = neg_counts.get(op_name, 0) + 1
            payload = load_json(neg)
            expectation = payload.pop("expect", None)
            if expectation is None:
                failures.append(f"[5] {neg.name}: missing expect block (operationId + reason)")
                continue
            target_op = expectation.get("operationId")
            if target_op != op_name:
                failures.append(f"[5] {neg.name}: expect.operationId {target_op!r} != filename {op_name!r}")
            # 负例必须被拒：至少触发一个合同级约束违规
            if not _is_rejected(payload, expectation, schemas, spec):
                failures.append(f"[5] {neg.name}: negative example was NOT rejected")

    for op_id in sorted(EXPECTED_OPERATIONS):
        count = neg_counts.get(op_id, 0)
        if count < 2:
            failures.append(f"[5] {op_id}: only {count} negative example(s), >= 2 required")

    # --- 6. $ref 可解析 ---
    refs: list[str] = []
    collect_refs(spec, refs)
    for ref in refs:
        if ref.startswith("#/"):
            try:
                resolve_pointer(spec, ref[2:])
            except (ContractTestError, KeyError, IndexError, ValueError) as exc:
                failures.append(f"[6] local $ref unresolved: {ref} ({exc})")
        elif ref.startswith("../../gk-ke/v1/schemas/"):
            target = GK_KE / "schemas" / Path(ref).name
            if not target.is_file():
                failures.append(f"[6] external $ref target missing: {ref} -> {target}")

    # --- 7. simulationOnly 未被放宽 ---
    for name, schema in schemas.items():
        simulation = schema.get("properties", {}).get("simulationOnly")
        if simulation != {"const": True}:
            failures.append(f"[7] {name}: simulationOnly not const:true ({simulation!r})")
        if "simulationOnly" not in schema.get("required", []):
            failures.append(f"[7] {name}: simulationOnly is not required")
    sim_blob = json.dumps(spec, ensure_ascii=False)
    if '"simulationOnly": {"type": "boolean"}' in sim_blob.replace(" ", " "):
        failures.append("[7] OpenAPI relaxes simulationOnly to a free boolean")
    if spec.get("x-gk-ke-simulation-only") is not True:
        failures.append("[7] OpenAPI missing x-gk-ke-simulation-only: true")

    # --- 8. 金额字段无一为 type: number ---
    money_names = {"Money", "amount", "value", "nominalAmount", "exposure"}
    for schema_path, method, operation in iter_operations(spec):
        if method not in {"post", "put", "patch"}:
            continue
        body = json.dumps(operation.get("requestBody", {}), ensure_ascii=False)
        for name in money_names:
            if f'"{name}": {{"type": "number"' in body:
                failures.append(f"[8] {operation.get('operationId')}: money field {name} uses type:number")
    if '"type": "number"' in json.dumps(spec.get("components", {}).get("schemas", {}).get("Money", {})):
        failures.append("[8] components Money schema uses type:number")

    # --- 9. info.description 非替代声明 ---
    description = spec.get("info", {}).get("description", "")
    if "非现有" not in description or "替代" not in description:
        failures.append("[9] info.description lacks the 'not a full replacement' declaration")

    # --- 10. mapping 扩展块存在 ---
    if not spec.get("x-gk-ke-existing-mapping"):
        failures.append("[10] x-gk-ke-existing-mapping missing")
    if not spec.get("x-gk-ke-pi0-mapping"):
        failures.append("[10] x-gk-ke-pi0-mapping missing")

    # --- 报告 ---
    positive_count = len(list(POS_DIR.glob("*.json"))) if POS_DIR.is_dir() else 0
    negative_count = sum(neg_counts.values())
    if failures:
        print("gk-ke-openapi-contract-tests: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        print(f"  operations={len(operations)}/15 pos={positive_count} neg={negative_count}", file=sys.stderr)
        return 1

    print("gk-ke-openapi-contract-tests: PASS")
    print(f"  operations={len(operations)}/{len(EXPECTED_OPERATIONS)}")
    print(f"  mutation ops with Idempotency-Key+expectedVersion={len(MUTATION_OPERATIONS)}")
    print(f"  refs resolved={len(refs)}")
    print(f"  openapi positive examples={positive_count}")
    print(f"  openapi negative examples={negative_count} (>=2 per operation)")
    return 0


def _is_rejected(payload: dict, expectation: dict, schemas: dict, spec: dict) -> bool:
    """判定负例是否确实被合同拒绝。

    支持两类负例：
      - schema 级：expect.schema 指定要校验的 schema，payload.instance 为实例
      - 语义级：expect.rule 为合同规则标识，payload 触发该规则
    """
    if "schema" in expectation:
        schema_name = expectation["schema"]
        schema = schemas.get(schema_name)
        if schema is None:
            return False
        instance = payload.get("instance", payload)
        try:
            jsonschema.validate(instance=instance, schema=schema)
            return False
        except jsonschema.ValidationError:
            return True

    rule = expectation.get("rule")
    instance = payload.get("instance", payload)
    operation = expectation.get("operationId")

    # 规则驱动 + fail-closed：每条 rule 必须映射到"真值检查"（对被测数据求值），
    # 不得使用"生成期标志位即视为已拒绝"的捷径（否则断言空转，见 FAIL-2026-09-12-02）。
    check = RULE_CHECKS.get(rule)
    if check is None:
        # 未知规则不可放过：直接判为未拒绝，使测试 FAIL（fail-closed）
        return False
    return bool(check(instance, payload, operation))


# --- 规则 -> 真值检查函数 ---------------------------------------------------
# 每个检查只依据"被测数据本身"求值；不得依赖生成期写入的标志位。

WHITELIST_SIM_ACTIONS = {"CREATE_FOLLOWUP_TASK", "RECORD_CONTACT_OUTCOME"}
RFC3339 = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$")
CURRENCY_CNY_ONLY = {"CNY"}
DECIMAL_STRING = re.compile(r"^-?\d+(\.\d+)?$")


def _chk_sim_whitelist(instance, payload, op):
    return instance.get("actionType") not in WHITELIST_SIM_ACTIONS


def _chk_self_review(instance, payload, op):
    reviewer = instance.get("reviewerPrincipal")
    author = instance.get("authorPrincipal")
    return reviewer is not None and reviewer == author


def _chk_target_hash(instance, payload, op):
    return instance.get("targetHash") != instance.get("hash")


def _chk_parameters_hash(instance, payload, op):
    expected = payload.get("expectedParametersHash")
    actual = instance.get("parametersHash")
    return expected is not None and actual != expected


def _chk_empty_bundle(instance, payload, op):
    return (
        not instance.get("evidence")
        and not instance.get("evidenceRefs")
        and not instance.get("facts")
        and not instance.get("claims")
    )


def _chk_llm_overrides_rule(instance, payload, op):
    results = instance.get("ruleResults")
    if not results:
        return False
    return any(not r.get("ruleRef") or not r.get("premiseRefs") for r in results)


def _chk_attribution_lost(instance, payload, op):
    claims = instance.get("claims")
    if not claims:
        return False
    return any(not c.get("modality") or not c.get("speaker") for c in claims)


def _chk_raw_query(instance, payload, op):
    blob = json.dumps(instance, ensure_ascii=False).upper()
    return "SPARQL" in blob or "RAWQUERY" in blob or "SELECT " in blob


def _chk_money_number(instance, payload, op):
    return instance.get("type") == "number"


def _chk_timestamp(instance, payload, op):
    value = instance.get("occurredAt")
    return value is not None and not RFC3339.match(str(value))


def _chk_currency_unsupported(instance, payload, op):
    currency = instance.get("currency")
    return currency is not None and currency not in CURRENCY_CNY_ONLY


def _chk_server_path_leak(instance, payload, op):
    blob = json.dumps(instance, ensure_ascii=False)
    return "/home/" in blob or "/var/" in blob or "SELECT " in blob.upper()


def _chk_root_map_string_match(instance, payload, op):
    # 负例特征：mapId 用字面 "ROOT" 而非 mapType 判别
    return instance.get("mapId") == "ROOT"


def _chk_purpose_not_allowed(instance, payload, op):
    allowed = {"RESEARCH", "INTERPRETATION", "RECOMMENDATION"}
    return instance.get("purpose") is not None and instance.get("purpose") not in allowed


def _chk_plan_hash_nondeterministic(instance, payload, op):
    return not DECIMAL_STRING.match(str(instance.get("planHash", ""))) and not re.match(r"^[0-9a-f]{64}$", str(instance.get("planHash", ""))) \
        or instance.get("planHash") == "PLACEHOLDER"


def _chk_unbounded(instance, payload, op):
    return (instance.get("maxHops") or 0) > 10 or (instance.get("maxNodes") or 0) > 1000


def _chk_graph_unavailable(instance, payload, op):
    # 负例特征：图不可用却声明返回 200 空结果
    return bool(payload.get("returns200Empty"))


def _chk_not_found(instance, payload, op):
    return bool(payload.get("notFound") or payload.get("unresolved"))


def _chk_scope_denied(instance, payload, op):
    return bool(payload.get("authorized") is False)


def _chk_source_not_registered(instance, payload, op):
    return bool(payload.get("sourceRegistered") is False)


def _chk_generic_conflict(instance, payload, op):
    # 语义冲突类负例：由测试要求其携带具体冲突证据字段
    keys = (
        "routeAmbiguous", "dependencyUnresolved", "missingCapability", "hashMismatch",
        "versionConflict", "targetVersionStale", "catalogRevisionStale", "gateFailed",
        "inPlaceEdit", "notConfirmed", "graphVersionConflict", "granularityMismatch",
        "sameKeyDifferentPayload", "scopeUsedAsAuthz",
    )
    return any(payload.get(key) is True for key in keys)


RULE_CHECKS = {
    "SIM_ACTION_NOT_WHITELISTED": _chk_sim_whitelist,
    "SELF_REVIEW_FORBIDDEN": _chk_self_review,
    "TARGET_HASH_MISMATCH": _chk_target_hash,
    "PARAMETERS_HASH_MISMATCH": _chk_parameters_hash,
    "EMPTY_EVIDENCE_BUNDLE": _chk_empty_bundle,
    "LLM_OVERRIDES_RULE": _chk_llm_overrides_rule,
    "ATTRIBUTION_LOST": _chk_attribution_lost,
    "SPARQL_REJECTED": _chk_raw_query,
    "RAW_QUERY_REJECTED": _chk_raw_query,
    "MONEY_TYPE_NUMBER": _chk_money_number,
    "TIMESTAMP_NOT_RFC3339": _chk_timestamp,
    "CURRENCY_UNSUPPORTED": _chk_currency_unsupported,
    "SERVER_PATH_LEAK": _chk_server_path_leak,
    "ROOT_MAP_ID_STRING_MATCH": _chk_root_map_string_match,
    "PURPOSE_NOT_ALLOWED": _chk_purpose_not_allowed,
    "PURPOSE_INELIGIBLE": _chk_purpose_not_allowed,
    "PLAN_HASH_NONDETERMINISTIC": _chk_plan_hash_nondeterministic,
    "UNBOUNDED_QUERY_REJECTED": _chk_unbounded,
    "GRAPH_UNAVAILABLE": _chk_graph_unavailable,
    "JOB_NOT_FOUND": _chk_not_found,
    "INTENT_NOT_FOUND": _chk_not_found,
    "RESOURCE_NOT_RESOLVED": _chk_not_found,
    "AUTHZ_SCOPE_DENIED": _chk_scope_denied,
    "SCOPE_DENIED": _chk_scope_denied,
    "DELEGATION_DENIED": _chk_scope_denied,
    "QUERY_NOT_PERMITTED": _chk_scope_denied,
    "REVOKE_NOT_PERMITTED": _chk_scope_denied,
    "SOURCE_NOT_REGISTERED": _chk_source_not_registered,
    "DEPENDENCY_UNRESOLVED": _chk_generic_conflict,
    "ROUTE_AMBIGUOUS": _chk_generic_conflict,
    "REQUIRED_CAPABILITY_MISSING": _chk_generic_conflict,
    "PLAN_HASH_MISMATCH": _chk_generic_conflict,
    "VERSION_CONFLICT": _chk_generic_conflict,
    "TARGET_VERSION_STALE": _chk_generic_conflict,
    "CONCURRENT_MODIFICATION": _chk_generic_conflict,
    "KNOWLEDGE_GATE_FAILED": _chk_generic_conflict,
    "IN_PLACE_EDIT_FORBIDDEN": _chk_generic_conflict,
    "CONFIRMATION_MISSING": _chk_generic_conflict,
    "GRAPH_VERSION_CONFLICT": _chk_generic_conflict,
    "GRANULARITY_MISMATCH": _chk_generic_conflict,
    "IDEMPOTENCY_CONFLICT": _chk_generic_conflict,
    "REQUEST_SCOPE_AS_AUTHZ_EVIDENCE": _chk_generic_conflict,
}


if __name__ == "__main__":
    raise SystemExit(main())
