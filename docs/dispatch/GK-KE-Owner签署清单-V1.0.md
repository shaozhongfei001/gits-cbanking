# GK-KE Owner 签署清单（OC-02 ~ OC-06 + 试点裁定）

> 出具角色：Tech Lead（planning_review）｜日期：2026-09-12｜基线 HEAD：`5a60959`
> 用途：**供 Owner 逐项批注/签署**。本清单**不构成签署**；TL/QA 均不得代签。
> 依据：`GK-KE-OWNER-003` §9（范围不变的落实不再申请相同 Owner 决定）——
> 本清单所列**非"同一认领/映射决定的重复"**，而是**各 Loop 的领域验收与试点裁定**，
> 属 Owner 保留权限，故须签署。

---

## 0. 签署前状态确认（Agent 侧已完成）

| 项 | 值 |
|---|---|
| 完成 Loop | **12 / 12** |
| 门禁通过 | **20 / 20**（含跨语言 T35） |
| 变异回归 | **10 / 10** 变异被捕获（证明断言非空转） |
| 独立 QA | 4 次全 `QA_PASS`（`qa-gk1-l02-001` / `qa-gk1-g4-001` / `qa-gk1-g2-001` / `qa-gkl6-001`） |
| 自愈记录 | 16 项，全 CLOSED |
| `OC-01` / `ACT-01` | **已关闭** / **已生效** |
| 红线 | 全部守住（见 §3） |

**结论**：Agent 侧工作完毕，**余下 9 项全为人工签署/裁定**。

---

## 1. 条件签署项（OC-02 ~ OC-06）

### OC-02｜指标服务化（承接 L2-1）

| 项 | 内容 |
|---|---|
| **关闭时点** | L2-1 退出前 |
| **责任角色** | **指标 Owner**（签署 OM-C1 / OM-C2） |
| **技术证据** | `scripts/gk_ke_l2_1_semantic_query_tests.py`（9 条错误路径全触发）；指标定义 `specs/gk-ke/v1/definitions/SIM.METRIC.CUSTOMER_AVG_DEPOSIT.json`（C04 §2 七字段组 / 42 必填） |
| **关键真值** | **C001 日均存款 = 2,983,333.33 CNY**（独立复算，C07 §5 公式：先按业务日跨账户汇总，再除以 30 天） |
| **需 Owner 确认** | ☐ 指标口径与杭银正式口径的**差异边界**已明确（本包为 SIM，非正式口径）<br>☐ 公式与粒度定义可作为服务化基线<br>☐ OM-C1 / OM-C2 编号与内容认可 |
| **风险提示** | 本包 `currencyPolicy=CNY_ONLY`；跨币种一律拒绝（不入聚合）。若正式口径需多币种，须另立版本。 |

**签署**：Owner ______ 日期 ______ ☐ 关闭 OC-02 ／ ☐ 附条件（说明：__________）

---

### OC-03｜候选内容与发布（承接 L3-2）

| 项 | 内容 |
|---|---|
| **关闭时点** | L3-2 发布前 |
| **责任角色** | **知识 Owner** |
| **技术证据** | `scripts/gk_ke_l3_2_release_tests.py`（Publishable 八项逐项 + 7 类违规夹具 + 13 条 C03 §9 失败证据）；`specs/knowledge-architecture/release/` |
| **已验证的否定式要求** | 审批后改字阻断 ／ 自审自批阻断 ／ 过期审批不计入 ／ 半发布阻断 ／ 撤销即时生效 ／ 回滚不得指向已撤销版本 ／ 用途标记不得静默升级 |
| **需 Owner 确认** | ☐ 双维审核（内容认定 + 地图执行认定）责任方已指定<br>☐ 「人工更正可追踪」的留痕要求满足审计需要<br>☐ 生产署名须来自**真实认证主体**（当前 `SIM-REVIEWER` 仅为夹具） |
| **风险提示** | 本包未接入真实身份认证；生产署名要求已写入合同但**未实现**。 |

**签署**：Owner ______ 日期 ______ ☐ 关闭 OC-03 ／ ☐ 附条件（说明：__________）

---

### OC-04｜地图和能力（承接 L4-1）

| 项 | 内容 |
|---|---|
| **关闭时点** | L4-1 激活/退出 |
| **责任角色** | **知识 Owner + 能力维护者** |
| **技术证据** | `scripts/gk_ke_l4_1_map_activation_tests.py`（同输入同 hash ／ 同优先级歧义拒绝 ／ 必需能力缺失拒绝 ／ DAG 成环拒绝）；`specs/knowledge-architecture/activation/` |
| **已验证 | MapSpec 必须有入口节点与用途声明；KERT 计划不得含 GITS 正式业务写回 |
| **需 Owner 确认** | ☐ `SIM-MAP-FINANCE` 的任务入口/必需节点/预算（2000 tokens）符合业务预期<br>☐ 路由策略 `SIM-ROUTE-001` 的**无匹配拒绝**与**歧义拒绝**两种行为均认可<br>☐ 能力清单（`SIM-CAP-INTERPRET`）的真实性由能力维护者确认 |
| **风险提示** | 计划编译器目前为**确定性参考实现**（Python 门禁），非 KERT 运行时；KERT 侧 `ActivationPlan` 集成按 `OWNER-003` §6 由 KERT 负责。 |

**签署**：Owner ______ 日期 ______ ☐ 关闭 OC-04 ／ ☐ 附条件（说明：__________）

---

### OC-05｜完整经营闭环（承接 L4-2）

| 项 | 内容 |
|---|---|
| **关闭时点** | L4-2 退出前 |
| **责任角色** | **业务专家**（验收门禁 **OB-C3**） |
| **技术证据** | `scripts/gk_ke_l4_2_closed_loop_tests.py`（五步闭环 / 3000 万场景 / UNKNOWN / 失效版本 / 超时对账 / 白名单强制）；`specs/knowledge-architecture/closed-loop/` |
| **已验证的边界** | 「下季度可能需 3000 万」= **客户声明**（`CUSTOMER_STATEMENT`），**不得**当作真实贷款需求/额度/可提款金额<br>用途未知 → 输出 **UNKNOWN** + 补充问题，**不得**因行业图存在「资金需求」关系而通过准入<br>超时 → **RESULT_UNKNOWN**，**先查目标回执**，不直接判失败<br>白名单仅 `CREATE_FOLLOWUP_TASK` / `RECORD_CONTACT_OUTCOME` |
| **需 Owner 确认（**OB-C3 核心**）** | ☐ 五步闭环（解读→体检→推荐→确认→模拟跟进）符合对公客户经理实际作业流程<br>☐ 3000 万场景的**声明 / 事实 / 额度**区分符合业务与合规要求<br>☐ UNKNOWN 处置与补充问题清单符合访前实务<br>☐ 两类模拟动作足以支撑试点验证<br>☐ 超时对账语义（不做即时失败判定）符合运营预期 |
| **风险提示** | 本包**不产生授信结论**，推荐仅为候选建议。业务专家验收是**唯一**能确认"闭环可用"的角色。 |

**签署**：业务专家 ______ 日期 ______ ☐ 通过 OB-C3 ／ ☐ 不通过（说明：__________）

---

### OC-06｜范围持续遵守（每 Loop + L6 放行前）

| 项 | 内容 |
|---|---|
| **关闭时点** | L6 放行前 |
| **责任角色** | **Owner** |
| **技术证据** | `specs/knowledge-architecture/acceptance/acceptance_report.json` 的 `oc06ScopeDeclarations`（**12 个 Loop 逐一**声明 `outOfScopeRespected=true`）；`scripts/gk_ke_l6_runtime_acceptance_tests.py` |
| **需 Owner 确认** | ☐ 12 个 Loop **均未越界**（未做 scope 外功能、未跨 Loop 混做）<br>☐ 未启用隔离资产（Oracle / Ossie）<br>☐ 未发生生产写回<br>☐ `CONTRACT_CANDIDATE` 未被擅自改 `APPROVED`（实测 21 / 0）<br>☐ 36 项 `PLANNED_NOT_EXECUTED` 未被改 `PASS` |
| **风险提示** | 无 |

**签署**：Owner ______ 日期 ______ ☐ 关闭 OC-06

---

## 2. 领域签署项（非 OC，但属既定验收要求）

| # | 项 | 角色 | 证据 | 签署 |
|---|---|---|---|---|
| S-1 | **L1-1 语义专家审**（12 类型 / 双版本 / ID·时间·金额规范） | 语义专家 | `scripts/gk_ke_l1_1_semantics_tests.py`；`specs/gk-ke/v1/schemas/` | ______ |
| S-2 | **L1-2 数据专家核对**（模拟对象服务 / 账务快照 / 外键余额币种） | 数据专家 | `scripts/gk_ke_l1_2_simulation_tests.py`（C001 复算） | ______ |
| S-3 | **RTO 具体目标值**（已实测，目标值待提交） | 运维 | `specs/knowledge-architecture/acceptance/acceptance_report.json` 的 `upgradeRecovery.rto` | ______ |
| S-4 | **KERT 仓 G2 正式副本落盘** | KERT 维护方 | 待建 `Leibniz-KERT/docs/integration/L0-2_G2_MAPPING_CONFIRMATION.md`（主仓侧登记已完成） | ______ |

> **S-4 说明**：本环境对 KERT 仓**只读**，故正式副本须由 KERT 维护方建立。主仓侧登记见
> `docs/integration/L0-2_G2_MAPPING_CONFIRMATION.md`（含 §10 落盘清单）。

---

## 3. 红线核查（请 Owner 复核）

| 红线 | 实测 | 结果 |
|---|---|---|
| `generated/` 手工编辑 | `make generate` 后 `git status` 为空 | ✅ 可重现 |
| 封版 `docs/dd/gk-ke-contract/` | tree 仍为 `4c5f5373`，diff 0 行 | ✅ 未改 |
| P20 / DKES / PI-0 合同 | 未改 | ✅ |
| `CONTRACT_CANDIDATE` → `APPROVED` | 21 / **0** | ✅ |
| `PLANNED_NOT_EXECUTED` → `PASS` | 36 项未改 | ✅ |
| `git add .` | 未使用（显式路径） | ✅ |
| 隔离资产（Oracle / Ossie） | 未启用 | ✅ |
| 生产写回 | 无（SIM only） | ✅ |
| Owner 决议代签 | 无 | ✅ |

---

## 4. 试点范围裁定（L6 最终门禁）

| 项 | 内容 |
|---|---|
| **裁定事项** | GK-KE 试点范围与放行条件 |
| **当前登记** | `PENDING_OWNER_DECISION`（见 `evidence/L6/DEPLOYMENT.lock.json`） |
| **可选范围** | ☐ **全量试点**（12 Loop 能力）<br>☐ **基础闭环试点**（L1-1/L2-1/L4-1/L4-2 + L1-2，**不含 L5**）<br>☐ **只读试点**（L1-1/L2-1/L2-2/L3-1/L3-2，不做动作）<br>☐ **暂不放行**（继续补充证据） |
| **建议依据** | L5-1/L5-2 为**可关增强项**，C05 门槛未满足（LightRAG 未启用），故"基础闭环试点"风险最低且不影响主业务链 |
| **放行附加条件** | ☐ 真实身份认证接入（L3-2 生产署名）<br>☐ 真实数据源对接（当前为 SIM）<br>☐ 运维监控与回滚演练<br>☐ 其它：__________ |

**裁定**：Owner ______ 日期 ______ 范围 ______

---

## 5. 签署汇总（供归档）

| 编号 | 事项 | 角色 | 结论 |
|---|---|---|---|
| OC-02 | 指标服务化 | 指标 Owner | ______ |
| OC-03 | 候选内容与发布 | 知识 Owner | ______ |
| OC-04 | 地图和能力 | 知识/能力 Owner | ______ |
| OC-05 | 完整经营闭环（OB-C3） | 业务专家 | ______ |
| OC-06 | 范围持续遵守 | Owner | ______ |
| S-1 | L1-1 语义专家审 | 语义专家 | ______ |
| S-2 | L1-2 数据专家核对 | 数据专家 | ______ |
| S-3 | RTO 目标值 | 运维 | ______ |
| S-4 | KERT 仓 G2 副本 | KERT 维护方 | ______ |
| PILOT | 试点范围 | Owner | ______ |

**全部签署完成后**：
1. TL 登记 OC-02 ~ OC-06 关闭与试点范围到各 Loop 的 `EVIDENCE.json` / `STATE.json`
2. 各 Loop 由 `ready_for_independent_qa` → `closed`
3. 更新 `DEPLOYMENT.lock.json` 的 `pilotScope` 与放行条件
4. 输出 GK-KE 交付闭环确认

> **注**：若任一项附条件通过，TL 将按条件清单建立跟踪项，不视为已关闭。
