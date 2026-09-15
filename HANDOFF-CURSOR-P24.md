# P24 交接文档 — CodeBuddy → Cursor

> **创建日期**: 2026-08-25  
> **分支**: `feature/P24-dkws-supplychain`  
> **HEAD**: `c0e19da`  
> **工作区**: 干净（仅 `docs/dd/ui/` 未跟踪，非 P24 范围）

---

## 1. 当前状态总览

### 1.1 两个 P24 Loop

| Loop | 状态 | Baton | 说明 |
|------|------|-------|------|
| `P24-dkws-platform` | `ready_for_independent_qa` | `independent_qa` | DKWS 模拟平台（Python），P0-P9 全部 DEV_SELF_CHECK_PASS，待独立 QA 签收 |
| `P24-dkws-supplychain` | 无 Loop 目录 | — | 当前分支名，实际承载的是架构修复 + 供应链前端/后端功能代码 |

### 1.2 架构修复（ARCH-REVIEW-2026-08-23-001）

| 维度 | 状态 |
|------|------|
| GATE 决策 | `BLOCKED` → `CONDITIONAL_LIFT`（待独立 QA 验证） |
| P0 (BLOCKER) | 6/6 CLOSED |
| P1 (MAJOR) | 5 完全 + 2 部分 / 7 |
| P2 (MINOR) | 1/1 CLOSED |
| 开放项 | 14 项，跟踪至 P25/P26 |

### 1.3 供应链功能（分支 feature/P24-dkws-supplychain）

已提交的供应链相关代码（HEAD 之前的提交）：
- **后端**: 供应链图谱端点 + 服务方案端点 + Skill/ServiceProposal/InteractionMemory Port + WritableCustomerRepository
- **前端**: 供应链图谱组件 + 服务方案组件 + 知识访前报告重构
- **合同**: OpenAPI 合同更新（供应链图谱 + 服务方案端点）

---

## 2. 待办事项（按优先级排序）

### 🔴 P0 — 必须立即处理

#### 2.1 P24-dkws-platform 独立 QA 签收

**位置**: `loops/P24-dkws-platform/`  
**当前 Baton**: `independent_qa`  
**操作步骤**:

```bash
# 1. 跑 DKWS 平台测试
cd scenario/dkws-platform
PYTHONPATH=src:tests:scripts python3 -m unittest discover -s tests -v

# 2. 跑证据检查
cd /home/szf/dev/gits-knowledge-engineering
make evidence-check LOOP=P24-dkws-platform

# 3. 通过后签收
cd scenario/dkws-platform
python3 scripts/qa_attest.py --loop P24-dkws-platform --actor independent_qa --session iqa-p24-<timestamp> --decision pass --evidence <log>

# 4. 失败则 reject 并追加 FAILURES.md
python3 scripts/qa_attest.py --loop P24-dkws-platform --actor independent_qa --session iqa-p24-<timestamp> --decision reject --evidence <log>
```

**注意**: 开发角色禁止自签 `QA_PASS`。如果用 Cursor 做此步骤，必须声明角色为 `independent_qa`。

#### 2.2 P24 架构修复独立 QA 验证

**位置**: `docs/governance/P24_INDEPENDENT_QA_HANDOFF.md`  
**验证清单**:

```bash
# P0 验证
git ls-files evidence/ | wc -l  # ≥ 77
cat .github/workflows/ci.yml    # 确认 Maven -am, Node 22, 合同检查
mvn test -Dtest="ProdConfigValidatorTest,ApiKeyAuthenticationFilterTest" -Denforcer.skip=true

# P1 验证
mvn test -Dtest="OpenApiControllerGateTest" -Denforcer.skip=true  # REPORT 模式
mvn test -Dtest="ArchitectureBoundaryTest" -Denforcer.skip=true   # 6/6 PASS (REPORT)
grep -r "DEMO_ONLY" apps/api/src/main/java/  # 命中 ProductMatchingService

# 全量
mvn -pl apps/api -am test -Denforcer.skip=true
cd frontend && npm run build && npx vue-tsc --noEmit
```

---

### 🟡 P1 — 近期需处理

#### 2.3 CI Diagram 生成步骤

**来源**: NEXT_SESSION.md 架构委员会决议  
**问题**: `diagrams/architecture.png` 已删除（旧图含已移除节点），CI 无 diagram 生成步骤  
**操作**: 在 `.github/workflows/ci.yml` 增加 playwright 环境下 `diagrams/gen_arch.py` PNG 生成步骤，或登记独立任务跟踪

#### 2.4 OpenAPI-Controller 漂移清理

**来源**: REM-P1-01  
**当前状态**: 门禁已建立（REPORT 模式），但漂移未清理  
**操作**: 
1. 运行 `OpenApiControllerGateTest` 查看具体漂移项
2. 逐项修复（增量修复策略 B，见 P24_OPEN_DECISIONS.md #1）
3. 漂移清零后切换门禁为 ENFORCE 模式

#### 2.5 ArchUnit 架构边界违规清理

**来源**: REM-P1-04  
**当前状态**: 6 条规则在 REPORT 模式，发现 2 个违规（modules→adapters、adapters→apps）  
**操作**:
1. 运行 `ArchitectureBoundaryTest` 查看违规详情
2. 解除违规依赖（引入 Port 接口解耦）
3. 违规清零后切换为 ENFORCE 模式

---

### 🟢 P2 — 后续规划

#### 2.6 P25 规划

**开放决策**: 见 `docs/governance/P24_OPEN_DECISIONS.md`（14 项）  
**关键项**:
- #1-2: OpenAPI 漂移清理 + ENFORCE 切换
- #3-4: DKWS→P23 集成（推荐方案 C: 投影兼容格式）
- #5-6: JSON Schema 校验 + LLM 输出持久化
- #7: ArchUnit ENFORCE 切换
- #8: pre-commit hook (推荐 gitleaks)
- #12: 许可证策略（需 Owner 决策）

#### 2.7 P26 规划

- DKWS HTTP API 生产化
- 多模型 LLM 支持
- 知识平台选型（RAG/GraphDB/MetadataCatalog，需 Owner 指定）

---

## 3. 关键文件索引

### 3.1 治理文档

| 文件 | 说明 |
|------|------|
| `docs/governance/P24_CHANGE_PACKAGE.md` | 可审计变更包（21+ 提交） |
| `docs/governance/P24_REMEDIATION_EXECUTION_REPORT.md` | 修复执行报告 |
| `docs/governance/P24_FINDINGS_CLOSURE_MATRIX.md` | 闭环矩阵 |
| `docs/governance/P24_ROLLBACK_PLAN.md` | 回滚计划 |
| `docs/governance/P24_OPEN_DECISIONS.md` | 14 项开放决策 |
| `docs/governance/P24_INDEPENDENT_QA_HANDOFF.md` | QA 交接清单 |
| `docs/governance/AUTHORITY_STATUS.md` | 权威状态 SSOT |
| `docs/governance/LICENSE_RISK_ASSESSMENT.md` | 许可证风险评估 |
| `docs/governance/SEC_CLOSURE_REVIEW.md` | 安全闭环审查 |

### 3.2 架构文档

| 文件 | 说明 |
|------|------|
| `docs/architecture/KNOWLEDGE_CONTROL_PLANE_CHAIN.md` | P23→P24 知识控制面连接 |
| `docs/architecture/LLM_GROUNDING_STRATEGY.md` | LLM 接地策略 L0-L4 |
| `diagrams/ARCH-REVIEW-2026-08-23-001.html` | 架构评审交互图 |

### 3.3 关键测试

| 文件 | 说明 |
|------|------|
| `apps/api/src/test/java/com/gien/gits/api/architecture/ArchitectureBoundaryTest.java` | ArchUnit 6 条规则（REPORT 模式） |
| `apps/api/src/test/java/com/gien/gits/api/contract/OpenApiControllerGateTest.java` | OpenAPI-Controller 漂移门禁（REPORT 模式） |

### 3.4 DKWS 平台

| 路径 | 说明 |
|------|------|
| `scenario/dkws-platform/` | Python 工程（src/cli/tests/scripts） |
| `scenario/文件目录型数据知识服务模拟平台_详细需求与详细设计_V1.0.md` | DKWS-SPEC-001 规范 |
| `loops/P24-dkws-platform/` | Loop 管理文件 |

### 3.5 Loop 共享记忆

| 文件 | 说明 |
|------|------|
| `loops/P24-dkws-platform/LOOP.yaml` | Loop 定义（P0-P9 门禁） |
| `loops/P24-dkws-platform/STATE.json` | 当前状态 |
| `loops/P24-dkws-platform/EVIDENCE.json` | 证据板 |
| `loops/P24-dkws-platform/FAILURES.md` | 缺陷记录（9 个 FAIL） |
| `loops/P24-dkws-platform/memory/NEXT_SESSION.md` | 下次会话指引 |

---

## 4. 环境与运行时

### 4.1 后端

```bash
# 全量测试
mvn -pl apps/api -am test -Denforcer.skip=true

# 单测
mvn -pl apps/api -am test -Dtest="ClassName" -Denforcer.skip=true

# 启动（H2 内存库）
mvn -pl apps/api spring-boot:run -Denforcer.skip=true
```

### 4.2 DKWS 平台

```bash
cd scenario/dkws-platform
PYTHONPATH=src:tests:scripts python3 -m unittest discover -s tests -v

# CLI
cd scenario/dkws-platform
PYTHONPATH=src python3 -m dkws --help
# 禁止 --llm real（会调用真实 API 产生费用）
```

### 4.3 前端

```bash
cd frontend
npm run build
npx vue-tsc --noEmit
npm run dev  # 代理 /api → localhost:8080
```

### 4.4 Python 版本

DKWS 平台需要 Python ≥ 3.11，本机有 3.14.3：
```
/home/szf/.workbuddy/binaries/python/versions/3.14.3/bin/python3
```

### 4.5 dependency-check 离线

```bash
MAVEN_OPTS="-Ddependency.check.auto.update=false" mvn ...
```

---

## 5. 项目规则速查

Cursor 操作时需遵守的关键规则：

| 规则 | 要点 |
|------|------|
| **合同 SSOT** | `specs/CONTRACT_INDEX.yaml` 是唯一合同注册，实现不得发明合同未定义的字段 |
| **API First** | 新端点先改 OpenAPI → `make generate` → `make check` → 再写实现 |
| **禁止改 generated/** | 所有生成文件只读，改 specs/ 后 `make generate` |
| **Port/Adapter 分层** | modules 不依赖 adapters/apps，通过 Port 接口解耦 |
| **开发不自签 QA** | `DEV_SELF_CHECK_PASS` 可写，`QA_PASS` 仅独立 QA 可写 |
| **失败先记录** | 测试失败先写 `FAILURES.md`，再修复 |
| **禁止 git add .** | 显式添加文件 |
| **前端四态** | 每个数据组件必须处理 Idle/Loading/Success/Error |
| **前端不发明字段** | 不得添加后端 API 未返回的字段 |

完整规则见 `.codebuddy/rules/` 目录和 `AI_GUIDE.md`。

---

## 6. 未跟踪文件

```
docs/dd/ui/
├── 00_全量界面目录_4K.png
├── 杭州银行岗位智能体UX概念设计与前端需求_V1.1_20260824/
├── 杭州银行岗位智能体UX概念设计与前端需求_V1.1_20260824.zip
└── 杭州银行知识工程与岗位智能体_前端UX与操作需求_V1.1_20260824.md
```

这是 UX 设计文档，非 P24 范围。如需纳入版本控制，请显式 `git add`。

---

## 7. 提交历史（P24 架构修复，最近 10 个）

```
c0e19da docs(architecture): ARCH-REVIEW V2.0 — 独立架构复核报告
cb251ab evidence(p24): P24 证据链 + .gitignore frontend/dist 排除
eea20fd docs(governance): P24 REM-P0-01 — 可审计变更包 + 交付文档
e850d62 docs(governance): P24 REM-P1-05 — 安全闭环审查报告
39301b4 docs(architecture): P24 REM-P1-02/03 — 知识控制面连接 + LLM 接地策略
1452d0a test(architecture): P24 REM-P1-04 — ArchUnit 架构边界机械验证
ae05497 feat(contract): P24 REM-P1-01 — OpenAPI-Controller 双向漂移门禁
f6418e6 fix(evidence): P24 REM-P0-02 — 修复证据链可审计性
ce140d6 fix(governance): P24 REM-P0-03/05/06 + REM-P1-06/07 — CI门禁+权威状态+许可证+产品推荐限定+适配器治理
e1e769c fix(security): P24 REM-P0-04 — 修复生产配置与安全默认值
```
