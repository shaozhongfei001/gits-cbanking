# 任务交接文档：信号与互动·访前路径 UX 改造（待 CodeBuddy 续作）

> 日期：2026-08-29
> 交接人：需求分析师 / UX 设计师（本轮）
> 承接方：CodeBuddy
> 状态：核心改造已完成并验证通过；以下为**剩余续作任务**。

---

## 1. 背景与目标

V3.2 设计（`docs/dd/ui/GITS_Bank_对公客户经营UX与功能全量重构_V3.2_20260825/`，§11–§19）要求把「信号与互动 → 互动记录·访前路径」从旧的「单页 7 步手风琴卡片」重构为「对象主页 + 阶段 Path + 分页记录」。本轮已完成核心前端改造。

**硬约束（不可变更）**：「生成客户访前报告」仍通过 KERT 后台 `POST /journey/{id}/prepare-previsit`（3 个 `skill-customer-*` Skill 并行）获得。后端契约零变更。

---

## 2. 已完成内容（本轮交付）

### 2.1 新增文件
| 文件 | 作用 |
|---|---|
| `frontend/src/stores/previsit.ts` | Pinia 共享访前状态（KYC 缺口 + 一键访前结果 + 供应链图谱），P11–P14 共享 |
| `frontend/src/components/shell/GuidancePanel.vue` | 右侧四段式门禁面板（下一步/业务规则/异常/契约） |
| `frontend/src/components/shell/StagePath.vue` | 阶段 Path |
| `frontend/src/components/shell/HighlightsMetrics.vue` | 首屏四项指标 |
| `docs/dd/GITS_Bank_信号与互动_互动记录访前路径_UX改造方案_V1.0_20260829.md` | 差异分析 + 改造方案（设计候选） |

### 2.2 重构/修复文件
| 文件 | 改动 |
|---|---|
| `views/EngagementWorkspace.vue` (P11) | 7 步卡片 → 对象主页（对象头 + 指标 + 阶段 Path + 关键工作 + 时间线 + 门禁面板） |
| `views/PrevisitGapsView.vue` (P12) | 纯查询 KYC 缺口，接 store |
| `views/PrevisitEvidenceView.vue` (P13) | **移除 onMounted 自动调 KERT**；「生成访前包」= 唯一 KERT 入口 |
| `views/PrevisitPackView.vue` (P14) | **移除 executePrevisit**，改从 store 只读复用 |
| `views/PostvisitReconcileView.vue` (P18) | 加门禁面板 + 处理建议 + 冲突升级提示 |
| `views/CrmWritebackView.vue` (P19) | 加四项指标 + 差异预览表 + 门禁面板 |

### 2.3 同步更新的测试
`views/__tests__/EngagementWorkspace.spec.ts`、`PrevisitEvidenceView.spec.ts`、`PrevisitPackView.spec.ts`。

### 2.4 验证结果
- ✅ `vue-tsc --noEmit`：改动文件零错误（12 个既有错误在 `Claim` 类型无关文件，非本轮引入）
- ✅ `vite build`：成功
- ✅ `vitest run`（改造相关 6 个文件）：26/26 通过
- ⚠️ 全量单测：303 通过 / 5 失败（均为既有失败，在 `TimelineItem.spec.ts`、`EngagementsView.spec.ts`、`api/__tests__/engagement.spec.ts`，与本轮无关）

---

## 3. 剩余工作（按优先级）

### P0 — 必须完成：P13 → P14 导航断链
**问题**：P13「生成访前包」后只展示装配轨迹，**没有「去访前包预览」的入口**，用户无法自然流转到 P14。
**修复**：在 `PrevisitEvidenceView.vue` 的 `previsitDone` 分支增加「去访前包预览」按钮（`data-testid="p13-go-pack"`），导航到 `/engagement/previsit/pack`（携带 query 上下文）。

### P0 — 必须完成：e2e 测试适配（4 个文件）
旧 data-testid 已失效，需更新为新的。见下方映射表。

| 旧 data-testid | 新 data-testid / 替代方案 |
|---|---|
| `p11-object-context` | 已移除；用 `.ew-bar` 文本断言，或 `p11-select-customer` 存在性 |
| `p11-link-gaps` | `p11-open-previsit`（打开访前工作区 → P12） |
| `p11-link-evidence` | P12 的 `p12-go-evidence`（进入证据装配 → P13） |
| `p11-link-pack` | 待补的 `p13-go-pack`（见 P0 第一项） |
| `p11-link-postvisit` / `p11-link-crm` | 经会中→离场→访后→CRM 链路到达，不再有 P11 直达链接 |
| `p11-link-in-meeting` | `p11-mark-ready` 或 P14 的 `p14-complete` |
| `p11-subnav` | `signals-domain-tabs`（SignalsDomainTabs） |
| `p11-action-previsit` | P13 的 `p13-generate-pack` |
| `p11-dkws-call` | 已移除（KERT 调用提示移入 store，发生在 P13） |
| `.sp-node` / `.sp-label` / `.sp-loop-badge` / `.ew-act` | 螺旋工作台已移除；改为 `stage-path` / `highlights-metrics` |

受影响文件：`frontend/e2e/five-scenarios.live.spec.ts`、`signals-engagement.live.spec.ts`、`customer-manager-flow.spec.ts`、`full-experience.spec.ts`。

### P1 — 建议完成：P15/P16/P17 统一门禁面板
`InMeetingAssistant.vue` (P15)、`MeetingCaptureView.vue` (P16)、`MeetingCheckoutView.vue` (P17) 尚未加 `GuidancePanel`。为达到 V3.2 全链路一致，补右侧门禁面板（下一步/业务规则/异常/契约），内容参照 V3.2 设计 §15–§17。

### P2 — 待 Owner 决策：访前结果整页刷新持久化（方案 C）
当前 `previsitStore` 为内存态，整页刷新后 `previsitResult` 丢失。彻底解决需后端新增结果缓存查询 `GET /journey/{id}/previsit-result`（不触发 Skill）。**属后端变更，须 Owner 批准**，本轮不做。

### P3 — 流程验证：P11「标记准备完成」语义
当前「标记准备完成」为前端本地动作（`previsitDone` 后导航到会中）。需确认是否需要真实后端「访前门禁→会中」状态机。现状无对应后端契约，保持前端派生即可，但须 Tech Lead/Owner 确认。

---

## 4. 关键约束（必须遵守）

1. **KERT 唯一入口**：`prepare-previsit`（3 Skill 并行）。任何页面都不得再新增 `executePrevisit`、`preparePrevisit` 的重复调用。P13/P14 只读消费 store。
2. **后端契约零变更**：不新增/重命名/改动 OpenAPI 字段、枚举、状态、Action、权限语义。
3. **一色一义**：蓝=`--gits-blue-600`（动作/当前）、青绿=`--gits-teal-500`（确认/完成）、琥珀=`--gits-amber-400`（待处理/冲突/阻断）；不用深红/深绿。
4. **阶段 Path 由后端 `journey.phase` 驱动**，前端不可越级。

---

## 5. 验证方法

```bash
cd ~/dev/gits-knowledge-engineering/frontend
npx vue-tsc --noEmit          # 类型检查（排除既有 Claim 相关错误）
npx vite build                 # 打包（需写 node_modules/.vite-temp）
npx vitest run                # 单元测试
npx playwright test           # e2e（需后端与浏览器环境）
```

---

## 6. 风险与注意事项

- 本仓库工作区有大量**既有未提交改动**（Java 后端、其他视图、e2e、dist 等），非本轮产物。改动时只针对 `views/EngagementWorkspace.vue`、`Previsit*.vue`、`Postvisit*.vue`、`CrmWritebackView.vue`、`stores/previsit.ts`、`components/shell/{GuidancePanel,StagePath,HighlightsMetrics}.vue` 及相关测试。
- 不要删除/覆盖 `docs/dd/GITS_Bank_信号与互动_互动记录访前路径_UX改造方案_V1.0_20260829.md`。
- `fetchAssembledKnowledgeMap`（`GET /customer/{id}/knowledge-map`）**也触发 KERT Skill**（内部调用同一 `KnowledgeDrivenPrevisitReportGenerator.generate`），不是纯查询，P13 不得用它替代 store。
