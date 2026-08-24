# P25-gits-crm-directory｜Failures（append-only）

失败必须在修改实现之前由 `scripts/record_gate.py`追加。每项至少包含时间、Gate、命令、退出码、证据文件、初步分类和下一动作；修复后追加根因、变更SHA与原命令重跑结果，不覆盖原记录。

## 2026-08-22T11:12:44Z | unit_api | FAIL

- Gate: `unit_api`
- Command: `./mvnw -pl apps/api -am -Dsurefire.failIfNoSpecifiedTests=false -Dtest=CrmCustomerMasterServiceTest,CustomerContextControllerTest,CustomerContextServiceTest test`
- Exit: `1`
- Evidence: surefire `CrmCustomerMasterServiceTest.reloadFromFixture_upsertsPrimaryDemoCustomer`
- Classification: fixture path resolution — Surefire `user.dir` is `apps/api`; one-level parent is `apps/`, not repo root, so `docs/dd/fixtures/gits-crm-customer-master.json` was not found
- Next: walk `user.dir` ancestors until the fixture file exists; rerun the same Maven command
- Repair: `CrmCustomerMasterService.resolveFixtureFile()` now walks `user.dir` ancestors (apps/api → apps → repo root). Rerun 2026-08-22T11:13:17Z exit 0; Tests run: 14, Failures: 0.

