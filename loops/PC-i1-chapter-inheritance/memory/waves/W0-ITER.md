# W0｜Iteration log（append-only）

由 `scripts/record_gate.py` 追加实际attempt、命令、退出码、证据hash和下一动作。没有实际执行不得登记PASS。

## Attempt 2｜20260922T145810Z

- Gate: `contract_generate`
- Revision epoch: 0
- Command: `make generate`
- Exit: `0`
- Evidence: `loops/PC-i1-chapter-inheritance/evidence/contract_generate-20260922T145810Z.log`
- SHA256: `048ab7c55cfbb3c6707b7212288bd84d678861d4abb19a7eca16fbb7a71803b8`

## Attempt 2｜20260922T145811Z

- Gate: `security_check`
- Revision epoch: 0
- Command: `make security-check`
- Exit: `0`
- Evidence: `loops/PC-i1-chapter-inheritance/evidence/security_check-20260922T145811Z.log`
- SHA256: `1ddebf1d6907f2e68756381845f8a94d34fbd54a85005f21d321ceb6250cd91c`

## Attempt 2｜20260922T145812Z

- Gate: `frontend_typecheck`
- Revision epoch: 0
- Command: `npm --prefix frontend run check`
- Exit: `0`
- Evidence: `loops/PC-i1-chapter-inheritance/evidence/frontend_typecheck-20260922T145812Z.log`
- SHA256: `b3662785bd7165b2c084dd047249ca79e8f869265e268d9c7e06cf83a5e56e4e`

## Attempt 2｜20260922T145816Z

- Gate: `frontend_unit`
- Revision epoch: 0
- Command: `npx --prefix frontend vitest run`
- Exit: `1`
- Evidence: `loops/PC-i1-chapter-inheritance/evidence/frontend_unit-20260922T145816Z.log`
- SHA256: `f8f06ce6a98967baaa062aa99e2facdd37e2c318b00bbe71ea562b2636014fff`

## Attempt 2｜20260922T145834Z

- Gate: `e2e_parity`
- Revision epoch: 0
- Command: `npx --prefix frontend playwright test e2e/product-center-pc1.spec.ts`
- Exit: `1`
- Evidence: `loops/PC-i1-chapter-inheritance/evidence/e2e_parity-20260922T145834Z.log`
- SHA256: `8c0ac0675512dd488fea8a035d59e81a64c9337de7dfe63897994c15d43a995e`

## Attempt 2｜20260922T145839Z

- Gate: `contract_check`
- Revision epoch: 0
- Command: `make check`
- Exit: `2`
- Evidence: `loops/PC-i1-chapter-inheritance/evidence/contract_check-20260922T145839Z.log`
- SHA256: `74e46c46b9a195db729c8eee62b7fe63468c2dcdd16dc494bd2907e5e1c6a14c`

## Attempt 3｜20260923T023039Z

- Gate: `frontend_unit`
- Revision epoch: 0
- Command: `cd frontend && npx vitest run`
- Exit: `0`
- Evidence: `loops/PC-i1-chapter-inheritance/evidence/frontend_unit-20260923T023039Z.log`
- SHA256: `cf59cc02b2f32669c988159ed9fab443a0a42c3da1789586b4a454d116d81681`

## Attempt 3｜20260923T023048Z

- Gate: `e2e_parity`
- Revision epoch: 0
- Command: `cd frontend && VITE_API_PROXY_TARGET=http://127.0.0.1:18080 npx playwright test e2e/product-center-pc1.spec.ts`
- Exit: `1`
- Evidence: `loops/PC-i1-chapter-inheritance/evidence/e2e_parity-20260923T023048Z.log`
- SHA256: `fceb532f929907b05aef89753fbf6cb0d1f6b66882e8e1037e4baf8c86e60994`

## Attempt 4｜20260923T023115Z

- Gate: `e2e_parity`
- Revision epoch: 0
- Command: `cd frontend && VITE_API_PROXY_TARGET=http://127.0.0.1:18080 npx playwright test e2e/product-center-pc1.spec.ts --output=test-results/gate-e2e-parity`
- Exit: `0`
- Evidence: `loops/PC-i1-chapter-inheritance/evidence/e2e_parity-20260923T023115Z.log`
- SHA256: `39f1f056792f507325203e9945e0c24eb0373cadef42f0e826636b7076681b46`

## Attempt 4｜20260923T031008Z

- Gate: `frontend_unit`
- Revision epoch: 0
- Command: `cd frontend && npx vitest run`
- Exit: `0`
- Evidence: `loops/PC-i1-chapter-inheritance/evidence/frontend_unit-20260923T031008Z.log`
- SHA256: `d5242923e663f31710e0c35a7130ca7d6d8eff308a468d49a3d90ba8dce2cbc3`

## Attempt 5｜20260923T031018Z

- Gate: `e2e_parity`
- Revision epoch: 0
- Command: `cd frontend && VITE_API_PROXY_TARGET=http://127.0.0.1:18080 npx playwright test e2e/product-center-pc1.spec.ts --output=test-results/gate-e2e-parity`
- Exit: `0`
- Evidence: `loops/PC-i1-chapter-inheritance/evidence/e2e_parity-20260923T031018Z.log`
- SHA256: `9dc5e99ed990da108f8134bf0c3eadf5610d8b45673621cb6c6a54e974314329`

## Attempt 5｜20260923T031137Z

- Gate: `frontend_unit`
- Revision epoch: 0
- Command: `cd frontend && npx vitest run`
- Exit: `0`
- Evidence: `loops/PC-i1-chapter-inheritance/evidence/frontend_unit-20260923T031137Z.log`
- SHA256: `f0a9c410aeb5b1327791b6f0c0f67d3536140b989745e364e2e9757fc0ef3162`

## Attempt 6｜20260923T031151Z

- Gate: `frontend_unit`
- Revision epoch: 0
- Command: `cd frontend && npx vitest run`
- Exit: `0`
- Evidence: `loops/PC-i1-chapter-inheritance/evidence/frontend_unit-20260923T031151Z.log`
- SHA256: `5d0e503a3942c024593ea498d2df6d6b999d3580db589edca355b1735a905e26`

## Attempt 3｜20260923T033153Z

- Gate: `contract_check`
- Revision epoch: 0
- Command: `make check`
- Exit: `0`
- Evidence: `loops/PC-i1-chapter-inheritance/evidence/contract_check-20260923T033153Z.log`
- SHA256: `9042f812c2e373868d2dcf34e263ab99436f274c43a2734a98dc9fba464f470d`

## Attempt 6｜20260923T034516Z

- Gate: `e2e_parity`
- Revision epoch: 0
- Command: `cd frontend && VITE_API_PROXY_TARGET=http://127.0.0.1:18080 npx playwright test e2e/product-center-pc1.spec.ts --output=test-results/gate-e2e-parity`
- Exit: `0`
- Evidence: `loops/PC-i1-chapter-inheritance/evidence/e2e_parity-20260923T034516Z.log`
- SHA256: `7e8c12948362ba42b82ab21ed1b98d15e8fc125d21fa3141e83248ac37ea6fb8`

## Revision epoch 1｜制品 revision 变更（W1-d/W1-e 实现 + 卡间节号错配/版本区写死节号两处缺陷修复）后按 D-15 重记｜2026-09-23T03:45:33.114772+00:00
- 依 **D-15**：预算按 revision 纪元计数（修复尝试与 revision 重记口径分离）。

## Attempt 2｜20260923T034533Z

- Gate: `frontend_unit`
- Revision epoch: 1
- Command: `cd frontend && npx vitest run`
- Exit: `0`
- Evidence: `loops/PC-i1-chapter-inheritance/evidence/frontend_unit-20260923T034533Z.log`
- SHA256: `2f2fc2134ab85d6107537326db704e6c6aa27cbef4ab1df7f0067df68045070e`

## Attempt 2｜20260923T045732Z

- Gate: `frontend_typecheck`
- Revision epoch: 1
- Command: `npm --prefix frontend run check`
- Exit: `0`
- Evidence: `loops/PC-i1-chapter-inheritance/evidence/frontend_typecheck-20260923T045732Z.log`
- SHA256: `b3662785bd7165b2c084dd047249ca79e8f869265e268d9c7e06cf83a5e56e4e`

## Attempt 3｜20260923T045737Z

- Gate: `frontend_unit`
- Revision epoch: 1
- Command: `cd frontend && npx vitest run`
- Exit: `0`
- Evidence: `loops/PC-i1-chapter-inheritance/evidence/frontend_unit-20260923T045737Z.log`
- SHA256: `9fd3aced2d2438e94bc1ee072bb57963510f0f25e456359bc585ea517d83997a`

## Attempt 2｜20260923T045752Z

- Gate: `e2e_parity`
- Revision epoch: 1
- Command: `cd frontend && VITE_API_PROXY_TARGET=http://127.0.0.1:18080 npx playwright test e2e/product-center-pc1.spec.ts --output=test-results/gate-e2e-parity`
- Exit: `0`
- Evidence: `loops/PC-i1-chapter-inheritance/evidence/e2e_parity-20260923T045752Z.log`
- SHA256: `171d588a4086ccb59290471876f9d96d6b816e188fce9e56e69da3ab81a9b97a`
