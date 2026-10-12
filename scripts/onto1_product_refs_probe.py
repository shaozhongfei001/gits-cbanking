#!/usr/bin/env python3
"""ONTO1 WI-A5｜产品关系引用探针：把「40 处悬空引用」变成 D2 可分类的机读清单。

背景：复审包与设计 V2.0 反复提到「40 处悬空引用」，但**没有任何文件给出逐条清单**，
产品 Owner 无法据此裁决。本脚本把产品卡 front matter 中的产品引用字段逐条展开、
与产品身份空间（`PROD-*` / `products.ttl` 个体）比对，产出可分类的清单。

引用字段（front matter）：
    product_id                      身份（期望落在产品身份空间）
    prerequisite_product_ids[]      requiresProduct 语义
    mutex_product_ids[]             mutuallyExclusiveWith 语义
    complementary_products[]        complementsProduct 语义
    admission_criteria.requiredAccountRelationship   账户关系（**不是**产品引用）

门禁（fail-closed）
    P1 必须找到产品卡，否则 FAIL（不得"0 卡片也算绿"）
    P2 三个产品引用字段必须至少在卡片中出现过，否则 FAIL（探针失明）
    P3 悬空引用必须 > 0，否则 FAIL（若真为 0，说明问题已修，需人工确认后放宽）
    P4 机读清单与汇总必须落盘并记哈希
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
KERT = WORKSPACE / "Leibniz-KERT"
CARD_GLOBS = ["examples/**/product-cards/PROD-*.md", "examples/**/PROD-*.md"]
PRODUCTS_TTL = ROOT / "specs/knowledge-architecture/instances/product/products.ttl"
OUT_DIR = ROOT / "loops/ONTO1-ontology-split/evidence"

PRODUCT_REF_FIELDS = {
    "prerequisite_product_ids": "requiresProduct",
    "mutex_product_ids": "mutuallyExclusiveWith",
    "complementary_products": "complementsProduct",
}
NON_PRODUCT_FIELDS = ("capabilities", "product_family", "applicable_scenarios", "risk_notes",
                      "required_materials", "prohibited_industries")


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def find_cards(root: Path) -> list[Path]:
    cards: set[Path] = set()
    for pattern in CARD_GLOBS:
        cards.update(path for path in root.glob(pattern) if path.is_file())
    return sorted(cards)


def parse_front_matter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    parts = text.split("---")
    if len(parts) < 3:
        return {}
    fields: dict[str, str] = {}
    for line in parts[1].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*?)\s*$", line)
        if match:
            fields[match.group(1)] = match.group(2)
    return fields


def parse_list(value: str) -> list[str]:
    value = (value or "").strip()
    if value in ("", "null", "[]", "~"):
        return []
    value = value.strip("[]")
    return [item.strip().strip("'\"") for item in value.split(",") if item.strip().strip("'\"")]


def product_id_space(cards: list[Path], ttl: Path) -> set[str]:
    ids: set[str] = set()
    for card in cards:
        pid = parse_front_matter(card).get("product_id", "").strip()
        if pid:
            ids.add(pid)
    if ttl.is_file():
        for match in re.finditer(r"^gits:(prod_[a-z0-9_]+)", ttl.read_text(encoding="utf-8"), re.M):
            ids.add(match.group(1).upper().replace("_", "-"))
    return ids


def probe(card_root: Path, ttl: Path = PRODUCTS_TTL) -> dict:
    cards = find_cards(card_root)
    if not cards:
        raise RuntimeError(f"no product cards found under {card_root}")
    ids = product_id_space(cards, ttl)
    other_vocab: dict[str, set[str]] = {name: set() for name in NON_PRODUCT_FIELDS}
    parsed = {card: parse_front_matter(card) for card in cards}
    for fields in parsed.values():
        for name in NON_PRODUCT_FIELDS:
            other_vocab[name].update(parse_list(fields.get(name, "")))

    occurrences: list[dict] = []
    declared: set[str] = set()
    for card in cards:
        fields = parsed[card]
        declared.update(field for field in PRODUCT_REF_FIELDS if field in fields)
        for field, relation in PRODUCT_REF_FIELDS.items():
            for value in parse_list(fields.get(field, "")):
                if value in ids:
                    kind = "RESOLVED_PRODUCT_ID"
                    hint = ""
                else:
                    colliding = [name for name, vocab in other_vocab.items() if value in vocab]
                    if colliding:
                        kind = "SCHEME_MISMATCH_OTHER_VOCAB"
                        hint = "值同时出现在非产品字段: " + ",".join(colliding)
                    else:
                        kind = "UNKNOWN_TOKEN"
                        hint = "在产品身份空间与其它词表中均未出现"
                occurrences.append({
                    "card": card.name,
                    "product_id": fields.get("product_id", ""),
                    "field": field,
                    "relation": relation,
                    "value": value,
                    "resolution": kind,
                    "hint": hint,
                })
    account_rel = [{"card": card.name, "value": value}
                   for card, fields in parsed.items()
                   for value in parse_list(fields.get("requiredAccountRelationship", ""))]
    zero_instance = [field for field in PRODUCT_REF_FIELDS
                     if not any(row["field"] == field for row in occurrences)]
    return {"cards": cards, "ids": sorted(ids), "occurrences": occurrences,
            "account_relationship": account_rel, "declared_fields": sorted(declared),
            "zero_instance_fields": zero_instance}


def write_report(result: dict, out_dir: Path | None = None) -> dict:
    global OUT_DIR
    if out_dir is not None:
        OUT_DIR = out_dir
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    inventory = OUT_DIR / "product-refs-inventory.csv"
    with inventory.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["card", "product_id", "field", "relation",
                                                   "value", "resolution", "hint"])
        writer.writeheader()
        for row in result["occurrences"]:
            writer.writerow(row)
    by_field: dict[str, int] = {}
    by_value: dict[str, int] = {}
    by_resolution: dict[str, int] = {}
    for row in result["occurrences"]:
        by_field[row["field"]] = by_field.get(row["field"], 0) + 1
        by_value[row["value"]] = by_value.get(row["value"], 0) + 1
        by_resolution[row["resolution"]] = by_resolution.get(row["resolution"], 0) + 1
    summary = {
        "cards": len(result["cards"]),
        "product_ids": len(result["ids"]),
        "reference_occurrences": len(result["occurrences"]),
        "by_field": by_field,
        "by_resolution": by_resolution,
        "distinct_values": len(by_value),
        "top_values": sorted(by_value.items(), key=lambda item: -item[1])[:15],
        "account_relationship_occurrences": len(result["account_relationship"]),
        "account_relationship_distinct": sorted({row["value"] for row in result["account_relationship"]}),
        "declared_fields": result["declared_fields"],
        "zero_instance_fields": result["zero_instance_fields"],
        "inventory_file": _rel(inventory),
        "inventory_sha256": hashlib.sha256(inventory.read_bytes()).hexdigest(),
    }
    (OUT_DIR / "product-refs-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


def gate(card_root: Path = KERT, ttl: Path = PRODUCTS_TTL, out_dir: Path | None = None) -> int:
    failures: list[str] = []
    try:
        result = probe(card_root, ttl)
    except RuntimeError as exc:
        # QA-W3R4 C-2 修复：P1 原先位于 `raise` 之后的 `failures.append("P1 no product cards")` ⇒ **永不可达**。
        # 现把 P1 具名并入异常路径（退出语义不变：仍 exit 2，仅失败消息含 P1）。
        print(f"onto1-product-refs: FAIL: P1 no product cards（{exc}）", file=sys.stderr)
        return 2
    summary = write_report(result, out_dir)

    if summary["cards"] < 1:
        failures.append("P1 no product cards")
    print(f"[P1] cards={summary['cards']} product_ids={summary['product_ids']} "
          f"references={summary['reference_occurrences']}")

    for field in PRODUCT_REF_FIELDS:
        if field not in summary["declared_fields"]:
            failures.append(f"P2 relation field never declared in any card front matter: {field}")
    print(f"[P2] by_field={summary['by_field']} declared={summary['declared_fields']}")

    dangling = sum(count for kind, count in summary["by_resolution"].items()
                   if kind != "RESOLVED_PRODUCT_ID")
    if dangling == 0:
        failures.append("P3 zero dangling references (problem may be fixed; confirm before relaxing)")
    print(f"[P3] by_resolution={summary['by_resolution']} dangling={dangling}")
    print(f"[P4] inventory={summary['inventory_file']} sha256={summary['inventory_sha256'][:16]}")
    print(f"     账户关系字段（非产品引用）：{summary['account_relationship_occurrences']} 处 "
          f"{summary['account_relationship_distinct']}")
    if summary["zero_instance_fields"]:
        print(f"[P5] 零实例关系（⇒ 对应 SHACL 场景 = NOT_EVALUATED，不得包装为通过）："
              f"{summary['zero_instance_fields']}")

    if failures:
        for item in failures:
            print(f"onto1-product-refs: FAIL: {item}", file=sys.stderr)
        return 2
    print("onto1-product-refs: PASS")
    return 0


def selftest() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="onto1-product-refs-selftest-"))
    failures: list[str] = []
    try:
        def make(root: Path, body: str) -> Path:
            cards = root / "examples" / "x" / "product-cards"
            cards.mkdir(parents=True, exist_ok=True)
            (cards / "PROD-XX-001.md").write_text(body, encoding="utf-8")
            return root

        good = make(tmp / "good", "---\nproduct_id: PROD-XX-001\n"
                                   "prerequisite_product_ids: [PROD-XX-001]\n"
                                   "mutex_product_ids: [PROD-XX-001]\n"
                                   "complementary_products: [PROD-XX-001]\n---\n# x\n")
        result = probe(good, Path("/nonexistent"))
        resolved = all(row["resolution"] == "RESOLVED_PRODUCT_ID" for row in result["occurrences"])
        print(f"{'PASS' if resolved else 'FAIL'}  M1 已解析 ID 必须判 RESOLVED_PRODUCT_ID")
        if not resolved:
            failures.append("M1")

        bad = make(tmp / "bad", "---\nproduct_id: PROD-XX-001\n"
                                "prerequisite_product_ids: [SETTLEMENT_ACCOUNT]\n"
                                "mutex_product_ids: []\n"
                                "complementary_products: [CORPORATE_E_BANK]\n"
                                "capabilities: [CORPORATE_E_BANK]\n---\n# x\n")
        result2 = probe(bad, Path("/nonexistent"))
        kinds = {row["value"]: row["resolution"] for row in result2["occurrences"]}
        ok2 = kinds.get("SETTLEMENT_ACCOUNT") == "UNKNOWN_TOKEN" and \
            kinds.get("CORPORATE_E_BANK") == "SCHEME_MISMATCH_OTHER_VOCAB"
        print(f"{'PASS' if ok2 else 'FAIL'}  M2 悬空/跨词表取值必须被区分  {kinds}")
        if not ok2:
            failures.append("M2")

        (tmp / "empty").mkdir()
        code = gate(tmp / "empty", Path("/nonexistent"), out_dir=tmp / "out-empty")
        ok3 = code == 2
        print(f"{'PASS' if ok3 else 'FAIL'}  M3 无产品卡 ⇒ 门禁 FAIL  exit={code}")
        if not ok3:
            failures.append("M3")

        code4 = gate(KERT)
        print(f"{'PASS' if code4 == 0 else 'FAIL'}  M0 对照：真实产品卡 ⇒ PASS  exit={code4}")
        if code4 != 0:
            failures.append("M0")

        if failures:
            print(f"onto1-product-refs-selftest: FAIL {failures}", file=sys.stderr)
            return 2
        print("onto1-product-refs-selftest: PASS")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--card-root", default=str(KERT))
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    return gate(Path(args.card_root))


if __name__ == "__main__":
    raise SystemExit(main())
