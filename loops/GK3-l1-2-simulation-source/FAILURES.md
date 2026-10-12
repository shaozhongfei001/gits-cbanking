# GK3-l1-2-simulation-source｜Failures（append-only）

## FAIL-2026-09-12-06: L1-2 日均公式错误 + 分录列名不符（C08 L1-2 退出标准）

- **时间**：2026-09-12（Wave B2，Feature Pilot）
- **Gate**：`l1_2_simulation_tests`
- **命令**：`python3 scripts/gk_ke_l1_2_simulation_tests.py`
- **退出码**：1（先 KeyError，后校验失败）
- **分类**：**MAJOR**（C001 日均真值不符 + 脚本崩溃）
- **现象（两个独立缺陷）**：
  1. `KeyError: 'debitCredit'` —— 脚本引用了不存在的列名，实际列为 `direction`。
  2. C001 日均算得 **1,491,666.67**，恰为期望值 **2,983,333.33** 的**一半**。
- **根因**：
  1. 未核对封版 CSV 的真实列名（`direction` 而非 `debitCredit`）。
  2. **公式错误**：我把两个账户的**所有行**相加后除以**总行数**（2 账户 × 30 天 = 60）。
     权威公式（`tools/verify_simulation.py:check_c001_avg_deposit`）是
     **先按业务日跨账户汇总（30 个日合计），再除以区间天数 30**。
     我误把"行数"当"天数"，导致分母翻倍 → 结果减半。
- **合规影响**：C001 = 2,983,333.33 是 C07 §5 与 C08 L1-2 明确的**数学真值**，
  且是 L2-1 指标复算的唯一基准。公式错误会污染下游全部指标验收。
- **下一动作**：改为权威公式；核对全部列名；重跑。

### 修复记录（第 1 轮，已闭环）

- **修复**：
  1. `gk_ke_l1_2_simulation_tests.py`：借贷平衡改用 `direction` + 按 DEBIT/CREDIT 分别求和比对。
  2. 两处（生成器 + 测试）C001 公式改为**先按 `businessDate` 跨账户汇总，再除以 `periodDays=30`**；
     并从 manifest 读取 `c001PeriodDays` 而非硬编码行数。
  3. manifest 新增 `c001PeriodDays` / `c001AccountCount` 供测试交叉核对。
- **验证**：C001 日均 = **2,983,333.33**（`matches=True`）；7 项一致性检查全通过；
  负例 7 个均带 `expectedError`。
- **状态**：CLOSED（1 轮）。
