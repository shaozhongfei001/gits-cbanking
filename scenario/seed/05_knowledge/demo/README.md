# 演示知识资产（xlsx 标准版）

本目录为 `scenario/execute` 升级后的"模拟访问知识的数据提供者（SimulatedKnowledgeProvider）"
的演示数据源，数据组织方式遵循《银行知识工程规范打样_fixed.xlsx / 智能访前作战单》标准
（任务定义 → 任务资产依赖 → 知识条目 KI → 知识要素 KE → 规则库 RUL）。

## 与其它目录的关系

| 路径 | 角色 |
|------|------|
| `specs/knowledge-architecture/` | 受控生产知识资产（权威 SSOT，不在此编辑） |
| `scenario/seed/05_knowledge/` | V1.1 业务数据（客户、授信、交易、产品卡片等） |
| `scenario/seed/05_knowledge/demo/` | **本目录**：按 xlsx 标准组织的演示知识资产（影子/演示数据源） |

`demo/` 是影子/演示数据源：它模拟一个"知识服务"，被 `SimulatedKnowledgeProvider`
读取后，复现生产 P23 `KnowledgeAssembler` 的"先读知识地图 → 按地图任务装配知识条目(KI→KE→RUL)"
装配行为，供演示与影子环境使用。`demo/` 不进入受控 `specs/`，字段与受控资产对齐，不发明合同字段。

## 资产清单

- `knowledge-map.yaml` — 知识地图（含 scope、任务列表）
- `tasks.yaml` — 任务定义（对齐 TASK-FRONT-000~007）
- `activation-contract.json` — 激活合同 AC-PREVISIT-DEMO（scope→任务→KI 映射）
- `elements/` — 知识条目 KI / 知识要素 KE
- `rules.yaml` — 规则库 RUL

## 数据绑定

演示知识条目绑定到 `06_interactions` / `01_story` 中的张伟（RM-ZW-001 / CUST-CORP-0001 华东精工）
访前叙事，使"读图→装配"产出贴近真实业务演示素材。