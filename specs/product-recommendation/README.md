# 产品解读与推荐 SDD 契约（候选）

文档状态：`CANDIDATE / FROZEN=NO / IMPLEMENTED=NO / REAL_E2E_PASS=NO`
权威基线：`V2.0 业务需求基线 + PB-V2.0-R1 + GITS 受保护合同`
KERT 运行时：`~/dev/Leibniz-KERT`(DKWS)，Gate 0 通过后以 `/api/skill/execute` 为真实执行契约。

## 1. 三个概念的关系（唯一权威口径）

- **产品解读** = 版本化知识能力：`ProductVersion → ProductInterpretationVersion`（KERT 主责）。回答"产品是什么、适合谁、条件/边界/材料/风险"，不做客户判断。
- **产品推荐** = 受控决策运行：`ProductRecommendationRun →（硬过滤 → 需求能力匹配 → 客户经理确认）→ ProductRecommendationProposalVersion → RecommendationDecision`。输出 = "产品适配/组合子方案"，不是完整建议书，不代表审批。
- **客户服务建议书** = 顶层对象：`Proposal → ProposalVersion（G0—G5）`，在 G2 消费已决定采用的推荐子方案，再补非产品服务/专家/风险/价值/行动/双版本/正式审批。

唯一权威链：
`Need(唯一ID/版本) → ProductRecommendationRun(ID) → ProductRecommendationProposalVersion(ID) → Product/ProductVersion(ID) → Rule/Model快照(Hash) → EvidenceBundle(ID+Hash) → RecommendationHumanDecision(decision=RecommendationDecision + actor + time + reason) → ProposalVersion 引用该子方案 → G3 正式审批`

命名说明：`RecommendationHumanDecision` 是人工决定的**记录对象**（gateId/runId/proposalVersionId/decision/modifications/reason/actor/decidedAt）；`RecommendationDecision` 是其**决策值枚举**（`APPROVE/MODIFY/REJECT/HOLD`）。两者不混用。

## 2. 不变量（机器可测）

```text
INV-01 Active(ProductVersion)=false → 不得进入正式候选
INV-02 Eligibility=INELIGIBLE → rankScore/fitScore 必须为 null
INV-03 Eligibility=UNKNOWN → 不得按 ELIGIBLE 处理
INV-04 CandidateReason → 至少一条 EvidenceRef
INV-05 HardRule → 一个已批准 Owner + 一个权威来源
INV-06 HumanDecision.proposalVersionId = 当前 proposalVersionId
INV-07 KERT 不可达 → 禁止本地生产推荐回退（fail-closed）
INV-08 ProductVersion/RuleVersion 变化 → 下游 STALE（不自动删除）
INV-09 AI 输出 → 不得直接创建授信/定价/审批/写回动作
INV-10 权威证据冲突 → 禁止确定性解读
```

## 3. 状态命名空间分离（不得混用）

| 命名空间 | 值 |
|---|---|
| Claim/Fact | `F/C/B/H`、`VERIFIED/CONFLICT/UNKNOWN` |
| Need | `VERIFIED_FACT/HUMAN_CONFIRMED/INFERRED_NEED/UNKNOWN/CONFLICT` |
| Eligibility | `ELIGIBLE/INELIGIBLE/UNKNOWN/REVIEW_REQUIRED` |
| Recommendation Run | `REQUESTED…FAILED_CLOSED`（见 run schema） |
| Recommendation Decision | `APPROVE/MODIFY/REJECT/HOLD`（D01 范围） |
| Proposal Gate | `G0—G5` |
| Formal Approval | 授信/价格/产品/合规各自状态 |

禁止：把 `APPROVE` 显示为"产品已批准/建议书已审批"；把 `ELIGIBLE` 当授信通过；把 `G3` 当一切子审批完成；把客户已查看建议书写成 `G5`。

## 4. KERT 错误码 → GITS 处理映射

| KERT 错误码 | 语义 | GITS 处理 |
|---|---|---|
| `KERT_PERMISSION_DENIED` | 权限不允许 | run=`FAILED_CLOSED`，不重试 |
| `KERT_CONTEXT_INSUFFICIENT` | 必须事实不足 | run=`HELD`，生成核实任务 |
| `KERT_PRODUCT_KNOWLEDGE_STALE` | 产品知识版本失效 | run=`FAILED_CLOSED`，通知知识 Owner |
| `KERT_RULE_VERSION_MISSING` | 规则不可复现 | run=`FAILED_CLOSED` |
| `KERT_EXECUTION_TIMEOUT` | 技术超时 | 保留 attempt，可按策略重试，不启用本地推荐 |
| `KERT_CONTRACT_MISMATCH` | 输入/输出不符合同 | run=`FAILED_CLOSED`，触发契约告警 |
| `KERT_EVIDENCE_INCOMPLETE` | 结果缺乏必要证据 | 不创建 HG-D01 |
| `KERT_INTERNAL_ERROR` | 未分类技术错误 | 技术重试后仍失败则关闭本轮 |

## 5. 旧实现处置（迁移，非删除）

- `ProductMatchingService` + `POST /customer/{id}/product-matching` + 前端 `matchProducts`：保留兼容期 + 弃用标记 + 调用量监控；生产切换后不作为 KERT 失败回退；最终删除走消费者清零门禁。
- `ProductMatch` 三方漂移：OpenAPI=`productId/productName/matchScore/matchReasons[]/productCategory`；Java=`productId/productName/reason/confidence/signal`；前端=两者并集。新链路用本目录独立 schema，不在旧字段上继续堆新字段；旧端点保留兼容，待消费者清零后退役。
- `REJECT` vs `DECLINE` 双语义：待 HumanGate Contract Owner 裁决；未裁决前前端不得自行解释。

## 6. 文件清单

| 文件 | 责任 |
|---|---|
| `product-recommendation-run.schema.json` | Run 状态机/版本/attempt/快照 |
| `eligibility-result.schema.json` | 第一段四态硬过滤 |
| `product-fit-result.schema.json` | 第二段分维度匹配/排序 |
| `portfolio-candidate.schema.json` | 核心/配套/依赖/互斥/顺序 |
| `recommendation-result.schema.json` | KERT 完整输出 + 证据/哈希 |
| `recommendation-human-decision.schema.json` | 结构化人工决定 |
| `../knowledge-architecture/activations/AC-PRODUCT-RECOMMEND-001.json` | 推荐任务激活合同 |
| `../openapi/product-recommendation.openapi.json` | vNext 推荐端点（增量，独立文档） |
