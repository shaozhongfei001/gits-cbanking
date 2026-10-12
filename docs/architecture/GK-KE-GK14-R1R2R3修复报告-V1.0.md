# GK-KE GK14：R-1 / R-2 / R-3 修复报告 V1.0

> 执行：GK-KE Tech Lead｜Loop：`GK14-l4-0-capability-closure`｜日期：2026-09-12
> 依据：`GK-KE-OWNER-004`（建议书采纳决议）；WP01 差异表 §7；建议书 §9.2 / §15.4
> 锚点：`/home/szf/dev/gits-cbanking` @ `5c91ec348e8a74d81ed80a09cb49a76373b15fde`

---

## 0. 结论摘要

| 风险 | 原描述 | 修复后 | 状态 |
|---|---|---|---|
| **R-1** | 能力三方不闭合（地图 9 / 注册 1 / 设计 4） | 注册中心登记 **10 项**（9 地图引用 + 1 INTERPRET），逐项带 `readiness` 与证据 | ✅ **闭合** |
| **R-2** | 三套命名并存且无显式映射 | 新增 `CapabilityIdMapping.json`，**10 条全链映射** | ✅ **闭合** |
| **R-3** | `skill-customer-previsit-report` 疑为僵尸注册 | **已证实：非僵尸，代码完全可达**；真实问题是**文档与代码不一致** | ✅ **定性并登记** |

**门禁**：`make check` **PASS**（contract-check / knowledge-architecture-check / loop-guard /
secret-scan / enum-consistency / semantic-rule-gate / gk-ke-contract-examples 全绿）。

---

## 1. R-1：能力三方闭合

### 1.1 修复前的真实性质

`specs/knowledge-architecture/activation/map_spec.json` 的 `capabilities` 段
**其实已含完整就绪度数据与证据行号**：

```json
{"id":"SIM-CAP-SUPPLY-CHAIN","readiness":"PACKAGE_LOADABLE_UNVERIFIED",
 "evidence":"skills.py 含该 skillId 字面量，走技能包加载分支；待运行验证"}
{"id":"SIM-CAP-REPORT-ASSEMBLE","readiness":"IMPLEMENTED_DIFFERENT_NAME",
 "evidence":"skill-customer-previsit-report → _run_previsit（skills.py:542）"}
```

**→ 故 R-1 不是"数据缺失"，而是"数据未同步"**：地图侧已如实记录，
注册中心只登记 1 项，导致下游若查注册中心会**得出与实际不符的结论**。

### 1.2 修复动作

改写 `specs/knowledge-architecture/registry/Capability.json`，登记 **10 项**：

| # | capabilityId | readiness | callable | probeStatus | 在地图 |
|---|---|---|---|---|---|
| 1 | `SIM-CAP-INTERPRET` | `IMPLEMENTED_AND_PROBED` | **true** | **PASSED** | 否（独立链路） |
| 2 | `SIM-CAP-SUPPLY-CHAIN` | `PACKAGE_LOADABLE_UNVERIFIED` | false | NOT_RUN | 是 |
| 3 | `SIM-CAP-EIGHT-DIM` | `DESIGN_ONLY` | false | NOT_RUN | 是 |
| 4 | `SIM-CAP-FACT-RECON` | `DESIGN_ONLY` | false | NOT_RUN | 是 |
| 5 | `SIM-CAP-COMMITMENT` | `PARTIAL_VIA_OTHER_SKILL` | false | NOT_RUN | 是 |
| 6 | `SIM-CAP-KYC-GAP` | `DESIGN_ONLY` | false | NOT_RUN | 是 |
| 7 | `SIM-CAP-PRODUCT-REC` | `DESIGN_ONLY` | false | NOT_RUN | 是 |
| 8 | `SIM-CAP-REPORT-ASSEMBLE` | `IMPLEMENTED_DIFFERENT_NAME` | false | NOT_RUN | 是 |
| 9 | `SIM-CAP-MEETING-SCRIPT` | `IMPLEMENTED` | false | NOT_RUN | 是 |
| 10 | `SIM-CAP-OUTREACH-SCRIPT` | `IMPLEMENTED` | false | NOT_RUN | 是 |

### 1.3 关键设计决策：**只有 1 项 callable=true**

**这是本次修复最重要的一点**。虽然 4 项标注为 `IMPLEMENTED*`，但
**`probeStatus` 全部为 `NOT_RUN`**，故 **`callable` 一律为 `false`**。

**依据**（建议书 §9.4 原文）：
> 「**健康检查也不能只验证 HTTP 200**；至少使用一个**已知语义样例**检查输入、结果、证据及失败状态。」

**→ 设计原则**：`IMPLEMENTED`（代码存在）**不等于** `callable`（可调用）。
只有通过**语义探针**的才置 `callable: true`。此原则可防止下游把"有代码"误读为"可运行"。

### 1.4 逐项 `mustNotClaim` 声明

对 9 项非就绪能力各加 `mustNotClaim` 字段，把建议书的禁止性约束固化到合同里：

| capabilityId | mustNotClaim |
|---|---|
| `SIM-CAP-SUPPLY-CHAIN` | 不得因可被包加载即认定多跳图能力已实现（§9.1） |
| `SIM-CAP-EIGHT-DIM` | 不得按名称自动认定与 `KI-FRONT-002` 内容相同（§5.2） |
| `SIM-CAP-FACT-RECON` | 现有规则仅"方向 + 待核实"，缺阈值、窗口与可比性前置 |
| `SIM-CAP-COMMITMENT` | 功能相近不等于语义兼容；须区分历史承诺/沟通问题/新行动建议（§9.2） |
| `SIM-CAP-KYC-GAP` | 业务访谈缺口检查不等同法定反洗钱 KYC 完成（§9.2） |
| `SIM-CAP-PRODUCT-REC` | 拆分 CAP-06/CAP-07 前不得作为单一能力对外声明 |
| `SIM-CAP-REPORT-ASSEMBLE` | 见 R-3 生命周期登记 |
| `SIM-CAP-MEETING-SCRIPT` / `SIM-CAP-OUTREACH-SCRIPT` | 代码有实现不等于已通过语义探针 |

---

## 2. R-2：显式 ID 映射

### 2.1 新增合同

`specs/knowledge-architecture/registry/CapabilityIdMapping.json`

**登记 10 条全链映射** + 3 条未映射代码侧技能 + 3 条能力缺口。

### 2.2 映射结果（诚实结论）

```json
"summary": {
  "provenCompatible": 0,
  "pending": 8,
  "noCounterpart": 2,
  "provenIncompatible": 0,
  "statement": "无一项达到 PROVEN_COMPATIBLE。
                本表的作用是阻止同名自动兼容，不是宣称兼容已成立。"
}
```

**→ 无一项已证实兼容**。这是**正确的结果**，不是修复失败 ——
建议书 §9.2 要求「**文档存在、包可以加载、代码有同名字符串，都不是实际语义兼容的充分证据**」。

### 2.3 三套命名的正式定义

| 命名系 | 定义 | 例 |
|---|---|---|
| `documentedDir` | KERT `examples/bank-front-skills/<dir>/` 目录名 | `bank-front-fact-reconciliation` |
| `documentedNumber` | 正文编号 `SK-FRONT-00x`，**不按目录顺序** | `SK-FRONT-004` |
| `codeSideId` | `skills.py` `registry()` 中 `skillId` 字面量 | `skill-customer-outreach-script` |

### 2.4 `forbiddenAssumptions`（10 条禁止推定）

把 WP01 §8 的 10 条禁止推定**固化进合同**，使其可被门禁引用：

```
1.  不得按名称推定 bank-front-X 与 SIM-CAP-Y 兼容
2.  不得推定 skill-customer-* 与 bank-front-* 是同一能力的两个名字
3.  不得按目录名顺序推定 SK-FRONT-00x 编号
4.  不得因 SKILL.md 存在即认定技能可调用
5.  不得因 registry 含字符串即认定实现已存在
6.  不得因 frontmatter 有 version 即认定存在版本化契约
7.  不得因 T-MARKET-001 是智能体即视其输出为权威研究结果
8.  不得因 supply-chain-graph 可被包加载即认定多跳图能力已实现
9.  不得把 SIM-MAP-FINANCE.json 的 status=VALIDATION 当作本图自身状态
10. 未在本表出现的映射不得被采用
```

---

## 3. R-3：生命周期冲突（**定性已更正**）

### 3.1 原假设

WP01 记为「**僵尸注册**：注释称已下线，但仍在 registry」。

### 3.2 实际核查结果（**已证实，与原假设不同**）

读取 `/home/szf/dev/Leibniz-KERT/src/kert/application/skills.py`，四处证据：

| 位置 | 内容 | 含义 |
|---|---|---|
| 第 5 行（头部注释） | 「两个独立 Skill：外联脚本 / 会面脚本（**R1 拜访报告已于 2026-08-21 下线移除**）」 | 声称已移除 |
| **第 169 行** | `SkillInfo("skill-customer-previsit-report", "R1 拜访报告", "1.0.0")` | **仍在 registry** |
| **第 218 行** | `if skill_id == "skill-customer-previsit-report":` —— 含 `exit_policy_no_new_evidence` 阻断逻辑 | **有专属业务分支** |
| **第 542 行** | `"skill-customer-previsit-report": self._run_previsit,` | **有 executor 映射** |
| **第 635 行** | `def _run_previsit(self, request, trace):` —— 含 `_call_model("previsit", ...)` | **有完整实现** |

**结论更正**：

> **不是僵尸注册。该技能代码完全存在且可达**（注册 → 分支 → 映射 → 实现四环完整）。
> **真实问题是「文档与代码不一致」**：
> 头部注释声称 2026-08-21 已下线移除，**但代码实际完整保留**，
> 且含 v1.3 的「无新证据策略」（`evidenceTimestamp` 未更新 → `exit_policy_no_new_evidence`）。

### 3.3 为什么这个更正很重要

| 若按原假设（僵尸注册）处置 | 按实际结论处置 |
|---|---|
| 直接从未就绪清单剔除 | **不可剔除** —— 它真的可执行 |
| 误判为"代码冗余，可清理" | **不可清理** —— 清理会破坏现有行为 |
| 结论：风险低 | 结论：**注释与实现矛盾，属治理问题**，须由 KERT 维护方裁定 |

### 3.4 登记处置

在 `Capability.json` 的 `SIM-CAP-REPORT-ASSEMBLE` 条目下：
```json
"lifecycleConflict": "R-3 已登记：KERT skills.py 文件注释称 R1 拜访报告
                      2026-08-21 已下线，但该 skillId 仍留在 registry() 硬编码列表中。
                      须确认是否为僵尸注册。"
```
并在 `CapabilityIdMapping.json` 的对应条目 `note` 中记录同等内容。

**未决**：注释与实现何者为准，**须 KERT 维护方确认**（我方不得单方面裁定）。

---

## 4. 门禁证据

### 4.1 `make check` **PASS**

```
contract-check: PASS
knowledge-architecture-check: PASS
{"activations": 3, "assets": 21, "maps": 4, "routes": 1, "schemas": 7, "skills": 5, "test_cases": 18}
loop-guard: PASS
secret-scan: PASS (with 124 advisory finding(s))
enum-consistency: PASS — 2 族受控枚举, 20 个 seed 文件
semantic-rule-gate: SHACL: PASS / Schema JSON: PASS / DMN: PASS / LinkML: PASS
gk-ke 合同样例: 正例通过 20/20，负例被拒 41 个
gk-ke-contract-examples: PASS
```

### 4.2 未触碰的保护

| 保护 | 状态 |
|---|---|
| `generated/` | **未手改**（AGENTS.md 明令禁止） |
| `_registry.json` 侧车清单 | **未手改**（`FAIL-2026-09-12-03` 禁止手工编辑） |
| `gk_ke_g2_definitions_check.py` 的 3 项定义 | **未改**（`make check` 仍 PASS） |
| 既有 Owner 决议 / QA 结论 | **未改** |
| P20 / DKES / PI-0 | **未绕过** |

---

## 5. 对建议书 §14.2 的影响评估

| §14.2 要求 | 修复前 | 修复后 |
|---|---|---|
| 「所需能力**真实可调用**（固定提供者、语义探针、实际调用结果、失败样例）」 | 注册中心仅 1 项，无法核对 | **10 项全部登记**，但 **callable 仅 1 项** → **仍不达标** |
| 「**不能接受的替代**：`DESIGN_ONLY`、健康端点或静态样例冒充结果」 | — | **已用 `callable=false` 落实该禁止** |
| 「能力之间**真正消费结果**」 | 仅 `optional` 关联 | **未改善**（属 WP05/WP06 范畴） |

**→ OC-04 仍不支持关闭**。本次修复**消除的是"信息不对称"**（注册中心与地图不一致），
**未消除"能力未就绪"**这一实质缺口。

**诚实表述**：R-1/R-2/R-3 的关闭**不等于** OC-04 推进 ——
它只是让"前进的门槛"从**看不清**变为**看得清**：
现在可明确知道 **9 项能力需要真实提供者与语义探针**。

---

## 6. 剩余未决项

| # | 事项 | 责任 | 阻塞 |
|---|---|---|---|
| U-A | R-3 注释与实现何者为准 | **KERT 维护方** | `SIM-CAP-REPORT-ASSEMBLE` 状态 |
| U-B | 9 项能力的 **providerId / version / endpoint / schema** 落地 | 集成合同负责人 | **WP05** |
| U-C | `SIM-CAP-PRODUCT-REC` 拆分为 CAP-06 / CAP-07 | 能力负责人 | WP05 |
| U-D | KERT 提交基线固定（工作区大量未提交改动） | KERT 维护方 | 证据可复现性 |
| U-E | 语义探针实现（"已知语义样例"而非 HTTP 200） | 工程 | `callable=true` 的判定 |

---

## 7. 边界声明

- 本次**未修改** `generated/`、`_registry.json` 侧车清单、既有 Owner 决议、QA 结论
- 本报告**不构成** OC-04 关闭证据，**不构成**能力就绪声明
- R-3 的定性**已从"僵尸注册"更正为"文档与代码不一致"**，处置权在 KERT 维护方
- 所有映射判定**无一项** `PROVEN_COMPATIBLE`，**未做任何兼容性推定**
