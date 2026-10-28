# NEXT SESSION｜GK1-registry-map-core

| 字段 | 值 |
|---|---|
| **holder** | `owner_review` |
| **wave** | `W2-OWNER-REVIEW` |
| **state** | `qa_pass` / current_phase=`owner_review` |
| **QA** | `gk1-qa2`，session `qa-gk1-formal-003`，结论 **QA_PASS**（2026-09-10T19:00Z，HEAD `1c80c6d`） |

## QA 结论（先读）

`evidence/INDEPENDENT_QA-003.md`（sha256 `c6ef1004…f11625`）。002 退回的五项必修全部修复并经独立验证：

- **独立 clean 重跑**：模块 **95 tests / 0 failures / 0 errors / 0 skipped**（基线 67→95）。
- **仓库外行为探针** `/tmp/gk1qa3/Probe.java`：**26/26 PASS**；并做变异实验（篡改 DAG 边过滤重现 002 缺陷→探针 24/26，还原→26/26），证明探针有效。
- **make check**：全 PASS、零漂移（合同样例正例 14/14、负例 28 全拒）。
- T20 执行边判环/导航边放行、T06 三错误码硬拒绝无静默降级、T07 四出口零泄漏+五要素缓存键不串、T05 Wiki/对象双入口 planHash 逐字节相等，均行为级通过。
- 合同纪律：`specs/generated` diff 为空，未实现 T17/REST，改动仅 modules/knowledge-architecture + loops。

## 三个合同解释点（QA 判定均不阻断，详见报告 §6）

1. principalScopeHash 用 JVM 内确定性 hashCode（非跨语言 SHA-256）：L1 可接受，跨语言算法留 L2/L3 ADR。
2. 邻居出口"可见即可导航"、仅按节点可见性过滤：满足 C02 §7.1 零泄漏，可接受。
3. ActivationPlanner 遍历全部节点、未在装配路径启用 entryNodes 可达闭包（`reachableSubgraph` 已存在且有测试）：L1 可接受偏差，**建议 L2/T17 Loop 列为必做**。

## 残留风险（不阻断关闭）

- 基线 spring-core CVE 的全量 `make backend-test`/聚合 JaCoCo 待 GKB-baseline-hardening 收口（与 GK1 代码无关，Owner 已授权窄抑制至 2026-10-31）。
- 上述解释点 1、3 建议在 L2/T17 入口跟踪。

## 下一步

Owner 评审并按 Loop 流程关闭（status→closed）。dev 角色不得改 QA 记录。
