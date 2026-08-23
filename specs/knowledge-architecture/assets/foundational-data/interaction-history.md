---
{"schemaVersion":"1.0.0","assetId":"ASSET-DATA-INTERACTION-HISTORY","assetType":"FOUNDATIONAL_DATA","name":"客户历史互动与原话","domain":"KD-CORP-RM","version":"0.1.0","status":"VALIDATION","source":{"type":"FILESYSTEM_MOCK","uri":"scenario/seed/06_interactions/historical_interactions.jsonl","authority":"SYNTHETIC","contentMode":"RETRIEVE","sourceVersionPolicy":"EVENT_TIME_AND_VERSION"},"governance":{"owner":"客户经营Owner","classification":"SENSITIVE","permissionInherit":"CALLER","allowedActions":["READ","QUERY"]},"capabilities":["读取历史互动、客户原话和未决事项","支持访前继承和事实对账"],"activation":{"mode":"RETRIEVE","adapter":"filesystem-interaction-adapter","requiredParameters":["customerId","permissionDecisionId","asOf"],"maxContextTokens":2600,"failurePolicy":"DEGRADE_WITH_DISCLOSURE"},"evidence":{"citationRequired":true,"sourceVersionRequired":true,"contentHashRequired":true},"relatedAssets":["ASSET-KNOW-EVIDENCE-POLICY"],"limitations":["客户原话必须与AI解释分层","未确认表达不得成为正式事实"]}
---

# 客户历史互动与原话

支持持续经营上下文继承；必须保留说话人、时间、互动ID和原文定位。
