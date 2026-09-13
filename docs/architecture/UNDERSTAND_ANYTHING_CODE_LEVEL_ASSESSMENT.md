# Understand Anything 代码级评估报告（能力 / 相容性 / 引入建议）

```text
DOC_ID=UA-CODE-LEVEL-ASSESSMENT-001
STATUS=DRAFT_FOR_OWNER_REVIEW（待决策；未改变任何合同、Loop 状态、generated 制品）
AUTHOR=tech_lead
CREATED_AT=2026-09-13
REVIEWED_ARTIFACT=Egonex-AI/Understand-Anything（GitHub, MIT, TypeScript）
ARTIFACT_FACTS=82,358★ / 6,923 fork / subscribers 254 / 301 open issues
             =created 2026-03-15 / last push 2026-09-12 / repo size ≈34.6MB
SCOPE=能力核查 · 与本项目权威顺序的相容性 · 集成难度 · 是否值得引入
RELATED=ADR-0017（OpenWiki 投影边界）/ OPENWIKI_CODE_LEVEL_ASSESSMENT.md
       / loops/P22-llm-wiki-knowledge-map（status=qa_pass）
       / docs/architecture/candidates/
EVALUATED_AT_HEAD=5ea981c
```

---

## 0. 一句话结论

**有利有弊，但不是"很大帮助"：它是有价值的"代码理解/上手加速器"，不能作为"治理/证据/权威源"的一环。**

引入它的最大障碍不是技术，而是**权威方向相反**：UA 是 code-first（从代码反推事实），本项目是 contract-first（`specs/` → `generated/` → 实现，低权威不得反向覆盖高权威）。若把 UA 产物当成"项目理解的事实"使用，等于让派生视图凌驾于合同 SSOT 之上。

---

## 1. 真实定位（代码级澄清）

**它不是知识管理平台，也不是文档生成器，而是"代码 → 交互式知识图谱"的 Agent 技能包。**

| 维度 | 事实 |
|---|---|
| 形态 | Claude Code Plugin（技能/skill 形态），16 个平台适配 |
| 核心流水线 | 5 个 agent：`project-scanner` / `file-analyzer` / `architecture-analyzer` / `tour-builder` / `graph-reviewer`，另有 `domain-analyzer`、`article-analyzer` |
| 技术路线 | **Tree-sitter 确定性结构提取（import/export/函数/类/调用点）+ LLM 语义层（摘要、分层、业务域、学习路径）** |
| 图 schema | 16 种节点前缀：`file/func/class/module/concept/config/document/service/table/endpoint/pipeline/schema/resource/domain/flow/step`；5 种边：`imports/calls/belongs_to_layer/part_of_domain/depends_on` |
| 产物 | `.ua/knowledge-graph.json` + 交互式 Dashboard |
| 命令 | `/understand`、`-dashboard`、`-chat`、`-diff`、`-explain`、`-onboard`、`-domain`、`-knowledge` |
| 增量 | 4 档：SKIP / PARTIAL_UPDATE(≤10 文件) / ARCHITECTURE_UPDATE(11–30 或目录变化) / FULL_UPDATE(>30 或 >50%) |
| 去重机制 | `FileFingerprint{contentHash(SHA-256), functions, classes, imports, exports}` + 三档变化级别 NONE/COSMETIC/STRUCTURAL |
| 架构质量 | 值得肯定：`@understand-anything/core` **零 LLM SDK 依赖**（纯数据+算法），LLM 适配在外圈；"能算的交给代码，能判断的才交给 LLM" |
| 数据出域 | 支持 `provider.type=ollama/vllm/lm-studio` 或自定义 HTTP 端点 |
| 只读查看器 | `npx .../understand-anything-viewer.tgz <project>`：**无需 LLM、无需 API Key、从本地磁盘只读、数据不出本机**（Node ≥18） |

### 1.1 平台支持 —— CodeBuddy 不在列表（关键缺口）

16 个平台为：Claude Code / Cursor / VS Code+Copilot / Copilot CLI / Codex / OpenCode / OpenClaw / Antigravity / Gemini CLI / Pi Agent / Vibe CLI / Hermes / Cline / KIMI CLI / Nanobot / Kiro。

**本项目当前使用 CodeBuddy，无原生适配。** 可用姿势只有两条：
1. 走"自然语言技能"手工适配（把它的 SKILL prompt 落到本仓 `.codebuddy/skills/`）；
2. 只消费 `.ua/knowledge-graph.json` 用独立 viewer / 自行解析（推荐，耦合最低）。

---

## 2. 按用途匹配矩阵（这是本报告的核心）

必须把三种用途严格拆开，结论完全不同：

| 用途 | 是否有帮助 | 判断依据 |
|---|---|---|
| **A. 代码理解 / 新人上手 / 影响面分析**<br>（`/understand`、`-explain`、`-diff`、`-onboard`） | ✅ **有帮助**（中等） | 653 个 Java 文件 + 196 个前端 TS/Vue + 六边形分层，确实存在"跨模块理清 Port→Adapter→App 链路"的成本。`-diff` 对 Feature Pilot 评估改动爆炸半径有实际价值 |
| **B. 人机共读知识地图**<br>（`-domain`、`-knowledge`） | ⚠️ **理念契合，只能作投影视图** | `-knowledge` 直接对标 Karpathy 模式 LLM Wiki，与本 Loop `P22-llm-wiki-knowledge-map` 同源思路。但它从**文件与代码**派生语义，不具备 `specs/knowledge-architecture/` 的 `source.authority`（AUTHORITATIVE/REFERENCE/DERIVED/SYNTHETIC）与 `governance.classification` 字段，**不能承载权威知识资产**，只能是 ADR-0017 意义上的投影 |
| **C. 质量门禁 / 证据 / 权威事实** | ❌ **不可用** | 其分层、域归属、摘要全部含 LLM 非确定性判定，无法满足本仓"确定性断言 + 变异复验"（FAIL-2026-09-12 系列、GK16 trust-hardening 已确立）的门禁标准；且与本仓红线"AI 只能产生候选 Claim/Proposal"直接冲突 |

---

## 3. 五个硬约束 / 风险

### R1 权威倒置（最高风险）
- UA 的 layer 划分 = 目录关键词启发式（`service/`、`controller/`、`middleware/`、`util/`）+ LLM 判断，**不认本项目的 `modules/adapters/apps` 六边形与 Port/Adapter 边界**。
- 它会给出"看起来对"的分层；而错误的分层/域归属会**静默污染** Graph RAG 的答案（原文亦承认此点）。
- 一旦有人拿它的回答当"项目事实"，即构成 `AGENTS.md` 第 1 条权威顺序的违反。

### R2 数据出域（银行项目红线）
- 全流程把**文件名、内容、摘要**送入 LLM provider。
- 本仓含 `docs/dd/`（封版受控）、`specs/`、客户/产品相关设计资料。用云 provider 即违规。
- 缓解：本地 `ollama/vllm` 端点 + `.understandignore` 硬排除 `specs/`、`generated/`、`docs/dd/`、`evidence/`、`loops/`。**这是引入的前置条件，不是可选项。**

### R3 首次全量 token 成本
- 本仓实际规模：653 Java、`frontend/src` 196 TS/Vue、`specs` 399、`docs` 361、未生成文件合计约 9,945。
- README 自述大型仓库首扫"可能消耗大量 token"。单次全量成本在本仓量级不可忽略，且**产出物与我们已有的 graphify 高度重复**。

### R4 与存量能力重复（边际收益被压缩）
- 本仓已有 `graphify-out/`（**2026-08-12 生成**，6790 节点 / 13248 边 / 463 社区，含 `GRAPH_REPORT.md` + `index.html`），且 `graphify` 技能已安装在用户级（`~/.codebuddy/skills/graphify/`）。
- 关键事实：该图谱 `.graphify_root=/home/szf/dev/gits-knowledge-engineering`，**该路径已不存在**；图谱生成后至今已产生 **228 个提交**，且已被 `.gitignore:41` 忽略 → **现状是"存量图谱已过期且指向失效根路径"**。
- 对比：`graphify` 输入面更宽（代码/文档/论文/图片/视频）、支持 `--mcp`（Agent 直查图）、`--wiki`、`--obsidian`、`--neo4j`。UA 的差异化仅在"代码语义层 + 业务域抽取 + 增量指纹"。

### R5 维护与漂移
- 301 个 open issue、35MB 仓库、三套 plugin manifest 各自维护、tree-sitter 跨语言版本同步。
- 其设计反复强调 schema `autoFixGraph()` 与回退链 —— 这本身即承认 **LLM 输出漂移是长期问题**。把这种组件放进主链会引入不可控的不确定性。

---

## 4. 明确不建议的做法

1. ❌ 把 UA 产物（`.ua/knowledge-graph.json`）提交入库并当作项目理解基线 —— 它是派生视图，会与合同 SSOT 争夺权威。
2. ❌ 用 UA 的输出写入 `EVIDENCE.md` / Gate 记录 / ADR 结论 —— 违反证据纪律。
3. ❌ 用云 LLM provider 扫描含 `docs/dd/`、`specs/` 的目录 —— 数据出域。
4. ❌ 在 `P22` 或其他已 `qa_pass` 的 Loop 内偷偷替换权威知识源 —— 属"低权威反向覆盖高权威"。
5. ❌ 顺带把 `graphify-out/` 提交进 git（当前正确处于 `.gitignore`）。

---

## 5. 建议路径（按成本从低到高）

### 路径 0（推荐，零新增依赖）：先修既有能力
先重建 `graphify-out`（对齐当前 `5ea981c` 与现存根路径），恢复一个"不过期"的代码/文档图谱，再判断是否还需要 UA。**这一步不需要引入任何新工具，且已装 `--mcp` 可直接供 Agent 查询。**

### 路径 1（低成本试点）：只读旁挂，限定子树 + 本地模型
若仍要验证 UA：
- 范围：单个 bounded 子树（如 `modules/operational-ontology` 或 `scenario/execute`），不做全仓；
- 模型：本地 Ollama/vLLM；
- `.understandignore` 硬排除：`specs/`、`generated/`、`docs/dd/`、`evidence/`、`loops/`、`frontend/node_modules/`；
- 产物：落 gitignored 目录，**只读消费**，消费者用官方 viewer（无 LLM、不出本机）；
- 治理：结论只能记入 `docs/architecture/candidates/`，标注 `DERIVED / NOT_AUTHORITATIVE`。

### 路径 2（仅当目标是"人机共读知识地图"）
UA 的 `-domain` / `-knowledge` 可作为 P22 之后"派生投影视图"的一个候选实现，但必须：
- 走 ADR（新 ADR 或修订 ADR-0017 的投影边界）+ 专用 Loop；
- 权威源仍是 `specs/knowledge-architecture/**`，UA 产物单向派生、不回流；
- 通过本项目权限过滤（`classification`）后才可投影 `SENSITIVE/RESTRICTED` 内容。

---

## 6. 需 Owner 决策项

| ID | 决策 | 建议 |
|---|---|---|
| UA-D1 | 是否引入 UA 作为代码理解工具 | 先走路径 0；UA 暂缓 |
| UA-D2 | 是否允许任何形式的云 LLM 扫描本仓 | 建议明确禁止，仅本地端点 |
| UA-D3 | `graphify-out` 是否重建并纳入日常（仍 gitignore） | 建议重建，成本低收益直接 |
| UA-D4 | UA 是否进入"同类框架调研"清单归档 | 建议归档为"已知候选，未采纳"，避免重复评估 |

---

## 附：本报告未做的事（边界声明）

- 未安装、未执行 UA 的任何脚本（含 `curl | bash` 类安装命令）。
- 未修改 `specs/`、`generated/`、`CONTRACT_INDEX.yaml`、任何 Loop 文件。
- 未做代码级源码审计（网络受限，GitHub 克隆未完成），事实来源为 GitHub REST API 元数据 + 官方 README（jsDelivr 镜像）+ 第三方架构深度拆解文章；文中数据一致性差异（如节点类型 14 vs 16）已在 §1 按可核实的 schema 前缀表述。
- 未记录 `QA_PASS`（本报告为开发/架构侧评估，非独立 QA 结论）。
