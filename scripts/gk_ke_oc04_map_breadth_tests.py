#!/usr/bin/env python3
"""GK-KE OC-04 地图知识广度门禁。

背景：Owner 验收判定 OC-04「需调整」，指出缺口是**知识广度**而非节点数量：
「客户方前准备，要查这三项资料（产品条款、日均存款、解读能力）还不够，
  客户经理专业能力并不比客户强，还要准备产业调研、客户准入条件等信息」

本门禁防止「知识广度」再次被悄悄削回。若有人删掉知识条目 / 规则 / 能力 / 数据源，
门禁必须失败（fail-closed）。

检查：
  1. 7 类知识条目齐备（对标 KI-FRONT-001~007）
  2. 2 项准入类规则知识齐备（对标 KI-RULE-001/002）—— Owner 点名的「客户准入条件」
  3. 1 项流程知识齐备（KI-FLOW-001）
  4. 7 项能力齐备，且**每项标注真实就绪状态**
  5. 3 个数据源引用齐备（T-CORE-001 / T-EXT-001 / T-MARKET-001）
  6. **不得**把 DESIGN_ONLY 能力写成已就绪（诚实性断言）
  7. 节点由广度推导（节点数 ≥ 知识条目 + 规则 + 能力之和的下界）
  8. 变更有 changeLog 且记录 Owner 原话

退出码：全通过 0，否则 1。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "specs" / "knowledge-architecture" / "activation" / "map_spec.json"

REQUIRED_KI = {
    "KI-FRONT-001", "KI-FRONT-002", "KI-FRONT-003", "KI-FRONT-004",
    "KI-FRONT-005", "KI-FRONT-006", "KI-FRONT-007",
}
REQUIRED_RULES = {"KI-RULE-001", "KI-RULE-002"}
REQUIRED_SOURCES = {"T-CORE-001", "T-EXT-001", "T-MARKET-001"}
REQUIRED_CAPABILITIES = {
    "bank-front-supply-chain-graph", "bank-front-eight-dimension",
    "bank-front-fact-reconciliation", "bank-front-commitment-script",
    "bank-front-kyc-gap-check", "bank-front-product-recommendation",
    "bank-front-report-assembler",
}
VALID_READINESS = {
    "IMPLEMENTED", "IMPLEMENTED_DIFFERENT_NAME", "PACKAGE_LOADABLE_UNVERIFIED",
    "PARTIAL_VIA_OTHER_SKILL", "DESIGN_ONLY",
}
# 声明为"已实现"的状态；其余一律视为未就绪
READY_STATES = {"IMPLEMENTED", "IMPLEMENTED_DIFFERENT_NAME"}


def main() -> int:  # noqa: C901
    failures: list[str] = []

    if not MAP.is_file():
        print(f"FAIL: map spec missing: {MAP}", file=sys.stderr)
        return 2
    d = json.loads(MAP.read_text(encoding="utf-8"))

    # 1. 知识条目 7 类
    entries = d.get("knowledgeBreadth", {}).get("entries", [])
    got_ki = {e.get("maps") for e in entries}
    missing = REQUIRED_KI - got_ki
    if missing:
        failures.append(f"[1] knowledge entries missing (KI-FRONT-*): {sorted(missing)}")
    if len(entries) < 7:
        failures.append(f"[1] expected >=7 knowledge entries, got {len(entries)}")
    for e in entries:
        for f in ("id", "maps", "name", "content", "nodeId"):
            if not e.get(f):
                failures.append(f"[1] entry {e.get('id')} missing {f}")

    # 2. 准入类规则知识
    rules = d.get("ruleKnowledge", {}).get("rules", [])
    got_rules = {r.get("maps") for r in rules}
    missing_rules = REQUIRED_RULES - got_rules
    if missing_rules:
        failures.append(f"[2] admission rule knowledge missing (Owner named '客户准入条件'): {sorted(missing_rules)}")

    # 3. 流程知识
    flow = d.get("ruleKnowledge", {}).get("flowKnowledge", {})
    if flow.get("maps") != "KI-FLOW-001":
        failures.append(f"[3] flow knowledge must map KI-FLOW-001, got {flow.get('maps')!r}")

    # 4/6. 能力齐备 + 就绪状态诚实
    caps = d.get("capabilities", {}).get("items", [])
    got_caps = {c.get("maps") for c in caps}
    missing_caps = REQUIRED_CAPABILITIES - got_caps
    if missing_caps:
        failures.append(f"[4] capabilities missing: {sorted(missing_caps)}")
    for c in caps:
        r = c.get("readiness")
        if r not in VALID_READINESS:
            failures.append(f"[4] capability {c.get('id')}: invalid readiness {r!r}")
        if not c.get("evidence"):
            failures.append(f"[4] capability {c.get('id')}: missing readiness evidence")
        # 诚实性：DESIGN_ONLY 不得回避证据
        if r == "DESIGN_ONLY" and "仅" not in str(c.get("evidence", "")):
            failures.append(f"[6] capability {c.get('id')}: DESIGN_ONLY must state it has no code registration")
        # 诚实性（关键）：声称已实现的能力必须有**源码级证据**（skillId + 文件引用），
        # 否则即为"把设计说成已实现"——本程序反复出现过的错误类型。
        if r in READY_STATES:
            ev = str(c.get("evidence", ""))
            if "skills.py" not in ev or ":" not in ev:
                failures.append(
                    f"[6] capability {c.get('id')}: claiming readiness {r} requires source-level "
                    f"evidence (skills.py + line); got {ev!r}")

    # 6b. 设计能力数不得少于 7（不得悄悄裁剪）
    if len(caps) < 7:
        failures.append(f"[4] expected >=7 capabilities, got {len(caps)}")

    # 5. 数据源
    srcs = {s.get("id") for s in d.get("dataSources", {}).get("refs", [])}
    missing_srcs = REQUIRED_SOURCES - srcs
    if missing_srcs:
        failures.append(f"[5] data sources missing: {sorted(missing_srcs)}")
    if d.get("dataSources", {}).get("rule") is None:
        failures.append("[5] data sources must declare a reference-only rule (不复制数据)")

    # 7. 节点由广度推导
    nodes = d.get("nodes", {}).get("list", [])
    lower_bound = len(entries) + len(rules) + len(caps)
    if len(nodes) < lower_bound:
        failures.append(f"[7] node count {len(nodes)} < breadth lower bound {lower_bound} "
                        f"(nodes must be derived from breadth, not hand-added)")

    # 8. changeLog 记录 Owner 原话
    clog = d.get("changeLog", {})
    if not clog:
        failures.append("[8] missing changeLog")
    else:
        if "客户经理专业能力并不比客户强" not in str(clog.get("ownerNote", "")):
            failures.append("[8] changeLog must quote the Owner's note verbatim")
        if not clog.get("notNodeCountFix"):
            failures.append("[8] changeLog must record that this fixes breadth, not node count")

    # 覆盖率自述必须与实际一致（防止自述漂移）
    cov = d.get("coverage", {})
    if cov.get("knowledgeEntries") != len(entries):
        failures.append(f"[9] coverage.knowledgeEntries {cov.get('knowledgeEntries')} != actual {len(entries)}")
    if cov.get("capabilities") != len(caps):
        failures.append(f"[9] coverage.capabilities {cov.get('capabilities')} != actual {len(caps)}")

    # 10. 就绪断言必须与 KERT 代码实测一致（防止"整批宣称已实现"）
    #     实测基准（GK-KE-OC04-G3能力就绪核对-V1.0.md）：
    #       代码硬编码 3 个 skill-customer-*，另可包加载 1 个 bank-front-*
    #     => bank-front-* 命名下最多 2 项可声称已实现
    KERT_MAX_READY_BANK_FRONT = 2
    ready_bank_front = [c for c in caps
                        if c.get("readiness") in READY_STATES
                        and str(c.get("maps", "")).startswith("bank-front-")]
    if len(ready_bank_front) > KERT_MAX_READY_BANK_FRONT:
        failures.append(
            f"[10] {len(ready_bank_front)} bank-front capabilities claimed ready, but KERT code "
            f"registers at most {KERT_MAX_READY_BANK_FRONT} "
            f"(see GK-KE-OC04-G3能力就绪核对-V1.0.md) - over-claiming readiness")

    if failures:
        print("gk-ke-oc04-map-breadth-tests: FAIL", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    ready = [c["id"] for c in caps if c.get("readiness") in READY_STATES]
    design = [c["id"] for c in caps if c.get("readiness") not in READY_STATES]
    print("gk-ke-oc04-map-breadth-tests: PASS")
    print(f"  knowledge entries : {len(entries)} (KI-FRONT-001~007)")
    print(f"  admission rules   : {len(rules)} (KI-RULE-001/002)")
    print(f"  flow knowledge    : 1 (KI-FLOW-001)")
    print(f"  capabilities      : {len(caps)}  ready={len(ready)} design_only={len(design)}")
    print(f"  data sources      : {len(srcs)}")
    print(f"  nodes             : {len(nodes)} (was {d.get('nodes', {}).get('previousCount')})")
    print("  checks: ki-breadth, admission-rules, flow, capabilities+readiness-honesty, "
          "data-sources, nodes-derived, changelog, coverage-consistency, readiness-vs-kert")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
