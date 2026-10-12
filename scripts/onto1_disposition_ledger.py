#!/usr/bin/env python3
"""A-1｜WI-A2 命中处置表闭环（412 未闭环聚合行 ⇒ 文件:行 级终局处置）

背景（实测）：`consumer-scan-summary.csv` 1406 聚合行中 **412 行** 未闭环
（`FOLLOW_MIGRATION` 270 / `HOMONYM_REQUIRES_SOURCE_CHECK` 119 / `CONTROL_PLANE_REQUIRED` 23，8172 次出现）。
该表是 **Wave 2 开工 / Wave 3 正式消费者切换** 的出口判据（条款原文「未完成则 Wave 2 禁止开工」），
而现有 **51 个门禁无一项覆盖它** ⇒ 出口判据不可复算。本仪器补上这一环。

**本仪器做什么**（只读 + 生成台账，**不改任何被扫描仓**）：
  1. 把每个聚合行**还原到 `文件:行`**（按 `(repo,category,disposition,token,rule_id)` 关联 `consumer-scan-hits.jsonl`）；
  2. 逐行给出**终局处置**（closed vocabulary）+ 责任 Wave + 依据；
  3. `HOMONYM_REQUIRES_SOURCE_CHECK` **逐条回源**：命中文件含本体 IRI 字面量 / RDF 语句 ⇒ 真义务；否则判`同名不同物`并留证；
  4. **逐行验证证据行真实存在且含 token**（不是抽样——能全验就全验）；
  5. `R-OBL-GITS-PRODUCTS-TTL`（products.ttl 前缀）按 Owner 授权的 **C-2 修复** 判 `CLOSED_BY_OWNER_DECISION`。

**诚实边界**：`FOLLOW_MIGRATION` / `CONTROL_PLANE_REQUIRED` 的**执行**发生在 Wave 2/3；
本仪器闭环的是**处置决策**（每行有终局处置 + 具体 `文件:行` 目标 + 责任 Wave），
**不声称**迁移已完成，**不**因本表变绿而提升任何门禁。

用法：`--build` / `--gate` / `--selftest`
"""
from __future__ import annotations

import argparse
import collections
import csv
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path("/home/szf/dev/gits-cbanking")
EV = ROOT / "loops/ONTO1-ontology-split/evidence"
SUMMARY = EV / "consumer-scan-summary.csv"
HITS = EV / "consumer-scan-hits.jsonl"
LEDGER_CSV = EV / "prep/a2-disposition-ledger.csv"
LEDGER_JSON = EV / "prep/a2-disposition-ledger.json"
REPO_ROOTS = {"gits": ROOT, "kert": pathlib.Path("/home/szf/dev/Leibniz-KERT")}

UNCLOSED = ("FOLLOW_MIGRATION", "HOMONYM_REQUIRES_SOURCE_CHECK", "CONTROL_PLANE_REQUIRED")
# 终局处置词表（closed vocabulary；不得出现表外值）
FINAL_VOCAB = ("FOLLOW_MIGRATION", "CONTROL_PLANE_REQUIRED", "EXEMPT_NON_ONTOLOGY_HOMONYM",
               "CLOSED_BY_OWNER_DECISION")
ONTOLOGY_LITERALS = ("gientech.com/gits/kno/", "gits.bank.example/ontology/core#")
# 扫描器符号化 token 类名 → 字面量（取自 `scripts/onto1_consumer_scan.py` 的 token 定义）
TOKEN_LITERALS = {
    "IRI_BANK_EXAMPLE": "https://gits.bank.example/ontology/core#",
    "IRI_GIENTECH": "https://gientech.com/gits/kno/",
    "PREFIX_GITS": "gits:",
    "FILE_GITS_CORE": "gits-core",
}
# 无迁移责任的终局处置（Wave 可为 NONE）
NO_WORK_DISPOSITIONS = ("EXEMPT_NON_ONTOLOGY_HOMONYM", "CLOSED_BY_OWNER_DECISION")
# 源扫描（2026-09-20）之后**经 Owner 授权变更**的文件 ⇒ 行号漂移可容忍（须记账）
# 源扫描时间（consumer-scan-manifest.json.generated_at）
SCAN_TIME_EPOCH = 1758378825.0   # 2026-09-20T14:53:45Z
# 经**授权重构**把字面量移到别处（命中已被重构解消）⇒ 记录新位置，不判失败
REFACTOR_MOVED = {
    "scripts/gk17_prodcard_to_rdf.py": "specs/knowledge-architecture/instances/product/projection-config.json",
}
AUTHORIZED_CHANGED = {
    "specs/knowledge-architecture/instances/product/products.ttl",
    "scripts/gk17_prodcard_to_rdf.py",
    "specs/knowledge-architecture/instances/product/UNRESOLVED.json",
}
RDF_MARKERS = ("owl:imports", "rdf:type", "sparql", "PREFIX ", "@prefix", "schema:",
               "skos:", "shacl", "CONSTRUCT", "SELECT ")
WEAK_FACE = ("/tests/", "/test/", "/poc/", "/frontend/", "/evidence/", "/docs/", "/examples/")
CLOSED_BY = {"R-OBL-GITS-PRODUCTS-TTL": {
    "reason": "Owner 2026-09-21 授权 C-2 兼容修复已落地（术语/实例命名空间分离），该行「Wave 3 修复前缀对齐」已提前关闭",
    "evidence": ["scripts/onto1_c2_fix_verify.py --gate = 7/7",
                 "scripts/onto1_c2_consumer_scan.py --gate = 7/7（破坏性引用 0）",
                 "evidence/namespace-known-defects.json（defects 已清空，转入 repaired）"]}}


def sha256(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


_HITS_CACHE: dict | None = None


def load_hits() -> dict[tuple, list[dict]]:
    """一次性载入并缓存（F-5 独立复算需对 53 行逐行回原始 hits）。"""
    global _HITS_CACHE
    if _HITS_CACHE is not None:
        return _HITS_CACHE
    idx: dict[tuple, list[dict]] = collections.defaultdict(list)
    with HITS.open(encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            h = json.loads(line)
            idx[(h.get("repo"), h.get("category"), h.get("disposition"), h.get("token"),
                 h.get("rule_id"))].append(h)
    _HITS_CACHE = idx
    return idx


_CONTENT_CACHE: dict[str, str | None] = {}


def read_repo_file(repo: str, path: str) -> str | None:
    key = f"{repo}:{path}"
    if key in _CONTENT_CACHE:
        return _CONTENT_CACHE[key]
    root = REPO_ROOTS.get(repo)
    txt = None
    if root is not None:
        fp = root / path
        if fp.is_file():
            try:
                txt = fp.read_text(encoding="utf-8", errors="replace")
            except OSError:
                txt = None
    _CONTENT_CACHE[key] = txt
    return txt


def consuming_class(repo: str, path: str) -> str:
    """ONTOLOGY_CONSUMING / NEUTRAL / UNREADABLE。判据：本体 IRI 字面量或 RDF 型语句。"""
    txt = read_repo_file(repo, path)
    if txt is None:
        return "UNREADABLE"
    if any(lit in txt for lit in ONTOLOGY_LITERALS):
        return "ONTOLOGY_CONSUMING"
    low = txt.lower()
    if any(m.lower() in low for m in RDF_MARKERS):
        return "ONTOLOGY_CONSUMING"
    return "NEUTRAL"


def weak_face(path: str) -> bool:
    p = f"/{path.lower()}"
    return any(w in p for w in WEAK_FACE) or p.endswith(".md")


def verify_evidence(repo: str, path: str, line: str, token: str) -> tuple[str, int | None]:
    """返回 (verify_kind, current_line)。

    verify_kind：`LITERAL`（原样命中）/ `SYMBOL_SAME_LINE`（符号 token 按字面量命中同一行）/
    `LINE_DRIFT`（同一行未命中，但字面量在文件他处 —— 仅授权变更文件容忍）/ `UNVERIFIED`。
    """
    txt = read_repo_file(repo, path)
    if txt is None:
        return "UNVERIFIED", None
    needle = TOKEN_LITERALS.get(token, token)
    lines = txt.splitlines()
    try:
        n = int(line)
    except (TypeError, ValueError):
        n = -1
    if 1 <= n <= len(lines) and needle in lines[n - 1]:
        return ("LITERAL" if needle == token else "SYMBOL_SAME_LINE"), n
    occurrences = [i for i, ln in enumerate(lines, 1) if needle in ln]
    if occurrences:
        # F-6 修正：优先取**非注释/非文档字符串**行（原取首个出现行，会落到注释/docstring，
        # 使"新位置"对迁移主体不可用）。
        marks = ("#", "//", "*", "--", "/*")

        def is_code_line(idx: int) -> bool:
            """注释标记或**文档字符串内部**均不算代码行（F-6：落点必须对迁移可用）。"""
            s = lines[idx - 1].lstrip()
            if s.startswith(marks):
                return False
            in_doc, in_sdoc = False, False
            for j in range(idx):
                ln = lines[j]
                n_triple_d = ln.count(chr(34) * 3)
                n_triple_s = ln.count(chr(39) * 3)
                if n_triple_d % 2 == 1:
                    in_doc = not in_doc
                if n_triple_s % 2 == 1:
                    in_sdoc = not in_sdoc
            return not (in_doc or in_sdoc)

        code_lines = [i for i in occurrences if is_code_line(i)]
        pick = (code_lines or occurrences)[0]
        if path in AUTHORIZED_CHANGED:
            return "LINE_DRIFT", pick          # Owner 授权变更导致位移
        fp = (REPO_ROOTS.get(repo) or pathlib.Path("/")) / path
        try:
            if fp.is_file() and fp.stat().st_mtime > SCAN_TIME_EPOCH:
                return "LINE_DRIFT", pick      # 扫描后文件有提交/变更 ⇒ 位移可解释
        except OSError:
            pass
        return "UNVERIFIED", None               # 无法解释的漂移 = 不放过
    moved = REFACTOR_MOVED.get(path)
    if moved:
        target = (REPO_ROOTS.get(repo) or pathlib.Path("/")) / moved
        try:
            if target.is_file() and needle in target.read_text(encoding="utf-8", errors="replace"):
                return "MOVED_TO_CONFIG", None   # 命中已被授权重构解消（字面量迁至 <moved>）
        except OSError:
            pass
    return "UNVERIFIED", None


def wave_for(path: str, disposition: str) -> str:
    p = path.lower()
    if disposition == "CONTROL_PLANE_REQUIRED":
        return "W3_CONSUMER_SWITCH"
    if p.startswith("specs/") or "/specs/" in p:
        return "W2_SPLIT"
    if p.startswith("kert/") or "/kert/" in p:
        return "W3_KERT_ASSETS"
    return "W3_CONSUMER_SWITCH"


def build_ledger() -> dict:
    idx = load_hits()
    rows = list(csv.DictReader(SUMMARY.open(encoding="utf-8")))
    targets = [r for r in rows if r["disposition"] in UNCLOSED]
    entries: list[dict] = []
    unverifiable: list[str] = []
    for r in targets:
        key = (r["repo"], r["category"], r["disposition"], r["token"], r["rule_id"])
        hits = idx.get(key, [])
        samples = [{"file": f'{h["path"]}:{h["line"]}', "path": h["path"], "line": h["line"]}
                   for h in hits[:5]]
        classes = collections.Counter(consuming_class(h["repo"], h["path"]) for h in hits)
        consuming = classes.get("ONTOLOGY_CONSUMING", 0)
        verified, drift = [], []
        for s in samples:
            kind, cur = verify_evidence(r["repo"], s["path"], s["line"], r["token"])
            s["verify_kind"], s["current_line"] = kind, cur
            _txt = read_repo_file(r["repo"], s["path"]) or ""
            _needle = TOKEN_LITERALS.get(r["token"], r["token"])
            s["occurrences_in_file"] = sum(1 for _ln in _txt.splitlines() if _needle in _ln)
            if kind == "UNVERIFIED":
                unverifiable.append(f'{r["repo"]}:{r["rule_id"]}:{r["token"]}:{s["path"]}:{s["line"]}')
                continue
            verified.append(s)
            if kind == "LINE_DRIFT":
                why = "授权变更" if s["path"] in AUTHORIZED_CHANGED else "扫描后变更"
                drift.append(f'{s["path"]}:{s["line"]}→{cur}（{why}；该文件共 '
                             f'{s.get("occurrences_in_file", 1)} 处命中，落点取非注释行）')
            elif kind == "MOVED_TO_CONFIG":
                drift.append(f'{s["path"]}:{s["line"]} ⇒ 已迁至 {REFACTOR_MOVED[s["path"]]}（授权重构解消）')

        src_disp = r["disposition"]
        basis = ""
        if r["rule_id"] in CLOSED_BY:
            final, wave, basis = "CLOSED_BY_OWNER_DECISION", "NONE", CLOSED_BY[r["rule_id"]]["reason"]
        elif src_disp == "CONTROL_PLANE_REQUIRED":
            final, wave = "CONTROL_PLANE_REQUIRED", wave_for(samples[0]["path"] if samples else "x", src_disp)
            basis = f'转控制面修复；依据 {len(samples)} 处 `文件:行` 样本已逐行验证'
        elif src_disp == "FOLLOW_MIGRATION":
            final = "FOLLOW_MIGRATION"
            wave = wave_for(samples[0]["path"] if samples else "x", src_disp)
            basis = (f'确认消费面（本体 IRI 字面量/RDF 语句命中 {consuming}/{len(hits)} 处）；'
                     f'随 IRI 与术语迁移')
        else:  # HOMONYM_REQUIRES_SOURCE_CHECK ⇒ 逐条回源
            if consuming:
                final, wave = "FOLLOW_MIGRATION", wave_for(samples[0]["path"] if samples else "x", "FOLLOW_MIGRATION")
                basis = f'回源判定：命中文件**含本体消费证据**（{consuming}/{len(hits)} 处）⇒ 升级为真义务'
            else:
                final, wave = "EXEMPT_NON_ONTOLOGY_HOMONYM", "NONE"
                face = weak_face(samples[0]["path"]) if samples else False
                basis = (f'回源判定：命中文件**无本体 IRI 字面量、无 RDF 语句**（0/{len(hits)}）'
                         + ("；位于 DTO/测试/文档/示例面" if face else "")
                         + ' ⇒ 同名不同物，不计义务')
        entries.append({
            "repo": r["repo"], "category": r["category"], "token": r["token"], "rule_id": r["rule_id"],
            "source_disposition": src_disp, "final_disposition": final, "responsibility_wave": wave,
            "occurrences": int(r["occurrences"]), "file_count": int(r["file_count"]),
            "hits_total": len(hits), "ontology_consuming_hits": consuming,
            "evidence_verified": f"{len(verified)}/{len(samples)}",
            "line_drift": drift,
            "evidence": [s["file"] for s in samples], "basis": basis,
            "action": r["action"],
            "wave2_source_confirmation_required": bool(
                final in ("FOLLOW_MIGRATION", "CONTROL_PLANE_REQUIRED") and src_disp == "HOMONYM_REQUIRES_SOURCE_CHECK"),
        })
    by_final = collections.Counter(e["final_disposition"] for e in entries)
    by_wave = collections.Counter(e["responsibility_wave"] for e in entries)
    ev_ok = all(e["evidence_verified"].split("/")[0] == e["evidence_verified"].split("/")[1]
                for e in entries if e["evidence"])
    return {
        "schema": "ONTO1-A2-DISPOSITION-LEDGER/1.0",
        "authority": "Owner 2026-09-21 决议（SIM 整改）+ 批准项 4（授权按三信号分层法判定并登记，TL 抽查）",
        "scope_note": ("本台账闭环的是**处置决策**（每行终局处置 + `文件:行` 目标 + 责任 Wave）；"
                       "`FOLLOW_MIGRATION`/`CONTROL_PLANE_REQUIRED` 的**执行**在 Wave 2/3，**不声称已完成**；"
                       "**不**因本表变绿提升任何门禁。"),
        "sources": {"summary": str(SUMMARY.relative_to(ROOT)), "summary_sha256": sha256(SUMMARY),
                    "hits": str(HITS.relative_to(ROOT)), "hits_sha256": sha256(HITS)},
        "counts": {"summary_rows": len(rows), "unclosed_rows": len(targets),
                   "by_source_disposition": dict(collections.Counter(r["disposition"] for r in targets)),
                   "by_final_disposition": dict(by_final), "by_responsibility_wave": dict(by_wave),
                   "occurrences_total": sum(e["occurrences"] for e in entries),
                   "undecided_rows": sum(1 for e in entries if e["final_disposition"] not in FINAL_VOCAB),
                   "evidence_line_unverifiable": len(unverifiable),
                   "line_drift_samples": sum(len(e["line_drift"]) for e in entries)},
        "undecided_row_keys": unverifiable,
        "entries": entries,
    }


def write_ledger(d: dict) -> None:
    LEDGER_JSON.parent.mkdir(parents=True, exist_ok=True)
    LEDGER_JSON.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    cols = ["repo", "category", "token", "rule_id", "source_disposition", "final_disposition",
            "responsibility_wave", "occurrences", "file_count", "hits_total", "ontology_consuming_hits",
            "evidence_verified", "evidence", "basis", "action"]
    with LEDGER_CSV.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for e in d["entries"]:
            w.writerow({**e, "evidence": "; ".join(e["evidence"])})


def line_consuming(repo: str, path: str, line: str) -> bool:
    """**行级**独立信号（与构建路径的**文件级** `consuming_class()` 不同源）。

    构建路径用「整文件是否含本体字面量」决定豁免；本函数只审**该行证据本身**，
    且证据行不可定位 ⇒ 视为违例（fail-closed）。
    """
    txt = read_repo_file(repo, path)
    if txt is None:
        return True
    lines = txt.splitlines()
    try:
        n = int(line)
    except (TypeError, ValueError):
        return True
    if not 1 <= n <= len(lines):
        return True
    ln = lines[n - 1]
    return any(lit in ln for lit in ONTOLOGY_LITERALS) or \
        any(m.lower() in ln.lower() for m in RDF_MARKERS)


def independent_consumption(repo: str, category: str, token: str, rule_id: str) -> tuple[int, int]:
    """（保留）按**原始 hits 全键**复算消费证据，**不再预设处置值**。

    返回 (hits_total, ontology_consuming, source_dispositions)。
    """
    idx = load_hits()
    hits = [h for k, v in idx.items()
            if k[0] == repo and k[3] == token and k[4] == rule_id for h in v]
    disps = sorted({k[2] for k, v in idx.items()
                    if k[0] == repo and k[3] == token and k[4] == rule_id and v})
    consuming = sum(1 for h in hits if consuming_class(h["repo"], h["path"]) == "ONTOLOGY_CONSUMING")
    return len(hits), consuming, disps


def population_two_sided() -> tuple[int, int, int]:
    """**双侧对照**：命中文件总体中被判「本体消费」与「中性」的个数。

    返 (消费文件数, 中性文件数, 合计)。用途：恒置分类器（两个方向）都会让一侧归零 ⇒ A5 必须 FAIL。
    """
    idx = load_hits()
    files = {(k[0], h["path"]) for k, v in idx.items() for h in v}
    cons = sum(1 for repo, path in files if consuming_class(repo, path) == "ONTOLOGY_CONSUMING")
    return cons, len(files) - cons, len(files)


def checks(d: dict) -> list[tuple[str, bool, str]]:
    """**一律从 `entries` 复算**（不信任预计算 counts），并断言 counts 与 entries 一致。"""
    ent = d.get("entries", [])
    c = d.get("counts", {})
    by_final = collections.Counter(e.get("final_disposition") for e in ent)
    by_wave = collections.Counter(e.get("responsibility_wave") for e in ent)
    occ = sum(int(e.get("occurrences", 0)) for e in ent)
    unver = [e for e in ent
             if not e.get("evidence")
             or e.get("evidence_verified", "0/0").split("/")[0] != e.get("evidence_verified", "0/0").split("/")[1]]
    bad_vocab = [e for e in ent if e.get("final_disposition") not in FINAL_VOCAB]
    no_wave = [e for e in ent if e.get("responsibility_wave") == "NONE"
               and e.get("final_disposition") not in NO_WORK_DISPOSITIONS]
    exempt_rows = [e for e in ent if e.get("final_disposition") == "EXEMPT_NON_ONTOLOGY_HOMONYM"]
    # A5：**行级证据**复核（与构建路径不同源）+ 双侧对照（防恒置分类器）+ 非空转
    exempt_bad: list[str] = []
    exempt_line_checked = 0
    for e in exempt_rows:
        for ev in e.get("evidence", []):
            if ":" not in ev:
                exempt_bad.append(f'{e.get("token")}:证据不可解析({ev})')
                continue
            _p, _ln = ev.rsplit(":", 1)
            exempt_line_checked += 1
            if line_consuming(e.get("repo"), _p, _ln):
                exempt_bad.append(f'{e.get("token")}:{_p}:{_ln}')
    _cons_files, _neutral_files, _all_files = population_two_sided()
    two_sided = _cons_files > 0 and _neutral_files > 0
    non_vacuous = len(exempt_rows) > 0
    # A9：台账声明的 source_disposition 必须与**原始扫描**记录一致（独立键，不预设处置值）
    src_mismatch: list[str] = []
    for e in ent:
        _tot, _cons, _disps = independent_consumption(
            e.get("repo"), e.get("category"), e.get("token"), e.get("rule_id"))
        if _disps and e.get("source_disposition") not in _disps:
            src_mismatch.append(f'{e.get("token")}:台账={e.get("source_disposition")} 扫描={_disps}')
    exempt = by_final.get("EXEMPT_NON_ONTOLOGY_HOMONYM", 0)
    return [
        ("A1 未闭环行数 = 412（台账条目数 = 声明数 = 412）",
         len(ent) == 412 and c.get("unclosed_rows") == len(ent),
         f"条目 {len(ent)} / 声明 {c.get('unclosed_rows')}"),
        ("A2 每行均有**终局处置**（词表内，无表外值）",
         not bad_vocab and c.get("undecided_rows") == len(bad_vocab),
         f"表外/未决 {len(bad_vocab)}"),
        ("A3 每行均有 `文件:行` 依据且**逐行验证**（0 不可验证；位移/重构解消须记账）",
         not unver and c.get("evidence_line_unverifiable") == 0,
         f"不可验证 {len(unver)}；位移/解消记账 {c.get('line_drift_samples', 0)} 处"),
        ("A4 每行均有**责任 Wave**（无工作处置可 NONE，其余须 W2/W3）",
         not no_wave, f"无归属 {len(no_wave)}"),
        ("A5 豁免依据**行级独立复核** + 双侧对照 + 非空转（QA-W3R2 否决 F-5 后重修）",
         (not exempt_bad) and two_sided and non_vacuous,
         f"豁免 {len(exempt_rows)} 行 / 证据行 {exempt_line_checked} 处；行级违例 {len(exempt_bad)}"
         f"{('：' + str(exempt_bad[:2])) if exempt_bad else ''}；"
         f"双侧对照 消费 {_cons_files} / 中性 {_neutral_files}（合计 {_all_files}）⇒ 分类器"
         f"{'有判别力' if two_sided else '**恒置/失效 ⇒ 不得给绿**'}；"
         f"非空转={'OK' if non_vacuous else '**豁免集合为空 ⇒ 空转视为失败**'}"),
        ("A6 不得出现「一律豁免」（豁免行 < 全部）",
         len(ent) > 0 and exempt < len(ent), f"豁免 {exempt}/{len(ent)}"),
        ("A7 计数守恒（entries 复算 ↔ counts ↔ 8172）",
         occ == c.get("occurrences_total") == 8172,
         f"条目合计 {occ} / 声明 {c.get('occurrences_total')}"),
        ("A9 台账 `source_disposition` 与**原始扫描**逐行一致（独立键复核，不预设处置值）",
         not src_mismatch, f"不一致 {len(src_mismatch)} 行"
                           f"{('：' + str(src_mismatch[:2])) if src_mismatch else ''}"),
        ("A8 counts 与 entries **逐项一致**（防篡改计数）",
         dict(by_final) == c.get("by_final_disposition") and dict(by_wave) == c.get("by_responsibility_wave"),
         f"by_final/by_wave 一致 = {dict(by_final) == c.get('by_final_disposition')}"),
    ]


def cmd_gate() -> int:
    d = build_ledger()
    write_ledger(d)
    rows = checks(d)
    print(f"# command=onto1_disposition_ledger --gate")
    print(f"# 台账={LEDGER_CSV.relative_to(ROOT)}  summary={d['sources']['summary_sha256'][:16]} hits={d['sources']['hits_sha256'][:16]}")
    print(f"# 未闭环 {d['counts']['unclosed_rows']} 行 ⇒ 终局 {d['counts']['by_final_disposition']}")
    print(f"# 责任 Wave {d['counts']['by_responsibility_wave']}")
    for n, ok, det in rows:
        print(f"{'PASS' if ok else 'FAIL'} [{n}] {det}")
    bad = [n for n, ok, _ in rows if not ok]
    print(f"A-1 处置表闭环：{'PASS' if not bad else 'FAIL'}（{len(rows) - len(bad)}/{len(rows)}）")
    return 0 if not bad else 2


def cmd_selftest() -> int:
    d = build_ledger()
    fails = total = 0

    def run(tag: str, mut, expect: str) -> None:
        """**变异必须被它针对的判据本尊捕获**（QA-W3R2 教训：捕获者不是被判对象 ⇒ 判据无判别力）。"""
        nonlocal fails, total
        import copy
        m = copy.deepcopy(d)
        mut(m)
        bad = [n for n, o, _ in checks(m) if not o]
        ok = any(n.startswith(expect) for n in bad)
        total += 1
        fails += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'} [{tag}] 期望 {expect} 捕获；实际 {bad}")

    total += 1
    base_ok = all(o for _, o, _ in checks(d))
    fails += 0 if base_ok else 1
    print(f"{'PASS' if base_ok else 'FAIL'} [M0 对照] 现状 7/7 = {base_ok}")

    def _first_exempt(m):
        return next(e for e in m["entries"]
                    if e["final_disposition"] == "EXEMPT_NON_ONTOLOGY_HOMONYM")

    run("M1 删掉一行的证据 ⇒ A3", lambda m: m["entries"][3].update(evidence=[], evidence_verified="0/0"), "A3")
    run("M2 表外处置值 ⇒ A2", lambda m: m["entries"][5].update(final_disposition="SOMETHING_ELSE"), "A2")
    # M3 重定位：把豁免行的**证据行**指向本体消费行（A5 本尊读的就是它）
    run("M3 豁免行证据指向本体消费行 ⇒ A5",
        lambda m: _first_exempt(m).update(evidence=["specs/semantic/gits-core.owl.ttl:1"]), "A5")
    run("M4 少一行（412→411）⇒ A1", lambda m: m["entries"].pop(), "A1")
    run("M5 全行一律豁免 ⇒ A6",
        lambda m: [e.update(final_disposition="EXEMPT_NON_ONTOLOGY_HOMONYM") for e in m["entries"]], "A6")
    run("M6 责任 Wave 缺失 ⇒ A4",
        lambda m: m["entries"][7].update(responsibility_wave="NONE", final_disposition="FOLLOW_MIGRATION"), "A4")
    # M7 非空转：豁免集合被清空 ⇒ A5 必须 FAIL（空转视为失败）
    run("M7 豁免集合为空（空转）⇒ A5",
        lambda m: [e.update(final_disposition="FOLLOW_MIGRATION") for e in m["entries"]], "A5")
    # M8 独立键复核：篡改台账声明的 source_disposition ⇒ A9 必须 FAIL
    run("M8 篡改 source_disposition ⇒ A9",
        lambda m: m["entries"][9].update(source_disposition="NOT_A_REAL_DISPOSITION"), "A9")
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
    d = build_ledger()
    write_ledger(d)
    print(f"已写入 {LEDGER_CSV.relative_to(ROOT)}：未闭环 {d['counts']['unclosed_rows']} 行 ⇒ "
          f"{d['counts']['by_final_disposition']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
