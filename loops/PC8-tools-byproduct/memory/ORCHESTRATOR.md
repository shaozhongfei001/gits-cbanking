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
