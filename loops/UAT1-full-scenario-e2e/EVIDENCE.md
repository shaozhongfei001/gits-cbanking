# UAT1-full-scenario-e2e｜Evidence index

机器可判定的唯一证据板为 `EVIDENCE.json`。本文件只提供人类导航，不复制状态。

- 命令日志：`evidence/`
- 失败记录：`FAILURES.md`
- 波次迭代：`memory/waves/`
- 独立QA：必须由非implementation actor写入 `EVIDENCE.json.independent_qa`

## 本轮（2026-09-26）人类导航

- 门禁：11/11 PASS（env_ready、W0–W8 九个波次、uat_package），浏览器用例合计 **115 全通过**。
- 证据：各门禁原始日志在 `evidence/<gate>-<时间戳>.log`（含 Playwright list 输出与逐路由诊断）。
- 交付包：`UAT_PACKAGE.md`（场景 × 功能点 × 判定矩阵）。
- 真实被测环境：前端 5173（Vite，代理 → 后端 18080 / KERT 8107）、GITS API 18080、KERT 8107（DuckDB 分析库）、LightRAG 9621。
- 关键修复：F-UAT1-01（KERT 分析 503）、F-UAT1-06（报告页伪造数据，P0）、F-UAT1-07（录音同意参数语义）、F-UAT1-08（门禁自身缺陷）。
- 变异复验：真实停掉 KERT 8107 ⇒ W5 5 failed / 1 passed ⇒ 恢复后 6/6 PASS（证明断言非空转）。
- 已知未决（非阻塞）：F-UAT1-10 前端存量单测 17 failed（组件测试与 UI 文案漂移）。
