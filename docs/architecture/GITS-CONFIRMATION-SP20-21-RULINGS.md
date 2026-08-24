# GITS 端正式确认：DKWS 架构师 SP-20/SP-21 八项裁定

> 确认人：GITS Tech Lead ｜ 日期：2026-08-23
> 确认对象：`docs/architecture/DKWS-ARCH-REVIEW-SP20-21.md` §2 八项裁定
> 立场：**知识在 DKWS，业务在 GITS**（确认 v1.3 数据所有权原则延续）

---

## 总体立场

**全部 8 项裁定确认接受。** DKWS 架构师的核心判断——"把闸门/记忆/版本三类业务状态划给 DKWS 与平台定位冲突"——完全正确。GITS 原始设计（§13 决策项 4/5）确实越界，裁定纠正了架构风险。

职责边界总表（DKWS §1.1）GITS 无异议，逐条确认如下：

| 能力 | 归属 | GITS 确认 |
|---|---|---|
| 行业/财务/模板/规则知识资产 | DKWS | ✅ 知识资产归知识平台 |
| SP-20 逐章生成 + 事实标签 + 引用索引 | DKWS | ✅ 技能/生成是 DKWS 职责 |
| 6 条 BLOCKING 规则校验 | DKWS（RULE 资产 + evaluate_rule） | ✅ 规则是知识 |
| 内部版/对客版过滤执行 | DKWS（确定性过滤引擎） | ✅ 标签同源才能自洽 |
| 对客版发布权 | **GITS（闸门）** | ✅ 审批权在业务端 |
| 闸门状态机 G0-G5 | **GITS** | ✅ 业务编排+人工审批 |
| 交互记忆抽取（SP-21） | DKWS | ✅ 抽取=知识化 |
| 交互记忆存储与生命周期 | **GITS** | ✅ 操作性状态，非知识资产 |
| 建议书业务版本 | **GITS + DKWS 双轨** | ✅ 业务版本 GITS 记录，知识快照 DKWS 不可变 |
| ContextPackage 组装 | **GITS** | ✅ 业务上下文组装在业务端 |

---

## 逐项裁定确认

### D1：五层映射 —— ✅ 确认采纳但改造

GITS 原方案 `01_raw/{customerId}/proposal/...` 按客户建业务目录确实与 DKWS 域/版本模型冲突。DKWS 裁定方案（建议书按"知识资产"落库，保持域/版本/run_id 模型）更合理。

**GITS 适配动作**：
- `DkwsProposalAdapter`（实现 ProposalPort）不再假设 DKWS 按客户目录存储，改为通过 `requestId` / `runId` / `release_version` 引用 DKWS 产出
- GITS 侧 `ProposalVersion` 记录中保存 `dkwsRunId` 和 `dkwsReleaseVersion` 作为关联键
- 业务版本号（v1.0/v1.1/v2.0）由 GITS 编号，DKWS `release_version` 由 DKWS 编号，两者通过引用索引关联

### D2：HTTP API —— ✅ 确认复用 /api/skill/execute v1.4 + 异步作业

不新增 `/skills/execute` 端点，复用并扩展现有契约。异步模式（`request.async=true` → 202 + jobId 轮询）是解决 8 次 LLM 调用超时的正确方案。

**GITS 适配动作**：
- `DkwsProposalAdapter` 实现 `ProposalPort.generateDraft()` 时：
  - 组装 `ContextPackage`，调用 `POST /api/skill/execute {skillId: "SP-20", request: {context, async: true}}`
  - 收到 `202 {jobId}` 后启动轮询（复用 `/v1/jobs/{jobId}`，间隔 3s，超时 180s）
  - 轮询完成后解析 `data.result`（ProposalServiceResult）和 `data.ruleViolations`
- `SkillExecutionPort`（已有）签名不变，新增 `async` 参数支持
- GITS 侧 HTTP 客户端超时设为 ≥ 120s（同步场景兜底）

### D3：双版本 —— ✅ 确认 DKWS 确定性过滤 + GITS 保留发布权

DKWS 生成内部版 + 确定性过滤出对客版（无 LLM、可审计、filtering-report），GITS 通过 `releaseBlockedUntil` 控制放行时机。这是最安全的方案——过滤逻辑就近标签源可复现，放行权在业务端可审计。

**GITS 适配动作**：
- `ProposalVersion` record 新增字段：
  - `customerVersionAvailable: boolean` — 对客版是否已生成（DKWS 已过滤）
  - `releaseBlockedUntil: List<String>` — 放行闸门列表（G1/G2/G3）
- `ProposalPort.generateCustomerVersion()` 逻辑调整：
  - 不再调用 DKWS 生成对客版（DKWS 已在 SP-20 输出中包含 `data.content.customerVersion`）
  - 改为检查 `releaseBlockedUntil` 是否全部通过，通过后标记 `customerVersionReleased: true`
- 前端"导出对客版"按钮：仅在 `customerVersionReleased=true` 时可用

### D4：交互记忆存储 —— ✅ 确认放 GITS，DKWS 只做抽取

记忆有生命周期（CANDIDATE→CONFIRMED→EXPIRED/SUPERSEDED）+ 置信度衰减，是操作性业务状态，放 DKWS 03_core 会污染"不可变知识资产"语义。DKWS 只做 SP-21 抽取，输出结构化候选 + 比对建议。

**GITS 适配动作**：
- `InteractionMemoryPort` 接口保留在 `modules/operational-ontology/port/`
- 新增 `InteractionMemory` 实体（H2 存储）：
  - `id`, `customerId`, `category`（PREFERENCE/DECISION_PATTERN/RELATIONSHIP/BUSINESS_SIGNAL/EMOTIONAL_STATE）
  - `content`, `sourceInteractionId`, `confidence`, `decayRule`（NONE/LINEAR/STEP）
  - `status`（CANDIDATE/CONFIRMED/EXPIRED/SUPERSEDED）, `supersededBy`
  - `createdAt`, `confirmedAt`, `expiresAt`
- `DkwsInteractionMemoryAdapter`（实现 InteractionMemoryPort）：
  - `extractCandidates()` → 调用 DKWS SP-21（`POST /api/skill/execute {skillId: "SP-21"}`）
  - `confirmCandidate()` → GITS 本地持久化，不回调 DKWS
  - `getEffectiveMemories()` → GITS 本地查询（CONFIRMED + 未过期 + 按置信度排序）
- ContextPackage 组装时从 GITS 本地读取交互记忆，传入 DKWS

### D5：闸门状态机 —— ✅ 确认 GITS 唯一权威

DKWS 90_control 的 G0-G5 是平台知识资产门禁，与业务 G0-G5 同名异义，必须区分。GITS 是业务闸门唯一权威；DKWS 提供 checklist 知识与就绪度建议（`gateRecommendations`）。

**GITS 适配动作**：
- 闸门命名空间分离：
  - GITS 内部：`GATE-BIZ-G0` ~ `GATE-BIZ-G5`（业务闸门）
  - DKWS 平台：`GATE-PLATFORM-*`（平台门禁，GITS 不操作）
- `ProposalPort.advanceGate()` 逻辑：
  - 检查当前闸门状态（GITS 本地）
  - 可选：读取 DKWS `gateRecommendations` 作为就绪度参考（不阻塞）
  - 人工确认后推进闸门
  - 可选：镜像闸门决策到 DKWS 审计端点（DKWS 可选暴露）
- 前端闸门进度条显示 `GATE-BIZ-*`，与 DKWS 平台门禁无关

### D6：行业粒度 —— ✅ 确认 ~15 类银行常用行业 + OTHER

一级 20 类太粗、二级 97 类太细，银行对公常用约 15 类是务实选择。

**GITS 适配动作**：
- `ContextPackage.industry` 字段格式：`"<一级>-<二级>"` 字符串
- GITS 侧维护行业分类映射表（`INDUSTRY_CLASSIFICATION_MAP`），将客户行业映射到 DKWS 的 ~15 类
- 未命中 → `OTHER`，记入日志供后续补充

### D7：分章生成策略 —— ✅ 确认逐章 + 并行 2-3 路 + 章节级结构化 JSON

逐章生成可控可重试，并行 2-3 路控制总耗时，章节级结构化 JSON（claims/labels/citations/unknowns）使 GITS 可按断言渲染卡片。

**GITS 适配动作**：
- `ProposalDraft` record 调整：
  - `chapters: List<ProposalChapter>`（每章含 `markdown`, `claims[]`, `factLabels[]`, `citations[]`, `unknowns[]`）
  - 前端按章节渲染，每条断言可点击查看标签和引用
- 异步轮询时，章节可逐步返回（DKWS 逐章完成可推送进度，或 GITS 轮询时读取已完成章节）
- 前端建议书预览组件：章节目录 + 卡片式断言展示

### D8：ContextPackage 大小 —— ✅ 确认 50KB 上限 + DKWS 侧相关性裁剪

50KB 合理，DKWS 侧裁剪策略（行业框架按章节注入、记忆 Top-N、财务摘要近 3 年）正确。裁剪在 `limitations` 中显式声明。

**GITS 适配动作**：
- GITS 组装 ContextPackage 时：
  - 交互记忆按置信度/时效 Top-N（≤20 条）
  - 财务摘要只取最近 3 年 + 关键比率
  - 交互历史只传最近 5 次纪要摘要
- 超过 50KB 时 GITS 侧先裁剪，再传 DKWS（DKWS 可二次裁剪）
- 前端展示 `limitations` 列表，让客户经理知晓裁剪范围

---

## GITS 侧合同变更清单（基于裁定调整）

以下合同需注册到 `specs/CONTRACT_INDEX.yaml`，与原始设计（§11）对比标注变更：

| 合同ID | 类型 | 说明 | 与原设计差异 |
|--------|------|------|-------------|
| CTR-PROPOSAL-001 | json_schema | ProposalPort 接口合同 | **调整**：`generateCustomerVersion()` 不再调 DKWS，改为本地放行控制 |
| CTR-INTERACTION-MEMORY-001 | json_schema | InteractionMemoryPort 接口合同 | **调整**：存储在 GITS H2，非 DKWS 03_core |
| CTR-PROPOSAL-V1-4 | json_schema | DKWS execute v1.4 契约扩展 | **新增**：context/async/ruleViolations/ServiceResult |
| SP-20 | Skill | 对公客户服务建议书生成 | **调整**：implementationType=HYBRID（非 RULE_MODEL） |
| SP-21 | Skill | 交互记忆抽取 | 不变 |
| AC-SERVICE-PROPOSAL-001 | ActivationContract | 首次建议书生成 | 不变 |
| AC-SERVICE-PROPOSAL-002 | ActivationContract | 基于交互记忆的建议书更新 | 不变 |
| AC-ONGOING-ENGAGEMENT-001 | ActivationContract | 持续经营交互记忆积累 | 不变 |
| KM-CORP-RM-SERVICE-PROPOSAL | KnowledgeMap | 服务建议书任务地图 | 不变 |
| ASSET-KNOW-INDUSTRY-ANALYSIS | Asset | 行业分析框架（~15 类） | **调整**：粒度从 20/97 类改为 ~15 类 + OTHER |
| ASSET-KNOW-FINANCIAL-ANALYSIS | Asset | 财务分析框架 | 不变 |
| ASSET-KNOW-PROPOSAL-TEMPLATE | Asset | 建议书模板 | 不变 |

---

## GITS 侧实施路径（对齐 DKWS Phase 1-3）

### Phase 1（P24 Loop）—— 对齐 DKWS SP-20 骨架

| # | GITS 工作项 | 依赖 DKWS |
|---|------------|-----------|
| 1 | `ProposalPort` 接口 + `DkwsProposalAdapter`（async execute v1.4） | DKWS v1.4 契约 |
| 2 | `ProposalCommand` / `ProposalDraft` / `ProposalVersion` record 定义 | — |
| 3 | `ProposalController`（OpenAPI 先行） | — |
| 4 | `InteractionMemory` 实体 + H2 迁移脚本 | — |
| 5 | `InteractionMemoryPort` 接口 + `DkwsInteractionMemoryAdapter`（SP-21 调用） | DKWS SP-21（Phase 3） |
| 6 | 前端建议书 Tab 骨架（版本列表 + 预览 + 闸门进度条） | — |
| 7 | 合同注册（CTR-PROPOSAL-001 等）到 CONTRACT_INDEX.yaml | — |

### Phase 2（P25 Loop）—— 双版本 + 闸门协作

| # | GITS 工作项 | 依赖 DKWS |
|---|------------|-----------|
| 8 | 对客版放行逻辑（`releaseBlockedUntil` + 闸门推进） | DKWS 确定性过滤引擎 |
| 9 | 闸门状态机（GATE-BIZ-G0~G5 + 顺序推进 + 跳门禁止） | DKWS gateRecommendations |
| 10 | 前端交互记忆面板（候选确认 + 类别筛选 + 置信度指示） | — |
| 11 | GITS→DKWS 完整调用链路联调 | DKWS Phase 2 完成 |

### Phase 3（P26 Loop）—— 记忆与阶段演进

| # | GITS 工作项 | 依赖 DKWS |
|---|------------|-----------|
| 12 | 置信度衰减引擎（LINEAR/STEP 计算 + 定时刷新） | — |
| 13 | `EngagementPhase` 阶段演进（PROSPECTING→RETENTION 转换规则） | — |
| 14 | 动态 routeMode 切换（ONTOLOGY_THEN_MAP ↔ MAP_FIRST） | DKWS AC-SERVICE-PROPOSAL-002 |
| 15 | E2E 闭环验证 | DKWS Phase 3 完成 |

---

## 待 DKWS 端交付的接口契约（GITS 依赖项）

为启动 Phase 1 开发，GITS 需要 DKWS 先交付以下契约定义：

| # | 契约 | 用途 | 优先级 |
|---|------|------|--------|
| 1 | `POST /api/skill/execute` v1.4 请求/响应 Schema | DkwsProposalAdapter 实现 | P0 |
| 2 | `ProposalServiceResult` JSON Schema | 解析 SP-20 返回结果 | P0 |
| 3 | `/v1/jobs/{jobId}` 轮询响应格式 | 异步作业轮询 | P0 |
| 4 | `AC-SERVICE-PROPOSAL-001` 激活合同 JSON | 理解 SP-20 资产依赖 | P0 |
| 5 | `gateRecommendations` 结构定义 | 闸门就绪度展示（Phase 2） | P1 |
| 6 | `filtering-report.json` 结构定义 | 对客版过滤审计（Phase 2） | P1 |
| 7 | SP-21 输入/输出 Schema | DkwsInteractionMemoryAdapter（Phase 3） | P2 |

> **GITS 可以在 DKWS 交付 v1.4 契约前先行开发**：用 `MockDkwsProposalAdapter`（返回固定 ServiceResult）完成 Port 接口 + Controller + 前端骨架，待 DKWS Phase 1 完成后切换到真实 Adapter。

---

## 一句话总结

GITS 确认全部 8 项裁定，核心原则"知识在 DKWS、业务在 GITS"无争议；GITS 侧最大调整是交互记忆存储归 GITS H2（非 DKWS 03_core）和闸门命名空间分离（GATE-BIZ-* vs GATE-PLATFORM-*）；Phase 1 可立即启动，用 Mock Adapter 先行开发，等 DKWS v1.4 契约交付后联调切换。
