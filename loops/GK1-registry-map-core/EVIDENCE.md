# GK1-registry-map-core｜Evidence index

机器可判定的唯一证据板为 `EVIDENCE.json`。本文件只提供人类导航，不复制状态。

- 命令日志：`evidence/`
- 失败记录：`FAILURES.md`
- 波次迭代：`memory/waves/`
- 独立QA：必须由非implementation actor写入 `EVIDENCE.json.independent_qa`

## 2026-09-11 gk1-fix 修复独立 QA 退回（Q1/Q2/Q3）

范围严格限定派工三项，未触碰 specs/generated，未处理 T05/T07（不在本次派工范围）。

- **Q1（T20 执行依赖环）**：新增 `map/MapRelation` 枚举（合同 6 值 requires/optional/uses/dependsOn/covers/relatedTo）；`KnowledgeMapDagValidator` 只对执行依赖边（dependsOn/requires/uses）建图做 DAG 环检测，covers/relatedTo（导航）与 optional（可选增强）不参与；新增 relation 枚举合法性校验。
- **Q2（schema 字段对齐）**：`MapEdge`→`edgeId/from/to/relation/reason/designDecisionRef`；`MapNode`→`nodeId/nodeType/label/ref(VersionRef)`；`KnowledgeMapRecord`→schema 12 字段（contractVersion/simulationOnly/mapId/version/releaseId/taskTypes/entryNodes/routePolicyRef/nodes/edges/purpose/scope）；`AssetVersionRecord` 对齐 AssetVersion schema（contractVersion/simulationOnly + lifecycle 五值枚举，删除 DRAFT）；删除发明字段 type/ROUTES_TO/entryNodeIds/title/assetId/capabilityId/preconditions。
- **Q3（T06 错误码）**：新增 `registry/GkErrorCode`（10 码，含 ROUTE_AMBIGUOUS/BUDGET_EXCEEDED/PERMISSION_DENIED 预留）与 `GkDomainException` 基类；AssetNotFoundException→DEPENDENCY_UNRESOLVED；新增 CapabilityNotRegisteredException→CAPABILITY_NOT_REGISTERED + 最小 CapabilityRegistry；AssetNotAvailableException→ASSET_NOT_AVAILABLE（未发布资产硬拒绝）；MapValidationException→MAP_VALIDATION_FAILED/MAP_CYCLE_DETECTED；Duplicate/DependencyCycle 各归其码。
- **新增测试**：`KnowledgeMapDagTest` 重写（Q1 导航环通过/执行环拒绝/混合关系/非法 relation 等 15 项）；`KnowledgeMapContractAlignmentTest`（合同正例反序列化 + networknt JSON Schema additionalProperties=false 校验 + DAG 校验）；`CapabilityRegistryTest`（错误码 4 项）。模块全量 80 tests 全绿、零失败零跳过。
- 重跑 gate（actor=gk1-fix）：map_dag_validate / registry_core / plan_canonical_hash / contract_check 均 PASS；`make generate && make check` 无漂移。
- 交接：`memory/handoffs/gk1-fix.md`。
