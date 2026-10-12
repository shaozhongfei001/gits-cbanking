# P31 Dispatch｜GITS Bank P04–P10 客户/信号只读切片

```text
DISPATCH_ID=P31-GITS-BANK-CUSTOMER-SLICE
STATUS=QA_PASS
OWNER_DECISION=OD-GITS-BANK-UX-2026-08-25
BASE_COMMIT=d3142c9557aaa197c41ef89343ec1e05b073d0a0
WORKING_BRANCH=feature/P30-gits-bank-experience-shell
LOOP=loops/P31-gits-bank-customer-slice
DEPENDS_ON=P30-gits-bank-experience-shell
IMPLEMENTATION_ACTOR=feature_pilot
CONTRACT_CHANGE=NOT_AUTHORIZED
AUTHORITY_SOURCE_CHANGE=NO
PAGES=P04,P05,P06,P07,P08,P09,P10
PRODUCTION_READY=NO
FROZEN=NO
QA_ACTOR=MUST_BE_INDEPENDENT
```

## 启动条件

仅当 `P30-gits-bank-experience-shell` 的 `STATE.status=qa_pass`（独立 QA `qa_attest --decision pass`）后，Tech Lead 才可将本 Loop 置 `in_progress` 并派 Feature Pilot。

## 目标

在 Experience Shell 内交付 V3.2 页面 P04–P10 的 **C0/C1 只读消费 + C2 写禁用**，不改契约权威源。

| 页 | 名称 | C | 路由候选 | 既有合同消费 |
|---|---|---|---|---|
| P04 | 客户记录·经营总览 | C0 | `/customers/:id`（保留深链） | `fetchCustomer` / `fetchCustomerContext` |
| P05 | 客户记录·集团关系 | C2 只读 | `/customers/:id/group` | 客户字段只读；「发起核验」禁用 |
| P06 | 客户记录·业务资金全景 | C1 | `/customers/:id/funds` | `fetchTransactions`；「创建需求」禁用（Need=C3） |
| P07 | 客户记录·关系人情报 | C2 | `/customers/:id/parties` | 展示中性关系摘要；「请求引荐」禁用 |
| P08 | 经营信号对象主页 | C0 | `/signals` | `fetchOpportunitySignals` / 既有 signal GET |
| P09 | 经营信号记录 | C0 | `/signals/:id` | 单条信号只读；「忽略」写禁用除非已有合同写 |
| P10 | 互动对象主页 | C1 | `/engagements` | `recentInteractions` / journey interactions；「同步日历」禁用 |

保留 `/customers/:id`、`/engagement`、`/external-events` 既有深链，不得 404。

## 禁止

- 改 `specs/` 权威源或手改 `generated/`
- 把 Need / G0–G5 / 账户计划写成正式对象
- 前端硬编码审批、授信、定价、F/C/B/H/P/A
- P05「发起核验」、P07「请求引荐」、P06「创建需求」作为正式 Action
- 开发角色自签 `QA_PASS`
- 在 `feature/P24-dkws-supplychain` 上混写

## Feature Pilot 派工

```text
LOOP_ID=P31-gits-bank-customer-slice
TASK_ID=WP-UX-CUST
PAGE_IDS=P04,P05,P06,P07,P08,P09,P10
REQUIREMENT_IDS=UX-FR-04-* … UX-FR-10-*
BUSINESS_OBJECTS=Customer C0; Signal C0; Interaction C1; Group/Party C2 read-only
CURRENT_ROUTE=/customers/:id ; /engagement ; /external-events
TARGET_ROUTE_CANDIDATE=/customers/:id ; /customers/:id/group|funds|parties ; /signals ; /signals/:id ; /engagements
CONTRACT_IDS_OR_C1_C2=CTR-API-001 customer/signal/transaction reads C0; writes C2 disable
FORBIDDEN_FIELDS_OR_ACTIONS=Need formal; G0-G5; CRM write; new OpenAPI fields; relationship verify write; referral write
TEST_IDS=TC-P04-* … TC-P10-* (remain PLANNED until executed with evidence)
EXIT_CRITERIA=LOOP.yaml gates green via record_gate.py; old routes still open; no specs diff
EVIDENCE_REQUIRED=loops/P31-gits-bank-customer-slice/evidence/
ROLLBACK=revert branch; no data migration
```

TDD：先合同消费/禁用路径测试，再实现。失败先写 FAILURES.md。
