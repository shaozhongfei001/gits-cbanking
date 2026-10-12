# Handoff｜P34-gits-bank-proposal-degrade｜feature_pilot

**Time**: `2026-08-25T16:58:18Z`  
**Role**: `feature_pilot`  
**Baton**: handed to `independent_qa`

## Result

四门 implementation gates 均 `pass`。Loop 为 `ready_for_independent_qa`。仅 `DEV_SELF_CHECK_PASS`。未写 `QA_PASS`。未 commit / push / `git add .`。`qa_actor` 保持 `null`。未改 specs 权威源，未手改 generated。未实现 G0–G5 可回写状态机，未 POST proposal API，未引用 NEED-826。

## Files changed (this actor)

- `frontend/src/router/index.ts` — P24 `/proposals/new` 先于 P25 `/proposals/:id`；P23 `/proposals`；P26–P30 子路径
- `frontend/src/router/__tests__/routes.spec.ts`
- `frontend/src/layouts/navConfig.ts` — 「服务建议书」启用并指向 `/proposals`；写按钮仍全部 disabled
- `frontend/src/components/shell/AppSidebar.vue` 与 `__tests__/AppSidebar.spec.ts`
- `frontend/src/composables/proposalDegrade.ts` — 空列表 / 空向导 / 路由占位 ID，非正式 / C2 降级
- `frontend/src/components/shell/ProposalDegradeShell.vue`
- `frontend/src/views/ProposalsView.vue` — P23
- `frontend/src/views/ProposalWizardView.vue` — P24
- `frontend/src/views/ProposalRecordView.vue` — P25 静态「阶段机 C3 未授权」，无点击晋级
- `frontend/src/views/ProposalEditorView.vue` — P26
- `frontend/src/views/ProposalMapView.vue` — P27
- `frontend/src/views/ProposalEvidenceView.vue` — P28 说明当前不可反查
- `frontend/src/views/ProposalProjectView.vue` — P29
- `frontend/src/views/ProposalVersionsView.vue` — P30
- 对应 `frontend/src/views/__tests__/*.spec.ts` 与 `frontend/src/composables/__tests__/proposalDegrade.spec.ts`
- `loops/P34-gits-bank-proposal-degrade/*` evidence / state / memory

## Not changed

- `specs/` 权威源（本 actor 未改）
- `generated/`（无手改）
- `.github/workflows/ci.yml`
- Proposal / G0–G5 / ProposalVersion 正式对象
- P31–P44
- `QA_PASS` / `qa_attest`

## Evidence

See `loops/P34-gits-bank-proposal-degrade/EVIDENCE.json` and `evidence/*.log`。
