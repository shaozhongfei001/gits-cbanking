# Handoff｜P36-gits-bank-mobile-degrade｜feature_pilot

**Time**: `2026-08-25T17:32:00Z`  
**Role**: `feature_pilot`  
**Baton**: handed to `independent_qa`

## Result

四门 implementation gates 均 `pass`。Loop 为 `ready_for_independent_qa`。仅 `DEV_SELF_CHECK_PASS`。未写 `QA_PASS`。未 commit / push / `git add .`。`qa_actor` 保持 `null`。未改 specs 权威源，未手改 generated。未改 `/commitments` path 或 pageId=P36。未实现移动缓存 / 同步 / 离线包 / Service Worker。未把 localStorage 当正式 Claim/Task/Commitment。

## Files changed (this actor)

- `frontend/src/router/index.ts` — P41 `/m/today`、P42 `/m/previsit`、P43 `/m/notes`、P44 `/m/checkout`；`/commitments` path 与 pageId=P36 未改
- `frontend/src/router/__tests__/routes.spec.ts`
- `frontend/src/layouts/navConfig.ts` — 新增「移动端（降级）」分组
- `frontend/src/components/shell/__tests__/AppSidebar.spec.ts`
- `frontend/src/composables/mobileDegrade.ts` 与 `__tests__/mobileDegrade.spec.ts`
- `frontend/src/components/shell/MobileDegradeFrame.vue`
- `frontend/src/views/MobileTodayView.vue` — P41；「打开首项」仅 RouterLink 到在线深链
- `frontend/src/views/MobilePrevisitView.vue` — P42；「开始拜访」DisabledAction
- `frontend/src/views/MobileNotesView.vue` — P43；「新增速记」禁用；草稿非正式 Claim
- `frontend/src/views/MobileCheckoutView.vue` — P44；无 PENDING E01 时禁用「完成会谈」；有则 `decideHumanGate` 与桌面 P17 同一合同
- `frontend/src/views/__tests__/MobileDegradeViews.spec.ts`
- `loops/P36-gits-bank-mobile-degrade/*` evidence / state / memory

## Not changed

- `specs/` 权威源（本 actor 未改）
- `generated/`（无手改）
- `.github/workflows/ci.yml`
- `/commitments` path / pageId=P36
- 移动缓存 / 同步 / 离线包 OpenAPI
- Service Worker / Cache API
- P31–P40 行为
- `QA_PASS` / `qa_attest`

## Evidence

See `loops/P36-gits-bank-mobile-degrade/EVIDENCE.json` and `evidence/*.log`。
