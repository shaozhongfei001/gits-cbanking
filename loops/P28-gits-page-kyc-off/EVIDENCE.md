# P28-gits-page-kyc-off｜Evidence index

机器可判定的唯一证据板为 `EVIDENCE.json`。本文件只提供人类导航，不复制状态。

- 命令日志：`evidence/`
- 失败记录：`FAILURES.md`
- 波次迭代：`memory/waves/`
- 实现门禁：`unit_page`、`security_check` 已由 `feature_pilot` 记为 pass
- 独立QA：必须由非implementation actor写入 `EVIDENCE.json.independent_qa`
- E2E Owner 复核：Maven 4/0 + frontend 53/0；启动响应 `kycGapSummary=null`；COV 提示 KI-FRONT-005/003。不是 `QA_PASS`

`unit_page` 组合命令一次通过（Maven `EngagementJourneyControllerTest` 4/0 + frontend 3 files / 53/0），无需拆半。
