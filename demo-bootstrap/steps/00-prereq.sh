#!/usr/bin/env bash
# 步骤 0：环境前置检查。
# 校验两仓路径、Python 依赖、可选工具链，并报告 bundle 可用性。

set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/lib/common.sh"

# ---- 两仓路径
assert_dir "${GITS_ROOT}" "GITS 仓库根（用 GITS_ROOT 覆盖）"
info "GITS 仓库: ${GITS_ROOT}"

if [[ ${SKIP_KERT:-0} -eq 1 ]]; then
  warn "SKIP_KERT=1，不检查 KERT"
else
  assert_dir "${KERT_ROOT}" "KERT 仓库根（用 KERT_ROOT 覆盖）"
  info "KERT 仓库: ${KERT_ROOT}"
fi

# ---- Python 与 KERT 依赖
need_cmd "${KERT_PY%% *}" "演示环境依赖 Python 3.12+ 运行 KERT 造数脚本"

if [[ ${SKIP_KERT:-0} -eq 0 ]]; then
  info "校验 KERT Python 依赖（kert / kuzu / duckdb / pyarrow）…"
  if ! (cd "${KERT_ROOT}" && PYTHONPATH="${KERT_ROOT}/src" "${KERT_PY}" \
        -c "import kert, kuzu, duckdb, pyarrow" >/dev/null 2>&1); then
    warn "KERT 依赖不完整。请在 ${KERT_ROOT} 执行："
    warn "  python3 -m venv --system-site-packages .venv"
    warn "  .venv/bin/pip install -e \".[api,dev]\""
    warn "（依赖缺失时，regen 策略会失败，仅 restore 策略可用）"
  else
    info "KERT Python 依赖完整"
  fi
fi

# ---- 可选工具链（缺失只警告，不阻断数据初始化）
for c in java mvn node npm python3; do
  if command -v "$c" >/dev/null 2>&1; then
    info "工具链 $c: $(command -v "$c")"
  else
    warn "工具链 $c 未安装（仅影响对应服务的启动，不影响数据初始化）"
  fi
done

# ---- bundle 可用性
if [[ -d "${BUNDLE:-${BUNDLE_DIR}}" ]]; then
  MANIFEST="${BUNDLE:-${BUNDLE_DIR}}/MANIFEST.json"
  if [[ -f "${MANIFEST}" ]]; then
    info "数据包: ${BUNDLE:-${BUNDLE_DIR}}（含 MANIFEST.json）"
  else
    warn "数据包存在但缺 MANIFEST.json：${BUNDLE:-${BUNDLE_DIR}}"
  fi
else
  warn "未找到数据包 ${BUNDLE:-${BUNDLE_DIR}}"
  if [[ ${REGEN:-0} -ne 1 ]]; then
    warn "KERT 侧将自动改用 regen 策略（从源码重新生成数据）"
  fi
fi

info "前置检查通过"
