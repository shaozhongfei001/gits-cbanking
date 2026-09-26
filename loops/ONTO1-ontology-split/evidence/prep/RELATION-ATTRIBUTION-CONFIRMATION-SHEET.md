# 12 条隔离关系｜**归属确认单**（供 Owner / 产品·数据 Owner 逐条勾选）

> 编制：全局 TL，2026-09-21｜依据 Owner 指示「按建议办」
> 机读事实源：`evidence/product-alias-resolution.json`（`quarantined_unresolved`）
> 现状口径：**28 条已解析 / 12 条隔离**（`total 40`，`distinct_aliases 12`）
> **本单不含推定结论**；我不代填、不代勾、不把"建议"写成裁定。

---

## 1. 这 12 条是什么（逐条，全部为 `complementary_products` 字段）

| # | 卡片 | 字段 | 值（别名） | 分栏 |
|---|---|---|---|---|
| 1 | `PROD-CM-001.md` | complementary_products | `CORPORATE_E_BANK` | **A** |
| 2 | `PROD-CM-002.md` | complementary_products | `CORPORATE_E_BANK` | **A** |
| 3 | `PROD-FIN-001.md` | complementary_products | `CORPORATE_E_BANK` | **A** |
| 4 | `PROD-SET-001.md` | complementary_products | `CORPORATE_E_BANK` | **A** |
| 5 | `PROD-SET-002.md` | complementary_products | `CORPORATE_E_BANK` | **A** |
| 6 | `PROD-FIN-001.md` | complementary_products | `CASH_MANAGEMENT` | **A** |
| 7 | `PROD-SET-001.md` | complementary_products | `CASH_MANAGEMENT` | **A** |
| 8 | `PROD-CB-001.md` | complementary_products | `FX_FORWARD` | **A** |
| 9 | `PROD-FIN-002.md` | complementary_products | `RECEIVABLE_LEDGER_TOOL` | **B** |
| 10 | `PROD-FIN-003.md` | complementary_products | `ORDER_RECEIVABLE_CLOSED_ACCOUNT` | **B** |
| 11 | `PROD-IB-001.md` | complementary_products | `FINANCIAL_ADVISORY` | **B** |
| 12 | `PROD-TF-001.md` | complementary_products | `DISCOUNT_SERVICE` | **B** |

**别名汇总（7 个）**：`CORPORATE_E_BANK` 5 · `CASH_MANAGEMENT` 2 · `FX_FORWARD` 1 · `RECEIVABLE_LEDGER_TOOL` 1 ·
`ORDER_RECEIVABLE_CLOSED_ACCOUNT` 1 · `FINANCIAL_ADVISORY` 1 · `DISCOUNT_SERVICE` 1 = **12**

## 2. 建议的分栏（**建议，非裁定**）

- **A 栏（8 条 / 3 个别名）⇒ 建议转业务确认**：`CORPORATE_E_BANK`(5) · `CASH_MANAGEMENT`(2) · `FX_FORWARD`(1)
  - **选取依据**：关系数最多 + 名称最接近"可能确有产品对应"（`FX_FORWARD` 是典型产品名）。
  - 请对每个别名回：**目标产品 ID**（若确有产品卡）**或**"确认继续隔离"。
- **B 栏（4 条 / 4 个别名）⇒ 建议直接书面确认继续隔离**：其余四个各 1 条
  - **依据**：单条、影响面小，逐条追查的沟通成本高于收益；隔离是**安全默认**（不会把错写进制品）。
- **更省的替代方案（同样合法）**：**7 个别名一次性全部"确认继续隔离"** —— 代价是 SIM 投影保持 28 条不变、CQ3 口径不变；
  **收益是零沟通成本、零推定风险**。若你选这条，请在 §3 直接勾"全部继续隔离"。

## 3. 请勾选（Owner / 产品·数据 Owner）

```
[ ] 方案甲：A 栏 3 个别名由业务确认（目标产品 ID 见附表），B 栏 4 个别名确认继续隔离
[ ] 方案乙：7 个别名**全部继续隔离**（最省，零推定）
[ ] 其他：____________________________（请写明）
```

A 栏若走方案甲，请逐别名填（**留空＝未裁定，继续隔离，不得推定**）：

| 别名 | 目标产品 ID（填） | 或勾"继续隔离" |
|---|---|---|
| `CORPORATE_E_BANK` | ________________ | [ ] |
| `CASH_MANAGEMENT` | ________________ | [ ] |
| `FX_FORWARD` | ________________ | [ ] |

签字：________________（角色：______________）　日期：________

## 4. 硬约束（原文引用，**我不推定**）

> - `CASH_MANAGEMENT` **不得**被映射为"现金池"或任何产品实例（可能是产品类别或能力概念）；
> - **不得**虚构不存在的产品卡；
> - **不得**把 12 条强行映射以**凑齐**；
> - **不得**把本兼容修复解释为 V2 目标本体**全部落地**。
>
> （出处：`product-alias-resolution.json` → `explicit_denials`）

**CQ3 口径（不得扩张）**：只能报告「**28 条已解析、12 条隔离**」，**不得**宣称全量通过。

## 5. 两种结果的后果（差异要说清）

| 你的勾选 | 我会做什么（机器可复算） | 对板面/门禁的影响 |
|---|---|---|
| 某别名给出**目标产品 ID** | 加入 `projection-config.json.aliasMap`（版本化）→ 重新生成 SIM 投影 → 该条由隔离转解析；**同时**必须通过 G8/G9/G10/G11 守卫 | **不提升任何门禁值**；`wi_d2_relation_resolution` 判据含"目标与别名集合须与 Owner 批准项完全一致"⇒ 我改配置后**须重记**该门禁（属正常 revision 变更） |
| 勾**继续隔离** | 不做任何改动，保持现状；隔离项持续受守卫（出现在任何 SIM 输出即 FAIL） | 无变化 |

**边界**：本单不推定、不代填、不代勾；未勾选的别名**一律维持隔离**（安全默认）。
