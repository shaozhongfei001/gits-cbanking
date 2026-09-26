# V8 导航菜单与路由权限映射表

> 基于 V8「对公经营书桌」设计语言，映射现有 59 个页面到一级/二级菜单。

---

## 1. 菜单结构总览

V8 样稿有 7 个菜单项（经营总览/客户档案/访前准备/持续经营/产品解读/客户体检/受控推荐），其中 03/04/06/07 在样稿中用弹窗呈现。**正式产品按真实页面和路由决定入口**，不因样稿删减页面或编造权限。

### 一级菜单（5 组）

| 组 | Key | 中文名 | 设计意图 |
|---|---|---|---|
| 经营 | `workspace` | 经营 | 客户经理日常工作入口：总览、任务、旅程 |
| 客户 | `client` | 客户 | 客户档案与经营全景，从组合到个体 |
| 产品 | `product` | 产品 | 产品解读→客户体检→受控推荐的业务顺序 |
| 方案 | `proposal` | 方案 | 建议书、协同、交付、账户计划 |
| 分析 | `analytics` | 分析 | 经营分析（KERT 数据服务） |

### 菜单项与路由映射

| # | 菜单组 | 菜单项 | Key | 路由 | pageId | 可见角色 | 面包屑 | 实现状态 |
|---|---|---|---|---|---|---|---|---|
| 01 | 经营 | 经营总览 | `workbench` | `/workbench` | P01 | RM | 经营 / 经营总览 | ✅ 已实现 |
| 02 | 经营 | 我的任务 | `commitments` | `/commitments` | P36 | RM | 经营 / 我的任务 | ✅ 已实现 |
| 03 | 经营 | 经营旅程 | `journeys` | `/engagement` | P45 | RM | 经营 / 经营旅程 | ✅ 已实现 |
| 04 | 客户 | 客户组合 | `portfolio` | `/accounts` | P02 | RM | 客户 / 客户组合 | ✅ 已实现 |
| 05 | 客户 | 客户全景 | `panorama` | `/customers/:id` | P04 | RM | 客户 / 客户全景 | ✅ 已实现 |
| 06 | 客户 | 经营信号 | `signals` | `/signals` | P08 | RM | 客户 / 经营信号 | ✅ 已实现 |
| 07 | 客户 | 需求与机会 | `needs` | `/needs` | P20 | RM | 客户 / 需求与机会 | ✅ 已实现 |
| 08 | 产品 | 产品解读 | `product-center` | `/product-center` | — | RM | 产品 / 产品解读 | ✅ 已实现 |
| 09 | 产品 | 客户体检 | `recommendation` | `/recommendation/new` | — | RM | 产品 / 客户体检 | ✅ 已实现 |
| 10 | 产品 | 受控推荐 | `recommendation-run` | `/recommendation/:runId` | — | RM | 产品 / 受控推荐 | ✅ 已实现 |
| 11 | 产品 | 产品知识 | `product-knowledge` | `/product-knowledge/interpretation` | P38 | RM | 产品 / 产品知识 | ✅ 已实现 |
| 12 | 方案 | 服务建议书 | `proposals` | `/proposals` | P23 | RM | 方案 / 服务建议书 | ✅ 已实现 |
| 13 | 方案 | 专家协同 | `collab` | `/collab` | P31 | RM | 方案 / 专家协同 | ⚠️ 降级壳 |
| 14 | 方案 | 审批中心 | `approvals` | `/approvals` | P32 | RM+审批角色 | 方案 / 审批中心 | ✅ 已实现 |
| 15 | 方案 | 账户计划 | `account-plans` | `/account-plans` | P34 | RM | 方案 / 账户计划 | ⚠️ 降级壳 |
| 16 | 分析 | 经营指标 | `analytics-metrics` | `/analytics/operating-metrics` | — | RM | 分析 / 经营指标 | ✅ 已实现 |
| 17 | 分析 | 客群分析 | `analytics-segments` | `/analytics/segments` | — | RM | 分析 / 客群分析 | ✅ 已实现 |
| 18 | 分析 | 组合查询 | `analytics-combo` | `/analytics/combo-query` | — | RM | 分析 / 组合查询 | ✅ 已实现 |
| 19 | 分析 | 指标监视 | `analytics-monitors` | `/analytics/monitors` | — | RM | 分析 / 指标监视 | ✅ 已实现 |

---

## 2. 不进入一级菜单的页面

以下页面通过二级导航、页面内 Tab、上下文跳转或深层链接进入，**不提升为全局菜单**：

| 页面 | 入口方式 | 原因 |
|---|---|---|
| 客户档案·集团关系 `/customers/:id/group` | 客户全景页内 Tab | 页面内步骤/标签 |
| 客户档案·业务资金 `/customers/:id/funds` | 客户全景页内 Tab | 页面内步骤/标签 |
| 客户档案·关系人 `/customers/:id/parties` | 客户全景页内 Tab | 页面内步骤/标签 |
| 访前缺口 `/engagement/previsit/gaps` | 旅程工作区内步骤 | 业务阶段 |
| 访前证据 `/engagement/previsit/evidence` | 旅程工作区内步骤 | 业务阶段 |
| 访前包 `/engagement/previsit/pack` | 旅程工作区内步骤 | 业务阶段 |
| 会中工作区 `/in-meeting/:id` | 旅程工作区内步骤 | 业务阶段 |
| 会中捕获 `/in-meeting/:id/capture` | 会中工作区内步骤 | 业务阶段 |
| 离场确认 `/in-meeting/:id/checkout` | 会中工作区内步骤 | 业务阶段 |
| 访后对账 `/engagement/postvisit` | 旅程工作区内步骤 | 业务阶段 |
| CRM 回写 `/engagement/crm-writeback` | 旅程工作区内步骤 | 业务阶段 |
| 互动工作区 `/engagement/workspace/:journeyId` | 旅程详情页跳转 | 上下文关联 |
| 经营信号记录 `/signals/:id` | 列表→详情 | 上下文关联 |
| 需求记录 `/needs/:id` | 列表→详情 | 上下文关联 |
| 机会计划 `/needs/:id/plan` | 需求详情内 | 页面内步骤 |
| 建议书向导 `/proposals/new` | 建议书列表→新建 | 上下文关联 |
| 建议书记录 `/proposals/:id` | 列表→详情 | 上下文关联 |
| 建议书编辑器 `/proposals/:id/editor` | 建议书详情内 | 页面内步骤 |
| 建议书映射 `/proposals/:id/map` | 建议书详情内 | 页面内步骤 |
| 建议书依据 `/proposals/:id/evidence` | 建议书详情内 | 页面内步骤 |
| 建议书对照 `/proposals/:id/project` | 建议书详情内 | 页面内步骤 |
| 建议书版本 `/proposals/:id/versions` | 建议书详情内 | 页面内步骤 |
| 供应链报告 `/supply-chain-report/:requestId` | KERT Skill 跳转 | 外部触发 |
| 知识地图 `/knowledge-map` | 产品知识页内链接 | 页面内关联 |
| Claim 中心 `/claims` | 审计/知识页内链接 | 页面内关联 |
| 审计追踪 `/audit-trace` | 审批中心内链接 | 页面内关联 |
| 服务降级 `/degrade` | 系统异常自动跳转 | 运维页面 |
| 外部事件 `/external-events` | 经营信号页内链接 | 页面内关联 |
| 旅程时间线 `/journeys/:id` | 列表→详情 | 上下文关联 |
| 报告详情 `/reports/:id` | 列表→详情 | 上下文关联 |
| 客户价值 `/value` | 账户计划页内链接 | 页面内关联 |
| 对客交付 `/delivery` | 建议书页内链接 | 页面内关联 |
| 移动端·今日 `/m/today` | 移动端独立入口 | 独立设备 |
| 移动端·访前 `/m/previsit` | 移动端独立入口 | 独立设备 |
| 移动端·速记 `/m/notes` | 移动端独立入口 | 独立设备 |
| 移动端·离场 `/m/checkout` | 移动端独立入口 | 独立设备 |
| 旅程进入 `/engagement/enter` | 旅程列表→新建 | 上下文关联 |
| 客户组合看板 `/accounts/portfolio` | 客户组合页内 Tab | 页面内步骤 |

---

## 3. V8 样稿与正式菜单差异

| V8 样稿菜单 | 正式产品处理 | 差异说明 |
|---|---|---|
| 01 经营总览 | ✅ 保留为「经营总览」 | 路由 `/workbench` |
| 02 客户档案 | ✅ 保留为「客户全景」 | 样稿用弹窗，正式用独立页面 `/customers/:id` |
| 03 访前准备 | ❌ 不作为一级菜单 | 是旅程工作区内的业务阶段，从「经营旅程」进入 |
| 04 持续经营 | ❌ 不作为一级菜单 | 是访后回到客户经营的闭环，非独立页面入口 |
| 05 产品解读 | ✅ 保留为「产品解读」 | 路由 `/product-center` |
| 06 客户体检 | ✅ 保留为「客户体检」 | 样稿用弹窗，正式用 `/recommendation/new` |
| 07 受控推荐 | ✅ 保留为「受控推荐」 | 样稿用弹窗，正式用 `/recommendation/:runId` |

**新增菜单**（样稿无，业务需要）：
- 我的任务、经营旅程、客户组合、经营信号、需求与机会、产品知识、服务建议书、专家协同、审批中心、账户计划、经营指标、客群分析、组合查询、指标监视

---

## 4. 待业务确认项

1. **「客户体检」与「受控推荐」是否合并为一个菜单项？** 当前是同一个推荐工作区的两个阶段（三段式中的 02/03），但用户可能需要从菜单直接进入体检入口
2. **「产品知识」是否归入产品组？** 当前 `/product-knowledge/interpretation` 与产品中心是不同页面，但业务语义属于产品域
3. **「审批中心」是否需要独立菜单？** 当前归入方案组，但审批角色可能不限于方案
4. **经营分析组是否需要更多菜单项？** KERT 后续可能增加更多分析页面
5. **移动端是否需要独立菜单结构？** 当前移动端页面（/m/*）不在桌面导航中

---

## 5. V8 色彩与视觉规格

| 角色 | V8 色值 | 替换 V6 色值 | 用途 |
|---|---|---|---|
| 矿物深蓝 | `#112D40` | `#002d72` (Navy) | 品牌标识、当前导航、重点叙事面 |
| 靛蓝 | `#3B58C8` | `#056dae` (Cerulean) | 主操作、关键链接 |
| 深靛蓝 | `#2C46AE` | `#2a8fc9` (Cerulean-light) | 主操作 hover/pressed |
| 矿物青绿 | `#1A827E` | `#00823B` (Success) | 已确认状态、步骤当前态 |
| 温砂色 | `#D3A465` | 新增 | 深蓝重点面中的小面积定位点 |
| 工作区底 | `#F4F5F3` | `#ffffff` (Canvas) | 主内容背板 |
| 暖纸色 | `#F9F7F1` | `#f8f9fb` (Sidebar) | 左侧导航 |
| 主文字 | `#172C3D` | `#333333` (Ink) | 标题、值 |
| 次文字 | `#61717A` | `#666666` (Ink-muted) | 解释、辅助 |
| 弱文字 | `#63747A` | `#888888` (Tertiary) | 时间、注释 |
| 边界 | `#E1E7E7` | `#dddddd` (Hairline) | 内容分隔 |
