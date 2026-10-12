# GITS Bank V8 对公经营书桌 — 逐页前端 UX 设计规格

> **版本**: V8.0 · **日期**: 2026-09-25 · **用途**: 外部智能体审阅  
> **设计系统**: V8 矿物深蓝 + 暖纸色 + 靛蓝交互色 + 青绿确认态  
> **技术栈**: Vue 3 + Naive UI + Tailwind CSS + Vite

---

## 1. 设计令牌（Design Tokens）

### 1.1 V8 色彩系统

| Token | 值 | 用途 |
|-------|-----|------|
| `--v8-dark` | `#112D40` | 矿物深蓝：品牌锚定、侧边栏品牌区、选中态竖线 |
| `--v8-ink` | `#1A2332` | 墨色：正文标题 |
| `--v8-steel` | `#3A4A5C` | 钢色：正文、导航项默认 |
| `--v8-faint` | `#7B8794` | 淡钢色：辅助文字、占位符 |
| `--v8-line` | `#D8DEE4` | 线色：分隔线、边框 |
| `--v8-line-strong` | `#B0B8C1` | 强线色：强调分隔 |
| `--v8-soft` | `#EEF0F2` | 柔色：骨架屏底色 |
| `--v8-cream` | `#F4F5F3` | 奶油色：工作区底色 |
| `--v8-paper` | `#FFFFFF` | 纸色：卡片/面板底色 |
| `--v8-canvas` | `#F9F7F1` | 画布色：侧边栏底色 |
| `--brand-primary` | `#3B58C8` | 靛蓝：交互色、主操作按钮 |
| `--brand-primary-light` | `#5a78d8` | 靛蓝-浅：悬停态 |
| `--brand-primary-dark` | `#2C46AE` | 靛蓝-深：按下态 |
| `--v8-teal` | `#1A827E` | 青绿：确认态、成功指示 |
| `--v8-amber` | `#C49A6C` | 温砂色：小面积定位点 |
| `--color-danger` | `#c0392b` | 警示红：错误、高风险 |
| `--color-warning` | `#836239` | 警告琥珀：中风险、待确认 |
| `--color-info` | `#3B58C8` | 信息蓝：提示 |
| `--color-success` | `#1A827E` | 成功青绿：确认、低风险 |

### 1.2 排版系统

| Token | 值 | 用途 |
|-------|-----|------|
| `--font-sans` | Inter, PingFang SC, Microsoft YaHei, Noto Sans CJK SC, system-ui | 主字体栈 |
| `--font-display` | Inter, system-ui | 品牌标题 |
| `--text-xs` | 11px | 辅助标注 |
| `--text-sm` | 13px | 导航项、表格辅助 |
| `--text-base` | 14px | 正文 |
| `--text-lg` | 18px | 区块标题 |
| `--text-xl` | 22px | 页面标题 |
| `--leading-tight` | 1.25 | 标题行高 |
| `--leading-normal` | 1.5 | 正文行高 |

### 1.3 间距系统

| Token | 值 | 用途 |
|-------|-----|------|
| `--space-1` | 4px | 图标与文字间距 |
| `--space-2` | 8px | 紧凑元素间距 |
| `--space-3` | 12px | 导航项内边距 |
| `--space-4` | 16px | 区块间距 |
| `--space-5` | 20px | 卡片内边距 |
| `--space-6` | 24px | 页面内边距 |
| `--space-8` | 32px | 区段间距 |
| `--space-12` | 48px | 大区段间距 |

### 1.4 圆角系统

| Token | 值 | 用途 |
|-------|-----|------|
| `--radius-sm` | 4px | 小按钮、标签 |
| `--radius-md` | 9px | 卡片、输入框（V8 分层圆角） |
| `--radius-lg` | 14px | 面板、对话框 |
| `--radius-full` | 9999px | 胶囊、头像 |

### 1.5 阴影系统

| Token | 值 | 用途 |
|-------|-----|------|
| `--shadow-sm` | 0 1px 2px rgba(17,45,64,0.05) | 卡片微浮 |
| `--shadow-md` | 0 4px 12px rgba(17,45,64,0.08) | 面板浮层 |
| `--shadow-lg` | 0 8px 24px rgba(17,45,64,0.12) | 对话框 |
| `--shadow-xl` | 0 16px 48px rgba(17,45,64,0.16) | 抽屉 |

### 1.6 动效系统

| Token | 值 | 用途 |
|-------|-----|------|
| `--transition-fast` | 120ms ease | 悬停、焦点 |
| `--transition-normal` | 200ms ease | 展开/收起 |
| `--transition-slow` | 300ms cubic-bezier(0.4,0,0.2,1) | 抽屉、模态 |

---

## 2. 全局 Shell 布局

### 2.1 布局结构

```
┌──────────────────────────────────────────────────────────────┐
│ Shell Header（顶栏）                                         │
│ h=48px · bg=rgba(255,255,255,0.88) · backdrop-blur          │
│ 左：面包屑 · 右：主题切换 + 用户头像                          │
├────────┬─────────────────────────────────────────────────────┤
│        │                                                     │
│ Side   │  Main Content                                       │
│ bar    │                                                     │
│        │  padding: 24px                                      │
│ 256px  │  bg: var(--v8-cream) #F4F5F3                        │
│ (展开) │                                                     │
│ 60px   │                                                     │
│ (收起) │                                                     │
│        │                                                     │
│ bg:    │                                                     │
│ var(-- │                                                     │
│ v8-    │                                                     │
│ canvas)│                                                     │
│ #F9F7F1│                                                     │
│        │                                                     │
├────────┤                                                     │
│ User   │                                                     │
│ Area   │                                                     │
│ h=56px │                                                     │
└────────┴─────────────────────────────────────────────────────┘
```

### 2.2 侧边栏（AppSidebar）

**展开态（256px）**

| 区域 | 规格 |
|------|------|
| 品牌区 | h=64px, bg=var(--v8-dark) #112D40, 左对齐品牌名+副标题 |
| 导航组 | 每组：组标题（可点击展开/收起）+ 子项列表 |
| 组标题 | h=32px, font-size=11px, letter-spacing=0.06em, text-transform=uppercase, color=var(--v8-faint) |
| 导航项 | h=36px, pl=36px, font-size=13px, color=var(--v8-steel), border-radius=6px |
| 导航项·悬停 | bg=rgba(17,45,64,0.04), color=var(--v8-ink) |
| 导航项·选中 | bg=rgba(17,45,64,0.07), color=var(--v8-dark), font-weight=600, 左侧3px竖线 bg=var(--v8-dark) |
| 导航项·聚焦 | outline=2px solid var(--v8-ring), outline-offset=2px |
| 收起按钮 | 底部, 36x36px, 圆形, bg=var(--v8-soft), 悬停 bg=var(--v8-line) |
| 用户区 | h=56px, 头像32px + 姓名 + 角色 |

**收起态（60px）**

| 区域 | 规格 |
|------|------|
| 品牌区 | 仅显示品牌图标（26x26 SVG） |
| 导航项 | 仅显示图标，居中，32x32, tooltip 显示全名 |
| 收起按钮 | 变为展开箭头 |

**移动端抽屉（<768px）**

- 侧边栏默认隐藏（transform: translateX(-100%)）
- 汉堡按钮出现在顶栏左侧
- 点击后侧边栏从左滑出，z-index=50
- 遮罩层 bg=rgba(0,0,0,0.4), 点击关闭
- Esc 键关闭
- 路由变化自动关闭
- 过渡动画: transform 300ms cubic-bezier(0.4,0,0.2,1)

### 2.3 顶栏（Shell Header）

| 元素 | 规格 |
|------|------|
| 高度 | 48px |
| 背景 | rgba(255,255,255,0.88) + backdrop-blur(8px) |
| 底边框 | 1px solid var(--v8-line) |
| 面包屑 | 左侧, font-size=13px |
| 面包屑·组名 | color=var(--v8-faint), hover=var(--brand-primary) |
| 面包屑·分隔符 | `/` color=var(--v8-line) |
| 面包屑·当前页 | color=var(--v8-ink), font-weight=600 |
| 主题切换 | 右侧, 32x32, 圆形按钮 |
| 用户头像 | 右侧, 28px 圆形 |

### 2.4 面包屑规则

面包屑由 `navConfig.ts` 自动计算：`组名 / 菜单项名`

- 一级菜单项：`经营 / 经营总览`
- 深层页面：`客户 / 客户组合`（/accounts）
- 对象详情页：面包屑不变，页面内 ObjectHeader 显示对象标题

### 2.5 导航菜单结构

| 组 | 菜单项 | 路由 | 图标 |
|----|--------|------|------|
| **经营** | 经营总览 | /workbench | ◧ |
| | 经营信号 | /signals | ◈ |
| | 经营旅程 | /engagement | ◉ |
| **客户** | 客户组合 | /accounts | ◫ |
| | 客户体检 | /recommendation/new | ◆ |
| | 需求/机会 | /needs | ◇ |
| **产品** | 产品解读 | /product-center | ◷ |
| | 受控推荐 | /recommendation | ◿ |
| | 产品知识 | /product-knowledge | ◬ |
| **方案** | 建议书 | /proposals | ◮ |
| | 承诺事项 | /commitments | ◯ |
| | 审批中心 | /approvals | ✓ |
| **分析** | 经营指标 | /analytics/operating-metrics | ◓ |
| | 客户分群 | /analytics/segments | ◔ |
| | 组合看板 | /portfolio | ◕ |
| | 审计追踪 | /audit-trace | ◑ |
| | CRM 回写 | /crm-writeback | ◘ |

---

## 3. 登录页

### 3.1 布局

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│              bg: var(--v8-canvas) #F9F7F1                    │
│              装饰纹理: 135° 对角线, opacity=0.3              │
│                                                              │
│              ┌──────────────────────────┐                    │
│              │ 品牌条                    │                    │
│              │ bg: var(--v8-dark) #112D40│                    │
│              │ h=72px                    │                    │
│              │ [图标] GITS Bank          │                    │
│              │        对公经营书桌        │                    │
│              ├──────────────────────────┤                    │
│              │ 表单区                    │                    │
│              │ bg: var(--v8-paper)       │                    │
│              │ padding: 28px 32px 24px   │                    │
│              │                           │                    │
│              │ 登录到您的账户             │                    │
│              │ ┌────────────────────┐    │                    │
│              │ │ API Key            │    │                    │
│              │ └────────────────────┘    │                    │
│              │ [──── 登录 ────]          │                    │
│              │                           │                    │
│              │ 内网开发环境·API Key 认证   │                    │
│              └──────────────────────────┘                    │
│                                                              │
│              max-width: 420px                                │
│              border-radius: var(--radius-lg) 14px            │
│              box-shadow: var(--shadow-md)                    │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 3.2 品牌条规格

| 属性 | 值 |
|------|-----|
| 背景 | `var(--v8-dark)` #112D40 |
| 高度 | 72px |
| 内边距 | 24px 32px |
| 图标 | 42x42, bg=rgba(255,255,255,0.10), border-radius=9px, 内含26x26 SVG |
| 品牌名 | font-family=var(--font-display), 22px, font-weight=700, color=#fff, letter-spacing=0.04em |
| 副标题 | 12px, color=rgba(255,255,255,0.6), letter-spacing=0.06em, "对公经营书桌" |

### 3.3 表单区规格

| 属性 | 值 |
|------|-----|
| 背景 | `var(--v8-paper)` #FFFFFF |
| 内边距 | 28px 32px 24px |
| 标题 | 16px, font-weight=600, color=var(--v8-ink), "登录到您的账户" |
| 输入框 | Naive UI NInput, type=password, show-password-on=click |
| 按钮 | Naive UI NButton type=primary, block, loading 态 |
| 提示 | 11px, color=var(--v8-faint), 居中, "内网开发环境·API Key 认证" |

### 3.4 状态矩阵

| 状态 | 表现 |
|------|------|
| 默认 | 品牌条深蓝 + 白色表单区 |
| 空提交 | NMessage warning: "请输入 API Key" |
| 认证中 | 按钮显示 loading spinner, 输入框 disabled |
| 认证失败 | NMessage error: "认证失败，请检查 API Key" |
| 成功 | 路由跳转 /workbench |

### 3.5 响应式

| 断点 | 变化 |
|------|------|
| ≤480px | 卡片 max-width=100%, 品牌条 padding=20px 24px, 表单区 padding=24px |

---

## 4. 经营总览（P01）

### 4.1 页面结构

```
┌─────────────────────────────────────────────────────────────┐
│ ObjectHeader                                                │
│ ┌──────────────────────────────┐ ┌──────────────────────┐  │
│ │ 客户经营应用                  │ │ [返回并恢复位置]      │  │
│ │ 经营总览                      │ │                      │  │
│ │ 当前状态：已加载              │ │                      │  │
│ └──────────────────────────────┘ └──────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│ PageState (四态)                                            │
│ ┌─ Success ─────────────────────────────────────────────┐  │
│ │ [搜索客户/原因...]  行动队列(3) | 暂存快照(0)          │  │
│ │                                                       │  │
│ │ 行动队列表格                                          │  │
│ │ ┌────────────────────────────────────────────────┐   │  │
│ │ │ 客户名 │ 候选原因 │ 风险 │ 层级 │ 排名分       │   │  │
│ │ │ XX公司 │ 存款下降 │ HIGH │ KEY  │ 34           │   │  │
│ │ └────────────────────────────────────────────────┘   │  │
│ │                                                       │  │
│ │ DisabledAction: [一键访前](disabled)                  │  │
│ │ 原因：需先选择客户。解除路径：从行动队列选择客户       │  │
│ └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 ObjectHeader 规格（全局复用）

| 属性 | 值 |
|------|-----|
| 布局 | flex, justify-between, align-center |
| 底边框 | 1px solid var(--border-light) |
| 下边距 | 20px |
| 对象类型 | 11px, uppercase, letter-spacing=0.06em, font-weight=600, color=var(--text-tertiary) |
| 标题 | 22px, font-weight=700, color=var(--text-primary), letter-spacing=-0.01em |
| 对象状态 | 13px, color=var(--text-secondary) |
| 返回按钮 | NButton quaternary size=small, "返回并恢复位置" |

### 4.3 PageState 四态（全局复用）

| 状态 | 视觉 |
|------|------|
| idle | NEmpty "尚未加载", 垂直居中, padding=64px 0 |
| loading | NSpin large + "加载中…", 垂直居中 |
| error | NResult status=error + 重试按钮 |
| success | 具名 slot 渲染业务内容 |

### 4.4 行动队列

| 属性 | 值 |
|------|-----|
| 数据源 | `fetchCustomers()` → 派生行动队列 |
| 排序 | 风险权重(30/20/10) + 层级权重(4/3/2/1) 降序 |
| 筛选 | 客户名/候选原因 模糊匹配 |
| 行点击 | 路由到 `/customers/:id` |
| 空态 | "暂无待行动客户" |

### 4.5 DisabledAction 规格（全局复用）

| 属性 | 值 |
|------|-----|
| 禁用态 | NButton disabled type=primary + NTooltip 显示原因 |
| 原因文字 | 12px, color=var(--text-tertiary), "原因：{reason}。解除路径：{unlockPath}" |
| 启用态 | NButton type=primary 正常可点击 |
