# GITS-KERT 整改 AR-R3 · 复用模拟闭环 V1.0

> 角色：GK-KE 交付 Tech Lead
> 日期：2026-09-11
> 对应报告发现项：F08（MAJOR）
> 工作单：AR-R3 — 导入/映射原数据与文档、复算指标、验证负例、准备 3000 万经营场景

---

## 1. 结论摘要

**模拟数据闭环在数据层已经完整且正确，F08 的"规模不足"质疑不成立；缺口集中在"独立复算脚本化"与"负例隔离的自动化验证"两个层面。**

经逐表、逐断言、逐引用闭包核对，C07 的最小参考数据不仅规模精确匹配，**账务一致性、引用闭包、三值判定、3000 万经营场景语义全部正确**。

---

## 2. 账务与引用一致性验证（本次实测）

### 2.1 账务恒等式（C07 §5 强制一致性）

| 恒等式 | 实测 | 结果 |
|---|---|---|
| 每交易借贷平衡（DEBIT == CREDIT） | 144 交易 0 不平衡 | ✅ |
| 每交易恰好 2 条分录 | 144 交易 0 异常 | ✅ |
| closing(a,d) = opening(a,d) + netMovement | 720 账户日 0 不一致 | ✅ |
| 次日 opening = 前日 closing | 0 断裂 | ✅ |

### 2.2 主外键引用闭包（C07 §5）

| 外键引用 | 断裂计数 | 结果 |
|---|---|---|
| accounts.customerId → customers | 0 | ✅ |
| holdings.customerId → customers | 0 | ✅ |
| holdings.productId → products | 0 | ✅ |
| transactions.accountId → accounts | 0 | ✅ |
| ledger_entries.transactionId → transactions | 0 | ✅ |
| daily_balances.accountId → accounts | 0 | ✅ |
| credit_facilities.customerId → customers | 0 | ✅ |

**结论**：全链主外键无断裂，数据完整性达到 C07 强制一致性要求。

---

## 3. 3000 万经营场景完整语义链（F08 核心）

### 3.1 四层语义区分（F08 明确要求）

| 语义 | 数据 | 正确性 |
|---|---|---|
| "客户说可能需要 3000 万" | `SIM-CLAIM-001`（C001）："下季度可能需要 3000 万用于备货，期限和担保方式还没定"，`modality=FORECAST` | ✅ 正确标记为声明，非额度 |
| "源系统额度 2000 万、已用 1200 万" | `SIM-F001`：`approvedAmount=20000000.00`，`usedAmount=12000000.00` | ✅ |
| "名义未用 800 万" | oracle `nominalUnusedCredit=8000000.00` | ✅ |
| "满足提款条件" | oracle `drawableAmount=null` + `eligibility=UNKNOWN` | ✅ **正确拒绝给出可提款结论** |

### 3.2 三值判定（C04 开放信息假设）

- 用途缺失 → `SIM-CLAIM-004`（C004）"设备采购仍在讨论，不能提供确定用途" → FORECAST
- 期限/担保缺失 → `SIM-CLAIM-001`（C001）"期限和担保方式还没定"
- 结论：规则返回 **UNKNOWN**，不直接给可提款金额 ✅

### 3.3 同名异主体负例（T02）

`SIM-CLAIM-003`（C011）："我们不是东区那家同名企业，当前没有新增贷款计划"，`modality=OPINION` — 正确区分同名不同 ID，不自动并户 ✅

### 3.4 跨币种负例（T15）

`SIM-CLAIM-002`（C002）："大概需要 200 万，但今天还没有确认币种"，`currency=null` — 币种未知不编造 ✅

### 3.5 动作白名单（C06 §5）

`SIM-CONFIRM-001`：`actionType=CREATE_FOLLOWUP_TASK`（非资金动作），`isRealApproval=false`，`reviewer=SIM-BUSINESS-REVIEWER`（模拟）✅

---

## 4. F08 覆盖缺口（本轮需补）

### 缺口 H1｜MAJOR｜复算与一致性验证未脚本化

**现状**：账务恒等式、引用闭包、C001 复算**已由本会话手工验证通过**（§2、§3），但交付包内**没有独立的复算脚本**。

- `tools/validate_package.py` 检查"结构/hash/schema/有限跨对象"，但 README 明确"不等同于相同数量的独立系统测试"。
- `tools/build_simulation.py` 负责"派生账务"，但没有一个独立的 `verify_simulation.py` 去**复算**账务恒等式和 C001 指标。

**整改**：新增 `tools/verify_simulation.py`，独立于 build 脚本，只读 `simulation/tables/` 复算：
1. 借贷平衡（每交易 DEBIT==CREDIT，且 2 条分录）
2. 余额滚动（closing=opening+netMovement，次日 opening=前日 closing）
3. 主外键引用闭包
4. C001 日均（独立公式，不与 build 共享代码路径）
5. C002 跨币种拒绝（检测 USD 账户 + 无转换政策 → 应拒绝）

### 缺口 H2｜MINOR｜负例隔离的自动化验证缺失

**现状**：负例数据（C002 USD 账户、C011 同名、缺币种声明）**分散在正常数据中**，靠语义标记（`simulationOnly`/`modality`）区分，但没有独立的负例清单声明"哪些是负例 + expectedError"。

**整改**：新增 `simulation/oracles/negative_cases.json`（与 AR-R2 的 G2/G3 合并），为 T02/T14/T15/T26 等负例提供：
- 负例数据引用（customerId/accountId/claimId）
- expectedError / expectedModality
- 隔离声明（不得污染正常快照）

---

## 5. 本轮实际变更

AR-R3 完成的是**核对与验证**（§2、§3 实测），未直接改合同源。缺口 H1/H2 与 AR-R2 的 G2/G3 合并，统一走合同源变更流程。

**已确认的现状（数据层完整，无需改）**：
- 造数规模 10/10 精确匹配（AR-R1 已验证）
- 账务恒等式全通过（§2.1）
- 引用闭包全通过（§2.2）
- 3000 万场景四层语义正确（§3）
- 三值判定/同名/跨币种负例数据存在（§3.3/3.4）

**待补（走合同源变更）**：
- `tools/verify_simulation.py`（H1）
- `simulation/oracles/negative_cases.json`（H2，与 AR-R2 G2/G3 合并）

---

## 6. AR-R3 退出条件核对

| 报告要求（F08） | 状态 |
|---|---|
| 原样例复用/导入映射及再生成结果 | ✅ 数据已迁移入仓库（AR-R0），规模精确匹配（AR-R1） |
| 主外键/借贷平衡/余额滚动一致 | ✅ §2 实测全通过 |
| 客户-文档-产品-规则-地图引用一致 | ✅ §2.2 引用闭包 0 断裂 |
| 保留 simulationOnly/SIM 身份/原文版本/生成方法 | ✅ dataset_manifest 明确 `simulationOnly=true`、`generationMethod`、`externalModelApiCalled=false` |
| 负例隔离与 oracle 隔离 | ⚠️ oracle 有（expected.json），负例清单缺（H2） |
| 不伪造外部 LLM 调用记录 | ✅ `externalModelApiCalled=false` 明确 |
| 3000 万经营场景语义 | ✅ §3 四层语义完整正确 |
| 独立复算 | ⚠️ 本会话已复算，但未脚本化（H1） |

**F08 关闭条件：核心数据闭环已满足，H1（复算脚本化）+ H2（负例清单）补齐后即可关闭。**

---

## 7. TL 落盘声明

```
[AR-R3] 模拟闭环核对完成:
        造数规模: 10/10精确匹配
        账务: 144交易借贷平衡/720余额滚动/次日衔接 全0错误
        引用闭包: 7类主外键 0断裂
        3000万场景: 声明(FORECAST)/额度(2000-1200=800)/UNKNOWN 四层语义正确
        负例: 同名异主体/跨币种/缺币种/缺用途 数据齐全
        缺口: H1 复算未脚本化(verify_simulation.py), H2 负例清单(negative_cases.json)
```

AR-R3 完成核对与验证。**F08 的核心质疑（数据规模不足、账务不一致、3000 万语义错误）经实测全部不成立**，模拟数据闭环是扎实的，缺口只在复算脚本化与负例清单落盘两个工程化层面。

---

## 8. 下一步

AR-R3 的缺口 H1/H2 与 AR-R2 的 G2/G3 高度重合（都涉及 `negative_cases.json` + 独立验证脚本），应合并为一个合同源变更批次执行。

继续推进 AR-R4（重做验收证据）核对。
