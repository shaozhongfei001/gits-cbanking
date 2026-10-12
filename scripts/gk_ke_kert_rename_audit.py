#!/usr/bin/env python3
"""审阅 KERT 工作区改动：确认是否纯 dkws→kert 重命名，是否存在夹带。

方法：
  对每个 M 类文件，取 HEAD 版本与工作区版本，
  将 dkws/DKWS 统一替换为 X 后比对。不一致者即存在"非改名"实质改动。
"""
from __future__ import annotations

import os
import re
import subprocess

KERT = "/home/szf/dev/Leibniz-KERT"


def norm(text: str) -> str:
    """把 dkws/DKWS/Dkws 与 kert/KERT/Kert 统一归一，用于判定"仅改名"。

    注意：必须**同时**归一旧名与新名，否则 kert.domain 与 dkws.domain 会被判为不同。
    """
    text = re.sub(r"[Dd][Kk][Ww][Ss]", "X", text)
    text = re.sub(r"[Kk][Ee][Rr][Tt]", "X", text)
    return text


def git(*args: str) -> bytes:
    return subprocess.run(["git", *args], cwd=KERT, capture_output=True).stdout


def main() -> int:
    status = git("status", "--porcelain").decode("utf-8", "replace")
    mfiles = []
    for line in status.splitlines():
        if line.startswith(" M"):
            path = line[3:].strip()
            if path.startswith('"') and path.endswith('"'):
                path = path[1:-1]
            mfiles.append(path)

    print(f"M 类文件: {len(mfiles)}")

    mismatch = []
    identical = 0
    for path in mfiles:
        full = os.path.join(KERT, path)
        if not os.path.isfile(full):
            continue
        old_b = git("show", f"HEAD:{path}")
        if not old_b:
            continue
        with open(full, "rb") as fh:
            new_b = fh.read()
        old = old_b.decode("utf-8", "replace")
        new = new_b.decode("utf-8", "replace")
        if norm(old) == norm(new):
            identical += 1
        else:
            mismatch.append(path)

    print(f"  去掉命名差异后完全一致（纯改名）: {identical}")
    print(f"  仍有差异（需人工判定）: {len(mismatch)}")
    for f in mismatch:
        print(f"    - {f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
