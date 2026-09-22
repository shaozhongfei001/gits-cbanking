# 产品引用｜待裁定清单 V1.1（交产品 Owner 签）

| 项 | 值 |
|---|---|
| 用途 | 把产品关系引用中**仍需产品 Owner 分类**的部分转成可逐条裁定的清单 |
| 数据来源（**权威**） | `specs/knowledge-architecture/instances/product/projection-config.json`（`aliasMapDecisionRef=OWNER-DECISION-2026-09-21-D2`） |
| 裁定人 | **产品 Owner**（TL/实现负责人**不得**代裁） |
| 我方状态 | 隔离别名**不得进入任何 A-Box 投影**；分类完成前相关关系**不显示确定结论** |
| 关联 | `ONTO1-SCENARIO-PI-Owner决定登记-V1.0.md`；`ONTO1-SCENARIO-PI-CQ与验证夹具-V1.0.md` CQ3-S4 |

---

## 0. 修订记录（V1.0 → V1.1，2026-09-22，**自伤修正**）

V1.0 有两处错误，均由本轮回源发现：

| # | 我的错误 | 事实 | 修正 |
|---|---|---|---|
| 1 | 把 `UNRESOLVED.json` 的 **40 条**全部当作"待 Owner 裁定" | `projection-config.json` 已登记 **`aliasMap`（5 个别名，覆盖 28 条关系）**，状态 `RESOLVED_BY_OWNER_APPROVED_ALIAS`，决定引用 `OWNER-DECISION-2026-09-21-D2` ⇒ **28 条早已解决** | 待裁定范围 = **12 条 / 7 个符号**（即 `quarantinedAliases`） |
| 2 | 清单漏列 `FINANCIAL_ADVISORY`，且 `CORPORATE_E_BANK` 被重复计入两个类别 | 去重符号共 **12** 个，其中 5 个入 `aliasMap`、**7 个入 `quarantinedAliases`** | 本节以下按 7 个符号重列 |

> 教训（第二次同类）：**派生快照（`UNRESOLVED.json`）不是状态源**；状态源是 Owner 决定驱动的版本化配置（`projection-config.json`）。上一版我引用的 `unresolvedReferenceCount=40` 是**别名批准前的生成快照**。

**并列发现的缺陷（登记，非我修）**：`UNRESOLVED.json` 仍记为 `unresolvedReferenceCount=40`，未反映"28 条已由别名解决" ⇒ **生成器需重建**（状态漂移，MINOR），归 ONTO1 既有 WI 通道。

---

## 1. 已解决部分（**无需你签**，仅供参考）

| 符号 | 条数 | 映射到 | 状态 |
|---|---:|---|---|
| `SETTLEMENT_ACCOUNT` | 24 | `PROD-SET-001` 单位结算账户 | `RESOLVED_BY_OWNER_APPROVED_ALIAS` |
| `CORPORATE_E_BANK`→ 见 §2 | — | — | 已隔离（见下） |
| `CASH_POOL` | 1 | `PROD-CM-001` 现金池 | 同上 |
| `WORKING_CAPITAL_LOAN` | 1 | `PROD-FIN-001` 流动资金贷款 | 同上 |
| `CROSS_BORDER_RMB_SETTLEMENT` | 1 | `PROD-CB-001` 跨境人民币结算 | 同上 |
| `BANK_ACCEPTANCE_DRAFT` | 1 | `PROD-TF-001` 银行承兑汇票 | 同上 |
| **小计** | **28** | 5 个别名 | 由 `OWNER-DECISION-2026-09-21-D2` 批准 |

---

## 2. 待你签：**7 个符号 / 12 条关系**（`quarantinedAliases`）

> 隔离规则原文：**「隔离别名不得进入任何 A-Box 投影；隔离 ≠ 分类 ≠ 排除」** ⇒ 下列符号目前**既没被当作产品，也没被判作废**，需要你的分类结论。

| # | 符号 | 条数 | 引用它的产品卡 | 表面性质 | **TL 建议** | 备选 |
|---|---|---:|---|---|---|---|
| 1 | `CORPORATE_E_BANK` | 5 | PROD-CM-001、PROD-CM-002、PROD-FIN-001、PROD-SET-001、PROD-SET-002 | 电子渠道 | **作废引用**：电子银行属渠道域，不在本 13 产品目录内；渠道关系由系统层面承载 | 有效待补（补一张"企业网银"产品卡） |
| 2 | `CASH_MANAGEMENT` | 2 | PROD-FIN-001、PROD-SET-001 | **产品族名**（现金管理族） | **错误引用**：族名不是产品 ⇒ 需你指定具体产品，**TL 建议指向 `PROD-CM-001` 现金池** | 删除该引用 |
| 3 | `FX_FORWARD` | 1 | PROD-CB-001 跨境人民币结算 | 远期结售汇（真实产品） | **有效待补**：属跨境金融族，需新增产品卡（编号待分配，建议 `PROD-CB-003`） | 作废 |
| 4 | `DISCOUNT_SERVICE` | 1 | PROD-TF-001 银行承兑汇票 | 票据贴现（真实产品） | **有效待补**：属贸易金融族，需新增卡（建议 `PROD-TF-003`） | 作废 |
| 5 | `FINANCIAL_ADVISORY` | 1 | PROD-IB-001 并购贷款 | 财务顾问（服务/产品边界模糊） | **有效待补**（投行族常设财务顾问类产品） | 作废（若认定属服务不属产品） |
| 6 | `RECEIVABLE_LEDGER_TOOL` | 1 | PROD-FIN-002 应收账款质押融资 | 台账工具 | **作废引用**：工具不属可售产品 | 有效待补 |
| 7 | `ORDER_RECEIVABLE_CLOSED_ACCOUNT` | 1 | PROD-FIN-003 订单融资 | 账户安排 | **作废引用**：账户安排不属可售产品（与第 1 项同理） | 有效待补 |

**TL 建议汇总**：判「有效待补」3 项（#3/#4/#5）· 判「错误引用」1 项（#2）· 判「作废引用」3 项（#1/#6/#7）。

---

## 3. 签字模板（可直接回复，最短路径）

**方案 A（全按建议，最快）**：
```
7 项全部按 TL 建议：
1 CORPORATE_E_BANK=作废  2 CASH_MANAGEMENT=错误引用(→PROD-CM-001)  3 FX_FORWARD=有效待补(PROD-CB-003)
4 DISCOUNT_SERVICE=有效待补(PROD-TF-003)  5 FINANCIAL_ADVISORY=有效待补(编号待分配)
6 RECEIVABLE_LEDGER_TOOL=作废  7 ORDER_RECEIVABLE_CLOSED_ACCOUNT=作废
产品 Owner / 2026-09-22
```
**方案 B（逐条改）**：
```
1 CORPORATE_E_BANK = 有效待补 | 错误引用 | 作废
2 CASH_MANAGEMENT  = 错误引用 → 应指向: ________   （或"删除该引用"）
3 FX_FORWARD       = ______                       （有效待补编号：______）
4 DISCOUNT_SERVICE = ______
5 FINANCIAL_ADVISORY = ______
6 RECEIVABLE_LEDGER_TOOL = ______
7 ORDER_RECEIVABLE_CLOSED_ACCOUNT = ______
产品 Owner / 日期
```

---

## 4. 签完后我的动作（无需你再介入）

| # | 动作 | 说明 |
|---|---|---|
| 1 | 更新 `projection-config.json` 的 `aliasMap` / `quarantinedAliases`，登记新决定引用（如 `OWNER-DECISION-2026-09-22-D2`） | 走版本化配置，**不硬编码** |
| 2 | 重建 SIM 关系投影 `sim/product-relations.SIM.ttl` | 生成产物，勿手编 |
| 3 | 重建 `UNRESOLVED.json` | 未决数应从 40 → **0**（或仅留"有效待补"待补卡占位） |
| 4 | CQ3-S4 场景从 `NOT_EVALUATED` 转可评测 | 仍是 SIM，`formalRelationRelease` 保持 `NOT_AUTHORIZED` |
| 5 | 比较/前置/配套章节显示确定关系；助手可回答"需先开什么账户"类问题 | 附证据回链 |
| 6 | **新增产品卡需求**（若 #3/#4/#5 判"有效待补"）⇒ 转产品 Owner 出卡，不在本 Loop | 编号按 taxonomy 规则分配 |

## 5. 非声明

- 本清单是**待裁定材料**；7 项建议为 TL 初判（`EXPERT_JUDGMENT`），**须你签署**；
- 我不改产品卡、不改 taxonomy、不改本体权威制品、不解除隔离（`queued: QUARANTINED_UNRESOLVED`）；
- 未标 `PASS`；`formalRelationRelease` 保持 `NOT_AUTHORIZED`。

## 6. 复现命令

```bash
python3 - <<'PY'
import json
cfg = json.load(open('specs/knowledge-architecture/instances/product/projection-config.json'))
print('aliasMap(已批准):', cfg['aliasMap'])
print('aliasMapDecisionRef:', cfg['aliasMapDecisionRef'])
print('quarantined(待分类):', list(cfg['quarantinedAliases']))
print('quarantineRule:', cfg['quarantineRule'])
un = json.load(open('specs/knowledge-architecture/instances/product/UNRESOLVED.json'))
print('UNRESOLVED(需重建):', un['unresolvedReferenceCount'])
PY
```
