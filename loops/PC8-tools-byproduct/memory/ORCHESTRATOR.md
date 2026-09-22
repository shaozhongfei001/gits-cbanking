# PC8-tools-byproduct｜Orchestrator tick log（append-only）

## Tick 0｜INITIALIZED

- Time: `2026-09-22T09:21:20.521101+00:00`
- Baton: `tech_lead / W0`
- State: `planned`

## Tick 1｜方案交付（2026-09-22T09:34:09+00:00）

- Baton: `tech_lead`；状态 `planned → in_progress`
- 交付：`docs/dispatch/PC8-工具链多产品化与可复现性方案-V1.0.md`（先方案后改码，未改任何代码）
- 实测发现（均带 `文件:行`）：
  - `F-PC8-01` `l10:154` 摄入时间取 wall clock ⇒ 跨日重跑新件+旧件残留；同日重跑字节不一致
  - `F-PC8-02` `l11:74` `PRODUCT_VERSION_SCOPE="version=2026.09.06.1"` 与**所有**卡目录版本（09.01.1 / 08.31.1）不匹配
  - `F-PC8-03` `l11:112-119` 族名硬编码为 `CASH_MANAGEMENT`；`field-policy.schema.json` 仅 2 实例 ⇒ **5 族无字段策略**
  - `F-PC8-04` `check_l10_sources.py:74-77` 强制 SV 文件数 == manifest ⇒ 重跑必须幂等重建（清理陈旧件）
- 结论：W2 障碍不是 4 个常量，而是**单族实现 + 合同面缺实例**；`T3` 已上报为 `B-5b`
- 下一步：T5（`--run-date`）→ T6（幂等重建，先快照）→ T1+T4（`--product`/`--all` + 版本派生）→ T2（族 fail-closed）

## Tick 2｜T6 实施 + 自我更正（2026-09-22T10:08:03+00:00）

- 更正 `F-PC8-01`：`now_cst()` **已支持 `SOURCE_DATE_EPOCH`**（8 脚本均支持）⇒ 确定性**已具备**，T5 零改造
  隔离副本实测：固定 epoch 连跑两次**逐字节一致**；换 epoch 重跑 **SV 34 vs manifest 17**（旧件残留成立）
- `T6` 已实施：`l10` 重建前清理 `SV-*.json`/`*.fragments.json`（只清这两类）
  实测：跨日重跑 PRUNE 34 → **SV 17 == manifest 17**；同 epoch 连跑仍逐字节一致（J1 未被破坏）
- 降级 `F-PC8-02`：常量 `2026.09.06.1` 与既有 Release `RLS-2026.09.06.1` 一致 ⇒ 语义待澄清，T4 挂起
- 新增 `F-PC8-05`：`check_l10_sources.py:151` 期望值 `DEMO==3` 与 registry 门禁 `EXPECTED_DEMO` **双点**，须单点化；
  **现在不改**（改成 17 会立即让 unified_gate 变红，须与跑 pipeline 同批）
- 新增 `T7`：跑 `l10` 后回填 registry §5.8「条款数」（现为 None，门禁 check_l10:117 会 FAIL）
- 真实仓 `02_work` **零变动**；unified_gate 保持绿

## Tick 3｜T1/T2 完成 + F-PC8-07 实证（2026-09-22T10:20:04+00:00）

- T1/T2 已实施（4 脚本，模块级 --product/--family/--all；族选择 fail-closed）
- 实测：默认参数下 SV/fragments 与真实仓**逐字节一致**；evidence-spans 仅 run 级 id 不同；
  `--family FINANCING` ⇒ **exit=1** + 明确 FAIL 文案；`--product PROD-SET-001` 在 l11/l12 均产出产物
- **F-PC8-07 实证（阻塞级）**：17 源下 `PROD-CM-001` 断言引用了 `SRC-CB-001`/`SRC-FIN-001`（跨族）证据
  根因：l11 不读 registry §5「被引用产品卡」列，对全部 fragments 无差别匹配 ⇒ 无源↔产品绑定
- 新增 `T8`（W2 强制前置）：登记驱动的合法源集合过滤 + fail-closed；本次 2 条串味样本作回归负例
- 结论：**先做 T8 再跑全链**；否则 13 卡产物是「看起来完整、实际串味」

## Tick 4｜T3 实施（Owner 批准 5 族实例）（2026-09-22T10:27:59+00:00）

- Owner 2026-09-22 批准 ① ⇒ `B-5b` 解除（授权新建 5 族字段策略实例）
- 事实更正：SETTLEMENT 既有实例 `FLD-SETTLEMENT-999` 是**反例**（PUBLIC_TRACK_REJECT）⇒ 缺正例的族为 5 个
- `field-policy.schema.json` examples 2 → 7（新增 5 族 POSITIVE）；采用**跨族通用槽位骨架**，
  **不添加族特有字段**（FieldSpec.fieldPath 只有语法 pattern 无 enum ⇒ 字段目录权威 = 批准的策略本身）
- `ownerApproved` **未翻真**（我不代签合规语义）；`pricing.serviceFee` 保留 `ownerDecisionRequired: true`
- 门禁：L02 41/41 PASS · check_contracts 14/14 PASS
- 隔离副本：FINANCING exit=0；`--all` **13 卡全部产出断言**；PROD-CM-001 字段集无增无缺
- **T8 仍是 W2 唯一硬前置**（F-PC8-07 未解）⇒ 先 T8 再跑全链

## Tick 5｜T8 实施并实证（2026-09-22T10:40:00+00:00）

- `l11` 新增 `load_source_product_binding()`：解析 registry 族表（§5.1–§5.7）「被引用产品卡」列，
  断言匹配前收窄到本产品合法源集合；无绑定 ⇒ SystemExit(1)
- 实测：PROD-CM-001 合法源 8 个、参与证据 49/136（剔除 87 条）；**串味 2 条 → 0 条（回归 PASS）**；
  断言 19 → 16；`--product PROD-XX-999` ⇒ exit=1；`--all` **13/13** 卡各打印 SCOPE
- 新增 `B-6`（Owner 口径）：§5.8 DEMO 行「无」 vs 族表绑定 —— 我取族表并在代码注释显式声明，非静默
- 新增 `F-PC8-08`（gits Java `ProductCardCatalogService.isInterpretable` 写死 PROD-CM-001，与自身注释不符）
- 新增 `F-PC8-09`（`l10` 只 glob `*.DEMO.md` ⇒ 9 份 REG 真实源从不入 fragments ⇒ `compliance.regulatoryBasis` 恒 UNKNOWN）
- 下一步：T10（修 Java 硬编码）+ T11（全链 13 卡 + T7 回填 + F-PC8-05 期望值同批）
