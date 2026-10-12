#!/usr/bin/env python3
"""
不变式执行测试器

Loop L03 W8 交付。对 invariants.py 中每条不变式提供 正例 + 反例：
  - 正例必须通过（返回 None）
  - 反例必须被拒绝（返回非空原因）

反例被拒是核心：若某不变式对反例也返回 None，说明该断言写错了/没有实际约束力，
判 FAIL。这防止「有不变式文档但无执行力」的假安全。

用法:
    python3 specs/product-knowledge/check_invariants.py
退出码 0 表示全部通过。
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from invariants import INVARIANTS  # noqa: E402

results = []


def case(inv_id, positive, negative, kwargs=None):
    """注册一条不变式的正/反例。"""
    return (inv_id, positive, negative, kwargs or {})


# ---------- 公共夹具 ----------
EV_AUTH = {"usage": "AUTHORITATIVE"}
EV_PUB = {"usage": "VERIFICATION_ONLY"}
EVIDX = {"EVS-A-11111111": EV_AUTH, "EVS-P-22222222": EV_PUB}
DECIDX = {"DEC-20260905-aaaaaaaa": {"resolvedByRole": "PRODUCT_OWNER"},
          "DEC-20260905-bbbbbbbb": {"resolvedByRole": "ANALYST"}}

CASES = [
    # ---- EvidenceSpan ----
    case("INV-EVS-01",
         {"quote": "abc", "quoteHash": "x", "_strictHash": False},
         {"quote": "abc", "quoteHash": "deadbeef", "_strictHash": True}),
    case("INV-EVS-03",
         {"sourcePath": "01_raw/_public_reference/a.pdf", "usage": "VERIFICATION_ONLY"},
         {"sourcePath": "01_raw/_public_reference/a.pdf", "usage": "AUTHORITATIVE"}),
    case("INV-EVS-04",
         {"sourcePath": "01_raw/_authoritative/b.pdf", "usage": "AUTHORITATIVE"},
         {"sourcePath": "01_raw/_authoritative/b.pdf", "usage": "VERIFICATION_ONLY"}),
    case("INV-EVS-05",
         {"claimType": "PRICE"}, {"claimType": "RISK"},
         {"allowed_claim_types": ["PRICE", "PROCESS"]}),
    case("INV-EVS-07",
         {"locator": {"kind": "CLAUSE", "clauseVerified": True}, "_usedForRecommendationReady": True},
         {"locator": {"kind": "CLAUSE", "clauseVerified": False}, "_usedForRecommendationReady": True}),
    case("INV-EVS-08",
         {"evidenceId": "EVS-REGCM001-3f2a9c11"},
         {"evidenceId": "EVS-REGCM001-3F2A9C11"}),
    case("INV-EVS-09",
         {"sourceVersionId": "SV-SRCCM001-20260906-11111111"},
         {"sourceVersionId": "SV-SRCCM001-20260906-11111111",
          "_usedForRecommendationReady": True},
         {"source_version_index": {"SV-SRCCM001-20260906-11111111":
                                   {"provenanceState": "DEMO"}}}),
    case("INV-EVS-10",
         {"sourceVersionId": "SV-SRCCM001-20260906-11111111",
          "_usedForInterpretationReady": True, "_releaseProvenanceState": "DEMO"},
         {"sourceVersionId": "SV-SRCCM001-20260906-11111111",
          "_usedForInterpretationReady": True, "_releaseProvenanceState": "VERIFIED"},
         {"source_version_index": {"SV-SRCCM001-20260906-11111111":
                                   {"provenanceState": "DEMO"}}}),
    case("INV-EVS-11",
         {"sourceVersionId": "SV-SRCCM001-20260906-11111111",
          "_peerEvidenceIds": ["EVS-B-33333333"],
          "_peerSourceVersions": {"EVS-B-33333333": "SV-SRCCM001-20260906-11111111"}},
         {"sourceVersionId": "SV-SRCCM001-20260906-11111111",
          "_peerEvidenceIds": ["EVS-B-33333333"],
          "_peerSourceVersions": {"EVS-B-33333333": "SV-REGCM001-20260904-105df242"}},
         {"source_version_index": {"SV-SRCCM001-20260906-11111111": {"provenanceState": "DEMO"},
                                   "SV-REGCM001-20260904-105df242": {"provenanceState": "VERIFIED"}}}),

    # ---- FieldAssertion ----
    case("INV-ASM-01",
         {"knowledgeState": "SUPPORTED", "evidenceIds": ["EVS-A-11111111"]},
         {"knowledgeState": "SUPPORTED", "evidenceIds": []},
         {"evidence_index": EVIDX}),
    case("INV-ASM-02",
         {"knowledgeState": "UNKNOWN", "rawValue": None, "normalizedValue": None, "evidenceIds": []},
         {"knowledgeState": "UNKNOWN", "rawValue": None, "normalizedValue": 120, "evidenceIds": []}),
    case("INV-ASM-03",
         {"knowledgeState": "CONFLICT", "normalizedValue": None},
         {"knowledgeState": "CONFLICT", "normalizedValue": 120}),
    case("INV-ASM-04",
         {"knowledgeState": "CONFLICT", "conflictId": "CNF-X-aabbccdd"},
         {"knowledgeState": "CONFLICT", "conflictId": None}),
    case("INV-ASM-05",
         {"knowledgeState": "NOT_APPLICABLE", "reviewDecisionId": "DEC-20260905-aaaaaaaa"},
         {"knowledgeState": "NOT_APPLICABLE", "reviewDecisionId": "DEC-20260905-bbbbbbbb"},
         {"decision_index": DECIDX}),
    case("INV-ASM-06",
         {"assertionId": "ASM-X-11111111", "normalizedValue": "v1"},
         {"assertionId": "ASM-X-22222222", "normalizedValue": "CHANGED"},
         {"prior_index": {"ASM-X-22222222": {"normalizedValue": "v1"}}}),
    case("INV-ASM-08",
         {"knowledgeState": "SUPPORTED", "evidenceIds": ["EVS-A-11111111"]},
         {"knowledgeState": "SUPPORTED", "evidenceIds": ["EVS-P-22222222"]},
         {"evidence_index": EVIDX}),
    case("INV-ASM-09",
         {"knowledgeState": "SUPPORTED", "conflictId": "CNF-A-11111111",
          "reviewDecisionId": "DEC-1"},
         {"knowledgeState": "SUPPORTED", "conflictId": "CNF-A-11111111",
          "reviewDecisionId": "DEC-OTHER"},
         {"conflict_index": {"CNF-A-11111111": {"status": "RESOLVED",
                                                "resolution": {"decisionId": "DEC-1"}}}}),

    # ---- ConflictCase ----
    case("INV-CNF-01",
         {"status": "RESOLVED", "resolution": {"resolvedByRole": "PRODUCT_OWNER"}},
         {"status": "RESOLVED", "resolution": {"resolvedByRole": "ANALYST"}}),
    case("INV-CNF-02",
         {"status": "OPEN", "assertionIds": ["A1"]},
         {"status": "OPEN", "assertionIds": ["A2"]},
         {"assertion_index": {"A1": {"knowledgeState": "CONFLICT"},
                              "A2": {"knowledgeState": "SUPPORTED"}}}),
    case("INV-CNF-03",
         {"resolution": {"resolvedBy": "product.owner@example"}},
         {"resolution": {"resolvedBy": "system.autoresolver"}}),
    case("INV-CNF-04",
         {"assertionIds": ["A1", "A2"], "resolution": {"resolvedAssertionId": "A1"}},
         {"assertionIds": ["A1", "A2"], "resolution": {"resolvedAssertionId": "A9"}}),

    # ---- Release ----
    case("INV-RLS-01",
         {"purposeFlags": {"interpretationReady": True, "recommendationReady": True}},
         {"purposeFlags": {"interpretationReady": False, "recommendationReady": True}}),
    case("INV-RLS-02",
         {"gateReport": {"unknown": 0, "conflict": 0, "stale": 0},
          "purposeFlags": {"interpretationReady": True, "recommendationReady": True}},
         {"gateReport": {"unknown": 3, "conflict": 0, "stale": 0},
          "purposeFlags": {"interpretationReady": True, "recommendationReady": False}}),
    case("INV-RLS-05",
         {"lifecycleState": "PUBLISHED", "releaseId": "R1", "bundleHash": "h1"},
         {"lifecycleState": "PUBLISHED", "releaseId": "R1", "bundleHash": "h2"},
         {"published_index": {"R1": {"bundleHash": "h1"}}}),
    case("INV-RLS-06",
         {"staleFlag": {"isStale": True}, "gateReport": {"blockingReasons": ["RELEASE_STALE"]}},
         {"staleFlag": {"isStale": True}, "gateReport": {"blockingReasons": []}}),
    case("INV-RLS-07",
         {"_strictHash": False, "bundleHash": "whatever"},
         {"_strictHash": True, "assertionManifestHash": "a", "evidenceManifestHash": "b",
          "cardProjectionHash": "c", "rulePackageHash": "d", "bundleHash": "wrong"}),
    case("INV-RLS-09",
         {"provenanceState": "DEMO", "purposeFlags": {"recommendationReady": False}},
         {"provenanceState": "DEMO", "purposeFlags": {"recommendationReady": True}}),

    # ---- ChangeEvent ----
    case("INV-CHG-02",
         {"eventType": "RELEASE_STALED", "impactScope": {"staleRecommendationRunIds": ["R1"]}},
         {"eventType": "RELEASE_STALED", "impactScope": {"staleRecommendationRunIds": []}}),
    case("INV-CHG-03",
         {"impactScope": {"staleRecommendationRunIds": ["R1"], "explicitlyNotAffected": ["R2"]}},
         {"impactScope": {"staleRecommendationRunIds": ["R1"], "explicitlyNotAffected": ["R1"]}}),
    case("INV-CHG-04",
         {"eventType": "RELEASE_PUBLISHED", "newReleaseId": "RLS-2026.09.01.1"},
         {"eventType": "RELEASE_PUBLISHED", "newReleaseId": None}),

    # ---- FieldPolicy ----
    case("INV-FLD-01",
         {"fieldPath": "a.b", "purposeGate": "RECOMMENDATION_ELIGIBLE", "minAuthorityLevel": "INTERNAL_POLICY"},
         {"fieldPath": "a.b", "purposeGate": "RECOMMENDATION_ELIGIBLE", "minAuthorityLevel": "PUBLIC_PRICE_DISCLOSURE"}),
    case("INV-FLD-03",
         {"fieldPath": "a.b", "required": "REQUIRED_HARD", "purposeGate": "INTERPRETATION_ONLY", "note": "理由"},
         {"fieldPath": "a.b", "required": "REQUIRED_HARD", "purposeGate": "INTERPRETATION_ONLY"}),
    case("INV-FLD-04",
         {"fields": [{"fieldPath": "a.b"}, {"fieldPath": "c.d"}]},
         {"fields": [{"fieldPath": "a.b"}, {"fieldPath": "a.b"}]}),
    case("INV-FLD-05",
         {"ownerApproved": True, "_usedForRelease": True},
         {"ownerApproved": False, "_usedForRelease": True}),
    case("INV-FLD-06",
         {"fieldPath": "p.f", "allowedClaimTypes": ["PRICE"],
          "minAuthorityLevel": "PUBLIC_PRICE_DISCLOSURE", "purposeGate": "INTERPRETATION_ONLY"},
         {"fieldPath": "p.f", "allowedClaimTypes": ["PRICE"],
          "minAuthorityLevel": "PUBLIC_PRICE_DISCLOSURE", "purposeGate": "RECOMMENDATION_ELIGIBLE"}),

    # ---- 推荐侧 ----
    case("INV-RES-01",
         {"knowledgeBinding": {"releaseId": "RLS-2026.09.01.1", "recommendationReady": True}},
         {"knowledgeBinding": {"releaseId": "RLS-2026.08.01.1", "recommendationReady": True}},
         {"release_index": {
             "RLS-2026.09.01.1": {"purposeFlags": {"recommendationReady": True},
                                  "staleFlag": {"isStale": False}},
             "RLS-2026.08.01.1": {"purposeFlags": {"recommendationReady": True},
                                  "staleFlag": {"isStale": True}}}}),
    case("INV-RES-06",
         {"knowledgeBinding": {"releaseId": "R1"},
          "_hashedFields": ["runId", "knowledgeBinding", "eligibilityResults"]},
         {"knowledgeBinding": {"releaseId": "R1"},
          "_hashedFields": ["runId", "eligibilityResults"]}),
    case("INV-RES-02",
         {"knowledgeStaleState": "FRESH", "_presentedToCustomer": True},
         {"knowledgeStaleState": "UNBOUND", "_presentedToCustomer": True}),
    case("INV-RES-03",
         {"knowledgeStaleState": "FRESH", "_presentedToCustomer": True},
         {"knowledgeStaleState": "STALE_REQUIRES_RERUN", "_presentedToCustomer": True}),
    case("INV-RES-04",
         {"controlledFailure": {"code": "FAILED_CLOSED"}, "eligibilityResults": [],
          "fitResults": [], "portfolioCandidates": []},
         {"controlledFailure": {"code": "FAILED_CLOSED"}, "eligibilityResults": [{"x": 1}],
          "fitResults": [], "portfolioCandidates": []}),
    case("INV-RES-05",
         {"controlledFailure": {"failedClosed": True}},
         {"controlledFailure": {"failedClosed": False}}),
    case("INV-ELIG-01",
         {"knowledgeState": "SUPPORTED", "eligibility": "ELIGIBLE"},
         {"knowledgeState": "STALE", "eligibility": "ELIGIBLE"}),
    case("INV-ELIG-02",
         {"knowledgeBindingRef": "RLS-2026.09.01.1", "eligibility": "ELIGIBLE"},
         {"knowledgeBindingRef": None, "eligibility": "ELIGIBLE"}),
    case("INV-ELIG-03",
         {"knowledgeState": "STALE", "neutralizationReason": "KNOWLEDGE_STALE"},
         {"knowledgeState": "STALE", "neutralizationReason": None}),
    case("INV-ELIG-04",
         {"eligibility": "INELIGIBLE", "_fitResult": {"fitScore": None, "rank": None}},
         {"eligibility": "INELIGIBLE", "_fitResult": {"fitScore": 0.8, "rank": 1}}),
    case("INV-ELIG-05",
         {"_priorKnowledgeState": "UNKNOWN", "eligibility": "ELIGIBLE",
          "_promotedBy": "product.owner@example", "_ownerDecisionId": "DEC-20260905-aaaaaaaa"},
         {"_priorKnowledgeState": "UNKNOWN", "eligibility": "ELIGIBLE",
          "_promotedBy": "ai.recommender"}),
    case("INV-DEC-01",
         {"aiBoundaryAttestation": {"decidedByHuman": True}},
         {"aiBoundaryAttestation": {"decidedByHuman": False}}),
    case("INV-DEC-02",
         {"decision": "APPROVE", "knowledgeBindingAudit": {"staleStateAtDecision": "FRESH"}},
         {"decision": "APPROVE", "knowledgeBindingAudit": {"staleStateAtDecision": "UNBOUND"}}),
    case("INV-DEC-03",
         {"decision": "REJECT", "knowledgeBindingAudit": {"staleStateAtDecision": "STALE_REQUIRES_RERUN"}},
         {"decision": "APPROVE", "knowledgeBindingAudit": {"staleStateAtDecision": "STALE_REQUIRES_RERUN"}}),
    case("INV-DEC-04",
         {"aiBoundaryAttestation": {"aiAssistanceScope": ["EVIDENCE_SUMMARY", "RANKING_HINT"]}},
         {"aiBoundaryAttestation": {"aiAssistanceScope": ["CREDIT_APPROVAL"]}}),
    case("INV-DEC-05",
         {"decision": "APPROVE", "_sideEffects": ["AUDIT_LOG", "TASK_CREATE"]},
         {"decision": "APPROVE", "_sideEffects": ["AUDIT_LOG", "CRM_WRITEBACK"]}),
]


def main():
    covered = set()
    for inv_id, pos, neg, kw in CASES:
        fn = INVARIANTS.get(inv_id)
        if fn is None:
            results.append((f"{inv_id} 已注册", False, "未在 INVARIANTS 中找到"))
            print(f"FAIL | {inv_id} 已注册 | 未在 INVARIANTS 中找到")
            continue
        covered.add(inv_id)

        r_pos = fn(pos, **kw)
        ok_pos = r_pos is None
        results.append((f"{inv_id} 正例通过", ok_pos, r_pos or ""))
        print(f"{'PASS' if ok_pos else 'FAIL'} | {inv_id} 正例通过" + (f" | {r_pos}" if r_pos else ""))

        r_neg = fn(neg, **kw)
        ok_neg = r_neg is not None
        results.append((f"{inv_id} 反例被拒", ok_neg, r_neg or "反例未被拒绝——断言无约束力"))
        print(f"{'PASS' if ok_neg else 'FAIL'} | {inv_id} 反例被拒"
              + (f" | {r_neg}" if ok_neg else " | 反例未被拒绝——断言无约束力"))

    uncovered = sorted(set(INVARIANTS) - covered)
    ok_cov = not uncovered
    results.append(("全部注册不变式均有测试用例", ok_cov, f"未覆盖: {uncovered}" if uncovered else ""))
    print(f"{'PASS' if ok_cov else 'FAIL'} | 全部注册不变式均有测试用例"
          + (f" | 未覆盖: {uncovered}" if uncovered else ""))

    failed = [r for r in results if not r[1]]
    print(f"\n{'=' * 60}")
    print(f"不变式执行测试：{len(results) - len(failed)}/{len(results)} PASS"
          f"（覆盖 {len(covered)} 条不变式，正反例各 1）")
    if failed:
        print("失败项：")
        for n, _, d in failed:
            print(f"  - {n} {d}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
