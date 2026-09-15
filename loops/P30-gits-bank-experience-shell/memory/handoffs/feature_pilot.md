# Handoff｜P30-gits-bank-experience-shell｜feature_pilot

**Time**: `2026-08-25T15:46:30Z`  
**Role**: `feature_pilot`  
**Baton**: handed to `independent_qa`

## Result

Implementation gates all pass. Loop is `ready_for_independent_qa`. `DEV_SELF_CHECK_PASS` only. No `QA_PASS`.

## Files changed (this actor)

- `.github/workflows/ci.yml` — Contract Index job calls `python3 scripts/check_contract_index_refs.py`
- `scripts/secret_scan.py` — skip `.venv`/`venv` (false-positive from unrelated untracked venv)
- `.gitignore` — ignore `.venv/` and `venv/`
- `frontend/package-lock.json` — sync for `npm ci`
- `frontend/playwright.config.ts` — fail-closed `webServer.url` health check; no skip; no 500-as-pass
- `frontend/e2e/experience-shell.spec.ts`
- `frontend/src/App.vue`
- `frontend/src/router/index.ts`
- `frontend/src/style.css`
- `frontend/src/styles/shell.css`
- `frontend/src/layouts/ExperienceShell.vue`
- `frontend/src/layouts/navConfig.ts`
- `frontend/src/types/pageReference.ts`
- `frontend/src/stores/pageReference.ts`
- `frontend/src/stores/workspaceTabs.ts`
- `frontend/src/stores/__tests__/pageReference.spec.ts`
- `frontend/src/composables/useResourceStatus.ts`
- `frontend/src/composables/__tests__/useResourceStatus.spec.ts`
- `frontend/src/components/shell/AppSidebar.vue`
- `frontend/src/components/shell/WorkspaceTabs.vue`
- `frontend/src/components/shell/ObjectHeader.vue`
- `frontend/src/components/shell/PageState.vue`
- `frontend/src/components/shell/DisabledAction.vue`
- `frontend/src/components/shell/__tests__/*`
- `frontend/src/views/WorkbenchView.vue` (P01)
- `frontend/src/views/AccountsView.vue` (P02)
- `frontend/src/views/PortfolioBoardView.vue` (P03)
- `frontend/src/views/Dashboard.vue` (compat wrapper)
- `frontend/src/views/__tests__/WorkbenchView.spec.ts`
- `frontend/src/views/__tests__/AccountsView.spec.ts`
- `frontend/src/views/__tests__/PortfolioBoardView.spec.ts`
- `frontend/src/views/__tests__/Dashboard.spec.ts`
- `frontend/src/router/__tests__/routes.spec.ts`
- `loops/P30-gits-bank-experience-shell/*` evidence, state, memory

## Not changed

- `specs/` authority sources
- `generated/` (no hand edit)
- P04–P44 pages, G0–G5, Need formal objects, CRM writeback, mobile offline write

## Evidence

See `loops/P30-gits-bank-experience-shell/EVIDENCE.json` and `evidence/*.log`.
