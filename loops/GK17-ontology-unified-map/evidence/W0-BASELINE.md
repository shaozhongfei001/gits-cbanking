# W0 基线快照（GK17 动手前）

> 目的：**把既有真实状态钉死**，使后续任何红灯都能被判定"既有"还是"本 Loop 引入"。
> 采集时间：2026-09-15｜采集者：`tech_lead`｜HEAD：`b892b88`（自 `edc4a55` 起，**本体/语义相关代码未再改动**）

---

## 1. 采集结果（全部串行执行）

| # | 项 | 命令 | 结果 | 结论 |
|---|---|---|---|---|
| 1 | 合同生成 | `make generate` | exit 0，`contract-generate: PASS` | ✅ 绿 |
| 2 | 统一门禁 | `make check` | exit 0，**22/23** | ✅ 绿（含 1 项无法判定） |
| 3 | GK 门禁 | `python3 scripts/run_gates.py` | **22/23**，耗时 4.0s，**INTEGRITY FAILURES 为空** | ✅ 完整 |
| 4 | 本体装载 | `./mvnw -pl apps/api test -Dtest=MechanismE2eIT -DskipITs=false` | **1 test / 0 failure**（真实 Jena 加载 OWL + SHACL 校验） | ✅ 绿 |
| 5 | 后端测试 | `./mvnw -pl apps/api -am test -DskipITs` | **600 tests / 0 failure / 0 error / 4 skipped，BUILD SUCCESS** | ✅ 绿 |
| 6 | 前端类型 | `npx vue-tsc --noEmit` | **exit 0，0 错误** | ✅ 绿 |
| 7 | 前端测试 | `npx vitest --run` | **63 文件 / 342 测试全通过** | ✅ 绿 |
| 8 | Loop 合规 | `python3 scripts/loop_guard.py --loop GK17-ontology-unified-map` | **PASS** | ✅ 绿 |
| 9 | 实例棘轮 | `python3 scripts/loop_guard.py --instances-check` | **59/59 合规**，无新增违规，基线冻结 0 | ✅ 绿 |

## 2. 既有红灯（**不是本 Loop 引入，也不由本 Loop 负责收口**）

| 项 | 状态 | 说明 |
|---|---|---|
| `semantic-consumption` | **READINESS NOT MET** | 独立判定结论，TL **不得代判**；本 Loop 的 V1–V4 是**新增证据**，不改变该判定 |
| `gate-injection-tests` | **INCONCLUSIVE** | 覆盖不完整（`INCONCLUSIVE ≠ 通过`），**不得计入通过** |
| Gate 注入覆盖 | 18 项已设计 / 仍有无负例门禁 | 本 Loop 的 W5 **新增门禁必须附变异负例** |
| `contract-check` 覆盖盲区 | 已登记（`FAIL-2026-09-14-01`） | 门禁**不检"已实现未登记合同"的端点**；本 Loop W5 不负责修，但**不得加重** |

## 3. 跨会话事实（编排须知道）

- 自 `edc4a55` 以来，**另一执行者**提交了 `82b70b4`（`Dockerfile` + `.github/workflows/ci.yml` + `scripts/check_dockerfile_module_copies.py`）。
  该改动**与本 Loop 的 include 范围不重叠**；双方均按显式路径提交。
- 本 Loop 的单写者路径：`specs/semantic/`、`specs/knowledge-architecture/`、`generated/`、Loop 记忆。

## 4. 并行度实测结论（**编排第一原则的再次确认**）

`python3 scripts/run_gates.py` 单独串行执行 → 4.0s、exit 0、22/23、INTEGRITY 干净。
对照 GK16 `T-24`：**并发执行同一批门禁会产生假 FAIL** ⇒ 本 Loop 强制执行"**并行读 + 串行写**"。

## 5. 非声明

- 本文件**不声称**任何新功能；
- 基线中的绿项**不归功于本 Loop**（它们在本 Loop 之前已是绿）；
- `semantic-consumption` 与 `gate-injection-tests` 的状态**不因本 Loop 而改变**。
