#!/usr/bin/env node
/**
 * fail-closed：验证 E2E 用例**真实执行**了，而不是"一个都没跑 / 全部跳过"。
 *
 * 背景（真实 CI 证据，run 34870734027 的 e2e job）：
 *   原判定读 `playwright-report/index.html`，但 `playwright.config.ts` 当时**没有配置
 *   HTML reporter** → 该文件**从不产生** → 步骤固定打印 "WARN: No Playwright report
 *   found" 并 `exit 0`，属于**恒真空转**。同轮日志：
 *     `No files were found with the provided path: frontend/playwright-report/`
 *   此外，从 HTML 正文 grep `\d+ passed` 本身也很脆（改版即失效）。
 *
 * 现改为读 Playwright JSON reporter 产出的机器可读计数，并对以下情形一律 exit 1：
 *   报告文件缺失 / JSON 解析失败 / 零执行 / 有用例失败 / 有用例被跳过 /
 *   出现 flaky（`retries: 0` 下不应存在 → 说明配置漂移）/ 总数低于基线。
 *
 * 基线（--min）：当前为 38，等于 run 34870734027 与本地复现一致的用例数。
 *   新增用例请同步上调该值；下调必须显式说明理由（例如确有用例被合法删除），
 *   否则"用例被静默删除 / 改名后落进 testIgnore"将无法被发现。
 *
 * 用法：node scripts/check-e2e-ran.mjs [--report <path>] [--min <n>]
 * 退出码：0=PASS；1=FAIL。
 */

import fs from 'node:fs'
import path from 'node:path'

const DEFAULT_REPORT = 'playwright-report/e2e-results.json'
const DEFAULT_MIN = 38

function parseArgs(argv) {
  const opts = { report: DEFAULT_REPORT, min: DEFAULT_MIN }
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i]
    if (arg === '--report') {
      opts.report = argv[i + 1]
      i += 1
    } else if (arg === '--min') {
      opts.min = Number.parseInt(argv[i + 1], 10)
      i += 1
    } else {
      fail(`未知参数：${arg}`)
    }
  }
  if (!Number.isInteger(opts.min) || opts.min < 1) {
    fail(`--min 必须是正整数，实际为：${opts.min}`)
  }
  return opts
}

function fail(message) {
  console.error(`FAIL: ${message}`)
  process.exit(1)
}

/** 递归遍历 suites（可嵌套），按 `test.status` 计数。 */
function countTests(suites, acc) {
  for (const suite of suites ?? []) {
    for (const spec of suite.specs ?? []) {
      for (const test of spec.tests ?? []) {
        const status = test.status ?? 'unknown'
        acc[status] = (acc[status] ?? 0) + 1
      }
    }
    countTests(suite.suites, acc)
  }
  return acc
}

function main() {
  const opts = parseArgs(process.argv.slice(2))
  const reportPath = path.resolve(opts.report)

  if (!fs.existsSync(reportPath)) {
    fail(`未找到 E2E 报告 ${opts.report}：JSON reporter 未产出（config 是否被改动？）`)
  }

  let report
  try {
    report = JSON.parse(fs.readFileSync(reportPath, 'utf8'))
  } catch (error) {
    fail(`无法解析 ${opts.report}：${error.message}`)
  }

  const counts = countTests(report.suites, {})
  const expected = counts.expected ?? 0
  const unexpected = counts.unexpected ?? 0
  const flaky = counts.flaky ?? 0
  const skipped = counts.skipped ?? 0
  const other = counts.unknown ?? 0
  const executed = expected + unexpected + flaky
  const total = executed + skipped + other

  console.log(
    `E2E 计数：总用例=${total} 真实执行=${executed} 通过=${expected} 失败=${unexpected} `
    + `跳过=${skipped} flaky=${flaky} 未识别=${other}（基线 min=${opts.min}）`,
  )

  // 与 playwright 自算的 stats 交叉核对：两者不一致说明解析假设已失效，
  // 此时计数不可信，宁可失败也不给出"看起来正常"的结论。
  const stats = report.stats
  if (stats) {
    const statsTotal = (stats.expected ?? 0) + (stats.unexpected ?? 0) + (stats.skipped ?? 0) + (stats.flaky ?? 0)
    if (statsTotal !== total) {
      fail(`计数不一致：递归统计=${total}，报告 stats=${statsTotal}（JSON 结构假设已失效）`)
    }
  }

  if (total === 0) fail('报告里没有任何用例记录')
  if (executed === 0) fail('没有任何用例真实执行（全部 skipped？）')
  if (unexpected > 0) fail(`${unexpected} 个用例失败`)
  if (flaky > 0) fail(`${flaky} 个用例 flaky（retries=0 下不应出现，疑似配置漂移）`)
  if (skipped > 0) fail(`${skipped} 个用例被跳过（本套件不应有 skip；*.live.spec.ts 由 testIgnore 排除而非 skip）`)
  if (other > 0) fail(`${other} 个用例状态未识别（未预期的 status 取值）`)
  if (executed < opts.min) {
    fail(
      `实际执行 ${executed} 个用例，低于基线 ${opts.min}：`
      + '用例可能被静默删除、改名（落入 testIgnore）或未被收集',
    )
  }

  console.log(`PASS: E2E ${executed} 个用例真实执行且全部通过（无跳过、无 flaky）`)
}

main()
