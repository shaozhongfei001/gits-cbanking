---
{"schemaVersion":"1.0.0","assetId":"ASSET-KNOW-KYC-QUESTION-LIBRARY","assetType":"KNOWLEDGE_RULE","name":"角色化KYC问题库","domain":"KD-CORP-RM","version":"0.1.0","status":"VALIDATION","source":{"type":"FILESYSTEM_MOCK","uri":"scenario/seed/05_knowledge/kyc_question_library.jsonl","authority":"SYNTHETIC","contentMode":"RETRIEVE","sourceVersionPolicy":"SCENARIO_PACKAGE_VERSION"},"governance":{"owner":"KYC知识Owner","classification":"INTERNAL","permissionInherit":"CALLER","allowedActions":["READ","QUERY"]},"capabilities":["按未知对象和客户角色生成访谈问题","支持KYC Gap补全"],"activation":{"mode":"RETRIEVE","adapter":"filesystem-knowledge-adapter","requiredParameters":["unknownObjects","contactRole"],"maxContextTokens":1600,"failurePolicy":"DEGRADE_WITH_DISCLOSURE"},"evidence":{"citationRequired":true,"sourceVersionRequired":true,"contentHashRequired":true},"relatedAssets":["ASSET-TOOL-SP05"],"limitations":["问题库不替代客户经理判断","不应重复询问已经确认的事实"]}
---

# 角色化KYC问题库

由Ontology-first识别未知对象后激活，而不是将全部问题库一次性装入上下文。
