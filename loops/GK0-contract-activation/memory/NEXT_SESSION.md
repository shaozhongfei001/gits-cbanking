# GK0-contract-activation｜Next Session Baton

| 字段 | 值 |
|---|---|
| **Updated** | `2026-09-11` |
| **holder** | `owner_review` |
| **packet** | `GK0-contract-activation` |
| **wave** | `W2（Owner 决议）` |
| **do_not_start** | 无（V1.0.2 封版已 QA_PASS） |
| **review_result** | `QA_PASS`（封版 V1.0.2 / HEAD `886f710` / AC-01·02·03 全 PASS，session `qa-gk0-v102-reattest-001`） |

## 短提示词

独立 QA 二次复核已完成，结论 **QA_PASS**（范围：封版制品一致性 AC-01/02/03）。

新增证据：`loops/GK0-contract-activation/evidence/INDEPENDENT_QA-V1.0.2-REATTEST.md`
（sha256 `6d97a619047ad4835cdde0c292b709bcfbff8a831725931e239f5de083144d46`）
已写入 `EVIDENCE.json.independent_qa_v1_0_2`，绑定 `reviewed_head=886f710`。

**当前 Baton → owner**：四项 Owner 决议（TL/QA 均不得代签）：
1. metric 口径 `SIM.METRIC.CUSTOMER_AVG_DEPOSIT`（metric owner）
2. 知识认证（knowledge owner）
3. 地图任务价值（business owner）
4. 试点范围（domain owners）

**非阻断建议（供 Owner/TL 决策）**：
- 封版 ZIP 未纳入 git 跟踪，建议改为 `make package` 从 `886f710` tree 确定性重建，形成纯 git 内生证据链。
- `EVIDENCE.json.independent_qa`（旧记录，`reviewed_head=91d5fed`）保留不动；封版结论以 `independent_qa_v1_0_2` 为准。

## 交接历史

- W0：tech_lead 规划 → 架构委员会评审 RETURN_TO_HLD
- W1：feature_pilot 执行 WP-R4-1（6 合同源变更）→ independent_qa QA_PASS（HEAD 91d5fed）
- W1.5：架构委员会复审 PASS_WITH_REQUIRED_CHANGES → feature_pilot 修复分叉封版 V1.0.2（HEAD 886f710）→ independent_qa 二次复核 **QA_PASS**（session `qa-gk0-v102-reattest-001`）
- W2：owner 决议（**当前**）
