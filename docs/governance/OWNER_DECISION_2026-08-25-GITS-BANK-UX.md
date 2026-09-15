# Owner Decision｜GITS Bank UX V3.2 与全周期施工规划

| 字段 | 值 |
|---|---|
| Decision ID | OD-GITS-BANK-UX-2026-08-25 |
| Date | 2026-08-25 |
| Role | HUMAN_OWNER（会话确认） |
| Recorded by | Tech Lead |
| Loop | P30-gits-bank-experience-shell |
| Production ready | NO |
| Frozen | NO |

## 决定

1. **两包进入基线**：施工规划包 V1.0 与设计需求包 V3.2 登记为 `specs/BASELINE_INDEX.yaml` 受控输入。状态为 `CONTROLLED_INPUT_NOT_FROZEN` / `DESIGN_CANDIDATE`，**不是** FROZEN，不是已实现。
2. **C3 授权契约候选**：C3 页/对象允许建立 `CONTRACT_CHANGE_CANDIDATE` 并进入评审。**不授权**修改 authority source、`CONTRACT_INDEX.yaml` 业务合同或 `generated/`。`AUTHORITY_SOURCE_CHANGE=NO` 直至 CCC 完成 CC2 签署。
3. **实施基线分支**：产品对照基线为 `origin/main@d3142c9557aaa197c41ef89343ec1e05b073d0a0`。工作分支为 `feature/P30-gits-bank-experience-shell`（从该提交创建）。禁止在 `feature/P24-dkws-supplychain` 上实施本 UX 重构。
4. **批准 P30 壳层 Loop**：范围限定 Experience Shell + 页面 P01–P03 **只读**。P03 分层拖动写回保持禁用。不实现 P04–P44 业务页，不实现 G0–G5 / Need / 移动离线写回。

## 明确未批准

- 受保护 GITS—DKES authority source 变更
- Feature 实现由本 Tech Lead 会话完成
- QA_PASS / SIT / UAT / PRODUCTION_READY / FROZEN
- 将 PNG 示例字段升级为正式枚举或状态机

## 权威顺序不变

Owner 本决定 > BASELINE_INDEX 受控输入 > 已批准 ADR > CONTRACT_INDEX > 当前 Loop > 实现 > V3.2 静态图。
