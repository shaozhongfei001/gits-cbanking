# 下一会话交接 · AN0-ccrm-analytics-landing

| 项 | 值 |
|---|---|
| Loop | AN0-ccrm-analytics-landing |
| status | ready_for_independent_qa（修复轮完成） |
| **holder** | `independent_qa` |
| 上一 holder | tech_lead（修复轮） |
| 依赖 | KERT 8107（KERT_ANALYTICS_DUCKDB=examples/bank-front-analytics/cb_analytics.duckdb）；vite 5173 |

## 本次修复（QA qa-an0-001 判定 FAIL 的 7 项）
- MAJOR-01/02：趋势 500 双根因 —— `_series_agg` 补 `JOIN dim_org`；`_derive({})` 返回全 null（不再 TypeError）。
- MAJOR-03：前端按行轴传 `dim=ORG`（新增 `ScreenDef.rowAxis`）+ 趋势失败显示错误态（新增 `analytics-trend-error`）+ E2E 断言趋势必须渲染真实点。
- MAJOR-04：不动户 N 真接线（`_inactive_by_member` N 期窗口 + 造数补约 8% 长期不动样本 + 回归门禁）。
- MINOR-05/06/07：门禁文案 over-claim 修正；端点计数统一 8；`loop_guard.reject_placeholders` 跳过二进制证据。

## 复判要求
1. 复跑 7 道门禁（LOOP.yaml），比对 EVIDENCE.json 修复轮 sha256；
2. 重做 M1~M5 变异（尤其 M3 白名单 / M5 菜单高亮 / M4 typecheck 非空转）；
3. 趋势探针：逐屏 `/trend` 状态码与点值（含 ORG 轴 4 屏、未知成员 null 点列）；
4. 复判通过 → QA 记 QA_PASS；不通过 → FAILURES.md 交回 TL。

## 禁止
- 不得放宽 fail-closed；不得以 mock 代替真实链路；不得恢复认证（Owner 决策）；不得代签。
