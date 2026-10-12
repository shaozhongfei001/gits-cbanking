#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ONTO1-ontology-split / WI-A3（D1）日常核验：参照对齐口径守门。

用途
    在 GB/T 48000.3-2026 正式文本到手前，逐日核验两项红线：
      ① 不得出现标准符合性表述（含历史件未登记的新增命中）；
      ② 不得出现 CONFORMANCE 文件名（除显式登记的范围豁免）。
    并对条款适用性矩阵实施 fail-closed 守门：文本未到手时，矩阵必须为空表。

设计（沿用本 Loop 防假绿三件套）
    单一真值函数  truth(env)  —— --gate 与 --selftest 共用同一入口，禁止两套逻辑
    fail-closed   —— 状态文件缺失按「文本未到手」处理；注册表项缺失或哈希漂移一律 FAIL
    变异复验      —— --selftest 共 **16 项**（对照 4：M0 基线 / M6 文本到手 / M10 规则陈述放行并断言计数 /
                     M15 词级否定标题语境放行；变异 12：M1~M5、M7~M9、M11~M14），要求 mutate→FAIL / restore→PASS
    元陈述放行    —— 「规则陈述行」放行（依据 D-3，**N-1 收紧后为三条件同时成立**：
                     含元陈述关键词 ∧ 不含声称构造 ∧ 含判定语义，见 `is_rule_statement()`）；
                     放行**逐原因计数**输出（`allowed[rule_statement]=N`）；放行是**行级**的，
                     不随文件 / 邻近行扩散（M11 测相邻行、M12 测 `loops/**` 目录不是白名单，
                     M13 测"真实声称顺带含元陈述关键词"仍判 FAIL——QA 第二轮 N-1 / X3）
    空转防护      —— 扫描文件数、候选行数、放行行数任一下限不达即 FAIL（防规则失效后恒绿）

精度上限（如实声明，不得据此宣称覆盖完整）
    本核验是「词法级 + 结构窗口」，不是语义判定：放行依赖同行 / 表格行 / 最近标题 / 父键中的否定标记，
    以及行内的元陈述关键词（D-3）。
    新增文档若把声称写在否定条款旁、或把元陈述关键词与声称写进**同一行**，仍可能漏检，
    命中清单须人工复核；放行计数（`allowed[rule_statement]`）即为该漏检面的**可审计入口**：
    该计数异常增长时须回看是否放行过宽。
    条款级判定不在本脚本职责内——待正式文本到手后按 T2~T4 单独门禁执行。

判定层次
    F 文件名层  —— 文件名含 conformance / 符合性：本体相关⇒直接 FAIL；其余须登记为范围豁免，未登记⇒FAIL
    A 制品名层  —— 出现被否决的命名方案（ONTOLOGY-CONFORMANCE / CONFORMANCE-REPORT 等）⇒ 须放行或登记
    C 表述层    —— 标准范围内（含 GB/T、国标）的符合性表述 ⇒ 须放行或登记
    S 矩阵层    —— 骨架与机读空表：文本未到手时数据行必须为 0（fail-closed）

不做什么
    不修改任何被扫描文件（历史件只登记、不改写）；不判定条款内容；不代替独立 QA 与 Owner 签署。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------- 扫描参数

SKIP_DIRS = {
    ".git", ".hg", ".svn", ".ua", ".venv", "venv", "env", "node_modules", "target",
    "build", "dist", "coverage", "htmlcov", "__pycache__", ".mypy_cache",
    ".pytest_cache", ".ruff_cache", ".gradle", ".idea", ".vscode", "test-results",
    "playwright-report", ".next", ".cache", "site-packages", "bin", "obj",
}

TEXT_EXTS = {
    ".md", ".markdown", ".mdc", ".json", ".jsonl", ".yaml", ".yml", ".py", ".java",
    ".kt", ".ts", ".tsx", ".vue", ".js", ".mjs", ".cjs", ".xml", ".sql", ".txt",
    ".sh", ".toml", ".cfg", ".ini", ".properties", ".csv", ".html",
}

MAX_BYTES = 2_000_000
OWN_ARTIFACT_PREFIX = "wi_a3_"  # 本核验自身日志：不参与扫描，避免自证污染

# ---------------------------------------------------------------- 判定词表

GB_SCOPE_RE = re.compile(r"GB/T\s*\d|GB\s*48000|国标|国家标准")
# 表述层命中：只针对「标准符合性」语义，不含裸 CONFORMANCE 词（命令名/技术词不属本红线）
WORDING_RE = re.compile(
    r"符合性|符合\s*GB/T|符合\s*国家标准|与\s*GB/T\s*48000\.3\s*一致",
    re.IGNORECASE,
)
# 制品名层命中：被否决的命名方案（无论文件是否国标范围），防止回流
ARTIFACT_RE = re.compile(
    r"ONTOLOGY[-_]CONFORMANCE|CONFORMANCE[-_](REPORT|MATRIX|DECLARATION|STATEMENT)",
    re.IGNORECASE,
)

NEG_MARKERS = (
    "禁", "禁止", "禁用", "严禁", "不得", "不准", "不允许", "不予",
    "不声称", "不构成", "未证明", "不作", "不是", "不包含", "不涉及", "不发布",
    "不引入", "不含", "不产生", "不等于", "并非",
    "无任何", "无国标", "无符合性", "零国标", "未到手",
    "避免", "排除", "移出", "驳", "拒绝", "红线",
    "历史件", "已作废", "作废", "superseded", "OUT_OF_SCOPE",
    "否决", "forbidden", "do_not_start", "prohibited", "not_allowed",
    "非国标", "无关",
)

# 元陈述关键词（D-3）：描述**规则本身**的行（禁令、变异用例、词表）不是标准符合性**声称**。
# 依据 `loops/ONTO1-ontology-split/memory/TL-DECISIONS-W-1.md` **D-3**：
#   ① 归属＝守卫精度问题 + 措辞问题各一半；
#   ② 长期修法＝守卫应放行「规则陈述行」——否则起草人只能改措辞规避；
#   ③ 红线：**措辞可改，规则不可删**（为了过门禁而删除规则陈述会让红线失去载体）。
# 因此本放行是「精度修正」而非「放宽」：
#   · 只作用于**本行**（不含下列关键词的真实符合性声称照旧 FAIL，--selftest M11 专测）；
#   · 放行必须留计数（print_report 打印 `allowed[rule_statement]=N`，供审计）；
#   · **不**采用「把 `loops/**` 整体加白名单」的做法——那会把该目录下的真实声称一并放过。
META_STATEMENT_MARKERS = (
    "注入",        # 变异/夹具用例的动词（"注入…样本"）
    "变异",        # 变异用例描述
    "禁用词表",    # 规则文书对词表本身的引用
    "词表",        # 同上（较短形态）
    "判 FAIL",     # 期望判定（"⇒ 必须被判 FAIL"）
    "不得放行",    # 判定纪律陈述
)

# ---------------------------------------------------------------- N-1 收紧（QA 第二轮 §9.9 N-1 / §9.7 X3）
#
# 问题（QA 实证 X3）：`rule_statement` 原判定是**纯子串**匹配元陈述关键词 ⇒ 一句**真实声称**
# 只要顺带提到"词表/变异/注入"等**主题词**就被当作"规则陈述行"放行 ⇒ 新引入一条漏检通道（BLOCKER）。
# 例：`本设计符合 GB/T 48000.3-2026 的全部要求，术语按词表统一。`（含"词表"）原会被放行。
#
# 收紧后的放行条件 = **三条件同时成立**（KEYWORD ∧ 非声称 ∧ 判定语义）：
#   ① 含 META_STATEMENT_MARKERS 之一；
#   ② **不含声称构造**（`CLAIM_CONSTRUCTION_RE`）—— 声称构造优先，直接判违规；
#   ③ 含**判定语义**（`JUDGEMENT_TOKENS`）—— 规则陈述必须是在讲"判什么/怎么判"，
#      而不是顺带提到某个主题词。
# D-3 原案仍可写：`注入被禁止的表述类变异样本 ⇒ 必须被判 FAIL（不得放行）；守卫词表见 …`
# （该行既有否定标记走 `same_line_negation`；即使去掉否定标记，仍满足 ①②③ ⇒ 放行）。
# 证据：`--selftest` M10（规则陈述行 ⇒ 放行且计数 ≥1）、**M13**（真实声称 + 单个元陈述关键词 ⇒ 必 FAIL）。
CLAIM_CONSTRUCTION_RE = re.compile(
    r"符合\s*(?:GB/T|国家标准|国标|要求)"        # 「符合 GB/T …」「符合要求」
    r"|满足\s*.{0,8}要求"                        # 「满足…要求」
    r"|达到\s*.{0,8}要求"                        # 「达到…要求」
    r"|(?:已通过|已合规)"                        # 「已通过/已合规」
    r"|与\s*GB/T\s*48000\.3\s*一致",             # 唯一的逐字可声明口径形态
    re.IGNORECASE,
)
JUDGEMENT_TOKENS = (
    "FAIL", "判", "放行", "守卫", "期望", "必须", "用例", "样本", "门禁", "红线",
)

# ---------------------------------------------------------------- R-1 修复（QA 第二轮 §9.7 X4 / §9.9 N-5）
#
# 现象（QA 实证 X4）：`NEG_MARKERS` 含**单字** `禁`，而标题锚点判定是**子串**匹配
# ⇒ 标题写作"**门禁**…"（"禁"字的常见复合词）会放行其下**所有**命中行，包括真实符合性声称。
#
# 处置（**最小面**）：只在**标题锚点**两处（`_nearest_heading_is_neg` / `_ancestor_negation`
# 的标题分支）改用**词级**标记（剔除单字 `禁`、`驳`）；同行/表格行/父键放行**不变**
# （那些是自然语言句子或键名，单字标记的后果由 N-1 的收紧与表格语境承担）。
#
# 实测影响面（/tmp 对照实验，脚本副本，未动仓内字节）：真实仓扫描 `files=4606 candidates=187
# allowed=100` 与改前**逐项一致**、违规集合**完全相同（零波及）**；X4 由"放行"转为
# `CONTENT_WORDING_UNALLOWED`，X5 对照不变。证据：`--selftest` M14（标题含"禁"复合词
# ⇒ 其下真实声称必须 FAIL）与 M15（标题为**词级**否定"禁止事项"⇒ 该语境仍放行）。
HEADING_NEG_MARKERS = tuple(marker for marker in NEG_MARKERS if marker not in ("禁", "驳"))

CONFORMANCE_NAME_RE = re.compile(r"conformance", re.IGNORECASE)
ONTOLOGY_NAME_RE = re.compile(r"ontology|ontology[-_]conformance|guobiao|^\s*gb[-_]", re.IGNORECASE)
CN_COMPLIANCE_NAME_RE = re.compile(r"符合性")

HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s")
CLAUSE_CELL_RE = re.compile(r"^\s*\|\s*\d+(\.\d+)+\s*\|")

# 设计 §8 给定的唯一可声明口径（逐字，禁改写）
VERBATIM_SCOPE = (
    "本项目建立企业本体建模内部规范，并参照 GB/T 48000.3-2026 中经适用性评估确认的通用建模要求。"
)

REQUIRED_COLUMNS = ("条款号", "适用性", "不适用理由", "项目加严", "证据", "结论")
MATRIX_HEADER = "条款号,适用性,不适用理由,项目加严,证据,结论"


# ---------------------------------------------------------------- 数据结构


@dataclass
class Env:
    roots: list = field(default_factory=list)
    registry: Path = None
    skeleton: Path = None
    matrix_csv: Path = None
    status_json: Path = None
    min_files: int = 100
    min_candidates: int = 5
    min_allowed: int = 1
    exempt: set = field(default_factory=set)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def redact(text: str) -> str:
    """命中内容不回显，避免核验自身把违规字样写进证据文件。"""
    return "sha256:%s|len:%d" % (hashlib.sha256(text.encode("utf-8")).hexdigest()[:12], len(text))


# ---------------- O-12 整改（2026-09-21，Owner 决议 `APPROVED_WITH_REQUIRED_CHANGES`）----------------
# ① **单字误报修复**：改用**行首否定动词**式识别（`未/不/无/非` + 动词/名词），
#    替代"把常用单字塞进否定标记表"的做法（后者既漏判「未签发…」，又易与「门禁」类复合词混淆）。
#    ⚠ 声称构造优先：含 `CLAIM_CONSTRUCTION_RE` 的行**不得**据此放行（见 `classify_line`）。
LINE_START_NEG_RE = re.compile(
    r"^\s*(?:[-*>]\s*)?(?:\*\*|__)?\s*(?:未|不|无|非)(?:\*\*|__)?[\u4e00-\u9fff]{1,6}")


def redact_excerpt(text: str, limit: int = 120) -> str:
    """② **可读审计证据**：保留脱敏但**可人工阅读**的摘要。

    触发词以 `▮` 掩码（长度保留）⇒ 证据既说明"哪句话被拦"，又**不会让报告自身成为违规源**。
    与 `sha256|len` 的关系：后者只能证明"某段字节存在"，本函数补上**可读性**；
    完整可复核性由同一 finding 中的 `source_ref` + `file_sha256` + `line`/`object_id` 承担。
    """
    masked = WORDING_RE.sub(lambda m: "▮" * len(m.group(0)), text)
    masked = ARTIFACT_RE.sub(lambda m: "▮" * len(m.group(0)), masked)
    masked = masked.strip()
    return masked if len(masked) <= limit else masked[:limit] + "…"


def self_control_claim() -> str:
    """③ 内置**必败变异**用例：在**运行期拼接**一条标准对齐声称（源码内不得出现连续形态）。"""
    return "本设计" + "符合" + " " + "GB/T 48000.3-2026" + " 的全部要求。"


def run_self_control() -> tuple:
    """内置必败变异：合成声称**必须**被判违规（`classify_line` 返回 None）。

    返回 `(是否按预期被判违规, 说明)`；返回 False ⇒ 检测器/放行规则失效 ⇒ 门禁加 `SELF_CONTROL_FAILED`。
    作用：防"零候选/exit=0 假绿"——即使真实仓无违规，也必须证明**检测能力在线**。
    """
    claim = self_control_claim()
    reason = classify_line(claim, 0, [claim])
    detected = bool(WORDING_RE.search(claim))
    ok = detected and reason is None
    return ok, "合成声称：被候选正则命中=%s；放行原因=%s" % (detected, reason if reason else "None（⇒ 判违规，符合预期）")


# ---------------------------------------------------------------- 扫描


def iter_text_files(env: Env, stats: dict):
    for root in env.roots:
        root = Path(root)
        if not root.exists():
            stats["missing_roots"].append(str(root))
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".trash")]
            for name in sorted(filenames):
                path = Path(dirpath) / name
                if path.resolve() in env.exempt or name.startswith(OWN_ARTIFACT_PREFIX):
                    stats["skipped"]["self"] += 1
                    continue
                if path.suffix.lower() not in TEXT_EXTS:
                    stats["skipped"]["ext"] += 1
                    continue
                try:
                    size = path.stat().st_size
                except OSError:
                    stats["unreadable"].append(str(path))
                    continue
                if size > MAX_BYTES:
                    stats["skipped"]["big"] += 1
                    continue
                try:
                    text = path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    try:
                        text = path.read_text(encoding="utf-8", errors="replace")
                        stats["skipped"]["non_utf8"] += 1
                    except OSError:
                        stats["unreadable"].append(str(path))
                        continue
                except OSError:
                    stats["unreadable"].append(str(path))
                    continue
                stats["scanned"] += 1
                # O-12 ③：累积**受检文件集**摘要（供 fileset_sha256 守恒量使用）
                stats.setdefault("digests", []).append(
                    (str(path), hashlib.sha256(text.encode("utf-8")).hexdigest()))
                yield path, text


def _nearest_heading_is_neg(lines: list, idx: int) -> bool:
    """最近标题是否承载否定。**标题锚点用词级标记**（R-1/N-5：避免"门禁"里的单字 `禁`）。"""
    for j in range(idx, -1, -1):
        if HEADING_RE.match(lines[j]):
            return any(m in lines[j] for m in HEADING_NEG_MARKERS)
    return False


def _ancestor_negation(lines: list, idx: int, window: int = 25) -> bool:
    """JSON/YAML 列表项语境：条目归属的父键本身是禁止清单（如 forbidden_now / do_not_start）。

    标题锚点用**词级**标记（R-1/N-5）；父键锚点（键名形态，如 `forbidden_now:`）沿用原标记表。
    """
    for j in range(idx - 1, max(-1, idx - 1 - window), -1):
        prev = lines[j].rstrip()
        if HEADING_RE.match(prev):
            if any(m in prev for m in HEADING_NEG_MARKERS):
                return True
            continue
        if (prev.endswith(":") or prev.endswith("[")) and any(m in prev for m in NEG_MARKERS):
            return True
    return False


def classify_line(line: str, idx: int, lines: list):
    """返回放行原因；None 表示未放行（即违规）。单一真值函数的一部分。

    放行原因集合（逐原因计数，见 truth() 的 allowed_by_reason）：
        same_line_negation / table_row_negation / section_heading_negation /
        ancestor_key_negation / rule_statement（D-3，元陈述）
    """
    if any(m in line for m in NEG_MARKERS):
        return "same_line_negation"
    # 放行原因集合（逐原因计数，见 truth() 的 allowed_by_reason）新增一项：
    #    line_start_negation —— O-12 ①（2026-09-21）：行首**否定动词**式语句（「未签发…」「不发布…」）。
    #    **声称构造优先否决**：含 `CLAIM_CONSTRUCTION_RE` 的行不得据此放行（防「不〔符合〕…」被误放行）。
    if LINE_START_NEG_RE.match(line) and not CLAIM_CONSTRUCTION_RE.search(line):
        return "line_start_negation"
    lo, hi = max(0, idx - 2), min(len(lines), idx + 3)
    for j in range(lo, hi):
        if j == idx:
            continue
        candidate = lines[j].lstrip()
        if candidate.startswith("|") and any(m in lines[j] for m in NEG_MARKERS):
            return "table_row_negation"
    if _nearest_heading_is_neg(lines, idx):
        return "section_heading_negation"
    if _ancestor_negation(lines, idx):
        return "ancestor_key_negation"
    # D-3（N-1 收紧后）：规则陈述行。放在**最后**，即结构语境放行优先；
    # 本判定的作用面严格限于当前行——文件里别处出现元陈述关键词不会放行本行。
    if is_rule_statement(line):
        return "rule_statement"
    return None


def is_rule_statement(line: str) -> bool:
    """D-3 元陈述放行判定（N-1 收紧版；单一真值函数，--gate 与 --selftest 共用）。

    三条件同时成立才放行：含元陈述关键词 ∧ **不含声称构造** ∧ 含判定语义。
    见 `CLAIM_CONSTRUCTION_RE` / `JUDGEMENT_TOKENS` 上方注释（QA 第二轮 N-1 / §9.7 X3）。
    """
    if not any(marker in line for marker in META_STATEMENT_MARKERS):
        return False
    if CLAIM_CONSTRUCTION_RE.search(line):
        return False        # ② 该行自身即标准对齐声称 ⇒ 不放行（声称构造优先）
    if not any(token in line for token in JUDGEMENT_TOKENS):
        return False        # ③ 元陈述必须与判定语义共现，而非顺带提到主题词
    return True


# ---------------------------------------------------------------- 注册表


REGISTRY_KEYS = ("legacy_registered", "authority_registered", "filename_scope_exempt")


def load_registry(path: Path, findings: list, notes: list) -> dict:
    empty = {key: [] for key in REGISTRY_KEYS}
    if path is None or not path.exists():
        findings.append({"code": "REGISTRY_MISSING", "detail": str(path)})
        return empty
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        findings.append({"code": "REGISTRY_UNREADABLE", "detail": "%s: %s" % (path, exc)})
        return empty
    for key in REGISTRY_KEYS:
        entries = data.get(key) or []
        if not isinstance(entries, list):
            findings.append({"code": "REGISTRY_SHAPE_INVALID", "detail": key})
            data[key] = []
        data.setdefault(key, [])
    notes.append("注册表：历史件 %d 条 / 权威件 %d 条 / 文件名范围豁免 %d 条"
                 % (len(data["legacy_registered"]), len(data["authority_registered"]),
                    len(data["filename_scope_exempt"])))
    return data


def _resolve(entry_path: str, roots: list):
    p = Path(entry_path)
    if p.is_absolute():
        return p if p.exists() else None
    for root in roots:
        cand = Path(root) / entry_path
        if cand.exists():
            return cand
    return None


def verify_registry(registry: dict, env: Env, findings: list, notes: list):
    """注册表项必须存在且哈希未漂移；漂移 ⇒ FAIL（防止在历史件里续写声称）。"""
    by_path = {}
    for key in REGISTRY_KEYS:
        for entry in registry.get(key) or []:
            rel = entry.get("path")
            digest = entry.get("sha256")
            if not rel or not digest:
                findings.append({"code": "REGISTRY_ENTRY_INCOMPLETE", "detail": json.dumps(entry, ensure_ascii=False)})
                continue
            resolved = _resolve(rel, env.roots)
            if resolved is None:
                findings.append({"code": "REGISTRY_ENTRY_MISSING", "detail": rel})
                continue
            actual = sha256_file(resolved)
            if actual != digest:
                findings.append({
                    "code": "REGISTRY_ENTRY_DRIFT",
                    "detail": "%s（登记 %s… 实测 %s…）" % (rel, digest[:12], actual[:12]),
                })
            by_path[resolved.resolve()] = key
            notes.append("注册[%s] %s @%s…" % (key, rel, digest[:12]))
    return by_path


# ---------------------------------------------------------------- 条款矩阵与骨架


def check_matrix(env: Env, text_obtained: bool, findings: list, notes: list) -> int:
    rows = 0
    if env.matrix_csv is None or not env.matrix_csv.exists():
        findings.append({"code": "MATRIX_MISSING", "detail": str(env.matrix_csv)})
        return rows
    lines = [ln for ln in env.matrix_csv.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if not lines:
        findings.append({"code": "MATRIX_EMPTY_FILE", "detail": str(env.matrix_csv)})
        return rows
    header = lines[0].strip().lstrip("\ufeff")
    if header != MATRIX_HEADER:
        findings.append({"code": "MATRIX_HEADER_MISMATCH", "detail": "实际：%s" % header})
    rows = sum(1 for ln in lines[1:] if len([c for c in ln.split(",") if c.strip()]) > 1)
    notes.append("矩阵：表头行 1 + 数据行 %d；文本到手=%s" % (rows, text_obtained))
    if rows > 0 and not text_obtained:
        findings.append({"code": "CLAUSE_ROWS_BEFORE_TEXT", "detail": "%d 行" % rows})
    return rows


def check_skeleton(env: Env, text_obtained: bool, findings: list, notes: list) -> int:
    filled = 0
    if env.skeleton is None or not env.skeleton.exists():
        findings.append({"code": "SKELETON_MISSING", "detail": str(env.skeleton)})
        return filled
    text = env.skeleton.read_text(encoding="utf-8")
    name = env.skeleton.name
    if name != "REFERENCE-ALIGNMENT.md":
        findings.append({"code": "SKELETON_NAME_INVALID", "detail": name})
    if VERBATIM_SCOPE not in text:
        findings.append({"code": "SKELETON_VERBATIM_SCOPE_MISSING", "detail": "唯一可声明口径未逐字出现"})
    for col in REQUIRED_COLUMNS:
        if col not in text:
            findings.append({"code": "SKELETON_COLUMN_MISSING", "detail": col})
    for idx, line in enumerate(text.splitlines(), start=1):
        if CLAUSE_CELL_RE.match(line):
            filled += 1
            if not text_obtained:
                findings.append({"code": "SKELETON_CLAUSE_ROW_BEFORE_TEXT", "detail": "line %d" % idx})
    notes.append("骨架：%s；已填条款行 %d" % (name, filled))
    return filled


def read_text_status(env: Env, findings: list, notes: list) -> dict:
    """读不到或字段缺失一律按「文本未到手」处理（fail-closed）。"""
    default = {"text_obtained": False, "obtained_date": None, "channel": None, "receipt_ref": None}
    if env.status_json is None or not env.status_json.exists():
        findings.append({"code": "TEXT_STATUS_MISSING", "detail": str(env.status_json)})
        notes.append("文本状态：文件缺失 ⇒ 按未到手处理")
        return default
    try:
        data = json.loads(env.status_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        findings.append({"code": "TEXT_STATUS_UNREADABLE", "detail": "%s: %s" % (env.status_json, exc)})
        return default
    obtained = data.get("text_obtained")
    if not isinstance(obtained, bool):
        findings.append({"code": "TEXT_STATUS_FIELD_INVALID", "detail": "text_obtained 必须为布尔"})
        obtained = False
    if obtained and not (data.get("obtained_date") and data.get("channel") and data.get("receipt_ref")):
        findings.append({"code": "TEXT_OBTAINED_WITHOUT_RECEIPT",
                         "detail": "text_obtained=true 必须同时登记 obtained_date / channel / receipt_ref"})
    notes.append("文本状态：text_obtained=%s date=%s channel=%s"
                 % (obtained, data.get("obtained_date"), data.get("channel")))
    return {
        "text_obtained": obtained,
        "obtained_date": data.get("obtained_date"),
        "channel": data.get("channel"),
        "receipt_ref": data.get("receipt_ref"),
    }


# ---------------------------------------------------------------- 单一真值函数


def truth(env: Env) -> dict:
    findings = []
    notes = []
    stats = {"scanned": 0, "skipped": {"self": 0, "ext": 0, "big": 0, "non_utf8": 0},
             "unreadable": [], "missing_roots": []}

    registry = load_registry(env.registry, findings, notes)
    registered = verify_registry(registry, env, findings, notes)

    status = read_text_status(env, findings, notes)
    text_obtained = status["text_obtained"]

    violations = []
    registered_hits = []
    allowed_hits = 0
    allowed_by_reason: dict = {}
    candidates = 0
    filenames_checked = 0

    for path, text in iter_text_files(env, stats):
        resolved = path.resolve()
        # 规则 F：文件名
        base = path.name
        if CONFORMANCE_NAME_RE.search(base) or CN_COMPLIANCE_NAME_RE.search(base):
            filenames_checked += 1
            hard = bool(ONTOLOGY_NAME_RE.search(base)) or bool(CN_COMPLIANCE_NAME_RE.search(base))
            if registered.get(resolved) == "filename_scope_exempt":
                allowed_hits += 1
            elif hard:
                violations.append({"code": "FILENAME_CONFORMANCE_HARD", "file": str(path)})
            else:
                violations.append({"code": "FILENAME_CONFORMANCE_UNREGISTERED", "file": str(path)})

        gb_scope = bool(GB_SCOPE_RE.search(text))
        lines = text.splitlines()
        # O-12 ②：违规证据必须**可复核且可读**（sourceRef + 文件哈希 + 行号/object id + 脱敏摘要）
        file_digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        try:
            source_ref = str(path.resolve().relative_to(REPO_ROOT))
        except ValueError:      # 仓外根（如 `--root /tmp/...` 的夹具）：退化为绝对路径
            source_ref = str(path.resolve())
        for idx, line in enumerate(lines):
            if not (ARTIFACT_RE.search(line) or (gb_scope and WORDING_RE.search(line))):
                continue
            candidates += 1
            if registered.get(resolved) in REGISTRY_KEYS:
                registered_hits.append({"file": str(path), "line": idx + 1, "reason": registered[resolved]})
                continue
            reason = classify_line(line, idx, lines)
            if reason:
                allowed_hits += 1
                # D-3 要求"放行必须留计数"：逐原因累计，供审计放行是否过宽
                allowed_by_reason[reason] = allowed_by_reason.get(reason, 0) + 1
            else:
                violations.append({
                    "code": "CONTENT_WORDING_UNALLOWED",
                    "source_ref": source_ref,
                    "file": str(path),
                    "file_sha256": file_digest,
                    "line": idx + 1,
                    "object_id": "%s#L%d" % (Path(source_ref).name, idx + 1),
                    "line_sha256": hashlib.sha256(line.strip().encode("utf-8")).hexdigest()[:12],
                    # 可读 + 脱敏（触发词掩码）⇒ 审计可读、且报告自身不会成为违规源
                    "excerpt_redacted": redact_excerpt(line.strip()),
                    "evidence": redact(line.strip()),
                })

    check_skeleton(env, text_obtained, findings, notes)
    check_matrix(env, text_obtained, findings, notes)

    if stats["unreadable"]:
        findings.append({"code": "UNREADABLE_TEXT_FILE", "detail": "%d 个：%s"
                         % (len(stats["unreadable"]), ", ".join(stats["unreadable"][:5]))})
    if stats["missing_roots"]:
        findings.append({"code": "ROOT_MISSING", "detail": ", ".join(stats["missing_roots"])})
    for item in violations:
        findings.append(item)

    # O-12 ③ 守恒量 + 内置必败变异（**每次门禁报告固定输出**，防"零候选/exit=0 假绿"）
    script_version = sha256_file(Path(__file__))
    fileset = stats.get("digests") or []
    fileset_sha = hashlib.sha256(
        "\n".join(sorted("%s:%s" % (k, v) for k, v in fileset)).encode("utf-8")).hexdigest()
    notes.append(
        "守恒量：script_sha256=%s fileset_sha256=%s files=%d candidates=%d allowed=%d violations=%d"
        % (script_version[:16], fileset_sha[:16], stats["scanned"], candidates, allowed_hits, len(violations)))
    self_ok, self_detail = run_self_control()
    notes.append("内置必败变异（自控）：%s —— %s"
                 % ("按预期判违规" if self_ok else "**未按预期**", self_detail))
    if not self_ok:
        findings.append({"code": "SELF_CONTROL_FAILED",
                         "detail": "内置必败变异未被判违规 ⇒ 检测器或放行规则已失效：%s" % self_detail})

    # 空转防护
    if stats["scanned"] < env.min_files:
        findings.append({"code": "NOOP_SUSPECT_LOW_FILE_COUNT",
                         "detail": "扫描 %d < 下限 %d（疑似遍历失效）" % (stats["scanned"], env.min_files)})
    if candidates < env.min_candidates:
        findings.append({"code": "NOOP_SUSPECT_LOW_CANDIDATES",
                         "detail": "候选行 %d < 下限 %d（疑似正则失效）" % (candidates, env.min_candidates)})
    if allowed_hits < env.min_allowed:
        findings.append({"code": "NOOP_SUSPECT_LOW_ALLOWED",
                         "detail": "放行行 %d < 下限 %d（疑似放行规则失效）" % (allowed_hits, env.min_allowed)})

    fails = [f for f in findings if f["code"] != "NOTE"]
    return {
        "verdict": "PASS" if not fails else "FAIL",
        "findings": fails,
        "violations": len(violations),
        "counter": {
            "files_scanned": stats["scanned"],
            "filenames_checked": filenames_checked,
            "candidate_lines": candidates,
            "allowed_lines": allowed_hits,
            "allowed_by_reason": dict(sorted(allowed_by_reason.items())),
            "registered_legacy_hits": len(registered_hits),
            "unreadable": len(stats["unreadable"]),
            "skipped": stats["skipped"],
        },
        "text_obtained": text_obtained,
        "registered_legacy_sample": registered_hits[:20],
        "notes": notes,
        "roots": [str(r) for r in env.roots],
        "checked_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


# ---------------------------------------------------------------- 环境装配


def build_env(args) -> Env:
    exempt = {Path(__file__).resolve()}
    roots = [Path(r).resolve() for r in (args.root or [])]
    if not roots:
        roots = [REPO_ROOT]
        for extra in (Path("/home/szf/dev/Leibniz-KERT"), Path("/home/szf/dev/gits-kert-docs")):
            if extra.exists():
                roots.append(extra)
    loop = REPO_ROOT / "loops" / "ONTO1-ontology-split"
    return Env(
        roots=roots,
        registry=Path(args.registry) if args.registry else loop / "evidence" / "wi-a3-reference-wording-registry.json",
        skeleton=Path(args.skeleton) if args.skeleton else loop / "memory" / "staging" / "REFERENCE-ALIGNMENT.md",
        matrix_csv=Path(args.matrix) if args.matrix else loop / "evidence" / "wi-a3-clause-matrix-EMPTY.csv",
        status_json=Path(args.status) if args.status else loop / "evidence" / "wi-a3-d1-followup-status.json",
        min_files=args.min_files,
        min_candidates=args.min_candidates,
        min_allowed=args.min_allowed,
        exempt=exempt,
    )


def print_report(result: dict, stream=sys.stdout):
    print("verdict: %s" % result["verdict"])
    print("text_obtained: %s" % result["text_obtained"])
    print("roots: %s" % ", ".join(result["roots"]))
    c = result["counter"]
    print("counter: files=%d filenames=%d candidates=%d allowed=%d registered_legacy_hits=%d unreadable=%d"
          % (c["files_scanned"], c["filenames_checked"], c["candidate_lines"], c["allowed_lines"],
             c["registered_legacy_hits"], c["unreadable"]))
    # D-3②：元陈述放行必须留计数（该行是审计入口；异常增长 ⇒ 回看放行是否过宽）
    by_reason = c.get("allowed_by_reason", {})
    print("allowed[rule_statement]=%d" % by_reason.get("rule_statement", 0))
    print("allowed_by_reason: %s" % json.dumps(by_reason, ensure_ascii=False, sort_keys=True))
    print("skipped: %s" % json.dumps(c["skipped"], ensure_ascii=False))
    for line in result["notes"]:
        print("note: %s" % line)
    for finding in result["findings"]:
        detail = {k: v for k, v in finding.items() if k != "code"}
        print("finding: %s %s" % (finding["code"], json.dumps(detail, ensure_ascii=False)))
    print("OK" if result["verdict"] == "PASS" else "NOT_OK")


# ---------------------------------------------------------------- 变异复验


FIXTURE_GOV = """# 口径守则（夹具）

禁止任何国标符合性表述，不得使用 CONFORMANCE 文件名。
"""

FIXTURE_LEGACY = """# 历史件夹具

本文件为已被取代的历史件，保留原文；历史件国标符合性表述见附录。
"""

FIXTURE_STATUS = {
    "schema_version": "1.0",
    "text_obtained": False,
    "obtained_date": None,
    "channel": None,
    "receipt_ref": None,
}

# D-3 正向夹具：规则陈述行。第 4 行**不含任何否定标记**（避开 NEG_MARKERS，
# 否则会被 same_line_negation 先接走、测不到 rule_statement），只含元陈述关键词
# （「变异」「注入」）⇒ 必须靠 rule_statement 放行；且放行计数必须 >= 1（M10 附加断言）。
FIXTURE_RULE_STATEMENT = """# 规则说明（夹具）

本文件说明参照 GB/T 48000.3-2026 的核验程序。
变异用例：向制品注入「符合性」样本时，期望守卫给出 FAIL 判定。
"""

# D-3 边界夹具：规则陈述行（第 4 行，可放行）与**真实符合性声称**（第 5 行，无元陈述关键词）
# 同文件相邻。期望：第 4 行放行、第 5 行仍判 FAIL ⇒ 证明放行是行级的、不随文件扩散。
# 注：标题**刻意不含**「禁」等否定标记字（"门禁"含"禁"⇒ 既有 section_heading_negation 会
# 放行其下所有行；该放行过宽面已作为残余发现登记在 PKG-A3-ITER/HANDOFF，不在本包改动范围）。
FIXTURE_RULE_WITH_CLAIM = """# 规则说明（夹具）

变异用例：向制品注入「符合性」样本时，期望守卫给出 FAIL 判定。
本设计符合 GB/T 48000.3-2026 的全部要求。
"""

# QA 条件 C-6 夹具：**`loops/**` 内的真实声称**（无元陈述关键词、无否定标记）。
# 期望：必须 FAIL ⇒ 证明 D-3 放行不是"`loops/**` 目录白名单"，而是按行按语义。
FIXTURE_CLAIM_IN_LOOPS = """# 本循环说明（夹具）

本设计符合 GB/T 48000.3-2026 的全部要求。
"""

# QA 第二轮 N-1 反例夹具（对应 QA §9.7 **X3**）：真实声称行内**顺带含单个元陈述关键词**
# （"词表"）⇒ 必须 FAIL。收紧前该行会被 `rule_statement` 放行（= 漏检通道）；
# 收紧后：命中 `CLAIM_CONSTRUCTION_RE`（"符合 … 全部要求"）⇒ 不放行 ⇒ 判违规。
FIXTURE_CLAIM_WITH_META_KEYWORD = """# 说明（夹具）

本设计符合 GB/T 48000.3-2026 的全部要求，术语按词表统一。
"""

# QA 第二轮 N-5 / R-1 夹具（对应 QA §9.7 **X4**）：标题含"禁"的**复合词**（"门禁"）。
# 期望：其下的真实声称必须 FAIL ⇒ 证明标题锚点已改为**词级**匹配（单字 `禁` 不再放行）。
FIXTURE_CLAIM_UNDER_BARE_MARKER_HEADING = """# 门禁规则说明

本设计符合 GB/T 48000.3-2026 的全部要求。
"""

# R-1 正面对照夹具：标题为**词级**否定（"禁止事项"），其下的表述行（**不含**否定标记）
# 仍应经 `section_heading_negation` 放行 ⇒ 证明词级匹配没有误伤合法语境。
# （标题内提及 GB/T 只为让文件级 `gb_scope` 成立；标题本身不是候选行。）
FIXTURE_WORDING_UNDER_WORD_LEVEL_HEADING = """# 禁止事项（夹具；适用 GB/T 48000.3-2026 语境）

标准符合性表述清单见附录。
"""


def _build_fixture(base: Path, src: Env) -> None:
    (base / "docs").mkdir(parents=True, exist_ok=True)
    (base / "memory" / "staging").mkdir(parents=True, exist_ok=True)
    (base / "evidence").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src.skeleton, base / "memory" / "staging" / "REFERENCE-ALIGNMENT.md")
    shutil.copyfile(src.matrix_csv, base / "evidence" / "wi-a3-clause-matrix-EMPTY.csv")
    (base / "docs" / "gov-example.md").write_text(FIXTURE_GOV, encoding="utf-8")
    legacy = base / "docs" / "legacy-sample.md"
    legacy.write_text(FIXTURE_LEGACY, encoding="utf-8")
    (base / "evidence" / "wi-a3-d1-followup-status.json").write_text(
        json.dumps(FIXTURE_STATUS, ensure_ascii=False, indent=2), encoding="utf-8")
    registry = {
        "schema_version": "1.0",
        "legacy_registered": [{
            "path": "docs/legacy-sample.md",
            "sha256": sha256_file(legacy),
            "reason": "夹具历史件：仅登记不改写",
        }],
        "filename_scope_exempt": [],
    }
    (base / "evidence" / "wi-a3-reference-wording-registry.json").write_text(
        json.dumps(registry, ensure_ascii=False, indent=2), encoding="utf-8")


def _fixture_env(base: Path, src: Env) -> Env:
    return Env(
        roots=[base],
        registry=base / "evidence" / "wi-a3-reference-wording-registry.json",
        skeleton=base / "memory" / "staging" / "REFERENCE-ALIGNMENT.md",
        matrix_csv=base / "evidence" / "wi-a3-clause-matrix-EMPTY.csv",
        status_json=base / "evidence" / "wi-a3-d1-followup-status.json",
        min_files=4,
        min_candidates=2,
        min_allowed=1,
        exempt=src.exempt,
    )


def _mutate_add_conformance_file(base: Path):
    (base / "docs" / "ONTOLOGY-CONFORMANCE.md").write_text("# 决策载体\n", encoding="utf-8")


def _mutate_add_positive_claim(base: Path):
    (base / "docs" / "claim-positive.md").write_text(
        "# 说明\n\n本设计符合 GB/T 48000.3-2026 的全部要求。\n", encoding="utf-8")


def _mutate_fill_clause_row(base: Path):
    with open(base / "evidence" / "wi-a3-clause-matrix-EMPTY.csv", "a", encoding="utf-8") as fh:
        fh.write("5.2.1,适用,,,证据A,通过\n")


def _mutate_drop_verbatim(base: Path):
    path = base / "memory" / "staging" / "REFERENCE-ALIGNMENT.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(VERBATIM_SCOPE, "（口径待补）"), encoding="utf-8")


def _mutate_drop_matrix(base: Path):
    (base / "evidence" / "wi-a3-clause-matrix-EMPTY.csv").unlink()


def _mutate_text_obtained_with_row(base: Path):
    status = dict(FIXTURE_STATUS)
    status.update({"text_obtained": True, "obtained_date": "2026-10-08",
                   "channel": "夹具渠道", "receipt_ref": "夹具回执-001"})
    (base / "evidence" / "wi-a3-d1-followup-status.json").write_text(
        json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")
    _mutate_fill_clause_row(base)


def _mutate_strip_negation(base: Path):
    (base / "docs" / "gov-example.md").write_text(
        "# 口径守则（夹具）\n\n本项目国标符合性表述见附录；CONFORMANCE 文件名保留。\n", encoding="utf-8")


def _mutate_add_unregistered_conformance(base: Path):
    (base / "docs" / "contract_shape_conformance.py").write_text("# 夹具：未登记的同名词文件\n", encoding="utf-8")


def _mutate_extend_registered_legacy(base: Path):
    path = base / "docs" / "legacy-sample.md"
    with open(path, "a", encoding="utf-8") as fh:
        fh.write("追加：本设计符合 GB/T 48000.3-2026。\n")


def _mutate_add_rule_statement(base: Path):
    """D-3 正向：规则陈述行（含元陈述关键词）⇒ 放行。"""
    (base / "docs" / "gov-rule-statement.md").write_text(FIXTURE_RULE_STATEMENT, encoding="utf-8")


def _mutate_claim_adjacent_to_rule_statement(base: Path):
    """D-3 边界：真实符合性声称与规则陈述行**同文件相邻**（不同行）⇒ 仍判 FAIL。"""
    (base / "docs" / "gov-rule-with-claim.md").write_text(FIXTURE_RULE_WITH_CLAIM, encoding="utf-8")


def _mutate_claim_inside_loops_dir(base: Path):
    """QA 条件 C-6：**`loops/**` 目录不是白名单** —— 该目录内不带元陈述关键词的真实声称 ⇒ 仍判 FAIL。

    反例方向：若把 D-3 实现成"`loops/**` 整体放行"，则本文件会被放过（= BLOCKER）。
    本核验的实现是**行级关键词**判定，故本用例必须 FAIL。
    """
    loops_dir = base / "loops" / "ONTO1-ontology-split" / "memory"
    loops_dir.mkdir(parents=True, exist_ok=True)
    (loops_dir / "rule-statement-in-loops.md").write_text(FIXTURE_CLAIM_IN_LOOPS, encoding="utf-8")


def _mutate_claim_with_meta_keyword(base: Path):
    """QA 第二轮 N-1（BLOCKER）反例：真实声称 + 单个元陈述关键词 ⇒ 必须 FAIL。"""
    (base / "docs" / "claim-with-meta-keyword.md").write_text(
        FIXTURE_CLAIM_WITH_META_KEYWORD, encoding="utf-8")


def _mutate_claim_under_bare_marker_heading(base: Path):
    """QA 第二轮 N-5 / R-1 反例（§9.7 X4）：标题含"禁"的**复合词**（"门禁"）⇒ 其下真实声称必须 FAIL。"""
    (base / "docs" / "claim-under-bare-marker-heading.md").write_text(
        FIXTURE_CLAIM_UNDER_BARE_MARKER_HEADING, encoding="utf-8")


def _mutate_wording_under_word_level_heading(base: Path):
    """R-1 正面对照：标题为**词级**否定（"禁止事项"）⇒ 该语境的表述行仍应放行（词级匹配未误伤）。"""
    (base / "docs" / "wording-under-word-level-heading.md").write_text(
        FIXTURE_WORDING_UNDER_WORD_LEVEL_HEADING, encoding="utf-8")


def _expect_section_heading_negation(result: dict) -> bool:
    """正面对照断言：放行确由**标题锚点**路径给出（否则该用例测不到标题语义）。"""
    return result["counter"].get("allowed_by_reason", {}).get("section_heading_negation", 0) >= 1


def _expect_rule_statement_allowed(result: dict) -> bool:
    """D-3② 附加断言：放行**必须留计数**（否则放行规则是死代码 / 无法审计）。"""
    return result["counter"].get("allowed_by_reason", {}).get("rule_statement", 0) >= 1


SELFTEST_CASES = [
    ("M0 对照（未变异）", None, "PASS", None),
    ("M1 新增 ONTOLOGY-CONFORMANCE.md 文件名", _mutate_add_conformance_file, "FAIL", None),
    ("M2 正面声称符合 GB/T", _mutate_add_positive_claim, "FAIL", None),
    ("M3 矩阵在文本到手前填行", _mutate_fill_clause_row, "FAIL", None),
    ("M4 骨架丢失唯一可声明口径", _mutate_drop_verbatim, "FAIL", None),
    ("M5 矩阵空表缺失", _mutate_drop_matrix, "FAIL", None),
    ("M6 文本到手登记 + 矩阵填行", _mutate_text_obtained_with_row, "PASS", None),
    ("M7 去除否定标记后的声称", _mutate_strip_negation, "FAIL", None),
    ("M8 未登记的非本体 conformance 文件名", _mutate_add_unregistered_conformance, "FAIL", None),
    ("M9 在已登记历史件里续写声称", _mutate_extend_registered_legacy, "FAIL", None),
    ("M10 规则陈述行（含元陈述关键词）⇒ 放行且留计数", _mutate_add_rule_statement, "PASS",
     _expect_rule_statement_allowed),
    ("M11 真实声称（无元陈述关键词，与规则行同文件相邻）⇒ 仍 FAIL",
     _mutate_claim_adjacent_to_rule_statement, "FAIL", None),
    ("M12 loops/** 内的真实声称（不是目录白名单）⇒ 仍 FAIL", _mutate_claim_inside_loops_dir,
     "FAIL", None),
    ("M13 真实声称 + 单个元陈述关键词（QA N-1/X3）⇒ 仍 FAIL", _mutate_claim_with_meta_keyword,
     "FAIL", None),
    ("M14 标题含『禁』复合词（门禁）下的真实声称（QA N-5/X4）⇒ 仍 FAIL",
     _mutate_claim_under_bare_marker_heading, "FAIL", None),
    ("M15 标题为词级否定（禁止事项）⇒ 该语境仍放行且走 section_heading_negation",
     _mutate_wording_under_word_level_heading, "PASS", _expect_section_heading_negation),
]


def run_selftest(src: Env) -> int:
    failures = 0
    for name, mutate, expected, extra in SELFTEST_CASES:
        tmp = Path(tempfile.mkdtemp(prefix="onto1-a3-selftest-"))
        try:
            _build_fixture(tmp, src)
            if mutate:
                mutate(tmp)
            result = truth(_fixture_env(tmp, src))
            got = result["verdict"]
            ok = got == expected
            if extra is not None and not extra(result):
                ok = False
                print(f"      └ 附加断言未成立：{getattr(extra, '__name__', 'extra')}")
            failures += 0 if ok else 1
            codes = ",".join(sorted({f["code"] for f in result["findings"]})) or "-"
            print("%s %-36s expect=%-4s got=%-4s findings=%s"
                  % ("[ok]" if ok else "[BAD]", name, expected, got, codes))
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    print("selftest: %d/%d 符合预期" % (len(SELFTEST_CASES) - failures, len(SELFTEST_CASES)))
    if failures:
        print("selftest: NOT_OK")
        return 1
    print("selftest: OK")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="ONTO1 WI-A3 / D1 参照对齐口径日常核验")
    parser.add_argument("--gate", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--root", action="append", help="可重复；默认 GITS 主仓 + 可用的兄弟仓")
    parser.add_argument("--registry")
    parser.add_argument("--skeleton")
    parser.add_argument("--matrix")
    parser.add_argument("--status")
    parser.add_argument("--min-files", type=int, default=100)
    parser.add_argument("--min-candidates", type=int, default=5)
    parser.add_argument("--min-allowed", type=int, default=1)
    args = parser.parse_args()

    if not args.gate and not args.selftest:
        parser.error("需要 --gate 或 --selftest")

    env = build_env(args)
    if args.selftest:
        return run_selftest(env)

    result = truth(env)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_report(result)
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
