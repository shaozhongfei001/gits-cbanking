#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════
#  GITS ↔ DKWS 产品推荐三段式 · WP6 联调冒烟脚本（准备件）
#
#  状态：CANDIDATE / FROZEN=NO / IMPLEMENTED=NO / REAL_E2E_PASS=NO
#  配套计划：docs/dispatch/WP6_SMOKE_TEST_PLAN_CANDIDATE.md
#
#  运行前提（本脚本【不】自动启动/停止任何服务）：
#    1. DKWS 已启动：http://127.0.0.1:8106
#         ~/dev/Leibniz-KERT 下：.venv/bin/python scripts/serve_skill_service.py --port 8106
#    2. GITS 已启动：http://127.0.0.1:8080
#         docker compose -f compose.local.yaml up -d  或  ./mvnw -pl apps/api spring-boot:run
#    3. API Key（可选）：GITS_API_KEY（X-API-KEY）/ DSH_API_KEY（X-API-Key）
#
#  用法：
#    ./scripts/product-recommendation-smoke.sh            # 用例 1/2/5/3（两端均在线，happy path）
#    ./scripts/product-recommendation-smoke.sh --fail-closed   # 仅用例 4（DKWS 已由人工停止后执行）
#    ./scripts/product-recommendation-smoke.sh --help
#
#  可覆盖环境变量：GITS_BASE_URL、DSH_BASE_URL、GITS_API_KEY、DSH_API_KEY、
#                  CUSTOMER_ID、JOURNEY_ID、NEED_VERSION_ID、OBJECTIVE、
#                  POLL_TIMEOUT_S、POLL_INTERVAL_S
#
#  注意（如实标注）：createRun / getRun / getStages 的 REST 控制器当前尚未接线
#  （契约权威 specs/openapi/product-recommendation.openapi.json，CTR-PR-API-001
#  status=CANDIDATE）。接线完成前，用例 2/5 会以明确的 FAIL 暴露该缺口，不伪装通过。
#  HG-D01 decide（用例 3）已接线（POST /api/v1/human-gates/{gateId}/decide）。
# ═══════════════════════════════════════════════════════════════════════════
set -uo pipefail
# 注：冒烟脚本本身以“检测并报告失败”为目的，刻意不启用 `set -e`，改为对每个
# 用例函数返回值显式判定（否则任一用例返回非 0 会在汇总前提前退出）。

# ── 可覆盖配置 ────────────────────────────────────────────────────────────
GITS_BASE_URL="${GITS_BASE_URL:-http://127.0.0.1:8080}"
DSH_BASE_URL="${DSH_BASE_URL:-http://127.0.0.1:8106}"
GITS_API_KEY="${GITS_API_KEY:-}"
DSH_API_KEY="${DSH_API_KEY:-}"

CUSTOMER_ID="${CUSTOMER_ID:-CUST-CORP-0001}"
JOURNEY_ID="${JOURNEY_ID:-JOURNEY-CUST-CORP-0001}"
NEED_VERSION_ID="${NEED_VERSION_ID:-NEEDV-CUST-CORP-0001}"
OBJECTIVE="${OBJECTIVE:-补充流动资金与跨境结算方案}"

POLL_TIMEOUT_S="${POLL_TIMEOUT_S:-180}"   # 对齐 dsh.async-poll-timeout-ms
POLL_INTERVAL_S="${POLL_INTERVAL_S:-3}"   # 对齐 dsh.async-poll-interval-ms

MODE="happy"                              # happy | fail-closed
for arg in "$@"; do
  case "$arg" in
    --fail-closed) MODE="fail-closed" ;;
    -h|--help)
      sed -n '2,28p' "$0" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *) echo "未知参数: $arg（支持 --fail-closed / --help）" >&2; exit 2 ;;
  esac
done

# ── 颜色与日志 ────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
log_step() { echo -e "\n${CYAN}━━━ $1 ━━━${NC}"; }
log_ok()   { echo -e "  ${GREEN}✓ $1${NC}"; }
log_warn() { echo -e "  ${YELLOW}⚠ $1${NC}"; }
log_err()  { echo -e "  ${RED}✗ $1${NC}"; }

PASS_COUNT=0
FAIL_COUNT=0
record() { # record <pass|fail> <label>
  if [ "$1" = "pass" ]; then log_ok "$2"; PASS_COUNT=$((PASS_COUNT+1));
  else log_err "$2"; FAIL_COUNT=$((FAIL_COUNT+1)); fi
}

# ── HTTP 请求原语（结果存入 RESP_CODE / RESP_BODY） ──────────────────────
SMOKE_TMP="$(mktemp -d)"
trap 'rm -rf "$SMOKE_TMP"' EXIT
BODY_FILE="$SMOKE_TMP/body.json"
RESP_CODE=""; RESP_BODY=""

request() { # request <METHOD> <url> [curl 额外参数...]
  local method="$1" url="$2"; shift 2
  RESP_CODE="$(curl -sS -o "$BODY_FILE" -w '%{http_code}' -X "$method" "$@" "$url" 2>/dev/null || true)"
  RESP_CODE="${RESP_CODE:-000}"
  RESP_BODY="$(cat "$BODY_FILE" 2>/dev/null || true)"
}

# ── 断言原语（作用于最近一次 request 的 RESP_BODY/RESP_CODE） ────────────
assert_http() { # assert_http <expected-code> <label>
  if [ "$RESP_CODE" = "$1" ]; then record pass "$2 (HTTP $RESP_CODE)"; return 0
  else record fail "$2 (HTTP $RESP_CODE != $1)"; return 1; fi
}
assert_jq() {  # assert_jq <jq-filter> <label>  — filter 需为布尔表达式
  if echo "$RESP_BODY" | jq -e "$1" >/dev/null 2>&1; then record pass "$2"; return 0
  else record fail "$2 (jq: $1)"; return 1; fi
}
assert_eq() {  # assert_eq <actual> <expected> <label>
  if [ "$1" = "$2" ]; then record pass "$3 (=$2)"; return 0
  else record fail "$3 (got '$1' != '$2')"; return 1; fi
}

# ── 认证头 ────────────────────────────────────────────────────────────────
gits_auth=(); dsh_auth=()
[ -n "$GITS_API_KEY" ] && gits_auth=(-H "X-API-KEY: $GITS_API_KEY")
[ -n "$DSH_API_KEY" ]  && dsh_auth=(-H "X-API-Key: $DSH_API_KEY")

# ── 幂等键 / 业务时点 ─────────────────────────────────────────────────────
new_key() {
  if command -v uuidgen >/dev/null 2>&1; then uuidgen | tr '[:upper:]' '[:lower:]';
  elif [ -r /proc/sys/kernel/random/uuid ]; then cat /proc/sys/kernel/random/uuid;
  else echo "idem-$(date +%s)-$RANDOM$RANDOM"; fi
}
AS_OF="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

# ── createRun 请求体（用 jq 安全构造 JSON） ───────────────────────────────
build_create_body() {
  jq -n --arg customerId "$CUSTOMER_ID" --arg journeyId "$JOURNEY_ID" \
        --arg needVersionId "$NEED_VERSION_ID" --arg objective "$OBJECTIVE" \
        --arg asOf "$AS_OF" '
    {
      customerId: $customerId,
      journeyId: $journeyId,
      needVersionIds: [$needVersionId],
      recommendationObjective: $objective,
      requestedProductDomains: ["FINANCING", "SETTLEMENT"],
      asOf: $asOf,
      customerFactSnapshotId: "CFS-CUST-CORP-0001",
      productKnowledgeSnapshotRef: "PKS-CUST-CORP-0001",
      ruleBundleRef: "RB-PR-20260831-0001",
      permissionDecisionId: "PERM-CUST-CORP-0001",
      activationContract: "AC-PRODUCT-RECOMMEND-001"
    }'
}

# ── 用例 1：两端健康检查 ──────────────────────────────────────────────────
case_health() {
  local rc=0
  log_step "用例 1：两端健康检查"

  log_step "  DKWS health — GET $DSH_BASE_URL/api/skill/health"
  request GET "$DSH_BASE_URL/api/skill/health" -H 'Accept: application/json'
  if [ "$RESP_CODE" = "200" ]; then
    assert_jq '.status == "ok" or .status == "degraded"' "DKWS /api/skill/health status ∈ {ok,degraded}" || rc=1
  else
    # 契约 vNext §2 也提供 /v1/health 作为健康检查
    log_warn "  /api/skill/health 返回 HTTP $RESP_CODE，回退 /v1/health"
    request GET "$DSH_BASE_URL/v1/health" -H 'Accept: application/json'
    assert_http 200 "DKWS /v1/health" || rc=1
  fi

  log_step "  GITS health — GET $GITS_BASE_URL/actuator/health"
  request GET "$GITS_BASE_URL/actuator/health" -H 'Accept: application/json'
  assert_http 200 "GITS /actuator/health" || rc=1
  assert_jq '.status == "UP"' "GITS actuator health == UP" || rc=1
  return $rc
}

# ── 轮询：方案就绪（用例 2） ─────────────────────────────────────────────
poll_run_ready() { # poll_run_ready <runId> → 0 就绪 / 1 失败终态 / 2 非200 / 3 超时
  local run_id="$1" elapsed=0
  while [ "$elapsed" -lt "$POLL_TIMEOUT_S" ]; do
    request GET "$GITS_BASE_URL/api/v1/product-recommendation-runs/$run_id" -H 'Accept: application/json'
    [ "$RESP_CODE" = "200" ] || { echo "$RESP_BODY" >&2; return 2; }
    RUN_STATUS="$(echo "$RESP_BODY" | jq -r '.status // empty')"
    case "$RUN_STATUS" in
      AWAITING_HUMAN|PROPOSAL_READY) return 0 ;;
      FAILED_CLOSED|HELD|STALE_REQUIRES_RERUN|APPROVED|MODIFIED|REJECTED) return 1 ;;
    esac
    sleep "$POLL_INTERVAL_S"; elapsed=$((elapsed + POLL_INTERVAL_S))
    echo -n "."
  done
  echo "" >&2
  return 3
}

# ── 用例 2：createRun → 轮询至方案就绪 → GET stages ──────────────────────
case_create_and_stages() {
  local rc=0
  log_step "用例 2：createRun → 轮询至方案就绪 → GET stages"
  IDEM_KEY="$(new_key)"
  log_warn "  Idempotency-Key=$IDEM_KEY"
  CREATE_BODY="$(build_create_body)"

  log_step "  POST $GITS_BASE_URL/api/v1/product-recommendation-runs"
  request POST "$GITS_BASE_URL/api/v1/product-recommendation-runs" \
    -H 'Content-Type: application/json' -H 'Accept: application/json' \
    -H "Idempotency-Key: $IDEM_KEY" "${gits_auth[@]}" -d "$CREATE_BODY"
  assert_http 200 "createRun HTTP 200" || { rc=1; echo "  (若 404：createRun REST 控制器尚未接线，见计划 §0)"; }
  RUN_ID="$(echo "$RESP_BODY" | jq -r '.runId // empty')"
  if [ -z "$RUN_ID" ]; then record fail "createRun 返回缺 runId"; return 1; fi
  record pass "createRun 返回 runId=$RUN_ID"

  log_step "  轮询 GET .../product-recommendation-runs/$RUN_ID（最长 ${POLL_TIMEOUT_S}s）"
  poll_run_ready "$RUN_ID"
  local prc=$?
  if [ "$prc" = "0" ]; then
    record pass "run 状态就绪：$RUN_STATUS"
  elif [ "$prc" = "1" ]; then
    record fail "run 进入失败/异常终态：$RUN_STATUS"
    rc=1
  elif [ "$prc" = "2" ]; then
    record fail "轮询 GET 返回非 200"
    rc=1
  else
    record fail "轮询超时（${POLL_TIMEOUT_S}s），最后状态=$RUN_STATUS"
    rc=1
  fi

  CURRENT_VERSION_ID="$(echo "$RESP_BODY" | jq -r '.currentVersionId // empty')"
  assert_jq '.currentVersionId != null and (.currentVersionId|length > 0)' \
    "run.currentVersionId 非空" || rc=1

  log_step "  GET .../product-recommendation-runs/$RUN_ID/stages"
  request GET "$GITS_BASE_URL/api/v1/product-recommendation-runs/$RUN_ID/stages" \
    -H 'Accept: application/json' "${gits_auth[@]}"
  assert_http 200 "getStages HTTP 200" || rc=1
  assert_eq "$(echo "$RESP_BODY" | jq -r '.runId // empty')" "$RUN_ID" "stages.runId 匹配" || rc=1
  assert_jq '.status != null' "stages.status 存在" || rc=1
  assert_jq 'has("eligibilityResults") and has("fitResults") and has("portfolioCandidates") and has("needProfile")' \
    "stages 三段式数组字段齐全" || rc=1
  return $rc
}

# ── 用例 3：HG-D01 人工决定（APPROVE） ────────────────────────────────────
case_human_decision() {
  local rc=0
  log_step "用例 3：HG-D01 人工决定（APPROVE）"
  if [ -z "${CURRENT_VERSION_ID:-}" ]; then record fail "缺少 currentVersionId，无法构造决定载荷"; return 1; fi
  DECIDE_BODY="$(jq -n --arg runId "$RUN_ID" --arg vid "$CURRENT_VERSION_ID" '
    {
      runId: $runId,
      proposalVersionId: $vid,
      expectedVersion: $vid,
      decision: "APPROVE",
      actorId: "RM-SMOKE-001",
      actorRole: "RELATIONSHIP_MANAGER"
    }')"
  log_step "  POST $GITS_BASE_URL/api/v1/human-gates/HG-D01/decide"
  request POST "$GITS_BASE_URL/api/v1/human-gates/HG-D01/decide" \
    -H 'Content-Type: application/json' -H 'Accept: application/json' \
    "${gits_auth[@]}" -d "$DECIDE_BODY"
  assert_http 200 "HG-D01 decide HTTP 200" || { rc=1; echo "  (409=版本过期 / 403=权限 / 422=前置失败 / 400=校验失败)"; }
  assert_eq "$(echo "$RESP_BODY" | jq -r '.decision // empty')" "APPROVE" "decision == APPROVE" || rc=1
  assert_eq "$(echo "$RESP_BODY" | jq -r '.runId // empty')" "$RUN_ID" "decision.runId 匹配" || rc=1

  log_step "  复验 run 状态推进为 APPROVED"
  request GET "$GITS_BASE_URL/api/v1/product-recommendation-runs/$RUN_ID" -H 'Accept: application/json' "${gits_auth[@]}"
  assert_eq "$(echo "$RESP_BODY" | jq -r '.status // empty')" "APPROVED" "run.status == APPROVED" || rc=1
  return $rc
}

# ── 用例 5：同 Idempotency-Key 重放返回同 run ─────────────────────────────
case_idempotency_replay() {
  local rc=0
  log_step "用例 5：同 Idempotency-Key 重放返回同 run"
  log_step "  再次 POST createRun（同一 Idempotency-Key=$IDEM_KEY）"
  request POST "$GITS_BASE_URL/api/v1/product-recommendation-runs" \
    -H 'Content-Type: application/json' -H 'Accept: application/json' \
    -H "Idempotency-Key: $IDEM_KEY" "${gits_auth[@]}" -d "$CREATE_BODY"
  assert_http 200 "重放 HTTP 200" || rc=1
  local replay_run_id
  replay_run_id="$(echo "$RESP_BODY" | jq -r '.runId // empty')"
  assert_eq "$replay_run_id" "$RUN_ID" "重放 runId 与首次一致（幂等命中，不重复调 KERT）" || rc=1
  return $rc
}

# ── 用例 4：DKWS 停服 → run=FAILED_CLOSED（后端部分） ────────────────────
case_fail_closed() {
  local rc=0
  log_step "用例 4：DKWS 停服 → run=FAILED_CLOSED（后端部分；前端空态由前端工程师浏览器验证）"
  log_warn "  请确认 DKWS（$DSH_BASE_URL）已被人工停止，GITS 仍在运行"
  request GET "$DSH_BASE_URL/api/skill/health" -H 'Accept: application/json'
  if [ "$RESP_CODE" = "200" ]; then
    record fail "DKWS 仍在线（HTTP 200）——请先停服再执行 --fail-closed"
    return 1
  fi
  record pass "确认 DKWS 已停服（HTTP $RESP_CODE）"

  FC_KEY="$(new_key)"
  FC_BODY="$(build_create_body)"
  log_step "  POST createRun（新 Idempotency-Key=$FC_KEY）"
  request POST "$GITS_BASE_URL/api/v1/product-recommendation-runs" \
    -H 'Content-Type: application/json' -H 'Accept: application/json' \
    -H "Idempotency-Key: $FC_KEY" "${gits_auth[@]}" -d "$FC_BODY"
  assert_http 200 "createRun（DKWS 停服）HTTP 200（run 应已落库）" || { rc=1; }
  FC_RUN_ID="$(echo "$RESP_BODY" | jq -r '.runId // empty')"
  [ -z "$FC_RUN_ID" ] && { record fail "createRun 返回缺 runId"; return 1; }
  record pass "createRun 返回 runId=$FC_RUN_ID"

  log_step "  轮询至 FAILED_CLOSED（最长 ${POLL_TIMEOUT_S}s）"
  local elapsed=0 fstatus=""
  while [ "$elapsed" -lt "$POLL_TIMEOUT_S" ]; do
    request GET "$GITS_BASE_URL/api/v1/product-recommendation-runs/$FC_RUN_ID" -H 'Accept: application/json' "${gits_auth[@]}"
    [ "$RESP_CODE" = "200" ] || { record fail "轮询 GET 返回非 200"; rc=1; break; }
    fstatus="$(echo "$RESP_BODY" | jq -r '.status // empty')"
    [ "$fstatus" = "FAILED_CLOSED" ] && { record pass "run.status == FAILED_CLOSED"; break; }
    case "$fstatus" in
      AWAITING_HUMAN|PROPOSAL_READY|APPROVED|MODIFIED|REJECTED|HELD|STALE_REQUIRES_RERUN)
        record fail "run 未 fail-closed，反而落入 $fstatus（INV-07 违反）"; rc=1; break ;;
    esac
    sleep "$POLL_INTERVAL_S"; elapsed=$((elapsed + POLL_INTERVAL_S)); echo -n "."
  done
  if [ "$fstatus" != "FAILED_CLOSED" ] && [ "$elapsed" -ge "$POLL_TIMEOUT_S" ]; then
    record fail "轮询超时（${POLL_TIMEOUT_S}s），最后状态=$fstatus"; rc=1
  fi
  return $rc
}

# ── 汇总 ──────────────────────────────────────────────────────────────────
summary() {
  log_step "冒烟结果汇总"
  echo -e "  ${GREEN}PASS: $PASS_COUNT${NC}   ${RED}FAIL: $FAIL_COUNT${NC}"
  if [ "$FAIL_COUNT" = "0" ]; then
    log_ok "全部通过"
    return 0
  else
    log_err "存在失败项（见上）；本脚本为 CANDIDATE 准备件，失败可能是 createRun REST 控制器未接线所致，见计划 §0"
    return 1
  fi
}

# ── 主流程 ────────────────────────────────────────────────────────────────
log_step "GITS↔DKWS 产品推荐冒烟（GITS=$GITS_BASE_URL / DKWS=$DSH_BASE_URL / mode=$MODE）"

if [ "$MODE" = "fail-closed" ]; then
  case_fail_closed
  summary
  exit $?
fi

# happy path：用例 1 → 2 → 5 → 3（用例 4 需停服，默认跳过）
case_health
HEALTH_RC=$?
if [ "$HEALTH_RC" != "0" ]; then
  log_warn "健康检查失败，先修复环境再继续；以下用例可能无法执行"
fi

case_create_and_stages
CASE2_RC=$?

if [ "$CASE2_RC" = "0" ]; then
  case_idempotency_replay
  case_human_decision
else
  log_warn "用例 2 未通过，跳过用例 5/3（依赖 runId/currentVersionId）"
  record fail "用例 5（幂等重放）— 因用例 2 失败而跳过"
  record fail "用例 3（HG-D01）— 因用例 2 失败而跳过"
fi

log_warn "用例 4（DKWS 停服 fail-closed）默认跳过；在 DKWS 停服后执行：$0 --fail-closed"

summary
exit $?
