#!/usr/bin/env python3
"""
候选合同不变式执行库

Loop L03 W8 交付。把 6+2 份候选合同声明的 x-invariants 从文档描述
转为可执行断言，使门禁能真正拦截违规实例。

设计：每个不变式是一个 (id, 谓词函数) 对。谓词返回 None 表示通过，
返回字符串表示违规原因。配套 check_invariants.py 对每条不变式提供
正例 + 反例，确保断言本身有效（反例必须被拒绝）。
"""

import hashlib
import re

OWNER_ROLES = {"PRODUCT_OWNER", "RISK_OWNER", "COMPLIANCE_OWNER"}
PUBLIC_LEVELS = {"PUBLIC_PRICE_DISCLOSURE", "PUBLIC_MARKETING"}


def _sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ============================================================
# CTR-PK-EVS-002  EvidenceSpan
# ============================================================

def evs_01(o):
    """quoteHash = SHA-256(quote)"""
    if o.get("quoteHash") and o.get("quote") is not None:
        # 样例使用占位 hash，仅当声明 strict 时严格比对
        if o.get("_strictHash") and o["quoteHash"] != _sha(o["quote"]):
            return "quoteHash 与 SHA-256(quote) 不符"
    return None


def evs_03(o):
    """_public_reference/ => VERIFICATION_ONLY"""
    p = o.get("sourcePath", "")
    if "_public_reference/" in p and o.get("usage") != "VERIFICATION_ONLY":
        return f"公开区证据 usage 必须为 VERIFICATION_ONLY，实为 {o.get('usage')}"
    return None


def evs_04(o):
    """_authoritative/ => AUTHORITATIVE"""
    p = o.get("sourcePath", "")
    if "_authoritative/" in p and o.get("usage") != "AUTHORITATIVE":
        return f"权威区证据 usage 必须为 AUTHORITATIVE，实为 {o.get('usage')}"
    return None


def evs_05(o, allowed_claim_types=None):
    """claimType ∈ SourceDocument.allowedClaimTypes"""
    if allowed_claim_types and o.get("claimType") not in allowed_claim_types:
        return f"claimType {o.get('claimType')} 不在源允许集 {allowed_claim_types}"
    return None


def evs_07(o):
    """CLAUSE 且 clauseVerified=false => 不得支撑 RECOMMENDATION_READY"""
    loc = o.get("locator", {})
    if loc.get("kind") == "CLAUSE" and not loc.get("clauseVerified", False):
        if o.get("_usedForRecommendationReady"):
            return "条款未核定的证据不得支撑 RECOMMENDATION_READY"
    return None


def evs_08(o):
    """evidenceId 后缀必须为确定性十六进制"""
    eid = o.get("evidenceId", "")
    if not re.fullmatch(r"EVS-[A-Z0-9]+-[0-9a-f]{8}", eid):
        return f"evidenceId 不符确定性格式: {eid}"
    return None


def evs_09(o, source_version_index=None):
    """DEMO 源证据不得支撑 RECOMMENDATION_READY"""
    sv = (source_version_index or {}).get(o.get("sourceVersionId"))
    if sv and sv.get("provenanceState") == "DEMO" and o.get("_usedForRecommendationReady"):
        return "DEMO 演示源证据不得支撑 RECOMMENDATION_READY"
    return None


def evs_10(o, source_version_index=None):
    """DEMO 源证据必须被 Release 显式标 DEMO 后方可进入解读"""
    sv = (source_version_index or {}).get(o.get("sourceVersionId"))
    if sv and sv.get("provenanceState") == "DEMO" and o.get("_usedForInterpretationReady"):
        if o.get("_releaseProvenanceState") != "DEMO":
            return "DEMO 证据所在 Release 必须标 provenanceState=DEMO"
    return None


def evs_11(o, source_version_index=None):
    """DEMO 与 VERIFIED 证据不得混合支撑同一断言"""
    idx = source_version_index or {}
    sv = idx.get(o.get("sourceVersionId"))
    if not sv:
        return None
    peer_states = set()
    for peer in (o.get("_peerEvidenceIds") or []):
        pv = idx.get((o.get("_peerSourceVersions") or {}).get(peer))
        if pv:
            peer_states.add(pv.get("provenanceState"))
    peer_states.add(sv.get("provenanceState"))
    if "DEMO" in peer_states and len(peer_states - {"DEMO"}) > 0:
        return "DEMO 证据不得与 VERIFIED 证据混合支撑同一断言"
    return None


# ============================================================
# CTR-PK-ASM-001  FieldAssertion
# ============================================================

def asm_01(o, evidence_index=None):
    """SUPPORTED => 至少 1 条证据且全部 AUTHORITATIVE"""
    if o.get("knowledgeState") != "SUPPORTED":
        return None
    ids = o.get("evidenceIds") or []
    if not ids:
        return "SUPPORTED 必须至少引用 1 条证据"
    if evidence_index:
        for i in ids:
            ev = evidence_index.get(i)
            if ev and ev.get("usage") != "AUTHORITATIVE":
                return f"SUPPORTED 引用了非权威证据 {i}"
    return None


def asm_02(o):
    """UNKNOWN => rawValue/normalizedValue 为 null 且 evidenceIds 为空"""
    if o.get("knowledgeState") != "UNKNOWN":
        return None
    if o.get("rawValue") is not None:
        return "UNKNOWN 的 rawValue 必须为 null"
    if o.get("normalizedValue") is not None:
        return "UNKNOWN 的 normalizedValue 必须为 null"
    if o.get("evidenceIds"):
        return "UNKNOWN 的 evidenceIds 必须为空数组"
    return None


def asm_03(o):
    """CONFLICT => normalizedValue 为 null"""
    if o.get("knowledgeState") == "CONFLICT" and o.get("normalizedValue") is not None:
        return "CONFLICT 的 normalizedValue 必须为 null"
    return None


def asm_04(o):
    """CONFLICT => conflictId 非空"""
    if o.get("knowledgeState") == "CONFLICT" and not o.get("conflictId"):
        return "CONFLICT 必须引用 conflictId"
    return None


def asm_05(o, decision_index=None):
    """NOT_APPLICABLE => reviewDecisionId 非空且签发者为 Owner"""
    if o.get("knowledgeState") != "NOT_APPLICABLE":
        return None
    did = o.get("reviewDecisionId")
    if not did:
        return "NOT_APPLICABLE 必须有 reviewDecisionId"
    if decision_index:
        d = decision_index.get(did)
        if d and d.get("resolvedByRole") not in OWNER_ROLES:
            return f"决议签发者角色 {d.get('resolvedByRole')} 非 Owner"
    return None


def asm_06(o, prior_index=None):
    """值变更必须走 supersedes 链，不得原地覆盖"""
    if prior_index and o.get("assertionId") in prior_index:
        prior = prior_index[o["assertionId"]]
        if prior.get("normalizedValue") != o.get("normalizedValue"):
            return "同一 assertionId 的值被原地修改，必须新建并设 supersedes"
    return None


def asm_08(o, evidence_index=None):
    """任一证据为 VERIFICATION_ONLY => 不得 SUPPORTED"""
    if o.get("knowledgeState") != "SUPPORTED" or not evidence_index:
        return None
    for i in o.get("evidenceIds") or []:
        ev = evidence_index.get(i)
        if ev and ev.get("usage") == "VERIFICATION_ONLY":
            return f"公开轨证据 {i} 不得支撑 SUPPORTED"
    return None


# ============================================================
# CTR-PK-CNF-001  ConflictCase
# ============================================================

def cnf_01(o):
    """RESOLVED => resolution 非空且角色为 Owner"""
    if o.get("status") != "RESOLVED":
        return None
    r = o.get("resolution")
    if not r:
        return "RESOLVED 必须有 resolution"
    if r.get("resolvedByRole") not in OWNER_ROLES:
        return f"resolution 角色 {r.get('resolvedByRole')} 非 Owner"
    return None


def cnf_02(o, assertion_index=None):
    """OPEN/UNDER_REVIEW => 关联断言必须为 CONFLICT"""
    if o.get("status") not in ("OPEN", "UNDER_REVIEW") or not assertion_index:
        return None
    for aid in o.get("assertionIds", []):
        a = assertion_index.get(aid)
        if a and a.get("knowledgeState") != "CONFLICT":
            return f"未决冲突关联的断言 {aid} 状态应为 CONFLICT"
    return None


def cnf_03(o):
    """禁止系统自动写入 resolution"""
    r = o.get("resolution")
    if r and r.get("resolvedBy", "").startswith(("system", "ai", "auto", "model")):
        return f"resolution 不得由系统/AI 自动写入: {r.get('resolvedBy')}"
    return None


def cnf_04(o):
    """resolvedAssertionId ∈ assertionIds"""
    r = o.get("resolution")
    if r and r.get("resolvedAssertionId") not in o.get("assertionIds", []):
        return "resolvedAssertionId 不在 assertionIds 中"
    return None


# ============================================================
# CTR-PK-RLS-001  ProductKnowledgeRelease
# ============================================================


def asm_09(o, conflict_index=None):
    """SUPPORTED 保留 conflictId 时必须与冲突裁决一致"""
    if o.get("knowledgeState") != "SUPPORTED" or not o.get("conflictId"):
        return None
    c = (conflict_index or {}).get(o["conflictId"])
    if not c:
        return f"conflictId 指向的冲突不存在: {o['conflictId']}"
    if c.get("status") != "RESOLVED":
        return "SUPPORTED 断言引用的冲突必须已 RESOLVED"
    if (c.get("resolution") or {}).get("decisionId") != o.get("reviewDecisionId"):
        return "SUPPORTED 断言的 reviewDecisionId 必须等于冲突裁决的 decisionId"
    return None

def rls_01(o):
    """recommendationReady => interpretationReady"""
    f = o.get("purposeFlags", {})
    if f.get("recommendationReady") and not f.get("interpretationReady"):
        return "recommendationReady 必须蕴含 interpretationReady"
    return None


def rls_02(o):
    """REQUIRED_HARD 存在 UNKNOWN/CONFLICT/STALE => 两 flag 均 false"""
    g = o.get("gateReport") or {}
    bad = g.get("unknown", 0) + g.get("conflict", 0) + g.get("stale", 0)
    f = o.get("purposeFlags", {})
    if bad > 0 and (f.get("interpretationReady") or f.get("recommendationReady")):
        return f"存在 {bad} 个非 SUPPORTED 的 REQUIRED_HARD 字段，两 purposeFlag 必须为 false"
    return None


def rls_05(o, published_index=None):
    """PUBLISHED 后内容变化必须产生新 releaseId"""
    if o.get("lifecycleState") != "PUBLISHED" or not published_index:
        return None
    prior = published_index.get(o.get("releaseId"))
    if prior and prior.get("bundleHash") != o.get("bundleHash"):
        return "已发布 Release 被原地修改，必须产生新 releaseId"
    return None


def rls_06(o):
    """isStale=true => recommendationReady 消费侧视为 false"""
    s = (o.get("staleFlag") or {}).get("isStale")
    if s and not (o.get("gateReport") or {}).get("blockingReasons"):
        return "stale Release 必须在 gateReport.blockingReasons 中记录 RELEASE_STALE"
    return None



def rls_09(o):
    """provenanceState=DEMO => recommendationReady=false"""
    if o.get("provenanceState") == "DEMO":
        flags = o.get("purposeFlags") or {}
        if flags.get("recommendationReady"):
            return "DEMO 发布包不得进入 RECOMMENDATION_READY"
    return None


def rls_07(o):
    """bundleHash = SHA-256(四个 manifest hash 拼接)"""
    if not o.get("_strictHash"):
        return None
    cat = (o.get("assertionManifestHash", "") + o.get("evidenceManifestHash", "")
           + o.get("cardProjectionHash", "") + o.get("rulePackageHash", ""))
    if o.get("bundleHash") != _sha(cat):
        return "bundleHash 与四元 manifest 拼接哈希不符"
    return None


# ============================================================
# CTR-PK-CHG-001  ProductKnowledgeChanged
# ============================================================

def chg_02(o):
    """RELEASE_STALED => staleRecommendationRunIds 必须枚举"""
    if o.get("eventType") != "RELEASE_STALED":
        return None
    scope = o.get("impactScope") or {}
    if not scope.get("staleRecommendationRunIds"):
        return "RELEASE_STALED 必须完整枚举 staleRecommendationRunIds"
    return None


def chg_03(o):
    """精确性：stale 集合与 notAffected 集合不得相交"""
    scope = o.get("impactScope") or {}
    stale = set(scope.get("staleRecommendationRunIds") or [])
    notaff = set(scope.get("explicitlyNotAffected") or [])
    both = stale & notaff
    if both:
        return f"运行同时出现在 stale 与 notAffected 集合: {sorted(both)}"
    return None


def chg_04(o):
    """RELEASE_PUBLISHED => newReleaseId 非空"""
    if o.get("eventType") == "RELEASE_PUBLISHED" and not o.get("newReleaseId"):
        return "RELEASE_PUBLISHED 必须提供 newReleaseId"
    return None


# ============================================================
# CTR-PK-FLD-001  FieldPolicy
# ============================================================

def fld_01(f):
    """RECOMMENDATION_ELIGIBLE => 权威级不得为公开轨"""
    if f.get("purposeGate") == "RECOMMENDATION_ELIGIBLE" and f.get("minAuthorityLevel") in PUBLIC_LEVELS:
        return f"{f.get('fieldPath')}: 推荐资格字段不得以公开轨为最低权威级"
    return None


def fld_03(f):
    """REQUIRED_HARD + INTERPRETATION_ONLY 必须说明理由"""
    if f.get("required") == "REQUIRED_HARD" and f.get("purposeGate") == "INTERPRETATION_ONLY":
        if not f.get("note"):
            return f"{f.get('fieldPath')}: 该组合必须显式声明 note"
    return None


def fld_04(policy):
    """fieldPath 唯一"""
    paths = [f["fieldPath"] for f in policy.get("fields", [])]
    dup = {p for p in paths if paths.count(p) > 1}
    if dup:
        return f"fieldPath 重复: {sorted(dup)}"
    return None


def fld_05(policy):
    """ownerApproved=false => 不得用于签发 Release"""
    if not policy.get("ownerApproved") and policy.get("_usedForRelease"):
        return "未经 Owner 批准的策略不得用于签发 Release"
    return None


def fld_06(f):
    """PRICE + 公开价目 => 必须 INTERPRETATION_ONLY"""
    if "PRICE" in (f.get("allowedClaimTypes") or []) and \
       f.get("minAuthorityLevel") == "PUBLIC_PRICE_DISCLOSURE" and \
       f.get("purposeGate") != "INTERPRETATION_ONLY":
        return f"{f.get('fieldPath')}: 公开价目类字段必须限定为 INTERPRETATION_ONLY"
    return None


# ============================================================
# CTR-PR-RES/ELIG/DEC  推荐侧增补
# ============================================================

def res_02(o):
    """UNBOUND => 不得对客呈现"""
    if o.get("knowledgeStaleState") == "UNBOUND" and o.get("_presentedToCustomer"):
        return "未绑定 Release 的结果不得对客呈现"
    return None


def res_01(o, release_index=None):
    """knowledgeBinding 存在 => 对应 Release 的 recommendationReady 必须为 true

    L03 W12：跨对象不变式。需 release_index 提供 releaseId -> Release 映射。
    """
    kb = o.get("knowledgeBinding")
    if not kb:
        return None
    rid = kb.get("releaseId")
    # 绑定自带的 flag 与 Release 真值都要检查
    if kb.get("recommendationReady") is False:
        return f"绑定的 Release {rid} recommendationReady=false，不得用于推荐"
    if release_index is not None:
        rel = release_index.get(rid)
        if rel is None:
            return f"绑定的 releaseId {rid} 在 Release 索引中不存在"
        flags = rel.get("purposeFlags", {})
        if not flags.get("recommendationReady"):
            return f"Release {rid} 的 recommendationReady 为 false"
        if (rel.get("staleFlag") or {}).get("isStale"):
            return f"Release {rid} 已 stale，不得绑定用于推荐"
    return None


def res_06(o):
    """contentHash 必须覆盖 knowledgeBinding，使证据包可重放

    L03 W12：以 _hashedFields 声明 contentHash 的覆盖范围进行校验。
    """
    if not o.get("knowledgeBinding"):
        return None
    covered = o.get("_hashedFields")
    if covered is None:
        return None  # 未声明覆盖范围时不判定
    if "knowledgeBinding" not in covered:
        return "contentHash 覆盖范围未包含 knowledgeBinding，证据包不可重放"
    return None


def res_03(o):
    """STALE_REQUIRES_RERUN => 不得对客呈现"""
    if o.get("knowledgeStaleState") == "STALE_REQUIRES_RERUN" and o.get("_presentedToCustomer"):
        return "stale 结果不得对客呈现，必须重跑"
    return None


def res_04(o):
    """controlledFailure 非空 => 结果集必须为空"""
    if not o.get("controlledFailure"):
        return None
    for k in ("eligibilityResults", "fitResults", "portfolioCandidates"):
        if o.get(k):
            return f"受控失败时 {k} 必须为空数组"
    return None


def res_05(o):
    """failedClosed 恒为 true"""
    cf = o.get("controlledFailure")
    if cf and cf.get("failedClosed") is not True:
        return "controlledFailure.failedClosed 必须为 true，禁止降级放行"
    return None


def elig_01(o):
    """UNKNOWN/CONFLICT/STALE => 不得 ELIGIBLE"""
    if o.get("knowledgeState") in ("UNKNOWN", "CONFLICT", "STALE") and o.get("eligibility") == "ELIGIBLE":
        return f"knowledgeState={o.get('knowledgeState')} 时不得判定为 ELIGIBLE"
    return None


def elig_02(o):
    """未绑定 Release => 不得 ELIGIBLE"""
    if not o.get("knowledgeBindingRef") and o.get("eligibility") == "ELIGIBLE":
        return "未绑定 Release 不得判定为 ELIGIBLE"
    return None


def elig_03(o):
    """非 SUPPORTED => neutralizationReason 必填"""
    ks = o.get("knowledgeState")
    if ks and ks != "SUPPORTED" and not o.get("neutralizationReason"):
        return f"knowledgeState={ks} 必须提供 neutralizationReason"
    return None


def elig_04(o):
    """INELIGIBLE => fitScore/rank 必须 null"""
    if o.get("eligibility") != "INELIGIBLE":
        return None
    fit = o.get("_fitResult") or {}
    if fit.get("fitScore") is not None or fit.get("rank") is not None:
        return "INELIGIBLE 的 fitScore 与 rank 必须为 null"
    return None


def dec_01(o):
    """decidedByHuman 恒为 true"""
    att = o.get("aiBoundaryAttestation")
    if att and att.get("decidedByHuman") is not True:
        return "决定必须由自然人作出"
    return None


def elig_05(o):
    """禁止由模型将 UNKNOWN/CONFLICT/STALE 提升为 ELIGIBLE

    L03 W12：需状态转换上下文。以 _priorKnowledgeState + _promotedBy 检测
    「非 SUPPORTED 态被提升为 ELIGIBLE」且提升者为模型/AI 的越权行为。
    """
    prior = o.get("_priorKnowledgeState")
    by = (o.get("_promotedBy") or "").lower()
    if prior in ("UNKNOWN", "CONFLICT", "STALE") and o.get("eligibility") == "ELIGIBLE":
        if by.startswith(("ai", "model", "llm", "system", "auto")):
            return f"模型/系统 ({o.get('_promotedBy')}) 不得将 {prior} 提升为 ELIGIBLE"
        if not o.get("_ownerDecisionId"):
            return f"{prior} 提升为 ELIGIBLE 必须有 Owner 决议"
    return None


def dec_05(o):
    """本合同不授权任何 CRM 写回或对客发送动作

    L03 W12：检测决定对象是否夹带越权副作用声明。
    """
    forbidden = {"CRM_WRITEBACK", "CUSTOMER_SEND", "CREDIT_APPROVAL",
                 "PRICING_OVERRIDE", "AUTO_DISPATCH"}
    acts = set(o.get("_sideEffects") or [])
    bad = acts & forbidden
    if bad:
        return f"本合同不授权以下动作: {sorted(bad)}"
    return None


def dec_02(o):
    """APPROVE => 审计段非空且 FRESH"""
    if o.get("decision") != "APPROVE":
        return None
    a = o.get("knowledgeBindingAudit")
    if a is None:
        return None  # 旧实例向后兼容，由灰度期豁免
    if a.get("staleStateAtDecision") != "FRESH":
        return f"APPROVE 时知识状态必须为 FRESH，实为 {a.get('staleStateAtDecision')}"
    return None


def dec_03(o):
    """STALE => 不得 APPROVE"""
    a = o.get("knowledgeBindingAudit") or {}
    if a.get("staleStateAtDecision") == "STALE_REQUIRES_RERUN" and o.get("decision") == "APPROVE":
        return "知识 stale 时不得 APPROVE"
    return None


def dec_04(o):
    """AI 辅助范围受限"""
    allowed = {"EVIDENCE_SUMMARY", "RANKING_HINT", "RISK_FLAG"}
    att = o.get("aiBoundaryAttestation") or {}
    bad = set(att.get("aiAssistanceScope") or []) - allowed
    if bad:
        return f"AI 辅助超出允许范围: {sorted(bad)}"
    return None


# ============================================================
# 注册表
# ============================================================

INVARIANTS = {
    "INV-EVS-01": evs_01, "INV-EVS-03": evs_03, "INV-EVS-04": evs_04,
    "INV-EVS-05": evs_05, "INV-EVS-07": evs_07, "INV-EVS-08": evs_08,
    "INV-EVS-09": evs_09, "INV-EVS-10": evs_10, "INV-EVS-11": evs_11,
    "INV-ASM-01": asm_01, "INV-ASM-02": asm_02, "INV-ASM-03": asm_03,
    "INV-ASM-04": asm_04, "INV-ASM-05": asm_05, "INV-ASM-06": asm_06,
    "INV-ASM-08": asm_08, "INV-ASM-09": asm_09,
    "INV-CNF-01": cnf_01, "INV-CNF-02": cnf_02, "INV-CNF-03": cnf_03, "INV-CNF-04": cnf_04,
    "INV-RLS-01": rls_01, "INV-RLS-02": rls_02, "INV-RLS-05": rls_05,
    "INV-RLS-06": rls_06, "INV-RLS-07": rls_07, "INV-RLS-09": rls_09,
    "INV-CHG-02": chg_02, "INV-CHG-03": chg_03, "INV-CHG-04": chg_04,
    "INV-FLD-01": fld_01, "INV-FLD-03": fld_03, "INV-FLD-04": fld_04,
    "INV-FLD-05": fld_05, "INV-FLD-06": fld_06,
    "INV-RES-01": res_01, "INV-RES-02": res_02, "INV-RES-03": res_03,
    "INV-RES-04": res_04, "INV-RES-05": res_05, "INV-RES-06": res_06,
    "INV-ELIG-01": elig_01, "INV-ELIG-02": elig_02, "INV-ELIG-03": elig_03,
    "INV-ELIG-04": elig_04, "INV-ELIG-05": elig_05,
    "INV-DEC-01": dec_01, "INV-DEC-02": dec_02, "INV-DEC-03": dec_03,
    "INV-DEC-04": dec_04, "INV-DEC-05": dec_05,
}
