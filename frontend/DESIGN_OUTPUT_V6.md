# GITS V6.0 CitiDirect 前端设计输出

> 供外部智能体审阅的完整设计规格。包含设计意图、Token 系统、组件样式、与旧版对比。

---

## 1. 设计意图

**目标**：将 GITS 对公客户经营工作台从"暗色金融科技风"翻转为"CitiDirect BE® 白画布机构银行风"。

**参考对象**：CitiDirect BE® — 花旗全球机构银行数字银行平台。

**核心原则**：
1. **品牌蓝(#002d72)与交互蓝(#056dae)严格分离** — 品牌蓝仅用于品牌区（侧边栏顶部、登录页品牌条），交互蓝承载所有可点击元素
2. **纯白画布 + 浅灰条带交替** — 无装饰性色彩填充，信息密度优先
3. **"可点击=蔚蓝"用户心智** — 所有链接、按钮、激活态统一蔚蓝色
4. **8px 统一圆角** — 取代旧版 6-12px 混合圆角
5. **极轻柔阴影** — 从冷色调中等阴影降级到近乎无感

---

## 2. 色彩系统

### 2.1 基础色板（Foundational Palette）

| Token | 色值 | 用途 |
|-------|------|------|
| `--citi-navy` | `#002d72` | 品牌锚定，极度克制，仅品牌区 |
| `--citi-navy-dark` | `#001d4a` | 品牌区 hover |
| `--citi-navy-light` | `#003d99` | 品牌区 hover |
| `--citi-cerulean` | `#056dae` | 交互承载，高频出现 |
| `--citi-cerulean-light` | `#2a8fc9` | 交互 hover |
| `--citi-cerulean-dark` | `#004f80` | 交互 pressed |
| `--citi-canvas` | `#ffffff` | 页面底色 |
| `--citi-surface` | `#f4f4f4` | 浅灰条带 |
| `--citi-ink` | `#333333` | 主文字 |
| `--citi-ink-muted` | `#666666` | 次文字 |
| `--citi-ink-subtle` | `#555555` | 导航项默认色 |
| `--citi-hairline` | `#dddddd` | 分隔线 |
| `--citi-hairline-strong` | `#888888` | 强分隔/禁用文字 |

### 2.2 语义色

| 语义 | 亮色 | 用途 |
|------|------|------|
| success | `#00823B` | 确认/完成 |
| warning | `#7a4b00` | 警告 |
| danger | `#d60000` | 错误/高风险 |
| info | `#056dae` | 信息提示（=交互蓝） |

### 2.3 背景层级

| Token | 色值 | 用途 |
|-------|------|------|
| `--bg-page` | `#ffffff` | 页面底色（纯白） |
| `--bg-surface` | `#ffffff` | 卡片/面板 |
| `--bg-surface-soft` | `#f4f4f4` | 浅灰条带 |
| `--bg-elevated` | `#ffffff` | 浮层 |
| `--bg-hover` | `#eef4f9` | hover 态（微蓝灰） |
| `--bg-active` | `#d6e8f3` | active 态 |
| `--bg-sidebar` | `#f8f9fb` | 侧边栏底色 |
| `--bg-header` | `#ffffff` | 顶栏底色 |

---

## 3. 排版系统

| Token | 值 | 说明 |
|-------|------|------|
| `--font-display` | `'Noto Serif SC', 'STSong', 'SimSun', Georgia, serif` | 展示字体（合同/公文场景） |
| `--font-sans` | `'Overpass', 'Interstate', -apple-system, 'PingFang SC', 'Microsoft YaHei', ...` | UI 字体 |
| `--font-mono` | `ui-monospace, SFMono-Regular, Menlo, Consolas, ...` | 等宽字体 |
| `--text-base` | `0.875rem` (14px) | 正文 |
| `--text-sm` | `0.8125rem` (13px) | 辅助文字 |
| `--text-xs` | `0.75rem` (12px) | 标签/徽章 |

---

## 4. 圆角与阴影

| Token | 值 | 说明 |
|-------|------|------|
| `--radius-md` | `8px` | **统一默认圆角** |
| `--radius-sm` | `6px` | 小元素 |
| `--radius-xl` | `12px` | 大卡片 |
| `--shadow-xs` | `0 1px 2px rgba(0,0,0,0.04)` | 卡片默认 |
| `--shadow-sm` | `0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04)` | 卡片 hover |

---

## 5. 组件样式规格

### 5.1 侧边栏（AppSidebar.vue）

```
整体：白灰底 #f8f9fb，右边框 1px #dddddd
品牌区：深海军蓝 #002d72，高 64px
  - 品牌图标：36×36px，8px 圆角，rgba(255,255,255,0.15) 底
  - 品牌名：Noto Serif SC 18px 700，白色
  - 副标题：10px，rgba(255,255,255,0.7)
导航组标签：10px 600，#888888，0.08em 字距，大写
导航项：38px 高，8px 圆角，默认 #555555
  - hover：底色 #eef4f9，文字 #056dae
  - active：底色 #e8f4fa，文字 #056dae 600，左侧 3px 蔚蓝竖线
徽章：9px 圆角，底色 #e8f4fa，文字 #056dae 10px 700
用户区：border-top 1px #dddddd，底色 #f0f2f5
  - 头像：34px 圆形，2px #056dae 边框，底色 #e8f4fa
```

### 5.2 顶栏（ExperienceShell.vue）

```
高度：56px
底色：#ffffff
下边框：1px #dddddd
阴影：0 1px 2px rgba(0,0,0,0.04)
头像：28px 圆形，2px #056dae 边框
```

### 5.3 登录页（Login.vue）

```
页面底色：#ffffff（纯白，无渐变）
卡片：420px 宽，8px 圆角，1px #dddddd 边框
  阴影：0 4px 12px rgba(0,0,0,0.06)
品牌条：深海军蓝 #002d72，padding 24px 32px
  图标：40×40px，8px 圆角，rgba(255,255,255,0.15) 底
  品牌名：Noto Serif SC 22px 700
表单区：padding 28px 32px 24px
欢迎语：16px 600，#333333
提示语：11px，#888888
```

### 5.4 全局组件

**Section 标题竖线**：
- 3px 宽，16px 高，蔚蓝 #056dae，9999px 圆角

**按钮**：
- primary：蔚蓝底 #056dae，白字
- secondary：白底，#c0c8d0 边框，hover 时边框变蔚蓝
- ghost：透明底，hover 时微蓝灰底

---

## 6. 与旧版（V5.1）对比

| 维度 | V5.1（旧） | V6.0 CitiDirect（新） |
|------|-----------|---------------------|
| 页面背景 | 冷白 `#f8f9fb` | 纯白 `#ffffff` |
| 侧边栏 | 深海蓝渐变 `#0c1a2e→#0a1628` | 白灰 `#f8f9fb` |
| 品牌色 | 海军蓝 `#1e3a8a` | 深海军蓝 `#002d72`（仅品牌区） |
| 交互色 | 蓝金混合 | 蔚蓝 `#056dae` 统一 |
| 激活指示 | 金色渐变条 `#d4a017→#f2b84b` | 蔚蓝条 `#056dae` |
| 圆角 | 6-12px 混合 | 8px 统一 |
| 阴影 | 冷色调中等 | 极轻柔 |
| 登录页 | 深蓝渐变+毛玻璃 | 白底+深海军蓝品牌条 |
| 字体 | Noto Serif SC + 系统栈 | Overpass/Interstate + 系统栈 |
| 侧边栏文字 | 白色/金色 | 深灰/蔚蓝 |

---

## 7. Naive UI 运行时主题

```typescript
// 亮色
primaryColor: '#056dae'        // = --brand-primary = --citi-cerulean
primaryColorHover: '#2a8fc9'   // = --brand-primary-light
primaryColorPressed: '#004f80' // = --brand-primary-dark
successColor: '#00823B'
warningColor: '#7a4b00'
errorColor: '#d60000'
infoColor: '#056dae'
borderRadius: '8px'            // = --radius-md
fontFamily: 'Overpass, Interstate, -apple-system, ...'
```

---

## 8. 已知问题 / 待改进

1. **SVG 图标**：当前使用通用 SVG 路径（circle/line/path），未使用 CitiDirect 风格图标集
2. **字体加载**：Overpass/Interstate 字体未实际加载（仅声明回退链），浏览器会 fallback 到系统字体
3. **侧边栏品牌区**：使用通用"天平"SVG，非花旗伞形标志
4. **暗色模式**：CitiDirect 实际无暗色模式，当前保留最小兼容
5. **动画**：缺少 CitiDirect 特征性的微交互（如菜单展开/收起过渡）
6. **数据密集区域**：表格、表单、卡片等业务组件尚未适配新 Token
