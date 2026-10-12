#!/usr/bin/env python3
"""M3 变异：临时去除 combo-query 的 metric/op 白名单校验（即改即还原）。

用法：python3 apply_m3.py mutate|restore
备份：/tmp/qa_an0/backup/operational_analytics.py
"""
from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path

SRC = Path("/home/szf/dev/Leibniz-KERT/src/kert/application/operational_analytics.py")
BAK = Path("/tmp/qa_an0/backup/operational_analytics.py")

GUARD = """            if metric not in COMBO_METRIC_COLUMNS:
                raise UsageError(f"amountRules.metric 非法: {metric}")
            if op not in COMBO_OPERATORS:
                raise UsageError(f"amountRules.op 非法: {op}")
"""


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    action = sys.argv[1]
    if action == "mutate":
        BAK.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SRC, BAK)
        text = SRC.read_text(encoding="utf-8")
        if GUARD not in text:
            print("[FAIL] 变异锚点未命中，未做任何改动")
            return 1
        SRC.write_text(text.replace(GUARD, "            # [QA-M3] 白名单校验已临时移除\n"),
                       encoding="utf-8")
        print(f"[MUTATED] before={sha(BAK)} after={sha(SRC)}")
        return 0
    if action == "restore":
        shutil.copy2(BAK, SRC)
        print(f"[RESTORED] now={sha(SRC)} backup={sha(BAK)} "
              f"match={sha(SRC) == sha(BAK)}")
        return 0
    print("用法: apply_m3.py mutate|restore")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
