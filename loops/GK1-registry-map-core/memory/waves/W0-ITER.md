# W0｜Iteration log（append-only）

由 `scripts/record_gate.py` 追加实际attempt、命令、退出码、证据hash和下一动作。没有实际执行不得登记PASS。

## Attempt 1｜20260910T150220Z

- Gate: `contract_check`
- Command: `make generate && make check`
- Exit: `0`
- Evidence: `loops/GK1-registry-map-core/evidence/contract_check-20260910T150220Z.log`
- SHA256: `6db14820bf55424b6cc77039050eeb3f4273e4c599f4499aee8592261eeb1752`

## Attempt 1｜20260910T151348Z

- Gate: `registry_core`
- Command: `./mvnw --batch-mode --no-transfer-progress -pl modules/knowledge-architecture -am test -Dtest='RegistryCoreTest,AssetCatalogRegistryTest,NormalizationTest,DependencyClosureTest'`
- Exit: `1`
- Evidence: `loops/GK1-registry-map-core/evidence/registry_core-20260910T151348Z.log`
- SHA256: `38255244ef43ff8322f2e0d59e92d39eee07e552f7f65ebcfecef57ae6d306d4`

## Attempt 2｜20260910T151842Z

- Gate: `registry_core`
- Command: `./mvnw --batch-mode --no-transfer-progress -pl modules/knowledge-architecture -am test -Dtest='RegistryCoreTest,AssetCatalogRegistryTest,NormalizationTest,DependencyClosureTest'`
- Exit: `0`
- Evidence: `loops/GK1-registry-map-core/evidence/registry_core-20260910T151842Z.log`
- SHA256: `86921ce095f637fdb7af99d995331695d8d9ffd4ec44d0407aeb2daff31b302d`

## Attempt 1｜20260910T152025Z

- Gate: `map_dag_validate`
- Command: `./mvnw --batch-mode --no-transfer-progress -pl modules/knowledge-architecture test -Dtest='*Dag*,*MapCycle*,*KnowledgeMap*'`
- Exit: `0`
- Evidence: `loops/GK1-registry-map-core/evidence/map_dag_validate-20260910T152025Z.log`
- SHA256: `f68cda47e12d4500d91082dc47a2f0ce947d653f46c892013c0ae5b2ef694d57`

## Attempt 1｜20260910T152433Z

- Gate: `permission_filter`
- Command: `./mvnw --batch-mode --no-transfer-progress -pl modules/knowledge-architecture test -Dtest='*Permission*,*Scope*,*Secret*,*Access*'`
- Exit: `0`
- Evidence: `loops/GK1-registry-map-core/evidence/permission_filter-20260910T152433Z.log`
- SHA256: `c82b6549861a6d522e16d76e3c4cb8350c2f23396ba54e63ceb0c3d676acdee3`

## Attempt 1｜20260910T152747Z

- Gate: `plan_canonical_hash`
- Command: `./mvnw --batch-mode --no-transfer-progress -pl modules/knowledge-architecture test -Dtest='*ActivationPlan*,*PlanHash*,*Canonical*,*TaskContext*'`
- Exit: `0`
- Evidence: `loops/GK1-registry-map-core/evidence/plan_canonical_hash-20260910T152747Z.log`
- SHA256: `99fdbcefc42ee30d4a562f85db56d6d906ba2f88ec1bed29f0091ebcf5cb97a5`

## Attempt 1｜20260910T154424Z

- Gate: `backend_test`
- Command: `make backend-test`
- Exit: `2`
- Evidence: `loops/GK1-registry-map-core/evidence/backend_test-20260910T154424Z.log`
- SHA256: `2ee590dd0f406e9f49c39b8c944c3498c858fa4b93c2e3645287a224feb3a4ef`

## Attempt 2｜20260910T154927Z

- Gate: `backend_test`
- Command: `make backend-test`
- Exit: `2`
- Evidence: `loops/GK1-registry-map-core/evidence/backend_test-20260910T154927Z.log`
- SHA256: `45bbbc90aee245a585140c9d5ddb8db6b7ff8ac5003e12cef971fb3afc224ceb`

## Attempt 2｜20260910T155033Z

- Gate: `backend_test`
- Command: `make backend-test`
- Exit: `2`
- Evidence: `loops/GK1-registry-map-core/evidence/backend_test-20260910T155033Z.log`
- SHA256: `a707ab9a93a3db1d5eb6851c631d6fdf928771b5e896734887d9537dbc8439e9`

## Attempt 4｜20260910T160230Z

- Gate: `backend_test`
- Command: `make backend-test`
- Exit: `2`
- Evidence: `loops/GK1-registry-map-core/evidence/backend_test-20260910T160230Z.log`
- SHA256: `248219cfb4039d9879e4cbd20abbbdac425f5bc1c05d7c5df01894f24c733374`

## Attempt 1｜20260910T161059Z

- Gate: `security_check`
- Command: `make security-check`
- Exit: `0`
- Evidence: `loops/GK1-registry-map-core/evidence/security_check-20260910T161059Z.log`
- SHA256: `699c514935724263bca7c41fb8786a211fc2b7c2ce083b7cc1fe44e2a2b92ad0`

## Attempt 2｜20260910T161124Z

- Gate: `security_check`
- Command: `make security-check`
- Exit: `0`
- Evidence: `loops/GK1-registry-map-core/evidence/security_check-20260910T161124Z.log`
- SHA256: `699c514935724263bca7c41fb8786a211fc2b7c2ce083b7cc1fe44e2a2b92ad0`
