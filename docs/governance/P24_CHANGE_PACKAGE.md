# P24 可审计变更包

> **编号**：P24-CHANGE-PACKAGE-001
> **创建日期**：2026-08-24
> **创建角色**：Feature Pilot (P24 Architecture Remediation)
> **关联发现**：REM-P0-01 (ARCH-REVIEW-2026-08-23-001)
> **审计基线**：`origin/main@d3142c9`
> **当前 HEAD**：待提交

---

## 1. 变更包概述

P24 变更包包含两个阶段的工作：

| 阶段 | 范围 | 提交数 | 说明 |
|------|------|--------|------|
| Phase 1: DKWS 功能开发 | 供应链图谱 + 服务方案 + 知识访前 | 12 | 功能实现 |
| Phase 2: 架构修复 | ARCH-REVIEW-2026-08-23-001 修复 | 4+ | 安全/治理/合同 |

## 2. 提交清单

### 2.1 Phase 1: DKWS 功能开发

| # | 提交哈希 | 类型 | 范围 | 说明 |
|---|----------|------|------|------|
| 1 | `eacda25` | feat | dkws | 文件目录型数据知识服务模拟平台 |
| 2 | `1307f17` | feat | engagement | 公司供应链图谱生产链 + 知识组装轨迹 |
| 3 | `5e7750d` | chore | dkws | 演示知识要素 + Loop 权威入口入库 |
| 4 | `6c15175` | test | engagement | EngagementJourneyControllerTest 补 mock |
| 5 | `2e1118d` | docs | dkws | P24 PR 描述与自检清单 |
| 6 | `d5b06c1` | contract | arch-review | ARCH-REVIEW-2026-08-23-001 架构委员会决议执行 |
| 7 | `55ffc6c` | chore | arch-cleanup | 架构清理 — 消除已删除组件引用 |
| 8 | `a531cd3` | feat | dkws | DKWS 供应链重构 — 后端代码 |
| 9 | `c2fd2fb` | contract | dkws | OpenAPI 合同更新 — 供应链图谱 + 服务方案 |
| 10 | `0a9ba9a` | feat | dkws | 前端 — 供应链图谱 + 服务方案 + 知识访前报告 |
| 11 | `4110651` | feat | dkws | 持久化层 — WritableCustomerRepository + CustomerMapper |
| 12 | `d866856` | feat | dkws | scenario/execute — Skill/ServiceProposal/InteractionMemory Port |
| 13 | `5647e8a` | chore | loops | P23-P29 Loop 记录入库 |
| 14 | `3b19d05` | chore | dkws | CI + Skill 适配器 + 图表 + 工具 |
| 15 | `de9f3c6` | docs | dkws | DKWS 需求规格与设计文档 |
| 16 | `250a904` | docs | dkws | DKWS 架构评审 + 交接 + 集成设计 |
| 17 | `0e336f3` | docs | dkws | P24 详细设计文档 |

### 2.2 Phase 2: 架构修复 (Architecture Remediation)

| # | 提交哈希 | 类型 | 范围 | 关联发现 | 说明 |
|---|----------|------|------|----------|------|
| 18 | `e1e769c` | fix | security | REM-P0-04 | 修复生产配置与安全默认值 |
| 19 | `ce140d6` | fix | governance | REM-P0-03/05/06, REM-P1-06/07 | CI门禁+权威状态+许可证+产品推荐+适配器治理 |
| 20 | `f6418e6` | fix | evidence | REM-P0-02 | 修复证据链可审计性 |
| 21 | `ae05497` | feat | contract | REM-P1-01 | OpenAPI-Controller 双向漂移门禁 |

### 2.3 Phase 2: 待提交 (本会话新增)

| # | 类型 | 范围 | 关联发现 | 说明 |
|---|------|------|----------|------|
| 22 | docs | architecture | REM-P1-02 | 知识控制面到 P23 主链连接文档 |
| 23 | docs | architecture | REM-P1-03 | LLM 接地策略文档 |
| 24 | test | architecture | REM-P1-04 | ArchUnit 架构边界机械验证 |
| 25 | docs | governance | REM-P1-05 | 安全闭环审查报告 |

## 3. 文件变更统计

### 3.1 按目录分类

| 目录 | 新增 | 修改 | 删除 | 说明 |
|------|------|------|------|------|
| `modules/` | ~15 | ~5 | 0 | Port 接口 + 领域服务 |
| `adapters/` | ~8 | ~3 | 0 | 适配器实现 |
| `apps/api/` | ~20 | ~10 | 0 | Controller + Config + Security + Test |
| `scenario/` | ~30 | ~5 | 0 | DKWS 平台 + 种子数据 |
| `frontend/` | ~10 | ~5 | 0 | 供应链图谱 + 服务方案 |
| `specs/` | ~5 | ~3 | 0 | OpenAPI 合同 |
| `docs/` | ~15 | ~5 | 0 | 架构文档 + 治理文档 |
| `loops/` | ~10 | ~3 | 0 | Loop 记录 |
| `.github/` | 0 | 1 | 0 | CI 工作流重写 |
| `evidence/` | ~77 | 0 | 0 | 受控日志文件 |

### 3.2 关键安全变更

| 文件 | 变更类型 | 安全影响 |
|------|----------|----------|
| `ProdConfigValidator.java` | 修复 | 属性路径对齐，fail-closed |
| `ApiKeyAuthenticationFilter.java` | 修复 | deadline 解析 fail-closed |
| `application-prod.yaml` | 修复 | stacktrace 隐藏 |
| `ci.yml` | 重写 | Maven -am, Node 22, 合同检查 |

## 4. 合同变更

| 合同 | 变更类型 | 向后兼容 | 说明 |
|------|----------|----------|------|
| `gits-kno-api.openapi.json` | 新增端点 | ✅ | 供应链图谱 + 服务方案 |
| `CONTRACT_INDEX.yaml` | 注册 | ✅ | 新增合同注册 |
| `ADAPTER_STATUS.md` | 更新 | N/A | 适配器生命周期定义 |

**无破坏性合同变更**。

## 5. 测试覆盖

| 测试类型 | 新增 | 通过 | 说明 |
|----------|------|------|------|
| 单元测试 | ~15 | ✅ | ArchUnit + Security + Service |
| 集成测试 | ~5 | ✅ | Controller + Contract |
| 合同门禁 | 1 | ✅ | OpenAPI-Controller 双向漂移 |
| 架构验证 | 6 | ✅ | ArchUnit REPORT 模式 |

## 6. 变更记录

| 日期 | 变更 | 角色 |
|------|------|------|
| 2026-08-24 | 初始创建 | Feature Pilot (P24 REM-P0-01) |
