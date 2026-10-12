# W0｜Plan

## Goal

执行LOOP中受控门禁并保留可复核证据。

## Gates

以 `LOOP.yaml.gates` 为唯一命令源；禁止复制后漂移。

---

## 派工卡（TL 派发·W1）

| 项 | 内容 |
|---|---|
| 批次 | `PC8-src-batch-b4b6` |
| 实施角色 | `feature_pilot` |
| 复核角色 | `independent_qa`（gate_review，独立） |
| 波次 | `W1` |
| 依赖 | 无 —— 可与 PC8-tools-byproduct / PC8-reg-cb001-naming 并行 |

### 目标

1. 按既有 DEMO 演示轨（registry §5.8）补齐 B4 贸易金融 3 份、B5 跨境 2 份、B6 投行 1 份，格式逐字对齐已入库源
2. 同批登记：§5.8 明细/红线/入库记录(hash 实测)/汇总句/EXPECTED_DEMO，并过既有登记铁闸
3. 保持判据单点：与在库真实监管源分工，法定要件一律引 REG-* 不抄条文

### 交付物

- 6 份 SRC-*.DEMO.md + registry 登记 + 门禁通过记录

### 完成判据（未绿不得交棒）

见 `LOOP.yaml.gates`（唯一命令源）；每条 gate 须经 `scripts/record_gate.py` 留证（actor/actor_role/executed_at/evidence_file/output_sha256）。

### 边界（越界即记 FAILURES）

不手写 02_work/* 与 04_serve/* 流水线产物；不新增 usage/区（第三轨已撤回）；产品+合规确认未做 ⇒ 不得对客引用

### 起手第一动作

先读 registry §5.4/§5.5/§5.6 与在库 REG-TF-001/002/003、REG-CB-002 的分工，再落 B4（SRC-TF-001/002/003）
