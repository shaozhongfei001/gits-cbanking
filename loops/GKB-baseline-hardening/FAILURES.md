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
