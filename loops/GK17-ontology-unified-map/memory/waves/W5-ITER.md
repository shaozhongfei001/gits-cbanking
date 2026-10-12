# W5｜ITER 记录

## ITER 1｜WP5.1 / WP5.2 / WP5.3-前置（2026-09-15）

### 并发执行

| 写者 | WP | 独占文件 | 纪律 |
|---|---|---|---|
| `w5-ref-anchor` | WP5.1 | `scripts/gk17_ref_anchor_check.py` | 禁跑 make/run_gates/mvn、禁 commit（已遵守：`git status` 仅 `??`，无 M/A） |
| `w5-triple-consistency` | WP5.2 | `scripts/gk17_triple_consistency_check.py` | 同上 |
| `tech_lead` | 门禁执行 + 验证 | — | **串行**执行，不采信作者自述 |

### WP5.1 `ref_anchor_check` = **PASS** ✅

覆盖 **7 个 ID 空间**、4 张地图。锚点一律**复用既有权威**（未另造第二套定义）：

| ID 空间 | 锚点来源（权威） | 数量 |
|---|---|---|
| `KM-*` | `maps/**/*.md` 的 `mapId` | 4 |
| `KD-*` | 资产 manifest 的 `domain` ∪ 各图 `domains[].domainId` | 3 |
| `ASSET-*` | `assets/**/*.md` front matter 的 `assetId` | **21** |
| `SP-*` | `skills/*.json` 的 `skillId` | 5 |
| `AC-*` | `activations/*.json` 的 `contractId` | 3 |
| `RP-*` | `routes/*.json` 的 `policyId` | 1 |
| TaskType | 本体 `gits:TaskType` ∪ activations/routes 的 `taskType` | 5 |

**变异自证（6/6 全部被捕获）**：`fake_assetRef` / `fake_skillRef` / `fake_activationContractRef` /
`fake_taskRef` / `fake_domainRef` / `fake_mapRef` —— 每个都 `BEFORE → 注入 → FAIL（附 ID 空间+字段+原因）→ 恢复 → PASS`，
且**被测 4 个原文件 sha256 全部 SAME**（自证未污染权威源），临时目录已清理。
另有端到端 fail-closed 验证（独立 `--root` 副本注入 2 个假引用 ⇒ exit 2，逐条打印）。

**诚实缺口（不计入 PASS 断言）**：`KD-*` 无独立锚点来源 ——
`selfDeclaredOnly=['KD-CORP-RM-PREVISIT','KD-CORP-RM-RECON']`（只有父图自声明），
`soundness=NOT_COUNTED_AS_PASS_ASSERTION`。

**TL 裁决**：批准"诚实清单"口径，**不改成硬 FAIL** ——
理由与本仓教条一致（`INCONCLUSIVE ≠ 通过`）。KD-* 的问题是**无权威源可校验**，不是**引用错**；
改硬 FAIL 会让门禁**永久红**，永久红的门禁会被当噪音忽略，那才是真的失去防线。

### WP5.2 `triple_consistency_check` = **FAIL**（门禁自曝空转）

见 `FAILURES.md` 的 `GATE_NOOP` 条目。**作者自曝**并判 FAIL，**未**以"不一致项 0"报绿。
D3（mapRef 文件不存在）/D4（悬空引用）已 OK；原本体 sha256 逐字节复原。
已按单写者规则交回作者修复（第 1/5 次）。

### TL 独立复核（**不采信自述**）：作者报的 6 项既有缺口，逐条实测

| # | 发现 | 实测结论 | 处置 |
|---|---|---|---|
| 1 | 既有 `validate_knowledge_architecture.py` 不校验 `domainId`/`mapRef`/`entrypoints.tasks` | **真**（正是 WP5.1 补上的三项：`mapRef=3`、`taskType=10`、`domain=3`） | 记档 |
| 2 | `KM-*` 无独立 registry（`MapVersion.json` 只有 `SIM-MAP-FINANCE`） | **真** | 记档 |
| 3 | `KD-*` 无独立锚点来源 | **真** | 按"诚实清单"保留 |
| 4 | **KD 命名空间混淆**：`elements/knowledge-items-index.json` 用 `KD-01/KD-02/KD-08` | **真**（实测取值集合） | 记档为**后续对齐陷阱**（按 KD- 前缀全局 grep 会撞上） |
| 5 | `registry/AssetVersion.json` 只含 4 条 `SIM-ASSET-*`；而**本体 `gits:Asset` 注释声称资产登记于该文件** | **真** | ⚠️ **已修**（见下） |
| 6 | `Capability.json` 的 `probeStatusEnum` 有枚举外值 `SUPERSEDED` | **真** | 记档待裁定（扩枚举 vs 改值属合同变更，不由本 Loop 单方改） |

### ⚠️ 本 ITER 修掉的一处**合同错误指引**（发现 #5，价值最高）

WP5.1 的作者报告直接暴露了**本体注释指错登记处**：

```
修正前： gits:Asset ... "ID 空间 ASSET-*；登记于 specs/knowledge-architecture/registry/AssetVersion.json。"
实测：   registry/AssetVersion.json 只有 SIM-ASSET-P001 / SIM-ASSET-METRIC / SIM-ASSET-RESTRICTED / SIM-ASSET-CAS-CONFLICT
真实锚点：specs/knowledge-architecture/assets/**/*.md 的 front matter assetId（21 个）
```

⇒ 任何按本体注释去 registry 找资产锚点的人都会**全量假 FAIL**。已修正为指向 `assets/` manifest，
并显式注明 registry 只含夹具。修后 `make generate` PASS、`make check` exit 0 / **22-23**。
（对照：`gits:Skill` 的注释"登记于 `specs/knowledge-architecture/skills/`"是**对的**，未动。）

### 门禁总表（**9 pass / 2 fail**）

| pass | `contract_generate` · `contract_check`(22-23) · `gk_ke_gates` · `ontology_load` · `security_check` · `backend_test` · **`ref_anchor_check`** · **`gk17_prodcard_projection`** · （`contract_generate`/`contract_check`/`ref_anchor_check` 已因合同变更**重落证**） |
|---|---|
| **fail** | `frontend_test`（环境限制）· **`triple_consistency_check`**（门禁空转，待作者修） |

### 关于"挂进 `run_gates.py`"

**本轮不做，留到 W8**。理由：`run_gates.py` 是 `make check` 的组成部分、被多个 Loop 共用，
改动会外溢到其他 actor 的验证面。本 Loop 门禁先以 `record_gate.py` 独立落证；
是否并入 `make check` 属**收口期决策**，W8 时连同说明提交。

### 非声明

- WP5.1 的 PASS **不等于**"所有 ID 空间都有权威锚点"—— `KD-*` 的缺口已如实标注且**未计入通过**；
- WP5.2 **尚未通过**，不得以"不一致项 0"计入任何通过口径；
- 本 ITER **未**把任何既有红灯转绿：`frontend_test` 仍 fail、`semantic-consumption` 仍 READINESS NOT MET。

---

## ITER 2｜WP5.2 空转根治（2026-09-15）

### 事件经过（**必须自曝**）

作者 `w5-triple-consistency` **已停止**（文件 mtime 停在 `09:33:05`，逾 2 小时无活动，未接修复指令）
⇒ 按单写者失效处置，**所有权回归 TL**。

1. **第 1 次修复（D1）**：定位到 `_parse_chunk` 以「第一个 `;` **或 `.`**」为界取主语 ——
   单谓词三元组 `S P O .` 无 `;` ⇒ `.` 成边界 ⇒ 谓词与宾语被吞进主语、pairs 为空、
   语句在 `if st.pairs:` 处被**静默丢弃**。修后变异被捕获（0→1）。
   **附带修复**：`gits-core.owl.ttl:12` 的 `gits:OperatingCase a owl:Class .` 是真语句，
   旧解析器把它丢了 ⇒ 该类的声明从未进入本体类集合。
2. **然后我差点接受这个门禁** —— 直到我读了输出里**一直在打印但我第一遍没读**的一行：

```
ontology stats  : 0 classes / 0 object properties / 0 datatype properties   ← 实际 32/34/1
projection      : 1 个 RDF 文件 / 0 个个体                                  ← 实际 13
```

   ⇒ **门禁两边都读了个空，D1–D4 全部空转**，它 PASS 是因为它**什么都没解析**。

### 自我批评（升格为本 Loop 纪律）

> **门禁 PASS 前必须核对输入基数。只跑变异负例不够** ——
> 变异只证明"我改的那一处"能触发；输入基数才证明"其余各处"有物可查。
> 这次我**第一遍没读那一行数字**，正是本仓已有前例（"6 个 Loop 首报全绿实为空转"）的同一形态。

### 根治：六处缺陷（详见 `FAILURES.md` 的 `GATE_VACUOUS` 条目）

| # | 缺陷 | 性质 |
|---|---|---|
| 1 | 主语边界含 `.` ⇒ `S P O .` 被丢弃 | 静默丢语句 |
| 2 | `a <T>` 留在主语里 ⇒ 四个取数函数 + D2 全匹配不到 `p=="type"` | 全局空转的**主因** |
| 3 | `classes()` 语义错 + **未定义自由变量 `t`**（因内层循环从不执行而从未被求值，错误被长期掩盖） | 空集 |
| 4 | `strip_comments` 把 `<...rdf-syntax-ns#>` 的 `#` 当注释 ⇒ 产生 `subject='@prefix'` 垃圾语句并**吞掉后续真实语句** | 解析污染 |
| 5 | `individuals` 要求"谓词/宾语属于本文件声明的资源"，而投影文件不声明类 | 恒为空 |
| 6 | **D4 逻辑自证**：把投影每个宾语都计入"已知个体集" ⇒ 任何引用自动"存在" ⇒ **构造上不可能触发** | 同义反复 |

### 重跑结果（**原命令未改**）

```
ontology stats  : 32 classes / 34 object properties / 1 datatype properties
projection      : 1 个 RDF 文件 / 13 个个体
  [D1] OK  [D2] OK  [D3] OK  [D4] OK
不一致项合计：0
gk17-triple-consistency-check: PASS (不一致项 0；变异已捕获，断言非空转)
EXIT=0
```

**输入基数与 TL 在 W1/W3.1 的独立实测值逐项相等**（32/34/1；13）⇒ 不再是空转。

### 非空转证明（四个各自自证）

| 检测 | 变异 | 结果 |
|---|---|---|
| D1 | 追加关系实例三元组到本体副本 | **捕获**（0→1，附行号 367） |
| D2 | 把 `a owl:Class` 改成 `a owl:Klass` | **真检出 13 项** |
| 基数断言（新增） | 同上 | **FAIL**：`本体有语句但解析出 0 个类 ⇒ 解析器失效` |
| D4 | 注入 `gits:gk17_no_such_individual` | **真检出 1 项** |
| 不回归 | `git show HEAD` 取旧版对比 | 新增 2 条 / **丢失 0 条** |

### 残留（如实登记）

1. **D2/D4 探针未内置到 `--selftest`**（当前只覆盖 D1）⇒ **W5 收口前必办**；
2. **D4 有能无力**：`products.ttl` 现为 **0 条对象引用**（因产品卡引用空间缺陷，40 处引用 100% 悬空未入 A-Box）
   ⇒ D4 能力已由变异证明，但**当前数据触发不到**；**与 Owner 待签第 1 项直接相关**。
3. **教训已升格为纪律**：门禁 PASS 前核对**输入基数**。

### 门禁总表：**9 pass / 1 fail**

| pass | `contract_generate` · `contract_check` · `gk_ke_gates` · `ontology_load` · `security_check` · `backend_test` · `ref_anchor_check` · `gk17_prodcard_projection` · **`triple_consistency_check`** |
|---|---|
| **fail** | `frontend_test`（环境 safe-delete 守卫阻断 `npm ci`，非产品缺陷） |

---

## ITER 3｜WP5.3 变异回归（**复用唯一机制，未新造**，2026-09-15）

### 先做的纪律性检查（约束①）

派工表原写"新建 `scripts/gk17_mutation_regression.py`"。但动手前我先查了仓内是否**已有**变异机制 ——
结果发现 `scripts/gate_injection_tests.py`（611 行）**就是**它，其自述：

> 「门禁注入测试：**对每个门禁注入一个真实缺陷，要求它失败**。
>   ……实测 **18 个门禁 0 个**有可复现的负例测试。
>   一个从不失败的检查器，与没有检查器等价，但更危险 —— 它提供虚假的安心。」

⇒ **不得新造第二套**（那本身就是"两份可独立修改的定义"，违反约束①）。
**改为把 GK17 两道门禁接入这一套机制。**

### 接入方式（**最小侵入、零外溢**）

| 改动 | 内容 |
|---|---|
| `LOOP_GATE_CMDS` | 新增命令回退表（GK17 门禁未登记进 `run_gates.py`） |
| `_gate_cmd()` | 加回退分支（**未**改动既有查表逻辑） |
| `INJECTIONS` | +2 条：`gk17-ref-anchor`、`gk17-triple-consistency` |
| `PRECISE` + `_assert_precise_identity()` | +2 个**精确注入器**（对 `.md` 追加文本改不到 front matter JSON，属"测试无效"，已按 FAIL-49 教训处理） |

**为何不登记进 `run_gates.py`**：那会改动 `make check` 的门禁**数量与结果**，
而 `LOOP.yaml` 里 `contract_check` 的通过条件**写作"22/23"** —— 登记后该文字即失效，
并外溢到其他 Loop/执行者的验证面。属**收口期协调变更**，**W8 二选一**：
① 登记并同步改 `LOOP.yaml` 文案；② 删除回退表与对应条目。
（代价：暂存一处"回退表"，已在此**显式命名其临时性**，避免它悄悄变成第二个权威。）

### 结果

```
  OK  gk17-ref-anchor          注入被检出（FAIL，受控失败）
  OK  gk17-triple-consistency  注入被检出（FAIL，受控失败）
  注入测试: 20 项受控失败被检出 / 0 项崩溃 / 0 项注入有效但未被检出 / 0 项有效性未确立
  __GATE_VERDICT__=INCONCLUSIVE
```

- 注入数 **18 → 20**，两道 GK17 门禁**均被检出**；
- **0 崩溃 / 0 空转注入 / 0 未确立**；
- 仓库在运行后**干净**（`finally` 还原生效，脚本还自动回滚了 1 个副作用产物）；
- `make check` **exit 0 / 22-23 未变** ⇒ **零外溢已证实**。

### ⚠️ 关于 `__GATE_VERDICT__=INCONCLUSIVE`（**必须说清，不得含糊**）

脚本自身总判定是 **INCONCLUSIVE**，原因是**另有 3 个门禁缺负例证据**
（`probe-mutation-tests` 与 `semantic-consumption` 为**正当排除**，`semantic-rule-gate` 因目标只读按纪律跳过）——
**这三个都非 GK17 门禁，属 W0 既有基线**。

⇒ 本 Loop 的门禁 `gk17_mutation_regression` 的通过条件是**被限定的**：
「GK17 两道门禁在 OK 列表中，且 0 崩溃 / 0 未检出 / 0 未确立」。
它**不**宣称 `run_gates` 整体通过；那条 INCONCLUSIVE **不归本 Loop 收口**，已写入 `LOOP.yaml` 的 `pass_condition` 原文。

### 残余

- D2/D4 的变异探针仍**未内置**到 `gk17_triple_consistency_check.py` 的 `--selftest`；
  但现在它们已被**仓内唯一机制**（`gate_injection_tests.py`）覆盖 —— 见 `INJECTIONS` 的
  `gk17-triple-consistency`（本体注入关系实例 → D1 检出）与 `gk17-ref-anchor`（地图注入假资产 → 拒绝）。
  **D2/D4 的专门探针**（破坏类声明 / 注入悬空引用）仍只在 TL 的外部临时根上执行过，**记为 W8 必办**。

### 门禁总表：**10 pass / 1 fail**

| pass | 上述 9 项 + **`gk17_mutation_regression`** |
|---|---|
| **fail** | `frontend_test`（环境限制） |
