#!/usr/bin/env python3
"""GK-KE L6 运行验收测试（C08 L6 / wave F）。

依据 C08 L6「并发、故障注入、升级/恢复、保留删除、完整追踪」与 §6 保留/恢复目标。
退出标准：「无未关闭 BLOCKER/MAJOR；Owner 另行裁定试点范围」。

检查（五类验收）：
  1. **并发**：CAS 冲突被拒、幂等键冲突被拒、乱序事件按 eventId 去重且核对 catalogRevision
  2. **故障注入**：依赖失效 / 图不可用 / 快照不可用 / 超时 —— 每类语义正确
     （503 或明确错误码，**不得**静默降级为 200 空结果）
  3. **升级/恢复**：可重建投影、升级不丢已发布版本、RPO/RTO 目标已登记（RTO 须实测）
  4. **保留删除**：删除留 tombstone、不可重放、撤权即时生效
  5. **完整追踪**：correlationId/traceId 贯穿，证据可追溯

另：
  6. 无未关闭 BLOCKER/MAJOR
  7. 产物齐备：独立 QA 包、操作说明、部署锁文件
  8. OC-06 范围遵守：每 Loop 均记 scope 声明

退出码：全通过 0，否则 1。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACC = ROOT / "specs" / "knowledge-architecture" / "acceptance"

ACCEPTANCE_AREAS = ["concurrency", "faultInjection", "upgradeRecovery", "retentionDeletion", "tracing"]
REQUIRED_FAULTS = {"DEPENDENCY_UNAVAILABLE", "GRAPH_UNAVAILABLE", "SNAPSHOT_UNAVAILABLE", "TIMEOUT"}


def load(name: str):
    return json.loads((ACC / name).read_text(encoding="utf-8"))


def detect_issues(doc: dict) -> set[str]:
    """统一真值函数：对给定文档求全部验收问题（fail-closed，FAIL-2026-09-12-15）。"""
    found: set[str] = set()
    for i in doc.get("openIssues", []):
        if i.get("severity") in {"BLOCKER", "MAJOR"} and i.get("status") != "CLOSED":
            found.add("OPEN_BLOCKER_BLOCKS_ACCEPTANCE")
    for f in doc.get("faultInjection", {}).get("faults", []):
        if f.get("silentlyDegradedTo200Empty") is True:
            found.add("SILENT_DEGRADE_REJECTED")
    rto = doc.get("upgradeRecovery", {}).get("rto", {})
    if rto and rto.get("measured") is False:
        found.add("RTO_UNMEASURED_REJECTED")
    if doc.get("retentionDeletion", {}).get("replayableAfterDeletion") is True:
        found.add("REPLAY_AFTER_DELETE_REJECTED")
    tr = doc.get("tracing", {})
    if tr and tr.get("traceIdPropagated") is False:
        found.add("TRACE_BREAK_REJECTED")
    return found


REQUIRED_ISSUE_CODES = {
    "OPEN_BLOCKER_BLOCKS_ACCEPTANCE", "SILENT_DEGRADE_REJECTED", "RTO_UNMEASURED_REJECTED",
    "REPLAY_AFTER_DELETE_REJECTED", "TRACE_BREAK_REJECTED",
}


def main() -> int:  # noqa: C901
    failures: list[str] = []

    if not ACC.is_dir():
        print(f"FAIL: acceptance dir missing: {ACC}", file=sys.stderr)
        return 2

    report = load("acceptance_report.json")
    violations = load("violations.json").get("violations", [])

    # 1. 并发
    conc = report.get("concurrency", {})
    if conc.get("casConflictsRejected") is not True:
        failures.append("[1] CAS conflicts must be rejected")
    if conc.get("idempotencyConflictsRejected") is not True:
        failures.append("[1] idempotency conflicts must be rejected")
    if conc.get("duplicateEventsDeduplicated") is not True:
        failures.append("[1] duplicate/out-of-order events must be deduplicated by eventId")
    if conc.get("catalogRevisionChecked") is not True:
        failures.append("[1] catalogRevision must be verified on event replay")

    # 2. 故障注入
    faults = {f.get("fault"): f for f in report.get("faultInjection", {}).get("faults", [])}
    missing_faults = REQUIRED_FAULTS - set(faults)
    if missing_faults:
        failures.append(f"[2] missing fault injection cases: {sorted(missing_faults)}")
    for name, f in faults.items():
        if f.get("silentlyDegradedTo200Empty") is True:
            failures.append(f"[2] {name}: silently degraded to a 200 empty result")
        if name in {"GRAPH_UNAVAILABLE", "DEPENDENCY_UNAVAILABLE", "SNAPSHOT_UNAVAILABLE"}:
            if f.get("statusOrError") not in {503, "SNAPSHOT_UNAVAILABLE", "DEPENDENCY_UNAVAILABLE"}:
                failures.append(f"[2] {name}: unexpected status/error {f.get('statusOrError')!r}")
        if name == "TIMEOUT" and f.get("statusOrError") != "RESULT_UNKNOWN":
            failures.append(f"[2] TIMEOUT must map to RESULT_UNKNOWN, got {f.get('statusOrError')!r}")

    # 3. 升级/恢复
    up = report.get("upgradeRecovery", {})
    if up.get("rebuildableProjections") is not True:
        failures.append("[3] projections must be rebuildable")
    if up.get("publishedVersionsPreservedOnUpgrade") is not True:
        failures.append("[3] upgrade must not drop published versions")
    rpo = up.get("rpo", {})
    if rpo.get("target") != "LATEST_SUCCESSFUL_PERSISTED_SNAPSHOT":
        failures.append(f"[3] RPO target mismatch: {rpo.get('target')!r}")
    rto = up.get("rto", {})
    if rto.get("measured") is not True:
        failures.append("[3] RTO must be MEASURED before a target is submitted (C08 section 6)")
    if rto.get("measured") is True and not rto.get("measuredValue"):
        failures.append("[3] measured RTO must carry an actual value")

    # 4. 保留删除
    ret = report.get("retentionDeletion", {})
    if ret.get("tombstoneRecorded") is not True:
        failures.append("[4] deletion must leave a tombstone")
    if ret.get("replayableAfterDeletion") is True:
        failures.append("[4] deleted content must not be replayable")
    if ret.get("revocationImmediate") is not True:
        failures.append("[4] revocation must take effect immediately")
    if ret.get("awaitingProjectionRebuild") is True:
        failures.append("[4] revocation must not wait for projection rebuild")

    # 5. 完整追踪
    tr = report.get("tracing", {})
    if tr.get("correlationIdPropagated") is not True or tr.get("traceIdPropagated") is not True:
        failures.append("[5] correlationId/traceId must propagate end to end")
    if tr.get("evidenceTraceable") is not True:
        failures.append("[5] evidence must remain traceable")
    if not tr.get("sampledRuns"):
        failures.append("[5] tracing must include sampled runs")

    # 6. 统一真值：正例必须无任何问题
    positive_issues = detect_issues(report)
    if positive_issues:
        failures.append(f"[6] compliant report unexpectedly has issues: {sorted(positive_issues)}")
    open_high = [i for i in report.get("openIssues", [])
                 if i.get("severity") in {"BLOCKER", "MAJOR"} and i.get("status") != "CLOSED"]

    # 7. 产物齐备
    deliverables = report.get("deliverables", {})
    for key in ("independentQaPackage", "operationsGuide", "deploymentLockFile"):
        if not deliverables.get(key):
            failures.append(f"[7] missing deliverable: {key}")
    lock_file = ROOT / str(deliverables.get("deploymentLockFile", ""))
    if deliverables.get("deploymentLockFile") and not lock_file.is_file():
        failures.append(f"[7] deployment lock file not found: {lock_file}")

    # 8. OC-06 范围遵守：每 Loop 均记 scope 声明
    scopes = report.get("oc06ScopeDeclarations", [])
    loops = {s.get("loop") for s in scopes}
    if len(scopes) < 12:
        failures.append(f"[8] OC-06 requires a scope declaration per loop, found {len(scopes)}")
    for s in scopes:
        if s.get("outOfScopeRespected") is not True:
            failures.append(f"[8] {s.get('loop')}: out-of-scope work detected")

    # 负例（fail-closed，可执行）
    violation_seen: set[str] = set()
    required_violations = {"OPEN_BLOCKER_BLOCKS_ACCEPTANCE", "SILENT_DEGRADE_REJECTED",
                           "RTO_UNMEASURED_REJECTED", "REPLAY_AFTER_DELETE_REJECTED",
                           "TRACE_BREAK_REJECTED"}
    if not violations:
        failures.append("[neg] no violation fixtures (assertions would be noop)")
    for v in violations:
        expected = v.get("expectedError")
        detected = detect_issues(v)  # 与正例共用同一真值函数
        if expected not in detected:
            failures.append(f"[neg] {v.get('case')}: expected {expected} not detected "
                            f"(detected={sorted(detected)})")
        else:
            violation_seen.add(expected)
    uncovered = required_violations - violation_seen
    if uncovered:
        failures.append(f"[neg] rejection paths never triggered: {sorted(uncovered)}")

    if failures:
        print("gk-ke-l6-runtime-acceptance-tests: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    print("gk-ke-l6-runtime-acceptance-tests: PASS")
    print(f"  faults={sorted(faults)}")
    print(f"  rpo={rpo.get('target')} rto_measured={rto.get('measured')} value={rto.get('measuredValue')}")
    print(f"  oc06_scope_declarations={len(scopes)}")
    print(f"  open_blocker_major={len(open_high)}")
    print("  checks: concurrency, fault-injection, upgrade-recovery, retention-deletion, tracing, "
          "no-open-blocker, deliverables, oc06-scope")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
