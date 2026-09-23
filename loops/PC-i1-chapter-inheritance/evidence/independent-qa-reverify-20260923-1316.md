# 独立 QA 复验报告 · PC-i1 · **QA-B1 / QA-B2 / QA-N1 整改闭合复验** · 含正式复签

| 项 | 值 |
|---|---|
| Loop | `loops/PC-i1-chapter-inheritance` |
| 复验对象 | TL 依 Owner 授权对上一轮 `reject`（QA-B1 阻断·中 / QA-B2 阻断·低 / QA-N1 非阻断）的**具名整改**：3 处渲染口径 + 三态可达性 + 测试侧反向断言，以及重记的 3 项门禁与 6/6 门禁自洽 |
| 分支 / HEAD | `recover/PI-ARCH-product-catalog` @ `652a23f09f5139261791d977958f2e2ebeac1c0f`（与上一轮 `reject` 报告所记 **同一 HEAD**；复验期未变） |
| 角色 / 会话 | `independent_qa` / `qa-pc-i1-reverify-20260923-1316`（**≠** `STATE.json.implementation_actor = tech_lead`） |
| 环境 | 15173（前端 dev，200）· 18080（后端，200）· 8107（KERT，404 响应=监听中）· 9621（307=监听中）· **8080 亦在监听且返回 401（非被测后端，收工前仍在）**；5173 **复验前后均无监听**（E2E 由 Playwright 自起自收） |
| 只读声明 | 未改 `frontend/src/**`、`frontend/e2e/**`、`apps/**`、`scenario/**`、`scripts/**`、`specs/**`、`generated/**`；未改任何既有 `loops/**` 文件；未 `git add`/commit/push；未对 8107/9621 发写请求 |
| 判据来源 | ① 接口事实 `GET /api/v1/product-center/products` 与 `GET /api/v1/product-knowledge/cards/{id}`（经 15173 → 18080 真实链路）**独立推导期望值**；② 真实页面 DOM（**我自有探针**，仅失败注入 `route.abort`，**零假数据**）；③ 上一轮 QA 自有探针（**只读运行**，文件 sha256 复核未变） |
| 签署结论 | **PASS**（`qa_attest.py --decision pass`，见 §四） |

---

## 〇、前置自检（逐条，均通过 ⇒ 不记 BLOCKED）

```text
STATE.status        = ready_for_independent_qa   （期望一致）
STATE.qa_actor      = independent_qa             （期望一致）
STATE.blocked       = false / current_phase = awaiting_re_attest_after_QA_B1_B2_N1_fix
6/6 gate            = pass  且 command 与 LOOP.yaml **逐字一致 6/6**、evidence sha256 **6/6 一致**（程序化比对，非目测）
loop_guard --loop PC-i1-chapter-inheritance = PASS（exit 0）
loop_guard --instances-check                = 合规 69 / 69，不合规 0，基线冻结 0，**无新增违规**
ROLE_BOARD.baton.holder = independent_qa == NEXT_SESSION.md holder = independent_qa
环境                = 15173 = 200 · 18080 = 200 · 8107 = 404(监听) · 9621 = 307(监听)
EVIDENCE.json.independent_qa（签署前） = reject / actor=independent_qa / session=qa-pc-i1-formal-20260923-1227
  ⇒ 上一轮 REJECT 仍**原样在场**（§一 覆盖声明）
```

---

## 一、总判：**PASS —— 可以签发 `QA_PASS`**

| 复验项 | 结论 | 依据 |
|---|---|---|
| **V-B1**（阻断·中）登记章号 vs 实际节号未分离 | **闭合** | §二 V-B1：13 产品 × 7 章 = **91 章** head/meta 判据 **0 违规**（期望值由接口独立推导）；版本区（C11）13/13 正确；且**同一判据回放到修前制品即判红（20 违规）** ⇒ 判据非空转 |
| **V-B2**（阻断·低）缺失归因不实 | **闭合** | §二 V-B2：13/13 卡故障注入 `findings` **空**；且含**正向对照**（3 张 FIN 卡无注入时原文确实渲染）⇒ 「原文消失」可归因于中断；判据回放修前 **判红（10 违规）** |
| **V-N1**（非阻断·测试侧） | **闭合** | §二 V-N1：变异复验 **baseline 全绿 / 3 组变异全部判红**（含 `expected '12. EvidenceRef' to contain '卡内第 11 节'`、`expected 12 to be null`） ⇒ 新断言确有判红能力 |
| **V-G** 门禁证据自洽 | **通过** | §二 V-G：6/6 命令逐字一致、6/6 哈希一致、3 份重记日志与其登记结论逐项相符；且 **3 项门禁由我独立复跑复现**（69 文件/379 tests、4 passed、0 TS 错误） |
| **V-H** 诚实性 | **通过** | §二 V-H：`reject` 未被改写；3 条失败登记**先于**整改（mtime 12:55:13 < 首次源码改动 12:55:39）；`NOT MET` / `INCONCLUSIVE` 如实保留；D-15 纪元口径如实 |
| **V-R** 不得回退 | **通过** | §二 V-R：`findCardSection` 定位（标题优先、节号前缀兜底）**未被改动**；`pc-inherited-c12-content` 绑 §11、`pc-immutable-source` 绑 §12（独立复算） |
| **V-C** 基线口径 | **如实登记**，不计入本轮缺陷 | §二 V-C：`generated/` 2 文件漂移 + 工作树混入非本 loop 在飞改动 ⇒ **门禁结论只对当时工作树成立** |

### 覆盖声明（协议内复签，非篡改；必读）

`qa_attest.py` 的设计是：一旦本次签署为 `pass`，即以本次结果**覆盖** `EVIDENCE.json.independent_qa`。据此我显式声明：

1. 上一轮 `reject` 的结论与其证据文件**未被改动、仍可追溯**：`evidence/independent-qa-formal-20260923-1227.md` sha256 复算 = `766cb36d2d3853d23685b0edf407b51f69c499e63102314c5cb7548f7e6530be`，与 `EVIDENCE.json` 登记值及上一轮报告所述**完全一致**；`…-ADDENDUM-01.md`、4 支探针、3 份变异 JSON、2 份门禁日志等 `independent-qa-*` 全部在场，本会话**只读**。
2. `FAILURES.md` 中 QA-B1/QA-B2/QA-N1 三条登记**未被删除或改写**（append-only），本轮结论**新增**于本报告，不覆盖原记录。
3. 本次覆盖是**协议内规定的正式复签动作**，是对整改结果的新结论，不表示上一轮判定为误判。
4. 我对 `EVIDENCE.json` / `STATE.json` / `NEXT_SESSION.md` / `ROLE_BOARD.yaml` **未做任何手工编辑**；其变更**只**来自 §四 的 `qa_attest.py` 执行。

---

## 二、复验矩阵（逐项：预期 / 实际 / 证据 / 严重度 / 结论）

### V-B1 阻断项闭合 —— 「章节标题」与 meta 节号自洽（`PASS`）

**方法（刻意不复用上一轮探针的判定逻辑）**：我另写自有 oracle `probe-reverify-heading.mjs` + 共用规则引擎 `rules-heading.mjs`，**期望值由接口 `sections[].title` 独立推导**（章标题关键字为唯一语义锚；登记章号 = `C<n>` 的 n），再与真实 DOM 比对。判据包含：命中该节 ⇒ 标题必须含「（卡内第 N 节）」且**标题内不得残留任何 `<N>.`**、meta 必须写实际节号、content 必须与该节原文一致；未命中 ⇒ 标题/meta **不得出现任何数字节号**、meta 必须写「本卡未含该节 · R2 章号 Cx」、缺失文案不得写「未包含第 N 节」。

| 子项 | 预期 | 实际 | 结论 |
|---|---|---|---|
| 我自有 oracle 全量（13 产品 × 7 章 = **91 章** + C11 × 13） | 0 违规 | **violationCount = 0**（exit 0） | **通过** |
| `PROD-FIN-003` / `PROD-FIN-001` 的 C12 标题 | 含「卡内第 11 节」，不含 `12.` | `EvidenceRef （卡内第 11 节） C12原文` | **通过** |
| `PROD-CM-003` / `PROD-IB-001`（本无该节）标题 | 不出现数字节号 | `EvidenceRef C12`（数字节号 0 处；`C12` 为 R2 章号 tag） | **通过** |
| 同块 meta 与标题自洽（FIN 卡） | meta=「（第 11 节）」 | `…（第 11 节）…`，无「12.」并列 | **通过** |
| 未命中卡 meta 口径 | 「本卡未含该节 · R2 章号 C12」 | `…（本卡未含该节 · R2 章号 C12）…` | **通过** |
| 上一轮 QA 自有探针（**只读运行，原样命令**） | FIN head 含「卡内第 11 节」、无 `^(12\.)`；CM/IB 无数字节号 | 与上表逐字一致（`/tmp/qa2-after`） | **通过** |
| **非空转证明**（同一规则引擎回放修前制品） | 修前必须判红 | **20 违规**（`HEAD_HAS_NUMERIC_NO:C12`、`HEAD_NO_MISSING:C12`、`META_CLAIMS_SECTION_NO:C12`…，落在 `PROD-FIN-001/002/003`） | **通过** |

**覆盖声明（诚实性）**：`rules-heading.mjs` 只在 live 探针与回放脚本之间共用，**未进入任何仓内产品/测试代码路径**；回放用的「C11 版本区 source」字段在历史制品中不存在，故回放**只覆盖 c2/c3/c6/c8/c9/c10/c12 的 head/meta 判据**，C11 仅由 live 判据覆盖（已在脚本内注释）。

> 代码回源（本轮新增，供收口）：
> `frontend/src/components/product-center/ProductInheritedChapters.vue:120-129`（标题：章节标题 + `v-if="block.sectionNo !== null"` 才标「卡内第 N 节」，R2 章号由 `n-tag` 承载）
> `…:68-80 sectionNoLabel()`（实际节号 / 来源不可得 ⇒「节号不可判」/ 加载中 ⇒「节号待判」/ 未含 ⇒「本卡未含该节 · R2 章号 Cx」）
> `frontend/src/utils/cardChapter.ts:80-86 actualSectionNo()`（未命中 **返回 `null`**，不再回落登记值）

### V-B2 阻断项闭合 —— 卡接口不可达时不得并列矛盾表述（`PASS`）

**方法**：我另写 `probe-reverify-faultcard.mjs` + `rules-fault.mjs`，与上一轮探针的**差异是刻意的**：① 含**正向对照**（同一产品、同一浏览器、**不注入失败**先确证原文确实渲染 ⇒ 之后「消失」才可归因于中断）；② **抽样全部 13 张卡**，而非仅 1 张；③ 判据含标题侧（来源不可得时标题亦不得标节号）。

| 子项 | 预期 | 实际 | 结论 |
|---|---|---|---|
| `findings`（13/13 卡，卡片接口 `route.abort`） | 空 | **violationCount = 0**（exit 0） | **通过** |
| 上一轮 QA 自有探针（只读，`PROD-FIN-003`） | `findings` 空、`CONTENT_DESPITE_ABORT`=0、C10 合同字段仍在 | `findings: []`、`abortedRequests=2`、`c12content=null`、`immContent=null`、`c10contract` 非空 | **通过** |
| 承接区 meta（故障态） | 「来源标识不可得」+ 节号不可判 | `…｜来源：来源标识不可得 （来源不可得 · 节号不可判）｜…` | **通过** |
| 承接区缺失文案（故障态，`PROD-FIN-003`） | 不得写「未包含第 N 节」 | `产品卡来源不可得 ⇒ 无法判定该卡是否包含「EvidenceRef」节（R2 章号 C12）原文 —— …` | **通过** |
| 版本区缺失文案（故障态） | 去写死节号 + 不判定 | `产品卡来源不可得 ⇒ 无法判定该卡是否包含「不可变版本语义」节（R2 章号 C11）原文 —— …` | **通过** |
| 标题（故障态） | 不得标卡内节号 | `c6head=前置、互斥、替代与配套产品`、`c12head=EvidenceRef`（0 处数字节号） | **通过** |
| **正向对照**（无注入） | 接口表明有该节的卡必须渲染原文 | 3 张 FIN 卡 `ctrlC12=有原文`（如 `\| ref_id \| source_id …`）· 13/13 `ctrlImm=有原文`；无该节的 10 张卡两态一致为「无」 | **通过**（对照有效，非空转） |
| **非空转证明**（同一规则引擎回放修前故障制品） | 修前必须判红 | **10 违规**（`ABSENT_STATES_SECTION_NO:c6/c12`、`META_CLAIMS_SECTION_NO:c12`…） | **通过** |
| 无关接口连带影响 | C10 合同字段不得受影响 | 13/13 故障态 `pc-inherited-c10-contract` 仍在 | **通过** |

> 代码回源：`frontend/src/views/ProductCenterView.vue:60`（`cardState` 三态）· `:70-84 loadCardDetail()`（`ready/unavailable`）· `ProductInheritedChapters.vue:86-94 absentText()` · `ProductGovernancePanel.vue:34-46 immutableAbsentText()`

### V-N1 防回归断言可信 —— 变异复验（`PASS`）

**方法**：**只在 `frontend/test-results/qa-reverify-pci1-20260923/mutant/`（gitignored，我自有输出区）** 复制组件/工具/用例，仅改动副本中的目标行（生成器 `make-mutants.py` 对所有锚点做**存在性断言**，锚点缺失即 FATAL ⇒ 禁止盲改），用我自有的 `vitest.mutant.config.ts` 运行；**仓内 `frontend/src/**` 零改动**。

副本文件名刻意用 `.check.ts`（非 `*.spec.ts`），**以免被仓内 `npx vitest run` 的默认收集规则纳入** —— 独立 QA 制品不得影响被验门禁命令的判定（首轮实验曾因命名不当被仓内收集，已即时修正并复跑验证，见 §五 #6）。

| 副本组 | 变异内容（复现修前语义） | 预期 | 实测 | 结论 |
|---|---|---|---|---|
| `baseline` | 无（原样副本） | 全绿 | **2 文件 / 11 tests passed，exit 0** | 夹具/环境有效 |
| `mutant-B1` | 标题回退为 `{{ spec.no }}. {{ spec.title }}` | 判红 | **1 failed**：`AssertionError: expected '12. EvidenceRef' to contain '卡内第 11 节'`（用例「FIN 卡节号错位…」） | **新断言可判红** |
| `mutant-B2` | 缺失文案恒写「该产品卡未包含第 `<登记章号>` 节」且节号回落登记值 | 判红 | **2 failed**：`to contain 'R2 章号 C12'`、`to contain '无法判定'`（用例「定位不到该节…」「来源不可得…QA-B2」） | **新断言可判红** |
| `mutant-util` | `actualSectionNo()` 未命中回落 `_spec.no` | 判红 | **3 failed**：`expected 12 to be null` + 2 条组件级（`to contain '本卡未含该节'`、`to contain '来源不可得 · 节号不可判'`） | **新断言可判红** |

**结论**：QA-N1 所指「QA-B1 / QA-B2 类缺陷在既有断言下不可见」的缺口**已闭合**；新断言在修前语义下**确实判红**，非空转。

### V-G 门禁证据自洽（`PASS`）

| 检查 | 预期 | 实际 |
|---|---|---|
| `EVIDENCE.json.gates[*].command` vs `LOOP.yaml.gates[*].command` | 6/6 逐字一致 | **6/6 `True`**（程序化比对：`contract_generate` / `contract_check` / `security_check` / `frontend_typecheck` / `frontend_unit` / `e2e_parity`） |
| 每个 `evidence_file` 重算 sha256 == `output_sha256` | 6/6 | **6/6 `True`**（含 `frontend_typecheck-20260923T045732Z.log` `b3662785…`、`frontend_unit-20260923T045737Z.log` `9fd3aced…`、`e2e_parity-20260923T045752Z.log` `171d588a…`） |
| `frontend_unit-20260923T045737Z.log` 内容 | 69 文件 / 379 tests、exit 0 | `COMMAND=cd frontend && npx vitest run` · `EXIT_CODE=0` · `Test Files 69 passed (69)` · `Tests 379 passed (379)` · 日志内 `failed` 计数 = **0** |
| `e2e_parity-20260923T045752Z.log` 内容 | 4 passed、exit 0 | `EXIT_CODE=0` · 4 个用例 ✓（含新增「章级承接：FIN 卡节号错位不得错配…」「故障路径：产品卡接口不可达 ⇒ 缺失归因如实…」）· `4 passed (6.6s)` |
| `frontend_typecheck-20260923T045732Z.log` 内容 | 0 TS 错误、exit 0 | `EXIT_CODE=0` · `vue-tsc --noEmit` · STDOUT 无错误行 |
| **独立复跑**（不引用实现者结论） | 与登记一致 | ① `cd frontend && npx vitest run` ⇒ **69 passed (69) / 379 passed (379)**，exit 0；② `npm --prefix frontend run check` ⇒ exit 0（无错误）；③ `VITE_API_PROXY_TARGET=http://127.0.0.1:18080 npx playwright test e2e/product-center-pc1.spec.ts --output=<我自有目录>` ⇒ **4 passed**，exit 0；④ `make check` ⇒ exit 0，`[PASS] contract-check` / `[PASS] loop-instances` / `[PASS] loop-guard` |
| `fixed` 与门禁时序 | 门禁晚于整改 | 末次源码改动 **12:56:17** < 门禁执行 **12:57:32–12:57:52**（mtime 实测） |

### V-H 诚实性（`PASS`）

| 检查 | 预期 | 实际 |
|---|---|---|
| 签署前 `EVIDENCE.json.independent_qa` | 仍为 `reject` | **`reject`**（`actor=independent_qa`、`session=qa-pc-i1-formal-20260923-1227`、`attested_at=2026-09-23T04:29:40Z`、`evidence_sha256=766cb36d…be`）；主报告文件 sha256 复算一致 |
| `FAILURES.md` 3 条是否**在修改之前**登记 | 是 | **是**（文件 mtime `12:55:13` **早于**首次源码改动 `cardChapter.ts` `12:55:39`、组件 `12:55:47/49`、视图 `12:56:04`、测试 `12:55:39–12:56:17`；门禁日志 `12:57:48`）⇒ `record_before_fix` 满足 |
| 既有独立 QA 产物未被删改 | 7 个哈希一致 | 与 `EVIDENCE.md`「独立 QA — 导航」逐条一致（`8acc36c9…` / `d59a0109…` / `484e7f28…` / `e50897bc…` / `9c08acee…` / `ac5fcf70…` / `a097d558…`） |
| `semantic-consumption` / `gate-injection-tests` 是否被粉饰 | 仍如实保留 | **保留**：我独立复跑 `make check` ⇒ `22/23`、`[FAIL] semantic-consumption … NOT_MET`、`⚠️ INCONCLUSIVE（不得计为通过）：['gate-injection-tests']`、`READINESS NOT MET: ['semantic-consumption']` —— 与实现者自述完全一致，**未被改写为 pass** |
| D-15 纪元口径（`NEXT_SESSION.md §13.4`） | 如实声明「记入 epoch 1 而非新开纪元」 | **如实**：`memory/waves/W0-ITER.md` 显示 epoch 1 内 `frontend_typecheck` Attempt 2（045732）、`frontend_unit` **Attempt 3**（045737）、`e2e_parity` Attempt 2（045752）—— 与 §13.4 声明**逐条一致**；未见手工改写纪元头 |
| 整改自述（§13.1–13.3）与实测一致性 | 逐条可核 | 逐条核对**一致**（标题形态、meta 口径、缺失文案去写死、三态、69/379、4 passed、修前/修后对照） |
| 是否代签 / 是否自行提升状态 | 均未 | 未：`EVIDENCE.json.independent_qa` 由 `reject` 至今仍 `reject`（签署前），`STATE.status=ready_for_independent_qa`（非 `qa_pass`），无 `QA_PASS` 字样 |

### V-R 不得回退（`PASS`）

| 子项 | 预期 | 实际 |
|---|---|---|
| `cardChapter.ts` 定位策略 | 「标题优先、节号前缀兜底」**未被改坏** | `findCardSection()` 的 diff **仅注释**，`find` 两段式逻辑逐字未变（`section.title.includes(spec.title)` 优先，`startsWith(\`${spec.no}.\`)` 兜底）；本轮真正改动只有 `actualSectionNo()` 的 `spec.no → null`（+ `number \| null` 签名） |
| `pc-inherited-c12-content` 绑定 | 必须绑 §11 EvidenceRef | **绑 §11**：独立复算 content 前缀 == 接口中 `11. EvidenceRef（源文件与条款定位）` 的 content（13/13 章节 content 判据 0 违规）；FIN 卡渲染出 `\| ref_id \| source_id …` |
| `pc-immutable-source` / `-content` 绑定 | 必须绑 §12 不可变版本语义 | **绑 §12**：`source` 含实际标题 `12. 不可变版本语义`、`content` 前缀与该节原文一致（my probe `IMM_*` 判据 0 违规） |
| 断言删除审查（是否放宽） | 只能替换/加强 | 单测被删的 3 行**均为替换**：`exists()` 提取为变量；`toContain('未包含第 12 节')`（**即缺陷语义**）→ 换为 `not.toMatch(/未包含第\s*\d+\s*节/)` + `toContain('R2 章号 C12')`（加强）；`toBe(12)` → `toBeNull()`（纠正）。**无** `.skip/.only/.todo` 新增 |

### V-C 基线口径（如实登记，**不归因本轮整改**）

| 事实 | 说明 |
|---|---|
| `generated/` 漂移 **2 文件** | `generated/manifest.json`（+2/−2）· `generated/product-knowledge/field-policy.schema.json`（+395） |
| 工作树规模 | `git status --short` = **489 条**（上一轮 `reject` 报告记为 455），其中含 **另一 loop（AN0）在飞**的 `App.vue`/`theme.css`/`AppSidebar`/`navConfig`/`router/index.ts` 等未提交改动 |
| 口径 | `EVIDENCE.json` **未绑定被测 tree hash** ⇒ **门禁结论只对当时工作树成立**；该漂移与 AN0 在飞改动**属既有基线问题、非 PC-i1 交付缺陷**，本报告**不**将其归因于本轮整改。旁证：我复跑 `npx vitest run`、`vue-tsc`、E2E、`make check` 四项结果与门禁登记一致 |

---

## 三、缺陷清单

**本轮未发现新的阻断缺陷。** 遗留登记如下（**均非阻断，不影响 `QA_PASS`**）：

| # | 项 | 级别 | 事实与最小复现 | 建议 |
|---|---|---|---|---|
| O-1 | `EVIDENCE.md` 的「独立 QA — 导航」段仍写「`EVIDENCE.json.independent_qa` 仍为 `pending`」 | 观察·低（文档陈旧） | `loops/PC-i1-chapter-inheritance/EVIDENCE.md:13`。实际为 `reject`（本轮后为 `pass`）。该行本身声明「状态以 `EVIDENCE.json`/`STATE.json` 为准」⇒ **不产生错误判定**，但字面已过期 | 由实现侧 append 一行更正（独立 QA 不改他人文件） |
| O-2 | `NEXT_SESSION.md` §七「未开工」表与 §十二「已完成」措辞相反（W1-d/e/g） | 观察·很低（时序追加所致） | 文件按回合 append，§七 写于其未开工时、§十二 为后续回合；**门禁与状态机不受影响** | 收口时点明「§七 为历史时点」，避免后续读者误读 |
| O-3 | `R-2`（干净检出复跑 / 门禁绑定 tree hash）未做 | 观察（既存欠账） | `NEXT_SESSION.md §13.5` 已如实登记为「未做」；本报告 §二 V-C 同口径 | 收口时裁决；本轮我以「7 个被测文件 sha256 + HEAD `652a23f0` + 3 项独立复跑」部分弥补 |
| O-4 | `semantic-consumption = NOT MET`、`gate-injection-tests = INCONCLUSIVE` 未关闭 | 就绪度（非完整性失败） | 我复跑 `make check` 复现同结论；`make check` 自身明写不得计为通过 | 归口至相应 loop/Owner，不得在汇报中计为通过 |

---

## 四、签署（逐字执行）

```bash
python3 scripts/qa_attest.py --loop PC-i1-chapter-inheritance \
  --actor independent_qa --session qa-pc-i1-reverify-20260923-1316 --decision pass \
  --evidence loops/PC-i1-chapter-inheritance/evidence/independent-qa-reverify-20260923-1316.md
```

- `--actor = independent_qa`（**≠** `implementation_actor = tech_lead`）⇒ 未代签。
- 前置（§〇）均已满足；`loop_guard --evidence-only` 类前置由脚本自检。
- 结果（预期）：`EVIDENCE.json.independent_qa.status = pass`、`STATE.json.status = qa_pass`。§一 已声明该覆盖为**协议内正式复签**，上一轮 `reject` 及其证据仍可追溯（sha256 `766cb36d…be`）。

---

## 五、未覆盖 / 存疑（**必填**）

1. **`cardState = loading` 分支未由真实页面观测**：dev server 本地响应过快，故障注入只产生 `unavailable`；`loading` 仅由单测覆盖（组件默认值与分支），**未由真实网络慢速场景验证**。
2. **「卡读到但确无该节」的 C11 分支（`pc-immutable-absent` 且 `ready`）无真实数据**：13/13 卡均含「不可变版本语义」节 ⇒ 该分支只由代码/单测覆盖。
3. **C10「`salesBoundaries` 为空」分支仍无真实数据**（13/13 非空，2–3 条）；沿用上一轮结论，未改判。
4. **未做逐条事实等价比对**：仍只核到「落点/来源/字段/节号一致性」，**未**把 P38 每节文本与新版逐条对照 ⇒ 「事实等价」层面仍未知（与上一轮、与 `W1-g` 自述一致）。
5. **历史制品回放的可信前提**：`frontend/test-results/qa-fix-pci1-20260923/{before,after}/` 系实现侧运行**上一轮 QA 自有探针**所得（该探针文件 sha256 复核未变 `e7fa5921…`/`d1fc06d8…`），其 `before` 内容与上一轮 QA 正本**逐字一致**、且 `before` 目录 mtime（12:54）**早于**整改（12:55:39）⇒ 我判定其可比；但我**未能**独立证明其采集过程无中途改动（属间接证据）。
6. **我自己的实验曾一度污染仓内测试收集（已即时修正，如实登记）**：首轮变异副本命名为 `*.spec.ts` 且位于 `frontend/test-results/` 下，被仓内 `npx vitest run` 默认收集 ⇒ 该次全量运行得 `4 failed | 73 passed (77)`（4 个失败**全部**为我自己的变异副本，原 69 文件全绿）；我已把副本改名为 `*.check.ts`（非仓内收集模式）并**复跑确认** `69 passed (69) / 379 passed (379)`。⇒ 不影响门禁结论，且说明「QA 制品命名不得进入被验门禁的收集范围」。
7. **门禁证据未绑定 tree hash + 工作树 489 条脏改动（含 AN0 在飞）**：见 §二 V-C，结论只对当时工作树成立。
8. **未评估**：`PRICING`(PC3)/`FAQ`(PC4) 未来有数据时的渲染；生产构建（`vite build`）；LightRAG(9621) 检索质量（只读、未 publish/retract）；KERT(8107) 一切写操作（未做）。
9. **未重新裁定**既有 7 条历史失败（`analytics`×4 / `A3` / `D1` / `customer-detail`），沿用原归属，与本轮判据无关。
10. **`repro_baseline` 反向门禁、`semantic-consumption` / `gate-injection-tests` 判定口径本身**：我只核到「已如实声明、未被计为通过」，**未**评估其判定合理性。
11. **本轮未重记 `contract_generate` / `security_check`**（实现侧声明「前端改动不影响其结论」）；我仅核验其证据 sha256 与命令一致，**未**复跑（`make generate` 会写制品，超出只读边界）。

---

## 六、环境变动登记（只读复验；写入仅限 QA 自有产物区）

| 类别 | 明细 |
|---|---|
| 只读 | 13 产品页面 × 3 轮（自有 heading 探针 / 自有 fault 探针的对照+故障两阶段）· `PROD-FIN-003`/`PROD-CM-003`/`PROD-FIN-001`/`PROD-IB-001`（上一轮探针只读运行）· 接口 `GET /api/v1/product-center/products`、`GET /api/v1/product-knowledge/cards/{id}` · 门禁 `make check`、`loop_guard.py`（默认 / `--instances-check`）、`npx vitest run`、`npm --prefix frontend run check`、`npx playwright test`（自建 `--output`） |
| 写入（**均在 QA 自留区**） | `frontend/test-results/qa-reverify-pci1-20260923/**`（我自有探针 + 规则引擎 + 变异夹具 + `e2e-out/`）· `/tmp/qa2-after/**` · `/tmp/qa2-reverify/**` |
| 新增入 loop evidence（**仅 append-only 新增**） | 本报告 + 17 个 `independent-qa-reverify-*` 产物（sha256 见 §七） |
| 端口/进程 | Playwright 自起自收 webServer(5173)：复验结束**无 5173 监听**；15173 / 18080 全程未重启；**未触碰 8080**（非被测服务仍在监听，返回 401） |
| 未做 | 未改任何产品代码 / 测试断言 / 门禁脚本 / `specs/` / `generated/` / 既有 `loops/**` · 未 `git add`/commit/push · 未动 LightRAG / KERT · 未手工编辑 `EVIDENCE.json` / `STATE.json` / `NEXT_SESSION.md`（其变更**只**由 `qa_attest.py` 产生） |

---

## 七、原始产物索引

**被测制品指纹（复验期未变，供收口绑定）**

```text
HEAD = 652a23f09f5139261791d977958f2e2ebeac1c0f
66cb9fda3d68d3a7b2fed523d8de7ce131c614ee11d798960b6e21b0a43faf94  frontend/src/utils/cardChapter.ts
32bc6d6d818a017eb3726415299bd09a3d9649b56136048d583530ae61d318fc  frontend/src/components/product-center/ProductInheritedChapters.vue
823ebe44edb31706bc8db1388cb118e976d727c8b2ba2ecde57eadbbe9a843fd  frontend/src/components/product-center/ProductGovernancePanel.vue
de43d4a4b4dea7c5cc7703298306c211ac862bf22427cfe558c51ed29c433d3b  frontend/src/views/ProductCenterView.vue
92398acff06afe29d30f44763c8fe1f2778b049b80932b11f8ac55e823b27de1  frontend/src/utils/__tests__/cardChapter.spec.ts
f74b6fa898443a365acece016f6528619235fcdc39f05d9fa326019e2c0cee34  frontend/src/components/product-center/__tests__/ProductInheritedChapters.spec.ts
b4234b0b0afe2d7d722fc966d58d3c6ebe62d2cd0ec0c55b7e3407a70c936ddb  frontend/e2e/product-center-pc1.spec.ts
```

| 产物（`loops/PC-i1-chapter-inheritance/evidence/`） | sha256（前 16） | 说明 |
|---|---|---|
| `independent-qa-reverify-20260923-1316.md` | 见 `EVIDENCE.json.independent_qa.evidence_sha256`（签署时登记） | 本报告（签署正本） |
| `independent-qa-reverify-probe-heading.json` | `3e0e53ccfcad88a6` | **V-B1 主证据**：13 产品 × 7 章 = 91 章 head/meta 判据 + C11，`violationCount=0` |
| `independent-qa-reverify-probe-faultcard.json` | `e653cdfe5b6ac16d` | **V-B2 主证据**：13 卡正向对照 + 故障注入，`violationCount=0` |
| `independent-qa-reverify-replay-history.json` | `9a75112561c00b12` | **非空转证明**：修前 3 源判红（heading 20 / fault 10）、修后 2 源判绿，`MISMATCH=0` |
| `independent-qa-reverify-probe-heading.mjs` | `22ba05194873a565` | 自有 heading 探针（期望值由接口推导） |
| `independent-qa-reverify-rules-heading.mjs` | `db562316a109bb62` | 共用 V-B1 判据规则引擎 |
| `independent-qa-reverify-probe-faultcard.mjs` | `81ce8e0e3eeba8ce` | 自有 fault 探针（含正向对照） |
| `independent-qa-reverify-rules-fault.mjs` | `6281b78c4961ee5a` | 共用 V-B2 判据规则引擎 |
| `independent-qa-reverify-replay-history.mjs` | `3a8b110843b20b46` | 修前/修后回放脚本 |
| `independent-qa-reverify-make-mutants.py` | `ab900a08cc401fbd` | **V-N1 变异夹具生成器**（锚点缺失即 FATAL） |
| `independent-qa-reverify-vitest-baseline.log` | `0092d12df362fb9a` | 变异复验 基线：2 文件 / 11 tests **passed** |
| `independent-qa-reverify-vitest-mutant-B1.log` | `18b6633f3c7f1bb9` | 变异 B1：**1 failed**（`'12. EvidenceRef'` 不含 `卡内第 11 节`） |
| `independent-qa-reverify-vitest-mutant-B2.log` | `f12a74d4dbbaca35` | 变异 B2：**2 failed** |
| `independent-qa-reverify-vitest-mutant-util.log` | `a929cb0024d0429f` | 变异 util：**3 failed**（`expected 12 to be null`） |
| `independent-qa-reverify-vitest-full.log` | `0c920f8144e1c891` | 我独立复跑仓内单测：**69 passed (69) / 379 passed (379)** |
| `independent-qa-reverify-typecheck.log` | `91806f686a2e32c0` | 我独立复跑 `npm --prefix frontend run check`：exit 0 |
| `independent-qa-reverify-playwright-pc1.log` | `bb8e86c596eca0df` | 我独立复跑 E2E 门禁命令：**4 passed** |
| `independent-qa-reverify-make-check.log` | `791a53227088fb08` | 我独立复跑 `make check`：22/23、`NOT_MET` / `INCONCLUSIVE` 如实保留 |
| 只读引用（**未改**） | — | `independent-qa-formal-20260923-1227{,-ADDENDUM-01}.md` · 4 支上一轮探针 + 其 JSON · 3 份变异 JSON · `EVIDENCE.json` · `LOOP.yaml` · `memory/NEXT_SESSION.md` · `memory/waves/W0-ITER.md` · `memory/ROLE_BOARD.yaml` · `FAILURES.md` |
| 临时文件（未入仓） | — | `/tmp/qa2-after/**`、`/tmp/qa2-reverify/**`（探针 JSON/日志副本） |

---

## 八、一句话结论

**PC-i1 本轮可签发 `QA_PASS`（`--decision pass`）**：上一轮 `reject` 的 2 项阻断**已闭合并经我独立复验** —— **QA-B1**（「登记章号 vs 实际节号」未分离）在我自有的接口推导 oracle 下，13 产品 × 7 章 = 91 章 head/meta 判据 **0 违规**、C11 版本区 13/13 正确，且**同一判据回放到修前制品即判红（20 违规）** ⇒ 判据非空转；**QA-B2**（缺失归因不实）在含**正向对照**的故障注入下 13/13 卡 `findings` 为空、无原文幻觉、C10 合同字段不受连带影响（回放修前判红 10 违规）；**QA-N1** 经**变异复验**证明新断言可判红（3 组变异全红 / 基线全绿，含 `expected 12 to be null`）；**V-G** 6/6 命令逐字一致 + 6/6 哈希一致 + 3 项门禁我独立复跑复现（69 文件/379 tests、4 passed、0 TS 错误）；**V-H** 诚实性成立（`reject` 未被改写、3 条失败登记先于整改、`NOT MET`/`INCONCLUSIVE` 如实保留、D-15 纪元声明与 `W0-ITER.md` 一致）；**V-R** 无回退（定位逻辑未变、C12↔§11、C11↔§12 绑定正确，无 `.skip/.only`、无放宽断言）；**V-C** 如实登记为「`generated/` 2 文件漂移 + 工作树混入 AN0 在飞改动属既有基线问题」，**门禁结论只对当时工作树成立**。**未满足项：无阻断项**；仅 4 项非阻断遗留（O-1 `EVIDENCE.md` 导航行陈旧、O-2 `NEXT_SESSION §七/§十二` 时序措辞、O-3 `R-2`/tree-hash 绑定未做、O-4 `semantic-consumption` 与 `gate-injection-tests` 未关闭）与 §五 11 项未覆盖/存疑，**均不构成 `QA_PASS` 的阻碍**。
