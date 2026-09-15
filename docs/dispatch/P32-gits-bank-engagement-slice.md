# P32 Dispatch｜GITS Bank P11–P19 持续经营 C0/C2 切片

```text
DISPATCH_ID=P32-GITS-BANK-ENGAGEMENT-SLICE
STATUS=QA_PASS
OWNER_DECISION=OD-GITS-BANK-UX-2026-08-25
BASE_COMMIT=d3142c9557aaa197c41ef89343ec1e05b073d0a0
WORKING_BRANCH=feature/P30-gits-bank-experience-shell
LOOP=loops/P32-gits-bank-engagement-slice
DEPENDS_ON=P31-gits-bank-customer-slice
IMPLEMENTATION_ACTOR=feature_pilot
CONTRACT_CHANGE=NOT_AUTHORIZED
AUTHORITY_SOURCE_CHANGE=NO
PAGES=P11,P12,P13,P14,P15,P16,P17,P18,P19
PRODUCTION_READY=NO
FROZEN=NO
QA_ACTOR=MUST_BE_INDEPENDENT
```

## 启动条件

仅当 `P31-gits-bank-customer-slice` 的 `STATE.status=qa_pass` 后，Tech Lead 才可将本 Loop 置 `in_progress` 并派 Feature Pilot。

## 目标

在 Experience Shell 内交付 V3.2 页面 P11–P19：复用既有 journey / previsit / postvisit / CRM writeback 合同。缺对象则 C2 禁用，不造伪正式对象。

| 页 | 名称 | C | 路由候选 | 既有合同消费 |
|---|---|---|---|---|
| P11 | 互动记录·访前路径 | C0/C1 | `/engagement` 升级壳层；或 `/journeys/:id` | 既有 EngagementWorkspace / journey 查询 |
| P12 | 访前目标与信息缺口 | C0 | `/engagement/previsit/gaps` 或工作台页签 | `fetchKycGapProfile` / preparePrevisit 只读预览 |
| P13 | 访前知识证据装配 | C0 | `/engagement/previsit/evidence` | preparePrevisit / 既有知识查询；无来源则空态 |
| P14 | 访前包预览 | C0 | `/engagement/previsit/pack` | executePrevisit **仅在已有合同且人工确认**；否则只读预览 + 禁用 |
| P15 | 互动记录·会中工作区 | C1 | `/in-meeting/:id?` | 升级 InMeetingAssistant 壳层 |
| P16 | 会中实时捕获 | C1 | `/in-meeting/:id/capture` | UI 草稿；转写失败切手工；禁止当正式 Claim |
| P17 | 离场确认 | C2 | `/in-meeting/:id/checkout` | 清单只读/草稿；「结束会谈」无合同则禁用 |
| P18 | 访后事实对账 | C0 | `/engagement/postvisit` | `executePostvisit` 既有合同；冲突保留双方版本 |
| P19 | CRM 受控回写 | C0 | `/engagement/crm-writeback` | `frontend/src/api/v11.ts` writeback-commands GET/decide |

保留 `/engagement`、`/in-meeting`、`/journeys/:id`、`/engagements`（P10）深链。

## 禁止

- 改 `specs/` 权威源或手改 `generated/`
- Need / G0–G5 / 账户计划正式对象
- 会中草稿直接写成正式 Claim/Evidence 而不走既有 HumanGate
- 前端硬编码审批、授信、定价、F/C/B/H/P/A
- 开发自签 `QA_PASS`
- 移动离线写回（P41–P44）

## Feature Pilot 派工

```text
LOOP_ID=P32-gits-bank-engagement-slice
TASK_ID=WP-UX-ENG
PAGE_IDS=P11,P12,P13,P14,P15,P16,P17,P18,P19
REQUIREMENT_IDS=UX-FR-11-* … UX-FR-19-*
BUSINESS_OBJECTS=Journey/Previsit/Postvisit C0; In-meeting C1 draft; CRM writeback C0
CURRENT_ROUTE=/engagement ; /in-meeting ; /journeys/:id
CONTRACT_IDS_OR_C1_C2=CTR-API-001 journey/previsit/postvisit; CTR-V11 CRM writeback; missing checkout C2
FORBIDDEN_FIELDS_OR_ACTIONS=Need formal; G0-G5; new OpenAPI fields; unsigned CRM write; meeting draft as formal Claim
TEST_IDS=TC-P11-* … TC-P19-* (remain PLANNED until executed with evidence)
EXIT_CRITERIA=LOOP.yaml gates green via record_gate.py; old routes still open; no specs diff
EVIDENCE_REQUIRED=loops/P32-gits-bank-engagement-slice/evidence/
ROLLBACK=revert branch; no data migration
```
