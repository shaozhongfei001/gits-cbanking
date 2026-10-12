# P35 Dispatch｜治理切片 C0/C2（HumanGate / Claim / Audit；其余禁用）

```text
DISPATCH_ID=P35-GITS-BANK-GOV-DEGRADE
STATUS=QA_PASS
OWNER_DECISION=OD-GITS-BANK-UX-2026-08-25
BASE_COMMIT=d3142c9557aaa197c41ef89343ec1e05b073d0a0
WORKING_BRANCH=feature/P30-gits-bank-experience-shell
LOOP=loops/P35-gits-bank-gov-degrade
DEPENDS_ON=P34-gits-bank-proposal-degrade
IMPLEMENTATION_ACTOR=feature_pilot
CONTRACT_CHANGE=NOT_AUTHORIZED
AUTHORITY_SOURCE_CHANGE=NO
PAGES=P31,P32,P33,P34,P35,P37,P38,P39,P40
PRODUCTION_READY=NO
FROZEN=NO
QA_ACTOR=MUST_BE_INDEPENDENT
```

## 启动条件

仅当 `P34-gits-bank-proposal-degrade` 的 `STATE.status=qa_pass` 后，Tech Lead 才可将本 Loop 置 `in_progress` 并派 Feature Pilot。`ready_for_independent_qa` 不够。

## 编号警告

| 本 Loop | 页面 ID | 不要混用 |
|---|---|---|
| Loop **P35** | 页面 **P35** = 客户价值实现 | 不是本 Loop 的名字 |
| 页面 **P34** = 30/90/180 账户计划 | Loop P34 已是建议书降级 | 路由不要写成 loop 名 |
| 页面 **P36** | 已在 Loop P33 以 `/commitments` 交付 | **本 Loop 不改路径、不重做** |
| 页面 **P31–P40** | 不等于 Loop P31 | Loop P31 是客户切片 |

## 目标

在 Experience Shell 内交付 V3.2 页面 P31–P40（不含已交付的 P36）：HumanGate / Claim / Audit **C0 复用既有查询与既有 decide**；专家协同、交付包、账户计划、价值口径、产品适用写、离线包 **C2 禁用**。禁止发明授信/定价状态机，禁止把 F02/F03 标签做成可新建门禁的前端机。

| 页 | 名称 | C | 路由候选 | 做法 |
|---|---|---|---|---|
| P31 | 专家协同记录 | C2 | `/collab` | 对象头+四态；「补充材料」「提交意见」DisabledAction |
| P32 | 审批工作中心 | C0 | `/approvals` | 消费 `fetchHumanGates`；既有 `decideHumanGate` 仅对已返回的门禁；启用导航「审批工作中心」。禁止新建 F02/F03 授信/定价机 |
| P33 | 对客交付中心 | C2 | `/delivery` | 「生成交付包」「确认发送」禁用；无 DeliveryPackage |
| P34 | 30/90/180 天账户计划 | C2 | `/account-plans` | 「新增里程碑」「开始复盘」禁用；Task/Commitment 不能替代 AccountPlan |
| P35 | 客户价值实现 | C2 | `/value` | 「记录基线」「发起复盘」禁用 |
| P36 | 任务与承诺中心 | C0 已交付 | `/commitments` | **保留深链**；不要改 path / pageId |
| P37 | Claim / Evidence 中心 | C0 | `/claims` | 只读消费 `listClaims`；有 `evidenceId` 时用 `fetchEvidenceVersions`。无登记/冲突写 API 则「登记证据」「处理冲突」禁用。启用导航「Claim / Evidence 中心」 |
| P38 | 知识卡与产品适用边界 | C2 | `/knowledge-map`（升级壳层 pageId=P38） | KE 只读；「比较产品」「反馈知识」禁用 |
| P39 | 审计与权限 | C0 | `/audit-trace`（升级壳层 pageId=P39） | 消费 `fetchAuditTrace`。无导出/验权 API 则「导出审计包」「验证权限」禁用 |
| P40 | 服务降级与异常恢复 | C2 | `/degrade` | 查询失败可重试；「下载离线包」禁用（离线写属 P36 Loop / P41–P44） |

启用左侧「审批工作中心」→ `/approvals`、「Claim / Evidence 中心」→ `/claims`。保留 `/proposals`、`/needs`、`/commitments`、`/engagement`、`/engagements`、`/workbench`、`/signals`、`/knowledge-map`、`/audit-trace`。

## 禁止

- 改 `specs/` 或新增专家协同 / DeliveryPackage / AccountPlan / 价值口径 OpenAPI
- 前端画出可回写的授信、定价、F/C/B/H/P/A 状态机
- 把 HumanGate 枚举里的 F02/F03 **标签**做成可创建新门禁的作业流
- 移动离线写回 / 下载离线包当真能力
- 开发自签 `QA_PASS`
- 重做 P36 `/commitments`

## Feature Pilot 派工

```text
LOOP_ID=P35-gits-bank-gov-degrade
PAGE_IDS=P31,P32,P33,P34,P35,P37,P38,P39,P40
C0=P32 HumanGate list+existing decide; P37 listClaims+evidence versions; P39 audit-trace
C2=P31 collab; P33 delivery; P34 account-plan; P35 value; P38 product-boundary write; P40 offline pack
FORBIDDEN=new OpenAPI; fake AccountPlan; F02/F03 create-machine; offline download write
EXIT_CRITERIA=shell pages + C0 reuse + disabled writes; gates green; no specs diff; /commitments unchanged
```
