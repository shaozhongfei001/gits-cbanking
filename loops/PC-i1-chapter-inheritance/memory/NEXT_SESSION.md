# PC-i1-chapter-inheritance｜Next Session Baton

| 字段 | 值 |
|---|---|
| **Updated** | `2026-09-23T03:32:23+00:00` |
| **holder** | `independent_qa` |
| **packet** | `PC-i1-chapter-inheritance` |
| **wave** | `W1-a/b/c（已实现，**未经独立复验**）` |
| **status** | `ready_for_independent_qa`（交棒独立 QA；6/6 门禁 pass、loop-guard PASS） |
| **do_not_start** | ① 不得删改/覆盖 `evidence/independent-qa-*`（7 个文件，属独立 QA）；② 不得把 **BLOCKED 记成 pass**；③ 不得由 implementation actor 记 `QA_PASS`（`EVIDENCE.json.independent_qa` 保持 `pending`）；④ 不得改 P38 冻结文件与 `specs/` 受控源；⑤ `R-1/R-2` 未获 Owner 授权前不得改 `loop_guard.py` |

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
