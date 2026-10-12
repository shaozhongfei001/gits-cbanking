# PC-i1 收口 Wave 1 / 路 1C —— 未跟踪与已修改文件只读分类清单

- 角色：`repo_curator`（只读甄别）
- 仓库：`/home/szf/dev/gits-cbanking`
- 分支 / HEAD：`recover/PI-ARCH-product-catalog` @ `652a23f09f5139261791d977958f2e2ebeac1c0f`
  （HEAD 提交：`chore(pc-i1)+docs(loops): 交棒独立 QA（status=ready_for_independent_qa）+ 多角色派工与并行/串行编排`）
- 采样时刻：2026-09-23 12:26（CST）
- **声明：本轮未做任何清理 / 提交 / 删除 / 移动 / 重命名 / 编辑既有文件；未执行 `git add|commit|rm|clean|checkout|stash|reset|update-index`。唯一写入为 `evidence/pc-i1-closure/**`。**

---

## 1. 基线计数（M / D / ??）

命令与原始输出已留档：

- `evidence/pc-i1-closure/diag4-git-status-porcelain-20260923-122605.txt`
- `evidence/pc-i1-closure/diag4-git-status-uall-20260923-122605.txt`

```bash
git status --porcelain | wc -l        # 456
git status --porcelain -uall | wc -l  # 918
```

| 类别 | porcelain 口径 | `-uall` 展开口径 | 说明 |
|---|---|---|---|
| ` M` 已修改（工作树） | **35** | 35 | 无暂存改动 |
| `M ` 已修改（暂存） | 0 | 0 | 暂存区干净 |
| ` D` 已删除（工作树） | **2** | 2 | 无暂存删除 |
| `??` 未跟踪 | **419** | **881** | porcelain 对未跟踪**目录折叠**，展开后 881 |
| `R`/`C` 重命名/复制 | 0 | 0 | — |
| 合计条目 | 456 | 918 | |

**与 TL 上次观测的差异**：TL 记录为「36 已修改 / 418 未跟踪」，本次实测为「**35 已修改（+2 删除）** / **419 未跟踪**」。

- 未跟踪 419 ≈ 418（差 1，且本次实测期间 `evidence/` 正被并发写入，见 §6）；
- 已修改 35 vs 36：若 TL 将 1 个删除项计入「已修改」则为 37；更可能是采样时点不同（工作树正被多 Agent 并发写入）。**建议以本次实测为准**。

> 重要前提：本次甄别期间工作树**正在被并发写入**（`evidence/pc-i1-closure/` 未跟踪条目在 5 分钟内由 5 → 28；`pw-analytics-baseline/` 于 12:25 新建）。因此所有计数均为**时点快照**，不具幂等性。

---

## 2. A–G 分类表

### A. 他人未完成功能件 —— 归属：`loops/AN0-ccrm-analytics-landing`（在飞，qa FAIL 待复判）

**判定依据（可复核）**：

1. `loops/AN0-ccrm-analytics-landing/LOOP.yaml`：`"title": "CCRM 对公经营分析落地：GITS 展示 + KERT 分析服务/SKILL + DuckDB 造数（Owner 直派）"`，`"status": "ready_for_independent_qa"`。
2. `loops/AN0-ccrm-analytics-landing/STATE.json`：`current_phase = W1_delivered__ALL_6_IMPLEMENTATION_GATES_PASS__INDEPENDENT_QA_COMPLETED_VERDICT_FAIL__pending_TL_repair__pending_OWNER_signoff`，`qa_verdict = PENDING_RE_QA`。
3. `loops/AN0-.../evidence/` 含 `frontend_analytics_unit-*`、`frontend_typecheck-*`、`e2e_analytics-*`、`analytics_params_failclosed-*` 等 2026-09-22 起日志。
4. `git diff -- frontend/src/layouts/navConfig.ts` 内容为 domain 联合类型**新增 `'analytics'`**（`git diff` 第 1307–1308 行），`frontend/src/router/index.ts` +44 行为新增 analytics 路由。

| 数量 | 代表路径 | 建议动作 |
|---|---|---|
| 16（未跟踪） | `frontend/src/api/analytics.ts` · `frontend/src/components/analytics/{AnalyticsFilterBar,AnalyticsPageNav,AnalyticsResultsPanel,BarList,TrendChart}.vue` · `frontend/src/composables/useAnalyticsMeta.ts` · `frontend/src/theme/naiveTheme.ts` + `theme/__tests__/naiveTheme.spec.ts` · `frontend/src/views/Analytics{ComboQuery,Monitor,OperatingMetrics,Segment}View.vue` · `frontend/src/views/__tests__/AnalyticsViews.spec.ts` · `frontend/e2e/analytics.spec.ts` | **保留**（等 AN0 修复轮提交）；本轮不处置 |
| 8（已修改） | `frontend/src/App.vue` · `frontend/src/router/index.ts` · `frontend/src/layouts/navConfig.ts` · `frontend/src/components/shell/AppSidebar.vue` · `frontend/src/components/shell/__tests__/AppSidebar.spec.ts` · `frontend/src/assets/styles/theme.css` · `frontend/vite.config.ts` · `frontend/e2e/experience-shell.spec.ts` | **保留**；见 §5 高危 H-2 |
| 1（归属待定） | `frontend/DESIGN.md`（无 git 历史，未读内容） | **待 Owner 决定** |

> 注：`frontend/src/**` 属实施方写入面，本报告**只读分类、不触碰**。

### B. 构建产物 / 运行时产物

| 路径 | 忽略状态（`git check-ignore -v`） | 处置建议 |
|---|---|---|
| `frontend/dist/index.html`（**M**） | **NOT-IGNORED**（`.gitignore:5 frontend/dist/` 虽在册，但该文件**已被强制跟踪**：`git ls-files frontend/dist` = 4 个文件） | 构建产物入库遗留；**不在本轮处置**，建议 Owner 后续单独裁决（移出跟踪 或 改为构建期生成） |
| `**/target/` | `.gitignore:2 target/`、`:3 **/target/` —— 无未跟踪命中 ✓ | 保持 |
| `frontend/test-results/` | `.gitignore:37 test-results/` ✓ | 保持 |
| `frontend/node_modules/` | `.gitignore:11` ✓ | 保持 |
| `.ua/`（含 `.ua/knowledge-graph.json`） | `.gitignore:62 .ua/` ✓ | 保持 |
| `*.log` | `.gitignore:33 *.log`，但 `:67-68` **显式反忽略** `loops/**/evidence/*.log` | **不建议改忽略**（属 loop 证据，有意入仓）；见 §4 体量 |
| `diagrams/**` | **NOT-IGNORED**（`diagrams/` 已有 9 个受跟踪文件） | 129 项未跟踪；建议（**不执行**）：`*.visual-check.*` 渲染中间产物（PNG/HTML/JSON）可考虑忽略；需 Owner 裁决 |
| `docs/review/**`（含 `*.tar.gz` / `*.zip`） | **NOT-IGNORED** | 见 §3、§4 |

**结论**：构建/运行时产物**基本已被 `.gitignore` 覆盖**；仅 `frontend/dist/`（被强制跟踪）与 `diagrams/`、`docs/review/` 三处未覆盖，均为**历史遗留或交付物**，不建议在收口轮内新增忽略规则（会改变工作树状态且属跨 Loop 决策）。

### C. 门禁 / 工具脚本的未提交改动

**C-1 已由 Owner 裁定入仓（已提交、当前无未提交改动）**

```bash
git ls-files scripts | grep -E 'record_gate|loop_guard'
# scripts/loop_guard.py
# scripts/record_gate.py
```
依据：HEAD 前序提交 `c5cb6fd chore(scripts): 入仓 record_gate.py 的既有未提交改动（QA-4 归属裁定：入仓）`；且 `git status` 中两者**均无 M/?? 条目**。→ **已裁定，无待办**。

**C-2 已跟踪但有未提交改动（属 GK17 W8 在飞）**

| 路径 | 改动量 | 建议 |
|---|---|---|
| `scripts/gk17_prodcard_to_rdf.py` | +94 行级 | 保留；随 `GK17-ontology-unified-map` W8 提交入仓 |
| `scripts/gk17_triple_consistency_check.py` | +421 行级 | 同上 |

（`scripts/gk17_ref_anchor_check.py`、`scripts/onto1_sim_projection.py` 已跟踪且**无改动**。）

**C-3 仍待裁定 —— 46 个未跟踪脚本**

| 分组 | 数量 | 代表路径 | 建议 |
|---|---|---|---|
| `scripts/onto1_*.py` | **44** | `onto1_gate_log.py` · `onto1_evidence_board_check.py` · `onto1_zip_manifest_verify.py` · `onto1_construction_plan.py` · `onto1_consumer_scan.py`（+ `_tests.py`） | 随 `ONTO1-ontology-split` loop 收口入仓；**本轮待 Owner 决定** |
| `scripts/ua_index_gate.py` · `scripts/ua_index_gate_tests.py` | **2** | — | **建议优先裁定**：`Makefile:99 index-status` 调用 `scripts/ua_index_gate.py`、`Makefile:102 index-gate-tests` 调用 `scripts/ua_index_gate_tests.py`。脚本未入仓 ⇒ **干净检出上这两个 Make 目标会因脚本缺失而失败**。建议随 `code-fact-index` 规则一并入仓（**待 Owner 决定**） |

### D. 既存脏文件（与本轮工作无关）

| 路径 | 状态 | 建议动作 |
|---|---|---|
| `.codebuddy/rules/contract-check/RULE.mdc`、`.codebuddy/rules/senior-workflow/RULE.mdc` | M | **保留现状，不在本轮处置** |
| `.codebuddy/rules/code-fact-index/RULE.mdc` | ??（新增，与 `AGENTS.md` 修改配套） | 保留现状 |
| `.understandignore` | M（+12/-8：注释掉 A 节 `specs/ generated/ docs/dd/ evidence/ loops/ .codebuddy/`，注明「2026-09-15 由 Owner 裁决放开 / UA-D9」） | 保留现状（已有 Owner 裁决背书） |
| `AGENTS.md`、`AI_GUIDE.md`、`FAILURES.md`、`Makefile` | M | 保留现状 |
| `docs/governance/CODE-FACT-INDEX-PROCESS.md`（新增）、`docs/architecture/UNDERSTAND_ANYTHING_CODE_LEVEL_ASSESSMENT.md`、`docs/dispatch/GK17-ontology-unified-map-长篇编排-V1.0.md` | ??（1） / M（2） | 保留现状 |
| `evidence/gk-ke-capability-probe/report.json`、`evidence/gk-ke-chain-trace/trace.json` | M | 保留现状 |
| `generated/manifest.json`、`generated/product-knowledge/field-policy.schema.json` | M | ⚠ **非普通脏文件 —— 见 §5 高危 H-1** |
| `specs/knowledge-architecture/instances/product/products.ttl` | M | 保留现状（GK17 实例数据在飞） |
| `loops/GK17-ontology-unified-map/**` | 8 M + 15 ??（含 `memory/ORCHESTRATOR.md`、`memory/waves/W8-PLAN.md`、`evidence/*.log`） | 保留现状（GK17 在飞） |
| `loops/_template/memory/{NEXT_SESSION.md,PROTOCOL.md}`（M）、`loops/_template/memory/INDEX_BASIS.md`（??） | M + ?? | 保留现状 |

### E. 删除项（` D`）

| 路径 | 影响面 | 建议 |
|---|---|---|
| `diagrams/architecture.html` | 旧架构图（由 `49b175f docs(diagrams): add architecture and flow diagrams (HTML/PNG/MD) + generators` 引入）。无代码/门禁引用；仓库内引用仅在文档与评审快照中 | **长期既存，非本轮新增** —— 见下方证据；建议保留现状，或由 Owner 裁定「显式提交删除」以消除评审快照噪声 |
| `diagrams/architecture.png` | 同上 | 同上 |

**"长期既存"证据（可复核）**：

```text
HANDOFF-CURSOR-P24.md:95: **问题**: `diagrams/architecture.png` 已删除（旧图含已移除节点），CI 无 diagram 生成步骤
docs/review/ONTO1-PREP-INDEPENDENT-REVIEW-20260921-R2…R4/ANCHORS.json:{18,19}: " D diagrams/architecture.html" / " D diagrams/architecture.png"
```
即：自 2026-09-21 起的 ONTO1 独立评审快照已记录这两个 ` D` 条目 —— 属**跨轮既存状态**，本轮未新增删除。

### F. 体量 / 风险前 10（详见 §3、§4）

### G. 其余 / 无法归类 —— 均属各自 Loop 的在飞交付物

| 分组 | 数量（`-uall`） | 说明 | 建议 |
|---|---|---|---|
| `loops/ONTO1-ontology-split/**` | 375（evidence 241 + memory 50 + 顶层 9） | ONTO1 在飞 | 随 Loop 收口入仓 |
| `docs/review/**` | 286 | ONTO1 独立评审包 `R2/R3/R4`（各 53–54）+ `ARCH-ONTO-2026-001` 委员会包（26） | 交付物，随 Loop 收口 |
| `docs/architecture/*-DRAFT.md` 等 | 21 个 DRAFT + 若干 | ONTO1 / ONTOLOGY-SPLIT 系列 | 随 Loop 收口 |
| `docs/dispatch/ONTO1-*.md`、`ONTO-SPLIT-*.md`、`GK17-W0-*.md`、`CCRM-经营分析菜单登记-V1.0.md` | 14 | 派工单 | 随 Loop 收口 |
| 无法归类 | 1 | `frontend/DESIGN.md` | **待 Owner 决定** |

---

## 3. Top 10 体量（`du -k`，未跟踪 + 已修改全体）

全体未跟踪 + 已修改条目合计 ≈ **80.6 MB**。

| # | 路径 | 大小 | 备注 |
|---|---|---|---|
| 1 | `loops/ONTO1-ontology-split/evidence/consumer-scan-hits.jsonl` | **9.9 MB** | JSONL 全量消费者扫描命中 |
| 2–4 | `docs/review/ONTO1-PREP-INDEPENDENT-REVIEW-20260921-{R2,R3,R4}/EVIDENCE/loops/…/consumer-scan-hits.jsonl` | **9.9 MB ×3 ≈ 30 MB** | `cmp` 验证**与 #1 字节完全相同 ⇒ 纯重复副本** |
| 5–18 | `diagrams/*.html`（`kert-knowledge-pipeline` 824K、`ontology-model-design`/`gits-app-to-kert-call-chain`/`activation-contract-into-kert` 各 808K、`ontology-governance-landscape` 804K …） | 784–824 KB ×14 | 自包含 HTML |
| 19 | `loops/AN0-ccrm-analytics-landing/evidence/qa-an0-001/probes/kert_8107_service_console.log` | **752 KB** | 服务控制台日志（运行期输出） |
| 20 | `docs/review/ONTO1-PREP-INDEPENDENT-REVIEW-20260921-R4.tar.gz` | 440 KB | 交付包 |
| — | `docs/review/ONTO1-…-{R3,R2}.tar.gz`、`ONTO1-PREP-INDEPENDENT-REVIEW-20260921.tar.gz` | 436 / 432 / 208 KB | 同上 |
| — | `loops/ONTO1-…/evidence/obligation-triage.csv` + 4 份副本 | 396 KB ×5 | 重复副本 |
| — | `loops/ONTO1-…/evidence/prep/a2-disposition-ledger.json` | 388 KB | — |
| — | `loops/ONTO1-…/evidence/prep/check-strength-audit.json` | 268 KB | — |
| — | `diagrams/*.visual-check.2048x1320.{dark,light}.png` | 200–344 KB ×N | 渲染中间产物 |
| — | `docs/review/ARCH-ONTO-2026-001-committee-package.zip` | — | 委员会交付包 |

扩展名分布（全体条目 918）：`md 277` · `json 151` · `log 170` · `png 69` · `py 95` · `html 35` · `vue 11` · `ts 11` · `zip 1` · `tar.gz 4`。

---

## 4. 敏感与二进制风险项

| 检查 | 命令（只报路径/类型，不打印内容） | 结果 |
|---|---|---|
| 敏感**文件名** | `grep -iE 'key\|token\|secret\|password\|credential\|\.env\|pem\|p12\|keystore'` | **0 命中** |
| 敏感**内容** | `grep -lIE 'sk-[A-Za-z0-9]{16,}\|-----BEGIN [A-Z ]*PRIVATE KEY\|DSEEK_2026_SZF_KEY\|ghp_[A-Za-z0-9]{20,}'` | **0 命中** |
| 个人绝对路径 | `grep -lIE '/home/szf\|/Users/[a-z]+/'` | **0 命中** |
| 二进制入库风险 | `zip 1 · tar.gz 4 · png 69`（共 74 项） | 见下 |

**二进制风险清单（建议 Owner 裁定，不在本轮处置）**

- **归档 5 个**：`docs/review/ARCH-ONTO-2026-001-committee-package.zip`、`docs/review/ONTO1-PREP-INDEPENDENT-REVIEW-20260921{-R2,-R3,-R4,}.tar.gz`（交付包，另有配套 `.sha256`）。
- **PNG 69 个**：以 `diagrams/*.visual-check.{1440x900,2048x1320}.{dark,light}.png` 为主（单图 4 张渲染中间产物），另含 `evidence/an0-ccrm-analytics-qa/shots/*.png`。
- 体量集中项见 §3；其中 **30 MB 为同一 JSONL 的 3 份字节级重复副本**（R2/R3/R4 评审快照内嵌全量证据）—— 若后续需要瘦身，这是收益最高的目标，但**属跨 Loop 决策，本轮不动**。
- `loops/**/evidence/*.log` 170 个未跟踪日志为 `.gitignore:67-68` **有意反忽略**（loop 证据），不建议改忽略；其中 `kert_8107_service_console.log`（752 KB）为服务控制台运行期输出，如含凭据请在提交前自查（本报告未逐字节审阅其内容，见 §6）。

---

## 5. 高危项

### H-1（实质性 · 合同制品漂移）`generated/` 领先于 HEAD，而 HEAD 上"源已领先生成物"

**事实（可复核）**

```bash
grep -n -A6 '"CTR-PK-FLD-001"' specs/CONTRACT_INDEX.yaml
# 626:  "authority_source": "specs/product-knowledge/field-policy.schema.json"
# 634:  "generated": [ "generated/product-knowledge/field-policy.schema.json" ]

git status --porcelain -- specs/product-knowledge/field-policy.schema.json generated/product-knowledge/  # → 源无输出；生成物 M
git --no-pager diff --stat -- generated/product-knowledge/field-policy.schema.json
#  … | 395 +++++++++++++++++++++++++   （+395 / -0）
git --no-pager log --oneline -1 -- specs/product-knowledge/field-policy.schema.json
#  bcf124e feat(contracts): PC8 T3 —— CTR-PK-FLD-001 补 5 族字段策略正例（examples 2→7）
git --no-pager log --oneline -1 -- generated/product-knowledge/field-policy.schema.json
#  2ceb66d contract(product-knowledge): DEMO 语义与解读合同登记，修复生成管线阻塞
git merge-base --is-ancestor 2ceb66d bcf124e && echo YES   # YES  ⇒ 生成物提交早于源提交
ls -l --time-style=long-iso generated/product-knowledge/field-policy.schema.json
#  -r--r--r-- 20654 2026-09-22 22:58   （只读位，晚于源文件 18:27）
```

- `generated/manifest.json` 中 `product-knowledge/field-policy.schema.json` 与 `CTR-PK-FLD-001` 两个 sha256 同步变更（+4/-4）。
- `specs/product-knowledge/field-policy.schema.json` **内容 == HEAD**（无 M）；其生成物相对 HEAD **+395/-0 行未提交**，新增内容为带 `"_case"` 标记的**正例用例**（与 `bcf124e examples 2→7` 语义吻合）。
- 源提交 `bcf124e` **晚于**生成物提交 `2ceb66d`，即：**HEAD 上源已领先生成物（生成物未随之更新入库）**；本地工作树中生成物**已被重新生成**（只读权限位 + mtime 09-22 22:58，符合 `scripts/generate-contracts.sh` 产物特征）。

**推断（需回源确认，本报告不作事实断言）**：本地曾执行 `make generate`（`Makefile:20 → scripts/generate-contracts.sh`）将源变更注入生成物，但成果未提交；因此
(a) 在 **HEAD 干净检出**上，合同源与生成物不一致 ⇒ 完整性/哈希类门禁存在失败风险；
(b) 在 **当前工作树**上，生成物是"已补齐"的 ⇒ 用工作树跑门禁会**通过**，从而可能把漂移掩盖为 PASS。

**影响**：PC-i1 正在签署的 revision（HEAD `652a23f`）若引用 `generated/**` 哈希或合同一致性门禁结果，需先明确**以哪一份为准**；否则"工作树全绿"与"HEAD 全绿"可能给出相反结论。

**建议（不在本轮执行）**：由 Owner / 合同 Owner（`knowledge_architecture_owner`）裁定其一：
1. 将再生成的 `generated/product-knowledge/field-policy.schema.json` + `generated/manifest.json` 提交入库（消除源领先）；或
2. 判定为工作树污染，`git restore generated/` 回退。
在此之前：**PC-i1 独立 QA 不得以"工作树 `make check` 全绿"作为合同一致性 PASS 依据**，应在干净检出上复核。

### H-2（一致性 · PC-i1 独立 QA 存在"混入他人在飞改动"风险）

**PC-i1 自身工作面无残留（好）**

```bash
git status --porcelain -uall | grep -i 'pc-i1\|chapter-inheritance'
# → 仅 evidence/pc-i1-closure/**（本收口证据目录，属有意产出）
git ls-files loops/PC-i1-chapter-inheritance | wc -l   # 51（受跟踪）
git status --porcelain -uall | grep -i 'product-center'  # → 空 ⇒ 无未提交改动
git status --porcelain -- frontend/src/components/product-center  # → 空
```
⇒ **未发现对 `loops/PC-i1-chapter-inheritance/**` 或 `frontend/src/components/product-center/**` 的直接污染**。

**但工作树 ≠ HEAD，且混入如下他人在飞改动**

- AN0：**8 个已修改 + 16 个未跟踪**前端文件，其中 `frontend/e2e/experience-shell.spec.ts`、`frontend/src/components/shell/__tests__/AppSidebar.spec.ts`、`frontend/vite.config.ts` 会**直接影响 e2e / 单测 / 构建**的判定结果；
- H-1：`generated/**` 漂移；
- `loops/GK17-ontology-unified-map/**`（8 M + 15 ??）与 `loops/ONTO1-ontology-split/**`（375 ??）未提交。

**结论**：**PC-i1 的独立 QA 必须在干净检出（HEAD `652a23f`）上复跑 e2e / 类型检查 / 门禁**，或至少在报告中显式声明"工作树已混入 AN0/GK17/ONTO1 未提交改动"，否则 e2e 结论不可归因于 PC-i1 revision。已按指令即时告警 `main`。
（完整 diff 根因：`git diff` 中不含任何 `PC-i1` 语义改动；`frontend/src/**` 改动全部指向 `'analytics'` domain，见 §2-A 依据 4。）

---

## 6. 未覆盖 / 存疑（必填）

1. **工作树为动态目标**：甄别期间并发写入（`evidence/` 未跟踪条目 5 → 28，`pw-analytics-baseline/` 12:25 新建）。所有计数为 12:26 时点快照；§1 与 TL 观测的 1 项差异可能源于此。
2. **未扫内容**：仅对**文本文件**做敏感内容 grep；`*.zip` / `*.tar.gz`（5 个）、`*.webm`（`evidence/pc-i1-closure/pw-analytics-baseline/**` 内的 Playwright 原始产物）、`*.jpeg`、`*.png` **未解包/未 OCR**，其内容敏感性未判定。仅报路径与类型。
3. **未执行（有意）**：`make generate` / `make check` / `make index-status` —— 其中 `generate` 会**改写 `generated/`**，违反只读铁律；H-1 的"推断"部分因此**未经执行验证**，请以"回源确认"对待。
4. **归属未证**：`frontend/DESIGN.md`（无 git 历史）归属不明 ⇒ 记「待 Owner 决定」。`loops/_template/memory/INDEX_BASIS.md`（??）与 `loops/_template/memory/{NEXT_SESSION,PROTOCOL}.md`（M）同属模板层，未进一步定责。
5. **未验证**：C-3 中 `scripts/ua_index_gate*.py` "未入仓 ⇒ `make index-status` / `make index-gate-tests` 在干净检出上失败"的判断，依据是 `Makefile:99/102` 的调用关系；**未实际在干净检出上执行**（会改变工作树）。
6. **未纳入**：`docs/review/**` 内部 R2/R3/R4 的**逐文件差异**未比对（仅对体量最大的 `consumer-scan-hits.jsonl` 做了 `cmp`，结果为字节相同）。R2/R3/R4 之间是否存在其它增量差异未判定。
7. **跨仓未查**：`/home/szf/dev/Leibniz-KERT`、`/home/szf/dev/gits-kert-docs` 本次未纳入（本任务限定本仓）。

---

## 7. 建议动作汇总（本轮一律不执行）

| 优先级 | 动作 | 对象 | 归属 |
|---|---|---|---|
| 高 | 裁定 H-1：提交生成物 或 回退 `generated/` | `generated/product-knowledge/field-policy.schema.json`、`generated/manifest.json` | 合同 Owner（`knowledge_architecture_owner`） |
| 高 | PC-i1 独立 QA 限在干净检出复跑 e2e/门禁 | 全仓 | PC-i1 编排 |
| 中 | 裁定 `scripts/ua_index_gate*.py` 入仓 | 2 个脚本 | Owner |
| 中 | 裁定 44 个 `scripts/onto1_*.py` 入仓 | ONTO1 Loop | ONTO1 编排 |
| 中 | 裁定 `frontend/DESIGN.md` 归属 | 1 文件 | Owner |
| 低 | 显式提交或恢复 `diagrams/architecture.{html,png}` 删除 | 2 项删除 | Owner |
| 低 | 评估 `frontend/dist/` 移出跟踪（4 个受跟踪文件） | 1 类 | Owner |
| 低 | 评估 `diagrams/**/*.visual-check.*` 是否加忽略 | 渲染中间产物 | Owner |

**再次声明：本次甄别全程只读；未做任何清理、提交、删除、移动、改名或编辑既有文件；唯一写入为 `evidence/pc-i1-closure/**`（本报告 + 2 份原始 `git status` 落档）。**

---

# 8. H-1 更正与复核（2026-09-23 追加 · 应 TL 复核要求）

> 纪律不变：只读；未执行 `git add/commit/rm/clean/mv`，未实跑 `make generate/check/index-status`（会改写工作树），未触碰 `loops/PC-i1-chapter-inheritance/**` 与 `frontend/src/**`；唯一写入仍为 `evidence/pc-i1-closure/**`。

## 8.1 接受的更正：H-1 成因（原表述作废）

**原表述（作废）**：*"本地曾执行 `make generate`（`Makefile:20 → scripts/generate-contracts.sh`）… 成果未提交"* —— 含"疑似旁人/手工"暗示。

**更正表述（接受 TL 复核）**：该漂移是 **PC-i1 自身门禁第 1 项 `contract_generate`（命令 `make generate`）的确定性产物**，非手工、非旁人所为。三重时间证据互相吻合：

| 证据 | 值 |
|---|---|
| `loops/PC-i1-chapter-inheritance/EVIDENCE.json` → `gates.contract_generate.command` | `make generate` |
| 同上 `executed_at` | `2026-09-22T14:58:10.901521+00:00` = **北京时间 22:58:10** |
| `generated/manifest.json` mtime | **22:58:11** |
| `generated/product-knowledge/field-policy.schema.json` mtime | **22:58:11** |
| `loops/PC-i1-.../evidence/security_check-20260922T145811Z.log` mtime | **22:58:12** |
| `loops/PC-i1-.../evidence/frontend_unit-20260922T145816Z.log` mtime | **22:58:21** |

⇒ 门禁表首项 `contract_generate` 执行（22:58:10）→ 生成物落盘（22:58:11）→ 后续门禁取证（22:58:12 / 22:58:21），**因果与时序一致**。

## 8.2 ① 复核结论：`make check` **确实（间接）读 `generated/`，且会因漂移 FAIL**

**TL 的更正 #4 不成立** —— `grep run_gates.py` 只覆盖**字面文本**，而门禁通过脚本**间接**读 `generated/`。完整证据链（file:line）：

1. `scripts/run_gates.py:46` —— GATES 第 5 项：
   ```python
   ("contract-check",          ["bash", "scripts/check-contracts.sh"], "integrity"),
   ```
2. `scripts/check-contracts.sh:4`：
   ```bash
   python3 "${ROOT}/scripts/contract_pipeline.py" check
   ```
3. `scripts/contract_pipeline.py:25` → `GENERATED = ROOT / "generated"`
   `:323-336` → `check()`：
   ```python
   def check() -> None:
       if not GENERATED.is_dir():
           raise ValueError("generated directory missing; run make generate")
       ...
           compile_all(expected)                       # 由 specs/ 现场重新编译
           expected_files = {...digest...}
           actual_files   = {...GENERATED...}          # 磁盘上的 generated/
           if expected_files != actual_files:
               raise ValueError(f"generated drift detected: missing={missing}, extra={extra}, changed={changed}")
   ```
   `:350-352` → 失败以 **exit=2** 返回。
4. `run_gates.py:209-210, 243-247`：`contract-check` 类别 = `integrity` ⇒ 计入 `integrity_failed` ⇒ **`make check` 非零退出**。

**另有两个门禁也读 `generated/`**（与本次漂移文件无交集，但证明"门禁读 generated/"是既定事实）：

- `semantic-rule-gate`（`run_gates.py:59`）→ `scripts/semantic_rule_gate.py:17-19`：
  ```python
  SHACL_TTL  = ROOT / "generated" / "semantic" / "gits-core.shacl.ttl"
  SCHEMA_JSON= ROOT / "generated" / "semantic" / "gits-core.schema.json"
  DMN_XML    = ROOT / "generated" / "rules" / "claim-reconciliation.normalized.dmn"
  ```
- `gate-injection-tests`（`run_gates.py:45`）→ `scripts/gate_injection_tests.py:72`（`"generated/semantic/*.json"`）、`:499-506`（"受保护制品 … 被写坏"注入）。

**"HEAD 上确实存在漂移"的硬证据**（只读命令）：

```bash
git show HEAD:generated/product-knowledge/field-policy.schema.json | grep -c '"_case"'   # → 2
grep -c '"_case"' generated/product-knowledge/field-policy.schema.json                    # → 7  (工作树)
git show HEAD:generated/product-knowledge/field-policy.schema.json | wc -l                # → 296
wc -l < generated/product-knowledge/field-policy.schema.json                              # → 691
```

⇒ **诚实结论**：干净检出（HEAD `652a23f`）上执行 `make check`，会在 `contract-check` 处报
`generated drift detected: … changed=['product-knowledge/field-policy.schema.json', 'manifest.json']`。
因此原报告"影响：干净检出上完整性门禁可能失败"应**从"推测"升级为"已证实"**，并把"可能"改为"会"。

**附带发现（合同管线纪律缺口）**：`git show --stat bcf124e` 显示该提交**只改了 `specs/product-knowledge/field-policy.schema.json`（+180）与 loop 文档，未同步 `generated/**`** ⇒ HEAD 上"源领先生成物"；而 `2ceb66d` 提交的生成物为 296 行（= HEAD 版本）。即：**源变更提交时未随附其生成物**，属规则（合同源变更 → `make generate` → 提交生成物）的执行缺口，而非"谁手工动了 generated"。

## 8.3 ② 复核结论：漂移对 PC-i1 六门禁证据可复现性的影响

| PC-i1 门禁 | 命令 | 是否读 `generated/` | 可复现性结论 |
|---|---|---|---|
| `contract_generate` | `make generate` | **是（且为漂移源头，写 `generated/`）** | 可复现（每次执行都会产出同一 691 行结果） |
| `contract_check` | `make check` | **是**（见 §8.2） | **状态相关**：在当前工作树（已重生成）**可复现 PASS**；在 **HEAD 干净检出不可复现（会 FAIL）** |
| `security_check` | `make security-check` | **否（结论不受影响）** | 可复现 |
| `frontend_typecheck` | `npm --prefix frontend run check` | 否 | 可复现 |
| `frontend_unit` | `cd frontend && npx vitest run` | 否 | 可复现 |
| `e2e_parity` | `playwright test e2e/product-center-pc1.spec.ts` | 否 | 可复现 |

`security_check` 不受影响的证据：

- `grep -c 'generated'`：`scripts/secret_scan.py` = **0**、`scripts/sensitive_permissions.py` = **0**、`tools/quarantine/oracle/readonly_guard.py` = **0**。
- `scripts/sensitive_permissions.py:12`：`SENSITIVE = ("source_private", "reports/private", "artifacts/private", "oracle_source", "oracle_snapshots")` —— 白名单**不含 `generated/`**。
- `tools/quarantine/oracle/readonly_guard.py`：无 `rglob` / `generated` 命中（自检限于 quarantine）。
- 细微补充（**不改变结论**）：`scripts/secret_scan.py:57` 用 `root.rglob("*")` 全仓扫描，`SKIP_PARTS`（`:13` = `.git/node_modules/target/dist/backups/__pycache__/.venv/venv`）**不含 `generated`** ⇒ 它**确实会读到 `generated/` 内文件内容**做凭据模式扫描；但该门禁判定与"源-生成物一致性"无关，新增内容为合同正例用例，故漂移**不改变其 PASS 结论**。

## 8.4 ③ 复核结论：`make verify` / `make index-status` 在干净检出上的失败形态（基于调用关系推理，未实跑）

**调用关系（file:line）**

- `Makefile:94`：`verify: bootstrap-check generate check framework-test tooling-test backend-test frontend-test db-check semantic-rule-gate criteria-key-audit criteria-line-audit index-gate-tests`
- `Makefile:99-100`：`index-status:` → `@$(PYTHON) scripts/ua_index_gate.py $(if $(STRICT),--require,)`
- `Makefile:102-103`：`index-gate-tests:` → `@$(PYTHON) scripts/ua_index_gate_tests.py`
- `Makefile:7`：`PYTHON ?= $(if $(VENV_PY),$(VENV_PY),python3)`
- 入仓状态：
  ```
  $ git ls-files --error-unmatch scripts/ua_index_gate.py
  error: 路径规格 'scripts/ua_index_gate.py' 未匹配任何 git 已知文件
  $ git status --porcelain -- scripts/ua_index_gate.py scripts/ua_index_gate_tests.py
  ?? scripts/ua_index_gate.py
  ?? scripts/ua_index_gate_tests.py
  ```

**干净检出上的具体失败形态（可预期）**

```text
$ make index-status
python3: can't open file '<ROOT>/scripts/ua_index_gate.py': [Errno 2] No such file or directory
make: *** [Makefile:100: index-status] Error 2

$ make verify
（前置目标 bootstrap-check / generate / check / framework-test / tooling-test /
 backend-test / frontend-test / db-check / semantic-rule-gate / criteria-*-audit 依次执行）
python3: can't open file '<ROOT>/scripts/ua_index_gate_tests.py': [Errno 2] No such file or directory
make: *** [Makefile:103: index-gate-tests] Error 2
make: *** [Makefile:94: verify] Error 2
```

**性质判定**：这不是"门禁判 FAIL"，而是**工具缺失 ⇒ 该门禁未产生结论**（等同 `run_gates.py` 的四态之 `BLOCKED`，见 `run_gates.py:117-129, 146-148`）。但 **Make 层无法区分**，"can't open file … Error 2"会被读者误读为"索引红线门禁失败"。更严重的是：`index-status` 是 `code-fact-index` 规则（GOV-CFI-001）明文要求的**红线门禁**，脚本未入仓 ⇒ 干净检出上该红线**恒不可执行**（既永不可能 PASS，也不表达真实结论）。

**建议动作（三选一，待 Owner 决定；本轮不执行）**

- **(a) 优先**：将 `scripts/ua_index_gate.py` + `scripts/ua_index_gate_tests.py` 入仓 —— 它们是已颁布规则（`AGENTS.md` 索引门禁、GOV-CFI-001、`Makefile` 目标）的**可执行底座**，不入仓则规则空转。
- **(b)** 暂缓：从 `Makefile` 移除 `index-status` / `index-gate-tests` 目标及 `verify` 依赖中的引用，并同步修订规则文本（避免"有目标、无脚本"）。
- **(c)** 保持现状，但在**干净检出交付规程**中显式声明：无未提交文件时这两个目标不可用。

## 8.5 ④ 复核结论：PC-i1 六门禁**不依赖**未入仓脚本 —— 无反例

逐一核对（`git ls-files --error-unmatch`）：

| 依赖项 | 入仓状态 |
|---|---|
| `scripts/run_gates.py` | TRACKED |
| `scripts/check-contracts.sh` | TRACKED |
| GATES 全部 24 个脚本（`gate_selftest.py`、`gate_injection_tests.py`、`semantic_rule_gate.py`、`loop_guard.py`、`secret_scan.py`、`enum_consistency_check.py`、`gk_ke_*` ×10、`generate_gk_ke_dataset_v2.py`、`contract_pipeline.py` 等） | **全部 TRACKED** |
| `scripts/generate-contracts.sh` → `scripts/contract_pipeline.py` | TRACKED |
| `scripts/sensitive_permissions.py`、`tools/quarantine/oracle/readonly_guard.py` | TRACKED |
| `frontend/package.json`、`frontend/e2e/product-center-pc1.spec.ts` | TRACKED |
| `scripts/ua_index_gate.py` / `ua_index_gate_tests.py` | **UNTRACKED（未入仓）** |

⇒ **PC-i1 六门禁（contract_generate / contract_check / security_check / frontend_typecheck / frontend_unit / e2e_parity）均不依赖 `scripts/ua_index_gate*.py` 或 `scripts/onto1_*.py`；TL 的判断成立，未发现反例。**

**但须区分两类不同依赖**（避免把 §8.5 读成"contract_check 无外部依赖"）：

- 依赖 1（脚本入仓）：六门禁**全部满足** ✔
- 依赖 2（工作树状态）：`contract_check` **不满足** —— 其可复现性依赖工作树中存在**未提交**的 `generated/` 再生成物（§8.2 / §8.3）

## 8.6 H-1 修订后结论（对照表）

| 维度 | 修订前（原文） | 修订后 |
|---|---|---|
| **成因** | "本地疑似执行过 `make generate` 未提交"（含旁人/手工暗示） | **PC-i1 门禁首项 `contract_generate`（`make generate`）的确定性产物**（mtime × 2 与 `EVIDENCE.json.executed_at` 三重吻合） |
| **影响** | "干净检出上完整性门禁**可能**失败"（推测） | **已证实**：`make check` 的 `contract-check` 门禁**会**报 `generated drift detected`（`contract_pipeline.py:323-336`） |
| **影响范围** | 未界定 | 仅 `contract-check`（`contract_generate` 为源头）；`semantic-rule-gate` / `gate-injection-tests` 亦读 `generated/` 但与本次漂移文件**无交集**；`security_check` 与 3 项前端门禁**不受影响** |
| **HEAD 漂移存在性** | 仅由提交先后推断 | **硬证据**：HEAD 版 `"_case"` = 2 / 296 行；工作树 = 7 / 691 行 |
| **纪律缺口** | 未提及 | `bcf124e` 只提交了 `specs/` 源（+180），**未同步提交 `generated/**`** ⇒ HEAD 上"源领先生成物" |
| **建议动作** | 提交生成物 或 `git restore generated/` | **建议提交生成物**（`make generate` 的确定性产物，提交后 HEAD 自洽）——须 Owner / 合同 Owner（`knowledge_architecture_owner`）裁定；**本轮只读，不执行** |

## 8.7 未覆盖（本轮新增）

1. 未实跑 `make check` / `make index-status` / `make verify`（会改写 `generated/` 或与只读纪律冲突）⇒ §8.2 的判定为**代码级推导（`contract_pipeline.py:check()` 逻辑）**，§8.4 为**Make 调用关系推导**，均**未经执行验证**；建议由具备写权限的角色在**临时克隆**上取证复现。
2. 未逐文件比对 `specs@HEAD` 与 `generated@HEAD` 的**全部**合同（仅 `CTR-PK-FLD-001` 一项已证实漂移）；是否存在其它"源领先"的合同未判定。
3. 未检查 `.gitignore` 是否覆盖 `scripts/__pycache__/`（`grep -rn generated` 命中多个 `scripts/__pycache__/*.pyc`，属编译缓存；本报告未列为分类项，见下条）
4. **补充项（已复核闭合）**：`grep` 命中的 `scripts/__pycache__/*.pyc`（含 `contract_diff.cpython-31{1,2,4}.pyc` 多版本）属编译缓存。已复核：`git check-ignore -v scripts/__pycache__/contract_diff.cpython-312.pyc` → `.gitignore:15:**/__pycache__/`（另有 `:14 __pycache__/`）；`git status --porcelain -uall | grep -c '__pycache__'` = **0** ⇒ **已被忽略、无未跟踪条目，不构成 B 类风险**，§2-B 无需修订。
