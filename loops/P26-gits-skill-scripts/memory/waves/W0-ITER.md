# W0｜Iteration log（append-only）

由 `scripts/record_gate.py` 追加实际attempt、命令、退出码、证据hash和下一动作。没有实际执行不得登记PASS。

## Attempt 1｜20260822T113518Z

- Gate: `unit_scripts`
- Command: `./mvnw -pl apps/api -am -Dsurefire.failIfNoSpecifiedTests=false -Dtest=OutreachScriptServiceTest,MeetingScriptServiceTest,FallbackSkillExecutionAdapterTest test`
- Exit: `0`
- Evidence: `loops/P26-gits-skill-scripts/evidence/unit_scripts-20260822T113518Z.log`
- SHA256: `89c92d76561776209e4c336469b946c5da16638e96dda74c07af7bfb5ddcd898`

## Attempt 1｜20260822T113530Z

- Gate: `security_check`
- Command: `make security-check`
- Exit: `0`
- Evidence: `loops/P26-gits-skill-scripts/evidence/security_check-20260822T113530Z.log`
- SHA256: `2a73064a1dd51cbd66e4bca7751b12e762914cf8871a3d077d3897dd2b74ba9a`

## Attempt 1｜20260822T1137Z

- Gate: `e2e_it_scripts` (not in LOOP.yaml; E2E Owner stale-AT repair)
- Command: `./mvnw -pl apps/api -am -Dsurefire.failIfNoSpecifiedTests=false -Dtest=EngagementScenarioE2eIT,OutreachScriptServiceTest,MeetingScriptServiceTest test`
- Exit: `0` (Feature Pilot post-fix; E2E Owner re-verified assertions)
- Note: AT-007/008 identity-only; empty talkingPoints / kycQuestions OK when Skill down
