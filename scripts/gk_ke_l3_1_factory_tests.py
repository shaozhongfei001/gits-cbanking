#!/usr/bin/env python3
"""GK-KE L3-1 工厂与候选测试（C08 L3-1 / wave C2）。

依据 C03 §2 P01–P10 流水线（本 Loop 覆盖 P01–P06）与必需阻断条件。
覆盖 C08 L3-1 退出标准：「18 文档全可回链；注入/同名/时态负例保留」。

检查（P01–P06 阻断条件）：
  P01 接入：来源不可验证 / 用途不允许 → 阻断
  P02 解析：表头丢失 / 关键金额识别不可靠 → 阻断
  P03 抽取：无原文支持 / 单位缺失 / 预测伪装事实 → 阻断
  P04 对齐：同名主体无法区分不得自动合并 → 阻断
  P05 组图：文档出现的工具名称不得自动注册为执行能力 → 阻断
  P06 质量冲突：必需规则缺口 / 身份不明 / 来源矛盾 → 阻断

另：
  - 18 文档全可回链（原始 sourceId+version → Fragment 坐标 → EvidenceSpan）
  - 可恢复 ingestion job（分步状态可续跑）
  - 候选隔离（候选不得与已发布混放）

退出码：全通过 0，否则 1。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FACTORY = ROOT / "specs" / "knowledge-architecture" / "factory"
NEG = FACTORY / "negatives"
SIM_DOCS = ROOT / "docs" / "dd" / "gk-ke-contract" / "simulation" / "documents"

# C03 P01-P06 的必需阻断条件
BLOCKING_CONDITIONS = {
    "P01": {"SOURCE_UNVERIFIABLE", "PURPOSE_NOT_ALLOWED"},
    "P02": {"HEADER_LOST", "AMOUNT_EXTRACTION_UNRELIABLE"},
    "P03": {"NO_SOURCE_SUPPORT", "UNIT_MISSING", "PREDICTION_AS_FACT"},
    "P04": {"AMBIGUOUS_SUBJECT_NOT_AUTO_MERGED"},
    "P05": {"TOOL_NAME_NOT_AUTO_REGISTERED"},
    "P06": {"MANDATORY_RULE_GAP", "IDENTITY_UNKNOWN", "SOURCE_CONTRADICTION"},
}

EXPECTED_DOC_COUNT = 18


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:  # noqa: C901
    failures: list[str] = []

    if not FACTORY.is_dir():
        print(f"FAIL: factory dir missing: {FACTORY}", file=sys.stderr)
        return 2

    job = load(FACTORY / "ingestion_job.json")
    fragments = load(FACTORY / "fragments.json")
    assertions = load(FACTORY / "candidate_assertions.json")
    review = load(FACTORY / "review_package.json")
    negatives = sorted(NEG.glob("*.json")) if NEG.is_dir() else []

    # --- 18 文档全可回链 ---
    # 文档计数按 (sourceId, sourceVersion)：C07 §3 的 18 份中含「同产品新旧版本 2 份」，
    # 故唯一 sourceId 数(17) < 文档数(18)。不得用去重 sourceId 计数（FAIL-2026-09-12-10）。
    doc_keys = {(f["sourceId"], f["sourceVersion"]) for f in fragments.get("fragments", [])}
    if len(doc_keys) != EXPECTED_DOC_COUNT:
        failures.append(f"[chain] expected {EXPECTED_DOC_COUNT} document versions, got {len(doc_keys)}")
    # 版本对必须存在且未被误合并（C07 §3 旧/新版差异是时态负例的载体）
    by_source: dict[str, set] = {}
    for sid, ver in doc_keys:
        by_source.setdefault(sid, set()).add(ver)
    if not any(len(vers) >= 2 for vers in by_source.values()):
        failures.append("[chain] no multi-version document pair found (version pair was collapsed)")
    frag_by_id = {f["fragmentId"]: f for f in fragments.get("fragments", [])}
    for frag in fragments.get("fragments", []):
        for field in ("fragmentId", "sourceId", "sourceVersion", "locator", "parseVersion"):
            if field not in frag:
                failures.append(f"[chain] fragment {frag.get('fragmentId')} missing {field}")
    for item in assertions.get("assertions", []):
        # P03：断言必须有原文支持（EvidenceSpan → Fragment → Source）
        span = item.get("evidenceSpan") or {}
        frag_id = span.get("fragmentId")
        if frag_id not in frag_by_id:
            failures.append(f"[P03] assertion {item.get('assertionId')}: evidenceSpan -> unknown fragment")
            continue
        frag = frag_by_id[frag_id]
        if not frag.get("sourceId") or not frag.get("locator"):
            failures.append(f"[P03] assertion {item.get('assertionId')}: broken backlink chain")
        if not span.get("quoteHash"):
            failures.append(f"[P03] assertion {item.get('assertionId')}: missing quoteHash")

    # --- 断链必须被拒（fail-closed：无触发夹具即视为断言空转）---
    dangling_path = FACTORY / "negative_fixtures" / "dangling_evidence_span.json"
    if not dangling_path.is_file():
        failures.append(f"[chain] dangling fixture missing: {dangling_path} (assertion would be noop)")
    else:
        ddoc = load(dangling_path)
        dangling_detected = False
        for item in ddoc.get("assertions", []):
            span = item.get("evidenceSpan") or {}
            if span.get("fragmentId") not in frag_by_id:
                dangling_detected = True
        if not dangling_detected:
            failures.append("[chain] dangling fixture NOT rejected by backlink check")

    # --- 可恢复 ingestion job ---
    for field in ("jobId", "steps", "resumable", "candidateSetRef"):
        if field not in job:
            failures.append(f"[job] missing field {field}")
    if job.get("resumable") is not True:
        failures.append("[job] ingestion job must be resumable")
    step_ids = [s.get("step") for s in job.get("steps", [])]
    for expected_step in ("P01", "P02", "P03", "P04", "P05", "P06"):
        if expected_step not in step_ids:
            failures.append(f"[job] missing pipeline step {expected_step}")

    # --- P01-P06 阻断条件必须全部被负例覆盖（fail-closed）---
    covered: set[str] = set()
    for path in negatives:
        doc = load(path)
        if not doc.get("expectedError"):
            failures.append(f"[neg] {path.name}: missing expectedError")
            continue
        covered.add(doc["expectedError"])
        if "stage" not in doc:
            failures.append(f"[neg] {path.name}: missing stage")
    for stage, required in BLOCKING_CONDITIONS.items():
        missing = required - covered
        if missing:
            failures.append(f"[{stage}] blocking conditions not covered by negatives: {sorted(missing)}")

    # --- P04 同名不得自动合并 ---
    for item in review.get("identityResolutions", []):
        if item.get("sameNameDifferentSubject") is True and item.get("autoMerged") is True:
            failures.append(f"[P04] identity {item.get('candidateId')}: auto-merged ambiguous subject")

    # --- P05 工具名不得自动注册为能力 ---
    for gap in review.get("capabilityGaps", []):
        if gap.get("mentionedInDocument") is True and gap.get("autoRegistered") is True:
            failures.append(f"[P05] capability {gap.get('name')}: auto-registered from document mention")

    # --- 候选隔离：候选不得标 published ---
    for item in assertions.get("assertions", []):
        if item.get("status") == "PUBLISHED":
            failures.append(f"[isolation] assertion {item.get('assertionId')}: candidate marked PUBLISHED")

    # --- P06 冲突必须登记且未关闭时阻断 ---
    open_conflicts = [c for c in review.get("conflicts", []) if c.get("status") == "OPEN"]
    if review.get("blockingConflicts") and not open_conflicts:
        failures.append("[P06] blockingConflicts declared but no OPEN conflict recorded")

    # --- simulationOnly 贯穿 ---
    for name, doc in (("fragments", fragments), ("assertions", assertions), ("review", review)):
        if doc.get("simulationOnly") is not True:
            failures.append(f"[flag] {name}: simulationOnly must be true")

    if failures:
        print("gk-ke-l3-1-factory-tests: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    print("gk-ke-l3-1-factory-tests: PASS")
    print(f"  documents_backlinked={len(doc_keys)}/{EXPECTED_DOC_COUNT} (unique sourceIds={len(by_source)})")
    print(f"  fragments={len(fragments.get('fragments', []))} assertions={len(assertions.get('assertions', []))}")
    print(f"  blocking_conditions_covered={len(covered)}")
    print(f"  pipeline_steps={step_ids}")
    print("  checks: backlink-chain, resumable-job, P01-P06 blocking, no-auto-merge, "
          "no-auto-capability, candidate-isolation, conflicts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
