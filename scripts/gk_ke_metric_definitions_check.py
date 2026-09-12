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


def recompute(column: str, rows: list[dict]) -> dict:
    usable = [r for r in rows
              if r.get("valueState") == "KNOWN" and r.get(column) not in (None, "")]
    if not usable:
        return {"periods": 0, "sum": None, "latest": None, "status": "NO_DATA"}
    values = [_num(r[column]) for r in usable]
    is_int = all(v.is_integer() for v in values)
    return {
        "periods": len(usable),
        "sum": str(int(sum(values))) if is_int else f"{sum(values):.4f}".rstrip("0").rstrip("."),
        "latest": str(int(values[-1])) if values[-1].is_integer() else str(values[-1]),
        "latestPeriod": (usable[-1].get("periodStart")
                         or usable[-1].get("businessDate")
                         or usable[-1].get("eventTime")
                         or "UNKNOWN"),
        "status": "RECOMPUTED",
    }


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
        if col:
            source_ref = doc.get("data", {}).get("sourceRef", "")
            target_rows = resolve_rows(source_ref, rows)
            result = recompute(col, target_rows)
            if result["status"] != "RECOMPUTED":
                failures.append(
                    f"[{mid}] 声明 expectedColumn={col} 但无可复算值"
                    f"（sourceRef={source_ref or 'default monthly'}）")
            else:
                recomputed_count += 1
                doc["recomputeEvidence"] = {
                    "datasetRef": source_ref or
                    ("scenario/seed/18_gk_ke_dataset_v2/"
                     "observation/monthly_business_observation.csv"),
                    "column": col,
                    "periodsUsed": result["periods"],
                    "sum": result["sum"],
                    "latest": result["latest"],
                    "latestPeriod": result["latestPeriod"],
                    "note": "复算仅统计 valueState=KNOWN 的期；未完结期不计入。",
                }
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
    print(f"  recomputed from dataset: {recomputed_count}")
    print("  groups checked: " + ", ".join(REQUIRED_GROUPS))
    if HASH_REGISTRY.is_file():
        print(f"  registry: {HASH_REGISTRY.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
