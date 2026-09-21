# 40 条产品引用｜待裁定清单 V1.0（交产品 Owner 签）

| 项 | 值 |
|---|---|
| 用途 | 把 `UNRESOLVED.json` 中 **40 条产品关系引用**转成**产品 Owner 可逐条裁定**的清单 |
| 数据来源 | `specs/knowledge-architecture/instances/product/UNRESOLVED.json`（当日实测） |
| 裁定人 | **产品 Owner**（TL/实现负责人**不得**代裁） |
| 我方状态 | `NOT_EVALUATED`（裁定前比较/前置/配套章节中这些关系**不显示确定结论**） |
| 关联 | `ONTO1-SCENARIO-PI-Owner决定登记-V1.0.md`；`ONTO1-SCENARIO-PI-CQ与验证夹具-V1.0.md` CQ3-S4 |

---

## 0. 先说结论：**40 条其实是 12 个符号**

| 项 | 数值 |
|---|---:|
| 原始引用条数 | **40** |
| 去重后**不同符号数** | **12** |
| 其中可机械判定的（符号 ↔ 已有产品卡命名不一致） | **7** |
| 其中概念错误（拿产品族名当产品） | **1** |
| 需要你判断「是否属于本行产品目录」 | **4** |
| 属性分布 | `complementsProduct` 28 条 + `requiresProduct` 12 条（**无** `mutuallyExclusiveWith`） |

⇒ **你（或产品负责人）只需做 12 个判断，不是 40 个。**

---

## 1. 类别一：**可直接映射**（7 项，建议判为"有效待补 → 映射到已有产品卡"）

推理依据：符号名与本行已有 13 张产品卡之一**语义相同**，差异只是命名风格（产品卡用 `PROD-XX-NNN` + 中文名，引用处用英文符号）。

| # | 引用符号 | 次数 | 引用它的产品卡 | **建议映射到** | 依据 |
|---|---|---:|---|---|---|
| 1 | `SETTLEMENT_ACCOUNT` | **24** | 12 张卡（几乎全部） | `PROD-SET-001` 单位结算账户 | 语义一致；影响面最大（24/40） |
| 2 | `CASH_POOL` | 1 | PROD-CM-002 资金归集 | `PROD-CM-001` 现金池 | 同名 |
| 3 | `WORKING_CAPITAL_LOAN` | 1 | PROD-CM-003 法人账户透支 | `PROD-FIN-001` 流动资金贷款 | 同名 |
| 4 | `BANK_ACCEPTANCE_DRAFT` | 1 | PROD-TF-002 国内信用证 | `PROD-TF-001` 银行承兑汇票 | 同名 |
| 5 | `CROSS_BORDER_RMB_SETTLEMENT` | 1 | PROD-CB-002 内保外贷 | `PROD-CB-001` 跨境人民币结算 | 同名 |
| 6 | `CORPORATE_E_BANK` | 5 | 5 张卡 | **待定**：本行 13 张卡中无"企业网银" | 见类别三（若产品 Owner 认定企业网银属于渠道而非产品 ⇒ 判"作废引用"） |
| 7 | `DISCOUNT_SERVICE` | 1 | PROD-TF-001 银行承兑汇票 | **待定**：本行无"票据贴现"卡 | 见类别三 |

> 1~5 号建议判定：**有效待补**（产品存在，只是引用处用了符号名）⇒ 动作 = 建立符号↔`PROD-*` 映射（由别名配置承载，**不改产品卡**）。

## 2. 类别二：**概念错误**（1 项，建议判为"错误引用"）

| # | 引用符号 | 次数 | 引用它的卡 | 问题 | 建议动作 |
|---|---|---:|---|---|---|
| 8 | `CASH_MANAGEMENT` | 2 | PROD-FIN-001、PROD-SET-001 | 这是**产品族名**（现金管理族），**不是产品** | 判**错误引用** ⇒ 由产品 Owner 指出应指向的具体产品（`PROD-CM-001/002/003`）或删除该引用 |

## 3. 类别三：**需产品 Owner 判断是否属于产品目录**（4 项）

这些符号**看起来是「工具/账户/服务/渠道」而不是可售产品**，落在产品目录边界之外。需要你决定三选一：

| # | 引用符号 | 次数 | 引用它的卡 | 表面性质 | 三选一 |
|---|---|---:|---|---|---|
| 9 | `CORPORATE_E_BANK` | 5 | PROD-CM-001/002、PROD-FIN-001、PROD-SET-001/002 | 电子渠道 | ① 有效待补（补一张产品卡）② 错误引用（应指向别的产品）③ 作废（渠道不属于产品目录） |
| 10 | `FX_FORWARD` | 1 | PROD-CB-001 跨境人民币结算 | 外汇产品（远期结售汇） | 同上（可能是"有效但未出卡"） |
| 11 | `RECEIVABLE_LEDGER_TOOL` | 1 | PROD-FIN-002 应收账款质押融资 | 工具 | 同上 |
| 12 | `ORDER_RECEIVABLE_CLOSED_ACCOUNT` | 1 | PROD-FIN-003 订单融资 | 账户 | 同上 |

## 4. 裁定模板（逐条填，签完交我）

```
符号:                          ← 上表 1~12
判定: [ ] 有效待补  [ ] 错误引用  [ ] 作废
若"有效待补" → 对应产品: PROD-___-___   （或"需新增产品卡，编号待分配"）
若"错误引用" → 应指向:                  （或"删除该引用"）
若"作废"   → 作废理由:
裁定人 / 日期:
```

**签完后我的动作**（不需要你再介入）：
1. 把「有效待补」映射写进投影配置的别名表（SIM，`projection-config.json` 既有机制）；
2. 触发 SIM 关系投影重建（`sim/product-relations.SIM.ttl` 为生成产物）；
3. 重跑 `UNRESOLVED.json` ⇒ 未决数应从 **40 → 0（或仅剩作废登记）**；
4. CQ3-S4 场景从 `NOT_EVALUATED` 转 `DESIGN_ONLY→` 可评测；
5. 比较/前置/配套章节可显示确定关系（不再是"待核验"）。

---

## 5. 对页面的具体影响（为什么值得做）

| 页面区域 | 现状（12 符号未裁定） | 裁定后 |
|---|---|---|
| 适用边界 → 前置/配套产品 | 12 个产品的关系**全部**显示"待核验" | 显示真实前置/配套产品（可点击跳转） |
| 同类产品比较章节 | 只有维度表，**关系列缺失** | 可补"本行产品间关系"维度（A 来源主体） |
| 产品知识助手 | 问到"这个产品需要先开什么账户"时**必须拒答** | 可依据裁定结论回答（仍附证据回链） |

## 6. 复现命令（任何时点可重算）

```bash
python3 - <<'PY'
import json, collections
d = json.load(open('specs/knowledge-architecture/instances/product/UNRESOLVED.json'))
un = d['unresolved']
print('原始条数', len(un), '| 去重符号数', len({x['referenced_symbol'] for x in un}))
print('属性分布', collections.Counter(x['ontology_property'] for x in un))
agg = collections.defaultdict(lambda: {'n': 0, 'cards': set()})
for x in un:
    agg[x['referenced_symbol']]['n'] += 1
    agg[x['referenced_symbol']]['cards'].add(x['card_product_id'])
for s, v in sorted(agg.items(), key=lambda kv: -kv[1]['n']):
    print(f"{s:32} x{v['n']:<3} 来自 {len(v['cards'])} 张卡")
PY
```

## 7. 非声明

- 本清单是**待裁定材料**，不是裁定结论；类别一的映射是 **TL 初判（`EXPERT_JUDGMENT`）**，须产品 Owner 确认；
- 我不改任何产品卡、不改 taxonomy、不改本体权威制品；
- 未标 `PASS`；未解除 `QUARANTINED_UNRESOLVED` 隔离（`formalRelationRelease` 仍 `NOT_AUTHORIZED`）。
