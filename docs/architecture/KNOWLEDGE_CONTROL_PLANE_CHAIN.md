# 知识控制面主链连接文档

> **编号**：KNOWLEDGE-CONTROL-PLANE-CHAIN-001
> **创建日期**：2026-08-24
> **创建角色**：Feature Pilot (P24 Architecture Remediation)
> **关联发现**：REM-P1-02 (ARCH-REVIEW-2026-08-23-001)
> **状态**：ENGINEERING_CANDIDATE

---

## 1. 目的

建立 P23 `SimulatedKnowledgeProvider`（scenario/execute）与 P24 DKWS 平台（scenario/dkws-platform）之间的知识控制面连接关系，明确数据流、依赖方向和升级路径。

## 2. 当前架构

### 2.1 P23 知识供给链

```
scenario/seed/05_knowledge/demo/
├── knowledge-map.yaml          ← 知识地图（KM-CORP-RM-PREVISIT-DEMO）
├── activation-contract.json    ← 激活合同（scope→task→KI 映射）
├── rules.yaml                  ← 规则库（RUL-FRONT-001~005）
├── tasks.yaml                  ← 任务定义（TASK-FRONT-000~005）
└── elements/
    ├── _index.yaml             ← 知识条目索引
    ├── KI-FRONT-001/           ← 知识条目目录
    │   └── *.md                ← 知识元素
    └── ...

        ↓ ScenarioDataProvider.readAsText()

SimulatedKnowledgeProvider (scenario/execute)
    ├── resolveKnowledgeItemIds()  ← 读 activation-contract.json
    ├── readRules()                ← 读 rules.yaml
    ├── appendKnowledgeItem()      ← 读 elements/_index.yaml + KI/*.md
    └── assemble(scope, ctx)       ← 输出 KnowledgeAssemblyResult

        ↓ 返回与生产同构的知识上下文

apps/api (Spring Boot)
    └── 通过 ScenarioDataProvider 接口注入
```

### 2.2 P24 DKWS 知识服务链

```
scenario/dkws-platform/
├── src/dkws/
│   ├── workspace.py      ← 五层工作区管理
│   ├── ingest.py         ← 原始数据接入
│   ├── knowledge.py      ← 知识候选生成
│   ├── publish.py        ← 核心层发布
│   ├── projection.py     ← 投影构建
│   ├── service.py        ← KnowledgeService（query/search/rule）
│   └── http_api.py       ← 可选 HTTP API（FastAPI）
└── tests/

        ↓ CLI 或 HTTP API

KnowledgeService
    ├── query(domain, entity_type)    ← 查询已发布实体
    ├── search(query, domain)         ← 全文检索
    ├── run_rule(rule_id, inputs)     ← 规则执行
    └── build_projection(service_id)  ← 投影构建
```

## 3. 连接关系

### 3.1 数据层连接

| 维度 | P23 (SimulatedKnowledgeProvider) | P24 (DKWS) | 关系 |
|------|----------------------------------|------------|------|
| 数据源 | `scenario/seed/05_knowledge/demo/` 静态文件 | DKWS 五层工作区动态管理 | P24 是 P23 的**升级路径** |
| 读取方式 | `ScenarioDataProvider.readAsText()` 直接读文件 | `KnowledgeService.query/search` 服务化读取 | P24 提供服务化封装 |
| 知识地图 | `knowledge-map.yaml` 静态 YAML | DKWS `03_core/` 发布层 + 投影 | P24 提供版本化发布 |
| 激活合同 | `activation-contract.json` 静态 JSON | DKWS `90_control/contracts/` 契约管理 | P24 提供契约生命周期 |
| 规则 | `rules.yaml` 静态 YAML | DKWS `90_control/rules/` + `run_rule()` | P24 提供规则执行引擎 |

### 3.2 依赖方向

```
modules/knowledge-architecture/  ← 受控 Port 接口（SSOT）
    ↑                               ↑
    │ 实现                          │ 实现
apps/api (InMemory*)           scenario/execute (SimulatedKnowledgeProvider)
                                    ↑
                                    │ 升级路径
                                scenario/dkws-platform (KnowledgeService)
```

**关键约束**：
- P23 和 P24 都**复用** `modules/knowledge-architecture/` 的受控 Port 接口
- P23 是**影子/演示层**实现，使用静态文件
- P24 是**模拟平台**实现，提供服务化知识管理
- 两者不直接依赖，通过 Port 接口解耦

### 3.3 与 P23 主链的集成点

P23 主链的核心链路是：

```
SimulatedKnowledgeProvider.assemble(scope, businessContext)
    → KnowledgeAssemblyResult (knowledgeContext, sources, trace)
```

DKWS 可作为 P23 的**替代数据源**：

1. **方案 A（当前）**：P23 直接读 `scenario/seed/` 静态文件
2. **方案 B（DKWS 集成）**：P23 通过 DKWS HTTP API 读取知识数据
3. **方案 C（DKWS 投影）**：DKWS 构建投影到 `scenario/seed/` 兼容格式，P23 无感知切换

**推荐**：方案 C — DKWS 投影输出与 `scenario/seed/` 兼容格式，P23 的 `ScenarioDataProvider` 无需修改。

## 4. DKWS 投影与 P23 种子数据对齐

### 4.1 投影输出格式

DKWS `ProjectionBuilder` 可将 `03_core/` 发布层投影为：

| 投影类型 | 输出格式 | P23 兼容 |
|----------|----------|----------|
| `json` | Parquet/JSON 实体清单 | 需适配器 |
| `markdown` | Markdown 知识条目 | 直接兼容 `elements/KI-*/` |
| `catalog` | YAML 索引 | 需适配 `_index.yaml` |

### 4.2 对齐差距

| 差距 | 说明 | 优先级 |
|------|------|--------|
| 投影格式适配 | DKWS 投影输出需与 `scenario/seed/05_knowledge/demo/` 目录结构对齐 | P2 |
| 激活合同投影 | DKWS 需支持将 `90_control/contracts/` 投影为 `activation-contract.json` | P2 |
| 知识地图投影 | DKWS 需支持将 `03_core/` 地图投影为 `knowledge-map.yaml` | P2 |
| 规则投影 | DKWS 需支持将 `90_control/rules/` 投影为 `rules.yaml` | P3 |

## 5. 受控合同复用

P23 和 P24 均复用以下受控合同（`contract_scope: reuse_only`）：

| 合同 ID | Port 接口 | P23 使用 | P24 使用 |
|---------|-----------|----------|----------|
| CTR-KELEM-001 | `KnowledgeElementPort` | ✅ 类型引用 | ✅ 类型引用 |
| CTR-KMAP-001 | `KnowledgeMapPort` | ✅ 类型引用 | ✅ 类型引用 |
| CTR-ACTIVATION-001 | `ActivationContractPort` | ✅ 类型引用 | ✅ 类型引用 |

**不新增受控合同**：P23 和 P24 均为 scenario 层实现，不触发 `make generate` / `make check`。

## 6. 开放决策

| 决策 | 选项 | 推荐 | 状态 |
|------|------|------|------|
| DKWS→P23 集成方式 | A:直接读/B:HTTP API/C:投影兼容 | C | OPEN |
| 投影格式适配时机 | P24 当前/P25 专项 | P25 | OPEN |
| DKWS HTTP API 生产化 | 可选/必须 | 可选 | OPEN |

## 7. 变更记录

| 日期 | 变更 | 角色 |
|------|------|------|
| 2026-08-24 | 初始创建 | Feature Pilot (P24 REM-P1-02) |
