---
{"schemaVersion":"1.0.0","assetId":"ASSET-DATA-TRANSACTION-SUMMARY","assetType":"FOUNDATIONAL_DATA","name":"本行交易与余额摘要","domain":"KD-CORP-RM","version":"0.1.0","status":"VALIDATION","source":{"type":"FILESYSTEM_MOCK","uri":"scenario/seed/03_bank_data/monthly_transaction_summary.csv","authority":"SYNTHETIC","contentMode":"QUERY","sourceVersionPolicy":"AS_OF_REQUIRED"},"governance":{"owner":"交易数据Owner","classification":"RESTRICTED","permissionInherit":"CALLER","allowedActions":["QUERY"]},"capabilities":["识别本行交易变化","支持访前经营信号和资金节奏分析"],"activation":{"mode":"QUERY","adapter":"filesystem-transaction-adapter","requiredParameters":["customerId","permissionDecisionId","asOf"],"maxContextTokens":1600,"failurePolicy":"DEGRADE_WITH_DISCLOSURE"},"evidence":{"citationRequired":true,"sourceVersionRequired":true,"contentHashRequired":true},"relatedAssets":[],"limitations":["本行交易不代表客户全量现金流","不得将趋势直接升级为正式商机"]}
---

# 本行交易与余额摘要

只提供本行可见交易和余额变化，输出必须标注观察范围和截止时间。
