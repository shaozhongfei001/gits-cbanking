# OpenWiki 代码级评估报告（引入集成难度 / 先进性 / 权威规范适用性）

> **⚠️ 2026-08-23 架构审查标注**：本文档中引用的 `adapters/knowledge-filesystem/`（含 `InMemoryKnowledgeStore`、`KnowledgeSnapshotLoader`）已在 P24 DKWS 重构中移除，由 `scenario/dkws-platform/` 模拟平台替代。下文中涉及 `knowledge-filesystem` 的代码路径和类名仅作历史参考。Owner 已决策放弃引入 OpenWiki（参见 OPENWIKI_PROJECTION_ASSESSMENT.md），保留人机共读目标，增强 Git 控制面至生产可用。

```text
DOC_ID=OPENWIKI-CODE-LEVEL-ASSESSMENT-001
STATUS=DRAFT_FOR_OWNER_REVIEW（待 Owner 决策，未替代既有 DEFER 决策）
AUTHOR=tech_lead
CREATED_AT=2026-08-19
REVIEWED_ARTIFACT=langchain-ai/openwiki（GitHub, MIT, 15.3k★, npm CLI v0.3.x）
SCOPE=代码级能力核查 / 集成难度 / 先进性 / 对《银行知识工程规范打样_fixed.xlsx》适用性
AUTHORITY=docs/dd/银行知识工程规范打样_fixed.xlsx
RELATED=ADR-0017（OpenWiki 投影边界）/ OPENWIKI_PROJECTION_ASSESSMENT.md（既有 DEFER 决策）
```

> **重要澄清**：本评估基于 `langchain-ai/openwiki`（当前主流开源实现，npm CLI）。此前 `OPENWIKI_PROJECTION_ASSESSMENT.md` 将 OpenWiki 作为抽象"wiki 平台"评估，**未做代码级核查**，其"人机共读平台"假设与 langchain-ai/openwiki 的真实定位（Agent 文档生成 CLI）存在偏差。本文档以真实代码能力为准修正。

---

## 0. 真实定位（代码级澄清）

`langchain-ai/openwiki` 的真实定位是：

> **一个 CLI，为代码库或个人知识库生成并维护 Agent 可读的 Markdown wiki。**
> "Built for agents to read as memory, and it ships an interactive visualizer for humans to explore."

关键事实：
- 技术栈：TypeScript（Node.js），`npm install -g openwiki`，`pnpm` 工作区
- 核心：**Deep Agents 文档智能体**读取源码/知识源 → 合成带链接的 Markdown wiki → 每次变更增量更新
- 双模式：`code`（代码库）/ `personal`（个人知识）
- 输出：**Open Knowledge Format (OKF v0.2)**，带校验的 Mermaid 图
- 12 个模型提供商、OpenAI-compatible 网关
- Connectors：Custom MCP、Notion、Slack、Gmail、X、Web Search、git-repo
- 可视化器：`openwiki visualize`，**本地 loopback（127.0.0.1:4321），不暴露网络**
- 自我更新：GitHub Actions / GitLab CI / Bitbucket Pipelines（自动开 PR）

---

## 1. 代码级引入集成难度评估

### 1.1 集成技术栈差异（银行 Java 环境 vs OpenWiki Node.js）

| 维度 | 本项目（GITS-KNE） | OpenWiki | 集成难度 |
|---|---|---|---|
| 语言/运行时 | Java 21 + Maven + Spring Modulith | **TypeScript + Node.js + pnpm** | **高：需引入第二运行时** |
| 部署 | JVM 应用（api 8080 / worker 8090） | Node CLI / 独立服务 | 中 |
| 构建 | Maven 多模块 | pnpm + TypeScript | 中 |
| 知识源 | `specs/knowledge-architecture/**/*.md|json`（frontmatter） | 扫描 git-repo / MCP | 中 |
| 权限 | 本项目合同级权限（source.authority/governance） | **OpenWiki 无细粒度字段级权限** | **高：权限模型不匹配** |

### 1.2 关键集成障碍（代码级）

**A. 可视化器不满足银行内网要求（硬约束）**
- `openwiki visualize` 只监听 **`127.0.0.1`（loopback）**，文档明确"never exposed on the network"
- 且**页面从公共 CDN 加载**（`client.js`/`client-lib.js`/`graph.json` 相关库走公开 CDN），"an internet connection is required"
- 银行生产内网通常**隔离外网** → 可视化器默认不可用或需改造自托管

**B. 权限模型缺失（红线冲突）**
- OpenWiki 产出的是**全量可读 Markdown**，无字段级/行级权限
- 本项目知识要素带 `source.authority`（AUTHORITATIVE/REFERENCE/DERIVED/SYNTHETIC）和 `governance.classification`（PUBLIC/INTERNAL/SENSITIVE/RESTRICTED）
- **若投影 SENSITIVE/RESTRICTED 要素，OpenWiki 无法按字段过滤** → 需在发布管线前置过滤（本项目侧做）

**C. 单向流维护（与 ADR-0017 一致但需工程）**
- OpenWiki 定位是"**写** wiki"（agent 合成），但 ADR-0017 要求"**单向流**：specs → 编译发布 → 投影，禁止反向"
- 需改造 OpenWiki 为**只读投影**，禁止它反向写权威源 → 需 wrapper/配置约束

**D. 权威源格式适配**
- 本项目知识要素是 `specs/knowledge-architecture/elements/{KI}/KE-*.md`（JSON frontmatter + Markdown body）
- OpenWiki 期望 OKF v0.2（YAML front matter + `type` 字段 + Mermaid）
- 需**映射层**：`knowledge-element.schema.json` ↔ OKF 文档，或让 OpenWiki 直接读 frontmatter（需验证兼容性）

### 1.3 集成难度综合评定

| 项 | 评级 | 说明 |
|---|---|---|
| 技术栈引入 | **中-高** | 新增 Node 运行时，与现有 Java 栈隔离部署 |
| 可视化器 | **高** | 内网 CDN 依赖 + loopback 约束，需改造 |
| 权限隔离 | **高** | 需在投影管线前置按 classification 过滤 |
| 单向流约束 | **中** | 需 wrapper 防反向写 |
| 数据映射 | **中** | KE frontmatter ↔ OKF 适配 |
| **综合** | **中-高** | 非"零成本"，需专门集成 Loop + 管线改造 |

---

## 2. 先进性评估（代码级）

### 2.1 真正先进的地方

| 能力 | 说明 | 对 GITS-KNE 的价值 |
|---|---|---|
| **Agent 自维护文档** | 文档智能体随变更增量更新，`<!-- OPENWIKI:START/END -->` 块只更新自身内容 | 高：知识地图可随 spec 变更自动更新 |
| **OKF v0.2 开放格式** | 输出可移植的标准知识格式，带 `type`/`generated`/`provenance`/`status`/`stale_after` | 高：与我们合同 SSOT 思想契合 |
| **Mermaid 校验** | 图失败自动降级为文本，`--update` 修复 | 中 |
| **12 模型提供商 + OpenAI-compatible** | 多后端、可接内网网关（LiteLLM/Ollama） | 中：我们已有 LlmClient |
| **MCP connectors** | Custom MCP / Notion / Slack 等接入 | 中：但多为 personal 模式 |
| **增量更新 + no-op** | 无变化时零写入，CI 不抖动 | 高 |

### 2.2 先进性局限（代码级）

| 局限 | 说明 |
|---|---|
| **定位是"生成器"非"权威知识平台"** | 它是"写 wiki 的 CLI"，**不是**结构化知识本体/权限运行时；不提供 CRUD API 给业务用户 |
| **人机共读偏弱** | 可视化器是"探索性 node graph"，非强协作编辑平台；编辑仍需改 Markdown 文件 |
| **无细粒度权限** | 非安全/审计级，不满足银行敏感知识字段级控制 |
| **CDN/外网依赖** | 可视化器依赖公网 CDN，内网需自托管改造 |
| **非运行时组件** | 它生成文档，不承载运行时地图查询（运行时仍靠我们的 Port/adapter） |

### 2.3 先进性结论

**OpenWiki 作为"知识文档自动生成器"是先进的**（OKF、增量维护、Agent 驱动），**但作为"人机共读知识平台"是薄弱的**——它更像"让 Agent 读的文档生成器 + 简单可视化器"，**不是**业务用户可编辑协作的成熟 wiki。

**关键洞察**：如果我们的目标是"人机共读 + 结构化知识控制面"，**OpenWiki 解决了"机器读文档"的一半，但"人友好编辑/浏览/权限"仍需我们自己构建或选型更成熟的方案。**

---

## 3. 对《银行知识工程规范》的适用性评估

### 3.1 规范核心要求 vs OpenWiki 能力

| 规范要求（权威 xlsx） | OpenWiki 能力 | 适用性 |
|---|---|---|
| 场景→知识域→KI→KE 层级 | 支持 Markdown 链接 + OKF concept 文档 | **部分**：需用链接表达层级，但 KI/KE 的关系（挂载、kind、source）需额外 schema |
| K-Type-F/R/P/E/M 要素分类 | OKF `type` 字段可承载 | **中**：`kind` 需映射到 OKF type |
| 原子知识要素（不可再分） | OKF concept 可表达 | 中 |
| 大模型优先读图再执行 | **正是 OpenWiki 强项**（AGENTS.md 引导 agent 先读 wiki） | **高**：理念契合 |
| 权限/审计（source.authority, governance.classification） | **无字段级权限** | **低-不满足** |
| 单向权威流（specs 为 SSOT） | 需 wrapper 强制只读投影 | 中（可工程化） |
| 受控可追踪（版本/来源/失效） | OKF 有 `status`/`stale_after`/`sources`/`verified` | **高**：理念契合 |

### 3.2 适用性结论

**OpenWiki 的理念（OKF、Agent 先读文档、增量维护）与规范高度契合，尤其"大模型优先读图"正是它的设计初衷。**

但**关键不适用点**：
1. **权限模型缺失**：规范要求知识要素带 `authority`/`classification`，OpenWiki 无字段级权限 → 银行敏感知识无法安全投影
2. **非结构化本体**：规范的 KI/KE 是结构化合同（schema + 枚举），OpenWiki 输出是 Markdown 文档 → 需映射层保持结构化
3. **运行时控制面分离**：OpenWiki 只做"投影/阅读"，运行时地图查询仍需我们的 Port/adapter（P20/P22）

---

## 4. 综合结论与决策建议

### 4.1 核心判断（修正既有 DEFER 的前提）

既有 DEFER 决策的前提（"Git 具备 OpenWiki 核心能力 → 不需要 OpenWiki"）**不成立**，应修正为：

> **OpenWiki 是"Agent 文档生成器 + 可视化器"，不是权威知识平台。它解决"机器读知识地图"（与 Git 文件系统互补），但"人机共读中的'人友好编辑/浏览/权限'"它并不充分提供。**
> **它不能完全替代 Git 文件系统作为权威源/控制面；它更适合作为"投影/阅读层"（若引入）。**

### 4.2 决策建议

| 方案 | 说明 | 适用 |
|---|---|---|
| **A. 暂不引入 OpenWiki（维持 DEFER）** | Git 文件系统作为权威源 + 运行时内存索引已够机器驱动；人机共读的"人友好层"OpenWiki 提供有限，且内网 CDN/权限障碍高 | 当前 shadow 阶段 |
| **B. 原型验证 OpenWiki 投影（推荐后续）** | 建只读投影 Loop：验证内网 CDN 自托管改造、权限过滤管线、KE↔OKF 映射、单向流 | 转生产前评估 |
| **C. 评估替代的人机共读方案** | OpenWiki 的"人友好编辑"偏弱，可同时评估成熟 wiki（如 BookStack/Outline）或自建投影 | 需明确人机共读的具体形态 |

### 4.3 关键结论

1. **Git 文件系统**：作为权威源 + 控制面，**充分且必要**（P20 已验证）——不可替代，也不该被 OpenWiki 替代。
2. **OpenWiki（langchain-ai）**：是先进的"Agent 文档生成器"，理念契合（大模型先读图），**可作为投影/阅读层候选**，但**权限、内网 CDN、非结构化**三大障碍使其**不能直接满足银行权威规范**，需原型验证 + 管线改造。
3. **人机共读的"人侧"**：OpenWiki 提供有限（探索性图，非协作编辑）。若"人机共读"指业务用户编辑/审阅，需评估是否 OpenWiki 够用，或需更强方案。

---

## 5. 决策路径（供 Owner）

```
若目标 = 机器驱动为主，人浏览为辅：
   → OpenWiki 可作为投影层原型验证（方案 B）
若目标 = 业务用户深度编辑/协作/审阅知识地图：
   → 需评估 OpenWiki 是否够，或选型更强人机共读方案（方案 C）
若目标 = 当前仅机器驱动验证，人操作不急：
   → 维持 DEFER，但保留 ADR-0017 单向流约束（方案 A）
```

---

## 6. 变更记录

| 版本 | 时间 | 说明 |
|---|---|---|
| v1 | 2026-08-19 | 代码级评估：引入集成难度、先进性、权威规范适用性；修正既有 DEFER 前提（OpenWiki 真实定位为 Agent 文档生成 CLI，非权威知识平台） |
