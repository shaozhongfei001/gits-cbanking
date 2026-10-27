#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════════
#  GITS + KERT 演示环境标准启动脚本
#
#  用法：
#    scripts/demo-startup.sh                          # 全栈启动（含 LightRAG）
#    scripts/demo-startup.sh up --no-lightrag         # 不启动 LightRAG
#    scripts/demo-startup.sh down                     # 全栈停止
#    scripts/demo-startup.sh status                   # 查看状态
#    scripts/demo-startup.sh check                    # 仅预检（不启动）
#    scripts/demo-startup.sh smoke                    # 启动后跑冒烟验证
#
#  启动顺序（依赖链）：
#    LightRAG(9621) → KERT(8107) → GITS API(18080) → GITS FE(15173)
#
#  密钥管理：从 .lr-kert.local.env（已 gitignore）自动加载
# ═══════════════════════════════════════════════════════════════════════════════
set -uo pipefail

GITS_ROOT="${GITS_ROOT:-/home/szf/dev/gits-cbanking}"
KERT_ROOT="${KERT_ROOT:-/home/szf/dev/Leibniz-KERT}"
HOST="${HOST:-127.0.0.1}"
FE_PORT="${FE_PORT:-15173}"
API_PORT="${API_PORT:-18080}"
SKILL_PORT="${SKILL_PORT:-8107}"
LIGHTRAG_PORT="${LIGHTRAG_PORT:-9621}"
# LightRAG 实际安装在 /home/szf/dev/lightrag（自带 .venv 与 start.sh）；
# 原默认值 /tmp/lr-venv 会被系统清理，导致 up（含 LightRAG）静默跳过。
LIGHTRAG_HOME="${LIGHTRAG_HOME:-/home/szf/dev/lightrag}"
LIGHTRAG_BIN="${LIGHTRAG_BIN:-$LIGHTRAG_HOME/.venv/bin/lightrag-server}"
LOG_DIR="${LOG_DIR:-/tmp/demo-startup-$(date -u +%Y%m%dT%H%M%SZ)}"
STARTUP_TIMEOUT="${STARTUP_TIMEOUT:-120}"

JAR="$GITS_ROOT/apps/api/target/gits-kno-api-0.1.0-SNAPSHOT.jar"
KERT_PY="$KERT_ROOT/.venv/bin/python"
KERT_DUCKDB="$KERT_ROOT/examples/bank-front-analytics/cb_analytics.duckdb"
ASSETS="$KERT_ROOT/examples/product-recommendation-assets"
KERT_SKILLS="$KERT_ROOT/examples/bank-front-skills"
KERT_WS="$KERT_ROOT/bank_front_ws"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
say()   { printf "  ${CYAN}▸${NC} %s\n" "$*"; }
ok()    { printf "  ${GREEN}✓${NC} %s\n" "$*"; }
warn()  { printf "  ${YELLOW}⚠${NC} %s\n" "$*" >&2; }
fail()  { printf "  ${RED}✗${NC} %s\n" "$*" >&2; }
die()   { printf "  ${RED}✗ FATAL${NC} %s\n" "$*" >&2; exit 1; }

# 注意：curl 超时（exit 28）时 -w 仍会输出 "000"，若再用 `|| echo 000` 拼接会得到 "000000"，
# 导致与 "000" 的字面比较全部失配。这里统一收敛为单个 "000"。
http_code() { local c; c=$(curl -s -o /dev/null -w '%{http_code}' --max-time "${2:-6}" "$1" 2>/dev/null); echo "${c:-000}"; }
http_body() { curl -s --max-time "${2:-6}" "$1" 2>/dev/null; }

# 密钥加载
_LOCAL_ENV="${GITS_ROOT}/.lr-kert.local.env"
[ -f "$_LOCAL_ENV" ] && { say "加载密钥: $_LOCAL_ENV"; set -a; . "$_LOCAL_ENV"; set +a; } || warn "密钥文件不存在: $_LOCAL_ENV"

KERT_LLM_MODEL="${KERT_LLM_MODEL:-Qwen3.6-27B}"
KERT_LLM_BASE_URL="${KERT_LLM_BASE_URL:-http://10.62.64.38:30808/api/inference/v1}"
KERT_LLM_API_KEY="${LR_KERT_LLM_API_KEY:-${KERT_LLM_API_KEY:-}}"
LR_LLM_BINDING="${LR_LLM_BINDING:-openai}"
LR_LLM_MODEL="${LR_LLM_MODEL:-Qwen3.6-27B}"
LR_LLM_BASE_URL="${LR_LLM_BASE_URL:-http://10.62.64.38:30808/api/inference/v1}"
LR_LLM_API_KEY="${LR_LLM_API_KEY:-}"

# ── 预检 ──────────────────────────────────────────────────────────────────────
preflight() {
  say "═══ 预检 ═══"
  local errors=0

  local java_ver; java_ver=$(java -version 2>&1 | awk -F'[\".]' '/version/ {print $2; exit}')
  [ "$java_ver" = "21" ] && ok "Java $java_ver" || { fail "Java 21 required, found ${java_ver:-?}"; errors=$((errors+1)); }

  local node_ver; node_ver=$(node --version 2>/dev/null | sed 's/^v//' | cut -d. -f1)
  [ "${node_ver:-0}" -ge 22 ] && ok "Node $node_ver" || { fail "Node 22+ required"; errors=$((errors+1)); }

  [ -x "$KERT_PY" ] && ok "KERT Python $($KERT_PY --version 2>&1 | cut -d' ' -f2)" || { fail "KERT venv 不存在"; errors=$((errors+1)); }
  [ -f "$JAR" ] && ok "GITS JAR ($(du -h "$JAR" | cut -f1))" || { fail "GITS JAR 不存在"; errors=$((errors+1)); }
  [ -x "$GITS_ROOT/frontend/node_modules/.bin/vite" ] && ok "Vite 已安装" || { fail "前端未安装"; errors=$((errors+1)); }
  [ -f "$KERT_DUCKDB" ] && ok "DuckDB ($(du -h "$KERT_DUCKDB" | cut -f1))" || warn "DuckDB 缺失 ⇒ analytics 将 503"
  [ -d "$KERT_SKILLS" ] && ok "KERT 技能包 ($(ls "$KERT_SKILLS" | wc -l) 个)" || { fail "KERT 技能包不存在"; errors=$((errors+1)); }

  local d; for d in "$ASSETS/04_serve/interpretation" "$ASSETS/03_core" "$ASSETS/04_serve/product-center"; do
    [ -d "$d" ] || warn "资产目录缺失: $d"
  done

  if [ -d "$KERT_WS/04_serve" ]; then
    local pq; pq=$(find "$KERT_WS/04_serve" -name "*.parquet" 2>/dev/null | wc -l)
    ok "KERT 图数据 ($pq parquet)"
  else warn "KERT 工作区图数据缺失"; fi

  # 首次 DNS/TLS 冷解析可能超过 5s，5s 阈值会偶发误报"不可达"（实测冷启动后 0.34s 即 401）。
  # 放宽到 15s 并重试一次，避免演示前误判 LLM 不可用。
  local llm_code; llm_code=$(http_code "$KERT_LLM_BASE_URL/models" 15)
  if [ "$llm_code" != "200" ] && [ "$llm_code" != "401" ]; then
    llm_code=$(http_code "$KERT_LLM_BASE_URL/models" 15)
  fi
  [ "$llm_code" = "200" ] || [ "$llm_code" = "401" ] && ok "LLM 端点可达 (HTTP=$llm_code, $KERT_LLM_BASE_URL)" || warn "LLM 端点不可达 (HTTP=$llm_code, $KERT_LLM_BASE_URL)"

  [ -n "$KERT_LLM_API_KEY" ] && ok "KERT LLM Key 已设置" || warn "LR_KERT_LLM_API_KEY 未设置 ⇒ 确定性适配器"
  [ -n "${KERT_LIGHTRAG_API_KEY:-}" ] && ok "KERT LightRAG Key 已设置" || warn "KERT_LIGHTRAG_API_KEY 未设置"
  [ -n "$LR_LLM_API_KEY" ] && ok "LightRAG LLM Key 已设置" || warn "LR_LLM_API_KEY 未设置"

  for p in "$FE_PORT" "$API_PORT" "$SKILL_PORT" "$LIGHTRAG_PORT"; do
    ss -ltn 2>/dev/null | grep -q ":$p " && warn "端口 :$p 已占用（将被释放）" || true
  done

  [ "$errors" -gt 0 ] && die "预检失败 ($errors 项)" || ok "预检通过"
}

# ── 停止 ──────────────────────────────────────────────────────────────────────
stop_stack() {
  say "═══ 停止全栈 ═══"
  local with_lr="${1:-}"
  pkill -f "vite --port $FE_PORT" 2>/dev/null
  pkill -f "gits-kno-api-0.1.0-SNAPSHOT.jar" 2>/dev/null
  pkill -f "serve_skill_service.py --port $SKILL_PORT" 2>/dev/null
  # LightRAG 由自带 start.sh 启动，命令行不含 --port（端口来自 .env），故按进程名匹配。
  [ -n "$with_lr" ] && pkill -f "lightrag-server" 2>/dev/null

  for _ in $(seq 1 30); do
    ss -ltn 2>/dev/null | grep -cE ":$FE_PORT|:$API_PORT|:$SKILL_PORT" | grep -q '^0$' && break
    sleep 1
  done
  if ss -ltn 2>/dev/null | grep -qE ":$FE_PORT|:$API_PORT|:$SKILL_PORT"; then
    warn "强制 SIGKILL"; pkill -9 -f "vite --port $FE_PORT" 2>/dev/null; pkill -9 -f "gits-kno-api" 2>/dev/null; pkill -9 -f "serve_skill_service.py --port $SKILL_PORT" 2>/dev/null; sleep 3
  fi
  ok "全栈已停止"
}

# ── 启动各服务（含健康门禁）───────────────────────────────────────────────────
start_lightrag() {
  say "═══ 启动 LightRAG :$LIGHTRAG_PORT ═══"
  [ -x "$LIGHTRAG_BIN" ] || { warn "lightrag-server 不存在（$LIGHTRAG_BIN），跳过"; return 0; }
  # 用 LightRAG 自带的 start.sh：它读取同目录 .env（LLM=DeepSeek 公网 / Embedding=Ollama all-minilm）
  # 并检查 Ollama 依赖。此处**不再**注入 LLM_* 环境变量——原注入的 LR_LLM_BASE_URL 默认值指向
  # 已不可达的内网地址，会把 .env 里可用的配置覆盖坏。
  if [ -x "$LIGHTRAG_HOME/start.sh" ]; then
    ( cd "$LIGHTRAG_HOME" && ./start.sh ) > "$LOG_DIR/lightrag.log" 2>&1 \
      || warn "LightRAG start.sh 返回非零，详见 $LOG_DIR/lightrag.log"
  else
    warn "未找到 $LIGHTRAG_HOME/start.sh，回退直接启动（依赖其 .env 已被读取）"
    ( cd "$LIGHTRAG_HOME" && setsid nohup "$LIGHTRAG_BIN" \
        > "$LOG_DIR/lightrag.log" 2>&1 < /dev/null & )
  fi
  wait_for "LightRAG" "http://$HOST:$LIGHTRAG_PORT/health" 200 || warn "LightRAG 未就绪（KERT 检索将降级）"
}

start_kert() {
  say "═══ 启动 KERT :$SKILL_PORT ═══"
  [ -x "$KERT_PY" ] || die "KERT Python 不存在"
  cd "$KERT_ROOT" || die "无法进入 $KERT_ROOT"
  env KERT_PROFILE=dev KERT_REPO_ROOT="$KERT_ROOT" KERT_SKILL_PACKAGES="$KERT_SKILLS" \
      KERT_LIGHTRAG_URL="http://$HOST:$LIGHTRAG_PORT" KERT_LIGHTRAG_API_KEY="${KERT_LIGHTRAG_API_KEY:-}" \
      KERT_ANALYTICS_DUCKDB="$KERT_DUCKDB" KERT_LLM_MODEL="$KERT_LLM_MODEL" \
      KERT_LLM_BASE_URL="$KERT_LLM_BASE_URL" KERT_LLM_API_KEY="$KERT_LLM_API_KEY" \
    setsid nohup "$KERT_PY" scripts/serve_skill_service.py \
      --port "$SKILL_PORT" --host "$HOST" --workspace "$KERT_WS" \
      > "$LOG_DIR/kert.log" 2>&1 < /dev/null &
  wait_for "KERT" "http://$HOST:$SKILL_PORT/v1/health" 200 || die "KERT 未就绪 — 日志: $LOG_DIR/kert.log"
  local a; a=$(http_code "http://$HOST:$SKILL_PORT/v1/analytics/screens" 6)
  [ "$a" = "200" ] && ok "KERT Analytics 就绪" || warn "KERT Analytics 不可用 (HTTP=$a)"
}

start_api() {
  say "═══ 启动 GITS 后端 :$API_PORT ═══"
  [ -f "$JAR" ] || die "GITS JAR 不存在"
  cd "$GITS_ROOT" || die "无法进入 $GITS_ROOT"
  setsid nohup java -jar "$JAR" --server.port="$API_PORT" \
    --gits.product-knowledge.snapshot-dir="$ASSETS/04_serve/interpretation" \
    --gits.product-knowledge.card-dir="$ASSETS/03_core" \
    --gits.product-center.section-dir="$ASSETS/04_serve/product-center" \
    > "$LOG_DIR/gits-api.log" 2>&1 < /dev/null &
  wait_for "GITS 后端" "http://$HOST:$API_PORT/actuator/health" 200 || die "GITS 后端未就绪 — 日志: $LOG_DIR/gits-api.log"
  local j; j=$(http_code "http://$HOST:$API_PORT/api/v1/engagement/journey" 6)
  [ "$j" = "200" ] && ok "种子数据可查" || warn "种子数据异常 (HTTP=$j)"
}

start_fe() {
  say "═══ 启动 GITS 前端 :$FE_PORT ═══"
  [ -x "$GITS_ROOT/frontend/node_modules/.bin/vite" ] || die "Vite 未安装"
  cd "$GITS_ROOT/frontend" || die "无法进入 frontend"
  VITE_API_PROXY_TARGET="http://$HOST:$API_PORT" VITE_KERT_PROXY_TARGET="http://$HOST:$SKILL_PORT" \
  setsid nohup ./node_modules/.bin/vite --port "$FE_PORT" --host "$HOST" \
    > "$LOG_DIR/gits-fe.log" 2>&1 < /dev/null &
  wait_for "GITS 前端" "http://$HOST:$FE_PORT/" 200 || die "GITS 前端未就绪 — 日志: $LOG_DIR/gits-fe.log"
}

wait_for() {
  local name="$1" url="$2" expected="${3:-200}" elapsed=0 code
  say "等待 $name 就绪（最多 ${STARTUP_TIMEOUT}s）…"
  while [ "$elapsed" -lt "$STARTUP_TIMEOUT" ]; do
    code=$(http_code "$url" 3)
    [ "$code" = "$expected" ] && { ok "$name 就绪 (HTTP=$code, ${elapsed}s)"; return 0; }
    sleep 2; elapsed=$((elapsed+2))
  done
  fail "$name 未就绪 (HTTP=$code, ${elapsed}s)"
  return 1
}

# ── 全栈验证 ──────────────────────────────────────────────────────────────────
verify_stack() {
  say "═══ 全栈验证 ═══"
  local pass=0 fail_count=0

  check_ep() {
    local name="$1" url="$2" expected="${3:-200}"
    local code; code=$(http_code "$url" 8)
    if [ "$code" = "$expected" ]; then ok "$name (HTTP=$code)"; pass=$((pass+1))
    else fail "$name (期望=$expected, 实际=$code)"; fail_count=$((fail_count+1)); fi
  }

  check_ep "GITS Health"       "http://$HOST:$API_PORT/actuator/health"
  check_ep "GITS 旅程列表"     "http://$HOST:$API_PORT/api/v1/engagement/journey"
  check_ep "GITS 旅程详情"     "http://$HOST:$API_PORT/api/v1/engagement/journey/a1b2c3d4-e5f6-7890-abcd-000000000004"
  check_ep "GITS 客户查询"     "http://$HOST:$API_PORT/api/v1/engagement/customer?rmId=RM-001"
  check_ep "GITS 产品中心"     "http://$HOST:$API_PORT/api/v1/product-center/products"
  check_ep "GITS 产品卡"       "http://$HOST:$API_PORT/api/v1/product-knowledge/cards/PROD-CM-003"
  check_ep "GITS 门禁"         "http://$HOST:$API_PORT/api/v1/human-gates?status=PENDING"
  check_ep "GITS CRM回写"      "http://$HOST:$API_PORT/api/v1/crm/writeback-commands"
  check_ep "KERT Health"       "http://$HOST:$SKILL_PORT/v1/health"
  check_ep "KERT Analytics"    "http://$HOST:$SKILL_PORT/v1/analytics/screens"
  check_ep "KERT 指标"         "http://$HOST:$SKILL_PORT/v1/analytics/metrics?screen=operating-customer&dim=INDUSTRY&orgId=350200&period=201012"
  check_ep "KERT 趋势"         "http://$HOST:$SKILL_PORT/v1/analytics/trend?screen=operating-customer&dim=INDUSTRY&dimValue=manufacturing&orgId=350200&period=201012&metric=custCnt"
  check_ep "KERT 知识地图"     "http://$HOST:$SKILL_PORT/v1/knowledge-maps"
  check_ep "前端→API代理"      "http://$HOST:$FE_PORT/api/v1/engagement/journey"
  check_ep "前端→KERT代理"     "http://$HOST:$FE_PORT/kert-api/v1/health"

  [ -x "$LIGHTRAG_BIN" ] && check_ep "LightRAG" "http://$HOST:$LIGHTRAG_PORT/health"

  say "结果：${GREEN}${pass} 通过${NC} / ${RED}${fail_count} 失败${NC}"
  [ "$fail_count" -gt 0 ] && warn "日志: $LOG_DIR"
  return $fail_count
}

# ── 状态 ──────────────────────────────────────────────────────────────────────
show_status() {
  say "═══ 服务状态 ═══"
  printf "  %-12s %-6s %-6s %-6s %s\n" "服务" "端口" "监听" "HTTP" "PID"
  printf "  %s\n" "$(printf '─%.0s' {1..50})"
  for svc in "GITS 前端|$FE_PORT|vite --port $FE_PORT|http://$HOST:$FE_PORT/" \
             "GITS 后端|$API_PORT|gits-kno-api|http://$HOST:$API_PORT/actuator/health" \
             "KERT 技能|$SKILL_PORT|serve_skill_service.py --port $SKILL_PORT|http://$HOST:$SKILL_PORT/v1/health" \
             "LightRAG|$LIGHTRAG_PORT|lightrag-server|http://$HOST:$LIGHTRAG_PORT/health"; do
    IFS='|' read -r name port pat url <<< "$svc"
    local listen pids code
    listen=$(ss -ltn 2>/dev/null | grep -c ":$port ")
    pids=$(pgrep -f "$pat" 2>/dev/null | tr '\n' ',' | sed 's/,$//')
    code=$(http_code "$url" 5)
    printf "  %-12s :%-5s %-6s %-6s %s\n" "$name" "$port" "$listen" "$code" "${pids:--}"
  done
}

# ── 主入口 ────────────────────────────────────────────────────────────────────
CMD="${1:-up}"; shift || true
WITH_LIGHTRAG=1
for a in "$@"; do [ "$a" = "--no-lightrag" ] && WITH_LIGHTRAG=""; done

case "$CMD" in
  check)  preflight ;;
  down)   stop_stack "$WITH_LIGHTRAG" ;;
  status) show_status ;;
  smoke)  verify_stack ;;
  up|restart)
    mkdir -p "$LOG_DIR" || die "无法创建 LOG_DIR"
    say "══════════════════════════════════════════════"
    say " GITS + KERT 演示环境启动"
    say " GITS_ROOT=$GITS_ROOT"
    say " KERT_ROOT=$KERT_ROOT"
    say " LOG_DIR =$LOG_DIR"
    say "══════════════════════════════════════════════"
    preflight || exit 1
    stop_stack "$WITH_LIGHTRAG"
    [ -n "$WITH_LIGHTRAG" ] && start_lightrag
    start_kert
    start_api
    start_fe
    verify_stack
    say "══════════════════════════════════════════════"
    ok "演示环境就绪！"
    say "前端: http://$HOST:$FE_PORT"
    say "后端: http://$HOST:$API_PORT/actuator/health"
    say "KERT: http://$HOST:$SKILL_PORT/v1/health"
    say "══════════════════════════════════════════════"
    ;;
  *) die "未知子命令: $CMD（可用：up | down | status | check | smoke | restart）" ;;
esac
