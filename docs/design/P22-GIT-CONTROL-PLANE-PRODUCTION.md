# P22 增强方向：Git/文件系统控制面生产就绪 + 同类框架调研结论

```text
DOC_ID=P22-GIT-CONTROL-PLANE-PRODUCTION-001
STATUS=DRAFT_FOR_OWNER_REVIEW（A线增强方案 + B线调研结论）
AUTHOR=tech_lead
CREATED_AT=2026-08-19
OWNER_DECISION=放弃引入 OpenWiki；保留"人机共读知识地图/目录/契约"目标；增强 Git 控制面至生产可用
BASELINE=6247048
RELATED=OPENWIKI_CODE_LEVEL_ASSESSMENT.md / ADR-0017 / P22 LOOP
AUTHORITY=docs/dd/银行知识工程规范打样_fixed.xlsx
```

## 0. Owner 决策（已确认）

1. **放弃引入 OpenWiki**（langchain-ai/openwiki 是 Agent 文档生成 CLI，权限/内网CDN/非结构化三大硬伤）。
2. **保留"人机共读知识地图/目录/契约"** 目标设定（当前测试过渡期人操作不急）。
3. **增强基于 Git/文件系统承载权威源 + 控制面（机器读取）的能力，争取生产可用**。
4. **同步深度调研 GitHub 同类理念先进框架**（本文件 §3）。

---

## 1. A 线现状与生产就绪差距

### 1.1 已就绪（P20/P22 已验证）

| 能力 | 载体 | 状态 |
|---|---|---|
| 权威源（SSOT） | `specs/knowledge-architecture/**/*.md|json`（Git 承载） | ✅ |
| 知识地图/资产/合同/路由 | `KnowledgeMap/AssetManifest/ActivationContract/RoutePolicy` 合同 + schema | ✅ qa_pass |
| 知识要素（KE） | `specs/knowledge-architecture/elements/{KI}/KE-*.md`（39 个） | ✅ P22 G1 |
| 规划器（fail-closed） | `DefaultActivationPlanner`（Deny 护栏/planHash 可重放/权限未决拒绝） | ✅ 完整 |
| 文件系统读取 | `Filesystem*Reader`（PathSafety 防护 + fail-closed） | ✅ |
| 合同一致性 | `make generate`/`make check`（哈希校验） | ✅ |

### 1.2 生产就绪差距（需增强）

| # | 差距 | 现状 | 生产要求 | 优先级 |
|---|---|---|---|---|
| GAP-1 | **运行时集成缺失** | `apps/api` 无 knowledge-architecture 依赖/装配；规划器独立模块 | 需通过 Port→Adapter→App 装配进 API 运行时 | **高** |
| GAP-2 | **每请求扫盘（无内存缓存）** | `Filesystem*Reader.listAll()` 每次遍历目录+解析 JSON | 需**启动时加载内存索引 + 运行时高频读内存** | **高** |
| GAP-3 | **权限过滤未到字段级** | 数据含 `classification`，但运行时无按权限过滤读取 | 需按用户/角色/classification 投影过滤（SEC-001/002/003 对齐） | 中-高 |
| GAP-4 | **单向权威流未强制** | 依赖开发纪律，无运行时保障 | 需保证"specs→编译→投影"单向，禁止运行时反向写 | 中 |
| GAP-5 | **人机共读的"人侧"缺失** | 仅 Git 原始文件，业务用户不可浏览/检索/编辑 | 需后续评估（OpenWiki 偏弱；可考虑自建只读投影或更强方案） | 中（过渡期不急） |
| GAP-6 | **真实平台选型留空** | RAG/GraphDB/MetadataCatalog 未定 | 需 Owner 指定后再实现（当前不做） | 低（依赖决策） |

### 1.3 生产目标架构

```
Git 权威源 (specs/knowledge-architecture, SSOT, 低频)
   │  make generate/check（哈希一致）
   ▼
编译/发布产物 (只读快照)
   │  启动时一次性加载
   ▼
运行时内存索引 (KnowledgeMap/Asset/Contract/Route/Element/Planner)
   ▲  高频读取（每次请求）
LLM / Agent 执行（经 ActivationPlanner → KnowledgeWikiPort 渲染）
   │
   ▼
权限投影过滤（按 classification/SEC 护栏）→ 只输出授权内容
```

---

## 2. A 线增强计划（分阶段）

### 阶段 P22-E1：内存索引 + 运行时装配（GAP-1, GAP-2）

| 项 | 动作 |
|---|---|
| 内存索引 | 新增 `InMemoryKnowledgeRepository`（启动时从 filesystem 加载一次，运行时读内存）|
| Port 保持 | `KnowledgeMapPort/AssetCatalogPort/ActivationContractPort/RoutePolicyPort/KnowledgeElementPort` 不变 |
| Adapter 切换 | filesystem adapter 变为"一次性加载器"，运行时走内存实现（`InMemory*Reader`）|
| App 装配 | `apps/api` 加 `knowledge-architecture` + `knowledge-filesystem` 依赖 + `KnowledgeArchitectureConfig`（@Bean）|
| 并发/一致性 | 内存索引不可变（immutable），加载失败 fail-closed（拒绝启动）|

### 阶段 P22-E2：权限投影过滤（GAP-3）

| 项 | 动作 |
|---|---|
| 分类过滤 | 运行时按调用者 `classification` 权限投影，SENSITIVE/RESTRICTED 不泄露给未授权方 |
| 对齐 SEC | 复用 P20 `PermissionDecision` + Deny 护栏 |
| 测试 | 权限投影单元测试（授权/拒绝）|

### 阶段 P22-E3：单向流保障（GAP-4）

| 项 | 动作 |
|---|---|
| 只读强制 | 运行时 Port 全部只读；无任何反向写路径 |
| 防篡改 | 内存索引不可变 + 加载时 schema 校验（fail-closed）|

### 阶段 P22-E4：人机共读"人侧"评估（GAP-5）

- 过渡期不引入重型平台；先做**只读 HTML/Markdown 投影渲染**（KnowledgeWikiPort 已规划），供业务浏览
- 若业务侧提出编辑/审阅需求，再评估自建投影或成熟方案

---

## 3. B 线调研结论：同类理念先进框架

### 3.1 Karpathy LLM Wiki（**理念最契合，核心印证**）

> **三层模型：Raw Sources（不可变证据）/ Markdown Wiki（知识编译层）/ Schema（Agent 维护契约）**

**与我们的架构逐项对应**（惊人一致）：

| Karpathy LLM Wiki | GITS/P22 实现 |
|---|---|
| Raw Sources（不可变证据） | `specs/` 权威源（SSOT） |
| Markdown Wiki（知识编译层） | `specs/knowledge-architecture/elements/` |
| Schema（AGENTS.md 约束） | `knowledge-map/asset-manifest/knowledge-element` 合同 |
| `index.md` + backlinks 双链 | `KnowledgeMap`（ROOT/DOMAIN/TASK 导航）+ assetRefs |
| `log.md` 演化记录 | `ActivationPlan.Trace` + EVIDENCE + planHash |
| Git diff/回滚/最小 diff | Git 版本控制 + `make check` |
| frontmatter（status/confidence/sources） | `source.authority`/`status` + schema |
| **Obsidian 浏览（人侧）** | **缺**（人机共读的"人侧"） |

**关键洞察**：我们的架构**正是 LLM Wiki 理念的银行级实现**，且比 Karpathy 多了 fail-closed 规划器、权限决策、可重放 planHash、受控合同、影子/生产隔离。**这验证了"增强 Git 控制面"的方向有理论依据，无需引入 OpenWiki。**

### 3.2 Graphiti（getzep/graphiti）：时间感知知识图谱（**可借鉴，非替代**）

- 定位：为 AI Agent 构建实时、时间感知的知识图谱（temporal-aware knowledge graph）
- 价值：节点有生物时间戳，支持时间点回溯查询、实体状态演化
- 与我们的差异：我们基于**合同化文件系统 + 确定性计划**；Graphiti 基于**动态图谱 + 时间戳**，两者定位不同
- 借鉴点：**时间感知/版本回溯**能力可强化我们的 `KnowledgeElement` 版本管理（但需评估是否必要）

### 3.3 Graphify（from karpathy llm wiki 启发）

- 定位：将代码/文档转成持久知识图谱（god nodes/community detection）
- 价值：知识结构化 + 图谱查询
- 与我们的关系（**2026-09-13 事实勘误**）：曾以仓库 `graphify-out/`（.gitignore 排除）作为分析工具使用，非运行时组件；**该工具与产物已于 2026-09-13 按 Owner 指示卸载并删除**，现状为"不使用 Graphify"，与本文件 §3.4 / §4 的"不引入"决策方向一致
- 借鉴点：社区检测/概念聚合可辅助知识要素的组织，但非生产运行时

### 3.4 结论：无需替代框架，需补强自身

**没有任何同类框架能直接替代"Git 权威源 + 受控控制面"方案**。最接近的 Karpathy LLM Wiki **印证了我们的架构**（而非推翻）。因此：

- **不引入新框架**（含 OpenWiki、Graphiti、Graphify）
- **增强自身**：按 §2 计划推进 A 线（内存索引/运行时装配/权限过滤/单向流）
- **人侧**：过渡期用只读投影，业务需求明确后再决策

---

## 4. 决策建议

1. **批准 A 线增强计划**（P22-E1 内存索引+运行时装配 → E2 权限过滤 → E3 单向流 → E4 人侧投影评估）
2. **B 线确认**：Karpathy LLM Wiki 印证架构；不引入 Graphiti/Graphify；人侧过渡期只读投影
3. **真实平台（RAG/GraphDB/Metadata）**：仍留空，待 Owner 指定后再推进（不阻塞 A 线）
4. **优先级**：P22-E1（内存索引+运行时装配）是生产可用**最关键的第一步**，建议先做

---

## 5. 变更记录

| 版本 | 时间 | 说明 |
|---|---|---|
| v1 | 2026-08-19 | 初稿：A 线生产就绪差距（GAP-1..6）+ 增强计划（E1-E4）+ B 线调研（Karpathy LLM Wiki/Graphiti/Graphify）|
| v1.1 | 2026-09-13 | **事实勘误（不动决策）**：§3.3 中"已在仓库 `graphify-out/` 作为分析工具使用"已不成立——graphify（uv tool `graphifyy v0.9.38`）与 `graphify-out/` 已按 Owner 指示卸载并删除；§3.4 / §4 "不引入 Graphify" 的决策**不变且已事实上达成** |
