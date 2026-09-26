# GITS Bank V8 对公经营书桌 — 前端 UX 设计规格索引

> **版本**: V8.0 · **日期**: 2026-09-25 · **用途**: 外部智能体审阅

## 文件清单

| 文件 | 内容 | 页面覆盖 |
|------|------|---------|
| [Part1](./V8-UX-Spec-Part1-Shell-Login-Workbench.md) | 设计令牌、Shell 布局、登录页、经营总览 | 全局 + P01 + Login |
| [Part2](./V8-UX-Spec-Part2-Customer-Signals.md) | 客户组合、客户记录、经营信号、经营旅程 | P02 + P04 + P08 + P11 |
| [Part3](./V8-UX-Spec-Part3-Previsit-Meeting-Postvisit.md) | 访前准备、会中协作、访后核验 | P14-1/2/3 + P15 + P16 |
| [Part4](./V8-UX-Spec-Part4-Product-Recommendation.md) | 承诺事项、产品解读、产品中心、产品推荐 | P36 + P38 + PC1 + WP5-1 |
| [Part5](./V8-UX-Spec-Part5-Proposal-Analytics-Admin.md) | 建议书、经营分析、审批、审计、CRM回写 | P23 + P25 + Analytics + Admin |
| [Part6](./V8-UX-Spec-Part6-Mobile-Components-States-A11y.md) | 移动端、通用组件、交互状态、响应式、无障碍 | Mobile + Components + States + A11y |

## 设计系统概要

| 维度 | 值 |
|------|-----|
| 品牌色 | 矿物深蓝 #112D40 |
| 交互色 | 靛蓝 #3B58C8 |
| 侧边栏底色 | 暖纸色 #F9F7F1 |
| 工作区底色 | 奶油色 #F4F5F3 |
| 确认态色 | 青绿 #1A827E |
| 定位点色 | 温砂色 #C49A6C |
| 字体 | Inter + PingFang SC + Microsoft YaHei |
| 圆角 | 4px / 9px / 14px / full |
| 阴影 | 4级 (sm/md/lg/xl) |
| 动效 | 120ms / 200ms / 300ms |

## 页面覆盖矩阵

| 页面 | ID | 路由 | 所在文件 | 菜单组 |
|------|-----|------|---------|--------|
| 登录页 | - | /login | Part1 | - |
| 经营总览 | P01 | /workbench | Part1 | 经营 |
| 客户组合 | P02 | /accounts | Part2 | 客户 |
| 客户记录 | P04 | /customers/:id | Part2 | 客户 |
| 经营信号 | P08 | /signals | Part2 | 经营 |
| 经营旅程 | P11 | /engagement | Part2 | 经营 |
| 访前·缺口 | P14-1 | /previsit/gaps | Part3 | 经营 |
| 访前·证据 | P14-2 | /previsit/evidence | Part3 | 经营 |
| 访前·包 | P14-3 | /previsit/pack | Part3 | 经营 |
| 会中协作 | P15 | /in-meeting/:id | Part3 | 经营 |
| 访后核验 | P16 | /postvisit/:id | Part3 | 经营 |
| 承诺事项 | P36 | /commitments | Part4 | 方案 |
| 产品解读 | P38 | /product-knowledge | Part4 | 产品 |
| 产品中心 | PC1 | /product-center | Part4 | 产品 |
| 产品推荐 | WP5-1 | /recommendation/:runId | Part4 | 客户/产品 |
| 建议书列表 | P23 | /proposals | Part5 | 方案 |
| 建议书详情 | P25 | /proposals/:id | Part5 | 方案 |
| 经营指标 | - | /analytics/operating-metrics | Part5 | 分析 |
| 客户分群 | - | /analytics/segments | Part5 | 分析 |
| 组合看板 | - | /portfolio | Part5 | 分析 |
| 审批中心 | - | /approvals | Part5 | 方案 |
| 审计追踪 | - | /audit-trace | Part5 | 分析 |
| CRM回写 | - | /crm-writeback | Part5 | 分析 |
| 移动端 | - | /m/* | Part6 | - |

## 审阅重点

1. **色彩系统**: V8 双蓝色层级（品牌锚定 #112D40 + 交互承载 #3B58C8）是否清晰区分
2. **导航结构**: 5 组 19 项菜单是否准确反映客户经理工作路径
3. **四态处理**: 每个数据页面是否完整覆盖 idle/loading/error/success
4. **移动端**: 抽屉交互（打开/关闭/Esc/遮罩/焦点）是否完整
5. **无障碍**: 键盘导航、ARIA、对比度、动效偏好是否达标
6. **业务顺序**: 产品解读 → 客户体检 → 受控推荐 的业务顺序是否在导航中正确体现
