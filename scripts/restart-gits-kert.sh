#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# 本地开发栈：GITS（前端 15173 + 后端 18080）与 KERT 技能服务（8107，含 analytics）
#
# 用法：
#   scripts/restart-gits-kert.sh              # 默认 = up（停 → 起 → 等就绪 → 验证）
#   scripts/restart-gits-kert.sh up
#   scripts/restart-gits-kert.sh down
#   scripts/restart-gits-kert.sh status
#   scripts/restart-gits-kert.sh up --with-lightrag     # 连 LightRAG(9621) 一起重启
#
# 可覆盖的变量（环境变量）：
#   GITS_ROOT  = /home/szf/dev/gits-cbanking     仓库根
#   KERT_ROOT  = /home/szf/dev/Leibniz-KERT      KERT 仓根
#   HOST       = 127.0.0.1
#   FE_PORT    = 15173    API_PORT = 18080    SKILL_PORT = 8107    LIGHTRAG_PORT = 9621
#   LOG_DIR    = /tmp/restart-gits-kert-<UTC 时间戳>     各服务 stdout/stderr 落此处
#   KERT_LIGHTRAG_API_KEY   KERT→LightRAG 检索键（**不设只告警**，绝不回退读仓内文件）
#   LIGHTRAG_BIN = /tmp/lr-venv/bin/lightrag-server      （--with-lightrag 时使用）
#   KERT 技能运行时 LLM（OpenAI 兼容；适配器自动补 /chat/completions）：
#     KERT_LLM_MODEL       默认 Qwen3.6-27B
#     KERT_LLM_BASE_URL    默认 http://10.62.64.38:30808/api/inference/v1
#     LR_KERT_LLM_API_KEY  **API Key 仅从此 env 读，绝不写入本跟踪文件**（不设 ⇒ KERT 回退确定性适配器）
#   LightRAG server 自身的索引/查询 LLM（OpenAI 兼容绑定；仅注入 lightrag 子进程，不污染 GITS 后端同名 LLM_*）：
#     LR_LLM_BINDING       默认 openai
#     LR_LLM_MODEL         默认 Qwen3.6-27B
#     LR_LLM_BASE_URL      默认 http://10.62.64.38:30808/api/inference/v1
#     LR_LLM_API_KEY       **API Key 仅从此 env 读，绝不写入本跟踪文件**（不设 ⇒ 抽取 LLM 可能不可用）
#
# 设计要点（踩过的坑）：
#   * 前端必须**直接调用 vite 二进制**：`npm run dev --port …` 会被 npm 当自身配置吃掉
#     （缺 `--` ⇒ vite 只拿到位置参数 ⇒ CACError: Unused args），故此处不复刻 npm 形式。
#   * 8107 **必须带 KERT_ANALYTICS_DUCKDB**，否则 /v1/analytics/* 返回 503。
#   * 停止只按精确模式匹配，绝不误伤 8106(dkws) 等其他 workspace 的同名服务。
#   * 本脚本不做任何 git 操作，也不修改仓库文件（只读仓库 + 写 LOG_DIR）。
# ─────────────────────────────────────────────────────────────────────────────
set -uo pipefail

GITS_ROOT="${GITS_ROOT:-/home/szf/dev/gits-cbanking}"
KERT_ROOT="${KERT_ROOT:-/home/szf/dev/Leibniz-KERT}"
HOST="${HOST:-127.0.0.1}"
FE_PORT="${FE_PORT:-15173}"
API_PORT="${API_PORT:-18080}"
SKILL_PORT="${SKILL_PORT:-8107}"
LIGHTRAG_PORT="${LIGHTRAG_PORT:-9621}"
LIGHTRAG_BIN="${LIGHTRAG_BIN:-/tmp/lr-venv/bin/lightrag-server}"
LOG_DIR="${LOG_DIR:-/tmp/restart-gits-kert-$(date -u +%Y%m%dT%H%M%SZ)}"

# 可选：本地未跟踪密钥文件（.lr-kert.local.env，已 gitignore；含 LR_KERT_LLM_API_KEY / LR_LLM_API_KEY）
# 存在则自动 source（set -a 使其导出为环境），免去每次手动 export；不存在则跳过。
_LOCAL_ENV="${GITS_ROOT:-.}/.lr-kert.local.env"
if [ -f "$_LOCAL_ENV" ]; then
  set -a; . "$_LOCAL_ENV"; set +a
fi

JAR="$GITS_ROOT/apps/api/target/gits-kno-api-0.1.0-SNAPSHOT.jar"
KERT_PY="$KERT_ROOT/.venv/bin/python"
KERT_DUCKDB="$KERT_ROOT/examples/bank-front-analytics/cb_analytics.duckdb"
ASSETS="$KERT_ROOT/examples/product-recommendation-assets"

say()  { printf '  %s\n' "$*"; }
warn() { printf '  ⚠ %s\n' "$*" >&2; }
die()  { printf '  ✗ %s\n' "$*" >&2; exit 1; }
http() { curl -s -o /dev/null -w '%{http_code}' --max-time "${2:-6}" "$1" 2>/dev/null || echo 000; }

stop_stack() {
  say "停止：GITS 前端($FE_PORT) · GITS 后端($API_PORT) · KERT 技能($SKILL_PORT)${1:+ · LightRAG($LIGHTRAG_PORT)}"
  pkill -f "vite --port $FE_PORT"                     2>/dev/null
  pkill -f "npm run dev --port $FE_PORT"              2>/dev/null
  pkill -f "gits-kno-api-0.1.0-SNAPSHOT.jar"          2>/dev/null
  pkill -f "serve_skill_service.py --port $SKILL_PORT" 2>/dev/null
  [ -n "${1:-}" ] && pkill -f "lightrag-server --host $HOST --port $LIGHTRAG_PORT" 2>/dev/null
  local n
  for _ in $(seq 1 20); do
    n=$(ss -ltn 2>/dev/null | grep -cE ":$FE_PORT|:$API_PORT|:$SKILL_PORT")
    [ "$n" -eq 0 ] && break
    sleep 1
  done
  if ss -ltn 2>/dev/null | grep -qE ":$FE_PORT|:$API_PORT|:$SKILL_PORT"; then
    warn "仍有监听 ⇒ 强制收尾（仅精确模式）"
    pkill -9 -f "vite --port $FE_PORT"                     2>/dev/null
    pkill -9 -f "gits-kno-api-0.1.0-SNAPSHOT.jar"          2>/dev/null
    pkill -9 -f "serve_skill_service.py --port $SKILL_PORT" 2>/dev/null
    sleep 3
  fi
  say "停止后本栈监听数（应为 0）: $(ss -ltn 2>/dev/null | grep -cE ":$FE_PORT|:$API_PORT|:$SKILL_PORT")"
}

start_kert() {
  say "启动 KERT 技能 $SKILL_PORT（工作区 bank_front_ws）"
  [ -x "$KERT_PY" ] || die "KERT venv 不存在: $KERT_PY"
  [ -f "$KERT_DUCKDB" ] || warn "analytics DuckDB 缺失: $KERT_DUCKDB ⇒ /v1/analytics/* 将 503"
  [ -n "${KERT_LIGHTRAG_API_KEY:-}" ] || warn "KERT_LIGHTRAG_API_KEY 未设置 ⇒ KERT→LightRAG 检索可能 401"
  # KERT 技能运行时 LLM（OpenAI 兼容；KERT_LLM_BASE_URL 由适配器自动补 /chat/completions）
  local kert_llm_model="${KERT_LLM_MODEL:-Qwen3.6-27B}"
  local kert_llm_base_url="${KERT_LLM_BASE_URL:-http://10.62.64.38:30808/api/inference/v1}"
  local kert_llm_api_key="${LR_KERT_LLM_API_KEY:-${KERT_LLM_API_KEY:-}}"
  [ -n "$kert_llm_api_key" ] || warn "LR_KERT_LLM_API_KEY 未设置 ⇒ KERT 回退确定性适配器（无真实 LLM 推理）"
  cd "$KERT_ROOT" || die "无法进入 $KERT_ROOT"
  env KERT_PROFILE=dev \
      KERT_REPO_ROOT="$KERT_ROOT" \
      KERT_SKILL_PACKAGES="$KERT_ROOT/examples/bank-front-skills" \
      KERT_LIGHTRAG_URL="http://$HOST:$LIGHTRAG_PORT" \
      KERT_LIGHTRAG_API_KEY="${KERT_LIGHTRAG_API_KEY:-}" \
      KERT_ANALYTICS_DUCKDB="$KERT_DUCKDB" \
      KERT_LLM_MODEL="$kert_llm_model" \
      KERT_LLM_BASE_URL="$kert_llm_base_url" \
      KERT_LLM_API_KEY="$kert_llm_api_key" \
    setsid nohup "$KERT_PY" scripts/serve_skill_service.py \
      --port "$SKILL_PORT" --host "$HOST" --workspace "$KERT_ROOT/bank_front_ws" \
      > "$LOG_DIR/kert-$SKILL_PORT.log" 2>&1 < /dev/null &
}

start_api() {
  say "启动 GITS 后端 $API_PORT（资产目录 → KERT examples/product-recommendation-assets）"
  [ -f "$JAR" ] || die "后端 jar 不存在: $JAR（先 mvn -pl apps/api package -DskipTests）"
  for d in "$ASSETS/04_serve/interpretation" "$ASSETS/03_core" "$ASSETS/04_serve/product-center"; do
    [ -d "$d" ] || warn "资产目录缺失: $d"
  done
  cd "$GITS_ROOT" || die "无法进入 $GITS_ROOT"
  setsid nohup java -jar "$JAR" --server.port="$API_PORT" \
    --gits.product-knowledge.snapshot-dir="$ASSETS/04_serve/interpretation" \
    --gits.product-knowledge.card-dir="$ASSETS/03_core" \
    --gits.product-center.section-dir="$ASSETS/04_serve/product-center" \
    > "$LOG_DIR/gits-api-$API_PORT.log" 2>&1 < /dev/null &
}

start_fe() {
  say "启动 GITS 前端 $FE_PORT（VITE_API_PROXY_TARGET=http://$HOST:$API_PORT）"
  cd "$GITS_ROOT/frontend" || die "无法进入 $GITS_ROOT/frontend"
  [ -x ./node_modules/.bin/vite ] || die "vite 未安装: $GITS_ROOT/frontend/node_modules/.bin/vite"
  VITE_API_PROXY_TARGET="http://$HOST:$API_PORT" setsid nohup ./node_modules/.bin/vite \
    --port "$FE_PORT" --host "$HOST" > "$LOG_DIR/gits-fe-$FE_PORT.log" 2>&1 < /dev/null &
}

start_lightrag() {
  say "启动 LightRAG $LIGHTRAG_PORT"
  [ -x "$LIGHTRAG_BIN" ] || die "lightrag-server 不存在: $LIGHTRAG_BIN（默认在 /tmp/lr-venv，若被清理需重建）"
  # LightRAG server 自身的索引/查询 LLM（OpenAI 兼容绑定；仅注入本子进程，不污染 GITS 后端同名 LLM_*）
  local lr_llm_binding="${LR_LLM_BINDING:-openai}"
  local lr_llm_model="${LR_LLM_MODEL:-Qwen3.6-27B}"
  local lr_llm_base_url="${LR_LLM_BASE_URL:-http://10.62.64.38:30808/api/inference/v1}"
  local lr_llm_api_key="${LR_LLM_API_KEY:-}"
  [ -n "$lr_llm_api_key" ] || warn "LR_LLM_API_KEY 未设置 ⇒ LightRAG 实体/关系抽取 LLM 可能不可用"
  cd "$GITS_ROOT"
  setsid nohup env LLM_BINDING="$lr_llm_binding" LLM_MODEL="$lr_llm_model" \
      LLM_BASE_URL="$lr_llm_base_url" LLM_API_KEY="$lr_llm_api_key" \
    "$LIGHTRAG_BIN" --host "$HOST" --port "$LIGHTRAG_PORT" --workers 1 \
    > "$LOG_DIR/lightrag-$LIGHTRAG_PORT.log" 2>&1 < /dev/null &
}

wait_ready() {
  say "等待就绪（最多 120s）…"
  local k a f
  for _ in $(seq 1 60); do
    k=$(http "http://$HOST:$SKILL_PORT/v1/health" 3)
    a=$(http "http://$HOST:$API_PORT/actuator/health" 3)
    f=$(http "http://$HOST:$FE_PORT/" 3)
    [ "$k" = 200 ] && [ "$a" = 200 ] && [ "$f" = 200 ] && break
    sleep 2
  done
  say "健康：KERT $SKILL_PORT=$k · GITS 后端 $API_PORT=$a · GITS 前端 $FE_PORT=$f"
}

verify() {
  say "KERT 分析端点 /v1/analytics/screens = $(http "http://$HOST:$SKILL_PORT/v1/analytics/screens")"
  say "GITS 产品中心 API = $(http "http://$HOST:$API_PORT/api/v1/product-center/products")"
  say "GITS 产品卡 API   = $(http "http://$HOST:$API_PORT/api/v1/product-knowledge/cards/PROD-CM-003")"
  [ -x "$LIGHTRAG_BIN" ] && say "LightRAG $LIGHTRAG_PORT = $(http "http://$HOST:$LIGHTRAG_PORT/health" 5)"
  echo "LOG_DIR=$LOG_DIR"
}

st_row() {  # name port pgrep-pattern health-url
  local name="$1" port="$2" pat="$3" url="$4" listen pids
  listen=$(ss -ltn 2>/dev/null | grep -c ":$port ")
  pids=$(pgrep -f "$pat" 2>/dev/null | tr '\n' ',' | sed 's/,$//')
  printf '  %-10s :%-5s 监听=%s  PID=%-9s HTTP=%s\n' \
    "$name" "$port" "$listen" "${pids:--}" "$(http "$url" 5)"
}

status() {
  say "服务       端口   监听  进程         健康"
  st_row "GITS 前端"  "$FE_PORT"       "vite --port $FE_PORT"                          "http://$HOST:$FE_PORT/"
  st_row "GITS 后端"  "$API_PORT"      "gits-kno-api-0.1.0-SNAPSHOT.jar"               "http://$HOST:$API_PORT/actuator/health"
  st_row "KERT 技能"  "$SKILL_PORT"    "serve_skill_service.py --port $SKILL_PORT"     "http://$HOST:$SKILL_PORT/v1/health"
  st_row "LightRAG"   "$LIGHTRAG_PORT" "lightrag-server.*--port $LIGHTRAG_PORT"        "http://$HOST:$LIGHTRAG_PORT/health"
  printf '  %-10s :%-5s                                   HTTP=%s\n' \
    "KERT 分析" "$SKILL_PORT" "$(http "http://$HOST:$SKILL_PORT/v1/analytics/screens" 6)"
}

CMD="${1:-up}"; shift || true
WITH_LIGHTRAG=""
for a in "$@"; do [ "$a" = "--with-lightrag" ] && WITH_LIGHTRAG=1; done

case "$CMD" in
  down)   stop_stack "$WITH_LIGHTRAG" ;;
  status) status ;;
  up|restart)
    mkdir -p "$LOG_DIR" || die "无法创建 LOG_DIR=$LOG_DIR"
    say "GITS_ROOT=$GITS_ROOT  KERT_ROOT=$KERT_ROOT  LOG_DIR=$LOG_DIR"
    stop_stack "$WITH_LIGHTRAG"
    [ -n "$WITH_LIGHTRAG" ] && start_lightrag
    start_kert
    start_api
    start_fe
    wait_ready
    verify
    ;;
  *) die "未知子命令: $CMD（可用：up | down | status | restart）" ;;
esac
