# SIM 临时模拟权威声明（草案）

| 项 | 值 |
|---|---|
| 文档性质 | **草案（DRAFT）**——随 D2 / D4 请求函提交，**未生效** |
| 依据 | 设计 V2.0 §3.2「SIM 阶段特别裁定项」；复审包 `01-主模型` 同段 |
| 适用对象 | 试点期产品身份（`ProductOffering`）、客户/法人/集团身份（`CustomerRole`/`LegalEntity`/`EnterpriseGroup`/`GroupMembership`）的**临时**权威载体 |
| 批准方 | 产品 Owner（产品身份）+ 数据 Owner/业务 Owner（客户与集团身份） |
| 当前状态 | 未批准；未批准前相关 CQ 场景 = `NOT_EVALUATED` |

---

## 1. 为什么需要这份声明

试点期没有正式的产品主数据接口，也没有正式客户/法人主数据接口，但：
- 设计不接受"没有权威"（会退化为隐式权威）；
- 设计不接受"GITS/KERT 自己当权威"（B-02 已纠正）；
- 设计**明确禁止**把临时登记表静默升级为企业权威。

因此：把试点期用到的登记表**显式声明为临时模拟权威**，写清四要素，并预设退出条件。

## 2. 四要素（设计 §3.2 要求的全部内容）

### 2.1 临时性质

- 本声明指定的载体是**模拟（SIM）权威**，仅用于试点期开发与验证；
- 它不是银行源系统，不是产品主数据，不是数据平台；其内容**不得**被引用为业务事实或审批结论；
- 所有由 SIM 载体产生的数据必须带 `simulationOnly = true` 标记（沿用 OF-02 状态分离：地图生命周期 / 合同注册 / SIM 身份三平面不互相推断）。

### 2.2 覆盖范围（本声明生效期间指定的临时权威载体）

| 事实类型 | 临时权威载体（待填具体路径/系统） | 覆盖的术语 |
|---|---|---|
| 产品身份与编码 | `<SIM-PRODUCT-REGISTRY>` = `specs/knowledge-architecture/instances/product/products.ttl` + KERT 产品卡 front matter | `ProductOffering` |
| 客户角色 | `<SIM-CUSTOMER-REGISTRY>`（SIM 登记表，待指定） | `CustomerRole` + `SourceIdentifier` |
| 法人 / 组织 / 集团 | `<SIM-ENTITY-REGISTRY>`（SIM 登记表，待指定） | `Party` / `Organization` / `LegalEntity` / `EnterpriseGroup` / `GroupMembership` |

**明确排除**：知识文档、规则包、知识地图、技能定义、产品知识版本**不在**本声明范围（其权威是 KERT，见设计 §3.1）。

### 2.3 退出条件（硬条件，不设例外）

本声明在下列任一条件发生时**自动废止**，无需另行决议：

1. 对应的正式源系统（EDWCRM / 产品主数据 / 数据平台）接入并可用；
2. 正式权威矩阵确认件（D4）或产品身份权威确认（D2）签署生效；
3. `OWNER_ACTIVATED` 激活评审要求（激活门禁不接受 SIM 作为最终权威依据）；
4. 任一方书面撤回。

废止后 30 日内必须完成：临时注册表转正式投影或下线；相关 `simulationOnly=true` 数据的处置登记；引用方切换记录。

### 2.4 责任人

| 角色 | 责任 |
|---|---|
| 产品 Owner | 产品身份 SIM 载体的维护、内容正确性、提供分类裁定（D2） |
| 数据 Owner + 业务 Owner | 客户/法人/集团 SIM 载体的维护与内容正确性、提供权威矩阵确认（D4） |
| 公共语义 Owner（待任命） | 术语定义与 T-Box；SIM 数据不得反写 T-Box |
| 全局 Tech Lead | 退出条件跟踪台账；到期未废止即上报（见 §5） |

## 3. 允许与禁止（生效期间）

**允许**：继续 Wave 2~4 的开发与验证；以 SIM 数据构造受控测试夹具；以 `simulationOnly` 标记的数据跑场景验证。

**禁止**：
- 以 SIM 数据作为 `PASS` 的唯一依据去满足**激活门禁**；
- 把 SIM 登记表写入正式制品（OWL 本体、合同 Schema、`CONTRACT_INDEX`）；
- 在对外文书、对客户材料、评审材料中把 SIM 数据表述为真实业务数据；
- 用 SIM 前缀缺失来推断"非模拟"（OF-02 已推翻该推断，3 反例作废）。

## 4. 与 D2 / D4 的关系

| 依赖 | 先签 SIM 声明的作用 | 后补的内容 |
|---|---|---|
| D2（产品关系 40 处分类） | 允许继续开发（不阻塞 Wave 2~4） | 产品 Owner 的逐条分类裁定 + `PROD-*` 映射 |
| D4（A-Box 权威确认） | 允许构造投影与夹具 | 数据 Owner 的权威矩阵确认 + 授权投影合同 |

> 注意：SIM 声明**不能**让 CQ3/CQ1/CQ2 场景进入满足**激活门禁**的状态——这条在设计中是硬约束（豁免永不满足激活门禁）。

## 5. 跟踪台账（生效后由 TL 维护）

| 项 | 内容 |
|---|---|
| 章节位置 | `loops/ONTO1-ontology-split/memory/ORCHESTRATOR.md` 风险登记 |
| 到期检查 | 每次 Wave 收工核对退出条件 1~4 是否触发；触发即启动废止流程 |
| 当前状态 | 本声明**未生效**，无台账项 |

## 6. 签署区

| 项 | 内容 |
|---|---|
| 产品 Owner（产品身份部分） | ☐ 批准 ☐ 有条件批准 ☐ 不批准；签署/日期 |
| 数据 Owner（客户/集团身份部分） | ☐ 批准 ☐ 有条件批准 ☐ 不批准；签署/日期 |
| 业务 Owner 会签 | ☐ 批准 ☐ 不批准；签署/日期 |
| 指定载体路径（§2.2 三个占位） | |

---

## 附：Owner 决议附件（2026-09-21 · O-07 / O-08 落地）

> **本附件不改动上文 §2.2/§2.3 原文**（该草案已随 D2/D4 请求函发出；就地改写会造成**已发文书漂移**）。本附件是 **Owner 决议对占位载体的具名授权**，与原文冲突时**以本附件为准**。

### A.1 占位载体 → Owner 具名授权（O-07）

| 原文占位 | **Owner 授权具名** | 覆盖事实类型 / 术语 | 限定 |
|---|---|---|---|
| `<SIM-PRODUCT-REGISTRY>` | **`SIM-PRODUCT-CATALOG`** | `ProductOffering` | 产品**身份**；产品**关系**仍受 O-06 隔离（40 处 = `QUARANTINED_UNRESOLVED`） |
| `<SIM-CUSTOMER-REGISTRY>` | **`SIM-CUSTOMER-MASTER`** | `Party` / `Organization` / `LegalEntity` / `CustomerRole` | 模拟客户与主体身份**快照** |
| `<SIM-ENTITY-REGISTRY>` | **`SIM-GROUP-REGISTRY`** | `EnterpriseGroup` / `GroupMembership` | 模拟集团身份与**带有效期**的成员关系 |

`SourceIdentifier` **不另建载体**，随上述三个数据产品生成；它只表达**来源标识与授权**，**不承载业务真相**。

### A.2 `SourceIdentifier` 六必填字段（O-07 批准）

`sourceSystemId` · `sourceObjectType` · `sourceRecordId` · `sourceVersion` · `observedAt` · `authorizationBasis`
**缺任一 ⇒ 具名拒绝 `MISSING_SOURCE_IDENTIFIER`**。
**明确禁止**：把业务有效期 `effectiveFrom`/`effectiveTo` 塞入 `SourceIdentifier`（会污染业务时间语义）。

### A.3 投影 freshness（O-07 批准；**相对 `scenarioAsOf` 判定**）

| 对象 | 最大允许年龄 |
|---|---:|
| Party / CustomerRole | 24 小时 |
| Organization / LegalEntity | 7 天 |
| EnterpriseGroup / GroupMembership | 7 天 |
| ProductOffering | 24 小时 |

> **不得**以机器当前时间判定（会破坏可重复测试）；判定基准固定为 `scenarioAsOf`。

### A.4 授权边界与生效状态（**不变**）

- 合同授权范围：**`simulationOnly=true` · 无生产写回 · 无正式银行权威声明**；
- **本声明与投影合同仍为 `NOT_EFFECTIVE`**：生效前必须完成 **Schema 校验 + 正负夹具 + 来源/时点/版本校验 + 独立 QA**；
- SIM **只对模拟试点有效**，**不得**外推为银行正式口径、生产权威或生产写回许可；
- **生产数据 Owner 对真实银行源系统的正式确认仍缺**（不可由 SIM 替代）。

### A.5 与 O-08 的接口

过渡期 L1 `SourceIdentifier` 与既有 `core.ExternalIdentifier` **并存**；缺 `sourceVersion`/`observedAt`/`authorizationBasis` 的旧记录**只能标 `PARTIAL_MAPPING`**；**C-2 碰撞未关闭前 CQ1 不得标 `PASS`**。
