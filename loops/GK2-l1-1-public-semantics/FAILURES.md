# GK2-l1-1-public-semantics｜Failures（append-only）

## FAIL-2026-09-12-05: L1-1 同名异义 / 破坏变更 两类必测未被拒（C08 指定退出条件）

- **时间**：2026-09-12（Wave B1，Feature Pilot）
- **Gate**：`l1_1_semantics_tests`
- **命令**：`python3 scripts/gk_ke_l1_1_semantics_tests.py`
- **退出码**：1
- **分类**：**MAJOR**（C08 L1-1 明确点名的两类测试未生效）
- **现象**：
  ```
  [3] SemanticPackage_homonym.json: negative NOT rejected (HOMONYM_CONFLICT)
  [3] SemanticPackage_semantic_fork.json: negative NOT rejected (SHARED_TYPE_FORKED)
  ```
- **根因**：JSON Schema 2020-12 **无法直接表达**
  （a）数组内 `types[].typeId` 的**跨项唯一性**（同名异义检测）；
  （b）「共享类型被复制后改义」这一**跨类型集合的语义判定**（破坏变更检测）。
  原 schema 仅约束单项结构，故两类负例被放行。
- **合规影响**：C08 L1-1 退出标准原文要求「**同名异义、破坏变更、身份误并测试通过**」——
  前两者在 schema 层无法单独表达，须引入**包级语义校验**。
- **下一动作**：新增包级语义规范文件（`x-gk-ke-package-invariants`）+ 在测试中实现真值检查；
  schema 增加结构级护栏（typeId 唯一由校验器保证，schema 侧声明不变式）。

### 修复记录（第 1 轮，已闭环）

- **修复**：
  1. schema 增加 `x-gk-ke-package-invariants`（机器可读不变式声明：`TYPEID_UNIQUE`、`SHARED_TYPE_NOT_FORKED`、`NO_IDENTITY_MERGE_BY_NAME`）。
  2. 测试脚本实现 `check_package_invariants()` 真值校验：
     - `TYPEID_UNIQUE`：同 `typeId` 出现 >1 次即拒绝（同名异义）
     - `SHARED_TYPE_NOT_FORKED`：`origin=DOMAIN` 的类型**不得**占用 `core.` 前缀命名空间（复制改义）
     - `NO_IDENTITY_MERGE_BY_NAME`：`nameSubstitutionForbidden` 必须为 true
  3. 负例新增 `expect_invariant` 字段，测试据此断言**由不变式而非 schema** 拒绝。
- **验证**：两类负例由不变式路径拒绝；正例与域包正例通过；其余 8 类负例 schema 路径拒绝。
- **状态**：CLOSED（1 轮）。


失败必须在修改实现之前由 `scripts/record_gate.py`追加。每项至少包含时间、Gate、命令、退出码、证据文件、初步分类和下一动作；修复后追加根因、变更SHA与原命令重跑结果，不覆盖原记录。
