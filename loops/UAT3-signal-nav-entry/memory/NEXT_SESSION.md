# UAT3-signal-nav-entry｜Next Session Baton

| 字段 | 值 |
|---|---|
| **Updated** | `2026-09-26T04:05:00+00:00` |
| **holder** | `independent_qa` |
| **packet** | `UAT3-signal-nav-entry` |
| **wave** | `三门禁 PASS，待独立 QA` |
| **index_basis** | `INDEX_FRESH`；结论回源 `文件:行` 与 git 历史，未依赖派生索引 |
| **do_not_start** | QA_PASS、REAL_E2E_PASS、BUSINESS_SIGNED |

## 已完成（feature_pilot）

- `type_check` PASS、`component_test` PASS（11 用例）、`e2e_nav_entry` PASS（W2 8 用例）
- 全量 `npx vitest run`：**73 文件 / 440 用例全绿**（原 17 failed 与 1 expected fail 全部消除）

## D-4 的判定与修复（关键点）

- 判定依据不是"测试说了算"，而是**可达性**：
  - `git show HEAD:frontend/src/views/SignalsView.vue` 含跨页入口（131/134 行），被**在途未提交改动**删除；
  - `navConfig.ts` 无 `/engagements` 菜单项 ⇒ 删除后 P10 互动对象主页**无任何 UI 入口**（孤儿页）⇒ 真实退化，须恢复。
  - 页内 P08/P10/P11 Tab 由 `SignalsDomainTabs.vue:26/33/40` 提供且 `SignalsView.vue:129` 仍在使用 ⇒ **未缺失**，
    之前取不到是因为断言在入口处先失败（不是 Tab 被删）。
- 修复：恢复两个 `router-link`（`p08-open-engagements` / `p08-open-journey`）+ `.related-link` 样式；
  `it.fails` 改回正向断言；W2 新增浏览器用例「从信号页入口真的能到 /engagements 与 /engagement」。

## 变异复验（证明断言非空转）

- 变异：把 `data-testid="p08-open-engagements"` 改为 `…-MUTANT`
- 结果：SignalsView 用例 **1 failed / 4 passed**（捕获）
- 还原：**5 passed**（恢复）
- 结论：该用例对入口缺失敏感，不是空转断言。

## 下一棒（independent_qa）

1. 复跑 `component_test` 与 `e2e_nav_entry`；
2. 复核「恢复入口」的判断依据是否成立（侧栏确实无 /engagements 入口？若侧栏后续补入口，此处可再议）；
3. 通过后写 `EVIDENCE.json.independent_qa`。

短提示词：你是 `independent_qa`。复核 UAT3 的 D-4 修复依据与变异复验，独立复跑后再签 QA_PASS。
