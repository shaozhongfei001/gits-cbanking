# W0｜Plan

## Goal

执行LOOP中受控门禁并保留可复核证据。

## Gates

以 `LOOP.yaml.gates` 为唯一命令源；禁止复制后漂移。

---

## 派工卡（TL 派发·W1）

| 项 | 内容 |
|---|---|
| 批次 | `PC8-tools-byproduct` |
| 实施角色 | `tech_lead` |
| 复核角色 | `independent_qa`（gate_review，独立） |
| 波次 | `W1` |
| 依赖 | 改造无依赖；跑全链依赖 PC8-src-batch-b4b6 完成（源集齐） |

### 目标

1. 消除 tools/l11|l12|l13 的 PRODUCT_ID 常量硬编码，改为 --product/--all 参数化（不改判定逻辑）
2. 用 13 张产品卡跑通 l10→l11→l12→l13 全链，产出逐卡 candidate-card/conflicts/health/interpretation/rule-package
3. 保持既有产物字节不变性（PROD-CM-001 重跑结果与现库一致，除非演进被显式记录）

### 交付物

- tools/l1{1,2,3}_*.py 参数化 + 13 卡 02_work/04_serve 产物 + 字节不变性对照证据

### 完成判据（未绿不得交棒）

见 `LOOP.yaml.gates`（唯一命令源）；每条 gate 须经 `scripts/record_gate.py` 留证（actor/actor_role/executed_at/evidence_file/output_sha256）。

### 边界（越界即记 FAILURES）

不改任何合同 schema/不变式；不扩 EGRESS_ROOTS；90_control/decisions 未签署时 Release 只能 DRAFT（不得伪 PUBLISHED）

### 起手第一动作

先出「硬编码点清单 + 参数化最小 diff + 字节不变性对照方案」，经 TL 复核后再改代码
