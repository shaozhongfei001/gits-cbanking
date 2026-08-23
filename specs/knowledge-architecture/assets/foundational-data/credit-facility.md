---
{"schemaVersion":"1.0.0","assetId":"ASSET-DATA-CREDIT-FACILITY","assetType":"FOUNDATIONAL_DATA","name":"授信额度与提款事实","domain":"KD-CORP-RM","version":"0.1.0","status":"VALIDATION","source":{"type":"FILESYSTEM_MOCK","uri":"scenario/seed/03_bank_data/credit_facilities.csv","authority":"SYNTHETIC","contentMode":"QUERY","sourceVersionPolicy":"SCENARIO_PACKAGE_VERSION"},"governance":{"owner":"授信数据Owner","classification":"RESTRICTED","permissionInherit":"CALLER","allowedActions":["QUERY"]},"capabilities":["查询已批额度、可用额度和期限","支持额度、提款和新增需求语义区分"],"activation":{"mode":"QUERY","adapter":"filesystem-credit-adapter","requiredParameters":["customerId","permissionDecisionId","asOf"],"maxContextTokens":1600,"failurePolicy":"FAIL_CLOSED"},"evidence":{"citationRequired":true,"sourceVersionRequired":true,"contentHashRequired":true},"relatedAssets":["ASSET-KNOW-CLAIM-RECONCILIATION"],"limitations":["可用额度不等于提款额度或新增授信需求"]}
---

# 授信额度与提款事实

用于精确事实对账；必须与客户原话、提款记录、项目主体和用途信息分开解释。
