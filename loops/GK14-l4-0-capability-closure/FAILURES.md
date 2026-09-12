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

## FAIL-2026-09-12-06 派工偏差（我作为 TL 的编排错误）

- **现象**：我把 A1（WP06，需要**写文件**）派给了 `code-explorer` SubAgent，
  但该 SubAgent **工具集是只读的**（搜索/读取类），**无法落盘**。
  结果：SubAgent 耗费 242 次工具调用与 15 credits，产出全部留在消息里，**文件零落盘**。
- **性质**：**我的编排错误**，非 SubAgent 能力问题，也非模型缺陷。
- **重复性**：此前 WP01、WP03 也发生同样情况（SubAgent 返回文本未落盘）。
  **已发生 3 次，属系统性偏差，必须记录并纠正。**
- **根因**：我在派工时只描述"要产出什么"，**未确认执行者是否具备写权限**。
- **纠正措施（即刻生效）**：
  1. 需要**写文件**的任务：**不再派给只读 SubAgent**，由我直接执行，
     或派给具备写权限的执行角色。
  2. 派工前**先确认执行者工具集**是否覆盖任务所需的全部动作类型。
  3. 派工任务书中**显式声明**「本任务需要写文件」或「本任务只读」。
- **教训**：**"派出去"不等于"做完了"**。SubAgent 返回了一大段看起来完整的产出，
  若我不核实落盘，就会把"消息里的文本"误当成"已交付的制品"。
  **这与本项目历史上的"假绿"是同一类错误：把表象当成事实。**

## FAIL-2026-09-12-07 场景族跨越开发/验收集（A4 守卫自捕获）

- **现象**：`gk_ke_acceptance_pack.py` 首次运行即报
  `场景族跨越开发与验收集: ['SIM-FAM-A2','SIM-FAM-B2','SIM-FAM-N2']`。
- **性质**：**数据集生成器的真实设计缺陷**。我原先按 `(i-1)//5+1` 连续编号场景族，
  导致同一族既含调优案例也含验收案例 —— 这正是 §14.4 明令禁止的
  「同一故事换几个数字后同时进入开发和验收集」。
- **发现方式**：**A4 验收包的守卫自动捕获**，非人工发现。
- **处置**：场景族编号按调优分组拆分为 `-DEV` / `-HOLD` 两套前缀，
  使调优组与验收集在场景族上**不相交**；数据集重新生成，验收包复验 PASS。
- **教训**：评测集与开发集**同源**时，即使案例 ID 不同，
  只要底层故事相同，就退化为"只证明记住了故事"。
  这与 §16.3-12「评测自我确认」是同一类风险。

## FAIL-2026-09-12-08 指标定义 expectedColumn 指向错误（A2 门禁自捕获）

- **现象**：`gk_ke_metric_definitions_check.py` 报 19 项
  `声明 expectedColumn=REVENUE 但无可复算值`。
- **根因**：生成器把**指标常量名**（`REVENUE`）写入 `expectedColumn`，
  而数据集 v2 实际列名是 **camelCase**（`revenue`）。
- **性质**：我引入的错误。若门禁只校验"字段存在"而不实际重算，
  这 19 项会以"已定义"状态通过 —— **是典型的"有模板没内容"**。
- **处置**：修正为真实列名；对 5 项确实无对应列者（如本行代发覆盖人数、
  逾期本金金额）**如实标 `recomputeBlockedReason`**，不编造列名。
- **结果**：19 项定义中 **14 项可从真实数据复算**，5 项如实标注不可直接复算。
- **教训**：**"定义了指标"与"指标可复算"是两件事**；
  可复算性必须由**实际重算**证明，不能由字段齐备声明。
