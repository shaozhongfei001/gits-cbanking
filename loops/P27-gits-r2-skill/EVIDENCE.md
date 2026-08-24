# P27-gits-r2-skill｜Evidence index

机器可判定的唯一证据板为 `EVIDENCE.json`。本文件只提供人类导航，不复制状态。

- 命令日志：`evidence/`
- 失败记录：`FAILURES.md`
- 波次迭代：`memory/waves/`
- 实现门禁：`unit_r2`、`security_check` 已由 `feature_pilot` 记为 pass
- 独立QA：必须由非implementation actor写入 `EVIDENCE.json.independent_qa`
- E2E Owner 复核：mapper + generator + `EngagementScenarioE2eIT` 合计 21/0；R2 不走 `PrevisitWorkflowService`；不是 `QA_PASS`
- 开发侧额外：`EngagementScenarioE2eIT` 14/0（空列表合法）；不是 `QA_PASS`
