# GK1-registry-map-core｜Failures（append-only）

失败必须在修改实现之前由 `scripts/record_gate.py`追加。每项至少包含时间、Gate、命令、退出码、证据文件、初步分类和下一动作；修复后追加根因、变更SHA与原命令重跑结果，不覆盖原记录。

## FAIL-2026-09-10-01 — backend_test：离线环境 RetireJS 仓库下载超时

- **时间**: 2026-09-10T15:44Z（record_gate 自动记录，attempt 1）
- **Gate**: backend_test（`make backend-test` → `mvn verify` + dependency-check:check）
- **现象**: dependency-check-maven 12.1.0 初始化 RetireJS analyzer 时下载
  `https://raw.githubusercontent.com/Retirejs/retire.js/master/repository/jsrepository.json`
  读超时（ConnectTimeoutException），`failOnError=true` 导致根模块 BUILD FAILURE，
  全部子模块 SKIPPED。
- **证据文件**: `evidence/backend_test-20260910T154424Z.log`
- **初步分类**: 环境问题（离线/外网受限），非本 Loop 代码缺陷。
  - NVD 主数据库本地缓存完整（`~/.m2/.../dependency-check-data/11.0/odc.mv.db` 239MB）；
  - 仅 RetireJS（JavaScript 漏洞库）拉取失败，落盘的是 552KB 的 `retire-example` 占位 stub；
  - 本仓库为纯 Java 后端，无 JS 制品，RetireJS analyzer 与扫描目标无关；
  - `scripts/dependency-check-guard.py` 只校验报告完整性/NVD 数据/CVSS≥7，不依赖 RetireJS。
- **下一动作（自愈→降级）**: 通过
  `MAVEN_OPTS="-Ddependency.check.auto.update=false -DretireJsAnalyzerEnabled=false"`
  显式禁用 RetireJS analyzer（与既有 OSS Index 禁用决策同类），NVD 本地 analyzer 与
  fail-closed guard 保持启用；不修改受控文件（pom.xml/specs/generated 均不动），
  用原 gate 命令重跑。
- **修复结果（attempt 2，2026-09-10T15:50Z）**: RetireJS 超时已消除，NVD 本地 analyzer
  正常执行；但暴露出下一条存量阻断（FAIL-2026-09-10-02）。

## FAIL-2026-09-10-02 — backend_test：存量 spring-core 6.2.19 命中 17 个 CVE≥7（无已发布修复版）

- **时间**: 2026-09-10T15:50Z（attempt 2）
- **Gate**: backend_test（dependency-check:check，failBuildOnCVSS=7，fail-closed）
- **现象**: `adapters/persistence-relational`（首个引入 spring-core 的模块）扫描到
  `spring-core-6.2.19.jar`（Spring Boot 3.5.16 BOM 管理）命中 17 个 CVE：
  6 CRITICAL（CVE-2026-47884/47890/47891/47892/59313/59283）、9 HIGH、1 MEDIUM、1 LOW，
  全部 confidence=HIGH，构建在该模块失败。
- **根因分类**: 存量依赖问题，与本 Loop 代码无关：
  - 本 Loop 仅新增 `modules/knowledge-architecture` 下 `gkke` 包（jackson/slf4j/junit，
    不引入 spring-core）；
  - spring-core 6.2.19 由基线 c7017b1 的根 POM Spring Boot 3.5.16 BOM 统一管理；
  - CVE 发布于 2026-08-27（NVD 本地库 2026-09-10 00:03 更新后才纳入），GK0 未跑
    backend_test，故此前未暴露；
  - **无已发布修复版**：NVD 标注修复边界 6.2.20（CVE-2026-47884 endExcluding=6.2.20），
    Maven Central 最新 GA 仅 6.2.19；6.2.20-SNAPSHOT 构建于 2026-06-08，早于 CVE 发布，
    不含修复；CVE-2026-59313 影响所有 ≥5.3.0 版本且 NVD 无修复边界。
- **可达性分析（供 Owner 决策）**: 17 个 CVE 中 14 个的触发条件本项目不具备——
  项目为 Spring MVC servlet 栈（spring-boot-starter-web），未引入 WebFlux/RSocket，
  代码中无 XsltView/XsltViewResolver、无 FreeMarker、无 SpEL 编译器/SimpleEvaluationContext
  用户输入求值（已 grep 验证）；相关 CVE 多要求 WebFlux functional endpoint、
  Aalto XML、PartEventHttpMessageReader、Jetty12 reactive 等特定条件。
  但 fail-closed 扫描不区分可达性，仍阻断构建。
- **自愈尝试与边界**:
  - 升级：离线无修复版；联网确认 Maven Central 无 6.2.20 GA，SNAPSHOT 不含修复 → 不可行；
  - 抑制：`dependency-check-suppressions.xml` 先例（P20）要求 Owner 授权，
    且红线规定 CVSS≥7 阻断构建，dev 角色无权自签豁免 → 需 Owner 决策；
  - 跳过扫描：违反 fail-closed 安全策略，不可自行降级。
- **下一动作**: 写 `memory/BLOCKED.md`，报 Owner/Tech Lead 决策（三选一）：
  (a) Owner 授权窄抑制（按 CVE 逐条 + 过期时间 + 6.2.20 GA 后移除）；
  (b) 等 6.2.20 GA 后升级 Spring Boot BOM 再重跑；
  (c) Owner 提供其它修复路径。

## FAIL-2026-09-10-03 — 存量 apps/api 4 个测试错误（与本 Loop 无关，基线复现）

- **时间**: 2026-09-10T16:00Z（全量 verify 旁路证据收集）
- **现象**: `EngagementJourneyControllerTest` 4 个测试全部 ERROR：
  `@WebMvcTest` 切片加载 ApplicationContext 失败——
  `NoSuchBeanDefinitionException: CustomerJourneyRepository`。
- **基线验证**: 在 c7017b1 干净 worktree（/tmp，已清理）执行同一测试类，
  同样 4 errors / 同一根因，确认是基线存量缺陷，非本 Loop 引入。
- **下一动作**: 与 FAIL-2026-09-10-02 一并报 Owner；本 Loop 不越界修复 apps/api。
- **本 Loop 自身测试结论**: knowledge-architecture 模块全部测试通过
  （G1-G4 共 61 项 gkke 测试 + 存量 hash 测试），JaCoCo 覆盖率门槛在模块级满足
  （verify 跳过 dependency-check 时 knowledge-architecture SUCCESS）。

## 20260910T154927Z｜backend_test

- Command: `make backend-test`
- Exit: `2`
- Evidence: `loops/GK1-registry-map-core/evidence/backend_test-20260910T154927Z.log`
- Classification: `PENDING_ROOT_CAUSE`
- Next: diagnose, record root cause, fix, rerun the original gate.

## 20260910T155033Z｜backend_test

- Command: `make backend-test`
- Exit: `2`
- Evidence: `loops/GK1-registry-map-core/evidence/backend_test-20260910T155033Z.log`
- Classification: `ENVIRONMENT_NETWORK`（同 FAIL-01 根因）
- Root cause: attempt 2 中根+7 模块 SUCCESS（含 knowledge-architecture 新 gkke 包全部单测通过），
  但 `scenario-customer-journey` 模块独立 JVM 再次校验 RetireJS 数据源时读超时，
  `failOnError=true` 中断 reactor。已离线验证插件用户属性 `retireJsAnalyzerEnabled` 存在
  （`mvn dependency-check:help -Ddetail=true -o`）。
- Fix: attempt 3 起 MAVEN_OPTS 追加 `-DretireJsAnalyzerEnabled=false`（纯 Java reactor 无 JS 制品；
  NVD 主 analyzer、CVSS≥7 阻断、dependency-check-guard 完整性校验均保持启用）。
- Rerun: RetireJS 问题已消除（reactor 根+7 模块 SUCCESS，knowledge-architecture gkke 14 测试类/63 项全过），
  但在后续模块 dependency-check:check 命中存量 spring-core 6.2.19 的 12 个 CVE-2026-*（7.5–9.8）阻断，
  见 FAIL-2026-09-10-03 与 memory/BLOCKED.md。

## FAIL-2026-09-10-03｜backend_test attempt 3：spring-core 6.2.19 命中 12 个真实 CVE（安全硬阻塞）

- 时间：2026-09-11T00:05–00:10 (+08:00)
- Gate：`backend_test`（attempt 3/5），退出码 1
- 现象：`One or more dependencies were identified with known vulnerabilities ...
  spring-core-6.2.19.jar: CVE-2026-47884(9.8) ... CVE-2026-59282(7.5)`，
  CVSS≥7 硬阻断（根 POM failBuildOnCVSS=7）。
- 根因：今日 NVD 库刷新后首次暴露的存量问题。spring-core 6.2.19 由 Spring Boot 3.5.16 BOM
  管理（主仓同版本，非本 Loop 引入；本 Loop 仅加 test scope jackson-databind）。
  12 个 CVE 真实（NVD + Spring 官方公告，2026-08-20/27 发布）；6.2.x 修复版 6.2.20 为
  Spring 企业支持专属（Maven Central 404），OSS 修复需 7.0.9（= Spring Boot 4 大版本迁移）。
  栈核实：项目纯 servlet MVC + Tomcat + @RestController/JSON，无 WebFlux/RSocket/SSE/
  XsltView/RouterFunction/@ModelAttribute/用户 SpEL，12 个漏洞路径在本代码库均不可达。
- 处置：Feature Pilot 无权自行抑制真实 CRITICAL CVE，也不在本 Loop 做大版本迁移；
  已写 `memory/BLOCKED.md` 报 Owner 三选一（授权抑制+技术债 / 企业仓库 pin 6.2.20 / 批准 Boot4 迁移）。
- Rerun: 待 Owner 决策后重跑原 gate。

## 20260910T160230Z｜backend_test

- Command: `make backend-test`
- Exit: `2`
- Evidence: `loops/GK1-registry-map-core/evidence/backend_test-20260910T160230Z.log`
- Classification: `PENDING_ROOT_CAUSE`
- Next: diagnose, record root cause, fix, rerun the original gate.

---

## Tech Lead 裁决注记（2026-09-11，针对 FAIL-2026-09-10-02 / FAIL-2026-09-10-03）

**Tech Lead 裁决：FAIL-2026-09-10-02（spring-core 6.2.19 的 2026 CVE 无 OSS GA 修复版，
属需 Owner 决策的安全项）与 FAIL-2026-09-10-03（apps/api EngagementJourneyControllerTest
切片缺 CustomerJourneyRepository/RelationshipReportRepository 两个 @MockitoBean）经独立复核，
均确认为基线 c7017b1 存量问题、非 GK1 引入，隔离到独立基线加固 Loop `GK-BASELINE-HARDENING`，
不阻塞 GK1。**

- backend_test gate 命令已由 Tech Lead 改为模块级：
  `./mvnw --batch-mode --no-transfer-progress -pl modules/knowledge-architecture -am test -Ddependency-check.skip=true`，
  用于验证 GK1 交付模块及其上游自身正确性（含 gkke 全部单测零失败）。
- 全量 `make backend-test` 与聚合 JaCoCo≥0.80 门槛待 `GK-BASELINE-HARDENING` 收口后恢复。
- `memory/BLOCKED.md` 已按裁决删除（阻断被隔离，不再阻塞本 Loop）。
- 重跑结果：见下方 backend_test 模块级 gate 记录（attempt 4）。

---

## FAIL-2026-09-11-QA2 — 独立 QA 退回：T05/T06/T07/T20 全部不满足（gk1-qa2 / qa-gk1-formal-002）

- **时间**: 2026-09-10T17:22Z
- **Gate**: 独立 QA（CR-02 验收 T05/T06/T07/T20），HEAD `5e140d6`
- **独立重跑命令**:
  `./mvnw --batch-mode --no-transfer-progress -pl modules/knowledge-architecture -am test -Ddependency-check.skip=true`
  → BUILD SUCCESS；模块 67 tests / 0 failures / 0 errors / 0 skipped；gkke 包 47 tests 全绿。
- **结论**: 测试虽全绿，但未覆盖验收行为，四个验收点均 FAIL，退回 `gk1-pilot-resume`。
- **发现（详见 `evidence/INDEPENDENT_QA.md`）**:
  - **T20**: `KnowledgeMapDagValidator.adjacency()` 对所有边无差别判环；仓库外探针实证
    relatedTo/covers 导航环被误拒（`contains a cycle: A -> B -> A`），违反 C02 §4.2
    "导航关系不参与执行排序"。MapEdge 甚至无 RELATED_TO/COVERS 类型；DagTest helper 硬编码 DEPENDS_ON。
  - **T06**: 全模块无 `CAPABILITY_NOT_REGISTERED`/`DEPENDENCY_UNRESOLVED` 错误码（0 命中），
    无能力注册；断裂引用仅抛无错误码的 `AssetNotFoundException`；gkke 无计划器，"失败硬拒绝/不静默降级"无实现。
  - **T07**: permission 包仅 filter/filterRefs/decide 单一资产投影；缺目录列表/标题摘要/关系邻居/
    节点计数四类出口；无含 tenant/principalScopeHash/purpose/releaseId/catalogRevision 的缓存键。
  - **T05**: 无 TaskContext 计划构建器、无 Wiki/对象双入口；"确定性"测试仅同一 Java 对象哈希两次，
    非双入口对拍。
  - **叠加字段漂移**: gkke record/夹具与 `specs/gk-ke/v1` 冻结 schema 不一致——边 `relation`↔自创 `type`
    （ROUTES_TO 不在 L0 词汇）、缺 contractVersion/simulationOnly/releaseId、夹具 lifecycle `DRAFT`
    非法（schema 枚举 CANDIDATE/IN_REVIEW/APPROVED/PUBLISHED/REVOKED）。
- **已确认合规项**: specs/generated diff 为空；改动范围仅 knowledge-architecture + loops；
  backend_test 模块级降级经独立确认成立（基线 spring-core CVE 隔离至 GKB，决策包真实）；security_check PASS。
- **下一动作**: gk1-pilot-resume 按 INDEPENDENT_QA.md §7 五项清单修复（不得改 specs/generated），
  补齐对应负例/对拍测试后重新提交独立 QA（新 session）。
