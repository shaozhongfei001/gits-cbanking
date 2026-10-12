# ONTO1｜D4 决策包（L1 八类 A-Box 权威确认 · 授权投影合同 · SIM 载体与退出台账）

| 项 | 值 |
|---|---|
| 包 ID | `W-1/D4-pack` V1.0 |
| 文档性质 | **决策包（DRAFT）**——把「待确认」变成「可勾选、可裁定、可签署」；**本包不替代任何签署** |
| 裁定与签署方 | **数据 Owner**（数据平台归口）；**业务 Owner 会签**；产品身份部分由产品 Owner（D2）并行 |
| 编制角色 | `data-authority-analyst`（TL 派工 P-5；Baton holder = `tech_lead`） |
| 依据 | `docs/dispatch/ONTO1-D4-数据Owner请求函.md`｜设计 `ONTOLOGY-SPLIT-DESIGN-V2.0-REVIEW.md` §3.2/§4.2/§6.1｜`ONTO1-SIM临时模拟权威声明草案.md`｜复审包 `03/05/11`｜夹具 `evidence/cq-fixtures/CQ1.json`、`CQ2.json` |
| 机读底座 | `loops/ONTO1-ontology-split/evidence/d4-l1-authority-candidates.csv`（32 行）｜`d4-pack.json`｜`d4-pack-manifest.json` |
| 门禁 | `wi_a5_d4_pack` / `wi_a5_d4_pack_selftest`（`scripts/onto1_d4_pack.py`） |
| 状态 | `DRAFT_FOR_OWNER_REVIEW`；**当前门禁 `RETURN_TO_HLD`**，Wave 0 及以后未开工 |
| 不生效声明 | **授权投影合同未生效**（无生效日期、无签署人、未登记合同 ID）；**SIM 临时权威声明未生效**（台账无生效项） |

---

## 0. 一句话

**客户 / 法人 / 集团 / 产品身份的正式 A-Box 权威在银行源系统与数据平台；GITS 与 KERT 只持带来源、时点、版本的授权投影——本包把这句原则落成 8 个术语的可勾选候选、1 套最小字段、1 份投影合同草案、3 条 SIM 载体建议与 4 条退出台账项，请数据 Owner 裁定并（如走 SIM 路径）先签声明。**

---

## 1. 逐术语权威确认表（L1 八类）

**读法**：每术语给 2~3 个**权威候选**（`PRIMARY` 首选 / `ALTERNATE` 备选）+ 明确**禁止项**（`EXCLUDED`，红线显式登记）。另有 `CARRIER` 类型表示「**仅存放位置，不是权威**」（仅 `SourceIdentifier` 用到）。「依据」列的 `文件:行` 均可回源（复现命令见 §7）。**勾选后由数据 Owner 填写「最终具名系统」**——本包不预填结论。

### 1.1 `Party` 主体 ｜登记值：A-Box = 银行源系统/数据平台；ID Owner = 源系统

| 候选 | 类型 | 候选（角色 → 具名） | 依据 | 强度 |
|---|---|---|---|---|
| P-1 | PRIMARY | 客户主数据源 → **EDWCRM**（源合同 `SRC-EDWCRM-CUST-BASE-v0.1`） | `specs/data/src-edwcrm-cust-base.v0.1.json:2-12`；`specs/semantic/gits-core.owl.ttl:22-24` | 强 |
| P-2 | ALTERNATE | 行内 CRM 客户信息系统 → **未具名**（知识资产 sourceRef 称「CRM系统」） | `specs/knowledge-architecture/elements/KI-009/KE-009-01.md:2`；`…/KE-009-06.md:2` | 弱 |
| P-3 | ALTERNATE | 数据平台模拟源 → 银行数据与业务模拟平台 | `docs/dd/gk-ke-contract/contracts/C01_系统边界与理论合同.md:10` | 中 |
| P-4 | EXCLUDED | **GITS 运营库**（仅可作投影载体） | `docs/dd/mybatis-integration-spec.md:68` | 禁止 |

> ⚠ **O-D4-1**：`Party` 是跨分型顶层概念（客户/供应商/监管/同业），**类级取值不可执行**。请 Owner 二选一：☐ 落为分型级映射 ☐ 明确本试点仅覆盖客户侧分型。

☐ 确认登记值　☐ 修改（最终具名：________________）

### 1.2 `Organization` 组织

| 候选 | 类型 | 候选 | 依据 | 强度 |
|---|---|---|---|---|
| O-1 | PRIMARY | 客户主数据源（已含机构/区域字段 `BRID`/`REGION`）→ **EDWCRM** | `specs/data/src-edwcrm-cust-base.v0.1.json:20-21`；同上 `:2-12` | 中 |
| O-2 | ALTERNATE | 数据平台组织维（数据产品） | `docs/dd/gk-ke-contract/contracts/C01_系统边界与理论合同.md:22` | 中 |
| O-3 | ALTERNATE | 行内机构/组织登记 → 未具名 | `docs/dd/gk-ke-contract/contracts/C01_系统边界与理论合同.md:9` | 弱 |
| O-4 | EXCLUDED | **GITS 运营库** | `docs/dd/mybatis-integration-spec.md:68` | 禁止 |

> ⚠ 行内机构树（机关/部门/分支机构）来源在本仓**零证据**。请 Owner 明示：☐ 仅指客户侧组织　☐ 需纳入行内机构树（请具名）

☐ 确认登记值　☐ 修改（最终具名：________________）

### 1.3 `LegalEntity` 法人

| 候选 | 类型 | 候选 | 依据 | 强度 |
|---|---|---|---|---|
| LE-1 | PRIMARY | 客户主档中的法人属性（`CERTNO`/`CUSTCODE`）→ **EDWCRM** | `specs/data/src-edwcrm-cust-base.v0.1.json:13-22` | 中 |
| LE-2 | ALTERNATE | 行内对公客户/法人客户登记 → 未具名 | `specs/knowledge-architecture/elements/KI-009/KE-009-01.md:2` | 弱 |
| LE-3 | ALTERNATE | 外部工商登记数据源（采购与授权待定） | `scenario/seed/03_DATA_DICTIONARY.md:5`；`specs/knowledge-architecture/activation/map_spec.json:365-366` | 弱 |
| LE-4 | EXCLUDED | **GITS 运营库 `legal_entity` 表**（旧送审设计口径，已由 B-02 纠正，不得回退） | `docs/review/ARCH-ONTO-2026-001-committee-package/06-主设计文档-V1.2-送审快照.md:208`；`docs/dd/mybatis-integration-spec.md:68` | 禁止 |

> ⚠ LE-1 是**客户主档**，法人身份在其中是客户属性，非独立法人主档。请 Owner 裁定是否足以充当法人权威。LE-3 属采购/授权决定，纳入前不得用于正式身份认定。

☐ 确认登记值　☐ 修改（最终具名：________________）

### 1.4 `CustomerRole` 客户角色 ｜登记值：A-Box = EDWCRM 等源系统（SIM 阶段临时模拟权威 D4）；ID Owner = 源系统（经 `SourceIdentifier`）

| 候选 | 类型 | 候选 | 依据 | 强度 |
|---|---|---|---|---|
| CR-1 | PRIMARY | 客户主数据源 → **EDWCRM.A_ZHCX_CUST_BASE**（`CUSTID`）**三处登记一致** | `specs/data/src-edwcrm-cust-base.v0.1.json:2-14`；`specs/data/customer-source-mapping.r2rml.ttl:4-15`；`specs/semantic/gits-core.owl.ttl:22-24` | 强 |
| CR-2 | ALTERNATE | 数据平台客户维 / 客户 360（数据产品；不得自主并户） | `docs/dd/gk-ke-contract/contracts/C01_系统边界与理论合同.md:22` | 中 |
| CR-3 | EXCLUDED | **GITS 运营库 `customer`** | `docs/dd/mybatis-integration-spec.md:68` | 禁止 |
| CR-4 | EXCLUDED | **KERT workspace**（其 A-Box 仅 L2 知识供给） | `docs/dd/gk-ke-contract/contracts/C01_系统边界与理论合同.md:12`；`docs/review/ARCH-ONTO-2026-001-rereview-package/03-逐术语权威矩阵-22字段.csv:5` | 禁止 |

☐ 确认登记值　☐ 修改（最终具名：________________）

### 1.5 `EnterpriseGroup` 集团 ／ 1.6 `GroupMembership` 集团成员关系

| 候选 | 类型 | 候选 | 依据 | 强度 |
|---|---|---|---|---|
| EG-1 / GM-1 | PRIMARY | 集团登记源系统 → **未具名** | `…/03-逐术语权威矩阵-22字段.csv:6`、`:7`；`specs/semantic/gits-core.owl.ttl:115-117`、`:123-125` | 弱 |
| EG-2 / GM-2 | ALTERNATE | 客户主档中的集团线索 → **EDWCRM** | `specs/semantic/gits-core.owl.ttl:115-117`；`:123-125` | 弱 |
| EG-3 / GM-3 | ALTERNATE | 数据平台集团关系维（数据产品） | `docs/dd/gk-ke-contract/contracts/C01_系统边界与理论合同.md:11` | 中 |
| EG-4 / GM-4 | EXCLUDED | **GITS 运营库**（旧送审设计口径） | `…/06-主设计文档-V1.2-送审快照.md:209`、`:210` | 禁止 |

> ⚠ **O-D4-7**：集团族在本仓**零具名源系统、零源合同、零实例**。D4 必须具名，否则 Wave 3 的投影合同无法设计（不接受留空占位）。基线 `GroupRelationship` 的 `fromEntityId`/`toEntityId`/`ownershipRatio` 均未绑定任何外部源。

☐ 确认登记值　☐ 修改（最终具名：________________）

### 1.7 `ProductOffering` 产品身份 ｜登记值：A-Box = 产品主数据/数据产品（SIM 临时模拟权威 **D2**）；ID Owner = 产品主数据 Owner

| 候选 | 类型 | 候选 | 依据 | 强度 |
|---|---|---|---|---|
| PO-1 | PRIMARY | 产品主数据（产品目录/产品工厂）→ 待 **D2** 产品 Owner 具名 | `docs/architecture/ONTOLOGY-SPLIT-DESIGN-V2.0-REVIEW.md:120` | 中 |
| PO-2 | ALTERNATE | 经批准的数据产品（数据平台发布的产品代码表） | 同上；`docs/dispatch/ONTO1-D2-产品Owner请求函.md:5` | 中 |
| PO-3 | ALTERNATE | SIM 临时载体（D2 路径，非正式权威）→ `products.ttl`（13 个体）+ KERT 产品卡 front matter | `docs/architecture/ONTO1-SIM临时模拟权威声明草案.md:34` | 弱（SIM） |
| PO-4 | EXCLUDED | **KERT 产品卡**当作产品身份正式权威 | `…/ONTOLOGY-SPLIT-DESIGN-V2.0-REVIEW.md:120`；`specs/semantic/gits-core.owl.ttl:127-129` | 禁止 |

> D4 侧对产品身份**只需确认一条否定命题**：☐ 「产品身份 A-Box ≠ KERT 产品卡」。具名与取值分类属 D2。

☐ 确认否定命题　☐ 修改（________________）

### 1.8 `SourceIdentifier` 来源标识 ｜登记值：A-Box = 随各源系统；ID Owner = 源系统

| 候选 | 类型 | 候选 | 依据 | 强度 |
|---|---|---|---|---|
| SI-1 | PRIMARY | 各源系统的原始标识（**值权威**）→ 如 `EDWCRM.CUSTID` | `specs/data/src-edwcrm-cust-base.v0.1.json:14` | 强 |
| SI-2 | ALTERNATE | 受控映射合同（**规则权威**）→ `CTR-MAP-001`（R2RML） | `specs/data/customer-source-mapping.r2rml.ttl:4-15`；`specs/CONTRACT_INDEX.yaml:166` | 强 |
| SI-3 | `CARRIER` | 投影侧载体（**仅存放不裁决**，非权威候选） | `docs/review/ARCH-ONTO-2026-001-rereview-package/05-六列权威与发布依赖表.md:25` | 中（存放） |
| SI-4 | EXCLUDED | **裸字符串标识**（`customerId` 退役模式） | `…/03-逐术语权威矩阵-22字段.csv:88` | 禁止 |

> 三点必须分开登记，不得混为一列：**值权威**在源系统、**规则权威**在受控映射合同、**存放**在投影侧。另见 §6 **O-D4-2**（与 GK-KE `core.ExternalIdentifier` 未对齐）。

☐ 确认登记值　☐ 修改（________________）

---

## 2. `SourceIdentifier` 最小字段设计（6 必填 + 4 可选）

| # | 字段 | 含义 | 必填 | 与既有合同的对齐 | 缺失时的具名子码 |
|---|---|---|---|---|---|
| 1 | `sourceSystem` | 来源系统标识 | ✔ | `CTR-DATA-001` `source-contract.schema.json#system` | `MISSING_SOURCE_SYSTEM` |
| 2 | `objectType` | 对象类型（源侧对象/表） | ✔ | `CTR-DATA-001` `objects[].name` | `MISSING_OBJECT_TYPE` |
| 3 | `originalId` | 原始 ID（源侧主键取值） | ✔ | `CTR-DATA-001` `fields[role=primary_key]` + `mapsToSubject` | `MISSING_ORIGINAL_ID` |
| 4 | `validFrom` / `validTo` | 生效区间（**左闭右开** `[from,to)`） | `validFrom` ✔ | `C01` §3 时间语义；业务日 `Asia/Shanghai` | `MISSING_VALIDITY_WINDOW` |
| 5 | `extractedAt` | 投影提取时点（**UTC 时间戳**） | ✔ | `CTR-DATA-001#effectiveFrom` 同族语义 | `MISSING_EXTRACTED_AT` |
| 6 | `authorizationBasis` | 授权依据（合同 ID / 文书哈希 / 授权编号） | ✔ | `CTR-DATA-001#owner` + 本包 §3 `contract_id` | `MISSING_AUTHORIZATION_BASIS` |
| — | `scheme` / `issuedBy` | 与 GK-KE `core.ExternalIdentifier` 对齐用 | ✘ | `specs/gk-ke/v1/examples/l1-1/positive/SemanticPackage.json:177-194` | — |
| — | `sourceRecordedAt` | 源侧记录时点（若源合同提供） | ✘ | 待源合同扩展 | — |

**标识唯一性**：`sourceSystem + objectType + originalId`；同一实例 **≥1** 条 `SourceIdentifier`（缺失即拒绝）。基线与设计字段口径见 `docs/architecture/ONTO1-L1-八类术语定义稿-DRAFT.md` §2.8（L1 定义稿），本表只补充**可判定规则**。

### 2.1 fail-closed 具名拒绝

- **顶层错误码**：`MISSING_SOURCE_IDENTIFIER`（`fail_closed = true`）
- **语义**：拒**摄取**（write path），不是「返回空集」；查询侧（read path）也**不得**把「无来源」解释为「来源任意」
- **HTTP 语义**：`422`；响应体沿用仓库统一错误结构：`{status, error, message, path, timestamp}`，`message = "<子码>: <字段>"`
- **子码（10）**：`NO_SOURCE_IDENTIFIER`、`MISSING_SOURCE_SYSTEM`、`MISSING_OBJECT_TYPE`、`MISSING_ORIGINAL_ID`、`MISSING_VALIDITY_WINDOW`、`MISSING_EXTRACTED_AT`、`MISSING_AUTHORIZATION_BASIS`、`UNKNOWN_SOURCE_SYSTEM`、`AMBIGUOUS_SOURCE_IDENTIFIER`、`PROJECTION_STALE`

**禁止行为（6 条，任一即视为缺陷）**

1. 静默补默认值（不得填 `UNKNOWN` / `N/A` / `0` / 空串）；
2. 从上下文或相邻字段**推断**来源系统；
3. 以 SIM 前缀缺失推断「非模拟」（OF-02 已推翻该推断，3 反例作废）；
4. 把拒绝降级为告警后继续写入；
5. 查询侧把「无来源」解释为「来源任意」；
6. 用 try-catch 吞掉拒绝并提供降级结果。

> **与 CQ 的关系**：CQ1 负例 = 无 `SourceIdentifier` ⇒ 拒绝（`NO_SOURCE_IDENTIFIER`）；CQ2 负例 = 无有效期 ⇒ `MISSING_VALIDITY_WINDOW`。这两条属**设计层确定语义**，不依赖 D4（详见 §5）。

---

## 3. 授权投影合同草案（7 要素）— **NOT_EFFECTIVE**

> **状态声明（硬约束）**：本合同**未生效**。`effective_from = null`、`signed_by = null`、合同 ID 未分配、未登记 `CONTRACT_INDEX.yaml`、未进入 `generated/`。**本 Loop 无权令其生效**（Wave -1 只读；生效需 D4 签署 + 注册中心登记）。

| # | 要素 | 草案内容 | 依据 |
|---|---|---|---|
| 1 | **来源** | `sourceSystem=EDWCRM`；`sourceObject=EDWCRM.A_ZHCX_CUST_BASE`；`fieldMapping=CTR-MAP-001`（R2RML）；`sourceClassification=SENSITIVE`（承 `CTR-DATA-002`） | `specs/data/src-edwcrm-cust-base.v0.1.json:2-14`；`specs/data/customer-source-mapping.r2rml.ttl:4-15` |
| 2 | **时点** | `extractedAt` 用 UTC 时间戳；业务日按 `Asia/Shanghai`；生效区间 `[validFrom, validTo)` 左闭右开；**freshness 阈值待数据 Owner 给定**（O-D4-5） | `docs/dd/gk-ke-contract/contracts/C01_系统边界与理论合同.md:41` |
| 3 | **版本** | `sourceContractVersion=SRC-EDWCRM-CUST-BASE-v0.1`；`projectionSchemaVersion` 待定；消费方钉版本 IRI **并**校验内容哈希 | `specs/data/src-edwcrm-cust-base.v0.1.json:3`；设计 §6.4 |
| 4 | **授权范围** | 用途=试点期开发与验证（构造受控夹具、跑场景验证）；对象=客户角色/法人/组织/集团/产品身份；字段=授权清单内（逐字段由数据 Owner 圈定）；保留期=待定；**不得再分发、不得用于对外材料、不得作为激活门禁的唯一依据** | `docs/architecture/ONTO1-SIM临时模拟权威声明草案.md:62-68` |
| 5 | **责任人** | 授权方=**数据 Owner**（+业务 Owner 会签）；供给方=源系统 Owner；保管方=GITS 投影侧与 KERT 投影侧（**仅存放不裁决**）；定义方=公共语义 Owner（**待任命**） | `…/05-六列权威与发布依赖表.md:24-29` |
| 6 | **漂移拒绝行为** | 六类漂移一律**具名拒绝并阻断**，不得降级为告警；漂移判定与投影写入同一事务边界 | `docs/dispatch/ONTO1-D4-数据Owner请求函.md:51` |
| 7 | **失效条件** | 任一失效条件触发即**自动失效**（无需另行决议），30 日内完成投影下线/转正式/引用方切换登记 | `docs/architecture/ONTO1-SIM临时模拟权威声明草案.md:42-49` |

**漂移拒绝码（7）**

| 码 | 触发 | 行为 |
|---|---|---|
| `SOURCE_VERSION_DRIFT` | 源合同版本变更未重新签署 | 拒绝写入 + 阻断消费 |
| `SOURCE_FIELD_MISSING` | 被引用字段在源合同修订中消失 | 拒绝写入 + 阻断消费 |
| `SOURCE_AUTHORITY_DOWNGRADED` | `authority` 由 `AUTHORITATIVE` 降为 `REFERENCE`/`DERIVED` | 拒绝写入 + 标记投影失效 |
| `SOURCE_IDENTIFIER_UNKNOWN` | `sourceSystem` 不在受控清单内 | 拒绝写入（**不得当作新源自动接受**） |
| `PROJECTION_STALE` | `extractedAt` 超阈值 | 拒绝消费（读路径也拒绝） |
| `AUTHORIZATION_EXPIRED` | 授权保留期到期 | 拒绝写入 + 拒绝消费 |
| `AUTHORIZATION_REVOKED` | 授权方书面撤回 | 拒绝写入 + 拒绝消费 + 启动下线登记 |

**失效条件（6）**：① 正式源系统接入并可用；② D4/D2 签署生效（转正式合同）；③ 授权方书面撤回；④ 保留期到期未续；⑤ SIM 声明废止；⑥ 源合同 major 变更未重新签署。

**正式登记路径（不在本包执行）**：`specs/` 定义 → `CONTRACT_INDEX.yaml` 登记 → `make generate`；执行方 = Integration Contract Owner（**尚未任命**）。

---

## 4. SIM 临时模拟权威声明：§2.2 三个载体建议填法 + §2.3 退出台账

> 原草案 `docs/architecture/ONTO1-SIM临时模拟权威声明草案.md` **保持原样未改**（已随 D2/D4 请求函发出；改动会造成已发文书漂移）。以下为**建议填法**，请 Owner 圈定后回填草案 §2.2 / §6。

### 4.1 §2.2 三个占位载体的建议值

| 占位 | 建议填法 | 理由 | 必须写明的限定 | 明确排除 |
|---|---|---|---|---|
| `<SIM-PRODUCT-REGISTRY>`（D2 范围） | `specs/knowledge-architecture/instances/product/products.ttl`（13 个产品身份个体）+ KERT 仓 `examples/**/product-cards/PROD-*.md` front matter | 两侧已被 GK17 W3.1 投影打通，改动面最小 | ① 两侧均为 SIM 临时载体、`simulationOnly=true`；② KERT 侧本环境**只读**，维护责任在 KERT 维护方；③ 该 ttl 前缀为**占位根域**，须 Wave 2 同批修复（O-D4-6）；④ 13 个体↔13 卡是当前事实非承诺 | 把 KERT 产品卡登记为产品身份**正式**权威；把该 ttl 写入 `specs/semantic/` 或 `CONTRACT_INDEX.yaml` |
| `<SIM-CUSTOMER-REGISTRY>` | **建议新建隔离载体**：`specs/knowledge-architecture/instances/sim/customer-roles.sim.json`（每行携带完整 `SourceIdentifier` + `simulationOnly=true`） | ① 不与生产权威路径混放；② 可按 `simulationOnly` 被门禁检出；③ 废止只需下线单一路径；④ **不使运营库变相成为事实权威** | 本包**不创建**该路径（创建属 Wave 2+ 且须 `DESIGN_APPROVED`） | **GITS 运营库 `customer` 生产表直用**；KERT workspace；`specs/semantic/` 与 `CONTRACT_INDEX.yaml` 内任何位置 |
| `<SIM-ENTITY-REGISTRY>` | 同客户角色：`specs/knowledge-architecture/instances/sim/entities.sim.json` | 同上四条；集团族在本仓零源合同，隔离载体可先承载可验证的成员关系时间语义 | 同上 | 同上；另：**不得**把 SIM 载体内容反写 T-Box |

**备选路径（供 Owner 比较）**

- 备选 A：`specs/data/` 下新增 SIM 源合同实例（如 `src-sim-customer-v0.1.json`），复用 `CTR-DATA-001` schema —— 但需其 `authority` 枚举支持 `SIM_TEMP`，**属合同变更（合同先行）**，Wave -1 不可做；
- 备选 B（**不推荐**）：复用 GITS 运营库 `customer` 表只读视图 —— 会把运行库的隐式权威固化，需额外隔离、审计与废止流程。

### 4.2 §2.3 四条退出条件的可执行跟踪台账

**台账状态**：`TRACKING_NOT_STARTED`（声明未生效 ⇒ 四条一律 `NOT_TRIGGERED`，**不得预填触发日期或废止结论**）。声明生效后由全局 Tech Lead 启动跟踪；章节位置同草案 §5（`memory/ORCHESTRATOR.md` 风险登记）。

| # | 退出条件 | 触发判据（可机读/可核验） | 检测方式 | 责任人 | 频率 | 当前状态 | 触发日期 | 30 日废止动作 | 完成证据哈希 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 对应正式源系统接入并可用 | `CONTRACT_INDEX.yaml` 出现覆盖客户/法人/集团/产品身份的 `source_contract_instance` 且 `authority=AUTHORITATIVE`；并有可用性确认（连通与权限） | 索引差异比对 + 确认件哈希 | 数据 Owner（客户/法人/集团）+ 产品 Owner（产品身份） | 每 Wave 收工 | `NOT_TRIGGERED` | — | 转正式投影或下线；`simulationOnly` 数据处置登记；引用方切换记录 | — |
| 2 | D4 权威矩阵确认件 / D2 产品身份确认签署生效 | D4 请求函 §7 签署区非空 **且** 03 号矩阵 `A-Box Owner` 列签署版落盘并记哈希 | 签署区非空断言 + 文件 sha256 | 数据 Owner + 业务 Owner（会签） | 每 Wave 收工 | `NOT_TRIGGERED` | — | 同上 | — |
| 3 | `OWNER_ACTIVATED` 激活评审要求 | 设计 §10 状态机进入 `OWNER_ACTIVATED`；`EVIDENCE.json` 出现分域激活记录 | loop EVIDENCE + 激活决议文书哈希 | 分域 Owner（L1/L2/L3/L4） | 状态机跃迁时 | `NOT_TRIGGERED` | — | 同上 | — |
| 4 | 任一方书面撤回 | 产品 Owner / 数据 Owner / 业务 Owner 任一撤回文书落盘 | 文书登记 + 哈希 | 撤回发起方 | 事件驱动 | `NOT_TRIGGERED` | — | 同上，且 24 小时内停止新增 SIM 数据 | — |

---

## 5. CQ1 / CQ2 的 A-Box 依赖说明（D4 未签期间必须保持 `NOT_EVALUATED`）

### 5.1 CQ1「某法人何时、依据哪个源系统成为客户？」

| 维度 | 结论 |
|---|---|
| 当前状态 | **`NOT_EVALUATED`**（不得改） |
| 阻塞源 | ① **D4 未签**；② 责任 Owner「公共语义 Owner」**尚未任命**（`memory/ROLE_BOARD.yaml`：`UNASSIGNED_GAP`） |
| A-Box 依赖 1 | 正例 `SourceIdentifier{EDWCRM, Customer, C001, 2026-01-05}` **已把 EDWCRM 预置为来源** ⇒ D4 未签前该取值只是**候选**，不得作为断言基线（否则构成夹具层的隐式权威认定）→ **O-D4-3** |
| A-Box 依赖 2 | 正例的**可判真结论**依赖 `CustomerRole` 的 A-Box Owner 落定 |
| A-Box 依赖 3 | 5 条 range 改指核验（`gateOfCustomer`/`ofCustomer`/`opportunityOfCustomer`/`profileOfCustomer`/`refersToCustomer`）**一并被阻塞** |
| **不阻塞的部分** | 负例（无 `SourceIdentifier` ⇒ 具名拒绝 `MISSING_SOURCE_IDENTIFIER`）属设计层确定语义，可保持设计基线 |

### 5.2 CQ2「某集团成员关系在指定业务日是否有效，来源是什么？」

| 维度 | 结论 |
|---|---|
| 当前状态 | **`NOT_EVALUATED`** |
| 阻塞源 | ① D4 未签；② 责任 Owner 未任命 |
| A-Box 依赖 1 | 正例来源写作「集团登记系统」⇒ **系统名未具名**，D4 具名后方可成为断言基线（**O-D4-7**） |
| A-Box 依赖 2 | 成员关系有效期断言依赖实例存在；本仓集团族**零源合同、零实例** ⇒ 目标数 0，**不得以「0 目标 0 违规」充当通过**（设计 §6.2） |
| **不阻塞的部分** | 负例（过期关系在查询日不得返回有效）与时间语义（`validFrom`/`validTo` 强制、左闭右开）属设计层确定语义 |

### 5.3 共用纪律

1. D4 未签期间 CQ1/CQ2 及关联 SHACL 场景**一律 `NOT_EVALUATED`**（设计 §6.1 五态模型）；
2. **不得**用 `WAIVED_FOR_DEVELOPMENT` 替代通过依据（豁免永不满足激活退出标准）；
3. `negative` 与 `mutation` 可先保持设计基线；`positive` 的**可判真结论**必须等 D4；
4. `PASS` 只能由**独立 QA** 在执行后记录；开发/分析角色不得自签。

---

## 6. 本包登记的待决项（登记 ≠ 修改，不得静默决定）

| ID | 级别 | 待决项 | 依据 |
|---|---|---|---|
| **O-D4-1** | MAJOR | `Party`/`Organization` 的**类级 A-Box 取值不可执行**，须落为分型级或明确试点仅覆盖客户侧 | `…/03-逐术语权威矩阵-22字段.csv:2-3` |
| **O-D4-2** | MAJOR | `SourceIdentifier` 与 GK-KE L1-1 已登记的 **`core.ExternalIdentifier`**（`scheme`/`value`/`issuedBy`）**未对齐**，两套外部标识模型并存会造成实施期二义 | `specs/gk-ke/v1/examples/l1-1/positive/SemanticPackage.json:177-194` |
| **O-D4-3** | MAJOR | CQ1/CQ2 夹具**已隐式预置来源系统**（EDWCRM / 集团登记系统），未签前不得作断言基线 | `evidence/cq-fixtures/CQ1.json:6`；`CQ2.json:6` |
| **O-D4-4** | MEDIUM | `authorizationBasis` 与 `CTR-DATA-001#owner` 的关系未定义（授权编号 / 文书哈希 / 合同 ID？）⇒ 否码无法客观判定 | `specs/data/src-edwcrm-cust-base.v0.1.json:5`；`specs/data/source-contract.schema.json:12` |
| **O-D4-5** | MEDIUM | 投影 **freshness 阈值**未定 ⇒ `PROJECTION_STALE` 目前为空转 | `docs/dispatch/ONTO1-D4-数据Owner请求函.md:50-51` |
| **O-D4-6** | MEDIUM | SIM 产品身份载体 `products.ttl:1` 前缀为**占位根域**（`bank.example`），与 D3 纪律冲突 | `specs/knowledge-architecture/instances/product/products.ttl:1` |
| **O-D4-7** | MINOR | 集团族在本仓**零具名源系统、零源合同、零实例** ⇒ D4 必须具名 | `…/03-逐术语权威矩阵-22字段.csv:6-7` |

---

## 7. 本包红线自证与复现命令

**红线自证（全部成立）**

- 未把 **GITS 运营库** 或 **KERT workspace** 登记为客户/法人/集团/产品身份的正式权威（已在机读清单中列为 `EXCLUDED`/`PROHIBITED`）；
- **未代签**：全部签署区留空，本包不含任何签署人姓名与日期；
- **授权投影合同未生效**：`effective_from=null`、`signed_by=null`、合同 ID 未分配、未登记注册表、未进入 `generated/`；
- **未把场景标 PASS**：CQ1/CQ2 保持 `NOT_EVALUATED`，本包不含任何 PASS 断言；
- 未修改 `specs/`、`generated/`、`CONTRACT_INDEX.yaml`、封版 `docs/dd/`；未执行 `make generate`；
- 未使用 `git add .`（只显式添加文件）；
- 无任何国标符合性表述（无 `CONFORMANCE` 字样）。

**复现命令**

```bash
# 门禁（本包自检 + 变异复验）
python3 scripts/onto1_d4_pack.py --gate
python3 scripts/onto1_d4_pack.py --selftest

# 关键回源
sed -n '1,14p'  specs/data/src-edwcrm-cust-base.v0.1.json          # EDWCRM 具名源合同 + CUSTID
sed -n '1,15p'  specs/data/customer-source-mapping.r2rml.ttl        # CTR-MAP-001 映射（ADR-0010）
sed -n '207,212p' docs/review/ARCH-ONTO-2026-001-committee-package/06-主设计文档-V1.2-送审快照.md  # 旧口径（须防回退）
sed -n '177,194p' specs/gk-ke/v1/examples/l1-1/positive/SemanticPackage.json                     # core.ExternalIdentifier
sed -n '1,12p'  specs/knowledge-architecture/instances/product/products.ttl                       # SIM 载体占位根域

# 机读清单与包
wc -l loops/ONTO1-ontology-split/evidence/d4-l1-authority-candidates.csv
python3 -c "import json;d=json.load(open('loops/ONTO1-ontology-split/evidence/d4-pack.json'));print(d['pack_status'], d['projection_contract']['status'], d['sim_declaration']['declaration_status'])"
```

---

## 8. 签署区（**留空**；TL / 分析角色不得代签）

| 项 | 内容 |
|---|---|
| L1 八类权威矩阵 | ☐ 全部确认 ☐ 逐项修改（见 §1 各表） |
| 具体源系统清单（含未具名项具名） | |
| `SourceIdentifier` 最小字段设计 | ☐ 批准 ☐ 有条件批准（条件：______） ☐ 不批准 |
| 授权投影合同 | ☐ 批准 ☐ 有条件批准（条件：______） ☐ 不批准 |
| 路径选择 | ☐ 直接签正式权威矩阵确认 ☐ 先签 SIM 临时声明（正式接入后补确认，载体见 §4.1） |
| SIM 载体圈定（三选一/逐条填写） | |
| 数据 Owner 签署 / 日期 | |
| 业务 Owner 会签 / 日期 | |

> 签署前的硬约束：**投影合同不生效**；`CustomerRole` / `GroupMembership` 场景**不得标 `PASS`**；CQ1/CQ2 保持 `NOT_EVALUATED`。

---

## 9. Owner 决议落地状态（2026-09-21 · O-07 / O-08）

> 本节**追加**，不改动上文 §0~§8 与签署区（**签署区仍留空**）。权威文本：`docs/dispatch/ONTO1-Owner决议建议与授权边界-V1.0.md`；落地台账：`loops/ONTO1-ontology-split/memory/OWNER-DECISIONS-2026-09-21-LANDING.md`。

| 本包待办 | 状态 | 依据 |
|---|---|---|
| B-4-a 八类逐项确认 | **Owner 已选 SIM 路线**（不直接签生产正式矩阵） | O-07 |
| B-4-b 集团族具名 | **`SIM-GROUP-REGISTRY`** | O-07 |
| B-4-c `SourceIdentifier` 六必填 + `MISSING_SOURCE_IDENTIFIER` | **批准** | O-07 |
| B-4-d 授权投影合同 | **批准，但保持 `NOT_EFFECTIVE`** | O-07 |
| B-4-e 路径选择 | **"先签 SIM 临时声明"** | O-07 |
| B-4-f SIM 载体圈定 | 客户/主体 = `SIM-CUSTOMER-MASTER`；集团 = `SIM-GROUP-REGISTRY`；产品 = `SIM-PRODUCT-CATALOG` | O-07 |
| B-4-g 投影 freshness 阈值 | **已给**：Party/CustomerRole 24h · Organization/LegalEntity 7d · EnterpriseGroup/GroupMembership 7d · ProductOffering 24h（**相对 `scenarioAsOf`**） | O-07 |
| B-4-h O-D4-2 | **选定"B 过渡 → A 目标"** | O-08 |

**仍未解除（须外部/人类）**：① 生产数据 Owner 对**真实银行源系统**的正式确认（SIM 不可外推）；② 投影合同生效所需 Schema 校验 / 正负夹具 / 来源·时点·版本校验 / **独立 QA**；③ O-08 目标态进入前须开放 **GK-KE 回归窗口**并通过旧消费者兼容测试；④ 映射合同与一致性门禁未落地前，过渡态 **B 不视为可用**。

**消费禁令（立即生效）**：40 处产品关系 = `QUARANTINED_UNRESOLVED` ⇒ 不进 ACTIVE 关系图、不参与推荐/资格/GraphRAG 事实回答；**CQ3 保持 `NOT_EVALUATED`**。
