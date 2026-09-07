# GITS 业务场景演示清单（P01–P44 全路由）

> 生成时间：2026-09-07 12:44 (UTC+8)
> 数据来源：**Playwright 真实浏览器遍历**（chromium，逐一访问 51 条路由并抓取控制台/网络失败），非人工推测
> 环境：后端 `localhost:8080`（H2 + 种子）· 前端 `localhost:5173`（vite dev，代理 /api → 8080）
> 演示用真实 ID：客户 `CUST-CORP-0003`（RM-001 张明远）· 旅程 `a1b2c3d4-…-0003` · 报告 `b1b2c3d4-…-0031`

## 总览

| 判定 | 数量 | 含义 |
|---|---|---|
| ✅ 有数据 | 9 | 页面渲染且抓到真实数据（卡片/长文本） |
| ⚠️ 渲染无数据 | 30 | 页面能开，但接口返回空或未装配数据 |
| ❌ 接口失败 | 12 | 存在 4xx 网络失败，数据未加载 |
| 合计 | 51 | 可渲染（HTTP 200 且正文>200字）49/51 |

## 失败根因（4 类，非 51 个独立问题）

- `/api/v1/engagement/claims` —— 后端缺口：全仓无 GET /claims 映射，前端 P04/P08/P09/P20/P21/P22/P37/P40 均调用它
- `/api/v1/engagement/kyc` —— 映射存在（KycInsightController）但运行期 404：controller 未装配，需排查条件装配/依赖
- `/api/v1/engagement/supply-chain-graph/reports` —— 需真实 requestId（先 POST /supply-chain-graph 创建）
- `/api/v1/product-recommendation-runs` —— 需真实 runId（先 POST 创建运行）
- `/api/v1/engagement/journey` —— 需 journeyId（非 customerId）；可 POST /journey/start 获取

## 逐页清单

| # | 页面 | 路径 | 判定 | 依赖接口 | 备注 |
|---|---|---|---|---|---|
| P01 | 我的客户经营 | `/workbench` | ⚠️ 渲染无数据（骨架/空态） | engagement |  |
| P02 | 客户对象主页 | `/accounts` | ✅ 有数据 | engagement |  |
| P03 | 客户分层与组合看板 | `/accounts/portfolio` | ⚠️ 渲染无数据（骨架/空态） | engagement |  |
| P04 | 客户记录·经营总览 | `/customers/CUST-CORP-0003` | ❌ 接口失败 | engagement | /api/v1/engagement/claims; /api/v1/engagement/kyc/{id}/gap-profile |
| P05 | 客户记录·集团关系 | `/customers/CUST-CORP-0003/group` | ⚠️ 渲染无数据（骨架/空态） | engagement |  |
| P06 | 客户记录·业务资金全景 | `/customers/CUST-CORP-0003/funds` | ⚠️ 渲染无数据（骨架/空态） | engagement |  |
| P07 | 客户记录·关系人情报 | `/customers/CUST-CORP-0003/parties` | ⚠️ 渲染无数据（骨架/空态） | engagement |  |
| P08 | 经营信号对象主页 | `/signals` | ❌ 接口失败 | engagement | /api/v1/engagement/claims; /api/v1/engagement/kyc/{id}/gap-profile |
| P09 | 经营信号记录 | `/signals/CUST-CORP-0003` | ❌ 接口失败 | engagement | /api/v1/engagement/claims; /api/v1/engagement/kyc/{id}/gap-profile |
| P10 | 互动对象主页 | `/engagements` | ✅ 有数据 | engagement |  |
| P11 | 互动记录·访前路径 | `/engagement` | ⚠️ 渲染无数据（骨架/空态） | engagement |  |
| P12 | 访前目标与信息缺口 | `/engagement/previsit/gaps` | ⚠️ 渲染无数据（骨架/空态） | - |  |
| P13 | 访前知识证据装配 | `/engagement/previsit/evidence` | ⚠️ 渲染无数据（骨架/空态） | - |  |
| P14 | 访前包预览 | `/engagement/previsit/pack` | ⚠️ 渲染无数据（骨架/空态） | - |  |
| P15 | 会中工作区 | `/in-meeting/CUST-CORP-0003?` | ✅ 有数据 | v11 |  |
| P16 | 会中实时捕获 | `/in-meeting/CUST-CORP-0003/capture` | ❌ 接口失败 | engagement,v11 | /api/v1/engagement/journey/{id} |
| P17 | 离场确认 | `/in-meeting/CUST-CORP-0003/checkout` | ⚠️ 渲染无数据（骨架/空态） | v11 |  |
| P18 | 访后事实对账 | `/engagement/postvisit` | ⚠️ 渲染无数据（骨架/空态） | engagement |  |
| P19 | CRM 受控回写 | `/engagement/crm-writeback` | ⚠️ 渲染无数据（骨架/空态） | v11 |  |
| P20 | 需求与机会对象主页 | `/needs` | ❌ 接口失败 | - | /api/v1/engagement/claims; /api/v1/engagement/kyc/{id}/gap-profile |
| P21 | 需求记录 | `/needs/CUST-CORP-0003` | ❌ 接口失败 | engagement | /api/v1/engagement/claims; /api/v1/engagement/kyc/{id}/gap-profile |
| P22 | 机会与服务计划记录 | `/needs/CUST-CORP-0003/plan` | ❌ 接口失败 | - | /api/v1/engagement/claims; /api/v1/engagement/kyc/{id}/gap-profile |
| P23 | 建议书对象主页 | `/proposals` | ⚠️ 渲染无数据（骨架/空态） | - |  |
| P24 | 新建建议书向导 | `/proposals/new` | ⚠️ 渲染无数据（骨架/空态） | engagement,v14 |  |
| P25 | 建议书记录 | `/proposals/CUST-CORP-0003` | ⚠️ 渲染无数据（骨架/空态） | - |  |
| P26 | 建议书模块编辑器 | `/proposals/CUST-CORP-0003/editor` | ⚠️ 渲染无数据（骨架/空态） | - |  |
| P27 | 需求—方案—产品映射 | `/proposals/CUST-CORP-0003/map` | ⚠️ 渲染无数据（骨架/空态） | - |  |
| P28 | AI 内容依据反查 | `/proposals/CUST-CORP-0003/evidence` | ⚠️ 渲染无数据（骨架/空态） | - |  |
| P29 | 内部版与客户版对照 | `/proposals/CUST-CORP-0003/project` | ⚠️ 渲染无数据（骨架/空态） | - |  |
| P30 | 版本比较与恢复 | `/proposals/CUST-CORP-0003/versions` | ⚠️ 渲染无数据（骨架/空态） | - |  |
| P31 | 专家协同记录 | `/collab` | ⚠️ 渲染无数据（骨架/空态） | - |  |
| P32 | 审批工作中心 | `/approvals` | ✅ 有数据 | v11 |  |
| P33 | 对客交付中心 | `/delivery` | ⚠️ 渲染无数据（骨架/空态） | - |  |
| P34 | 30/90/180 天账户计划 | `/account-plans` | ⚠️ 渲染无数据（骨架/空态） | - |  |
| P35 | 客户价值实现 | `/value` | ⚠️ 渲染无数据（骨架/空态） | - |  |
| P36 | 任务与承诺中心 | `/commitments` | ✅ 有数据 | v11 |  |
| P37 | Claim / Evidence 中心 | `/claims` | ❌ 接口失败 | engagement,v11 | /api/v1/engagement/claims |
| P38 | 知识卡与产品适用边界 | `/knowledge-map` | ⚠️ 渲染无数据（骨架/空态） | engagement |  |
| P39 | 审计与权限 | `/audit-trace` | ✅ 有数据 | v11 |  |
| P40 | 服务降级与异常恢复 | `/degrade` | ❌ 接口失败 | - | /api/v1/engagement/claims |
| P41 | 移动端·今日客户行动 | `/m/today` | ⚠️ 渲染无数据（骨架/空态） | - |  |
| P42 | 移动端·访前包 | `/m/previsit` | ⚠️ 渲染无数据（骨架/空态） | - |  |
| P43 | 移动端·会中速记 | `/m/notes` | ⚠️ 渲染无数据（骨架/空态） | - |  |
| P44 | 移动端·离场确认与任务 | `/m/checkout` | ⚠️ 渲染无数据（骨架/空态） | v11 |  |
| - | 登录 | `/login` | ⚠️ 渲染无数据（骨架/空态） | auth | 正文过短（可能为空态） |
| - | 产品解读·业务场景演示 | `/product-knowledge/interpretation` | ✅ 有数据 | productKnowledge |  |
| - | 供应链图谱分析报告 | `/supply-chain-report/b1b2c3d4-e5f6-7890-abcd-000000000031` | ❌ 接口失败 | engagement | /api/v1/engagement/supply-chain-graph/reports/{id} |
| - | 旅程时间线 | `/journeys/CUST-CORP-0003` | ❌ 接口失败 | engagement | /api/v1/engagement/journey/{id}; /api/v1/engagement/journey/{id}/repor |
| - | 报告详情 | `/reports/CUST-CORP-0003` | ✅ 有数据 | engagement |  |
| - | 产品推荐三段式工作区 | `/recommendation/b1b2c3d4-e5f6-7890-abcd-000000000031` | ❌ 接口失败 | productRecommendation | /api/v1/product-recommendation-runs/{id} |
| - | 外部事件监控 | `/external-events` | ✅ 有数据 | v11 |  |

## 主链路（建议演示顺序）

| 顺序 | 页面 | 路径 | 当前状态 |
|---|---|---|---|
| 1 | 我的客户经营 | `/workbench` | ⚠️ 渲染无数据（骨架/空态） |
| 2 | 客户对象主页 | `/accounts` | ✅ 有数据 |
| 3 | 客户记录·经营总览 | `/customers/CUST-CORP-0003` | ❌ 接口失败 |
| 4 | 互动记录·访前路径 | `/engagement` | ⚠️ 渲染无数据（骨架/空态） |
| 5 | 访前目标与信息缺口 | `/engagement/previsit/gaps` | ⚠️ 渲染无数据（骨架/空态） |
| 6 | 访前知识证据装配 | `/engagement/previsit/evidence` | ⚠️ 渲染无数据（骨架/空态） |
| 7 | 访前包预览 | `/engagement/previsit/pack` | ⚠️ 渲染无数据（骨架/空态） |
| 8 | 会中工作区 | `/in-meeting/CUST-CORP-0003?` | ✅ 有数据 |
| 9 | 会中实时捕获 | `/in-meeting/CUST-CORP-0003/capture` | ❌ 接口失败 |
| 10 | 离场确认 | `/in-meeting/CUST-CORP-0003/checkout` | ⚠️ 渲染无数据（骨架/空态） |
| 11 | 访后事实对账 | `/engagement/postvisit` | ⚠️ 渲染无数据（骨架/空态） |
| 12 | CRM 受控回写 | `/engagement/crm-writeback` | ⚠️ 渲染无数据（骨架/空态） |
| 13 | 需求与机会对象主页 | `/needs` | ❌ 接口失败 |
| 14 | 需求记录 | `/needs/CUST-CORP-0003` | ❌ 接口失败 |
| 15 | 机会与服务计划记录 | `/needs/CUST-CORP-0003/plan` | ❌ 接口失败 |
| 16 | 建议书对象主页 | `/proposals` | ⚠️ 渲染无数据（骨架/空态） |
| 17 | 建议书记录 | `/proposals/CUST-CORP-0003` | ⚠️ 渲染无数据（骨架/空态） |
| 18 | 建议书模块编辑器 | `/proposals/CUST-CORP-0003/editor` | ⚠️ 渲染无数据（骨架/空态） |
| 19 | 需求—方案—产品映射 | `/proposals/CUST-CORP-0003/map` | ⚠️ 渲染无数据（骨架/空态） |
| 20 | AI 内容依据反查 | `/proposals/CUST-CORP-0003/evidence` | ⚠️ 渲染无数据（骨架/空态） |
| 21 | 内部版与客户版对照 | `/proposals/CUST-CORP-0003/project` | ⚠️ 渲染无数据（骨架/空态） |
| 22 | 版本比较与恢复 | `/proposals/CUST-CORP-0003/versions` | ⚠️ 渲染无数据（骨架/空态） |
| 23 | 任务与承诺中心 | `/commitments` | ✅ 有数据 |
| 24 | Claim / Evidence 中心 | `/claims` | ❌ 接口失败 |
| 25 | 审计与权限 | `/audit-trace` | ✅ 有数据 |

## 前置操作（参数路由需真实 ID）

```bash
# 1) 取客户 ID
curl "http://localhost:8080/api/v1/engagement/customer?rmId=RM-001"
# 2) 取旅程 ID
curl "http://localhost:8080/api/v1/engagement/journey?customerId=CUST-CORP-0003"
# 3) 取报告 ID
curl "http://localhost:8080/api/v1/engagement/journey/<journeyId>/reports"
```

`/journeys/:id`、`/in-meeting/:id` 用**旅程 ID**；`/supply-chain-report/:requestId`、
`/recommendation/:runId` 需先 POST 创建后取 ID —— 这 3 类无法用静态 ID 遍历。
