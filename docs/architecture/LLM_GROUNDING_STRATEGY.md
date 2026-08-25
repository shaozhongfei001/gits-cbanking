# LLM 接地策略 (Grounding Strategy)

> **编号**：LLM-GROUNDING-STRATEGY-001
> **创建日期**：2026-08-24
> **创建角色**：Feature Pilot (P24 Architecture Remediation)
> **关联发现**：REM-P1-03 (ARCH-REVIEW-2026-08-23-001)
> **状态**：ENGINEERING_CANDIDATE

---

## 1. 目的

显式定义 GITS-KNE 项目中所有 LLM 调用的接地（Grounding）策略，确保 LLM 输出受控、可追溯、不产生未经权威源验证的事实。

## 2. LLM 使用清单

### 2.1 受控 LLM 调用点

| 调用方 | Port | 场景 | 接地方式 | Fallback |
|--------|------|------|----------|----------|
| `KnowledgeWikiService` | `KnowledgeWikiPort` + `LlmClient` | 知识地图渲染为 LLM 可读 Markdown | 受控知识地图 (scenario/seed/) | 空字符串 (fail-closed) |
| `KycInsightService` | `LlmClient` | 语义提取/模式识别 | 原始对话文本 + 规则约束 | 模板匹配 (DMN Fallback) |
| `EngagementOrchestrator` | `LlmClient` | 脚本生成/访前分析 | 知识地图 + 业务上下文 | 模板脚本 |
| `ProductMatchingService` | 规则引擎 (非 LLM) | 产品匹配 | 规则表 (DEMO_ONLY) | N/A |
| `SimulatedKnowledgeProvider` | `ScenarioDataProvider` (非 LLM) | 知识装配 | 静态 YAML/JSON 文件 | N/A |

### 2.2 LLM Client 架构

```
LlmClient (Port 接口, scenario/execute)
├── MockLlmClient     ← 开发/测试环境，关键词匹配返回预定义 JSON
└── RealLlmClient     ← 生产环境，OpenAI 兼容 API 调用
    ├── 重试: 3次，指数退避
    ├── 熔断: 5次失败后开启，30s 半开
    └── 超时: 连接 5s，读取 30s
```

切换配置: `engagement.llm.mode` (mock/real)

## 3. 接地原则

### 3.1 核心原则：LLM 输出 = 候选，非事实

```
受控权威源 (scenario/seed/, specs/, rules.yaml)
    ↓ 注入 systemPrompt
LLM 生成
    ↓ 标记为候选
人工确认 → 权限复核 → 幂等校验 → 回执
    ↓
正式 ControlledAction / Claim
```

**红线**：
- LLM 输出不得直接写入权威事实
- 所有 LLM 生成内容必须标记 `notFact: true`（参见 MockLlmClient 语义提取响应）
- 正式 ControlledAction 必须经过完整人工控制路径

### 3.2 接地层级

| 层级 | 接地源 | 适用场景 | 置信度 |
|------|--------|----------|--------|
| **L0: 无接地** | 无约束自由生成 | ❌ 禁止使用 | 不可信 |
| **L1: Prompt 约束** | systemPrompt 角色定义 | 通用对话辅助 | 低 |
| **L2: 知识注入** | 受控知识地图注入 systemPrompt | 知识驱动访前分析 | 中 |
| **L3: 结构化输出** | JSON Schema 约束 + 知识注入 | 语义提取/脚本生成 | 中高 |
| **L4: 规则验证** | 规则引擎后校验 + 知识注入 | 产品推荐/风险评估 | 高 |

### 3.3 当前项目接地等级映射

| 调用点 | 当前等级 | 目标等级 | 差距 |
|--------|----------|----------|------|
| KnowledgeWikiService | L2 | L2 | ✅ 已达标 |
| KycInsightService 语义提取 | L3 | L3 | ✅ 已达标 |
| EngagementOrchestrator 脚本生成 | L2 | L3 | 需增加 JSON Schema 校验 |
| EngagementOrchestrator 访前分析 | L2 | L2 | ✅ 已达标 |

## 4. 知识注入机制

### 4.1 方案 A：LLM 优先读图（已实现）

```
KnowledgeWikiPort.renderMap(scope)
    → 受控知识地图 Markdown
    → 注入 LlmClient.complete() 的 systemPrompt

KnowledgeWikiPort.renderKnowledgeItem(kiId)
    → 知识条目要素清单 Markdown
    → 注入 systemPrompt 补充上下文
```

**优势**：LLM 在执行任务前先"读图"，输出受知识地图约束
**约束**：渲染内容仅含受控合同定义字段，不发明新字段

### 4.2 知识注入格式

```markdown
# [AUTHORITATIVE] 知识地图: KM-CORP-RM-PREVISIT

## 场景: 访前分析
- 任务: TASK-FRONT-000~005
- 角色: 客户经理

## 知识域: KD-CORP-RM
### 知识条目 KI-FRONT-001: 客户基础信息
- KE-FRONT-001-01: 工商登记信息
- KE-FRONT-001-02: 股权结构
...

## 规则约束
- RUL-FRONT-003: 不得承诺授信额度
- RUL-FRONT-005: 客户表达需语义消歧后再认定事实
```

`[AUTHORITATIVE]` 标签标识内容来自受控权威源，LLM 应优先遵循。

## 5. Fallback 策略

### 5.1 LLM 不可用时的降级路径

```
LlmClient.complete() 失败
    ↓ LlmClientException
调用方 Fallback
    ├── KycInsightService → DMN 规则引擎 (FallbackClaimReconciliationAdapter)
    ├── EngagementOrchestrator → 静态模板脚本
    └── KnowledgeWikiService → 空字符串 (fail-closed)
```

### 5.2 Fallback 原则

1. **Fail-closed**：不确定时返回空/默认值，不编造内容
2. **降级不升级**：Fallback 路径的输出范围 ≤ LLM 路径
3. **可观测**：每次 Fallback 触发记录指标 (`businessMetrics.recordLlmCall`)

## 6. 安全约束

### 6.1 Prompt 注入防护

- `systemPrompt` 由后端代码构造，不直接拼接用户输入
- `userPrompt` 中的用户输入标记为业务数据，不作为指令
- `RealLlmClient` 超时和熔断防止资源耗尽

### 6.2 输出校验

- LLM 输出必须经过 `extractContent()` 提取，不直接使用原始响应
- 结构化输出（JSON）需经 `ObjectMapper` 解析，解析失败走 Fallback
- 禁止将 LLM 原始输出直接持久化到数据库

### 6.3 数据隔离

- API Key 通过环境变量注入，不硬编码
- 生产配置 (`application-prod.yaml`) 不包含 LLM API 密钥明文
- 日志中不输出完整 systemPrompt（可能含敏感业务数据）

## 7. 可观测性

### 7.1 指标

| 指标 | 来源 | 用途 |
|------|------|------|
| `llm.call.count{mode, status}` | `BusinessMetrics` | 调用次数/成功率 |
| `llm.call.latency{mode}` | `BusinessMetrics` | 调用延迟 |
| `circuit.breaker.state` | `RealLlmClient` | 熔断器状态 |

### 7.2 审计

- LLM 调用日志包含: `claimId`, `customerId`, `mode`(mock/real), `status`(success/fallback)
- 知识注入日志包含: `scope`, `kiIds`, 渲染条目数
- 禁止在日志中输出完整 LLM 响应体

## 8. 开放决策

| 决策 | 选项 | 推荐 | 状态 |
|------|------|------|------|
| JSON Schema 校验 | LLM 输出后校验 / Prompt 约束 | 输出后校验 | OPEN |
| 知识注入范围控制 | 全量注入 / 按需注入 | 按需注入 (当前) | DECIDED |
| LLM 输出持久化 | 不持久化 / 审计日志 / 完整存储 | 审计日志 | OPEN |
| 多模型支持 | 单模型 / 路由多模型 | 单模型 (当前) | OPEN |

## 9. 变更记录

| 日期 | 变更 | 角色 |
|------|------|------|
| 2026-08-24 | 初始创建 | Feature Pilot (P24 REM-P1-03) |
