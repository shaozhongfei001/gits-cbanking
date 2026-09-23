# W1 计划｜P38 十二章 → 新版区块逐一落位（PC-i1 · Owner 2026-09-23 授权开工）

```text
依据（权威输入，已核验）：
  R2 包 = /home/szf/deliverables/GITS-PI-EXPERT-REVIEW-20260922-R2.zip
          sha256 747a5b4a679605a30b2cf899a2df1b0019aac5d4de318c048d987abe16f85665（与登记一致，3,386,793 bytes）
          · 03_十二章四维映射.csv（12 章 × 四维）
          · 04_95项差异矩阵_R2.csv · 06_同产品同条件走查.md
  Owner 裁决：docs/dispatch/PI-O-裁决登记-2026-09-22.md（O-1 过渡安排 / O-2 ①②分别建模两者都保留）
  前置已完成：W-1/W-2（d4ad4a2）—— 5 章空壳已修、期望值已语义化
```

## 1. 缺口重算（R2 映射的"新位置"列**成文于 W-1 之前**，故必须按**当前代码**重算）

| 章 | 标题 | R2 记的"新位置"（W-1 前） | **W-1 后实测**（回源） | 仍缺 |
|---|---|---|---|---|
| C1 | 产品概览与客户价值 | 首屏一句话定义 + 附录原材料 | 首屏 `summary.oneSentenceDefinition` ✓ + 原始材料区 ✓ | — |
| C2 | 适用客户与适用场景 | 首屏「适用主体」= **待核验**；附录原材料 | FIT 章已渲染 `boundaries[].scenarioName/scenarioDescription`（`ProductChapterStack.vue` `FIT` 分支）；P38 卡 `scenarios` 有值（CM-003 实测 3 项） | 首屏「适用主体」仍「待核验」；**未指名引用** P38 `scenarios` |
| C3 | 产品能力 | 首屏能力标签（capabilities）= 部分 | P38 `capabilities` 实测有值（如 IB-001 3 项 / FIN-001 3 项）；新版页**未指名引用** | 需落点（指名引用，不可只留关键词） |
| C4 | 准入条件 | 「适用边界」= 具名未接入 | **已承接**：FIT 渲染 `prerequisites[].requirementText`（CM-003 实测 4 条） | — |
| C5 | 排除条件与禁止用途 | 「适用边界」= 具名未接入 | **部分**：`boundaries` 已渲染（CM-003 3 条，含 `boundaryType`）；**排除/禁止用途**是否单列待核 `boundaryType` 取值分布 | 需确认被"排除"语义有独立可见位 |
| **C6** | **前置、互斥、替代与配套产品** | 「**无任何对应区块**（比较章为具名未接入）」 | COMPARE 章现渲染 `comparison`（维度/行）—— 但 loop 明令「**不得被比较表替代**」 | **必须有独立可见区块** |
| C7 | 流程与材料 | 「办理流程」「申请材料」= 具名未接入 | **已承接**：PROCESS `processSteps`（5 步，含 `humanDecisionRequired`）+ MATERIALS `materialGroups` | — |
| C8 | 价格边界 | 「价格与协议」= 具名未接入；附录 | PRICING 仍具名未接入（`pricingItems=0`）**如实** | 待契约数据（PC3），本波不改口径 |
| **C9** | **风险提示与人工复核** | 「**无任何对应区块**」 | P38 卡详情 `sections` 第 9 节有原文（CM-003 40 字）；`riskNotes` 在卡列表有值（CM-003 详情为 0） | **必须有独立可见区块** |
| C10 | 销售边界 | 首屏通用 2 条 + 右栏「页面边界」（部分） | 契约有 `salesBoundaries`；新版页**未指名引用** | 需落点（产品级销售边界） |
| **C11** | **不可变版本语义** | 右栏版本区=**被替代**（仅版本徽章） | 契约有 `version` + `PkcVersionDiff` | **版本区须承载该节语义**（不得仅徽章敷衍） |
| C12 | EvidenceRef（源文件与条款定位） | 无（仅 PROD-FIN-* 3 张） | P38 卡 `sections` 最多到 §11；CM-003 无 §12 | FIN 3 卡需按章节原文落位 |

## 2. 数据源（实测，决定实现口径）

| 用途 | 来源 | 事实 |
|---|---|---|
| **合同化字段**（C1/C4/C7 等） | `GET /api/v1/product-center/products/{id}` | 已由 W-1 渲染 |
| **未实现章节的原文**（C6/C9/C11/C12 与 C5 排除项） | `GET /api/v1/product-knowledge/cards/{id}` → `sections[{title, content}]` + `sourceFile` + `rawMarkdown` | **实测 PROD-CM-003 有 11 节**，标题与 C1–C11 一一对应（`1. 产品概览与客户价值` … `11. 不可变版本语义`）；`sourceFile` = `cash-management/version=2026.09.01.1/product-cards/PROD-CM-003.md`（**相对路径**，满足"相对来源标识"） |
| 卡摘要字段 | `GET /api/v1/product-knowledge/cards` | `capabilities`/`scenarios`/`riskNotes` 均有值（13 卡实测） |
| **契约无结构化对象** | 契约 schema 清单 | `风险/复核类: []`；关系类仅 `PkcPrerequisite` ⇒ **C6/C9 不得自造结构化字段**，只能"原样呈现原文 + 来源 + 有效状态"（loop objective 原话） |

## 3. 工作分解（本波）

| # | 工作项 | 口径 | 验收 |
|---|---|---|---|
| `W1-a` | **C6 独立区块** | 新增独立区块，渲染 P38 卡 §6 原文 + `sourceFile` + 节号 + 有效状态；**不得**用 `comparison` 表替代 | 该区块可定位（`data-testid`）；原文与卡片 §6 逐字一致；含相对来源与状态 |
| `W1-b` | **C9 独立区块** | 同上（§9 原文；若 `riskNotes` 有值则并列显示，不合并） | 同上；`riskNotes` 有值时可见 |
| `W1-c` | **C11 版本区承载语义** | 版本区呈现 `version`（versionId/label/status/knowledgeAsOf/effectiveFrom-To/审核）+ §11 原文；**不得**只留徽章 | 版本区可断言"含 §11 语义" |
| `W1-d` | **C2/C3/C10 落点（指名引用）** | 首屏适用主体/能力标签指名引用 P38 `scenarios`/`capabilities`；`salesBoundaries` 单独呈现（产品级） | 三项各自可见且可追溯到来源 |
| `W1-e` | **C12 按需落位** | 仅当卡片有 §12（PROD-FIN-*）时呈现 | FIN 3 卡可见；其余卡如实"无 §12" |
| `W1-f` | **有效状态语义** | 统一"有效状态"呈现（未发布受控版本 / DRAFT / 未复核），**不得**暗示已生效 | 与右栏治理栏口径一致 |
| `W1-g` | **同产品对照三判定** | 按 `06_同产品同条件走查.md`：事实不丢 / 来源可达 / 阅读更快；**不得**做"阅读用时"结论（未做用户测试） | 三判定逐项留证 |

**禁止**：改 P38 冻结文件（`ProductInterpretationView.vue`、`apps/api/**/productknowledge/`）、改 `specs/` 受控源、手改 KERT 制品、以前端硬编码业务内容。

## 4. 门禁（沿用 `LOOP.yaml`，G-1/G-2 已修）

`contract_generate` / `security_check` / `frontend_typecheck` / `frontend_unit`（`cd frontend && npx vitest run`）/ `e2e_parity`（`cd frontend && VITE_API_PROXY_TARGET=http://127.0.0.1:18080 npx playwright test e2e/product-center-pc1.spec.ts --output=test-results/gate-e2e-parity`）；
`contract_check` 仍为既存生成漂移（非本 loop 引入）。

## 5. 关联未决

- `F-PC-i1-04`：`loop-guard` 因原始失败日志含 Vue 插值被误判 ⇒ **阻塞** `scripts/qa_attest.py`（其内部先跑 `loop_guard --evidence-only`）。修法 R-1/R-2 待 Owner 授权。
- `contract_check` 既存漂移 ⇒ 按 `loop_guard.py:243`，状态无法升到 `ready_for_independent_qa`（该状态要求全部门禁 pass）。


---

## 6. 执行记录（2026-09-23T03:10:38+00:00）

| 工作项 | 状态 | 实现与证据 |
|---|---|---|
| `W1-a` C6 独立区块 | **已完成** | 新增 `ProductInheritedChapters.vue`：按 `utils/cardChapter.ts` 定位产品卡第 6 节，**原样呈现原文** + 相对来源（`sourceFile` + 节号）+ 有效状态；锚点 `pc-inherited-c6[-content|-meta|-absent]` |
| `W1-b` C9 独立区块 | **已完成** | 同上（第 9 节）；两区块位于主栏八章之下，**未被比较表替代** |
| `W1-c` C11 版本区承载语义 | **已完成** | `ProductGovernancePanel` 新增「版本语义（不可变版本）」：语义陈述 + 本页版本事实字段 + 第 11 节原文 + 相对来源；锚点 `pc-immutable-version[-statement|-facts|-content|-source|-absent]` |
| `W1-f` 有效状态语义（部分） | **已完成（承接区/版本区）** | 以事实字段拼接（versionStatus（versionLabel）｜生效日：字段值或「未设定」），**不**改写为判断性表述 |
| 数据接线 | **已完成** | `ProductCenterView.vue` 增 `cardDetail` 取数（CTR-PK-INT-001，只读复用）+ `watch(selectedProductId)`；失败 ⇒ 具名「来源标识不可得 / 未包含第 N 节原文」（**不伪造**） |
| 用例 | **已完成** | 新增 `ProductInheritedChapters.spec.ts`（3 例）+ 视图 2 例（含「来源不可得具名降级」）；e2e 增 C6/C9/C11 断言（真实原文关键字：前置产品 / 人工复核 / 不可变） |
| 门禁 | **已记录** | `frontend_unit` **pass**（68 文件 / **371 tests**）· `e2e_parity` **pass**（2/2）；`contract_check` 仍 fail（既存漂移） |
| **未开工（下一批）** | — | `W1-d`（C2/C3/C10 指名引用）· `W1-e`（C12，仅 FIN 3 卡）· `W1-g`（同产品对照三判定） |

**边界复核**：未改 P38 冻结文件、`specs/` 受控源、KERT 制品；组件内**未硬编码**任何业务文本（原文一律取自接口）；页面不出现本机绝对路径（用例已断言）。


---

## 7. 执行记录 · 第二批（2026-09-23T03:45:23+00:00）：W1-d / W1-e / W1-g

| 工作项 | 状态 | 实现与证据 |
|---|---|---|
| `W1-d` C2/C3/C10 指名引用 | **已完成** | `cardChapter.ts` 增 `landing`（承接位置，指名引用）并扩章表为 C2/C3/C6/C8/C9/C10/C12；`ProductInheritedChapters.vue` 每章渲染「承接位置 + 原文 + 相对来源 + 有效状态」；**C10 呈现合同字段 `salesBoundaries`**（产品级，实测 2 条含 `boundaryKind`/`riskCategory`/`mandatoryDisplay`），为空时具名标注 |
| `W1-e` C12 按需落位 | **已完成** | 章表含 C12；`PROD-FIN-*` 3 卡实际渲染 §EvidenceRef 原文；其余卡**具名缺失**（本卡 11 节实测） |
| `W1-g` 同产品对照三判定 | **已完成（含诚实边界）** | `memory/waves/W1-g-同产品对照.md` + `evidence/w1-g-parity-<ts>.json`：落点覆盖 **12/12**；**来源可达 ✅**；**操作路径更短 ✅**（1 选择 + 0 展开，旧版侧引用 R2 §6 基线）；**事实等价未验证 ⇒ 不得宣布通过**；**无任何用时结论** |
| **本轮修掉 2 个真实缺陷（我引入的）** | **已修 + 回归** | ① 节号在卡间**不一致**（`CM-003` §11=不可变版本语义；`FIN-003` §11=EvidenceRef、§12=不可变版本语义）⇒ 原「节号前缀优先」会把 C11 错配到 §11；改为**标题优先、节号兜底**，并新增 `actualSectionNo` 展示**实际**节号 ② 右栏版本区**写死**「第 11 节原文」⇒ 改为使用**实际节标题**。回归：`utils/__tests__/cardChapter.spec.ts`（4）+ 组件/视图用例 + e2e 新增「FIN 卡节号错位不得错配」用例 |
| 门禁 | **已记录** | `frontend_unit` pass（靶向 20/20；全量见日志）· `e2e_parity` pass（**3/3**，含 FIN 错位回归） |

**边界复核**：未改 P38 冻结文件、`specs/` 受控源、KERT 制品；组件内未硬编码业务文本（原文/字段一律取自接口）；页面无本机绝对路径。
