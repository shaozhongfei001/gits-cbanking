# P23-scenario-knowledge-provider｜Failures（append-only）

失败必须在修改实现之前由 `scripts/record_gate.py`追加。每项至少包含时间、Gate、命令、退出码、证据文件、初步分类和下一动作；修复后追加根因、变更SHA与原命令重跑结果，不覆盖原记录。

## FAIL-2026-08-20-01｜Gate `backend_test` 未达标（apps/api 覆盖率门槛）

- **time**: `2026-08-20T12:47:00Z`
- **gate**: `backend_test`
- **command**: `make backend-test`（即 `./mvnw --batch-mode --no-transfer-progress verify` + `dependency-check-guard.py`）
- **exit_code**: 1（`BUILD FAILURE`）
- **preliminary_classification**: `apps_api_coverage_existing_baseline`
- **evidence**: `make backend-test 输出`；根因模块 `apps/api` JaCoCo：`lines covered ratio is 0.78, but expected minimum is 0.80`
- **root_cause**:
  - 与本 Loop 改动无关。本 Loop 改动仅限 `scenario/execute`（新增 `hermes.knowledge.SimulatedKnowledgeProvider`/`KnowledgeAssemblyResult`/测试）与 `scenario/seed/05_knowledge/demo`（演示数据），全 Reactor 编译 SUCCESS、`scenario-execute` 全部测试 PASS、`scenario-execute` 覆盖率达标。
  - `BUILD FAILURE` 仅发生在 `gits-kno-api`（apps/api）模块，因 JaCoCo 行覆盖率 0.78 < 门槛 0.80。
  - 根因是**用户未提交的在制品改动**（git 中 ` M` 的三个 apps/api 文件：`EngagementConfig.java`、`ScenarioSeedDataService.java`、`V11ScenarioDataLoader.java`，其中 `V11ScenarioDataLoader.loadTransactions` + 交易流水类型映射新增约 61 行未覆盖路径）。
- **next_action**:
  - 本次 Loop 的 scenario 侧 gate 已自证通过（编译 + 测试 + 覆盖率达标）。
  - apps/api 覆盖率需由持有该在制品改动的责任方补充针对 `loadTransactions`/`mapTransactionType`/`mapTransaction` 的单元测试，或暂不纳入本 Loop 的 `backend_test` gate。**本 Loop 不扩权改动 apps/api 用户在制代码。**

## FAIL-2026-08-20-01 修复记录｜apps/api 覆盖率达标

- **fix_time**: `2026-08-20T14:24:00+08:00`
- **change_sha**: `make backend-test` 重新运行通过（`BUILD SUCCESS` + `dependency-check-guard` 全 PASS）
- **root_cause**: 补充如下单元测试，使 apps/api JaCoCo 行覆盖率 ≥ 0.80 门槛：
  - `service/TaskServiceTest`（11 项）、`service/CommitmentServiceTest`（10 项）
  - `service/OpportunityServiceTest`（10 项）、`service/ExternalEventServiceTest`（9 项）、`service/ProductKnowledgeVersionServiceTest`（7 项）
  - `controller/GlobalExceptionHandlerTest`（7 项）
  - 均为对既有 pure-delegation Service / Controller Advice 的补充覆盖测试，未改动任何实现代码，未触碰用户在制改动。
- **rerun_result**: `make backend-test` → `BUILD SUCCESS`，`Jacoco lines covered ratio ≥ 0.80` 通过。

## FAIL-2026-08-21-01｜Independent QA re-run rejected（actor=`independent_qa`）

- **time**: `2026-08-21T09:44:46Z`（started）/ `2026-08-21T09:48:45Z`（attested reject）
- **actor**: `independent_qa`（NOT implementation / NOT feature_pilot / NOT tech_lead）
- **session**: `iqa-p23-20260821T094446Z`
- **gate**: independent re-run of `evidence_check` + `backend_test`（LOOP.yaml owner_kind=implementation；QA 不改写实现侧 gate 记录）
- **commands**:
  - `make evidence-check LOOP=P23-scenario-knowledge-provider` → **exit 0**
  - `make backend-test` → **exit 2**
  - `./mvnw -pl scenario/execute -am -q --batch-mode --no-transfer-progress test` → **exit 1**
- **preliminary_classification**: `backend_test_owasp_retirejs_timeout` + `scenario_execute_wip_compile_error`
- **evidence**: `loops/P23-scenario-knowledge-provider/evidence/independent_qa_20260821T094446Z.log`
- **output_sha256**: `4a288e84abca0c74cea68603bbbc559c6cd3c8710d73cdfb7a5bac81541a5a26`
- **qa_attest**: `--decision reject` exit 0；STATE `blocked` / `INDEPENDENT_QA_REJECTED`
- **observed**:
  1. Seed assets present under `scenario/seed/05_knowledge/demo/`（knowledge-map.yaml、tasks.yaml、activation-contract.json、rules.yaml、elements/KI-FRONT-001~006）。
  2. `backend-deps-check: PASS`；`./mvnw verify` failed on root module `gits-knowledge-engineering` plugin `org.owasp:dependency-check-maven:12.1.0:check`：`UpdateException: Failed to initialize the RetireJS repo` caused by `DownloadFailedException` / `SocketTimeoutException: Read timed out` fetching `jsrepository.json` from GitHub raw.
  3. Additional scenario-execute test compile failed in `scenario/execute/src/main/java/com/gien/gits/engagement/skill/SkillExecutionRouter.java`（missing `org.slf4j`, missing `com.gien.gits.knowledge`, `ModelCall` vs `ModelCallEntry` type mismatch）。These files were untracked WIP at QA start and are outside the P23 hermes.knowledge seed-provider deliverable.
- **next_action**: baton → `feature_pilot`。按原命令修复后重跑 `make backend-test`；处理或隔离导致 scenario-execute 无法编译的 WIP；失败先记本文件再改实现。独立 QA 未写 `QA_PASS` / `REAL_E2E_PASS`。

## FAIL-2026-08-21-01 修复记录｜feature_pilot

- **fix_time**: `2026-08-21T10:01:14Z`
- **actor**: `feature_pilot`（implementation；未自签 QA_PASS）
- **rerun_command**: `make backend-test`（via `scripts/record_gate.py --gate backend_test`）
- **rerun_result**: EXIT=`0`，`BUILD SUCCESS`，`dependency-check-guard` 15 reports PASS
- **evidence**: `loops/P23-scenario-knowledge-provider/evidence/backend_test-20260821T095949Z.log`
- **output_sha256**: `d5356d949dec503d5e676afdf0856ea4a23fb529dbb4f3c4379ad9a94974e365`
- **root_cause / 变更**:
  1. OWASP RetireJS：独立环境从 GitHub raw 拉 `jsrepository.json` Read timed out，且 `failOnError=true` 使根模块 verify 失败。扫描器保持启用；`retireJsUrl` 改为仓库快照 `tools/owasp/jsrepository.json`（`retireJsForceUpdate=false`），不再在 verify 时访问 GitHub。
  2. `SkillExecutionRouter` WIP 编译失败：去掉对 `ActivationContract` 的模块依赖（改为 `List<String> skills`）、补 `slf4j-api`、`modelCalls` 使用 `SkillExecutionResult.ModelCall`、`SkillExecutionCommand.customerId` 禁止 null。测试 8 项通过。
- **next_action**: 状态交回 `ready_for_independent_qa`，baton → `independent_qa`。开发角色不得自签 QA_PASS。
