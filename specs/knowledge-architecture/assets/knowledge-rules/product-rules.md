---
{"schemaVersion":"1.0.0","assetId":"ASSET-KNOW-PRODUCT-RULES","assetType":"KNOWLEDGE_RULE","name":"产品适配规则包","domain":"KD-CORP-RM","version":"0.1.0","status":"VALIDATION","source":{"type":"FILESYSTEM_MOCK","uri":"Leibniz-KERT/examples/product-recommendation-assets/04_serve/rule-packages/PROD-CM-001.rule-package.json","authority":"SYNTHETIC","contentMode":"RETRIEVE","sourceVersionPolicy":"ACTIVE_VERSION_ONLY"},"governance":{"owner":"公司金融产品管理部","classification":"INTERNAL","permissionInherit":"CALLER","allowedActions":["READ","QUERY"]},"capabilities":["承载产品版本生效性、候选非审批、准入硬过滤与组合冲突检查规则","为 SP-15 产品适配与综合方案提供规则依据"],"activation":{"mode":"RETRIEVE","adapter":"kert-rule-package-adapter","requiredParameters":["productIntent","asOf"],"maxContextTokens":1200,"failurePolicy":"FAIL_CLOSED"},"evidence":{"citationRequired":true,"sourceVersionRequired":true,"contentHashRequired":true},"relatedAssets":["ASSET-KNOW-PRODUCT-CARDS"],"limitations":["规则包当前为空包（status=NOT_BUILT），不得据此判定任何准入或适配结论","空包必须触发 FAIL_CLOSED，不得退化为本地兜底","产品规则内容须由产品管理部与风险部共同签署后方可置为 BUILT"]}
---

# 产品适配规则包

本资产承载 SP-15（产品适配与综合方案，`implementationType=RULE_MODEL`）所需的规则依据，
对应其 `ruleDependencies`：

| 规则 | 作用 | 当前状态 |
|---|---|---|
| `PRODUCT_VERSION_ACTIVE` | 只使用 ACTIVE 版本的产品知识 | NOT_BUILT |
| `CANDIDATE_NOT_APPROVAL` | 候选产品不等于审批或定价承诺 | NOT_BUILT |
| `ELIGIBILITY_HARD_FILTER` | 准入硬过滤 | NOT_BUILT |
| `PORTFOLIO_CONFLICT_CHECK` | 组合冲突检查 | NOT_BUILT |

## 为什么先建资产再建规则

`SP-15.json` 早已声明依赖 `ASSET-KNOW-PRODUCT-RULES`，但资产清单中从未注册，
导致 `knowledge-architecture-check` 失败（`unknown asset dependency`）。
先补齐资产登记，是为了让"规则未建设"这件事**显式可见**，
而不是让契约假装不需要规则 —— 后者会让调用方误以为产品适配可以不依赖规则得出结论。

## 空包约束（红线）

规则包当前 `status=NOT_BUILT`、`rules=[]`。因此：

1. 任何依赖本资产的技能（SP-15）在规则包为空时**必须受控失败**，
   不得退化为模型推断或本地兜底；
2. 产品解读链路中对应的 `rulePackageHash` 只表示**包容器的内容哈希**，
   不代表规则已生效；
3. 规则内容须由产品管理部与风险部共同签署后方可将 `status` 置为 `BUILT`。

## 与产品卡的边界

- `ASSET-KNOW-PRODUCT-CARDS`：产品**是什么**（用途、条件、材料、风险点）
- `ASSET-KNOW-PRODUCT-RULES`：产品**怎么筛**（版本、审批、准入、冲突）

两者不可互相替代，也不得双写同一份判断逻辑。
