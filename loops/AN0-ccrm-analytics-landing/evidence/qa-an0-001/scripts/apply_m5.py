#!/usr/bin/env python3
"""M5 变异：AppSidebar.isActive 改回按 domain 判定（即改即还原）。

用法：python3 apply_m5.py mutate|restore
"""
from __future__ import annotations

import hashlib
import shutil
import sys
from pathlib import Path

SRC = Path("/home/szf/dev/gits-cbanking/frontend/src/components/shell/AppSidebar.vue")
BAK = Path("/tmp/qa_an0/backup/AppSidebar.vue")

ORIG = """  const sameDomain = SHELL_NAV_ITEMS.filter(i => i.domain === item.domain)
  if (sameDomain.length > 1) {
    return route.path === item.to || route.path.startsWith(`${item.to}/`)
  }
  return true
"""

MUT = """  // [QA-M5] 变异：改回按 domain 判定（同域整组同亮）
  return true
"""


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    action = sys.argv[1]
    if action == "mutate":
        BAK.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SRC, BAK)
        text = SRC.read_text(encoding="utf-8")
        if ORIG not in text:
            print("[FAIL] 变异锚点未命中，未做任何改动")
            return 1
        SRC.write_text(text.replace(ORIG, MUT), encoding="utf-8")
        print(f"[MUTATED] before={sha(BAK)} after={sha(SRC)}")
        return 0
    if action == "restore":
        shutil.copy2(BAK, SRC)
        print(f"[RESTORED] now={sha(SRC)} match={sha(SRC) == sha(BAK)}")
        return 0
    print("用法: apply_m5.py mutate|restore")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
