#!/usr/bin/env python3
"""GK-KE 合同覆盖完整性核对。

【目的】
主动发现"建议书要求了、但我方合同没覆盖"的遗漏 ——
不等 QA 指出。本轮此前已有多次"漏项由 QA 发现"的记录。

【核对对象】
  建议书 §9.3（能力间结果合同）   ← 权威要求
    ↕
  specs/.../contracts/CapabilityResultEnvelope.json  ← 我方结果包合同
  specs/.../contracts/ConsumerObligations.json        ← 我方消费义务合同

【核对维度】
  A. 建议书 §9.3 的 7 行消费表 → 是否每条都有对应义务
  B. 我方每条义务 → 是否都能追溯到建议书（防自造要求）
  C. 建议书列举的结果包字段 → 是否都在 Envelope 中登记
  D. 字段命名差异 → 是否已记录（防止"名字不同实为同一物"被误判为缺失）

用法：
  python3 scripts/gk_ke_contract_coverage.py
  python3 scripts/gk_ke_contract_coverage.py --json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = (ROOT / "docs" / "architecture"
            / "GITS-KERT_对公访前准备与知识工程完整解决方案建议书_V2.0.md")
ENVELOPE = (ROOT / "specs" / "knowledge-architecture" / "contracts"
            / "CapabilityResultEnvelope.json")
OBLIGATIONS = (ROOT / "specs" / "knowledge-architecture" / "contracts"
               / "ConsumerObligations.json")

# 建议书 §9.3 消费表的 7 行（原文顺序）
# 每行：上游字段（建议书原文写法）/ 下游用途关键字 / 异常行为关键字
PROPOSAL_ROWS = [
    ("taskId / entityId / asOf", "同一次任务", "拒绝消费"),
    ("evaluationStatus", "已做、失败或未执行", "不能当无冲突"),
    ("evaluatedRuleIds", "哪些规则实际覆盖", "返回覆盖不足"),
    ("conflictCases / signals", "需要核实的问题", "未发现"),
    ("comparedMetricRefs", "可比口径", "不能引用该结论"),
    ("evidenceRefs / explanations", "核实依据", "保留为假设"),
    ("requiredQuestions", "必须询问", "不得无理由删除"),
]

# 建议书 §9.3 列举的结果包字段（原文）
PROPOSAL_ENVELOPE_FIELDS = [
    "taskId", "entityId", "purpose", "asOf", "capabilityId", "version",
    "inputDigest", "status", "result", "evidenceRefs", "limitations",
    "ruleTrace", "providerVersion", "executionId",
]

# 已知命名差异：建议书写法 → 我方合同写法（须显式登记，不得视为缺失）
KNOWN_RENAMES = {
    "evaluationStatus": "status",
    "evaluatedRuleIds": "ruleTrace.expectedRules/coveredRules",
    "capabilityId/version": "capabilityId + capabilityVersion",
}


def extract_proposal_rows() -> list[tuple[str, str, str]]:
    """从建议书原文抽取 §9.3 表格，用于与常量互校（防止常量偷改）。"""
    if not PROPOSAL.is_file():
        return []
    text = PROPOSAL.read_text(encoding="utf-8")
    m = re.search(r"### 9\.3[\s\S]*?\| 上游字段 \| 下游用途 \| 缺失或异常时的行为 \|"
                  r"\n\|---\|---\|---\|\n([\s\S]*?)\n\n", text)
    if not m:
        return []
    rows = []
    for line in m.group(1).splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 3:
            rows.append(tuple(cells))
    return rows


def norm(s: str) -> str:
    return re.sub(r"[\s`/、，,]", "", s or "")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    failures: list[str] = []
    notes: list[dict] = []

    if not PROPOSAL.is_file():
        print(f"gk-ke-contract-coverage: FAIL — 建议书缺失 {PROPOSAL}",
              file=sys.stderr)
        return 1

    # ---- 0. 常量与原文互校（防止常量被改而原文未变）----
    live_rows = extract_proposal_rows()
    if live_rows:
        if len(live_rows) != len(PROPOSAL_ROWS):
            failures.append(
                f"§9.3 表行数不符：原文 {len(live_rows)} 行 vs 常量 "
                f"{len(PROPOSAL_ROWS)} 行")
        else:
            for i, (live, const) in enumerate(zip(live_rows, PROPOSAL_ROWS)):
                if norm(live[0]) != norm(const[0]):
                    failures.append(
                        f"§9.3 第 {i+1} 行上游字段不符：原文 {live[0]!r} vs "
                        f"常量 {const[0]!r}")
        notes.append({"check": "proposal_table_crosscheck", "rows": len(live_rows)})
    else:
        failures.append("无法从建议书抽取 §9.3 表格（正则未匹配），"
                        "常量无法与原文互校")

    envelope = json.loads(ENVELOPE.read_text(encoding="utf-8")) \
        if ENVELOPE.is_file() else {}
    obligations = json.loads(OBLIGATIONS.read_text(encoding="utf-8")) \
        if OBLIGATIONS.is_file() else {}
    if not envelope:
        failures.append("CapabilityResultEnvelope.json 缺失或为空")
    if not obligations:
        failures.append("ConsumerObligations.json 缺失或为空")

    env_fields = {f["name"] for f in envelope.get("fields", [])}
    obl_list = obligations.get("obligations", [])

    # 已登记的命名差异：建议书用词 → 我方用词。
    # 匹配时必须使用该映射，否则同一概念的两套写法会被误判为"缺失"。
    declared_map = (envelope.get("namingDivergences") or {}).get("map") or {}
    alias: dict[str, list[str]] = {}
    for prop_name, info in declared_map.items():
        ours = (info or {}).get("oursName") or ""
        tokens = [t.strip() for t in re.split(r"[+/]", ours) if t.strip()]
        alias[norm(prop_name)] = [norm(t.split(".")[-1]) for t in tokens]

    def expand(prop_field: str) -> list[str]:
        """把建议书字段名展开为其自身 + 已登记的我方别名。"""
        base = norm(prop_field)
        out = [base]
        out += alias.get(base, [])
        return out

    # ---- A. 建议书每行 → 是否有对应义务 ----
    coverage_a = []
    for row in PROPOSAL_ROWS:
        upstream = row[0]
        wanted: list[str] = []
        for t in upstream.split("/"):
            wanted += expand(t.strip())
        hit = None
        for obl in obl_list:
            fields = [norm(f.split(".")[-1]) for f in obl.get("upstreamFields", [])]
            if any(w and (w in fields or any(w in f for f in fields))
                   for w in wanted):
                hit = obl.get("id")
                break
        coverage_a.append({"proposalRow": upstream,
                           "matchedTokens": sorted(set(wanted)),
                           "coveredBy": hit})
        if hit is None:
            failures.append(f"建议书 §9.3 行 {upstream!r} **无对应消费义务**"
                            f"（已考虑登记别名 {sorted(set(wanted))}）")
    notes.append({"check": "A_proposal_to_obligation", "detail": coverage_a})

    # ---- B. 我方义务 → 是否可追溯到建议书（防自造要求）----
    proposal_field_tokens: set[str] = set()
    for row in PROPOSAL_ROWS:
        for t in row[0].split("/"):
            proposal_field_tokens.update(expand(t.strip()))
    # 已登记为我方别名者也视为可追溯
    for ours_tokens in alias.values():
        proposal_field_tokens.update(ours_tokens)

    coverage_b = []
    for obl in obl_list:
        fields = [norm(f.split(".")[-1]) for f in obl.get("upstreamFields", [])]
        traced = any(any(tok and (tok in f or f in tok)
                         for tok in proposal_field_tokens)
                     for f in fields)
        coverage_b.append({"obligationId": obl.get("id"),
                           "upstreamFields": obl.get("upstreamFields"),
                           "traceableToProposal": traced,
                           "sourceRow": obl.get("sourceRow")})
        if not traced and not obl.get("additionalObligation"):
            failures.append(
                f"义务 {obl.get('id')} 无法追溯到建议书 §9.3，"
                "且未标注为附加义务（防自造要求）")
    notes.append({"check": "B_obligation_to_proposal", "detail": coverage_b})

    # ---- C. 建议书结果包字段 → 是否都在 Envelope ----
    coverage_c = []
    for f in PROPOSAL_ENVELOPE_FIELDS:
        present = f in env_fields
        if not present and f == "version":
            present = "capabilityVersion" in env_fields
        coverage_c.append({"proposalField": f, "present": present})
        if not present:
            failures.append(f"建议书 §9.3 字段 {f!r} 未在 Envelope 中登记")
    notes.append({"check": "C_envelope_field_coverage", "detail": coverage_c})

    # ---- D. 命名差异是否已登记 ----
    # 修正（第三轮 QA 指出，属实）：
    # 原先 D 维遍历**脚本内硬编码**的 KNOWN_RENAMES（仅 2–3 项），
    # 而合同实际登记了 5 处 —— 于是"删掉第 4、5 处登记"仍报 3/3 PASS，
    # 使该维度形同虚设。现改为**遍历合同已登记的全部条目**，
    # 并对合同未登记的"疑似差异"（由 §9.3 原文与 Envelope 字段名比对发现）报 FAIL。
    renames_declared = (envelope.get("namingDivergences") or {}).get("map") or {}
    coverage_d = []
    for prop_name, info in sorted(renames_declared.items()):
        ours = (info or {}).get("oursName", "")
        # 逐条校验：登记项必须结构完整（有 oursName 且语义标注为一致）
        structural_ok = bool(ours) and (info or {}).get("semanticsIdentical") is not None
        coverage_d.append({"proposalName": prop_name, "oursName": ours,
                           "declared": True, "structuralOk": structural_ok})
        if not structural_ok:
            failures.append(
                f"命名差异登记 {prop_name!r} 结构不完整"
                "（须含 oursName 与 semanticsIdentical）")

    # 反向检查：§9.3 原文用词若同时**未**出现在 Envelope 字段名中，
    # 也**未**被登记为差异，则该概念**处于悬空状态** —— 必须登记。
    # 这一步使"漏登记第 N 处"能被发现，而非只校验已知条目。
    env_names = {f["name"] for f in envelope.get("fields", [])}
    for row in PROPOSAL_ROWS:
        for tok in row[0].split("/"):
            tok = tok.strip()
            if not tok:
                continue
            norm_tok = norm(tok)
            if tok in env_names:
                continue                      # 名字一致，无需登记
            if norm_tok in alias:             # 已登记别名
                continue
            # 允许下沉到 result 层（如 conflictCases → result.conflictCases）
            if any(norm_tok == norm(t.split(".")[-1]) for t in env_names):
                continue
            failures.append(
                f"§9.3 用词 {tok!r} 既不在 Envelope 字段名中，"
                "也未被登记为命名差异 —— 概念处于悬空状态，必须显式登记")

    notes.append({"check": "D_naming_divergence",
                  "declaredCount": len(renames_declared),
                  "detail": coverage_d})

    summary = {
        "proposalRows": len(PROPOSAL_ROWS),
        "obligationsInContract": len(obl_list),
        "envelopeFields": len(env_fields),
        "coverageA": sum(1 for c in coverage_a if c["coveredBy"]),
        "coverageB": sum(1 for c in coverage_b if c["traceableToProposal"]),
        "coverageC": sum(1 for c in coverage_c if c["present"]),
        "coverageD": sum(1 for c in coverage_d if c["declared"]),
        "declaredDivergences": len(renames_declared),
        "failures": len(failures),
    }

    if args.json:
        print(json.dumps({"summary": summary, "failures": failures,
                          "notes": notes}, ensure_ascii=False, indent=2))
    else:
        print("gk-ke-contract-coverage: "
              + ("PASS" if not failures else "FAIL"))
        print(f"  §9.3 消费表行数:        {summary['proposalRows']}")
        print(f"  我方消费义务数:          {summary['obligationsInContract']}")
        print(f"  A 建议书行→有义务:       {summary['coverageA']}/{summary['proposalRows']}")
        print(f"  B 义务→可追溯建议书:     {summary['coverageB']}/{summary['obligationsInContract']}")
        print(f"  C 结果包字段覆盖:        {summary['coverageC']}/{len(PROPOSAL_ENVELOPE_FIELDS)}")
        print(f"  D 命名差异已登记:        {summary['coverageD']} 条（遍历合同全部登记项，非硬编码清单）")
        for f in failures:
            print(f"  - {f}")

    if failures:
        if not args.json:
            print("\ngk-ke-contract-coverage: FAIL — 存在未覆盖面", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
