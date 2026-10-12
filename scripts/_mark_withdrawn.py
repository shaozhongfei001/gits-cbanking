#!/usr/bin/env python3
"""标注已撤回/已废弃的产物（我判断失误的记录），避免后续 TL 误读。"""
from __future__ import annotations

import pathlib

BANNER_LINES = [
    "> **[已撤回 / 已废弃 — 2026-09-12]**",
    ">",
    "> R-3 已由 GK-KE 全局 Tech Lead **自行查清并裁定**（代码为准，注释错误，已更正）。",
    "> 本文件**无需对方回函**，保留仅作为**判断失误的记录**。",
    "> 裁定详情见 `GK-KE-R3裁定与责任外推纠正-V1.0.md`。",
    "> **后续 TL 请勿据此以为正在等待 KERT 回复。**",
    "",
    "---",
    "",
]

FILES = [
    "docs/architecture/GK-KE-致KERT维护方确认函-V1.0.md",
    "docs/architecture/GK-KE-致KERT维护方确认函-发出记录-V1.0.md",
    "docs/architecture/GK-KE-KERT回函监控机制-V1.0.md",
]

SCRIPT_BANNER = (
    '"""【已废弃 — 2026-09-12】\n'
    "R-3 已由全局 TL 自行查清并裁定，无待回之事，本脚本不再需要。\n"
    "保留作为判断失误记录。\n"
    "见 docs/architecture/GK-KE-R3裁定与责任外推纠正-V1.0.md\n"
    '"""\n'
)


def main() -> int:
    root = pathlib.Path(".")

    for rel in FILES:
        path = root / rel
        if not path.is_file():
            print(f"SKIP 不存在: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        if "已撤回 / 已废弃" in text.split("\n\n")[0]:
            print(f"SKIP 已标注: {rel}")
            continue
        lines = text.split("\n")
        for idx, line in enumerate(lines):
            if line.startswith("# "):
                lines[idx + 1:idx + 1] = [""] + BANNER_LINES
                break
        path.write_text("\n".join(lines), encoding="utf-8")
        print(f"已标注: {rel}")

    script = root / "scripts" / "gk_ke_kert_watch.py"
    if script.is_file():
        text = script.read_text(encoding="utf-8")
        if "已废弃" not in text[:400]:
            end = text.index('"""', text.index('"""') + 3) + 3
            script.write_text(SCRIPT_BANNER + text[end:], encoding="utf-8")
            print(f"已标注废弃: {script}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
