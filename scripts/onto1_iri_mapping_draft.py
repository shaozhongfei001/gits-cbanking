#!/usr/bin/env python3
"""ONTO1 WI-A4｜旧 IRI → 新 IRI 映射**草案**与语义关系分类（决策包输入，**不发布任何 IRI**）。

用途：把 `evidence/attribution-45-v2.csv`（87 行 / 45 模型资产）逐行转成"迁移可判定"的三列
—— `旧 IRI(LEGACY, 只读)`、`新 IRI 草案(未发布)`、`语义关系` —— 并给出该关系**允许/禁止**的绑定。

## 语义关系判定表（ADR-ONTO1 §5.1 三分法 + 复审包 04 号 §D；顺序即优先级，先命中先返回）

| # | 语义关系 | 判据（全部为"且"） | 允许绑定 | 禁止 |
|---|---|---|---|---|
| 1 | `DEPRECATED` | `生命周期 == 退役RETIRED`（当前仅 `customerId`） | `owl:deprecated` + `dcterms:isReplacedBy` 指向替代模式 | `equivalent*` |
| 2 | `NEW_TERM_NO_LEGACY_IRI` | 无 `←gits:` 旧 IRI（净新增术语） | 不建 old→new 映射（无旧端） | 伪造旧端 |
| 3 | `TRANSFORMED` | `兼容性等级 == major转制品`（源 OWL 类/属性 → Schema 对象 / SKOS 概念体系 / L4 Schema 字段） | 注册表 **RDF 投影**保持图查询 | OWL 等价（不同构） |
| 4 | `REMODELED` | 短名改变 ∨ `兼容性等级 ∈ {major改名, major重构}` ∨ 域/值域变更标记（`改指`/`指向L1`/`适配`/`修正`） | SKOS `closeMatch`；`exactMatch` **需 Owner 书面确认（当前 NOT_GRANTED）** | **`equivalent*`（硬约束）** |
| 5 | `RETAINED_AUTHORITY_MOVED` | `兼容性等级 == major迁移` ∧ 短名未变 ∧ 无域/值域变更标记 | `equivalent*`（**仅在"权威层迁移 ≠ 语义变更"经 TL 显式裁定后**） | 默认放行等价（须裁定） |
| 6 | `RETAINED` | `兼容性等级 == 不变` ∧ 短名未变 ∧ 口径同类 ∧ 无域/值域变更标记 | `owl:equivalentClass` / `owl:equivalentProperty` | — |
| — | 未命中以上任何一条 | 分类器未知情形 | — | **FAIL（fail-closed，不静默归类）** |

## 红线（本脚本内建，触发即 FAIL）

- **R1 占位根域**：`新 IRI 草案` 只允许 `PENDING:{NS-L*}` / `REGISTRY:` / `SKOS:` / `RETIRED:`
  四种形态；出现任何 `http(s)://` 字面量（含 `.example` / `localhost`）⇒ FAIL。
  （D3 未签署前，根域**不得**出现在任何制品中。）
- **R2 重构项等价化**：非 `RETAINED*` 行的 `equivalentClass/equivalentProperty 可用性` 必须为
  `FORBIDDEN` —— 人类编辑产物同样受此校验（`--gate` 会**从磁盘重读产物**再判，防分类器自证清白）。
- **R3 计数锚定**：87 行 / 45 模型资产 / 迁移域 67（32 类 + 34 对象属性 + 1 数据属性）/
  六类关系计数 32/4/23/7/1/20 —— 任一不符即 FAIL（防"删行后仍报绿"）。
- **R4 映射唯一**：旧 IRI 与新 IRI 草案各自在草案内**至多出现一次**（C-1 的前置条件）。
- **R5 非同构硬约束**：`制品类型转换 == 是` 的行**无论关系标签为何**一律 `FORBIDDEN`
  （`CapabilityPublication` 同时命中"重构"与"制品类型转换"，其等价禁用由**两重理由**支撑，
  证据列仍按 `兼容性等级` 归类为 `REMODELED` —— 分类以证据为准，禁用取并集）。

产物：
- `loops/ONTO1-ontology-split/evidence/iri-mapping-draft.csv`
- `loops/ONTO1-ontology-split/evidence/iri-mapping-draft-summary.json`
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
ATTR_CSV = ROOT / "loops/ONTO1-ontology-split/evidence/attribution-45-v2.csv"
BASELINE_TTL = ROOT / "specs/semantic/gits-core.owl.ttl"
R2RML_TTL = ROOT / "specs/data/customer-source-mapping.r2rml.ttl"
OUT_CSV = ROOT / "loops/ONTO1-ontology-split/evidence/iri-mapping-draft.csv"
OUT_SUMMARY = ROOT / "loops/ONTO1-ontology-split/evidence/iri-mapping-draft-summary.json"

LEGACY_PREFIX = "gits"
EXPECTED_ROWS = 87
EXPECTED_MODEL_ASSETS = 45
EXPECTED_MIGRATION_SCOPE = 67
EXPECTED_RELATION_COUNTS = {
    "RETAINED": 32,
    "RETAINED_AUTHORITY_MOVED": 4,
    "REMODELED": 23,
    "TRANSFORMED": 7,
    "DEPRECATED": 1,
    "NEW_TERM_NO_LEGACY_IRI": 20,
}
RELATIONS = tuple(EXPECTED_RELATION_COUNTS)
FORBIDS_EQUIVALENT = {"REMODELED", "TRANSFORMED", "DEPRECATED"}
ALLOWS_EQUIVALENT = {"RETAINED", "RETAINED_AUTHORITY_MOVED"}
OWL_TARGETS = {"OWL类", "OWL对象属性"}
NON_OWL_TARGETS = {"集成契约Schema对象", "L4 Schema字段(不再是OWL属性)", "SKOS概念体系"}
CHANGE_TOKENS = ("改指", "指向L1", "适配", "修正")
RENAME_LEVELS = {"major改名", "major重构"}
ALLOWED_NEW_IRI_SCHEMES = ("PENDING:{NS-L", "REGISTRY:", "SKOS:", "RETIRED:", "SCHEMA-FIELD:")
PLACEHOLDER_HINTS = (".example", "example.com", "localhost", "127.0.0.1", "://")

BINDING = {
    "RETAINED": "owl:equivalentClass / owl:equivalentProperty（ALLOWED）",
    "RETAINED_AUTHORITY_MOVED": "owl:equivalentClass / owl:equivalentProperty（ALLOWED，须先经 TL 裁定『权威层迁移≠语义变更』）",
    "REMODELED": "SKOS closeMatch（默认）；exactMatch 需公共语义 Owner 书面确认（当前 NOT_GRANTED）",
    "TRANSFORMED": "注册表 RDF 投影；不建 OWL 等价",
    "DEPRECATED": "owl:deprecated + dcterms:isReplacedBy → SourceIdentifier 模式",
    "NEW_TERM_NO_LEGACY_IRI": "不适用（无旧端，不建立 old→new 映射）",
}

RISK = {
    "RETAINED": "无（定义/域值域/基数/时间语义均未变）",
    "RETAINED_AUTHORITY_MOVED": "权威层迁移（L3→L1/L2）；扩展定义未变，但发布权威变更 —— 若 TL 裁定迁移本身即语义变更，须降级 closeMatch（须显式裁定，不得默认）",
    "REMODELED": "语义收窄/改变（改名、重构或 range 改指）—— 使用 equivalent* 会把两个不同扩展永久绑定，属硬禁止项",
    "TRANSFORMED": "OWL 类/属性 与 Schema 对象/SKOS 概念**不同构**；图查询能力经注册表 RDF 投影保持，迁移期查询口径须同步验证",
    "DEPRECATED": "旧 IRI 只读；不得写入任何新制品；替代关系是 isReplacedBy（非等价）",
    "NEW_TERM_NO_LEGACY_IRI": "无旧 IRI，不产生迁移义务；SourceIdentifier 是 customerId 的替代目标（isReplacedBy 指向，非等价）",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path: Path) -> list[dict]:
    if not path.is_file():
        raise RuntimeError(f"attribution csv missing: {path}")
    with path.open(encoding="utf-8", newline="") as handle:
        rows = [row for row in csv.DictReader(handle) if row.get("termId")]
    return rows


def legacy_namespace(ttl_path: Path = BASELINE_TTL) -> str:
    """从基线本体读取 `gits:` 前缀绑定（**不硬编码命名空间**；多绑定或缺失即失败）。"""
    if not ttl_path.is_file():
        raise RuntimeError(f"baseline ontology missing: {ttl_path}")
    pattern = re.compile(rf"^@prefix\s+{LEGACY_PREFIX}:\s*<([^>]+)>\s*\.", re.MULTILINE)
    found = sorted(set(pattern.findall(ttl_path.read_text(encoding="utf-8"))))
    if len(found) != 1:
        raise RuntimeError(f"{LEGACY_PREFIX}: prefix bindings = {found} (expect exactly 1)")
    return found[0]


def legacy_term(deprecated_mapping: str) -> str | None:
    match = re.search(r"←\s*gits:([A-Za-z0-9_]+)", deprecated_mapping or "")
    return match.group(1) if match else None


def short_name(iri: str) -> str:
    tail = iri.rsplit("#", 1)[-1]
    return tail.rsplit("/", 1)[-1]


def has_change_marker(row: dict) -> bool:
    blob = f"{row.get('域/值域', '')} {row.get('来源证据', '')}"
    return any(token in blob for token in CHANGE_TOKENS)


def classify(row: dict) -> str:
    term = row["termId"]
    compat = (row.get("兼容性等级") or "").strip()
    life = (row.get("生命周期") or "").strip()
    kind = (row.get("概念类型") or "").strip()
    target = (row.get("目标制品口径") or "").strip()
    old = legacy_term(row.get("弃用映射", ""))

    if life == "退役RETIRED" or target == "退役":
        return "DEPRECATED"
    if old is None:
        return "NEW_TERM_NO_LEGACY_IRI"
    if compat == "major转制品":
        return "TRANSFORMED"
    if old != term or compat in RENAME_LEVELS or has_change_marker(row):
        return "REMODELED"
    if compat == "major迁移":
        return "RETAINED_AUTHORITY_MOVED"
    if compat == "不变" and target in OWL_TARGETS:
        return "RETAINED"
    return "UNCLASSIFIED"


def new_iri_form(new_iri: str) -> str:
    if new_iri.startswith("PENDING:{NS-"):
        return "OWL_TERM_IRI_PENDING"
    if new_iri.startswith("REGISTRY:"):
        return "REGISTRY_OBJECT_PENDING"
    if new_iri.startswith("SKOS:"):
        return "SKOS_SCHEME_PENDING"
    if new_iri.startswith("RETIRED:"):
        return "NONE_RETIRED"
    return "UNKNOWN_FORM"


def availability(relation: str) -> str:
    if relation in FORBIDS_EQUIVALENT:
        return "FORBIDDEN"
    if relation in ALLOWS_EQUIVALENT:
        return "ALLOWED（见允许绑定列的前置条件）"
    return "NOT_APPLICABLE"


def build(rows: list[dict], namespace: str) -> list[dict]:
    out: list[dict] = []
    for row in rows:
        relation = classify(row)
        term = row["termId"]
        old = legacy_term(row.get("弃用映射", ""))
        old_iri = f"{namespace}{old or term}" if relation != "NEW_TERM_NO_LEGACY_IRI" else "—（无旧端）"
        new_iri = row.get("权威IRI", "")
        out.append({
            "termId": term,
            "旧IRI(LEGACY,只读)": old_iri,
            "旧短名": old or "—",
            "新IRI草案(未发布)": new_iri,
            "新IRI形态": new_iri_form(new_iri) if relation != "NEW_TERM_NO_LEGACY_IRI" else "N/A_NEW_TERM",
            "短名变化": "是" if (old and old != term) else ("否" if old else "N/A"),
            "源制品口径": row.get("概念类型", ""),
            "目标制品口径": row.get("目标制品口径", ""),
            "兼容性等级": row.get("兼容性等级", ""),
            "语义关系": relation,
            "制品类型转换": "是" if row.get("目标制品口径", "") in NON_OWL_TARGETS else "否",
            "附加语义变更": (f"是（同时改名/重构：{old}→{term}）" if relation == "TRANSFORMED" and old != term else "否"),
            "允许绑定(草案)": BINDING.get(relation, "—"),
            "equivalentClass/equivalentProperty 可用性": availability(relation),
            "迁移生效前置": "D3 根域签署 + Wave 2 拆分授权（本行为草案，未发布、不可消费）",
            "依据": row.get("来源证据", ""),
            "风险注记": RISK.get(relation, "**分类器未命中判据表 ⇒ fail-closed**"),
        })
    return out


def validate_input(rows: list[dict], out_rows: list[dict], namespace: str) -> list[str]:
    failures: list[str] = []

    def fail(message: str) -> None:
        failures.append(message)

    if len(rows) != EXPECTED_ROWS:
        fail(f"R3 rows = {len(rows)} != {EXPECTED_ROWS}")
    assets = [r for r in rows if not r.get("概念类型", "").startswith(("OWL对象属性", "转L4 Schema字段", "退役数据属性"))]
    if len(assets) != EXPECTED_MODEL_ASSETS:
        fail(f"R3 model assets = {len(assets)} != {EXPECTED_MODEL_ASSETS}")

    counts = {relation: 0 for relation in RELATIONS}
    for row in out_rows:
        relation = row["语义关系"]
        counts[relation] = counts.get(relation, 0) + 1
    for relation, expected in EXPECTED_RELATION_COUNTS.items():
        if counts.get(relation, 0) != expected:
            fail(f"R3 {relation} = {counts.get(relation, 0)} != {expected}")
    if counts.get("UNCLASSIFIED"):
        fail(f"分类器未命中：{counts['UNCLASSIFIED']} 行 ⇒ fail-closed")

    scope = [r for r in out_rows if r["语义关系"] != "NEW_TERM_NO_LEGACY_IRI"]
    if len(scope) != EXPECTED_MIGRATION_SCOPE:
        fail(f"R3 migration scope = {len(scope)} != {EXPECTED_MIGRATION_SCOPE}")

    for row in out_rows:
        iri = row["新IRI草案(未发布)"]
        # R1 作用于**全部**行（含净新增术语）——新增术语同样不得携带具体根域
        if not iri.startswith(ALLOWED_NEW_IRI_SCHEMES):
            fail(f"R1 {row['termId']} 新 IRI 非 PENDING/REGISTRY/SKOS/RETIRED/SCHEMA-FIELD 形态：{iri}")
        lowered = iri.lower()
        if "://" in iri or any(hint in lowered for hint in PLACEHOLDER_HINTS):
            fail(f"R1 {row['termId']} 出现具体根域字面量（D3 未签期间禁止）：{iri}")
        # R5 制品类型转换 ⇒ 无论关系标签为何，一律禁用 OWL 等价（不同构）；仅约束有旧端的迁移行
        if (row["制品类型转换"] == "是"
                and row["语义关系"] != "NEW_TERM_NO_LEGACY_IRI"
                and not row["equivalentClass/equivalentProperty 可用性"].startswith("FORBIDDEN")):
            fail(f"R5 {row['termId']} 目标为 {row['目标制品口径']}（非同构）却允许 OWL 等价")

    for column in ("旧IRI(LEGACY,只读)", "新IRI草案(未发布)"):
        values = [r[column] for r in scope]
        duplicates = sorted({v for v in values if values.count(v) > 1})
        if duplicates:
            fail(f"R4 {column} 重复：{duplicates}")

    if not namespace.endswith(("/", "#")):
        fail(f"legacy namespace 形态异常（应以 / 或 # 结尾）：{namespace}")
    return failures


def validate_output(path: Path) -> list[str]:
    """**从磁盘重读产物**并独立校验 —— 防分类器"自证清白"。"""
    failures: list[str] = []

    def fail(message: str) -> None:
        failures.append(message)

    if not path.is_file():
        return [f"产物缺失：{path}"]
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        return ["产物为空（空转）"]

    counts: dict[str, int] = {}
    for row in rows:
        relation = row.get("语义关系", "")
        counts[relation] = counts.get(relation, 0) + 1
        if relation not in RELATIONS:
            fail(f"产物语义关系非法：{row.get('termId')} → {relation}")
            continue
        bind = (row.get("equivalentClass/equivalentProperty 可用性") or "").strip()
        if relation in FORBIDS_EQUIVALENT and not bind.startswith("FORBIDDEN"):
            fail(f"R2 {row.get('termId')}（{relation}）可用性 = {bind} ⇒ 禁止 equivalent*")
        if relation in ALLOWS_EQUIVALENT and not bind.startswith("ALLOWED"):
            fail(f"R2 {row.get('termId')}（{relation}）可用性 = {bind} ⇒ 应允许等价但被标为其它")
        if not (row.get("允许绑定(草案)") or "").strip():
            fail(f"R2 {row.get('termId')} 缺绑定草案")
        if ((row.get("制品类型转换") or "").strip() == "是"
                and relation != "NEW_TERM_NO_LEGACY_IRI"
                and not bind.startswith("FORBIDDEN")):
            fail(f"R5 {row.get('termId')} 制品类型已转换却未标 FORBIDDEN ⇒ 禁止 OWL 等价")
    for relation, expected in EXPECTED_RELATION_COUNTS.items():
        if counts.get(relation, 0) != expected:
            fail(f"R3 产物 {relation} = {counts.get(relation, 0)} != {expected}")
    return failures


def write_outputs(out_rows: list[dict], namespace: str, migration_scope: int,
                  out_csv: Path = OUT_CSV, out_summary: Path = OUT_SUMMARY) -> dict:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    fields = list(out_rows[0].keys())
    with out_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(out_rows)
    counts = {relation: sum(1 for r in out_rows if r["语义关系"] == relation) for relation in RELATIONS}
    summary = {
        "artifact": "iri-mapping-draft",
        "status": "DRAFT（未发布、不可消费；不构成 ADR 接受）",
        "authority": "docs/architecture/ADR-ONTO1-namespace-neutral-iri-DRAFT.md §5",
        "legacy_namespace": namespace,
        "legacy_namespace_source": f"{BASELINE_TTL.relative_to(ROOT).as_posix()}:1",
        "rows": len(out_rows),
        "migration_scope": migration_scope,
        "new_term_without_legacy_iri": len(out_rows) - migration_scope,
        "relation_counts": counts,
        "equivalent_forbidden_relations": sorted(FORBIDS_EQUIVALENT),
        "unfilled_root": "D3 未签署 ⇒ 根域为空；全部新 IRI 保持 PENDING 形态，无 http(s) 字面量",
        "redlines": [
            "不发布新 IRI",
            "不重钉制品",
            "不退役旧 IRI",
            "不把候选/占位根域写入任何 specs/ 制品",
            "RETAINED_AUTHORITY_MOVED 的等价放行须经 TL 显式裁定（默认不放行）",
        ],
        "outputs": {
            "csv": out_csv.relative_to(ROOT).as_posix() if out_csv.is_relative_to(ROOT)
            else str(out_csv),
            "csv_sha256": sha256(out_csv),
        },
    }
    if out_summary is not None:
        out_summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


def gate(attr_csv: Path = ATTR_CSV, ttl: Path = BASELINE_TTL, write: bool = True,
         tamper=None) -> int:
    try:
        rows = read_rows(attr_csv)
        namespace = legacy_namespace(ttl)
        out_rows = build(rows, namespace)
        failures = validate_input(rows, out_rows, namespace)
    except RuntimeError as exc:
        print(f"onto1-iri-mapping: FAIL: {exc}", file=sys.stderr)
        return 2

    counts = {relation: sum(1 for r in out_rows if r["语义关系"] == relation) for relation in RELATIONS}
    scope = sum(1 for r in out_rows if r["语义关系"] != "NEW_TERM_NO_LEGACY_IRI")
    print(f"[M1] legacy namespace = {namespace}（源：{ttl.relative_to(ROOT).as_posix()}:1）")
    print(f"[M2] 迁移域={scope}  无旧端={len(out_rows) - scope}  关系计数={counts}")
    print(f"[M3] 禁止 equivalent* 的关系：{sorted(FORBIDS_EQUIVALENT)}")

    tmp_dir = Path(tempfile.mkdtemp(prefix="onto1-iri-mapping-"))
    try:
        staged = tmp_dir / "iri-mapping-draft.csv"
        write_outputs(out_rows, namespace, scope, out_csv=staged, out_summary=None)
        if tamper is not None:
            tamper(staged)
        failures += validate_output(staged)
        if failures:
            for item in failures:
                print(f"onto1-iri-mapping: FAIL: {item}", file=sys.stderr)
            return 2
        if write:
            summary = write_outputs(out_rows, namespace, scope)
            print(f"[M4] wrote {summary['outputs']['csv']} sha256={summary['outputs']['csv_sha256'][:16]}")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    print("onto1-iri-mapping: PASS")
    return 0


def selftest() -> int:
    """变异复验：每条变异必须被拦下，未变异对照必须通过。"""
    failures: list[str] = []
    tmp = Path(tempfile.mkdtemp(prefix="onto1-iri-mapping-selftest-"))
    try:
        base_rows = read_rows(ATTR_CSV)
        header = list(base_rows[0].keys())

        def write_variant(name: str, rows: list[dict]) -> Path:
            path = tmp / name
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=header)
                writer.writeheader()
                writer.writerows(rows)
            return path

        # M1 关键变异：把 REMODELED 行的等价可用性洗成 ALLOWED（模拟人类手改产物）
        def tamper_equivalence(path: Path) -> None:
            with path.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
                fields = list(rows[0].keys())
            for row in rows:
                if row["语义关系"] == "REMODELED":
                    row["equivalentClass/equivalentProperty 可用性"] = "ALLOWED（已人工确认等同）"
                    break
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields)
                writer.writeheader()
                writer.writerows(rows)

        cases: list[tuple[str, Path, object]] = []

        # M1b 删除一条基线映射行 ⇒ 迁移域 / 关系计数锚定必须 FAIL
        dropped = [r for r in base_rows if r["termId"] != "Task"]
        cases.append(("M1 删除迁移行 gits:Task ⇒ 迁移域≠67 FAIL", write_variant("drop-row.csv", dropped), None))

        # M2 把 customerId 的语义关系洗成"不变"（退役项当作保留） ⇒ 计数锚定失败
        washed = [dict(r) for r in base_rows]
        for row in washed:
            if row["termId"] == "customerId":
                row["生命周期"] = "候选CANDIDATE"
                row["目标制品口径"] = "OWL对象属性"
        cases.append(("M2 退役项 customerId 洗成候选 ⇒ DEPRECATED 计数≠1 FAIL",
                      write_variant("wash-deprecated.csv", washed), None))

        # M3 写入占位根域字面量 ⇒ R1 必须 FAIL
        rooted = [dict(r) for r in base_rows]
        for row in rooted:
            if row["termId"] == "Party":
                row["权威IRI"] = "https://ns-l1.bank.example/v1#Party"
        cases.append(("M3 新 IRI 填 bank.example 占位根域 ⇒ R1 FAIL",
                      write_variant("placeholder-root.csv", rooted), None))

        # M4 旧 IRI 一对一被破坏（两行指向同一旧术语） ⇒ R4 必须 FAIL
        duplicated = [dict(r) for r in base_rows]
        for row in duplicated:
            if row["termId"] == "Organization":
                row["弃用映射"] = "←gits:OperatingCase(LEGACY)"
        cases.append(("M4 旧 IRI 重复指向 ⇒ R4 FAIL",
                      write_variant("dup-legacy.csv", duplicated), None))

        for name, path, tamper in cases:
            code = gate(path, write=False, tamper=tamper)
            ok = code == 2
            print(f"{'PASS' if ok else 'FAIL'}  {name}  exit={code}")
            if not ok:
                failures.append(name)

        # M5 关键变异（产物侧）：把 REMODELED 的等价可用性洗成 ALLOWED ⇒ R2 必须 FAIL
        code = gate(ATTR_CSV, write=False, tamper=tamper_equivalence)
        ok = code == 2
        print(f"{'PASS' if ok else 'FAIL'}  M5 产物侧把 REMODELED 洗成 ALLOWED 等价 ⇒ R2 FAIL  exit={code}")
        if not ok:
            failures.append("M5")

        # M0 对照：未变异 ⇒ PASS
        control = gate(ATTR_CSV, write=False)
        print(f"{'PASS' if control == 0 else 'FAIL'}  M0 对照：未变异 ⇒ PASS  exit={control}")
        if control != 0:
            failures.append("M0 对照")

        if failures:
            print(f"onto1-iri-mapping-selftest: FAIL {failures}", file=sys.stderr)
            return 2
        print("onto1-iri-mapping-selftest: PASS")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--attr", default=str(ATTR_CSV))
    parser.add_argument("--ttl", default=str(BASELINE_TTL))
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    return gate(Path(args.attr), Path(args.ttl), write=not args.no_write)


if __name__ == "__main__":
    raise SystemExit(main())
