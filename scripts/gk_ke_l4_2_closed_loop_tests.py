#!/usr/bin/env python3
"""GK-KE L4-2 GITS 闭环测试（C08 L4-2 / wave E）。

依据 C06 运行接口合同与 C03 §8 端到端样例，覆盖 C08 L4-2 退出标准：
「3000 万场景、UNKNOWN、失效版本、超时对账；业务专家验收（OB-C3）」。

检查：
  1. 五步闭环：解读 → 体检 → 推荐 → 确认 → 模拟跟进（每步有产物）
  2. **3000 万场景**：客户声明「可能需 3000 万」→ 必须是 CUSTOMER_STATEMENT 声明，
     且**不得**被当作真实贷款需求、额度或可提款金额
  3. **UNKNOWN**：用途未知 → 输出 UNKNOWN + 补充问题；**不得**因行业图"资金需求"关系而通过准入
  4. **失效版本**：目标版本失效 → 拒绝动作
  5. **超时对账**：超时 → status=RESULT_UNKNOWN，**先查询目标回执**，不直接判失败
  6. **白名单强制**：仅 CREATE_FOLLOWUP_TASK / RECORD_CONTACT_OUTCOME；
     转账/放款/授信审批一律拒绝
  7. 确认绑定：动作必须绑定 confirmationRef + expectedTargetVersion
  8. 不产生授信结论（解读/推荐边界）

退出码：全通过 0，否则 1。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CL = ROOT / "specs" / "knowledge-architecture" / "closed-loop"

ALLOWED_ACTIONS = {"CREATE_FOLLOWUP_TASK", "RECORD_CONTACT_OUTCOME"}
FORBIDDEN_ACTIONS = {
    "TRANSFER_FUNDS", "DISBURSE_LOAN", "APPROVE_CREDIT",
    "EXECUTE_WIRE", "CREATE_LOAN_CONTRACT", "SUBMIT_CREDIT_APPLICATION",
}
LOOP_STEPS = ["interpretation", "healthCheck", "recommendation", "confirmation", "simulatedFollowUp"]


def load(name: str):
    return json.loads((CL / name).read_text(encoding="utf-8"))


def detect_violations(doc: dict) -> set[str]:
    """对给定文档执行全部拒绝判定，返回触发的违规码集合（fail-closed）。

    与 L3-2 同构：违规夹具必须**可执行**并通过同一套真值判定，
    避免"自述 detected"式的空转断言（FAIL-2026-09-12-14）。
    """
    found: set[str] = set()

    # 6. 禁止动作（安全红线）
    follow = doc.get("simulatedFollowUp", {})
    if follow.get("attempted") is True:
        action_type = follow.get("actionType")
        if action_type in FORBIDDEN_ACTIONS:
            found.add("FORBIDDEN_ACTION_REJECTED")
        # 7. 缺确认引用
        if not follow.get("confirmationRef"):
            found.add("MISSING_CONFIRMATION_REJECTED")
        # 4. 失效版本被接受
        for bad in follow.get("invalidVersionAttempts", []):
            if bad.get("attempted") is True and bad.get("accepted") is True:
                found.add("STALE_TARGET_VERSION_REJECTED")

    for bad in doc.get("invalidVersionAttempts", []):
        if bad.get("attempted") is True and bad.get("accepted") is True:
            found.add("STALE_TARGET_VERSION_REJECTED")

    # 5. 超时对账
    timeout = doc.get("timeoutReconciliation", {})
    if timeout.get("timedOut") is True:
        if timeout.get("status") != "RESULT_UNKNOWN" or timeout.get("queriedTargetReceipt") is not True \
                or timeout.get("declaredFailureImmediately") is True:
            found.add("TIMEOUT_RESULT_UNKNOWN")

    # 2. 声明被当作事实
    stmt = doc.get("interpretation", {}).get("statement3000W", {})
    if stmt:
        if stmt.get("modality") != "CUSTOMER_STATEMENT" \
                or stmt.get("treatedAsRealLoanDemand") is True \
                or stmt.get("treatedAsApprovedAmount") is True \
                or stmt.get("treatedAsDrawableAmount") is True:
            found.add("STATEMENT_AS_FACT_REJECTED")

    # 3. 用途未知却通过准入
    hc = doc.get("healthCheck", {})
    if hc.get("purposeKnown") is False:
        if hc.get("result") != "UNKNOWN" or not hc.get("followUpQuestions") \
                or hc.get("passedAdmissionBasedOnGraphRelation") is True:
            found.add("UNKNOWN_PURPOSE_NOT_ADMITTED")

    return found


REQUIRED_VIOLATION_CODES = {
    "FORBIDDEN_ACTION_REJECTED", "STALE_TARGET_VERSION_REJECTED",
    "MISSING_CONFIRMATION_REJECTED", "TIMEOUT_RESULT_UNKNOWN",
    "STATEMENT_AS_FACT_REJECTED", "UNKNOWN_PURPOSE_NOT_ADMITTED",
}


def main() -> int:  # noqa: C901
    failures: list[str] = []

    if not CL.is_dir():
        print(f"FAIL: closed-loop dir missing: {CL}", file=sys.stderr)
        return 2

    run = load("closed_loop_run.json")
    violations = load("violations.json").get("violations", [])

    # 1. 五步闭环
    for step in LOOP_STEPS:
        if step not in run:
            failures.append(f"[1] closed loop missing step: {step}")
    order = run.get("stepOrder", [])
    if order != LOOP_STEPS:
        failures.append(f"[1] step order must be {LOOP_STEPS}, got {order}")

    # 2. 3000 万场景：是声明而非事实
    stmt = run.get("interpretation", {}).get("statement3000W", {})
    if stmt.get("modality") != "CUSTOMER_STATEMENT":
        failures.append(f"[2] 3000W must be CUSTOMER_STATEMENT, got {stmt.get('modality')!r}")
    if stmt.get("treatedAsRealLoanDemand") is True:
        failures.append("[2] 3000W must not be treated as a real loan demand")
    if stmt.get("treatedAsApprovedAmount") is True:
        failures.append("[2] 3000W must not be treated as an approved amount")
    if stmt.get("treatedAsDrawableAmount") is True:
        failures.append("[2] 3000W must not be treated as a drawable amount")
    if not stmt.get("sourceRef"):
        failures.append("[2] 3000W statement must carry a source reference")

    # 3. UNKNOWN
    hc = run.get("healthCheck", {})
    if hc.get("purposeKnown") is False:
        if hc.get("result") != "UNKNOWN":
            failures.append(f"[3] unknown purpose must yield UNKNOWN, got {hc.get('result')!r}")
        if not hc.get("followUpQuestions"):
            failures.append("[3] UNKNOWN must be accompanied by follow-up questions")
    if hc.get("passedAdmissionBasedOnGraphRelation") is True:
        failures.append("[3] admission must not pass merely because a graph relation mentions funding need")

    # 4/5/6/7. 动作
    action = run.get("simulatedFollowUp", {})
    action_type = action.get("actionType")
    if action_type in FORBIDDEN_ACTIONS:
        failures.append(f"[6] forbidden action executed: {action_type}")
    elif action_type not in ALLOWED_ACTIONS:
        failures.append(f"[6] action {action_type!r} not in whitelist")

    if not action.get("confirmationRef"):
        failures.append("[7] action must bind a confirmationRef")
    if action.get("expectedTargetVersion") is None:
        failures.append("[7] action must bind expectedTargetVersion")

    # 4. 失效版本
    for bad in run.get("invalidVersionAttempts", []):
        if bad.get("attempted") is True and bad.get("accepted") is True:
            failures.append(f"[4] stale target version accepted: {bad.get('targetVersion')!r}")

    # 5. 超时对账
    timeout = run.get("timeoutReconciliation", {})
    if timeout.get("timedOut") is True:
        if timeout.get("status") != "RESULT_UNKNOWN":
            failures.append(f"[5] timeout must map to RESULT_UNKNOWN, got {timeout.get('status')!r}")
        if timeout.get("queriedTargetReceipt") is not True:
            failures.append("[5] on timeout, the target receipt must be queried before declaring failure")
        if timeout.get("declaredFailureImmediately") is True:
            failures.append("[5] must not declare failure immediately on timeout")

    # 8. 不产生授信结论
    for step in ("interpretation", "recommendation"):
        if run.get(step, {}).get("producesCreditDecision") is True:
            failures.append(f"[8] {step} must not produce a credit decision")
    rec = run.get("recommendation", {})
    if rec.get("isCandidateProposal") is not True:
        failures.append("[8] recommendation must remain a candidate proposal")

    # 负例：必须**可执行**并通过真值判定（fail-closed，FAIL-2026-09-12-14）
    violation_seen: set[str] = set()
    if not violations:
        failures.append("[neg] no violation fixtures (all rejection assertions would be noop)")
    for v in violations:
        detected = detect_violations(v)
        expected = v.get("expectedError")
        if expected not in detected:
            failures.append(f"[neg] {v.get('case')}: expected {expected} not detected "
                            f"(detected={sorted(detected)})")
        else:
            violation_seen.add(expected)
    uncovered = REQUIRED_VIOLATION_CODES - violation_seen
    if uncovered:
        failures.append(f"[neg] rejection paths never triggered: {sorted(uncovered)}")

    # 正向夹具必须无违规
    positive_violations = detect_violations(run)
    if positive_violations:
        failures.append(f"[pos] compliant run unexpectedly violates: {sorted(positive_violations)}")

    if failures:
        print("gk-ke-l4-2-closed-loop-tests: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    print("gk-ke-l4-2-closed-loop-tests: PASS")
    print(f"  stepOrder={order}")
    print(f"  action={action_type} (whitelist enforced)")
    print(f"  timeout_status={timeout.get('status')} receipt_queried={timeout.get('queriedTargetReceipt')}")
    print(f"  healthCheck={hc.get('result')} purgeKnown={hc.get('purposeKnown')}")
    print("  checks: five-steps, statement-not-fact, unknown-purpose, stale-version, "
          "timeout-reconcile, action-whitelist, confirmation-binding, no-credit-decision")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
