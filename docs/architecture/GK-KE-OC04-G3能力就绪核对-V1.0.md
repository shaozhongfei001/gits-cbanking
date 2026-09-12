# GK-KE OC-04 · G-3 能力就绪核对（访前准备 7 能力）

> 角色：Tech Lead（planning_review）｜日期：2026-09-12
> 依据：Owner 确认 G-1~G-5；本文件落实 **G-3「能力是否从 1 个扩到 7 个」** 中的
> 「**需能力负责人确认真实能力是否已实现**」这一前置条件。
> 核对对象：`/home/szf/dev/Leibniz-KERT` @ `3b6640b`（`feat(kert): 规则包容器落地，rulePackageHash 改为真实文件哈希`）

---

## 1. 核对方法

三个来源交叉比对：

| 来源 | 路径 | 性质 |
|---|---|---|
| **A. 技能文档** | `examples/bank-front-skills/*/SKILL.md` | 设计制品（声明） |
| **B. 运行时代码** | `src/kert/application/skills.py` | 实现（可执行） |
| **C. 技能包仓库** | `src/kert/application/skills.py` 的包加载分支 | 实现（可执行） |

---

## 2. 核对结果：**文档 7 个 vs 代码 3+若干，存在口径差**

### 2.1 代码中**实际注册**的 skillId（`skills.py:539-543`）

```python
return {
    "skill-customer-outreach-script":  self._run_outreach,
    "skill-customer-meeting-script":   self._run_meeting,
    "skill-customer-previsit-report":  self._run_previsit,
}[skill_id]
```

**明确硬编码可执行的 3 个**：
| skillId | 方法 | 用途 |
|---|---|---|
| `skill-customer-outreach-script` | `_run_outreach` | 触达话术 |
| `skill-customer-meeting-script` | `_run_meeting` | 会面话术 |
| `skill-customer-previsit-report` | `_run_previsit` | **访前报告**（`_trace_knowledge_map("KM-CORP-RM-PREVISIT", "PRE_VISIT_PREPARATION")`） |

**另有技能包动态加载分支**（`skills.py:538` 之前的 `run_pkg` 路径），可按包加载
`bank-front-supply-chain-graph` 等（`skills.py` 中可见该字面量）。

### 2.2 文档侧声明的 **7 个** `bank-front-*` 技能

| # | 文档技能 | 代码状态 |
|---|---|---|
| 1 | `bank-front-supply-chain-graph` | **技能包加载**（代码中出现字面量，走包分支） |
| 2 | `bank-front-eight-dimension` | ❓ 仅文档 |
| 3 | `bank-front-fact-reconciliation` | ❓ 仅文档 |
| 4 | `bank-front-commitment-script` | ❓ 仅文档 |
| 5 | `bank-front-kyc-gap-check` | ❓ 仅文档 |
| 6 | `bank-front-product-recommendation` | ❓ 仅文档 |
| 7 | `bank-front-report-assembler` | ❓ 仅文档 |

### 2.3 差异总结

| 维度 | 数量 |
|---|---|
| 文档声明技能 | **7** |
| 代码硬编码可执行 | **3**（`skill-customer-*`，与 7 个命名不同） |
| 代码可包加载 | **≥1**（`bank-front-supply-chain-graph`） |
| **命名口径** | 文档用 `bank-front-*`，代码硬编码用 `skill-customer-*` —— **两套命名** |

---

## 3. G-3 处置结论

**按 Owner 确认执行，但必须分列「设计应有」与「已就绪」两栏。**
**不得**把文档声明的 7 个技能直接登记为「已就绪能力」。

### 3.1 地图中的能力清单（分列状态）

| 能力（对照文档） | 对应知识条目 | **就绪状态（实测）** | 依据 |
|---|---|---|---|
| 供应链图谱能力 | KI-FRONT-001 | **包加载可用**（待运行验证） | `skills.py` 含 `bank-front-supply-chain-graph` 字面量 |
| 八维研判能力 | KI-FRONT-002 | **设计待实现** | 仅 `SKILL.md`，代码无硬编码 |
| 事实对账能力 | KI-FRONT-003 | **设计待实现** | 仅 `SKILL.md` |
| 承诺话术能力 | KI-FRONT-004 | **设计待实现**（`_run_outreach` 功能相近但命名/合同不同） | 仅 `SKILL.md` |
| KYC 缺口能力 | KI-FRONT-005 | **设计待实现** | 仅 `SKILL.md` |
| 产品推荐能力 | KI-FRONT-006 | **设计待实现** | 仅 `SKILL.md` |
| 报告组装能力 | KI-FRONT-007 | **已实现（命名不同）** | `skill-customer-previsit-report` → `_run_previsit` |
| 会面话术能力 | —（额外） | **已实现** | `_run_meeting` |
| 触达话术能力 | —（额外） | **已实现** | `_run_outreach` |

### 3.2 命名口径差异（须记录，不静默抹平）

| 文档命名 | 代码命名 | 关系 |
|---|---|---|
| `bank-front-report-assembler` | `skill-customer-previsit-report` | 功能对应，**命名不同** —— 需显式转换登记 |
| `bank-front-commitment-script` | `skill-customer-outreach-script` / `_run_meeting` | 部分对应，**边界待确认** |
| 其余 4 个 | 无 | **未实现** |

---

## 4. 对地图设计的影响（重要）

按 G-3 的**诚实口径**，地图应这样登记：

```
能力引用（7 项设计需求 + 就绪状态标注）
├─ SIM-CAP-SUPPLY-CHAIN     ← 供应链图谱   [包加载可用, 待运行验证]
├─ SIM-CAP-EIGHT-DIMENSION  ← 八维研判     [DESIGN_ONLY 未实现]
├─ SIM-CAP-FACT-RECON       ← 事实对账     [DESIGN_ONLY 未实现]
├─ SIM-CAP-COMMITMENT       ← 承诺话术     [DESIGN_ONLY 未实现]
├─ SIM-CAP-KYC-GAP          ← KYC 缺口     [DESIGN_ONLY 未实现]
├─ SIM-CAP-PRODUCT-REC      ← 产品推荐     [DESIGN_ONLY 未实现]
└─ SIM-CAP-REPORT-ASSEMBLE  ← 报告组装     [已实现: skill-customer-previsit-report]
```

**关键约束（沿用 OWNER-003 §7.2 与 L4-1 口径）**：
- `DESIGN_ONLY` 能力**可登记为设计依赖**，但**不得在运行时就绪检查中放行**；
- 地图激活时若必需能力未就绪 → 应按 `REQUIRED_CAPABILITY_MISSING` **拒绝执行**（已有门禁覆盖）；
- **不得**把「设计应有」写成「已就绪」—— 这正是本程序反复避免的错误类型。

---

## 5. 待确认（提交能力负责人）

| # | 问题 |
|---|---|
| C-1 | `bank-front-supply-chain-graph` 的技能包加载是否**真实可用**？请给出一次成功调用证据 |
| C-2 | 文档 7 个技能与代码 `skill-customer-*` 的**命名映射**，是否有官方对照表？ |
| C-3 | 4 个「仅文档」技能（八维/对账/承诺/KYC/产品）**是否有实现计划与时间点**？ |
| C-4 | `bank-front-commitment-script` 是否等价于 `skill-customer-outreach-script`，还是两个不同能力？ |

---

## 6. 状态

| 项 | 状态 |
|---|---|
| G-3 核对 | ✅ 完成（本文档） |
| **OC-04** | ⛔ 仍未关闭，等地图重建后请 Owner 复核 |
| 下一步 | 按 G-1/G-2/G-4/G-5 重建地图知识广度；能力按 §3.1 分列就绪状态 |
