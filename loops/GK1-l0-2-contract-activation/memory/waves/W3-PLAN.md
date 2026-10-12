# W3｜Plan（L0-2 契约激活规划与派工）

## Goal

TL 侧完成 L0-2 规划与派工：CR 审计、兼容与生成策略、OC-01 收口证据、Feature Pilot 派工单。

## Baseline

- 主仓 HEAD（开工）：`597d6facdc120a9fbffc44cff116eab50bbb3367`（分支 `feature/GK-KE-L0-contract`）
- 封版锚点：`886f710` / tree `4c5f5373` / ZIP `b21638ab`（V1.0.2）
- 祖先核验：`886f710` 是 HEAD 的祖先（封版未被回退）

## Scope（TL 只做规划，不写实现）

| WI | 交付 | 角色 |
|---|---|---|
| WI-00 | CR-01~08 审计与处置 | tech_lead ✅ |
| WI-01 | 完整 /gk-ke/v1 OpenAPI（15 operation） | feature_pilot（已派工） |
| WI-02 | 兼容与生成策略 | tech_lead ✅ |
| WI-03 | 候选契约正负例（每 operation ≥2） | feature_pilot（已派工） |
| WI-04 | 消费者驱动测试 | feature_pilot（已派工） |
| WI-05 | OC-01 收口 | tech_lead（证据齐备，Owner 签署待） |

## Gates（以 LOOP.yaml.gates 为唯一命令源）

`contract_generate` / `contract_check` / `security_check` / `gk_ke_examples` / `gk_ke_openapi_lint`（新增）/ `gk_ke_hash`

## TL 决策摘要

- D-1：L0-2 只产出候选 + 正负例 + 消费者测试，不产出服务实现。
- D-2：gk-ke/v1 不吞并 PI-0 既有合同，以 `x-gk-ke-pi0-mapping` 登记映射。
- D-3：接口命名空间隔离，`specs/openapi/gk-ke-v1.openapi.json` 物理分文件。
- D-4：C06 §1 的 15 个 operation 全落 OpenAPI，每 operation ≥2 负例。
- D-5：`simulationOnly` 为硬约束，不得放宽。
- D-6：兼容基调 = `explicit_migration`（与 CONTRACT_INDEX 现有 CTR-GKKE-001~020 对齐）。

## 红线遵守

- 未改 `generated/`、未改 `specs/gk-ke/`、未改封版制品 `docs/dd/gk-ke-contract/`。
- 未把 CONTRACT_CANDIDATE 改 APPROVED；未把 GK0 标 closed。
- TL 未记 `DEV_SELF_CHECK_PASS` / `QA_PASS`（门禁由 Feature Pilot 执行后记录）。
