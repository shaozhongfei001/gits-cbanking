# GK14-l4-0-capability-closure｜Failures（append-only）

失败必须在修改实现之前由 `scripts/record_gate.py`追加。每项至少包含时间、Gate、命令、退出码、证据文件、初步分类和下一动作；修复后追加根因、变更SHA与原命令重跑结果，不覆盖原记录。

## FAIL-2026-09-12-04 时间泄漏（生成器自捕获，已修复）

- **现象**：数据集 v2 首次生成时，`monthly_business_observation` 的 2026-08 期
  `availableAt=2026-09-16` **晚于** `asOf=2026-09-12`，但该期仍带有完整业务值。
- **性质**：这正是建议书 §12.4 要防的时间泄漏——用任务截止后才会发布的资料冒充当期事实。
- **发现方式**：生成器内置 P-6 守卫（`verify_time_leakage`）在写入后校验时**自动拦截**，
  非人工发现。守卫首次运行即报错，证明断言非空转。
- **处置**：
  1. 未完结期间（`pub > asOf`）强制将所有业务值置空；
  2. `valueState` 置 `UNKNOWN`、`coverage` 置 `PARTIAL_LATEST_PERIOD`、
     `freshness` 置 `NOT_YET_PUBLISHED`、`retrievalOutcome` 置 `PARTIAL`、
     新增 `unavailableReason=MTD_NOT_CLOSED`；
  3. 守卫收紧为：`availableAt > asOf` 的行**必须**同时满足
     `isLatestIncompletePeriod=true` + `valueState=UNKNOWN` + 业务值全空，
     否则判 FAIL。仅比时间戳不再判失败。
- **复现**：`python3 scripts/generate_gk_ke_dataset_v2.py`（现为 PASS）
- **证据**：`observation/monthly_business_observation.csv` 末行为
  `2026-08-01 avail=2026-09-16 within=False state=UNKNOWN revenue=NULL`
- **教训**：若不设此守卫，2026-08 未完结月度会以完整口径进入访前包，
  等价于声称"本月已完成实际数据"。与既有夹具被误用为当月实际值的风险同源。

## FAIL-2026-09-12-05 我引入的契约违规（能力注册中心）

- **现象**：`python3 scripts/gk_ke_l2_2_registry_tests.py` FAIL：
  - 9 项能力 `probeStatus='NOT_RUN'`，**非法枚举**（合法值仅 `PASSED|FAILED|NOT_PROBED`）
  - 9 项缺 6 个必填字段：`inputSchemaRef / outputSchemaRef / preconditions /
    budget / timeoutMs / idempotencyPolicy`
- **根因**：我在 R-1 修复时**只看了 `map_spec.json` 的自由文本**，
  未核对 `gk_ke_l2_2_registry_tests.py` 定义的 `REQUIRED_FIELDS` 与枚举约束。
- **为什么首次未被发现**：该测试**未接入 `make check`**，
  故我此前"全绿"的结论**不覆盖该约束**——这是我的验证盲区。
- **性质**：**我引入的**缺陷，非既有缺陷。R-1 的修复动作本身制造了新的契约违规。
- **处置**：
  1. `NOT_RUN` → `NOT_PROBED`（合枚举）
  2. 为 9 项补齐 6 个必填字段；未固定的值如实标 `PENDING` / `NOT_FIXED`，
     **不编造 schema 引用**
- **教训（值得记住）**：**"门禁全绿"不等于"契约合规"**，取决于门禁覆盖面。
  仅凭 `make check` PASS 就宣称合规，本身就是一种过度声明。
