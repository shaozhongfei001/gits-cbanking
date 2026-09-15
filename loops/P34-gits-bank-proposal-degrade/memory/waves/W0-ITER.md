# W0｜Iteration log（append-only）

由 `scripts/record_gate.py` 追加实际attempt、命令、退出码、证据hash和下一动作。没有实际执行不得登记PASS。

## Attempt 1｜20260825T165810Z

- Gate: `contract_generate`
- Command: `make generate`
- Exit: `0`
- Evidence: `loops/P34-gits-bank-proposal-degrade/evidence/contract_generate-20260825T165810Z.log`
- SHA256: `048ab7c55cfbb3c6707b7212288bd84d678861d4abb19a7eca16fbb7a71803b8`

## Attempt 1｜20260825T165812Z

- Gate: `contract_check`
- Command: `make check`
- Exit: `0`
- Evidence: `loops/P34-gits-bank-proposal-degrade/evidence/contract_check-20260825T165812Z.log`
- SHA256: `44f27f0067edd08e854f5344f7c8179dc2f54b4ab378dffe7bb837b1efffec68`

## Attempt 1｜20260825T165814Z

- Gate: `security_check`
- Command: `make security-check`
- Exit: `0`
- Evidence: `loops/P34-gits-bank-proposal-degrade/evidence/security_check-20260825T165814Z.log`
- SHA256: `93401ff002dd340d12b6dd36f9c2625d80badd76f0a95040ef1271c900654ac1`

## Attempt 1｜20260825T165818Z

- Gate: `frontend_proposal_degrade`
- Command: `cd frontend && npm ci && npm run check && npm run test && npm run build`
- Exit: `0`
- Evidence: `loops/P34-gits-bank-proposal-degrade/evidence/frontend_proposal_degrade-20260825T165818Z.log`
- SHA256: `ef17d9d1f1177d8b2d404fc25ee9c96c26dc5b91c2e51eb0ff7a913b33c9c4f8`
