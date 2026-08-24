# P29-gits-product-skill｜Evidence index

机器可判定的唯一证据板为 `EVIDENCE.json`。本文件只提供人类导航，不复制状态。

- 命令日志：`evidence/`
- 失败记录：`FAILURES.md`
- 波次迭代：`memory/waves/`
- 实现门禁：`unit_product`、`security_check` 已由 `feature_pilot` 记为 pass
- 独立QA：必须由非implementation actor写入 `EVIDENCE.json.independent_qa`
- E2E Owner 复核：ProductMatching 5 + Fallback 7 + AT-009 1 = Maven 13/0；COV 4/0。不是 `QA_PASS`
- 可选开发侧验收：`CustomerOperatingView.spec.ts` 4/0；`EngagementScenarioE2eIT#productMatchingBasedOnTransactions` 1/0。此非 `QA_PASS`
