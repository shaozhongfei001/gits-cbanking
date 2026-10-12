# P36 Dispatch｜移动端 C2 降级（无离线写）

```text
DISPATCH_ID=P36-GITS-BANK-MOBILE-DEGRADE
STATUS=QA_PASS
OWNER_DECISION=OD-GITS-BANK-UX-2026-08-25
BASE_COMMIT=d3142c9557aaa197c41ef89343ec1e05b073d0a0
WORKING_BRANCH=feature/P30-gits-bank-experience-shell
LOOP=loops/P36-gits-bank-mobile-degrade
DEPENDS_ON=P35-gits-bank-gov-degrade
IMPLEMENTATION_ACTOR=feature_pilot
CONTRACT_CHANGE=NOT_AUTHORIZED
AUTHORITY_SOURCE_CHANGE=NO
PAGES=P41,P42,P43,P44
PRODUCTION_READY=NO
FROZEN=NO
QA_ACTOR=MUST_BE_INDEPENDENT
```

## 启动条件

仅当 `P35-gits-bank-gov-degrade` 的 `STATE.status=qa_pass` 后，Tech Lead 才可将本 Loop 置 `in_progress` 并派 Feature Pilot。

## 编号警告

Loop **P36** ≠ 页面 **P36**。页面 P36（`/commitments`）已在 Loop P33 交付，本 Loop **不得改**该路径。本 Loop 只做 V3.2 页面 P41–P44 移动端降级壳。

## 目标

本分支 **没有** 移动缓存 / 撤权 / 同步合同。交付 **可进入的降级壳**：对象头 + 四态 + 离线写全部 DisabledAction。在线只读可复用既有桌面查询；禁止把 PNG 上的离线包、缓存、同步画成可写能力。

| 页 | 名称 | C | 路由候选 | 主动作 |
|---|---|---|---|---|
| P41 | 移动端·今日客户行动 | C2 | `/m/today` | 「打开首项」仅可跳已有在线深链；禁止离线队列写 |
| P42 | 移动端·访前包 | C2 | `/m/previsit` | 「开始拜访」禁用（隐含缓存/离线包） |
| P43 | 移动端·会中速记 | C2 | `/m/notes` | 「新增速记」禁用离线写；不要当作正式 Claim |
| P44 | 移动端·离场确认与任务 | C2 | `/m/checkout` | 「完成会谈」禁用，除非复用已有 PENDING `E01_EXIT_CONFIRM` HumanGate（与桌面 P17 同一合同）；禁止离线完成 |

窄屏布局可做，但不要声称原生 App / Service Worker 缓存 / 下载离线包。

保留桌面深链：`/workbench`、`/engagement`、`/in-meeting`、`/commitments`、`/approvals`、`/claims`。

## 禁止

- 改 `specs/`；新增移动缓存 / 同步 OpenAPI
- Service Worker 写回、localStorage 当正式事实、下载离线包当真能力
- 开发自签 `QA_PASS`
- 改页面 P36 `/commitments`

## Feature Pilot 派工

```text
LOOP_ID=P36-gits-bank-mobile-degrade
PAGE_IDS=P41-P44
FORBIDDEN=offline write; mobile cache contract; change /commitments
EXIT_CRITERIA=enterable mobile degrade shells; writes disabled; gates green; no specs diff
```
