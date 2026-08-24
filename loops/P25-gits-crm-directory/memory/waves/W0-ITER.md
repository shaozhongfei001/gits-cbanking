# W0｜Iteration log（append-only）

由 `scripts/record_gate.py` 追加实际attempt、命令、退出码、证据hash和下一动作。没有实际执行不得登记PASS。

## 2026-08-22T11:12:44Z | unit_api (manual, before record_gate)

- Actor: `feature_pilot`
- Result: FAIL — fixture not found from Surefire `user.dir=apps/api` (parent is `apps/`, not repo root)
- Next: walk ancestors in `resolveFixtureFile`

## 2026-08-22T11:13:17Z | unit_api (manual rerun)

- Actor: `feature_pilot`
- Command: `./mvnw -pl apps/api -am -Dsurefire.failIfNoSpecifiedTests=false -Dtest=CrmCustomerMasterServiceTest,CustomerContextControllerTest,CustomerContextServiceTest test`
- Exit: `0`
- Result: Tests run: 14, Failures: 0


## Attempt 1｜20260823T171106Z

- Gate: `contract_generate`
- Command: `make generate`
- Exit: `0`
- Evidence: `loops/P25-gits-crm-directory/evidence/contract_generate-20260823T171106Z.log`
- SHA256: `048ab7c55cfbb3c6707b7212288bd84d678861d4abb19a7eca16fbb7a71803b8`

## Attempt 1｜20260823T171106Z

- Gate: `contract_check`
- Command: `make check`
- Exit: `0`
- Evidence: `loops/P25-gits-crm-directory/evidence/contract_check-20260823T171106Z.log`
- SHA256: `0a9da677b7a3943b8860a78e776b733929e475f1c2161207198a573a9f916e3b`

## Attempt 1｜20260823T171107Z

- Gate: `security_check`
- Command: `make security-check`
- Exit: `0`
- Evidence: `loops/P25-gits-crm-directory/evidence/security_check-20260823T171107Z.log`
- SHA256: `2b4fcb2684ba673957048528ce7fb2842671246fd521c1d9660cfd271626ba64`
