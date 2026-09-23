# PC-i1-chapter-inheritance｜Failures（append-only）

失败必须在修改实现之前由 `scripts/record_gate.py`追加。每项至少包含时间、Gate、命令、退出码、证据文件、初步分类和下一动作；修复后追加根因、变更SHA与原命令重跑结果，不覆盖原记录。

## 20260922T145816Z｜frontend_unit

- Command: `npx --prefix frontend vitest run`
- Exit: `1`
- Evidence: `loops/PC-i1-chapter-inheritance/evidence/frontend_unit-20260922T145816Z.log`
- Classification: `PENDING_ROOT_CAUSE`
- Next: diagnose, record root cause, fix, rerun the original gate.

## 20260922T145834Z｜e2e_parity

- Command: `npx --prefix frontend playwright test e2e/product-center-pc1.spec.ts`
- Exit: `1`
- Evidence: `loops/PC-i1-chapter-inheritance/evidence/e2e_parity-20260922T145834Z.log`
- Classification: `PENDING_ROOT_CAUSE`
- Next: diagnose, record root cause, fix, rerun the original gate.

## 20260922T145839Z｜contract_check

- Command: `make check`
- Exit: `2`
- Evidence: `loops/PC-i1-chapter-inheritance/evidence/contract_check-20260922T145839Z.log`
- Classification: `PENDING_ROOT_CAUSE`
- Next: diagnose, record root cause, fix, rerun the original gate.


## 20260922T145816Z｜frontend_unit（根因 + 等价复跑；append-only，不覆盖上方 record_gate 原记录）

- 原记录：上方 record_gate 自动追加项（Exit `1`，Evidence `evidence/frontend_unit-20260922T145816Z.log`）
- **根因（已回源）**：门禁命令 `npx --prefix frontend vitest run` 由 `record_gate.py` 在**仓库根**执行 ⇒
  ① vitest 收集范围含 `frontend/e2e/*.spec.ts`（Playwright 用例被当单测加载，必然失败）；
  ② vitest 的 cwd 仍为仓库根 ⇒ 依赖 cwd 的用例 `frontend/src/theme/__tests__/naiveTheme.spec.ts:26`
  读 `src/assets/styles/theme.css` 报 `ENOENT`。实测 **75 failed / 10 passed**。
- **判定**：**门禁命令/执行位置缺陷**（非产品缺陷；本次改动为 frontend 三个源文件 + loop 文档，不在失败项内）。
- **等价复跑（修正执行位置；非官方门禁记录）**：`cd frontend && npx vitest run` ⇒ **366 passed / 0 failed**，
  证据 `evidence/frontend_unit-equiv-20260922T145854Z.log`。
- 影响：`EVIDENCE.json.gates.frontend_unit.status = fail` —— **保持 fail，不改正**；PC-i1 出口不得据此判通过。
- **建议（待授权，未改 `LOOP.yaml`）**：门禁命令改为在 `frontend` 目录执行（`bash -lc 'cd frontend && npx vitest run'`），
  或显式给 vitest 配 `root`/`exclude`（排除 `e2e/**`）。
- **流程偏差（如实登记）**：本条根因属**事后**补记（原始失败由独立 QA 报告首次暴露）；`record_before_fix=true`
  的"改前记录"未严格满足，不删改原记录。

## 20260922T145900Z｜e2e_parity（根因 + 等价复跑）

- 原记录：上方 record_gate 自动追加项（Exit `1`）
- **根因（已回源）**：同类执行环境问题 —— 从仓库根执行 `npx --prefix frontend playwright test e2e/…` 时，
  基线 `playwright.config.ts` 的 `webServer` 起 5173，其 vite 代理默认指向 `127.0.0.1:8080`（实测 401，非被测后端）
  ⇒ `page.goto('/product-center')` 失败（**2 failed**）。
- **判别（与 QA D-4 同族，非链路失效）**：用 `playwright.qa.config.ts` 指向已运行环境（15173/18080）复跑
  ⇒ **2 passed**，证据 `evidence/e2e_parity-equiv-20260922T145854Z.log`。
- 影响：`EVIDENCE.json.gates.e2e_parity.status = fail` —— **保持 fail**。
- **建议（待授权）**：门禁命令注入 `VITE_API_PROXY_TARGET=http://127.0.0.1:18080`，或直接改用 QA 配置对已运行环境执行。

## 20260922T145901Z｜contract_check（Exit 2 · 既存生成漂移，非本次引入）

- 原记录：上方 record_gate 自动追加项（Exit `2`）
- 事实：`contract-check: FAIL: generated drift detected: missing=[], extra=[], changed=['manifest.json', 'product-knowl…`（该输出**自身截断**）；
  漂移清单内**无 frontend 路径**；本次改动文件（`frontend/src/api/productCenter.ts`、
  `frontend/src/components/product-center/ProductChapterStack.vue`、`frontend/e2e/product-center-pc1.spec.ts`、
  `frontend/src/views/__tests__/ProductCenterView.spec.ts`）**均非契约生成产物**。
- 工作树状态：`make generate` 前后脏文件数均 **465+**（本会话开工前即存在）。
- **判定**：既存生成漂移，**与本次改动无关**；`EVIDENCE.json.gates.contract_check.status = fail` **保持**，
  **不得声称制品完整**；由合同 Owner / 收口流程处理。


## 20260922T150000Z｜loop-guard（**未解析占位符**误判 · 由记录门禁的动作触发）

- 现象：`python3 scripts/loop_guard.py --loop PC-i1-chapter-inheritance`
  ⇒ `FAIL: unresolved placeholders: ['loops/PC-i1-chapter-inheritance/evidence/frontend_unit-20260922T145816Z.log']`，
  并使 `--instances-check` 报「1 个新增不合规实例」。
- **根因（已回源，逐字节核对）**：`scripts/loop_guard.py:88-110` 的 `reject_placeholders` 对 loop 内**每个文件**扫
  `{` / `TEMPLATE 前缀` / `Replace-with 短语`。而 `scripts/record_gate.py:89-93` 把门禁的**原始输出**写入 `loop/evidence/`。
  本次 `frontend_unit` 失败时 vitest 打印了被测源码片段 ⇒ 该日志 **第 556 行**含
  `<span class="customer-name">{ { customer.customerName }}</span>` ⇒ 被当作"未解析占位符"。
- **判别（非真占位符）**：① 全文仅 **1** 处命中，且位于失败输出所引的 Vue 源码；② **通过的**等价复跑日志
  （`evidence/frontend_unit-equiv-20260922T145854Z.log`）命中数 **0**；③ loop 内其他文件命中数 **0**。
  ⇒ 属**扫描原始证据内容**导致的误判，与 2026-09-22 既有案例 `FAIL-2026-09-22-AN0-QA-07`
  （把"有截图"误判成"有占位符"，后改为跳过二进制）**同族**。
- **处置（本次刻意不做）**：**未**修改 `loop_guard.py` 以变绿（改门禁 = 削弱门禁）；**未**删除/改写该证据日志
  （改证据 = 失实）。因此 `loop-guard` 现为 **FAIL**，`EVIDENCE.json` 与证据**原样保留**。
- **建议修法（待授权，二选一）**：
  `R-1` `reject_placeholders` 跳过原始证据目录（`evidence/**`）/非模板类扩展名（只扫 `.md/.yaml/.json`）；
  `R-2` `record_gate.py` 把门禁原始日志写到 `frontend/test-results/gates/**`（`EVIDENCE.json` 仍记路径 + sha256），
  使其不落入占位符扫描范围。
- 影响：本 loop 出口**不得**宣称通过；`make check` 的 `loop-instances`/`loop-guard` 会因本条 FAIL。

## 20260923T023048Z｜e2e_parity

- Command: `cd frontend && VITE_API_PROXY_TARGET=http://127.0.0.1:18080 npx playwright test e2e/product-center-pc1.spec.ts`
- Exit: `1`
- Evidence: `loops/PC-i1-chapter-inheritance/evidence/e2e_parity-20260923T023048Z.log`
- Classification: `PENDING_ROOT_CAUSE`
- Next: diagnose, record root cause, fix, rerun the original gate.


## 20260923T113000Z｜**更正**：20260922T145901Z 对 contract_check 的根因叙述有误（独立 QA-1）

- 原叙述（上方 `20260922T145901Z`）称失败为「generated drift detected: changed=[...]」。
- **事实（本 TL 已回源复核）**：该叙述与 loop 自身证据不符 —— 同一门禁日志内 `[PASS] contract-check`；
  实际的**完整性失败项 = `loop-instances`**。今日复核：`bash scripts/check-contracts.sh` ⇒ **exit 0 / PASS**；
  `make check` ⇒ `[PASS] contract-check`、`[FAIL] loop-instances`、`loop-guard`（模板口径）PASS。
- 真实原因两条：
  1. `[REVERSE-GATE] 1 个 gate 的通过条件是「命令失败」：['repro_baseline(expected_exit_code=1)']`
     —— 属 **`loops/GKB-baseline-hardening`**（**非本 loop**、既有欠账，需其归属人处置）；
  2. **PC-i1 新增不合规实例**（= `F-PC-i1-04`，占位符扫描误判）。
- 影响：结论方向**不变**（门禁仍 fail、**不得**声称制品完整），但原叙述**归因错误**；该错误由本 TL 产生
  （当时只依据 `make check` 被截断的输出推断，未回源到该 loop 自己的证据日志）。**不删改原记录**，按 QA-1 更正。
- 注：`contract_check` 这一 gate id 名不副实（其失败可来自 `loop-instances`）—— 见独立 QA 报告 QA-2（观察项）。
