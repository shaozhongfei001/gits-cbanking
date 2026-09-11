#!/usr/bin/env python3
"""生成 GK-KE L5-1 Kuzu 图适配夹具（C08 L5-1 / wave C3）。

依据 C05「图服务」路径与 C08 L5-1 退出标准。
Kuzu 版本依据 CR-06「用户指定 KERT 内 Kuzu 模拟」—— 锁定 0.11.3。
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "specs" / "knowledge-architecture" / "graph"

KUZU_VERSION = "0.11.3"  # 锁版


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    manifest = {
        "simulationOnly": True,
        "graphAdapter": "KuzuGraphAdapter",
        "kuzuVersion": KUZU_VERSION,
        "versionLocked": True,
        "versionLockPolicy": "精确版本，不使用 latest 或范围约束",
        "isRebuildableProjection": True,
        "carriesAuthoritativeTransactions": False,
        "sourceOfTruth": "registry",
        "projectionRule": "由已发布清单投影；可重建；不覆盖源",
        "acceptsArbitraryCypher": False,
        "candidateProjectionSeparate": True,

        "nodes": [
            {"nodeId": "SIM-N-C001", "type": "Customer", "releaseState": "PUBLISHED",
             "searchableInPublished": True, "scope": "SIM-O01"},
            {"nodeId": "SIM-N-ASSET-P001", "type": "Asset", "releaseState": "PUBLISHED",
             "searchableInPublished": True, "scope": "SIM-O01"},
            {"nodeId": "SIM-N-CAND-1", "type": "Asset", "releaseState": "CANDIDATE",
             "searchableInPublished": False, "scope": "SIM-O01"},
        ],
        "edges": [
            {"edgeId": "SIM-E-1", "from": "SIM-N-C001", "to": "SIM-N-ASSET-P001",
             "relation": "uses", "authorized": True, "visible": True,
             "revoked": False, "awaitingRebuild": False, "releaseState": "PUBLISHED"},
            {"edgeId": "SIM-E-2", "from": "SIM-N-C001", "to": "SIM-N-ACL-DENIED",
             "relation": "relatedTo", "authorized": False, "visible": False,
             "revoked": False, "awaitingRebuild": False, "releaseState": "PUBLISHED"},
            {"edgeId": "SIM-E-3", "from": "SIM-N-C001", "to": "SIM-N-ASSET-REVOKED",
             "relation": "uses", "authorized": True, "visible": False,
             "revoked": True, "awaitingRebuild": False, "releaseState": "PUBLISHED"},
        ],

        "degradedBehavior": {
            "graphUnavailableStatus": 503,
            "returnsEmptyResultWhenUnavailable": False,
            "fallbackPath": "existing_rag_adapter",
            "note": "停止图服务时返回 503 语义明确；不得返回 200 空结果冒充成功（C08 L5-1）。",
        },

        "rebuildReportRef": "reports/SIM-GRAPH-REBUILD-001.json",
        "exportReportRef": "reports/SIM-GRAPH-EXPORT-001.json",
        "restoreReportRef": "reports/SIM-GRAPH-RESTORE-001.json",
    }

    bounded_queries = {
        "simulationOnly": True,
        "queries": [
            {"queryId": "SIM-GQRY-001", "version": "1.0.0", "bounded": True,
             "maxHops": 2, "maxNodes": 50,
             "description": "从客户出发的有界关系查询", "registered": True},
            {"queryId": "SIM-GQRY-002", "version": "1.0.0", "bounded": True,
             "maxHops": 1, "maxNodes": 20,
             "description": "从资产出发的有界反查", "registered": True},
        ],
        "rejected": [
            {"pattern": "MATCH (n) RETURN n", "reason": "UNBOUNDED"},
            {"pattern": "MATCH p=(a)-[*]-(b) RETURN p", "reason": "VARIABLE_LENGTH_UNBOUNDED"},
        ],
    }

    violations = {
        "simulationOnly": True,
        "violations": [
            {"case": "arbitrary_cypher", "expectedError": "ARBITRARY_CYPHER_REJECTED",
             "description": "任意 Cypher 被拒绝", "detected": True},
            {"case": "unauthorized_edge", "expectedError": "UNAUTHORIZED_EDGE_HIDDEN",
             "description": "无权边不可见", "detected": True},
            {"case": "revoked_edge_immediate", "expectedError": "REVOKED_EDGE_IMMEDIATE",
             "description": "撤销边立即不可见，不等投影重建", "detected": True},
            {"case": "graph_down", "expectedError": "GRAPH_DOWN_503",
             "description": "图服务停止返回 503，不返回 200 空结果", "detected": True},
            {"case": "candidate_in_published", "expectedError": "CANDIDATE_NOT_IN_PUBLISHED",
             "description": "候选投影不出现在已发布检索", "detected": True},
        ],
    }

    for name, doc in (("graph_manifest", manifest), ("bounded_queries", bounded_queries),
                      ("violations", violations)):
        (OUT / f"{name}.json").write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("L5-1 kuzu fixtures generated")
    print(f"  kuzuVersion={KUZU_VERSION} queries={len(bounded_queries['queries'])} "
          f"violations={len(violations['violations'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
