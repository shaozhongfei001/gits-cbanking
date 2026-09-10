# NEXT SESSION｜GK1-registry-map-core

| 字段 | 值 |
|---|---|
| **holder** | `gk1-pilot-resume` |
| **wave** | `W0` |
| **gate** | 独立 QA 验收（7/7 implementation gate 已全绿） |
| **state** | `in_progress` (QA 退回修复 Q1/Q2/Q3) |

## 交付摘要（CR-02，验收 T05/T06/T07/T20）

- 模块：`modules/knowledge-architecture`，新增包 `com.gien.gits.knowledge.gkke`
  （model 11 个 record/sealed、registry 注册中心+规范化+依赖闭包、map DAG 校验、
  permission 权限过滤、plan ActivationPlan+规范化 SHA-256）。
- 测试：14 个 gkke 测试类 + 存量，模块级 **67 tests / 0 failures / 0 errors / 0 skipped**。
- 资源：`src/test/resources/gk-ke-registry/` 8 个（assets/releases/plans golden+sha256）。
- 合同策略：reuse_only，未改 `specs/` 与 `generated/`，未实现 T17/REST。

## 7 个 gate（全绿）

contract_check / registry_core / map_dag_validate / permission_filter /
plan_canonical_hash（gk1-pilot）；backend_test / security_check（gk1-pilot-resume）。

## QA 须知：backend_test 范围裁决（Tech Lead 2026-09-11）

- backend_test gate 命令为模块级：
  `./mvnw -pl modules/knowledge-architecture -am test -Ddependency-check.skip=true`。
- 全量 `make backend-test` 的两个阻断经 Tech Lead 独立复核确认是基线 c7017b1 存量、非 GK1 引入，
  已隔离到独立基线加固 Loop **`GK-BASELINE-HARDENING`**：
  1. spring-core 6.2.19 的 2026 CVE（6.2.20 企业专属、OSS 无 GA 修复版，需 Owner 决策）；
  2. apps/api `EngagementJourneyControllerTest` 切片缺 CustomerJourneyRepository /
     RelationshipReportRepository 两个 `@MockitoBean`。
- 聚合 JaCoCo≥0.80 门槛随全量 verify 待基线 Loop 收口后恢复；GK1 模块级测试自身全绿。
- 详见 `FAILURES.md` 的 Tech Lead 裁决注记与 `memory/handoffs/gk1-pilot-resume.md`。

## 边界

dev 角色未自签 QA_PASS；独立 QA 按 C02 合同与验收矩阵独立判定。
