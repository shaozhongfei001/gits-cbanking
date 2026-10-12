# GITS-KERT 整改 AR-R2 · 修复核心设计覆盖（F06 分析语义优先）V1.0

> 角色：GK-KE 交付 Tech Lead
> 日期：2026-09-11
> 对应报告发现项：F06（MAJOR，最高优先级）、F03/F04/F05/F07（后续）
> 工作单：AR-R2 — 依次核对权威矩阵、注册/地图、构建发布、分析语义、RAG/图适配与动作恢复
> 本轮范围：**优先 F06 分析语义服务覆盖**（业务正确性风险最高）

---

## 1. F06 覆盖现状核查（区分"设计已有 / Schema 落地 / 数据验证 / 服务实现"）

### 1.1 F06 六类合同对象的四层覆盖状态

| F06 要求对象 | 设计层（C04 正文） | Schema 层 | 数据层 | 服务层 | 综合判定 |
|---|---|---|---|---|---|
| MetricDefinition 完整字段 | ✅ C04 §2 有完整字段表 | ⚠️ SIM-only 瘦剖面 | ✅ 正例 1 个 | ❌ NOT_PERFORMED | **部分覆盖，Schema 缺字段** |
| 指标批准责任（Owner/approvalRef） | ✅ | ✅ ownerSystem/ownerRole/approvalRef | ✅ | ❌ | 覆盖 |
| 受控 QueryPlan（白名单/服务端注入） | ✅ C04 §6 | ✅ query_registry | ✅ query_registry.json + avg_deposit.sql | ❌ | **覆盖良好** |
| 账户日粒度唯一性 | ✅ C04 §4 | ✅ baseGrain | ✅ 720 记录 0 重复 | ❌ | 覆盖 |
| 跨币种政策 | ✅ C04 §3 | ⚠️ 仅 CNY_ONLY 枚举 | ✅ C002 有 USD 账户 | ❌ | **数据有，负例预期缺** |
| 快照复算 | ✅ C04 §5 | ✅ snapshotId 字段 | ✅ snapshotId 贯穿 | ❌ | 覆盖 |
| 授权执行清单 | ✅ C04 §6 | ✅ permissionDecisionRef | ⚠️ 无授权负例数据 | ❌ | 部分 |

### 1.2 关键正面证据（已在 AR-R1 验证，此处引用）

| 验证 | 结果 |
|---|---|
| C001 日均复算 | **2,983,333.33 CNY 精确命中**（30 天总和 89,500,000） |
| 账户日主键唯一性 | 720 记录，`(accountId, businessDate)` 0 重复 |
| 跨币种数据存在 | C002 = SIM-A0021(CNY) + SIM-A0022(USD)，用于 T15 负例 |
| 受控查询模板 | `avg_deposit.sql` 用 `:authorizedOrgId` 服务端注入，prechecks 前置 |
| 三值判定 | oracle `drawableAmount=null` + `eligibility=UNKNOWN` |

---

## 2. F06 覆盖缺口（本轮需补的设计）

### 缺口 G1｜BLOCKER-级｜MetricDefinition Schema 是 SIM-only 瘦剖面，未落地 C04 完整字段

**现状**：`schemas/MetricDefinition.schema.json` 把 C04 §2 的字段组大幅收窄为 SIM 单值枚举：

| C04 §2 要求的字段组 | Schema 现状 |
|---|---|
| 分子分母 numerator/denominator 或 expressionRef | ❌ 缺失（仅有 `formula` 字符串） |
| distinctKey / dedupPolicy | ❌ 缺失 |
| fxPolicy / fxSource / fxDateRule | ❌ 缺失（currencyPolicy 仅 `CNY_ONLY`） |
| lateArrivalPolicy / accountLifecyclePolicy | ❌ 缺失 |
| allowedJoinPaths / joinCardinality | ❌ 缺失 |
| population / entityType | ❌ 缺失 |
| sourceProductRef / sourceSnapshotPolicy | ❌ 缺失（仅 mappingVersion） |
| completenessRule / qualityChecks | ❌ 缺失 |
| parameterSchemaRef / resultSchemaRef / permissionRef / costBudget | ❌ 缺失 |

**性质**：Schema 是"最小交换剖面"（README 已声明"正式合同正文比最小交换 Schema 覆盖面更广"），但 F06 明确要求"MetricDefinition 字段必须逐项提供证据"。设计层（C04 §2）有字段表，**但 Schema 作为可校验合同未落地这些字段**，导致"有 Schema 文件存在" ≠ "指标合同可机器校验"。

**整改**：新增一份 `MetricDefinition.full.schema.json`（或扩展原 Schema 为 full 剖面），把 C04 §2 的 7 组字段完整落地，保留现有 SIM-only 剖面作为最小子集。这是 F06 关闭的核心设计补齐。

### 缺口 G2｜MAJOR｜跨币种负例 C002 缺独立预期错误

**现状**：C002 有 USD 账户（SIM-A0022，120000.00 USD），但 `simulation/oracles/expected.json` 只有 C001 的 expectedValue，**没有 C002 的预期错误**（应为 `CURRENCY_POLICY_REQUIRED`，对应 T15）。

**整改**：在 oracle 增加 C002 负例预期：
```json
{
  "metricId": "SIM.METRIC.CUSTOMER_AVG_DEPOSIT",
  "customerId": "SIM-C002",
  "currency": "CNY",
  "expectedError": "CURRENCY_POLICY_REQUIRED",
  "reason": "客户含 USD 账户且未指定获准转换政策"
}
```

### 缺口 G3｜MAJOR｜T11–T16 六类负例缺独立预期数据

**现状**：总契约 C04 §7 定义了 8 类失败行为（METRIC_NOT_REGISTERED、GRAIN_VIOLATION、DATA_INCOMPLETE、CURRENCY_POLICY_REQUIRED、SCOPE_DENIED、SNAPSHOT_UNAVAILABLE、QUERY_BUDGET_EXCEEDED 等），验收矩阵 T11–T16 定义了 6 个负例场景，但**数据层没有对应的坏数据样本 + expectedError 落盘**。

| 验收 | 负例场景 | 数据现状 |
|---|---|---|
| T12 关联放大 | 余额关联多笔交易 | ❌ 无坏数据样本 |
| T13 相同余额两账户 | 两个 100 元账户 | ❌ 无独立样本（C001 是 300 万场景） |
| T14 缺失/重复日期 | 删一天/复制账户日 | ❌ 无坏数据样本 |
| T15 币种/汇率缺失 | C002 CNY+USD | ⚠️ 数据有（USD 账户），但无 expectedError |
| T16 授权与历史时态 | 越权 customerId/旧快照 | ❌ 无负例样本 |

**整改**：新增 `simulation/oracles/negative_cases.json`，为 T12–T16 每项提供坏数据样本引用 + expectedError + 隔离声明（不能污染正常快照）。

---

## 3. 本轮 F06 补齐设计（可执行方案）

### 3.1 补齐 MetricDefinition 完整 Schema

在 `schemas/` 新增 `MetricDefinition.full.schema.json`，覆盖 C04 §2 的 7 组字段（身份/对象与粒度/计算/时间/金额/数据/运行），原 `MetricDefinition.schema.json` 保留为 SIM-only 最小剖面并标注 `"$ref"` 关系。

**字段组落地清单**（对齐 C04 §2）：

| 字段组 | 落地字段 |
|---|---|
| 身份 | metricId、version、中文定义、Owner、approvalRef、definitionHash |
| 对象与粒度 | population、entityType、baseGrain、aggregationGrain、dimensions、allowedJoinPaths、joinCardinality |
| 计算 | numerator/denominator 或 expressionRef、additivity、distinctKey、dedupPolicy、roundingMode、scale |
| 时间 | intervalConvention、businessTimezone、calendarVersion、asOfPolicy、lateArrivalPolicy、accountLifecyclePolicy |
| 金额 | currencyPolicy、unit、fxPolicy、fxSource、fxDateRule、precision |
| 数据 | sourceProductRef、sourceSnapshotPolicy、mappingVersion、completenessRule、nullPolicy、qualityChecks |
| 运行 | queryTemplateRef、parameterSchemaRef、resultSchemaRef、permissionRef、maxRows、timeoutMs、costBudget |

### 3.2 补齐 C002 跨币种负例 + T11–T16 负例数据

新增 `simulation/oracles/negative_cases.json`，结构与 `expected.json` 并列，明确 `simulationOnly` + `expectedError` + 隔离声明。

---

## 4. F03–F05、F07 覆盖核对（本轮已完成 Schema 层逐项核对）

### 4.1 核对结论总表

AR-R2 要求"依次核对"。经逐项读取 14 个 Schema 后，结论如下：

| 发现项 | 设计层（C 正文） | Schema 层 | 主要缺口 | 优先级 |
|---|---|---|---|---|
| F03 系统权威矩阵 | ✅ C01 §1/§2 完整（五子系统六边界 + 对象级唯一权威表） | ⚠️ SemanticPackage 覆盖类型/imports，但**缺"唯一写入口"字段** | 对象级权威的"唯一变更责任/写入口"未在 Schema 落地 | 中 |
| F04 注册中心/地图 | ✅ C02 §2 完整（六注册模块 + 三视图） | ✅ AssetVersion/KnowledgeMap **字段完整**，但六注册对象仅 2 个有 Schema | SourceVersion/Capability/QueryDefinition/MapVersion/Release 缺独立 Schema | 中 |
| F05 构建发布主链 | ✅ C03 §2 完整（P01–P10 + 状态机） | ✅ Assertion/ReviewDecision/ReleaseManifest **字段完整**（含 evidence 闭包/targetHash/投影状态） | 缺"端到端设计实例"（带新旧版本/否定/同名主体的走查） | 中 |
| F07 RAG/图适配 | ✅ C05 §2/§3 完整（三路径 + 适配能力） | ✅ GraphRequest/GraphResponse **字段完整**（含 maxHops 1-3/sourceRefs） | 缺 ExistingRagAdapter 的 Schema（LegacyRagHit 映射） | 中 |

### 4.2 关键正面证据（Schema 落地质量显著高于 F06）

经逐项核对，F03–F05/F07 的 Schema **大部分字段已落地**，远好于 F06 的 MetricDefinition（瘦剖面）：

| Schema | 覆盖质量 | 亮点 |
|---|---|---|
| SemanticPackage | 良好 | ownerSystem 枚举含 CORE、types 含 typeId/definition/identityRule、imports 版本化 |
| AssetVersion | **完整** | 16 字段全覆盖（assetClass 四类、kind 九类、contentHash 64hex、scope、purposeFlags、lifecycle、dependencyRefs） |
| KnowledgeMap | **完整** | 节点四类型、边六 relation、routePolicyRef、scope 全覆盖 |
| Assertion | **完整** | modality 四类、knowledgeState 四态、evidence 引用闭包（sourceId/version/quoteHash/sourceHash） |
| ReviewDecision | **完整** | targetHash 64hex 绑定、reviewerPrincipal/authorPrincipal 分离、reviewerRole 三 Owner |
| ReleaseManifest | **完整** | payload/payloadHash 分离、projectionStates（READY/PENDING/FAILED）、graphRequired、status |
| GraphRequest/Response | **完整** | queryId 白名单（SIM-GQ-HOLDINGS）、maxHops 1-3、maxNodes 1-50、paths 含 sourceRefs |

### 4.3 各发现项的具体缺口

#### F03（权威矩阵）缺口：Schema 缺"唯一写入口"字段

C01 §2 明确"每个可变权威字段有唯一 ownerSystem；所有投影写入口受限"（INV-01）。但 `SemanticPackage.schema.json` 的 `types[]` 只有 `typeId/definition/identityRule`，**缺 `writeOwner`/`writeEntry`/`authorityScope` 字段**。这意味着权威矩阵的"唯一变更责任"停留在正文描述，未落到可校验 Schema。

#### F04（注册/地图）缺口：六注册对象仅 2 个有 Schema

C02 §2 定义六个逻辑模块：AssetCatalog、SourceRegistry、CapabilityRegistry、QueryRegistry、MapRegistry、ReleaseRegistry，对应六类注册对象（AssetVersion、SourceVersion、Capability、QueryDefinition、MapVersion、Release）。但 Schema 层只有：
- AssetVersion ✅
- KnowledgeMap（≈ MapVersion 的一部分）✅
- **SourceVersion ❌ 缺**
- **Capability ❌ 缺**
- **QueryDefinition ❌ 缺**（query_registry.json 是数据样例，非 Schema）
- **Release ❌ 缺**（ReleaseManifest 是发布清单，非 ReleaseRegistry 的注册对象）

#### F05（构建发布）缺口：缺端到端设计实例

C03 §2 的 P01–P10 流水线 + §5 状态机 + §6 原子发布，Schema 层（Assertion/ReviewDecision/ReleaseManifest）都已落地。缺口是报告 F05 明确要求的"**一份带新旧版本、条件、否定和同名主体的文档走完整设计实例**"——即需要一份贯穿 SourceVersion → Fragment → CandidateAssertion → 身份对齐 → CandidateMap → ReviewPackage → StagedRelease → Release → 撤销/新版本的完整走查文档，作为黄金样例。

#### F07（RAG/图适配）缺口：缺 ExistingRagAdapter Schema

C05 §3 定义了 `LegacyRagHit` 至少映射 sourceId/sourceVersion/fragmentId/locator/text/score/permissionDecisionRef。但 Schema 层只有 GraphRequest/GraphResponse（图路径），**缺 RAG 路径的 Schema**。这是 F07 要求"ExistingRagAdapter 明确 sourceId/chunkId/sourceVersion、原文定位、ACL、用途和撤销"的关键缺口。

### 4.4 TL 判断

F03–F05、F07 的**设计层与 Schema 层大部分已扎实落地**，远好于 F06。四者的缺口高度同构，都是"设计正文 → 可校验 Schema 落地"的最后一公里：

| 缺口类型 | 涉及发现项 | 具体动作 |
|---|---|---|
| Schema 缺关键字段 | F03 | SemanticPackage 补 writeOwner/writeEntry |
| Schema 缺对象 | F04、F07 | 补 SourceVersion/Capability/QueryDefinition/Release 四 Schema + RAG 适配 Schema |
| 缺端到端实例 | F05 | 补一份完整走查黄金样例 |

这些与 F06 的 G1（MetricDefinition.full）同属"合同源变更"范畴，应统一走 `specs/` → `make generate` → `make check` 流程，避免分散执行。

---

## 5. 本轮实际变更（本次会话已落盘）

本轮 AR-R2 完成的是**核对与缺口定位**，未直接改 `generated/`、未动合同源。具体变更将在后续"合同源→generate→check"流程中执行（遵守 api-first 红线）。

**已确认的现状（无需改，只需补证据）**：
- C04 设计层字段表完整 ✅
- 受控查询模板 `query_registry.json` + `avg_deposit.sql` ✅
- C001 复算 + 账户日唯一性 ✅
- C002 跨币种数据存在 ✅

**待补（需走合同源变更流程）**：
1. `MetricDefinition.full.schema.json`（G1）
2. `negative_cases.json`（G2 + G3）

---

## 6. AR-R2（F06 部分）退出条件

| 报告要求（F06） | 状态 |
|---|---|
| 指标 metricId/version、Owner/approvalRef、定义 hash | ✅ 已有（approvalRef 用 SIM 占位，definitionHash 待补） |
| 分子分母与舍入规则 | ⚠️ formula 有，numerator/denominator 结构化字段待补（G1） |
| 数据映射 accountId+businessDate+snapshotId 唯一性 | ✅ 已验证 720 记录 0 重复 |
| 账户当日归属、允许 join 路径与基数 | ⚠️ allowedJoinPaths/joinCardinality 仅设计层，Schema 待补（G1） |
| 时间/金额（统计区间/日历/时区/迟到/币种） | ⚠️ 区间/时区/币种有，lateArrivalPolicy 待补（G1） |
| 执行（仅 metricId/queryId、白名单、服务端授权） | ✅ query_registry 体现良好 |
| 返回（数值/币种/口径/时点/queryRunId/追踪） | ✅ SemanticResult Schema 完整 |
| 负例（关联放大/同余额/重复账户日/缺日/跨币/越权/旧快照） | ⚠️ 跨币数据有，其余负例数据待补（G2/G3） |

---

## 7. TL 落盘声明

```
[AR-R2 全量核对完成] F06 + F03/F04/F05/F07
        F06: 设计扎实, G1 MetricDefinition瘦剖面 / G2 C002负例 / G3 T12-16负例
        F03: 设计层完整, Schema缺writeOwner/writeEntry字段
        F04: 设计层完整, 六注册对象仅2个有Schema(缺SourceVersion/Capability/QueryDefinition/Release)
        F05: 设计层+Schema完整, 缺端到端黄金实例
        F07: 设计层+Graph Schema完整, 缺ExistingRagAdapter Schema
        共性: "设计正文→可校验Schema"最后一公里, 统一走合同源变更流程
```

本轮 AR-R2 完成 F06 + F03/F04/F05/F07 的**全量核对与缺口定位**。核心结论：

1. **F06 设计最扎实**：受控查询（query_registry + avg_deposit.sql）、账户日粒度、C001 复算（2,983,333.33 命中）均正确，缺口只在 Schema 完整性与负例落盘。
2. **F03–F05/F07 Schema 落地质量显著高于 F06**：AssetVersion/KnowledgeMap/Assertion/ReviewDecision/ReleaseManifest/GraphRequest/GraphResponse 七份 Schema 字段完整，远非空模板。
3. **所有缺口高度同构**：都是"设计正文已写 → 可校验 Schema 未落地"的最后一公里，应统一走合同源变更，避免分散执行。

---

## 8. 下一步（供决策）

### 8.1 合同源变更清单（统一走 `specs/` → `make generate` → `make check`）

| 批次 | 动作 | 对应发现项 | 关闭对象 |
|---|---|---|---|
| 批次 1（F06 优先） | 新增 `MetricDefinition.full.schema.json` + `negative_cases.json` | F06 | G1/G2/G3 |
| 批次 2（F03/F04/F07） | 补 `SourceVersion/Capability/QueryDefinition/Release` 四 Schema + `ExistingRagAdapter` Schema + SemanticPackage 补 writeOwner | F03/F04/F07 | 权威写入口/六注册对象/RAG 适配 |
| 批次 3（F05） | 补端到端黄金实例文档（新旧版本/否定/同名主体走查） | F05 | 主链实例 |

### 8.2 执行顺序建议

1. **批次 1 先行**：F06 是业务正确性最高风险，且缺口最小（2 个文件）。
2. **批次 2 次之**：F04 六注册对象 Schema 是 F04 关闭的关键，且与 F07 的 RAG Schema 可合并。
3. **批次 3 最后**：F05 端到端实例依赖前两批 Schema 就绪后才有意义。

是否现在执行批次 1（F06 优先）的合同源变更？
