# GK6-simulation-factory｜Evidence index

机器可判定的唯一证据板为 `EVIDENCE.json`。本文件只提供人类导航，不复制状态。

- 命令日志：`evidence/`（6 gate，全部 PASS；isolation_oracle 第 1 次红见 FAILURES.md）
- 失败记录：`FAILURES.md`
- 波次迭代：`memory/waves/`
- 交接：`memory/handoffs/gk6-pilot.md`
- 独立QA：必须由非implementation actor写入 `EVIDENCE.json.independent_qa`

## Gate 结果导航（2026-09-10，gk6-pilot）

| Gate | 结果 | 关键结论 |
|---|---|---|
| contract_check | PASS | `make generate` + `make check` 无合同漂移（未改 specs/generated） |
| vendor_factory | PASS | 自包含包 `tools/gk-ke-simulation/` 可从仓库根运行，确定性重写 |
| validate_dataset | PASS | 离线自检 117/117，T30/T31 真值全部满足 |
| isolation_oracle | PASS | T32/T33 负例 11 项；oracle 真值不进 graph/documents 语料 |
| tooling_test | PASS | tests/tooling 43 项全绿，无回归 |
| security_check | PASS | 无密钥/凭据/真实机构映射 |
