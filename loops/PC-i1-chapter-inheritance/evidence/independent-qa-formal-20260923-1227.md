# 独立 QA 正式复验报告 · PC-i1 · 甲（既有主体）+ 乙（交棒后新增） · **含正式签署**

| 项 | 值 |
|---|---|
| Loop | `loops/PC-i1-chapter-inheritance` |
| 复验对象 | **甲**：W-1/W-2（既有非正式复验过的主体，抽验） · **乙**：W1-a/b/c/d/e/g + 2 处自报缺陷修复 + 门禁/证据自洽 + 粉饰核查 |
| 分支 / HEAD | `recover/PI-ARCH-product-catalog` @ `652a23f09f5139261791d977958f2e2ebeac1c0f`（复验期间未变；`git status` 前后一致） |
| 角色 / 会话 | `independent_qa` / `qa-pc-i1-formal-20260923-1227`（≠ `STATE.json.implementation_actor = tech_lead`） |
| 环境 | 15173（前端，200）· 18080（后端，200）· 8107（KERT，监听）· 9621（LightRAG，监听）· **8080 亦在监听且返回 401（非被测后端）** |
| 只读声明 | 未改 `frontend/src/**`、`frontend/e2e/**`、`apps/**`、`scripts/**`、`loops/**` 中任何既有文件；仅**新增**本报告与 `independent-qa-formal-*` 证据；未 `git add`/commit/push；未对 9621 发写请求；未改 KERT 工作区 |
| 判据来源 | 接口 `GET /api/v1/product-center/products{,/{id}}` 与 `GET /api/v1/product-knowledge/cards/{id}`（经 15173 → 18080 真实链路）+ 真实页面 DOM（**自研探针，无 stub**） |
| 签署结论 | **REJECT**（`qa_attest.py --decision reject`，见 §七） |

---

## 〇、前置自检（§1 逐条，均通过）

```text
status             = ready_for_independent_qa   （期望一致）
qa_actor           = independent_qa             （期望一致）
6/6 gate           = pass                       （期望一致：contract_generate/contract_check/security_check/frontend_typecheck/frontend_unit/e2e_parity）
independent_qa     = pending                    （期望一致）
loop_guard --loop  = PASS
loop_guard --instances-check = 69/69 合规、0 不合规、0 基线冻结
```

⇒ 前置条件成立，**不记 BLOCKED**，本轮可执行正式签署。

---

## 一、总判：**REJECT —— 不得签发 `QA_PASS`**

| 层次 | 结论 | 依据 |
|---|---|---|
| **甲 · 既有主体**（W-1/W-2） | **抽验通过**（与 `independent-qa-pc-i1-20260923-1101.md` 结论一致，未发现回退） | §二 甲 |
| **乙 · Owner 逐条列举的判据** | **9/9 全部通过**（含卡间节号错位的**正常路径**绑定、C6/C9 独立区块、C11 版本区、C10 产品级边界、C12 具名缺失、门禁证据自洽、失败未被粉饰） | §二 乙 |
| **乙 · 新增独立发现** | **2 项具名阻断**（均属「登记章号 vs 实际节号」这一被实现者自报修复的缺陷类**未彻底分离**） | §三 QA-B1 / QA-B2 |
| **正式签署** | **执行 `--decision reject`** | §七 |

> **口径声明（防误读）**：本轮**不是**「判整个 PC-i1 失败」。Owner 列举的 9 条判据我逐条独立复现且全部成立；REJECT 的唯一依据是**我在其外新发现的 2 项可由最小复现触达的缺陷**，且它们与实现者自报已修复的「卡间节号错配 / 版本区写死节号」属**同一缺陷类**。修复面很小（3 处渲染表达式），但按 fail-closed 纪律，存在未闭合的真实缺陷时不得签发 `QA_PASS`。

---

## 二、逐项结论

### 甲、已复验过的主体（抽验）

| 项 | 命令（逐字） | 实测 | 结论 |
|---|---|---|---|
| 前端单测 | `cd frontend && npx vitest run` | **exit 0**，`Test Files 69 passed (69)` / `Tests 377 passed (377)` | **通过**（且与门禁证据 `frontend_unit-20260923T034533Z.log` 的 `69/377` **逐字一致**） |
| E2E | `cd frontend && VITE_API_PROXY_TARGET=http://127.0.0.1:18080 npx playwright test e2e/product-center-pc1.spec.ts --output=…` | **exit 0**，`3 passed (5.9s)` | **通过** |

- 引用既有非正式复验（`evidence/independent-qa-pc-i1-20260923-1101.md`，**不改写**）：「W-1/W-2 本体：独立复验通过」（13/13 产品 × 8 章 = 104 章，二选一 0 违规）。
- 本轮抽验未发现回退；两个被阻断项的**解除事实**经我独立复核（见 §二 乙「门禁与证据自洽」与「失败未被粉饰」）。

### 乙、非正式复验之后新增、尚未经独立复验的工作（**重点**）

> 方法：自研 4 支探针（`probe-pci1` / `probe-landing` / `probe-faultcard` / `probe-heading`），**不使用 `page.route` 伪造数据**（仅 `probe-faultcard` 用**请求中断**做故障注入，不注入任何假数据）。期望值**独立推导**：以**节标题关键字**为唯一语义锚，另记录「节号前缀兜底」路径是否与之冲突。

#### 乙-1 `W1-a/b` C6/C9 独立区块 —— **通过**

- 13/13 产品：`pc-inherited-c6` / `pc-inherited-c9` 均 `present`，且 `inInheritedRoot=true`、`insideTable=false`、`insideCompare=false` ⇒ **位于 `pc-inherited-chapters` 承接区之内、不在比较表 `<table>` 内、不在 `data-section-key="COMPARE"` 章内** ⇒ **未被比较表替代**（判据按你的口径逐条成立）。
- 含**原文**：`pc-inherited-{c6,c9}-content` 与接口 `sections` 中关键字命中的该节 `content` **一致**（归一化空白后前 20 字包含比对），13/13 成立。
- 含**相对来源**（`sourceFile` + **实际**节号）与**有效状态**：13/13 的 meta 均含 `来源：`（且**不以 `/` 开头**）、`（第 N 节）`、`有效状态：…（…）｜生效日：…`。
- 样例（`PROD-FIN-003` C6）：`承接位置：本区独立区块（R2：无对应区块）｜来源：financing/version=2026.08.31.1/product-cards/PROD-FIN-003.md （第 6 节）｜有效状态：DRAFT（产品卡镜像（未发布））｜生效日：未设定`

#### 乙-2 `W1-c` C11 版本语义 —— **通过**

- 右栏 `pc-immutable-version` 13/13 出现且 `inRightCol=true`；承载四要素：
  ① **语义陈述** `pc-immutable-statement`（含「不可变」）；
  ② **版本事实字段** `pc-immutable-facts`（`versionStatus（versionLabel）｜生效日`）；
  ③ **实际节标题原文** `pc-immutable-source` = `{{ 实际节标题 }} 原文 · 来源：{{ 相对 sourceFile }}`，且 `pc-immutable-content` 与该节 `content` 一致；
  ④ 相对来源（非绝对路径）。
- **不得只留版本徽章** ⇒ 成立（原文与语义均在，非仅 `n-tag`）。

#### 乙-3 `W1-d` C2/C3/C10 指名引用 —— **通过**

- `pc-inherited-c2/c3/c10` 13/13 均含 `承接位置：`（指名引用）。
- **C10 产品级 `salesBoundaries`**：13/13 均渲染 `pc-inherited-c10-contract`，逐条含 `boundaryKind`、`riskCategory`、`mandatoryDisplay`（=true 时显式「强制展示」）、`text`，且**条数与合同字段一致**（实测 10 卡 × 2 条 + 3 卡 × 3 条 = **29 条**，逐条比对 0 差异）。
- 另核 C10 的另两处落点：首屏 `pc-fixed-boundaries` 与右栏「页面边界」均含全部 `fixedBoundaryStatements`（13/13）。
- **「为空时具名标注」分支：未覆盖** —— 真实数据中 **13/13 产品 `salesBoundaries` 均非空**（见 §五 #2）。

#### 乙-4 `W1-e` C12 —— **通过**

- `PROD-FIN-001/002/003` 3 卡：渲染 `pc-inherited-c12-content`，内容与 `EvidenceRef` 节一致（13/13 探针内取证）。
- 其余 10 卡：**具名缺失**且**非空白**（`pc-inherited-c12-absent` 存在、无 `pc-inherited-c12-content`）。
- 我的判据前提（独立复算）：`PROD-FIN-*` 与其余卡在 `sections` 上的差异 = **12 节 vs 11 节**，`EvidenceRef` 节仅存在于前者 ⇒ 结论方向成立。

#### 乙-5 卡间节号错位（实现者自报修复）—— **正常路径通过；但同一缺陷类在另一分支残留 ⇒ 见 §三 QA-B1**

**（a）事实前提（我独立取自接口，非引用实现者）**

| 卡组 | 节数 | §10 | §11 | §12 |
|---|---|---|---|---|
| `PROD-FIN-001/002/003` | 12 | 销售边界 | **EvidenceRef（源文件与条款定位）** | **不可变版本语义** |
| 其余 10 卡（含 `PROD-CM-003`/`PROD-IB-001`） | 11 | 销售边界 | **不可变版本语义** | —（无该节） |

⇒ 「登记章号（C11→11 / C12→12）与实际节号在前者上错位」这一前提**成立**；我的探针自动检出 **6 处冲突**（3 张 FIN 卡 × {C11, C12}）。

**（b）正常路径绑定 —— 通过**

- `PROD-FIN-003`：版本区 `pc-immutable-source` 含 `12.`，`pc-immutable-content` 与「12. 不可变版本语义」一致 ⇒ **版本区绑 §12** ✓
- `PROD-FIN-003`：`pc-inherited-c12-content` 与「11. EvidenceRef…」一致，`pc-inherited-c12-meta` 含「第 11 节」⇒ **C12 绑 §11** ✓（**未错配**）
- 13/13 产品全量同口径核对：`SECTION_NO_MISMATCH` / `ORIGINAL_MISMATCH` **0 起**。

**（c）变异复验（证明我的探针**不是**空转、对该缺陷类有鉴别力）**

| 变异 | 期望 | 实测 |
|---|---|---|
| （基线） | 0 违规 | **0 违规**（13 产品） |
| `QA_MUTATE=prefix`：期望改用「节号前缀」推导（即复现被修复前的**错位 bug**） | > 0，且应落在 FIN 卡 | **18 违规**，产品集合 = `{PROD-FIN-001, −002, −003}`，code = `FIN_C11_BIND` / `FIN_C12_BIND` / `C11_ORIGINAL_MISMATCH` / `C11_SOURCE_TITLE` / `ORIGINAL_MISMATCH:c12` / `SECTION_NO_MISMATCH:c12` |
| `QA_MUTATE=c10wrong`：C10 文本期望故意改错 | > 0 | **29 违规**（= 29 条合同边界的逐条比对全部报错），code = `C10_TEXT` |

⇒ 判据**非空转**：错位到 §11/§12 的任一方向都会被我的探针判红。

#### 乙-6 `W1-g` 三判定文档诚实性 —— **通过（无粉饰）**

`loops/PC-i1-chapter-inheritance/memory/waves/W1-g-同产品对照.md`

| 你的判据 | 我的独立核验 |
|---|---|
| 落点 **12/12 可复核** | **成立**。我用两支探针独立覆盖 C1–C12：`probe-pci1` 覆盖 C2/C3/C6/C8/C9/C10/C11/C12，`probe-landing` 覆盖 C1(OVERVIEW 正文)/C3(首屏能力标签)/C4/C5/C7/C10(首屏+右栏)。**13 产品 × 12 章 = 156 章，落点违规 0**。其中 C1 判据我按接口 `summary.oneSentenceDefinition` 在 **OVERVIEW 章正文**核到（该字段**不在**首屏——见 §五 #1 我的探针自纠） |
| **来源可达**须有实测依据 | **成立**。实测依据 = 每个落点均给出相对来源/契约字段名 + 有效状态；13/13 页面 `text` 无 `/home/` |
| **操作路径更短**须有实测依据 | **部分成立，且已如实标注方法边界**：新版侧有本机实物量测（`evidence/w1-g-parity-2026-09-23T0344.json`，`operations={select:1, expand:0}`，`at=2026-09-23T03:44:50Z`）；旧版侧**明确写为「引用 R2 §6 权威基线，本次未据旧版 DOM 重算」**。我独立观察一致：以 URL 直达产品页后，各承接块与章正文**无需任何展开操作即可见** |
| **「事实等价未验证」必须如实保留** | **成立**。§2.1 原文：「未满足（遗留）…未做逐条事实等价比对…⇒ 结论：**事实不丢** 目前只能记「落点层面成立；等价层面未验证」」，且 §4 复述「**事实等价层面未验证**」 |
| **不得出现任何「用时」结论** | **成立**。全文无任何用时/效率数字；§2.3 与 §4 主动声明「**不作任何用时结论**」「**不含**任何用时/效率数字」 |
| **不得声称「新版优于 P38」** | **成立**。§4 原文「**不得声称"新版优于 P38"**」，并复述 R2 原结论「在 I1–I4 完成前，"新版优于 P38"不成立**继续成立**」 |

#### 乙-7 门禁与证据自洽 —— **通过**

| 检查 | 结果 |
|---|---|
| `EVIDENCE.json.gates[*].command` 与 `LOOP.yaml.gates[*].command` **逐字一致** | **6/6 `identical=True`**（含改后的 `frontend_unit` / `e2e_parity`） |
| 对每个 `evidence_file` 重算 sha256 == `output_sha256` | **6/6 `hash_match=True`** |
| `Revision epoch 1` 的开启理由在 `W0-ITER.md` 可查 | **可查**（`W0-ITER.md:140`：「制品 revision 变更（W1-d/W1-e 实现 + 卡间节号错配/版本区写死节号两处缺陷修复）后按 D-15 重记｜2026-09-23T03:45:33」） |
| `--revision-note` 使用是否正当（制品是否**真的**变了） | **正当**。`git diff c23d1e4..396ff23` 实际改动 `frontend/src/components/product-center/ProductInheritedChapters.vue`（+111/−…）、`cardChapter.ts`、`ProductCenterView.vue`、`ProductGovernancePanel.vue`、`api/productCenter.ts` ⇒ 制品确已变更，非「为重置预算而空转」 |
| `independent_qa` 是否被自签 | **未**：仍为 `pending`（`actor/session/attested_at/evidence_file/evidence_sha256` 全 `null`） |

> 需知悉（非缺陷，见 §五 #4）：`frontend_unit` 与 `e2e_parity` 在 **epoch 0 各已用满 5 次**（Attempt 2–6），且两次门禁在 epoch 0 的**最后一次已 pass**。⇒ 不存在「用新纪元掩盖失败尝试」；但纪元边界与触顶点重合，属需 Owner 知悉项。

#### 乙-8 失败未被粉饰 —— **通过**

- `make check` 独立复跑：**exit 0**，`gk-ke-gates: 22/23 通过`，其中
  - `semantic-consumption` = **`READINESS NOT MET`**（就绪度，**不计入完整性失败**）—— **如实保留**；
  - `gate-injection-tests` = **`INCONCLUSIVE`**（**不得计为通过**）—— **如实保留**，`make check` 自身输出明写「⚠️ 有下列检查**无法判定**，不得在汇报中计为通过」。
- `EVIDENCE.json.gates.contract_check.status` = **`pass`**（配 `contract_check-20260923T033153Z.log`，exit 0）：与 `make check` 现状一致（`[PASS] contract-check` / `[PASS] loop-instances` / `[PASS] loop-guard`），**非**把 fail 改写成 pass。
- `loop_guard.py --loop PC-i1-chapter-inheritance` ⇒ **PASS**；`--instances-check` ⇒ **69/69 合规**。
- 文档诚实性扫描（`loops/PC-i1-chapter-inheritance/**`）：`QA_PASS`/「已生效」/「有证据支撑」类命中**全部**为「不得/不能/未」等**禁止性**表述或角色权限说明，**无自我认证**。
- `FAILURES.md` 为 append-only，独立 QA 的 `QA-1` 更正以**新增**条目 `20260923T113000Z` 落盘（原记录未删改）。

---

## 三、缺陷清单

### QA-B1【阻断 · 中】**「登记章号 vs 实际节号」未彻底分离** —— 与实现者自报已修复的缺陷类同源

**现象**：`C12` 区块的**标题**与**缺失文案**、以及版本区的**缺失文案**，仍使用 R2 **登记章号**（C12→`12`、C11→`11`）而非该卡**实际节号**。在 `PROD-FIN-*`（§11=`EvidenceRef`、§12=`不可变版本语义`）上与实际节号冲突。

**最小复现 A（正常路径，无需任何故障注入，约 20 秒）**
```bash
cd /home/szf/dev/gits-cbanking/frontend
node test-results/qa-formal-pci1-20260923/probe-heading.mjs /tmp
```
实测（`PROD-FIN-003`）：
- `pc-inherited-c12 .pc-inherited-block-head` = **`12. EvidenceRefC12原文`**
- 同块 `pc-inherited-c12-meta` = `…｜来源：financing/version=2026.08.31.1/product-cards/PROD-FIN-003.md （第 **11** 节）｜…`
⇒ **同一区块内「12.」与「第 11 节」并列**（`PROD-FIN-001` 同）。
（`PROD-CM-003`/`PROD-IB-001` 因该卡确实无 §12，标题与 meta 同为 12，**不冲突**。）

**最小复现 B（故障路径）**
```bash
node test-results/qa-formal-pci1-20260923/probe-faultcard.mjs /tmp PROD-FIN-003
# 探针内部 page.route 拦截 '**/api/v1/product-knowledge/cards/**' 并 route.abort('failed')
```
实测 DOM 原文（`abortedRequests=2`）：
- 承接区 meta：`…｜来源：来源标识不可得 （第 6 节）｜…`
- 承接区缺失文案：**`该产品卡未包含第 12 节（EvidenceRef）原文 —— 如实标注，不以示意内容填充。`**
- 版本区缺失文案：**`该产品卡未包含第 11 节（不可变版本语义）原文 —— 如实标注，不以示意内容填充。`**
⇒ 对 `PROD-FIN-003`，`EvidenceRef` 实际在 **§11**、`不可变版本语义` 实际在 **§12**，两处文案的节号**均与实际相反**。

**代码位置（回源）**
| 文件:行 | 内容 |
|---|---|
| `frontend/src/components/product-center/ProductInheritedChapters.vue:74` | `{{ block.spec.no }}. {{ block.spec.title }}`（标题用登记章号） |
| `frontend/src/components/product-center/ProductInheritedChapters.vue:94` | `该产品卡未包含第 {{ block.spec.no }} 节（…）原文` |
| `frontend/src/components/product-center/ProductGovernancePanel.vue:104` | `该产品卡未包含第 11 节（不可变版本语义）原文`（**写死**） |

**与「自报修复」的关系（精确表述，不夸大）**：epoch 1 说明称修复「版本区写死节号」，`git diff c0843e3..396ff23 -- ProductGovernancePanel.vue` 显示**只改了正常路径的 source 行**（`第 11 节原文 ·` → `{{ immutableVersion.title }} 原文 ·`）；同文件 `:104` 的**缺失分支**仍写死「第 11 节」，承接区 `:74/:94` 仍用登记章号。⇒ 该缺陷类**未彻底分离**（正常路径已正确，另一分支残留）。

**不得回退的部分**（已由我 13/13 + 变异复验确认）：`cardChapter.ts:57-73` 的**定位**已改为「标题优先、节号前缀兜底」；`pc-inherited-c12-content` 在 FIN 卡绑 §11、`pc-immutable-source` 绑 §12 **均正确**。

### QA-B2【阻断 · 低】**缺失文案归因不实** —— 把「来源不可得」断言成「该卡未含该节」

**现象**：产品卡接口不可达时，**同一区块**并列两句互相矛盾/无据的表述：meta 说「**来源：来源标识不可得**」，缺失文案却断言「**该产品卡未包含第 N 节（…）原文**」。来源不可读时**无法**判定该卡是否含该节 ⇒ 属对**未验证事实**的事实断言。

- 最小复现：同 QA-B1「复现 B」；原始产物 `independent-qa-formal-probe-faultcard-FIN003-20260923-1227.json`。
- 影响：不会伪造内容（该路径**未**渲染任何原文，`CONTENT_DESPITE_ABORT` 0 起），但会把「读取失败」呈现为「受控制品缺少该节」，可能误导读者对产品卡完整性的判断。
- 与 loop 口径关系：`LOOP.yaml.objective` 要求「如实呈现…有效状态」、`exit_criteria` #2「无空占位」，且 `ProductCenterView.vue:73` 的注释自述「如实：不伪造来源；承接区/版本区会分别显示『来源标识不可得』『未包含该节原文』」—— 该自述把两者并列为「如实」，我判定**后者不成立**。

### QA-N1【非阻断 · 观察（测试侧）】`ProductInheritedChapters.spec.ts` 未覆盖 absent 分支的节号正确性
现状单测与 E2E 均只断言「具名缺失存在」，未断言该文案的**节号与实际节号一致** ⇒ QA-B1/QA-B2 两类缺陷在现有断言下**不可见**（建议补：以 `PROD-FIN-*` 夹具断 absent 文案不得含登记章号）。

---

## 四、签署（§4 逐字执行）

```bash
python3 scripts/qa_attest.py --loop PC-i1-chapter-inheritance \
  --actor independent_qa --session qa-pc-i1-formal-20260923-1227 --decision reject \
  --evidence loops/PC-i1-chapter-inheritance/evidence/independent-qa-formal-20260923-1227.md
```

- `--actor` = `independent_qa`（**≠** `STATE.json.implementation_actor = tech_lead`）；未代签、未把 BLOCKED 当 pass。
- 脚本前置（`STATE.json.status=ready_for_independent_qa`、`loop_guard --evidence-only` 通过、报告在仓内）**均已满足**（§〇）。
- 结果：`EVIDENCE.json.independent_qa.status = reject`、`STATE.json.status = blocked`、`blocking_reason = INDEPENDENT_QA_REJECTED`。

**解除路径（建议，供 TL/Owner）**
1. 置 `STATE.json.status = in_progress`（按协议回实现态），由实现者修 QA-B1/QA-B2（建议做法：`actualSectionNo()` 对 absent 分支返回 `null` 并渲染「该卡未包含第 N 节」时改用**实际节号或「节号不可得」**；来源不可得时文案与 meta 一致，改为「来源不可得 ⇒ 无法判定该卡是否含第 N 节」；版本区 `:104` 同口径；区块标题区分 R2 章号与卡内节号）；
2. 补 QA-N1 的反向断言（`PROD-FIN-*` 夹具）；
3. 重跑并重记 `frontend_unit` / `e2e_parity`（`frontend_typecheck` 亦建议重记），再交独立 QA。

---

## 五、未覆盖 / 存疑（**必填**）

1. **我自己的探针曾报错判（已自纠，未据此下任何产品结论）**：`probe-landing` 初版把 C1 落点定位在**首屏**，导致 13/13 报 `C1_LANDING` 假违规；回源 `ProductChapterStack.vue:90` 后确认 `summary.oneSentenceDefinition` 渲染在 **OVERVIEW 章正文**，改判据后 0 违规。该假违规**恰成为 C1 判据非空转的证据**（同一断言能判红），记录在此以免被误读为产品缺陷。
2. **C10「为空时具名标注」分支无真实数据覆盖**：13/13 产品 `salesBoundaries` 均非空（2–3 条）⇒ `pc-inherited-c10-contract-empty` 只由代码/单测覆盖，**未由真实数据验证**。
3. **未做逐条事实等价比对**：W1-g §2.1 已如实声明「等价层面未验证」；我同样只核到「落点/来源/字段一致性」层面，**未**把 P38 每节文本与新版呈现逐条对照。⇒ 「事实不丢」在等价层面**仍未知**。
4. **门禁证据未绑定 tree hash + 工作树含大量非 PC-i1 脏改动**：`EVIDENCE.json` 不记录被测 tree；复验期 `git status --short` 有 **455** 条（含 `frontend/src/router/index.ts`、`frontend/vite.config.ts`、`frontend/e2e/experience-shell.spec.ts`、`frontend/src/components/shell/**` 等**非本 loop scope** 的未提交改动）。⇒ 门禁结论只对**当时工作树**成立。旁证：我复跑 `npx vitest run` 得 `69 files / 377 tests`，与门禁日志**逐字相同**。
5. **E2E 门禁命令在本会话出现一次 3-failed，我判为「本机会话卫生」而非产品/门禁缺陷（但建议收口知悉）**：`playwright.config.ts:17` 的 `reuseExistingServer=!CI` 会**复用已在监听的 5173**；本机 **8080 亦在监听且返回 401**（非被测后端）。我首次复跑因与上一轮被后台化的运行**并发**、复用了未注入 `VITE_API_PROXY_TARGET` 的 dev server ⇒ 走默认 8080 ⇒ `page.request.get` 得 **HTTP 401**、目录族计数 0 ⇒ 3 failed。清场后**同命令逐字复跑 3 passed**。⇒ 该失败**不可复现于干净环境**，与门禁日志（11:45 3 passed）不矛盾；但说明该门禁命令**对环境中的残留 5173 敏感**（建议：`reuseExistingServer=false` 或显式 `--port` 隔离，属**另案**，未列入阻断项）。
6. **`repro_baseline` 反向门禁**（`GKB-baseline-hardening`）与 `semantic-consumption` / `gate-injection-tests` 的判定合理性我只核到「已如实声明、未被计为通过」，**未**评估其判定口径本身。
7. **旧版（P38）侧操作路径基线未重算**：W1-g 旧版列**引用** R2 `06` §6，我未据旧版 DOM 重新计数 ⇒ 「操作路径更短」的**对照侧**仍属引用。
8. **生产构建产物（`vite build`）未验**：本轮只测 dev server（15173 / playwright webServer 5173）。
9. **未评估**：`PRICING`（PC3）/ `FAQ`（PC4）未来有数据时的渲染；LightRAG(9621) 检索质量（只读、未 publish/retract）；KERT(8107) 未做写操作；未改 KERT 工作区。
10. **未重新裁定**既有 7 条失败（`analytics` ×4 / `A3` / `D1` / `customer-detail`）：沿用原归属（环境未就绪 / P1 已转 PI-1 / 测试侧 locator），与本轮判据无关。

---

## 六、环境变动登记（只读复验；写入仅限 QA 产物区）

| 类别 | 明细 |
|---|---|
| 只读 | 13 产品页面 × 多轮（`probe-pci1` / `probe-landing` / `probe-heading`）；`PROD-FIN-003` 故障注入 1 轮（`probe-faultcard`）；接口 `GET /api/v1/product-center/products{,/{id}}`、`GET /api/v1/product-knowledge/cards/{id}`；门禁复跑 `make check`、`loop_guard.py`（默认 / `--instances-check`） |
| 写入（QA 产物，**均在 QA 自留区**） | `frontend/test-results/qa-formal-pci1-20260923/**`（4 支探针 + 其 JSON + 日志）、`…/qa-mut-{prefix,c10,landing}/**`（变异产物）、`test-results/qa-formal-甲/**`、`test-results/qa-formal-甲2/**`（Playwright 自建输出目录） |
| 新增入 loop evidence（**仅新增，未改既有**） | 本报告 · `independent-qa-formal-per-chapter-20260923-1227.json` · 4 个探针（`.mjs`）+ 4 份探针 JSON + 3 份变异 JSON + 2 份门禁日志（sha256 见 §八） |
| 端口/进程 | Playwright 按其 config 自起/回收 webServer(5173)；复验结束**无 5173 监听**；15173 / 18080 全程未重启；未触碰 8080（该端口有非被测服务在监听，返回 401） |
| 未做 | 未改任何产品代码 / 测试断言 / 门禁脚本 / `specs/` · 未 `git add`/commit/push · 未动 LightRAG / KERT · **未**改 `EVIDENCE.json` / `STATE.json` / `NEXT_SESSION.md`（其变更**只**由 `qa_attest.py` 依 §四 产生） |

---

## 七、原始产物索引

| 产物 | 路径（`loops/PC-i1-chapter-inheritance/evidence/`） | 说明 |
|---|---|---|
| 逐章/落点结构化证据（主证据） | `independent-qa-formal-per-chapter-20260923-1227.json` | 13 产品 × 12 章 = 156；`landingViolations=0`、`misalignedCards=[FIN-001,002,003]`、`misalignmentConflicts=6`（结构对齐 `w1-per-chapter-evidence.json`） |
| 探针 1（章级承接 + C11 + 错位） | `independent-qa-formal-probe-pci1-20260923-1227.{mjs,json}` | 13 产品 × 7 块 + 版本区；0 违规 |
| 探针 2（C1/C3/C4/C5/C7/C10 落点） | `independent-qa-formal-probe-landing-20260923-1227.{mjs,json}` | 13 产品 × 6 落点；0 违规 |
| 探针 3（故障注入） | `independent-qa-formal-probe-faultcard-20260923-1227.{mjs}` · `…-probe-faultcard-FIN003-20260923-1227.json` | **QA-B1/QA-B2 的直接证据**（DOM 原文 + `findings`） |
| 探针 4（标题 vs meta 节号） | `independent-qa-formal-probe-heading-20260923-1227.{mjs,json}` | **QA-B1 正常路径证据** |
| 变异复验 | `…-mutant-prefix-…json`（18 违规）· `…-mutant-c10wrong-…json`（29 违规）· `…-mutant-landing-…json`（26 违规） | 证明 3 组判据**非空转** |
| 甲 · 单测原文 | `independent-qa-formal-vitest-20260923-1227.log` | `VITEST_EXIT=0`，69 files / 377 tests |
| 甲 · E2E 原文 | `independent-qa-formal-playwright-pc1-20260923-1227.log` | 干净复跑 `3 passed` |
| 实现者证据（被核对象） | `w1-per-chapter-evidence.json` · `w1-g-parity-2026-09-23T0344.json` · `EVIDENCE.json` · `LOOP.yaml` · `memory/waves/W0-ITER.md` · `memory/waves/W1-g-同产品对照.md` | 只读引用，未改 |
| 既有独立 QA 产物（**非我所有，未删改**） | `independent-qa-pc-i1-20260923-1101.md` 等 7 个 | 哈希见 `EVIDENCE.md`「独立 QA — 导航」 |
| 临时文件（未入仓） | `/tmp/**` | 无 |

**本轮已入仓 QA 产物 sha256（前 16）**

```text
1e0bdf2db82c23e9  independent-qa-formal-per-chapter-20260923-1227.json
75a0a48b637bb3fa  independent-qa-formal-probe-pci1-20260923-1227.json
9d51d73cdc50fd35  independent-qa-formal-probe-landing-20260923-1227.json
3016e58cd38e8f82  independent-qa-formal-probe-faultcard-FIN003-20260923-1227.json
428de1671d3ba686  independent-qa-formal-probe-heading-20260923-1227.json
a03432570b3609cb  independent-qa-formal-mutant-prefix-20260923-1227.json
5615fc73229fcd57  independent-qa-formal-mutant-c10wrong-20260923-1227.json
c1068c65e8b772ac  independent-qa-formal-mutant-landing-20260923-1227.json
d6d5e6df7830cec6  independent-qa-formal-probe-pci1-20260923-1227.mjs
fbd40925964f7ea0  independent-qa-formal-probe-landing-20260923-1227.mjs
d1fc06d8b1d21f3d  independent-qa-formal-probe-faultcard-20260923-1227.mjs
e7fa5921f6a8d8ea  independent-qa-formal-probe-heading-20260923-1227.mjs
a9ca1b16f6315bc2  independent-qa-formal-vitest-20260923-1227.log
a4693ad2dce1fad8  independent-qa-formal-playwright-pc1-20260923-1227.log
```

---

## 八、一句话结论

**PC-i1 本轮不得签 `QA_PASS`（`--decision reject`）**：Owner 列举的 **9 条判据我已逐条独立复现且全部通过**（C6/C9 独立区块未被比较表替代、C11 版本区四要素齐备、C2/C3/C10 指名引用与产品级 `salesBoundaries` 29 条逐条一致、C12 在 `PROD-FIN-*` 呈现 `EvidenceRef` 原文而其余卡具名缺失、卡间节号错位在**正常路径**已正确绑定 §12/§11 并经变异复验证明判据非空转、W1-g 文档诚实且保留「事实等价未验证」、门禁命令逐字一致且 6/6 哈希自洽、`semantic-consumption=NOT READY`/`gate-injection-tests=INCONCLUSIVE` 未被粉饰）；**未满足项为 2 项具名阻断**：**QA-B1**「登记章号 vs 实际节号未彻底分离」——`PROD-FIN-*` 上 C12 区块标题仍写「12.」而 meta 写「第 11 节」，卡片接口不可达时更输出「该产品卡未包含第 **12** 节（EvidenceRef）」与「未包含第 **11** 节（不可变版本语义）」两处**与实际相反**的断言（`ProductInheritedChapters.vue:74/:94`、`ProductGovernancePanel.vue:104`）；**QA-B2** 同路径把「来源不可得」断言成「该卡未含该节」（对未验证事实作事实断言）。另有 1 项非阻断测试侧缺口（QA-N1：absent 分支节号正确性无断言）。修复面为 3 处渲染表达式 + 1 处文案口径，建议按 §四「解除路径」处理后重记 `frontend_unit`/`e2e_parity` 再交回独立 QA。

---

*报告生成：2026-09-23 12:35（本地）× actor=`independent_qa` × session=`qa-pc-i1-formal-20260923-1227` × 模式=**独立 QA 正式复验（含 `qa_attest.py` 签署）**。*
