# P37 适用 SIT 矩阵（executed vs PLANNED）

**Loop**: `P37-gits-bank-sit-gates`  
**Actor**: `feature_pilot`（implementation only）  
**Branch**: `feature/P30-gits-bank-experience-shell`  
**Baseline**: `d3142c9557aaa197c41ef89343ec1e05b073d0a0`

## 明确不声称

| 声明 | 本 Loop |
|---|---|
| 264 PASS | **否。不声称。** |
| 224 PASS（V3.2 目录合计） | **否。不声称。** |
| 44/44 完成 | **否。不声称。** |
| UAT_PASS | **否。未签署。** |
| QA_PASS | **否。仅 DEV_SELF_CHECK_PASS。** |
| FROZEN / PRODUCTION_READY | **否。** |

本文件记录的是 **已经实现的 P01–P44 降级/C0 页面上的工程用例**，不是 V3.2 正式 Need / G0–G5 真写 / AccountPlan / DeliveryPackage / 离线缓存 的验收。

V3.2 设计候选目录（`GITS_Bank_全量功能清单与测试验证用例_V3.2.md`）计划用例为 **176 页面级 + 48 端到端/契约/质量 = 224**。Dispatch/长程仍禁止声称 **264 PASS**。两者均未在本 Loop 宣称通过。

## 已执行（工程用例）

| 命令 | 范围 | EXIT | 官方证据 |
|---|---|---|---|
| `make generate` | 合同生成 | `0` | `evidence/contract_generate-20260825T174726Z.log` sha256 `048ab7c55cfbb3c6707b7212288bd84d678861d4abb19a7eca16fbb7a71803b8` |
| `make check` | 合同/语义/loop-guard/secret-scan | `0` | `evidence/contract_check-20260825T174729Z.log` sha256 `11fe4de0f4b8093cecbea794f4df21488ece06b1ab8d3d7cc962ee611b1175ed` |
| `make security-check` | secret-scan / permissions / oracle-readonly | `0` | `evidence/security_check-20260825T174732Z.log` sha256 `1c2e54ff47942adeb3070579d07769971cc013a065391befe99d643485d14736` |
| `cd frontend && npm ci && npm run check && npm run test && npm run e2e` | vue-tsc；vitest **54** 文件 / **291** 用例；Playwright **8** spec / **36** 用例 | `0` | `evidence/sit_applicable-20260825T174738Z.log` sha256 `a4c23e2c6fbb572804b4b4f4a79887b9e2d8e9739d4629cd95b7cd4dd292aa94` |

Playwright spec 文件：

- `frontend/e2e/experience-shell.spec.ts`
- `frontend/e2e/dashboard.spec.ts`（改写：P01 工作台，不再断言「客户经营概览」）
- `frontend/e2e/customer-detail.spec.ts`（改写：`/customers/:id`）
- `frontend/e2e/journey.spec.ts`（改写：`/journeys/:id`）
- `frontend/e2e/report.spec.ts`（改写：`/reports/:id`）
- `frontend/e2e/full-experience.spec.ts`（改写：已实现页 mock smoke，去掉「华东精工」与真后端 API 计数）
- `frontend/e2e/customer-manager-flow.spec.ts`（改写：访前/承诺/客户 mock smoke；C2 写保持禁用）
- `frontend/e2e/sit-applicable.spec.ts`（新增：`/workbench` `/commitments` `/proposals` `/approvals` `/m/today`）

共享 mock：`frontend/e2e/sit-fixtures.ts`（只拦截 pathname `/api/...`，不拦截 Vite `/src/api/`）。无 `it.skip` / `test.skip`。未把 C2 `DisabledAction` 改成可写。未改 `/commitments` 的 `pageId=P36`。

### 抽查覆盖的已实现页（mock API，不是 44/44）

| 路由 | pageId | 抽查内容 |
|---|---|---|
| `/workbench`、`/` | P01 | 壳层、行动队列、四态、确认型写禁用 |
| `/customers/:id` | P04 | 经营总览、KYC、信号、写禁用 |
| `/engagement` | P11 | 访前路径、螺旋文案、正式 Claim 写禁用 |
| `/commitments` | P36 | 承诺/任务列表、Need 派生写禁用 |
| `/proposals` | P23 | 空态 C2 壳、导入禁用 |
| `/approvals` | P32 | HumanGate 列表或错误态；不发明新门禁 |
| `/m/today` | P41 | 在线深链、离线队列禁用 |
| `/journeys/:id` | （既有旅程页） | 时间线 mock |
| `/reports/:id` | （既有报告页） | 占位报告渲染 |
| `/external-events` | （既有监控页） | mock 事件 |
| `/login` | 公开页 | 开发模式进入工作台 |

## 仍为 PLANNED（未在本 Loop 执行、不得记 PASS）

下列 V3.2 TC **保持 PLANNED**。原因：C3 对象未授权、真写未授权、无独立 QA/UAT 环境，或超出适用工程用例范围。

### 正式 Need / 机会真写（P20–P22）

- `TC-P20-01` … `TC-P20-04` 需求与机会对象主页：正式 Need 对象、主动作写回
- `TC-P21-01` … `TC-P21-04` 需求记录：正式 Need 记录与写
- `TC-P22-01` … `TC-P22-04` 机会与服务计划：正式服务计划写

本分支仅有非正式 Need（C2 降级）只读/禁用壳。页面级 vitest 存在，**不等于**上述 TC PASS。

### G0–G5 建议书真写（P23–P30）

- `TC-P23-01` … `TC-P30-04`：建议书工厂、阶段机晋级、模块提交、客户版投影、版本恢复等真写
- 含「保存并继续」「提交评审」「预览客户版」「运行完整性检查」等未授权写

本分支仅有非正式建议书 C2 壳。e2e 只断言空态与 DisabledAction。**不是** G0–G5 PASS。

### AccountPlan / DeliveryPackage / 价值口径（P33–P35）

- `TC-P33-01` … `TC-P33-04` 对客交付中心 / DeliveryPackage
- `TC-P34-01` … `TC-P34-04` 30/90/180 天账户计划 / AccountPlan
- `TC-P35-01` … `TC-P35-04` 客户价值实现正式口径

无合同对象。保持 PLANNED。

### 离线缓存 / 移动写回（P41–P44 与专项）

- `TC-P41-01` … `TC-P44-04` 中涉及离线队列、离线包、离线完成会谈、正式 Claim 速记的步骤
- `TC-E2E-04` 桌面访前包→发送移动→离线查看→撤权清除
- `TC-E2E-05` 会中移动速记→弱网暂存→桌面恢复
- `TC-QLT-14` 移动离线加密与清除

本分支无移动缓存/同步/离线包合同。e2e 只抽查在线只读与禁用写。

### 端到端正式闭环（未授权对象连续写）

- `TC-E2E-01` 信号→互动→访前→会中→访后→CRM 写回（完整正式证据链）
- `TC-E2E-02` 客户记录→Need→服务计划→建议书→专家→审批→交付
- `TC-E2E-03` 交付→30/90/180 天计划→价值复盘→新信号
- `TC-E2E-06` 建议书内部版→客户版投影→版本比较→恢复
- `TC-E2E-07` 证据中心双向反查正式 Finding
- `TC-E2E-08` 审批附条件通过→补件→重新检查→交付
- `TC-E2E-09` … `TC-E2E-12` 任务转派/分层提案/服务降级恢复等完整闭环

Playwright 抽查 **不是** 上述 E2E PASS。

### 契约/权限/质量专项（独立 QA / 联调环境）

- `TC-CTR-01` … `TC-CTR-12` 以 21 个 authority source 为输入的正式契约回归（本 Loop `AUTHORITY_SOURCE_CHANGE=NO`，不把前端 mock 当成契约 PASS）
- `TC-Pxx-02` 全页权限/字段级受限（无独立权限夹具）
- `TC-QLT-01` … `TC-QLT-24` 键盘/读屏/P95/跨浏览器/打印等（未在本 Loop 跑）

`make generate` / `make check` / `make security-check` 是仓库工程门禁，**不是** `TC-CTR-*` 全量 PASS。

### 其余已实现页的 V3.2 四条 TC

P01–P19、P31–P32、P36–P40 的 `TC-Pxx-01`…`04`（含权限、返回恢复、异常降级的正式证据包）**未**按 V3.2 步骤在独立 SIT 环境逐条执行。本 Loop 只跑了 vitest 组件用例与 Playwright mock smoke。这些 TC 仍为 **PLANNED**。

## 旧 e2e 处理

| 旧断言 | 处理 |
|---|---|
| `h1` =「客户经营概览」 | 改为 P01「首页·我的客户经营」 |
| `text=华东精工` | 改为 mock「测试企业A」；断言华东精工 count=0 |
| `/customer/:id` | 改为 `/customers/:id` |
| `/customer/:id/journeys` | 改为 `/journeys/:id` |
| `/report/:id` | 改为 `/reports/:id` |
| `page.request.get` 真后端 minCount | 删除；改为 UI mock |
| 把 C2 写按钮点成可写 | **未做** |
| `it.skip` / `test.skip` | **未使用** |

## 结论

适用工程用例（vue-tsc + vitest 54/291 + Playwright 8 spec / 36 tests）用于支撑 `sit_applicable`。  
**不是 264 PASS。不是 224 PASS。不是 44/44 完成。不是 UAT_PASS。**
