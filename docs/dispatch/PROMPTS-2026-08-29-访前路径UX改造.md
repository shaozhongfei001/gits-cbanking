# CodeBuddy 提示词：信号与互动·访前路径 UX 改造续作

> 用法：把每个提示词**原样粘贴**给 CodeBuddy（工作目录 `~/dev/gits-knowledge-engineering`）。每个提示词自包含，不依赖对话上下文。
> 通用背景：核心改造已完成（见 `docs/dispatch/HANDOFF-2026-08-29-访前路径UX改造.md`）。硬约束：KERT 唯一入口 `prepare-previsit` 不变、后端契约零变更。

---

## 提示词 1：修复 P13→P14 导航断链（T1）

```
你是前端工程师，工作在 ~/dev/gits-knowledge-engineering 项目。

背景：刚完成「信号与互动·互动记录·访前路径」的 UX 重构。P13 页面（frontend/src/views/PrevisitEvidenceView.vue）
的「生成访前包」按钮触发 KERT 一键访前（store 的 runPrevisit），结果写入 Pinia store（frontend/src/stores/previsit.ts）。
但当前 P13 生成完成后没有跳转到 P14（访前包预览）的入口，用户无法自然流转。

任务：
1. 在 PrevisitEvidenceView.vue 的 `previsitStore.previsitDone` 为 true 的分支里，增加一个「去访前包预览」按钮，
   data-testid="p13-go-pack"，点击后 router.push 到 /engagement/previsit/pack，query 携带 customerId/journeyId/operatingCaseId/rmId
   （这些值来自 useEngagementContext）。
2. 参考同文件里已有的 goEvidence 导航写法（P12 的 PrevisitGapsView.vue 里 goEvidence 是现成示例）。

约束：
- 不改动 KERT 调用逻辑（不新增 preparePrevisit/executePrevisit 调用）。
- 后端契约零变更。
- 保持一色一义，按钮用主色（品牌蓝 --brand-primary）。

验收：
- 在 frontend/src/views/__tests__/PrevisitEvidenceView.spec.ts 补一条测试：seed store 的 previsitResult 后，
  p13-go-pack 按钮可见，点击后路由到 /engagement/previsit/pack。
- 运行 `cd frontend && npx vue-tsc --noEmit`（改动文件零新增错误，忽略 Claim 相关的既有错误）和
  `npx vitest run src/views/__tests__/PrevisitEvidenceView.spec.ts` 确认通过。
```

---

## 提示词 2：e2e 测试适配（T2）

```
你是测试工程师，工作在 ~/dev/gits-knowledge-engineering 项目。

背景：刚完成「互动记录·访前路径」UX 重构，P11 从「7 步手风琴卡片」改为「对象主页 + 阶段 Path + 门禁面板」，
一些旧 data-testid 已失效。需要更新 4 个 e2e 测试文件：
- frontend/e2e/five-scenarios.live.spec.ts
- frontend/e2e/signals-engagement.live.spec.ts
- frontend/e2e/customer-manager-flow.spec.ts
- frontend/e2e/full-experience.spec.ts

旧→新映射：
- p11-object-context  → 已移除；改用 .ew-bar 文本断言，或断言 p11-select-customer 存在
- p11-link-gaps      → p11-open-previsit（打开访前工作区 → P12）
- p11-link-evidence  → P12 的 p12-go-evidence（进入证据装配 → P13）
- p11-link-pack      → P13 的 p13-go-pack（去访前包预览，T1 新增）
- p11-link-postvisit / p11-link-crm → 经会中→离场→访后→CRM 链路到达，无 P11 直达
- p11-link-in-meeting → p11-mark-ready 或 P14 的 p14-complete
- p11-subnav         → signals-domain-tabs
- p11-action-previsit → P13 的 p13-generate-pack
- p11-dkws-call      → 已移除
- .sp-node / .sp-label / .sp-loop-badge / .ew-act（螺旋工作台）→ 改为 stage-path / highlights-metrics / guidance-panel

任务：
1. 逐文件替换上述失效 data-testid。
2. 删除螺旋工作台相关断言，改为断言 stage-path、highlights-metrics、guidance-panel 的存在。
3. 检查还有没有其它对已移除元素的引用（如 full-experience.spec.ts 里的「螺旋」文本断言）。

约束：
- 只改这 4 个 e2e 文件，不动其它文件。
- 如某个用例依赖未就绪的后端/环境，明确标注 `// TODO(e2e): needs backend`，不要静默 skip 或删断言。

验收：
- `grep -rn "p11-object-context\|sp-node\|sp-loop-badge\|ew-act\|p11-link-" frontend/e2e/` 应无残留（除注释说明）。
- 尽量本地 `npx playwright test` 验证可跑项。
```

---

## 提示词 3：P15/P16/P17 补门禁面板（T3）

```
你是前端工程师，工作在 ~/dev/gits-knowledge-engineering 项目。

背景：已完成 P11–P14、P18、P19 的右侧「门禁面板」（组件 frontend/src/components/shell/GuidancePanel.vue）改造。
现在需要给会中阶段的三个页面补上统一门禁面板：
- frontend/src/views/InMeetingAssistant.vue（P15 会中工作区）
- frontend/src/views/MeetingCaptureView.vue（P16 会中实时捕获）
- frontend/src/views/MeetingCheckoutView.vue（P17 离场确认）

参考：PrevisitGapsView.vue / PrevisitEvidenceView.vue 里已用 GuidancePanel 的写法（2 栏 grid + 右侧面板）。

文案取自 V3.2 设计（docs/dd/ui/GITS_Bank_对公客户经营UX与功能全量重构_V3.2_20260825/GITS_Bank_对公客户经营_前端UX与操作需求_V3.2_20260825.md）：
- P15：下一步=「点击笔记可转候选事实、需求或承诺；所有转化需人工确认」；业务规则=「会中笔记只有经人工确认才转为事实、需求或承诺」；契约=REUSE_EXISTING。
- P16：下一步=「逐条选择类型和证据级别；未经确认不进入正式客户事实」；业务规则=「AI仅输出候选结构；低置信度项必须进入人工确认队列」；契约=CANDIDATE_OUTPUT。
- P17：下一步=「未确认内容保留客户陈述/待核实，结束后进入访后事实对账」；业务规则=「未确认内容保持客户陈述或待核实状态，不伪装成银行事实」；契约=CONTROLLED_ACTION。

任务：给这三页分别加 GuidancePanel（放右侧 2 栏布局），动作按钮用 slot 传入门禁面板，文案按上面。

约束：不改动既有 HumanGate/CRM 调用逻辑；后端契约零变更；一色一义。

验收：三页均渲染 data-testid="guidance-panel"；运行 `cd frontend && npx vue-tsc --noEmit` 和
`npx vitest run src/views/__tests__/InMeetingAssistant.spec.ts src/views/__tests__/MeetingCaptureView.spec.ts src/views/__tests__/MeetingCheckoutView.spec.ts` 确认不回归（如需改测试，同步更新）。
```

---

## 提示词 4：Owner 评审材料核对（T5 前置）

```
你是需求分析师，工作在 ~/dev/gits-knowledge-engineering 项目。

背景：访前路径 UX 改造的核心实现已完成，文档在：
- docs/dd/GITS_Bank_信号与互动_互动记录访前路径_UX改造方案_V1.0_20260829.md（设计候选 + 差异分析）
- docs/dispatch/HANDOFF-2026-08-29-访前路径UX改造.md（交接）
- docs/dispatch/TECHLEAD-2026-08-29-访前路径UX改造-任务拆分.md（任务拆分）

任务：核对「设计文档」与「已实现代码」的一致性，输出一份核对清单（markdown），逐页列出：
1. 每个页面（P11–P14、P18、P19）的设计意图 vs 实现是否一致。
2. KERT 唯一入口约束是否在代码中落实（重点：PrevisitEvidenceView 是否还有 onMounted 自动调用、PrevisitPackView 是否还有 executePrevisit）。
3. 有没有设计文档描述但代码未实现、或代码实现但文档未记录的差异点。

约束：只读分析，不改代码。核对清单写入 docs/dispatch/OWNER_CHECKLIST-2026-08-29-访前路径.md。
```

---

## 附加说明

- 每个提示词都强调「后端契约零变更」与「KERT 唯一入口」，因为这是本项目最易被无意破坏的约束。
- 若 CodeBuddy 需要跑 `vite build` 或 `vitest`，需确保有写 `node_modules/.vite-temp` 的权限（本仓库环境可能要求提权）。
- T4（刷新持久化/方案 C）因涉及 OpenAPI 变更，**不要**让 CodeBuddy 直接做，必须先由 Tech Lead 拿到 Owner 决策。
