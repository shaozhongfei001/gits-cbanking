#!/usr/bin/env python3
"""施工计划与合同候选生成器（Owner 决议 2026-09-21 准备项 1、2）

产出（均标 `CANDIDATE_NOT_EFFECTIVE`，未正式生效）：
  · `evidence/prep/contract-split-candidates.json` + `ONTO1-CONTRACT-SPLIT-CANDIDATES-DRAFT.md`
      —— CTR-SEM-002 收窄 + CTR-SEM-003/004/005 拆分候选 + 影响清单 + 适用禁令
  · `evidence/prep/construction-plan.json` + `ONTO1-CONSTRUCTION-PLAN-DRAFT.md`
      —— 691 项真义务按**同类改造/依赖/可验证单元**聚为 8 批（**不是 691 次独立开发**）

用法：`--build`（默认）/ `--gate` / `--selftest`
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
EV = ROOT / "loops/ONTO1-ontology-split/evidence"
PREP = EV / "prep"
TRIAGE = EV / "obligation-triage.csv"

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
PROHIBITIONS = [
    "未签 D3 前**禁止发布新 IRI / 重钉**（执行计划 §WI-A4）",
    "WI-A2 命中处置表未 100% 处置前 **Wave 2 禁止开工**（执行计划 §WI-A2；当前处置率 100%、待回源 0）",
    "重构项**禁止**使用 `equivalentClass`（执行计划 §WI-1-3 校验④）",
    "D1 标准文本到手前**禁止任何国标符合性表述**（执行计划 §WI-A3）",
]


def batch_of(r: dict) -> str:
    s, _ = r["signal"], r["path"]
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


def build_plan(obligations: list[dict]) -> dict:
    by = collections.defaultdict(list)
    for r in obligations:
        by[batch_of(r)].append(r)
    batches = []
    for b, items in sorted(by.items()):
        batches.append({
            "id": b, "count": len(items),
            "repos": dict(collections.Counter(r["repo"] for r in items)),
            "waves": dict(collections.Counter(r["responsible_wave"] for r in items)),
            "tiers": dict(collections.Counter(r["tier"] for r in items)),
            "deps": DEPS.get(b, []), "verification": VERIFY.get(b, "按模块测试"),
            "sim_eligible": b in SIM_ELIGIBLE,
            "sample": [f'{r["repo"]}/{r["path"]}' for r in sorted(items, key=lambda x: x["path"])[:3]],
        })
    return {
        "schema": "ONTO1-CONSTRUCTION-PLAN/1.0",
        "basis": "691 真义务（obligation-triage.csv；待回源 = 0）",
        "principle": "**不是 691 次独立开发**：按同类改造聚类为批次；批次内可并行、批次间按依赖串行；每批以『可验证单元』定义完成。",
        "authority_status": "CANDIDATE（未正式生效；正式执行需合同拆条获批 + 相应签署）",
        "total": len(obligations),
        "external_gates": ["D3 正式根域（正式切换时）", "KERT 维护方写权限", "委员会签署页（正式基线）"],
        "prohibitions": PROHIBITIONS,
        "batches": batches,
    }


def build_contracts(obligations: list[dict]) -> dict:
    sem = sorted({r["path"] for r in obligations if r["path"].startswith("specs/semantic")})
    core = sorted({r["path"] for r in obligations
                   if "FILE_GITS_CORE" in r["signal"] or "gits-core" in (r["evidence"] or "")})
    return {
        "schema": "ONTO1-CONTRACT-SPLIT-CANDIDATES/1.0",
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
             "status": "CANDIDATE_NOT_EFFECTIVE"},
        ],
        "impact": {
            "CTR-SEM-002 登记 consumers": ["semantic_runtime"],
            "受影响义务数（去重）": len(set(sem) | set(core)),
            "specs/semantic 直接义务": sem,
            "引用 gits-core 的义务（样本）": core[:10],
            "受影响批次": ["B2_L1_L2_语义规格层", "B7_导入级耦合（代码导入本体包）", "B8_内容级重绑（IRI/词表/哈希）"],
        },
        "prohibitions_cited": PROHIBITIONS,
    }


def render_md(plan: dict, cand: dict) -> tuple[str, str]:
    md1 = ["# 候选合同与影响清单（DRAFT｜**未正式生效**）", "",
           "- 依据：Owner 决议 2026-09-21 准备项 1；执行计划 §74",
           f"- 状态：`{cand['status']}`", "",
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
           "| 批次 | 项数 | 仓库 | 波次 | 依赖 | 验证方式 | SIM 可先行 |",
           "|---|---|---|---|---|---|---|"]
    for b in plan["batches"]:
        md2.append(f"| `{b['id']}` | {b['count']} | {b['repos']} | {b['waves']} | {b['deps']} | "
                   f"{b['verification']} | {'✅' if b['sim_eligible'] else '需外部'} |")
    md2 += ["", f"**计数守恒**：各批次之和 = {plan['total']}（构建时断言）。",
            "", "## 外部前置", "- " + " · ".join(plan["external_gates"]),
            "", "## 适用禁令"] + [f"- {p}" for p in plan["prohibitions"]]
    return "\n".join(md1) + "\n", "\n".join(md2) + "\n"


def cmd_build() -> int:
    obs = load_obligations()
    plan, cand = build_plan(obs), build_contracts(obs)
    assert sum(b["count"] for b in plan["batches"]) == len(obs) == 691
    PREP.mkdir(parents=True, exist_ok=True)
    (PREP / "construction-plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (PREP / "contract-split-candidates.json").write_text(json.dumps(cand, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md1, md2 = render_md(plan, cand)
    (PREP / "ONTO1-CONTRACT-SPLIT-CANDIDATES-DRAFT.md").write_text(md1, encoding="utf-8")
    (PREP / "ONTO1-CONSTRUCTION-PLAN-DRAFT.md").write_text(md2, encoding="utf-8")
    print(f"已生成施工计划（{len(plan['batches'])} 批 / 合计 {plan['total']} 项）与合同候选（{len(cand['candidates'])} 项）")
    for b in plan["batches"]:
        print(f"   {b['count']:4d}  {b['id']}{'  [SIM 可先行]' if b['sim_eligible'] else ''}")
    return 0


def cmd_gate() -> int:
    obs = load_obligations()
    plan = json.loads((PREP / "construction-plan.json").read_text(encoding="utf-8"))
    cand = json.loads((PREP / "contract-split-candidates.json").read_text(encoding="utf-8"))
    rows = [
        ("P1 计数守恒", sum(b["count"] for b in plan["batches"]) == len(obs) == 691,
         f"批次和={sum(b['count'] for b in plan['batches'])} 真义务={len(obs)}"),
        ("P2 批次不重复覆盖", len(plan["batches"]) == len({b["id"] for b in plan["batches"]}), f"{len(plan['batches'])} 批"),
        ("P3 合同候选全部标 NOT_EFFECTIVE",
         all(c["status"] == "CANDIDATE_NOT_EFFECTIVE" for c in cand["candidates"]), "4 项候选"),
        ("P4 列明适用禁令", len(cand["prohibitions_cited"]) >= 4, f"{len(cand['prohibitions_cited'])} 条"),
        ("P5 影响清单非空", cand["impact"]["受影响义务数（去重）"] > 0, str(cand["impact"]["受影响义务数（去重）"])),
        ("P6 外部前置已声明", len(plan["external_gates"]) >= 3, str(plan["external_gates"])),
    ]
    for name, ok, d in rows:
        print(f"{'PASS' if ok else 'FAIL'} [{name}] {d}")
    bad = [n for n, ok, _ in rows if not ok]
    print(f"施工计划：{'PASS' if not bad else 'FAIL'}（{len(rows) - len(bad)}/{len(rows)}）")
    return 0 if not bad else 2


def cmd_selftest() -> int:
    obs = load_obligations()
    plan = build_plan(obs)
    fails = 0
    # M1 抽掉一项 ⇒ 计数不再守恒
    p2 = json.loads(json.dumps(plan))
    p2["batches"][0]["count"] -= 1
    ok1 = sum(b["count"] for b in p2["batches"]) != len(obs)
    print(f"{'PASS' if ok1 else 'FAIL'} [M1 计数被篡改 ⇒ 应被 P1 拦下] = {ok1}")
    fails += 0 if ok1 else 1
    # M2 合同候选取消 NOT_EFFECTIVE 标记 ⇒ 应被 P3 拦下
    cand = build_contracts(obs)
    cand["candidates"][0]["status"] = "EFFECTIVE"
    ok2 = not all(c["status"] == "CANDIDATE_NOT_EFFECTIVE" for c in cand["candidates"])
    print(f"{'PASS' if ok2 else 'FAIL'} [M2 候选被标 EFFECTIVE ⇒ 应被 P3 拦下] = {ok2}")
    fails += 0 if ok2 else 1
    # M3 克隆：真实文件与内存构建一致（防"文档与数据脱钩"）
    disk = json.loads((PREP / "construction-plan.json").read_text(encoding="utf-8"))
    ok3 = [b["count"] for b in disk["batches"]] == [b["count"] for b in plan["batches"]]
    print(f"{'PASS' if ok3 else 'FAIL'} [M3 磁盘计划与重建一致] = {ok3}")
    fails += 0 if ok3 else 1
    print(f"--selftest {'PASS' if fails == 0 else 'FAIL'}（{3 - fails}/3）")
    return 0 if fails == 0 else 2


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--gate", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ns = ap.parse_args()
    if ns.selftest:
        return cmd_selftest()
    if ns.gate:
        return cmd_gate()
    return cmd_build()


if __name__ == "__main__":
    sys.exit(main())
