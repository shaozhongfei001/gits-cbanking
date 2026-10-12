# V8 UX 设计规格 — 第6部分：移动端、通用组件、交互状态、响应式、无障碍

---

## 26. 移动端页面

### 26.1 移动端 Shell

```
┌──────────────────┐
│ ☰  面包屑   👤   │  ← 顶栏 h=48px
├──────────────────┤
│                  │
│  内容区          │
│  padding: 16px   │
│                  │
│  (无侧边栏)      │
│                  │
│                  │
│                  │
│                  │
│                  │
└──────────────────┘

抽屉打开时:
┌──────────────────┐
│██████████████████│  ← 遮罩 rgba(0,0,0,0.4)
│██┌─────────────┐█│
│██│ 品牌区      │█│  ← 侧边栏从左滑出
│██│ GITS Bank   │█│     width=272px
│██│ 对公经营书桌 │█│     z-index=50
│██├─────────────┤█│
│██│ 导航组      │█│
│██│ · 经营总览  │█│
│██│ · 经营信号  │█│
│██│ · 经营旅程  │█│
│██│             │█│
│██│ 客户        │█│
│██│ · 客户组合  │█│
│██│ · 客户体检  │█│
│██│ · 需求/机会 │█│
│██│             │█│
│██│ ...         │█│
│██│             │█│
│██├─────────────┤█│
│██│ 用户区      │█│
│██└─────────────┘█│
│██████████████████│
└──────────────────┘
```

### 26.2 移动端规格

| 属性 | 值 |
|------|-----|
| 断点 | <768px |
| 侧边栏 | 隐藏, transform=translateX(-100%) |
| 汉堡按钮 | 顶栏左侧, 32x32, ☰ 图标 |
| 抽屉宽度 | 272px |
| 遮罩 | bg=rgba(0,0,0,0.4), z-index=40 |
| 过渡 | transform 300ms cubic-bezier(0.4,0,0.2,1) |
| 关闭方式 | 点击遮罩 / Esc 键 / 路由变化 / 点击导航项 |
| 焦点管理 | 打开时焦点进入侧边栏, 关闭时焦点回到汉堡按钮 |

### 26.3 移动端专属页面

| 页面 | 路由 | 说明 |
|------|------|------|
| 移动端今日 | /m/today | 今日待办概览 |
| 移动端访前 | /m/previsit | 简化版访前准备 |
| 移动端笔记 | /m/notes | 会中快速笔记 |
| 移动端结账 | /m/checkout | 访后快速结账 |

### 26.4 MobileTodayView 规格

| 属性 | 值 |
|------|-----|
| 布局 | 垂直列表, 无侧边栏 |
| 今日待办 | NCard 列表, 每项 h=64px |
| 快捷操作 | 底部固定栏, 2-3 个快捷按钮 |

---

## 27. 通用组件规格

### 27.1 ObjectHeader

| 属性 | 值 |
|------|-----|
| Props | objectType, objectStatus, title, pageId |
| Slots | actions (右侧操作区) |
| 布局 | flex, justify-between, align-center |
| 底边框 | 1px solid var(--border-light) |
| 下边距 | 20px |
| 对象类型 | 11px, uppercase, letter-spacing=0.06em, font-weight=600 |
| 标题 | 22px, font-weight=700 |
| 返回按钮 | NButton quaternary size=small |

### 27.2 PageState

| 属性 | 值 |
|------|-----|
| Props | status: ResourceStatus, error?: string, idleDescription?: string |
| Events | retry |
| idle | NEmpty, 垂直居中, padding=64px 0 |
| loading | NSpin large + "加载中…" |
| error | NResult status=error + 重试按钮 |
| success | 具名 slot |

### 27.3 DisabledAction

| 属性 | 值 |
|------|-----|
| Props | label, disabled, reason, unlockPath, buttonTestId?, hideReason? |
| 禁用态 | NButton disabled + NTooltip(reason) |
| 原因文字 | 12px, color=var(--text-tertiary) |
| 启用态 | NButton type=primary |

### 27.4 StagePath

| 属性 | 值 |
|------|-----|
| Props | stages: StagePathStage[], completedKeys: string[], currentKey: string |
| 步骤圆点 | 24px, 已完成=var(--v8-teal), 当前=var(--brand-primary), 未完成=var(--v8-line) |
| 连线 | 2px, 已完成=var(--v8-teal), 未完成=var(--v8-line) |
| 标签 | 13px, font-weight=600 |

### 27.5 SignalsDomainTabs

| 属性 | 值 |
|------|-----|
| 选项卡 | 经营旅程 / 经营信号 / 互动对象 |
| 路由 | /engagement, /signals, /engagements |
| 激活 | border-bottom=2px solid var(--gits-blue-600) |

### 27.6 RiskBadge

| 风险等级 | 颜色 | NTag type |
|----------|------|-----------|
| LOW | var(--v8-teal) | success |
| MEDIUM | var(--color-warning) | warning |
| HIGH | var(--color-danger) | error |

### 27.7 CustomerCard

| 属性 | 值 |
|------|-----|
| Props | customer: Customer |
| Events | click |
| 容器 | NCard hoverable, cursor=pointer |
| 悬停 | translateY(-2px), shadow |
| 客户名 | 16px, font-weight=600 |
| 标签 | NTag size=small type=info, 最多3个 |

### 27.8 AnalyticsPageNav

| 属性 | 值 |
|------|-----|
| Props | items: AnalyticsNavItem[], modelValue: string |
| Events | update:modelValue |
| 宽度 | 196px |
| 激活 | border-left=3px solid var(--gits-blue-600) |
| 子项 | 缩进, 更小字号 |

### 27.9 ProductCatalog

| 属性 | 值 |
|------|-----|
| Props | families, products, selectedProductId, loading |
| Events | select(productId) |
| 产品族 | 可折叠, ▸/▾ 箭头 |
| 产品项 | 32px 高, 13px 字号 |
| 选中 | 高亮背景+加粗 |

### 27.10 ProductSectionNav

| 属性 | 值 |
|------|-----|
| 位置 | sticky, top=49px |
| 滚动同步 | IntersectionObserver |
| 激活 | bg=var(--brand-primary-lighter), font-weight=600 |

---

## 28. 交互状态矩阵

### 28.1 导航项状态

| 状态 | 背景 | 文字 | 左竖线 | 字重 |
|------|------|------|--------|------|
| 默认 | transparent | var(--v8-steel) | none | 400 |
| 悬停 | rgba(17,45,64,0.04) | var(--v8-ink) | none | 400 |
| 选中 | rgba(17,45,64,0.07) | var(--v8-dark) | 3px solid var(--v8-dark) | 600 |
| 聚焦 | rgba(17,45,64,0.04) | var(--v8-steel) | none | 400, outline=2px solid var(--v8-ring) |
| 禁用 | transparent | var(--v8-line-strong) | none | 400, opacity=0.5 |

### 28.2 按钮状态

| 状态 | 背景 | 文字 | 边框 |
|------|------|------|------|
| 默认 | var(--brand-primary) | #fff | none |
| 悬停 | var(--brand-primary-light) | #fff | none |
| 按下 | var(--brand-primary-dark) | #fff | none |
| 禁用 | var(--v8-soft) | var(--v8-faint) | none |
| 加载 | var(--brand-primary) | #fff | none + spinner |

### 28.3 卡片状态

| 状态 | 阴影 | 变换 | 边框 |
|------|------|------|------|
| 默认 | var(--shadow-sm) | none | 1px solid var(--v8-line) |
| 悬停 | var(--shadow-md) | translateY(-2px) | 1px solid var(--brand-primary-light) |
| 选中 | var(--shadow-md) | none | 2px solid var(--brand-primary) |
| 禁用 | none | none | 1px solid var(--v8-line), opacity=0.5 |

### 28.4 输入框状态

| 状态 | 边框 | 背景 | 阴影 |
|------|------|------|------|
| 默认 | 1px solid var(--v8-line) | var(--v8-paper) | none |
| 聚焦 | 1px solid var(--brand-primary) | var(--v8-paper) | 0 0 0 3px rgba(59,88,200,0.1) |
| 错误 | 1px solid var(--color-danger) | var(--v8-paper) | 0 0 0 3px rgba(192,57,43,0.1) |
| 禁用 | 1px solid var(--v8-line) | var(--v8-soft) | none |

### 28.5 表格行状态

| 状态 | 背景 |
|------|------|
| 默认 | transparent |
| 悬停 | rgba(17,45,64,0.03) |
| 选中 | rgba(59,88,200,0.06) |
| 条纹 | rgba(17,45,64,0.015) |

---

## 29. 响应式断点规格

| 断点 | 宽度 | 侧边栏 | 内容区 | 变化 |
|------|------|--------|--------|------|
| xl | ≥1440px | 256px 展开 | 自适应 | 默认布局 |
| lg | ≥1024px | 256px 展开 | 自适应 | 无变化 |
| md | ≥768px | 60px 收起 | 自适应 | 侧边栏默认收起 |
| sm | <768px | 隐藏(抽屉) | 100% | 汉堡菜单+抽屉 |

### 29.1 各断点页面适配

| 页面元素 | xl (≥1440) | lg (1024-1439) | md (768-1023) | sm (<768) |
|----------|-----------|---------------|--------------|-----------|
| 侧边栏 | 256px 展开 | 256px 展开 | 60px 收起 | 抽屉 |
| 内容区 padding | 24px | 24px | 20px | 16px |
| 产品中心三栏 | 240+auto+280 | 200+auto+240 | 隐藏左右栏 | 单栏 |
| 分析页双栏 | 196+auto | 160+auto | 单栏 | 单栏 |
| 卡片网格 | 4列 | 3列 | 2列 | 1列 |
| 表格 | 全字段 | 关键字段 | 关键字段 | 卡片视图 |
| ObjectHeader | 水平 | 水平 | 垂直堆叠 | 垂直堆叠 |

---

## 30. 无障碍规格

### 30.1 键盘导航

| 区域 | 键 | 行为 |
|------|-----|------|
| 侧边栏 | Tab | 导航项间移动 |
| 侧边栏 | Enter/Space | 激活导航项 |
| 侧边栏 | ↑/↓ | 导航项间移动 |
| 组标题 | Enter/Space | 展开/收起组 |
| 抽屉 | Esc | 关闭抽屉 |
| 面包屑 | Tab | 链接间移动 |
| 表格 | Tab | 单元格间移动 |
| 模态 | Esc | 关闭模态 |
| 章节导航 | Tab | 链接间移动 |

### 30.2 ARIA 属性

| 元素 | 属性 | 值 |
|------|------|-----|
| 侧边栏 | role | navigation |
| 侧边栏 | aria-label | "主导航" |
| 导航组标题 | aria-expanded | true/false |
| 导航项 | role | link |
| 面包屑 | nav aria-label | "面包屑" |
| 抽屉遮罩 | role | presentation |
| StagePath | role | list |
| StagePath 步骤 | role | listitem |
| PageState | aria-live | polite |
| 加载中 | aria-busy | true |
| 禁用操作 | aria-disabled | true |

### 30.3 颜色对比度

| 组合 | 对比度 | WCAG |
|------|--------|------|
| var(--v8-ink) on var(--v8-paper) | 14.2:1 | AAA |
| var(--v8-steel) on var(--v8-canvas) | 6.8:1 | AA |
| var(--v8-faint) on var(--v8-paper) | 4.6:1 | AA |
| var(--brand-primary) on var(--v8-paper) | 5.2:1 | AA |
| #fff on var(--v8-dark) | 12.1:1 | AAA |
| var(--color-danger) on var(--v8-paper) | 5.8:1 | AA |
| var(--v8-teal) on var(--v8-paper) | 4.8:1 | AA |

### 30.4 焦点指示器

| 元素 | 焦点样式 |
|------|---------|
| 导航项 | outline: 2px solid var(--v8-ring), outline-offset: 2px |
| 按钮 | outline: 2px solid var(--v8-ring), outline-offset: 2px |
| 链接 | outline: 2px solid var(--v8-ring), outline-offset: 2px, border-radius: 2px |
| 输入框 | border-color: var(--brand-primary), box-shadow: 0 0 0 3px rgba(59,88,200,0.1) |

### 30.5 动效偏好

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

### 30.6 屏幕阅读器

- 所有图标附带 `aria-hidden="true"` + 相邻文字标签
- 状态变化使用 `aria-live="polite"` 通知
- 表格使用 `<th scope>` 标记
- 表单输入关联 `<label>`
- 装饰元素标记 `role="presentation"`
