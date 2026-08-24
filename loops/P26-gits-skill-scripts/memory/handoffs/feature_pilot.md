# Handoff｜P26-gits-skill-scripts｜feature_pilot

**Time**: `2026-08-22T11:40:00Z`
**Role**: `feature_pilot`
**Baton**: handed to `independent_qa`

## Implementation

GITS H2 remains CRM identity only. Outreach/meeting on 一键访前 call DKWS Skill with `customerId` only (outreach may add `channel`). No KYC/products/profile packing, no local LLM fill.

1. `OutreachScriptService` — `SkillExecutionPort` + `findCustomer`; skillId `skill-customer-outreach-script`; empty persist on Skill down
2. `MeetingScriptService` — same pattern, skillId `skill-customer-meeting-script`, request only `customerId`
3. `EngagementConfig` beans drop `LlmClient` for those two services
4. `FallbackSkillExecutionAdapter` NO_LOCAL_FILL includes both skill ids
5. Frontend: empty objective/openingLine/agenda → 「DKWS 未返回该话术」
6. `PrevisitPreparationService` still throws on customer-not-found; empty Skill result does not throw

## Gates

- `unit_scripts`: Tests run: 15, Failures: 0
- `security_check`: PASS (advisory findings only)

## 未交

- `QA_PASS` / independent QA
- OpenAPI / `generated/` (must not change)
- Did not touch `loops/P24-dkws-platform` or P25 IQA baton
- No commit
