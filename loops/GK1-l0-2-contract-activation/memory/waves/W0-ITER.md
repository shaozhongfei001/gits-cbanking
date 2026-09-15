# W0｜Iteration log（append-only）

由 `scripts/record_gate.py` 追加实际attempt、命令、退出码、证据hash和下一动作。没有实际执行不得登记PASS。

## Attempt 1｜20260911T164830Z

- Gate: `contract_generate`
- Command: `make generate`
- Exit: `0`
- Evidence: `loops/GK1-l0-2-contract-activation/evidence/contract_generate-20260911T164830Z.log`
- SHA256: `048ab7c55cfbb3c6707b7212288bd84d678861d4abb19a7eca16fbb7a71803b8`

## Attempt 1｜20260911T164831Z

- Gate: `contract_check`
- Command: `make check`
- Exit: `0`
- Evidence: `loops/GK1-l0-2-contract-activation/evidence/contract_check-20260911T164831Z.log`
- SHA256: `6a2b036a8be4c13c0c0dba995bd28bd8cef0480037434d849728a88be57c9f01`

## Attempt 1｜20260911T164832Z

- Gate: `security_check`
- Command: `make security-check`
- Exit: `0`
- Evidence: `loops/GK1-l0-2-contract-activation/evidence/security_check-20260911T164832Z.log`
- SHA256: `21cfa108e57447010ca054f429ccb7c82d18658e62ae47698df21109186f63cf`

## Attempt 1｜20260911T164833Z

- Gate: `gk_ke_examples`
- Command: `python3 scripts/gk_ke_contract_examples.py`
- Exit: `0`
- Evidence: `loops/GK1-l0-2-contract-activation/evidence/gk_ke_examples-20260911T164833Z.log`
- SHA256: `9d05754cdb4fde8a5b7d9ff2a7109d10dcadfb49312d69741d24ab1eb2324d0e`

## Attempt 1｜20260911T164833Z

- Gate: `gk_ke_openapi_lint`
- Command: `python3 scripts/gk_ke_openapi_contract_tests.py`
- Exit: `0`
- Evidence: `loops/GK1-l0-2-contract-activation/evidence/gk_ke_openapi_lint-20260911T164833Z.log`
- SHA256: `237156c1be19e35854dd88438c5d24cf462b9e342c967bbe1a8666ee9246bf1a`

## Attempt 1｜20260911T164833Z

- Gate: `gk_ke_hash`
- Command: `./mvnw -pl modules/knowledge-architecture test -Dtest=CanonicalHashGoldenTest`
- Exit: `0`
- Evidence: `loops/GK1-l0-2-contract-activation/evidence/gk_ke_hash-20260911T164833Z.log`
- SHA256: `77c8574b3b39cd45241f496737da50a7e62f064e6d7a41bc1a548cc844415b3d`
