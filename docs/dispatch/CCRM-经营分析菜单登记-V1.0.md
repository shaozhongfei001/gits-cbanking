# CCRM 经营分析菜单登记 V1.0

| 项 | 值 |
|---|---|
| 登记日期 | 2026-09-22 |
| 指令来源 | Owner 直派（CCRM 对公数据分析落地，GITS 前端展示） |
| 代码权威 | `frontend/src/layouts/navConfig.ts`（`SHELL_NAV_GROUPS`） |
| 路由 | `frontend/src/router/index.ts`（`/analytics/*`，pageId 留空先例同「产品中心」） |
| 数据服务 | KERT `Leibniz-KERT`：`/v1/analytics/*`（**8 端点** = 7 GET + 1 POST，DuckDB `cbdm_*` 造数） |
| Loop 登记 | `loops/AN0-ccrm-analytics-landing/` |

## 1. 菜单结构（Owner 口径）

| 一级 | 二级 | 页面内导航（分析页左侧面板） |
|---|---|---|
| 经营分析 | 经营指标分析 | 客户指标分析 / 业务概况分析 / 利润贡献分析 / 风险指标分析 |
| 经营分析 | 细分客群分析 | 客户分布特征分析 / 细分客户业务分析（子项：存款业务 / 贷款业务 / 中间业务 / 结算量业务） |
| 经营分析 | 组合查询工具 | —（直接挂链「组合条件查询分析」页面） |
| 经营分析 | 指标监视器 | 业务增减变化监控 / 存贷比变化监控 / 不良贷款分布变化监控 |

**相对原型的重排**（Owner 指令）：原「客户分析工具」更名「细分客群分析」；原「组合条件查询分析」菜单项删除（并入组合查询工具直挂）；「产品分析器」及其二期占位删除；「分析工具」一级菜单更名并升为「经营分析」一级菜单。

## 2. 与既有菜单的一致性约束

- 一级导航只切稳定对象域（`navConfig.ts` 设计纪律）——「经营分析」为分析对象域，符合；
- 图标沿用既有几何字形家族（`▥ ▨ ☰ ▩`，与 `▦ ▤ ◫` 同族）；
- 同域多菜单的激活高亮：按路由前缀精确命中当前项（`AppSidebar.isActive`），不得整组同亮；
- 全局菜单项 17 = 既有 13 + 新增 4（`AppSidebar.spec.ts` 断言）。

## 3. 权威源同步状态（待办）

`navConfig.ts` 声明的 V3.2 权威源为：设计系统 Token、页面 01 PNG、`generate_gits_bank_ux_v32.py` 的 `NAV_GROUPS`。

**本仓未包含该生成脚本**（全仓检索 0 命中，属设计侧外部资产），故本登记表为本仓内的权威登记；**外部权威源的 `NAV_GROUPS` 同步登记为待办**，责任人：UX/设计侧（由 Owner 指派）。在外部同步完成前，以本登记表 + `navConfig.ts` 为准，二者不一致视为漂移。

## 4. 验收证据

- 单元/视图：`frontend/src/views/__tests__/AnalyticsViews.spec.ts`、`AppSidebar.spec.ts`
- E2E：`frontend/e2e/analytics.spec.ts`（真实链路 5173 → /kert-api → KERT 8107）
- Loop 门禁与哈希：`loops/AN0-ccrm-analytics-landing/EVIDENCE.json`
