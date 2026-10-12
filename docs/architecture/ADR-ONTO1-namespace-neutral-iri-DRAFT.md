# ADR-ONTO1（草案）：公共语义采用中立持久 IRI 与旧 `gits:` 兼容迁移

| 项 | 值 |
|---|---|
| 文档性质 | **ADR 草案（DRAFT）**——WI-A4 产出，送审稿，**未生效** |
| 关联决议 | 架构委员会 ARCH-ONTO-2026-001 裁定 1（中立持久 IRI + 旧 IRI 转 LEGACY）；设计 V2.0 §7（命名空间 ADR 框架） |
| 关联依赖 | **D3**：语义架构 Owner + 基础设施/域名 Owner 联合批准（`11-外部依赖登记表.md`） |
| 当前门禁 | `RETURN_TO_HLD` 有效；本文**不代表** `DESIGN_APPROVED`，也不代表 ADR 已接受 |
| 状态 | `PROPOSED`（语义架构 Owner 与域名 Owner 签署前不得转为 `ACCEPTED`） |
| 编号 | 待定（生效时由 ADR 登记处分配；本草案使用 `ADR-ONTO1-<TBD>`） |

> **纪律声明（必读）**：本草案**不预填根域名**。`bank.example`、`example.com`、`localhost`、任何临时或占位值**禁止**作为正式值写入制品。设计 V2.0 §7 与复审意见均要求根域由双 Owner 联合批准。

---

## 1. 背景与问题

体系当前把企业公共业务语义（`gits-core.owl.ttl`，`sha256:705578d6324abd0c…`）放在 **GITS 侧的 `https://gientech.com/gits/kno/`** 命名空间下，同时：

1. 存在**第二个命名空间**被同一 `gits:` 前缀指向：`specs/knowledge-architecture/instances/product/products.ttl:1` = `https://gits.bank.example/ontology/core#` ⇒ T-Box 与 A-Box 在 IRI 层**不连通**（GK17 已记 `NAMESPACE_MISMATCH_SILENTLY_GREEN`：`targetedInstances=0`、`vacuous=true`）；
2. 公共语义的**权威实体**与**物理寄放仓库**在元数据里未分离（`PROVENANCE.json` 仅有 `authorityRepo`）；
3. 委员会裁定公共模块**不得长期寄放 KERT 根目录**，须有独立受保护语义契约库（裁定 3）。

结论：需要一次**显式**的命名空间决议，同时解决"中立性/持久性"与"旧 IRI 迁移"两个问题。

## 2. 决策方向（采纳委员会，不改写）

1. 新公共术语采用**机构控制的中立、持久 IRI**；
2. 旧 `gits:` IRI 保持**只读**并置 `LEGACY` 状态；
3. 逐术语给出 `oldIRI → newIRI` 映射与**语义关系**；
4. 兼容窗口（≥1 发布周期，新旧**双发布**）后才退役旧入口；
5. 解析机制：HTTP 可解析（303 / 内容协商）**或**受控离线解析 + 内容哈希钉值；
6. 碰撞检查：新旧 IRI 集合**交集必须为空**（脚本门禁）；
7. 影响面：全部消费方（含硬编码 ID、生成目标、plan hash）纳入影响分析（→ WI-A2 产出）。

## 3. 未决项（阻塞本 ADR 定稿）

| # | 未决项 | 决策 Owner | 未决期间禁止动作 |
|---|---|---|---|
| U-1 | **根域名 / 根 IRI 前缀** | 语义架构 Owner + 域名 Owner | 发布任何新中立 IRI；把占位值写入正式制品 |
| U-2 | 解析端点与解析机制选型（在线 303 vs 离线受控解析 + 哈希） | 域名 Owner + 平台 | 声称 IRI "可解析"；发布解析服务 |
| U-3 | LEGACY 双发布窗口长度（≥1 发布周期，具体值） | 公共语义 Owner（待任命） | 关闭旧入口；旧 IRI 退役 |
| U-4 | 公共层产权与 `authorityEntity` / `hostingRepo` 具体值 | 公共语义 Owner（待任命）+ 契约库 Owner | 候选公共模块标 `ACTIVE` |

## 4. IRI 形态与命名规则（待 U-1 填根域后生效）

```
新公共术语 IRI = {NS-L1}/{术语短名}          # L1 公共业务语义核心
L2 KERT 术语   = {NS-L2}/{术语短名}          # KERT 知识供给元模型
L3 GITS 术语   = {NS-L3}/{术语短名}          # GITS 经营运行本体
L4 注册表对象  = {NS-L4}/{对象短名}          # 集成契约注册表（Schema/SKOS）
```

约束：
- **单一发布权威**：每个 IRI 只有一个发布流水线；禁止两侧各自发布同名术语；
- **禁止动态 IRI**：不得含时间戳、构建号、会话 ID；
- **大小写与分隔**：术语段用 `UpperCamelCase`（与 OWL 类名一致）；属性段用 `lowerCamelCase`；
- **保留段**：`LEGACY/`、`_meta/` 为保留路径，不得作为术语短名。

## 5. 迁移机制（oldIRI → newIRI）

### 5.1 语义关系三分法（必须逐术语标注，禁止一刀切）

| 情形 | 判据 | 允许的绑定 | 项目映射状态 |
|---|---|---|---|
| **保留原名 + 语义不变** | 定义、域/值域、基数、时间语义均不变 | `owl:equivalentClass` / `owl:equivalentProperty`（身份可互换） | `RETAINED` |
| **改名 / 重构**（如 `Customer → CustomerRole`、`CorporateGroup → EnterpriseGroup`、`Product → ProductOffering`） | 语义**收窄或改变** | **禁止 `equivalentClass`**；用 SKOS `closeMatch` / `exactMatch`（仅当足够近似） | `REMODELED` |
| **转换制品类型**（如 `ActivationContract` OWL 类 → JSON Schema 对象） | 不同构（OWL 类 vs Schema 对象） | 不建立 OWL 等价；经注册表 **RDF 投影**保持图查询能力 | `TRANSFORMED` |
| **退役**（如数据属性 `customerId`） | 由新模式承载（`CustomerRole` + `SourceIdentifier`） | 弃用映射（`owl:deprecated` + 映射注释） | `DEPRECATED` |

> 依据：复审包 `04-基线32项映射表.md §D`。**重构项不得使用 `equivalentClass`** 是硬约束（Wave 2 校验项之一）。

### 5.2 双发布窗口与退役门

```
T0  新 IRI 发布（新根域生效）+ 旧 IRI 保持只读并标 LEGACY
    ├── 同步发布映射（oldIRI → newIRI + 语义关系）
    ├── 消费方按 WI-A2 处置表切换（先钉新值 → 后切消费 → 旧值只读）
T0+ ≥1 发布周期（U-3 未定值）
    ├── 全部消费方已切换（WI-A2 处置表零遗留 + 漂移用例绿）
    └── 退役门通过 ⇒ 旧 IRI 标记 retired（不再双发布，但记录不删）
```

退役门**必须**同时满足：
1. WI-A2 处置表 `CONTROL_PLANE_REQUIRED` 与 `FOLLOW_MIGRATION` 项 100% 关闭或具名豁免（带解除条件）；
2. 新旧 IRI 碰撞检查绿；
3. import closure **不得同时包含同一 ontology series 的两个版本**（设计 §6.4）；
4. 双侧 Owner 签署退役记录。

### 5.3 解析机制（U-2 选型后细化）

- 路线 A（在线）：HTTP `303 See Other` + 内容协商（`Accept: text/turtle`）指向受控制品；
- 路线 B（离线受控）：发布内容寻址包（manifest + `sha256`），消费方按哈希钉值解析；
- **两路线共同要求**：解析结果必须可哈希校验；不可解析时**fail-closed**（具名拒绝），不得静默降级为文本比对。

### 5.4 碰撞检查（脚本门禁设计）

| 检查 | 判据 | 失败动作 |
|---|---|---|
| C-1 集合互斥 | `set(oldIRI) ∩ set(newIRI) == ∅` | 阻断发布 |
| C-2 前缀唯一 | 同一短前缀不得指向两个命名空间（当前 `products.ttl:1` 正是反例） | 阻断发布（修前缀） |
| C-3 单版本闭包 | import closure 内同一 series 不得出现两个 versionIRI | 阻断发布 |
| C-4 钉值一致性 | 制品内容哈希 == 钉值文件声明哈希 | 具名漂移拒绝 |

> C-2 的现实样本：`products.ttl:1` 用 `gits:` 指向 `https://gits.bank.example/ontology/core#`，而本体用同名前缀指向 `https://gientech.com/gits/kno/`（`specs/data/customer-source-mapping.r2rml.ttl:2`）。此缺陷**必须先修**，否则新 IRI 迁移会叠加一层错配。

## 6. 影响面（引用 WI-A2，不重复枚举）

- 扫描口径与结果：`loops/ONTO1-ontology-split/evidence/consumer-scan-hits.jsonl`（26690 命中，4818 文件）；
- 净迁移义务：`consumer-scan-obligations.csv`（file 级 1052 行 = `CONTROL_PLANE_REQUIRED` 14 + `FOLLOW_MIGRATION` 1038）；
- **诚实性声明**：扫描是**词法级**，`FOLLOW_MIGRATION` 是**候选**义务；Wave 2 执行前须逐条回源确认（方法见 WI-A2 报告 §4）。

## 7. 后果（Consequences）

**正向**：公共语义摆脱单系统私有化；T-Box/A-Box IRI 连通性可验证；迁移有显式窗口与退役门；解析可哈希校验。

**代价与风险**：
- 一次性 IRI 迁移成本覆盖两仓（含 GITS 的 plan hash 派生链：本体内容哈希变 ⇒ `versions.ontology` 与 `planHash` 必变，须逐环验证子块）；
- 若 U-1 延迟，Wave 2 阻塞（`R-D3`，等级高）；
- 旧 `gits:` 前缀的**同名双命名空间**缺陷会放大迁移噪声，须先修 C-2。

## 8. 与既有 ADR 的关系

- `ADR-018`（公共本体独立性与治理）已标 **SUPERSEDED**，仅作溯源，不构成依据；
- 本草案不取代 `ADR-0016`（统一激活计划）与 `ADR-0017`（投影边界）；
- 本草案生效后，`gits-core.owl.ttl` 的前缀与命名空间声明以本 ADR 为准。

## 9. 批准路径（禁止跳步）

| 步 | 动作 | 签署方 | 状态 |
|---|---|---|---|
| 1 | 本草案送审 | TL（本文件） | **已完成**（2026-09-20） |
| 2 | 填根域与解析机制（U-1/U-2） | 语义架构 Owner + 域名 Owner | 待 |
| 3 | 公共语义 Owner 确认 L1/L2/L4 命名规则与产权字段（U-4） | 公共语义 Owner（**待任命**） | 阻塞 |
| 4 | 碰撞检查脚本实现 + 绿证 | Integration Contract Owner（**待任命**）+ TL | 阻塞 |
| 5 | ADR 转 `ACCEPTED` 并分配编号 | 双 Owner 联签 | 待 |
| 6 | 纳入 Wave 2 前置（`G-1` 条件 ③） | TL | 待 |

**未完成第 2~5 步前，禁止**：发布任何新中立 IRI、生产重钉、把占位根域写入正式制品、旧 IRI 退役。
