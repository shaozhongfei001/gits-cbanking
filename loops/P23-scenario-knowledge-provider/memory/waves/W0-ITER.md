# W0｜Iteration log（append-only）

由 `scripts/record_gate.py` 追加实际attempt、命令、退出码、证据hash和下一动作。没有实际执行不得登记PASS。

## Attempt 1｜20260821T095949Z

- Gate: `backend_test`
- Command: `make backend-test`
- Exit: `0`
- Evidence: `loops/P23-scenario-knowledge-provider/evidence/backend_test-20260821T095949Z.log`
- SHA256: `d5356d949dec503d5e676afdf0856ea4a23fb529dbb4f3c4379ad9a94974e365`

## Attempt 1｜20260821T102328Z

- Gate: `evidence_check`
- Command: `make evidence-check LOOP=P23-scenario-knowledge-provider`
- Exit: `0`
- Evidence: `loops/P23-scenario-knowledge-provider/evidence/evidence_check-20260821T102328Z.log`
- SHA256: `3cc2470900616c4c7d6c693dd3493aa5d5034f2c4aec5a3c3e126ac1ffba8674`
