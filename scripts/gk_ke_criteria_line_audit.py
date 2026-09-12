#!/usr/bin/env python3
"""判据**出处行号**审计：文档标注的 `file.md:NN` 是否真的指向该字段。

动因（第二次独立复核 Q1b / Q8-b，实测可复现）：
    判据文档 55 条出处行号中，**大量指向 KERT 改动前的旧行号** ——
    R1–R6 交付后只补了新字段的行号，**未回头重核旧字段**。
    而行号是"我去核实过"的**唯一可验痕迹**。
    更糟：既有审计脚本 `CITE_RE` **捕获了行号但从未使用** ——
    等于把该痕迹保留为**不可验证的装饰**。

本脚本把该痕迹变成可验证的：
    · 取出每个键的标注出处（文件 + 行号）
    · 到合同文件里读**该行**，检查是否真的含该字段
    · 报告不匹配（并给出正确行号，可 `--fix` 回写）

退出码：不匹配即非零（fail-closed）。
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
SHORT = {
    "output-schema.md": ["bank-front-fact-reconciliation/references/output-schema.md",
                         "bank-front-kyc-gap-check/references/output-schema.md"],
    "input-schema.md": ["bank-front-fact-reconciliation/references/input-schema.md",
                        "bank-front-kyc-gap-check/references/input-schema.md"],
}

# `键` … `文件.md:NN`  同段（表格行或 bullet 行）
CITE = re.compile(r"`((?:[a-z-]+/references/)?(?:output|input)-schema\.md):(\d+)`")


NON_FIELD = {
    "verified", "pending", "missing", "high", "medium", "general",
    "SUCCESS", "PARTIAL", "NOT_RUN", "FAILED", "OPEN", "PENDING", "CLOSED",
    "资金安全", "合规风险", "经营决策", "JSON", "ISO-8601",
    "RUL-FRONT-001-xxx", "xxx", "A", "B", "U", "d",
}


def leaf(k: str) -> str:
    return k.split(".")[-1].split("[]")[0].strip()


def fname_of(cites: list[tuple[str, str]]) -> str:
    return cites[0][0]


def resolve(fname: str, section: str, label: str) -> str:
    """由小节上下文把短文件名解析为具体合同路径。"""
    if "/" in fname:
        return fname
    up = section.startswith("1.1") or "上游" in section
    down = section.startswith("1.2") or "下游" in section
    if section.startswith("4") or "S6" in section or "S8" in section:
        return ("bank-front-fact-reconciliation/references/" + fname) if "上游" in label \
            else ("bank-front-kyc-gap-check/references/" + fname)
    if up:
        return "bank-front-fact-reconciliation/references/" + fname
    if down:
        return "bank-front-kyc-gap-check/references/" + fname
    return ""


def find_line(text: str, key: str) -> int | None:
    """字段在合同中的**实际**首次出现行号（优先 JSON 代码块内的 `"key"` 形态）。"""
    lf = leaf(key)
    pat = re.compile(r'"' + re.escape(lf) + r'"\s*:')
    for i, line in enumerate(text.splitlines(), 1):
        if pat.search(line):
            return i
    for i, line in enumerate(text.splitlines(), 1):
        if f"`{lf}`" in line or f"`{key}`" in line:
            return i
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true", help="把错误行号回写为实测行号")
    args = ap.parse_args()

    texts = {p: f.read_text(encoding="utf-8") for p, f in FILES.items()}
    if not DOC.exists():
        print(f"gk-ke-criteria-line-audit: FAIL — 判据文档缺失 {DOC}", file=sys.stderr)
        return 1
    lines = DOC.read_text(encoding="utf-8").splitlines()

    mism: list[tuple[int, str, str, int, int]] = []
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
            continue
        if not s.startswith(("|", "-")) and "判定键" not in s:
            continue
        cites = CITE.findall(line)
        if not cites:
            continue
        keys = [k for k in re.findall(r"`([^`\n]+)`", line) if not CITE.fullmatch(f"`{k}`")]
        for k in keys:
            if re.search(r"[\u4e00-\u9fff]", k) or len(k) > 30:
                continue
            # 非字段标识符（枚举值/函数名）不是判定键，跳过
            if leaf(k) in NON_FIELD:
                continue
            # **按小节判定所属合同** —— 短文件名（output-schema.md）在上/下游都有，
            # 不结合小节会选出错误文件（v1 曾因此给出自相矛盾的"实际行号"）。
            p = resolve(fname_of(cites), section, label)
            if not p or p not in texts:
                continue
            actual = find_line(texts[p], k)
            if actual is None:
                continue
            checked += 1
            if actual != int(cites[0][1]):
                mism.append((idx, k, p, int(cites[0][1]), actual))

    print("gk-ke-criteria-line-audit")
    print(f"  判据文档: {DOC.name}")
    print(f"  核对的出处标注: {checked} 条")
    if not mism:
        print("  [PASS] 全部出处行号指向正确位置")
        return 0

    print(f"  [FAIL] **{len(mism)} 条**出处行号指向错误位置")
    for idx, k, p, dec, act in mism[:40]:
        print(f"    判据:{idx:>4}  `{k}`  标注 {p.split('/')[-2]}/{p.split('/')[-1]}:{dec}"
              f"  实际:{act}")
    if len(mism) > 40:
        print(f"    …另有 {len(mism) - 40} 条")

    if args.fix:
        fixed = 0
        for idx, k, p, dec, act in mism:
            line = lines[idx - 1]
            # 三种形态：全路径（§4）、`references/x.md`、裸文件名（§1）
            for fname in (p, "references/" + p.split("/")[-1], p.split("/")[-1]):
                old = f"`{fname}:{dec}`"
                if old in line:
                    lines[idx - 1] = line.replace(old, f"`{fname}:{act}`")
                    line = lines[idx - 1]
                    fixed += 1
        DOC.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"  → 已回写 {fixed} 处行号")
        return 0

    print("  → 加 --fix 可自动回写为实测行号")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
