# W0｜Iteration log（append-only）

由 `scripts/record_gate.py` 追加实际attempt、命令、退出码、证据hash和下一动作。没有实际执行不得登记PASS。

## Attempt 1｜20260822T124022Z

- Gate: `unit_r2`
- Command: `./mvnw -pl apps/api -am -Dsurefire.failIfNoSpecifiedTests=false -Dtest=QuickBattleCardFromSkillTest,KnowledgeDrivenPrevisitReportGeneratorTest test`
- Exit: `0`
- Evidence: `loops/P27-gits-r2-skill/evidence/unit_r2-20260822T124022Z.log`
- SHA256: `7dc2766089dd3283794bfb5be90de123594a4325d5a6f3ae9a3acc48f97e2d1c`

## Attempt 1｜20260822T124035Z

- Gate: `security_check`
- Command: `make security-check`
- Exit: `0`
- Evidence: `loops/P27-gits-r2-skill/evidence/security_check-20260822T124035Z.log`
- SHA256: `2a73064a1dd51cbd66e4bca7751b12e762914cf8871a3d077d3897dd2b74ba9a`

## Feature Pilot close-out｜2026-08-22T12:42:00Z

- `unit_r2` and `security_check` both exit 0 via `scripts/record_gate.py`
- Extra (not a loop gate): `EngagementScenarioE2eIT` Tests run: 14, Failures: 0
- Next: Baton → `independent_qa`. Do not write `QA_PASS`.
