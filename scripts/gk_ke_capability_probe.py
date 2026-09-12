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

# 各 provider 的实测 output-schema 顶层必含键
# 来源：KERT examples/bank-front-skills/<skill>/references/output-schema.md
EXPECTED_DATA_KEYS = {
    "skill-customer-outreach-script": None,   # 内置技能无独立 output-schema
    "skill-customer-meeting-script": None,
    "skill-customer-previsit-report": None,
    "bank-front-fact-reconciliation": ["schemaVersion", "skillId", "customerId", "indicators", "conflicts"],
    "bank-front-eight-dimension": ["schemaVersion", "skillId", "industryCode", "dimensions"],
    "bank-front-kyc-gap-check": ["schemaVersion", "skillId", "customerId", "kycGaps"],
    "bank-front-commitment-script": ["schemaVersion", "skillId", "customerId", "commitments"],
    "bank-front-supply-chain-graph": ["schemaVersion", "skillId", "customerId", "nodes"],
    "bank-front-product-recommendation": ["schemaVersion", "skillId", "customerId", "candidates"],
    "bank-front-report-assembler": ["schemaVersion", "skillId", "customerId", "battleOrder"],
}


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
    """真实调用一次，返回 {ok, status, dataKeys, error}。"""
    payload = sample.get("input") or {"customerId": "SIM-C001"}
    try:
        res = svc.execute(skill_id, f"SIM-PROBE-{abs(hash(skill_id)) % 100000}", payload)
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "status": None, "dataKeys": [],
                "error": f"{type(exc).__name__}: {exc}"}
    status = getattr(res, "status", None)
    if status is None and isinstance(res, dict):
        status = res.get("status")
    data = getattr(res, "data", None)
    if data is None and isinstance(res, dict):
        data = res.get("data")
    data_keys = list(data) if isinstance(data, dict) else []
    return {"ok": status == "ok", "status": status, "dataKeys": data_keys, "error": None}


def probe_one(item: dict, samples: dict, mapping_index: dict, svc, svc_err: str) -> dict:
    cid = item.get("capabilityId")
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
    elif svc is None:
        verdict = "NOT_PROBED"
        reasons.append(f"无法构造调用环境：{svc_err}")
    else:
        sample = samples.get(cid)
        checks["hasSemanticSample"] = sample is not None
        expected_keys = EXPECTED_DATA_KEYS.get(provider)

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
                missing = [k for k in expected_keys if k not in call_info["dataKeys"]]
                checks["outputMatchesSchema"] = not missing
                if missing:
                    verdict = "CALLED_CONTRACT_UNMET"
                    reasons.append(
                        f"调用成功但输出顶层缺 {missing}；"
                        f"实际 keys={call_info['dataKeys']}")
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
        print("gk-ke-capability-probe: FAIL", file=sys.stderr)
        for v in violations:
            print(f"  - {v}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
