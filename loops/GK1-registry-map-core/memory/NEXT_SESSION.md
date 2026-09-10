# NEXT SESSION｜GK1-registry-map-core

| 字段 | 值 |
|---|---|
| **holder** | `independent_qa` |

> holder 由 gk1-qa2 或其他非 implementation actor 执行（dev 角色禁止自签 QA_PASS）。
| **wave** | `W1-QA-FIX-RECHECK` |
| **gate** | 复验 gk1-fix 对 Q1/Q2/Q3 的修复 |
| **state** | `ready_for_independent_qa` / current_phase=`independent_qa` |
| **上轮 QA** | `gk1-qa2`，session `qa-gk1-formal-002`，结论 **REJECTED**（2026-09-11） |

## 本次修复范围（严格限定）

gk1-fix 只修派工指定的三项，详见 `memory/handoffs/gk1-fix.md`：

- **Q1（T20）**：新增 `map/MapRelation` 枚举；`KnowledgeMapDagValidator` 只对执行依赖边
  （dependsOn/requires/uses）做 DAG 环检测，covers/relatedTo/optional 不参与；relation 非法值拒绝。
- **Q2**：`MapEdge/MapNode/KnowledgeMapRecord/AssetVersionRecord` 严格对齐
  `specs/gk-ke/v1/schemas/KnowledgeMap.schema.json`（additionalProperties=false）与 AssetVersion schema；
  删除 type/ROUTES_TO/entryNodeIds/DRAFT 等漂移；新增合同正例反序列化 + JSON Schema 校验测试
  `KnowledgeMapContractAlignmentTest`（正例 `test/resources/gk-ke-registry/maps/SIM-MAP-FINANCE.json`）。
- **Q3（T06）**：`registry/GkErrorCode`（10 码）+ `GkDomainException`；
  DEPENDENCY_UNRESOLVED / CAPABILITY_NOT_REGISTERED（+最小 CapabilityRegistry）/
  ASSET_NOT_AVAILABLE 等落地，测试断言错误码字符串。

**T05 与 T07 不在本次派工范围，未修复**，QA 报告中该两项退回结论保持不变，需后续批次处理。
未改 specs/ 与 generated/（reuse_only）。

## 复验入口

1. 交接详单：`memory/handoffs/gk1-fix.md`（含 relation 取舍依据、新增测试清单）。
2. 模块全量：`MAVEN_OPTS=-Ddependency.check.auto.update=false ./mvnw --batch-mode --no-transfer-progress -pl modules/knowledge-architecture -am test -Ddependency-check.skip=true`
   → 80 tests / 0 failures / 0 errors / 0 skipped。
3. gate 证据（actor=gk1-fix，均 PASS）：evidence/ 下 20260910T18332*Z~183333Z 四份日志
   （map_dag_validate / registry_core / plan_canonical_hash / contract_check）。
4. `make generate && make check` 无漂移。
5. 独立 QA 结论写入 `EVIDENCE.json.independent_qa`（dev 角色禁止自签 QA_PASS）。

## 已确认合规、无需返工

- `git diff c7017b1 HEAD -- specs generated` 为空；本次改动仅 modules/knowledge-architecture + loops + 模块测试 pom。
- backend_test 模块级降级合法（Tech Lead 裁决，基线 spring-core CVE 隔离至 GKB）。
- security_check PASS；代码风格（record/sealed/无 System.out）无阻断问题。
