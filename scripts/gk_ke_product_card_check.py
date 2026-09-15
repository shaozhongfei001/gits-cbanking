#!/usr/bin/env python3
"""GK-KE 产品卡核验（A3 门禁）。

职责：
  1. 核验产品卡具备 §8.1 要求的必填字段
  2. **H-6 守卫：对客解释不得超出原文** —— 每一项条件必须带 sourceQuote，
     且该 sourceQuote 必须**真实出现在** contentRef 指向的原文中
  3. 核验原文哈希与声明一致
  4. 核验体检结论与各检查项自洽

H-6 守卫是本脚本的核心：它防止"我自行给产品加条件"这类超出原文的补写。
依据 KERT skills/product-recommendation/product-cards/README.md：
「产品卡是对权威材料的结构化投影，必须能追溯回源文件与条款。」

用法：
  python3 scripts/gk_ke_product_card_check.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARDS = ROOT / "specs" / "product-knowledge" / "cards"

REQUIRED_CARD_FIELDS = [
    "cardId", "cardVersion", "identity", "conditions", "validity",
    "requiredDocuments", "mutex", "healthCheck", "currentStatus",
]
REQUIRED_CONDITION_FIELDS = ["conditionId", "name", "predicate", "predicateType"]

# 原文中被允许缺省引用的段落（结构化字段允许从这些段取）
SOURCE_QUOTE_MIN_LEN = 4


def norm(text: str) -> str:
    """归一化：去空白，便于中文引文比对。"""
    return "".join(text.split())


def main() -> int:
    failures: list[str] = []
    checked_conditions = 0
    cards = sorted(CARDS.glob("*.json"))

    if not cards:
        print("gk-ke-product-card-check: FAIL", file=sys.stderr)
        print(f"  - 未找到产品卡: {CARDS}", file=sys.stderr)
        return 1

    for card_path in cards:
        card = json.loads(card_path.read_text(encoding="utf-8"))
        cid = card.get("cardId", card_path.stem)

        for f in REQUIRED_CARD_FIELDS:
            if f not in card:
                failures.append(f"[{cid}] 缺必填字段 {f}")

        sv = card.get("sourceVerification", {})
        ref = sv.get("contentRef")
        if not ref:
            failures.append(f"[{cid}] 缺 sourceVerification.contentRef")
            continue

        source_path = ROOT / ref
        if not source_path.is_file():
            failures.append(f"[{cid}] 原文不存在: {ref}")
            continue

        raw = source_path.read_bytes()
        actual = hashlib.sha256(raw).hexdigest()
        declared = sv.get("declaredHash")
        if declared and declared != actual:
            failures.append(f"[{cid}] 原文哈希不匹配: 声明 {declared[:16]}… 实际 {actual[:16]}…")
        if sv.get("locatorAvailable") is not True:
            failures.append(f"[{cid}] locatorAvailable 非 true，但原文实际存在")

        source_text = norm(raw.decode("utf-8"))

        # --- H-6 守卫：每条条件的 sourceQuote 必须真实存在于原文 ---
        for cond in card.get("conditions", []):
            for f in REQUIRED_CONDITION_FIELDS:
                if f not in cond:
                    failures.append(
                        f"[{cid}] 条件 {cond.get('conditionId','?')} 缺字段 {f}")
            quote = cond.get("sourceQuote")
            ccid = cond.get("conditionId", "?")
            if not quote:
                failures.append(f"[{cid}] 条件 {ccid} 缺 sourceQuote（H-6 守卫要求逐条可追溯）")
                continue
            if len(quote) < SOURCE_QUOTE_MIN_LEN:
                failures.append(f"[{cid}] 条件 {ccid} 的 sourceQuote 过短: {quote!r}")
                continue
            if norm(quote) not in source_text:
                failures.append(
                    f"[{cid}] **H-6 违规**：条件 {ccid} 的 sourceQuote 未出现在原文中: "
                    f"{quote!r}")
            else:
                checked_conditions += 1

        # --- 移除记录须说明原因 ---
        for removed in card.get("conditionsNotAsserted", {}).get("removed", []):
            if not removed.get("reason"):
                failures.append(
                    f"[{cid}] conditionsNotAsserted 条目 {removed.get('id')} 缺 reason")

        # --- 体检结论自洽：H-6 有违规则 overall 不得为 HEALTHY ---
        hc = card.get("healthCheck", {})
        h6 = (hc.get("H-6") or {}).get("result")
        if h6 not in ("PASS", None):
            failures.append(f"[{cid}] H-6 未 PASS（{h6}）")
        if hc.get("overall") == "HEALTHY" and h6 != "PASS":
            failures.append(f"[{cid}] overall=HEALTHY 但 H-6 未 PASS，自相矛盾")

        # --- 不得含内容已发布的虚假声明 ---
        if card.get("currentStatus", {}).get("contentPublished") is True:
            failures.append(f"[{cid}] 不得声称 contentPublished=true")

    if failures:
        print("gk-ke-product-card-check: FAIL", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print("gk-ke-product-card-check: PASS")
    print(f"  cards: {len(cards)}")
    print(f"  conditions with verified sourceQuote: {checked_conditions}")
    print("  H-6 guard: 每条条件的 sourceQuote 均已核对存在于原文")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
