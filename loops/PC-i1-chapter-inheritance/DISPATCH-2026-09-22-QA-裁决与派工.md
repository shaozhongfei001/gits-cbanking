# 派工单 · PC-i1-DISPATCH-001 · QA 裁决与派工（2026-09-22）

```text
DISPATCH_ID   = PC-i1-DISPATCH-001
LOOP_ID       = PC-i1-chapter-inheritance
DISPATCHED_BY = tech_lead
DATE          = 2026-09-22
授权状态      = PENDING_OWNER_AUTHORIZATION —— **未授权，任何人不得开工实现**
依据          = frontend/test-results/qa-20260922-1430/REPORT.md（独立 E2E QA，总判 FAIL）
                loops/PC-i1-chapter-inheritance/memory/INDEX_BASIS.md（本轮裁决 + 影响面回源）
基线          = 分支 recover/PI-ARCH-product-catalog；gits HEAD fdd2bdb / KERT HEAD 65b96df
                索引 INDEX_STALE(51)（make index-status → WARN）⇒ 本条所有事实逐条回源
```

> **本单只做派工，不做实现。** 需 Owner 在文末签字后，由 `feature_pilot` 执行；期间不得触碰本单未列文件。

---

## 一、范围（逐字取自 `LOOP.yaml`，不得扩大）

**include**：`frontend/src/components/product-center/`、`frontend/src/views/ProductCenterView.vue`、`frontend/src/api/productCenter.ts`、`frontend/e2e/product-center-pc1.spec.ts`、`apps/api/src/main/java/com/gien/gits/api/productcenter/`、`loops/PC-i1-chapter-inheritance/`

**exclude**：`ProductInterpretationView.vue`（P38 冻结）、`apps/api/.../productknowledge/`（P38 冻结）、`specs/` 受控源（改须合同 Owner 签字）、**Leibniz-KERT 制品**

---

## 二、工作项

### W-1 ·【P0 · 阻塞 · 本 loop】补齐 5 章正文渲染（QA-D-1）

| 项 | 内容 |
|---|---|
| 现象 | `TERMS`/`FIT`/`PROCESS`/`MATERIALS`/`COMPARE` 五章**有契约数据却不渲染**，也无「待接入」标签 ⇒ 空壳章节。**13/13 产品全命中**（每产品 5 章） |
| 根因（回源） | `frontend/src/components/product-center/ProductChapterStack.vue:106`（`v-else-if="!hasPayload"`）之前只有 `:70` 的 `v-if="section.key === 'OVERVIEW'"`；**全组件无 `v-else`** ⇒ `hasPayload===true` 且非 `OVERVIEW` 的章节无分支可命中 |
| 动作 | ① 按 `sections.ts:28-37` 的契约对象，为 `TERMS`/`FIT`/`PROCESS`/`MATERIALS`/`COMPARE` 增加**正文分支**（`v-else` 或按 key 分派）；② 形状**必须**取自既有受控契约 `specs/product-center/product-center-api.openapi.json:368/401/414/426/461/511`（`PkcTerm`/`PkcBoundary`/`PkcPrerequisite`/`PkcProcessStep`/`PkcMaterialGroup`/`PkcComparisonSet`），**不是新造**；③ 在 `frontend/src/api/productCenter.ts:108-117` 把章节字段由 `unknown[]`/`unknown \| null` 收敛为契约类型 |
| **禁止** | 不得硬编码业务内容（`sections.ts:4-11` 明令）；不得以示意值/占位文案填空；**不得**把 `PRICING`(`待接入 PC3`)/`FAQ`(`待接入 PC4`) 改成空白（它们当前是**正确行为**：`pricingItems=0`、`faqs=0`）；不得改 P38 冻结文件、`specs/` 受控源、KERT 制品 |
| 验收（机械可验） | ① 8 章**逐一二选一**成立：有数据 ⇒ 该章正文非空且含接口该章首条内容；无数据 ⇒ 该章存在具名「待接入 <批次>」；② 抽样 ≥3 产品（`PROD-CM-003`/`PROD-SET-001`/`PROD-FIN-003`）逐章核；③ `npm --prefix frontend run check`（vue-tsc）0 错误；④ `npx --prefix frontend vitest run` 全绿 |
| 证据 | 逐章 JSON（结构同 `b4-per-chapter.json`）+ 每章截图 + 页面文本与接口响应比对 + trace |
| 关联 | 与 W-2 同批交付；`LOOP.yaml` exit_criteria「未实现章节呈现原文 + 相对来源 + 有效状态，**无空占位**」 |

### W-2 ·【P0 · 阻塞 · 本 loop】验收期望值改**语义**（QA-D-3）—— 禁止 `7 → 2`

| 项 | 内容 |
|---|---|
| 现象 | `frontend/e2e/product-center-pc1.spec.ts:53` 与 `frontend/src/views/__tests__/ProductCenterView.spec.ts:213` 硬编码 `pc-chapter-pending = 7`，实测 2 ⇒ 用例长期红 |
| 裁决 | **"期望值过期"与"产品缺陷"并存**：过期（后端仅 `PRICING`/`FAQ` 真未接入）**且**另 5 章是 W-1 的空壳 ⇒ 只改常量 = **把 5 个空壳锁进"通过"** |
| 动作 | 两处断言改为 **逐章二选一**（覆盖 8 章全量）：有数据 ⇒ 正文非空且与接口一致；无数据 ⇒ 具名 `待接入 <批次>`。**必须**在 W-1 完成之后同批提交 |
| **禁止** | 禁止 `7 → 2` 常量替换；禁止弱化（`toBeVisible`/仅 `toHaveCount(8)`）；禁止 `waitForTimeout` 掩盖竞态；禁止删用例 |
| 验收 | 两处用例全绿；`git diff` 中不存在常量替换式改动（评审判据）；`LOOP.yaml` gate `e2e_parity` 全绿 |

### W-3 ·【P1 · 非本 loop · 转派 + 待授权】跨页产品族名收敛（QA-D-2，7 例）

| 项 | 内容 |
|---|---|
| 裁决 | **成立但非新缺陷**：权威名**已由 Owner 裁决 OQ-B 定为「结算 / 贸易金融 / 融资」**（`specs/product-knowledge/product-taxonomy.yaml:19-26`，并已登记为 `CTR-PK-TAX-001` 已知差异 D-1，"产品卡侧对齐放 **PI-1**"） |
| 归属 | 漂移侧 = **KERT 产品卡 front matter**；修正点落在 `LOOP.yaml` 的 exclude（P38 冻结视图 / `specs/` 受控源 / **Leibniz-KERT 制品**）⇒ **本 loop 不施工，只登记** |
| 派往 | **PI-1**（KERT `examples/product-recommendation-assets/03_core/*/product-cards/` front matter 对齐裁决名）；**需 Owner 单独授权 KERT 侧改动** |
| 严重度 | 维持 P1（用户可见），**不阻塞发布**；TL 不降级、不撤项 |
| **禁止** | 前端硬编码族名别名（会形成第三份命名，违反 `CTR-PK-TAX-001` 权威关系） |
| 待补 | `INDEX_BASIS.md` 影响面 #8 未回源到单卡行号（记 `F-PC-i1-03`），PI-1 开工前须补 |

---

## 三、**未裁决 / 不派工**（保持 QA 原判定，另行裁决，不得顺手改）

| QA 项 | 状态 | 说明 |
|---|---|---|
| QA-D-4 | 测试脚手架漂移 | `*.live.spec.ts` 默认 `8082`/`8106` ≠ 现行 `18080`/`8107`；覆盖后 **12/12 PASS** ⇒ 非链路失效。改默认值或强制注入 env，**另行派工** |
| QA-D-5 | 待 Owner 裁决 | `/analytics/*` 4 条 `console.error`（浏览器对被调 API 503 的资源日志）。**A3 一律仍记 FAIL**，白名单未采用 |
| QA-D-6 | **BLOCKED（不得记 pass）** | `analytics.spec.ts` 4 条因 `ANALYTICS_UNAVAILABLE`（`KERT_ANALYTICS_DUCKDB` 未配）⇒ 环境未就绪，保持 BLOCKED |
| QA-F2 裸跑 9 条 | **BLOCKED（不得记 pass）** | 同上（D-4 具名原因） |
| QA-D-7 | 测试侧缺陷 | `customer-detail.spec.ts:21` locator 严格模式冲突；另行派工（收窄定位器） |
| QA-D-8 | 观察项 | C1/C2 文案未回显 `errorCode` 且回显内部端点 URL ⇒ 待 Owner 决定是否要求 |
| QA-G1 | 判 PASS 但抖动未查明 | 4 次复跑通过、1 次失败未复现；**不得**据 G1 推断"窄屏完全稳定" |

---

## 四、出口与门禁（`LOOP.yaml` gates，不得跳过）

| gate | 命令 | 通过条件 |
|---|---|---|
| `contract_generate` / `contract_check` | `make generate` / `make check` | 无占位/不支持构造；产物与权威源一致 |
| `security_check` | `make security-check` | 凭据/权限/隔离检查通过 |
| `frontend_typecheck` | `npm --prefix frontend run check` | `vue-tsc` 0 错误 |
| `frontend_unit` | `npx --prefix frontend vitest run` | 全绿（含章节继承断言） |
| `e2e_parity` | `npx --prefix frontend playwright test e2e/product-center-pc1.spec.ts` | 全绿（含 8 章落位断言） |

**出口状态**：`ready_for_independent_qa` / `blocked`。
**`QA_PASS` 只能由独立 QA 角色签发**；作者自检仅可为 `DEV_SELF_CHECK_PASS`。

---

## 五、通用禁令（违反即退回）

1. 不得削弱/删除 QA 断言，不得把 **BLOCKED** 当作 pass，不得以环境问题掩盖产品缺陷。
2. 不得改本单未列文件；不得改 `specs/` 受控源（须合同 Owner 签字）；不得改 P38 冻结文件；不得改 KERT 制品。
3. **未授权不得开工**：本单签字前，任何实现动作（含本地试改）均视为越权。

---

## 六、授权签字位（Owner）

```text
[x] 授权 W-1 + W-2 开工（本 loop）
[x] 同时授权 W-3 转 PI-1（需 KERT 侧改动授权）
[ ] 其他指示：__________________________________________

Owner 签字：Owner（授权原文：① 授权 W-1 + W-2 开工（本 loop）；② 同时授权 W-3 转 PI-1）
授权日期：2026-09-22
授权记录人：tech_lead
```

---

## 七、执行记录（TL · 2026-09-22，授权后）

### 7.1 W-1（P0 · D-1）已完成实现

| 项 | 事实 |
|---|---|
| 改动文件 | `frontend/src/components/product-center/ProductChapterStack.vue`（**新增 `v-else` 正文分支**：`TERMS`/`FIT`/`PROCESS`/`MATERIALS`/`COMPARE`，统一锚点 `data-testid="pc-chapter-body"`）、`frontend/src/api/productCenter.ts`（按契约新增 `Pkc*` 类型，替换原 `unknown[]`） |
| 附带修正 | `FIT` 的 `hasPayload` 由「仅 `boundaries`」扩为 **`boundaries ∪ prerequisites`**（消除"有前置条件却报未接入"的反向不诚实） |
| 内容口径 | 只按契约字段呈现；缺失项逐个显式「待核验」；无示意值、无硬编码业务内容 |
| **端到端证据** | `frontend/test-results/pc-i1-w1/evidence/evidence.json` + 3 张整页截图：`PROD-CM-003` / `PROD-SET-001` / `PROD-FIN-003` **各 8 章 0 违规**；`TERMS` 内容抽查 `present=true` |
| **QA 判据复跑** | `B3/B4/B5/B6/E1/G1` + `product-center-pc1` ⇒ **7/7 PASS**（`B4`/`E1` 此前为 **P0 FAIL**） |

### 7.2 W-2（P0 · D-3）已完成改写

| 项 | 事实 |
|---|---|
| 改动文件 | `frontend/e2e/product-center-pc1.spec.ts`（原 `:53`）、`frontend/src/views/__tests__/ProductCenterView.spec.ts`（原 `:213`） |
| 改法 | **逐章二选一**（有数据 ⇒ `pc-chapter-body` 可见 + 正文非空 + `pending` 为 0；无数据 ⇒ 反之）；判据取自接口事实，非常量 |
| 约束核实 | `git diff` **无 `7 → 2` 常量替换**；无断言弱化（无 `toBeVisible` 顶替、无 `waitForTimeout`） |
| 新增 | 单测「有契约数据的章节必须渲染正文（W-1 回归）」——夹具与既有相反（5 章有数据），直接锁住 D-1 反面 |

### 7.3 门禁结果（以 `EVIDENCE.json` 为准，**未粉饰**）

| gate | 状态 | 说明 |
|---|---|---|
| `contract_generate` | **pass** | `make generate` |
| `security_check` | **pass** | 334 条 advisory（非阻塞） |
| `frontend_typecheck` | **pass** | `vue-tsc` 0 错误 |
| `frontend_unit` | **fail** | 根因 = 门禁命令在**仓库根**执行（`npx --prefix frontend` 不改 cwd）⇒ vitest 把 `frontend/e2e/*.spec.ts` 当单测收集 + cwd 依赖用例 ENOENT（75 failed）。**等价复跑**（`cd frontend && npx vitest run`）= **366 passed**，证据 `evidence/frontend_unit-equiv-20260922T145854Z.log` |
| `e2e_parity` | **fail** | 根因 = 基线 webServer 起 5173，其 vite 代理默认 `8080`（401）≠ 被测 `18080`。**等价复跑**（QA 配置指 15173/18080）= **2 passed**，证据 `evidence/e2e_parity-equiv-20260922T145854Z.log` |
| `contract_check` | **fail** | 既存生成漂移（`changed=['manifest.json','product-knowl…]`，清单内**无 frontend 路径**）；`make generate` 前后工作树均 465+ 项既存脏文件 ⇒ **与本次改动无关**，但**不记为通过** |

> **出口状态不宣告**：3 道门禁为 `fail`（含 2 道"门禁命令/环境缺陷"），PC-i1 **不得**记 `ready_for_independent_qa` 之外的通过；`QA_PASS` 只能由独立 QA 角色签发。

### 7.4 新发现（本次执行中实测，需 Owner 决定是否修门禁定义）

| # | 问题 | 影响 | 建议（**未改 `LOOP.yaml`**） |
|---|---|---|---|
| `G-1` | 门禁命令 `npx --prefix frontend vitest run` 由 `record_gate.py` 在仓库根执行 ⇒ cwd 语义与收集范围均错 | `frontend_unit` 永远 fail（假红） | 改为 `bash -lc 'cd frontend && npx vitest run'`，或为 vitest 配 `root` + 排除 `e2e/**` |
| `G-2` | 门禁命令起的 5173 vite 代理指向 `8080`(401)，与被测后端 `18080` 不一致 | `e2e_parity` 假红 | 门禁命令注入 `VITE_API_PROXY_TARGET=http://127.0.0.1:18080`，或改用 QA 配置对已运行环境执行 |
| `F-PC-i1-03` | W-3 未回源到 KERT 单卡行号 | PI-1 开工前须补 | 已转派 `docs/dispatch/PI-1-派工-W3-族名收敛-2026-09-22.md` |

### 7.5 本次**未开工**（loop 其余目标，防误读）

P38 12 章逐一落位、C6（前置/互斥/替代/配套）与 C9（风险提示与人工复核）独立可见、C11 版本语义承载、
同产品对照三判定（事实不丢 / 来源可达 / 阅读更快）—— **全部未动**；本 loop **远未 complete**。


---

## 八、G-1 / G-2 门禁修复（Owner 2026-09-23 授权 · 执行记录）

> Owner 指示：「① 授权 G-1/G-2；② 把本次改动入仓」。本节追加，**不覆盖** §7 的原记录。

### 8.1 修复内容（`LOOP.yaml`，命令 + 修法依据一并登记）

| gate | 修前 | 修后 | 依据 |
|---|---|---|---|
| `frontend_unit` | `npx --prefix frontend vitest run` | **`cd frontend && npx vitest run`** | `record_gate.py` 以仓库根为 cwd 执行 ⇒ ① vitest 收集 `frontend/e2e/*.spec.ts`（Playwright 用例被当单测）② cwd 依赖用例 `ENOENT`（实测 75 failed）。`frontend/vitest.config.ts:11` 已 `exclude: ['e2e/**']`，在 frontend 目录执行即正确 |
| `e2e_parity` | `npx --prefix frontend playwright test e2e/product-center-pc1.spec.ts` | **`cd frontend && VITE_API_PROXY_TARGET=http://127.0.0.1:18080 npx playwright test e2e/product-center-pc1.spec.ts --output=test-results/gate-e2e-parity`** | ① cwd 同上；② `frontend/vite.config.ts:5` 的代理默认 `8080`（实测 401，非被测后端）⇒ 注入 `VITE_API_PROXY_TARGET`；③ Playwright 默认清理整个 `test-results`（当时 3233 文件 > 500 阈值）被 IDE safe-delete 批量保护拦截 ⇒ 显式独立 `--output`（与 QA 报告 §4.11 同源） |

### 8.2 复验（按新命令重新 `record_gate.py`）

| gate | 结果 |
|---|---|
| `frontend_unit` | **pass**（exit 0，证据 `evidence/frontend_unit-20260923T023039Z.log`） |
| `e2e_parity` | **pass**（exit 0） |
| `contract_check` | 仍 **fail**（既存生成漂移，与本次无关；未改） |

`EVIDENCE.json` 终态：`contract_generate` pass · `contract_check` **fail** · `security_check` pass · `frontend_typecheck` pass · `frontend_unit` **pass** · `e2e_parity` **pass**。

### 8.3 仍未解（**需 Owner 再裁一次**）：`F-PC-i1-04`

`loop-guard` 现仅剩 **1 个**命中文件：`evidence/frontend_unit-20260922T145816Z.log`（其第 556 行含失败输出所引的 Vue 源码插值，被 `reject_placeholders` 判为"未解析占位符"）。
- 本次已把**我方文档**中所有字面占位令牌清理为等价描述（`STATE.json` / `FAILURES.md` / `memory/INDEX_BASIS.md`）。
- **仍未**修改 `loop_guard.py`（改门禁 = 削弱门禁）、**仍未**删改该原始日志（改证据 = 失实）⇒ `loop-guard` 保持 **FAIL**，`--instances-check` 仍报 1 个不合规实例。
- 待授权修法：`R-1` 扫描跳过 `evidence/**`；`R-2` `record_gate.py` 把原始日志改落 `frontend/test-results/gates/**`（`EVIDENCE.json` 仍记路径 + sha256）。


---

## 九、按独立 QA 报告的更正与处置（2026-09-23T03:11:30+00:00）

> 独立 QA 报告：`loops/PC-i1-chapter-inheritance/evidence/independent-qa-pc-i1-20260923-1101.md`
> **总判**：W-1/W-2 **独立复验通过**（13/13 产品 × 8 章 = 104 章，二选一 0 违规）；**PC-i1 整体 BLOCKED，不得签 `QA_PASS`**。

| QA 发现 | 处置（本次） |
|---|---|
| `QA-1`【中】`FAILURES.md` 对 `contract_check` 的根因叙述与自身证据不符 | **已更正（append-only）**：`scripts/check-contracts.sh` ⇒ **PASS(exit 0)**；`make check` 的真实完整性失败项 = **`loop-instances`**（① `repro_baseline` 反向门禁，属 **`loops/GKB-baseline-hardening`**，非本 loop；② PC-i1 新增不合规实例 = `F-PC-i1-04`）。原叙述为本 TL 误判（只依据被截断输出推断），**不删改原记录**；`INDEX_BASIS.md` 同步更正 |
| `QA-2`【观察】gate id `contract_check` 名不副实（失败可能来自 `loop-instances`） | 已登记，**未改 gate 定义**（等 Owner 决定是否拆分/改名） |
| `QA-3`【低】`LOOP.yaml.status=planned` 与 `STATE.json=in_progress` 不一致 | **已改**：`LOOP.yaml.status = in_progress` 并加 `status_note` 说明依据 |
| `QA-4`【待确认】`loop_guard.py` / `record_gate.py` 存在**未提交**改动 | **已核实归属**：非本次引入 —— 本 TL 今日提交（`d4ad4a2`/`c69a24c`/`4e5e517`）**涉及 0 个 `scripts/` 路径**；两文件最近提交分别为 `be4b91b`(2026-09-13) 与 `c67ba0c`(2026-08-01) ⇒ 属**既存未提交改动**，来源与授权**请 Owner/收口确认** |
| `QA-5`【观察】单测 `fixtureHasPayload` 为手写常量表 | **已改**：改为**由夹具事实推导**（夹具变更不再误报） |

**仍未解（需 Owner 决策）**：
1. `F-PC-i1-04` 修法 **R-1 / R-2** 未获授权 ⇒ `loop-guard` 仍 FAIL、`--instances-check` 仍判 PC-i1 不合规（这也是 `make check` 完整性失败的第二条原因）；
2. **`loops/GKB-baseline-hardening` 的 `repro_baseline(expected_exit_code=1)`** 反向门禁 —— 非本 loop，需其归属人处置；
3. 独立 QA 为**非正式**（`qa_attest.py` 三条件均不满足，见 QA 报告 §四）⇒ 即使 1/2 解决，仍须由独立 actor 走正式签署。
