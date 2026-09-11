#!/usr/bin/env python3
"""生成 GK-KE L2-2 注册中心数据（C08 L2-2 / wave B3）。

依据 C02 §3 六类注册对象与 §4 边类型。
产出：specs/knowledge-architecture/registry/{AssetVersion,SourceVersion,Capability,
      QueryDefinition,MapVersion,Release}.json + negatives/
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "specs" / "knowledge-architecture" / "registry"
NEG = REG / "negatives"

H = lambda c: c * 64  # noqa: E731  (固定 64 位 hex 占位)


def write(name: str, doc: dict) -> None:
    (REG / f"{name}.json").write_text(
        json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def main() -> int:
    REG.mkdir(parents=True, exist_ok=True)
    NEG.mkdir(parents=True, exist_ok=True)

    # --- AssetVersion（C02 §3）---
    write("AssetVersion", {
        "$comment": "C02 §3 注册对象：AssetVersion。assetId 稳定；version 不可变；审批的是具体版本/哈希。",
        "items": [
            {
                "assetId": "SIM-ASSET-P001", "version": "1.0.0",
                "assetClass": "KNOWLEDGE_RULE", "kind": "PRODUCT_CARD",
                "title": "模拟流动资金贷条款", "description": "SIM-P001 产品卡（集合选取后的单卡）",
                "ownerSystem": "KERT", "ownerRole": "SIM-KNOWLEDGE-OWNER",
                "contentRef": "simulation/documents/SIM-DOC-P001_1.0.0.md",
                "contentHash": "47b41179c648d29a943f9d8d896b58eae170ea5b191fdde69d7228ecc3ff62c8",
                "coreVersion": "1.0.0",
                "scope": {"tenantId": "SIM-BANK", "orgIds": ["SIM-O01"], "customerIds": ["SIM-C001"], "purpose": "INTERPRETATION", "authorized": True},
                "purposeFlags": ["INTERPRETATION"], "lifecycle": "CANDIDATE",
                "dependencyRefs": ["SIM-SRC-DOC-001"],
                "discoverable": True,
                "currentVersion": "1.0.0", "casExpectedVersion": "1.0.0", "casAccepted": True,
            },
            {
                "assetId": "SIM-ASSET-METRIC", "version": "1.0.0",
                "assetClass": "KNOWLEDGE_RULE", "kind": "METRIC_ASSET",
                "title": "日均存款指标资产", "description": "引用既定 SIM 口径，不在地图内改指标定义",
                "ownerSystem": "KERT", "ownerRole": "SIM-METRIC-KNOWLEDGE-OWNER",
                "contentRef": "specs/knowledge-architecture/registry/METRIC_ASSET.md",
                "contentHash": H("b"), "coreVersion": "1.0.0",
                "scope": {"tenantId": "SIM-BANK", "orgIds": ["SIM-O01"], "customerIds": ["SIM-C001"], "purpose": "INTERPRETATION", "authorized": True},
                "purposeFlags": ["INTERPRETATION"], "lifecycle": "CANDIDATE",
                "dependencyRefs": ["SIM.METRIC.CUSTOMER_AVG_DEPOSIT"],
                "discoverable": True,
                "currentVersion": "1.0.0", "casExpectedVersion": "1.0.0", "casAccepted": True,
            },
            {
                "assetId": "SIM-ASSET-RESTRICTED", "version": "1.0.0",
                "assetClass": "KNOWLEDGE_RULE", "kind": "RESTRICTED_NOTE",
                "title": "受限内部注释", "description": "未授权目录资产，用于非授权泄漏负例",
                "ownerSystem": "KERT", "ownerRole": "SIM-KNOWLEDGE-OWNER",
                "contentRef": "simulation/documents/RESTRICTED.md", "contentHash": H("c"),
                "coreVersion": "1.0.0",
                "scope": {"tenantId": "SIM-BANK", "orgIds": ["SIM-O99"], "customerIds": [], "purpose": "INTERPRETATION", "authorized": False},
                "purposeFlags": ["INTERPRETATION"], "lifecycle": "CANDIDATE",
                "dependencyRefs": [], "discoverable": False,
                "currentVersion": "1.0.0", "casExpectedVersion": "1.0.0", "casAccepted": True,
            },
        ],
    })

    # --- SourceVersion ---
    write("SourceVersion", {
        "$comment": "C02 §3 注册对象：SourceVersion。文档替代产生新版本；检索块不能是唯一原文。",
        "items": [
            {
                "sourceId": "SIM-SRC-DOC-001", "version": "1.0.0",
                "originalRef": "simulation/documents/SIM-DOC-P001_1.0.0.md",
                "hash": "47b41179c648d29a943f9d8d896b58eae170ea5b191fdde69d7228ecc3ff62c8",
                "issuedAt": "2026-09-01T00:00:00Z",
                "validFrom": "2026-09-01", "validTo": "2026-12-31",
                "sourceClass": "PRODUCT_DESCRIPTION", "allowedUses": ["INTERPRETATION"],
                "permissionRef": "SIM-PERM-SRC-001", "simulationOnly": True,
            },
        ],
    })

    # --- Capability（C02 §3：必须有探针）---
    write("Capability", {
        "$comment": "C02 §3 注册对象：Capability。文档建议某工具不等于存在可调用工具；需要运行探针。",
        "items": [
            {
                "capabilityId": "SIM-CAP-INTERPRET", "version": "1.0.0",
                "inputSchemaRef": "gk-ke/v1:KnowledgeExecuteRequest",
                "outputSchemaRef": "gk-ke/v1:EvidenceBundle",
                "executorRef": "SIM-EXEC-INTERPRET", "sideEffect": "NONE",
                "preconditions": ["SIM-ASSET-P001@1.0.0 已发布", "scope 授权通过"],
                "permissionRef": "SIM-PERM-CAP-001",
                "budget": {"maxRows": 500, "timeoutMs": 60000},
                "timeoutMs": 60000,
                "idempotencyPolicy": "IDEMPOTENT_BY_PLAN_HASH",
                "probeStatus": "PASSED", "callable": True,
            },
        ],
    })

    # --- QueryDefinition ---
    write("QueryDefinition", {
        "$comment": "C02 §3 注册对象：QueryDefinition。LLM 只选择 queryId 与参数；模板由平台签署。",
        "items": [
            {
                "queryId": "SIM-QRY-AVG-DEPOSIT", "version": "1.0.0",
                "parameterSchemaRef": "gk-ke/v1:SemanticRequest",
                "templateRef": "specs/gk-ke/v1/definitions/query-templates/SIM-QRY-AVG-DEPOSIT.sql",
                "resultSchemaRef": "gk-ke/v1:SemanticResult",
                "sourceProductRef": "SIM-SRC-DOC-001",
                "maxRows": 1000, "timeoutMs": 30000,
                "metricRef": "SIM.METRIC.CUSTOMER_AVG_DEPOSIT",
            },
        ],
    })

    # --- MapVersion（C02 §4 边类型约束）---
    write("MapVersion", {
        "$comment": "C02 §3 注册对象：MapVersion。每个资产/能力引用可解析；没有入口和用途说明不能激活。",
        "items": [
            {
                "mapId": "SIM-MAP-FINANCE", "version": "1.0.0",
                "taskTypes": ["FINANCE_VISIT_PREP"],
                "entryNodes": ["N-TASK"],
                "nodes": [
                    {"nodeId": "N-TASK", "nodeType": "Task", "ref": "SIM-TASK-TEMPLATE"},
                    {"nodeId": "N-PRODUCT", "nodeType": "Asset", "ref": "SIM-ASSET-P001"},
                    {"nodeId": "N-METRIC", "nodeType": "Asset", "ref": "SIM-ASSET-METRIC"},
                    {"nodeId": "N-SKILL", "nodeType": "Capability", "ref": "SIM-CAP-INTERPRET"},
                ],
                "edges": [
                    {"edgeId": "SIM-ME-1", "from": "N-TASK", "to": "N-PRODUCT", "fromType": "Task", "toType": "Asset", "relation": "requires"},
                    {"edgeId": "SIM-ME-2", "from": "N-TASK", "to": "N-METRIC", "fromType": "Task", "toType": "Asset", "relation": "requires"},
                    {"edgeId": "SIM-ME-3", "from": "N-TASK", "to": "N-SKILL", "fromType": "Task", "toType": "Capability", "relation": "requires"},
                    {"edgeId": "SIM-ME-4", "from": "N-SKILL", "to": "N-PRODUCT", "fromType": "Capability", "toType": "Asset", "relation": "uses"},
                ],
                "routePolicyRef": "SIM-ROUTE-001",
                "releaseRef": "SIM-REL-001",
                "coverage": {"assetRefsResolvable": True, "capabilityRefsResolvable": True},
                "dependencyRefs": ["SIM-ASSET-P001", "SIM-ASSET-METRIC", "SIM-CAP-INTERPRET", "SIM-ROUTE-001"],
            },
        ],
    })

    # --- Release ---
    write("Release", {
        "$comment": "C02 §3 注册对象：Release。发布内容不可变；当前指针单独维护，更新使用版本条件。",
        "items": [
            {
                "releaseId": "SIM-REL-001",
                "manifest": "specs/gk-ke/v1/definitions/SIM-MAP-FINANCE.json",
                "hash": H("d"),
                "approvalRefs": ["SIM-REVIEW-001"],
                "qualityRunRef": "SIM-QA-RUN-001",
                "effectiveFrom": "2026-09-01",
                "purposeFlags": ["INTERPRETATION"],
            },
        ],
    })

    # --- 负例（C08 L2-2 三条退出标准的拒绝路径）---
    negatives = [
        ("dangling_dependency_ref", "DANGLING_DEPENDENCY_REF", "断链：dependencyRefs 引用不存在资产"),
        ("unauthorized_discoverable", "UNAUTHORIZED_DISCOVERY_LEAK", "非授权目录资产出现在发现结果（泄漏）"),
        ("stale_cas_accept", "CAS_STALE_VERSION_ACCEPTED", "expectedVersion 过期仍被接受（并发冲突未被拒）"),
        ("version_mutated_in_place", "VERSION_MUTATED_IN_PLACE", "同 id+version 内容 hash 被原地改写（version 不可变被违反）"),
        ("invalid_edge_endpoint", "EDGE_ENDPOINT_NOT_ALLOWED", "边类型与端点类型不匹配（如 uses 从 Task 出发）"),
        ("capability_callable_without_probe", "CAPABILITY_CALLABLE_WITHOUT_PROBE", "能力探针未通过却标记可调用"),
        ("missing_required_field", "REGISTRY_REQUIRED_FIELD_MISSING", "注册对象缺 C02 §3 必填字段"),
    ]
    for name, error, desc in negatives:
        (NEG / f"{name}.json").write_text(
            json.dumps({"expectedError": error, "case": name, "description": desc,
                        "simulationOnly": True, "source": "C02 section 3/4 + C08 L2-2"},
                       ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("L2-2 registry generated")
    print(f"  negatives={len(negatives)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
