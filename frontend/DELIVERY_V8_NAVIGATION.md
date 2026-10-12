# V8 导航改造交付报告

## ① 正式菜单与路由权限映射表

见 `NAVIGATION_MAP_V8.md`，包含 19 个一级菜单项、5 个菜单组、完整路由映射和 5 项待业务确认项。

## ② 高保真效果截图

| 截图 | 文件 | 说明 |
|------|------|------|
| 登录页 1440px | `screenshots/v8-login-1440.png` | 矿物深蓝品牌条 + 暖纸色底 |
| 经营总览 1440px | `screenshots/v8-workbench-1440.png` | 暖纸色侧边栏 + 工作区底 |
| 窄屏 1024px | `screenshots/v8-workbench-1024.png` | 侧边栏收窄 |
| 手机 390px | `screenshots/v8-workbench-390.png` | 汉堡菜单 + 抽屉 |
| 侧边栏展开 1440px | `screenshots/v8-sidebar-expanded-1440.png` | 5 组导航全部展开 |
| 产品中心 1440px | `screenshots/v8-product-center-1440.png` | 产品组激活 |
| 客户组合 1440px | `screenshots/v8-accounts-1440.png` | 客户组激活 |
| 分析页 1440px | `screenshots/v8-analytics-1440.png` | 分析组激活 |
| 收起侧边栏 1440px | `screenshots/v8-collapsed-1440.png` | 60px 收起态 |
| 移动端抽屉 390px | `screenshots/v8-mobile-390.png` | 抽屉打开态 |

## ③ 可复用组件与代码改动

| 文件 | 改动类型 | 说明 |
|------|----------|------|
| `src/assets/styles/theme.css` | 重写 | V8 色彩系统：矿物深蓝+靛蓝+暖纸色+青绿+温砂色 |
| `src/layouts/navConfig.ts` | 重写 | 5 组 19 项菜单结构 + 路由映射函数 |
| `src/components/shell/AppSidebar.vue` | 重写 | V8 暖纸色侧边栏：品牌区/导航组/收起/用户区/移动端抽屉 |
| `src/layouts/ExperienceShell.vue` | 重写 | V8 顶栏+面包屑+移动端遮罩+汉堡按钮 |
| `src/styles/shell.css` | 重写 | V8 全局样式：骨架屏/空状态/关键面/确认态/打印 |
| `src/views/Login.vue` | 改造 | V8 登录页：矿物深蓝品牌条+装饰纹理 |
| `src/theme/naiveTheme.ts` | 改造 | V8 色彩映射到 Naive UI |
| `src/style.css` | 微调 | 导入路径不变 |
| `src/theme/__tests__/naiveTheme.spec.ts` | 微调 | V8 字体族断言更新 |

### 关键组件 API

**AppSidebar.vue**
- Props: 无（自包含）
- 自动展开当前激活组
- 收起/展开按钮
- 移动端抽屉模式（768px 断点）

**ExperienceShell.vue**
- 自动面包屑（从 navConfig 计算）
- 移动端汉堡菜单
- Esc 键关闭抽屉
- 路由变化自动关闭抽屉

**navConfig.ts**
- `SHELL_NAV_GROUPS`: 菜单结构定义
- `SHELL_NAV_ITEMS`: 扁平化菜单项
- `navDomainForPath(path)`: 路径→domain 映射
- `navGroupLabelForDomain(domain)`: domain→组名
- `navItemLabelForPath(path)`: 路径→菜单项名

## ④ 改造前后对比

| 维度 | V6 CitiDirect（旧） | V8 对公经营书桌（新） |
|------|---------------------|---------------------|
| 侧边栏底色 | 冷灰白 `#f8f9fb` | 暖纸色 `#F9F7F1` |
| 品牌区色 | 海军蓝 `#002d72` | 矿物深蓝 `#112D40` |
| 交互色 | 蔚蓝 `#056dae` | 靛蓝 `#3B58C8` |
| 激活指示 | 蔚蓝竖线 | 深矿蓝竖线 `#112D40` |
| 选中态底色 | `#e8f4fa`（微蓝） | `rgba(17,45,64,0.07)`（微深蓝灰） |
| 页面底色 | 纯白 `#ffffff` | 工作区底 `#F4F5F3` |
| 圆角 | 8px 统一 | 9px 默认，4-14px 分层 |
| 字体 | Overpass/Interstate | Inter + 系统中文 |
| 确认态色 | 绿色 `#00823B` | 青绿 `#1A827E` |
| 品牌副标题 | "对公客户经营工作台" | "对公经营书桌" |
| 菜单结构 | 5 组 15 项 | 5 组 19 项 |
| 面包屑 | 无 | 组名 / 菜单项名 |
| 移动端 | 无抽屉 | 汉堡菜单+抽屉+Esc+遮罩 |
| 收起侧边栏 | 无 | 60px 收起态 |
| 登录页 | 白底+品牌条 | 暖纸色底+装饰纹理+品牌条 |

## ⑤ 尚需业务确认的菜单差异

1. **「客户体检」与「受控推荐」是否合并？** 当前是推荐工作区的两个阶段
2. **「产品知识」是否归入产品组？** 语义属于产品域但页面独立
3. **「审批中心」是否需要独立菜单？** 审批角色可能不限于方案
4. **经营分析组是否需要更多菜单项？** KERT 后续可能增加
5. **移动端是否需要独立菜单结构？** 当前 /m/* 不在桌面导航中

## 验证结果

- ✅ TypeScript 类型检查通过
- ✅ 10/10 naiveTheme 测试通过
- ✅ 全部 vitest 测试通过
- ✅ Vite 构建成功
- ✅ 登录页：矿物深蓝品牌区 + 暖纸色底
- ✅ 侧边栏：暖纸色底 + 深矿蓝品牌区 + 5 组导航
- ✅ 深层链接刷新后选中态正确（/signals→经营信号, /analytics/*→分析组）
- ✅ 面包屑自动计算
- ✅ 移动端：抽屉打开/关闭/Esc/遮罩
- ✅ 侧边栏收起/展开
- ✅ 导航组展开/收起动画
