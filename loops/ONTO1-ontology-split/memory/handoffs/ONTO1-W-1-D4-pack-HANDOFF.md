# ONTO1｜包级交接：`W-1/D4-pack`（D4 A-Box 权威确认决策包）

| 项 | 值 |
|---|---|
| 包 ID | `W-1/D4-pack` V1.0 |
| 编制角色 | `data-authority-analyst`（TL 派工 P-5） |
| 交回 | `tech_lead`（Baton 未换手；本包不改变 `RETURN_TO_HLD`） |
| 门禁 | `wi_a5_d4_pack` = pass（Attempt 1）｜`wi_a5_d4_pack_selftest` = pass（Attempt 1） |
| 阻塞归属 | **全部剩余动作在人类手上**：数据 Owner 裁定 + 业务 Owner 会签 + 产品 Owner（产品身份部分） |

## 1. 交付物（4 件 + 1 门禁脚本）

| 类型 | 路径 | 说明 |
|---|---|---|
| 决策包正文 | `docs/dispatch/ONTO1-D4-决策包-V1.0.md` | 8 术语逐项确认表（候选 + 依据 + 勾选）/ SourceIdentifier 最小字段 / 投影合同草案 / SIM 载体与退出台账 / CQ1-CQ2 依赖 / 待决项 / 签署区（空白） |
| 机读清单 | `loops/ONTO1-ontology-split/evidence/d4-l1-authority-candidates.csv` | 32 行 = 8 术语 ×（2~3 权威候选 + ≥1 禁止项 / 1 存放位置） |
| 机读包 | `loops/ONTO1-ontology-split/evidence/d4-pack.json` | 非声明 + 字段表 + 拒绝规则 + 合同草案 + SIM 台账 + CQ 依赖 + 7 项待决项 |
| 哈希清单 | `loops/ONTO1-ontology-split/evidence/d4-pack-manifest.json` | 冻结机读底座（防静默漂移） |
| 门禁脚本 | `scripts/onto1_d4_pack.py` | `--gate` / `--selftest` / `--write-manifest` |

## 2. 这份包把什么变「可判定」

1. **候选可勾选**：8 术语各 2~3 个权威候选（含强度与 `文件:行`），并显式登记**禁止项**（GITS 运营库 / KERT workspace / KERT 产品卡 / 裸字符串 ID）——禁止项是红线，不是建议。
2. **拒绝可判定**：`MISSING_SOURCE_IDENTIFIER`（fail-closed）+ 10 个子码 + 6 条禁止行为 + 统一错误结构；字段与既有合同（`CTR-DATA-001`）逐一对齐，不新造词汇。
3. **合同不生效可证**：`effective_from = null`、`signed_by = null`、合同 ID 未分配 → 门禁 C7 强制。
4. **台账可跟踪**：四条退出条件各有「触发判据 / 检测方式 / 责任人 / 频率 / 状态」，且声明未生效期间状态只能 `NOT_TRIGGERED` → 门禁 C8 强制。
5. **CQ 拆解**：CQ1/CQ2 的 `negative` 与 `mutation` **不依赖 D4**（设计层已定）；只有 `positive` 的可判真结论被 D4 阻塞 → 可先做负例设计，不必空等。

## 3. 接手第一件事（按顺序）

0. 复跑 `python3 scripts/onto1_d4_pack.py --gate`（应 PASS；若 FAIL 说明机读底座被改过，先查是谁改的——manifest 有哈希）。
1. 把本包随 D4 请求函一并交数据 Owner；**产品身份部分（`ProductOffering`）同步交产品 Owner（D2）**——D4 侧只需其确认否定命题「产品身份 A-Box ≠ KERT 产品卡」。
2. 收签署件后按 `memory/OWNER_REQUESTS.md` 更新状态；若走 **SIM 路径**，先取 SIM 声明签署件再启动台账——把 `ledger_status` 由 `TRACKING_NOT_STARTED` 改为已启动属**声明生效后**的动作，不得提前（门禁 C8 会拦下提前启动）。
3. 合同草案若要进入受控：`specs/` → `CONTRACT_INDEX.yaml` → `make generate`，执行方是 Integration Contract Owner（**尚未任命**）；在此之前**不得**让它「生效」。

## 4. 本会话有意未做（不是遗漏）

- 未修改 `specs/`、`generated/`、`CONTRACT_INDEX.yaml`、封版 `docs/dd/`；未执行 `make generate`；
- **未修改** `docs/architecture/ONTO1-SIM临时模拟权威声明草案.md`（已随请求函发出，改动会造成已发文书漂移）——三个载体只给**建议填法**，请 Owner 圈定后回填；
- 未创建任何 SIM 载体路径（`…/instances/sim/` 属 Wave 2+ 且须 `DESIGN_APPROVED`）；
- 未在 KERT 仓写任何文件（本环境只读）；
- 未记录 `QA_PASS`（开发/分析角色不得自签；且本包无实现可交付）；
- 未把任何场景标 `PASS`；未代签任何栏位。

## 5. 风险提示（给接手人）

| # | 风险 | 处置 |
|---|---|---|
| 1 | **O-D4-3**：CQ1/CQ2 夹具已把 EDWCRM / 集团登记系统**预置为来源**，若被当作基线即成立「隐式权威」 | 未签前只把这两个取值当候选；正例结论保持 `NOT_EVALUATED` |
| 2 | **O-D4-1**：`Party`/`Organization` 类级 A-Box 取值不可执行 | 请 Owner 落为分型级，或明确试点仅覆盖客户侧 |
| 3 | **O-D4-7**：集团族零具名源系统、零源合同 | D4 必须具名；不接受留空过 Wave 3 |
| 4 | **O-D4-2**：与 GK-KE `core.ExternalIdentifier` 未对齐 | 实施前须归一或显式映射，否则两套外部标识模型并存 |
| 5 | **O-D4-5**：freshness 阈值未定 ⇒ `PROJECTION_STALE` 目前为空转 | 请数据 Owner 按业务日粒度给定 |
| 6 | **O-D4-6**：SIM 产品身份载体前缀为占位根域 | Wave 2 拆分时同批修复 |

## 6. 一句话

**D4 的技术准备已到边界：8 术语候选、6 必填字段、1 份不生效合同、3 个载体建议、4 条退出台账项全部可判定且经变异复验；剩下的是数据 Owner 裁定与业务 Owner 会签，任何一方未签之前，投影合同不生效、CQ1/CQ2 保持 `NOT_EVALUATED`。**
