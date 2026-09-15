# W2｜PLAN（本体真实进入知识路由）

## Goal

把"本体被路由真实消费"从**声称**变成**可判定的事实**，并让判据 **V2**（只改本体 ⇒ 计划必须变）成立。

## 靶心（实测定位，非推测）

`modules/knowledge-architecture/.../plan/DefaultActivationPlanner.java`：

```40:41:modules/knowledge-architecture/src/main/java/com/gien/gits/knowledge/plan/DefaultActivationPlanner.java
    /** Ontology 版本占位（shadow 阶段不加载真实本体，仅登记合同引用）。 */
    private static final String ONTOLOGY_VERSION = "CTR-SEM-001/002@CURRENT_BASE";
```

```160:164:modules/knowledge-architecture/src/main/java/com/gien/gits/knowledge/plan/DefaultActivationPlanner.java
                new ActivationPlan.Versions(    // 各合同版本，供审计溯源
                        map.mapId() + "@" + map.version(),          // 知识地图版本
                        route.policyId() + "@" + route.policyVersion(), // 路由策略版本
                        contract.contractId() + "@" + contract.version(), // 激活合同版本
                        ONTOLOGY_VERSION),                          // 本体版本占位
```

**⇒ 缺口三条**：
1. `versions.ontology` 是**硬编码占位串**，本体**从未被加载**；
2. `deterministicContent()`（决定 `planHash`）**不含**本体版本 ⇒ 改本体不改变 `planHash` ⇒ **V2 在构造上不成立**；
3. 计划里**没有任何字段**能证明本体被读过（只有一句"已登记合同引用"）。

## 爆炸半径（实测）

占位串只被钉在 **3 处**：常量 1 处 + `specs/knowledge-architecture/examples/AP-PREVISIT-GOLDEN.json`
与 `AP-FACT-RECON-GOLDEN.json` 的 `versions.ontology` 各 1 处。
黄金用例里的 `planHash` 是 `GOLDEN_PLAN_HASH_NOT_...`（**未被钉死**）⇒ 改 `planHash` 不破黄金。

## Work Packages

| WP | 内容 | 独占路径 | 状态 |
|---|---|---|---|
| **WP2.1** | `OntologyPort` + Jena 实现（读 T-Box + A-Box，fail-closed） | `modules/semantic-runtime/`, `adapters/semantic-jena/` | **完成** |
| **WP2.2** | `routeMode` 四路径消费 `versions.ontology`；裁决带本体依据写入 plan trace；本体不可达 ⇒ fail-closed | `modules/knowledge-architecture/` | 未开始 |
| **WP2.3** | `planHash` 纳入本体版本 | 同上 | 未开始 |

## ACCEPT 判据

> 路由裁决**带本体依据**并写入 plan trace；本体不可达 ⇒ **fail-closed**；**负例通过**。

## 关键设计决定（**复用而非新造**）

- **不复用** `JenaSemanticRepositoryAdapter` 的 `validate()` —— 那是 SHACL 校验，职责不同；
  但**复用其依赖与读法**（`RDFDataMgr` + `Lang.TURTLE`），且 **SHACL 校验仍归它**，本 WP 不重复实现；
- T-Box/A-Box 判定**复用 Jena 词汇表**（`owl:Class` / `owl:ObjectProperty` / `owl:DatatypeProperty`），
  与 `specs/semantic/gits-core.owl.ttl` 的写法一致，**不另立一套判定**；
- **版本由内容 SHA-256 派生**（`<contractRef>@sha256:<16hex>`）——
  这是 V2 能被机械保障的前提：本体一变，版本必变。

## 非声明

- WP2 **不**启用 fusion、**不**改 SHACL、**不**做生产写回；
- WP2 **不**声称"本体语义已被完整消费"—— 只保证"本体被真实加载，且其版本进入计划与 `planHash`"。
