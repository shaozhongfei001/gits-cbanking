# ONTO1｜三方评审召集规则（GITS / KERT / 数据平台）DRAFT

| 项 | 值 |
|---|---|
| 文档性质 | **DRAFT（草稿）**——候任 Integration Contract Owner 任职技术准备产出 |
| 状态 | `DRAFT` / `NOT_EFFECTIVE`；**未生效**，不得作为任何评审已完成的依据 |
| 依据 | 执行计划 §1（角色）、§4 WI-1-1（"② GITS/KERT/数据平台三方评审规则（CODEOWNERS 或等效）"）；设计 §3.1、§3.2、§6.6、§10 |
| 主持角色 | Integration Contract Owner（**待任命**，`memory/OWNER_REQUESTS.md` A-2） |
| 前置 | 五条件中第 ② 条是**独立语义契约库 ACTIVE 的必要条件**；本规则未生效 ⇒ 契约库不得标 `ACTIVE` |

> **红线声明**：本规则**不代签**；不改变 `workspace` 规则的权威顺序；逾期**不得**默认通过；无决议**不得**生效。

---

## 1. 目的与边界

**目的**：把"GITS / KERT / 数据平台 三方共同评审"从口号变成**可执行、可留痕、可被门禁读取**的规则，使"跨方变更不得单方生效"可被证明。

**边界（不做）**：

| 不做 | 原因 |
|---|---|
| 不替代 Owner 决策 | 评审结论是**输入**，`OWNER_ACTIVATED` 仍须 Owner 激活（设计 §10） |
| 不替代独立 QA | 评审 ≠ 验证；`QA_PASS` 只能由独立 QA 记录 |
| 不改变合同 SSOT | 决议产出的变更仍须走"合同先行 → generate → check" |
| 不引入新状态词汇 | 复用 06 号五态 + L4 设计 §4 发布状态，**不造第三套** |

---

## 2. 三方定义与代表资格

| 方 | 覆盖范围 | 代表角色（**待填姓名**） | 缺席时的后果 |
|---|---|---|---|
| **GITS 方** | L3 经营运行本体、GITS 侧消费与运行时 | GITS Owner / Business Process Owner（`memory/ROLE_BOARD.yaml:50`，`EXTERNAL`） | 涉及 L3 或 GITS 消费的决议**不得通过** |
| **KERT 方** | L2 知识供给元模型、知识资产与技能运行时 | Knowledge Owner / KERT Owner（`memory/ROLE_BOARD.yaml:45`，`EXTERNAL`） | 涉及 L2 或跨仓消费的决议**不得通过** |
| **数据平台方** | L1 A-Box 权威（客户/法人/集团/产品身份）、数据投影 | 数据 Owner（D4）+ 源系统代表 | 涉及 L1 实例权威或投影的决议**不得通过** |

**主持与秘书**：

| 议题类型 | 主持 | 秘书（记录） |
|---|---|---|
| L1 语义与命名空间 | 公共语义 Owner（**待任命**） | TL 指定 |
| L2 知识元模型 | Knowledge Owner | KERT 侧 |
| L3 运行本体 | GITS Owner | GITS 侧 |
| **L4 注册表、跨方绑定、兼容性** | **Integration Contract Owner** | TL 指定 |

**资格硬约束**：**无姓名/无授权书面依据的代表不得计入法定人数**；`OWNER_REQUESTS.md` §C-1-a 的"指定本轮评审人与渠道"属于同一类组织动作，**目前全部待办**。

---

## 3. 触发条件（哪些变更**必须**三方评审）

| # | 触发 | 为什么必须三方 | 依据 |
|---|---|---|---|
| T-1 | L1 术语新增/改名/重构/退役 | 单域无权独改公共语义 | 设计 §2.2 条件 2 |
| T-2 | L1 ↔ L2/L3 的跨层引用变更（如 `ofCustomer` range 改指 `CustomerRole`） | 破坏消费方类型断言 | 07 号 §1"range 改指 = major" |
| T-3 | 任意 `major` 兼容级别变更（删项/改名/收窄域值域/**新增约束**） | 07 号 §2.1：只增也可能是 major | 07 号 §1 |
| T-4 | IRI 迁移与旧 IRI 退役（LEGACY 退役门） | 跨方消费方全部受影响 | ADR §5.2 退役门第 4 条"双侧 Owner 签署" |
| T-5 | 端点绑定变更（`EndpointBinding` 新增/改指/解绑） | 跨仓授权（`crossRepoAuthorization`） | L4 设计 §5 |
| T-6 | 消费者授权变更（`ConsumerBinding` 授权范围/有效期） | 授权不得单方扩大 | CQ5 `UNAUTHORIZED` |
| T-7 | 能力发布状态跃迁（`DRAFT→PUBLISHED`、`→DEPRECATED`、`→RETIRED`） | 决定 CQ5 首因 | L4 设计 §4 |
| T-8 | 数据投影合同生效（D4 域） | A-Box 权威不可由 GITS/KERT 自定 | 设计 §3.2 |
| T-9 | 词表（`TaskTypeScheme`）概念退役 | 退役 = major，须替代映射 | 07 号 §2.2 |
| T-10 | 任何"以豁免替代通过"的申请 | `WAIVED` 只放行开发 | 06 号 §3 |

**非触发（可单方，但仍需留痕）**：`patch` 级修订（注释/标签/示例，不动语义）；词表新增概念（`minor`）；Schema 新增**可选**字段（`minor`）。

**防误判**：若一方主张"这是 patch"，须给出"消费方解析结果不变"的证明；**主张方负举证责任**（谁主张 minor，谁证明）。

---

## 4. 否决权（hard veto）边界

**原则**：**本域语义不得被他方多数票推翻**。这是设计 §2.2 条件 2 的规程化。

| 变更是关于… | 拥有 hard veto 的一方 | 说明 |
|---|---|---|
| L1 术语定义 | 公共语义 Owner | 但 A-Box 权威归属须数据平台同意 |
| L1 实例权威 / 投影生效 | **数据平台方** | 设计 §3.2：GITS/KERT 只持授权投影 |
| L2 知识元模型 | KERT 方 | — |
| L3 运行本体 | GITS 方 | — |
| L4 注册表对象与兼容集 | Integration Contract Owner | 但跨方绑定须**被绑定方**同意 |
| 跨仓授权 | **被授权方**（不得由授权方单方声明已授权） | 回源：`provider-bindings.json` 的 `authority.crossRepoAuthorization` |
| 国标参照对齐措辞 | 公共语义 Owner + 项目标准管理员 | 设计 §8 唯一可声明口径 |

**约束**：`veto` 必须**具名、书面、给理由与解除条件**；不得以"沉默"或"未回复"行使否决（沉默 ⇒ 该方未参与，决议按 §5.3 处理，**不得**视为同意）。

---

## 5. 流程（六步，每步可留痕）

```
① 提案（Proposal）
     └─ 含：变更对象 / 层 / 兼容级别自评 / 影响面 / 回滚预案
② 门禁预检（Precheck）
     └─ 合同先行是否满足；是否属 §3 触发；材料完整性
③ 召集（Convene）
     └─ 通知三方 + 时限 + 材料包（自含，不得要求评审方读代码仓）
④ 评审（Review）
     └─ 每方出具：APPROVE / APPROVE_WITH_CONDITIONS / REJECT / ABSTAIN(具名理由)
⑤ 决议记录（Decision）
     └─ 结论 + 条件清单 + 到期 + 解除条件 + 责任 Owner + 决议 ID
⑥ 生效条件登记（Effect）
     └─ 条件未全关 ⇒ 不得声称已生效（"有条件批准 ≠ 条件已通过"）
```

### 5.1 材料包要求（防"信息不对称通过"）

| 必含 | 说明 |
|---|---|
| 变更前后的机器可读制品（或差分） | 不得只给文字描述 |
| **旧夹具行为预测表** | 07 号 §4：旧夹具在新版下"该通过仍通过、该失败仍失败" |
| 影响面分析（受影响钉值方、plan hash 失效范围、消费者清单） | 07 号 §4；WI-A2 处置表为输入 |
| 兼容级别判定依据（逐条对 07 号矩阵） | 防"自称 patch" |
| 回滚预案（单提交可 revert 的具体 commit 范围） | 计划 §10 |
| **不确定项与未覆盖范围** | 诚实性要求：不得把 `NOT_EVALUATED` 写成通过 |

### 5.2 时限

| 项 | 规定 |
|---|---|
| 召集通知提前量 | ≥ 3 个工作日（`major` 变更 ≥ 5 个工作日） |
| 单轮评审时限 | 默认 5 个工作日（可经三方书面同意延长，须记录） |
| 逾期处理 | **不得默认通过**；记 `NOT_EVALUATED` + 原因 + 关联依赖（对齐 06 号 §1） |
| 紧急通道 | 仅限"生产事故止损"；须事后 5 个工作日内补全流程，否则决议失效 |

### 5.3 法定人数与结论规则

| 项 | 规定 |
|---|---|
| 法定人数 | ① 主持方 + ② **受影响各方的被授权代表全部到场**（或书面出具意见） |
| `ABSTAIN` 的效力 | 不阻碍但须具名理由；**若某受影响方 ABSTAIN，则该方的 hard veto 覆盖范围内事项不得通过**（回到 §4） |
| 通过条件 | 无 `REJECT` + 无未解除的 `veto` + 受影响方均出具意见 |
| `APPROVE_WITH_CONDITIONS` | 视为**有条件批准**：条件未全关，**不得**计为通过（沿用 GK-KE `OWNER-002` 口径） |
| 决议 ID | `DCN-ONTO1-<YYYYMMDD>-<nn>`（提案） |

### 5.4 决议记录最小字段（机读，进 L4 `ContractVersion.approvalRefs`）

| 字段 | 说明 |
|---|---|
| `decisionId` | 决议 ID |
| `subjectRef` | 变更对象（合同 ID + 版本） |
| `trigger` | §3 的 T-n 编号 |
| `verdict` | `APPROVED` / `APPROVED_WITH_CONDITIONS` / `REJECTED` / `NOT_EVALUATED` |
| `conditions[]` | 每条含 `text` / `ownerRole` / `dueAt` / `releaseCondition` |
| `attendees[]` | 各方代表**角色**（姓名由人类填，AI 不填） |
| `artifacts[]` | 材料包文件 + **内容哈希**（防事后改材料） |
| `vetoes[]` | 具名否决（如有） |
| `evidenceRef` | 落盘位置（`loops/ONTO1-ontology-split/evidence/`） |

**材料哈希纪律**：材料包须**冻结哈希**（同 `wi_review_package_integrity` 的做法），防止"决议后材料被静默修改"。

---

## 6. CODEOWNERS 等效实现（**待填**）

执行计划 §4 要求"CODEOWNERS 或等效"。本草案给出**路径 → 必须评审方**的映射骨架，**owner 名单（GitHub handle/邮箱）待人类 Owner 填写**：

| 路径 glob | 必须评审方 | 主持 |
|---|---|---|
| `specs/semantic/**`（L1 部分，拆分后 `gits-public-core*`） | 公共语义 + 数据平台 | 公共语义 Owner |
| `specs/semantic/gits-operational*` | GITS | GITS Owner |
| L2 制品（KERT 仓内 / 钉定副本） | KERT | Knowledge Owner |
| `specs/knowledge-architecture/schemas/**`（L4 治理面） | GITS + KERT | Integration Contract Owner |
| `specs/gk-ke/v1/schemas/**` | GITS + KERT | gk-ke contract owner |
| `specs/CONTRACT_INDEX.yaml` | 合同 Owner + TL | Integration Contract Owner |
| `generated/**` | **任何人不得手改**（只读） | — |

**注**：`generated/` 的"必须评审方"是**空集**——因为禁止手改（`AGENTS.md`）；对 `generated/` 的改动只能通过 `make generate` 产生。

---

## 7. 与既有规则的关系

| 关系 | 说明 |
|---|---|
| 不改变权威顺序 | 合同 SSOT、`specs/` 优先于 `generated/`、索引不升格（`code-fact-index` 规则） |
| 不替代 Owner 决议 | 评审是 `OWNER_ACTIVATED` 的**输入** |
| 不替代 Loop 纪律 | Loop 的 baton/门禁/证据纪律照旧 |
| 与 GK-KE 程序的关系 | 复用 GK-KE 已建立的"决议链 + 生效条件 + 条件关闭 ≠ 决议通过"口径（`OWNER-001→002→003` 经验），但不改写其记录 |

### 7.1 与 `PSO-01` 准备包的分工（**避免重复造规则**）

公共语义 Owner 候选包已给出**评审分级矩阵**（`ONTO1-Wave1独立语义契约库五条件落地方案-DRAFT.md` §7.1：`patch` 单签 / `minor` 双方 / `major` 三方会签 + 禁自审）与三条**失败具名码**：
`SCC_REVIEW_SINGLE_PARTY`、`SCC_SELF_APPROVAL`、`SCC_REVIEW_RECORD_MISSING`（同文件"条件 ②"行）。

**分工**：
- **分级与失败码以 `PSO-01` 为准**（本文不重定义级别表）；
- **本文补其缺口**：召集流程（§5 六步）、**否决权边界**（§4）、时限与逾期规则（§5.2）、法定人数与 `ABSTAIN` 效力（§5.3）、决议最小字段（§5.4）、触发条件清单（§3）、CODEOWNERS 骨架（§6）；
- 两文冲突时：级别判定与失败码从 `PSO-01`；召集与决议程序从本文。**须由 TL 合并为一份受控文件**（建议 Wave 1 出正式版）。

### 7.2 与 ADR 批准路径的关系

`docs/architecture/ONTO1-命名空间ADR联签意见-DRAFT.md` 的 **P-3** 把"碰撞检查 C-1~C-4 脚本可执行 + 变异复验绿"列为 ADR 联签前置，并把**脚本原型责任归 Integration Contract Owner（待任命）**——与本 Loop `ADR-ONTO1` §9 第 4 步一致。本规则的 §5 召集流程即该项前置的**程序载体**（谁召集、谁签署、如何留痕）。

---

## 8. 待办（全部在人类手上）

| # | 待办 | 落点 |
|---|---|---|
| 1 | 任命 Integration Contract Owner（主持人） | `memory/OWNER_REQUESTS.md` A-2 |
| 2 | 任命公共语义 Owner（L1 主持） | 同上 A-1 |
| 3 | 裁定词表 Owner | 同上"另需裁定" |
| 4 | 指定三方代表**姓名与授权书** | 本文 §2 表 |
| 5 | 填写 §6 CODEOWNERS 名单 | 本文 §6 |
| 6 | 确认决议 ID 编号规则与归档位置 | 本文 §5.3 |

---

## 9. 变更记录

| 版本 | 日期 | 变更 | 作者 |
|---|---|---|---|
| DRAFT-v0.1 | 2026-09-20 | 初稿 | 候任 Integration Contract Owner（AI 起草） |

> 草稿，签字权在人类 Owner。
