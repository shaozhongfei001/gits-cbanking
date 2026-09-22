# W0｜Plan

## Goal

执行LOOP中受控门禁并保留可复核证据。

## Gates

以 `LOOP.yaml.gates` 为唯一命令源；禁止复制后漂移。

---

## 派工卡（TL 派发·W5）

| 项 | 内容 |
|---|---|
| 批次 | `PC8-interpretation-e2e` |
| 实施角色 | `feature_pilot` |
| 复核角色 | `independent_qa`（gate_review，独立） |
| 波次 | `W5` |
| 依赖 | 依赖 PC8-tools-byproduct 与 PC8-retrieval-endpoint |

### 目标

1. 把 13 卡的 interpretation 三视图投影接到解读页 8 章（overview/terms/fit/process/materials/pricing/compare/faq）
2. 检索出处（docId/chunkId）回填到条款定位区，标注 evidenceClass/simulationOnly
3. DEMO 源编译的卡必须显示演示标识且不得进入 RECOMMENDATION_READY

### 交付物

- 8 章联调记录 + 出处回填样本 + DEMO 标识与 RECOMMENDATION 阻断证据

### 完成判据（未绿不得交棒）

见 `LOOP.yaml.gates`（唯一命令源）；每条 gate 须经 `scripts/record_gate.py` 留证（actor/actor_role/executed_at/evidence_file/output_sha256）。

### 边界（越界即记 FAILURES）

不改「产品解读与知识」既有代码范围外的模块；字段值仍来自受控知识版本；不对客声明已验收

### 起手第一动作

等前序 loop 交出 interpretation 产物后开工；先出 8 章↔三视图字段映射表
