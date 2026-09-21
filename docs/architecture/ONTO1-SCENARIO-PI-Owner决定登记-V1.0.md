# 产品解读重构｜Owner 决定登记 V1.0（2026-09-21）

| 项 | 值 |
|---|---|
| 登记人 | Tech Lead（产品解读重构实现负责人） |
| 性质 | **决定登记 + 执行边界**；不构成 `QA_PASS`、不构成激活、不构成标准符合性声明 |
| 输入 | Owner 2026-09-21 答复：「1 产品比较：选 B（同业材料脱敏只读展示），若无法获得权威材料，请找同业相似产品进行造数；2 演示数据临时权威：同意生效」 |
| 关联件 | `GITS-Bank-产品解读与知识-需求变更方案-V1.0.md` §3 / §5；`ONTO1-SCENARIO-PI-影响面分析-V1.0.md`；`ONTO1-SCENARIO-PI-变更预测表-V1.0.md`；`ONTO1-SCENARIO-PI-CQ与验证夹具-V1.0.md`；`ONTO1-SIM临时模拟权威声明草案.md`（含 2026-09-21 附件） |

---

## 决定 ① 产品比较章节 = **B 方案 + 造数授权**

### 1.1 你批的是什么（逐字边界）

| 项 | 内容 |
|---|---|
| 方案 | **B：公开参考只读展示（脱敏）** —— 同业资料以「**公开参考（非权威）**」明确标注呈现：去机构名、**不进门禁**、不参与 READY 判定、标注来源未验证 |
| 附加授权 | 若无法获得权威材料 ⇒ **允许以"同业相似产品"造数**补充 |
| 我登记的豁免范围 | **仅「展示口径」**：允许在**内部**产品中心页面展示公开参考内容与 SIM 对照数据 |

### 1.2 明确**未**获豁免（红线仍在，我不得越过）

依据 KERT `examples/product-recommendation-assets/01_raw/_public_reference/README.md` 原文：

| # | 仍未豁免 | 原文依据 |
|---|---|---|
| N-1 | 公开参考**不得作为任何产品卡字段的权威依据** | 「不得作为任何产品卡字段的权威依据」 |
| N-2 | 引用本区证据的产品卡**永久停留 `CANDIDATE`**，门禁自动阻断 | 同文件「门禁自动阻断，无需人工判断」 |
| N-3 | 44 条证据 100% `usage=VERIFICATION_ONLY`，**不得支撑**本机构字段、`HardRule`、`INTERPRETATION_READY`、`RECOMMENDATION_READY` | 同文件「红线复述」 |
| N-4 | **不得出现来源机构名称**（产品卡 `institution` 统一 `DEMO-BANK`；同样适用于页面、SIM 数据、对比表） | 合规约束 C-2 |
| N-5 | **不向外分发**（仅内部研发/内部使用）⇒ **本页不得用于对客交付** | 合规约束 C-2 |
| N-6 | `authorityLevel` 只能取 `PUBLIC_PRICE_DISCLOSURE` / `PUBLIC_MARKETING` | 证据能力上限 |
| N-7 | 可复现性 `UNVERIFIED`、来源补证未闭（`F-L00-10`）⇒ 页面必须标注「来源未验证」 | 同上 |
| N-8 | 本场景**不解除** `_public_reference` 红线本身；豁免只作用于本页展示 | 需求变更方案 §3「我不做的事情」 |

### 1.3 造数（SIM 同业对照）四条硬约束

| # | 约束 | 理由 |
|---|---|---|
| S-1 | 造数必须分类为 **SIM**：`simulationOnly=true` / `isDemo=true` / `evidenceClass=SAMPLE_EVIDENCE`；**绝不**写入产品卡字段、taxonomy、`CONTRACTS_INDEX` | 与 SIM 框架一致；防冒充 |
| S-2 | **不得出现任何真实机构名称**（含可识别的代称）；只允许中性代称（如「同业示例产品 A/B」） | 合规 C-2 |
| S-3 | **不得在价格维度放造数数字**：价格维度统一表述为「以各行公示为准，需单独核验」；比较只保留客观维度（主要用途/资金发生方式/使用灵活度/计息关注点/资料关注点/典型限制） | 需求 §7 维度本身不含具体价格；价格最敏感，造数价格会构成误导 |
| S-4 | 造数内容须经**产品经理/产品 Owner + 合规**确认后方可用于演示；**不得由工程单方定稿** | 防工程自造业务口径 |

### 1.4 事实输入：B 现有材料**质量不足以单独支撑页面**（当日实测）

| sourceId | 状态 | 抽出条目 | `unknownFieldRate` |
|---|---|---:|---:|
| `PUB-PRICE-001` | `AVAILABLE` | 24 | 0.119 |
| `PUB-PRICE-002` | `AVAILABLE` | 20 | **0.76**（76% 字段抽不出） |

⇒ **结论（诚实汇报）**：B 区当前只有 **2 份公示价目**，且第二份抽出质量很差，**无法**覆盖比较表所需的 6 个客观维度。因此本页比较章节的实际构成应为：

```
主体：A 本行产品间对比（13 张产品卡的真实关系数据：前置/互斥/配套）
补充：B 公开参考（脱敏、非权威、来源未验证标注）
补充：SIM 同业对照（按 S-1~S-4 造数，产品+合规确认后启用）
```
**不会出现"只有造数"的页面**；造数是补充列，不是事实来源。

### 1.5 落地动作与门禁断言

| # | 动作 | 责任 | 状态 |
|---|---|---|---|
| 1 | KERT 侧登记本次展示豁免（红线原文在 KERT 仓，需在该仓留痕，不得只在 GITS 侧自述） | TL（OD-PI-09 已授权进入；**不 push/merge**） | 待做 |
| 2 | GITS 侧把「比较数据来源三类（A/B/SIM）」写进场景合同说明与 `ComparisonSet` 使用约束 | TL | 本件 + PC README |
| 3 | 造数数据集设计（含中性代称、无价格数字、SIM 标记） | TL 出草案 → 产品+合规确认 | 待做 |
| 4 | 门禁断言（**负例优先**）：① 对比数据缺 `simulationOnly` ⇒ FAIL；② 出现机构名 ⇒ FAIL；③ 价格维度出现造数数字 ⇒ FAIL；④ 造数数据参与 `INTERPRETATION_READY`/`RECOMMENDATION_READY` 判定 ⇒ FAIL | TL（Wave 4 门禁） | 设计就绪，未实现 |
| 5 | 页面对客场景拦截：本页若被复用到对客交付 ⇒ 具名拒绝（N-5） | TL | 设计就绪 |

---

## 决定 ② SIM 临时模拟权威声明：**Owner 同意生效**

### 2.1 状态判定（**不得**简化为"已生效"）

| 项 | 状态 |
|---|---|
| Owner 同意 | ✅ **已获**（2026-09-21，产品身份部分） |
| 声明是否 `EFFECTIVE` | ❌ **尚未** —— 声明 §A.4 明文：生效前必须完成 ① Schema 校验 ② 正负夹具 ③ 来源/时点/版本校验 ④ **独立 QA** |
| 我的登记状态 | `OWNER_APPROVED_PENDING_TECHNICAL_PRECONDITIONS` |
| 不得声称 | 不得说声明已生效、不得把 SIM 当生产权威、不得据此满足激活门禁 |

### 2.2 范围限定（两条签署栏分置）

| 签署栏 | 覆盖术语 | 本决定是否覆盖 |
|---|---|---|
| 产品 Owner（产品身份部分） | `ProductOffering`（= `SIM-PRODUCT-CATALOG`） | ✅ Owner 已同意 |
| 数据 Owner（客户/集团身份部分） | `Party`/`Organization`/`LegalEntity`/`CustomerRole`/`EnterpriseGroup`/`GroupMembership` | ⚠ **未覆盖**（本场景不需要；若后续客户体检/推荐要用，需数据 Owner 另行签署） |
| 业务 Owner 会签 | — | ⚠ 未签 |

### 2.3 四项技术前置（谁做）

| # | 前置 | 责任 | 我方可立即做的部分 |
|---|---|---|---|
| P1 | Schema 校验（三个 SIM 载体对 Schema 的合规性） | TL | ✅ 可做（`projection-config.json` + `sim/*.ttl` 已存在，可写校验脚本） |
| P2 | 正负夹具（含 `MISSING_SOURCE_IDENTIFIER` 负例、freshness 超期负例） | TL | ✅ 可做（夹具设计已在 CQ 件 §3） |
| P3 | 来源/时点/版本校验（`SourceIdentifier` 六必填 + freshness 相对 `scenarioAsOf`） | TL | ✅ 可做 |
| P4 | **独立 QA** | **独立角色**（开发角色**禁止自签**） | ❌ 不可代办 |

⇒ 我方**今天即可启动 P1~P3**；P4 需你指定独立 QA 角色（或沿用既有 `independent_qa` 安排）。

### 2.4 生效期间仍必须遵守

1. 页面/接口所有 SIM 数据带 `simulationOnly` 标记并显示**演示**标识；
2. **不得**把 SIM 载体写入正式制品（OWL/合同 Schema/`CONTRACT_INDEX`）；
3. **不得**用 SIM 数据作为 `PASS` 的唯一依据去满足激活门禁；
4. 退出条件（正式源系统接入 / 权威矩阵确认签署 / 激活要求 / 书面撤回）触发 ⇒ 30 日内完成下线与切换登记，台账由 TL 维护；
5. 声明文件本体（`ONTO1-SIM临时模拟权威声明草案.md`）当前为**另一执行者的未跟踪在飞文件** ⇒ 签署页/决议附件的落盘由 ONTO1 执行者完成，本件仅登记 Owner 授权输入，**不代改该文件**。

---

## 决定 ③（仍未决）：40 条悬空产品引用分类

- 归属：**产品 Owner**（不是 TL、不是实现负责人）；
- 现状：`UNRESOLVED.json` 已登记 40 条（`relationInstances=0`，`formalRelationRelease=NOT_AUTHORIZED`）；
- 我方可先行：**「按页面影响排序的 40 条待裁定清单」**（不需要你做决定，做完交产品负责人签）；
- 未签影响：比较/前置/互斥章节中这些关系保持「待核验」，页面不显示确定结论。

---

## 复现命令

```bash
# 决定①的实测输入（B 区材料质量）
sed -n '28,40p' /home/szf/dev/Leibniz-KERT/examples/product-recommendation-assets/01_raw/_public_reference/README.md

# 决定②的现状（SIM 载体与配置）
python3 -c "import json;d=json.load(open('specs/knowledge-architecture/instances/product/projection-config.json'));print(d['simulationOnly'], d['formalRelationRelease'], d['version'])"
head -6 specs/knowledge-architecture/instances/product/sim/product-relations.SIM.ttl

# 决定③的现状
python3 -c "import json;d=json.load(open('specs/knowledge-architecture/instances/product/UNRESOLVED.json'));print(d['unresolvedReferenceCount'], d['relationInstances'])"
```
