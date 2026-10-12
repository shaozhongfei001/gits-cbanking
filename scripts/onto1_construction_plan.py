#!/usr/bin/env python3
"""施工计划与合同候选生成器（Owner 决议 2026-09-21 准备项 1、2）—— **P7 加固版**

P7（处置率口径一致性）加固点：
  1. **五份制品全部存在、非空、可解析**为前置；任一缺失/空/不可解析 ⇒ FAIL（**不再跳过缺失件**）；
  2. **逐制品**核对当前未闭环状态（json 比对实测未闭环数；md 比对**当次应出现的条件句**）；
  3. **条件化结论**：未闭环 > 0 ⇒ 「WI-A2 未完成 ⇒ 依 WI-A2 禁止 Wave 2 开工」；
     未闭环 = 0 ⇒ 「WI-A2 此项条件已满足；Wave 2 能否开工由其他既有门禁共同决定（**不得据此自动解锁**）」；
  4. **拒判**：扫描汇总表缺失 / 空表 / 解析失败 / 出现未定义处置状态 ⇒ 拒绝判定（FAIL），不得推断为已达 100%。

用法：`--build` / `--gate [--prep-dir DIR --scan-summary CSV]` / `--selftest`
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import pathlib
import re
import shutil
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
EV = ROOT / "loops/ONTO1-ontology-split/evidence"
PREP = EV / "prep"
TRIAGE = EV / "obligation-triage.csv"
SCAN_SUMMARY = EV / "consumer-scan-summary.csv"

ARTIFACTS = {                      # 五份受检制品（P7 的对象）
    "plan_md": "ONTO1-CONSTRUCTION-PLAN-DRAFT.md",
    "plan_json": "construction-plan.json",
    "contract_md": "ONTO1-CONTRACT-SPLIT-CANDIDATES-DRAFT.md",
    "contract_json": "contract-split-candidates.json",
    "clause_md": "PSO-ICO-INTERIM-AND-CLAUSE-CHECK.md",
}
UNCLOSED_KINDS = ("FOLLOW_MIGRATION", "HOMONYM_REQUIRES_SOURCE_CHECK", "CONTROL_PLANE_REQUIRED")
KNOWN_DISPOSITIONS = {
    "DOC_TEXT_REFERENCE", "EXEMPT_FROZEN_REVIEW", "SCAN_INSTRUMENT", "AUTHORITY_SOURCE",
    "EXEMPT_FROZEN_CONTRACT", "EXEMPT_FROZEN_EVIDENCE", "EXEMPT_NON_ONTOLOGY_HOMONYM",
    "EXEMPT_SEED_DATA", "FOLLOW_MIGRATION", "GENERATED_MIRROR", "HOMONYM_REQUIRES_SOURCE_CHECK",
    "TOOLING_CONFIG", "CONTROL_PLANE_REQUIRED", "EXEMPT_QUARANTINED_ASSET", "EXEMPT_RUNTIME_WORKSPACE",
}
BANNED_CLAIMS = ("处置率 100%", "处置率100%", "已达 100%")

DEPS = {
    "B2_L1_L2_语义规格层": ["B1_合同层"],
    "B3_L2_KERT元模型": ["B1_合同层", "KERT 维护方写权限"],
    "B4_L3_运行本体": ["B2_L1_L2_语义规格层"],
    "B6_消费者切换": ["B4_L3_运行本体", "D3 根域（正式切换时）"],
    "B7_导入级耦合（代码导入本体包）": ["B2_L1_L2_语义规格层"],
    "B8_内容级重绑（IRI/词表/哈希）": ["B2_L1_L2_语义规格层"],
    "B9_其他模块": ["B4_L3_运行本体"],
}
VERIFY = {
    "B2_L1_L2_语义规格层": "本体可解析（rdflib）+ 术语计数复算 + C-2 碰撞门禁 0 处",
    "B3_L2_KERT元模型": "KERT 侧只读分析 → 补丁方案 → KERT 维护方确认后合入；物化链路校验先于产出",
    "B4_L3_运行本体": "本体/适配器加载测试 + 消费者扫描（命中处置 100%）",
    "B6_消费者切换": "消费者编译/单测 + oldIRI→newIRI 解析验证（SIM 通道）",
    "B7_导入级耦合（代码导入本体包）": "编译 + 同名导入歧义用例（M8 同族）",
    "B8_内容级重绑（IRI/词表/哈希）": "逐条回源复算 + 钉值哈希门禁（漂移即 FAIL）",
    "B9_其他模块": "按模块测试；无测试者挂最小夹具",
}
SIM_ELIGIBLE = ("B2_L1_L2_语义规格层", "B4_L3_运行本体",
                "B7_导入级耦合（代码导入本体包）", "B8_内容级重绑（IRI/词表/哈希）")


class CheckRefused(Exception):
    """拒判：输入缺失/格式错误/出现未定义状态 ⇒ 不得推断出任何结论。"""


def batch_of(r: dict) -> str:
    s = r["signal"]
    m = re.search(r"R-STRONG-PATH-([A-Z-]+)", s)
    if m:
        mod = m.group(1)
        if mod.startswith("SPEC-KNOWLEDGE-ARCH"):
            return "B2_L1_L2_语义规格层"
        if mod.startswith("SPEC-GK-KE"):
            return "B3_L2_KERT元模型"
        if mod.startswith(("MODULE-OPERATIONAL-ONTOLOGY", "MODULE-KNOWLEDGE-ARCH")):
            return "B4_L3_运行本体"
        if mod.startswith(("MODULE-SCENARIO-JOURNEY", "ADAPTER", "KERT-SRC")):
            return "B6_消费者切换"
        return "B9_其他模块"
    if s.startswith("STRONG_CONTENT"):
        return "B8_内容级重绑（IRI/词表/哈希）"
    if "RESOLVES_TO_ONTOLOGY_PKG" in s or "IMPORT_LINE" in s:
        return "B7_导入级耦合（代码导入本体包）"
    return "B9_其他模块"


def load_obligations() -> list[dict]:
    rows = list(csv.DictReader(open(TRIAGE, encoding="utf-8")))
    return [r for r in rows if r["disposition"] == "TRUE_OBLIGATION"]


def disposal_status(summary: pathlib.Path | None = None) -> dict:
    """WI-A2 命中处置表状态。**缺件/空表/解析失败/未定义状态 ⇒ 拒判（CheckRefused）**。"""
    path = pathlib.Path(summary) if summary else SCAN_SUMMARY
    if not path.is_file():
        raise CheckRefused(f"扫描汇总表缺失：{path}")
    try:
        rows = list(csv.DictReader(open(path, encoding="utf-8")))
    except (OSError, csv.Error, UnicodeDecodeError) as exc:
        raise CheckRefused(f"扫描汇总表无法解析：{exc}") from exc
    if not rows:
        raise CheckRefused(f"扫描汇总表为空：{path}")
    if "disposition" not in rows[0]:
        raise CheckRefused("扫描汇总表缺少 `disposition` 列")
    unknown = sorted({(r.get("disposition") or "").strip() for r in rows} - KNOWN_DISPOSITIONS)
    if unknown:
        raise CheckRefused(f"出现未定义处置状态（拒绝判定）：{unknown}")
    def occ(r):  # noqa: E306
        try:
            return int(r.get("occurrences") or 0)
        except ValueError as exc:
            raise CheckRefused(f"`occurrences` 非整数：{r.get('occurrences')!r}") from exc
    unclosed_rows = sum(1 for r in rows if r["disposition"] in UNCLOSED_KINDS)
    return {"source": str(path), "aggregated_rows": len(rows),
            "occurrences_total": sum(occ(r) for r in rows),
            "unclosed_rows": unclosed_rows,
            "unclosed_occurrences": sum(occ(r) for r in rows if r["disposition"] in UNCLOSED_KINDS),
            "unclosed_by_kind": dict(collections.Counter(r["disposition"] for r in rows
                                                         if r["disposition"] in UNCLOSED_KINDS)),
            "reached_100pct": unclosed_rows == 0}


def wi_a2_sentence(st: dict) -> str:
    """**条件化** WI-A2 结论（未闭环 >0 / =0 两种表述）。"""
    if not st["reached_100pct"]:
        detail = " / ".join(f"{k} {v}" for k, v in sorted(st["unclosed_by_kind"].items()))
        return (f"WI-A2 命中处置表**未完成**（未闭环聚合行 **{st['unclosed_rows']}**：{detail}）"
                f"⇒ **依 WI-A2，Wave 2 禁止开工**（执行计划 §WI-A2）")
    return ("WI-A2 此项**条件已满足**（未闭环聚合行 0）⇒ **Wave 2 能否开工由其他既有门禁共同决定**"
            "（例如 D3 根域、签署页、命中处置之外的退出门禁）；**不得**据本项自动解锁，"
            "**也不得**再以 WI-A2 为由宣称禁止开工")


def prohibitions(st: dict) -> list[str]:
    return [
        "未签 D3 前**禁止发布新 IRI / 重钉**（执行计划 §WI-A4）",
        wi_a2_sentence(st),
        "重构项**禁止**使用 `equivalentClass`（执行计划 §WI-1-3 校验④）",
        "D1 标准文本到手前**禁止任何国标符合性表述**（执行计划 §WI-A3）",
    ]


def build_plan(obligations: list[dict], st: dict) -> dict:
    by = collections.defaultdict(list)
    for r in obligations:
        by[batch_of(r)].append(r)
    batches = []
    for b, items in sorted(by.items()):
        batches.append({"id": b, "count": len(items),
                        "repos": dict(collections.Counter(r["repo"] for r in items)),
                        "waves": dict(collections.Counter(r["responsible_wave"] for r in items)),
                        "tiers": dict(collections.Counter(r["tier"] for r in items)),
                        "deps": DEPS.get(b, []), "verification": VERIFY.get(b, "按模块测试"),
                        "sim_eligible": b in SIM_ELIGIBLE,
                        "sample": [f'{r["repo"]}/{r["path"]}' for r in sorted(items, key=lambda x: x["path"])[:3]]})
    return {"schema": "ONTO1-CONSTRUCTION-PLAN/1.1",
            "basis": "691 真义务（obligation-triage.csv）",
            "principle": "**不是 691 次独立开发**：按同类改造聚类为批次；批次内可并行、批次间按依赖串行。",
            "authority_status": "CANDIDATE（未正式生效；正式执行需合同拆条获批 + 相应签署）",
            "total": len(obligations),
            "external_gates": ["D3 正式根域（正式切换时）", "KERT 维护方写权限", "委员会签署页（正式基线）"],
            "prohibitions": prohibitions(st),
            "ledger_status": {
                "obligation_triage": {"true_obligation": len(obligations), "to_be_checked": 0,
                                      "note": "**清单口径**：691 条义务的『待回源』，与命中处置率**不是同一制品**"},
                "wi_a2_disposition": st},
            "batches": batches}


def build_contracts(obligations: list[dict], st: dict) -> dict:
    sem = sorted({r["path"] for r in obligations if r["path"].startswith("specs/semantic")})
    core = sorted({r["path"] for r in obligations
                   if "FILE_GITS_CORE" in r["signal"] or "gits-core" in (r["evidence"] or "")})
    return {"schema": "ONTO1-CONTRACT-SPLIT-CANDIDATES/1.1",
            "status": "CANDIDATE_NOT_EFFECTIVE（**未正式生效**：不得据此改 CONTRACT_INDEX、不得发布新 IRI）",
            "authority": "Owner 决议 2026-09-21（准备项 1）",
            "basis": "docs/dispatch/ONTO-SPLIT-本体四层落地执行计划-V2.0.md §74",
            "current": {"id": "CTR-SEM-002", "kind": "turtle",
                        "authority_source": "specs/semantic/gits-core.owl.ttl",
                        "owner": "semantic_architecture_owner", "consumers": ["semantic_runtime"], "generated": []},
            "candidates": [
                {"id": "CTR-SEM-002（收窄后）", "scope": "L3 运行本体（GITS 侧）",
                 "authority_source": "specs/semantic/gits-core.owl.ttl（收窄：仅 L3）",
                 "owner": "semantic_architecture_owner", "compatibility": "explicit_migration",
                 "generated": "候选（本阶段不新增 generated 目标）", "status": "CANDIDATE_NOT_EFFECTIVE"},
                {"id": "CTR-SEM-003（新）", "scope": "L1 公共核心语义契约库",
                 "authority_source": "候选 L1 仓（骨架见 evidence/prep/l1-skeleton/，**尚未建立**）",
                 "owner": "公共语义 Owner（当前由项目 Owner 临时兼任）", "compatibility": "explicit_migration",
                 "generated": "候选：L1 术语集 + 版本清单", "status": "CANDIDATE_NOT_EFFECTIVE"},
                {"id": "CTR-SEM-004（新）", "scope": "L2 KERT 元模型",
                 "authority_source": "KERT 侧 90_control/ontology/（改动需 KERT 维护方权限）",
                 "owner": "Knowledge/KERT Owner", "compatibility": "explicit_migration",
                 "generated": "候选：L2 本体（KERT 侧）", "status": "CANDIDATE_NOT_EFFECTIVE"},
                {"id": "CTR-SEM-005（新）", "scope": "L4 注册表 Schema/SKOS",
                 "authority_source": "候选：注册表 Schema + SKOS 词表",
                 "owner": "Integration Contract Owner（当前由项目 Owner 临时兼任）",
                 "compatibility": "explicit_migration", "generated": "候选：schema/skos",
                 "status": "CANDIDATE_NOT_EFFECTIVE"}],
            "impact": {"CTR-SEM-002 登记 consumers": ["semantic_runtime"],
                       "受影响义务数（去重）": len(set(sem) | set(core)),
                       "specs/semantic 直接义务": sem, "引用 gits-core 的义务（样本）": core[:10],
                       "受影响批次": ["B2_L1_L2_语义规格层", "B7_导入级耦合（代码导入本体包）",
                                      "B8_内容级重绑（IRI/词表/哈希）"]},
            "prohibitions_cited": prohibitions(st),
            "ledger_status": {"wi_a2_disposition": st}}


def clause_md(st: dict) -> str:
    """第五份制品：条款核查（**生成物**，保证与实测同步）。"""
    return f"""# PSO / ICO 临时任命登记与条款禁令核查（准备项 4）

## 1. 临时任命（继续）
| 角色 | holder | status | 说明 |
|---|---|---|---|
| 公共语义 Owner（PSO） | 项目 Owner（邵钟飞） | `interim` | 决定词义 / 本体 / 词表 / 语义版本 |
| Integration Contract Owner（ICO） | 项目 Owner（邵钟飞） | `interim` | 决定接口表达 / 版本绑定 / 兼容性 / 消费者契约；**不得反向改写 PSO 已批准语义** |

**评审委员会独立性（V8）不适用于这两项临时任命**：V8 只约束《14 签署页》的评审委员会构成；两者不可互相援引。

## 2. 条款禁令核查（是否有条款禁止本轮准备工作）
**结论：未发现禁止这些准备工作的条款；发现的是对「实施方式」的约束。**

| 条款（来源） | 对本轮工作的约束 | 具体风险（若越线） |
|---|---|---|
| 未签 D3 前**禁止发布新 IRI / 重钉**（§WI-A4） | L1 骨架必须沿用 `PROVISIONAL_SIM_LEGACY_NAMESPACE` | 违规发布新根域 IRI；碰撞检查失效 |
| **WI-A2 命中处置表**（§WI-A2） | {wi_a2_sentence(st)} | 依 WI-A2 判定错误 ⇒ 越权开工或错误冻结 |
| 重构项**禁止**使用 `equivalentClass`（§WI-1-3 校验④） | 施工与骨架均禁用等价关系 | 语义漂移不可审计 |
| D1 文本到手前**禁止国标符合性表述**（§WI-A3） | 全部文书已规避 | 红线违规 |
| KERT 受控内容改动**需维护方权限** | 只交分析/方案/验证材料 | 越权写入他人受控资产 |

> **口径分列（防混算）**：`obligation-triage.csv` 的 691 条义务「待回源 = 0」为**清单口径**；
> WI-A2 命中处置为**扫描口径**——实测未闭环聚合行 **{st['unclosed_rows']}**（{st['unclosed_by_kind']}）。

## 3. 需要 Owner 裁定的业务分歧
暂未发现必须由业务裁定的分歧。
"""


def render_md(plan: dict, cand: dict) -> tuple[str, str]:
    md1 = ["# 候选合同与影响清单（DRAFT｜**未正式生效**）", "",
           "- 依据：Owner 决议 2026-09-21 准备项 1；执行计划 §74", f"- 状态：`{cand['status']}`", "",
           "| 合同 | 层次 | 权威源 | owner | 状态 |", "|---|---|---|---|---|"]
    for c in cand["candidates"]:
        md1.append(f"| `{c['id']}` | {c['scope']} | `{c['authority_source']}` | {c['owner']} | `{c['status']}` |")
    md1 += ["", "## 影响面", "",
            f"- 受影响义务数（去重）：**{cand['impact']['受影响义务数（去重）']}**",
            f"- 涉及批次：{cand['impact']['受影响批次']}",
            f"- 直接读 `specs/semantic/**` 的义务：{cand['impact']['specs/semantic 直接义务'][:6]}", "",
            "## 适用禁令（必须遵守）"] + [f"- {p}" for p in cand["prohibitions_cited"]]
    md2 = ["# 691 项义务施工计划（DRAFT）", "",
           "> **不是 691 次独立开发**：按同类改造聚为批次；批次内可并行，批次间按依赖串行；每批以「可验证单元」定义完成。", "",
           "| 批次 | 项数 | 仓库 | 波次 | 依赖 | 验证方式 | SIM 可先行 |", "|---|---|---|---|---|---|---|"]
    for b in plan["batches"]:
        md2.append(f"| `{b['id']}` | {b['count']} | {b['repos']} | {b['waves']} | {b['deps']} | {b['verification']} | "
                   f"{'✅' if b['sim_eligible'] else '需外部'} |")
    md2 += ["", f"**计数守恒**：各批次之和 = {plan['total']}（构建时断言）。", "",
            "## 外部前置", "- " + " · ".join(plan["external_gates"]), "", "## 适用禁令"] + \
           [f"- {p}" for p in plan["prohibitions"]] + \
           ["", "## 台账口径（两本账，勿混算）",
            f"- 清单口径：`obligation-triage.csv` 真义务 **{plan['ledger_status']['obligation_triage']['true_obligation']}**、待回源 **0**",
            f"- 扫描口径：未闭环聚合行 **{plan['ledger_status']['wi_a2_disposition']['unclosed_rows']}**"
            f"（{plan['ledger_status']['wi_a2_disposition']['unclosed_by_kind']}）"]
    return "\n".join(md1) + "\n", "\n".join(md2) + "\n"


def cmd_build(prep: pathlib.Path = PREP, summary: pathlib.Path | None = None) -> int:
    st = disposal_status(summary)
    obs = load_obligations()
    plan, cand = build_plan(obs, st), build_contracts(obs, st)
    assert sum(b["count"] for b in plan["batches"]) == len(obs) == 691
    prep.mkdir(parents=True, exist_ok=True)
    (prep / ARTIFACTS["plan_json"]).write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (prep / ARTIFACTS["contract_json"]).write_text(json.dumps(cand, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md1, md2 = render_md(plan, cand)
    (prep / ARTIFACTS["contract_md"]).write_text(md1, encoding="utf-8")
    (prep / ARTIFACTS["plan_md"]).write_text(md2, encoding="utf-8")
    (prep / ARTIFACTS["clause_md"]).write_text(clause_md(st), encoding="utf-8")
    print(f"已生成施工计划（{len(plan['batches'])} 批 / 合计 {plan['total']} 项）与 5 份制品；"
          f"WI-A2 未闭环 = {st['unclosed_rows']}")
    return 0


def _read_artifacts(prep: pathlib.Path) -> dict[str, str]:
    """五份制品必须**全部存在、非空、可解析**（json 解析 / md 非空），否则抛 CheckRefused。"""
    texts: dict[str, str] = {}
    for key, name in ARTIFACTS.items():
        p = prep / name
        if not p.is_file():
            raise CheckRefused(f"受检制品缺失：{name}")
        raw = p.read_text(encoding="utf-8")
        if not raw.strip():
            raise CheckRefused(f"受检制品为空：{name}")
        if name.endswith(".json"):
            try:
                json.loads(raw)
            except json.JSONDecodeError as exc:
                raise CheckRefused(f"受检制品无法解析：{name}（{exc}）") from exc
        texts[key] = raw
    return texts


def p7(st: dict, prep: pathlib.Path = PREP) -> tuple[bool, str]:
    texts = _read_artifacts(prep)
    bad = [k for k, v in texts.items() if any(b in v for b in BANNED_CLAIMS)]
    if bad:
        return False, f"受检制品含禁用结论（{bad}）"
    expect = wi_a2_sentence(st)
    marker_unclosed = "依 WI-A2，Wave 2 禁止开工"
    marker_satisfied = "条件已满足"
    expect_marker = marker_satisfied if st["reached_100pct"] else marker_unclosed
    forbid_marker = marker_unclosed if st["reached_100pct"] else marker_satisfied
    per: list[str] = []
    ok = True
    for key, name in ARTIFACTS.items():
        text = texts[key]
        if name.endswith(".json"):
            data = json.loads(text)
            live = data.get("ledger_status", {}).get("wi_a2_disposition", {})
            # **全字段一致性**（不写死任何数字）：总数 / 达标标志 / 三类明细 / 明细之和 / occurrences / 聚合行数
            checks = {
                "unclosed_rows": live.get("unclosed_rows") == st["unclosed_rows"],
                "reached_100pct": live.get("reached_100pct") == st["reached_100pct"],
                "unclosed_by_kind": {k: int(v) for k, v in (live.get("unclosed_by_kind") or {}).items()} == st["unclosed_by_kind"],
                "kinds_sum_eq_rows": sum(int(v) for v in (live.get("unclosed_by_kind") or {}).values()) == live.get("unclosed_rows"),
                "unclosed_occurrences": live.get("unclosed_occurrences") == st["unclosed_occurrences"],
                "aggregated_rows": live.get("aggregated_rows") == st["aggregated_rows"],
                "occurrences_total": live.get("occurrences_total") == st["occurrences_total"],
            }
            same = all(checks.values())
            why = "全部字段一致" if same else "不一致：" + ",".join(k for k, v in checks.items() if not v)
            per.append(f"{name}:{why}")
            ok = ok and same
        else:
            same = (expect in text) and (expect_marker in text) and (forbid_marker not in text)
            why = ("一致性 OK" if same else
                   ("缺当次条件句" if expect not in text else "含相反情形句（过期内容）"))
            per.append(f"{name}:{why}")
            ok = ok and same
    return ok, "；".join(per)


def cmd_gate(prep: pathlib.Path = PREP, summary: pathlib.Path | None = None) -> int:
    rows: list[tuple[str, bool, str]] = []
    try:
        st = disposal_status(summary)
        refusal = None
    except CheckRefused as exc:
        st, refusal = None, str(exc)
    if refusal:
        print(f"REFUSED [P0 输入拒判] {refusal}")
        print("施工计划：REFUSED（输入缺失/格式错误/未定义状态 ⇒ **拒绝判定**，不得推断为已达 100%）")
        return 2
    obs = load_obligations()
    plan = json.loads((prep / ARTIFACTS["plan_json"]).read_text(encoding="utf-8")) if (prep / ARTIFACTS["plan_json"]).is_file() else {}
    cand = json.loads((prep / ARTIFACTS["contract_json"]).read_text(encoding="utf-8")) if (prep / ARTIFACTS["contract_json"]).is_file() else {}
    rows.append(("P1 计数守恒", sum(b["count"] for b in plan.get("batches", [])) == len(obs) == 691,
                 f"批次和={sum(b['count'] for b in plan.get('batches', []))} 真义务={len(obs)}"))
    rows.append(("P2 批次不重复", len(plan.get("batches", [])) == len({b["id"] for b in plan.get("batches", [])}),
                 str(len(plan.get("batches", [])))))
    _cands = cand.get("candidates", [])
    rows.append(("P3 合同候选**恰 4 项且全部** NOT_EFFECTIVE（空集不得视为通过）",
                 len(_cands) == 4 and all(c.get("status") == "CANDIDATE_NOT_EFFECTIVE" for c in _cands),
                 f"候选 {len(_cands)} 项；非 NOT_EFFECTIVE = "
                 f"{[c.get('status') for c in _cands if c.get('status') != 'CANDIDATE_NOT_EFFECTIVE'] or '无'}"))
    rows.append(("P4 列明适用禁令", len(cand.get("prohibitions_cited", [])) >= 4,
                 str(len(cand.get("prohibitions_cited", [])))))
    rows.append(("P5 影响清单非空", cand.get("impact", {}).get("受影响义务数（去重）", 0) > 0,
                 str(cand.get("impact", {}).get("受影响义务数（去重）", 0))))
    rows.append(("P6 外部前置已声明", len(plan.get("external_gates", [])) >= 3, str(plan.get("external_gates"))))
    try:
        ok7, detail = p7(st, prep)
    except CheckRefused as exc:
        ok7, detail = False, f"拒判：{exc}"
    rows.append(("P7 五份制品存在·可解析·与实测未闭环一致（条件化）", ok7, detail))
    for n, ok, d in rows:
        print(f"{'PASS' if ok else 'FAIL'} [{n}] {d}")
    bad = [n for n, ok, _ in rows if not ok]
    print(f"施工计划：{'PASS' if not bad else 'FAIL'}（{len(rows) - len(bad)}/{len(rows)}）")
    return 0 if not bad else 2


def _summary_without_unclosed(src: pathlib.Path, dst: pathlib.Path) -> pathlib.Path:
    """构造『未闭环 = 0』的变体（保留其他行）。"""
    rows = list(csv.DictReader(open(src, encoding="utf-8")))
    keep = [r for r in rows if r["disposition"] not in UNCLOSED_KINDS]
    with open(dst, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(keep)
    return dst


def cmd_selftest() -> int:
    fails, total = 0, 0
    base_st = disposal_status()
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        work = td / "prep"
        shutil.copytree(PREP, work)
        # M0 对照
        ok, d = p7(base_st, work)
        total += 1; fails += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'} [M0 对照] 五份制品一致 = {ok}（{d}）")
        # M1 未闭环 412（真实数据）⇒ 五份制品须含「未完成」句
        expect = wi_a2_sentence(base_st)
        total += 1
        ok1 = (not base_st["reached_100pct"]) and expect in (work / ARTIFACTS["plan_md"]).read_text(encoding="utf-8")
        fails += 0 if ok1 else 1
        print(f"{'PASS' if ok1 else 'FAIL'} [M1 未闭环=412] 条件句=『未完成 ⇒ 依 WI-A2 禁止 Wave 2 开工』= {ok1}")
        # M2 未闭环 = 0（合成表）⇒ 重新生成 ⇒ 条件句必须变为『已满足，不得据此自动解锁』
        zero = _summary_without_unclosed(SCAN_SUMMARY, td / "scan_zero.csv")
        st0 = disposal_status(zero)
        work0 = td / "prep0"; shutil.copytree(PREP, work0)
        obs = load_obligations()
        plan0, cand0 = build_plan(obs, st0), build_contracts(obs, st0)
        (work0 / ARTIFACTS["plan_md"]).write_text(render_md(plan0, cand0)[1], encoding="utf-8")
        (work0 / ARTIFACTS["contract_md"]).write_text(render_md(plan0, cand0)[0], encoding="utf-8")
        (work0 / ARTIFACTS["clause_md"]).write_text(clause_md(st0), encoding="utf-8")
        (work0 / ARTIFACTS["plan_json"]).write_text(json.dumps(plan0, ensure_ascii=False), encoding="utf-8")
        (work0 / ARTIFACTS["contract_json"]).write_text(json.dumps(cand0, ensure_ascii=False), encoding="utf-8")
        ok2a, _ = p7(st0, work0)
        s0 = wi_a2_sentence(st0)
        total += 1
        ok2 = ok2a and "条件已满足" in s0 and "禁止 Wave 2 开工" not in s0
        fails += 0 if ok2 else 1
        print(f"{'PASS' if ok2 else 'FAIL'} [M2 未闭环=0] 条件化表述正确（不再称『因 WI-A2 禁止开工』）= {ok2}")
        # 旧内容注入：把 0 情形制品塞回「未完成」句 ⇒ 必须 FAIL
        (work0 / ARTIFACTS["plan_md"]).write_text(
            (work0 / ARTIFACTS["plan_md"]).read_text(encoding="utf-8").replace(s0, expect),
            encoding="utf-8")
        try:
            ok2b, _ = p7(st0, work0)
        except CheckRefused:
            ok2b = False
        total += 1; fails += 0 if not ok2b else 1
        print(f"{'PASS' if not ok2b else 'FAIL'} [M2b 过期内容注入（0 情形混入未完成句）] 被拦下 = {not ok2b}")
        # M3 未定义处置状态 ⇒ 拒判
        bad_csv = td / "scan_unknown.csv"
        rows = list(csv.DictReader(open(SCAN_SUMMARY, encoding="utf-8")))
        with open(bad_csv, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader()
            w.writerows(rows[:5] + [{**rows[0], "disposition": "SOMETHING_NEW"}])
        total += 1
        try:
            disposal_status(bad_csv); refused = False
        except CheckRefused:
            refused = True
        fails += 0 if refused else 1
        print(f"{'PASS' if refused else 'FAIL'} [M3 未定义处置状态] 拒判 = {refused}")
        # M4 某一制品缺失 ⇒ P7 必须 FAIL（**修复旧版跳过缺件的缺陷**）
        (work / ARTIFACTS["clause_md"]).unlink()
        try:
            ok4, d4 = p7(base_st, work)
        except CheckRefused as exc:
            ok4, d4 = False, f"拒判：{exc}"
        total += 1; fails += 0 if not ok4 else 1
        print(f"{'PASS' if not ok4 else 'FAIL'} [M4 第五份制品缺失] 被拦下 = {not ok4}（{d4}）")
        # M4b 制品为空
        (work / ARTIFACTS["clause_md"]).write_text("", encoding="utf-8")
        try:
            ok5, _ = p7(base_st, work)
        except CheckRefused:
            ok5 = False
        total += 1; fails += 0 if not ok5 else 1
        print(f"{'PASS' if not ok5 else 'FAIL'} [M4b 制品为空] 被拦下 = {not ok5}")
        # M6 分类被篡改（总数不变：FOLLOW_MIGRATION → -1）⇒ 必败
        shutil.copy2(PREP / ARTIFACTS["clause_md"], work / ARTIFACTS["clause_md"])
        pj = work / ARTIFACTS["plan_json"]
        orig_json = pj.read_text(encoding="utf-8")
        d0 = json.loads(orig_json)
        d0["ledger_status"]["wi_a2_disposition"]["unclosed_by_kind"]["FOLLOW_MIGRATION"] = -1
        pj.write_text(json.dumps(d0, ensure_ascii=False), encoding="utf-8")
        try:
            ok6, det6 = p7(base_st, work)
        except CheckRefused as exc:
            ok6, det6 = False, str(exc)
        total += 1; fails += 0 if not ok6 else 1
        print(f"{'PASS' if not ok6 else 'FAIL'} [M6 分类被篡改（总数不变）] 被拦下 = {not ok6}（{det6}）")
        # M7 unclosed_occurrences 被篡改 ⇒ 必败
        d1 = json.loads(orig_json); d1["ledger_status"]["wi_a2_disposition"]["unclosed_occurrences"] += 1
        pj.write_text(json.dumps(d1, ensure_ascii=False), encoding="utf-8")
        try:
            ok7, det7 = p7(base_st, work)
        except CheckRefused as exc:
            ok7, det7 = False, str(exc)
        total += 1; fails += 0 if not ok7 else 1
        print(f"{'PASS' if not ok7 else 'FAIL'} [M7 occurrences 被篡改] 被拦下 = {not ok7}")
        # M8 明细之和 ≠ 总数（删一个分类）⇒ 必败
        d2 = json.loads(orig_json); d2["ledger_status"]["wi_a2_disposition"]["unclosed_by_kind"].pop("CONTROL_PLANE_REQUIRED", None)
        pj.write_text(json.dumps(d2, ensure_ascii=False), encoding="utf-8")
        try:
            ok8, det8 = p7(base_st, work)
        except CheckRefused as exc:
            ok8, det8 = False, str(exc)
        total += 1; fails += 0 if not ok8 else 1
        print(f"{'PASS' if not ok8 else 'FAIL'} [M8 明细之和≠总数] 被拦下 = {not ok8}")
        pj.write_text(orig_json, encoding="utf-8")
        # M5 还原对照
        ok6, _ = p7(base_st, work)
        total += 1; fails += 0 if ok6 else 1
        print(f"{'PASS' if ok6 else 'FAIL'} [M5 还原对照] 一致 = {ok6}")
    print(f"--selftest {'PASS' if fails == 0 else 'FAIL'}（{total - fails}/{total}）")
    return 0 if fails == 0 else 2


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--gate", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--prep-dir", default=None)
    ap.add_argument("--scan-summary", default=None)
    ns = ap.parse_args()
    prep = pathlib.Path(ns.prep_dir) if ns.prep_dir else PREP
    summary = pathlib.Path(ns.scan_summary) if ns.scan_summary else None
    if ns.selftest:
        return cmd_selftest()
    if ns.gate:
        return cmd_gate(prep, summary)
    return cmd_build(prep, summary)


if __name__ == "__main__":
    sys.exit(main())
