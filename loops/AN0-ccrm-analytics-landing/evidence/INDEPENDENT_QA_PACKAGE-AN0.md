# 独立 QA 包 · AN0-ccrm-analytics-landing

| 项 | 值 |
|---|---|
| Loop | AN0-ccrm-analytics-landing |
| 交付角色 | tech_lead（Owner 直派） |
| QA 角色 | independent_qa（**不得复用 TL 结论，须自行复跑**） |
| 冻结时间 | 2026-09-22 |
| 判定权 | QA 出报告；`QA_PASS` 仅 QA 角色可记；Owner 签收在 QA 之后 |

## 1. 靶标冻结清单（sha256，复核基准）

### 1.1 门禁证据文件（与 EVIDENCE.json 同源）

| 门禁 | sha256 |
|---|---|
| kert_analytics_unit | `c6ce8518a2cc113cc5560b3731e234ed6d559e746221ae903ce01599dfe7e797` |
| kert_analytics_integration | `0db356ee91ac6f4323f5e9f7af3f60f50ef236bb0f748f141783308a103c3ab9` |
| frontend_typecheck | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| frontend_analytics_unit | `3a9e053ddca6f782097e6b2a6900506501a006036f5c2cd12e44498c9c7d7bff` |
| e2e_analytics | `2874593a951200f0a181c236cac3e73be999d35e175507fc483226a6bf1edce8` |
| analytics_params_failclosed | `700bc0322b00f8e8db3ce495047983b54ab27ab59ed1fedac05f3aeba47dae24` |

> ⚠ `frontend_typecheck` 的哈希 `e3b0c442…b855` 是**空文件**的 sha256（vue-tsc 无诊断即无输出）。
> QA 必须做**非空转验证**（§3.1 变异 M4）：空日志本身不构成通过证据。

### 1.2 实现靶标

| 仓 | 文件 | sha256 |
|---|---|---|
| KERT | `src/kert/application/operational_analytics.py` | `ecb5235fe35646c4c69040e1611f6cc6044bce077c46ec29aeccde45abe3a966` |
| KERT | `src/kert/infrastructure/analytics_store.py` | `e6dd9073ed55a0ac5470b3dbc3b8f1cc7a8f68cbe661428e84247721197b9837` |
| KERT | `src/kert/api/server.py` | `f43859781b51de33afda7aefee1561bb764b779cdd2c18b910c296b832f4fa26` |
| KERT | `src/kert/application/skills.py` | `4c08c9f4ad958ab6232bf6f5d874937d009f571bb20b99dfb58879d8bc377e75` |
| KERT | `tests/unit/test_operational_analytics.py` | `b5c89274a7ea5258395b85dab62df19ecd0714c61e25143e12152dbb723c501d` |
| KERT | `tests/integration/test_analytics_api.py` | `f5eb5a90b83c7969961f7aa99e3958e447470dee39159adc07d91e3fb1a8e96d` |
| KERT | `scripts/build_analytics_duckdb.py` | `43889b3088565b795ddacca156b14347b2596d533e1f615a09b31b6cd2bae6e4` |
| GITS | `frontend/src/layouts/navConfig.ts` | `a14ac6f56e5334375dd0e80de21d42562a6d95d7b6e46b53513ec5eb7e823886` |
| GITS | `frontend/src/components/shell/AppSidebar.vue` | `1c3240f0be040bb2e357f9ddbe5e368ffa2eb8021ded57bfa6e35f58157d8263` |
| GITS | `frontend/src/router/index.ts` | `1dcfe2db2282f83e734bd3cd826c72f15b7b3e99a05f4022073a17d2a96a679b` |
| GITS | `frontend/src/api/analytics.ts` | `c917c7cd6ff213c371a93798a92863b72dbb728e9a441c2ba5ee39f2b7519e55` |
| GITS | `frontend/src/components/analytics/AnalyticsPageNav.vue` | `a631aefc9796f01045d0839318df94813db2835413d9255b2261d9420a20873b` |
| GITS | `frontend/src/components/analytics/AnalyticsResultsPanel.vue` | `a8a45f48f386c1caae909c2d4fba76affbda009f8b2b49a1db7ffa4cf958c804` |
| GITS | `frontend/src/views/AnalyticsOperatingMetricsView.vue` | `b38f56854d83db3b98455ce5a13054504558b7220732821965adc003715f3f13` |
| GITS | `frontend/src/views/AnalyticsSegmentView.vue` | `b8713522a505df06bea9c9c74f0ed6bab024b141cfd602fee17c174f87c2aead` |
| GITS | `frontend/src/views/AnalyticsMonitorView.vue` | `8c2a20080d7fb2da9e49386bf3881bf03d97c5cac1c77ea31064820988a92b4e` |
| GITS | `frontend/src/views/AnalyticsComboQueryView.vue` | `7d0fab6405eedad632b55a223f241e7d8fd9702836780caa79de3c779fae722f` |
| GITS | `frontend/e2e/analytics.spec.ts` | `796af68cbf9ca8b2d47adbc3e72ca3105e5f69c0c9bb011a4e2c9f32ac3281bf` |

## 2. 复现前置（QA 自行搭建，不得复用 TL 会话状态）

```bash
# 1) 建 DuckDB 造数库（建库前须停 KERT 服务以释放读锁）
cd /home/szf/dev/Leibniz-KERT && python3 scripts/build_analytics_duckdb.py
# 2) 起分析服务（8107）
KERT_ANALYTICS_DUCKDB=$PWD/examples/bank-front-analytics/cb_analytics.duckdb \
  python3 scripts/serve_analytics_api.py
# 3) 前端（E2E 亦可由 playwright webServer 自起；须 --host 127.0.0.1 以过 IPv4 健康检查）
cd /home/szf/dev/gits-cbanking/frontend && npx vite --host 127.0.0.1 --port 5173
```

## 3. 判定清单（逐条给 PASS / FAIL / INCONCLUSIVE + 证据）

| # | 判定项 | 方法 |
|---|---|---|
| Q1 | 6 道门禁**独立复跑** exit=0 | 按 `LOOP.yaml` 的 `gates[].command` 原样执行 |
| Q2 | 证据 `sha256` 与 §1.1 比对（日志含时间戳致哈希变化须记录并说明） | `sha256sum` |
| Q3 | 断言**非空转**：M1~M5 变异全部被捕获，恢复后原样 PASS | §3.1 |
| Q4 | 口径一致：`GET /v1/analytics/params` = `metrics.meta.params` = `cfg_analytics_param` 行 | 直连 8107 比对 |
| Q5 | FTP fail-closed：`profit_source=FTP` 且无 FTP 列 ⇒ **400 具名拒绝**，不得静默降级 | 改配置行后请求 `/metrics` |
| Q6 | 未配置即隔离：未设 `KERT_ANALYTICS_DUCKDB` ⇒ 端点 503、4 个分析 SKILL 不注册（零扰动） | 集成用例 + 手工起服复核 |
| Q7 | 组合查询注入面：`metric/op` 白名单外 ⇒ 400，SQL 不被拼接执行 | 发 `metric='evil; DROP'`、`op='LIKE'` |
| Q8 | 并发正确性：≥12 路并发混合请求 0 个 5xx/400（DuckDB 连接串行化） | 并发打 8 类端点 |
| Q9 | 菜单与页面内导航符合 Owner 口径：一级「经营分析」+ 4 二级；3 个分析页**左侧**页面内导航；组合查询直挂；无「产品分析器」 | E2E 复跑 + 目视 |
| Q10 | 同域多菜单激活不整组同亮：任一分析页仅 1 项高亮 | E2E + 截图 |
| Q11 | 认证旁路为 Owner 决策（不恢复）：免登录直达 `/analytics/*`，401 不跳登录页 | 浏览器无痕窗口直开深链 |
| Q12 | Owner 五项决策落地无遗漏 | 逐项查文件与代码 |

### 3.1 变异复验（仓库纪律：断言必须能变红）

| 变异 | 操作（须在副本或即改即还原，仓库不得留存） | 期望 |
|---|---|---|
| M1 | `cfg_analytics_param.alert_threshold` 改 `9.9` | `monitor-*` 的 `alerts` 变空 ⇒ 告警断言非恒真 |
| M2 | `profit_source` 改 `FTP`（数据无 FTP 列） | `/metrics` 必须 400 ⇒ 口径开关真生效 |
| M3 | 临时去 `combo_query` 白名单校验 | 注入用例必须变红 ⇒ 白名单断言非空转 |
| M4 | 任一 `.ts` 副本注入类型错误后跑 `vue-tsc` | 必须非 0 退出 ⇒ 证明 `frontend_typecheck` 非假绿 |
| M5 | `AppSidebar.isActive` 改回按 domain 判定 | 「仅 1 项高亮」断言必须变红 ⇒ 菜单断言有效 |

## 4. 红线

1. **只读复核**：不得修改实现/文档；变异须副本或即改即还原并留痕；
2. **不得以 mock 代替真实链路**：E2E 必须打真实 KERT 8107（未起服务即失败不降级）；
3. **不得放宽 fail-closed**：FTP 缺列 / 未配置分析库 / 白名单外取值三类拒绝必须保持；
4. **不得代签 Owner 决策**；不得自行恢复认证（Owner 明确「不恢复」）；
5. 发现文档与实现不符须**先记账再请示**，不得顺手改文。

## 5. 输出

- 报告：`loops/AN0-ccrm-analytics-landing/evidence/INDEPENDENT_QA-AN0-<session>.md`（逐条判定 + 命令 + 输出摘要 + 变异结果）；
- 判定通过：以 QA 角色记 `QA_PASS` 并更新 `STATE.json.qa_actor`；有 FAIL：记 `FAILURES.md`，TL 修复后重跑；
- 报告须含「未验证项」一节，明确写清因环境缺失未验内容（不得以推定代替）。

## 6. 修复轮靶标冻结（2026-09-22 修复轮，**QA 复判请以本节为准**）

> qa-an0-001 冻结的旧值见其报告 `INDEPENDENT_QA-AN0-qa-an0-001.md`；修复轮的当前基线如下。

### 6.1 门禁证据（修复轮 EVIDENCE.json）

| 门禁 | sha256 |
|---|---|
| kert_analytics_unit | `a2a3c4b68aa70416fb312e4aaae8e14c352c367fc692b27c4622eb9644d825cf` |
| kert_analytics_integration | `0db356ee91ac6f4323f5e9f7af3f60f50ef236bb0f748f141783308a103c3ab9` |
| frontend_typecheck | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| frontend_analytics_unit | `bc3bcbec21db844cdf7c2793214da0dcfb886e4d46c058465fa9f63b597f6b98` |
| e2e_analytics | `25a96d1681efc7262e4edeaedb7747c481fc090c70806762a28b744214e304e2` |
| analytics_params_failclosed | `700bc0322b00f8e8db3ce495047983b54ab27ab59ed1fedac05f3aeba47dae24` |
| analytics_trend_and_inactive_regression | `4d2df7a96ce4a667da3ccf295f2d16c728a65ed0e861a3baa919f7bb469b02b5` |

### 6.2 修复轮实现靶标

| 文件 | sha256 |
|---|---|
| `operational_analytics.py` | `15915d72308199f8b3b604c45e6b7a9dc78161077079fba042614797fe9020ee` |
| `analytics_store.py` | `e6dd9073ed55a0ac5470b3dbc3b8f1cc7a8f68cbe661428e84247721197b9837` |
| `server.py` | `f43859781b51de33afda7aefee1561bb764b779cdd2c18b910c296b832f4fa26` |
| `test_operational_analytics.py` | `f4cebe6e43e0a92b55c5d1e0e6b3e205cbeee5d115a77ce0459805868141b608` |
| `analytics.ts` | `6777dc6769be718f11dc3e70eee303c61956f3089e4980b92626835379d6a26c` |
| `AnalyticsResultsPanel.vue` | `01c037dc02181dddbdcdd5b62a7fe1adcdb1665abc4f198eefcc334dd2ff4b38` |
| `TrendChart.vue` | `fc30676833ab0a344ce69f773109e23674bdf4b34bef9e1efdecb784d855187f` |
| `analytics.spec.ts` | `9a8619c43d5dd0f6639f4f772794496f14d2c211e42899698f2162b3f0265302` |
| `AnalyticsViews.spec.ts` | `4d710aea4a5e1030dce3019866857a0a302abcc912fbb7ca7a4bc3241327ede6` |
| `loop_guard.py` | `f347a9496db8d973f00cdf354031e10198bc3b2d79ea16a4fed1ad1f2b6476b5` |

### 6.3 修复轮新增/变更要点（复判关注）

- 新增门禁 `analytics_trend_and_inactive_regression`（常驻防回潮）；
- `frontend_typecheck.pass_condition` 已改如实（e2e 不在 tsconfig include）；
- E2E 新增断言：趋势图 `polyline` 必须 ≥2 点、不得出现“趋势数据不足”/错误态；
- 造数新增约 8% 长期不动样本（使不动户 N 口径可观测、非恒 0）。
