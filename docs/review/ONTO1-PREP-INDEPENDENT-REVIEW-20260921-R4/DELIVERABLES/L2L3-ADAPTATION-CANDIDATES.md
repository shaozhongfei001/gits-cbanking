# L2 / L3 适配候选（准备项 3）

> 状态：`CANDIDATE_NOT_EFFECTIVE`｜命名空间：`PROVISIONAL_SIM_LEGACY_NAMESPACE`（非正式根域）
> 依据：执行计划 §84（KERT 侧 L1 副本 + L2 本体）、§74（合同拆条）；批次见 `construction-plan.json`

## L2 — KERT 元模型适配（批次 `B3_L2_KERT元模型`，110 项）

| 项 | 候选做法 | 前提 |
|---|---|---|
| 权威源 | KERT 侧 `90_control/ontology/` 改放「**L1 副本 + L2 本体**」 | **KERT 维护方写权限**（未确认） |
| 引用登记 | `ontology_reference.json` → `authorityEntity`（公共语义实体）+ 新钉值 | 同上 |
| 资产角色 | `ontology_assets.py` role 扩：`PUBLIC` / `KERT` / `GITS-EXTERNAL` | 同上 |
| 物化链路 | 重跑，**校验先于产出**（校验红则不产出） | 同上 |
| 验证 | 校验/物化复算 + 引用可回源（文件:行 + 哈希） | — |

> 本轮**只交分析/补丁方案/验证材料**，**未对 KERT 写入任何内容**（近 3 小时 KERT 侧变更文件 = 0）。

## L3 — 运行本体与适配器适配（批次 `B4_L3_运行本体` 106 项 + `B6_消费者切换` 86 项）

| 项 | 候选做法 | 边界 |
|---|---|---|
| `specs/semantic/gits-core.owl.ttl` | **收窄为 L3**；公共核心上移 L1（候选 `CTR-SEM-003`） | 收窄生效需合同拆条获批 |
| `modules/operational-ontology`（80 项） | 运行本体侧引用切到 L1/L3 的**provisional** 命名空间 | 不得发布新 IRI（D3 未签） |
| `adapters/semantic-jena`（6 项） | 解析端点按**离线 + 哈希**口径适配 | 同上 |
| 消费者（`apps/api` 95 项等） | `oldIRI→newIRI` **显式迁移清单**（禁用 `equivalentClass`） | 正式切换需 D3 根域 |
| 验证 | 本体/适配器加载测试 + 消费者编译单测 + 解析验证（SIM 通道） | SIM 可先行 |

## 消费者迁移验证材料（已生成）

`evidence/prep/consumer-migration-coverage.json` —— 对 **691 项真义务**所在 **499 个唯一文件**的本体引用面做了解析分类：

| 分类 | 计数 | 含义 |
|---|---|---|
| `RESOLVES_LOCAL_OR_PROVISIONAL_CURIE` | 332 | 落在 `gits:` / `prod:`（provisional）→ 迁移可直接验证 |
| `RESOLVES_LOCAL_OR_PROVISIONAL_IRI` | 32 | 绝对 IRI 落在 provisional 命名空间 |
| `KNOWN_EXTERNAL_CURIE` / `KNOWN_EXTERNAL_IRI` | 89 / 36 | 通用词汇（rdf/rdfs/owl/xsd/prov/skos…），不需迁移 |
| **`OTHER_PREFIX_CURIE`** | **64** | 未知前缀（含非 RDF 语境碰撞，如 `ngits:`、`root:`）⇒ **需逐条裁决** |
| **`UNMAPPED_APP_IRI`** | **34** | 未映射的应用 IRI（如 `http://gien.com/gits/ontology#`）⇒ **迁移期必须逐条裁决** |
| **`CODE_IMPORT_ONTOLOGY_PKG`** | **325** | Java 导入本体包（`com.gien.gits.ontology.*`）——**最大耦合面**，切换期需编译级验证 |

> 说明：`OTHER_PREFIX_CURIE` 含**非 RDF 语境的误匹配**（如 JSON/Java 中的 `xxx:`）。该表是**裁决清单**，不是缺陷清单；
> 本文件**不改变**任何制品，也不构成正式映射批准。
