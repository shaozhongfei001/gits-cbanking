# P26-gits-skill-scripts｜Failures（append-only）

失败必须在修改实现之前由 `scripts/record_gate.py`追加。每项至少包含时间、Gate、命令、退出码、证据文件、初步分类和下一动作；修复后追加根因、变更SHA与原命令重跑结果，不覆盖原记录。

## 2026-08-22T11:36Z — E2E Owner

- Gate: e2e_it_scripts (pre-fix record)
- Command: inspect `EngagementScenarioE2eIT.outreachScriptGeneration` / `meetingScriptGeneration`
- Exit: expected FAIL when DSH unset (Fallback NO_LOCAL_FILL → empty script)
- Class: stale_acceptance — AT-007/008 still require talkingPoints / kycQuestions from GITS seed
- Next: Feature Pilot update AT-007/008 to identity-only: scriptId + customerId; empty lists OK; openingLine must not be seed-fabricated

## 2026-08-22T11:37Z — Feature Pilot (post-fix rerun)

- Gate: e2e_it_scripts (rerun after AT-007/008 identity-only)
- Command: `./mvnw -pl apps/api -am -Dsurefire.failIfNoSpecifiedTests=false -Dtest=EngagementScenarioE2eIT,OutreachScriptServiceTest,MeetingScriptServiceTest test`
- Exit: 0
- Result: BUILD SUCCESS — Tests run: 24, Failures: 0, Errors: 0, Skipped: 0
  - `EngagementScenarioE2eIT`: 14/0/0 (AT-007/008 empty talkingPoints / kycQuestions OK when Fallback NO_LOCAL_FILL)
  - `OutreachScriptServiceTest`: 5/0/0
  - `MeetingScriptServiceTest`: 5/0/0
- Root cause: stale E2E assertions required non-empty seed/LLM talkingPoints and KYC questions
- Change: `apps/api/src/test/java/com/gien/gits/api/e2e/EngagementScenarioE2eIT.java` AT-007/008 identity-only (scriptId + customerId + channel; lists/lines may be empty)
- SHA: uncommitted (no commit per dispatch)
- Next: independent QA may re-inspect; Feature Pilot did not write QA_PASS

## 2026-08-22T11:40Z — E2E Owner (re-verify)

- Gate: e2e_it_scripts
- Inspect: AT-007/008 now identity-only (`scriptId`, `customerId`, channel); lists/lines `assertNotNull` only — empty talkingPoints / kycQuestions allowed
- Feature Pilot rerun already exit 0 (24 tests). E2E Owner did not patch production code to pass tests.
- Class: closed — stale_acceptance fixed in IT, not in implementation
- Next: baton remains `independent_qa`. Do not write QA_PASS from E2E Owner or Feature Pilot.

