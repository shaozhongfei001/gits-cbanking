#!/usr/bin/env python3
"""M4 变异：向 .ts 副本注入类型错误后跑 vue-tsc（即改即还原）。

用法：python3 apply_m4.py mutate <target>|restore <target>
target: src | e2e   （src=src/api/analytics.ts；e2e=e2e/analytics.spec.ts）
"""
from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path

FE = Path("/home/szf/dev/gits-cbanking/frontend")
TARGETS = {
    "src": (FE / "src/api/analytics.ts", Path("/tmp/qa_an0/backup/analytics.ts")),
    "e2e": (FE / "e2e/analytics.spec.ts", Path("/tmp/qa_an0/backup/analytics.spec.ts")),
}
INJECT = "\nconst __qaM4Typecheck: number = 'qa-m4-injected-type-error'\n"


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    action, target = sys.argv[1], sys.argv[2]
    src, bak = TARGETS[target]
    if action == "mutate":
        bak.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, bak)
        src.write_text(src.read_text(encoding="utf-8") + INJECT, encoding="utf-8")
        print(f"[MUTATED {target}] before={sha(bak)} after={sha(src)}")
        return 0
    if action == "restore":
        shutil.copy2(bak, src)
        print(f"[RESTORED {target}] now={sha(src)} match={sha(src) == sha(bak)}")
        return 0
    print("用法: apply_m4.py mutate|restore src|e2e")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
