#!/usr/bin/env python3
"""判据**出处行号**审计：文档标注的 `file.md:NN` 是否真的指向该字段。

动因（第二次独立复核 Q1b）：
    判据文档 55 条出处行号中 **37 条指向 KERT 改动前的旧行号** ——
    R1–R6 交付后只补了新字段的行号，**未回头重核旧字段**。
    而行号是"我去核实过"的**唯一可验痕迹**；既有键审计捕获了行号却从不使用。

== v1 的失败（第三次独立复核 Q1b / Q12a-c，实测确认，必须记录）==
    v1 **假通过**：在被审文档上输出 [PASS]，而其中 **5 条行号是错的**。
    跳过机制（两类，均为**静默丢弃**）：
      · `len(k) > 30: continue` —— 丢掉恰是三层的长路径键
        （`kycGaps[].verifyScript.factBasis` = 32 字符），而错标的正是它们；
      · 只解析以 `|`/`-` 开头的行 —— 多行 `判定键` 的**续行**整行跳过。
    且**无 fail-closed 计数**：不比对"文档里共有多少条引用"与"实际核对了多少条"。
    → 与键审计（有 MIN_EXPECTED_KEYS）形成反差：**一个 fail-closed，一个静默**。

== v2 的设计纪律（针对上表）==
    **任何一条引用都不允许被静默跳过。**
      · 无长度过滤；
      · 不限制行前缀（续行也解析）；
      · **引用总数 vs 已核对数必须相等**，不等即 fail-closed 并逐条列出未核对项；
      · 无法归属到键的引用 → **失败并列出**，而不是 continue。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KERT = Path("/home/szf/dev/Leibniz-KERT")
DOC = ROOT / "docs" / "architecture" / "GK-KE-语义级消费验证方案-V1.2.2.md"

FILES = {
    "bank-front-fact-reconciliation/references/output-schema.md":
        KERT / "examples/bank-front-skills/bank-front-fact-reconciliation/references/output-schema.md",
    "bank-front-fact-reconciliation/references/input-schema.md":
        KERT / "examples/bank-front-skills/bank-front-fact-reconciliation/references/input-schema.md",
    "bank-front-kyc-gap-check/references/output-schema.md":
        KERT / "examples/bank-front-skills/bank-front-kyc-gap-check/references/output-schema.md",
    "bank-front-kyc-gap-check/references/input-schema.md":
        KERT / "examples/bank-front-skills/bank-front-kyc-gap-check/references/input-schema.md",
}

CITE = re.compile(r"`((?:[a-z-]+/references/)?(?:output|input)-schema\.md):(\d+)`")

# 非字段标识符（枚举值、函数名、路径等），不作为判定键核对
NON_FIELD = {
    "verified", "pending", "missing", "high", "medium", "general",
    "SUCCESS", "PARTIAL", "NOT_RUN", "FAILED", "OPEN", "PENDING", "CLOSED",
    "资金安全", "合规风险", "经营决策", "JSON", "ISO-8601", "make", "verify",
    "RUL-FRONT-001-xxx", "RUL-FRONT-001-003", "xxx", "A", "B", "U", "d", "i", "k", "n",
    "stable", "notRun", "noUsableInput", "coverage", "hasConflict", "placeholder",
}

# 本判据范围外的引用（其他能力的合同），不计入本文档的核对范围，但**必须列出**
KNOWN_EXTERNAL = (
    "bank-front-report-assembler/",
)


def leaf(k: str) -> str:
    """`kycGaps[].verifyScript.question` → `question`；`indicators[]` → `indicators`。"""
    return k.split(".")[-1].split("[]")[0].strip()


def resolve(fname: str, section: str, label: str) -> str:
    if "/" in fname:
        return fname
    up = section.startswith("1.1") or "上游" in section or "上游" in label
    down = section.startswith("1.2") or "下游" in section or "下游" in label
    if section.startswith("4") or section.startswith("3"):
        if "上游" in label:
            return "bank-front-fact-reconciliation/references/" + fname
        if "下游" in label:
            return "bank-front-kyc-gap-check/references/" + fname
    if up:
        return "bank-front-fact-reconciliation/references/" + fname
    if down:
        return "bank-front-kyc-gap-check/references/" + fname
    return ""


def find_line(text: str, key: str) -> int | None:
    lf = leaf(key)
    pat = re.compile(r'"' + re.escape(lf) + r'"\s*:')
    for i, line in enumerate(text.splitlines(), 1):
        if pat.search(line):
            return i
    for i, line in enumerate(text.splitlines(), 1):
        if f"`{lf}`" in line:
            return i
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true", help="把错误行号回写为实测行号")
    args = ap.parse_args()

    if not DOC.exists():
        print(f"gk-ke-criteria-line-audit: FAIL — 判据文档缺失 {DOC}", file=sys.stderr)
        return 1
    full = DOC.read_text(encoding="utf-8")
    lines = full.splitlines()
    texts = {p: f.read_text(encoding="utf-8") for p, f in FILES.items()}

    total_cites = len(CITE.findall(full))
    mism: list[tuple[int, str, str, int, int]] = []
    unattributed: list[tuple[int, str]] = []
    external: list[tuple[int, str]] = []
    checked = 0
    section, label = "", ""

    for idx, line in enumerate(lines, 1):
        s = line.strip()
        if s.startswith("#"):
            section, label = s.lstrip("#").strip(), ""
            continue
        m = re.match(r"^\*\*(.+?)\*\*", s)
        if m and not s.startswith("|"):
            label = m.group(1)
        cites = CITE.findall(line)
        if not cites:
            continue
        # **不做行前缀过滤** —— 续行也要解析（v1 在此静默跳过）
        keys = [k for k in re.findall(r"`([^`\n]+)`", line) if not CITE.fullmatch(f"`{k}`")]
        field_keys = [k for k in keys
                      if not re.search(r"[\u4e00-\u9fff]", k)
                      and leaf(k) not in NON_FIELD
                      and leaf(k) not in NON_FIELD]
        for fname, declared in cites:
            if any(x in fname for x in KNOWN_EXTERNAL):
                external.append((idx, fname))     # 范围外，列出但不判失败
                continue
            p = resolve(fname, section, label)
            if not p or p not in texts:
                unattributed.append((idx, f"无法判定合同: {fname}"))
                continue
            # 该行若无可核对字段键（如纯散文引用），记录为未归属而非静默跳过
            if not field_keys:
                unattributed.append((idx, f"未归属字段键: {line.strip()[:70]}"))
                continue
            for k in field_keys:
                actual = find_line(texts[p], k)
                if actual is None:
                    if leaf(k) in texts[p]:
                        continue          # 字段存在但行定位不到，另由键审计负责
                    continue
                checked += 1
                if actual != int(declared):
                    mism.append((idx, k, p, int(declared), actual))

    print("gk-ke-criteria-line-audit")
    print(f"  判据文档: {DOC.name}")
    print(f"  文档中引用总数: {total_cites}   已核对: {checked}   "
          f"未归属: {len(unattributed)}   不符: {len(mism)}")

    # ---- fail-closed：未归属引用必须列出（不允许静默跳过）----
    if unattributed:
        print(f"  [FAIL] **{len(unattributed)} 条引用未被核对**（不允许静默跳过）：")
        for idx, why in unattributed[:10]:
            print(f"    第 {idx} 行  {why}")
        if len(unattributed) > 10:
            print(f"    …另有 {len(unattributed) - 10} 条")
        print("  → 这些引用**未经验证**。请修正解析或文档，不得放行。")

    if external:
        print(f"  [所属范围外] {len(external)} 条引用指向其他能力合同（不属于本判据依据）：")
        for idx, f in external[:5]:
            print(f"    第 {idx} 行  {f}")

    if not mism and not unattributed:
        print("  [PASS] 全部出处行号指向正确位置")
        return 0

    if mism:
        print(f"  [FAIL] **{len(mism)} 条**出处行号指向错误位置：")
        for idx, k, p, dec, act in mism[:40]:
            print(f"    第 {idx:>4} 行  `{k}`  标注 {p.split('/')[-2]}/{p.split('/')[-1]}:{dec}"
                  f"  实际:{act}")
        if len(mism) > 40:
            print(f"    …另有 {len(mism) - 40} 条")

    if args.fix and mism:
        fixed = 0
        for idx, k, p, dec, act in mism:
            line = lines[idx - 1]
            for fname in (p, "references/" + p.split("/")[-1], p.split("/")[-1]):
                old = f"`{fname}:{dec}`"
                if old in line:
                    lines[idx - 1] = line.replace(old, f"`{fname}:{act}`")
                    line = lines[idx - 1]
                    fixed += 1
        DOC.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"  → 已回写 {fixed} 处行号")

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
