# P33 Dispatch｜Need C2 降级 + P36 任务承诺 C0

```text
DISPATCH_ID=P33-GITS-BANK-NEED-TASK-DEGRADE
STATUS=QA_PASS
OWNER_DECISION=OD-GITS-BANK-UX-2026-08-25
BASE_COMMIT=d3142c9557aaa197c41ef89343ec1e05b073d0a0
WORKING_BRANCH=feature/P30-gits-bank-experience-shell
LOOP=loops/P33-gits-bank-need-task-degrade
DEPENDS_ON=P32-gits-bank-engagement-slice
IMPLEMENTATION_ACTOR=feature_pilot
CONTRACT_CHANGE=NOT_AUTHORIZED
AUTHORITY_SOURCE_CHANGE=NO
PAGES=P20,P21,P22,P36
PRODUCTION_READY=NO
FROZEN=NO
QA_ACTOR=MUST_BE_INDEPENDENT
```

## 启动条件

仅当 `P32-gits-bank-engagement-slice` 的 `STATE.status=qa_pass` 后，Tech Lead 才可将本 Loop 置 `in_progress` 并派 Feature Pilot。

## 目标

Need / ServicePlan 无正式合同对象：页面必须 **C2 禁用正式 Need 写**，可用 Claim / KYC / Signal **只读近似**，禁止发明 NEED-826 一类正式 ID。P36 任务与承诺复用既有 `/commitments` `/tasks`（C0）。

| 页 | 名称 | C | 路由候选 | 做法 |
|---|---|---|---|---|
| P20 | 需求与机会对象主页 | C2 | `/needs` | 列表只读近似（机会信号/Claim）；「新建机会」禁用 |
| P21 | 需求记录 | C2 | `/needs/:id` | 只读详情；「请求专家」禁用 |
| P22 | 机会与服务计划记录 | C2 | `/needs/:id/plan` | 只读；「创建建议书」禁用（建议书属 P34） |
| P36 | 任务与承诺中心 | C0 | `/commitments`（保留深链） | 升级 CommitmentDashboard 壳层；消费 listCommitments / listTasks |

## 禁止

- 改 `specs/` 或把 Need 写成正式领域对象
- 前端硬编码 G0–G5、审批、授信、定价
- 开发自签 `QA_PASS`

## Feature Pilot 派工

```text
LOOP_ID=P33-gits-bank-need-task-degrade
TASK_ID=WP-UX-NEED-TASK
PAGE_IDS=P20,P21,P22,P36
FORBIDDEN_FIELDS_OR_ACTIONS=Need as formal; ServicePlan as formal; new OpenAPI fields
EXIT_CRITERIA=LOOP.yaml gates green; /commitments still open; no specs diff
```
