# FO-02 产品推荐领域模型唯一归属合并（CANDIDATE）

```text
文档编号   = FO-02_DOMAIN_MODEL_CONSOLIDATION
角色       = GITS/MAIN
任务       = FO-02（GITS 领域模型合并）
批次       = GITS-WP4（见 docs/dispatch 派工清单）
状态       = CANDIDATE
FROZEN     = NO
IMPLEMENTED = NO
形成日期   = 2026-09-01
权威依据   = HLD §6.1（scenario-customer-journey 领域落点）+
             三段式落地方案 V1.0 §4.1 +
             DKWS_GITS_STATE_MAPPING_CANDIDATE.md §3.1（GITS 业务状态机权威）+
             specs/product-recommendation/product-recommendation-run.schema.json（CTR-PR-RUN-001）+
             adapters/persistence-relational V020__product_recommendation.sql（五张表列）
```

> 本文件是 FO-02 领域模型唯一归属合并的**候选登记**，只登记取证结果、唯一归属决策、迁移/删除清单与影响面，不宣称任何冻结、实施或联调结论。

---

## 0. 取证结果（先取证，再下结论）

本轮对比了产品推荐领域模型的**两处定义**：

| # | 位置 | 类 | 性质 |
|---|---|---|---|
| 1 | `modules/scenario-customer-journey/.../customerjourney/recommendation/` | `ProductRecommendationRun` / `RecommendationProposalVersion` / `ProductRecommendationRunStatus` / `RecommendationStage` | WP4-1 **权威**（HLD §6.1 落点；状态机忠实复刻 §3.1） |
| 2 | `modules/operational-ontology/.../ontology/domain/` 与 `ontology/port/` | `ProductRecommendationRun`（重复）+ `RecommendationProposalVersion`（重复）+ `RecommendationRunStatus`（重复）+ `RecommendationAttempt` / `RecommendationAttemptStatus` / `RecommendationDecision` / `RecommendationFeedback` / `RecommendationHumanDecision` / `RecommendationGatePreconditionException` / `RecommendationVersionConflictException`（互补）+ `port/ProductRecommendationRepository` / `port/RecommendationAuthorizationPort`（端口） | WP4-2 额外创建；`ProductRecommendationRun` / `RecommendationProposalVersion` / `RecommendationRunStatus` 与 WP4-1 重复 |

**关键差异**：

- WP4-1 的 `ProductRecommendationRun` 采用 `UUID` 强类型标识、无持久化字段；WP4-2 的 `ProductRecommendationRun` 采用 `String` 标识并携带 `needVersionIds / requestedProductDomains / kertJobRef / snapshotRefs`，且其迁移表与 §3.1 权威状态机**不一致**（例如 WP4-2 允许 `REQUESTED -> FAILED_CLOSED` / `REQUESTED -> HELD`，§3.1 权威图只允许 `REQUESTED -> CONTEXT_ASSEMBLING`）。
- 契约 schema（CTR-PR-RUN-001）与 V020 迁移均以 **字符串（`CHAR(36)`）** 表达 `runId / journeyId / operatingCaseId`，枚举名为 `RecommendationRunStatus`，且含 `needVersionIds / requestedProductDomains / kertJobRef / snapshotRefs`。

**一句话结论**：WP4-1 拥有**状态机语义权威**（19 条合法迁移），但字段形状与契约/库表脱节；WP4-2 的字段形状与契约/库表一致，但其状态机偏离 §3.1。合并方向 = **以 WP4-1 的 §3.1 权威状态机为准，吸收 WP4-2 的持久化字段，统一落到 scenario-customer-journey 的 recommendation 包**。

---

## 1. 唯一归属决策

1. **唯一归属模块**：`modules/scenario-customer-journey`（HLD §6.1 领域落点），包 `com.gien.gits.customerjourney.recommendation`。
2. **唯一权威状态机**：`ProductRecommendationRun` 内嵌的 19 条合法迁移表（忠实复刻 DKWS_GITS_STATE_MAPPING_CANDIDATE.md §3.1 状态机图 + 补充语义）。`REQUESTED` 的唯一后继为 `CONTEXT_ASSEMBLING`；`HELD` 可恢复到 `CONTEXT_ASSEMBLING` / `AWAITING_HUMAN`；终态（`APPROVED/MODIFIED/REJECTED/FAILED_CLOSED`）与 `STALE_REQUIRES_RERUN` 无出边。
3. **标识字段类型**：字符串（对齐 schema 与 V020 迁移 `CHAR(36)`），非 `UUID` 强类型。WP4-1 单元测试中原 `UUID` 字面量机械替换为 `UUID.randomUUID().toString()`，状态机语义不变。
4. **状态枚举名**：保留 WP4-1 的 `ProductRecommendationRunStatus`（12 值闭集）；删除 WP4-2 的重复 `RecommendationRunStatus`。
5. **端口归属**：`ProductRecommendationRepository` / `RecommendationAuthorizationPort` 归入 `com.gien.gits.customerjourney.recommendation.port`（recommendation 包树内的 port 子包，沿用模块既有 port 约定）。
6. **状态推进对齐修正**：应用服务 `onKertFailure` 原直接从 `REQUESTED` 迁 `HELD / FAILED_CLOSED`（依赖 WP4-2 偏离的迁移表）；合并后修正为 `REQUESTED -> CONTEXT_ASSEMBLING -> HELD / FAILED_CLOSED`，与 §3.1 权威图一致，且不改变测试断言的终态（`HELD` / `FAILED_CLOSED`）。

---

## 2. 迁移清单（新增/合并到 scenario-customer-journey）

| 目标文件（`modules/scenario-customer-journey/src/main/java/com/gien/gits/customerjourney/`） | 来源 | 处置 |
|---|---|---|
| `recommendation/ProductRecommendationRun.java` | WP4-1 权威 + WP4-2 字段 | **合并**：String 字段 + 权威状态机 + 双方法集（`decide` / `applyDecision` / `markStaleIfExpired` / `withProposal` / `withCurrentVersionId` / `create`） |
| `recommendation/RecommendationProposalVersion.java` | WP4-1 权威 + WP4-2 字段 | **合并**：String `runId` + `payload` 字段 + `create` / `withSupersededBy` / `isSuperseded` |
| `recommendation/ProductRecommendationRunStatus.java` | WP4-1 | 保留（权威 12 值枚举） |
| `recommendation/RecommendationStage.java` | WP4-1 | 保留 |
| `recommendation/RecommendationAttempt.java` | WP4-2 | 迁移（仅改 package） |
| `recommendation/RecommendationAttemptStatus.java` | WP4-2 | 迁移（仅改 package） |
| `recommendation/RecommendationDecision.java` | WP4-2 | 迁移（仅改 package） |
| `recommendation/RecommendationFeedback.java` | WP4-2 | 迁移（仅改 package） |
| `recommendation/RecommendationHumanDecision.java` | WP4-2 | 迁移（仅改 package） |
| `recommendation/RecommendationGatePreconditionException.java` | WP4-2 | 迁移（仅改 package） |
| `recommendation/RecommendationVersionConflictException.java` | WP4-2 | 迁移（仅改 package） |
| `recommendation/port/ProductRecommendationRepository.java` | WP4-2 | 迁移（package + 领域类 import 指向新包） |
| `recommendation/port/RecommendationAuthorizationPort.java` | WP4-2 | 迁移（仅改 package） |

---

## 3. 删除清单（operational-ontology）

删除 `modules/operational-ontology/src/main/java/com/gien/gits/ontology/` 下 12 个文件：

- `domain/ProductRecommendationRun.java`（重复）
- `domain/RecommendationProposalVersion.java`（重复）
- `domain/RecommendationRunStatus.java`（重复）
- `domain/RecommendationAttempt.java`（迁移）
- `domain/RecommendationAttemptStatus.java`（迁移）
- `domain/RecommendationDecision.java`（迁移）
- `domain/RecommendationFeedback.java`（迁移）
- `domain/RecommendationHumanDecision.java`（迁移）
- `domain/RecommendationGatePreconditionException.java`（迁移）
- `domain/RecommendationVersionConflictException.java`（迁移）
- `port/ProductRecommendationRepository.java`（迁移）
- `port/RecommendationAuthorizationPort.java`（迁移）

> 注：`operational-ontology` 的通用门禁/本体类（`HumanGate` / `HumanGateRepository` / `GateDecision` / `GateType` 等）**不属于**产品推荐领域，保持原位不动。

---

## 4. 影响面（import 指向唯一来源）

以下文件的 import 由 `com.gien.gits.ontology.domain/port.*` 改指 `com.gien.gits.customerjourney.recommendation.*`（`RecommendationRunStatus` → `ProductRecommendationRunStatus`），**逻辑不变**：

| 文件 | 变更 |
|---|---|
| `apps/api/.../service/ProductRecommendationApplicationService.java` | import 改指 + `RecommendationRunStatus`→`ProductRecommendationRunStatus` + `onKertFailure` 经 `CONTEXT_ASSEMBLING` 推进 |
| `adapters/persistence-relational/.../JdbcProductRecommendationRepository.java` | import 改指 + 枚举名改指 |
| `apps/api/.../service/ProductRecommendationApplicationServiceTest.java` | import 改指 + 枚举名改指 |
| `adapters/persistence-relational/.../JdbcProductRecommendationRepositoryIT.java` | import 改指 + 枚举名改指 |
| `modules/scenario-customer-journey/.../recommendation/ProductRecommendationRunTest.java` | UUID 字面量 → String（15 参构造），状态机断言不变 |
| `apps/api/.../config/ProductRecommendationConfig.java`（并发 WP5-2） | import 机械改指（无逻辑改动） |
| `apps/api/.../controller/RecommendationExceptionHandler.java`（并发 WP5-2） | import 机械改指（无逻辑改动） |
| `apps/api/.../dto/RecommendationHumanDecisionRequest.java`（并发 WP5-2） | import 机械改指（无逻辑改动） |
| `apps/api/.../service/ProductRecommendationHumanGateService.java`（并发 WP5-2） | import 机械改指（无逻辑改动） |
| `apps/api/.../service/ProductRecommendationHumanGateServiceTest.java`（并发 WP5-2） | import 机械改指（无逻辑改动） |
| `apps/api/.../controller/HumanGateControllerTest.java`（并发 WP5-2） | import 机械改指（无逻辑改动） |

> 标注「并发 WP5-2」的文件为本批其他任务并发产出；本次仅对**被迁移类**的 import 做机械 package 改指（保持其业务逻辑与语义不变），以维持 `apps/api` 全量编译（「全程保持编译」）。如并发任务后续重写这些文件，需自行对齐到唯一来源 `com.gien.gits.customerjourney.recommendation`。

---

## 5. 状态推进语义不变性（自证要点）

- 19 条合法迁移表：`ProductRecommendationRunTest` 全覆盖（`allLegalTransitionsAreAccepted`）。
- 终态无出边：`illegalTransitionsAreRejected` + `failedClosedIsTerminal`。
- 过期 → `STALE_REQUIRES_RERUN`：`proposalReadyBecomesStaleAfterValidityExpires`。
- 决定并发（INV-06）：`decide` 版本校验 + `StaleProposalVersionException`（`decisionWithStaleVersionIsRejected`）。
- 幂等/并发/状态推进：`ProductRecommendationApplicationServiceTest`（幂等同键、并发同键、KERT fail-closed/HELD、决定前置校验）+ `JdbcProductRecommendationRepositoryIT`（V020 五表读写 + 唯一约束）。
