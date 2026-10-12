# O-D4-2 差异补充决议草案：两套外部标识模型的冲突与出口

| 项 | 值 |
|---|---|
| 文档编号 | `ONTO1-W-1-OD42-01` |
| 性质 | **差异补充决议草案（DRAFT）**——TL 侧决策包，**不含结论**；出口选择权在 Owner / 契约方 |
| 触发依据 | TL 裁定 **D-8**（`loops/ONTO1-ontology-split/memory/TL-DECISIONS-W-1.md`） |
| 冲突对象 | GK-KE 已登记 `core.ExternalIdentifier` ⟷ ONTO1 拟新增 `SourceIdentifier` |
| 上游登记 | `docs/dispatch/ONTO1-D4-决策包-V1.0.md` §6 **O-D4-2**（MAJOR）；`docs/review/ARCH-ONTO-2026-001-rereview-package/11-外部依赖登记表.md` §D4 |
| 前置口径 | GK 程序裁定：「范围不变的客观落实不再申请相同决定；**实质语义冲突或扩大范围须提差异补充决议**」 |
| 当前门禁 | `RETURN_TO_HLD`（有效）；本草案不改变任何门禁 |

---

## 1. 事实（逐字段回源，未采信转述）

| 维度 | GK-KE `core.ExternalIdentifier` | ONTO1 `SourceIdentifier` | 是否可自动互转 |
|---|---|---|---|
| 定义 | 外部标识，指向**外部登记体系的稳定 ID** | **来源系统 + 对象类型 + 原始 ID + 生效区间**的复合标识 | 语义相关但不等价 |
| 来源（回源） | `specs/gk-ke/v1/examples/l1-1/positive/SemanticPackage.json:177-194`（`origin=CORE`，`temporal=TEMPORAL`） | `loops/ONTO1-ontology-split/evidence/attribution-45-v2.csv:9`（L1 新增，承接 `customerId` 退役）；字段表见 `docs/dispatch/ONTO1-D4-决策包-V1.0.md` §2 | — |
| **身份规则** | **`scheme + value`**（二元） | **`sourceSystem + objectType + originalId`**（三元，见 D4 包 §2「标识唯一性」） | ❌ 差异：`objectType` 无对应位 |
| 属性集 | `scheme`、`value`、`issuedBy`（**必填：scheme、value**） | 六必填：`sourceSystem`/`objectType`/`originalId`/`validFrom`/`extractedAt`/`authorizationBasis`（+ 可选 `validTo`/`sourceRecordedAt`） | ❌ 必填强度不同 |
| 时态 | `TEMPORAL`（声明时态化，未定口径） | 生效区间**左闭右开** `[from,to)`；业务日 `Asia/Shanghai`；`extractedAt` 为 **UTC** | ⚠️ 口径需统一否则真值可差一天 |
| 既有反例资产 | `SemanticPackage_identity_merge.json`（身份合并反例）、`SemanticPackage_semantic_fork.json`（语义分叉反例）等 6 个 neg 夹具 | ONTO1 侧尚无对应用例（CQ1 夹具受 D4 阻塞） | ❌ 未复用 |
| 既有对齐声明 | — | D4 包 §2 已把 `scheme`/`issuedBy` 列为**可选对齐字段** | 说明起草时已察觉重叠 |

## 2. 冲突定性（**不是命名冲突，是规则冲突**）

1. **身份规则不等价**：`scheme+value` 与 `sourceSystem+objectType+originalId` 不是同一等价关系的两种写法。若 `scheme := sourceSystem`、`value := originalId`，则**同一 `sourceSystem` 下不同 `objectType` 的同名 ID 会被判为同一标识**（GK-KE 侧接受、ONTO1 侧应拒绝）⇒ 直接产生"**两套规则对同一实例给出不同判定**"。
2. **必填强度不同**：ONTO1 六必填 ⊃ GK-KE 二必填 ⇒ 存在"**GK-KE 合法但 ONTO1 必须拒绝**"的实例集。若不显式声明谁生效，摄取路径会随实现者选择而漂移。
3. **时态口径未统一**：`TEMPORAL` 未定边界与业务日；ONTO1 已定左闭右开 + 时区 ⇒ 差一天的真值差异在 CQ1（"何时成为客户"）上直接可见。
4. **违反"每术语单一发布权威"**：两者若同时进 L1，同一实体将存在**两条可解析身份路径**，而设计 §3.1 要求每术语单一发布权威、跨仓单向钉值。
5. **绕过既有验收门禁**：GK-KE 侧已用 neg 夹具把"身份合并/语义分叉"做成可判定的红线；另造术语而不映射，等于**让这些门禁对新模型不可见**。

**结论**：属"**实质语义冲突**"，须走差异补充决议，**不得由任一侧静默吸收**。

## 3. 三个出口（供 Owner / 契约方选择；TL 不选）

### 出口 A｜`SourceIdentifier` **吸收** `core.ExternalIdentifier`（L1 唯一定义）

**做法**：L1 只保留一个外部标识类（命名可保留 `SourceIdentifier` 或回到 `ExternalIdentifier`），字段集取并集，`identityRule` 显式定义为**三元**（把 `objectType` 纳入）；ONTO1 的六必填作为**项目加严**声明（而非新模型）；GK-KE L1-1 包改为引用/映射该 L1 定义。

| 项 | 评估 |
|---|---|
| 优点 | 单一权威、CQ1 有唯一真值、**直接复用** GK-KE 既有 6 个 neg 夹具 |
| 代价 | **须改动 GK-KE 已登记件**（L1-1 包 + 相关 neg 夹具）⇒ 触发其回归与署名；属"扩大范围" |
| 风险 | GK-KE 若已在激活流程中，改动会连带其门禁与证据链；需协调窗口 |
| 可逆性 | 中（术语收敛后再次分开代价高） |
| 必要证据 | ① 双侧 Owner 联签；② GK-KE L1-1 包改动后的完整回归（含 6 neg）；③ `identityRule` 唯一性证明 + 反例 ≥2 |

### 出口 B｜**并存 + 显式职责边界与双向映射**

**做法**：保留两术语，但先用**机器可判的映射合同**把它们绑死：
`scheme := "<sourceSystem>/<objectType>"`、`value := originalId`、`issuedBy := sourceSystem`；并声明冲突裁决优先级（摄取侧以 ONTO1 六必填为强校验，注册表/合同侧以 GK-KE 二元为准），映射合同登记于 **L4 注册表**。

| 项 | 评估 |
|---|---|
| 优点 | **不动他人已登记件**即可前进；ONTO1 的强校验作为摄取加严可立即落地；增量、可逆 |
| 代价 | 必须新增：映射合同 + 一致性校验门禁（**fail-closed**）+ 冲突优先级声明；两套规则须同时有反例 |
| 风险 | **映射一旦有损即制造静默错配**（如 `originalId` 在源侧不唯一）；"并存"若无机器校验，就是二义的合法化 |
| 可逆性 | 高（后续可收敛为 A） |
| 必要证据 | ① 映射合同（含 `scheme` 编码规则）；② 双向一致性校验脚本 + 变异复验；③ 优先级声明；④ ≥2 组跨包反例 |

### 出口 C｜**撤回** `SourceIdentifier`，全部用 `core.ExternalIdentifier`

**做法**：ONTO1 不新增类；`customerId` 退役由 `CustomerRole` + `core.ExternalIdentifier`（如 `scheme=EDWCRM`、`value=CUSTID`）承载；`objectType`/`extractedAt`/`authorizationBasis` 下沉为 **L4 摄取合同字段**。

| 项 | 评估 |
|---|---|
| 优点 | 术语面最小、零重复、完全复用 GK-KE 定义与反例 |
| 代价 | CQ1 的"来源系统 + 对象类型"从 L1 下沉到 L4 ⇒ 图查询需跨层表达；L1 语义表达力下降 |
| 风险 | 丢失 `objectType` 后，**同一 `sourceSystem` 下不同对象的 ID 空间重叠**无法区分，需用 `scheme` 编码补偿（否则等于引入已知歧义） |
| 可逆性 | 高（但将来第二个来源系统出现时仍需回头做映射） |
| 必要证据 | ① `scheme` 编码规则；② CQ1 跨层查询可表达性验证；③ 与 `customerId` 退役映射的对照表 |

## 4. 三个出口共同适用的硬约束（无论选哪个）

1. **合同先行**：出口选定并登记前，**不得**在 `specs/` 或 L4 注册表登记 `SourceIdentifier`（或任何新外部标识术语）；
2. **CQ1 状态**：出口选定前保持 `NOT_EVALUATED`；**追加**阻塞（原受 D4，现叠加本条）；
3. **触他人登记件**（出口 A/C 必然涉及）⇒ 必须走差异补充决议 + 列受影响回归清单，**不得**由 ONTO1 单方改动；
4. **禁静默吸收**：不得以"实现时再说"把两套规则同时放进运行路径；
5. **时态统一**：`TEMPORAL` 与「左闭右开 + `Asia/Shanghai` 业务日 + UTC 记录时点」必须二选一或给出换算规则；
6. **不动制品**：本阶段只读——不改 `specs/gk-ke/**`、不改 `specs/semantic/**`、不改 `CONTRACT_INDEX.yaml`、不改 `generated/`。

## 5. TL 倾向（**建议，不是裁定**）

- **目标态建议出口 A**：它与设计 §3.1「每术语单一发布权威」和跨仓单向钉值最一致，且能直接复用 GK-KE 既有反例资产；
- **过渡态建议出口 B**：在 GK-KE 无改动窗口时，B 是**唯一不触他人合同**的前进路径，但**必须先落地映射合同与一致性门禁**，否则不得视为可用；
- **不建议出口 C**：`objectType` 的语义损失会把已知歧义制度化（需要用 `scheme` 编码补偿，等于把复杂度挪到看不见的地方）；
- **路径建议**：`B（过渡，登记映射合同） → A（目标，待 GK-KE 窗口收敛）`，并在 B 的映射合同里**预留收敛到 A 的字段**。

> 重申：以上是 TL 的**技术倾向**。出口选择与是否触发 GK-KE 回归窗口，属 Owner / 契约方权限；TL 不代选、不代签。

## 6. 若 Owner 选定某出口，下一步各自需要什么（验收清单）

| 出口 | 下一步动作 | 验收证据（缺一不可） |
|---|---|---|
| A | 起草 L1 收敛术语定义（22 字段）+ GK-KE L1-1 包改动影响清单 | 双侧 Owner 联签 + GK-KE 全量回归（含 6 neg）+ 唯一性证明 |
| B | 起草映射合同（L4 登记）+ 一致性校验脚本 | 映射合同 + 校验脚本门禁绿（含变异）+ 优先级声明 + ≥2 组跨包反例 |
| C | 起草 `scheme` 编码规则 + CQ1 跨层查询方案 | 编码规则 + 跨层查询可表达性验证 + `customerId` 退役映射表 |

## 7. 签署区（Owner / 契约方）

| 项 | 内容 |
|---|---|
| 出口选择 | ☐ A 吸收 ☐ B 并存 + 映射 ☐ C 撤回 ☐ 其它（请写明） |
| 若选 B：是否授权起草映射合同 | ☐ 是 ☐ 否 |
| 若选 A/C：是否开放 GK-KE 回归窗口 | ☐ 是（窗口：______） ☐ 否 |
| 责任人 / 日期 | |
| 结论依据的草案版本 | `ONTO1-W-1-OD42-01` V1.0 / 2026-09-20 |
