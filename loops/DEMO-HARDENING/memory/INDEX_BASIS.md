# INDEX_BASIS — 演示就绪批次（2026-11-14）

## 索引新鲜度

- 开工：`INDEX_ABSENT @ make index-status` → `WARN: F1 索引产物缺失：.ua/knowledge-graph.json`、`WARN: F2 merge-meta 未记录 kertCommit`。
- 收工：`INDEX_ABSENT`，`ua_index_gate: WARN (nodes=None)`；本机未建立两仓合并图。
- 因索引未覆盖，本批次全部按 **L4 回源** 定位；以下只记「候选影响面 + 回源结论」，索引本身为 DERIVED，不作 Gate / ADR 依据。

## 候选影响面（索引缺席，改由文件清单给出，非索引产物）

- `scripts/demo-startup.sh`、`scripts/demo-smoke.sh`、`DEMO-FREEZE.md`、`.gitignore`
- `frontend/playwright.config.ts`、`frontend/e2e/uat/*`、`frontend/e2e/qa-e2e-acceptance.spec.ts`
- `frontend/src/api/productCenter.ts`、`frontend/src/components/product-center/ProductChapterStack.vue`
- `frontend/src/assets/styles/theme.css`（只读回源，未修改）
- KERT：`src/kert/application/skills.py`、`src/kert/application/product_recommendation/eligibility.py`

## 回源结论（文件:行，全部指向 2026-11-14 本批次落盘版本）

| 结论 | 回源 |
|---|---|
| E2E 原指向 5173、代理默认 8080，与演示链路不一致 | `frontend/playwright.config.ts:3,35,46`（现统一 15173 并注入 18080/8107） |
| 截图证据沿用 `QA_EVIDENCE_DIR` 单一约定，未另造目录 | `frontend/e2e/uat/_harness.ts:8,9,202-205`；`.gitignore:45`（`test-results/`） |
| Playwright 每轮清空 `outputDir`，证据须与之隔离 | `frontend/playwright.config.ts:21` |
| 单后端并发导致时序红灯，收敛到 4 worker | `frontend/playwright.config.ts:15` |
| PRICING 章节有 `pricingItems` 却无渲染分支 ⇒ 空壳 | `frontend/src/components/product-center/ProductChapterStack.vue`（本批次新增 06 分支，字段对齐 `specs/product-center/product-center-api.openapi.json` 的 `PkcPricingItem`） |
| V9 设计令牌（白侧栏 / 17 项菜单 / Inter 字体栈）与 V8.1 遗留断言漂移 | `frontend/src/assets/styles/theme.css`（`--v8-sidebar-bg:#FFFFFF`、`--font-sans` 含 Inter）；`frontend/src/layouts/navConfig.ts`（5+4+2+2+4=17） |
| KERT 示意型 output-schema 的嵌套键被误当顶层必含键 | `Leibniz-KERT/src/kert/application/skills.py:69,298` |
| 产品卡 `minRating: BB` 不在 `_RATING_ORDER` 内致 `tuple.index` 抛错 | `Leibniz-KERT/src/kert/application/product_recommendation/eligibility.py:80` |
| 日志固定为 `logs/demo/`，PID 文件 `logs/demo/pids/`，`stop_stack` 不再用 `pkill -f` | `scripts/demo-startup.sh:40,41,80,93,188` |
| `status` 的 READY = 4 端口 200 + 冒烟 0 FAIL | `scripts/demo-startup.sh:326`；`scripts/demo-smoke.sh` 末行 `exit "$FAIL"` |
| `up` 与 `restart` 同一分支，`restart` 必先 `stop_stack` | `scripts/demo-startup.sh:389` |

## 追加批次（2026-11-15）：P15 会中工作区刷屏

- 索引仍 `INDEX_ABSENT`，按 L4 回源；本批次为 Feature Pilot 前端改动，未做架构面外推。
- **根因（浏览器实证）**：`frontend/src/views/InMeetingAssistant.vue` 的 `onMounted → startPolling()` 每 5s
  调 `loadWorkspace()` → `useHumanGate.loadGates` / `useCrmWriteback.loadCommands` 每次置 `loading=true`
  → 页面 `status` 反复切到 `loading` → `frontend/src/components/shell/PageState.vue:19-32` 把整个三栏
  `<slot>` 卸载换成 spinner。实测 13s 内 `page-state-loading ⇄ success` 循环 3 次；无 4xx/5xx、无 console error，
  故**不是接口报错**。副作用：输入框 DOM 每 5s 重建、焦点与光标丢失。
- **修复**：四态只由首次加载/手动重试驱动（`initialLoading` / `initialError`）；5s 轮询改走静默通道
  `refreshWorkspace()`，直接经 `api/v11.ts` 取数写回列表 ref，不置 loading、防重入、失败显式提示且保留上次结果；
  侧栏重复 `NSpin` 移除，四态归一到 `PageState`。修复后 13s 状态序列仅 `none → loading → success`，
  输入节点与内容保留。
- 文案按 Owner 指令改为「未解读 / 开始解读 / 解读中 / 停止解读」；「会议记录」页签新增预生成的
  客户经理 ↔ 客户对话（10 轮，纯前端演示样例，显式标注 DEMO，不冒充真实业务数据）。
- 验证：`vue-tsc` 通过；`vitest` 458/458；P15 UAT 巡检通过；全量 E2E `180 passed / 0 failed / 2 skipped`。
- 未纳入范围：`RecordingConsentPanel.vue` 与 `F05_RECORDING_APPROVE: '录音授权'` 属后端合同中的
  「录音授权」业务概念（P16 实时捕获页），非本次四个按钮文案，改之需先走 OpenAPI 合同变更。

## 追加批次（2026-11-15）：全站页头一行化（layout 压缩）

- 索引仍 `INDEX_ABSENT`，按 L4 回源；本批次为 Feature Pilot 前端布局压缩。`impeccable context`
  引擎下载被网络拒绝，按技能回退路径读取仓内 `frontend/DESIGN.md` 与 `reference/layout.md`、
  `reference/craft-floor.md`。
- **盘点结论**：三段式页头唯一公共实现是 `frontend/src/components/shell/ObjectHeader.vue:29-42`；
  34 个 `.vue` 直接引用，另有 17 个视图经 `GovDegradeShell.vue:69` / `ProposalDegradeShell.vue:118` /
  `MobileDegradeFrame.vue:16` 间接引用，合计 **51 页**。其中 11 页用 `<template #actions>` 覆盖默认的
  「返回并恢复位置」，操作区仍恒在最右。
- 例子回源：`frontend/src/views/WorkbenchView.vue:12,153-158`（`OBJECT_TYPE='客户经营应用'`、
  `title='经营总览'`、`object-status='今日'`）；`frontend/DESIGN.md:182` 约定 ObjectHeader 职责且禁止页面自建 h1。
- **空间根因**：原 `ObjectHeader.vue:31-33` 三个块级元素竖排 + `h1` 30px（`:69-76`），头部实测 **99px**。
  现删除大号标题的视觉呈现（`sr-only h1` 保留无障碍语义与被 9 个测试锁定的文本契约），
  对象类型 + 当前状态同一行，`.object-actions` 用 `margin-left:auto` 恒最右；间距改 `--space-*`、
  字号改 `--text-xs/--text-sm`。
- 同步修复：`frontend/src/views/EngagementWorkspace.vue:265,372-379` 的「ObjectHeader + 自绘 hero」双 h1
  冲突，hero 客户名 30px → `h2` + `var(--text-xl)`；`frontend/DESIGN.md:182` 与
  `frontend/src/components/shell/__tests__/ObjectHeader.spec.ts` 同步约定与结构断言。
- 实测：Playwright 在 1440 / 1024 / 640 三宽度下 header **99px → 37px**，三项 `sameRow=true`、
  `srTitleHidden=true`、`actionsRightmost=true`，无 4xx / console error；暗色 `data-theme=dark` 下变量自动切换、
  高度一致。`vue-tsc` 通过；`vitest` 458/458；单测 33/33（header 相关 5 个文件）。
- **未纳入（待 Owner 确认）**：8 处自建大标题（`Login.vue:45` 品牌、`ProductHero.vue:21` 产品名、
  `Analytics*View` 的 18px 标题、`ExternalEventMonitor.vue:3`、`SupplyChainGraphReport.vue:14`、
  `ReportDetail.vue:15`）属于页内内容标题，不是「小标题 + 当前状态 + 返回并恢复位置」三段式页头，
  删除会损失关键信息；本次只统一三段式页头。

## 校验现状

- `make index-status` → WARN（索引缺失），退出码 0。
- `make memory-check LOOP=DEMO-HARDENING` / `make evidence-check LOOP=DEMO-HARDENING` → FAIL：
  缺 `EVIDENCE.json` / `EVIDENCE.md` / `FAILURES.md` / `HANDOFF.md`，以及共享记忆 5 件套
  （`SHARED_MEMORY.md`、`memory/PROTOCOL.md`、`ROLE_BOARD.yaml`、`ORCHESTRATOR.md`）。
  这些文件自 2026-10-28 该 Loop 建立即缺失，且 `STATE.json` 已冻结 `qa_pass`；
  本批次**不补造历史证据**，登记为遗留问题。
