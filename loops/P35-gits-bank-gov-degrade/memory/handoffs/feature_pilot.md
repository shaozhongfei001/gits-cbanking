# Handoff｜P35-gits-bank-gov-degrade｜feature_pilot

**Time**: `2026-08-25T17:18:30Z`  
**Role**: `feature_pilot`  
**Baton**: handed to `independent_qa`

## Result

四门 implementation gates 均 `pass`。Loop 为 `ready_for_independent_qa`。仅 `DEV_SELF_CHECK_PASS`。未写 `QA_PASS`。未 commit / push / `git add .`。`qa_actor` 保持 `null`。未改 specs 权威源，未手改 generated。未改 `/commitments` path 或 pageId=P36。未实现 F02/F03 新建机或授信/定价可回写状态机。未引用 NEED-826 作为对象。

## Files changed (this actor)

- `frontend/src/router/index.ts` — P31 `/collab`、P32 `/approvals`、P33 `/delivery`、P34 `/account-plans`、P35 `/value`、P37 `/claims`、P40 `/degrade`；P38 `/knowledge-map` 与 P39 `/audit-trace` 补 pageId；P36 `/commitments` 未改
- `frontend/src/router/__tests__/routes.spec.ts`
- `frontend/src/layouts/navConfig.ts` — 启用「审批工作中心」「Claim / Evidence 中心」；C2 治理页可深链
- `frontend/src/components/shell/__tests__/AppSidebar.spec.ts`
- `frontend/src/composables/govDegrade.ts` 与 `__tests__/govDegrade.spec.ts`
- `frontend/src/components/shell/GovDegradeShell.vue`
- `frontend/src/views/CollabView.vue` — P31
- `frontend/src/views/ApprovalsView.vue` — P32 C0
- `frontend/src/views/DeliveryCenterView.vue` — P33
- `frontend/src/views/AccountPlansView.vue` — P34
- `frontend/src/views/ValueRealizationView.vue` — P35
- `frontend/src/views/ClaimsView.vue` — P37 C0
- `frontend/src/views/KnowledgeMapView.vue` — P38 升级
- `frontend/src/views/AuditTraceView.vue` — P39 升级
- `frontend/src/views/DegradeRecoveryView.vue` — P40
- 对应 `frontend/src/views/__tests__/*.spec.ts`
- `loops/P35-gits-bank-gov-degrade/*` evidence / state / memory

## Not changed

- `specs/` 权威源（本 actor 未改）
- `generated/`（无手改）
- `.github/workflows/ci.yml`
- `/commitments` path / pageId=P36 / CommitmentDashboard 重做
- 专家协同 / DeliveryPackage / AccountPlan / 价值口径 OpenAPI
- F02/F03 新建作业流
- P41–P44
- `QA_PASS` / `qa_attest`

## Evidence

See `loops/P35-gits-bank-gov-degrade/EVIDENCE.json` and `evidence/*.log`。
