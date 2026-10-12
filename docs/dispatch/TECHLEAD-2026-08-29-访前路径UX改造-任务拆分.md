# Tech Lead 任务拆分：信号与互动·访前路径 UX 改造续作

> 日期：2026-08-29
> 对象：Tech Lead
> 前置：核心前端改造已完成（见 `HANDOFF-2026-08-29-访前路径UX改造.md`）
> 目的：把剩余续作拆成可独立分配、可验收的任务，明确依赖与优先级。

---

## 1. 任务总览

| 任务 | 标题 | 优先级 | 依赖 | 预估 | 类型 |
|---|---|---|---|---|---|
| T1 | P13→P14 导航断链修复 | P0 | 无 | 0.5 人日 | 前端 |
| T2 | e2e 测试适配（4 文件） | P0 | T1 | 1 人日 | 测试 |
| T3 | P15/P16/P17 补门禁面板 | P1 | 无 | 1 人日 | 前端 |
| T4 | 访前结果刷新持久化（方案 C） | P2 | Owner 决策 | 2 人日 | 前后端 |
| T5 | Owner 评审 + 客户经理走查 | P3 | T1–T3 | 2 人日 | 流程 |

---

## 2. 逐任务拆分

### T1 — P13→P14 导航断链修复（P0，前端）
- **问题**：`PrevisitEvidenceView.vue` 生成访前包后无「去访前包预览」入口。
- **改法**：在 `previsitDone` 分支加「去访前包预览」按钮（`data-testid="p13-go-pack"`），`router.push('/engagement/previsit/pack')` 携带 `customerId/journeyId/operatingCaseId/rmId` query。
- **验收**：P13 生成后可见入口；点击进入 P14 且访前包可见；`vitest` 补一条断言。

### T2 — e2e 测试适配（P0，测试）
- **范围**：`five-scenarios.live.spec.ts`、`signals-engagement.live.spec.ts`、`customer-manager-flow.spec.ts`、`full-experience.spec.ts`。
- **改法**：按 `HANDOFF` 第 3 节映射表替换失效 data-testid；删除螺旋工作台相关断言（`.sp-node`/`.sp-loop-badge`/`.ew-act`），改为断言 `stage-path`/`highlights-metrics`/`guidance-panel`。
- **验收**：`npx playwright test` 在本地后端启动时通过（或至少定位并注释不可跑项，不静默跳过）。

### T3 — P15/P16/P17 补门禁面板（P1，前端）
- **范围**：`InMeetingAssistant.vue` (P15)、`MeetingCaptureView.vue` (P16)、`MeetingCheckoutView.vue` (P17)。
- **改法**：加 `GuidancePanel`，文案取自 V3.2 设计 §15/§16/§17 的「下一步/业务规则/异常/契约」。
- **验收**：三页均有 `guidance-panel`；文案与 V3.2 一致；单测不回归。

### T4 — 访前结果刷新持久化（P2，前后端，待 Owner）
- **问题**：`previsitStore` 内存态，整页刷新丢 `previsitResult`。
- **方案 C**：后端新增 `GET /journey/{id}/previsit-result`（只读查询，不触发 Skill），前端刷新时读取。**须先改 OpenAPI（`make generate`）→ 需 Owner 批准**。
- **验收**：刷新 P13/P14 后访前结果仍在；不新增 KERT 调用。

### T5 — Owner 评审 + 客户经理走查（P3，流程）
- **范围**：设计候选冻结前，按 `docs/dd/...UX改造方案_V1.0` 第 7 节走查；确认 P11「标记准备完成」语义。
- **验收**：Owner 决策记录 + 6–8 名客户经理两条可用性任务完成率。

---

## 3. 依赖关系

```
T1 ──► T2（T2 依赖 T1 新增的 p13-go-pack）
T3（独立，可与 T1 并行）
T4（独立，但依赖 Owner 决策；不建议与 T1 并行以避 OpenAPI 冲突）
T5（依赖 T1、T2、T3 完成）
```

---

## 4. 风险清单

| 风险 | 概率 | 影响 | 缓解 |
|---|---|---|---|
| e2e 依赖后端环境，本地难全跑 | 中 | 中 | 明确「可跑 vs 注释」边界，不静默跳过 |
| T4 改 OpenAPI 与其他分支冲突 | 中 | 高 | 单独分支 + Owner 先行决策 |
| P11「标记准备完成」无后端状态机 | 高 | 中 | 保持前端派生，T5 确认 |
| 工作区既有未提交改动干扰 | 高 | 低 | 只改交接清单内文件 |

---

## 5. 统一验收标准

1. KERT 唯一入口不变，无新增 `prepare-previsit`/`executePrevisit` 重复调用。
2. 后端契约零变更（T4 除外，须 Owner 批准）。
3. `vue-tsc` 改动文件零新增错误；`vitest` 相关用例通过。
4. 一色一义色彩语义，无深红/深绿/深琥珀混用。
