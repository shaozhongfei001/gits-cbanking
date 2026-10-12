# GKB-baseline-hardening｜Failures（append-only）

失败必须在修改实现之前由 `scripts/record_gate.py`追加。每项至少包含时间、Gate、命令、退出码、证据文件、初步分类和下一动作；修复后追加根因、变更SHA与原命令重跑结果，不覆盖原记录。

## 20260910T162648Z｜repro_baseline

- Command: `./mvnw --batch-mode --no-transfer-progress -pl apps/api -am test -Dtest=EngagementJourneyControllerTest -Ddependency-check.skip=true`
- Exit: `1`
- Evidence: `loops/GKB-baseline-hardening/evidence/repro_baseline-20260910T162648Z.log`
- Classification: `GATE_COMMAND_DEFECT（非产品缺陷）`
- Root cause: gate 命令带 `-am` 会在依赖模块（首个为 operational-ontology）执行 test 阶段，而 `-Dtest=EngagementJourneyControllerTest` 在这些模块匹配不到测试；surefire 3.5.6 默认 `failIfNoSpecifiedTests=true`，构建在到达 apps/api 前即失败（"No tests matching pattern ... were executed"）。该命令即使修复产品代码也永远无法通过。
- Fix: LOOP.yaml 中 repro_baseline / fix_test_slice 两条命令补 `-Dsurefire.failIfNoSpecifiedTests=false`（最小机械修正，不改变 gate 意图与 scope，已在交接说明）。
- Rerun: 见下条 20260910T162825Z，命令可正确执行并复现产品基线缺陷。

## 20260910T162825Z｜repro_baseline

- Command: `./mvnw --batch-mode --no-transfer-progress -pl apps/api -am test -Dtest=EngagementJourneyControllerTest -Dsurefire.failIfNoSpecifiedTests=false -Ddependency-check.skip=true`
- Exit: `1`
- Evidence: `loops/GKB-baseline-hardening/evidence/repro_baseline-20260910T162825Z.log`
- Classification: `BASELINE_TEST_DEFECT（基线存量，复现成功，符合 repro_baseline pass_condition）`
- Root cause: `EngagementJourneyControllerTest` 为 `@WebMvcTest(EngagementJourneyController.class)` 切片，仅声明 7 个 `@MockitoBean`（taskService、opportunityService、commitmentService、externalEventService、productKnowledgeVersionService、customerService、auditLogPort）；而 `EngagementJourneyController` 构造器需要 8 个依赖，切片缺少 `com.gien.gits.customerjourney.port.CustomerJourneyRepository`（构造器参数 6）与 `com.gien.gits.ontology.port.RelationshipReportRepository`（构造器参数 7）。Spring 上下文加载失败：`NoSuchBeanDefinitionException`，4 个测试方法全部 ERROR（首个真实失败 + 3 个 "ApplicationContext failure threshold (1) exceeded" 跳过重复加载）。干净基线 c7017b1 可复现（GK1 backend-test 首次暴露，FAIL-2026-09-10-02）。
- Next: fix_test_slice gate——仅在测试类补这两个 `@MockitoBean`（正确 Port 类型 import），不改生产代码、不删/弱化断言。

## 20260911T0707Z｜spring_cve_suppression（attempt 1）

- Command: `MAVEN_OPTS="-Ddependency.check.auto.update=false -DretireJsAnalyzerEnabled=false" ./mvnw verify`
- Exit: `1`（根聚合模块 dependency-check 阶段，12.7s，全部子模块 SKIPPED）
- Evidence: `/tmp/gkb_verify.log`（本次会话）；关键报错：`Unable to parse suppression xml file ... cvc-datatype-valid.1.2.1: '20261031' 不是 'date' 的有效值`（Line=186）
- Classification: `SUPPRESSION_XSD_DATE_FORMAT`
- Root cause: dependency-check suppressions schema 的 `until` 属性类型为 xsd:date，合法格式为 `yyyy-MM-dd`，不是决策包 §6 注释中误写的 `yyyyMMdd`。
- Fix: suppress 节点改为 `until="2026-10-31"`（Owner 确认的到期日 2026-10-31 不变），同步修正决策包 §6 的格式说明与草案。
- Next: 重跑全量 verify。

## 20260911T0715Z｜spring_cve_suppression（attempt 2）

- Command: `MAVEN_OPTS="-Ddependency.check.auto.update=false -DretireJsAnalyzerEnabled=false" ./mvnw verify`
- Exit: `1`（reactor 在 adapters/persistence-relational dependency-check:check 阶段中断；前 10 个模块 SUCCESS）
- Evidence: `/tmp/gkb_verify2.log`；`adapters/persistence-relational/target/dependency-check-report.json`
- Classification: `SUPPRESSION_ARTIFACT_SCOPE_EXTENSION（授权集群内）+ UNAUTHORIZED_BASELINE_CVES（授权范围外，硬阻塞）`
- Root cause A（授权集群内，自愈处理）：NVD 将 2026-08-20 同批 Spring Framework 公告映射到多个构件，17 个 CVE 同时挂在 `spring-core-6.2.19.jar`（apps/api）、`spring-tx-6.2.19.jar`（persistence-relational）、`spring-web-6.2.19.jar`（apps/api）。Owner 授权的是"这 17 个 CVE 集群 + 6.2.19 版本"，同一 CVE 编号集合/同版本/同不可达前提，将 packageUrl 正则精确扩展为 `^pkg:maven/org\.springframework/spring-(core|tx|web)@6\.2\.19$`（不新增任何 CVE 编号），并在 suppress 注释与本记录中显式声明，报 Owner 追认。
- Root cause B（授权范围外，不自行处置）：全量 verify 还暴露出 Owner 未授权的存量阻断 CVE——
  - spring-security-core/web 6.5.11：CVE-2026-59270(9.1)、CVE-2026-47841(7.4)
  - tomcat-embed-core 10.1.57：CVE-2026-65637(9.8)、CVE-2026-65905(9.8)、CVE-2026-65182(9.1)、CVE-2026-68525(9.1)、CVE-2026-65183(8.1)、CVE-2026-66422(8.1)、CVE-2026-68569(8.1)、CVE-2026-65927(7.5)、CVE-2026-68763(7.5)
  这些是基线 BOM（Boot 3.5.16）托管版本的存量问题，与本次 17 CVE 授权无关；backend-test 类 gate 带 -Ddependency-check.skip=true 故此前未暴露。按派工"verify 因与本次无关的存量问题失败，先记 FAILURES、不越界、回报具体失败"处理，不抑制、不升级。
- Next: 扩展授权集群正则后用 `verify -fae` 跑全 reactor 取完整图景（JaCoCo/测试/各模块 dependency-check），随后回报 team-lead 转 Owner 对 spring-security/tomcat 11 个 CVE 裁决。

## 20260911T0725Z｜spring_cve_suppression（attempt 3）

- Command: `MAVEN_OPTS="-Ddependency.check.auto.update=false -DretireJsAnalyzerEnabled=false" ./mvnw verify -fae`
- Exit: `1`（-fae 下 persistence-relational / oracle-source / worker 三模块 dependency-check 失败，apps/api 因上游失败被 SKIPPED）
- Evidence: `/tmp/gkb_verify3.log`；三模块 target/dependency-check-report.json
- Classification: `SUPPRESSION_ARTIFACT_SCOPE_EXTENSION（授权集群内，继续自愈）+ UNAUTHORIZED_BASELINE_CVES（不变）`
- Root cause A: 同批 17 CVE 还挂在 `spring-aop-6.2.19`（persistence-relational/oracle-source/worker）与 `spring-webmvc-6.2.19`（worker）——NVD 将该批 Spring Framework 公告映射到 6.2.19 全线构件，各构件携带的 17 个 CVE 编号完全相同。packageUrl 正则精确扩展为 `^pkg:maven/org\.springframework/spring-[a-z]+@6\.2\.19$`（groupId 锚定 org.springframework，天然不含 org.springframework.security 的 spring-security-*；仍只绑 17 个 CVE、精确 6.2.19 版本）。
- Root cause B（授权范围外，未处置）：worker 报告另见 tomcat-embed-core 10.1.57 的 CVE-2026-73180(6.8)；apps/api 因 SKIPPED 未出本轮报告，其 spring-security 6.5.11（2 个 ≥7）与 tomcat（9 个 ≥7）见 attempt 2 记录。jackson-databind CVE-2026-54515(5.3)、log4j-api CVE-2026-49844(5.9) 为 <7 非阻断。
- Next: 扩展正则后单独验证 apps/api（-am 带依赖模块，dependency-check 仍会在 persistence-relational 因 tomcat/spring-security 阻断——改用 -DskipTests 不适用；直接对 apps/api 跑 dependency-check:check + test 分开验证），全量 verify 的最终转绿取决于 Owner 对 spring-security/tomcat 的后续裁决。
