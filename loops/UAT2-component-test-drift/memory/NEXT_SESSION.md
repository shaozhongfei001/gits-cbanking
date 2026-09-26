# UAT2-component-test-drift｜Next Session Baton

| 字段 | 值 |
|---|---|
| **Updated** | `2026-09-26T03:40:00+00:00` |
| **holder** | `independent_qa` |
| **packet** | `UAT2-component-test-drift` |
| **wave** | `三门禁全 PASS，待独立 QA` |
| **index_basis** | `INDEX_FRESH`（UAT1 收工实测 drift=0）；本批次结论全部回源 `文件:行`，未依赖派生索引 |
| **do_not_start** | QA_PASS、REAL_E2E_PASS、BUSINESS_SIGNED |

## 已完成（feature_pilot）

- `type_check` PASS（`vue-tsc --noEmit`）
- `component_test` PASS：**440 用例 439 passed + 1 expected fail（D-4 待裁决），0 failed**
- `e2e_regression` PASS：W0 + W1 + W2 共 **71/71**

## 修了什么

**真实缺陷（修实现）**
1. D-1 `navConfig.ts:88/101`：`/engagement/crm-writeback` 域映射被通用 `/engagement` 分支吞掉 ⇒ 死代码，
   CRM 回写页侧栏高亮/面包屑落在「经营旅程」。已把特化分支上移。
2. D-2 `AppSidebar.vue`：导航项/组标题缺 `data-testid`（`nav-item-<key>` / `nav-group-<key>`），
   既有 spec 与 E2E 老用例按该约定定位却取不到。已补（只加属性，未改结构样式）。
3. 四个视图 loading 骨架补齐 `data-testid="loading-state"`（Workbench/Signals/Accounts/Commitment）。

**测试期望过时（改测试，每条注明依据）**
- Workbench/Dashboard：「首页·我的客户经营」→ 当前 ObjectHeader「客户经营应用 / 经营总览」（router meta 一致）
- CommitmentDashboard：「任务与承诺」→「承诺事项」（与 navConfig 侧栏一致；路由 meta 差异登记 D-3）
- EngagementWorkspace：「互动记录·访前路径」→「互动 Interaction / 经营旅程」（router meta 一致）
- AppSidebar：折叠语义（只展开当前激活域）⇒ 渲染断言改数据层 + 点击前先展开分组
- 四态选择器：通用 `success-state/error-state` 仅由 `PageState.vue` 提供，这 6 个视图自绘四态 ⇒ 改用页面级 testid

**E2E 用例自身缺陷**
- F-UAT2-01：W1/W6 取「旅程列表第一条」被同批次「启动旅程」写入污染 ⇒ 新增 `pickJourneyId(customerId)` 按种子客户挑选。

## 下一棒（independent_qa）

1. 复跑 `component_test` 与 `e2e_regression`，确认非偶发绿；
2. 复核**改测试的 5 处**是否有放水（派工单第 2 节表格给了每条依据，须逐条对照回源）；
3. 复核 D-4（`it.fails` 固定 SignalsView 入口缺失）是否可接受，或要求 Owner 裁决；
4. 通过后写 `EVIDENCE.json.independent_qa`。

短提示词：你是 `independent_qa`。复核 UAT2 三门禁与 5 处测试期望变更的依据，独立复跑后再签 QA_PASS；不许沿用 implementation 自述。
