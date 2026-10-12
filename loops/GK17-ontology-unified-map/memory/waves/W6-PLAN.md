# W6｜PLAN（**先写后做** —— Wave 级硬要求 #1）

> Time: `2026-09-15`｜Actor: `tech_lead`（TL 拥有 W6）｜max_attempts = **5**（编排表）

## 1. 靶心（照抄编排表，不得自改）

**V1–V4 实验与证据。** ACCEPT 判据：**V1 链路可复核** + **V2/V3/V4 反例全部有变异对照**。

依赖：**W2 ✔（本轮 Tick 14 完成）** + W3（WP3.1 ✔ / **WP3.2 阻塞**）+ W4（未开始）+ **W5 ✔**。

## 2. 判据原文（`docs/architecture/GK-KE-统一地图承担者论证-V1.0.md` §5）

| # | 实验 | 通过判据 |
|---|---|---|
| **V1** | `PRE_VISIT_PREPARATION`（`ONTOLOGY_THEN_MAP`）跑通完整链：路由裁决 → 本体查实体/关系 → 地图按结果定向激活资产 → SKILL 调用 → 输出证据 | 有**可复核的原始输出**（含 `planHash`、`versions.ontology`、路由理由） |
| **V2** | **反例1**：只改本体（如给客户加一条互斥关系），**不动地图** | 计划**必须变化**。不变 ⇒ 本体未被消费 |
| **V3** | **反例2**：地图引用一个**本体中不存在**的个体 | 规划**必须拒绝（fail-closed）**。静默放行 ⇒ ID 锚定形同虚设 |
| **V4** | **反例3**：把同一对象在地图与本体中**手工改成不一致** | 门禁**必须检出** |

**纪律**：V2–V4 若"通过"是因为**夹具缺失导致断言空转**，视为**未验证**；每个反例必须附**变异前后对照**。

## 3. 现状盘点（开工前已实测，不猜）

| 步骤 | 载体 | 现状与注意点 |
|---|---|---|
| ① 路由裁决 | `DefaultRoutePolicyEvaluator` + 真实策略 `RP-CORP-RM-001` | 规则 `priority=20`：`PRE_VISIT_PREPARATION` → `ONTOLOGY_THEN_MAP` / `AC-PREVISIT-001`，**reason 原文**"先锁定客户事实和缺口，再定向加载文档知识"。`RouteDecision.AllowRoute` 携带 `reason`，但**规划器不把 reason 写进计划** ⇒ V1 证据必须**同时**记录 RouteDecision 与计划 |
| ② 本体查实体/关系 | `JenaOntologyAdapter` | 真实本体读数 **32/34/1/0**。⚠ **`individuals = 0`** —— A-Box 个体在 W3 投影（`instances/product/products.ttl`），WP3.2/W4 未完成 ⇒ 本步当前**只能到 T-Box**（须如实声明） |
| ③ 地图定向激活资产 | `DefaultActivationPlanner` | `selectedAssets` / `semanticQueries` / `ruleChecks` / `skills` 全部由**真实文件**（maps / activations / assets）驱动 |
| ④ SKILL 调用 | `SkillExecutionPort` | `dsh.base-url` 为空 ⇒ `FallbackSkillExecutionAdapter` + `MockLlmClient`。⚠ **`NO_LOCAL_FILL` 含 `skill-customer-previsit-report`** ⇒ previsit 技能被**策略性 fail-closed**（`KERT_REQUIRED`），**不补数** |
| ⑤ 输出证据 | `loops/GK17-ontology-unified-map/evidence/` | 本轮独占路径 |
| V3 门禁 | `scripts/gk17_ref_anchor_check.py` | W5 ACCEPT（`--selftest`，6/6 变异自证） |
| V4 门禁 | `scripts/gk17_triple_consistency_check.py` | W5 ACCEPT（**内置变异自证**，`--no-mutation-selftest` 可关） |

## 4. 交付物

| # | 文件 | 内容 |
|---|---|---|
| D1 | `apps/api/src/test/java/com/gien/gits/api/e2e/V1PrevisitChainEvidenceIT.java` | V1 驱动：**真实装配**（filesystem readers + 真实 Jena + 真实路由策略 + 真实规划器）→ 五步全部落**原始**输出 |
| D2 | `evidence/gk17-v1-previsit-chain-<ts>.json` | V1 原始输出（`planHash` / `versions.ontology` / **路由理由** / 本体依据 / 资产 / 技能 / 技能调用轨迹） |
| D3 | `evidence/gk17-v1-<ts>.log` | V1 运行原始日志 |
| D4 | `apps/api/src/test/java/com/gien/gits/api/e2e/V2OntologyOnlyChangeIT.java` | V2 驱动：**只改本体、不动地图**（以地图文件 sha256 证明未动）⇒ `planHash` 必变 |
| D5 | `evidence/gk17-v2-<ts>.json` + log | V2 前后对照 |
| D6 | `evidence/gk17-v3-<ts>.log` | V3：临时根注入悬空引用 ⇒ **检出**；并录基线对照 |
| D7 | `evidence/gk17-v4-<ts>.log` | V4：临时根制造地图/本体不一致 ⇒ **检出**；并录基线对照 |
| D8 | `evidence/GK17-W6-V1-V4-证据包.md` | 汇总（含**覆盖度声明**与**非声明**） |
| D9 | `memory/waves/W6-ITER.md` | ITER 记录 + 变异对照表 |

## 5. 变异对照（每条反例自证「非空转」）

| 判据 | 变异（施加在**源码/临时副本**，不污染权威源） | 期望 |
|---|---|---|
| V2 | 从 `deterministicContent` **移除本体版本** | 驱动 **FAIL**（计划不随本体变） |
| V3 | 临时根注入**悬空** `assetRefs` ID | 门禁 **FAIL**（检出并给出文件+行号） |
| V4 | 临时根制造 D1（本体承载关系实例）/ D4（投影悬空引用） | 门禁 **FAIL** |
| 反向 | 上述恢复 | 回到 **PASS** |

## 6. 明确不做 / 非声明

- **不**声称真实 dsh/KERT 平台已接通：④ 为 **fail-closed 调用**（有轨迹、**无业务产物**）；
- **不**声称 A-Box 实体/关系查询已可用（`individuals=0`，属 WP3.2/W4）；
- V3 的"本体中不存在"当前锚定在**既有权威 ID 空间**（含 `entrypoints.tasks` 对齐本体 `gits:TaskType`），
  **不是**"地图 → A-Box 个体"锚定 —— 此为 WP3.2/W4 完成前的能力边界，**必须在证据包里标注**；
- 不代签 `QA_PASS`；**不把 `INCONCLUSIVE` 计入通过**（`make check` 的 `gate-injection-tests`）；
- W6 的 pending gate `gk17_v1_v4_experiments` **未进 `LOOP.yaml.gates`** ⇒ 本轮**不能**经
  `record_gate.py` 落 `EVIDENCE.json`（该文件属 Loop 记忆单写者）；证据以
  `evidence/` 制品 + `W6-ITER.md` + Tick 落盘，登记留给持 baton 的编排者。

## 7. 失败处理

每次失败**先写 `FAILURES.md`（`record_before_fix`）再修**，按**原命令**重跑并**追加**结果（不覆盖）。
