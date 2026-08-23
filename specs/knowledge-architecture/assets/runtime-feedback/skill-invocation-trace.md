---
{"schemaVersion":"1.0.0","assetId":"ASSET-RUN-SKILL-TRACE","assetType":"RUNTIME_FEEDBACK","name":"Skill调用轨迹","domain":"KD-CORP-RM","version":"0.1.0","status":"VALIDATION","source":{"type":"TRACE_FILE","uri":"scenario/seed/09_skill_agent/skill_invocation_trace.jsonl","authority":"DERIVED","contentMode":"REVIEW","sourceVersionPolicy":"CALL_ID"},"governance":{"owner":"SkillOps Owner","classification":"SENSITIVE","permissionInherit":"EXPLICIT","allowedActions":["READ","REVIEW"]},"capabilities":["追踪Skill输入、输出、策略和Human Gate","支持资产激活回放"],"activation":{"mode":"REVIEW","adapter":"filesystem-trace-adapter","requiredParameters":["callId","permissionDecisionId"],"maxContextTokens":1600,"failurePolicy":"OPTIONAL_SKIP"},"evidence":{"citationRequired":true,"sourceVersionRequired":true,"contentHashRequired":true},"relatedAssets":[],"limitations":["现有input_refs为静态绑定，P20后应来自ActivationPlan"]}
---

# Skill调用轨迹

新轨迹必须记录ActivationPlan ID、资产版本、Semantic Query ID和裁剪信息。
