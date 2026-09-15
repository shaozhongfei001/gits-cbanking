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

## Attempt 1｜20260915T013349Z

- Gate: `ref_anchor_check`
- Command: `python3 scripts/gk17_ref_anchor_check.py --selftest`
- Exit: `0`
- Evidence: `loops/GK17-ontology-unified-map/evidence/ref_anchor_check-20260915T013349Z.log`
- SHA256: `041c9e73337046097c92516f2bd79f4257d25f88b898b76c76dfb1363f51c82a`

## Attempt 1｜20260915T013349Z

- Gate: `gk17_prodcard_projection`
- Command: `python3 scripts/gk17_prodcard_to_rdf.py --root . --cards-dir /home/szf/dev/Leibniz-KERT/examples/product-recommendation-assets/03_core --allow-unresolved --verify-determinism`
- Exit: `0`
- Evidence: `loops/GK17-ontology-unified-map/evidence/gk17_prodcard_projection-20260915T013349Z.log`
- SHA256: `f0a74a62e1979e5fd5f67abb3e07730ec3fe0c9eafca0b1a25fa7c6f01ca690e`

## Attempt 1｜20260915T013349Z

- Gate: `triple_consistency_check`
- Command: `python3 scripts/gk17_triple_consistency_check.py`
- Exit: `1`
- Evidence: `loops/GK17-ontology-unified-map/evidence/triple_consistency_check-20260915T013349Z.log`
- SHA256: `ddfdf4da2f249b462957810ba2a62c3190e1c9058c634c11d1c7c74d204eadaf`

## Attempt 3｜20260915T013451Z

- Gate: `contract_generate`
- Command: `make generate`
- Exit: `0`
- Evidence: `loops/GK17-ontology-unified-map/evidence/contract_generate-20260915T013451Z.log`
- SHA256: `048ab7c55cfbb3c6707b7212288bd84d678861d4abb19a7eca16fbb7a71803b8`

## Attempt 3｜20260915T013451Z

- Gate: `contract_check`
- Command: `make check`
- Exit: `0`
- Evidence: `loops/GK17-ontology-unified-map/evidence/contract_check-20260915T013451Z.log`
- SHA256: `0e4db17e674d23fd938f5844527af42dee3a77cea000144e5514cae6e0303b0f`

## Attempt 2｜20260915T013455Z

- Gate: `ref_anchor_check`
- Command: `python3 scripts/gk17_ref_anchor_check.py --selftest`
- Exit: `0`
- Evidence: `loops/GK17-ontology-unified-map/evidence/ref_anchor_check-20260915T013455Z.log`
- SHA256: `041c9e73337046097c92516f2bd79f4257d25f88b898b76c76dfb1363f51c82a`

## Attempt 2｜20260915T034031Z

- Gate: `triple_consistency_check`
- Command: `python3 scripts/gk17_triple_consistency_check.py`
- Exit: `0`
- Evidence: `loops/GK17-ontology-unified-map/evidence/triple_consistency_check-20260915T034031Z.log`
- SHA256: `e268c604a93f6105b55848bd4147457813891e58af0af83326b50e22181c8883`

## Attempt 1｜20260915T034816Z

- Gate: `gk17_mutation_regression`
- Command: `python3 scripts/gate_injection_tests.py`
- Exit: `0`
- Evidence: `loops/GK17-ontology-unified-map/evidence/gk17_mutation_regression-20260915T034816Z.log`
- SHA256: `2c7aca10f5f0ea98f14e305a7917b485ed322f9416eaf8b4e37e80a65105a3e8`

## Attempt 3｜20260915T034817Z

- Gate: `gk_ke_gates`
- Command: `python3 scripts/run_gates.py`
- Exit: `0`
- Evidence: `loops/GK17-ontology-unified-map/evidence/gk_ke_gates-20260915T034817Z.log`
- SHA256: `dfabc49eaddff42dea799cd3fdc6d6f883792ea84030ce8e2ea3c571154eb623`

## Attempt 4｜20260915T034821Z

- Gate: `contract_check`
- Command: `make check`
- Exit: `0`
- Evidence: `loops/GK17-ontology-unified-map/evidence/contract_check-20260915T034821Z.log`
- SHA256: `49e894f2afaeb7cfabc66fa59db7b7436dcf26c58d6ead01a2cac1166a287cf1`
