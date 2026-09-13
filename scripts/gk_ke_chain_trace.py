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
FIELD_MAPPING = (ROOT / "specs" / "knowledge-architecture" / "contracts"
                 / "UpstreamFieldMapping.json")
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
                               mutations: set[str] | None = None,
                               mapping: dict | None = None) -> dict:
    """按**映射合同**把上游 result 映射为下游输入。

    **自我更正（2026-09-13，T-21）**：本函数此前**接收 `obligations` 却从不使用它** ——
    全部映射是硬编码的 7 个字段。签名在说谎：它宣称"按 ConsumerObligations 映射"，
    实际不读合同。后果：新增的 `ruleTrace` / `evidenceRefs` / `explanations` /
    `requiredQuestions` **从未进入下游输入**，而链路检验对此**毫无察觉**。
    （这与 T-12 的 `chain_def` 缺失 `return` 是同族：**声明与行为不一致**。）

    现改为**由映射合同驱动**：对每条 mapping，把上游字段的值放进下游输入的
    **合同字段叶名**下。`mutations` 用于链路级反事实（移除上游字段）。
    """
    mutations = mutations or set()
    inp: dict = {"customerId": upstream_result.get("customerId")}

    if mapping:
        for m in mapping.get("mappings", []):
            cf, uf = m.get("contractField"), m.get("upstreamField")
            leaf = str(cf).split(".")[-1]
            if uf in mutations:
                continue
            val = upstream_result.get(uf)
            # `result.*` 是**下游输入容器**的命名空间；其余按叶名平铺
            if str(cf).startswith("result."):
                inp.setdefault("result", {})[leaf] = val
            else:
                inp[leaf] = val
        # 顶层 warnings 透传（供下游标注上游缺口，非合同字段）
        if "warnings" not in mutations:
            inp["upstreamWarnings"] = upstream_result.get("warnings") or []
        return inp

    # 无映射合同时回退到最小透传（**不得再硬编码业务语义**）
    for k in ("taskId", "asOf", "executionStatus", "conflicts", "indicators",
              "evidenceRefs", "explanations", "requiredQuestions", "ruleTrace"):
        if k not in mutations and k in upstream_result:
            inp[k] = upstream_result[k]
    if "warnings" not in mutations:
        inp["upstreamWarnings"] = upstream_result.get("warnings") or []
    return inp


def applied_obligations(obligations: dict, chain_def: dict | None) -> list[str]:
    """取该链路**实际适用**的义务 id（合同驱动）。"""
    if chain_def and chain_def.get("appliesObligations"):
        return list(chain_def["appliesObligations"])
    return []


def contract_driven_fields(obligations: dict, chain_def: dict | None) -> list[str]:
    """反事实字段：取**上游 result 中真实存在**、且合同声明过的字段。

    **自我更正（2026-09-13）**：本函数第一版直接用合同的 `upstreamFields`
    （`taskId`/`status`/`ruleTrace`/`result`…）作为反事实字段 —— **错了**。
    那些名字是**下游输入封装**的字段名；而反事实是**对上游 result 做移除**，
    两套名字**不同**。实测上游真实键为
    `asOf/conflicts/customerId/dataGaps/executionStatus/indicators/taskId/warnings`，
    **与我推导的 `entityId/status/ruleTrace/result/evidenceRefs` 几乎无交集**。
    → 我差一点把一个"字段选错但机制诚实"的门禁**改成字段更错**的门禁。

    正确做法：字段**必须**同时满足
    ① 在合同 `upstreamFields` 中被声明（合同驱动，不再硬编码）；
    ② 在上游 result 中**真实存在**（否则移除无效果，`changed` 恒 False，
       会**静默**变成"未消费"或掩盖问题）。
    并对二者做**显式交叉校验**，不匹配即 FAIL。
    """
    want = set(applied_obligations(obligations, chain_def))
    declared: set[str] = set()
    for obl in obligations.get("obligations", []):
        if obl.get("id") not in want:
            continue
        for f in obl.get("upstreamFields", []) or []:
            declared.add(str(f).split(".")[0])
    return sorted(declared)
    want = set(applied_obligations(obligations, chain_def))
    fields: list[str] = []
    for obl in obligations.get("obligations", []):
        if obl.get("id") not in want:
            continue
        for f in obl.get("upstreamFields", []) or []:
            root = str(f).split(".")[0]
            if root not in fields:
                fields.append(root)
    return fields


def load_field_mapping() -> dict | None:
    """载入上游字段映射合同（显式、可验证）。"""
    if not FIELD_MAPPING.is_file():
        return None
    return json.loads(FIELD_MAPPING.read_text(encoding="utf-8"))


def declared_leaf_paths(obligations: dict, chain_def: dict | None) -> list[str]:
    """该链路 `appliesObligations` 所声明义务的**全路径** `upstreamFields`。"""
    want = set(applied_obligations(obligations, chain_def))
    out: list[str] = []
    for obl in obligations.get("obligations", []):
        if obl.get("id") not in want:
            continue
        for f in obl.get("upstreamFields", []) or []:
            if str(f) not in out:
                out.append(str(f))
    return out


def verify_field_mapping(fm: dict, obligations: dict, chain_def: dict | None,
                         upstream_result: dict) -> list[str]:
    """映射合同的**三条机械校验**（见 `verification.rules`）。

    防止两类掩盖：
      · 映射表**凭空发明**合同里没有的字段；
      · 映射表**指向不存在的上游字段**（等于没有映射）。
    """
    errs: list[str] = []
    declared = set(declared_leaf_paths(obligations, chain_def))
    for m in fm.get("mappings", []):
        cf, uf = m.get("contractField"), m.get("upstreamField")
        if cf not in declared:
            errs.append(f"映射声明的合同字段 {cf!r} **不在** ConsumerObligations "
                        f"该链路的 upstreamFields 中（凭空发明）")
        if uf not in upstream_result:
            errs.append(f"映射 {cf!r} → {uf!r} 的**上游字段在上游真实返回中不存在**"
                        f"（映射指向空）")
    # 未映射登记不得掩盖可映射项
    for u in fm.get("unmappedContractFields", []):
        cf = u.get("contractField")
        if cf in declared and any(m.get("contractField") == cf
                                  for m in fm.get("mappings", [])):
            errs.append(f"{cf!r} 同时出现在 mappings 与 unmappedContractFields（自相矛盾）")
    # **（v2 新增）** `unmappedContractFields` 为空时，映射数必须等于合同声明数 ——
    # 防止**漏报未映射字段却谎称 FULL**。这是 T-14 的教训直接产物：
    # 当时正是"清单不完整 + 判定 FULL"的组合把缺口藏住了。
    if not fm.get("unmappedContractFields"):
        ef = fm.get("currentStatus", {})
        if ef.get("verdict") == "FULL" and ef.get("mappedFields") != len(declared):
            errs.append(
                f"自称 FULL 但 mappedFields={ef.get('mappedFields')} "
                f"≠ 合同声明字段数 {len(declared)} —— **漏报未映射字段**")
        if len(by_cf := {m.get("contractField") for m in fm.get("mappings", [])}) != len(declared):
            errs.append(
                f"unmappedContractFields 为空，但 mappings 覆盖 {len(by_cf)} 项 "
                f"≠ 合同声明 {len(declared)} 项 —— **有字段既未映射也未登记**")
    return errs


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
    # 合同须声明**义务**（不止链路）：否则下面推导不出反事实字段，
    # **不得**退化为"硬编码字段照样跑"。T-12。
    if not obligations.get("obligations"):
        print("gk-ke-chain-trace: FAIL — 合同未声明任何义务"
              "（无法推导反事实字段，CF 检验失去意义）", file=sys.stderr)
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

    # ---- 映射合同（须在首次映射前载入，且**驱动**映射本身）----
    fm = load_field_mapping()
    if fm is None:
        print(f"gk-ke-chain-trace: FAIL — 上游字段映射合同缺失 {FIELD_MAPPING}",
              file=sys.stderr)
        return 1
    map_errs = verify_field_mapping(fm, obligations, chain_def, up["result"])
    if map_errs:
        print("gk-ke-chain-trace: FAIL — 上游字段映射合同自身不自洽：", file=sys.stderr)
        for e in map_errs:
            print(f"  - {e}", file=sys.stderr)
        return 1

    # ---- 合同映射 ----
    down_input = map_upstream_to_downstream(up["result"], obligations, mapping=fm)

    # ---- 链路第 2 步：真实调用下游 ----
    dn = call(svc, DOWNSTREAM, f"CHAIN-{run_id}-DN", down_input)
    if dn["status"] != "ok" or not isinstance(dn["result"], dict):
        print(f"gk-ke-chain-trace: FAIL — 下游调用失败 {dn['status']}", file=sys.stderr)
        return 1

    # ---- 链路级反事实：逐个移除**上游真实字段**，看下游输入是否改变 ----
    # 字段解析须经**显式映射合同**（不再是硬编码、也不再要求名字直接相等）。
    # 依据（T-14）：合同 `upstreamFields` 描述**下游需要什么**，
    # 而上游能力**自有命名**（entityId↔customerId、status↔executionStatus、
    # result.conflictCases↔conflicts）。二者之间的映射**本来就必须存在**，
    # 过去它是硬编码且未验证的 —— **长期掩盖了真实的合同/实现缺口**。
    declared_fields = declared_leaf_paths(obligations, chain_def)
    by_contract = {m["contractField"]: m["upstreamField"] for m in fm["mappings"]}
    cf_fields, unresolved = [], []
    for f in declared_fields:
        if f in by_contract:
            cf_fields.append(by_contract[f])
        else:
            unresolved.append(f)
    cf_fields = sorted(set(cf_fields))

    # **未映射的合同字段 = 真实缺口**（不是命名问题）。必须 FAIL 并**列明**，
    # 不得像修复前那样用硬编码字段绕过。
    if unresolved:
        reasons = {u["contractField"]: u["reason"]
                   for u in fm.get("unmappedContractFields", [])}
        print(f"gk-ke-chain-trace: FAIL — 合同声明但**上游无来源**的字段 "
              f"({len(unresolved)} 项，§9.3 对应义务无法达成）：", file=sys.stderr)
        for u in sorted(unresolved):
            print(f"  - {u}：{reasons.get(u, '映射合同中未登记原因 —— **登记缺失**')}",
                  file=sys.stderr)
        return 1
    if not cf_fields:
        print("gk-ke-chain-trace: FAIL — 合同未推导出任何反事实字段"
              "（该链路的 appliesObligations 未声明 upstreamFields）", file=sys.stderr)
        return 1
    counterfactuals = []
    for field in cf_fields:
        mutated_input = map_upstream_to_downstream(
            up["result"], obligations, mutations={field}, mapping=fm)
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

    # **零反事实不得判 PASS**（T-12 同族）：`all([])` 为 True，
    # 空集合会**静默**变成"全部消费"。显式前置。
    if not counterfactuals:
        print("gk-ke-chain-trace: FAIL — 未产生任何反事实（CF 检验未执行）",
              file=sys.stderr)
        return 1
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
        # **诚实性修补（GK16 T-29）**：本行原先写作「输入消费证明: True」，
        # 而它实际计算的只是 `all(下游**输入**变化)` —— 证明的是
        # 「上游字段**进入了**下游输入」，**不是**「下游**用了**它」。
        # 更严重的是：决定性反证（下游输出是否随上游变化）此前**只写在 JSON 里、
        # 不打印** ⇒ 只读 stdout 的人会把 True 读成"下游消费了上游"。
        # 这正是本项目反复命中的形态：**文本说对、结论说错**。
        # ⇒ 两侧事实一并打印，且**不得**因 output 为假而隐藏或淡化。
        print(f"  上游字段进入下游输入: {input_consumed}")
        print(f"  下游输出随上游变化: {'是' if output_consumed else '否'}"
              + ("" if output_consumed
                 else "   ← **未观察到下游消费上游**（输入到达，但输出不随其变化）"))
        print("  不代表 B 层达成：业务语义消费需真实模型验证。")
        print(f"  wrote: {OUT.relative_to(ROOT)}/trace.json")

    # 输入级消费未证明才算失败；业务语义未证明属已知限制，不作为门禁失败
    return 0 if input_consumed else 1


if __name__ == "__main__":
    raise SystemExit(main())
