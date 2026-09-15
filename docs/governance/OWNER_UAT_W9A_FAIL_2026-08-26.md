# Owner UAT｜W9-A 不通过

| 字段 | 值 |
|---|---|
| Decision ID | OD-GITS-BANK-UX-W9A-FAIL-2026-08-26 |
| Date | 2026-08-26 |
| Role | HUMAN_OWNER（人工测试） |
| Recorded by | Tech Lead |
| Result | **UAT_FAIL** |
| UAT_PASS | NO |
| FROZEN | NO |
| PRODUCTION_READY | NO |

## Owner 结论

人工测试不通过。左侧导航与 V3.2 设计图不相符；菜单逻辑混乱，像上一版本把阶段页塞进一级导航；配色与给定设计图不符。严重违背设计。

## 对照（权威：V3.2 设计系统 + 页面 01 PNG + `NAV_GROUPS`）

V3.2 一级导航只保留稳定对象域（业务阶段不得进入一级导航）：

| 分组 | 一级项 |
|---|---|
| 日常作业 | 客户经营作战台、我的任务与承诺 |
| 客户经营 | 客户组合、客户全景、信号与互动、需求与机会 |
| 方案与交付 | 服务建议书、专家协同、账户计划与价值 |
| 知识与治理 | 证据与知识、审批与审计 |

当时实现把访前路径、会中、CRM 写回、移动端 P41–P44 等全部挂在左侧，且 `theme.css` 仍用旧 SPDB 蓝 `#1a56db`，不是 `--gits-navy-900 #08233B` / `--gits-blue-600 #1976D2`。

## 处置

Experience Shell 按上表与 Token 返工。不改合同源。不签署 UAT_PASS。

## 返工状态（仍失败，待 Owner 复测）

工作区已按 V3.2 `NAV_GROUPS` 重做一级导航与 Token（11 个稳定对象域、四组、navy sider `#08233B`、选中条 `#48A7E8`）。访前/会中/写回/移动端不再进入一级导航。`UAT_PASS` 仍为 **NO**，须 Owner 刷新 `http://127.0.0.1:5173/workbench` 对照 01 图复测后才可改签署。

## 追加失败（2026-08-26｜信号与互动 / 互动对象）

人工测试：从「信号与互动」点选「互动对象」无法开始旅程，页面报 `Request failed with status code 500`。

| 项 | 事实 |
|---|---|
| 映射 | L1「信号与互动」= V3.2 稳定域 P08–P19，不是旧菜单「客户经营旅程」的改名 |
| 点选「互动对象」 | 进入 P10 `/engagements`（互动对象主页），调用既有合同 `GET /api/v1/interactions`（operationId=`listInteractions`） |
| 启动旅程 | 仍是 P11 `/engagement` 上的「启动旅程」→ `POST /api/v1/engagement/journey/start` |
| 500 根因 | OpenAPI 已登记该 GET；运行中的 API **没有** `/api/v1/interactions` 映射。Spring 记为 `NoResourceFoundException: No static resource api/v1/interactions.`，被全局处理成 HTTP 500 |
| 处置 | 先记失败。已实现该只读 GET（空列表返回 `[]`，不发明字段、不改合同源）。P08/P10 增加进入 P11 的入口。活环境 `GET /api/v1/interactions` 现为 200。不签署 UAT_PASS |

## 追加失败（2026-08-26｜客户经营旅程无法启动）

人工测试：要求从「信号与互动」进入客户经营旅程，但菜单落到经营信号列表；旅程页「启动旅程」在未选客户时不可见，点选螺旋节点只打开选择框，功能表现为不可用。

| 项 | 事实 |
|---|---|
| 域不是空壳 | P08 经营信号（客户上下文 opportunitySignals）、P10 互动列表（GET /api/v1/interactions）、P11 持续经营工作台（POST journey/start 等 C0）是三块既有能力；P12–P19 为访前/会中/访后/CRM 切片或 C2 禁用 |
| L1 入口 | V3.2 一级项仍叫「信号与互动」；本波按 Owner 要求默认进入 P11 经营旅程，域内页签切换信号/互动/旅程 |
| 启动失败 | `v-if="sc&&!jid"` 使启动按钮在未选客户时不出现；错误只进 toast |
| 处置 | 默认选客户、启动按钮常驻、页内错误、CORS 含 127.0.0.1:5173。live E2E 5/5 已绿。不签署 UAT_PASS，交 Owner 复测 |

## 追加失败（2026-08-26｜访前一键准备并非 DKWS；知识图谱/装配控制台缺失）

人工测试：进入互动记录·访前路径，确认「执行访前准备（一键）」数据是否来自请求 DKWS 知识工程服务。上一版可显示知识图谱与 DKWS 知识装配跟踪控制台；现服务不可达。Owner 要求盘点全部须与 DKWS 联动的功能，**禁止用本地假数据拼凑页面**。

Owner 纠正：把「企业集团关系图 / P38 知识地图」说成「不要和 DKWS 混为一谈的本地能力」是自说自话，违背「不得变更原有 DKWS」的约定。P05 与 P38 必须走原 DKWS Skill，禁止用 H2 股权种子或仓库知识快照填页。

| 项 | 失败时 | 纠正后 |
|---|---|---|
| 一键访前 | Mock LLM + 仓库快照 + H2 规则兜底 | `prepare-previsit` → DKWS Skill；失败空态，不本地补数 |
| P05 集团关系图谱 | `operating-view` 的 H2 `LegalEntity` / `OWNS` 边 | `bank-front-supply-chain-graph`；未返回则空态 |
| P38 知识地图 | GITS `GET /api/v1/knowledge/map` 仓库快照 | `GET /engagement/customer/{id}/knowledge-map` → `skill-customer-previsit-report`；产品适用并行 `bank-front-product-recommendation` |
| 装配跟踪 | 无 `assemblyTrace` | 访前页与 P38 展示 DSH 轨迹；未配置 DSH 时提示未收到轨迹 |

处置：先记失败。不签署 UAT_PASS。活环境未配 `DSH_BASE_URL` 时保持空态，待 Owner 提供可达 DKWS 后复测。

## 追加失败（2026-08-26｜一键访前浏览器 15s 超时，页面上看不到 DKWS）

人工测试：点「执行访前准备（一键）」看不到调用 DKWS 的迹象；DKWS 后台作业列表也查不到请求。

| 项 | 事实 |
|---|---|
| GITS 是否发了 HTTP | 是。8082 日志在点击后打出 `[SKILL-HTTP] execute` → `http://127.0.0.1:8106/api/skill/execute`（outreach / meeting / previsit / supply-chain-graph） |
| 为何页面像没调 | `frontend/src/api/engagement.ts` 默认 `timeout: 15000`。一键 `prepare-previsit` 当时**串行** 3 个同步 Skill，墙钟约 19s。浏览器 15s 断开 → `断开的管道`，结果写不回页面 |
| 为何 DKWS 作业列表可能为空 | 这 4 个 Skill 走**同步** `POST /api/skill/execute`（`async=false`），不创建 `/v1/jobs` 作业。作业台过滤 job 时会漏掉 |
| 未单独 POST 的 DKWS skill | `bank-front-eight-dimension` / `kyc-gap-check` / `fact-reconciliation` / `commitment-script` / `report-assembler` 原 GITS 一键就不直接调；由 `skill-customer-previsit-report` 在平台内取对应 KI |
| 处置 | 先记失败。Skill 调用超时改为 180s；一键三项并行；页内展示正在 POST 的 skillId。活验证：浏览器点一键 → prepare-previsit 200，页面出现 KI-009 与装配文案。不签署 UAT_PASS |
