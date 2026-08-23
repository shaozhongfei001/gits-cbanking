---
{"schemaVersion":"1.0.0","assetId":"ASSET-RUN-EVALUATION","assetType":"RUNTIME_FEEDBACK","name":"评测与回归案例","domain":"KD-CORP-RM","version":"0.1.0","status":"VALIDATION","source":{"type":"EVALUATION_FILE","uri":"scenario/seed/09_skill_agent/eval_feedback.jsonl","authority":"DERIVED","contentMode":"REVIEW","sourceVersionPolicy":"EVAL_CASE_VERSION"},"governance":{"owner":"evaluation_owner","classification":"SENSITIVE","permissionInherit":"EXPLICIT","allowedActions":["READ","REVIEW"]},"capabilities":["将人工修改转化为回归用例","验证语义边界和低信息密度问题"],"activation":{"mode":"REVIEW","adapter":"filesystem-evaluation-adapter","requiredParameters":["evalCaseId","permissionDecisionId"],"maxContextTokens":1200,"failurePolicy":"OPTIONAL_SKIP"},"evidence":{"citationRequired":true,"sourceVersionRequired":true,"contentHashRequired":true},"relatedAssets":["ASSET-RUN-HUMAN-GATE"],"limitations":["样本使用须遵循脱敏和用途限制"]}
---

# 评测与回归案例

P20新增路由正确性、资产选择、权限、Semantic Query和ActivationPlan回放评测。
