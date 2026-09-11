# GK7-l3-2-review-release｜Failures（append-only）

失败必须在修改实现之前由 `scripts/record_gate.py`追加。每项至少包含时间、Gate、命令、退出码、证据文件、初步分类和下一动作；修复后追加根因、变更SHA与原命令重跑结果，不覆盖原记录。
# GK7-l3-2-review-release｜Failures（append-only）

## FAIL-2026-09-12-12: L3-2 五类拒绝断言全部空转（独立 QA 变异测试发现）

- **时间**：2026-09-12（Wave D1，Independent QA 审计）
- **Gate**：`l3_2_release_tests`
- **命令**：变异测试 —— 同时禁用「半发布」与「自审自批」检查后重跑
- **退出码**：0（**期望非 0**）
- **分类**：**MAJOR**（C08 L3-2 明确要求的三项测试全部未真实验证）
- **现象**：禁用两类检查后测试**仍 PASS**。
- **根因**：全部夹具都是**合规正例** ——
  `projections` 全部 ready 或明确 `required=false`、`decisions` 无自审、
  审批无过期、`runtimeStates` 无 REVOKED-仍可检索、`rollbacks` 未指向撤销版本、
  `purposeFlags` 未升级。故**所有拒绝分支从未进入**，断言恒真。
- **合规影响**：C08 L3-2 退出标准原文为「人工更正可追踪；**审批后改字阻断**；
  **半发布/撤销测试**」。三项均为**否定式**要求，只测正例**不可能**证明其成立。
  这是本程序反复出现的同一类缺陷模式（见 FAIL-2026-09-12-02 / -07 / -11）。
- **下一动作**：为每类拒绝建立**独立的违规夹具**，使断言具备真实触发路径；
  并要求「违规夹具必须被拒」写成 fail-closed 断言（无夹具即失败）。

### 修复记录（第 1 轮，已闭环）

- **修复**：新增 `violations` 段（7 类违规），每类含 `expectedError`：
  `CONTENT_CHANGED_AFTER_APPROVAL` / `SELF_APPROVAL` / `EXPIRED_APPROVAL_COUNTED` /
  `HALF_PUBLISH` / `REVOKED_STILL_SEARCHABLE` / `ROLLBACK_TO_REVOKED` /
  `PURPOSE_FLAG_SILENT_UPGRADE`。
  测试改为对**违规夹具执行同一套判定函数**，要求**必须被拒**；
  并断言违规夹具集合覆盖全部 7 类（缺一即失败）。
- **验证（变异必须失败）**：再次禁用半发布/自审检查 → 测试 **FAIL**（违规夹具未被拒）。
- **验证（恢复必须通过）**：恢复 → 测试 **PASS**（正例通过 + 7 类违规全被拒）。
- **状态**：CLOSED（1 轮）。
