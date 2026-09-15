# P34 Dispatch｜建议书工厂 C2/C3 降级（禁用 G0–G5 写）

```text
DISPATCH_ID=P34-GITS-BANK-PROPOSAL-DEGRADE
STATUS=QA_PASS
OWNER_DECISION=OD-GITS-BANK-UX-2026-08-25
BASE_COMMIT=d3142c9557aaa197c41ef89343ec1e05b073d0a0
WORKING_BRANCH=feature/P30-gits-bank-experience-shell
LOOP=loops/P34-gits-bank-proposal-degrade
DEPENDS_ON=P33-gits-bank-need-task-degrade
IMPLEMENTATION_ACTOR=feature_pilot
CONTRACT_CHANGE=NOT_AUTHORIZED
AUTHORITY_SOURCE_CHANGE=NO
PAGES=P23,P24,P25,P26,P27,P28,P29,P30
PRODUCTION_READY=NO
FROZEN=NO
QA_ACTOR=MUST_BE_INDEPENDENT
```

## 启动条件

仅当 `P33-gits-bank-need-task-degrade` 的 `STATE.status=qa_pass` 后，Tech Lead 才可将本 Loop 置 `in_progress` 并派 Feature Pilot。

## 目标

本分支 **没有** 建议书工厂 / G0–G5 / ProposalVersion 合同。交付 **可进入的降级壳层**：对象头 + 四态 + 全部写动作 DisabledAction。禁止前端画出可回写的 G0–G5 状态机。

| 页 | 名称 | C | 路由候选 | 主动作 |
|---|---|---|---|---|
| P23 | 建议书对象主页 | C2 | `/proposals` | 「导入草稿」禁用 |
| P24 | 新建建议书向导 | C2 | `/proposals/new` | 「保存并继续」禁用 |
| P25 | 建议书记录·G0—G5 | C3 降级 | `/proposals/:id` | 不实现晋级；「预览客户版」禁用或只读空态 |
| P26 | 模块化编辑器 | C2 | `/proposals/:id/editor` | 「提交评审」禁用 |
| P27 | 需求—方案—产品映射 | C2 | `/proposals/:id/map` | 「运行完整性检查」禁用 |
| P28 | AI 内容依据反查 | C2 | `/proposals/:id/evidence` | 「标记问题」禁用；可只读说明不可反查原因 |
| P29 | 内部版与客户版对照 | C2 | `/proposals/:id/project` | 「查看隐藏规则」禁用 |
| P30 | 版本比较与恢复 | C2 | `/proposals/:id/versions` | 「创建新版本」禁用 |

启用左侧「服务建议书」指向 `/proposals`，写路径保持禁用。不要引用 NEED-826 或伪造建议书正文为正式事实。

## 禁止

- 改 `specs/`；新增 Proposal/G0–G5 OpenAPI
- 前端枚举 G0–G5 并回写
- 开发自签 `QA_PASS`

## Feature Pilot 派工

```text
LOOP_ID=P34-gits-bank-proposal-degrade
PAGE_IDS=P23-P30
FORBIDDEN=G0-G5 machine; ProposalVersion formal write; new OpenAPI
EXIT_CRITERIA=shell pages + disabled writes; gates green; no specs diff
```
