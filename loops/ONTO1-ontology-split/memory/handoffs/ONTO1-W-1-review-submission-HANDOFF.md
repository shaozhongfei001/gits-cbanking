# ONTO1｜包级交接：`W-1/review-submission`（复审轮送审程序与结论回收链路）

| 项 | 值 |
|---|---|
| 包名 | `review-submission`（Wave -1 内的程序包，非新波次） |
| 交出角色 | `architect-review-liaison`（Tech Lead 侧 liaison，程序与文书） |
| 接棒角色 | `tech_lead`（**同一 holder 继续**；`ROLE_BOARD.baton.holder` 与 `NEXT_SESSION.holder` 保持 `tech_lead`） |
| 交接时间 | 2026-09-20T14:15Z（本地 22:15） |
| 门禁状态 | `RETURN_TO_HLD` **有效未变**；Wave 0 及以后**零动作** |
| 索引新鲜度 | gits `INDEX_FRESH @71169042`（0 drift）；KERT `INDEX_STALE(144)`（未用索引外推，KERT 结论均回源 `文件:行`） |

## 1. 本包交付物（3 件，全部落 `memory/handoffs/`）

| # | 文件 | 内容 |
|---|---|---|
| 1 | `ONTO1-W-1-送审操作清单-V1.0.md` | 送达对象待填位（主席/3 委员/秘书处汇总人）、交付方式（重打包 zip 含 13/14 + 打包后自证 + 发出前门禁）、期限与回执、回收路径、发出前红线自查 |
| 2 | `ONTO1-W-1-结论回收与门禁更新预案-V1.0.md` | 受理有效性判定（fail-closed）+ 三形态（`DESIGN_APPROVED` / `PASS_WITH_REQUIRED_CHANGES` / 继续退回）各自 24h 动作清单 + 三形态对照表 + 通用五件 + 禁止清单 |
| 3 | 本文件 | 包级交接与接手动作 |

## 2. 本包证据（本会话新跑，可复算）

| 门禁 | 命令 | 结果 | 证据文件（loop 内） | SHA-256 |
|---|---|---|---|---|
| `wi_review_package_integrity` | `python3 scripts/onto1_review_package_check.py --gate` | PASS（`[R1] 12/12`、`[R2] 13/14 齐备`、`[R3] MANIFEST 14 件自洽`） | `evidence/wi_review_package_integrity-20260920T141501Z.log` | `23e0bf343d5103bd1bf269606d7c7c204f783dd82040739d66fb13287d0f1121` |
| `wi_review_package_selftest` | `python3 scripts/onto1_review_package_check.py --selftest` | PASS（`M1` 静默改 01 ⇒ FAIL；`M2` 删 14 ⇒ FAIL；`M0` 对照 ⇒ PASS） | `evidence/wi_review_package_selftest-20260920T141504Z.log` | `0f5f502c121b446aedd4a17b6f8f20e87cfba4aa001abb61ab1c3080e2abb0a5` |
| 重打包预演（非门禁） | `zip -r -X … /tmp`（仅 `/tmp` 草稿） | 解包 **16 项** = 1 目录 + 15 件（MANIFEST + 01~14） | `evidence/review-submission-zip-dryrun-20260920T1415Z.log` | 见文件 |

两次门禁均经 `scripts/record_gate.py` 执行并记账（`memory/waves/W0-ITER.md` Attempt 2，预算 5 次/门禁）。

## 3. 接手第一件事（Owner 侧，5 项，**全在人类手上**）

`memory/OWNER_REQUESTS.md §C-1-a ~ C-1-e`，与操作清单 §2/§3/§4 一一对应：

1. **指定**本轮评审人 / 主席 / 秘书处汇总人（填 `13` 表头与清单 §2.1）；
2. **批准并发出**送审函（`13` 末页：送审单位代表 + Owner 确认）；
3. **交付包**：重打包 zip（含 13/14），按清单 §3 步骤 1~3 自证后分发；
4. **设定期限**：建议 2026-10-09，交秘书处汇总并催办；
5. **收回签署页（14）**并交回项目侧 → 触发本包预案 §1 受理。

## 4. 本包明确未做（有意为之，非遗漏）

- **未发函**：仅落盘待发件；对外发文权限在 Owner；
- **未代签**：`13` 末页与 `14` 全部签署栏保持空白；
- **未代替委员会出结论**：预案只写"收到后做什么"；
- **未改状态机**：`gate_state.current` 仍为 `RETURN_TO_HLD`；未标 `DESIGN_APPROVED`/`FROZEN`；未启动 Wave 0+；
- **未改受审包**：01~12 零改动（`[R1] 12/12`），`MANIFEST` 保持 V1.1；未重算/未改写任何冻结哈希；
- **未产出仓库内 zip**：重打包仅预演到 `/tmp`，仓库无新增二进制制品；
- **未改** `specs/`、`generated/`、`docs/dd/`；未执行 `make generate`；未 `git add .`。

## 5. 风险提示（给接手人）

| # | 风险 | 处置 |
|---|---|---|
| 1 | **包被静默改动**：发出后若有人改 01~12 又改 MANIFEST 哈希 ⇒ 委员会结论建立在漂移证据上 | 发出前跑 `--gate`；发出后用清单 §3 步骤 2 的 `diff` 自证"发出的包 == 受检的包" |
| 2 | **误引旧包**：旧送审包（`…-committee-package/`）的三层模型 / 沿用 `gits:` 前缀 / Product 归 KERT 裁定**已被推翻** | 新包只含 MANIFEST + 01~14；旧包不夹带、不指路 |
| 3 | **无效签署件被当有效** | 预案 §1 V1~V9 共九项 fail-closed；不合格 ⇒ 退回补正，**门禁零动作** |
| 4 | **越界预支**："先按已批准开工，等签了再补" | 预案 §7 明列禁止；`gate_state` 不改即无开工许可 |
| 5 | **等**：结论未达前本 Loop 可做之事已到 Wave -1 边界 | 只读产出继续（WI-A3 跟催 / WI-A2 残留回源 / WI-A4·A5 待签） |
