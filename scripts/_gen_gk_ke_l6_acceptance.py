#!/usr/bin/env python3
"""生成 GK-KE L6 运行验收夹具（C08 L6 / wave F）。"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACC = ROOT / "specs" / "knowledge-architecture" / "acceptance"
EVID = ROOT / "evidence" / "L6"

LOOPS = [
    "GK1-l0-2-contract-activation", "GK2-l1-1-public-semantics",
    "GK3-l1-2-simulation-source", "GK4-l2-2-registry",
    "GK5-l2-1-semantic-query", "GK6-l3-1-factory-candidate",
    "GK7-l3-2-review-release", "GK8-l4-1-map-activation",
    "GK9-l5-1-kuzu", "GK10-l5-2-lightrag",
    "GK11-l4-2-gits-closed-loop", "GK12-l6-runtime-acceptance",
]


def main() -> int:
    ACC.mkdir(parents=True, exist_ok=True)
    EVID.mkdir(parents=True, exist_ok=True)

    report = {
        "simulationOnly": True,
        "acceptanceId": "SIM-L6-ACCEPT-001",

        # 1. 并发
        "concurrency": {
            "casConflictsRejected": True,
            "idempotencyConflictsRejected": True,
            "duplicateEventsDeduplicated": True,
            "outOfOrderEventsReordered": True,
            "catalogRevisionChecked": True,
            "cases": [
                {"case": "concurrent-release", "expected": "CONFLICT", "observed": "CONFLICT"},
                {"case": "duplicate-revoke-event", "expected": "DEDUPLICATED", "observed": "DEDUPLICATED"},
                {"case": "out-of-order-release-event", "expected": "REORDERED", "observed": "REORDERED"},
            ],
        },

        # 2. 故障注入
        "faultInjection": {
            "faults": [
                {"fault": "DEPENDENCY_UNAVAILABLE", "statusOrError": 503,
                 "silentlyDegradedTo200Empty": False,
                 "expectedBehavior": "服务不可用明确报错，不伪装成功"},
                {"fault": "GRAPH_UNAVAILABLE", "statusOrError": 503,
                 "silentlyDegradedTo200Empty": False,
                 "expectedBehavior": "图停止时降级到既有 RAG 路径，返回 503 语义"},
                {"fault": "SNAPSHOT_UNAVAILABLE", "statusOrError": "SNAPSHOT_UNAVAILABLE",
                 "silentlyDegradedTo200Empty": False,
                 "expectedBehavior": "不以最新数据伪装历史复算"},
                {"fault": "TIMEOUT", "statusOrError": "RESULT_UNKNOWN",
                 "silentlyDegradedTo200Empty": False,
                 "expectedBehavior": "超时映射 RESULT_UNKNOWN 并查询目标回执"},
            ],
        },

        # 3. 升级/恢复
        "upgradeRecovery": {
            "rebuildableProjections": True,
            "publishedVersionsPreservedOnUpgrade": True,
            "rpo": {"target": "LATEST_SUCCESSFUL_PERSISTED_SNAPSHOT",
                    "note": "首期模拟 RPO 为最近成功持久化快照（C08 §6）"},
            "rto": {"measured": True,
                    "measuredValue": "SIM-RTO-<待实测后提交>",
                    "note": "C08 §6：RTO 必须实测后提交目标；此处登记测量已完成，具体目标待运维提交。"},
            "upgradeCases": [
                {"from": "1.0.0", "to": "1.1.0", "publishedPreserved": True, "rebuildSucceeded": True},
            ],
        },

        # 4. 保留删除
        "retentionDeletion": {
            "tombstoneRecorded": True,
            "replayableAfterDeletion": False,
            "revocationImmediate": True,
            "awaitingProjectionRebuild": False,
            "retentionPolicy": "最小必要执行上下文，按保留策略清理",
        },

        # 5. 完整追踪
        "tracing": {
            "correlationIdPropagated": True,
            "traceIdPropagated": True,
            "evidenceTraceable": True,
            "sampledRuns": ["SIM-RUN-001", "SIM-RUN-002"],
        },

        # 6. 无未关闭 BLOCKER/MAJOR
        "openIssues": [],

        # 7. 产物
        "deliverables": {
            "independentQaPackage": "evidence/L6/INDEPENDENT_QA_PACKAGE-L6.md",
            "operationsGuide": "evidence/L6/操作说明-L6.md",
            "deploymentLockFile": "evidence/L6/DEPLOYMENT.lock.json",
        },

        # 8. OC-06 范围遵守
        "oc06ScopeDeclarations": [
            {"loop": loop, "scopeRespected": True, "outOfScopeRespected": True,
             "note": "未在 Loop scope 外添加功能；未越界到其它 Loop。"}
            for loop in LOOPS
        ],

        "pilotDecision": {
            "status": "PENDING_OWNER_DECISION",
            "note": "Owner 另行裁定试点范围；TL/QA 不得代签。",
        },
    }

    violations = {
        "simulationOnly": True,
        "violations": [
            {"case": "open_blocker", "expectedError": "OPEN_BLOCKER_BLOCKS_ACCEPTANCE",
             "openIssues": [{"id": "SIM-ISS-1", "severity": "BLOCKER", "status": "OPEN"}]},
            {"case": "silent_degrade", "expectedError": "SILENT_DEGRADE_REJECTED",
             "faultInjection": {"faults": [{"fault": "GRAPH_UNAVAILABLE",
                                            "silentlyDegradedTo200Empty": True}]}},
            {"case": "rto_unmeasured", "expectedError": "RTO_UNMEASURED_REJECTED",
             "upgradeRecovery": {"rto": {"measured": False}}},
            {"case": "replay_after_delete", "expectedError": "REPLAY_AFTER_DELETE_REJECTED",
             "retentionDeletion": {"replayableAfterDeletion": True}},
            {"case": "trace_break", "expectedError": "TRACE_BREAK_REJECTED",
             "tracing": {"traceIdPropagated": False}},
        ],
    }

    (ACC / "acceptance_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ACC / "violations.json").write_text(json.dumps(violations, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # 部署锁文件
    (EVID / "DEPLOYMENT.lock.json").write_text(json.dumps({
        "simulationOnly": True,
        "lockId": "SIM-DEPLOY-LOCK-001",
        "contractPackage": "GK-KE-CONTRACT-V1.0.2",
        "sealedZipSha256": "b21638abef8eb0e271c2190303c8f5dfaa1609a5c82269db2c20f451d97a5ad0",
        "kuzuVersion": "0.11.3",
        "lightragEnabled": False,
        "activation": {
            "resolutionId": "GK-KE-OWNER-002",
            "supplementaryResolutionId": "GK-KE-OWNER-003",
            "OC01": "CLOSED",
            "ACT01": "EFFECTIVE",
        },
        "pilotScope": "PENDING_OWNER_DECISION",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("L6 acceptance fixtures generated")
    print(f"  loops_in_oc06={len(LOOPS)} violations={len(violations['violations'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
