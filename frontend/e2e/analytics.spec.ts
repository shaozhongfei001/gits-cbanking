import { expect, test } from '@playwright/test'

/**
 * CCRM 经营分析 E2E（Owner 指令 2026-09-22 落地验收）：
 * 真实链路 前端 5173 → vite /kert-api 代理 → KERT 8107（DuckDB 造数，cbdm_*）。
 * 覆盖：侧边栏菜单结构与单项高亮、页面内导航（左侧）切换分析图表、
 * 细分客群业务子项、组合查询圈选、指标监视器告警图例与行联动趋势。
 * KERT 分析服务未启动时本用例应失败（不得以 mock 数据代替验收）。
 */
test.describe('经营分析（CCRM-BA 落地）', () => {
  test('侧边栏：经营分析组 4 项，点击进入且仅当前项高亮', async ({ page }) => {
    await page.goto('/workbench')
    const group = page.getByTestId('nav-group-analytics')
    await expect(group).toContainText('经营分析')
    await expect(group.getByRole('button')).toHaveCount(4)
    // 全局菜单数量不受破坏（13 既有 + 4 新增）
    await expect(page.getByTestId('shell-sidebar').locator('.nav-item')).toHaveCount(17)

    await page.getByTestId('nav-item-analytics-operating-metrics').click()
    await expect(page).toHaveURL(/\/analytics\/operating-metrics/)
    // 同 domain 组：仅当前项激活，不再整组同亮
    const active = group.locator('.nav-item.active')
    await expect(active).toHaveCount(1)
    await expect(active).toContainText('经营指标分析')
  })

  test('经营指标分析：左侧 4 项页面内导航 + 机构表格（KERT 真实数据）', async ({ page }) => {
    await page.goto('/analytics/operating-metrics')
    const nav = page.getByTestId('analytics-page-nav')
    await expect(nav.getByTestId('analytics-nav-item')).toHaveCount(4)
    await expect(nav).toContainText('客户指标分析')
    await expect(nav).toContainText('业务概况分析')
    await expect(nav).toContainText('利润贡献分析')
    await expect(nav).toContainText('风险指标分析')

    // 默认面板：客户指标分析（行=机构，原文口径）
    const panel = page.getByTestId('analytics-panel-operating-customer')
    await expect(panel).toBeVisible()
    await expect(panel.locator('.table')).toContainText('机构名称')
    await expect(panel.locator('.table')).toContainText('厦门分行')
    await expect(panel.getByTestId('analytics-bar-list')).toBeVisible()
    const trend = panel.getByTestId('analytics-trend-chart')
    await expect(trend).toContainText('12个月趋势')
    // QA FAIL-2026-09-22-AN0-QA-03 回归：趋势必须渲染真实数据点（此前该屏恒显示"趋势数据不足"）
    await expect(trend.locator('polyline')).toHaveAttribute('points', /\d+,\d+[\s\S]*\d+,\d+/)
    await expect(trend).not.toContainText('趋势数据不足')
    await expect(panel.getByTestId('analytics-trend-error')).toHaveCount(0)

    // 切换到「风险指标分析」：面板切换、指标列变化
    await nav.getByTestId('analytics-nav-item').filter({ hasText: '风险指标分析' }).click()
    await expect(page.getByTestId('analytics-panel-operating-risk')).toBeVisible()
    await expect(page.getByTestId('analytics-panel-operating-customer')).toHaveCount(0)
    await expect(
      page.getByTestId('analytics-panel-operating-risk').locator('.table'),
    ).toContainText('不良贷款金额')
  })

  test('细分客群分析：2 项导航 + 细分客户业务 4 子项切换', async ({ page }) => {
    await page.goto('/analytics/segments')
    const nav = page.getByTestId('analytics-page-nav')
    await expect(nav.getByTestId('analytics-nav-item')).toHaveCount(2)
    await expect(nav.getByTestId('analytics-nav-subitem')).toHaveCount(4)
    await expect(page.getByTestId('analytics-panel-segment-distribution')).toBeVisible()

    // 子项「结算量业务」→ segment-business 面板（借贷发生额列组）
    await nav.getByTestId('analytics-nav-subitem').filter({ hasText: '结算量业务' }).click()
    await expect(page.getByTestId('analytics-panel-segment-business')).toBeVisible()
    await expect(
      page.getByTestId('analytics-panel-segment-business').locator('.table'),
    ).toContainText('借贷累加')
    await expect(
      page.getByTestId('analytics-panel-segment-business').locator('.table'),
    ).toContainText('行业名称')
  })

  test('组合查询：数值条件圈选返回客户清单（白名单真实链路）', async ({ page }) => {
    await page.goto('/analytics/combo-query')
    // 默认数值条件：存款时点金额 ≥ 5000（万元）
    await page.getByRole('button', { name: '查 询' }).click()

    const table = page.getByTestId('combo-result-table')
    await expect(table).toBeVisible()
    await expect(table).toContainText('客户编号')
    await expect(table).toContainText('存款时点金额')
    await expect(table.locator('tbody tr').first()).toContainText('分行')
    await expect(page.locator('.pager')).toContainText('共')
    await expect(page.locator('.pager')).toContainText('户')
  })

  test('指标监视器：3 项导航 + 告警图例 + 表格行点击联动趋势图', async ({ page }) => {
    await page.goto('/analytics/monitors')
    const nav = page.getByTestId('analytics-page-nav')
    await expect(nav.getByTestId('analytics-nav-item')).toHaveCount(3)
    await expect(nav).toContainText('业务增减变化监控')
    await expect(nav).toContainText('存贷比变化监控')
    await expect(nav).toContainText('不良贷款分布变化监控')

    const panel = page.getByTestId('analytics-panel-monitor-balance')
    await expect(panel).toBeVisible()
    await expect(panel).toContainText('±15%')
    // 监视器屏趋势同样必须有点（防"静默空图"回潮）
    await expect(panel.getByTestId('analytics-trend-chart').locator('polyline'))
      .toHaveAttribute('points', /\d+,\d+[\s\S]*\d+,\d+/)

    // 点击表格首行 → 趋势图切换为该维度成员（成员名取自首列单元格）
    const firstRow = panel.locator('.n-data-table tbody tr').first()
    await expect(firstRow).toBeVisible()
    const member = ((await firstRow.locator('td').first().textContent()) ?? '').trim()
    await firstRow.click()
    await expect(panel.getByTestId('analytics-trend-chart')).toContainText('12个月趋势')
    if (member) {
      await expect(panel.getByTestId('analytics-trend-chart')).toContainText(member)
    }

    // 切换「存贷比变化监控」
    await nav.getByTestId('analytics-nav-item').filter({ hasText: '存贷比变化监控' }).click()
    await expect(page.getByTestId('analytics-panel-monitor-ldr')).toBeVisible()
    await expect(
      page.getByTestId('analytics-panel-monitor-ldr').locator('.table'),
    ).toContainText('存贷比')
  })
})
