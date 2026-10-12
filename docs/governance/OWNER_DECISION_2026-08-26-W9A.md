# Owner Decision｜W9 验收范围锁定为 W9-A

| 字段 | 值 |
|---|---|
| Decision ID | OD-GITS-BANK-UX-W9A-2026-08-26 |
| Date | 2026-08-26 |
| Role | HUMAN_OWNER（会话确认：选 W9-A） |
| Recorded by | Tech Lead |
| Dispatch | `docs/dispatch/W9-gits-bank-uat-release.md` |
| Commit | `797f3ebd4a15422d844e0def08526916359d0e12` |
| Production ready | NO |
| Frozen | NO |
| UAT pass | NO |

## 决定

1. **W9 范围 = W9-A。** 验收对象是已交付的导航壳、C0 查询、C2 禁用/降级说明。不是 V3.2 正式 Need / G0–G5 / AccountPlan / 离线缓存。
2. **不启动 W9-B。** 不因此开 C3 合同 Loop，不改 authority source。
3. **灰按钮不是本波缺陷。** 主动作禁用且写明原因与解除路径，视为诚实降级。
4. **本签署不是** 264 PASS、不是 44/44 功能完成、不是生产发布。不得勾选 `PRODUCTION_READY` / `FROZEN`。

## 明确未批准

- `UAT_PASS`（范围已锁定；人类 UAT 签署仍未做）
- `FROZEN` / `PRODUCTION_READY`
- 合并入 `main`
- CC2 或 C3 合同源变更
