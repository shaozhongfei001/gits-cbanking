# Handoff: gk1-fix → independent_qa（2026-09-11）

## 背景

接续 gk1-pilot-resume（其 WIP 暂存 `/tmp/gk1-wip`，worktree 已由其清理为干净 HEAD `a0f0010`，见 FAILURES.md FAIL-2026-09-11-01）。本次派工**只修独立 QA 报告（evidence/INDEPENDENT_QA.md）中的 Q1/Q2/Q3**：

- Q1 = T20 执行依赖环检测
- Q2 = gkke 地图模型与 `specs/gk-ke/v1/schemas/KnowledgeMap.schema.json` 字段对齐
- Q3 = T06 稳定合同错误码

**T05（双入口对拍）与 T07（权限四类出口/五要素缓存键）不在本次派工范围**，未改动；QA 报告中这两项的退回结论保持不变，需后续批次处理。未改 `specs/` 与 `generated/`（reuse_only）。

## Q1：执行依赖子图环检测（T20）

**问题**：旧 `KnowledgeMapDagValidator.adjacency()` 对全部 edges 建图，导航边（covers/relatedTo）成环会被误判为执行环。

**修法**：
- 新增 `map/MapRelation.java` 枚举，严格承载 schema relation 6 值：`requires/optional/uses/dependsOn/covers/relatedTo`，每个值带 `executableDependency` 标志与 `wireValue()`、`fromWire()`（非法值抛 IllegalArgumentException）。
- `KnowledgeMapDagValidator`：
  - `adjacency(map, executableOnly)` 双模式；`validateExecutableSubgraphAcyclic` 只收执行依赖边做三色 DFS；
  - `reachableSubgraph`（T20 入口可达子图）沿**全部边** BFS（导航边也可达）；
  - 新增 relation 枚举合法性校验（ROUTES_TO 等发明值 → MAP_VALIDATION_FAILED）。

**relation 取舍依据（C02 §4.2 + schema 字段注释）**：
- `dependsOn`：节点间执行先后依赖 → **执行依赖**（合同明确“可执行依赖子图必须 DAG”）。
- `requires`：任务装配必需资产/能力，缺失不可激活 → **执行依赖**（装配期必须满足，纳入执行子图）。
- `uses`：能力/任务执行时调用资产/能力 → **执行依赖**（执行期调用依赖，纳入执行子图）。
- `optional`：可选增强，缺失不阻断激活 → **不参与**（不阻断执行，成环不构成死锁）。
- `covers`：领域→知识的导航/溯源 → **不参与**（导航边，允许成环）。
- `relatedTo`：松散语义关联 → **不参与**（导航边，允许成环）。

## Q2：模型字段对齐 KnowledgeMap.schema.json（additionalProperties=false）

以 schema 为唯一准绳（注意：schema 实际字段与派工口述略有出入，已严格按 schema 实现）：

- `MapEdge`：`(edgeId, from, to, relation, reason, designDecisionRef)`，删除旧 `(from,to,type)` 与 ROUTES_TO。
- `MapNode`：`(nodeId, nodeType, label, ref: VersionRef)`，nodeType 枚举 `Task/KnowledgeDomain/Asset/Capability`；删除旧 title/assetId/capabilityId/preconditions/minTokens/maxTokens 等发明字段（schema 节点只有 4 字段）。
- `KnowledgeMapRecord`：12 字段 `(contractVersion, simulationOnly, mapId, version, releaseId, taskTypes, entryNodes, routePolicyRef: VersionRef, nodes, edges, purpose, scope)`；删除旧 name/status/entryNodeIds。**schema 无 name/status 字段**，故未添加；scope 子结构是单值 `purpose`（非 allowedPurposes 数组），现有 `Scope` record 已匹配，直接复用；ref 子结构 `{id,version}` 复用现有 `VersionRef`。
- `AssetVersionRecord`：对齐 AssetVersion.schema.json（Q3 CapabilityRegistry/发布判定需要，且夹具 lifecycle 非法）：新增合同信封 `contractVersion/simulationOnly`，lifecycle 严格五值 `CANDIDATE/IN_REVIEW/APPROVED/PUBLISHED/REVOKED`（删除 DRAFT），保留 `isPublished()`。
- 夹具 `KE-SKILL-001__0.9.0.json`：`DRAFT`→`CANDIDATE`。
- 所有引用旧构造器的类与测试同步更新（validator、registry 测试、3 个 permission 测试、Normalization/DependencyClosure/RegistryCore）。

**合同样例反序列化测试**：复制 `specs/gk-ke/v1/examples/positive/KnowledgeMap.json` 到 `src/test/resources/gk-ke-registry/maps/SIM-MAP-FINANCE.json`，schema 复制到 `src/test/resources/gk-ke-v1-schema/KnowledgeMap.schema.json`；新增 `KnowledgeMapContractAlignmentTest`（test 依赖 `com.networknt:json-schema-validator:1.5.7`，scope=test）：
1. networknt 校验正例对 schema 零 violation（覆盖 additionalProperties=false）；
2. Jackson 反序列化为 record 并逐字段断言（含 4 节点 nodeType、4 边 relation 全 requires/uses）；
3. 反序列化结果过 DAG 校验 + 入口可达 4 节点。

## Q3：稳定合同错误码（T06）

- 新增 `registry/GkErrorCode.java`：10 个稳定码。L1 落地 `DEPENDENCY_UNRESOLVED`、`CAPABILITY_NOT_REGISTERED`、`ASSET_NOT_AVAILABLE`、`DUPLICATE_ASSET_VERSION`、`DEPENDENCY_CYCLE`、`MAP_CYCLE_DETECTED`、`MAP_VALIDATION_FAILED`；`ROUTE_AMBIGUOUS`、`BUDGET_EXCEEDED`、`PERMISSION_DENIED` 先定义常量（L2+ 使用）。
- 新增 `registry/GkDomainException.java`（RuntimeException 基类，携带 `GkErrorCode code()` 与合同字符串 `errorCode()`）。
- 映射：
  - `AssetNotFoundException` → **DEPENDENCY_UNRESOLVED**（引用断裂，T06 验收期望）；
  - 新增 `CapabilityNotRegisteredException` → **CAPABILITY_NOT_REGISTERED**；
  - 新增 `AssetNotAvailableException` → **ASSET_NOT_AVAILABLE**（资产存在但未发布/撤销；`InMemoryAssetRegistry.requirePublished` 由裸 IllegalStateException 改抛此码，snapshotRelease/闭包现在硬拒绝非 PUBLISHED）；
  - `DuplicateAssetVersionException` → DUPLICATE_ASSET_VERSION；`DependencyCycleException` → DEPENDENCY_CYCLE；
  - `MapValidationException` → 工厂 `invalid()`=MAP_VALIDATION_FAILED、`cycle()`=MAP_CYCLE_DETECTED。
- 新增最小 `registry/CapabilityRegistry.java`：登记能力 ID+版本，`requireRegistered(VersionRef)` 未登记抛 CAPABILITY_NOT_REGISTERED（能力资产化元数据留后续 Loop）。
- 测试断言错误码**字符串**（如 `"DEPENDENCY_UNRESOLVED"`、`"CAPABILITY_NOT_REGISTERED"`），并新增枚举 wireValue 稳定性测试。

## 测试

- 模块全量：`./mvnw -pl modules/knowledge-architecture -am test` → **Tests run: 80, Failures: 0, Errors: 0, Skipped: 0**（原 67 项基线 + 新增 13 项：DAG 测试 15 项替换原 10 项、Q2 合同对齐 3 项、Q3 能力注册 4 项，净增 13）。
- 重跑 gate（actor=gk1-fix，均 PASS，日志在 evidence/）：map_dag_validate、registry_core、plan_canonical_hash、contract_check。
- `make generate && make check`：全部 PASS，generated/ 零漂移。
- backend_test/security_check 未重跑（派工说明其已绿且命令未变；模块全量已绿）。

## 给独立 QA 的复验建议

1. Q1：重点看 `KnowledgeMapDagTest.relatedToCyclePasses/coversCyclePasses/optionalCyclePasses/requiresUsesCycleRejected/mixedRelationsExecutableCycleStillRejected` 与 `MapRelation` 的取舍注释是否符合 C02 §4.2。
2. Q2：`KnowledgeMapContractAlignmentTest` 直接以合同正例 + schema 做断言，是字段对齐的最强证据；可再用负例（specs negative KnowledgeMap_1/2）验证模型拒绝（本次未纳入，如需要可补）。
3. Q3：错误码字符串断言见 RegistryCoreTest/DependencyClosureTest/CapabilityRegistryTest/KnowledgeMapDagTest。
4. T05/T07 本次未处理，不应视为已修复；请仅对 Q1/Q2/Q3 出具复验结论。
