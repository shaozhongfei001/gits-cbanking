---
{"schemaVersion":"1.0.0","assetId":"ASSET-KNOW-VISIT-SOP","assetType":"KNOWLEDGE_RULE","name":"拜访与离场确认SOP","domain":"KD-CORP-RM","version":"0.1.0","status":"VALIDATION","source":{"type":"PROCEDURE_FILE","uri":"scenario/seed/05_knowledge/visit_sop.yaml","authority":"REFERENCE","contentMode":"READ","sourceVersionPolicy":"FILE_VERSION"},"governance":{"owner":"客户经营方法Owner","classification":"INTERNAL","permissionInherit":"CALLER","allowedActions":["READ","REVIEW"]},"capabilities":["提供访前、访中、访后作业步骤","约束离场确认和后续跟进"],"activation":{"mode":"READ","adapter":"filesystem-policy-adapter","requiredParameters":["journeyPhase"],"maxContextTokens":1000,"failurePolicy":"OPTIONAL_SKIP"},"evidence":{"citationRequired":true,"sourceVersionRequired":true,"contentHashRequired":true},"relatedAssets":["ASSET-TOOL-SP10"],"limitations":["参考性方法，不自动视为银行现行制度"]}
---

# 拜访与离场确认SOP

用于Wiki-first任务指导；涉及客户事实和承诺时必须回到运营对象和Human Gate。
