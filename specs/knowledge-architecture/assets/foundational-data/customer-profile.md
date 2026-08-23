---
{"schemaVersion":"1.0.0","assetId":"ASSET-DATA-CUSTOMER-PROFILE","assetType":"FOUNDATIONAL_DATA","name":"客户基础画像","domain":"KD-CORP-RM","version":"0.1.0","status":"VALIDATION","source":{"type":"FILESYSTEM_MOCK","uri":"scenario/seed/02_master_data/customer_master.json","authority":"SYNTHETIC","contentMode":"RUNTIME_FETCH","sourceVersionPolicy":"SCENARIO_PACKAGE_VERSION"},"governance":{"owner":"客户主数据Owner","classification":"SENSITIVE","permissionInherit":"CALLER","allowedActions":["READ","QUERY"]},"capabilities":["获取客户名称、行业、规模、等级和管户关系","提供客户上下文装配入口"],"activation":{"mode":"QUERY","adapter":"filesystem-customer-adapter","requiredParameters":["customerId","permissionDecisionId","asOf"],"maxContextTokens":1800,"failurePolicy":"FAIL_CLOSED"},"evidence":{"citationRequired":true,"sourceVersionRequired":true,"contentHashRequired":true},"relatedAssets":["ASSET-KNOW-CUSTOMER-ONTOLOGY"],"limitations":["P20为合成场景数据","不得视为真实客户主数据"]}
---

# 客户基础画像

用于定位客户关系和基础经营上下文。MD仅保存使用说明，客户内容在运行时按客户ID和权限读取。
