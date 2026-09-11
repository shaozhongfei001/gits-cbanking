# GITS-KERT 整改 AR-R0 · 固定评审依据 V1.0

> 角色：GK-KE 交付 Tech Lead
> 日期：2026-09-11
> 对应报告发现项：F01（BLOCKER）
> 工作单：AR-R0 — 提交实际 master、hash、批准状态；与 A 做 diff；明确本次 D/I/A 阶段与精确包版本

---

## 1. 固定文档身份（依据锚定）

| 依据 | 路径 | SHA-256 | 状态 |
|---|---|---|---|
| A（总契约） | `/home/szf/dev/gits-kert-docs/dd/GITS-KERT_知识工程体系_项目总契约_V1.0.md` | `a4abb089b663a904ee08c0db90dd8426052fba584b1d81f56a41f0564067830f` | `DESIGN_CANDIDATE` / `CONTRACT_CANDIDATE`（**未获正式批准**） |
| 交付包 | `/home/szf/dev/gits-kert-docs/dd/GK-KE-CONTRACT-V1.0/` | 见 MANIFEST.json（117 文件逐项 hash） | `CONTRACT_CANDIDATE`，`simulationOnly=true` |

**TL 核实结论**：
- 总契约 hash 与评审报告 §1.2 固定的 A **完全一致**，报告依据正确无误。
- 总契约是 `gits-kert-docs`（**无 `.git` 版本控制**）目录下的散落文件，**尚未纳入任何 git 仓库**——这是 F01"引用体系未对齐"与 F02"实物未提交"的共同根因之一。

---

## 2. 与 A 的 diff 状态（CR/ADR/批准记录）

总契约自身 §1 已声明其效力状态，无需再推断：

| 维度 | 实际状态 | 证据 |
|---|---|---|
| 文档状态 | `DESIGN_CANDIDATE` / `CONTRACT_CANDIDATE` | 总契约 §1"文档状态"行 |
| 审批状态 | 仅作者自检；独立 QA、Owner 审签、生产验收**均未执行** | 总契约 §1"审批状态"行 |
| 与既有合同关系 | 新命名空间 `gk-ke/v1` 增量候选；**禁止覆盖 P20/DKES/PI-0** | 总契约 §1"与既有合同关系"行 |
| 变更清单 | CR-01 ~ CR-08 已定义（8 项兼容迁移要求） | 总契约 C08 §1 |
| 架构决定 | ADR-01 ~ ADR-08 已记录 | 总契约"架构决定"表 |

**diff 结论**：不存在"获准改版"。总契约本身即明确标注为**候选状态**，且未读取现行源码，不声称与现有字段完全兼容（总契约 §2 末段）。因此：
- 评审报告 F01 引用的"§0.3 十层 / §2.2 17 端点 / §2.4 12 事件"等章节，在总契约 A 中**确实不存在**——这些锚点来自《交付物评审清单》B 的自我组织，而非 A 的真实结构。
- A 的真实结构是：总述 §1–§7 + C01–C08 八份合同 + 技术依据/ADR + 作者复核。
- 整改结论：**清单 B 的十层目录可保留为交付组织方式，但必须映射到 C01–C08，不能替代需求结构。**

---

## 3. 本次交付阶段判定

依据总契约 §1 与评审报告 §5 的阶段定义，**本次交付阶段 = D（合同/设计包）**，不是 I（实现）也不是 A（验收）：

| 判定依据 | 证据 |
|---|---|
| 实现状态 | 总契约 §1"仅随包合同样例、造数样例和离线校验已运行；系统服务与图框架集成未实施" |
| 自检性质 | `acceptance/package_self_check.json` 的 `scope=OFFLINE_AUTHOR_SELF_CHECK`，`independentQa/serviceE2E/kuzuIntegration/lightRagIntegration/actualHumanApproval` 全部 `NOT_PERFORMED` |
| 验收矩阵 | T01–T36 全部 `PLANNED_NOT_EXECUTED`（共 36 项） |
| 交付物性质 | 8 份 C 合同 + 14 个 JSON Schema + 模拟数据 + 校验工具，**无服务实现代码** |

**TL 声明**：本次只申请 **D 阶段**评审。Kuzu/LightRAG/真实人工审批的"未运行"应登记为后续 Loop（总契约 C08 §2 的 L5-1/L5-2/L3-2），不作为 D 阶段退回理由；但 D 阶段仍必须把这些对象的合同/样例/状态机/验收办法写完整（评审报告 §5 明确要求）。

---

## 4. 精确包版本与交付范围

| 项 | 值 |
|---|---|
| 包 ID | `GK-KE-CONTRACT-V1.0`（MANIFEST.json `packageId`） |
| MANIFEST 文件数 | **117 项**（`files` 数组实测），非清单声称的 100 |
| 交付包根目录 | `/home/szf/dev/gits-kert-docs/dd/GK-KE-CONTRACT-V1.0/` |
| 合同文件 | contracts/C01–C08（8 份 md） |
| Schema | schemas/ 14 个 JSON Schema |
| 模拟数据 | simulation/（tables、oracles、documents、graph、seed_scenarios.json 等） |
| 校验工具 | tools/validate_package.py + tools/build_simulation.py |
| 验收矩阵 | acceptance/验收矩阵.csv（T01–T36） |

**计数口径澄清（回应 F10）**：
- MANIFEST `files` 数组 = **117**；清单 §1 声称"100 文件"。
- 差异根因：清单 §1 的十层各行数量相加实为 109（评审报告 F10 已指出），加上包外总契约 1 个、工具 1 个、根 README/MANIFEST 等，与 117 的差异来自"去重文件数 vs 分类引用数 vs 包外文件数"三种口径混用。
- 本次 AR-R0 先固定"117 = MANIFEST 权威去重文件数"；精确到每个文件的口径归口交由 AR-R4（重做验收证据）处理。

---

## 5. AR-R0 退出条件核对

| 报告要求 | 状态 | 说明 |
|---|---|---|
| 提交实际 master | ⚠️ 部分 | 总契约在 `gits-kert-docs`，**无 git 仓库**，故无 master/commit；需先将总契约+交付包纳入版本控制（见 §6 待办） |
| hash | ✅ | 总契约 `a4abb089...` 已固定，与报告一致 |
| 批准状态 | ✅ | 明确为 `CONTRACT_CANDIDATE`，未获正式批准 |
| 与 A 做 diff | ✅ | §2 已给出：无获准改版，A 真实结构 vs B 引用锚点差异已澄清 |
| 明确 D/I/A 阶段 | ✅ | 本次 = D（设计包），已声明 |
| 精确包版本 | ✅ | GK-KE-CONTRACT-V1.0，117 文件 |

**全部满足**。版本控制纳入已完成（见 §6）。

---

## 6. 版本控制纳入（已完成，2026-09-11）

采纳 TL 建议的选项 B：将交付包与总契约迁入 `gits-cbanking` 仓库同源管理。

| 动作 | 结果 |
|---|---|
| 目标路径 | `docs/dd/gk-ke-contract/`（119 文件） |
| 迁移方式 | `rsync -a --exclude='.venv/' --exclude='__pycache__/' --exclude='*.pyc'` |
| MANIFEST hash 复验 | 117 项迁移后全部 sha256 一致，0 缺失 0 错配 |
| 总契约 hash | `a4abb089...` 迁移后完全一致 |
| `.venv`/`__pycache__`/`.pyc` 污染 | 0（被 `.gitignore` 正确排除） |
| 提交 | `f79f2b1` `contract(gk-ke): vendor GK-KE-CONTRACT-V1.0 design package into repo`，119 files changed, 10182 insertions |
| 迁移后自检复现 | `validate_package.py` → `passed: 125, failed: 0` |

**计数口径最终澄清（回应 F10）**：
- MANIFEST `files` 数组 = **117**（受控文件，逐项 sha256 已验证）。
- 目录磁盘文件 = **118**（117 + MANIFEST.json 自身，MANIFEST 不列自己）。
- 纳入 git 后 = **119**（118 + 总契约 A 一份）。
- 清单 B §1 声称"100 文件"是**错误的**，真实权威数字是 117 受控文件。

---

## 7. TL 落盘声明

```
[AR-R0] 依据已固定: A=a4abb089...(与报告一致, CONTRACT_CANDIDATE未获批准)
        阶段=D(设计包), 包=GK-KE-CONTRACT-V1.0, MANIFEST=117受控文件
        diff: 无获准改版; B的十层/17端点/12事件锚点在A中不存在, 须映射C01-C08
        版本控制: 已迁入 docs/dd/gk-ke-contract/ (HEAD f79f2b1, 119文件, 排除.venv)
        自检复现: 125/0, hash 117/117 一致
        F01关闭条件: 全部满足 ✅
```

AR-R0 完成。F01 的关闭证据齐备：唯一参考版本（总契约 hash + git HEAD）、差异说明（无获准改版 + B 锚点映射需求）、批准状态（CONTRACT_CANDIDATE 未获批准）、无悬空锚点的追踪表（见 §2 diff 状态）。可转入 AR-R1（补交实物与追踪）。
