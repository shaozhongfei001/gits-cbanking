#!/usr/bin/env bash
# 步骤 1：恢复 KERT 工作区 bank_front_ws（五层结构 + 90_control）。
#
# restore 策略：从 bundle 拷贝（逐字节一致，演示可复现）
# regen   策略：kert init → provision → seed_customer_knowledge.py
#              （不依赖 bundle，可验证生成链路，但版本目录日期会变）

set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/lib/common.sh"

WS="${KERT_ROOT}/bank_front_ws"
BUNDLE_WS="${BUNDLE:-${BUNDLE_DIR}}/kert/bank_front_ws"

# 决定是否走 regen
USE_REGEN=${REGEN:-0}
if [[ $USE_REGEN -eq 0 && ! -d "${BUNDLE_WS}" ]]; then
  warn "bundle 中无工作区数据，自动切换 regen 策略"
  USE_REGEN=1
fi

if [[ $USE_REGEN -eq 1 ]]; then
  step "regen: 初始化工作区"
  (cd "${KERT_ROOT}" && PYTHONPATH="${KERT_ROOT}/src" kert_cli init \
     --workspace "${WS}" --force) || die "kert init 失败"

  step "regen: 供给控制面（源 = examples/bank-front-knowledge-maps）"
  (cd "${KERT_ROOT}" && PYTHONPATH="${KERT_ROOT}/src" kert_cli provision \
     -w "${WS}" \
     -s "${KERT_ROOT}/examples/bank-front-knowledge-maps" --init) \
    || die "kert provision 失败"

  step "regen: 造数落库（02_work → 审核 → 03_core → 04_serve 投影）"
  (cd "${KERT_ROOT}" && PYTHONPATH="${KERT_ROOT}/src" "${KERT_PY}" \
     scripts/seed_customer_knowledge.py -w "${WS}") \
    || die "seed_customer_knowledge.py 失败"

  step "regen: 一致性校验"
  (cd "${KERT_ROOT}" && PYTHONPATH="${KERT_ROOT}/src" kert_cli validate \
     --workspace "${WS}" --mode full) || warn "validate 未通过（见上）"

else
  step "restore: 从 bundle 恢复工作区"
  if [[ -d "${WS}" ]]; then
    warn "目标已存在工作区，备份为 ${WS}.bak"
    rm -rf "${WS}.bak"
    mv "${WS}" "${WS}.bak"
  fi
  mkdir -p "$(dirname "${WS}")"
  if command -v rsync >/dev/null 2>&1; then
    rsync -a --quiet "${BUNDLE_WS}/" "${WS}/"
  else
    cp -a "${BUNDLE_WS}" "${WS}"
  fi
fi

# ---- 断言：五层结构 + 关键产物
assert_dir "${WS}/01_raw"    "工作区 01_raw"
assert_dir "${WS}/02_work"   "工作区 02_work"
assert_nonempty_dir "${WS}/03_core"  "权威知识源 03_core（regen 由 seed 脚本生成）"
assert_nonempty_dir "${WS}/04_serve" "投影层 04_serve（parquet + graph）"
assert_dir "${WS}/90_control" "控制面 90_control"

# 控制面必须已供给，否则 RoutePolicy defaultDecision=DENY 会让所有技能被拒
assert_nonempty_dir "${WS}/90_control/catalog" "知识地图注册表（provision 产物）"
assert_file "${WS}/90_control/schema/route_policy.json" "路由策略（缺失则技能全拒）"

CURRENT="${WS}/04_serve/customer_knowledge/CURRENT.md"
if [[ -f "${CURRENT}" ]]; then
  VERSION=$(grep -oP '(?<=target_version:\s)[0-9.]+' "${CURRENT}" | head -1 || true)
  info "当前投影版本: ${VERSION:-unknown}"
else
  warn "未找到 ${CURRENT}，04_serve 未发布版本"
fi

info "工作区就绪: ${WS}（$(count_files "${WS}") 文件，$(dir_bytes "${WS}")）"
