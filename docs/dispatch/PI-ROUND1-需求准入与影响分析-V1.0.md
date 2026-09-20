# 对公产品中心「产品解读」需求准入与影响分析 V1.0

> 角色：GITS Bank Tech Lead｜工作流：`REQ-PI-01`
> 需求包：`~/dev/gits-kert-docs/dd/GITS_CBanking优化产品解读0920/GITS_Corporate_Product_Rq_V1.0/`（8 文件 / 9 项，含 reference 原型）
> 本文件性质：**开发前只读盘点与计划，不是实现、验收或冻结**
> 门禁状态：`PI-GATE-A = PASS_WITH_REQUIRED_CHANGES`（详见 §3）
> 未声明：需求已冻结 / 页面已验收 / 条款代表真实银行制度 / 生产可用 / 独立 QA 通过 —— **以上均不成立**

---

## 0. 事实基线与声明

### 0.1 代码事实索引新鲜度（GOV-CFI-001）

```text
INDEX_FRESH @ merge 2026-09-15T17:50:17Z (gits 7116904 / kert 64f6f873)
.ua/meta.json  : gitCommitHash=71169042227ce86f870cea81b50f77bf985ffe7f, analyzedAt=2026-09-15T17:48:10Z, files=3318
HEAD           : 71169042227ce86f870cea81b50f77bf985ffe7f  → 提交偏移 = 0，天数差 = 5（阈值 50 / 14）⇒ 无需刷新
```

本文件所有事实陈述均回源到 `文件:行`；索引仅用于定位候选范围，不作为权威。
`specs/`、`modules/`、`adapters/`、`apps/` 本次盘点**未发生写入**，索引仍可代表当前设计全貌。

### 0.2 权威顺序（本次执行口径）

| 序 | 来源 | 本次角色 |
|---|---|---|
| 1 | 用户本轮指令（新增「产品中心」二级菜单；**不改**「产品解读与知识」及其相关代码） | 范围硬约束 |
| 2 | `GITS_Corporate_Product_Rq_V1.0/00–06` 需求包 | 需求权威（`READY_FOR_OWNER_REVIEW`，`FROZEN=NO`） |
| 3 | `reference/法人账户透支_产品解读页面_参考实现.html` | 视觉/交互参考（`PI-EV-002`，`SAMPLE_EVIDENCE`，**禁止直接作为生产代码**） |
| 4 | 本仓 `specs/`（合同 SSOT） | 接口/数据权威 |
| 5 | 本仓既有实现与测试 | 现状事实 |
| — | 真实银行制度/价目/协议模板 | **缺失**（`PI-EV-005 = UNKNOWN`） |

---

## 1. 仓库、分支、HEAD 与工作区事实

### 1.1 三仓事实

| 仓 | 路径 | 分支 | HEAD | 工作区 |
|---|---|---|---|---|
| GITS（主） | `/home/szf/dev/gits-cbanking` | `recover/PI-ARCH-product-catalog` | `7116904`（2026-09-15 15:46） | **182 项未提交**（M/D/?? 混合） |
| KERT | `/home/szf/dev/Leibniz-KERT` | `feature/m7-3-knowledge-map-route` | — | 多文件未提交 |
| 需求包 | `/home/szf/dev/gits-kert-docs` | — | — | `dd/GITS_CBanking优化产品解读0920/` 为新增未跟踪材料 |

证据：`git branch --show-current` / `git rev-parse HEAD` / `git status --short | wc -l` = 182。

### 1.2 工作区未提交内容分类（影响开工）

| 类别 | 示例（显式路径） | 风险 |
|---|---|---|
| 规则/指引 | `.codebuddy/rules/*/RULE.mdc`、`AGENTS.md`、`AI_GUIDE.md`、`Makefile`、`.understandignore` | 与本次无关，**不得**被纳入本 Loop 提交 |
| GK17 Loop 记忆 | `loops/GK17-ontology-unified-map/{STATE.json,EVIDENCE.json,FAILURES.md,memory/*}` | 由 GK17 归属 |
| 前端 e2e | `frontend/e2e/experience-shell.spec.ts`、`frontend/e2e/full-experience.spec.ts` | ⚠ 本需求可能改同文件，**须先确认归属** |
| 前端配置 | `frontend/vite.config.ts` | 由 TL 上一轮演示启动所改（代理目标可环境变量覆盖，默认值未变） |
| 图与制品 | `diagrams/*.html/png`（删除）、`diagrams/activation-contract-into-kert.*`（新增） | 与其他执行者相关 |

> **TL 约束**：本 Loop 全程使用显式路径 `git add`，禁止 `git add .` / `git add -A`（既有另一执行者并发提交的事实见 `docs/dispatch/GK17-ontology-unified-map-长程编排-V1.0.md` 的"跨会话注意"）。

### 1.3 工具链与运行态

| 项 | 实测 |
|---|---|
| Java | `openjdk 21.0.11` |
| Node / npm | `v25.0.0`（`frontend/package.json` engines `>=22`） |
| 前端 UI/构建 | Naive UI 2.44.1、vue 3.5.40、vite 8.2.0、vitest 4.1.10、playwright 1.62.0（`frontend/package.json:29-40`） |
| **无 Tailwind** | `package.json` 无 tailwind 依赖；全仓无 `tailwind.config.*` ⇒ 前端兜底规则中"Tailwind 优先"在本仓**不成立**，样式走 `src/assets/styles/theme.css` + scoped CSS |
| 现网演示实例 | GITS API `127.0.0.1:8088`（H2+seed）、前端 `127.0.0.1:5173`、KERT `127.0.0.1:8106`（TL 上一轮启动，与本 Loop 无因果关系） |
| 端口 | `8080` 被需鉴权的本机代理占用（`{"error":"Unauthorized: missing authentication"}`），**不可假定 8080 空闲** |

### 1.4 邻近分支（潜在冲突）

| 分支 | 内容 | 状态 |
|---|---|---|
| `feature/PI-ARCH-L10-L13` | L10–L13 产品解读链路（DEMO 制度→源版本/片段→证据/断言→冲突/体检→发布包+三视图投影），KERT 先合、GITS 后合 | **未合并**（`docs/pr/PI-ARCH-L10-L13-PR.md:5-8`） |
| `feature/GK-KE-L0-contract` | GK-KE 全程序 L0-2→L6 | 未合并 |
| `recover/PI-ARCH-product-catalog` | 当前分支；名含 product-catalog 但**未见**对应 Loop 目录或派工单（`loops/` 下无 `PI-ARCH*`） | 事实：分支名 ≠ 已交付产品中心 |

---

## 2. 当前「产品解读」实现盘点（逐项带证据）

### 2.1 前端

| 项 | 事实 | 证据 |
|---|---|---|
| 现有二级菜单「产品解读与知识」 | `to:'/product-knowledge/interpretation'`，`domain:'evidence'`，位于一级组「知识与治理」 | `frontend/src/layouts/navConfig.ts:51-55` |
| 该组第二项 | 「审批与审计」→ `/approvals`，`domain:'audit'` | `navConfig.ts:54` |
| 页面 | `ProductInterpretationView.vue`（441 行，pageId `P38`），三视图 Tab：概览/准入/定价 | `frontend/src/router/index.ts:39-43`；`views/ProductInterpretationView.vue:38-61` |
| 页面数据 | `api/productKnowledge.ts`：`GET /cards`、`GET /cards/{id}`、`GET /{id}/interpretation` | `api/productKnowledge.ts:130-159` |
| 硬编码风险 | `KERT_ASSET_ROOT = '/home/szf/dev/Leibniz-KERT/.../03_core'`（绝对路径硬编码）；`FAMILY_ORDER` 硬编码 6 族 | `views/ProductInterpretationView.vue:42,45` |
| 同域第二页 | `/knowledge-map` → `KnowledgeMapView.vue`（pageId 同为 `P38`），走 `api/engagement` 而非 `api/knowledge` | `router/index.ts:135-139`；`views/KnowledgeMapView.vue:6-13` |
| 该页单测 | `ProductInterpretationView` **无单元测试**（`UNKNOWN`）；有 `KnowledgeMapView.spec.ts` | `views/__tests__/` 清单 |
| 壳层导航 | `SHELL_NAV_GROUPS` 4 组；数据驱动渲染；高亮按 `domain` 等值匹配 | `layouts/navConfig.ts:20-57`；`components/shell/AppSidebar.vue:97-119` |
| 壳层副作用 | 侧栏固定 **226px**、header 搜索仅 `router.push('/accounts?q=')`、无 1700px 内容容器 | `layouts/ExperienceShell.vue:41-44,50`；`src/style.css:117`（`.page-container{max-width:1400px}`） |
| 设计令牌 | `theme.css :root` 提供 navy/blue/teal/amber/line/text/radius/space/text 令牌；**无** `--product-*`、无 1700/246/310 | `src/assets/styles/theme.css:7-123` |
| 权限 | 前端只有 API Key（`X-API-KEY`）+ `isAuthenticated`；**无 RBAC/角色/ABAC** | `api/auth.ts:3-28`；`router/index.ts:317-339` |
| 下载/导出 | **无实现**；审计页导出按钮为 `DisabledAction` | `views/AuditTraceView.vue:82-93` |
| 全局搜索 | 仅壳层输入框 → `/accounts?q=`；无独立搜索页/组件 | `ExperienceShell.vue:41-44` |
| AI 助手 | **无前端实现**（仅"AI 提案""AI 内容依据反查"等只读壳文案） | `HumanGateDialog.vue`、`ProposalEvidenceView.vue:22` |
| 产品知识 store | **不存在**；`stores/` 无产品知识 store | `frontend/src/stores/` 清单（9 store） |

### 2.2 后端与合同

| 项 | 事实 | 证据 |
|---|---|---|
| 既有解读 API | `ProductInterpretationController`：`GET /api/v1/product-knowledge`（显式 404）、`/cards`、`/cards/{productId}`、`/{productId}/interpretation` | `apps/api/.../productknowledge/ProductInterpretationController.java:27-30,54,62,70,89` |
| 白名单（收紧点） | `productId` 必须匹配 `^PROD-[A-Z]+-[0-9]{3}$`；`view ∈ {OVERVIEW,ELIGIBILITY,PRICING}`；`purpose ∈ {INTERPRETATION,RECOMMENDATION}` | 同文件 `:33-38` |
| 受控失败矩阵 | 未发布→404 `PRODUCT_KNOWLEDGE_NOT_PUBLISHED`；stale→409 `RELEASE_STALE`；用途不允许→422；源不可达→503 `FAILED_CLOSED` | 同文件 `:109-124,190-212` |
| 字段呈现 | `InterpretedField(fieldPath, value, state, evidence[], conflictId)`；`state=UNKNOWN` 时**清空证据**，`CONFLICT` 保留证据但 value 恒 null | 同文件 `:146-163` |
| 合同 | `CTR-PK-INT-001`（CANDIDATE）→ `specs/product-knowledge/interpretation-api.openapi.json`；`CTR-PK-TAX-001/EVR-001/EVS-002/ASM-001/CNF-001/RLS-001/CHG-001/FLD-001`（均 CANDIDATE） | `specs/CONTRACT_INDEX.yaml:491-639` |
| 产品知识版本 API | `ProductKnowledgeVersionController` 7 个 GET + **1 个 POST 写端点** | `apps/api/.../controller/ProductKnowledgeVersionController.java:26-65` |
| ⚠ 方向冲突 | 解读控制器注释声明"GITS 不得拥有产品卡写接口"（`:23-24`），但同 base path 下存在 POST 创建版本 | 两处对照 |
| 领域对象 | 有 `ProductKnowledgeVersion`（15 字段，**无 status/生效日/复审日/责任岗位**）、`ProductKnowledgeCard`、`Evidence`、`EvidenceVersionLink`、`AuditTraceEntry` | `modules/operational-ontology/.../domain/ProductKnowledgeVersion.java:10-25` |
| Port | `ProductKnowledgeVersionRepository`、`ProductCatalogRepository`、`EvidenceVersionLinkRepository`、`AuditTraceRepository`、`ProductKnowledgeInterpretationPort` | `modules/operational-ontology/.../port/`；`apps/api/.../productknowledge/ProductKnowledgeInterpretationPort.java:12` |
| 持久化 | `product_knowledge_version`（`version_id,product_id,version_number,product_name,category,description,key_features,target_industries,risk_level,required_materials,pricing_basis,previous_version_id,change_summary,changed_by,changed_at`）、`product_catalog`、`evidence_version_link`、`audit_trace` | `adapters/persistence-relational/.../h2/V011__...sql:30-46`、`V004:5-16`、`V013:7-17`、`V015:47-58` |
| 种子 | 对公产品知识 13 条 / 6 族 | `.../h2/V021__corporate_product_knowledge_seed.sql:7-124` |
| 候选未落地 DDL | 12 张 `pk_*` 表（source_document/source_version/fragment/evidence_span/field_assertion/assertion_evidence/conflict_case/review_decision/knowledge_release/release_product/change_event/field_policy）**仅在候选目录** | `specs/product-knowledge/migration-candidates/h2/V023__product_knowledge_objects.sql` |
| 关键字段存在性实测 | `knowledge_as_of` ❌ / `next_review_at` ❌ / `evidence_snapshot` ❌ / `published_version_id` ❌ / `faq` ❌ / `material_group` ❌ / `productFamily` 仅 schema 候选 / `lifecycleState` 仅 KERT 投影适配器 | 全仓 grep（见执行记录） |
| 认证 | `ApiKeyAuthenticationFilter`（`X-API-KEY`，支持轮转）；`SecurityConfig` CORS 白名单 | `apps/api/.../security/ApiKeyAuthenticationFilter.java:31-105`；`config/SecurityConfig.java:41-66` |
| 审计 | `audit_trace` 落库 + `GET /api/v1/audit-trace`；生产装配为 `LoggingAuditLogAdapter`（**仅日志**） | `adapter/persistence/JdbcAuditTraceRepository.java:31-82`；`controller/AuditTraceController.java:25-48`；`config/EngagementConfig.java:114-117` |
| 全局搜索端点 | **不存在**（无 `/search`） | 全仓 `@*Mapping` 检索无匹配 |
| LLM | `LlmClient` Port + `MockLlmClient`/`RealLlmClient`，按 `engagement.llm.mode` 切换；7 处调用点 | `scenario/execute/.../port/LlmClient.java`；`apps/api/.../adapter/llm/MockLlmClient.java:14`；`config/EngagementConfig.java:130-153` |
| 契约合规测试盲区 | `ContractComplianceTest` **不覆盖** product-knowledge / product-recommendation / interpretation-api | `apps/api/src/test/.../contract/ContractComplianceTest.java:49-256` |
| 既有解读测试 | `ProductInterpretationControllerTest`（15+ 用例）、`KertReleaseSnapshotAdapterTest`、`ProductKnowledgeVersionControllerTest/ServiceTest` | `apps/api/src/test/java/com/gien/gits/api/productknowledge/`、`.../controller/`、`.../service/` |

### 2.3 参考原型（`reference/法人账户透支_产品解读页面_参考实现.html`）事实

原型为**单文件可视化封装**（外层 iframe + `data-srcdoc`，2650 行）；`data-srcdoc` 解码后 2437 行 / 94,947 字符。结构实测：

| 项 | 实测 |
|---|---|
| 8 个 `<section>` | `overview, terms, fit, process, materials, pricing, compare, faq`（与需求 8 章一一对应） |
| H1 / H2 | `法人账户透支` / `60 秒读懂这个产品`、`核心条款逐项解释`、`适用边界与前置条件`、`办理流程与每一步产出`、`申请材料清单`、`价格、计息与协议展示`、`同类产品客观比较`、`客户经理常见问题` |
| 左栏目录 | **硬编码 5 族**：账户与支付 12 / 融资与授信 28 / 贸易金融 19 / 资金管理 16 / 跨境与外汇 21，合计"共 96 个已发布产品知识页"；页脚注明"目录数据为 DEMO-BANK 示例" |
| DEMO 证据编号 | 仅 4 个：`DEMO-PM-001`、`DEMO-OP-001`、`DEMO-PRICE-001`、`DEMO-AGR-001` |
| 三栏网格 | `grid-template-columns: 246px minmax(680px,1fr) 310px; max-width:1700px`（原型 `:1615` 附近） |
| 推荐性词汇实测 | `推荐` 3 次 / `适配` 2 次 —— **全部出现在边界声明中**（"不输出客户适配分数或推荐结论""不计算适配度"）；`最低价` 1 次在"× 不应这样承诺"清单内；`评分/星级/排名/胜率/最匹配/秒批/一定通过/立即推荐/加入客户方案/测算适配度` 均 **0 次** |
| 结论 | 原型的**信息架构可继承**；其**硬编码族/计数/DEMO 编号/内联样式不可继承** |

### 2.4 参考原型 vs 当前实现：逐项差异清单

| # | 维度 | 参考原型 | 当前 GITS 实现 | 差异性质 | 处置 |
|---|---|---|---|---|---|
| D-01 | 页面定位 | 独立「企业金融产品中心」，产品为主语 | `P38 产品解读与知识`，产品全景+三视图 | **架构差异** | 新建「产品中心」页；P38 保持不动（本轮硬约束） |
| D-02 | 页面区域数 | 8 章 + 环境条 + 目录 + 右栏治理 | 3 Tab（概览/准入/定价）+ 列表 | 缺失 | Loop 1–4 新建 |
| D-03 | 目录 | 5 族、族内产品、计数、当前选中 | `FAMILY_ORDER` 硬编码 6 族 + 卡片列表 | 冲突 | 需 Owner 定分类法（`OD-PI-04`） |
| D-04 | 产品族命名 | 账户与支付/融资与授信/贸易金融/资金管理/跨境与外汇 | `流动资金融资/贸易融资/结算服务/现金管理/跨境金融/投资银行`（`ProductInterpretationView.vue:45`）与 `CTR-PK-TAX-001` | **冲突** | `PI-OI-002` 升级为开发前 MAJOR |
| D-05 | 产品编号 | 无编号（DEMO 目录） | 后端强制 `^PROD-[A-Z]+-[0-9]{3}$` | 冲突 | 需求 03 §3.2 要求 DEMO 用 `DEMO-*` 前缀 ⇒ 需合同决策（`OD-PI-05`） |
| D-06 | 条款表 | 4 列：字段/口径/如何解释/状态+证据 | 字段级 `fieldPath` + `state(5态)` + 证据摘要 | 部分可复用 | 复用证据回链机制，新增条款对象 |
| D-07 | 确定性状态 | 6 态：已核验/待核验/审批变量/价格变量/冲突/已失效 | 5 态：`SUPPORTED/UNKNOWN/CONFLICT/STALE/NOT_APPLICABLE` | **语义冲突** | `OD-PI-03` 需枚举映射决策 |
| D-08 | 右栏治理 | 版本/完整度/证据/助手/边界 5 块 | 无右栏 | 缺失 | Loop 4–5 新建 |
| D-09 | 搜索 | 头部全局搜索（对象类型区分） | 壳层搜索仅跳转客户列表 | 缺失 | Loop 1 新建（后端需新端点） |
| D-10 | 视觉令牌 | `--product-*` 16 个（蓝 `#0D5FA8` / 青绿 `#078477` / 琥珀 `#B66A00` / 红 `#B33C3C`） | `--gits-*`（蓝 `#1976d2` / 青绿 `#12a7a0` / 琥珀 `#f2b84b`） | **令牌不一致** | 映射到现有设计系统，不新增重复 Token（`02` §8.4） |
| D-11 | 尺寸 | 1700 / 246 / 310 / 13–14px 圆角 / 正文≥12px | 1400 容器 / 侧栏 226 / 圆角 4–16 | 缺失 | 新增页面级布局令牌，不改编全局壳层（避免影响 P30–P37 验收） |
| D-12 | 响应式 | 1680/1440/1280 三档 + <1180 抽屉 | 壳层无该三档基线 | 缺失 | Loop 1 建立基线 |
| D-13 | DEMO 隔离 | 页面级醒目 DEMO（顶部+页脚） | 后端有 `.DEMO.md` 三道闸（L10 决策）；前端无环境条 | 部分存在 | Loop 1/6 补齐前端层 |
| D-14 | 证据编号 | `DEMO-PM/OP/PRICE/AGR-001` | KERT 侧 `DEMO-*` 三类闸 + 4 个公开轨证据未参与 | 可映射 | Loop 0 定映射表 |
| D-15 | 数据来源 | 内联硬编码 | KERT Release 投影（`RLS-2026.09.06.1`）+ GITS `product_knowledge_version` 13 条 | 双源 | Loop 0 定唯一权威源（`PI-OI-001/004`） |

---

## 3. 需求包准入结论（Gate A）

```text
PI-GATE-A = PASS_WITH_REQUIRED_CHANGES
```

**通过依据**：
1. 需求包结构完整：12 BR / 95 FR / 12 NFR / 86 AT，ID 可追踪（`04` §1–§4）；
2. 业务边界明确且与既有"客户上下文"体系物理隔离（`01` §3.2 `PI-BR-001~012`）；
3. 参考原型可解码、可复现，与 8 章需求一一对应（§2.3 实测）；
4. 未要求破坏既有 GITS↔DKES 契约（`06` §3 明确"原则上保持不变，必要变化需单独变更申请"）。

**必须变更（不阻塞只读盘点，阻塞 Loop 1 之后）**：
| 编号 | 事项 | 门禁级别 |
|---|---|---|
| `PI-OI-002` | 产品目录是否沿用受控分类法（不得硬编码 5 族） | 开发前 MAJOR |
| `PI-OI-003` | GITS↔DKES 是否已有产品/版本/证据对象（**现状：部分有**，见 §2.2） | 开发前 MAJOR |
| `PI-OI-011` | 地区/机构/币种 Scope 呈现方式 | 开发前 MAJOR |
| `PI-OI-014` | 搜索是否返回证据正文片段 | 开发前 MAJOR |
| `PI-OI-001/015` | 生产权威来源+责任组织 / DEMO 生产隔离 | **上线 BLOCKER** |
| `PI-OI-004/006/009/010` | 证据正文承载 / 历史版本开放度 / 助手模型检索 / 比较审批责任人 | Loop 4–5 前 MAJOR |

**准入结论**：TL 可继续 Loop 0（基线与契约），**不得**进入 Loop 1 及之后的编码，直到上述 4 项"开发前 MAJOR"有结论或受控假设被 Owner 书面接受。

---

## 4. `PI-FR-001`—`PI-FR-095` 需求覆盖矩阵

状态仅用受控枚举：`NOT_ASSESSED` / `EXISTING_AND_COMPLIANT` / `EXISTING_NEEDS_CHANGE` / `MISSING` / `BLOCKED`。
（本轮为开发前盘点，"新建页面"类需求统一记 `MISSING`；已有可复用实现记 `EXISTING_NEEDS_CHANGE`；受 Owner 决策阻塞记 `BLOCKED`。）

权限列缩写：`V`=查看 · `E`=证据 · `$`=价格敏感 · `H`=历史版本 · `D`=下载/导出 · `A`=助手。
审计列引用 `03` §7 事件名。

### 4.1 环境条与全局头部（`PI-FR-001`—`008`，AT 001–005）

| FR | 要点 | 区域 | 前端组件 | 后端接口 | 数据对象 | 权限 | 审计 | 状态 | 缺口/冲突 |
|---|---|---|---|---|---|---|---|---|---|
| 001 | DEMO/UAT/PROD 环境标识（持续可见） | 环境条+页脚 | *EnvBanner | 新 | ProductKnowledgeVersion.environment | V | — | MISSING | 枚举 `environment`/`is_demo` 字段不存在 |
| 002 | 知识基准日来自版本字段 | 环境条 | *EnvBanner | 新 | `knowledge_as_of` | V | — | MISSING | 字段全仓不存在 ⇒ 不得用系统日期冒充 |
| 003 | DEMO 不代表真实制度（滚动后仍可见） | 环境条+页脚 | *EnvBanner/*PageFooter | 新 | `is_demo` | V | — | MISSING | 需与 L10 `.DEMO.md` 三道闸对齐 |
| 004 | 模块品牌"企业金融产品中心" | 头部 | *ProductHeader | 配置 | ModuleConfig | V | — | MISSING | 壳层品牌为"对公客户经营工作台"（`AppSidebar.vue:81-83`），页内须自带 |
| 005 | 全局产品知识搜索（5 类范围） | 头部 | *GlobalSearch | **新端点** | Product/Term/Material/Process/Evidence | V | — | BLOCKED | 后端无 `/search`；`PI-OI-014` |
| 006 | 结果区分对象类型+命中字段 | 头部 | *GlobalSearch | 新 | 同上 | V | — | MISSING | 同上 |
| 007 | 用户身份/机构/岗位 | 头部 | *ProductHeader | 统一身份（依赖） | UserContext | V | — | BLOCKED | 无统一身份服务；`01` §11 列为依赖假设 |
| 008 | 帮助入口（产品中心说明） | 头部 | *ProductHeader | 静态文档 | HelpDoc | V | — | MISSING | 壳层有帮助入口但目标未回源确认 |

### 4.2 左侧产品目录（`PI-FR-009`—`014`，AT 006–010）

| FR | 要点 | 区域 | 前端组件 | 后端接口 | 数据对象 | 权限 | 审计 | 状态 | 缺口/冲突 |
|---|---|---|---|---|---|---|---|---|---|
| 009 | 产品族分层（≥5 族，缺失进"待归类"） | 左栏 | ProductCatalog | 改 `/cards` | ProductFamily/Product | V | — | EXISTING_NEEDS_CHANGE | `FAMILY_ORDER` 硬编码（`:45`）；族分类法冲突 D-04 |
| 010 | 族内可见产品数（权限+有效版本过滤） | 左栏 | ProductCatalog | 改 `/cards` | `active_product_count` | V | — | EXISTING_NEEDS_CHANGE | 现 `/cards` 无计数、无过滤 |
| 011 | 展开/收起 + 会话记忆 | 左栏 | ProductCatalog | — | SessionState | V | — | MISSING | — |
| 012 | 当前产品 active（URL 为准并纠正） | 左栏 | ProductCatalog | — | route | V | — | EXISTING_NEEDS_CHANGE | 现有 `selectedId` 未与 URL 同步（`:111`） |
| 013 | 切换产品；无有效版本态 | 左栏 | ProductCatalog | 改 `/cards` | Version | V | `PRODUCT_VIEWED` | EXISTING_NEEDS_CHANGE | 无"暂无有效版本"分支 |
| 014 | 目录权限过滤（不泄漏名称/数量/片段） | 左栏 | ProductCatalog | **服务端 RBAC** | AccessPolicy | V | — | BLOCKED | 现仅 API Key 无 RBAC（`ApiKeyAuthenticationFilter.java:31`）；`PI-OI-014` |

### 4.3 面包屑、首屏与操作（`PI-FR-015`—`025`，AT 011–017）

| FR | 要点 | 区域 | 前端组件 | 后端接口 | 数据对象 | 权限 | 审计 | 状态 | 缺口/冲突 |
|---|---|---|---|---|---|---|---|---|---|
| 015 | 面包屑（中心/族/产品） | 首屏 | ProductHero | 改 `/cards/{id}` | ProductFamily | V | — | MISSING | — |
| 016 | 名称+唯一编号（缺号显示待维护） | 首屏 | ProductHero | `/cards/{id}` | `product_code` | V | — | EXISTING_NEEDS_CHANGE | 强制 `PROD-XX-NNN` 与 `DEMO-*` 冲突 D-05 |
| 017 | 副标题（禁推荐语言） | 首屏 | ProductHero | 改 | ProductSummary | V | — | MISSING | — |
| 018 | 发布状态（受控状态样式） | 首屏 | ProductHero | 改 | `version_status` | V | — | EXISTING_NEEDS_CHANGE | GITS 版本对象无 status；仅 KERT 投影 `lifecycleState`（`ProductInterpretationController.java:109`） |
| 019 | 产品标签（可作筛选） | 首屏 | ProductHero | 改 | ProductTag | V | — | MISSING | — |
| 020 | 收藏（幂等，不改版本） | 首屏 | ProductHero | **新端点** | Favorite | V | `FAVORITE_CHANGED` | MISSING | 无收藏存储/端点 |
| 021 | 下载内部说明（带版本水印） | 首屏 | ProductHero | **新端点** | DownloadFile | V+D | `INTERNAL_NOTE_DOWNLOADED` | MISSING | 全前端无下载实现 |
| 022 | 生成客观讲解提纲（含边界+证据） | 首屏 | ProductHero | **新端点** | Outline | V+A | `OUTLINE_GENERATED` | MISSING | 依赖 `PI-OI-008` |
| 023 | 产品目的摘要（无客户痛点） | 首屏 | ProductHero | 改 | `product_purpose` | V | — | MISSING | — |
| 024 | 使用方式与计息口径摘要（与条款同源） | 首屏 | ProductHero | 改 | `usage_mode`/`interest_summary` | V+$ | — | EXISTING_NEEDS_CHANGE | 现仅 `pricingBasis` 单字段（`V011:30-46`） |
| 025 | 适用主体摘要（保留"符合准入与授信条件"） | 首屏 | ProductHero | 改 | `eligible_entity_summary` | V | — | MISSING | — |

### 4.4 页内章节导航（`PI-FR-026`—`029`，AT 018–020）

| FR | 要点 | 区域 | 前端组件 | 后端接口 | 数据对象 | 权限 | 审计 | 状态 | 缺口/冲突 |
|---|---|---|---|---|---|---|---|---|---|
| 026 | 8 章节入口固定顺序（无数据也保留） | 导航 | ProductSectionNav | — | SectionConfig | V | — | MISSING | — |
| 027 | 平滑定位（避让吸顶高度） | 导航 | ProductSectionNav | — | — | V | — | MISSING | — |
| 028 | 滚动同步激活 + 位置恢复 | 导航 | ProductSectionNav | — | SessionState | V | — | MISSING | 可复用 `stores/pageReference.ts` 的 scroll 捕获 |
| 029 | 深链接（产品+版本+锚点，不绕权限） | 导航 | router | 改 | route | V+H | `VERSION_HISTORY_VIEWED` | MISSING | 需新路由 + 权限校验 |

### 4.5 60 秒读懂（`PI-FR-030`—`036`，AT 021–024）

| FR | 要点 | 区域 | 前端组件 | 后端接口 | 数据对象 | 权限 | 审计 | 状态 | 缺口/冲突 |
|---|---|---|---|---|---|---|---|---|---|
| 030 | 一句话定义（主体+机制+目的+条件） | 正文① | ProductOverview | 新 | `one_sentence_definition` | V | — | MISSING | ProductSummary 不存在 |
| 031 | 定义边界补充（额度/期限/利率/担保以批复协议为准） | 正文① | ProductOverview | 新 | `boundary_statement` | V | — | MISSING | 不得放 tooltip |
| 032 | 核心机制列表（每条可回链条款） | 正文① | ProductOverview | 新 | `mechanisms[]` | V | — | MISSING | — |
| 033 | "解决什么"（禁客户数据） | 正文① | ProductOverview | 新 | `solves` | V | — | MISSING | — |
| 034 | "它不是什么"（含非无条件余额） | 正文① | ProductOverview | 新 | `is_not` | V | — | MISSING | — |
| 035 | 直观区别（不生成推荐） | 正文① | ProductOverview | 新 | `nearest_difference` | V | — | MISSING | — |
| 036 | 本章证据摘要（失效则阻断发布） | 正文① | ProductOverview | 新 | EvidenceRef | V+E | `EVIDENCE_OPENED` | MISSING | 可复用证据回链机制 |

### 4.6 核心条款（`PI-FR-037`—`043`，AT 025–030）

| FR | 要点 | 区域 | 前端组件 | 后端接口 | 数据对象 | 权限 | 审计 | 状态 | 缺口/冲突 |
|---|---|---|---|---|---|---|---|---|---|
| 037 | 4 列表格（字段/口径/如何解释/状态+证据） | 正文② | ProductTermsTable | 新 | ProductTerm | V+E | — | MISSING | — |
| 038 | 8 关键字段（对象/用途/额度/额度期限/支用/计息/归还/担保） | 正文② | ProductTermsTable | 新 | `term_key` 受控枚举 | V | — | MISSING | 现有 `fieldPath`（如 `identity.productCode`）非条款语义 |
| 039 | 6 态确定性状态（文字+颜色） | 正文② | ProductTermsTable | 改 | `certainty_type` | V | — | EXISTING_NEEDS_CHANGE | **枚举冲突 D-07**：现 5 态 `KnowledgeState`（`api/productKnowledge.ts:6-13`） |
| 040 | 客户经理解释口径 | 正文② | ProductTermsTable | 新 | `explanation_for_rm` | V | — | MISSING | — |
| 041 | 证据回链（无权时只给元数据） | 正文② | ProductEvidencePanel | 复用 | EvidenceRef | V+E | `EVIDENCE_OPENED` | EXISTING_NEEDS_CHANGE | 现 `EvidenceSummary`（`Controller.java:147-151`）可复用 |
| 042 | 条款版本差异对比 | 正文② | ProductTermsTable | 新 | VersionDiff | V+H | `VERSION_HISTORY_VIEWED` | MISSING | 无 diff 能力 |
| 043 | 冲突发布阻断（AI 不裁决） | 正文② | ProductTermsTable | 改 | ConflictCase | V | — | EXISTING_NEEDS_CHANGE | `ConflictCase` schema 存在（`CTR-PK-CNF-001`），`conflictId` 已呈现；发布阻断流程无 |

### 4.7 适用边界与前置条件（`PI-FR-044`—`049`，AT 031–034）

| FR | 要点 | 区域 | 前端组件 | 后端接口 | 数据对象 | 权限 | 审计 | 状态 | 缺口/冲突 |
|---|---|---|---|---|---|---|---|---|---|
| 044 | 典型适用场景（不含客户） | 正文③ | ProductFitBoundary | 新 | ApplicabilityBoundary(`TYPICAL_USE`) | V | — | MISSING | — |
| 045 | 通常不适用/禁止用途 | 正文③ | ProductFitBoundary | 新 | `NOT_SUITABLE`/`PROHIBITED_USE` | V | — | MISSING | — |
| 046 | 账户前提 | 正文③ | ProductFitBoundary | 新 | Prerequisite(`ACCOUNT`) | V | — | MISSING | — |
| 047 | 授信前提（不写成审批通过） | 正文③ | ProductFitBoundary | 新 | Prerequisite(`CREDIT`) | V | — | MISSING | — |
| 048 | 合同前提（条件性标"如适用"） | 正文③ | ProductFitBoundary | 新 | Prerequisite(`CONTRACT`) | V | — | MISSING | — |
| 049 | 固定声明"边界≠客户适配结论"（不可删） | 正文③ | ProductFitBoundary | 契约常量 | BoundaryConfig | V | — | MISSING | 声明缺失须阻断发布 |

### 4.8 办理流程（`PI-FR-050`—`054`，AT 035–038）

| FR | 要点 | 区域 | 前端组件 | 后端接口 | 数据对象 | 权限 | 审计 | 状态 | 缺口/冲突 |
|---|---|---|---|---|---|---|---|---|---|
| 050 | 有序步骤（6 步可配置，含角色/输入/产出） | 正文④ | ProductProcessFlow | 新 | ProcessStep | V | — | MISSING | — |
| 051 | 默认 6 步正常路径 | 正文④ | ProductProcessFlow | 新 | ProcessStep | V | — | MISSING | — |
| 052 | 补件/驳回/条件未落实可展开 | 正文④ | ProductProcessFlow | 新 | `exceptions[]` | V | — | MISSING | — |
| 053 | 每步责任边界（审批不归 AI） | 正文④ | ProductProcessFlow | 新 | `actors`/`human_decision_required` | V | — | MISSING | — |
| 054 | 不承诺时效（说明影响因素） | 正文④ | ProductProcessFlow | 新 | `sla_reference`（无依据不展示） | V | — | MISSING | 原型含"不承诺时效"提醒条 |

### 4.9 申请材料（`PI-FR-055`—`059`，AT 039–043）

| FR | 要点 | 区域 | 前端组件 | 后端接口 | 数据对象 | 权限 | 审计 | 状态 | 缺口/冲突 |
|---|---|---|---|---|---|---|---|---|---|
| 055 | 三组材料（基础/经营交易/条件性）+数量 | 正文⑤ | ProductMaterialGroups | 新 | MaterialGroup | V | — | MISSING | 现仅 `requiredMaterials` 字符串列表（`V011:30-46`） |
| 056 | 材料字段（用途/必填性/条件/有效期/模板） | 正文⑤ | ProductMaterialGroups | 新 | MaterialItem | V | — | MISSING | — |
| 057 | 机构/地区/主体差异 Scope | 正文⑤ | ProductMaterialGroups | 新 | `scope` | V | — | BLOCKED | `PI-OI-011` |
| 058 | 下载模板/查看脱敏样例（带版本+哈希） | 正文⑤ | ProductMaterialGroups | **新端点** | FileRef | V+D | `INTERNAL_NOTE_DOWNLOADED` | MISSING | 无文件服务 |
| 059 | 固定"非穷尽清单"边界 | 正文⑤ | ProductMaterialGroups | 契约常量 | BoundaryConfig | V | — | MISSING | — |

### 4.10 价格、计息与协议（`PI-FR-060`—`068`，AT 044–051）

| FR | 要点 | 区域 | 前端组件 | 后端接口 | 数据对象 | 权限 | 审计 | 状态 | 缺口/冲突 |
|---|---|---|---|---|---|---|---|---|---|
| 060 | 价格构成（利率/基数/结息/费用/逾期挪用） | 正文⑥ | ProductPricingAgreement | 新 | PricingItem | V+$ | — | EXISTING_NEEDS_CHANGE | 现 `pricingBasis` 单字段 |
| 061 | 价格决定因素（不含自动推导报价） | 正文⑥ | ProductPricingAgreement | 新 | `determining_factors` | V+$ | — | MISSING | — |
| 062 | 计息公式语义解释 | 正文⑥ | ProductPricingAgreement | 新 | PricingItem(`INTEREST_BASE`) | V+$ | — | MISSING | — |
| 063 | 其他费用（无数据显"未配置"非"免费"） | 正文⑥ | ProductPricingAgreement | 新 | PricingItem(`FEE`) | V+$ | — | MISSING | AT-045 强约束 |
| 064 | 协议关键落点（条款号可定位） | 正文⑥ | ProductPricingAgreement | 新 | AgreementClause | V+E | `EVIDENCE_OPENED` | MISSING | — |
| 065 | "可以这样解释"话术（绑版本+证据） | 正文⑥ | ProductPricingAgreement | 新 | SalesBoundary(`ALLOWED`) | V | — | MISSING | — |
| 066 | "不应这样承诺"（≥5 类，不可折叠） | 正文⑥ | ProductPricingAgreement | 新 | SalesBoundary(`PROHIBITED`) | V | — | MISSING | 原型已含 4 类示例 |
| 067 | 价格三级权限（前端隐藏不算） | 正文⑥ | ProductPricingAgreement | **服务端 RBAC** | `disclosure_level` | V+$/E | — | BLOCKED | 现仅 API Key；AT-050/069 |
| 068 | 证据失效联动（限制生成/发布） | 正文⑥ | ProductPricingAgreement | 改 | EvidenceRef(`EXPIRED`) | V | — | EXISTING_NEEDS_CHANGE | KERT stale→409 机制可复用（`Controller.java:115-118`） |

### 4.11 同类产品比较（`PI-FR-069`—`073`，AT 052–055）

| FR | 要点 | 区域 | 前端组件 | 后端接口 | 数据对象 | 权限 | 审计 | 状态 | 缺口/冲突 |
|---|---|---|---|---|---|---|---|---|---|
| 069 | 同族/邻近产品比较（配置并审核） | 正文⑦ | ProductComparison | 新 | ComparisonSet | V | — | MISSING | — |
| 070 | 统一 6 维度（缺值显示待维护） | 正文⑦ | ProductComparison | 新 | ComparisonDimension | V | — | MISSING | — |
| 071 | 当前产品仅浅色识别（禁奖牌/星级） | 正文⑦ | ProductComparison | — | — | V | — | MISSING | — |
| 072 | 比较内容绑版本 + 基准日 | 正文⑦ | ProductComparison | 新 | `comparison_as_of` | V+H | — | MISSING | — |
| 073 | 禁推荐性计算（DOM/API 均不得偷返） | 正文⑦ | ProductComparison | 门禁断言 | 禁字段清单 | V | — | MISSING | 需负例测试：`recommendation_score/fit_score/ranking/win_rate/next_best_action` |

### 4.12 常见问题（`PI-FR-074`—`077`，AT 056–058）

| FR | 要点 | 区域 | 前端组件 | 后端接口 | 数据对象 | 权限 | 审计 | 状态 | 缺口/冲突 |
|---|---|---|---|---|---|---|---|---|---|
| 074 | FAQ 折叠（键盘可操作） | 正文⑧ | ProductFAQ | 新 | FAQ | V | — | MISSING | — |
| 075 | 覆盖 6 类高频误解 | 正文⑧ | ProductFAQ | 新 | FAQ.`risk_level` | V | — | MISSING | — |
| 076 | 答案受证据约束 + 变更触发复审 | 正文⑧ | ProductFAQ | 改 | FAQ+EvidenceRef | V+E | `EVIDENCE_OPENED` | MISSING | 需复审联动 |
| 077 | 问题反馈（进治理任务不改答案） | 正文⑧ | ProductFAQ | **新端点** | Feedback | V | `KNOWLEDGE_FEEDBACK_CREATED` | MISSING | — |

### 4.13 右侧知识治理（`PI-FR-078`—`085`，AT 059–065）

| FR | 要点 | 区域 | 前端组件 | 后端接口 | 数据对象 | 权限 | 审计 | 状态 | 缺口/冲突 |
|---|---|---|---|---|---|---|---|---|---|
| 078 | 版本号+发布状态（非构建号） | 右栏 | ProductVersionPanel | 复用+改 | Version | V | — | EXISTING_NEEDS_CHANGE | `versionNumber` 有（`ProductKnowledgeVersion.java:10-25`），状态无 |
| 079 | 产品归属与知识责任人（失效告警） | 右栏 | ProductVersionPanel | 新 | `owner` | V | — | EXISTING_NEEDS_CHANGE | 仅 `changedBy`，无责任岗位 |
| 080 | 审核状态（须有审核记录） | 右栏 | ProductVersionPanel | 新 | `review_record_id` | V | — | MISSING | AT-060：无记录不得显示已审核 |
| 081 | 下次复审日期（临近/逾期分级） | 右栏 | ProductVersionPanel | 新 | `next_review_at` | V | — | MISSING | 字段全仓不存在 |
| 082 | 知识完整度（可解释规则+缺口明细） | 右栏 | ProductVersionPanel | 新 | Coverage | V | — | EXISTING_NEEDS_CHANGE | L12"七字段体检"可作起点，规则需重定 |
| 083 | 制度与证据列表（无权只给元数据） | 右栏 | ProductEvidencePanel | 复用+改 | EvidenceRef | V+E | `EVIDENCE_OPENED` | EXISTING_NEEDS_CHANGE | `EvidenceVersionLink` + `/evidences/{id}/versions` 可复用 |
| 084 | 证据定位（失败给原因+维护入口） | 右栏 | ProductEvidencePanel | 复用 | `locatorHint`/`anchor` | V+E | `EVIDENCE_OPENED` | EXISTING_NEEDS_CHANGE | 现 `locatorHint`（`Controller.java:149`）为提示非定位 |
| 085 | 历史版本（只读，不冒充当前） | 右栏 | ProductVersionPanel | 复用+改 | Version+`previousVersionId` | V+H | `VERSION_HISTORY_VIEWED` | EXISTING_NEEDS_CHANGE | `GET /products/versions`（`openapi:1151-1173`）可复用 |

### 4.14 产品知识助手（`PI-FR-086`—`092`，AT 066–072）

| FR | 要点 | 区域 | 前端组件 | 后端接口 | 数据对象 | 权限 | 审计 | 状态 | 缺口/冲突 |
|---|---|---|---|---|---|---|---|---|---|
| 086 | 仅答当前产品+当前发布版本 | 右栏 | ProductKnowledgeAssistant | **新端点** | AssistantQuery | V+A | `ASSISTANT_ASKED` | MISSING | 可复用 `LlmClient`（`MockLlmClient.java:14`） |
| 087 | 每个实质回答附证据引用 | 右栏 | ProductKnowledgeAssistant | 新 | Citation | V+A+E | `ASSISTANT_ASKED` | MISSING | 无证据须明确"未找到依据" |
| 088 | 快捷问题（由版本配置，无推荐问题） | 右栏 | ProductKnowledgeAssistant | 新 | IngestedQuestion | V+A | — | MISSING | — |
| 089 | 权限继承（≤ 直接浏览权限，防提示注入） | 右栏 | ProductKnowledgeAssistant | 服务端过滤 | AccessPolicy | V+A+$ | — | BLOCKED | 依赖 `PI-OI-009` + RBAC |
| 090 | 明示边界（不可配置关闭） | 右栏 | ProductKnowledgeAssistant | 契约常量 | BoundaryConfig | V | — | MISSING | — |
| 091 | 助手审计（版本/问题/引用/模型/结果） | 右栏 | ProductKnowledgeAssistant | 改 | AuditEvent | V+A | `ASSISTANT_ASKED` | EXISTING_NEEDS_CHANGE | `audit_trace` 可承载，事件类型需扩展 |
| 092 | 高风险问题转人工/制度（可承诺答案） | 右栏 | ProductKnowledgeAssistant | 新 | Handoff | V+A | `ASSISTANT_ASKED` | MISSING | AT-068 强约束 |

### 4.15 页脚与页面边界（`PI-FR-093`—`095`，AT 073–075）

| FR | 要点 | 区域 | 前端组件 | 后端接口 | 数据对象 | 权限 | 审计 | 状态 | 缺口/冲突 |
|---|---|---|---|---|---|---|---|---|---|
| 093 | 页脚重复环境与数据声明 | 页脚 | *PageFooter | 配置 | Environment | V | — | MISSING | 与顶部一致 |
| 094 | 业务链位置（无推荐 CTA） | 页脚 | *PageFooter | 静态 | BoundaryConfig | V | — | MISSING | — |
| 095 | 固定非推荐边界（不可 CSS/配置隐藏） | 页脚 | *PageFooter | 契约常量 | BoundaryConfig | V | — | MISSING | 需负例测试：不可被隐藏 |

### 4.16 非功能（`PI-NFR-001`—`012`，AT 076–086）

| NFR | 要求 | 状态 | 缺口/证据计划 |
|---|---|---|---|
| 001 | 首屏 P95≤2.5s / 全量≤4s / 搜索≤2s | NOT_ASSESSED | Loop 6 压测并留基线差异 |
| 002 | 核心静态知识不依赖 AI | EXISTING_NEEDS_CHANGE | 已有 fail-closed 传统（`Controller.java:202-212`），需页面级降级 |
| 003 | 首屏/条款/价格/FAQ/导出同版本 | MISSING | 需 `published_version_id` 贯穿（AT-078） |
| 004 | 服务端 RBAC/ABAC + 证据级权限 | BLOCKED | 现仅 API Key（`SecurityConfig.java:41-66`） |
| 005 | 审计可按用户/产品/版本/事件查询导出 | EXISTING_NEEDS_CHANGE | `JdbcAuditTraceRepository` 查询方法已有（`:56-82`），字段与导出缺 |
| 006 | 键盘可达 + WCAG 2.1 AA | NOT_ASSESSED | Loop 6 检查清单 |
| 007 | 1280 可用 / <1180 受控折叠 | MISSING | Loop 1 建立三档基线 |
| 008 | Chrome/Edge 企业版基线 | NOT_ASSESSED | Loop 6 |
| 009 | 区块组件化，字段/顺序/枚举受控 | MISSING | §7 组件边界 |
| 010 | 错误/定位失败/冲突/无引用/生成失败有指标与 trace | MISSING | 需 traceId 统一 |
| 011 | 发布后 SLA 内缓存失效，不并存两个当前版本 | MISSING | AT-078 |
| 012 | 状态文字化（不仅颜色） | MISSING | 视觉验收项 |

### 4.17 覆盖统计

| 状态 | 数量 | 占比 |
|---|---:|---:|
| `MISSING` | 65 | 68.4% |
| `EXISTING_NEEDS_CHANGE` | 17 | 17.9% |
| `BLOCKED` | 7 | 7.4% |
| `NOT_ASSESSED`（仅 NFR） | 4 | 4.2% |
| `EXISTING_AND_COMPLIANT` | 0 | 0% |
| **合计** | **95** | 100% |

> **关键结论**：现有实现**没有任何一项 FR 可判 `EXISTING_AND_COMPLIANT`**。P38 是"产品全景+三视图只读"，与"产品中心八章解读"是**两个不同产品形态**，不可简单改造冒充。

---

## 5. 组件、接口、数据、权限与测试影响图

### 5.1 组件影响图（前端）

```text
前端影响面
├─【必须新增·不得触碰既有 P38】
│   ├─ layouts/navConfig.ts          ── 追加 1 个 item（「产品中心」），不修改「产品解读与知识」行
│   ├─ router/index.ts               ── 追加新路由（如 /product-center/:productId?），不动 P38 路由
│   ├─ views/ProductCenterView.vue   ── 新页面壳（三栏 + 环境条 + 吸顶）
│   ├─ components/product-center/    ── 15 组件（见 §7）
│   ├─ stores/productCenter.ts       ── 新 store（当前产品/版本/章节/收藏）
│   └─ api/productCenter.ts          ── 新 API 模块（新 baseURL 或复用 /api/v1/product-knowledge）
│
├─【必须修改·共享件（风险点）】
│   ├─ components/shell/AppSidebar.vue ── 仅因新增 item 自动多渲染一项（逻辑无需改）
│   ├─ layouts/navConfig.ts:6          ── ShellNavItem.domain 联合类型需 +1 值
│   ├─ layouts/navConfig.ts:61-84      ── navDomainForPath 需 +1 分支（不改现有分支）
│   └─ components/shell/__tests__/AppSidebar.spec.ts:62 ── `toHaveLength(12)` 断言必须改 → 13
│
└─【禁止触碰（本轮硬约束）】
    ├─ views/ProductInterpretationView.vue           （P38 页）
    ├─ api/productKnowledge.ts                       （P38 数据层）
    ├─ router /product-knowledge/interpretation 与 /knowledge-map
    └─ components/shell/__tests__ 中 P38 相关断言
```

> **最小改动面**：新增菜单只要求 `navConfig.ts` **追加**、`router` **追加**、一个新 store、一个新 API 模块、一个测试断言更新（12→13）。**不需要**修改 P38 任何文件。
> **必须避免的陷阱**：新 item 若复用 `domain:'evidence'`，会与「产品解读与知识」**同时高亮**（`AppSidebar.vue:109` 为等值匹配）⇒ 必须新增独立 domain（如 `product-center`），并同步 `navDomainForPath`。

### 5.2 接口影响图（后端）

```text
后端影响面
├─【可复用（不改语义）】
│   ├─ GET /api/v1/product-knowledge/cards            产品卡目录（KERT 只读）
│   ├─ GET /api/v1/product-knowledge/cards/{id}       产品卡详情
│   ├─ GET /api/v1/product-knowledge/{id}/interpretation  三视图 + 证据回链
│   ├─ GET /api/v1/products/versions                  版本查询
│   ├─ GET /api/v1/evidences/{id}/versions            证据版本链
│   ├─ GET /api/v1/audit-trace                        审计查询
│   └─ LlmClient / MockLlmClient / RealLlmClient      LLM 出口
│
├─【需新增（合同先行）】
│   ├─ 产品族目录（含权限与有效版本过滤 + 计数）      GET  /api/v1/product-center/families
│   ├─ 产品中心详情（8 章一次性或分章）               GET  /api/v1/product-center/{productId}
│   ├─ 章节分片加载（支持单章失败）                   GET  /api/v1/product-center/{productId}/sections/{key}
│   ├─ 全局产品知识搜索                               GET  /api/v1/product-center/search?q=
│   ├─ 收藏（幂等）                                   PUT/DELETE /api/v1/product-center/{productId}/favorite
│   ├─ 内部说明下载                                   GET  /api/v1/product-center/{productId}/internal-note
│   ├─ 客观讲解提纲生成                               POST /api/v1/product-center/{productId}/outline
│   ├─ 知识助手问答                                   POST /api/v1/product-center/{productId}/assistant
│   ├─ 证据定位（带锚点）                             GET  /api/v1/product-center/evidence/{evidenceId}/locate
│   ├─ 历史版本与差异                                 GET  /api/v1/product-center/{productId}/versions[/diff]
│   ├─ 完整度与缺口                                   GET  /api/v1/product-center/{productId}/coverage
│   └─ 反馈                                           POST /api/v1/product-center/{productId}/feedback
│
└─【必须解决的不一致】
    ├─ POST /api/v1/product-knowledge/versions（写端点）vs 控制器注释"GITS 不得有产品卡写接口"
    └─ productId 白名单 ^PROD-[A-Z]+-[0-9]{3}$ vs 需求 DEMO-* 前缀
```

### 5.3 数据影响图

```text
数据对象
├─ 已有（可映射）  ProductKnowledgeVersion(15字段) / ProductKnowledgeCard / Evidence /
│                   EvidenceVersionLink / AuditTraceEntry / 12 张 pk_* 候选表（未落地）
├─ 需求要求但不存在  ProductFamily / Product / ProductKnowledgeVersion(扩展:status,owner,review,
│                   knowledge_as_of,next_review_at,evidence_snapshot_id,environment,is_demo) /
│                   ProductSummary / ProductTerm / ApplicabilityBoundary / Prerequisite /
│                   ProcessStep / MaterialGroup / MaterialItem / PricingItem / AgreementClause /
│                   SalesBoundary / ComparisonSet / ComparisonDimension / FAQ / EvidenceRef(Java 模型) /
│                   Favorite / Feedback / Coverage / AssistantLog / AuditEvent
└─ 落库路径         specs/product-knowledge/migration-candidates/*/V023（12 表）→ 需迁入
                   adapters/persistence-relational/src/main/resources/db/migration/{h2,mysql}
                   并按规则同步双方言（H2 + MySQL）
```

### 5.4 权限影响图

```text
权限（PI-NFR-004 / PI-FR-014/067/089 / AT-004/010/050/069）
现状：仅 API Key 认证（X-API-KEY），无角色/主体/证据级授权
        ApiKeyAuthenticationFilter.java:31-105 · SecurityConfig.java:41-66
必需：服务端 RBAC/ABAC 决策点，覆盖
       产品可见性 → 目录/搜索/深链接
       证据可见性 → 证据列表/定位/搜索片段
       价格分级   → PUBLIC / RM_INTERNAL / SENSITIVE_INTERNAL
       历史版本   → 变更摘要 vs 全文
       助手       → 可用知识集合 ≤ 用户直接浏览权限（防提示注入）
结论：BLOCKED —— 需 Owner 决定身份/权限服务来源（PI-OI-014 + 需求 01 §11 依赖假设）
```

### 5.5 测试影响图

```text
测试
├─ 前端单测 新增 components/product-center/__tests__/*、stores/__tests__/productCenter.spec.ts、
│            router/__tests__/routes.spec.ts（新增路由断言）
├─ 前端单测 必须修改 components/shell/__tests__/AppSidebar.spec.ts:62（12 → 13）
├─ E2E      新增 e2e/product-center*.spec.ts（1680/1440/1280 + 异常态 + 键盘）
│           ⚠ frontend/e2e/experience-shell.spec.ts 与 full-experience.spec.ts 当前**已被未提交修改**
├─ 后端单测 新增 ProductCenterControllerTest / 各领域服务 Test（JUnit5+AssertJ+Mockito）
├─ 后端集成 @SpringBootTest + H2（*IT）
├─ 契约测试 **扩展** ContractComplianceTest 覆盖 product-center 新契约（当前盲区）
└─ 门禁     make generate → make check → contract-verify → （新增）负例/变异测试
            注：`make backend-test` 走 verify，含 OWASP dependency-check（需联网，间歇性超时）
                按 GK17 口径测试面应用 `./mvnw test`
```

### 5.6 门禁与产物影响

| 门禁 | 本次影响 |
|---|---|
| `make generate` | 新增合同必须先登记 `specs/CONTRACT_INDEX.yaml` 才能生成（登记驱动，非通配） |
| `make check` | `generated/` 哈希一致性；新生成目标须**独立**，不得覆盖既有制品 |
| `contract-verify` | 建议扩展 `ContractComplianceTest` 覆盖新契约 |
| `frontend-test` | `npm ci && vue-tsc --noEmit && vitest run && vite build` 全部需通过 |
| 证据纪律 | 每 Loop 需 `EVIDENCE.md`/`STATE.json`/`NEXT_SESSION.md` + `make memory-check`/`evidence-check` |

---

## 6. 可复用 / 需改造 / 缺失 / 冲突 清单

### 6.1 可直接复用（不改语义）

| 资产 | 位置 | 复用方式 |
|---|---|---|
| 产品卡目录与详情只读 API | `ProductInterpretationController.java:62-84` | 目录/详情数据源之一 |
| 证据回链摘要（含 authorityLevel/locatorHint/quoteExcerpt） | 同文件 `:146-151` | 条款/FAQ/协议的证据展示 |
| 受控失败矩阵（404/409/422/503 + 统一错误体） | 同文件 `:178-212` | 新端点沿用同一错误语义 |
| fail-closed 适配器（KERT 不可达不本地补数） | `KertReleaseSnapshotAdapter.java:37-64` | 全部新数据入口 |
| 证据版本链 | `EvidenceVersionLink.java:9` + `EvidenceVersionController` | 证据失效联动（FR-068） |
| 审计落库 | `JdbcAuditTraceRepository.java:31-82` | 8 类新事件 |
| LLM 出口 | `LlmClient` / `MockLlmClient.java:14` / `RealLlmClient` | 助手 + 提纲生成 |
| API Key 过滤链与 CORS | `SecurityConfig.java:41-66` | 在既有链上增加授权决策点 |
| 版本查询 API | `gits-kno-api.openapi.json:1151-1173` | 历史版本（FR-085） |
| 前端四态 composable | `composables/useResourceStatus.ts` | 每章节独立四态 |
| 前端滚动位置恢复 | `stores/pageReference.ts` | 章节位置恢复（FR-028） |
| 壳层通用件 | `components/shell/{ObjectHeader,PageState,DisabledAction,StagePath}.vue` | 页面头部/状态/禁用写操作 |
| 设计令牌 | `assets/styles/theme.css:7-123` | 颜色/圆角/间距映射 |

### 6.2 需改造

| 资产 | 改造点 | 风险 |
|---|---|---|
| `layouts/navConfig.ts` | 追加 1 item + domain 联合类型 + `navDomainForPath` 分支 | 影响 `AppSidebar.spec.ts:62` 与 e2e 导航断言 |
| `ProductInterpretationController.getInterpretation` | 若扩展 view 枚举或 productId 白名单 | 会动 P38 依赖的合同 ⇒ **本轮禁止**，应另开新端点 |
| `ProductKnowledgeVersion`（record + 表） | 需补 status/owner/review/knowledge_as_of/next_review_at/evidence_snapshot_id/environment/is_demo | 改 record 会波及既有 6 个测试类 |
| `ContractComplianceTest` | 扩展覆盖 product-center 契约 | 当前为盲区 |
| `audit_trace` | 需支持 8 类新事件字段（section/citations/model_version 等） | 迁移脚本双方言同步 |
| `frontend` 布局容器 | 页面级 1700/246/310 与三档基线 | **不应**改全局壳层（P30–P37 已验收） |

### 6.3 缺失（必须新建）

- 后端：产品族/产品/条款/边界/前提/流程/材料/价格/协议/比较/FAQ 领域对象与 Port；14 个新端点（§5.2）；12 张 `pk_*` 表落地；搜索；文件下载/生成；助手；完整度；反馈；RBAC。
- 前端：15 个组件 + 1 新页面 + 1 store + 1 API 模块 + 三档响应式基线 + 环境条/页脚边界。
- 测试：86 项 AT 的自动化与 E2E；契约负例与变异测试（防"断言空转"）。
- 数据：真实权威来源（`PI-OI-001`，上线 BLOCKER）；DEMO 与生产隔离机制（`PI-OI-015`）。

### 6.4 冲突（必须 Owner 裁决，不得自行覆盖）

| # | 冲突 | 冲突双方 | 建议默认 |
|---|---|---|---|
| C-01 | 产品族分类法 | `CTR-PK-TAX-001`（6 族：流动资金融资/贸易融资/结算服务/现金管理/跨境金融/投资银行） vs 参考原型（5 族：账户与支付/融资与授信/贸易金融/资金管理/跨境与外汇） vs `FAMILY_ORDER`（`ProductInterpretationView.vue:45`） | 以 `CTR-PK-TAX-001` 为受控分类法，原型 5 族仅作展示示例；如需改为 5 族须走合同变更 |
| C-02 | 产品编号规则 | 后端 `^PROD-[A-Z]+-[0-9]{3}$`（`Controller.java:33`） vs 需求 `DEMO-*` 前缀（`03` §3.2） | 新增独立 DEMO 命名空间，不改既有正则语义 |
| C-03 | 确定性状态枚举 | `KnowledgeState` 5 态 vs 需求 6 态（已核验/待核验/审批变量/价格变量/冲突/已失效） | 建立映射表（`APPROVAL_VARIABLE`+`PRICING_VARIABLE` 均映射自现 `UNKNOWN/SUPPORTED` 语义需明确）；**不得**静默合并 |
| C-04 | 版本状态机 | 需求 `DRAFT→IN_REVIEW→APPROVED→PUBLISHED→REVIEW_DUE→EXPIRED/RETIRED` vs 既有 KERT Release `lifecycleState`（`PUBLISHED`/stale） | KERT 侧为运行态、GITS 侧为治理态，需明确单一权威与同步方向 |
| C-05 | 写接口方向 | `ProductInterpretationController.java:23-24` 声明"GITS 不得有产品卡写接口" vs `ProductKnowledgeVersionController.java:62-65` 存在 POST 创建版本 | 需 Owner/架构裁定，本轮不处置 |
| C-06 | 设计令牌 | `--product-*`（16 个）vs `--gits-*`（既有） | 映射到既有令牌；新增页面级布局令牌，避免双套颜色体系 |
| C-07 | 数据权威源 | KERT Release 投影（`RLS-2026.09.06.1`）vs GITS `product_knowledge_version` 13 条种子 | 只读消费 KERT、GITS 不产生结论（沿用既有决策） |
| C-08 | 全量布局 | 需求 1700px vs `.page-container{max-width:1400px}`（`style.css:117`） | 新页面用独立容器类，**不**改全局容器（避免回归 P30–P37） |

---

## 7. 分 Loop 施工计划与工作量估算

**Loop 命名建议**：`PC1`–`PC7`（Product Center），或复用 `PI-ARCH` 系列。见 `OD-PI-07`。

| Loop | 目标 | 主要交付 | 估算（人日） | 依赖 | ACCEPT 判据 |
|---|---|---|---:|---|---|
| **PC0** | 基线与契约 | 菜单/路由/新页面骨架占位；需求矩阵固化；12 张表迁移设计与双方言；14 端点合同登记（`CONTRACT_INDEX`）；DEMO/生产隔离方案；枚举与错误码映射表 | 5–7 | 无 | `make generate`+`make check` PASS；新契约在 `CONTRACT_INDEX` 登记；13 项菜单断言更新后 `frontend-test` PASS |
| **PC1** | 页面骨架与目录 | 环境条、页内头部、三栏布局、产品目录、产品首屏、章节导航、1680/1440/1280 基线、新 store/API | 6–8 | PC0 | 三档截图无截断；目录切换不残留旧数据；`vue-tsc` 0 错误 |
| **PC2** | 核心产品解读 | 60 秒读懂、核心条款表、适用边界、三类前提、办理流程与例外 | 8–10 | PC1 | 8 关键条款齐备；状态 6 态文字化；边界固定声明不可隐藏 |
| **PC3** | 材料、价格与协议 | 三类材料、价格构成与变量、协议条款定位、可说/不可承诺、敏感价格分级 | 7–9 | PC2 | 无费用显"未配置"；不可承诺 ≥5 类；服务端过滤生效 |
| **PC4** | 比较、FAQ 与知识治理 | 无推荐性比较、FAQ、版本/审核/责任人/复审、完整度与缺口、证据列表与历史 | 6–8 | PC2 | DOM/API 无 `score/ranking/win_rate`；完整度可解释且含缺口 |
| **PC5** | 下载、生成、助手与审计 | 收藏、内部说明下载、讲解提纲、受控助手、引用/拒答/权限继承/审计/AI 降级 | 7–9 | PC3+PC4 | 无证据拒答；提示注入不越权；助手不可用页面仍完整 |
| **PC6** | 全量验收 | `PI-AT-001`–`086` 执行、性能、安全、可访问性、浏览器与视觉回归、E2E 证据、独立 QA | 8–12 | PC5 | 全 P0 通过；无 BLOCKER/未豁免 MAJOR；三种宽度 + 异常态截图 |
| | **合计** | | **47–63 人日** | | |

**关键路径**：PC0 → PC1 → PC2 →（PC3 ∥ PC4）→ PC5 → PC6。
**并行约束（沿用本仓实测纪律）**：`make generate` / `make check` / Maven 测试 **必须串行**；Loop 记忆只有 TL 可写。

---

## 8. 风险、依赖与回滚策略

### 8.1 风险登记

| # | 风险 | 概率 | 影响 | 缓解 |
|---|---|---|---|---|
| R-01 | **共享件波及**：新增菜单改 `navConfig`，破坏 `AppSidebar.spec.ts` 的 12 项断言与 e2e 导航 | 高 | 中 | PC0 内先改断言（12→13）并留证；不改 P38 相关代码 |
| R-02 | **误以为可复用 P38** | 中 | 高 | 本文件 §4.17 明确：**0 项** FR 可判 compliant |
| R-03 | **枚举/分类法静默合并**（C-01/C-03） | 中 | 高 | 显式映射表 + 负例测试 + Owner 裁决 |
| R-04 | **权限缺失被前端隐藏掩盖**（AT-050/069） | 高 | 高（BLOCKER 级） | 服务端过滤先行；前端隐藏不作为证据 |
| R-05 | **DEMO 被当生产**（AT-065） | 中 | 高（BLOCKER 级） | 三道闸 + 环境条 + 生产开关 + 阻断测试 |
| R-06 | **版本混用**（AT-078） | 中 | 高 | `published_version_id` 贯穿请求周期；断言单一版本 |
| R-07 | **断言空转**（本仓已被证实的系统性陷阱：6 个 Loop 首报全绿实为空转） | 高 | 高 | 每个门禁做**变异复验**（mutate→FAIL / restore→PASS）；断言前核对输入基数 |
| R-08 | 工作区 182 项未提交 + 另有执行者并发提交 | 高 | 中 | 显式路径 `git add`；开工前确认 `frontend/e2e/*` 归属 |
| R-09 | OWASP dependency-check 间歇超时导致模块 SKIPPED | 中 | 中 | 测试面用 `./mvnw test`；不把 SKIPPED 读作通过 |
| R-10 | 契约变更波及既有 CANDIDATE 合同 | 中 | 中 | 新生成目标独立；`contract-diff` 比对基线 |
| R-11 | 助手成本/模型/检索未定 | 中 | 中 | 助手为增强项，核心页不依赖（NFR-002） |
| R-12 | 真实产品数据缺失（27/28 未上传） | 高 | 高（上线） | 明确标注 DEMO；上线前替换（`PI-OI-001/015`） |

### 8.2 外部依赖

统一身份/权限服务 · 产品目录与版本服务 · 证据文档库与定位服务 · 审计日志与文件下载服务 · 受控检索/生成服务（KERT 侧） · 真实产品制度/价目/协议模板（Owner 提供并审核）。

### 8.3 回滚策略

| 层 | 回滚方式 |
|---|---|
| 菜单/路由 | 移除 `navConfig` 追加项与路由条目即可回到当前 12 项状态（纯追加，无既有行变更） |
| 前端页面 | 新目录 `components/product-center/`、`views/ProductCenterView.vue` 独立；删除不影响 P38 |
| 后端 | 新端点独立于 `/api/v1/product-knowledge` 既有 3 端点；停用新控制器 Bean 即可 |
| 契约 | 新 CTR 条目可回退为未登记；`generated/` 由 `make generate` 重建，禁止手改 |
| 数据 | 新表由独立迁移脚本创建；提供对应 down 脚本（本仓约定：迁移不删除既有列） |
| 全局 | 全过程不修改封版制品、不修改 P38、不改全局壳层样式 ⇒ 回滚面局限于新增文件 |

---

## 9. 需要 Owner 决定的开放问题

### 9.1 需求包既有（继承）

| ID | 问题 | 建议默认 | 阻断级别 |
|---|---|---|---|
| `PI-OI-001` | 生产产品知识权威来源与责任组织 | 制度/规程/价目/协议分设 Owner，由产品知识版本聚合 | 上线 BLOCKER |
| `PI-OI-002` | 是否沿用受控分类法 | 沿用 `CTR-PK-TAX-001`，禁止硬编码 5 族（见 C-01） | 开发前 MAJOR |
| `PI-OI-003` | GITS↔DKES 是否已有产品/版本/证据对象 | **现状：部分已有**（§2.2）；建议适配器优先、既有契约不变 | 开发前 MAJOR |
| `PI-OI-004` | 证据正文由哪个系统承载 | 本页存 `EvidenceRef`，正文由受控文档服务承载 | Loop 4 前 MAJOR |
| `PI-OI-005` | 完整度权重 | 初期显示"已覆盖 X/Y"，权重获批后再显百分比 | MINOR |
| `PI-OI-006` | 历史版本开放度 | 默认只给变更摘要，全文按角色授权 | Loop 4 前 MAJOR |
| `PI-OI-007` | 内部说明下载格式 | 默认 PDF，保留 HTML/Word 扩展 | Loop 5 前 MINOR |
| `PI-OI-008` | 提纲是否可编辑保存 | 本期只生成可复制内容，不回写产品版本 | MINOR |
| `PI-OI-009` | 助手模型/检索/引用服务 | 复用受控知识服务；硬要求=版本锁定+权限继承+证据引用+拒答 | Loop 5 前 MAJOR |
| `PI-OI-010` | 比较内容审批责任人 | 各产品 Owner 供内容，产品族 Owner 统一审核 | Loop 4 前 MAJOR |
| `PI-OI-011` | 地区/机构/币种差异呈现 | 版本/章节支持 Scope，页面显示当前范围与切换入口 | 开发前 MAJOR |
| `PI-OI-012` | 暗色模式是否纳入本期 | 不纳入，浅色为验收基线 | NOTE |
| `PI-OI-013` | <1180px 是否要完整移动端 | 只做可用降级 | MINOR |
| `PI-OI-014` | 搜索是否返回证据正文片段 | 返回有权受控片段，敏感只回元数据 | 开发前 MAJOR |
| `PI-OI-015` | DEMO 在 UAT/生产如何隔离 | 独立命名空间 + 水印 + 环境开关，生产默认不可见 | 上线 BLOCKER |

### 9.2 TL 新增（本仓实测发现）｜**决策结果见 §11 决策登记**

| ID | 需 Owner 决定 | TL 建议 | 为什么必须 Owner 定 |
|---|---|---|---|
| `OD-PI-01` | 新「产品中心」与既有「产品解读与知识」(P38) 的长期关系 | 并存；本轮 P38 完全冻结；后续另行申请是否收敛 | 涉及既有已验收页面（P30–P37 `qa_pass`）的定位 |
| `OD-PI-02` | 是否允许修改 `AppSidebar.spec.ts:62`（12→13）与相关 e2e | 允许（纯追加导致的断言更新），并在证据中说明"未改 P38 相关断言" | 触碰既有测试基线 |
| `OD-PI-03` | 状态枚举统一口径（C-03） | 建映射表，不合并语义 | 影响合同与既有 5 态消费方 |
| `OD-PI-04` | 产品族分类法（C-01） | 沿用 `CTR-PK-TAX-001` | 影响目录、搜索、迁移 |
| `OD-PI-05` | `DEMO-*` 产品编号与既有 `PROD-XX-NNN` 正则（C-02） | 新增独立 DEMO 命名空间 | 影响合同校验 |
| `OD-PI-06` | 工作区 **182 项未提交改动**如何处理（尤其 `frontend/e2e/experience-shell.spec.ts`、`full-experience.spec.ts` 与本需求同文件） | 先由归属者提交/隔离，再开 PC0 | 并发写同一文件会互相覆盖 |
| `OD-PI-07` | 新 Loop ID 命名（`PC1`–`PC7` vs `PI-ARCH-*`） | 用 `PC1`–`PC7`，避免与未合并的 `feature/PI-ARCH-L10-L13` 混淆 | Loop 治理与记忆归属 |
| `OD-PI-08` | 是否允许新增合同（`CTR-PK-CENTER-*` 等 14 端点 + 领域 schema）并登记 `CONTRACT_INDEX` | 允许，且新生成目标独立、不改既有制品 | 合同为 SSOT，变更需授权 |
| `OD-PI-09` | 是否需要改 KERT 仓（本 TL 对 KERT 目前**只读**） | 优先 GITS 侧适配器；如需 KERT 变更另立变更申请 | 跨仓边界（KERT `AGENTS.md` 规则 1/10） |
| `OD-PI-10` | 写接口方向冲突（C-05：`ProductKnowledgeVersionController` POST vs 只读声明） | 本轮不处置，登记为技术债 | 涉及既有设计决策归属 |
| `OD-PI-11` | 1700px 容器是否可采用页面级独立类 | 采用页面级，不改全局 `.page-container` | 避免 P30–P37 视觉回归 |

---

## 10. Loop 0（PC0）具体任务、完成定义、检查命令与验收证据

### 10.1 任务分解

| 任务 | 内容 | 产出 |
|---|---|---|
| T0-1 | 需求矩阵落库：95 FR × 13 字段 + 86 AT 映射到本 Loop 归属 | `docs/dispatch/PC-需求覆盖矩阵-V1.0.md`（或 Loop memory） |
| T0-2 | 菜单与路由最小追加：`navConfig` +1 item（新 domain）+ `navDomainForPath` +1 分支 + 新路由 + 占位页 | 代码 diff（**不动 P38**） |
| T0-3 | 测试基线修复：`AppSidebar.spec.ts` 12→13；新增菜单可见性断言 | 测试 diff |
| T0-4 | 契约设计：14 端点 OpenAPI + 18 类对象 schema（含 6 态枚举、SalesBoundary、ComparisonSet 禁字段） | `specs/product-center/*` |
| T0-5 | 合同登记：`specs/CONTRACT_INDEX.yaml` 追加条目（独立 generated 目标） | 合同索引 diff |
| T0-6 | 数据迁移设计：12 张 `pk_*` 表从 `migration-candidates` 迁入 `adapters/persistence-relational/.../{h2,mysql}`，双方言同步 | 迁移脚本 + 校验 |
| T0-7 | DEMO/生产隔离方案：命名空间、水印、环境开关、生产默认不可见 | 设计文档 + 断言 |
| T0-8 | 错误码映射：需求 12 个错误码 ↔ 既有 4 类受控失败 ↔ HTTP 状态 | 映射表 |
| T0-9 | 枚举映射：`KnowledgeState` 5 态 ↔ 需求 6 态（C-03） | 映射表 + 负例 |
| T0-10 | 目录/搜索/权限设计：分类法（C-01）、Scope（`PI-OI-011`）、RBAC 决策点 | 设计文档 |
| T0-11 | 负例与变异测试骨架：为 T0-4/5/6/9 各写"注入故障应判 FAIL"的测试 | 测试脚本 |

### 10.2 完成定义（DoD）

1. 菜单新增可见且**唯一高亮**（不与「产品解读与知识」同时高亮）；
2. P38 相关文件 `git diff` 为**空**（`views/ProductInterpretationView.vue`、`api/productKnowledge.ts`、P38 路由）；
3. `make generate` 与 `make check` PASS；新合同在 `CONTRACT_INDEX` 可检索；
4. `frontend`：`npm run check` 0 错误、`npm run test` 全绿（含更新后的 13 项断言）、`npm run build` 成功；
5. 后端：`./mvnw -q -DskipTests -Ddependency-check.skip=true install` 成功；`./mvnw test` 全绿（不用 `verify` 判绿，避免 SKIPPED 假绿）；
6. 迁移脚本 H2/MySQL 双份存在且 H2 可启动执行；
7. T0-11 的变异测试：**mutate→FAIL / restore→PASS** 双向留证；
8. Loop 记忆与证据：`EVIDENCE.md` / `STATE.json` / `memory/NEXT_SESSION.md` 更新，`make memory-check`、`make evidence-check` PASS；
9. 缺陷按 `BLOCKER/MAJOR/MINOR/NOTE` 登记，先记账后修复。

### 10.3 检查命令

```bash
# 索引新鲜度（TL 开工/收工必跑）
make index-status

# 合同链
make generate
make check
make contract-verify
make contract-diff BASELINE=<既有基线目录>     # 兼容性比对

# 后端（按 GK17 口径：测试面用 test，不用 verify）
./mvnw -q -DskipTests -Ddependency-check.skip=true install
./mvnw --batch-mode --no-transfer-progress test

# 前端
cd frontend && npm ci && npm run check && npm run test && npm run build

# Loop 治理
make memory-check   LOOP=<PC0_LOOP_ID>
make evidence-check LOOP=<PC0_LOOP_ID>

# 变异复验（证明断言非空转）
python3 scripts/gate_selftest.py
```

### 10.4 验收证据清单（PC0）

| # | 证据 | 形式 |
|---|---|---|
| E-01 | 菜单新增前后侧栏截图（含高亮唯一性） | PNG（附路径） |
| E-02 | P38 未被改动的证明 | `git diff --stat` 指定路径为空 |
| E-03 | `make generate` / `make check` 输出 | 日志（含 commit/时间/退出码） |
| E-04 | `CONTRACT_INDEX` 新条目摘录 | diff |
| E-05 | 迁移脚本 H2/MySQL 对照 | diff + H2 启动日志 |
| E-06 | 前端三命令输出 | 日志 |
| E-07 | 后端 `install` + `test` 输出 | 日志（注明是否含 SKIPPED） |
| E-08 | 枚举映射表 + 负例执行结果 | 文档 + 日志 |
| E-09 | 变异测试双向留证（mutate→FAIL / restore→PASS） | 日志对 |
| E-10 | DEMO/生产隔离方案与验证 | 文档 + 断言输出 |
| E-11 | Loop 治理命令输出 | 日志 |
| E-12 | 缺陷登记（按四级分级） | `FAILURES.md` 条目 |

### 10.5 PC1 准入条件

- `OD-PI-01/02/04/05/06/07/08` 已裁决或形成 Owner 接受的受控假设；
- `PI-OI-002/003/011/014` 有结论或受控假设；
- PC0 全部 DoD 项有证据；
- 无 `BLOCKER`，无未豁免 `MAJOR`。

---

## 附：本轮已执行事实回源（节选）

| 结论 | 回源 |
|---|---|
| 一级组「知识与治理」下现有 2 项，第二项为「产品解读与知识」 | `frontend/src/layouts/navConfig.ts:51-55` |
| 侧栏按 `domain` 等值高亮 ⇒ 复用 domain 会双高亮 | `frontend/src/components/shell/AppSidebar.vue:109,113` |
| 测试断言导航项恰为 12 | `frontend/src/components/shell/__tests__/AppSidebar.spec.ts:62` |
| 既有解读 API 白名单与失败矩阵 | `apps/api/.../ProductInterpretationController.java:33-38,109-124,178-212` |
| 版本对象无 status/基准日/复审日 | `modules/operational-ontology/.../ProductKnowledgeVersion.java:10-25` |
| 12 张产品知识表仅存在于候选迁移 | `specs/product-knowledge/migration-candidates/h2/V023__product_knowledge_objects.sql` |
| 参考原型 8 section 与硬编码 5 族 | `reference/...参考实现.html` → `data-srcdoc` 解码（`overview…faq`；账户与支付 12/融资与授信 28/贸易金融 19/资金管理 16/跨境与外汇 21） |
| 索引新鲜 | `.ua/meta.json`（`gitCommitHash=7116904`）· `.ua/merge-meta.json` |

---

```text
## 11. 决策登记（2026-09-20）

### 11.1 登记表

| ID | 事项 | 结论 | 状态 |
|---|---|---|---|
| `OD-PI-01` | 「产品中心」与 P38「产品解读与知识」长期关系 | **本轮并存；P38 及其相关代码完全冻结**（route / view / api / 测试均不得改） | `OWNER_DECIDED` 2026-09-20 |
| `OD-PI-02` | 允许修改 `AppSidebar.spec.ts:62` 的 `toHaveLength(12)` | **允许**（仅长度断言 + 新增项断言；不动 P38 相关断言） | `OWNER_DECIDED` 2026-09-20 |
| `OD-PI-08` | 允许新增 `CTR-PK-CENTER-*` 合同 | **允许**（须登记 `CONTRACT_INDEX`；新 generated 目标独立；实现前先合同） | `OWNER_DECIDED` 2026-09-20 |
| `OD-PI-09` | 进入 KERT 仓改动 | **允许进入**（`Leibniz-KERT/AGENTS.md` 规则 10：push/merge 仍需单独授权；前置见 §11.4） | `OWNER_DECIDED` 2026-09-20 |
| `OD-PI-04` | 产品分类法 | **采纳 TL 建议**：唯一权威 = `CTR-PK-TAX-001`；原型 5 族仅作视觉示例；`PROD-CM-003` 归 `CASH_MANAGEMENT`（见 §11.2） | `OWNER_DECIDED` 2026-09-20 |
| `OD-PI-05` | `DEMO-*` 编号规则 | **采纳 TL 建议**：DEMO 前缀落在 `product_code`；`product_id` 保持 `PROD-XX-NNN` 不变（见 §11.3） | `OWNER_DECIDED` 2026-09-20 |
| `OD-PI-06` | 182 项未提交改动的处置 | **采纳 TL 建议**：分级最小动作三步（e2e 修复单独提交 / vite.config 保留提交 / 其余 179 项本 Loop 不碰）（见 §11.1.1） | `OWNER_DECIDED` 2026-09-20 |
| `OD-PI-03` | 状态枚举 5 态 → 6 态（C-03） | TL 受控假设：显式映射表 + 新增第 7 态 `NOT_APPLICABLE` 承接既有语义（见 §11.5）；合同登记时需 Owner 背书 | `TL_ASSUMPTION_PENDING_OWNER_ENDORSE` |
| `OD-PI-07` | 新 Loop ID 命名 | TL 决定：`PC0`–`PC7`（Product Center）；Owner 可否决重命名 | `TL_DECIDED` 2026-09-20 |
| `OD-PI-10` | 写接口方向冲突（C-05） | 建议登记技术债，本轮不处置 | `OPEN` |
| `OD-PI-11` | 1700px 容器 | 建议页面级独立类，不改全局 `.page-container` | `OPEN` |

### 11.1.1 `OD-PI-06` 详述：182 项未提交改动到底怎么处理

**先说人话。** `git status` 的 182 项不是"一个改动"，而是三方混在同一个工作区里都没提交：

| 类 | 数量 | 内容 | 归属判断 |
|---|---:|---|---|
| 未跟踪 `??` | 192 | `loops/GK17-ontology-unified-map/*`（20）、`docs/architecture/*`（20）、`docs/dispatch/*`（12）、`scripts/onto1_*.py` 等 | GK17 Loop 与另一执行者的在飞工作 |
| 已修改 `M` | 25 | `.codebuddy/rules/*`、`AGENTS.md`、`AI_GUIDE.md`、`Makefile`、`.understandignore`、`FAILURES.md`、`frontend/e2e/*`（2）、`frontend/vite.config.ts`（TL 上一轮）、GK17 记忆 | 混杂 |
| 已删除 `D` | 2 | `diagrams/architecture.{html,png}` | 另一执行者 |

**关键技术事实（本轮实测，决定这 2 个文件必须优先落定）**：
`frontend/e2e/experience-shell.spec.ts` 与 `frontend/e2e/full-experience.spec.ts` 的未提交改动是**修复 HEAD 上已经红的测试**：

| 位置 | HEAD 里写的 | HEAD 的 `navConfig.ts` 实际值 | 判定 |
|---|---|---|---|
| `e2e/experience-shell.spec.ts:18` | `'信号与互动'` | `'经营旅程'`（`navConfig.ts:35`） | HEAD 上该断言**必红** |
| `e2e/experience-shell.spec.ts:23` | `'证据与知识'` | `'产品解读与知识'`（`navConfig.ts:53`） | HEAD 上该断言**必红** |
| `e2e/full-experience.spec.ts:67` | `'信号与互动'` | `'经营旅程'` | HEAD 上该断言**必红** |
| `AppSidebar.spec.ts:67,73`（HEAD 已提交） | 已是 `'经营旅程'` / `'产品解读与知识'` | 一致 | 已同步，无需改 |

⇒ 这 3 行 e2e 改动是**必要修复，不是噪声**。同理 `docs/dispatch/PI-ROUND1-*.md` 是本轮 TL 新建，归属明确。

**为什么必须现在定**：PC0 要改 `AppSidebar.spec.ts`（12→13，`OD-PI-02` 已批）。若 e2e 修复仍悬在工作区，"前端全绿"的证据会混进一个无法区分归属的 diff，证据链断裂（本仓纪律：未落盘结论 = 不存在）；且任何人误跑 `git add .` 会把 GK17 的中间态记忆一起提交，污染那个 Loop 的证据。

**TL 建议：分级最小动作（三步）**

| 步 | 动作 | 范围 | 谁做 |
|---|---|---|---|
| 1（必须，PC0 前置） | 单独提交 `test(e2e): 修复已过期菜单名断言（信号与互动→经营旅程、证据与知识→产品解读与知识）` | 仅 `frontend/e2e/experience-shell.spec.ts`、`frontend/e2e/full-experience.spec.ts` | 归属者提交；若 Owner 确认无归属，TL 可代提交（需授权） |
| 2 | `frontend/vite.config.ts`（TL 上一轮为演示所改：代理目标支持 `VITE_API_PROXY_TARGET`，默认 `http://127.0.0.1:8080` 未变）→ 建议**保留并单独提交** | 1 文件 | TL |
| 3（明确排除） | 其余约 179 项：本 Loop **不碰、不提交、不 stash** | — | — |

**硬约束（TL 已执行并持续执行）**：全程只用显式路径 `git add <path>`，**禁止** `git add .` / `git add -A`（`AGENTS.md` 明令）。
**不由 TL 代做**：`git stash` / `git checkout --` 清空他人未提交改动 —— 会覆盖他人在飞工作。

### 11.2 `OD-PI-04` 详述：分类法建议（附本轮决定性新发现）

**新发现**：参考产品**已在受控分类法中登记**，无需新建产品：

```text
specs/product-knowledge/product-taxonomy.yaml:307  →  name_zh: 法人账户透支
product_id = PROD-CM-003    family = CASH_MANAGEMENT（现金管理）
```

权威分类法实测规模：3 Domain（交易银行/公司金融/国际业务）· 7 Family（6 active + 1 reserved `GUARANTEE_COMMITMENT`，文件注明"不得增删"）· 26 Category · 13 Product。

| Family | 中文名 | Domain | 已出卡 |
|---|---|---|---:|
| `CASH_MANAGEMENT` | 现金管理 | 交易银行 | 3（含 **PROD-CM-003 法人账户透支**） |
| `SETTLEMENT` | 结算 | 交易银行 | 2 |
| `TRADE_FINANCE` | 贸易金融 | 交易银行 | 2 |
| `CROSS_BORDER` | 跨境金融 | 国际业务 | 2 |
| `FINANCING` | 融资 | 公司金融 | 3（流动资金贷款 / 应收账款质押融资 / 订单融资） |
| `INVESTMENT_BANKING` | 投资银行 | 公司金融 | 1（并购贷款） |
| `GUARANTEE_COMMITMENT` | 担保承诺 | 公司金融 | 0（预留位） |

**TL 建议四条**：

1. **唯一权威 = `CTR-PK-TAX-001`**（Owner 已有 OQ-B 裁决，且文件注明"不得增删"）。参考原型的 5 族（账户与支付/融资与授信/贸易金融/资金管理/跨境与外汇）**不采纳为目录结构**，仅作视觉参考 —— 采纳即违反 `PI-OI-002`"不得从参考页硬编码 5 个产品族"。
2. **目录显示名以 taxonomy 的 `name_zh` 为准**：现金管理/结算/贸易金融/跨境金融/融资/投资银行。注意 taxonomy 头注 D-1 已登记"族中文名漂移"（产品卡侧写"结算服务/贸易融资/流动资金融资"）——这正是不能拿产品卡侧族名当权威的原因。
3. **法人账户透支 = `PROD-CM-003`，归 `CASH_MANAGEMENT`**。原型目录把它放在"融资与授信"属示例口径；若产品 Owner 认为应归 `FINANCING`，走分类变更申请 + `classification_review` 标记（taxonomy D-3 的既有先例），不擅改。
4. **比较对象跨族问题（新暴露的设计点）**：需求 §7 参考比较 = 法人账户透支（`CASH_MANAGEMENT`）vs 流动资金贷款/订单融资（`FINANCING`）→ **跨族比较**。可行（`ComparisonSet` 不限同族），但比较集合须由产品经理配置并经审核（`PI-FR-069`/`PI-OI-010`），且不得由分类法自动推导"邻近产品"。

### 11.3 `OD-PI-05` 详述：DEMO 编号建议

需求 `03` §3.2 原文区分了两个字段：

| 字段 | 需求定义 | 本轮建议 |
|---|---|---|
| `product_id` | **稳定产品标识** | **保持 `PROD-XX-NNN` 不变**（`PROD-CM-003` 等已存在；既有 P38 正则 `^PROD-[A-Z]+-[0-9]{3}$` 因此无需任何修改，P38 冻结约束自动满足） |
| `product_code` | 银行产品代码；**DEMO 使用 `DEMO-*` 前缀** | DEMO 前缀只落在这里：`product_code = DEMO-LOAN-OD-001` 这类 |
| `environment` / `is_demo` | 需求 3.3 要求 | 环境语义只放这两个字段，**不进 ID**（ID 稳定、无环境语义，符合需求"id 不随标题/环境变化"） |

**好处**：① 与需求原文逐字一致；② 不触碰 P38 的合同与正则；③ 不引入"同一产品在不同环境有不同 ID"的追溯难题（下游引用只认 `product_id + published_version_id + evidence_snapshot_id`）。
**DEMO 隔离**另由 `PI-OI-015` 方案承载：`is_demo=true` + 环境条/页脚强制标识 + 生产默认不可见 + 发布阻断校验（`03` §8 第 5 条：DEMO 数据试图进入生产正式版本 → 阻断）。

### 11.4 `OD-PI-09` 详述：进入 KERT 仓的前置与边界

Owner 已批准进入 KERT 仓。KERT 侧事实与约束（本轮实测）：

| 项 | 事实 |
|---|---|
| 分支/HEAD | `feature/m7-3-knowledge-map-route` @ `922a674` |
| 未提交改动 | **40 `M` + 40 `??`**（与 `OD-PI-06` 同一性质的问题，进入前同样需要归属确认） |
| 产品卡权威目录 | `examples/product-recommendation-assets/03_core/{cash-management,financing,trade-finance,settlement,cross-border,investment-banking,...}` |
| 既有在飞分支 | `feature/PI-ARCH-L10-L13`（L10–L13 产品解读链路，**未合并**） |
| 硬规则（`Leibniz-KERT/AGENTS.md`） | 不修改 GITS 仓；GITS 不得直连 Java Runtime；生产禁 `autoReload`；未过安全 Gate 禁 PythonTool/ShellTool；**不自行宣布 PRODUCTION_READY**；不删历史文档/ADR；**没有 Owner 授权不得自动 push/merge** |

**KERT 侧预判工作范围（供 Owner 排期，非本轮承诺）**：法人账户透支 8 章知识资产加工（条款/边界/前提/流程/材料/价格/协议/比较/FAQ 对象）+ `EvidenceSpan`/`FieldAssertion` + DEMO 源三道闸 + Release 发布与投影 —— 延续 L10–L13 既有链路。GITS 侧只读消费，不产生结论。

**进入前 TL 需要 Owner 补充授权的三件事**：① KERT 未提交改动的归属处置（同 OD-PI-06 步骤 1）；② KERT 侧分支策略（基于 `develop` 还是接续 `feature/PI-ARCH-L10-L13`）；③ push/merge 授权（规则 10，默认不授权时 TL 只在本地提交）。

### 11.5 `OD-PI-03` TL 受控假设：确定性状态映射表（5 态 → 7 态）

原则：**不合并语义、不删既有态、单向映射（既有 → 新）**；新枚举在需求要求的 6 态之上**新增第 7 态 `NOT_APPLICABLE`** 承接既有语义（需求原文为"至少支持"6 态，允许增补）。

| 既有 `KnowledgeState`（CTR-PK-INT-001 / P38 在用） | 新 `certainty_type`（产品中心） | 语义说明 |
|---|---|---|
| `SUPPORTED` | `VERIFIED`（已核验） | 有有效证据支撑 |
| `UNKNOWN` | `PENDING_VERIFICATION`（待核验） | 无证据/未复核；不得显示确定值 |
| `CONFLICT` | `CONFLICTING`（冲突） | 有效证据互斥；AI 不裁决 |
| `STALE` | `EXPIRED`（已失效） | 证据/版本过期 |
| `NOT_APPLICABLE` | `NOT_APPLICABLE`（不适用） | **新增第 7 态**，承接既有语义，避免信息丢失 |
| —（无既有来源） | `APPROVAL_VARIABLE`（审批变量） | 由产品知识版本侧标注，投影层不自动推导 |
| —（无既有来源） | `PRICING_VARIABLE`（价格变量） | 同上 |

约束：
1. P38 消费的既有 5 态枚举**不改**（P38 冻结）；映射只发生在产品中心新合同内；
2. KERT 投影字段 `knowledgeState` 进入产品中心 API 前按上表单向映射，映射代码必须有**逐态变异测试**（注入错误映射必须 FAIL）；
3. `APPROVAL_VARIABLE`/`PRICING_VARIABLE` 只能由受控知识版本写入，**禁止**由前端或 LLM 推导；
4. 该假设随 PC0 合同登记一并提交 Owner 背书；背书前不得进入 PC2（核心条款章节实现）。

---

```text
本文件状态：ROUND_1_DELIVERABLE_V1.2（Owner 决策登记完成）
GATE_A = PASS_WITH_REQUIRED_CHANGES
DECISIONS = OWNER_DECIDED ×7（OD-PI-01/02/04/05/06/08/09） + TL_ASSUMPTION ×1（OD-PI-03，§11.5） + TL_DECIDED ×1（OD-PI-07） + OPEN ×2（OD-PI-10/11 技术债类）
PC0 前置：已满足（Owner 2026-09-20 确认 OD-PI-04/05/06）
进入 PC2 前置：OD-PI-03 映射表 Owner 背书
FROZEN = NO
PRODUCTION_READY = NO
QA_PASS = 未申请（dev 角色不得自签）
```
```
