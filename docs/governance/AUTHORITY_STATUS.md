# GITS-KNO 权威状态索引

> **⚠️ 本文档为唯一权威状态来源。** 其他文件（`docs/governance/STATUS.md`、`specs/SPEC_INDEX.md`、`README.md`）的状态声明必须引用本文件，不得各自独立声明。
>
> 最后更新：2026-08-24  
> 更新角色：Tech Lead（P24 REM-P0-05 整改）  
> Tech Lead 只能整理事实和提出候选状态。涉及正式冻结、Owner 签署和 CCB 批准时标记 `AWAITING_BASELINE_OWNER_DECISION`。

## 1. 项目级状态

| 字段 | 值 | 来源 | 备注 |
|------|-----|------|------|
| `PACKAGE_ID` | GITS-KNO-DEV-PACKAGE-V0.1 | BASELINE_INDEX | |
| `FRAMEWORK_ID` | GITS-SDD-FRAMEWORK-V0.2 | BASELINE_INDEX | |
| `CURRENT_MATURITY` | M2_ENGINEERING_PROTOTYPE | ARCH-REVIEW-2026-08-23-001 | 架构委员会评审结论 |
| `FROZEN` | **CONFLICT** | — | 见下方冻结状态分析 |
| `PRODUCTION_READY` | NO | SPEC_INDEX + ARCH-REVIEW | 多处一致确认 |
| `QA_PASS` | NO (LOOP_SCOPED_ONLY) | SPEC_INDEX | 仅 P0-P10 有独立 QA 签署 |
| `INDEPENDENT_QA_REQUIRED` | YES | ARCH-REVIEW | P24 必须独立 QA |

## 2. 冻结状态分析

**矛盾**：以下文件对冻结状态声明不一致：

| 文件 | 冻结声明 | 时间 |
|------|----------|------|
| `docs/governance/STATUS.md` | `FROZEN=YES_2026_08_06_CUSTOMER_SIGNED` | 2026-08-06 |
| `specs/BASELINE_INDEX.yaml` | `freeze_state=FROZEN_2026_08_06` | 2026-08-06 |
| `specs/SPEC_INDEX.md` | `FROZEN=NO` | — |
| `README.md` | `FROZEN=NO` | — |
| `ARCH-REVIEW-2026-08-23-001` | `GATE_DECISION=BLOCKED` | 2026-08-23 |

**事实**：
- 2026-08-06 客户签字确认基线冻结（P16 交付包）
- 冻结后（2026-08-06 至 2026-08-24）已有 **69+ 个提交**变更了代码、合同和文档
- P17-P24 均在冻结后实施，改变了冻结基线

**Tech Lead 候选状态**：

```text
FREEZE_STATUS=PARTIALLY_INVALIDATED
FREEZE_DATE=2026-08-06
FREEZE_SCOPE=P16_DELIVERY_PACKAGE
POST_FREEZE_COMMITS=69+
POST_FREEZE_LOOPS=P17,P18,P19,P20,P21,P22,P23,P24
FREEZE_INTEGRITY=COMPROMISED_BY_POST_FREEZE_CHANGES
AWAITING_BASELINE_OWNER_DECISION=YES
REQUIRED_OWNER_ACTION=确认冻结范围是否仍有效，或重新冻结
```

## 3. Loop 状态补录

| Loop | 状态 | QA Actor | 关闭依据 | 治理归属 |
|------|------|----------|----------|----------|
| P0-P10 | completed/closed | independent_qa | 各自 EVIDENCE.json | 冻结前 |
| P11 | completed | tech_lead | DMN 引擎实现 | 冻结后，无独立 QA |
| P12-P18 | completed | tech_lead | 各自 EVIDENCE.json | 冻结后，无独立 QA |
| P19 | in_progress | — | DEV_SELF_CHECK_PASS | 冻结后，独立 QA 待执行 |
| P20 | closed | tech_lead | 合同候选 | 冻结后，无独立 QA |
| P21 | closed | tech_lead | 生产就绪 | 冻结后，无独立 QA |
| P22 | closed | independent_qa | QA_PASS (qa-p22-formal-001) | 冻结后，唯一独立 QA |
| P23 | ready_for_independent_qa | — | DEV_SELF_CHECK_PASS | 冻结后，独立 QA 待执行 |
| P24 | in_dev | — | 架构整改中 | 冻结后，BLOCKED |

**注意**：P11-P21（除 P22）均由 tech_lead 自检通过，无独立 QA 签署。按项目规范，tech_lead 自检最多记录 `DEV_SELF_CHECK_PASS`，不得记录 `QA_PASS`。

## 4. 冻结后变更治理

冻结后 69+ 个提交的变更治理情况：

| 类别 | 数量 | 治理状态 |
|------|------|----------|
| 合同变更 | 6+ | CCB 审批记录缺失 |
| 代码新增/修改 | 50+ | Loop 内自检，无独立 QA |
| 适配器删除 | 1 (knowledge-filesystem) | 无 CCB 审批记录 |
| 文档变更 | 10+ | 无变更控制 |
| CI 变更 | 1+ | 无变更控制 |

**AWAITING_BASELINE_OWNER_DECISION**：是否需要补办 CCB 审批，或接受冻结后变更。

## 5. QA 责任人

| Loop | QA 责任人 | 状态 |
|------|-----------|------|
| P0-P10 | independent_qa_agent/subagent | 已签署 |
| P11-P21 | tech_lead (自检) | ⚠️ 缺独立 QA |
| P22 | independent_qa (qa-p22-formal-001) | 已签署 |
| P23 | 待指定 | 待执行 |
| P24 | 待指定 | 待执行 |

## 6. Owner 签署状态

| 项目 | 签署状态 |
|------|----------|
| P16 交付包冻结 | ✅ 客户签字 (2026-08-06) |
| P17-P24 变更授权 | ⚠️ AWAITING_BASELINE_OWNER_DECISION |
| knowledge-filesystem 删除 | ⚠️ AWAITING_BASELINE_OWNER_DECISION |
| 生产部署 | ❌ 未授权 |
| 公开仓库 | ⚠️ AWAITING_LEGAL_DECISION |

## 7. 引用本文件的其他状态文件

以下文件的状态声明应引用本文件：

- `docs/governance/STATUS.md` — 历史状态记录，新增条目必须引用本文件
- `specs/SPEC_INDEX.md` — 显式非声明部分引用本文件
- `README.md` — 项目状态部分引用本文件
