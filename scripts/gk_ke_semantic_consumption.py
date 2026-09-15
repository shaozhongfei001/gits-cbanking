#!/usr/bin/env python3
"""GK-KE 语义级消费验证：**采集器**（不做判定）v2.0.0。

【设计原则（关键，勿改）】
本脚本**只采集原始观测**，**不做通过/失败判定** ——
判据在 `docs/architecture/GK-KE-语义级消费验证方案-V1.0.md` 中预先锁定，
判定必须由**独立执行者**（非判据作者）依据该判据对原始观测作出。

理由（防自证规则 G-1）：本轮此前的错误（静态标志冒充真实调用、门禁永不失败、
统一求和冒充按公式复算）**根因都是"作者即执行者"**。
若本脚本自行判定，等于在同一处再犯一次。

【产出】
  evidence/gk-ke-semantic-consumption/observations.json
    · 每个判据的**原始输入**与**原始输出**（未经加工）
    · `judgement` 字段一律为 null，等待独立执行者填写

用法：
  python3 scripts/gk_ke_semantic_consumption.py --preregister   # 锁定判据哈希
  python3 scripts/gk_ke_semantic_consumption.py --collect       # 采集原始观测
  python3 scripts/gk_ke_semantic_consumption.py                 # 校验预注册 + 报告
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
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

CRITERIA = ["S1_CONFLICT_PROPAGATION", "S2_EMPTY_MEANS_NONE",
            "S3_NOT_RUN_NOT_NONE", "S4_HYPOTHESIS_NOT_CLOSED",
            "S5_REPRODUCIBLE"]

# 每个判据要求的输入条件（**由判据文档决定，此处仅实现采集**）
SCENARIOS = {
    "S1_CONFLICT_PROPAGATION": {
        "needsUpstream": True,
        "upstreamInput": {
            "customerId": "SIM-C001",
            "metrics": {"revenue": {"prev": 25000000, "curr": 31250000},
                        "taxPaid": {"prev": 800000, "curr": 656000}},
            "note": "营收上升而实缴税款下降，期望上游产出冲突/异常信号",
        },
        "downstreamInputExtra": {},
    },
    "S2_EMPTY_MEANS_NONE": {
        "needsUpstream": False,
        "downstreamInputExtra": {
            "reconciliationStatus": "SUCCESS",
            "conflictCases": [],
            "indicators": [],
            "ruleCoverage": {"expected": ["R01", "R03"], "covered": ["R01", "R03"]},
        },
    },
    "S3_NOT_RUN_NOT_NONE": {
        "needsUpstream": False,
        "downstreamInputExtra": {
            "reconciliationStatus": "NOT_RUN",
            "conflictCases": [],
            "indicators": [],
            "ruleCoverage": {"expected": ["R01", "R03"], "covered": []},
        },
    },
    "S4_HYPOTHESIS_NOT_CLOSED": {
        "needsUpstream": False,
        "downstreamInputExtra": {
            "reconciliationStatus": "SUCCESS",
            "conflictCases": [{"conflictId": "XC-1", "type": "营收-税款背离"}],
            "explanations": [
                {"name": "可能享受税收优惠", "evidenceRefs": []}   # 无证据
            ],
            "ruleCoverage": {"expected": ["R01"], "covered": ["R01"]},
        },
    },
    "S5_REPRODUCIBLE": {
        "needsUpstream": False,
        "downstreamInputExtra": {
            "reconciliationStatus": "SUCCESS",
            "conflictCases": [{"conflictId": "XC-1", "type": "营收-税款背离"}],
            "indicators": [],
        },
    },
}


def sha256_file(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def llm_configured() -> tuple[bool, str]:
    """判断是否具备真实 LLM（决定能否采集到有内容的输出）。"""
    base = os.environ.get("KERT_LLM_BASE_URL")
    key = os.environ.get("KERT_LLM_API_KEY")
    model = os.environ.get("KERT_LLM_MODEL")
    if base and key and model:
        return True, f"{model} @ {base}"
    return False, "未配置 KERT_LLM_BASE_URL/API_KEY/MODEL（将回退确定性适配器）"


def load_service():
    sys.path.insert(0, str(KERT_SRC))
    from kert.application.skills import SkillExecutionService  # noqa: WPS433
    return SkillExecutionService(skill_packages=PKG_DIR)


def call(svc, skill_id: str, req_id: str, payload: dict) -> dict:
    res = svc.execute(skill_id, req_id, payload)
    data = getattr(res, "data", None) or {}
    return {"status": getattr(res, "status", None),
            "result": data.get("result") if isinstance(data, dict) else None}


def collect(svc) -> dict:
    """采集每个判据的原始输入输出。**不判定。**"""
    obs: dict = {"collectedAt": datetime.now(timezone.utc).isoformat(),
                 "llmConfigured": llm_configured()[0],
                 "llmDetail": llm_configured()[1],
                 "criteria": {}}

    upstream_result = None
    up_raw = None

    # S1 需要上游先跑一次
    if SCENARIOS["S1_CONFLICT_PROPAGATION"]["needsUpstream"]:
        up_in = SCENARIOS["S1_CONFLICT_PROPAGATION"]["upstreamInput"]
        up_raw = call(svc, UPSTREAM, "SEM-S1-UP", up_in)
        upstream_result = up_raw.get("result") or {}
        obs["criteria"]["S1_CONFLICT_PROPAGATION"] = {
            "upstreamInput": up_in,
            "upstreamRawOutput": up_raw,
            "judgement": None,
            "judgedBy": None,
            "note": ("上游真实输出已记录；下游输入由独立执行者依合同映射决定，"
                     "本采集器不代替其构造，以避免影响判定"),
        }

    for cid in ("S2_EMPTY_MEANS_NONE", "S3_NOT_RUN_NOT_NONE",
                "S4_HYPOTHESIS_NOT_CLOSED", "S5_REPRODUCIBLE"):
        sc = SCENARIOS[cid]
        payload = {"customerId": "SIM-C001"}
        payload.update(sc.get("downstreamInputExtra") or {})

        if cid == "S5_REPRODUCIBLE":
            a = call(svc, DOWNSTREAM, "SEM-S5-A", payload)
            b = call(svc, DOWNSTREAM, "SEM-S5-B", payload)
            obs["criteria"][cid] = {
                "downstreamInput": payload,
                "rawOutputRunA": a,
                "rawOutputRunB": b,
                "judgement": None,
                "judgedBy": None,
            }
        else:
            out = call(svc, DOWNSTREAM, f"SEM-{cid}", payload)
            obs["criteria"][cid] = {
                "downstreamInput": payload,
                "downstreamRawOutput": out,
                "judgement": None,
                "judgedBy": None,
            }

    return obs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preregister", action="store_true")
    parser.add_argument("--collect", action="store_true")
    args = parser.parse_args()

    if not SCHEME.is_file():
        print(f"gk-ke-semantic-consumption: FAIL — 判据文档缺失 {SCHEME}",
              file=sys.stderr)
        return 1
    scheme_hash = sha256_file(SCHEME)

    if args.preregister:
        PREREG.parent.mkdir(parents=True, exist_ok=True)
        PREREG.write_text(json.dumps({
            "$comment": ("语义级消费验证判据的**预注册哈希**。判据文档一旦修改，"
                         "此处记录的哈希即不匹配，校验将失败。"),
            "preregisteredAt": datetime.now(timezone.utc).isoformat(),
            "criteriaDocument": str(SCHEME.relative_to(ROOT)),
            "criteriaSha256": scheme_hash,
            "criteria": CRITERIA,
            "passRule": "S1–S5 全部通过方为达成；任一失败为未达成；无法判定不得记为通过",
            "antiSelfCertification": [
                "G-1 执行者与判据作者不得为同一人（本采集器不做判定即为落实此条）",
                "G-2 不得修改被测对象以迎合判据",
                "G-3 不得删除失败用例",
                "G-4 判据变更须留痕并保留旧版",
                "G-5 不得以波动为由重跑到通过",
                "G-6 不得只报通过率而不报明细",
            ],
            "collectorOnlyNote": ("采集器与判定器分离：本仓库脚本只采集原始输入输出，"
                                  "通过/失败由独立执行者依判据作出。"),
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("gk-ke-semantic-consumption: 判据已预注册")
        print(f"  criteria: {CRITERIA}")
        print(f"  sha256:   {scheme_hash}")
        return 0

    # 预注册校验
    if not PREREG.is_file():
        print("gk-ke-semantic-consumption: FAIL — 判据未预注册", file=sys.stderr)
        return 1
    prereg = json.loads(PREREG.read_text(encoding="utf-8"))
    if prereg.get("criteriaSha256") != scheme_hash:
        print("gk-ke-semantic-consumption: FAIL — 判据文档已被修改！",
              file=sys.stderr)
        print(f"  预注册: {prereg.get('criteriaSha256')}", file=sys.stderr)
        print(f"  当前:   {scheme_hash}", file=sys.stderr)
        print("  依 G-4，判据变更须新发版本并保留旧版对照。", file=sys.stderr)
        return 1

    configured, detail = llm_configured()

    if args.collect:
        try:
            svc = load_service()
        except Exception as exc:  # noqa: BLE001
            print(f"gk-ke-semantic-consumption: FAIL — 无法构造 KERT 服务: "
                  f"{type(exc).__name__}: {exc}", file=sys.stderr)
            return 1
        obs = collect(svc)
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / "observations.json").write_text(
            json.dumps(obs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("gk-ke-semantic-consumption: 原始观测已采集")
        print(f"  LLM: {'✅ ' + detail if configured else '❌ ' + detail}")
        print(f"  判据数: {len(obs['criteria'])}，judgement 全部为 null（待独立执行者判定）")
        print(f"  wrote: {OUT.relative_to(ROOT)}/observations.json")
        return 0

    # 默认：报告状态（不判定）
    have_obs = (OUT / "observations.json").is_file()
    judged = None
    if have_obs:
        o = json.loads((OUT / "observations.json").read_text(encoding="utf-8"))
        judged = sum(1 for c in o.get("criteria", {}).values()
                     if c.get("judgement"))

    # 依预注册判据 §3 通过规则**汇总独立执行者的判定**：
    #   · 任一 FAIL            → 未达成
    #   · 否则任一 INCONCLUSIVE → 无法判定（**不得记为通过**）
    #   · 否则全部 PASS         → 达成
    #   · 未全部判定           → 无法判定（同样不得记为通过）
    #
    # 本脚本**不产生判定**（判定由独立执行者作出，G-1），
    # 只做**汇总与如实报告**。但汇总必须正确，否则会出现
    # "判定为 FAIL 却显示 PASS" 的静默通过 —— 与该脚本此前
    # "无判定却显示 PASS" 属同一类缺陷（QA 第三轮指出后已修，此处为其同族）。
    n_total = len(CRITERIA)
    verdicts: dict[str, str] = {}
    if have_obs:
        o = json.loads((OUT / "observations.json").read_text(encoding="utf-8"))
        for cid in CRITERIA:
            v = (o.get("criteria", {}).get(cid) or {}).get("judgement")
            if v:
                verdicts[cid] = v
    n_judged = len(verdicts)
    fails = [c for c, v in verdicts.items() if v == "FAIL"]
    incon = [c for c, v in verdicts.items() if v == "INCONCLUSIVE"]

    if fails:
        overall = "NOT_MET"
    elif incon or n_judged < n_total:
        overall = "INCONCLUSIVE"
    else:
        overall = "MET"

    print(f"gk-ke-semantic-consumption: {overall}")
    # 门禁结论走**专用 token 通道**（见 run_gates 的 VERDICT_RE）：
    # 不再依赖"输出里出现某个词"，避免说明文字/测试标签误命中。
    print("__GATE_VERDICT__=" + {"MET": "PASS", "NOT_MET": "FAIL",
                                 "INCONCLUSIVE": "INCONCLUSIVE"}[overall])
    print(f"  判据哈希校验: 通过（{scheme_hash[:16]}…）")
    print(f"  真实 LLM: {'✅ ' + detail if configured else '❌ ' + detail}")
    print(f"  已判定: {n_judged} / {n_total}（判定由独立执行者作出，TL 未代判）")
    if verdicts:
        counts: dict[str, int] = {}
        for v in verdicts.values():
            counts[v] = counts.get(v, 0) + 1
        print(f"  判定计数: {counts}")
    if fails:
        print(f"  **未达成** —— FAIL: {fails}")
    if incon:
        print(f"  无法判定（不得记为通过）: {incon}")
    if n_judged < n_total:
        print(f"  尚未判定 {n_total - n_judged} 条 —— 依规则**不得记为通过**")

    if overall == "MET":
        print("  §9.3 中由 S1–S5 覆盖的四行达成"
              "（注意：**不覆盖**行 1/5/7，故不得表述为「§9.3 达成」）")
        print("  ⚠️ 判定结论见 observations.json 的 judgement 字段。")
        return 0

    print()
    print("  ⚠️ 本脚本**只汇总，不产生判定**（判定由独立执行者作出，G-1）。")
    print(f"     结论: **语义级消费未达成**（{overall}）。")
    print("     不得表述为「§9.3 语义级消费达成」或「部分通过、基本达成」。")
    print("     判定记录: evidence/gk-ke-semantic-consumption/"
          "INDEPENDENT-JUDGEMENT-S1-S5-V1.0.md")
    # NOT_MET / INCONCLUSIVE 均返回 0：就绪度类不计入常规门禁失败，
    # 由 run_gates 第四态与 make readiness --strict 分别呈现与把关。
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
