# 独立架构复核处理回执（F-01~F-05）

复核来源：`docs/dd/ONTO1_准备包独立架构复核_20260921.md`（架构顾问复核，**不代替独立 QA**）。

| 发现 | 处理 | 证据 |
|---|---|---|
| **F-01** 制品保留「处置率 100%」 | ✅ 生成源改**数据驱动**（实测未闭环聚合行 **412** 内嵌禁止句）；新增 **P7**：未闭环非零却声称 100% ⇒ FAIL | `SOURCE/scripts/onto1_construction_plan.py` · `DELIVERABLES/ONTO1-CONSTRUCTION-PLAN-DRAFT.md` |
| **F-02** 自检只比脚本常量 | ✅ 改为**解析受控源文档**（设计 §4.2 / 映射表 / 归属矩阵）；候选由数据推导；**设计表/映射表/归属矩阵各一处真实变异**均被拦下（M1/M2/M3） | `SOURCE/scripts/onto1_class_reconciliation.py` · `DELIVERABLES/32-classes-target-mapping.json` |
| **F-03** 入口引 V1.2 且称 32 类为 L1 候选 | ✅ 改引 **V2.0 §4.2**；入口明示「来源盘点(32) ≠ L1 候选(8)」 | `DELIVERABLES/README.md` · `l1-term-inventory.json` |
| **F-04** 48 项 vs 封包 45 项 | ✅ **同快照重封**（本 R2 包）；新增门禁逐条列名/日志/退出码/环境 | 本文件 · `GATE-DELTA.md` · `RESULTS.md` |
| **F-05** 扫描与 KERT 归因不可独立确认 | ✅ 入包**原始** `consumer-scan-hits.jsonl` + 扫描脚本 + 双仓边界；「零写入证明」→ **KERT 差异观察（归因未核实）**，纳入工作区路径并声明归因限度 | `EVIDENCE/.../consumer-scan-hits.jsonl` · `KERT-DIFF-OBSERVATION.json` |

## 评审边界（F-05）
1. 入包原始扫描数据 `consumer-scan-hits.jsonl`（**26,690** 命中行）；**扫描覆盖率**与**逐条处置完整性**仍需在有双仓源码的环境复算。
2. KERT 归因**未核实**：需**本轮开始时的 KERT 工作区哈希快照**方可闭合；本包不作归因断言。

## 非声明
不构成 QA_PASS / 委员会批准 / 正式根域 / 生产激活；**Wave 2 仍禁止开工**（WI-A2 处置未达 100%）。
