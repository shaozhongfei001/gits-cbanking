# W0｜Iteration log（append-only）

由 `scripts/record_gate.py` 追加实际attempt、命令、退出码、证据hash和下一动作。没有实际执行不得登记PASS。

## Attempt 2｜20260925T185257Z

- Gate: `env_ready`
- Revision epoch: 0
- Command: `curl -sf http://127.0.0.1:18080/actuator/health; curl -sf -o /dev/null http://127.0.0.1:5173/; curl -sf -o /dev/null http://127.0.0.1:8107/api/skill/health`
- Exit: `0`
- Evidence: `loops/UAT1-full-scenario-e2e/evidence/env_ready-20260925T185257Z.log`
- SHA256: `19708bf835990ace151fab6894346574efb9f800f56d8190766b0e8308d5b9d4`

## Attempt 2｜20260925T185301Z

- Gate: `w0_route_sweep`
- Revision epoch: 0
- Command: `bash scripts/uat_wave.sh w0_route_sweep e2e/uat/w0-route-sweep.spec.ts`
- Exit: `1`
- Evidence: `loops/UAT1-full-scenario-e2e/evidence/w0_route_sweep-20260925T185301Z.log`
- SHA256: `cc5f301b39b5a1904d607420e537a1d53677e27b2a223065cf0c4591da7af24d`

## Attempt 3｜20260925T185904Z

- Gate: `w0_route_sweep`
- Revision epoch: 0
- Command: `bash scripts/uat_wave.sh w0_route_sweep e2e/uat/w0-route-sweep.spec.ts`
- Exit: `1`
- Evidence: `loops/UAT1-full-scenario-e2e/evidence/w0_route_sweep-20260925T185904Z.log`
- SHA256: `cdf0cfcb05820ffa22f9e52c60607d5159a437b4342070ff4d973edb18a16c11`

## Attempt 4｜20260926T030302Z

- Gate: `w0_route_sweep`
- Revision epoch: 0
- Command: `bash scripts/uat_wave.sh w0_route_sweep e2e/uat/w0-route-sweep.spec.ts`
- Exit: `0`
- Evidence: `loops/UAT1-full-scenario-e2e/evidence/w0_route_sweep-20260926T030302Z.log`
- SHA256: `b394d5898c728317b63119bc35ba0415287c7c052b55013f810af441ae91ddf7`

## Attempt 2｜20260926T030525Z

- Gate: `w1_workspace_domain`
- Revision epoch: 0
- Command: `bash scripts/uat_wave.sh w1_workspace_domain e2e/uat/w1-workspace-domain.spec.ts`
- Exit: `0`
- Evidence: `loops/UAT1-full-scenario-e2e/evidence/w1_workspace_domain-20260926T030525Z.log`
- SHA256: `d7c6bc882cb22c8b222372e9ac4c7062fe609971791c1004e9a01fc58f3aa223`

## Attempt 2｜20260926T030554Z

- Gate: `w2_customer_domain`
- Revision epoch: 0
- Command: `bash scripts/uat_wave.sh w2_customer_domain e2e/uat/w2-customer-domain.spec.ts`
- Exit: `0`
- Evidence: `loops/UAT1-full-scenario-e2e/evidence/w2_customer_domain-20260926T030554Z.log`
- SHA256: `f51f20acc0e35563c799329687676594ab7ef8e6164a899a11e431a6e33d48a1`

## Attempt 2｜20260926T030642Z

- Gate: `w3_product_domain`
- Revision epoch: 0
- Command: `bash scripts/uat_wave.sh w3_product_domain e2e/uat/w3-product-domain.spec.ts`
- Exit: `0`
- Evidence: `loops/UAT1-full-scenario-e2e/evidence/w3_product_domain-20260926T030642Z.log`
- SHA256: `6bae90afa70671b38096cce84f395c13a097b60edfe4a6fc36e956906a39a58b`

## Attempt 2｜20260926T030659Z

- Gate: `w4_proposal_domain`
- Revision epoch: 0
- Command: `bash scripts/uat_wave.sh w4_proposal_domain e2e/uat/w4-proposal-domain.spec.ts`
- Exit: `0`
- Evidence: `loops/UAT1-full-scenario-e2e/evidence/w4_proposal_domain-20260926T030659Z.log`
- SHA256: `a867bfb64b4c82190a7587392e37b13072418e153d24ab0c5114302bbdf4ad21`

## Attempt 2｜20260926T030722Z

- Gate: `w5_analytics_domain`
- Revision epoch: 0
- Command: `bash scripts/uat_wave.sh w5_analytics_domain e2e/uat/w5-analytics-domain.spec.ts`
- Exit: `0`
- Evidence: `loops/UAT1-full-scenario-e2e/evidence/w5_analytics_domain-20260926T030722Z.log`
- SHA256: `0af62d5b9208c2e2666763d8aeb3d94d90b5ebfd9b833f6cadc9006fc0040b9f`

## Attempt 2｜20260926T030748Z

- Gate: `w6_journey_closed_loop`
- Revision epoch: 0
- Command: `bash scripts/uat_wave.sh w6_journey_closed_loop e2e/uat/w6-journey-closed-loop.spec.ts`
- Exit: `0`
- Evidence: `loops/UAT1-full-scenario-e2e/evidence/w6_journey_closed_loop-20260926T030748Z.log`
- SHA256: `4fcbd95d998962e48373b192ddba2a1c078b01974fde417eddd4216cfc4ed04a`

## Attempt 2｜20260926T030812Z

- Gate: `w7_mobile_governance`
- Revision epoch: 0
- Command: `bash scripts/uat_wave.sh w7_mobile_governance e2e/uat/w7-mobile-governance.spec.ts`
- Exit: `0`
- Evidence: `loops/UAT1-full-scenario-e2e/evidence/w7_mobile_governance-20260926T030812Z.log`
- SHA256: `40b1e5c71eb61644ae75cf0f95fc20949df2125e5229519e555e27cca613f8c8`

## Attempt 2｜20260926T030856Z

- Gate: `w8_error_paths`
- Revision epoch: 0
- Command: `bash scripts/uat_wave.sh w8_error_paths e2e/uat/w8-error-paths.spec.ts`
- Exit: `0`
- Evidence: `loops/UAT1-full-scenario-e2e/evidence/w8_error_paths-20260926T030856Z.log`
- SHA256: `17d24b903bd78ffc159781ebea23f267f9728199f8172e8f2e5a9a57c355ac44`

## Attempt 3｜20260926T031124Z

- Gate: `w5_analytics_domain`
- Revision epoch: 0
- Command: `bash scripts/uat_wave.sh w5_analytics_domain e2e/uat/w5-analytics-domain.spec.ts`
- Exit: `1`
- Evidence: `loops/UAT1-full-scenario-e2e/evidence/w5_analytics_domain-20260926T031124Z.log`
- SHA256: `eb677854485cab0c1d75281538caeabe90b7dc8d2af14b7e521344f78df74ca9`

## Attempt 4｜20260926T031214Z

- Gate: `w5_analytics_domain`
- Revision epoch: 0
- Command: `bash scripts/uat_wave.sh w5_analytics_domain e2e/uat/w5-analytics-domain.spec.ts`
- Exit: `0`
- Evidence: `loops/UAT1-full-scenario-e2e/evidence/w5_analytics_domain-20260926T031214Z.log`
- SHA256: `873811734cfef2e3396daa07bd83d534a99b621deef563cb79ad1e06dd56546e`

## Attempt 2｜20260926T031253Z

- Gate: `uat_package`
- Revision epoch: 0
- Command: `python3 scripts/uat_package.py --loop UAT1-full-scenario-e2e`
- Exit: `0`
- Evidence: `loops/UAT1-full-scenario-e2e/evidence/uat_package-20260926T031253Z.log`
- SHA256: `ea46a36037a8a386913f21b156d8d329f0aa8c39fcba0c072425592130cad6f1`

## Attempt 3｜20260926T031815Z

- Gate: `uat_package`
- Revision epoch: 0
- Command: `python3 scripts/uat_package.py --loop UAT1-full-scenario-e2e`
- Exit: `0`
- Evidence: `loops/UAT1-full-scenario-e2e/evidence/uat_package-20260926T031815Z.log`
- SHA256: `1c336656387bd0eb310d86f7c35638d7531cc70b096e7c6eee1ef3800418c47a`

## Attempt 4｜20260926T034635Z

- Gate: `uat_package`
- Revision epoch: 0
- Command: `python3 scripts/uat_package.py --loop UAT1-full-scenario-e2e`
- Exit: `0`
- Evidence: `loops/UAT1-full-scenario-e2e/evidence/uat_package-20260926T034635Z.log`
- SHA256: `e0f4ef5bb65fecf093e11e1117a418860902282dc652bf907ec73caac425ad14`

## Attempt 5｜20260926T034714Z

- Gate: `uat_package`
- Revision epoch: 0
- Command: `python3 scripts/uat_package.py --loop UAT1-full-scenario-e2e`
- Exit: `0`
- Evidence: `loops/UAT1-full-scenario-e2e/evidence/uat_package-20260926T034714Z.log`
- SHA256: `839303300c91051b9e3bea84f4d30c20d25a119b8d1903838a9fd91ec80adbfe`

## Attempt 6｜20260926T034749Z

- Gate: `uat_package`
- Revision epoch: 0
- Command: `python3 scripts/uat_package.py --loop UAT1-full-scenario-e2e`
- Exit: `0`
- Evidence: `loops/UAT1-full-scenario-e2e/evidence/uat_package-20260926T034749Z.log`
- SHA256: `3dfb59123798700ca877d0f500f272b976acf5dcaafbe829a1713047f1834a41`

## Revision epoch 1｜uat_package.py 制品修订（新增待裁决项提取、已修复项识别）后重记，非修复尝试｜2026-09-26T03:48:14.410481+00:00
- 依 **D-15**：预算按 revision 纪元计数（修复尝试与 revision 重记口径分离）。

## Attempt 2｜20260926T034814Z

- Gate: `uat_package`
- Revision epoch: 1
- Command: `python3 scripts/uat_package.py --loop UAT1-full-scenario-e2e`
- Exit: `0`
- Evidence: `loops/UAT1-full-scenario-e2e/evidence/uat_package-20260926T034814Z.log`
- SHA256: `6c1a0f3d00c6a91454b9926f1a0b20a3535bffd46b8228e1ab0e24a4403340d5`

## Attempt 3｜20260926T040112Z

- Gate: `uat_package`
- Revision epoch: 1
- Command: `python3 scripts/uat_package.py --loop UAT1-full-scenario-e2e`
- Exit: `0`
- Evidence: `loops/UAT1-full-scenario-e2e/evidence/uat_package-20260926T040112Z.log`
- SHA256: `4d3cd0d7ce1b1c7776306c6d3709f99e56c2c28cfe0a010adf38617157676dda`

## Attempt 4｜20260926T040127Z

- Gate: `uat_package`
- Revision epoch: 1
- Command: `python3 scripts/uat_package.py --loop UAT1-full-scenario-e2e`
- Exit: `0`
- Evidence: `loops/UAT1-full-scenario-e2e/evidence/uat_package-20260926T040127Z.log`
- SHA256: `b6f2507af4d2a1ac9b756a82836dcb9b5cf609e3a255a36660325f63d94cada4`

## Attempt 5｜20260926T051435Z

- Gate: `uat_package`
- Revision epoch: 1
- Command: `python3 scripts/uat_package.py --loop UAT1-full-scenario-e2e`
- Exit: `0`
- Evidence: `loops/UAT1-full-scenario-e2e/evidence/uat_package-20260926T051435Z.log`
- SHA256: `415a29aa8a6e23dfd5b15e7289aa966661764787fc88864114279771694bed67`

## Attempt 6｜20260926T051447Z

- Gate: `uat_package`
- Revision epoch: 1
- Command: `python3 scripts/uat_package.py --loop UAT1-full-scenario-e2e`
- Exit: `0`
- Evidence: `loops/UAT1-full-scenario-e2e/evidence/uat_package-20260926T051447Z.log`
- SHA256: `9d6a719548b3988084f3e770056dc815d87854ca10e00a79b48a398a40266ecb`
