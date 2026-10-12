# GITS-KERT Tech Lead 派工单 · AR-R4 + AR-R5 V1.0

> 角色：GK-KE 交付 Tech Lead
> 日期：2026-09-11
> 对应发现项：F09（MAJOR，验收证据范围）、F10（MINOR，计数口径）、F11（MINOR，治理用语）
> 工作单：AR-R4（重做验收证据）+ AR-R5（复审与决定）

---

## 一、TL 派工原则

依据项目角色规范，TL 负责规划与审批，**不直接写 Feature 实现代码**。AR-R4/AR-R5 的工作拆分为三类：

| 类别 | 责任人 | 性质 |
|---|---|---|
| A 类：证据整理 / 统计口径修正 / 治理用语修正 | **TL 直接完成** | 文档与治理职责，非实现代码 |
| B 类：合同源变更（full Schema / 负例清单 / 复算脚本） | **Feature Pilot** | 实现代码，走 `specs/` → `make generate` → `make check` |
| C 类：独立 QA 签署 / Owner 决议 | **独立 QA + 各 Owner** | 角色隔离，TL 不得代签 |

---

## 二、A 类任务（TL 本轮直接完成）

### A1｜修正 F10 计数口径（统计错误）

**已核实事实**：清单 B §1 声称"100 文件 / json 8"，但 MANIFEST 实测：

| 扩展名 | 实际数量（MANIFEST `files` 数组） |
|---|---|
| json | **69** |
| md | 30 |
| csv | 11 |
| py | 3 |
| jsonl | 2 |
| sql | 1 |
| txt | 1 |
| **合计** | **117** |

清单 B 的"json 8"严重错误（实际 69 个），"100 文件"错误（实际 117）。已由 AR-R0（§6）和 AR-R1（§1.1）固定正确数字。

**TL 决定**：权威计数以 MANIFEST 为准（117 受控文件，json 69），清单 B 的计数口径作废。此结论已写入 AR-R0/AR-R1，无需再改清单 B（清单 B 是历史评审材料，保留原样作为整改记录）。

### A2｜修正 F11 治理用语（限定适用范围）

**已核实事实**：清单 B 两处用语过宽：
1. §5"所有 schema 变更走 Flyway" → 应限定为"关系数据库结构迁移走 Flyway"。
2. §10"Supervisor 阻塞写 BLOCKED.md 不向人提问" → 应限定为"自动任务停机留痕约定，不能取消 Owner 变更决定/指标批准/知识认定责任"。

**TL 决定**：交付包 `README.md` 的治理描述无此问题（已核对，README 未出现"所有 schema 走 Flyway"或"不向人提问"）。清单 B 是历史材料，其用语问题**作为整改记录保留**，本轮以 TL 意见文档（本派工单）明确正确表述，不回头改历史清单。正确表述已在 AR-R0 §2 diff 状态中隐含。

### A3｜单列历史 QA（F09 范围绑定）

**已核实事实**：
- 125/0 = 本交付包离线自检，已绑定 HEAD `f79f2b1` + MANIFEST 117 项 hash（AR-R1 §5）。
- 1808 测试 / 覆盖率 0.8001 / qa-gkd-formal-001 = `gits-cbanking` 主仓库独立安全工作（spring-security/tomcat CVE），**非本交付包**，不继承。

**TL 决定**：已完成范围绑定（AR-R1 §5）。结论：
- 本交付包验收只认 125/0 自检（D 阶段作者自检）。
- 1808/0.8001 属主仓库另一工作项，与本知识工程交付无继承关系。

---

## 三、B 类任务（派发 Feature Pilot）

### 派工单 WP-R4-1｜合同源变更批次

**派工对象**：Feature Pilot（GK-KE 交付实现角色）

**任务内容**（合并 AR-R2 G1/G2/G3 + AR-R3 H1/H2 的合同源变更）：

| # | 变更 | 产出 | 关闭对象 |
|---|---|---|---|
| 1 | 新增 `MetricDefinition.full.schema.json`（落地 C04 §2 七组字段） | full Schema | F06 G1 |
| 2 | 新增 `simulation/oracles/negative_cases.json`（C002 跨币种 + T12–T16 负例 expectedError） | 负例清单 | F06 G2/G3 + F08 H2 |
| 3 | 新增 `tools/verify_simulation.py`（独立复算账务/引用闭包/C001/C002） | 复算脚本 | F08 H1 |
| 4 | 补 `SourceVersion/Capability/QueryDefinition/Release` 四 Schema | 注册对象 Schema | F04 |
| 5 | 补 `ExistingRagAdapter` Schema（LegacyRagHit 映射） | RAG 适配 Schema | F07 |
| 6 | `SemanticPackage` 补 writeOwner/writeEntry 字段 | 权威写入口 | F03 |

**红线**（派工时明确）：
- 走 `specs/` 合同源 → `make generate` → `make check`，禁止直接改 `generated/`。
- 禁止发明合同外字段；字段必须对齐总契约 C01–C07 正文。
- 每个变更记录 `DEV_SELF_CHECK_PASS`，不得自签 `QA_PASS`。

**退出条件**：`make check` 通过 + 每个变更有对应测试/负例 + 覆盖矩阵更新。

---

## 四、C 类任务（派发独立 QA + Owner，非本轮）

| 任务 | 责任人 | 时机 | TL 边界 |
|---|---|---|---|
| 独立 QA 核查可复现性 | 独立 QA（非 dev 角色） | B 类完成后 | TL 不代签 |
| 指标口径认定 | 指标 Owner | B 类后 | TL 不代签 |
| 知识认定/地图任务价值 | 知识 Owner + 业务 Owner | B 类后 | TL 不代签 |
| Owner 决议（试点范围） | 各领域 Owner | 独立 QA 后 | TL 不代签 |

---

## 五、AR-R5 复审与决定（TL 提交）

### 5.1 本轮整改的 TL 复审结论

| 发现项 | 整改状态 | TL 复审 |
|---|---|---|
| F01 引用体系未对齐 | AR-R0 完成（依据固定 + 版本控制纳入） | ✅ 关闭 |
| F02 缺实物 | AR-R1 完成（实物纳入 git + hash 全验） | ✅ 关闭 |
| F03 权威矩阵 | AR-R2 核对完成，Schema 补字段待 B 类 | ⏳ 待 B 类 |
| F04 注册/地图 | AR-R2 核对完成，四 Schema 待 B 类 | ⏳ 待 B 类 |
| F05 构建发布主链 | AR-R2 核对完成，端到端实例待 B 类 | ⏳ 待 B 类 |
| F06 分析语义 | AR-R2 核对完成，full Schema + 负例待 B 类 | ⏳ 待 B 类 |
| F07 RAG/图适配 | AR-R2 核对完成，RAG Schema 待 B 类 | ⏳ 待 B 类 |
| F08 模拟闭环 | AR-R3 核对完成，复算脚本 + 负例清单待 B 类 | ⏳ 待 B 类 |
| F09 验收证据范围 | AR-R1 §5 + AR-R4 A3 完成 | ✅ 关闭 |
| F10 计数口径 | AR-R0/R1 + AR-R4 A1 完成 | ✅ 关闭 |
| F11 治理用语 | AR-R4 A2 完成 | ✅ 关闭 |

### 5.2 TL 的阶段性决定

1. **F01/F02/F09/F10/F11 已关闭**（5/11）：这五项是"依据/实物/证据/口径/用语"类问题，无需写实现代码，TL 已直接闭环。
2. **F03–F08 的核对已完成，关闭条件明确**（6/11）：这六项是"设计→可校验制品"的最后一公里，缺口已精确定位为 6 个合同源变更动作（B 类），不涉及设计重写。
3. **下一步唯一阻塞**：B 类合同源变更（Feature Pilot 执行）+ C 类独立 QA/Owner 签署（角色隔离，不可省略）。

### 5.3 TL 最终声明

```
[AR-R5] TL 复审:
        已关闭 5/11 (F01/F02/F09/F10/F11): 依据/实物/证据/口径/用语
        核对完成 6/11 (F03-F08): 缺口定位为 6 个合同源变更, 不涉及设计重写
        阻塞: B类(Feature Pilot合同源变更) + C类(独立QA/Owner签署, 角色隔离)
        TL 不代签 QA_PASS, 不代签 Owner 决议
        下一 baton: Feature Pilot (执行 WP-R4-1)
```

---

## 六、Baton 交接

| 项 | 值 |
|---|---|
| 当前 holder | Tech Lead（本派工单） |
| 下一 holder | **Feature Pilot**（执行 WP-R4-1 合同源变更） |
| 交接内容 | AR-R0~R5 全部产出 + 6 个合同源变更清单 |
| 待办 | B 类合同源变更 → 独立 QA → Owner 决议 |
| 红线重申 | 不代签 QA_PASS，不直接改 generated，不发明合同外字段 |
