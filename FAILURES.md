# FAILURES.md

## FAIL-2026-09-14-02: 已交付工作包被 stash 后从未回合并，成果"消失"近一周（并导致 Agent 误判为不存在）

**发现日期**: 2026-09-14
**发现角色**: Owner（指出）→ Tech Lead（复核确认）
**严重程度**: **MAJOR**（成果流失风险 + 证据链断裂）

### 现象

Owner 指出"产品解读功能在 2026-09-07 真实存在，绝对被改过"。
复核确认：**Owner 正确**。

- 该功能 = **PI-ARCH-IMPLEMENTATION-01 阶段 B（L10–L13）**，GITS 侧 7 提交 `2ceb66d → 433a21d`，
  73 files / +17428；`docs/pr/PI-ARCH-L10-L13-PR.md` 记载 **`REAL_E2E_PASS=YES`（S1–S17 全 PASS，双实例真实 HTTP）**。
- 2026-09-08 截图（现存于 `evidence/p24-e2e/s1-product-knowledge/`，亦在被 stash 的未跟踪集内）。
- **2026-09-10 因 GK-KE L0 合同工作接管分支，整包被 `git stash`**
  （`stash@{0}: On GK-KE-L0-contract: PI-ARCH-L10-L13 WIP before GK-KE-L0`），
  工作树回退到 09-07 的演示页版本，**此后从未回合并**。

### 我的误判（**这是本条最该记住的部分**）

我据以断言"那一版从未在本仓存在过"的三步全部无效：

| 我的动作 | 为何无效 |
|---|---|
| `grep -rn "深度解读\|产品摘要\|制度解读" frontend/src docs/` → 零命中 | 这些字符串是**产品卡 markdown 的数据内容**，不在前端源码里。**拿数据串去搜代码，等于没搜** |
| `git log --all -S"深度解读"` → 零命中 | 同上；且该版当时**未提交**，只在工作树/stash |
| 结论"从未存在" | **未检查 `git stash`**；且更早一次 grep 已列出 `docs/pr/PI-ARCH-L10-L13-PR.md`，**我看到了线索却没跟** |

⇒ **零命中 ≠ 不存在。** 检索不到时，必须换检索面（stash / 悬挂提交 / 数据 vs 代码 / 文档索引），
而不是把"我没找到"写成"它不存在"。

### 处置（已完成）

从 `stash@{0}`（基线 `2934a9e`）**选择性还原最小完整集**，提交 `1bd4363`，分支
`recover/PI-ARCH-product-catalog`（`feature/GK-KE-L0-contract` 未动，`stash@{0}` 保留）：

- 前端 4：`ProductInterpretationView.vue`、`api/productKnowledge.ts`、`layouts/navConfig.ts`（菜单指向
  `/product-knowledge/interpretation`）、`router/index.ts`
- 后端：`productknowledge` 包（目录服务 + DTO + 控制器）、`ProductKnowledgeVersion` record
- 配置：`application.yaml` 增 `gits.product-knowledge.card-dir`
- 数据：`V021__corporate_product_knowledge_seed.sql`（h2 + mysql）
- 测试 3 个

**验证**：`vue-tsc --noEmit` **0 错误**；`mvnw compile/package` OK；
`GET /api/v1/product-knowledge/cards` → **200，13 张卡**，`interpretable=true` **仅 `PROD-CM-001`**
（与截图说明逐字吻合）；`GET …/PROD-CM-001/interpretation?view=ELIGIBILITY` → **200**，
`minAccountBalance="50 万元"/SUPPORTED`、证据 `SRC-CM-001` / `locatorHint 第十条`（= PR 文档期望值）、
`customerSegment=UNKNOWN` 且 `displayValue=null`（**忠实，不补值**）。

### 未做（给出归属与理由）

| 项 | 理由 | 归属 |
|---|---|---|
| `specs/product-knowledge/*` 5 个合同 | **DIRTY**：HEAD 相对 stash 基线已变动，**不得用旧版覆盖新版**，须**合同先行**逐一合并 | Tech Lead |
| `v11.ts`、`ProductKnowledgeCard.vue` | 一并还原会拖入**无关的商机字段重构**，引发 17 处无关类型错误；目录页**不依赖**二者 | 需单独立项 |
| `make check`、前后端测试 | 未跑（本轮只做编译与端到端实测） | 下一步 |
| **`PAGE_ID='P38'` 冲突** | `KnowledgeMapView.vue:17` 与 `ProductInterpretationView.vue:38` **都声明 P38** | 随 IA 变更一并解决 |

### 教训（写入长期纪律）

1. **检索不得以"零命中"下"不存在"的结论**；必须换检索面。
2. **分支被接管时必须处理未完成成果**：要么合并、要么转分支、要么落盘登记，
   **不得留在 `stash` 里静默丢弃**。本次即为反例。
3. **交付物索引要坚持**：`docs/pr/` 有 PR 文档、`evidence/` 有截图，却无人据此回头核对是否真的落地。

---

## FAIL-2026-09-14-01: 运行期与合同的四处漂移（编制人工测试清单时只读取证命中）

**发现日期**: 2026-09-14
**发现角色**: Tech Lead（编制 `docs/governance/GITS-Bank-人工测试清单-V1.0.md` 时的只读探测）
**严重程度**: MAJOR（①④）/ MINOR（②③）
**环境锚点**: gits-cbanking `3f16d97`、KERT `c65a861`、jar 构建于 09-11 12:45

### ① 6 个端点在 OpenAPI 中已登记，运行期**无映射**（MAJOR）

只读探测所得，报错原文为 Spring 的 `No static resource <path>`：

| 端点（合同已登记） | 实测 | 报错原文 |
|---|---|---|
| `GET /engagement/claims`（`listClaims`） | 404 | `No static resource api/v1/engagement/claims.` |
| `GET /customer-journeys` | 404 | `No static resource api/v1/customer-journeys.` |
| `GET /knowledge-rules` | 404 | `No static resource api/v1/knowledge-rules.` |
| `GET /operating-cases` | 404 | `No static resource api/v1/operating-cases.` |
| `GET /products/versions` | 404 | `No static resource api/v1/products/versions.` |
| `GET /engagement/kyc/{customerId}/insights` | 404 | `No static resource api/v1/engagement/kyc/….` |

- **影响**：**P37 Claim/Evidence 中心页会报错**（`frontend/src/views/ClaimsView.vue` 使用 `listClaims`）；
  其余 5 个前端当前未调用。
- **与既有失败同根**：`OWNER_UAT_W9A_FAIL_2026-08-26.md` 记载的 500（`/api/v1/interactions`）
  就是同一形态 ——「OpenAPI 已登记该 GET；运行中的 API 没有映射」。
  本次可诊断性提升（明确的 404 + 原因），但**同类问题仍有 6 处未清**。
- **处置**：先记。补实现 or 从合同移除 —— **属合同变更，须走合同先行**
  （改合同源 → `make generate` → `make check` → 再改实现）。**未在本次修复。**

### ② 错误响应结构与合同不符（MINOR）

- **实测**（运行期）：`{"errorCode":"NOT_FOUND","message":"No static resource …","timestamp":"…"}`
- **合同权威**（`specs/openapi/gits-kno-api.openapi.json` → `components.schemas.Problem`）：
  `{status, error, message, path, timestamp}`
- ⇒ 字段名集合不同（`errorCode` vs `status`+`error`，缺 `path`）。
  **与「合同 SSOT」规则冲突**；客户端按合同解析会取不到字段。
- **处置**：先记。与 ① 一并处理（同一处 `@ExceptionHandler` 与合同对齐）。

### ③ 导航「客户组合」未指向 P03（MINOR·待 Owner 判定是否为缺陷）

- `frontend/src/layouts/navConfig.ts`：`{key:'portfolio', label:'客户组合', to:'/accounts'}`，
  而**路由表中 P03「客户分层与组合看板」是 `/accounts/portfolio`**；
  且「客户全景」也指向 `/accounts` ⇒ **两个一级项落到同一路由**。
- **影响**：菜单语义与页面身份不符（Owner 在 08-26 已对导航与设计图一致性提出过不通过）。
- **处置**：先记，**待 Owner 判是否为缺陷**（涉及导航语义，编制者不代为定性）。

### ④ 依赖服务不可用时的降级口径**两份文档冲突**（MAJOR·待裁定）

- **实测**：停掉 KERT 8107 后调用 `POST …/prepare-previsit` → **`200` + 空态**
  （`openingLine=""`、`talkingPoints=[]`）；恢复 8107 后 → `openingLine="综合金融服务"`、
  `talkingPoints=2`、`skillSections=7`、`assemblyTrace=13`。
- ✅ **好消息**：**未发现本地补数**，"禁止本地补数"红线守住。
- ⚠️ **冲突**：
  - `evidence/L6/操作说明-L6.md` §4 要求「依赖服务不可用 ⇒ **503 明确报错**；**禁止静默成功**」；
  - `OWNER_UAT_W9A_FAIL_2026-08-26.md` 的处置写「**失败空态**，不本地补数」（Owner 当时要求）。
- **实测行为 = `200` + 空态**：同时满足后者、违反前者。
- **处置**：**先记，不代替 Owner 裁定**。裁定前，人工测试者**必须核对 8107 是否在线**，
  否则会把空态误判为"页面坏了"，或把静默降级误判为"正常"。

### 边界声明

- 本条全部证据来自**只读探测**；**未修改**任何被测实现、合同、`generated/`；
- 未签署任何通过结论；① ② 的修复涉及合同变更，**须 Tech Lead 走合同先行流程另开工作项**。

---

## FAIL-2026-09-11-02: 封版 V1.0.1 证据链两处硬错误 + SemanticPackage schema 分叉

**发现日期**: 2026-09-11
**发现角色**: Tech Lead（对架构委员会 PASS_WITH_REQUIRED_CHANGES 整改的独立机器核验）
**严重程度**: BLOCKER（阻断独立 QA 二次复核与 D 阶段门禁提升）

### 现象

TL 对整改答复（`GITS-KERT_架构委员会整改答复_AC01-04_V1.0.md`）声称的"唯一证据链"做独立机器核验，发现三处不实：

1. **受控目录 tree hash 笔误**（已修正）：整改答复 + 独立QA提示词 + STATE.json 三处写 `daa9b511...`，真实值 `git rev-parse HEAD:docs/dd/gk-ke-contract` = `8de275b722f7d65186f3f0691973f28f3c51b8b3`。已由 TL 勘误修正为真实值。

2. **SemanticPackage.schema.json 权威源与交付包分叉**（未修复，需 Feature Pilot）：
   权威源 `specs/gk-ke/v1/schemas/SemanticPackage.schema.json` 含 `writeOwner`/`writeEntry`/`authorityScope` 三字段（WP-R4-1 任务6 补的 F03 权威矩阵整改），
   但交付包 `docs/dd/gk-ke-contract/schemas/SemanticPackage.schema.json` 仍是旧版（缺这三字段）。
   其正例 `examples/positive/SemanticPackage.json` 同样分叉。
   其余 19 schema + 59 example 均 byte-identical，分叉仅 SemanticPackage 一处。

3. **整改答复 AC-03 声称"byte-identical 0 差异"不成立**：见上，SemanticPackage 分叉直接推翻该声明。

### 影响

- 封版 V1.0.1 交付包缺少 F03（权威矩阵）整改的核心成果（writeOwner/writeEntry/authorityScope）。
- 独立 QA 按提示词执行会发现 tree hash 不符（已修正）与 schema 分叉，无法给出 QA_PASS。
- AC-03「Git-QA 一一对应」实际未关闭，整改答复的"AC-01/02/03 全部完成"声明不成立。

### 处理

- [x] tree hash 笔误：TL 已勘误 3 处（整改答复、QA提示词、STATE.json）。
- [x] SemanticPackage schema 分叉：Feature Pilot 已重新同步权威源 → 交付包（byte-identical，diff -r 0 差异），重跑 validate_package.py（148/0）、gk_ke_contract_examples.py（20/40）、verify_simulation.py（PASS），重新封包 V1.0.2。新三值锚点：HEAD `886f7104f47bc3fa7ed1de1c95b91e3aa1cda13e`、tree `4c5f5373c83386d27ea996293a49ee7f3b9f10ce`、ZIP `GK-KE-CONTRACT-V1.0.2_REVIEW.zip` SHA-256 `b21638abef8eb0e271c2190303c8f5dfaa1609a5c82269db2c20f451d97a5ad0`（145/145 逐文件一致，0 差异）。整改答复/STATE/QA提示词证据链锚点已同步更新。
- [x] loop_guard 状态枚举缺口（TL 决策）：`sealed_pending_qa` 是非标准状态，破坏 loop_guard ALLOWED_STATES。TL 决策归一化为标准态 `ready_for_independent_qa`（封版二次复核语义由 EVIDENCE.json 的 `sealing_v1_0_2` 字段 + QA 提示词附录承载，不新造顶层 status）；Baton 从 `owner` 回退到 `independent_qa`（V1.0.2 尚未 QA 二次复核，不能越级进 Owner）。修复后 `make memory-check` / `make evidence-check` 均 PASS。

---

## FAIL-2026-09-10-01: S4 建议书草稿各章内容完全相同 — KERT 未接真实 LLM

**发现日期**: 2026-09-08（修复），2026-09-10 复测确认
**发现角色**: E2E Owner
**严重程度**: MAJOR（草稿无业务价值，不影响链路连通性）

### 现象

`POST /api/v14/proposals`（SP-20）返回 SUCCESS，但 CH01~CH10 每章正文逐字相同，
均为「CUST-CORP-0001为制造业客户，经营基本正常，存在金融需求（确定性样例…）」。

### 根因（非数据样本、非 LLM 质量，而是根本没调 LLM）

1. `Leibniz-KERT/src/kert/infrastructure/adapters/llm.py` `create_llm_adapter()`
   仅当 `KERT_LLM_BASE_URL` + `KERT_LLM_API_KEY` + `KERT_LLM_MODEL` 三者齐备才用真实适配器，
   否则静默退化为 `DeterministicLlmAdapter`。启动时只设了 `DEEPSEEK_API_KEY`，三个 `KERT_LLM_*` 缺失。
2. `DeterministicLlmAdapter` 的 proposal 分支对所有章节用同一段硬编码模板，
   只替换 chapterId/chapterName/industry，丢弃全部 chapterContext 真实企业数据。

### 修复

1. 主修复：启动 8107 注入 `KERT_LLM_BASE_URL=https://api.deepseek.com/v1`、
   `KERT_LLM_API_KEY`、`KERT_LLM_MODEL=deepseek-chat`、`KERT_LLM_TIMEOUT=180`。
2. 兜底加固：`DeterministicLlmAdapter` 新增 `_sample_proposal()`，按 chapterId 分化
   10 章叙述焦点并引用 chapterContext 真实字段，缺失字段进 unknowns 而非编造；
   `KERT_LLM_TIMEOUT` 改为可配（原硬编码 60s）。
3. 回归防护：`frontend/e2e/p24-s4-wizard.live.spec.ts` 断言各章正文互不相同
   （`new Set(bodies).size === bodies.length`），并禁止出现「确定性样例」。

### 复测结果（2026-09-10）

```
[s4] 200 in 31.6s status=SUCCESS draftLen=14145 citations=111 unknowns=53
[s4] headings=36 bodies=34 uniqueBodies=34 renderedLen=14145
1 passed (37.7s)
```

修复前：1085 字 / 10 章全同 / 16 引用 / model=deterministic_fallback。
修复后：14145 字 / 34 章正文全部唯一 / 111 引用 / model=deepseek-chat。

---

## Mapper XML Record 适配修复 — E2E 验证失败记录

**验证日期**: 2026-08-12
**验证角色**: E2E Owner
**分支**: feature/v11-frontend-depth-remediation

---

### F-1: FactReconciliationCaseMapper.xml 引用不存在的内部类 [BLOCKER]

**严重程度**: BLOCKER — 阻断所有集成测试

**文件**: `adapters/persistence-relational/src/main/resources/mapper/foundation/ontology/FactReconciliationCaseMapper.xml`

**行号**: 21

**现状**:
```xml
<arg column="status" javaType="com.gien.gits.ontology.FactReconciliationCase$ReconciliationStatus"/>
```

**期望**:
```xml
<arg column="status" javaType="com.gien.gits.ontology.ReconciliationStatus"/>
```

**原因**: `ReconciliationStatus` 是顶级枚举类 (`com.gien.gits.ontology.ReconciliationStatus`)，不是 `FactReconciliationCase` 的内部类。

**影响**: MyBatis 解析 Mapper XML 失败 → SqlSessionFactory 创建失败 → 所有 43 个集成测试 ERROR。

---

### F-2: 6 个 Mapper XML 的 INSERT 语句中 Instant 字段缺少 InstantTypeHandler [MINOR]

**严重程度**: MINOR — H2 兼容模式下可能不阻塞，但与项目规范不一致

**规范要求**: 所有 `java.time.Instant` 字段在 INSERT/UPDATE 中必须指定 `typeHandler=com.gien.gits.adapter.persistence.common.typehandler.InstantTypeHandler`

| 文件 | 缺失字段 |
|------|----------|
| `RelationshipReportMapper.xml` | `createdAt`, `updatedAt` |
| `ProductKnowledgeCardMapper.xml` | `createdAt` |
| `BankRelationshipSnapshotMapper.xml` | `createdAt` |
| `FactReconciliationCaseMapper.xml` | `createdAt`, `updatedAt` |
| `CreditFacilityMapper.xml` | `createdAt`, `updatedAt` |
| `TransactionRecordMapper.xml` | `createdAt` |
| `GroupRelationshipMapper.xml` | `createdAt` |

**注意**: `OpportunityMapper.xml` 的 `expectedCloseDate` 是 `String` 类型，不需要 InstantTypeHandler（已排除）。

---

## 验证通过项

| 检查项 | 结果 |
|--------|------|
| 编译 + 单元测试 (persistence-relational -am) | ✅ 19 tests, 0 failures |
| 所有 33 个 Mapper XML 使用 `<constructor>` 模式 | ✅ 无残留 `<result property=...>` |
| PrevisitReportContentMapper productSchemes typeHandler 一致性 | ✅ resultMap 和 INSERT 均使用 ProductSchemeListTypeHandler |
| 其他 `$` 内部类引用 (17 处) | ✅ 全部为真实内部类/枚举 |
| 已有 INSERT 中 InstantTypeHandler 覆盖 | ✅ 大部分 Mapper 已正确添加 |

---

## 退回建议

退回至 Feature Pilot 修复 F-1 (BLOCKER) 和 F-2 (MINOR) 后重新验证。
