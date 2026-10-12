# P30 Dispatch｜GITS Bank Experience Shell + P01–P03 只读

```text
DISPATCH_ID=P30-GITS-BANK-EXPERIENCE-SHELL
STATUS=QA_PASS
OWNER_DECISION=OD-GITS-BANK-UX-2026-08-25
BASE_COMMIT=d3142c9557aaa197c41ef89343ec1e05b073d0a0
WORKING_BRANCH=feature/P30-gits-bank-experience-shell
LOOP=loops/P30-gits-bank-experience-shell
IMPLEMENTATION_ACTOR=feature_pilot
CONTRACT_CHANGE=NOT_AUTHORIZED
AUTHORITY_SOURCE_CHANGE=NO
PAGES=P01,P02,P03
P03_TIER_WRITE=DISABLED_C2
PRODUCTION_READY=NO
FROZEN=NO
QA_ACTOR=MUST_BE_INDEPENDENT
```

## 目标

在不修改 GITS—DKES 受保护契约源的前提下，交付 V3.2 Experience Shell 与 P01–P03 只读切片，并堵住 CI 契约检查空通过。

## 禁止

- 改 `specs/` 权威源或手改 `generated/`
- 实现 C3 正式对象（Need、G0–G5、账户计划、移动写回等）
- 前端硬编码审批、授信、定价、G0–G5、F/C/B/H/P/A 晋级
- 开发角色自签 `QA_PASS`
- 在 `feature/P24-dkws-supplychain` 上混写

## Feature Pilot 派工

```text
LOOP_ID=P30-gits-bank-experience-shell
TASK_ID=WP-UX-FND
PAGE_IDS=P01,P02,P03
REQUIREMENT_IDS=GLOBAL-FR-002,003,004,006,007,015,016,020 + UX-FR-01/02/03-*
BUSINESS_OBJECTS=UI shell context; Customer list C0
CURRENT_ROUTE=/
TARGET_ROUTE_CANDIDATE=/workbench ; /accounts ; /accounts/portfolio
CONTRACT_IDS_OR_C1_C2=CTR-API-001 listCustomers C0; P01 C1; P03 write C2 disable
FORBIDDEN_FIELDS_OR_ACTIONS=G0-G5; Need as formal; portfolio tier write; CRM write; new OpenAPI fields
TEST_IDS=TC-P01-* TC-P02-* TC-P03-* (remain PLANNED until executed with evidence)
EXIT_CRITERIA=LOOP.yaml gates green via record_gate.py; old routes still open; no specs diff
EVIDENCE_REQUIRED=loops/P30-gits-bank-experience-shell/evidence/
ROLLBACK=revert branch; no data migration
```

TDD：先合同消费/组件/拒绝路径测试，再实现。失败先写 FAILURES.md。
