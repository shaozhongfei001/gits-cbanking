#!/usr/bin/env python3
"""生成 GK-KE L4-2 GITS 闭环夹具（C08 L4-2 / wave E）。

依据 C03 §8 端到端样例 + C06 运行接口 + OWNER-003 §6.1 白名单。
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "specs" / "knowledge-architecture" / "closed-loop"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    run = {
        "simulationOnly": True,
        "runId": "SIM-RUN-002",
        "taskId": "SIM-TASK-001",
        "customerId": "SIM-C001",
        "planId": "SIM-PLAN-001",
        "releaseId": "SIM-REL-001",
        "stepOrder": ["interpretation", "healthCheck", "recommendation", "confirmation", "simulatedFollowUp"],

        # 1. 解读
        "interpretation": {
            "basedOn": "EvidenceBundle",
            "producesCreditDecision": False,
            "statement3000W": {
                "text": "客户表示下季度可能需 3000 万",
                "modality": "CUSTOMER_STATEMENT",
                "sourceRef": "SIM-VISIT-003#L14",
                "treatedAsRealLoanDemand": False,
                "treatedAsApprovedAmount": False,
                "treatedAsDrawableAmount": False,
                "note": "名义未用额度 800 万不等于可提款金额；3000 万是需求声明不是额度。",
            },
            "productInterpretation": {
                "assetRef": "SIM-ASSET-P001@1.0.0",
                "hasEvidence": True,
                "unknowns": ["期限是否可放宽"],
            },
        },

        # 2. 体检
        "healthCheck": {
            "purposeKnown": False,
            "result": "UNKNOWN",
            "followUpQuestions": ["本次融资的具体用途是什么？", "是否有担保安排？"],
            "passedAdmissionBasedOnGraphRelation": False,
            "rules": [
                {"ruleRef": "SIM-RULE-TERM-12M", "result": "TRUE",
                 "premiseRefs": ["SIM-AS-P001-1"]},
                {"ruleRef": "SIM-RULE-PURPOSE-VERIFY", "result": "UNKNOWN",
                 "premiseRefs": ["SIM-AS-P001-1"]},
            ],
            "note": "不得因行业图存在「资金需求」关系而通过准入（C03 §8）。",
        },

        # 3. 推荐（候选）
        "recommendation": {
            "recommendationId": "SIM-REC-001",
            "isCandidateProposal": True,
            "producesCreditDecision": False,
            "subjectRef": "SIM-ASSET-P001@1.0.0",
            "evidenceRefs": ["SIM-EVR-001"],
            "value": "建议在访前核实融资用途与担保安排",
        },

        # 4. 人工确认
        "confirmation": {
            "confirmationRef": "SIM-CONFIRM-001",
            "confirmedBy": "SIM-RM-001",
            "confirmedAt": "2026-09-12T11:00:00+08:00",
            "targetVersion": "1",
            "note": "人工确认后才可提交动作意图。",
        },

        # 5. 模拟跟进动作
        "simulatedFollowUp": {
            "actionType": "CREATE_FOLLOWUP_TASK",
            "confirmationRef": "SIM-CONFIRM-001",
            "expectedTargetVersion": "1",
            "idempotencyKey": "SIM-ACTION-001-ATTEMPT",
            "mode": "SIMULATION",
            "parametersHash": "431fa58621ef66a373621c0b7f764bcfdff20e8ee63e409ca0dc8b15481a7413",
            "receiptRef": "SIM-RECEIPT-001",
            "status": "EXECUTED",
        },

        # 4. 失效版本尝试
        "invalidVersionAttempts": [
            {"targetVersion": "0", "attempted": True, "accepted": False,
             "reason": "STALE_TARGET_VERSION"},
        ],

        # 5. 超时对账
        "timeoutReconciliation": {
            "timedOut": True,
            "status": "RESULT_UNKNOWN",
            "queriedTargetReceipt": True,
            "declaredFailureImmediately": False,
            "reconciledStatus": "EXECUTED",
            "note": "超时不代表失败；先查询目标回执再判定（C06 §3）。",
        },

        "businessAcceptance": {
            "gate": "OB-C3",
            "status": "PENDING_HUMAN_EXPERT",
            "note": "业务专家验收由 Owner 侧执行，TL/QA 不得代签。",
        },
    }

    violations = {
        "simulationOnly": True,
        "violations": [
            {"case": "forbidden_action", "expectedError": "FORBIDDEN_ACTION_REJECTED",
             "description": "转账/放款/授信审批一律拒绝", "detected": True},
            {"case": "stale_target_version", "expectedError": "STALE_TARGET_VERSION_REJECTED",
             "description": "目标版本失效拒绝", "detected": True},
            {"case": "missing_confirmation", "expectedError": "MISSING_CONFIRMATION_REJECTED",
             "description": "缺确认引用拒绝", "detected": True},
            {"case": "timeout_result_unknown", "expectedError": "TIMEOUT_RESULT_UNKNOWN",
             "description": "超时映射为 RESULT_UNKNOWN 并查询回执", "detected": True},
            {"case": "statement_as_fact", "expectedError": "STATEMENT_AS_FACT_REJECTED",
             "description": "客户声明不得当作事实", "detected": True},
            {"case": "unknown_purpose_admitted", "expectedError": "UNKNOWN_PURPOSE_NOT_ADMITTED",
             "description": "用途未知不得通过准入", "detected": True},
        ],
    }

    (OUT / "closed_loop_run.json").write_text(json.dumps(run, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "violations.json").write_text(json.dumps(violations, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("L4-2 closed-loop fixtures generated")
    print(f"  steps={len(run['stepOrder'])} violations={len(violations['violations'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
