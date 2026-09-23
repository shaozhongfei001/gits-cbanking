# 独立 QA 复验报告 · PC-i1 · W-1 / W-2（**非正式独立复验**）

| 项 | 值 |
|---|---|
| Loop | `loops/PC-i1-chapter-inheritance` |
| 复验对象 | W-1（5 章正文渲染，QA-D-1）、W-2（两处期望值改语义，QA-D-3） |
| 实现提交 | `d4ad4a2`（W-1/W-2 + G-1/G-2）；`c69a24c`（STATE 更正）；`4e5e517`（QA spec 入仓） |
| 分支 / HEAD | `recover/PI-ARCH-product-catalog` @ `4e5e51775c8dcd1993d75ef8a35acb5d8cf891d0`（复验期间未变） |
| 角色 / 会话 | `independent_qa` / `qa-pc-i1-independent-20260923-1101`（≠ `STATE.json.implementation_actor = tech_lead`） |
| 环境 | 15173（前端，200）· 18080（后端，`/api/v1/product-center/products` = 200）· 8107（KERT 技能，监听）· 9621（LightRAG，监听） |
| 只读声明 | 未修改任何产品代码 / 测试断言 / 门禁脚本 / loop 受控文件；未 `git add`/commit/push；未对 9621 发写请求；未改 KERT 工作区 |
| 判据来源 | 接口 `GET /api/v1/product-center/products/{id}`（经 15173 → 18080 真实链路）+ 真实页面 DOM（自研探针，**无 stub**） |

> 本报告结论**仅**覆盖 W-1 / W-2 及其相关门禁；**不**等于 PC-i1 loop 整体通过（见「总判」与「未覆盖/存疑」#1）。

---

## 一、总判：**BLOCKED —— 不得签发 `QA_PASS`**

| 层次 | 结论 | 依据 |
|---|---|---|
| **W-1 / W-2 本体**（V-1…V-4、V-8） | **独立复验通过**：13/13 产品 × 8 章 = 104 章，二选一**0 违规**；未发现产品缺陷 | 见 V-1…V-4、V-8 |
| **loop 出口**（V-5…V-7） | V-5 通过；**V-6 确认 2 项阻断仍然存在**（未被洗绿）；V-7 通过 | 见 V-5…V-7 |
| **正式签署** | **不可执行** | 具名 2 条，见 §四 |

`BLOCKED` 归因（均非"环境不可达"，而是 loop 级阻断）：

1. `contract_check` 门禁在 `EVIDENCE.json` 中仍为 **fail**（`make check` ⇒ exit 2，完整性失败项 = `loop-instances`）。
2. `F-PC-i1-04`：`loop-guard` 仍 **FAIL**（唯一命中 = 一份原始失败日志中含 Vue 插值片段，被"未解析占位符"规则误判）。

---

## 二、逐条结论（V-1…V-8）

### V-1 · D-1 是否真修好 —— **通过**

- 方法：自研探针（`probe-per-chapter.mjs`，**不使用 `page.route`**）在真实页面上对**全部 13 个产品**逐章核"二选一"；判据**全部取自接口**（`terms` / `boundaries ∪ prerequisites` / `processSteps` / `materialGroups` / `pricingItems` / `comparison` / `faqs` / `summary`），**不含任何常量计数期望**。
- 结果：**13 产品 × 8 章 = 104 章，violations = 0**；`PROD-CM-003` 在样本内（另有 SET-001 / FIN-003 / CB-001 / IB-001）。
- 结构与实现者证据 `evidence/w1-per-chapter-evidence.json` 对齐的逐章 JSON：`evidence/independent-qa-per-chapter-20260923-1101.json`（`totals = {products:13, chapters:104, violations:0}`）。
- 交叉印证（同一环境、独立进程）：QA spec 自身产出的 `b4-per-chapter.json`（`violations: []`）与 `e1-pending.json`（`noPendingAndEmpty: []`）本轮复跑同样为 0 违规；副本已固化为 `evidence/independent-qa-replay-spec-b4-per-chapter-20260923-1101.json`、`…-e1-pending-…json`。
- 原 QA 的 D-1（5 章 `bodyLen=0` 空壳）**未复现**：`TERMS/FIT/PROCESS/MATERIALS/COMPARE` 现在各产品的 `bodyCount=1` 且 `bodyLen>0`。

### V-2 · 内容确为契约数据 —— **通过**

- 前提先断言、再断言包含（前提不成立即失败，不静默跳过）：探针记录 `premiseTermsCount=2`、`expected=terms[0].businessDefinition`、`premiseOk=true`、`present=true`，**13/13 产品全部成立**。
- 样例（接口值 ⇒ 页面包含）：`PROD-CM-003` = 「经营稳定、信用评级较高的中型及以上企业。」；`PROD-FIN-003` = 「承接优质买方真实订单、具备稳定履约能力的中型/小型企业。」；`PROD-IB-001` = 「大型企业，有战略并购或产业整合需求。」
- 与 `product-center-pc1.spec.ts` 的对应断言一致（`:84-90`：先 `toBeGreaterThan(0)` + `toBeTruthy()`，再 `toContainText`），该断言为**加强而非弱化**。

### V-3 · 未接入章节未被误改 —— **通过**

- 13/13 产品：`PRICING` ⇒ `pricingItems=0`、`pendingCount=1`、具名标签 `待接入 PC3`、`bodyCount=0`；`FAQ` ⇒ `faqs=0`、`pendingCount=1`、`待接入 PC4`、`bodyCount=0`。
- 单测侧另有反向锁：`ProductCenterView.spec.ts` 新增用例在 `PRICING/FAQ` 上断言 `pc-chapter-pending` 存在且 `pc-chapter-body` 不存在。
- 未接入文案保留契约对象说明（如 `PkcFAQ[]`）与计划批次，**未**退化为空白。

### V-4 · D-3 改的是语义不是数字 —— **通过**

- 靶向复跑（§3.2 字面命令）：`7 passed`，exit 0，覆盖 `product-center-pc1`（八章用例）+ `B3/B4/B5/B6/E1`；另因 `-g` 过滤词含 `B3`，`G1` 标题亦被匹配（合法字面行为），实际 7 条全绿。
- 全量复跑（§3.1）**两次**均 `57 passed / 7 failed`，且 `B3/B4/B5/B6/E1/E2` 与 `product-center-pc1` 全绿；失败 7 条与 W-1/W-2 无关（归因见 V-7）。
- `git diff d4ad4a2^..d4ad4a2 -- <两个测试文件>` 逐行核实（快照：`evidence/independent-qa-gitdiff-W2-tests-20260923-1101.txt`，sha256 `8acc36c9…`）：
  - **不存在 `7 → 2` 常量替换**：只有被删除的 `toHaveCount(7)` / `toHaveLength(7)`，无 `toHaveCount(2)` / `toHaveLength(2)`；
  - **无弱化**：无 `waitForTimeout` 新增、无 `toBeVisible` 顶替强断言；反向是**收紧**（新增「无数据 ⇒ pending=1 且 body=0」「有数据 ⇒ pending=0」「正文不得为空」）；
  - 新增 1 条单测（5 章有数据的夹具 ⇒ 必须渲染正文），直接锁 D-1 反面。

### V-5 · 门禁与证据自洽 —— **通过**

- `EVIDENCE.json` 的 `command` 与 `LOOP.yaml` 逐字一致：6/6 均为 `identical=True`（含改后的 `frontend_unit` / `e2e_parity`）。
- 对每个 `evidence_file` 重算 sha256：**6/6 与 `output_sha256` 相同**（`hash_match=True`）。
- 附带登记（非缺陷）：`frontend_unit` / `e2e_parity` 的命令在失败**之后**被修改（G-1/G-2，Owner 2026-09-23 授权，`LOOP.yaml` 内 `command_fix_note` 已登记依据）；改后命令由我**逐字独立复跑**并各自通过 ⇒ 新命令非空转（见 V-7）。`W0-ITER.md` 显示全部条目 `Revision epoch: 0`，**无**预算重置痕迹。

### V-6 · 失败未被粉饰 —— **通过（未发现洗绿），但发现 1 处归因不实**

- `contract_check`：`EVIDENCE.json` 仍为 **`fail`**（未被改成 pass）。独立复跑 `make check` ⇒ **exit 2**。但失败项已具名区分：
  - `contract-check` 子项 **PASS**（`bash scripts/check-contracts.sh` ⇒ PASS，exit 0）；
  - 实际完整性失败 = `loop-instances`（`[REVERSE-GATE] repro_baseline(expected_exit_code=1)` + **PC-i1 新增不合规实例**）；
  - 另有 `semantic-consumption` **NOT_MET**（就绪度，不计入完整性失败）与 `gate-injection-tests` **INCONCLUSIVE**（不得计通过）。
- `loop-guard`：`python3 scripts/loop_guard.py --loop PC-i1-chapter-inheritance` ⇒ **FAIL**（exit 2），命中仍为**唯一 1 个**文件 `evidence/frontend_unit-20260922T145816Z.log`；逐字节复核该行为**失败输出中引用的 Vue 源码插值**（`<span class="customer-name">…`）⇒ 误判成立（`F-PC-i1-04` 属实）。`--instances-check` ⇒ FAIL：「1 个新增不合规实例」= `PC-i1-chapter-inheritance`（68/69 合规）。`--template-check` ⇒ PASS（仅校验模板，不判实例）。
- 未发现任何"改成 pass"：`git diff d4ad4a2^..HEAD -- EVIDENCE.json` 显示 `contract_check` 保持 `fail`；`independent_qa` 仍为 `pending`（无自签 QA_PASS）。
- **但**：`FAILURES.md` 对 `contract_check` 的根因叙述与其自身证据日志不符 ⇒ **QA-1**（见缺陷清单）。结论方向未变（都是 fail），不构成粉饰，但属"归因未回源"。

### V-7 · 环境项未被算成产品缺陷 —— **通过**

- 按 `LOOP.yaml` **当前**命令逐字复跑并记录真实退出码：

| gate | 命令（逐字） | 实测 |
|---|---|---|
| `frontend_unit` | `cd frontend && npx vitest run` | **exit 0**，`Test Files 67 passed` / `Tests 366 passed`（与门禁日志一致） |
| `e2e_parity` | `cd frontend && VITE_API_PROXY_TARGET=http://127.0.0.1:18080 npx playwright test e2e/product-center-pc1.spec.ts --output=test-results/gate-e2e-parity` | **exit 0**，`2 passed` |

- 全量复跑 2 次（§3.1）退出码：r2 = **1**（r1 未捕获退出码，失败集合与 r2 逐条一致）。7 条失败**具名归因**，全部为既存/环境/测试侧，**不计入** W-1/W-2 结论、也不改写其原始判定：
  | 失败用例 | 具名归因 |
  |---|---|
  | `analytics.spec.ts` ×4 | `ANALYTICS_UNAVAILABLE`（`KERT_ANALYTICS_DUCKDB` 未配）⇒ 环境未就绪，原判 BLOCKED |
  | `qa-e2e-acceptance A3` | 4 条 `console.error` 全为 `/analytics/*` 被调 API 的 503 资源日志（`pageErrors=0`）⇒ 环境项，原判 FAIL 待 Owner 裁决 |
  | `qa-e2e-acceptance D1` | 产品族名漂移（`结算` vs `结算服务` 等）⇒ 原判 P1、已转 PI-1 |
  | `customer-detail.spec.ts` | 测试侧 locator 严格模式冲突（`机会信号` 命中 2 元素）⇒ 原判测试侧缺陷 |

### V-8 · 诚实性红线 —— **通过**

- 13/13 产品页面：`pc-env-tag` = `DEMO · 演示数据`、`pc-data-environment` = `DEMO（演示数据）`、接口 `version.isDemo=true` 且 `environment=DEMO`；`pc-data-provenance` 原文含「演示数据不代表真实银行制度、价目或协议，禁止对客引用」。
- 缺失位仍为「待核验」（每产品 16–25 处）；`unverifiedClaimHits = []`（未出现「有证据支撑 / 已生效 / 已验证通过 / PRODUCTION_READY=YES」类表述）；`forbiddenRecommendHits = []`；`absolutePathHits = []`。
- loop 文档扫描：唯一命中为 DISPATCH §三「**不得**据 G1 推断"窄屏完全稳定"」与 `W1-PLAN.md`「**不得**暗示已生效」——均为**禁止性**表述，非自我认证。`EVIDENCE.md` 明示机器可判定证据板为 `EVIDENCE.json` 且不复写状态。

---

## 三、缺陷清单

### QA-1【文档/归因 · 中】`FAILURES.md` 对 `contract_check` 的根因叙述与自身证据不符

- 原文（`FAILURES.md` `20260922T145901Z`）：「`contract-check: FAIL: generated drift detected: missing=[], extra=[], changed=['manifest.json', 'product-knowl…`」。
- 事实：该 loop **自身**的证据 `evidence/contract_check-20260922T145839Z.log`（`COMMAND=make check`）内 `[PASS] contract-check`，同一份日志的失败项是 `loop-instances`（`[REVERSE-GATE] repro_baseline`）；今日复核 `bash scripts/check-contracts.sh` ⇒ `contract-check: PASS`（exit 0）。
- 最小复现（<1 分钟）：`cd /home/szf/dev/gits-cbanking && bash scripts/check-contracts.sh; echo $?` ⇒ `PASS / 0`；`make check` ⇒ 表内 `[FAIL] loop-instances`、`[PASS] contract-check`，整体 exit 2。
- 影响：**不改变**"门禁仍 fail、不得声称制品完整"的结论；但该根因叙述**未回源**，易让后续读者把 fail 误归因于合同漂移。建议更正或注明"另有单独执行 `check-contracts.sh` 的观察"。

### QA-2【门禁口径 · 观察】`contract_check` 这一 gate id 名不副实

`run_gates.py:46-51` 已把 `contract-check`（脚本）与 `loop-instances` / `loop-guard` 分开登记，但 `make check` 的聚合退出码只反映"任一完整性门禁失败"；`LOOP.yaml` 中 `contract_check` 的 `pass_condition` 写的是"产物与权威源一致"。⇒ 当失败来自 `loop-instances` 时，板面 `contract_check = fail` 会被读成合同漂移。非本 loop 引入，建议在 gate 描述中区分"合同漂移"与"实例合规"。

### QA-3【一致性 · 低】`LOOP.yaml.status = planned` 与 `STATE.json.status = in_progress` 不一致

`LOOP.yaml:5` 仍为 `planned`，`STATE.json:4` 为 `in_progress`（且 `blocked: true`）。`loop_guard` 未拦截该差异。建议随执行更新 `LOOP.yaml` 状态或明确其为规划期字段。

### QA-4【门禁脚本工作树改动 · 需收口确认归属】`loop_guard.py` / `record_gate.py` 存在**未提交**改动

- 改动内容：`loop_guard.py` 占位符扫描跳过非 UTF-8 文件（注释称源于 `FAIL-2026-09-22-AN0-QA-07` 的误判修正）；`record_gate.py` 增加 `--revision-note`（按 revision 纪元计数重记预算）与 `exit 3 ⇒ inconclusive`。
- 对**本 loop** 的独立影响核查（这是本次唯一需要防"削弱门禁"的点）：
  1. `--instances-check` 仍判 `PC-i1-chapter-inheritance` **不合规**（1/69）⇒ 未被洗绿；
  2. `W0-ITER.md` 全部为 `Revision epoch: 0`，无 `--revision-note` 使用痕迹 ⇒ 尝试预算未被重置（`frontend_unit` 2 次、`e2e_parity` 3 次，均 < `max_attempts_per_gate: 5`）；
  3. 副作用（非削弱）：Attempt 编号存在 1 起偏移——首条记录写作 `## Attempt 2`。
- 结论：**不构成本 loop 的"削弱门禁"**；但这两个门禁脚本为**未提交改动**，其来源与授权需 Owner/收口确认。

### QA-5【测试侧 · 观察】单测"逐章二选一"的判据由手写常量映射驱动

`ProductCenterView.spec.ts` 新增用例的 `fixtureHasPayload` 是手写常量表（非从 `detail` 夹具推导）。漂移时表现为**红灯**（不会假绿），但夹具变更时会误报。建议改为从夹具对象推导（如判定各字段长度）。

---

## 四、正式签署路径不可用的具名原因（§4 复核）

| # | 阻断 | 独立复核命令与结果 |
|---|---|---|
| 1 | `scripts/qa_attest.py:30` 要求 `STATE.json.status == "ready_for_independent_qa"`；本 loop 为 `in_progress` | `python3 -c "import json;print(json.load(open('loops/PC-i1-chapter-inheritance/STATE.json'))['status'])"` ⇒ `in_progress` |
| 2 | `qa_attest.py:41` 内部先跑 `loop_guard.py --loop <id> --evidence-only`，因 `F-PC-i1-04` 判 FAIL | `python3 scripts/loop_guard.py --evidence-only --loop PC-i1-chapter-inheritance` ⇒ `FAIL: unresolved placeholders: ['…/evidence/frontend_unit-20260922T145816Z.log']`，exit 2 |
| 3 | 即使改为 `ready_for_independent_qa`，`loop_guard.py:243` 仍要求 `all implementation gates pass`；`contract_check` 为 fail | `loop_guard.py:243` 原文：`if state.get("status") in {"ready_for_independent_qa","qa_pass","closed"} and not all_pass: raise` |

⇒ 本次为**非正式独立复验**：结论写在本报告与 `independent-qa-per-chapter-*.json`，**未**声称 `QA_PASS`、**未**改 `EVIDENCE.json`（其 `independent_qa.status` 保持 `pending`），结论交回 TL / Owner 记录。

---

## 五、未覆盖 / 存疑（**必填**）

1. **PC-i1 loop 其余出口未开工**：P38 12 章逐一落位、C6/C9/C11 独立可见、同产品对照三判定（事实不丢/来源可达/阅读更快）——TL 自述（DISPATCH §7.5）与现场一致，**均未动**。本报告**不**为这些目标背书，PC-i1 远未 complete。
2. 未核 8 章的**逐字段**语义正确性：`PROCESS` / `MATERIALS` / `COMPARE` 只核了"正文非空 + 内容抽查"（TERMS 对标接口）；未逐条比对 `processSteps[i].summary`、`materialGroups[].items[]`、`comparison.rows[].values` 的完整映射。
3. 未用**真实数据**覆盖 `FIT = boundaries ∪ prerequisites` 的反例（`boundaries` 空 + `prerequisites` 非空）：现状 13/13 均有 `boundaries`；该分支仅由单测夹具覆盖。
4. 未验证**生产构建产物**（`vite build`）：本次只测 dev server 15173；历史上"页面 200 但静态资源 404"一类缺陷未被覆盖。
5. **不造 mock** 覆盖 `PRICING` / `FAQ` 未来有数据时的渲染（PC3/PC4 未接入，无法构造真实数据；按 §0.4 不引入 stub）。
6. 7 条失败**未重新裁定**（沿用原 QA 归属：环境未就绪 / P1 已转 PI-1 / 测试侧 locator）；D1 族名漂移与 W-1/W-2 无关。
7. **证据落盘位置不稳定（方法论问题）**：QA spec 的默认 `EVIDENCE_DIR` 是 `test-results/qa-latest`，与 `reportDir` 同名，跨运行会被清理/覆盖 ⇒ 第 1 次全量与 §3.2 靶向跑的 per-test JSON 未能留存（其失败截图/trace 仍在各自 raw 目录）。我已将第 2 次全量的 4 个结构化 JSON 固化入 `loops/PC-i1-chapter-inheritance/evidence/`。建议后续 QA 显式设置 `QA_EVIDENCE_DIR` 并与 `QA_REPORT_DIR` 分离。
8. 第 1 次全量运行的**退出码未捕获**（当时未包 exit 捕获）；第 2 次已捕获 = **1**。两次失败集合逐条一致（7 条）。
9. **我自研探针自身两轮失败（已修正，非产品结论）**：第 1 轮缺 baseURL ⇒ `Cannot navigate to invalid URL`；第 2 轮把「待接入 PCx」定位在 `pc-chapter-pending` 段落（实际在章头 n-tag）⇒ 报 20 条假违规。两轮均为**我自己的工具缺陷**，修正后重跑 0 违规；由此产生的误导性截图已删除，**未据此下任何产品结论**。
10. `LightRAG(9621)` 只读：未 publish/retract，未评估检索质量；`KERT(8107)` 未做写操作；未改 KERT 工作区。
11. `make check` 中另有**非 PC-i1** 的失败/未判定项（`repro_baseline` 反向门禁、`semantic-consumption` 就绪度、`gate-injection-tests` 无法判定）——我不对它们的判定合理性下结论。

---

## 六、环境变动登记（只读复验，写入仅限 QA 产物区）

| 类别 | 明细 |
|---|---|
| 只读 | 13 个产品页面 × 多轮；`GET /api/v1/product-center/products{,/{id}}`；门禁复跑：`make check` · `bash scripts/check-contracts.sh` · `loop_guard.py`（默认/`--instances-check`/`--template-check`/`--evidence-only`） |
| 写入（QA 产物） | `frontend/test-results/qa-independent-20260923-1054/**`（自研探针 + 逐章 JSON）、`…-raw-20260923-1054/**`、`…-20260923-1101-r2/**` + `…-raw-…-r2/**`、`test-results/gate-e2e-parity/**`（被 `LOOP.yaml` 的 `e2e_parity` 命令覆写，属该门禁自身输出目录）、`test-results/qa-latest/**`（spec 默认 EVIDENCE_DIR，被本轮复跑覆写） |
| 新增入 loop evidence | 本报告 · `independent-qa-per-chapter-20260923-1101.json` · `independent-qa-gitdiff-W2-tests-20260923-1101.txt` · 4 个 spec 产物副本（`b4/e1/e2/d1`，均已确认不含占位符令牌，复跑 `loop-guard` 未新增命中） |
| 端口/进程 | `e2e_parity` 门禁命令按其基线 config 自行拉起 webServer(5173)，运行结束已回收（复核无 5173 监听）；15173 / 18080 全程未重启 |
| 未做 | 未改任何产品代码 / 断言 / 门禁脚本 / `specs/` · 未 `git add`/commit/push · 未动 LightRAG / KERT · 未改 `EVIDENCE.json` / `STATE.json` / `NEXT_SESSION.md`（按任务书 §5：结论交回 TL/Owner 记录） |

---

## 七、原始产物索引

| 产物 | 路径 | 说明 |
|---|---|---|
| 逐章 JSON（本报告主证据） | `loops/PC-i1-chapter-inheritance/evidence/independent-qa-per-chapter-20260923-1101.json` | 13 产品 × 8 章；sha256 `484e7f28…` |
| 自研探针 | `frontend/test-results/qa-independent-20260923-1054/probe-per-chapter.mjs` | 无 stub；sha256 `ead83d13…` |
| 探针原始输出 | `frontend/test-results/qa-independent-20260923-1054/per-chapter-probe.json` | 含 honesty 段（DEMO/待核验/未证实表述扫描） |
| W-2 改动 diff 快照 | `loops/PC-i1-chapter-inheritance/evidence/independent-qa-gitdiff-W2-tests-20260923-1101.txt` | `d4ad4a2^..d4ad4a2` 两个测试文件全量 diff；sha256 `8acc36c9…` |
| 全量复跑 #1 | `frontend/test-results/qa-independent-20260923-1054/**`、`…-raw-…-1054/**` | 57 passed / 7 failed（3.8m） |
| 全量复跑 #2 | `frontend/test-results/qa-independent-20260923-1101-r2/**`、`…-raw-…-r2/**` | 57 passed / 7 failed，**exit 1**（3.7m） |
| spec 复跑结构化产物（副本已固化） | `evidence/independent-qa-replay-spec-{b4-per-chapter,e1-pending,e2-demo,d1-cross-page}-20260923-1101.json` | 原始位置 `frontend/test-results/qa-latest/` |
| 门禁复跑原文 | `/tmp/pci1-make-check.log`、`/tmp/pci1-qa-full.log`、`/tmp/pci1-qa-full-r2.log`、`/tmp/pci1-targeted.log`、`/tmp/pci1-gate-e2e.log`、`/tmp/pci1-vitest.log` | 临时目录，未入仓 |
| 原始 QA（复验其结论是否真被修掉） | `frontend/test-results/qa-20260922-1430/REPORT.md` | 总判 FAIL；D-1 / D-3 |

---

## 八、一句话结论

**W-1 / W-2 可判「独立复验通过」**（13/13 产品逐章二选一 0 违规、TERMS 正文确含接口 `terms[0].businessDefinition`、未接入的 PRICING/FAQ 未被误改、两处断言是语义化改写且无弱化或 `7 → 2` 常量替换、门禁证据哈希自洽、真实性红线守稳）；但 **PC-i1 整体不得签 `QA_PASS`**，剩余阻断项为：① **`F-PC-i1-04`**（`loop-guard` 把原始失败日志里的 Vue 插值误判为未解析占位符，待 Owner 授权 R-1/R-2）；② **`contract_check` 门禁仍 fail**（真实完整性失败项 = `loop-instances` 的 `repro_baseline` 反向门禁 + PC-i1 新增不合规实例；合同漂移子项现已 PASS ⇒ 归因须按 QA-1 更正）；另需知悉 **QA-3**（`LOOP.yaml` 状态未更新）、**QA-4**（`loop_guard.py`/`record_gate.py` 未提交改动，经复核未洗绿本 loop，来源待确认）。

---

*报告生成：2026-09-23 11:01（本地）× actor=`independent_qa` × session=`qa-pc-i1-independent-20260923-1101` × 模式=非正式独立复验（`qa_attest.py` 不可用，见 §四）。*
