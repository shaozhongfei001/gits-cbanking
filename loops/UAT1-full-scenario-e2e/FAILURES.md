# UAT1-full-scenario-e2e｜Failures（append-only）

失败必须在修改实现之前由 `scripts/record_gate.py`追加。每项至少包含时间、Gate、命令、退出码、证据文件、初步分类和下一动作；修复后追加根因、变更SHA与原命令重跑结果，不覆盖原记录。

## 20260925T185301Z｜w0_route_sweep

- Command: `bash scripts/uat_wave.sh w0_route_sweep e2e/uat/w0-route-sweep.spec.ts`
- Exit: `1`
- Evidence: `loops/UAT1-full-scenario-e2e/evidence/w0_route_sweep-20260925T185301Z.log`
- Classification: `PENDING_ROOT_CAUSE`
- Next: diagnose, record root cause, fix, rerun the original gate.

## 2026-09-26T02:53Z｜w0_route_sweep｜根因分析（E2E Owner 手工追加）

门禁结果：19 failed / 40 passed。失败归为三类，**分别对应不同的处置责任**，不得混为一谈。

### F-UAT1-01｜KERT 经营分析全端点 503（环境/配置缺陷，阻塞 UAT）
- 现象：`/analytics/operating-metrics`、`/analytics/segments`、`/analytics/combo-query`、`/analytics/monitors` 四页全部失败。
- 证据：`[http5xx] 503 GET http://127.0.0.1:5173/kert-api/v1/analytics/{orgs,dimensions,periods,metrics}`（各 8/2 次）。
- 回源：KERT `src/kert/api/server.py:1047` 返回 `ANALYTICS_UNAVAILABLE — 经营分析未接入（设置 KERT_ANALYTICS_DUCKDB 后重启）`；
  `_maybe_analytics_service()`（`src/kert/api/server.py:403`）未配置 env 则不接入。
- 实测：`curl http://127.0.0.1:8107/v1/analytics/orgs` → 503；8107 进程为
  `python scripts/serve_skill_service.py --port 8107 --host 127.0.0.1 --workspace bank_front_ws`，**未注入** `KERT_ANALYTICS_DUCKDB`。
- 可用数据源：`/home/szf/dev/Leibniz-KERT/examples/bank-front-analytics/cb_analytics.duckdb` 存在。
- 分类：`ENV_CONFIG`（非前端代码缺陷）。
- 处置（TL 派工-环境）：带 `KERT_ANALYTICS_DUCKDB` 重启 8107；重跑 W0 验证四页。

### F-UAT1-02｜13 个降级壳页「未发起后端请求」——门禁判定错误（非产品缺陷）
- 现象：`/proposals`、`/collab`、`/account-plans`、`/delivery`、`/value`、`/engagement/previsit/{gaps,evidence,pack}`、`/engagement/postvisit`、`/m/previsit`、`/m/notes`、`/in-meeting/:id/capture`（部分）被判「未发起后端请求」。
- 复核：逐页读取渲染文本，**均为诚实降级页**，显式写明 `C2 降级 / 禁止… / 解除路径：待 CCC …合同后由独立 Loop 启用` 或 `缺对象，暂无…`，
  **未伪造数据、未白屏**，符合项目诚实性红线（E1/E2）。
- 分类：`GATE_DEFECT`（我的门禁把「降级壳」误判为「未接数据的桩」）。
- 处置：W0 判定改为——无后端请求时，页面**必须**显式出现降级标注（C2 降级/未授权/禁止/缺对象/暂无/待接入/解除路径），否则才 FAIL。

### F-UAT1-03｜合成 ID 路由的 4xx 被判失败——门禁判定过严
- 现象：`/product-center/PROD-UAT-PLACEHOLDER`(400)、`/recommendation/UAT-RUN-PLACEHOLDER`(404)、`/supply-chain-report/UAT-SCG-PLACEHOLDER`(404)。
- 说明：这三个 ID 是我为覆盖路由而**故意构造的无效 ID**，4xx 属预期响应；真正要验的是「无效参数不得白屏/不得 5xx/须有友好提示」。
- 分类：`GATE_DEFECT`。处置：synthetic 路由不因 4xx 判 FAIL，改为断言页面给出可读提示。

### F-UAT1-04｜`/api/v1/recording-consents/latest/{journeyId}` 404（真实 journeyId）
- 现象：会中捕获页 `/in-meeting/<真实journeyId>/capture` 请求录音同意记录返回 404。
- 待定：属「种子数据无录音同意记录」还是「前端未降级」——由 W6 旅程闭环波次带着真实上下文复核，不在 W0 定性。

### F-UAT1-05｜门禁执行器受工具环境「批量删除保护」干扰（已修）
- 现象：首次运行 37 个用例报错 `[safe-delete][SAFE_DELETE_BULK_CONFIRM_REQUIRED] {count:500}`，与业务断言无关。
- 根因：Playwright 启动时清理旧 `test-results/**` 产物，单次删除文件数达阈值被工具环境拦截。
- 处置：新增 `scripts/uat_wave.sh`，每次运行使用**全新且已存在**的 `/tmp/uat-artifacts/<wave>-<ts>/raw`（无需删除旧文件）。
- 复验：本次门禁日志 `safe-delete` 计数 = 0。

## 20260925T185904Z｜w0_route_sweep

- Command: `bash scripts/uat_wave.sh w0_route_sweep e2e/uat/w0-route-sweep.spec.ts`
- Exit: `1`
- Evidence: `loops/UAT1-full-scenario-e2e/evidence/w0_route_sweep-20260925T185904Z.log`
- Classification: `PENDING_ROOT_CAUSE`
- Next: diagnose, record root cause, fix, rerun the original gate.

## 2026-09-26T03:05Z｜w0_route_sweep（第二次）｜新增根因

门禁结果：2 failed / 57 passed（KERT 修复生效：4 个经营分析页由 503 → PASS）。

### F-UAT1-06｜报告详情页伪造数据 + Loading 永不消失（P0 红线，阻塞 UAT）
- 现象：`/reports/<任意ID>`（含无效 ID）渲染出「R5A 内部关系报告 / INTERNAL_RELATIONSHIP / 生成时间: <当前时间> / 报告内容加载中...」，且**未发起任何后端请求**。
- 回源：`frontend/src/api/engagement.ts:455-470` `fetchReport()` 注释即写明「后端无独立报告端点，返回占位数据」，
  直接硬编码 `reportType='INTERNAL_RELATIONSHIP'`、`content='报告内容加载中...'`、`generatedAt=new Date().toISOString()`。
- 定性：**前端发明后端未返回的数据**（前端兜底规范 §3）+ **演示/占位数据冒充真实数据**（诚实性红线 E2）+ 典型失败模式「Loading 永不消失」。
- 分类：`PRODUCT_DEFECT` / `BLOCKER`。
- 处置：TL 派工 Feature Pilot —— 改接真实报告来源（`/api/v1/engagement/journey/{journeyId}/reports`），
  取不到时显式标注「报告不存在/未接入」，禁止占位冒充。合同先行（API First）。

### F-UAT1-07｜会中捕获页 `recording-consents/latest/{id}` 404 未降级
- 现象：`/in-meeting/<真实journeyId>/capture` 请求 `404 GET /api/v1/recording-consents/latest/<journeyId>`。
- 回源：后端 `RecordingConsentController.java:39-43` `/latest/{interactionId}` 无记录时 `ResponseEntity.notFound()`（404 是合同的「不存在」语义）；
  前端 `frontend/src/api/v11.ts:320` 以 **journeyId** 作为 interactionId 查询 → 语义可能不匹配。
- 分类：`PRODUCT_DEFECT`（未处理 404 降级；参数语义待 W6 复核）。
- 处置：W6 旅程闭环波次带真实 interactionId 复核；前端对 404 显式降级为「未取得录音同意」。

## 20260926T031124Z｜w5_analytics_domain

- Command: `bash scripts/uat_wave.sh w5_analytics_domain e2e/uat/w5-analytics-domain.spec.ts`
- Exit: `1`
- Evidence: `loops/UAT1-full-scenario-e2e/evidence/w5_analytics_domain-20260926T031124Z.log`
- Classification: `PENDING_ROOT_CAUSE`
- Next: diagnose, record root cause, fix, rerun the original gate.

## 2026-09-26T03:12Z｜修复与复验记录（E2E Owner 追加）

### F-UAT1-01 修复与复验
- 处置：以 `KERT_ANALYTICS_DUCKDB=/home/szf/dev/Leibniz-KERT/examples/bank-front-analytics/cb_analytics.duckdb`
  重启 KERT 8107（`scripts/serve_skill_service.py --port 8107 --host 127.0.0.1 --workspace bank_front_ws`）。
- 复验：`curl http://127.0.0.1:8107/v1/analytics/orgs` → 200；W0 的 4 个分析页由 FAIL 转 PASS；W5 门禁 6/6 PASS。

### F-UAT1-06 修复与复验（P0 红线）
- 变更：
  - `frontend/src/api/engagement.ts`：`fetchReport(reportId, journeyId?)` 删除占位伪造，
    改由既有 `fetchJourneyReports(journeyId)` 定位，取不到返回 `null`。
  - `frontend/src/views/ReportDetail.vue`：新增 `notFoundReason` 三态（加载中 / 未找到 / 成功），
    未找到时以 `NResult` 显式说明「报告详情未接入独立端点，需携带 journeyId」。
  - `frontend/src/api/__tests__/engagement.spec.ts`：把「fetchReport returns placeholder」改为
    「无 journeyId 返回 null 且不发请求」+「带 journeyId 按 id 定位，找不到返回 null」。
- 复验：单测 38/38 通过；`vue-tsc --noEmit` 通过；W0 门禁 RP-01 由 FAIL 转 PASS（59/59）。

### F-UAT1-07 修复与复验
- 变更：`frontend/src/views/MeetingCaptureView.vue` —— 录音同意改按**客户维度**查询
  （`fetchRecordingConsents({ customerId })`），不再用 journeyId 打 `/recording-consents/latest/{interactionId}`。
- 复验：W0 门禁 P16 由 FAIL 转 PASS（59/59）。

### 变异复验（证明断言非空转 —— 本轮最关键的一条）
- 变异：kill KERT 8107（真实故障注入，非改代码）。
- 期望：W5 必须 FAIL。实测：W5 **5 failed / 1 passed**，
  失败项覆盖 4 个分析页（`/analytics/*` 全部判定失败）+「分析页缺少筛选器」。
- 恢复：带 DuckDB env 重启 8107 → health 200 / orgs 200 → 复跑 W5 **6/6 PASS**。
- 结论：W5 的「必须调用 KERT + 无 5xx + 无白屏」断言具备真实捕获力，不是空转断言。
- 同类证据（天然变异）：W0 首跑捕获 KERT 503（4 页）与报告页伪造；W1 捕获启动旅程 URL 未变；
  W3 捕获产品目录选择器失效；W8 首跑捕获「glob 误伤 /src/api 造成假白屏」（F-UAT1-08，已修，并补 `injected > 0` 的注入生效断言）。

### F-UAT1-08｜W8 门禁自身缺陷（glob 误伤源码模块 + 注入生效未校验）
- 现象：W8 首跑 12 个用例全 FAIL，报「500/空数据注入后白屏」与 goto 超时。
- 根因：`page.route('**/api/**')` 命中前端源码模块 `/src/api/*.ts`，把应用自身打挂 ⇒ **假白屏**；
  且未校验故障注入是否真的命中（注入未生效也会「通过」）。
- 处置：改为 URL 谓词 `isBackendApi`（只匹配 `/api`、`/kert-api`，显式排除 `/src/`、`/node_modules/`），
  并为 4 类故障各加 `expect(injected).toBeGreaterThan(0)`（fail-closed）。
- 复验：W8 12/12 PASS。

### F-UAT1-09｜合同缺口（登记，未擅自改合同）
- 事实：后端已实现 `GET /api/v1/engagement/journey/{journeyId}/reports`（`EngagementJourneyController.java:114`），
  前端 `fetchJourneyReports` 已在调用，但 `specs/openapi/gits-kno-api.openapi.json` **未登记**该路径，
  `components.schemas` 也无 `RelationshipReport`。
- 处置：登记待 TL/Contract Owner 补合同（本轮不擅自改合同，避免越权与 `make check` 漂移）。

### F-UAT1-10｜前端存量单测 17 failed（UI 文案/导航与组件测试漂移）—— **非阻塞**，登记待修
- 现象：`npx vitest run` → 440 用例中 17 failed（3 个文件：
  `src/views/__tests__/WorkbenchView.spec.ts`、`src/views/__tests__/SignalsView.spec.ts`、
  `src/components/shell/__tests__/AppSidebar.spec.ts`）。
- 根因（回源）：期望文案过时 —— 实测页面渲染「客户经营应用 / 经营总览 / 当前状态：今日」，
  而测试仍断言旧文案「首页·我的客户经营」（`WorkbenchView.spec.ts:71`）；导航类用例同因。
- 与本轮修复**无关**：三个失败文件均不引用本轮改动的 `fetchReport` / `ReportDetail` /
  `fetchRecordingConsents`（已 grep 确认零命中）；`src/api/__tests__/engagement.spec.ts` 单跑 38/38 通过。
- 与浏览器级 E2E 的关系：115 个 E2E 用例全绿，导航与页面在真实浏览器实测可用；
  该问题属**组件级测试漂移**（技术债），不阻断人工 UAT，但仓库并非全绿，须告知 Owner。
- 分类：`PRE_EXISTING_DEBT` / 非阻塞。处置：派工 Feature Pilot 更新这三组组件测试期望。

## 2026-09-26T03:42Z｜F-UAT1-10 修复完成（feature_pilot，批次 UAT2-component-test-drift）

- 交付批次：`loops/UAT2-component-test-drift`（三门禁 PASS：type_check / component_test / e2e_regression）。
- 结果：`npx vitest run` → **440 用例 439 passed + 1 expected fail（D-4 待裁决），0 failed**；
  E2E 回归 W0+W1+W2 **71/71 PASS**。
- 修到的**真实实现缺陷**（不是改测试放水）：
  1. `navConfig.ts` 中 `/engagement/crm-writeback` 域映射被通用 `/engagement` 分支吞掉（死代码）→ CRM 回写页侧栏高亮错位；
  2. `AppSidebar.vue` 导航项缺 `data-testid`（`nav-item-<key>`/`nav-group-<key>`）→ 既有 spec 与 E2E 定位不到；
  3. 四个视图 loading 骨架缺 `data-testid="loading-state"`。
- 更新为当前实现的测试期望（依据见 `docs/dispatch/UAT2-component-test-drift-派工单-V1.0.md` 第 2 节）。
- **遗留待 Owner 裁决（D-4）**：SignalsView 的「P08/P10/P11 页内 Tab + 跨页入口」在当前实现中不存在，
  已用 `it.fails` 如实固定（补回入口时该用例会报警）。E2E 老用例 `five-scenarios.live.spec.ts` 仍在按这些
  testid 做**条件式断言**（找不到就跳过），属空转形态，建议一并清理。
- **遗留待设计裁决（D-3）**：`/commitments` 路由 meta title「任务与承诺」与侧栏/对象头「承诺事项」不一致。

## 2026-09-26T04:06Z｜D-4 已修复（批次 UAT3-signal-nav-entry）

- 判定：跨页入口被**在途未提交改动**删除（HEAD 版存在），且侧栏无 `/engagements` 菜单项 ⇒ P10 成孤儿页 ⇒ **真实可达性退化**（不是"测试过时"）。
- 修复：恢复 `p08-open-engagements` / `p08-open-journey` 两个 router-link 与样式；`it.fails` 回正向断言；
  W2 新增浏览器用例「从信号页入口真的能到 /engagements 与 /engagement」。
- 复核纠错：页内 `signals-tab-*` **并未缺失**（`SignalsDomainTabs.vue` 提供且 SignalsView 仍在使用），
  此前"页内 Tab 已不存在"的表述不准确，以本条为准。
- 门禁：type_check / component_test(11) / e2e_nav_entry(8) 全 PASS；全量 `npx vitest run` → **440/440 全绿**。
- 变异复验：改坏入口 testid ⇒ 用例 1 failed；还原 ⇒ 5 passed（断言非空转）。
- 遗留建议（未做，登记）：E2E 老用例 `five-scenarios.live.spec.ts` 仍按 `signals-tab-*` 做**条件式断言**
  （元素不存在就跳过），属空转形态，建议后续清理。

## 2026-09-26T04:15Z｜D-3 已修复（TL 派工 d3-fixer）

- 决策：以侧栏标签「承诺事项」为准（用户导航入口是权威命名源）。
- 变更：`frontend/src/router/index.ts:268` meta.title 从「任务与承诺」→「承诺事项」。
- 全局确认：`grep -rn "任务与承诺" frontend/src/` → 零命中。
- 交付包中「待 Owner 裁决」清单已清空（D-3 和 D-4 均已修复）。
