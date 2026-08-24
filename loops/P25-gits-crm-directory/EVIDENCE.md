# P25-gits-crm-directory｜Evidence index

机器可判定的唯一证据板为 `EVIDENCE.json`。本文件只提供人类导航，不复制状态。

- 命令日志：`evidence/`
- 失败记录：`FAILURES.md`
- 波次迭代：`memory/waves/`
- 独立QA：必须由非implementation actor写入 `EVIDENCE.json.independent_qa`

## Backend CRM upsert (not yet recorded via record_gate.py)

- Command: `./mvnw -pl apps/api -am -Dsurefire.failIfNoSpecifiedTests=false -Dtest=CrmCustomerMasterServiceTest,CustomerContextControllerTest,CustomerContextServiceTest test`
- Result: Tests run: 14, Failures: 0 (2026-08-22T11:13:17Z). First attempt failed on fixture path; recorded in FAILURES.md.
- Actor: feature_pilot (backend). Not QA_PASS.

## Frontend slice (not a LOOP.yaml gate)

- Command: `cd frontend && npx vitest run src/api/__tests__/engagement.spec.ts src/views/__tests__/EngagementWorkspace.spec.ts`
- Result: Test Files 2 passed; Tests 50 passed; Duration 1.50s
- Actor: feature_pilot (frontend). Not QA_PASS.

