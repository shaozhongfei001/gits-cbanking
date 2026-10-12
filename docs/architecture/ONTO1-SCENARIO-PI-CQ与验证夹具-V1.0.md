# 产品解读重构｜CQ 与验证夹具设计 V1.0（R4）

> **修订记录（V1.0 → V1.1，2026-09-21）**：初稿 CQ3-S4/S5 的目标数与状态引用了复审期快照，自检回源后按当日实测改写（40 条**已登记未分类**、13 产品个体在册、前缀碰撞已由 C-2 消除、判据脚本易名）。

| 项 | 值 |
|---|---|
| 文档性质 | **夹具设计件（DESIGN_ONLY / NOT_EVALUATED）**——复审前允许工作（设计 V2.0 §11 第⑤项） |
| 依据 | `ONTOLOGY-SPLIT-DESIGN-V2.0-REVIEW.md` §6.2/§6.3/§6.6｜`ONTO1-L1-建模规则R1-R9修订版-DRAFT.md` R4/R5/R7 |
| 夹具格式 | 沿用既有 `onto1_cq_fixture/v1`（`loops/ONTO1-ontology-split/evidence/cq-fixtures/CQ3.json`） |
| **纪律** | **空转（实际目标数=0）不得给绿** ⇒ 本件全部场景状态为 `DESIGN_ONLY`（类未建）或 `NOT_EVALUATED`（无生产实例）；**无一处 PASS** |
| Shape 策略 | **废止「每类一份 NodeShape」**（R4）；Shape 由**验证场景与封闭边界**决定，由源模型生成、**禁手改** |

---

## 1. 场景清单与覆盖矩阵（R4 要求物）

**CQ 编号纪律**：V2.0 §6.6 的 **CQ1–CQ6 为已冻结集合**，本场景**不新增 CQ 编号**，而以 **`CQ3-S*`** 子场景形式挂在 CQ3（产品知识卡/版本/`describesProduct`）之下，责任 Owner = Knowledge Owner。

| 场景 | 意图 | 目标类（含层） | 关联 Shape | 期望目标数 | **实际目标数（实测口径）** | 正例 | 负例 | 变异用例 | Owner | 状态 | 阻塞 |
|---|---|---|---|---:|---:|---|---|---|---|---|---|
| **CQ3-S1** | 解读归属：解读是对哪个产品的解读 | `ProductInterpretation`(L2) `--interprets-->` `ProductOffering`(L1) | `InterpretationPublicationShape` | = 已发布解读个体数（**类未建 ⇒ 无可计**） | **0** | 解读 `PI-CM-003-1` → `ProductOffering PROD-CM-003`（存在且在用） | `interprets` 指向不存在的产品 ⇒ 具名拒绝 `DANGLING_PRODUCT_REF` | 删除 `interprets` 三元组 ⇒ **必须 FAIL** | Knowledge Owner | `DESIGN_ONLY` | 类未建（Wave 2）+ D2/D3 |
| **CQ3-S2** | 规则包归属：规则包服务哪个产品 | `RuleBundle`(L2) `--rulesFor-->` `ProductOffering`(L1) | `RuleBundleIngestionShape` | = 已登记规则包数 | **0** | `RB-CM-003` → `PROD-CM-003` | `rulesFor` 缺失 ⇒ `MISSING_RULE_TARGET` | 把 `rulesFor` 改指不存在产品 ⇒ **必须 FAIL** | Knowledge Owner | `DESIGN_ONLY` | 类未建 + D2/D3 |
| **CQ3-S3** | 版本有效性（**复用 CQ3 正/负例**） | `ProductKnowledgeCard` `--describesProduct-->` `ProductOffering` + `ProductKnowledgeVersion` 有效期 | `CardVersioningShape` | = 生效卡数 | **0** | 卡 `PROD-CB-001` → `PROD-CB-001`，有效版本 v3（查询日 `2026-09-20` 在有效期内） | 卡指向**已退役版本** ⇒ 具名提示 | `describesProduct` 改指不存在产品 ⇒ **必须 FAIL** | Knowledge Owner | `NOT_EVALUATED` | **D2 硬阻塞**（40 处悬空引用） |
| **CQ3-S4** | 悬空引用处置闭环 | `requiresProduct`/`complementsProduct`/`mutuallyExclusiveWith` 实例 | `ProductRelationShape` | = **40 条逐条分类**（有效待补/错误引用/作废） | **已登记 40 / 40，已分类 0 / 40**（`UNRESOLVED.json`：`unresolvedReferenceCount=40`、`relationInstances=0`） | 每条给出产品 Owner 分类结论 + 处置动作 | 任一条**未分类**即 FAIL；**不得永久豁免** | 抽 1 条改回未分类 ⇒ **必须 FAIL** | 产品 Owner（分类）/ Knowledge Owner（执行） | `NOT_EVALUATED` | **D2**（`formalRelationRelease=NOT_AUTHORIZED`） |
| **CQ3-S5** | 实例命名空间一致（R1） | `products.ttl` 产品个体 | `ProductInstanceShape` | = 13 产品个体 | **13 个体已在册**（`productIndividuals=13`）；Shape 命中数**未测**（未跑门禁，ONTO1 板面预算受限） | 13 个体全部被 Shape 命中；术语前缀 ↔ 实例前缀**分置且各自 1:1** | 术语前缀指向 `https://gits.bank.example/ontology/core#`（回改）⇒ `ONTOLOGY_PREFIX_COLLISION` | 把 `prod:` 与 `gits:` 合并为同前缀 ⇒ **必须 FAIL** | Integration Contract Owner（待任命） | `NOT_EVALUATED` | **D3**（实例命名空间仍为占位根域，正式 IRI 不得发布） |

**覆盖矩阵（目标类 × 场景）**

| 目标类 | 层 | CQ3-S1 | CQ3-S2 | CQ3-S3 | CQ3-S4 | CQ3-S5 |
|---|---|:--:|:--:|:--:|:--:|:--:|
| `ProductInterpretation` | L2 | ● | | | | |
| `RuleBundle` | L2 | | ● | | | |
| `ProductKnowledgeCard` / `ProductKnowledgeVersion` | L2 | | | ● | | |
| `ProductOffering` | L1 | ○（被引） | ○（被引） | ○（被引） | | ●（实例层） |
| 产品关系 3 属性 | L2 | | | | ● | |
| `products.ttl` 产品个体 | 实例 | | | | | ● |

● = 主验证目标　○ = 被引用对象（不独立断言）

---

## 2. Shape 设计（由场景决定，非「每类一份」）

| Shape | 封闭边界（只校验什么） | 关键约束 | 生成方式 |
|---|---|---|---|
| `InterpretationPublicationShape` | **发布场景**：仅已发布解读个体 | `interprets` **恰好 1**；目标须为 L1 `ProductOffering` 个体；必填元数据六项齐备（R7）；不得引用 `PENDING:` 占位（R1） | 由源模型生成，禁手改 |
| `RuleBundleIngestionShape` | **摄取场景**：规则包登记 | `rulesFor` ≥1；来源/版本/责任人齐备；`sourcedFrom` 指向 `KnowledgeSource` | 同上 |
| `CardVersioningShape` | **时态场景**：卡↔版本有效期 | `describesProduct` ≥1；版本 `validFrom/validTo` 区间合法（R5 时态约束）；过期 ⇒ 具名提示而非静默 | 同上 |
| `ProductRelationShape` | **实例场景**：产品卡投影个体 | 关系目标必须存在于本体（否则 `DANGLING_PRODUCT_REF`）；**实例只读可重建**（WP1.3 §3.3） | 同上 |
| `ProductInstanceShape` | **命名空间场景**（R1） | 前缀→命名空间 1:1；IRI 唯一；无动态 IRI | 同上 |

**一致性门禁锚点**：源模型类清单 ↔ Shape 目标类清单**同步**（**不是**「类数 == Shape 数」，R4 修订要点）。

---

## 3. 夹具字段设计（机读，沿用 `onto1_cq_fixture/v1`）

```json
{
  "schema": "onto1_cq_fixture/v1",
  "id": "CQ3-S1",
  "parent_cq": "CQ3",
  "question": "某个产品解读对应的是哪个产品身份，该解读是否可用于当前时点？",
  "validates": "ProductInterpretation -interprets-> ProductOffering（L1 引用）",
  "target_class": "ProductInterpretation",
  "layer": "L2",
  "shape": "InterpretationPublicationShape",
  "query": "按解读 ID 查 interprets 目标 + interprets 唯一性",
  "expected_target_count": "已发布解读个体数（类未建 ⇒ 无可计）",
  "actual_target_count": 0,
  "positive": "解读 PI-CM-003-1 -> PROD-CM-003（产品存在且状态在用）",
  "negative": "interprets 指向不存在产品 ⇒ 具名拒绝 DANGLING_PRODUCT_REF",
  "mutation": "删除 interprets 三元组 ⇒ 必须 FAIL",
  "fixture_hits": { "positive": 0, "negative": 0, "mutation": 0 },
  "owner": "Knowledge Owner（KERT 维护方）",
  "status": "DESIGN_ONLY",
  "gate": "Wave 2 后（类建成）+ Wave 4（门禁）",
  "external_blocker": ["D2", "D3"],
  "notes": "空转不得给绿；PENDING: 占位不得进发布制品"
}
```

**夹具落地纪律**：本件**只给设计**，不写盘假数据；实际 `CQ3-S*.json` 由 Wave 2 建类后按上表填充，且 `actual_target_count=0` 时必须保持 `NOT_EVALUATED`/`DESIGN_ONLY`。

---

## 4. 门禁判据与失败具名码（本场景用到的全集）

| 判据 | 失败具名码 | 触发点 |
|---|---|---|
| 目标数=0 却给绿 | `ONTOLOGY_VACUOUS_SHACL` | 全部场景（**当前最大风险**：现有 gate 静默绿） |
| 场景缺覆盖矩阵 | `ONTOLOGY_SHAPE_SCENARIO_MISSING` | Wave 4 |
| Shape 与源模型不一致 | `ONTOLOGY_SHAPE_DRIFT` | Wave 2 |
| 手改生成物 | `ONTOLOGY_GENERATED_FILE_TAMPERED` | 全阶段（**红线段**） |
| 前缀→命名空间非 1:1 | `ONTOLOGY_PREFIX_COLLISION` | CQ3-S5 |
| `PENDING:` 占位进发布制品 | `ONTOLOGY_PLACEHOLDER_IN_RELEASE` | 发布门禁 |
| 悬空产品引用 | `DANGLING_PRODUCT_REF` | CQ3-S3/S4 |
| 缺来源标识（6 必填） | `MISSING_SOURCE_IDENTIFIER` | L1 实例（`SIM-*` 数据产品） |
| 元数据六项缺失 | `ONTOLOGY_METADATA_INCOMPLETE` | 全部类/属性 |
| 未钉 `versionIRI` | `ONTOLOGY_UNPINNED_IMPORT` | C-03/C-04（跨层引用） |

---

## 5. 本件的状态声明与下一步

| 项 | 状态 |
|---|---|
| 场景清单与覆盖矩阵 | ✅ 已给（本件 §1/§2） |
| 夹具设计 | ✅ 已给（§3 字段级） |
| 夹具执行记录（期望 vs 实际 + 命中数） | ❌ **未执行**（类未建、无实例）⇒ 全部 `DESIGN_ONLY` / `NOT_EVALUATED` |
| 变异复验记录 | ❌ 未执行（Wave 2/4 收工必须补：mutate→FAIL / restore→PASS） |
| 可升级为 PASS 的前置 | ① `DESIGN_APPROVED`；② Wave 2 建类 + 三份 SHACL 生成；③ D2 完成 40 条分类；④ D3 签署（仅 CQ3-S5） |

> **汇报口径**：本场景当前**没有任何一项可报 `PASS`**；可报的只有「设计件已产出 + 判据已具名 + 空转风险已定位（现有 gate `vacuous=true` 静默绿）」。

---

## 6. 复现命令

```bash
# 现状：既有 CQ 全部 NOT_EVALUATED（若被标 PASS 即违规）
for f in loops/ONTO1-ontology-split/evidence/cq-fixtures/CQ*.json; do
  python3 -c "import json;d=json.load(open('$f'));print(d['id'],d['status'])"
done

# 空转判据的真实位置（本场景最大风险点）
grep -rn "vacuous" scripts/onto1_namespace_collision_check.py | head -5   # :308-309

# 命名空间现状（CQ3-S5：术语/实例分前缀；实例仍占位根域）
sed -n '1,8p' specs/knowledge-architecture/instances/product/products.ttl

# 悬空引用规模与权威归属（CQ3-S4）
python3 -c "import json;d=json.load(open('specs/knowledge-architecture/instances/product/UNRESOLVED.json'));print(d['unresolvedReferenceCount'], d['relationInstances'], d['relationTypeAuthority'], d['relationInstanceAuthority'])"
```
