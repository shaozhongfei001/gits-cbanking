# Handoff｜P25-gits-crm-directory｜feature_pilot

**Time**: `2026-08-22T11:13:17Z`
**Role**: `feature_pilot`
**Baton**: remains `feature_pilot`

## Backend CRM upsert (this slice)

GITS H2 `customer` table is CRM directory only. Upsert/reload never write KYC/products/transactions/graph.

1. DTOs: `CrmCustomerMaster`, `CrmCustomerUpsertResponse`, `CrmCustomerMasterReloadResponse`
2. `WritableCustomerRepository.update()` — MyBatis `CustomerMapper.xml` + `JdbcCustomerRepository` UPDATE
3. `CrmCustomerMasterService`: path≠body → 400; both credit codes non-blank and differ → 409; fixture reload upserts `CUST-CORP-0001`
4. `PUT /api/v1/engagement/customer/{customerId}` and `POST /api/v1/engagement/crm-customer-master/reload`
5. Startup load after Flyway when `gits.crm-master.load-on-startup=true` (default). Missing fixture: warn, do not fail boot.
6. Tests: `CrmCustomerMasterServiceTest` (6), `CustomerContextControllerTest` (8 including PUT CREATED→UPDATED and POST reload)

Command: `./mvnw -pl apps/api -am -Dsurefire.failIfNoSpecifiedTests=false -Dtest=CrmCustomerMasterServiceTest,CustomerContextControllerTest,CustomerContextServiceTest test`
Result: Tests run: 14, Failures: 0. `CustomerContextServiceTest` not present (failIfNoSpecifiedTests=false).

## Frontend slice (prior)

Workbench CRM directory refresh. Does not pack DKWS knowledge.

1. `frontend/src/api/engagement.ts` — types + `upsertCrmCustomer` + `reloadCrmCustomerMaster`
2. `frontend/src/views/EngagementWorkspace.vue` — 「刷新客户目录」
3. Vitest: 2 files, 50 tests passed

## 未交

- `QA_PASS` / independent QA / `DEV_SELF_CHECK_PASS`
- OpenAPI / `generated/` (must not change)
- Did not touch `loops/P24-dkws-platform`
- No commit

## 关键提示

- Do not `git add .`. Do not write `QA_PASS`.
- Fixture SSOT: `docs/dd/fixtures/gits-crm-customer-master.json`
- Primary identity: `CUST-CORP-0001` / `RM-ZW-001`
