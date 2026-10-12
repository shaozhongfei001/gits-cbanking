# W0｜Iteration log（append-only）

由 `scripts/record_gate.py` 追加实际attempt、命令、退出码、证据hash和下一动作。没有实际执行不得登记PASS。

## Attempt 1｜20260910T141716Z

- Gate: `contract_generate`
- Command: `make generate`
- Exit: `0`
- Evidence: `loops/GK0-contract-activation/evidence/contract_generate-20260910T141716Z.log`
- SHA256: `048ab7c55cfbb3c6707b7212288bd84d678861d4abb19a7eca16fbb7a71803b8`

## Attempt 1｜20260910T141717Z

- Gate: `contract_check`
- Command: `make check`
- Exit: `0`
- Evidence: `loops/GK0-contract-activation/evidence/contract_check-20260910T141717Z.log`
- SHA256: `78efc1498b1926210e18a129b0c7ba9c5ff07a5b2e12d152223b5ce7f2ee891a`

## Attempt 1｜20260910T141718Z

- Gate: `security_check`
- Command: `make security-check`
- Exit: `0`
- Evidence: `loops/GK0-contract-activation/evidence/security_check-20260910T141718Z.log`
- SHA256: `c98ab45add56ff03cca313b0d4161d89b5b20f2ef5e19cc83780a1b8d3dae780`

## Attempt 1｜20260910T141929Z

- Gate: `gk_ke_examples`
- Command: `python3 scripts/gk_ke_contract_examples.py`
- Exit: `0`
- Evidence: `loops/GK0-contract-activation/evidence/gk_ke_examples-20260910T141929Z.log`
- SHA256: `8053fbe7774144a6bb4201ddfa1c87c8c143af0144c02744f27ec01d093c8634`

## Attempt 1｜20260910T141936Z

- Gate: `gk_ke_hash`
- Command: `./mvnw -pl modules/knowledge-architecture test -Dtest=CanonicalHashGoldenTest`
- Exit: `0`
- Evidence: `loops/GK0-contract-activation/evidence/gk_ke_hash-20260910T141936Z.log`
- SHA256: `e89476dac407a04280471981ec47a4c2ecef2daebecaa98494412129e4245232`
