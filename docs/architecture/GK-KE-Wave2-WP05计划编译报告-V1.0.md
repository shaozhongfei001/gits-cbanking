# GK-KE Wave 2：WP05 能力与地图 · 计划编译报告 V1.0

> 执行：GK-KE 全局 Tech Lead（B1）｜Loop：`GK14-l4-0-capability-closure`｜日期：2026-09-12
> 依据：建议书 §10.3（六步计划编译）/ §14.2（最小闭环）｜`GK-KE-OWNER-004`
> 前置：A1/A2/A3/A5 已固定 + D1/D2/D3 已决（§15.4 硬门禁满足）

---

## 0. 结论：**BLOCKED**（且这正是正确结果）

```
gk-ke-plan-compiler: BLOCKED
  route: SELECTED
  planDigest: cff109446d697a6f...
  nodes: 9 (callable 7)
  enabled metrics: 19
  playbook: OK
  barriers: 1 blocking, 0 conditional
    [BLOCKING] REQUIRED_CAPABILITY_NOT_CALLABLE SIM-CAP-REPORT-ASSEMBLE
```

**→ 计划无法编译为可执行。阻断原因是能力不可调用，不是脚本缺陷。**

**这是 OC-04 无法关闭的「机械化证据」** —— 不再是文字描述，而是可重复执行的判定。

---

## 1. 六步编译过程（§10.3 逐步骤实施）

| 步骤 | 建议书要求 | 实现 | 结果 |
|---|---|---|---|
| **1** | 解析意图，选择批准的地图版本；多个同优先级匹配 → `ROUTE_AMBIGUOUS` | 读 `TaskTemplate.taskType` + `map_spec.mapId` | ✅ `SELECTED`（唯一匹配） |
| **2** | 选择行业方案包和指标子集 | 校验 `SIM-IND-MANUFACTURING` 存在性；读指标注册 | ✅ 行业包 OK；**19 项指标已启用** |
| **3** | 解析资产/产品/规则/能力的精确版本；验证权限、用途、有效期和依赖 | 交叉读 `map_dependency_lock` + `Capability.json` + `provider-bindings.json` | ✅ 9 节点全部解析出版本与 provider |
| **4** | 检查必需能力语义探针；**必需能力不可用则阻断** | 逐节点检查 `callable` | ❌ **1 项阻断** |
| **5** | 生成受控 DAG 与**计划摘要值** | canonical JSON → SHA-256 | ✅ `planDigest` 已固化 |
| **6** | 执行时逐步检查，**不悄悄换版本** | 摘要值作为重规划判据 | ✅ 设计已实现 |

---

## 2. 阻断详情（**这是 OC-04 的核心阻塞**）

```json
{
  "code": "REQUIRED_CAPABILITY_NOT_CALLABLE",
  "capabilityId": "SIM-CAP-REPORT-ASSEMBLE",
  "proposalRef": "CAP-09",
  "probeStatus": "NOT_PROBED",
  "bindingVerdict": "PROVEN_BOUND",
  "detail": "SIM-CAP-REPORT-ASSEMBLE 不可调用（probeStatus=NOT_PROBED）。
             §10.3 步骤4：必需能力不可用则阻断。"
}
```

### 2.1 为什么它不可调用（**根因链**）

```
KERT skills.py:5   模块注释称「R1 拜访报告已于 2026-08-21 下线移除」
KERT skills.py:169 但 SkillInfo 仍在 registry
                    ↓
GK-KE 语义探针判定 NOT_PROBED
（映射 verdict=PENDING，因生命周期冲突未裁）
                    ↓
计划编译步骤 4 阻断
                    ↓
OC-04 无法达标
```

### 2.2 与我此前判断的**一致性**

| 环节 | 此前结论 | 本次机械化确认 |
|---|---|---|
| U-A 阻塞 REPORT-ASSEMBLE | 文字结论 | ✅ **编译器独立复现** |
| OC-04 瓶颈在 KERT 侧 | 我的判断 | ✅ **不再依赖我的判断** |

**意义**：此前"OC-04 因 R-3 阻塞"是我的**叙述**；
现在是**可重复执行的机械判定** —— 任何人运行 `make plan-compile` 都会得到同样结果。

---

## 3. 条件能力（不阻断，但有约束）

`CAP-03`（`SIM-CAP-SUPPLY-CHAIN`）为**条件能力**：

```json
{
  "conditional": true,
  "detail": "CAP-03 属条件能力：普通融资访前可用一跳关系，不构成必需。"
}
```

**约束**（§9.1 原文）：
> 「CAP-03 在供应链路径被声明为必需时必须可运行；
> 普通融资访前可使用**已核实的一跳关系列表**，
> **不能声称已经实现多跳图能力**。」

**本计划采用**：普通融资访前模式 → **一跳关系** → **不声称多跳**。

---

## 4. 计划摘要值（§10.3 要求）

```
planDigest: cff109446d697a6f...
algorithm:  sha256(canonical json: sorted keys, compact separators, utf-8)
```

**摘要输入**（`digestInputs`）：

| 输入 | 值 |
|---|---|
| taskTemplate | `SIM-TASK-001` |
| mapId / version / releaseId | `SIM-MAP-FINANCE` / `2.0.0` / `SIM-REL-001` |
| scope | `SIM-C001` / 对公客户经理 / `FINANCE_VISIT_PREP` |
| playbook | `SIM-IND-MANUFACTURING` |
| metricsEnabled | `19` |
| nodes | 9 节点（含版本） |
| ruleSubset | `R01/R03/R06/R08/R12/R14` |
| parameterProfile | `SIM-PARAM-FIRST-SLICE` |
| dataSnapshot | `SIM-SNAPSHOT-V2-20260912` |

**满足 §10.3**：「同一份**已经固定**的任务意图、证据、权限、版本、配置和运行依赖快照
应得到**同一计划摘要值**」

**明确不满足的**：§10.3 同时提到「不能把这一要求扩张为'任何随机生成文本都必须逐字相同'」
—— 本摘要**只覆盖受控输入**，不覆盖生成文本。

---

## 5. 编译产物

`specs/knowledge-architecture/activation/compiled_plan.json`

含：`verdict` / `routeDecision` / `planDigest` / `digestInputs` / 9 个节点
（各带 `version`/`providerId`/`bindingVerdict`/`callable`/`probeStatus`）/ `barriers` / `notes`

**状态**：`CANDIDATE`，`verdict=BLOCKED`

---

## 6. 关键设计决策

| # | 决策 | 理由 |
|---|---|---|
| 1 | **BLOCKED 不返回非零退出码** | 编译器职责是**如实报告编译结论**，不是"失败"。若返回非零，会被误读为脚本 bug |
| 2 | **条件能力不阻断但记 note** | §9.1 明确 CAP-03 非必需；但**不得声称多跳** |
| 3 | **摘要只覆盖受控输入** | 避免 §10.3 警告的"过度扩张到随机文本" |
| 4 | **阻断信息含根因链** | 使 OC-04 阻塞**可被任何人独立复现** |

---

## 7. §14.2 逐项对照（当前状态）

| §14.2 要求 | 状态 | 证据 |
|---|---|---|
| 一条明确范围的访前地图 | ✅ | map_spec v2.0.0 + TaskTemplate + **依赖锁**（A5） |
| 行业研究和客户经营模型 | ✅ | `SIM-IND-MANUFACTURING` 八维逐维比较（WP02） |
| 指标及规则可执行 | ✅ | **19 项定义，14 项实测复算**（A2）；规则子集已固定 |
| 产品条件有实质内容 | ⚠️ **部分** | 6 项条件均为可执行谓词（A3），但**体检 INCOMPLETE**（缺原文定位） |
| **所需能力真实可调用** | ❌ **不达标** | **编译器阻断**：`REPORT-ASSEMBLE` `callable=false` |
| 能力之间真正消费结果 | ❌ **不达标** | 合同已定义（A1），**无运行 trace** |
| 可确认的任务证据 | ⚠️ **部分** | 三阶段证据接口已定义（B2），**持久化未实现** |
| 必要负向边界 | ✅ | 探针含大量负例；注册中心 7 个负例夹具 |
| 固定交付证据 | ✅ | 依赖锁 + 侧车 hash + 计划摘要值 |

**→ 9 项中：5 项达成，2 项部分，2 项不达标。**

---

## 8. 下一步（Wave 3 就绪判定）

| 前置 | 状态 |
|---|---|
| A1–A5 + B1/B2 完成 | ✅ |
| D1/D2/D3 已决 | ✅ |
| **U-A（R-3 裁定）** | ❌ **仍是唯一硬阻塞** |
| U-D（KERT 提交） | ❌ 可复现性 |

**Wave 3（A4 正式验收 + OC-04 判定包）可以在 U-A 解决前先行准备，但无法得出"通过"结论。**

**理由**：编译器已机械化证明阻断，验收只能复现同一结论。

---

## 9. 边界声明

- 本轮**未修改** KERT 任何文件
- 本轮**未修改** `generated/`、`_registry.json`
- **BLOCKED 不构成**"脚本失败"，也不构成"可运行"
- 本报告**不构成** OC-04 关闭证据 —— **恰恰相反，它机械证明了不能关闭**
- 计划状态 `CANDIDATE`，`verdict=BLOCKED`，**未声称可执行**
