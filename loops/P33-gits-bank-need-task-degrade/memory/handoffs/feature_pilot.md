# Handoff｜P33-gits-bank-need-task-degrade｜feature_pilot

**Time**: `2026-08-25T16:43:00Z`  
**Role**: `feature_pilot`  
**Baton**: handed to `independent_qa`

## Result

四门 implementation gates 均 `pass`。Loop 为 `ready_for_independent_qa`。仅 `DEV_SELF_CHECK_PASS`。未写 `QA_PASS`。未 commit / push / `git add .`。`qa_actor` 保持 `null`。未改 specs 权威源，未手改 generated。未发明 Need / ServicePlan schema 或 POST /needs。

## Files changed (this actor)

- `frontend/src/router/index.ts` — P20 `/needs`、P21 `/needs/:id`、P22 `/needs/:id/plan`；P36 保留 `/commitments` 深链并补 pageId
- `frontend/src/router/__tests__/routes.spec.ts`
- `frontend/src/layouts/navConfig.ts` — 「方案与交付」新增「需求/机会（降级）」；「服务建议书」保持禁用；日常作业「任务与承诺」仍指向 `/commitments`
- `frontend/src/components/shell/AppSidebar.vue`
- `frontend/src/components/shell/__tests__/AppSidebar.spec.ts`
- `frontend/src/api/engagement.ts` — `listClaims`（既有 OpenAPI GET /engagement/claims）；`fetchCustomerContext.claims` 只读组合；无 Need schema
- `frontend/src/composables/needApprox.ts` — C1 近似行，主键 signalId / claimId
- `frontend/src/views/NeedsView.vue` — P20 C2
- `frontend/src/views/NeedRecordView.vue` — P21 C2
- `frontend/src/views/NeedPlanView.vue` — P22 C2
- `frontend/src/views/CommitmentDashboard.vue` — P36 C0 ObjectHeader/PageState，消费 `fetchCommitments` / `fetchTasks`，保留 createCommitment
- 对应 `frontend/src/views/__tests__/*.spec.ts` 与 `frontend/src/composables/__tests__/needApprox.spec.ts`
- `loops/P33-gits-bank-need-task-degrade/*` evidence / state / memory

## Not changed

- `specs/` 权威源（本 actor 未改）
- `generated/`（无手改）
- `.github/workflows/ci.yml`
- Need / ServicePlan 正式对象、NEED-826、建议书阶段可回写枚举
- P23–P44
- `QA_PASS` / `qa_attest`

## Evidence

See `loops/P33-gits-bank-need-task-degrade/EVIDENCE.json` and `evidence/*.log`。
