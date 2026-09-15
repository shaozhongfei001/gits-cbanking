# W0｜Iteration log（append-only）

由 `scripts/record_gate.py` 追加实际attempt、命令、退出码、证据hash和下一动作。没有实际执行不得登记PASS。

## Attempt 1｜20260915T002316Z

- Gate: `contract_generate`
- Command: `make generate`
- Exit: `0`
- Evidence: `loops/GK17-ontology-unified-map/evidence/contract_generate-20260915T002316Z.log`
- SHA256: `048ab7c55cfbb3c6707b7212288bd84d678861d4abb19a7eca16fbb7a71803b8`

## Attempt 1｜20260915T002319Z

- Gate: `contract_check`
- Command: `make check`
- Exit: `0`
- Evidence: `loops/GK17-ontology-unified-map/evidence/contract_check-20260915T002319Z.log`
- SHA256: `0e4db17e674d23fd938f5844527af42dee3a77cea000144e5514cae6e0303b0f`

## Attempt 1｜20260915T002323Z

- Gate: `gk_ke_gates`
- Command: `python3 scripts/run_gates.py`
- Exit: `0`
- Evidence: `loops/GK17-ontology-unified-map/evidence/gk_ke_gates-20260915T002323Z.log`
- SHA256: `ccc178caebd628d35575eea9837100e189bee3cd393d797af737f8d6f08ba3a8`

## Attempt 1｜20260915T002327Z

- Gate: `ontology_load`
- Command: `./mvnw -q -pl apps/api test -Dtest=MechanismE2eIT -DskipITs=false`
- Exit: `0`
- Evidence: `loops/GK17-ontology-unified-map/evidence/ontology_load-20260915T002327Z.log`
- SHA256: `6fe53c90119a99cbf77117f5976a0b87beb7d3dea2a7a0cd6408e3cb8c32e7fe`

## Attempt 1｜20260915T002331Z

- Gate: `security_check`
- Command: `make security-check`
- Exit: `0`
- Evidence: `loops/GK17-ontology-unified-map/evidence/security_check-20260915T002331Z.log`
- SHA256: `83a2808577106ca7d7fd16d9aee2783e798237b7e30df82b91008f63891a9ebd`

## Attempt 1｜20260915T002338Z

- Gate: `backend_test`
- Command: `make backend-test`
- Exit: `0`
- Evidence: `loops/GK17-ontology-unified-map/evidence/backend_test-20260915T002338Z.log`
- SHA256: `e7d2669def2ee7d53ce5f293ddb11ed6bcd54ce066565341851834b1dcb16f48`

## Attempt 1｜20260915T002544Z

- Gate: `frontend_test`
- Command: `make frontend-test`
- Exit: `2`
- Evidence: `loops/GK17-ontology-unified-map/evidence/frontend_test-20260915T002544Z.log`
- SHA256: `596e61483f5c67b8932d37d08ba3cab40d903ef084f4483a97d4ea7022bd48c1`

## Attempt 2｜20260915T002723Z

- Gate: `contract_generate`
- Command: `make generate`
- Exit: `0`
- Evidence: `loops/GK17-ontology-unified-map/evidence/contract_generate-20260915T002723Z.log`
- SHA256: `048ab7c55cfbb3c6707b7212288bd84d678861d4abb19a7eca16fbb7a71803b8`

## Attempt 2｜20260915T002723Z

- Gate: `contract_check`
- Command: `make check`
- Exit: `0`
- Evidence: `loops/GK17-ontology-unified-map/evidence/contract_check-20260915T002723Z.log`
- SHA256: `0e4db17e674d23fd938f5844527af42dee3a77cea000144e5514cae6e0303b0f`

## Attempt 2｜20260915T002727Z

- Gate: `gk_ke_gates`
- Command: `python3 scripts/run_gates.py`
- Exit: `0`
- Evidence: `loops/GK17-ontology-unified-map/evidence/gk_ke_gates-20260915T002727Z.log`
- SHA256: `7dc821307932253394b5cab6d08a78fa8cfdcdab6f29ec637cd04b9f7af6a05f`

## Attempt 2｜20260915T002731Z

- Gate: `ontology_load`
- Command: `./mvnw -q -pl apps/api test -Dtest=MechanismE2eIT -DskipITs=false`
- Exit: `0`
- Evidence: `loops/GK17-ontology-unified-map/evidence/ontology_load-20260915T002731Z.log`
- SHA256: `6fe53c90119a99cbf77117f5976a0b87beb7d3dea2a7a0cd6408e3cb8c32e7fe`

## Attempt 2｜20260915T002735Z

- Gate: `security_check`
- Command: `make security-check`
- Exit: `0`
- Evidence: `loops/GK17-ontology-unified-map/evidence/security_check-20260915T002735Z.log`
- SHA256: `fba32adf851b49bd00fbff4b929e583694674bc98f068c0400894fd122e35537`

## Attempt 2｜20260915T002736Z

- Gate: `backend_test`
- Command: `make backend-test`
- Exit: `0`
- Evidence: `loops/GK17-ontology-unified-map/evidence/backend_test-20260915T002736Z.log`
- SHA256: `f353ce4f1ab046f0df7a063a8a79ada4cf036c813598db31f5f1b5ea5153da0d`
