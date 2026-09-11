# GK0-contract-activation｜Next Session Baton

| 字段 | 值 |
|---|---|
| **Updated** | `2026-09-12` |
| **holder** | `owner_review` |
| **packet** | `GK0-contract-activation` |
| **wave** | `W2（Owner 决议）` |
| **do_not_start** | 无（V1.0.2 封版已 QA_PASS） |
| **review_result** | `PASS_FOR_OWNER_REVIEW`（封版 V1.0.2 / HEAD `886f710` / AC-01·02·03 全 PASS，session `qa-gk0-v102-reattest-001`） |

## 短提示词

D 阶段门禁已提升为 **PASS_FOR_OWNER_REVIEW**，独立 QA 二次复核 QA_PASS（封版制品一致性 AC-01/02/03）。

**当前 Baton → owner_review**：四项 Owner 决议（TL/QA 均不得代签）。
派工提示词：`docs/dd/GITS-KERT_Owner决议派工提示词_V1.0.md`（四 Owner 可并行，各司其职）：

1. metric 口径 `SIM.METRIC.CUSTOMER_AVG_DEPOSIT`（metric owner）— C04 §3 / C08 L2-1
2. 知识认证（knowledge owner）— C08 CR-04 / C08 §3
3. 地图任务价值（business owner）— C08 §3 / L4-1·L4-2
4. 试点范围（domain owners）— C08 L6 / CR-08 / §5

**非阻断建议（供 Owner/TL 决策）**：
- 封版 ZIP 未纳入 git 跟踪，建议改为 `make package` 从 `886f710` tree 确定性重建，形成纯 git 内生证据链。
- `EVIDENCE.json.independent_qa` 已同步为封版 `886f710` 结论（supersedes `91d5fed`），`independent_qa_v1_0_2` 保留作历史明细。

## 交接历史

- W0：tech_lead 规划 → 架构委员会评审 RETURN_TO_HLD
- W1：feature_pilot 执行 WP-R4-1（6 合同源变更）→ independent_qa QA_PASS（HEAD 91d5fed）
- W1.5：架构委员会复审 PASS_WITH_REQUIRED_CHANGES → feature_pilot 修复分叉封版 V1.0.2（HEAD 886f710）→ independent_qa 二次复核 **QA_PASS**（session `qa-gk0-v102-reattest-001`）
- W2：D 门禁 PASS_FOR_OWNER_REVIEW → owner 决议（**当前**）
