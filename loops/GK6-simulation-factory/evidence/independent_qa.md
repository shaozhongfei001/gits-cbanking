# Independent QA Attestation — GK6-simulation-factory (CR-07, T30–T33)

| 字段 | 值 |
|---|---|
| Loop | `GK6-simulation-factory` |
| 需求/合同 | CR-07《模拟数据合同》v1.0；验收矩阵 T30/T31/T32/T33 |
| QA actor | `gk6-qa`（独立 QA，与 implementation actor `gk6-pilot` 相互独立） |
| Session | `qa-gk6-formal-001` |
| Worktree | `/home/szf/dev/gk-wt-L6`（分支 `feature/GK-KE-L6`） |
| 基线 commit | `c7017b1` |
| 实现 commit | `c0d6dac`（`feat(GK6): L6 simulation factory CR-07 T30-T33`） |
| 复核时间(UTC) | 2026-09-10T15:33:41Z |
| 结论 | **QA_PASS**（离线工厂范围；见“范围声明”） |

## 0. 独立性声明

- 本 QA 未修改任何实现/合同代码；所有负例实验均在 `/tmp` 下的副本进行（`/tmp/qa-g6-mut`、`/tmp/qa-g6-leak`），worktree 内仅新增本 Loop 的 evidence/QA 记录文件。
- 全部 gate 命令由 QA 从 worktree 根独立重跑，未采信实现者日志。
- 真值复算使用 QA 自写只读脚本 `/tmp/qa_g6_independent_check.py`（Decimal 精确计算，不调用包内校验器），输出见 `qa-independent-truth-check-20260910T153341Z.log`：**42/42 PASS**。

## 1. Gate 独立重跑（全部 exit=0）

| Gate | 命令（worktree 根） | 结果 | QA 证据日志 |
|---|---|---|---|
| contract_check | `make generate && make check` | PASS（generate 无漂移；check exit 0） | `qa-contract_check-20260910T153341Z.log` |
| vendor_factory | `python3 tools/gk-ke-simulation/build_simulation.py` ×2 | PASS，两次产物 sha256 逐字节一致 | `qa-vendor_factory-build1/2-*.log`、`qa-vendor_factory-sha256-run1/2-*.txt`（`diff` 无差异） |
| validate_dataset | `python3 tools/gk-ke-simulation/validate_package.py` | PASS，**117/117** checks | `qa-validate_dataset-20260910T153341Z.log` |
| isolation_oracle | `python3 -m unittest tests.tooling.test_gk_ke_simulation -v` | PASS，**11 tests OK** | `qa-isolation_oracle-20260910T153341Z.log` |
| tooling_test | `make tooling-test` | PASS，Ran 11 tests OK | `qa-tooling_test-20260910T153341Z.log` |
| security_check | `make security-check` | PASS（gitleaks 无泄露；detect-secrets baseline 审计完成） | `qa-security_check-20260910T153341Z.log` |

确定性：两次 `build_simulation.py` 后对全部 csv/json/jsonl/md/sql 产物的 sha256 清单 `diff` 为空；`git status` 重写后无漂移（仅 `__pycache__` 被忽略）。

## 2. T30 真值独立复算（42 项断言全过）

计数（直接数 CSV 数据行/文档文件）：

| 资产 | 合同要求 | 实测 |
|---|---|---|
| 客户 | 12 | 12 |
| 账户 | 24 | 24 |
| 产品 | 6 | 6 |
| 日历 | 30 天（2026-09-01..09-30，工作日 22） | 30，工作日 22 |
| 交易 | 144 | 144 |
| 分录 | 288 | 288 |
| 日余额 | 720（24×30） | 720 |
| 授信 | 12 | 12 |
| 持有 | 12 | 12 |
| 文档 | 18 | 18 |
| 机构 | 2（同名客户分属不同机构） | 2 |

关键真值（Decimal 独立计算）：

- **C001 日均存款 = 2,983,333.33 CNY**：两账户 30 天 closing 之和 89,500,000.00 ÷ 30 = 2,983,333.33（HALF_UP），与 `oracles/expected.json` 一致；C001 两账户期初合计 3,000,000.00。
- **复式记账**：144 笔交易各 2 条分录，方向恰为 DEBIT/CREDIT，金额相等、方向相反，且分录币种 = 交易币种 = 账户币种。
- **余额滚动**：逐日逐账户验证 `closing = opening + ΣsignedAmount`、`netMovement = ΣsignedAmount`；次日 `opening = 前日 closing`；首日 opening = 账户 `openingBalance`；(账户,日期) 唯一。
- **授信**：全部 `0 ≤ used ≤ approved`；抽样 SIM-F001 = 20,000,000.00 / 12,000,000.00。
- 金额列为两位小数字面量文本，无浮点伪影；全部 ID 以 `SIM-` 开头；FK 闭包（账户→客户、客户→机构、交易→账户、持有→客户/产品、分录→交易）完整。

## 3. T31 证据链与版本

- `dataset_manifest.json` 列出 42 个文件，QA 逐一重算 sha256，**0 失配**；`simulationOnly=true`、`snapshotId=SIM-SNAPSHOT-2026-09-01`、`externalModelApiCalled=false`、`generationMethod=deterministic_stdlib_python`。
- `source_catalog.json` 18 条语料，contentHash 逐一重算 0 失配，全部 `simulationOnly=true`。
- 14 个 schema 正负例：14 正例全部 valid、28 负例全部 invalid（validator 输出 14/14、28/28；unittest 独立复跑一致）。
- 图引用闭包：12 nodes / 12 edges，每条边 source/target 均存在；12 条 HOLDS_PRODUCT 边与 holdings 12 行一一对应。
- **提及≠持有**：SIM-VISIT-001 记录 C001“可能需要 3000 万”（FORECAST 陈述 SIM-CLAIM-001），但 holdings 中 C001 仅持有 SIM-P001，30M 意向未生成任何持有/授信事实。
- **同名不同身份**：SIM-C001（SIM-O01）与 SIM-C011（SIM-O02）同名“模拟星澜精密部件有限公司”，归属不同机构；SIM-CLAIM-003 明确否认身份与新增贷款计划。
- **版本族**：SIM-P001-SUPPLEMENT 存在 0.9.0 与 1.0.0 两版，语料清单按 sourceId+sourceVersion 分别登记。
- 18/18 文档含“虚构模拟材料”声明。

## 4. T32 人工控制（负例独立验证）

QA 直接调用 `guards.py` 对 10 个负例做变异测试，全部以稳定错误码拒绝（日志 `qa-guard-negatives-20260910T153341Z.log`）：

- 生产写能力（sideEffect=PRODUCTION_WRITE）→ `SIDE_EFFECT_NOT_READ_ONLY`
- productionProbePassed=true → `PRODUCTION_PROBE_NOT_FALSE`
- 自批（reviewer==author）→ `SELF_APPROVAL`；isRealApproval=true → `REAL_APPROVAL_FLAG_SET`
- 陈旧 targetVersion → `STALE_TARGET_VERSION`
- FORECAST 被标 certainty/confirmed → `FORECAST_TREATED_AS_FACT`；币种未确认 → `CURRENCY_UNCONFIRMED`
- 客户端注入授权参数 → `AUTH_PARAM_CLIENT_CONTROLLED`
- 缺 simulationOnly → `SIMULATION_ONLY_NOT_TRUE`；非 SIM- ID → `NON_SIM_ID`

另在 `/tmp/qa-g6-mut` 副本删除语料条目的 simulationOnly 后运行 `validate_package.py`，exit=1 被拒。真实夹具（capability/confirmation/query registry）全部通过。

## 5. T33 模拟边界与 Oracle 隔离

- 全部产物 `simulationOnly=true`（manifest、18 语料、4 statements、capability、confirmation、query registry），全部业务 ID `SIM-` 前缀。
- `oracles/expected.json` 仅存在于 `simulation/oracles/`；`source_catalog.json`、`registry_snapshot.json`、graph（nodes/edges）、documents 中均无 oracle 路径或真值字符串（QA grep + 内容扫描）。
- 独立泄漏负例：在 `/tmp/qa-g6-leak` 副本把 oracle 真值 `2983333.33` 追加进某文档，`guard_oracle_isolation` 立即拒绝（`ORACLE_LEAK_IN_CORPUS`）；真实包扫描通过。
- `build_simulation.py` 源码不引用 oracles（grep 无命中），构建器仅 import csv/hashlib/json/datetime/decimal/pathlib，无 random（确定性）、无网络/模型/DB。
- `validate_package.py` 的 sqlite3 仅用于 `:memory:` 验证 avg_deposit.sql 模板可执行，无磁盘 DB 写入。

## 6. 合同纪律与红线

- `git diff --stat c7017b1 HEAD -- specs generated` = **空**（证据 `qa-contract-diff-20260910T153341Z.txt`）；变更仅限 `tools/gk-ke-simulation/`、`tests/tooling/test_gk_ke_simulation.py` 与本 Loop 目录。
- 无真实客户/机构映射（全部 SIM- 合成名）、无凭据（security-check 通过）、无网络/LLM 调用（manifest 声明 externalModelApiCalled=false，源码 grep 无 socket/requests/urllib/openai 等）、无 DB 写入。
- 实现者 FAILURES.md 记录的 isolation_oracle 首轮失败（11 负例误判 valid）已在同一 gate 第 2 次尝试修复并经 QA 独立复跑确认，符合“失败先记录”。

## 7. 范围声明（不降低本 Loop 结论）

验收矩阵 T30–T33 标注 `PLANNED_NOT_EXECUTED` 且要求“服务验证/真实服务探针/生产动作”。本 Loop 经 Owner 明确豁免为**离线工厂**范围（LOOP scope: offline factory；exit criteria 明确“不要求服务运行、不要求生产探针、不要求真实人工审批”）。因此本次 QA_PASS 仅覆盖：确定性合成、真值复算、证据链/版本、人工控制负例、模拟边界与 oracle 隔离的**离线**证据；REAL_E2E_PASS、生产探针、真实人工审批、BUSINESS_SIGNED 仍为 do_not_start，须后续独立 Loop 承接，不得据本次结论宣称生产就绪。

## 8. 复核产物清单（本目录 qa-* 前缀）

- `qa-contract_check-20260910T153341Z.log`
- `qa-vendor_factory-build1-20260910T153341Z.log` / `build2` / `sha256-run1` / `sha256-run2`
- `qa-validate_dataset-20260910T153341Z.log`
- `qa-isolation_oracle-20260910T153341Z.log`
- `qa-tooling_test-20260910T153341Z.log`
- `qa-security_check-20260910T153341Z.log`
- `qa-independent-truth-check-20260910T153341Z.log`（42/42）
- `qa-guard-negatives-20260910T153341Z.log`（10 负例全拒 + 真实夹具通过）
- `qa-contract-diff-20260910T153341Z.txt`（specs/generated diff 为空 + 全变更文件清单）
