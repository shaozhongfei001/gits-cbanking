# PKG-A1｜HANDOFF（候选义务回源确认：1052 → 626 / 0 / 426）

| 项 | 值 |
|---|---|
| Loop | `ONTO1-ontology-split`（W-1.5 就绪加固，`gate_state=RETURN_TO_HLD` 未变） |
| 交付者 | `pilot-a1`（Feature Pilot）；**未认领 Baton、未记任何门禁、未改 TL 单写者文件** |
| 交付时间 | 2026-09-20 |
| 状态 | **DONE**（`--gate` exit 0；`--selftest` exit 0，11/11） |

## 1. 交付物 + 哈希（AU-1 用）

| 交付物 | sha256 | 说明 |
|---|---|---|
| `scripts/onto1_obligation_triage.py` | `1982a9ec2017df97c3e48a7cb87738c0a69c38ecf98461c51d4000d4c99c2b30` | 单一真值函数 `triage()/triage_row()` + `--report/--gate/--selftest`（1163 行） |
| `loops/ONTO1-ontology-split/evidence/obligation-triage.csv` | `81e5ebc414df576cb1969d6073b44a06d83e885dc32ee09ec64e3469625b2250` | 1052 行判定；列 = `repo,path,tier,signal,disposition,rationale,evidence,responsible_wave` |
| `loops/ONTO1-ontology-split/evidence/obligation-triage-summary.json` | `325910baeac0a402c9ba95fa8f49132e1421e159715713604953c5c008ce0362` | 计数/目录分布/对账闭合/P0-P1/Wave 归类/替代口径 |
| `loops/ONTO1-ontology-split/evidence/PKG-A1-义务收敛报告.md` | `89428f094a2af3511f00dcee3fea4cf27f8fecd1153425ee10da30b2aa34bd5b` | 人读报告（方法与口径、收敛前后、真义务按 Wave 归类、待回源处置、诚实声明） |
| `memory/waves/PKG-A1-PLAN.md`、`memory/waves/PKG-A1-ITER.md` | — | loop engineering 过程记录（含缺陷 F-1~F-6） |

> **哈希稳定性提示（AU-1）**：`obligation-triage.csv` 的内容是确定性的（哈希固定为
> `81e5ebc414df576c…`）；`summary.json` 与报告内含 `generated_at`，**重跑 `--report` 会使这两个哈希变化**。
> 若 AU-1 之前先跑了 `--report`，请以重跑后的哈希为准；`--gate` 与 `--selftest` 不写产物、不影响哈希。

## 2. 结论（收敛结果，对账闭合）

| 判定 | 行数 | 占比 | 含义 |
|---|---|---|---|
| `TRUE_OBLIGATION` | **626** | 59.5% | 强信号（内容级证据 140 / 仅路径依据 486）⇒ 必须跟随迁移 |
| `HOMONYM_CANDIDATE` | **0** | 0% | 无一条弱面命中达到"可证明的唯一解析"（**不等于**净义务里没有同名） |
| `NEEDS_SOURCE_CHECK` | **426** | 40.5% | 待回源；内含 **P0=65**（裸名精确解析到本体/领域模型包）/ P1=361 |
| 合计 | **1052** | 100% | 基线 1052，delta 0，`closed=True` |

真义务按责任 Wave：`W2_SPLIT` 291 · `W3_CONSUMER_SWITCH` 316 · `W3_KERT_ASSETS` 19。

**本轮最有信息量的发现（建议 TL 裁定）**：426 行待回源里有 **65 行**的裸名按简单名**精确解析到
`com.gien.gits.ontology`（55）/ `com.gien.gits.action.domain`（6）/ `com.gien.gits.ontology.domain`（4）**，
即这些文件导入的就是 `modules/operational-ontology` 的 Java 本体模型类（样本
`apps/api/.../ClaimController.java:15` = `import com.gien.gits.ontology.Claim;`）。按派工单强信号清单
（IRI 字面量 / OWL / SPARQL / 路径面）此形态**不在强信号内**，故我**没有**自行升格为真义务，
只打了可复核的 P0 标签；**是否升级由 TL 裁定**（口径 I-6）。

## 3. 门禁实测（AU-2 请 TL 复跑；命令文本已人工复核）

| 门禁 | 命令 | 实测 exit | 关键输出 |
|---|---|---|---|
| `wi_a2_obligation_triage` | `python3 scripts/onto1_obligation_triage.py --gate` | **0** | `PASS (G1 输入锚定 / G2 对账闭合 / G3 强面判定 / G4 证据可回源 / G5 弱面反一刀切 / G6 Wave 合法 / G7 产物一致 / G8 无占位)` |
| `wi_a2_obligation_triage_selftest` | `python3 scripts/onto1_obligation_triage.py --selftest` | **0** | `11/11 用例符合预期`（M0/M1/M2a/M2b/M3/M4/M5/M6/M7/M8/M9） |
| （生成） | `python3 scripts/onto1_obligation_triage.py --report` | **0** | `rows=1052 true=626 homonym=0 needs=426 sum=1052 closed=True` |

**门禁断言清单**（供 `pass_condition` 落文）：G1 输入锚定（1052 行 + 处置锚点 1038/14 + 源文件齐备，
缺任一 ⇒ FAIL）· G2 对账闭合（三类之和 = 1052；磁盘与复算**双向**）· G3 强信号面 100% 有判定
且强面非空、内容面与路径面均非空 · G4 `TRUE/HOMONYM` 每条带 `文件:行` 且**该行可回源复核**
（含行号越界、行内无 token ⇒ FAIL）· G5 弱面禁判 `TRUE`、同名须带机械证明、本体包标签须有导入行证据
· G6 Wave 合法性 · G7 磁盘 CSV/摘要 = 本次复算（防手改证据）· G8 无 TODO/占位。

## 4. 登记建议（**由 TL 执行 `record_gate.py`，本包不自行登记**）

```text
gate id            : wi_a2_obligation_triage
command            : python3 scripts/onto1_obligation_triage.py --gate
pass_condition     : G1 输入锚定（1052 行 + 1038/14 处置锚点 + 源文件齐备，缺即 FAIL）/
                     G2 对账闭合（TRUE+HOMONYM+NEEDS = 1052，磁盘与复算双向）/
                     G3 强信号面 100% 有判定且非空转（内容面与路径面均非空）/
                     G4 TRUE|HOMONYM 证据可回源（行号在范围内且行内含该 token）/
                     G5 弱面禁判 TRUE、同名须带机械证明 /
                     G6 Wave 合法性 / G7 产物与复算逐行一致 / G8 无占位
expected exit      : 0（当前实测 0；输入漂移/证据不可回源时为 2）

gate id            : wi_a2_obligation_triage_selftest
command            : python3 scripts/onto1_obligation_triage.py --selftest
pass_condition     : M0 对照 PASS；M1 弱面注入本体 IRI 必须判强信号；M2a/M2b 弱面判真义务必须 FAIL；
                     M3 删强信号判定必须 FAIL；M4 真值函数短路必须 FAIL；M5 输入缺失必须 FAIL；
                     M6 证据不可回源必须 FAIL；M8 同文件有本体包通配导入必须禁判同名；
                     M9 本体包耦合必须落待回源并带 P0 标签；M7 恢复后对照 PASS（共 10 条计数 + 1 对照）
expected exit      : 0（11/11；任一变异未被拦下即 2）
evidence_file 建议 : 由 TL 在记账时生成（本包刻意未写 evidence/*.log，避免在该门禁登记前产生
                     wi_evidence_board_check 孤儿日志）
```

## 5. 口径声明（**TL 必审，5 条**；详见报告 §2.1 与 ITER §3）

- **I-1** 弱信号面扩展：并入本仓惯用的 `**/src/test/**`、`**/dto/**`、`**/__tests__/**`（派工单列举之外；`signal` 中标 rule id）。**实测精确信息**：派工单列举的弱面前缀（`frontend/`、`tests/`、`adapters/persistence-relational/`、`evidence/`、`loops/`）在 1052 行净义务内为 **0 行**（相关命中已被 WI-A2 路由到 `HOMONYM_REQUIRES_SOURCE_CHECK`）；`--strict-weak-surface` 关闭扩展后弱面 = 0 行、判定计数不变（626/0/426，仅 tier 标签 WEAK→MEDIUM）——即该扩展**只影响 tier 标签与 G5 保护范围，不影响任何判定**。
- **I-2** 同名判定要求机械证明 **且命名解析唯一**；无证明落 `NEEDS`（比"tier=WEAK 即判同名"更保守）。替代口径计数：同名 97 / 待回源 329（`summary.alternatives`）。
- **I-3** `id_pattern`（CTR-/KM-/AC-/ASSET-/SP-/KI-/KD-）不算裸术语名；弱面带 ID 命中的 13 行落 `NEEDS`。
- **I-4** `TRUE_OBLIGATION` = 「必须跟随迁移」的**判定**，非「已确认本体消费」的**结论**；其中 486 行依据是路径规则，Wave 2 应优先抽检。
- **I-6** P0/P1 是**回源优先级**，不改判定；P0 是否升格真义务由 TL 裁定。
- **I-5** 不收「文件自述该名来自 OpenAPI 合同」作同名证明（`api/dto/ClaimResponse.java:9` 同段又写"本 DTO 同时携带两种语义字段"）。

## 6. 未决与风险

1. **真义务 626 行 > `PLAN-NEXT.md` §1 A1 的 400 行阈值** ⇒ 触发"立即回写 `evidence/WBS-RESTIMATE.md`
   并在 `ORCHESTRATOR.md §5` 新增风险项"条款。**该两文件在本包写域外，请 TL 执行**（数据来源：
   `obligation-triage-summary.json.true_by_wave`）。
2. **同名候选 = 0 是"无可证明者"，不是"不存在同名"**：WI-A2 已把可判同名的 2690 处路由到
   `HOMONYM_REQUIRES_SOURCE_CHECK`（未进入净义务）。若 TL 采用口径 I-2 的替代读法，同名档为 97 行。
3. **P0=65 的"是否升格真义务"未决**：升格会使真义务升到 691；不升格则 Wave 2 需读判这 65 行。
   我未自行升格（不自创强信号口径）。
4. **`kert/examples|skills` 65 行**（P1 内）需 KERT 侧回源：`INDEX_STALE(144)`，KERT 目录只读，
   本轮结论全部回源到 `文件:行`（未据索引外推）。
5. `apps/api/src` 待回源 188 行是本轮最大的单块人工量；报告 §5 给了 5 档回源次序建议。
6. 弱面 97 行里有 7 行同文件存在本体包**通配**导入（如 `HumanGateControllerTest.java:8`）⇒ 命名解析
   不唯一，**这类文件很可能是真消费面**，请勿按"测试面"一概豁免。

## 7. 红线声明（AU-5 用）

- `git status`：本包只新增/改动 `scripts/onto1_obligation_triage.py` 与
  `loops/ONTO1-ontology-split/{evidence/obligation-*,evidence/PKG-A1-*,memory/waves/PKG-A1-*,memory/handoffs/PKG-A1-*}`；
  **未**改 `specs/**`、`generated/**`、`docs/dd/**`、`LOOP.yaml`、`EVIDENCE.json`、`EVIDENCE.md`、
  `STATE.json`、`FAILURES.md`、`memory/{ROLE_BOARD,NEXT_SESSION,ORCHESTRATOR,PLAN-NEXT,INDEX_BASIS,TL-DECISIONS-*}`；
- **未写 KERT 仓**（Leibniz-KERT 全程只读：仅 `read_text`）；
- **未执行** `make generate`；**未** `git add .`；**未**记任何门禁（含 `DEV_SELF_CHECK_PASS`）；
- **未**为过门禁弱化断言：F-4（单向校验空转）与 F-5（同名证明过宽）是**反向收紧**记录，见 ITER §2-§3。

## 8. 交接

Baton 仍在 TL（本包不认领）。建议 TL 后续动作：① AU-2 复跑两条命令；② AU-3 随机抽 3 条判定回源
（建议抽：1 条内容级 `TRUE`、1 条仅路径 `TRUE`、1 条 P0 `NEEDS`）；③ AU-4 手工注入一条变异（推荐
"把某 `TRUE` 行证据行号 +1"）验证 G4 有牙齿；④ `record_gate.py` 记账两条门禁 + `loop_guard` +
`onto1_evidence_board_check`；⑤ 裁定 I-1/I-2/I-6 三条口径与 P0 是否升格。
