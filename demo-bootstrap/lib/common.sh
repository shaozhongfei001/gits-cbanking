#!/usr/bin/env bash
# demo-bootstrap 公共库：路径约定、日志、校验。被所有步骤脚本 source。
# 不单独执行。

set -euo pipefail

# ---------------------------------------------------------------- 路径约定
# 可用环境变量覆盖，默认按本机开发布局推导。
BOOTSTRAP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

: "${GITS_ROOT:=$(cd "${BOOTSTRAP_DIR}/.." && pwd)}"
: "${KERT_ROOT:=$(cd "${GITS_ROOT}/../Leibniz-KERT" && pwd 2>/dev/null || echo "${GITS_ROOT}/../Leibniz-KERT")}"

BUNDLE_DIR="${BUNDLE_DIR:-${BOOTSTRAP_DIR}/bundle}"

# KERT Python 环境：优先 .venv，缺失时回落到 python3 + PYTHONPATH=src
if [[ -x "${KERT_ROOT}/.venv/bin/python" ]]; then
  KERT_PY="${KERT_ROOT}/.venv/bin/python"
else
  KERT_PY="python3"
fi
export KERT_PY
export PYTHONPATH="${KERT_ROOT}/src${PYTHONPATH:+:${PYTHONPATH}}"

# kert CLI 调用函数。
# 实测缺陷：src/kert/cli/main.py 没有 `if __name__ == "__main__": app()` 块，
# 因此 `python -m kert.cli.main` 会静默无操作（不报错、也不建目录）。
# 必须显式 `from kert.cli.main import app; app()`。venv 内有 kert 可执行文件时优先用它。
kert_cli() {
  if [[ -x "${KERT_ROOT}/.venv/bin/kert" ]]; then
    "${KERT_ROOT}/.venv/bin/kert" "$@"
  else
    "${KERT_PY}" -c "from kert.cli.main import app; app()" "$@"
  fi
}
export -f kert_cli 2>/dev/null || true

# ---------------------------------------------------------------- 日志
C_RESET=$'\033[0m'; C_RED=$'\033[31m'; C_GRN=$'\033[32m'; C_YEL=$'\033[33m'; C_DIM=$'\033[2m'

log()  { printf '%s\n' "$*"; }
info() { printf '%s[INFO]%s %s\n'  "$C_GRN" "$C_RESET" "$*"; }
warn() { printf '%s[WARN]%s %s\n'  "$C_YEL" "$C_RESET" "$*" >&2; }
err()  { printf '%s[FAIL]%s %s\n'  "$C_RED" "$C_RESET" "$*" >&2; }
step() { printf '%s\n==> %s%s\n' "$C_DIM" "$*" "$C_RESET"; }

die() { err "$*"; exit 1; }

# need_cmd <命令> <缺失时提示>
need_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "缺少命令 '$1'。$2"
}

# ---------------------------------------------------------------- 校验
# sha256_file <文件> → 输出 64 位十六进制摘要
sha256_file() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk '{print $1}'
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | awk '{print $1}'
  else
    die "缺少 sha256sum / shasum，无法生成校验摘要"
  fi
}

# count_files <目录> → 文件数（不存在时输出 0）
count_files() {
  [[ -d "$1" ]] && find "$1" -type f | wc -l | tr -d ' ' || echo 0
}

# dir_bytes <目录> → 人类可读体积
dir_bytes() {
  [[ -e "$1" ]] && du -sh "$1" 2>/dev/null | awk '{print $1}' || echo "0"
}

# ---------------------------------------------------------------- 断言
# assert_dir <目录> <说明>
assert_dir() {
  [[ -d "$1" ]] || die "断言失败：目录不存在 $1（$2）"
}

# assert_file <文件> <说明>
assert_file() {
  [[ -f "$1" ]] || die "断言失败：文件不存在 $1（$2）"
}

# assert_nonempty_dir <目录> <说明>
assert_nonempty_dir() {
  assert_dir "$1" "$2"
  local n; n=$(count_files "$1")
  (( n > 0 )) || die "断言失败：空目录 $1（$2）"
}
