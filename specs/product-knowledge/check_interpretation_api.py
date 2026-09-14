#!/usr/bin/env python3
"""
CTR-PK-INT-001 解读 API 契约测试骨架

Loop L03 W13 交付。合同定义了 6 个样例但无执行力，本脚本使其可验证：

  1. 每个成功响应样例按 InterpretationResponse schema 校验
  2. 每个错误响应样例按 ErrorResponse schema 校验
  3. 错误码矩阵完备性：受控失败矩阵中每个 code 都有对应样例或 responses 定义
  4. 状态码与 code 的对应关系正确（404/409/422/503）
  5. 红线校验：UNKNOWN/CONFLICT/STALE 的 displayValue 必须为 null
  6. 红线校验：UNKNOWN 的 evidenceSummaries 必须为空数组
  7. 集合字段必须为数组而非 null（后端规范）
  8. 篡改检测：内置变异用例，篡改后必须被拒（证明校验有约束力）

本脚本是契约测试骨架，不依赖运行中的服务；待 L13 实现 API 后可直接复用
schema 部分做真实响应校验。

用法:
    python3 specs/product-knowledge/check_interpretation_api.py
"""

import copy
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, RefResolver

REPO = Path(__file__).resolve().parent.parent.parent
SPEC = REPO / "specs" / "product-knowledge" / "interpretation-api.openapi.json"

CONTROLLED_FAILURE_CODES = {
    "PRODUCT_KNOWLEDGE_NOT_PUBLISHED": 404,
    "PURPOSE_NOT_ALLOWED": 422,
    "RELEASE_STALE": 409,
    "KNOWLEDGE_GATE_FAILED": 422,
    "FAILED_CLOSED": 503,
}

NULL_REQUIRED_STATES = {"UNKNOWN", "CONFLICT", "STALE"}

results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"{'PASS' if ok else 'FAIL'} | {name}" + (f" | {detail}" if detail else ""))
    return ok


def validator_for(doc, schema_name):
    schemas = doc["components"]["schemas"]
    resolver = RefResolver.from_schema({"components": {"schemas": schemas}},
                                       store={})
    # 用内联方式解析 $ref
    base = {"$defs": schemas, **schemas[schema_name]}
    text = json.dumps(base).replace("#/components/schemas/", "#/$defs/")
    return Draft202012Validator(json.loads(text))


def main():
    if not SPEC.exists():
        check("interpretation-api.openapi.json 存在", False, str(SPEC))
        return 1

    doc = json.loads(SPEC.read_text(encoding="utf-8"))
    examples = doc["components"].get("examples", {})
    check(f"样例数量 ({len(examples)})", len(examples) >= 6, f"实际 {len(examples)}，期望 >= 6")

    v_resp = validator_for(doc, "InterpretationResponse")
    v_err = validator_for(doc, "ErrorResponse")

    success_cases, error_cases = {}, {}
    for name, ex in examples.items():
        val = ex.get("value", {})
        (error_cases if "status" in val and "error" in val else success_cases)[name] = val

    check(f"成功样例 {len(success_cases)} / 错误样例 {len(error_cases)}",
          len(success_cases) >= 3 and len(error_cases) >= 3,
          f"success={sorted(success_cases)} error={sorted(error_cases)}")

    # 1：成功响应校验
    for name, val in sorted(success_cases.items()):
        errs = list(v_resp.iter_errors(val))
        check(f"成功样例 {name} 符合 InterpretationResponse", not errs,
              errs[0].message[:100] if errs else "")

        # 5 + 6 + 7：红线校验
        for f in val.get("fields", []):
            ks = f.get("knowledgeState")
            fp = f.get("fieldPath")
            if ks in NULL_REQUIRED_STATES:
                ok = f.get("displayValue") is None
                check(f"  {name}/{fp} {ks} 的 displayValue 为 null",
                      ok, "" if ok else f"实为 {f.get('displayValue')!r}")
            if ks == "UNKNOWN":
                ok = f.get("evidenceSummaries") == []
                check(f"  {name}/{fp} UNKNOWN 的 evidenceSummaries 为空数组",
                      ok, "" if ok else f"实为 {f.get('evidenceSummaries')!r}")
            if ks == "CONFLICT":
                ok = bool(f.get("conflictId"))
                check(f"  {name}/{fp} CONFLICT 必须带 conflictId",
                      ok, "" if ok else "conflictId 缺失")
        check(f"  {name} fields 为数组（非 null）", isinstance(val.get("fields"), list))

    # 2 + 4：错误响应校验
    for name, val in sorted(error_cases.items()):
        errs = list(v_err.iter_errors(val))
        check(f"错误样例 {name} 符合 ErrorResponse", not errs,
              errs[0].message[:100] if errs else "")
        code = val.get("code")
        if code in CONTROLLED_FAILURE_CODES:
            expected = CONTROLLED_FAILURE_CODES[code]
            ok = val.get("status") == expected
            check(f"  {name} status {val.get('status')} 与 code {code} 匹配",
                  ok, "" if ok else f"期望 {expected}")

    # 3：错误码矩阵完备性
    declared = set(doc["components"]["schemas"]["ErrorResponse"]["properties"]["code"]["enum"])
    missing = set(CONTROLLED_FAILURE_CODES) - declared
    check("错误码枚举覆盖受控失败矩阵", not missing, f"缺 {sorted(missing)}" if missing else "")

    # responses 定义完备性
    op = doc["paths"]["/api/v1/product-knowledge/{productId}/interpretation"]["get"]
    resp_codes = {int(c) for c in op["responses"] if c.isdigit()}
    need = {200} | set(CONTROLLED_FAILURE_CODES.values())
    check("responses 覆盖全部状态码", need <= resp_codes,
          f"缺 {sorted(need - resp_codes)}" if need - resp_codes else f"{sorted(resp_codes)}")

    # purpose / view 参数枚举
    params = {p["name"]: p for p in op.get("parameters", [])}
    check("purpose 参数为必填枚举",
          params.get("purpose", {}).get("required") is True
          and set(params["purpose"]["schema"]["enum"]) == {"INTERPRETATION", "RECOMMENDATION"})
    check("view 参数覆盖三视图",
          set(params.get("view", {}).get("schema", {}).get("enum", []))
          == {"OVERVIEW", "ELIGIBILITY", "PRICING"})

    # 8：篡改检测（证明校验有约束力）
    if success_cases:
        base = copy.deepcopy(next(iter(success_cases.values())))
        m1 = copy.deepcopy(base)
        m1.pop("bundleHash", None)
        check("篡改检测：删除 bundleHash 必须被拒",
              bool(list(v_resp.iter_errors(m1))))

        m2 = copy.deepcopy(base)
        m2["bundleHash"] = "not-a-hash"
        check("篡改检测：非法 bundleHash 必须被拒",
              bool(list(v_resp.iter_errors(m2))))

        m3 = copy.deepcopy(base)
        m3["view"] = "INVALID_VIEW"
        check("篡改检测：非法 view 必须被拒",
              bool(list(v_resp.iter_errors(m3))))

    if error_cases:
        e = copy.deepcopy(next(iter(error_cases.values())))
        e["code"] = "SOME_UNDECLARED_CODE"
        check("篡改检测：未声明错误码必须被拒", bool(list(v_err.iter_errors(e))))

    failed = [r for r in results if not r[1]]
    print(f"\n{'=' * 60}")
    print(f"解读 API 契约测试：{len(results) - len(failed)}/{len(results)} PASS")
    if failed:
        print("失败项：")
        for n, _, d in failed:
            print(f"  - {n} {d}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
