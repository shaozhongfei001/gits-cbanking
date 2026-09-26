#!/usr/bin/env python3
"""ONTO1 W-1.5 PKG-A2｜Wave 0 输入锚点就绪预检门禁（fail-closed）。

问题（`memory/PLAN-NEXT.md` §1 A2）：`memory/waves/W0-PLAN.md` 已列出「W0 开工前必须核对的输入锚点」
与失败条件，但**没有可执行门禁**——失败条件只是措辞。等 G-1 达成后才核对（复审包哈希漂移 /
映射草案过期 / ADR 未签 / 门禁位置未离开 `RETURN_TO_HLD`），窗口白白损失。
本脚本把 8 项锚点逐项判成 `READY` / `NOT_READY(<原因>)`，让失败条件在等待期就变红灯。

三种模式（**语义必须区分，否则会被误读为"全绿"**）：

    --gate      = 「**G-1 是否已满足**」= R1~R8 全部 READY 才 exit 0。
                  R6（D3 签署件）/ R7（门禁位置）在 G-1 前**必然 NOT_READY**
                  ⇒ 本模式**现在期望 FAIL（exit 2）**，并逐项列出原因。这是设计如此，不是缺陷。
    --precheck  = 「**除 R6/R7 外**全部 READY？」（等待期自查）现在**期望 PASS（exit 0）**。
    --selftest  = 变异复验（条目级断言，见文件末说明）。

八项锚点（判据来源：`memory/waves/W0-PLAN.md:15-23`、执行计划 V2.0 §2 G-1/:56 + §3/:58-62）：

    R1 复审包 01~14 逐件 sha256 与 `docs/review/ARCH-ONTO-2026-001-rereview-package/MANIFEST.md` 一致（14/14）
    R2 基线本体 `specs/semantic/gits-core.owl.ttl` sha256 前缀 705578d6324abd0c 且 rdflib 计数 32/34/1
    R3 `evidence/attribution-45-v2.csv` 存在且 45 资产分口径 39 OWL / 1 SKOS / 5 Schema 可复算
    R4 `evidence/consumer-scan-obligations.csv` 存在且 `consumer-scan-summary.csv` 中 PENDING_TRIAGE = 0
    R5 `docs/architecture/ADR-ONTO1-namespace-neutral-iri-DRAFT.md` 存在且**未预填正式根域**（WI-A4 纪律）
    R6 D3 签署件存在（**G-1 前必然 NOT_READY，设计如此**）
    R7 `LOOP.yaml.gate_state.current` 已离开 `RETURN_TO_HLD`
    R8 `STATE.json.baseline_commit` 非 `PENDING_FIRST_COMMIT`

单一真值函数 `readiness(cfg)`；`--gate` / `--precheck` / `--selftest` 全部由它派生，无第二套判据。

变异的**非空转**要求：本门禁当前本来就 FAIL（R6/R7），所以"变异后 exit==2"是**恒真断言**——
正是 GK 系列反复踩到的"假绿"形态。故 selftest 一律断言到**条目级**（`items["R1"].status`），
不用全局退出码凑数。
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
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LOOP = ROOT / "loops/ONTO1-ontology-split"

READY = "READY"
NOT_READY = "NOT_READY"

# 门禁未满足时（G-1 前）**期望**的退出码；由 record_gate.py 如实记账
EXPECTED_EXIT_BEFORE_G1 = 2

# R6/R7 是"外部动作"锚点：G-1 达成前必然未满足。--precheck 把它们排除，只查"确定性锚点"。
EXTERNAL_HELD_ITEMS = ("R6", "R7")

DEV_BLOCKING_GATE_STATE = "RETURN_TO_HLD"
PENDING_COMMIT_MARKER = "PENDING_FIRST_COMMIT"

REQUIRED_REVIEW_IDS = tuple(f"{index:02d}" for index in range(1, 15))

# R6「D3 签署件」的可接受载体（三选一）。-DRAFT 草案**不算**签署件。
D3_SIGNED_PATTERNS = (
    "ADR-ONTO1-namespace-neutral-iri.md",
    "*ADR-ONTO1*签署*",
    "*ADR-ONTO1*SIGNED*",
    "*ONTO1-D3*签署*",
)
# 签署件必须含签署痕迹，否则不计（fail-closed：空文件/改名不算签）
D3_SIGNATURE_MARKERS = ("签署人", "签署日期", "SIGNED", "Signature", "signed by")
D3_RATIFIED_MARKER = "ACCEPTED"

# R5：正式根域被"预填"的判据 = 占位变量被赋了具体 http(s) 字面量
NS_PREFILL_RE = re.compile(r"NS-L[1-4][^\n]{0,24}https?://")
NS_PLACEHOLDER = "{NS-L1}"
# 草案"自称已批准"的判据 = **本文件的状态声明值**为 ACCEPTED。
# 注意：不得用 `"ACCEPTED" in text` —— 草案正文会写「签署前**不得**转为 ACCEPTED」，
# 那是纪律陈述而非状态声明，字面包含判定会产生假阳性（本轮实测踩到）。
ADR_STATUS_ROW_RE = re.compile(r"^\s*\|\s*状态\s*\|\s*([^|\n]+)\|", flags=re.M)
ADR_STATUS_INLINE_RE = re.compile(r"^\s*状态\s*[:：]\s*([^\n]+)", flags=re.M)


@dataclass
class Cfg:
    """全部可注入（selftest 靠它做变异，无需改真实仓库）。"""

    root: Path = ROOT
    loop_dir: Path = LOOP
    package_dir: Path = ROOT / "docs/review/ARCH-ONTO-2026-001-rereview-package"
    baseline_ttl: Path = ROOT / "specs/semantic/gits-core.owl.ttl"
    baseline_sha256_prefix: str = "705578d6324abd0c"
    baseline_counts: dict[str, int] = field(
        default_factory=lambda: {"owl_class": 32, "owl_object_property": 34, "owl_datatype_property": 1}
    )
    attribution_csv: Path = LOOP / "evidence/attribution-45-v2.csv"
    obligations_csv: Path = LOOP / "evidence/consumer-scan-obligations.csv"
    summary_csv: Path = LOOP / "evidence/consumer-scan-summary.csv"
    adr_draft: Path = ROOT / "docs/architecture/ADR-ONTO1-namespace-neutral-iri-DRAFT.md"
    d3_search_dirs: tuple[Path, ...] = (ROOT / "docs/architecture", ROOT / "docs/dispatch")
    loop_yaml: Path = LOOP / "LOOP.yaml"
    state_json: Path = LOOP / "STATE.json"


@dataclass
class Item:
    id: str
    title: str
    status: str
    reason: str = ""
    evidence: str = ""

    def line(self) -> str:
        detail = self.status if not self.reason else f"{self.status}({self.reason})"
        suffix = f"  [{self.evidence}]" if self.evidence else ""
        return f"{self.id} {self.title}: {detail}{suffix}"


# --------------------------------------------------------------------------------------
# 工具
# --------------------------------------------------------------------------------------


def sha256_of(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path, root: Path) -> str:
    """展示用相对路径；沙箱（selftest）路径不在 root 下时退回绝对路径。"""
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def parse_manifest(text: str) -> dict[str, str]:
    """MANIFEST.md 表格行 → {文件名: sha256}。行格式：| # | `文件` | … | … | `sha256` |"""
    rows = re.findall(
        r"\|\s*`([^`\n]+)`\s*\|[^|\n]*\|[^|\n]*\|\s*`([0-9a-f]{64})`",
        text,
    )
    return {name.strip(): digest for name, digest in rows}


def declared_adr_status(text: str) -> str:
    """解析文档**自身状态声明**（表格行 `| 状态 | X |` 或行内 `状态: X`）的首个标识符。

    只认状态字段，不做全文包含匹配——正文的「不得转为 ACCEPTED」是纪律陈述，不是状态。
    """
    raw = ""
    match = ADR_STATUS_ROW_RE.search(text)
    if match:
        raw = match.group(1).strip()
    if not raw:
        match = ADR_STATUS_INLINE_RE.search(text)
        if match:
            raw = match.group(1).strip()
    token = re.match(r"[`\s]*([A-Za-z_]+)", raw)
    return token.group(1).upper() if token else ""


def is_adr_ratified(text: str) -> bool:
    return declared_adr_status(text) == D3_RATIFIED_MARKER


def load_structured(path: Path) -> dict[str, Any]:
    """LOOP.yaml 实为 JSON 文本（schema_version 2.0）；两种解析都试，失败即抛。"""
    text = path.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(text)
        if isinstance(data, dict):
            return data
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"cannot parse {path.name}: {exc}") from exc
    raise RuntimeError(f"cannot parse {path.name}: not a mapping")


# --------------------------------------------------------------------------------------
# 逐项判据（全部由 readiness() 调用；每条只返回 Item）
# --------------------------------------------------------------------------------------


def check_r1_review_package(cfg: Cfg) -> Item:
    manifest_path = cfg.package_dir / "MANIFEST.md"
    if not cfg.package_dir.is_dir():
        return Item("R1", "复审包 01~14 哈希", NOT_READY, f"package dir missing: {cfg.package_dir}")
    if not manifest_path.is_file():
        return Item("R1", "复审包 01~14 哈希", NOT_READY, "MANIFEST.md missing")

    registered = parse_manifest(manifest_path.read_text(encoding="utf-8"))
    registered_ids = {name[:2] for name in registered}
    missing_ids = [rid for rid in REQUIRED_REVIEW_IDS if rid not in registered_ids]
    if missing_ids:
        return Item("R1", "复审包 01~14 哈希", NOT_READY,
                    f"MANIFEST registers only {sorted(registered_ids)}, missing {missing_ids}")

    drifted: list[str] = []
    absent: list[str] = []
    for name, digest in sorted(registered.items()):
        path = cfg.package_dir / name
        if not path.is_file():
            absent.append(name)
        elif sha256_of(path) != digest:
            drifted.append(f"{name}({sha256_of(path)[:16]}!={digest[:16]})")

    verified = len([n for n in registered if (cfg.package_dir / n).is_file()
                    and sha256_of(cfg.package_dir / n) == registered[n]])
    if absent or drifted:
        return Item("R1", "复审包 01~14 哈希", NOT_READY,
                    f"MANIFEST drift: absent={absent} DRIFT={drifted}",
                    evidence=f"{rel(manifest_path, cfg.root)} (registered={len(registered)})")
    if verified != len(REQUIRED_REVIEW_IDS):
        return Item("R1", "复审包 01~14 哈希", NOT_READY,
                    f"verified {verified}/14 manifest entries")
    return Item("R1", "复审包 01~14 哈希", READY,
                evidence=f"{rel(manifest_path, cfg.root)} 14/14 sha256 match")


def check_r2_baseline(cfg: Cfg) -> Item:
    path = cfg.baseline_ttl
    if not path.is_file():
        return Item("R2", "基线本体哈希与计数", NOT_READY, f"baseline TTL missing: {path}")

    digest = sha256_of(path)
    if not digest.startswith(cfg.baseline_sha256_prefix):
        return Item("R2", "基线本体哈希与计数", NOT_READY,
                    f"sha256 prefix drift: {digest[:16]} != {cfg.baseline_sha256_prefix}")

    try:
        from rdflib import Graph
        from rdflib.namespace import OWL, RDF
    except ImportError as exc:  # fail-closed：不降级为"跳过计数"
        return Item("R2", "基线本体哈希与计数", NOT_READY, f"rdflib unavailable: {exc}")

    try:
        graph = Graph()
        graph.parse(str(path), format="turtle")
        observed = {
            "owl_class": len(list(graph.subjects(RDF.type, OWL.Class))),
            "owl_object_property": len(list(graph.subjects(RDF.type, OWL.ObjectProperty))),
            "owl_datatype_property": len(list(graph.subjects(RDF.type, OWL.DatatypeProperty))),
        }
    except Exception as exc:  # noqa: BLE001
        return Item("R2", "基线本体哈希与计数", NOT_READY, f"rdflib parse failed: {exc}")

    mismatch = {key: (observed[key], expected) for key, expected in cfg.baseline_counts.items()
                if observed[key] != expected}
    if mismatch:
        return Item("R2", "基线本体哈希与计数", NOT_READY,
                    f"count mismatch (observed,expected)={mismatch}")
    return Item("R2", "基线本体哈希与计数", READY,
                evidence=f"{rel(path, cfg.root)} sha256={digest[:16]} "
                         f"counts={observed['owl_class']}/{observed['owl_object_property']}"
                         f"/{observed['owl_datatype_property']}")


def check_r3_attribution(cfg: Cfg) -> Item:
    path = cfg.attribution_csv
    if not path.is_file():
        return Item("R3", "四层归属矩阵", NOT_READY, f"missing: {path}")
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        if "概念类型" not in fieldnames:
            return Item("R3", "四层归属矩阵", NOT_READY, "column 概念类型 missing")
        rows = list(reader)

    owl = sum(1 for row in rows if row.get("概念类型") == "OWL类")
    skos = sum(1 for row in rows if row.get("概念类型") == "SKOS概念体系")
    schema = sum(1 for row in rows if (row.get("概念类型") or "").startswith("Schema对象"))
    total = owl + skos + schema
    if (owl, skos, schema) != (39, 1, 5) or total != 45:
        return Item("R3", "四层归属矩阵", NOT_READY,
                    f"spec split (OWL,SKOS,Schema)=({owl},{skos},{schema}) total={total} "
                    "expect (39,1,5)/45")
    return Item("R3", "四层归属矩阵", READY,
                evidence=f"{rel(path, cfg.root)} rows={len(rows)} 39/1/5 recomputed")


def check_r4_consumer_scan(cfg: Cfg) -> Item:
    if not cfg.obligations_csv.is_file():
        return Item("R4", "消费者处置表", NOT_READY, f"missing: {cfg.obligations_csv}")
    with cfg.obligations_csv.open(encoding="utf-8", newline="") as handle:
        obligation_rows = sum(1 for _ in csv.DictReader(handle))
    if obligation_rows <= 0:
        return Item("R4", "消费者处置表", NOT_READY, "obligations csv is empty")

    if not cfg.summary_csv.is_file():
        return Item("R4", "消费者处置表", NOT_READY, f"missing: {cfg.summary_csv}")
    pending = 0
    with cfg.summary_csv.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        if "disposition" not in fieldnames:
            return Item("R4", "消费者处置表", NOT_READY, "summary column disposition missing")
        summary_rows = 0
        for row in reader:
            summary_rows += 1
            if any((value or "").strip() == "PENDING_TRIAGE" for value in row.values()):
                pending += 1
    if pending:
        return Item("R4", "消费者处置表", NOT_READY, f"PENDING_TRIAGE = {pending} (>0)")
    return Item("R4", "消费者处置表", READY,
                evidence=f"{cfg.obligations_csv.name} rows={obligation_rows}; "
                         f"{cfg.summary_csv.name} rows={summary_rows} PENDING_TRIAGE=0")


def check_r5_adr_draft(cfg: Cfg) -> Item:
    path = cfg.adr_draft
    if not path.is_file():
        return Item("R5", "命名空间 ADR 草案", NOT_READY, f"missing: {path}")
    text = path.read_text(encoding="utf-8")

    prefill = NS_PREFILL_RE.findall(text)
    if prefill:
        return Item("R5", "命名空间 ADR 草案", NOT_READY,
                    f"formal root domain ALREADY FILLED (D3 unsigned ⇒ forbidden): {prefill[:2]}")
    if is_adr_ratified(text):
        return Item("R5", "命名空间 ADR 草案", NOT_READY,
                    "draft self-declared ACCEPTED while unsigned")
    if NS_PLACEHOLDER not in text:
        return Item("R5", "命名空间 ADR 草案", NOT_READY,
                    "no {NS-L1} placeholder found ⇒ cannot prove root domain is unfilled")
    return Item("R5", "命名空间 ADR 草案", READY,
                evidence=f"{rel(path, cfg.root)} no formal root domain prefilled")


def check_r6_d3_signed(cfg: Cfg) -> Item:
    draft_text = cfg.adr_draft.read_text(encoding="utf-8") if cfg.adr_draft.is_file() else ""
    if is_adr_ratified(draft_text):
        return Item("R6", "D3 签署件", NOT_READY,
                    "D3 unsigned (draft claims ACCEPTED without a signed carrier)")

    found: list[str] = []
    for directory in cfg.d3_search_dirs:
        if not directory.is_dir():
            continue
        for pattern in D3_SIGNED_PATTERNS:
            for candidate in directory.glob(pattern):
                if candidate.name.endswith("-DRAFT.md") or not candidate.is_file():
                    continue
                body = candidate.read_text(encoding="utf-8", errors="replace")
                if any(marker in body for marker in D3_SIGNATURE_MARKERS):
                    found.append(rel(candidate, cfg.root))
    if not found:
        return Item("R6", "D3 签署件", NOT_READY, "D3 unsigned")
    return Item("R6", "D3 签署件", READY, evidence=f"signed carrier(s)={sorted(found)}")


def check_r7_gate_position(cfg: Cfg) -> Item:
    if not cfg.loop_yaml.is_file():
        return Item("R7", "门禁位置", NOT_READY, f"missing: {cfg.loop_yaml}")
    try:
        data = load_structured(cfg.loop_yaml)
    except RuntimeError as exc:
        return Item("R7", "门禁位置", NOT_READY, str(exc))
    current = str(data.get("gate_state", {}).get("current", "") or "")
    if not current:
        return Item("R7", "门禁位置", NOT_READY, "gate_state.current missing")
    if current == DEV_BLOCKING_GATE_STATE:
        return Item("R7", "门禁位置", NOT_READY, f"still {DEV_BLOCKING_GATE_STATE}")
    return Item("R7", "门禁位置", READY,
                evidence=f"{rel(cfg.loop_yaml, cfg.root)} gate_state.current={current}")


def check_r8_baseline_commit(cfg: Cfg) -> Item:
    if not cfg.state_json.is_file():
        return Item("R8", "基线提交记录", NOT_READY, f"missing: {cfg.state_json}")
    try:
        data = json.loads(cfg.state_json.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return Item("R8", "基线提交记录", NOT_READY, f"STATE.json unreadable: {exc}")
    commit = str(data.get("baseline_commit", "") or "")
    if not commit:
        return Item("R8", "基线提交记录", NOT_READY, "baseline_commit missing")
    if commit == PENDING_COMMIT_MARKER:
        return Item("R8", "基线提交记录", NOT_READY, f"baseline_commit = {PENDING_COMMIT_MARKER}")
    return Item("R8", "基线提交记录", READY,
                evidence=f"{rel(cfg.state_json, cfg.root)} baseline_commit={commit[:12]}")


CHECKERS = (
    check_r1_review_package,
    check_r2_baseline,
    check_r3_attribution,
    check_r4_consumer_scan,
    check_r5_adr_draft,
    check_r6_d3_signed,
    check_r7_gate_position,
    check_r8_baseline_commit,
)


# --------------------------------------------------------------------------------------
# 单一真值函数
# --------------------------------------------------------------------------------------


def readiness(cfg: Cfg | None = None) -> dict[str, Any]:
    """唯一判据来源：返回 {"items": {id: Item}, "gate_pass": bool, "precheck_pass": bool}。"""
    cfg = cfg or Cfg()
    items = [checker(cfg) for checker in CHECKERS]
    by_id = {item.id: item for item in items}
    gate_pass = all(item.status == READY for item in by_id.values())
    precheck_pass = all(item.status == READY for key, item in by_id.items()
                        if key not in EXTERNAL_HELD_ITEMS)
    return {"items": by_id, "gate_pass": gate_pass, "precheck_pass": precheck_pass}


def render(report: dict[str, Any], mode: str) -> int:
    by_id = report["items"]
    title = {
        "gate": "G-1 是否已满足（R1~R8 全 READY）",
        "precheck": "等待期自查（除 R6/R7 外全部 READY）",
    }[mode]
    print(f"onto1-wave0-readiness[{mode}] 语义：{title}")
    for key in sorted(by_id):
        print("  " + by_id[key].line())
    passed = report["gate_pass"] if mode == "gate" else report["precheck_pass"]
    if passed:
        print(f"onto1-wave0-readiness[{mode}]: PASS (exit 0)")
        return 0
    reason = ("G-1 not satisfied" if mode == "gate"
              else "non-external anchors not ready")
    print(f"onto1-wave0-readiness[{mode}]: FAIL ({reason})", file=sys.stderr)
    return EXPECTED_EXIT_BEFORE_G1


def report_payload(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "onto1_wave0_readiness/v1",
        "items": {key: {"title": item.title, "status": item.status,
                        "reason": item.reason, "evidence": item.evidence}
                  for key, item in sorted(report["items"].items())},
        "gate_pass": report["gate_pass"],
        "precheck_pass": report["precheck_pass"],
        "expected_exit_before_g1": EXPECTED_EXIT_BEFORE_G1,
    }


def gate(report_path: Path | None = None) -> int:
    report = readiness()
    if report_path is not None:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report_payload(report), ensure_ascii=False, indent=2) + "\n",
                               encoding="utf-8")
    return render(report, "gate")


def precheck(report_path: Path | None = None) -> int:
    report = readiness()
    if report_path is not None:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report_payload(report), ensure_ascii=False, indent=2) + "\n",
                               encoding="utf-8")
    return render(report, "precheck")


# --------------------------------------------------------------------------------------
# 变异复验（条目级断言，非空转）
# --------------------------------------------------------------------------------------


def selftest() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="onto1-wave0-readiness-selftest-"))
    failures: list[str] = []
    try:
        # ---------- M4 对照：真实仓库原样 ----------
        base = readiness()
        control_ok = (not base["gate_pass"]) and base["precheck_pass"]
        print(f"{'PASS' if control_ok else 'FAIL'}  M4 对照：真实仓库 ⇒ --gate FAIL / --precheck PASS"
              f"  (gate_pass={base['gate_pass']}, precheck_pass={base['precheck_pass']})")
        if not control_ok:
            failures.append("M4 对照")
        # 断言 R6/R7 是当前唯二 NOT_READY，防止"别处也坏了却当成设计如此"
        not_ready_ids = sorted(k for k, item in base["items"].items() if item.status == NOT_READY)
        only_external = not_ready_ids == sorted(EXTERNAL_HELD_ITEMS)
        print(f"{'PASS' if only_external else 'FAIL'}  M4b 对照：NOT_READY 恰为 {sorted(EXTERNAL_HELD_ITEMS)}"
              f"  (actual={not_ready_ids})")
        if not only_external:
            failures.append("M4b 对照")

        # ---------- M1 篡改 R1 一个复审包文件 ⇒ R1 必须 NOT_READY ----------
        pkg = tmp / "pkg"
        shutil.copytree(Cfg().package_dir, pkg)
        target = pkg / "01-主设计-V2.0-复审快照.md"
        target.write_text(target.read_text(encoding="utf-8") + "\n<!-- drift -->\n", encoding="utf-8")
        item = check_r1_review_package(Cfg(package_dir=pkg))
        ok1 = item.status == NOT_READY and "DRIFT" in item.reason
        print(f"{'PASS' if ok1 else 'FAIL'}  M1 篡改复审包 01 ⇒ R1 NOT_READY  ({item.reason[:72]})")
        if not ok1:
            failures.append("M1")

        # ---------- M2a 改写基线 TTL 内容（计数塌为 1 类）⇒ R2 必须 NOT_READY ----------
        ttl = tmp / "flat.ttl"
        ttl.write_text(
            "@prefix owl: <http://www.w3.org/2002/07/owl#> .\n"
            "@prefix ex: <https://gientech.com/gits/kno/> .\n"
            "ex:OnlyClass a owl:Class .\n",
            encoding="utf-8",
        )
        item = check_r2_baseline(Cfg(baseline_ttl=ttl))
        # 该沙箱 TTL 的哈希必然不等于前缀 ⇒ 也属诚信拒绝；两边任一原因都必须拦下
        ok2a = item.status == NOT_READY and ("sha256 prefix drift" in item.reason
                                             or "count mismatch" in item.reason)
        print(f"{'PASS' if ok2a else 'FAIL'}  M2a 基线 TTL 变形 ⇒ R2 NOT_READY  ({item.reason[:72]})")
        if not ok2a:
            failures.append("M2a")

        # ---------- M2b 只改"预期计数=1"（TTL 原样）⇒ 隔离证明计数断言有牙齿 ----------
        item = check_r2_baseline(Cfg(baseline_counts={"owl_class": 1, "owl_object_property": 34,
                                                      "owl_datatype_property": 1}))
        ok2b = item.status == NOT_READY and "count mismatch" in item.reason
        print(f"{'PASS' if ok2b else 'FAIL'}  M2b 预期计数改 1（TTL 原样）⇒ R2 NOT_READY  "
              f"({item.reason[:72]})")
        if not ok2b:
            failures.append("M2b")

        # ---------- M3a 仅 R7 置 DESIGN_APPROVED ⇒ R7 READY 但 R6 仍 NOT_READY ⇒ gate 仍 FAIL ----------
        loop_yaml = tmp / "LOOP.yaml"
        loop_data = load_structured(Cfg().loop_yaml)
        loop_data["gate_state"]["current"] = "DESIGN_APPROVED"
        loop_yaml.write_text(json.dumps(loop_data, ensure_ascii=False, indent=2), encoding="utf-8")
        r7_item = check_r7_gate_position(Cfg(loop_yaml=loop_yaml))
        r6_item = check_r6_d3_signed(Cfg())
        ok3a = r7_item.status == READY and r6_item.status == NOT_READY
        print(f"{'PASS' if ok3a else 'FAIL'}  M3a 仅置 DESIGN_APPROVED ⇒ R7 READY / R6 NOT_READY"
              f"  (R7={r7_item.status}, R6={r6_item.status}) ⇒ R6 有牙齿")
        if not ok3a:
            failures.append("M3a")

        # ---------- M3b 仅造 D3 签署件 ⇒ R6 READY 但 R7 仍 NOT_READY ⇒ gate 仍 FAIL ----------
        signed_dir = tmp / "architecture"
        signed_dir.mkdir(parents=True)
        (signed_dir / "ADR-ONTO1-namespace-neutral-iri.md").write_text(
            "# ADR-ONTO1（已签）\n\n状态: ACCEPTED\n\n签署人：语义架构 Owner / 域名 Owner\n"
            "签署日期：2026-10-09\n",
            encoding="utf-8",
        )
        r6_item = check_r6_d3_signed(Cfg(d3_search_dirs=(signed_dir,)))
        r7_item = check_r7_gate_position(Cfg())
        ok3b = r6_item.status == READY and r7_item.status == NOT_READY
        print(f"{'PASS' if ok3b else 'FAIL'}  M3b 仅造 D3 签署件 ⇒ R6 READY / R7 NOT_READY"
              f"  (R6={r6_item.status}, R7={r7_item.status}) ⇒ R7 有牙齿")
        if not ok3b:
            failures.append("M3b")

        # ---------- M3c 签署件 + DESIGN_APPROVED ⇒ 全项 READY ⇒ gate PASS ----------
        report = readiness(Cfg(loop_yaml=loop_yaml, d3_search_dirs=(signed_dir,)))
        ok3c = report["gate_pass"] is True
        residual = {k: v.status for k, v in report["items"].items() if v.status != READY}
        print(f"{'PASS' if ok3c else 'FAIL'}  M3c 签署件 + DESIGN_APPROVED ⇒ --gate 转 PASS"
              f"  (residual={residual})")
        if not ok3c:
            failures.append("M3c")

        # ---------- M3d 签署件无签署标记 ⇒ 不算签署件（fail-closed） ----------
        (signed_dir / "ADR-ONTO1-namespace-neutral-iri.md").write_text(
            "# ADR-ONTO1（改名冒充）\n\n（本文件无任何签署痕迹）\n", encoding="utf-8")
        item = check_r6_d3_signed(Cfg(d3_search_dirs=(signed_dir,)))
        ok3d = item.status == NOT_READY
        print(f"{'PASS' if ok3d else 'FAIL'}  M3d 改名冒充无签署标记 ⇒ R6 NOT_READY  ({item.reason[:60]})")
        if not ok3d:
            failures.append("M3d")

        # ---------- M5 预填根域 ⇒ R5 必须 NOT_READY ----------
        adr = tmp / "adr-prefilled.md"
        adr.write_text("# ADR（违规预填）\n\n新公共术语 IRI = NS-L1: https://acme.internal/onto/Party\n",
                       encoding="utf-8")
        item = check_r5_adr_draft(Cfg(adr_draft=adr))
        ok5 = item.status == NOT_READY and "ALREADY FILLED" in item.reason
        print(f"{'PASS' if ok5 else 'FAIL'}  M5 预填正式根域 ⇒ R5 NOT_READY  ({item.reason[:60]})")
        if not ok5:
            failures.append("M5")

        # ---------- M6 缺输入 / 待提交标记 ⇒ fail-closed（不得"跳过"） ----------
        state_pending = tmp / "state-pending.json"
        state_pending.write_text(json.dumps({"baseline_commit": PENDING_COMMIT_MARKER}), encoding="utf-8")
        absent = tmp / "does-not-exist"
        missing_cases = (
            ("R1 MANIFEST 缺失", check_r1_review_package(Cfg(package_dir=absent))),
            ("R3 归属矩阵缺失", check_r3_attribution(Cfg(attribution_csv=absent / "a.csv"))),
            ("R4 处置表缺失", check_r4_consumer_scan(Cfg(obligations_csv=absent / "o.csv"))),
            ("R5 ADR 草案缺失", check_r5_adr_draft(Cfg(adr_draft=absent / "adr.md"))),
            ("R7 LOOP.yaml 缺失", check_r7_gate_position(Cfg(loop_yaml=absent / "LOOP.yaml"))),
            ("R8 baseline_commit=PENDING_FIRST_COMMIT",
             check_r8_baseline_commit(Cfg(state_json=state_pending))),
        )
        bad = [name for name, item in missing_cases if item.status != NOT_READY]
        for name, item in missing_cases:
            mark = "PASS" if item.status == NOT_READY else "FAIL"
            print(f"{mark}  M6 缺输入 fail-closed：{name}  ({item.reason[:56]})")
        if bad:
            failures.append(f"M6 {bad}")

        if failures:
            print(f"onto1-wave0-readiness-selftest: FAIL {failures}", file=sys.stderr)
            return 2
        print("onto1-wave0-readiness-selftest: PASS")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="ONTO1 Wave 0 输入锚点就绪预检门禁")
    parser.add_argument("--gate", action="store_true",
                        help="G-1 是否已满足；G-1 前期望 FAIL(exit 2)")
    parser.add_argument("--precheck", action="store_true",
                        help="除 R6/R7 外全部 READY？等待期自查；现在期望 PASS(exit 0)")
    parser.add_argument("--selftest", action="store_true", help="变异复验（条目级断言）")
    parser.add_argument("--report", default=None, help="把机读结果写入该路径（JSON）")
    args = parser.parse_args()
    report_path = Path(args.report) if args.report else None
    if args.selftest:
        return selftest()
    if args.precheck:
        return precheck(report_path)
    return gate(report_path)


if __name__ == "__main__":
    raise SystemExit(main())
