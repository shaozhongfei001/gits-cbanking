#!/usr/bin/env python3
"""ONTO1 W-1｜D4 决策包门禁：把「决策包已就绪」变成可机读、可变异复验的断言。

背景
----
D4 把「客户/法人/集团/产品身份 A-Box 权威」交给数据 Owner + 业务 Owner 裁定与签署。
文书本身不能自证合规：最典型的失效模式是**红线被悄悄违反** ——

  · 有人把 GITS 运营库 / KERT workspace 填成正式权威；
  · 有人给授权投影合同填了生效日期（等于让它生效）；
  · 有人把 CQ1/CQ2 标成 PASS；
  · 某术语只剩一个候选（等于替 Owner 做了决定）；
  · 依据写成「见设计」（无法回源）。

因此本门禁不检查「文书写得漂不漂亮」，只检查**这些红线是否仍成立**。
fail-closed：缺夹具、缺候选、缺证据、状态异常一律 FAIL，不设「0 项也算绿」。

门禁（C1~C11）
--------------
  C1  L1 八类齐备（8 项，不多不少）
  C2  每术语 A-Box Owner / ID Owner 非空，且不得为 GITS 运营库 / KERT workspace；
      权威候选（PRIMARY/ALTERNATE）同样受限；`CARRIER`（仅存放位置）须自述「仅存放」
  C3  每术语 2~3 个候选（PRIMARY/ALTERNATE），且每个候选带证据
  C4  每术语至少 1 条 EXCLUDED（禁止项，strength=PROHIBITED）
  C5  证据必须回源：`文件` 必须真实存在（`文件:行` 形态）
  C6  SourceIdentifier：六必填字段齐备 + 具名拒绝码/子码/禁止行为齐备
  C7  投影合同 NOT_EFFECTIVE（无生效日期、无签署人）+ 七要素 + 漂移码 + 失效条件
  C8  SIM 声明 NOT_EFFECTIVE + 三载体 + 四退出条件（状态仅 NOT_TRIGGERED）
  C9  CQ1/CQ2 = NOT_EVALUATED 且有 A-Box 依赖说明；包内不得出现 PASS 断言
  C10 机读清单哈希与 manifest 一致
  C11 决策包正文存在且关键声明与机读包一致
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOOP = ROOT / "loops" / "ONTO1-ontology-split"
EVID = LOOP / "evidence"
CSV_NAME = "d4-l1-authority-candidates.csv"
JSON_NAME = "d4-pack.json"
MANIFEST_NAME = "d4-pack-manifest.json"
PACK_DOC = ROOT / "docs" / "dispatch" / "ONTO1-D4-决策包-V1.0.md"

L1_TERMS = ["Party", "Organization", "LegalEntity", "CustomerRole",
            "EnterpriseGroup", "GroupMembership", "ProductOffering", "SourceIdentifier"]
CANDIDATE_KINDS = {"PRIMARY", "ALTERNATE", "EXCLUDED", "CARRIER"}
OPEN_KINDS = {"PRIMARY", "ALTERNATE"}
FORBIDDEN_AUTHORITY = ("GITS 运营库", "KERT workspace", "gits 运营库")
REQUIRED_SI_FIELDS = {"sourceSystem", "objectType", "originalId", "validFrom",
                      "extractedAt", "authorizationBasis"}
REQUIRED_CONTRACT_KEYS = {"source", "as_of", "version", "authorization_scope",
                          "responsibility", "drift_rejection", "invalidation"}
ALLOWED_SIM_STATUS = {"NOT_TRIGGERED", "TRIGGERED", "CLOSED"}
STATUS_KEYS = {"status", "pack_status", "declaration_status", "ledger_status"}
DOC_MARKERS = ("MISSING_SOURCE_IDENTIFIER", "NOT_EFFECTIVE", "NOT_EVALUATED",
               "不得代签", "GITS 运营库", "KERT workspace", "授权投影合同")
LINE_REF = re.compile(r"\d+(-\d+)?$")
PASS_ROW = re.compile(r"\|\s*PASS\s*\|")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_evidence(token: str) -> str:
    """`specs/a/b.json:2-12` / `docs/x.md:5` / `specs/CONTRACT_INDEX.yaml:166` → 文件路径。"""
    token = token.strip()
    head, _, tail = token.rpartition(":")
    if head and LINE_REF.match(tail):
        return head
    return token


# --------------------------------------------------------------------------
# 载入
# --------------------------------------------------------------------------

def load_rows(csv_path: Path) -> list[dict[str, str]]:
    with csv_path.open(encoding="utf-8", newline="") as stream:
        return [row for row in csv.DictReader(stream) if (row.get("term") or "").strip()]


def load_pack(json_path: Path) -> dict:
    return json.loads(json_path.read_text(encoding="utf-8"))


def walk_statuses(node, out: list[tuple[str, str]]) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            if isinstance(value, str) and key in STATUS_KEYS:
                out.append((key, value))
            walk_statuses(value, out)
    elif isinstance(node, list):
        for item in node:
            walk_statuses(item, out)


# --------------------------------------------------------------------------
# 校验
# --------------------------------------------------------------------------

def check(rows: list[dict[str, str]], pack: dict, doc_path: Path = PACK_DOC) -> list[str]:
    failures: list[str] = []

    # C1 -----------------------------------------------------------------
    terms: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        terms.setdefault(row["term"].strip(), []).append(row)
    if set(terms) != set(L1_TERMS):
        failures.append(f"C1 L1 term set mismatch: missing={sorted(set(L1_TERMS) - set(terms))} "
                        f"extra={sorted(set(terms) - set(L1_TERMS))}")

    for term in L1_TERMS:
        rows_of_term = terms.get(term)
        if not rows_of_term:
            continue

        # C2 -------------------------------------------------------------
        abox = (rows_of_term[0].get("abox_owner_registered") or "").strip()
        idowner = (rows_of_term[0].get("id_owner_registered") or "").strip()
        if not abox or not idowner:
            failures.append(f"C2 {term}: abox_owner_registered / id_owner_registered 不得为空")
        for bad in FORBIDDEN_AUTHORITY:
            if bad in abox:
                failures.append(f"C2 {term}: A-Box Owner 不得登记禁止权威「{bad}」")
                break
        for row in rows_of_term:
            named = (row.get("candidate_named") or "")
            # 只有「权威候选」受禁止名单约束；`CARRIER`（仅存放位置）允许出现运营库/工作区名称，
            # 但必须在 note 中自述「仅存放」，防止把存放位置当权威混进来。
            if row.get("candidate_kind") in OPEN_KINDS:
                for bad in FORBIDDEN_AUTHORITY:
                    if bad in named:
                        failures.append(f"C2 {term}/{row.get('candidate_id')}: 候选不得为禁止权威「{bad}」")
                        break
            if row.get("candidate_kind") == "CARRIER" and "仅存放" not in (row.get("note") or ""):
                failures.append(f"C2 {term}/{row.get('candidate_id')}: CARRIER 必须在 note 自述「仅存放」"
                                "（存放位置 ≠ 权威）")

        # C3 -------------------------------------------------------------
        open_rows = [r for r in rows_of_term if r.get("candidate_kind") in OPEN_KINDS]
        if not 2 <= len(open_rows) <= 3:
            failures.append(f"C3 {term}: 候选数 {len(open_rows)} 不在 2~3（等于替 Owner 做了决定 / 选不过来）")
        for row in rows_of_term:
            if row.get("candidate_kind") not in CANDIDATE_KINDS:
                failures.append(f"C3 {term}/{row.get('candidate_id')}: candidate_kind 非法 "
                                f"{(row.get('candidate_kind') or '').strip()!r}")
            if not (row.get("evidence") or "").strip():
                failures.append(f"C3 {term}/{row.get('candidate_id')}: 候选缺证据（无法回源）")

        # C4 -------------------------------------------------------------
        excluded = [r for r in rows_of_term if r.get("candidate_kind") == "EXCLUDED"]
        if not excluded:
            failures.append(f"C4 {term}: 缺 EXCLUDED 禁止项（红线未显式登记）")
        for row in excluded:
            if (row.get("strength") or "").strip() != "PROHIBITED":
                failures.append(f"C4 {term}/{row.get('candidate_id')}: EXCLUDED 的 strength 必须为 PROHIBITED")

    # C5 -----------------------------------------------------------------
    for row in rows:
        for token in (row.get("evidence") or "").split(";"):
            if not token.strip():
                continue
            target = split_evidence(token)
            if not (ROOT / target).is_file():
                failures.append(f"C5 {row.get('term')}/{row.get('candidate_id')}: 证据回源失败，"
                                f"文件不存在：{target}")

    # C6 -----------------------------------------------------------------
    si = pack.get("source_identifier") or {}
    required = {f.get("name") for f in si.get("required_fields") or [] if f.get("required")}
    if required != REQUIRED_SI_FIELDS:
        failures.append(f"C6 SourceIdentifier 必填字段不齐：missing={sorted(REQUIRED_SI_FIELDS - required)} "
                        f"extra={sorted(required - REQUIRED_SI_FIELDS)}")
    for field in si.get("required_fields") or []:
        for key in ("meaning", "mapping", "expected_refusal"):
            if not (field.get(key) or "").strip():
                failures.append(f"C6 SourceIdentifier.{field.get('name')}: {key} 为空")
    refusal = si.get("refusal") or {}
    if refusal.get("code") != "MISSING_SOURCE_IDENTIFIER":
        failures.append("C6 具名拒绝码必须为 MISSING_SOURCE_IDENTIFIER")
    if refusal.get("fail_closed") is not True:
        failures.append("C6 具名拒绝必须 fail_closed=true")
    if len(refusal.get("subcodes") or []) < 6:
        failures.append("C6 具名拒绝子码少于 6 个（覆盖不足）")
    behaviors = refusal.get("forbidden_behaviors") or []
    if len(behaviors) < 4:
        failures.append("C6 禁止行为少于 4 条")
    if not any("静默补默认值" in item for item in behaviors):
        failures.append("C6 禁止行为必须显式禁止「静默补默认值」")

    # C7 -----------------------------------------------------------------
    contract = pack.get("projection_contract") or {}
    if contract.get("status") != "NOT_EFFECTIVE":
        failures.append(f"C7 投影合同状态必须为 NOT_EFFECTIVE，实际 "
                        f"{contract.get('status')!r}（红线：不得让投影合同生效）")
    if contract.get("effective_from") is not None:
        failures.append("C7 投影合同不得填生效日期（effective_from 必须为 null）")
    if contract.get("signed_by") is not None:
        failures.append("C7 投影合同不得填签署人（signed_by 必须为 null）")
    keys = {item.get("key") for item in contract.get("elements") or []}
    if keys != REQUIRED_CONTRACT_KEYS:
        failures.append(f"C7 投影合同七要素不齐：missing={sorted(REQUIRED_CONTRACT_KEYS - keys)} "
                        f"extra={sorted(keys - REQUIRED_CONTRACT_KEYS)}")
    for item in contract.get("elements") or []:
        if not (item.get("draft_value") or "").strip():
            failures.append(f"C7 投影合同要素 {item.get('key')} 缺草案取值")
    if len(contract.get("drift_refusal_codes") or []) < 5:
        failures.append("C7 漂移拒绝码少于 5 条")
    if len(contract.get("invalidation_conditions") or []) < 4:
        failures.append("C7 失效条件少于 4 条")

    # C8 -----------------------------------------------------------------
    sim = pack.get("sim_declaration") or {}
    if sim.get("declaration_status") != "NOT_EFFECTIVE":
        failures.append(f"C8 SIM 声明状态必须为 NOT_EFFECTIVE，实际 {sim.get('declaration_status')!r}")
    carriers = sim.get("carriers") or []
    if len(carriers) != 3:
        failures.append(f"C8 SIM 载体必须为 3 个（§2.2 三个占位），实际 {len(carriers)}")
    for carrier in carriers:
        if not (carrier.get("recommended_path") or "").strip():
            failures.append(f"C8 SIM 载体 {carrier.get('placeholder')} 缺建议填法")
        if not carrier.get("excluded_paths"):
            failures.append(f"C8 SIM 载体 {carrier.get('placeholder')} 未写明明确排除项")
    exits = sim.get("exit_conditions") or []
    if len(exits) != 4:
        failures.append(f"C8 SIM 退出条件必须为 4 条（§2.3），实际 {len(exits)}")
    for item in exits:
        for key in ("trigger_criteria", "detection", "owner", "frequency", "status"):
            if not str(item.get(key) or "").strip():
                failures.append(f"C8 退出条件 {item.get('no')} 缺 {key}")
        if str(item.get("status")) not in ALLOWED_SIM_STATUS:
            failures.append(f"C8 退出条件 {item.get('no')} 状态非法：{item.get('status')!r}")
    if sim.get("ledger_status") != "TRACKING_NOT_STARTED":
        failures.append(f"C8 台账状态必须为 TRACKING_NOT_STARTED（声明未生效），实际 "
                        f"{sim.get('ledger_status')!r}")

    # C9 -----------------------------------------------------------------
    for cq in ("CQ1", "CQ2"):
        block = (pack.get("cq_dependency") or {}).get(cq) or {}
        if block.get("status") != "NOT_EVALUATED":
            failures.append(f"C9 {cq} 状态必须为 NOT_EVALUATED，实际 {block.get('status')!r}"
                            "（红线：不得把场景标 PASS）")
        if not block.get("abox_dependency"):
            failures.append(f"C9 {cq} 缺 A-Box 依赖说明")
    statuses: list[tuple[str, str]] = []
    walk_statuses(pack, statuses)
    for key, value in statuses:
        if value == "PASS":
            failures.append(f"C9 机读包出现 PASS 断言（{key}=PASS）")
    if doc_path.is_file():
        text = doc_path.read_text(encoding="utf-8")
        if PASS_ROW.search(text):
            failures.append("C9 决策包正文出现 PASS 表格断言")

    # C10 ----------------------------------------------------------------
    manifest_path = EVID / MANIFEST_NAME
    if not manifest_path.is_file():
        failures.append(f"C10 缺 manifest：{manifest_path.relative_to(ROOT)}")
    else:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for name, digest in (manifest.get("artifacts") or {}).items():
            target = EVID / name
            if not target.is_file():
                failures.append(f"C10 manifest 声明的制品缺失：{name}")
            elif sha256(target) != digest:
                failures.append(f"C10 {name} 哈希与 manifest 不一致（决策包被静默改动）")

    # C11 ----------------------------------------------------------------
    if not doc_path.is_file():
        failures.append(f"C11 决策包正文缺失：{doc_path.relative_to(ROOT)}")
    else:
        text = doc_path.read_text(encoding="utf-8")
        for marker in DOC_MARKERS:
            if marker not in text:
                failures.append(f"C11 决策包正文缺关键声明：{marker}")

    return failures


# --------------------------------------------------------------------------
# 入口
# --------------------------------------------------------------------------

def write_manifest() -> int:
    artifacts = {}
    for name in (CSV_NAME, JSON_NAME):
        target = EVID / name
        if not target.is_file():
            print(f"onto1-d4-pack: FAIL: 缺制品 {name}", file=sys.stderr)
            return 2
        artifacts[name] = sha256(target)
    manifest = {
        "schema": "onto1_d4_pack_manifest/v1",
        "loop_id": "ONTO1-ontology-split",
        "pack_id": "W-1/D4-pack",
        "artifacts": artifacts,
        "doc": "docs/dispatch/ONTO1-D4-决策包-V1.0.md",
    }
    (EVID / MANIFEST_NAME).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for name, digest in artifacts.items():
        print(f"[manifest] {name} sha256={digest[:16]}")
    return 0


def gate(csv_path: Path = EVID / CSV_NAME, json_path: Path = EVID / JSON_NAME,
         doc_path: Path = PACK_DOC) -> int:
    if not csv_path.is_file() or not json_path.is_file():
        print("onto1-d4-pack: FAIL: 机读清单缺失", file=sys.stderr)
        return 2
    rows = load_rows(csv_path)
    pack = load_pack(json_path)
    failures = check(rows, pack, doc_path)

    terms = {row["term"] for row in rows}
    print(f"[C1] terms={len(terms)} rows={len(rows)}")
    print(f"[C6] source_identifier required="
          f"{[f['name'] for f in pack['source_identifier']['required_fields'] if f.get('required')]}")
    print(f"[C7] projection_contract={pack['projection_contract']['status']} "
          f"effective_from={pack['projection_contract']['effective_from']}")
    print(f"[C8] sim_declaration={pack['sim_declaration']['declaration_status']} "
          f"exit_conditions={len(pack['sim_declaration']['exit_conditions'])} "
          f"ledger={pack['sim_declaration']['ledger_status']}")
    print(f"[C9] CQ1={pack['cq_dependency']['CQ1']['status']} "
          f"CQ2={pack['cq_dependency']['CQ2']['status']}")

    if failures:
        for item in failures:
            print(f"onto1-d4-pack: FAIL: {item}", file=sys.stderr)
        return 2
    print("onto1-d4-pack: PASS")
    return 0


def selftest() -> int:
    failures: list[str] = []
    tmp = Path(tempfile.mkdtemp(prefix="onto1-d4-pack-selftest-"))
    try:
        base_rows = load_rows(EVID / CSV_NAME)
        base_pack = load_pack(EVID / JSON_NAME)

        def expect_fail(label: str, rows: list[dict[str, str]], pack: dict,
                        needle: str) -> None:
            found = check(rows, pack)
            hit = any(needle in item for item in found)
            print(f"{'PASS' if hit else 'FAIL'}  {label}")
            if not hit:
                failures.append(label)

        # M1 把法人 A-Box Owner 改成 GITS 运营库 ⇒ C2
        rows = copy.deepcopy(base_rows)
        for row in rows:
            if row["term"] == "LegalEntity":
                row["abox_owner_registered"] = "GITS 运营库"
        expect_fail("M1 A-Box Owner 登记为 GITS 运营库 ⇒ FAIL",
                    rows, copy.deepcopy(base_pack), "C2 LegalEntity")

        # M2 删掉 SourceIdentifier 的 extractedAt ⇒ C6
        pack = copy.deepcopy(base_pack)
        pack["source_identifier"]["required_fields"] = [
            f for f in pack["source_identifier"]["required_fields"] if f["name"] != "extractedAt"]
        expect_fail("M2 删掉 SourceIdentifier.extractedAt ⇒ FAIL",
                    copy.deepcopy(base_rows), pack, "C6 SourceIdentifier")

        # M3 把 CQ1 标成 PASS ⇒ C9
        pack = copy.deepcopy(base_pack)
        pack["cq_dependency"]["CQ1"]["status"] = "PASS"
        expect_fail("M3 CQ1 标 PASS ⇒ FAIL",
                    copy.deepcopy(base_rows), pack, "C9 CQ1")

        # M4 给投影合同填生效日期 ⇒ C7
        pack = copy.deepcopy(base_pack)
        pack["projection_contract"]["effective_from"] = "2026-10-15"
        expect_fail("M4 投影合同填生效日期 ⇒ FAIL",
                    copy.deepcopy(base_rows), pack, "C7")

        # M5 删掉某候选的证据 ⇒ C3/C5
        rows = copy.deepcopy(base_rows)
        rows[0]["evidence"] = ""
        expect_fail("M5 候选缺证据 ⇒ FAIL",
                    rows, copy.deepcopy(base_pack), "C3 Party/P-1")

        # M6 证据指向不存在的文件 ⇒ C5
        rows = copy.deepcopy(base_rows)
        rows[0]["evidence"] = "specs/does/not/exist.json:1"
        expect_fail("M6 证据不可回源 ⇒ FAIL",
                    rows, copy.deepcopy(base_pack), "C5 Party/P-1")

        # M7 某术语候选只剩 1 个 ⇒ C3
        rows = [r for r in copy.deepcopy(base_rows) if r["candidate_id"] != "EG-2"]
        rows = [r for r in rows if r["candidate_id"] != "EG-3"]
        expect_fail("M7 集团候选只剩 1 个 ⇒ FAIL",
                    rows, copy.deepcopy(base_pack), "C3 EnterpriseGroup")

        # M8 删掉一条 SIM 退出条件 ⇒ C8
        pack = copy.deepcopy(base_pack)
        pack["sim_declaration"]["exit_conditions"] = pack["sim_declaration"]["exit_conditions"][:3]
        expect_fail("M8 SIM 退出条件少一条 ⇒ FAIL",
                    copy.deepcopy(base_rows), pack, "C8 SIM 退出条件")

        # M9 台账状态提前写成已启动 ⇒ C8
        pack = copy.deepcopy(base_pack)
        pack["sim_declaration"]["ledger_status"] = "TRACKING_ACTIVE"
        expect_fail("M9 声明未生效却启动台账 ⇒ FAIL",
                    copy.deepcopy(base_rows), pack, "C8 台账状态")

        # M0 对照：真实包 ⇒ PASS
        code = gate(EVID / CSV_NAME, EVID / JSON_NAME)
        print(f"{'PASS' if code == 0 else 'FAIL'}  M0 对照：真实决策包 ⇒ PASS  exit={code}")
        if code != 0:
            failures.append("M0")

        if failures:
            print(f"onto1-d4-pack-selftest: FAIL {failures}", file=sys.stderr)
            return 2
        print("onto1-d4-pack-selftest: PASS")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gate", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--write-manifest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    if args.write_manifest:
        return write_manifest()
    return gate()


if __name__ == "__main__":
    raise SystemExit(main())
