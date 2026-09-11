#!/usr/bin/env python3
"""生成 GK-KE L4-1 地图激活夹具（C08 L4-1 / wave D2）。

依据 C06 §2 确定性计划 + OWNER-003 §4.2 路由规则（无匹配与歧义分别处理）。
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "specs" / "knowledge-architecture" / "activation"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    task_template = {
        "simulationOnly": True,
        "taskId": "SIM-TASK-001",
        "taskType": "FINANCE_VISIT_PREP",
        "customerId": "SIM-C001",
        "asOf": "2026-09-12T10:00:00+08:00",
        "businessDate": "2026-09-12",
        "identityBy": "customerId",
        "nameSubstitutionForbidden": True,
        "frozenFields": ["taskId", "taskType", "customerId", "asOf", "businessDate",
                         "sourceSnapshotId", "permissionScopeHash"],
        "sourceSnapshotId": "SIM-SNAPSHOT-20261001",
        "permissionScopeHash": "a" * 64,
    }

    map_spec = {
        "simulationOnly": True,
        "mapId": "SIM-MAP-FINANCE",
        "version": "1.0.0",
        "releaseId": "SIM-REL-001",
        "entryNodes": ["N-TASK"],
        "taskTypes": ["FINANCE_VISIT_PREP"],
        "purpose": "INTERPRETATION",
        "routePolicyRef": "SIM-ROUTE-001",
        "defaultPolicy": "DENY",
        "maxInitialTokens": 2000,
        "coverage": {"assetRefsResolvable": True, "capabilityRefsResolvable": True},
    }

    # 路由策略：含 1 条正常规则、0 条 UNKNOWN_TASK、2 条同优先级 AMBIGUOUS_TASK
    route_policy = {
        "simulationOnly": True,
        "policyId": "SIM-ROUTE-001",
        "version": "1.0.0",
        "defaultDecision": "REJECT_NO_MATCH",
        "rules": [
            {"ruleId": "SIM-RR-001", "priority": 20, "taskType": "FINANCE_VISIT_PREP",
             "mode": "ONTOLOGY_THEN_MAP", "mapRef": "SIM-MAP-FINANCE",
             "activationContractRef": "AC-PREVISIT-001"},
            {"ruleId": "SIM-RR-A1", "priority": 30, "taskType": "AMBIGUOUS_TASK",
             "mode": "MAP_FIRST", "mapRef": "SIM-MAP-FINANCE"},
            {"ruleId": "SIM-RR-A2", "priority": 30, "taskType": "AMBIGUOUS_TASK",
             "mode": "ONTOLOGY_FIRST", "mapRef": "SIM-MAP-FINANCE"},
        ],
    }

    activation_plan = {
        "simulationOnly": True,
        "planId": "SIM-PLAN-001",
        "traceId": "SIM-TRACE-001",
        "createdAt": "2026-09-12T10:00:00+08:00",
        "taskId": "SIM-TASK-001",
        "mapRef": {"id": "SIM-MAP-FINANCE", "version": "1.0.0"},
        "releaseId": "SIM-REL-001",
        "coreVersion": "1.0.0",
        "catalogRevision": 2,
        "routePolicyVersion": "1.0.0",
        "assetRefs": [{"id": "SIM-ASSET-P001", "version": "1.0.0"},
                      {"id": "SIM-ASSET-METRIC", "version": "1.0.0"}],
        "capabilityRefs": [{"id": "SIM-CAP-INTERPRET", "version": "1.0.0"}],
        "queryRefs": [{"id": "SIM-QRY-AVG-DEPOSIT", "version": "1.0.0"}],
        "requiredCapabilityRefs": ["SIM-CAP-INTERPRET"],
        "steps": [
            {"stepId": "S1", "executorRef": "SIM-CAP-INTERPRET",
             "inputBindings": {"customerId": "SIM-C001", "assetRef": "SIM-ASSET-P001"},
             "dependencyStepIds": [], "evidenceRequirement": "SIM-EVR-001",
             "onFailure": "FAIL_CLOSED", "sideEffect": "NONE"},
            {"stepId": "S2", "executorRef": "SIM-CAP-INTERPRET",
             "inputBindings": {"customerId": "SIM-C001", "queryRef": "SIM-QRY-AVG-DEPOSIT"},
             "dependencyStepIds": ["S1"], "evidenceRequirement": "SIM-EVR-002",
             "onFailure": "FAIL_CLOSED", "sideEffect": "READ_ONLY"},
        ],
        "permissionDecisionRef": "SIM-PERM-001",
        "purpose": "INTERPRETATION",
        "scope": {"tenantId": "SIM-BANK", "orgIds": ["SIM-O01"],
                  "customerIds": ["SIM-C001"], "purpose": "INTERPRETATION"},
        "budget": {"maxSteps": 5, "maxTokens": 2000, "timeoutMs": 60000},
        "planHashNote": "canonical planHash 只对确定的执行语义字段计算；"
                        "随机 planId、traceId、创建时间及签名包络排除在外（C06 §2）。",
    }

    violations = {
        "simulationOnly": True,
        "violations": [
            {"case": "route_ambiguous", "expectedError": "ROUTE_AMBIGUOUS",
             "description": "同优先级多规则，无法唯一选择", "detected": True},
            {"case": "no_match_reject", "expectedError": "NO_MATCH_REJECT",
             "description": "无匹配规则，必须拒绝而非用默认模式扩大任务集合", "detected": True},
            {"case": "required_capability_missing", "expectedError": "REQUIRED_CAPABILITY_MISSING",
             "description": "计划必需能力缺失", "detected": True},
            {"case": "dependency_cycle", "expectedError": "DEPENDENCY_CYCLE",
             "description": "执行子图成环，非 DAG", "detected": True},
            {"case": "gits_writeback_in_kert_plan", "expectedError": "GITS_WRITEBACK_IN_KERT_PLAN",
             "description": "KERT 计划含 GITS 正式业务写回动作", "detected": True},
        ],
    }

    for name, doc in (("task_template", task_template), ("map_spec", map_spec),
                      ("route_policy", route_policy), ("activation_plan", activation_plan),
                      ("violations", violations)):
        (OUT / f"{name}.json").write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("L4-1 activation fixtures generated")
    print(f"  violations={len(violations['violations'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
