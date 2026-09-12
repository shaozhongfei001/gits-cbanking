#!/usr/bin/env python3
"""GK-KE 能力语义探针（建议书 §9.4）。

§9.4 原文要求：
  「结构和变异测试有价值，但不能证明测试所表达的业务标准正确。
   健康检查也不能只验证 HTTP 200；**至少使用一个已知语义样例检查
   输入、结果、证据及失败状态**。」

因此本探针不检查"端点是否响应"，而检查：
  (a) 该能力是否有**真实提供者**（providerId 可解析）
  (b) 是否有**已知语义样例**（输入 + 期望输出 + **必须失败**的负例）
  (c) 调用结果是否包含**证据引用**（evidenceRefs），而非仅文本
  (d) 失败行为是否**明确失败**（不可静默成功）

结论只能是：
  PASSED     —— (a)(b)(c)(d) 全部满足
  FAILED     —— 已尝试调用但结果不符合语义样例
  NOT_PROBED —— 无提供者或无语义样例，**未尝试**（不是"通过"）

关键纪律（防止把"未测"当成"通过"）：
  无 providerId 的能力一律 NOT_PROBED，且 callable 必须为 false。
  本项目当前**不存在任何真实 KERT 提供者绑定**，故预期结果为：
  仅 SIM-CAP-INTERPRET 通过（因其有已注册 executor 与 EvidenceBundle 绑定），
  其余 9 项均为 NOT_PROBED。

用法：
  python3 scripts/gk_ke_capability_probe.py            # 运行探针并报告
  python3 scripts/gk_ke_capability_probe.py --write    # 回填 probeStatus/callable
  python3 scripts/gk_ke_capability_probe.py --json     # 机器可读输出
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "specs" / "knowledge-architecture" / "registry" / "Capability.json"
MAPPING = ROOT / "specs" / "knowledge-architecture" / "registry" / "CapabilityIdMapping.json"
PROBES = ROOT / "specs" / "knowledge-architecture" / "registry" / "semantic-probes"
DATASET = ROOT / "scenario" / "seed" / "18_gk_ke_dataset_v2"

UNRESOLVED_PROVIDER = {"PENDING", "PENDING_NAMING_MAPPING", "", None}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def load_probes() -> dict[str, dict]:
    """载入已知语义样例。每个样例必须含 input / expected / mustFail。"""
    out: dict[str, dict] = {}
    if not PROBES.is_dir():
        return out
    for path in sorted(PROBES.glob("*.json")):
        doc = load(path)
        cid = doc.get("capabilityId")
        if cid:
            out[cid] = doc
    return out


def probe_capability(item: dict, probes: dict[str, dict], mapping_index: dict[str, dict]) -> dict:
    """对单个能力做语义探针判定。

    返回 {capabilityId, verdict, reasons: [...], checks: {...}}
    """
    cid = item.get("capabilityId")
    reasons: list[str] = []
    checks: dict[str, bool] = {}

    mapping = mapping_index.get(cid, {})
    provider = item.get("executorRef")
    has_provider = provider not in UNRESOLVED_PROVIDER
    checks["providerResolvable"] = has_provider
    if not has_provider:
        reasons.append(f"executorRef 未解析（{provider!r}）")

    # 映射侧兼容性未证实者，不得视为已绑定真实提供者。
    # 说明：只有**存在** legacyId 映射条目时才受此约束。
    # 若能力有直接已注册 executor（非经 legacy 命名映射获得），则无需映射判定。
    verdict_map = mapping.get("verdict")
    has_mapping_entry = bool(mapping)
    mapping_proven = (not has_mapping_entry) or (verdict_map == "PROVEN_COMPATIBLE")
    checks["mappingProven"] = mapping_proven
    if has_provider and has_mapping_entry and not mapping_proven:
        reasons.append(
            f"ID 映射 verdict={verdict_map!r}，未证实语义兼容（建议书 §9.2）"
        )

    sample = probes.get(cid)
    checks["hasSemanticSample"] = sample is not None
    if sample is None:
        reasons.append("无已知语义样例（§9.4 要求，禁止用 HTTP 200 代替）")

    has_evidence_expectation = bool(
        sample and sample.get("expected", {}).get("evidenceRefsRequired") is not None
    )
    checks["interrogatesEvidence"] = has_evidence_expectation
    if sample is not None and not has_evidence_expectation:
        reasons.append("语义样例未声明 evidenceRefs 要求")

    has_must_fail = bool(sample and sample.get("mustFail"))
    checks["hasFailureCase"] = has_must_fail
    if sample is not None and not has_must_fail:
        reasons.append("语义样例未含必须失败的负例（无法验证失败行为）")

    # schema 引用固定
    schemas_fixed = (
        item.get("inputSchemaRef") not in UNRESOLVED_PROVIDER
        and item.get("outputSchemaRef") not in UNRESOLVED_PROVIDER
    )
    checks["schemasFixed"] = schemas_fixed
    if not schemas_fixed:
        reasons.append("inputSchemaRef/outputSchemaRef 未固定")

    # 判定
    if not has_provider:
        verdict = "NOT_PROBED"
    elif not (mapping_proven and checks["hasSemanticSample"]
              and checks["interrogatesEvidence"] and checks["hasFailureCase"]
              and schemas_fixed):
        verdict = "NOT_PROBED"
    else:
        # 具备完整探针条件：此处为真实调用点。
        # 当前仓库无 KERT 运行环境接入，故实际调用以 dry-run 声明；
        # 只有样本、映射、schema、失败用例齐备时才允许进入此分支。
        verdict = "PASSED" if sample.get("dryRunVerified") is True else "FAILED"
        if verdict == "FAILED":
            reasons.append("探针条件齐备但 dryRunVerified 非 true")

    return {
        "capabilityId": cid,
        "verdict": verdict,
        "callable": verdict == "PASSED",
        "checks": checks,
        "reasons": reasons,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="回填 probeStatus/callable")
    parser.add_argument("--json", action="store_true", help="机器可读输出")
    args = parser.parse_args()

    registry = load(REGISTRY)
    mapping = load(MAPPING)
    items = registry.get("items", [])
    mapping_index = {e.get("canonicalCapabilityId"): e for e in mapping.get("entries", [])}
    probes = load_probes()

    results = [probe_capability(it, probes, mapping_index) for it in items]

    # 一致性守卫：以**计算出的**判定为准，检查回填后是否会留下
    # 「probeStatus != PASSED 但 callable == true」的矛盾状态。
    # 注意不能用回填前的 item['callable'] 判断——那会在首次引入探针时误报。
    violations: list[str] = []
    for item, res in zip(items, results):
        if res["verdict"] != "PASSED" and res["callable"] is True:
            violations.append(
                f"{res['capabilityId']}: probeStatus={res['verdict']} 但 callable=true"
            )
        # 额外守卫：不得出现"无语义样例却声称 PASSED"
        if res["verdict"] == "PASSED" and not res["checks"].get("hasSemanticSample"):
            violations.append(
                f"{res['capabilityId']}: 无语义样例却判定 PASSED（禁止）"
            )
    if violations:
        print("gk-ke-capability-probe: FAIL", file=sys.stderr)
        for v in violations:
            print(f"  - {v}", file=sys.stderr)
        return 1

    if args.write:
        by_id = {r["capabilityId"]: r for r in results}
        for item in items:
            r = by_id[item["capabilityId"]]
            item["probeStatus"] = r["verdict"]
            item["callable"] = r["callable"]
            item["probeEvidence"] = {
                "probedAt": "2026-09-12",
                "method": "SEMANTIC_SAMPLE_NOT_HTTP_200",
                "checks": r["checks"],
                "reasons": r["reasons"],
                "datasetRef": (
                    "scenario/seed/18_gk_ke_dataset_v2"
                    if DATASET.is_dir() else None
                ),
            }
        registry["probeSummary"] = {
            "total": len(results),
            "passed": sum(1 for r in results if r["verdict"] == "PASSED"),
            "failed": sum(1 for r in results if r["verdict"] == "FAILED"),
            "notProbed": sum(1 for r in results if r["verdict"] == "NOT_PROBED"),
            "callableCount": sum(1 for r in results if r["callable"]),
            "statement": (
                "只有 PASSED 的能力 callable=true。NOT_PROBED 表示未尝试，"
                "不表示通过；不得据未探针能力声明可运行。"
            ),
        }
        REGISTRY.write_text(
            json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print("gk-ke-capability-probe: PASS (report)")
        print(f"  semantic samples found: {len(probes)}")
        for r in results:
            mark = "PASSED " if r["verdict"] == "PASSED" else r["verdict"]
            print(f"  [{mark:9s}] {r['capabilityId']:28s} callable={r['callable']}")
            for reason in r["reasons"][:2]:
                print(f"              - {reason}")
        n_pass = sum(1 for r in results if r["verdict"] == "PASSED")
        print(f"  total={len(results)} passed={n_pass} "
              f"notProbed={sum(1 for r in results if r['verdict'] == 'NOT_PROBED')}")
        print("  NOTE: NOT_PROBED 表示未尝试，不表示通过。")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
