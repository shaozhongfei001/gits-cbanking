# L0-2 G2 映射确认与责任认领登记

> **正式副本位置说明（重要）**：本文件在**主仓** `gits-cbanking` 内建立。
> 依据 `GK-KE-OWNER-003` §7.1，L0-2 受控目标定义**在主仓 `specs/gk-ke/v1` 内维护**，不新建第二份业务权威。
> 决议 §9 要求在 KERT 仓建立 `Leibniz-KERT/docs/integration/L0-2_G2_MAPPING_CONFIRMATION.md`；
> **本环境无 KERT 仓写权限**（`/home/szf/dev/Leibniz-KERT` 为只读参考），
> 故**正式副本须由 KERT 责任方在主仓之外落盘**；本文件为**主仓侧登记 + 待 KERT 落盘的模板**。
> 此偏差如实记录，**不伪造** KERT 侧提交。

---

## 1. 授权依据

| 项 | 内容 |
|---|---|
| 决议编号 | `GK-KE-OWNER-003` |
| 关联 | `GK-KE-OWNER-002`；`GK1-l0-2-contract-activation`；G2 / OC-01 / ACT-01 |
| 决议日期 | `2026-09-12`（Asia/Shanghai） |
| 授权主体 | 本会话人类项目 Owner、全部项目维护者 |
| 出具主体 | 邵钟飞，依据本轮明确授权承担项目 Owner 及 **KERT 维护责任**的决策代理 |
| 总体结论 | `APPROVED_WITH_CONDITIONS` |
| 决议登记（主仓） | `loops/GK1-l0-2-contract-activation/evidence/OWNER-RESOLUTION-GK-KE-OWNER-003.md` |
| 唯一新增直接输入 | `docs/dispatch/GK-KE-L0-2-G2-KERT确认函.md`，SHA-256 `59006f99b1710b73b2381092c97d30c6907944e1d85db0bfb6f60192ebdee6ca`（实测一致） |

**授权边界声明**：本决议为**授权代理**作出，不伪称用户亲笔签名、不伪称另一维护人签名、不伪称独立 QA 签名。
SIM 决策授权**不延伸**为银行生产授信、资金动作、正式银行口径或具体知识内容的真实审批。

## 2. 四问答复（逐条）

### Q1｜产品卡对象粒度 → `APPROVED_WITH_CONDITIONS`

- `ASSET-KNOW-PRODUCT-CARDS` 按**产品卡集合 / 集合入口**管理。
- 首个目标选择 SIM-P001 的固定版本，形成 `SIM-ASSET-P001`。
- **不得把整个集合认作这张单卡**。
- 关系类型：**选择 / 构造**（`SELECT_OR_CONSTRUCT`），**不是身份等价**。

### Q2｜路由策略认领 → `APPROVED_WITH_CONDITIONS`

- **KERT 认领 `SIM-ROUTE-001`** 的定义、维护及后续运行实现责任。**不因当前未实现而否弃**。
- 采用受限访前融资任务路由；**无匹配与歧义分别处理**：
  - 无匹配 → `REJECT`（不用默认模式扩大任务集合）
  - 多匹配歧义 → `ROUTE_AMBIGUOUS`（不按文件顺序、不由 LLM 自选）
- **保留来源规则优先级 20 作为可追溯属性**；不凭 10/20/30/40 数值推断引擎排序语义。
- **排除**事实核对 / 市场发现 / 报告生成三条规则；**不带入** `AC-NOT-IN-P20` 占位引用。

### Q3｜地图投影认领 → `APPROVED_WITH_CONDITIONS`

- **KERT 认领 `SIM-MAP-FINANCE`** 作为目标任务知识地图，负责定义、认定发布及运行适配。
- 源地图 `KM-CORP-RM-PREVISIT@0.1.0`，目标 `FINANCE_VISIT_PREP`，限 `SIM-C001` / `SIM-O01` / `INTERPRETATION`。
- 关系类型：**受限场景投影**（`SCENARIO_PROJECTION`），**是有损的**，不是整个访前准备业务的无损等价映射。
- **旧轨迹代码仅确认存在地图引用，不证明运行能力完整**。

### Q4｜运行计划对象 → `APPROVED`

- **KERT 接受并负责 `ActivationPlan` 的规划与运行集成**。
- `AC-PREVISIT-001` 是**编译前置约束**，**不是计划实例**。
- **禁止复用 AC ID 充当 planId**。
- 同一固化输入下 canonical `planHash` 应一致；随机标识与追踪信息按 C06 排除在语义 hash 之外。
- KERT 计划**不得接管** GITS 的正式业务写回。

## 3. 三个目标的正式责任认领

| 目标对象 | 认领结论 | 权威责任 | 当前运行状态处理 |
|---|---|---|---|
| `SIM-ASSET-P001` | **接受，不否弃** | KERT 知识资产责任方维护产品卡内容、来源及版本 | 未凭本决议认定内容已发布或服务已可用 |
| `SIM-MAP-FINANCE` | **接受，不否弃** | KERT 地图责任方维护任务地图；业务用途遵守已批准边界 | 未凭轨迹记录认定地图解析/执行已完成 |
| `SIM-ROUTE-001` | **接受，不否弃** | KERT 地图/规划责任方维护派生策略；原 RP 仍按原归属维护 | 未凭本次认领认定路由引擎已实现 |

## 4. 唯一受控路径与内容指纹（§7.2 E-3/E-4）

| 目标 | 唯一受控路径（主仓） | 对象 ID / 版本 | **文件原始字节 SHA-256** | canonical instance SHA-256 | 落实提交 |
|---|---|---|---|---|---|
| SIM-ASSET-P001 | `specs/gk-ke/v1/definitions/SIM-ASSET-P001.json` | `SIM-ASSET-P001` / `1.0.0` | `11926c26f70201e1351a753c8cb97c01909f10d97de5e1724cfc158523788a2b` | `2bcd96081881e79a9ae87144f061f096911c27fc3554dc88f5182c4a1ac2288b` | 见 `_registry.json` |
| SIM-MAP-FINANCE | `specs/gk-ke/v1/definitions/SIM-MAP-FINANCE.json` | `SIM-MAP-FINANCE` / `1.0.0` | `78fa5ec9a58f6213eb20c36b5dfb17f1e2c937880023f18e4261654492d89d3d` | `a0321371a627738c97d271f4124db959ab745a6400591b1e5851172bf4ed1acd` | 见 `_registry.json` |
| SIM-ROUTE-001 | `specs/gk-ke/v1/definitions/SIM-ROUTE-001.json` | `SIM-ROUTE-001` / `1.0.0` | `31190e64f1fb258e87410bc50a21704071c8e81c93576f30ffa341fb4d07b1b0` | （策略无内嵌 instance，见 §4.1） | 见 `_registry.json` |

**指纹口径**：以上 hash 由 `scripts/gk_ke_g2_definitions_check.py` **按真实文件字节计算**并写入侧车清单
`specs/gk-ke/v1/definitions/_registry.json`。**未手工填造**。
定义文件内 `origin.contentSha256` 固定为 `null`（**自引用防护**，见 `FAIL-2026-09-12-03`）。

**未使用的替代物（§9 明确禁止）**：**未**以本文或确认函的 hash 充当目标对象内容 hash。

### 4.1 SIM-ROUTE-001 无内嵌 instance 的说明

`SIM-ROUTE-001` 是**策略定义**，非 `gk-ke/v1` 闭集 Schema 的实体实例（无对应 schema 约束其顶层）。
其内容以 `targetPolicy` + `singleRuleInstance` 结构化表述，故：
- **文件字节 SHA-256** = `31190e64…`（可用，已登记）
- **canonical instance SHA-256** = 不适用（无内嵌完整实体）
- 后续若 L4-1 需要策略 instance hash，按届时绑定的引擎合同定义，**不提前编造**。

## 5. 来源核对（§7.2 保留证据）

| 项 | 值 |
|---|---|
| 所依据的 KERT 源提交 | `3b6640b993f4834d36833fa0bc3005d73768b594`（分支 `feature/PI-ARCH-L10-L13`） |
| 源证据片段 | `src/kert/application/skills.py:637` `_trace_knowledge_map(trace, "KM-CORP-RM-PREVISIT", "PRE_VISIT_PREPARATION")` |
| 该片段**能**证明 | 存在地图标识引用（`KM-CORP-RM-PREVISIT` / `PRE_VISIT_PREPARATION`） |
| 该片段**不能**证明 | 地图加载、Schema 校验、依赖解析、版本选择、执行消费已完成 |
| 表述修正 | **撤回**确认函中「消费关系已获实证」的过强表述 |
| 其他源证据 | `src/kert/application/product_recommendation/sp15_skill.py:347,874-877`（列表输入 + `{productId: card}` 构造）；`portfolio.py:222-225`（单卡读取）；`eligibility.py:270-285`（卡片字段门禁） |
| 基线差异 | KERT HEAD 若已前进，**不覆盖**旧基线 `3b6640b`，补差异或未变证明 |

## 6. 五条映射登记（§7.2，根地图规则沿用 OWNER-002）

| # | 来源对象 | 目标对象 | 关系 | 状态 |
|---|---|---|---|---|
| 1 | `KM-GITS-ROOT@0.1.0` | （无 SIM 对应） | 不转换（导航/定位） | 按 `mapType=ROOT` 识别；沿用 OWNER-002 |
| 2 | `KM-CORP-RM-PREVISIT@0.1.0` | `SIM-MAP-FINANCE@1.0.0` | `SCENARIO_PROJECTION`（有损） | **已认领**（OWNER-003 §5） |
| 3 | `ASSET-KNOW-PRODUCT-CARDS` | `SIM-ASSET-P001@1.0.0` | `SELECT_OR_CONSTRUCT` | **已认领**（OWNER-003 §3） |
| 4 | `AC-PREVISIT-001` | `ActivationPlan` | `COMPILE_PREREQUISITE`（非实例化） | **已认领**（OWNER-003 §6） |
| 5 | `RP-CORP-RM-001@0.1.0` | `SIM-ROUTE-001@1.0.0` | `CONTROLLED_POLICY_ADAPTATION` | **已认领**（OWNER-003 §4） |

**状态口径**：五条的**角色选择已完成**（Owner 已裁定）；剩余状态为**定义/证据待完成**。
**不新造状态枚举**，沿用现有允许字段（`pending_owner_confirmation` 已不适用 → 由本决议替换为已认领）。

## 7. 运行缺口移交（§7.3，不制造循环依赖）

| 后续阶段 | 承接内容 |
|---|---|
| L2-2 | 目标定义导入、注册/引用解析、消费者适配、可见性与可执行性分离 |
| L3 | 产品卡与地图内容/用途认定、发布、撤销；候选与发布隔离 |
| L4-1 | 路由解析、计划编译、能力探针、相同输入同 hash、歧义及必需依赖缺失拒绝 |
| L4-2 | GITS 经营任务、人工确认、两类模拟动作、回执及恢复 |

**完整运行能力未验收时，正常运行入口必须拒绝或明确不可用**；研发隔离环境的合同测试**不冒充**正式知识执行。

## 8. 状态区分（必须维持，§9）

| 状态 | 当前值 | 说明 |
|---|---|---|
| 资产候选 | CANDIDATE | 三份定义为设计制品 |
| 契约激活 | 待生效 | 依赖 G2/OC-01 关闭 |
| 已发布 | **否** | 未认定内容已发布 |
| 当前可执行 | **否** | 未认定服务已可用 |

**不得**要求先完成 L4 才允许激活 L0 契约；**也不得**凭 L0 激活宣称 L4 完成。

## 9. 禁止误引（§8）

`Leibniz-KERT/docs/integration/KERT_GITS_STATE_MAPPING_CANDIDATE.md` 属 **WP1-3 产品推荐状态映射**
（`status=CANDIDATE` / `FROZEN=NO` / `IMPLEMENTED=NO`），
**禁止**用作本次 L0-2 五条对象映射的确认证据。保留其原始限定。

## 10. KERT 侧落盘清单（待 KERT 责任方执行）

- [ ] 在 `Leibniz-KERT/docs/integration/L0-2_G2_MAPPING_CONFIRMATION.md` 建立正式副本
- [ ] 引用本决议与主仓定义（**不复制定义**，仅引用路径 + 版本 + hash）
- [ ] 登记上述三个目标的唯一受控路径与内容 SHA-256
- [ ] 检查 KERT 仓现行权威索引是否已将某定义指定到其他路径；若是，**保留其唯一源**并准确引用
- [ ] 记录落实提交号（主仓 hash 绑定到具体提交）
- [ ] 运行投影/生成文件/缓存均标明上游来源，**不形成可独立修改的第二份定义**
