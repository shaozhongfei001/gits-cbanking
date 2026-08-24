# GITS × DKWS 服务建议书与持续经营交互记忆集成设计

> 文档编号：ARCH-DESIGN-2026-08-23-001  
> 版本：1.0.0-draft  
> 日期：2026-08-23  
> 作者：GITS 技术架构评审委员会  
> 状态：待 DKWS 端架构师审核  
> 关联：`docs/dd/对公客户服务建议书主体研究_完整交接文档_V1.0_20260820.md`

---

## 目录

1. [业务背景与核心洞察](#1-业务背景与核心洞察)
2. [现状分析](#2-现状分析)
3. [三个关键缺口](#3-三个关键缺口)
4. [调用架构](#4-调用架构)
5. [GITS 后端 Port 接口设计](#5-gits-后端-port-接口设计)
6. [DKWS 端 SKILL 定义](#6-dkws-端-skill-定义)
7. [交互记忆设计](#7-交互记忆设计)
8. [客户经营阶段演进模型](#8-客户经营阶段演进模型)
9. [客户经理操作界面设计](#9-客户经理操作界面设计)
10. [DKWS 端改造清单](#10-dkws-端改造清单)
11. [合同变更清单](#11-合同变更清单)
12. [实施路径](#12-实施路径)
13. [待 DKWS 端确认的决策项](#13-待-dkws-端确认的决策项)

附录文件（独立文档）：
- [A. ContextPackage 与 ServiceResult 详细 Schema](./GITS-DKWS-SERVICE-PROPOSAL-APPENDIX-A.md)
- [B. Port 接口完整 Java 定义](./GITS-DKWS-SERVICE-PROPOSAL-APPENDIX-B.md)
- [C. SP-20/SP-21 Skill 完整 JSON 定义](./GITS-DKWS-SERVICE-PROPOSAL-APPENDIX-C.md)
- [D. 前端界面交互线框描述](./GITS-DKWS-SERVICE-PROPOSAL-APPENDIX-D.md)

---

## 1. 业务背景与核心洞察

### 1.1 两阶段客户经营模型

银行对公客户经理在接手客户时，存在两个截然不同的经营阶段：

```
┌─────────────────────────────────────────────────────────────────┐
│  阶段一：首次接手（陌生客户）                                      │
│  ─────────────────────────────                                   │
│  输入：企业内数据 + 公开行业/产业数据                               │
│  客户经理姿态：专业顾问                                            │
│  核心任务：准备服务方案，了解背景知识                                 │
│  关键约束：对客户了解仅限于企业内数据和公开数据，                     │
│           必须以专业顾问姿态给客户准备服务方案                        │
├─────────────────────────────────────────────────────────────────┤
│  阶段二：持续经营（已有交互历史）                                    │
│  ─────────────────────────────                                   │
│  输入：交互记忆历史 + 阶段一的所有数据                               │
│  客户经理姿态：深度伙伴                                            │
│  核心任务：依靠交互记忆历史不断调整拜访内容、服务内容，最终赢得客户     │
│  关键约束：交互记忆是核心驱动力，每次交互都应积累可复用的结构化洞察     │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 需求来源

| 优先级 | 来源 | 说明 |
|--------|------|------|
| 1 | `docs/dd/对公客户服务建议书主体研究_完整交接文档_V1.0_20260820.md` | 服务建议书完整业务规范 |
| 2 | `docs/dd/改造-客户经理持续经营Skill-v2-当前项目端需求详细设计.md` | 当前项目端需求 |
| 3 | `docs/dd/改造-客户经理持续经营Skill-v2-deepseek-harness端需求详细设计.md` | DeepSeek Harness 端需求 |
| 4 | `specs/knowledge-architecture/` 下的已有合同 | 知识架构合同体系 |

### 1.3 核心业务规则（来自交接文档，必须严格遵循）

#### 1.3.1 五闸门（G0-G5）

| 闸门 | 核心要求 | 未通过时禁止事项 |
|------|----------|------------------|
| G0 证据准备 | 公开信息有来源和日期；事实与假设分列；完成缺口清单 | 不得把假设作为确定事实带入正式建议 |
| G1 客户核验 | 目标、事件、痛点、决策人、期限经确认或标记待确认 | 不得直接进入正式方案承诺 |
| G2 专家设计 | 需求—方案—产品映射完整；主备方案、条件和风险明确 | 不得以客户经理个人判断替代专业评估 |
| G3 内部审批 | 产品、授信、价格、合规、合同、数据使用按权限批准 | 不得对客承诺额度、价格、收益和时效 |
| G4 对客确认 | 客户理解价值、条件、责任和下一步 | 不得将"客户已收到"视为"客户已接受并实施" |
| G5 实施复盘 | 里程碑、KPI、证据、问题和复盘闭环 | 不得把建议书交付视为经营任务完成 |

#### 1.3.2 双版本原则

- **内部版**：包含所有假设、风险红旗、内部判断、待审批事项
- **对客版**：只保留客户可见、经核验或经批准的内容
- 两版必须**分别编号和留痕**，不能直接复制敏感内部判断
- 对客版仅在 G1+G2+G3 完成后生成

#### 1.3.3 事实状态标签

| 标签 | 含义 | 可否写入对客版 |
|------|------|----------------|
| F (Fact) | 经核验的确定事实 | 可以 |
| C (Candidate) | 有来源但未经客户确认 | 不可以 |
| B (Belief) | 客户经理个人判断 | 不可以 |
| H (Hypothesis) | 基于行业/产业数据的假设 | 不可以 |
| P (Pending) | 待审批事项 | 不可以 |
| A (Approved) | 已批准事项 | 可以 |

#### 1.3.4 AI 辅助边界

> AI辅助识别和写作，不继承授信审批、价格审批、合规判断、合同承诺或客户最终决策责任。

- GITS/DKWS 只能**生成草稿**，不能自动审批
- 闸门推进必须**人工确认**
- 对客版发布必须**经过审批链**
- AI 不能做出任何**承诺性表述**

---

## 2. 现状分析

### 2.1 GITS 已覆盖的能力

| 能力 | 合同/实现 | 说明 |
|------|-----------|------|
| 访前准备 | `AC-PREVISIT-001` + `KM-CORP-RM-PREVISIT` | R1 报告 + R2 速战卡 |
| 预约话术 | `engagementApi.generateOutreachScript` | 四渠道话术 |
| 会面脚本 | `engagementApi.generateMeetingScript` | 议程 + KYC 问题 |
| 访后复盘 | `engagementApi.executePostvisit` | R4 分析 + R5 报告 + 事实对账 |
| 迭代决策 | `engagementApi.handleNewEvidence` | 新证据→R7 更新→R8 下轮访前 |
| CRM 回写 | `CrmWritebackChannel` | 受控写回 |
| 事实对账 | `ClaimReconciliationPort` + DMN | 决策表驱动 |
| 供应链图谱 | `engagementApi.executeSupplyChainGraph` | 上下游关系 |
| 迭代环 | 前端 `EngagementWorkspace.vue` | PREVISIT→INTERACTION→POSTVISIT→ITERATE |

### 2.2 GITS 未覆盖的缺口

| 缺口 | 影响 | 优先级 |
|------|------|--------|
| **服务建议书生成** | 无法生成 8 大章节 + 5 张配套表 | P0 |
| **交互记忆结构化积累与检索** | 只有原话记录，无法驱动后续决策 | P0 |
| **客户经营阶段演进** | routeMode 静态，不随阶段变化 | P1 |
| **双版本管理** | 无内部版/对客版分离 | P1 |
| **闸门状态机** | 无 G0-G5 顺序推进和跳门禁止 | P1 |
| **建议书版本化** | 无历史版本管理和 diff | P2 |

### 2.3 GITS 前端现有界面

当前 `EngagementWorkspace.vue` 布局：

```
持续经营工作台
├── 状态栏（客户名、旅程阶段、迭代轮次、操作按钮）
├── 螺旋迭代流程图（START → [PREVISIT → INTERACTION → POSTVISIT → ITERATE] → COMPLETE）
├── 迭代历史时间线
├── 操作面板（4 卡片：访前准备、访后复盘、迭代决策、完成旅程）
├── 迭代决策面板、预约话术面板、会面脚本面板
├── 访前报告面板（KnowledgePrevisitReport 组件）
├── 访后分析面板
└── 弹窗：客户选择、渠道选择
```

**缺失**：建议书工作区、交互记忆面板、闸门进度条、双版本切换。

### 2.4 DKWS 已有能力

| 能力 | 实现位置 | 说明 |
|------|----------|------|
| 五层工作区 | `src/dkws/workspace.py` | 01_raw→02_work→03_core→04_serve→90_control |
| 契约化 Markdown 读写 | `src/dkws/mdio.py` | frontmatter+正文，原子替换 |
| Schema 校验 | `src/dkws/schemas.py` | RUN_REPORT、STATUS、RELEASE 等 |
| 批次接入 | `src/dkws/ingest.py` | raw→batch 接入流水线 |
| 知识服务 | `src/dkws/service.py` | KnowledgeService + ServiceResult |
| LLM 增强 | `src/dkws/llm.py` | 按激活合同装配知识资产 + LLM 生成 |
| HTTP API | `src/dkws/http_api.py` | FastAPI 端点 |

### 2.5 DKWS 当前缺失的能力

| 缺失 | 说明 |
|------|------|
| SP-20 服务建议书 Skill | "建议书写作"Skill 尚未实现 |
| 行业分析框架资产 | 按行业分类的关键指标、痛点根因、典型产品组合 |
| 财务分析框架资产 | 财务比率、现金流、风险指标框架 |
| 建议书模板资产 | 8 大章节 + 5 张配套表模板 |
| 双版本生成逻辑 | 内部版→规则过滤→对客版 |
| 闸门状态机 | G0→G1→G2→G3→G4→G5 顺序推进 |
| 交互记忆 Schema | 结构化交互记忆定义和存储 |
| 交互记忆抽取 Skill | 从纪要中自动抽取候选记忆 |
| 置信度衰减引擎 | 按时效性计算记忆权重 |

---

## 3. 三个关键缺口

### 3.1 缺口一：服务建议书知识地图

交接文档核心产出——**对公客户服务建议书**，包含 8 大章节：

1. 企业概况与经营现状
2. 行业与竞争分析
3. 财务状况与经营能力分析
4. 风险分析与预警
5. 客户需求识别与优先级排序
6. 服务方案设计（主方案 + 备选方案）
7. 产品推荐与适配
8. 实施路径（30/90/180 天计划）

5 张配套表：客户信息采集表、行业分析表、需求—方案—产品映射表、专家协同单、30/90/180 天实施计划。

当前 `AC-PREVISIT-001` 只覆盖"访前准备"，不覆盖"方案生成"。

### 3.2 缺口二：持续经营交互记忆

| 维度 | interaction-history（已有） | interaction-memory（需新增） |
|------|---------------------------|---------------------------|
| 内容 | 原始对话/纪要文本 | 结构化洞察：偏好、决策模式、关系网络 |
| 粒度 | 一次交互一条 | 一个洞察一条，可跨多次交互聚合 |
| 用途 | 归档、回溯 | 驱动下次访前准备、建议书更新 |
| 生命周期 | 永久保留 | 有时效性（置信度衰减） |
| 检索方式 | 全文搜索 | 按类别/置信度/时效性结构化检索 |

### 3.3 缺口三：客户经营阶段演进

交接文档隐含了客户从"陌生"到"赢得"的阶段演进，但当前合同没有这个维度。`activation-contract` 的 `routeMode` 是静态的。

---

## 4. 调用架构

### 4.1 整体调用流程

```
GITS 前端（客户经理操作界面）
    │
    │  HTTP POST /api/v1/engagement/proposal/generate
    │
    ▼
GITS 后端（apps/api）
    │  ProposalService.generateProposal(...)
    │     │
    │     │  Step 1: 组装 ContextPackage（客户数据+交互历史+证据+交互记忆）
    │     │  Step 2: HTTP POST → DKWS /skills/execute { skill_id: "SP-20", context: ... }
    │     │  Step 3: 接收 ServiceResult（建议书草稿+引用+未知项+闸门建议）
    │     │  Step 4: 返回草稿给前端，等待客户经理人工确认
    │     │  Step 5: 确认后版本化存储，通知 DKWS 02_work/ → 03_core/
    │     ▼
DKWS 平台
    │  KnowledgeService.execute_skill("SP-20", context)
    │     │
    │     │  Step 1: 读取激活合同 AC-SERVICE-PROPOSAL-001
    │     │  Step 2: 按合同装配知识资产（行业框架+财务框架+模板+产品矩阵）
    │     │  Step 3: LLM 逐章生成，标注事实标签（F/C/B/H/P/A）
    │     │  Step 4: 规则校验（CITATION_REQUIRED / DUAL_VERSION / GATE_SEQUENCING）
    │     │  Step 5: 返回 ServiceResult
    │     ▼
DKWS 五层工作区
    01_raw/   ← 客户原始数据
    02_work/  ← 建议书草稿（run_id 隔离，可重跑）
    03_core/  ← 发布版建议书（不可变，版本化）
    04_serve/ ← 对客版投影（脱敏、合规过滤）
    90_control/ ← G0-G5 闸门记录
```

### 4.2 ContextPackage 结构（详见附录 A）

GITS 后端组装、传递给 DKWS 的上下文包，包含：
- `customerId`, `customerName`, `industry`, `engagementPhase`
- `enterpriseData`（基本信息、财务摘要、授信、交易）
- `publicData`（行业报告、新闻事件、监管变化）
- `interactionHistory`（交互纪要列表）
- `interactionMemory`（结构化交互记忆列表）
- `evidence`（已有证据列表，含 factLabel）
- `proposalContext`（建议书类型、已有版本、闸门状态）

### 4.3 ServiceResult 结构（详见附录 A）

DKWS 返回给 GITS 的结果，包含：
- `content.proposalDraft`（建议书正文 Markdown）
- `content.internalVersion`（内部版 + factLabels 映射）
- `content.customerVersion`（对客版，G1+G2+G3 后才有）
- `citations`（引用索引：断言→来源→日期→factLabel）
- `unknowns`（未知项列表）
- `limitations`（限制说明）
- `gateRecommendations`（当前闸门、checklist、下一闸门前置条件）

---

## 5. GITS 后端 Port 接口设计

### 5.1 ProposalPort

```java
public interface ProposalPort {
    ProposalDraft generateDraft(ProposalCommand command);
    List<ProposalVersion> listVersions(String customerId);
    ProposalVersion getVersion(String customerId, String versionId);
    ProposalVersion advanceGate(GateAdvancementCommand command);
    ProposalVersion generateCustomerVersion(String customerId, String versionId);
}
```

### 5.2 InteractionMemoryPort

```java
public interface InteractionMemoryPort {
    List<CandidateMemory> extractCandidates(String interactionId);
    void confirmCandidate(String memoryId, boolean confirmed, String revisedContent);
    List<InteractionMemory> getEffectiveMemories(String customerId);
    List<InteractionMemory> getMemoriesByCategory(String customerId, MemoryCategory category);
}
```

### 5.3 核心枚举

```java
public enum FactLabel { F, C, B, H, P, A }

public enum EngagementPhase {
    PROSPECTING, FIRST_CONTACT, ACTIVE_ENGAGEMENT,
    PROPOSAL_DELIVERED, IMPLEMENTATION, RETENTION
}

public enum MemoryCategory {
    PREFERENCE, DECISION_PATTERN, RELATIONSHIP,
    BUSINESS_SIGNAL, EMOTIONAL_STATE
}

public enum GateState { PENDING, READY_FOR_REVIEW, PASSED, BLOCKED }
```

完整 Java 定义见[附录 B](./GITS-DKWS-SERVICE-PROPOSAL-APPENDIX-B.md)。

---

## 6. DKWS 端 SKILL 定义

### 6.1 SP-20：对公客户服务建议书生成

| 属性 | 值 |
|------|-----|
| skillId | SP-20 |
| name | 对公客户服务建议书生成 |
| implementationType | RULE_MODEL |
| inputs | ContextPackage, proposalType, engagementPhase |
| outputs | ProposalDraft, citationIndex, unknowns, limitations, gateRecommendations |
| assetDependencies | ASSET-KNOW-INDUSTRY-ANALYSIS, ASSET-KNOW-FINANCIAL-ANALYSIS, ASSET-KNOW-PROPOSAL-TEMPLATE, ASSET-KNOW-VISIT-SOP |
| ruleDependencies | CITATION_REQUIRED, NO_UNDISCLOSED_DEGRADATION, DUAL_VERSION_PRINCIPLE, GATE_SEQUENCING |
| humanGatePolicy | REQUIRED |
| sideEffectPolicy | PROPOSE_ONLY |

8 大章节 + 5 张配套表定义见[附录 C](./GITS-DKWS-SERVICE-PROPOSAL-APPENDIX-C.md)。

### 6.2 SP-21：交互记忆抽取

| 属性 | 值 |
|------|-----|
| skillId | SP-21 |
| name | 交互记忆抽取 |
| implementationType | RULE_MODEL |
| inputs | interactionId, interactionContent, existingMemories |
| outputs | candidateMemories, memoryUpdates, memorySupersessions |
| ruleDependencies | CONFIDENCE_CALIBRATION, DECAY_RULE_APPLICATION, DUPLICATE_DETECTION |
| humanGatePolicy | REQUIRED |
| sideEffectPolicy | PROPOSE_ONLY |

---

## 7. 交互记忆设计

### 7.1 什么是交互记忆

从客户交互中抽取的**结构化洞察**，用于驱动后续经营决策。与 interaction-history 的区别：

| 维度 | interaction-history | interaction-memory |
|------|---------------------|---------------------|
| 内容 | 原始对话/纪要 | 结构化洞察 |
| 粒度 | 一次交互一条 | 一个洞察一条 |
| 用途 | 归档 | 驱动决策 |
| 生命周期 | 永久 | 有时效性 |
| 检索 | 全文搜索 | 结构化检索 |

### 7.2 记忆类别

| 类别 | 说明 | 示例 |
|------|------|------|
| PREFERENCE | 客户偏好 | "偏好面对面沟通"、"CFO 是关键决策人" |
| DECISION_PATTERN | 决策模式 | "采购决策需3个月"、"需董事会审批超500万" |
| RELATIONSHIP | 关系网络 | "CFO与CEO是大学同学"、"财务总监是新任" |
| BUSINESS_SIGNAL | 业务信号 | "Q4有采购计划"、"正在考虑海外扩张" |
| EMOTIONAL_STATE | 情感状态 | "对现有银行服务不满意"、"对数字化方案有疑虑" |

### 7.3 记忆生命周期

```
交互纪要
    │
    │  SP-21 抽取
    ▼
CANDIDATE（候选，待人工确认）
    │
    │  客户经理确认/修正
    ▼
CONFIRMED（已确认，可驱动决策）
    │
    │  时间推移 / 新交互否定
    ▼
EXPIRED（已过期）或 SUPERSEDED（已被新记忆取代）
```

### 7.4 置信度衰减

| 衰减规则 | 说明 | 适用场景 |
|----------|------|----------|
| NONE | 不衰减 | 事实性记忆（如决策人身份） |
| LINEAR | 线性衰减 | 业务信号（如采购计划，随时间不确定性增加） |
| STEP | 阶梯衰减 | 情感状态（在关键事件后骤变） |

### 7.5 交互记忆如何驱动建议书更新

```
每次交互（拜访/电话/微信）
    │
    ▼
访后复盘（POSTVISIT）
    │  1. SP-21 从纪要抽取候选记忆
    │  2. 与已有记忆比对：新洞察→CANDIDATE / 强化→置信度↑ / 否定→SUPERSEDED
    │  3. 人工闸门确认
    │
    ▼
下次访前准备（PREVISIT）
    │  1. 检索所有 CONFIRMED 记忆
    │  2. 按时效性和置信度排序
    │  3. 注入 ContextPackage
    │
    ▼
SP-20 生成/更新建议书
    │  1. 读取交互记忆中的偏好和决策模式
    │  2. 调整建议书语气、重点、产品推荐
    │  3. 引用索引标注"基于交互记忆"
    │
    ▼
建议书版本演进
    v1.0（首次）→ v1.1（G1后更新）→ v2.0（G2后重写）
    → v2.1（加入交互记忆洞察）→ v3.0（重大方向调整）
```

---

## 8. 客户经营阶段演进模型

### 8.1 阶段定义

| 阶段 | 说明 | 输入特征 |
|------|------|----------|
| PROSPECTING | 潜客，仅有公开数据 | 无交互历史 |
| FIRST_CONTACT | 首次接触，已准备建议书 | 有建议书草稿 |
| ACTIVE_ENGAGEMENT | 深度经营，有交互记忆 | 有交互记忆积累 |
| PROPOSAL_DELIVERED | 方案已对客确认 | 对客版已发布 |
| IMPLEMENTATION | 实施阶段 | 30/90/180天计划执行中 |
| RETENTION | 存续经营 | 定期复盘 |

### 8.2 阶段与知识地图的映射

| 阶段 | 激活合同 | routeMode | 核心任务 |
|------|----------|-----------|----------|
| PROSPECTING | AC-PREVISIT-001 | ONTOLOGY_THEN_MAP | 行业/产业数据形成经营假设 |
| FIRST_CONTACT | AC-SERVICE-PROPOSAL-001 | ONTOLOGY_THEN_MAP | 生成首次服务建议书 |
| ACTIVE_ENGAGEMENT | AC-ONGOING-ENGAGEMENT-001 | MAP_FIRST | 交互记忆驱动迭代 |
| PROPOSAL_DELIVERED | AC-SERVICE-PROPOSAL-002 | MAP_FIRST | 基于交互记忆更新建议书 |
| IMPLEMENTATION | AC-IMPLEMENTATION-001 | MAP_FIRST | 30/90/180天计划跟踪 |
| RETENTION | AC-ONGOING-ENGAGEMENT-001 | MAP_FIRST | 定期复盘 + 交互记忆更新 |

**关键区别**：首次接触用 `ONTOLOGY_THEN_MAP`（先读本体再读地图），持续经营用 `MAP_FIRST`（直接读已有地图）。因为首次没有交互记忆，需要从本体（行业知识框架）出发；后续有了交互记忆，直接从地图出发效率更高。

### 8.3 阶段转换规则

```
PROSPECTING → FIRST_CONTACT:  建议书草稿生成（G0 通过）
FIRST_CONTACT → ACTIVE_ENGAGEMENT:  首次拜访完成 + G1 通过 + 至少1条交互记忆
ACTIVE_ENGAGEMENT → PROPOSAL_DELIVERED:  G2+G3 通过 + 对客版发布
PROPOSAL_DELIVERED → IMPLEMENTATION:  G4 通过（客户确认）
IMPLEMENTATION → RETENTION:  G5 通过（实施复盘完成）
RETENTION → ACTIVE_ENGAGEMENT:  新需求识别（可循环）
```

---

## 9. 客户经理操作界面设计

### 9.1 推荐方案：建议书作为独立工作区

在现有持续经营工作台中新增"建议书"Tab，与迭代环并列：

```
持续经营工作台
    │
    ├── 迭代环 Tab（现有）
    │    PREVISIT → INTERACTION → POSTVISIT → ITERATE
    │
    └── 建议书 Tab（新增）
         ├── 建议书版本列表
         ├── 当前版本预览（内部版 / 对客版 双版本切换）
         ├── 闸门进度（G0→G1→G2→G3→G4→G5）
         ├── 交互记忆面板
         │    ├── 记忆列表（按类别/置信度排序）
         │    ├── 候选记忆确认（访后自动抽取，人工确认）
         │    └── 记忆详情（来源交互、时效性、衰减曲线）
         └── 操作按钮
              ├── 生成建议书（首次）
              ├── 更新建议书（基于新交互记忆）
              ├── 推进闸门
              └── 导出对客版
```

### 9.2 关键交互设计

#### 9.2.1 建议书生成按钮

- **首次**（PROSPECTING/FIRST_CONTACT）：文案"生成服务建议书"，DKWS 基于行业/产业数据 + 企业内数据生成
- **后续**（ACTIVE_ENGAGEMENT+）：文案"更新服务建议书"，DKWS 基于交互记忆 + 新证据更新

#### 9.2.2 双版本切换

- 内部版：完整信息，含假设、风险红旗、内部判断
- 对客版：脱敏过滤，只保留经核验/经批准的内容
- 交接文档要求"两版必须分别编号和留痕，不能直接复制敏感内部判断"

#### 9.2.3 闸门进度条

```
G0 证据准备 ✅ → G1 客户核验 ✅ → G2 专家设计 ⏳ → G3 内部审批 → G4 对客确认 → G5 实施复盘
```

- 每个闸门有明确的"必须完成"和"禁止事项"
- 闸门推进需人工确认（humanGatePolicy: REQUIRED）
- 跳门禁止（GATE_SEQUENCING 规则）

#### 9.2.4 交互记忆面板

- 访后复盘时自动抽取候选记忆（高亮标注来源）
- 客户经理确认/修正/拒绝
- 确认后的记忆按类别展示
- 每条记忆有置信度指示器和时效性标签

### 9.3 界面与迭代环的联动

```
迭代环 → 建议书 Tab：
  - POSTVISIT 完成后，自动触发 SP-21 抽取候选记忆
  - 候选记忆出现在建议书 Tab 的交互记忆面板

建议书 Tab → 迭代环：
  - 建议书更新后，PREVISIT 的访前准备自动引用最新建议书内容
  - 闸门推进后，迭代环的阶段指示器更新
```

完整界面线框描述见[附录 D](./GITS-DKWS-SERVICE-PROPOSAL-APPENDIX-D.md)。

---

## 10. DKWS 端改造清单

| # | 改造项 | 说明 | 优先级 |
|---|--------|------|--------|
| 1 | **SP-20 Skill 实现** | `src/dkws/skills/proposal_generator.py`：按激活合同装配资产 + LLM 生成建议书 8 大章节 | P0 |
| 2 | **AC-SERVICE-PROPOSAL-001 激活合同** | 定义建议书生成的资产依赖、路由模式、闸门序列 | P0 |
| 3 | **建议书模板资产** | 8 大章节模板 + 5 张配套表模板，存入 `03_core/templates/` | P0 |
| 4 | **行业分析框架资产** | 按行业分类的分析框架，存入 `03_core/knowledge-rules/` | P0 |
| 5 | **财务分析框架资产** | 财务比率、现金流、风险指标框架 | P0 |
| 6 | **HTTP API 扩展** | 新增 `/skills/execute` 端点，GITS 后端通过此端点调用 SKILL | P0 |
| 7 | **双版本生成逻辑** | 内部版完整输出 → 规则过滤（脱敏/合规）→ 对客版 | P1 |
| 8 | **闸门状态机** | G0→G1→G2→G3→G4→G5 顺序推进，跳门禁止 | P1 |
| 9 | **交互记忆 Schema** | `src/dkws/schemas.py` 新增 INTERACTION_MEMORY schema | P1 |
| 10 | **SP-21 交互记忆抽取 Skill** | 从交互纪要中抽取候选记忆 | P2 |
| 11 | **置信度衰减引擎** | 按 decayRule 计算记忆的时效性权重 | P2 |

---

## 11. 合同变更清单

以下合同需注册到 `specs/CONTRACT_INDEX.yaml`：

| 合同ID | 类型 | 说明 | 优先级 |
|--------|------|------|--------|
| SP-20 | Skill | 对公客户服务建议书生成 | P0 |
| SP-21 | Skill | 交互记忆抽取 | P2 |
| AC-SERVICE-PROPOSAL-001 | ActivationContract | 首次建议书生成 | P0 |
| AC-SERVICE-PROPOSAL-002 | ActivationContract | 基于交互记忆的建议书更新 | P1 |
| AC-ONGOING-ENGAGEMENT-001 | ActivationContract | 持续经营交互记忆积累 | P1 |
| AC-IMPLEMENTATION-001 | ActivationContract | 实施阶段计划跟踪 | P2 |
| KM-CORP-RM-SERVICE-PROPOSAL | KnowledgeMap | 服务建议书任务地图 | P0 |
| KM-CORP-RM-ONGOING | KnowledgeMap | 持续经营任务地图 | P1 |
| ASSET-DATA-INTERACTION-MEMORY | Asset | 交互记忆资产定义 | P0 |
| ASSET-KNOW-INDUSTRY-ANALYSIS | Asset | 行业分析框架 | P0 |
| ASSET-KNOW-FINANCIAL-ANALYSIS | Asset | 财务分析框架 | P0 |
| ASSET-KNOW-PROPOSAL-TEMPLATE | Asset | 建议书模板 | P0 |
| CTR-PROPOSAL-001 | Contract | ProposalPort 接口合同 | P0 |
| CTR-INTERACTION-MEMORY-001 | Contract | InteractionMemoryPort 接口合同 | P1 |

---

## 12. 实施路径

```
Phase 1（P24 当前 Loop 可完成）：
  ├── DKWS: SP-20 Skill 骨架 + AC-SERVICE-PROPOSAL-001
  ├── GITS: ProposalPort 接口 + ProposalController
  ├── 前端: 建议书工作区 Tab
  └── 合同: 注册所有新合同到 CONTRACT_INDEX.yaml

Phase 2（P25 Loop）：
  ├── DKWS: 双版本生成 + 闸门状态机
  ├── GITS: InteractionMemoryPort + 访后自动抽取
  ├── 前端: 交互记忆面板
  └── 集成: GITS→DKWS 完整调用链路

Phase 3（P26 Loop）：
  ├── DKWS: 置信度衰减引擎 + SP-21
  ├── GITS: EngagementPhase 阶段演进
  ├── 前端: 阶段指示器 + 动态 routeMode 切换
  └── E2E: 完整客户经营闭环验证
```

---

## 13. 待 DKWS 端确认的决策项

| # | 决策项 | GITS 侧建议 | 需 DKWS 确认 |
|---|--------|-------------|---------------|
| 1 | SP-20 的输入输出契约是否与 DKWS 五层工作区兼容 | ContextPackage 放入 01_raw/，草稿放 02_work/，发布版放 03_core/，对客版放 04_serve/ | 五层映射是否合理？02_work/ 的 run_id 隔离机制是否满足建议书版本管理需求？ |
| 2 | HTTP API 扩展设计 | 新增 `/skills/execute` 端点，接受 skill_id + context，返回 ServiceResult | 端点路径、认证方式、超时策略？是否复用现有 `/generate` 端点？ |
| 3 | 双版本生成逻辑放在 DKWS 还是 GITS | 建议 DKWS 生成内部版 + 对客版，GITS 只做展示和闸门控制 | DKWS 是否愿意承担合规过滤责任？还是 GITS 做过滤？ |
| 4 | 交互记忆的存储位置 | 建议 DKWS 03_core/ 存储（不可变、版本化），GITS 通过 InteractionMemoryPort 调用 | 交互记忆是否适合放在 DKWS？还是 GITS 领域模块自行管理？ |
| 5 | 闸门状态机的实现位置 | 建议 DKWS 90_control/ 记录闸门决策，GITS ProposalPort 做闸门推进控制 | 两边是否需要同步闸门状态？以谁为准？ |
| 6 | 行业分析框架资产的粒度 | 按国民经济行业分类一级（20 类）还是二级（97 类） | 一级太粗，二级太细，建议按银行对公业务常用行业（约 15 类） |
| 7 | LLM 生成建议书的分章策略 | 逐章生成（8 次 LLM 调用）还是一次性生成 | 逐章可控但慢，一次性快但可能超 token 限制 |
| 8 | ContextPackage 的大小限制 | 建议上限 50KB（压缩后），超出需分批 | DKWS LLM 上下文窗口能接受多大输入？ |
