# W0｜Plan

## Goal

执行LOOP中受控门禁并保留可复核证据。

## Gates

以 `LOOP.yaml.gates` 为唯一命令源；禁止复制后漂移。

---

## 派工卡（TL 派发·W4）

| 项 | 内容 |
|---|---|
| 批次 | `PC8-retrieval-endpoint` |
| 实施角色 | `tech_lead` |
| 复核角色 | `independent_qa`（gate_review，独立） |
| 波次 | `W4` |
| 依赖 | 依赖 PC8-tools-byproduct（需 Release/interpretation 产物） |

### 目标

1. 新增 POST /v1/retrieval/query（纯新增，暴露既有 retrieve_via_lightrag），响应带可回译出处与 evidenceClass/simulationOnly
2. 在既有 egress 白名单（03_core/04_serve）内灌入，产出索引基线（节点/边/体积）
3. 按 ADR-017 判据执行索引重建：清空⇒同集重灌⇒核对覆盖与出处一致；重建期 fail-closed 禁空结果

### 交付物

- 新端点 + 合同 diff + 灌入记录(索引基线) + 重建对照证据（出处集合 Jaccard）

### 完成判据（未绿不得交棒）

见 `LOOP.yaml.gates`（唯一命令源）；每条 gate 须经 `scripts/record_gate.py` 留证（actor/actor_role/executed_at/evidence_file/output_sha256）。

### 边界（越界即记 FAILURES）

不改 EGRESS_ROOTS；不把 01_raw 原文灌入；LightRAG 仅派生检索层——字段值不得取自检索

### 起手第一动作

先在 gits 侧出端点合同提案（含出处字段与 fail-closed 三码），经 Owner 签 CR-5 后动代码
