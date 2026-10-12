# W0｜Iteration log（append-only）

由 `scripts/record_gate.py` 追加实际attempt、命令、退出码、证据hash和下一动作。没有实际执行不得登记PASS。

## Attempt 1｜20260825T153616Z

- Gate: `ci_contract_index_wired`
- Command: `python3 scripts/check_ci_contract_index_wired.py`
- Exit: `0`
- Evidence: `loops/P30-gits-bank-experience-shell/evidence/ci_contract_index_wired-20260825T153616Z.log`
- SHA256: `f27585dbce9043e3a4993b79b355d79b43abaec6d2ba4e7174374d72ffde33ac`

## Attempt 1｜20260825T153645Z

- Gate: `contract_generate`
- Command: `make generate`
- Exit: `0`
- Evidence: `loops/P30-gits-bank-experience-shell/evidence/contract_generate-20260825T153645Z.log`
- SHA256: `048ab7c55cfbb3c6707b7212288bd84d678861d4abb19a7eca16fbb7a71803b8`

## Attempt 1｜20260825T153717Z

- Gate: `contract_check`
- Command: `make check`
- Exit: `2`
- Evidence: `loops/P30-gits-bank-experience-shell/evidence/contract_check-20260825T153717Z.log`
- SHA256: `b065bf1c1225950a4bfc2b99621b2c1a05a520ee22117d98776d27b01c3afce1`

## Attempt 2｜20260825T153827Z

- Gate: `contract_check`
- Command: `make check`
- Exit: `0`
- Evidence: `loops/P30-gits-bank-experience-shell/evidence/contract_check-20260825T153827Z.log`
- SHA256: `0a9da677b7a3943b8860a78e776b733929e475f1c2161207198a573a9f916e3b`

## Attempt 1｜20260825T153836Z

- Gate: `contract_index_nonzero`
- Command: `python3 scripts/check_contract_index_refs.py`
- Exit: `0`
- Evidence: `loops/P30-gits-bank-experience-shell/evidence/contract_index_nonzero-20260825T153836Z.log`
- SHA256: `c5721190c11638e61316cbb603a5941e4ec52eee52807d6d04ca181daea22e12`

## Attempt 1｜20260825T153836Z

- Gate: `security_check`
- Command: `make security-check`
- Exit: `0`
- Evidence: `loops/P30-gits-bank-experience-shell/evidence/security_check-20260825T153836Z.log`
- SHA256: `c1c91d3f68461c22dd41b04a47990778fb6546e431f00d6617bc18e930ce6eb7`

## Attempt 1｜20260825T153925Z

- Gate: `frontend_shell`
- Command: `cd frontend && npm ci && npm run check && npm run test && npm run build`
- Exit: `1`
- Evidence: `loops/P30-gits-bank-experience-shell/evidence/frontend_shell-20260825T153925Z.log`
- SHA256: `99efc4ea4d7767f5cf0baec8a1393c3a0a9fbd47b6df7ef7c84f5a3b02db7a5d`

## Attempt 2｜20260825T154108Z

- Gate: `frontend_shell`
- Command: `cd frontend && npm ci && npm run check && npm run test && npm run build`
- Exit: `0`
- Evidence: `loops/P30-gits-bank-experience-shell/evidence/frontend_shell-20260825T154108Z.log`
- SHA256: `75e7a5fb5345b407357f249a3b8ffea0233a4294084bfa09042dbd7597a24060`

## Attempt 3｜20260825T154531Z

- Gate: `frontend_shell`
- Command: `cd frontend && npm ci && npm run check && npm run test && npm run build`
- Exit: `0`
- Evidence: `loops/P30-gits-bank-experience-shell/evidence/frontend_shell-20260825T154531Z.log`
- SHA256: `6e602536e29d3019ae190370d4873a5da99ea6b97d070e3b8e44ba2c5cb112b3`
