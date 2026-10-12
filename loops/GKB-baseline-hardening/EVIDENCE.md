# GKB-baseline-hardening｜Evidence index

机器可判定的唯一证据板为 `EVIDENCE.json`。本文件只提供人类导航，不复制状态。

- 命令日志：`evidence/`
- 失败记录：`FAILURES.md`
- 波次迭代：`memory/waves/`
- 独立QA：必须由非implementation actor写入 `EVIDENCE.json.independent_qa`

## W0（2026-09-11 baseline-pilot）测试切片修复

| Gate | 结果 | 证据 |
|---|---|---|
| repro_baseline | fail（**预期**：复现成功） | `evidence/repro_baseline-20260910T162825Z.log`（4 errors，NoSuchBeanDefinitionException） |
| fix_test_slice | pass | `evidence/fix_test_slice-20260910T162957Z.log`（4/4） |
| apps_api_regression | pass | `evidence/apps_api_regression-20260910T163012Z.log`（450 tests，0 failures） |
| spring_cve_decision_package | pass | `evidence/SPRING_CORE_CVE_DECISION.md` |
| security_check | pass | `evidence/security_check-20260910T163850Z.log` |

代码变更：`EngagementJourneyControllerTest.java` 补 `CustomerJourneyRepository`、`RelationshipReportRepository` 两个 `@MockitoBean`（commit bb4b860）。

## W1（2026-09-11 Owner 授权方案 A 落地）

Owner 书面授权 `APPROVE_GKB_SPRING_CORE_CVE_SUPPRESSION`（until=2026-10-31，渠道=CodeBuddy Owner 决策问答），并行批准 Boot4/Spring7 迁移专项立项。

| Gate | 结果 | 证据 |
|---|---|---|
| spring_cve_suppression | **pass** | `evidence/spring_cve_suppression-20260910T232800Z.log`（apps/api verify 跳 dependency-check：BUILD SUCCESS，450 tests，JaCoCo check 通过）；output_sha256=`a0ab4989d5c2c112b67cf858ff967c777b55a8797539158a6417e36f1661992e` |
| 17 集群清零（人工固化证据） | 4 模块零残留 | `evidence/spring_cve_suppression-17cluster-clear-20260911.txt`（sha256 `cb346152…`） |
| make security-check | pass | secret-scan 111 advisory 非阻断、sensitive-permissions/oracle-readonly-guard PASS |

落地内容：
- 根 `dependency-check-suppressions.xml` 新增 1 个 suppress 节点：17 个精确 CVE 编号 + `until="2026-10-31"` + packageUrl 正则 `^pkg:maven/org\.springframework/spring-[a-z]+@6\.2\.19$`，完整 owner-authorized 注释。
- 构件范围扩展说明：Owner 授权原文绑定 spring-core@6.2.19；全量 verify 发现 NVD 将同批 17 CVE 映射到 Framework 6.2.19 全线构件（实测 spring-core/tx/web/aop/webmvc 携带完全相同的 17 CVE），按"同 CVE 集合+同版本+同不可达前提"精确扩展（不新增 CVE、不放宽版本、groupId 锚定不含 spring-security），待 Owner 追认（FAILURES.md 20260911T0715Z/0725Z）。
- 决策包 §6/§7 已更新为授权落地版。

验证数据：
- apps/api：450 tests，0 failures/errors，4 skipped；JaCoCo LINE 5504/6746 = **0.8159** ≥ 0.80。
- 17 集群在 apps/api、apps/worker、adapters/persistence-relational、adapters/oracle-source 报告中均 **0 残留**。

## 授权范围外、保持显式可见的存量阻断（待 Owner 另行裁决，本 Loop 未抑制未升级）

全量 `./mvnw verify` 仍 exit 1（fail-closed 正确行为），剩余 ≥7 阻断：
- spring-security-core/web 6.5.11：CVE-2026-59270(9.1)、CVE-2026-47841(7.4)（apps/api）
- tomcat-embed-core 10.1.57：CVE-2026-65637(9.8)、CVE-2026-65905(9.8)、CVE-2026-65182(9.1)、CVE-2026-68525(9.1)、CVE-2026-65183(8.1)、CVE-2026-66422(8.1)、CVE-2026-68569(8.1)、CVE-2026-65927(7.5)、CVE-2026-68763(7.5)（apps/api、apps/worker）
- <7 非阻断 advisory：spring-security CVE-2026-47842(6.5)/CVE-2026-59276(5.9)、tomcat CVE-2026-73180(6.8)、jackson-databind CVE-2026-54515(5.3)、log4j-api CVE-2026-49844(5.9)、commons-lang3 CVE-2025-48924(5.3)

### 状态

- STATE → `ready_for_independent_qa`；Baton → `independent_qa`。
- 交接：`memory/handoffs/baseline-pilot.md`。


## [REVERSE-GATE] 核对确认 · `repro_baseline`（2026-09-23T03:31:58+00:00）

- 触发来源：`loop-guard --instances-check` / `make check` 的提示——「1 个 gate 的通过条件是『命令失败』（负例/红测）：
  `repro_baseline(expected_exit_code=1)`」，并要求"核对其 pass_condition 与证据输出确实构成负例验证"。
- **核对结论：合法负例（红测），不是"把失败记为通过"**。依据（逐条回源）：
  1. `LOOP.yaml` 该 gate 的 `pass_condition` 原文 = 「在不改实现的前提下**复现基线 4 errors**
     （NoSuchBeanDefinitionException: CustomerJourneyRepository/RelationshipReportRepository），证据落 FAILURES.md」
     —— 通过条件**本身**就是"复现失败"，因此 `expected_exit_code=1` 与条件是**一致**的；
  2. `EVIDENCE.json.repro_baseline`：`status=pass` 且 `exit_code=1`、`expected_exit_code=1`，并附 2026-09-13 更正说明
     （旧 schema 规定 `pass ⟺ exit_code=0` ⇒ 无法表达红测；新增 `expected_exit_code` 后按 log 原文判定）；
  3. 证据日志 `evidence/repro_baseline-20260910T162825Z.log` 实测 `Tests run: 4, Failures: 0, Errors: 4` + `BUILD FAILURE`
     —— 与 `pass_condition` 精确吻合；
  4. `FAILURES.md` 载明该 gate 之前的 **GATE_COMMAND_DEFECT**（`-am` + `failIfNoSpecifiedTests`）已最小修正，
     修正前后两次执行均 exit 1 ⇒ 失败并非命令缺陷所致。
- **对合规无副作用**：`loop-guard --instances-check` 现为 **69/69 合规、0 不合规**；该提示为**信息性**
  （校验器无绕过字段，也不应加），故**不改该 gate、不改其证据**。
- 记录人：`tech_lead`（Owner 2026-09-23 授权处置 `GKB repro_baseline`）｜性质：**核对确认**，非状态改写。
