# UAT2-component-test-drift 派工单 V1.0（TL → Feature Pilot）

> 来源：UAT1 全场景 E2E 收尾时暴露的 **F-UAT1-10**——`npx vitest run` 440 用例中 **17 failed**（7 个 spec 文件）。
> 立场：**不得为了让测试变绿而改测试**。每个失败必须先判定「实现错」还是「期望过时」，判定依据必须可回源。

## 1. 已定位的两处**真实缺陷**（修实现，不许改测试放水）

#### D-1（已修复）｜`navDomainForPath` 存在不可达分支（死代码）
- 回源：`frontend/src/layouts/navConfig.ts:88` `if (path.startsWith('/engagement') …) return 'journeys'`
  排在 `:101` `if (path.startsWith('/engagement/crm-writeback')) return 'crm-writeback'` **之前**，
  导致后者永远不可达。
- 后果：访问 `/engagement/crm-writeback` 时侧栏高亮与面包屑落在「经营旅程」，而非「CRM 回写」。
- 修复：把 crm-writeback 分支**上移**到通用 `/engagement` 分支之前。
- 验收：`AppSidebar.spec.ts > selects correct domain` 中 `navDomainForPath('/engagement/crm-writeback') === 'crm-writeback'` 由红转绿（该断言本身是**正确的**，不许改）。

#### D-2（已修复）｜侧栏导航项缺少 `data-testid`（可测性缺陷）
- 回源：`frontend/src/components/shell/AppSidebar.vue:106-117` 的 `.nav-item` 按钮只有 class，**无任何 data-testid**；
  而既有 spec（`AppSidebar.spec.ts:121/128/135`）与 E2E 老用例（`e2e/five-scenarios.live.spec.ts`）都按
  `nav-item-<key>` 约定定位。
- 修复：为 `.nav-item` 加 `:data-testid="`nav-item-${item.key}`"`，为组标题按钮加 `:data-testid="`nav-group-${group.key}`"`。
- 约束：**只加属性，不改 DOM 结构与样式**。

## 2. 属「测试期望过时」的部分（改测试，但每条必须写明依据）

| # | 位置 | 旧期望 | 现状（回源依据） | 处置 |
|---|---|---|---|---|
| 1 | `WorkbenchView.spec.ts:71`、`Dashboard.spec.ts:53` | `'首页·我的客户经营'` | 页面渲染 `客户经营应用 / 经营总览 / 当前状态：今日`（ObjectHeader 结构，与 `router/index.ts:18` meta `objectType:'客户经营应用'`、`objectStatus:'今日'` 一致） | 改为断言 `客户经营应用` + `经营总览` |
| 2 | `CommitmentDashboard.spec.ts:83` | `'任务与承诺'` | 页面对象头渲染 `承诺事项`（与 `navConfig.ts:33` 侧栏 `承诺事项` 一致） | 改为 `承诺事项`；**登记 D-3 命名不一致** |
| 3 | `EngagementWorkspace.spec.ts:128` | `'互动记录·访前路径'` | 渲染 `互动 Interaction / 经营旅程`（与 `router/index.ts:173` meta `objectType:'互动 Interaction'`、`objectStatus:'经营旅程'` 一致） | 改为断言这两段 |
| 4 | `AppSidebar.spec.ts:75-87`（在 `/workbench` 下断言全部子项文案） | 文本含 `客户组合/经营信号/审计追踪/…` | 侧栏按**当前域自动展开**（`AppSidebar.vue:14-20`），`/workbench` 下只展开「经营」组 —— 折叠是设计行为，非缺陷 | 改为：①断言 `SHELL_NAV_ITEMS` 数据层完整；②在**对应域路由**下断言渲染与点击 |
| 5 | `AppSidebar.spec.ts:119-138`（在 `/workbench` 下点 portfolio/signals/audit-trace） | 元素存在并可点击 | 同上，未展开时元素不渲染 | 改为挂载到对应域路由（`/accounts`、`/signals`、`/audit-trace`）后再点击 |
| 6 | `SignalsView/AccountsView/CommitmentDashboard/WorkbenchView/EngagementWorkspace` 中的 `success-state` / `error-state` / `loading-state` | 通用四态 testid 存在 | 通用四态 testid **仅由 `PageState.vue` 提供**；这 6 个视图自绘四态，用页面级 testid（如 `p01-error`、`p01-empty`、`p08-signals`） | 改用视图真实 testid；视图仅补齐**确实缺失**的 loading testid |

#### D-3（已修复，TL 派工 d3-fixer）｜路由 meta title 与侧栏命名统一为「承诺事项」
`router/index.ts:267` 路由 meta title 为「任务与承诺」，而侧栏（`navConfig.ts:33`）与页面对象头为「承诺事项」。
三者不一致属**命名一致性**问题，需 Owner/设计裁决；本批次只对齐测试，不改命名。

## 3. 完成判据（三个门禁）

1. `cd frontend && npx vue-tsc --noEmit` → 0 错误
2. `cd frontend && npx vitest run` → **440 全绿**
3. `bash scripts/uat_wave.sh uat2_regression e2e/uat/w0-route-sweep.spec.ts e2e/uat/w1-workspace-domain.spec.ts e2e/uat/w2-customer-domain.spec.ts` → 全绿（证明未破坏运行时）

## 4. 纪律

- 先 `FAILURES.md` 记录再修复；每个修复注明回源 `文件:行`。
- 禁止为了让测试变绿而放宽断言到「只检查页面不为空」。
- 修完把 Baton 交回 `e2e_owner` 复跑 UAT1 波次。

## 5. 修复过程中新增的登记项

#### D-4（已修复，批次 UAT3-signal-nav-entry）｜SignalsView 跨页入口已恢复
- 事实：`SignalsView.spec.ts` 断言的 `p08-open-engagements`、`p08-open-journey`、
  `signals-tab-p08/p10/p11` 在 `frontend/src/views/SignalsView.vue` 中**全文 grep 无命中**；
  当前页面只有 `p08-signals / p08-filter / loading-state / p08-error / p08-signal-list / p08-empty`。
- 含义：要么这些入口在 V8 改版中被**有意移除**，要么属**功能退化**（E2E 老用例 `five-scenarios.live.spec.ts`
  仍按这些 testid 定位，实际会静默跳过——这正是"条件式断言空转"的典型形态）。
- 处置：不以删除用例的方式掩盖，改用 `it.fails` 如实固定现状；一旦入口补回，该用例将"意外通过"而报警。
- 需 Owner 裁决：保留入口（派工实现）还是确认移除（同步清理 E2E 旧用例）。

## 6. D-3 修复记录（批次 UAT3-signal-nav-entry 后续，TL 派工 d3-fixer）

- 决策：以侧栏标签「承诺事项」为准（用户导航入口是权威命名源）。
- 变更：`frontend/src/router/index.ts:268` meta.title 从「任务与承诺」→「承诺事项」。
- 同步：`CommitmentDashboard.spec.ts:83-84` 断言注释更新。
- 全局确认：`grep -rn "任务与承诺" frontend/src/` → 零命中。

## 7. QA 复核次要发现（2026-09-26，independent_qa session qa-uat2-20260926）

1. 第 3 条称 router meta `objectStatus:'经营旅程'`，实际为 `'访前路径'`。EngagementWorkspace 用硬编码 `title="经营旅程"` 覆盖，断言仍正确。派工单描述与源码不一致，但不影响测试有效性。
2. 第 5 条称"6 个视图自绘四态"，EngagementWorkspace 实际使用 PageState 组件（非自绘）。测试断言与实际渲染一致，不影响正确性。
