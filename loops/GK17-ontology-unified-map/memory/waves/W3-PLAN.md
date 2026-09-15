# W3｜PLAN（结构化知识 → 图，A-Box）

## Goal

把**已结构化的权威知识**投影成 RDF 个体，使地图/路由可以**引用**它们（W5.1 引用锚定、
W6/V1 链路、W6/V2 关系变更的前提）。

## 输入（实测，非假设）

| WP | 源 | 位置 | 状态 |
|---|---|---|---|
| **WP3.1** | 产品卡 front matter（`schema: product_card/v1`） | `/home/szf/dev/Leibniz-KERT/examples/product-recommendation-assets/03_core/*/version=*/product-cards/*.md`（与 gits-cbanking **同级的工作区**） | **13 张卡实测** |
| **WP3.2** | 事实对象（客户 / 集团 / 法人） | 仓内 `V011__v11_operational_ontology_entities.sql`（`legal_entity` / `group_relationship`）+ `V018__customer_seed_data.sql` | 待做 |

> **仓内无产品卡副本**（`PROD-*.md` 零命中、无 `03_core/`）⇒ 产品卡的**权威源在工作区外**。
> V021 头部自己也写明：「本表为产品知识版本元数据，**非产品卡权威源**；产品卡权威源在 KERT workspace」。

## 关键规则（来自 WP1.3 裁定）

- 关系**类型**权威 = 本体（`gits:requiresProduct` / `mutuallyExclusiveWith` / `complementsProduct`）；
- 关系**实例**权威 = 产品卡；
- 投影**单向**：产品卡 → 个体；**本体不得反向承载实例**；
- **悬空引用必须 fail-closed，不得静默丢弃**。

## ACCEPT 判据

1. **个体数可度量**；
2. **重复投影逐字节一致**（确定性）；
3. **非空转证明**：必须演示投影器**真的能产出关系**（否则"0 条关系"可能是空转而非真实结论）。

## 非声明

- WP3 **不**解决产品卡引用空间的缺陷（见 ITER 记录的 40 条悬空引用）—— 须产品 Owner 裁定；
- WP3 **不**把产品卡内容复制进仓（避免制造"第二份可独立修改的定义"，违反约束①）；
- WP3 **不**定义任何关系类型（那在本体）。
