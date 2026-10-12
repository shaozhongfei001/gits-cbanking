# P37-gits-bank-sit-gates｜Evidence index

机器可判定的唯一证据板为 `EVIDENCE.json`。本文件只提供人类导航，不复制状态。

- 命令日志：`evidence/`
  - `evidence/contract_generate-20260825T174726Z.log` EXIT 0
  - `evidence/contract_check-20260825T174729Z.log` EXIT 0
  - `evidence/security_check-20260825T174732Z.log` EXIT 0
  - `evidence/sit_applicable-20260825T174738Z.log` EXIT 0（vue-tsc；vitest 54/291；Playwright 8 spec / 36 tests）
- 适用矩阵：`evidence/SIT_MATRIX.md`（executed vs PLANNED；**不是** 264 PASS / UAT_PASS）
- 失败记录：`FAILURES.md`（本轮无失败追加）
- 波次迭代：`memory/waves/W0-ITER.md`
- Implementation 四门：`EVIDENCE.json.gates.*` 保持 `actor=feature_pilot`，独立 QA 未改写
- 独立QA：`EVIDENCE.json.independent_qa`（session `iqa-p37-20260825T175104Z`）
- 独立QA 复跑与抽查日志：`loops/P37-gits-bank-sit-gates/evidence/independent_qa_20260825T175104Z.log`
- SHA256：`035a98d97e6fc6c990ad3aab7e0ec6f0d7b3a414b503d9e20d2ea43087a9fff1`

Independent QA 已 `qa_attest --decision pass`。这不是 `UAT_PASS` / `FROZEN` / `PRODUCTION_READY` / 264 PASS。
