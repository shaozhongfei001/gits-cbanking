---
{"schemaVersion":"1.0.0","assetId":"ASSET-KNOW-EVIDENCE-POLICY","assetType":"KNOWLEDGE_RULE","name":"证据分层与引用策略","domain":"KD-CORP-RM","version":"0.1.0","status":"VALIDATION","source":{"type":"POLICY_FILE","uri":"scenario/seed/05_knowledge/evidence_policy.yaml","authority":"REFERENCE","contentMode":"READ","sourceVersionPolicy":"FILE_VERSION"},"governance":{"owner":"evidence_owner","classification":"INTERNAL","permissionInherit":"CALLER","allowedActions":["READ","REVIEW"]},"capabilities":["区分Fact、Claim、Finding、Signal和Pending Confirmation","定义证据充分度和引用要求"],"activation":{"mode":"READ","adapter":"filesystem-policy-adapter","requiredParameters":[],"maxContextTokens":1000,"failurePolicy":"FAIL_CLOSED"},"evidence":{"citationRequired":true,"sourceVersionRequired":true,"contentHashRequired":true},"relatedAssets":[],"limitations":["现有文件含参考性方法，非杭州银行现行制度"]}
---

# 证据分层与引用策略

所有ActivationPlan和Skill输出都必须遵守此策略，并保留未知项和冲突项。
