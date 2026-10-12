#!/usr/bin/env python3
"""判据强度自审｜AST 级扫描全部 `onto1_*.py` 仪器，标出「判据恒真 / 同义反复 / 与声明脱钩 / 变异体无效 / **未审**」

**修订史（QA-W3R2 否决 ⑨ 后重修，2026-09-21）**
QA 第二轮否决原版的两个致命缺陷：
  1. **覆盖率不 fail-closed**：原版对 18/45 仪器**抽不到任何判据**却报「0 条候选」——
     把「没审到」当成「没问题」。（成因：只认 3 元组 ⇒ 2 元组 `(名称, ok)` 被丢；dict 式判定；
     `failures.append("...")` 字符串式；条件被预计算成变量后不在审查域。）
  2. **白名单可自我满足**：按**名称**匹配 + 含泛化键（`V1/V2/V3`）⇒ 清空白名单后仍有 7 条候选，
     而「0 条未复核」完全由白名单产生（白名单作者 = 被审代码作者 = 出结论者）。

修订后：
  · 抽取覆盖 **2/3 元组 · dict 式 · 字符串式 · 预计算变量（回溯源表达式）**；
  · **未抽到判据的仪器一律报 `NOT_AUDITED`（high）**，不得静默通过；
  · 白名单**按（仪器, 判据名, 条件表达式哈希）三元匹配**，泛化短名必须带哈希；
    哈希与冻结记录不符 ⇒ `REVIEW_STALE`（需重新复核）；
  · 输出 `not_audited` 清单与覆盖率。

用法：`--scan`（默认）/ `--freeze`（复核后冻结哈希）/ `--json`
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path("/home/szf/dev/gits-cbanking")
SCRIPTS = ROOT / "scripts"
OUT = ROOT / "loops/ONTO1-ontology-split/evidence/prep/check-strength-audit.json"
FROZEN = ROOT / "loops/ONTO1-ontology-split/evidence/prep/check-strength-review-hashes.json"

PREDICATE = (ast.Compare, ast.BoolOp, ast.UnaryOp, ast.Call, ast.Name, ast.Subscript,
             ast.ListComp, ast.GeneratorExp, ast.IfExp, ast.Dict, ast.Tuple, ast.Attribute)
SEVERITY = {"TAUTOLOGY_CONST": "high", "TAUTOLOGY_CMP": "high", "EMPTY_ALL": "high",
            "NOT_AUDITED": "high", "DECLARED_ONLY": "medium", "REVIEW_STALE": "medium",
            "MUTANT_SCOPE": "info", "BRANCH_CONCLUSION": "info", "REVIEWED_OK": "info",
            # B-i1/B2（QA-W3R4）：两类**主流判定形态**，原实现结构性看不见（覆盖率 0/205）
            "STRING_JUDGMENT": "info", "STATE_WRITE": "info"}
GENERIC_NAME_RE = re.compile(r"^[A-Z]{1,3}\d{0,2}$")

# **已复核白名单**：理由留档；哈希由 `--freeze` 冻结 ⇒ 条件表达式一旦变更即 `REVIEW_STALE`
REVIEWED: dict[str, dict[str, str]] = {
    "onto1_breakpoint_option_rehearsal.py": {
        "C-3 出口 A **相邻名保持**（逐断点核对通过）":
            "读 `all_adjacent_preserved`，该值由 A-12 沙箱内**逐文件前后计数比对**派生（非声明）；另有 K7/K8 真实路径反例。"},
    "onto1_c2_fix_verify.py": {
        "V1": "`try` 内解析成功才置 True；解析异常即 False 并提前返回 ⇒ **fail-closed**，非恒真。",
        "V2": "if/else 分支结论：不满足即走 else 追加 False（分支豁免）。",
        "V3": "if/else 分支结论：`bad_types` 非空即 False（分支豁免）。"},
    "onto1_kert_registration_request.py": {
        "Z5 **派生**判定未发出且未写入 KERT（KERT 近 1 日写入 = 0 且无发出标记）":
            "已由 `derive_write_state()` **实测派生**（今日写入计数 + 发出标记存在性）；`is False` 只是对派生布尔取值。"},
    "onto1_l1_prep.py": {
        "L2 命名空间为 provisional":
            "交叉比对**两个独立制品**的 status 字段；**部分成立**（QA-W3R2 指出「D3 台账钉定」无运行期依据）⇒ 保留但降级为观察项。"},
    "onto1_l3_load_fixture.py": {
        "L1 三制品均可解析（**由实际三元组数派生**）":
            "读 `parse.ok`，该值由 `load_all()` 实际解析并计数派生（实测 T-Box 255 / A-Box 39 / SIM 290）。"},
    "onto1_scenario_readiness.py": {
        "S4 预演**未触碰隔离别名**（一处未改）":
            "由沙箱预演时**逐文件实际计数**得出（另配 U7 真实路径反例）。"},
    "onto1_sim_rehearsal.py": {
        "M5 演练后 TTL **仍可解析**（全绿）":
            "由 `rehearse_one()` 对每个演练副本**实际 rdflib 解析**得出（实测 0 失败）。",
        "M6 **退役项一处未换**（未走改名路径）":
            "由演练后文件内容**实际比对**退役名是否保留得出（实测 0 违例）。"},
}


def expr_text(src_lines: list[str], node: ast.AST) -> str:
    if hasattr(node, "lineno"):
        return src_lines[node.lineno - 1].strip()
    return ast.dump(node)[:120]


def expr_sha12(node: ast.AST, src_lines: list[str]) -> str:
    body = ast.get_source_segment("\n".join(src_lines), node) or ast.dump(node)
    return hashlib.sha256(re.sub(r"\s+", " ", body).strip().encode()).hexdigest()[:12]


def classify(cond: ast.AST) -> list[str]:
    flags: list[str] = []
    if isinstance(cond, ast.Constant) and isinstance(cond.value, bool):
        return ["TAUTOLOGY_CONST"]
    for n in ast.walk(cond):
        if isinstance(n, ast.Compare) and len(n.ops) == 1:
            op, right = n.ops[0], n.comparators[0]
            if isinstance(right, ast.Constant) and right.value == 0 and isinstance(op, (ast.GtE, ast.LtE)):
                flags.append("TAUTOLOGY_CMP")
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in ("all", "any"):
            for sub in ast.walk(n):
                if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute) and \
                        sub.func.attr == "get" and len(sub.args) >= 2 and \
                        isinstance(sub.args[1], (ast.List, ast.Dict)):
                    flags.append("EMPTY_ALL")
                    break
        if isinstance(n, ast.Compare) and isinstance(n.ops[0], (ast.Is, ast.Eq)) and \
                any(isinstance(c, ast.Constant) and isinstance(c.value, bool) for c in n.comparators):
            flags.append("DECLARED_ONLY")
            break
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "bool" and \
                any(isinstance(s, ast.Call) and isinstance(s.func, ast.Attribute) and s.func.attr == "get"
                    for s in ast.walk(n)):
            flags.append("DECLARED_ONLY")
            break
    return sorted(set(flags))


def resolve(node: ast.AST, assigned: dict[str, ast.AST]) -> ast.AST:
    """条件若被预计算成变量（如 `ok7 = <expr>` 后 `(名称, ok7, ...)`）⇒ 回溯源表达式。"""
    seen = 0
    while isinstance(node, ast.Name) and node.id in assigned and seen < 6:
        node, seen = assigned[node.id], seen + 1
    return node


def extract_in_func(fn: ast.AST, src_lines: list[str]) -> list[dict]:
    out: list[dict] = []
    assigned: dict[str, ast.AST] = {}
    for n in ast.walk(fn):
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            assigned[n.targets[0].id] = n.value
    # 收集「结构化分支结论」位置：except 处理器内、if 的 else 分支内
    branch_linenos: set[int] = set()
    for n in ast.walk(fn):
        if isinstance(n, ast.ExceptHandler) and n.body:
            for b in n.body:
                branch_linenos.update(range(b.lineno, (getattr(b, "end_lineno", b.lineno) or b.lineno) + 1))
        if isinstance(n, ast.If):
            # QA-W3R3：只豁免 else 分支会漏 If.body ⇒ 失败分支里的具名 False 被误报 TAUTOLOGY_CONST
            for b in list(n.body) + list(n.orelse):
                branch_linenos.update(range(b.lineno, (getattr(b, "end_lineno", b.lineno) or b.lineno) + 1))
    cands: list[tuple[str, ast.AST, int]] = []
    for n in ast.walk(fn):
        if isinstance(n, (ast.List, ast.Tuple)):
            for el in n.elts:
                if isinstance(el, ast.Tuple) and len(el.elts) >= 2 and \
                        isinstance(el.elts[0], ast.Constant) and isinstance(el.elts[0].value, str):
                    cands.append((el.elts[0].value, el.elts[1], el.lineno))
                if isinstance(el, ast.Dict):
                    kv = {k.value: v for k, v in zip(el.keys, el.values)
                          if isinstance(k, ast.Constant) and isinstance(k.value, str)}
                    nm = kv.get("name") or kv.get("check") or kv.get("id")
                    cd = kv.get("ok") or kv.get("condition") or kv.get("passed")
                    if isinstance(nm, ast.Constant) and isinstance(nm.value, str) and cd is not None:
                        cands.append((nm.value, cd, el.lineno))
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "append":
            for a in n.args:
                if isinstance(a, ast.Tuple) and len(a.elts) >= 2 and \
                        isinstance(a.elts[0], ast.Constant) and isinstance(a.elts[0].value, str):
                    cands.append((a.elts[0].value, a.elts[1], a.lineno))
                if isinstance(a, ast.Dict):
                    kv = {k.value: v for k, v in zip(a.keys, a.values)
                          if isinstance(k, ast.Constant) and isinstance(k.value, str)}
                    nm = kv.get("name") or kv.get("check") or kv.get("id")
                    cd = kv.get("ok") or kv.get("condition") or kv.get("passed")
                    if isinstance(nm, ast.Constant) and isinstance(nm.value, str) and cd is not None:
                        cands.append((nm.value, cd, a.lineno))
    # B-i1/B2 加固：① 裸字符串 append（120 个门禁拒绝点的**主流形态**）；
    #               ② 下标赋值 dict（31 个状态写入点）。二者原**不在审查域**（覆盖率 0/205）。
    for n in ast.walk(fn):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and \
                n.func.attr == "append" and len(n.args) == 1 and \
                isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str):
            out.append({"name": "STRING_JUDGMENT::" + n.args[0].value[:26],
                        "flags": ["STRING_JUDGMENT"], "line": n.lineno,
                        "expr": expr_text(src_lines, n), "sha12": expr_sha12(n, src_lines),
                        "literal_value": None, "literal_bool": False, "resolved": False})
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and \
                isinstance(n.targets[0], ast.Subscript):
            out.append({"name": "STATE_WRITE::" + expr_text(src_lines, n.targets[0])[:22],
                        "flags": ["STATE_WRITE"], "line": n.lineno,
                        "expr": expr_text(src_lines, n), "sha12": expr_sha12(n, src_lines),
                        "literal_value": None, "literal_bool": False, "resolved": False})

    for name, cond, ln in cands:
        raw = cond
        cond = resolve(cond, assigned)
        # 字符串式判定：`failures.append("...")` 属**记录**而非判据，只登记不计候选
        if isinstance(cond, ast.Constant) and isinstance(cond.value, str):
            out.append({"name": name, "flags": ["STRING_NOTE"], "line": ln,
                        "expr": expr_text(src_lines, raw), "sha12": expr_sha12(raw, src_lines),
                        "literal_value": None, "literal_bool": False, "resolved": False})
            continue
        second_ok = isinstance(cond, PREDICATE) or (isinstance(cond, ast.Constant)
                                                    and isinstance(cond.value, bool))
        if not second_ok:
            continue
        _flags = classify(cond)
        if ln in branch_linenos and isinstance(cond, ast.Constant) and isinstance(cond.value, bool):
            _flags = [f for f in _flags if f != "TAUTOLOGY_CONST"] + ["BRANCH_CONCLUSION"]
        # 数据元组误计（QA-W3R3）：第 2 项非谓词形态且非布尔常量 ⇒ 不是判据，不登记为候选
        if not (isinstance(cond, PREDICATE) or (isinstance(cond, ast.Constant)
                                               and isinstance(cond.value, bool))):
            continue
        out.append({"name": name, "flags": _flags, "line": ln,
                    "expr": expr_text(src_lines, cond), "sha12": expr_sha12(cond, src_lines),
                    "literal_value": (cond.value if isinstance(cond, ast.Constant)
                                      and isinstance(cond.value, bool) else None),
                    "literal_bool": (isinstance(cond, ast.Constant) and isinstance(cond.value, bool)),
                    "resolved": cond is not raw})
    return out


def extract_checks_in_func(fn: ast.AST, src_lines: list[str]) -> list[dict]:
    return extract_in_func(fn, src_lines)


def extract_checks(tree: ast.Module, src_lines: list[str]) -> list[dict]:
    out: list[dict] = []
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        got = extract_in_func(fn, src_lines)
        const_names = {c["name"] for c in got if c["literal_bool"]}
        both = {n for n in const_names
                if {c["literal_value"] for c in got if c["name"] == n} == {True, False}}
        for c in got:
            if c["literal_bool"] and c["name"] in both:
                c["flags"] = [f for f in c["flags"] if f != "TAUTOLOGY_CONST"]
                c["flags"].append("BRANCH_CONCLUSION")
            c["flags"] = sorted(set(c["flags"]))
            c["function"] = fn.name
        out += got
    return out


def extract_mutant_keys(tree: ast.Module) -> set[str]:
    keys: set[str] = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Subscript) and isinstance(n.value, ast.Name) and n.value.id in ("m", "d", "mut"):
            if isinstance(n.slice, ast.Constant) and isinstance(n.slice.value, str):
                keys.add(n.slice.value)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "update":
            for kw in n.keywords:
                keys.add(kw.arg or "")
    return {k for k in keys if k}


def function_sources(tree: ast.Module, src_lines: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out[n.name] = ast.get_source_segment("\n".join(src_lines), n) or ""
    return out


def has_gate_flag(src: str) -> bool:
    return "--gate" in src


def scan() -> dict:
    frozen = json.loads(FROZEN.read_text(encoding="utf-8")) if FROZEN.is_file() else {"entries": {}}
    rows: list[dict] = []
    for p in sorted(SCRIPTS.glob("onto1_*.py")):
        try:
            src = p.read_text(encoding="utf-8")
            tree = ast.parse(src)
        except SyntaxError as exc:
            rows.append({"instrument": p.name, "error": f"语法错误 {exc.lineno}", "checks": [],
                         "checks_total": 0, "flagged": [], "not_audited": True})
            continue
        lines = src.splitlines()
        checks = extract_checks(tree, lines)
        mutant_keys = extract_mutant_keys(tree)
        fsrc = function_sources(tree, lines)
        check_text = " ".join(fsrc.get(n, "") for n in ("checks", "run_checks", "scan", "build", "inspect")) \
                     or " ".join(fsrc.values())
        for c in checks:
            flags = list(c["flags"])
            if mutant_keys and not any(k in check_text for k in mutant_keys if len(k) > 3):
                flags.append("MUTANT_SCOPE")
            if c["name"] in REVIEWED.get(p.name, {}):
                fk = frozen.get("entries", {}).get(p.name, {}).get(c["name"])
                if fk and c["sha12"] not in (fk if isinstance(fk, list) else [fk]):
                    flags.append("REVIEW_STALE")
                else:
                    flags = [f for f in flags
                             if f not in ("TAUTOLOGY_CONST", "DECLARED_ONLY", "EMPTY_ALL")]
                    flags.append("REVIEWED_OK")
            c["flags"] = sorted(set(flags))
            c["review_note"] = REVIEWED.get(p.name, {}).get(c["name"])
            c["severity"] = max((SEVERITY.get(f, "info") for f in c["flags"]),
                                key=lambda s: ("info", "medium", "high").index(s), default="info")
        # **诚实口径**：B-i1/B2 新增的两类形态是"**已看见但未判定**"——
        # 它们能被抽取与计数，但"能否 FAIL"仍需违规点分析（QA 第三/四轮的方法）。
        # 故**不计入** `auditable`（否则 NOT_AUDITED 会被自己的加固软化掉，属自欺）。
        _UNJUDGED = {"STRING_NOTE", "STRING_JUDGMENT", "STATE_WRITE"}
        auditable = [c for c in checks if not (set(c["flags"]) & _UNJUDGED)]
        sighted_unjudged = [c for c in checks if set(c["flags"]) & _UNJUDGED]
        not_audited = len(auditable) == 0 and has_gate_flag(src)
        rows.append({"instrument": p.name, "checks": checks, "checks_total": len(checks),
                     "auditable": len(auditable), "sighted_unjudged": len(sighted_unjudged),
                     "not_audited": not_audited,
                     "has_gate": has_gate_flag(src),
                     "flagged": [c for c in checks if c["severity"] in ("high", "medium")],
                     "mutant_keys": sorted(mutant_keys)[:24]})
        if not_audited:
            rows[-1]["flagged"].append({"name": "（整份仪器未抽到任何判据）", "flags": ["NOT_AUDITED"],
                                        "line": 0, "expr": "—", "severity": "high",
                                        "review_note": "覆盖率 fail-closed：未抽到 ⇒ 不得视为通过"})
    flagged_all = [{"instrument": r["instrument"], "check": c.get("name"), "flags": c.get("flags"),
                    "line": c.get("line"), "expr": c.get("expr"), "severity": c.get("severity")}
                   for r in rows for c in r.get("flagged", [])]
    by_flag: dict[str, int] = {}
    for f in flagged_all:
        for fl in f["flags"]:
            by_flag[fl] = by_flag.get(fl, 0) + 1
    not_audited = [r["instrument"] for r in rows if r.get("not_audited")]
    sj = sum(1 for r in rows for c in r.get("checks", []) if "STRING_JUDGMENT" in c.get("flags", []))
    sw = sum(1 for r in rows for c in r.get("checks", []) if "STATE_WRITE" in c.get("flags", []))
    return {"schema": "ONTO1-CHECK-STRENGTH-AUDIT/2.0",
            "string_judgments_total": sj, "state_writes_total": sw,
            "note": "**候选清单，非结论**：每条须人工复核；`NOT_AUDITED` = 抽不到判据（**fail-closed，不得视为通过**）。",
            "instruments": rows, "instruments_total": len(rows),
            "auditable_total": sum(r.get("auditable", 0) for r in rows),
            "not_audited": not_audited, "not_audited_total": len(not_audited),
            "flagged_total": len(flagged_all), "by_flag": by_flag, "flagged": flagged_all}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--freeze", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true",
                    help="批次纪律入口：存在 high 候选或 NOT_AUDITED ⇒ exit 2（默认 0 是**设计**：本器不是门禁，见 D-20）")
    ns = ap.parse_args()
    if ns.freeze:
        d = scan()
        entries: dict[str, dict[str, str]] = {}
        for r in d["instruments"]:
            for c in r.get("checks", []):
                if c.get("name") in REVIEWED.get(r["instrument"], {}):
                    entries.setdefault(r["instrument"], {}).setdefault(c["name"], [])
                    if c["sha12"] not in entries[r["instrument"]][c["name"]]:
                        entries[r["instrument"]][c["name"]].append(c["sha12"])
        FROZEN.write_text(json.dumps({"schema": "ONTO1-CHECK-STRENGTH-REVIEW/1.0",
                                      "frozen_at": "2026-09-21", "entries": entries},
                                     ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"已冻结复核哈希：{sum(len(v) for v in entries.values())} 条 / {len(entries)} 仪器 → {FROZEN.name}")
        return 0
    d = scan()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if ns.json:
        print(json.dumps({"by_flag": d["by_flag"], "not_audited": d["not_audited"]}, ensure_ascii=False))
        return 0
    print(f"# 判据强度自审 v2：仪器 {d['instruments_total']} 个；可审判据 {d['auditable_total']} 条；"
          f"候选 {d['flagged_total']} 条；**未审仪器 {d['not_audited_total']} 个**")
    print(f"# 分类计数：{d['by_flag']}")
    print(f"# B 块两类形态（B-i1/B2 加固后）：裸字符串 append {d.get('string_judgments_total')} 点 · "
          f"下标赋值 dict {d.get('state_writes_total')} 点（此前覆盖率 0）")
    if ns.strict:
        highs = [f for f in d['flagged'] if f['severity'] == 'high']
        bad = bool(highs) or d['not_audited_total'] > 0
        print(f"# --strict：high 候选 {len(highs)} / 未审仪器 {d['not_audited_total']} ⇒ "
              f"{'FAIL' if bad else 'PASS'}")
        return 2 if bad else 0
    for f in d["flagged"]:
        print(f"  [{','.join(f['flags'])}] {f['instrument']}:{f['line']} :: {str(f['check'])[:44]}")
        print(f"      条件：{str(f['expr'])[:110]}")
    if d["not_audited"]:
        print("# 未审仪器（fail-closed，不得视为通过）：")
        for x in d["not_audited"]:
            print(f"  ! {x}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
