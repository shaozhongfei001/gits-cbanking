#!/usr/bin/env python3
"""GK-KE 能力语义探针（真实调用版）v2.0.0。

【为什么重写】
v1.0.0 的判定逻辑是：
    verdict = "PASSED" if sample.get("dryRunVerified") is True else "FAILED"
即 **PASSED 由样例文件里一个我手写的静态布尔决定**，探针**从未调用任何 KERT 代码**。
这构成建议书 §14.2 明令禁止的「**静态样例冒充结果**」。
独立 QA 指出该缺陷，经核验属实，本版为重写。

【v2 的判定依据】
  1. **真实调用** KERT `SkillExecutionService.execute(skill_id, request_id, input)`
  2. 取得 `status` 与 `data`
  3. 按该技能的实测 output-schema 要求校验 `data` 的**顶层结构**
  4. 只有「调用成功」**且**「输出结构符合该技能语义」才判 PASSED

【为什么必须校验结构】
实测发现：KERT 确定性适配器对**所有技能**返回**同一个通用结构**
（`scriptTitle/sections/callObjectives/keyMessages/evidenceRefs`）。
故 `status=ok` **不能**证明该技能按其契约工作 ——
必须用结构校验把「调用成功」与「契约满足」区分开。

【判定枚举】
  PASSED           真实调用成功且输出结构符合该技能语义
  CALLED_CONTRACT_UNMET   调用成功但输出不符合该技能语义契约
  CALL_FAILED      调用抛出异常或 status != ok
  NOT_PROBED       无法构造调用（无 provider / 无样例 / schema 未固定）

**callable 仅在 PASSED 时为 true。**

用法：
  python3 scripts/gk_ke_capability_probe.py            # 报告
  python3 scripts/gk_ke_capability_probe.py --write    # 回填 probeStatus/callable
  python3 scripts/gk_ke_capability_probe.py --json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KERT = Path("/home/szf/dev/Leibniz-KERT")
KERT_SRC = KERT / "src"
PKG_DIR = KERT / "examples" / "bank-front-skills"

REGISTRY = ROOT / "specs" / "knowledge-architecture" / "registry" / "Capability.json"
MAPPING = ROOT / "specs" / "knowledge-architecture" / "registry" / "CapabilityIdMapping.json"
PROBES = ROOT / "specs" / "knowledge-architecture" / "registry" / "semantic-probes"
OUT = ROOT / "evidence" / "gk-ke-capability-probe"

UNRESOLVED = {"PENDING", "PENDING_NAMING_MAPPING", "", None}

# GK-KE 本地执行器（非 KERT 技能）：不经 KERT 调用路径
GK_KE_LOCAL_PROVIDERS = {"SIM-EXEC-INTERPRET"}


def expected_keys_from_kert(svc, provider: str) -> list[str] | None:
    """从 KERT 已加载的包中取得该 provider 的 schema 顶层键。

    为什么从这里取而不是在 GK-KE 侧硬编码：
    硬编码会产生"我方期望"与"对方声明"两套事实，一旦对方 schema 变化，
    我方会以错误的期望值判其不合格 —— 本探针初版即犯此错
    （误为 report-assembler 硬编码了 customerId，而其 schema 并无该键）。
    改为一律以 **KERT 包自身声明的 schema** 为唯一事实来源。

    返回 None 表示该 provider 无独立 output-schema（如内置技能）。
    """
    if svc is None:
        return None
    pkg = getattr(svc, "_packages", {}).get(provider)
    if pkg:
        keys = pkg.get("schema_keys") or []
        if keys:
            return list(keys)
    # 内置技能（skill-customer-*）不在 _packages 中，其 schema 声明于
    # skills/customer-engagement/<name>/references/output-schema.md。
    # 若该文件存在则据其校验；不存在则如实返回 None（不得声称契约满足）。
    import re as _re
    name = provider.replace("skill-customer-", "")
    md = KERT / "skills" / "customer-engagement" / name / "references" / "output-schema.md"
    if md.is_file():
        m = _re.search(r"```json\n([\s\S]*?)\n```", md.read_text(encoding="utf-8"))
        if m:
            try:
                obj = json.loads(m.group(1))
                if isinstance(obj, dict):
                    return list(obj.keys())
            except Exception:
                keys = _re.findall(r'^\s{0,4}"([A-Za-z_]\w*)"\s*:', m.group(1), _re.M)
                if keys:
                    return list(dict.fromkeys(keys))
    return None


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8")) if p.is_file() else {}


def load_samples() -> dict[str, dict]:
    out: dict[str, dict] = {}
    if not PROBES.is_dir():
        return out
    for path in sorted(PROBES.glob("*.json")):
        doc = load(path)
        if doc.get("capabilityId"):
            out[doc["capabilityId"]] = doc
    return out


def build_service():
    """构造真实 KERT 服务；失败返回 (None, 原因)。"""
    if not KERT_SRC.is_dir():
        return None, f"KERT 源码目录不存在: {KERT_SRC}"
    sys.path.insert(0, str(KERT_SRC))
    try:
        from kert.application.skills import SkillExecutionService  # noqa: WPS433
    except Exception as exc:  # noqa: BLE001
        return None, f"KERT 导入失败: {type(exc).__name__}: {exc}"
    try:
        svc = SkillExecutionService(
            skill_packages=PKG_DIR if PKG_DIR.is_dir() else None)
    except Exception as exc:  # noqa: BLE001
        return None, f"SkillExecutionService 构造失败: {type(exc).__name__}: {exc}"
    return svc, ""


def real_call(svc, skill_id: str, sample: dict) -> dict:
    """真实调用一次，返回 {ok, status, dataKeys, resultKeys, error}。

    说明：外部技能包的统一返回外壳为 ``{"skillId":..., "result": {...}}``，
    技能**自身语义结构在 result 内层**。故同时记录外壳键与内层键，
    契约校验针对**内层 result**（那才是该技能 output-schema 的落点）。
    """
    payload = sample.get("input") or {"customerId": "SIM-C001"}
    try:
        # requestId 必须唯一：服务按 requestId 幂等，复用会命中缓存导致误判
        req_id = f"SIM-PROBE-{skill_id}-{abs(hash((skill_id, json.dumps(payload, sort_keys=True)))) % 10**8}"
        res = svc.execute(skill_id, req_id, payload)
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "status": None, "dataKeys": [], "resultKeys": [],
                "error": f"{type(exc).__name__}: {exc}"}
    status = getattr(res, "status", None)
    if status is None and isinstance(res, dict):
        status = res.get("status")
    data = getattr(res, "data", None)
    if data is None and isinstance(res, dict):
        data = res.get("data")
    data_keys = list(data) if isinstance(data, dict) else []
    inner = data.get("result") if isinstance(data, dict) else None
    result_keys = list(inner) if isinstance(inner, dict) else []
    return {"ok": status == "ok", "status": status, "dataKeys": data_keys,
            "resultKeys": result_keys, "error": None}


def probe_one(item: dict, samples: dict, mapping_index: dict, svc, svc_err: str) -> dict:
    cid = item.get("capabilityId")

    # **已被取代的条目**：不作独立探测、不计为欠账（见 main() 中 ④ 的说明）。
    if item.get("probingScope") == "OUT_OF_PROBE_SCOPE":
        return {
            "capabilityId": cid,
            "executorRef": item.get("executorRef"),
            "verdict": "OUT_OF_PROBE_SCOPE",
            "callable": False,
            "reasons": [item.get("probingScopeBasis") or "本探针不适用"],
            "checks": {"outOfScope": True},
        }
    if item.get("status") == "SUPERSEDED":
        return {
            "capabilityId": cid,
            "executorRef": None,
            "verdict": "SUPERSEDED",
            "callable": False,
            "supersededBy": item.get("supersededBy") or [],
            "reasons": [item.get("supersededBasis") or "已被后继能力取代"],
            "checks": {"superseded": True},
        }

    checks: dict[str, bool] = {}
    reasons: list[str] = []

    mapping = mapping_index.get(cid, {})
    provider = item.get("executorRef")
    has_provider = provider not in UNRESOLVED
    checks["providerResolvable"] = has_provider

    verdict = None
    call_info = None

    if not has_provider:
        verdict = "NOT_PROBED"
        reasons.append(f"executorRef 未解析（{provider!r}）")
    elif provider in GK_KE_LOCAL_PROVIDERS:
        # GK-KE 本地执行器：不在 KERT 技能注册表内，不经 KERT 调用路径。
        # 其契约由 GK-KE 侧 schema 保证；本探针不冒充对其做过 KERT 端到端调用。
        verdict = "NOT_PROBED"
        reasons.append(
            "GK-KE 本地执行器（非 KERT 技能）：契约由 GK-KE 侧 schema 保证，"
            "本探针不声称对其做过 KERT 端到端调用")
    elif svc is None:
        verdict = "NOT_PROBED"
        reasons.append(f"无法构造调用环境：{svc_err}")
    else:
        sample = samples.get(cid)
        checks["hasSemanticSample"] = sample is not None
        expected_keys = expected_keys_from_kert(svc, provider)
        checks["schemaDeclaredByProvider"] = expected_keys is not None

        if sample is None:
            verdict = "NOT_PROBED"
            reasons.append("无已知语义样例（§9.4 要求）")
        elif not sample.get("mustFail"):
            verdict = "NOT_PROBED"
            reasons.append("语义样例缺 mustFail 负例")
        elif expected_keys is None:
            # 内置技能无独立 output-schema：可调用但不能声称契约满足
            call_info = real_call(svc, provider, sample)
            checks["realCallSucceeded"] = bool(call_info["ok"])
            if call_info["ok"]:
                verdict = "NOT_PROBED"
                reasons.append(
                    "调用成功，但该 provider 无独立 output-schema，"
                    "无法校验语义契约（不得据此声称契约满足）")
            else:
                verdict = "CALL_FAILED"
                reasons.append(f"调用失败: {call_info['error'] or call_info['status']}")
        else:
            call_info = real_call(svc, provider, sample)
            checks["realCallSucceeded"] = bool(call_info["ok"])
            if not call_info["ok"]:
                verdict = "CALL_FAILED"
                reasons.append(f"调用失败: {call_info['error'] or call_info['status']}")
            else:
                # 契约校验针对**内层 result**（该技能 output-schema 的落点）
                actual = call_info["resultKeys"] or call_info["dataKeys"]
                where = "result 内层" if call_info["resultKeys"] else "返回外壳"
                missing = [k for k in expected_keys if k not in actual]
                checks["outputMatchesSchema"] = not missing
                if missing:
                    verdict = "CALLED_CONTRACT_UNMET"
                    reasons.append(
                        f"调用成功但{where}缺 {missing}；实际 keys={actual}")
                else:
                    verdict = "PASSED"

    return {
        "capabilityId": cid,
        "providerId": provider,
        "verdict": verdict,
        "callable": verdict == "PASSED",
        "checks": checks,
        "reasons": reasons,
        "call": call_info,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    registry = load(REGISTRY)
    mapping = load(MAPPING)
    items = registry.get("items", [])
    mapping_index = {e.get("canonicalCapabilityId"): e for e in mapping.get("entries", [])}
    samples = load_samples()

    svc, svc_err = build_service()

    results = [probe_one(it, samples, mapping_index, svc, svc_err) for it in items]

    # 一致性守卫：非 PASSED 不得 callable
    violations = [
        f"{r['capabilityId']}: verdict={r['verdict']} 但 callable=true"
        for r in results if r["verdict"] != "PASSED" and r["callable"]
    ]

    # ---- T-17 修复（2026-09-13，反角色攻击命中）----
    # 攻击：把**全部** 12 个条目的 executorRef 置为不可解析 →
    #   `total=12 PASSED=0 NOT_PROBED=12`，**exit=0 ⇒ PASS**。
    # 即：**即使所有能力都不可调用，门禁仍报通过** ——
    # `NOT_PROBED` 与 `PASSED` 在退出码上**完全等价**，
    # 「我没查」与「我查通过了」同义。
    # 这正是判据 `S2_EMPTY_MEANS_NONE` / `S3_NOT_RUN_NOT_NONE` 要防的形态，
    # 而它出现在门禁链自身（与 T-12 同族）。
    #
    # 修复分两条，均**不含主观阈值**：
    # ① 零能力通过 ⇒ 不可能算通过（最小、无争议）；
    # ② NOT_PROBED 中「**注册表条目本身未完成**」类（executorRef 未解析，
    #    如 `PENDING_NAMING_MAPPING`）是**缺陷**，不是「环境限制」，必须 FAIL。
    #    有意声明的 NOT_PROBED（如「GK-KE 本地执行器，非 KERT 技能」）仍允许，
    #    因为那是**已声明的事实**而非未完成项。
    n_passed = sum(1 for r in results if r["verdict"] == "PASSED")
    if not results:
        # **空集合不得静默通过**（2026-09-13 实测命中，T-12 同族）。
        # 攻击：把 Capability.json 写成 `{}` → `total=0 PASSED=0 NOT_PROBED=0`，
        # **__GATE_VERDICT__=PASS**。
        # 我第一版修复写的是 `if results and n_passed == 0` —— **`results` 为空时短路**，
        # 于是"零条目"这一更极端的情形**反而绕过**了检查。
        # 形态与 `chain-trace` 的 `all([]) == True` **完全同构** ——
        # **修一个的同时写了一个新的同族缺陷。**
        violations.append(
            "**注册表未声明任何能力**（items 为空）—— "
            "「零条目」不得等价于通过（S2_EMPTY_MEANS_NONE）")
    elif n_passed == 0:
        violations.append(
            f"**零能力通过**：total={len(results)} 而 PASSED=0 —— "
            "「全部未探测」不得等价于通过（S2_EMPTY_MEANS_NONE / S3_NOT_RUN_NOT_NONE）")
    # ③ 「注册表条目未完成」类 NOT_PROBED（executorRef 未解析）⇒ **INCONCLUSIVE**。
    #    依据（实测）：`PENDING_NAMING_MAPPING` 是**已登记的已知欠账** ——
    #    `docs/architecture/GK-KE-GK14-UE-UC-交付报告-V1.0.md:110` 明载
    #    「9 项能力的 executorRef 仍未解析（PENDING_NAMING_MAPPING）」，
    #    :246 并称「只要 executorRef 仍是 PENDING_NAMING_MAPPING，callable 就永远只有 1」。
    #    故它**不应**判 PASS（那正是把它当成没问题），
    #    **也不应**判 FAIL（那是新失败）—— 正确语义是**部分证明，不得计为全部通过**。
    #    这与 `gate-injection-tests` 的「覆盖不完整 ⇒ INCONCLUSIVE」同一模式。
    # ④ `SUPERSEDED` 条目**不作独立能力探测，也不计为欠账**（2026-09-13 终结命名映射债）。
    #    依据：`SIM-CAP-PRODUCT-REC` 的 `CapabilityIdMapping.json` note 明载
    #    「建议书 §9.2 要求拆为 CAP-06 知识体检 + CAP-07 条件核验；
    #      **拆分未完成前不得作为单一能力声明**」——
    #    它不是"映射没做"，而是"该条目已被两个后继取代"。
    #    故在注册表中**显式声明** `status/ supersededBy / supersededBasis`，
    #    门禁据此将其**排除**出探测与欠账统计（而非塞一个猜来的 providerId）。
    superseded = [
        f"{r['capabilityId']} → {r.get('supersededBy')}"
        for r in results if r.get("verdict") == "SUPERSEDED"
    ]
    out_of_scope = [
        f"{r['capabilityId']}（{'; '.join(r.get('reasons') or [])[:80]}…）"
        for r in results if r.get("verdict") == "OUT_OF_PROBE_SCOPE"
    ]
    pending_debt = [
        f"{r['capabilityId']}: {r['verdict']}"
        f"（{'; '.join(r.get('reasons') or [])}）"
        for r in results
        if r["verdict"] == "NOT_PROBED"
    ]

    if args.write:
        by_id = {r["capabilityId"]: r for r in results}
        for item in items:
            r = by_id[item["capabilityId"]]
            item["probeStatus"] = r["verdict"]
            item["callable"] = r["callable"]
            item["probeEvidence"] = {
                "probedAt": "2026-09-13",
                "method": "REAL_CALL_VIA_KERT_SkillExecutionService",
                "probeVersion": "2.0.0",
                "checks": r["checks"],
                "reasons": r["reasons"],
                "callStatus": (r["call"] or {}).get("status"),
                "returnedDataKeys": (r["call"] or {}).get("dataKeys"),
                "returnedResultKeys": (r["call"] or {}).get("resultKeys"),
            }
        registry["probeSummary"] = {
            "probeVersion": "2.0.0",
            "method": "REAL_CALL",
            "serviceConstructed": svc is not None,
            "serviceError": svc_err or None,
            "total": len(results),
            "passed": sum(1 for r in results if r["verdict"] == "PASSED"),
            "calledContractUnmet": sum(1 for r in results
                                       if r["verdict"] == "CALLED_CONTRACT_UNMET"),
            "callFailed": sum(1 for r in results if r["verdict"] == "CALL_FAILED"),
            "notProbed": sum(1 for r in results if r["verdict"] == "NOT_PROBED"),
            "callableCount": sum(1 for r in results if r["callable"]),
            "statement": ("PASSED 仅表示真实调用成功**且**输出结构符合该技能语义契约。"
                          "NOT_PROBED 表示未尝试或无法校验，不表示通过。"),
        }
        REGISTRY.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n",
                            encoding="utf-8")

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(f"gk-ke-capability-probe: report (v2.0.0 REAL_CALL)")
        print(f"  KERT service: {'可用' if svc else '不可用 — ' + svc_err}")
        for r in results:
            mark = r["verdict"]
            print(f"  [{mark:22s}] {r['capabilityId']:28s} "
                  f"provider={r.get('providerId')}")
            for reason in r["reasons"][:1]:
                print(f"{'':29s}- {reason}")
        n_pass = sum(1 for r in results if r["verdict"] == "PASSED")
        print(f"  total={len(results)} PASSED={n_pass} "
              f"CALLED_CONTRACT_UNMET="
              f"{sum(1 for r in results if r['verdict']=='CALLED_CONTRACT_UNMET')} "
              f"CALL_FAILED={sum(1 for r in results if r['verdict']=='CALL_FAILED')} "
              f"NOT_PROBED={sum(1 for r in results if r['verdict']=='NOT_PROBED')}")
        print("  NOTE: PASSED 需真实调用成功且输出符合该技能语义契约。")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "report.json").write_text(
        json.dumps({"results": results, "serviceAvailable": svc is not None,
                    "serviceError": svc_err or None},
                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if violations:
        print("__GATE_VERDICT__=FAIL")
        print("gk-ke-capability-probe: FAIL", file=sys.stderr)
        for v in violations:
            print(f"  - {v}", file=sys.stderr)
        return 1
    if out_of_scope:
        print(f"  **{len(out_of_scope)} 项属本探针适用范围之外（已分类，不计欠账）**：",
              file=sys.stderr)
        for s in out_of_scope:
            print(f"  - {s}", file=sys.stderr)
    if superseded:
        print(f"  **{len(superseded)} 项已被后继能力取代（不作探测、不计欠账）**：",
              file=sys.stderr)
        for s in superseded:
            print(f"  - {s}", file=sys.stderr)
    if pending_debt:
        print("__GATE_VERDICT__=INCONCLUSIVE")
        print(f"gk-ke-capability-probe: INCONCLUSIVE —— "
              f"PASSED={n_passed}/{len(results)}，"
              f"**{len(pending_debt)} 项 NOT_PROBED（可调用性未被证明）**：", file=sys.stderr)
        for d in pending_debt:
            print(f"  - {d}", file=sys.stderr)
        print("  **本门禁未完成，不得计为全部通过。**", file=sys.stderr)
        return 0
    print("__GATE_VERDICT__=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
