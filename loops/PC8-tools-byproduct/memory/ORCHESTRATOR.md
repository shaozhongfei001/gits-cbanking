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
