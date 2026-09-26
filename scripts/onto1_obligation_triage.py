#!/usr/bin/env python3
"""ONTO1 WI-A2 §4 / W-1.5 PKG-A1｜候选义务三层判定引擎（真义务 / 同名候选 / 待回源）。

问题陈述
========
`consumer-scan-obligations.csv` 的 **1052 行**净义务（FOLLOW_MIGRATION 1038 +
CONTROL_PLANE_REQUIRED 14）是**词法命中**的产物：扫描按 token（本体类名/属性名/IRI 字面量/
ID 模式）命中文件即判"候选消费面"。WI-A2 报告 §4 已用 3 类抽样证伪其中一部分为**同名不同物**
（`customerId`=MyBatis 库列、前端 `Customer`=OpenAPI DTO、`AC-004`=账号号段）。
因此：**未回源的 1038 行既不能当义务执行，也不能算已排除**。本引擎做第一遍机器分层，
把人工回源范围从 1052 行压到"待回源"那一层。

三层信号（判据来自 W-1.5 派工单，不自创口径）
=============================================
强（STRONG → TRUE_OBLIGATION）
  a. 文件内容含本体 IRI 字面量 / OWL 语句 / SPARQL-RDF 语句 / `gits-core` /
     `versions.ontology` / `planHash`（`STRONG_CONTENT_PATTERNS`）；
  b. 或路径落在已确认消费面（`STRONG_PATH_PREFIXES`）；其中 `apps/api` **仅限本体端口/规划器相关**
     （`APPS_API_PORT_HINTS`），非该类文件落中信号。
弱（WEAK → HOMONYM_CANDIDATE，需同名机械证明；无证明落 NEEDS_SOURCE_CHECK）
  只出现**裸术语名**（category ∈ `BARE_TERM_CATEGORIES`）且位于 DTO/UI/测试/日志/持久化面
  （`WEAK_PATH_DECLARED` + `WEAK_PATH_EXTENDED`）。
中（MEDIUM → NEEDS_SOURCE_CHECK）
  其余（合同/映射/物化链路附近：`specs/*` 其余、`scripts/*`、`scenario/*`、KERT `examples|skills` 其余）。

推理口径声明（**必须被 TL 审计，不得静默扩权**）
================================================
I-1 弱信号面扩展：派工单列举 `frontend/*`、`tests/*`、`adapters/persistence-relational/*`、
    `evidence/*`、`loops/*`；本仓测试实际位于 `**/src/test/**`、DTO 位于 `**/dto/**`，
    故把这两类并入弱信号面（`signal` 中标出对应 rule id；`--strict-weak-surface` 可关闭）。
I-2 同名判定要求**机械证明**（H1 库列 snake_case / H2 合同类型精确导入且命名解析唯一 /
    H3 前端 SDK 类型导入），且证明必须**唯一解析**（同文件出现本体/领域包同名或通配导入即禁判）；
    tier=WEAK 但无证明的行落 `NEEDS_SOURCE_CHECK`（更保守）。
    summary 同时给出"仅按 tier 判同名"的替代计数 `alternatives.homonym_if_tier_only` 供 TL 裁定。
I-3 `id_pattern` 命中（CTR-/KM-/AC-/ASSET-/SP-/KI-/KD-）不是"裸术语名"，故弱信号面要求
    category ∈ 裸术语；弱面上带 ID 命中的文件落 `NEEDS_SOURCE_CHECK`。
I-4 `TRUE_OBLIGATION` = 「必须跟随迁移」的判定，**不是**「已确认本体消费」的最终结论；
    Wave 2 逐条回源仍可推翻。`HOMONYM_CANDIDATE` 同理 ≠ 已排除。
I-5 刻意**不**把「文件自述该名来自 OpenAPI 合同」当作同名证明（例：`api/dto/ClaimResponse.java:9`
    同段又写「本 DTO 同时携带两种语义字段」）⇒ 该形态落 NEEDS_SOURCE_CHECK。
I-6 待回源行再分两档：P0 = 裸名按简单名精确解析到本体/知识模型包
    （`import com.gien.gits.ontology.<Term>` 一类，Java 本体模型层耦合）；P1 = 其余。
    **TL 已裁定（2026-09-21，PKG-A1b）：P0 升格为 `TRUE_OBLIGATION` + Wave `W3_CONSUMER_SWITCH`**，
    开关 `RULING_I6_UPGRADE_P0`（集中一处，可回退）。理由（fail-closed）：显式导入是**代码级耦合**的
    机械证据 ⇒ 四层拆分若改命名空间/包结构，消费面必须跟随；"不能证明无关"即不得静默排除。
    **附带义务（下发给 Wave 2）**：抽检必须优先覆盖 P0 面前 5 行，逐一确认包语义（防"同名包无关"），
    若抽检推翻则按证据回退。**反例（D-12）**：无 `PROOF:IMPORT_LINE` 机械证据的弱面行判 TRUE ⇒ G5 FAIL。

防假绿三件套
============
1) **单一真值函数**：所有判定由 `triage()` / `triage_row()` 产出；CSV、摘要、报告、门禁、变异复验
   共用同一实现（报告里的数字不可能与门禁看到的不同）。
2) **fail-closed**：输入缺失、基线行数漂移、输入处置锚点不符、源文件缺失、证据不可回源
   —— 任一情况一律 FAIL（exit 2），绝不"缺夹具即跳过"。
3) **期望值锚定（防空转）**：`BASELINE_ROWS=1052` 与输入处置锚点 `1038/14` 是硬锚点；
   强信号面计数为 0 亦判 FAIL（证明分层逻辑没有整体塌掉）。
4) **变异复验**：`--selftest` M0~M9（见 `selftest()` docstring）。

用法
====
    python3 scripts/onto1_obligation_triage.py --report      # 生成 CSV + 摘要 + 报告
    python3 scripts/onto1_obligation_triage.py --gate        # 门禁（G1~G8），exit 0/2
    python3 scripts/onto1_obligation_triage.py --selftest    # 变异复验 M0~M6，exit 0/2
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

# --------------------------------------------------------------------------- #
# 路径与输出
# --------------------------------------------------------------------------- #
ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
DEFAULT_REPO_ROOTS = {"gits": ROOT, "kert": WORKSPACE / "Leibniz-KERT"}

EVIDENCE_DIR = ROOT / "loops/ONTO1-ontology-split/evidence"
OBLIGATIONS_CSV = EVIDENCE_DIR / "consumer-scan-obligations.csv"
HITS_JSONL = EVIDENCE_DIR / "consumer-scan-hits.jsonl"
OUT_CSV = EVIDENCE_DIR / "obligation-triage.csv"
OUT_SUMMARY = EVIDENCE_DIR / "obligation-triage-summary.json"
OUT_REPORT = EVIDENCE_DIR / "PKG-A1-义务收敛报告.md"

BASELINE_SCAN_REPORT = "loops/ONTO1-ontology-split/evidence/WI-A2-消费者扫描报告.md"

# --------------------------------------------------------------------------- #
# 输入锚点（fail-closed：不符即 FAIL，不改写为 inconclusive）
# --------------------------------------------------------------------------- #
BASELINE_ROWS = 1052
BASELINE_INPUT_DISPOSITIONS = {"FOLLOW_MIGRATION": 1038, "CONTROL_PLANE_REQUIRED": 14}
INPUT_COLUMNS = ["repo", "disposition", "category", "path", "rule_id", "tokens", "lines", "action"]
OUTPUT_COLUMNS = ["repo", "path", "tier", "signal", "disposition", "rationale", "evidence",
                  "responsible_wave"]

# --------------------------------------------------------------------------- #
# 判定词汇
# --------------------------------------------------------------------------- #
TIER_STRONG, TIER_WEAK, TIER_MEDIUM = "STRONG", "WEAK", "MEDIUM"
DISPO_TRUE, DISPO_HOMONYM, DISPO_NEEDS = "TRUE_OBLIGATION", "HOMONYM_CANDIDATE", "NEEDS_SOURCE_CHECK"
DISPOSITIONS = (DISPO_TRUE, DISPO_HOMONYM, DISPO_NEEDS)
WAVE_W2 = "W2_SPLIT"
WAVE_W3 = "W3_CONSUMER_SWITCH"
WAVE_W3_KERT = "W3_KERT_ASSETS"
WAVE_HOMONYM = "NOT_APPLICABLE_HOMONYM"
WAVE_PENDING = "PENDING_SOURCE_CHECK"

# ---- TL 裁定 I-6（2026-09-21，PKG-A1b）------------------------------------
# P0（裸名按简单名**精确解析到本体/知识模型包**）**升格为真义务**，随四层拆分迁移。
# 依据：`import <pkg>.<Class>;` 是**可机械复核**的代码级耦合证据（G5 会二次校验该行确为
# 对应包的精确导入），四层拆分若改命名空间/包结构，消费面必须跟随。
# 开关集中一处：便于审计与**一键回退**（回退后真义务 626 / 待回源 426）。
RULING_I6_UPGRADE_P0 = True
P0_IMPORT_PROOF = "PROOF:IMPORT_LINE"
# D-12 反例（本升格是"放宽"性质的例外，必须自带反例）：**弱面行判 TRUE 但不含**
# `PROOF:IMPORT_LINE` + `RESOLVES_TO_ONTOLOGY_PKG:` 机械证据 ⇒ G5 必须 FAIL。
# 由 `--selftest` M2a/M2b（弱面判真义务）与 TL 独立变异 MU-4（剥掉 P0 标签）共同保证。

NEEDS_REASON_NO_EVIDENCE_OF_CONSUMPTION = "无本体消费证据（仅词法命中裸术语）"

# --------------------------------------------------------------------------- #
# 规则表（强信号）
# --------------------------------------------------------------------------- #
# 行级强内容信号：命中即判"文件确实在本体/RDF 语义层"（不是词法同名）
STRONG_CONTENT_PATTERNS = [
    ("IRI_GIENTECH", re.compile(r"gientech\.com/gits/kno/")),
    ("IRI_BANK_EXAMPLE", re.compile(r"gits\.bank\.example/ontology/core#")),
    ("OWL_IMPORTS", re.compile(r"owl:imports")),
    ("TTL_PREFIX", re.compile(r"@prefix")),
    ("SPARQL_PREFIX", re.compile(r"^\s*PREFIX\s+\w+\s*:")),
    ("RDF_STATEMENT", re.compile(r"\brdf:|\brdfs:")),
    ("OWL_STATEMENT", re.compile(r"owl:")),
    ("FILE_GITS_CORE", re.compile(r"gits-core")),
    ("VERSIONS_ONTOLOGY", re.compile(r"versions\.ontology")),
    ("PLAN_HASH", re.compile(r"planHash")),
]
# SPARQL 查询跨行（SELECT ... WHERE），单独处理：证据行取 SELECT 所在行
SPARQL_QUERY_NAME = "SPARQL_QUERY"
SPARQL_SELECT = re.compile(r"\bSELECT\b")
SPARQL_QUERY = re.compile(r"(?is)\bSELECT\b.{0,400}?\bWHERE\b")

# 路径级强信号：已确认消费面（派工单口径）
STRONG_PATH_PREFIXES = [
    ("gits", "modules/operational-ontology/", "R-STRONG-PATH-MODULE-OPERATIONAL-ONTOLOGY"),
    ("gits", "modules/knowledge-architecture/", "R-STRONG-PATH-MODULE-KNOWLEDGE-ARCH"),
    ("gits", "modules/scenario-customer-journey/", "R-STRONG-PATH-MODULE-SCENARIO-JOURNEY"),
    ("gits", "adapters/semantic-jena/", "R-STRONG-PATH-ADAPTER-SEMANTIC-JENA"),
    ("gits", "adapters/knowledge-filesystem/", "R-STRONG-PATH-ADAPTER-KNOWLEDGE-FS"),
    ("gits", "specs/semantic/", "R-STRONG-PATH-SPEC-SEMANTIC"),
    ("gits", "specs/knowledge-architecture/", "R-STRONG-PATH-SPEC-KNOWLEDGE-ARCH"),
    ("gits", "specs/gk-ke/", "R-STRONG-PATH-SPEC-GK-KE"),
    ("gits", "specs/CONTRACT_INDEX.yaml", "R-STRONG-PATH-SPEC-CONTRACT-INDEX"),
    ("kert", "src/kert/", "R-STRONG-PATH-KERT-SRC"),
    ("kert", "examples/bank-front-knowledge-maps/90_control/", "R-STRONG-PATH-KERT-90-CONTROL"),
]
APPS_API_PREFIX = "apps/api/"
APPS_API_PORT_HINTS = ("knowledge", "ontology", "semantic", "activation", "plan", "jena", "rdf",
                       "sparql", "gk-ke")
APPS_API_RULE = "R-STRONG-PATH-APPS-API-PORT-OR-PLANNER"

# --------------------------------------------------------------------------- #
# 规则表（弱信号）+ 同名机械证明
# --------------------------------------------------------------------------- #
# I-1：DECLARED = 派工单列举；EXTENDED = 本仓惯用路径（测试/DTO 面），可用 --strict-weak-surface 关闭
WEAK_PATH_DECLARED = [
    ("frontend/", "R-WEAK-PATH-FRONTEND"),
    ("tests/", "R-WEAK-PATH-TESTS"),
    ("adapters/persistence-relational/", "R-WEAK-PATH-PERSISTENCE-RELATIONAL"),
    ("evidence/", "R-WEAK-PATH-EVIDENCE"),
    ("loops/", "R-WEAK-PATH-LOOPS"),
]
WEAK_PATH_EXTENDED = [
    ("/src/test/", "R-WEAK-PATH-EXT-SRC-TEST"),
    ("/dto/", "R-WEAK-PATH-EXT-DTO"),
    ("/__tests__/", "R-WEAK-PATH-EXT-FRONTEND-TEST"),
]
BARE_TERM_CATEGORIES = ("owl_class", "owl_object_property", "owl_datatype_property")
MEDIUM_SIGNAL_ID_ON_WEAK_SURFACE = "MEDIUM_PATH_WEAK_SURFACE_ID_PATTERN"
MEDIUM_SIGNAL_FALLBACK = "MEDIUM_PATH"

SHORT_CIRCUIT_RATIONALE = "short-circuit-constant"  # 仅用于变异复验 M4
PLACEHOLDER_PATTERNS = (r"\bTODO\b", r"\bFIXME\b", r"<placeholder>", r"XXX待补")

# 扫描器 token 标签 → 文件中的字面量（iri_or_file_ref 类别的 token 是标签而非文本）
TOKEN_LITERAL_PATTERNS = {
    "IRI_GIENTECH": r"gientech\.com/gits/kno/",
    "IRI_BANK_EXAMPLE": r"gits\.bank\.example/ontology/core#",
    "PREFIX_GITS": r"gits:",
    "FILE_GITS_CORE": r"gits-core",
}


class InputError(RuntimeError):
    """输入/证据不可用 ⇒ 一律 FAIL（fail-closed）。"""


# --------------------------------------------------------------------------- #
# 输入加载（fail-closed）
# --------------------------------------------------------------------------- #
def load_obligation_rows(path: Path) -> list[dict]:
    if not path.is_file():
        raise InputError(f"obligations csv missing: {path}")
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames != INPUT_COLUMNS:
            raise InputError(f"obligations csv header mismatch: {reader.fieldnames}")
        rows = [dict(r) for r in reader]
    if not rows:
        raise InputError(f"obligations csv has no data rows: {path}")
    seen: dict[tuple, int] = {}
    for idx, r in enumerate(rows):
        key = (r["repo"], r["path"], r["category"], r["tokens"], r["lines"], r["rule_id"])
        if key in seen:
            raise InputError(f"ambiguous duplicate obligation row at lines {seen[key] + 2}/{idx + 2}: {key}")
        seen[key] = idx
    return rows


def load_hits(path: Path) -> dict[tuple[str, str], list[dict]]:
    if not path.is_file():
        raise InputError(f"hits jsonl missing: {path}")
    grouped: dict[tuple[str, str], list[dict]] = {}
    count = 0
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            grouped.setdefault((obj["repo"], obj["path"]), []).append(obj)
            count += 1
    if count == 0:
        raise InputError(f"hits jsonl empty: {path}")
    return grouped


class SourceCache:
    """源文件正文缓存（判据与证据校验共用；缺文件 ⇒ 记 missing，由门禁判 FAIL）。"""

    def __init__(self, repo_roots: dict[str, Path]):
        self.repo_roots = dict(repo_roots)
        self._lines: dict[tuple[str, str], list[str] | None] = {}
        self.missing: list[str] = []

    def lines(self, repo: str, path: str) -> list[str] | None:
        key = (repo, path)
        if key not in self._lines:
            base = self.repo_roots.get(repo)
            target = (base / path) if base else None
            if target is None or not target.is_file():
                self._lines[key] = None
                self.missing.append(f"{repo}:{path}")
            else:
                self._lines[key] = target.read_text(encoding="utf-8", errors="replace").splitlines()
        return self._lines[key]

    @property
    def loaded(self) -> int:
        return len(self._lines)


# --------------------------------------------------------------------------- #
# 文本工具
# --------------------------------------------------------------------------- #
def split_tokens(raw: str) -> list[str]:
    return [t for t in (raw or "").split(";") if t.strip()]


def token_regex(tok: str) -> re.Pattern:
    if tok in TOKEN_LITERAL_PATTERNS:
        return re.compile(TOKEN_LITERAL_PATTERNS[tok])
    return re.compile(r"(?<![A-Za-z0-9_])" + re.escape(tok) + r"(?![A-Za-z0-9_])")


def locate_tokens(lines: list[str], tokens: list[str]) -> list[tuple[str, int]]:
    """返回 [(token, 1-based line)]，按文件行序、token 声明序去重。"""
    out: list[tuple[str, int]] = []
    for tok in tokens:
        rx = token_regex(tok)
        for idx, line in enumerate(lines):
            if rx.search(line):
                out.append((tok, idx + 1))
                break
    return out


def strong_content_hit(lines: list[str]) -> tuple[str, int] | None:
    """返回 (pattern_name, 1-based line)；SPARQL 查询取 SELECT 所在行。"""
    for idx, line in enumerate(lines):
        for name, rx in STRONG_CONTENT_PATTERNS:
            if rx.search(line):
                return name, idx + 1
    for idx, line in enumerate(lines):
        if SPARQL_SELECT.search(line):
            window = "\n".join(lines[idx:idx + 8])
            if SPARQL_QUERY.search(window):
                return SPARQL_QUERY_NAME, idx + 1
    return None


def snake_case(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def evidence_of(repo: str, path: str, line: int) -> str:
    return f"{repo}:{path}:{line}"


# --------------------------------------------------------------------------- #
# 命名解析（弱/中面共用）：裸名是否**精确解析到本体模型包**
# --------------------------------------------------------------------------- #
def ontology_pkg_resolve(tokens: list[str], lines: list[str]) -> tuple[str, str, int] | None:
    """返回 (包名, token, 1-based 导入行)：裸名按简单名精确解析到本体/知识模型包。

    这是**优先级信号**（不是判定）：如 `import com.gien.gits.ontology.Customer;` 表明该文件的
    裸名就是 `modules/operational-ontology` 的 Java 本体模型类 ⇒ 回源时属"只差确认"的一类。
    刻意**不**据此直接判 `TRUE_OBLIGATION`（派工单强信号清单未含此形态，不自创口径）。
    """
    named, _ = _imports(lines)
    for tok in tokens:
        pkg = named.get(tok)
        if not pkg or not ONTOLOGY_PKG_RX.search(pkg):
            continue
        rx = re.compile(r"^\s*import\s+(?:static\s+)?[\w.]*[.]" + re.escape(tok) + r"\s*;")
        for idx, line in enumerate(lines):
            if rx.search(line):
                return pkg, tok, idx + 1
    return None


# --------------------------------------------------------------------------- #
# 弱信号同名证明（H1~H3，机械可复算）
# --------------------------------------------------------------------------- #
# 同名证明刻意**不收**的形态（诚实性）：文件自述"该名来自 OpenAPI 合同"（如
# `api/dto/ClaimResponse.java:9` 同段又写"本 DTO 同时携带两种语义字段"）⇒ 不能判同名，
# 因为该文件可能同时是本体语义的消费者。此类一律落 NEEDS_SOURCE_CHECK。
CONTRACT_PKG_RX = re.compile(r"(?:^|\.)(?:dto|contract|contracts|api|model)(?:\.|$)")
ONTOLOGY_PKG_RX = re.compile(r"(?:^|\.)(?:ontology|kno|semantic|domain|core)(?:\.|$)")


def _imports(lines: list[str]) -> tuple[dict[str, str], list[str]]:
    """返回 ({简单类名: 包名}, [通配导入的包名])。"""
    named: dict[str, str] = {}
    wildcard: list[str] = []
    rx = re.compile(r"^\s*import\s+(?:static\s+)?([\w.]+?)(\.\*)?\s*;")
    for line in lines:
        m = rx.match(line)
        if not m:
            continue
        dotted, wild = m.group(1), m.group(2)
        if wild:
            wildcard.append(dotted)
        else:
            named[dotted.rsplit(".", 1)[-1]] = dotted.rsplit(".", 1)[0] if "." in dotted else ""
    return named, wildcard


def homonym_proof(path: str, tokens: list[str], lines: list[str]) -> tuple[str, str, int] | None:
    """返回 (proof_kind, matched_token, 1-based line)；无证明返回 None（⇒ NEEDS_SOURCE_CHECK）。

    H1_DB_COLUMN      驼峰 token 的 snake_case 形态出现 ⇒ 库列/查询参数，非 OWL 属性
    H2_CONTRACT_TYPE  文件**按简单名导入**了该术语，且来源包是 dto/contract/api/model，
                      且**没有**任何本体/领域包的同名导入或通配导入（否则命名解析不唯一 ⇒ 不判）
    H3_FRONTEND_SDK   `import type { Token } from '.../api/...'`（WI-A2 报告 §4 抽样 2 形态）
    """
    named, wildcard = _imports(lines)
    ontology_wildcard = [w for w in wildcard if ONTOLOGY_PKG_RX.search(w)]
    # H1_DB_COLUMN
    for tok in tokens:
        snake = snake_case(tok)
        if snake != tok.lower():
            rx = re.compile(r"(?<![A-Za-z0-9_])" + re.escape(snake) + r"(?![A-Za-z0-9_])")
            for idx, line in enumerate(lines):
                if rx.search(line):
                    return "H1_DB_COLUMN", tok, idx + 1
    # H2_CONTRACT_TYPE（严格：命名解析必须唯一，且不得来自本体/领域包）
    if not ontology_wildcard:
        for tok in tokens:
            src_pkg = named.get(tok)
            if src_pkg is None or not CONTRACT_PKG_RX.search(src_pkg):
                continue
            rx = re.compile(r"^\s*import\s+(?:static\s+)?[\w.]*[.]" + re.escape(tok) + r"\s*;")
            for idx, line in enumerate(lines):
                if rx.search(line):
                    return "H2_CONTRACT_TYPE", tok, idx + 1
    # H3_FRONTEND_SDK_TYPE
    for tok in tokens:
        rx = re.compile(r"import\s+type\s*\{[^}]*\b" + re.escape(tok)
                        + r"\b[^}]*\}\s*from\s*['\"][^'\"]*api")
        for idx, line in enumerate(lines):
            if rx.search(line):
                return "H3_FRONTEND_SDK_TYPE", tok, idx + 1
    return None


# --------------------------------------------------------------------------- #
# 责任 Wave
# --------------------------------------------------------------------------- #
def wave_from_action(action: str) -> str | None:
    if "Wave 2" in action:
        return WAVE_W2
    if "Wave 3" in action:
        return WAVE_W3
    return None


def wave_for_path(repo: str, path: str) -> str:
    if path.startswith("specs/"):
        return WAVE_W2
    if repo == "kert" and (path.startswith("examples/") or path.startswith("skills/")):
        return WAVE_W3_KERT
    if repo == "kert" and path.startswith("specs/"):
        return WAVE_W2
    return WAVE_W3


def phase_label(wave: str) -> str:
    return {
        WAVE_W2: "Wave 2 四层拆分 / 合同先行",
        WAVE_W3: "Wave 3 双侧换消费 / 原子窗口",
        WAVE_W3_KERT: "Wave 3 KERT 知识资产换版",
        WAVE_HOMONYM: "不适用（同名候选，不计义务）",
        WAVE_PENDING: "待回源（未回源前不计义务）",
    }.get(wave, wave)


# --------------------------------------------------------------------------- #
# 单一真值函数
# --------------------------------------------------------------------------- #
def triage_row(entry: dict, ctx: SourceCache, strict_weak_surface: bool = False) -> dict:
    """**唯一判定点**：输入一行净义务 + 源文件正文 ⇒ 输出一行判定。"""
    repo, path, category = entry["repo"], entry["path"], entry["category"]
    tokens = split_tokens(entry["tokens"])
    lines = ctx.lines(repo, path)
    if lines is None:
        raise InputError(f"source file missing (cannot judge): {repo}:{path}")

    evidence_lines = locate_tokens(lines, tokens)
    if not evidence_lines:
        raise InputError(f"no locatable hit token in source file: {repo}:{path} tokens={tokens}")

    content_hit = strong_content_hit(lines)
    strong_path = next((rule for rp, prefix, rule in STRONG_PATH_PREFIXES
                        if rp == repo and path.startswith(prefix)), None)
    apps_port = (repo == "gits" and path.startswith(APPS_API_PREFIX)
                 and any(hint in path.lower() for hint in APPS_API_PORT_HINTS))
    weak_rule = None
    for prefix, rule in WEAK_PATH_DECLARED:
        if path.startswith(prefix):
            weak_rule = rule
            break
    if weak_rule is None and not strict_weak_surface:
        for frag, rule in WEAK_PATH_EXTENDED:
            if frag in path:
                weak_rule = rule
                break

    # ---- 分层（强 > 弱 > 中）----
    if content_hit is not None:
        tier, signal = TIER_STRONG, f"STRONG_CONTENT:{content_hit[0]}"
    elif strong_path is not None:
        tier, signal = TIER_STRONG, f"STRONG_PATH:{strong_path}"
    elif apps_port:
        tier, signal = TIER_STRONG, f"STRONG_PATH:{APPS_API_RULE}"
    elif weak_rule is not None:
        tier, signal = TIER_WEAK, f"WEAK_PATH:{weak_rule}"
    else:
        tier, signal = TIER_MEDIUM, MEDIUM_SIGNAL_FALLBACK

    # ---- 判定 + 证据 ----
    if tier == TIER_STRONG:
        if content_hit is not None:
            line = content_hit[1]
            rule_txt = f"文件含{content_hit[0]}（本体/RDF 语义层语句）"
        else:
            line = evidence_lines[0][1]
            rule_txt = f"路径落已确认消费面（{signal.split(':', 1)[1]}）"
        reason = (f"强信号：{rule_txt}；命中术语 {evidence_lines[0][0]}@L{evidence_lines[0][1]}"
                  f"⇒ 必须跟随迁移")
        if entry["disposition"] == "CONTROL_PLANE_REQUIRED":
            # 控制面修复（硬编码 ID / 前缀缺陷 / D3-A 残留）在 Wave 3 执行（执行计划 §6）；
            # 除非 action 自身指明 Wave 2（如 CONTRACT_INDEX 拆条登记）
            wave = wave_from_action(entry["action"]) or WAVE_W3
        else:
            wave = wave_from_action(entry["action"]) or wave_for_path(repo, path)
        return {
            "repo": repo, "path": path, "tier": tier, "signal": signal,
            "disposition": DISPO_TRUE, "rationale": reason,
            "evidence": evidence_of(repo, path, line), "responsible_wave": wave,
        }

    if tier == TIER_WEAK and category in BARE_TERM_CATEGORIES:
        proof = homonym_proof(path, tokens, lines)
        if proof is not None:
            kind, tok, line = proof
            return {
                "repo": repo, "path": path, "tier": tier,
                "signal": f"{signal}|PROOF:{kind}",
                "disposition": DISPO_HOMONYM,
                "rationale": (f"弱信号面裸术语 {tok} 有同名机械证明（{kind}）"
                              f"⇒ 同名候选；不计义务，但**不等于已排除**（Wave 2 可推翻）"),
                "evidence": evidence_of(repo, path, line), "responsible_wave": WAVE_HOMONYM,
            }
        resolved = ontology_pkg_resolve(tokens, lines)
        if resolved is not None:
            pkg, tok, imp_line = resolved
            if RULING_I6_UPGRADE_P0:
                # TL 裁定 I-6：带机械导入证据的 P0 行升格为真义务（G5 对该证据做二次校验）
                return {
                    "repo": repo, "path": path, "tier": tier,
                    "signal": f"{signal}|{P0_IMPORT_PROOF}|RESOLVES_TO_ONTOLOGY_PKG:{pkg}",
                    "disposition": DISPO_TRUE,
                    "rationale": (f"TL 裁定 I-6：弱信号面裸术语 {tok} **精确解析到本体/领域模型包 "
                                  f"{pkg}**（`import` 行机械证据 @L{imp_line}）⇒ **升格为真义务**，"
                                  f"随四层拆分跟随迁移；Wave 2 须优先抽检 P0 面前 5 行确认包语义"),
                    "evidence": evidence_of(repo, path, imp_line), "responsible_wave": WAVE_W3,
                }
            return {
                "repo": repo, "path": path, "tier": tier,
                "signal": f"{signal}|PROOF:NONE|RESOLVES_TO_ONTOLOGY_PKG:{pkg}",
                "disposition": DISPO_NEEDS,
                "rationale": (f"弱信号面裸术语，无同名机械证明；但 {tok} **精确解析到本体模型包 "
                              f"{pkg}**（Java 本体/领域模型层耦合）⇒ 回源优先级 P0："
                              f"只需确认该类是否随四层拆分改名/换 IRI；本行仍不计义务、不算已排除"),
                "evidence": evidence_of(repo, path, imp_line), "responsible_wave": WAVE_PENDING,
            }
        line = evidence_lines[0][1]
        return {
            "repo": repo, "path": path, "tier": tier, "signal": f"{signal}|PROOF:NONE",
            "disposition": DISPO_NEEDS,
            "rationale": (f"弱信号面裸术语但无同名机械证明 ⇒ {NEEDS_REASON_NO_EVIDENCE_OF_CONSUMPTION}；"
                          f"须 Wave 2 逐条回源（不得计义务，也不得算已排除）"),
            "evidence": evidence_of(repo, path, line), "responsible_wave": WAVE_PENDING,
        }

    # ---- 中信号（含"弱面但带 ID 模式"的例外）----
    line = evidence_lines[0][1]
    if weak_rule is not None and category not in BARE_TERM_CATEGORIES:
        signal = MEDIUM_SIGNAL_ID_ON_WEAK_SURFACE
        why = (f"弱信号面无裸术语命中（category={category}，属注册/合同 ID）⇒ "
               f"ID 模式不可仅凭词法判定")
    else:
        why = NEEDS_REASON_NO_EVIDENCE_OF_CONSUMPTION
    resolved = ontology_pkg_resolve(tokens, lines)
    if resolved is not None:
        pkg, tok, imp_line = resolved
        if RULING_I6_UPGRADE_P0:
            # TL 裁定 I-6：中信号面 P0 行同样升格为真义务（同一条机械证据口径）
            return {
                "repo": repo, "path": path, "tier": tier,
                "signal": f"{signal}|{P0_IMPORT_PROOF}|RESOLVES_TO_ONTOLOGY_PKG:{pkg}",
                "disposition": DISPO_TRUE,
                "rationale": (f"TL 裁定 I-6：中信号面 {tok} **精确解析到本体/领域模型包 {pkg}**"
                              f"（`import` 行机械证据 @L{imp_line}）⇒ **升格为真义务**，"
                              f"随四层拆分跟随迁移；Wave 2 须优先抽检 P0 面前 5 行确认包语义"),
                "evidence": evidence_of(repo, path, imp_line), "responsible_wave": WAVE_W3,
            }
        signal = f"{signal}|RESOLVES_TO_ONTOLOGY_PKG:{pkg}"
        why += (f"；但 {tok} 精确解析到本体/领域模型包 {pkg}（Java 模型层耦合）⇒ 回源优先级 P0")
        line = imp_line
    return {
        "repo": repo, "path": path, "tier": tier, "signal": signal,
        "disposition": DISPO_NEEDS,
        "rationale": (f"中信号：{why}；命中 {evidence_lines[0][0]}@L{evidence_lines[0][1]}"
                      f" ⇒ 须逐条回源（人工/会话），本行**不计义务、也不算已排除**"),
        "evidence": evidence_of(repo, path, line), "responsible_wave": WAVE_PENDING,
    }


def triage(entries: list[dict], hits: dict[tuple[str, str], list[dict]], ctx: SourceCache,
           strict_weak_surface: bool = False) -> tuple[list[dict], dict]:
    """对全部净义务行跑三层判定；同时做命中表完整性对账（缺即 InputError）。"""
    for entry in entries:
        key = (entry["repo"], entry["path"])
        if key not in hits:
            raise InputError(f"obligation has no hits record: {key}")
        hits_tokens = {h.get("token") for h in hits[key]}
        missing = [t for t in split_tokens(entry["tokens"]) if t and t not in hits_tokens]
        if missing:
            raise InputError(f"obligation token absent from hits: {key} tokens={missing}")
    rows = [triage_row(entry, ctx, strict_weak_surface=strict_weak_surface) for entry in entries]
    meta = {
        "rows": len(rows),
        "source_files_loaded": ctx.loaded,
        "source_files_missing": list(ctx.missing),
    }
    return rows, meta


# --------------------------------------------------------------------------- #
# 对账
# --------------------------------------------------------------------------- #
def group_key(repo: str, path: str) -> str:
    parts = path.split("/")
    return f"{repo}:{'/'.join(parts[:3]) if len(parts) >= 3 else path}"


def reconcile(rows: list[dict], baseline_rows: int) -> dict:
    counts = {d: 0 for d in DISPOSITIONS}
    tiers = {TIER_STRONG: 0, TIER_WEAK: 0, TIER_MEDIUM: 0}
    dirs: dict[str, dict] = {}
    waves: dict[str, dict] = {}
    for r in rows:
        counts[r["disposition"]] = counts.get(r["disposition"], 0) + 1
        tiers[r["tier"]] = tiers.get(r["tier"], 0) + 1
        d = dirs.setdefault(group_key(r["repo"], r["path"]),
                            {"total": 0, DISPO_TRUE: 0, DISPO_HOMONYM: 0, DISPO_NEEDS: 0})
        d["total"] += 1
        d[r["disposition"]] += 1
        w = waves.setdefault(r["responsible_wave"], {"total": 0, "dirs": {}})
        w["total"] += 1
        w["dirs"][group_key(r["repo"], r["path"])] = w["dirs"].get(
            group_key(r["repo"], r["path"]), 0) + 1
    total = sum(counts.values())
    return {
        "baseline_rows": baseline_rows,
        "true_obligation": counts.get(DISPO_TRUE, 0),
        "homonym_candidate": counts.get(DISPO_HOMONYM, 0),
        "needs_source_check": counts.get(DISPO_NEEDS, 0),
        "sum": total,
        "closed": total == baseline_rows,
        "delta": total - baseline_rows,
        "by_tier": tiers,
        "by_directory": dirs,
        "by_wave": waves,
    }


# --------------------------------------------------------------------------- #
# 门禁校验（G1~G8）
# --------------------------------------------------------------------------- #
def _read_output_csv(path: Path) -> list[dict] | None:
    if not path.is_file():
        return None
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames != OUTPUT_COLUMNS:
            return None
        return [dict(r) for r in reader]


def run_checks(obligations_csv: Path, hits_jsonl: Path, repo_roots: dict[str, Path],
               baseline_rows: int, expected_input_dispositions: dict[str, int],
               out_csv: Path, out_summary: Path, strict_weak_surface: bool = False) -> list[str]:
    """跑全部门禁断言，返回失败列表（空 = PASS）。所有异常按 FAIL 处理（fail-closed）。"""
    failures: list[str] = []

    # ---- G1 输入锚定（fail-closed）----
    try:
        entries = load_obligation_rows(obligations_csv)
        hits = load_hits(hits_jsonl)
    except InputError as exc:
        return [f"G1 input unusable (fail-closed): {exc}"]
    if len(entries) != baseline_rows:
        failures.append(f"G1 baseline row drift: input={len(entries)} expected={baseline_rows}")
    got_disp: dict[str, int] = {}
    for e in entries:
        got_disp[e["disposition"]] = got_disp.get(e["disposition"], 0) + 1
    if got_disp != expected_input_dispositions:
        failures.append(f"G1 input disposition anchor mismatch: {got_disp} != "
                        f"{expected_input_dispositions}")

    # ---- 跑真值函数 ----
    ctx = SourceCache(repo_roots)
    try:
        rows, meta = triage(entries, hits, ctx, strict_weak_surface=strict_weak_surface)
    except InputError as exc:
        return failures + [f"G1 truth-function input error (fail-closed): {exc}"]
    if meta["source_files_missing"]:
        failures.append(f"G1 source files missing: {len(meta['source_files_missing'])} "
                        f"e.g. {meta['source_files_missing'][:3]}")

    # ---- 目标产物 = 磁盘 CSV（交付物本身必须过行级断言；缺文件 ⇒ fail-closed）----
    disk_rows = _read_output_csv(out_csv)
    if disk_rows is None:
        failures.append(f"G2 triage csv missing or header mismatch (fail-closed): {out_csv}")
        disk_rows = []

    tokens_by_path: dict[tuple[str, str], set[str]] = {}
    for e in entries:
        tokens_by_path.setdefault((e["repo"], e["path"]), set()).update(split_tokens(e["tokens"]))

    # ---- G2 对账闭合（复算 + 磁盘产物 双向）----
    for label, target in (("computed", rows), ("disk", disk_rows)):
        rec_t = reconcile(target, baseline_rows)
        if len(target) != baseline_rows or not rec_t["closed"]:
            failures.append(f"G2 [{label}] reconciliation not closed: true={rec_t['true_obligation']} "
                            f"homonym={rec_t['homonym_candidate']} "
                            f"needs={rec_t['needs_source_check']} sum={rec_t['sum']} "
                            f"baseline={baseline_rows}")

    # ---- G3 强信号面 100% 有判定（无 NEEDS 残留）+ 非空转（双向）----
    for label, target in (("computed", rows), ("disk", disk_rows)):
        strong_rows = [r for r in target if r.get("tier") == TIER_STRONG]
        if not strong_rows:
            failures.append(f"G3 [{label}] strong-signal face is empty (分层逻辑整体塌掉 ⇒ 空转)")
        for r in [x for x in strong_rows if x.get("disposition") != DISPO_TRUE][:10]:
            failures.append(f"G3 [{label}] strong signal not adjudicated: {r.get('evidence')} "
                            f"tier={r.get('tier')} disposition={r.get('disposition')}")
        signals = [str(r.get("signal", "")) for r in strong_rows]
        if strong_rows and not any(s.startswith("STRONG_CONTENT") for s in signals):
            failures.append(f"G3 [{label}] no content-level strong hit at all "
                            f"(IRI/OWL/SPARQL 检出能力可疑)")
        if strong_rows and not any(s.startswith("STRONG_PATH") for s in signals):
            failures.append(f"G3 [{label}] no path-level strong hit at all (路径面规则未生效)")

    def row_level(label: str, target: list[dict]) -> list[str]:
        """G4 证据可回源 / G5 弱面反一刀切 / G6 Wave 合法 / G8 无占位。"""
        out: list[str] = []
        # G4
        for r in target:
            if r.get("disposition") not in (DISPO_TRUE, DISPO_HOMONYM):
                continue
            ev = str(r.get("evidence") or "")
            if not ev or ev.count(":") < 2:
                out.append(f"G4 [{label}] {r.get('disposition')} without evidence: "
                           f"{r.get('repo')}:{r.get('path')}")
                continue
            repo, path, line_txt = ev.split(":", 2)
            if not line_txt.isdigit():
                out.append(f"G4 [{label}] evidence line not numeric: {ev}")
                continue
            lines = ctx.lines(repo, path)
            if lines is None:
                out.append(f"G4 [{label}] evidence source file missing: {ev}")
                continue
            line_no = int(line_txt)
            if line_no < 1 or line_no > len(lines):
                out.append(f"G4 [{label}] evidence line out of range: {ev} "
                           f"(file has {len(lines)} lines)")
                continue
            content = lines[line_no - 1]
            if not _evidence_verifies(content, r, tokens_by_path.get((repo, path), set())):
                out.append(f"G4 [{label}] evidence does not verify at source: {ev} "
                           f"-> {content.strip()[:80]!r}")
        # G5
        for r in target:
            if r.get("tier") == TIER_WEAK and r.get("disposition") == DISPO_TRUE:
                # **TL 裁定 I-6 的唯一例外**：带 `PROOF:IMPORT_LINE` + `RESOLVES_TO_ONTOLOGY_PKG:`
                # 机械证据的 P0 行允许升格（证据行还须通过下方"精确导入"二次校验）。
                # **反例（D-12，必须仍 FAIL）**：无该证据的弱面行判 TRUE —— M2a/M2b 与 TL 变异 MU-4 覆盖。
                sig_now = str(r.get("signal", ""))
                if not (P0_IMPORT_PROOF in sig_now and "RESOLVES_TO_ONTOLOGY_PKG:" in sig_now):
                    out.append(f"G5 [{label}] weak-signal row judged TRUE_OBLIGATION without I-6 machine proof "
                               f"(一刀切): {r.get('evidence')}")
            if r.get("tier") == TIER_WEAK and r.get("disposition") == DISPO_HOMONYM \
                    and "PROOF:" not in str(r.get("signal", "")):
                out.append(f"G5 [{label}] homonym without machine proof: {r.get('evidence')}")
            # RESOLVES_TO_ONTOLOGY_PKG 是一个**可复核**的标签：证据行必须是"该 token 从该包精确导入"。
            #
            # **FIX-2026-09-21（QA 第三轮 BLOCKER，`FAIL-2026-09-20-W15TL-09`）**：本块原先**缩进为
            # 8 空格**（与 `for r in target:` 同级）⇒ **出循环**，只对 `target` 末元素求值、依赖泄漏的
            # 循环变量；真实仓末行恰为非 P0 行 ⇒ 该断言对 65 行 P0 **覆盖 0/65**（TL 复核：把 65 行包名
            # 全改成不存在的包，本检查命中 **0**，只剩 1 条 G7）。现移入循环 ⇒ **逐行**校验，且因条件挂在
            # `signal` 标签上，**覆盖全部 tier**（含 36 行 MEDIUM 升格行）。
            # 反例（D-12）：M9b-2（单行改包名 ⇒ FAIL）、**M9b-3（全部 P0 改包名 ⇒ 命中数 == 行数）**。
            sig = str(r.get("signal", ""))
            if "RESOLVES_TO_ONTOLOGY_PKG:" in sig:
                pkg = sig.split("RESOLVES_TO_ONTOLOGY_PKG:", 1)[1]
                ev = str(r.get("evidence") or "")
                ok = False
                if ev.count(":") >= 2:
                    repo, path, line_txt = ev.split(":", 2)
                    lines = ctx.lines(repo, path) if line_txt.isdigit() else None
                    if lines and 1 <= int(line_txt) <= len(lines):
                        m = re.match(r"^\s*import\s+(?:static\s+)?([\w.]+)\s*;$",
                                     lines[int(line_txt) - 1])
                        if m:
                            simple = m.group(1).rsplit(".", 1)[-1]
                            pkgname = m.group(1).rsplit(".", 1)[0]
                            ok = simple in tokens_by_path.get((repo, path), set()) and pkgname == pkg
                if not ok:
                    out.append(f"G5 [{label}] ontology-pkg resolve label without import evidence: {ev}")
        if target and len({r.get("disposition") for r in target}) < 2:
            out.append(f"G5 [{label}] all rows share a single disposition (真值函数疑似被短路)")
        # G6
        for r in target:
            disp, wave = r.get("disposition"), r.get("responsible_wave")
            if disp == DISPO_TRUE and wave not in (WAVE_W2, WAVE_W3, WAVE_W3_KERT):
                out.append(f"G6 [{label}] true obligation without actionable wave: "
                           f"{r.get('evidence')} wave={wave}")
            if disp == DISPO_HOMONYM and wave != WAVE_HOMONYM:
                out.append(f"G6 [{label}] homonym wave not N/A: {r.get('evidence')}")
            if disp == DISPO_NEEDS and wave != WAVE_PENDING:
                out.append(f"G6 [{label}] needs-source-check wave not PENDING: {r.get('evidence')}")
        # G8
        for r in target:
            blob = " ".join(str(r.get(k)) for k in OUTPUT_COLUMNS)
            for pat in PLACEHOLDER_PATTERNS:
                if re.search(pat, blob):
                    out.append(f"G8 [{label}] placeholder text in output row: "
                               f"{r.get('evidence')} ({pat})")
        return out

    failures += row_level("computed", rows)
    failures += row_level("disk", disk_rows)

    # ---- G7 磁盘产物与本次复算一致（防手改证据）----
    if disk_rows:
        if len(disk_rows) != len(rows):
            failures.append(f"G7 csv row count drift: disk={len(disk_rows)} computed={len(rows)}")
        else:
            for i, (a, b) in enumerate(zip(disk_rows, rows)):
                if {k: a.get(k) for k in OUTPUT_COLUMNS} != {k: b.get(k) for k in OUTPUT_COLUMNS}:
                    failures.append(f"G7 csv row {i + 2} drifted from recomputation: "
                                    f"{a.get('repo')}:{a.get('path')} "
                                    f"disk={a.get('disposition')}/{a.get('evidence')} "
                                    f"computed={b.get('disposition')}/{b.get('evidence')}")
                    break
    if not out_summary.is_file():
        failures.append(f"G7 summary json missing: {out_summary}")
    else:
        try:
            disk_sum = json.loads(out_summary.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"G7 summary json unreadable: {exc}")
            disk_sum = None
        if isinstance(disk_sum, dict):
            rec = reconcile(rows, baseline_rows)
            recomputed = build_summary(rows, entries, hits, meta, rec, baseline_rows,
                                       expected_input_dispositions, obligations_csv, hits_jsonl,
                                       out_csv, strict_weak_surface)
            for key in ("reconciliation", "by_tier", "by_signal_rule", "true_by_wave",
                        "true_evidence_strength", "needs_by_directory", "needs_priority",
                        "homonym_rows", "alternatives"):
                if disk_sum.get(key) != recomputed.get(key):
                    failures.append(f"G7 summary section drifted from recomputation: {key}")
    return failures


def _evidence_verifies(content: str, row: dict, tokens: set[str]) -> bool:
    """证据行必须**自证**（不是"填了就算"）：
    a) 强内容证据行必须真的命中该强内容模式；
    b) 其余（路径强信号 / 同名候选）证据行必须含该文件的某个命中 token（或其 snake_case 形态 /
       同名证明形态），否则该 `文件:行` 不成立 ⇒ FAIL。"""
    signal = row["signal"]
    if signal.startswith("STRONG_CONTENT:"):
        name = signal.split(":", 1)[1]
        if name == SPARQL_QUERY_NAME:
            return bool(SPARQL_SELECT.search(content))
        for pat_name, rx in STRONG_CONTENT_PATTERNS:
            if pat_name == name:
                return bool(rx.search(content))
        return False
    for tok in tokens:
        if token_regex(tok).search(content):
            return True
        snake = snake_case(tok)
        if snake != tok.lower() and re.search(r"(?<![A-Za-z0-9_])" + re.escape(snake)
                                             + r"(?![A-Za-z0-9_])", content):
            return True
        if re.search(r"import\s+[\w.]*\.(?:dto|contract|contracts|model|api)\.\w*"
                     + re.escape(tok) + r"\w*\s*;", content):
            return True
        if re.search(r"(?<![A-Za-z0-9_])" + re.escape(tok) + r"(?![A-Za-z0-9_])", content) \
                and "OpenAPI" in content:
            return True
    return False


# --------------------------------------------------------------------------- #
# 摘要 / 报告
# --------------------------------------------------------------------------- #
def _signal_rule(signal: str) -> str:
    """信号族（去掉 `|PROOF:...` / `|RESOLVES_TO_ONTOLOGY_PKG:...` 等后缀）。"""
    return signal.split("|", 1)[0]


def _proof_kind(signal: str) -> str:
    return signal.split("PROOF:", 1)[1] if "PROOF:" in signal else "-"


def build_summary(rows: list[dict], entries: list[dict], hits: dict, meta: dict, rec: dict,
                  baseline_rows: int, expected_input_dispositions: dict[str, int],
                  obligations_csv: Path, hits_jsonl: Path, out_csv: Path,
                  strict_weak_surface: bool) -> dict:
    by_rule: dict[str, int] = {}
    for r in rows:
        by_rule[_signal_rule(r["signal"])] = by_rule.get(_signal_rule(r["signal"]), 0) + 1
    true_by_wave: dict[str, dict] = {}
    needs_dirs: dict[str, int] = {}
    for r in rows:
        if r["disposition"] == DISPO_TRUE:
            w = true_by_wave.setdefault(r["responsible_wave"], {"total": 0, "dirs": {}})
            w["total"] += 1
            k = group_key(r["repo"], r["path"])
            w["dirs"][k] = w["dirs"].get(k, 0) + 1
        elif r["disposition"] == DISPO_NEEDS:
            k = group_key(r["repo"], r["path"])
            needs_dirs[k] = needs_dirs.get(k, 0) + 1
    for w in true_by_wave.values():
        # 转成 list-of-list：JSON 往返后仍与内存中的复算结果逐字相等（G7 依赖此可比较性）
        w["dirs_sorted"] = [[d, n] for d, n in sorted(w["dirs"].items(),
                                                       key=lambda kv: (-kv[1], kv[0]))]
    homonym_rows = [{"repo": r["repo"], "path": r["path"], "evidence": r["evidence"],
                     "proof": _proof_kind(r["signal"]), "rationale": r["rationale"]}
                    for r in rows if r["disposition"] == DISPO_HOMONYM]
    true_rows = [r for r in rows if r["disposition"] == DISPO_TRUE]
    true_by_rule: dict[str, int] = {}
    for r in true_rows:
        k = _signal_rule(r["signal"])
        true_by_rule[k] = true_by_rule.get(k, 0) + 1
    true_content = [r for r in true_rows if r["signal"].startswith("STRONG_CONTENT")]
    true_path = [r for r in true_rows if r["signal"].startswith("STRONG_PATH")]
    true_evidence_strength = {
        "content_evidence": {
            "total": len(true_content),
            "note": "文件正文含本体 IRI / OWL / SPARQL / gits-core / planHash 等语义层语句 "
                    "⇒ 依据最强（每条证据行由 G4 逐行回源复核）",
        },
        "path_evidence_only": {
            "total": len(true_path),
            "note": "仅在「已确认消费面」路径内命中术语，依据是路径规则（派工单口径）"
                    "⇒ **回源可推翻**，是 Wave 2 抽检的首选对象",
        },
        "by_rule": dict(sorted(true_by_rule.items(), key=lambda kv: (-kv[1], kv[0]))),
    }
    p0_rows = [r for r in rows if "RESOLVES_TO_ONTOLOGY_PKG:" in r["signal"]]
    p0_dirs: dict[str, int] = {}
    p0_by_pkg: dict[str, int] = {}
    for r in p0_rows:
        k = group_key(r["repo"], r["path"])
        p0_dirs[k] = p0_dirs.get(k, 0) + 1
        pkg = r["signal"].split("RESOLVES_TO_ONTOLOGY_PKG:", 1)[1]
        p0_by_pkg[pkg] = p0_by_pkg.get(pkg, 0) + 1
    needs_priority = {
        "P0_ONTOLOGY_PKG_COUPLED": {
            "total": len(p0_rows),
            "note": "**TL 裁定 I-6 已升格**（2026-09-21，PKG-A1b）：裸名按简单名精确解析到本体/领域模型包"
                    "（包名含 ontology/kno/semantic/domain/core 段，如 com.gien.gits.ontology）⇒ "
                    "`disposition=TRUE_OBLIGATION`、`wave=W3_CONSUMER_SWITCH`；机械证据 = 该 `import` 行"
                    "（由 G5 二次校验\"精确导入该包\"）。"
                    "**未升格前的对照口径**：这部分原属 `NEEDS_SOURCE_CHECK`（真义务 626 / 待回源 426），"
                    "升格后为 **691 / 361**；开关 `RULING_I6_UPGRADE_P0` 可一键回退。"
                    "**下发给 Wave 2 的抽检义务**：必须优先抽检本面前 5 行确认包语义（防同名包无关），"
                    "抽检推翻则按证据回退并留痕。",
            "by_package": dict(sorted(p0_by_pkg.items(), key=lambda kv: (-kv[1], kv[0]))),
            "dirs_sorted": [[d, n] for d, n in sorted(p0_dirs.items(), key=lambda kv: (-kv[1], kv[0]))][:20],
            "samples": [{"evidence": r["evidence"], "path": r["path"]} for r in p0_rows[:10]],
        },
        "P1_OTHER_NEEDS": {
            "total": rec["needs_source_check"],
            "note": "其余待回源行（无本体包解析证据，也无同名证明）—— 全部落在 `NEEDS_SOURCE_CHECK`。",
        },
    }
    tier_counts = rec["by_tier"]
    weak_total = tier_counts.get(TIER_WEAK, 0)
    weak_needs = sum(1 for r in rows if r["tier"] == TIER_WEAK and r["disposition"] == DISPO_NEEDS)
    homonym_if_tier_only = rec["homonym_candidate"] + weak_needs
    needs_if_tier_only = rec["needs_source_check"] - weak_needs
    return {
        "schema": "onto1_obligation_triage/v1",
        "loop_id": "ONTO1-ontology-split",
        "wi": "WI-A2 §4 消费者义务回源确认（W-1.5 PKG-A1）",
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "inputs": {
            "obligations_csv": _rel(obligations_csv),
            "obligations_rows": len(entries),
            "input_dispositions": expected_input_dispositions,
            "hits_jsonl": _rel(hits_jsonl),
            "hits_paths": len(hits),
            "repo_roots": {k: str(v) for k, v in DEFAULT_REPO_ROOTS.items()},
            "source_files_loaded": meta["source_files_loaded"],
            "source_files_missing": meta["source_files_missing"],
            "baseline_rows_anchor": baseline_rows,
            "strict_weak_surface": strict_weak_surface,
        },
        "reconciliation": rec,
        "by_tier": tier_counts,
        "by_signal_rule": dict(sorted(by_rule.items(), key=lambda kv: (-kv[1], kv[0]))),
        "true_by_wave": {k: {"total": v["total"], "dirs_sorted": v["dirs_sorted"]}
                         for k, v in sorted(true_by_wave.items())},
        "needs_by_directory": dict(sorted(needs_dirs.items(), key=lambda kv: (-kv[1], kv[0]))),
        "needs_priority": needs_priority,
        "true_evidence_strength": true_evidence_strength,
        "homonym_rows": homonym_rows,
        "alternatives": {
            "homonym_if_tier_only": homonym_if_tier_only,
            "needs_if_tier_only": needs_if_tier_only,
            "weak_rows_without_proof": weak_needs,
            "note": "口径 I-2：本 CSV 采用『需机械证明才算同名』的保守口径；"
                    "上列 alternatives 为『tier=WEAK 即判同名』口径下的计数，供 TL 裁定。",
        },
        "interpretations": [
            "I-1 弱信号面并入本仓惯用的 **/src/test/** 与 **/dto/**（派工单列举之外，signal 中标 rule id）",
            "I-2 HOMONYM 需机械证明 H1/H2/H3，且要求命名解析唯一"
            "（同文件出现本体/领域包同名导入或通配导入 ⇒ 禁判同名）；无证明落 NEEDS_SOURCE_CHECK",
            "I-3 id_pattern（CTR-/KM-/AC-/ASSET-/SP-/KI-/KD-）不算裸术语名，弱面带 ID 命中落 NEEDS",
            "I-4 TRUE_OBLIGATION = 必须跟随迁移，不等于已确认本体消费；Wave 2 回源可推翻",
            "I-5 刻意不收「文件自述该名来自 OpenAPI 合同」作为同名证明"
            "（如 api/dto/ClaimResponse.java:9 同段又写『本 DTO 同时携带两种语义字段』）",
            "I-6 待回源行再分 P0（裸名精确解析到本体/领域模型包）/ P1（其余）两档；"
            "**TL 已裁定 P0 升格为 TRUE_OBLIGATION + W3_CONSUMER_SWITCH**（机械证据 = 精确 import 行；"
            "开关 RULING_I6_UPGRADE_P0 可回退；原 626/426 口径作为对照保留）",
        ],
        "outputs": {"csv": str(out_csv.name)},
    }


def _rel(path: Path) -> str:
    """仓内相对路径（用于摘要可读性）；仓外路径（变异复验夹具）原样返回。"""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _md_table(headers: list[str], rows: list[list]) -> str:
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(out) + "\n"


def render_report(summary: dict) -> str:
    rec = summary["reconciliation"]
    tier = summary["by_tier"]
    lines: list[str] = []
    add = lines.append
    add("# ONTO1 PKG-A1｜候选义务三层收敛报告（WI-A2 §4 义务回源确认）")
    add("")
    add("| 项 | 值 |")
    add("|---|---|")
    add(f"| 性质 | 只读分析（W-1.5 就绪加固）；不改 `specs/**`/`generated/**`/`docs/dd/**`；KERT 仓只读 |")
    add(f"| 输入 | `{summary['inputs']['obligations_csv']}`（{summary['inputs']['obligations_rows']} 行）"
        f" + `consumer-scan-hits.jsonl` |")
    add(f"| 复现 | `python3 scripts/onto1_obligation_triage.py --report` → `--gate` → `--selftest` |")
    add(f"| 机读产出 | `obligation-triage.csv`、`obligation-triage-summary.json` |")
    add(f"| 生成时间 | {summary['generated_at']} |")
    add("")
    add("## 1. 收敛结果（对账闭合）")
    add("")
    add(_md_table(["判定", "行数", "占 1052", "含义"], [
        ["`TRUE_OBLIGATION`（真义务）", rec["true_obligation"],
         f"{rec['true_obligation'] / rec['baseline_rows']:.1%}", "强信号：本体 IRI/OWL/SPARQL 语句，或已确认消费面 → 必须跟随迁移"],
        ["`HOMONYM_CANDIDATE`（同名候选）", rec["homonym_candidate"],
         f"{rec['homonym_candidate'] / rec['baseline_rows']:.1%}", "弱信号面裸术语 + 同名机械证明（H1/H2/H3）→ 不计义务（**≠ 已排除**）"],
        ["`NEEDS_SOURCE_CHECK`（待回源）", rec["needs_source_check"],
         f"{rec['needs_source_check'] / rec['baseline_rows']:.1%}", "中信号 / 弱面无证明 → Wave 2 逐条回源，本行不计义务也不算已排除"],
        ["**合计**", rec["sum"], f"{rec['sum'] / rec['baseline_rows']:.1%}",
         f"基线 {rec['baseline_rows']}；闭合 = {rec['closed']}（delta {rec['delta']}）"],
    ]))
    add("")
    add(f"分层信号：STRONG {tier.get('STRONG', 0)} / WEAK {tier.get('WEAK', 0)} / "
        f"MEDIUM {tier.get('MEDIUM', 0)}。")
    add("")
    add("## 2. 方法与三层规则（与脚本规则表一一对应）")
    add("")
    add("- **强信号 ⇒ 真义务**：文件含本体 IRI 字面量（`gientech.com/gits/kno/`、"
        "`gits.bank.example/ontology/core#`）、`owl:imports`/`owl:`/`rdf:`/`rdfs:` 语句、"
        "`@prefix`/SPARQL `PREFIX`/`SELECT…WHERE`、`gits-core`、`versions.ontology`、`planHash`；"
        "**或**路径落已确认消费面（`modules/{operational-ontology,knowledge-architecture,"
        "scenario-customer-journey}`、`adapters/{semantic-jena,knowledge-filesystem}`、`specs/{semantic,"
        "knowledge-architecture,gk-ke}`、`specs/CONTRACT_INDEX.yaml`、`apps/api`（本体端口/规划器相关）、"
        "KERT `src/kert` 与 `examples/bank-front-knowledge-maps/90_control`）。")
    add("- **弱信号 ⇒ 同名候选**：只出现**裸术语名**（class/object property/data property）且位于 "
        "DTO/UI/测试/日志/持久化面；**必须**有同名机械证明 —— H1 库列 `snake_case` 形态 / "
        "H2 按简单名从 `dto|contract|api|model` 包导入该术语（且同文件**无**本体/领域包同名或通配导入 ⇒ "
        "命名解析唯一）/ H3 前端 `import type { X } from '.../api/...'`；无证明一律降级为待回源。")
    add("- **中信号 ⇒ 待回源**：其余（`specs/*` 其余、`scripts/*`、`scenario/*`、KERT `examples|skills` 其余）。")
    add("")
    add("### 2.1 口径声明（**请 TL 重点审计**）")
    add("")
    for item in summary["interpretations"]:
        add(f"- {item}")
    add("")
    add("> 替代口径计数：若按「tier=WEAK 即判同名」，则同名 = "
        f"{summary['alternatives']['homonym_if_tier_only']}、待回源 = "
        f"{summary['alternatives']['needs_if_tier_only']}。本 CSV 采用更保守的『需机械证明』口径。")
    add("")
    add("## 3. 真义务清单（按责任 Wave 归类）")
    add("")
    add("逐文件完整清单见 `obligation-triage.csv`（`disposition=TRUE_OBLIGATION`）。先看**依据强度**"
        "（回源抽检应优先抽「仅路径依据」那一档）：")
    add("")
    st = summary["true_evidence_strength"]
    add(_md_table(["依据强度", "行数", "含义"], [
        ["内容级证据（IRI/OWL/SPARQL/planHash…）", st["content_evidence"]["total"],
         st["content_evidence"]["note"]],
        ["仅路径依据（已确认消费面）", st["path_evidence_only"]["total"],
         st["path_evidence_only"]["note"]],
    ]))
    add("")
    add("真义务按信号规则分布：")
    add("")
    add(_md_table(["信号规则", "行数"],
                  [[f"`{k}`", v] for k, v in st["by_rule"].items()]))
    add("")
    add("下表为 Wave × 目录聚合。")
    add("")
    for wave, info in summary["true_by_wave"].items():
        add(f"### {wave}（{phase_label(wave)}）— {info['total']} 行")
        add("")
        add(_md_table(["目录（前 3 段）", "行数"],
                      [[d, n] for d, n in info["dirs_sorted"][:15]]))
        add("")
    add("## 4. 同名候选（全部列出，附机械证明与回源证据）")
    add("")
    if summary["homonym_rows"]:
        add(_md_table(["证明", "证据（`文件:行`）", "路径"],
                      [[h["proof"], f"`{h['evidence']}`", f"`{h['path']}`"]
                       for h in summary["homonym_rows"]]))
    else:
        add("本轮**无**满足机械证明的同名候选行。")
        add("")
        add("这不是「没有同名」，而是「**没有一条弱面命中能达到可证明的唯一解析**」：WI-A2 扫描已把"
            "可判同名的 2690 处路由到 `HOMONYM_REQUIRES_SOURCE_CHECK`（未进入净义务 1052 行）；"
            "净义务里剩下的弱面命中（本仓惯用测试/DTO 面）大多与本体包**同文件共存**，"
            "例如 `apps/api/src/test/.../HumanGateControllerTest.java:8` 同时 `import "
            "com.gien.gits.ontology.*;`，裸名解析不唯一 ⇒ 只能落待回源。")
    add("")
    add("**同名候选 ≠ 已排除**：它们只是「不计入迁移义务」，Wave 2 逐条回源仍可推翻。")
    add("")
    add("## 5. 待回源项与处置建议")
    add("")
    p0 = summary["needs_priority"]["P0_ONTOLOGY_PKG_COUPLED"]
    add(f"待回源共 {rec['needs_source_check']} 行，按「回源只需一步确认」程度再分两档：")
    add("")
    add(_md_table(["优先级档", "行数", "含义"], [
        ["**P0** 裸名精确解析到本体/领域模型包", p0["total"],
         "`import <本体/领域包>.<Term>;` 精确命中（Java 模型层耦合）⇒ 只需确认该类是否随四层拆分改名/换 IRI"],
        ["**P1** 其余待回源", summary["needs_priority"]["P1_OTHER_NEEDS"]["total"],
         "无本体包解析证据、也无同名证明 ⇒ 需逐条读判用法"],
    ]))
    add("")
    add("> **P0 是优先级信号，不是判定**：本引擎刻意不据此直接判 `TRUE_OBLIGATION`"
        "（派工单强信号清单未含此形态；是否升级由 TL 裁定）。P0 行按包分布：")
    add("")
    add(_md_table(["本体/领域模型包", "行数"],
                  [[f"`{k}`", v] for k, v in list(p0["by_package"].items())[:10]] or [["—", 0]]))
    add("")
    add("P0 样例（回源起点）：")
    add("")
    add(_md_table(["证据（`文件:行`）"],
                  [[f"`{s['evidence']}`"] for s in p0["samples"][:6]] or [["—"]]))
    add("")
    add("待回源行按目录分布（全量，前 20）：")
    add("")
    add(_md_table(["目录（前 3 段）", "待回源行数"],
                  [[d, n] for d, n in list(summary["needs_by_directory"].items())[:20]]))
    add("")
    add("处置建议（**次序 = 回源 ROI**）：")
    add("")
    add("1. **P0 行（本体包耦合）**：先回源这一档，多数只需确认 `com.gien.gits.ontology.*` 的 Java 模型类"
        "是否随四层拆分改名/换 IRI ⇒ 可批量定论（这批是本轮最有信息量的发现）。")
    add("2. `apps/api/src` 其余非本体端口文件（控制器/DTO/service）：逐条读判该术语是「本体类/属性消费」"
        "还是「Java 领域模型同名」；判据同 WI-A2 报告 §4 抽样 2（类型来源是 API 合同还是本体）。")
    add("3. `scripts/*`：门禁/生成器脚本内的术语多为**字面量断言**，按「是否驱动受控制品」逐条判定。")
    add("4. `specs/*` 其余（`openapi`/`data`/`product-recommendation`/`actions`/`evidence`）：按合同登记"
        "关系判定（是否将被本体拆分引用的 schema/字段）。")
    add("5. KERT `examples/*`、`skills/*`：按 L2 元模型消费面判定（需 KERT 侧回源，`INDEX_STALE(144)`）。")
    add("")
    add("## 6. 门禁与变异复验")
    add("")
    add("- 门禁：`python3 scripts/onto1_obligation_triage.py --gate`（G1 输入锚定/ G2 对账闭合/ "
        "G3 强信号面 100% 有判定 / G4 证据可回源 / G5 弱面反一刀切 / G6 Wave 合法性 / "
        "G7 产物与复算一致 / G8 无占位）。")
    add("- 变异复验：`--selftest` M0 对照 / M1 强信号注入必须检出 / M2 弱面真义务（无证据与有证据）必须 FAIL / "
        "M3 删强信号判定必须 FAIL / M4 真值函数短路必须 FAIL / M5 输入缺失必须 FAIL / "
        "M6 证据不可回源必须 FAIL / M8 本体包通配导入存在时禁判同名 / "
        "**M9 本体包耦合 ⇒ 升格真义务(W3) + 机械证据双标签** / "
        "**M9b-1 开关回退 ⇒ 回落 NEEDS（回退有效）/ M9b-2 剥掉 `PROOF:IMPORT_LINE` ⇒ 弱面 G5 必须 FAIL / "
        "M9b-3 全部 P0 行包名改为不存在 ⇒ 逐行 G5 命中数须 == 行数（覆盖全 tier）**（D-12 反例）。"
        "逐条输出见 HANDOFF 与 TL 记账日志。")
    add("")
    add("## 7. 诚实声明（**不得援引为已完成的事**）")
    add("")
    add("1. 本报告**不声称**消费者影响分析已关闭：它把 1052 行压到三层，**待回源的 "
        f"{rec['needs_source_check']} 行仍未确认**，既不能当义务执行、也不得算已排除；")
    add("2. `TRUE_OBLIGATION` 是「必须跟随迁移」的**判定**，不是「已确认本体消费」的**结论**"
        "（Wave 2 回源可推翻，尤其强路径面内的裸术语命中）；")
    add("3. 弱信号面的同名判定是**候选**：证明只到「该名在此文件解析到 API 合同/库列」这一层，"
        "不等于该文件与本体毫无关系；本轮该档为 0 行，"
        "**不等于**「净义务里没有同名」——只是没有一条达到可证明的唯一解析（详见 §4）；")
    add("4. 第 5 节的 P0/P1 是**回源优先级**，不是判定；P0（65 行）是否升级为真义务 **由 TL 裁定**，"
        "本引擎不自行升格（口径 I-6）；")
    add("5. 本报告**未**执行 `make generate`、**未**改 `specs/**`/`generated/**`/`docs/dd/**`、"
        "**未**写 KERT 仓、**未**签任何门禁（登记由 TL 执行）；")
    add("6. KERT 侧结论一律回源到 `文件:行`（`INDEX_STALE(144)`，不得据索引外推）。")
    add("7. `TRUE_OBLIGATION` 里只有内容级证据那一档（"
        f"{st['content_evidence']['total']} 行）是「文件正文自证」；其余 "
        f"{st['path_evidence_only']['total']} 行依据是路径规则，Wave 2 应优先抽检。")
    add("")
    if rec["true_obligation"] > 400:
        add("> **风险提示**：真义务 "
            f"{rec['true_obligation']} 行 > `PLAN-NEXT.md` §1 A1 的 400 行阈值 ⇒ 触发"
            "「立即回写 `evidence/WBS-RESTIMATE.md` 并在 `ORCHESTRATOR.md §5` 新增风险项」条款"
            "（本文件写域外，建议由 TL 执行）。")
        add("")
    add("## 8. 与 WI-A2 扫描报告的关系")
    add("")
    add(f"- 输入锚点：`{BASELINE_SCAN_REPORT}` §3（1038 FOLLOW_MIGRATION + 14 CONTROL_PLANE_REQUIRED）；")
    add("- 本报告不替代 §3 清单，而是给它加**第三维（判定 + 证据）**；扫描报告的 §4 诚实性声明继续有效；")
    add("- 扫描报告 §4 已完成 3 类抽样证伪（`customerId` 库列 / 前端 `Customer` DTO / `AC-004` 号段）；"
        "本轮把前两类**机器化为全量规则**（H1 库列 snake_case / H3 前端 SDK 类型导入），"
        "实测**在 1052 行净义务内零命中** —— 因为这三类命中在扫描阶段已被路由到 "
        "`HOMONYM_REQUIRES_SOURCE_CHECK`（2690 处）与 `EXEMPT_NON_ONTOLOGY_HOMONYM`，**未进入净义务**。"
        "这反过来解释了「同名候选 = 0」：净义务集合的构成本身已不含可机械证明的同名形态。")
    add("")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# 产出
# --------------------------------------------------------------------------- #
def report(obligations_csv: Path = OBLIGATIONS_CSV, hits_jsonl: Path = HITS_JSONL,
           repo_roots: dict[str, Path] | None = None, baseline_rows: int = BASELINE_ROWS,
           expected_input_dispositions: dict[str, int] | None = None,
           out_csv: Path = OUT_CSV, out_summary: Path = OUT_SUMMARY, out_report: Path = OUT_REPORT,
           strict_weak_surface: bool = False, verbose: bool = True) -> int:
    repo_roots = repo_roots or DEFAULT_REPO_ROOTS
    expected_input_dispositions = expected_input_dispositions or BASELINE_INPUT_DISPOSITIONS
    try:
        entries = load_obligation_rows(obligations_csv)
        hits = load_hits(hits_jsonl)
        ctx = SourceCache(repo_roots)
        rows, meta = triage(entries, hits, ctx, strict_weak_surface=strict_weak_surface)
    except InputError as exc:
        print(f"onto1-obligation-triage: FAIL: {exc}", file=sys.stderr)
        return 2

    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=OUTPUT_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    csv_sha = hashlib.sha256(out_csv.read_bytes()).hexdigest()

    rec = reconcile(rows, baseline_rows)
    summary = build_summary(rows, entries, hits, meta, rec, baseline_rows,
                            expected_input_dispositions, obligations_csv, hits_jsonl, out_csv,
                            strict_weak_surface)
    summary["outputs"] = {"csv": out_csv.name, "csv_sha256": csv_sha,
                          "report": out_report.name}
    out_summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8")
    out_report.write_text(render_report(summary), encoding="utf-8")

    if verbose:
        print(f"[report] rows={len(rows)} true={rec['true_obligation']} "
              f"homonym={rec['homonym_candidate']} needs={rec['needs_source_check']} "
              f"sum={rec['sum']} closed={rec['closed']}")
        print(f"[report] csv={out_csv} sha256={csv_sha[:16]}")
        print(f"[report] summary={out_summary}")
        print(f"[report] report={out_report}")
    return 0


def gate(obligations_csv: Path = OBLIGATIONS_CSV, hits_jsonl: Path = HITS_JSONL,
         repo_roots: dict[str, Path] | None = None, baseline_rows: int = BASELINE_ROWS,
         expected_input_dispositions: dict[str, int] | None = None,
         out_csv: Path = OUT_CSV, out_summary: Path = OUT_SUMMARY,
         strict_weak_surface: bool = False, verbose: bool = True) -> int:
    repo_roots = repo_roots or DEFAULT_REPO_ROOTS
    expected_input_dispositions = expected_input_dispositions or BASELINE_INPUT_DISPOSITIONS
    failures = run_checks(obligations_csv, hits_jsonl, repo_roots, baseline_rows,
                          expected_input_dispositions, out_csv, out_summary,
                          strict_weak_surface=strict_weak_surface)
    if failures:
        for item in failures:
            print(f"onto1-obligation-triage: FAIL: {item}", file=sys.stderr)
        print(f"onto1-obligation-triage: FAIL ({len(failures)} finding(s))", file=sys.stderr)
        return 2
    if verbose:
        print("onto1-obligation-triage: PASS (G1 输入锚定 / G2 对账闭合 / G3 强面判定 / "
              "G4 证据可回源 / G5 弱面反一刀切 / G6 Wave 合法 / G7 产物一致 / G8 无占位)")
    return 0


# --------------------------------------------------------------------------- #
# 变异复验（M0~M6）
# --------------------------------------------------------------------------- #
def selftest() -> int:
    """M0 对照 PASS / M1 强信号注入必须被检出 / M2 弱面判真义务（无证据 & 有证据）必须 FAIL /
    M3 删强信号判定必须 FAIL / M4 真值函数短路必须 FAIL / M5 输入缺失必须 FAIL /
    M6 证据不可回源必须 FAIL。全部符合预期 ⇒ exit 0。"""
    tmp = Path(tempfile.mkdtemp(prefix="onto1-a1-selftest-"))
    results: list[tuple[str, bool, str]] = []
    try:
        root = tmp / "repos"
        gits = root / "gits"
        fixture_files = {
            "specs/gk-ke/v1/contract.ttl": (
                "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
                "<https://gientech.com/gits/kno/Claim> a owl:Class .\n"
            ),
            "specs/gk-ke/v1/README.md": "# gk-ke v1\n\nClaim 是 L1 语义对象（本文件故意不含 IRI 字面量，用于验证路径级强信号）。\n",
            "scripts/tool.py": "import json\nclaim_name = 'Claim'\nClaim = 1\n",
            "apps/api/src/main/java/x/dto/MapDto.java": (
                "package x.dto;\n"
                "import com.gien.gits.contract.Claim;\n"
                "/** 合同类型，非本体类。 */\n"
                "public record MapDto(String customerId, Claim claim) {}\n"
            ),
            "apps/api/src/main/java/x/dto/WildcardImportDto.java": (
                "package x.dto;\n"
                "import com.gien.gits.ontology.*;\n"
                "import com.gien.gits.contract.Claim;\n"
                "/** 本体包通配导入存在 ⇒ 裸名 Claim 解析不唯一 ⇒ 禁判同名（M8）。 */\n"
                "public record WildcardImportDto(Claim claim) {}\n"
            ),
            "apps/api/src/main/java/x/dto/CustomerModelDto.java": (
                "package x.dto;\n"
                "import com.gien.gits.ontology.Customer;\n"
                "/** 本体模型类耦合（回源优先级 P0，M9）。 */\n"
                "public record CustomerModelDto(Customer customer) {}\n"
            ),
            "apps/api/src/main/java/x/dto/OntologyAwareDto.java": (
                "package x.dto;\n"
                "// 本体 IRI: https://gientech.com/gits/kno/Task\n"
                "public record OntologyAwareDto(String id) {}\n"
            ),
            "apps/api/src/main/java/x/Plain.java": (
                "package x;\npublic class Plain { String claim = \"Claim\"; }\n"
            ),
        }
        for rel, body in fixture_files.items():
            p = gits / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(body, encoding="utf-8")

        fixture_rows = [
            # 强（路径 + 内容）
            dict(repo="gits", disposition="FOLLOW_MIGRATION", category="owl_class",
                 path="specs/gk-ke/v1/contract.ttl", rule_id="R-T", tokens="Claim", lines="2",
                 action="合同/映射/实例随迁移更新（合同先行）"),
            # 中（scripts 裸术语）
            dict(repo="gits", disposition="FOLLOW_MIGRATION", category="owl_class",
                 path="scripts/tool.py", rule_id="R-T", tokens="Claim", lines="3",
                 action="门禁脚本随术语迁移（含新门禁 onto_split_test.py）"),
            # 弱 + H2 机械证明 ⇒ 同名候选
            dict(repo="gits", disposition="FOLLOW_MIGRATION", category="owl_class",
                 path="apps/api/src/main/java/x/dto/MapDto.java", rule_id="R-T", tokens="Claim",
                 lines="3", action="应用装配层随本体/合同迁移"),
            # 弱 + 无证明 ⇒ 待回源（M2 变异目标）
            dict(repo="gits", disposition="FOLLOW_MIGRATION", category="owl_datatype_property",
                 path="apps/api/src/main/java/x/dto/MapDto.java", rule_id="R-T", tokens="customerId",
                 lines="4", action="应用装配层随本体/合同迁移"),
            # apps/api 非端口面 ⇒ 中
            dict(repo="gits", disposition="FOLLOW_MIGRATION", category="owl_class",
                 path="apps/api/src/main/java/x/Plain.java", rule_id="R-T", tokens="Claim", lines="2",
                 action="应用装配层随本体/合同迁移"),
            # M1：弱面目录（/dto/）内注入本体 IRI ⇒ 必须判强
            dict(repo="gits", disposition="FOLLOW_MIGRATION", category="owl_class",
                 path="apps/api/src/main/java/x/dto/OntologyAwareDto.java", rule_id="R-T",
                 tokens="Task", lines="2", action="应用装配层随本体/合同迁移"),
            # 路径级强信号（无强内容）：specs/gk-ke 下的裸术语命中 ⇒ G3 路径面断言有牙齿
            dict(repo="gits", disposition="FOLLOW_MIGRATION", category="owl_class",
                 path="specs/gk-ke/v1/README.md", rule_id="R-T", tokens="Claim", lines="3",
                 action="合同/映射/实例随迁移更新（合同先行）"),
            # M9：裸名精确解析到本体模型包 ⇒ **TL 裁定 I-6 升格真义务**（P0，证据=导入行）
            #     **刻意放在 M8 之前**：使 P0 行**不落在 `target` 末位**，从而让 M9b-3 能抓住
            #     "断言缩进出循环、只判末元素"这类死代码（QA 第三轮 BLOCKER 的同族回归防护）。
            dict(repo="gits", disposition="FOLLOW_MIGRATION", category="owl_class",
                 path="apps/api/src/main/java/x/dto/CustomerModelDto.java", rule_id="R-T",
                 tokens="Customer", lines="2", action="应用装配层随本体/合同迁移"),
            # M8：弱面 + 合同类型导入，但同文件存在本体包通配导入 ⇒ 命名解析不唯一 ⇒ 禁判同名
            dict(repo="gits", disposition="FOLLOW_MIGRATION", category="owl_class",
                 path="apps/api/src/main/java/x/dto/WildcardImportDto.java", rule_id="R-T",
                 tokens="Claim", lines="4", action="应用装配层随本体/合同迁移"),
        ]
        csv_path = tmp / "obligations.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=INPUT_COLUMNS, lineterminator="\n")
            w.writeheader()
            w.writerows(fixture_rows)
        hits_path = tmp / "hits.jsonl"
        with hits_path.open("w", encoding="utf-8") as fh:
            for r in fixture_rows:
                for tok in r["tokens"].split(";"):
                    fh.write(json.dumps({"repo": r["repo"], "path": r["path"], "line": 2,
                                         "category": r["category"], "token": tok,
                                         "disposition": r["disposition"]}) + "\n")
        out_csv = tmp / "triage.csv"
        out_summary = tmp / "triage-summary.json"
        repo_roots = {"gits": gits, "kert": root / "kert"}
        expected = {"FOLLOW_MIGRATION": len(fixture_rows)}
        args = dict(obligations_csv=csv_path, hits_jsonl=hits_path, repo_roots=repo_roots,
                    baseline_rows=len(fixture_rows), expected_input_dispositions=expected,
                    out_csv=out_csv, out_summary=out_summary)

        def snapshot_csv() -> str:
            return out_csv.read_text(encoding="utf-8")

        def rewrite_csv(rows: list[dict]) -> None:
            with out_csv.open("w", newline="", encoding="utf-8") as fh:
                w = csv.DictWriter(fh, fieldnames=OUTPUT_COLUMNS, lineterminator="\n")
                w.writeheader()
                w.writerows(rows)

        def read_csv() -> list[dict]:
            with out_csv.open(newline="", encoding="utf-8") as fh:
                return [dict(r) for r in csv.DictReader(fh)]

        def failures_of() -> list[str]:
            return run_checks(**args)

        # ---- M0 对照 ----
        rc = report(out_report=tmp / "report.md", verbose=False, **args)
        m0_failures = failures_of()
        results.append(("M0 对照（正式规则 + 正式夹具）", rc == 0 and not m0_failures,
                        f"report_exit={rc} failures={m0_failures[:2]}"))

        # ---- M1 强信号注入必须被检出（不是"跑完就算"）----
        try:
            entries = load_obligation_rows(csv_path)
            hits = load_hits(hits_path)
            ctx = SourceCache(repo_roots)
            rows, _ = triage(entries, hits, ctx)
            inj = [r for r in rows if r["path"].endswith("OntologyAwareDto.java")]
            ok = bool(inj) and inj[0]["tier"] == TIER_STRONG and inj[0]["disposition"] == DISPO_TRUE \
                and inj[0]["signal"].startswith("STRONG_CONTENT:IRI_GIENTECH")
            results.append(("M1 弱面注入本体 IRI ⇒ 必须判强信号", ok,
                            inj[0]["signal"] if inj else "row not found"))
        except InputError as exc:
            results.append(("M1 弱面注入本体 IRI ⇒ 必须判强信号", False, f"InputError {exc}"))

        # ---- M2a 弱面判真义务且无证据 ⇒ FAIL ----
        pristine = read_csv()
        tampered = [dict(r) for r in pristine]
        for r in tampered:
            if r["path"].endswith("MapDto.java") and r["disposition"] == DISPO_HOMONYM:
                r["disposition"] = DISPO_TRUE
                r["evidence"] = ""
        rewrite_csv(tampered)
        f2a = failures_of()
        results.append(("M2a 弱面判真义务且无证据 ⇒ FAIL",
                        any("G4" in x or "G5" in x for x in f2a), f"{len(f2a)} finding(s)"))

        # ---- M2b 弱面判真义务但**有**证据 ⇒ 仍必须 FAIL（防"补个证据就放行"）----
        tampered2 = [dict(r) for r in pristine]
        for r in tampered2:
            if r["path"].endswith("MapDto.java") and r["disposition"] == DISPO_NEEDS:
                r["disposition"] = DISPO_TRUE
                r["responsible_wave"] = WAVE_W3
        rewrite_csv(tampered2)
        f2b = failures_of()
        results.append(("M2b 弱面判真义务（证据齐全）⇒ 仍 FAIL",
                        any("G5" in x for x in f2b), f"{len(f2b)} finding(s)"))

        # ---- M3 删掉一条强信号判定 ⇒ FAIL ----
        tampered3 = [r for r in pristine
                     if not (r["tier"] == TIER_STRONG and r["disposition"] == DISPO_TRUE)]
        rewrite_csv(tampered3)
        f3 = failures_of()
        results.append(("M3 删掉强信号判定 ⇒ FAIL", any("G2" in x or "G7" in x for x in f3),
                        f"{len(f3)} finding(s)"))

        # ---- M6 证据不可回源（行号越界/该行无 token）⇒ FAIL ----
        tampered4 = [dict(r) for r in pristine]
        for r in tampered4:
            if r["tier"] == TIER_STRONG and r["disposition"] == DISPO_TRUE:
                r["evidence"] = r["evidence"].rsplit(":", 1)[0] + ":999"
                break
        rewrite_csv(tampered4)
        f6 = failures_of()
        results.append(("M6 证据不可回源 ⇒ FAIL", any("G4" in x for x in f6), f"{len(f6)} finding(s)"))

        # ---- M8 同名证明被本体包导入阻断（防"看到 DTO 导入就判同名"一刀切）----
        try:
            entries8 = load_obligation_rows(csv_path)
            hits8 = load_hits(hits_path)
            rows8, _ = triage(entries8, hits8, SourceCache(repo_roots))
            wild = [r for r in rows8 if r["path"].endswith("WildcardImportDto.java")]
            results.append(("M8 同文件有本体包通配导入 ⇒ 禁判同名（落待回源）",
                            bool(wild) and wild[0]["disposition"] == DISPO_NEEDS,
                            wild[0]["disposition"] if wild else "row not found"))
        except InputError as exc:
            results.append(("M8 同文件有本体包通配导入 ⇒ 禁判同名（落待回源）", False,
                            f"InputError {exc}"))

        # ---- M9 本体包耦合 ⇒ **TL 裁定 I-6 升格为真义务**（可复核：证据=导入行 + 双标签）----
        try:
            entries9 = load_obligation_rows(csv_path)
            hits9 = load_hits(hits_path)
            rows9, _ = triage(entries9, hits9, SourceCache(repo_roots))
            model = [r for r in rows9 if r["path"].endswith("CustomerModelDto.java")]
            ok9 = (bool(model)
                   and model[0]["disposition"] == DISPO_TRUE
                   and model[0]["responsible_wave"] == WAVE_W3
                   and P0_IMPORT_PROOF in model[0]["signal"]
                   and "RESOLVES_TO_ONTOLOGY_PKG:com.gien.gits.ontology" in model[0]["signal"]
                   and model[0]["evidence"].endswith(":2"))
            results.append(("M9 裸名精确解析到本体包 ⇒ 升格真义务(W3) + 机械证据双标签", ok9,
                            model[0]["signal"] if model else "row not found"))
        except InputError as exc:
            results.append(("M9 裸名精确解析到本体包 ⇒ 升格真义务(W3) + 机械证据双标签", False,
                            f"InputError {exc}"))

        # ---- M9b **反例（D-12，本升格是"放宽"⇒ 必须自带反例）** ----
        # (1) 回退口径有效：开关置 False ⇒ 同一行回落 NEEDS + P0 标签（证明"一键回退"非空话）；
        # (2) 剥掉机械证据 ⇒ G5 必须 FAIL（证明 G5 例外是**条件性**的，不是"弱面判 TRUE 一律放行"）。
        try:
            globals()["RULING_I6_UPGRADE_P0"] = False
            rows9r, _ = triage(load_obligation_rows(csv_path), load_hits(hits_path),
                               SourceCache(repo_roots))
            model_r = [r for r in rows9r if r["path"].endswith("CustomerModelDto.java")]
            ok_rollback = (bool(model_r) and model_r[0]["disposition"] == DISPO_NEEDS
                           and "RESOLVES_TO_ONTOLOGY_PKG:com.gien.gits.ontology" in model_r[0]["signal"])
            results.append(("M9b-1 开关回退 ⇒ 回落 NEEDS + P0 标签（回退有效）", ok_rollback,
                            f"{model_r[0]['disposition']} / {model_r[0]['signal']}" if model_r else "not found"))
        except InputError as exc:
            results.append(("M9b-1 开关回退 ⇒ 回落 NEEDS + P0 标签（回退有效）", False, f"InputError {exc}"))
        finally:
            globals()["RULING_I6_UPGRADE_P0"] = True

        try:
            stripped = [dict(r) for r in pristine]
            hit = False
            for r in stripped:
                if P0_IMPORT_PROOF in str(r.get("signal", "")):
                    r["signal"] = str(r["signal"]).replace(P0_IMPORT_PROOF + "|", "")
                    hit = True
            rewrite_csv(stripped)
            f9b = failures_of()
            results.append((f"M9b-2 剥掉 PROOF:IMPORT_LINE ⇒ 弱面 G5 必须 FAIL（仅覆盖 WEAK 半边）",
                            hit and any("G5" in x for x in f9b), f"{len(f9b)} finding(s)"))
        except InputError as exc:
            results.append((f"M9b-2 剥掉 PROOF:IMPORT_LINE ⇒ 弱面 G5 必须 FAIL（仅覆盖 WEAK 半边）",
                            False, f"InputError {exc}"))

        # ---- M9b-3 **反例（抓"缩进出循环/只判末元素"这类死代码）** ----
        # 把**全部** P0 行的包名改成不存在的包 ⇒ 逐行标签校验必须**逐条**命中，命中数 == 被改行数。
        # 这条断言正是 QA 第三轮用来实证"本检查空转"的变异；它必须进回归集，防止再次退化。
        try:
            bogus = [dict(r) for r in pristine]
            touched = 0
            for r in bogus:
                sig = str(r.get("signal", ""))
                if "RESOLVES_TO_ONTOLOGY_PKG:" not in sig:
                    continue
                head, _, rest = sig.partition("RESOLVES_TO_ONTOLOGY_PKG:")
                old_pkg = rest.split("|", 1)[0]
                r["signal"] = (head + "RESOLVES_TO_ONTOLOGY_PKG:com.bogus.pkg"
                               + rest[len(old_pkg):])
                touched += 1
            rewrite_csv(bogus)
            f9c = failures_of()
            hits = sum(1 for x in f9c if "ontology-pkg resolve label without import evidence" in x)
            results.append(("M9b-3 全部 P0 行包名改为不存在 ⇒ 逐行 G5 命中数须 == 行数（覆盖全 tier）",
                            touched > 0 and hits == touched,
                            f"touched={touched} G5hits={hits}"))
        except InputError as exc:
            results.append(("M9b-3 全部 P0 行包名改为不存在 ⇒ 逐行 G5 命中数须 == 行数（覆盖全 tier）",
                            False, f"InputError {exc}"))

        # ---- M9c **前置断言（QA 第四轮 N-8）** ----
        # M9b-3 的区分度**依赖夹具行序**：若 P0 行被移回末位，在"断言缩进出循环"这类死代码下
        # M9b-3 会**重新通过**（末元素恰好是 P0 行）。故把该前提显式钉死，并把"移到末位"作为元变异判据。
        try:
            p0_idx = [i for i, r in enumerate(fixture_rows)
                      if r["path"].endswith("CustomerModelDto.java")]
            ok9c = bool(p0_idx) and p0_idx[0] < len(fixture_rows) - 1
            results.append(("M9c 前置：P0 夹具行**不落在末位**（M9b-3 区分度的前提）", ok9c,
                            f"p0_index={p0_idx} total={len(fixture_rows)}"))
        except Exception as exc:  # noqa: BLE001 —— 前置断言自身失败亦须如实记为不符预期
            results.append(("M9c 前置：P0 夹具行**不落在末位**（M9b-3 区分度的前提）", False, repr(exc)))

        # ---- M4 真值函数被短路（返回常量）⇒ FAIL ----
        restore = globals()["triage_row"]

        def short_circuit(entry, ctx, strict_weak_surface=False):  # type: ignore[no-untyped-def]
            return {"repo": entry["repo"], "path": entry["path"], "tier": TIER_MEDIUM,
                    "signal": MEDIUM_SIGNAL_FALLBACK, "disposition": DISPO_NEEDS,
                    "rationale": SHORT_CIRCUIT_RATIONALE, "evidence": "",
                    "responsible_wave": WAVE_PENDING}

        try:
            globals()["triage_row"] = short_circuit
            rewrite_csv(pristine)  # 恢复磁盘 CSV（由未短路的真值函数产出）
            f4 = failures_of()
        finally:
            globals()["triage_row"] = restore
        results.append(("M4 真值函数被短路（返回常量）⇒ FAIL", any("G3" in x for x in f4),
                        f"{len(f4)} finding(s)"))

        # ---- M5 输入缺失 ⇒ FAIL（fail-closed）----
        rewrite_csv(pristine)
        missing_args = dict(args)
        missing_args["obligations_csv"] = tmp / "nope.csv"
        f5 = run_checks(**missing_args)
        results.append(("M5 输入缺失 ⇒ FAIL（fail-closed）", any("G1" in x for x in f5),
                        f"{len(f5)} finding(s)"))

        # ---- 恢复并复核对照仍 PASS ----
        rewrite_csv(pristine)
        f_restore = failures_of()
        results.append(("M7 恢复后对照 ⇒ PASS（证明变异有效且可回退）", not f_restore,
                        f"{len(f_restore)} finding(s)"))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    ok = True
    for name, passed, detail in results:
        print(f"[selftest] {'PASS' if passed else 'FAIL'}  {name}  ({detail})")
        ok = ok and passed
    print(f"[selftest] {sum(1 for _, p, _ in results if p)}/{len(results)} 用例符合预期")
    return 0 if ok else 2


# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ONTO1 候选义务三层判定引擎（WI-A2 §4）")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--report", action="store_true", help="生成 CSV + 摘要 + 报告")
    group.add_argument("--gate", action="store_true", help="门禁 G1~G8（exit 0/2）")
    group.add_argument("--selftest", action="store_true", help="变异复验 M0~M9（exit 0/2）")
    parser.add_argument("--strict-weak-surface", action="store_true",
                        help="弱信号面只用派工单列举的前缀（不并入 src/test、dto）")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    if args.gate:
        return gate(strict_weak_surface=args.strict_weak_surface)
    return report(strict_weak_surface=args.strict_weak_surface)


if __name__ == "__main__":
    sys.exit(main())
