# KERT 侧登记/变更请求（草案）

状态：**DRAFT_NOT_SENT**（草案，未发出；发出需 Owner 批准）

> 收件方：**KERT 维护方**｜发起方：ONTO1 全局 TL（代拟，未经 Owner 批准不发出）
> 依据：Owner 2026-09-21 决议（SIM 整改）；D3 未签前**不得**发布新 IRI。

## 1. 请求事项概览

| # | 类别 | 术语 / 对象 | 目标 | 请求动作 |
|---|---|---|---|---|
| 1 | 非 IRI 目标 | `ActivationContract` | `REGISTRY:ActivationContract` | 登记（REGISTRY/SCHEMA-FIELD/SKOS 各自机制），不写文件 |
| 2 | 非 IRI 目标 | `CapabilityPublication` | `REGISTRY:CapabilityPublication` | 登记（REGISTRY/SCHEMA-FIELD/SKOS 各自机制），不写文件 |
| 3 | 非 IRI 目标 | `TaskTypeScheme` | `SKOS:TaskTypeScheme` | 登记（REGISTRY/SCHEMA-FIELD/SKOS 各自机制），不写文件 |
| 4 | 非 IRI 目标 | `hasTaskType` | `SCHEMA-FIELD:hasTaskType` | 登记（REGISTRY/SCHEMA-FIELD/SKOS 各自机制），不写文件 |
| 5 | 非 IRI 目标 | `governedByContract` | `SCHEMA-FIELD:governedByContract` | 登记（REGISTRY/SCHEMA-FIELD/SKOS 各自机制），不写文件 |
| 6 | 非 IRI 目标 | `invokesCapability` | `SCHEMA-FIELD:invokesCapability` | 登记（REGISTRY/SCHEMA-FIELD/SKOS 各自机制），不写文件 |
| 7 | 非 IRI 目标 | `referencesAsset` | `SCHEMA-FIELD:referencesAsset` | 登记（REGISTRY/SCHEMA-FIELD/SKOS 各自机制），不写文件 |
| 8 | 非 IRI 目标 | `referencesSkill` | `SCHEMA-FIELD:referencesSkill` | 登记（REGISTRY/SCHEMA-FIELD/SKOS 各自机制），不写文件 |
| 9 | 退役 | `customerId` | — | deprecated + dcterms:isReplacedBy（**不得改名**） |

## 2. KERT 侧义务规模（只读统计，来源 `kert-change-proposal.json`）

- 总义务：**86**
  - `src/kert`：50
  - `examples/bank-front-knowledge-maps`：33
  - `specs/kert-openapi-v1.yaml`：3

## 3. 执行前置（缺一不可）

- **写权限**：`['KERT 维护方写权限（未确认）']`
- **校验先于产出**：物化链路重跑前须先通过校验（校验红则不产出）；
- **不得发布新 IRI**（D3 未签）；不得以 `equivalentClass` 承接重构项。

## 4. 我方边界声明（可核）

- 本草案**未发出**、**未写入 KERT**：今日（日历日）KERT 写入 = 0 件；发出标记件 = 无。
- 本轮对 KERT 侧只做**只读分析 + 补丁方案 + 验证材料**（`L2-KERT-PATCH-PLAN.md`）；
- 合入权在 KERT 维护方；本函只请求**确认与安排**，不请求代替执行。

## 5. 请你回复（3 项）

1. 是否受理上述登记/变更请求（或指定由你方执行的时点）；
2. `ontology_reference.json` → `authorityEntity` 的新钉值口径；
3. 物化链路重跑的**前置校验清单**。

