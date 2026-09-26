# W0｜Iteration log（append-only）

由 `scripts/record_gate.py` 追加实际attempt、命令、退出码、证据hash和下一动作。没有实际执行不得登记PASS。

## Attempt 2｜20260926T033923Z

- Gate: `type_check`
- Revision epoch: 0
- Command: `cd frontend && npx vue-tsc --noEmit`
- Exit: `0`
- Evidence: `loops/UAT2-component-test-drift/evidence/type_check-20260926T033923Z.log`
- SHA256: `0b1d7009b59b553b70adc26b8910727a011ae82cb891b8792042f4cd809f985b`

## Attempt 2｜20260926T033929Z

- Gate: `component_test`
- Revision epoch: 0
- Command: `cd frontend && npx vitest run`
- Exit: `0`
- Evidence: `loops/UAT2-component-test-drift/evidence/component_test-20260926T033929Z.log`
- SHA256: `946beaa983e6648c059a04bf1c4c5167b98f3e97249c56c3c29a1cad50c2335e`

## Attempt 2｜20260926T033949Z

- Gate: `e2e_regression`
- Revision epoch: 0
- Command: `bash scripts/uat_wave.sh uat2_regression e2e/uat/w0-route-sweep.spec.ts e2e/uat/w1-workspace-domain.spec.ts e2e/uat/w2-customer-domain.spec.ts`
- Exit: `1`
- Evidence: `loops/UAT2-component-test-drift/evidence/e2e_regression-20260926T033949Z.log`
- SHA256: `32ea83b935212f199f54fd3619988b709df3282f84c0bb14b7aad016b30e3a2f`

## Attempt 3｜20260926T034305Z

- Gate: `e2e_regression`
- Revision epoch: 0
- Command: `bash scripts/uat_wave.sh uat2_regression e2e/uat/w0-route-sweep.spec.ts e2e/uat/w1-workspace-domain.spec.ts e2e/uat/w2-customer-domain.spec.ts`
- Exit: `0`
- Evidence: `loops/UAT2-component-test-drift/evidence/e2e_regression-20260926T034305Z.log`
- SHA256: `3c60c40b2f4b785183f4e74cd342900d415824fcbf7b2b1cc735d152b7787234`
