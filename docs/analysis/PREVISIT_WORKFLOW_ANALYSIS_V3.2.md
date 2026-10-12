# 访前工作流深度分析：V3.2 设计 vs 后端实际能力

> **文档版本**: 2026-08-29  
> **分析范围**: V3.2 设计文档 P12/P13/P14 页面 vs 当前后端 API/Skill 能力  
> **目的**: 诚实评估 V3.2 设计是否需要调整，以及如何正确实现  
> **审查状态**: 待专家评审

---

## 1. 问题陈述

V3.2 设计将访前路径拆分为三个页面：

| 页面 | 名称 | 核心功能 |
|------|------|---------|
| P12 | 访前目标与信息缺口 | 展示 KYC 缺口画像，明确"不知道什么" |
| P13 | 访前知识证据装配 | 展示知识证据的装配轨迹，明确"证据从哪来" |
| P14 | 访前包预览 | 预览完整访前包（外联脚本+会面脚本+访前报告+速战卡） |

**核心争议**：这三个页面是否可以独立触发？是否需要三个独立的后端 Skill/API 调用？还是同一份数据的三个前端视角？

---

## 2. 后端实际能力清单

### 2.1 已有 API 端点

| 端点 | 方法 | 说明 | 调用 Skill? | 可独立调用? |
|------|------|------|------------|-----------|
| `/api/v1/engagement/kyc/{customerId}/gap-profile` | GET | KYC 缺口画像查询 | 否（纯查询） | **可以** |
| `/api/v1/engagement/journey/{journeyId}/prepare-previsit` | POST | 一键访前准备 | **是（3 Skill 并行）** | 可以 |
| `/api/v1/engagement/supply-chain-graph` | POST | 供应链图谱 | 是（1 Skill） | 可以 |
| `/api/v1/engagement/supply-chain-graph/reports/{requestId}` | GET | 获取图谱报告 | 否（纯查询） | 可以 |
| `/api/v14/gates/assets/{customerId}` | GET | 闸门资产查询 | 否（纯查询） | 可以 |
| `/api/v14/gates/state/{customerId}` | GET | 闸门状态查询 | 否（纯查询） | 可以 |

### 2.2 一键访前 `prepare-previsit` 的 Skill 编排

```
POST /api/v1/engagement/journey/{journeyId}/prepare-previsit
    │
    ├── Skill 1: skill-customer-outreach-script  → 外联脚本
    ├── Skill 2: skill-customer-meeting-script   → 会面脚本
    └── Skill 3: skill-customer-previsit-report  → 访前报告（含速战卡）
```

**关键事实**：三个 Skill 由 `PrevisitPreparationService.prepare()` **并行调用**，结果合并为 `PreparedPrevisitResponse` 一次性返回。

### 2.3 `PreparedPrevisitResponse` 返回字段

```java
public record PreparedPrevisitResponse(
    String outreachScript,          // 外联脚本（Skill 1 产出）
    String meetingScript,           // 会面脚本（Skill 2 产出）
    String previsitReport,          // 访前报告正文（Skill 3 产出）
    String battleCard,              // 速战卡（Skill 3 产出）
    String supplyChainMarkdown,     // 供应链图谱摘要
    List<AssemblyTraceStep> assemblyTrace,  // 装配轨迹（Skill 3 产出）
    String skillReportTitle,        // 报告标题（Skill 3 产出）
    String skillExecutiveSummary,   // 执行摘要（Skill 3 产出）
    List<SkillSection> skillSections // 报告章节（Skill 3 产出）
) {}
```

### 2.4 `AssemblyTraceStep` 结构

```java
public record AssemblyTraceStep(
    String stepId,
    String knowledgeElementId,
    String knowledgeElementTitle,
    String source,        // 来源：CRM / 公示 / 年报 / ...
    String confidence,    // 置信度
    String usedFor        // 用途：外联 / 会面 / 报告
) {}
```

### 2.5 KYC 缺口画像 API

```
GET /api/v1/engagement/kyc/{customerId}/gap-profile
```

返回：
```typescript
interface KycGapProfile {
  profileId: string
  customerId: string
  asOf: string
  knownItems: string[]
  partialKnownItems: string[]
  staleItems: string[]
  conflictingOrAmbiguousItems: string[]
  unknownItems: string[]
  priorityQuestions: string[]
}
```

### 2.6 后端能力总结

| 能力 | 是否存在 | 备注 |
|------|---------|------|
| 独立查询 KYC 缺口 | **存在** | `GET /kyc/{id}/gap-profile`，纯查询，不调 Skill |
| 独立生成外联脚本 | **不存在** | 只有 `prepare-previsit` 内部调用，无独立端点 |
| 独立生成会面脚本 | **不存在** | 同上 |
| 独立生成访前报告 | **不存在** | 同上 |
| 独立查询装配轨迹 | **不存在** | `assemblyTrace` 是 `prepare-previsit` 返回值的一部分 |
| 一键访前（3 Skill 并行） | **存在** | `POST /journey/{id}/prepare-previsit` |

---

## 3. V3.2 设计文档逐页分析

### 3.1 P12：访前目标与信息缺口

**V3.2 设计意图**：
- 展示客户 KYC 缺口画像（已知/部分已知/过时/冲突/未知）
- 明确本次访前的信息获取目标
- 契约策略：`REUSE_EXISTING` — 仅消费既有查询、状态与对象契约；无支持能力时禁用或降级

**后端支撑**：
- ✅ `GET /kyc/{customerId}/gap-profile` — **完全匹配**
- 该 API 不调用任何 Skill，纯查询
- 旅程启动后即可独立查询，无需先执行一键访前

**结论**：**P12 可以独立实现，无需后端变更。**

---

### 3.2 P13：访前知识证据装配

**V3.2 设计意图**：
- 展示知识证据的装配轨迹（哪条知识来自哪个数据源、置信度如何、用于哪个产出物）
- 帮助 RM 理解"访前包的证据基础"，建立信任
- 契约策略：`DERIVED_READ_ONLY` — 前端编排既有对象与证据形成派生视图，不新增持久化契约

**后端支撑**：
- ❌ **没有独立的"证据装配"API 或 Skill**
- `assemblyTrace` 是 `prepare-previsit` 返回值的一个字段
- 只有执行了一键访前，才能拿到装配轨迹数据
- V3.2 契约策略明确说了 `DERIVED_READ_ONLY` — **这是前端对已有数据的派生展示，不需要后端新增能力**

**关键分析**：

V3.2 的 `DERIVED_READ_ONLY` 契约策略说明：P13 的设计者**已经知道**证据装配不是独立的后端操作，而是对 `prepare-previsit` 返回数据的派生视图。

**结论**：**P13 不需要后端变更。它是 `prepare-previsit` 返回的 `assemblyTrace` 的前端展示。**

---

### 3.3 P14：访前包预览

**V3.2 设计意图**：
- 预览完整访前包：外联脚本 + 会面脚本 + 访前报告 + 速战卡
- RM 确认后可下载或发送
- 契约策略：`REUSE_EXISTING` — 仅消费既有查询、状态与对象契约

**后端支撑**：
- ❌ **没有独立的"访前包生成"API 或 Skill**
- 访前包的所有组件都是 `prepare-previsit` 一次性返回的
- V3.2 契约策略 `REUSE_EXISTING` 说明：P14 只是消费已有的 `prepare-previsit` 结果

**结论**：**P14 不需要后端变更。它是 `prepare-previsit` 返回的完整结果的前端展示。**

---

## 4. 数据流分析

### 4.1 当前实现的数据流

```
用户点击"一键访前"按钮
    │
    ▼
POST /journey/{id}/prepare-previsit
    │
    ├── 并行调用 3 个 DKWS Skill
    │   ├── skill-customer-outreach-script  → outreachScript
    │   ├── skill-customer-meeting-script   → meetingScript
    │   └── skill-customer-previsit-report  → previsitReport + battleCard + assemblyTrace
    │
    ▼
返回 PreparedPrevisitResponse（一次性包含所有结果）
    │
    ▼
前端在同一页面展示所有结果
```

### 4.2 V3.2 设计期望的数据流

```
P12（缺口）                    P13（装配）                    P14（预览）
    │                              │                              │
    ▼                              ▼                              ▼
GET /kyc/{id}/gap-profile    assemblyTrace 展示            完整访前包展示
（纯查询，独立触发）         （来自 prepare-previsit）     （来自 prepare-previsit）
                                    │                              │
                                    └──────────┬───────────────────┘
                                               │
                                    同一次 prepare-previsit 调用
                                               │
                                    ┌──────────┴───────────────────┐
                                    │ 触发时机：用户在 P12 或       │
                                    │ P13 页面点击"执行访前准备"    │
                                    └──────────────────────────────┘
```

### 4.3 关键洞察

**P12/P13/P14 是同一流程的三个视角，不是三个独立操作**：

1. **P12（缺口）**：旅程启动后即可查看，调用 `fetchKycGapProfile`，**不需要调 Skill**
2. **一键访前按钮**：一个按钮，调用 `prepare-previsit`（3 Skill 并行），**唯一的 KERT 调用入口**
3. **P13（装配）**：一键访前完成后，展示 `assemblyTrace` 派生视图 — **只读展示，不触发新调用**
4. **P14（预览）**：一键访前完成后，展示完整访前包 — **只读展示，不触发新调用**

---

## 5. 之前实现中的错误

### 5.1 错误 1：把 3 个页面当成 3 个独立后端调用

之前的实现将 P12/P13/P14 设计为 3 个步骤卡片，暗示每个步骤可以独立触发：

```
Step 1: 缺口分析 → 点击触发 fetchKycGapProfile
Step 2: 证据装配 → 点击触发 ???（实际没有独立 API）
Step 3: 访前包   → 点击触发 ???（实际没有独立 API）
```

**问题**：Step 2 和 Step 3 的数据都来自同一个 `prepare-previsit` 调用，不存在独立的"证据装配"或"访前包生成"API。

### 5.2 错误 2：`handlePrevisit` 按钮位置不当

之前的实现将一键访前按钮放在 Step 1（缺口分析）中，但它实际触发的是完整的 3 Skill 并行调用，不是只做缺口分析。

### 5.3 错误 3：伪分步

之前的实现中，Step 2（证据装配）和 Step 3（访前包）实际上共享同一次 API 调用的结果，但 UI 暗示它们是分步触发的。这是**伪分步** — 给用户错误的操作心智模型。

---

## 6. V3.2 是否需要调整？

### 6.1 V3.2 设计本身的合理性

**V3.2 的页面拆分设计是合理的**，原因如下：

1. **信息架构清晰**：缺口 → 装配 → 预览，是符合认知逻辑的信息层次
2. **契约策略正确**：P12 `REUSE_EXISTING`、P13 `DERIVED_READ_ONLY`、P14 `REUSE_EXISTING`，都说明设计者知道这些页面不需要后端新增能力
3. **用户体验合理**：RM 可以先看缺口（不需要等待），再决定是否执行一键访前，然后查看装配轨迹和访前包

### 6.2 V3.2 需要调整的地方

**V3.2 不需要调整设计文档本身，但需要在实现时明确以下约束**：

| 约束 | 说明 |
|------|------|
| P12 可以独立查看 | 调用 `fetchKycGapProfile`，不依赖一键访前 |
| P13/P14 依赖一键访前 | 只有执行了 `prepare-previsit` 后才有数据展示 |
| 一键访前是单一操作 | 3 个 Skill 并行调用，不可拆分为分步触发 |
| P13/P14 是只读展示 | 不触发新的后端调用，只展示已有结果的不同视角 |

### 6.3 如果 V3.2 真正要求"每步可独立触发"

如果产品需求确实是"每步可独立触发"，则需要后端新增以下 API：

| 新增 API | 调用 Skill | 说明 |
|----------|-----------|------|
| `POST /journey/{id}/prepare-outreach` | `skill-customer-outreach-script` | 独立生成外联脚本 |
| `POST /journey/{id}/prepare-meeting` | `skill-customer-meeting-script` | 独立生成会面脚本 |
| `POST /journey/{id}/prepare-report` | `skill-customer-previsit-report` | 独立生成访前报告（含装配轨迹） |

**但这会引入以下问题**：

1. **破坏一键访前的原子性**：3 个 Skill 本应并行执行，拆分后可能产生数据不一致
2. **增加 DKWS 调用次数**：原本 1 次并行调用变成 3 次串行调用
3. **增加前端复杂度**：需要管理 3 个异步操作的状态和错误处理
4. **违反 V3.2 契约策略**：V3.2 的 `REUSE_EXISTING` 和 `DERIVED_READ_ONLY` 明确不需要后端新增能力

---

## 7. 正确的实现方案

### 7.1 方案 A：前端视角切分（推荐）

**核心思路**：P12/P13/P14 是同一流程的三个前端视角，后端不变。

```
┌─────────────────────────────────────────────────────────┐
│                    访前工作区                              │
├──────────┬──────────┬──────────┤
│ P12 缺口  │ P13 装配  │ P14 预览  │  ← Tab 切换
├──────────┼──────────┼──────────┤
│          │          │          │
│ KYC 缺口  │ 装配轨迹  │ 访前包    │
│ 画像展示   │ 展示     │ 完整预览   │
│          │          │          │
│ [一键访前] │ (只读)   │ (只读)    │
│          │          │          │
└──────────┴──────────┴──────────┘

数据流：
  P12: GET /kyc/{id}/gap-profile → 独立查询
  一键访前: POST /journey/{id}/prepare-previsit → 3 Skill 并行
  P13: 展示 prepare-previsit 返回的 assemblyTrace
  P14: 展示 prepare-previsit 返回的完整结果
```

**实现细节**：

1. **P12（缺口）**：
   - 旅程启动后自动加载 `fetchKycGapProfile`
   - 展示缺口画像（已知/部分已知/过时/冲突/未知）
   - 底部放置"执行访前准备"按钮

2. **一键访前按钮**：
   - 点击后调用 `preparePrevisit(journeyId, customerId, ...)`
   - 同时并行调用 `executeSupplyChainGraph(customerId)`
   - 加载状态覆盖整个 Tab 区域

3. **P13（装配）**：
   - 一键访前未执行时：显示空状态提示"请先执行访前准备"
   - 一键访前完成后：展示 `assemblyTrace` 表格
   - 每行展示：知识元素 ID / 标题 / 来源 / 置信度 / 用途

4. **P14（预览）**：
   - 一键访前未执行时：显示空状态提示"请先执行访前准备"
   - 一键访前完成后：展示完整访前包
   - 分区展示：外联脚本 / 会面脚本 / 访前报告 / 速战卡 / 供应链图谱

**优点**：
- 后端零变更
- 符合 V3.2 契约策略
- 用户体验清晰（缺口 → 触发 → 装配 → 预览）
- 不会产生伪分步的误导

**缺点**：
- P13/P14 必须等待一键访前完成才能查看
- 无法"只看装配轨迹不看访前报告"（因为它们来自同一次调用）

### 7.2 方案 B：后端拆分 Skill 调用（不推荐）

**核心思路**：后端新增 3 个独立 API，分别调用 3 个 Skill。

**优点**：
- 每个页面可以独立触发
- 更灵活的操作粒度

**缺点**：
- 需要修改 OpenAPI 合同 → `make generate` → `make check`
- 需要新增 Controller + Service 方法
- 破坏一键访前的原子性
- 增加 DKWS 调用次数
- 违反 V3.2 契约策略（`REUSE_EXISTING` / `DERIVED_READ_ONLY`）
- 增加前端复杂度

### 7.3 方案 C：后端保持一键，增加结果缓存查询（折中）

**核心思路**：后端保持一键访前的原子性，但增加一个查询 API 获取已执行的结果。

```
POST /journey/{id}/prepare-previsit  → 执行一键访前，返回结果
GET  /journey/{id}/previsit-result   → 查询最近一次访前结果（不触发 Skill）
```

**优点**：
- 一键访前保持原子性
- P13/P14 可以独立查询已有结果（页面刷新后不丢失）
- 不需要重新调用 Skill

**缺点**：
- 需要新增 1 个查询 API
- 需要持久化访前结果（目前是内存态）
- 需要修改 OpenAPI 合同

---

## 8. 推荐方案与理由

### 推荐：方案 A（前端视角切分）

**理由**：

1. **V3.2 契约策略已明确**：P12 `REUSE_EXISTING`、P13 `DERIVED_READ_ONLY`、P14 `REUSE_EXISTING`，设计者已经知道不需要后端新增能力
2. **后端零变更**：不需要修改合同、不需要新增 API、不需要新增 Skill
3. **用户体验合理**：RM 先看缺口 → 决定是否执行访前 → 查看装配和预览，这是自然的操作流程
4. **实现简单**：只需要前端调整 Tab/步骤的展示逻辑
5. **不破坏原子性**：3 个 Skill 并行调用的一致性得到保障

### 方案 A 的实现路径

1. **P12 页面**：
   - 旅程启动后自动 `fetchKycGapProfile`
   - 展示缺口画像
   - 放置"执行访前准备"按钮（调用 `preparePrevisit`）

2. **P13 页面**：
   - 检查 `previsitResult` 是否存在
   - 不存在：显示空状态 + 引导按钮"请先执行访前准备"
   - 存在：展示 `assemblyTrace` 表格

3. **P14 页面**：
   - 检查 `previsitResult` 是否存在
   - 不存在：显示空状态 + 引导按钮
   - 存在：展示完整访前包

4. **状态管理**：
   - `previsitResult` 存储在 Pinia store 或组件状态中
   - 一键访前完成后，P13/P14 自动更新

---

## 9. 当前前端实现的问题清单

### 9.1 EngagementWorkspace.vue

当前 `handlePrevisit` 函数（第 495-529 行）：

```typescript
async function handlePrevisit() {
  // ...
  dkwsCallHint.value='一键访前：GITS 正在并行 POST DKWS /api/skill/execute（外联、会面、R1 访前报告、供应链图谱）'
  // 并行调用 preparePrevisit + executeSupplyChainGraph
  const graphJob = executeSupplyChainGraph(sc.value.customerId)
  const r = await preparePrevisit(jid.value, sc.value.customerId, ...)
  // 结果存储在组件 ref 中
  outR.value = r.outreachScript || null
  meetR.value = r.meetingScript || null
  preR.value = { ... } as PrevisitExecutionResponse
}
```

**问题**：
1. ❌ 所有结果存储在组件级 `ref`，页面刷新后丢失
2. ❌ 没有 P12/P13/P14 的 Tab 切换
3. ❌ 缺口画像（`fetchKycGapProfile`）没有在访前流程中展示
4. ❌ 装配轨迹（`assemblyTrace`）没有独立展示区域

### 9.2 PrevisitGapsView.vue / PrevisitEvidenceView.vue / PrevisitPackView.vue

这三个视图文件已存在，但需要确认：
1. 是否正确处理了"一键访前未执行"的空状态
2. 是否正确从 `previsitResult` 中读取数据
3. 是否避免了独立调用不存在的后端 API

---

## 10. 对 V3.2 设计文档的评审意见

### 10.1 设计合理的部分

1. **页面拆分逻辑**：缺口 → 装配 → 预览，信息层次清晰
2. **契约策略**：`REUSE_EXISTING` / `DERIVED_READ_ONLY` 准确反映了后端能力边界
3. **渐进式展示**：RM 可以先看缺口（快速），再决定是否执行一键访前（耗时）

### 10.2 需要明确的部分

1. **一键访前按钮的位置**：V3.2 没有明确说明"执行访前准备"按钮应该放在哪个页面。建议放在 P12（缺口）页面，因为缺口信息是触发访前准备的决策依据。

2. **P13/P14 的空状态处理**：V3.2 没有明确说明一键访前未执行时 P13/P14 应该显示什么。建议显示空状态 + 引导按钮。

3. **装配轨迹的数据来源**：V3.2 没有明确说明 `assemblyTrace` 来自哪个 API。实际上它来自 `prepare-previsit` 的返回值，不是独立的查询。

### 10.3 不需要调整的部分

1. **页面结构**：P12/P13/P14 的拆分不需要调整
2. **契约策略**：`REUSE_EXISTING` / `DERIVED_READ_ONLY` 不需要调整
3. **后端 API**：不需要新增 API 或 Skill

---

## 11. 风险评估

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| 用户期望 P13/P14 可独立触发 | 中 | 中 | 在 UI 上明确标注"需先执行访前准备" |
| 一键访前执行时间过长 | 高 | 高 | 优化 Skill 执行效率，增加进度提示 |
| 页面刷新后访前结果丢失 | 高 | 中 | 方案 C（增加结果缓存查询 API） |
| 装配轨迹数据不够丰富 | 低 | 低 | 后续迭代增强 Skill 输出 |

---

## 12. 结论

### 核心结论

1. **V3.2 的页面拆分设计是合理的**，不需要调整设计文档
2. **后端不需要新增 API 或 Skill**，V3.2 的契约策略已正确反映了后端能力边界
3. **P12 可以独立查看**（调用 `fetchKycGapProfile`），**P13/P14 依赖一键访前的结果**
4. **一键访前是唯一的 KERT 调用入口**，3 个 Skill 并行执行，不可拆分
5. **P13/P14 是前端对同一份数据的不同视角展示**，不是独立的后端操作

### 实现建议

1. 采用**方案 A（前端视角切分）**
2. 一键访前按钮放在 P12 页面
3. P13/P14 检查 `previsitResult` 是否存在，不存在则显示空状态
4. 后续如需持久化访前结果，再考虑方案 C

---

## 附录 A：后端 Skill 调用链详解

### A.1 PrevisitPreparationService.prepare()

```
PrevisitPreparationService.prepare(journeyId, customerId, operatingCaseId, roundLabel, rmId)
    │
    ├── outreachScriptService.generateScript(customerId, rmId, roundLabel)
    │   └── skillExecutionPort.execute(
    │         skillId = "skill-customer-outreach-script",
    │         systemPrompt = ...,
    │         userPrompt = ...
    │       )
    │   └── 返回 outreachScript: String
    │
    ├── meetingScriptService.generateScript(customerId, rmId, roundLabel)
    │   └── skillExecutionPort.execute(
    │         skillId = "skill-customer-meeting-script",
    │         systemPrompt = ...,
    │         userPrompt = ...
    │       )
    │   └── 返回 meetingScript: String
    │
    └── reportGenerator.generate(customerId, rmId, roundLabel)
        └── skillExecutionPort.execute(
              skillId = "skill-customer-previsit-report",
              systemPrompt = ...,
              userPrompt = ...
            )
        └── 返回 PrevisitReportResult(
              previsitReport, battleCard, assemblyTrace,
              skillReportTitle, skillExecutiveSummary, skillSections
            )
    │
    ▼
    合并为 PreparedPrevisitResponse 一次性返回
```

### A.2 SkillExecutionPort 接口

```java
public interface SkillExecutionPort {
    SkillExecutionResult execute(String skillId, String systemPrompt, String userPrompt);
}
```

### A.3 DshHttpSkillExecutionAdapter（DKWS HTTP 调用）

```
POST {dkwsBaseUrl}/api/skill/execute
Headers: X-API-KEY: {dkwsApiKey}
Body: {
    "skillId": "skill-customer-outreach-script",
    "systemPrompt": "...",
    "userPrompt": "..."
}
```

返回：`SkillExecutionResult`（含 `output` 字段和 `jobId`）

### A.4 异步轮询机制

DKWS Skill 执行可能是异步的，`DshJobPoller` 负责轮询：

```
GET {dkwsBaseUrl}/api/skill/jobs/{jobId}
→ PENDING / RUNNING / COMPLETED / FAILED
```

---

## 附录 B：前端 API 类型定义

### B.1 PreparedPrevisitResponse

```typescript
export interface PreparedPrevisitResponse {
  outreachScript: string
  meetingScript: string
  previsitReport: string
  battleCard: string
  supplyChainMarkdown: string
  assemblyTrace: AssemblyTraceStep[]
  skillReportTitle: string
  skillExecutiveSummary: string
  skillSections: SkillSection[]
}
```

### B.2 AssemblyTraceStep

```typescript
export interface AssemblyTraceStep {
  stepId: string
  knowledgeElementId: string
  knowledgeElementTitle: string
  source: string
  confidence: string
  usedFor: string
}
```

### B.3 KycGapProfile

```typescript
export interface KycGapProfile {
  profileId: string
  customerId: string
  asOf: string
  knownItems: string[]
  partialKnownItems: string[]
  staleItems: string[]
  conflictingOrAmbiguousItems: string[]
  unknownItems: string[]
  priorityQuestions: string[]
}
```

---

## 附录 C：V3.2 契约策略定义

| 策略 | 含义 | 适用页面 |
|------|------|---------|
| `REUSE_EXISTING` | 仅消费既有查询、状态与对象契约；无支持能力时禁用或降级 | P12, P14 |
| `DERIVED_READ_ONLY` | 前端编排既有对象与证据形成派生视图，不新增持久化契约 | P13 |
| `NEW_CONTRACT` | 需要后端新增 API 或 Skill | **无**（V3.2 访前路径不需要） |

---

---

## 附录 D：源码核验报告（2026-08-29）

### D.1 外部审计声明核验

> **审计声明**："GitHub 当前 feature/P30-gits-bank-experience-shell 只实现了 P12–P14 的 C0/C2 降级壳层。P13 在页面加载时调用未登记于 OpenAPI 的 prepare-previsit，P14 又调用 executePrevisit，存在重复生成和刷新丢状态；而 CodeBuddy 文档声称的 DshHttpSkillExecutionAdapter、DshJobPoller、3 个 skill-customer-* Skill、扩展 assemblyTrace 响应字段，在该 GitHub 提交中都不存在。"

### D.2 逐条核验结果

| # | 审计声明 | 核验结果 | 详情 |
|---|---------|---------|------|
| 1 | "只实现了 P12-P14 的 C0/C2 降级壳层" | **部分正确** | P12 是 C0 壳层（纯查询 `fetchKycGapProfile`），P13/P14 确实是 C2 降级壳层（调用了后端 API 但展示简陋） |
| 2 | "P13 在页面加载时调用未登记于 OpenAPI 的 prepare-previsit" | **错误** | `prepare-previsit` 已登记在 OpenAPI（`/engagement/journey/{journeyId}/prepare-previsit`），但 P13 在 `onMounted` 时自动调用它确实是问题 — 这意味着每次进入 P13 页面都会触发 3 个 Skill 并行执行 |
| 3 | "P14 又调用 executePrevisit" | **正确** | `PrevisitPackView.vue` 第 53 行调用 `executePrevisit()`，这是另一个后端端点（`/engagement/journey/{journeyId}/previsit`），与 P13 调用的 `preparePrevisit` 不同 |
| 4 | "存在重复生成" | **正确且严重** | P13 调 `preparePrevisit`（3 Skill 并行），P14 调 `executePrevisit`（也是 3 Skill 并行），两者功能高度重叠，造成 DKWS 重复调用 |
| 5 | "刷新丢状态" | **正确** | P13/P14 的结果存在组件级 `ref` 中（`prepared.value` / `pack.value`），页面刷新即丢失 |
| 6 | "DshHttpSkillExecutionAdapter 不存在于 GitHub 提交" | **语境正确** | 该文件在磁盘上存在且已 `git add`（staged），但尚未 `git commit`，所以 `git show HEAD:` 找不到 |
| 7 | "DshJobPoller 不存在" | 同上 | staged 但未 commit |
| 8 | "3 个 skill-customer-* Skill 不存在" | **语境正确** | Skill ID 字符串存在于代码中（`skill-customer-outreach-script` / `skill-customer-meeting-script` / `skill-customer-previsit-report`），但 DKWS 端是否实际部署了这些 Skill 是运行时问题，不在 git 提交范围 |
| 9 | "扩展 assemblyTrace 响应字段不存在" | **语境正确** | `AssemblyTraceStep.java` 和 `PreparedPrevisitResponse` 的扩展字段已 staged 但未 commit |

### D.3 核心问题确认

**问题 1：P13 在 `onMounted` 自动调用 `preparePrevisit`**

```typescript
// PrevisitEvidenceView.vue 第 102 行
onMounted(loadEvidence)  // 每次进入页面自动触发 3 Skill 并行调用
```

这意味着：
- 用户每次导航到 P13 页面，都会触发一次完整的 DKWS 调用
- 如果用户在 P12 → P13 → P14 之间来回切换，会产生多次重复调用
- DKWS 调用是昂贵的（LLM 推理），不应在页面加载时自动触发

**问题 2：P14 调用 `executePrevisit` 而非复用 P13 的结果**

```typescript
// PrevisitPackView.vue 第 53 行
pack.value = await executePrevisit(journeyId.value, customerId.value, operatingCaseId.value, '访前包预览')
```

`executePrevisit` 和 `preparePrevisit` 是两个不同的后端端点：
- `preparePrevisit` → `POST /journey/{id}/prepare-previsit` → 3 Skill 并行 → 返回 `PreparedPrevisitResponse`
- `executePrevisit` → `POST /journey/{id}/previsit` → 3 Skill 并行 → 返回 `PrevisitExecutionResponse`

两者功能高度重叠，但 P14 没有复用 P13 的结果，而是重新调用了一个不同的端点。

**问题 3：刷新丢状态**

P13 和 P14 的结果都存储在组件级 `ref` 中，页面刷新后丢失。没有使用 Pinia store 或 URL 参数持久化。

### D.4 正确的实现方向

1. **P13 不应在 `onMounted` 自动调用 `preparePrevisit`** — 应改为用户手动触发或从 P12 导航时传入
2. **P14 不应调用 `executePrevisit`** — 应复用 `preparePrevisit` 的结果（同一份数据的不同视角）
3. **一键访前的结果应存储在共享状态中** — 使用 Pinia store，P13/P14 都从同一份 store 数据读取
4. **一键访前按钮应在 P12 页面** — 缺口信息是触发访前准备的决策依据

---

*文档结束。欢迎专家评审，特别是以下方面的意见：*
1. *方案 A 的前端视角切分是否足够？是否需要方案 C 的结果缓存？*
2. *一键访前按钮放在 P12 是否合理？还是应该放在独立的操作区？*
3. *P13/P14 的空状态处理是否符合用户预期？*
4. *是否需要考虑访前结果的持久化（页面刷新后恢复）？*
5. *P13 自动调用 `preparePrevisit` vs 用户手动触发，哪种更合理？*
6. *`executePrevisit` 和 `preparePrevisit` 两个端点是否应该合并？*
