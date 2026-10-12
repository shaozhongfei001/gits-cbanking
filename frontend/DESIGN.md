# DESIGN.md — GITS Bank 对公客户经营工作台

> **本文件是什么**：给 AI Agent 与前端开发者读取的**视觉与交互约束**文档。
> `AGENTS.md` 管"项目怎么构建"，本文件管"界面该长什么样、什么不许出现"。

---

## 0. 权威声明（先读，违反即无效）

| 项 | 值 |
|---|---|
| 文件定位 | **DERIVED 派生视图**，不是权威源 |
| 权威顺序 | Owner 决定 > `specs/BASELINE_INDEX.yaml` > ADR > `specs/CONTRACT_INDEX.yaml` > 当前 Loop > **本文件** > 实现 |
| 与 `specs/` 冲突时 | **以 `specs/` 为准**，本文件让步 |
| 事实来源 | 令牌取自 `frontend/src/assets/styles/theme.css`；骨架取自 `frontend/src/components/shell/` 与 `frontend/src/layouts/` |
| 变更方式 | 改本文件不构成合同变更；但**改 token 必须改 `theme.css` 并同步本文件** |

**本文件不授权任何业务行为**。它不定义字段、不给接口、不批准功能开关。界面上的"禁用/降级"表达必须回源到对应 Loop 与合同，不得由本文件发明。

---

## 1. Visual Theme & Atmosphere

**气质**：银行对公业务的**高信息密度专业台**。冷静、克制、可核对，不是消费级产品的"轻盈愉悦"。

| 维度 | 取值 |
|---|---|
| 密度 | **高**。客户经理在单屏内完成"看画像 → 对账 → 决策"，不追求大留白 |
| 语气 | **克制**。颜色只用于承载语义（风险、状态、来源），不做装饰 |
| 明暗 | 亮色为默认；暗色为等价一等公民（`data-theme="dark"`） |
| 权威感 | 来自**信息可核对性**（来源、版本、状态齐备），不来自视觉炫技 |
| 反模式 | 玻璃拟态、渐变 hero、霓虹发光、大圆角卡通化、装饰性插画 |

**核心判断标准**：客户经理能否在 3 秒内回答"这个数字从哪来、现在什么状态、我下一步该干什么"。视觉设计服务于这个判断，其它一律让路。

---

## 2. Color Palette & Roles

### 2.1 三层令牌结构（必须遵守）

```
原始色（palette）  →  品牌/语义 token  →  组件消费
--gits-blue-600        --brand-primary       var(--brand-primary)
```

**规则：组件样式只允许消费第 2 层。** 直接写 `var(--gits-blue-600)` 仅在该颜色没有语义别名时允许。

### 2.2 原始色板（palette）

| Token | 值 | 说明 |
|---|---|---|
| `--gits-navy-900` | `#08233b` | 侧边栏深底、全局最暗面 |
| `--gits-navy-800` | `#0b2e4f` | 次级深底、深色标题 |
| `--gits-blue-600` | `#1976d2` | 品牌主色 |
| `--gits-blue-400` | `#48a7e8` | 品牌主色 hover |
| `--gits-teal-500` | `#12a7a0` | 强调/成功描边 |
| `--gits-teal-700` | `#087771` | 成功文字 |
| `--gits-amber-400` | `#f2b84b` | 警示描边、导航角标 |
| `--gits-amber-800` | `#7a4b00` | 警示文字 |
| `--gits-page` | `#f3f6f9` | 页面底色 |
| `--gits-line` | `#d8e2ec` | 分隔线/边框 |
| `--gits-text` | `#1b2632` | 主文字 |
| `--gits-muted` | `#596779` | 次文字 |

> **已废弃**：旧 SPDB 蓝 `#003366`。`theme.css:8` 明文"禁止用旧 SPDB 蓝充当品牌"。存量清理由 §10.3 负责。

### 2.3 语义色角色

使用语义 token，**禁止**按"看起来像蓝色"选色。

| 角色 | Token | 用于 |
|---|---|---|
| 品牌主色 | `--brand-primary` | 主按钮、链接、当前态、焦点环 |
| 品牌浅底 | `--brand-primary-lighter` | 选中行背景、信息型卡片底 |
| 强调色 | `--brand-accent` | 完成态、正向指标点缀 |
| 成功 | `--color-success` / `-bg` / `-border` | 达成、通过、已确认 |
| 警示 | `--color-warning` / `-bg` / `-border` | 待办、需确认、边界临近 |
| 危险 | `--color-danger` / `-bg` / `-border` | 拒绝、失败、越权、冲突 |
| 信息 | `--color-info` / `-bg` / `-border` | 中性提示、来源说明 |

### 2.4 金融领域风险色（独立于状态色）

| Token | 值 | 用于 |
|---|---|---|
| `--risk-high` | `#dc2626` | 高风险等级 |
| `--risk-medium` | `#f59e0b` | 中风险等级 |
| `--risk-low` | `#10b981` | 低风险等级 |

**风险色与状态色语义不同，不得互相替换**。风险等级表达的是业务对象属性，状态色表达的是流程状态。同时出现时，风险用 `--risk-*`（点/标签），状态用 `--color-*`（徽标/底色）。

### 2.5 表面（surface）层级

| Token | 亮色 | 暗色 | 用于 |
|---|---|---|---|
| `--bg-page` | `#f3f6f9` | `#0c1220` | 页面最底 |
| `--bg-surface` | `#ffffff` | `#151e2d` | 卡片、面板 |
| `--bg-surface-soft` | `#f8fafc` | `#1a2536` | 卡片内分区 |
| `--bg-hover` | `#eff3fb` | `#243248` | 悬停底 |
| `--bg-active` | `#e0e8f5` | `#2a3a52` | 选中/按下底 |
| `--bg-sidebar` | `#08233b` | `#111a28` | 主导航 |

### 2.6 无障碍下限

- 正文与背景对比度 **≥ 4.5:1**；大字号/图标 **≥ 3:1**。
- **禁止仅用颜色传达状态**：必须同时有文字、图标或形状（风险等级必须带文字标签，不能只给一个红点）。
- 焦点可见：所有可聚焦元素必须有可见焦点环，不得 `outline: none` 而无替代。

---

## 3. Typography Rules

### 3.1 字体栈（P0 已修复）

**修复前**（`theme.css` 旧值）有两个缺陷：

1. `index.html` **未加载任何 Web Font**，而栈首写着 `Inter` / `JetBrains Mono` → 字体名永远命中不到，声明是空话。
2. 界面语言为 `zh-CN`（`index.html:2`），但栈里**没有任何中文字体** → 中文走系统默认，字重与西文不匹配，是"界面显廉价"的直接原因之一。

**现行规范值**（`theme.css` `:root`，P0 起生效）：

```css
--font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC',
  'Hiragino Sans GB', 'Microsoft YaHei', 'Noto Sans SC', Roboto,
  'Helvetica Neue', Arial, sans-serif;
--font-mono: ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas,
  'Liberation Mono', 'PingFang SC', 'Microsoft YaHei', monospace;
```

**取舍记录**：**不引入** `Inter` / 任何外部字体资源。理由是内网/离线部署环境下 Web Font 是额外风险面，且 Inter 无 CJK 字形、解决不了主要问题（中文排版）。若将来确要自托管，须先验证 Docker/nginx 离线可用性，再放回栈首并同步 `src/theme/naiveTheme.ts`。

**漂移守卫**：`--font-sans` 会与 `naiveTheme.ts` 的 `GITS_FONT_SANS` 做逐字比对（`src/theme/__tests__/naiveTheme.spec.ts`），并有 E2E 断言栈内必须含中文字体、且不得残留 `Inter`（`e2e/experience-shell.spec.ts`）。

### 3.2 字阶（唯一允许的取值）

| Token | 值 | 行高 | 用途 |
|---|---|---|---|
| `--text-xs` | `0.75rem` (12px) | 1.5 | 标签、徽标、辅助说明 |
| `--text-sm` | `0.8125rem` (13px) | 1.5 | **正文默认**、表格单元格 |
| `--text-base` | `0.875rem` (14px) | 1.5 | 段落正文 |
| `--text-lg` | `1rem` (16px) | 1.5 | 卡片标题 |
| `--text-xl` | `1.125rem` (18px) | 1.25 | 区块标题 |
| `--text-2xl` | `1.25rem` (20px) | 1.25 | 页面标题 |
| `--text-3xl` | `1.5rem` (24px) | 1.25 | 关键指标数值 |

**硬性红线**：

- **禁止出现 `< 11px` 的字号**。当前 `8px / 9px / 10px` 共 **8 处 / 3 文件**，属缺陷，按 §10.2 清理：

  | 文件 | 行 | 值 |
  |---|---|---|
  | `components/shell/AppSidebar.vue` | 177, 185 | `9px` |
  | `components/shell/AppSidebar.vue` | 248, 279 | `10px` |
  | `components/shell/AppSidebar.vue` | 284 | `8px` |
  | `components/KnowledgePrevisitReport.vue` | 369, 380 | `10px` |
  | `layouts/ExperienceShell.vue` | 191 | `9px` |

- **禁止出现 §3.2 表外字号**。需要新字号 → 先加 token，再使用。
- 数值类文本（金额、比率、计数）使用 `--font-mono` 并右对齐或等宽对齐。

### 3.3 字重

仅允许 `400`（正文）/ `500`（强调）/ `600`（标题）/ `700`（数值与徽标）。**禁止 `800` / `900`**。

---

## 4. Component Stylings

### 4.1 页面骨架（强制）

所有业务页必须按此三段结构组织，**不得自创骨架**：

```vue
<ObjectHeader :page-id="PAGE_ID" :object-type="OBJECT_TYPE"
              object-status="..." title="..." />
<!-- 可选：<HighlightsMetrics :items="..." /> -->
<PageState :status="status" :error="error" @retry="reload">
  <!-- 页面主体 -->
</PageState>
```

- **`ObjectHeader`** 承担「对象类型 / 标题 / 当前状态 / 返回并恢复位置」。**页面不得再自建 `<h1>` 级页头**（避免全局壳层 + 页级标题两级重复）。
- **`PageState`** 是**四态渲染的唯一实现**（见 §4.2）。
- 右侧辅助信息用 **`GuidancePanel`**（粘性定位，`top: 16px`），不得自建侧栏。
- 阶段型流程用 **`StagePath`**，不得自绘进度条。

存量覆盖：`ObjectHeader` 32 个文件、`PageState` 35 个文件。新页面必须加入，未加入的存量页按 §10.2 补齐。

### 4.2 四态（强制，缺一即缺陷）

权威类型：`useResourceStatus.ts:1`

```ts
export type ResourceStatus = 'idle' | 'loading' | 'success' | 'error'
```

| 状态 | 呈现要求 |
|---|---|
| `idle` | 明确空态文案，说明"尚未请求"，不得显示空白 |
| `loading` | 骨架屏或 spinner，**禁止空白页** |
| `success` | 渲染内容 |
| `error` | 错误信息 + **重试按钮**（`data-testid="retry-action"`） |

**降级态**：请求失败但持有快照时，必须**显式声明"展示最近成功快照"**，并禁用确认型操作。禁止静默降级。

### 4.3 按钮

| 层级 | 用法 | 取值 |
|---|---|---|
| 主按钮 | 页面唯一主行动 | `type="primary"`，背景 `--brand-primary` |
| 次按钮 | 辅助行动 | 默认样式，边框 `--border-normal` |
| 幽灵按钮 | 表格行内、工具栏 | `quaternary` |
| 危险按钮 | 删除、拒绝、回滚 | `type="error"` |

- 圆角统一 `--radius-sm`（6px）。naive-ui 全局 `borderRadius` 必须与 token 一致（当前 `App.vue:18` 硬编码 `4px`，属漂移）。
- **按钮文案必须是业务动词**（"提交评审"、"生成访前报告"），禁止工程术语（见 §7.2）。

### 4.4 状态徽标 / 风险点

```html
<span class="badge badge--success">已确认</span>
<span class="badge badge--warning">待复核</span>
<span class="badge badge--danger">已拒绝</span>
<span class="badge badge--info">草稿</span>
```

- 徽标必须是**「底色 + 文字 + 边框」三件套**（已由 `theme.css` 的 `.badge--*` 提供），不得自建纯色块。
- 风险点用 `.risk-dot--high|medium|low`，且**必须伴随文字等级**。

### 4.5 卡片

- 基础卡片：`.surface-card`（`--bg-surface` + `--border-light` + `--radius-md` + `--shadow-xs`）
- 抬升卡片：`.surface-card-elevated`（`--shadow-md`），**仅用于弹层/抽屉，不得用于普通列表项**
- 禁止在卡片内再嵌卡片超过一层。

### 4.6 指标卡（`HighlightsMetrics`）

- 桌面 4 列，`≤900px` 降为 2 列。
- 数值用 `--text-3xl` + `700` + `--font-mono`；标签用 `--text-xs`。
- 左侧 3px 语义色条：`blue`（中性）/ `teal`（正向）/ `amber`（需关注）。
- **禁止在指标卡内放图表**。

### 4.7 阶段路径（`StagePath`）

- 已完成：teal 圆环 + 勾；当前：蓝圆环 + 序号 + 加粗标签；未来：灰圆环 + 序号。
- 连接线已完成段 teal，未完成段 `--gits-line`。
- 单一流程实例只允许一条 `StagePath`。

### 4.8 表单与表格

- 表单标签在**上方**（不做左侧对齐），必填项显式标注。
- 校验错误信息紧随字段下方，用 `--color-danger`。
- 表格：表头 `--bg-surface-soft`，行分隔用 `--border-light`，悬停 `--bg-hover`；**禁止斑马纹**。
- 长表格必须提供列固定或横向滚动（`.custom-scrollbar`）。

### 4.9 图标

- **唯一图标来源：`naive-ui` 内置图标或 `@vicons/*` 矢量图标**。
- **禁止用文本字形充当图标**（如 `▦ ✓ ◎ ◉ ↗ ◇ ▤ ★ ♙ ▱ ⌁ ◌`）。当前 `navConfig.ts` 的 `icon` 字段即为文本字形，属存量缺陷，按 §10.2 清理。
- 图标尺寸：导航 16px / 按钮内 16px / 状态点 8px。图标与文字间距 `--space-2`。

---

## 5. Layout Principles

### 5.1 间距（唯一尺度）

`--space-1..12` = `4 / 8 / 12 / 16 / 20 / 24 / 32 / 40 / 48` px。

- **禁止出现表外间距**（如 `7px`、`15px`、`18px`）。
- 组件内间距用 `--space-2/3/4`；区块间用 `--space-6/8`；页面留白用 `--space-6`。

### 5.2 全局壳层（`ExperienceShell`，唯一）

```
┌───────────┬────────────────────────────────────────┐
│ AppSidebar│ Header（搜索 / 全局新建 / 主题 / 用户）  │
│  226px    ├────────────────────────────────────────┤
│  navy     │ WorkspaceTabs（多页签，42px）            │
│  #08233b  ├────────────────────────────────────────┤
│           │ 内容区 padding: 20px 24px 32px          │
│  ⊞ 分组导航│  └─ 页面骨架（ObjectHeader + PageState）│
└───────────┴────────────────────────────────────────┘
```

- 壳层在 `App.vue:42` **只挂载一次**。页面**不得**再渲染导航、搜索或用户区。
- 一级导航只切换**稳定对象域**；业务阶段（访前/会中/写回/移动端）不得进入一级导航（`navConfig.ts:15-19` 已确立此原则，保持）。
- 折叠宽度 `64px`，侧栏固定 `226px`。

### 5.3 内容宽度

- 页容器 `max-width: 1400px`，居中，`padding: var(--space-6)`。
- 阅读型长文（报告、条款）单独 `max-width: 800px`。
- 数据密集型（表格、看板）允许满宽。

### 5.4 栅格

使用 CSS Grid 而非 `float`/绝对定位。指标卡 `repeat(4, minmax(0,1fr))`；两栏（主体 + `GuidancePanel`）比例 `1fr 320px`。

---

## 6. Depth & Elevation

| 层级 | Token | 用于 |
|---|---|---|
| 0 | 无阴影 | 平铺内容、表格行 |
| 1 | `--shadow-xs` | 基础卡片 |
| 2 | `--shadow-sm` | 卡片悬停 |
| 3 | `--shadow-md` | 抽屉、下拉、粘性面板 |
| 4 | `--shadow-lg` | 弹窗 |
| 5 | `--shadow-xl` | 全屏遮罩层内容 |

- z-index 必须取 `--z-dropdown(100) / --z-sticky(200) / --z-overlay(300) / --z-modal(400) / --z-toast(500)`，**禁止 `z-index: 9999`**。
- 同一视觉层级不得用两种阴影。

---

## 7. Do's and Don'ts

### 7.1 Do（必须）

1. **只用 token**：颜色、间距、圆角、阴影、字号一律 `var(--*)`。
2. **四态齐全**：任何数据加载都走 `PageState`。
3. **语义优先**：先问"这是什么语义"，再选 token。
4. **状态可核对**：界面必须能回答"数字来源 / 当前状态 / 下一步"。
5. **暗色等价**：新增样式必须在 `[data-theme="dark"]` 下同样可读。
6. **可聚焦**：交互元素用原生 `<button>` / `<a>` 或带 `tabindex` 的正确角色。

### 7.2 Don't（硬红线）

| # | 禁止项 | 原因 |
|---|---|---|
| D1 | 硬编码十六进制颜色 | 令牌漂移；存量 48/101 文件违规 |
| D2 | 使用 `#003366`（旧 SPDB 蓝） | `theme.css:8` 明文禁止；存量 41 处 / 19 文件 |
| D3 | 字号 `< 11px` | 不可读、不合规；存量 8 处 / 3 文件 |
| D4 | 引入 `tdesign-vue-next` 或第二个 UI 库 | 单一 UI 库原则；tdesign 在 `src` 中 **0 引用** 属死依赖 |
| D5 | 用文本字形当图标 | 跨平台渲染不一致 |
| D6 | 页面自建导航/页头/侧栏 | 与全局壳层重复，装出"两层标题" |
| D7 | 只处理 `success` 状态 | 四态缺失即缺陷 |
| D8 | 静默降级（失败还装作成功） | 违反 C08 红线 |
| D9 | `any` / `@ts-ignore` | 类型纪律 |
| D10 | 内联 `style="..."` | 无法被令牌统一约束 |
| D11 | `!important` 覆盖组件库（除 `styles/shell.css` 的集中治理点） | 不可维护 |
| D12 | **把工程术语当用户文案** | 见 §7.3 |

### 7.3 工程术语不得进入用户界面（重点）

**禁止出现在任何用户可见位置的词**：`未授权`、`解除路径`、`只读切片`、`C2/C3 降级`、`P30`、`Loop`、`合同`、`contract`、`testid`、`pageId`、`Port`、`Gate`。

存量违规示例（须按 §10.2 修正）：

```23:23:frontend/src/components/shell/DisabledAction.vue
      原因：{{ reason }}。解除路径：{{ unlockPath }}
```

```71:71:frontend/src/layouts/ExperienceShell.vue
        <button type="button" class="global-new" data-testid="global-new" disabled title="全局新建写未授权；解除路径：CC2 后独立合同 Loop">
```

**存量覆盖面（实测）**：

| 来源 | 覆盖 |
|---|---|
| `DisabledAction.vue:23`（唯一通用渲染点） | 被 **23 个页面**调用、模板中 **30 处** `<DisabledAction>` → 30 处用户可见"解除路径" |
| `ExperienceShell.vue:71`（内联） | 1 处 |
| 其它 `.vue` 模板硬编码（`未授权` / `只读切片` / `C2 降级`） | 7 处 |
| **合计** | **≈38 处** |

> 这意味着：**修好 `DisabledAction.vue` 一处，即消除 30 处违规**。这是本文件里性价比最高的一次修复。

**正确表达方式**：

| 场景 | 用户看到的文案 | 工程信息去哪 |
|---|---|---|
| 功能未开放 | "该功能尚未开放" | `title` 仅开发态显示，或写入 `data-*` 供测试断言 |
| 依赖前置 | "请先启动经营旅程" | 同上 |
| 无权限 | "当前角色无此权限，请联系管理员" | 同上 |

**判定标准**：把界面截图给一位客户经理看，他不应该看到任何他需要查开发文档才能理解的词。

> 实现建议：保留 `reason` / `unlockPath` prop 供测试与审计使用，但渲染受 `import.meta.env.DEV` 或专门的"审计面板"控制，不进主界面。

---

## 8. Responsive Behavior

### 8.1 断点（收敛为 4 个）

| 名称 | 断点 | 行为 |
|---|---|---|
| Mobile | `< 600px` | 侧栏折叠为抽屉；单列；表格横向滚动 |
| Tablet | `< 900px` | 指标卡 4→2 列；两栏→单列；`GuidancePanel` 移到主体下方 |
| Desktop | `≥ 900px` | 完整布局 |
| Wide | `≥ 1400px` | 页容器封顶 1400px，不再拉伸 |

**禁止新增断点**。存量散落的 `430/514/560/1000/1100/1200/1700px` 属过渡态，新代码统一到上表。

### 8.2 触控与可读性

- 触控目标（移动端）最小 **44×44px**。
- 正文最小 **13px**，标签最小 **12px**。
- 表格在 `< 900px` 必须可横向滚动，**禁止压缩列宽到文字换行三行以上**。

### 8.3 暗色（P0 已修复）

- 切换机制：`data-theme="dark"` 挂在 `<html>` 上，持久化 key = `gits-theme`（`src/App.vue`）。
- **所有自定义组件必须走 CSS 变量**，这样暗色自动生效。
- **naive-ui 组件**：由 `src/theme/naiveTheme.ts` 提供 `GITS_THEME_LIGHT` / `GITS_THEME_DARK` 两套 `themeOverrides`，`App.vue` 按 `isDark` 分发。
  - **禁止**在组件或 `App.vue` 里再写 `primaryColor: '#xxxxxx'` 这类硬编码。
  - **禁止**把 `var(--x)` 直接交给 naive-ui 的色值字段：naive-ui 会对颜色做运算，传入变量会得到非法色值；必须传解析后的字面量，并由漂移守卫测试保证与 CSS 同源。
  - 已知行为（非缺陷）：naive-ui 的 CSS 变量在配置更新后**异步**落到样式上，切换瞬间有极短延迟。断言时请用轮询（`expect.poll`），不要一次性读取。
- `--font-sans` 与主题同样受守卫：见 §3.1。

---

## 9. Agent Prompt Guide

### 9.1 新建页面的标准提示词

```text
按 frontend/DESIGN.md 新建页面 <页面名>（<业务对象>）。

要求：
- 骨架：ObjectHeader(pageId, objectType, objectStatus, title) + PageState(四态)
- 数据：只用 frontend/src/api/ 下既有方法，不得发明字段
- 样式：只用 var(--*) token，禁止任何十六进制颜色与内联 style
- 图标：naive-ui / @vicons 矢量图标，禁止文本字形
- 文案：业务语言；禁止"未授权/解除路径/P30/Loop"等工程术语
- 响应式：<900px 单列，指标卡 4→2 列
- 完成后：npm run check && npm run test 必须通过
```

### 9.2 代码模板

```vue
<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { NButton } from 'naive-ui'
import ObjectHeader from '../components/shell/ObjectHeader.vue'
import PageState from '../components/shell/PageState.vue'
import type { ResourceStatus } from '../composables/useResourceStatus'

const PAGE_ID = 'PXX'
const OBJECT_TYPE = '<业务对象>'

const data = ref<Item[]>([])
const loading = ref(true)
const error = ref('')
const requested = ref(false)

const status = computed<ResourceStatus>(() => {
  if (loading.value) return 'loading'
  if (error.value) return 'error'
  return requested.value ? 'success' : 'idle'
})

async function load() {
  loading.value = true
  error.value = ''
  requested.value = true
  try {
    data.value = await fetchItems()
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '加载失败'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="page" data-testid="pxx-page">
    <ObjectHeader :page-id="PAGE_ID" :object-type="OBJECT_TYPE"
                  object-status="…" title="…" />
    <PageState :status="status" :error="error" @retry="load">
      <!-- 主体：只用 token -->
    </PageState>
  </div>
</template>

<style scoped>
.page { display: flex; flex-direction: column; gap: var(--space-4); }
</style>
```

### 9.3 提交前自检

```bash
cd frontend
npm run check        # vue-tsc 类型检查
npm run test         # vitest
npm run build        # 构建
```

并**人工确认**：

- [ ] 无新增十六进制颜色（`grep -rE "#[0-9a-fA-F]{6}" --include=*.vue src`）
- [ ] 无 `< 11px` 字号
- [ ] 无用户可见工程术语
- [ ] 四态齐全且 error 有重试
- [ ] 暗色下可读

---

## 10. 债务与迁移映射

### 10.1 现状基线（2026-09-21 实测，用于验收对比）

| 指标 | 当前值 | 目标 |
|---|---|---|
| `.vue` 文件数 | 101 | — |
| 含硬编码颜色的 `.vue` | **48** | 0 |
| `#003366` 出现次数 / 文件 | **41 / 19** | 0 |
| `< 11px` 字号处数 / 文件 | **8 / 3** | 0 |
| 用户可见工程术语处数 | **≈38**（`DisabledAction` 覆盖 23 页 / 30 处 + 内联 1 + 模板 7） | 0 |
| UI 库数量 | 3（naive-ui 实用 / tdesign 死依赖 / @vicons 死依赖） | 1 |
| 页面骨架覆盖 | ObjectHeader 32、PageState 35 | 全部业务页 |
| `--font-sans` 中文字体 | ✅ 已含（P0） | 保持 |
| naive-ui 品牌色硬编码于 TS | ✅ 已消除，改为双套 overrides（P0） | 保持 |
| `borderRadius` 与 `--radius-sm` 一致 | ✅ 6px（P0 前为 4px） | 保持 |

### 10.2 清理顺序

| 阶段 | 内容 | 状态 |
|---|---|---|
| **P0** | 令牌收口：`--font-sans` 中文字体栈；`gitsTheme` → `src/theme/naiveTheme.ts` 双套 overrides；`borderRadius` 4px→`--radius-sm`(6px)；`data-theme` 首帧生效 | ✅ **已完成** |
| **P1** | 旧色清零：按 §10.3 逐处替换 `#003366`（41 处 / 19 文件） | 待做 |
| **P2** | 可读性：`AppSidebar.vue`(5 处)、`KnowledgePrevisitReport.vue`(2 处)、`ExperienceShell.vue`(1 处) 的 `8/9/10px` 提到 `--text-xs`(12px) | 待做 |
| **P3** | 术语外移：`DisabledAction.vue:23` 的 `reason/unlockPath` 改开发态渲染 —— **一处修复覆盖 23 页 / 30 处**，性价比最高 | 待做 |
| **P4** | 依赖瘦身：移除 `tdesign-vue-next`、`@vicons/ionicons5`（已确认 `src` 中零引用）及 `style.css:65-72` 的 TDesign 覆盖 | 待做 |
| **P5** | 图标矢量：`navConfig.ts` 文本字形换 `@vicons` | 待做 |

### 10.2.1 P0 交付物与守卫（验收依据）

| 交付物 | 作用 |
|---|---|
| `src/assets/styles/theme.css` | `--font-sans` / `--font-mono` 改为系统 UI 字体 + 显式中文字体；无外部字体资源 |
| `src/theme/naiveTheme.ts` | `GITS_THEME_LIGHT` / `GITS_THEME_DARK` + `gitsThemeFor()`；另导出 `NAIVE_TOKEN_MAP` 记录「naive 变量 ↔ CSS token」对应关系 |
| `src/App.vue` | 按 `isDark` 分发 overrides；`data-theme` 在 setup 阶段（首帧前）写入，消除亮→暗闪烁 |
| `src/theme/__tests__/naiveTheme.spec.ts` | **令牌漂移守卫**：解析 `theme.css`（含 `var()` 链）逐项比对 TS 取值；并断言 `naiveTheme.ts` 不含 CSS 未定义的色值 |
| `e2e/experience-shell.spec.ts` | 3 个新增浏览器用例：暗色切换 naive 品牌色、刷新后保持、字体栈含中文字体且无 `Inter` |

**变异复验（证明守卫非空转）**：

| 变异 | 期望 | 实测 |
|---|---|---|
| `naiveTheme.ts` 的 `errorColor` → `#ff0000` | FAIL | ✅ 2 个断言同时红（值比对 + 色值存在性） |
| `theme.css` 的 `--color-danger` → `#dd2626` | FAIL | ✅ 1 个断言红（证明 CSS 侧漂移同样被捕获） |
| `--font-sans` 移除 `'PingFang SC'` | FAIL | ✅ 2 个断言红 |
| `App.vue` 改为 `gitsThemeFor(false)` | FAIL | ✅ 2 个 E2E 红（精确复现修复前行为） |

> 复验后所有变异均已还原；改动范围经 `git diff` 核验，`theme.css` 仅字体栈一处变化。

### 10.3 旧色映射表（逐处判定，禁止全局 sed）

> **警告**：`#003366` 在不同位置的**语义不同**（文字 / 底 / 边框 / 强调）。必须按语义选 token，机器替换会造成语义错误。

| 出现位置 | 当前值 | 替换为 |
|---|---|---|
| 标题 / 正文文字 | `#003366` | `var(--text-primary)` 或 `var(--gits-navy-800)` |
| 品牌强调 / 链接 | `#003366` | `var(--brand-primary)` |
| 深色底 / 侧重底 | `#003366` | `var(--bg-sidebar)` 或 `var(--gits-navy-900)` |
| 边框 / 分隔 | `#003366` | `var(--border-normal)` |

**分布清单（19 文件，41 处）**：

| 文件 | 处数 |
|---|---|
| `components/OpportunityCard.vue` | 6 |
| `components/OpportunityPipeline.vue` | 4 |
| `components/CommitmentCard.vue` | 4 |
| `views/ReportDetail.vue` | 3 |
| `components/TaskCard.vue` | 3 |
| `components/SignalCard.vue` | 3 |
| `components/TaskForm.vue` | 2 |
| `components/recommendation/RecommendationEvidenceDrawer.vue` | 2 |
| `components/ProductKnowledgeCard.vue` | 2 |
| `components/ExternalEventCard.vue` | 2 |
| `components/CommitmentForm.vue` | 2 |
| `components/TaskList.vue` | 1 |
| `components/RecordingConsentPanel.vue` | 1 |
| `components/recommendation/ReviewRequiredPanel.vue` | 1 |
| `components/ProductKnowledgeList.vue` | 1 |
| `components/OpportunityList.vue` | 1 |
| `components/ExternalEventList.vue` | 1 |
| `components/CustomerCard.vue` | 1 |
| `components/CommitmentList.vue` | 1 |

### 10.4 其它高频硬编码色映射

| 值 | 出现 | 映射 |
|---|---|---|
| `#1976d2` / `#1976D2` | 37 / 10 | `var(--brand-primary)` |
| `#596779` | 19 | `var(--text-secondary)` |
| `#8c8c8c` | 17 | `var(--text-tertiary)` |
| `#d8e2ec` | 16 | `var(--border-normal)` |
| `#e6f7ff` | 13 | `var(--brand-primary-lighter)` |
| `#d9d9d9` | 13 | `var(--border-strong)` |
| `#389e0d` | 12 | `var(--color-success)` |
| `#087771` | 12 | `var(--gits-teal-700)` |
| `#b91c1c` / `#cf1322` | 11 / 10 | `var(--color-danger)` |
| `#b8860b` | 11 | `var(--color-warning)` |
| `#1b2632` | 11 | `var(--text-primary)` |
| `#0b2e4f` | 11 | `var(--gits-navy-800)` |
| `#fff7e6` | 10 | `var(--color-warning-bg)` |
| `#e8e8e8` | 10 | `var(--border-strong)` |
| `#12a7a0` | 9 | `var(--gits-teal-500)` |
| `#f6ffed` | 8 | `var(--color-success-bg)` |
| `#f5f5f5` | 8 | `var(--bg-surface-soft)` |

---

## 11. 变更流程

1. **改 token** → 改 `frontend/src/assets/styles/theme.css`，同步本文件 §2/§3/§5/§6。
2. **改页面骨架** → 改 `components/shell/*` 与本节 §4.1，同步更新相关 spec。
3. **新增视觉模式** → 先在本文件"立法"，再写实现。**禁止先在页面里写死再由文档追认**。
4. **权威冲突** → 若本文件与 `specs/` 或 ADR 冲突，以 `specs/`/ADR 为准，并立即修正本文件。

> 本文件不改变 `AGENTS.md` 与 `.codebuddy/rules/` 的权威顺序，只是把既有 token 与骨架**显式化、可校验化**，使 AI Agent 不必每次重新发明界面。
