# ONTO1｜L4 集成契约注册表治理设计（DRAFT）

| 项 | 值 |
|---|---|
| 文档性质 | **DRAFT（草稿）**——候任 Integration Contract Owner 任职技术准备产出，**未生效、未签署** |
| 状态 | `DRAFT` / `NOT_ACTIVE`；不得标 `ACTIVE`、不得标 `OWNER_ACTIVATED` |
| 所属 Loop | `loops/ONTO1-ontology-split/`（Wave -1 只读分析；Wave 0 及以后须 `DESIGN_APPROVED`） |
| 设计依据 | `docs/architecture/ONTOLOGY-SPLIT-DESIGN-V2.0-REVIEW.md` §3.1、§4.4、§6.5、§6.6；`docs/review/ARCH-ONTO-2026-001-rereview-package/07-兼容性矩阵-major-minor-patch.md`；`06-验证状态模型与状态跃迁表.md` |
| 执行依据 | `docs/dispatch/ONTO-SPLIT-本体四层落地执行计划-V2.0.md` §1（角色）、§5.1（合同登记拆条）、§7（门禁） |
| 门禁现状 | `RETURN_TO_HLD` 仍有效。本文**不代表** `DESIGN_APPROVED`，不代表 L4 已获批、不代表 CQ4/CQ5 可标 `PASS` |
| 事实基线 | `specs/CONTRACT_INDEX.yaml`（62 条合同，本轮**只读**）；`specs/semantic/gits-core.owl.ttl` `sha256:705578d6324abd0c…` |

> **红线声明（必读）**
> 1. 本文未改动 `specs/CONTRACT_INDEX.yaml`、未改动 `generated/`、未执行 `make generate`；
> 2. 本文不标 `ACTIVE`、不签发任何符合性声明、不代签任何 Owner 决议；
> 3. 文中所有 `PROPOSED_*` / 待裁定项均为**提案**，须由人类 Owner 裁决后才可落地；
> 4. 现状字段一律**回源**到 `文件:行`；本文不含未经回源的推断。

---

## 0. 设计目标与最小性判据

**目标**：L4 是"跨系统端点、消费者、版本绑定和兼容性"的唯一登记面（设计 §3.2 第 5 行）。治理设计要回答四个问题：

| # | 问题 | 对应对象 |
|---|---|---|
| Q-A | 某个能力**现在能不能被消费**？ | `CapabilityPublication` + `EndpointBinding` |
| Q-B | **谁**被允许消费、消费了什么版本？ | `ConsumerBinding` + `ContractVersion` |
| Q-C | 一次激活**用了哪一版**资产与语义？ | `ActivationContract`（+ CQ4 的 planHash 版本子块） |
| Q-D | 任务类型的**受控取值**从哪来？ | `TaskTypeScheme`（SKOS） |

**最小性判据（本设计的取舍规则，先定规则再列字段）**：

> 一个字段是"必要"的，当且仅当**去掉它会导致下列任一项无法判定**：
> ① CQ4/CQ5 的判定（设计 §6.6）；
> ② 兼容性级别判定（07 号矩阵）；
> ③ 验证状态记录与门禁映射（06 号 §3）；
> ④ 碰撞检查 C-1~C-4（ADR §5.4）；
> ⑤ 授权与责任的具名归属（设计 §3.2）。
>
> 不满足上述任一项的字段，一律**不入最小集**（列入"可选/扩展"，需 Owner 批准后加入）。

**反向纪律**：最小集不等于"少写"。**缺少必要字段 = 无法判定 = 不得以 `NOT_EVALUATED` 或 `WAIVED` 充当通过**（06 号 §3 激活门禁）。

---

## 1. 治理对象总览

| 对象 | 制品形式 | 层 | T-Box / 定义 Owner | 记录 Owner | 实例 ID 空间（提案） |
|---|---|---|---|---|---|
| `ActivationContract` | JSON Schema | L4 | Integration Contract Owner | 契约注册中心 | `AC-*`（**既有**，见 §3.1） |
| `CapabilityPublication` | JSON Schema | L4 | Integration Contract Owner | 契约注册中心 | 沿用既有物（`SIM-CAP-*`） |
| `EndpointBinding` | JSON Schema / OpenAPI 片段 | L4 | Integration Contract Owner | 契约注册中心 | `EPB-*`（提案） |
| `ConsumerBinding` | JSON Schema | L4 | Integration Contract Owner | 契约注册中心 | `CSB-*`（提案） |
| `ContractVersion` | JSON Schema（原设计为 LinkML，见 §7 待裁定 T-1） | L4 | Integration Contract Owner | 契约注册中心 | 由 `contractId + semVer` 复合，不单设前缀 |
| `TaskTypeScheme` | **SKOS**（RDF 词表，非 OWL 类） | L4 词表 | 词表 Owner（**任命待裁定**，见 `memory/OWNER_REQUESTS.md` §A） | 注册中心 | 概念前缀 `TT-*`（提案） |

**ID 空间不新造的红线**：`AC-*` 已被既有制品占用（`specs/knowledge-architecture/schemas/activation-contract.schema.json:10`，pattern `^AC-[A-Z0-9-]+$`），且 GK-KE 已裁定**设计期 AC ID 不得复用为运行期 planId**（`specs/gk-ke/v1/schemas/ActivationPlan.schema.json` 属性 `planId.description` + `pattern` = `^(?!AC[-_]).+$`）。L4 任何新对象**不得**复用 `AC-` 前缀承载新语义。

---

## 2. 版本语义（跨对象统一口径）

设计 §6.5 与 07 号矩阵已定级，L4 只需把它落到**字段级**：

| 口径 | 规定 | 依据 |
|---|---|---|
| 版本号形态 | 语义版本 `MAJOR.MINOR.PATCH`；`versionIRI` 承载语义版本 | 07 号 §3 第 1 条 |
| 版本 + 内容哈希双钉 | 版本号**不单独**作为完整性依据，必须同时校验内容哈希（项目加严，非 W3C/GB 强制） | 设计 §6.4 |
| 兼容级别 | `patch` / `minor` / `major` 三值，判定权在 07 号矩阵；**"只增"不自动等于 minor**（新增约束可为 major 候选） | 07 号 §1、§2 |
| 弃用期 | `major` 变更须 ≥1 发布周期**新旧双发布**；旧项标 `owl:deprecated` + 弃用映射 | 07 号 §3 |
| import closure | 同一 ontology series 不得同时出现两个 `versionIRI` | 设计 §6.4、ADR §5.2 退役门第 3 条 |
| 回滚 | 保留上一版本只读；回滚 = 消费方重钉旧 `versionIRI` + 哈希 | 07 号 §3 末条 |

**L4 的落点**：`ContractVersion.compatibilityLevel` 必须**显式记录级别**，不得留空由读者推断——因为激活门禁需要机器判定"本次变更是否需要一个弃用期"。空值 ⇒ 门禁 FAIL（fail-closed）。

---

## 3. 各对象最小字段集

> 约定：`R` = required（缺失 ⇒ 门禁 FAIL）；`C` = conditional（另一字段触发时必填）；`O` = optional（扩展）。
> "现状"列指本工作区既有制品中**已经存在**的等价字段（有则回源，无则标"无"）。

### 3.1 `ActivationContract`（最小字段集）

**关键结论（避免重复造物）**：ActivationContract 的 Schema **已经存在且已登记**：
- 制品：`specs/knowledge-architecture/schemas/activation-contract.schema.json`
- 登记：`specs/CONTRACT_INDEX.yaml:307`（`CTR-ACTIVATION-001`，kind `json_schema`，owner `activation_contract_owner`，compatibility `explicit_migration`）
- 既有 13 项 required：`schemaVersion` / `contractId` / `version` / `taskType` / `routeMode` / `preconditions` / `activations` / `semanticQueries` / `ruleChecks` / `skills` / `context` / `humanGates` / `failurePolicy`（回源：该 schema `required` 数组）

**因此本设计的立场是"不改语义、只补治理"**：

| 字段 | R/C/O | 类型 | 语义 | 是否新增 | 依据 |
|---|---|---|---|---|---|
| `contractId` | R | string `^AC-[A-Z0-9-]+$` | 契约身份 | 既有 | 既有 schema:10 |
| `version` | R | semver | 契约版本 | 既有 | 07 号 §3 |
| `taskType` | R | string → **必须取值于 `TaskTypeScheme`** | 任务类型 | 既有字段，**约束加严** | 设计 §4.5（TaskType 转 SKOS）；⚠️ 加严属 **major 候选**（07 号 §2.1），须走兼容流程 |
| `routeMode` | R | enum 4 值 | 路由模式 | 既有 | schema:13 |
| `preconditions.permissionDecisionRequired` | R | boolean | 是否需要权限裁决 | 既有 | CQ5 `UNAUTHORIZED` 判定入口 |
| `failurePolicy` | R | enum `FAIL_CLOSED`/`DEGRADE_WITH_DISCLOSURE` | 失败策略 | 既有 | 与 ADR §5.3 fail-closed 口径对齐 |
| `publicationStatus` | **O（提案）** | enum（见 §4） | 契约自身发布状态 | **新增提案** | CQ5 需要区分"未发布" |

**提案（待裁定）**：`publicationStatus` 是否加入 ActivationContract，或统一由 `ContractVersion` 承载？—— 本草案**倾向后者**（单一版本对象承载状态，避免同一语义两处登记）；标为待裁定 **T-2**（§7）。

### 3.2 `CapabilityPublication`（最小字段集）

现状回源：`specs/gk-ke/v1/schemas/Capability.schema.json`（登记于 `specs/CONTRACT_INDEX.yaml:943`，`CTR-GKKE-017`），required 13 项且 `simulationOnly` 为 `const true`（**SIM 阶段专用**）；实例侧见 `specs/knowledge-architecture/registry/Capability.json`（含 `probeStatus` / `callable` / `readiness` / `providerKind` / `endpoint` / `bindingVerdict` / `bindingAuthority`）。

| 字段 | R/C/O | 类型 | 语义 | 现状 | 依据 |
|---|---|---|---|---|---|
| `capabilityId` | R | string | 能力身份（沿用既有 ID 空间，不新造前缀） | 两处均有 | 设计 §4.4 |
| `version` | R | semver | 能力版本 | 有 | 07 号 §3 |
| `publicationStatus` | R | enum（§4） | 发布状态 | **CQ5 现状隐含于 fixture 的 `status=DRAFT`** | CQ5 fixture `positive` ① |
| `providerKind` | R | enum（`GK_KE_LOCAL_PROVIDER` / `KERT_SKILL` / …） | 执行器归属，决定端点绑定方式 | 有（实例侧） | registry `Capability.json` 实例字段 |
| `executorRef` | R | string | 执行器引用 | 有 | schema required |
| `inputSchemaRef` / `outputSchemaRef` | R | string | 交换契约引用 | 有 | schema required |
| `sideEffect` | R | enum `NONE`/`READ_ONLY`/`WRITE_BACK` | 副作用等级 | 有 | schema required |
| `permissionRef` | R | string | 权限引用（`UNAUTHORIZED` 判定入口） | 有 | CQ5 |
| `budget` / `timeoutMs` | R | object / integer | 资源约束 | 有 | schema required |
| `idempotencyPolicy` | R | enum | 幂等策略 | 有 | schema required |
| `probeStatus` | R | enum `PASSED`/`FAILED`/`NOT_PROBED` | 运行探针状态 | 有（实例侧，schema 未含） | registry 实例 `callableRule` |
| `callable` | R | boolean | 可运行性 | 有（实例侧） | registry `callableRule`：`probeStatus ≠ PASSED ⇒ callable 必须 false`（**"IMPLEMENTED ≠ callable"**） |
| `simulationOnly` | R | boolean | 模拟数据身份 | 有（`const true`） | 设计 §3.2 SIM 特别裁定 |

**重要缺口（诚实登记）**：`probeStatus` / `callable` 存在于**实例登记文件**，但**不在** `CTR-GKKE-017` 的 schema 里（schema 为 SIM-only 交换剖面）。`CapabilityPublication` 若要成为 L4 治理对象，必须明确这两组登记哪个是权威——否则 CQ5 会读到一个 schema 不承认的字段。列为待裁定 **T-3**。

**SIM 退出条件**：`simulationOnly=true` 的登记不得静默升级为企业权威（设计 §3.2），L4 需登记**退出条件引用**字段（提案：`simExitConditionRef`，O）。

### 3.3 `EndpointBinding`（最小字段集）

现状回源：`specs/knowledge-architecture/registry/provider-bindings.json`（`bindings[]`、`bindingVerdict`、`authority.crossRepoAuthorization`、`anchors.{gitsCbanking,kert}`、`forbiddenInferences[]`）。

| 字段 | R/C/O | 类型 | 语义 | 现状来源 | 依据 |
|---|---|---|---|---|---|
| `bindingId` | R | string `EPB-*`（提案） | 绑定身份 | 无（新增） | 设计 §4.4 |
| `capabilityId` | R | string | 被绑定的能力 | 实例侧 `endpoint`/`providerKind` | CQ5 `NO_ENDPOINT` |
| `capabilityVersion` | R | semver / range | 该绑定覆盖的版本 | 无 | CQ5 `VERSION_INCOMPATIBLE` |
| `endpointKind` | R | enum `HTTP_GRPC`/`IN_PROCESS`/`KERT_SKILL_DISPATCH`/`GK_KE_LOCAL` | 端点种类 | 部分（`providerKind` 相近） | 设计 §4.4 |
| `endpointRef` | R | string | 端点定位（URL / 服务名 / 包内类名） | 有（`endpoint`、`providerResolutionFacts`） | CQ5 |
| `resolutionMode` | R | enum `ONLINE`/`OFFLINE_CONTENT_ADDRESSED` | 解析方式 | 无（ADR U-2 未决） | ADR §5.3 |
| `bindingStatus` | R | enum `BOUND`/`UNBOUND`/`DEPRECATED` | 绑定状态 | `bindingVerdict` 相近 | CQ5 |
| `bindingEvidenceRef` | R | string | 绑定结论的依据（**必须可回源**） | 有（`bindingAuthority`） | `provider-bindings.json` 的 `forbiddenInferences` 纪律 |
| `contentHash` | C（`resolutionMode=OFFLINE_CONTENT_ADDRESSED` 时必填） | `^[0-9a-f]{64}$` | 内容哈希钉值 | 无 | ADR §5.3 路线 B |
| `validFrom` / `validTo` | R | date-time | 生效区间 | 无 | 06 号 §2 状态跃迁需时点 |
| `authnSchemeRef` | O | string | 认证方案引用 | 无 | 运维扩展 |

**禁止**：`endpointRef` 不得写入占位值（`localhost`、`example.com`、空串）—— 占位值必须判 `NO_ENDPOINT`，不是"已绑定"（与 `scripts/contract_pipeline.py:217` 的 `reject_placeholders` 同型纪律）。

### 3.4 `ConsumerBinding`（最小字段集）

现状回源：`specs/knowledge-architecture/contracts/ConsumerObligations.json`（`obligations[]`、`consumptionChains[]`、`proofOfConsumption`）；消费者扫描净义务见 `loops/ONTO1-ontology-split/evidence/consumer-scan-obligations.csv`（1 052 数据行 = `CONTROL_PLANE_REQUIRED` 14 + `FOLLOW_MIGRATION` 1038）。

| 字段 | R/C/O | 类型 | 语义 | 现状来源 | 依据 |
|---|---|---|---|---|---|
| `bindingId` | R | string `CSB-*`（提案） | 绑定身份 | 无 | 设计 §4.4 |
| `consumerId` | R | string | 消费方身份（GITS / KERT / 数据平台 等） | `consumptionChains[].downstream` 相近 | 三方评审规则 |
| `contractId` + `contractVersion` | R | string | 被消费合同与钉定版本 | 部分（`envelopeRef`） | CQ5 `VERSION_INCOMPATIBLE` |
| `authorizedScopes` | R | string[]（可空数组） | 授权范围（空 = 无任何授权，**不得**解释为全权） | 无 | CQ5 `UNAUTHORIZED` |
| `grantedBy` / `grantedAt` | R | string / date-time | 授权人与时点 | `authority.ownerDecision` 相近 | 设计 §3.2 授权链 |
| `validFrom` / `validTo` | R | date-time | 授权有效期（过期 ⇒ `UNAUTHORIZED`） | 无 | CQ5 fixture `positive` ③"缺失/过期" |
| `bindingStatus` | R | enum `ACTIVE`/`SUSPENDED`/`REVOKED`/`EXPIRED` | 绑定状态 | 无 | CQ5 |
| `obligationsRef` | O | string | 义务清单引用（`ConsumerObligations.json`） | 有 | `ConsumerObligations.json` `obligations[]` |
| `onMissingPolicyRef` | R | string | 缺字段时的处置策略引用 | 部分（`obligations[].onMissing`） | 消费者义务现有纪律 |

**铁律**：`authorizedScopes` 为**空数组 ≠ 全权**；空数组 + `bindingStatus=ACTIVE` 时必须判 `UNAUTHORIZED`（fail-closed，防空转）。

### 3.5 `ContractVersion`（最小字段集）

| 字段 | R/C/O | 类型 | 语义 | 依据 |
|---|---|---|---|---|
| `contractId` | R | string | 合同身份（`AC-`/`CTR-*`/`EPB-`/`CSB-`…） | 设计 §4.4 |
| `version` | R | semver | 版本号 | 07 号 §3 |
| `versionIRI` | R | IRI | 版本身份 IRI | 设计 §6.4 |
| `contentHash` | R | `^[0-9a-f]{64}$` | 制品内容哈希（双钉之一） | 设计 §6.4 |
| `compatibilityLevel` | R | enum `patch`/`minor`/`major` | 兼容级别（**显式**，禁空） | 07 号 §1 |
| `compatibleSet` | **C（`major` 时必填）** | object `{pinned[], min, max}` | 兼容集 | 07 号 §1、CQ5 ④"版本 ∉ 兼容集" |
| `supersedes` / `supersededBy` | O | versionIRI[] / versionIRI | 取代关系 | 07 号 §3 |
| `deprecation` | C（`major` 时必填） | object `{since, sunsetAt, migrationRef}` | 弃用期与迁移映射 | 07 号 §3 |
| `approvalRefs` | R | object[] `{ownerRole, decisionRef, at}` | 批准记录（**不含姓名字段**，姓名由人类 Owner 填） | 设计 §10 |
| `status` | R | enum（§4） | 发布状态 | 06 号 §1 映射 |

**指纹自引用禁止（历史教训固化）**：`contentHash` 是对**制品**的哈希，**不得**把该哈希写回被哈希的制品自身（GK-KE 程序 `FAIL-2026-09-12-03` 根因：指纹自引用导致永不收敛）。必须侧车登记（`_registry.json` 形态）。本设计把这一条写为 `ContractVersion` 的**结构性约束**，不是建议。

### 3.6 `TaskTypeScheme`（SKOS 最小字段集）

现状回源：`specs/semantic/gits-core.owl.ttl:65`（`gits:TaskType a owl:Class`）、`:81`（`gits:hasTaskType a owl:ObjectProperty`，range `:84`）。**全仓 `specs/` 当前零 `skos:` 使用**（回源：`grep -rl "skos:" specs/` 无输出）⇒ SKOS 词表为**全新制品类型**。

| 层级 | 字段 | R/O | 语义 | 依据 |
|---|---|---|---|---|
| Scheme | `schemeIRI` | R | 词表身份 | 设计 §4.4 |
| Scheme | `title` / `definition` | R | 词表名与定义 | §9 术语合同字段 |
| Scheme | `version` + `contentHash` | R | 版本与钉值 | 07 号 §3 |
| Scheme | `ownerRole` | R | 词表 Owner（**任命待裁定**） | `memory/OWNER_REQUESTS.md` §A 另需裁定 |
| Concept | `conceptIRI` + `notation`(`TT-*` 提案) | R | 概念身份与稳定标识 | §9 |
| Concept | `prefLabel@zh` / `prefLabel@en` | R | 双语首选标签 | §9 |
| Concept | `definition` | R | 精确定义 | §9 |
| Concept | `broader` | O | 上位概念 | SKOS 结构 |
| Concept | `status` | R | `ACTIVE`/`DEPRECATED`/`RETIRED` | 07 号 §2.2 |
| Concept | `replacedBy` | **C（`status≠ACTIVE` 时必填）** | 替代概念 | 07 号 §2.2"退役概念 = major（须 `owl:deprecated` + 替代映射）" |
| Concept | `mappingFromOld` | R | 旧 `gits:TaskType` IRI 的映射状态（`RETAINED`/`REMODELED`/…） | ADR §5.1 三分法 |
| Concept | `compatLevel` | R | 本次词表变更级别 | 07 号 §2.2 |

**词表变更规则（07 号 §2.2 落点）**：新增概念 = `minor`；退役概念 = `major`（须 `owl:deprecated` + 替代映射）；改定义不动 notation = `patch`/`minor` 评审。

---

## 4. 发布状态模型（单一枚举，全对象共用）

统一状态机（与 06 号五态**互补而非替换**：06 号管"验证状态"，本节管"发布状态"，二者不得混用）：

```
DRAFT ──▶ REVIEW ──▶ PUBLISHED ──▶ DEPRECATED ──▶ RETIRED
   │                    │
   └──▶ WITHDRAWN ◀─────┘        （撤回：从未生效或生效前撤销）
```

| 状态 | 含义 | 谁可置入 | 未决禁止 |
|---|---|---|---|
| `DRAFT` | 草案，未评审 | 起草人 | 不得被消费；CQ5 ⇒ `NOT_PUBLISHED` |
| `REVIEW` | 待三方评审 | Integration Contract Owner | 同上 |
| `PUBLISHED` | 已发布、可被授权消费 | **Owner 批准后** | — |
| `DEPRECATED` | 弃用期，仍双发布 | Owner | 弃用期结束前不得 `RETIRED` |
| `RETIRED` | 已退役，**记录不删** | Owner（含退役门四条） | 不得删除历史 |
| `WITHDRAWN` | 撤回 | Owner | 不得当作"从未存在"（须留痕） |

**硬约束（对应本次红线）**：本草案交付期间**禁止**将任何对象置为 `PUBLISHED`；`ACTIVE` **不是**本状态机的合法取值——避免与 `OWNER_ACTIVATED`（Loop 级）和 L1 契约库"ACTIVE 五条件"（计划 §4）混淆。**三套状态词汇必须物理分离**（GK-KE 程序 `OF-02` 教训：状态平面混用造成误判）。

### 4.1 发布状态 ↔ 验证状态（两平面，禁止互推）

| 情况 | 允许写法 | 禁止写法 |
|---|---|---|
| 制品已发布但无生产实例 | 发布状态 `PUBLISHED` + 验证状态 `NOT_EVALUATED` | 用 `PUBLISHED` 暗示验证通过 |
| 验证 `PASS` 但未发布 | 验证状态 `PASS` + 发布状态 `DRAFT` | 用 `PASS` 暗示可被消费 |
| 豁免 | 验证状态 `WAIVED_FOR_DEVELOPMENT` | 任何情况下替代激活门禁（06 号 §3） |

---

## 5. 授权模型（最小两跳）

设计 §3.2 要求"双方按批准合同消费；运行时验证版本、权限和状态"。L4 最小授权模型：

```
能力/合同（CapabilityPublication / ActivationContract）
   ▲ 发布授权：Owner 批准 → publicationStatus = PUBLISHED
   │
ConsumerBinding（consumerId × contractId@version × authorizedScopes × validFrom/To）
   ▲ 授权来源：grantedBy + grantedAt（具名，可追溯）
   │
EndpointBinding（bindingStatus = BOUND 且 endpointRef 非占位）
   ▲ 端点授权：crossRepoAuthorization（跨仓授权须显式登记，见 provider-bindings.authority）
```

**判定顺序（由 §6 的 CQ5 原因码短路序强制）**：发布 → 端点 → 授权 → 版本。任一环缺失即在该环具名拒绝，**不得**继续向后判定（否则产生混报）。

**跨仓授权**：KERT 侧执行器的绑定必须带 `crossRepoAuthorization` 依据（`provider-bindings.json` 已设此字段），否则视为 `NO_ENDPOINT`。

---

## 6. 兼容集与端点/消费者绑定的联动

| 联动点 | 规则 | 失败动作 |
|---|---|---|
| 版本 ∈ `compatibleSet` 但端点缺失 | 判 `NO_ENDPOINT`（优先级高于版本） | 不得报 `VERSION_INCOMPATIBLE` |
| 端点存在但版本 ∉ 兼容集 | 判 `VERSION_INCOMPATIBLE` | 不得静默放行 |
| `compatibilityLevel=major` 缺 `compatibleSet` | Schema 校验 FAIL | fail-closed |
| 消费者钉定版本已 `DEPRECATED` 且未过弃用期 | 允许消费 + 记录弃用告警 | 不得判 `VERSION_INCOMPATIBLE` |
| 弃用期已过（`sunsetAt < 查询时点`） | 判 `VERSION_INCOMPATIBLE` | — |

详见 `docs/architecture/ONTO1-CQ5-四态原因码与负例设计-DRAFT.md`。

---

## 7. 待裁定项（本草案**不自行决定**）

| # | 待裁定 | 为什么必须 Owner 决定 | 建议 |
|---|---|---|---|
| T-1 | `ContractVersion` 制品形式：JSON Schema（本草案）vs 原设计 §4.4 的 LinkML | 原设计写 LinkML，但 `scripts/contract_pipeline.py` 的 `linkml_subset` 只接受"LinkML 源 → JSON Schema + SHACL"，与"版本与兼容性记录"这类**实例型**对象不同构 | 维持 JSON Schema（本草案），并回写设计 §4.4 措辞 |
| T-2 | `publicationStatus` 归 `ActivationContract` 还是 `ContractVersion` | 同一语义两处登记 = 合同漂移源 | 归 `ContractVersion`（单一版本对象） |
| T-3 | `probeStatus` / `callable` 的权威位置（schema vs 实例登记） | CQ5 依赖它，但 `CTR-GKKE-017` 的 schema 未含 | 提升为 `CapabilityPublication` schema 字段 |
| T-4 | 词表 Owner 是否由公共语义 Owner 兼任 | `memory/OWNER_REQUESTS.md` §A 已列为"另需裁定" | 不预设 |
| T-5 | `EPB-*` / `CSB-*` / `TT-*` 前缀是否接受 | ID 空间一经发布难改 | 请一次裁定 |
| T-6 | L4 与既有 62 条合同的**重叠归并**（见 §8） | 涉及既有登记变更，非本草案权限 | 见 §8 三选一 |

---

## 8. L4 与既有合同登记的重叠分析（**本草案最重要的发现**）

`specs/CONTRACT_INDEX.yaml` 现有 **62 条**合同，其中多条**已经**覆盖了 L4 想登记的语义：

| L4 对象 | 既有登记（回源） | 重叠性质 | 处置建议（**待 Owner 裁定 T-6**） |
|---|---|---|---|
| `ActivationContract` | `CTR-ACTIVATION-001`（`specs/CONTRACT_INDEX.yaml:307` → `specs/knowledge-architecture/schemas/activation-contract.schema.json`） | **完全重叠** | **不新建**：收窄/沿用既有登记；L4 只补治理字段 |
| `CapabilityPublication` | `CTR-GKKE-017`（`specs/CONTRACT_INDEX.yaml:943` → `specs/gk-ke/v1/schemas/Capability.schema.json`） | **大部分重叠**（缺 `probeStatus`/`callable`/`publicationStatus`） | 三选一：① 扩 `CTR-GKKE-017`；② 新建 `CTR-SEM-005` 并把 `CTR-GKKE-017` 标 `superseded`；③ 分工（gk-ke/v1 为交换剖面，L4 为治理剖面） |
| `EndpointBinding` | **无独立登记**（`provider-bindings.json` 未被任何合同登记） | **零覆盖（真缺口）** | 新建（本草案 §3.3） |
| `ConsumerBinding` | `ConsumerObligations.json` 未被独立登记；消费者义务散落 | **部分覆盖** | 新建 + 与义务文件交叉引用 |
| `ContractVersion` | 各合同 `compatibility` 字段（单值，非对象） | **弱覆盖** | 新建（本草案 §3.5） |
| `TaskTypeScheme` | **无**（`gits:TaskType` 现为 `gits-core.owl.ttl:65` 的 owl:Class） | **转换制品类型** | 新建 SKOS + `TRANSFORMED` 映射状态（ADR §5.1） |

**结论**：若按原设计"直接新建 5 个 Schema + 1 SKOS"，会与既有 4 处登记产生**双处登记**（同一语义两个权威），这本身就是合同漂移。**必须先裁定 T-6 再动 Schema**。本草案的立场：**L4 新建范围收窄为 `EndpointBinding` / `ConsumerBinding` / `ContractVersion` / `TaskTypeScheme` 四项**，前两项（ActivationContract / CapabilityPublication）走"扩既有"路线。

**附带发现（越界提示，仅登记不改动）**：`CTR-SEM-001` 的源 `specs/semantic/gits-core.linkml.yaml` 含 **32 个类**，其中 `Customer` / `CorporateGroup` / `GroupRelationship` / `LegalEntity` / `Product`（L1）、`KnowledgeMap` / `Asset` / `Skill` / `ProductKnowledgeCard` / `ProductKnowledgeVersion`（L2）、`ActivationContract` / `Capability` / `TaskType`（L4）与 19 个 L3 类**混在同一制品**。因此"拆条"不是只拆 `CTR-SEM-002`——`CTR-SEM-001` 同为跨层混合源。详见 `docs/architecture/ONTO1-CTR-SEM-拆条登记草案-DRAFT.md` §5。

---

## 9. 门禁建议（提案，**不接线**）

| 门禁 ID（提案） | 命令（提案） | 判定 |
|---|---|---|
| `l4_registry_schema_check` | `python3 scripts/onto1_l4_registry_check.py --gate` | 五个对象 Schema 可解析 + 最小字段集齐备 + 无 `ACTIVE` 取值 + 无占位值 |
| `l4_registry_selftest` | `python3 scripts/onto1_l4_registry_check.py --selftest` | 删必需字段 / 置 `PUBLISHED` / 写占位端点 ⇒ 三种变异均 FAIL；对照 PASS |
| `cq5_reason_code_check` | 见 CQ5 设计文档 §5 | 四态可区分 + 优先级 + 负例全捕获 |
| `iri_collision_check` | 见碰撞检查脚本需求规格 | C-1~C-4 全绿 |

**接线前置**：`DESIGN_APPROVED` + T-1~T-6 裁定 + 角色任命。**本轮只出需求，不实现、不接线。**

---

## 10. 未决与阻塞（诚实登记）

| # | 未决/阻塞 | 级别 | 解除条件 |
|---|---|---|---|
| B-1 | Integration Contract Owner **未任命** ⇒ 本设计无人可批准 | 高 | Owner 任命（`memory/OWNER_REQUESTS.md` A-2） |
| B-2 | 词表 Owner 未裁定 ⇒ `TaskTypeScheme` 无发布权威 | 中 | §7 T-4 |
| B-3 | 三方评审规则无主体（无姓名/组织） | 高 | `docs/governance/ONTO1-三方评审召集规则-DRAFT.md` §6 待填 |
| B-4 | ADR 根域未签（D3）⇒ `EndpointBinding.resolutionMode` 无法终定 | 高 | D3 双 Owner 签署 |
| B-5 | `DESIGN_APPROVED` 未达 ⇒ 一切实现冻结 | 高 | 书面复审结论 |
| B-6 | L4 无生产实例 ⇒ 所有 L4 验证状态只能 `DESIGN_ONLY` / `NOT_EVALUATED` | — | 设计如此，**不得**标 `PASS` |

---

## 11. 变更记录

| 版本 | 日期 | 变更 | 作者 |
|---|---|---|---|
| DRAFT-v0.1 | 2026-09-20 | 初稿（任职技术准备，候任 Integration Contract Owner） | 候任 Integration Contract Owner（AI 起草） |

> 本文件为草稿，**签字权在人类 Owner**。
