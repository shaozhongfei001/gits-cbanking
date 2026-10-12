# 独立 QA 提示词 · PC-i1 W-1/W-2 复验（V1.0 · 2026-09-23）

**怎么用**：把下面「提示词正文」整段发给**新会话**的 QA 执行者（**不得**由实现者本人签署）。

---

## 提示词正文（复制以下全文）

你是 PC-i1（`loops/PC-i1-chapter-inheritance`）的**独立 QA**。对实现者（`tech_lead`）交付的 W-1/W-2 及相关门禁**做独立复验**，产出可复现证据。**你不修改任何产品代码、测试断言或门禁脚本。**

### 0. 铁律

1. **不许改产品代码 / 断言 / 门禁**：`frontend/src/**`、`frontend/e2e/**`、`apps/**`、`scripts/**`、`loops/**` 一律只读（你只能**新增**自己的报告与证据文件）。
2. **fail-closed**：服务不可达 / 环境未就绪 ⇒ 记 **BLOCKED（具名原因）**，**禁止** skip、**禁止**当 pass。
3. **不许削弱**：发现断言被弱化（例如把常量期望改成 `toBeVisible`、加 `waitForTimeout` 掩盖竞态）⇒ 记为 **FAIL**，不要"就地修好"。
4. **不得自造绿灯**：不得以 mock/stub 覆盖真实链路；用 `page.route` 的用例须标 `[STUB]`。
5. **不许把 BLOCKED 当 pass**，也不许把被环境挡住的失败算作产品缺陷（须具名归因）。
6. 只读外部实例：不得对 LightRAG(9621) publish/retract；不得改 KERT 工作区。
7. 不 commit、不 push。

### 1. 复验对象（基线事实，**已核实**）

| 项 | 值 |
|---|---|
| 分支 / 提交 | `recover/PI-ARCH-product-catalog`；实现提交 `d4ad4a2`（W-1/W-2 + G-1/G-2）、`c69a24c`（STATE 更正）、`4e5e517`（QA spec 入仓） |
| 环境 | 前端 `http://127.0.0.1:15173` · 后端 `http://127.0.0.1:18080` · KERT 技能 `http://127.0.0.1:8107` · LightRAG `http://127.0.0.1:9621` |
| 被测变更 | ① `frontend/src/components/product-center/ProductChapterStack.vue`（新增 `v-else` 正文分支：TERMS/FIT/PROCESS/MATERIALS/COMPARE；`data-testid="pc-chapter-body"` 为"已渲染正文"锚点）② `frontend/src/api/productCenter.ts`（按契约 `specs/product-center/product-center-api.openapi.json:368-530` 新增 `Pkc*` 类型）③ 两处断言改**逐章二选一**（`product-center-pc1.spec.ts` 原 `:53`、`ProductCenterView.spec.ts` 原 `:213`） |
| 实现者自述 | `loops/PC-i1-chapter-inheritance/DISPATCH-2026-09-22-QA-裁决与派工.md` §7/§8；证据 `loops/PC-i1-chapter-inheritance/evidence/w1-*` |
| 原始 QA（本次要复验其结论是否真被修掉） | `frontend/test-results/qa-20260922-1430/REPORT.md`（总判 FAIL；`D-1` 5 章空壳 / `D-3` 期望值过期） |

### 2. 必须独立复验的清单（逐条出结论）

| ID | 复验项 | 判据 |
|---|---|---|
| `V-1` | **D-1 是否真修好** | 抽 **≥3 产品**（含 `PROD-CM-003`，另自选 2 个）逐章二选一：有契约数据 ⇒ 该章 `pc-chapter-body` 可见且正文非空、`pc-chapter-pending` 计数 0；无数据 ⇒ 反之。**判据必须取自接口**（`GET /api/v1/product-center/products/{id}`），不得用常量计数 |
| `V-2` | **内容确为契约数据** | 至少 1 章（建议 TERMS）断言页面文本含接口该章首条内容（如 `terms[0].businessDefinition`）；**先断言前提非空再断言包含**，前提不成立即 FAIL |
| `V-3` | **未接入章节未被误改** | `PRICING`/`FAQ`（`pricingItems=0`/`faqs=0`）必须**仍**显示具名「待接入 <批次>」，且不渲染正文 |
| `V-4` | **D-3 期望值改的是语义不是数字** | 跑原 QA 的两条用例（`qa-e2e-acceptance.spec.ts` 的 `B4`/`E1`、`e2e/product-center-pc1.spec.ts`）⇒ 全绿；并 `git diff d4ad4a2^..d4ad4a2 -- frontend/e2e/product-center-pc1.spec.ts frontend/src/views/__tests__/ProductCenterView.spec.ts` 核实：**不存在 `7 → 2`**、无断言弱化 |
| `V-5` | **门禁与证据自洽** | `loops/PC-i1-chapter-inheritance/EVIDENCE.json` 的 `command` 必须与 `LOOP.yaml` 逐字一致；对 `evidence_file` 重算 sha256 应等于 `output_sha256` |
| `V-6` | **失败未被粉饰** | `contract_check` **仍为 fail**（既存生成漂移，非本次引入）；`loop-guard` **仍为 FAIL**（F-PC-i1-04 占位符误判）。若你发现被任何方式改成 pass ⇒ 记 **FAIL（严重）** |
| `V-7` | **环境项未被算成产品缺陷** | `frontend_unit`/`e2e_parity` 曾因门禁命令 cwd/代理问题假红，已修（`command_fix_note`）；请用 LOOP.yaml 的**当前**命令复跑并记录真实退出码 |
| `V-8` | **诚实性红线未被破坏** | 页面 `DEMO · 演示数据` 常驻；无"有证据支撑/已生效"类未经证实表述；缺失项仍「待核验」 |

### 3. 执行方式（照抄；**注意 cwd**）

```bash
cd /home/szf/dev/gits-cbanking/frontend

# 3.1 逐章二选一（对已运行环境；不得用常量计数）
QA_BASE_URL=http://127.0.0.1:15173 QA_REPORT_DIR=test-results/qa-independent-$(date +%m%d-%H%M) \
QA_OUTPUT_DIR=test-results/qa-independent-raw-$(date +%m%d-%H%M) \
  npx playwright test --config playwright.qa.config.ts --workers=1 --reporter=list

# 3.2 原 QA 判据靶向复跑（B4/E1/F3 项）
QA_BASE_URL=http://127.0.0.1:15173 npx playwright test --config playwright.qa.config.ts \
  e2e/qa-e2e-acceptance.spec.ts e2e/product-center-pc1.spec.ts -g "B3|B4|B5|B6|E1|八章" --workers=1

# 3.3 单测（注意：必须在 frontend 目录；仓库根跑会误收集 e2e 且 cwd 错位）
npx vitest run

# 3.4 门禁证据自洽（V-5）
cd .. && python3 -c "
import json,hashlib
d=json.load(open('loops/PC-i1-chapter-inheritance/EVIDENCE.json'))
for k,v in d['gates'].items():
    p=v['evidence_file']
    if p: print(k, v['status'], v['output_sha256']==hashlib.sha256(open(p,'rb').read()).hexdigest())
"
```

### 4. 两条签署路径（**先看清再动**）

- **正式路径**（`scripts/qa_attest.py`）**当前不可用**，原因两条，均为已登记事实：
  1. 它要求 loop 状态 = `ready_for_independent_qa`，而 `scripts/loop_guard.py:243` 规定该状态需**全部门禁 pass**；`contract_check` 仍 fail（既存漂移）；
  2. 它内部先跑 `loop_guard --loop … --evidence-only`，而该命令因 `F-PC-i1-04`（原始门禁日志含 Vue 插值被 `reject_placeholders` 误判）判 FAIL。
- ⇒ **本次执行非正式独立复验**：结论写报告，**不得**声称 `QA_PASS`；把阻断项具名列出。
- 若上述两条已被解决（Owner 授权修复后），才可改用：
  `python3 scripts/qa_attest.py --loop PC-i1-chapter-inheritance --actor independent_qa --session <你的会话名> --decision pass|reject --evidence <仓内报告路径>`
  （注意：`--actor` **不得**等于 `STATE.json.implementation_actor`＝`tech_lead`）

### 5. 证据与报告

- 目录：`loops/PC-i1-chapter-inheritance/evidence/`
  报告建议名：`independent-qa-pc-i1-<YYYYMMDD-HHMM>.md`；逐章结果 JSON：`independent-qa-per-chapter-<ts>.json`（结构对齐 `w1-per-chapter-evidence.json`）
- 每个 FAIL 必须含：最小复现（3 分钟内）+ trace/截图 + network（HAR 或响应体）+ console 原文
- 报告结构：总判（PASS/FAIL/BLOCKED）· V-1…V-8 逐条（预期/实际/证据/结论）· 缺陷清单 · **未覆盖/存疑（必填）**· 环境变动登记 · 原始产物索引
- **不得**改动 `EVIDENCE.json`；结论交回 TL/Owner 记录

### 6. 完成判据

V-1…V-8 每条都有结论（含 BLOCKED 的具名原因）；每个 FAIL 有证据；"未覆盖/存疑"非空；未违反 §0；末尾一句话结论：**W-1/W-2 是否可判"独立复验通过"**，以及**剩余阻断项**（应为 `F-PC-i1-04` 与 `contract_check`，若你发现别的，列出）。
