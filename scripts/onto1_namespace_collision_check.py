#!/usr/bin/env python3
"""ONTO1 WI-A4｜命名空间碰撞检查（ADR-ONTO1 §5.4 的**可执行原型**）。

四项检查（C-1 ~ C-4）以及一个"诚实性"约束：**无法判定 ≠ 通过**。

| 检查 | 判据 | 现状（Wave -1） |
|---|---|---|
| **C-1a** 旧端唯一可重建 | 基线本体声明的术语集合非空、唯一、与归属矩阵 1:1 | **可判定 → PASS** |
| **C-1b** 新旧集合互斥 + 命名空间不重叠 | 新旧 IRI 交集为空；新根域与旧命名空间互不包含 | **NOT_EVALUATED**（D3 未签 ⇒ 根域未定；无具体新 IRI 无从判定） |
| **C-2a** 前缀唯一 | 同一短前缀不得指向两个命名空间 | **实际反例**：`gits:` 双绑定（`products.ttl:1`）⇒ 经**具名登记**后方可通过，登记即修复义务 |
| **C-2b** 同名跨命名空间 | 本体已声明的本地名，不得在另一命名空间下被使用 | **实际反例**：`gits:Product`（`products.ttl:10` 等，A-Box IRI 与 T-Box 不连通） |
| **C-3** 单版本闭包 | import closure 内同一 series 不得出现两个 versionIRI | 可判定但**空转**（当前 0 个 `owl:versionIRI`）⇒ 显式声明空转，不计覆盖 |
| **C-4** 钉值一致 | 制品内容哈希 == 钉值声明哈希（**适用范围见下**） | **可判定 → PASS**（声明 4 个：受控 1 通过 / D-2 范围外 3；**必需钉值 allow-list 4/4**；载体自冻结子检查**空转，不计为覆盖**）；判据：漂移 / 受控载体未冻结 / 必需钉值缺失 / 范围未裁决 ⇒ FAIL |

### C-4 适用范围（D-2 收窄，2026-09-20）

裁定：`loops/ONTO1-ontology-split/memory/TL-DECISIONS-W-1.md` **D-2**。C-4 只对**受控钉值文件**生效
（哈希具跨仓/跨程序治理效力者）：`specs/semantic/**`、`specs/CONTRACT_INDEX.yaml`、
`.../90_control/schema/ontology_reference.json`、`.../90_control/ontology/PROVENANCE.json`；
本 Loop 的**清单类工具产物**（每次运行重生成、含 `generated_at` 时间戳，落在 `loops/**` 或 `evidence/**`）
**不属**受控钉值文件 ⇒ 不做哈希比对、也不要求自身冻结，否则产生"**每次重跑即漂移**"的噪声 FAIL
（回源：`FAILURES.md` FAIL-2026-09-20-05）。

收窄**不等于不管**（六条保留的牙齿）：

1. 受控被钉制品漂移 ⇒ 照旧 FAIL（`C-4 <label> 钉值漂移`）；
2. **受控**钉值载体未冻结 ⇒ FAIL（`C-4_PIN_FILE_UNFROZEN`）；冻结记录**必须落在冻结扫描根内**
   （默认 `loops/ONTO1-ontology-split/evidence`，在报告中**显式声明**扫描根），写在根外
   （例如 Loop 根目录的 `EVIDENCE.md`）**看不见** ⇒ 仍 FAIL
   （复现 `FAILURES.md` FAIL-2026-09-20-W15TL-03 的机制性失效；`--selftest` **M12** 正向 / **M12b** 该反例）；
3. **必需钉值 allow-list**（`REQUIRED_PINS`，4 项：基线本体 + 归属矩阵 + 消费命中 + 消费汇总）
   任一项从声明集合中**消失** ⇒ FAIL（`C-4_REQUIRED_PIN_MISSING`）。D-2 收窄**只能减"清单类产物被
   当作钉值文件"**，**绝不能减"必需钉值"**——旧实现只有"声明数 ≥1"的下限，删掉必需项后内容层
   **0 失败**（QA 反例 E3 ／ QA 条件 **C-4**；`--selftest` **M15 / M15b**）；
4. 钉值声明落在"受控"与"范围外"两者之外（范围未裁决）⇒ **fail-closed FAIL**（`C-4_PIN_SCOPE_UNCLASSIFIED`），不得静默略过；
5. 受控条目为 **0**（全部声明都在范围外）⇒ **FAIL（`C-4_NO_CONTROLLED_PIN`）**——收窄不得收窄到空；
6. 自引用检测（`C-4_SELF_REFERENCE`）**与范围无关**，照旧对所有声明生效。

**D-2 过渡义务**（`TL-DECISIONS-W-1.md:40`；QA 条件 **C-8**）：收窄实现**之前**，输出须显式标注
C-4 两条为**已知误报**（"声明而非隐藏"）。本文件已实现收窄 ⇒ 该两条（对两个**清单类侧车**的
`C-4_PIN_FILE_UNFROZEN`，即 `FAILURES.md` FAIL-2026-09-20-05 的**已知误报**）**已消失**；
输出的「载体自冻结豁免」一行仍**逐条声明**豁免对象、原因与出处（不失为"隐藏"）。
`--selftest` **M13** 证明"把清单类产物放回 C-4 扫描集 ⇒ 必 FAIL"（收窄是定向范围纠正，不是删断言换绿）。

两条子检查（**受控载体自冻结**、**受控条目为 0**）在真实仓当前均为"受控载体 0 个"⇒ 自冻结子检查
**空转**，按本 Loop 纪律**显式声明**且**不计为覆盖**（不得当成通过项上报）。

## 三条内建纪律（都是"防假绿"）

1. **登记 ≠ 豁免**：C-2 的每个实测违规必须逐条出现在
   `evidence/namespace-known-defects.json` 中（含 Owner 与**解除条件**）。
   观察到未登记 ⇒ FAIL；登记了但已不存在（陈旧登记）⇒ FAIL（防止登记被当成永久豁免）。
   登记表缺失 ⇒ **FAIL（fail-closed）**。
2. **通过条件不可绕过**：C-1b 只有在"新 IRI 具备**具体**根域形态"时才可判定；
   只要缺失即 `NOT_EVALUATED`，**整体判定为 INCOMPLETE（exit 3）而非 PASS**。
   具体根域一旦出现，必须同时存在 D3 签署件，否则 FAIL（`D3_SIGNATURE_REQUIRED`）；
   非 sandbox 模式下出现 `.example`/`.invalid`/`localhost` 等占位 TLD ⇒ FAIL
   （`PLACEHOLDER_ROOT_REJECTED`）。
3. **反空转锚定**：旧端集合必须非空且恰好唯一重建（否则检查本身空转）；C-3 空转必须显式声明。

退出码：`0` 全部判定且通过 · `2` 有 FAIL · `3` 无 FAIL 但存在 NOT_EVALUATED（**不是通过**）。

`--selftest` 在 `/tmp` 沙箱树上做 **21 条变异 + 5 条对照**（含 3 条 `restore ⇒ PASS`；
沙箱全绿 / 真实仓 **FAIL（exit 2）**），**共 26 项**。沙箱目录布局与真实仓**同构**
（受控制品在 `specs/semantic/`；清单类侧车与清单类被钉制品在 `loops/ONTO1-ontology-split/evidence/`），
故 C-4 范围收窄、**必需钉值 allow-list**（声明 + **文件存在性**）与冻结作用域在沙箱与真实仓走同一条
代码路径。`sandbox` 模式是**唯一**允许出现具体根域与占位 TLD 的路径，且只写临时目录。
缺输入 ⇒ **具名 FAIL（不抛异常）**：必需钉值文件缺失由「输入存在性闸门」在任何解析之前拦下
（TL 退回条件 A3-1/A3-2；`--selftest` M15c/M15d）。
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "loops/ONTO1-ontology-split/evidence"
DEFAULT_MANIFEST = EVIDENCE / "iri-mapping-draft.csv"
DEFAULT_REGISTRY = EVIDENCE / "namespace-known-defects.json"
DEFAULT_SIGNATURE = ROOT / "docs/architecture/ADR-ONTO1-namespace-neutral-iri-SIGNED.md"
DEFAULT_PINS = EVIDENCE / "baseline-v2-manifest.json"
DEFAULT_SCAN_PINS = EVIDENCE / "consumer-scan-manifest.json"

LEGACY_PREFIX = "gits"
EXPECTED_LEGACY_TERMS = 67          # 32 类 + 34 对象属性 + 1 数据属性
PLACEHOLDER_TLDS = (".example", ".invalid", "example.com", "localhost", "127.0.0.1")
PLACEHOLDER_ROOTS = ("PENDING:{NS-L", "REGISTRY:", "SKOS:", "SCHEMA-FIELD:", "RETIRED:")
OWL_KINDS = ("Class", "ObjectProperty", "DatatypeProperty", "Ontology")

# ---------------------------------------------------------------- C-4 适用范围（D-2 收窄）
#
# 裁定依据：`loops/ONTO1-ontology-split/memory/TL-DECISIONS-W-1.md` **D-2**。
#   D-2 把 C-4「钉值一致性」的适用范围**收窄为受控钉值文件** —— 即哈希具有**跨仓/跨程序
#   治理效力**的制品（下列 CONTROLLED_PIN_* 四项，逐条对应 D-2 的列举）。
#   D-2 同时**排除**"本 Loop 的清单类工具产物"（`baseline-v2-manifest.json`、
#   `consumer-scan-manifest.json`、`product-refs-summary.json` 等）：它们每次运行都重生成
#   （含 `generated_at` 时间戳），当作钉值必然产生"**每次重跑即漂移**"的噪声 FAIL
#   （回源：`loops/ONTO1-ontology-split/FAILURES.md` FAIL-2026-09-20-05）。
#
# 为什么把范围写成**集中常量**而不是散在判定里：让 TL 审计时一眼看出"范围是否被悄悄放大
# （把不该管的纳管）或放松（把该管的漏掉）"。改动这两个常量 = 改动 C-4 的管辖范围，必须
# 有裁定依据。
#
# 三类分类（`pin_scope()`，单一真值函数；--gate 与 --selftest 共用）：
#   controlled    —— 受控钉值文件：参与哈希比对 + 载体自身冻结要求（**牙齿保留**）
#   list_artifact —— D-2 排除的清单类工具产物：逐条登记但**不判定**（不比对、不要求冻结）
#   unclassified  —— 两者皆非：范围未裁决 ⇒ **fail-closed FAIL**（不得静默略过）
CONTROLLED_PIN_PREFIXES = (
    "specs/semantic/",                  # D-2①：L1 正式语义制品（本体与语义制品）
    "specs/CONTRACT_INDEX.yaml",        # D-2④：合同登记表的钉值字段
)
CONTROLLED_PIN_SUFFIXES = (
    "/90_control/schema/ontology_reference.json",   # D-2②：KERT 受控控制面
    "/90_control/ontology/PROVENANCE.json",         # D-2③：KERT 受控控制面
)
# D-2 排除类的**所在区**：本 Loop（及各 Loop）目录与仓根证据目录。
# 回源：被 D-2 点名的 `baseline-v2-manifest.json` / `consumer-scan-manifest.json` 实际位于
# `<root>/loops/ONTO1-ontology-split/evidence/`（`git ls-files` 可复核）；
# 沙箱以 `--root` 为仓根，布局同构，故同一模式对沙箱与真实仓一致生效。
LIST_ARTIFACT_PREFIXES = (
    "loops/",
    "evidence/",
)

# C-4 **必需钉值 allow-list**（QA 条件 C-4；反例来源：QA 报告 §4.2 E3）。
#
# 为什么需要：D-2 只允许把**清单类工具产物**移出范围，而旧实现的下限仅为"声明数 ≥ 1"
# （`"PASS" if entries else "FAIL"`）⇒ 把**受控制品**从侧车里删掉后，内容层**0 失败**，
# "收窄过度"在内容层不可检出（这就是 E3：删到只剩 1 项仍报 PASS）。本 allow-list 把
# "必需要钉住什么"从**隐性假设**变成**可断言集合**：任一项消失 ⇒ `C-4_REQUIRED_PIN_MISSING` FAIL。
#
# 口径说明（路径为**仓根相对**，即侧车 `file` 字段的原值）：
#   · `specs/semantic/gits-core.owl.ttl`                    ← `evidence/baseline-v2-manifest.json:3`
#   · `loops/ONTO1-ontology-split/evidence/attribution-45-v2.csv` ← 同文件 `:11`（D-2 范围外，仍**必须声明**）
#   · `loops/ONTO1-ontology-split/evidence/consumer-scan-hits.jsonl`    ← `evidence/consumer-scan-manifest.json:18`
#   · `loops/ONTO1-ontology-split/evidence/consumer-scan-summary.csv`   ← 同文件 `:19`
# 说明：QA 条件 C-4 对后三项写作 `evidence/…` 简写，其实际声明路径为 Loop 证据目录
# （回源见上）——本条按**实际声明路径**断言，避免因简写造成"断言永不成立"的空转。
REQUIRED_PINS = (
    "specs/semantic/gits-core.owl.ttl",
    "loops/ONTO1-ontology-split/evidence/attribution-45-v2.csv",
    "loops/ONTO1-ontology-split/evidence/consumer-scan-hits.jsonl",
    "loops/ONTO1-ontology-split/evidence/consumer-scan-summary.csv",
)

PREFIX_RE = re.compile(r"^[ \t]*@prefix[ \t]+([A-Za-z0-9_.-]*):[ \t]*<([^>]*)>[ \t]*\.", re.MULTILINE)
TYPED_RE = re.compile(
    r"^([A-Za-z][A-Za-z0-9_]*):([A-Za-z0-9_]+)[ \t]+a[ \t]+owl:(Class|ObjectProperty|DatatypeProperty|Ontology)\b",
    re.MULTILINE)
USED_RE = re.compile(r"\b([A-Za-z][A-Za-z0-9_]*):([A-Za-z0-9_]+)\b")
ONTOLOGY_RE = re.compile(
    r"^([A-Za-z][A-Za-z0-9_]*):([A-Za-z0-9_]+)[ \t]+a[ \t]+owl:Ontology\b", re.MULTILINE)
VERSION_IRI_RE = re.compile(r"owl:versionIRI[ \t]+<([^>]+)>")
IMPORTS_RE = re.compile(r"owl:imports[ \t]+<([^>]+)>")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scan_prefixes(paths: list[Path]) -> list[dict]:
    bindings: list[dict] = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for line_no, line in enumerate(text.splitlines(), start=1):
            match = PREFIX_RE.match(line)
            if match:
                bindings.append({"file": path, "line": line_no, "prefix": match.group(1),
                                 "namespace": match.group(2)})
    return bindings


def ttl_files(root: Path) -> list[Path]:
    return sorted((root / "specs").rglob("*.ttl"))


def declared_terms(path: Path) -> dict[str, dict]:
    text = path.read_text(encoding="utf-8")
    terms: dict[str, dict] = {}
    for line_no, line in enumerate(text.splitlines(), start=1):
        match = TYPED_RE.match(line)
        if not match:
            continue
        prefix, local, kind = match.groups()
        if kind == "Ontology":
            continue
        terms.setdefault(local, {"prefix": prefix, "kind": kind, "line": line_no})
    return terms


def legacy_namespace(root: Path) -> tuple[str, str]:
    bindings = [b for b in scan_prefixes(ttl_files(root))
                if b["prefix"] == LEGACY_PREFIX and b["file"].name == "gits-core.owl.ttl"]
    namespaces = sorted({b["namespace"] for b in bindings})
    if len(namespaces) != 1:
        raise RuntimeError(f"{LEGACY_PREFIX}: 基线本体前缀绑定 = {namespaces}（期望恰好 1）")
    return namespaces[0], f"{bindings[0]['file'].relative_to(root).as_posix()}:{bindings[0]['line']}"


def concrete_new_iris(manifest: Path) -> dict:
    if not manifest.is_file():
        raise RuntimeError(f"新 IRI 清单缺失（fail-closed）：{manifest}")
    with manifest.open(encoding="utf-8", newline="") as handle:
        rows = [row for row in csv.DictReader(handle) if row.get("新IRI草案(未发布)")]
    concrete, placeholder = [], []
    for row in rows:
        iri = row["新IRI草案(未发布)"].strip()
        if iri.startswith(("http://", "https://", "urn:", "info:")):
            concrete.append({"termId": row["termId"], "iri": iri,
                             "root": iri.rsplit("#", 1)[0] if "#" in iri else iri.rsplit("/", 1)[0] + "/"})
        elif iri.startswith(PLACEHOLDER_ROOTS):
            placeholder.append({"termId": row["termId"], "iri": iri})
        else:
            raise RuntimeError(f"未识别的新 IRI 形态（fail-closed）：{row['termId']} → {iri}")
    return {"rows": len(rows), "concrete": concrete, "placeholder": placeholder}


def load_registry(path: Path) -> dict:
    if not path.is_file():
        raise RuntimeError(f"已知缺陷登记表缺失（fail-closed，登记不得缺省为空）：{path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    defects = data.get("defects")
    if not isinstance(defects, list):
        raise RuntimeError(f"登记表 defects 必须为数组：{path}")
    return {"path": path, "defects": defects}


def observed_c2(root: Path, legacy_ns: str, terms: dict[str, dict]) -> list[dict]:
    files = ttl_files(root)
    bindings = scan_prefixes(files)
    violations: list[dict] = []

    by_prefix: dict[str, dict[str, list[str]]] = {}
    for binding in bindings:
        by_prefix.setdefault(binding["prefix"], {}).setdefault(binding["namespace"], []).append(
            f"{binding['file'].relative_to(root).as_posix()}:{binding['line']}")
    for prefix, namespaces in sorted(by_prefix.items()):
        if len(namespaces) > 1:
            violations.append({
                "check": "C-2a",
                "key": f"prefix={prefix};namespaces={','.join(sorted(namespaces))}",
                "prefix": prefix,
                "detail": f"短前缀 `{prefix}:` 同时指向 {len(namespaces)} 个命名空间",
                "evidence": sorted(occ for occs in namespaces.values() for occ in occs),
            })

    for binding in bindings:
        if binding["namespace"] == legacy_ns:
            continue
        file_terms = []
        for line_no, line in enumerate(binding_file_lines(binding["file"]), start=1):
            for prefix, local in USED_RE.findall(line):
                if prefix == binding["prefix"] and local in terms:
                    file_terms.append((line_no, local))
        for line_no, local in sorted(set(file_terms)):
            violations.append({
                "check": "C-2b",
                "key": f"localname={local};namespace={binding['namespace']}",
                "prefix": binding["prefix"],
                "detail": f"本体已声明的 `{local}` 在命名空间 {binding['namespace']} 下被使用（同名不同 IRI）",
                "evidence": [f"{binding['file'].relative_to(root).as_posix()}:{line_no}"],
            })
    deduped: dict[str, dict] = {}
    for violation in violations:
        key = violation["key"]
        if key in deduped:
            deduped[key]["evidence"] = sorted(set(deduped[key]["evidence"]) | set(violation["evidence"]))
        else:
            deduped[key] = violation
    return list(deduped.values())


def binding_file_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def check_c3(root: Path) -> dict:
    series: dict[str, set[str]] = {}
    ontology_count = 0
    import_count = 0
    for path in ttl_files(root):
        text = path.read_text(encoding="utf-8")
        for prefix, local in ONTOLOGY_RE.findall(text):
            ontology_count += 1
            versions = set(VERSION_IRI_RE.findall(text))
            series.setdefault(f"{prefix}:{local}", set()).update(versions)
        import_count += len(IMPORTS_RE.findall(text))
    if ontology_count == 0:
        return {"status": "FAIL", "reason": "closure 无法构建：未声明任何 owl:Ontology（空转）",
                "series": {}, "ontologies": 0, "imports": 0}
    multi = {name: sorted(versions) for name, versions in series.items() if len(versions) > 1}
    versions_total = sum(len(v) for v in series.values())
    return {
        "status": "FAIL" if multi else "PASS",
        "reason": "同一 series 出现多个 versionIRI" if multi else None,
        "multi_version_series": multi,
        "ontologies": ontology_count,
        "imports": import_count,
        "version_iri_total": versions_total,
        "vacuous": versions_total == 0,
        "vacuous_note": ("closure 内 0 个 owl:versionIRI ⇒ 单版本约束**空转**，不计为覆盖"
                         if versions_total == 0 else None),
        "series": {name: sorted(versions) for name, versions in sorted(series.items())},
    }


def _rel_posix(root: Path, path: Path) -> str:
    """仓根相对 POSIX 路径；不在仓根下（如 KERT 侧绝对路径）时退回自身 POSIX 形态。"""
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def pin_scope(root: Path, path: Path) -> str:
    """C-4 适用范围分类（单一真值函数；--gate 与 --selftest 共用，见文件头「C-4 适用范围」）。

    controlled    —— 受控钉值文件（D-2）：参与哈希比对 + 载体自身冻结要求
    list_artifact —— D-2 排除的清单类工具产物：逐条登记但不判定（不比对、不要求冻结）
    unclassified  —— 两者皆非：范围未裁决 ⇒ fail-closed（调用方必须判 FAIL，不得静默略过）
    """
    rel = _rel_posix(root, path)
    absolute = path.as_posix()
    if any(rel.startswith(prefix) for prefix in CONTROLLED_PIN_PREFIXES):
        return "controlled"
    if any(absolute.endswith(suffix) for suffix in CONTROLLED_PIN_SUFFIXES):
        return "controlled"
    if any(rel.startswith(prefix) for prefix in LIST_ARTIFACT_PREFIXES):
        return "list_artifact"
    return "unclassified"


def check_c4(root: Path, pins: Path, scan_pins: Path, freeze_root: Path) -> dict:
    """C-4 钉值一致（适用范围 = CONTROLLED_PIN_PREFIXES/SUFFIXES，D-2 收窄）。

    判据与牙齿（与文件头一一对应）：受控制品漂移 ⇒ FAIL；受控载体未冻结 ⇒ FAIL（冻结记录必须在
    冻结扫描根内，报告中显式声明扫描根）；**必需钉值缺失 ⇒ FAIL（REQUIRED_PINS allow-list）**；
    范围未裁决 ⇒ FAIL；受控条目为 0 ⇒ FAIL（防"收窄到空"）；自引用 ⇒ FAIL（与范围无关）。
    """
    empty_counters = {"count": 0, "controlled_count": 0, "out_of_scope_count": 0,
                      "unclassified_count": 0, "freeze_subjects": 0,
                      "required_missing": list(REQUIRED_PINS),
                      "freeze_scope": _rel_posix(root, freeze_root),
                      "freeze_exempt": []}
    if not pins.is_file():
        reason = f"钉值清单缺失（fail-closed）：{pins}"
        return {"status": "FAIL", "reason": reason, "pins": [], "declarations": [],
                "out_of_scope": [], "vacuous": [], "failures": [reason], **empty_counters}
    data = json.loads(pins.read_text(encoding="utf-8"))
    declarations: list[dict] = []
    baseline = data.get("baseline") or {}
    if baseline.get("file") and baseline.get("sha256"):
        declarations.append({"label": "baseline", "path": root / baseline["file"],
                             "declared": baseline["sha256"], "sidecar": pins})
    if data.get("attribution_csv") and data.get("attribution_sha256"):
        declarations.append({"label": "attribution", "path": root / data["attribution_csv"],
                             "declared": data["attribution_sha256"], "sidecar": pins})
    if scan_pins.is_file():
        scan = json.loads(scan_pins.read_text(encoding="utf-8"))
        for label, key_file, key_hash in (("hits", "hits_file", "hits_sha256"),
                                         ("summary", "summary_file", "summary_sha256")):
            if scan.get(key_file) and scan.get(key_hash):
                declarations.append({"label": label, "path": root / scan[key_file],
                                     "declared": scan[key_hash], "sidecar": scan_pins})
    sidecars = [p for p in (pins, scan_pins) if p.is_file()]
    results: list[dict] = []
    failures: list[str] = []

    # C-4a 自引用检测（规格 §4.4 的结构性约束：指纹不得写回被哈希文件自身 ⇒ 永不收敛；
    # 反例 GK-KE FAIL-2026-09-12-03）。**与 D-2 范围无关**：只要"被钉者 == 钉值载体"即违规，
    # 因此本项在范围过滤之前对所有声明生效。
    for declaration in declarations:
        for sidecar in sidecars:
            if declaration["path"].resolve() == sidecar.resolve():
                failures.append(f"C-4_SELF_REFERENCE 钉值文件 {sidecar.name} 自身即被钉值 "
                                f"`{declaration['label']}`")

    in_scope: list[dict] = []
    out_of_scope: list[dict] = []
    unclassified: list[dict] = []
    for declaration in declarations:
        scope = pin_scope(root, declaration["path"])
        entry = {"label": declaration["label"], "path": _rel_posix(root, declaration["path"]),
                 "scope": scope}
        if scope == "controlled":
            if not declaration["path"].is_file():
                entry.update(status="FAIL", reason="missing")
                failures.append(f"C-4 {declaration['label']} 受控制品缺失：{entry['path']}")
            else:
                actual = sha256(declaration["path"])
                ok = actual == declaration["declared"]
                entry.update(status="PASS" if ok else "FAIL",
                             expected=declaration["declared"][:16], actual=actual[:16])
                if not ok:
                    failures.append(f"C-4 {declaration['label']} 钉值漂移：{declaration['path'].name} "
                                    f"{actual[:16]} != {declaration['declared'][:16]}")
            in_scope.append(entry)
        elif scope == "list_artifact":
            entry.update(status="OUT_OF_SCOPE",
                         reason="D-2：本 Loop 清单类工具产物（每次运行重生成）⇒ 不属受控钉值文件；"
                                "不比对哈希、不要求自身冻结（噪声 FAIL 的根因已消除）")
            out_of_scope.append(entry)
        else:
            entry.update(status="FAIL", reason="范围未裁决：既非受控钉值文件，也不属 D-2 排除的清单类产物")
            unclassified.append(entry)
            failures.append(f"C-4_PIN_SCOPE_UNCLASSIFIED 钉值声明落在 C-4 无法判定的范围"
                            f"（fail-closed，不得静默略过）：{entry['path']}")
        results.append(entry)

    # 必需钉值 allow-list（QA 条件 C-4 + TL 退回条件 A3-1）：两件事都断言 ——
    #   ① 该路径**出现在钉值声明集合**中（D-2 收窄不得减必需钉值）；
    #   ② 该**文件存在**（`is_file()`）—— TL 沙箱 M-C 实证：只断言声明时，**删掉范围外的必需钉值文件**
    #      仍报 `[C-4] PASS（必需钉值 allow-list 4/4）`，即 Q_A 的 E3 只关了一半。
    # 反例来源：QA 报告 §4.2 E3（删声明）＋ TL 审计 §4 M-B/M-C（删文件）。
    declared_paths = {_rel_posix(root, declaration["path"]) for declaration in declarations}
    required_missing: list[str] = []
    for path in REQUIRED_PINS:
        if path not in declared_paths:
            required_missing.append(path)
            failures.append(f"C-4_REQUIRED_PIN_MISSING 必需钉值未出现在声明集合中"
                            f"（D-2 收窄不得减必需钉值）：{path}")
            results.append({"label": f"required:{path}", "status": "FAIL",
                            "reason": "必需钉值**声明**缺失（allow-list，QA 条件 C-4）"})
        elif not (root / path).is_file():
            required_missing.append(path)
            failures.append(f"C-4_REQUIRED_PIN_MISSING 必需钉值**文件**不存在"
                            f"（allow-list 断言文件存在，TL 退回条件 A3-1）：{path}")
            results.append({"label": f"required:{path}", "status": "FAIL",
                            "reason": "必需钉值**文件**不存在（A3-1）"})
        else:
            results.append({"label": f"required:{path}", "status": "PASS"})

    # 空转防护：**收窄不得收窄到空**。D-2 只收窄适用范围，不得使 C-4 变成恒绿。
    if not in_scope:
        failures.append("C-4_NO_CONTROLLED_PIN 受控钉值条目为 0（全部声明都在 D-2 范围外）⇒ "
                        "C-4 判定空转，不得计为通过")

    # C-4b 钉值载体自身冻结（规格 §4.4：否则"改钉值即可通过"）。
    # D-2 收窄后**只对受控载体**生效；清单类产物载体是可重生成的工具产物，冻结必然漂移。
    # 作用域（QA 条件 C-3 / F-3）：记录必须落在 **冻结扫描根内**，扫描根在本函数返回并在报告中打印；
    # 写在扫描根之外（如 Loop 根目录的 `EVIDENCE.md`）⇒ 看不到 ⇒ 仍 FAIL。
    freeze_scope_rel = _rel_posix(root, freeze_root)
    freeze_exempt = [_rel_posix(root, p) for p in sidecars if pin_scope(root, p) == "list_artifact"]
    controlled_sidecars = [p for p in sidecars if pin_scope(root, p) == "controlled"]
    vacuous: list[str] = []
    for sidecar in controlled_sidecars:
        digest = sha256(sidecar)
        if frozen_in(freeze_root, digest, exclude=sidecar):
            results.append({"label": f"freeze:{sidecar.name}", "scope": "controlled",
                            "status": "PASS", "sha256_prefix": digest[:16],
                            "freeze_scope": freeze_scope_rel})
        else:
            failures.append(f"C-4_PIN_FILE_UNFROZEN 受控钉值载体未冻结（在扫描根 {freeze_scope_rel} 内"
                            f"无独立记录其哈希）：{sidecar.name} {digest[:16]}")
            results.append({"label": f"freeze:{sidecar.name}", "scope": "controlled",
                            "status": "FAIL", "sha256_prefix": digest[:16],
                            "freeze_scope": freeze_scope_rel})
    if not controlled_sidecars:
        vacuous.append("pin_sidecar_freeze")
        results.append({"label": "freeze_subjects", "status": "VACUOUS", "freeze_scope": freeze_scope_rel,
                        "reason": f"受控钉值载体 0 个（本 Loop 侧车均属 D-2 范围外的清单类产物；"
                                  f"原 FAIL-2026-09-20-05 的 C-4_PIN_FILE_UNFROZEN 为**已知误报**，"
                                  f"收窄后消除）⇒ 该子检查空转，**不计为覆盖**"})
    results.append({"label": "self_reference", "status": "FAIL" if any(
        f.startswith("C-4_SELF_REFERENCE") for f in failures) else "PASS"})

    status = "FAIL" if failures else ("PASS" if declarations else "FAIL")
    reason = failures[0] if failures else (None if declarations else "无任何钉值可校验（空转）")
    return {"status": status, "reason": reason, "pins": results, "declarations": declarations,
            "count": len(declarations), "controlled_count": len(in_scope),
            "out_of_scope_count": len(out_of_scope), "unclassified_count": len(unclassified),
            "freeze_subjects": len(controlled_sidecars), "vacuous": vacuous,
            "required_total": len(REQUIRED_PINS), "required_missing": required_missing,
            "freeze_scope": freeze_scope_rel, "freeze_exempt": freeze_exempt,
            "out_of_scope": [f"{e['label']}={e['path']}" for e in out_of_scope],
            "failures": failures}


def frozen_in(freeze_root: Path, digest: str, exclude: Path, max_bytes: int = 2_000_000) -> bool:
    """钉值文件的哈希是否被**另一份**独立记录所覆盖（版本控制内的证据索引即可）。"""
    if not freeze_root.is_dir():
        return False
    for path in sorted(freeze_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in (".md", ".json", ".txt", ".csv"):
            continue
        if path.resolve() == exclude.resolve():
            continue
        try:
            if path.stat().st_size > max_bytes:
                continue
            if digest in path.read_text(encoding="utf-8", errors="ignore"):
                return True
        except OSError:
            continue
    return False


def _empty_report_tail() -> dict:
    """报告尾部字段的**统一默认值**（A3-2：任何提前/异常返回都必须形状完整，`emit()` 不得触雷）。

    TL 沙箱 M-B 实测：删除必需钉值文件后，`legacy_namespace()` 抛 `RuntimeError`，而 `run()` 的
    兜底报告缺 `refirement_gate_scope` ⇒ `emit()` 抛 `KeyError`（崩溃 ≠ FAIL）。本函数把"崩溃路径"
    收敛为"形状完整的具名 FAIL 报告"。
    """
    return {
        "legacy_namespace": "?", "legacy_namespace_source": "?", "legacy_terms": -1,
        "new_iri": None, "d3_signature": {"present": False, "path": "?"},
        "not_evaluated": [], "refirement_gate_scope": ["C-2 碰撞检查", "C-3 import closure 单版本"],
        "not_covered": ["WI-A2 处置表关闭", "双侧 Owner 签署"],
        "missing_required_inputs": [], "result": "FAIL", "exit_code": 2,
    }


def check(root: Path, manifest: Path, registry_path: Path, signature: Path,
          pins: Path, scan_pins: Path, sandbox: bool, freeze_root: Path | None = None) -> dict:
    freeze_root = freeze_root or (root / "loops/ONTO1-ontology-split/evidence")
    report: dict = {"root": str(root), "sandbox": sandbox, "failures": [], "checks": {}}
    report.update(_empty_report_tail())

    def fail(code: str, message: str) -> None:
        report["failures"].append(f"{code}: {message}")

    # ---- 必需钉值**输入存在性**闸门（TL 退回条件 A3-1 + A3-2）----
    # 位置在**任何解析之前**：缺文件时若继续走，`legacy_namespace()` 等会抛异常，再由 emit 触雷
    # （TL 沙箱 M-B 实测 `KeyError: 'refirement_gate_scope'`）。此处先给出**具名 FAIL** 并
    # **提前返回**（fail-closed、确定、可复核），保证"缺输入 ⇒ 具名 FAIL，**不崩镲**"。
    missing_inputs = [path for path in REQUIRED_PINS if not (root / path).is_file()]
    if missing_inputs:
        for path in missing_inputs:
            fail("C-4", f"C-4_REQUIRED_PIN_MISSING 必需钉值**文件**不存在"
                        f"（输入存在性闸门，A3-1/A3-2）：{path}")
        report["legacy_namespace"], report["legacy_namespace_source"] = "?", "?"
        report["legacy_terms"] = -1
        report["checks"]["C-4"] = {
            "status": "FAIL", "reason": "必需钉值文件缺失 ⇒ 未进入任何解析（fail-closed）",
            "pins": [], "declarations": [], "count": 0, "controlled_count": 0,
            "out_of_scope_count": 0, "unclassified_count": 0, "freeze_subjects": 0,
            "freeze_scope": _rel_posix(root, freeze_root), "freeze_exempt": [],
            "required_total": len(REQUIRED_PINS), "required_missing": missing_inputs,
            "out_of_scope": [], "vacuous": ["pin_sidecar_freeze"],
            "failures": [f"C-4_REQUIRED_PIN_MISSING（输入存在性闸门）：{path}" for path in missing_inputs],
        }
        report["result"], report["exit_code"] = "FAIL", 2
        report["missing_required_inputs"] = missing_inputs
        return report

    legacy_ns, legacy_src = legacy_namespace(root)
    report["legacy_namespace"] = legacy_ns
    report["legacy_namespace_source"] = legacy_src
    terms = declared_terms(root / "specs/semantic/gits-core.owl.ttl")
    report["legacy_terms"] = len(terms)

    # ---- C-1a 旧端唯一可重建（反空转：非空 + 恰好 67） ----
    if len(terms) != EXPECTED_LEGACY_TERMS:
        fail("C-1a", f"旧端集合 = {len(terms)} != {EXPECTED_LEGACY_TERMS}（检查空转或基线漂移）")
        report["checks"]["C-1a"] = {"status": "FAIL", "count": len(terms)}
    else:
        report["checks"]["C-1a"] = {"status": "PASS", "count": len(terms),
                                    "namespace": legacy_ns,
                                    "kinds": {kind: sum(1 for t in terms.values() if t["kind"] == kind)
                                              for kind in ("Class", "ObjectProperty", "DatatypeProperty")}}

    # ---- 新 IRI 形态与占位纪律 ----
    manifest_data = concrete_new_iris(manifest)
    roots = sorted({entry["root"] for entry in manifest_data["concrete"]})
    report["new_iri"] = {"rows": manifest_data["rows"],
                         "concrete": len(manifest_data["concrete"]),
                         "placeholder": len(manifest_data["placeholder"]),
                         "roots": roots}
    placeholder_hit = [r for r in roots if any(hint in r.lower() for hint in PLACEHOLDER_TLDS)]
    signed = signature.is_file()
    report["d3_signature"] = {"path": signature.relative_to(root).as_posix()
                              if signature.is_relative_to(root) else str(signature), "present": signed}

    if roots and not sandbox and placeholder_hit:
        fail("PLACEHOLDER_ROOT_REJECTED",
             f"非 sandbox 模式出现占位根域：{placeholder_hit}（D3 未签期间禁止写入任何制品）")
    if roots and not sandbox and not signed:
        fail("D3_SIGNATURE_REQUIRED",
             f"已填具体新根域 {roots} 但缺 D3 签署件：{report['d3_signature']['path']}")

    # ---- C-1b 新旧集合互斥 ----
    old_set = {f"{legacy_ns}{name}" for name in terms}
    new_set = {entry["iri"] for entry in manifest_data["concrete"]}
    # sandbox 是唯一允许用占位 TLD 的路径（且只写 /tmp）；真实模式下占位根域已被上方具名拒绝
    can_decide_c1b = bool(new_set) and (sandbox or not placeholder_hit)
    if not can_decide_c1b:
        report["checks"]["C-1b"] = {
            "status": "NOT_EVALUATED",
            "reason": "无具体新 IRI（D3 未签、根域未定）⇒ 交集无从计算；**不得计为通过**",
            "concrete_new_iris": len(new_set),
        }
    else:
        overlap = sorted(old_set & new_set)
        ns_overlap = []
        for root_ns in roots:
            for old_ns in sorted({legacy_ns}):
                if root_ns == old_ns or root_ns.startswith(old_ns) or old_ns.startswith(root_ns):
                    ns_overlap.append({"new_root": root_ns, "old_namespace": old_ns})
        if overlap or ns_overlap:
            fail("C-1b", f"新旧集合不互斥：term_overlap={overlap[:3]} ns_overlap={ns_overlap[:3]}")
            report["checks"]["C-1b"] = {"status": "FAIL", "term_overlap": overlap, "ns_overlap": ns_overlap}
        else:
            report["checks"]["C-1b"] = {"status": "PASS", "old": len(old_set), "new": len(new_set),
                                        "roots": roots}

    # ---- C-2 前缀唯一 / 同名跨命名空间 ----
    # 规格约束（ONTO1-碰撞检查脚本需求规格-DRAFT §4.2 / R-2）：**首次修复前豁免不得掩盖 C-2**，
    # 「全豁免 ⇒ FAIL」。故：实测冲突存在即 FAIL；登记表只用来记录**修复义务**，永不能使 C-2 转绿。
    observed = observed_c2(root, legacy_ns, terms)
    try:
        registry = load_registry(registry_path)
    except RuntimeError as exc:
        fail("C-2", str(exc))
        report["checks"]["C-2"] = {"status": "FAIL", "reason": str(exc), "observed": len(observed)}
    else:
        registered = {d.get("key"): d for d in registry["defects"] if d.get("key")}
        observed_keys = {v["key"] for v in observed}
        unregistered = sorted(observed_keys - set(registered))
        stale = sorted(set(registered) - observed_keys)
        unowned = sorted(k for k, v in registered.items() if not v.get("owner") or not v.get("removal_condition"))
        if observed_keys:
            fail("C-2", f"实测碰撞 {len(observed_keys)} 处 ⇒ 阻断发布（ADR §5.4『必须先修』）")
        if observed_keys and not unregistered:
            fail("C-2", "C-2_ALL_CONFLICTS_REGISTERED_NOT_EXEMPTED：全部实测碰撞均已登记 ⇒ "
                        "登记不等于豁免，仍阻断发布（规格 M-C2-2 全豁免假绿）")
        if unregistered:
            fail("C-2", f"未登记修复义务的碰撞（fail-closed）：{unregistered}")
        if stale:
            fail("C-2", f"陈旧登记（缺陷已消失但登记未撤，登记不得当永久豁免）：{stale}")
        if unowned:
            fail("C-2", f"登记项缺 Owner 或解除条件：{unowned}")
        report["checks"]["C-2"] = {
            "status": "FAIL" if (observed_keys or unregistered or stale or unowned) else "PASS",
            "observed": observed, "registered": sorted(registered), "stale": stale,
            "unregistered": unregistered,
            "note": "登记 ≠ 豁免：冲突存在即阻断发布；登记表只记录修复义务（Owner + 解除条件）",
        }

    # ---- C-3 单版本闭包 ----
    c3 = check_c3(root)
    report["checks"]["C-3"] = c3
    if c3["status"] == "FAIL":
        fail("C-3", c3["reason"])

    # ---- C-4 钉值一致（含自引用与钉值文件自冻结） ----
    c4 = check_c4(root, pins, scan_pins, freeze_root)
    report["checks"]["C-4"] = c4
    if c4["status"] == "FAIL":
        for item in c4.get("failures", [c4["reason"]]):
            fail("C-4", item)

    not_evaluated = [name for name, row in report["checks"].items() if row["status"] == "NOT_EVALUATED"]
    report["not_evaluated"] = not_evaluated
    # QA-W3R4 C-1 修复：**空转（VACUOUS）不得给绿**。
    # 原实现把"冻结域为空"只记 VACUOUS 而整体仍可 PASS；且 D3 签署后 C-1b 转绿会连带整门转绿
    # ⇒ 与 R4「空转 = 失败」冲突。现：存在任何 VACUOUS 子检查 ⇒ 整体 INCOMPLETE（exit 3），**永不 0**。
    vacuous_rows = [name for name, row in report["checks"].items() if row.get("status") == "VACUOUS"]
    report["vacuous"] = vacuous_rows
    # 规格 §5：本脚本只负责退役门的第 2/3 条 ⇒ 固定输出范围，禁止把"本脚本绿"表述为"退役门通过"
    report["refirement_gate_scope"] = ["C-2 碰撞检查", "C-3 import closure 单版本"]
    report["not_covered"] = ["WI-A2 处置表关闭", "双侧 Owner 签署"]
    if report["failures"]:
        report["result"] = "FAIL"
        report["exit_code"] = 2
    elif not_evaluated or vacuous_rows:
        report["result"] = "INCOMPLETE"
        report["exit_code"] = 3
    else:
        report["result"] = "PASS"
        report["exit_code"] = 0
    return report


def emit(report: dict) -> None:
    """输出报告。**只读 + 形状容错**（A3-2）：缺字段时打印"?"而非抛异常。"""
    print(f"[根] {report.get('root')}（legacy namespace = {report.get('legacy_namespace')} @ "
          f"{report.get('legacy_namespace_source')}；旧端术语 {report.get('legacy_terms')}）")
    if report.get("new_iri"):
        print(f"[新] 清单行 {report['new_iri']['rows']}  具体 IRI {report['new_iri']['concrete']}  "
              f"占位 {report['new_iri']['placeholder']}  根域 {report['new_iri']['roots'] or '未定'}"
              f"  D3 签署件={report.get('d3_signature', {}).get('present')}")
    for name in ("C-1a", "C-1b", "C-2", "C-3", "C-4"):
        row = report["checks"].get(name)
        if row is None:
            continue
        status = row["status"]
        extra = ""
        if name == "C-2":
            extra = (f"（实测 {len(row['observed'])} / 登记 {len(row['registered'])}"
                     f" / 未登记 {len(row['unregistered'])} / 陈旧 {len(row['stale'])}）")
        elif name == "C-3" and row.get("vacuous_note"):
            extra = f"（{row['vacuous_note']}）"
        elif name == "C-4":
            extra = (f"（声明 {row['count']} 个：受控 {row['controlled_count']}"
                     f" / D-2 范围外 {row['out_of_scope_count']}"
                     f" / 未裁决 {row['unclassified_count']}；"
                     f"必需钉值 allow-list "
                     f"{row['required_total'] - len(row['required_missing'])}/{row['required_total']}；"
                     f"载体自冻结：受控载体 {row['freeze_subjects']} 个"
                     + ("，**空转不计为覆盖**" if row.get("vacuous") else "") + "）")
        print(f"[{name}] {status}{extra}")
        if status == "NOT_EVALUATED":
            print(f"        └ {row['reason']}")
        if name == "C-2":
            for violation in row.get("observed", []):
                print(f"        └ {violation['check']} {violation['key']} ← {violation['evidence'][:2]}")
        if name == "C-4":
            for item in row.get("out_of_scope", []):
                print(f"        └ 范围外（D-2 清单类产物，不判定）：{item}")
            print(f"        └ 冻结记录扫描根（作用域声明；根外的记录不可见）：{row.get('freeze_scope')}")
            for item in row.get("freeze_exempt", []):
                print(f"        └ 载体自冻结豁免（D-2 清单类产物；原 FAIL-2026-09-20-05 的"
                      f"C-4_PIN_FILE_UNFROZEN 已知误报项）：{item}")
            for item in row.get("required_missing", []):
                print(f"        └ 必需钉值缺失（allow-list，QA 条件 C-4 / TL 条件 A3-1）：{item}")
    if report.get("missing_required_inputs"):
        print(f"[输入] 必需钉值文件缺失 ⇒ **未进入任何解析**（fail-closed，A3-1/A3-2）："
              f"{report['missing_required_inputs']}")
    if report.get("failures"):
        for item in report["failures"]:
            print(f"onto1-namespace-collision: FAIL: {item}", file=sys.stderr)
    print(f"[范围] 退役门覆盖：{report.get('refirement_gate_scope')}；"
          f"**不覆盖**：{report.get('not_covered')}（禁止把本脚本绿表述为退役门通过）")
    if report.get("result") == "INCOMPLETE":
        print("onto1-namespace-collision: INCOMPLETE "
              f"（{','.join(report.get('not_evaluated', []))} 未判定 ⇒ **不得计为通过**；"
              "解除需 D3 签署根域后重跑）")
    elif report.get("result") == "PASS":
        print("onto1-namespace-collision: PASS")
    else:
        print(f"onto1-namespace-collision: FAIL（{len(report.get('failures', []))} 项）⇒ 阻断发布")


def build_sandbox(base: Path) -> dict:
    """构造 /tmp 沙箱：仅 sandbox 模式允许出现具体根域与占位 TLD。

    目录布局与真实仓**同构**：受控制品在 `specs/semantic/**`，清单类侧车与清单类被钉制品在
    `loops/ONTO1-ontology-split/evidence/**`（形态分别对齐真实仓的
    `baseline-v2-manifest.json` 与 `consumer-scan-manifest.json`）。
    因此 D-2 的 C-4 范围判定在沙箱与真实仓走**同一条**代码路径。
    """
    (base / "specs/semantic").mkdir(parents=True, exist_ok=True)
    (base / "specs/data").mkdir(parents=True, exist_ok=True)
    (base / "specs/knowledge-architecture/instances/product").mkdir(parents=True, exist_ok=True)
    (base / "evidence").mkdir(parents=True, exist_ok=True)
    (base / "docs/architecture").mkdir(parents=True, exist_ok=True)
    loop_ev = base / "loops/ONTO1-ontology-split/evidence"
    loop_ev.mkdir(parents=True, exist_ok=True)

    core = ROOT / "specs/semantic/gits-core.owl.ttl"
    shutil.copyfile(core, base / "specs/semantic/gits-core.owl.ttl")
    shutil.copyfile(ROOT / "specs/data/customer-source-mapping.r2rml.ttl",
                    base / "specs/data/customer-source-mapping.r2rml.ttl")
    legacy_ns, _ = legacy_namespace(ROOT)
    # 沙箱的 products.ttl = **修复后**形态（前缀对齐），仅 TTL 源保留一个实例行
    (base / "specs/knowledge-architecture/instances/product/products.ttl").write_text(
        f"@prefix gits: <{legacy_ns}> .\n@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n\n"
        "gits:prod_cb_001\n  a gits:Product ;\n  rdfs:label \"沙箱实例\" .\n", encoding="utf-8")

    def write_manifest(path: Path, new_root: str) -> None:
        rows = [{"termId": "Task", "新IRI草案(未发布)": f"{new_root}Task"}]
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["termId", "新IRI草案(未发布)"])
            writer.writeheader()
            writer.writerows(rows)

    manifest = base / "evidence/manifest.csv"
    write_manifest(manifest, "https://ns-l1.onto.invalid/v1#")
    registry = base / "evidence/registry.json"
    registry.write_text(json.dumps({"defects": []}, ensure_ascii=False, indent=2), encoding="utf-8")
    signature = base / "docs/architecture/ADR-ONTO1-namespace-neutral-iri-SIGNED.md"
    signature.write_text("沙箱签署占位（仅 /tmp）\n", encoding="utf-8")

    # 侧车 #1：形态对齐真实仓 `baseline-v2-manifest.json`
    # （一个**受控**被钉制品 + 一个 D-2 范围外的清单类被钉制品；路径逐字对齐 REQUIRED_PINS）
    attribution = loop_ev / "attribution-45-v2.csv"
    attribution.write_text("termId,file\nTask,specs/semantic/gits-core.owl.ttl\n", encoding="utf-8")
    pins = loop_ev / "baseline-v2-manifest.json"
    pins.write_text(json.dumps({
        "baseline": {"file": "specs/semantic/gits-core.owl.ttl",      # 受控（D-2①）
                     "sha256": sha256(base / "specs/semantic/gits-core.owl.ttl")},
        "attribution_csv": "loops/ONTO1-ontology-split/evidence/attribution-45-v2.csv",
        "attribution_sha256": sha256(attribution),                    # D-2 范围外（清单类产物）
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    # 侧车 #2：形态对齐真实仓 `consumer-scan-manifest.json` —— **含 `generated_at`**
    # （每次重跑即变 ⇒ 当钉值必然产生"每次重跑即漂移"的噪声 FAIL，正是 FAIL-2026-09-20-05 的根因）
    hits = loop_ev / "consumer-scan-hits.jsonl"
    hits.write_text('{"term":"Task"}\n', encoding="utf-8")
    summary = loop_ev / "consumer-scan-summary.csv"
    summary.write_text("term,hits\nTask,1\n", encoding="utf-8")
    scan_pins = loop_ev / "consumer-scan-manifest.json"
    scan_pins.write_text(json.dumps({
        "generated_at": "2026-09-20T00:00:00+00:00",
        "hits_file": "loops/ONTO1-ontology-split/evidence/consumer-scan-hits.jsonl",
        "hits_sha256": sha256(hits),
        "summary_file": "loops/ONTO1-ontology-split/evidence/consumer-scan-summary.csv",
        "summary_sha256": sha256(summary),
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"manifest": manifest, "registry": registry, "signature": signature, "pins": pins,
            "scan_pins": scan_pins, "loop_evidence": loop_ev, "write_manifest": write_manifest}


def run(root: Path, sandbox: bool, manifest: Path, registry: Path, signature: Path,
        pins: Path, scan_pins: Path, freeze_root: Path | None = None) -> dict:
    """执行检查。**任何缺输入/不可解析都收敛为具名 FAIL 报告，绝不向上抛异常**（A3-2）。"""
    try:
        return check(root, manifest, registry, signature, pins, scan_pins, sandbox, freeze_root)
    except (RuntimeError, OSError, ValueError, json.JSONDecodeError) as exc:
        report = {"root": str(root), "sandbox": sandbox, "checks": {},
                  "failures": [f"SETUP: {exc}"]}
        report.update(_empty_report_tail())
        return report


def selftest() -> int:
    failures: list[str] = []
    tmp = Path(tempfile.mkdtemp(prefix="onto1-ns-collision-selftest-"))
    sandbox_root = tmp / "sandbox"
    sandbox_root.mkdir(parents=True)
    bind = build_sandbox(sandbox_root)
    freeze_dir = bind["loop_evidence"]

    def case(name: str, expect: int, expect_code: str | None = None, **kwargs) -> dict:
        report = run(root=kwargs.pop("root", sandbox_root), sandbox=kwargs.pop("sandbox", True),
                     manifest=kwargs.pop("manifest", bind["manifest"]),
                     registry=kwargs.pop("registry", bind["registry"]),
                     signature=kwargs.pop("signature", bind["signature"]),
                     pins=kwargs.pop("pins", bind["pins"]),
                     scan_pins=kwargs.pop("scan_pins", bind["scan_pins"]),
                     freeze_root=kwargs.pop("freeze_root", freeze_dir))
        ok = report["exit_code"] == expect
        if expect_code is not None:
            ok = ok and any(expect_code in item for item in report["failures"])
        print(f"{'PASS' if ok else 'FAIL'}  {name}  exit={report['exit_code']} "
              f"result={report['result']}")
        if not ok:
            failures.append(name)
        return report

    # M0 对照：沙箱全绿 ⇒ PASS
    # （C-4：受控制品钉值一致；两个清单类侧车属 D-2 范围外 ⇒ 不判定、不要求自身冻结）
    case("M0 对照：沙箱（根域已填 + 已签署 + 登记为空 + 受控钉值一致）⇒ PASS", 0)

    # M1 新旧集合不互斥：把新 IRI 设成旧 IRI 本身
    legacy_ns, _ = legacy_namespace(ROOT)
    m1 = tmp / "m1.csv"
    bind["write_manifest"](m1, legacy_ns)
    case("M1 新 IRI == 旧 IRI ⇒ C-1b FAIL", 2, "C-1b", manifest=m1)

    # M2 新增未登记的前缀碰撞
    m2_ttl = sandbox_root / "specs/data/extra-collision.ttl"
    m2_ttl.write_text(f"@prefix gits: <https://third.invalid/core#> .\ngits:x a gits:Product .\n",
                      encoding="utf-8")
    case("M2 第三命名空间绑定同一前缀且未登记 ⇒ C-2 FAIL", 2, "C-2")
    m2_ttl.unlink()

    # M3 陈旧登记：登记一个不存在的缺陷
    m3 = tmp / "m3-registry.json"
    m3.write_text(json.dumps({"defects": [{"check": "C-2a", "key": "prefix=zz;namespaces=a,b",
                                           "owner": "x", "removal_condition": "y"}]},
                             ensure_ascii=False), encoding="utf-8")
    case("M3 陈旧登记（缺陷已消失但登记未撤）⇒ C-2 FAIL", 2, "C-2", registry=m3)

    # M4 同一 series 两个 versionIRI
    m4_ttl = sandbox_root / "specs/semantic/versions.ttl"
    m4_ttl.write_text(
        "@prefix gits: <" + legacy_ns + "> .\n@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
        "gits:CoreOntology a owl:Ontology ;\n  owl:versionIRI <" + legacy_ns + "0.1.0> ;\n"
        "  owl:versionIRI <" + legacy_ns + "0.2.0> .\n", encoding="utf-8")
    case("M4 同一 series 两个 versionIRI ⇒ C-3 FAIL", 2, "C-3")

    # M-元（元变异）：把 C-3 判定替换为恒 PASS ⇒ M4 必须**失去判别力**，
    # 否则说明 M4 抓的其实不是 C-3（GK-KE FAIL-2026-09-12-02「门禁空转」教训）。
    original_c3 = globals()["check_c3"]
    globals()["check_c3"] = lambda _root: {
        "status": "PASS", "reason": None, "series": {}, "ontologies": 1, "imports": 0,
        "version_iri_total": 0, "vacuous": False}
    meta = run(root=sandbox_root, sandbox=True, manifest=bind["manifest"], registry=bind["registry"],
               signature=bind["signature"], pins=bind["pins"], scan_pins=bind["scan_pins"],
               freeze_root=freeze_dir)
    globals()["check_c3"] = original_c3
    ok = meta["exit_code"] != 2
    print(f"{'PASS' if ok else 'FAIL'}  M-元 把 C-3 判定替换为恒 PASS ⇒ M4 失去判别力"
          f"（证明 M4 真在测 C-3）  exit={meta['exit_code']}")
    if not ok:
        failures.append("M-元")
    m4_ttl.unlink()

    # M5 钉值漂移（**受控**被钉制品，D-2①：specs/semantic/**）
    # 收窄后此变异仍必须 FAIL ⇒ 证明"范围收窄"没有放过受控件
    target = sandbox_root / "specs/semantic/gits-core.owl.ttl"
    original = target.read_text(encoding="utf-8")
    target.write_text(original + "\n# drift\n", encoding="utf-8")
    case("M5 受控被钉制品内容被改 ⇒ C-4 钉值漂移 FAIL", 2, "C-4")
    target.write_text(original, encoding="utf-8")

    # M6 登记表缺失 ⇒ fail-closed
    case("M6 已知缺陷登记表缺失 ⇒ C-2 FAIL（fail-closed）", 2, "C-2",
         registry=tmp / "no-such-registry.json")

    # M7 空转：旧端集合为空
    empty_root = tmp / "empty"
    shutil.copytree(sandbox_root, empty_root)
    (empty_root / "specs/semantic/gits-core.owl.ttl").write_text(
        f"@prefix gits: <{legacy_ns}> .\n@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
        "gits:CoreOntology a owl:Ontology .\n", encoding="utf-8")
    m7_manifest = tmp / "m7.csv"
    bind["write_manifest"](m7_manifest, "https://ns-l1.onto.invalid/v1#")
    empty_ev = empty_root / "loops/ONTO1-ontology-split/evidence"
    m7_pins = empty_ev / "m7-pins.json"
    m7_pins.write_text(json.dumps({
        "baseline": {"file": "specs/semantic/gits-core.owl.ttl",
                     "sha256": sha256(empty_root / "specs/semantic/gits-core.owl.ttl")},
    }, ensure_ascii=False), encoding="utf-8")
    case("M7 旧端集合为空（检查空转）⇒ C-1a FAIL", 2, "C-1a",
         root=empty_root, manifest=m7_manifest, pins=m7_pins, freeze_root=empty_ev)

    # M8 填了具体根域但缺 D3 签署件（非 sandbox 语义）
    case("M8 填具体根域但缺 D3 签署件 ⇒ FAIL", 2, "D3_SIGNATURE_REQUIRED",
         sandbox=False, signature=tmp / "no-signature.md")

    # M9 非 sandbox 模式下出现占位 TLD ⇒ 具名拒绝
    case("M9 非 sandbox 模式出现 .invalid 占位根域 ⇒ PLACEHOLDER_ROOT_REJECTED", 2,
         "PLACEHOLDER_ROOT_REJECTED", sandbox=False)

    # M10 全豁免假绿：冲突全部登记在册 ⇒ 仍必须 FAIL（规格 M-C2-2）
    conflicted = sandbox_root / "specs/knowledge-architecture/instances/product/products.ttl"
    conflicted_original = conflicted.read_text(encoding="utf-8")
    conflicted.write_text("@prefix gits: <https://other.invalid/core#> .\n"
                          "gits:prod_cb_001 a gits:Product .\n", encoding="utf-8")
    probe = run(root=sandbox_root, sandbox=True, manifest=bind["manifest"], registry=bind["registry"],
                signature=bind["signature"], pins=bind["pins"], scan_pins=bind["scan_pins"],
                freeze_root=freeze_dir)
    m10 = tmp / "m10-registry.json"
    m10.write_text(json.dumps({"defects": [
        {"check": v["check"], "key": v["key"], "owner": "GITS Owner",
         "removal_condition": "Wave 3 前缀对齐"}
        for v in probe["checks"]["C-2"]["observed"]]}, ensure_ascii=False, indent=2), encoding="utf-8")
    case("M10 全部冲突均已登记 ⇒ 仍 FAIL（登记不等于豁免 / 全豁免假绿）", 2,
         "C-2_ALL_CONFLICTS_REGISTERED_NOT_EXEMPTED", registry=m10)
    conflicted.write_text(conflicted_original, encoding="utf-8")

    # M11 钉值自引用（指纹写进被哈希文件自身 ⇒ 永不收敛，GK-KE FAIL-2026-09-12-03）
    # 注意（D-2 收窄后仍然成立）：自引用检测**与范围无关** —— 本例被钉者落在范围外
    # （`evidence/` ⇒ 清单类产物区），仍必须 FAIL，否则"范围外"会变成自引用的避风港。
    m11_root = tmp / "m11root"
    shutil.copytree(sandbox_root, m11_root)
    m11_pins = m11_root / "evidence/pins.json"
    m11_pins.write_text(json.dumps({
        "baseline": {"file": "evidence/pins.json", "sha256": "0" * 64},   # 自引用：被钉者 == 侧车
        "attribution_csv": "specs/semantic/gits-core.owl.ttl",            # 保留受控条目（避免与 M13b 空转规则混淆）
        "attribution_sha256": sha256(m11_root / "specs/semantic/gits-core.owl.ttl"),
    }, ensure_ascii=False), encoding="utf-8")
    case("M11 钉值文件自身被钉值（自引用）⇒ C-4_SELF_REFERENCE FAIL", 2,
         "C-4_SELF_REFERENCE", root=m11_root, pins=m11_pins,
         freeze_root=m11_root / "loops/ONTO1-ontology-split/evidence")

    # M12（按 D-2 收窄**同步调整**，未删除）：钉值载体自身未被独立冻结 ⇒ "改钉值即可通过"。
    # 收窄后的口径：载体须落在**受控范围**才被 C-4b 管辖；清单类侧车不再要求自身冻结
    # （那是噪声 FAIL 的根因），但受控载体一旦未冻结，断言照旧生效。
    m12_root = tmp / "m12root"
    shutil.copytree(sandbox_root, m12_root)
    m12_pins = m12_root / "specs/semantic/pins.json"          # 受控载体（specs/semantic/** ⇒ D-2①）
    m12_pins.write_text(
        (bind["pins"]).read_text(encoding="utf-8"), encoding="utf-8")
    m12_freeze = m12_root / "loops/ONTO1-ontology-split/evidence"   # 冻结扫描根（C-3 口径）
    case("M12 受控钉值载体无独立冻结记录 ⇒ C-4_PIN_FILE_UNFROZEN FAIL", 2,
         "C-4_PIN_FILE_UNFROZEN", root=m12_root, pins=m12_pins, freeze_root=m12_freeze)
    # M12 对照（restore ⇒ PASS）：记录**落在扫描根内** ⇒ 同一配置必须转绿（双向验证有牙齿）
    (m12_freeze / "FREEZE.md").write_text(
        f"# 受控钉值载体冻结记录（夹具）\nspecs/semantic/pins.json sha256: {sha256(m12_pins)}\n",
        encoding="utf-8")
    m12_ok = run(root=m12_root, sandbox=True, manifest=bind["manifest"], registry=bind["registry"],
                 signature=bind["signature"], pins=m12_pins, scan_pins=bind["scan_pins"],
                 freeze_root=m12_freeze)
    ok = m12_ok["exit_code"] == 0
    print(f"{'PASS' if ok else 'FAIL'}  M12 对照：记录落在扫描根内 ⇒ PASS（restore ⇒ PASS）"
          f"  exit={m12_ok['exit_code']} result={m12_ok['result']}")
    if not ok:
        failures.append("M12 对照")

    # M12b（**新增**，QA 条件 C-3 / F-3 复现）：同一份冻结记录写在**扫描根之外**
    # （Loop 根目录 `EVIDENCE.md` 形态——真实仓曾经的写法）⇒ 判据**看不见** ⇒ 仍 FAIL。
    # 证明"判据的作用域必须覆盖声明的存放位置"，且**不得**用"在根外补一行声明"消掉该 FAIL。
    m12b_root = tmp / "m12broot"
    shutil.copytree(sandbox_root, m12b_root)
    m12b_pins = m12b_root / "specs/semantic/pins.json"          # 受控载体（与 M12 同形）
    m12b_pins.write_text((bind["pins"]).read_text(encoding="utf-8"), encoding="utf-8")
    # 冻结记录**确实存在**，但写在**扫描根之外**（Loop 根目录的 `EVIDENCE.md` 形态）
    (m12b_root / "EVIDENCE.md").write_text(
        f"# 冻结记录（夹具；刻意写在扫描根之外）\n"
        f"specs/semantic/pins.json sha256: {sha256(m12b_pins)}\n", encoding="utf-8")
    case("M12b 冻结记录写在扫描根之外（Loop 根 EVIDENCE.md 形态）⇒ 仍 FAIL（复现 F-3）", 2,
         "C-4_PIN_FILE_UNFROZEN", root=m12b_root, pins=m12b_pins,
         freeze_root=m12b_root / "loops/ONTO1-ontology-split/evidence")

    # M13（**新增**，D-2 的反向证明）：**取消收窄** —— 把清单类产物放回 C-4 扫描集
    # （让 `pin_scope` 对一切路径判 controlled）⇒ 旧噪声 FAIL 必须**复现**。
    # 证明两点：① 被消除的 FAIL 确实是"断言范围过宽"造成的噪声；② C-4b 断言仍在
    # （收窄是定向范围纠正，**不是删断言换绿**）。
    original_scope = globals()["pin_scope"]
    globals()["pin_scope"] = lambda _root, _path: "controlled"     # 取消收窄：清单类产物进扫描集
    case("M13 取消 D-2 收窄（清单类产物放进 C-4 扫描集）⇒ FAIL（旧噪声复现）", 2,
         "C-4_PIN_FILE_UNFROZEN")
    globals()["pin_scope"] = original_scope

    # M13b（**新增**）：**收窄不得收窄到空** —— 侧车只声明 D-2 范围外的清单类产物
    # ⇒ 受控条目 0 ⇒ 必须 FAIL（否则"收窄"可被用来把 C-4 变成恒绿）。
    # 注：本例同时违反"必需钉值 allow-list"（baseline 被删）⇒ 两条独立防线同时生效。
    m13b_root = tmp / "m13broot"
    shutil.copytree(sandbox_root, m13b_root)
    m13b_ev = m13b_root / "loops/ONTO1-ontology-split/evidence"
    m13b_pins = m13b_ev / "baseline-v2-manifest.json"
    m13b_pins.write_text(json.dumps({
        "attribution_csv": "loops/ONTO1-ontology-split/evidence/attribution-45-v2.csv",
        "attribution_sha256": sha256(m13b_ev / "attribution-45-v2.csv"),
    }, ensure_ascii=False), encoding="utf-8")
    case("M13b 受控钉值条目为 0（全部在 D-2 范围外）⇒ C-4_NO_CONTROLLED_PIN FAIL（收窄到空即 FAIL）",
         2, "C-4_NO_CONTROLLED_PIN", root=m13b_root, pins=m13b_pins,
         scan_pins=m13b_ev / "consumer-scan-manifest.json", freeze_root=m13b_ev)

    # M15（**新增**，QA 反例 E3 / QA 条件 C-4）：**删除一条必需钉值**（范围外的"消费命中"）。
    # 旧实现的"内容层 0 失败"根因：该声明本就在 D-2 范围外 ⇒ 删掉后完全不可见。
    # 现在由 REQUIRED_PINS allow-list 拦下 ⇒ 必须 FAIL。
    m15_root = tmp / "m15root"
    shutil.copytree(sandbox_root, m15_root)
    m15_ev = m15_root / "loops/ONTO1-ontology-split/evidence"
    m15_scan = m15_ev / "consumer-scan-manifest.json"
    m15_scan_original = m15_scan.read_text(encoding="utf-8")
    m15_scan_data = json.loads(m15_scan_original)
    m15_scan_data.pop("hits_file", None)
    m15_scan_data.pop("hits_sha256", None)
    m15_scan.write_text(json.dumps(m15_scan_data, ensure_ascii=False, indent=2), encoding="utf-8")
    m15_pins = m15_ev / "baseline-v2-manifest.json"
    case("M15 删除必需钉值（范围外/消费命中）⇒ C-4_REQUIRED_PIN_MISSING FAIL（QA 反例 E3）", 2,
         "C-4_REQUIRED_PIN_MISSING", root=m15_root, pins=m15_pins, scan_pins=m15_scan,
         freeze_root=m15_ev)
    # M15 对照（restore ⇒ PASS）：恢复该必需钉值 ⇒ 同一配置必须转绿
    m15_scan.write_text(m15_scan_original, encoding="utf-8")
    m15_ok = run(root=m15_root, sandbox=True, manifest=bind["manifest"], registry=bind["registry"],
                 signature=bind["signature"], pins=m15_pins, scan_pins=m15_scan, freeze_root=m15_ev)
    ok = m15_ok["exit_code"] == 0
    print(f"{'PASS' if ok else 'FAIL'}  M15 对照：恢复必需钉值 ⇒ PASS（restore ⇒ PASS）"
          f"  exit={m15_ok['exit_code']} result={m15_ok['result']}")
    if not ok:
        failures.append("M15 对照")

    # M15b（**新增**）：删除**受控**必需钉值（`baseline`）⇒ 必须 FAIL。
    # 这是"收窄过度"的最危险形态：受控制品从钉值集合里静默消失（QA E3 的原型）。
    m15b_root = tmp / "m15broot"
    shutil.copytree(sandbox_root, m15b_root)
    m15b_pins = m15b_root / "loops/ONTO1-ontology-split/evidence/baseline-v2-manifest.json"
    m15b_data = json.loads(m15b_pins.read_text(encoding="utf-8"))
    m15b_data.pop("baseline", None)
    m15b_pins.write_text(json.dumps(m15b_data, ensure_ascii=False, indent=2), encoding="utf-8")
    case("M15b 删除受控必需钉值（baseline）⇒ C-4_REQUIRED_PIN_MISSING FAIL", 2,
         "C-4_REQUIRED_PIN_MISSING", root=m15b_root, pins=m15b_pins,
         scan_pins=m15b_root / "loops/ONTO1-ontology-split/evidence/consumer-scan-manifest.json",
         freeze_root=m15b_root / "loops/ONTO1-ontology-split/evidence")

    # M15c（**新增**，TL 退回条件 A3-1 / TL 沙箱 M-C）：删除必需钉值的**文件**（范围外的消费汇总）。
    # 声明仍在、文件没了 ⇒ 必须具名 FAIL（TL 实证：只断言声明时仍误报"allow-list 4/4 PASS"）。
    m15c_root = tmp / "m15croot"
    shutil.copytree(sandbox_root, m15c_root)
    m15c_ev = m15c_root / "loops/ONTO1-ontology-split/evidence"
    m15c_summary = m15c_ev / "consumer-scan-summary.csv"
    m15c_summary_original = m15c_summary.read_text(encoding="utf-8")
    m15c_summary.unlink()
    case("M15c 删除必需钉值**文件**（范围外）⇒ C-4_REQUIRED_PIN_MISSING FAIL（A3-1 / M-C）", 2,
         "C-4_REQUIRED_PIN_MISSING", root=m15c_root,
         pins=m15c_ev / "baseline-v2-manifest.json",
         scan_pins=m15c_ev / "consumer-scan-manifest.json", freeze_root=m15c_ev)
    # M15c 对照（restore ⇒ PASS）：恢复文件 ⇒ 同一配置必须转绿
    m15c_summary.write_text(m15c_summary_original, encoding="utf-8")
    m15c_ok = run(root=m15c_root, sandbox=True, manifest=bind["manifest"], registry=bind["registry"],
                  signature=bind["signature"], pins=m15c_ev / "baseline-v2-manifest.json",
                  scan_pins=m15c_ev / "consumer-scan-manifest.json", freeze_root=m15c_ev)
    ok = m15c_ok["exit_code"] == 0
    print(f"{'PASS' if ok else 'FAIL'}  M15c 对照：恢复必需钉值文件 ⇒ PASS（restore ⇒ PASS）"
          f"  exit={m15c_ok['exit_code']} result={m15c_ok['result']}")
    if not ok:
        failures.append("M15c 对照")

    # M15d（**新增**，TL 退回条件 A3-2 / TL 沙箱 M-B）：删除**受控**必需钉值文件（基线本体）
    # ⇒ 由「输入存在性闸门」给出**具名 FAIL**、exit=2，且**不得崩溃**
    # （旧实现在 `emit()` 抛 `KeyError: 'refirement_gate_scope'`）。
    m15d_root = tmp / "m15droot"
    shutil.copytree(sandbox_root, m15d_root)
    m15d_ev = m15d_root / "loops/ONTO1-ontology-split/evidence"
    (m15d_root / "specs/semantic/gits-core.owl.ttl").unlink()
    m15d = case("M15d 删除受控必需钉值文件（基线本体）⇒ 具名 FAIL 且不崩溃（A3-2 / M-B）", 2,
                "C-4_REQUIRED_PIN_MISSING", root=m15d_root,
                pins=m15d_ev / "baseline-v2-manifest.json",
                scan_pins=m15d_ev / "consumer-scan-manifest.json", freeze_root=m15d_ev)
    if not m15d.get("missing_required_inputs"):
        print("FAIL  M15d 未走「输入存在性闸门」（missing_required_inputs 为空）")
        failures.append("M15d 输入闸门")

    # M14（原 M13，本会话按序重编号；**未删除**）未判定 ≠ 通过：
    # 根域未填（全占位）而其余可判定项全绿 ⇒ INCOMPLETE（exit 3，不是 0）
    m14 = tmp / "m14.csv"
    with m14.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["termId", "新IRI草案(未发布)"])
        writer.writeheader()
        writer.writerow({"termId": "Task", "新IRI草案(未发布)": "PENDING:{NS-L3}#Task"})
    m14_report = case("M14 根域未填（全占位）⇒ C-1b NOT_EVALUATED ⇒ INCOMPLETE（不是 PASS）", 3,
                      manifest=m14)
    if "C-1b" not in m14_report.get("not_evaluated", []):
        print("FAIL  M14 未把 C-1b 标为 NOT_EVALUATED")
        failures.append("M14 未判定标注")

    # M0b 对照（**2026-09-21 更新**，Owner 授权 C-2 兼容修复后）：
    # 真实仓现为 C-2 实测 0 处 + C-1b 未判定 ⇒ **INCOMPLETE（exit 3）**，**绝不是 PASS**。
    # 断言强度**不降**（仅按新事实收紧）：
    #   ① 不得为 PASS（exit 必须 3、result 必须 INCOMPLETE；若变 exit 0/PASS 即 FAIL）；
    #   ② **C-2 实测必须为 0**（冲突若回归，本对照立即 FAIL —— 比原来"必须等于 2 处"更有牙）；
    #   ③ C-1b 必须仍标未判定（D3 未签 ⇒ 不得把整体算作通过）；
    #   ④ C-4 噪声 FAIL 已消除且必需钉值 allow-list 齐备。
    real = run(root=ROOT, sandbox=False, manifest=DEFAULT_MANIFEST, registry=DEFAULT_REGISTRY,
               signature=DEFAULT_SIGNATURE, pins=DEFAULT_PINS, scan_pins=DEFAULT_SCAN_PINS)
    real_c4 = real["checks"].get("C-4", {})
    real_c2 = real["checks"].get("C-2", {})
    ok = (real["exit_code"] == 3 and real["result"] == "INCOMPLETE"
          and len(real_c2.get("observed", [])) == 0
          and "C-1b" in real.get("not_evaluated", [])
          and not any(item.startswith("C-2") for item in real["failures"])
          and not any(item.startswith("C-4") for item in real["failures"])
          and not real_c4.get("required_missing"))
    print(f"{'PASS' if ok else 'FAIL'}  M0b 对照：真实仓 = INCOMPLETE（C-2 实测 0 处 + C-1b 未判定）、"
          f"C-4 噪声 FAIL 已消除、必需钉值 "
          f"{real_c4.get('required_total', 0) - len(real_c4.get('required_missing', []))}"
          f"/{real_c4.get('required_total', 0)} 齐备、**绝不是 PASS**  "
          f"exit={real['exit_code']} result={real['result']}")
    if not ok:
        failures.append("M0b 对照")

    shutil.rmtree(tmp, ignore_errors=True)
    if failures:
        print(f"onto1-namespace-collision-selftest: FAIL {failures}", file=sys.stderr)
        return 2
    print("onto1-namespace-collision-selftest: PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", action="store_true")
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--json", action="store_true", help="额外输出机读报告")
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--sandbox", action="store_true")
    parser.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    parser.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    parser.add_argument("--signature", default=str(DEFAULT_SIGNATURE))
    parser.add_argument("--pins", default=str(DEFAULT_PINS))
    parser.add_argument("--scan-pins", default=str(DEFAULT_SCAN_PINS))
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    report = run(Path(args.root), args.sandbox, Path(args.manifest), Path(args.registry),
                 Path(args.signature), Path(args.pins), Path(args.scan_pins))
    emit(report)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, default=str))
    return report["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
