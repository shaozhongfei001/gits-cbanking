# 交接 · AN0-ccrm-analytics-landing

| 项 | 值 |
|---|---|
| 交付人 | tech_lead（Owner 直派任务） |
| 交付时间 | 2026-09-22 |
| 状态 | ready_for_independent_qa |
| Baton | owner_review |

## 交付内容
- **GITS**：经营分析一级菜单（4 二级）+ 3 个分析页左侧页面内导航 + 组合查询直挂页；
  菜单登记 `docs/dispatch/CCRM-经营分析菜单登记-V1.0.md`；E2E `frontend/e2e/analytics.spec.ts`。
- **KERT**：`/v1/analytics/*` 8 端点、10 屏口径服务、4 个数据分析 SKILL（SK-FRONT-008~011）、
  DuckDB `cbdm_*` 造数（DWD 7200 / DWS 3816 / 参数表 5 行）；落地说明
  `../Leibniz-KERT/docs/integration/CCRM_ANALYTICS_LANDING.md`。
- **部署**：`deploy/systemd/kert-api.service` + `deploy/.env.example` 补 `KERT_ANALYTICS_DUCKDB`。

## 运行前置（复现门禁所需）
1. 建库：`cd ../Leibniz-KERT && python3 scripts/build_analytics_duckdb.py`
2. 起服务：`KERT_ANALYTICS_DUCKDB=$PWD/examples/bank-front-analytics/cb_analytics.duckdb python3 scripts/serve_analytics_api.py`（8107）
3. 前端：`cd frontend && npx vite --host 127.0.0.1 --port 5173`（E2E 亦可由 playwright webServer 自起）

## 下一位接手
- **independent_qa**：复跑 6 道门禁、比对 `EVIDENCE.json` sha256、核对口径参数与 Owner 五项决策；出报告（TL 不代签）。
- **owner_review**：签收本 Loop；指派外部 UX 权威源（NAV_GROUPS）同步登记责任人。
