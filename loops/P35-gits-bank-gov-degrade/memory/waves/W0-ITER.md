# W0｜Iteration log（append-only）

由 `scripts/record_gate.py` 追加实际attempt、命令、退出码、证据hash和下一动作。没有实际执行不得登记PASS。

## Attempt 1｜20260825T171315Z

- Gate: `contract_generate`
- Command: `make generate`
- Exit: `0`
- Evidence: `loops/P35-gits-bank-gov-degrade/evidence/contract_generate-20260825T171315Z.log`
- SHA256: `048ab7c55cfbb3c6707b7212288bd84d678861d4abb19a7eca16fbb7a71803b8`

## Attempt 1｜20260825T171325Z

- Gate: `contract_check`
- Command: `make check`
- Exit: `0`
- Evidence: `loops/P35-gits-bank-gov-degrade/evidence/contract_check-20260825T171325Z.log`
- SHA256: `44f27f0067edd08e854f5344f7c8179dc2f54b4ab378dffe7bb837b1efffec68`

## Attempt 1｜20260825T171340Z

- Gate: `security_check`
- Command: `make security-check`
- Exit: `0`
- Evidence: `loops/P35-gits-bank-gov-degrade/evidence/security_check-20260825T171340Z.log`
- SHA256: `93401ff002dd340d12b6dd36f9c2625d80badd76f0a95040ef1271c900654ac1`

## Attempt 1｜20260825T171735Z

- Gate: `frontend_gov_degrade`
- Command: `cd frontend && npm ci && npm run check && npm run test && npm run build`
- Exit: `0`
- Evidence: `loops/P35-gits-bank-gov-degrade/evidence/frontend_gov_degrade-20260825T171735Z.log`
- SHA256: `396fb8e81fcc0a5a4d5c6e070074833fb8ec7c66d324fb7202c6f5305f0cd86d`
