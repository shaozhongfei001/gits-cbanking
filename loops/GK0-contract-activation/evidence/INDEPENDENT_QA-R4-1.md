# GK0-contract-activation｜独立 QA 复核报告（WP-R4-1 整改）

- **复核角色**: independent_qa（独立 QA，与 Feature Pilot 隔离）
- **actor**: gk0-qa1
- **session**: qa-gk0-formal-001
- **被验收 HEAD**: `91d5fedee7c8b5c9db8a99a9592ad7b9623f4ac3`（含 WP-R4-1 全部 6 个合同源变更）
- **复核日期**: 2026-09-11
- **复核对象**: WP-R4-1 六合同源变更 + 生成一致性 + 门禁 + 负例隔离 + 计数与证据

## 一、复核前独立复现（不采信开发自检）

| 命令 | 结果 | exit |
|---|---|---|
| `git rev-parse HEAD` | `91d5fed...`（预期一致） | — |
| `make generate` | contract-generate: PASS | 0 |
| `make check` | contract-check / knowledge-architecture-check / loop-guard / secret-scan / enum-consistency / semantic-rule-gate / gk-ke-contract-examples 全 PASS | 0 |
| `python3 tools/verify_simulation.py` | verify_simulation: PASS | 0 |
| `python3 scripts/gk_ke_contract_examples.py` | 正例通过 20/20，负例被拒 40 个 | 0 |

## 二、逐项结论

### 1. 合同源变更正确性 — PASS

- `MetricDefinition.full.schema.json` 覆盖 C04 §2 七组字段：
  - 身份（metricId/version/definition/owner/approvalRef/definitionHash）✅
  - 对象与粒度（population/entityType/baseGrain/aggregationGrain/dimensions/allowedJoinPaths/joinCardinality）✅
  - 计算（numerator/denominator/expressionRef/additivity/distinctKey/dedupPolicy/roundingMode/scale）✅
  - 时间（intervalConvention/businessTimezone/calendarVersion/asOfPolicy/lateArrivalPolicy/accountLifecyclePolicy）✅
  - 金额（currencyPolicy/unit/fxPolicy/fxSource/fxDateRule/precision）✅
  - 数据（sourceProductRef/sourceSnapshotPolicy/mappingVersion/completenessRule/nullPolicy/qualityChecks）✅
  - 运行（queryTemplateRef/parameterSchemaRef/resultSchemaRef/permissionRef/maxRows/timeoutMs/costBudget）✅
- `additionalProperties: false`，`simulationOnly: const true`，未发明合同外字段。
- `SemanticPackage.schema.json` 的 types[].items 补 `writeOwner/writeEntry/authorityScope` 为可选字段（required 仅 typeId/definition/identityRule），向后兼容 ✅。
- `LegacyRagHit.schema.json` 映射 C05 §3 七字段：sourceId/sourceVersion/fragmentId/locator/text/score/permissionDecisionRef ✅。
- `SourceVersion/Capability/QueryDefinition/Release` 四注册对象字段与 C02 §2 注册中心表逐项对齐 ✅。

### 2. 生成一致性 — PASS

- `make generate` 成功。
- `generated/gk-ke/v1/`（20 文件）与 `specs/gk-ke/v1/schemas/`（20 文件）**JSON 语义完全一致**（逐字节差异仅为生成器键排序/缩进规范化，非手工篡改）。
- 未发现手工改 generated 痕迹。

### 3. 门禁通过性 — PASS

- `make check` 全绿。
- 正负例对拍：20 正例通过 / 40 负例被拒。
- `CONTRACT_INDEX.yaml` 登记 CTR-GKKE-015（MetricDefinition.full）/016（SourceVersion）/017（Capability）/018（QueryDefinition）/019（Release）/020（LegacyRagHit），六条齐全，contract_ref 分别为 C04/C02/C02/C02/C02/C05，compatibility=explicit_migration，simulation_only=true ✅。

### 4. 负例隔离 — PASS

- `negative_cases.json` 正确声明 6 个负例：
  - T15 expectedError=CURRENCY_POLICY_REQUIRED（跨币种拒绝）
  - T14 expectedError=GRAIN_VIOLATION（重复账户日）
  - T14b expectedError=DATA_INCOMPLETE（缺日）
  - T12 expectedError=GRAIN_VIOLATION（交易连接放大）
  - T13 expectedError=null / expectedValue=200.00（同余额两账户，禁 DISTINCT）
  - T02 expectedError=null（同名异主体，不并户）
  - 均与 C04 §7 错误码表对齐。
- 负例数据未污染 `simulation/tables/` 正常快照：daily_balances 720 行 = 720 唯一键（无重复账户日）；USD 账户 SIM-A0022 属 SIM-C002（跨币种正常 seed，非坏数据）。
- `verify_simulation.py` 仅 import 标准库（csv/sys/collections/decimal/pathlib），只读 tables，独立复算 C001=2983333.33，与 `expected.json` 一致，不共享 build_simulation 代码路径 ✅。

### 5. 计数与证据 — PASS

- MANIFEST 实测 117 文件 / 69 json，与任务预期一致（清单"100 文件/json 8"口径错误已纠正）。
- `FAIL-2026-09-11-01`（loops/GK0-contract-activation/FAILURES.md）如实记录 RETURN_TO_HLD 及 AR-R0~R5 整改 ✅。

## 三、最终结论

**QA_PASS**（针对 WP-R4-1 合同源整改范围）

独立 QA 确认：六项合同源变更正确对齐总契约 C01-C07，生成一致，门禁全绿，负例隔离干净，计数与证据如实。RETURN_TO_HLD 解除。后续 Owner 决议（指标口径/知识认定/试点范围）不在本 QA 权限内，留待各 Owner 审签。
