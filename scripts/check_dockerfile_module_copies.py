#!/usr/bin/env python3
"""Fail-closed：Dockerfile 的依赖预热 COPY 必须覆盖 pom.xml 的全部 <module>。

背景：`Dockerfile` 在 `COPY . .` 之前先逐个 COPY 各模块的 `pom.xml`，用于预热
Maven 依赖缓存。该清单原先是**手工维护**的，与 `pom.xml` 的 `<module>` 列表发生
漂移（14 个模块只 COPY 了 11 个），导致 Maven 在读取 reactor 时报：

    [ERROR] Child module /app/modules/knowledge-architecture of /app/pom.xml does not exist

→ `Docker Build Verification` job 失败（真实 CI run 34847175044），并连带
`Build Summary` 失败、`E2E Tests` 被 skip（其 needs 含 docker-build）。

本检查把这类漂移从"镜像构建中途失败"提前为**构建前的秒级失败**，且给出缺失清单。

退出码：0=PASS（可能带 WARN）；2=FAIL。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# 匹配 `COPY <path>/pom.xml <dst>` 形式的预热拷贝
_COPY_RE = re.compile(r"^COPY ([\w./-]+)/pom\.xml ", re.M)
_MODULE_RE = re.compile(r"<module>([^<]+)</module>")


def main() -> int:
    pom = ROOT / "pom.xml"
    dockerfile = ROOT / "Dockerfile"
    for path in (pom, dockerfile):
        if not path.is_file():
            print(f"FAIL: 缺少 {path.name}", file=sys.stderr)
            return 2

    modules = _MODULE_RE.findall(pom.read_text(encoding="utf-8"))
    if not modules:
        print("FAIL: pom.xml 未声明任何 <module>", file=sys.stderr)
        return 2

    copied = set(_COPY_RE.findall(dockerfile.read_text(encoding="utf-8")))
    missing = [m for m in modules if m not in copied]
    extra = sorted(copied - set(modules))

    if missing:
        for module in missing:
            print(f"MISSING: Dockerfile 缺少 COPY {module}/pom.xml", file=sys.stderr)
        print(
            f"FAIL: pom.xml 声明 {len(modules)} 个模块，Dockerfile 只 COPY 了 "
            f"{len(copied)} 个；缺失 {len(missing)} 个 → 镜像构建会在 Maven 读取 "
            f"reactor 时报 'Child module ... does not exist'",
            file=sys.stderr,
        )
        return 2

    # 多余项不阻断（可能是尚未纳入 reactor 的模块），但要求显式可见
    for module in extra:
        print(f"WARN: Dockerfile COPY 了 {module}/pom.xml，但它不在 pom.xml <module> 内")

    print(f"PASS: Dockerfile 覆盖全部 {len(modules)} 个模块的 pom（共 {len(copied)} 条 COPY）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
