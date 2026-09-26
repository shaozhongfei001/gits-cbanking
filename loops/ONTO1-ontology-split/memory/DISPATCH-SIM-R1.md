# ONTO1｜下一步派工方案（SIM 整改第一轮）

| 项 | 值 |
|---|---|
| 编制 | 全局 Tech Lead（delegated technical executor），2026-09-21 |
| 性质 | **方案待审**：本文件只做规划与派工设计，**未开工任何任务** |
| 执行状态 | `OWNER_AUTHORIZED_SIM_REMEDIATION_AND_IMPLEMENTATION` |
| 事实基线（编制时实测） | 门禁 **51 = 50 pass / 0 fail / 1 PENDING_EXTERNAL_AUTHORITY**（`wi_a4_namespace_collision` exit 3 = `INCOMPLETE`，未判定项 `C-1b` 需 D3）；`gate_state.current = RETURN_TO_HLD`；Wave 0+ 全 `BLOCKED`；`independent_qa=pending/actor=null`；受控目录 `generated/` 改动 0；基线 `gits-core.owl.ttl` = `705578d6324abd0c` |
| 编制依据 | `evidence/prep/construction-plan.json`（691 义务 / 7 批次）· `evidence/WBS-RESTIMATE.md` · `memory/PLAN-NEXT.md` · `memory/NEXT_SESSION.md` 路线图 · `evidence/prep/WI-A2-CLAUSE-SCOPE-AND-DISPOSAL-TIMING.md` |

---

## 0. 授权边界（本方案的硬约束，不可逾越）

**允许**（Owner 2026-09-21 决议）：C-2 后续维护 · 28 条已批准关系的 SIM 投影 · 12 条关系的隔离处理 · 自动化测试与消费者影响分析 · SIM 范围内的后续实现 · 迁移验证。

**禁止**（同决议 + 执行计划 §WI-A4）：声称架构委员会已批准 · 正式根域发布 / 新 IRI 发布或重钉 · 生产数据接入或写回 · 将候选资产提升为 `ACTIVE` · 强行映射 12 条未解析关系 · 把本次兼容修复解释为 V2 目标本体全部落地 · 重构项使用 `equivalentClass` · D1 文本到手前任何国标符合性表述。

**我（TL）永不代做**（五项禁止）：代替 Owner 或委员会签署 · 批准契约激活 · **单人**将候选资产提升为 `ACTIVE` · 充当独立 QA · 将**建议结论**登记为**正式权威事实**。

---

## 1. 无人值守等级定义（本方案统一口径）

| 等级 | 含义 | 需人在场的环节 | 可否夜间批量跑 |
|---|---|---|---|
| **L0** | **全无人值守**：输入确定、判据机器可判、反例齐备 | 无（仅次日复核） | ✅ 可 |
| **L1** | **机器跑 + 出待判清单**：第一遍机器分层，中间层需人工/会话逐条回源 | 中信号层判定 | ⚠️ 前半段可，后半段需人 |
| **L2** | **需人判定**：判据含语义取舍，机器只能给候选 | 全程 | ❌ 否 |
| **L3** | **必须人类权威签署**：Owner/委员会/外部方 | 全程 | ❌ 否 |

**无人值守窗口的夜间红线**（任何 L0/L1 批次都必须遵守）：

1. 只允许**读**全仓；只允许**写** `loops/ONTO1-ontology-split/evidence/**`（新文件）、`evidence/prep/**`、`/tmp/**`；
2. **禁止**写 `specs/**`、`generated/**`、`docs/dd/**`、`docs/review/**`、KERT 仓；**禁止**改 `CONTRACT_INDEX`；
3. **禁止**任何门禁"重记"（记账是 R-TL 人的动作，须在场确认）；
4. **禁止**删除任何证据文件（`D-14`：先 dry-run 打印清单 → 白名单按 `file` 键 → 删除前 `cp -a` 留副本 → 人复核）；
5. 每批次日志**首行必须含** `# artifact=<hash>` 自证；缺自证视为批次无效；
6. 次日由 R-TL 复核并跑 `loop-guard` / `onto1-evidence-board` / `onto1_reference_alignment_check --gate`；任何 FAIL 立即记 `FAILURES.md`；
7. **无人值守 ≠ 无监督**：批次出口必须经 R-TL 验收；**独立复算不得由实现者自签**（禁 `QA_PASS` 自签）。

---

## 2. 派工角色（含写域与禁止）

| 角色 | 数量 | 身份 | 写域 | 明确禁止 |
|---|---|---|---|---|
| **R-TL** | 1 | 全局 TL：编排 / 验收 / 记账 / 跨 Loop 协调 | `memory/**`、`evidence/**`、门禁登记 | 五项禁止（见 §0）；**不得自任 QA** |
| **R-PILOT** | 3~5（并行） | 只读分析员（新 holder，替代已下线的 pilot-a1/a2/a3） | 各自 `evidence/prep/<pilot-id>/**` + 台账 | 只读全仓产物；不改 `specs/**`；不签名 |
| **R-IMPL** | 2（并行） | 实现执行者（**SIM 通道内**） | `scripts/**`（新仪器）、`evidence/**` | 不改正式基线；不碰 `generated/**` |
| **R-QA** | 1 | **独立**复算者（必须与 R-IMPL 不同主体） | 自己的报告文件 | 不得由实现者担任；不得采信 TL 报告 |
| **R-OWNER** | 1 | 项目 Owner | 决议、签署、角色任命 | — |
| **R-KERT** | 1 | KERT 维护方（外部） | KERT 仓 | — |
| **R-REVIEW** | 4 席 | 评审组（现四席同一自然人 ⇒ **不构成独立评审**） | 签署页 14 | 不得由 Owner 预填/代勾 |

---

## 3. 任务清单

### 3.1 A 族 —— **可立即开工**（不依赖任何外部签署）

| ID | 任务 | 派工角色 | 依赖（串行前置） | 并行 | 无人值守 | 出口判据 |
|---|---|---|---|---|---|---|
| **A-1** | **WI-A2 命中处置表闭环（412 聚合行）** | R-PILOT-A1a/b/c（3 面并行）+ R-TL 汇总 | 无 | 面间并行；与 A-2/A-3/A-6 并行 | **L1** | 412 行 100% 有判定（转控制面/跟随迁移/豁免/后续立项）+ 每行 `文件:行` 依据；**新建门禁 `wi_a2_disposition`(+selftest)** 使出口可复算 |
| **A-2** | **T-4 余项 C5~C7 收口** + 陈旧证据重记 | R-PILOT-A2（新 holder）+ R-TL 记账 | C5→C6→C7 内部串行 | 与 A-1/A-3/A-6 并行 | **L0** | 冻结哈希下仪器 8/8 + 4 份 `a3fix-after-*.log` 首行含 `# artifact=` + 回执表；随后重记 `wi_a4_namespace_collision_selftest`(26 用例) 与 `wi_a3_reference_alignment`(16/16) |
| **A-3** | **隔离与投影守卫强化**（负例补齐 + 两账交叉一致） | R-IMPL-A3 + R-TL 验收 | 无 | 与 A-1/A-2/A-6 并行 | **L0** | 新反例被捕获（隔离项出现在**任何 SIM 投影输出** / 目标 IRI 指向隔离项 / 28-12 与 `consumer-scan-summary.csv` 口径交叉一致）；门禁重跑绿 |
| **A-4** | **SIM 通道迁移验证装置**（oldIRI→SIM 解析 + B6/B8 dry-run） | R-IMPL-A4（装置）+ R-PILOT-A4（覆盖分析） | 装置→dry-run；**dry-run 依赖 A-1 分面 + A-3 判据** | 装置与覆盖分析并行；**本体属第二波** | **L0** | SIM 通道解析覆盖率报告 + 不可解析项清单（附 `文件:行`）；**不改**正式 IRI、**不建** `namespaces.json` 根域 |
| **A-5** | **L1/L2/L3 SIM 候选深化** | R-PILOT-A5（L2 只读）+ R-IMPL-A5（L3 夹具） | L1→L2→L3 内部串行；L3 夹具依赖 L2 方案 | 与 A-1/A-2/A-3 并行 | L2 = **L1**；L3 夹具 = **L0** | KERT 元模型适配**补丁方案**（含 `文件:行`）+ L3 加载夹具通过 + **KERT 零写入** |
| **A-6** | **GK17 侧陈旧证据重跑重记**（生成器已配置驱动 ⇒ 跨写在域证据可能陈旧） | R-TL 协调 + GK17 holder | 无 | 与 A-1..A-5 并行 | **L0** | `gk17_triple_consistency_check` / `gk17_ref_anchor_check` 重跑重记；GK17 板面无陈旧项 |
| **A-7** | （可选，P3）**V8/V9 签署页校验器工具化** | R-IMPL-A7 + R-TL | 无 | 可任意并行 | **L0** | 四角色分别签署才可判 `ARCHITECTURE_COMMITTEE_APPROVED`；仅 Owner 单签 ⇒ `OWNER_REVIEW`；**含反例** |

**A-1 面切分（互不重叠，供 3 pilot 并行）**

| pilot | 面 | 未闭环聚合行的预期归属 |
|---|---|---|
| A1a | `gits/apps/**` + `gits/modules/**` | `FOLLOW_MIGRATION` 主体 |
| A1b | `gits/specs/**` + `gits/scripts/**` + `gits/adapters/**` | `CONTROL_PLANE_REQUIRED` 主体 |
| A1c | `kert/**` + `frontend/**` + `tests/**` + DTO/UI/日志面 | `HOMONYM_REQUIRES_SOURCE_CHECK` 主体 |

> **A-1 的量级声明**：未闭环 **412 聚合行**（`FOLLOW_MIGRATION` 270 / `HOMONYM_REQUIRES_SOURCE_CHECK` 119 / `CONTROL_PLANE_REQUIRED` 23），对应 **26690 行命中**中的 8172 次出现。**人日不做承诺（M-10）**：第一遍机器分层后**立即回写**量级。
> **为什么现在做**：该表是 **Wave 2 开工 / Wave 3 正式消费者切换**的出口判据（条款原文「未完成则 **Wave 2 禁止开工**」），**不受 SIM 解耦影响**；它是"到点就来不及"的那一类。**注意**：现状**没有门禁**覆盖它（51 个门禁中无 disposition 项）⇒ 出口判据目前不可复算，A-1 顺带补上。

### 3.2 B 族 —— **只有 Owner 能做**（我不代做，也不作为 SIM 阻塞重复提交）

| ID | 动作 | 现状 | 阻塞范围 |
|---|---|---|---|
| B-1 | C-1-a~e：指定评审人 / 批准并发出送审函 13 / 交付包 / 设期限 / 回收签署页 14 | 包已就绪；四处签署载体齐备 | 仅决定能否声明 `ARCHITECTURE_COMMITTEE_APPROVED` 与正式基线生效 |
| B-2 | **D3 正式根域联签** | `PROVISIONAL_SIM_LEGACY_NAMESPACE` 已临时覆盖 | 仅阻塞：正式 IRI 发布 · 持久解析承诺 · 外部消费者契约 · 生产激活；并卡住碰撞门禁 `C-1b` |
| B-3 | **12 条关系归属裁定**（或确认继续隔离） | 已隔离（`CASH_MANAGEMENT` 未映射） | 卡住 CQ3 全量口径 |
| B-4 | **KERT 写权限归属** | 未确认 | 卡住 B3/B6/B8 的 KERT 部分 |
| B-5 | **O-D4-2 出口裁定**（A 吸收 / B 并存+映射 / C 撤回） | 草案在手 | 卡住 CQ1/CQ2 与映射合同 |
| B-6 | **独立 QA 派出** | `independent_qa=pending/actor=null` | 卡住 A 族批次的**独立验收**（我不得自任 QA） |

### 3.3 C 族 —— **外部**（我只能登记与跟催）

| ID | 主体 | 事项 |
|---|---|---|
| C-1 | KERT 维护方 | 写权限确认 → 补丁方案合入 → 物化链路重跑（校验先于产出） |
| C-2 | 生产数据 Owner | 真实银行源系统确认 |
| C-3 | 域名/基础设施 Owner | 根域联签（= B-2 的另一签署方） |

---

## 4. 串并行总图（三波）

```
波 1（可立即并行，6 路；全部 L0/L1）
 ├─ A-1  ├─ pilot-A1a ─┐
 │       ├─ pilot-A1b ─┼─(并行)─→ R-TL 汇总 → wi_a2_disposition 门禁
 │       └─ pilot-A1c ─┘
 ├─ A-2  pilot-A2（C5→C6→C7 串行）→ R-TL 重记两处陈旧证据
 ├─ A-3  impl-A3（判据→反例→门禁 串行）
 ├─ A-5  pilot-A5（L2 只读分析）
 ├─ A-6  GK17 侧重跑重记
 └─ A-7  impl-A7（可选，P3，不占关键路径）

波 2（依赖波 1，2 路）
 ├─ A-4  dry-run（依赖 A-1 分面 + A-3 判据）
 └─ A-5  L3 夹具（依赖 A-5 L2 方案）

波 3（依赖人类/外部，触发式：预案 §1~§4 已就绪）
 └─ B-1..B-6 →（B-1 达成）→ 预案三分支；C-1..C-3 跟催
```

**关键路径**：`A-1（412 行）` → `A-4 dry-run` → 波 3 的 Wave 2 前判定。
**不被关键路径阻塞**：A-2 / A-3 / A-5 / A-6 / A-7 均可与 A-1 并行。

---

## 5. 批次作业规程（每个 A 族批次通用）

1. **开工声明三行**：actor / 写域 / 复验对象（先声明再动手）；
2. **冻结哈希**：批次内所有结论必须绑定 `# artifact=<hash>`（缺自证视为无效）；
3. **仪器优先**：能机器判的不得人判；每个新判据必须配 **反例**（`D-12`）；
4. **证据纪律**：`D-14` 四道闸（dry-run → 白名单按 `file` 键 → 备份 → 人复核）；
5. **出口验收**：R-TL 验收 + 独立复算（R-QA，待 B-6 派出）；
6. **记账**：门禁记录走 `record_gate.py`（`D-11` 包装器），**不得**手改 `EVIDENCE.json`；
7. **失败即记**：任何 FAIL 进 `FAILURES.md`，附根因与重跑结果。

---

## 6. 需 Owner 审阅批准的事项（**5 项**）

| # | 待批 | 我的建议 | 说明 |
|---|---|---|---|
| 1 | **是否批准波 1 的 6 路并发布局**（尤其 A-1 三面并行） | **批准** | 全部只读或 SIM 内，不触红线 |
| 2 | **并行度与预算**（3 pilot + 2 impl + 1 汇总）；**无人值守窗口时段** | 批准 3 面并行；窗口建议非工作时段全量跑 L0 项 | 需你给时间窗 |
| 3 | 是否批准**索引刷新**（`INDEX_STALE(144)`） | 建议批准并给窗口 | 增量约 0.3M tokens / 全量约 3.7M；未刷新不得声称掌握全局 |
| 4 | **A-1 中信号层的判定方式** | 授权 pilot 按三信号分层法判定并登记，**我抽查 20%** | 若要求逐条回报，工期由"机器第一遍"改为"人工逐条"，量级会显著上升 |
| 5 | 是否把 **A-7（V8/V9 校验器）** 排入本波 | 可排（L0 低成本），但**不占关键路径** | 你已明示不要把它当 SIM 阻塞反复提交，故列为 P3 |

> **未获批准前我不开工任何 A 族批次**；B/C 族我在拿到你裁定时只做"登记与跟催"，不做代签、不做替代裁定。

---

## 7. 本方案明确不做的事（防止越界解读）

- **不**把 A-1 的 412 行拿来"批量标豁免"凑 100%（每行须有 `文件:行` 依据，`FAIL-2026-09-21-W15TL-17` 的教训）；
- **不**在 SIM 实现里发布新 IRI 或重钉（`§WI-A4`）；
- **不**用 `equivalentClass` 做重构桥接；
- **不**把 `gits:Product` 自动认定为 V2 最终 `ProductOffering`（须显式迁移清单）；
- **不**因 A 族全绿而提升任何门禁（`wave_unlock` 不动；唯一通路仍是有效签署页 14 → V1~V9）。

---

## 8. 不变量（每一轮都要核）

`gate_state.current = RETURN_TO_HLD` · Wave 0 及后续 `BLOCKED` · `independent_qa = pending/actor=null` · `wi_a4_namespace_collision` 仍 `INCOMPLETE`（`C-1b` 待 D3）· 受控目录 `generated/` 零改动 · 基线 `gits-core.owl.ttl` = `705578d6324abd0c` · 我不签署、不批准激活、不单人置 `ACTIVE`、不充当独立 QA、不把建议写成权威事实。
