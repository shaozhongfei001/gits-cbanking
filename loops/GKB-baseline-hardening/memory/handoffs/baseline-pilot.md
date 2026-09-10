# Handoff: baseline-pilot → owner_review / independent_qa

- Loop: `GKB-baseline-hardening`
- 时间: 2026-09-11（UTC 2026-09-10T16:40Z）
- 分支: `feature/GK-KE-L0-contract`
- 基线: c7017b1（STATE baseline_commit 字段为 7ae4e66，为 Loop 创建时记录值）

## 一、测试切片修复 —— 可直接合入

**问题**：`apps/api` 的 `EngagementJourneyControllerTest`（`@WebMvcTest` 切片）只声明了 7 个 `@MockitoBean`，而 `EngagementJourneyController` 构造器需要 8 个依赖，缺：

- `com.gien.gits.customerjourney.port.CustomerJourneyRepository`（构造器参数 6）
- `com.gien.gits.ontology.port.RelationshipReportRepository`（构造器参数 7）

导致 Spring 切片上下文加载抛 `NoSuchBeanDefinitionException`，4 个测试方法全部 ERROR（1 个真实失败 + 3 个 threshold-exceeded 连带）。干净基线 c7017b1 可复现（GK1 backend-test 首次暴露）。

**修复（唯一代码变更）**：`apps/api/src/test/java/com/gien/gits/api/controller/EngagementJourneyControllerTest.java`

- 新增 2 个 import（上述两个 Port 类型）；
- 新增 2 个字段：`@MockitoBean CustomerJourneyRepository journeyRepository;`、`@MockitoBean RelationshipReportRepository reportRepository;`。

未改任何生产代码；未删除/弱化任何断言；测试中既有的多余 `AuditLogPort` mock 保留未动（无害，避免无关 diff）。

**验证**：
- fix_test_slice: Tests run: 4, Failures: 0, Errors: 0（`evidence/fix_test_slice-20260910T162957Z.log`）
- apps_api_regression: apps/api 全量 Tests run: 450, Failures: 0, Errors: 0, Skipped: 4（`evidence/apps_api_regression-20260910T163012Z.log`）
- security_check: `make security-check` PASS（secret-scan 111 条均为非阻断 advisory、sensitive-permissions PASS、oracle-readonly-guard PASS）

## 二、LOOP.yaml gate 命令机械修正（需 QA 知悉）

原 repro_baseline / fix_test_slice 命令带 `-am` 且未加 `-Dsurefire.failIfNoSpecifiedTests=false`，Maven 会先在依赖模块（operational-ontology 等）执行 test 阶段，因这些模块匹配不到 `-Dtest=EngagementJourneyControllerTest` 而被 surefire 3.5.6 默认策略判失败，构建在到达 apps/api 前终止——命令即使在修复后的代码上也永远无法通过（FAILURES.md 20260910T162648Z 条）。

已在 LOOP.yaml 为这两条命令补 `-Dsurefire.failIfNoSpecifiedTests=false`。这是让 gate 命令可执行的最小机械修正，不改变 gate 意图、scope 或通过标准。

## 三、spring-core 6.2.19 CVE 集群 —— 待 Owner 在 A/B/C 中裁决（未落地）

完整决策包：`loops/GKB-baseline-hardening/evidence/SPRING_CORE_CVE_DECISION.md`。

要点：
- **17 个 CVE**（11 个 CVSS≥7：5×9.8、1×9.1、5×7.5；其余 6 个 3.7–6.1），全部 2026-08-20 披露，dependency-check 12.1.0 + NVD 2026-09-10 数据，在 apps/api 新鲜报告中确认。
- **修复版本**：7.0.9 为唯一 OSS 修复（需 Spring Boot 4.x）；6.2.20/6.1.29 等均为 Enterprise Support Only——Maven Central 实测 `spring-core/6.2.20/*.pom` 返回 404，6.2.x OSS 最新 GA 就是 6.2.19；6.1.21 虽在 Central 但仍处受影响范围 6.1.0–6.1.28，降级无收益。
- **可达性**：逐项 grep 核查，17 个 CVE 的利用前提（WebFlux、RSocket、Jetty 12、XsltView、FreeMarker、SSE 函数式端点、用户可控 SpEL、表单数据绑定、multipart/Content-Disposition）在本项目 Servlet + Tomcat + 纯 `@RestController` JSON 架构下均不存在（0 命中）。残留风险与局限已在决策包 §2 末尾诚实声明。
- **编制者推荐：方案 A**（精确 17 CVE + `spring-core@6.2.19` 窄抑制，`until=20261231`，沿用 P20 owner-authorized 注释格式）即时解除 fail-closed 阻断；**并行立项方案 C**（Boot 4.1.x / Framework 7.0.9 迁移专项 Loop）根治；方案 B（等 6.2.20 OSS）仅在 Owner 持有 Spring Enterprise 支持合同时才现实。
- 决策包 §6 附**可直接粘贴的抑制 XML 草案**（含 17 个精确 CVE 编号与完整治理注释），§7 为 Owner 签署区。

**红线遵守**：未修改 `dependency-check-suppressions.xml`；未修改任何 pom.xml 的 spring 版本；未改 `specs/` 与 `generated/`；未自签 QA_PASS。

## 四、给独立 QA 的建议核查点

1. 复现路径：`git stash` 测试改动后跑 gate 命令应见 4 errors；恢复后 0 errors。
2. 确认 diff 仅含测试文件 2 个 import + 2 个字段，以及 LOOP.yaml 的 surefire 参数、loops/GKB-baseline-hardening 文档。
3. 复核决策包 17 个 CVE 与 `apps/api/target/dependency-check-report.json` 一致（注意 target/ 不入库，需重跑 `./mvnw -pl apps/api dependency-check:check`，离线加 `MAVEN_OPTS=-Ddependency-check.auto.update=false`，exit 1 为 fail-closed 预期）。
4. 可达性 grep 命令已在决策包 §2 列出，可独立复跑。

## 五、未决事项

- Owner 对 A/B/C 的书面裁决（阻塞豁免落地与全量 verify 转绿）。
- 独立 QA 指派与 QA_PASS。
- 若选 A：批准后需实施角色落地 XML 并重跑 reactor 全量 verify（本 Loop 的 security_check gate 仅为 secret-scan，不含 dependency-check；决策包制作时已单独对 apps/api 跑过新鲜扫描）。
