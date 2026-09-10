# Handoff｜gk1-fix2｜W1-QA-FIX（T05 + T07）

- Loop: `GK1-registry-map-core`（L1，CR-02，验收 T05/T06/T07/T20）
- 基线：HEAD `275dd4e`（gk1-fix 已提交 Q1/Q2/Q3，在 a0f0010 之上），工作区开工时干净
- 本轮范围（team-lead 收窄）：**仅 T07 与 T05**；不重做/不改动 gk1-fix 的第 1/2/5 项
- 合同决策：reuse_only（未改 specs/ 与 generated/）
- 结果：模块 **95 tests / 0 failures / 0 errors / 0 skipped**，BUILD SUCCESS；5 gate 重跑 PASS

---

## 一、T07：权限感知目录四类出口零泄漏 + 五要素缓存键

### QA §7 对应要求
无权用户对秘密资产在四类出口零泄漏：目录列表、标题摘要、关系邻居、节点计数；缓存键含
`tenant/principalScopeHash/purpose/releaseId/catalogRevision` 五要素并测隔离。

### 实现
| 文件 | 变更 | 说明 |
|---|---|---|
| `permission/PermissionAwareCatalog.java` | 新增 | 四出口统一权限收口 |
| `permission/PermissionContext.java` | 修改 | 扩展五要素 + `cacheKey()` |
| `registry/AssetRegistryPort.java` | 修改 | 新增 `findAll()` |
| `registry/InMemoryAssetRegistry.java` | 修改 | 实现 `findAll()` |
| `permission/PermissionAwareCatalogTest.java` | 新增测试 | 11 例 |

四类出口（默认拒绝，复用既有 `RegistryPermissionFilter.decide`）：
1. `discover(ctx)` → `List<AssetView>`：只返回通过权限决议的资产安全投影；秘密资产不出现（存在性零泄漏）。
2. `summaries(map,ctx)` → `Map<nodeId,label>`：引用秘密资产的节点标题不出现。
3. `neighbors(map,nodeId,ctx)` → `List<nodeId>`：仅返回相邻且自身可见的节点；
   - 从公开节点查秘密邻居 → 空；
   - 直接对秘密节点查邻居 → 空（不确认节点存在）。
4. `countVisibleNodes(map,ctx)` → `int`：只计可见节点。

可见性判定：不引用受控版本的节点（Task/KnowledgeDomain）恒可见；Asset/Capability 节点仅当
其 `ref.id()` 对应资产通过权限决议时可见。

五要素缓存键：
```
cacheKey = tenantId | principalScopeHash | purpose | releaseId | catalogRevision
```
- `principalScopeHash` 由 `PermissionContext.scopeHash(tenant, orgIds, customerIds)` 对排序后的
  授权范围做稳定摘要（非明文范围）；
- 可见资产集合按 cacheKey 缓存（`ConcurrentHashMap`），任一要素不同即不同槽，结构上杜绝串缓存；
- 保留 4 参兼容构造器（releaseId=UNBOUND/revision=0），仅供既有“单资产决议”测试使用；目录出口走全参构造器。

### 测试用例（PermissionAwareCatalogTest，11 例）
- 嵌套类「四类出口零泄漏」5 例：
  - `discoverHidesSecret`（出口1）
  - `summariesHideSecret`（出口2）
  - `neighborsHideSecret`（出口3）
  - `neighborsOfSecretNodeEmptyForUnauthorized`（出口3b）
  - `countExcludesSecret`（出口4）
  - 每例均同时断言有权主体可见，证明是“过滤”而非“数据缺失”。
- 嵌套类「五要素缓存键隔离」6 例：
  - `differentPrincipalNotShared`（先填无权缓存再查有权，验证不命中前者）
  - `differentPurposeNotShared`（秘密资产仅声明 INTERPRETATION，RESEARCH 看不到）
  - `differentReleaseNotShared` / `differentRevisionNotShared` / `differentTenantNotShared`（键不同）
  - `sameFactorsSameKey`（同五要素键相同，缓存可复用）

---

## 二、T05：Wiki/对象双入口 canonical planHash 对拍

### QA §7 对应要求
提供 Wiki 入口与对象入口两个**独立**入口，基于同一确定性 TaskContext 分别构建 ActivationPlan，
对拍两者 canonical planHash 相等；不是同一对象哈希两次。

### 实现
| 文件 | 变更 | 说明 |
|---|---|---|
| `plan/PlanRequest.java` | 新增 | 剥离入口导航来源的确定性内部请求 |
| `plan/ActivationPlanner.java` | 新增 | 硬拒绝装配器 + 附 canonical planHash |
| `plan/ActivationEntryPoint.java` | 新增 | Wiki/对象两个独立入口门面 |
| `plan/DualEntryPlanHashTest.java` | 新增测试 | 4 例 |

- 两个入口是**不同入参 record 类型**：
  - `ActivationEntryPoint.WikiEntry`（含 `wikiPage` 浏览来源）→ `fromWiki(...)`
  - `ActivationEntryPoint.ObjectEntry`（含 `businessObjectRef` + `entryAnchor`）→ `fromObject(...)`
- 二者共享 `ActivationEntryPoint.TaskContext(taskId, purpose, scope, budget)`。
- 入口特有导航字段（wikiPage / businessObjectRef / entryAnchor）**不进入 PlanRequest 载荷**，
  两入口都归一为同一确定性 PlanRequest（planId 由 taskId:mapId:version:releaseId 派生）。
- `ActivationPlanner` 遍历地图节点装配 PlanStep，硬拒绝语义复用 gk1-fix 的 T06 成果：
  - 资产版本缺失 → `AssetNotFoundException`（DEPENDENCY_UNRESOLVED）
  - 资产未发布 → `AssetNotAvailableException`（ASSET_NOT_AVAILABLE）
  - 能力未注册 → `CapabilityRegistry.requireRegistered` 抛 `CapabilityNotRegisteredException`
  - 无跳过步骤、无静默降级；成功后由既有 `PlanCanonicalHasher.withComputedHash` 附 planHash。
- 步骤的 `dependsOn` 仅取执行依赖边（`MapEdge.isExecutableDependency()`：requires/uses/dependsOn），
  导航边不进入执行排序——与 T20 口径一致。

### 测试用例（DualEntryPlanHashTest，4 例）
- `twoIndependentEntriesProduceSamePlanHash`（核心对拍）：构造 WikiEntry 与 ObjectEntry 两个独立对象
  （不同导航来源），分别 fromWiki/fromObject；断言 `isNotSameAs`（非同一 Java 对象）且
  `planHash` 相等，并对 steps/assetRefs/capabilityRefs/purpose 载荷做相等断言。
- `navigationSourceDoesNotAffectHash`：不同 wikiPage 不影响 planHash。
- `differentReleaseProducesDifferentHash`：releaseId 不同 → planHash 不同。
- `differentTaskContextProducesDifferentHash`：同 taskId 不同 purpose → planHash 不同。

---

## 三、requires/uses 取舍（与 gk1-fix T20 口径一致）
C02 §4.2 规定“可执行依赖子图必须为 DAG”。requires/uses 表达激活/执行期必须满足的装配与调用依赖，
与 dependsOn 同属执行语义，故 `MapEdge.isExecutableDependency()` 把 requires/uses/dependsOn 一并纳入
执行子图判环；optional 不阻断、covers/relatedTo 仅导航，不参与执行环。T05 步骤 dependsOn 与 T07
邻居出口均沿用该分类（邻居出口不过滤关系类型，但按节点可见性过滤）。

## 四、schema 映射策略
本轮**未新增**内部领域模型与 schema 之间的映射层：T05/T07 直接复用 gk1-fix 已严格对齐
`specs/gk-ke/v1` 的 record（KnowledgeMapRecord/MapNode/MapEdge/AssetVersionRecord/ActivationPlanRecord）。
- `routePolicyRef` 在冻结 schema 中为 `{id,version}` 对象，与 `VersionRef` 形状一致，直接复用 VersionRef。
- PermissionContext 是运行时权限载体（非 14 个冻结 schema 之一的持久化合同），其五要素缓存键为
  注册中心内部机制，不进入对外合同 JSON。

## 五、验证
- 模块全量：95 tests / 0 failures / 0 errors / 0 skipped，BUILD SUCCESS。
- gate（actor=gk1-fix2，均 PASS）：registry_core / map_dag_validate / permission_filter /
  plan_canonical_hash / contract_check；backend_test 已用模块级命令重跑 95 全绿
  （gate 尝试预算 5/5 早已由 gk1-pilot-resume 记 pass，无法重录，仅落新日志）。
- `make generate && make check`：contract-check PASS，gk-ke 正例 14/14、负例被拒 28，无合同漂移。

## 六、仍存疑/提请 QA 关注的合同解释点
1. `principalScopeHash` 的具体摘要算法合同未强制；当前用排序后授权范围的稳定 `Integer.toHexString(hashCode)`
   派生（JVM 内确定性，非跨语言/跨进程黄金值）。若 C02 要求跨语言稳定哈希，需改为 SHA-256 等标准算法，
   请 QA/Owner 确认期望强度。
2. T07 邻居出口当前对所有关系类型（含导航边）计算邻居，仅按“节点可见性”过滤；若合同要求邻居出口
   只暴露执行依赖邻居、完全隐藏导航边，需进一步按 relation 分流（当前实现选择“可见即可导航”）。
3. `ActivationPlanner` 目前遍历地图全部节点装配步骤（含非入口可达节点），因为测试夹具为单连通小图；
   L2 路由层若要求“仅从 entryNodes 做依赖闭包可达”，需引入可达性遍历（与 T17 同批处理较合适）。
