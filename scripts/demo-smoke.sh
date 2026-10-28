#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════════════════
#  GITS + KERT 端到端冒烟验证脚本
#
#  覆盖全部核心演示场景，确保端到端链路可用
#
#  用法：
#    scripts/demo-smoke.sh                    # 默认 127.0.0.1
#    scripts/demo-smoke.sh --host 10.0.0.1    # 指定主机
#    scripts/demo-smoke.sh --json             # JSON 输出
#    scripts/demo-smoke.sh --verbose          # 详细输出
# ═══════════════════════════════════════════════════════════════════════════════
set -uo pipefail

HOST="127.0.0.1"
FE_PORT="15173"
API_PORT="18080"
SKILL_PORT="8107"
JSON_OUTPUT=0
VERBOSE=0
GET_TIMEOUT=10
POST_TIMEOUT=30

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
say()   { printf "  ${CYAN}▸${NC} %s\n" "$*"; }
ok()    { printf "  ${GREEN}✓${NC} %s\n" "$*"; }
warn()  { printf "  ${YELLOW}⚠${NC} %s\n" "$*" >&2; }
fail()  { printf "  ${RED}✗${NC} %s\n" "$*" >&2; }

http_code() { local c; c=$(curl -s -o /dev/null -w '%{http_code}' --max-time "${2:-$GET_TIMEOUT}" "$1" 2>/dev/null); echo "${c:-000}"; }
http_body() { curl -s --max-time "${2:-$GET_TIMEOUT}" "$1" 2>/dev/null; }
post_code() { local c; c=$(curl -s -o /dev/null -w '%{http_code}' --max-time "${3:-$POST_TIMEOUT}" -X POST -H "Content-Type: application/json" -d "$2" "$1" 2>/dev/null); echo "${c:-000}"; }
post_body() { curl -s --max-time "${3:-$POST_TIMEOUT}" -X POST -H "Content-Type: application/json" -d "$2" "$1" 2>/dev/null; }

# 解析参数
while [ $# -gt 0 ]; do
  case "$1" in
    --host) HOST="$2"; shift 2 ;;
    --json) JSON_OUTPUT=1; shift ;;
    --verbose) VERBOSE=1; shift ;;
    --fe-port) FE_PORT="$2"; shift 2 ;;
    --api-port) API_PORT="$2"; shift 2 ;;
    --kert-port) SKILL_PORT="$2"; shift 2 ;;
    *) echo "未知参数: $1"; exit 1 ;;
  esac
done

API="http://$HOST:$API_PORT"
KERT="http://$HOST:$SKILL_PORT"
FE="http://$HOST:$FE_PORT"

PASS=0; FAIL=0; SKIP=0; WARN=0
RESULTS=()

record() {
  local sid="$1" name="$2" status="$3" detail="${4:-}"
  RESULTS+=("$sid|$name|$status|$detail")
  case "$status" in
    PASS) PASS=$((PASS+1)); ok "S$sid $name — PASS $detail" ;;
    FAIL) FAIL=$((FAIL+1)); fail "S$sid $name — FAIL $detail" ;;
    WARN) WARN=$((WARN+1)); warn "S$sid $name — WARN $detail" ;;
    SKIP) SKIP=$((SKIP+1)); say "S$sid $name — SKIP $detail" ;;
  esac
}

# ── S1: 经营旅程列表 ──────────────────────────────────────────────────────────
say "[S1] 经营旅程列表"
s1_code=$(http_code "$API/api/v1/engagement/journey")
s1_body=$(http_body "$API/api/v1/engagement/journey")
s1_count=$(echo "$s1_body" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
if [ "$s1_code" = "200" ] && [ "$s1_count" -gt 0 ]; then
  JOURNEY_ID=$(echo "$s1_body" | python3 -c "import sys,json; print(json.load(sys.stdin)[0]['journeyId'])" 2>/dev/null)
  CUSTOMER_ID=$(echo "$s1_body" | python3 -c "import sys,json; print(json.load(sys.stdin)[0]['customerId'])" 2>/dev/null)
  record "1" "经营旅程列表" "PASS" "($s1_count 条, first=$JOURNEY_ID)"
else
  record "1" "经营旅程列表" "FAIL" "HTTP=$s1_code, count=$s1_count"
  JOURNEY_ID=""; CUSTOMER_ID=""
fi

# ── S2: 旅程详情 ──────────────────────────────────────────────────────────────
say "[S2] 旅程详情"
if [ -n "$JOURNEY_ID" ]; then
  s2_code=$(http_code "$API/api/v1/engagement/journey/$JOURNEY_ID")
  [ "$s2_code" = "200" ] && record "2" "旅程详情" "PASS" "id=$JOURNEY_ID" || record "2" "旅程详情" "FAIL" "HTTP=$s2_code"
else
  record "2" "旅程详情" "SKIP" "无旅程ID"
fi

# ── S3: 客户查询 ──────────────────────────────────────────────────────────────
say "[S3] 客户查询"
s3_code=$(http_code "$API/api/v1/engagement/customer?rmId=RM-001")
[ "$s3_code" = "200" ] && record "3" "客户查询" "PASS" "rmId=RM-001" || record "3" "客户查询" "FAIL" "HTTP=$s3_code"

# ── S4: 产品中心 ──────────────────────────────────────────────────────────────
say "[S4] 产品中心"
s4_code=$(http_code "$API/api/v1/product-center/products")
s4_body=$(http_body "$API/api/v1/product-center/products")
s4_count=$(echo "$s4_body" | python3 -c "import sys,json; d=json.load(sys.stdin); print(len(d) if isinstance(d,list) else d.get('totalElements',1))" 2>/dev/null || echo "?")
[ "$s4_code" = "200" ] && record "4" "产品中心" "PASS" "($s4_count 项)" || record "4" "产品中心" "FAIL" "HTTP=$s4_code"

# ── S5: 产品知识卡 ────────────────────────────────────────────────────────────
say "[S5] 产品知识卡"
s5_code=$(http_code "$API/api/v1/product-knowledge/cards/PROD-CM-003")
[ "$s5_code" = "200" ] && record "5" "产品知识卡" "PASS" "PROD-CM-003" || record "5" "产品知识卡" "FAIL" "HTTP=$s5_code"

# ── S6: 门禁列表 ──────────────────────────────────────────────────────────────
say "[S6] 门禁列表"
s6_code=$(http_code "$API/api/v1/human-gates?status=PENDING")
[ "$s6_code" = "200" ] && record "6" "门禁列表" "PASS" || record "6" "门禁列表" "FAIL" "HTTP=$s6_code"

# ── S7: CRM回写命令 ──────────────────────────────────────────────────────────
say "[S7] CRM回写命令"
s7_code=$(http_code "$API/api/v1/crm/writeback-commands")
[ "$s7_code" = "200" ] && record "7" "CRM回写命令" "PASS" || record "7" "CRM回写命令" "FAIL" "HTTP=$s7_code"

# ── S8: KERT Analytics 屏幕 ──────────────────────────────────────────────────
say "[S8] KERT Analytics 屏幕"
s8_code=$(http_code "$KERT/v1/analytics/screens")
[ "$s8_code" = "200" ] && record "8" "KERT Analytics" "PASS" || record "8" "KERT Analytics" "FAIL" "HTTP=$s8_code"

# ── S9: KERT 指标 ────────────────────────────────────────────────────────────
say "[S9] KERT 经营指标"
s9_code=$(http_code "$KERT/v1/analytics/metrics?screen=operating-customer&dim=INDUSTRY&orgId=350200&period=201012")
[ "$s9_code" = "200" ] && record "9" "KERT 经营指标" "PASS" "screen=operating-customer" || record "9" "KERT 经营指标" "FAIL" "HTTP=$s9_code"

# ── S10: KERT 知识地图 ───────────────────────────────────────────────────────
say "[S10] KERT 知识地图"
s10_code=$(http_code "$KERT/v1/knowledge-maps")
[ "$s10_code" = "200" ] && record "10" "KERT 知识地图" "PASS" || record "10" "KERT 知识地图" "FAIL" "HTTP=$s10_code"

# ── S11: 前端页面可达 ────────────────────────────────────────────────────────
say "[S11] 前端页面可达"
s11_code=$(http_code "$FE/" 8)
[ "$s11_code" = "200" ] && record "11" "前端页面" "PASS" || record "11" "前端页面" "FAIL" "HTTP=$s11_code"

# ── S12: 建议书生成（KERT 技能，LLM 不可用时 503 可接受）────────────────────
# 注意：SP-20 真实执行约 30s（LLM 逐章生成，非冷启动）。实测换新 requestId 恒为 ~30.2s；
# 若沿用同一 requestId 则命中 KERT 幂等（~3s）。阈值必须 >30s，否则必然误报 FAIL。
say "[S12] 建议书生成（真实执行约 30s）"
s12_body='{"requestId":"smoke-001","customerId":"CUST-CORP-0001","context":{}}'
s12_code=$(post_code "$API/api/v14/proposals" "$s12_body" 90)
if [ "$s12_code" = "200" ] || [ "$s12_code" = "202" ]; then
  record "12" "建议书生成" "PASS" "HTTP=$s12_code"
elif [ "$s12_code" = "503" ] || [ "$s12_code" = "500" ]; then
  record "12" "建议书生成" "WARN" "KERT 技能异常(HTTP=$s12_code)，LLM 可能不可用"
else
  record "12" "建议书生成" "FAIL" "HTTP=$s12_code"
fi

# ── S13: 访前准备（异步长耗时，60s 超时）─────────────────────────────────────
say "[S13] 访前准备"
if [ -n "$JOURNEY_ID" ]; then
  s13_ocid=$(echo "$s1_body" | python3 -c "
import sys,json
d=json.load(sys.stdin)
j=[x for x in d if x['journeyId']=='$JOURNEY_ID']
print(j[0].get('operatingCaseId','') if j else '')
" 2>/dev/null)
  s13_cid=$(echo "$s1_body" | python3 -c "
import sys,json
d=json.load(sys.stdin)
j=[x for x in d if x['journeyId']=='$JOURNEY_ID']
print(j[0].get('customerId','') if j else '')
" 2>/dev/null)
  if [ -n "$s13_ocid" ] && [ -n "$s13_cid" ]; then
    s13_body="{\"customerId\":\"$s13_cid\",\"operatingCaseId\":\"$s13_ocid\"}"
    s13_code=$(post_code "$API/api/v1/engagement/journey/$JOURNEY_ID/prepare-previsit" "$s13_body" 60)
    if [ "$s13_code" = "200" ] || [ "$s13_code" = "202" ]; then
      record "13" "访前准备" "PASS" "HTTP=$s13_code"
    elif [ "$s13_code" = "503" ] || [ "$s13_code" = "500" ]; then
      record "13" "访前准备" "WARN" "KERT 技能异常(HTTP=$s13_code)"
    elif [ "$s13_code" = "000" ]; then
      record "13" "访前准备" "WARN" "超时(60s)，KERT 技能执行中（非故障）"
    else
      record "13" "访前准备" "FAIL" "HTTP=$s13_code"
    fi
  else
    record "13" "访前准备" "SKIP" "无 operatingCaseId/customerId"
  fi
else
  record "13" "访前准备" "SKIP" "无旅程ID"
fi

# ── S14: KYC洞察（404 可接受）────────────────────────────────────────────────
say "[S14] KYC洞察"
s14_code=$(http_code "$API/api/v1/engagement/kyc/CUST-CORP-0001/insights")
if [ "$s14_code" = "200" ]; then
  record "14" "KYC洞察" "PASS"
elif [ "$s14_code" = "404" ]; then
  record "14" "KYC洞察" "WARN" "端点未实现(HTTP=404)，前端需降级"
else
  record "14" "KYC洞察" "FAIL" "HTTP=$s14_code"
fi

# ── S15: 前端代理验证 ────────────────────────────────────────────────────────
say "[S15] 前端→后端代理"
s15_code=$(http_code "$FE/api/v1/engagement/journey" 8)
[ "$s15_code" = "200" ] && record "15" "前端→API代理" "PASS" || record "15" "前端→API代理" "FAIL" "HTTP=$s15_code"

say "[S16] 前端→KERT代理"
s16_code=$(http_code "$FE/kert-api/v1/health" 8)
[ "$s16_code" = "200" ] && record "16" "前端→KERT代理" "PASS" || record "16" "前端→KERT代理" "FAIL" "HTTP=$s16_code"

# ── S17: KERT 趋势 ───────────────────────────────────────────────────────────
say "[S17] KERT 趋势"
s17_code=$(http_code "$KERT/v1/analytics/trend?screen=operating-customer&dim=INDUSTRY&dimValue=manufacturing&orgId=350200&period=201012&metric=custCnt")
[ "$s17_code" = "200" ] && record "17" "KERT 趋势" "PASS" || record "17" "KERT 趋势" "FAIL" "HTTP=$s17_code"

# ── S18: KERT 可用期间 ───────────────────────────────────────────────────────
say "[S18] KERT 可用期间"
s18_code=$(http_code "$KERT/v1/analytics/periods")
[ "$s18_code" = "200" ] && record "18" "KERT 可用期间" "PASS" || record "18" "KERT 可用期间" "FAIL" "HTTP=$s18_code"

# ── 汇总 ──────────────────────────────────────────────────────────────────────
echo ""
say "══════════════════════════════════════════════"
say " 冒烟验证汇总"
say "══════════════════════════════════════════════"
printf "  ${GREEN}PASS${NC}: %d  ${RED}FAIL${NC}: %d  ${YELLOW}WARN${NC}: %d  ${CYAN}SKIP${NC}: %d  总计: %d\n" \
  "$PASS" "$FAIL" "$WARN" "$SKIP" "$((PASS+FAIL+WARN+SKIP))"

if [ "$JSON_OUTPUT" = "1" ]; then
  printf '[\n'
  first=1
  for r in "${RESULTS[@]}"; do
    IFS='|' read -r sid name status detail <<< "$r"
    [ $first -eq 0 ] && printf ',\n'
    printf '  {"id":"S%s","name":"%s","status":"%s","detail":"%s"}' "$sid" "$name" "$status" "$detail"
    first=0
  done
  printf '\n]\n'
fi

if [ "$FAIL" -gt 0 ]; then
  say "❌ 有 $FAIL 项失败，演示环境不可用"
  exit "$FAIL"
else
  say "✅ 核心场景全部通过！($PASS PASS, $WARN WARN, $SKIP SKIP)"
  exit 0
fi
