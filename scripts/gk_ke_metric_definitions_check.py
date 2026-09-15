#!/usr/bin/env python3
"""GK-KE 指标定义核验与可复算性检查（A2 门禁）。

职责：
  1. 核验每项指标定义具备 §6.4 七组合同字段。
  2. 核验未固定值如实标注（不得留空或编造）。
  3. **可复算性检查**：对有 expectedColumn 的指标，用数据集 v2 实际重算，
     与定义声明的口径比对（§15.4 WP03 完成定义）。
  4. 计算并回填真实字节 SHA-256（禁止手工填写）。

用法：
  python3 scripts/gk_ke_metric_definitions_check.py          # 核验
  python3 scripts/gk_ke_metric_definitions_check.py --write  # 回填 hash 与复算证据
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFS = ROOT / "specs" / "gk-ke" / "v1" / "definitions"
DATASET = (ROOT / "scenario" / "seed" / "18_gk_ke_dataset_v2"
           / "observation" / "monthly_business_observation.csv")
HASH_REGISTRY = DEFS / "_metric_registry.json"

REQUIRED_GROUPS = {
    "identity": ["metricId", "version", "definition", "owner", "approvalRef"],
    "grain": ["entityType", "baseGrain", "aggregationGrain", "dimensions"],
    "time": ["intervalConvention", "businessTimezone", "calendarVersion", "asOfPolicy"],
    "compute": ["expressionText"],
    "money": ["currencyPolicy", "unit", "precision"],
    "data": ["sourceProductRef", "sourceSnapshotPolicy", "mappingVersion",
             "availabilityDimensions", "valueStates", "executionStates"],
    "runtime": ["parameterSchemaRef", "resultSchemaRef", "permissionRef",
                "maxRows", "timeoutMs"],
}

UNFIXED_TOKENS = {"", None, "PENDING", "TODO", "TBD", "XXX"}


def file_hash(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load_dataset() -> list[dict]:
    if not DATASET.is_file():
        return []
    with DATASET.open(encoding="utf-8") as fh:
        return [r for r in csv.DictReader(fh)]


def _num(raw: str):
    """解析数值：支持整数、小数、千分位与负号。"""
    return float(str(raw).replace(",", "").strip())


def _fmt(v: float) -> str:
    return str(int(v)) if float(v).is_integer() else f"{v:.6f}".rstrip("0").rstrip(".")


def _usable(rows: list[dict], column: str) -> list[dict]:
    return [r for r in rows
            if r.get("valueState") == "KNOWN" and r.get(column) not in (None, "")]


def _period_of(row: dict) -> str:
    return (row.get("periodStart") or row.get("businessDate")
            or row.get("eventTime") or "UNKNOWN")


def recompute(kind: str, column: str, rows: list[dict],
              spec: dict | None = None) -> dict:
    """按 recomputeKind 分派复算方式。

    关键设计：**不是所有指标都能求和**。
      SUM_FLOW        跨期求和有意义
      LATEST_STOCK    存量型只取期末值（跨期求和无意义）
      RATIO_DERIVED   由组分按公式逐期复算，并与夹具值比对
      DAYS_DERIVED    同上（加减组合）
      DAYS_OBSERVED   公式输入不可得 → 取观测值，并做内部一致性校验
      AVG_FROM_DAILY  按去重后逐日平均复算
    """
    spec = spec or {}
    usable = _usable(rows, column)
    if not usable:
        return {"status": "NO_DATA", "kind": kind}

    values = [_num(r[column]) for r in usable]
    base = {"kind": kind, "column": column, "periods": len(usable),
            "latestPeriod": _period_of(usable[-1]),
            "status": "RECOMPUTED"}

    if kind == "SUM_FLOW":
        base["sum"] = _fmt(sum(values))
        base["sumMeaningful"] = True
        return base

    if kind == "LATEST_STOCK":
        base["latest"] = _fmt(values[-1])
        # 明确声明：存量型**不做**跨期求和，避免把余额相加
        base["sumMeaningful"] = False
        base["sumOmittedReason"] = "存量型指标跨期求和无意义（会把余额重复计入）"
        return base

    if kind in ("RATIO_DERIVED", "DAYS_DERIVED"):
        num_col = spec.get("numerator")
        den_col = spec.get("denominator")
        comps = spec.get("components")
        per_period: list[dict] = []
        mismatches: list[str] = []
        for row in usable:
            if row.get("valueState") != "KNOWN":
                continue
            if num_col and den_col:
                a, b = row.get(num_col), row.get(den_col)
                if a in (None, "") or b in (None, ""):
                    continue
                bv = _num(b)
                if bv == 0:
                    continue
                calc = _num(a) / bv
            elif comps:
                vals = {}
                ok = True
                for c in comps.get("+", []) + comps.get("-", []):
                    if row.get(c) in (None, ""):
                        ok = False
                        break
                    vals[c] = _num(row[c])
                if not ok:
                    continue
                calc = sum(vals[c] for c in comps.get("+", [])) \
                    - sum(vals[c] for c in comps.get("-", []))
            else:
                continue
            fixture = _num(row[column])
            tol = max(abs(fixture) * 0.005, 0.01)   # 0.5% 容差
            matched = abs(calc - fixture) <= tol
            per_period.append({
                "period": _period_of(row),
                "recomputed": _fmt(calc),
                "fixtureValue": _fmt(fixture),
                "matched": matched,
            })
            if not matched:
                mismatches.append(_period_of(row))
        base["perPeriod"] = per_period
        base["matchedPeriods"] = sum(1 for p in per_period if p["matched"])
        base["mismatchedPeriods"] = mismatches
        base["tolerance"] = "0.5% 或 0.01（取大）"
        base["formula"] = (f"{num_col} / {den_col}" if num_col
                           else " + ".join(comps.get("+", []))
                           + " − " + " − ".join(comps.get("-", [])))
        base["latest"] = _fmt(values[-1])
        base["sumMeaningful"] = False
        base["sumOmittedReason"] = (
            "比率/天数型指标跨期求和无意义；已改为**按公式逐期复算并与夹具值比对**。")
        base["status"] = "RECOMPUTED_AND_CROSSCHECKED" if not mismatches \
            else "RECOMPUTED_WITH_MISMATCH"
        return base

    if kind == "DAYS_OBSERVED":
        base["latest"] = _fmt(values[-1])
        base["sumMeaningful"] = False
        base["sumOmittedReason"] = (
            f"公式所需输入不可得（{spec.get('formulaNeeds', '见 recomputeSpec')}）；"
            "只能取观测值，**不得声称按公式复算**。")
        base["status"] = "OBSERVED_ONLY"
        return base

    if kind == "AVG_FROM_DAILY":
        # 日均：按 (entity, date) 先跨账户求和，再对天数取平均
        by_day: dict[str, float] = {}
        for r in rows:
            d = r.get("businessDate")
            if not d or r.get("valueState") != "KNOWN":
                continue
            if r.get(column) in (None, ""):
                continue
            by_day[d] = by_day.get(d, 0.0) + _num(r[column])
        if not by_day:
            return {"status": "NO_DATA", "kind": kind}
        days = sorted(by_day)
        avg = sum(by_day[d] for d in days) / len(days)
        base.update({
            "distinctDays": len(days),
            "firstDay": days[0], "lastDay": days[-1],
            "dailyAvg": _fmt(avg),
            "perAccountSummedByDay": True,
            "sumMeaningful": False,
            "sumOmittedReason": "日均型指标对余额求和无意义；已改为逐日汇总后取平均。",
            "status": "RECOMPUTED_AVG_FROM_DAILY",
        })
        return base

    # 未分类：不擅自求和
    base["status"] = "UNCLASSIFIED_KIND"
    base["sumMeaningful"] = False
    base["sumOmittedReason"] = f"未声明 recomputeKind={kind!r}，不擅自求和。"
    return base


def load_csv(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    with path.open(encoding="utf-8") as fh:
        return [r for r in csv.DictReader(fh)]


def resolve_rows(source_ref: str, monthly: list[dict]) -> list[dict]:
    """按定义的 sourceRef 选择数据文件；缺省用月度观察。"""
    if not source_ref:
        return monthly
    candidate = ROOT / source_ref
    if candidate.is_file():
        return load_csv(candidate)
    return monthly


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    failures: list[str] = []
    computed: dict[str, dict] = {}
    recomputed_count = 0
    recomputed_derived_count = 0

    rows = load_dataset()
    if not rows:
        failures.append(f"数据集缺失或不可读: {DATASET}")

    files = sorted(DEFS.glob("SIM.METRIC.*.json"))
    if not files:
        failures.append("未找到任何 SIM.METRIC.*.json 定义")

    for path in files:
        doc = json.loads(path.read_text(encoding="utf-8"))
        mid = doc.get("metricId") or path.stem

        for group, fields in REQUIRED_GROUPS.items():
            node = doc.get(group)
            if not isinstance(node, dict):
                failures.append(f"[{mid}] 缺组 {group}")
                continue
            for f in fields:
                if f not in node:
                    failures.append(f"[{mid}] {group}.{f} 缺失")
                    continue
                value = node.get(f)
                # 只对字符串/None 判定"未固定"；列表/字典为结构化值，不算未固定
                if isinstance(value, (str, type(None))) and value in UNFIXED_TOKENS:
                    failures.append(f"[{mid}] {group}.{f} 未固定（{value!r}）")

        if doc.get("simulationOnly") is not True:
            failures.append(f"[{mid}] simulationOnly 必须为 true")

        declared = doc.get("identity", {}).get("definitionHash", "__MISSING__")
        if declared is not None:
            failures.append(f"[{mid}] identity.definitionHash 必须为 null")

        col = doc.get("expectedColumn")
        kind = doc.get("recomputeKind")
        if col:
            if not kind:
                failures.append(
                    f"[{mid}] 有 expectedColumn 但未声明 recomputeKind —— "
                    "不得默认按求和处理（比率/天数求和无意义）")
                continue
            source_ref = doc.get("data", {}).get("sourceRef", "")
            target_rows = resolve_rows(source_ref, rows)
            result = recompute(kind, col, target_rows, doc.get("recomputeSpec"))

            if result["status"] in ("NO_DATA", "UNCLASSIFIED_KIND"):
                failures.append(
                    f"[{mid}] recomputeKind={kind} 复算失败：{result['status']}"
                    f"（sourceRef={source_ref or 'default monthly'}）")
            else:
                recomputed_count += 1
                if kind in ("RATIO_DERIVED", "DAYS_DERIVED"):
                    recomputed_derived_count += 1
                    if result.get("mismatchedPeriods"):
                        failures.append(
                            f"[{mid}] 按公式复算与夹具值不一致的期: "
                            f"{result['mismatchedPeriods']}")
                doc["recomputeEvidence"] = {
                    "datasetRef": source_ref or
                    ("scenario/seed/18_gk_ke_dataset_v2/"
                     "observation/monthly_business_observation.csv"),
                    "note": ("复算仅统计 valueState=KNOWN 的期；未完结期不计入。"
                             "复算方式由 recomputeKind 决定，**并非一律求和**。"),
                }
                doc["recomputeEvidence"].update(result)
                if args.write:
                    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n",
                                    encoding="utf-8")

        computed[mid] = {"path": str(path.relative_to(ROOT)), "fileSha256": file_hash(path)}

    if args.write:
        HASH_REGISTRY.write_text(json.dumps({
            "$comment": ("GK-KE 指标定义指纹登记（侧车清单）。由 "
                         "scripts/gk_ke_metric_definitions_check.py --write 按真实字节计算；"
                         "禁止手工编辑。定义文件自身不得含自己的 hash。"),
            "hashMethod": "sha256(raw file bytes)",
            "authority": "GK-KE-D3-DECISION-001",
            "definitions": computed,
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    elif HASH_REGISTRY.is_file():
        stored = json.loads(HASH_REGISTRY.read_text(encoding="utf-8")).get("definitions", {})
        for mid, cur in computed.items():
            prev = stored.get(mid, {})
            if prev.get("fileSha256") != cur["fileSha256"]:
                failures.append(
                    f"[{mid}] registry fileSha256 不一致: "
                    f"stored={prev.get('fileSha256')!r} actual={cur['fileSha256']!r}")

    if failures:
        print("gk-ke-metric-definitions-check: FAIL", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print("gk-ke-metric-definitions-check: PASS")
    print(f"  definitions: {len(files)}")
    print(f"  recomputed from dataset: {recomputed_count} "
          f"(其中按公式逐期复算并交叉校验 {recomputed_derived_count})")
    print("  NOTE: 复算方式按 recomputeKind 分派，并非一律求和。")
    print("  groups checked: " + ", ".join(REQUIRED_GROUPS))
    if HASH_REGISTRY.is_file():
        print(f"  registry: {HASH_REGISTRY.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
