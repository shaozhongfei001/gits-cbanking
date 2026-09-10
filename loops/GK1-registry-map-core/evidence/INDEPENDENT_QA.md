# GK1-registry-map-core｜独立 QA 验收报告（CR-02 / T05·T06·T07·T20）

- **结论**: **FAIL — 退回 Feature Pilot（gk1-pilot-resume）**
- **独立 QA**: `gk1-qa2`
- **session**: `qa-gk1-formal-002`
- **验收时间**: 2026-09-11
- **被验收对象**: worktree `/home/szf/dev/gk-wt-L1`，分支 `feature/GK-KE-L1`，HEAD `5e140d6`（工作区干净）
- **权威依据**:
  - `C02_注册中心与知识地图合同.md`（CR-02，§4.1/4.2/4.3/5/6/7）
  - 验收矩阵 `T05/T06/T07/T20`
  - L0 冻结 schema `specs/gk-ke/v1/schemas/*.json`
  - 本 Loop `LOOP.yaml` gates（plan_hash / registry_core / secret_isolation / map_dag）
- **独立性声明**: 未修改任何实现/合同代码；仅新增本 QA 记录与 Loop 状态文件。行为实证探针写在仓库外 `/tmp/gk1qa/`，未入库。

---

## 0. 复跑结果（独立重跑，非仅看日志）

命令（按要求跳过离线 dependency-check）：

```
MAVEN_OPTS=-Ddependency.check.auto.update=false \
./mvnw --batch-mode --no-transfer-progress \
  -pl modules/knowledge-architecture -am test -Ddependency-check.skip=true
```

- 结果：**BUILD SUCCESS**
- 模块合计：**Tests run: 67, Failures: 0, Errors: 0, Skipped: 0**
- 其中 `com.gien.gits.knowledge.gkke` 包：**47 tests，0 failures / 0 errors / 0 skipped**（13 个测试类）

测试确实编译运行且有真实断言（非空测试），但**测试覆盖的行为与 CR-02 验收点不对齐**：现有用例只验证了"哈希确定性/投影过滤/依赖闭包抛 AssetNotFoundException/DEPENDS_ON 环拒绝"等基础性质，未实现也未验证 T05/T06/T07/T20 要求的关键行为。**"测试全绿"不等于"验收通过"**。

---

## 1. T20 — FAIL（已行为实证）

**验收要求**：`dependsOn` 执行环必须被拒；`relatedTo`/`covers` 导航环**不得**误判为执行环。C02 §4.2 明确："relatedTo 等导航关系不参与执行排序；DAG 无环约束只作用于执行依赖子图"。

**实现现状**：`KnowledgeMapDagValidator.adjacency()` 对**所有边**无差别建邻接表判环：

```java
// modules/knowledge-architecture/.../gkke/map/KnowledgeMapDagValidator.java
private Map<String, List<String>> adjacency(KnowledgeMapRecord map) {
    Map<String, List<String>> adjacency = new HashMap<>();
    map.edges().forEach(edge ->
        adjacency.computeIfAbsent(edge.sourceId(), k -> new ArrayList<>()).add(edge.targetId()));
    return adjacency;
}
```

未按边类型区分执行边与导航边；`MapEdge` 仅支持 `DEPENDS_ON` / `ROUTES_TO`，**根本没有 `RELATED_TO` / `COVERS` 类型**。

**独立行为实证**（仓库外探针 `/tmp/gk1qa/T20Probe.java`，直接加载 `target/classes`）：

| 输入 | 期望 | 实际 | 判定 |
|---|---|---|---|
| A→B→A 全 `DEPENDS_ON` | 拒绝 | 拒绝 | OK |
| A↔B `RELATED_TO` 导航环 | **不拒绝** | **拒绝**（`Knowledge map contains a cycle: A -> B -> A`） | **MISMATCH** |
| A↔B `COVERS` 导航环 | **不拒绝** | **拒绝**（同上） | **MISMATCH** |
| 无环 `DEPENDS_ON` | 通过 | 通过 | OK |

现有 `KnowledgeMapDagTest` 的 `edge()` helper 硬编码 `DEPENDS_ON`，**没有任何 relatedTo/covers 导航环用例**，因此该缺陷被绿测试掩盖。

**结论**：T20 第二句（导航环不误判）不满足，`map_dag` gate 的 pass_condition 未达成。

---

## 2. T06 — FAIL（错误码与能力注册缺失）

**验收要求**：未注册能力→`CAPABILITY_NOT_REGISTERED`；断裂/未发布引用→`DEPENDENCY_UNRESOLVED`；计划失败必须硬拒绝，禁止静默降级。C02 §6 错误码表 + §4.3"计划失败必须返回明确错误码，禁止静默降级"。

**实现现状**（全模块 grep 核实）：

- `CAPABILITY_NOT_REGISTERED` / `DEPENDENCY_UNRESOLVED` / `ROUTE_AMBIGUOUS` / `ASSET_NOT_AVAILABLE` / `BUDGET_EXCEEDED`：**主代码 0 处**。
- 无"能力（Capability）"注册表概念，无 `CapabilityRegistry`。
- 断裂依赖在 `InMemoryAssetRegistry.dependencyClosure()` 抛的是 `AssetNotFoundException`（仅 assetId/version，**无错误码字段**），不是 `DEPENDENCY_UNRESOLVED`；未发布引用也无独立错误码。
- gkke 包**没有计划器**（`gkke/plan/` 仅有 `PlanCanonicalHasher`），因此"计划失败硬拒绝/不静默降级"无对应实现与测试。
- 注：`com.gien.gits.knowledge.plan.DefaultActivationPlanner`（非 gkke，P20 shadow 存量）使用 `DENY_*` 码，**不是** C02 §6 的错误码，且不在 GK1 范围。

**结论**：T06 三个子项均不满足，`registry_core` gate 的 pass_condition（"断裂/未发布引用返回 DEPENDENCY_UNRESOLVED"）未达成。

---

## 3. T07 — FAIL（四类出口与缓存键缺失）

**验收要求**：秘密资产对无权用户在**目录列表 / 标题摘要 / 关系邻居 / 节点计数**四类出口零泄漏；缓存键必须含 `tenant / principalScopeHash / purpose / releaseId / catalogRevision`。C02 §7.1/7.2。

**实现现状**（`gkke/permission/` 仅 4 个类：`AssetView/PermissionContext/PermissionDecision/RegistryPermissionFilter`）：

- `RegistryPermissionFilter` 只有 `filter / filterRefs / decide`，是**单一的资产投影过滤**。
- **没有** `discover`（目录列表）、**没有**标题摘要出口、**没有**关系邻居出口、**没有**节点计数出口；grep `cache|discover|neighbor|count|principalScopeHash|catalogRevision` 在 gkke 主代码 **0 命中**。
- 因此"四类出口零泄漏"只可能间接覆盖"资产详情投影"一类，其余三类无实现、无测试；缓存键五要素完全不存在。
- 现有 `SecretLeakTest` 仅验证无权用户拿到的 `AssetView` 中 secret 字段被抹除（单一出口）。

**结论**：T07 的四类出口与缓存键要求不满足，`secret_isolation` gate 的 pass_condition 未达成。

---

## 4. T05 — FAIL（无双入口、无 TaskContext→计划构建）

**验收要求**：Wiki 入口与对象入口对同一 TaskContext 生成的 canonical planHash 必须一致（真实比较双入口 hash）。C02 §4.3 + §5.1。

**实现现状**：

- gkke 主代码**没有 `TaskContext`**（仅 test 下有一个 record），**没有计划构建器**，也没有 Wiki/对象两个装配入口。
- `PlanCanonicalHasher` 只对**已构造好的 `ActivationPlanRecord`** 做规范化哈希。
- `ActivationPlanCanonicalTest` 的"确定性"断言是**对同一个 Java 对象哈希两次**比较相等，**不是**"两个入口分别构建计划后比较 hash"。
- 黄金值测试（`PlanHashGoldenTest`）只锁定当前算法输出，不能证明双入口等价。

**结论**：T05 的"双入口相同 TaskContext → 相同 planHash"无实现、无对拍测试，`plan_hash` gate 的 pass_condition（"双入口哈希一致"）未达成。

---

## 5. 合同/字段对齐问题（CR-02 红线，叠加退回项）

> 与上一轮 QA（gk1-qa-manual，Q1/Q2/Q3）一致，且 HEAD `5e140d6` 早于该退回、**未修复**。本轮独立复核再次确认。

1. **gkke record 与 L0 冻结 schema 字段漂移**（违反"不发明字段/字段对齐 gk-ke/v1"）：
   - `KnowledgeMapRecord`：缺 schema 必填 `contractVersion`，发明 `schemaVersion/name/status/entryNodeIds/revision`；schema 用 `releaseId/taskTypes/routePolicyRef/purpose/scope`，实现未对齐。
   - `MapEdge`：schema 边字段为 `relation`（枚举 `requires/optional/uses/dependsOn/covers/relatedTo`），实现用 `type`（`DEPENDS_ON/ROUTES_TO`），字段名与枚举均不符；`ROUTES_TO` 不在 L0 边词汇内。
   - `MapNode`：schema 节点字段（`id/title/assetId/assetVersion/assetType/taskTypes/...`）与实现（`nodeId/title/assetRef/.../type/kind/...`）不一致。
   - `AssetVersionRecord`：缺 schema 必填 `contractVersion/simulationOnly`；`lifecycle` 注释枚举 `DRAFT/REVIEW/...` 与 schema 枚举 `CANDIDATE/IN_REVIEW/APPROVED/PUBLISHED/REVOKED` 不一致。
2. **测试夹具违反冻结 schema**：`KE-SKILL-001__0.9.0.json` 使用 `lifecycle: "DRAFT"`，不在 schema 枚举内。
3. 加载器 `InMemoryAssetRegistryLoader` 直接反序列化这套**自创 record**，不存在到 gk-ke/v1 的映射层，等于在实现侧另立了一套 schema。

> 说明：本 Loop 未改 `specs/` 与 `generated/`（见 §6 合同 diff 为空，合规）；问题在于**实现没有对齐已冻结的 L0 schema**，而非改了合同。

---

## 6. 已独立确认合规/降级成立的事项

- **合同纪律**：`git diff --stat c7017b1 HEAD -- specs generated` **为空**，未触碰合同/生成物；未实现 T17（L2）与 REST（L3），范围克制正确。
- **改动范围**：`git diff --name-only c7017b1 HEAD` 全部落在 `modules/knowledge-architecture/` 与 `loops/GK1-registry-map-core/`，无越界。
- **backend_test 降级（独立确认成立）**：
  - FAIL-2026-09-10-02/03 记录的 spring-core 6.2.19 CVE 与 apps/api 切片错误，经 Tech Lead 裁决为基线 c7017b1 存量，隔离到独立基线加固 Loop，不阻塞 GK1；
  - 独立基线决策包真实存在：主仓 `loops/GKB-baseline-hardening/evidence/SPRING_CORE_CVE_DECISION.md`（2026-09-11，Owner 已授权窄抑制至 2026-10-31）；
  - GK1 模块级 gate 命令（`-pl modules/knowledge-architecture -am test -Ddependency-check.skip=true`）复跑 SUCCESS。
  - **残留风险（沿用结论）**：基线 spring-core CVE 的全量 `make backend-test` / 聚合 JaCoCo 门槛待基线加固 Loop 收口，与本 Loop 代码无关。
- **security_check**：`evidence/security_check-20260910T154442Z.log` 为 PASS（0 命中），离线环境未重跑。
- **代码风格抽查**：gkke 主代码无 `System.out/printStackTrace`；模型类使用 record；未发现超长方法/明显 null 传参问题。风格不是退回主因。

---

## 7. 退回结论与必修清单

四个验收点 **T05/T06/T07/T20 全部不满足**，且 LOOP.yaml 四个 gate 的 pass_condition 均未真正达成（当前 gate 仅凭"测试编译运行通过"被标记 pass，判定标准与 gate 定义不符）。**不予记录 QA_PASS**，退回 `gk1-pilot-resume`。

修复最低要求（对齐 CR-02 与 L0 schema，不得改 `specs/`/`generated/`）：

1. **T20**：DAG 校验只对执行依赖边（`dependsOn`/`requires` 等执行类型）建图判环；`relatedTo`/`covers` 导航边不参与执行环判定；补导航环不误判 + 执行环仍拒绝的对拍用例。
2. **T06**：引入能力注册与 C02 §6 错误码（至少 `CAPABILITY_NOT_REGISTERED`、`DEPENDENCY_UNRESOLVED`）；断裂/未发布引用返回对应错误码；实现计划失败硬拒绝、无静默降级路径，并加负例测试。
3. **T07**：补齐目录列表/标题摘要/关系邻居/节点计数四类出口的无权零泄漏测试；实现含 `tenant/principalScopeHash/purpose/releaseId/catalogRevision` 五要素的缓存键并测试隔离。
4. **T05**：提供 Wiki 与对象两个入口、基于同一 TaskContext 构建 ActivationPlan，并对拍两者 canonical planHash 相等（而非同一对象哈希两次）。
5. **字段对齐**：gkke record/夹具对齐 `specs/gk-ke/v1` 冻结 schema（边用 `relation` 词汇、补 `contractVersion/simulationOnly/releaseId/...`、修正 lifecycle 枚举），或提供明确的 schema↔record 映射层并在证据中说明。

修复后重新提交独立 QA（新 session）。本报告 sha256 与登记见 EVIDENCE.json `independent_qa`。
