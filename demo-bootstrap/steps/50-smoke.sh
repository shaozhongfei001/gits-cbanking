#!/usr/bin/env bash
# 步骤 5：冒烟验证 —— 输出最终数据资产状态总表。
# 只做存在性与关键断言，不启动服务、不写数据库。

set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/lib/common.sh"

WS="${KERT_ROOT}/bank_front_ws"
FAILED=0

# check <说明> <路径> [类型: dir|file]
check() {
  local desc="$1" path="$2" kind="${3:-dir}"
  if [[ "${kind}" == "dir" && -d "${path}" ]]; then
    printf '  %s✓%s %-46s %8s\n' "$C_GRN" "$C_RESET" "$desc" "$(dir_bytes "${path}")"
  elif [[ "${kind}" == "file" && -f "${path}" ]]; then
    printf '  %s✓%s %-46s %8s\n' "$C_GRN" "$C_RESET" "$desc" "$(dir_bytes "${path}")"
  else
    printf '  %s✗%s %-46s %8s\n' "$C_RED" "$C_RESET" "$desc" "缺失"
    FAILED=$((FAILED+1))
  fi
}

log ""
log "演示数据资产状态"
log "------------------------------------------------------------"
log " KERT"
if [[ ${SKIP_KERT:-0} -eq 0 ]]; then
  check "工作区 bank_front_ws"        "${WS}" dir
  check "权威知识源 03_core"          "${WS}/03_core" dir
  check "投影层 04_serve（parquet）"   "${WS}/04_serve" dir
  check "控制面 90_control"            "${WS}/90_control" dir
  check "知识地图注册表 catalog"       "${WS}/90_control/catalog" dir
  check "路由策略 route_policy.json"   "${WS}/90_control/schema/route_policy.json" file
  check "Kuzu 产品知识图库"            "${KERT_ROOT}/data/product_knowledge_graph.kuzu" file
  check "DuckDB 分析库"                "${KERT_ROOT}/examples/bank-front-analytics/cb_analytics.duckdb" file
  check "DuckDB 造数 CSV"              "${KERT_ROOT}/examples/bank-front-analytics/seed" dir
else
  log "  (已跳过)"
fi

log ""
log " GITS"
if [[ ${SKIP_GITS:-0} -eq 0 ]]; then
  check "场景种子包 scenario/seed"     "${GITS_ROOT}/scenario/seed" dir
  check "Flyway 迁移（H2）"            "${GITS_ROOT}/adapters/persistence-relational/src/main/resources/db/migration/h2" dir
  check "知识架构"                     "${GITS_ROOT}/specs/knowledge-architecture" dir
  check "产品分类骨架 taxonomy"        "${GITS_ROOT}/specs/product-knowledge/product-taxonomy.yaml" file
  log "  · H2 为内存库（jdbc:h2:mem），由 Flyway + seed 启动时重建，无落盘文件"
else
  log "  (已跳过)"
fi
log "------------------------------------------------------------"

# 04_serve 版本目录与 parquet 明细
VERSION_DIR=$(ls -d "${WS}"/04_serve/customer_knowledge/version=* 2>/dev/null | head -1 || true)
if [[ -n "${VERSION_DIR}" ]]; then
  log ""
  log "投影层明细 $(basename "${VERSION_DIR}")"
  for p in entities relations segments vectors statements rules; do
    f="${VERSION_DIR}/${p}.parquet"
    [[ -f "$f" ]] && printf '  %-14s %8s\n' "${p}.parquet" "$(dir_bytes "$f")" \
                  || printf '  %-14s %8s\n' "${p}.parquet" "缺失"
  done
  [[ -e "${VERSION_DIR}/graph" ]] && printf '  %-14s %8s\n' "graph(kuzu)" "$(dir_bytes "${VERSION_DIR}/graph")"
fi

log ""
if [[ $FAILED -eq 0 ]]; then
  info "冒烟验证通过：全部数据资产就位"
else
  err "冒烟验证：${FAILED} 项缺失（详见上方 ✗ 标记）"
  exit 1
fi
