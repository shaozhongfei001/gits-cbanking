# P25 Tech Lead delivery plan

Updated: 2026-08-22
Role: tech_lead
Baton: do not touch P24-dkws-platform (holder=independent_qa).

## Principle

GITS does not dump DKWS knowledge into H2. `customer` is a CRM directory. Workbench selects a row; Skill receives that `customerId` only.

## Frozen identity

- Primary demo: `CUST-CORP-0001` 华东精工装备集团有限公司 / RM-ZW-001
- Do not mix with V1.1 `CUST-001` unless `SCENARIO_DATA_ROOT` is explicitly on
- Fixture SSOT: `docs/dd/fixtures/gits-crm-customer-master.json`

## Approved contract (CTR-API-001)

- `PUT /api/v1/engagement/customer/{customerId}` operationId `upsertCrmCustomer`
- Body `CrmCustomerMaster` (CRM fields only, additionalProperties false)
- Path id must equal body.customerId or 400
- Same id + different unifiedSocialCreditCode → 409 STATE_CONFLICT
- 200 `{customerId, customerName, status: CREATED|UPDATED}`
- `POST /api/v1/engagement/crm-customer-master/reload` loads the fixture (idempotent upsert)

Out of scope: KI ingest, outreach/meeting Skill cutover, inventing OpenAPI KYC fields on this resource.

## Feature Pilot tasks

1. Port: upsert on WritableCustomerRepository (MyBatis update + JDBC update; MERGE/update-by-id)
2. Service: map CrmCustomerMaster → Customer; reject unknown extra JSON (already additionalProperties false)
3. Startup: after Flyway, load fixture into customer (config `gits.crm-master.fixture-path`, default the docs/dd fixture; skip missing file)
4. Tests: create, update, 409 credit-code clash, reload does not write KYC
5. Frontend: types + workbench 刷新客户 list (GET already exists)

## E2E Owner

Run unit tests + make generate/check. Record DEV_SELF_CHECK only if needed. Do not write QA_PASS.
