#!/usr/bin/env python3
"""一次性生成 gk-ke/v1 OpenAPI operation 级负例（L0-2 / WI-03）。

本脚本是**构建期工具**：生成 specs/gk-ke/v1/examples/openapi/negative/*.json。
命名约定 <operationId>_<n>.json（消费者测试按此解析）。
生成后由 scripts/gk_ke_openapi_contract_tests.py 消费，不参与运行时。
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NEG = ROOT / "specs" / "gk-ke" / "v1" / "examples" / "openapi" / "negative"

# (operationId, expect_status, rule, 描述, payload 内容)
CASES = [
    # --- 1. getCorePackageVersion ---
    ("getCorePackageVersion", 404, "RESOURCE_NOT_RESOLVED", "包版本未解析",
     {"instance": {"package": {"contractVersion": "gk-ke/v1", "simulationOnly": True,
                               "packageId": "SIM-CORE", "version": "9.9.9", "ownerSystem": "CORE",
                               "types": [{"typeId": "core.Customer", "definition": "x", "identityRule": "y"}],
                               "imports": []},
                  "hash": "47b41179c648d29a943f9d8d896b58eae170ea5b191fdde69d7228ecc3ff62c8"},
                  "unresolved": True}),
    ("getCorePackageVersion", 403, "AUTHZ_SCOPE_DENIED", "无该包授权",
     {"instance": {"package": {"contractVersion": "gk-ke/v1", "simulationOnly": True,
                               "packageId": "SIM-CORE", "version": "1.0.0", "ownerSystem": "CORE",
                               "types": [], "imports": []},
                  "hash": "47b41179c648d29a943f9d8d896b58eae170ea5b191fdde69d7228ecc3ff62c8"},
                  "authorized": False}),

    # --- 2. discoverCatalog ---
    ("discoverCatalog", 422, "PURPOSE_NOT_ALLOWED", "用途不在允许集",
     {"instance": {"taskType": "PRE_VISIT_PREPARATION", "purpose": "MARKETING_BLAST", "requestedScope": {"tenantId": "SIM-BANK", "orgIds": ["SIM-O01"], "purpose": "MARKETING_BLAST"}, "expectedVersion": "1"}}),
    ("discoverCatalog", 403, "REQUEST_SCOPE_AS_AUTHZ_EVIDENCE", "把请求 scope 当授权证据",
     {"instance": {"taskType": "PRE_VISIT_PREPARATION", "purpose": "INTERPRETATION", "requestedScope": {"tenantId": "SIM-BANK", "orgIds": ["SIM-O99"], "purpose": "INTERPRETATION"}, "expectedVersion": "1"}, "scopeUsedAsAuthz": True}),

    # --- 3. expandMap ---
    ("expandMap", 409, "DEPENDENCY_UNRESOLVED", "地图依赖未解析",
     {"instance": {"mapId": "SIM-MAP-FINANCE", "version": "1.0.0", "entryNode": "N-MISSING", "budget": 2000, "expectedVersion": "1.0.0"}, "dependencyUnresolved": True}),
    ("expandMap", 422, "ROOT_MAP_ID_STRING_MATCH", "按 mapId 字符串匹配根地图（应判 mapType==ROOT）",
     {"instance": {"mapId": "ROOT", "version": "1.0.0", "entryNode": "N-TASK", "budget": 2000, "expectedVersion": "1.0.0"}, "matchedByString": True}),

    # --- 4. createPlan ---
    ("createPlan", 409, "ROUTE_AMBIGUOUS", "同优先级路由歧义",
     {"instance": {"taskContext": {"taskId": "SIM-TASK-001", "taskType": "X"}, "mapRelease": {"id": "SIM-MAP-FINANCE", "version": "1.0.0"}, "dependencyVersions": {}, "expectedVersion": "1", "purpose": "INTERPRETATION", "scope": {"tenantId": "SIM-BANK", "orgIds": ["SIM-O01"], "purpose": "INTERPRETATION"}}, "routeAmbiguous": True}),
    ("createPlan", 422, "REQUIRED_CAPABILITY_MISSING", "必需能力缺失",
     {"instance": {"taskContext": {"taskId": "SIM-TASK-001", "taskType": "X"}, "mapRelease": {"id": "SIM-MAP-FINANCE", "version": "1.0.0"}, "dependencyVersions": {}, "expectedVersion": "1", "purpose": "INTERPRETATION", "scope": {"tenantId": "SIM-BANK", "orgIds": ["SIM-O01"], "purpose": "INTERPRETATION"}}, "missingCapability": True}),
    ("createPlan", 422, "PLAN_HASH_NONDETERMINISTIC", "planHash 含随机字段（planId/traceId/时间）",
     {"instance": {"planId": "SIM-PLAN-001", "planHash": "PLACEHOLDER"}, "planHashIncludesNondeterministic": True}),

    # --- 5. executeKnowledge ---
    ("executeKnowledge", 403, "DELEGATION_DENIED", "越权执行",
     {"instance": {"planId": "SIM-PLAN-001", "planHash": "9f2c", "capabilityInputs": [{"capabilityRef": "SIM-CAP-001", "stepId": "S1"}], "delegation": {"permissionDecisionRef": "SIM-PERM-999", "purpose": "INTERPRETATION", "expiresAt": "2026-09-12T12:00:00Z"}, "expectedVersion": "1"}, "authorized": False}),
    ("executeKnowledge", 409, "PLAN_HASH_MISMATCH", "planId/hash 版本不匹配",
     {"instance": {"planId": "SIM-PLAN-001", "planHash": "0000000000000000000000000000000000000000000000000000000000000000", "capabilityInputs": [{"capabilityRef": "SIM-CAP-001", "stepId": "S1"}], "delegation": {"permissionDecisionRef": "SIM-PERM-001", "purpose": "INTERPRETATION", "expiresAt": "2026-09-12T12:00:00Z"}, "expectedVersion": "1"}, "hashMismatch": True}),

    # --- 6. getKnowledgeJob ---
    ("getKnowledgeJob", 404, "JOB_NOT_FOUND", "作业不存在",
     {"instance": {"jobId": "SIM-JOB-MISSING"}, "notFound": True}),
    ("getKnowledgeJob", 422, "EMPTY_EVIDENCE_BUNDLE", "空 Bundle 当成功知识交付",
     {"instance": {"contractVersion": "gk-ke/v1", "simulationOnly": True, "bundleId": "SIM-B-1", "planId": "SIM-P-1", "releaseId": "SIM-R-1", "permissionDecisionRef": "SIM-PERM-001", "facts": [], "claims": [], "evidence": [], "ruleResults": [], "unknowns": [], "conflicts": [], "scope": {"tenantId": "SIM-BANK", "orgIds": ["SIM-O01"], "customerIds": ["SIM-C001"], "purpose": "INTERPRETATION"}}}),

    # --- 7. querySemantic ---
    ("querySemantic", 422, "SPARQL_REJECTED", "旧查询携带任意 SPARQL",
     {"instance": {"contractVersion": "gk-ke/v1", "simulationOnly": True, "metricId": "SIM-METRIC-001", "metricVersion": "1.0.0", "customerId": "SIM-C001", "period": {"from": "2026-08-01", "to": "2026-08-31"}, "snapshotId": "SIM-SNAP-001", "currency": "CNY", "purpose": "INTERPRETATION", "rawQuery": "SELECT ?s WHERE { ?s ?p ?o }"}}),
    ("querySemantic", 422, "GRANULARITY_MISMATCH", "粒度不符",
     {"instance": {"contractVersion": "gk-ke/v1", "simulationOnly": True, "metricId": "SIM-METRIC-001", "metricVersion": "1.0.0", "customerId": "SIM-C001", "period": {"from": "2026-08-01", "to": "2026-08-31"}, "snapshotId": "SIM-SNAP-001", "currency": "CNY", "purpose": "INTERPRETATION"}, "granularityMismatch": True}),
    ("querySemantic", 422, "CURRENCY_UNSUPPORTED", "币种不支持（CNY_ONLY 却传 USD）",
     {"instance": {"contractVersion": "gk-ke/v1", "simulationOnly": True, "metricId": "SIM-METRIC-001", "metricVersion": "1.0.0", "customerId": "SIM-C001", "period": {"from": "2026-08-01", "to": "2026-08-31"}, "snapshotId": "SIM-SNAP-001", "currency": "USD", "purpose": "INTERPRETATION"}, "currencyPolicy": "CNY_ONLY"}),
    ("querySemantic", 403, "SCOPE_DENIED", "范围越权",
     {"instance": {"contractVersion": "gk-ke/v1", "simulationOnly": True, "metricId": "SIM-METRIC-001", "metricVersion": "1.0.0", "customerId": "SIM-C999", "period": {"from": "2026-08-01", "to": "2026-08-31"}, "snapshotId": "SIM-SNAP-001", "currency": "CNY", "purpose": "INTERPRETATION"}, "authorized": False}),

    # --- 8. queryGraph ---
    ("queryGraph", 503, "GRAPH_UNAVAILABLE", "图服务不可用（不得返回 200 空结果）",
     {"instance": {"contractVersion": "gk-ke/v1", "simulationOnly": True, "queryId": "SIM-GQRY-001", "queryVersion": "1.0.0", "entityId": "SIM-C001", "releaseId": "SIM-REL-001", "maxHops": 2, "maxNodes": 50, "scope": {"tenantId": "SIM-BANK", "orgIds": ["SIM-O01"], "customerIds": ["SIM-C001"], "purpose": "INTERPRETATION"}}, "graphAvailable": False, "returns200Empty": True}),
    ("queryGraph", 409, "GRAPH_VERSION_CONFLICT", "图版本冲突",
     {"instance": {"contractVersion": "gk-ke/v1", "simulationOnly": True, "queryId": "SIM-GQRY-001", "queryVersion": "1.0.0", "entityId": "SIM-C001", "releaseId": "SIM-REL-001", "maxHops": 2, "maxNodes": 50, "scope": {"tenantId": "SIM-BANK", "orgIds": ["SIM-O01"], "customerIds": ["SIM-C001"], "purpose": "INTERPRETATION"}}, "graphVersionConflict": True}),
    ("queryGraph", 422, "UNBOUNDED_QUERY_REJECTED", "无界查询被拒",
     {"instance": {"contractVersion": "gk-ke/v1", "simulationOnly": True, "queryId": "SIM-GQRY-001", "queryVersion": "1.0.0", "entityId": "SIM-C001", "releaseId": "SIM-REL-001", "maxHops": 999, "maxNodes": 999999, "scope": {"tenantId": "SIM-BANK", "orgIds": ["SIM-O01"], "customerIds": ["SIM-C001"], "purpose": "INTERPRETATION"}}, "unbounded": True}),

    # --- 9. createIngestionJob ---
    ("createIngestionJob", 422, "SOURCE_NOT_REGISTERED", "来源未登记",
     {"instance": {"sourceVersionRef": {"id": "SIM-SRC-UNKNOWN", "version": "1.0.0"}, "extractionConfig": {}, "purpose": "INTERPRETATION", "expectedVersion": "1"}, "sourceRegistered": False}),
    ("createIngestionJob", 422, "PURPOSE_INELIGIBLE", "用途不合格",
     {"instance": {"sourceVersionRef": {"id": "SIM-SRC-DOC-001", "version": "1.0.0"}, "extractionConfig": {}, "purpose": "MARKETING", "expectedVersion": "1"}}),

    # --- 10. createReview ---
    ("createReview", 403, "SELF_REVIEW_FORBIDDEN", "审核人=提交人（自审）",
     {"instance": {"contractVersion": "gk-ke/v1", "simulationOnly": True, "decisionId": "SIM-REVIEW-002", "targetId": "SIM-REL-001", "targetVersion": "1.0.0", "targetHash": "85a23ed46d570b7d244be708743a562776cbaaac87f2626d60ec51a960aa6bba", "reviewerPrincipal": "SIM-AUTHOR", "authorPrincipal": "SIM-AUTHOR", "reviewerRole": "KNOWLEDGE_OWNER", "decision": "APPROVED", "purpose": "INTERPRETATION", "reason": "自审"}}),
    ("createReview", 409, "TARGET_HASH_MISMATCH", "审批后改字（hash 变化）",
     {"instance": {"contractVersion": "gk-ke/v1", "simulationOnly": True, "decisionId": "SIM-REVIEW-003", "targetId": "SIM-REL-001", "targetVersion": "1.0.0", "targetHash": "85a23ed46d570b7d244be708743a562776cbaaac87f2626d60ec51a960aa6bba", "hash": "0000000000000000000000000000000000000000000000000000000000000000", "reviewerPrincipal": "SIM-REVIEWER", "authorPrincipal": "SIM-AUTHOR", "reviewerRole": "KNOWLEDGE_OWNER", "decision": "APPROVED", "purpose": "INTERPRETATION", "reason": "hash 不符"}}),

    # --- 11. createRelease ---
    ("createRelease", 409, "CONCURRENT_MODIFICATION", "并发（expectedCatalogRevision 过期）",
     {"instance": {"contractVersion": "gk-ke/v1", "simulationOnly": True, "payload": {}, "payloadHash": "47b41179c648d29a943f9d8d896b58eae170ea5b191fdde69d7228ecc3ff62c8", "approvalRefs": ["SIM-REVIEW-001"], "projectionStates": [], "status": "APPROVED"}, "catalogRevisionStale": True}),
    ("createRelease", 422, "KNOWLEDGE_GATE_FAILED", "知识门禁未通过",
     {"instance": {"contractVersion": "gk-ke/v1", "simulationOnly": True, "payload": {}, "payloadHash": "47b41179c648d29a943f9d8d896b58eae170ea5b191fdde69d7228ecc3ff62c8", "approvalRefs": [], "projectionStates": [], "status": "APPROVED"}, "gateFailed": True}),
    ("createRelease", 422, "IN_PLACE_EDIT_FORBIDDEN", "原地编辑已发布版本（须新 releaseId）",
     {"instance": {"contractVersion": "gk-ke/v1", "simulationOnly": True, "payload": {}, "payloadHash": "47b41179c648d29a943f9d8d896b58eae170ea5b191fdde69d7228ecc3ff62c8", "approvalRefs": ["SIM-REVIEW-001"], "projectionStates": [], "status": "APPROVED"}, "inPlaceEdit": True}),

    # --- 12. revokeRelease ---
    ("revokeRelease", 403, "REVOKE_NOT_PERMITTED", "无撤销权限",
     {"instance": {"reason": "x", "expectedVersion": "1.0.0"}, "authorized": False}),
    ("revokeRelease", 409, "VERSION_CONFLICT", "expectedVersion 冲突",
     {"instance": {"reason": "x", "expectedVersion": "9.9.9"}, "versionConflict": True}),

    # --- 13. createTaskAction ---
    ("createTaskAction", 403, "CONFIRMATION_MISSING", "未确认",
     {"instance": {"action": {"contractVersion": "gk-ke/v1", "simulationOnly": True, "actionId": "SIM-A-1", "taskId": "SIM-TASK-001", "actionType": "CREATE_FOLLOWUP_TASK", "customerId": "SIM-C001", "parametersHash": "431fa58621ef66a373621c0b7f764bcfdff20e8ee63e409ca0dc8b15481a7413", "confirmationRef": "", "targetVersion": 1, "idempotencyKey": "K1", "mode": "SIMULATION", "purpose": "x"}, "confirmationRef": "", "expectedTargetVersion": "1", "purpose": "INTERPRETATION", "expectedVersion": "1"}, "notConfirmed": True}),
    ("createTaskAction", 409, "TARGET_VERSION_STALE", "目标版本失效",
     {"instance": {"action": {"contractVersion": "gk-ke/v1", "simulationOnly": True, "actionId": "SIM-A-1", "taskId": "SIM-TASK-001", "actionType": "CREATE_FOLLOWUP_TASK", "customerId": "SIM-C001", "parametersHash": "431fa58621ef66a373621c0b7f764bcfdff20e8ee63e409ca0dc8b15481a7413", "confirmationRef": "SIM-CONFIRM-001", "targetVersion": 1, "idempotencyKey": "K1", "mode": "SIMULATION", "purpose": "x"}, "confirmationRef": "SIM-CONFIRM-001", "expectedTargetVersion": "99", "purpose": "INTERPRETATION", "expectedVersion": "1"}, "targetVersionStale": True}),
    ("createTaskAction", 422, "PARAMETERS_HASH_MISMATCH", "parametersHash 与实际参数不符（名义未用额度被写成可提款）",
     {"instance": {"action": {"contractVersion": "gk-ke/v1", "simulationOnly": True, "actionId": "SIM-A-1", "taskId": "SIM-TASK-001", "actionType": "CREATE_FOLLOWUP_TASK", "customerId": "SIM-C001", "parametersHash": "0000000000000000000000000000000000000000000000000000000000000000", "confirmationRef": "SIM-CONFIRM-001", "targetVersion": 1, "idempotencyKey": "K1", "mode": "SIMULATION", "purpose": "x"}, "confirmationRef": "SIM-CONFIRM-001", "expectedTargetVersion": "1", "purpose": "INTERPRETATION", "expectedVersion": "1", "parametersHash": "431fa58621ef66a373621c0b7f764bcfdff20e8ee63e409ca0dc8b15481a7413"}, "hashMismatch": True}),

    # --- 14. createSimAction ---
    ("createSimAction", 422, "SIM_ACTION_NOT_WHITELISTED", "白名单外动作：转账",
     {"instance": {"actionType": "TRANSFER_FUNDS", "targetVersion": "1", "confirmationRef": "SIM-CONFIRM-001", "expectedVersion": "1.0.0"}}),
    ("createSimAction", 422, "SIM_ACTION_NOT_WHITELISTED", "白名单外动作：放款",
     {"instance": {"actionType": "DISBURSE_LOAN", "targetVersion": "1", "confirmationRef": "SIM-CONFIRM-001", "expectedVersion": "1.0.0"}}),
    ("createSimAction", 422, "SIM_ACTION_NOT_WHITELISTED", "白名单外动作：授信审批",
     {"instance": {"actionType": "APPROVE_CREDIT", "targetVersion": "1", "confirmationRef": "SIM-CONFIRM-001", "expectedVersion": "1.0.0"}}),
    ("createSimAction", 409, "IDEMPOTENCY_CONFLICT", "相同幂等键不同 payload",
     {"instance": {"actionType": "CREATE_FOLLOWUP_TASK", "targetVersion": "1", "confirmationRef": "SIM-CONFIRM-001", "expectedVersion": "1.0.0"}, "sameKeyDifferentPayload": True}),
    ("createSimAction", 409, "IDEMPOTENCY_CONFLICT", "相同幂等键不同 payload（状态冲突）",
     {"instance": {"actionType": "RECORD_CONTACT_OUTCOME", "targetVersion": "1", "confirmationRef": "SIM-CONFIRM-002", "expectedVersion": "1.0.0"}, "sameKeyDifferentPayload": True}),

    # --- 15. getSimAction ---
    ("getSimAction", 404, "INTENT_NOT_FOUND", "未见该意图",
     {"instance": {"actionId": "SIM-SIMACTION-999"}, "notFound": True}),
    ("getSimAction", 403, "QUERY_NOT_PERMITTED", "无权查询目标动作",
     {"instance": {"actionId": "SIM-SIMACTION-001"}, "authorized": False}),
    ("getSimAction", 422, "SERVER_PATH_LEAK", "响应泄露服务器路径/凭据/SQL",
     {"instance": {"actionId": "SIM-SIMACTION-001", "status": "EXECUTED", "simulationOnly": True, "serverPath": "/home/szf/sim/db.sqlite", "sql": "SELECT * FROM actions"}}),

    # --- 22. scope 被当作授权证据 / 时间格式 / 金额浮点（跨 operation 合同级负例） ---
    ("discoverCatalog", 422, "TIMESTAMP_NOT_RFC3339", "时间非 RFC3339",
     {"instance": {"taskType": "X", "purpose": "INTERPRETATION", "requestedScope": {"tenantId": "SIM-BANK", "orgIds": ["SIM-O01"], "purpose": "INTERPRETATION"}, "expectedVersion": "1", "occurredAt": "2026/09/12 10:00"}}),
    ("querySemantic", 422, "MONEY_TYPE_NUMBER", "金额用浮点（禁止）",
     {"instance": {"evidenceRefs": [], "unknowns": [], "conflicts": [], "type": "number", "amount": 2983333.33}}),
    ("getKnowledgeJob", 422, "LLM_OVERRIDES_RULE", "LLM 覆盖规则判定（缺 ruleRef/premiseRefs）",
     {"instance": {"contractVersion": "gk-ke/v1", "simulationOnly": True, "bundleId": "SIM-B-2", "planId": "SIM-P-1", "releaseId": "SIM-R-1", "permissionDecisionRef": "SIM-PERM-001", "facts": [], "claims": [], "evidence": [{"evidenceRef": "SIM-EVR-001"}], "ruleResults": [{"result": "TRUE"}], "unknowns": ["SIM-U-1"], "conflicts": [], "scope": {"tenantId": "SIM-BANK", "orgIds": ["SIM-O01"], "customerIds": ["SIM-C001"], "purpose": "INTERPRETATION"}}}),
    ("getKnowledgeJob", 422, "ATTRIBUTION_LOST", "客户声明与银行已验证混淆（claims 缺 modality/speaker）",
     {"instance": {"contractVersion": "gk-ke/v1", "simulationOnly": True, "bundleId": "SIM-B-3", "planId": "SIM-P-1", "releaseId": "SIM-R-1", "permissionDecisionRef": "SIM-PERM-001", "facts": [], "claims": [{"claimId": "SIM-CLAIM-002"}], "evidence": [{"evidenceRef": "SIM-EVR-001"}], "ruleResults": [{"ruleRef": "SIM-RULE-001", "result": "TRUE", "premiseRefs": ["SIM-AS-001"]}], "unknowns": ["SIM-U-1"], "conflicts": [], "scope": {"tenantId": "SIM-BANK", "orgIds": ["SIM-O01"], "customerIds": ["SIM-C001"], "purpose": "INTERPRETATION"}}}),
]


def main() -> int:
    NEG.mkdir(parents=True, exist_ok=True)
    counters: dict[str, int] = {}
    for op_id, status, rule, description, body in CASES:
        counters[op_id] = counters.get(op_id, 0) + 1
        payload = {
            "expect": {"operationId": op_id, "status": status, "rule": rule, "reason": description},
        }
        payload.update(body)
        path = NEG / f"{op_id}_{counters[op_id]}.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"generated {sum(counters.values())} negative examples for {len(counters)} operations")
    for op_id in sorted(counters):
        print(f"  {op_id}: {counters[op_id]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
