---
{"schemaVersion":"1.0.0","assetId":"ASSET-KNOW-PRODUCT-CARDS","assetType":"KNOWLEDGE_RULE","name":"产品知识卡与版本","domain":"KD-CORP-RM","version":"0.1.0","status":"VALIDATION","source":{"type":"FILESYSTEM_MOCK","uri":"scenario/seed/05_knowledge/product_knowledge_cards.yaml","authority":"SYNTHETIC","contentMode":"RETRIEVE","sourceVersionPolicy":"ACTIVE_VERSION_ONLY"},"governance":{"owner":"公司金融产品管理部","classification":"INTERNAL","permissionInherit":"CALLER","allowedActions":["READ","QUERY"]},"capabilities":["提供产品用途、条件、材料和风险点","支持产品候选解释"],"activation":{"mode":"RETRIEVE","adapter":"mock-rag-adapter","requiredParameters":["productIntent","asOf"],"maxContextTokens":2200,"failurePolicy":"DEGRADE_WITH_DISCLOSURE"},"evidence":{"citationRequired":true,"sourceVersionRequired":true,"contentHashRequired":true},"relatedAssets":["ASSET-TOOL-SP15"],"limitations":["只使用ACTIVE版本","产品候选不代表审批或定价承诺"]}
---

# 产品知识卡与版本

建议由本体和规则先缩小候选范围，再定向加载相关产品卡，避免全量产品知识进入上下文。
