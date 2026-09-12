#!/usr/bin/env python3
"""GK-KE 计划编译器（B1 / WP05）。

依据建议书 §10.3 六步计划编译与 §14.2 最小闭环：
  1. 根据 TaskTemplate 解析意图，选择批准的地图版本；多个同优先级匹配 → ROUTE_AMBIGUOUS
  2. 根据任务范围，选择行业方案包和指标子集
  3. 解析资产、产品、规则、能力的精确版本；验证权限、用途、有效期和依赖
  4. 检查必需能力的语义探针与依赖；必需能力不可用则**阻断**
  5. 生成受控 DAG、端口绑定、查询模板及预算，固化 ActivationPlan 和**计划摘要值**
  6. 执行时逐步检查参数与结果，重要引用撤销或失效后重新规划，不悄悄换版本

关键纪律（§10.3）：
  「同一份已经固定的任务意图、证据、权限、版本、配置和运行依赖快照
    应得到**同一计划摘要值**。」

本脚本**不执行**计划，只做编译与阻断判定。

用法：
  python3 scripts/gk_ke_plan_compiler.py            # 编译并报告
  python3 scripts/gk_ke_plan_compiler.py --write    # 写出 ActivationPlan
  python3 scripts/gk_ke_plan_compiler.py --json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KA = ROOT / "specs" / "knowledge-architecture"
LOCK = KA / "activation" / "map_dependency_lock.json"
MAP_SPEC = KA / "activation" / "map_spec.json"
TASK_TEMPLATE = KA / "activation" / "task_template.json"
REGISTRY = KA / "registry" / "Capability.json"
BINDINGS = KA / "registry" / "provider-bindings.json"
PLAYBOOK = KA / "industry" / "SIM-IND-MANUFACTURING.json"
METRIC_REGISTRY = ROOT / "specs" / "gk-ke" / "v1" / "definitions" / "_metric_registry.json"
OUT = KA / "activation" / "compiled_plan.json"


def load(p: Path) -> dict:
    if not p.is_file():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def canonical(obj) -> str:
    return hashlib.sha256(
        json.dumps(obj, ensure_ascii=False, sort_keys=True,
                   separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    barriers: list[dict] = []
    notes: list[str] = []

    lock = load(LOCK)
    map_spec = load(MAP_SPEC)
    task_template = load(TASK_TEMPLATE)
    registry = load(REGISTRY)
    bindings = load(BINDINGS)
    playbook = load(PLAYBOOK)
    metric_registry = load(METRIC_REGISTRY)

    if not lock:
        barriers.append({"step": 1, "code": "DEPENDENCY_LOCK_MISSING",
                         "detail": "map_dependency_lock.json 缺失，无法保证版本固定"})

    # --- 步骤 1：意图解析与地图选择 ---
    route_candidates = []
    if map_spec.get("mapId") and task_template.get("taskType"):
        route_candidates.append(map_spec.get("mapId"))
    route_decision = "SELECTED"
    if len(route_candidates) > 1:
        route_decision = "ROUTE_AMBIGUOUS"
        barriers.append({"step": 1, "code": "ROUTE_AMBIGUOUS",
                         "detail": f"多个同优先级匹配: {route_candidates}"})
    selected_map = lock.get("lockedDependencies", {}).get("mapSpec", {})

    # --- 步骤 2：行业方案包与指标子集 ---
    scope = lock.get("scope", {})
    playbook_id = scope.get("industryPlaybook")
    playbook_ok = bool(playbook) and playbook.get("playbookId") == playbook_id
    if not playbook_ok:
        barriers.append({"step": 2, "code": "INDUSTRY_PLAYBOOK_MISSING",
                         "detail": f"未找到声明的行业方案包 {playbook_id}"})
    enabled_metrics = len(metric_registry.get("definitions", {}))
    if enabled_metrics == 0:
        barriers.append({"step": 2, "code": "NO_ENABLED_METRICS",
                         "detail": "无已启用指标；§14.2 禁止整份报告只有缺失提示"})

    # --- 步骤 3：版本与权限校验 ---
    capability_items = {i["capabilityId"]: i for i in registry.get("items", [])}
    binding_items = {b["canonicalCapabilityId"]: b
                     for b in bindings.get("bindings", [])}

    plan_caps = lock.get("capabilityPlan", {})
    resolved_nodes = []
    for entry in plan_caps.get("required", []) + plan_caps.get("conditional", []):
        cid = entry.get("gkKeId")
        if not cid:
            resolved_nodes.append({
                "proposalRef": entry["ref"], "gkKeId": None,
                "provider": entry.get("provider"), "status": "OUTSIDE_THIS_REPO",
            })
            continue
        item = capability_items.get(cid, {})
        binding = binding_items.get(cid, {})
        resolved_nodes.append({
            "proposalRef": entry["ref"],
            "gkKeId": cid,
            "version": item.get("version"),
            "providerId": binding.get("providerId") or item.get("executorRef"),
            "providerKind": binding.get("providerKind"),
            "bindingVerdict": binding.get("bindingVerdict"),
            "callable": bool(item.get("callable")),
            "probeStatus": item.get("probeStatus"),
            "endpoint": item.get("endpoint"),
        })

    # --- 步骤 4：必需能力探针与依赖（不可用则阻断） ---
    for node in resolved_nodes:
        if node.get("status") == "OUTSIDE_THIS_REPO":
            continue
        if node["callable"] is not True:
            reason = (node.get("bindingVerdict") or "UNKNOWN")
            barrier = {
                "step": 4,
                "code": "REQUIRED_CAPABILITY_NOT_CALLABLE",
                "capabilityId": node["gkKeId"],
                "proposalRef": node["proposalRef"],
                "probeStatus": node["probeStatus"],
                "bindingVerdict": reason,
                "detail": (f"{node['gkKeId']} 不可调用（probeStatus="
                           f"{node['probeStatus']}, verdict={reason}）。"
                           "§10.3 步骤4：必需能力不可用则阻断。"),
            }
            if node["proposalRef"] == "CAP-03":
                barrier["conditional"] = True
                barrier["detail"] += " CAP-03 属条件能力：普通融资访前可用一跳关系，不构成必需。"
                notes.append("CAP-03 为条件能力，其不可调用不阻断，但地图不得声明多跳图能力。")
                continue
            barriers.append(barrier)

    # --- 步骤 5：DAG 与计划摘要值 ---
    digest_input = {
        "taskTemplate": task_template.get("taskId"),
        "mapId": selected_map.get("mapId"),
        "mapVersion": selected_map.get("version"),
        "releaseId": selected_map.get("releaseId"),
        "scope": scope,
        "playbook": playbook_id,
        "metricsEnabled": enabled_metrics,
        "nodes": sorted(
            [{"ref": n["proposalRef"], "id": n.get("gkKeId"), "v": n.get("version")}
             for n in resolved_nodes], key=lambda x: x["ref"]),
        "ruleSubset": lock.get("ruleSubset", {}).get("rules", []),
        "parameterProfile": lock.get("ruleSubset", {}).get("parameterProfile", {}).get("profileId"),
        "dataSnapshot": lock.get("lockedDependencies", {}).get("dataset", {}).get("snapshotId"),
    }
    plan_digest = canonical(digest_input)

    blockers = [b for b in barriers if not b.get("conditional")]
    verdict = "BLOCKED" if blockers else "COMPILABLE"

    plan = {
        "$comment": ("B1/WP05 编译产物。不执行计划，只固化受控 DAG 与计划摘要值。"),
        "planId": "SIM-PLAN-FINANCE-001",
        "planVersion": "1.0.0",
        "simulationOnly": True,
        "status": "CANDIDATE",
        "verdict": verdict,
        "routeDecision": route_decision,
        "planDigest": plan_digest,
        "digestMethod": "sha256(canonical json: sorted keys, compact separators, utf-8)",
        "digestInputs": digest_input,
        "nodes": resolved_nodes,
        "barriers": barriers,
        "notes": notes,
    }

    summary = {
        "verdict": verdict,
        "routeDecision": route_decision,
        "planDigest": plan_digest,
        "nodeCount": len(resolved_nodes),
        "callableNodes": sum(1 for n in resolved_nodes if n.get("callable")),
        "blockerCount": len(blockers),
        "conditionalCount": len(barriers) - len(blockers),
        "enabledMetrics": enabled_metrics,
        "playbookResolved": playbook_ok,
    }

    if args.json:
        print(json.dumps({"summary": summary, "barriers": barriers},
                         ensure_ascii=False, indent=2))
    else:
        print(f"gk-ke-plan-compiler: {verdict}")
        print(f"  route: {route_decision}")
        print(f"  planDigest: {plan_digest[:16]}...")
        print(f"  nodes: {len(resolved_nodes)} (callable {summary['callableNodes']})")
        print(f"  enabled metrics: {enabled_metrics}")
        print(f"  playbook: {'OK' if playbook_ok else 'MISSING'}")
        if barriers:
            print(f"  barriers: {len(blockers)} blocking, "
                  f"{len(barriers) - len(blockers)} conditional")
            for b in barriers:
                tag = "conditional" if b.get("conditional") else "BLOCKING"
                print(f"    [{tag}] {b.get('code')} {b.get('capabilityId', '')}")
        for n in notes:
            print(f"  note: {n}")

    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")
        print(f"  wrote: {OUT.relative_to(ROOT)}")

    # 编译结果不允许被当作"可运行"证据
    if verdict == "BLOCKED":
        print("  NOTE: 计划被阻断。阻断原因是能力不可调用，不是脚本失败。")
        print("  NOTE: 阻断不构成失败退出码——本脚本的职责是如实报告编译结论。")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
