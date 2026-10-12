# 证据摘要 · AN0-ccrm-analytics-landing

时间：2026-09-22T10:53:47.878585+00:00｜执行者：tech_lead（implementation）｜状态：全部 pass

| 门禁 | 命令 | 退出码 | 证据文件 | sha256（前 12） |
|---|---|---|---|---|
| kert_analytics_unit | `cd ../Leibniz-KERT && python3 -m pytest tests/unit/test_operational_analytics.py -q` | 0 | `loops/AN0-ccrm-analytics-landing/evidence/kert_analytics_unit-20260922T105316Z.log` | `c6ce8518a2cc` |
| kert_analytics_integration | `cd ../Leibniz-KERT && python3 -m pytest tests/integration/test_analytics_api.py -q` | 0 | `loops/AN0-ccrm-analytics-landing/evidence/kert_analytics_integration-20260922T105316Z.log` | `0db356ee91ac` |
| frontend_typecheck | `cd frontend && npx vue-tsc --noEmit` | 0 | `loops/AN0-ccrm-analytics-landing/evidence/frontend_typecheck-20260922T105316Z.log` | `e3b0c44298fc` |
| frontend_analytics_unit | `cd frontend && npx vitest run src/views/__tests__/AnalyticsViews.spec.ts src/components/shell/__tests__/AppSidebar.spec.ts` | 0 | `loops/AN0-ccrm-analytics-landing/evidence/frontend_analytics_unit-20260922T105316Z.log` | `3a9e053ddca6` |
| e2e_analytics | `cd frontend && npx playwright test e2e/analytics.spec.ts` | 0 | `loops/AN0-ccrm-analytics-landing/evidence/e2e_analytics-20260922T105316Z.log` | `2874593a9512` |
| analytics_params_failclosed | `cd ../Leibniz-KERT && python3 -m pytest tests/unit/test_operational_analytics.py -q -k Params` | 0 | `loops/AN0-ccrm-analytics-landing/evidence/analytics_params_failclosed-20260922T105316Z.log` | `700bc0322b00` |

## 结论要点

- KERT：单元 25 + 集成 14 全过（含口径参数化与 FTP fail-closed）；未配置分析库时端点 503、注册表零扰动。
- 前端：vue-tsc 0 错误；页面内导航/菜单结构单测全过。
- E2E：5/5 通过（真实链路 5173 → /kert-api → KERT 8107，未起服务即失败不降级）。
- 并发修复：DuckDB 连接串行化后 12 路并发 × 54 请求 0 错误。

## 独立 QA 待办

- 复跑 6 道门禁并比对 sha256；核对口径参数与 Owner 五项决策落地。TL 不得代签 QA_PASS。
