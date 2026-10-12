#!/usr/bin/env bash
# UAT1 波次门禁执行器：每次运行使用全新且**已存在**的产物目录，
# 避免 Playwright 启动时批量删除旧产物（会触发工具环境的批量删除保护，污染门禁结果）。
#
# 用法：bash scripts/uat_wave.sh <wave-id> <spec 路径...>
set -uo pipefail

WAVE="${1:?wave id required}"
shift
if [ "$#" -eq 0 ]; then
  echo "spec path required" >&2
  exit 2
fi
STAMP="$(date +%Y%m%dT%H%M%S)"
BASE_URL="${UAT_BASE_URL:-http://127.0.0.1:5173}"
ARTIFACT_DIR="/tmp/uat-artifacts/${WAVE}-${STAMP}/raw"
REPORT_DIR="/tmp/uat-reports/${WAVE}-${STAMP}"

mkdir -p "$ARTIFACT_DIR" "$REPORT_DIR"

cd frontend || exit 2

QA_BASE_URL="$BASE_URL" \
  QA_REPORT_DIR="$REPORT_DIR" \
  QA_OUTPUT_DIR="$ARTIFACT_DIR" \
  npx playwright test --config playwright.qa.config.ts "$@" --reporter=list
