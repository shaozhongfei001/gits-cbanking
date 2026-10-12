# ADR-PR-IDEMPOTENCY｜产品推荐：幂等、重试、并发与过期（WP1-4）

> 文档编号：`ADR-PR-IDEMPOTENCY`
> 文档状态：`CANDIDATE / FROZEN=NO / IMPLEMENTED=NO / REAL_E2E_PASS=NO`
> 日期：2026-08-31
> 派工任务：WP1-4（双方 幂等与并发 ADR）
> 决策对象：GITS HLD / KERT Tech Lead / HumanGate Contract Owner / 业务 Owner
> 交付范围：本文件只新增 `docs/adr/ADR-PR-IDEMPOTENCY_CANDIDATE.md`，不改动任何既有文件、合同、schema、代码或 `generated/` 产物。

---

## 0. 取证说明与一致性锚点（先取证，再下结论）

### 0.1 权威依据

| 顺位 | 依据 | 用途 |
|:--:|---|---|
| 1 | `GITS_KERT_产品推荐三段式决策_详细落地方案_V1.0_20260831.md`（§10 幂等/重试/并发/版本控制、§4.1 状态机、§6.2 API、§7.5 错误码） | 本 ADR 四决议的语义权威源 |
| 2 | `GITS_KERT_产品解读与产品推荐_完整分析交接总册_V1.1.md`（§7.3 INV-01~INV-10、§11 验收指标） | 不变量与验收锚点 |
| 3 | `GITS_Bank_本体智能体完整交接包_V1.0_20260831/00_本体智能体交接总册_V1.0.md`（§7 状态命名空间、§8 STALE 触发清单） | 状态/过期语义锚点 |
| 4 | `GITS_Bank_本体智能体完整交接包_V1.0_20260831/01_客户服务建议书_产品解读_产品推荐_差异冲突与统一设计.md`（§6 最小对象链与不变量） | 版本/决策对象关系锚点 |
| 5 | 已落地 SDD 契约：`specs/product-recommendation/*.schema.json` + README、`specs/CONTRACT_INDEX.yaml`（`CTR-PR-*`）、`specs/openapi/product-recommendation.openapi.json`、`specs/knowledge-architecture/skills/SP-15.json`、`specs/knowledge-architecture/activations/AC-PRODUCT-RECOMMEND-001.json` | 枚举/字段自洽锚点（只读引用） |
| 6 | `~/dev/Leibniz-KERT/skills/product-recommendation/`（SP-15.md / contracts / rules / product-cards）、`specs/dkws-openapi-v1.yaml` | KERT 侧 Skill/失败码锚点（只读引用） |

### 0.2 取证结论（如实报告）

1. 截至本 ADR 生成时，`~/dev/gits-cbanking` 工作树内 `specs/product-recommendation/` 目录**仅有并发 WP1-1 核验任务生成的 `examples/` 子目录**，**不含** 6 个 schema + README；`specs/openapi/product-recommendation.openapi.json`、`specs/knowledge-architecture/activations/AC-PRODUCT-RECOMMEND-001.json` 与 `CONTRACT_INDEX.yaml` 的 `CTR-PR-*` 登记均**不在工作树**；`specs/knowledge-architecture/skills/SP-15.json` 仍是旧版（`version=1.1.0-p20`、`status=VALIDATION`，非 product-recommendation vNext）。
2. 上述 step 3 契约（6 个 schema + README + openapi + `CTR-PR-*` + AC-*）以未提交状态被 **WP0-1 隔离到 `git stash@{0}`**（`WP0-1 isolation: step3 SDD product-recommendation contracts ...`）。本 ADR 以只读 `git show stash@{0}` / `git show stash@{0}^3:<path>` 取证，**不 pop、不改动**该 stash，也不改动工作树内并发任务新生成的任何文件。
3. 因此本 ADR 的“枚举/字段自洽”锚定于该 stash 内**实际落地**的 6 个 schema + openapi + README（`CTR-PR-*`），同时与权威设计文档的语义口径对齐；字段名以落地 schema 为准，设计文档措辞差异在第 6 节登记。

### 0.3 一致性锚点（本 ADR 四条决议共同引用的枚举/字段）

| 锚点 | 枚举 / 字段 | 出处（契约 ID → 文件） |
|---|---|---|
| `RecommendationRunStatus`（run 状态） | `REQUESTED, CONTEXT_ASSEMBLING, HARD_FILTERING, MATCHING, PROPOSAL_READY, AWAITING_HUMAN, APPROVED, MODIFIED, REJECTED, HELD, STALE_REQUIRES_RERUN, FAILED_CLOSED` | `CTR-PR-RUN-001` → `product-recommendation-run.schema.json` |
| `RecommendationAttempt`（attempt） | `attemptId, kertRequestId, startedAt, finishedAt, status, errorCode, retryable`；`status ∈ {SUBMITTED, RUNNING, SUCCEEDED, FAILED, TIMEOUT, CONTRACT_MISMATCH}` | `CTR-PR-RUN-001` |
| run 幂等/快照字段 | `idempotencyKey, asOf, journeyId, operatingCaseId, recommendationObjective, currentVersionId, kertJobRef, snapshotRefs{customerFactSnapshotId, productKnowledgeSnapshotRef, ruleBundleRef, evidenceBundleId}` | `CTR-PR-RUN-001` |
| `RecommendationHumanDecision` 并发字段 | `proposalVersionId, expectedVersion（If-Match/ETag）, decision, modifications, reason, actorId, actorRole, decidedAt` | `CTR-PR-DEC-001` → `recommendation-human-decision.schema.json` |
| `RecommendationDecision`（决策值） | `APPROVE, MODIFY, REJECT, HOLD` | `CTR-PR-DEC-001` |
| `RecommendationProposalVersion`（方案版本） | `versionId, runId, resultRef, evidenceBundleId, contentHash, supersededBy, createdAt` | `CTR-PR-API-001` → `product-recommendation.openapi.json` |
| KERT 失败码 | `KERT_PERMISSION_DENIED, KERT_CONTEXT_INSUFFICIENT, KERT_PRODUCT_KNOWLEDGE_STALE, KERT_RULE_VERSION_MISSING, KERT_EXECUTION_TIMEOUT, KERT_CONTRACT_MISMATCH, KERT_EVIDENCE_INCOMPLETE, KERT_INTERNAL_ERROR` | `README.md §4`、`SP-15.md §6` |
| 端点 | `POST /product-recommendation-runs`、`GET .../{runId}`、`GET .../{runId}/stages`、`GET .../{runId}/versions/{versionId}`、`POST .../{runId}/retry` | `CTR-PR-API-001` |

---

## 1. ADR-PR-008｜创建 run 的幂等范围与重复请求语义

- ID：`ADR-PR-008`
- 状态：`Candidate`（`FROZEN=NO / IMPLEMENTED=NO`）

### Context（背景）

`POST /product-recommendation-runs` 是副作用入口：一次创建会调用 KERT 执行并落业务对象。网关重放、客户端重试、前端重复点击都会造成重复调用 KERT 与重复业务对象。需要在入口建立幂等，同时避免幂等范围过大而吞掉“用户主动改变时点/目的”的合法语义差异。

### Decision（决策）

1. 创建 run 的幂等范围 = `caller + customerId + journeyId/operatingCaseId + objectiveHash + asOf + Idempotency-Key`（权威设计 §10.1）。其中 `caller` 来自鉴权上下文，`objectiveHash` 由 `recommendationObjective` 内容哈希派生（非独立存储字段），`journeyId` 与 `operatingCaseId` 至少其一存在。
2. `Idempotency-Key` 请求头落库为 `ProductRecommendationRun.idempotencyKey`；在 `product_recommendation_run` 上按幂等范围建立唯一约束，命中即复用。
3. **相同幂等键的重复请求返回同一 `runId`，不重复调用 KERT**（验收 `TC-PR-010`；openapi create 描述“同一幂等键返回同一 run，不重复调用 KERT”）。
4. 幂等保护只作用于“创建 run”这一动作；幂等范围中的任一成分变化（如 `objectiveHash`/`asOf`/`customerId`/`journeyId·operatingCaseId`/`caller` 变化）即构成不同业务运行，应得到不同 `runId`，不得被旧键误复用。

### Consequences（后果）

- 正面：网络重试/重放不重复执行 KERT、不产生重复 run；“幂等键重复形成多个运行：0”可机器验证（交接总册 §11）。
- 负面/风险：`objectiveHash` 直接参与幂等范围，因此 `recommendationObjective` 的措辞变化会影响幂等命中；需由合同层澄清 `objectiveHash` 归一化口径（见 §6 未决 U-01）。
- 边界：幂等不覆盖 `retry`、`HumanGate decide`、CRM 写回等其他动作；`GET` 只读永不创建（见 ADR-PR-009）。

---

## 2. ADR-PR-009｜重试：attemptId 与方案版本化（不漂移、不覆盖、不重复 job）

- ID：`ADR-PR-009`
- 状态：`Candidate`（`FROZEN=NO / IMPLEMENTED=NO`）

### Context（背景）

KERT 执行可能技术失败或超时。重试必须同时满足：可追踪（保留每次轨迹）、不漂移（不因重试读到不同快照）、不重复（超时不重复建 job）、并与“需要刷新事实/产品版本的合法重跑”区分开。

### Decision（决策）

1. **每次重试产生新的 `attemptId`，但保留同一业务 `runId`**：`POST .../{runId}/retry` 追加一条 `RecommendationAttempt`（新 `attemptId` + 新 `kertRequestId`），旧 attempt 轨迹不覆盖（openapi retry 描述“新 attempt，不覆盖旧轨迹”）。
2. **技术重试默认复用同一客户/知识快照，避免漂移**：重试期间 `snapshotRefs{customerFactSnapshotId, productKnowledgeSnapshotRef, ruleBundleRef, evidenceBundleId}` 与 `asOf` 保持不变。
3. **刷新事实/产品/规则版本 ≠ 技术重试**：若需刷新事实或产品版本，必须创建新的 `RecommendationProposalVersion`（新 `versionId`），并把旧版本标记 `SUPERSEDED`——落地表示为旧版本 `supersededBy = 新 versionId`、`run.currentVersionId` 指向新版本（权威设计 §10.2；`RecommendationProposalVersion.supersededBy` 字段），不得原地改写已审核版本。
4. **GET 与页面刷新只读**：`GET .../{runId}`、`GET .../stages`、`GET .../versions/{versionId}` 均“无副作用；不得触发 KERT 生成或重试”（openapi 描述）。
5. **KERT 超时先查询原 execution 状态**：`attempt.status = TIMEOUT`（对应 `KERT_EXECUTION_TIMEOUT`）时，先按 `kertRequestId` 查询原 execution/job 状态，不得直接创建重复 job（验收 `TC-PR-011`；openapi retry 描述）。
6. **非技术失败不自动重试**：`KERT_PERMISSION_DENIED → FAILED_CLOSED`（不重试）；`KERT_CONTEXT_INSUFFICIENT → HELD`（生成核实任务）；`KERT_PRODUCT_KNOWLEDGE_STALE / KERT_RULE_VERSION_MISSING → FAILED_CLOSED`；`KERT_CONTRACT_MISMATCH → FAILED_CLOSED`；`KERT_EVIDENCE_INCOMPLETE → 不创建 HG-D01`（README §4）。只有 `retryable = true` 的 attempt 才允许走 retry 端点。

### Consequences（后果）

- 正面：attempt 级审计与可重放；超时不产生重复 KERT job；技术重试与版本刷新两条路径显式分离，结果漂移可控。
- 负面/风险：实现需在 `ProductRecommendationApplicationService` 显式分支“技术重试（复用快照）”与“版本刷新（升版 + `supersededBy`）”，不能用一个布尔标志含糊；旧实现 HumanGate 直接操作 Repository 的现状必须改造为应用服务编排。
- 未决：`KERT_INTERNAL_ERROR`“技术重试后仍失败则关闭本轮”的重试次数/退避策略待业务 Owner 给出（见 §6 U-02）。

---

## 3. ADR-PR-010｜并发：HumanGate 乐观并发与 409（不得覆盖）

- ID：`ADR-PR-010`
- 状态：`Candidate`（`FROZEN=NO / IMPLEMENTED=NO`）

### Context（背景）

两名客户经理（或同一人多端）同时打开同一待审方案并先后提交，后提交者若基于过期版本，可能静默覆盖先提交者的决定。需要乐观并发控制，保证决定不被覆盖。

### Decision（决策）

1. **HumanGate 决策必须携带 `proposalVersionId` 或 `If-Match/ETag`**：`RecommendationHumanDecision.proposalVersionId` 必填；等价乐观锁由 `expectedVersion`（“If-Match/ETag 并发校验”）承载（`CTR-PR-DEC-001`）。
2. **落地校验 INV-06**：`HumanDecision.proposalVersionId = run.currentVersionId`（README §2 `INV-06`）；不相等即视为过期提交。
3. **两人同时审核时，第二个（基于过期版本）提交返回 HTTP `409 Conflict`，不得覆盖第一人的决定**（权威设计 §10.3；openapi `Conflict` 响应）。不采用“最后写入者胜”。
4. 决策写入后：`APPROVE/MODIFY` 推进 `run.status` 至 `APPROVED/MODIFIED`（若 `MODIFY` 产生新方案版本则另建版本并 `supersededBy`）；`REJECT/HOLD` 分别推进至 `REJECTED/HELD`。全部记录 `actorId`、`decidedAt`、`reason`（`REJECT/HOLD` 必填）。

### Consequences（后果）

- 正面：推荐决定不会被静默覆盖，先后与原因可审计；`TC-PR-012`（待审期间版本更新 → 阻止旧方案批准）可测。
- 负面/风险：需在 HumanGate 应用服务内做 `proposalVersionId`/`expectedVersion` 比较 + 事务/乐观锁；`HumanGateController` 现有“直接操作 Repository”的实现（交接总册 §9 差距 4）必须改为应用服务，不能绕过。
- 边界：并发控制只作用于 `RecommendationHumanDecision`，不改动通用 `GateDecision` 枚举；`REJECT` 与 `DECLINE` 语义待 `OQ-04` 裁决，本 ADR 不自行裁决。

---

## 4. ADR-PR-011｜过期：`STALE_REQUIRES_RERUN` 触发与版本保留

- ID：`ADR-PR-011`
- 状态：`Candidate`（`FROZEN=NO / IMPLEMENTED=NO`）

### Context（背景）

待审方案依赖的上游事实/知识/规则/权限/经营目标在其生成后可能变化；沿用旧结论批准会造成错误决策。需要明确的过期触发清单与“过期≠删除”的保留策略。

### Decision（决策）

1. **触发条件**：发生以下任一变化，`ProductRecommendationRun.status` 转为 `STALE_REQUIRES_RERUN`（`RecommendationRunStatus` 枚举；状态机 `PROPOSAL_READY → STALE_REQUIRES_RERUN`）：
   1. Need 内容、确认状态或版本变化；
   2. `ProductVersion` 失效或关键条款变更；
   3. Eligibility/组合规则版本变化；
   4. 权限撤销；
   5. 经营目标改变；
   6. 超过业务 Owner 定义的有效期。
   （来源：权威设计 §10.4 + 本体交接总册 §8 + README §2 `INV-08`。）
2. **STALE 不自动删除**：保留旧 `RecommendationProposalVersion`、新旧差异（diff）、以及重跑/重审决策记录；重跑走 ADR-PR-009 的“新版本 + `supersededBy`”路径，不物理删除旧版本。
3. **STALE 阻断批准**：HumanGate 前置校验（§3.3.2：最新版本 / 快照与知识版本无影响变化 / 证据哈希一致 / 核心候选 `ELIGIBLE` / 高风险意见齐备 / 操作者有权限）任一失败，门禁转 `STALE_REQUIRES_RERUN` 或 `HOLD`，不得沿用旧结果批准。

### Consequences（后果）

- 正面：`INV-08` 可机器检测；`TC-PR-012` 可测；过期方案不会进入批准，审计链完整。
- 负面/风险：STALE 触发涉及 Need/ProductVersion/Rule/权限/目标/有效期多源，必须由 GITS Domain 统一聚合过期判断（不能靠前端或 KERT job 状态做第二权威源，§4.1）；触发清单中“经营目标改变/超有效期”需业务 Owner 落地为可执行信号。
- 未决：推荐方案有效期与触发重跑的变化清单待业务 Owner 裁决（`OQ-05`）。

---

## 5. 契约自洽核对表（Decision ↔ 落地 schema 枚举/字段）

| 决议 | 关键语义 | 落地字段/枚举（出处） |
|---|---|---|
| A 幂等 | 幂等范围、同键返回同一 run | `idempotencyKey`、`customerId`、`journeyId`、`operatingCaseId`、`asOf`、`recommendationObjective`（→ `objectiveHash`）（`CTR-PR-RUN-001`）；`Idempotency-Key` header（`CTR-PR-API-001`） |
| B 重试 | 新 attempt、保留 run | `RecommendationAttempt.attemptId / kertRequestId / status / retryable / errorCode`（`CTR-PR-RUN-001`） |
| B 重试 | 复用快照、不漂移 | `snapshotRefs{customerFactSnapshotId, productKnowledgeSnapshotRef, ruleBundleRef, evidenceBundleId}`（`CTR-PR-RUN-001`） |
| B 重试 | 刷新→新版本、旧版本 SUPERSEDED | `RecommendationProposalVersion.supersededBy` + `currentVersionId`（`CTR-PR-API-001` / `CTR-PR-RUN-001`） |
| B 重试 | GET 只读、超时先查原 execution | `GET` 端点“无副作用”（`CTR-PR-API-001`）；`attempt.status=TIMEOUT` ↔ `KERT_EXECUTION_TIMEOUT`；`kertRequestId`（`CTR-PR-RUN-001` + `README §4`） |
| C 并发 | 决策带版本、过期 409 | `proposalVersionId`、`expectedVersion`（If-Match/ETag）（`CTR-PR-DEC-001`）；`Conflict` 响应（`CTR-PR-API-001`）；`INV-06`（README §2） |
| D 过期 | STALE 状态 | `RecommendationRunStatus.STALE_REQUIRES_RERUN`（`CTR-PR-RUN-001`）；`INV-08`（README §2） |

---

## 6. 差异与未决问题（如实登记）

| 编号 | 问题 | 现状 | 建议处置 |
|---|---|---|---|
| U-01 | `objectiveHash` 归一化 | run schema 的 `idempotencyKey` 描述为“幂等范围 = caller + customerId + journeyId/operatingCaseId + objectiveHash + asOf”（不含 `Idempotency-Key` 自身）；权威设计 §10.1 与本派工口径为“… + objectiveHash + asOf **+ Idempotency-Key**”。 | 本 ADR 采用 §10.1/派工口径（含 `Idempotency-Key`）；待 schema `idempotencyKey` 描述与 `objectiveHash` 归一化口径由 OpenAPI Owner 收口。 |
| U-02 | `KERT_INTERNAL_ERROR` 重试策略 | “技术重试后仍失败则关闭本轮”，但次数/退避未定。 | 业务 Owner 给出重试上限与退避；在契约层以 `retryable` 约束。 |
| U-03 | `409` 语义 | openapi `Conflict` 描述为“幂等键重复或并发版本过期”，把两类 409 合并。 | 本 ADR 采纳“同键 → 返回同一 run（200）”“并发版本过期 → 409”两分；建议 OpenAPI Owner 收口 `Conflict` 描述，避免误读。 |
| U-04 | `SUPERSEDED` 表示法 | 权威设计 §10.2 写作“标记旧版本 SUPERSEDED”；落地 schema 无版本状态枚举，以 `RecommendationProposalVersion.supersededBy`（字符串指针）+ `run.currentVersionId` 表达。 | 本 ADR 以落地字段为准；“SUPERSEDED”仅作业务标签。 |
| U-05 | `HELD` vs `NEEDS_DATA` | 权威设计 §7.5 写作 `KERT_CONTEXT_INSUFFICIENT → run=HELD/NEEDS_DATA`；落地 `RecommendationRunStatus` 仅含 `HELD`，无 `NEEDS_DATA`。 | 本 ADR 以枚举 `HELD` 为准；`NEEDS_DATA` 待合同收口，不擅自新增枚举。 |
| U-06 | `REJECT` vs `DECLINE` | 通用 `GateDecision` 含 `DECLINE`，`RecommendationDecision` 仅 `APPROVE/MODIFY/REJECT/HOLD`。 | 待 HumanGate Contract Owner 裁决（`OQ-04`）；本 ADR 不自行解释。 |
| U-07 | ADR 编号 | `docs/adr/ADR-PR-CANDIDATES.md`（在 WP0-1 stash 内）已占用 `ADR-PR-001~007`（三段式架构候选）。 | 本文件使用 `ADR-PR-008~011`，延续编号；不覆盖、不依赖 001~007 的落地状态。 |
| U-08 | 契约可见性 | step 3 契约当前被 WP0-1 隔离在 `git stash@{0}`，工作树不可见。 | 本 ADR 只读引用；由 WP0-1 责任方决定 pop/提交时点，本任务不 pop。 |

---

## 门禁结论

```text
DOCUMENT_STATUS=CANDIDATE
FROZEN=NO
IMPLEMENTED=NO
REAL_E2E_PASS=NO
ADR_STATUS=Candidate（不得视为 Accepted / Frozen / Implemented）
NEXT_GATE=Owner 评审（含 OQ-04/OQ-05 裁决）+ KERT Gate 0 + ProductMatch 三方漂移关闭
```

本文件只沉淀“幂等、重试、并发、过期”四条候选决议，不构成任何“已批准、已冻结、已实现、已联调或生产就绪”声明；落地顺序受《详细落地方案 V1.0》§17 的 Tech Lead 执行顺序约束。
