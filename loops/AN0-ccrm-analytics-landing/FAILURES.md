# 失败与自愈记录 · AN0

| # | 现象 | 根因 | 处置 |
|---|---|---|---|
| 1 | 建库 BinderException（stat_month cannot be referenced） | DuckDB `CAST(x AS T) x` 别名与源列同名 | 改 `read_csv(columns=)` 显式类型声明 |
| 2 | 种子 DWD 57 列 vs 表头 56 列 | 造数脚本五级分类多写一个 `bad*0.05` | 删多余值并重生成（DWS 尾部错位随之修正） |
| 3 | 浏览器间歇 400，curl 单发正常 | DuckDB 单连接非线程安全，FastAPI 线程池并发踩游标 | 查询加 `threading.Lock` 串行化；12 路并发 × 54 请求复测 0 错误 |
| 4 | 侧边栏「经营分析」4 项整组同亮 | 4 个二级菜单共用 domain，激活按 domain 判定 | `AppSidebar.isActive` 改按路由前缀精确命中 |
| 5 | E2E webServer 超时 | 旧 vite 进程仅绑 IPv6 `[::1]`，IPv4 健康检查失败 | 清进程由 playwright 自起 |
| 6 | E2E 断言成员名拼接数值 | 整行 textContent 无分隔符 | 改取首列单元格文本 |
| 7 | 顶部 tab 被 Owner 否决 | 需求口径理解错误（页面内导航=左侧面板） | 重构为 `AnalyticsPageNav` 左导航布局 |

## 独立 QA 发现（2026-09-22，session `qa-an0-001`）—— **待修复，修复前不得 Owner 签收**

QA 报告：`evidence/INDEPENDENT_QA-AN0-qa-an0-001.md`；证据：`evidence/qa-an0-001/`。
背景：6 道 implementation 门禁独立复跑全绿、M1~M5 变异全部被捕获，但**目视复核暴露 4 个分析屏趋势图失效**，且现有门禁对该失效结构性不可见。

| ID | 等级 | 现象 | 根因 | 证据 | 处置 |
|---|---|---|---|---|---|
| FAIL-2026-09-22-AN0-QA-01（F1） | MAJOR | `GET /v1/analytics/trend` + `dim=ORG` ⇒ HTTP 500 | `_series_agg` 用 `_dim_expr(dim)`（ORG→`o.org_name`）但该 SQL 未 `JOIN dim_org`（`_aggregate` 有 JOIN，两处不对称）⇒ `BinderException: Referenced table "o" not found!` | `evidence/qa-an0-001/probes/qa_trend_500_repro.log`、`probes/kert_8107_service_console.log` | 待 TL 修复（补 JOIN 或改按 `w.org_id` 关联） |
| FAIL-2026-09-22-AN0-QA-02（F2） | MAJOR | `/trend` 成员/期间无数据 ⇒ HTTP 500（应空点列或 400） | `trend()` 对空 `sums` 调 `_derive({})` ⇒ `profit=None` ⇒ `roa = profit * months / assets` ⇒ `TypeError: unsupported operand type(s) for *: 'NoneType' and 'float'` | 同上；复现 `screen=monitor-ldr&dimValue=NOT_EXIST` → 500（传真实成员 → 200） | 待 TL 修复（空数据短路返回 null 点列） |
| FAIL-2026-09-22-AN0-QA-03（F3） | MAJOR | **4 个「经营指标分析」屏趋势图整屏失效**（界面恒显示「趋势数据不足（至少 2 期）」，库中实有 24 期） | 视图层对 ORG 轴屏把「分布维度」当 trend 的 dim 传、`dimValue` 传机构名 ⇒ 命中 F2；前端 `loadTrend()` catch 后置空 **静默吞 500** | `evidence/qa-an0-001/shots/operating-metrics.png` vs `shots/monitors.png`；`probes/qa_trend_scope.log`（4 处"趋势数据不足" / 3 条 500 / 6 条 200） | 待 TL 修复（传参按行轴语义 + 前端显示错误态 + E2E 补"趋势图有点"断言） |
| FAIL-2026-09-22-AN0-QA-04（F5） | MAJOR | 「不动户参数 N」宣称参数化但**未接线**：改 `inactive_months` 不影响任何指标 | `inactive_months` 仅出现在 `_DEFAULT_PARAMS`、`meta.params`、种子 CSV，**无任何计算引用**；`custCntInactive = SUM(w.inactive_flag)` 直用造数标志位 | `grep -rn inactive_months src/`（3 处全为声明/输出）；对照 `probes`/`mutations/m1_alert_threshold.log`（阈值真接线） | 待 TL 处置（实现 N 判定，或显式标注"展示用未接线"并从决策②已落地清单移除） |
| FAIL-2026-09-22-AN0-QA-05（F4） | MINOR | 门禁文字 over-claim：`LOOP.yaml` `frontend_typecheck.pass_condition` 称「含 e2e 文件的类型检查」，实测不含 | `frontend/tsconfig.json` `include=["src/**/*.ts","src/**/*.vue","vite.config.ts"]`，无 `e2e/**`，亦无第二 tsconfig | `evidence/qa-an0-001/mutations/m4b_e2e_typecheck_green.log`（注入类型错误后 exit=0、日志 0 字节） | 待 TL 处置（改文案或把 e2e 纳入 tsconfig） |
| FAIL-2026-09-22-AN0-QA-06（F6） | MINOR | 端点计数文案不一致：菜单登记写「7 端点」，`LOOP.yaml` 写「8 端点」 | 实测 7 GET + 1 POST = 8 | `grep '@app.\(get\|post\)("/v1/analytics'` | 待 TL 统一文案 |
| FAIL-2026-09-22-AN0-QA-07（F7） | MINOR（工具） | `loop_guard` 拒绝 Loop 目录内任何二进制证据：`reject_placeholders()` 对 `loop.rglob("*")` 每个文件 `read_text(encoding="utf-8")` ⇒ 截图入 Loop 即 `make memory-check/evidence-check` FAIL | `scripts/loop_guard.py:88-96` 无二进制跳过分支 | 复现：截图置于 `evidence/qa-an0-001/shots/` 时 → `loop-guard: FAIL: 'utf-8' codec can't decode byte 0x89 in position 0`；QA 处置=截图改落 Loop 外 `evidence/an0-ccrm-analytics-qa/shots/`（**未改工具**） | 待 TL/Owner 决策（约定截图放 Loop 外，或给 guard 加跳过） |

## 修复记录（2026-09-22 修复轮 · 证据轮次 20260922T120338Z）

独立 QA `qa-an0-001` 判定 FAIL，7 项全部处置；7 道门禁重跑全 PASS（含新增回归门禁）。

| QA 项 | 处置 | 证据 |
|---|---|---|
| QA-01/02（F1+F2，MAJOR：趋势 500 双根因） | `_series_agg` 补 `JOIN dim_org`（与 `_aggregate` 对齐）；`_derive({})` 空聚合返回全 null（不再 TypeError）。新增回归门禁 `analytics_trend_and_inactive_regression`（ORG 轴 4 屏取点 + 未知成员 null 点列）。 | `loops/AN0-ccrm-analytics-landing/evidence/analytics_trend_and_inactive_regression-20260922T120338Z.log` |
| QA-03（F3，MAJOR：前端静默吞 500 + 传参错轴） | 前端 `ScreenDef` 新增 `rowAxis`；趋势按行轴传 `dim=ORG`；失败显示 `analytics-trend-error` 错误态（不再伪装「趋势数据不足」）；E2E 补断言「趋势必须渲染真实数据点（polyline ≥2 点）且不得出现数据不足/错误态」。 | `loops/AN0-ccrm-analytics-landing/evidence/e2e_analytics-20260922T120338Z.log` |
| QA-04（F5，MAJOR：inactive_months 未接线） | 实现 `_inactive_by_member()`（连续 N 期结算发生额为 0 的客户数），在 `metrics()` 覆盖注入；造数补约 8% 长期不动样本使口径可观测；回归测试断言「参数变则值变」且总数 >0（非空转）。 | `loops/AN0-ccrm-analytics-landing/evidence/analytics_trend_and_inactive_regression-20260922T120338Z.log` |
| QA-05（F4，MINOR：门禁文案 over-claim） | `frontend_typecheck.pass_condition` 改为如实描述（范围 frontend/src 与 vite.config.ts；e2e 由 playwright 运行期 + E2E 断言覆盖）。 | `loops/AN0-ccrm-analytics-landing/LOOP.yaml` |
| QA-06（F6，MINOR：端点计数 7 vs 8） | 统一为 8（7 GET + 1 POST）：菜单登记 V1.0、KERT 落地说明。 | `docs/dispatch/CCRM-经营分析菜单登记-V1.0.md`、`../Leibniz-KERT/docs/integration/CCRM_ANALYTICS_LANDING.md` |
| QA-07（F7，MINOR：guard 拒绝二进制证据） | `scripts/loop_guard.py::reject_placeholders` 对非 UTF-8 文件跳过（占位符只可能在文本中），截图不再阻断 `make memory-check/evidence-check`。 | `scripts/loop_guard.py` |

> 复判由 `independent_qa` 执行（TL 不代签）：复跑 7 道门禁 + 变异 M1~M5 + 趋势探针。
