#!/usr/bin/env python3
"""
产品知识合同自检门禁

Loop PI-0 · 由独立 QA 退回项 QA-1 触发新增。

背景：QA-1 发现 evidence-ref.schema.json 的 example[0] 中 sourceBytesHash 为 65 位 hex，
违反自身声明的 pattern ^[0-9a-f]{64}$，而此前的验证只跑了 check_schema（校验 schema 本身
是否合法），没有用 schema 去 validate 它自带的 examples。schema 声明了约束却没人验过示例，
调用方照抄 example 就会产出不合规数据。

本脚本把这类校验固化为可重复执行的门禁，覆盖：
  1. evidence-ref.schema.json 的 meta-schema 合法性
  2. 该 schema 自带 examples 全部通过自身校验（QA-1 的直接防复发）
  3. product-taxonomy.yaml 的 counts 声明与实际数量一致
  4. taxonomy 内部引用完整性（family→category, category→family, product→family/category）
  5. has_products 声明与实际 products 分布一致
  6. 两个合同已注册进 CONTRACT_INDEX 且 authority_source 路径存在
  7. C-2 合规：taxonomy 数据字段中不含真实机构名称（注释区豁免）

用法：
    python3 specs/product-knowledge/check_contracts.py
退出码 0 表示全部通过，非 0 表示有失败项。
"""

import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("FAIL: 缺少 pyyaml", file=sys.stderr)
    sys.exit(2)

try:
    import jsonschema
except ImportError:
    print("FAIL: 缺少 jsonschema", file=sys.stderr)
    sys.exit(2)

REPO = Path(__file__).resolve().parent.parent.parent
SCHEMA = REPO / "specs" / "product-knowledge" / "evidence-ref.schema.json"
TAXONOMY = REPO / "specs" / "product-knowledge" / "product-taxonomy.yaml"
INDEX = REPO / "specs" / "CONTRACT_INDEX.yaml"

# C-2 合规：数据字段中禁止出现的真实机构名称
BANK_NAMES = re.compile(
    r"民生|光大|建设银行|建行|招商银行|招行|工商银行|工行|中国银行|中行|"
    r"农业银行|农行|交通银行|交行|邮储|邮政储蓄|国开行|国家开发银行|浦发|中信银行|兴业银行"
)

results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"{'PASS' if ok else 'FAIL'} | {name}" + (f" | {detail}" if detail else ""))
    return ok


def check_schema_file():
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    try:
        jsonschema.Draft202012Validator.check_schema(schema)
        check("evidence-ref meta-schema 合法", True)
    except jsonschema.SchemaError as e:
        check("evidence-ref meta-schema 合法", False, str(e)[:150])
        return

    # QA-1 防复发：用 schema 校验它自己的 examples
    validator = jsonschema.Draft202012Validator(schema)
    examples = schema.get("examples", [])
    if not examples:
        check("evidence-ref examples 存在", False, "schema 未提供 examples")
        return
    failures = []
    for i, ex in enumerate(examples):
        errs = list(validator.iter_errors(ex))
        if errs:
            failures.append(f"example[{i}]: {errs[0].message[:100]}")
    check(
        f"evidence-ref examples 自校验（{len(examples)} 个）",
        not failures,
        "; ".join(failures) if failures else f"{len(examples)}/{len(examples)} PASS",
    )

    # 显式复查哈希字段长度——QA-1 的具体形态
    for i, ex in enumerate(examples):
        bh = ex.get("sourceBytesHash")
        if bh is not None:
            check(f"example[{i}].sourceBytesHash 为 64 位 hex", len(bh) == 64, f"len={len(bh)}")
        ch = ex.get("sourceContentHash")
        if ch is not None:
            body = ch[len("sha256:"):] if ch.startswith("sha256:") else ch
            check(
                f"example[{i}].sourceContentHash 为 sha256: + 64 位 hex",
                ch.startswith("sha256:") and len(body) == 64,
                f"len={len(body)}",
            )


def check_taxonomy():
    tax = yaml.safe_load(TAXONOMY.read_text(encoding="utf-8"))

    actual = {
        "domains": len(tax["domains"]),
        "families": len(tax["families"]),
        "categories": len(tax["categories"]),
        "products": len(tax["products"]),
    }
    declared = tax.get("counts", {})
    mismatch = [f"{k}: 声明{declared.get(k)} 实际{v}" for k, v in actual.items() if declared.get(k) != v]
    check("taxonomy counts 声明与实际一致", not mismatch, "; ".join(mismatch) or str(actual))

    fam_ids = {f["id"] for f in tax["families"]}
    cat_ids = {c["id"] for c in tax["categories"]}

    dangling = []
    for f in tax["families"]:
        for cid in f.get("categories", []):
            if cid not in cat_ids:
                dangling.append(f"family {f['id']} -> 不存在的 category {cid}")
    for c in tax["categories"]:
        if c["family"] not in fam_ids:
            dangling.append(f"category {c['id']} -> 不存在的 family {c['family']}")
    for p in tax["products"]:
        if p["family"] not in fam_ids:
            dangling.append(f"product {p['product_id']} -> 不存在的 family {p['family']}")
        if p["category"] not in cat_ids:
            dangling.append(f"product {p['product_id']} -> 不存在的 category {p['category']}")
    check("taxonomy 引用完整性", not dangling, "; ".join(dangling[:3]) or "无悬空引用")

    prod_cats = {p["category"] for p in tax["products"]}
    hp_mismatch = [
        f"{c['id']}: 声明{c['has_products']} 实际{c['id'] in prod_cats}"
        for c in tax["categories"]
        if c["has_products"] != (c["id"] in prod_cats)
    ]
    check("taxonomy has_products 一致性", not hp_mismatch, "; ".join(hp_mismatch[:3]) or "一致")

    # 各族 existing_card_count 之和须等于 products 总数
    total_declared = sum(f.get("existing_card_count", 0) for f in tax["families"])
    check(
        "taxonomy 各族卡数之和等于 products 总数",
        total_declared == actual["products"],
        f"族卡数之和={total_declared} products={actual['products']}",
    )

    # C-2：仅检查数据字段，注释已被 yaml.safe_load 剥离，故此处天然只看数据
    dumped = yaml.safe_dump(tax, allow_unicode=True)
    hits = set(BANK_NAMES.findall(dumped))
    check("C-2 taxonomy 数据字段无真实机构名", not hits, f"命中: {sorted(hits)}" if hits else "无命中")


def check_index():
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    by_id = {c["id"]: c for c in index["contracts"]}
    for cid in ("CTR-PK-TAX-001", "CTR-PK-EVR-001"):
        entry = by_id.get(cid)
        if not check(f"{cid} 已注册", entry is not None):
            continue
        src = REPO / entry["authority_source"]
        check(f"{cid} authority_source 存在", src.exists(), entry["authority_source"])


def main():
    print("=== 产品知识合同自检门禁 ===\n")
    check_schema_file()
    print()
    check_taxonomy()
    print()
    check_index()

    failed = [n for n, ok, _ in results if not ok]
    print(f"\n=== 合计 {len(results)} 项，PASS {len(results) - len(failed)}，FAIL {len(failed)} ===")
    if failed:
        for n in failed:
            print(f"  FAILED: {n}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
