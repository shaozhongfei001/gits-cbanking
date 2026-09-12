#!/usr/bin/env python3
"""GK-KE 语义级消费验证骨架（预注册 S1–S5）。

【设计要点】
判据在 `docs/architecture/GK-KE-语义级消费验证方案-V1.0.md` 中**预先锁定**，
本脚本**只执行、不定义**判据。预注册哈希登记于 `_preregistration.json`，
脚本启动时校验该文档哈希未变 —— **若被人修改，脚本拒绝执行**。

【诚实性约束】
在确定性适配器下（无分析能力），S1/S3 所需的输入差异**无法产生**，
本脚本**必须**报 `INCONCLUSIVE`，**不得**报通过。
这是本脚本最重要的行为：**没有能力证明时，就说不确定。**

用法：
  python3 scripts/gk_ke_semantic_consumption.py            # 执行
  python3 scripts/gk_ke_semantic_consumption.py --preregister  # 锁定判据哈希
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KERT = Path("/home/szf/dev/Leibniz-KERT")
KERT_SRC = KERT / "src"
PKG_DIR = KERT / "examples" / "bank-front-skills"
SCHEME = ROOT / "docs" / "architecture" / "GK-KE-语义级消费验证方案-V1.0.md"
PREREG = (ROOT / "specs" / "knowledge-architecture" / "contracts"
          / "_preregistration.json")
OUT = ROOT / "evidence" / "gk-ke-semantic-consumption"

UPSTREAM = "bank-front-fact-reconciliation"
DOWNSTREAM = "bank-front-kyc-gap-check"

# 判定项标识（判据内容见方案文档，本脚本不重复定义）
CRITERIA = ["S1_CONFLICT_PROPAGATION", "S2_EMPTY_MEANS_NONE",
            "S3_NOT_RUN_NOT_NONE", "S4_HYPOTHESIS_NOT_CLOSED",
            "S5_REPRODUCIBLE"]

ALLOWED_VOLATILE_FIELDS = {"generatedAt", "executionId", "requestId"}


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_service():
    sys.path.insert(0, str(KERT_SRC))
    from kert.application.skills import SkillExecutionService  # noqa: WPS433
    return SkillExecutionService(skill_packages=PKG_DIR)


def call(svc, skill_id: str, req_id: str, payload: dict) -> dict:
    res = svc.execute(skill_id, req_id, payload)
    data = getattr(res, "data", None) or {}
    return {"status": getattr(res, "status", None),
            "result": data.get("result") if isinstance(data, dict) else None}


def normalize(obj, drop_volatile: bool = True):
    """规范化输出；S5 比较时排除生成时间/执行 id 等易变字段。"""
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if drop_volatile and k in ALLOWED_VOLATILE_FIELDS:
                continue
            out[k] = normalize(v, drop_volatile)
        return out
    if isinstance(obj, list):
        return [normalize(x, drop_volatile) for x in obj]
    return obj


def collects_any(result: dict, key: str) -> bool:
    if not isinstance(result, dict):
        return False
    v = result.get(key)
    return isinstance(v, list) and len(v) > 0


def run_criteria(svc) -> dict:
    """执行 S1–S5。

    本函数**只观测**，不改变判据。所有观测结果原样记录。
    """
    obs: dict = {}

    # ---- 能力探测：下游是否可能产出非空条目 ----
    probe = call(svc, DOWNSTREAM, "SEM-PROBE-1",
                 {"customerId": "SIM-C001", "conflictCases": [{"id": "XC-1"}]})
    obs["downstreamCanProduceContent"] = collects_any(probe.get("result") or {},
                                                      "kycGaps")
    obs["upstreamCanProduceContent"] = collects_any(
        (call(svc, UPSTREAM, "SEM-PROBE-2",
              {"customerId": "SIM-C001"}).get("result") or {}), "conflicts")

    # ---- S5 可复现（唯一在确定性适配器下可执行的判据）----
    a = call(svc, DOWNSTREAM, "SEM-S5-A",
             {"customerId": "SIM-C001", "conflictCases": [{"id": "XC-1"}]})
    b = call(svc, DOWNSTREAM, "SEM-S5-B",
             {"customerId": "SIM-C001", "conflictCases": [{"id": "XC-1"}]})
    s5_pass = (json.dumps(normalize(a.get("result")), sort_keys=True,
                          ensure_ascii=False)
               == json.dumps(normalize(b.get("result")), sort_keys=True,
                             ensure_ascii=False))
    obs["S5_REPRODUCIBLE"] = {"executable": True, "passed": s5_pass}

    # ---- S1–S4 需要"内容相关"的输出：先判断是否具备条件 ----
    content_capable = (obs["downstreamCanProduceContent"]
                       and obs["upstreamCanProduceContent"])
    obs["contentCapableAdapter"] = content_capable

    for cid in ("S1_CONFLICT_PROPAGATION", "S2_EMPTY_MEANS_NONE",
                "S3_NOT_RUN_NOT_NONE", "S4_HYPOTHESIS_NOT_CLOSED"):
        if not content_capable:
            obs[cid] = {
                "executable": False,
                "reason": ("当前适配器产出占位内容（集合字段恒为空），"
                           "无法产生该判据所需的输入差异；"
                           "**按要求报 INCONCLUSIVE，不得记为通过**"),
            }
        else:
            # 具备条件时的执行路径在真实 LLM 接入后启用；
            # 该分支在本轮**故意不实现**，以避免"看起来跑过"的假象。
            obs[cid] = {
                "executable": False,
                "reason": ("适配器具备内容能力，但 S1–S4 的判定实现"
                           "须在真实 LLM 接入后由**独立执行者**编写并执行"
                           "（防自证规则 G-1：判据作者不得兼执行者）"),
            }
    return obs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preregister", action="store_true")
    args = parser.parse_args()

    if not SCHEME.is_file():
        print(f"gk-ke-semantic-consumption: FAIL — 方案缺失 {SCHEME}",
              file=sys.stderr)
        return 1

    scheme_hash = sha256_file(SCHEME)

    # ---- 预注册：锁定判据哈希 ----
    if args.preregister:
        PREREG.parent.mkdir(parents=True, exist_ok=True)
        PREREG.write_text(json.dumps({
            "$comment": ("语义级消费验证判据的**预注册哈希**。"
                         "判据文档一旦修改，本文件中记录的哈希即不匹配，"
                         "验证脚本将拒绝执行 —— 以此防止执行前调整判据。"),
            "preregisteredAt": datetime.now(timezone.utc).isoformat(),
            "criteriaDocument": str(SCHEME.relative_to(ROOT)),
            "criteriaSha256": scheme_hash,
            "criteria": CRITERIA,
            "passRule": "S1–S5 全部通过方为达成；任一失败为未达成；无法判定不得记为通过",
            "antiSelfCertification": [
                "G-1 执行者与判据作者不得为同一人",
                "G-2 不得修改被测对象以迎合判据",
                "G-3 不得删除失败用例",
                "G-4 判据变更须留痕并保留旧版",
                "G-5 不得以波动为由重跑到通过",
                "G-6 不得只报通过率而不报明细",
            ],
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"gk-ke-semantic-consumption: 判据已预注册")
        print(f"  criteria: {CRITERIA}")
        print(f"  sha256:   {scheme_hash}")
        print(f"  written:  {PREREG.relative_to(ROOT)}")
        return 0

    # ---- 执行：先校验判据未被改动 ----
    if not PREREG.is_file():
        print("gk-ke-semantic-consumption: FAIL — 判据未预注册；"
              "请先运行 --preregister", file=sys.stderr)
        return 1
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    if prereg.get("criteriaSha256") != scheme_hash:
        print("gk-ke-semantic-consumption: FAIL — 判据文档已被修改！",
              file=sys.stderr)
        print(f"  预注册哈希: {prereg.get('criteriaSha256')}", file=sys.stderr)
        print(f"  当前哈希:   {scheme_hash}", file=sys.stderr)
        print("  依防自证规则 G-4，判据变更须新发版本并保留旧版为对照；"
              "本脚本拒绝在判据被静默修改后执行。", file=sys.stderr)
        return 1

    try:
        svc = load_service()
    except Exception as exc:  # noqa: BLE001
        print(f"gk-ke-semantic-consumption: FAIL — 无法构造 KERT 服务: "
              f"{type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    obs = run_criteria(svc)

    executable = [k for k in CRITERIA if obs.get(k, {}).get("executable")]
    passed = [k for k in executable if obs[k].get("passed")]
    inconclusive = [k for k in CRITERIA if not obs.get(k, {}).get("executable")]
    failed = [k for k in executable if not obs[k].get("passed")]

    # 结论按预注册规则：全部通过才算达成；否则未达成或无法判定
    if failed:
        verdict = "NOT_MET"
    elif inconclusive:
        verdict = "INCONCLUSIVE"
    else:
        verdict = "MET"

    report = {
        "verdict": verdict,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "criteriaSha256": scheme_hash,
        "adapter": ("DeterministicLlmAdapter（占位内容）"
                    if not obs.get("contentCapableAdapter") else "content-capable"),
        "executableCriteria": executable,
        "passedCriteria": passed,
        "failedCriteria": failed,
        "inconclusiveCriteria": inconclusive,
        "observations": obs,
        "statement": {
            "MET": "S1–S5 全部通过，语义级消费达成。",
            "NOT_MET": "存在失败判据，语义级消费未达成。",
            "INCONCLUSIVE": ("**无法判定** —— 当前适配器无分析能力，"
                             "S1–S4 无法执行。"
                             "依预注册规则，**不得记为通过**。"),
        }[verdict],
        "notAClaimOfFailure": (
            "INCONCLUSIVE 不等于失败，也不等于通过；"
            "它表示**当前环境不具备验证条件**。"),
    }

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"gk-ke-semantic-consumption: {verdict}")
    print(f"  判据哈希校验: 通过（{scheme_hash[:16]}…）")
    for cid in CRITERIA:
        o = obs.get(cid, {})
        if not o.get("executable"):
            print(f"  [INCONCLUSIVE] {cid}")
            print(f"                 {o.get('reason', '')[:70]}")
        else:
            mark = "PASS" if o.get("passed") else "FAIL"
            print(f"  [{mark:12s}] {cid}")
    print(f"  可执行 {len(executable)} / 无法判定 {len(inconclusive)} / 失败 {len(failed)}")
    print(f"  {report['statement']}")
    print(f"  NOTE: INCONCLUSIVE 不得记为通过。")
    print(f"  wrote: {OUT.relative_to(ROOT)}/report.json")

    # INCONCLUSIVE 不作为门禁失败：它是"环境不具备验证条件"，
    # 而非"制品损坏"或"能力未达成"。
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
