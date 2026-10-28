#!/usr/bin/env bash
# 步骤 2：Kuzu 产品知识图库（SP-15 产品推荐原型库）。
#
# 注意：此库独立于工作区，src/ 下无代码在运行时读取它，仅 SP-15 原型/演示使用。
#       regen 路径用脚本内硬编码常量重建（先删旧库，天然幂等）。

set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/lib/common.sh"

DB_PATH="${KERT_ROOT}/data/product_knowledge_graph.kuzu"
BUNDLE_DB="${BUNDLE:-${BUNDLE_DIR}}/kert/data/product_knowledge_graph.kuzu"
GEN_SCRIPT="${KERT_ROOT}/scripts/graph/init_product_knowledge_graph.py"

USE_REGEN=${REGEN:-0}
if [[ $USE_REGEN -eq 0 && ! -f "${BUNDLE_DB}" ]]; then
  warn "bundle 中无 Kuzu 库，自动切换 regen"
  USE_REGEN=1
fi

if [[ $USE_REGEN -eq 1 ]]; then
  step "regen: 重建 Kuzu 产品知识图库"
  assert_file "${GEN_SCRIPT}" "图库生成脚本"
  (cd "${KERT_ROOT}" && PYTHONPATH="${KERT_ROOT}/src" "${KERT_PY}" "${GEN_SCRIPT}") \
    || die "init_product_knowledge_graph.py 失败"
else
  step "restore: 从 bundle 恢复 Kuzu 库"
  mkdir -p "$(dirname "${DB_PATH}")"
  cp -a "${BUNDLE_DB}" "${DB_PATH}"
fi

assert_file "${DB_PATH}" "Kuzu 产品知识图库"
info "Kuzu 库就绪: ${DB_PATH}（$(dir_bytes "${DB_PATH}")）"

# 工作区投影图（这才是运行时消费的图）：由 seed/投影步骤生成，此处仅断言
WS_GRAPH="${KERT_ROOT}/bank_front_ws/04_serve/customer_knowledge/version="*/graph
# shellcheck disable=SC2086
ls -d ${WS_GRAPH} >/dev/null 2>&1 \
  && info "工作区投影图已存在" \
  || warn "工作区投影图不存在（04_serve/*/graph），技能图查询可能为空；可重跑 seed_customer_knowledge.py"
