# GK1-registry-map-core｜独立 QA 复验报告（CR-02 / T05·T06·T07·T20）

- **结论**: **PASS — 记录 QA_PASS，baton → owner_review**
- **独立 QA**: `gk1-qa2`
- **session**: `qa-gk1-formal-003`（返工后复验；002 退回历史见 `INDEPENDENT_QA.md`）
- **验收时间**: 2026-09-10T19:00Z
- **被验收对象**: worktree `/home/szf/dev/gk-wt-L1`，分支 `feature/GK-KE-L1`，HEAD `1c80c6d`（工作区干净）
- **返工提交**: `275dd4e`（T20/T06/字段对齐）、`065fcca`（T07/T05）、`1c80c6d`（证据/baton）
- **权威依据**: C02 合同（§4.1/4.2/4.3/5/6/7）、验收矩阵 T05/T06/T07/T20、L0 冻结 schema `specs/gk-ke/v1/schemas/*.json`、本 Loop `LOOP.yaml`
- **独立性声明**: 未修改任何实现/合同代码。行为探针与变异实验均在仓库外 `/tmp/gk1qa3/` 进行；变异实验对 `KnowledgeMapDagValidator` 的临时篡改已还原并重新编译，`git status` 干净。

---

## 0. 独立重跑（clean，非增量、非采信日志）

```
MAVEN_OPTS="-Ddependency.check.auto.update=false -DretireJsAnalyzerEnabled=false" \
./mvnw --batch-mode --no-transfer-progress \
  -pl modules/knowledge-architecture -am clean test -Ddependency-check.skip=true
```

- **BUILD SUCCESS**；模块合计 **Tests run: 95, Failures: 0, Errors: 0, Skipped: 0**（基线 67 → 95）。
- gkke 包 16 个测试类，含 `PermissionAwareCatalogTest` 的 11 个 `@Nested` 用例（surefire 顶层 .txt 因嵌套显示 0，XML `tests="11"` 已核实真实执行）。
- `make check`：contract-check / knowledge-architecture-check / loop-guard / secret-scan / enum-consistency / semantic-rule-gate / gk-ke-contract-examples（正例 14/14、负例 28 全拒）**全 PASS，零漂移**。

## 0.1 独立行为探针（仓库外，加载 target/classes，26 项断言）

`/tmp/gk1qa3/Probe.java` 直接调用主代码（不经测试框架），结果 **26/26 PASS**。
**变异实验（防假阳性）**：将 `KnowledgeMapDagValidator.adjacency()` 的执行边过滤临时改为"所有边判环"（重现 002 缺陷），探针立即变为 24 pass / **2 fail**（relatedTo、covers 导航环被误拒）；还原后恢复 26/26。证明探针真实有效、非空转。

---

## 1. T20 — PASS

`MapRelation` 枚举与 L0 schema 边词汇逐字一致：`requires/optional/uses/dependsOn/covers/relatedTo`，`isExecutableDependency()` 仅前四者为真；`MapEdge.relation()` 加载时对非合同枚举抛 `relation not in contract enum`。`KnowledgeMapDagValidator.adjacency()` 仅对执行边建图，导航边（covers/relatedTo）不参与。

探针实测：

| 输入 | 期望 | 实际 |
|---|---|---|
| relatedTo 双向环 | 不拒绝 | PASS（不拒绝） |
| covers 三节点环 | 不拒绝 | PASS |
| dependsOn 双向环 | 拒绝 | PASS |
| requires 双向环 | 拒绝 | PASS |
| uses 双向环 | 拒绝 | PASS |
| 自创 `ROUTES_TO` | 拒绝（非合同枚举） | PASS |

无自创 `ROUTES_TO` 残留（grep 主代码 0 命中）。

## 2. T06 — PASS

`GkErrorCode` 提供 C02 §6 稳定错误码；`GkDomainException` 携带可断言的 `errorCode`；`CapabilityRegistry` 管理能力注册。探针实测三类失败各走对应码且可断言：

- 断裂依赖（依赖未注册版本）→ **DEPENDENCY_UNRESOLVED**（`dependencyClosure`）。
- 未发布资产（CANDIDATE 进入 release 快照）→ **ASSET_NOT_AVAILABLE**（`snapshotRelease`）。
- 未注册能力 → **CAPABILITY_NOT_REGISTERED**（`CapabilityRegistry.requireRegistered`）。
- **无静默降级**：`ActivationPlanner.plan()` 对未注册能力直接抛 `CAPABILITY_NOT_REGISTERED`，探针确认"抛错且不返回任何 plan"（`returnedPlanAnyway=false`）。

## 3. T07 — PASS

`PermissionAwareCatalog` 提供四类出口，探针以无权主体（orgs=[ORG-001]，秘密资产仅 ORG-SECRET 可见）逐一验证零泄漏：

| 出口 | 无权主体结果 | 判定 |
|---|---|---|
| 目录列表 `discover` | 不含 KE-SECRET | PASS |
| 标题摘要 `summaries` | 无 N-SECRET 键、无"秘密标题"值 | PASS |
| 关系邻居 `neighbors`（从公开节点） | 空（不暴露秘密邻居） | PASS |
| 关系邻居（直接查秘密节点） | 空（不确认秘密节点存在） | PASS |
| 节点计数 `countVisibleNodes` | 无权=2，授权=3 | PASS |

缓存键 `PermissionContext.cacheKey()` 含五要素 `tenant|principalScopeHash|purpose|releaseId|catalogRevision`。探针逐一翻转五要素，缓存键均不同；并实测"先填无权缓存、授权主体仍能看到秘密资产"，**无跨主体串缓存**。

## 4. T05 — PASS

`ActivationEntryPoint` 提供两个独立入口 `WikiEntry` / `ObjectEntry`（携带不同导航来源 wikiUrl / objectId+panelType），经同一 `ActivationPlanner` 装配。探针实测：

- 两入口产出不同 plan 对象（`pw != po`），但 `planHash` **逐字节相等**。
- 改变导航来源（wikiUrl）不影响 hash。
- 不同 releaseId → hash 不同；不同 TaskContext.purpose → hash 不同。

`PlanCanonicalHasher` 规范化排序（steps/assetRefs/capabilityRefs/routePolicyRefs），不含导航来源字段。

## 5. 字段对齐 gk-ke/v1 — PASS

- 夹具 lifecycle 全部为五值枚举（CANDIDATE/IN_REVIEW/APPROVED/PUBLISHED/REVOKED），**无 DRAFT**。
- 地图夹具 relation 仅用合同枚举（dependsOn/relatedTo/requires/uses/covers）。
- 夹具含 `contractVersion:"gk-ke/v1"`、`simulationOnly:false`、`releaseId`。
- `KnowledgeMapContractAlignmentTest` 直接加载 `KnowledgeMap.schema.json` 做 networknt 校验（正例通过、缺 contractVersion/错误 relation/错误 lifecycle 三负例被拒）。
- `git diff --stat c7017b1 HEAD -- specs generated` **为空**；gkke 主代码无 `@RestController/@RequestMapping`，**未实现 T17/REST**。

---

## 6. 实现者主动声明的 3 个合同解释点 — QA 判定

| # | 声明 | QA 判定 | 依据 |
|---|---|---|---|
| 1 | principalScopeHash 用 JVM 内确定性 hashCode 摘要，非跨语言 SHA-256 黄金值 | **本 Loop 可接受，不阻断**（记残留说明） | C02 §7.2 仅要求缓存键"必须包含 principalScopeHash"，**未规定其哈希算法**；§5.1 的 SHA-256 黄金值约束针对的是 **planHash**（已用 SHA-256，见 PlanCanonicalHasher），非 scopeHash。当前实现 scopeHash 对同一身份输入稳定、跨身份隔离（探针五要素翻转已验证），满足缓存隔离目的。跨语言可移植性属 L2/L3 多运行时议题，建议在进入跨语言/REST 层时以 ADR 明确，不影响 L1 模块级验收。 |
| 2 | 邻居出口对所有关系类型算邻居、仅按节点可见性过滤（"可见即可导航"），未按 relation 分流隐藏导航边 | **可接受，不阻断** | C02 §7.1 要求"无权访问的资产不得出现在目录、搜索、关系、推荐结果中"，落点是**资产/节点可见性**；§4.2 规定 relatedTo/covers 是不参与执行排序的导航边。实现对无权节点在邻居出口完全剔除（探针：公开节点看不到秘密邻居、直接查秘密节点也为空），已满足零泄漏。合同未要求"节点可见但按 relation 类型隐藏边"这一更细粒度分流。 |
| 3 | ActivationPlanner 遍历地图全部节点装配，未做"仅 entryNodes 可达闭包"裁剪（建议留 L2 与 T17 同批） | **本 Loop 可接受偏差，不阻断**（建议跟踪） | C02 §4.2 要求"从入口节点出发不可达的节点不参与执行"。实现已提供 `KnowledgeMapDagValidator.reachableSubgraph(...)`（合同对齐测试覆盖），具备闭包能力，但 `ActivationPlanner.plan()` 当前遍历全部节点。在 L1 模块级、夹具地图均为入口可达的前提下不产生错误激活结果；真正的"不可达节点不激活"风险在路由/编排层（T17/L2）才会暴露。实现者已主动声明并建议与 T17 同批，**建议 Owner 在 L2/T17 Loop 入口将其列为必做项**，不作为本次 CR-02 registry+map core 的阻断项。 |

> 三点均非"CR-02 文本明确强制而实现违反"的情形：第 1、2 点合同未作更细规定；第 3 点合同有原则要求、实现已具备闭包工具方法但未在装配路径启用，属 L1→L2 的合理分期，残留风险已在此显式记录。

## 7. 合规/降级复核（沿用并复核）

- 改动范围 `git diff --name-only c7017b1 HEAD` 全部在 `modules/knowledge-architecture/` 与 `loops/GK1-registry-map-core/`，无越界。
- backend_test 模块级降级仍成立：基线 spring-core CVE 隔离至 GKB（决策包主仓 `loops/GKB-baseline-hardening/evidence/SPRING_CORE_CVE_DECISION.md` 真实存在，Owner 授权窄抑制至 2026-10-31），与 GK1 代码无关；模块级 gate 复跑 SUCCESS。**残留风险**：全量 `make backend-test`/聚合 JaCoCo 门槛待基线加固 Loop 收口。
- security_check：secret-scan PASS（113 advisory 为依赖公告，非密钥泄漏）。
- 代码风格：record/sealed、无 System.out、错误码集中枚举，符合规范。

## 8. 最终结论

002 报告 §7 的五项必修**全部修复并经独立行为探针 + 变异实验证实**；T05/T06/T07/T20 满足 CR-02 与验收矩阵；合同零漂移、范围干净、无 REST/T17 越界。**记录 QA_PASS**，Loop 移交 `owner_review`。残留事项（均不阻断）：解释点 1 的 scopeHash 跨语言算法、解释点 3 的 entryNodes 可达闭包在装配路径启用——建议纳入 L2/T17 Loop。
