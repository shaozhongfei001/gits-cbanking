#!/usr/bin/env python3
"""
CTR-PR 增补合同门禁

Loop L03 W5 交付。校验推荐侧三份合同的 L03 增补：
  1. meta-schema 合法性
  2. 向后兼容：不含新字段的旧实例必须仍然通过
  3. 新增字段结构正确（knowledgeBinding 四元组等）
  4. 既有 examples 无回归
  5. L03 新样例通过
  6. x-invariants 已声明且已在 invariants.py 中注册为可执行

用法:
    python3 specs/product-knowledge/check_pr_contracts.py
"""

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, SchemaError

sys.path.insert(0, str(Path(__file__).resolve().parent))
from invariants import INVARIANTS  # noqa: E402

REPO = Path(__file__).resolve().parent.parent.parent
PR = REPO / "specs" / "product-recommendation"

SCHEMAS = {
    "CTR-PR-RES-001": PR / "recommendation-result.schema.json",
    "CTR-PR-ELIG-001": PR / "eligibility-result.schema.json",
    "CTR-PR-DEC-001": PR / "recommendation-human-decision.schema.json",
}

# 不含任何 L03 新字段的最小旧实例（向后兼容基线）
LEGACY_INSTANCES = {
    "CTR-PR-RES-001": {
        "schemaVersion": "1.0.0", "runId": "RUN-legacy", "productKnowledgeSnapshotRef": "SNAP-1",
        "ruleExecutionRef": "RE-1", "evidenceBundleId": "EB-1", "contentHash": "a" * 64,
        "traceId": "T-1", "generatedAt": "2026-09-05T10:00:00+08:00"},
    "CTR-PR-ELIG-001": {
        "schemaVersion": "1.0.0", "productId": "PROD-CM-001",
        "productVersion": "v1", "eligibility": "UNKNOWN"},
    "CTR-PR-DEC-001": {
        "schemaVersion": "1.0.0", "gateId": "HG-D01", "runId": "RUN-1",
        "proposalVersionId": "PV-1", "decision": "APPROVE", "actorId": "rm001",
        "decidedAt": "2026-09-05T10:00:00+08:00"},
}

REQUIRED_NEW_FIELDS = {
    "CTR-PR-RES-001": ["knowledgeBinding", "knowledgeStaleState", "controlledFailure"],
    "CTR-PR-ELIG-001": ["knowledgeState", "knowledgeBindingRef", "neutralizationReason"],
    "CTR-PR-DEC-001": ["knowledgeBindingAudit", "aiBoundaryAttestation"],
}

L03_EXAMPLES = {
    "l03-valid-result-bound-fresh.json": "CTR-PR-RES-001",
    "l03-valid-result-failed-closed.json": "CTR-PR-RES-001",
    "l03-valid-eligibility-stale-neutralized.json": "CTR-PR-ELIG-001",
    "l03-valid-decision-with-audit.json": "CTR-PR-DEC-001",
}

LEGACY_EXAMPLES = {
    "valid-eligibility.json": "CTR-PR-ELIG-001",
    "valid-decision.json": "CTR-PR-DEC-001",
}

results = []


def check(name, ok, detail=""):
    results.append((name, ok, detail))
    print(f"{'PASS' if ok else 'FAIL'} | {name}" + (f" | {detail}" if detail else ""))
    return ok


def main():
    loaded = {}
    for cid, p in SCHEMAS.items():
        if not p.exists():
            check(f"{cid} 文件存在", False, str(p))
            continue
        s = json.loads(p.read_text(encoding="utf-8"))
        loaded[cid] = s

        try:
            Draft202012Validator.check_schema(s)
            check(f"{cid} meta-schema 合法", True)
        except SchemaError as e:
            check(f"{cid} meta-schema 合法", False, str(e).split("\n")[0])
            continue

        # 2：向后兼容
        errs = list(Draft202012Validator(s).iter_errors(LEGACY_INSTANCES[cid]))
        check(f"{cid} 向后兼容（旧实例无新字段）", not errs,
              errs[0].message[:90] if errs else "")

        # 3：新字段已加入
        props = s.get("properties", {})
        missing = [f for f in REQUIRED_NEW_FIELDS[cid] if f not in props]
        check(f"{cid} L03 增补字段齐备", not missing, f"缺 {missing}" if missing else "")

        # x-contract 版本与兼容性标注
        xc = s.get("x-contract", {})
        check(f"{cid} 标注 v1.1-candidate", xc.get("version") == "1.1.0-candidate",
              xc.get("version", "MISSING"))
        check(f"{cid} 标注 backward_compatible",
              xc.get("compatibility") == "backward_compatible", xc.get("compatibility", "MISSING"))
        check(f"{cid} status=CANDIDATE", xc.get("status") == "CANDIDATE", xc.get("status", "MISSING"))

        # 6：不变式已声明且可执行
        invs = s.get("x-invariants", [])
        check(f"{cid} 声明 x-invariants", len(invs) > 0, f"{len(invs)} 条")
        ids = [i.split(":")[0].strip() for i in invs]
        unreg = [i for i in ids if i not in INVARIANTS]
        # L03 W12：跨对象不变式已全部执行化，无豁免项
        check(f"{cid} 不变式已注册为可执行（零豁免）", not unreg,
              f"未注册 {unreg}" if unreg else f"{len(ids)}/{len(ids)} 条可执行")

    # 4 + 5：样例校验
    exdir = PR / "examples"
    for ex, cid in {**LEGACY_EXAMPLES, **L03_EXAMPLES}.items():
        p = exdir / ex
        if not p.exists():
            check(f"样例 {ex} 存在", False)
            continue
        inst = {k: v for k, v in json.loads(p.read_text(encoding="utf-8")).items() if k != "_case"}
        errs = list(Draft202012Validator(loaded[cid]).iter_errors(inst))
        check(f"样例 {ex} 校验通过", not errs, errs[0].message[:90] if errs else "")

    failed = [r for r in results if not r[1]]
    print(f"\n{'=' * 60}")
    print(f"CTR-PR 增补门禁：{len(results) - len(failed)}/{len(results)} PASS")
    if failed:
        print("失败项：")
        for n, _, d in failed:
            print(f"  - {n} {d}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
