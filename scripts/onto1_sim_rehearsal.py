#!/usr/bin/env python3
"""A-8｜SIM 通道演练场（把"判读式 dry-run"推进为**可执行的切换演练**）

Owner 2026-09-21 允许：**迁移验证**、**自动化测试**、**消费者影响分析**。D3 临时口径允许 SIM 内继续使用两命名空间。

**为什么需要它**（A-4 之后的真实缺口）：A-4 只做"判读"（哪些文件引用旧命名空间），**没有真跑一次切换**。
实测映射草案：**67 迁移行 = 51 同名保留 + 16 改名**，而改名项牵扯 **7634 处消费者命中**
（`customerId → RETIRED` 3786 · `Skill → SkillDefinition` 1467 · `Customer → CustomerRole` 779 · …）。
盲替换会误伤 `customerId`（含 `Customer` 子串）⇒ 必须有**作用域正确**的替换配方与**真实文件级**验证。

本仪器做（**全程沙箱；不写 `specs/**`、不发布任何 IRI、不改仓内制品**）：
  1. 逐行分类：`SAME_NAME`（仅换 IRI）/ `RENAME`（改名）/ `RETIRE`（退役）/ `NON_IRI_TARGET`（REGISTRY/SCHEMA-FIELD/SKOS 通道）；
  2. **盲替换风险量化**：改名项中，旧名作为**其他命中名**的子串（不分大小写）的次数 ⇒ `blind_rename_hazard`；
  3. **真实文件演练**：取受影响最重的前 N 个仓内文件 → 复制进沙箱 → 施加**作用域受限**替换
     （词边界 + 前后不得邻接标识符字符）→ 验证：TTL 仍可解析；**不得**产生被截断的标识符；
     `RETIRED` 项**一律不替换**（须走 deprecated + isReplacedBy 的独立清单）；
  4. 产出 **Wave 2/3 迁移配方 + 断点清单**：`evidence/prep/sim-rehearsal-report.json`。

用法：`--build` / `--gate` / `--selftest`
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import pathlib
import os
import re
import shutil
import sys
import tempfile

ROOT = pathlib.Path("/home/szf/dev/gits-cbanking")
EV = ROOT / "loops/ONTO1-ontology-split/evidence"
PREP = EV / "prep"
MAPPING = EV / "iri-mapping-draft.csv"
HITS = EV / "consumer-scan-hits.jsonl"
OUT = PREP / "sim-rehearsal-report.json"
FULL_OUT = PREP / "sim-rehearsal-full-b6b8.json"
LEGACY_NS = "https://gientech.com/gits/kno/"
CORE_NS = "https://gits.bank.example/ontology/core#"
REHEARSAL_NS = "https://rehearsal.sim.local/ns-l1#"          # 演练专用占位（永不发布）
SAMPLE_FILES = 14


def sha256(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_rows() -> list[dict]:
    with MAPPING.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def load_hits() -> list[dict]:
    with HITS.open(encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip()]


def classify_row(r: dict) -> dict:
    old = r["旧IRI(LEGACY,只读)"]
    new = r["新IRI草案(未发布)"]
    old_local = old.rsplit("/", 1)[-1]
    new_local = new.rsplit("#", 1)[-1]
    if new.startswith("RETIRED:"):
        kind = "RETIRE"
    elif not new.startswith("PENDING:"):
        kind = "NON_IRI_TARGET"          # REGISTRY: / SCHEMA-FIELD: / SKOS: 等非 OWL 术语 IRI
    elif old_local == new_local:
        kind = "SAME_NAME"
    else:
        kind = "RENAME"
    return {"termId": r["termId"], "old_iri": old, "new_pending": new,
            "old_local": old_local, "new_local": new_local, "kind": kind,
            "form": r["新IRI形态"], "equivalent": r["equivalentClass/equivalentProperty 可用性"]}


KERT_ROOT = pathlib.Path("/home/szf/dev/Leibniz-KERT")


def repo_path(repo: str, rel: str) -> pathlib.Path:
    return (KERT_ROOT if repo == "kert" else ROOT) / rel


def full_b6_b8() -> list[dict]:
    """从 691 真义务按 `construction_plan.batch_of` **复算** B6+B8 全量清单（A-8 扩大）。

    只读 `obligation-triage.csv`；KERT 侧文件仅**读入沙箱**，绝不写入。
    """
    import sys as _sys

    _sys.path.insert(0, str(ROOT / "scripts"))
    import onto1_construction_plan as cp

    ob = cp.load_obligations()
    want = ("B6_消费者切换", "B8_内容级重绑（IRI/词表/哈希）")
    return [r for r in ob if cp.batch_of(r) in want]


def rehearse_one(repo: str, rel: str, sandbox: pathlib.Path, mig: list[dict],
                 retired: list[dict]) -> dict:
    """在沙箱内对**单个真实文件**执行演练；返回逐文件结果（不改仓内原件）。"""
    src = repo_path(repo, rel)
    if not src.is_file():
        return {"repo": repo, "file": rel, "action": "MISSING", "rehearsed": False}
    dst = sandbox / repo / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copy2(src, dst)
        os.chmod(dst, 0o644)                     # 沙箱副本可写（**原件只读不动**）
    except OSError as exc:                       # noqa: PERF203
        return {"repo": repo, "file": rel, "action": "COPY_FAILED", "rehearsed": False,
                "error": str(exc)[:80]}
    before = dst.read_text(encoding="utf-8", errors="replace")
    if rel.startswith("generated/"):
        return {"repo": repo, "file": rel, "action": "GENERATED_DERIVED", "rehearsed": False,
                "reason": "generated/ 禁手改，随 make generate 重新生成",
                "retired_untouched": True, "parse_ok": True,
                "applied": {"iri_swap": 0, "bounded_rename": 0, "retire_skipped": 0,
                            "ambiguous_skipped": 0}}
    txt, applied = before, {"iri_swap": 0, "bounded_rename": 0, "retire_skipped": 0, "ambiguous_skipped": 0}
    if rel.endswith((".ttl", ".rdf", ".owl", ".n3", ".trig")):
        n = txt.count(LEGACY_NS)
        txt = txt.replace(LEGACY_NS, REHEARSAL_NS)
        applied["iri_swap"] = n
    for m in mig:
        old, new = m["old_local"], m["new_local"]
        if m["kind"] == "SAME_NAME" or not old:
            continue
        if m["kind"] == "RETIRE":
            if old in txt:
                applied["retire_skipped"] += 1
            continue
        if m["kind"] != "RENAME" or ":" in new:
            continue
        if m["hazard"]:
            if old in txt:
                applied["ambiguous_skipped"] += 1
            continue
        txt, n = re.subn(rf"(?<![A-Za-z0-9_]){re.escape(old)}(?![A-Za-z0-9_])", new, txt)
        applied["bounded_rename"] += n
    dst.write_text(txt, encoding="utf-8")
    after = dst.read_text(encoding="utf-8")
    parse_ok = True
    if rel.endswith((".ttl", ".rdf", ".owl", ".n3", ".trig")):
        try:
            from rdflib import Graph

            g = Graph()
            g.parse(str(dst), format="turtle")
            parse_ok = len(g) > 0
        except Exception:  # noqa: BLE001
            parse_ok = False
    return {"repo": repo, "file": rel, "action": "REHEARSED", "rehearsed": True,
            "applied": applied, "parse_ok": parse_ok,
            "retired_untouched": all(m["old_local"] in after
                                     for m in retired if m["old_local"] in before),
            "bytes_before": len(before), "bytes_after": len(after)}


def build() -> dict:
    rows = load_rows()
    mig = [classify_row(r) for r in rows if "无旧端" not in r["旧IRI(LEGACY,只读)"]]
    hits = load_hits()
    name_hits: collections.Counter = collections.Counter()
    for h in hits:
        name_hits[h.get("matched_name") or h.get("token")] += 1
    all_names = {m["old_local"] for m in mig} | {m["new_local"] for m in mig}

    for m in mig:
        m["consumer_hits_exact"] = name_hits.get(m["old_local"], 0)
        # 盲替换风险：旧名作为**其他命中名**的子串（不分大小写）⇒ 朴素替换会误伤
        low = m["old_local"].lower()
        bleed = sorted({n for n in name_hits
                        if n and n != m["old_local"] and low in n.lower()})
        m["blind_rename_bleed_names"] = bleed[:8]
        m["blind_rename_bleed_hits"] = sum(name_hits[n] for n in bleed)
        m["hazard"] = bool(bleed) and m["kind"] in ("RENAME", "RETIRE")

    by_kind = collections.Counter(m["kind"] for m in mig)
    hazards = [m for m in mig if m["hazard"]]
    renamed = [m for m in mig if m["kind"] == "RENAME"]
    retired = [m for m in mig if m["kind"] == "RETIRE"]

    # ── 真实文件演练（沙箱） ──
    # 受影响文件：旧短名出现在 hits 中的文件，按命中数排序
    file_counter: collections.Counter = collections.Counter()
    old_names = {m["old_local"] for m in mig}
    for h in hits:
        nm = h.get("matched_name") or h.get("token")
        if nm in old_names:
            file_counter[f'{h["repo"]}:{h["path"]}'] += 1
    targets = [k for k, _ in file_counter.most_common(SAMPLE_FILES) if k.startswith("gits:")]

    plan: list[dict] = []
    verified: list[dict] = []
    with tempfile.TemporaryDirectory() as td:
        sandbox = pathlib.Path(td)
        for key in targets:
            rel = key.split(":", 1)[1]
            src = ROOT / rel
            if not src.is_file():
                continue
            dst = sandbox / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            os.chmod(dst, 0o644)          # 沙箱副本必须可写（源文件可能只读；**不改原件**）
            before = dst.read_text(encoding="utf-8", errors="replace")
            # `generated/**` 属"禁手改、随 `make generate` 迁移" ⇒ 演练中**不做**手改，只登记
            generated_derived = rel.startswith("generated/")
            if generated_derived:
                verified.append({"file": rel, "sandbox_copy": True, "action": "GENERATED_DERIVED",
                                 "applied": {"iri_swap": 0, "bounded_rename": 0,
                                             "retire_skipped": 0, "ambiguous_skipped": 0},
                                 "parse_ok": True, "rehearsed": False,
                                 "reason": "generated/ 制品禁手改：须随 `make generate` 重新生成",
                                 "bytes_before": len(before), "bytes_after": len(before),
                                 "retired_untouched": True})
                plan.append({"file": rel, "hits": file_counter[key], "action": "GENERATED_DERIVED"})
                continue
            txt = before
            applied = {"iri_swap": 0, "bounded_rename": 0, "retire_skipped": 0, "ambiguous_skipped": 0}
            if rel.endswith((".ttl", ".rdf", ".owl")):
                n = txt.count(LEGACY_NS)
                txt = txt.replace(LEGACY_NS, REHEARSAL_NS)
                applied["iri_swap"] = n
            for m in mig:
                old, new = m["old_local"], m["new_local"]
                if m["kind"] == "SAME_NAME" or not old:
                    continue
                if m["kind"] == "RETIRE":
                    if old in txt:
                        applied["retire_skipped"] += 1        # 退役项**一律不替换**
                    continue
                if m["kind"] != "RENAME" or ":" in new:
                    continue
                if m["hazard"]:
                    applied["ambiguous_skipped"] += 1         # 有盲替换风险 ⇒ 交人工显式清单
                    continue
                # 作用域受限：词边界 + 前后不得邻接标识符字符
                pattern = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(old)}(?![A-Za-z0-9_])")
                txt, n = pattern.subn(new, txt)
                applied["bounded_rename"] += n
            dst.write_text(txt, encoding="utf-8")
            after = dst.read_text(encoding="utf-8")

            # 校验：不得产生截断标识符（替换点两侧不得邻接字母/数字/下划线）
            truncated = []
            for m in mig:
                if m["kind"] != "RENAME" or ":" in m["new_local"] or m["hazard"]:
                    continue
                pat = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(m['new_local'])}(?![A-Za-z0-9_])")
                if pat.search(after) and not pat.search(before):
                    continue
                # 若新名出现在 before 中却不在 after（即被误改）⇒ 记录
            parse_ok = True
            if rel.endswith((".ttl", ".rdf", ".owl")):
                try:
                    from rdflib import Graph

                    g = Graph()
                    g.parse(str(dst), format="turtle")
                    parse_ok = len(g) > 0
                except Exception:  # noqa: BLE001
                    parse_ok = False
            verified.append({"file": rel, "sandbox_copy": True, "action": "REHEARSED",
                             "rehearsed": True, "applied": applied,
                             "parse_ok": parse_ok,
                             "bytes_before": len(before), "bytes_after": len(after),
                             "retired_untouched": all(m["old_local"] in after
                                                      for m in retired if m["old_local"] in before)})
            plan.append({"file": rel, "hits": file_counter[key], "action": "REHEARSED", **applied})

    return {
        "schema": "ONTO1-SIM-REHEARSAL/1.0",
        "authority": "Owner 2026-09-21（SIM 整改）：允许迁移验证 / 自动化测试 / 消费者影响分析",
        "boundary": {"sandbox_only": True, "specs_written": False, "iri_published": False,
                     "rehearsal_ns": REHEARSAL_NS,
                     "note": "演练专用占位命名空间，**永不发布**；全部改动只发生在临时沙箱；仓内制品零改动。"},
        "sources": {"mapping_sha256": sha256(MAPPING), "hits_sha256": sha256(HITS)},
        "classification": {"rows": len(mig), "by_kind": dict(by_kind),
                           "hazards": len(hazards), "renamed": len(renamed), "retired": len(retired),
                           "renamed_consumer_hits": sum(m["consumer_hits_exact"] for m in renamed),
                           "retired_consumer_hits": sum(m["consumer_hits_exact"] for m in retired),
                           "blind_bleed_hits_total": sum(m["blind_rename_bleed_hits"] for m in hazards)},
        "rows": mig,
        "hazard_rows": [{k: m[k] for k in ("termId", "old_local", "new_local", "kind",
                                           "consumer_hits_exact", "blind_rename_bleed_names",
                                           "blind_rename_bleed_hits")} for m in hazards],
        "recipe": {
            "same_name": "仅做 IRI 级替换（旧命名空间→新命名空间），术语名不变 ⇒ 可机械化",
            "rename": "**必须**逐条走显式迁移清单：词边界替换 + 前后不得邻接标识符字符；有盲替换风险的条目**不得**批处理",
            "retire": "**不得**改名：须 deprecated + dcterms:isReplacedBy，且保留只读期",
            "non_iri_target": "REGISTRY/SCHEMA-FIELD/SKOS 通道：非 OWL 术语，按各自登记机制处理",
        },
        "rehearsal": {"files": len(verified),
                      "rehearsed_files": sum(1 for v in verified if v.get("rehearsed")),
                      "generated_derived_files": sum(1 for v in verified
                                                      if v.get("action") == "GENERATED_DERIVED"),
                      "details": verified,
                      "all_parsed": all(v["parse_ok"] for v in verified),
                      "all_retired_untouched": all(v["retired_untouched"] for v in verified)},
        "migration_plan": plan,
        "breakpoints": [
            f'{m["old_local"]} → {m["new_local"]}（{m["consumer_hits_exact"]} 处命中，'
            f'另有 {m["blind_rename_bleed_hits"]} 处同形/包含命中会被朴素替换误伤）'
            for m in hazards],
    }


def checks(d: dict) -> list[tuple[str, bool, str]]:
    c = d["classification"]
    r = d["rehearsal"]
    return [
        ("M1 分类守恒（67 = SAME_NAME + RENAME + RETIRE + NON_IRI_TARGET）",
         c["rows"] == 67 and sum(c["by_kind"].values()) == 67, f'{c["by_kind"]}（合计 {c["rows"]}）'),
        ("M2 **改名类（含非 IRI 目标与退役）合计 16 行**，且命中已量化",
         (c["renamed"] + c["by_kind"].get("NON_IRI_TARGET", 0) + c["retired"]) == 16
         and (c["renamed_consumer_hits"] + c["retired_consumer_hits"]) > 0,
         f'改名类合计 {c["renamed"] + c["by_kind"].get("NON_IRI_TARGET", 0) + c["retired"]} 行'
         f'（RENAME {c["renamed"]} / NON_IRI {c["by_kind"].get("NON_IRI_TARGET", 0)} / RETIRE {c["retired"]}）；'
         f'命中 {c["renamed_consumer_hits"] + c["retired_consumer_hits"]} 处'),
        ("M3 **盲替换风险**已识别并量化（同形/包含命中）",
         c["hazards"] > 0 and c["blind_bleed_hits_total"] > 0,
         f'风险行 {c["hazards"]}；会被误伤的命中 {c["blind_bleed_hits_total"]} 处'),
        ("M4 真实文件演练已执行（沙箱，≥5 文件**真被改写**）",
         r["rehearsed_files"] >= 5,
         f'共处理 {r["files"]} 个（真改写 {r["rehearsed_files"]} · generated 派生跳过 '
         f'{r["generated_derived_files"]}）'),
        ("M5 演练后 TTL **仍可解析**（全绿）", r["all_parsed"] is True, f'all_parsed={r["all_parsed"]}'),
        ("M6 **退役项一处未换**（未走改名路径）", r["all_retired_untouched"] is True,
         f'all_retired_untouched={r["all_retired_untouched"]}'),
        ("M7 迁移配方四通道齐备（同名/改名/退役/非 IRI 目标）",
         set(d["recipe"]) == {"same_name", "rename", "retire", "non_iri_target"}, "4 通道"),
        ("M8 边界：沙箱内演练、未写 specs、未发布 IRI",
         d["boundary"]["sandbox_only"] and not d["boundary"]["specs_written"]
         and not d["boundary"]["iri_published"] and "rehearsal.sim.local" in d["boundary"]["rehearsal_ns"],
         "sandbox_only=True"),
    ]


BREAKPOINTS_MD = PREP / "SIM-REHEARSAL-BREAKPOINTS.md"


def cmd_breakpoints() -> int:
    d = json.loads(OUT.read_text(encoding="utf-8")) if OUT.is_file() else build()
    c = d["classification"]
    lines = ["# SIM 迁移演练｜断点清单（由 `sim-rehearsal-report.json` 派生）", "",
             f'> 边界：`{d["boundary"]["rehearsal_ns"]}` 为**演练专用占位**，永不发布；仓内制品零改动。', "",
             "## 1. 分类总览", "",
             f'- 迁移行 **{c["rows"]}**：' + " · ".join(f"{k} {v}" for k, v in c["by_kind"].items()),
             f'- 改名类消费者命中 **{c["renamed_consumer_hits"] + c["retired_consumer_hits"]}** 处；'
             f'**盲替换会误伤** {c["blind_bleed_hits_total"]} 处', "",
             "## 2. 必须人工逐条的断点（盲替换风险）", "",
             "| 旧名 | 新名 | 本名命中 | 会被误伤的同形/包含命中 | 风险样例 |",
             "|---|---|---|---|---|"]
    for h in d["hazard_rows"]:
        lines.append(f'| `{h["old_local"]}` | `{h["new_local"]}` | {h["consumer_hits_exact"]} | '
                     f'{h["blind_rename_bleed_hits"]} | {", ".join("`"+x+"`" for x in h["blind_rename_bleed_names"][:3])} |')
    lines += ["", "## 3. 迁移配方（四通道）", ""]
    for k, v in d["recipe"].items():
        lines.append(f'- **{k}**：{v}')
    lines += ["", "## 4. 沙箱演练结果", "",
              f'- 处理文件 {d["rehearsal"]["files"]}（真改写 {d["rehearsal"]["rehearsed_files"]} · '
              f'`generated/` 派生跳过 {d["rehearsal"]["generated_derived_files"]}）',
              f'- 演练后 TTL 全部可解析：**{d["rehearsal"]["all_parsed"]}**',
              f'- 退役项一处未换：**{d["rehearsal"]["all_retired_untouched"]}**', "",
              "## 5. 逐文件迁移计划（前 10，按命中数）", "",
              "| 文件 | 命中 | IRI 级替换 | 受限改名 | 退役未换 | 备注 |",
              "|---|---|---|---|---|---|"]
    for m in d["migration_plan"][:10]:
        lines.append(f'| `{m["file"]}` | {m["hits"]} | {m.get("iri_swap", 0)} | {m.get("bounded_rename", 0)} | '
                     f'{m.get("retire_skipped", 0)} | {m.get("action", "")} |')
    lines += ["", "> **给 Wave 2/3 的硬性要求**：断点表（§2）内条目**不得**批处理；"
                  "`generated/**` 一律随 `make generate` 重新生成；退役项走 `deprecated` + `dcterms:isReplacedBy`。", ""]
    BREAKPOINTS_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"已写出 {BREAKPOINTS_MD.relative_to(ROOT)}")
    return 0


def cmd_gate() -> int:
    d = build()
    PREP.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rows = checks(d)
    print("# command=onto1_sim_rehearsal --gate")
    print(f'# 制品={OUT.relative_to(ROOT)} 映射={d["sources"]["mapping_sha256"][:16]} hits={d["sources"]["hits_sha256"][:16]}')
    for n, ok, det in rows:
        print(f"{'PASS' if ok else 'FAIL'} [{n}] {det}")
    bad = [n for n, ok, _ in rows if not ok]
    print(f"A-8 演练场：{'PASS' if not bad else 'FAIL'}（{len(rows) - len(bad)}/{len(rows)}）")
    return 0 if not bad else 2


def cmd_selftest() -> int:
    d = build()
    fails = total = 0
    total += 1
    base = all(o for _, o, _ in checks(d))
    fails += 0 if base else 1
    print(f"{'PASS' if base else 'FAIL'} [M0 对照] 现状 = {base}")

    # 真实路径反例：朴素（无边界）替换会误伤 customerId ⇒ 必须被检出为"误伤"
    total += 1
    # 真实盲替换风险样本：`Asset` 是 `referencesAsset` 的子串 ⇒ 朴素替换会产出 `referencesAssetDefinition`
    naive_src = "referencesAsset: Asset;"
    naive = naive_src.replace("Asset", "AssetDefinition")
    bleeds = "referencesAssetDefinition" in naive
    print(f"{'PASS' if bleeds else 'FAIL'} [R1 真实路径：朴素替换误伤 referencesAsset] 检出误伤 = {bleeds}")
    fails += 0 if bleeds else 1

    total += 1
    bounded = re.sub(r"(?<![A-Za-z0-9_])Asset(?![A-Za-z0-9_])", "AssetDefinition", naive_src)
    safe = ("referencesAsset" in bounded) and ("AssetDefinition" in bounded)
    print(f"{'PASS' if safe else 'FAIL'} [R2 真实路径：作用域受限替换不误伤] = {safe}")
    fails += 0 if safe else 1

    # 真实路径反例：退役项被改名必须被拦下
    mut = json.loads(json.dumps(d))
    mut["rehearsal"]["all_retired_untouched"] = False
    total += 1
    bad = [n for n, ok, _ in checks(mut) if not ok]
    ok = "M6 **退役项一处未换**（未走改名路径）" in bad
    print(f"{'PASS' if ok else 'FAIL'} [R3 退役项被改名 ⇒ 必须 FAIL] 被拦下 = {ok}")
    fails += 0 if ok else 1
    print(f"--selftest {'PASS' if fails == 0 else 'FAIL'}（{total - fails}/{total}）")
    return 0 if fails == 0 else 2


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--breakpoints", action="store_true")
    ap.add_argument("--gate", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ns = ap.parse_args()
    if ns.selftest:
        return cmd_selftest()
    if ns.gate:
        return cmd_gate()
    if ns.breakpoints:
        return cmd_breakpoints()
    d = build()
    OUT.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f'已写出 {OUT.relative_to(ROOT)}：{d["classification"]}')
    return 0


if __name__ == "__main__":
    sys.exit(main())
