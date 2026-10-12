# 交接｜ONTO1-W-1/D1（国标正式文本跟催 + 条款矩阵空表与判据）

| 项 | 值 |
|---|---|
| 包 | `ONTO1-W-1/D1`（Wave -1，只读） |
| 交出角色 | standards-alignment-analyst（P-6 会话） |
| 接棒 | **tech_lead** |
| 日期 | 2026-09-20 |
| 门禁位置 | `RETURN_TO_HLD` 仍有效（本包不改变门禁） |
| 文本状态 | **未到手**（`text_obtained=false`） |

## 1. 交付物（7 件）

| # | 制品 | 位置 | 哈希/状态 |
|---|---|---|---|
| 1 | 跟催登记表（含载体缺口核查 + 每日核验 + 存量发现） | `evidence/WI-A3-D1-跟催登记表.md` | 见 §2 |
| 2 | 申请函草案（**未发出**，待 Owner/标准管理员签署） | `docs/dispatch/ONTO1-D1-国标正式文本获取申请-DRAFT.md` | — |
| 3 | 矩阵空表（机读，数据行 0） | `evidence/wi-a3-clause-matrix-EMPTY.csv` | 表头 6 栏 |
| 4 | 骨架（未发布，无条款内容；禁 CONFORMANCE 命名） | `memory/staging/REFERENCE-ALIGNMENT.md` | 含逐字口径 + 判据 |
| 5 | 机读状态（门禁 fail-closed 读取） | `evidence/wi-a3-d1-followup-status.json` | `text_obtained=false` |
| 6 | 日常核验门禁（单一真值函数 + 变异复验） | `scripts/onto1_reference_alignment_check.py` | `--gate` PASS / `--selftest` 10/10 |
| 7 | 登记表（历史件 11 / 权威件 2 / 文件名范围豁免 2，全部钉哈希） | `evidence/wi-a3-reference-wording-registry.json` | 逐条 `sha256` |

核验日志（交付态终验）：`evidence/wi_a3_reference_alignment-20260920T142412Z.log`（`sha256 9d3b9cb540784bc8…`）、
`evidence/wi_a3_reference_alignment_selftest-20260920T142412Z.log`（`sha256 94ffa19bb38e3280…`）。

## 2. 关键结论（都要回源）

1. **D1 的载体缺口**：登记表所称《国标正式文本获取申请》在 10 号文件中**只是流程表一行**，
   无独立申请函/受理人/渠道/回执 ⇒ 程序真实状态＝**未发出**（回源见跟催登记表 §3）。
2. **存量登记缺口**：归档旧送审包与外部权威评议件仍含**已被否决的命名方案**（多文件）；
   按仓内纪律**保留原文 + 显式登记哈希**，不改写（清单见登记表 §5）。
3. **矩阵守门已可执行**：文本未到手时，骨架与机读空表的数据行必须为 0，且置真状态必须四项字段齐备
   （M3/M5/M6 三条变异已证明该断言有牙齿）。
4. **判定层次**：F 文件名 / A 制品名 / C 表述 / S 矩阵；未登记即 FAIL，已登记钉哈希。

## 3. 未做（越界或属他人单写者/权限）

| # | 未做项 | 原因 | 归属 |
|---|---|---|---|
| 1 | 登记 `wi_a3_reference_alignment` + `_selftest` 进 `LOOP.yaml.gates` | `LOOP.yaml` 为 TL 单写者 | **tech_lead** |
| 2 | 更新 `STATE.json` / `EVIDENCE.json` / `NEXT_SESSION.md` / `ORCHESTRATOR.md` | 同上（单写者） | **tech_lead** |
| 3 | `memory/INDEX_BASIS.md` 追加本批次回源结论 | 同上（单写者） | **tech_lead** |
| 4 | 发出申请函、任命公共语义 Owner、两条存量裁决（是否加抬头 / KERT 侧处置） | 人类权限，TL 与分析角色不得代发代签 | **Owner / 标准管理员 / 公共语义 Owner / KERT 维护方** |
| 5 | 改动历史件与权威评议件 | 仓内规则要求保留历史文档；且权威件属评审方记录 | **不做（设计如此）** |
| 6 | 条款级判定 | 文本未到手（`BLOCKED-ON-EXTERNAL`） | 待 T1 |

## 4. 接手动作（按优先级）

1. `python3 scripts/onto1_reference_alignment_check.py --gate` 先跑一次确认基线（预期 PASS）；
2. 把 §3 第 1~3 项按单写者身份落盘（门禁登记 + 状态/证据/交接更新 + 索引依据追加）；
3. 催办 Owner 签署发出申请函（目标 2026-10-09）；到手后 1 个工作日内走 T2→T3→T4；
4. 每日跑一次 `--gate` 并把日志留 `evidence/wi_a3_*`（前缀已登记为核验自身产物，不参与扫描）。

## 5. 风险与红线

| 风险 | 说明 | 处置 |
|---|---|---|
| R-D1-1 | 载体不补齐 ⇒ 10-09 到期无法归因（从未申请 vs 未回复） | 草案已就绪，只差签署发出 |
| R-D1-2 | 归档件被误引用为当前方案（含已被否决的命名） | 登记表钉哈希 + 门禁拦新增；须明确"不得引用为当前口径" |
| R-D1-3 | 公共语义 Owner 未任命 ⇒ 接收确认与矩阵签署无人可签 | 已并入角色缺口上报（`OWNER_REQUESTS.md §A`） |
| R-D1-4 | 核验为词法级，可能漏检 | 已如实声明精度上限；命中清单须人工复核 |

**红线保持**：文本到手前零标准符合性表述；条款对齐不并入设计基线；R1~R9 不声称即标准要求；
未使用 CONFORMANCE 命名；未改动 `specs/` / `generated/` / 封版 `docs/dd/`；未 `git add .`。

**索引新鲜度（GOV-CFI-001）**：`[索引] INDEX_FRESH @ merge 2026-09-15T17:50Z (gits 71169042)`；
**`[索引] KERT INDEX_STALE(144)`**（@64f6f87 → HEAD 922a674d）⇒ 本包 KERT 结论均直接读取并带 `文件:行`，未用索引外推。
