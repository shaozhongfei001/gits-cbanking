# 代码事实索引与检索底座（SDD 交付流程约束 · TL/架构角色）

```text
DOC_ID     = GOV-CFI-001
STATUS     = ACTIVE（技术负责人发布的工程流程约束；非 Owner 业务决策）
AUTHOR     = tech_lead
CREATED_AT = 2026-09-15
SCOPE      = TL / 架构角色在 SDD 交付流程中的"全局设计理解"与"代码事实检索"活动
AUTHORITY  = 本流程本身是强制约束；它管理的索引产物是 DERIVED 派生视图（非权威）
RELATED    = docs/architecture/UNDERSTAND_ANYTHING_CODE_LEVEL_ASSESSMENT.md（引入评估 + Owner 裁决 附五/附六）
             .codebuddy/rules/code-fact-index/RULE.mdc（角色可执行约束）
             scripts/ua_index_gate.py（红线门禁）
             scripts/ua_index_gate_tests.py（门禁变异复验）
             docs/architecture/candidates/UA-人读模块地图-V1.0.md（人读派生视图）
             .understandignore（采集边界）
INDEX_AT   = .ua/knowledge-graph.json（合并图 5106 节点 / 4235 边 / 54 层 / 26 导览；gits @7116904 + KERT @64f6f87，刷新于 2026-09-16）
LAST_REFRESH = 2026-09-16（增量：批次级语义缓存复用，两仓合计 37 次 LLM 调用 / 0.27M prompt tokens；见 §6.1）
```

---

## 0. 一句话

**把 Understand-Anything 的产物从"一次性分析报告"变成 TL/架构角色开工的默认检索底座：先查索引定位，再按需回源验证；索引永不升格为权威事实。**

---

## 1. 要解决的两个问题（本流程的唯一目的）

| # | 痛点（原始表述） | 本流程给出的机制 |
|---|---|---|
| P1 | 加速对全局设计的理解，避免"以往"那种从零重建全局视图的方式 | §4 检索协议：**L0 模块级 → L1 归属 → L2 依赖 → L3 摘要 → L4 回源**，把"通读源码建立全局视图"降级为例外手段 |
| P2 | 减少反复阅读源代码重新理解代码 | §4 C1 检索优先 + §6 新鲜度/刷新 SOP：**同一问题第二次出现时，答案应来自索引或已回源结论，而不是第三次通读源码** |

### 本流程明确不解决的问题（防过度承诺）

- 它**不**让索引变得权威，**不**免除回源验证（C2）。
- 它**不**解决索引自身的已知盲区（前端 `.vue` 结构未抽取、无函数级调用边、两仓 0 跨仓边、`specs/` 未做字段级解析）。盲区范围内**必须**回源。
- 它**不**替代 `specs/` 合同 SSOT，也不产出任何 Gate / 证据结论。

---

## 2. 定位与权威边界（五条硬约束）

### 三级台阶（不得跨越）

```text
第 3 级  specs/ 合同与基线      ← 唯一权威 SSOT（权威顺序第 1–3 级）
第 2 级  实现代码               ← 实现事实（权威顺序第 4 级）
第 1 级  .ua/ 代码事实索引      ← DERIVED 检索层：给线索，不给事实
```

索引位于**实现代码之下**，只用于"更快地找到第 2 级"，不具备任何结论效力。

### 约束条款

| 编号 | 约束 | 判定方式 |
|---|---|---|
| **C1** | **检索优先**：TL/架构角色遇到"X 在哪实现 / 谁依赖谁 / 这个模块负责什么"这类定位问题，**第一步必须查索引**；`rg` 全仓通读源码只能作为索引未覆盖时的兜底，且须在交付物中说明"索引未覆盖" | 交付物须有 `索引依据` 段（§5） |
| **C2** | **回源强制**：凡进入 ADR / LOOP scope / dispatch / 设计结论 / 影响面判定的**事实陈述**，必须回源到 `文件:行` 验证。索引只提供候选范围，回源结论才可引用 | 交付物须给出 `文件:行` |
| **C3** | **权威不升格**：索引产物**不入 git**（`.ua/` 保持 gitignore）、**不进** `evidence/`、**不进** Gate 判定、**不作为** ADR 依据；与 `specs/` 冲突时以 `specs/` 为准 | `make index-status` 的红线 R1/R3 |
| **C4** | **出域与采集边界**：`.understandignore` 的凭据/二进制排除段（§B）与自我递归段（§C）为硬排除，**任何放开必须在评估文档留下显式裁决记录**（已有 UA-D9 / UA-D10 放开 §A 的先例，§B 未放开） | `make index-status` 的红线 R2 |
| **C5** | **新鲜度声明**：TL 开工/收工必须声明索引相对 HEAD 的状态：`INDEX_FRESH` / `INDEX_STALE(<n>)` / `INDEX_ABSENT`。不得在未声明的情况下声称"已掌握全局设计" | 收工声明 + `make index-status` 的 F1 |

---

## 3. 产物清单（索引底座由什么构成）

| 产物 | 位置 | 内容 | 入库 |
|---|---|---|---|
| 合并图 | `.ua/knowledge-graph.json` | 两仓合并：4947 节点 / 4090 边 / 54 层 / 25 导览；含 `humanView`（层名=业务模块名，`derived/notAuthoritative=true`） | ❌ gitignore |
| 单仓图 | `.ua/backup/gits-cbanking-*-knowledge-graph.json`、`.ua/Leibniz-KERT-knowledge-graph.json` | 分仓视图，排障用 | ❌ |
| 新鲜度元数据 | `.ua/merge-meta.json`（`gitsCommit`/`kertCommit`）、`.ua/meta.json`（`gitCommitHash`/`analyzedFiles`） | 门禁 F1 判据来源 | ❌ |
| 增量指纹 | `.ua/fingerprints.json` | 逐文件内容指纹，支持 UA 4 档增量 | ❌ |
| 采集边界 | `.understandignore` | gitignore 语法；§A 权威源（Owner 已裁决放开）、§B 凭据硬排除、§C 自我递归 | ✅ |
| 人读派生视图 | `docs/architecture/candidates/UA-人读模块地图-V1.0.md` | 模块级白话地图（人读），标注 `DERIVED / NOT_AUTHORITATIVE` | ✅ |

> 图形 Dashboard（只读、无 LLM、不出本机）：
> `node $HOME/.understand-anything-plugin/packages/viewer/bin/viewer.mjs <project-dir>`

---

## 4. 检索协议（五步阶梯，含实测命令）

> 全部命令在仓库根执行，已在当前索引实测通过。

### L0 · 模块级全局视图（回答"这个系统由哪几块组成"）

```bash
python3 -c "import json;g=json.load(open('.ua/knowledge-graph.json'));[print(l['name'],'|',len(l['nodeIds']),'|',l['description']) for l in g['layers']]"
python3 -c "import json;g=json.load(open('.ua/knowledge-graph.json'));[print(t['order'],t['title'],'->',len(t['nodeIds'])) for t in g['tour']]"
```

### L1 · 归属定位（回答"X 在哪实现"）

```bash
python3 -c "import json,sys;k=sys.argv[1];g=json.load(open('.ua/knowledge-graph.json'));[print(n['id'],'|',n.get('type'),'|',n.get('filePath')) for n in g['nodes'] if k.lower() in (n.get('name','')+' '+n.get('filePath','')).lower()]" ClaimReconciliationPort
```

### L2 · 依赖方向（回答"谁依赖谁"）

```bash
python3 -c "import json,sys;k=sys.argv[1];g=json.load(open('.ua/knowledge-graph.json'));[print(e['type'],e['source'],'->',e['target']) for e in g['edges'] if k in e['source'] or k in e['target']]" operational-ontology
```

> **边界（必须记住）**：边类型为 `imports` / `contains` / `exports`，**不是函数级调用图**。因此 L2 只能回答"文件/模块级依赖方向"，不能回答"谁调用了哪个方法"——后者必须回源（L4）。

### L3 · 逐文件摘要（回答"这个文件大概干什么"，仅作线索）

```bash
python3 -c "import json,sys;k=sys.argv[1];g=json.load(open('.ua/knowledge-graph.json'));[print(n['filePath'],'\n  ',n.get('summary','')) for n in g['nodes'] if n.get('filePath','')==k]" modules/operational-ontology/src/main/java/com/gien/gits/ontology/service/KycInsightService.java
```

> 摘要是 LLM 归纳（非确定性），**只可用于决定"该读哪个文件"，不可引用为事实**。

### L4 · 回源验证（唯一可引用结论的来源）

用语义检索定位符号，再读源码，产出 `文件:行`：

```text
lsp readSymbol / findReferences / incomingCalls  →  或  rg -n "<符号>" <file>
输出形态：modules/.../KycInsightService.java:88
```

### L5 · 落盘（回答"下次不重复读"）

回源结论必须写进**受控交付物**（Loop `memory/`、dispatch、ADR、设计文档），带 `文件:行` 与索引版本。**未落盘的结论 = 未检索**，下一个会话仍会重复通读源码（P2 未解决）。

---

## 5. 挂载到 SDD 交付流程各阶段

| 阶段 | 角色 | 本流程要求的动作 | 落到哪个文件 |
|---|---|---|---|
| **S1 Loop 规划** | TL | ① 跑 L0 建立模块视图；② 对 scope 内每个待改模块跑 L1/L2；③ 写"索引依据"（候选影响面 + 回源结论 + 未覆盖盲区） | `loops/<LOOP_ID>/memory/INDEX_BASIS.md`（模板已内置） |
| **S2 合同变更影响面** | TL | 改 `specs/` 前：用索引拿**候选实现文件集** → **逐个回源**确认是否真受影响 → 写进 dispatch。⚠ 索引对 `specs/` 只做文件级摘要，**合同字段细节必须回查权威源** | `docs/dispatch/<派工单>.md` 的"索引依据"段 |
| **S3 派工** | TL | 派工单必须包含：索引版本（`merge-meta` commit）、候选影响面、回源结论、已知盲区 | 同上 |
| **S4 实现** | Feature Pilot | 推荐（非强制）：定位类问题先查索引；结论同样须回源 | Loop `memory/` |
| **S5 收工** | TL | ① 声明 `INDEX_FRESH` / `INDEX_STALE(n)` / `INDEX_ABSENT`；② 超过阈值跑刷新 SOP；③ 把本批次新得到的回源结论追加到 `INDEX_BASIS.md` | `INDEX_BASIS.md` + `NEXT_SESSION.md` |
| **S6 QA / E2E** | 独立 QA | **禁止**以索引作为判据；QA 只看 `specs/`、源码、证据链（索引不得入场） | — |

### 标准动作模板（TL 开工）

```text
[开工] Loop: <ID>, 角色: tech_lead, Baton: <holder>, Gate: <current>
[索引] INDEX_FRESH @ merge 2026-09-15T06:37:38Z (gits a1e183bb)
[索引] 候选影响面: <模块/文件清单>  ← 来自 L0/L1/L2
[回源] <文件:行> 确认 <事实>
```

---

## 6. 新鲜度与刷新 SOP

### 阈值（`scripts/ua_index_gate.py` 默认值，可 `--max-drift`/`--max-age-days` 覆盖）

| 项 | 阈值 | 超出后的动作 |
|---|---|---|
| 提交漂移 | > 50 个提交 | 收工前刷新（advisory WARN；`--require` 下 FAIL） |
| 生成时长 | > 14 天 | 同上 |
| 结构性变更（`specs/`、`modules/`、`adapters/`、`apps/` 增删目录或大量文件） | 立即 | 无论漂移多少都必须刷新 |

### 刷新步骤

```text
1. 确认采集边界未被放开：git diff .understandignore（§B 凭据段必须仍生效）
2. 重跑 /understand（默认走 4 档增量：SKIP / PARTIAL / ARCHITECTURE / FULL）
3. 重建人读层与合并视图（层名=业务模块名、node.repo 字段、filePath 保持仓内相对路径）
4. 更新 .ua/merge-meta.json 与 .ua/meta.json 的 commit/时间戳
5. make index-status  → 必须 PASS（红线）+ 漂移归零
```

> ⚠ **步骤 3 的已知陷阱（2026-09-16 实测）**：`ua_humanize.py` 原地改写会在 `.ua/` 留下
> `knowledge-graph.prehumanize.bak.json`。官方 `merge-subdomain-graphs.py` 按
> `*knowledge-graph*.json` 非递归 glob 发现子域图，会把这个备份当作第三个"仓库"重复并入
> （实测 5106 → 9130 节点，且 `make index-status` 仍 PASS，**不会自动发现**）。
> 合并前必须删除该备份，或让 `ua_humanize.py` 输出到 `.ua/` 之外。
> 校验手段：合并后 `mergedNodes` 必须等于 `gitsNodes + kertNodes`。

### 6.1 本机可复现的刷新实现（2026-09-16 核实）

| 项 | 位置 | 说明 |
|---|---|---|
| 全量编排 | `/home/szf/ua-harness/ua_run.py` | Phase 0–7；`--from-phase N` 可只跑后半段 |
| 语义层 | `/home/szf/ua-harness/ua_semantic_pass.py` | 替代 UA 官方 `file-analyzer`（DeepSeek 云） |
| 层/导览 | `/home/szf/ua-harness/ua_arch_tour_pass.py` | 替代 `architecture-analyzer` / `tour-builder` |
| 人读层 | `/home/szf/ua-harness/ua_humanize.py` | 业务模块层；原结构层保留在 `layersStructural` |
| 两仓合并 | `/home/szf/ua-harness/ua_merge.py` | 仓名前缀隔离 + 官方合并 + `merge-meta.json` |
| 增量驱动 | `<repo>/.ua/tmp/ua_incr.py`（会话内生成，勿入库） | 复用上轮 `batch-*.json` 的逐文件语义，仅对新增/变更文件调 LLM |

增量口径（2026-09-16 实测）：gits 3318 文件仅 76 个需 LLM（16 次调用 / 0.13M tokens），
KERT 666 文件仅 76 个（21 次调用 / 0.14M tokens），对比全量 3.7M tokens 降幅约 93%。
判定依据 = `git diff --name-only <索引commit>..HEAD` ∪ 工作区差异 ∪ 未跟踪文件。

### 已知流程缺口（诚实登记，尚未解决）

| ID | 缺口 | 影响 | 状态 |
|---|---|---|---|
| CFI-OPEN-01 | 生成人读层与合并视图的侧车脚本（`ua_humanize.py` / `ua_merge.py` / `ua_run.py` / 增量驱动）**未入库**，仅存在于本机 `/home/szf/ua-harness/` | 本机可复现（见 §6.1），但不随仓库分发；换机/换人即退化为"由会话重建" | 部分缓解（仍未入库） |
| CFI-OPEN-02 | UA 官方未适配 CodeBuddy（无 hooks），无"提交后自动更新" | 依赖人工按 §6 触发 | OPEN（上游限制） |
| CFI-OPEN-03 | 前端 `.vue` 结构未抽取（约 101 个页面组件只有文本摘要） | 前端影响面分析**必须**回源，索引不可用 | OPEN（上游限制） |

---

## 7. 禁止清单（反模式，出现即退回）

1. ❌ 把 `.ua/knowledge-graph.json` 提交进 git，或把 `.ua/` 挂进任何构建/测试依赖。
2. ❌ 把索引摘要写进 `EVIDENCE.md` / `EVIDENCE.json` / Gate 记录 / ADR 结论。
3. ❌ 用索引回答"谁调用了这个方法""这个字段的校验规则是什么"——索引没有这两类信息。
4. ❌ 在 `--require` 门禁 FAIL（索引缺失/过期）时仍声称"已完成全局设计理解"。
5. ❌ 以"节省时间"为由放开 `.understandignore` §B 凭据段（须 Owner 裁决 + 留痕）。
6. ❌ 未经回源，把 L1/L2/L3 的输出直接写成 dispatch 或 ADR 中的事实陈述。

---

## 8. 可执行门禁

```bash
make index-status        # 红线 fail-closed + 新鲜度 advisory（日常/收工）
make index-status STRICT=1   # 严格模式：索引缺失或过期即失败（TL 收工声明前）
make index-gate-tests    # 变异复验：证明红线断言非空转
```

判定语义（`scripts/ua_index_gate.py`）：

| 编号 | 判定 | 类别 |
|---|---|---|
| R1 | `.ua/` 未被 git 跟踪且被忽略 | FAIL |
| R2 | `.understandignore` 凭据/二进制段与 `.ua/` 自我递归段处于生效态 | FAIL |
| R3 | 索引产物自带非权威标记（`humanView.notAuthoritative` 或 `project.description` 含 `DERIVED`） | FAIL |
| R4 | 索引 JSON 可解析且 `nodes`/`layers` 非空 | FAIL |
| R5 | 本流程文档与角色规则落盘且红线标记未被改写 | FAIL |
| F1 | 索引相对 HEAD 的漂移/年龄在阈值内 | WARN（`--require` 下 FAIL） |
| F1' | `--require`（`STRICT=1`）下索引**存在且新鲜度可判定** | FAIL（缺索引、无法判定漂移、超阈值均失败；对应 FAIL-2026-09-15-01 的修复） |

> **本门禁不声称**"索引被正确使用"——那是不可机器判定的。它只保证"索引没有变成权威、没有出域、没有假装新鲜"。

---

## 9. 角色与责任

| 角色 | 责任 | 禁止 |
|---|---|---|
| **Tech Lead / 架构** | 维持索引可用（§6 刷新）；开工/收工声明新鲜度；交付物带"索引依据 + 回源结论"；索引版本记录到 Loop `memory/INDEX_BASIS.md` | 禁止把索引输出直接当事实；禁止跳过回源 |
| **Feature Pilot** | 推荐使用索引定位；其回源结论追加到同 Loop `INDEX_BASIS.md` | 禁止修改索引产物或采集边界 |
| **独立 QA / E2E Owner** | 不使用索引作为判据；可核验"交付物是否含回源结论" | 禁止以索引作为 PASS 依据 |

---

## 10. 变更控制

- 本流程的**流程性调整**（阈值、命令、挂载点）由 TL 修订本文档并同步 `.codebuddy/rules/code-fact-index/RULE.mdc`，修订后必须 `make index-status && make index-gate-tests` 通过。
- 任何**改变索引权威地位**的提案（例：把索引纳入 Gate 判定、把 `.ua/` 入库、把索引摘要写入 ADR）属**扩大范围**，必须：Owner 裁决 + 新增 ADR + 专用 Loop。理由：那会直接违反 `AGENTS.md` 权威顺序与 `.understandignore` 的 DERIVED 声明。
- 放开 `.understandignore` §B（凭据/二进制）**不属流程调整**，必须走 Owner 裁决。

---

## 11. 边界与非声明

- 本文是**流程约束**，不是"索引已可信"的证明；索引始终是 DERIVED。
- 本文**不构成** `QA_PASS`、不代表 `PRODUCTION_READY`、不作为 Gate/ADR 依据。
- 索引的已知盲区（§4 L2 边界、§6 CFI-OPEN-01/02/03）在本轮**未修复**，不声称已修复。
- 本流程不修改 `specs/`、`generated/`、`CONTRACT_INDEX.yaml`、任何已关闭 Loop 的状态。
