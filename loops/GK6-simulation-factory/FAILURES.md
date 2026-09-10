# GK6-simulation-factory｜Failures（append-only）

失败必须在修改实现之前由 `scripts/record_gate.py`追加。每项至少包含时间、Gate、命令、退出码、证据文件、初步分类和下一动作；修复后追加根因、变更SHA与原命令重跑结果，不覆盖原记录。

## 20260910T150958Z｜isolation_oracle

- Command: `python3 -m unittest tests.tooling.test_gk_ke_simulation -v`
- Exit: `1`
- Evidence: `loops/GK6-simulation-factory/evidence/isolation_oracle-20260910T150958Z.log`
- Classification: `PENDING_ROOT_CAUSE`
- Next: diagnose, record root cause, fix, rerun the original gate.

### 根因与修复（20260910T1520Z）

- Root cause: TDD 正常红——G4 命令引用的 `tests/tooling/test_gk_ke_simulation.py` 尚未创建（ModuleNotFoundError），命令本身正确。
- Fix: 新增 `tools/gk-ke-simulation/guards.py`（T32 人工控制闸 + T33 模拟边界/oracle 隔离守卫，纯 stdlib）与 `tests/tooling/test_gk_ke_simulation.py`（11 项：5 个 T32 负例、3 个 T33 负例、基线正例、确定性重构建）。
- Rerun: 原命令 `python3 -m unittest tests.tooling.test_gk_ke_simulation -v` → Ran 11, OK；record_gate isolation_oracle → PASS。
