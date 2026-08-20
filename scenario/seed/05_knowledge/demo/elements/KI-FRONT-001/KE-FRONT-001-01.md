---
{"schemaVersion": "1.0.0", "elementId": "KE-FRONT-001-01", "name": "上游供应商列表", "kind": "K-Type-F", "knowledgeItemId": "KI-FRONT-001", "content": "华东精工（CUST-CORP-0001）直接原材料/零部件供应商清单，每家展示企业全称、供应品类、近12个月采购额（万元）及占年总采购比例（%）、采购价格趋势（持平/上涨X%/下跌X%）。演示版绑定 06_interactions 交易流水与行内交易数据，拟态上游供应关系图谱。", "source": {"sourceRef": "行内交易流水（演示）+ 外部工商/产业数据", "authority": "AUTHORITATIVE"}, "status": "DRAFT", "scenarioBinding": {"customerId": "CUST-CORP-0001", "asOf": "2026-07-08"}}
---

# 上游供应商列表

华东精工（CUST-CORP-0001）直接原材料/零部件供应商清单，每家供应商展示：企业全称、供应品类、近 12 个月采购额（万元）及占年总采购比例（%）、采购价格趋势（持平/上涨/下跌）。

演示版通过本包内交易流水数据与工商数据接口拟态生成完整上游供应关系图谱，供 `SimulatedKnowledgeProvider` 装配"客户概况"任务。