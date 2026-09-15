# GITS Bank「信号与互动 → 互动记录·访前路径」UX 改造分析与方案

> 文档版本：V1.0 · 2026-08-29
> 角色：需求分析师 + UX 设计师
> 范围：V3.2 设计文档 §11「互动记录·访前路径」至 §19「CRM受控回写」（P10–P19）
> 硬约束：**「生成客户访前报告」逻辑不变**，仍通过请求 KERT 后台（`POST /journey/{id}/prepare-previsit`，3 个 Skill 并行）获得。

---

## 1. 交付现状诊断

### 1.1 现有「信号与互动」域结构

一级导航「客户经营」→ 二级「信号与互动」指向 `/engagement`（`EngagementWorkspace.vue`，P11）。
`SignalsDomainTabs` 提供三个域页签：经营旅程（`/engagement`）、经营信号（`/signals`）、互动对象（`/engagements`）。

### 1.2 现有「互动记录·访前路径」的实现形态

`EngagementWorkspace.vue`（941 行）把 P11–P19 的**全部业务阶段压进一个页面**：

- 顶部：对象头 + 域页签 + 上下文栏（当前客户 / 旅程 / 迭代轮次 / 启动旅程 / 完成旅程）
- 左侧：互动记录时间线（timelineItems）
- 右侧：**7 个手风琴步骤卡片**（访前缺口 → 证据装配 → 访前包 → 会中 → 访后对账 → 迭代决策 → CRM 回写）
- 底部：DKWS 调用提示条、客户选择弹窗、渠道选择弹窗

另有 8 个独立切片页：P12 `PrevisitGapsView`、P13 `PrevisitEvidenceView`、P14 `PrevisitPackView`、P15 `InMeetingAssistant`、P16 `MeetingCaptureView`、P17 `MeetingCheckoutView`、P18 `PostvisitReconcileView`、P19 `CrmWritebackView`。

### 1.3 后端契约与「生成客户访前报告」链路（必须保持不变）

| 能力 | 端点 | 是否调 KERT Skill | 说明 |
|---|---|---|---|
| 启动旅程 | `POST /journey/start`（经 `startJourney`） | 否 | 返回 journeyId/operatingCaseId/phase |
| KYC 缺口画像 | `GET /kyc/{customerId}/gap-profile` | 否（纯查询） | `fetchKycGapProfile` |
| **一键访前（唯一 KERT 入口）** | `POST /journey/{id}/prepare-previsit` | **是（3 Skill 并行）** | 外联 + 会面 + R1 访前报告（含速战卡、装配轨迹） |
| 供应链图谱 | `POST /supply-chain-graph` | 是（1 Skill） | `executeSupplyChainGraph` |
| 访后分析 | `POST /journey/{id}/postvisit` | 否 | 返回 CRM 写回命令计数 |
| 完成旅程 | `POST /journey/{id}/complete` | 否 | `completeJourney` |

> 关键事实：`prepare-previsit` 一次返回 `outreachScript + meetingScript + previsitReport + battleCard + assemblyTrace + skillSections`，是**原子的一键操作**。P13（证据装配）与 P14（访前包）都只是这份结果的不同视角，**没有独立后端能力**。

---

## 2. 旧实现 vs V3.2 设计的差异分析

### 2.1 信息架构：从「伪分步单页」到「对象主页 + 阶段 Path + 分页记录」

| 维度 | 旧实现 | V3.2 设计 | 问题 |
|---|---|---|---|
| P11 形态 | 7 个步骤卡片 + 时间线塞一页 | 互动记录**对象主页**（`record_detail`），阶段 Path 导航到各记录页 | 伪分步误导 |
| 阶段表达 | 手风琴步骤序号 1–7 | 阶段 Path（访前→会中→访后），由后端状态机驱动 | 序号暗示可逐级触发 |
| 时间线 | 与步骤卡片**重复**表达同一状态 | 活动时间线是记录页的辅助信息，不与阶段重复 | 信息冗余 |

**根因**：旧实现把「阶段 Path」与「任务内容」混成同一种步骤卡片，导致一个页面既要表达"现在在哪个阶段"，又要表达"每阶段做什么"，还要表达"历史轨迹"——三者互相打架。

### 2.2 操作心智模型：从「每步独立触发」到「主动作由门禁决定」

| 维度 | 旧实现 | V3.2 设计 |
|---|---|---|
| 主动作数量 | 每张步骤卡片 1–2 个按钮，共 10+ 个 | 每页**主动作最多 1 个、次动作最多 2 个** |
| 触发语义 | Step1"生成访前准备包"实际触发 3 Skill 并行；Step2/3 暗示独立触发但无独立 API | 「一键访前」唯一入口，P13/P14 只读展示 |
| 阻断解释 | 锁定步骤显示"需先完成访前准备"，无原因/解除路径 | 右侧门禁面板解释阻断原因与解除方式 |

**已确认的具体缺陷**（源码核验）：

1. `PrevisitEvidenceView.vue` 在 `onMounted` 自动调 `preparePrevisit`——每次进入 P13 都触发 3 个 Skill 并行，来回切换会重复烧钱。
2. `PrevisitPackView.vue` 调 `executePrevisit`（`POST /journey/{id}/previsit`），与 `preparePrevisit` **功能重叠但端点不同**，造成 KERT 重复调用。
3. `preR/postR/outR/meetR` 都存组件级 `ref`，页面刷新即丢。
4. 「迭代决策」是旧实现自造的独立步骤，V3.2 中迭代属于持续经营，不在访前路径内。

### 2.3 右侧面板：从「无解释按钮」到「门禁面板」

旧实现所有操作都是「按钮 + toast」，没有 V3.2 要求的「下一步 / 业务规则 / 异常 / 契约使用」四段式门禁面板。违反 V3.2 页页声明的「禁止只给一个无解释按钮」。

### 2.4 状态语义：从「深绿/深红/深琥珀混色」到「一色一义」

旧实现 `step-done` 用绿色、`gap-unknown` 用深红、`gap-stale` 用灰、`dot-meeting` 用浅绿——同一语义多色表达。V3.2 规范：蓝=动作/当前、青绿=确认/完成、琥珀=待处理/冲突/阻断，普通待办统一琥珀，不用红。

---

## 3. 核心 UX 建议（改造原则）

### 原则 1：P11 回归「互动记录对象主页」，不承载 9 个阶段的业务细节
阶段 Path 只做导航与状态透传；业务作业落到 P12–P19 各自的记录页。

### 原则 2：一键访前是唯一 KERT 入口（硬约束），P13/P14 降为只读视角
- 一键访前（「生成访前包」）按钮放在 **P13（访前知识证据装配）**，作为唯一 KERT 触发动作（对齐 V3.2 矩阵 P13 主动作「生成访前包」）。
- P12 只做纯查询（KYC 缺口）；P13 触发 KERT 后展示 `assemblyTrace`；P14 只读展示完整访前包，二者从同一份 `prepare-previsit` 结果读取，**绝不各自调后端**。

### 原则 3：阶段 Path 由后端 `journey.phase` 驱动，前端不可越级
Path 主动作、门禁、阻断原因全部由服务端状态机返回；前端只做渲染与透传。

### 原则 4：右侧「门禁面板」组件化，四段式强制展示
统一 `GuidancePanel`：下一步 / 业务规则 / 异常与降级 / 契约使用。禁止无解释按钮。

### 原则 5：状态管理集中化，解决刷新丢状态与重复调用
新增 Pinia store `usePrevisitStore`，缓存 `previsitResult`、`kycGapProfile`、`journey`，P12/P13/P14 共享同一份数据；刷新后从 store + 深链 PageReference 恢复，不重新触发 KERT。

### 原则 6：一色一义，复用 V3.2 色彩 Token
`--gits-blue-600`=动作/当前、`--gits-teal-500`=确认/完成、`--gits-amber-400`=待处理/冲突/阻断。

---

## 4. 改造后的 UX 界面规格（逐页）

> 通用约定（所有页面）：左侧导航固定选中「信号与互动」；对象头 = 对象类型 + 标题 + 状态 Pill + 主动作；首屏四项关键指标；右侧固定门禁面板；离开/返回恢复筛选、页签、滚动、草稿。

### 4.1 P10 互动对象主页（`object_list`）
**主动作：新建互动 / 同步日历**。按客户分组的互动列表保留（现状已接近），补右侧门禁面板即可。

### 4.2 P11 互动记录·访前路径（`record_detail`）—— 本次改造核心

```
┌──────────────────────────────────────────────────────────────────────────┐
│ 互动 Interaction · 扩产融资专题拜访                    [返回并恢复位置]      │
│ 状态：访前准备 (琥珀 Pill)                                                  │
│ [准备完整度 76%] [客户参会人 3] [待核实问题 6] [关联需求 2]                 │
├──────────────────────────────────────────────────────────────────────────┤
│ 阶段 Path：  ●访前准备 ── ○会中协作 ── ○访后核验与受控回写                  │
│            （当前，蓝）   （未到达）      （未到达）                          │
├───────────────────────────────────────────┬──────────────────────────────┤
│ 关键工作                                   │ 下一步与门禁                  │
│  ☐ 确认拜访目标与成功标准                   │ 主动作：打开访前工作区 →        │
│  ☐ 补齐行业/客户证据                       │ 业务规则：Path主动作由阶段和门禁决定│
│  ☐ 确定专家与会中分工                      │ 异常：依赖失败保持上下文，可重试  │
│                                           │ 契约：REUSE_EXISTING            │
│ 活动时间线（启动→访前准备→…）               │                              │
└───────────────────────────────────────────┴──────────────────────────────┘
```

- 主动作 **「打开访前工作区」** 跳转 P12；次动作 **「标记准备完成」** 受门禁控制（未完成 P12–P14 时禁用并解释阻断原因）。
- 阶段 Path 由 `journey.phase` 映射：`PREVISIT_PREP→访前准备`、`INTERACTION→会中协作`、`POSTVISIT_REVIEW→访后核验`。
- 时间线保留但**去重**，只表达事件流（启动/访前完成/会中/访后），不再与 Path 重复。

### 4.3 P12 访前目标与信息缺口（`three_pane_workspace`）
**主动作：进入证据装配**（仅导航到 P13）。三栏：左=拜访目标与工作假设；中=信息缺口（点击缺口直接创建会谈问题）；右=门禁面板。
- `onMounted` 只调 `fetchKycGapProfile`（纯查询，不触发 KERT）。
- 「进入证据装配」跳转 P13；KERT 在 P13 的「生成访前包」触发。

### 4.4 P13 访前知识证据装配（`evidence_workspace`，只读派生）
**主动作：生成访前包**（= 唯一 KERT 入口，受门禁）。点击后调 `preparePrevisit` + `executeSupplyChainGraph`，结果写入 store；随后展示 `assemblyTrace` 表格：知识元素 / 标题 / 来源 / 置信度 / 用途。
- **移除 `onMounted` 自动调 `preparePrevisit`**；未执行一键访前时显示空态 + 引导「先点击生成访前包」。

### 4.5 P14 访前包预览（`document_preview`，只读派生）
**主动作：完成准备**（受门禁）。分区展示：外联脚本 / 会面脚本 / R1 访前报告 + 速战卡 / 供应链图谱。
- **移除 `executePrevisit` 调用**，直接读 store 的一键访前结果，避免 KERT 重复调用。

### 4.6 P15 会中工作区（`three_pane_workspace`）
**主动作：开始记录 / 打开移动速记**。现状已有门禁 + CRM 命令侧栏，补三栏议程/速记/候选结构，加右侧门禁面板。

### 4.7 P16 会中实时捕获（`live_capture`）
**主动作：新增速记 / 暂停转写**。AI 只输出候选结构，低置信度进人工确认队列；转写失败切手工速记（现状已具备草稿恢复）。

### 4.8 P17 离场确认（`exit_checklist`）
**主动作：生成确认摘要 / 结束会谈**。双方确认清单 + E01_EXIT_CONFIRM 门禁（现状已对齐，补摘要与门禁面板）。

### 4.9 P18 访后事实对账（`fact_reconciliation`）
**主动作：提交核验 / 进入CRM预览**。冲突并列原值/新值/证据/处理建议（现状的"先前主张 vs 新证据"双栏方向正确，补处理建议与升级机制）。

### 4.10 P19 CRM受控回写（`controlled_diff`）
**主动作：批准并执行 / 退回修改**。先差异预览（原值→新值）→ 白名单写回 → 幂等回执。现状 `CrmWritebackView` 已有命令列表 + `CrmWritebackApproval`，补**差异预览表格**与回执展示。

---

## 5. 数据流与契约（KERT 约束不破）

```
P10 互动对象主页
   └─(选客户/启动旅程)─> startJourney ── journeyId/phase/operatingCaseId
                            │
P11 互动记录·访前路径（对象主页，读 journey.phase 渲染 Path）
   └─(打开访前工作区)─> P12
                            │
P12 访前目标与信息缺口：fetchKycGapProfile(纯查询) + 「进入证据装配」→ 导航 P13
                            │
P13 证据装配：读 store.assemblyTrace（未生成时显示空态）
   └─(生成访前包)─> preparePrevisit  ← ★唯一 KERT 入口（3 Skill 并行）
                    + executeSupplyChainGraph（1 Skill，可并行）
                    → 结果写入 usePrevisitStore
P14 访前包预览 ──读 store.previsitResult── 只读
   └─(完成准备)─> journey 阶段 → 会中
P15/P16/P17 会中（HumanGate 门禁，非正式 Claim/承诺）
   └─(结束会谈)─> 访后
P18 访后事实对账：executePostvisit
   └─(进入CRM预览)─> P19 CRM受控回写：fetchCrmWritebackCommands + decide
```

**不变项**：`prepare-previsit` 端点、3 个 `skill-customer-*` Skill 编排、`PreparedPrevisitResponse` 字段结构、供应链图谱单独 Skill——全部保持原样，仅前端消费方式从"多入口重复调用"改为"单入口 + 共享 store"。

---

## 6. 前端改造实施路线

### 6.1 新增/改造文件清单

| 文件 | 动作 | 内容 |
|---|---|---|
| `stores/previsit.ts` | 新增 | `usePrevisitStore`：journey / kycGapProfile / previsitResult / supplyChainReport 的缓存与恢复 |
| `components/shell/GuidancePanel.vue` | 新增 | 右侧四段式门禁面板（下一步/规则/异常/契约） |
| `components/shell/StagePath.vue` | 新增 | 阶段 Path（由 journey.phase 驱动） |
| `components/shell/HighlightsMetrics.vue` | 新增 | 首屏四项关键指标 |
| `views/EngagementWorkspace.vue` | **重构** | 由 7 步卡片改为 record_detail：对象头 + 指标 + 阶段 Path + 关键工作 + 时间线 + 门禁面板 |
| `views/PrevisitGapsView.vue` | 改造 | 一键访前按钮 + fetchKycGapProfile；不自动调 KERT |
| `views/PrevisitEvidenceView.vue` | 修复 | 移除 onMounted 自动调 preparePrevisit，改为读 store |
| `views/PrevisitPackView.vue` | 修复 | 移除 executePrevisit，改为读 store |
| `views/PostvisitReconcileView.vue` | 增强 | 补处理建议 + 升级机制 |
| `views/CrmWritebackView.vue` | 增强 | 补差异预览表格 + 回执展示 |

### 6.2 实施顺序（建议）

1. 新建 `usePrevisitStore` + 三个 shell 组件（无业务耦合，可先行）
2. 重构 `EngagementWorkspace.vue` 为对象主页
3. 修复 P12/P13/P14 的 KERT 调用（消除重复调用，接 store）
4. 增强 P18/P19 的门禁与差异预览
5. 全链路回归：一键访前结果在 P12→P13→P14 间不丢、不重复调用

---

## 7. 逐页验收标准对照（节选，与 V3.2 AC 对齐）

- **AC-11**：进入 P11 首屏可见对象/状态/主动作/下一步；阶段 Path 由后端驱动；无权/缺证/冲突/超时不静默失败。
- **AC-12**：P12 进入只触发纯查询；一键访前是唯一 KERT 入口。
- **AC-13**：P13 只读展示装配轨迹，不再自动触发 KERT；未执行访前时显示空态引导。
- **AC-14**：P14 只读展示完整访前包，不调 executePrevisit；完成准备后 Path 进入会中。
- **AC-19**：CRM 写回先差异预览，再确认执行，展示幂等回执、失败字段与重试/撤销。

---

*本方案为设计候选（DESIGN_CANDIDATE），落地前需客户经理走查 + Owner 评审；后端契约零变更。*
