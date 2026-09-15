# Owner 评审核对清单 — 访前路径 UX 改造

> **日期**: 2026-08-30  
> **分支**: feature/P30-gits-bank-experience-shell  
> **核对范围**: P11–P14、P15–P17、P18、P19 设计意图 vs 实现一致性

---

## 1. 逐页核对

### P11 EngagementWorkspace（经营工作台）

| 维度 | 设计意图 | 实现状态 | 一致？ |
|------|---------|---------|--------|
| 信号域 Tab 导航 | 展示信号域分组，点击进入对应切片 | `signals-domain-tabs` data-testid | ✅ |
| 访前入口 | 单一入口按钮打开访前路径 | `p11-open-previsit` data-testid | ✅ |
| 启动旅程 | 按钮触发 `startJourney` | `p11-start-journey` data-testid | ✅ |
| 阶段路径 | 替代旧螺旋图，展示当前阶段 | `stage-path` data-testid | ✅ |
| 门禁状态 | 展示待审批门禁计数 | `gated-action` + `disabled-reason` | ✅ |
| 旧 data-testid 清理 | 移除 `p11-object-context`、`p11-subnav`、`p11-link-*` | 已移除，e2e 已适配 | ✅ |

### P12 PrevisitGapsView（访前目标与信息缺口）

| 维度 | 设计意图 | 实现状态 | 一致？ |
|------|---------|---------|--------|
| KYC 缺口画像 | 展示 `fetchKycGapProfile` 结果 | `p12-gap-list` data-testid | ✅ |
| 纯查询，不调 KERT | 明确标注"本页不触发 KERT" | GuidancePanel 中注明 | ✅ |
| 契约策略 | `REUSE_EXISTING` | GuidancePanel `contract-usage` 标注 | ✅ |
| P12→P13 导航 | 缺口页 → 证据装配页 | `p12-go-evidence` data-testid | ✅ |
| 一键访前按钮 | 缺口页触发 KERT | `p12-generate-pack` data-testid | ✅ |

### P13 PrevisitEvidenceView（访前知识证据装配）

| 维度 | 设计意图 | 实现状态 | 一致？ |
|------|---------|---------|--------|
| **KERT 唯一入口** | **禁止 onMounted 自动调用** | `onMounted` 只调 `syncContext`，不调 KERT | ✅ |
| 装配轨迹展示 | 展示 `assemblyTrace` 派生视图 | `p13-trace-list` data-testid | ✅ |
| 证据来源展示 | 派生来源视图 | `p13-source-list` data-testid | ✅ |
| 契约策略 | `DERIVED_READ_ONLY` | GuidancePanel 标注 | ✅ |
| P13→P14 导航 | 证据装配 → 访前包预览 | `p13-go-pack` data-testid | ✅ |
| 空 state | 一键访前未执行时提示 | `p13-empty` data-testid | ✅ |
| 单元测试 | 覆盖核心行为 | 8 项测试全通过 | ✅ |

### P14 PrevisitPackView（访前包预览）

| 维度 | 设计意图 | 实现状态 | 一致？ |
|------|---------|---------|--------|
| **禁止 executePrevisit** | **只读消费 previsitStore** | 已移除 `executePrevisit` 调用 | ✅ |
| 访前包展示 | 外联/会面/报告/速战卡 | `p14-pack-content` data-testid | ✅ |
| 契约策略 | `REUSE_EXISTING` | GuidancePanel 标注 | ✅ |
| P14→P13 返回 | 返回装配页 | `p14-back-evidence` data-testid | ✅ |
| 完成准备按钮 | 进入会中 | `p14-complete` data-testid | ✅ |
| 单元测试 | 覆盖核心行为 | 3 项测试全通过 | ✅ |

### P15 InMeetingAssistant（会中工作区）

| 维度 | 设计意图 | 实现状态 | 一致？ |
|------|---------|---------|--------|
| 门禁面板 | GuidancePanel 展示下一步/规则/异常/契约 | 已添加 | ✅ |
| 待审批门禁 | 展示 HumanGate 列表 | `p15-in-meeting` data-testid | ✅ |
| CRM 写回 | 展示写回命令 | 已实现 | ✅ |
| 禁止正式 Claim | DisabledAction 约束 | 已实现 | ✅ |
| P15→P16 导航 | 进入实时捕获 | `p15-go-capture` | ✅ |
| P15→P17 导航 | 进入离场确认 | `p15-go-checkout` | ✅ |

### P16 MeetingCaptureView（会中实时捕获）

| 维度 | 设计意图 | 实现状态 | 一致？ |
|------|---------|---------|--------|
| 门禁面板 | GuidancePanel | 已添加 | ✅ |
| 候选标注 | 明确标注"候选 · 非正式 Claim" | `p16-candidate-label` | ✅ |
| 禁止提交正式 Claim | DisabledAction | 已实现 | ✅ |
| 转写降级 | 转写失败切手工速记 | `p16-manual-fallback` | ✅ |

### P17 MeetingCheckoutView（离场确认）

| 维度 | 设计意图 | 实现状态 | 一致？ |
|------|---------|---------|--------|
| 门禁面板 | GuidancePanel | 已添加 | ✅ |
| E01_EXIT_CONFIRM 门禁 | 结束会谈必须走 HumanGate | 已实现 | ✅ |
| 离场清单 | 双方确认清单（草稿） | `p17-checklist` | ✅ |
| 契约策略 | `REUSE_EXISTING` | GuidancePanel 标注 | ✅ |

### P18 / P19（访后 / CRM 写回）

| 维度 | 设计意图 | 实现状态 | 一致？ |
|------|---------|---------|--------|
| P18 访后 | 未在本次改造范围 | 保留现有壳层 | ✅ |
| P19 CRM 写回 | 未在本次改造范围 | 保留现有壳层 | ✅ |

---

## 2. KERT 唯一入口约束核验

| 检查项 | 结果 | 证据 |
|--------|------|------|
| P13 `onMounted` 不调 `preparePrevisit` | ✅ 通过 | `onMounted` 只调 `syncContext` |
| P14 不调 `executePrevisit` | ✅ 通过 | 已移除，改为只读消费 `previsitStore` |
| KERT 入口统一在 `previsitStore.runPrevisit` | ✅ 通过 | 唯一入口 |
| P12 一键访前按钮调 `previsitStore.runPrevisit` | ✅ 通过 | `p12-generate-pack` |
| 无重复 KERT 调用 | ✅ 通过 | P13/P14 不触发新 Skill |

---

## 3. 差异点记录

### 3.1 设计文档描述但代码未实现

| # | 差异 | 优先级 | 说明 |
|---|------|--------|------|
| 1 | T4 刷新持久化 | P2 | 需 Owner 决策是否实施方案 C（后端增加结果缓存查询 API） |
| 2 | P15/P16/P17 单元测试 | P1 | 提示词 3 要求补测试，尚未完成 |

### 3.2 代码实现但设计文档未记录

| # | 差异 | 说明 |
|---|------|------|
| 1 | `p14-back-evidence` 返回按钮 | V3.2 未描述 P14→P13 返回导航，但实现中已添加 |
| 2 | `p12-go-evidence` 导航按钮 | V3.2 未描述 P12→P13 导航，但实现中已添加 |
| 3 | `p13-go-pack` 导航按钮 | V3.2 未描述 P13→P14 导航，但实现中已添加 |

### 3.3 e2e 测试适配

| # | 文件 | 状态 |
|---|------|------|
| 1 | `five-scenarios.live.spec.ts` | ✅ 已适配 |
| 2 | `signals-engagement.live.spec.ts` | ✅ 已适配 |
| 3 | `customer-manager-flow.spec.ts` | ✅ 已适配 |
| 4 | `full-experience.spec.ts` | ✅ 已适配 |

---

## 4. 验证结果

| 验证项 | 结果 |
|--------|------|
| `vue-tsc --noEmit` | ✅ 访前/会中相关文件无类型错误 |
| `vitest run` (P13/P14 单元测试) | ✅ 11/11 通过 |
| `vitest run` (全量) | ⚠️ 3 个存量失败（ClaimsView 等，非本次引入） |
| GuidancePanel (P15/P16/P17) | ✅ 已添加 |
| e2e data-testid 适配 | ✅ 4 文件已更新 |

---

## 5. 待 Owner 决策

| # | 决策项 | 选项 | 建议 |
|---|--------|------|------|
| 1 | T4 刷新持久化 | A: 不做（接受刷新丢状态）/ C: 增加后端缓存查询 API | 建议先 A，后续按需 C |
| 2 | P15/P16/P17 单元测试 | 补 / 不补 | 建议补（P1） |
| 3 | 导航按钮是否需 V3.2 设计文档补录 | 补录 / 不补录 | 建议补录（避免审计差异） |

---

*核对人：CodeBuddy（AI 辅助）*  
*核对时间：2026-08-30*
