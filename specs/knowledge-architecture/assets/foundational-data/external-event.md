---
{"schemaVersion":"1.0.0","assetId":"ASSET-DATA-EXTERNAL-EVENT","assetType":"FOUNDATIONAL_DATA","name":"外部市场与企业事件","domain":"KD-CORP-RM","version":"0.1.0","status":"VALIDATION","source":{"type":"FILESYSTEM_MOCK","uri":"scenario/seed/04_external_data/external_events.jsonl","authority":"SYNTHETIC","contentMode":"RETRIEVE","sourceVersionPolicy":"EVENT_TIME_AND_LICENSE"},"governance":{"owner":"行业研究Owner","classification":"INTERNAL","permissionInherit":"CALLER","allowedActions":["READ","QUERY"]},"capabilities":["发现行业、政策和企业事件","为客户经营提供Signal候选"],"activation":{"mode":"RETRIEVE","adapter":"mock-rag-adapter","requiredParameters":["industry","asOf"],"maxContextTokens":2400,"failurePolicy":"OPTIONAL_SKIP"},"evidence":{"citationRequired":true,"sourceVersionRequired":true,"contentHashRequired":true},"relatedAssets":["ASSET-KNOW-EVIDENCE-POLICY"],"limitations":["外部事件只能形成Signal候选","必须执行客户和主体映射确认"]}
---

# 外部市场与企业事件

适合Wiki-first发现，再通过本体进行实体归一和客户关联。
