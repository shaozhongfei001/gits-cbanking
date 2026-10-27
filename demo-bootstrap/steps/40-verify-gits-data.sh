#!/usr/bin/env bash
# 步骤 4：校验 GITS 侧数据完整性。
#
# GITS 的 H2 是内存库（jdbc:h2:mem），每次重启由 Flyway + seed 重建，
# 因此"数据完整性" = 迁移脚本齐全 + seed 包文件与 manifest.json 的 sha256 一致。
#
# 已知红线（必须报告，不静默）：
#   MySQL 方言缺 V014 / V015 / V016（H2 有 24 个脚本，MySQL 只有 21 个）。

set -euo pipefail
source "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/lib/common.sh"

SEED="${GITS_ROOT}/scenario/seed"
MIG="${GITS_ROOT}/adapters/persistence-relational/src/main/resources/db/migration"

# ---- 1. 目录存在性
assert_nonempty_dir "${SEED}" "场景种子包"
assert_dir "${GITS_ROOT}/specs/knowledge-architecture" "知识架构（运行时内存加载）"
assert_dir "${GITS_ROOT}/specs/product-knowledge" "产品知识"
assert_file "${GITS_ROOT}/specs/product-knowledge/product-taxonomy.yaml" \
  "产品中心分类骨架权威源（缺失 ⇒ 目录端点 503）"

# ---- 2. Flyway 脚本计数与方言差异
if [[ -d "${MIG}" ]]; then
  H2_N=$(find "${MIG}/h2" -name 'V*.sql' 2>/dev/null | wc -l | tr -d ' ')
  MY_N=$(find "${MIG}/mysql" -name 'V*.sql' 2>/dev/null | wc -l | tr -d ' ')
  info "Flyway 脚本：H2=${H2_N}  MySQL=${MY_N}"

  for v in V014 V015 V016; do
    if [[ -n "$(find "${MIG}/h2" -name "${v}__*.sql" 2>/dev/null)" \
       && -z "$(find "${MIG}/mysql" -name "${v}__*.sql" 2>/dev/null)" ]]; then
      warn "MySQL 方言缺 ${v}（H2 有）。若目标机用 MySQL，需补该脚本，否则演示数据不全。"
    fi
  done
else
  warn "未找到 Flyway 迁移目录：${MIG}"
fi

# ---- 3. 用 manifest.json 逐文件校验 seed 包 sha256
MANIFEST_JSON="${SEED}/manifest.json"
if [[ -f "${MANIFEST_JSON}" ]] && command -v "${KERT_PY%% *}" >/dev/null 2>&1; then
  step "按 manifest.json 校验 seed 包文件摘要"
  RESULT=$("${KERT_PY}" - <<PY
import hashlib, json, sys
from pathlib import Path
root = Path(r"${SEED}")
mf = json.loads(Path(r"${MANIFEST_JSON}").read_text(encoding="utf-8"))
files = mf.get("files") or []
checked = missing = mismatch = 0
bad = []
for f in files:
    rel = f.get("path") or f.get("name")
    want = f.get("sha256")
    if not rel or not want:
        continue
    p = root / rel
    if not p.exists():
        missing += 1
        bad.append(("MISSING", rel))
        continue
    got = hashlib.sha256(p.read_bytes()).hexdigest()
    checked += 1
    if got.lower() != str(want).lower():
        mismatch += 1
        bad.append(("SHA_MISMATCH", rel))
print(json.dumps({"total": len(files), "checked": checked,
                  "missing": missing, "mismatch": mismatch,
                  "bad": bad[:10]}))
PY
)
  echo "${RESULT}" | "${KERT_PY}" -c "
import json,sys
r=json.load(sys.stdin)
print(f\"  清单文件数={r['total']} 已校验={r['checked']} 缺失={r['missing']} 摘要不符={r['mismatch']}\")
for kind,rel in r['bad']:
    print(f\"  {kind}: {rel}\")
"
  # 读取结果判定
  MISSING=$(echo "${RESULT}" | "${KERT_PY}" -c "import json,sys; print(json.load(sys.stdin)['missing'])")
  MISMATCH=$(echo "${RESULT}" | "${KERT_PY}" -c "import json,sys; print(json.load(sys.stdin)['mismatch'])")
  if [[ "${MISSING}" != "0" || "${MISMATCH}" != "0" ]]; then
    warn "seed 包 ${MISSING} 个文件缺失、${MISMATCH} 个摘要不符（演示可能不完整）"
  else
    info "seed 包摘要全部一致"
  fi
else
  warn "未找到 ${MANIFEST_JSON}，跳过摘要校验"
fi

# ---- 4. 演示客户与 ID 体系提醒
info "演示数据要点："
log "  · 演示主客户 CUST-CORP-0003（北京绿源环保）由 V023 迁移脚本补全"
log "  · 存在两套 ID：seed JSON 用 CUST-001，Flyway/硬编码用 CUST-CORP-0001"
log "  · CUST-CORP-0004~0006 的 customer 行只在 Java 硬编码分支插入；"
log "    若设置 SCENARIO_DATA_ROOT 走 V1.1 文件分支，这 3 家客户主档不会落库"

info "GITS 数据校验完成（$(count_files "${SEED}") 个 seed 文件，$(dir_bytes "${SEED}")）"
