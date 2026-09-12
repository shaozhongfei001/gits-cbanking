#!/usr/bin/env python3
"""判据键审计：验证判据所依赖的每一个判定键**真实存在于合同中**。

动因（独立判定执行者 V1.1.0 判定 §7.1 —— 最严重项）：
    V1.1.0 的五条判据中，**三条的判定键在真实合同里不存在**
    （`evaluationStatus` / `reconciliationStatus` / `comparedMetricRefs` /
     `requiredQuestions` / `conflictId` / `conflicts[].id` / `COVERAGE_*` /
     `HYPOTHESIS` —— 全库 grep 命中 0）。
    后果：观测实际测的是"下游对**合同外**输入的处理"，不能代表合同闭合后的行为。

本脚本的定位：**把"判定键是否存在"这件事机械化**。
    7.1 的根因不是"我写错了字段名"，而是**没有任何机制检查我写的字段名是否存在**。

== 设计纪律（v1 教训，必须遵守）==
  **判据文档是唯一真源。** 本脚本**不持有**自己的键清单副本 ——
  v1 曾把白名单硬编码在脚本里，导致"往文档里加一个不存在的键，审计查不出来"。
  那是"检查器检查自己"，与本脚本要防的缺陷同源。
  现改为**从判据文档 §1 的表格解析键与出处引用**，再逐键回真实合同核对。

  **零命中即失败。** v1 的解析若因文档改版而解析不到任何键，会**静默通过**。
  故本脚本要求解析到的键数 ≥ MIN_EXPECTED_KEYS，否则 fail-closed。

退出码：不通过即非零（fail-closed）。纳入 `make verify`。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KERT = Path("/home/szf/dev/Leibniz-KERT")

CRITERIA_DOC = ROOT / "docs" / "architecture" / "GK-KE-语义级消费验证方案-V1.2.1.md"

KERT_SKILLS = KERT / "examples" / "bank-front-skills"
CONTRACTS = {
    "up_out": KERT_SKILLS / "bank-front-fact-reconciliation/references/output-schema.md",
    "up_in": KERT_SKILLS / "bank-front-fact-reconciliation/references/input-schema.md",
    "down_in": KERT_SKILLS / "bank-front-kyc-gap-check/references/input-schema.md",
    "down_out": KERT_SKILLS / "bank-front-kyc-gap-check/references/output-schema.md",
}
# 出处引用中的文件名 → 合同键（用于按"判据自称的出处"核对，而非按脚本猜测）
BY_FILENAME = {
    "output-schema.md": ("up_out", "down_out"),   # 需结合小节判定
    "input-schema.md": ("up_in", "down_in"),
}
# 判据文档小节 → 合同键
SECTION_TO_CONTRACT = {
    "1.1": "up_out",
    "1.2.input": "down_in",
    "1.2.output": "down_out",
}

# 明确登记为**不存在**的标识符：若被判据当作判定键使用，直接失败（防回归）
FORBIDDEN = [
    "evaluationStatus", "reconciliationStatus", "comparedMetricRefs", "requiredQuestions",
    "conflictId", "COVERAGE_INSUFFICIENT", "COVERAGE_NOT_REPORTED", "VERIFY_REQUIRED",
    "HYPOTHESIS", "entityId",
    "conflictCases", "ruleCoverage", "explanations",
]

# 非判定键的合法标识符（枚举值、派生函数名、技能 id、判据键名等）。
# 判据正文引用它们不算"未登记键"。
NON_KEY_EXTRA = {
    "verified", "pending", "missing", "high", "medium", "general",
    "资金安全", "合规风险", "经营决策", "FULL", "PARTIAL", "NONE",
    "coverage", "notRun", "noUsableInput", "stable", "hasConflict", "placeholder",
    "JSON", "ISO-8601", "SK-FRONT-004", "SK-FRONT-006",
    "PASS", "FAIL", "INCONCLUSIVE", "NOT_MET",
    "SUCCESS", "PARTIAL", "NOT_RUN", "FAILED", "OPEN", "CLOSED",  # 合同枚举值
    "RUL-FRONT-001-xxx", "RUL-FRONT-001-003", "KG-001", "HZB0000001234",
    "limitations", "A", "B", "U", "d", "i", "k", "n",
    "S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8",
    "xxx", "U_A", "U_B", "COVERAGE_*", "S1–S5",
    "S1_CONFLICT_PROPAGATION", "S2_EMPTY_MEANS_NONE", "S3_NOT_RUN_NOT_NONE",
    "S4_HYPOTHESIS_NOT_CLOSED", "S5_REPRODUCIBLE",
    "executionId",       # 已登记为"合同中不存在、故从允许集合删除"，非判定键
    "upstreamCoverage",  # 实施时改名为 upstreamStatus；旧名仅存于变更说明
}

# 解析下限：低于此数说明解析失效（文档改版），必须 fail-closed 而非静默通过
MIN_EXPECTED_KEYS = 30

# **待 KERT 交付的键**（我方已提出请求，字段尚不存在）。
# 语义：判据**可以**引用它们，但**必须**在同一行标注"待 KERT"；
# 否则视为"假定存在"—— 那正是 V1.1.0 的 7.1 缺陷。
# 交付后应把它们移入合同并从此表删除（届时 L1 会核对合同）。
PENDING_KEYS: dict[str, str] = {}
# 全部请求项（R1/R1b/R2/R3/R4/R5/R6）已于 2026-09-13 由 KERT 侧交付并折入 §1 白名单，
# 故本表清空 —— 此后这些键由 L1 直接核对真实合同（不再有"待交付"豁免）。


CITE_RE = re.compile(
    r"`((?:bank-front-[a-z-]+/references/)?(output-schema|input-schema)\.md):(\d+)`")


def _contract_for(citation: str, section: str, label: str) -> str:
    """由出处引用判定合同；引用不含路径时回退小节映射。"""
    if "fact-reconciliation" in citation:
        return "up_in" if "input-schema" in citation else "up_out"
    if "kyc-gap-check" in citation:
        return "down_in" if "input-schema" in citation else "down_out"
    sec_no = section.split()[0] if section else ""
    if sec_no.startswith("1.1"):
        return "up_out"
    if sec_no.startswith("1.2"):
        k = "1.2.input" if "输入" in label else ("1.2.output" if "输出" in label else "")
        return SECTION_TO_CONTRACT.get(k, "")
    return ""


def bullets_with_citations(doc: str) -> list[tuple[str, str, int]]:
    """从 **bullet 判定键行**解析 (合同, 键, 行号)。

    动因（第二次独立复核 Q2/Q8，实测确认）：
        §4 的出处引用写在 `- **判定键**：…（上游 `path:NN`）` 这类 **bullet 行**里，
        而 v3 的 `tables_with_citations` **只遍历表格行** →
        **§4 的键完全不在审计范围内**。
        作者曾声称"已为 §4 补齐引用使其纳入审计"，**实际未生效** ——
        引用的**承载位置**不对，补了等于没补。
    """
    out: list[tuple[str, str, int]] = []
    section = ""
    label = ""
    for idx, line in enumerate(doc.splitlines(), 1):
        s = line.strip()
        if s.startswith("#"):
            section = s.lstrip("#").strip()
            label = ""
            continue
        m = re.match(r"^\*\*(.+?)\*\*", s)
        if m and not s.startswith("|"):
            label = m.group(1)
            continue
        if s.startswith("|") or not s:
            continue
        if "判定键" not in s:
            continue
        cites = CITE_RE.findall(s)
        if not cites:
            continue
        contracts = {_contract_for(f"{c[0]}.md", section, label) for c in cites}
        contracts.discard("")
        if not contracts:
            continue
        # 该行所有反引号标识符中，形如字段名的作为候选键
        for ident in re.findall(r"`([^`\n]+)`", s):
            if CITE_RE.fullmatch(f"`{ident}`"):
                continue
            if re.search(r"[\u4e00-\u9fff]", ident) or len(ident) > 30:
                continue
            if ident in NON_KEY_EXTRA:
                continue
            for c in sorted(contracts):
                out.append((c, ident, idx))
    return out


def tables_with_citations(doc: str) -> list[tuple[str, str, int]]:
    """从判据文档解析 (小节, 键, 行号)。仅取**含出处引用**的表格行。

    形状：``| `key` | type | enum | `file.md:12` |``
    小节上下文决定该引用属于哪个合同（上/下游 × 输入/输出）。
    """
    out: list[tuple[str, str, int]] = []
    section = ""
    label = ""
    for idx, line in enumerate(doc.splitlines(), 1):
        s = line.strip()
        if s.startswith("###"):
            section = s.lstrip("#").strip()
            label = ""
            continue
        if s.startswith("##"):
            section = s.lstrip("#").strip()
            label = ""
            continue
        # 小节内的粗体标签，如 **输入合同** / **输出合同**
        m = re.match(r"^\*\*(.+?)\*\*", s)
        if m and not s.startswith("|"):
            label = m.group(1)
            continue
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 4:
            continue
        cite = cells[-1]
        cm = re.search(r"`?(output-schema\.md|input-schema\.md):(\d+)`?", cite)
        if not cm:
            continue  # 无出处引用 → 非白名单行（如"本版处置"表）
        keys = re.findall(r"`([^`]+)`", cells[0])
        if not keys:
            continue
        # 合同判定：**优先用引用里的路径**（§4 用全路径），否则回退小节映射（§1 用裸文件名）。
        # v3 变更：V1.2.0 只按小节映射，导致 §4 的键（无逐行引用）**完全不在审计范围** ——
        # 复核 3.2 指出 §6.1 声称的机械化防线对 S6'–S8' 实际失效。现 V1.2.1 的 §4 已补齐
        # 全路径引用，故按路径即可判定合同，使 §4 纳入覆盖。
        contract = ""
        if "fact-reconciliation" in cite:
            contract = "up_in" if "input-schema" in cm.group(1) else "up_out"
        elif "kyc-gap-check" in cite:
            contract = "down_in" if "input-schema" in cm.group(1) else "down_out"
        else:
            sec_no = section.split()[0] if section else ""
            if sec_no.startswith("1.1"):
                contract = "up_out"
            elif sec_no.startswith("1.2"):
                k = "1.2.input" if "输入" in label else (
                    "1.2.output" if "输出" in label else "")
                contract = SECTION_TO_CONTRACT.get(k, "")
        if not contract:
            continue
        out.append((contract, keys[0], idx))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--allow-missing-kert", action="store_true",
                    help="KERT 仓不可用时跳过（CI 无跨仓环境）；本地禁止")
    args = ap.parse_args()

    if not KERT.exists():
        msg = f"KERT 仓不存在：{KERT}"
        if args.allow_missing_kert:
            print(f"gk-ke-criteria-key-audit: SKIP — {msg}")
            return 0
        print(f"gk-ke-criteria-key-audit: FAIL — {msg}", file=sys.stderr)
        return 1

    if not CRITERIA_DOC.exists():
        print(f"gk-ke-criteria-key-audit: FAIL — 判据文档缺失：{CRITERIA_DOC}",
              file=sys.stderr)
        return 1
    body = CRITERIA_DOC.read_text(encoding="utf-8")

    texts: dict[str, str] = {}
    for k, p in CONTRACTS.items():
        if not p.exists():
            print(f"gk-ke-criteria-key-audit: FAIL — 合同文件缺失：{p}", file=sys.stderr)
            return 1
        texts[k] = p.read_text(encoding="utf-8")

    failures: list[str] = []
    warnings: list[str] = []

    # --- L0：解析必须有效（零命中即失败，防止"解析失效 → 静默通过"）---
    # 两条解析路径：表格行（§1）+ bullet 判定键行（§4）。
    # 后者是第二次复核 Q2/Q8 指出的缺口 —— §4 的引用不在表格里。
    declared = tables_with_citations(body) + bullets_with_citations(body)
    n_table = len(tables_with_citations(body))
    n_bullet = len(bullets_with_citations(body))
    if n_bullet == 0:
        print("gk-ke-criteria-key-audit: FAIL — bullet 判定键行解析为 0。", file=sys.stderr)
        print("  §4 等节的引用写在 bullet 行里；解析不到即意味着**该部分不受审计覆盖**"
              "（这正是第二次复核指出的缺口）。fail-closed，不静默通过。", file=sys.stderr)
        return 1
    if len(declared) < MIN_EXPECTED_KEYS:
        print(f"gk-ke-criteria-key-audit: FAIL — 仅从判据文档解析到 "
              f"{len(declared)} 个判定键，低于下限 {MIN_EXPECTED_KEYS}。",
              file=sys.stderr)
        print("  这通常意味着**解析失效**（文档改版）或**白名单被删减**。"
              "两种情况都必须 fail-closed，不得静默通过。", file=sys.stderr)
        return 1

    # --- L1/L2：文档声明的每个键，回真实合同核对 ---
    seen: set[tuple[str, str]] = set()
    n_code = 0
    for contract, key, lineno in declared:
        if (contract, key) in seen:
            continue
        seen.add((contract, key))
        text = texts[contract]
        leaf = key.split(".")[-1].split("[]")[0].strip()
        if leaf not in text:
            failures.append(f"L1 判据文档:${lineno} 声明 `{key}`，但合同 "
                            f"{CONTRACTS[contract].name} 中**不存在**")
            continue
        blocks = "\n".join(re.findall(r"```[^\n]*\n(.*?)```", text, re.S))
        if leaf in blocks:
            n_code += 1
        else:
            warnings.append(f"L2 判据文档:${lineno} `{key}` 仅出现在 "
                            f"{CONTRACTS[contract].name} 正文、不在代码块内")

    # --- L3：正文反引号标识符须在白名单/已知非键集合内 ---
    allowed_leaves = {k.split(".")[-1].split("[]")[0].strip()
                      for _, k, _ in declared} | NON_KEY_EXTRA | set(FORBIDDEN)
    unknown: list[str] = []
    for ident in sorted(set(re.findall(r"`([^`\n]{1,60})`", body))):
        leaf = ident.split(".")[-1].split("[]")[0].strip()
        if ident in allowed_leaves or leaf in allowed_leaves:
            continue
        if any(c in ident for c in "/\\-（）()：: →=") or len(ident) > 28:
            continue
        if re.search(r"[\u4e00-\u9fff]", ident):
            continue
        unknown.append(ident)
    if unknown:
        warnings.append("L3 正文反引号标识符不在白名单内（请确认非判定键）："
                        + ", ".join(f"`{u}`" for u in unknown))

    # --- L4：禁用标识符不得出现在**判定键声明位** ---
    #
    # v2 教训：v1 用"上下文窗口"判断是否"被当作判定键使用"，
    # 但**邻近的无关散文即可击败它** ——
    # 实测：某条判据的 `判定键` 行上方两行恰好有无关的"不存在"二字，
    # 该行即被误判为"合规"，注入 `evaluationStatus` 后审计**未报错**。
    # → 启发式上下文匹配本身就是脆弱的（与 S3 的"文本启发式"同类错误）。
    #
    # 现改为**精确定位声明位**，不做模糊匹配：
    #   (a) 含"判定键"的行
    #   (b) 含"判据"且含"："的行（判据定义句）
    #   (c) §1 白名单表格行（已由 tables_with_citations 解析，
    #       若解析出的键本身在 FORBIDDEN 中，亦在此拦截）
    # 声明位 = "判定键/判据" 后**紧跟冒号**（键列表形态），而非名词提及。
    # v3 教训：v2 用 `判定键` 裸词匹配，导致"§0.1 缺陷描述表"里
    # 「**§1 全部判定键重新取自真实合同**」这一**名词提及**被误判为声明位。
    DECL_PATTERNS = (
        re.compile(r"判定键\s*\**\s*[：:]"),      # - **判定键**：`a` / `b`
        re.compile(r"\*\*判据\*\*\s*[（(][^）)]*[）)]\s*[：:]"),  # **判据**（合取）：
        re.compile(r"\*\*判据\*\*\s*[：:]"),
    )
    lines = body.splitlines()
    pending_seen: set[str] = set()
    for f in FORBIDDEN:
        for idx, line in enumerate(lines, 1):
            if f"`{f}`" not in line:
                continue
            if not any(p.search(line) for p in DECL_PATTERNS):
                continue
            # 待 KERT 的键：允许引用，但**必须**同行标注"待 KERT"。
            # 区分"我们已请求该字段"与"我们假定它存在" —— 后者正是 7.1 缺陷。
            if f in PENDING_KEYS:
                if "待 KERT" in line or "待KERT" in line:
                    pending_seen.add(f)
                    continue
                failures.append(
                    f"L4 判据文档:${idx} `{f}` 属**待 KERT**的键（{PENDING_KEYS[f]}），"
                    "但声明行**未标注「待 KERT」** —— 会被读作假定其存在")
                continue
            failures.append(
                f"L4 判据文档:${idx} 禁用标识符 `{f}` 出现在**判定键/判据声明位**"
                "（该键在真实合同中不存在）")
    if pending_seen:
        warnings.append(
            "L4 下列判定键**待 KERT 交付**，当前尚不存在，已按「待 KERT」正确标注："
            + ", ".join(f"`{p}`（{PENDING_KEYS[p]}）" for p in sorted(pending_seen)))
    # (c) 白名单表里若解析出禁用键
    for contract, key, lineno in declared:
        leaf = key.split(".")[-1].split("[]")[0].strip()
        if leaf in FORBIDDEN or key in FORBIDDEN:
            failures.append(f"L4 判据文档:${lineno} §1 白名单声明了禁用标识符 `{key}`")

    # --- L5：判定键声明位用到的键**必须已在 §1 白名单登记** ---
    #
    # 关闭"用了但没登记"的缺口：仅靠 L3 告警不够 ——
    # 告警不会阻断，而"判据用了未登记的键"正是 7.1 缺陷的温床。
    declared_leaves = {k.split(".")[-1].split("[]")[0].strip() for _, k, _ in declared}
    declared_full = {k for _, k, _ in declared}
    for idx, line in enumerate(lines, 1):
        if not any(p.search(line) for p in DECL_PATTERNS):
            continue
        for ident in re.findall(r"`([^`]+)`", line):
            leaf = ident.split(".")[-1].split("[]")[0].strip()
            if (ident in declared_full or leaf in declared_leaves
                    or ident in NON_KEY_EXTRA or leaf in NON_KEY_EXTRA
                    or ident in FORBIDDEN):
                continue
            if re.search(r"[\u4e00-\u9fff]", ident) or any(
                    c in ident for c in "/\\：: →=") or len(ident) > 28:
                continue
            failures.append(
                f"L5 判据文档:${idx} 判定键声明位使用了 `{ident}`，"
                "但它**未在 §1 白名单登记**（须先登记并核对合同）")

    # --- 报告 ---
    print("gk-ke-criteria-key-audit")
    print(f"  判据文档（唯一真源）: {CRITERIA_DOC.name}")
    print(f"  解析到判定键: {len(seen)}（表格行 {n_table} + bullet 判定键行 {n_bullet}，"
          f"共 {len(declared)}；代码块内取证 {n_code}）  合同文件: {len(CONTRACTS)}")
    for w in warnings:
        print(f"  [WARN] {w}")
    if failures:
        print()
        for f in failures:
            print(f"  [FAIL] {f}", file=sys.stderr)
        print(f"\ngk-ke-criteria-key-audit: FAIL ({len(failures)} 项) — "
              "判据中存在合同不支持的判定键；不得预注册。", file=sys.stderr)
        return 1
    print(f"  [PASS] 判据声明的 {len(seen)} 个判定键**全部**在真实合同中存在"
          f"（{len(warnings)} 项告警）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
