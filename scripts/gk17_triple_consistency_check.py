#!/usr/bin/env python3
"""GK17 WP5.2 三处一致性门禁（地图 / 本体 / 投影）（判据 V4）。

依据
----
`docs/architecture/GK17-WP1.3-产品关系权威归属裁定-V1.0.md`：
  · **关系类型**的权威 = **本体**（谓词语义）
  · **关系实例**的权威 = **产品卡**（单向投影 产品卡 → 本体个体）
  ⇒ **本体里出现产品关系实例 = 越权写，必须检出**（判据 V4）。
  裁定 §4 明示：若 V4 检不出 ⇒ 裁定未被机械保障。

检测项（四项，全部 fail-closed）
--------------------------------
  [D1] 本体承载关系实例（违反 WP1.3 裁定）
       `gits:requiresProduct` / `gits:mutuallyExclusiveWith` / `gits:complementsProduct`
       只允许作为 T-Box 声明（`a owl:ObjectProperty`）存在；
       一旦出现在**个体三元组**（谓词被当数据用）⇒ FAIL。
  [D2] 投影个体类型不是本体类
       投影里 `a gits:Xxx`，而 `gits:Xxx` 不在本体类集合中 ⇒ FAIL。
  [D3] 地图引用的域地图文件不存在
       `domains[].mapRef` 指向的文件不存在 ⇒ FAIL。
  [D4] 投影个体悬空引用
       投影里对象（object）指向一个不存在的个体 ⇒ FAIL。

设计约束（本仓硬约束）
----------------------
  · 纯 stdlib / Python 3 / fail-closed；逐条不一致项**含文件路径与行号**；
  · **自带变异负例**：对 D1 执行「临时往本体副本追加一条关系实例三元组 ⇒ 判定 FAIL；
    撤销 ⇒ PASS」，并打印变异前后对照；
  · 变异**只改临时副本**，原始本体文件**逐字节复原并自证**（sha256 对比）；
  · `--json` / `--root` / `--allow-empty-projection`。
  · **禁止空转**：断言不得依赖"夹具缺失即通过"。若某项因输入缺失而无法判定，
    必须显式记为 SKIPPED/FAIL，不得静默计为通过（本仓已有 6 个 Loop 首报全绿实为空转的前例）；
    变异自检若**未能捕获**变异，则本门禁判 FAIL（宁红不假绿）。

用法
----
  python3 scripts/gk17_triple_consistency_check.py
  python3 scripts/gk17_triple_consistency_check.py --json
  python3 scripts/gk17_triple_consistency_check.py --root /path/to/repo
  python3 scripts/gk17_triple_consistency_check.py --allow-empty-projection   # W3 未就绪时
  python3 scripts/gk17_triple_consistency_check.py --no-mutation-selftest

退出码：0 全部一致（且变异自检捕获成功）；1 检出不一致 / 变异未被捕获；2 输入缺失等不可判定。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

# ══════════════════════════════════════════════════════════════════════════════
# 常量：路径与受控谓词
# ══════════════════════════════════════════════════════════════════════════════

ONTOLOGY_REL = "specs/semantic/gits-core.owl.ttl"
MAPS_DIR_REL = "specs/knowledge-architecture/maps"
INSTANCES_DIR_REL = "specs/knowledge-architecture/instances"

# WP1.3 裁定点名的三个产品关系谓词：**只允许 T-Box 声明，不允许实例**
PRODUCT_RELATION_PREDICATES = (
    "requiresProduct",
    "mutuallyExclusiveWith",
    "complementsProduct",
)

# 非个体断言的谓词（用于判定"该三元组是不是 T-Box 声明"）
TBOX_MARKERS = {
    "type",
    "label",
    "comment",
    "seeAlso",
    "isDefinedBy",
    "subClassOf",
    "subPropertyOf",
    "domain",
    "range",
    "inverseOf",
    "equivalentClass",
    "equivalentProperty",
    "disjointWith",
    "unionOf",
    "intersectionOf",
    "complementOf",
    "onProperty",
    "allValuesFrom",
    "someValuesFrom",
    "minCardinality",
    "maxCardinality",
    "cardinality",
    "deprecated",
    "versionInfo",
    "priorVersion",
    "imports",
}

# Turtle 里不会被当成主语的开头关键字
TURTLE_KEYWORDS = {
    "a",
    "true",
    "false",
    "base",
    "prefix",
}

# 用于 --self-test 的内部状态
_SELF_TEST_NOTES: list[str] = []


class FailClosed(Exception):
    """输入缺失或无法判定 —— 不得静默计为通过。"""


# ══════════════════════════════════════════════════════════════════════════════
# 轻量 Turtle 解析（纯 stdlib；只覆盖本仓实际使用的子集）
# ══════════════════════════════════════════════════════════════════════════════

_IRI_RE = re.compile(r"<([^>]*)>")
_PREFIX_RE = re.compile(r"^@prefix\s+([A-Za-z][\w-]*)?:\s*<([^>]*)>\s*\.\s*$")
_BASE_RE = re.compile(r"^@base\s+<([^>]*)>\s*\.\s*$")
_COMMENT_OR_STRING = re.compile(r'("""(?:.|\n)*?"""|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\')')


def strip_comments(line: str) -> str:
    """去掉 Turtle 行内的 `#` 注释，但**不碰字符串字面量里的 `#`**。"""
    out: list[str] = []
    i = 0
    in_string: str | None = None
    while i < len(line):
        ch = line[i]
        if in_string:
            out.append(ch)
            if ch == "\\" and i + 1 < len(line):
                out.append(line[i + 1])
                i += 2
                continue
            if ch == in_string:
                in_string = None
            i += 1
            continue
        if ch in ('"', "'"):
            if line[i:i + 3] in ('"""', "'''"):
                in_string = line[i:i + 3]
                out.append(line[i:i + 3])
                i += 3
                continue
            in_string = ch
            out.append(ch)
            i += 1
            continue
        if ch == "#":
            break
        out.append(ch)
        i += 1
    return "".join(out)


def split_quoted(text: str) -> list[str]:
    """按空白切分，但保留字符串字面量与 `<...>` IRI 作为整体。"""
    tokens: list[str] = []
    buf = ""
    i = 0
    in_string: str | None = None
    in_iri = False
    while i < len(text):
        ch = text[i]
        if in_string:
            buf += ch
            if ch == "\\" and i + 1 < len(text):
                buf += text[i + 1]
                i += 2
                continue
            if ch == in_string:
                in_string = None
            i += 1
            continue
        if in_iri:
            buf += ch
            if ch == ">":
                in_iri = False
            i += 1
            continue
        if ch.isspace():
            if buf:
                tokens.append(buf)
                buf = ""
            i += 1
            continue
        if ch in ('"', "'"):
            if text[i:i + 3] in ('"""', "'''"):
                in_string = text[i:i + 3]
                buf += text[i:i + 3]
                i += 3
                continue
            in_string = ch
            buf += ch
            i += 1
            continue
        if ch == "<":
            in_iri = True
            buf += ch
            i += 1
            continue
        buf += ch
        i += 1
    if buf:
        tokens.append(buf)
    return tokens


class Statement:
    """一条语句（一个主语的全部谓词-宾语对），带真实行号。"""

    __slots__ = ("subject", "pairs", "line", "custom_datatype")

    def __init__(self, subject: str, line: int):
        self.subject = subject
        self.pairs: list[tuple[str, str, int]] = []
        self.line = line
        self.custom_datatype = False


class TurtleDoc:
    """解析结果：前缀表 + 语句列表 + 已知个体。"""

    def __init__(self) -> None:
        self.prefixes: dict[str, str] = {}
        self.base: str | None = None
        self.statements: list[Statement] = []
        self.individuals: set[str] = set()

    # —— 类型 / 属性视角 ——
    def classes(self) -> set[str]:
        return {
            t
            for st in self.statements
            if st.subject
            for (p, o, _ln) in st.pairs
            if p == "type" and o.startswith("gits:")
        }

    def object_properties(self) -> set[str]:
        return {
            st.subject
            for st in self.statements
            if any(p == "type" and o == "owl:ObjectProperty" for (p, o, _ln) in st.pairs)
        }

    def datatype_properties(self) -> set[str]:
        return {
            st.subject
            for st in self.statements
            if any(p == "type" and o == "owl:DatatypeProperty" for (p, o, _ln) in st.pairs)
        }

    def declared_predicates(self) -> set[str]:
        """被声明为属性（对象/数据类型/注释）的谓词名（`gits:` 局部名）。"""
        names: set[str] = set()
        for st in self.statements:
            for (p, o, _ln) in st.pairs:
                if p == "type" and o in (
                    "owl:ObjectProperty",
                    "owl:DatatypeProperty",
                    "owl:AnnotationProperty",
                ):
                    if st.subject.startswith("gits:"):
                        names.add(st.subject.split(":", 1)[1])
        return names

    def is_tbox_statement(self, st: Statement) -> bool:
        """该语句是否是一条 T-Box 声明（而非个体断言）？"""
        if any(p == "type" and o == "owl:ObjectProperty" for (p, o, _ln) in st.pairs):
            return True
        if any(p == "type" and o == "owl:DatatypeProperty" for (p, o, _ln) in st.pairs):
            return True
        if any(p == "type" and o == "owl:AnnotationProperty" for (p, o, _ln) in st.pairs):
            return True
        if any(p == "type" and o == "owl:Ontology" for (p, o, _ln) in st.pairs):
            return True
        if any(p == "type" and o == "owl:Class" for (p, o, _ln) in st.pairs):
            return True
        # 属性声明块：谓词全部来自 T-Box 词表
        if st.pairs and all(p in TBOX_MARKERS for (p, _o, _ln) in st.pairs):
            return True
        return False

    def relation_instances(self, predicates: tuple[str, ...]) -> list[tuple[str, str, str, int]]:
        """返回 (subject, predicate, object, line) —— 三个产品关系谓词的**个体三元组**。"""
        found: list[tuple[str, str, str, int]] = []
        wanted = set(predicates)
        for st in self.statements:
            if self.is_tbox_statement(st):
                continue
            for (p, o, ln) in st.pairs:
                local = p.split(":", 1)[1] if ":" in p else p
                if local in wanted:
                    found.append((st.subject, p, o, ln))
        return found


def _count_unbalanced(text: str) -> bool:
    text = _COMMENT_OR_STRING.sub('""', text)
    return text.count("[") != text.count("]") or text.count("(") != text.count(")")


def parse_turtle(text: str) -> TurtleDoc:
    """解析 Turtle（本仓子集）。

    返回文档对象；语法明显不平衡时抛 `FailClosed`（fail-closed，不静默放过）。
    """
    doc = TurtleDoc()
    # 换行归一：行号与文件真实行号一致
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")

    buf: list[tuple[str, int]] = []      # (chunk, 起始行号)
    buf_open = False
    start_line = 1

    def flush() -> None:
        nonlocal buf, buf_open
        if not buf:
            return
        chunk = " ".join(c for c, _l in buf)
        buf = []
        buf_open = False
        _parse_chunk(doc, chunk, start_line)

    for idx, raw in enumerate(lines, 1):
        line = strip_comments(raw)
        if not line.strip():
            continue
        stripped = line.strip()
        # 前缀 / base 指令
        m = _PREFIX_RE.match(stripped)
        if m:
            doc.prefixes[m.group(1) or ""] = m.group(2)
            continue
        m = _BASE_RE.match(stripped)
        if m:
            doc.base = m.group(1)
            continue
        if not buf:
            start_line = idx
        buf.append((line, idx))
        if _count_unbalanced(" ".join(c for c, _l in buf)) or not stripped.endswith("."):
            buf_open = True
            continue
        flush()
    if buf_open and buf:
        flush()

    # 个体：有 `a <类>` 或对非属性声明谓词的使用，且不是属性/类本体本身
    declared = doc.declared_predicates()
    declared_classes = doc.classes()
    for st in doc.statements:
        if st.subject in declared_classes or st.subject in declared:
            continue
        for (p, o, _ln) in st.pairs:
            if p in declared or o in declared:
                doc.individuals.add(st.subject)
                break
    return doc


def _parse_chunk(doc: TurtleDoc, chunk: str, start_line: int) -> None:
    """解析一段以 `.` 结尾的语句块，记录真实行号。"""
    if not chunk.strip():
        return
    # 记录每个 token 的行号：按原始行的相对偏移近似
    tokens = split_quoted(chunk)
    if not tokens:
        return
    i = 0
    while i < len(tokens) and tokens[i] not in (";", "."):
        i += 1
    subject_tokens = tokens[: i if i else len(tokens)]
    if not subject_tokens:
        return
    subject = " ".join(subject_tokens)
    if subject.split(":", 1)[0].lower() in TURTLE_KEYWORDS:
        return
    if subject.startswith('"') or subject.startswith("'"):
        return

    st = Statement(subject, start_line)
    # 切分为 `p o` 对
    pairs: list[list[str]] = []
    current: list[str] = []
    for tok in tokens[i:]:
        if tok == ";":
            if current:
                pairs.append(current)
            current = []
            continue
        if tok == ".":
            if current:
                pairs.append(current)
            current = []
            break
        current.append(tok)
    if current:
        pairs.append(current)
    for pair in pairs:
        if not pair:
            continue
        pred = pair[0]
        obj = " ".join(pair[1:]) if len(pair) > 1 else ""
        if not obj:
            continue
        st.pairs.append((pred, obj, start_line))
        if pred == "type" and obj.strip().startswith("<") and "gits" not in obj:
            st.custom_datatype = True
    if st.pairs:
        doc.statements.append(st)


def subject_label(subject: str) -> str:
    """把主语渲染成可打印形式。"""
    return subject.strip()


def is_individual_ref(term: str) -> bool:
    """该宾语是否是一个"应存在于图里的个体引用"？"""
    t = term.strip()
    if not t:
        return False
    if t.startswith('"') or t.startswith("'"):
        return False
    if t.startswith("[") or t.startswith("("):
        return False
    if t in ("true", "false", "a"):
        return False
    return True


# ══════════════════════════════════════════════════════════════════════════════
# 地图 front matter
# ══════════════════════════════════════════════════════════════════════════════

def read_map_frontmatter(path: Path) -> tuple[dict, int]:
    """读取 `---` 之间的 JSON front matter，返回 (对象, 起始行号)。"""
    text = path.read_text(encoding="utf-8-sig")
    lines = text.replace("\r\n", "\n").split("\n")
    if not lines or lines[0].strip() != "---":
        raise FailClosed(f"{path}: 缺少 opening frontmatter delimiter")
    closing = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            closing = idx
            break
    if closing is None:
        raise FailClosed(f"{path}: 缺少 closing frontmatter delimiter")
    raw = "\n".join(lines[1:closing]).strip()
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise FailClosed(f"{path}: frontmatter 不是合法 JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise FailClosed(f"{path}: frontmatter 必须是 JSON 对象")
    return value, 2  # front matter 从第 2 行开始


def collect_map_files(root: Path) -> list[Path]:
    maps_dir = root / MAPS_DIR_REL
    if not maps_dir.is_dir():
        raise FailClosed(f"地图目录缺失: {maps_dir}")
    files = sorted(p for p in maps_dir.rglob("*.md") if p.is_file())
    if not files:
        raise FailClosed(f"地图目录下没有任何 .md 地图文件: {maps_dir}")
    return files


def collect_projection_files(root: Path) -> list[Path]:
    """投影产物的真实位置。

    现状（实测）：`instances/` **未登记在 CONTRACT_INDEX / generated 管线中**，
    只有 `specs/knowledge-architecture/instances/{product,fact,candidate}/` 下的
    `*.ttl` / `*.nt` 是 RDF 投影。`UNRESOLVED.json` 是 W3 的**解析报告**（非 RDF），
    不参与图一致性比对 —— 但会作为"投影缺失"判定的证据被报告出来。
    """
    instances = root / INSTANCES_DIR_REL
    if not instances.is_dir():
        return []
    rdf = [p for p in instances.rglob("*") if p.is_file() and p.suffix.lower() in (".ttl", ".nt")]
    return sorted(rdf)


# ══════════════════════════════════════════════════════════════════════════════
# 不一致项
# ══════════════════════════════════════════════════════════════════════════════

class Finding:
    __slots__ = ("code", "file", "line", "detail", "rule")

    def __init__(self, code: str, file: str, line: int, detail: str, rule: str):
        self.code = code
        self.file = file
        self.line = line
        self.detail = detail
        self.rule = rule

    def as_dict(self) -> dict:
        return {
            "code": self.code,
            "file": self.file,
            "line": self.line,
            "detail": self.detail,
            "rule": self.rule,
        }

    def render(self) -> str:
        return f"  [{self.code}] {self.file}:{self.line}  {self.detail}"

    def key(self) -> tuple:
        return (self.code, self.file, self.line, self.detail)


# ══════════════════════════════════════════════════════════════════════════════
# 四项检测
# ══════════════════════════════════════════════════════════════════════════════

def detect_ontology_relation_instances(rel_path: str, ontology: TurtleDoc) -> list[Finding]:
    """[D1] 本体承载关系实例 ⇒ FAIL（WP1.3 裁定 / V4）。"""
    findings: list[Finding] = []
    for (subject, predicate, obj, line) in ontology.relation_instances(PRODUCT_RELATION_PREDICATES):
        findings.append(
            Finding(
                code="D1_ONTOLOGY_CARRIES_RELATION_INSTANCE",
                file=rel_path,
                line=line,
                detail=(
                    f"本体出现产品关系**实例**三元组：{subject_label(subject)} {predicate} {obj}"
                    f" —— 关系实例权威在产品卡（单向投影 产品卡 → 本体个体）；"
                    f"本体侧只允许 T-Box 谓词声明"
                ),
                rule="WP1.3 裁定 §2：关系实例的权威 = 产品卡",
            )
        )
    return findings


def detect_projection_types_outside_ontology(
    ontology: TurtleDoc, projections: list[tuple[str, TurtleDoc]]
) -> list[Finding]:
    """[D2] 投影个体类型不在本体类集合中 ⇒ FAIL。"""
    findings: list[Finding] = []
    onto_classes = ontology.classes()
    # 本体里声明过的非类资源（属性等）—— 不算类
    for rel_path, doc in projections:
        for st in doc.statements:
            for (p, o, ln) in st.pairs:
                if p != "type":
                    continue
                if not o.startswith("gits:"):
                    continue
                if o in onto_classes:
                    continue
                findings.append(
                    Finding(
                        code="D2_PROJECTION_TYPE_NOT_IN_ONTOLOGY",
                        file=rel_path,
                        line=ln,
                        detail=(
                            f"个体类型 `{o}` 不在本体类集合中：{subject_label(st.subject)} a {o}"
                            f" —— 投影只允许实例化本体已声明的类"
                        ),
                        rule="地图/本体/投影三处一致：投影类型 ⊆ 本体类",
                    )
                )
    return findings


def detect_maprefs_missing(root: Path, maps: list[Path]) -> list[Finding]:
    """[D3] `domains[].mapRef` 指向的文件不存在 ⇒ FAIL。"""
    findings: list[Finding] = []
    for path in maps:
        rel = str(path.relative_to(root))
        front, base_line = read_map_frontmatter(path)
        domains = front.get("domains")
        if domains is None:
            continue
        if not isinstance(domains, list):
            findings.append(
                Finding(
                    code="D3_MAPREF_MISSING",
                    file=rel,
                    line=base_line,
                    detail=f"`domains` 必须是数组，实际为 {type(domains).__name__}",
                    rule="mapRef 必须指向存在的域地图文件",
                )
            )
            continue
        for item in domains:
            if not isinstance(item, dict):
                continue
            ref = item.get("mapRef")
            domain_id = item.get("domainId", "?")
            if ref is None:
                findings.append(
                    Finding(
                        code="D3_MAPREF_MISSING",
                        file=rel,
                        line=base_line,
                        detail=f"domain `{domain_id}` 缺 mapRef",
                        rule="mapRef 必须指向存在的域地图文件",
                    )
                )
                continue
            target = (root / str(ref)).resolve()
            if not target.is_file():
                findings.append(
                    Finding(
                        code="D3_MAPREF_MISSING",
                        file=rel,
                        line=base_line,
                        detail=(
                            f"domain `{domain_id}` 的 mapRef 指向不存在的文件：{ref}"
                            f"（解析为 {target}）"
                        ),
                        rule="mapRef 必须指向存在的域地图文件",
                    )
                )
    return findings


def detect_dangling_projection_references(
    ontology: TurtleDoc, projections: list[tuple[str, TurtleDoc]]
) -> list[Finding]:
    """[D4] 投影个体对象指向不存在的个体 ⇒ FAIL。

    已知个体集合 = 本体主语/宾语 ∪ 全部投影主语 ∪ 该行主语。
    逐**行**校验（避免跨文件行号错位）。
    """
    findings: list[Finding] = []
    known: set[str] = set()
    for st in ontology.statements:
        known.add(st.subject)
    for _rel, doc in projections:
        for st in doc.statements:
            known.add(st.subject)
            for (_p, o, _ln) in st.pairs:
                known.add(o)

    for rel_path, doc in projections:
        for st in doc.statements:
            local_known = set(known)
            local_known.add(st.subject)
            for (p, o, ln) in st.pairs:
                if p == "type":
                    continue
                if not is_individual_ref(o):
                    continue
                # 只校验本体/投影命名空间下的引用
                if not (o.startswith("gits:") or o.startswith("<")):
                    continue
                if o in local_known:
                    continue
                findings.append(
                    Finding(
                        code="D4_PROJECTION_DANGLING_REFERENCE",
                        file=rel_path,
                        line=ln,
                        detail=(
                            f"对象 `{o}` 在图中不存在（主语 {subject_label(st.subject)}，谓词 {p}）"
                        ),
                        rule="投影个体不得悬空引用",
                    )
                )
    return findings


# ══════════════════════════════════════════════════════════════════════════════
# 变异负例（D1）—— 必须用**临时副本**，原文件逐字节复原并自证
# ══════════════════════════════════════════════════════════════════════════════

MUTATION_INJECTION = (
    "\n"
    "# __GK17_WP5.2_MUTATION__ 越权写：把应由产品卡承载的关系**实例**写进本体\n"
    "gits:prod_cm_001 gits:requiresProduct gits:prod_set_001 .\n"
)


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_mutation_selftest(root: Path, ontology_rel: str, ontology_path: Path,
                          baseline_findings: list[Finding]) -> dict:
    """对 D1 做变异负例自检：临时副本追加实例 ⇒ 必须 FAIL；撤销 ⇒ 必须 PASS。"""
    result: dict = {
        "target": ontology_rel,
        "original_sha256": None,
        "restored_sha256": None,
        "restored_byte_identical": False,
        "temp_copy_removed": False,
        "malformed_probe": None,
        "baseline_findings": len(baseline_findings),
        "mutated_findings": None,
        "caught": False,
        "notes": [],
    }

    original_bytes = ontology_path.read_bytes()
    result["original_sha256"] = hashlib.sha256(original_bytes).hexdigest()

    tmpdir = Path(tempfile.mkdtemp(prefix="gk17-wp52-mutation-"))
    tmp_ontology = tmpdir / "gits-core.owl.ttl"
    try:
        shutil.copyfile(ontology_path, tmp_ontology)

        # ── 变异：往**临时副本**追加一条关系实例三元组 ──
        mutated_text = original_bytes.decode("utf-8") + MUTATION_INJECTION
        tmp_ontology.write_text(mutated_text, encoding="utf-8")

        mutated_doc = parse_turtle(mutated_text)
        mutated_findings = detect_ontology_relation_instances(ontology_rel, mutated_doc)
        result["mutated_findings"] = len(mutated_findings)
        result["caught"] = len(mutated_findings) > len(baseline_findings)
        if mutated_findings:
            result["mutation_detail"] = mutated_findings[-1].as_dict()

        # ── 撤销：从原始字节恢复临时副本，重跑必须回到基线 ──
        tmp_ontology.write_bytes(original_bytes)
        restored_doc = parse_turtle(tmp_ontology.read_text(encoding="utf-8"))
        restored_findings = detect_ontology_relation_instances(ontology_rel, restored_doc)
        result["restored_findings"] = len(restored_findings)
        result["restored_equals_baseline"] = len(restored_findings) == len(baseline_findings)

        # ── 反空转探针：给**同一谓词**加一条 T-Box 声明，不得被误报为实例 ──
        decoy = (
            "\n"
            "gits:requiresProductVariant a owl:ObjectProperty ;\n"
            f"  rdfs:label \"variant of requires product\"@en ;\n"
            f"  rdfs:domain gits:Product ;\n"
            f"  rdfs:range gits:Product .\n"
        )
        tmp_ontology.write_text(
            original_bytes.decode("utf-8") + decoy.replace(
                "requiresProductVariant", "requiresProduct"), encoding="utf-8")
        decoy_doc = parse_turtle(tmp_ontology.read_text(encoding="utf-8"))
        decoy_findings = detect_ontology_relation_instances(ontology_rel, decoy_doc)
        result["malformed_probe"] = {
            "case": "同一谓词的 T-Box 声明（自反/无个体）",
            "findings": len(decoy_findings),
            "expected": len(baseline_findings),
            "ok": len(decoy_findings) == len(baseline_findings),
        }
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    # ── 自证原文件未被动过 ──
    result["restored_sha256"] = _sha256_file(ontology_path)
    result["restored_byte_identical"] = (
        result["restored_sha256"] == result["original_sha256"]
        and ontology_path.read_bytes() == original_bytes
    )
    result["temp_copy_removed"] = not tmpdir.exists()
    return result


# ══════════════════════════════════════════════════════════════════════════════
# 主流程
# ══════════════════════════════════════════════════════════════════════════════

def run(root: Path, allow_empty_projection: bool, mutation_selftest: bool) -> dict:
    ontology_path = root / ONTOLOGY_REL
    report: dict = {
        "root": str(root),
        "ontology": ONTOLOGY_REL,
        "mapsDir": MAPS_DIR_REL,
        "instancesDir": INSTANCES_DIR_REL,
        "findings": [],
        "counts": {},
        "projection": {},
        "mutation": None,
        "errors": [],
    }

    if not ontology_path.is_file():
        raise FailClosed(f"本体文件缺失: {ontology_path}")

    ontology = parse_turtle(ontology_path.read_text(encoding="utf-8"))
    report["ontology_stats"] = {
        "classes": len(ontology.classes()),
        "objectProperties": len(ontology.object_properties()),
        "datatypeProperties": len(ontology.datatype_properties()),
        "statements": len(ontology.statements),
    }

    maps = collect_map_files(root)
    projection_paths = collect_projection_files(root)

    projections: list[tuple[str, TurtleDoc]] = []
    for path in projection_paths:
        rel = str(path.relative_to(root))
        projections.append((rel, parse_turtle(path.read_text(encoding="utf-8"))))
    report["projection"] = {
        "rdfFiles": [rel for rel, _ in projections],
        "individuals": sum(len(doc.individuals) for _rel, doc in projections),
        "present": bool(projection_paths),
    }
    report["mapFiles"] = [str(p.relative_to(root)) for p in maps]

    findings: list[Finding] = []

    # D1 —— 本体承载关系实例
    d1 = detect_ontology_relation_instances(ONTOLOGY_REL, ontology)
    findings.extend(d1)

    # D2 —— 投影类型不在本体
    d2 = detect_projection_types_outside_ontology(ontology, projections)
    findings.extend(d2)

    # D3 —— mapRef 缺失
    d3 = detect_maprefs_missing(root, maps)
    findings.extend(d3)

    # D4 —— 投影悬空引用
    d4 = detect_dangling_projection_references(ontology, projections)
    findings.extend(d4)

    report["counts"] = {
        "D1_ONTOLOGY_CARRIES_RELATION_INSTANCE": len(d1),
        "D2_PROJECTION_TYPE_NOT_IN_ONTOLOGY": len(d2),
        "D3_MAPREF_MISSING": len(d3),
        "D4_PROJECTION_DANGLING_REFERENCE": len(d4),
    }

    # ── 投影缺失：fail-closed；--allow-empty-projection 时只报告 ──
    if not projection_paths:
        if allow_empty_projection:
            report["errors"].append(
                "投影缺失（PROJECTION_ABSENT）：instances/ 下无 RDF 产物；"
                "--allow-empty-projection 已生效 —— D2/D4 **未判定**（不得读作通过）"
            )
            report["counts"]["D2_PROJECTION_TYPE_NOT_IN_ONTOLOGY"] = "SKIPPED(projection absent)"
            report["counts"]["D4_PROJECTION_DANGLING_REFERENCE"] = "SKIPPED(projection absent)"
        else:
            raise FailClosed(
                f"投影缺失（PROJECTION_ABSENT）：{INSTANCES_DIR_REL} 下没有 .ttl/.nt 投影产物。"
                f"W3（scripts/gk17_prodcard_to_rdf.py）未就绪时可用 --allow-empty-projection "
                f"只跑本体/地图侧检查。"
            )

    report["findings"] = [f.as_dict() for f in findings]

    # ── 变异自检 ──
    if mutation_selftest:
        report["mutation"] = run_mutation_selftest(root, ONTOLOGY_REL, ontology_path, d1)

    return report


def render_text(report: dict) -> str:
    lines: list[str] = []
    add = lines.append
    add("=" * 78)
    add("GK17 WP5.2 三处一致性门禁（地图 / 本体 / 投影）（判据 V4）")
    add("=" * 78)
    add(f"root            : {report['root']}")
    add(f"ontology        : {report['ontology']}")
    stats = report.get("ontology_stats", {})
    add(f"ontology stats  : {stats.get('classes')} classes / "
        f"{stats.get('objectProperties')} object properties / "
        f"{stats.get('datatypeProperties')} datatype properties")
    proj = report.get("projection", {})
    add(f"maps            : {len(report.get('mapFiles', []))} 个地图文件")
    add(f"projection      : {len(proj.get('rdfFiles', []))} 个 RDF 文件 / "
        f"{proj.get('individuals', 0)} 个个体")
    for rel in proj.get("rdfFiles", []):
        add(f"                  · {rel}")

    counts = report.get("counts", {})
    add("")
    add("检测结果（逐条）：")
    codes = [
        ("D1", "D1_ONTOLOGY_CARRIES_RELATION_INSTANCE", "本体承载关系实例（WP1.3 裁定）"),
        ("D2", "D2_PROJECTION_TYPE_NOT_IN_ONTOLOGY", "投影个体类型不是本体类"),
        ("D3", "D3_MAPREF_MISSING", "地图 mapRef 指向的文件不存在"),
        ("D4", "D4_PROJECTION_DANGLING_REFERENCE", "投影个体悬空引用"),
    ]
    by_code: dict[str, list[dict]] = {c: [] for _d, c, _t in codes}
    for f in report.get("findings", []):
        by_code.setdefault(f["code"], []).append(f)

    for did, code, title in codes:
        n = counts.get(code, 0)
        if isinstance(n, str):
            add(f"  [{did}] {title:38s} {n}")
            continue
        verdict = "OK" if n == 0 else f"FAIL ({n} 项)"
        add(f"  [{did}] {title:38s} {verdict}")
        for f in by_code.get(code, []):
            add(f"        · {f['file']}:{f['line']}  {f['detail']}")

    errors = report.get("errors", [])
    if errors:
        add("")
        add("不可判定 / 降级声明：")
        for e in errors:
            add(f"  ! {e}")

    mut = report.get("mutation")
    if mut:
        add("")
        add("─" * 78)
        add("变异负例（D1）：临时往本体**副本**追加一条关系实例三元组 ⇒ 必须 FAIL；撤销 ⇒ 必须 PASS")
        add("─" * 78)
        add(f"  变异目标（仅副本）   : {mut['target']} （原始文件 sha256={mut['original_sha256']}）")
        add(f"  变异前 D1 计数       : {mut['baseline_findings']}")
        add(f"  追加的三元组         : gits:prod_cm_001 gits:requiresProduct gits:prod_set_001 .")
        add(f"  变异后 D1 计数       : {mut['mutated_findings']}")
        add(f"  变异被捕获           : {mut['caught']}")
        if mut.get("mutation_detail"):
            d = mut["mutation_detail"]
            add(f"  变异检出明细         : {d['file']}:{d['line']}  {d['detail']}")
        add(f"  撤销后 D1 计数       : {mut['restored_findings']} "
            f"(恢复=基线: {mut['restored_equals_baseline']})")
        probe = mut.get("malformed_probe") or {}
        if probe:
            add(f"  反空转探针           : {probe['case']} → 检出 {probe['findings']} 项 "
                f"(期望 {probe['expected']}) ⇒ {'不误报' if probe['ok'] else '**误报**'}")
        add(f"  原文件逐字节复原     : {mut['restored_byte_identical']} "
            f"(sha256={mut['restored_sha256']})")
        add(f"  临时副本已删除       : {mut['temp_copy_removed']}")

    add("")
    total = sum(v for v in counts.values() if isinstance(v, int))
    add(f"不一致项合计：{total}")
    add("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="GK17 WP5.2 三处一致性门禁（地图 / 本体 / 投影）；判据 V4。",
    )
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1],
                        help="仓库根目录（默认脚本上一级）")
    parser.add_argument("--json", action="store_true", help="以 JSON 输出（含全部不一致项）")
    parser.add_argument("--allow-empty-projection", action="store_true",
                        help="投影缺失时只报告不失败（仅用于 W3 未就绪时跑本体/地图侧检查）")
    parser.add_argument("--no-mutation-selftest", action="store_true",
                        help="跳过变异负例自检（默认执行；跳过即视为负例缺失）")
    args = parser.parse_args()

    root = args.root.resolve()
    try:
        report = run(root, args.allow_empty_projection, not args.no_mutation_selftest)
    except FailClosed as exc:
        if args.json:
            print(json.dumps({"root": str(root), "verdict": "FAIL_CLOSED",
                              "error": str(exc)}, ensure_ascii=False, indent=2))
        else:
            print(f"gk17-triple-consistency-check: FAIL_CLOSED\n  {exc}", file=sys.stderr)
        return 2

    findings = report.get("findings", [])
    counts = report.get("counts", {})
    projected_gap = any(isinstance(v, str) for v in counts.values())

    # ── 判定 ──
    failures: list[str] = []
    if findings:
        failures.append(f"检出 {len(findings)} 项三处不一致")

    mut = report.get("mutation")
    if mut is None:
        failures.append(
            "变异负例缺失：未执行 --no-mutation-selftest 之外的负例自检；"
            "本仓硬约束「不做负例的门禁视为未完成」—— 不得读作 PASS"
        )
    else:
        if not mut.get("caught"):
            failures.append("**变异未被捕获** ⇒ D1 断言空转（noop），门禁无效")
        if not mut.get("restored_equals_baseline"):
            failures.append("**撤销后未回到基线** ⇒ 变异自检不可信")
        if not mut.get("restored_byte_identical"):
            failures.append("**原始本体文件未被逐字节复原** ⇒ 违反纪律")
        if not mut.get("temp_copy_removed"):
            failures.append("**临时副本未删除**")
        probe = mut.get("malformed_probe") or {}
        if probe and not probe.get("ok"):
            failures.append("**反空转探针误报**：T-Box 声明被当成实例")

    report["verdict"] = "FAIL" if failures else ("INCONCLUSIVE" if projected_gap else "PASS")
    report["failures"] = failures

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(render_text(report))
        if failures:
            print("gk17-triple-consistency-check: FAIL", file=sys.stderr)
            for f in failures:
                print(f"  - {f}", file=sys.stderr)
        elif projected_gap:
            print("gk17-triple-consistency-check: INCONCLUSIVE —— 已检项通过，但仍有未判定项"
                  "（不得读作通过）", file=sys.stderr)
        else:
            print(f"gk17-triple-consistency-check: PASS "
                  f"(不一致项 0；变异已捕获，断言非空转)")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
