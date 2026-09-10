# W0｜Plan

## Goal

在 `modules/knowledge-architecture` 上实现 C02 注册中心控制目录与任务知识地图核心，满足 T05/T06/T07/T20。合同 reuse_only：不改 `specs/`、`generated/`。

## 权威来源（开工必读）

- 候选合同：`/home/szf/dev/gits-kert-docs/dd/GK-KE-CONTRACT-V1.0/contracts/C02_注册中心与知识地图合同.md`
- 验收矩阵：`/home/szf/dev/gits-kert-docs/dd/GK-KE-CONTRACT-V1.0/acceptance/验收矩阵.csv`（T05/T06/T07/T20）
- L0 架构定位：`docs/architecture/GK-KE-L0-1-现状定位.md`（§4 L1 交付物、§5 复用/新建）
- L0 schema：`specs/gk-ke/v1/*.json`（CTR-GKKE-002/003/005/006/014）
- L0 hash：`modules/knowledge-architecture/.../hash/CanonicalHash.java` + `CanonicalHashGoldenTest`

## 现状（可复用，勿重复造）

- 已有 P22/P23 脚手架：`KnowledgeMap`、`KnowledgeElement`、`ActivationContract`、`KnowledgePlanner`、`RoutePolicy`、`InMemoryKnowledgeStore`、`KnowledgeSnapshotLoader`、各 Port（`KnowledgeElementPort`/`KnowledgeMapPort`/`KnowledgeWikiPort`）。
- 这些是旧 P22 模型，**字段与 gk-ke/v1 合同不完全一致**。优先在其旁按 gk-ke/v1 新建 C02 领域模型，或做适配；不得为迁就旧模型而偏离合同字段。

## 任务分解（建议顺序）

1. **领域模型（对齐 gk-ke/v1）**：`AssetVersion`(CTR-002)、`CapabilityContract`(CTR-003)、`KnowledgeMap`(CTR-005)、`ActivationPlan`(CTR-006)、`TaskContext`、`Release`、`CatalogRevision`、错误码枚举（`DEPENDENCY_UNRESOLVED`/`CAPABILITY_NOT_REGISTERED`/`MAP_CYCLE_DETECTED`/`PERMISSION_DENIED`）。
2. **注册中心**：Asset/Capability/Map 版本注册；`catalogRevision` 单调递增；发布门禁（未发布 Skill 不可被计划引用）。
3. **规范化**：固定字段排序、去空白、版本固定（T05 双入口一致的前提）。
4. **依赖闭包**：从入口节点递归解析 dependsOn；引用断裂→`DEPENDENCY_UNRESOLVED`；引用未注册能力→`CAPABILITY_NOT_REGISTERED`（T06）。
5. **DAG 校验**：仅对 `dependsOn` 构成的可执行子图做环检测；`relatedTo`/`covers` 等导航关系不参与执行环（T20）。
6. **权限过滤**：discover/expand 先过滤；秘密资产对无权用户在目录/标题摘要/邻居/计数零泄漏；缓存键含 tenant/principalScopeHash/purpose/releaseId/catalogRevision（T07）。
7. **ActivationPlan + planHash**：确定性装配，复用 `CanonicalHash` 计算 canonical planHash；相同 TaskContext 双入口同 hash（T05）。

## Gates（唯一命令源见 LOOP.yaml）

contract_check → registry_core → map_dag_validate → permission_filter → plan_canonical_hash → backend_test → security_check

## 红线

- 禁止改 `specs/`、`generated/`；禁止 `git add .`；失败先写本 Loop `FAILURES.md` 再修。
- 单测命名 `*Test.java`，JUnit5+AssertJ+Mockito；测试资源放 `src/test/resources/gk-ke-registry/`。
- 方法 ≤30 行、参数 ≤4、优先 record/sealed interface、SLF4J 参数化日志。
- 不实现 T17（路由歧义，归 L2）与服务级 REST（归 L3）。
- 环境：离线构建用 `MAVEN_OPTS=-Ddependency.check.auto.update=false`；Java 21。
