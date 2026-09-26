# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: analytics.spec.ts >> 经营分析（CCRM-BA 落地） >> 细分客群分析：2 项导航 + 细分客户业务 4 子项切换
- Location: e2e/analytics.spec.ts:58:3

# Error details

```
Error: expect(locator).toContainText(expected) failed

Locator: getByTestId('analytics-panel-segment-business').locator('.table')
Expected substring: "借贷累加"
Timeout: 5000ms
Error: element(s) not found

Call log:
  - Expect "toContainText" with timeout 5000ms
  - waiting for getByTestId('analytics-panel-segment-business').locator('.table')

```

```yaml
- complementary:
  - navigation "GITS Bank 主导航":
    - button "G GITS Bank 对公客户经营工作台"
    - paragraph: 日常作业
    - button "客户经营作战台"
    - button "我的任务与承诺": 我的任务与承诺 3
    - paragraph: 客户经营
    - button "客户组合"
    - button "客户全景"
    - button "经营旅程"
    - button "需求与机会"
    - paragraph: 方案与交付
    - button "服务建议书"
    - button "产品推荐"
    - button "专家协同"
    - button "账户计划与价值"
    - paragraph: 知识与治理
    - button "产品中心"
    - button "产品解读与知识"
    - button "审批与审计"
    - paragraph: 经营分析
    - button "经营指标分析"
    - button "细分客群分析"
    - button "组合查询工具"
    - button "指标监视器"
    - text: 开发会话 对公客户经理 · 在线
- searchbox "全局搜索"
- button "＋ 全局新建" [disabled]
- button "帮助": ？
- button "通知": ♢
- button "亮色"
- text: 开 开发会话 总行公司金融部
- button "GITS Bank ×":
  - text: GITS Bank
  - button "×"
- button "细分客群分析 ×":
  - text: 细分客群分析
  - button "×"
- heading "细分客群分析" [level=1]
- paragraph: 客群结构画像（数量 / 户均价值 / 基础账户）与分条线业务透视；行=维度成员，分段维度阈值由参数配置驱动。
- alert: Request failed with status code 503 无法连接 KERT 分析服务（/kert-api 代理 → 8107）。请先启动： KERT_ANALYTICS_DUCKDB=… python3 scripts/serve_analytics_api.py
- navigation "分析图表切换": 客户分布特征分析 细分客户业务分析 存款业务 贷款业务 中间业务 结算量业务
- text: 结算量业务 单位：万元 / 户 / % 环比=比上月 较年初=对当年首月
- alert:
  - text: 分析服务不可用 Request failed with status code 503（KERT 分析服务 /kert-api，请确认 KERT_ANALYTICS_DUCKDB 已配置）
  - button "重试"
```

# Test source

```ts
  1   | import { expect, test } from '@playwright/test'
  2   | 
  3   | /**
  4   |  * CCRM 经营分析 E2E（Owner 指令 2026-09-22 落地验收）：
  5   |  * 真实链路 前端 5173 → vite /kert-api 代理 → KERT 8107（DuckDB 造数，cbdm_*）。
  6   |  * 覆盖：侧边栏菜单结构与单项高亮、页面内导航（左侧）切换分析图表、
  7   |  * 细分客群业务子项、组合查询圈选、指标监视器告警图例与行联动趋势。
  8   |  * KERT 分析服务未启动时本用例应失败（不得以 mock 数据代替验收）。
  9   |  */
  10  | test.describe('经营分析（CCRM-BA 落地）', () => {
  11  |   test('侧边栏：经营分析组 4 项，点击进入且仅当前项高亮', async ({ page }) => {
  12  |     await page.goto('/workbench')
  13  |     const group = page.getByTestId('nav-group-analytics')
  14  |     await expect(group).toContainText('经营分析')
  15  |     await expect(group.getByRole('button')).toHaveCount(4)
  16  |     // 全局菜单数量不受破坏（13 既有 + 4 新增）
  17  |     await expect(page.getByTestId('shell-sidebar').locator('.nav-item')).toHaveCount(17)
  18  | 
  19  |     await page.getByTestId('nav-item-analytics-operating-metrics').click()
  20  |     await expect(page).toHaveURL(/\/analytics\/operating-metrics/)
  21  |     // 同 domain 组：仅当前项激活，不再整组同亮
  22  |     const active = group.locator('.nav-item.active')
  23  |     await expect(active).toHaveCount(1)
  24  |     await expect(active).toContainText('经营指标分析')
  25  |   })
  26  | 
  27  |   test('经营指标分析：左侧 4 项页面内导航 + 机构表格（KERT 真实数据）', async ({ page }) => {
  28  |     await page.goto('/analytics/operating-metrics')
  29  |     const nav = page.getByTestId('analytics-page-nav')
  30  |     await expect(nav.getByTestId('analytics-nav-item')).toHaveCount(4)
  31  |     await expect(nav).toContainText('客户指标分析')
  32  |     await expect(nav).toContainText('业务概况分析')
  33  |     await expect(nav).toContainText('利润贡献分析')
  34  |     await expect(nav).toContainText('风险指标分析')
  35  | 
  36  |     // 默认面板：客户指标分析（行=机构，原文口径）
  37  |     const panel = page.getByTestId('analytics-panel-operating-customer')
  38  |     await expect(panel).toBeVisible()
  39  |     await expect(panel.locator('.table')).toContainText('机构名称')
  40  |     await expect(panel.locator('.table')).toContainText('厦门分行')
  41  |     await expect(panel.getByTestId('analytics-bar-list')).toBeVisible()
  42  |     const trend = panel.getByTestId('analytics-trend-chart')
  43  |     await expect(trend).toContainText('12个月趋势')
  44  |     // QA FAIL-2026-09-22-AN0-QA-03 回归：趋势必须渲染真实数据点（此前该屏恒显示"趋势数据不足"）
  45  |     await expect(trend.locator('polyline')).toHaveAttribute('points', /\d+,\d+[\s\S]*\d+,\d+/)
  46  |     await expect(trend).not.toContainText('趋势数据不足')
  47  |     await expect(panel.getByTestId('analytics-trend-error')).toHaveCount(0)
  48  | 
  49  |     // 切换到「风险指标分析」：面板切换、指标列变化
  50  |     await nav.getByTestId('analytics-nav-item').filter({ hasText: '风险指标分析' }).click()
  51  |     await expect(page.getByTestId('analytics-panel-operating-risk')).toBeVisible()
  52  |     await expect(page.getByTestId('analytics-panel-operating-customer')).toHaveCount(0)
  53  |     await expect(
  54  |       page.getByTestId('analytics-panel-operating-risk').locator('.table'),
  55  |     ).toContainText('不良贷款金额')
  56  |   })
  57  | 
  58  |   test('细分客群分析：2 项导航 + 细分客户业务 4 子项切换', async ({ page }) => {
  59  |     await page.goto('/analytics/segments')
  60  |     const nav = page.getByTestId('analytics-page-nav')
  61  |     await expect(nav.getByTestId('analytics-nav-item')).toHaveCount(2)
  62  |     await expect(nav.getByTestId('analytics-nav-subitem')).toHaveCount(4)
  63  |     await expect(page.getByTestId('analytics-panel-segment-distribution')).toBeVisible()
  64  | 
  65  |     // 子项「结算量业务」→ segment-business 面板（借贷发生额列组）
  66  |     await nav.getByTestId('analytics-nav-subitem').filter({ hasText: '结算量业务' }).click()
  67  |     await expect(page.getByTestId('analytics-panel-segment-business')).toBeVisible()
  68  |     await expect(
  69  |       page.getByTestId('analytics-panel-segment-business').locator('.table'),
> 70  |     ).toContainText('借贷累加')
      |       ^ Error: expect(locator).toContainText(expected) failed
  71  |     await expect(
  72  |       page.getByTestId('analytics-panel-segment-business').locator('.table'),
  73  |     ).toContainText('行业名称')
  74  |   })
  75  | 
  76  |   test('组合查询：数值条件圈选返回客户清单（白名单真实链路）', async ({ page }) => {
  77  |     await page.goto('/analytics/combo-query')
  78  |     // 默认数值条件：存款时点金额 ≥ 5000（万元）
  79  |     await page.getByRole('button', { name: '查 询' }).click()
  80  | 
  81  |     const table = page.getByTestId('combo-result-table')
  82  |     await expect(table).toBeVisible()
  83  |     await expect(table).toContainText('客户编号')
  84  |     await expect(table).toContainText('存款时点金额')
  85  |     await expect(table.locator('tbody tr').first()).toContainText('分行')
  86  |     await expect(page.locator('.pager')).toContainText('共')
  87  |     await expect(page.locator('.pager')).toContainText('户')
  88  |   })
  89  | 
  90  |   test('指标监视器：3 项导航 + 告警图例 + 表格行点击联动趋势图', async ({ page }) => {
  91  |     await page.goto('/analytics/monitors')
  92  |     const nav = page.getByTestId('analytics-page-nav')
  93  |     await expect(nav.getByTestId('analytics-nav-item')).toHaveCount(3)
  94  |     await expect(nav).toContainText('业务增减变化监控')
  95  |     await expect(nav).toContainText('存贷比变化监控')
  96  |     await expect(nav).toContainText('不良贷款分布变化监控')
  97  | 
  98  |     const panel = page.getByTestId('analytics-panel-monitor-balance')
  99  |     await expect(panel).toBeVisible()
  100 |     await expect(panel).toContainText('±15%')
  101 |     // 监视器屏趋势同样必须有点（防"静默空图"回潮）
  102 |     await expect(panel.getByTestId('analytics-trend-chart').locator('polyline'))
  103 |       .toHaveAttribute('points', /\d+,\d+[\s\S]*\d+,\d+/)
  104 | 
  105 |     // 点击表格首行 → 趋势图切换为该维度成员（成员名取自首列单元格）
  106 |     const firstRow = panel.locator('.n-data-table tbody tr').first()
  107 |     await expect(firstRow).toBeVisible()
  108 |     const member = ((await firstRow.locator('td').first().textContent()) ?? '').trim()
  109 |     await firstRow.click()
  110 |     await expect(panel.getByTestId('analytics-trend-chart')).toContainText('12个月趋势')
  111 |     if (member) {
  112 |       await expect(panel.getByTestId('analytics-trend-chart')).toContainText(member)
  113 |     }
  114 | 
  115 |     // 切换「存贷比变化监控」
  116 |     await nav.getByTestId('analytics-nav-item').filter({ hasText: '存贷比变化监控' }).click()
  117 |     await expect(page.getByTestId('analytics-panel-monitor-ldr')).toBeVisible()
  118 |     await expect(
  119 |       page.getByTestId('analytics-panel-monitor-ldr').locator('.table'),
  120 |     ).toContainText('存贷比')
  121 |   })
  122 | })
  123 | 
```