# 经营旅程：第一入口列表化 + 工作区 URL 化 — 变更登记 V1.0

- **DOC_ID**: DISP-ENG-JOURNEY-LIST-001
- **登记日期**: 2026-09-25
- **登记角色**: Feature Pilot（Owner 决议为 2026-09-25 会话内裁定）
- **权威源关系**: 本文件**补充**（不替代）`docs/dd/GITS_Bank_信号与互动_互动记录访前路径_UX改造方案_V1.0_20260829.md`（下称 UX-V1.0，仍为 DESIGN_CANDIDATE）
- **性质**: 设计变更登记 + 合同变更说明 + 影响面清单

---

## 1. 变更内容（Owner 决议 2026-09-25）

| # | 变更 | 决议 |
|---|---|---|
| 1 | 二级菜单「经营旅程」第一入口由**工作区**改为**经营旅程列表** | 方案 **B** |
| 2 | 工作区身份改为 **URL 路径参数**：`/engagement/workspace/:journeyId`（无 journeyId 一律重定向列表） | 方案 B |
| 3 | 新增**确定性解析页** `/engagement/enter?customerId=X`（0 条→引导启动；**恰好 1 条活跃→直接进入**；多条→选择） | 做 |
| 4 | 列表**只列已创建旅程** | 需求原文「(例如未启动)」**删除** |
| 5 | 工作区内「切换客户」→「**返回列表**」 | 采纳 |
| 6 | 新增 `journeyName`（启动时可选填写 + 缺省派生），本轮**不含**列表内重命名 | 采纳 |

### 1.1 对 UX-V1.0 的 supersede 关系（局部）

UX-V1.0 的以下表述**被本次局部取代**（其余 P12–P19 章节继续有效）：

| UX-V1.0 位置 | 原文要点 | 本次变更后 |
|---|---|---|
| §3 原则 1（:82-84） | P11 回归「互动记录对象主页」，不承载阶段细节 | 不变（工作区职责未变） |
| §4.2（:110-112） | **P11 = 「互动记录·访前路径」record_detail，作为该域入口** | **入口改为 P45 列表**；P11 降为该域的**记录详情页**（URL 必须带 journeyId） |
| §7 AC-11（:220） | 「进入 P11 首屏可见对象/状态/主动作/下一步」 | 调整为：进入 **P45 列表**首屏见旅程列表；进入 **P11（带 journeyId）** 见对象/状态/主动作/下一步 |

> 说明：UX-V1.0 文件**保留原样不修改**（遵循"不删除历史文档、冲突时保留旧文件并登记"）。
> 页面编号：新增 **P45**（经营旅程对象主页/列表）；助手路由 `/engagement/enter` 不分配 pageId（同 `/journeys/:id` 先例）。

---

## 2. 合同变更（`specs/openapi/gits-kno-api.openapi.json`，CTR-API-001）

| 项 | 变更 | 兼容性 |
|---|---|---|
| `GET /engagement/journey` | **新登记**（此前前端已消费但合同未声明 → 修正"实现有、契约无"漂移）；`customerId` 改为**可选**（省略 ⇒ 全量），`operationId: listEngagementJourneys` | 兼容（既有 `?customerId=` 行为不变） |
| `CustomerJourney` | 新增 `customerName` / `operatingCaseId` / `journeyName` / `updatedAt`（均对齐运行时 record） | 兼容（新增字段） |
| `JourneyStartRequest` | 新增可选 `journeyName` | 兼容 |
| `JourneyStartResponse` | 新增 `operatingCaseId` / `journeyName` / `kycGapSummary`；`phase` 改为 `$ref JourneyPhase` | 兼容（新增字段） |
| `JourneyPhase` | **枚举修正**：`INITIATED/PREVISIT/IN_VISIT/POSTVISIT/FOLLOW_UP/COMPLETED` → `KYC_COLLECT/INSIGHT_ANALYSIS/PRODUCT_MATCHING/PREVISIT_PREP/POSTVISIT_REVIEW/COMPLETED` | ⚠️ **具名破坏性变更**（enum 值变更），理由：契约是唯一失真方（前端 TS 类型与标签、运行时 Java 均为后者）；实际消费者破坏面 = 0 |

- 生成门禁：`make generate` → `make check`（`contract-check` / `enum-consistency` / `registry-contract` / `contract-examples` / `contract-coverage` 全 PASS）
- `generated/openapi/gits-kno-api.normalized.json` 由 `make generate` 产出，**未手工编辑**

---

## 3. 数据与后端变更

| 项 | 内容 |
|---|---|
| 迁移 | `V024__journey_name.sql`（`h2/` 与 `mysql/` 双份）：`ALTER TABLE customer_journey ADD COLUMN journey_name VARCHAR(256) NULL` |
| 领域 | `CustomerJourney` 增 `journeyName`（**附 7 参兼容构造器 ⇒ 18 处既有调用点零改动**） |
| 派生规则 | 新增 `CustomerJourneyNaming`（**单一事实来源**）：缺省 `{客户名称} 经营旅程 #{N}`，N = 该客户已有旅程数 + 1；历史行（`journey_name` 为 NULL）由读取侧同规则兜底，**不回填、不伪造人工值** |
| Port | `CustomerJourneyRepository.findAllJourneys()`（按 startedAt 倒序） |
| 适配器 | MyBatis（`CustomerJourneyMapper` + XML，`journey_name` 列映射）与 JDBC 兜底实现同步 |

---

## 4. 路由与页面

| 路由 | 页面 | pageId |
|---|---|---|
| `/engagement` | `JourneyListView.vue`（**列表**，唯一无参入口） | **P45** |
| `/engagement/workspace/:journeyId` | `EngagementWorkspace.vue`（工作区，身份来自 URL） | P11 |
| `/engagement/workspace` | **重定向 → 列表**（铁律：无 journeyId 不得渲染工作区） | — |
| `/engagement/enter` | `JourneyEnterResolver.vue`（确定性直达） | — |

---

## 5. 影响面（既有断言/证据物已同步）

| 文件 | 动作 |
|---|---|
| `frontend/src/router/__tests__/routes.spec.ts` | `/engagement` → `JourneysHome`(P45)；新增 workspace/enter 断言与重定向断言 |
| `frontend/src/views/__tests__/EngagementWorkspace.spec.ts` | 重写：journeyId 驱动、缺 id 重定向、无「启动/切换客户」入口 |
| `frontend/src/views/__tests__/JourneyListView.spec.ts` | 新增（列/持续经营/启动进入/错误态） |
| `frontend/src/views/__tests__/JourneyEnterResolver.spec.ts` | 新增（0/1/多条/无 customerId/错误） |
| `frontend/src/views/__tests__/CustomerOperatingView.spec.ts` | 补 `JourneyEnterResolver` 测试路由 |
| `frontend/e2e/customer-manager-flow.spec.ts` | 列表用例 + 工作区 URL 化 + 重定向铁律 + 错误态 |
| `frontend/e2e/full-experience.spec.ts` | 用例 4 改用 `/engagement/workspace/jrn-001` |
| `frontend/e2e/signals-engagement.live.spec.ts` | 第一入口=列表；启动→工作区 URL；解析页直达 |
| `frontend/e2e/five-scenarios.live.spec.ts` | S1/S5 走列表启动；S2/S6 走解析页直达 |
| `frontend/e2e/previsit-chain.live.spec.ts` | ① 改为"列表启动 → 工作区 URL" |
| `frontend/e2e/sit-fixtures.ts` | `mockJourney` 增 `journeyName` |
| `frontend/scripts/w9a-escort.spec.ts` | 新增 P45 行；P11 行改为 `/engagement/workspace/jrn-001` |
| `frontend/tools/walkthrough/run.mjs` | ① 步骤改为"从列表启动旅程" |

### 5.1 待同步（历史台账，本次未改，需登记方裁决）

- `docs/dispatch/GITS-业务流程打通台账-V1.0.md:21` 与 `:29`（仍以 `/engagement` 为 P11 入口）
- `docs/demo/GITS-BUSINESS-SCENARIO-CATALOG.md:68`（P11 路径 `/engagement`）

> 未直接改写：属历史记录，遵循"保留旧文件 + 登记 superseded"。

---

## 6. 新增验收口径

| ID | 判据 |
|---|---|
| AC-J1 | `/engagement` 首屏 = 列表；列含 经营旅程名称/ID、客户名称、旅程状态、开始时间、继续旅程；空态不编造行 |
| AC-J2 | 「启动旅程」→ 选客户 → URL 变为 `/engagement/workspace/{uuid}`，状态条不再显示「未启动」 |
| AC-J3 | 未结束旅程显示「持续经营」，点击进入的 journeyId 与列表行一致 |
| AC-J4 | 无 journeyId 的 `/engagement/workspace` 重定向列表；不存在的 id → 具名错误态（**不得降级为"未启动"**） |
| AC-J5 | 刷新 / 新标签打开 workspace URL → 同一旅程、同一客户（不依赖会话状态） |
| AC-J6 | `/engagement/enter?customerId=X` 三态正确（0 / 1 / 多条） |

---

## 7. 验证证据（2026-09-25）

| 门禁 | 结果 |
|---|---|
| `make generate` / `make check` | PASS（合同类门禁全绿） |
| 后端（Maven，跳过 dependency-check） | 编译通过；新增 16 项测试通过（`CustomerJourneyNamingTest` 7 + `EngagementJourneyControllerTest` 9） |
| **`make backend-test`（JaCoCo 段）** | ✅ **已闭环**：发现时 0.7827 < 0.80（**归因=存量**）→ Owner 裁决「单独修复存量覆盖」→ 补 34 项测试后 **0.8252 ≥ 0.80**，`mvn verify` **BUILD SUCCESS**；详见 `FAILURES.md` FAIL-2026-09-25-01【已闭环】 |
| `make backend-test`（dependency-check 段） | ⚠️ 本机无法完成（OWASP 需 NVD 数据，无 API Key 时限流耗时不可接受）；本次**零依赖变更**，与该扫描结论无关 |
| `vue-tsc --noEmit` | PASS |
| `vitest run` | PASS（73 文件全绿） |
| `vite build` | PASS |
| 非 live E2E | 58 passed / 10 failed（**10 项为既有失败**：analytics×4、customer-detail×1、product-center×2、qa-acceptance×3，均不涉及本域） |
| live E2E（真实后端 18080 + KERT 8107） | `signals-engagement` 5 passed；`previsit-chain` 1 passed（含真实 `prepare-previsit` KERT fan-out）；`five-scenarios` 6 passed |
| 运行期实测 | `GET /engagement/journey`（无参）200 且返回 4 条历史行动态派生名称；启动不传名称 → `…经营旅程 #2`；传名称 → 原样保留；详情行兜底派生与列表口径一致 |

---

*本登记为实施交付物，不改变 Owner 决议的决策权归属。*
