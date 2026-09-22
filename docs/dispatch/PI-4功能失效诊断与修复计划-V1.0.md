# PI · 4 个演示功能失效诊断与修复计划 V1.0（2026-09-22）

> 触发：Owner 报「1 新建建议书向导 / 2 产品推荐三段式 / 3 经营旅程访前报告 / 4 企业金融产品中心 8 章」**都无效**，
> 并怀疑「LightRAG 召回没生效」。本文记**实测根因、已修复部分、剩余计划与分域归属**。

## 0. TL 结论（先看这段）

1. **1/2/3 的根因不是数据，是 KERT 侧「服务未运行 + 控制面未供给」** ⇒ 已修复并端到端验证通过（见 §2）；
2. **4 的根因不是 LightRAG**：两仓**都没有** LightRAG 代码实现，且架构明文「LightRAG **不得成为基础闭环新增前置**」；
   实际缺口是 **GITS 侧 7 章硬编码返回空数组** + **KERT 侧尚无 8 章结构化产物**（FAQ 全仓无来源、价格仅「待核定」）；
3. 分域口径（`ONTOLOGY-SPLIT-DESIGN-V2.0-REVIEW.md`）：**产品知识/8 章内容归 KERT（L2）**，GITS 只读消费、
   **不得本地兜底生成结论** ⇒ 8 章的修复必须由 KERT 产出数据、GITS 只接契约。

## 1. 三层根因（每层都已实测）

| 层 | 现象 | 证据 |
|---|---|---|
| **第 0 层 服务/控制面** | 8107 无人监听；起服务后仍 `KERT_PERMISSION_DENIED / ROUTE_POLICY_ABSENT` | GITS `application.yaml:59` 默认 `dsh.base-url=http://127.0.0.1:8107`；KERT 工作区 `bank_front_ws` 无 `.kert_workspace` 标记、无 `90_control/schema/` ⇒ 从未 provision；`RouteResolver` 缺策略**默认 DENY** |
| **第 1 层 调用方入参** | `KERT_CONTEXT_INSUFFICIENT`（SP-15 缺 `needVersionIds`）/ `SKILL_EXECUTION_FAILED`（SP-20 缺 `customerName`,`industry`）/ `exit_policy_no_new_evidence`（访前缺 `evidenceTimestamp`） | KERT `service_proposal.py:166,170-174`；`sp15_skill.py:80-88,248-264`；`skills.py:337-354`。**属契约入参不齐，非 KERT 数据缺口** |
| **第 2 层 真缺陷** | ① SP-20 失败被静默降级成 `200 + SUCCESS 空壳`；② 产品中心 7/8 章恒为空 | `ServiceProposalService.java:166-180`（违其自身端口契约 `ServiceProposalPort.java:9-10`）；`ProductCenterCatalogService.java:209-219`（`List.of()` 硬编码） |

## 2. 已修复并验证（第 0 层）

修复动作在 KERT 侧（零代码改动，工作区为 `.gitignore` 的运行时目录）：
`init_workspace(bank_front_ws, force=True)` + `provision_control_plane(bank_front_ws ← examples/bank-front-knowledge-maps)`
⇒ `policy=RP-KERT-BANKFRONT-001@1.1.0 maps=7 contracts=2`，并起服务于 **8107**。

**GITS 端到端实测（修复后）**：

| 功能 | 结果 |
|---|---|
| 1 建议书草稿 | `POST /api/v14/proposals` → **200 SUCCESS**；真实 8 章草稿 + **86 引文** + 46 未知项 |
| 2 产品推荐三段式 | `POST /api/v1/product-recommendation-runs` → **200**（`AWAITING_HUMAN`）；`/stages` → 资格 **13**、匹配 **13**、组合 **1**、needProfile **3**、冲突 **1** |
| 3 访前报告 | `POST …/journey/{id}/prepare-previsit` → **200**；外联 **13**、会面 **13**、访前 **11**、战卡 **9**、装配轨迹 **14** 步 |

## 3. 剩余修复计划（按优先级）

### P1 · `SP-20` 失败静默降级（**唯一"静默欺骗"型缺陷**，改法最小）

| 文件:行 | 改法 |
|---|---|
| `ServiceProposalService.java:170,178` | `return ServiceProposal.empty()` → `throw new SkillExecutionException(...)`（先判 `result.isOk()`） |
| `adapter/skill/ServiceProposalMapper.java:37,47` | 同步「缺失即失败」，消除空壳兜底 |
| `controller/V14KertIntegrationController.java:49-53` | 新增异常映射：**503**（KERT 不可达）/ **502**（契约不符）+ 统一错误体 |
| `frontend/src/views/ProposalWizardView.vue:77` | 空态文案区分「KERT 返回空结果」vs「失败」（`:76` 错误分支已就绪） |

> 不引入本地兜底、不写权威制品 ⇒ 与 `ServiceProposalPort` 契约、fail-closed 方向一致。

### P2 · 产品中心 8 章（**跨域**，需先定数据契约归属）

**现状（双方）**：GITS `ProductCenterCatalogService.java:209-219` 八章空集合（类注释自述「内容由 PC2–PC4 接入」）；
契约已就绪（`specs/product-center/product-center-api.openapi.json:65,704-726` + `product-center-domain.schema.json:121-273`：
`ProductTerm/ApplicabilityBoundary/Prerequisite/ProcessStep/MaterialGroup/MaterialItem/PricingItem/AgreementClause/SalesBoundary/ComparisonSet/FAQ`）；
KERT 侧**无** 8 章契约与生成器（产品卡是**散文 11 节** + front matter；`04_serve/interpretation` 只硬化 6 个 fieldPath）。

**分域裁决**：8 章内容归 **KERT（L2）** ⇒ 应由 KERT 发布**章节投影**（建议 `04_serve/product-center/PROD-*.json`），
GITS 只按契约消费（新增 `ProductCenterSectionProjectionAdapter` + `GET /products/{id}/sections/{sectionKey}` + 配置项
`gits.product-center.section-dir`）。

**KERT 侧可行性（实测盘点）**：`TERMS/FIT/PROCESS/MATERIALS/COMPARE` **素材在卡中**（需派生为结构化对象）；
`PRICING` 卡内仅「待核定」；**`FAQ` 全仓无来源**（13 张卡均无 FAQ 章节）。
⇒ `FAQ` 与 `PRICING` 属**内容缺口**（需业务/合规供内容），**不得由脚本编造**。

### P3 · 运行参数（不改代码）

后端启动须带：`--gits.product-knowledge.card-dir=<KERT>/03_core`、`--gits.product-knowledge.snapshot-dir=<KERT>/04_serve/interpretation`、
`DSH_BASE_URL=http://127.0.0.1:8107`（`application.yaml:31,33` 默认留空是**有意的 fail-closed**，不建议改默认值）。

## 4. 需 Owner 裁决（**非我可单方决定**）

| # | 事项 | 说明 |
|---|---|---|
| `O-1` | 是否为「产品中心 8 章」新建**跨域数据契约**（KERT 发布章节投影 → GITS 消费） | 属新契约，需明确 KERT Owner/契约版本；GITS 侧新增适配器/端点须回写 CTR |
| `O-2` | `FAQ` / `PRICING` 的**内容来源**（谁写、可否标「待核验」呈现） | 现无来源；按纪律**不得编造** |
| `O-3` | 是否授权把「need/NeedVersion」权威从 GITS 下沉到 KERT | 现契约（`skill-execute-api-contract-vNext.md:104`）把 `needVersionIds` 定为**调用方必填**；下沉属语义升级 |

## 5. 边界与纪律

- 本次**未改任何仓库配置默认值**（保持「未配置即 fail-closed」语义）；运行参数一律启动时注入；
- 本次**未在 GITS 侧自造产品知识**（分域红线：GITS 不得本地兜底生成结论）；
- LightRAG 保持**可关派生层**且**不接线为基础闭环前置**；字段值不得取自检索。
