# GK6-simulation-factory｜Handoff

| 项 | 状态 |
|---|---|
| 交付对象 | independent_qa（独立 QA） |
| 开发自检 | `DEV_SELF_CHECK_PASS`（6 gate 全绿，2026-09-10） |
| 独立QA | `PENDING` |
| 生产就绪 | `NO` |

## 交付物

- 自包含离线工厂：`tools/gk-ke-simulation/`（build_simulation.py、validate_package.py、guards.py、simulation/、schemas/、examples/、README.md）
- 单测：`tests/tooling/test_gk_ke_simulation.py`（11 项 T32/T33 负例与确定性）
- 详见 `memory/handoffs/gk6-pilot.md`

## 开放项与禁止声明

- 开发自检不是 QA、不是真实 E2E、不是客户验收、不是生产冻结。
- 未做服务 E2E、Kùzu/LightRAG 集成、真实人工审批（合同明确 NOT_PERFORMED）。
- 独立 QA 须由非 implementation actor 在 `EVIDENCE.json.independent_qa` 记录。
