#!/usr/bin/env python3
"""生成 GK-KE L3-1 工厂与候选夹具（C08 L3-1 / wave C2）。

依据 C03 §2 P01–P06。输入：封版 18 份文档（只读）。
产出：specs/knowledge-architecture/factory/{ingestion_job,fragments,candidate_assertions,
      review_package}.json + negatives/（P01–P06 阻断条件）
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "specs" / "knowledge-architecture" / "factory"
NEG = OUT / "negatives"
SEALED_DOCS = ROOT / "docs" / "dd" / "gk-ke-contract" / "simulation" / "documents"


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    NEG.mkdir(parents=True, exist_ok=True)

    if not SEALED_DOCS.is_dir():
        raise SystemExit(f"sealed documents missing: {SEALED_DOCS}")

    doc_files = sorted(SEALED_DOCS.glob("*.md"))
    if len(doc_files) != 18:
        raise SystemExit(f"expected 18 sealed documents, found {len(doc_files)}")

    fragments = []
    assertions = []
    for idx, path in enumerate(doc_files, start=1):
        # 文档名形如 SIM-DOC-P001_1.0.0.md → sourceId=SIM-DOC-P001, version=1.0.0
        stem = path.stem
        if "_" in stem:
            source_id, version = stem.rsplit("_", 1)
        else:
            source_id, version = stem, "1.0.0"

        text = path.read_text(encoding="utf-8")
        lines = [ln for ln in text.splitlines() if ln.strip()]
        # P02 解析：标题分段 → Fragment（含 locator 坐标与 parseVersion）
        for seg, heading in enumerate(lines[:3], start=1):
            fragment_id = f"FRAG-{source_id}-{seg}"
            fragments.append({
                "fragmentId": fragment_id,
                "sourceId": source_id,
                "sourceVersion": version,
                "locator": f"{path.name}#L{seg}",
                "parseVersion": "SIM-PARSE-1.0.0",
                "text": heading[:120],
                "headerIntact": True,
            })
            # P03 抽取：CandidateAssertion + EvidenceSpan（必须有原文支持）
            if seg == 1:
                assertions.append({
                    "assertionId": f"SIM-AS-{source_id}-1",
                    "subjectRef": source_id,
                    "predicate": "documentedAs",
                    "object": heading[:80],
                    "modality": "DOCUMENTED",
                    "unit": None,
                    "status": "CANDIDATE",
                    "evidenceSpan": {
                        "fragmentId": fragment_id,
                        "locator": f"{path.name}#L{seg}",
                        "quoteHash": sha256(path),
                    },
                })

    ingestion_job = {
        "simulationOnly": True,
        "jobId": "SIM-ING-JOB-001",
        "candidateSetRef": "SIM-CANDSET-001",
        "resumable": True,
        "inputDocs": [p.name for p in doc_files],
        "steps": [
            {"step": "P01", "name": "接入", "status": "DONE",
             "blockingConditions": ["SOURCE_UNVERIFIABLE", "PURPOSE_NOT_ALLOWED"]},
            {"step": "P02", "name": "解析", "status": "DONE",
             "blockingConditions": ["HEADER_LOST", "AMOUNT_EXTRACTION_UNRELIABLE"]},
            {"step": "P03", "name": "抽取", "status": "DONE",
             "blockingConditions": ["NO_SOURCE_SUPPORT", "UNIT_MISSING", "PREDICTION_AS_FACT"]},
            {"step": "P04", "name": "对齐", "status": "DONE",
             "blockingConditions": ["AMBIGUOUS_SUBJECT_NOT_AUTO_MERGED"]},
            {"step": "P05", "name": "组图", "status": "DONE",
             "blockingConditions": ["TOOL_NAME_NOT_AUTO_REGISTERED"]},
            {"step": "P06", "name": "质量/冲突", "status": "DONE",
             "blockingConditions": ["MANDATORY_RULE_GAP", "IDENTITY_UNKNOWN", "SOURCE_CONTRADICTION"]},
        ],
        "isolationRule": "已发布记录与候选/拒绝记录分目录；不让审核状态成为抽取模型的提示答案。",
    }

    review_package = {
        "simulationOnly": True,
        "packageId": "SIM-REVIEWPKG-001",
        "candidateSetRef": "SIM-CANDSET-001",
        "identityResolutions": [
            # P04 同名异主体：必须不自动合并
            {"candidateId": "SIM-IDR-001", "name": "同名不同主体样例",
             "sameNameDifferentSubject": True, "autoMerged": False,
             "resolution": "MANUAL_REVIEW_REQUIRED"},
            {"candidateId": "SIM-IDR-002", "name": "唯一主体样例",
             "sameNameDifferentSubject": False, "autoMerged": True,
             "resolution": "AUTO_RESOLVED"},
        ],
        "capabilityGaps": [
            # P05 文档提及工具≠已注册能力
            {"name": "SIM-TOOL-MENTIONED-IN-DOC", "mentionedInDocument": True,
             "autoRegistered": False, "gapStatus": "NOT_REGISTERED_REQUIRES_EVIDENCE"},
        ],
        "conflicts": [],
        "blockingConflicts": False,
        "mandatoryRuleGap": False,
    }

    (OUT / "ingestion_job.json").write_text(json.dumps(ingestion_job, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "fragments.json").write_text(json.dumps({"simulationOnly": True, "fragments": fragments}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "candidate_assertions.json").write_text(json.dumps({"simulationOnly": True, "assertions": assertions}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "review_package.json").write_text(json.dumps(review_package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    # 负例：P01–P06 全部必需阻断条件
    negatives = []
    for stage, codes in (
        ("P01", ["SOURCE_UNVERIFIABLE", "PURPOSE_NOT_ALLOWED"]),
        ("P02", ["HEADER_LOST", "AMOUNT_EXTRACTION_UNRELIABLE"]),
        ("P03", ["NO_SOURCE_SUPPORT", "UNIT_MISSING", "PREDICTION_AS_FACT"]),
        ("P04", ["AMBIGUOUS_SUBJECT_NOT_AUTO_MERGED"]),
        ("P05", ["TOOL_NAME_NOT_AUTO_REGISTERED"]),
        ("P06", ["MANDATORY_RULE_GAP", "IDENTITY_UNKNOWN", "SOURCE_CONTRADICTION"]),
    ):
        for code in codes:
            negatives.append((f"{stage.lower()}_{code.lower()}", stage, code))

    # 额外：注入 / 时态 负例（C08 L3-1 明确要求保留）
    negatives.append(("injection_attempt", "P03", "INJECTION_DETECTED"))
    negatives.append(("temporal_conflict", "P06", "SOURCE_CONTRADICTION"))

    for name, stage, code in negatives:
        (NEG / f"{name}.json").write_text(json.dumps({
            "expectedError": code, "stage": stage, "case": name,
            "simulationOnly": True, "source": "C03 section 2 P01-P06",
            "mustNotPolluteNormalSnapshot": True,
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("L3-1 factory generated")
    print(f"  documents={len(doc_files)} fragments={len(fragments)} assertions={len(assertions)}")
    print(f"  negatives={len(negatives)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
