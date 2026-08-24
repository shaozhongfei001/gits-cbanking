# P23-scenario-knowledge-provider｜Evidence index

机器可判定的唯一证据板为 `EVIDENCE.json`。本文件只提供人类导航，不复制状态。

- 命令日志：`evidence/`
- 失败记录：`FAILURES.md`
- 波次迭代：`memory/waves/`
- 独立QA：必须由非implementation actor写入 `EVIDENCE.json.independent_qa`

## 2026-08-21 independent_qa PASS

- session：`iqa-p23-20260821T102950Z`
- actor：`independent_qa`（非 feature_pilot / tech_lead）
- 证据：`evidence/independent_qa_20260821T102950Z.log` sha256 `ed3ff855b9634902853f63a1d7ff1d90f6f9a302ba50e82d9e10015b236a9ff7`
- `qa_attest --decision pass` EXIT=0；STATE `qa_pass`
- 未写 `REAL_E2E_PASS`

## 2026-08-21 feature_pilot 修复后（实现侧重跑，已被独立 QA 复跑）

- `backend_test` 原命令重跑 PASS：`evidence/backend_test-20260821T095949Z.log` sha256 `d5356d949dec503d5e676afdf0856ea4a23fb529dbb4f3c4379ad9a94974e365`
- `evidence_check` 原命令重跑 PASS：`evidence/evidence_check-20260821T102328Z.log` sha256 `3cc2470900616c4c7d6c693dd3493aa5d5034f2c4aec5a3c3e126ac1ffba8674`
- 上一轮独立 QA REJECT 证据仍保留：`evidence/independent_qa_20260821T094446Z.log`
