# D2 决策包：产品关系 40 处悬空引用的归一化候选与勾选表

| 项 | 值 |
|---|---|
| 包名 | `W-1/D2-pack` |
| 收件（裁定人） | **产品 Owner**（产品目录 / 产品工厂归口） |
| 抄送 | 公共语义 Owner（待任命）、Knowledge/KERT Owner、全局 Tech Lead |
| 编制角色 | `product-ref-normalization-analyst`（**只做分析，不做裁定**） |
| 配套文书 | 《D2 请求函》`docs/dispatch/ONTO1-D2-产品Owner请求函.md`（正式请求与签署区）· 本包为其**可勾选工作台** |
| 前置裁定 | `GK17-四项悬置口径裁定-V1.0.md` §1.5（12 符号"一个字"定性）· `GK17-产品卡引用空间裁定-V1.0.md` §4（候选清单） |
| 设计依据 | `ONTOLOGY-SPLIT-DESIGN-V2.0-REVIEW.md` §5（Product 模式闭合、**有效待补/错误引用/作废**三分类、条件 4） |
| 数据锚点 | KERT `922a674d`（只读）· GITS `71169042` |
| 生成器 | `scripts/onto1_d2_normalization_pack.py`（`--gate` 八项自检 / `--selftest` 六条变异） |
| 机读产物 | `loops/ONTO1-ontology-split/evidence/d2-normalization-pack.json`（sha256 `24c6e24ccb58ad82…`） |
| 当前状态 | **本包未生效**；产品 Owner 勾选并签署前，三场景一律 `NOT_EVALUATED` |

---

## 0. 本包做了什么、没做什么（先看这段）

| 项 | 本包**做了** | 本包**没做** |
|---|---|---|
| 事实 | 把 40 处引用复算到**逐卡片逐字段逐行**；复现 40 = 12 + 28、12 个取值、13 张卡 | 不新增/修改任何产品卡、`products.ttl`、`specs/`、`generated/` |
| 归一化 | 给每个取值列**候选映射 + 证据强度（强/弱/无）+ 回源位置**，78 条回源**逐条机器校验行内容** | 不写"权威映射表"（GK17 §1.3：映射一旦入册即第二份定义，须 Owner 先定性） |
| 交叉验证 | 列出每个取值与**非产品词表**的精确同形命中 + 邻近语义命中（族名 / 品类名 / 账户关系位 / GITS 种子） | 不把 SIM / 种子数据当企业权威 |
| 零实例 | 记录 `mutex_product_ids` 13/13 为空 ⇒ `mutuallyExclusiveWith` = `NOT_EVALUATED`，并**显式禁止**用"0 目标 0 违规"包装为通过 | 不标任何场景 `PASS`、不用 `WAIVED_FOR_DEVELOPMENT` 充当激活依据、**不关闭 R-6** |

> **裁定权在产品 Owner。** 表中"建议分类"是**分析员建议**，可直接推翻；勾选行才是你的输出。

---

## 1. 事实复核（全部可复现）

复现命令（两条，均在本包提交时实测通过）：

```bash
python3 scripts/onto1_product_refs_probe.py --gate
python3 scripts/onto1_d2_normalization_pack.py --gate
```

| 事实 | 值 | 复核方式 |
|---|---|---|
| 产品卡 / 产品身份个体 | **13 / 13** | KERT `examples/**/product-cards/PROD-*.md`；`products.ttl` 13 个 `gits:prod_*` |
| 产品引用出现次数 | **40** | `prerequisite_product_ids` **12** + `complementary_products` **28** |
| `mutex_product_ids` | **0**（13/13 空数组） | 见 §4 零实例 |
| 不同取值 | **12** | 见 §2 勾选表 |
| 能解析到真实卡的引用 | **0 / 12** | 投影 `relationInstances: 0`（`UNRESOLVED.json`） |
| 账户关系位（**不计入 40**） | **12 处**，取值同为 `SETTLEMENT_ACCOUNT` | `admission_criteria.requiredAccountRelationship` |

> 与《D2 请求函》§3 的计数**逐字一致**；本包另外把"账户关系位 12 处"独立列出，因为它是 `SETTLEMENT_ACCOUNT` 定性的关键（§3.1）。

### 1.1 逐卡片明细（哪张卡的哪个字段）

行号为该卡片内行号；前置 = `prerequisite_product_ids`，互斥 = `mutex_product_ids`，配套 = `complementary_products`，账户关系 = `admission_criteria.requiredAccountRelationship`。

| # | 卡片 | 前置产品（行） | 互斥产品（行） | 配套产品（行） | 账户关系（行） |
|---|---|---|---|---|---|
| 1 | `PROD-CM-001` 现金池 | `SETTLEMENT_ACCOUNT`（19） | `[]`（20） | `SETTLEMENT_ACCOUNT`、`CORPORATE_E_BANK`（30） | `SETTLEMENT_ACCOUNT`（26） |
| 2 | `PROD-CM-002` 资金归集 | `SETTLEMENT_ACCOUNT`（19） | `[]`（20） | `SETTLEMENT_ACCOUNT`、`CORPORATE_E_BANK`、`CASH_POOL`（30） | `SETTLEMENT_ACCOUNT`（26） |
| 3 | `PROD-CM-003` 法人账户透支 | `SETTLEMENT_ACCOUNT`（19） | `[]`（20） | `SETTLEMENT_ACCOUNT`、`WORKING_CAPITAL_LOAN`（30） | `SETTLEMENT_ACCOUNT`（26） |
| 4 | `PROD-CB-001` 跨境人民币结算 | `SETTLEMENT_ACCOUNT`（19） | `[]`（20） | `SETTLEMENT_ACCOUNT`、`FX_FORWARD`（30） | `SETTLEMENT_ACCOUNT`（26） |
| 5 | `PROD-CB-002` 内保外贷 | `SETTLEMENT_ACCOUNT`（19） | `[]`（20） | `SETTLEMENT_ACCOUNT`、`CROSS_BORDER_RMB_SETTLEMENT`（30） | `SETTLEMENT_ACCOUNT`（26） |
| 6 | `PROD-FIN-001` 流动资金贷款 | `SETTLEMENT_ACCOUNT`（19） | `[]`（20） | `SETTLEMENT_ACCOUNT`、`CORPORATE_E_BANK`、`CASH_MANAGEMENT`（30） | `SETTLEMENT_ACCOUNT`（26） |
| 7 | `PROD-FIN-002` 应收账款质押融资 | `SETTLEMENT_ACCOUNT`（19） | `[]`（20） | `SETTLEMENT_ACCOUNT`、`RECEIVABLE_LEDGER_TOOL`（30） | `SETTLEMENT_ACCOUNT`（26） |
| 8 | `PROD-FIN-003` 订单融资 | `SETTLEMENT_ACCOUNT`（19） | `[]`（20） | `SETTLEMENT_ACCOUNT`、`ORDER_RECEIVABLE_CLOSED_ACCOUNT`（30） | `SETTLEMENT_ACCOUNT`（26） |
| 9 | `PROD-IB-001` 并购贷款 | `SETTLEMENT_ACCOUNT`（19） | `[]`（20） | `SETTLEMENT_ACCOUNT`、`FINANCIAL_ADVISORY`（30） | `SETTLEMENT_ACCOUNT`（26） |
| 10 | `PROD-SET-001` 单位结算账户 | `[]`（19） | `[]`（20） | `CORPORATE_E_BANK`、`CASH_MANAGEMENT`（30） | `null`（26） |
| 11 | `PROD-SET-002` 国内保理 | `SETTLEMENT_ACCOUNT`（19） | `[]`（20） | `SETTLEMENT_ACCOUNT`、`CORPORATE_E_BANK`（30） | `SETTLEMENT_ACCOUNT`（26） |
| 12 | `PROD-TF-001` 银行承兑汇票 | `SETTLEMENT_ACCOUNT`（19） | `[]`（20） | `SETTLEMENT_ACCOUNT`、`DISCOUNT_SERVICE`（30） | `SETTLEMENT_ACCOUNT`（26） |
| 13 | `PROD-TF-002` 国内信用证 | `SETTLEMENT_ACCOUNT`（19） | `[]`（20） | `SETTLEMENT_ACCOUNT`、`BANK_ACCEPTANCE_DRAFT`（30） | `SETTLEMENT_ACCOUNT`（26） |

- 合计：前置 **12** + 配套 **28** + 互斥 **0** = **40**；账户关系位 **12**（独立字段，不计入 40）。
- 40 行**展开版**（逐条一行，含文件路径与关系名）：`evidence/d2-per-card-detail.md`。
- `PROD-SET-001` 是唯一前置为空、账户关系为 `null` 的卡 —— 这本身是 `SETTLEMENT_ACCOUNT` 定性的旁证（§3.1）。

---

## 2. 最小勾选决策表（**这是你的输出位**）

> 序号为本包重排（按次数降序）。与《D2 请求函》§4 的原序号对照：
> 原 1→本 1；原 2→本 2；原 3→本 3；原 4→本 5；原 5→本 6；原 6→本 12；原 7→本 4；原 8→本 9；
> 原 9→本 11；原 10→本 10；原 11→本 7；原 12→本 8。
> 两处**新增**（未在请求函 §4 出现）：本 §3.1 的"账户关系位 12 处"与本 §4 的"零实例"。

| # | 取值 | 次数 | 命中卡片数 | 候选归一化映射 | 证据强度 | 建议分类（**非裁定**） | 产品 Owner 勾选 |
|---|---|---|---|---|---|---|---|
| 1 | `SETTLEMENT_ACCOUNT` | 24 | 12 | `（非产品）账户关系取值`；`PROD-SET-001` | 强／弱 | 错误引用（账户关系被写入产品关系位）；账户关系位保留 | ☐ 有效待补 → PROD-SET-001 / ☐ 有效待补 → 需新增卡（对公结算账户） / ☐ 错误引用（非产品：账户关系） / ☐ 作废 |
| 2 | `CORPORATE_E_BANK` | 5 | 5 | `（非产品）渠道`；`PROD-*（无）` | 强／无 | 错误引用（渠道非产品）或 有效待补（须先做跨仓身份对齐） | ☐ 有效待补 → 需新增卡（企业网银） / ☐ 有效待补 → GITS 侧既有产品身份（企业网上银行） / ☐ 错误引用（非产品：渠道） / ☐ 作废 |
| 3 | `CASH_MANAGEMENT` | 2 | 2 | `（非产品）产品族 CASH_MANAGEMENT` | 强 | 错误引用（族名写入产品位）——若保留该语义需另立族级关系 | ☐ 错误引用（族编码非产品） / ☐ 有效待补 → 具体 PROD-CM-00x（由 Owner 指定成员） / ☐ 作废 |
| 4 | `BANK_ACCEPTANCE_DRAFT` | 1 | 1 | `PROD-TF-001` | 强 | 有效待补 → PROD-TF-001 | ☐ 有效待补 → PROD-TF-001 / ☐ 有效待补 → 需新增卡 / ☐ 错误引用 / ☐ 作废 |
| 5 | `CASH_POOL` | 1 | 1 | `PROD-CM-001`；`品类 CM_CASH_POOLING（非 PROD-*）` | 强／弱 | 有效待补 → PROD-CM-001 | ☐ 有效待补 → PROD-CM-001 / ☐ 有效待补 → 需新增卡 / ☐ 错误引用 / ☐ 作废 |
| 6 | `CROSS_BORDER_RMB_SETTLEMENT` | 1 | 1 | `PROD-CB-001` | 强 | 有效待补 → PROD-CB-001 | ☐ 有效待补 → PROD-CB-001 / ☐ 有效待补 → 需新增卡 / ☐ 错误引用 / ☐ 作废 |
| 7 | `DISCOUNT_SERVICE` | 1 | 1 | `PROD-*（无）` | 无 | 有效待补（需新增卡或定性为服务） | ☐ 有效待补 → 需新增卡 / ☐ 错误引用（若定性为服务非产品） / ☐ 作废 |
| 8 | `FINANCIAL_ADVISORY` | 1 | 1 | `PROD-*（无）` | 无 | 有效待补（须先定性产品 / 服务） | ☐ 有效待补 → 需新增卡 / ☐ 错误引用（若定性为服务非产品） / ☐ 作废 |
| 9 | `FX_FORWARD` | 1 | 1 | `PROD-*（无）` | 无 | 有效待补（需新增卡）或 错误引用（若定性为非产品） | ☐ 有效待补 → 需新增卡 / ☐ 有效待补 → GITS 侧既有产品身份 / ☐ 错误引用 / ☐ 作废 |
| 10 | `ORDER_RECEIVABLE_CLOSED_ACCOUNT` | 1 | 1 | `（非产品）账户` | 强 | 错误引用（账户被写入产品关系位） | ☐ 错误引用（非产品：账户） / ☐ 有效待补 → 需新增卡 / ☐ 作废 |
| 11 | `RECEIVABLE_LEDGER_TOOL` | 1 | 1 | `（非产品）工具` | 强 | 错误引用（工具被写入产品关系位） | ☐ 错误引用（非产品：工具） / ☐ 有效待补 → 需新增卡 / ☐ 作废 |
| 12 | `WORKING_CAPITAL_LOAN` | 1 | 1 | `PROD-FIN-001` | 强 | 有效待补 → PROD-FIN-001 | ☐ 有效待补 → PROD-FIN-001 / ☐ 有效待补 → 需新增卡 / ☐ 错误引用 / ☐ 作废 |
| | **合计** | **40** | 13 张卡 | | | | |

> 逐字同源文件：`evidence/d2-checklist-table.md`（sha256 `04df69e1a02ed32f…`）。
>
> **证据强度口径**：`强` = 有决定性回源（名称逐字一致或语义一一对应）；`弱` = 名称近似或存在第二身份可能；
> `无` = 本卡集内无 `PROD-*` 候选（**不等于"不是产品"**）。

---

## 3. 逐取值证据卡（候选 + 强度 + 回源 + 反证）

> 回源位置标注 `KERT:行` / `GITS:行`；**78 条回源全部经机器校验**（文件存在 + 行内容含所引字样），
> 校验逻辑见 `scripts/onto1_d2_normalization_pack.py` 的 `verify_ref()` 与自检项 `G4`。

### 3.1 `SETTLEMENT_ACCOUNT`（24 处 / 12 张卡）——单点影响面最大

**候选 A（建议）：账户关系取值，非产品。强度 = 强。**

| 回源 | 内容 |
|---|---|
| `KERT:…/PROD-CM-001.md:26` | `requiredAccountRelationship: SETTLEMENT_ACCOUNT`（12 张卡同构，`PROD-SET-001` 为 `null`） |
| `KERT:src/kert/application/product_recommendation/eligibility.py:547` | `required_rel = criteria.get("requiredAccountRelationship")` |
| `KERT:…/eligibility.py:552` | `if required_rel not in rels:` —— 与**客户账户关系事实**比对 |
| `KERT:scripts/product_recommendation_golden_benchmark.py:8` | `rel = ["SETTLEMENT_ACCOUNT"] if customer.get("hasAccount") else []` |
| `KERT:tests/integration/test_sp15_contract_conformance.py:155` | `"accountRelationships": ["SETTLEMENT_ACCOUNT"]` |
| `GITS:…/V021__corporate_product_knowledge_seed.sql:44` | 该 token 还是**关键特性**取值 |

⇒ 同一 token **至少出现在三个槽位**（产品位 / 账户关系位 / 能力特性位）。在**账户关系位**上它有可执行消费者：
KERT 把它当客户账户关系事实与卡上要求比对。**12 处账户关系位不计入 40**，本身就是请求函 §3 的计数基础。

**反证（必须同时看到）**：该证据只证明"账户关系位"的读法；**同 token 不同位 ≠ 同义**，不能据此断言产品位的 24 处也必是账户关系，故并列候选 B。

**候选 B：`PROD-SET-001`（单位结算账户）。强度 = 弱。**

| 回源 | 内容 | 反证 |
|---|---|---|
| `KERT:SET-001.md:4` = `GITS:products.ttl:56` | 卡名 / ttl label 均为「单位结算账户」 | 卡**正文**写的是「对公结算账户」（`KERT:CM-001.md:64` 等 12 处），**不完全一致** |
| `GITS:V021…seed.sql:42` | GITS PI-0 种子另有名为「对公结算账户」的**产品行** | ⇒ 存在**第二个身份候选** |
| `KERT:SET-001.md:26` | `PROD-SET-001` 自身 `requiredAccountRelationship: null` | 未自证"结算账户"是产品 |

**设计影响（提示，不在本包裁定范围）**：若判为"账户关系"，则"前置是账户"这一**事实**在当前谓词集合中**无处承载**，
是否新增关系类型属 TL + 语义架构（合同先行）。此项与 GK17 §5"取值词表未受控仍未解决"同源。

### 3.2 `CORPORATE_E_BANK`（5 处 / 5 张卡）

- 5 处与 5 张卡正文「配套产品：企业网银」**一一对应**（`KERT:CM-001.md:65`、`CM-002.md:65`、`FIN-001.md:77`、`SET-001.md:65`、`SET-002.md:66`）——语义无歧义。
- **性质冲突（关键）**：`GITS:product-taxonomy.yaml:197-198` 把「电子渠道」列为**品类**且 `has_products: false`；
  而 `GITS:V021…seed.sql:51` 把「企业网上银行」登记为**产品行** ⇒ 跨仓同一符号两种身份，须 Owner 定。
- 本卡集内**无** `PROD-*` 候选（强度 无）；本包**不**发明产品身份。

### 3.3 `CASH_MANAGEMENT`（2 处）——唯一同时命中非产品词表的取值

- `KERT:CM-001.md:5` `product_family: CASH_MANAGEMENT`（`CM-002/003` 同码）⇒ token 与**族编码逐字相同**。
- `KERT:CM-001.md:6` 族中文名「现金管理」= 两处正文所写配套名（`KERT:FIN-001.md:77`、`SET-001.md:65`）。
- `GITS:product-taxonomy.yaml:68-69` 族 id `CASH_MANAGEMENT` / 名称「现金管理」；`GITS:V021…seed.sql:61` category 列同码。
- 族有 **3 个成员**（`PROD-CM-001/002/003`）⇒ 指向**任一** `PROD-*` 都是推测，本包**不提供**映射。

### 3.4 `CASH_POOL`（1 处）→ `PROD-CM-001`

三处逐字一致：`KERT:CM-002.md:65`（正文配套名）＝`KERT:CM-001.md:4`（卡名）＝`GITS:products.ttl:21`（ttl label）。
**唯一争议**：`GITS:product-taxonomy.yaml:167-168` 有近名**品类** `CM_CASH_POOLING`（「资金池」，一字之差）⇒ 已列入弱候选。

### 3.5 `WORKING_CAPITAL_LOAN`（1 处）→ `PROD-FIN-001`

`KERT:CM-003.md:65`（正文）＝`KERT:FIN-001.md:4`（卡名）＝`GITS:products.ttl:36`（label）。近名品类 `FIN_WORKING_CAPITAL`（「流动资金」）。

### 3.6 `CROSS_BORDER_RMB_SETTLEMENT`（1 处）→ `PROD-CB-001`

`KERT:CB-002.md:65`（正文）＝`KERT:CB-001.md:4`（卡名）＝`GITS:products.ttl:11`（label）。近名品类 `CB_CROSS_BORDER_SETTLEMENT`（「跨境结算」）。

### 3.7 `BANK_ACCEPTANCE_DRAFT`（1 处）→ `PROD-TF-001`

`KERT:TF-002.md:65`（正文）＝`KERT:TF-001.md:4`（卡名）＝`GITS:products.ttl:66`（label）。近名品类 `TF_ACCEPTANCE_INSTRUMENT`（「承兑工具」）。

### 3.8 `FX_FORWARD`（1 处）—— 本卡集未覆盖

`KERT:CB-001.md:66`「配套产品：远期结售汇」；`GITS:taxonomy:229-230` 品类「外汇服务」`has_products: false`；
`GITS:V021…seed.sql:108` 有「外汇避险（远期结售汇）」产品行。**语义强，`PROD-*` 强度 = 无。**

### 3.9 `DISCOUNT_SERVICE`（1 处）—— 本卡集未覆盖

`KERT:TF-001.md:66`「配套产品：贴现服务」；`GITS:taxonomy:215-216` 品类「票据贴现」`has_products: false`。词尾 `SERVICE` ⇒ 性质待定性。

### 3.10 `FINANCIAL_ADVISORY`（1 处）—— 本卡集未覆盖

`KERT:IB-001.md:66`「配套产品：财务顾问」；`GITS:taxonomy:265-266` **品类**「财务顾问」`has_products: false` ⇒ 与"产品 / 服务"定性直接相关。

### 3.11 `RECEIVABLE_LEDGER_TOOL`（1 处）—— 非产品（工具）

`KERT:FIN-002.md:75`「配套产品：对公结算账户、应收账款台账/确权工具」；
同卡**前置位**写的是「与买方的真实贸易合同、本行结算账户」（`KERT:FIN-002.md:72`）——
**该字段本身就承载了合同 / 账户等非产品项**。
（附：`GITS:V021…seed.sql:27` 有 `RECEIVABLE_LEDGER` 材料项，**近形不同 token**，不构成归一化依据。）

### 3.12 `ORDER_RECEIVABLE_CLOSED_ACCOUNT`（1 处）—— 非产品（账户）

`KERT:FIN-003.md:75`「配套产品：对公结算账户、订单回款封闭账户」；「封闭账户」是**账户用途约束**。
账户在 GITS 侧无独立本体类（`GK17-四项悬置口径裁定` §3.2：身份由 `Transaction.accountId` 承担）。

---

## 4. 零实例事实：`mutuallyExclusiveWith` = `NOT_EVALUATED`（**不得包装为通过**）

| 项 | 值 | 回源 |
|---|---|---|
| `mutex_product_ids` 为空的卡 | **13 / 13** | 每卡第 20 行（`KERT:CM-001.md:20` 等） |
| 卡**正文**中的互斥叙述 | **4 处**：`FIN-001.md:75`、`FIN-002.md:73`、`FIN-003.md:73`、`SET-001.md:64`（后者为"无"） | 机器扫描 |
| 关系实例 | **0** | `GITS:UNRESOLVED.json` `relationInstances: 0` |

**结论（如实声明，不得升格）**：

1. front matter 层面 `mutex_product_ids` **零实例** ⇒ `mutuallyExclusiveWith` 场景记 `NOT_EVALUATED`；
2. 正文里的互斥**叙述**不构成实例，**不得**当作"已有互斥数据"；
3. 「0 目标 0 违规」在 SHACL 规范上合规，但按设计 §6.2 **项目不得解释为业务覆盖已验证**；
4. 该场景**不因** D2 签署而立即可评：即使 D2 给出映射，仍需**实例或受控夹具**才能从 `NOT_EVALUATED` 迁出。

**三场景当前状态（设计 §6.1 五态）**：

| 场景 | 期望目标数 | 实际目标数 | 状态 | 阻塞 |
|---|---|---|---|---|
| `requiresProduct` | 待 D2 裁定 | 0 | `NOT_EVALUATED` | D2 未签（40 处未分类） |
| `complementsProduct` | 待 D2 裁定 | 0 | `NOT_EVALUATED` | D2 未签（40 处未分类） |
| `mutuallyExclusiveWith` | **0** | 0 | `NOT_EVALUATED` | 零实例 + D2 未签 |

---

## 5. 交叉验证：取值与非产品词表的碰撞

**A. 精确同形命中**（脚本自动扫描 13 张卡全部非产品字段 + GITS 分类基线 + GITS 种子）

| 取值 | 命中的非产品词表 | 回源 |
|---|---|---|
| `CASH_MANAGEMENT` | `product_family`（3 张卡）、`gits.taxonomy_id`、`gits.seed_product_category` | `KERT:CM-001.md:5`、`CM-002.md:5`、`CM-003.md:5`；`GITS:taxonomy:68`；`GITS:V021…:61` |
| `SETTLEMENT_ACCOUNT` | `gits.seed_key_feature` | `GITS:V021…:44` |
| 其余 10 个取值 | **无**精确同形命中 | — |

**B. 邻近 / 跨词表语义命中**（同物不同形：族名 / 品类名 / 账户关系位 / GITS 种子 / 正文中文名）

| 取值 | 邻近词表来源 | 回源 | 说明 |
|---|---|---|---|
| `SETTLEMENT_ACCOUNT` | 账户关系位、正文主体名 | `KERT:CM-001.md:26`、`:64` | 同 token 跨槽位；「对公结算账户」≠ 卡名「单位结算账户」 |
| `CORPORATE_E_BANK` | 正文、GITS 品类、GITS 种子 | `KERT:CM-001.md:65`；`GITS:taxonomy:197`；`GITS:V021…:51` | 品类 `has_products:false` vs 种子产品行 ⇒ 跨仓冲突 |
| `CASH_MANAGEMENT` | 族中文名、GITS 族名、种子 category | `KERT:CM-001.md:6`；`GITS:taxonomy:69`；`GITS:V021…:61` | 族名写到产品位 |
| `CASH_POOL` | 正文、GITS 近名品类 | `KERT:CM-002.md:65`；`GITS:taxonomy:167` | 「资金池」vs「现金池」 |
| `WORKING_CAPITAL_LOAN` | 正文、GITS 近名品类 | `KERT:CM-003.md:65`；`GITS:taxonomy:239` | 近名品类「流动资金」 |
| `CROSS_BORDER_RMB_SETTLEMENT` | 正文、GITS 近名品类 | `KERT:CB-002.md:65`；`GITS:taxonomy:221` | 近名品类「跨境结算」 |
| `BANK_ACCEPTANCE_DRAFT` | 正文、GITS 近名品类 | `KERT:TF-002.md:65`；`GITS:taxonomy:203` | 近名品类「承兑工具」 |
| `FX_FORWARD` | 正文、GITS 品类、GITS 种子 | `KERT:CB-001.md:66`；`GITS:taxonomy:229`；`GITS:V021…:108` | 品类 `has_products:false` |
| `DISCOUNT_SERVICE` | 正文、GITS 品类 | `KERT:TF-001.md:66`；`GITS:taxonomy:215` | 品类「票据贴现」`has_products:false` |
| `FINANCIAL_ADVISORY` | 正文、GITS 品类 | `KERT:IB-001.md:66`；`GITS:taxonomy:265` | 品类「财务顾问」`has_products:false` |
| `RECEIVABLE_LEDGER_TOOL` | 正文、GITS 近形材料项 | `KERT:FIN-002.md:75`；`GITS:V021…:27` | 近形不同 token，不作归一化依据 |
| `ORDER_RECEIVABLE_CLOSED_ACCOUNT` | 正文 | `KERT:FIN-003.md:75` | 账户用途约束 |

> 完整机读版：`evidence/d2-cross-vocab.md`（sha256 `dc12bf8e2fdba3a0…`）。
> **一句话**：12 个取值中只有 `CASH_MANAGEMENT` 与 `SETTLEMENT_ACCOUNT` 命中**本仓既有词表**；
> 其余 10 个是"另一套命名"，其中 4 个在 GITS 分类基线里是**品类**、2 个在 GITS 种子里有**产品行**。

---

## 6. 影响面（勾选前请知悉的连带后果）

| 下游 | 现状 | 受本裁定影响的方式 |
|---|---|---|
| **CQ3**（`describesProduct` / 悬空引用） | `NOT_EVALUATED`（`evidence/cq-fixtures/CQ3.json`） | 分类完成前不得迁出；负例已覆盖 40 处悬空引用 |
| **投影**（产品卡 → A-Box） | `relationInstances: 0`，fail-closed | 判"有效待补"的项需**先补实例**才能产出三元组；判"错误引用/作废"的项产出仍为 0（正确结果） |
| **WP7.1**（产品关系展示） | 受 GK17 §1.6 解锁但范围收窄 | 关系项须带"待产品 Owner 定性"标注；本包勾选后才可去标注 |
| **D4 门禁** | "有能无力" | 与 D2 无关，不因本裁定变化 |
| **产品卡写入** | KERT 只读 | 任何"有效待补/更正"都要**产品 Owner 在 KERT 侧执行**（本环境无写权限） |
| **本体**（关系类型） | 谓词 3 个已落盘 | 「账户关系」「族级配套」若无谓词承载，需走合同先行（TL + 语义架构） |

---

## 7. 两个"一次性放行"签字选项（供直接引用，逐字可选）

> 以下为**建议措辞**，产品 Owner 可直接采用、修改或弃用；两选项**互斥**，也可逐行混选（§2 勾选表优先）。

**选项 α（按性质分派 + 逐条映射，推荐）**

> 「1 定为**账户关系**（非产品），24 处产品位引用属**错误引用**；3 定为**产品族编码**，产品位引用**作废**；
> 10、11 定为**非产品（账户 / 工具）**，**错误引用**；4 确认为 `PROD-TF-001`；5 确认为 `PROD-CM-001`；
> 6 确认为 `PROD-CB-001`；12 确认为 `PROD-FIN-001`；7、8、9 暂列**有效待补**（须先定性产品 / 服务，或补卡）；
> 2 暂列**有效待补**，但须先做 GITS「电子渠道 / 企业网上银行」跨仓身份对齐。」

**选项 β（仅按名称对齐，最小改动）**

> 「1 确认为 `PROD-SET-001`；4 确认为 `PROD-TF-001`；5 确认为 `PROD-CM-001`；6 确认为 `PROD-CB-001`；
> 12 确认为 `PROD-FIN-001`；3 为族编码；10、11 为账户 / 工具；2、7、8、9 另行补卡。」

> 若选 β，请特别注意：`SETTLEMENT_ACCOUNT` 仍是账户关系位取值（12 处），
> 出现"同一 token 在位 A 是产品、在位 B 是账户关系"的**双身份**，需在裁定中**明写**，否则投影与校验会各自解释。

---

## 8. 未决期间的禁止动作（本包自我约束，供监督）

- 不把三场景（`requiresProduct` / `complementsProduct` / `mutuallyExclusiveWith`）标 `PASS`；
- 不以 `WAIVED_FOR_DEVELOPMENT` 充当激活依据；
- 不把 SIM / 种子数据静默升级为企业产品权威；
- 不关闭 **R-6** 风险登记；
- 不修改产品卡与 `products.ttl`（KERT 只读）；
- 不新建"权威映射表"（GK17 §1.3：映射先定性后入册）。

---

## 9. 复现与哈希

```bash
# 1) 40 处引用清单（门禁）
python3 scripts/onto1_product_refs_probe.py --gate
# 2) 决策包自检（八项 fail-closed）与变异复验
python3 scripts/onto1_d2_normalization_pack.py --gate
python3 scripts/onto1_d2_normalization_pack.py --selftest
```

| 制品 | 哈希（sha256 前 16） |
|---|---|
| `evidence/d2-normalization-pack.json` | `24c6e24ccb58ad82` |
| `evidence/d2-checklist-table.md` | `04df69e1a02ed32f` |
| `evidence/d2-per-card-detail.md` | `06455d5f1978d25a` |
| `evidence/d2-cross-vocab.md` | `dc12bf8e2fdba3a0` |
| `evidence/wi_a5_d2_pack-20260920T142117Z.log` | `c946bf2998fd1786` |
| `evidence/wi_a5_d2_pack_selftest-20260920T142117Z.log` | `63fc855292db3038` |

自检结果：`--gate` **G1~G8 全 PASS**（78 条回源 0 问题）；`--selftest` **PASS**（M0 对照 + M1~M5 变异全被拦下）。
其中 `G4` 在开发期曾拦下一次**自伤**（证据条目缺仓根 ⇒ 13 条回源落空），已记 `FAILURES.md` **FAIL-2026-09-20-05**。

---

## 10. 签署区

| 项 | 内容 |
|---|---|
| 逐行勾选 | 见 §2 表「产品 Owner 勾选」列（12 行） |
| 一次性措辞（可选） | ☐ 采用选项 α ☐ 采用选项 β ☐ 自行措辞（附后） |
| 「有效待补」项的补齐方式 | ☐ 由产品 Owner 提供 `PROD-*` 映射表 ☐ 由本 Loop 按裁定生成候选映射后再确认 |
| 是否同步批准 SIM 临时模拟权威声明（产品身份部分） | ☐ 批准 ☐ 有条件批准（条件：______） ☐ 不批准 |
| 签署人 / 日期 | |
| 附件哈希 | 本文件 §9 表 |
