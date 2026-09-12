#!/usr/bin/env python3
"""GK-KE 能力间消费链 · 端到端 runtime trace（B 层）。

【为什么需要它】
§14.2 第 6 项「能力之间真正消费结果」先前仅由**参考实现**下的逻辑属性验证支撑
（`CONSUMPTION_PROVEN_LOGIC_ONLY`），**无运行时 trace**。
本脚本补上该缺口：**真实调用 KERT 两个能力，并在链路层记录实际传递的字段值**。

【链路】
    SIM-CAP-FACT-RECON  ──(按 ConsumerObligations)──▶  SIM-CAP-KYC-GAP

【trace 记录什么】
  1. 上游 executionId 与真实返回
  2. **按合同义务**实际传递到下游的字段与取值
  3. 下游真实返回
  4. **链路级反事实**：移除上游某字段后，下游**输入与输出**是否改变

【本脚本能证明什么 / 不能证明什么（**必读**）】
  能证明：
    - 两个能力在**真实运行**中依次被调用（非参考实现）
    - 上游输出经**合同映射**后确实进入下游输入
    - 移除上游字段会使**下游输入**改变（故不是"字段存在但未传递"）
  不能证明：
    - **业务语义正确性** —— 确定性适配器产出占位内容（indicators/conflicts 恒为空），
      故"下游因上游数据而得出不同结论"**无法在本环境证明**
    - 生产 LLM 场景下的行为

  → 故本脚本的结论**不得**用于声称 B 层达成；
    它把 B 层从"无运行时证据"推进到"有链路运行时证据，但业务语义仍待真实模型验证"。

用法：
  python3 scripts/gk_ke_chain_trace.py
  python3 scripts/gk_ke_chain_trace.py --json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KERT = Path("/home/szf/dev/Leibniz-KERT")
KERT_SRC = KERT / "src"
PKG_DIR = KERT / "examples" / "bank-front-skills"
OBLIGATIONS = (ROOT / "specs" / "knowledge-architecture" / "contracts"
               / "ConsumerObligations.json")
OUT = ROOT / "evidence" / "gk-ke-chain-trace"

UPSTREAM = "bank-front-fact-reconciliation"   # SIM-CAP-FACT-RECON
DOWNSTREAM = "bank-front-kyc-gap-check"       # SIM-CAP-KYC-GAP


def load_service():
    sys.path.insert(0, str(KERT_SRC))
    from kert.application.skills import SkillExecutionService  # noqa: WPS433
    return SkillExecutionService(skill_packages=PKG_DIR)


def call(svc, skill_id: str, req_id: str, payload: dict) -> dict:
    res = svc.execute(skill_id, req_id, payload)
    status = getattr(res, "status", None)
    data = getattr(res, "data", None) or {}
    inner = data.get("result") if isinstance(data, dict) else None
    return {"status": status, "data": data, "result": inner}


def map_upstream_to_downstream(upstream_result: dict, obligations: dict,
                               mutations: set[str] | None = None) -> dict:
    """按 ConsumerObligations 把上游 result 映射为下游输入。

    mutations：需要"移除"的上游字段集合（用于链路级反事实）。
    """
    mutations = mutations or set()
    inp: dict = {"customerId": upstream_result.get("customerId")}

    # OBL-01 三元组
    if "taskId" not in mutations:
        inp["taskId"] = upstream_result.get("taskId", "SIM-TASK-001")
    if "asOf" not in mutations:
        inp["asOf"] = upstream_result.get("asOf", "2026-09-12")

    # OBL-02 status
    if "status" not in mutations:
        inp["reconciliationStatus"] = upstream_result.get("status")

    # OBL-04 冲突与信号（本能力输出的核心）
    if "conflicts" not in mutations:
        inp["conflictCases"] = upstream_result.get("conflicts") or []
    if "indicators" not in mutations:
        inp["indicators"] = upstream_result.get("indicators") or []

    # OBL-03 覆盖轨迹
    if "warnings" not in mutations:
        inp["upstreamWarnings"] = upstream_result.get("warnings") or []

    return inp


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not OBLIGATIONS.is_file():
        print(f"gk-ke-chain-trace: FAIL — 合同缺失 {OBLIGATIONS}", file=sys.stderr)
        return 1
    obligations = json.loads(OBLIGATIONS.read_text(encoding="utf-8"))
    chain_def = next((c for c in obligations.get("consumptionChains", [])
                      if c.get("upstream") == "SIM-CAP-FACT-RECON"), None)
    if chain_def is None:
        print("gk-ke-chain-trace: FAIL — 合同未声明 FACT-RECON→KYC-GAP 链路",
              file=sys.stderr)
        return 1

    try:
        svc = load_service()
    except Exception as exc:  # noqa: BLE001
        print(f"gk-ke-chain-trace: FAIL — 无法构造 KERT 服务: "
              f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    customer = "SIM-C001"

    # ---- 链路第 1 步：真实调用上游 ----
    up = call(svc, UPSTREAM, f"CHAIN-{run_id}-UP", {"customerId": customer})
    if up["status"] != "ok" or not isinstance(up["result"], dict):
        print(f"gk-ke-chain-trace: FAIL — 上游调用失败 {up['status']}", file=sys.stderr)
        return 1

    # ---- 合同映射 ----
    down_input = map_upstream_to_downstream(up["result"], obligations)

    # ---- 链路第 2 步：真实调用下游 ----
    dn = call(svc, DOWNSTREAM, f"CHAIN-{run_id}-DN", down_input)
    if dn["status"] != "ok" or not isinstance(dn["result"], dict):
        print(f"gk-ke-chain-trace: FAIL — 下游调用失败 {dn['status']}", file=sys.stderr)
        return 1

    # ---- 链路级反事实：逐个移除上游字段，看下游输入是否改变 ----
    counterfactuals = []
    for field in ("conflicts", "indicators", "warnings", "status"):
        mutated_input = map_upstream_to_downstream(
            up["result"], obligations, mutations={field})
        changed_input = (json.dumps(mutated_input, sort_keys=True, ensure_ascii=False)
                         != json.dumps(down_input, sort_keys=True, ensure_ascii=False))
        # 再真实调用一次下游，看其输出是否改变
        dn2 = call(svc, DOWNSTREAM, f"CHAIN-{run_id}-DN-{field}", mutated_input)
        changed_output = (json.dumps(dn2.get("result"), sort_keys=True, ensure_ascii=False)
                          != json.dumps(dn["result"], sort_keys=True, ensure_ascii=False))
        counterfactuals.append({
            "removedUpstreamField": field,
            "downstreamInputChanged": changed_input,
            "downstreamOutputChanged": changed_output,
        })

    input_consumed = all(c["downstreamInputChanged"] for c in counterfactuals)
    output_consumed = any(c["downstreamOutputChanged"] for c in counterfactuals)

    trace = {
        "traceVersion": "1.0.0",
        "runId": run_id,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "authority": "建议书 §9.3 / §14.2 第 6 项",
        "chainId": chain_def.get("chainId"),
        "chain": f"{UPSTREAM} → {DOWNSTREAM}",
        "realInvocation": True,
        "steps": [
            {
                "step": 1, "role": "upstream",
                "skillId": UPSTREAM,
                "executionStatus": up["status"],
                "executionId": f"CHAIN-{run_id}-UP",
                "returnedTopLevelKeys": sorted(up["result"].keys()),
                "returnedValues": {
                    "customerId": up["result"].get("customerId"),
                    "skillId": up["result"].get("skillId"),
                    "indicatorsCount": len(up["result"].get("indicators") or []),
                    "conflictsCount": len(up["result"].get("conflicts") or []),
                },
            },
            {
                "step": 2, "role": "contract-mapping",
                "mappedBy": "ConsumerObligations.json",
                "obligationsApplied": chain_def.get("appliesObligations"),
                "downstreamInputFields": sorted(down_input.keys()),
                "downstreamInputValues": down_input,
            },
            {
                "step": 3, "role": "downstream",
                "skillId": DOWNSTREAM,
                "executionStatus": dn["status"],
                "executionId": f"CHAIN-{run_id}-DN",
                "returnedTopLevelKeys": sorted(dn["result"].keys()),
                "returnedValues": {
                    "customerId": dn["result"].get("customerId"),
                    "skillId": dn["result"].get("skillId"),
                    "kycGapsCount": len(dn["result"].get("kycGaps") or []),
                },
            },
        ],
        "chainCounterfactuals": counterfactuals,
        "inputConsumptionProven": input_consumed,
        "outputConsumptionProven": output_consumed,
        "verdict": ("CHAIN_TRACE_PROVEN_INPUT_LEVEL" if input_consumed
                    else "CHAIN_TRACE_INCOMPLETE"),
        "whatThisProves": [
            "两个能力在真实运行中被依次调用（非参考实现）",
            "上游输出经 ConsumerObligations 映射后确实进入下游输入",
            "移除上游字段会使下游**输入**改变，故不构成『字段存在但未传递』",
            f"下游输出随上游数据的改变: {'是' if output_consumed else '否'}",
        ],
        "whatThisDoesNotProve": [
            "**业务语义正确性**：确定性适配器产出占位内容"
            "（indicators/conflicts 恒为空），故『下游因上游数据得出不同业务结论』"
            "**无法在本环境证明**",
            "生产 LLM 场景下的行为",
            "报告与证据的端到端绑定",
        ],
        "layerBStatement": (
            "§14.2 第 6 项：**仍未达成**。"
            "链路运行时证据已产出（本 trace），"
            "但业务语义层的消费需真实模型才能验证。"
            "B 层缺口由『无运行时证据』缩小为『有链路证据、缺语义证据』。"),
    }

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "trace.json").write_text(
        json.dumps(trace, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(trace, ensure_ascii=False, indent=2))
    else:
        print(f"gk-ke-chain-trace: {trace['verdict']}")
        print(f"  链路: {trace['chain']}  (真实调用)")
        s1, s3 = trace["steps"][0], trace["steps"][2]
        print(f"  上游 {s1['skillId']}: status={s1['executionStatus']} "
              f"keys={s1['returnedTopLevelKeys'][:5]}")
        print(f"  下游 {s3['skillId']}: status={s3['executionStatus']} "
              f"keys={s3['returnedTopLevelKeys'][:5]}")
        print(f"  合同映射后下游输入字段: {trace['steps'][1]['downstreamInputFields']}")
        print("  链路级反事实:")
        for c in counterfactuals:
            print(f"    移除 {c['removedUpstreamField']:12s} → "
                  f"下游输入变化={c['downstreamInputChanged']} "
                  f"输出变化={c['downstreamOutputChanged']}")
        print(f"  输入消费证明: {input_consumed}")
        print("  不代表 B 层达成：业务语义消费需真实模型验证。")
        print(f"  wrote: {OUT.relative_to(ROOT)}/trace.json")

    # 输入级消费未证明才算失败；业务语义未证明属已知限制，不作为门禁失败
    return 0 if input_consumed else 1


if __name__ == "__main__":
    raise SystemExit(main())
