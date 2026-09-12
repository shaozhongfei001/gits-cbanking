#!/usr/bin/env python3
"""GK-KE OC-04 路径 A：能力定义可验收性门禁。

背景：Owner 复核指出「能力就绪状态分列（4 个 DESIGN_ONLY）不能接受，需要你设计、交付」。
路径 A = 在 GK-KE 侧把能力补成**可验收的定义与约束**（不再只是空壳登记）；
路径 B（KERT 侧写实现）另行交付。

本门禁校验 4 个原 DESIGN_ONLY 能力是否具备**可验收的完整定义**：
  1. 每个能力文件存在且含必需结构（input / output / rules / failureBehavior /
     acceptanceCriteria / negatives / boundary）
  2. 每个能力必须有**可触发的失败行为**（否定式断言，不得只写正例）
  3. 每个能力必须有**边界声明**（不得越界产生授信/准入结论等）
  4. 就绪状态必须**诚实**（GK-KE 侧已定义 / KERT 侧未实现，两侧分列）
  5. 能力必须与地图 map_spec 中的 id 对齐（不得孤儿定义）
  6. 交叉引用必须可解析（ruleKnowledgeRef / maps）

退出码：全通过 0，否则 1。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAPS_DIR = ROOT / "specs" / "knowledge-architecture" / "capabilities"
MAP = ROOT / "specs" / "knowledge-architecture" / "activation" / "map_spec.json"

# OC-04 路径 A 要求补全的 4 个能力
PATH_A_CAPABILITIES = {
    "SIM-CAP-EIGHT-DIM": {"maps": "bank-front-eight-dimension", "minFailures": 4},
    "SIM-CAP-FACT-RECON": {"maps": "bank-front-fact-reconciliation", "minFailures": 4},
    "SIM-CAP-KYC-GAP": {"maps": "bank-front-kyc-gap-check", "minFailures": 4},
    "SIM-CAP-PRODUCT-REC": {"maps": "bank-front-product-recommendation", "minFailures": 5},
}
REQUIRED_SECTIONS = ("input", "output", "rules", "failureBehavior",
                     "acceptanceCriteria", "negatives", "boundary")


def main() -> int:  # noqa: C901
    failures: list[str] = []

    if not CAPS_DIR.is_dir():
        print(f"FAIL: capabilities dir missing: {CAPS_DIR}", file=sys.stderr)
        return 2
    if not MAP.is_file():
        print(f"FAIL: map spec missing: {MAP}", file=sys.stderr)
        return 2

    map_doc = json.loads(MAP.read_text(encoding="utf-8"))
    map_caps = {c["id"]: c for c in map_doc.get("capabilities", {}).get("items", [])}

    for cap_id, spec in PATH_A_CAPABILITIES.items():
        path = CAPS_DIR / f"{cap_id}.json"
        if not path.is_file():
            failures.append(f"[{cap_id}] definition file missing: {path.name}")
            continue

        d = json.loads(path.read_text(encoding="utf-8"))

        # 1. 身份与结构
        if d.get("capabilityId") != cap_id:
            failures.append(f"[{cap_id}] capabilityId mismatch: {d.get('capabilityId')!r}")
        if d.get("maps") != spec["maps"]:
            failures.append(f"[{cap_id}] maps mismatch: {d.get('maps')!r} != {spec['maps']!r}")
        for sec in REQUIRED_SECTIONS:
            if sec not in d or not d[sec]:
                failures.append(f"[{cap_id}] missing required section: {sec}")

        # 2. 失败行为必须充分（否定式断言）
        fb = d.get("failureBehavior", [])
        if len(fb) < spec["minFailures"]:
            failures.append(f"[{cap_id}] failureBehavior too thin: {len(fb)} < {spec['minFailures']}")
        for f in fb:
            if not f.get("case") or not f.get("result"):
                failures.append(f"[{cap_id}] failureBehavior entry missing case/result")

        # 3. 边界声明（不得越界）
        boundary = d.get("boundary", {})
        if not boundary.get("doesNotProduce"):
            failures.append(f"[{cap_id}] boundary must declare doesNotProduce")
        if not boundary.get("produces"):
            failures.append(f"[{cap_id}] boundary must declare produces")

        # 4. 就绪状态诚实（两侧分列）
        rd = d.get("readinessDetail", {})
        if rd.get("gkKeSide") != "DEFINED_AND_GATED":
            failures.append(f"[{cap_id}] gkKeSide must be DEFINED_AND_GATED, got {rd.get('gkKeSide')!r}")
        if rd.get("kertSide") != "DESIGN_ONLY":
            failures.append(f"[{cap_id}] kertSide must honestly stay DESIGN_ONLY (path B not delivered)")
        if not rd.get("kertEvidence"):
            failures.append(f"[{cap_id}] must record the evidence that KERT has no implementation")
        if not rd.get("handoff"):
            failures.append(f"[{cap_id}] must state the handoff to KERT")

        # 5. 与地图对齐
        if cap_id not in map_caps:
            failures.append(f"[{cap_id}] not referenced by map_spec (orphan definition)")

        # 6. negatives 可解析
        for n in d.get("negatives", []):
            if not n.get("expectedError") or not n.get("desc"):
                failures.append(f"[{cap_id}] negative missing expectedError/desc")

    # 6b. 交叉引用：ruleKnowledgeRef 若声明，其引用的 KI-RULE-* 须能解析到地图规则
    #     地图规则的权威标识在 `maps` 字段（KI-RULE-00x），`id` 为内部 SIM- 标识。
    known_ki_rules = {r.get("maps") for r in map_doc.get("ruleKnowledge", {}).get("rules", [])}
    known_ki_rules.discard(None)
    for cap_id in PATH_A_CAPABILITIES:
        path = CAPS_DIR / f"{cap_id}.json"
        if not path.is_file():
            continue
        d = json.loads(path.read_text(encoding="utf-8"))
        ref = d.get("readinessDetail", {}).get("ruleKnowledgeRef")
        if not ref:
            continue
        if not any(ki in ref for ki in known_ki_rules):
            failures.append(
                f"[{cap_id}] ruleKnowledgeRef {ref!r} does not resolve to any map rule "
                f"(known KI rules: {sorted(known_ki_rules)})")

    # 7. 反 for-空壳：能力定义必须显著大于最初的空壳登记
    for cap_id in PATH_A_CAPABILITIES:
        path = CAPS_DIR / f"{cap_id}.json"
        if path.is_file():
            size = len(json.dumps(json.loads(path.read_text(encoding="utf-8")), ensure_ascii=False))
            if size < 1200:
                failures.append(f"[{cap_id}] definition suspiciously small ({size} chars) - likely a shell")

    if failures:
        print("gk-ke-oc04-capability-tests: FAIL", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print("gk-ke-oc04-capability-tests: PASS")
    print(f"  path_a_capabilities: {len(PATH_A_CAPABILITIES)}")
    for cap_id, spec in PATH_A_CAPABILITIES.items():
        d = json.loads((CAPS_DIR / f"{cap_id}.json").read_text(encoding="utf-8"))
        print(f"    {cap_id}: rules={len(d['rules'])} failures={len(d['failureBehavior'])} "
              f"negatives={len(d['negatives'])} kert={d['readinessDetail']['kertSide']}")
    print("  checks: structure, failure-behaviors, boundary, readiness-honesty, "
          "map-alignment, ref-resolution, not-a-shell")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
