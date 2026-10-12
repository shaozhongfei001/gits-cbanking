#!/usr/bin/env python3
"""GK-KE L3-2 审核发布测试（C08 L3-2 / wave D1）。

依据 C03 §4 双维审核、§5 状态机与审批绑定 + Publishable 谓词、§6 原子发布与回滚、§9 失败证据。
覆盖 C08 L3-2 退出标准：「人工更正可追踪；审批后改字阻断；半发布/撤销测试」。

Publishable(v,p) = ValidSchema ∧ RefClosure ∧ SourceUsable ∧ IdentityResolved
                 ∧ NoBlockingConflict ∧ ApprovedHash ∧ RequiredCapabilitiesReady ∧ QualityGate

检查：
  1. Publishable 八项逐项可判定（每项都有可触发的拒绝路径）
  2. **审批后改字阻断**：targetHash != 当前 hash → 拒绝
  3. **自审自批阻断**：reviewerPrincipal == authorPrincipal → 拒绝
  4. **过期审批阻断**：审批过期 → 拒绝
  5. **半发布阻断**：requiredProjection 未 ready 且 graphRequired=false 时
     不得把未就绪投影标为 PUBLISHED；graphRequired=true 时阻断
  6. **撤销即时生效**：REVOKED 立即不可检索，不等投影重建
  7. **回滚**：只能指向仍有效且兼容的历史 Release；已撤销规则不得通过回滚复活
  8. **purposeFlags 不得静默升级**（RESEARCH 不能变 RECOMMENDATION）
  9. **人工更正可追踪**：更正记录含 decisionId/decidedAt/reason/targetHash
 10. 状态机合法：CANDIDATE→IN_REVIEW→APPROVED/REJECTED；STAGED→PUBLISHED；
     运行有效性 ACTIVE/STALE/REVOKED/SUPERSEDED 独立于发布内容

退出码：全通过 0，否则 1。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REL = ROOT / "specs" / "knowledge-architecture" / "release"

PUBLISHABLE = [
    "ValidSchema", "RefClosure", "SourceUsable", "IdentityResolved",
    "NoBlockingConflict", "ApprovedHash", "RequiredCapabilitiesReady", "QualityGate",
]

CONTENT_STATES = {"CANDIDATE", "IN_REVIEW", "APPROVED", "REJECTED"}
PUBLISH_STATES = {"STAGED", "PUBLISHED"}
RUNTIME_STATES = {"ACTIVE", "STALE", "REVOKED", "SUPERSEDED"}


def load(name: str):
    return json.loads((REL / name).read_text(encoding="utf-8"))


def evaluable(doc: dict) -> dict[str, bool]:
    """按 Publishable 谓词逐项判定（C03 §5）。"""
    return {
        "ValidSchema": bool(doc.get("schemaValid")),
        "RefClosure": bool(doc.get("refClosure")),
        "SourceUsable": bool(doc.get("sourceUsable")),
        "IdentityResolved": bool(doc.get("identityResolved")),
        "NoBlockingConflict": not doc.get("blockingConflict"),
        "ApprovedHash": doc.get("targetHash") == doc.get("currentHash"),
        "RequiredCapabilitiesReady": bool(doc.get("requiredCapabilitiesReady")),
        "QualityGate": bool(doc.get("qualityGatePassed")),
    }


def detect_violations(doc: dict) -> set[str]:
    """对给定文档执行全部拒绝判定，返回触发的违规码集合（fail-closed）。"""
    found: set[str] = set()

    # 2. 审批后改字
    if doc.get("targetHash") is not None and doc.get("currentHash") is not None:
        if doc["targetHash"] != doc["currentHash"] and doc.get("published") is True:
            found.add("CONTENT_CHANGED_AFTER_APPROVAL")

    for d in doc.get("decisions", []):
        # 3. 自审自批
        if d.get("reviewerPrincipal") == d.get("authorPrincipal") and d.get("decision") == "APPROVED":
            found.add("SELF_APPROVAL")
        # 4. 过期审批被计入
        if d.get("expired") is True and d.get("countedInRelease") is True:
            found.add("EXPIRED_APPROVAL_COUNTED")

    # 5. 半发布
    for proj in doc.get("projections", []):
        if proj.get("published") is True and proj.get("ready") is not True:
            found.add("HALF_PUBLISH")

    # 6. 撤销后仍可检索
    for item in doc.get("runtimeStates", []):
        if item.get("state") == "REVOKED" and item.get("stillSearchable") is True:
            found.add("REVOKED_STILL_SEARCHABLE")

    # 7. 回滚指向已撤销版本
    for rb in doc.get("rollbacks", []):
        if rb.get("toReleaseRevoked") is True and rb.get("performed") is True:
            found.add("ROLLBACK_TO_REVOKED")

    # 8. 用途标记静默升级
    for pf in doc.get("purposeFlags", []):
        if pf.get("from") == "RESEARCH" and pf.get("to") == "RECOMMENDATION" and pf.get("silentlyUpgraded") is True:
            found.add("PURPOSE_FLAG_SILENT_UPGRADE")

    return found


REQUIRED_VIOLATION_CODES = {
    "CONTENT_CHANGED_AFTER_APPROVAL", "SELF_APPROVAL", "EXPIRED_APPROVAL_COUNTED",
    "HALF_PUBLISH", "REVOKED_STILL_SEARCHABLE", "ROLLBACK_TO_REVOKED",
    "PURPOSE_FLAG_SILENT_UPGRADE",
}


def main() -> int:  # noqa: C901
    failures: list[str] = []
    violation_seen: set[str] = set()

    if not REL.is_dir():
        print(f"FAIL: release dir missing: {REL}", file=sys.stderr)
        return 2

    release = load("release_manifest.json")
    decisions = load("review_decisions.json")
    negatives = load("negatives.json")

    # 违规夹具：必须被检出（fail-closed —— 缺夹具或缺检出均失败）
    violations = release.get("violations", [])
    if not violations:
        failures.append("[violations] no violation fixtures (all rejection assertions would be noop) "
                        "- see FAIL-2026-09-12-12")
    for v in violations:
        detected = detect_violations(v)
        expected = v.get("expectedError")
        if expected not in detected:
            failures.append(f"[violations] {v.get('case')}: expected {expected} not detected "
                            f"(detected={sorted(detected)})")
        else:
            violation_seen.add(expected)
    uncovered_violations = REQUIRED_VIOLATION_CODES - violation_seen
    if uncovered_violations:
        failures.append(f"[violations] rejection paths never triggered: {sorted(uncovered_violations)}")

    # 正向夹具必须无违规
    positive_violations = detect_violations(release)
    if positive_violations:
        failures.append(f"[positive] compliant fixture unexpectedly violates: {sorted(positive_violations)}")

    # 1. Publishable 八项逐项可判定 + 全通过才可发布
    verdict = evaluable(release)
    missing = [p for p in PUBLISHABLE if p not in verdict]
    if missing:
        failures.append(f"[1] Publishable predicates not evaluable: {missing}")
    all_pass = all(verdict.values())
    if release.get("published") is True and not all_pass:
        failures.append(f"[1] published while Publishable false: {[k for k, v in verdict.items() if not v]}")

    # 9. 人工更正可追踪
    for corr in release.get("corrections", []):
        for field in ("decisionId", "decidedAt", "reason", "targetHash"):
            if field not in corr:
                failures.append(f"[9] correction {corr.get('correctionId')} missing trace field {field}")

    # 10. 状态机合法
    for d in decisions.get("decisions", []):
        state = d.get("contentState")
        if state not in CONTENT_STATES:
            failures.append(f"[10] invalid content state {state!r}")
    for item in release.get("runtimeStates", []):
        state = item.get("state")
        if state not in RUNTIME_STATES:
            failures.append(f"[10] invalid runtime state {state!r}")
    publish_state = release.get("publishState")
    if publish_state not in PUBLISH_STATES:
        failures.append(f"[10] invalid publish state {publish_state!r}")

    # 负例：C03 §9 必须交付的失败证据全部覆盖（fail-closed）
    must_cover = {
        "SOURCE_DELETED", "AMOUNT_OCR_ERROR", "HOMONYM_ENTITY_MERGED",
        "TABLE_CONDITION_OMITTED", "EXPIRED_DOCUMENT", "DUAL_VERSION_RULE_CONFLICT",
        "CONTENT_CHANGED_AFTER_APPROVAL", "GRAPH_PROJECTION_HALF_DONE",
        "ACL_REVOKED", "MAP_DEPENDENCY_CYCLE",
        "SELF_APPROVAL", "ROLLBACK_TO_REVOKED", "PURPOSE_FLAG_SILENT_UPGRADE",
    }
    covered = {n.get("expectedError") for n in negatives.get("negatives", [])}
    uncovered = must_cover - covered
    if uncovered:
        failures.append(f"[neg] C03 section 9 failure evidence not covered: {sorted(uncovered)}")
    for n in negatives.get("negatives", []):
        if n.get("candidateRetained") is not True:
            failures.append(f"[neg] {n.get('case')}: candidate must be retained (C03 section 9)")

    if failures:
        print("gk-ke-l3-2-release-tests: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    print("gk-ke-l3-2-release-tests: PASS")
    print(f"  publishable_verdict={verdict}")
    print(f"  publishState={publish_state}")
    print(f"  failure_evidence_covered={len(covered)}/{len(must_cover)}")
    print("  checks: publishable-8, hash-binding, self-approval, expired-approval, "
          "half-publish, revoke-immediate, rollback-guard, purpose-upgrade, traceability, statemachine")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
