# UAT1-full-scenario-e2e 人工 UAT 交付包

生成时间：20260926T051447Z（UTC）
基线提交：70b14c23bb45f8d0b5ef305b375f2852338bcc85
用例总计：115 · 通过：115 · 未通过：0

## 判定口径

每个功能点都在真实浏览器（Playwright + Chromium）中验证**用户可见行为**：
不白屏、无未捕获异常、后端/KERT 接口无 5xx、真实数据路由无未预期 4xx、
无后端数据的页面必须显式降级标注（不得静默空白或伪造数据）。

### 环境就绪

- 状态：**pass** · 执行时间 2026-09-25T18:52:57.421169+00:00

### W0 全路由巡检

- 门禁状态：**pass** · 退出码 0 · 用例 59 · 证据 `loops/UAT1-full-scenario-e2e/evidence/w0_route_sweep-20260926T030302Z.log`

| 判定 | 功能点 | 耗时 |
|---|---|---|
| PASS | P01 经营总览 — 真实数据 | 1.8s |
| PASS | P36 我的任务 — 真实数据 | 1.8s |
| PASS | P45 经营旅程 — 真实数据 | 1.9s |
| PASS | P45-enter 进入经营旅程 — 真实数据 | 1.8s |
| PASS | P11 互动工作区 — 真实数据 | 1.8s |
| PASS | P02 客户组合 — 真实数据 | 1.8s |
| PASS | P03 客户分层与组合看板 — 真实数据 | 1.9s |
| PASS | P04 客户全景·经营总览 — 真实数据 | 1.9s |
| PASS | P05 客户档案·集团关系 — 真实数据 | 2.2s |
| PASS | P06 客户档案·业务资金 — 真实数据 | 1.9s |
| PASS | P07 客户档案·关系人 — 真实数据 | 1.8s |
| PASS | P08 经营信号 — 真实数据 | 1.9s |
| PASS | P09 经营信号记录 — 合成ID降级 | 1.9s |
| PASS | P10 互动对象主页 — 真实数据 | 1.9s |
| PASS | P20 需求与机会 — 真实数据 | 1.9s |
| PASS | P21 需求记录 — 合成ID降级 | 1.9s |
| PASS | P22 机会与服务计划 — 合成ID降级 | 1.9s |
| PASS | PC-01 企业金融产品中心 — 真实数据 | 4.9s |
| PASS | PC-02 产品中心·指定产品 — 合成ID降级 | 2.1s |
| PASS | P38 产品解读与知识 — 真实数据 | 2.1s |
| PASS | P38-map 知识卡与产品适用边界 — 真实数据 | 6.7s |
| PASS | REC-01 受控推荐工作区 — 合成ID降级 | 1.8s |
| PASS | SCG-01 供应链图谱报告 — 合成ID降级 | 2.1s |
| PASS | P23 建议书对象主页 — 真实数据 | 1.8s |
| PASS | P24 新建建议书向导 — 真实数据 | 1.8s |
| PASS | P25 建议书记录 — 合成ID降级 | 1.8s |
| PASS | P26 建议书模块编辑器 — 合成ID降级 | 1.8s |
| PASS | P27 需求—方案—产品映射 — 合成ID降级 | 1.9s |
| PASS | P28 AI 内容依据反查 — 合成ID降级 | 1.9s |
| PASS | P29 内部版与客户版对照 — 合成ID降级 | 1.8s |
| PASS | P30 版本比较与恢复 — 合成ID降级 | 1.9s |
| PASS | P31 专家协同记录 — 真实数据 | 1.8s |
| PASS | P32 审批工作中心 — 真实数据 | 1.8s |
| PASS | P34 账户计划 — 真实数据 | 1.8s |
| PASS | P33 对客交付中心 — 真实数据 | 1.8s |
| PASS | P35 客户价值实现 — 真实数据 | 1.8s |
| PASS | AN-01 经营指标分析 — 真实数据 | 2.0s |
| PASS | AN-02 细分客群分析 — 真实数据 | 2.0s |
| PASS | AN-03 组合条件查询分析 — 真实数据 | 1.9s |
| PASS | AN-04 指标监视器 — 真实数据 | 2.1s |
| PASS | P12 访前目标与信息缺口 — 真实数据 | 1.8s |
| PASS | P13 访前知识证据装配 — 真实数据 | 1.8s |
| PASS | P14 访前包预览 — 真实数据 | 1.8s |
| PASS | P15 会中工作区 — 真实数据 | 1.9s |
| PASS | P16 会中实时捕获 — 真实数据 | 1.9s |
| PASS | P17 离场确认 — 真实数据 | 1.8s |
| PASS | P18 访后事实对账 — 真实数据 | 1.8s |
| PASS | P19 CRM 受控回写 — 真实数据 | 1.8s |
| PASS | JT-01 旅程时间线 — 真实数据 | 6.9s |
| PASS | RP-01 报告详情 — 合成ID降级 | 1.9s |
| PASS | P37 Claim / Evidence 中心 — 真实数据 | 1.8s |
| PASS | P39 审计与权限 — 真实数据 | 1.8s |
| PASS | P40 服务降级与异常恢复 — 真实数据 | 1.8s |
| PASS | EV-01 外部事件监控 — 真实数据 | 1.8s |
| PASS | P41 移动端·今日客户行动 — 真实数据 | 1.8s |
| PASS | P42 移动端·访前包 — 真实数据 | 1.9s |
| PASS | P43 移动端·会中速记 — 真实数据 | 1.9s |
| PASS | P44 移动端·离场确认与任务 — 真实数据 | 1.8s |
| PASS | LG-01 登录页 — 真实数据 | 1.9s |

### W1 经营域

- 门禁状态：**pass** · 退出码 0 · 用例 5 · 证据 `loops/UAT1-full-scenario-e2e/evidence/w1_workspace_domain-20260926T030525Z.log`

| 判定 | 功能点 | 耗时 |
|---|---|---|
| PASS | P01 经营总览 — 交互与四态 | 1.8s |
| PASS | P36 我的任务 — 交互与四态 | 1.9s |
| PASS | P45 经营旅程 — 交互与四态 | 19.2s |
| PASS | P45 经营旅程列表 — 启动旅程必须产出真实 journeyId 并进入工作区 | 2.5s |
| PASS | P11 互动工作区 — 旅程上下文与访前入口 | 1.9s |

### W2 客户域

- 门禁状态：**pass** · 退出码 0 · 用例 7 · 证据 `loops/UAT1-full-scenario-e2e/evidence/w2_customer_domain-20260926T030554Z.log`

| 判定 | 功能点 | 耗时 |
|---|---|---|
| PASS | P02 客户组合 — 交互与四态 | 4.9s |
| PASS | P03 客户分层与组合看板 — 交互与四态 | 1.7s |
| PASS | P08 经营信号 — 交互与四态 | 7.7s |
| PASS | P10 互动对象主页 — 交互与四态 | 19.1s |
| PASS | P20 需求与机会 — 交互与四态 | 1.9s |
| PASS | P04 客户全景 — 三 Tab（集团关系/业务资金/关系人）逐个可达且带真实客户 | 7.1s |
| PASS | P02 客户组合 — 搜索框输入后列表必须响应（不得无变化） | 3.4s |

### W3 产品域

- 门禁状态：**pass** · 退出码 0 · 用例 4 · 证据 `loops/UAT1-full-scenario-e2e/evidence/w3_product_domain-20260926T030642Z.log`

| 判定 | 功能点 | 耗时 |
|---|---|---|
| PASS | PC-01 产品中心 — 目录、族、产品详情三段联动 | 2.2s |
| PASS | PC-01 产品中心 — 点击产品卡必须切换产品详情（URL 与首屏一致） | 4.1s |
| PASS | P38 产品解读与知识 / 知识地图 — 数据可渲染 | 8.1s |
| PASS | REC-01 受控推荐工作区 — 无效 runId 必须给出可读提示而非白屏 | 1.8s |

### W4 方案域

- 门禁状态：**pass** · 退出码 0 · 用例 9 · 证据 `loops/UAT1-full-scenario-e2e/evidence/w4_proposal_domain-20260926T030659Z.log`

| 判定 | 功能点 | 耗时 |
|---|---|---|
| PASS | P23 建议书对象主页 — 交互与降级诚实性 | 1.9s |
| PASS | P24 新建建议书向导 — 交互与降级诚实性 | 1.8s |
| PASS | P31 专家协同记录 — 交互与降级诚实性 | 1.7s |
| PASS | P32 审批工作中心 — 交互与降级诚实性 | 1.8s |
| PASS | P34 账户计划 — 交互与降级诚实性 | 1.8s |
| PASS | P33 对客交付中心 — 交互与降级诚实性 | 1.8s |
| PASS | P35 客户价值实现 — 交互与降级诚实性 | 1.8s |
| PASS | P24 建议书向导 — 逐步推进不得崩溃（降级态也要有可读说明） | 1.8s |
| PASS | P32 审批中心 — 审批动作须受控（不得静默放行） | 2.0s |

### W5 经营分析域（KERT）

- 门禁状态：**pass** · 退出码 0 · 用例 6 · 证据 `loops/UAT1-full-scenario-e2e/evidence/w5_analytics_domain-20260926T031214Z.log`

| 判定 | 功能点 | 耗时 |
|---|---|---|
| PASS | AN-01 经营指标分析 — KERT 数据渲染 | 3.6s |
| PASS | AN-02 细分客群分析 — KERT 数据渲染 | 3.6s |
| PASS | AN-03 组合条件查询分析 — KERT 数据渲染 | 3.4s |
| PASS | AN-04 指标监视器 — KERT 数据渲染 | 3.5s |
| PASS | AN-01 经营指标 — 切换维度/机构后数据区必须刷新 | 7.4s |
| PASS | SCG-01 供应链图谱报告 — 无效 requestId 须给出可读提示 | 2.1s |

### W6 旅程业务闭环

- 门禁状态：**pass** · 退出码 0 · 用例 4 · 证据 `loops/UAT1-full-scenario-e2e/evidence/w6_journey_closed_loop-20260926T030748Z.log`

| 判定 | 功能点 | 耗时 |
|---|---|---|
| PASS | 闭环 01｜互动工作区加载真实旅程 | 2.8s |
| PASS | 闭环 02｜访前缺口 → 证据装配 → 访前包 | 6.6s |
| PASS | 闭环 03｜会中工作区 → 实时捕获 → 离场确认 | 10.1s |
| PASS | 闭环 04｜访后对账 → CRM 受控回写 | 3.3s |

### W7 移动端与治理页

- 门禁状态：**pass** · 退出码 0 · 用例 9 · 证据 `loops/UAT1-full-scenario-e2e/evidence/w7_mobile_governance-20260926T030812Z.log`

| 判定 | 功能点 | 耗时 |
|---|---|---|
| PASS | P41 移动端·今日客户行动 — 窄屏可用 | 18.9s |
| PASS | P42 移动端·访前包 — 窄屏可用 | 4.5s |
| PASS | P43 移动端·会中速记 — 窄屏可用 | 4.5s |
| PASS | P44 移动端·离场确认与任务 — 窄屏可用 | 1.9s |
| PASS | P37 Claim / Evidence 中心 — 数据与交互 | 1.8s |
| PASS | P39 审计与权限 — 数据与交互 | 1.8s |
| PASS | P40 服务降级与异常恢复 — 数据与交互 | 1.9s |
| PASS | EV-01 外部事件监控 — 数据与交互 | 1.9s |
| PASS | JT-01 旅程时间线 — 真实 journeyId 可渲染时间线 | 6.2s |

### W8 错误路径与四态

- 门禁状态：**pass** · 退出码 0 · 用例 12 · 证据 `loops/UAT1-full-scenario-e2e/evidence/w8_error_paths-20260926T030856Z.log`

| 判定 | 功能点 | 耗时 |
|---|---|---|
| PASS | workbench｜后端 500 → 可读错误态（非白屏） | 4.6s |
| PASS | workbench｜空数据集 → 空状态占位（非崩溃） | 4.1s |
| PASS | workbench｜请求挂起 → 不得无限 spinner 且不得白屏 | 7.4s |
| PASS | workbench｜无效参数 400 → 提示而非白屏 | 4.0s |
| PASS | customer｜后端 500 → 可读错误态（非白屏） | 4.4s |
| PASS | customer｜空数据集 → 空状态占位（非崩溃） | 3.9s |
| PASS | customer｜请求挂起 → 不得无限 spinner 且不得白屏 | 7.4s |
| PASS | customer｜无效参数 400 → 提示而非白屏 | 3.9s |
| PASS | product-center｜后端 500 → 可读错误态（非白屏） | 4.5s |
| PASS | product-center｜空数据集 → 空状态占位（非崩溃） | 3.9s |
| PASS | product-center｜请求挂起 → 不得无限 spinner 且不得白屏 | 7.6s |
| PASS | product-center｜无效参数 400 → 提示而非白屏 | 3.9s |

## 结论

全部 115 个功能点用例通过，无人值守 E2E 迭代完成，**可提交人工 UAT**。

## 已修复缺陷（本轮）

- F-UAT1-01：KERT 经营分析全端点 503 —— 以 DuckDB 数据源重启 KERT 服务（环境/配置）
- F-UAT1-06：报告详情页伪造数据 + Loading 永不消失 —— 移除占位桩，改真实来源定位 + 显式降级（P0 红线）
- F-UAT1-07：会中捕获页用 journeyId 冒充 interactionId 查录音同意 —— 改为客户维度查询
- F-UAT1-10：前端存量单测 17 failed —— 修实现（navConfig 域映射死代码、侧栏缺 testid、loading 缺 testid） 并更新过时测试期望；批次 UAT2-component-test-drift 三门禁 PASS，440 用例 0 failed
- D-4：经营信号页跨页入口被在途改动删除，导致 P10 互动对象主页无 UI 入口（孤儿页） —— 恢复入口并补浏览器可达性用例；批次 UAT3-signal-nav-entry 三门禁 PASS + 变异复验闭环
