# 产品解读重构｜Owner 决定登记 V1.0（2026-09-21）

| 项 | 值 |
|---|---|
| 登记人 | Tech Lead（产品解读重构实现负责人） |
| 性质 | **决定登记 + 执行边界**；不构成 `QA_PASS`、不构成激活、不构成标准符合性声明 |
| 输入 | Owner 2026-09-21 答复：「1 产品比较：选 B（同业材料脱敏只读展示），若无法获得权威材料，请找同业相似产品进行造数；2 演示数据临时权威：同意生效」 |
| 关联件 | `GITS-Bank-产品解读与知识-需求变更方案-V1.0.md` §3 / §5；`ONTO1-SCENARIO-PI-影响面分析-V1.0.md`；`ONTO1-SCENARIO-PI-变更预测表-V1.0.md`；`ONTO1-SCENARIO-PI-CQ与验证夹具-V1.0.md`；`ONTO1-SIM临时模拟权威声明草案.md`（含 2026-09-21 附件） |

---

## 决定 ① 产品比较章节 = **B 方案 + 造数授权**

### 1.0 口径纠正（Owner 2026-09-22 指正，**以本节为准**）

我上一版把「公开参考」的红线按**摄入路径**的原文直接套到**只读展示路径**上，导致三条过度限制。纠正如下：

| # | 我的原登记（**作废**） | Owner 纠正 | **采纳后的口径** |
|---|---|---|---|
| ① | 「公开参考不得作为产品卡字段的权威依据」被理解为限制展示 | 本行产品卡**就是**权威（且其字段本身就是**授权造数**产物）；公开参考不作权威**但可以造数** | **保留**：公开参考不得作为**本行产品卡字段**的权威依据。**新增**：本行 13 张产品卡在本中心为**权威呈现对象**（其内容为 SIM 授权造数，范围为"本系统内权威"，**不等于**银行正式制度） |
| ② | 「引用本区证据的产品卡永久 CANDIDATE、门禁自动阻断」被扩展为"展示即阻断" | **不对**：只是**只读对比**，**不构成"引用"** | **作废该扩展**。机械判据收敛为：**触发条件是"产品卡字段的 `evidenceRefs` 指向 `_public_reference` 证据"**。因此对比表的公开参考行**不得把该证据写入任何产品卡字段的 `evidenceRefs` 链**——只带展示标签 ⇒ 不触发门禁阻断（Owner 纠正正确） |
| ③ | N-3「44 条证据 100% VERIFICATION_ONLY，不得支撑本机构字段/HardRule/`INTERPRETATION_READY`/`RECOMMENDATION_READY`」 | **看不懂**（Owner） | **人话**：这批同业材料的用途只有一个——"证明我们的程序能读懂文件"。**不能用它们给我们自己的产品字段填值**，也不能拿它们去判断"我们的产品知识够不够发布（READY）"。**只是把同业材料当对照摆出来看，不违反这一条** |
| ④ | S-2「不得出现任何真实机构名（含可识别代称）」 | **可以用一个脱敏代称** | **修正为**：使用**脱敏代称**（如「同业 A」「M 行（脱敏）」）；**不得**出现真实机构全称/可检索到的标识 |
| ⑤ | N-7「页面必须标注来源未验证」 | **没必要**（整个系统数据都是演示数据） | **取消逐行"来源未验证"标注**；对比行**只保留一个**来源标签：「公开参考（非权威）」或「同业示例（SIM）」 |
| ⑥ | N-5「不得对外分发」 | **没问题**（同意） | **保留**：本页不得用于对客交付；若复用到对客场景 ⇒ 具名拒绝 |

**DEMO/环境标识 —— Owner 已决定（2026-09-22）：保留。**

| 项 | 内容 |
|---|---|
| 决定 | **保留**全系统「演示数据」标识 |
| 实现口径 | 顶部一行"演示数据"胶囊 + 页脚重复声明；文案不得被业务配置关闭（`PI-BR-009`/`PI-FR-003`/`PI-FR-093` 保持有效） |
| 未豁免 | `PI-BR-009`、`PI-FR-003`、`PI-FR-093` **全部仍然有效**，无豁免登记 |
| 影响 | 与本场景全部页面设计一致；无需返工 |


### 1.1 你批的是什么（逐字边界）

| 项 | 内容 |
|---|---|
| 方案 | **B：公开参考只读展示（脱敏）** —— 同业资料以「**公开参考（非权威）**」明确标注呈现：去机构名、**不进门禁**、不参与 READY 判定、标注来源未验证 |
| 附加授权 | 若无法获得权威材料 ⇒ **允许以"同业相似产品"造数**补充 |
| 我登记的豁免范围 | **仅「展示口径」**：允许在**内部**产品中心页面展示公开参考内容与 SIM 对照数据 |

### 1.2 红线边界（**按 2026-09-22 纠正后口径**，只保留真实存在的约束）

依据 KERT `examples/product-recommendation-assets/01_raw/_public_reference/README.md`：

| # | 约束 | 触发条件（机械判据） | 原文依据 |
|---|---|---|---|
| N-1 | 公开参考**不得作为本行产品卡字段的权威依据** | 产品卡字段的 `evidenceRefs` 指向 `_public_reference` 证据 | 「不得作为任何产品卡字段的权威依据」 |
| N-2 | 上述字段一旦引用 ⇒ 产品卡**永久 `CANDIDATE`**、门禁自动阻断 | **同上**（同一触发条件）。**只读对比展示不触发**（Owner 2026-09-22 纠正） | 「门禁自动阻断，无需人工判断」 |
| N-3 | 44 条证据 100% `VERIFICATION_ONLY`：**不得给我们自己的字段填值**，**不得**用于 `HardRule`/`INTERPRETATION_READY`/`RECOMMENDATION_READY` 判定 | 该证据出现在字段值/规则/READY 判定链中 | 「红线复述」 |
| N-4 | 不得出现**真实机构名称**；使用**脱敏代称**；产品卡 `institution` 统一 `DEMO-BANK` | 文本中出现真实机构全称/可检索标识 | 合规约束 C-2（**2026-09-22 修正**） |
| N-5 | **不向外分发**（仅内部使用）⇒ 本页不得用于对客交付 | 本页被复用至对客场景 | 合规约束 C-2 |
| N-6 | `authorityLevel` 只能取 `PUBLIC_PRICE_DISCLOSURE` / `PUBLIC_MARKETING` | 证据登记字段 | 证据能力上限 |
| N-7 | ~~页面必须标注「来源未验证」~~ ⇒ **取消**（Owner 2026-09-22）：对比行只保留**一个**来源标签「公开参考（非权威）」或「同业示例（SIM）」 | — | — |
| N-8 | 本场景**不解除**红线本身；本件豁免仅作用于**本页只读展示** | 超出本页使用 | 需求变更方案 §3 |

### 1.3 造数（SIM 同业对照）四条硬约束

| # | 约束 | 理由 |
|---|---|---|
| S-1 | 造数必须分类为 **SIM**：`simulationOnly=true` / `isDemo=true` / `evidenceClass=SAMPLE_EVIDENCE`；**绝不**写入产品卡字段、taxonomy、`CONTRACTS_INDEX` | 与 SIM 框架一致；防冒充 |
| S-2 | 使用**脱敏代称**（如「同业 A」「M 行（脱敏）」）；**不得**出现真实机构全称/可检索标识 | 合规 C-2（2026-09-22 修正） |
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
| 4 | 门禁断言（**负例优先**）：① 对比行缺来源标签或 SIM 行缺 `simulationOnly` ⇒ FAIL；② 出现真实机构名（未用脱敏代称）⇒ FAIL；③ 价格维度出现造数数字 ⇒ FAIL；④ 造数数据参与 `READY` 类判定 ⇒ FAIL；⑤ **公开参考行的 `evidenceRef` 进入任何产品卡字段链** ⇒ FAIL（N-1/N-2 的真实触发条件） | TL（Wave 4 门禁） | 设计就绪，未实现 |
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

### 2.3 四项技术前置（**修正**：不新写脚本，先复用 ONTO1 既有产出）

> **自我修正（2026-09-22）**：我此前说"P1~P3 我方今天即可启动（可写校验脚本）"——**这是错的**，会与 ONTO1 Wave -1 已落地的同题产出重复。当日实测 ONTO1 已有：
> `evidence/wi_a4_sim_migration_verify{,_selftest}-*.log`、`wi_a8_sim_rehearsal{,_full}{,_selftest}-*.log`、`wi_a11_sim_rehearsal_sim4{,_selftest}-*.log`、`C2-D2-SIM-REMEDIATION-REPORT.md`、`SIM-R1-WAVE12-REPORT.md`，以及 `scripts/onto1_cq_fixtures.py`（夹具）、`scripts/onto1_d4_pack.py`（含 `MISSING_SOURCE_IDENTIFIER`/freshness 口径）。
> ⇒ **正确做法 = 核对 + 复用 + 只补缺口**，而不是另建一套。

| # | 前置 | ONTO1 既有产出（复用对象） | 缺口 / 谁做 |
|---|---|---|---|
| P1 | Schema 校验（SIM 载体对 Schema） | `wi_a4_sim_migration_verify`（含 selftest，变异复验已做） | 需核对是否覆盖 `projection-config.json` 版本字段；若缺，**在 ONTO1 Loop 内**补，不另建脚本 |
| P2 | 正负夹具 | `scripts/onto1_cq_fixtures.py` + `evidence/cq-fixtures/CQ*.json`；`wi_a8/a11_sim_rehearsal` 已有演练记录 | 本场景只需**引用** CQ 夹具与演练日志作为声明前置证据；不新增夹具文件 |
| P3 | 来源/时点/版本校验（`SourceIdentifier` 六必填 + freshness 相对 `scenarioAsOf`） | `scripts/onto1_d4_pack.py`（口径）；`wi_a11` 演练 | 同上：核对覆盖度，缺口回 ONTO1 |
| P4 | **独立 QA** | — | ❌ **不可代办**（开发角色禁止自签）⇒ 需 Owner 指定独立角色 |

**编排约束**：本场景**不新写 SIM 校验脚本、不跑 ONTO1 板面门禁**（其门禁预算受限，见 `ONTO1` STATE D-15）；如需补缺口，走 ONTO1 的既有 WI 通道。

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
