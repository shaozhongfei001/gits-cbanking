# 交接文档：信号与互动·访前路径 UX 改造（最终状态）

> 日期：2026-08-30
> 交接人：Tech Lead（本次会话）
> 承接方：CodeBuddy
> 状态：**核心改造 + 全部测试已通过并推送远程**。本文件取代旧的三份 `HANDOFF/TECHLEAD/PROMPTS-2026-08-29` 与 `OWNER_CHECKLIST`。

---

## 1. 一句话摘要

「信号与互动 → 互动记录·访前路径」已从旧的「单页 7 步手风琴卡片」重构为「对象主页 + 阶段 Path + 分页记录」，KERT 唯一入口约束落实，后端重建重启，**类型检查 / 单元测试 / mock e2e / live e2e 全部通过**，已提交并推送远程。

---

## 2. 当前状态（已验证）

### 2.1 Git
- 分支：`feature/P30-gits-bank-experience-shell`
- 工作树：**干净**，与 `origin` **同步**（无领先/落后）
- HEAD：`8c3fe7e`，最近 4 个提交：
  ```
  8c3fe7e fix: clear out-of-scope pre-existing failures
  bab8e0c fix(P30): Tech Lead E2E review — make visit-path flow pass live/mock e2e
  3136019 feat(P30): complete all dispatch tasks（CodeBuddy）
  b1f7093 feat(P30): previsit workflow UX overhaul（核心改造）
  ```

### 2.2 测试结果（全部通过）
| 验证 | 命令 | 结果 |
|---|---|---|
| 类型检查 | `cd frontend && npx vue-tsc --noEmit` | ✅ 0 错误 |
| 单元测试 | `cd frontend && npx vitest run` | ✅ 311/311 |
| Mock E2E | `cd frontend && npx playwright test` | ✅ 38/38 |
| Live E2E | `cd frontend && npx playwright test --config playwright.live.config.ts` | ✅ 11/11 |
| 生产构建 | `cd frontend && npx vite build` | ✅ 通过（仅既有 chunk size 提示） |

### 2.3 运行环境（当前都在运行且健康）
| 服务 | 端口 | 状态 | 启动方式 |
|---|---|---|---|
| 后端 GITS API | 8082 | UP | `./mvnw spring-boot:run -pl apps/api -Dspring-boot.run.profiles=dev -Dspring-boot.run.arguments=--server.port=8082` |
| 前端 Vite | 5173 | 200 | `cd frontend && npm run dev -- --host 0.0.0.0 --port 5173`（`/api` 代理到 8082） |
| KERT Skill Runtime | 8106 | ok | `spring-ai-alibaba-skill-runtime`（位于 `~/dev/deepseek_harness/data_knowledge_ws/dkws/poc/spring-ai-alibaba-skill-runtime`），3 个 `skill-customer-*` 已就绪 |

> ⚠️ 后端 `spring-boot:run -pl apps/api` 从 `.m2` 加载依赖模块 JAR。**改了后端任何模块（`modules/*` / `adapters/*`）后必须 `./mvnw install -DskipTests -Ddependency-check.skip=true` 并重启 8082**，否则出现 `NoSuchMethodError`（本次已踩坑）。

---

## 3. 已完成工作清单

### 3.1 前端核心改造（P11–P14、P18、P19）
| 文件 | 改动 |
|---|---|
| `stores/previsit.ts` | 新增 Pinia 共享访前状态（KYC 缺口 + 一键访前结果 + 供应链图谱） |
| `components/shell/GuidancePanel.vue` / `StagePath.vue` / `HighlightsMetrics.vue` | 新增门禁面板 / 阶段 Path / 四项指标组件 |
| `views/EngagementWorkspace.vue` (P11) | 7 步卡片 → 对象主页（对象头 + 指标 + 阶段 Path + 关键工作 + 时间线 + 门禁面板） |
| `views/PrevisitGapsView.vue` (P12) | 纯查询 KYC 缺口，接 store |
| `views/PrevisitEvidenceView.vue` (P13) | 移除 onMounted 自动调 KERT；「生成访前包」= 唯一 KERT 入口 |
| `views/PrevisitPackView.vue` (P14) | 移除 executePrevisit 重复调用，改 store 只读复用 |
| `views/PostvisitReconcileView.vue` (P18) | 加门禁面板 + 处理建议 + 冲突升级提示 |
| `views/CrmWritebackView.vue` (P19) | 加四项指标 + 差异预览 + 门禁面板 |
| `views/InMeetingAssistant.vue` / `MeetingCaptureView.vue` / `MeetingCheckoutView.vue` (P15–P17) | 补门禁面板 |

### 3.2 关键修复（Tech Lead 审核阶段）
- **KERT 重复调用消除**：P13 不再自动触发、P14 不再调 `executePrevisit`，单入口 `prepare-previsit`。
- **导航断链修复**：`p13-go-pack` 移到 toolbar（始终可见），P11 `p11-open-previsit` 按客户启用。
- **后端 `NoSuchMethodError`**：重建重装 `scenario-customer-journey` 模块 + 重启 8082。

### 3.3 范围外遗留修复
- `Claim` 接口兼容 statement 型 + content 型两种后端形状（消除 12 个类型错误）。
- `TimelineItem` / `EngagementsView` / `engagement.spec` / `journey.spec` 等 7 个过时测试与 mock 修正。

---

## 4. 关键约束（CodeBuddy 接手必须遵守）

1. **KERT 唯一入口**：访前报告仅通过 `POST /journey/{id}/prepare-previsit`（3 个 `skill-customer-*` 并行）。任何页面不得新增 `executePrevisit` / `preparePrevisit` 重复调用；P13/P14 只读消费 `previsitStore`。
2. **后端契约零变更**（除非 Owner 明确批准）：不改 OpenAPI 字段、枚举、状态、Action、权限语义。
3. **`fetchAssembledKnowledgeMap`（`GET /customer/{id}/knowledge-map`）也触发 KERT**（内部调用同一 report generator），不是纯查询——P13 不得用它替代 store。
4. **一色一义**：蓝 `--gits-blue-600`=动作/当前、青绿 `--gits-teal-500`=确认/完成、琥珀 `--gits-amber-400`=待处理/冲突/阻断；不用深红/深绿。
5. **阶段 Path 由后端 `journey.phase` 驱动**，前端不可越级。

---

## 5. 剩余待办（按优先级）

### P1 — T4：访前结果整页刷新持久化（方案 C，需 Owner 决策）
- **问题**：`previsitStore` 是内存态，整页刷新后 `previsitResult` 丢失，P13/P14 回退到空态。
- **方案 C**：后端新增只读查询 `GET /journey/{id}/previsit-result`（不触发 Skill），前端刷新时读取。
- **属后端 + OpenAPI 变更**，须 Owner 批准后单独分支实施（参考 `docs/analysis/PREVISIT_WORKFLOW_ANALYSIS_V3.2.md` §7.3）。

### P2 — T5：Owner 评审 + 客户经理走查
- 设计候选冻结前：6–8 名客户经理两条可用性任务（持续经营、建议书生成）+ 产品/风险/合规逐页核对 + Owner 决策记录。

### P3 — P11「标记准备完成」语义确认
- 当前是前端本地动作（`previsitDone` 后导航到会中），无后端「访前门禁→会中」状态机。需 Tech Lead/Owner 确认是否需要后端状态机，否则保持前端派生。

### P4 — 更广范围（非本次核心，可选）
- P15–P17 会中流程（转写/AI 结构化/离场）仍是 C2 降级壳层；移动端 P41–P44 降级壳层；建议书 G0–G5 阶段机未授权。这些属于后续 Loop，不在本次访前路径范围内。

---

## 6. CodeBuddy 接手提示词（可直接粘贴）

> 通用背景请先让 CodeBuddy 读本文件 §1–§4。

### 提示词 A — 接手核对（建议先做）
```
你是前端工程师，工作在 ~/dev/gits-knowledge-engineering 项目，分支 feature/P30-gits-bank-experience-shell。

请先阅读 docs/dispatch/HANDOFF-2026-08-30-访前路径UX改造-最终状态.md，然后核对当前状态：
1. git status 是否干净、与 origin 同步。
2. cd frontend && npx vue-tsc --noEmit 应为 0 错误。
3. npx vitest run 应 311/311；npx playwright test 应 38/38。
4. 后端 8082 /actuator/health 应为 UP；KERT 8106 /api/skill/health 应为 ok。

只做只读核对，输出一份核对结果（markdown），不要改任何代码。若发现不一致，列出差异点即可。
```

### 提示词 B — T4 刷新持久化（仅当 Owner 已批准后端变更）
```
（前置：Owner 已批准方案 C 后端变更，且你在独立分支）
实现访前结果整页刷新持久化：
1. 后端新增 GET /journey/{id}/previsit-result 只读查询，返回最近一次 prepare-previsit 结果，不触发 Skill。
2. 更新 OpenAPI（make generate）。
3. 前端 previsitStore 增加持久化读取：P13/P14 onMounted 时若内存无结果则调用该查询恢复。
4. 保持 prepare-previsit 仍是唯一 KERT 写入口。
验收：刷新 P13/P14 后访前结果仍在；不新增 KERT 调用；vue-tsc/vitest/playwright 全绿。
```

### 提示词 C — Owner 评审材料
```
你是需求分析师。核对 docs/dd/GITS_Bank_信号与互动_互动记录访前路径_UX改造方案_V1.0_20260829.md（设计候选）
与已实现代码（frontend/src/views/EngagementWorkspace.vue、Previsit*.vue、PostvisitReconcileView.vue、CrmWritebackView.vue、stores/previsit.ts）的一致性，
重点：KERT 唯一入口是否落实、P13/P14 是否只读、阶段 Path 是否由后端驱动。
输出一份 Owner 评审核对清单（markdown），列出设计 vs 实现差异、KERT 约束核验、待 Owner 决策项。
```

---

## 7. 环境操作速查

```bash
# 后端重启（改过后端模块后必须先 rebuild + restart）
cd ~/dev/gits-knowledge-engineering
./mvnw install -DskipTests -Ddependency-check.skip=true
# 找到并 kill 8082 的 mvnw/java 进程后：
nohup ./mvnw spring-boot:run -pl apps/api -Dspring-boot.run.profiles=dev -Dspring-boot.run.arguments=--server.port=8082 > /tmp/gits-api-8082.log 2>&1 &

# 前端
cd frontend && npm run dev -- --host 0.0.0.0 --port 5173

# 测试
cd frontend && npx vue-tsc --noEmit
cd frontend && npx vitest run
cd frontend && npx playwright test                                    # mock e2e
cd frontend && npx playwright test --config playwright.live.config.ts  # live e2e（需 8082+8106 健康）
```
