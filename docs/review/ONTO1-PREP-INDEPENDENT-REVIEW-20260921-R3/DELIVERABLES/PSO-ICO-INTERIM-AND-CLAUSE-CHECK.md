# PSO / ICO 临时任命登记与条款禁令核查（准备项 4）

## 1. 临时任命（继续）
| 角色 | holder | status | 说明 |
|---|---|---|---|
| 公共语义 Owner（PSO） | 项目 Owner（邵钟飞） | `interim` | 决定词义 / 本体 / 词表 / 语义版本 |
| Integration Contract Owner（ICO） | 项目 Owner（邵钟飞） | `interim` | 决定接口表达 / 版本绑定 / 兼容性 / 消费者契约；**不得反向改写 PSO 已批准语义** |

**评审委员会独立性（V8）不适用于这两项临时任命**：V8 只约束《14 签署页》的评审委员会构成；两者不可互相援引。

## 2. 条款禁令核查（是否有条款禁止本轮准备工作）
**结论：未发现禁止这些准备工作的条款；发现的是对「实施方式」的约束。**

| 条款（来源） | 对本轮工作的约束 | 具体风险（若越线） |
|---|---|---|
| 未签 D3 前**禁止发布新 IRI / 重钉**（§WI-A4） | L1 骨架必须沿用 `PROVISIONAL_SIM_LEGACY_NAMESPACE` | 违规发布新根域 IRI；碰撞检查失效 |
| **WI-A2 命中处置表**（§WI-A2） | WI-A2 命中处置表**未完成**（未闭环聚合行 **412**：CONTROL_PLANE_REQUIRED 23 / FOLLOW_MIGRATION 270 / HOMONYM_REQUIRES_SOURCE_CHECK 119）⇒ **依 WI-A2，Wave 2 禁止开工**（执行计划 §WI-A2） | 依 WI-A2 判定错误 ⇒ 越权开工或错误冻结 |
| 重构项**禁止**使用 `equivalentClass`（§WI-1-3 校验④） | 施工与骨架均禁用等价关系 | 语义漂移不可审计 |
| D1 文本到手前**禁止国标符合性表述**（§WI-A3） | 全部文书已规避 | 红线违规 |
| KERT 受控内容改动**需维护方权限** | 只交分析/方案/验证材料 | 越权写入他人受控资产 |

> **口径分列（防混算）**：`obligation-triage.csv` 的 691 条义务「待回源 = 0」为**清单口径**；
> WI-A2 命中处置为**扫描口径**——实测未闭环聚合行 **412**（{'FOLLOW_MIGRATION': 270, 'HOMONYM_REQUIRES_SOURCE_CHECK': 119, 'CONTROL_PLANE_REQUIRED': 23}）。

## 3. 需要 Owner 裁定的业务分歧
暂未发现必须由业务裁定的分歧。
