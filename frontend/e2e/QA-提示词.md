# E2E Playwright QA 提示词（V1.0 · 2026-09-22）

**怎么用**：在 `frontend/` 目录下，把下面「提示词正文」整段投给 AI 工程师 / QA 执行者。
环境已就绪时（前端 15173 · 后端 18080 · KERT 技能 8107 · LightRAG 9621）可直接跑；也可只跑配置自带的 5173 dev server。

---

## 提示词正文（复制以下全文）

你是本项目的 **E2E QA 工程师**。用 Playwright 对系统做端到端验收，产出**可复现的缺陷证据**，**不修改产品代码**，**不为了让用例变绿而放宽断言**。

### 0. 铁律（违反即本次 QA 作废）

1. **fail-closed**：服务不可达 / 环境未就绪 ⇒ 用例判 **BLOCKED**（具名原因）。**禁止** skip、**禁止**当 pass。
2. **不许改产品代码**：`src/**`、`apps/**`、`scenario/**` 一律只读。你只能新增/修改 `frontend/e2e/**` 用例与 `frontend/test-results/**` 证据。
3. **不许削弱断言**：不得把 `toHaveText` 改成 `toBeVisible`、不得加 `waitForTimeout` 掩盖竞态、不得删除失败用例。断言与产品实现冲突时，**先复现 → 判 FAIL → 在报告里给最小复现与证据**，由 Owner 决定改产品还是改期望值。
4. **不许冒充真实链路**：用 `page.route()` stub 的用例，用例名与报告结论必须显式标 `[STUB]`；**不得**把 stub 通过说成"链路已验证"。
5. **只读外部实例**：不得对 LightRAG（9621）做 publish / retract / delete；不得改 KERT 工作区文件。唯一允许的**环境写操作**是 C 组要求的"停/起 KERT 技能服务"，且**必须复原**并在报告登记。
6. **不得伪造**：不得手改 JSON/DB/浏览器 localStorage 制造"通过"；不得用截图工具美化结果。
7. **诚实报告未覆盖项**：没跑的、跑不了的、不确定的，列在报告"未覆盖/存疑"一节。**空着不写＝不合格**。
8. **不改 git**：不 commit、不 push（除非 Owner 明说）。

### 1. 被测系统事实卡（**已核实，不许再猜**）

| 项 | 事实 |
|---|---|
| 前端 | `frontend/`，Vue 3 + Vite（`naive-ui` / `tdesign-vue-next`），Node **≥ 22** |
| E2E 框架 | `@playwright/test` **1.62.0**，浏览器已装（chromium） |
| 配置 | `frontend/playwright.config.ts`：`testDir=./e2e`、`baseURL=http://127.0.0.1:5173`、`webServer` 自动起 `npm run dev -- --host 127.0.0.1 --port 5173`（本地 `reuseExistingServer=true`）、`trace=on-first-retry`、`screenshot=only-on-failure` |
| **命名约定（重要）** | `e2e/*.spec.ts` = 默认跑；`e2e/*.live.spec.ts` = **需真实后端，被 `testIgnore` 默认排除** —— 跑它们要显式覆盖（见 §3） |
| 已运行环境 | 前端 `http://127.0.0.1:15173` · 后端 `http://127.0.0.1:18080` · KERT 技能 `http://127.0.0.1:8107` · LightRAG `http://127.0.0.1:9621` |
| 既有 spec | `e2e/` 下 15 个（含 `product-center-pc1.spec.ts`、`p38-source-path.spec.ts`、`experience-shell.spec.ts`、`analytics.spec.ts`、`*.live.spec.ts` 三个、fixture `sit-fixtures.ts`） |
| 关键接口 | `/api/v1/product-center/products/{productId}` · `/api/v1/product-knowledge/**` · `/api/v1/product-recommendation-runs/**` · `/api/v14/proposals` · `/api/v14/gates/**` · `/api/v14/memories/extract` |
| 8 章实现 | `src/views/ProductCenterView.vue` → `src/components/product-center/ProductChapterStack.vue`（章清单在 `product-center/sections.ts`） |
| 章节生效规则 | 有契约数据 ⇒ 渲染正文；**无数据 ⇒ 必须显示具名 `待接入 <批次>` 标签**（`pc-chapter-pending`）。**严禁**示意值/占位文案填充（需求 01 §3.2 / PI-BR-005） |

**8 章清册（源自 `product-center/sections.ts`，**逐章核对用**）**：

| # | key | 标题（须逐字匹配） | 锚点 | 数据来源字段（取 `GET /api/v1/product-center/products/{id}`） |
|---|---|---|---|---|
| 01 | `OVERVIEW` | 60 秒读懂 | `pc-sec-overview` | `summary` |
| 02 | `TERMS` | 核心条款 | `pc-sec-terms` | `terms` |
| 03 | `FIT` | 适用边界 | `pc-sec-fit` | `boundaries` |
| 04 | `PROCESS` | 办理流程 | `pc-sec-process` | `processSteps` |
| 05 | `MATERIALS` | 申请材料 | `pc-sec-materials` | `materialGroups` |
| 06 | `PRICING` | 价格与协议 | `pc-sec-pricing` | `pricingItems` |
| 07 | `COMPARE` | 同类产品比较 | `pc-sec-compare` | `comparison` |
| 08 | `FAQ` | 常见问题 | `pc-sec-faq` | `faqs` |

`hasPayload` 规则（组件实现）：列表字段**数组非空** / `summary`·`comparison` **非 null** ⇒ 渲染正文；否则渲染 `pc-chapter-pending`（`待接入 <批次>`）。
> 同一"7 章待接入"的硬编码也出现在**单测** `src/views/__tests__/ProductCenterView.spec.ts:213` —— 与 `F3` 同源，一并按事实核。

**可用于断言的真实 testid（既有 spec 已在用，优先复用）**：
`pc-env-banner`、`pc-env-tag`（含 `DEMO` 与 `演示数据`）、`pc-knowledge-as-of`、`pc-search-input`、`pc-identity`、`pc-catalog`、`pc-catalog-family`（6 族）、`pc-catalog-product`（13 卡）、`pc-hero`、`pc-hero-product-id`、`pc-publish-status`、`pc-fixed-boundaries`、`pc-section-link`（8 项，第 1=`60 秒读懂`、第 8=`常见问题`）、`pc-chapter`（8 章）、`pc-chapter-pending`、`pc-governance`、`pc-gov-pending`。

### 2. 必测矩阵（按 ID 逐条出结论）

**A 组 · 环境与资源完整性（P0）**

- `A1` 页面 200 且 HTML 非空（产品中心 + 至少 3 个其他页）。
- `A2` **同源 css/js 无 4xx/5xx**。存在理由：历史上真实发生过 `mount_dsh` 把静态挂载排在 SPA 兜底之后 ⇒ 页面 200 但**样式/脚本全 404**（界面等于不可用），纯 HTTP 断言发现不了。
- `A3` 全程 `page.on('pageerror')` 与 `console.error` 为空（若有白名单，须逐条写明理由与来源）。
- `A4` 页面内的关键 API 请求**真实发起且 200**（读 HAR/network），不得靠 `page.route` 拦截伪装（stub 用例须标 `[STUB]`）。

**B 组 · 产品中心 8 章（P0）**

- `B1` 产品目录 6 族 / 13 卡可见。
- `B2` 点选产品 ⇒ URL 变 `/product-center/<PRODUCT_ID>` 且 hero 的 `pc-hero-product-id` 与 URL **一致**（跨层一致性）。
- `B3` 章节导航 8 项且锚点可跳（第 1 `60 秒读懂`、第 8 `常见问题`）；`pc-chapter` 计 8。
- `B4` **逐章二选一，且必须与接口事实对齐**：① 该章有数据 ⇒ 正文非空，且内容与 `/api/v1/product-center/products/<ID>` 返回一致（抽查 ≥1 处）；② 该章无数据 ⇒ 显示具名 `待接入 <批次>`。**空白页、"" 占位、假值 ⇒ FAIL（P0）**。
- `B5` 元信息缺失位必须显示"待维护/待核验"（如 `pc-knowledge-as-of`），**不得**出现伪造日期/伪造版本。
- `B6` 页面文本**不得**出现服务器绝对路径（沿用 `p38-source-path.spec.ts` 规则）。

**C 组 · SP-20 失败语义（P0 —— 刚修的口径，必须复验）**

- `C1` **反例**：停 KERT 技能（8107）后调 `POST /api/v14/proposals` ⇒ 必须 **HTTP 503** 且响应含具名码 `KERT_UNAVAILABLE`；**前端必须显示具名错误**。
  **禁止出现的旧缺陷**：HTTP 200 + `status=SUCCESS` 的空壳，或"页面静默无草稿"。
- `C2` 另一条反例：KERT 能连但**未供给控制面**时 ⇒ 503 且 message 含 KERT 错误码（如 `KERT_PERMISSION_DENIED` / `ROUTE_POLICY_ABSENT`）—— 不得被渲染成成功。
- `C3` **正例**：KERT 正常 ⇒ 200 且草稿非空（`citations ≥ 1`，`content.proposalDraft` 非空）。**C3 未过 ⇒ C1/C2 的"503"无意义**（可能只是全线不可用）。
- `C4` C1/C2 结束后**必须把 KERT 技能恢复**，并在报告登记"停/起时间、复原证据"。

**D 组 · 跨页一致性与证据链（P1）**

- `D1` 同一产品在**产品中心 / 解读页 / 推荐运行**等不同页的同一字段值一致（一页有值、另一页空 ⇒ FAIL）。
- `D2` 证据/出处可见且与后端返回集合一致；**限制声明必须可见**（如 `clause_verified=false`、OCR 件的复核义务、`DRAFT`/`无审核记录`），静默隐藏 ⇒ FAIL。
- `D3` 降级/恢复页、审计追溯页、审批页可开、无 console 错误、无一空白。

**E 组 · 诚实性红线（P0/P1）**

- `E1` 未接入能力必须**显式标注**（如 `身份服务未接入`、`未发布受控版本`、`待接入 <批次>`）。
- `E2` 若发现**演示/示意数据被当作真实数据呈现**（无标注）⇒ **FAIL（P0）**，这是本项目的核心红线。

**F 组 · 既有 spec 全量回归（P0）**

- `F1` 跑默认集全量（`npx playwright test`），逐条登记 pass/fail。
- `F2` 跑 `*.live.spec.ts`（需覆盖 `testIgnore`，见 §3），同样逐条登记。
- `F3` **已知疑点（先复现再判，不许直接改断言）**：`e2e/product-center-pc1.spec.ts` 硬编码 `pc-chapter-pending = 7`；而当前 `18080` 的产品中心已接 KERT 章节投影（实测 `GET /api/v1/product-center/products/PROD-CM-003` 的 `summary/comparison/terms/boundaries/processSteps/materialGroups/pricingItems/faqs` **均有值**）⇒ 该期望值**很可能已过期**。按事实报，并给出"产品缺陷 or 期望值过期"的判断依据。

**G 组 · 窄屏/移动降级（P2）**：至少 1 个 viewport（如 390×844）跑通 A2/A3/B3。

### 3. 执行方式（照抄）

```bash
cd frontend
npm ci                      # 或 npm install；Node ≥ 22
npx playwright install chromium   # 缺浏览器才需要（本机已装）

# ① 默认集（配置自带 webServer 会起 5173；本地若已有 5173 会复用）
npx playwright test --reporter=list,html

# ② 对**已运行环境**（15173/18080/8107/9621）跑，含 *.live.spec.ts
#    新建 playwright.qa.config.ts（覆盖 testIgnore 与 baseURL；不要改原 config 的默认值）
#    export default defineConfig(base, { testIgnore: [], webServer: undefined,
#      use: { ...base.use, baseURL: process.env.QA_BASE_URL ?? 'http://127.0.0.1:15173',
#             trace: 'on', screenshot: 'on', video: 'on' } })
QA_BASE_URL=http://127.0.0.1:15173 npx playwright test --config playwright.qa.config.ts

# ③ 单点复现
npx playwright test e2e/product-center-pc1.spec.ts -g "八章"
npx playwright show-trace test-results/<用例>/trace.zip
```

**环境就绪自检（先跑，不过就报 BLOCKED）**：
```bash
for u in http://127.0.0.1:15173/ http://127.0.0.1:18080/actuator/health \
         http://127.0.0.1:8107/v1/health http://127.0.0.1:9621/health; do
  printf "%-46s %s\n" "$u" "$(curl -s -o /dev/null -w '%{http_code}' --max-time 4 "$u")"; done
```

### 4. 证据要求（**弱证据不算证据**）

每个 FAIL 必须附：① 最小复现步骤（可让人 3 分钟重现）② Playwright trace 或 HTML report 片段 ③ 截图 ④ 相关 network 请求/响应（HAR 或 HAR 片段）⑤ console/pageerror 原文。
证据目录：`frontend/test-results/qa-<YYYYMMDD-HHMM>/`（含 `report.html`、`trace.zip`、`shot-*.png`、`har/*.har`、原始 JSON 报告）。
**只有 DOM 断言、没有证据的结论 = 不接受。**

### 5. 报告格式（写入 `test-results/qa-<日期>/REPORT.md`）

```markdown
# E2E QA 报告 · <日期> · 环境：<15173/18080/8107/9621 状态>
## 一、总判：PASS / FAIL / BLOCKED（BLOCKED 必须写清哪一环不可达）
## 二、用例结果
| ID | 场景 | 预期 | 实际 | 证据 | 严重度 | 结论 |
|---|---|---|---|---|---|---|
| A2 | css/js 无 4xx/5xx | 0 个失败请求 | 3 个 404（`/assets/xx.css`） | shot-02.png / har/h1.har | P0 | FAIL |
## 三、缺陷清单（每个含：现象 / 最小复现 / 影响面 / 建议 / 证据路径 / 是否阻塞发布）
## 四、未覆盖 / 存疑（**必填**：没测的、环境所限测不了的、断言与实现冲突待 Owner 决策的）
## 五、环境变动登记（如 C 组停/起 KERT 技能的时间与复原证据）
## 六、原始产物索引（report.html / trace / har / json）
```

### 6. 完成判据

- A–F 组每条都有结论（含 BLOCKED 的具名原因），G 组至少 1 个 viewport；
- 每个 FAIL 都有 §4 要求的证据；
- **未覆盖/存疑**一节非空（除非真的全测了，且要有依据说明）；
- 未违反 §0 任一铁律；
- 最终**一句话结论**：能否发布 / 阻塞项是什么。

### 7. 口径提醒（别把 A 说成 B）

- 本 QA 验的是**界面与接口契约的端到端行为**；链路的**正确性**证据在 `tests/integration/**` 与 CI 的 `retrieval-loop-e2e`，**界面通过 ≠ 链路已验证**。
- LightRAG 是**可重建的派生检索层**（ADR-017），其字段值**不得**作为业务字段来源；用 mock 模型的检索结果**不能**作为检索质量结论。
- KERT 侧 `clause_verified=false` / OCR 转写的材料，QA **不得**表述为"合规已核验"。演示环境（`DEMO` 标签）≠ 生产数据。
