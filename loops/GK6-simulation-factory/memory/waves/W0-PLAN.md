# W0｜Plan

## Goal

把候选包的确定性模拟银行数据工厂落地到仓内 `tools/gk-ke-simulation/`，满足 T30/T31/T32/T33。不调用外部 LLM、不写真实数据库、不改 `specs/` 与 `generated/`。

## 权威来源（开工必读）

- 数据合同：`/home/szf/dev/gits-kert-docs/dd/GK-KE-CONTRACT-V1.0/contracts/C07_模拟数据合同.md`
- 验收矩阵：`/home/szf/dev/gits-kert-docs/dd/GK-KE-CONTRACT-V1.0/acceptance/验收矩阵.csv`（T30–T33）
- 候选实现（搬迁源，勿直接引用仓库外路径作为运行依赖）：
  - `tools/build_simulation.py`、`tools/validate_package.py`
  - `simulation/`（seed_scenarios、tables/*.csv、graph/*.jsonl、oracles/expected.json、documents、statements、*fixture*.json、dataset_manifest.json）
  - `schemas/`（validate 用 jsonschema 校验）

## 落点与搬迁（Tech Lead 已裁决）

- 新建 `tools/gk-ke-simulation/`，自包含：
  - `build_simulation.py`、`validate_package.py`
  - `simulation/`（整目录数据与种子）
  - `schemas/`（工厂本地校验所需 schema 副本；这是工具自带校验，**不是** `specs/` 受控合同，禁止与 `generated/` 混淆）
- 候选工具用 `ROOT = Path(__file__).resolve().parents[1]` 定位包根；搬迁后目录层级变化需校正 ROOT/相对路径，确保从 worktree 根执行 `python3 tools/gk-ke-simulation/build_simulation.py` 可运行。
- 单测放 `tests/tooling/test_gk_ke_simulation.py`（对齐现有 `tests/tooling` 约定，纯 stdlib + jsonschema）。
- `validate_package.py` 依赖 `jsonschema`：确认系统 python3 是否可用；不可用则在脚本中给出清晰跳过/依赖说明，或用 stdlib 实现最小校验。优先不引入网络安装。

## 任务分解

1. 搬迁并校正路径，使 build/validate 可从仓根运行；产物落在 `tools/gk-ke-simulation/simulation/`。
2. **T30 编译器确定性**：只读固定种子/原文，重建 12 客户/24 账户/6 产品/30 天日历/144 事件/288 分录/720 日余额/12 授信/12 持有/18 文档 + 图投影 + oracles + manifest；重跑字节稳定（固定 snapshotId）。
3. **T30/T31 校验器**：字段结构、主外键闭包、每事件同币借贷相等反向、`closing=opening+ΣsignedAmount`、次日 opening=前日 closing、日均真值（C001=2,983,333.33 CNY）、文档/图引用存在、提及≠持有。
4. **T32 隔离**：负例——缺 `simulationOnly` 或非 `SIM-` 前缀被拒；生产动作/正常消费路径拒绝模拟数据；移除 simulationOnly 不改写为生产事实。
5. **T33 oracle 防泄漏**：oracles 不进检索语料清单；按场景家族/文档版本族分割；负例集 `expectedError` 声明且不污染正常快照。
6. 接入 `make tooling-test`（tests/tooling 被 unittest discover）。

## Gates（唯一命令源见 LOOP.yaml）

contract_check → vendor_factory → validate_dataset → isolation_oracle → tooling_test → security_check

## 红线

- 禁止改 `specs/`、`generated/`；禁止 `git add .`；失败先写本 Loop `FAILURES.md` 再修。
- 全部产物 `simulationOnly=true`、ID `SIM-` 前缀；不得出现真实客户/机构映射或凭据。
- 不调用模型/网络；不写 DB；oracle 仅作离线断言，不进检索。
- 环境：python3 为系统 3.10（勿依赖 3.14 专有语法）。
