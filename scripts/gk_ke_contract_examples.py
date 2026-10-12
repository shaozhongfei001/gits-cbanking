#!/usr/bin/env python3
"""GK-KE gk-ke/v1 候选合同样例验证器（L0 Gate 2）。

对 specs/gk-ke/v1 下 14 个 schema 执行样例对拍：
  - examples/positive/<Schema>.json   必须通过对应 schema 校验
  - examples/negative/<Schema>_*.json 必须被对应 schema 拒绝（每个负例至少触发一个校验错误）

退出码：全部符合预期返回 0，否则返回非 0。
本脚本只校验合同样例，不连接任何服务、不读取检索语料。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "specs" / "gk-ke" / "v1"
SCHEMA_DIR = BASE / "schemas"
POS_DIR = BASE / "examples" / "positive"
NEG_DIR = BASE / "examples" / "negative"


def load_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def main() -> int:
    schemas = {p.stem.replace(".schema", ""): load_json(p)
               for p in sorted(SCHEMA_DIR.glob("*.json"))}
    failures: list[str] = []
    pos_ok = neg_ok = 0

    # 正例：每个 schema 一个，必须通过
    for name, schema in schemas.items():
        pos = POS_DIR / f"{name}.json"
        if not pos.exists():
            failures.append(f"[正例缺失] {name}: {pos.name}")
            continue
        instance = load_json(pos)
        try:
            jsonschema.validate(instance=instance, schema=schema)
            pos_ok += 1
        except jsonschema.ValidationError as exc:
            failures.append(f"[正例被拒] {name}: {exc.message}")

    # 负例：<Schema>_<n>.json，必须被对应 schema 拒绝
    for neg in sorted(NEG_DIR.glob("*.json")):
        stem = neg.stem  # e.g. AssetVersion_1
        schema_name = stem.rsplit("_", 1)[0]
        schema = schemas.get(schema_name)
        if schema is None:
            failures.append(f"[负例无对应schema] {neg.name} -> {schema_name}")
            continue
        instance = load_json(neg)
        try:
            jsonschema.validate(instance=instance, schema=schema)
            failures.append(f"[负例未被拒绝] {neg.name}（schema={schema_name}）")
        except jsonschema.ValidationError:
            neg_ok += 1

    print(f"gk-ke 合同样例: 正例通过 {pos_ok}/{len(schemas)}，"
          f"负例被拒 {neg_ok} 个")
    if failures:
        print(f"FAIL ({len(failures)}):")
        for item in failures:
            print("  -", item)
        return 1
    print("gk-ke-contract-examples: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
