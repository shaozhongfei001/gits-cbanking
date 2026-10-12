# PKG-A1｜PLAN（候选义务回源确认：1052 行 → 三层判定）

| 项 | 值 |
|---|---|
| Loop | `ONTO1-ontology-split`（W-1.5 就绪加固，`gate_state=RETURN_TO_HLD` ⇒ **只读分析**） |
| 负责人 | `pilot-a1`（Feature Pilot）；Baton 属 TL，本包不认领 baton、不记门禁 |
| 权限依据 | `memory/W-1.5-ORCHESTRATION.md` §1/§5、`memory/PLAN-NEXT.md` §1 A1、派工单 §PKG-A1 |
| 输入 | `evidence/consumer-scan-obligations.csv`（**1052 行**：FOLLOW_MIGRATION 1038 + CONTROL_PLANE_REQUIRED 14）、`evidence/consumer-scan-hits.jsonl`（26690 行，作完整性对账） |
| 输出 | `scripts/onto1_obligation_triage.py`、`evidence/obligation-triage.{csv,json}`、`evidence/PKG-A1-义务收敛报告.md` |

## 1. 目标（一句话）

把 1052 行**词法级**候选义务收敛为「真义务 / 同名候选 / 待回源」三层判定，**每条带 `文件:行` 证据**，
使 Wave 2 的人工回源范围从 1052 行降到「待回源」那一层；**未回源项既不计义务、也不算已排除**。

## 2. 判据（派工单给定，不自创口径；实现见脚本规则表）

| 层 | 判据（脚本常量） | 判定 |
|---|---|---|
| 强 | 内容：本体 IRI 字面量 / `owl:` / `rdf:` / `@prefix` / SPARQL / `gits-core` / `versions.ontology` / `planHash`（`STRONG_CONTENT_PATTERNS`）；路径：已确认消费面（`STRONG_PATH_PREFIXES` + `apps/api` 本体端口/规划器，`APPS_API_PORT_HINTS`） | `TRUE_OBLIGATION` |
| 弱 | 只出现**裸术语名**（class/object/data property）且位于 DTO/UI/测试/日志/持久化面（`WEAK_PATH_DECLARED` + `WEAK_PATH_EXTENDED`）**且**有同名机械证明（H1/H2/H3） | `HOMONYM_CANDIDATE` |
| 中 | 其余（`specs/*` 其余、`scripts/*`、`scenario/*`、KERT `examples|skills` 其余） | `NEEDS_SOURCE_CHECK` |

优先级：强 > 弱 > 中。判定词汇为**闭集**（三类之和必须 = 基线 1052）。

## 3. 门禁与失败条件

| 门禁 | 命令 | pass_condition | 失败即代价 |
|---|---|---|---|
| `wi_a2_obligation_triage` | `python3 scripts/onto1_obligation_triage.py --gate` | G1 输入锚定（行数 1052、处置锚点 1038/14、源文件齐备）/ G2 对账闭合（三类之和 = 1052，磁盘与复算双向）/ G3 强信号面 100% 有判定且非空转 / G4 证据存在**且逐行回源可验** / G5 弱面反一刀切 / G6 Wave 合法 / G7 磁盘产物 = 复算结果 / G8 无占位 —— 全绿 exit 0 | exit 2 |
| `wi_a2_obligation_triage_selftest` | `python3 scripts/onto1_obligation_triage.py --selftest` | M0 对照 PASS；M1~M9 变异必须按预期 FAIL/命中（11/11） | exit 2 |

**失败条件（任一即 FAIL，禁写成 inconclusive）**：输入缺失；基线行数漂移；输入处置锚点不符；源文件缺失；
命中表与义务行不对账；`TRUE/HOMONYM` 无 `文件:行` 证据或证据行不含该 token；强信号面出现
`NEEDS_SOURCE_CHECK`；弱信号面被判 `TRUE`；产物与复算不一致；输出含 TODO/占位。

## 4. 不做清单（红线）

不写 `specs/**`、`generated/**`、`docs/dd/**`；**不写 KERT 仓**（只读，`INDEX_STALE(144)`）；
不改 TL 单写者文件（`LOOP.yaml`/`EVIDENCE.json`/`EVIDENCE.md`/`STATE.json`/`FAILURES.md`/
`memory/{ROLE_BOARD,NEXT_SESSION,ORCHESTRATOR,PLAN-NEXT,INDEX_BASIS,TL-DECISIONS-*}`）；
不执行 `make generate`；不代签任何 Owner 文书；不 `git add .`；**不为过门禁弱化断言**。

## 5. 口径声明（**请 TL 审计/裁定**）

- **I-1** 弱信号面并入本仓惯用的 `**/src/test/**`、`**/dto/**`、`**/__tests__/**`（派工单列举之外的扩展，`signal` 中标 rule id；`--strict-weak-surface` 可关闭）。
- **I-2** 同名判定要求**机械证明且命名解析唯一**；无证明 ⇒ 落 `NEEDS_SOURCE_CHECK`（更保守）。同时输出替代口径计数 `alternatives.homonym_if_tier_only` 供 TL 裁定。
- **I-3** `id_pattern`（CTR-/KM-/AC-/ASSET-/SP-/KI-/KD-）不算"裸术语名"；弱面上带 ID 命中的落 `NEEDS`。
- **I-5** 不收「文件自述该名来自 OpenAPI 合同」作同名证明（`api/dto/ClaimResponse.java:9` 同段又写"本 DTO 同时携带两种语义字段"）。
- **I-6** 待回源行再分 P0（裸名精确解析到本体/领域模型包）/ P1（其余）两档，**仅排序不改判定**；P0 是否升格为真义务**由 TL 裁定**。

## 6. DoD（缺一不可）

1. 强信号文件 100% 有判定（强面零 `NEEDS_SOURCE_CHECK` 残留）—— 门禁 G3 双向断言；
2. 弱信号文件不得被判 `TRUE` 而无依据（反向亦然）—— 门禁 G5；
3. 每条 `TRUE/HOMONYM` 带 `文件:行` 且**该行可回源复核** —— 门禁 G4；
4. 对账闭合（真义务 + 同名 + 待回源 = 1052）—— 门禁 G2；
5. 变异复验 M0~M9（含"强信号注入必须被检出"与"真值函数短路必须 FAIL"）—— `--selftest` 11/11；
6. 三件套齐备：单一真值函数 `triage()`、fail-closed、变异复验；无 TODO/占位。
