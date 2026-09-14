#!/usr/bin/env python3
"""
L02 候选合同自检门禁

Loop L02（PI-ARCH-IMPLEMENTATION-01）新增。与既有 check_contracts.py 并列，
只覆盖 L02 引入的 CANDIDATE 合同，不改动 PI-0 已有门禁。

覆盖范围：
  1. 5 份 JSON Schema 的 meta-schema 合法性
  2. 每份 schema 自带 examples 全部通过自身校验（防 PI-0 QA-1 类缺陷复发）
  3. OpenAPI 候选文件结构合法 + 无悬空 $ref
  4. 每份合同必须具备 4 类样例：POSITIVE / PUBLIC_TRACK_REJECT / UNKNOWN / CONFLICT / STALE（按合同适用性）
  5. 全部合同已登记进 CONTRACT_INDEX 且 status=CANDIDATE
  6. x-invariants 非空（合同必须声明不变式）
  7. 确定性 ID 约束：evidenceId 的 pattern 必须要求十六进制后缀（防 F-L00-01 复发）

用法：
    python3 specs/product-knowledge/check_l02_candidates.py
退出码 0 表示全部通过。
"""

import json
import sys
from pathlib import Path

try:
    import jsonschema
    from jsonschema import Draft202012Validator
except ImportError:
    print("FAIL: 缺少 jsonschema", file=sys.stderr)
    sys.exit(2)

REPO = Path(__file__).resolve().parent.parent.parent
PK = REPO / "specs" / "product-knowledge"
INDEX = REPO / "specs" / "CONTRACT_INDEX.yaml"

SCHEMAS = {
    "CTR-PK-EVS-002": PK / "evidence-span.schema.json",
    "CTR-PK-ASM-001": PK / "field-assertion.schema.json",
    "CTR-PK-CNF-001": PK / "conflict-case.schema.json",
    "CTR-PK-RLS-001": PK / "product-knowledge-release.schema.json",
    "CTR-PK-CHG-001": PK / "product-knowledge-changed.schema.json",
    "CTR-PK-FLD-001": PK / "field-policy.schema.json",
}
OPENAPI = {"CTR-PK-INT-001": PK / "interpretation-api.openapi.json"}

# 每份合同必须覆盖的样例场景（按适用性）
REQUIRED_CASES = {
    "CTR-PK-EVS-002": ["POSITIVE", "PUBLIC_TRACK_REJECT", "STALE"],
    "CTR-PK-ASM-001": ["POSITIVE", "UNKNOWN", "CONFLICT", "STALE", "PUBLIC_TRACK_REJECT"],
    "CTR-PK-CNF-001": ["OPEN", "RESOLVED"],
    "CTR-PK-RLS-001": ["POSITIVE", "UNKNOWN_BLOCK", "CONFLICT_BLOCK", "STALE", "PUBLIC_TRACK_REJECT"],
    "CTR-PK-CHG-001": ["POSITIVE", "STALE"],
    "CTR-PK-FLD-001": ["POSITIVE", "PUBLIC_TRACK_REJECT"],
}

results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"{'PASS' if ok else 'FAIL'} | {name}" + (f" | {detail}" if detail else ""))
    return ok


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def main():
    # 1 + 2 + 6：schema 合法性、examples 自校验、不变式非空
    for cid, path in SCHEMAS.items():
        if not path.exists():
            check(f"{cid} 文件存在", False, str(path))
            continue
        schema = load(path)

        try:
            Draft202012Validator.check_schema(schema)
            check(f"{cid} meta-schema 合法", True)
        except jsonschema.SchemaError as e:
            check(f"{cid} meta-schema 合法", False, str(e).split("\n")[0])
            continue

        # examples 自校验（剥离 _case 元字段后校验）
        examples = schema.get("examples", [])
        if not examples:
            check(f"{cid} 具备 examples", False, "examples 为空")
            continue

        validator = Draft202012Validator(schema)
        bad = []
        for i, ex in enumerate(examples):
            payload = {k: v for k, v in ex.items() if k != "_case"}
            errs = list(validator.iter_errors(payload))
            if errs:
                bad.append(f"[{i}] {ex.get('_case', '?')}: {errs[0].message[:80]}")
        check(f"{cid} examples 自校验 {len(examples) - len(bad)}/{len(examples)}",
              not bad, "; ".join(bad[:2]))

        # x-invariants 非空
        inv = schema.get("x-invariants", [])
        check(f"{cid} 声明 x-invariants", len(inv) > 0, f"{len(inv)} 条")

        # 4：必需样例场景覆盖
        cases = {ex.get("_case", "").split("—")[0].strip() for ex in examples}
        missing = [c for c in REQUIRED_CASES.get(cid, []) if c not in cases]
        check(f"{cid} 样例场景覆盖", not missing, f"缺 {missing}" if missing else "")

        # x-contract 状态
        xc = schema.get("x-contract", {})
        check(f"{cid} x-contract.status=CANDIDATE",
              xc.get("status") == "CANDIDATE", xc.get("status", "MISSING"))

    # 7：确定性 ID 约束（防 F-L00-01 复发）
    evs = load(SCHEMAS["CTR-PK-EVS-002"])
    pat = evs["properties"]["evidenceId"].get("pattern", "")
    check("CTR-PK-EVS-002 evidenceId 强制十六进制确定性后缀",
          "[0-9a-f]{8}" in pat, pat)

    # 3：OpenAPI 结构与悬空 $ref
    for cid, path in OPENAPI.items():
        if not path.exists():
            check(f"{cid} 文件存在", False, str(path))
            continue
        doc = load(path)
        check(f"{cid} 含 openapi/paths/components",
              all(k in doc for k in ("openapi", "paths", "components")))

        defined = set(doc.get("components", {}).get("schemas", {}).keys())
        refs = set()

        def walk(node):
            if isinstance(node, dict):
                for k, v in node.items():
                    if k == "$ref" and isinstance(v, str) and v.startswith("#/components/schemas/"):
                        refs.add(v.rsplit("/", 1)[1])
                    else:
                        walk(v)
            elif isinstance(node, list):
                for x in node:
                    walk(x)

        walk(doc)
        dangling = refs - defined
        check(f"{cid} 无悬空 $ref", not dangling, f"悬空 {sorted(dangling)}" if dangling else f"{len(refs)} refs")

        # 错误码枚举必须覆盖 6 类受控失败
        codes = set(doc["components"]["schemas"]["ErrorResponse"]["properties"]["code"]["enum"])
        need = {"PRODUCT_KNOWLEDGE_NOT_PUBLISHED", "PURPOSE_NOT_ALLOWED",
                "RELEASE_STALE", "KNOWLEDGE_GATE_FAILED", "FAILED_CLOSED"}
        check(f"{cid} 错误码覆盖受控失败矩阵", need <= codes, f"缺 {sorted(need - codes)}" if need - codes else "")

    # 5：CONTRACT_INDEX 登记
    if INDEX.exists():
        idx = json.loads(INDEX.read_text(encoding="utf-8"))
        registered = {c["id"]: c for c in idx.get("contracts", [])}
        for cid in list(SCHEMAS) + list(OPENAPI):
            entry = registered.get(cid)
            if entry is None:
                check(f"{cid} 已登记 CONTRACT_INDEX", False, "未找到")
            else:
                ok = entry.get("status") == "CANDIDATE"
                src = REPO / entry.get("authority_source", "")
                check(f"{cid} 已登记 CONTRACT_INDEX", ok and src.exists(),
                      f"status={entry.get('status')} source_exists={src.exists()}")
    else:
        check("CONTRACT_INDEX 存在", False, str(INDEX))

    failed = [r for r in results if not r[1]]
    print(f"\n{'=' * 60}")
    print(f"L02 候选合同自检：{len(results) - len(failed)}/{len(results)} PASS")
    if failed:
        print("失败项：")
        for n, _, d in failed:
            print(f"  - {n} {d}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
