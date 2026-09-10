# NEXT SESSION｜GK1-registry-map-core

| 字段 | 值 |
|---|---|
| **holder** | `independent_qa` |

> holder 由独立 QA actor 执行（dev 角色禁止自签 QA_PASS）。建议新 session（区别于 qa-gk1-formal-002）。
| **wave** | `W1-QA-FIX-RECHECK` |
| **gate** | 复验 QA §7 全部五项：Q1(T20)/Q2(schema对齐)/Q3(T06) + **T05/T07（本轮新增）** |
| **state** | 实现完成，待置 `ready_for_independent_qa` / current_phase=`independent_qa` |
| **上轮 QA** | `gk1-qa2`，session `qa-gk1-formal-002`，结论 **REJECTED**（2026-09-11） |

## 返工分工（W1-QA-FIX）

- **gk1-fix（HEAD 275dd4e，已提交）**：Q1(T20) / Q2(schema 字段对齐) / Q3(T06 错误码)。详见 `memory/handoffs/gk1-fix.md`。
- **gk1-fix2（本轮，未提交待原子提交）**：**T07** 与 **T05**。详见 `memory/handoffs/gk1-fix2.md`。

## 本轮修复（gk1-fix2，严格限定 T05/T07）

### T07 权限感知目录四出口零泄漏 + 五要素缓存键
- 新增 `permission/PermissionAwareCatalog`，在注册中心之上叠加运行时权限过滤，收口四类出口：
  1. `discover(ctx)`：目录列表，仅返回可见资产的安全投影 `AssetView`（秘密资产不出现，不泄漏存在性）；
  2. `summaries(map,ctx)`：标题摘要 nodeId→label（秘密节点标题不泄漏）；
  3. `neighbors(map,nodeId,ctx)`：关系邻居（仅相邻且自身可见的节点；直接查秘密节点返回空）；
  4. `countVisibleNodes(map,ctx)`：节点计数（仅可见节点）。
- `PermissionContext` 扩展为五要素：`tenantId / principalScopeHash / purpose / releaseId / catalogRevision`，
  `cacheKey() = tenant|principalScopeHash|purpose|releaseId|catalogRevision`；可见资产集合按该键缓存，
  不同主体/用途/发布快照/目录修订/租户不串缓存。保留 4 参兼容构造器供既有单资产决议测试。
- `AssetRegistryPort` + `InMemoryAssetRegistry` 新增 `findAll()`（目录全集，过滤在调用方）。
- 行为测试 `permission/PermissionAwareCatalogTest`（**11 例**）：四出口零泄漏 5 例 + 缓存隔离 6 例。

### T05 Wiki/对象双入口 canonical planHash 对拍
- 新增 `plan/PlanRequest`（剥离入口导航来源的确定性内部请求）、`plan/ActivationPlanner`（硬拒绝装配器，
  复用 T06 的 CapabilityRegistry/AssetNotFound/AssetNotAvailable；成功则经 PlanCanonicalHasher 附 planHash）、
  `plan/ActivationEntryPoint`（两个独立入口）：
  - `fromWiki(WikiEntry)`：知识地图页面发起，携带 `wikiPage` 浏览来源；
  - `fromObject(ObjectEntry)`：业务对象卡片发起，携带 `businessObjectRef` + `entryAnchor`。
  - 两入口入参类型不同、导航来源不同，但都归一到同一 PlanRequest；导航字段不进入计划载荷。
- 行为测试 `plan/DualEntryPlanHashTest`（**4 例**）：核心对拍断言两个独立入口对象（非同一 Java 引用）
  在同一 TaskContext 下 planHash 逐字节相等；另验证导航来源不影响哈希、releaseId/purpose 不同则哈希不同。

## 复验入口

1. 交接详单：`memory/handoffs/gk1-fix2.md`（T05/T07 实现方式、测试清单、设计取舍）。
2. 模块全量（Tech Lead 裁决的模块级命令）：
   ```
   MAVEN_OPTS="-Ddependency.check.auto.update=false -DretireJsAnalyzerEnabled=false" \
     ./mvnw -pl modules/knowledge-architecture -am test -Ddependency-check.skip=true
   ```
   → **95 tests / 0 failures / 0 errors / 0 skipped**（gk1-fix 基线 80 + gk1-fix2 新增 15）。
3. gate 证据（actor=gk1-fix2，均 PASS，20260910T1847*Z~1848*Z）：
   registry_core / map_dag_validate / permission_filter / plan_canonical_hash / contract_check。
   backend_test gate 尝试预算 5/5 已由 gk1-pilot-resume 记为 pass（无法重录），但本轮已用模块级命令
   重跑确认 95 全绿，日志 `evidence/backend_test-20260910T184813Z.log`。
4. `make generate && make check` 无漂移（contract-check PASS，gk-ke 正例 14/14）。
5. 独立 QA 结论写入 `EVIDENCE.json.independent_qa`（dev 角色禁止自签 QA_PASS）。

## 合规边界

- 改动仅限 `modules/knowledge-architecture`（gkke 包）+ 其测试；未改 specs/ 与 generated/（reuse_only）。
- 未实现 T17/REST（L2/L3 deferred）；spring-core CVE 与 apps/api 切片错误为基线存量，已隔离 GKB。
- record/sealed、方法≤30 行、参数≤4、JUnit5+AssertJ、SLF4J 参数化日志、无 System.out、无 null 传参。
