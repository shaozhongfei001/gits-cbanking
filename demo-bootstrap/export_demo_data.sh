#!/usr/bin/env bash
# 导出 GITS + KERT 全部测试/验证/演示数据到 demo-bootstrap/bundle/。
#
# 设计要点：
#   1. KERT 的 bank_front_ws/、*.kuzu、*.duckdb 被 .gitignore 排除，git clone 拿不到，
#      必须由本脚本导出，否则目标机演示环境无法重建。
#   2. GITS 的数据（scenario/seed、specs/**）已在 git 中，但仍导出一份到 bundle，
#      使数据包可离线传输、不依赖目标机的 git 访问权限。
#   3. 导出结束生成 MANIFEST.json（每项含文件数/体积/sha256），供目标机校验。
#
# 用法：
#   ./export_demo_data.sh                 # 完整导出
#   ./export_demo_data.sh --slim          # 剔除 90_control/jobs 历史执行结果（省 ~6.6M）
#   ./export_demo_data.sh --no-gits       # 只导出 KERT 侧（GITS 数据走 git）
#   ./export_demo_data.sh --tarball       # 额外打包为 tar.gz 便于传输
#   ./export_demo_data.sh --dest <dir>    # 指定导出目录（默认 bundle/）

set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/common.sh"

SLIM=0
NO_GITS=0
TARBALL=0
DEST="${BUNDLE_DIR}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --slim)     SLIM=1; shift ;;
    --no-gits)  NO_GITS=1; shift ;;
    --tarball)  TARBALL=1; shift ;;
    --dest)     DEST="${2:?--dest 需要参数}"; shift 2 ;;
    -h|--help)  sed -n '2,20p' "${BASH_SOURCE[0]}"; exit 0 ;;
    *)          die "未知参数: $1（用 --help 查看用法）" ;;
  esac
done

log "=================================================================="
log " GITS + KERT 演示数据导出"
log "=================================================================="
log "GITS_ROOT : ${GITS_ROOT}"
log "KERT_ROOT : ${KERT_ROOT}"
log "导出目标  : ${DEST}"
log "模式      : $([[ $SLIM -eq 1 ]] && echo slim || echo full) / $([[ $NO_GITS -eq 1 ]] && echo 'KERT only' || echo 'GITS+KERT')"
log ""

assert_dir "${KERT_ROOT}" "KERT 仓库根目录（可用 KERT_ROOT 环境变量覆盖）"

# 准备导出目录（覆盖式：已存在时同名文件被覆盖，重复导出幂等）
mkdir -p "${DEST}/kert" "${DEST}/gits"
MANIFEST="${DEST}/MANIFEST.json"

# ---------------------------------------------------------------- 工具函数
# 记录一项导出结果到 MANIFEST（追加 JSON 片段到临时文件）
manifest_items=()
add_manifest() {
  # add_manifest <name> <kind> <源路径> <目标相对路径> [备注]
  local name="$1" kind="$2" src="$3" rel="$4" note="${5:-}"
  local files size sha
  if [[ -f "${DEST}/${rel}" ]]; then
    files=1
    sha=$(sha256_file "${DEST}/${rel}")
  else
    files=$(count_files "${DEST}/${rel}")
    sha="(dir)"
  fi
  size=$(dir_bytes "${DEST}/${rel}")
  manifest_items+=("$(printf '  {\n    "name": "%s",\n    "kind": "%s",\n    "source": "%s",\n    "target": "%s",\n    "files": %s,\n    "size": "%s",\n    "sha256": "%s",\n    "note": "%s"\n  }' \
    "$name" "$kind" "$src" "$rel" "$files" "$size" "$sha" "$note")")
  info "$(printf '%-42s %6s 文件  %8s' "$name" "$files" "$size")"
}

# copy_dir <源> <目标相对路径>
copy_dir() {
  local src="$1" rel="$2"
  mkdir -p "$(dirname "${DEST}/${rel}")"
  if command -v rsync >/dev/null 2>&1; then
    rsync -a --quiet "${src}/" "${DEST}/${rel}/"
  else
    cp -a "${src}/." "${DEST}/${rel}/"
  fi
}

copy_file() {
  local src="$1" rel="$2"
  mkdir -p "$(dirname "${DEST}/${rel}")"
  cp -a "${src}" "${DEST}/${rel}"
}

# ================================================================ KERT 侧
step "导出 KERT 侧数据"

# 1) 工作区 bank_front_ws（五层 + 90_control），gitignored，重建演示环境的核心
if [[ -d "${KERT_ROOT}/bank_front_ws" ]]; then
  if [[ $SLIM -eq 1 ]]; then
    # 排除 90_control/jobs 下的历史执行结果，它们是运行痕迹而非演示数据
    mkdir -p "${DEST}/kert/bank_front_ws"
    if command -v rsync >/dev/null 2>&1; then
      rsync -a --quiet --exclude '90_control/jobs/' \
        "${KERT_ROOT}/bank_front_ws/" "${DEST}/kert/bank_front_ws/"
    else
      (cd "${KERT_ROOT}/bank_front_ws" && find . -type f \
         -not -path './90_control/jobs/*' -print0 \
         | while IFS= read -r -d '' f; do
             mkdir -p "${DEST}/kert/bank_front_ws/$(dirname "$f")"
             cp -a "$f" "${DEST}/kert/bank_front_ws/$f"
           done)
    fi
    add_manifest "KERT 工作区 bank_front_ws" "workspace" \
      "${KERT_ROOT}/bank_front_ws" "kert/bank_front_ws" \
      "五层结构+90_control；slim 模式已剔除 jobs 历史执行结果"
  else
    copy_dir "${KERT_ROOT}/bank_front_ws" "kert/bank_front_ws"
    add_manifest "KERT 工作区 bank_front_ws" "workspace" \
      "${KERT_ROOT}/bank_front_ws" "kert/bank_front_ws" \
      "01_raw/02_work/03_core/04_serve/90_control 全量"
  fi
else
  warn "未找到 ${KERT_ROOT}/bank_front_ws，跳过（目标机将改用重新生成路径）"
fi

# 2) Kuzu 产品知识图库（SP-15 原型库），gitignored
if [[ -e "${KERT_ROOT}/data/product_knowledge_graph.kuzu" ]]; then
  copy_file "${KERT_ROOT}/data/product_knowledge_graph.kuzu" \
    "kert/data/product_knowledge_graph.kuzu"
  add_manifest "Kuzu 产品知识图库" "graph-db" \
    "${KERT_ROOT}/data/product_knowledge_graph.kuzu" \
    "kert/data/product_knowledge_graph.kuzu" \
    "SP-15 产品推荐原型库；也可由 scripts/graph/init_product_knowledge_graph.py 重建"
else
  warn "未找到 data/product_knowledge_graph.kuzu，跳过"
fi

# 3) DuckDB 对公经营分析库，gitignored
if [[ -f "${KERT_ROOT}/examples/bank-front-analytics/cb_analytics.duckdb" ]]; then
  copy_file "${KERT_ROOT}/examples/bank-front-analytics/cb_analytics.duckdb" \
    "kert/analytics/cb_analytics.duckdb"
  add_manifest "DuckDB 分析库 cb_analytics" "duckdb" \
    "${KERT_ROOT}/examples/bank-front-analytics/cb_analytics.duckdb" \
    "kert/analytics/cb_analytics.duckdb" \
    "7 张表；也可由 seed/*.csv 经 build_analytics_duckdb.py 重建"
else
  warn "未找到 cb_analytics.duckdb，跳过（可由 seed CSV 重建）"
fi

# 4) DuckDB 造数 CSV（仓库内已有，导出保证离线可用）
if [[ -d "${KERT_ROOT}/examples/bank-front-analytics/seed" ]]; then
  copy_dir "${KERT_ROOT}/examples/bank-front-analytics/seed" "kert/analytics/seed"
  add_manifest "DuckDB 造数 CSV" "csv-seed" \
    "${KERT_ROOT}/examples/bank-front-analytics/seed" "kert/analytics/seed" \
    "7 个 CSV；上游生成器 scripts/gen_seed_data.py 本仓缺失，必须随包带走"
else
  warn "未找到 examples/bank-front-analytics/seed，跳过"
fi

# 5) 产品演示输入
if [[ -d "${KERT_ROOT}/examples/product_demo/inputs" ]]; then
  copy_dir "${KERT_ROOT}/examples/product_demo/inputs" "kert/product_demo_inputs"
  add_manifest "product_demo 输入" "demo-input" \
    "${KERT_ROOT}/examples/product_demo/inputs" "kert/product_demo_inputs" \
    "product.parquet + 产品手册/政策 md；run_demo.py 会重写 parquet"
fi

# 6) 演示产出样例（报告/图谱 HTML）
if [[ -d "${KERT_ROOT}/examples/output" ]]; then
  copy_dir "${KERT_ROOT}/examples/output" "kert/output"
  add_manifest "演示产出样例 examples/output" "demo-output" \
    "${KERT_ROOT}/examples/output" "kert/output" \
    "CRM 主档、访前报告、供应链图谱 HTML 等展示产物"
fi

# 7) SQLite Runtime Store（本机通常不存在；若存在则导出）
RUNTIME_DB="${KERT_ROOT}/bank_front_ws/90_control/runtime/runtime.db"
if [[ -f "${RUNTIME_DB}" ]]; then
  copy_file "${RUNTIME_DB}" "kert/runtime/runtime.db"
  add_manifest "SQLite Runtime Store" "sqlite" "$RUNTIME_DB" "kert/runtime/runtime.db" \
    "jobs/idempotency/evidence_audit/gate_audit 表"
else
  info "$(printf '%-42s %s' 'SQLite Runtime Store' '本机不存在（worker 未启用持久化），目标机将自动建库')"
fi

# ================================================================ GITS 侧
if [[ $NO_GITS -eq 0 ]]; then
  step "导出 GITS 侧数据"
  assert_dir "${GITS_ROOT}" "GITS 仓库根目录"

  # 1) 场景种子包（演示主数据：客户/银行流水/知识/交互/UI 状态/API fixture）
  if [[ -d "${GITS_ROOT}/scenario/seed" ]]; then
    copy_dir "${GITS_ROOT}/scenario/seed" "gits/scenario-seed"
    add_manifest "GITS 场景种子包 scenario/seed" "seed-package" \
      "${GITS_ROOT}/scenario/seed" "gits/scenario-seed" \
      "20 个子目录：主数据/银行数据/知识资产/交互/UI状态/API fixture/GK-KE 仿真集"
  fi

  # 2) Flyway 迁移脚本（H2 + MySQL 两套）
  if [[ -d "${GITS_ROOT}/adapters/persistence-relational/src/main/resources/db/migration" ]]; then
    copy_dir "${GITS_ROOT}/adapters/persistence-relational/src/main/resources/db/migration" \
      "gits/db-migration"
    add_manifest "Flyway 迁移脚本" "sql-migration" \
      "${GITS_ROOT}/adapters/persistence-relational/src/main/resources/db/migration" \
      "gits/db-migration" "H2 24 个 / MySQL 21 个（MySQL 缺 V014/V015/V016）"
  fi

  # 3) 知识架构（运行时内存加载的权威资产）
  if [[ -d "${GITS_ROOT}/specs/knowledge-architecture" ]]; then
    copy_dir "${GITS_ROOT}/specs/knowledge-architecture" "gits/knowledge-architecture"
    add_manifest "知识架构 specs/knowledge-architecture" "knowledge-assets" \
      "${GITS_ROOT}/specs/knowledge-architecture" "gits/knowledge-architecture" \
      "启动时由 KnowledgeSnapshotLoader 全量读入内存"
  fi

  # 4) 产品知识（分类骨架权威源 + 产品卡 + 契约）
  if [[ -d "${GITS_ROOT}/specs/product-knowledge" ]]; then
    copy_dir "${GITS_ROOT}/specs/product-knowledge" "gits/product-knowledge"
    add_manifest "产品知识 specs/product-knowledge" "product-knowledge" \
      "${GITS_ROOT}/specs/product-knowledge" "gits/product-knowledge" \
      "product-taxonomy.yaml 为产品中心分类骨架权威源，缺失则 503"
  fi

  # 5) 源合同与大种子数据（2.84MB oracle-seed-claims，仅 E2E 读取）
  if [[ -d "${GITS_ROOT}/specs/data" ]]; then
    copy_dir "${GITS_ROOT}/specs/data" "gits/specs-data"
    add_manifest "源合同与种子数据 specs/data" "source-contract" \
      "${GITS_ROOT}/specs/data" "gits/specs-data" \
      "oracle-seed-claims 2505 条等，仅 MechanismE2eIT 读取"
  fi
fi

# ================================================================ MANIFEST
step "生成 MANIFEST.json"
{
  printf '{\n'
  printf '  "schema": "gits-kert-demo-bundle/v1",\n'
  printf '  "exported_at": "%s",\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf '  "exported_by": "%s",\n' "$(hostname 2>/dev/null || echo unknown)"
  printf '  "mode": "%s",\n' "$([[ $SLIM -eq 1 ]] && echo slim || echo full)"
  printf '  "includes_gits": %s,\n' "$([[ $NO_GITS -eq 1 ]] && echo false || echo true)"
  printf '  "gits_root": "%s",\n' "${GITS_ROOT}"
  printf '  "kert_root": "%s",\n' "${KERT_ROOT}"
  printf '  "items": [\n'
  first=1
  for it in "${manifest_items[@]}"; do
    [[ $first -eq 1 ]] || printf ',\n'
    printf '%s' "$it"
    first=0
  done
  printf '\n  ]\n}\n'
} > "${MANIFEST}"

TOTAL_FILES=$(count_files "${DEST}")
TOTAL_SIZE=$(dir_bytes "${DEST}")
info "MANIFEST: ${MANIFEST}"

# ================================================================ 打包
if [[ $TARBALL -eq 1 ]]; then
  step "打包 tar.gz"
  TARBALL_PATH="${BOOTSTRAP_DIR}/gits-kert-demo-bundle-$(date +%Y%m%d).tar.gz"
  tar -czf "${TARBALL_PATH}" -C "$(dirname "${DEST}")" "$(basename "${DEST}")"
  info "打包完成: ${TARBALL_PATH} ($(dir_bytes "${TARBALL_PATH}"))"
fi

log ""
log "=================================================================="
info "导出完成：${TOTAL_FILES} 个文件，${TOTAL_SIZE}"
log "目录：${DEST}"
log ""
log "目标机重建演示环境："
log "  cd ${BOOTSTRAP_DIR} && ./init_demo_env.sh --bundle ${DEST}"
log "=================================================================="
