# 独立 QA 报告 · AN0-ccrm-analytics-landing

| 项 | 值 |
|---|---|
| Loop | AN0-ccrm-analytics-landing |
| QA 会话 | `qa-an0-001` |
| QA 角色 | `independent_qa`（未复用 TL 会话/结论，全部自行复跑取数） |
| 复核时间 | 2026-09-22T11:10Z ~ 11:25Z（19:10~19:25 +08:00） |
| 开工 HEAD | `4cdb52e78a987f584df9b28a899a40d538c47ea4`（br=`recover/PI-ARCH-product-catalog`，reflog 19:09:56 commit） |
| KERT HEAD | `/home/szf/dev/Leibniz-KERT` @ working-tree（交付未提交，哈希为准；收工时 HEAD=`456dfc7363a52d08c5b4d79f6868f381ea0b28ff`，br=`feature/m7-3-knowledge-map-route`） |
| **并发变更声明** | QA 窗口（19:10~19:25 +08:00）内**另一 PC8 会话在两仓持续提交**（GITS：19:17 `a3df7f5`、19:24 `5558fb4`，收工后 19:44 `56ce78e`；KERT：19:17/19:22/19:24/19:43/19:44）。本 QA 复核的 18 个冻结靶标（QA 包 §1.2）在**全部并发提交之后**做了 sha256 终检，**逐一与冻结值一致**（§4.5），故上述门禁与变异结论不受并发提交影响；PC8 范围内的文件不在本 Loop scope，未复核 |
| **QA 判定** | **FAIL（不得记 QA_PASS）** —— 6 道 implementation 门禁独立复跑全绿且 M1~M5 全部被捕获，但**目视复核发现 4 个分析屏趋势图整屏失效（后端 500）**，且门禁对该失效**结构性不可见**（假绿）。 |
| 报告哈希 | 本文件；证据目录 `evidence/qa-an0-001/`（sha256 清单见 §7） |

> 判定权说明：本报告只出 QA 判定，**不代签 Owner 签收**；Baton 按派工交回 `owner_review`，
> 并在 `STATE.json` 写明「修复前不得签收」。

---

## 1. 复现前置：QA 自建（不复用 TL 会话状态）

先停掉 TL 残留进程（KERT pid=456243 持有 DuckDB 读锁；vite pid=466085/466097），确认 8107/5173 端口空置后自建：

| 步 | 命令 | 结果 |
|---|---|---|
| 1 停服务释放库锁 | `kill -TERM 456243 466085 466096 466097` | 端口 8107/5173 已释放（`ss -lntp` 空） |
| 2 建 DuckDB | `cd Leibniz-KERT && python3 scripts/build_analytics_duckdb.py` | exit=0；`dim_org:6 dim_industry:8 dim_credit_rating:6 cfg_metric_banding:7 cfg_analytics_param:5 cbdm_cust_biz_wide:7200 cbdm_analysis_wide:3816` |
| 3 起 KERT 8107 | `KERT_ANALYTICS_DUCKDB=$PWD/examples/bank-front-analytics/cb_analytics.duckdb python3 scripts/serve_analytics_api.py` | pid=540127；`/v1/analytics/params` HTTP=200 |
| 4 起 vite 5173 | `cd frontend && npx vite --host 127.0.0.1 --port 5173` | `vite_http=200` |
| 5 打通代理 | `curl http://127.0.0.1:5173/kert-api/v1/analytics/params` | HTTP=200，body 为 KERT 信封（真实链路，无 mock） |

**独立复核造数口径**（不走构建脚本自报，直连库取数，read_only）：

```
duckdb(ro): SELECT COUNT(*) FROM cbdm_cust_biz_wide   -> 7200
             SELECT COUNT(*) FROM cbdm_analysis_wide  -> 3816
             SELECT * FROM cfg_analytics_param         -> 5 行
```
与交接声明（DWD 7200 / DWS 3816 / 参数 5 行）一致。

---

## 2. Q1 —— 6 道门禁独立复跑（按 LOOP.yaml `gates[].command` 原样）

| # | 门禁 | 命令（原样） | QA 退出码 | QA 证据 |
|---|---|---|---|---|
| G1 | kert_analytics_unit | `cd ../Leibniz-KERT && python3 -m pytest tests/unit/test_operational_analytics.py -q` | **0** | `gates/g1_kert_analytics_unit.log` |
| G2 | kert_analytics_integration | `cd ../Leibniz-KERT && python3 -m pytest tests/integration/test_analytics_api.py -q` | **0** | `gates/g2_kert_analytics_integration.log` |
| G3 | frontend_typecheck | `cd frontend && npx vue-tsc --noEmit` | **0** | `gates/g3_frontend_typecheck.log`（0 字节） |
| G4 | frontend_analytics_unit | `cd frontend && npx vitest run src/views/__tests__/AnalyticsViews.spec.ts src/components/shell/__tests__/AppSidebar.spec.ts` | **0** | `gates/g4_frontend_analytics_unit.log`（2 files / 9 tests passed） |
| G5 | e2e_analytics | `cd frontend && npx playwright test e2e/analytics.spec.ts` | **0** | `gates/g5_e2e_analytics.log`（5 passed） |
| G6 | analytics_params_failclosed | `cd ../Leibniz-KERT && python3 -m pytest tests/unit/test_operational_analytics.py -q -k Params` | **0** | `gates/g6_analytics_params_failclosed.log` |

用例数独立核对（`--collect-only`）：单元文件 25 例、`-k Params` 6 例、集成文件 14 例 —— 与日志点数一致。
（日志无 `N passed` 汇总行：`addopts=["-q","-m","not perf"]` + 命令再带 `-q` ⇒ 等效 `-qq` 抑制汇总；**退出码是唯一通过信号**，本报告据此判定。）

**Q1 = PASS。**

---

## 3. Q2 —— 证据 sha256 比对（QA 包 §1.1）

| 门禁 | QA 包 §1.1 | QA 自跑实测 | 判定 |
|---|---|---|---|
| kert_analytics_unit | `c6ce8518…e797` | `c6ce8518a2cc113cc5560b3731e234ed6d559e746221ae903ce01599dfe7e797` | **逐字节一致** |
| kert_analytics_integration | `0db356ee…3ab9` | `0db356ee91ac6f4323f5e9f7af3f60f50ef236bb0f748f141783308a103c3ab9` | **逐字节一致** |
| frontend_typecheck | `e3b0c442…b855` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | **逐字节一致**（空文件） |
| frontend_analytics_unit | `3a9e053d…7bff` | `941e2914231528977dd4bdf4c9341ae5db42cbb14bc21023bd40f6a4c4bb65db` | 不同（**含耗时行**，见下） |
| e2e_analytics | `2874593a…dce8` | `a2269bd3c868e5fbd8785ce9b31a86c0fd4b47a4d840b675833b745a56d86d49` | 不同（**含耗时行**） |
| analytics_params_failclosed | `700bc032…ae24` | `700bc0322b00f8e8db3ce495047983b54ab27ab59ed1fedac05f3aeba47dae24` | **逐字节一致** |

差异原因已核实：pytest 日志只含进度点（无时间戳）⇒ 4/6 门禁证据哈希**可逐字节复现**；vitest/playwright 日志含 `Duration/时间` 行 ⇒ 哈希随轮次变化，属预期，**不构成证据失真**（判定以退出码 + 用例计数为准）。

补充：实现靶标 sha256 亦全部与 §1.2 一致（KERT 7 文件 + GITS 11 文件，逐一 `sha256sum` 复核通过）。

**Q2 = PASS（含说明）。**

---

## 4. Q3 —— 变异复验（反证断言非空转）

仓库纪律遵守方式：**库类变异用副本**（`/tmp/qa_an0/m1.duckdb`、`m2.duckdb` + 独立端口 8109/8110），**源码类变异即改即还原并校验 sha256**。所有变异靶标复核后 sha256 与 QA 包 §1.2 完全一致（§4.5）。

| 变异 | 操作 | 期望 | 实测 | 判定 |
|---|---|---|---|---|
| **M1** | 副本库 `cfg_analytics_param.alert_threshold` → `9.9`，服务 8109 | `monitor-*` 的 `alerts` 变空 | 8109：`threshold=9.9`，`alerts=[]`（count=0）；对照 8107（0.15）：`alerts_count=5` | **被捕获** |
| **M2** | 副本库 `profit_source` → `FTP`（数据无 FTP 列），服务 8110 | `/metrics` 必须 400 | 8110：`/metrics` **400** `INVALID_REQUEST`「profit_source=FTP 但数据表缺少 FTP 利润列 ['profit_dep_ftp','profit_loan_ftp','profit_fee_ftp']（fail-closed…）」；`/trend` 同 400；不涉利润口径的 `/periods` 仍 200（非全局瘫痪）；对照 8107 同请求 200 | **被捕获** |
| **M3** | 临时删除 `combo_query` 的 metric/op 白名单校验 | 注入用例必须变红 | G1 原样复跑 **exit=1**（`TestComboQuery::test_metric_whitelist_fail_closed` + `test_operator_whitelist_fail_closed` FAILED）；G2 原样复跑 **exit=1**（`test_combo_query_whitelist_4xx` FAILED）；期间 `evil` 真达 SQL 层（`BinderException` / `KeyError: 'evil'`）⇒ 证明白名单确为唯一拦截点。还原后 G1/G2 **exit=0** | **被捕获** |
| **M4a** | 向 `src/api/analytics.ts` 注入类型错误 | `vue-tsc` 必须非 0 | **exit=2**，`src/api/analytics.ts(343,7): error TS2322: Type 'string' is not assignable to type 'number'` ⇒ 空日志非假绿 | **被捕获** |
| **M4b** | 向 `e2e/analytics.spec.ts` 注入同样类型错误 | —（清单只要求 M4「任一 .ts」） | **exit=0，日志 0 字节** ⇒ e2e 文件**未**被 typecheck 覆盖（见 F-AN0-QA-04） | **暴露覆盖面缺口** |
| **M5** | `AppSidebar.isActive` 改回按 domain 判定（同域整组同亮） | 「仅 1 项高亮」断言必须变红 | E2E 层：`toHaveCount(1)` 失败，`Received: 4`（`nav-group-analytics .nav-item.active` 14 次解析为 4）⇒ 测试 FAILED，其余 4 例仍 passed；还原后 E2E **5 passed**。**单测层同一变异下 6/6 仍绿**（该断言不在 `AppSidebar.spec.ts` 内） | **E2E 层被捕获**（覆盖层提示见 §6-F4） |

M1~M5 全部被捕获 ⇒ **门禁断言非空转**。
M4b/M5 两点附带结论同时说明：**「类型检查」与「高亮断言」的实际覆盖面小于 `LOOP.yaml`/QA 包的文字声明**。

### 4.5 变异后仓库洁净性

| 靶标 | 变异前（=§1.2 冻结值） | 变异后还原值 | 结论 |
|---|---|---|---|
| KERT `operational_analytics.py` | `ecb5235f…a966` | `ecb5235fe35646c4c69040e1611f6cc6044bce077c46ec29aeccde45abe3a966` | 一致 |
| GITS `src/api/analytics.ts` | `c917c7cd…9e55` | `c917c7cd6ff213c371a93798a92863b72dbb728e9a441c2ba5ee39f2b7519e55` | 一致 |
| GITS `e2e/analytics.spec.ts` | `796af68c…81bf` | `796af68cbf9ca8b2d47adbc3e72ca3105e5f69c0c9bb011a4e2c9f32ac3281bf` | 一致 |
| GITS `AppSidebar.vue` | `1c3240f0…8263` | `1c3240f0be040bb2e357f9ddbe5e368ffa2eb8021ded57bfa6e35f58157d8263` | 一致 |

`git status` 未见 QA 引入的任何新增/改动（`frontend/test-results/` 已被 `.gitignore:37` 忽略）。变异库副本、探针脚本、日志全部落在 `/tmp/qa_an0/` 与 `evidence/qa-an0-001/`，**未污染仓库源码**。

**Q3 = PASS。**

---

## 5. Q4~Q12 逐条判定

### Q4 口径一致（`/params` = `metrics.meta.params` = `cfg_analytics_param`）—— **PASS**

| 来源 | 值 |
|---|---|
| `GET /v1/analytics/params` | `{alert_threshold:0.15, roe_leverage:12.5, roa_annualize_months:12.0, inactive_months:3.0, profit_source:"DERIVED"}` |
| `GET /v1/analytics/metrics?screen=operating-overview…` 的 `meta.params` | `{alertThreshold:0.15, roeLeverage:12.5, roaAnnualizeMonths:12.0, inactiveMonths:3.0, profitSource:"DERIVED"}` |
| 直连库 `cfg_analytics_param`（5 行） | `alert_threshold=0.15 / roe_leverage=12.5 / roa_annualize_months=12 / inactive_months=3 / profit_source=DERIVED` |

三源一致；`meta.rowCount(4) == len(rows)`，`meta` 随响应返回（`data.pop("meta")` 后置入第三参，行为与观测一致）。

### Q5 FTP fail-closed（无 FTP 列 ⇒ 400 具名拒绝，不静默降级）—— **PASS**

见 M2：400 + 具名 message 明确列出缺失列与 fail-closed 语义；`/periods` 不受影响 ⇒ 未把整服务打挂、未降级回 DERIVED。
另：单元 `test_ftp_profit_source_fail_closed` 同时断言「异常后恢复 DERIVED 仍出数」，正负断言齐备。

### Q6 未配置即隔离（未设 `KERT_ANALYTICS_DUCKDB` ⇒ 503 + 4 SKILL 不注册）—— **PASS**

QA 自研脚本 `probes/q6_unconfigured_isolation.log`（**不复用 TL 测试**）：

- 未配置：`/v1/analytics/screens` **503** `ANALYTICS_UNAVAILABLE`；`analytics_service is None`；**7 个 GET 端点逐一 503**；分析 Skill 零泄漏；
- 已配置：同端点 **200**；注册表 `added=[bank-front-combo-query, bank-front-customer-segment, bank-front-metrics-monitor, bank-front-operating-metrics]`（恰 4 个），`removed=[]`（纯增）；
- 注册表规模 13 → 17；
- **手工起服复核**（真实进程 8108，无该环境变量）：`/v1/analytics/screens` 503 同一 code；活跃注册表 `8107 n=17 / 8108 n=13`，`新增=[4 个分析 Skill]`、`缺失=[]`。

### Q7 组合查询注入面（白名单外 ⇒ 400，SQL 不被拼接执行）—— **PASS**

| 请求 | 结果 |
|---|---|
| `metric="evil; DROP TABLE cbdm_cust_biz_wide"` | **400** `INVALID_REQUEST: amountRules.metric 非法: evil; DROP TABLE cbdm_cust_biz_wide` |
| `op="LIKE"` | **400** `amountRules.op 非法: LIKE` |
| `value=true`（bool 冒充数值） | **400** `amountRules.value 非法` |
| 注入后直连库复核 | `cbdm_cust_biz_wide rows=7200`（表未被破坏） |

### Q8 并发正确性（≥12 路并发混合请求 0 个 5xx/400）—— **PASS**

QA 自研探针（真实 HTTP，非 TestClient）`probes/q8_concurrency.log`：**16 并发 × 7 轮 = 112 请求**
→ `HTTP 码分布={200:112}`、`200 且信封 status=OK: 112/112`、`异常 0 条`。
端点覆盖（8 类）：dimensions 7 / orgs 7 / periods 7 / screens 7 / params 7 / metrics 14 / trend 7 / **POST combo-query 56**。

### Q9 菜单与页面内导航符合 Owner 口径 —— **PASS（口径）／见 §6 附带缺陷**

QA 自研浏览器探针（`probes/qa_visual_result.json`，34 项全 PASS）+ 4 张全页截图（`evidence/an0-ccrm-analytics-qa/shots/`，因 `loop_guard` 对 Loop 目录做 UTF-8 全目录扫描，二进制不入 Loop 目录，见 F7）：

| 口径项 | 实测 |
|---|---|
| 一级「经营分析」+ 4 二级 | `nav-group-analytics` 按钮数=4；标签依次为 经营指标分析/细分客群分析/组合查询工具/指标监视器 |
| 三个分析页**左侧**页面内导航 | 几何证据：`nav.x=250, nav.right=446 < panel.x=460`；项数 4/2(+4 子项)/3，均**仅 1 项激活** |
| 组合查询为**直挂页** | `/analytics/combo-query` 的 `analytics-page-nav` count=0（无页面内导航），直接呈现查询表单 |
| 无「产品分析器」 | 侧栏文本逐页检查通过；`grep -rn 产品分析器 src/ e2e/` 仅命中注释与负例断言，无菜单项 |
| 切换图表可用 | 点击「风险指标分析」⇒ `analytics-panel-operating-risk` 可见且 `operating-customer` 移除；「结算量业务」⇒ 表格含「借贷累加/行业名称」；监视器点行 ⇒ 趋势图切成员 |

> 附带：同一目视复核暴露 4 个分析屏趋势图失效（§6-F1/F2/F3），该失效**不在本清单口径项内**，但属本 Loop 交付的用户可见功能。

### Q10 同域多菜单激活不整组同亮（任一分析页仅 1 项高亮）—— **PASS**

4 个页面 × 静态进入 + 依次点击 4 个菜单项（8 次采样）：`nav-group-analytics .nav-item.active` **恒为 1**，且标签与点击项一致。M5 反证：改回按 domain 判定 ⇒ E2E 断言 `Received: 4` 变红。

### Q11 认证旁路为 Owner 决策（不恢复）—— **PASS**

- 代码：`router/index.ts:352-358` 注释明确「Owner 决策 2026-09-22：**不恢复认证**」，`SKIP_AUTH=true` 且守卫 `if (SKIP_AUTH) { next(); return }` 位于 `isAuthenticated()` 之前；
- 浏览器（**全新 context，localStorage 空**）深链直开 `/analytics/operating-metrics|segments|monitors|combo-query`：URL 未被改写、**无跳登录页**、面板正常渲染；
- 全程 **0 个请求带 `X-API-KEY`**（`page.on('request')` 逐条检查），localStorage 无 `gits_api_key`；
- 反向证据（旁路生效）：页面附带 `/api/v1/commitments` 返回 **401**，页面**未**跳登录页，仅侧栏徽标静默为 0 ⇒ 与「401 不跳登录页」决策一致。
  （该 401 属既有全局行为与既有 GITS 后端鉴权，非本 Loop 引入；QA 未改动。）

### Q12 Owner 五项决策落地 —— **4 项 PASS，1 项部分不落地（FAIL）**

| # | 决策（STATE.json.owner_decisions） | 实测 | 判定 |
|---|---|---|---|
| ① | 不恢复认证（SKIP_AUTH=true 永久保留，注释已按决策改写） | 见 Q11；注释含 Owner 决策字样 | **PASS** |
| ② | 生产口径替换：FTP 利润 / 真实 ROE 分母 / 不动户参数 N / 告警阈值参数化 | 告警阈值：`_alerts` 真引用（M1 反证通过）；FTP：`_profit_total`+`_ftp_columns` 真引用且 fail-closed（M2 通过）；`roa_annualize_months`/`roe_leverage`：`_derive` 真引用；**`inactive_months` 全仓仅出现在默认值表与对外 meta，无任何计算引用**（`custCntInactive = SUM(w.inactive_flag)` 直用造数标志位）⇒「不动户参数 N 参数化」不成立；「真实 ROE 分母」仍为 `ROE=ROA×12.5` 近似（代码自注「真实资本口径接入前近似」），NEXT_SESSION 已声明为待接入（按已声明待办处理，不计 FAIL） | **部分 PASS**（见 F5） |
| ③ | V3.2 UX 权威源同步登记 | 本仓交付 `docs/dispatch/CCRM-经营分析菜单登记-V1.0.md`（含菜单结构表、页面内导航映射、重排说明、§3 明确外部 `generate_gits_bank_ux_v32.py` 不在本仓且同步为待办、责任人待 Owner 指派） | **PASS（本仓侧）**；外部权威源不可验（见 §7 未验证项） |
| ④ | KERT systemd 样例补 `KERT_ANALYTICS_DUCKDB` | `deploy/systemd/kert-api.service`：`Environment=KERT_ANALYTICS_DUCKDB=/var/lib/kert/cb_analytics.duckdb` + 注释说明 503/fail-closed 语义与 `/var/lib/kert` 可写；`deploy/.env.example`：同名说明条目（注释态） | **PASS** |
| ⑤ | 本批作为 Loop 补登记 | `loops/AN0-ccrm-analytics-landing/`（LOOP.yaml/STATE.json/EVIDENCE.json/EVIDENCE.md/FAILURES.md/HANDOFF.md/memory）齐备 | **PASS** |

---

## 6. 补充发现（QA 目视/探针新增，清单外）

| ID | 等级 | 发现 | 证据 |
|---|---|---|---|
| **F1** | MAJOR | **`GET /v1/analytics/trend` + `dim=ORG` ⇒ HTTP 500**。`_series_agg` 用 `self._dim_expr(dim)`，`ORG` 返回 `o.org_name`，但该 SQL **未 JOIN `dim_org`**（`_aggregate` 有 JOIN，两处不对称）⇒ `BinderException: Referenced table "o" not found!` | `probes/qa_trend_500_repro.log`；`probes/kert_8107_service_console.log`（服务端根因）。复现：`/trend?screen=operating-customer&dim=ORG&dimValue=泉州分行&orgId=350000&metric=custCnt&months=12` → 500 |
| **F2** | MAJOR | **`/trend` 在无匹配成员（或该成员无期间数据）时 ⇒ HTTP 500**，而非空点列或 400。`trend()` 对空 `sums` 调用 `_derive({})` ⇒ `profit=None` ⇒ `roa = profit * months / assets` ⇒ `TypeError: unsupported operand type(s) for *: 'NoneType' and 'float'` | 同一日志；复现：`/trend?screen=monitor-ldr&dim=INDUSTRY&dimValue=NOT_EXIST&orgId=350000&metric=ldr&months=6` → 500（同 screen 传真实成员 制造业 → 200） |
| **F3** | MAJOR | **用户可见后果：4 个「经营指标分析」屏趋势图整屏失效。** 视图层对 ORG 轴屏把「分布维度」当 trend 的 dim 传（默认 `INDUSTRY`）而 `dimValue` 传机构名 ⇒ 命中 F2 ⇒ 500；前端 `loadTrend()` **catch 后把 points 置空静默吞掉 500**，界面显示「**趋势数据不足（至少 2 期）**」，而库中实有 24 期。目视截图与逐屏探针：经营指标分析 4/4 屏显示「趋势数据不足」，细分客群 5 屏 + 指标监视器 3 屏 trend 均 200 正常 | `evidence/an0-ccrm-analytics-qa/shots/operating-metrics.png`（显示"趋势数据不足"）vs `.../monitors.png`、`.../segments.png`（曲线有数据）；`probes/qa_trend_scope.log`（4 处"趋势数据不足"、3 条 500、6 条 200） |
| **F4** | MINOR | **门禁文字声明与实际覆盖面不符（over-claim）**：`LOOP.yaml` 的 `frontend_typecheck.pass_condition` 写「退出码 0（**含 e2e 文件的类型检查**）」，但 `frontend/tsconfig.json` 的 `include=["src/**/*.ts","src/**/*.vue","vite.config.ts"]` **不含 `e2e/**`**；实测向 `e2e/analytics.spec.ts` 注入类型错误后 `vue-tsc` **exit=0、日志 0 字节** ⇒ e2e 类型错误无任何门禁可拦。另：`frontend_analytics_unit` 的单测内**没有**「仅 1 项高亮」断言，该断言只在 E2E 中（QA 包 §3.1 M5 未指明层级） | `mutations/m4b_e2e_typecheck_green.log`（exit=0）；`mutations/m5_unit_green.log`（变异下单测仍 6/6 绿）；`grep` tsconfig/package.json 无第二 tsconfig、无覆盖 e2e 的 typecheck 脚本 |
| **F5** | MAJOR | **「不动户参数 N」未接线即宣称参数化**：`inactive_months` 仅存在于 `_DEFAULT_PARAMS`、`meta.params.inactiveMonths`、种子 CSV；**无任何计算引用**（`grep -rn inactive_months src/` 3 处，全是声明/输出）。而 STATE.json 决策② 与 EVIDENCE.md 均宣称「口径参数化已落地」。参数存在但改它不影响任何指标 ⇒ 属「旋钮摆设」，与 M1/M2 已证真接线的告警阈值/FTP 形成对照 | `grep` 输出（见 §5-Q12 表）；`mutations/m1_alert_threshold.log`（阈值真接线反证） |
| **F6** | MINOR | 端点计数文案不一致：`docs/dispatch/CCRM-经营分析菜单登记-V1.0.md` 写「`/v1/analytics/*`（7 端点）」，`LOOP.yaml` deliverables 写「8 端点」。实测 **7 GET + 1 POST = 8**（`grep '@app.\(get\|post\)("/v1/analytics'`）。仅文案，无功能影响 | `grep` 输出 |
| **F7** | MINOR（工具） | **`loop_guard` 不允许 Loop 目录内存在二进制证据**：`reject_placeholders()` 对 `loop.rglob("*")` 的**每个文件**执行 `read_text(encoding="utf-8")`，任一 PNG/JPG 即抛 `UnicodeDecodeError` ⇒ `make memory-check/evidence-check` 直接 FAIL。QA 首次把 4 张截图放在 `evidence/qa-an0-001/shots/` 即命中该限制，遂改为落在 Loop 目录外的 `evidence/an0-ccrm-analytics-qa/shots/`（未改工具）。全仓既有 Loop 目录**无**二进制文件，属首次触发；建议后续「截图/视频类证据」约定放 Loop 外或给 `reject_placeholders` 加二进制跳过（本报告未改工具，供 TL/Owner 决策） | 复现：`make memory-check LOOP=AN0-ccrm-analytics-landing` → `loop-guard: FAIL: 'utf-8' codec can't decode byte 0x89 in position 0`（截图在 Loop 内时）；`scripts/loop_guard.py:88-96` |

**F1~F3 为何 6 道门禁全绿（假绿结构）**：E2E 对趋势图只断言 `analytics-trend-chart` 容器含静态标题「12个月趋势」——该标题在**无数据时同样渲染**（数据为空时容器内追加「趋势数据不足（至少 2 期）」），故 500 不改变断言结果；加上前端主动静默吞错，链路两层都无失败信号。**只跑一次全绿会错误放行 4 个屏的功能失效。**

---

## 7. 未验证项（环境缺失或超出本 Loop 可验范围，不以推定代替）

1. **生产/部署态未验**：本机无 systemd/prod profile，`deploy/systemd/kert-api.service`（8106、User=kert、`ReadWritePaths=/var/lib/kert`、`/opt/kert` 路径）与 `.env.example` 仅做静态核对，**未真机安装启动**；`KERT_ANALYTICS_DUCKDB` 指向 `/var/lib/kert/…` 的可写性与服务账号权限未实测。
2. **认证开启态未验**：Owner 决策不恢复认证，本环境认证默认关闭（无 `KERT_AUTH_*`）。**KERT 开启 API Key 时 `/v1/analytics/*` 的鉴权/作用域行为未验证**。
3. **生产网关同路径未验**：仅验证 dev vite 代理 `/kert-api` → 8107；生产同路径代理/网关（含超时、CORS、限流）未验证。
4. **真实 FTP 口径正确性未验**：数据表无 FTP 列，只能验证 fail-closed 行为；接入真实 FTP 利润列后的数值口径正确性未验证。
5. **不动户 N 的判定逻辑未验**：无判定实现可验（见 F5），造数侧标志位与业务口径"3 个月不动"的关系未验证。
6. **外部 UX 权威源未验**：`generate_gits_bank_ux_v32.py` 的 `NAV_GROUPS` 不在本仓（全仓 0 命中），「经营分析」组在外部权威源的同步登记**不可验**，只能确认本仓登记表存在。
7. **浏览器矩阵未验**：仅 Chromium（`playwright.config.ts` 默认），Firefox/WebKit 未跑。
8. **规模/性能未验**：仅 7200 行造数；未做大数据量、慢查询、DuckDB 内存/并发上限压测（Q8 仅 16 并发 112 请求）。
9. **错误信封一致性未验（非本 Loop 范围）**：KERT 5xx 返回 `{"requestId":…,"status":"skill_error","errors":[{"code":"INTERNAL_ERROR"}]}`，与 GITS 后端统一错误结构（`status/error/message/path/timestamp`）不同；属 KERT 平台自有约定，本 Loop 未改、未验其与 GITS 约定的对齐。
10. **`/api/v1/commitments` 401 的成因未验**：属既有全局行为（8080 存量后端鉴权），本 Loop 未涉及，仅作为「401 不跳登录」的反向证据记录。

---

## 8. QA 证据 sha256 清单（`evidence/qa-an0-001/`）

```
gates/g1_kert_analytics_unit.log                 c6ce8518a2cc113cc5560b3731e234ed6d559e746221ae903ce01599dfe7e797
gates/g2_kert_analytics_integration.log          0db356ee91ac6f4323f5e9f7af3f60f50ef236bb0f748f141783308a103c3ab9
gates/g3_frontend_typecheck.log                  e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
gates/g4_frontend_analytics_unit.log             941e2914231528977dd4bdf4c9341ae5db42cbb14bc21023bd40f6a4c4bb65db
gates/g5_e2e_analytics.log                       a2269bd3c868e5fbd8785ce9b31a86c0fd4b47a4d840b675833b745a56d86d49
gates/g6_analytics_params_failclosed.log         700bc0322b00f8e8db3ce495047983b54ab27ab59ed1fedac05f3aeba47dae24
mutations/m1_alert_threshold.log                 156e02f95934be5107b7425d68a6fe252404929e1364fd9541662a94b47ff87e
mutations/m2_profit_source_ftp.log               5c728c23d3d49c5b95aeea71d83f1975d9ce0107a6d4307272cb4d558bb84f33
mutations/m3_unit_red.log                        fa96189dcb6111dcdb454d027b2b596e250c25302fdf9b29270294cfe5f56f37
mutations/m3_integration_red.log                 069fef566b33cbfce7bb525286c7e87579844d1b62f659977408d7f6f84b1850
mutations/m3_restored_unit_green.log             c6ce8518a2cc113cc5560b3731e234ed6d559e746221ae903ce01599dfe7e797
mutations/m3_restored_integration_green.log      0db356ee91ac6f4323f5e9f7af3f60f50ef236bb0f748f141783308a103c3ab9
mutations/m4a_src_typecheck_red.log              d6cd1ff1d7d2196c40aa5264c93dbbcac275d0ab8959048919f2911597dfff80
mutations/m4b_e2e_typecheck_green.log            e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
mutations/m5_unit_green.log                      b2432fc36e81ff1a39e041b88e5088d2740c766ef654fde1624b971851fe8602
mutations/m5_e2e_red.log                         e0336d38b7746edbb8a65b5cd8de93b5a840ba077f8a748d839ba5cf574758fa
mutations/m5_restored_e2e_green.log              6d29a053ad9d2da398128b1bec1266caf550a28fd17a5174654f2808bbf1226c
probes/q6_unconfigured_isolation.log             28c7a976dfab96765e05cd510e6df703c9d31f35ddf0c3ce5e5c457b49514153
probes/q7_injection_surface.log                  731cd2a8be03bacf0b88133eeee40d6d8a9d79a07cb344e86ecb64294fc09a53
probes/q8_concurrency.log                        81382d4b47ece58df8b7981da0a6b2b636e170c4d96114a91453bc6013e20d8f
probes/qa_trend_500_repro.log                    ba9c645f7a18da262c1b080ad0675dc250720044a33221299066565259f5a919
probes/qa_trend_scope.log                        f8161de234e47b0f5ffc8a5b9c0f6b30c8c0e2f29bca6a768197a4234a0061a3
probes/qa_visual_result.json                     65944ec25122c744b517a77640f0102d2ddb0f058428afe8b100273892a8d04c
probes/kert_8107_service_console.log             4ed85bbf346b2c69140cdfc5030ebbc1daa4dfbcd3e89c45ed7ad7381ab025b0
../an0-ccrm-analytics-qa/shots/operating-metrics.png   1f81c81f176910f5eb29e1f3a4eb72a4225362b77665c4d98e28dc352f039ee0
../an0-ccrm-analytics-qa/shots/segments.png            97da57bf9fd26f624708cc0bba922082e6994eb20f2b2a314f30a0d9e38c1838
../an0-ccrm-analytics-qa/shots/monitors.png            073a7f947fc5868e4922c48e4903ac9ed22bbf444d0b60cc1729e37547f5679e
../an0-ccrm-analytics-qa/shots/combo-query.png         5d4541f815fb686fadf1e9e445b4100a159ecf35ca9c44a4abf3aae440ddb27e
scripts/q6_isolation.py                          f4348297054769cd132f686ba1d8e6d1234f43e5818660bba1d284f5e4c2a9e0
scripts/q8_concurrency.py                        dda13956f1dc6bad076c85dbd035ac0debb2f2331ae27175b31c60f43d929aa8
scripts/apply_m3.py                              27d96935244d67a5ec50880306bff9d4c7eab0f4ff34a38adc6361929428a717
scripts/apply_m4.py                              d36c703dbdd9f0b028e71ac27c41c43ebb9235aad12b1e12fed3bad3eb6a188a
scripts/apply_m5.py                              eb0108f86d022d14608f720c60f95dd1507f2ba180a1e9dc4b865f9fb04ae7c9
scripts/qa_visual.cjs                            4ee5eb9acee99d0b8bc79d67d2002a2dff56b71de6f3d1ed062d3d7941c9b930
scripts/qa_trend_scope.cjs                       ebad8ae11bc0ac24fd68611fbcc0d64ff4a8d5f7b10d900fd87563555577ea8f
```

---

## 9. 结论与交接

**判定：FAIL —— 不予 QA_PASS。**

- 6 道 implementation 门禁独立复跑 **exit=0**（Q1 PASS）、证据哈希 4/6 逐字节可复现（Q2 PASS）、M1~M5 变异**全部被捕获**（Q3 PASS）、Q4~Q11 全部 PASS、Q12 4 项 PASS；
- 但 **F1/F2/F3（MAJOR）** 构成用户可见功能失效：**4 个「经营指标分析」屏的趋势图恒不可用**（后端 500 + 前端静默降级为"趋势数据不足"），且现有门禁对该失效**结构性不可见**；另有 **F5（MAJOR）**「不动户参数 N」宣称参数化但未接线。
- 记 `FAILURES.md`：`FAIL-2026-09-22-AN0-QA-01`（F1）、`-02`（F2）、`-03`（F3）、`-04`（F5）、`-05`（F4）、`-06`（F6）、`-07`（F7，工具限制）。

**交接**

- Baton → `owner_review`（按派工交回；**不代签 Owner 签收**）。`STATE.json.qa_actor=independent_qa`、`qa_verdict=FAIL`、`EVIDENCE.json.independent_qa.status=fail` 已落盘。
- **建议 Owner 在 F1/F2/F3/F5 修复并由 `independent_qa` 重跑对应门禁（G1/G2/G5 + 趋势探针）之前，不签收本 Loop。**
- 修复建议（供 TL 参考，QA 未改任何实现）：
  1. F1：`_series_agg` 补 `JOIN dim_org o`（与 `_aggregate` 对齐）或对 `ORG` 轴改用 `w.org_id` 关联；
  2. F2：`trend()` 对成员/期间无数据时返回全 null 点列（或空 `points`），不得进入 `_derive` 计算；`_derive` 对 `sums` 为空应短路；
  3. F3：ORG 轴屏的 trend 应按行轴语义传参（`dim=ORG` + `dimValue=机构名`），且前端 `loadTrend` 不应把 500 静默降级为"趋势数据不足"（应呈现错误态）；E2E 需补「趋势图有数据点」的断言而非仅断言静态标题；
  4. F5：实现 `inactive_months` 判定或显式标注为「展示用未接线」并从决策②的"已落地"清单中移除；
  5. F4：修正 `LOOP.yaml` 的 pass_condition 文字（或把 `e2e/**` 纳入 tsconfig），二者取一，避免 over-claim。

**红线遵守声明**

- 只读复核：未改任何实现/文档（`git status` 两仓与开工快照一致；仅新增 Loop 证据与 Loop 记忆文件）；文档与实现不符项**先记账未顺手改文**（F4/F6）。
- 未以 mock 代替真实链路：E2E 与全部探针均打真实 KERT 8107（其中 M5 变异/还原两次由 playwright webServer 自起 vite 亦然）；未起服务即失败不降级。
- 未放宽 fail-closed：FTP 缺列 / 未配置分析库 / 白名单外取值三类拒绝在复核全程保持（M2/Q6/Q7 分别反证）。
- 未代签 Owner 决策、未恢复认证。

**QA 自建进程现状**：复核结束时 8107/5173/8108/8109/8110 均在运行（PID 540127/563550/548723/550228/553356）；
**会话间隔中环境重启，上述进程与 `/tmp/qa_an0/` 已随之终止/清除**（QA 证据已全部先行落仓库，不受影响）。
复跑命令（TL 修复后由 independent_qa 重建前置）：

```bash
# 1) 建库（先停 8107 释放读锁）
cd /home/szf/dev/Leibniz-KERT && python3 scripts/build_analytics_duckdb.py
# 2) 起 KERT 8107
KERT_ANALYTICS_DUCKDB=$PWD/examples/bank-front-analytics/cb_analytics.duckdb \
  python3 scripts/serve_analytics_api.py
# 3) 起 vite 5173（--host 127.0.0.1 以过 IPv4 健康检查）
cd /home/szf/dev/gits-cbanking/frontend && npx vite --host 127.0.0.1 --port 5173
# 4) 变异实例（如需复验 M1/M2）：副本库 + KERT_PORT=8109/8110，见 evidence/qa-an0-001/scripts/
```

> 变异仅落在 `/tmp/qa_an0/m1.duckdb`、`/tmp/qa_an0/m2.duckdb` 与临时脚本，仓库源码未被改动（§4.5，且 §4.5 的 sha256 终检在进程终止后复核仍一致）。
