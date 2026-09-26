# W0｜Iteration log（append-only）

由 `scripts/record_gate.py` 追加实际attempt、命令、退出码、证据hash和下一动作。没有实际执行不得登记PASS。

## Attempt 2｜20260926T035745Z

- Gate: `type_check`
- Revision epoch: 0
- Command: `cd frontend && npx vue-tsc --noEmit`
- Exit: `0`
- Evidence: `loops/UAT3-signal-nav-entry/evidence/type_check-20260926T035745Z.log`
- SHA256: `0b1d7009b59b553b70adc26b8910727a011ae82cb891b8792042f4cd809f985b`

## Attempt 2｜20260926T035750Z

- Gate: `component_test`
- Revision epoch: 0
- Command: `cd frontend && npx vitest run src/views/__tests__/SignalsView.spec.ts src/components/shell/__tests__/AppSidebar.spec.ts`
- Exit: `0`
- Evidence: `loops/UAT3-signal-nav-entry/evidence/component_test-20260926T035750Z.log`
- SHA256: `a0a4cc1ac3628dae7d40b596990ecd9b1ab1800b0e4d0bacd6830dc3fb612aa4`

## Attempt 2｜20260926T035757Z

- Gate: `e2e_nav_entry`
- Revision epoch: 0
- Command: `bash scripts/uat_wave.sh uat3_nav e2e/uat/w2-customer-domain.spec.ts`
- Exit: `0`
- Evidence: `loops/UAT3-signal-nav-entry/evidence/e2e_nav_entry-20260926T035757Z.log`
- SHA256: `f58f7674137327a484d87738e62c1c592640e4da97ae375dcdfba6d5a2700f7c`
