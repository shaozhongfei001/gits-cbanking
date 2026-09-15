# P37 Dispatch｜适用 SIT 门禁（不声称 264 PASS）

```text
DISPATCH_ID=P37-GITS-BANK-SIT-GATES
STATUS=QA_PASS
OWNER_DECISION=OD-GITS-BANK-UX-2026-08-25
BASE_COMMIT=d3142c9557aaa197c41ef89343ec1e05b073d0a0
WORKING_BRANCH=feature/P30-gits-bank-experience-shell
LOOP=loops/P37-gits-bank-sit-gates
DEPENDS_ON=P36-gits-bank-mobile-degrade
IMPLEMENTATION_ACTOR=feature_pilot
CONTRACT_CHANGE=NOT_AUTHORIZED
AUTHORITY_SOURCE_CHANGE=NO
PAGES=APPLICABLE_IMPLEMENTED_ONLY
PRODUCTION_READY=NO
FROZEN=NO
UAT_PASS=NO
QA_ACTOR=MUST_BE_INDEPENDENT
```

## 启动条件

仅当 `P36-gits-bank-mobile-degrade` 的 `STATE.status=qa_pass` 后，Tech Lead 才可将本 Loop 置 `in_progress` 并派 Feature Pilot。

## 目标

对 **已经实现** 的 P01–P44 降级/C0 页面执行适用工程用例（vitest + 现有 Playwright e2e + 必要的路由抽查）。未覆盖的 V3.2 TC 保持 **PLANNED**。

必须在证据中写清：

- 已执行哪些用例（命令、EXIT、日志）
- 哪些 V3.2 TC 仍为 PLANNED（C3 未授权对象、离线写、G0–G5 真写等）

**禁止**声称 264 PASS、44/44 完成、UAT_PASS、FROZEN、PRODUCTION_READY。

本 Loop **不改业务功能**，不为变绿去实现 C3 对象。

## 禁止

- 改 `specs/` 权威源
- 把 C2 禁用按钮改成可写来凑 e2e
- 开发自签 `QA_PASS` / `UAT_PASS`
- 声称 264 PASS

## Feature Pilot 派工

```text
LOOP_ID=P37-gits-bank-sit-gates
FORBIDDEN=264 PASS claim; UAT_PASS; enable C3 writes to make tests green
EXIT_CRITERIA=applicable vitest+e2e green; SIT matrix executed vs PLANNED; no specs diff
```
