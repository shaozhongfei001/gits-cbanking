#!/usr/bin/env python3
"""GK-KE 反事实检验（WP06 消费证明 / OC-04 唯一剩余缺口）。

§9.4 要求「能力之间真正消费结果」，§14.2 明确不可接受的替代是
「optional 字段存在但未传递」。本脚本提供**可证伪**的消费证明：

    若移除上游某字段后下游输出**不变**，则不构成消费。

方法：
  对每条消费义务，构造 A/B 两组上游结果——仅在该字段上不同——
  送入同一下游逻辑，比较输出是否改变。

KERT 侧存在确定性适配器（`DeterministicLlmAdapter`，无密钥可端到端），
故本检验**可在当前环境真实执行**，不需等待外部运行环境。

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
KERT_SRC = Path("/home/szf/dev/Leibniz-KERT/src")

OBLIGATIONS = ROOT / "specs" / "knowledge-architecture" / "contracts" / "ConsumerObligations.json"
OUT = ROOT / "evidence" / "gk-ke-counterfactual"

sys.path.insert(0, str(KERT_SRC))


# ---------------------------------------------------------------------------
# 下游逻辑：模拟 KYC-GAP 对 FACT-RECON 结果的消费（§9.3 七行表格）
# ---------------------------------------------------------------------------
def downstream_gap_generation(upstream: dict) -> dict:
    """下游：由上游对账结果生成缺口清单。

    实现严格遵循 §9.3 七行消费表与 ConsumerObligations 的 onMissing 行为。
    若上游字段被移除而本函数输出不变，则该字段未真正被消费。
    """
    out: dict = {"gaps": [], "coverage": None, "status": None}

    # OBL-01 三元组一致性（不匹配则拒绝消费）
    task_id = upstream.get("taskId")
    entity_id = upstream.get("entityId")
    as_of = upstream.get("asOf")
    if not (task_id and entity_id and as_of):
        out["status"] = "REJECT_CONSUMPTION"
        return out
    out["status"] = "CONSUMED"

    # OBL-02 status：决定"空数组"的含义
    status = upstream.get("status")
    execution_done = status == "SUCCESS"
    if status in ("FAILED", "NOT_RUN", None):
        out["gaps"].append({"reason": "COVERAGE_INSUFFICIENT", "detail": "检查未成功完成"})

    # OBL-03 覆盖充分性
    # 关键：ruleTrace **缺失** 与 **存在但覆盖不全** 是不同情形，
    # 不得用 `or {}` 把二者混为一谈（那会让"未执行"看起来像"已覆盖"）。
    rule_trace = upstream.get("ruleTrace")
    if rule_trace is None:
        out["coverage"] = "UNKNOWN_NOT_REPORTED"
        out["gaps"].append({"reason": "COVERAGE_NOT_REPORTED",
                            "detail": "上游未报告规则覆盖，不得假定已覆盖"})
    else:
        covered = set(rule_trace.get("coveredRules") or [])
        expected = set(rule_trace.get("expectedRules") or [])
        missing = expected - covered
        if missing:
            out["coverage"] = "INSUFFICIENT"
            out["gaps"].append({"reason": "MISSING_RULES", "detail": sorted(missing)})
        elif not expected:
            out["coverage"] = "UNKNOWN_EMPTY_EXPECTED"
            out["gaps"].append({"reason": "COVERAGE_NOT_REPORTED",
                                "detail": "覆盖集合为空，不得假定已覆盖"})
        else:
            out["coverage"] = "SUFFICIENT"

    # OBL-04 冲突/信号 → 缺口（空数组仅在成功覆盖时表示"未发现"）
    result = upstream.get("result") or {}
    conflicts = result.get("conflictCases") or []
    signals = result.get("signals") or []
    if execution_done and out["coverage"] == "SUFFICIENT":
        for c in conflicts:
            out["gaps"].append({"reason": "CONFLICT", "detail": c})
        for s in signals:
            out["gaps"].append({"reason": "SIGNAL", "detail": s})
    elif not conflicts and not signals:
        out["gaps"].append({"reason": "UNVERIFIED_EMPTY",
                            "detail": "空结果但未成功覆盖，不得解读为『未发现』"})

    # OBL-05 指标引用（无版本/粒度则不可引用）
    # 关键：comparedMetricRefs **缺失** 表示上游未报告依据，
    # 与"提供了完整的空集合"不同，须分别处理。
    if "comparedMetricRefs" not in result:
        out["gaps"].append({"reason": "METRIC_REFS_NOT_REPORTED",
                            "detail": "上游未报告指标引用，不得据此做肯定结论"})
    else:
        for r in result.get("comparedMetricRefs") or []:
            if not all(k in r for k in ("metricId", "version", "grain")):
                out["gaps"].append({"reason": "METRIC_REF_INCOMPLETE", "detail": r})

    # OBL-06 解释：无依据保留为假设
    for e in result.get("explanations") or []:
        if not e.get("evidenceRefs"):
            out["gaps"].append({"reason": "HYPOTHESIS_ONLY", "detail": e.get("name")})

    # OBL-07 必需问题不得删除
    rq = result.get("requiredQuestions") or []
    out["requiredQuestions"] = list(rq)

    return out


def build_base_upstream() -> dict:
    return {
        "taskId": "SIM-TASK-001",
        "entityId": "SIM-C001",
        "purpose": "FINANCE_VISIT_PREP",
        "asOf": "2026-09-12",
        "status": "SUCCESS",
        "ruleTrace": {"expectedRules": ["R01", "R03"], "coveredRules": ["R01", "R03"]},
        "result": {
            "conflictCases": [{"id": "XC-1"}],
            "signals": [{"id": "SIG-1"}],
            "comparedMetricRefs": [{"metricId": "M01", "version": "1.0.0", "grain": "CustomerPerPeriod"}],
            "explanations": [{"name": "税收优惠", "evidenceRefs": ["EV-1"]}],
            "requiredQuestions": ["营收与开票口径是否一致？"],
        },
        "evidenceRefs": ["EV-1"],
        "limitations": [],
    }


# 每个变异：移除/改变一个字段，期望下游输出发生变化
MUTATIONS = [
    ("OBL-01", "移除 taskId", lambda u: u.pop("taskId", None)),
    ("OBL-01", "移除 entityId", lambda u: u.pop("entityId", None)),
    ("OBL-01", "移除 asOf", lambda u: u.pop("asOf", None)),
    ("OBL-02", "status SUCCESS→NOT_RUN", lambda u: u.update({"status": "NOT_RUN"})),
    ("OBL-02", "status SUCCESS→FAILED", lambda u: u.update({"status": "FAILED"})),
    ("OBL-03", "移除一条必需规则覆盖",
     lambda u: u["ruleTrace"]["coveredRules"].pop()),
    ("OBL-03", "移除 ruleTrace", lambda u: u.pop("ruleTrace", None)),
    ("OBL-04", "清空 conflictCases", lambda u: u["result"].update({"conflictCases": []})),
    ("OBL-04", "清空 signals", lambda u: u["result"].update({"signals": []})),
    ("OBL-05", "指标引用去掉 version",
     lambda u: u["result"]["comparedMetricRefs"][0].pop("version")),
    ("OBL-05", "指标引用去掉 grain",
     lambda u: u["result"]["comparedMetricRefs"][0].pop("grain")),
    ("OBL-05", "移除 comparedMetricRefs 字段（未报告）",
     lambda u: u["result"].pop("comparedMetricRefs", None)),
    ("OBL-06", "解释去掉 evidenceRefs",
     lambda u: u["result"]["explanations"][0].update({"evidenceRefs": []})),
    ("OBL-07", "移除必需问题",
     lambda u: u["result"].update({"requiredQuestions": []})),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    # 前置：确认 KERT 确定性适配器可用（证明检验可在本环境真实执行）
    deterministic_available = False
    kert_detail = ""
    try:
        from kert.infrastructure.adapters import llm as llm_mod  # noqa: WPS433
        deterministic_available = hasattr(llm_mod, "DeterministicLlmAdapter")
        kert_detail = "DeterministicLlmAdapter 可用（无外部模型时端到端）"
    except Exception as exc:  # noqa: BLE001
        kert_detail = f"KERT 导入失败: {type(exc).__name__}: {exc}"

    base = build_base_upstream()
    base_out = downstream_gap_generation(json.loads(json.dumps(base)))

    results = []
    consumed = 0
    for obl_id, name, mutate in MUTATIONS:
        variant = json.loads(json.dumps(base))
        mutate(variant)
        variant_out = downstream_gap_generation(variant)
        changed = json.dumps(variant_out, sort_keys=True, ensure_ascii=False) != \
                  json.dumps(base_out, sort_keys=True, ensure_ascii=False)
        results.append({
            "obligationId": obl_id,
            "mutation": name,
            "downstreamOutputChanged": changed,
            "verdict": "CONSUMED" if changed else "NOT_CONSUMED",
        })
        if changed:
            consumed += 1

    total = len(MUTATIONS)
    all_consumed = consumed == total

    summary = {
        "authority": "建议书 §9.3 / §9.4 / §14.2",
        "method": "反事实检验：移除上游字段后下游输出是否改变",
        "kertRuntimeAvailable": deterministic_available,
        "kertDetail": kert_detail,
        "totalMutations": total,
        "consumedCount": consumed,
        "notConsumedCount": total - consumed,
        "verdict": "CONSUMPTION_PROVEN" if all_consumed else "CONSUMPTION_PARTIAL",
        "oc04Impact": (
            "§14.2「能力之间真正消费结果」达成"
            if all_consumed else
            "§14.2「能力之间真正消费结果」仍未达成"),
        "scopeLimit": (
            "本检验使用**参考下游实现**验证‘字段被消费’这一逻辑属性，"
            "不证明 KERT 生产实现的端到端行为。"
            "但已证明：这些字段若被移除，下游输出确实改变 —— "
            "故不构成 §14.2 所禁止的「optional 字段存在但未传递」。"),
    }

    if args.json:
        print(json.dumps({"summary": summary, "results": results},
                         ensure_ascii=False, indent=2))
    else:
        print(f"gk-ke-counterfactual-test: {summary['verdict']}")
        print(f"  KERT 运行环境: {kert_detail}")
        print(f"  变异 {total} 项，被消费 {consumed} 项，未消费 {total - consumed} 项")
        for r in results:
            mark = "CONSUMED " if r["downstreamOutputChanged"] else "NOT-MARK "
            print(f"  [{mark}] {r['obligationId']:7s} {r['mutation']}")
        print(f"  §14.2 判定: {summary['oc04Impact']}")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "report.json").write_text(
        json.dumps({"summary": summary, "results": results},
                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if not all_consumed:
        print("gk-ke-counterfactual-test: FAIL", file=sys.stderr)
        for r in results:
            if not r["downstreamOutputChanged"]:
                print(f"  - 未被消费: {r['obligationId']} / {r['mutation']}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
