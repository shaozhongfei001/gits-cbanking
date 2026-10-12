# 变异记录（真实运行输出，未人工誊写）

> **命名提示**：脚本内的检查标签 `R1`~`R7`/`M1`~`M8` 与**包版本号**（R2/R3/R4）**无关**，避免误读。

命令：`python3 <脚本> --selftest`（每条的首行即退出码）

## L1/设计源变异 —— `scripts/onto1_class_reconciliation.py`（exit=0）

```
PASS [M0 对照] 现状 7/7 = True
PASS [M1 变异设计表 §4.2] 被拦下 = ['R3 候选集合 == **设计 §4.2 解析结果**']
PASS [M2 变异映射表（L1→L3）] 被拦下 = ['R2 L1 候选恰为 8 类', 'R3 候选集合 == **设计 §4.2 解析结果**']
PASS [M3 变异归属矩阵（L1→L2）] 被拦下 = ['R2 L1 候选恰为 8 类', 'R3 候选集合 == **设计 §4.2 解析结果**']
PASS [M4 还原对照] 7/7 = True
--selftest PASS（5/5）
```

## P7 处置口径变异 —— `scripts/onto1_construction_plan.py`（exit=0）

```
PASS [M0 对照] 五份制品一致 = True（ONTO1-CONSTRUCTION-PLAN-DRAFT.md:一致性 OK；construction-plan.json:全部字段一致；ONTO1-CONTRACT-SPLIT-CANDIDATES-DRAFT.md:一致性 OK；contract-split-candidates.json:全部字段一致；PSO-ICO-INTERIM-AND-CLAUSE-CHECK.md:一致性 OK）
PASS [M1 未闭环=412] 条件句=『未完成 ⇒ 依 WI-A2 禁止 Wave 2 开工』= True
PASS [M2 未闭环=0] 条件化表述正确（不再称『因 WI-A2 禁止开工』）= True
PASS [M2b 过期内容注入（0 情形混入未完成句）] 被拦下 = True
PASS [M3 未定义处置状态] 拒判 = True
PASS [M4 第五份制品缺失] 被拦下 = True（拒判：受检制品缺失：PSO-ICO-INTERIM-AND-CLAUSE-CHECK.md）
PASS [M4b 制品为空] 被拦下 = True
PASS [M6 分类被篡改（总数不变）] 被拦下 = True（ONTO1-CONSTRUCTION-PLAN-DRAFT.md:一致性 OK；construction-plan.json:不一致：unclosed_by_kind,kinds_sum_eq_rows；ONTO1-CONTRACT-SPLIT-CANDIDATES-DRAFT.md:一致性 OK；contract-split-candidates.json:全部字段一致；PSO-ICO-INTERIM-AND-CLAUSE-CHECK.md:一致性 OK）
PASS [M7 occurrences 被篡改] 被拦下 = True
PASS [M8 明细之和≠总数] 被拦下 = True
PASS [M5 还原对照] 一致 = True
--selftest PASS（11/11）
```

## L1 骨架不变式变异 —— `scripts/onto1_l1_prep.py`（exit=0）

```
PASS [M1 命名空间改为正式根域 ⇒ 应被 L3 拦下] = True
PASS [M2 清单计数篡改 ⇒ 应被 L1 拦下]
PASS [M3 骨架越出证据区 ⇒ 应被 L4 拦下]
--selftest PASS（3/3）
```

