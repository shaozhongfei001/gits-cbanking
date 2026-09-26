# D2 请求函：产品关系悬空引用分类裁定

| 项 | 值 |
|---|---|
| 收件 | **产品 Owner**（产品目录 / 产品工厂归口） |
| 抄送 | 公共语义 Owner（待任命）、Knowledge/KERT Owner |
| 发出 | 全局 Tech Lead，2026-09-20 |
| 目标日期 | **激活门禁（`OWNER_ACTIVATED`）之前**；建议 2026-10-09 前（与 D1 同批） |
| 依赖登记 | `docs/review/ARCH-ONTO-2026-001-rereview-package/11-外部依赖登记表.md` §D2 |
| 设计依据 | `docs/architecture/ONTOLOGY-SPLIT-DESIGN-V2.0-REVIEW.md` §5（Product 模式闭合） |
| 相关夹具 | `loops/ONTO1-ontology-split/evidence/cq-fixtures/CQ3-*.json` |
| 当前状态 | **请求函已发出，待 Owner 签署**（未签署前相关场景一律 `NOT_EVALUATED`） |

---

## 1. 请你裁决什么（一句话）

**40 处产品关系引用用了"非产品 ID"的取值（如 `SETTLEMENT_ACCOUNT`、`CASH_POOL`），请逐条裁定其为「有效待补 / 错误引用 / 作废」三类之一。**

裁定完成后我才可以：
- 给 `requiresProduct` / `complementsProduct` 补经批准的实例或受控夹具；
- 让 CQ3 从 `NOT_EVALUATED` 进入可执行验证；
- 关闭"Product 模式闭合"（复审十项关闭条件之条件 4）。

## 2. 为什么现在要（也为什么不能拖成豁免）

- 委员会裁定：**不得以永久豁免关闭**；`WAIVED_FOR_DEVELOPMENT` 只允许继续开发，**不满足任何激活门禁**（设计 §5、复审包 06 号 §3）。
- 因此 D2 是**激活门禁硬阻塞**，不能靠豁免绕开。

## 3. 事实清单：40 处引用的精确构成（本轮实测，可复现）

复现命令与机读清单：

```bash
python3 scripts/onto1_product_refs_probe.py --gate
# 机读清单：loops/ONTO1-ontology-split/evidence/product-refs-inventory.csv
# 汇总：    loops/ONTO1-ontology-split/evidence/product-refs-summary.json
```

| 字段 | 语义对应 | 出现次数 |
|---|---|---|
| `prerequisite_product_ids` | `requiresProduct` | **12** |
| `complementary_products` | `complementsProduct` | **28** |
| `mutex_product_ids` | `mutuallyExclusiveWith` | **0（零实例）** |
| **合计** | | **40** |

- 覆盖 13 张产品卡（`examples/**/product-cards/PROD-*.md`，13 个 `PROD-*` 身份）。
- **全部 40 处均为悬空**：取值不落在既有产品身份空间（`PROD-*`）内；其中 38 处为完全未知 token，2 处与其它词表取值重合。
- `mutex_product_ids` 在 13 张卡片中均为空 ⇒ `mutuallyExclusiveWith` 场景**零实例**，按五态模型应记 `NOT_EVALUATED`，**不得**用"0 目标 0 违规"包装为通过。

## 4. 逐取值裁决表（请逐行勾选一类）

| # | 取值 | 次数 | 出现字段 | 候选关系（证据，不是结论） | 请勾选 |
|---|---|---|---|---|---|
| 1 | `SETTLEMENT_ACCOUNT` | 24 | prerequisite, complementary | 同一取值也被 `admission_criteria.requiredAccountRelationship` 使用（12 张卡）⇒ **疑为"账户关系"而非产品** | ☐ 有效待补（→ 应填哪个 `PROD-*`？____） ☐ 错误引用 ☐ 作废 |
| 2 | `CORPORATE_E_BANK` | 5 | complementary | 既有 13 张卡中无同名产品 | ☐ 有效待补（____） ☐ 错误引用 ☐ 作废 |
| 3 | `CASH_MANAGEMENT` | 2 | complementary | 等于**产品族名** `CASH_MANAGEMENT`（对应 PROD-CM-001/002/003）⇒ 疑为"族名写到产品位" | ☐ 有效待补（____） ☐ 错误引用 ☐ 作废 |
| 4 | `CASH_POOL` | 1 | complementary | 疑似「现金池」`PROD-CM-001` 的语义名 | ☐ 有效待补（____） ☐ 错误引用 ☐ 作废 |
| 5 | `CROSS_BORDER_RMB_SETTLEMENT` | 1 | complementary | 疑似「跨境人民币结算」`PROD-CB-001` 的语义名 | ☐ 有效待补（____） ☐ 错误引用 ☐ 作废 |
| 6 | `WORKING_CAPITAL_LOAN` | 1 | complementary | 疑似「流动资金贷款」`PROD-FIN-001`，**待确认** | ☐ 有效待补（____） ☐ 错误引用 ☐ 作废 |
| 7 | `BANK_ACCEPTANCE_DRAFT` | 1 | complementary | 疑似银行承兑汇票类，**无对应卡** | ☐ 有效待补（____） ☐ 错误引用 ☐ 作废 |
| 8 | `FX_FORWARD` | 1 | complementary | 无对应卡 | ☐ 有效待补（____） ☐ 错误引用 ☐ 作废 |
| 9 | `RECEIVABLE_LEDGER_TOOL` | 1 | complementary | 无对应卡 | ☐ 有效待补（____） ☐ 错误引用 ☐ 作废 |
| 10 | `ORDER_RECEIVABLE_CLOSED_ACCOUNT` | 1 | complementary | 无对应卡；含 `ACCOUNT` 字样，疑与 #1 同类问题 | ☐ 有效待补（____） ☐ 错误引用 ☐ 作废 |
| 11 | `DISCOUNT_SERVICE` | 1 | complementary | 无对应卡 | ☐ 有效待补（____） ☐ 错误引用 ☐ 作废 |
| 12 | `FINANCIAL_ADVISORY` | 1 | complementary | 无对应卡 | ☐ 有效待补（____） ☐ 错误引用 ☐ 作废 |

> 逐卡片明细（哪张卡的哪个字段）见 `product-refs-inventory.csv`（40 行）。

## 5. 顺带需要你确认的两项（同一决策包）

1. **`ProductOffering` 身份权威（SIM 阶段）**：请确认/批准《SIM 临时模拟权威声明》草案
   （`docs/architecture/ONTO1-SIM临时模拟权威声明草案.md`），使产品身份在试点期有**显式临时权威**（含退出条件），而不是默认为 KERT 产品卡。
2. **关系类型权威**：设计 §5 记载"关系类型权威在 L2，实例权威在产品卡 front matter，经 WP1.3 裁定"。请确认该口径是否仍成立，或改写。

## 6. 未决期间的禁止动作（我已自我约束，供你监督）

- 不把三场景（`requiresProduct`/`complementsProduct`/`mutuallyExclusiveWith`）标 `PASS`；
- 不以 `WAIVED_FOR_DEVELOPMENT` 充当激活依据；
- 不把 SIM 产品登记表静默升级为企业产品权威；
- 不关闭 R-6 风险登记；
- 不修改产品卡与 `products.ttl`（Wave -1 只读）。

## 7. 签署区

| 项 | 内容 |
|---|---|
| 裁定结论 | 见 §4 逐行勾选 + 序号 1~12 的最终分类 |
| 「有效待补」项的补齐方式 | ☐ 由产品 Owner 提供 `PROD-*` 映射表 ☐ 由本 Loop 按裁定生成候选映射后再确认 |
| 是否批准 SIM 临时模拟权威声明 | ☐ 批准 ☐ 有条件批准（条件：______） ☐ 不批准 |
| 签署人 / 日期 | |
| 附件哈希 | `product-refs-inventory.csv` sha256 `6bbc17b718603285…`（全值见 `product-refs-summary.json`） |
