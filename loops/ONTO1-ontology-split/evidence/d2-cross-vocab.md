## A. 精确同形命中（脚本自动扫描非产品词表）

| 取值 | 命中的非产品词表 | 回源位置 |
|---|---|---|
| `SETTLEMENT_ACCOUNT` | `gits.seed_key_feature` | `adapters/persistence-relational/src/main/resources/db/migration/h2/V021__corporate_product_knowledge_seed.sql:44` |
| `CORPORATE_E_BANK` | （无） | — |
| `CASH_MANAGEMENT` | `product_family` | `examples/product-recommendation-assets/03_core/cash-management/version=2026.09.01.1/product-cards/PROD-CM-001.md:5`、`examples/product-recommendation-assets/03_core/cash-management/version=2026.09.01.1/product-cards/PROD-CM-002.md:5`、`examples/product-recommendation-assets/03_core/cash-management/version=2026.09.01.1/product-cards/PROD-CM-003.md:5` |
| `CASH_MANAGEMENT` | `gits.taxonomy_id` | `specs/product-knowledge/product-taxonomy.yaml:68` |
| `CASH_MANAGEMENT` | `gits.seed_product_category` | `adapters/persistence-relational/src/main/resources/db/migration/h2/V021__corporate_product_knowledge_seed.sql:61`、`adapters/persistence-relational/src/main/resources/db/migration/h2/V021__corporate_product_knowledge_seed.sql:70` |
| `BANK_ACCEPTANCE_DRAFT` | （无） | — |
| `CASH_POOL` | （无） | — |
| `CROSS_BORDER_RMB_SETTLEMENT` | （无） | — |
| `DISCOUNT_SERVICE` | （无） | — |
| `FINANCIAL_ADVISORY` | （无） | — |
| `FX_FORWARD` | （无） | — |
| `ORDER_RECEIVABLE_CLOSED_ACCOUNT` | （无） | — |
| `RECEIVABLE_LEDGER_TOOL` | （无） | — |
| `WORKING_CAPITAL_LOAN` | （无） | — |

## B. 邻近 / 跨词表语义命中（人工收录 + 机器校验行内容）

> 「同物不同形」的情况 A 段扫不到（族名 / 品类名 / 账户关系位 / GITS 种子 / 正文中文名），故单列，避免交叉验证留下最难判的那几行。

| 取值 | 词表来源 | 回源位置 | 说明 |
|---|---|---|---|
| `SETTLEMENT_ACCOUNT` | `card.admission_criteria.requiredAccountRelationship` | KERT `examples/product-recommendation-assets/03_core/cash-management/version=2026.09.01.1/product-cards/PROD-CM-001.md:26` | 同 token 出现在账户关系位（12 张卡），**不计入 40** |
| `SETTLEMENT_ACCOUNT` | `card.prose.§6` | KERT `examples/product-recommendation-assets/03_core/cash-management/version=2026.09.01.1/product-cards/PROD-CM-001.md:64` | 正文主体中文名，与 PROD-SET-001 卡名「单位结算账户」不完全一致 |
| `SETTLEMENT_ACCOUNT` | `gits.seed_key_feature` | GITS `adapters/persistence-relational/src/main/resources/db/migration/h2/V021__corporate_product_knowledge_seed.sql:44` | GITS PI-0 种子里是「关键特性」取值 |
| `CORPORATE_E_BANK` | `card.prose.§6` | KERT `examples/product-recommendation-assets/03_core/cash-management/version=2026.09.01.1/product-cards/PROD-CM-001.md:65` | 5 张卡正文一一对应 |
| `CORPORATE_E_BANK` | `gits.taxonomy_category` | GITS `specs/product-knowledge/product-taxonomy.yaml:197` | GITS 分类基线「电子渠道」品类，has_products=false |
| `CORPORATE_E_BANK` | `gits.seed_product_name` | GITS `adapters/persistence-relational/src/main/resources/db/migration/h2/V021__corporate_product_knowledge_seed.sql:51` | GITS PI-0 种子把同类事物登记为**产品** ⇒ 跨仓身份冲突 |
| `CASH_MANAGEMENT` | `card.product_family_name` | KERT `examples/product-recommendation-assets/03_core/cash-management/version=2026.09.01.1/product-cards/PROD-CM-001.md:6` | 族中文名 = 两处正文所写配套名 |
| `CASH_MANAGEMENT` | `gits.taxonomy_name_zh` | GITS `specs/product-knowledge/product-taxonomy.yaml:69` | GITS 分类基线族中文名 |
| `CASH_MANAGEMENT` | `gits.seed_product_category` | GITS `adapters/persistence-relational/src/main/resources/db/migration/h2/V021__corporate_product_knowledge_seed.sql:61` | GITS PI-0 种子的 category 列即产品族编码 |
| `BANK_ACCEPTANCE_DRAFT` | `card.prose.§6` | KERT `examples/product-recommendation-assets/03_core/trade-finance/version=2026.09.01.1/product-cards/PROD-TF-002.md:65` | 正文配套名 |
| `BANK_ACCEPTANCE_DRAFT` | `gits.taxonomy_category` | GITS `specs/product-knowledge/product-taxonomy.yaml:203` | 近名品类「承兑工具」 |
| `CASH_POOL` | `card.prose.§6` | KERT `examples/product-recommendation-assets/03_core/cash-management/version=2026.09.01.1/product-cards/PROD-CM-002.md:65` | 正文配套名 |
| `CASH_POOL` | `gits.taxonomy_category` | GITS `specs/product-knowledge/product-taxonomy.yaml:167` | 近名品类「资金池」（一字之差） |
| `CROSS_BORDER_RMB_SETTLEMENT` | `card.prose.§6` | KERT `examples/product-recommendation-assets/03_core/cross-border/version=2026.09.01.1/product-cards/PROD-CB-002.md:65` | 正文配套名 |
| `CROSS_BORDER_RMB_SETTLEMENT` | `gits.taxonomy_category` | GITS `specs/product-knowledge/product-taxonomy.yaml:221` | 近名品类「跨境结算」 |
| `DISCOUNT_SERVICE` | `card.prose.§6` | KERT `examples/product-recommendation-assets/03_core/trade-finance/version=2026.09.01.1/product-cards/PROD-TF-001.md:66` | 正文配套名 |
| `DISCOUNT_SERVICE` | `gits.taxonomy_category` | GITS `specs/product-knowledge/product-taxonomy.yaml:215` | GITS 品类「票据贴现」，has_products=false |
| `FINANCIAL_ADVISORY` | `card.prose.§6` | KERT `examples/product-recommendation-assets/03_core/investment-banking/version=2026.09.01.1/product-cards/PROD-IB-001.md:66` | 正文配套名 |
| `FINANCIAL_ADVISORY` | `gits.taxonomy_category` | GITS `specs/product-knowledge/product-taxonomy.yaml:265` | GITS 品类「财务顾问」，has_products=false |
| `FX_FORWARD` | `card.prose.§6` | KERT `examples/product-recommendation-assets/03_core/cross-border/version=2026.09.01.1/product-cards/PROD-CB-001.md:66` | 正文配套名 |
| `FX_FORWARD` | `gits.taxonomy_category` | GITS `specs/product-knowledge/product-taxonomy.yaml:229` | GITS 品类「外汇服务」，has_products=false |
| `FX_FORWARD` | `gits.seed_product_name` | GITS `adapters/persistence-relational/src/main/resources/db/migration/h2/V021__corporate_product_knowledge_seed.sql:108` | GITS PI-0 种子有产品行，但不在 PROD-* 空间 |
| `ORDER_RECEIVABLE_CLOSED_ACCOUNT` | `card.prose.§6` | KERT `examples/product-recommendation-assets/03_core/financing/version=2026.08.31.1/product-cards/PROD-FIN-003.md:75` | 正文自述为「账户」 |
| `RECEIVABLE_LEDGER_TOOL` | `card.prose.§6` | KERT `examples/product-recommendation-assets/03_core/financing/version=2026.08.31.1/product-cards/PROD-FIN-002.md:75` | 正文自述为「工具」 |
| `RECEIVABLE_LEDGER_TOOL` | `gits.seed_required_material` | GITS `adapters/persistence-relational/src/main/resources/db/migration/h2/V021__corporate_product_knowledge_seed.sql:27` | **近形不同 token**（RECEIVABLE_LEDGER 是材料项）⇒ 不构成归一化依据 |
| `WORKING_CAPITAL_LOAN` | `card.prose.§6` | KERT `examples/product-recommendation-assets/03_core/cash-management/version=2026.09.01.1/product-cards/PROD-CM-003.md:65` | 正文配套名 |
| `WORKING_CAPITAL_LOAN` | `gits.taxonomy_category` | GITS `specs/product-knowledge/product-taxonomy.yaml:239` | 近名品类「流动资金」 |
