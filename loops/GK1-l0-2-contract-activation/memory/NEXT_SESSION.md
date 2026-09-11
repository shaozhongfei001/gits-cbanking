# GK1-l0-2-contract-activation｜Next Session Baton

| 字段 | 值 |
|---|---|
| **Updated** | `2026-09-12` |
| **holder** | `tech_lead` |
| **packet** | `GK1-l0-2-contract-activation` |
| **wave** | `A（L0-2 契约激活，唯一入口）` |
| **gate** | `gk_ke_openapi_lint`（新增）+ 存量五门禁 |
| **do_not_start** | 无 |

## 短提示词

你是 **Feature Pilot**，做 L0-2 契约激活的 WI-01 / WI-03 / WI-04。
共享记忆按仓库规则自动开场/收工。

**派工单**：`docs/dispatch/GK-KE-L0-2-派工单-WI-01-03-04.md`（含 15 operation 清单、负例类别、消费者测试断言）
**CR 审计**：`docs/architecture/GK-KE-L0-2-CR审计与处置-V1.0.md`
**兼容策略**：`docs/architecture/GK-KE-L0-2-兼容与生成策略-V1.0.md`
**OC-01 收口**：`docs/architecture/GK-KE-L0-2-OC01收口-V1.0.md`

只做：
1. `specs/openapi/gk-ke-v1.openapi.json`（15 operation）
2. `specs/gk-ke/v1/examples/openapi/**`（每 operation ≥2 负例）
3. `scripts/gk_ke_openapi_contract_tests.py`（消费者驱动测试）
4. `specs/CONTRACT_INDEX.yaml` 新增 `CTR-GKKE-API-001` 登记

完成后记 `DEV_SELF_CHECK_PASS`，更新 EVIDENCE/STATE/NEXT_SESSION，Baton → `independent_qa`，**STOP**。

## TL 已完成（本次会话）

- 三检全绿（loop_guard / memory-check / evidence-check）
- Loop `GK1-l0-2-contract-activation` 创建并绑定 C08 L0-2 scope（6 门禁 + 6 工作单 + 退出标准）
- WI-00 CR-01~08 审计与处置（含 6 条 TL 决策 D-1~D-6）
- WI-02 兼容与生成策略（四级兼容 / 闭集清单 / 三层权威流 / 5 条回归门禁）
- WI-05 OC-01 收口证据（三仓锚点 / 地图 ID↔版本↔对象 / schema↔端点↔消费者）
- 派工单 WI-01/03/04

## 交接历史

- GK0 W0~W2.5：合同 V1.0.0→V1.0.1→V1.0.2 封版，QA_PASS，Owner 决议 GK-KE-OWNER-001，L0-1 现状定位
- GK1 W3（当前）：TL 承接 L0-2 规划与派工 → **已收工**，Baton → feature_pilot
- GK1 W4：Feature Pilot 执行 WI-01/03/04
- GK1 W5：独立 QA 查冲突 → 相应 Owner 批准 → 激活（OC-01 收口）
