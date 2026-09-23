# PC-i1-chapter-inheritance｜Next Session Baton

| 字段 | 值 |
|---|---|
| **Updated** | `2026-09-23T04:58:55+00:00` |
| **holder** | `independent_qa` |
| **packet** | `PC-i1-chapter-inheritance` |
| **wave** | `QA 正式 reject 后已闭环整改（QA-B1/B2/N1）+ 重记 3 门禁 ⇒ 待独立 QA 复签` |
| **status** | `ready_for_independent_qa`（6/6 门禁 pass · loop-guard PASS · 实例 69/69） |
| **do_not_start** | ① 不得删改/覆盖 `evidence/independent-qa-*`（含 QA 主报告 sha256 `766cb36d…be` 与 ADDENDUM-01）；② 不得把 `EVIDENCE.json.independent_qa` 从 `reject` 改回 `pending`/`pass`（只能 append-only 新增报告）；③ 不得把 BLOCKED / INCONCLUSIVE / NOT MET 记成 pass；④ 不得由 implementation actor 记 `QA_PASS`；⑤ 不得改 P38 冻结文件与 `specs/` 受控源 |

## 一、当前结论（引用独立 QA，**不改写**）

> 报告：`loops/PC-i1-chapter-inheritance/evidence/independent-qa-pc-i1-20260923-1101.md`
> 逐章证据：`evidence/independent-qa-per-chapter-20260923-1101.json`（**13 产品 × 8 章 = 104 章，0 违规**）
> actor=`independent_qa` / session=`qa-pc-i1-independent-20260923-1101` / 模式=**非正式独立复验**

| 层次 | 结论（QA 原文，只引用） |
|---|---|
| `W-1 / W-2 本体`（V-1…V-4、V-8） | 「**独立复验通过**」：TERMS 正文确含接口 `terms[0].businessDefinition`；未接入的 `PRICING/FAQ` 未被误改；两处断言为语义化改写（**无 7→2、无弱化**）；DEMO 与「待核验」守稳 |
| `loop 出口`（V-5…V-7） | 「**BLOCKED，不得签 `QA_PASS`**」 |
| 洗绿核查 | QA 已确认：`EVIDENCE.json` 的 `contract_check` 保持 **fail**、`independent_qa` 保持 **pending**；`W0-ITER.md` 全为 `Revision epoch 0` |

**状态口径（防误读）**：`W-1/W-2` = 独立复验通过（**非正式路径**）；**本 loop 未通过**，出口 BLOCKED。

## 二、阻断项（**保持具名；不得记 pass**）

| # | 阻断 | 解除方式 / 归属 |
|---|---|---|
| 1 | **`F-PC-i1-04`**：`loop-guard` 把原始失败日志中的 **Vue 插值**误判为「未解析占位符」⇒ `loop-guard` FAIL、`--instances-check` 判 **PC-i1 1/69 不合规** | **需 Owner 授权**修法 **R-1**（扫描跳过 `evidence/**`）或 **R-2**（门禁日志改落 `frontend/test-results/gates/**`）。本 TL **未**改门禁、**未**删改证据 |
| 2 | **`contract_check` 门禁仍 fail** | 其**真实完整性失败项 = `loop-instances`**：① `[REVERSE-GATE] repro_baseline(expected_exit_code=1)` 属 **`loops/GKB-baseline-hardening`**（**非本 loop**，需其归属人处置）；② PC-i1 不合规实例（= 第 1 条）。`contract-check` **子项为 PASS**（`bash scripts/check-contracts.sh` ⇒ exit 0）—— 见 §五 QA-1 更正 |
| 3 | 独立 QA 为**非正式** | 见 §四：三条件（状态 / `loop-guard` / 全 implementation gate pass）均需 1、2 解除后，由**非 implementation actor** 走 `qa_attest.py` |

## 三、本 TL 在其后完成（**尚未经独立复验，不得声称"已通过"**）

| 工作项 | 实现 | 门禁（本机实测，已 `record_gate.py` 登记） |
|---|---|---|
| `W1-a` C6 独立区块 | 新增 `frontend/src/components/product-center/ProductInheritedChapters.vue` + `frontend/src/utils/cardChapter.ts` | `frontend_unit` **pass**（68 文件 / 371 tests） |
| `W1-b` C9 独立区块 | 同上（两区块位于主栏八章之下，**未被比较表替代**） | `e2e_parity` **pass**（2/2，含 C6/C9/C11 新断言） |
| `W1-c` C11 版本区语义 | `ProductGovernancePanel.vue` 新增「版本语义（不可变版本）」：语义 + 事实字段 + 第 11 节原文 + 相对来源 | `frontend_typecheck` pass |
| 数据接线 | `ProductCenterView.vue` 增 `cardDetail`（`CTR-PK-INT-001` 只读复用）+ `watch(selectedProductId)`；失败 ⇒ 具名缺失（不伪造） | — |

## 四、正式签署路径（逐字，满足前置后才可执行）

```text
前置（全部满足）：
  ① STATE.json.status = ready_for_independent_qa（当前 in_progress）
  ② 全部 implementation gate pass（loop_guard.py:243 硬要求；当前 contract_check = fail）
  ③ loop_guard --loop PC-i1-chapter-inheritance 无 FAIL（当前因 F-PC-i1-04 为 FAIL）
执行：
  python3 scripts/qa_attest.py --loop PC-i1-chapter-inheritance \
    --actor independent_qa --session <新会话名> --decision pass|reject \
    --evidence <仓内报告路径>
注意：--actor 不得等于 STATE.json.implementation_actor（= tech_lead）
```

## 五、已关闭的 QA 发现（附落点）

| 发现 | 处置与落点 |
|---|---|
| `QA-1`（中）`FAILURES.md` 对 `contract_check` 根因叙述与自身证据不符 | **已更正**：`FAILURES.md` 追加条目 `20260923T113000Z`（具名归因 + 注明"另有单独执行 `check-contracts.sh` 的观察"）；`memory/INDEX_BASIS.md` 与 `DISPATCH…§九` 同步更正；**原记录未删改** |
| `QA-3`（低）`LOOP.yaml.status=planned` 与 STATE 不一致 | **已改**：`LOOP.yaml.status = in_progress` + `status_note` |
| `QA-5`（可选）单测 `fixtureHasPayload` 为手写常量 | **已改**：改为**由夹具事实推导**（`ProductCenterView.spec.ts`） |
| `QA-2`（观察）gate id `contract_check` 名不副实 | 已登记于 `DISPATCH…§九`；**未改 gate 定义**（待 Owner 决定拆分/改名） |

## 六、待 Owner/收口确认（**未列入清单的改动一律未做**）

| 项 | 事实 |
|---|---|
| **`QA-4`**：`scripts/loop_guard.py`（跳过非 UTF-8）、`scripts/record_gate.py`（`--revision-note` 分纪元、exit 3 ⇒ inconclusive）**为未提交改动** | **来源非本批次**：本 TL 今日提交（`d4ad4a2`/`c69a24c`/`4e5e517`）涉及 **0 个 `scripts/` 路径**；两文件最近提交为 `be4b91b`(2026-09-13) 与 `c67ba0c`(2026-08-01) ⇒ **登记归属，待 Owner/收口确认**（**未**由本 TL 入仓）。副作用：`W0-ITER.md` 的 Attempt 编号存在 1 起偏移（首条记为 `Attempt 2`），不影响门禁判定 |
| **`ROLE_BOARD.yaml` 陈旧** | `board_status=PLANNED__IMPLEMENTATION_NOT_STARTED`、`baton.wave=W0`、`blocked_note` 称"实现未开始"，与本 loop 实际（W1-a/b/c 已实现）不一致；该文件**未列入本次更新清单** ⇒ **未改**，请 Owner 决定是否更新（`loop_guard` 仅校验 `baton.holder` = `tech_lead`，当前一致） |

## 七、未开工（**不得声称完成**）

| 项 | 状态 |
|---|---|
| `W1-d` C2/C3/C10 指名引用（P38 `scenarios`/`capabilities`/`salesBoundaries`） | **未开工** |
| `W1-e` C12（EvidenceRef，仅 `PROD-FIN-*` 3 张） | **未开工** |
| `W1-g` 同产品对照三判定（事实不丢 / 来源可达 / 阅读更快，`R2 06` §6） | **未开工** |
| 12 章**逐一落位**整体（C1–C12 全量核验） | **未完成**（C6/C9/C11 已落，其余待 `W1-d/e` 与核验） |

## 八、红线（复述）

1. `evidence/independent-qa-*` **7 个文件**（报告 / 逐章 JSON / W2 diff 快照 / 4 个 spec 副本）属独立 QA，**任何 implementation actor 不得删改**（哈希见 `EVIDENCE.md`「独立 QA — 导航」）；
2. **BLOCKED 不得记 pass**；`QA_PASS` 只能由非 implementation actor 记录；
3. 未授权项（`R-1/R-2`、`GKB` 的 `repro_baseline`）保持具名，不得静默处理。

## 九、索引新鲜度声明（GOV-CFI-001 §C5）

```text
INDEX_STALE(54) —— make index-status ⇒ WARN
  merge-meta.json 落后 HEAD 54 个提交（阈值 50）；meta.json 同。
  .ua/merge-meta.json @ 2026-09-15T17:50:17Z（gits @7116904 / kert @64f6f87；nodes 5106 / edges 4235 / 54 层）
  ⇒ 本轮全部事实**逐条回源**（含 §一 QA 结论、§二 阻断、§三 门禁）；未据索引下任何结论。
```

## 十、下一会话第一步

```text
1) 先读本文件 + STATE.json + LOOP.yaml（scope 严格不越界）
2) 等 Owner 决定：R-1/R-2 是否授权（解除 F-PC-i1-04）；GKB repro_baseline 归属人；QA-4 归属;ROLE_BOARD 是否更新
3) 若继续实现：W1-d（C2/C3/C10 指名引用）→ W1-e（C12）→ W1-g（对照三判定），每项完成即 record_gate.py + 更新 STATE
4) **不得**自行把 loop 推向 ready_for_independent_qa（须先满足 §四 前置）
```


---

## 十一、回合更新：R-1 与 GKB 处置已执行（Owner 2026-09-23 授权）

| 项 | 结果（实测） |
|---|---|
| `R-1`（`scripts/loop_guard.py`） | `reject_placeholders` 跳过 `evidence/`（只跳原始证据；`LOOP.yaml`/`STATE`/`EVIDENCE`/`memory/**` **仍全量扫描**）⇒ `loop-guard --loop PC-i1-chapter-inheritance` **PASS**；`--instances-check` **69/69 合规、0 不合规** |
| 非弱化证明 | 新增回归用例 `tests/tooling/test_loop_guard.py::test_evidence_log_with_braces_is_not_a_placeholder`（**2 passed**）：同一 token 写在 `evidence/` ⇒ **PASS**；写在 `memory/` ⇒ **FAIL 且只报该文档** |
| `contract_check` | 重记后 **pass**（`make check` 现 **22/23**、**完整性失败清零**） |
| `GKB repro_baseline` | 已登记**核对确认**（`loops/GKB-baseline-hardening/EVIDENCE.md`，append-only）：属**合法负例/红测**（`pass_condition` 即「复现基线 4 errors」、`expected_exit_code=1`、log 实测 `Tests run: 4, Errors: 4` + `BUILD FAILURE`）⇒ **未改 gate、未改其证据** |
| 必须如实声明 | `make check` 仍：`semantic-consumption` = **READINESS NOT MET**（就绪度，不计入完整性失败）· `gate-injection-tests` = **INCONCLUSIVE**（**不得计为通过**） |
| 未做（红线） | **未交棒**（`ROLE_BOARD.baton.holder` 仍 `tech_lead`）· **未提升** `STATE.status` · **未签** `QA_PASS`（`EVIDENCE.json.independent_qa` 仍 `pending`）· `W1-d/e/g` 未开工 |


---

## 十二、交棒（TL → independent_qa · 2026-09-23T04:20:06+00:00）

- `ROLE_BOARD.baton.holder` 与本文档 holder 均为 **`independent_qa`**；`STATE.status = ready_for_independent_qa`、`qa_actor = independent_qa`。
- 已完成（TL）：W-1/W-2（独立 QA 非正式复验通过）· W1-a/b/c（C6/C9 独立区块、C11 版本语义）· W1-d/e/g（C2/C3/C8/C10/C12 落位、同产品对照三判定）· R-1/GKB 处置 · 6/6 门禁 pass。
- **QA 待办（正式路径）**：
  ```text
  python3 scripts/qa_attest.py --loop PC-i1-chapter-inheritance \
    --actor independent_qa --session <新会话名> --decision pass|reject \
    --evidence <仓内报告路径（如 loops/PC-i1-chapter-inheritance/evidence/independent-qa-*.md）>
  ```
  注意：① 报告须落在**仓内**；② `--actor` 不得等于 `tech_lead`；③ 本 TL **未**代签、**未**改 `EVIDENCE.json.independent_qa`（保持 pending）。
- 交棒后 TL 不再对实现门禁执行 `record_gate.py`（该脚本要求 `status=in_progress`）；如需修复，按协议回到 `in_progress` 重走门禁。


---

## 十三、回合更新：QA 正式 reject 后闭环整改（Owner 2026-09-23 授权）

### 13.1 具名阻断的处置（QA-B1 / QA-B2 / QA-N1）

| QA 项 | 处置 | 落点 |
|---|---|---|
| `QA-B1`（阻断·中）「登记章号 vs 实际节号未彻底分离」 | ① `actualSectionNo()` 未命中**返回 `null`**（不再回落 R2 登记章号）；② 承接区标题改为「章节标题 + **卡内第 N 节**」，R2 章号仅由 tag 承载；③ meta 节号表述只取实际值（未命中 ⇒「本卡未含该节 · R2 章号 C12」）；④ 版本区缺失文案**去写死**（原「第 11 节」）⇒「（R2 章号 C11）」 | `frontend/src/utils/cardChapter.ts` · `frontend/src/components/product-center/ProductInheritedChapters.vue` · `frontend/src/components/product-center/ProductGovernancePanel.vue` |
| `QA-B2`（阻断·低）「缺失归因不实」 | 新增产品卡三态 `cardState = loading/ready/unavailable`（`frontend/src/views/ProductCenterView.vue`）并传入两组件：**仅 `ready`** 才断言「未包含该节」；`unavailable` ⇒「来源不可得 ⇒ 无法判定…」；`loading` ⇒「加载中 ⇒ 暂不判定」 | 同上三文件 |
| `QA-N1`（非阻断·测试侧） | ① 单测改写原「未包含第 12 节」断言（**该断言即缺陷语义**）并新增**反向断言**与 FIN 错位回归用例；② E2E 增 FIN 标题/meta 一致性断言 + **故障注入**用例（`page.route` 仅中断请求，不注入假数据）；③ `cardChapter.spec.ts` 中原把「回落登记值」当期望值的断言同步改为 `toBeNull()` | `frontend/src/components/product-center/__tests__/ProductInheritedChapters.spec.ts` · `frontend/e2e/product-center-pc1.spec.ts` · `frontend/src/utils/__tests__/cardChapter.spec.ts` |

**不得回退项（独立 QA 变异复验已确认正确）**：`cardChapter.ts` 定位「标题优先、节号前缀兜底」；`pc-inherited-c12-content` 绑 §11 EvidenceRef、`pc-immutable-source` 绑 §12 —— 本轮**未改动**其定位语义。

### 13.2 修前 / 修后同一探针对照（用 QA 自有探针，未改动其文件）

| 探针 | 修前 | 修后 |
|---|---|---|
| `probe-heading`（正常路径） | `PROD-FIN-003`：`head="12. EvidenceRef…"` 与 `meta="（第 11 节）"` **并列冲突** | `head="EvidenceRef （卡内第 11 节） C12原文"`；meta 第 11 节 ⇒ **无冲突**；`PROD-CM-003`/`PROD-IB-001`（本无该节）标题只标 R2 章号、不再出现「12.」 |
| `probe-faultcard`（故障路径，卡接口中断 2 次） | `findings` = **3 条** `ABSENT_ATTRIBUTION_UNSOUND`（c6 / c12 / c11） | `findings` = **空**；三条缺失文案均改为「来源不可得 ⇒ 无法判定…」；`CONTENT_DESPITE_ABORT` 仍为 0；C10 合同字段不受连带影响 |

证据：`frontend/test-results/qa-fix-pci1-20260923/before/` 与 `…/after/`（`probe-heading.json`、`probe-faultcard-PROD-FIN-003.json`）。

### 13.3 门禁重记（3 项）

| 门禁 | 命令（LOOP.yaml 逐字） | 结果 | 证据 |
|---|---|---|---|
| `frontend_typecheck` | `npm --prefix frontend run check` | exit 0（0 错误） | `evidence/frontend_typecheck-20260923T045732Z.log` |
| `frontend_unit` | `cd frontend && npx vitest run` | exit 0 · **69 文件 / 379 tests passed**（较修前 377 增 2 新用例） | `evidence/frontend_unit-20260923T045737Z.log` |
| `e2e_parity` | `cd frontend && VITE_API_PROXY_TARGET=http://127.0.0.1:18080 npx playwright test e2e/product-center-pc1.spec.ts --output=test-results/gate-e2e-parity` | exit 0 · **4 passed**（含新增故障注入用例） | `evidence/e2e_parity-20260923T045752Z.log` |

未重记（前端改动不影响其结论）：`contract_generate` / `contract_check` / `security_check`。**6/6 gate = pass**。

### 13.4 如实声明（**不得省略**）

- **`EVIDENCE.json.independent_qa` 保持 `reject`**（`actor=independent_qa`、session `qa-pc-i1-formal-20260923-1227`、`attested_at=2026-09-23T04:29:40.683085+00:00`）——本轮**未改动**；QA 主报告 sha256 复核仍为 `766cb36d2d3853d2…be`，`evidence/independent-qa-*` **零改动**，ADDENDUM-01 与 post-signature loopguard 日志未被触碰。
- **本轮未声称 `QA_PASS`**；正式复签须由**新的独立 QA 会话**执行（`--actor` 不得等于 `tech_lead`）。
- **D-15 纪元如实说明**：本次重记属「制品 revision 变更后重记」，但 `scripts/record_gate.py:76-82` 仅在**尝试预算耗尽**时才开启新纪元 ⇒ 3 项尝试记入 **epoch 1**（`frontend_unit` 达 Attempt 3；`e2e_parity`/`frontend_typecheck` 各 Attempt 2）。**本 TL 未手工改写纪元头**（避免动摇门禁计账）。
- `make check` 现状如实保留：`semantic-consumption` = **READINESS NOT MET**（就绪度，不计入完整性失败）· `gate-injection-tests` = **INCONCLUSIVE**（**不得计为通过**）。
- 本轮**未改**：`specs/` 受控源、P38 冻结文件（`ProductInterpretationView.vue`、`apps/api/.../productknowledge/`）、`Leibniz-KERT` 制品、门禁脚本；**未** `git add`/commit/push；未触碰工作树中其它 loop 的在飞改动。

### 13.5 未做 / 待 Owner（不属本轮授权）

| 项 | 状态 |
|---|---|
| `R-1` 提交 `generated/` 漂移 2 文件（根因 `bcf124e` 漏提生成物） | **未做**（需 Owner 裁定归属） |
| `R-2` 干净检出复跑（`EVIDENCE.json` 未绑定被测 tree hash） | **未做** |
| `R-3` / `CFI-OPEN-04` `scripts/ua_index_gate*.py` 未入仓 | **未做** |
| `F-4` `gate_injection_tests.py` 自查为「行文本」比对（对既有 dirty 文件存在盲区） | **未做** |
| `QA-4`（`loop_guard.py`/`record_gate.py` 未提交改动归属）· `QA-2`（gate id 名不副实） | 仍待 Owner |
| `N-1…N-4`（KERT duckdb / S3 判据 / 索引度量 `kertCommit` / GK17 门禁登记） | 仍待 Owner |

### 13.6 下一会话第一步（独立 QA 复签）

```text
前置（已满足，可复验）：STATE.status=ready_for_independent_qa · 6/6 gate pass ·
  loop_guard --loop PASS · --instances-check 69/69 ·
  ROLE_BOARD.baton.holder == NEXT_SESSION holder == independent_qa
执行：
  python3 scripts/qa_attest.py --loop PC-i1-chapter-inheritance \
    --actor independent_qa --session <新会话名> --decision pass|reject \
    --evidence <仓内报告路径>
注意：① --actor 不得等于 implementation_actor（tech_lead）；
     ② 不得改写既有 independent_qa.status=reject 与其证据（只能 append-only 新增报告）；
     ③ BLOCKED / INCONCLUSIVE / NOT MET 不得记 pass；④ 报告须落在仓内。
```


---

## 十四、回合更新：QA 复签 PASS 后的收尾（Owner 2026-09-23 授权 Batch-1）· 2026-09-23T05:33:14+00:00

### 14.1 独立 QA 复签（**结论只引用，不改写**）

| 项 | 值 |
|---|---|
| 复签会话 | `qa-pc-i1-reverify-20260923-1316` × `actor=independent_qa` |
| 结论 | **`QA_PASS`**（`qa_attest.py --decision pass`，`ATTEST_EXIT=0`） |
| 落盘 | `EVIDENCE.json.independent_qa.status=pass` · `STATE.status=qa_pass` · `attested_at=2026-09-23T05:17:24Z` · 报告 `evidence/independent-qa-reverify-20260923-1316.md`（`evidence_sha256=db093f7086bf059d…`） |
| 上一轮 reject 可追溯 | `evidence/independent-qa-formal-20260923-1227.md` sha256 **仍为** `766cb36d2d3853d23685b0edf407b51f69c499e63102314c5cb7548f7e6530be`（TL 复核）；`…-ADDENDUM-01.md`、4 支探针、3 份变异 JSON、`FAILURES.md` 三条登记原文**全部在场** |
| 覆盖声明 | 本次 `independent_qa` 字段覆盖为**协议内正式复签**（`qa_attest.py` 设计如此），非篡改；QA 已在报告 §一 与其 ADDENDUM-01 显式声明 |

### 14.2 待办闭合（Batch-1）

| 项 | 处置 |
|---|---|
| `O-1` | `EVIDENCE.md` 导航节「`independent_qa` 仍为 `pending`」**已过期** ⇒ 该节为历史陈述，**原文保留**；已在 `EVIDENCE.md` 末尾**追加**一致更正节（append-only） |
| `O-2` | **§七 与 §十二 措辞相反**（§七 称 `W1-d/e/g` **未开工**，§十二 称**已完成**）⇒ 属时序追加所致，**以 §十二 为准**；**§七 之「未开工」自本节起作废**（不改写原文） |
| `O-5` | `LOOP.yaml.status` 由 `in_progress` **同步为 `qa_pass`**（与 `STATE.status` 一致）——**签署后受控字段同步**，如实登记：`qa_attest` 的证据指纹（报告 sha256）不因该字段改写而变 |
| `R-1` | **已提交** `cc57541`：`generated/` 漂移 2 文件（根因 `bcf124e` 改 `specs/` 未随附生成物）⇒ `git status --porcelain -- generated/` 现为**空** |
| `R-3` | **已提交** `83cdebf`：`scripts/ua_index_gate.py` + `ua_index_gate_tests.py` 入仓（`CFI-OPEN-04`；`Makefile:99/102` 的 `index-status`/`index-gate-tests` 在干净检出上不再"工具缺失"） |
| `F-4` | **已实施**：`gate_injection_tests.py` 未留痕核验由「`git status` 行文本」升级为「运行前 dirty 文件 ∪ 全部注入目标」的 **sha256 字节级快照 + 自备份还原 + 无法还原即 FAIL**；非空转证据 `tests/tooling/test_gate_injection_bytecheck.py`（3 用例） |

### 14.3 仍未做 / 待 Owner

| 项 | 状态 |
|---|---|
| `O-3`（门禁未绑定被测 tree hash） | 见 §十五（`R-2` 干净检出复跑） |
| `O-4`（`semantic-consumption`=NOT MET · `gate-injection-tests`=INCONCLUSIVE） | 跨切，待 Owner（`N-1`/`N-2`/`N-3`） |
| `N-1…N-4` | 待 Owner（KERT duckdb / S3 判据 / 索引度量 `kertCommit` / GK17 门禁登记） |
| `QA-2`/`QA-4` | 待 Owner（gate id 名不副实 / 工具脚本改动归属） |


---

## 十五、`R-2` 干净检出复跑（revision `3c9a605`）· 2026-09-23T05:33:44+00:00

### 15.1 净结论（**须与 §十四 的 `R-3` 措辞一并读**）

干净检出：`git worktree add --detach /home/szf/dev/pc-i1-clean-wt HEAD`（HEAD=`3c9a605`，含 R-1/R-3/F-4）；
`frontend/node_modules` 以**符号链接**复用（不改任何受跟踪文件）。

| 门禁 | 工作树（已签证据） | **干净检出（该 revision）** | 一致？ |
|---|---|---|---|
| `contract_generate` | pass | **pass**（`make generate` 后 `git status --porcelain -- generated/` = **0 项**） | ✅ **R-1 决定性验证通过：HEAD 已自洽** |
| `contract_check`（`make check`） | pass（22/23，完整性失败 0） | **FAIL：21/23**，`INTEGRITY FAILURES: ['loop-instances']`（不合规实例 = **`ONTO1-ontology-split`**，**非 PC-i1**） | ❌ **跨 loop** |
| `security_check` | pass | **pass**（`sensitive-permissions` / `oracle-readonly-guard` PASS） | ✅ |
| `frontend_typecheck` | pass（0 错误） | **pass**（0 TS 错误） | ✅ |
| `frontend_unit` | pass（**69 文件 / 379 tests**） | **pass，但 67 文件 / 362 tests** | ⚠ **计数不同** |
| `e2e_parity` | pass（**4 passed**，含 QA-N1 故障注入用例） | **pass，但 3 passed** | ⚠ **用例数不同** |
| `make index-status` | 可执行（WARN STALE） | **目标不存在**：`make: *** 没有规则可制作目标"index-status"` | ❌ **见 15.2** |

证据（append-only 新增）：`evidence/clean-checkout-20260923T053314Z.{generate,check,sec,tsc,unit,e2e,index}.log`。

### 15.2 差异的**具名归因**（均为"未提交状态"，非 PC-i1 缺陷）

| 差异 | 根因（回源） |
|---|---|
| `loop-instances` 干净检出 FAIL | 不合规实例是 **`ONTO1-ontology-split`**（另一 loop）；其合规性依赖**未提交**的 loop 状态（工作树 70 个 loop 目录 vs 干净检出 69 个） |
| `frontend_unit` 69→67 文件 / 379→362 tests | 缺的 2 个 spec 文件属 **AN0 未提交**（如 `frontend/src/views/__tests__/AnalyticsViews.spec.ts`）⇒ 工作树计数被 AN0 未提交用例抬高 |
| `e2e_parity` 4→3 passed | **PC-i1 本轮的 QA-N1 修复（含故障注入用例）全部未提交**：提交版 `frontend/e2e/product-center-pc1.spec.ts` 仍是**被 reject 的旧制品** |
| `make index-status` 目标不存在 | **`Makefile` 的 index 目标本身未提交**（`git show HEAD:Makefile` 命中 `index-status` **0 行**；工作树 `Makefile` 8+/2−，属 1C 归类 D 类既存脏文件）⇒ **§14.2 中「R-3 后干净检出不再"工具缺失"」的措辞更正为**：**脚本已入仓**（不再"仅本地可得"），但提交版上 `make index-status` **仍不可执行**（其 Makefile 依赖未提交） |

### 15.3 `R-2` 的**前提性发现**（重要，改变收口路径）

**PC-i1 的闭合态 100% 未提交**：`frontend/src`（7 文件）+ `frontend/e2e`（1 文件）的 QA-B1/B2/N1 修复、loop 的
`STATE`/`ROLE_BOARD`/`NEXT_SESSION`/`FAILURES`/`EVIDENCE`/`W0-ITER`、以及全部 QA 证据
（`evidence/independent-qa-*`）**均未提交**；提交版 `EVIDENCE.json.independent_qa` 仍为 **`pending`**、
`STATE.status=ready_for_independent_qa`（即 QA 之前的快照）。

⇒ **`O-3`（"门禁结论绑定 revision"）当前无法达成**：revision 里装的是**被 reject 的旧制品**。

| 选项 | 内容 |
|---|---|
| **建议路径** | 由 Owner **授权提交 PC-i1 交付物**（前端 7 文件 + loop 状态/证据 + QA 报告）⇒ 在**新 revision** 上复跑 6 门禁并登记 tree hash，才算真正闭合 `O-3` |
| 备选 | 维持"未提交"，则 `O-3` 只能记为**不可闭合**（结论只对工作树成立） |

> 本轮**未**执行该提交（Owner 未授权；原整改铁律明示「不 commit、不 push」）。
> 另：`loop-instances` 与 `frontend_unit` 的差异**不是 PC-i1 造成的**，但**证明**了工作树结论受其他 loop 未提交状态影响 —— 这正是 `O-3` 的实证。
