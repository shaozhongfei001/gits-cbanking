---
{"schemaVersion":"1.0.0","assetId":"ASSET-RUN-HUMAN-GATE","assetType":"RUNTIME_FEEDBACK","name":"Human Gate决策反馈","domain":"KD-CORP-RM","version":"0.1.0","status":"VALIDATION","source":{"type":"DECISION_LOG","uri":"scenario/seed/10_human_gates/human_gate_decisions.jsonl","authority":"DERIVED","contentMode":"REVIEW","sourceVersionPolicy":"DECISION_ID_AND_TIME"},"governance":{"owner":"human_action_owner","classification":"RESTRICTED","permissionInherit":"EXPLICIT","allowedActions":["READ","REVIEW"]},"capabilities":["记录接受、修改、拒绝和保持决定","形成评测和规则改进样本"],"activation":{"mode":"REVIEW","adapter":"filesystem-human-gate-adapter","requiredParameters":["gateId","permissionDecisionId"],"maxContextTokens":1400,"failurePolicy":"FAIL_CLOSED"},"evidence":{"citationRequired":true,"sourceVersionRequired":true,"contentHashRequired":true},"relatedAssets":["ASSET-RUN-EVALUATION"],"limitations":["决策日志不得被模型覆盖或改写"]}
---

# Human Gate决策反馈

用于Shadow比较和评测样本建设，不能作为模型自动批准依据。
