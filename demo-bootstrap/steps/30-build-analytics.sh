#!/usr/bin/env bash
# 步骤 3：DuckDB 对公经营分析库（7 张表，供 4 个分析 SKILL 使用）。
#
# 门禁：KERT_ANALYTICS_DUCKDB 未设置 ⇒ 分析能力不注册；
#       已设置但库文件缺失 ⇒ KERT 启动即失败。所以库必须真实存在。
#
# regen 依赖 examples/bank-front-analytics/seed 的 7 个 CSV
# （上游生成器 scripts/gen_seed_data.py 本仓缺失，CSV 必须随包带走）。

set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/lib/common.sh"

DB="${KERT_ROOT}/examples/bank-front-analytics/cb_analytics.duckdb"
SEED_DIR="${KERT_ROOT}/examples/bank-front-analytics/seed"
BUNDLE_DB="${BUNDLE:-${BUNDLE_DIR}}/kert/analytics/cb_analytics.duckdb"
BUNDLE_SEED="${BUNDLE:-${BUNDLE_DIR}}/kert/analytics/seed"
BUILD_SCRIPT="${KERT_ROOT}/scripts/build_analytics_duckdb.py"

# 造数 CSV 缺失时，优先从 bundle 补齐（gen_seed_data.py 本仓不存在，无法凭空生成）
if [[ $(count_files "${SEED_DIR}") -eq 0 && -d "${BUNDLE_SEED}" ]]; then
  step "补齐造数 CSV（从 bundle）"
  mkdir -p "${SEED_DIR}"
  if command -v rsync >/dev/null 2>&1; then
    rsync -a --quiet "${BUNDLE_SEED}/" "${SEED_DIR}/"
  else
    cp -a "${BUNDLE_SEED}/." "${SEED_DIR}/"
  fi
fi

USE_REGEN=${REGEN:-0}
if [[ $USE_REGEN -eq 0 && ! -f "${BUNDLE_DB}" ]]; then
  warn "bundle 中无 DuckDB 库，自动切换 regen"
  USE_REGEN=1
fi

if [[ $USE_REGEN -eq 1 ]]; then
  step "regen: 从 seed CSV 重建 DuckDB"
  assert_file "${BUILD_SCRIPT}" "DuckDB 构建脚本"
  if [[ $(count_files "${SEED_DIR}") -eq 0 ]]; then
    die "造数 CSV 缺失（${SEED_DIR}），且上游生成器 scripts/gen_seed_data.py 本仓不存在，"\
"无法重建。请提供 --bundle 数据包。"
  fi
  (cd "${KERT_ROOT}" && PYTHONPATH="${KERT_ROOT}/src" "${KERT_PY}" "${BUILD_SCRIPT}" \
     --seed "${SEED_DIR}" --db "${DB}") || die "build_analytics_duckdb.py 失败"
else
  step "restore: 从 bundle 恢复 DuckDB 库"
  mkdir -p "$(dirname "${DB}")"
  cp -a "${BUNDLE_DB}" "${DB}"
fi

assert_file "${DB}" "DuckDB 分析库"

# 校验表数量（预期 7 张）
TABLES=$(cd "${KERT_ROOT}" && PYTHONPATH="${KERT_ROOT}/src" "${KERT_PY}" - <<'PY' 2>/dev/null || echo ""
import sys, duckdb
con = duckdb.connect(sys.argv[1], read_only=True)
print(len([r[0] for r in con.execute("SHOW TABLES").fetchall()]))
PY
)
# 上面 heredoc 传参失败时回退到直接查询
if [[ -z "${TABLES}" ]]; then
  TABLES=$(cd "${KERT_ROOT}" && PYTHONPATH="${KERT_ROOT}/src" "${KERT_PY}" -c "
import duckdb
con = duckdb.connect('${DB}', read_only=True)
print(len([r[0] for r in con.execute('SHOW TABLES').fetchall()]))
" 2>/dev/null || echo "?")
fi
info "DuckDB 就绪: ${DB}（$(dir_bytes "${DB}"), 表数=${TABLES:-?}，预期 7）"

if [[ "${TABLES:-?}" != "7" && "${TABLES:-?}" != "?" ]]; then
  warn "表数 ${TABLES} != 7，分析 SKILL 可能异常"
fi
