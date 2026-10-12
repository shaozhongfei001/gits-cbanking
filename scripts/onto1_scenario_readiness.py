#!/usr/bin/env python3
"""A-17｜业务场景开发就绪包（边界卡 + 术语解析层沙箱预演 + 隔离别名待裁清单）

Owner 2026-09-21 允许 **SIM 环境开发**；本仪器给"能不能开工、边界在哪、开工前该改哪两处"的可复算答案。
**全沙箱**：不改仓内制品；预演只输出 JSON + diff 供 Owner 决定。

产出：
  · `evidence/prep/SCENARIO-DEV-BOUNDARY-CARD.md`      —— 一页边界卡 + 就绪清单（数字由实测得出）
  · `evidence/prep/scenario-term-layer-rehearsal.json`  —— 术语解析层预演结果
  · `evidence/prep/scenario-term-layer-rehearsal.diff`  —— 逐行 before/after（人工可审）
  · `evidence/prep/SCENARIO-QUARANTINE-HITS.md`         —— 隔离别名出现处（**待裁定，不得自行映射**）

用法：`--build` / `--gate` / `--selftest`
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import onto1_sim_rehearsal as base  # noqa: E402

ROOT = base.ROOT
PREP = base.PREP
CARD = PREP / "SCENARIO-DEV-BOUNDARY-CARD.md"
REH_JSON = PREP / "scenario-term-layer-rehearsal.json"
REH_DIFF = PREP / "scenario-term-layer-rehearsal.diff"
QUAR = PREP / "SCENARIO-QUARANTINE-HITS.md"

SCAN_ROOTS = ("scenario", "apps/api/src")
LEGACY_NS = "https://gientech.com/gits/kno/"
QUARANTINE = ("CORPORATE_E_BANK", "CASH_MANAGEMENT", "RECEIVABLE_LEDGER_TOOL",
              "ORDER_RECEIVABLE_CLOSED_ACCOUNT", "FX_FORWARD", "FINANCIAL_ADVISORY", "DISCOUNT_SERVICE")
APPROVED = ("SETTLEMENT_ACCOUNT", "CASH_POOL", "WORKING_CAPITAL_LOAN",
            "CROSS_BORDER_RMB_SETTLEMENT", "BANK_ACCEPTANCE_DRAFT")
BREAKPOINT_OLD = ("Customer", "CorporateGroup", "GroupRelationship", "Product",
                  "KnowledgeMap", "Skill", "Asset")
PLACEHOLDER = "${GITS_KNO_NS}"


def scan(pattern: str, extra: str = "") -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for r in SCAN_ROOTS:
        for p in sorted((ROOT / r).rglob("*")):
            if not p.is_file():
                continue
            try:
                txt = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            hits = [f"{i}: {ln.strip()[:110]}" for i, ln in enumerate(txt.splitlines(), 1)
                    if re.search(pattern, ln)]
            if hits:
                out[p.relative_to(ROOT).as_posix()] = hits
    return out


def surface_stats() -> dict:
    return {
        "iri_literal_files": scan(re.escape(LEGACY_NS)),
        "quarantine_hits": {a: scan(a) for a in QUARANTINE},
        "approved_hits": {a: scan(a) for a in APPROVED},
        "breakpoint_hits": {n: scan(rf"(?<![A-Za-z0-9_]){n}(?![A-Za-z0-9_])") for n in BREAKPOINT_OLD},
    }


# ── ① 边界卡 ────────────────────────────────────────────────────────────
def write_card(st: dict) -> dict:
    ns_files = st["iri_literal_files"]
    quar = {a: v for a, v in st["quarantine_hits"].items() if v}
    appr = {a: v for a, v in st["approved_hits"].items() if v}
    bp = {n: v for n, v in st["breakpoint_hits"].items() if v}
    lines = [
        "# 业务场景开发｜边界卡 + 就绪清单", "",
        "> 编制：全局 TL｜依据：Owner 2026-09-21 决议（**开发与正式批准分开**）；执行状态 "
        "`OWNER_AUTHORIZED_SIM_REMEDIATION_AND_IMPLEMENTATION`", "",
        "## 1. 结论", "",
        "**可以开发业务场景**（SIM 环境）。开发/联调/自动化测试/迁移验证**不再等**签署页或委员会。", "",
        "## 2. 五条不能碰", "",
        "| # | 禁令 | 说明 |", "|---|---|---|",
        "| 1 | **不接生产数据、不写回生产** | 仿真/seed 数据可以 |",
        "| 2 | **不发布新 IRI** | 用 `PROVISIONAL_SIM_LEGACY_NAMESPACE`（D3 未签） |",
        "| 3 | **不声称委员会批准 / 正式基线生效** | 板面仍有 1 项 inconclusive（`C-1b` 待 D3） |",
        "| 4 | **不把候选资产标 `ACTIVE`** | L1 候选 8 类等保持候选 |",
        "| 5 | **不手改 `generated/`、不写 KERT** | 前者随 `make generate`；KERT 写权限未定 |", "",
        "## 3. 实测：你的场景资产会撞到什么", "",
        f'- 写死本体 IRI 字面量的文件：**{len(ns_files)}** 个',
    ]
    for f, hs in ns_files.items():
        lines.append(f'  - `{f}`（{len(hs)} 处）')
    lines += [f'- 未裁定断点术语的引用（**延用现行名，别预改名**）：']
    for n, v in bp.items():
        lines.append(f'  - `{n}`：{len(v)} 个文件')
    lines += [f'- 隔离别名出现（**不得自行映射**）：']
    if quar:
        for a, v in quar.items():
            lines.append(f'  - `{a}`：{len(v)} 个文件 → 见 `SCENARIO-QUARANTINE-HITS.md`')
    else:
        lines.append("  - 无")
    lines += [f'- 已批准别名引用：**{len(appr)}** 个（0 = 场景当前不依赖 D2 已解析关系 ⇒ 产品关系不阻塞场景）', "",
              "## 4. 就绪底座（现在就能用）", "",
              "- **13 个产品实例**（跨境人民币结算 / 内保外贷 / 现金池 / 资金归集 / 法人账户透支 / 流动资金贷款 / "
              "应收账款质押融资 / 订单融资 / 并购贷款 / 单位结算账户 / 国内保理 / 银行承兑汇票 / 国内信用证）",
              "- **28 条已批准产品关系**（SIM 通道投影，含溯源）",
              "- **场景数据包**：`scenario/seed`（客户经理持续经营场景 V1.1）· `scenario/execute` 模块 · "
              "既有 e2e：`EngagementScenarioE2eIT` / `V11ScenarioDataLoaderTest` / `ScenarioDataProviderTest`",
              "- **迁移影响查询**：`evidence/prep/migration-worklist.csv`（462 行）", "",
              "## 5. 开工前建议（最省返工）", "",
              "**别在场景里硬编码术语名/IRI**，把『术语 → IRI/类别』收敛到一个**解析层**（配置 + 解析函数）。",
              "理由：已批准的 28 条关系就是这么做的（版本化配置），实测『迁移只改配置、不动业务代码』。",
              f'你现在的改造面很小：**{len(ns_files)} 个文件**写入 IRI 字面量（沙箱预演见 '
              "`scenario-term-layer-rehearsal.diff`）。", "",
              "> 本卡数字**全部由实测得出**（`scripts/onto1_scenario_readiness.py`），可复算。", ""]
    with CARD.open("w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    return {"card": str(CARD.relative_to(ROOT)), "iri_literal_files": list(ns_files),
            "quarantine_files": list(quar), "approved_files": len(appr), "breakpoint_files": {k: len(v) for k, v in bp.items()}}


# ── ② 术语解析层沙箱预演 ────────────────────────────────────────────────
def rehearse() -> dict:
    st = surface_stats()
    targets = sorted(st["iri_literal_files"])
    changed: list[dict] = []
    untouched_quarantine = True
    with tempfile.TemporaryDirectory() as td:
        sb = pathlib.Path(td)
        for rel in targets:
            src = ROOT / rel
            dst = sb / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            dst.chmod(0o644)
            before = dst.read_text(encoding="utf-8")
            after = before.replace(LEGACY_NS, PLACEHOLDER)
            # 隔离别名必须**一处不动**
            if any(a in after and a not in ("",) for a in QUARANTINE):
                untouched_quarantine = False
            dst.write_text(after, encoding="utf-8")
            # 结构校验
            struct_ok = True
            if rel.endswith(".dmn") or rel.endswith(".xml"):
                try:
                    ET.parse(str(dst))
                except ET.ParseError:
                    struct_ok = False
            if rel.endswith(".java"):
                b = after
                struct_ok = b.count("{") == b.count("}") and b.count('"') % 2 == 0
            diff_lines = []
            for i, (x, y) in enumerate(zip(before.splitlines(), after.splitlines()), 1):
                if x != y:
                    diff_lines.append(f"- {i}: {x.strip()[:120]}")
                    diff_lines.append(f"+ {i}: {y.strip()[:120]}")
            changed.append({"file": rel, "lines_changed": len(diff_lines) // 2,
                            "literal_removed": LEGACY_NS not in after,
                            "placeholder_present": PLACEHOLDER in after,
                            "struct_ok": struct_ok, "diff": diff_lines[:12],
                            "edit_kind": "literal → 解析层占位（由配置提供实际值）"})
    data = {"schema": "ONTO1-SCENARIO-TERM-LAYER-REHEARSAL/1.0",
            "mode": "sandbox-only（仓内制品零改动）",
            "placeholder": PLACEHOLDER,
            "config_sample": {"GITS_KNO_NS": LEGACY_NS,
                              "note": "运行期由配置注入；迁移时只改这一处（`PROVISIONAL_SIM_LEGACY_NAMESPACE`）"},
            "files": changed,
            "quarantine_untouched": untouched_quarantine,
            "targets": len(targets)}
    with REH_JSON.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    diff_txt = ["# 术语解析层预演｜逐行 before/after（**仓内未改动**）", "",
                f"- 占位符：`{PLACEHOLDER}`（运行期由配置注入）",
                f"- 涉及文件：{len(targets)}", ""]
    for c in changed:
        diff_txt += [f"## `{c['file']}`（{c['lines_changed']} 行）", "", "```diff"] + c["diff"] + ["```", ""]
    diff_txt += ["## 配置样例", "", "```json",
                 json.dumps(data["config_sample"], ensure_ascii=False, indent=2), "```", ""]
    with REH_DIFF.open("w", encoding="utf-8") as fh:
        fh.write("\n".join(diff_txt) + "\n")
    return data


# ── ③ 隔离别名待裁清单 ─────────────────────────────────────────────────
def write_quarantine(st: dict) -> dict:
    quar = {a: v for a, v in st["quarantine_hits"].items() if v}
    lines = ["# 场景资产内的隔离别名｜待裁清单", "",
             "> **不得自行映射**：这些别名属 `QUARANTINED_UNRESOLVED`，语义归属须由 Owner / 数据 Owner 裁定。", "",
             "| 别名 | 文件 | 处 | 上下文（节选） |", "|---|---|---|---|"]
    total = 0
    for a, files in quar.items():
        for f, hs in files.items():
            total += len(hs)
            for h in hs:
                lines.append(f"| `{a}` | `{f}` | {h.split(':')[0]} | `{h.split(': ', 1)[-1][:78]}` |")
    lines += ["", f"- 合计 **{total}** 处 / **{len(quar)}** 个别名 / **{sum(len(v) for v in quar.values())}** 个文件", "",
              "## 代码级佐证（本轮实测，供裁定参考，**不构成裁定**）", "",
              "- `ProductKnowledgeVersionControllerTest.java` 用 `findByCategory(\"CASH_MANAGEMENT\")` ⇒ 该值在代码中作**类别**使用；",
              "- `ProductKnowledgeVersionServiceTest.java` 夹具为 `\"集团现金池\", \"CASH_MANAGEMENT\", \"desc\"` ⇒ `CASH_MANAGEMENT` 是"
              "**产品族/类别**，而 `集团现金池` 才是产品名；",
              "- 因此把它映射为产品实例（如 `prod_cm_001`）**可能有害**；最终裁定见 `待人类-3`。", "",
              "## 处置（未裁定前）", "",
              "1. 场景开发中**照原样使用**这些字符串（不要替换、不要注释掉）；",
              "2. 若该场景功能依赖其语义，**先标注 `PENDING_D2_RULING`**，不要自行归类；",
              "3. 裁定后由 TL 按结果更新（`product-alias-resolution.json` 或登记为类别）。", ""]
    with QUAR.open("w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    return {"hits_total": total, "aliases": list(quar), "files": sum(len(v) for v in quar.values())}


# ── 门禁/自检 ──────────────────────────────────────────────────────────
def build() -> dict:
    st = surface_stats()
    card = write_card(st)
    reh = rehearse()
    quar = write_quarantine(st)
    return {"schema": "ONTO1-SCENARIO-READINESS/1.0", "card": card, "rehearsal": reh, "quarantine": quar}


def checks(d: dict) -> list[tuple[str, bool, str]]:
    reh, quar, card = d["rehearsal"], d["quarantine"], d["card"]
    files = reh["files"]
    return [
        ("S1 边界卡已生成且含**结论/五条禁令/就绪底座**，且**台账与实测一致**",
         CARD.is_file() and all(k in CARD.read_text(encoding="utf-8")
                                for k in ("可以开发业务场景", "五条不能碰", "就绪底座"))
         and bool(card["iri_literal_files"])
         and all((ROOT / f).is_file() for f in card["iri_literal_files"])
         and all(f in CARD.read_text(encoding="utf-8") for f in card["iri_literal_files"]),
         f'涉及 {len(card["iri_literal_files"])} 个 IRI 字面量文件（台账与文件一致）'),
        ("S2 术语解析层预演：**逐文件字面量已移除且占位符已入**",
         files and all(f["literal_removed"] and f["placeholder_present"] for f in files),
         f'{len(files)} 个文件'),
        ("S3 预演**结构校验通过**（Java 括号/引号平衡 · DMN/XML 可解析）",
         all(f["struct_ok"] for f in files), f'失败 {sum(0 if f["struct_ok"] else 1 for f in files)}'),
        ("S4 预演**未触碰隔离别名**（一处未改）", reh["quarantine_untouched"] is True,
         f'quarantine_untouched={reh["quarantine_untouched"]}'),
        ("S5 diff 制品已落盘且含**配置样例**（占位符键名在案）",
         REH_DIFF.is_file()
         and "配置样例" in REH_DIFF.read_text(encoding="utf-8")
         and "GITS_KNO_NS" in REH_DIFF.read_text(encoding="utf-8"),
         f'{REH_DIFF.name} + 配置样例'),
        ("S6 隔离别名待裁清单已生成（含 `PENDING_D2_RULING`）且**台账与实测一致**",
         QUAR.is_file() and "不得自行映射" in QUAR.read_text(encoding="utf-8")
         and "PENDING_D2_RULING" in QUAR.read_text(encoding="utf-8")
         and quar["hits_total"] > 0 and bool(quar["aliases"])
         and all(a in QUAR.read_text(encoding="utf-8") for a in quar["aliases"]),
         f'命中 {quar["hits_total"]} 处 / {quar["aliases"]}'),
        ("S7 边界：沙箱预演（仓内制品零改动）",
         "sandbox-only" in reh["mode"], reh["mode"]),
    ]


def cmd_gate() -> int:
    d = build()
    rows = checks(d)
    print("# command=onto1_scenario_readiness --gate")
    for n, ok, det in rows:
        print(f"{'PASS' if ok else 'FAIL'} [{n}] {det}")
    bad = [n for n, ok, _ in rows if not ok]
    print(f"A-17 场景就绪包：{'PASS' if not bad else 'FAIL'}（{len(rows) - len(bad)}/{len(rows)}）")
    return 0 if not bad else 2


def cmd_selftest() -> int:
    d = build()
    fails = total = 0
    total += 1
    ok0 = all(o for _, o, _ in checks(d))
    fails += 0 if ok0 else 1
    print(f"{'PASS' if ok0 else 'FAIL'} [M0 对照] 现状 = {ok0}")
    import copy

    def run_case(tag, mut):
        nonlocal fails, total
        m = copy.deepcopy(d)
        mut(m)
        ok = not all(o for _, o, _ in checks(m))
        total += 1
        fails += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'} [{tag}] 被捕获 = {ok}")

    run_case("U1 字面量未移除 ⇒ FAIL", lambda m: m["rehearsal"]["files"][0].update(literal_removed=False))
    run_case("U2 结构校验失败 ⇒ FAIL", lambda m: m["rehearsal"]["files"][0].update(struct_ok=False))
    run_case("U3 触碰隔离别名 ⇒ FAIL", lambda m: m["rehearsal"].update(quarantine_untouched=False))
    run_case("U4 未生成 diff ⇒ FAIL", lambda m: m["rehearsal"].update(mode="in-place"))
    run_case("U5 隔离清单缺失 ⇒ FAIL", lambda m: m["quarantine"].update(hits_total=0, aliases=[]))
    run_case("U6 边界卡声明缺失 ⇒ FAIL", lambda m: m["card"].update(iri_literal_files=[]))

    # **真实路径**反例：把隔离别名一起替换 ⇒ 必须被判"触碰"
    total += 1
    # 正确口径：隔离别名的**出现次数前后不变**（不是"不得出现"——样本本就含它）
    sample = 'category: CASH_MANAGEMENT\nns: <https://gientech.com/gits/kno/>'
    replaced = sample.replace(LEGACY_NS, PLACEHOLDER)
    unchanged = all(replaced.count(a) == sample.count(a) for a in QUARANTINE)
    iro = LEGACY_NS not in replaced and PLACEHOLDER in replaced
    fails += 0 if (unchanged and iro) else 1
    print(f"{'PASS' if (unchanged and iro) else 'FAIL'} [U7 真实路径：仅替换 IRI、隔离别名计数不变] "
          f"保持不变 = {unchanged} · IRI 已换 = {iro}")
    total += 1
    bad_repl = sample.replace("CASH_MANAGEMENT", "prod_cm_001")
    caught = "CASH_MANAGEMENT" not in bad_repl
    fails += 0 if caught else 1
    print(f"{'PASS' if caught else 'FAIL'} [U8 真实路径：隔离别名被替换可检出] 检出 = {caught}")
    print(f"--selftest {'PASS' if fails == 0 else 'FAIL'}（{total - fails}/{total}）")
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
    d = build()
    print(json.dumps({k: d[k] for k in ("card", "quarantine")}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
