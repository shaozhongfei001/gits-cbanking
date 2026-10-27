#!/usr/bin/env bash
# 在目标开发机重建 GITS + KERT 演示环境。
#
# 两种恢复策略（自动选择，可用 --regen 强制）：
#   restore（默认）— 从 bundle 拷回 KERT 的 gitignored 数据（工作区/kuzu/duckdb）。
#                     优点：与源机逐字节一致，演示效果可复现。
#   regen          — 调用 KERT 脚本从源重新生成。优点：不依赖 bundle，可验证生成链路。
#                     bundle 缺失或 --regen 时自动走这条。
#
# 用法：
#   ./init_demo_env.sh                        # 默认 restore（bundle 在 ./bundle）
#   ./init_demo_env.sh --bundle /path/to/bundle
#   ./init_demo_env.sh --regen                # 强制重新生成
#   ./init_demo_env.sh --skip-kert            # 只准备 GITS 侧
#   ./init_demo_env.sh --help

set -euo pipefail
BOOTSTRAP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${BOOTSTRAP_DIR}/lib/common.sh"

BUNDLE="${BUNDLE_DIR}"
REGEN=0
SKIP_KERT=0
SKIP_GITS=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --bundle)   BUNDLE="${2:?--bundle 需要参数}"; shift 2 ;;
    --regen)    REGEN=1; shift ;;
    --skip-kert) SKIP_KERT=1; shift ;;
    --skip-gits) SKIP_GITS=1; shift ;;
    -h|--help)  sed -n '2,16p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *)          die "未知参数: $1（用 --help 查看用法）" ;;
  esac
done

export BUNDLE REGEN

log "=================================================================="
log " GITS + KERT 演示环境初始化"
log "=================================================================="
log "GITS_ROOT : ${GITS_ROOT}"
log "KERT_ROOT : ${KERT_ROOT}"
log "BUNDLE    : ${BUNDLE}"
log "策略      : $([[ $REGEN -eq 1 ]] && echo regen || echo restore)"
log ""

# ---------------------------------------------------------------- 步骤 0：环境检查
step "[0/5] 环境前置检查"
"${BOOTSTRAP_DIR}/steps/00-prereq.sh"

# ---------------------------------------------------------------- 步骤 1：恢复 KERT 工作区
if [[ $SKIP_KERT -eq 0 ]]; then
  step "[1/5] 恢复 KERT 工作区"
  "${BOOTSTRAP_DIR}/steps/10-restore-kert-workspace.sh"

  step "[2/5] 构建 KERT 产品知识图库"
  "${BOOTSTRAP_DIR}/steps/20-build-kert-graph.sh"

  step "[3/5] 构建 DuckDB 分析库"
  "${BOOTSTRAP_DIR}/steps/30-build-analytics.sh"
else
  warn "已跳过 KERT 侧（--skip-kert）"
fi

# ---------------------------------------------------------------- 步骤 4：校验 GITS 数据
if [[ $SKIP_GITS -eq 0 ]]; then
  step "[4/5] 校验 GITS 数据完整性"
  "${BOOTSTRAP_DIR}/steps/40-verify-gits-data.sh"
else
  warn "已跳过 GITS 侧（--skip-gits）"
fi

# ---------------------------------------------------------------- 步骤 5：冒烟
step "[5/5] 冒烟验证"
"${BOOTSTRAP_DIR}/steps/50-smoke.sh"

log ""
log "=================================================================="
info "演示环境初始化完成"
log ""
log "启动服务："
log "  KERT(8107): cd ${KERT_ROOT} && KERT_PROFILE=dev KERT_REPO_ROOT=\$PWD \\"
log "              KERT_SKILL_PACKAGES=\$PWD/examples/bank-front-skills \\"
log "              ${KERT_PY} scripts/serve_skill_service.py --port 8107 --host 127.0.0.1 \\"
log "              --workspace ${KERT_ROOT}/bank_front_ws"
log "  GITS(8080): cd ${GITS_ROOT} && mvn -q -pl apps/api -am spring-boot:run"
log "  前端(5173): cd ${GITS_ROOT}/frontend && npm ci && npm run dev"
log "=================================================================="
