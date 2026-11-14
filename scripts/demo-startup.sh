#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════════
#  GITS + KERT 演示环境标准启动脚本（一条命令起、一条命令停，可反复演示）
#
#  用法：
#    scripts/demo-startup.sh up                       # 全栈启动（含 LightRAG）
#    scripts/demo-startup.sh up --no-lightrag        # 不启动 / 不停止 LightRAG
#    scripts/demo-startup.sh restart                 # = 先 stop_stack 再完整 up（与 up 同一分支）
#    scripts/demo-startup.sh down                   # 全栈停止（按 PID 文件精确停止）
#    scripts/demo-startup.sh down --no-lightrag     # 停止全栈但保留 LightRAG(9621)
#    scripts/demo-startup.sh status                 # 表格 + READY / NOT READY 判定（含冒烟）
#    scripts/demo-startup.sh status --quick         # 只看端口/PID，不做 READY 判定
#    scripts/demo-startup.sh check                  # 仅预检（不启动）
#    scripts/demo-startup.sh smoke                  # 16 端点全栈验证
#
#  启动顺序（依赖链）：
#    LightRAG(9621) → KERT(8107) → GITS API(18080) → GITS FE(15173)
#
#  日志固定落 logs/demo/（不再按时间戳新建目录），按服务分文件：
#    lightrag.log / kert.log / gits-api.log / gits-fe.log / smoke-last.log
#  PID 文件落 logs/demo/pids/<svc>.pid；停止只按该 PID（及其进程组）精确终止，
#  不再用 pkill -f 模式匹配，避免误杀同名进程。整个 logs/demo/ 已 gitignore。
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
# 固定日志目录：每次启动覆盖同名文件，事后永远找得到；可用 LOG_DIR 覆盖。
LOG_DIR="${LOG_DIR:-$GITS_ROOT/logs/demo}"
PID_DIR="$LOG_DIR/pids"
SMOKE_TIMEOUT="${SMOKE_TIMEOUT:-300}"
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

mkdir -p "$LOG_DIR" "$PID_DIR" || die "无法创建 LOG_DIR=$LOG_DIR"

# 注意：curl 超时（exit 28）时 -w 仍会输出 "000"，若再用 `|| echo 000` 拼接会得到 "000000"，
# 导致与 "000" 的字面比较全部失配。这里统一收敛为单个 "000"。
http_code() { local c; c=$(curl -s -o /dev/null -w '%{http_code}' --max-time "${2:-6}" "$1" 2>/dev/null); echo "${c:-000}"; }
http_body() { curl -s --max-time "${2:-6}" "$1" 2>/dev/null; }

# ── PID 文件 / 精确定位 ───────────────────────────────────────────────────────
write_pid() { printf '%s\n' "$2" > "$PID_DIR/$1.pid"; }
read_pid()  { local f="$PID_DIR/$1.pid"; if [ -f "$f" ]; then tr -dc '0-9' < "$f"; fi; }
pid_alive() { [ -n "${1:-}" ] && kill -0 "$1" 2>/dev/null; }

# 精确取「监听该端口」的 PID。LightRAG 由自带 start.sh 自行 daemon 化，$! 不可用；
# 统一用端口反查，登记的都是真正在监听的服务进程，不做进程名模式匹配。
port_pid() {
  ss -ltnp 2>/dev/null | awk -v p=":$1 " '
    index($0, p) && /pid=/ {
      if (match($0, /pid=[0-9]+/)) { print substr($0, RSTART+4, RLENGTH-4); exit }
    }'
}

register_pid() {
  local svc="$1" port="$2" pid
  pid=$(port_pid "$port")
  if [ -n "$pid" ]; then
    write_pid "$svc" "$pid"
    ok "$svc PID=$pid 已登记 → $PID_DIR/$svc.pid"
  else
    warn "$svc 未能登记 PID（端口 :$port 无监听进程）"
  fi
}

# 停止单个服务：优先读 PID 文件；PID 文件缺失/过期时按监听端口精确反查。
# 终止对象是该 PID 所在的进程组（setsid 起的组），可一并带走 vite/esbuild 等子进程。
stop_service() {
  local svc="$1" port="$2" name="$3" pid pgid my_pgid i
  pid=$(read_pid "$svc")
  if ! pid_alive "$pid"; then
    [ -n "$pid" ] && warn "$name PID 文件已过期 (PID=$pid)"
    pid=$(port_pid "$port")
    [ -n "$pid" ] && warn "$name 无有效 PID 文件，按监听端口 :$port 精确定位 PID=$pid"
  fi
  if [ -z "$pid" ]; then
    ok "$name 未运行"
    rm -f "$PID_DIR/$svc.pid"
    return 0
  fi

  my_pgid=$(ps -o pgid= -p "$$" 2>/dev/null | tr -dc '0-9')
  pgid=$(ps -o pgid= -p "$pid" 2>/dev/null | tr -dc '0-9')
  # 绝不向「自己所在的进程组」发信号，避免脚本自杀。
  if [ -n "$pgid" ] && [ "$pgid" != "0" ] && [ "$pgid" != "$my_pgid" ]; then
    kill -TERM -- "-$pgid" 2>/dev/null || kill -TERM "$pid" 2>/dev/null || true
  else
    kill -TERM "$pid" 2>/dev/null || true
  fi
  for i in $(seq 1 15); do
    pid_alive "$pid" || break
    sleep 1
  done
  if pid_alive "$pid"; then
    warn "$name 未优雅退出，SIGKILL (PID=$pid)"
    if [ -n "$pgid" ] && [ "$pgid" != "0" ] && [ "$pgid" != "$my_pgid" ]; then
      kill -KILL -- "-$pgid" 2>/dev/null || kill -KILL "$pid" 2>/dev/null || true
    else
      kill -KILL "$pid" 2>/dev/null || true
    fi
  fi
  rm -f "$PID_DIR/$svc.pid"
  ok "$name 已停止 (PID=$pid)"
}

# 密钥加载
_LOCAL_ENV="${GITS_ROOT}/.lr-kert.local.env"
[ -f "$_LOCAL_ENV" ] && { say "加载密钥: $_LOCAL_ENV"; set -a; . "$_LOCAL_ENV"; set +a; } || warn "密钥文件不存在: $_LOCAL_ENV"

KERT_LLM_MODEL="${KERT_LLM_MODEL:-Qwen3.6-27B}"
KERT_LLM_BASE_URL="${KERT_LLM_BASE_URL:-http://10.62.64.38:30808/api/inference/v1}"
KERT_LLM_API_KEY="${LR_KERT_LLM_API_KEY:-${KERT_LLM_API_KEY:-}}"
# LightRAG 侧不再需要 LR_LLM_*：模型统一走阿里百炼，密钥由环境变量 DASHSCOPE_API_KEY 注入（见 start_lightrag）

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

  # 04_serve/interpretation（产品解读三视图投影）已于 2026-10-28 随 GITS 下线链路删除，不再校验
  local d; for d in "$ASSETS/03_core" "$ASSETS/04_serve/product-center"; do
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
  # LightRAG 模型密钥统一取阿里百炼环境变量（.env 不落盘，见 lightrag/start.sh）
  [ -n "${DASHSCOPE_API_KEY:-}" ] && ok "LightRAG 百炼 Key 已设置" || warn "DASHSCOPE_API_KEY 未设置 ⇒ LightRAG 将启动失败"

  for p in "$FE_PORT" "$API_PORT" "$SKILL_PORT" "$LIGHTRAG_PORT"; do
    ss -ltn 2>/dev/null | grep -q ":$p " && warn "端口 :$p 已占用（将被释放）" || true
  done

  [ "$errors" -gt 0 ] && die "预检失败 ($errors 项)" || ok "预检通过"
}

# ── 停止 ──────────────────────────────────────────────────────────────────────
stop_stack() {
  say "═══ 停止全栈（按 PID 文件精确停止）═══"
  local with_lr="${1:-}"
  stop_service "gits-fe"   "$FE_PORT"   "GITS 前端"
  stop_service "gits-api"  "$API_PORT"  "GITS 后端"
  stop_service "kert"      "$SKILL_PORT" "KERT 技能"
  if [ -n "$with_lr" ]; then
    stop_service "lightrag" "$LIGHTRAG_PORT" "LightRAG"
  else
    say "保留 LightRAG :$LIGHTRAG_PORT（--no-lightrag）"
  fi

  # 端口兜底：只对仍占用演示端口的那个精确 PID 清理，绝不按进程名 pkill。
  local p pid
  for p in "$FE_PORT" "$API_PORT" "$SKILL_PORT"; do
    pid=$(port_pid "$p")
    if [ -n "$pid" ]; then
      warn "端口 :$p 仍有残留 PID=$pid，精确清理"
      kill -TERM "$pid" 2>/dev/null || true
      sleep 1
      if pid_alive "$pid"; then kill -KILL "$pid" 2>/dev/null || true; fi
    fi
  done
  ok "全栈已停止（日志: $LOG_DIR）"
}

# ── 启动各服务（含健康门禁）───────────────────────────────────────────────────
start_lightrag() {
  say "═══ 启动 LightRAG :$LIGHTRAG_PORT ═══"
  [ -x "$LIGHTRAG_BIN" ] || { warn "lightrag-server 不存在（$LIGHTRAG_BIN），跳过"; return 0; }
  # 用 LightRAG 自带的 start.sh：它读取同目录 .env（LLM/Embedding 均走阿里百炼 dashscope 兼容端点），
  # 并从环境变量 DASHSCOPE_API_KEY 注入模型密钥（密钥不落盘）。此处**不再**注入 LLM_* 环境变量——
  # 原注入的 LLM_* 默认值指向已不可达的内网地址，会把 .env 里可用的配置覆盖坏。
  if [ -x "$LIGHTRAG_HOME/start.sh" ]; then
    ( cd "$LIGHTRAG_HOME" && ./start.sh ) > "$LOG_DIR/lightrag.log" 2>&1 \
      || warn "LightRAG start.sh 返回非零，详见 $LOG_DIR/lightrag.log"
  else
    warn "未找到 $LIGHTRAG_HOME/start.sh，回退直接启动（模型密钥由 DASHSCOPE_API_KEY 注入）"
    ( cd "$LIGHTRAG_HOME" && \
      LLM_BINDING_API_KEY="${DASHSCOPE_API_KEY:-}" EMBEDDING_BINDING_API_KEY="${DASHSCOPE_API_KEY:-}" \
      setsid nohup "$LIGHTRAG_BIN" > "$LOG_DIR/lightrag.log" 2>&1 < /dev/null & )
  fi
  wait_for "LightRAG" "http://$HOST:$LIGHTRAG_PORT/health" 200 || warn "LightRAG 未就绪（KERT 检索将降级）"
  register_pid "lightrag" "$LIGHTRAG_PORT"
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
  register_pid "kert" "$SKILL_PORT"
  local a; a=$(http_code "http://$HOST:$SKILL_PORT/v1/analytics/screens" 6)
  [ "$a" = "200" ] && ok "KERT Analytics 就绪" || warn "KERT Analytics 不可用 (HTTP=$a)"
}

start_api() {
  say "═══ 启动 GITS 后端 :$API_PORT ═══"
  [ -f "$JAR" ] || die "GITS JAR 不存在"
  cd "$GITS_ROOT" || die "无法进入 $GITS_ROOT"
  setsid nohup java -jar "$JAR" --server.port="$API_PORT" \
    --gits.product-knowledge.card-dir="$ASSETS/03_core" \
    --gits.product-center.section-dir="$ASSETS/04_serve/product-center" \
    > "$LOG_DIR/gits-api.log" 2>&1 < /dev/null &
  wait_for "GITS 后端" "http://$HOST:$API_PORT/actuator/health" 200 || die "GITS 后端未就绪 — 日志: $LOG_DIR/gits-api.log"
  register_pid "gits-api" "$API_PORT"
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
  register_pid "gits-fe" "$FE_PORT"
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

  printf "  ${CYAN}▸${NC} 结果：${GREEN}%s 通过${NC} / ${RED}%s 失败${NC}\n" "$pass" "$fail_count"
  [ "$fail_count" -gt 0 ] && warn "日志: $LOG_DIR"
  return $fail_count
}

# ── 状态 + 能否演示判定 ───────────────────────────────────────────────────────
# READY 需要同时满足：4 个端口 HTTP=200 且 18 场景冒烟 0 FAIL。
# demo-smoke.sh 的退出码即 FAIL 数（0=全过），故直接取退出码；WARN（S14 已知 404）不算 FAIL。
show_status() {
  local quick="${1:-}" ports_ok=0 ports_total=0
  say "═══ 服务状态 ═══"
  say "日志: $LOG_DIR    PID: $PID_DIR"
  printf "  %-12s %-7s %-6s %-6s %-10s %s\n" "服务" "端口" "监听" "HTTP" "PID" "PID 来源"
  printf "  %s\n" "$(printf '─%.0s' {1..58})"
  local svc name key port url listen pids code src
  for svc in "GITS 前端|gits-fe|$FE_PORT|http://$HOST:$FE_PORT/" \
             "GITS 后端|gits-api|$API_PORT|http://$HOST:$API_PORT/actuator/health" \
             "KERT 技能|kert|$SKILL_PORT|http://$HOST:$SKILL_PORT/v1/health" \
             "LightRAG|lightrag|$LIGHTRAG_PORT|http://$HOST:$LIGHTRAG_PORT/health"; do
    IFS='|' read -r name key port url <<< "$svc"
    listen=$(ss -ltn 2>/dev/null | grep -c ":$port ")
    pids=$(read_pid "$key")
    src="pid文件"
    if ! pid_alive "$pids"; then pids=$(port_pid "$port"); src="端口探测"; fi
    code=$(http_code "$url" 5)
    printf "  %-12s :%-6s %-6s %-6s %-10s %s\n" "$name" "$port" "$listen" "$code" "${pids:--}" "$src"
    ports_total=$((ports_total+1))
    [ "$code" = "200" ] && ports_ok=$((ports_ok+1))
  done

  if [ "$quick" = "1" ]; then
    printf "  %s\n" "演示就绪判定: --quick 未跑冒烟，端口 ${ports_ok}/${ports_total} HTTP=200"
    echo "NOT READY"
    return 0
  fi

  say "跑 18 场景冒烟（上限 ${SMOKE_TIMEOUT}s，输出 → $LOG_DIR/smoke-last.log）…"
  local smoke_rc
  timeout "$SMOKE_TIMEOUT" bash "$GITS_ROOT/scripts/demo-smoke.sh" --json \
    > "$LOG_DIR/smoke-last.log" 2>&1
  smoke_rc=$?
  local smoke_fail
  if [ "$smoke_rc" -eq 124 ]; then
    warn "冒烟超时（${SMOKE_TIMEOUT}s）"
    smoke_fail="TIMEOUT"
  else
    smoke_fail="$smoke_rc"   # demo-smoke.sh 约定：exit code == FAIL 数
  fi

  printf "  %s\n" "演示就绪判定: 端口 ${ports_ok}/${ports_total} HTTP=200, 冒烟 FAIL=${smoke_fail} (WARN 不计)"
  if [ "$ports_ok" -eq "$ports_total" ] && [ "$smoke_fail" = "0" ]; then
    echo "READY"
  else
    echo "NOT READY"
  fi
}

# ── 主入口 ────────────────────────────────────────────────────────────────────
CMD="${1:-up}"; shift || true
WITH_LIGHTRAG=1
QUICK=0
for a in "$@"; do
  [ "$a" = "--no-lightrag" ] && WITH_LIGHTRAG=""
  [ "$a" = "--quick" ] && QUICK=1
done

case "$CMD" in
  check)  preflight ;;
  down)   stop_stack "$WITH_LIGHTRAG" ;;
  status) show_status "$QUICK" ;;
  smoke)  verify_stack ;;
  up|restart)
    # 已确认：up 与 restart 共用本分支，restart 会先 stop_stack 再完整启动，
    # 不会在 15173 上直接重启（避免僵尸进程占用端口）。用法见文件头与 DEMO-FREEZE.md §3。
    say "══════════════════════════════════════════════"
    say " GITS + KERT 演示环境启动 (cmd=$CMD)"
    say " GITS_ROOT=$GITS_ROOT"
    say " KERT_ROOT=$KERT_ROOT"
    say " LOG_DIR  =$LOG_DIR"
    say " PID_DIR  =$PID_DIR"
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
    say "日志: $LOG_DIR    PID: $PID_DIR"
    say "══════════════════════════════════════════════"
    ;;
  *) die "未知子命令: $CMD（可用：up | restart | down | status | check | smoke）" ;;
esac
