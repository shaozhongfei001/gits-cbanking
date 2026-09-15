# CONTRACT_CHANGE_CANDIDATE 登记册｜GITS Bank V3.2 C3

> Owner 决定 `OD-GITS-BANK-UX-2026-08-25` 授权**形成候选并评审**。  
> `AUTHORITY_SOURCE_CHANGE=NO`。`IMPLEMENTATION_DEPENDENCY=NO`（P30 不得实现这些正式对象）。

| Candidate ID | 对象族 | 页 | 现有合同 | 状态 |
|---|---|---|---|---|
| CCC-GITS-BANK-20260825-001 | 客户组合/分层写回 | P03 | CTR-API-001 Customer 查询 | REVIEW |
| CCC-GITS-BANK-20260825-002 | 集团关系核验写 | P05 | CTR-API-001 展示派生 | REVIEW |
| CCC-GITS-BANK-20260825-003 | Need / ServicePlan | P20–P22, P24 | Claim / KYC / Opportunity 片段 | REVIEW |
| CCC-GITS-BANK-20260825-004 | 建议书工厂 G0–G5 / 投影 / 版本 | P25–P30 | HumanGate；无 G0–G5 schema | REVIEW |
| CCC-GITS-BANK-20260825-005 | 专家协同记录 | P31 | 无 | REVIEW |
| CCC-GITS-BANK-20260825-006 | 对客交付包 | P33 | 无 DeliveryPackage | REVIEW |
| CCC-GITS-BANK-20260825-007 | 账户计划 / 价值实现 | P34–P35 | Task/Commitment 不能替代 | REVIEW |
| CCC-GITS-BANK-20260825-008 | 产品适用边界写回 | P38 | CTR-KELEM-001 只读 | REVIEW |
| CCC-GITS-BANK-20260825-009 | 移动缓存 / 撤权 / 同步 | P41–P44 | 无 | REVIEW |

零变更时 P30 对 P03 的处理：看板只读，禁用拖动写回（C2），等待上表 CC2 签署后才允许独立 Contract Loop 改源。

模板：`docs/dd` 规划包 `08_CONTRACT_CHANGE_CANDIDATE_模板.md`（参考区副本）。详细 Before/After 由后续 Contract Loop 填写，不在 P30 Feature 范围。
