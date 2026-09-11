# GK-KE L0-2 → L6 无人值守长程部署（Tech Lead 总指挥）

> 角色：Tech Lead（planning_review，总指挥）
> 授权：Owner 无人值守（用户指令 2026-09-12："安排无人值守的长程任务…根据依赖并行或串行 loop Engineering 完成每个Loop。中间不要打断"）
> 依据：`docs/dispatch/GK-KE-L0-2-开工规划.md`（Wave A~E）+ C08 §2 实施顺序 + Owner 决议 GK-KE-OWNER-001

## 0. 无人值守授权与红线

按 SDD 06 契约 §4a 阶梯协议（自愈 → 降级 → 回退）自主处理可自行解决的技术/环境问题，**不中断询问用户**。
仅以下 5 类硬阻塞才允许停机：

1. 缺凭据（如 `GITS_KEDB_PASSWORD`、外部 API key）
2. 需求冲突（合同间语义矛盾，TL 无权裁定）
3. 方向性变更（需 Owner 决议）
4. 自愈耗尽（同一 Gate 连续 5 次失败，`max_attempts_per_gate`）
5. 安全隐患（凭据泄露、越权、隔离资产）

**绝对红线（违反即回退）**：
- 不把任何 Loop 标 `closed` 除非其退出标准全部满足
- 不把 `CONTRACT_CANDIDATE` 改 `APPROVED`；不把 `PLANNED_NOT_EXECUTED` 改 `PASS`
- 不改 `generated/`；不改受测制品 `docs/dd/gk-ke-contract/`
- 不代签 Owner 决议；不代签 `QA_PASS`
- 禁止 `git add .`
- 只做 TL 角色工作；需实现改动时切换到 Feature Pilot 并声明 scope

## 1. Wave / Loop 计划（依赖驱动）

| Wave | Loop ID | 工作单 | 依赖 | 角色 | 执行方式 |
|---|---|---|---|---|---|
| **A** | `GK1-l0-2-contract-activation` | L0-2 契约激活 | L0-1 | TL(规划✅)+FP+QA | 串行（唯一入口） |
| **B1a** | `GK2-l1-1-public-semantics` | L1-1 公共语义 | A | FP+语义专家 | 串行（主链首） |
| **B1b** | `GK3-l2-1-semantic-query` | L2-1 语义查询 | B1a + B2a | FP+指标Owner | 串行 |
| **B2a** | `GK4-l1-2-simulation-source` | L1-2 模拟源 | A | FP+数据专家 | 并行（与 B1a） |
| **B2b** | `GK5-l2-2-registry` | L2-2 注册中心 | A | FP+QA | 并行（与 B1a） |
| **C1a** | `GK6-l3-1-factory-candidate` | L3-1 工厂与候选 | B2b | FP | 串行 |
| **C1b** | `GK7-l3-2-review-release` | L3-2 审核发布 | C1a | FP+知识Owner | 串行 |
| **C2** | `GK8-l4-1-map-activation` | L4-1 地图激活 | B1b + C1b | FP | 串行 |
| **C3a** | `GK9-l5-1-kuzu` | L5-1 Kuzu | 无硬依赖 | FP | 并行（可关） |
| **C3b** | `GK10-l5-2-lightrag` | L5-2 LightRAG | 无硬依赖 | FP | 并行（可关） |
| **D** | `GK11-l4-2-gits-closed-loop` | L4-2 GITS 闭环 | C2 + B1b + C1b | FP+业务专家 | 串行 |
| **E** | `GK12-l6-runtime-acceptance` | L6 运行验收 | 全部 | E2E Owner+QA | 串行收尾 |

## 2. Wave A 内部编排（TL → SubAgent 派发）

| 步 | 角色 | 任务 | 交付 | 退出 |
|---|---|---|---|---|
| A-1 | **Feature Pilot** | WI-01 完整 OpenAPI | `specs/openapi/gk-ke-v1.openapi.json` | 门禁全绿 + `DEV_SELF_CHECK_PASS` |
| A-2 | **Feature Pilot** | WI-03 正负例 | `specs/gk-ke/v1/examples/openapi/**` | `gk_ke_openapi_lint` 通过 |
| A-3 | **Feature Pilot** | WI-04 消费者测试 | `scripts/gk_ke_openapi_contract_tests.py` | 全断言通过 |
| A-4 | **TL** | 审合同变更 + 登记 CTR-GKKE-API-001 | `specs/CONTRACT_INDEX.yaml` | `make check` 通过 |
| A-5 | **Independent QA** | 查冲突（15 op 覆盖/闭集/命名空间/simulationOnly） | QA 报告 | `QA_PASS` 或退回 |
| A-6 | **Owner(移交)** | 批准激活 + OC-01 收口 | — | **不代签**，写 BLOCKED.md 或移交说明 |

## 3. 交叉角色约束矩阵

| 约束 | 说明 |
|---|---|
| 开发不得自签 QA | Feature Pilot 只能记 `DEV_SELF_CHECK_PASS` |
| QA 不得改实现 | 独立 QA 发现问题退回 Feature Pilot，不改代码 |
| TL 不得写 Feature 实现 | 需实现时切换到 FP 并声明 scope |
| TL/QA 不得代签 Owner | Owner 决议另记，写移交说明 |
| SubAgent 无 cross-loop 权限 | 每个 SubAgent 只做当前 Baton 分配的工作 |

## 4. SubAgent 派发模板（短提示词）

```text
你是 <ROLE>，做 <LOOP_ID> 的 <WORKITEM>。
共享记忆按仓库规则自动开场/收工（读 LOOP.yaml/STATE.json/ROLE_BOARD.yaml/NEXT_SESSION.md）。
只做 <SPECIFIC_SCOPE>；完成后 STOP，不越界到其它 Loop。
```

## 5. 证据与状态落盘规则

- 每个 Loop 用 `make new-loop` 创建
- 每个 Loop 的门禁通过 `scripts/record_gate.py` 记录（失败自动先写 `FAILURES.md`）
- 每波结束运行 `make evidence-check LOOP=<id>` + `make memory-check LOOP=<id>`
- 未落盘结论视为不存在
- TL tick log 记录在 `loops/<LOOP_ID>/memory/ORCHESTRATOR.md`
