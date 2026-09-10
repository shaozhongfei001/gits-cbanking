# Handoff: gk6-pilot → independent_qa

- Loop: GK6-simulation-factory（CR-07，T30/T31/T32/T33）
- 时间：2026-09-10T15:25Z
- 基线：c7017b18250ccef16b167d539d975aa0d809fffd
- 6 个 implementation gate 全部 PASS（EVIDENCE.json）：
  contract_check / vendor_factory / validate_dataset / isolation_oracle / tooling_test / security_check。
  isolation_oracle 首次红（TDD：测试模块未创建），根因与修复已记 FAILURES.md，重跑 PASS。

## 交付物

新增自包含包 `tools/gk-ke-simulation/`：
- `build_simulation.py`：确定性工厂（候选原文搬迁，仅包根 parents[1]→parent）。
- `validate_package.py`：离线自检（包根校正；报告改写到包内 reports/；删除仓库级 CONTRACT_INDEX 检查，该职责归 `make check`）。
- `guards.py`：T32 人工控制闸 + T33 模拟边界守卫（纯 stdlib）。
- `simulation/`：固定种子（seed_scenarios/source_catalog/documents）+ 派生产物（tables 10 CSV、graph nodes/edges、oracles/expected.json、dataset_manifest.json）+ 夹具（capability_contract/confirmation_fixture/query_registry/statements/registry_snapshot/map_review_decision/avg_deposit.sql）。
- `schemas/`：10 个本地 JSON Schema 校验副本。
- `examples/`：schema 正/负例夹具（registry_snapshot.contentRef 与校验器依赖）。
- `README.md`、`.gitignore`（reports/ 不入库）。

新增测试 `tests/tooling/test_gk_ke_simulation.py`（11 项，纯 stdlib）：
- T32 负例 5：生产写动作、自批、陈旧版本确认、预测当事实、客户端注入授权参数。
- T33 负例 3：缺 simulationOnly、非 SIM- 前缀、oracle 泄漏进语料。
- 基线正例 + 工厂重构建字节稳定。

## 关键真值（已由 validate_package 117 项断言）

12 客户 / 24 账户 / 6 产品 / 30 天 / 144 事件 / 288 分录 / 720 日余额 / 12 授信 / 12 持有 / 18 文档；
SIM-CUST-001 日均存款 2,983,333.33 CNY；每事件同币借贷相等反向；
closing=opening+ΣsignedAmount；次日 opening=前日 closing；manifest 哈希一致；确定性重写无 diff。

## 边界声明

- 未改 `specs/`、`generated/`、CONTRACT_INDEX；无模型/网络/真实 DB 调用。
- 全部产物 simulationOnly=true、ID 以 SIM- 开头；oracles 不在 graph/documents 语料。
- 开发角色仅记录 DEV_SELF_CHECK_PASS（validate_package scope=OFFLINE_AUTHOR_SELF_CHECK）；QA_PASS 待独立 QA。
- 非生产就绪：无服务 E2E、无 Kùzu/LightRAG 集成、无真实人工审批。
