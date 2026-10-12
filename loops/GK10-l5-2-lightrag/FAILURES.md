# GK10-l5-2-lightrag｜Failures（append-only）

失败必须在修改实现之前由 `scripts/record_gate.py`追加。每项至少包含时间、Gate、命令、退出码、证据文件、初步分类和下一动作；修复后追加根因、变更SHA与原命令重跑结果，不覆盖原记录。

---

## FAIL-2026-09-12-16: L5-2 门槛单项仍可被绕过（全程序变异回归暴露）

- **时间**：2026-09-12（Wave F 后，全程序变异回归 `scripts/gk_ke_mutation_regression.py`）
- **Gate**：`l5_2_lightrag_tests`
- **命令**：变异回归——把 `improvement_at_least_10pp` 判定硬编码为 `True`
- **退出码**：0（**期望非 0**）→ 回归报 `L5-2: MUTATION NOT CAUGHT`
- **分类**：**MAJOR**（门槛单项无独立否决力 → 未来若 C-vs-B 恰好达标而其它项未达，
  或反之，结论可能错误）
- **根因**：`gate_passed = all(checks.values())`。当**多项**同时不满足时
  （本例 4 项不满足），单独把某**一项**改为 `True` **不改变** `all()` 的结果，
  因此变异未被捕获。即**各项缺独立否决力的证明**。
- **合规影响**：C05 五项门槛必须**各自**具备否决力；否则"门槛判定正确"这一结论
  依赖于"恰好同时多项不满足"的偶然，不是结构性保证。
- **下一动作**：为每项门槛建立**独立否决性测试**：
  构造一个"全部满足"的夹具，逐项注入违规，要求 gate **必须**失败。

### 修复记录（第 1 轮，已闭环）

- **修复**：测试新增 `fully_passing` 夹具（须通过 gate）+ 逐项注入违规
  （`criticalNegativeFailures` / `accuracyC` / `criticalRegressions` /
  `ownerAcceptedCostValue`），每项注入后 gate **必须**失败；
  若某项注入后仍通过 → 报 `threshold <key> is ineffective`。
- **验证（变异必须失败）**：硬编码 `True` → 测试 **FAIL**（该项无否决力被检出）。
- **验证（恢复必须通过）**：恢复 → 测试 **PASS**。
- **全程序回归**：`gk-ke-mutation-regression: PASS (10/10 mutations caught)`。
- **状态**：CLOSED（1 轮）。
