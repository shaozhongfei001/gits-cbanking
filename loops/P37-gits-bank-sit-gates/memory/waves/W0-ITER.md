# W0｜Iteration log（append-only）

由 `scripts/record_gate.py` 追加实际attempt、命令、退出码、证据hash和下一动作。没有实际执行不得登记PASS。

## Attempt 1｜20260825T174726Z

- Gate: `contract_generate`
- Command: `make generate`
- Exit: `0`
- Evidence: `loops/P37-gits-bank-sit-gates/evidence/contract_generate-20260825T174726Z.log`
- SHA256: `048ab7c55cfbb3c6707b7212288bd84d678861d4abb19a7eca16fbb7a71803b8`

## Attempt 1｜20260825T174729Z

- Gate: `contract_check`
- Command: `make check`
- Exit: `0`
- Evidence: `loops/P37-gits-bank-sit-gates/evidence/contract_check-20260825T174729Z.log`
- SHA256: `11fe4de0f4b8093cecbea794f4df21488ece06b1ab8d3d7cc962ee611b1175ed`

## Attempt 1｜20260825T174732Z

- Gate: `security_check`
- Command: `make security-check`
- Exit: `0`
- Evidence: `loops/P37-gits-bank-sit-gates/evidence/security_check-20260825T174732Z.log`
- SHA256: `1c2e54ff47942adeb3070579d07769971cc013a065391befe99d643485d14736`

## Attempt 1｜20260825T174738Z

- Gate: `sit_applicable`
- Command: `cd frontend && npm ci && npm run check && npm run test && npm run e2e`
- Exit: `0`
- Evidence: `loops/P37-gits-bank-sit-gates/evidence/sit_applicable-20260825T174738Z.log`
- SHA256: `a4c23e2c6fbb572804b4b4f4a79887b9e2d8e9739d4629cd95b7cd4dd292aa94`
