# 共享记忆 · AN0-ccrm-analytics-landing

## 任务
CCRM 对公经营分析落地（Owner 直派）：GITS 展示 + KERT 分析服务/SKILL + DuckDB 造数。

## 边界
- 不改 `specs/`、`generated/`、封版制品与既有 Loop。
- KERT 侧改动限于 `src/kert/{application,infrastructure,api}`、`examples/bank-front-analytics/`、`deploy/`。
- 认证旁路为 Owner 决策（不恢复），不得自行恢复。

## 关键事实
- 表前缀 `cbdm_`（Owner 指令）；DWD `cbdm_cust_biz_wide` 为聚合单一口径源。
- 分析页左侧"页面内导航"为 Owner 口径；顶部 tab 已被否决。
- 口径参数在 `cfg_analytics_param`；FTP 利润口径缺列即 fail-closed。
- E2E 依赖真实链路（KERT 8107 + vite 5173），不得 mock 代替。

## 未落盘结论 = 不存在
