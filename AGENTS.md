# Repository agent instructions

- Read `AI_GUIDE.md`, `specs/BASELINE_INDEX.yaml`, the active dispatch, and the active loop before editing.
- Tech Lead / architect roles: start from the code fact index (`.ua/knowledge-graph.json`) before reading source, and enforce `make index-status`; index output is `DERIVED`, never authority — see `docs/governance/CODE-FACT-INDEX-PROCESS.md` (GOV-CFI-001).
- Treat `specs/CONTRACT_INDEX.yaml` as the only contract registry. Contract source changes precede generated artifacts and implementation.
- Never manually edit `generated/`.
- Do not implement business behavior for M01-M22 unless the active dispatch traces it to an authorized requirement/design object.
- AI-generated facts remain candidate Claims/Proposals until the required human-control path completes.
- Do not enable quarantined Oracle or Ossie assets without an approved ADR, data-owner authorization, and a dedicated loop.
- Development roles may record `DEV_SELF_CHECK_PASS`; only an independent QA actor may record `QA_PASS`.
- Never use `git add .`. Record failures before fixing them.

## Rules

项目规则位于 `.codebuddy/rules/`，按激活方式分为两类：

### 始终生效（alwaysApply: true）

| 规则 | 说明 |
|------|------|
| `workspace` | 总宪法：合同 SSOT、权威顺序、AI 边界、目录布局、证据纪律 |
| `senior-workflow` | 高级角色切换：Tech Lead / Feature Pilot / E2E Owner，禁止角色混用 |
| `backend-local` | 后端兜底：API First、错误结构、空数组、本地 H2、MyBatis |
| `frontend-local` | 前端兜底：SDK 类型、四态处理、不发明字段、Composition API |
| `dev-standards` | 开发规范：编码风格、命名约定、Git 工作流、PR 流程、代码审查 |
| `loop-shared-memory` | Loop 共享记忆：开场/收工纪律、Baton 交接、未落盘结论不存在 |
| `code-fact-index` | 代码事实索引：TL/架构角色先查索引定位、结论必须回源、索引永不升格为权威 |

### 按路径激活（alwaysApply: false + globs）

| 规则 | 激活路径 | 说明 |
|------|----------|------|
| `backend-engineer` | `modules/**,adapters/**,apps/**,scenario/**` | Port/Adapter 模式、领域建模、测试策略、迁移规范 |
| `frontend-engineer` | `frontend/**` | Vue3 / Pinia / vue-query / Naive UI / Tailwind |
| `integration` | `specs/**,generated/**,frontend/src/api/**` | 前后端契约漂移检查、联调前置条件、合同兼容性 |
| `api-first` | `modules/**,adapters/**,apps/**,frontend/src/api/**` | API First 可执行技能：合同先行，禁止先写实现再补合同 |
| `contract-check` | `specs/**,generated/**,frontend/src/api/**` | 合同检查技能：漂移检测、联调前置、兼容性验证 |
| `e2e-verify` | `apps/**,frontend/**` | E2E 验收技能：浏览器验证工作流，不只看代码 |
