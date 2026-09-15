# GITS Bank 人工测试清单 V1.0

> **编制**：Tech Lead（GK16 会话）｜**日期**：2026-09-14
> **性质**：**可勾选的执行单**，不是验收结论。
>
> **它不是**：`QA_PASS`、`UAT_PASS`、业务验收、生产就绪声明。
> **当前状态仍是** `UAT_PASS=NO / FROZEN=NO / PRODUCTION_READY=NO`
> （依据 `docs/governance/OWNER_UAT_W9A_FAIL_2026-08-26.md`）。
> 本清单的签署栏**只有 Owner 能填**；编制者不代签。

---

## 1. 环境与锚点（2026-09-14 实测）

### 1.1 启动（三条命令，无 MySQL 依赖）

```bash
# 顺序有意义：8107 是 8080 的依赖
cd /home/szf/dev/Leibniz-KERT     && nohup .venv/bin/python p24_serve_8107.py > /tmp/kert8107.log 2>&1 &
cd /home/szf/dev/gits-cbanking    && nohup java -jar apps/api/target/gits-kno-api-0.1.0-SNAPSHOT.jar > /tmp/api8080.log 2>&1 &
cd /home/szf/dev/gits-cbanking/frontend && nohup npx vite --host 127.0.0.1 --port 5173 > /tmp/vite5173.log 2>&1 &
```

| 组件 | 地址 | 实测 |
|---|---|---|
| 后端 API | `http://127.0.0.1:8080` | `/actuator/health` **200**（H2 内存库，4.1s 启动） |
| KERT 技能服务 | `http://127.0.0.1:8107` | `/api/skill/health` **200** |
| 前端工作台 | `http://127.0.0.1:5173/workbench` | **200**（`/api` 代理 → 8080 已通） |

| 锚点 | 值 |
|---|---|
| gits-cbanking HEAD | `3f16d97` |
| Leibniz-KERT HEAD | `c65a861` |
| 运行中的 jar | `apps/api/target/gits-kno-api-0.1.0-SNAPSHOT.jar`，**构建于 09-11 12:45** |

> ⚠️ **jar 早于 HEAD**（其后有 test/build 类提交）。要严格按 HEAD 测，先
> `./mvnw -pl apps/api -am package -DskipTests` 重建，并在本表更新锚点。

### 1.2 登录

本地 **DEV 模式跳过认证**（`frontend/src/router/index.ts`：`import.meta.env.DEV → next()`）。
直接访问 `http://127.0.0.1:5173/workbench` 即可，**不要**把"没登录也能进"当缺陷。
（后端 `gits.engagement.security.api-key` 为空 = 认证关闭。）

### 1.3 测试用种子客户

| customerId | 名称 |
|---|---|
| `CUST-CORP-0001` | 华东精工装备集团有限公司 |
| `CUST-CORP-0004` | 绿能新能源科技有限公司 |
| `CUST-CORP-0005` | 华创医药股份有限公司 |
| `CUST-CORP-0006` | 长江物流集团有限公司 |

（管户经理示例：`rmId=RM-ZW-001`）

---

## 2. 判读纪律（**先读这 5 条，否则你会误判**）

| # | 纪律 | 依据 |
|---|---|---|
| 1 | **空列表 ≠ 没有；`NOT_RUN` ≠ 没有**。本仓已因这两者不可区分而判 `semantic-consumption = NOT_MET` | 判据 S2/S3；`loops/GK16-trust-hardening/` |
| 2 | **`assemblyTrace` 说 `ok` ≠ 结论字段有值**。实测：trace 报"命中 7 条 KI"，而 `previsitReport.kycGapSummary` 四个列表全空、`customerOverview=null` | 见 §4.2 实测值 |
| 3 | **内容像模板 ≠ AI 差**。`engagement.llm.mode=mock`（确定性模板），不能据此评价模型能力 | `application.yaml` |
| 4 | **HTTP 404 ≠ "数据没有"**。本仓有多处"OpenAPI 登记了、实现没映射"，报错原文是 `No static resource api/v1/...` | §7 |
| 5 | **H2 内存库重启即丢**，种子每次重载。别用"数据还在不在"判断功能 | `application.yaml` |

---

## 3. A 组 · 冒烟（先跑这 5 项，任一不过就别往下测）

| # | 操作 | 期望 | 实测现状 | 判定 |
|---|---|---|---|---|
| A1 | `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8080/actuator/health` | `200` | **200** | □通过 □不通过 |
| A2 | `curl -s http://127.0.0.1:8080/api/v1/seed-data/status` | `{"loaded":true}` | **`{"loaded": true}`** | □通过 □不通过 |
| A3 | `curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8107/api/skill/health` | `200` | **200** | □通过 □不通过 |
| A4 | 浏览器打开 `http://127.0.0.1:5173/workbench` | 页面渲染，非空白页 | 页面 **200**；**视觉未实测** | □通过 □不通过 |
| A5 | 经前端代理取数：`curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5173/api/v1/interactions` | `200` | **200** | □通过 □不通过 |

> A3 不过时**不要继续测技能类页面**（见 §5 · D 组）。8107 不在线时页面会是"空态"而非"报错"，会被误读为页面坏了。

---

## 4. B 组 · 主链路（客户经营闭环）

### 4.1 启动旅程

| # | 操作 | 期望 | 实测现状 | 判定 |
|---|---|---|---|---|
| B1 | `POST /api/v1/engagement/journey/start`，体 `{"customerId":"CUST-CORP-0001"}` | `201` + `journeyId` + `phase` | **201**；`journeyId=3e4a0138-…`；`phase=INSIGHT_ANALYSIS`；`kycGapSummary="未知项:3,待确认:3"` | □通过 □不通过 |
| B2 | 浏览器：导航「信号与互动」→ 选中客户 → 点「启动旅程」 | 按钮可见可点，页面进入旅程态 | **未做视觉实测**；08-26 曾因 `v-if="sc&&!jid"` 按钮不出现，已改"默认选客户 + 按钮常驻" | □通过 □不通过 |
| B3 | 旅程页显示 `phase` 与 `kycGapSummary` | 与 B1 返回一致 | **未做视觉实测** | □通过 □不通过 |

### 4.2 一键访前（**本清单最需要注意的一项**）

请求体**必须**含 `customerId` 与 `operatingCaseId`，缺任一返回 `400`（实测）。

| # | 操作 | 期望 | 实测现状 | 判定 |
|---|---|---|---|---|
| B4 | `POST /api/v1/engagement/journey/{jid}/prepare-previsit` | `200` | **200** | □通过 □不通过 |
| B5 | 页面展示"正在调用的 skillId"与知识装配轨迹 | 可见 `assemblyTrace` | **13 步** trace，含 `skillId=skill-customer-previsit-report`、`进入知识地图 KM-CORP-RM-PREVISIT`、`KERT 客户知识库检索完成（命中 7 条 KI）`、逐条 `KI-FRONT-001…006 取数完成` | □通过 □不通过 |
| B6 | 访前报告**结论字段**是否有值 | 有业务内容 | ⚠️ **`previsitReport.customerOverview=null`；`kycGapSummary` 四个列表全空；`productSchemes=[]`；`keyQuestions=[]`；`visitStrategy` 为一句话套模板** | □通过 □不通过 |
| B7 | 速战卡（battleCard）是否有值 | 有业务内容 | ✅ **有**：`customerTier=STRATEGIC`、`riskLevel=MEDIUM`；`keyPoints` 含产业链八维；`dontForget` 含承诺事项与 KYC 缺口 | □通过 □不通过 |
| B8 | 报告正文（`skillSections`） | 有内容 | ✅ **7 段有内容**（KI-009 / KI-FRONT-001~006 供应链、八维、行内变动、承诺、KYC 缺口、产品组合） | □通过 □不通过 |
| B9 | 供应链图谱 `supplyChainMarkdown` | 有内容 | ⚠️ **`null`**（P05 集团关系图依赖 DKWS，当前为空态） | □通过 □不通过 |

> **B6/B7/B8 并置就是本仓最典型的"文本说对、结论说错"**：
> 轨迹说知识都命中了，正文有内容，**但结构化结论字段是空的**。
> 请**分别**记录：这是"展示层没映射"还是"结论确实没有"——**不要合并成一句"功能不可用"**。

### 4.3 只读数据面（人工目视页面时用这些做对照）

| # | 页面/数据 | 端点 | 实测现状 | 判定 |
|---|---|---|---|---|
| B10 | 互动列表 | `GET /interactions` | **200**，`list[23]` | □通过 □不通过 |
| B11 | 任务 | `GET /tasks` | **200**，`list[5]` | □通过 □不通过 |
| B12 | 承诺 | `GET /commitments` | **200**，`list[3]` | □通过 □不通过 |
| B13 | 机会 | `GET /opportunities` | **200**，`list[3]` | □通过 □不通过 |
| B14 | 人工门禁 | `GET /human-gates` | **200**，`list[5]` | □通过 □不通过 |
| B15 | CRM 回写命令 | `GET /crm/writeback-commands` | **200**，`list[3]` | □通过 □不通过 |
| B16 | 外部事件 | `GET /external-events` | **200**，`list[6]` | □通过 □不通过 |
| B17 | 审计追踪 | `GET /audit-trace` | **200**，`list[5]` | □通过 □不通过 |
| B18 | 客户经营总览 | `GET /engagement/customer/CUST-CORP-0001/operating-view` | **200**，25.8 KB；`customer/entities/groupRelationships/bankRelationship/creditFacilities/transactions` | □通过 □不通过 |
| B19 | 客户资金流水 | `GET /engagement/customer/CUST-CORP-0001/transactions` | **200**，`list[78]` | □通过 □不通过 |
| B20 | KYC 缺口画像 | `GET /engagement/kyc/CUST-CORP-0001/gap-profile` | **200**，含 `knownItems/partialKnownItems/staleItems/conflictingOrAmbiguousItems/unknownItems` | □通过 □不通过 |
| B21 | 知识卡（P38） | `GET /engagement/customer/CUST-CORP-0001/knowledge-map` | **200**，3.1 KB；`skillSections` + `assemblyTrace` | □通过 □不通过 |

> **通用检查**：列表接口**空时应返回 `[]` 而不是 `null`**（仓库规则）。目视时请留意页面是把空数组渲染成"0 条"还是"加载失败"。

---

## 5. C 组 · 导航巡检（4 组 12 项）

导航定义：`frontend/src/layouts/navConfig.ts`。逐项点击，核对**是否落到该页面**、**有无报错**、**设计是否与 V3.2 一致**。

| # | 分组 | 菜单项 | 目标路由 | 实测数据面 | 判定 |
|---|---|---|---|---|---|
| C1 | 日常作业 | 客户经营作战台 | `/workbench` | 页面 200 | □通过 □不通过 |
| C2 | 日常作业 | 我的任务与承诺 | `/commitments` | tasks 5 / commitments 3 | □通过 □不通过 |
| C3 | 客户经营 | 客户组合 | ⚠️ **`/accounts`** | — | □通过 □不通过 |
| C4 | 客户经营 | 客户全景 | `/accounts` | 客户列表 4 条（需 `rmId`） | □通过 □不通过 |
| C5 | 客户经营 | 信号与互动 | `/engagement` | interactions 23 | □通过 □不通过 |
| C6 | 客户经营 | 需求与机会 | `/needs` | **未实测**（C2 降级域） | □通过 □不通过 |
| C7 | 方案与交付 | 服务建议书 | `/proposals` | **未实测**（C2 降级域） | □通过 □不通过 |
| C8 | 方案与交付 | 产品推荐 | `/recommendation/new` | **未实测** | □通过 □不通过 |
| C9 | 方案与交付 | 专家协同 | `/collab` | **未实测**（`objectStatus: 无合同对象`） | □通过 □不通过 |
| C10 | 方案与交付 | 账户计划与价值 | `/account-plans` | **未实测**（`无 AccountPlan`） | □通过 □不通过 |
| C11 | 知识与治理 | 产品解读与知识 | `/knowledge-map` | knowledge-map 200 | □通过 □不通过 |
| C12 | 知识与治理 | 审批与审计 | `/approvals` | human-gates 5 | □通过 □不通过 |

> ⚠️ **C3 已实测到异常**：菜单「客户组合」指向 `/accounts`，而路由表里 P03「客户分层与组合看板」是
> **`/accounts/portfolio`**。即**「客户组合」没有指向 P03**，与菜单语义/设计图不符。
> 这是可以从代码直接确认的，属"待确认缺陷"，请 Owner 判是否为缺陷。

**移动端另测 4 页**（不在一级导航内，直接访问）：
`/m/today`（P41）、`/m/previsit`（P42，离线包未授权）、`/m/notes`（P43，草稿非正式）、`/m/checkout`（P44，在线门禁）。

---

## 6. D 组 · 降级与异常（**最能暴露问题的一组**）

期望依据：`evidence/L6/操作说明-L6.md` §4。

| # | 操作 | 期望 | 实测现状 | 判定 |
|---|---|---|---|---|
| D1 | **停掉 8107** 后点「一键访前」 | 依赖服务不可用 ⇒ **`503` 明确报错**；禁止静默成功 | ⚠️ **实测 `200`**，内容为空态（`openingLine=""`、`talkingPoints=[]`）；**未发现本地补数** | □通过 □不通过 |
| D2 | 恢复 8107 后同一请求 | 内容恢复 | ✅ 恢复：`openingLine="综合金融服务"`、`talkingPoints=2`、`skillSections=7`、`assemblyTrace=13` | □通过 □不通过 |
| D3 | 打开 `/degrade`（P40 服务降级与异常恢复） | 在线探测显示依赖状态 | **未实测** | □通过 □不通过 |
| D4 | 触发并发版本冲突（CAS） | `409`，不覆盖写 | **未实测**（需人工构造） | □通过 □不通过 |
| D5 | 同一幂等键、不同 payload | `409 IDEMPOTENCY_CONFLICT` | **未实测** | □通过 □不通过 |
| D6 | 触发受控动作超时 | `RESULT_UNKNOWN`，先查目标回执 | **未实测** | □通过 □不通过 |
| D7 | 尝试白名单外写回（转账/放款/授信审批） | 拒绝：`FORBIDDEN_ACTION_REJECTED` | **未实测**（红线，务必测） | □通过 □不通过 |

> **D1 是本次编制中发现的最需要裁定的口径冲突**：
> - `evidence/L6/操作说明-L6.md` §4 要求：**依赖服务不可用 ⇒ 503 明确报错；禁止静默成功**；
> - `docs/governance/OWNER_UAT_W9A_FAIL_2026-08-26.md` 的处置又写：**失败空态，不本地补数**（Owner 当时的要求）。
>
> 实测行为 = **`200` + 空态**。**好消息**：没有本地补数（红线守住了）。
> **待裁定**：空态应当以 `200` 还是 `503` 呈现。**本清单不替 Owner 判**，请在此栏写结论：
> 裁定：______________________

---

## 7. F 组 · 编制者实测到的缺口（**请登记，不要当人工测试结论**）

以下均为**只读探测**所得，报错原文可复现。它们不是"测试用例失败"，是**实现与合同的差距**。

| # | 端点（OpenAPI 已登记） | 实测 | 报错原文 | 影响 |
|---|---|---|---|---|
| F1 | `GET /engagement/claims`（`listClaims`） | **404** | `No static resource api/v1/engagement/claims.` | **P37 Claim/Evidence 中心页会报错**（`ClaimsView.vue` 使用它） |
| F2 | `GET /customer-journeys` | **404** | `No static resource api/v1/customer-journeys.` | 前端当前未调用 |
| F3 | `GET /knowledge-rules` | **404** | `No static resource api/v1/knowledge-rules.` | 前端当前未调用 |
| F4 | `GET /operating-cases` | **404** | `No static resource api/v1/operating-cases.` | 前端当前未调用 |
| F5 | `GET /products/versions` | **404** | `No static resource api/v1/products/versions.` | 前端当前未调用 |
| F6 | `GET /engagement/kyc/{customerId}/insights` | **404** | `No static resource api/v1/engagement/kyc/….` | 前端当前未调用 |
| F7 | 错误响应结构 | 运行时为 `{errorCode, message, timestamp}` | OpenAPI 权威 `Problem` 为 `{status, error, message, path, timestamp}` | **合同与实现漂移**（与本仓"合同 SSOT"规则冲突） |

> **F1 与 08-26 的 500 是同一根因**：`interactions` 当时也是"合同有、映射无"，被全局处理成 500；
> 现在至少退化为**明确的 404 + `No static resource`**（可诊断性提升了）。
> **建议**：先记 `FAILURES.md`，再决定是补实现还是从合同移除（**属合同变更，须走合同先行**）。

---

## 8. G 组 · 人工测试**无法**证明的事项（不要写进结论）

| # | 事项 | 为什么不能 |
|---|---|---|
| G1 | 语义级消费是否成立 | `semantic-consumption = NOT_MET`，**独立判定**；且 GITS 侧 `llm.mode=mock`，无真实模型语义可测 |
| G2 | AI 输出质量 | 确定性模板，不是模型输出 |
| G3 | 生产写回正确性 | `engagement.crm.mode=logging`（只写日志） |
| G4 | 图/向量检索能力 | LightRAG **未启用**；Kuzu 为**模拟**投影 |
| G5 | 性能与容量 | H2 内存库、单机、无压测 |
| G6 | 任何签署（QA_PASS / UAT_PASS / 冻结） | 非人工测试可产生；须 Owner/独立 QA 角色 |

---

## 9. 附 · 取证命令（可直接复制）

```bash
# 冒烟
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8080/actuator/health
curl -s http://127.0.0.1:8080/api/v1/seed-data/status
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8107/api/skill/health
curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:5173/workbench

# 客户
curl -s "http://127.0.0.1:8080/api/v1/engagement/customer?rmId=RM-ZW-001"

# 主链路（一次启动，取出两个 id）
RESP=$(curl -s -X POST http://127.0.0.1:8080/api/v1/engagement/journey/start \
  -H 'Content-Type: application/json' -d '{"customerId":"CUST-CORP-0001"}')
echo "$RESP"
JID=$(echo "$RESP" | python3 -c "import sys,json;print(json.load(sys.stdin)['journeyId'])")
CID=$(echo "$RESP" | python3 -c "import sys,json;print(json.load(sys.stdin)['operatingCaseId'])")
curl -s -X POST "http://127.0.0.1:8080/api/v1/engagement/journey/$JID/prepare-previsit" \
  -H 'Content-Type: application/json' \
  -d "{\"customerId\":\"CUST-CORP-0001\",\"operatingCaseId\":\"$CID\",\"visitObjective\":\"了解经营与融资需求\",\"channel\":\"EMAIL\"}"

# 缺口复现（F 组）
for p in /customer-journeys /engagement/claims /knowledge-rules /operating-cases /products/versions; do
  printf "%-24s " "$p"; curl -s "http://127.0.0.1:8080/api/v1$p"; echo
done

# 依赖降级（D 组）
pkill -f p24_serve_8107.py && sleep 2   # 停
cd /home/szf/dev/Leibniz-KERT && nohup .venv/bin/python p24_serve_8107.py > /tmp/kert8107.log 2>&1 &   # 起

# 自动化侧（覆盖回归，不替代人工）
make e2e-test          # Playwright，默认忽略 *.live.spec.ts
cd frontend && npx playwright test --headed        # 可视化跑
```

**自动化已覆盖的用例文件**（11 个 + `sit-fixtures.ts`）：
`dashboard` / `experience-shell` / `full-experience` / `customer-detail` / `customer-manager-flow` /
`customer-panorama` / `journey` / `report` / `sit-applicable` +
**live（需真实服务，默认跳过）**：`five-scenarios.live` / `p24-s4-wizard.live` / `signals-engagement.live`。

---

## 10. 签署栏（**仅 Owner 可填**）

| 项 | 值 |
|---|---|
| 测试日期 | |
| 测试人 | |
| 环境锚点（HEAD / jar） | |
| 通过 / 不通过 | |
| 缺陷登记（编号） | |
| `UAT_PASS` | □YES □NO　**（编制者不得代签）** |
| 结论与后续要求 | |

---

### 编制者声明

- 本清单中的"实测现状"**全部来自 2026-09-14 的实际命令输出**，取证命令见 §9；
- 标注 **"未实测"** 的行是**编制者没有验证**的，不得读作"没问题"（本仓纪律：未执行 ≠ 通过）；
- 编制者**未修改**任何被测实现、未签署任何通过结论、未替 Owner 裁定 D1 的口径冲突；
- 编制者为 **Tech Lead**，不是独立 QA，**不构成 `QA_PASS`**。
