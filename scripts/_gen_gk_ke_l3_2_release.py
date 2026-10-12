#!/usr/bin/env python3
"""生成 GK-KE L3-2 审核发布夹具（C08 L3-2 / wave D1）。

依据 C03 §4 双维审核、§5 状态机 + Publishable 谓词、§6 原子发布与回滚、§9 失败证据。
产出：specs/knowledge-architecture/release/{release_manifest,review_decisions,negatives}.json
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "specs" / "knowledge-architecture" / "release"

H = lambda c: c * 64  # noqa: E731


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    release_manifest = {
        "simulationOnly": True,
        "releaseId": "SIM-REL-001",
        "manifest": "specs/knowledge-architecture/factory/review_package.json",
        "approvalRefs": ["SIM-REVIEW-001", "SIM-REVIEW-002"],
        "qualityRunRef": "SIM-QA-RUN-001",
        "effectiveFrom": "2026-09-01",
        "purposeFlagsRequested": ["INTERPRETATION"],

        # Publishable 八项输入（C03 §5）
        "schemaValid": True,
        "refClosure": True,
        "sourceUsable": True,
        "identityResolved": True,
        "blockingConflict": False,
        "targetHash": H("a"),
        "currentHash": H("a"),
        "requiredCapabilitiesReady": True,
        "qualityGatePassed": True,

        "publishState": "PUBLISHED",
        "published": True,
        "graphRequired": False,
        "expectedCatalogRevision": 1,
        "catalogRevisionAfter": 2,

        # 双维审核（C03 §4）
        "dualReview": [
            {"dimension": "CONTENT_AUTHORITY",
             "responsibleRole": "KNOWLEDGE_OWNER",
             "passed": True},
            {"dimension": "MAP_AND_EXECUTION_AUTHORITY",
             "responsibleRole": "PROCESS_OWNER_AND_CAPABILITY_MAINTAINER",
             "passed": True},
        ],

        # 投影：graphRequired=false 时可选图未就绪不阻断基础检索路径（C03 §6.2）
        "projections": [
            {"name": "retrieval", "ready": True, "published": True, "required": True},
            {"name": "graph", "ready": False, "published": False, "required": False,
             "graphDisabledMarked": True},
        ],

        # 运行有效性独立于发布内容（C03 §5）
        "runtimeStates": [
            {"assetId": "SIM-ASSET-P001", "state": "ACTIVE", "stillSearchable": True},
            {"assetId": "SIM-ASSET-OLD", "state": "SUPERSEDED", "stillSearchable": False},
            {"assetId": "SIM-ASSET-REVOKED", "state": "REVOKED", "stillSearchable": False},
            {"assetId": "SIM-ASSET-STALE", "state": "STALE", "stillSearchable": True},
        ],

        # 回滚只能指向仍有效且兼容的历史 Release（C03 §6.6）
        "rollbacks": [
            {"toReleaseId": "SIM-REL-000", "toReleaseRevoked": False,
             "compatible": True, "performed": True},
        ],

        "purposeFlags": [
            {"subject": "SIM-ASSET-P001", "from": "INTERPRETATION",
             "to": "INTERPRETATION", "silentlyUpgraded": False},
        ],

        "corrections": [
            {"correctionId": "SIM-CORR-001", "decisionId": "SIM-REVIEW-001",
             "decidedAt": "2026-09-10T09:00:00+08:00", "reason": "人工更正：术语统一",
             "targetHash": H("a"), "before": H("b"), "after": H("a")},
        ],
    }

    review_decisions = {
        "simulationOnly": True,
        "decisions": [
            {"decisionId": "SIM-REVIEW-001", "reviewerPrincipal": "SIM-REVIEWER",
             "reviewerRole": "KNOWLEDGE_OWNER", "targetType": "MapVersion",
             "targetId": "SIM-MAP-FINANCE", "targetVersion": "1.0.0", "targetHash": H("a"),
             "authorPrincipal": "SIM-AUTHOR", "decision": "APPROVED",
             "purpose": "INTERPRETATION", "contentState": "APPROVED",
             "decidedAt": "2026-09-10T09:00:00+08:00", "expired": False,
             "countedInRelease": True, "reason": "内容与地图执行双维通过"},
            {"decisionId": "SIM-REVIEW-002", "reviewerPrincipal": "SIM-REVIEWER",
             "reviewerRole": "PROCESS_OWNER", "targetType": "AssetVersion",
             "targetId": "SIM-ASSET-P001", "targetVersion": "1.0.0", "targetHash": H("c"),
             "authorPrincipal": "SIM-AUTHOR", "decision": "APPROVED",
             "purpose": "INTERPRETATION", "contentState": "APPROVED",
             "decidedAt": "2026-09-10T10:00:00+08:00", "expired": False,
             "countedInRelease": True, "reason": "产品卡内容认定通过"},
        ],
        "note": "生产署名必须来自真实认证主体；本包 SIM-REVIEWER 仅为测试夹具（C03 §5）。",
    }

    failure_evidence = [
        ("SOURCE_DELETED", "来源删除"),
        ("AMOUNT_OCR_ERROR", "金额 OCR 错误"),
        ("HOMONYM_ENTITY_MERGED", "同名企业误并"),
        ("TABLE_CONDITION_OMITTED", "表格条件遗漏"),
        ("EXPIRED_DOCUMENT", "过期文档"),
        ("DUAL_VERSION_RULE_CONFLICT", "双版本规则冲突"),
        ("CONTENT_CHANGED_AFTER_APPROVAL", "审批后改字"),
        ("GRAPH_PROJECTION_HALF_DONE", "图投影半完成"),
        ("ACL_REVOKED", "ACL 撤销"),
        ("MAP_DEPENDENCY_CYCLE", "地图依赖环"),
        ("SELF_APPROVAL", "自审自批"),
        ("ROLLBACK_TO_REVOKED", "回滚指向已撤销版本"),
        ("PURPOSE_FLAG_SILENT_UPGRADE", "用途标记静默升级"),
    ]
    negatives = {
        "simulationOnly": True,
        "negatives": [
            {"case": code.lower(), "expectedError": code, "description": desc,
             "candidateRetained": True, "source": "C03 section 9"}
            for code, desc in failure_evidence
        ],
    }

    (OUT / "release_manifest.json").write_text(json.dumps(release_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "review_decisions.json").write_text(json.dumps(review_decisions, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "negatives.json").write_text(json.dumps(negatives, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("L3-2 release fixtures generated")
    print(f"  negatives={len(failure_evidence)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
