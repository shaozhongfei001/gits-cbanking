# KERT 侧变更准备（只读分析 + 补丁方案 + 验证材料）

> 状态：`CANDIDATE_NOT_EFFECTIVE`｜**本轮未对 KERT 侧写入任何内容**｜合入权在 **KERT 维护方**

## 1. 受控内容与义务面（KERT 侧真义务 86 项）
| 区域 | 项数 |
|---|---|
| `src/kert` | 50 |
| `examples/bank-front-knowledge-maps` | 33 |
| `specs/kert-openapi-v1.yaml` | 3 |

- 波次：{'W3_CONSUMER_SWITCH': 64, 'W3_KERT_ASSETS': 19, 'W2_SPLIT': 3}
- 定级：{'STRONG': 86}

## 2. 候选变更集（**方案**，未实施）
| 目标 | 变更 | 依据 | 前提 |
|---|---|---|---|
| `90_control/ontology/` | 改放「L1 副本 + L2 本体」 | 执行计划 §84 | KERT 维护方写权限 |
| `ontology_reference.json` | → `authorityEntity`（公共语义实体）+ 新钉值 | 同上 | 同上 |
| `ontology_assets.py` | role 扩：`PUBLIC` / `KERT` / `GITS-EXTERNAL` | 同上 | 同上 |
| 物化链路 | 重跑，**校验先于产出** | 同上 | 同上 |

## 3. 验证材料（已备，不含写入）
1. **只读证据快照**：待改文件清单 + sha256（维护方可据此比对合入前后）；
2. **物化链路顺序**：先校验后产出；校验红即不产出；
3. **消费者引用面**：64 项 W3_CONSUMER_SWITCH 的清单（见 `obligation-triage.csv`）。

## 4. 约束
- 未确认写权限前**不得合入**；本轮只交分析/方案/验证材料；
- 不得以"为通过门禁"为由修改 KERT 受控内容；
- KERT 侧改动必须保留**来源可回源**（文件:行 + 哈希）。
