# P26 Tech Lead delivery plan

Role: tech_lead
P25 remains with independent_qa. Do not touch P24.

## Principle

Same as P25: GITS CRM is identity only. Outreach/meeting on 一键访前 must not paint H2 KYC/products. DKWS Skill fetches knowledge by customerId.

## Contract (docs/dd v1.3, §3 updated this wave)

- `skill-customer-outreach-script` request: `customerId` + optional `channel`
- `skill-customer-meeting-script` request: `customerId` only
- Do not send structuredFacts / knowledgeContext
- GITS OpenAPI outreach/meeting **response shapes unchanged** — map Skill `data` into existing records

## Mapping (do not invent OpenAPI fields)

Outreach `data` → `OutreachScript`:
- objective ← join `callObjectives` or `scriptTitle`
- openingLine ← first `keyMessages` or first `sections[].content`
- talkingPoints ← `sections` as topic=heading, detail=content, suggestedQuestion="", priority=index
- riskReminders / closingLine / followUpAction ← empty unless an obvious matching section heading exists (风险/收口/后续)
- still require CRM customer exists (findCustomer); do not use industry/KYC for text

Meeting `data` → `MeetingScript`:
- meetingObjective ← first talkingPoint.title or first agenda.topic
- previsitSummary ← empty (R1 is separate)
- agendaItems ← `agenda` (topic, durationMinutes=0, keyPoints=time, expectedOutcome="")
- kycQuestions / productDiscussions ← empty unless heading clearly matches
- riskPoints ← `sensitivePoints`
- closingSummary ← join `actionItems`

On Skill error / exception / empty data: persist empty script (valid ids + empty lists), do not call LlmClient, do not template from seed.

## Fallback

Add `skill-customer-outreach-script` and `skill-customer-meeting-script` to FallbackSkillExecutionAdapter NO_LOCAL_FILL.

## Frontend

If objective/openingLine/agenda empty, show “DKWS 未返回该话术” — do not keep showing seed-flavored mock text.

## Tests

Rewrite Outreach/Meeting tests: capture SkillExecutionCommand.request has customerId, no structuredFacts/knowledgeContext; down → empty not 华东精工 template.
