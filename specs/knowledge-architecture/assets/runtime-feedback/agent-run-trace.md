---
{"schemaVersion":"1.0.0","assetId":"ASSET-RUN-AGENT-TRACE","assetType":"RUNTIME_FEEDBACK","name":"Agent运行轨迹","domain":"KD-CORP-RM","version":"0.1.0","status":"VALIDATION","source":{"type":"TRACE_FILE","uri":"scenario/seed/09_skill_agent/agent_run_trace.json","authority":"DERIVED","contentMode":"REVIEW","sourceVersionPolicy":"RUN_ID"},"governance":{"owner":"AgentOps Owner","classification":"SENSITIVE","permissionInherit":"EXPLICIT","allowedActions":["READ","REVIEW"]},"capabilities":["回放Agent步骤、模式和副作用","支持Shadow差异分析"],"activation":{"mode":"REVIEW","adapter":"filesystem-trace-adapter","requiredParameters":["runId","permissionDecisionId"],"maxContextTokens":1800,"failurePolicy":"OPTIONAL_SKIP"},"evidence":{"citationRequired":true,"sourceVersionRequired":true,"contentHashRequired":true},"relatedAssets":["ASSET-RUN-SKILL-TRACE"],"limitations":["P20现有记录为STATIC_SYNTHETIC_RUN"]}
---

# Agent运行轨迹

P20需要在此基础上增加知识地图、路由策略和ActivationPlan版本。
