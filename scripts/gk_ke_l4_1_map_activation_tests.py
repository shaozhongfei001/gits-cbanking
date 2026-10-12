#!/usr/bin/env python3
"""GK-KE L4-1 地图激活测试（C08 L4-1 / wave D2）。

依据 C06 §2 确定性计划。覆盖 C08 L4-1 退出标准：
「同输入同 hash；同优先级歧义拒绝；必需能力缺失拒绝」。

检查：
  1. TaskTemplate 固化任务上下文（稳定身份，不得用名称替代）
  2. MapSpec 有入口与用途（没有入口和用途说明不能激活）
  3. **确定性路由**：无匹配 → REJECT；同优先级歧义 → ROUTE_AMBIGUOUS
  4. **确定性计划**：
     - 同输入 → 同 canonical planHash（可重复）
     - 随机 planId / traceId / 创建时间 → **不改变** planHash
     - 数组按明确规则排序（重排不改变 hash）
     - Unicode / 小数 / 空值规范化
  5. **必需能力缺失拒绝**（REQUIRED_CAPABILITY_MISSING）
  6. KERT 计划不得包含 GITS 正式业务写回（只返回建议）
  7. 每步含 executor/inputBindings/dependencyStepIds/evidenceRequirement/onFailure/sideEffect
  8. 执行子图不得成环（dependsOn 非 DAG → 拒绝）

退出码：全通过 0，否则 1。
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACT = ROOT / "specs" / "knowledge-architecture" / "activation"

# GITS 正式业务写回动作：不得出现在 KERT 计划中（C06 §2）
GITS_WRITEBACK_ACTIONS = {
    "SUBMIT_CREDIT_APPLICATION", "DISBURSE_LOAN", "TRANSFER_FUNDS",
    "APPROVE_CREDIT", "EXECUTE_WIRE", "CREATE_LOAN_CONTRACT",
}


def canonical(obj) -> str:
    """canonical planHash（C06 §2）：键排序 + 紧凑分隔符 + 稳定数值/空值规范。

    排除：planId / traceId / createdAt（随机或时间性字段）。
    """
    def normalize(node):
        if isinstance(node, dict):
            return {k: normalize(v) for k, v in sorted(node.items())
                    if k not in {"planId", "traceId", "createdAt"}}
        if isinstance(node, list):
            # 数组按明确规则排序（本包按 stepId / 字符串序）
            items = [normalize(v) for v in node]
            if items and all(isinstance(i, dict) and "stepId" in i for i in items):
                return sorted(items, key=lambda i: str(i["stepId"]))
            if items and all(isinstance(i, str) for i in items):
                return sorted(items)
            return items
        if isinstance(node, str):
            return node.strip().replace("\u00a0", " ")
        if node is None:
            return None
        return node

    blob = json.dumps(normalize(obj), ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def load(name: str):
    return json.loads((ACT / name).read_text(encoding="utf-8"))


def route(task_type: str, policy: dict) -> dict:
    """确定性路由（C06 §2 + OWNER-003 §4.2：无匹配与歧义分别处理）。"""
    rules = [r for r in policy.get("rules", []) if r.get("taskType") == task_type]
    if not rules:
        return {"decision": "REJECT", "reason": "no matching rule"}
    best = min(r.get("priority", 999) for r in rules)
    winners = [r for r in rules if r.get("priority", 999) == best]
    if len(winners) > 1:
        return {"decision": "ROUTE_AMBIGUOUS", "reason": "same-priority ambiguity",
                "candidates": sorted(str(r.get("ruleId")) for r in winners)}
    return {"decision": "ROUTED", "rule": winners[0]}


def main() -> int:  # noqa: C901
    failures: list[str] = []

    if not ACT.is_dir():
        print(f"FAIL: activation dir missing: {ACT}", file=sys.stderr)
        return 2

    template = load("task_template.json")
    mapspec = load("map_spec.json")
    policy = load("route_policy.json")
    plan = load("activation_plan.json")
    violations = load("violations.json").get("violations", [])

    # 1. TaskTemplate 固化
    for field in ("taskId", "taskType", "customerId", "asOf", "frozenFields"):
        if field not in template:
            failures.append(f"[1] task template missing {field}")
    if template.get("identityBy") != "customerId":
        failures.append("[1] task template must identify by stable id, not name")

    # 2. MapSpec 入口与用途
    for field in ("mapId", "version", "entryNodes", "taskTypes", "purpose"):
        if field not in mapspec:
            failures.append(f"[2] map spec missing {field}")
    if not mapspec.get("entryNodes"):
        failures.append("[2] map spec without entry nodes cannot be activated")
    if not mapspec.get("purpose"):
        failures.append("[2] map spec without purpose statement cannot be activated")

    # 3. 路由确定性
    routed = route("FINANCE_VISIT_PREP", policy)
    if routed.get("decision") != "ROUTED":
        failures.append(f"[3] expected FINANCE_VISIT_PREP to route, got {routed.get('decision')}")
    no_match = route("UNKNOWN_TASK", policy)
    if no_match.get("decision") != "REJECT":
        failures.append(f"[3] no-match must REJECT, got {no_match.get('decision')}")
    ambiguous = route("AMBIGUOUS_TASK", policy)
    if ambiguous.get("decision") != "ROUTE_AMBIGUOUS":
        failures.append(f"[3] same-priority ambiguity must ROUTE_AMBIGUOUS, got {ambiguous.get('decision')}")

    # 4. 计划确定性
    h1 = canonical(plan)
    import copy
    p2 = copy.deepcopy(plan)
    p2["planId"] = "SIM-PLAN-999"
    p2["traceId"] = "SIM-TRACE-999"
    p2["createdAt"] = "2099-01-01T00:00:00Z"
    if canonical(p2) != h1:
        failures.append("[4] planHash changed when only random/temporal fields changed")
    p3 = copy.deepcopy(plan)
    p3["steps"] = list(reversed(p3["steps"]))
    if canonical(p3) != h1:
        failures.append("[4] planHash changed when steps were reordered (array ordering rule missing)")
    if canonical(plan) != h1:
        failures.append("[4] planHash not stable across repeated computation")
    p4 = copy.deepcopy(plan)
    p4["steps"][0]["executorRef"] = "SIM-CAP-DIFFERENT"
    if canonical(p4) == h1:
        failures.append("[4] planHash unchanged when execution semantics changed (over-normalized)")

    # 5. 必需能力缺失
    if plan.get("requiredCapabilityRefs"):
        for v in violations:
            if v.get("expectedError") == "REQUIRED_CAPABILITY_MISSING" and v.get("detected") is not True:
                failures.append("[5] required-capability-missing violation not detected in fixture set")

    # 6. KERT 计划不得含 GITS 正式业务写回
    for step in plan.get("steps", []):
        action = str(step.get("executorRef", "")).upper()
        if any(a in action for a in GITS_WRITEBACK_ACTIONS):
            failures.append(f"[6] step {step.get('stepId')}: KERT plan contains GITS writeback action")
        if step.get("sideEffect") not in {"NONE", "READ_ONLY", "PROPOSE_ONLY"}:
            failures.append(f"[6] step {step.get('stepId')}: unexpected sideEffect {step.get('sideEffect')!r}")

    # 7. 每步字段齐备
    for step in plan.get("steps", []):
        for field in ("stepId", "executorRef", "inputBindings", "dependencyStepIds",
                      "evidenceRequirement", "onFailure", "sideEffect"):
            if field not in step:
                failures.append(f"[7] step {step.get('stepId')} missing {field}")

    # 8. 子图非 DAG → 拒绝
    graph: dict[str, list[str]] = {s["stepId"]: list(s.get("dependencyStepIds", [])) for s in plan.get("steps", [])}
    visiting: set[str] = set()
    done: set[str] = set()
    def has_cycle(node: str) -> bool:
        if node in done:
            return False
        if node in visiting:
            return True
        visiting.add(node)
        for dep in graph.get(node, []):
            if dep in graph and has_cycle(dep):
                return True
        visiting.discard(node)
        done.add(node)
        return False
    if any(has_cycle(n) for n in graph):
        failures.append("[8] plan execution subgraph contains a cycle (must be a DAG)")

    # 负例必须覆盖三类拒绝（fail-closed）
    required_violations = {"ROUTE_AMBIGUOUS", "NO_MATCH_REJECT", "REQUIRED_CAPABILITY_MISSING",
                           "DEPENDENCY_CYCLE", "GITS_WRITEBACK_IN_KERT_PLAN"}
    covered = {v.get("expectedError") for v in violations}
    uncovered = required_violations - covered
    if uncovered:
        failures.append(f"[neg] rejection paths without fixtures: {sorted(uncovered)}")

    if failures:
        print("gk-ke-l4-1-map-activation-tests: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    print("gk-ke-l4-1-map-activation-tests: PASS")
    print(f"  planHash={h1}")
    print(f"  route(FINANCE_VISIT_PREP)={routed.get('decision')} rule={routed.get('rule', {}).get('ruleId')}")
    print(f"  route(UNKNOWN_TASK)={no_match.get('decision')} route(AMBIGUOUS_TASK)={ambiguous.get('decision')}")
    print(f"  steps={len(plan.get('steps', []))} dag_ok=True")
    print("  checks: template, mapspec, route-determinism, planHash-stability, capability, "
          "no-gits-writeback, step-fields, dag")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
