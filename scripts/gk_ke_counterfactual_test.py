#!/usr/bin/env python3
"""GK-KE 反事实检验（消费证明）v2.0.0。

【为什么重写】
v1.0.0 存在两个被独立 QA 指出的缺陷（经核验属实）：
  1. 定义了 `OBLIGATIONS` 路径但**从未 json.load 读取合同**，
     变异清单是**我在代码里硬编码**的。
  2. 下游 `downstream_gap_generation` 是**我手写的函数**，与合同**零运行时绑定**。

结果：它证明的是"我写的函数会对我写的变异作出反应"，
**不构成**"合同被系统消费"的证据。这属于**自我确认**。

【v2 的修法】
  1. **强制读取** `ConsumerObligations.json`；
  2. **变异从合同派生** —— 遍历 `obligations[].upstreamFields` 自动生成变异，
     不再硬编码；
  3. 若合同声明的义务在检验中**未被覆盖**，直接判 FAIL；
  4. 校验合同自身 `currentStatus` 与检验结论**不矛盾**。

【v2 的诚实边界】
本检验使用**参考下游实现**验证"字段被消费"这一**逻辑属性**，
**不证明** KERT 生产实现也消费这些字段。
故其结论**不得**单独用于声称 §14.2 第 6 项达成 ——
必须在结论中如实标注该限制。

用法：
  python3 scripts/gk_ke_counterfactual_test.py
  python3 scripts/gk_ke_counterfactual_test.py --json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OBLIGATIONS = (ROOT / "specs" / "knowledge-architecture" / "contracts"
               / "ConsumerObligations.json")
ENVELOPE = (ROOT / "specs" / "knowledge-architecture" / "contracts"
            / "CapabilityResultEnvelope.json")
OUT = ROOT / "evidence" / "gk-ke-counterfactual"


# ---------------------------------------------------------------------------
# 参考下游实现（**显式声明为参考实现，非生产实现**）
# ---------------------------------------------------------------------------
def downstream_gap_generation(upstream: dict) -> dict:
    """参考下游：由上游对账结果生成缺口清单。

    本函数是**参考实现**，用于验证字段被消费这一逻辑属性。
    它按 §9.3 七行消费表实现，但**不构成** KERT 生产实现的证据。
    """
    out: dict = {"gaps": [], "coverage": None, "status": None}

    if not (upstream.get("taskId") and upstream.get("entityId")
            and upstream.get("asOf")):
        out["status"] = "REJECT_CONSUMPTION"
        return out
    out["status"] = "CONSUMED"

    status = upstream.get("status")
    execution_done = status == "SUCCESS"
    if status in ("FAILED", "NOT_RUN", None):
        out["gaps"].append({"reason": "COVERAGE_INSUFFICIENT"})

    rule_trace = upstream.get("ruleTrace")
    if rule_trace is None:
        out["coverage"] = "UNKNOWN_NOT_REPORTED"
        out["gaps"].append({"reason": "COVERAGE_NOT_REPORTED"})
    else:
        covered = set(rule_trace.get("coveredRules") or [])
        expected = set(rule_trace.get("expectedRules") or [])
        missing = expected - covered
        if missing:
            out["coverage"] = "INSUFFICIENT"
            out["gaps"].append({"reason": "MISSING_RULES", "detail": sorted(missing)})
        elif not expected:
            out["coverage"] = "UNKNOWN_EMPTY_EXPECTED"
            out["gaps"].append({"reason": "COVERAGE_NOT_REPORTED"})
        else:
            out["coverage"] = "SUFFICIENT"

    result = upstream.get("result") or {}
    conflicts = result.get("conflictCases") or []
    signals = result.get("signals") or []
    if execution_done and out["coverage"] == "SUFFICIENT":
        for c in conflicts:
            out["gaps"].append({"reason": "CONFLICT", "detail": c})
        for s in signals:
            out["gaps"].append({"reason": "SIGNAL", "detail": s})
    elif not conflicts and not signals:
        out["gaps"].append({"reason": "UNVERIFIED_EMPTY"})

    # OBL-05：指标引用不可用则不能引用该结论。
    # "未报告"与"报告了完整集合"必须区分（否则"未执行"会被当成"无问题"）。
    refs = result.get("comparedMetricRefs")
    if refs is None or len(refs) == 0:
        out["gaps"].append({"reason": "METRIC_REFS_NOT_REPORTED"})
    else:
        for r in refs:
            if not all(k in r for k in ("metricId", "version", "grain")):
                out["gaps"].append({"reason": "METRIC_REF_INCOMPLETE"})

    # OBL-06：无依据的解释保留为假设，不关闭问题。
    # 同理：未报告解释 与 报告了空集合 都不得视为"无异常"。
    exps = result.get("explanations")
    if exps is None or len(exps) == 0:
        out["gaps"].append({"reason": "NO_EXPLANATIONS_REPORTED"})
    else:
        for e in exps:
            if not e.get("evidenceRefs"):
                out["gaps"].append({"reason": "HYPOTHESIS_ONLY"})

    # OBL-06（顶层 evidenceRefs）：上游未提供任何证据引用，
    # 下游结论不得被当作已证实。
    if not upstream.get("evidenceRefs"):
        out["gaps"].append({"reason": "NO_UPSTREAM_EVIDENCE"})

    out["requiredQuestions"] = list(result.get("requiredQuestions") or [])
    return out


def base_upstream() -> dict:
    return {
        "taskId": "SIM-TASK-001", "entityId": "SIM-C001",
        "purpose": "FINANCE_VISIT_PREP", "asOf": "2026-09-12",
        "status": "SUCCESS",
        "ruleTrace": {"expectedRules": ["R01", "R03"], "coveredRules": ["R01", "R03"]},
        "result": {
            "conflictCases": [{"id": "XC-1"}],
            "signals": [{"id": "SIG-1"}],
            "comparedMetricRefs": [{"metricId": "M01", "version": "1.0.0",
                                    "grain": "CustomerPerPeriod"}],
            "explanations": [{"name": "税收优惠", "evidenceRefs": ["EV-1"]}],
            "requiredQuestions": ["营收与开票口径是否一致？"],
        },
        "evidenceRefs": ["EV-1"], "limitations": [],
    }


def apply_field_mutation(u: dict, field: str) -> bool:
    """按合同声明的 upstreamFields 生成变异。返回是否成功施加。"""
    parts = field.split(".")
    # 定位父容器
    cur = u
    for p in parts[:-1]:
        if p not in cur or not isinstance(cur[p], dict):
            return False
        cur = cur[p]
    leaf = parts[-1]
    if leaf not in cur:
        return False
    val = cur[leaf]
    if isinstance(val, list):
        cur[leaf] = []                      # 清空
    elif isinstance(val, dict):
        cur.pop(leaf)                       # 移除
    elif isinstance(val, str):
        cur.pop(leaf)                       # 移除字符串字段
    else:
        cur.pop(leaf)
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    failures: list[str] = []

    # --- v2 关键：强制读取合同 ---
    if not OBLIGATIONS.is_file():
        print(f"gk-ke-counterfactual-test: FAIL — 合同缺失 {OBLIGATIONS}",
              file=sys.stderr)
        return 1
    contract = json.loads(OBLIGATIONS.read_text(encoding="utf-8"))
    obligations = contract.get("obligations", [])
    if not obligations:
        print("gk-ke-counterfactual-test: FAIL — 合同未声明任何义务",
              file=sys.stderr)
        return 1

    envelope = json.loads(ENVELOPE.read_text(encoding="utf-8")) \
        if ENVELOPE.is_file() else {}
    envelope_fields = {f["name"] for f in envelope.get("fields", [])}

    base = base_upstream()
    base_out = downstream_gap_generation(json.loads(json.dumps(base)))

    results = []
    consumed = 0
    skipped = []

    for obl in obligations:
        obl_id = obl.get("id")
        for field in obl.get("upstreamFields", []):
            # 合同字段须在 envelope 中登记（交叉校验两份合同）
            root_field = field.split(".")[0]
            if envelope_fields and root_field not in envelope_fields:
                failures.append(
                    f"{obl_id} 声明的字段 {field} 未在 CapabilityResultEnvelope 中登记")
                continue

            variant = json.loads(json.dumps(base))
            applied = apply_field_mutation(variant, field)
            if not applied:
                skipped.append({"obligationId": obl_id, "field": field,
                                "reason": "基座样例中无该字段，无法施加变异"})
                continue
            v_out = downstream_gap_generation(variant)
            changed = (json.dumps(v_out, sort_keys=True, ensure_ascii=False)
                       != json.dumps(base_out, sort_keys=True, ensure_ascii=False))
            results.append({
                "obligationId": obl_id, "field": field,
                "downstreamOutputChanged": changed,
                "verdict": "CONSUMED" if changed else "NOT_CONSUMED",
                "onMissingInContract": (obl.get("onMissing") or {}).get("behavior"),
            })
            if changed:
                consumed += 1

    # 覆盖完整性：合同每条义务都应有至少一个被检验的字段
    covered_obls = {r["obligationId"] for r in results}
    for obl in obligations:
        if obl.get("id") not in covered_obls:
            failures.append(f"合同义务 {obl.get('id')} 未被任何变异覆盖")

    total = len(results)
    all_consumed = total > 0 and consumed == total

    # --- 与合同自身 currentStatus 交叉校验（防自相矛盾）---
    cstatus = contract.get("currentStatus", {})
    if cstatus.get("runtimeTraceExists") is False and all_consumed:
        contract_note = ("合同自身声明 runtimeTraceExists=false；"
                         "本检验为**参考实现**下的逻辑属性验证，"
                         "**不得**据此认为该字段应被改为 true。")
    else:
        contract_note = None

    summary = {
        "probeVersion": "2.0.0",
        "authority": "建议书 §9.3 / §9.4 / §14.2",
        "method": "反事实检验（变异由 ConsumerObligations.json 驱动）",
        "contractLoaded": str(OBLIGATIONS.relative_to(ROOT)),
        "obligationsInContract": len(obligations),
        "mutationsExecuted": total,
        "consumedCount": consumed,
        "notConsumedCount": total - consumed,
        "skippedMutations": skipped,
        "referenceImplementation": True,
        "referenceImplementationNote": (
            "下游为**参考实现**，验证的是「字段被消费」这一逻辑属性，"
            "**不证明** KERT 生产实现也消费这些字段。"),
        "contractCrossCheck": contract_note,
        "verdict": "CONSUMPTION_PROVEN_LOGIC_ONLY" if all_consumed else "CONSUMPTION_PARTIAL",
        "oc04Impact": (
            "§14.2 第 6 项**不得**据此单独声称达成 —— 本检验仅证明逻辑属性，"
            "运行时 trace 仍缺失（见合同 currentStatus.runtimeTraceExists=false）"
            if all_consumed else
            "§14.2 第 6 项未达成"),
    }

    if args.json:
        print(json.dumps({"summary": summary, "results": results,
                          "failures": failures}, ensure_ascii=False, indent=2))
    else:
        print(f"gk-ke-counterfactual-test: {summary['verdict']}")
        print(f"  合同已读取: {summary['contractLoaded']}（{len(obligations)} 条义务）")
        print(f"  变异 {total} 项（由合同驱动），被消费 {consumed}，未消费 {total - consumed}")
        for r in results:
            mark = "CONSUMED" if r["downstreamOutputChanged"] else "NOT-CONS"
            print(f"  [{mark:8s}] {r['obligationId']:7s} {r['field']}")
        if skipped:
            print(f"  跳过 {len(skipped)} 项（基座无该字段）")
        if contract_note:
            print(f"  合同交叉校验: {contract_note}")
        print(f"  OC-04 影响: {summary['oc04Impact']}")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "report.json").write_text(
        json.dumps({"summary": summary, "results": results,
                    "failures": failures}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")

    if failures:
        print("gk-ke-counterfactual-test: FAIL", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
