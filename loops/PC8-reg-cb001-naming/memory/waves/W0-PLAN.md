# W0｜Plan

## Goal

执行LOOP中受控门禁并保留可复核证据。

## Gates

以 `LOOP.yaml.gates` 为唯一命令源；禁止复制后漂移。

---

## 派工卡（TL 派发·W1）

| 项 | 内容 |
|---|---|
| 批次 | `PC8-reg-cb001-naming` |
| 实施角色 | `tech_lead` |
| 复核角色 | `independent_qa`（gate_review，独立） |
| 波次 | `W1` |
| 依赖 | 无 —— 独立取证，可并行 |

### 目标

1. 指名 REG-CB-001 所指文件（名称/文号/施行日）并取逐字全文；取不到则如实记 blocked（不以摘要冒充原文）
2. 更正台账 V1.0 已过时计数：AVAILABLE 6→9、PENDING 21→19、门禁 94/94→131/131
3. 登记 bytes/sha256 + 抓取凭据，clause_verified 保持 false（只由 Owner 核定）

### 交付物

- REG-CB-001 入库件或 blocked 记录 + 台账 V1.1 + 登记同步

### 完成判据（未绿不得交棒）

见 `LOOP.yaml.gates`（唯一命令源）；每条 gate 须经 `scripts/record_gate.py` 留证（actor/actor_role/executed_at/evidence_file/output_sha256）。

### 边界（越界即记 FAILURES）

不拼装、不静默替换、不以通知当条文；不替 Owner 裁定 D-R2（REG-FIN-002 条件性）

### 起手第一动作

先判定能否取得逐字全文的官方承载（公报/官方法规库全文页），取不到即记 blocked 并交回 Owner
