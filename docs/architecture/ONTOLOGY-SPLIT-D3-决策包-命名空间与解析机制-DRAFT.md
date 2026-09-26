> 本文件是 **D3 决策包（DRAFT）**：为双 Owner 提供选项、权衡、可判定性与验收条件。**它不做决策、不选根域、不填根域**（详见 §0）。

# ONTOLOGY-SPLIT-D3 决策包：公共语义中立 IRI 根域与解析机制

| 项 | 值 |
|---|---|
| 文档编号 | `ONTOLOGY-SPLIT-D3-PACK`（DRAFT，非受控合同、非 ADR） |
| 文档性质 | **决策包 / 送审输入**——不是决策，不含已选项，不含任何根域字面量 |
| 决策对象 | **D3**：中立 IRI 根域与解析端点（`docs/review/ARCH-ONTO-2026-001-rereview-package/11-外部依赖登记表.md §D3`） |
| 决策 Owner | **语义架构 Owner + 基础设施/域名 Owner（联合批准，双签）** |
| 当前门禁 | `RETURN_TO_HLD` 有效；本文件**不代表** `DESIGN_APPROVED`，不代表 ADR 已接受，不代表 D3 已签署 |
| 上游依据 | `docs/architecture/ADR-ONTO1-namespace-neutral-iri-DRAFT.md`（§3 未决项、§5.1 三分法、§5.4 碰撞检查）；设计 V2.0 §7；复审包 `04-基线32项映射表.md §D`、`11-外部依赖登记表.md §D3` |
| 机读产物 | `loops/ONTO1-ontology-split/evidence/iri-mapping-draft.csv`、`iri-mapping-draft-summary.json`、`namespace-known-defects.json` |
| 可执行原型 | `scripts/onto1_iri_mapping_draft.py`、`scripts/onto1_namespace_collision_check.py` |
| 撰写角色 | `semantic-namespace-analyst`（tech_lead 委托、只读分析；**未认领 baton、未记任何门禁**） |
| 日期 | 2026-09-20 |

---

## 0. 本文件是什么 / 不是什么（先读）

**是**：D3 两个子问题的**选项与权衡**（根域类别、解析机制）、逐术语 `oldIRI → newIRI` 映射草案与语义关系分类、碰撞检查的可执行原型与变异复验、双发布窗口与退役门的**参数化建议**、以及 Owner 决议所需的最小填空板。

**不是，且全程不得被这样使用**：

| 禁止 | 本文件的处置 |
|---|---|
| 选根域 / 填根域 | 全文以符号 `{ROOT}`、`{NS-L1}`~`{NS-L4}` 表述；**不提供任何候选字面量**（提供候选字面量即等于替 Owner 选） |
| 发布新 IRI / 重钉 / 退役旧 IRI | 未做；映射草案的新端一律保持 `PENDING:` 占位形态（脚本 `R1` 内建红线） |
| 写入正式制品 | 未改 `specs/**`、`generated/**`、本体与 A-Box 制品；全仓实测不存在 `namespaces.json`（该文件名在上述红线清单中出现，实际无此文件） |
| 标 `DESIGN_APPROVED` / 关闭 D3 / 关闭 U-1~U-4 | 未做；`ADR-ONTO1 §3` 未决项逐项保持未决 |
| 被当作 Gate 依据 | 本文件不入 `LOOP.yaml.gates`、不入 `EVIDENCE.json`；实测结果只登记为证据日志 |

**与 `specs/` 冲突时以 `specs/` 为准。**

---

## 1. 事实基线（全部回源到 `文件:行`）

| # | 事实 | 出处 |
|---|---|---|
| F1 | 旧公共命名空间 = `https://gientech.com/gits/kno/`，短前缀 `gits:` | `specs/semantic/gits-core.owl.ttl:1` |
| F2 | 该本体声明 `gits:CoreOntology a owl:Ontology`；**无 `owl:versionIRI`、无 `owl:imports`** | `specs/semantic/gits-core.owl.ttl:8`（全文件无 `versionIRI`/`imports`） |
| F3 | 旧端术语实测 **67** 项 = 32 类 + 34 对象属性 + 1 数据属性 | 由 F2 文件按 `a owl:{Class,ObjectProperty,DatatypeProperty}` 重建（脚本 `C-1a`） |
| F4 | **第二个命名空间**被同一 `gits:` 前缀指向：`https://gits.bank.example/ontology/core#` | `specs/knowledge-architecture/instances/product/products.ttl:1` |
| F5 | `gits:Customer` 在 R2RML 映射中被消费，且 `rr:template` 直接拼旧命名空间下的实例 IRI | `specs/data/customer-source-mapping.r2rml.ttl:2`、`:14`（`rr:class gits:Customer`）、`:12` |
| F6 | A-Box 实例与 T-Box 类**同名不同 IRI**：`gits:prod_cb_001 a gits:Product`，其中 `gits:` 指 F4 的命名空间 | `specs/knowledge-architecture/instances/product/products.ttl:10`（同类实例多行） |
| F7 | 迁移域 67 项；语义关系分布 `RETAINED 32 / RETAINED_AUTHORITY_MOVED 4 / REMODELED 23 / TRANSFORMED 7 / DEPRECATED 1`；无旧端的净新增 20 项 | `evidence/iri-mapping-draft-summary.json`（本轮产物） |
| F8 | 消费面：词法命中 26690 / 4818 文件；净迁移义务 file 级 1052 行 = `CONTROL_PLANE_REQUIRED` 14 + `FOLLOW_MIGRATION` 1038（**后者是候选义务**） | `evidence/consumer-scan-manifest.json`；`evidence/consumer-scan-obligations.csv` |
| F9 | F4/F5/F6 构成两处真实前缀缺陷，已**具名登记**（含 Owner 与解除条件） | `evidence/namespace-known-defects.json`（`KD-NS-001`，覆盖 `C-2a`/`C-2b`） |

**推论（供判定用，不构成决策）**：新根域若不先解除 F4/F6，"旧前缀双绑定"会把新 IRI 迁移叠加一层错配噪声（`ADR-ONTO1 §7` 已列出"须先修 C-2"）。因此 **D3 的"碰撞检查绿"解除证据在当前状态下不可获得**（§7 实测 exit 3）。

---

## 2. Owner 需要回答的决策问题（D3-Q1~Q8）

| 问题 | 内容 | 为什么必须 Owner 定 |
|---|---|---|
| **D3-Q1** | 根域**类别**：企业自有域 / 组织中立持久域 / 受控离线命名空间（或其变体） | 涉及机构域名资产与对外承诺；见 §3 |
| **D3-Q2** | 若选可解析类根域：用**现有企业域的子域/子路径**，还是**新注册的独立域名** | 涉及注册人、DNS 控制权、组织变更时的存续 |
| **D3-Q3** | 单根还是多根：`{NS-L1}`~`{NS-L4}` 是否共用同一根域 | 影响解析服务数量、OPEX、"单一发布权威"的可验证性 |
| **D3-Q4** | 解析机制：在线 303 + 内容协商 / 离线内容寻址 / 组合 | 见 §4 |
| **D3-Q5** | 双发布窗口长度与退役门参数（含具名豁免与冻结期） | 见 §6 |
| **D3-Q6** | 根域**持久性承诺**的书面边界（"多久不变"、"变更时的迁移义务"） | 裁定 1 要求"中立、持久"，而"持久"的项目化定义只能由 Owner 给 |
| **D3-Q7** | 解析端点由谁运维、OPEX 承担方、SLA 与失败责任 | 平台/域名 Owner 职责边界 |
| **D3-Q8** | **外部可引用性**诉求：是否要求体系外（同业、监管、第三方工具）直接解引用 | 决定 §3 中 ROOT-C 是否可行 |

---

## 3. 候选根域方案对比（只列类别与权衡，**不填字面量、不推荐**）

### 3.1 选项定义

| 选项 | 类别 | 形态记号（**不是**候选值） | 说明 |
|---|---|---|---|
| **ROOT-A** | **企业自有域** | `{ORG-DOMAIN}`：机构**当前已控制**的域名，取其专用子域或专用路径 | 复用既有 DNS 资产；注册/审批路径最短 |
| **ROOT-B** | **组织中立持久域** | `{DEDICATED-ROOT}`：机构控制的**专用、不与某系统/产品名绑定**的持久标识域 | 最贴合裁定 1 的"中立 + 持久"字面要求；需显式持久承诺 |
| **ROOT-C** | **受控离线命名空间** | `{OFFLINE-SCHEME}`：IRI 不承诺公网可解析，解析完全走受控离线包 | 把"可解析"从 DNS 责任中剥离；在线可发现性归零 |
| **ROOT-D**（变体） | 混合/分层根 | `L1` 用 A 或 B，`L2/L3/L4` 沿用相应机构域 | 保留层次语义；代价是解析服务与签名方数量上升 |

> `{NS-L1}`~`{NS-L4}` 的命名规则约束（`UpperCamelCase` 术语段、保留段 `LEGACY/` 与 `_meta/`、禁动态 IRI）见 `ADR-ONTO1 §4`，对三个选项同等适用。

### 3.2 六维权衡矩阵

口径：**✅ 有利 · ⚠️ 有条件/需额外承诺 · ❌ 不利 · ❓ 取决于 Owner 未给的前提（不得代替判定）**

| 维度 | ROOT-A 企业自有域 | ROOT-B 组织中立持久域 | ROOT-C 受控离线命名空间 | ROOT-D 混合分层根 |
|---|---|---|---|---|
| **持久性** | ⚠️ 取决于该域是否属"商品/项目名"；组织调整可能被回收 | ✅ 专用标识域 + 书面持久承诺，最贴合"持久" | ✅ 不依赖 DNS 存续，IRI 字符串持久性最高 | ⚠️ 各层各自决定，整体=最弱层 |
| **控制权** | ✅ 已有控制权；变更走既有 IT 流程 | ⚠️ 需**明确归属**（法人？部门？）与注册人治理 | ✅ 完全内部，无外部注册依赖 | ⚠️ 多层多主体，治理面扩大 |
| **解析能力** | ✅ 可上 303 + 内容协商（前提：HTTPS 与内网可达） | ✅ 同 A | ❌ 公网不可解引用；仅离线/内网受控解析 | ⚠️ 各层能力不一致，需分别测试 |
| **OPEX** | ✅ 边际成本最低（复用现有托管） | ⚠️ 新增域名年费 + 证书 + 解析服务运维 | ✅ 无 DNS/证书成本，但需**内容寻址包发布管道** | ❌ 多套解析服务与证书；治理与巡检成本叠加 |
| **迁移影响** | ⚠️ 与旧命名空间差异小 ⇒ 消费方改动集中在 IRI 字符串；但**易与旧前缀混淆**（F4 本就是这个形态） | ✅ 命名空间明显可区分 ⇒ 漂移检测（C-1b/C-2）更易有牙齿 | ⚠️ scheme 变化大 ⇒ 消费方解析代码路径需改写（影响面见 F8） | ❌ 需区分四套；plan hash 派生链逐环验证工作量最大 |
| **外部可引用性** | ⚠️ 对外暴露企业域，可能触发安全/信息暴露评审 | ✅ 中立域对外语义最清晰 | ❌ 第三方无法解引用（只能拿到包） | ⚠️ 分层差异导致对外表述复杂 |

### 3.3 每选项的后果与失败模式（"代价清单"）

**ROOT-A 企业自有域**
- 正向：迁移期最短；消费方（含 KERT 侧钉值件）改动面最小；无需新采购。
- 代价/风险：与 F4 现有"第二个命名空间"形态同族 ⇒ 治理不当会再次出现"同前缀多命名空间"静默错配；企业域名因组织调整被回收时，**持久性承诺不可兑现**。
- fail 模式：把"当前可解析"误当成"永久可解析"。

**ROOT-B 组织中立持久域**
- 正向：同时满足"中立"（不与单系统绑定）与"持久"（专用标识）；对外表述清晰；碰撞检测最易有牙齿。
- 代价/风险：需**新增域名注册 + 归属治理 + 续费责任**；若归属写成某项目/小团队，"中立"只是名义；域名到期即全局断链。
- fail 模式：无书面的续费与归属责任 ⇒ 若干年后成为单点。

**ROOT-C 受控离线命名空间**
- 正向：不引入 DNS/证书/在线服务依赖；离线与内网环境（本项目多处为内网）可用性最好；与内容寻址（§4 MECH-B）天然配套。
- 代价/风险：**在线 303 选项自动出局**，D3 解除证据中"HTTP 303/内容协商可解析测试记录"须改为"离线解析 + 哈希钉值验证记录"（`11-外部依赖登记表.md §D3` 原文为"或"，故合规）；外部第三方无法解引用 ⇒ 若 Q8 答"需要外部引用"，本选项不可行。
- fail 模式：不可解析被静默当作"可解析"。

**ROOT-D 混合分层根**
- 正向：尊重四层模型，各层权威方各自持有标识。
- 代价/风险：解析服务从 1 套变 N 套；退役门与碰撞检查须在 N 套上分别通过；`{NS-L1}` 的中立性会被 L2/L3 的非中立根稀释。
- fail 模式：某一层漏签/漏测却被整体报绿。

> **本节不含推荐。** 若 Owner 只需"最小可判定集"，可先回答 Q1+Q2+Q3+Q8，其余按 §4/§6 的建议进入下一轮。

---

## 4. 解析机制方案对比（D3-Q4）

### 4.1 选项

| 选项 | 机制 | 对应 D3 解除证据 |
|---|---|---|
| **MECH-A** | 在线：HTTP `303 See Other` + 内容协商（`Accept: text/turtle`）指向受控制品 | "HTTP 303/内容协商可解析测试记录" |
| **MECH-B** | 离线受控：发布**内容寻址包**（manifest + `sha256`），消费方按哈希钉值解析 | "受控离线解析 + 哈希钉值" |
| **MECH-A+B** | 303 的解析目标**本身**是内容寻址制品（在线发现 + 离线可校验） | 两条同时满足 |

### 4.2 权衡

| 维度 | MECH-A 在线 303 | MECH-B 离线内容寻址 | MECH-A+B |
|---|---|---|---|
| 前置条件 | DNS + TLS + 内网可达 + 常驻解析服务 | 包发布管道 + 钉值分发 | 两者之和 |
| 内网/离线可用性 | ❌ 断网即不可解引用 | ✅ 完全可用 | ✅（离线降级为 B 路径，**须显式声明**而非静默） |
| 可验证性 | ⚠️ 内容正确性需额外校验（303 目标可能被替换） | ✅ 内容哈希即验证；与 C-4 钉值同源 | ✅ 最强 |
| 版本语义 | ⚠️ 303 目标随发布漂移，需版本化 URL + 内容哈希 | ✅ manifest 显式列版本与哈希 | ✅ |
| OPEX | ⚠️ 常驻服务 + 证书续期 | ✅ 无常驻服务（可静态托管） | ⚠️ 两者之和，但可共享一套制品 |
| 迁移期成本 | ✅ 消费方改动最小（仍是 HTTP 取回） | ⚠️ 消费方需接入 manifest/哈希校验 | ⚠️ 两条路径都要接 |
| 失败面 | DNS / 网络 / 证书 | 包完整性与分发 | 并集（须分别有负例） |

### 4.3 fail-closed 要求（**共同，不可裁剪**）

| # | 要求 | 判据（可测试） |
|---|---|---|
| **F1** | 不可解析 ⇒ **具名拒绝**（含 reason code） | 拒绝路径必须返回固定错误标识，不得返回空文档、空图或 `200 + 空 body` |
| **F2** | 解析结果**必须可哈希校验**，与 C-4 钉值同源 | 制品内容哈希 ≠ 钉值 ⇒ 具名漂移拒绝（复用碰撞检查 `C-4` 判定） |
| **F3** | **禁止静默降级**：不得回退为"文本比对"、不得回退为"上一次已知版本"、不得把失败降为 warning | 负例夹具必须证明"失败 ⇒ 判定失败"，而非"失败 ⇒ 仍然通过" |
| **F4** | 内容协商失败/超时/非预期 media type 一律拒绝 | 404 / 500 / `Accept` 被忽略（返回 HTML）/ 超时 四类负例 |
| **F5** | 离线路径必须能在**无 DNS** 环境重塑同一内容 | 断网噪声下正例必须通过（否则 MECH-A 单独使用不满足"可离线复现"） |
| **F6** | 拒绝可测试且**有牙齿**：每条拒绝路径 ≥1 负例夹具，且负例必须被门禁判 FAIL（变异复验） | 参照本仓既有教训：**只测正例无法证明否定式要求**（负例空转案例） |
| **F7** | 解析失败必须**影响判定结果**（构建/运行时/契约校验任一处硬失败），而非仅记日志 | 需指出具体失败落点，禁止"仅告警" |

### 4.4 D3 解除证据的最小测试包（建议形态，供 Owner 采纳或改判）

| 类别 | 数量下限 | 内容 |
|---|---|---|
| 正例 | 1 | 术语 IRI → 解析到**哈希与钉值一致**的制品（在线与离线各 1 更佳） |
| 负例 | ≥4 | ① 404/不存在 ② media type 不符 ③ 内容哈希不符 ④ 超时或网络不可达 |
| 变异复验 | ≥2 | 把负例夹具改成"通过"必须被门禁拦下；恢复后必须通过 |

---

## 5. 逐术语 `oldIRI → newIRI` 映射草案（机读：`evidence/iri-mapping-draft.csv`）

### 5.1 方法与计数

判定表（顺序即优先级，未命中即 fail-closed）见 `scripts/onto1_iri_mapping_draft.py` 模块 docstring；判据来源为 `ADR-ONTO1 §5.1` + 复审包 `04-基线32项映射表.md §D`。本轮实测：

| 语义关系 | 计数 | 允许绑定（草案） | `equivalentClass/Property` |
|---|---|---|---|
| `RETAINED` | 32 | `owl:equivalentClass` / `owl:equivalentProperty` | **ALLOWED** |
| `RETAINED_AUTHORITY_MOVED` | 4 | 同上，**但须先经 TL 显式裁定"权威层迁移≠语义变更"** | 默认不放行（待裁定） |
| `REMODELED` | 23 | SKOS `closeMatch`（`exactMatch` 需公共语义 Owner 书面确认，**当前 NOT_GRANTED**） | **FORBIDDEN（硬约束）** |
| `TRANSFORMED` | 7 | 注册表 **RDF 投影**；不建 OWL 等价 | **FORBIDDEN（不同构）** |
| `DEPRECATED` | 1 | `owl:deprecated` + `dcterms:isReplacedBy` → `SourceIdentifier` 模式 | **FORBIDDEN** |
| `NEW_TERM_NO_LEGACY_IRI` | 20 | 不适用（无旧端） | NOT_APPLICABLE |
| **迁移域合计** | **67** | — | — |

### 5.2 代表行（每类示例；全量见 CSV）

| termId | 旧 IRI（LEGACY，只读） | 新 IRI 草案 | 语义关系 | 依据 |
|---|---|---|---|---|
| `Task` | `{LEGACY-NS}Task` | `PENDING:{NS-L3}#Task` | `RETAINED` | 基线原名（`linkml.yaml:207-220`） |
| `LegalEntity` | `{LEGACY-NS}LegalEntity` | `PENDING:{NS-L1}#LegalEntity` | `RETAINED_AUTHORITY_MOVED` | `gits-core.owl.ttl:119-121`（层迁移至 L1） |
| `CustomerRole` | `{LEGACY-NS}Customer` | `PENDING:{NS-L1}#CustomerRole` | `REMODELED` | 基线 `Customer` 重构（`linkml.yaml:25-36`） |
| `EnterpriseGroup` | `{LEGACY-NS}CorporateGroup` | `PENDING:{NS-L1}#EnterpriseGroup` | `REMODELED` | 基线 `CorporateGroup` 改名（`gits-core.owl.ttl:115-117`） |
| `gateOfCustomer` | `{LEGACY-NS}gateOfCustomer` | `PENDING:{NS-L3}#gateOfCustomer` | `REMODELED` | range 改指 `CustomerRole` |
| `ActivationContract` | `{LEGACY-NS}ActivationContract` | `REGISTRY:ActivationContract` | `TRANSFORMED` | OWL 类 → JSON Schema 对象 |
| `hasTaskType` | `{LEGACY-NS}hasTaskType` | `SCHEMA-FIELD:hasTaskType` | `TRANSFORMED` | OWL 属性 → L4 Schema 字段 |
| `TaskTypeScheme` | `{LEGACY-NS}TaskType` | `SKOS:TaskTypeScheme` | `TRANSFORMED` | OWL 类 → SKOS 概念体系（**同时改名**） |
| `customerId` | `{LEGACY-NS}customerId` | `RETIRED:customerId` | `DEPRECATED` | 基线 datatype 属性退役 |
| `SourceIdentifier` | —（无旧端） | `PENDING:{NS-L1}#SourceIdentifier` | `NEW_TERM_NO_LEGACY_IRI` | 承接 `customerId` 退役（`isReplacedBy`，**非等价**） |

> `{LEGACY-NS}` = 实际旧命名空间（F1），由脚本**从本体读取**，未硬编码。

### 5.3 三处必须由人裁定的判断（分析角色不代答）

| # | 待裁定 | 影响 | 落在哪些行 |
|---|---|---|---|
| **J-1** | "权威层迁移（L3→L1/L2）是否算语义变更" | 决定 4 项 `RETAINED_AUTHORITY_MOVED` 能否用 `equivalentClass`；若答"算"，须降级 `closeMatch` | `LegalEntity`、`ProductKnowledgeCard`、`ProductKnowledgeVersion`、`supersedesVersion` |
| **J-2** | `REMODELED` 中是否有可升级为 SKOS `exactMatch` 的项 | 影响消费方等价推理强度；当前一律 `closeMatch`（保守） | 23 项 `REMODELED`，尤其"仅改名/重构、定义未收窄"者 |
| **J-3** | `CapabilityPublication` 的双重性质表述 | 它**同时**命中"重构"与"制品类型转换（→ Schema 对象）"；分类按证据归 `REMODELED`，而等价禁用由**两重理由**共同支撑（脚本 `R5`：`制品类型转换=是` 一律禁等价） | `CapabilityPublication` |

### 5.4 脚本内建红线（防"人改产物"绕过）

| 红线 | 内容 | 复验 |
|---|---|---|
| `R1` | 新 IRI 只允许 `PENDING:{NS-L*}` / `REGISTRY:` / `SKOS:` / `SCHEMA-FIELD:` / `RETIRED:` 形态；**任何 `http(s)://` 字面量一律 FAIL**（含 `.example`、`localhost`），且约束**作用于全部 87 行（含净新增术语）** | 变异 `M3` |
| `R2` | 非 `RETAINED*` 行的等价可用性必须为 `FORBIDDEN`；`--gate` **从磁盘重读产物**再判（防分类器自证清白） | 变异 `M5` |
| `R3` | 计数锚定：87 行 / 45 模型资产 / 迁移域 67 / 六类关系计数 32·4·23·7·1·20 | 变异 `M1`、`M2` |
| `R4` | 旧 IRI 与新 IRI 草案各自在草案内唯一（C-1 前置） | 变异 `M4` |
| `R5` | `制品类型转换=是` ⇒ 无论关系标签为何一律禁等价（非同构） | 与 `R2` 双路径覆盖 |

---

## 6. 双发布窗口与退役门：参数化建议（D3-Q5）

> `ADR-ONTO1 §5.2` 只给下限（≥1 发布周期）与 4 条退役门条件。本节把它**参数化**，逐项给建议值、理由与"谁定"。**建议值不是决策值。**

| # | 参数 | 建议值（DRAFT） | 理由 / 判据 | 谁定 |
|---|---|---|---|---|
| **P-1** | 窗口计量单位 | **发布周期数** | 与"发布"而非"日历"绑定，避免冻结期落在无发布期 | 公共语义 Owner |
| **P-2** | 窗口长度 | **≥2 个发布周期**（设计下限 1；本建议=1 稳定 + 1 缓冲） | 单周期无回滚余地；`ADR §5.2` 下限已被满足 | 公共语义 Owner + TL |
| **P-3** | 窗口最短日历时长 | **≥90 天**（与 D2 的 40 悬空引用处置联动） | 迁移义务含 1052 行（其中 1038 行为**候选**，须逐条回源确认），日历下限防止"周期很短 + 义务未清" | 双 Owner |
| **P-4** | T0 起算点 | **三事件同批最晚者**：① 新 IRI 发布 ② 映射表发布 ③ 消费方通知送达 | 防止"发布了但没通知"被算作已过窗口 | 公共语义 Owner |
| **P-5** | 切换顺序 | **先钉 → 后切 → 旧值只读** | 与"双仓同窗口变更"纪律一致；逆向（先切后钉）会制造不可判定的中间态 | TL |
| **P-6** | 退役门硬条件 | **W1~W7 全部为真**（见 §6.2） | — | 双 Owner 联签 |
| **P-7** | 具名豁免 | 允许，但**必须**带 Owner + 解除条件 + 到期日；**不计入"100% 关闭"** | 与 `WAIVED_FOR_DEVELOPMENT` 纪律一致（豁免永不满足激活门禁） | 双 Owner |
| **P-8** | 冻结期 | 退役前 **≥14 天**禁新增消费方接入旧 IRI | 防止"边退役边新增"，使闭环不可达 | TL |
| **P-9** | 退役后记录 | 旧 IRI 标 `retired`，**记录不删**，映射保留 ≥ 审计期 | `ADR §5.2`：不再双发布但记录保留 | Integration Contract Owner |
| **P-10** | 参数落地位置 | 建议登记在 **L4 注册表**（机读），而非散落多份文本 | 避免参数漂移；与 C-4 钉值机制同源 | Integration Contract Owner |
| **P-11** | 回滚 | 双发布期内每周期至少 **1 次回滚演练**；映射表保留回滚点 | 迁移期最贵的失败是"切一半" | TL |

### 6.2 退役门判定式（建议）

```text
RETIRE_OK = W1 且 W2 且 W3 且 W4 且 W5 且 W6 且 W7

W1  WI-A2 处置表「CONTROL_PLANE_REQUIRED + FOLLOW_MIGRATION」100% 关闭，或具名豁免（带 Owner/解除条件/到期日）
W2  碰撞检查全判定且通过：C-1a 且 C-1b 且 C-2 且 C-3 且 C-4 = PASS（C-1b 不得为 NOT_EVALUATED）
W3  import closure 单一版本（同一 series 不得出现两个 versionIRI）
W4  双侧 Owner 签署退役记录（不得代签）
W5  已知缺陷登记表 namespace-known-defects.json 为空（登记即修复义务，退役前必须清零）
W6  冻结期满足（P-8）且冻结期内无新增旧 IRI 消费方
W7  回滚演练记录存在且通过（P-11）
```

> **W2 与 W5 当前必然为假**：`C-1b` 在 D3 未签期间为 `NOT_EVALUATED`，且 `C-2` 因两处真实冲突**当下即 FAIL**（§7 实测）；`W5` 的登记表当前有 2 项。这是**设计如此**，不是缺陷。

---

## 7. 可执行原型与实测结果（本轮，全部只读）

### 7.1 映射草案

| 命令 | 退出码 | 含义 | 证据 |
|---|---|---|---|
| `python3 scripts/onto1_iri_mapping_draft.py --gate` | **0 PASS** | `R1~R5` 全绿；写出 `iri-mapping-draft.csv`（sha256 `cbf9c24d9e2eed1c…`） | `evidence/wi_a4_iri_mapping_gate-20260920T142432Z.log` |
| `python3 scripts/onto1_iri_mapping_draft.py --selftest` | **0 PASS** | 5 条变异全部被拦 + 对照通过 | `evidence/wi_a4_iri_mapping_selftest-20260920T142432Z.log` |

### 7.2 碰撞检查

| 命令 | 退出码 | 含义 | 证据 |
|---|---|---|---|
| `python3 scripts/onto1_namespace_collision_check.py --gate` | **2 FAIL ⇒ 阻断发布** | `C-1a PASS` / **`C-1b NOT_EVALUATED`** / **`C-2 FAIL（实测 2 处冲突未修；ADR §5.4「必须先修」）`** / `C-3 PASS（空转已声明）` / `C-4 PASS（4 钉值 + 自引用 + 钉值文件自冻结）` | `evidence/wi_a4_namespace_collision-20260920T142432Z.log` |
| `python3 scripts/onto1_namespace_collision_check.py --selftest` | **0 PASS** | **16 条用例全符合预期**：沙箱全绿对照 `M0`、真实仓 FAIL 对照 `M0b`、变异 `M1~M13`、元变异 `M-元` | `evidence/wi_a4_namespace_collision_selftest-20260920T142432Z.log` |

### 7.3 必须如实声明的事实（不得计为通过）

1. **当前整体是 FAIL，不是"未判定"也不是 PASS**：`C-2` 实测 **2 处**真实前缀冲突（F4/F6）尚未修复 ⇒ 依 `ADR-ONTO1 §5.4`「必须先修」，**发布被阻断**。这同时意味着 D3 解除证据中的"新旧 IRI 碰撞检查脚本绿"**现在不可能取得**。
2. **`C-1b` 是 `NOT_EVALUATED`，不是 PASS**：D3 未签、根域未定 ⇒ 新旧集合交集无从计算。脚本用退出码 `3`（区别于 FAIL=`2`）单独表达"未判定"，并在报告中固定打印"**不得计为通过**"。
3. **登记不等于豁免**：2 处冲突已逐条登记修复义务（Owner + 解除条件），但登记**不会**使 `C-2` 转绿；"全部冲突均已登记"本身也被判 FAIL（`C-2_ALL_CONFLICTS_REGISTERED_NOT_EXEMPTED`），防"全豁免假绿"。退役门 `W5` 要求该登记表**清零**。
4. **`C-3` 空转**：全仓 `specs/**/*.ttl` 中 `owl:versionIRI` 计数为 **0**，单版本闭包约束**无实际覆盖面**；脚本显式打印该空转，不计为覆盖（牙齿由变异 `M4` 与元变异 `M-元` 证明）。
5. **`C-4` 新增两道防线**：自引用检测（`C-4_SELF_REFERENCE`，防 GK-KE 式"指纹写进被哈希文件"永不收敛）与**钉值文件自冻结**（`C-4_PIN_FILE_UNFROZEN`，防"改钉值即可通过"）。后者在本轮实现时**首次暴露**：两份钉值文件原先无独立冻结记录，已通过 `EVIDENCE.md §2` 登记其哈希补齐。
6. **映射草案是 DRAFT**：不含任何新 IRI 字面量；`J-1/J-2/J-3` 三项须由人裁定。
7. 本轮**未**执行 `make generate`、**未**改 `generated/`、**未**改 `specs/**`、**未**改任何本体或 A-Box 制品、**未**发布任何 IRI、**未**重钉、**未**退役旧 IRI。

---

## 8. 决议所需的最小填空板（Owner 填；本决策包不预填）

| 字段 | 期望形态 | 谁填 | 状态 |
|---|---|---|---|
| D3-1 根域类别 | 从 §3.1 的 `ROOT-A/B/C/D`（或 Owner 自定类别）**单选** | 语义架构 Owner + 域名 Owner | 待填 |
| D3-2 根域字面量 | 实际根 IRI 前缀（**写入 ADR 签署件，不写入本决策包**） | 域名 Owner | 待填 |
| D3-3 根域归属/治理 | 注册人 + 续费责任 + 变更审批 | 域名 Owner | 待填 |
| D3-4 解析机制 | `MECH-A` / `MECH-B` / `A+B` | 域名 Owner + 平台 | 待填 |
| D3-5 持久性承诺 | 书面边界（"多久不变 + 变更时的迁移义务"） | 双 Owner | 待填 |
| D3-6 窗口与退役门参数 | 采纳/改判 §6 的 `P-1~P-11` | 公共语义 Owner（待任命） | 待填 |
| D3-7 `J-1` / `J-2` 语义裁定 | 见 §5.3 | TL（`J-1`）/ 公共语义 Owner（`J-2`） | 待填 |
| D3-8 签署件路径 | 填写 `ADR-ONTO1-namespace-neutral-iri-SIGNED.md` 的实际路径（碰撞检查以该文件**存在**为"已签署"判据） | 双 Owner | 待填 |

---

## 9. 非声明

- 本文件**不构成** `DESIGN_APPROVED`、不关闭 `D3`、不关闭 `U-1~U-4`、不构成任何国标符合性表述（D1 文本未到位）。
- 本文件与 `evidence/` 下产物均为**分析证据**，不在 `specs/`、`generated/`、任何本体或 A-Box 制品内，**不得**被引用为权威定义。
- 本文件全部计数（87 / 67 / 32·4·23·7·1·20）均**由脚本从证据重建**，可复现，不依赖人工转录。

---

## 10. 与并行交付的接口对齐（本节为**新增**，因同日出现同名需求规格）

同日另有角色交付了 **《ONTO1 碰撞检查脚本需求规格（C-1~C-4）与变异用例设计 DRAFT》**
（`docs/architecture/ONTO1-碰撞检查脚本需求规格-DRAFT.md`，候任 Integration Contract Owner 起草，
明确「**只出规格，不实现**」并把"脚本原型责任"归 Integration Contract Owner，提案脚本名
`scripts/onto1_iri_collision_check.py`）。本决策包的原型与之**目的相同、载体不同**，故在此显式对齐，
不静默重复、也不静默推翻。

### 10.1 覆盖对照

| 规格要求（§/条目） | 本原型 | 说明 |
|---|---|---|
| §2-A 单一真值函数 | **满足** | `--report` / `--gate` / `--selftest` 共用同一 `check()`；无"报告一套、门禁一套" |
| §2-B fail-closed | **满足** | 登记表缺失、新 IRI 清单缺失、旧端为空、钉值清单缺失、closure 无本体声明 ⇒ 均 FAIL |
| §2-C 变异复验 + 元变异 | **满足** | 16 条用例含 `M-元`（把 `C-3` 判定替换为恒 PASS ⇒ `M4` 必须失去判别力） |
| §2-D 期望值锚定 | **满足** | 旧端 67、迁移域 67、六类关系 32·4·23·7·1·20、C-2 两处真实反例、C-4 四钉值 |
| §3.1 CLI（`--gate`/`--report`/`--selftest`/`--out-dir`） | **部分** | 前三个具备；`--out-dir` 未实现（日志由调用方 `tee` 落盘，路径固定） |
| §3.2 输入 `namespaces.json` | **差异（见 10.2-③）** | 该文件全仓不存在（回源见决策包 §2e 结论 4），原型改以映射草案的根域字段为输入 |
| §3.2 占位值规则 | **满足** | `PLACEHOLDER_ROOT_REJECTED`（`.example`/`.invalid`/`localhost`）+ `D3_SIGNATURE_REQUIRED` |
| §3.3 机读报告 + `evidence` 必为 `文件:行` | **满足** | `--json` 输出完整报告；C-2/C-4 条目带 `文件:行` |
| §4.1 C-1 细则 1（新旧命名空间必须不同） | **满足** | `C-1b` 的 `ns_overlap` 判定（含前缀包含关系） |
| §4.1 C-1 细则 3（LEGACY 不计入 new） | **满足** | new 集合只取"具体 IRI"；`RETIRED:` 行不进 new 集合 |
| §4.1 变异 `M-C1-1/2/3` | **满足** | `M1`（new==old）；"新旧同命名空间"由 `M1` 变体覆盖；**空 new 集合**由 `M13`（⇒ NOT_EVALUATED，**不是 PASS**）覆盖 |
| §4.2 C-2 豁免不得掩盖 + 全豁免 ⇒ FAIL | **满足** | `C-2_ALL_CONFLICTS_REGISTERED_NOT_EXEMPTED`（变异 `M10`） |
| §4.2 扫描范围（TTL/JSON-LD/R2RML/SPARQL） | **部分** | 当前只扫 `specs/**/*.ttl` 的 `@prefix`；JSON-LD/R2RML/SPARQL 前缀未纳入（**待补**） |
| §4.2 显式排除清单 | **未实现** | 当前按 `specs/**/*.ttl` 限定范围（等价于"窄范围"），未做显式排除登记（**待补**） |
| §4.3 closure 入口清单（空 ⇒ FAIL） | **未实现** | 当前用"声明的 owl:Ontology 集合"作闭包锚点；**无显式入口清单登记**（**待补**，见 10.3） |
| §4.4 自引用检测 | **满足** | `C-4_SELF_REFERENCE`（变异 `M11`） |
| §4.4 钉值文件自身冻结 | **满足** | `C-4_PIN_FILE_UNFROZEN`（变异 `M12`）；真实仓两处已由 `EVIDENCE.md §2` 登记 |
| §5 退役门范围固定输出 | **满足** | `refirement_gate_scope` / `not_covered` 固定打印，禁把脚本绿表述为退役门通过 |
| §7 变异矩阵 M-0/M-C1~M-C4/M-元/M-输入 | **满足（映射命名不同）** | 本原型命名 `M0/M0b/M1~M13/M-元`；一一对应关系见 §7.2 与 `--selftest` 输出 |
| §9 门禁接线 | **未接线（有意）** | 未改 `LOOP.yaml.gates` / `EVIDENCE.json.gates`；接线属 TL 决定 |

### 10.2 三处必须由 TL 裁定的接口差异

| # | 差异 | 本原型 | 需求规格 | 建议 |
|---|---|---|---|---|
| ① | **脚本命名** | `scripts/onto1_namespace_collision_check.py` | 提案 `scripts/onto1_iri_collision_check.py`（配套 `*_tests.py`），且 §8 R-6 明言命名待 TL 批准 | 二选一，**避免两个同名职责并存**；若采用规格名，请以规格实现者为准，本原型转为"设计探针"保留在 Loop 证据内（不接线） |
| ② | **退出码语义** | `0` 通过 / `2` FAIL / **`3` 未判定（INCOMPLETE）** | `0` / `1`，且"根域未签 ⇒ 必须 FAIL（无输入即红）" | **本原型已改为默认即 FAIL**（真实仓当前 exit 2，非 3）；`3` 仅在"全部可判定项通过、但根域未填"时出现（变异 `M13` 即为该态）。若 TL 要求完全对齐规格，可把 `3` 合并进 `2`（代价：失去"未判定"与"判定失败"的区分；收益：接口更简）。**两种都不构成通过**，差异只在可读性 |
| ③ | **输入源** | 映射草案 CSV 的"新 IRI"列根域字段 | `namespaces.json` 必填、缺失 ⇒ FAIL | 当前**不得创建** `namespaces.json`（属 D3 决策物，红线）；故本轮以映射草案为输入。D3 签署后应**改读 L4 注册表产物**——建议在 `P-10` 参数落地时一并切换，并保留"缺失 ⇒ FAIL"语义 |

### 10.3 本原型**未实现**、需规格实现者补齐的三项（如实登记）

| # | 缺口 | 为什么本轮不补 |
|---|---|---|
| 1 | **`rdflib` 全量解析**（而非词法解析 `@prefix`） | 词法解析对本轮三份制品已足够且可复现；全量解析属规格实现者责任 |
| 2 | **显式 closure 入口清单**（空 ⇒ FAIL） | 需要"登记入口"这一**新制品**；创建它等于替 L4 注册表设计，超出本决策包范围 |
| 3 | **JSON-LD / R2RML / SPARQL 前缀源** 与 **显式排除清单** | 同上；当前扫描范围已显式限定为 `specs/**/*.ttl`，未声称"全仓覆盖" |

> 本节目的：让 TL 在一次裁定中同时决定**命名、退出码语义、输入源**与**缺口归属**，而不是等两份实现相互覆盖。
