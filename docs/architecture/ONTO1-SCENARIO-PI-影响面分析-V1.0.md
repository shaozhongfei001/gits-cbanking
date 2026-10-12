# 产品解读重构｜本体变更影响面分析 V1.0（R8）

| 项 | 值 |
|---|---|
| 文档性质 | **分析件（DESIGN_ONLY）**——复审前允许工作（设计 V2.0 §11 第②③⑤项）；**不是**合同变更、**不是**实施授权 |
| 场景 | GITS Bank 产品解读重构（实现负责人 = Tech Lead） |
| 架构依据 | `ONTOLOGY-SPLIT-DESIGN-V2.0-REVIEW.md` §3/§5/§6.4、`ONTO-SPLIT-本体四层落地执行计划-V2.0.md` §2、`ONTO1-L1-建模规则R1-R9修订版-DRAFT.md` R8 |
| 当前门禁 | `RETURN_TO_HLD` 有效；`DESIGN_APPROVED` 未达成 ⇒ **本件不含任何权威制品改动** |
| 计数口径 | `OWL 类 39 / SKOS 1 / Schema 对象 5`（分制品计数，**不**笼统称「45 个本体类」） |
| 非声明 | 未运行门禁、未改 `specs/`、未改 `generated/`、未发布 IRI、未把 SIM 说成生产权威、未标 `PASS` |

> **修订记录（V1.0 → V1.1，2026-09-21）**：初稿 P-7/P-8 两行**引用了复审期快照**（V1.2 §2.0）当作现状，自检时段回源发现已过期，现按 2026-09-21 13:05 实测重写，并补 P-11~P-13 三个新钉值方。
> 教训（自伤，未提交即修正）：**复审期文书的"现状"列不是现状**；影响面分析必须逐条回源当日实测。上节"复现命令"即为该纪律的可执行形式。

---

## 0. 本场景的变更定位（先归属，后实现 —— P2）

| 建什么 | 层 | 判据（V1.2 §3.2） | 制品载体 | 是否本次变更 |
|---|---|---|---|---|
| 产品**身份** `ProductOffering` | **L1** | B（域引用类：实例权威在产品主数据/SIM） | 公共本体（`CTR-SEM-003` 域） | **仅引用**（`Product→ProductOffering` 改名属 B-2 断点，**未签不得执行**） |
| 产品卡 / 版本 `ProductKnowledgeCard` / `ProductKnowledgeVersion` | **L2** | C（SSOT 在 KERT 工作区） | KERT 产品与知识供给本体 | 既有类，本次**引用并补 `describesProduct`** |
| **产品解读** `ProductInterpretation` | **L2** | C | 同上（`interprets` → `ProductOffering`） | **🆕 新增（本场景核心）** |
| **规则包** `RuleBundle` | **L2** | C | 同上（`rulesFor` → `ProductOffering`） | **🆕 新增（本场景核心）** |
| 消费入口 / 版本绑定 / 权限 | **L4** | 非 OWL | JSON Schema / OpenAPI（`CTR-PKC-API-001` / `CTR-PKC-DOM-001`，已登记） | 已就位，仅需口径对齐说明 |
| 产品类型 / 分类词表 | **L4 受控词表** | SKOS | 注册中心 | 本场景**不涉及** |

**结论**：本场景 = **L2 新增/完善 + 引用 L1 + L4 登记**。**不**改 legacy `gits-core.owl.ttl`（32 类混层件）、**不**在 `products.ttl` 堆业务关系、**不**新造并行产品关系（关系类型权威在 L2，实例权威在产品卡 front matter，`GK17-WP1.3-产品关系权威归属裁定-V1.0.md:27-29`）。

---

## 1. 受影响钉值方清单（as-is 实测）

| # | 钉值方 | 现钉值 / 现状 | 影响类型 | 回源 |
|---|---|---|---|---|
| P-1 | KERT `90_control/schema/ontology_reference.json` | `contractId=CTR-SEM-002`、`authorityRepo=gits-cbanking`、`authoritySource=specs/semantic/gits-core.owl.ttl`、`contentSha256=705578d6324abd0c1bd2bd670e6f3c0ffd8e04c358d0134246c89a3acfc38d00`、`pinnedAt=2026-09-15` | **权威源路径 + 内容哈希双失效**（Wave 3 换消费） | 实测读取该 JSON |
| P-2 | KERT `90_control/ontology/` 只读副本（4 件 `.ttl`）+ `PROVENANCE.json` | 逐件 sha256 钉值 | 副本集变更（改放「L1 副本 + L2 本体」） | 执行计划 V2.0 §3 WI-03-1 |
| P-3 | KERT `examples/bank-front-knowledge-maps/90_control/ontology/gits-core.{owl,shacl}.ttl` | 第二份副本（现有） | 同上，需纳入同一变更窗口 | 实测 `ls` 命中 |
| P-4 | GITS `apps/api/.../config/KnowledgeArchitectureConfig.java:167-171` | `@Value("${gits.semantic.ontology:specs/semantic/gits-core.owl.ttl}")` → `JenaOntologyAdapter` | **绑定路径失效**（Wave 3 改指 `gits-operational.owl.ttl` + `owl:imports`） | `:167-171` |
| P-5 | GITS `specs/CONTRACT_INDEX.yaml`（`CTR-SEM-001/002`） | 现状登记 legacy 单件 | 需**新增** `CTR-SEM-003`（L1）/`CTR-SEM-004`（L2）/`CTR-SEM-005`（L4 注册表）并收窄 `CTR-SEM-002` 为 L3 | 执行计划 V2.0 §3 WI-02-1 |
| P-6 | GITS `generated/semantic/gits-core.shacl.ttl`（生成物） | 由 `contract_pipeline.py` 生成 | 目标态拆为三份 SHACL；**禁手改** | V1.2 §2.0「生成物纪律」 |
| P-7 | GITS `specs/knowledge-architecture/instances/product/products.ttl:2-3` | **已整改（C-2）**：术语前缀 `gits: → https://gientech.com/gits/kno/`；产品实例改用 `prod: → https://gits.bank.example/ontology/core#`（术语/实例**分前缀**） | 原 R1 `ONTOLOGY_PREFIX_COLLISION` **已消除**；**残留**：实例命名空间仍是占位根域 ⇒ 正式 IRI 一律受 **D3 未签**阻塞 | 实测 `head -8` 该文件（2026-09-21） |
| P-8 | GITS `scripts/onto1_namespace_collision_check.py:308-309` | `vacuous = (versions_total == 0)`：closure 内 0 个 `owl:versionIRI` ⇒ 单版本约束**空转，不计为覆盖** | 空转判据现存位置在此（**非** `gk17_triple_consistency_check.py`，该脚本已无 `vacuous`/`targetedInstances` 字样 ⇒ 复审期 `:557-562` 引用已失效） | 实测 grep（2026-09-21） |
| P-9 | **本场景新增钉值方**：L2 制品（`ProductInterpretation` / `RuleBundle` 及其 Shape） | 暂无（不存在） | 新增后产生新钉值方：L1 import `versionIRI` 钉 + 内容哈希（R9） | 本件 §3 |
| P-10 | **L4（本场景既有）** `CTR-PKC-API-001` / `CTR-PKC-DOM-001` + `generated/openapi/product-center.normalized.json`、`generated/product-center/product-center-domain.schema.json` | 已登记（PC0），**不含 `owl:imports`、不钉本体哈希** | **不受 IRI 迁移直接影响**；仅需在说明中登记「`ProductOffering` 口径变化」（§4 重钉清单 R-6） | `specs/CONTRACT_INDEX.yaml`（本场景 PC0 条目） |
| P-11 | GITS `specs/knowledge-architecture/instances/product/projection-config.json` | `schema=ONTO1-PROJECTION-CONFIG/1.0`、`version=1.0.0`、`effective=2026-09-21`、`simulationOnly=true`、`formalRelationRelease=NOT_AUTHORIZED`、`forbiddenConstructs=[owl:equivalentClass]`、`sha256=6a4c53aff0984202…` | **新钉值方**：SIM 投影配置（版本 + 哈希被投影产物引用） | 实测读取（2026-09-21） |
| P-12 | GITS `specs/knowledge-architecture/instances/product/sim/product-relations.SIM.ttl` | SIM 关系投影**生成产物**（`simulation_only`，显式排除 `QUARANTINED_UNRESOLVED` 关系），头部钉 `config_sha256=6a4c53aff0984202` | **新钉值方**：配置一变即需重建；**勿手工编辑** | 实测 `head -14`（2026-09-21 13:05） |
| P-13 | GITS `specs/knowledge-architecture/instances/product/UNRESOLVED.json` | `productIndividuals=13`、`relationInstances=0`、`unresolvedReferenceCount=40`（**40 条逐条登记**：card/field/ontology_property/referenced_symbol/resolved_to）；`relationTypeAuthority=ontology`、`relationInstanceAuthority=product cards` | **D2 处置登记载体**；分类未签前 CQ3-S4 保持 `NOT_EVALUATED` | 实测读取（2026-09-21） |

**已由 ONTO1 Wave -1 覆盖、本件不重复造的部分**：全仓消费者全量扫描（`loops/ONTO1-ontology-split/evidence/consumer-scan-manifest.json`：`baseline_sha256=705578d6…`、`total_hits=26690`、`net_obligations=1052`、`orphan=0`、`pending_triage=0`）。本件只补充**产品解读场景子集**的处置口径。

---

## 2. planHash 失效范围

**机制（实测回源）**：`KnowledgeArchitectureConfig.java` 注释明写「版本由**本体内容 SHA-256** 派生 ⇒ 本体一变，`versions.ontology` 与 `planHash` 必变（判据 V2）」，绑定默认路径 `specs/semantic/gits-core.owl.ttl`（`:167-171`）。

| 影响面 | 说明 | 处置 |
|---|---|---|
| `versions.ontology` 子块 | 由本体文件内容哈希派生 | 拆分后**必然变化**（即使 IRI 集合不变，文件切分即改变字节） |
| `planHash` | 含 `versions.ontology` | 所有已产出并钉值的 `planHash` **全量失效** |
| 已钉 `planHash` 的夹具 / 证据 | GK17 及后续 Loop 的 plan trace、`evidence/` 中钉 hash 的记录 | 需按 Wave 3 的「先钉新值 → 再切消费」重新生成；旧值保留只读 ≥1 窗口期 |
| 本场景 L4 合同 | `CTR-PKC-*` **不含**本体哈希 | **不在失效范围**（无需重钉） |
| SIM 投影件（P-11/P-12） | `sim/product-relations.SIM.ttl` 头部只钉 **config_sha256**（`projection-config.json`） | **不因本体拆分而失效**；仅当投影配置版本变更时需重建（实例层非本体） |

**不承诺项**：受影响 `planHash` 的**精确条数**未统计（需先完成 Wave 3 双仓切换后重跑才能计数）⇒ 本条状态 `NOT_EVALUATED`，**不得**在汇报中给具体数字。

---

## 3. 重钉清单（谁、改什么、钉到什么、前置门禁）

| # | 钉值方 | 重钉动作 | 新钉值来源 | 前置门禁 |
|---|---|---|---|---|
| R-1 | KERT `ontology_reference.json` | `authorityRepo`→`Leibniz-KERT`、`authoritySource`→公共模块 `public-ontology/src/public-kno.owl.ttl`、`contentSha256`→新件哈希、`authorityEntity` 与 `hostingRepo` **分列且不得同值** | 公共模块发布件 | **D3 联签**（根域）+ 公共语义 Owner 任命 |
| R-2 | KERT `90_control/ontology/` + `PROVENANCE.json` | 改放「L1 副本 + L2 本体」，逐件 sha256 | 同上 | 同 R-1 |
| R-3 | GITS `KnowledgeArchitectureConfig` 绑定值 | `specs/semantic/gits-operational.owl.ttl`（含 `owl:imports` 公共模块本地副本 + `versionIRI` 钉） | L3 制品 | `CTR-SEM-*` 登记完成 + `make generate`/`check` 绿 |
| R-4 | GITS `CONTRACT_INDEX.yaml` | 新增 `CTR-SEM-003/004/005`（**各自独立 generated 目标**）；收窄 `CTR-SEM-002` | 执行计划 §3 | 本件 + 计划评审通过 |
| R-5 | GITS `products.ttl:1` 前缀 | 前缀与本体一致（D3 前不得填正式根域；`PENDING:` 占位不得进发布制品） | ADR-ONTO1（待签） | **D3 未签 ⇒ 本项阻塞** |
| R-6 | 本场景 L4 合同说明 | 在 `specs/product-center/README.md` 登记「产品身份口径 = L1 `ProductOffering`（A-Box：产品主数据/SIM `SIM-PRODUCT-CATALOG`；KERT 产品卡为 L2 知识内容）」；`productId` 数据值域**不变**（`^PROD-[A-Z]+-[0-9]{3}$`） | 本场景 PC0 合同 | 无（纯说明，PC1 前完成） |
| R-7 | 新 L2 制品（`ProductInterpretation`/`RuleBundle`） | 发布时钉：L1 `owl:imports versionIRI` + 内容哈希；Shape 由源模型生成 | KERT 知识供给本体 | 公共语义 Owner 任命 + DESIGN_APPROVED |

---

## 4. 消费方清单（产品解读场景子集）

| 消费方 | 位置 | 消费内容 | 影响 |
|---|---|---|---|
| 产品解读页（前端） | 本场景 PC1–PC5（`/product-center`） | L4 `CTR-PKC-API-001`（**不直接消费 OWL**） | **不受本体拆分影响**（P3 跨仓零直读） |
| GITS 规划器 | `DefaultActivationPlanner.versions.ontology` | 本体版本子块进 `planHash` | 受 planHash 失效影响（§2） |
| GITS 三条一致性门禁 | `scripts/gk17_triple_consistency_check.py` 等 | 32 类/34 属性/实例数 | vacuous 判定须随 R4 改为「空转=失败」 |
| KERT 物化链路 | `ontology_materialize.py`（类/属性/Shape parquet） | L1 副本 + L2 本体 | 角色枚举 4→（PUBLIC/KERT/GITS-EXTERNAL），旧值兼容读取一窗口期 |
| KERT 知识路由 | 知识地图/`AC-*`（`ASSET-KNOW-PRODUCT-CARDS`） | 只指向资产，**不复述产品关系** | 产品关系变更**不**触发地图改动（WP1.3 §2） |
| 产品卡（A-Box） | KERT `03_core/*/product-cards/PROD-*.md` front matter | 产品关系的**实例权威** | 本场景**不改产品卡**；关系实例仍由产品 Owner 维护 |

**明示不消费**：`scenario/seed/05_knowledge/ontology_seed.json` 的越界类型（`Party`/`Utterance`/`Need`/`VisitPlan`/`QuestionPlan` 等）不在本场景范围内，且不在 45 项目标清单中（V1.2 §2.1 第 3 行列其为缺陷）。

---

## 5. 本件的未决与阻塞（不由实现负责人裁决）

| # | 事项 | 决策方 | 本场景影响 |
|---|---|---|---|
| 1 | `Product ⇒ ProductOffering` 改名 | **B-2 断点签字**（出口 A 清单已备，100 文件/288 命中，**未签**） | 未签 ⇒ 涉及 `Product` 的改名动作**一律不执行**；本场景按「引用 L1、不改名」推进 |
| 2 | 根域字面量与联签（D3） | 语义架构 Owner + 域名/基础设施 Owner | 阻塞 R-1/R-5 与一切新 IRI 发布；L1 一律 `PENDING:{NS-L1}#X` |
| 3 | 40 处悬空产品引用分类 | **产品 Owner**（D2） | 已由 `UNRESOLVED.json` **逐条登记**（40 条），但**分类结论未签** ⇒ CQ3-S4 保持 `NOT_EVALUATED`；**不得永久豁免**；SIM 关系投影（P-12）已显式排除 `QUARANTINED_UNRESOLVED`，且 `formalRelationRelease=NOT_AUTHORIZED` |
| 4 | 产品身份 A-Box 临时权威 | Owner 批准《SIM 临时模拟权威声明》（O-07 已具名 `SIM-PRODUCT-CATALOG`，声明**仍 NOT_EFFECTIVE**） | 未生效前不得作为 `PASS` 依据 |
| 5 | 场景 §3「同业同类产品比对」红线冲突 | Owner 三选一（A 本行产品间对比 / B 公开参考脱敏展示 / C 真做同业比对） | 未选前**不落合同、不建字段** |
| 6 | O-2 `playedBy` 是否登记为第 37 条属性 | 设计 Owner | 影响属性计数自洽（36→37），**不影响本场景** `interprets`/`rulesFor` 的新增计数登记 |

---

## 6. 复现命令

```bash
# 钉值方实测
python3 -c "import json;d=json.load(open('/home/szf/dev/Leibniz-KERT/examples/bank-front-knowledge-maps/90_control/schema/ontology_reference.json'));print(d['contractId'],d['authoritySource'],d['contentSha256'])"
sed -n '160,175p' apps/api/src/main/java/com/gien/gits/api/config/KnowledgeArchitectureConfig.java
sed -n '1,8p'     specs/knowledge-architecture/instances/product/products.ttl   # 术语/实例分前缀（C-2 已整改）
python3 -c "import json;d=json.load(open('specs/knowledge-architecture/instances/product/UNRESOLVED.json'));print(d['productIndividuals'], d['relationInstances'], d['unresolvedReferenceCount'], d['relationTypeAuthority'], d['relationInstanceAuthority'])"
sed -n '1,14p'    specs/knowledge-architecture/instances/product/sim/product-relations.SIM.ttl
sed -n '127,129p' specs/semantic/gits-core.owl.ttl

# 消费者扫描（复用 ONTO1 Wave -1 产出，不重造）
python3 -c "import json;print(json.load(open('loops/ONTO1-ontology-split/evidence/consumer-scan-manifest.json'))['net_obligations'])"

# 空转现状（判据须改「空转=失败」）
grep -n "vacuous" scripts/gk17_triple_consistency_check.py | head -5
```
