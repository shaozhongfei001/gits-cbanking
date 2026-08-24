# 真实平台接入评估（RagEmbedding / KnowledgeGraph / MetadataCatalog）

```text
DOC_ID=REAL-PLATFORM-ASSESSMENT-001
STATUS=DRAFT_FOR_OWNER_DECISION（选型待 Owner 指定）
AUTHOR=tech_lead
CREATED_AT=2026-08-19
BASELINE=P22 完成（QA_PASS，HEAD 29e0c78）
RELATED=P21-REAL-PLATFORM-PORTS.md / P22-GIT-CONTROL-PLANE-PRODUCTION.md
AUTHORITY=docs/dd/银行知识工程规范打样_fixed.xlsx
```

> 本文档评估 P21 候选的真实平台 Port（RagEmbeddingPort / KnowledgeGraphPort / MetadataCatalogPort）在 **P22 完成之后**的接入价值与选型状态，供 Owner 决策。**技术选型未定前禁止实现适配器。**

---

## 0. P22 之后的关键变化（评估前提）

P22 完成后，控制面已是 **Git 权威源 + 内存快照**（~~`InMemoryKnowledgeStore`~~ + `KnowledgeWikiPort`），"大模型优先读图"已实现。因此真实平台接入的价值需重新定位：

> ⚠️ **P24 DKWS 重构后**：`InMemoryKnowledgeStore` 已移除，知识供给由 `scenario/dkws-platform/` 模拟平台替代。

| P22 现状 | 对真实平台的影响 |
|---|---|
| 39 个 KE 全量在内存快照 | 小规模知识（39 KE）**无需 RAG/GraphDB**，内存索引足够 |
| `KnowledgeWikiPort.renderMap` 已实现 LLM 读图 | "读图"已解决；真实平台是**增强检索**，非必需 |
| `AssetCatalogPort`（内存实现）已存在 | 与 `MetadataCatalogPort` **职责重叠** |
| P20 shadow 有 `MockRagAdapter` | 真实 RAG 仅当规模/语义检索需求明确才需要 |

**结论**：真实平台接入是"**可扩展的增强层**"，不是 P22 的必需项。价值在**大规模语义检索 / 关系图谱查询**场景，小规模 shadow 阶段用内存索引即可。

---

## 1. 三个候选 Port 评估

### 1.1 `RagEmbeddingPort`（真实 RAG）

| 项 | 内容 |
|---|---|
| 职责 | 资产文本 / 语义查询编码为向量并检索 Top-K |
| 方法 | `embed(String)` / `search(query, topK, filter)` |
| 实现候选 | `MilvusRagAdapter`（生产）；`MockRagAdapter`（shadow 已有） |
| **选型状态** | ❌ **未定**（Milvus 是候选，需 Owner 确认引擎 + 部署形态） |
| **P22 关系** | P22 用内存索引 + KnowledgeWikiPort 已满足"读图"；RAG 仅当语义检索规模大才需要 |
| **价值** | 高（大规模）；低（当前 39 KE 规模） |
| **优先级** | **待 Owner 定选型 + 明确语义检索需求** |

### 1.2 `KnowledgeGraphPort`（GraphDB）

| 项 | 内容 |
|---|---|
| 职责 | 资产 / 实体 / 关系的图查询（本体投影） |
| 方法 | `getEntity(iri)` / `queryNeighbors(iri, relation, depth)` |
| 实现候选 | `Neo4jGraphAdapter`（生产）；shadow 用 filesystem 地图 |
| **选型状态** | ❌ **未定**（Neo4j 是候选；P20 排除的是 OpenSPG，二者需 Owner 定） |
| **P22 关系** | P22 知识地图是**树状/层级**（场景→KD→KI→KE），用文件系统关联即可；GraphDB 用于**多跳关系查询**（如供应链图谱） |
| **价值** | 中-高（关系密集型）；当前层次结构 GraphDB 非必需 |
| **优先级** | **待 Owner 定选型 + 明确图谱查询需求** |

### 1.3 `MetadataCatalogPort`（OpenMetadata）

| 项 | 内容 |
|---|---|
| 职责 | 资产清单 / Schema / 数据血缘目录（元数据投影） |
| 方法 | `listAssets(AssetFilter)` / `getAsset(id)` |
| 实现候选 | `OpenMetadataAdapter`（生产） |
| **选型状态** | ⚠️ **与 `AssetCatalogPort` 职责重叠**——P22 已用内存快照实现资产目录 |
| **P22 关系** | **不新建**：复用 `AssetCatalogPort`（P20 合同 + P22 内存实现）。若需 Schema / 数据血缘，作为 `AssetCatalogPort` **扩展项**单独评估 |
| **价值** | 中（元数据血缘）；但当前资产目录已由 AssetCatalogPort 覆盖 |
| **优先级** | **不复用新建**；Schema/血缘作为独立扩展项 |

---

## 2. 选型决策点（需 Owner 拍板）

| # | 决策点 | 候选 | 建议 |
|---|---|---|---|
| D1 | RAG 引擎选型 | Milvus / Qdrant / pgvector / 其他 | 若引入：选与行内兼容的（如 pgvector 免新运维组件） |
| D2 | 是否需要真实 RAG | 39 KE 内存索引已够，语义检索是否必要 | 明确业务检索需求后再定 |
| D3 | GraphDB 选型 | Neo4j / OpenSPG / 其他 | 若引入：需明确图谱查询场景（供应链/关联关系） |
| D4 | 图谱是否本期需要 | 知识地图为层级结构，GraphDB 非必需 | 明确多跳查询需求 |
| D5 | MetadataCatalog | 复用 `AssetCatalogPort`（不新建） | **建议复用**（已确认） |
| D6 | Schema / 血缘扩展 | 是否扩展 `AssetCatalogPort` | 明确元数据血缘需求 |

---

## 3. 建议路径

### 结论
**P22 当前不引入任何真实平台**。理由：
1. 39 个 KE + 内存索引 + `KnowledgeWikiPort` 已满足"大模型读图执行"（P22 核心目标）
2. 真实平台是**投影/检索增强层**，非权威源，非必需
3. 选型未定，禁止臆测实现

### 触发真实平台接入的条件
```
A. Owner 明确 RAG 选型 + 语义检索需求（如大规模资产 / 跨文档语义查询）
B. Owner 明确图谱选型 + 多跳关系查询需求（如供应链图谱 / 关联风险传导）
C. 元数据 Schema / 血缘需求明确（扩展 AssetCatalogPort）
D. 生产就绪后（production_ready）再评估实际接入
```

### 推荐顺序（若 Owner 授权）
1. 先评估 **RAG**（若业务检索需求明确）——价值最高，选型需 Owner 定
2. **GraphDB** 次之——仅当图谱查询场景明确
3. **MetadataCatalog** 不复用新建——复用 `AssetCatalogPort`，血缘作为扩展项

---

## 4. 边界与红线

- 选型未定前**禁止登记 / 实现**真实平台 Port。
- 真实平台是投影层，权威源永远是 `specs/`（ADR-0017 / ADR-0015）。
- Oracle 写回属 quarantine 资产，需单独授权。
- 生产接入需 Owner 单独批准 + production_ready。

---

## 5. 变更记录

| 版本 | 时间 | 说明 |
|---|---|---|
| v1 | 2026-08-19 | P22 后真实平台接入评估：3 个候选 Port 选型状态、与 P22 现状关系、决策点 D1-D6、建议路径 |
