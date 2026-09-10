# GKB-baseline-hardening｜Evidence index

机器可判定的唯一证据板为 `EVIDENCE.json`。本文件只提供人类导航，不复制状态。

- 命令日志：`evidence/`
- 失败记录：`FAILURES.md`
- 波次迭代：`memory/waves/`
- 独立QA：必须由非implementation actor写入 `EVIDENCE.json.independent_qa`

## 2026-09-11 baseline-pilot 实施波次（W0）结果

| Gate | 结果 | 证据 |
|---|---|---|
| repro_baseline | fail（**预期**：复现成功，pass_condition 即 exit 1 + 4 errors） | `evidence/repro_baseline-20260910T162825Z.log`（Tests run: 4, Errors: 4，NoSuchBeanDefinitionException: CustomerJourneyRepository） |
| fix_test_slice | **pass** | `evidence/fix_test_slice-20260910T162957Z.log`（Tests run: 4, Failures: 0, Errors: 0） |
| apps_api_regression | **pass** | `evidence/apps_api_regression-20260910T163012Z.log`（Tests run: 450, Failures: 0, Errors: 0, Skipped: 4） |
| spring_cve_decision_package | **pass** | `evidence/SPRING_CORE_CVE_DECISION.md`（17 CVE 清单/可达性/版本可得性/三方案/抑制 XML 草案） |
| security_check | **pass** | `evidence/security_check-20260910T163850Z.log`（secret-scan PASS 111 advisory 非阻断、sensitive-permissions PASS、oracle-readonly-guard PASS） |

### 代码变更（唯一生产外变更）

- `apps/api/src/test/java/com/gien/gits/api/controller/EngagementJourneyControllerTest.java`：补 2 个 `@MockitoBean`（`CustomerJourneyRepository journeyRepository`、`RelationshipReportRepository reportRepository`）+ 对应 import。未改生产代码、未删/弱化断言。测试中既有的多余 `AuditLogPort` mock 保留未动（无害）。

### LOOP.yaml gate 命令机械修正（已记录 FAILURES.md）

- repro_baseline / fix_test_slice 两条命令补 `-Dsurefire.failIfNoSpecifiedTests=false`：原命令 `-am` 会在依赖模块因匹配不到指定测试而提前失败（surefire 3.5.6 默认 failIfNoSpecifiedTests=true），即使修复后也永远无法通过。修正不改变 gate 意图。

### spring-core CVE 决策（待 Owner 裁决，未落地）

- 17 个 CVE（11 个 CVSS≥7），2026-08-20 披露；6.2.20 修复版为 Enterprise Support Only（Maven Central 实测 404），OSS 唯一修复路径为 Framework 7.0.9（需 Boot 4.x）。
- 逐项可达性核查：本项目 Servlet+Tomcat+纯 JSON API 架构下，17 项利用前提（WebFlux/RSocket/Jetty12/XSLT/FreeMarker/SSE/用户 SpEL/表单绑定/文件头）均不存在。
- 编制者推荐：**方案 A 窄抑制（until 2026-12-31）即时解阻 + 并行立项方案 C（Boot4 迁移）根治**；方案 B 仅在 Owner 持 Enterprise 合同时首选。
- 决策包含可直接采用的精确抑制 XML 草案；**未修改 `dependency-check-suppressions.xml`、未改任何 pom**。

### 状态

- STATE → `ready_for_independent_qa`；Baton → `owner_review`（spring CVE 必须 Owner 裁决）。
- 交接：`memory/handoffs/baseline-pilot.md`。
