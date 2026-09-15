# ADR-PR-CANDIDATES｜产品推荐“三段式决策”架构决策记录（候选集）

- 文档编号：`ADR-PR-CANDIDATES`
- 文档状态：`CANDIDATE / FROZEN=NO / IMPLEMENTED=NO / REAL_E2E_PASS=NO`
- 权威基线：`V2.0 业务需求基线 + PB-V2.0-R1 + GITS 受保护合同`
- 权威输入：
  - `GITS_KERT_产品推荐三段式决策_详细落地方案_V1.0_20260831.md`（§15 建议新增 ADR 清单）
  - `GITS_KERT_产品解读与产品推荐_完整分析交接总册_V1.1.md`
  - `GITS_Bank_本体智能体完整交接包_V1.0_20260831/00_本体智能体交接总册_V1.0.md`
  - `GITS_Bank_本体智能体完整交接包_V1.0_20260831/01_客户服务建议书_产品解读_产品推荐_差异冲突与统一设计.md`
- 契约自洽基线（只读引用，不改动）：
  - `specs/product-recommendation/*.schema.json`（6 个 schema + README）
  - `specs/CONTRACT_INDEX.yaml`（`CTR-PR-*` 登记）
  - `specs/openapi/product-recommendation.openapi.json`
  - `specs/knowledge-architecture/skills/SP-15.json`
  - `specs/knowledge-architecture/activations/AC-PRODUCT-RECOMMEND-001.json`
  - `~/dev/Leibniz-KERT/skills/product-recommendation/`（SP-15.md / contracts / rules / product-cards）
- 范围声明：本文件仅新增候选 ADR（`ADR-PR-001` ~ `ADR-PR-007`），不改动任何既有合同、代码、schema 或 `generated/` 产物。全部条目均为 `Proposed / Candidate`，**不是** `Accepted / Frozen / Implemented`。

---

## 通用背景（Shared Context）

产品推荐不得继续沿用“从交易特征直接算一个分数再列产品”的单段算法模式，也不再是“RAG 问答 + 协同过滤推荐”的组合。对公产品推荐具有低频、复杂、规则强、解释要求高、责任链长的特点，因此目标方案固定为**同一 `ProductRecommendationRun` 内的三段式受控决策**，并把“决策式规则/模型”与“生成式解释”分层：

1. 第一段：硬约束过滤（Eligibility）——建立安全候选边界；
2. 第二段：需求—能力匹配与排序（Fit / Portfolio）——只在已通过硬约束的候选中解释“为什么、还缺什么”；
3. 第三段：客户经理人工确认（HumanGate）——对候选方案批准、修改、驳回或暂缓，形成可追踪的业务决定。

三段式不是三个独立智能体，也不是简单拆成三个页面。责任边界：**GITS** 负责业务入口、`ProductRecommendationRun` 生命周期、调用编排、阶段结果展示、人工门禁、方案版本与审计；**KERT** 负责受控资产激活、产品知识与规则装配、硬规则执行、匹配排序、组合约束校验、证据装配与 Skill 运行轨迹；**客户经理 / 产品 / 风险 / 合规 Owner** 分别承担人工决定与规则/知识发布治理。以下七条 ADR 是该边界的逐项落地。

---

## ADR-PR-001｜产品推荐采用“硬过滤 → 匹配排序 → 人工确认”三段式

- ID：`ADR-PR-001`
- 状态：`Proposed / Candidate`（`FROZEN=NO / IMPLEMENTED=NO`）
- 日期：2026-08-31
- 决策对象：GITS HLD / 业务 Owner

### Context（背景）

现状 `ProductMatchingService` 是五条 Java 硬编码启发式规则，直接输出产品列表，没有产品有效性控制、规则版本和证据链；“从交易特征算分再列产品”无法回答“哪些产品明确不能推荐、哪些因信息不足暂不能推荐、谁对结果负责”。三段式决策已被 `详细落地方案 V1.0` §0 与 §3 明确为唯一目标形态。

### Decision（决策）

产品推荐固定为**同一 `ProductRecommendationRun` 内的三个受控决策阶段**，不得拆成三个独立智能体，也不得退化为单段打分：

1. **第一段：硬约束过滤** → 对每个产品版本产出 `EligibilityResult`，结果闭集为 `ELIGIBLE / INELIGIBLE / UNKNOWN / REVIEW_REQUIRED`；`INELIGIBLE` 不得进入排序，`UNKNOWN` 不得按满足处理，`REVIEW_REQUIRED` 进入专家复核区。
2. **第二段：需求—能力匹配与排序** → 仅对 `ELIGIBLE` 产品产出 `ProductFitResult`（分维度匹配 `fitScore` 只用于已合格候选内部排序）与 `ProductPortfolioCandidate`（核心/配套/依赖/互斥/顺序）。
3. **第三段：客户经理人工确认** → 由 GITS 通过 `HG-D01 / D01_PRODUCT_RECOMMEND` 产出 `RecommendationHumanDecision`，其 `decision` 取值 `RecommendationDecision = APPROVE / MODIFY / REJECT / HOLD`；`APPROVE` 仅表示允许候选进入 G2 方案装配，不代表产品/授信/价格/建议书审批。

### Consequences（后果）

- 正面：候选边界、排序解释与人工责任分离；硬失败不可被软评分覆盖；每条结论可追溯规则、事实与证据。
- 负面/风险：实现与验收复杂度上升（状态机、幂等、版本、证据、人工门禁）；需 KERT 真实执行能力（Gate 0）支撑，否则只能停留在合同与 test fake 阶段。
- 未决：`REJECT` 与 `DECLINE` 双语义待 HumanGate Contract Owner 裁决（`OQ-04`），未裁决前前端不得自行解释。

### 契约自洽

对齐 `CTR-PR-RUN-001`（`product-recommendation-run.schema.json` 的 `RecommendationRunStatus`：`REQUESTED … HARD_FILTERING → MATCHING → PROPOSAL_READY → AWAITING_HUMAN → APPROVED/MODIFIED/REJECTED/HELD … FAILED_CLOSED`）、`CTR-PR-ELIG-001`（`EligibilityStatus` 四态）、`CTR-PR-FIT-001`（`ProductFitResult`）、`CTR-PR-PORT-001`（`ProductPortfolioCandidate`）、`CTR-PR-DEC-001`（`RecommendationDecision` 四态）、`CTR-PR-RES-001`（`ProductRecommendationResult` 聚合三阶段结果）。

---

## ADR-PR-002｜GITS 拥有业务 Run 与人工决定；KERT 拥有 Skill 执行与证据结果

- ID：`ADR-PR-002`
- 状态：`Proposed / Candidate`（`FROZEN=NO / IMPLEMENTED=NO`）
- 日期：2026-08-31
- 决策对象：GITS HLD / KERT Tech Lead

### Context（背景）

若业务状态机与 Skill 作业状态分属两处权威，会出现双重权威源与状态漂移。`详细落地方案 V1.0` §5 与 `本体智能体交接总册` §6 已给出责任边界表：GITS 主责业务 Run 与人工决定，KERT 主责 Skill 执行与证据结果。

### Decision（决策）

1. **GITS 拥有业务 Run**：`ProductRecommendationRun` 及其 `RecommendationRunStatus` 状态机由 GITS Domain 管理（创建、幂等、状态推进、版本过期、审计）。
2. **GITS 拥有人工决定**：`RecommendationHumanDecision`（`HG-D01 / D01_PRODUCT_RECOMMEND`）由 GITS 的 HumanGate 应用服务执行与审计，KERT 无审批权。
3. **KERT 拥有 Skill 执行与证据结果**：`SP-15` 的执行、`ProductRecommendationResult` 产出与 `EvidenceBundle` 装配由 KERT 负责；KERT 只维护 Skill 执行作业状态，**不得成为业务审批状态的第二权威源**。
4. **禁止重复权威**：GITS 不得复制 KERT 整套产品知识/规则/执行明细为第二权威库，只保存业务所需快照与引用。

### Consequences（后果）

- 正面：单一业务权威状态；人工责任明确；知识/规则/证据与业务编排解耦。
- 负面/风险：跨系统职责边界若实现不到位，可能出现状态映射漂移；需在 WP1 形成“业务状态 ↔ KERT job 状态”映射表。
- 未决：KERT 正式身份/仓库/统一执行 API 未受控（`BLK-01`），真实边界联调受 Gate 0 阻塞。

### 契约自洽

对齐 `CTR-PR-RUN-001`（`product-recommendation-run.schema.json` 描述“GITS 主责业务状态机；KERT 只维护 Skill 执行作业状态，不成为业务审批状态的第二权威源”）、`CTR-PR-RES-001`（`recommendation-result.schema.json` 描述“KERT 负责产出与证据装配；GITS 负责持久化业务快照与引用”）、`CTR-PR-DEC-001`、`specs/knowledge-architecture/skills/SP-15.json`（`humanGatePolicy=REQUIRED`、`sideEffectPolicy=PROPOSE_ONLY`）、`AC-PRODUCT-RECOMMEND-001.json`（`humanGates=["HG-D01"]`）。

---

## ADR-PR-003｜硬规则、权限、版本和证据失败一律 fail-closed

- ID：`ADR-PR-003`
- 状态：`Proposed / Candidate`（`FROZEN=NO / IMPLEMENTED=NO`）
- 日期：2026-08-31
- 决策对象：GITS HLD / KERT Tech Lead / 产品·风险·合规 Owner

### Context（背景）

银行对公推荐的安全底线要求“宁可不推荐，不可错推荐”。`README §2` 的不变量（`INV-01~INV-10`）与 `SP-15.md §7`、`rules/README.md` 已把 fail-closed 明确为机器可测不变量；`AC-PRODUCT-RECOMMEND-001.json` 设定 `failurePolicy=FAIL_CLOSED`、`defaultPolicy=DENY`。

### Decision（决策）

以下四类失败一律 fail-closed，不降级为“低置信度通过”，不启用本地生产推荐回退：

1. **硬规则失败**：`INELIGIBLE` 产品不得被软评分、模型置信度或历史销量重新拉回候选；`UNKNOWN` 不得按 `ELIGIBLE` 处理，只生成核实问题（`KERT_CONTEXT_INSUFFICIENT → HELD`）。
2. **权限失败**：调用人无权查看该客户/产品/规则 → `KERT_PERMISSION_DENIED → FAILED_CLOSED`，不重试。
3. **版本失败**：产品版本失效或规则版本缺失/不可复现 → `KERT_PRODUCT_KNOWLEDGE_STALE / KERT_RULE_VERSION_MISSING → FAILED_CLOSED`；上游版本变化 → 下游 `STALE`（不自动删除）。
4. **证据失败**：结果缺少必要证据 → `KERT_EVIDENCE_INCOMPLETE`，GITS 不得创建 `HG-D01`；权威证据冲突 → 禁止确定性解读。

### Consequences（后果）

- 正面：安全底线可机器验证；排除项对客户经理可解释；敏感内部规则按权限脱敏。
- 负面/风险：fail-closed 会提升“本轮无可用候选”的比例，需配套补材料/专家协同任务闭环。
- 未决：哪些准入/排除规则可对客户经理展示到何种粒度（`OQ-03`）未裁决。

### 契约自洽

对齐 `CTR-PR-ELIG-001`（`eligibility-result.schema.json` 描述“软评分、模型置信度、历史销量均不得覆盖 INELIGIBLE”）、`specs/product-recommendation/README.md §2` 不变量与 `§4` KERT 错误码映射、`AC-PRODUCT-RECOMMEND-001.json`（`failurePolicy=FAIL_CLOSED`）、`skills/product-recommendation/rules/README.md`（“`UNKNOWN` 不能转换为‘低置信度通过’；产品版本过期或规则版本缺失 → 整轮不得产出可批准方案”）。

---

## ADR-PR-004｜SP-15 保持稳定业务门面，KERT 内部步骤化执行与可观测

- ID：`ADR-PR-004`
- 状态：`Proposed / Candidate`（`FROZEN=NO / IMPLEMENTED=NO`）
- 日期：2026-08-31
- 决策对象：KERT Tech Lead / 产品 Owner

### Context（背景）

若把三段式定义成三个业务智能体并分别暴露给 GITS，会破坏业务稳定性并放大合同漂移面。`详细落地方案 V1.0` §7.2 与 `SP-15.md §3` 已规定：SP-15 保持为 GITS 看到的稳定业务门面，KERT 内部拆为可观测步骤。

### Decision（决策）

1. **稳定门面**：`SP-15 产品适配与综合方案` 保持为 GITS 可见的唯一业务 Skill 门面（`skillId=SP-15`，`implementationType=RULE_MODEL`，`humanGatePolicy=REQUIRED`，`sideEffectPolicy=PROPOSE_ONLY`）。
2. **内部步骤化**：KERT 内部将 SP-15 拆为可观测步骤，不向 GITS 暴露多个不稳定 Skill：`RecommendationInputValidator → ProductUniverseResolver → HardEligibilityRuleExecutor → NeedProfileResolver → NeedCapabilityMatcher → CandidateRanker → PortfolioConstraintChecker → RecommendationExplanationAssembler → EvidenceBundleAssembler`。
3. **LLM 边界**：LLM 只参与需求归纳、解释与文字组织，不得决定硬规则结果，不得补造缺失事实。

### Consequences（后果）

- 正面：业务门面稳定、合同面最小；内部步骤可观测、可独立回归。
- 负面/风险：内部步骤拆解若管理不善可能退化为“隐藏微服务”；需在 KERT 侧以可观测步骤而非独立对外 Skill 落地。
- 未决：试点产品族与产品清单未定（`OQ-02`），影响 `ProductUniverseResolver` 的实际范围。

### 契约自洽

对齐 `specs/knowledge-architecture/skills/SP-15.json`（`skillId=SP-15`、`implementationType=RULE_MODEL`、`outputs` 含 `EligibilityResult/ProductFitResult/ProductPortfolioCandidate/ProductRecommendationResult/EvidenceBundle`）、`skills/product-recommendation/SP-15.md §3`（九步骤表 + “LLM 只参与需求归纳、解释与文字组织”）、`CTR-PR-RES-001`（`skillId const SP-15`）。

---

## ADR-PR-005｜推荐基于不可变客户/知识快照和方案版本，可重放可过期（机器名 `ProductRecommendationRun` / `ProductRecommendationProposalVersion`，旧名 `RecommendationProposalVersion` 仅技术别名）

- ID：`ADR-PR-005`
- 状态：`Proposed / Candidate`（`FROZEN=NO / IMPLEMENTED=NO`）
- 日期：2026-08-31
- 决策对象：GITS HLD / 合同 Owner

### Context（背景）

推荐必须是可重放、可审计、可过期的证据链，不能只存一个“当前结果”。`本体智能体交接总册` §8 与 `差异冲突与统一设计` §4.2、§6 已给出最小版本与证据链；`差异冲突与统一设计` 明确 `RecommendationProposalVersion` 命名过宽，易与顶层 `ProposalVersion`（客户服务建议书版本）混淆，需收口为 `ProductRecommendationProposalVersion`。

### Decision（决策）

1. **不可变快照**：推荐只基于不可变快照——`CustomerFactSnapshot`（`customerFactSnapshotId`）、`ProductKnowledgeSnapshot`（`productKnowledgeSnapshotRef`）、`RuleBundle`（`ruleBundleRef`）与 `EvidenceBundle`（`evidenceBundleId`），由 `snapshotRefs` + `asOf` 固化本轮输入。
2. **不可变方案版本**：每次产出形成不可变 `ProductRecommendationProposalVersion`（`versionId/runId/resultRef/evidenceBundleId/contentHash/supersededBy/createdAt`），`contentHash`（sha256）用于重放与过期判断。
3. **命名收口**：
   - 机器名 = `ProductRecommendationRun`、`ProductRecommendationProposalVersion`（业务首选名）；
   - 旧名 `RecommendationProposalVersion` **仅作技术别名**，不再新增业务语义；现有 `specs/openapi/product-recommendation.openapi.json` 中仍以 `RecommendationProposalVersion` 作为 schema 名，属于待合同冻结时统一收口的命名缺口，不得据此新增与顶层 `ProposalVersion` 混淆的业务含义。
4. **可过期**：上游变化（Need 内容/状态/版本、`ProductVersion` 失效或变更、规则版本变化、`EvidenceBundle` 变化、权限撤销、经营目标改变、超有效期）→ 下游 `STALE_REQUIRES_RERUN`；`STALE` 保留旧版本与差异，不自动删除。

### Consequences（后果）

- 正面：重放可复现；过期可自动识别；`ProductRecommendationProposalVersion` 与顶层 `ProposalVersion` 语义分离。
- 负面/风险：命名收口与现网 schema 名存在一个过渡窗口；若合同冻结不允许改机器名，需显式登记“业务首选名 + 旧技术别名 + `subSolutionOf` 关系 + 弃用/迁移候选”。
- 未决：推荐方案有效期与触发重跑的变化清单待业务 Owner 裁决（`OQ-05`）。

### 契约自洽

对齐 `CTR-PR-RUN-001`（`product-recommendation-run.schema.json`：`snapshotRefs`、`currentVersionId`、`asOf`、`idempotencyKey`、`STALE_REQUIRES_RERUN`）、`CTR-PR-RES-001`（`recommendation-result.schema.json`：`productKnowledgeSnapshotRef/ruleExecutionRef/evidenceBundleId/contentHash`）、`specs/product-recommendation/README.md §1`（唯一权威链含 `ProductRecommendationProposalVersion`）、`specs/openapi/product-recommendation.openapi.json`（`ProductRecommendationRun` 与 `RecommendationProposalVersion` schema，后者待收口）。

---

## ADR-PR-006｜KERT 不可用时禁止 GITS 本地生产推荐 fallback

- ID：`ADR-PR-006`
- 状态：`Proposed / Candidate`（`FROZEN=NO / IMPLEMENTED=NO`）
- 日期：2026-08-31
- 决策对象：GITS HLD / Tech Lead

### Context（背景）

`INV-07` 明确“KERT 不可达 → 禁止本地生产推荐回退”。旧 `ProductMatchingService` 的五条 Java 硬编码启发式规则若在 KERT 失败时继续兜底，会冒充真实推荐并破坏 fail-closed 底线（`本体智能体交接总册` §6：可展示已签名/已缓存历史快照并明确过期，但不得用本地规则冒充同一次生产推荐运行）。

### Decision（决策）

1. **禁止本地生产 fallback**：KERT 不可达/执行失败时，GITS 不得调用本地 `ProductMatchingService` 或任何本地硬编码推荐逻辑冒充生产推荐结果。
2. **允许的降级**：返回受控失败（`FAILED_CLOSED`）；对 `KERT_EXECUTION_TIMEOUT` 按策略发起新 attempt（保留轨迹，不覆盖）；或展示**已签名/已缓存的历史快照**并显式标注“过期/不可刷新”，不得生成新的本地推荐。
3. **迁移期隔离**：旧 `product-matching` 端点仅作为待退役兼容实现存在，生产切换后**不得作为 KERT 失败回退**。

### Consequences（后果）

- 正面：杜绝“本地假推荐”这一零容忍项（验收指标：KERT 失败时本地假推荐 = 0）。
- 负面/风险：KERT 不可用期间的客户经理体验需要明确的受控降级 UX（显示失败/过期，而非空结果）。
- 未决：真实 KERT 适配器（鉴权、超时、错误码）待 Gate 0 落地后才可建设。

### 契约自洽

对齐 `specs/product-recommendation/README.md §2`（`INV-07`）与 `§4`（`KERT_EXECUTION_TIMEOUT` “不启用本地推荐”）、`AC-PRODUCT-RECOMMEND-001.json`（`failurePolicy=FAIL_CLOSED`）、`skills/product-recommendation/SP-15.md §7`（`INV-07`）、`本体智能体交接总册` §6。

---

## ADR-PR-007｜新合同增量发布；旧 product-matching 消费者清零后再退役（ProductMatch 三方漂移关闭为前置）

- ID：`ADR-PR-007`
- 状态：`Proposed / Candidate`（`FROZEN=NO / IMPLEMENTED=NO`）
- 日期：2026-08-31
- 决策对象：GITS HLD / 合同 Owner / OpenAPI Owner

### Context（背景）

当前 `ProductMatch` 存在三方漂移：OpenAPI 权威源 `productId/productName/matchScore/matchReasons[]/productCategory`，Java `productId/productName/reason/confidence/signal`，前端两者并集。旧端点 `POST /customer/{id}/product-matching` + `ProductMatchingService` + 前端 `matchProducts` 不可治理、不可版本化。`CONTRACT_INDEX.yaml` 中 `CTR-PR-API-001` 的 note 已明确“先关闭 ProductMatch 三方漂移再增量实现”。

### Decision（决策）

1. **新合同增量发布**：新增 `CTR-PR-API-001`、`CTR-PR-RUN-001`、`CTR-PR-ELIG-001`、`CTR-PR-FIT-001`、`CTR-PR-PORT-001`、`CTR-PR-RES-001`、`CTR-PR-DEC-001` 作为独立 vNext 合同，**不覆盖、不静默改变受保护旧合同**；在 `CTR-PR-API-001` 并入 `gits-kno-api.openapi.json` 前保持独立文档。
2. **旧实现保留兼容期**：`ProductMatchingService` + `POST /customer/{id}/product-matching` + 前端 `matchProducts` 停止新增业务逻辑，增加弃用标记与调用量监控；生产切换后不得作为 KERT 失败回退。
3. **消费者清零后再退役**：最终删除走契约变更 + 消费者清零门禁；**ProductMatch 三方漂移关闭（contract-diff + 兼容策略 + 合同测试）是旧端点退役的前置条件**。

### Consequences（后果）

- 正面：受保护合同不被静默覆盖；迁移可观测、可回滚；漂移关闭作为退役前置避免“边漂移边删”。
- 负面/风险：存在一段新旧并行的兼容窗口，需调用量监控防止旧路径继续被生产依赖。
- 未决：`REJECT` vs `DECLINE` 双语义（`OQ-04`）在旧 `GateDecision` 与新 `RecommendationDecision` 间的映射待裁决。

### 契约自洽

对齐 `specs/CONTRACT_INDEX.yaml`（`CTR-PR-API-001` note“先关闭 ProductMatch 三方漂移再增量实现”、`CTR-PR-RUN-001 … CTR-PR-DEC-001` 全部 `status=CANDIDATE`）、`specs/product-recommendation/README.md §5`（旧实现处置：保留兼容期 + 弃用标记 + 调用量监控 + 消费者清零门禁 + `ProductMatch` 三方漂移记录）、`CTR-PR-API-001`（`compatibility=backward_compatible`）。

---

## 门禁结论

```text
DOCUMENT_STATUS=CANDIDATE
FROZEN=NO
IMPLEMENTED=NO
REAL_E2E_PASS=NO
ADR_STATUS=Proposed / Candidate（不得视为 Accepted/Frozen/Implemented）
NEXT_GATE=Owner 评审 + KERT Gate 0 + ProductMatch 三方漂移关闭
```

本候选集不构成任何“已批准、已冻结、已实现、已联调或生产就绪”声明；落地顺序受 `详细落地方案 V1.0` §17 的 Tech Lead 执行顺序约束：先 WP0（V2.0 基线索引 + KERT Gate 0）与 ProductMatch contract-drift 记录，再进入合同设计与真实适配。
