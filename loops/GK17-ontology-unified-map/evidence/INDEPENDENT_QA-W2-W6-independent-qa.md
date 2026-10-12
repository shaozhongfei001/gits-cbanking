# GK17 · W2 + W6 独立对抗性复核报告（判定建议）

```text
PACKET        : GK17-ontology-unified-map
ENTRYPOINT    : evidence/INDEPENDENT_QA_PACKAGE-W2-W6.md（§0 / §8 已先读）
REVIEWER      : independent-qa（团队 gk17-qa）
DATE          : 2026-09-16
WORKSPACE     : /home/szf/dev/gits-cbanking
BRANCH / HEAD : recover/PI-ARCH-product-catalog @ 71169042227ce86f870cea81b50f77bf985ffe7f（工作区 dirty，以 sha256 为准）
VERDICT_MODE  : 判定建议（**不是 QA_PASS**；签署权在 Owner）
```

---

## 0.0 【第一条发现】能力自检 + 我实际跑过的命令数

### 0.0.1 能力清单（实测，非声明）

我**有**完整的命令执行能力。实测输出（原样）：

```text
shell: /usr/bin/bash  bash 5.1.16
sha256sum: sha256sum (GNU coreutils) 8.32
python3: Python 3.10.12
git: git version 2.34.1
tar: tar (GNU tar) 1.34
rsync: rsync  version 3.2.7  protocol version 31
java: openjdk version "21.0.11" 2026-04-21
mvnw: Apache Maven 3.9.12 (848fbb4bf2d427b72bdb2471c22fced7ebd9a7a1)
make: GNU Make 4.3
网络: https://api.github.com -> 200
```

可用工具域：shell / `sha256sum` / `python3`（含 import 门禁脚本模块）/ `git`（**只读**）/ `tar` / `rsync` /
`java 21` / `./mvnw`（**完整 Maven 构建与测试**）/ `make` / 网络 `curl`。
写盘能力仅限被授权的 `evidence/INDEPENDENT_QA-W2-W6-independent-qa.md` 与自建临时目录（已清理）。

### 0.0.2 命令计数（按本会话调用顺序计数）

| 类别 | 次数 |
|---|---|
| `execute_command`（shell 命令） | **51** |
| `read_file`（源码/文书/日志） | **14** |
| 落盘写入 | **1**（仅本报告） |
| **git 写操作** | **0** |

### 0.0.3 因此哪些判定我**无法**独立验证（只能标注"未独立验证"）

| 项 | 为什么无法独立验证 | 我在报告中的处理 |
|---|---|---|
| `gk17_prodcard_projection` 门禁 | 其输入源在**工作区外**（`Leibniz-KERT/examples/product-recommendation-assets/03_core`）。我核对了**产物**（`products.ttl`/`UNRESOLVED.json` 内容 + sha256），**未重跑该门禁** | §5.3-5 标注"未复核" |
| `frontend_test` | 沙箱 `npm ci` 批量删除守卫（`SAFE_DELETE_BULK_CONFIRM_REQUIRED`）是**工具层**拦截，非代码问题 | §5.3-6 标注"未跑，未计为通过" |
| `make backend-test` | ⚠ 见 §4 第 7 条 —— 我**未重跑**该命令，但我在**同一环境**做了端点级复现，并发现它在**同一天上午曾 BUILD SUCCESS** | §5.3-7 已按端点级证据重写 |
| 真实 dsh/KERT 平台、A-Box 实体查询、本体语义驱动 | 这些能力在代码/数据中**不存在**，不是"我没有能力验证"，而是**被测对象不存在** | Q1/Q2/Q3 |
| "起草期曾把 40 记成 38" | **过程陈述，无第三方可核** | §3.6 标注"不可独立验证" |
| OWL 推理层一致性 | 我未引入 reasoner；我的盲区测试是**静态文本层** | §3.7 已自限 |

> **我明确声明**：本报告中**每一条"通过"都来自我自己跑出来的标准输出**（见各条 §2/§3 的原始命令与输出片段）。
> 凡我没有能力或没有输入去验证的，我**没有**写"通过"，而是写"未复核 / 无法判定"。
> 唯一一次**部分依赖 TL 提供的日志**的地方，已在 §4 第 7 条显式标注，并附有我自己做的端点级复现作为独立支撑。

---

## 0. 你是如何独立的

### 0.1 独立性声明（必须显式，且是**降级**的）

> **本次复核是「授权下的降级独立」，不是真第三方。**
>
> - 本会话由 **TL 派生**（团队 `gk17-qa`，`ROLE_BOARD.independent_qa.independence_declaration` 已如实写成"降级独立"，
>   `NEXT_SESSION.md:32` 同口径）。TL 编写了入口包、选择了靶标、提供了复核配方。
>   **"靶标由被复核方选定"这一事实本身构成残余偏差风险**，我不声称已消除它。
> - 因此本报告的产出定位为 **「判定建议」**，**不构成 `QA_PASS`**，**不能**被引用为 `QA_PASS`。
> - 我能声称的独立性仅限于：**我执行的每条命令都是本会话新跑出来的**，
>   结论来自我自己看到的标准输出，而不是转述 TL 的日志；并且我做了 TL **没有**要求我做的对抗性测试（见 §3.7）。
> - 我**没有**收到、也**没有**接受任何"期望全绿"的暗示；下面 §4 记录了 6 条对 TL 表述的否定或修正意见。

### 0.2 工作边界（我实际做了什么、没做什么）

| 项 | 做 / 没做 |
|---|---|
| 写入路径 | 仅本文件 `evidence/INDEPENDENT_QA-W2-W6-independent-qa.md`；临时物在 `.tmp-qa-independent-qa/`（用后删除） |
| 变异实验 | **全部在临时副本上做**：`rsync -a --exclude=.git --exclude=node_modules --exclude=target ...` 到 `.tmp-qa-independent-qa/repo/`（374M，1.0s，副本源文件 sha256 与真实仓一致） |
| 原仓源码 | **零修改**。M1/M2/M3 变异全部施加在副本；收工核对 `DefaultActivationPlanner.java` 仍为 `83e3b300e5e5ffb4…` |
| git 写操作 | **零**（未 commit / checkout / stash / add） |
| `QA_PASS` | **未写入** `EVIDENCE.json` 或任何文件 |
| 门禁执行 | **全部串行**（§0.2 要求）；未与任何其他进程并发跑门禁 |
| 被 `make check` 重写的既有噪声 | `evidence/gk-ke-chain-trace/trace.json`、`evidence/gk-ke-capability-probe/report.json` 被重写；我用**运行前的 tar 快照**逐字节还原（**没有用 `git checkout`**），还原后 `git status --short` 与运行前**完全一致**（见 §3.1.6） |
| 约束自己 | 不作 `PRODUCTION_READY` / `REAL_E2E_PASS` 声明；不把环境红或 `INCONCLUSIVE` 计入通过 |

---

## 1. 靶标核对（逐项 sha256）

命令：`sha256sum <每一项>`（§8.2 清单为 16 位前缀，下表给出**完整值**的前 16 位与清单比对）

| # | 文件 | 实测 sha256（前 16） | 清单（§8.2） | 一致? |
|---|---|---|---|---|
| 1 | `scripts/gk17_triple_consistency_check.py` | `38ac71deea1c50d9` | `38ac71deea1c50d9` | ✅ |
| 2 | `scripts/gk17_ref_anchor_check.py` | `2d679cb9af441060` | `2d679cb9af441060` | ✅ |
| 3 | `scripts/gk17_prodcard_to_rdf.py` | `1011ca4f881dfae4` | `1011ca4f881dfae4` | ✅ |
| 4 | `specs/semantic/gits-core.owl.ttl` | `705578d6324abd0c` | `705578d6324abd0c` | ✅ |
| 5 | `specs/semantic/gits-core.linkml.yaml` | `11c99356faa23493` | `11c99356faa23493` | ✅ |
| 6 | `specs/knowledge-architecture/schemas/activation-plan.schema.json` | `291f933905a51c15` | `291f933905a51c15` | ✅ |
| 7 | `specs/knowledge-architecture/instances/product/products.ttl` | `e70bbe45bebcca2e` | `e70bbe45bebcca2e` | ✅ |
| 8 | `specs/knowledge-architecture/instances/product/UNRESOLVED.json` | `225e04bfae95e77b` | `225e04bfae95e77b` | ✅ |
| 9 | `modules/semantic-runtime/src/main/java/com/gien/gits/semantic/OntologyPort.java` | `5214da71e3fdba73` | `5214da71e3fdba73` | ✅ |
| 10 | `adapters/semantic-jena/src/main/java/com/gien/gits/adapter/jena/JenaOntologyAdapter.java` | `30f09a97acb87a3b` | `30f09a97acb87a3b` | ✅ |
| 11 | `modules/knowledge-architecture/src/main/java/com/gien/gits/knowledge/plan/DefaultActivationPlanner.java` | `83e3b300e5e5ffb4` | `83e3b300e5e5ffb4` | ✅ |

**结论：11/11 全部一致。我复核的状态 = §8.2 冻结清单的状态。**

补充事实（不影响一致性判定，但记录在案）：
- §8.2 对第 9/10 项写的是**省略号路径**（`…/semantic/OntologyPort.java`、`…/jena/JenaOntologyAdapter.java`），
  实际路径为 `com/gien/gits/semantic/` 与 `com/gien/gits/adapter/jena/`。按省略号展开的首个猜测路径**不存在**，
  我据文件名定位后才核对成功。**建议**（非阻塞）：W8 收口时把这两行写成完整路径，
  否则下一位复核者会先撞一次"文件不存在"。
- `git HEAD = 71169042227ce86f870cea81b50f77bf985ffe7f`，与 §8.2 一致；工作区 **dirty**（确认）。

---

## 2. Q1–Q6 逐条作答

### Q1 — V1 的 ②「本体查实体/关系」当前只到 T-Box 加载 + 查询声明

**1) 判定：不通过（就判据字面的"完整链"而言）。** 四个步骤中 ①③⑤ 达成、④ 见 Q2、**② 未达成**。

**2) 依据**

- 判据 §3 原文要求"路由裁决 → **本体查实体/关系** → 地图按结果定向激活资产 → SKILL 调用 → 输出证据"；"完整链"是 ACCEPT 的措辞。
- `DefaultActivationPlanner.plan()` 对本体只做 **`ontologyPort.load()`**（`modules/knowledge-architecture/src/main/java/com/gien/gits/knowledge/plan/DefaultActivationPlanner.java:115`），
  然后把 `contract.semanticQueries()` **原样拷贝**进计划（同文件 `:190`）。**没有任何查询被执行**。
- 即：计划里的 5 条 `semanticQueries` / 4 条 `ruleChecks` 是**合同声明值**，不是**查询结果**。
- A-Box 为 0 ⇒ 即使有执行器也无物可查（见 §3.5）。

**3) 我实际执行的命令 + 原始输出**

```bash
$ grep -rn "SemanticQueryPort" apps/api/src/main/
（无输出）
$ grep -rn "SemanticQueryPort" apps/api/src/main/ | wc -l
0
$ grep -rln "SemanticQueryPort" --include=*.java .
./modules/semantic-runtime/src/main/java/com/gien/gits/semantic/SemanticQueryPort.java
./modules/semantic-runtime/src/main/java/com/gien/gits/semantic/FailClosedSemanticQueryGuard.java
./apps/api/src/test/java/com/gien/gits/api/e2e/V1PrevisitChainTest.java
```

`SemanticQueryPort` **在 `apps/api/src/main` 零命中**（只存在于模块定义与一个测试文件里）⇒
**生产装配面上查询执行器不存在**。TL 在 `gk17-v1-previsit-chain.json` 的 `v1CoverageGaps[0]` 里对此**如实披露**，
我确认该披露属实、无粉饰。

**4) 不确定性与信心**

- **信心：高**（② 未执行为确定性事实，有源码与 grep 双重支撑）。
- 不确定性在于**判定权归属**：② 未达成是否构成 W6 的 ACCEPT 阻断，是 **Owner 的范围裁定**，不是我可代答的技术问题。
  TL 在包 §4 Q1 给出的 (a)/(b) 两种读法是诚实的，但**我不接受把 (a) 当作默认**——
  判据写的是"完整链"，把未执行的步骤读成"链路已通"是**降级判据**。
- **我不接受**下列任何表述：② 已达成 / 实体级查询可用 / "本体语义参与了路由"。

---

### Q2 — V1 的 ④ SKILL 调用为策略性 fail-closed（有轨迹、无业务产物）

**1) 判定：通过（就"调用真实发生且可复核"这一层），并强制附带两条限定。**

**2) 依据**

- `apps/api/src/main/java/com/gien/gits/adapter/skill/FallbackSkillExecutionAdapter.java:34-39`：
  `NO_LOCAL_FILL` 集合**确实包含** `skill-customer-previsit-report`（第 35 行），
  命中后返回 `SkillExecutionErrorItem("KERT_REQUIRED", …)` + `TraceStep("kert","failed",…)`（同文件 `:43-54`）。
- `V1PrevisitChainTest.java:152-155` 有**防误判对照**：策略外技能 `gk17-v1-port-probe` 断言 `isOk()` 为真。
  ⇒ 这确实把"**策略拒绝**"与"**端口故障**"区分开了，不是把两者混为一谈。

**3) 我实际执行的命令 + 原始输出**

```bash
$ ./mvnw --batch-mode --no-transfer-progress -pl apps/api -am test \
    -Dtest=V1PrevisitChainTest -Dsurefire.failIfNoSpecifiedTests=false \
    -Dgk17.evidence.dir=target/qa-evidence          # 在临时副本内执行
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, -- in com.gien.gits.api.e2e.V1PrevisitChainTest
[INFO] BUILD SUCCESS
```
产物（副本内独立重跑，非引用 TL 日志）：
```text
step4 skill = {"skillId":"skill-customer-previsit-report","invoked":true,
  "mode":"fallback(MockLlmClient) —— 非真实 dsh/KERT 平台","policyNoLocalFill":true,
  "note":"…策略性 fail-closed（KERT_REQUIRED），不补数",
  "trace":[{"phase":"kert","status":"failed","kiId":null,"message":"KERT 未配置或不可达，未使用本地种子补数"}]}
step4b      = {"skillId":"gk17-v1-port-probe","isOk":true,"status":"OK", …}
```

**4) 不确定性与信心**

- **信心：高**（判定拒绝的原因由名单常量与对照断言共同确定）。
- **限定 ①（必须随证据一起读）**：该"端口可用"由 **`FallbackSkillExecutionAdapter` 自身**证明 ——
  即证明的是**回落通道**可用，**不是**证明真实 KERT/dsh 端口可用。证据 JSON 的 `mode` 字段已如实写"非真实 dsh/KERT 平台"，
  我在报告中沿用该口径，**不接受**把它简述为"SKILL 已跑通"。
- **限定 ②**：④ 的产物是**轨迹**（trace），**不是业务产物**。"有轨迹"能满足判据对"输出证据"的要求（判据把"通过"定义为有可复核原始输出），
  但**不能**被引用为"能力已验证"或"端到端业务闭环已实现"。

---

### Q3 — V2：机制成立，但本体语义未驱动选择

**1) 判定：通过（就判据字面「只改本体 ⇒ 计划必须变化」）；同时强制声明：该"变化"承载的语义信息量为 0。**

**2) 依据（这是本报告最关键的一条事实修正）**

- 判据字面成立：我的 M3 变异（从 `deterministicContent` 移除本体版本）使该用例 **FAIL 1 条**（§3.3），
  说明 `planHash` 与本体确实有因果边，**不是空转**。
- **但**：`ontologyVersion` 的取值形态是 `CTR-SEM-002@sha256:705578d6324abd0c` ——
  **`705578d6324abd0c` 就是本体文件的 sha256 前缀**（我用 `sha256sum specs/semantic/gits-core.owl.ttl` 核对，完全相等）。
  `DefaultActivationPlanner.java:269-273` 把该**内容哈希串**拼入哈希输入。
  ⇒ **任何字节级改动**（哪怕加一个空格或一条注释、改一个 `rdfs:label` 文案）都会改变 `planHash`。
- 而 `selectedAssets` / `ruleChecks` / `skills` 全部来自 **激活合同**（`:190-192`、`resolveAssets()` `:227-252`），
  **没有一处读本体的类、属性或关系**。
- ⇒ 正确的表述是：**"本体被读取并被哈希"**，**不是**"本体语义参与了计划决策"。
  "计划必须变化"这一判据**无法区分**"本体语义被消费"与"本体文件字节变了"。

**3) 我实际执行的命令 + 原始输出**

```bash
# (a) 判据字面成立 —— 独立复跑 V2 基线
$ ./mvnw ... -pl apps/api -am test -Dtest=V2OntologyOnlyChangeTest ...
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0
# (b) 机制非空转 —— M3 变异后
[ERROR] Tests run: 1, Failures: 1, Errors: 0, Skipped: 0
[ERROR] V2OntologyOnlyChangeTest.changingOntologyOnlyChangesThePlanWhileTheMapStaysUntouched:122
        只改本体（新增类）而计划未变 ⇒ 本体未被消费 ⇒ V2 不成立 ==> expected: not equal but was: <57bedc00eb50da5c>
# (c) 语义未驱动的源码证据
$ sed -n '175,201p' modules/knowledge-architecture/.../DefaultActivationPlanner.java
        String planHash = sha256(deterministicContent(
                route.mode(), selectedAssets, contract, ontology.ontologyVersion()));
        ...
                contract.semanticQueries(),  contract.ruleChecks(),  contract.skills(),
```
```bash
$ sha256sum specs/semantic/gits-core.owl.ttl
705578d6324abd0c1bd2bd670e6f3c0ffd8e04c358d0134246c89a3acfc38d00  specs/semantic/gits-core.owl.ttl
# 与 plan 中 versions.ontology = CTR-SEM-002@sha256:705578d6324abd0c 的前 16 位完全一致
```

**4) 不确定性与信心**

- **信心：高**（版本=内容哈希、以及资产/规则/技能取自合同，均为源码级确定事实）。
- 我不接受把 V2 表述为"**本体已参与知识路由**"或"**本体内容驱动计划**"。可接受的表述只有：
  "**本体内容的哈希进入了计划指纹，且该边经变异验证非空转**"。
- 用例自身的**绊线断言**（`V2OntologyOnlyChangeTest.java:136-141` 断言 `selectedAssets/ruleChecks/skills` 在各变体下**相同**）
  是把该限制钉成可执行的正确做法，我**认可**这一设计；但它同时证明：**判据 V2 目前对"语义消费"完全没有约束力**。
- 若 ACCEPT 要求语义驱动，则 V2 **不通过**（此判断我支持 TL 在包 §3 V2 中给出的同一提示）。

---

### Q4 — V3 的锚定空间是既有权威 ID 空间，不是 A-Box 个体

**1) 判定：通过（就"引用锚定 fail-closed 机制"而言）；就判据字面的"不存在的**个体**"= 无法判定（A-Box 无个体可锚）。**

**2) 依据**

- 门禁基线 `verdict=PASS violations=0`，`--selftest` = `SELFTEST RESULT: PASS (6 mutations)`（6 个变异逐个 FAIL + `[restored] PASS`）。
- 锚定空间实测：`activationContract=3, asset=21, domain=3, map=4, routePolicy=1, skill=5, taskType=5`。
  这些**全部是 ID 空间**（KM/KD/ASSET/SP/AC/RP + `entrypoints.tasks` 对齐 `gits:TaskType`），**不含任何 A-Box 个体**。

**3) ⚠ 本条最重要的新增发现（TL 未在包 §3 V3 中提示）**

门禁**自己**打印了一条诚实缺口，而 §2/§3 V3 的"已知限制"栏**没有把它列出来**：

```text
HONEST GAP [domain]: KD-* 无独立锚点来源：registry 无 KD 条目、本体无 KnowledgeDomain 类
（gits-core.owl.ttl / gits-core.linkml.yaml 均无）、gits: 类中无 KD 类。
  assetManifestDomainValues=['KD-CORP-RM']
  selfDeclaredInMaps=['KD-CORP-RM', 'KD-CORP-RM-PREVISIT', 'KD-CORP-RM-RECON']
  selfDeclaredOnly(no external anchor)=['KD-CORP-RM-PREVISIT', 'KD-CORP-RM-RECON']
  soundness=NOT_COUNTED_AS_PASS_ASSERTION
```

⇒ **3 个 KD 域 ID 中有 2 个只有"地图自述"、无外部锚点，按门禁自身口径 `NOT_COUNTED_AS_PASS_ASSERTION`。**
它们出现在 `"anchorSources"` 计数里（`domain=3`），使"锚点来源数"看起来比实际可信的多。
`NEXT_SESSION.md:110` 确实把 `KD-* 无独立锚点` 列进"不得计为通过"，**但包 §2/§3 V3 的判定清单没有**——
**读包的人（含 Owner）看不到它**。这是一条**披露位置不当**的问题，不是隐瞒。

**4) 我实际执行的命令 + 原始输出**

```bash
$ python3 scripts/gk17_ref_anchor_check.py --root .
gk17-ref-anchor-check: PASS  (criterion V3)
anchor sources: activationContract=3, asset=21, domain=3, map=4, routePolicy=1, skill=5, taskType=5
references checked: activationContract=4, asset=21, domain=3, mapRef=3, routePolicy=4, skill=11, taskType=10
maps scanned: 4  taskType anchored via gits:TaskType (declared=True)
no unanchored reference found
HONEST GAP [domain]: …  soundness=NOT_COUNTED_AS_PASS_ASSERTION
$ echo $?
0
$ python3 scripts/gk17_ref_anchor_check.py --root . --selftest
--- mutation: fake_domainRef ---
  DETECTED: [asset] ASSET-DOMAIN-PROBE-GK17 referenced by …/DOMAIN_MAP.md (field: assetRefs, NO_ANCHOR_IN_AUTHORITATIVE_SOURCE)
  result  : OK (mutation rejected)
--- mutation: fake_mapRef ---
  DETECTED: [map] …/DOES-NOT-EXIST-GK17.md … (field: domains[].mapRef, MAP_REF_PATH_NOT_FOUND)
[restored] verdict=PASS  violations=0
SELFTEST RESULT: PASS  (6 mutations)
$ echo $?
0
```
（判据 §3 中"判据字面形状"点名的 `fake_assetRef ⇒ ASSET-DOES-NOT-EXIST-GK17 … assetRefs, NO_ANCHOR_IN_AUTHORITATIVE_SOURCE`
我**没有**在输出里逐字看到同名项；我看到的是 `ASSET-DOMAIN-PROBE-GK17`（同一 code、同一字段）。
形状一致、ID 名不同，**不影响结论**，但清单里的字面样例与实测输出不逐字对应，记录在案。）

**4) 不确定性与信心**

- **信心：高**（机制非空转已由 6 个变异独立复现）。
- 我不接受表述"V3 已锚定 A-Box 个体"或"地图引用的个体都在本体中存在"。
- **必须随 V3 一并读出**：`KD-CORP-RM-PREVISIT` / `KD-CORP-RM-RECON` 属 `NOT_COUNTED_AS_PASS_ASSERTION`。

---

### Q5 — V4 的 D2/D4 变异探针 + `gate_owner` 所有权回归（Tick 17）

**1) 判定：通过。** D2/D4 专门探针**确实已内置**，且我**独立证明**了判定逻辑非空转。

**2) 依据**

`scripts/gk17_triple_consistency_check.py` 新增 `run_projection_probes()`（`:867-955`），
在**内存中的投影副本**上分别注入 D2 / D4 变异，判据四条：期望项计数**严格增加**、交叉项**不误触发**、撤销回基线、真实投影文件 sha256 未变。

**3) 我实际执行的命令 + 原始输出**

```bash
$ python3 scripts/gk17_triple_consistency_check.py --json
verdict PASS      exit=0
inputCardinality {"ontologyStatements":68,"ontologyClasses":32,"ontologyObjectProperties":34,
                  "projectionFiles":1,"projectionIndividuals":13}
counts {"D1…":0,"D2…":0,"D3…":0,"D4…":0}
vacuity []        findings 0        failures []
MUT D1: baseline=0 mutated=1 caught=True restored=True byteIdentical=True tempRemoved=True
projectionProbes:
  P-D2: 注入 products.ttl 内存副本  期望 D2 0→1 ⇒ 已捕获(caught=true)
        交叉项 D4 0→0 ⇒ 不误报(cross_clean=true)   撤销回基线=true
  P-D4: 注入 products.ttl 内存副本  期望 D4 0→1 ⇒ 已捕获(caught=true)
        交叉项 D2 0→0 ⇒ 不误报(cross_clean=true)   撤销回基线=true
  baseline_consistent=true   filesUntouched=true
```

**"判定逻辑非空转"独立复现**（**在自建临时副本 `noop-probe.py` 上做，原脚本零改动**；
`noop-probe.py` 的 sha256=`9933c3e5bbb5c0ca…`，原脚本复核后仍为 `38ac71deea1c50d9…`）：

```bash
# 把 "caught": mutated[expect_key] > expect_base  改成恒 False
$ python3 .tmp-qa-independent-qa/noop-probe.py --root .    # 只读，不改任何文件
        期望 D2 计数增加：0 → 1 ⇒ **未捕获**
        期望 D4 计数增加：0 → 1 ⇒ **未捕获**
不一致项合计：0
gk17-triple-consistency-check: FAIL
  - **P-D2 变异未被捕获** ⇒ D2 断言空转（noop），门禁无效
  - **P-D4 变异未被捕获** ⇒ D4 断言空转（noop），门禁无效
exit=1
$ python3 scripts/gk17_triple_consistency_check.py --root . ; echo $?
0        # 原样脚本同根目录 ⇒ PASS，证明转红来自我的变异而非环境
```
⇒ TL 的声明（§8.1）**与事实一致**，且请特别注意：**在断言被破坏的情况下，门禁仍打印"不一致项合计：0"与 D1–D4 全 `OK`** ——
**只有变异探针把它判红**。这正说明"0 不一致"不能单独作为 PASS 依据，D2/D4 探针必须保留。

**4) ⚠ 我另外做了 TL 未要求的对抗测试，并找到两个可绕过盲区（详见 §3.7）** —— 这两点**不影响** Q5 的"探针非空转"判定，
但影响 V4 自称的"**越权写必须检出**"的强度。请务必与 Q5 一并读。

**5) 关于 `gate_owner` → TL 的所有权回归，我的单独表态：**

> **有条件接受。**
>
> **接受的理由**（三条，均为可核事实）：
> 1. `gate_owner` 侧确已无活动作者：`ROLE_BOARD` 原来把它记成 `status=waiting_on_W1`（**已失真的死状态**，与 W1 早已 ACCEPT 矛盾）；
>    Tick 9 已有"作者停止逾 2 小时 ⇒ 所有权回归 TL"的**先例**（`ORCHESTRATOR.md:161`）。
> 2. 改动**是收紧而非放宽**：`git --no-pager diff -U0 scripts/gk17_triple_consistency_check.py` ⇒ **+198 / −4**，
>    且**被删除的 4 行全部是结构性重排**（函数签名扩展、docstring 扩写、注释移位、调用点扩展），
>    **没有删除任何一条判定条件**；新增的全是 `failures.append(...)`（新增判红路径）。
> 3. 改动**自证非空转**：我按 §8.1 独立复现，破坏判定后**必须转红**（上面原始输出）。
>
> **条件（必须落实，否则我改为不接受）：**
> 1. **把所有权回归写进 `ROLE_BOARD.yaml` 本身，而不是只写在 `ORCHESTRATOR.md` 的叙述里。**
>    现状：`ORCHESTRATOR.md:530` 声称"已同步写入 `ROLE_BOARD.yaml`"，但 **`ROLE_BOARD.yaml` 里没有这条记录**
>    （`gate_owner.exclusive_paths` **仍然**把 `scripts/gk17_triple_consistency_check.py` 列为 `gate_owner` 独占）。
>    这是 §4 第 1 条缺陷。⇒ 要么在 `ROLE_BOARD` 增 `ownership_overrides` 字段显式记录，要么从 `gate_owner.exclusive_paths` 中移出并注明。
> 2. **该文件后续每次改动都附"判定逻辑变异复验"**（像 Tick 17 那样），否则"改门禁的人"与"验门禁的人"合一，独立性归零。
> 3. **W8 收口时把 `scripts/gate_injection_tests.py` 一并纳入同一口径** ——
>    它是 `gate_owner.exclusive_paths` 的第二项，且是"元门禁"（门禁的门禁），其所有权**不能悬空**。

---

### Q6 — W2 的两条设计裁定（本体加载位置；`evidence` 不入 `planHash`）

**1) 判定：两条均通过，且②我在一个 TL **没有用过**的条件下独立验证成功。**

**2) 依据**

- **裁定①（本体加载位置）**：`DefaultActivationPlanner.java:111-119` 的 `ontologyPort.load()` 与 fail-closed 返回
  位于**请求级护栏之后**（`:92-109`）、**路由解析之前**（`routeEvaluator.evaluate(...)` 在 `:123`）。
  本体是四条 `routeMode` 的共同前置，代码位置与声明一致 ⇒ **不给部分 credit** 的意图在代码里成立。
- **裁定②（`evidence` 不入 `planHash`，只有版本入哈希）**：`deterministicContent(route.mode(), selectedAssets, contract, ontology.ontologyVersion())`
  （`:175-176`），`ontologyVersion` 拼入（`:273`）；`ontology.evidence()` **只进 `Trace`**（`:200`），**不进哈希**。源码与声明一致。

**3) 我实际执行的命令 + 原始输出（这条是我这次复核里最强的一条独立证据）**

我在**完全不同的绝对路径**（`/home/szf/dev/gits-cbanking/.tmp-qa-independent-qa/repo/`）下重跑 V1，得到：

```text
我的复跑： step2_ontology.sourceRef      = /home/szf/dev/gits-cbanking/.tmp-qa-independent-qa/repo/specs/semantic/gits-core.owl.ttl
           step2_ontology.evidence       = CTR-SEM-002@sha256:705578d6324abd0c [classes=32,…,source=/home/szf/…/.tmp-qa-independent-qa/repo/…]
           step5_plan.ontologyEvidence   = （同上，含我的副本路径）
仓内既有： sourceRef / evidence / ontologyEvidence 均含 /home/szf/dev/gits-cbanking/specs/…

$ diff <(我的产物，去 generatedAt) <(仓内产物，去 generatedAt)
25c25  "evidence" …
30c30  "sourceRef" …
131c131 "ontologyEvidence" …
（**仅 3 处，全部是环境相关的绝对路径**）

两侧： step5_plan.planHash = a2413b72e01d7430      ← **完全相同**
```

⇒ 在**两处真实不同来源**下，`evidence` **确实不同**（反空转前提成立），而 `planHash` **相同**。
这比用例自身的 `planHashIgnoresOntologySourcePathSoPlansStayReplayableAcrossMachines` 更强：
它是**跨真实机器路径**的验证，而不是同一台机器上构造两个字符串。
**两条设计裁定我都认可。**

**4) 不确定性与信心**：**信心：高**。

---

## 3. 对抗性检查结果

### 3.1 输入基数自查（每道门禁"真的读到了输入"吗）

| 门禁 | 我报出的输入基数（命令原始输出） | 0 不一致是否可能是"什么都没解析" |
|---|---|---|
| `gk17_triple_consistency_check` | `ontologyStatements=68`、`ontologyClasses=32`、`ontologyObjectProperties=34`、`projectionFiles=1`、`projectionIndividuals=13`；地图 4 个；`vacuity=[]` | **不是**。且脚本内含 anti-vacuity 前置（`:1030-1044`）：语句非空却解析出 0 类/0 属性/0 个体即判 FAIL。我另用**该脚本自身的解析器**独立复算：`个体数=13、语句数=13、谓词={rdfs:comment,rdfs:label,type}` |
| `gk17_ref_anchor_check` | 锚点来源 `activationContract=3, asset=21, domain=3, map=4, routePolicy=1, skill=5, taskType=5`；被检引用 `activationContract=4, asset=21, domain=3, mapRef=3, routePolicy=4, skill=11, taskType=10`；`maps scanned 4`；`taskType anchored via gits:TaskType (declared=True)` | **不是**。⚠ 但 `domain` 的 3 个锚点来源中 **2 个是"地图自述"（`NOT_COUNTED_AS_PASS_ASSERTION`）**，见 Q4 |
| `gate_injection_tests` | `注入测试: 20 项受控失败被检出 / 0 崩溃 / 0 未检出 / 0 有效性未确立`；`gk17-ref-anchor` 与 `gk17-triple-consistency` 均在 OK 列表；`[UNCOVERED] 2 项`（`probe-mutation-tests` / `semantic-consumption`）+ `SKIP 1 项`（`semantic-rule-gate` 目标只读） | **不是**。20 项有真实注入目标 |
| `make check` / `run_gates.py` | 23 项门禁：`[PASS]=21`、`[FAIL]=1`（`semantic-consumption`，readiness）、`[INCONCLUSIVE]=1`（`gate-injection-tests`）；`integrity_failed=[]`（故 `INTEGRITY FAILURES:` 行**未打印**） | **不是**，但见 §4 第 2 条：汇总行 `22/23` 把 INCONCLUSIVE 计进了分子 |
| `./mvnw test` | api `603/0/0/4`、worker `22/0/0/0`、15 模块 SUCCESS | **不是** |
| `make generate` | 注册表 `contracts` 62 个；我另做**注入证明非空转**（见 3.1.7） | **不是** |

### 3.1.6 `make check` 的写副作用与我的还原（含原始输出）

```bash
$ git status --short > status-before.txt   # 134 行
$ make check ; echo $?
0
$ git status --short > status-after.txt
$ diff status-before.txt status-after.txt
11a12,13
>  M evidence/gk-ke-capability-probe/report.json
>  M evidence/gk-ke-chain-trace/trace.json
```
⇒ §0.3 的预警**属实**：`make check` 每次都会重写这两个**受版本控制**的证据文件。
我用**运行前的 `tar` 快照**还原（**未使用 `git checkout`**）：
```bash
$ tar xzf pre-check-snapshot.tgz evidence/gk-ke-capability-probe/report.json evidence/gk-ke-chain-trace/trace.json
$ diff status-before.txt status-restored.txt && echo OK
OK      # 工作区脏状态与运行前逐字一致
```

### 3.1.7 `make generate` 非空转注入（副本内）

```bash
$ make generate ; echo $?
contract-generate: PASS
0
$ git status --short generated/     # 空 ⇒ 生成是幂等的，generated/ 逐字节未变

# 在副本内注入合法源变更（给 Customer 加一个属性）
$ python3 scripts/contract_pipeline.py generate
before: 909f0dd8dc768a04   →   after : 70afd455e5c0d63a     # generated/semantic/gits-core.schema.json
$ grep -c qa_probe_field generated/semantic/gits-core.schema.json
1
# 反向：注入非法源（JSON 后追加注释）⇒ fail-closed
$ python3 scripts/contract_pipeline.py generate ; echo $?
contract-generate: FAIL: invalid JSON/YAML-JSON source …: Extra data: line 344 column 1
2
```
⇒ 生成管线**既非空转、也非"什么都接受"**。

### 3.2 M1 —— 移除本体 fail-closed 守卫（**已执行，在副本上**）

```bash
$ ./mvnw ... -pl modules/knowledge-architecture -am test -Dtest=DefaultActivationPlannerTest ...
# 变异前（基线）
[INFO] Tests run: 18, Failures: 0, Errors: 0, Skipped: 0
[INFO] BUILD SUCCESS
# 注入后（sha256 由 83e3b300… → eee35880…）
[ERROR] Tests run: 18, Failures: 2, Errors: 0, Skipped: 0
[ERROR]   DefaultActivationPlannerTest.deniesWhenOntologyMalformedInsteadOfPlanningWithoutIt:358
          Unexpected type, expected: <PlanDecision.Deny> but was: <PlanDecision.AllowPlan>
[ERROR]   DefaultActivationPlannerTest.deniesWhenOntologyMissingInsteadOfPlanningWithoutIt:343
          Unexpected type, expected: <PlanDecision.Deny> but was: <PlanDecision.AllowPlan>
exit=1
# 还原
$ cp <原仓文件> <副本文件> ; sha256sum <副本文件>
83e3b300e5e5ffb4c28c3cb38450d785fa8d871ecfa73d2839cfc3b18789398d
```
⇒ **期望 FAIL 2 条，实测 FAIL 2 条**，且命中的正是 W2-2 点名的两条 fail-closed 负例。
**判定：与 §5 配方完全一致，无夸大。**

### 3.3 M3 —— 把本体版本从 `planHash` 移除（**已执行，在副本上**）

```bash
$ ./mvnw ... -pl apps/api -am test -Dtest=V2OntologyOnlyChangeTest ...
# 变异前
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0 / BUILD SUCCESS
# 注入后（sha256 → 143859dd…）
[ERROR] Tests run: 1, Failures: 1, Errors: 0, Skipped: 0
[ERROR]   V2OntologyOnlyChangeTest.changingOntologyOnlyChangesThePlanWhileTheMapStaysUntouched:122
          只改本体（新增类）而计划未变 ⇒ 本体未被消费 ⇒ V2 不成立 ==> expected: not equal but was: <57bedc00eb50da5c>
exit=1
# 还原并复验
$ sha256sum <副本文件>
83e3b300e5e5ffb4c28c3cb38450d785fa8d871ecfa73d2839cfc3b18789398d
$ ./mvnw ... -Dtest=V2OntologyOnlyChangeTest ...
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0 / BUILD SUCCESS
$ sha256sum modules/knowledge-architecture/.../DefaultActivationPlanner.java   # **原仓文件**
83e3b300e5e5ffb4c28c3cb38450d785fa8d871ecfa73d2839cfc3b18789398d
```
⇒ **期望 FAIL 1 条，实测 FAIL 1 条；还原后回到 PASS；原仓文件零改动。判定：一致。**

### 3.4 M2（可选）—— 同一变异的模块级 + 文件系统 IT 捕获面

```bash
$ ./mvnw ... -pl modules/knowledge-architecture -am test -Dtest=DefaultActivationPlannerTest ...
[ERROR] Tests run: 18, Failures: 1, Errors: 0, Skipped: 0
[ERROR]   DefaultActivationPlannerTest.planHashChangesWithOntologyVersionAndIsStableForSameVersion:372
          本体版本变了而 planHash 不变 ⇒ 判据 V2 在构造上不成立 ==> expected: not equal but was: <bbc77ab4d925bb29>
$ ./mvnw ... -pl adapters/knowledge-filesystem -am test -Dtest=DefaultActivationPlannerFilesystemIT ...
[ERROR] Tests run: 5, Failures: 1, Errors: 0, Skipped: 0
[ERROR]   DefaultActivationPlannerFilesystemIT.planHashChangesWhenOntologyContentChangesAndReturnsWhenRestored:182
          本体内容变而 planHash 未变 ⇒ 判据 V2 在构造上不成立 ==> expected: not equal but was: <57bedc00eb50da5c>
```
⇒ **模块 1 + 端到端 1**，与 §5 M2 声明的"FAIL（模块 1 + 端到端 1）"**逐字一致**。

### 3.5 A-Box 空洞检查

```bash
$ python3 - <<'PY'   # 用 gk17_triple_consistency_check.py 自身的解析器
个体数 = 13 ；语句数 = 13 ；出现过的谓词 = ['rdfs:comment', 'rdfs:label', 'type']
真实对象引用数（非 type 且 is_individual_ref）= 0  []
PY
```

**`products.ttl` 的对象引用 = 0，确认。** 13 个个体各自只有 `a gits:Product` + 一个 label + 一个 comment，
**没有任何个体↔个体关系边**（成因见 `UNRESOLVED.json`：40 处引用 / 12 个符号 **100% 悬空**，`relationInstances: 0`）。

⇒ **当前无法被真实数据触发的断言（必须逐条列出）：**

| 受影响断言 | 为什么当前无法被真实数据触发 |
|---|---|
| **D4「投影个体悬空引用」** | 无对象引用可悬空。它在真实数据上**恒为 0**；唯一证明它非空转的方式是 §8.1 的内存注入（我复现通过）。⇒ 属"**有能无力**"，**不得**被表述为"已验证投影无悬空引用" |
| **V1 步骤 ② "本体查实体/关系"** | `individuals=0`（本体 A-Box 为空）+ `products.ttl` 无关系边 + `SemanticQueryPort` 未装配 ⇒ 无实体可查、无关系可走 |
| **V2 的"给客户加一条互斥关系"这一变异形态** | 该变异只在**本体副本**里加一条 `gits:gk17V2CustProbe gits:mutuallyExclusiveWith gits:prod_set_001`，**没有下游消费者**；因为无 A-Box，它不可能改变任何资产/规则/技能选择（这正是 Q3 的语义强度问题） |
| **V3 的"A-Box 个体锚定"** | 锚定空间完全不含 A-Box；`entrypoints.tasks` 对齐的是本体 `gits:TaskType`（T-Box 声明），不是个体 |
| **W3.2/W4 的"事实对象→A-Box"** | 依赖已由裁定②③解锁，但**尚未开工**（`STATE.json: w4=not_started`） |
| **`UNRESOLVED.json` 的 `relationInstances=0`** | 100% 悬空是**数据缺陷/范畴错误**（已裁定不建映射表），**不是**"无异常" |

**⇒ 我明确不接受把 W6 表述为"V1–V4 已在实例级数据上全部验证通过"。**
可接受的表述：**"V1–V3 的机制在**造数/T-Box**层面可复核；V4 的 D1/D2/D4 由注入证明非空转；
A-Box 实体/关系面上的断言**当前无真实输入**，属 W3.2/W4。"**

### 3.6 裁定文书数字复算（`docs/architecture/GK17-四项悬置口径裁定-V1.0.md` §1.2 / §1.5）

```bash
$ python3 -c "import json;d=json.load(open('specs/knowledge-architecture/instances/product/UNRESOLVED.json'));\
print(len(d['unresolved']), d['unresolvedReferenceCount'])"
40 40
```
```text
唯一符号数 = 12   出现次数合计 = 40
  SETTLEMENT_ACCOUNT                24
  CORPORATE_E_BANK                   5
  CASH_MANAGEMENT                    2
  FX_FORWARD / CASH_POOL / WORKING_CAPITAL_LOAN / CROSS_BORDER_RMB_SETTLEMENT /
  BANK_ACCEPTANCE_DRAFT / RECEIVABLE_LEDGER_TOOL / ORDER_RECEIVABLE_CLOSED_ACCOUNT /
  DISCOUNT_SERVICE / FINANCIAL_ADVISORY     各 1
按字段分布: {'complementary_products': 28, 'prerequisite_product_ids': 12}
productIndividuals=13 / relationInstances=0
```

**逐条比对结论：§1.2 与 §1.5 的表【全部正确】，无一处数字错误。**

| 文书声明 | 我的复算 | 结论 |
|---|---|---|
| `len(unresolved) == unresolvedReferenceCount == 40` | `40 40` | ✅ |
| 唯一符号 **12** | `12` | ✅ |
| `SETTLEMENT_ACCOUNT` **24**（占 60%） | `24`（24/40 = 60%） | ✅ |
| `CORPORATE_E_BANK` **5** | `5` | ✅ |
| `CASH_MANAGEMENT` **2** | `2` | ✅ |
| 其余 9 个各 **1** | 各 `1` | ✅ |
| 合计 **40** | `40` | ✅ |
| 字段分布 `complementary_products 28 / prerequisite_product_ids 12` | `28 / 12` | ✅ |
| 产品卡 **13** / 关系实例 **0** | `13 / 0` | ✅ |

**关于 §1.2 的"TL 自纠"（我按要求质询的点）：**
- 我核到的**事实**是 `len(unresolved)=40`，与自报一致 ⇒ **那次自纠的方向是对的**（把"38 条"的错误读数推翻），
  落盘前用命令核对并撤回是**正确动作**，`UNRESOLVED.json` 未被篡改（sha256 `225e04bfae95e77b` 与 §8.2 一致）。
- 但我**不能独立证实**"起草期确实出现过 38 这个错误数字" —— 那是一次**未落盘**的过程陈述，
  **只存在于自述中，无第三方可核**。我把它归类为**「已声明的过程陈述，不可独立验证」**，
  而**不是**"已验证的自纠"。这不影响 §1.2/§1.5 的数字正确性结论。
- **对 TL 记录可信度的判断**：在本次复核中我核对过的**每一条可验证陈述**（11 项 sha256、M1/M2/M3 的条数、
  603/22 用例数、`semanticQueries` 为声明值、`SemanticQueryPort` 零装配、12 符号表、KD 诚实缺口、`make check` 写副作用）
  **全部与事实相符**。⇒ **TL 的记录在本轮可核范围内是可信的**；但它对**不可核的过程陈述**（如"起草期写错过"）
  措辞偏"已完成态"，建议今后把这类内容明确标注为"自述、不可独立验证"。

### 3.7 ⚠ 我额外添加的对抗测试：两个**可绕过盲区**（TL 未要求、也未披露）

这三条是我自己设计的注入，**全部通过 import 门禁脚本自身的解析器/检测函数**执行（不写任何文件）：

```bash
$ python3 - <<'PY'
# 用 scripts/gk17_triple_consistency_check.py 的 parse_turtle + detect_* 直接测
baseline D1 = 0
E1 关系实例+RDF:type owl:Class 伪装          D1=0  ⚠ 未被检出（盲区）
E2 关系实例+RDF:type owl:ObjectProperty 伪装  D1=0  ⚠ 未被检出（盲区）
E3 关系实例+纯 T-Box 词表谓词同块              D1=1  已检出
E4 对照组：裸关系实例（应被检出）               D1=1  已检出
baseline D2 = 0   baseline D4 = 0
E5 投影类型用全 IRI（本体无此类）              D2=0 D4=0  ⚠ 未被检出（盲区）
E6 投影类型用裸自定义前缀                     D2=1 D4=0  已检出
E7 悬空引用用全 IRI                        D2=0 D4=1  已检出
E8 悬空引用用裸前缀                         D2=0 D4=1  已检出
PY
```

**盲区 1（D1，severity：中）** —— `is_tbox_statement()`（`:300-315`）只要语句含 `a owl:Class` / `a owl:ObjectProperty` 等
就**整条跳过**。因此把越权实例写成：

```turtle
gits:gk17_evade_e1 a owl:Class ;
  gits:requiresProduct gits:prod_set_001 .
```

**D1 计数仍为 0**（E1/E2 均未被检出）。而这恰恰是 D1 的全部存在意义
（其 docstring 自称"一旦出现在**个体三元组**（谓词被当数据用）⇒ FAIL"）。
⇒ **"本体里出现产品关系实例 = 越权写，必须检出"这一硬约束不是绝对的。**

**盲区 2（D2，severity：中高，因为它是"同一条 RDF 语句的等价写法"）** ——
`detect_projection_types_outside_ontology()`（`:619`）只检查 `o.startswith("gits:")`，
**全 IRI 形式的类型被整段跳过**：

```turtle
@prefix gits: <https://gits.bank.example/ontology/core#> .
gits:gk17_e5 a <https://gits.bank.example/ontology/core#GK17_NO_SUCH_CLASS> .
```

E5 的 `D2=0, D4=0`。**这不是异想天开的变形，而是同一三元组的合法等价写法** ——
合规写法 `<...#Product>` 与越权写法 `<...#GK17_NO_SUCH_CLASS>` **同样被静默放过**。
投影文件今后若改用全 IRI（Turtle 中完全合法，且部分工具链会这么输出），**D2 会整体失效**。

**我不声称这两条已在生产中发生**，也不声称它们使基线 PASS 变成假绿（基线 `products.ttl`/本体**确无**违规，
`vacuity=[]`、4 项计数为 0 均为真）。我声称的是：**D1/D2 的"必须检出"存在**已证实的反例**，
V4 的 ACCEPT 若建立在"该硬约束已被机械保障"之上，须知道这两个反例。**

**建议（非阻塞、留给 W8 或后续 Loop）：**
1. `is_tbox_statement` 不应因 → `owl:Class` 就整条豁免 **产品关系谓词**的实例检查；
   或在豁免前先断言"该语句不含三个受控关系谓词"。
2. `D2` 应把 `<…gits.bank.example/ontology/core#X>` 与 `gits:X` **规范化到同一命名空间再比对**（现有解析器已保留了 IRI 原文）。
3. 把 E1/E2/E5 三条**加进门禁自身的变异自检**（与 D1/D2/D4 探针同列），否则这两条盲区会**再次静默存在**。

---

## 4. TL 越线或夸大之处（逐条）

> 结论：**未发现越界修改**（未动封版制品、未手改 `generated/`、未改 `LOOP.yaml` 门禁命令、未代签 `QA_PASS`、
> 未启用隔离资产）。**发现 1 条"声明与事实不符"、2 条"数据口径/时效性表述过强"、4 条"表述不精确"，共 7 条，均非恶意，但都必须修。**

| # | 性质 | 具体 | 证据 |
|---|---|---|---|
| **1** | **声明与事实不符（须修）** | `ORCHESTRATOR.md:530` 写"本项所有权**显式回归 TL**，**已同步写入 `ROLE_BOARD.yaml`**"。**实际 `ROLE_BOARD.yaml` 中没有这条记录**：`gate_owner.exclusive_paths` **仍然**把 `scripts/gk17_triple_consistency_check.py` 列为 `gate_owner` 独占，全文件仅在 `independent_qa.must_also_do` 里出现"所有权回归"字样（那是**给 QA 的任务**，不是**所有权事实**）。 | `git --no-pager diff loops/GK17-ontology-unified-map/memory/ROLE_BOARD.yaml`（见 §3 引用）；`grep -niE "回归\|ownership\|handover" ROLE_BOARD.yaml` 无命中于 `gate_owner` 段 |
| **2** | **数据口径偏乐观（须修）** | 包 §6 / `NEXT_SESSION.md:98` 用 **"`make check` 22/23"** 作为门禁通过的表头数字。但实测分类为 **`[PASS]=21` / `[FAIL]=1`（readiness）/ `[INCONCLUSIVE]=1`**；`run_gates.py:213` 的 `len(results)-len(failed)` 把 `INCONCLUSIVE` 算进了分子（`INCONCLUSIVE` 不在 `failed=(FAIL,BLOCKED)` 中），**同一行**却写着"（其中 1 项**无法判定**，不计入通过）"。⇒ 分子与括注**自相矛盾**，**真实 PASS = 21/23**。 | `grep -c "^  \[PASS" make-check.log` ⇒ `21`；`[FAIL]`⇒`1`；`[INCONCLUSIVE]`⇒`1`；`[`总⇒`23`；`run_gates.py:200-214` |
| **3** | **披露位置不当（须修）** | `KD-CORP-RM-PREVISIT` / `KD-CORP-RM-RECON` 属 `NOT_COUNTED_AS_PASS_ASSERTION`（门禁**自己**打印 `HONEST GAP [domain]`）。该事实**只**出现在 `NEXT_SESSION.md:110`，**未进包 §2/§3 的 V3 判定清单**。⇒ 只读包（例如只读 §4 回答问答的签署人）**看不到它**。 | `python3 scripts/gk17_ref_anchor_check.py --root .` 的 `HONEST GAP [domain]` 段 |
| **4** | **表述不精确（低）** | §7 非声明："TL **未**修改 … `Makefile` …"。但工作区 `Makefile` **确实是 dirty**（新增 `index-status` / `index-gate-tests` 并写入 `verify`）。**经查该 diff 与 GK17 无关**（属 `GOV-CFI-001` 代码事实索引规则的落地，另一执行者的并发改动），且 GK17 的两道门禁**确实未登记进 `run_gates.py`**（与 `LOOP.yaml:96` 的说明一致）。⇒ **不是越线**，但"未修改 Makefile"这句在**读起来像全局事实**时是错的，应限定为"未修改 GK17 相关门禁构成"。 | `git --no-pager diff Makefile` |
| **5** | **度量口径未解释（低）** | `gate_injection_tests` 自报 **"门禁认领 25/23"**：注入器覆盖 25 个门禁，而 `run_gates.py` 只有 23 个。差值 = GK17 的 `gk17-ref-anchor` / `gk17-triple-consistency`（未登记进 `run_gates`）。**可解释、非缺陷**，但与"22/23"和 §6 的"23"是**三套分母**，W8 收口（必办④）时应对齐。 | `make-check.log` 第 5 行 |
| **6** | **清单字面与实测不逐字对应（极低）** | 包 §3 V3「判据字面形状」点名 `fake_assetRef ⇒ ASSET-DOES-NOT-EXIST-GK17 …`；实测 selftest 打的 ID 是 `ASSET-DOMAIN-PROBE-GK17`（同 code/同字段/同机制）。不影响结论，但"字面形状"一词会让人期待逐字匹配。 | `--selftest` 原始输出 |

| **7** | ⚠ **时效性表述过强（须修，影响 W8 阻塞理由）** | `NEXT_SESSION.md:105` / 包 §6 / 裁定 §4.1 把 `backend_test` 写成"OWASP **端点不可达** ⇒ 模块 SKIPPED"。**该表述对机制是对的，对"不可达"这个词是错的**：**本 Loop 自己的 evidence 目录里就存在一次 SUCCESS**。同一天 08:23 的 `backend_test-20260915T002338Z.log` 是 **BUILD SUCCESS**、**0 个模块 SKIPPED**、**dependency-check 完整执行**（`--- dependency-check:12.1.0:check (default)`、`Analysis Complete (1 seconds)`、写出 `dependency-check-report.html`、suppression 规则参与匹配）；而 11:55 的 `backend_test-20260915T035533Z.log` 才因 RetireJS `Read timed out` 整体 FAILURE。⇒ **这是间歇性/网络抖动，不是确定性的环境不可达。** | 见下方"我的独立复现" |

**我的独立复现（端点级，不是转述 TL 日志）：**

```bash
# ① 我自己测端点 —— 与 TL 的机制声明一致
$ curl -sS -o /dev/null -w "%{http_code}" <各端点>
  TIMEOUT/ERR  <- https://raw.githubusercontent.com/RetireJS/retire.js/master/repository/jsrepository.json
  200          <- https://services.nvd.nist.gov/rest/json/cves/2.0?resultsPerPage=1
  200          <- https://repo1.maven.org/maven2/
  200          <- https://registry.npmjs.org/
# ② 本 Loop 自己的证据里那次红的确切根因（原始行）
$ grep -n "RetireJS\|UpdateException\|SKIPPED" backend_test-20260915T035533Z.log
176:[WARNING] Unable to update 1 or more Cached Web DataSource, using local data instead. …
177:[ERROR] Unable to continue dependency-check analysis.
182-195: operational-ontology … gits-kno-worker  全部 SKIPPED（15/15）
197:[INFO] BUILD FAILURE
203:[ERROR]   UpdateException: Failed to initialize the RetireJS repo
204:[ERROR]     caused by DownloadFailedException: Download failed, unable to copy
             'https://raw.githubusercontent.com/Retirejs/retire.js/master/repository/jsrepository.json' …
             Read timed out
206:[ERROR]   NoDataException: No documents exist
# ③ 同环境另一次：完整跑通
$ grep -E "Analysis Complete|BUILD" backend_test-20260915T002338Z.log
34:[INFO] --- dependency-check:12.1.0:check (default) @ gits-knowledge-engineering ---
84:[INFO] Analysis Complete (1 seconds)
85:[INFO] Writing HTML report to: /home/szf/dev/gits-cbanking/target/dependency-check-report.html
[INFO] BUILD SUCCESS      # 15 模块 0 SKIPPED
```

⇒ **我确认"红是环境引起的"这一归因（机制、根因、原始报错都对），但"端点不可达"应修正为"RetireJS 端点**间歇性**超时"。
后果（必须让 Owner 看到）**：W8 的阻塞理由③"环境红阻塞 `exit_criteria.dev`"**比呈现的弱** ——
本环境**已存在一次 `backend_test` 全绿的可复现证据**（08:23）。
⇒ **建议**：W8 收口前对 `backend_test` 做**一次带重试/预热缓存的重跑**再定性；
若届时全绿，则"另立 GK18 拆门禁"（裁定 §4.2）的必要性下降，`ENVIRONMENT_LIMITATION` 的定性也应改为"**间歇性**"。
**结论不变**：即使它某次真绿，**本次会话我仍未跑它**，**它不得被计为通过**。

**关于 Tick 16 → Tick 17 的自我更正（§7 与 §8.1 的矛盾）：**
- `ORCHESTRATOR.md:509`（Tick 16）写"TL **未**修改 `gate_owner` 独占的门禁脚本"；
  `:521-530`（Tick 17）**显式承认相反**并给出理由。**包 §8.1 也主动标了"该说法已不成立"。**
  ⇒ **这不是隐瞒，是本 Loop 做对的一件事**（我叫它"登记了与上轮声明相反的事实"）。
  但由第 1 条可知：**它把回归写进了叙述，没写进 `ROLE_BOARD`** —— 即"声明完成度 > 落盘完成度"。

**关于未越界的核对（正面结论）：**
```bash
$ git status --short generated/ ; git status --short specs/ ; git status --short docs/dd/gk-ke-contract/
（三条均无输出 = 未改）
$ git rev-parse HEAD:docs/dd/gk-ke-contract
4c5f5373c83386d27ea996293a49ee7f3b9f10ce        # = 封版 tree，与 GK-KE 记忆一致
$ git --no-pager diff --stat loops/GK17-ontology-unified-map/LOOP.yaml
（空 = LOOP.yaml 未改，符合 §7）
$ grep -rn "QA_PASS" loops/GK17-ontology-unified-map/   # 全部命中均为"不是 QA_PASS"的否定式声明
（无任何代签）
$ git --no-pager diff loops/GK17-ontology-unified-map/EVIDENCE.json   # 仅两条 Tick-17 重落证的时间戳/哈希更新，
（**未**新增 gk17_v1_v4_experiments 记录 ⇒ §7 该声明属实）
```

---

## 5. 整体判定建议 + 我必须声明的未验证范围

### 5.1 W2 的判定建议

> **建议：ACCEPT_WITH_CONDITIONS（技术面已可复核，条件为门禁数字口径修正）。**

| 判据 | 我的判定 | 关键依据（我跑出来的） |
|---|---|---|
| W2-1 本体依据写入 plan trace | **通过** | `trace.ontologyEvidence` 含 `CTR-SEM-002@sha256:705578d6324abd0c [classes=32,objectProperties=34,datatypeProperties=1,individuals=0,source=…]`（我的独立复跑产物） |
| W2-2 本体不可达 ⇒ fail-closed | **通过** | M1 注入 ⇒ FAIL **恰好 2 条**，命中 `deniesWhenOntologyMissing…` / `deniesWhenOntologyMalformed…` |
| W2-3 `versions.ontology` 非占位串 | **通过** | `git grep CURRENT_BASE` 全仓 **1 命中**，位于 `OntologyPort.java:10` 的 **javadoc 历史说明**；生效代码/合同/黄金 **零命中**。且我证实该取值 = 本体文件内容 sha256 |
| W2-4 负例通过且非空转 | **通过** | M1 ⇒ FAIL 2；M2 ⇒ FAIL(模块 1 + E2E 1)；M3 ⇒ FAIL 1；三者还原后均回 PASS，源码 sha256 复原 |
| W2-5 门禁 | **通过（附限定）** | `make generate` exit 0 且**幂等**（`generated/` 逐字节未变）+ 非空转注入已证；`make check` exit 0、`integrity_failed=[]`；`ontology_load` **1/0/0/0**；`./mvnw test` **api 603/0/0/4、worker 22/0/0/0、15 模块 SUCCESS**。⚠ 但"22/23"应读作 **21/23 真 PASS + 1 INCONCLUSIVE + 1 READINESS NOT MET** |
| W2 设计裁定①② | **均通过** | ① 代码位置与声明一致（`:111-119` 在 `:92-109` 之后、`:123` 之前）；② 我在**跨真实绝对路径**的两处来源下复现：`evidence` 不同、`planHash` 同为 `a2413b72e01d7430` |

### 5.2 W6 的判定建议

> **建议：不 ACCEPT（就"V1 完整链"这一条判据字面而言），或 ACCEPT_WITH_SCOPE_REDUCTION（由 Owner 裁定范围）。**
> **其余 V2/V3/V4 的机制面我判定通过，但每一条都带我上述的强制限定。**

| 判据 | 我的判定 | 一句话理由 |
|---|---|---|
| V1 完整链 | **不通过**（② 未执行） | `SemanticQueryPort` 在 `apps/api/src/main` **零命中**；`individuals=0`；计划里的 5 条查询是**合同声明值**不是查询结果。①③④⑤ 通过，**② 未达成** |
| V2 只改本体 ⇒ 计划必变 | **通过（机制）/ 语义未驱动为强制性限定** | M3 证明该边非空转；但版本=内容 sha256 ⇒ 任何字节变动都会改 `planHash`，**该判据对"语义消费"零约束力** |
| V3 引用不存在 ⇒ 拒绝 | **通过（引用锚定机制）/ 对"A-Box 个体"无法判定** | 6 变异自检全过；但锚定空间不含 A-Box；且 `KD-*` 中 **2/3 为 `NOT_COUNTED_AS_PASS_ASSERTION`** |
| V4 手工不一致 ⇒ 检出 | **通过** | D1 变异被捕获（行号 `gits-core.owl.ttl:367`）；D2/D4 专门探针存在且**我独立复现"破坏判定 ⇒ 必转红"**；注入矩阵 20/20 被检出。⚠ **但我另找到 D1/D2 各一条可绕过盲区（§3.7）**，V4 的"必须检出"**不是绝对的** |

### 5.3 我必须声明的**未验证范围**（不得被读作已验证）

1. **我未验证** A-Box 实体/关系查询 —— 无输入、无执行器（Q1）。
2. **我未验证** 真实 dsh/KERT 平台接通 —— SKILL 走的是 `FallbackSkillExecutionAdapter` + `MockLlmClient`（Q2）。
3. **我未验证** 本体语义驱动计划选择 —— 该能力在当前代码中**不存在**（Q3）。
4. **我未验证** `KD-CORP-RM-PREVISIT` / `KD-CORP-RM-RECON` 的锚定 —— 门禁口径为 `NOT_COUNTED_AS_PASS_ASSERTION`（Q4）。
5. **我未验证** `gk17_prodcard_projection` 门禁 —— 其输入源 `Leibniz-KERT/examples/product-recommendation-assets/03_core` **在工作区外**；
   我只核对了它的**产物**（`products.ttl`、`UNRESOLVED.json` 的 sha256 与内容），**未重跑该门禁**。
6. **我未验证** `frontend_test` —— 环境红（沙箱 `npm ci` 守卫）。**未计为通过，也未为它改门禁。**
7. **我未跑 `make backend-test`** —— 我改用 `./mvnw test` 验证测试面（§0.1 允许），**未计为通过**。
   但注意 §4 第 7 条：其"环境红"的性质经我核实为 **RetireJS 端点间歇性超时**，
   且本 Loop 证据中存在一次 **BUILD SUCCESS + dependency-check 完整执行** 的运行记录。
8. **`gate-injection-tests` 总判定 `INCONCLUSIVE` 未计为通过**；其中 GK17 两道门禁在 OK 列表**是**检出成功的（可计）。
9. **我未验证** `make security-check`、`make gk_ke_gates` 的**内部**归因（只经 `make check` 看到其分类结果）。
10. **我未验证**"起草期曾把 40 记成 38"这一**过程陈述**（§3.6，不可独立验证）。
11. **我未做 OWL 推理层面的验证**（未用 reasoner 检查本体一致性/可满足性）—— 我的盲区测试是**静态文本层面**的。
12. **我未验证 TL 之外的其他执行者在本工作区的并发改动**（`Makefile`、`AGENTS.md`、`.codebuddy/rules/`、`diagrams/` 等）；它们不在本 Loop 判定范围内。

### 5.4 收尾声明

```text
[能力自检]   有完整 shell / python3 / java21 / ./mvnw / git(只读) / curl；execute_command 调用 51 次
             所有"通过"均来自我自己跑出的标准输出；无能力验证项已在 §0.0.3 与 §5.3 标注"未复核"
[判定建议] GK17 W2  : ACCEPT_WITH_CONDITIONS（真 PASS 应为 21/23，非 22/23；须修 §4-1/§4-2）
[判定建议] GK17 W6  : 不予 ACCEPT（V1 ② 未执行）/ 或由 Owner 裁定缩减范围的 ACCEPT
[所有权表态] gate_owner → TL 的回归：有条件接受（条件见 §2 Q5 第 5 条）
[对抗结论]   D1 / D2 各存在一条已证实的绕过盲区（§3.7），须在 W8 或后续 Loop 补负例
[新增修正]   backend_test 的"环境红"实为 **RetireJS 端点间歇性超时**；本 Loop 证据内存在一次
             BUILD SUCCESS + dependency-check 完整执行的运行（§4-7）⇒ W8 阻塞理由③需重新定性
[独立性]     授权下的降级独立；本文件**不是** QA_PASS；**不代签**；签署权在 Owner
```

**未做任何 git 写操作；未修改除本文件与临时目录外的任何文件；临时目录 `.tmp-qa-independent-qa/` 已按约定清理。**
