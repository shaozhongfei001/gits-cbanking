# W0｜Iteration log（append-only）

由 `scripts/record_gate.py` 追加实际attempt、命令、退出码、证据hash和下一动作。没有实际执行不得登记PASS。

## Attempt 1｜20260825T160030Z

- Gate: `contract_generate`
- Command: `make generate`
- Exit: `0`
- Evidence: `loops/P31-gits-bank-customer-slice/evidence/contract_generate-20260825T160030Z.log`
- SHA256: `048ab7c55cfbb3c6707b7212288bd84d678861d4abb19a7eca16fbb7a71803b8`

## Attempt 1｜20260825T160035Z

- Gate: `contract_check`
- Command: `make check`
- Exit: `0`
- Evidence: `loops/P31-gits-bank-customer-slice/evidence/contract_check-20260825T160035Z.log`
- SHA256: `44f27f0067edd08e854f5344f7c8179dc2f54b4ab378dffe7bb837b1efffec68`

## Attempt 1｜20260825T160038Z

- Gate: `security_check`
- Command: `make security-check`
- Exit: `0`
- Evidence: `loops/P31-gits-bank-customer-slice/evidence/security_check-20260825T160038Z.log`
- SHA256: `80830031fc6e290a32c61433b1633618e6f6334db4a87f108ca36621b6b86c72`

## Attempt 1｜20260825T160622Z

- Gate: `frontend_customer_slice`
- Command: `cd frontend && npm ci && npm run check && npm run test && npm run build`
- Exit: `0`
- Evidence: `loops/P31-gits-bank-customer-slice/evidence/frontend_customer_slice-20260825T160622Z.log`
- SHA256: `24dd43361ea1d9c579a121526178707f58176a858a913cdbe729f870e9788af5`
