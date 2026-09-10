# NEXT SESSION｜GK1-registry-map-core

| 字段 | 值 |
|---|---|
| **holder** | `gk1-pilot-resume` |
| **wave** | `W1-QA-FIX` |
| **gate** | 独立 QA 退回修复（T05/T06/T07/T20 全部 fail） |
| **state** | `in_progress` / current_phase=`implementation` |
| **QA** | `gk1-qa2`，session `qa-gk1-formal-002`，结论 **REJECTED**（2026-09-11） |

## 权威 QA 报告（先读）

`evidence/INDEPENDENT_QA.md`（sha256 见 EVIDENCE.json `independent_qa`）。
独立重跑：模块 **67 tests / 0 failures / 0 errors / 0 skipped**，其中 gkke 包 **47 tests** 全绿——
但绿测试未覆盖验收行为，**T05/T06/T07/T20 均不满足**。

## 必修清单（不得改 specs/ 与 generated/）

1. **T20（map_dag_validate）**：`KnowledgeMapDagValidator.adjacency()` 当前对所有边判环，
   实证 relatedTo/covers 导航环被误拒。改为只对执行依赖边（dependsOn/requires 等执行类型）判环，
   导航边（relatedTo/covers）不参与；补"导航环不误判 + 执行环仍拒绝"对拍用例。
2. **T06（registry_core）**：落地 C02 §6 错误码 `CAPABILITY_NOT_REGISTERED`、
   `DEPENDENCY_UNRESOLVED`（当前全代码 0 处，断裂引用只抛无码 AssetNotFoundException）；
   引入能力注册；计划失败硬拒绝、无静默降级；加负例。
3. **T07（permission_filter）**：当前仅单一资产投影 filter/filterRefs/decide。补齐
   目录列表 / 标题摘要 / 关系邻居 / 节点计数四类出口的无权零泄漏测试；实现含
   `tenant/principalScopeHash/purpose/releaseId/catalogRevision` 五要素的缓存键并测隔离。
4. **T05（plan_canonical_hash）**：当前无 TaskContext 计划构建器、无 Wiki/对象双入口，
   "确定性"测试只是同一 Java 对象哈希两次。需双入口基于同一 TaskContext 构建 plan 并对拍 hash 相等。
5. **字段对齐 gk-ke/v1 冻结 schema**：边字段 `relation`（requires/optional/uses/dependsOn/
   covers/relatedTo）替换自创 `type`（DEPENDS_ON/ROUTES_TO）；补 contractVersion/simulationOnly/
   releaseId 等；修正 lifecycle 枚举（夹具用了非法 DRAFT，应为 CANDIDATE/IN_REVIEW/APPROVED/
   PUBLISHED/REVOKED）；或提供明确 schema↔record 映射层并在证据说明。

## 已确认合规、无需返工

- `git diff c7017b1 HEAD -- specs generated` 为空；改动仅 modules/knowledge-architecture + loops。
- backend_test 模块级降级合法（Tech Lead 裁决，基线 spring-core CVE 隔离至 GKB，
  决策包主仓 loops/GKB-baseline-hardening/evidence/SPRING_CORE_CVE_DECISION.md 真实存在）。
- security_check PASS；代码风格（record/无 System.out）无阻断问题。

## 边界

dev 角色不得自签 QA_PASS；修复并更新证据后，重新提交独立 QA（新 session）。
