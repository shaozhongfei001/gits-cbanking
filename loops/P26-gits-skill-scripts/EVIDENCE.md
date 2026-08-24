# P26-gits-skill-scripts｜Evidence index

机器可判定的唯一证据板为 `EVIDENCE.json`。本文件只提供人类导航，不复制状态。

- 命令日志：`evidence/`
- 失败记录：`FAILURES.md`
- 波次迭代：`memory/waves/`
- 实现门禁：`unit_scripts`、`security_check` 已由 `feature_pilot` 记为 pass
- 独立QA：必须由非implementation actor写入 `EVIDENCE.json.independent_qa`
- E2E Owner 复核：`EngagementScenarioE2eIT` AT-007/008 改为 identity-only 后与 `OutreachScriptServiceTest`/`MeetingScriptServiceTest` 合计 24/0；此为开发侧验收，不是 `QA_PASS`
