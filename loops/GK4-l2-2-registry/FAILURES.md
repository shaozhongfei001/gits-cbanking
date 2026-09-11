# GK4-l2-2-registry｜Failures（append-only）

失败必须在修改实现之前由 `scripts/record_gate.py`追加。每项至少包含时间、Gate、命令、退出码、证据文件、初步分类和下一动作；修复后追加根因、变更SHA与原命令重跑结果，不覆盖原记录。
# GK4-l2-2-registry｜Failures（append-only）

## FAIL-2026-09-12-07: L2-2 CAS 并发断言空转（独立 QA 变异测试发现）

- **时间**：2026-09-12（Wave B3，Independent QA 审计）
- **Gate**：`l2_2_registry_tests`
- **命令**：变异测试 —— 把 CAS 冲突检查改为 `if False:` 后重跑
  `python3 scripts/gk_ke_l2_2_registry_tests.py`
- **退出码**：0（**期望非 0**）
- **分类**：**MAJOR**（C08 L2-2 明确要求的「并发更新 CAS 测试」为**空转**）
- **现象**：禁用 CAS 冲突检查后测试**仍报 PASS**。说明该断言对现有数据从未真正触发。
- **根因**：CAS 检查的触发条件是「`casExpectedVersion != currentVersion` **且** `casAccepted == true`」。
  我的注册数据中**所有条目**的 `casExpectedVersion` 都等于 `currentVersion`，
  因此该分支**从未进入**，断言恒真（noop）。属"正例数据未包含触发路径"的经典空转。
- **合规影响**：C08 L2-2 退出标准原文要求「**并发更新 CAS 测试**」。
  空转断言意味着并发冲突保护**未被验证**，无法据以声称满足退出标准。
- **下一动作**：在注册数据中新增**故意 CAS 冲突**的负例夹具
  （`casExpectedVersion != currentVersion` 且 `casAccepted=true`），
  使断言具备真实触发路径；重跑变异测试必须 FAIL。

### 修复记录（第 1 轮，已闭环）

- **修复**：
  1. `_gen_gk_ke_l2_2_registry.py` 新增 `SIM-ASSET-CAS-CONFLICT` 条目：
     `currentVersion=2.0.0`、`casExpectedVersion=1.0.0`、`casAccepted=true`，并声明 `expectedError=CAS_STALE_VERSION_ACCEPTED`。
  2. 测试新增 `expectedError` 感知：带 `expectedError` 的条目**必须**被对应检查拒绝，
     否则计入失败（与负例同一 fail-closed 口径）。
  3. 正例条目保持 `casExpectedVersion == currentVersion`（不误报）。
- **验证（变异必须失败）**：再次把 CAS 检查改为 `if False:` → 测试 **FAIL**（冲突条目未被拒）。
- **验证（恢复必须通过）**：恢复检查 → 测试 **PASS**。
- **状态**：CLOSED（1 轮）。
