# GK-KE L0-2 兼容与生成策略（V1.0）

> 角色：Tech Lead（planning_review）｜Loop：`GK1-l0-2-contract-activation`｜日期：2026-09-12
> 依据：C08 §2 L0-2 "定义兼容与生成策略"｜C08 §5 启动指令｜workspace 规则（合同 SSOT / 禁改 generated）
> 基线：GK-KE-CONTRACT-V1.0.2（HEAD `886f710` / tree `4c5f5373` / ZIP `b21638ab`）

## 1. 兼容性分级定义（本项目采用四级）

| 级别 | 含义 | 允许场景 | 激活要求 |
|---|---|---|---|
| `backward_compatible` | 只增可选字段；旧消费者无需改动 | 非闭集对象的新增可选字段 | 契约 Owner 备案 |
| `explicit_migration` | 语义等价但位置/形状变化；消费者需同步改动 | gk-ke/v1 全部新对象 | 契约 Owner + 语义 Owner 批准迁移映射 |
| `versioned_mapping` | 映射规则变更，需新版本号并行 | 数据源映射、R2RML | 数据 Owner 批准 |
| `no_silent_breaking_change` | 禁止静默破坏；破坏必须显式宣布 | 受控动作、智能体边界 | 业务 Owner 批准 |

> 依据：与 `specs/CONTRACT_INDEX.yaml` 既有 `compatibility` 词表一致（`backward_compatible` / `explicit_migration` / `versioned_mapping` / `versioned_decision` / `no_silent_breaking_change`），不发明新词。

## 2. gk-ke/v1 的兼容性判定

**结论：gk-ke/v1 整体为 `explicit_migration`。**

理由：
1. 20 个 schema 均为**新候选剖面**（`$id` 前缀 `https://contracts.example.invalid/gk-ke/v1/`），不是任何既有生产合同的原地升级。
2. `specs/CONTRACT_INDEX.yaml` 中 CTR-GKKE-001~020 已全部登记 `explicit_migration`，本策略与之对齐。
3. C08 §1 CR-02 明确"新增字段不能静默打破闭集 Schema"——闭集对象的新增**必须**走显式版本化，不能靠 `backward_compatible` 蒙混。

### 2.1 闭集字段清单（新增必须显式版本化）

以下字段是**闭集**，L0-2 及其后 Loop 都不得静默扩展：

| schema | 闭集字段 | 闭集值 |
|---|---|---|
| AssetVersion | `assetClass` | 四类（不得以 `subjectCategory` 替代） |
| SemanticPackage | `ownerSystem` | `["CORE"]` |
| SemanticPackage | `contractVersion` | `const: "gk-ke/v1"` |
| KnowledgeMap | `nodes[].nodeType` | Task / KnowledgeDomain / Asset / Capability |
| KnowledgeMap | `edges[].relation` | requires / optional / uses / dependsOn / covers / relatedTo |
| KnowledgeMap | `purpose` / `scope.purpose` | RESEARCH / INTERPRETATION / RECOMMENDATION |
| MetricDefinition.full | `joinCardinality` | 4 值闭集 |
| MetricDefinition.full | `additivity` | FULLY_ADDITIVE / SEMI_ADDITIVE / NON_ADDITIVE |
| MetricDefinition.full | `dedupPolicy` | NONE / DISTINCT / GROUP_BY / EXISTENCE_FILTER |
| MetricDefinition.full | `roundingMode` | 7 值闭集 |
| MetricDefinition.full | `intervalConvention` | 4 值闭集 |
| MetricDefinition.full | `asOfPolicy` | SNAPSHOT_PINNED / LATEST_CORRECTED / LATEST_AVAILABLE |
| MetricDefinition.full | `lateArrivalPolicy` | REJECT / RESTATE_WITH_NEW_RUN / IGNORE |
| MetricDefinition.full | `accountLifecyclePolicy` | FULL_PERIOD / ACTIVE_DAYS_ONLY / INCLUDE_CLOSED |
| MetricDefinition.full | `currencyPolicy` | CNY_ONLY / MULTI_CURRENCY |
| MetricDefinition.full | `fxPolicy` | NONE / CONVERT_TO_BASE / REPORT_PER_CURRENCY |
| MetricDefinition.full | `fxDateRule` | 4 值闭集 |
| MetricDefinition.full | `sourceSnapshotPolicy` | SNAPSHOT_ID_REQUIRED / LATEST_SNAPSHOT |
| MetricDefinition.full | `completenessRule` | 3 值闭集 |
| MetricDefinition.full | `nullPolicy` | 3 值闭集 |
| 全部 20 schema | `simulationOnly` | `const: true` |
| 全部 20 schema | `additionalProperties` | `false` |

### 2.2 版本化规则

- **命名空间版本**：`gk-ke/v1` 是**主版本**。不兼容变更 → `gk-ke/v2`，v1 与 v2 并行存在，不原地改写。
- **对象版本**：每个 schema 的 `version` 字段遵守 `^\d+\.\d+\.\d+$`（major.minor.patch）。
- **闭集扩展路径**：闭集加值 = **minor 版本 + 契约变更记录 + 正负例同步 + Owner 批准**。禁止只改 schema 不加负例。
- **CAS 语义**：`catalogRevision`、`expectedVersion` 用于并发控制；L0-2 在 OpenAPI 中定义其 header/param 位置，不在 L0-2 实现 CAS。

### 2.3 与既有合同的兼容边界（决策 D-2 落地）

| 既有对象 | gk-ke/v1 对应 | 关系 | 处理 |
|---|---|---|---|
| CTR-KMAP-001 KnowledgeMap | gk-ke/v1 KnowledgeMap | 映射 | OpenAPI `x-gk-ke-existing-mapping` 登记，不改原合同 |
| CTR-KELEM-001 KnowledgeElement | gk-ke/v1 AssetVersion | 映射 | 同上 |
| CTR-ASSET-001 AssetManifest | gk-ke/v1 AssetVersion | 映射 | 同上 |
| CTR-ACTIVATION-001 ActivationContract | gk-ke/v1 ActivationPlan | 映射 | 同上 |
| CTR-PK-* (PI-0 全族) | gk-ke/v1 Assertion/Release* | **映射，非替代** | 不改 PI-0；OpenAPI 以 `x-gk-ke-pi0-mapping` 登记 |
| CTR-ACTION-001 ControlledAction | gk-ke/v1 ControlledAction | 映射 | 同上 |
| CTR-EVIDENCE-001 EvidenceBundle | gk-ke/v1 EvidenceBundle | 映射 | 同上 |
| CTR-SEM-001 gits-core.linkml | gk-ke/v1 SemanticPackage | 映射 | 同上 |

**硬约束**：L0-2 **不修改任何上述既有合同的 authority_source 文件**。

## 3. 生成策略（Generation Strategy）

### 3.1 三层权威流（单向，不可逆）

```
specs/  (唯一权威源，手工编写)
   │  make generate
   ▼
generated/  (自动生成，只读，禁止手工编辑)
   │  make check (哈希一致性校验)
   ▼
消费者 (apps / modules / adapters / frontend)
```

依据：workspace 规则 §2「合同 SSOT」+ §3「禁止修改 generated/」。

### 3.2 每类合同的生成路径

| 合同类型 | 权威源 | 生成目标 | 生成器 |
|---|---|---|---|
| gk-ke/v1 JSON Schema (20) | `specs/gk-ke/v1/schemas/*.schema.json` | `generated/gk-ke/v1/*.schema.json` | `make generate` |
| **gk-ke/v1 OpenAPI (新)** | `specs/openapi/gk-ke-v1.openapi.json` | `generated/openapi/gk-ke-v1.normalized.json` | `make generate` |
| OpenAPI (既有) | `specs/openapi/gits-kno-api.openapi.json` | `generated/openapi/gits-kno-api.normalized.json` | `make generate` |
| AsyncAPI | `specs/events/domain-events.asyncapi.json` | `generated/events/domain-events.normalized.json` | `make generate` |

**注意**：`make generate` 是否覆盖 `specs/openapi/gk-ke-v1.openapi.json` 需 Feature Pilot 在 WI-01 实测确认；若生成脚本按 `specs/openapi/*.openapi.json` 通配，则自动纳入；若硬编码文件名清单，则需同步修改生成脚本（属 L0-2 scope 内 `scripts/`）。

### 3.3 执行顺序（不可颠倒）

```
1. 改 specs/           ← 权威源变更
2. make generate       ← 生成制品
3. make check          ← 校验哈希一致（不一致 = 构建失败）
4. 写实现 (后续 Loop)  ← 最后
```

**禁止**：先在实现里发明字段 → 再倒推补合同。

### 3.4 正负例与消费者测试的生成纪律

- 正例：每个 schema 1 个，`examples/positive/<Schema>.json`
- 负例：每个 schema ≥2 个，`examples/negative/<Schema>_<n>.json`
- **每个 OpenAPI operation ≥2 个负例**（C08 §2 与 C08 §5 双重要求）
- 消费者驱动测试：`scripts/gk_ke_openapi_contract_tests.py`
  - 校验 OpenAPI 可解析（3.0/3.1）
  - 校验 C06 §1 的 15 个 operation 全部存在
  - 校验每个 operation 有 ≥2 负例且负例确实被拒
  - 校验 `simulationOnly` 在全链路未被放宽

## 4. 兼容性回归门禁（L0-2 及后续 Loop 共用）

| 门禁 | 命令 | 判据 |
|---|---|---|
| G-1 生成一致 | `make generate && make check` | 退出码 0 |
| G-2 样例对拍 | `python3 scripts/gk_ke_contract_examples.py` | V1.0.2 基线 20 pos/40 neg 不回归 |
| G-3 OpenAPI 消费者测试 | `python3 scripts/gk_ke_openapi_contract_tests.py` | 15 operation 全覆盖 + 负例生效 |
| G-4 跨语言 hash | `./mvnw -pl modules/knowledge-architecture test -Dtest=CanonicalHashGoldenTest` | T35 黄金字节不变 |
| G-5 安全 | `make security-check` | 无凭据/隔离资产泄露 |

**回归红线**：L0-2 的变更**不得**使 G-2/G-4 从 PASS 变 FAIL。若闭集扩展导致必然失败，必须先提 Owner，不得静默放宽。

## 5. 激活前的兼容性检查清单（Owner 批准时使用）

- [ ] 全部 20 schema 的 `simulationOnly` 仍为必填 `const: true`
- [ ] 全部闭集字段未被静默扩展（对照 §2.1 清单）
- [ ] 既有合同 authority_source 未被我方修改（对照 §2.3 清单）
- [ ] `/gk-ke/v1/**` 命名空间与既有 `/api/v1/**` 无重叠
- [ ] OpenAPI `info.description` 保留"非现有 API 完整替代"声明
- [ ] G-1~G-5 全绿
- [ ] OC-01 收口证据齐备
- [ ] 独立 QA 冲突审计 QA_PASS
- [ ] 相应 Owner 签署迁移映射（`explicit_migration` 要求）
