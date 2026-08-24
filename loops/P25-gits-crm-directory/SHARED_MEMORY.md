# P25-gits-crm-directory｜Shared Memory

> Chat不是SSOT；未落盘等于不存在。

## Current Snapshot

| 字段 | 值 |
|---|---|
| status | ready_for_independent_qa |
| baseline_commit | `2e1118d251ff065d3793e6d771d28a306dd5a1af` |
| baton_holder | `independent_qa` |
| current_wave | `W0` |
| updated_at | `2026-08-22T11:15:00Z` |

## Role Results

| 角色 | 状态 | 结果 | Handoff |
|---|---|---|---|
| `tech_lead` | done | Contract + fixture + plan frozen | `memory/TECHLEAD_DELIVERY_PLAN.md` |
| `feature_pilot` | done | Backend upsert + frontend refresh | `memory/handoffs/feature_pilot.md` |
| `e2e_owner` | done | Re-ran API 14 + frontend 50; no QA_PASS | `HANDOFF.md` |
| `independent_qa` | dispatched | — | — |

## Implementation notes

- H2 `customer` is CRM directory only. No KYC/products/graph ingest.
- Fixture path walks `user.dir` ancestors (Surefire cwd is `apps/api`).
- `PUT /api/v1/engagement/customer/{customerId}` → CREATED|UPDATED; credit-code clash → 409.
- Workbench 「刷新客户目录」: POST reload then GET list.
