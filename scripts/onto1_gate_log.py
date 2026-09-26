#!/usr/bin/env python3
"""ONTO1 门禁日志包装器（D-11「日志自证 revision」的合规落地形态）。

背景：`loop_guard.py` 的 `FORBIDDEN_COMMAND_PARTS` 含 `"echo "`/`"printf "`，
因此**不能**用 shell 的 `echo` 把被测脚本哈希写进日志。本包装器由被调脚本自己
打印，等价达成同一目的，且不触碰任何守卫禁区：

    用法：python3 scripts/onto1_gate_log.py <被测脚本> [该脚本的参数...]

输出契约（写入 evidence/*.log）：
    第 1 行  `# artifact=<路径>@<sha256 前 16 位> sha256=<全量>`   ← 日志自证被测版本
    第 2 行  `# command=python3 <路径> <参数...>`                  ← 可复算命令
    ...     被测脚本原样 stdout
    末 行   `# exit_code=<被测脚本退出码>`                          ← 退出码透传，防被包装器吞掉

退出码 = 被测脚本退出码（**不被本包装器改写**）；被测脚本缺失 ⇒ 2（fail-closed）。
"""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="ONTO1 门禁日志包装器（D-11）")
    parser.add_argument("script", help="被测脚本路径（相对仓根）")
    parser.add_argument("args", nargs=argparse.REMAINDER, help="透传给被测脚本的参数")
    ns = parser.parse_args()

    relative = ns.script
    target = (ROOT / relative).resolve()
    if not target.is_file():
        print(f"# artifact={relative}@MISSING")
        print(f"gate-log: FAIL: artifact missing: {relative}", file=sys.stderr)
        return 2

    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    print(f"# artifact={relative}@{digest[:16]} sha256={digest}")
    print(f"# command=python3 {relative} {' '.join(ns.args)}".rstrip())
    sys.stdout.flush()

    result = subprocess.run([sys.executable, str(target), *ns.args], cwd=ROOT, text=True)
    try:
        print(f"# exit_code={result.returncode}")
    except BrokenPipeError:  # 下游提前关闭管道（如 `| head`）不应改变门禁结论
        pass
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
