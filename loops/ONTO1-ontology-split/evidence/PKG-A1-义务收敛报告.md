# ONTO1 PKG-A1｜候选义务三层收敛报告（WI-A2 §4 义务回源确认）

| 项 | 值 |
|---|---|
| 性质 | 只读分析（W-1.5 就绪加固）；不改 `specs/**`/`generated/**`/`docs/dd/**`；KERT 仓只读 |
| 输入 | `loops/ONTO1-ontology-split/evidence/consumer-scan-obligations.csv`（1052 行） + `consumer-scan-hits.jsonl` |
| 复现 | `python3 scripts/onto1_obligation_triage.py --report` → `--gate` → `--selftest` |
| 机读产出 | `obligation-triage.csv`、`obligation-triage-summary.json` |
| 生成时间 | 2026-09-20T16:08:41+00:00 |

## 1. 收敛结果（对账闭合）

| 判定 | 行数 | 占 1052 | 含义 |
|---|---|---|---|
| `TRUE_OBLIGATION`（真义务） | 691 | 65.7% | 强信号：本体 IRI/OWL/SPARQL 语句，或已确认消费面 → 必须跟随迁移 |
| `HOMONYM_CANDIDATE`（同名候选） | 0 | 0.0% | 弱信号面裸术语 + 同名机械证明（H1/H2/H3）→ 不计义务（**≠ 已排除**） |
| `NEEDS_SOURCE_CHECK`（待回源） | 361 | 34.3% | 中信号 / 弱面无证明 → Wave 2 逐条回源，本行不计义务也不算已排除 |
| **合计** | 1052 | 100.0% | 基线 1052；闭合 = True（delta 0） |


分层信号：STRONG 626 / WEAK 97 / MEDIUM 329。

## 2. 方法与三层规则（与脚本规则表一一对应）

- **强信号 ⇒ 真义务**：文件含本体 IRI 字面量（`gientech.com/gits/kno/`、`gits.bank.example/ontology/core#`）、`owl:imports`/`owl:`/`rdf:`/`rdfs:` 语句、`@prefix`/SPARQL `PREFIX`/`SELECT…WHERE`、`gits-core`、`versions.ontology`、`planHash`；**或**路径落已确认消费面（`modules/{operational-ontology,knowledge-architecture,scenario-customer-journey}`、`adapters/{semantic-jena,knowledge-filesystem}`、`specs/{semantic,knowledge-architecture,gk-ke}`、`specs/CONTRACT_INDEX.yaml`、`apps/api`（本体端口/规划器相关）、KERT `src/kert` 与 `examples/bank-front-knowledge-maps/90_control`）。
- **弱信号 ⇒ 同名候选**：只出现**裸术语名**（class/object property/data property）且位于 DTO/UI/测试/日志/持久化面；**必须**有同名机械证明 —— H1 库列 `snake_case` 形态 / H2 按简单名从 `dto|contract|api|model` 包导入该术语（且同文件**无**本体/领域包同名或通配导入 ⇒ 命名解析唯一）/ H3 前端 `import type { X } from '.../api/...'`；无证明一律降级为待回源。
- **中信号 ⇒ 待回源**：其余（`specs/*` 其余、`scripts/*`、`scenario/*`、KERT `examples|skills` 其余）。

### 2.1 口径声明（**请 TL 重点审计**）

- I-1 弱信号面并入本仓惯用的 **/src/test/** 与 **/dto/**（派工单列举之外，signal 中标 rule id）
- I-2 HOMONYM 需机械证明 H1/H2/H3，且要求命名解析唯一（同文件出现本体/领域包同名导入或通配导入 ⇒ 禁判同名）；无证明落 NEEDS_SOURCE_CHECK
- I-3 id_pattern（CTR-/KM-/AC-/ASSET-/SP-/KI-/KD-）不算裸术语名，弱面带 ID 命中落 NEEDS
- I-4 TRUE_OBLIGATION = 必须跟随迁移，不等于已确认本体消费；Wave 2 回源可推翻
- I-5 刻意不收「文件自述该名来自 OpenAPI 合同」作为同名证明（如 api/dto/ClaimResponse.java:9 同段又写『本 DTO 同时携带两种语义字段』）
- I-6 待回源行再分 P0（裸名精确解析到本体/领域模型包）/ P1（其余）两档；**TL 已裁定 P0 升格为 TRUE_OBLIGATION + W3_CONSUMER_SWITCH**（机械证据 = 精确 import 行；开关 RULING_I6_UPGRADE_P0 可回退；原 626/426 口径作为对照保留）

> 替代口径计数：若按「tier=WEAK 即判同名」，则同名 = 68、待回源 = 293。本 CSV 采用更保守的『需机械证明』口径。

## 3. 真义务清单（按责任 Wave 归类）

逐文件完整清单见 `obligation-triage.csv`（`disposition=TRUE_OBLIGATION`）。先看**依据强度**（回源抽检应优先抽「仅路径依据」那一档）：

| 依据强度 | 行数 | 含义 |
|---|---|---|
| 内容级证据（IRI/OWL/SPARQL/planHash…） | 156 | 文件正文含本体 IRI / OWL / SPARQL / gits-core / planHash 等语义层语句 ⇒ 依据最强（每条证据行由 G4 逐行回源复核） |
| 仅路径依据（已确认消费面） | 470 | 仅在「已确认消费面」路径内命中术语，依据是路径规则（派工单口径）⇒ **回源可推翻**，是 Wave 2 抽检的首选对象 |


真义务按信号规则分布：

| 信号规则 | 行数 |
|---|---|
| `STRONG_PATH:R-STRONG-PATH-SPEC-KNOWLEDGE-ARCH` | 135 |
| `STRONG_PATH:R-STRONG-PATH-SPEC-GK-KE` | 110 |
| `STRONG_PATH:R-STRONG-PATH-MODULE-OPERATIONAL-ONTOLOGY` | 80 |
| `STRONG_PATH:R-STRONG-PATH-KERT-SRC` | 38 |
| `MEDIUM_PATH` | 36 |
| `STRONG_CONTENT:FILE_GITS_CORE` | 33 |
| `STRONG_CONTENT:IRI_GIENTECH` | 31 |
| `STRONG_CONTENT:PLAN_HASH` | 30 |
| `STRONG_PATH:R-STRONG-PATH-ADAPTER-KNOWLEDGE-FS` | 28 |
| `STRONG_PATH:R-STRONG-PATH-MODULE-KNOWLEDGE-ARCH` | 26 |
| `WEAK_PATH:R-WEAK-PATH-EXT-SRC-TEST` | 26 |
| `STRONG_PATH:R-STRONG-PATH-MODULE-SCENARIO-JOURNEY` | 20 |
| `STRONG_CONTENT:SPARQL_QUERY` | 18 |
| `STRONG_PATH:R-STRONG-PATH-APPS-API-PORT-OR-PLANNER` | 17 |
| `STRONG_CONTENT:TTL_PREFIX` | 16 |
| `STRONG_CONTENT:VERSIONS_ONTOLOGY` | 16 |
| `STRONG_PATH:R-STRONG-PATH-KERT-90-CONTROL` | 16 |
| `STRONG_CONTENT:IRI_BANK_EXAMPLE` | 7 |
| `STRONG_CONTENT:OWL_STATEMENT` | 5 |
| `WEAK_PATH:R-WEAK-PATH-EXT-DTO` | 3 |


下表为 Wave × 目录聚合。

### W2_SPLIT（Wave 2 四层拆分 / 合同先行）— 291 行

| 目录（前 3 段） | 行数 |
|---|---|
| gits:specs/gk-ke/v1 | 114 |
| gits:specs/knowledge-architecture/elements | 40 |
| gits:specs/knowledge-architecture/assets | 32 |
| gits:specs/knowledge-architecture/registry | 18 |
| gits:specs/knowledge-architecture/capabilities | 11 |
| gits:specs/knowledge-architecture/schemas | 10 |
| gits:specs/knowledge-architecture/activation | 8 |
| gits:specs/knowledge-architecture/maps | 8 |
| gits:specs/knowledge-architecture/activations | 7 |
| gits:specs/knowledge-architecture/skills | 5 |
| gits:specs/CONTRACT_INDEX.yaml | 3 |
| gits:specs/data/customer-source-mapping.r2rml.ttl | 3 |
| gits:specs/knowledge-architecture/contracts | 3 |
| gits:specs/knowledge-architecture/tests | 3 |
| gits:specs/openapi/gk-ke-v1.openapi.json | 3 |


### W3_CONSUMER_SWITCH（Wave 3 双侧换消费 / 原子窗口）— 381 行

| 目录（前 3 段） | 行数 |
|---|---|
| gits:apps/api/src | 95 |
| gits:modules/operational-ontology/src | 80 |
| gits:modules/knowledge-architecture/src | 33 |
| gits:adapters/knowledge-filesystem/src | 30 |
| kert:src/kert/application | 27 |
| gits:modules/scenario-customer-journey/src | 20 |
| kert:examples/bank-front-knowledge-maps/90_control | 14 |
| kert:src/kert/domain | 14 |
| gits:adapters/semantic-jena/src | 6 |
| gits:modules/semantic-runtime/src | 5 |
| kert:src/kert/infrastructure | 5 |
| gits:apps/worker/src | 4 |
| gits:modules/context-evidence/src | 4 |
| gits:scripts/gate_injection_tests.py | 4 |
| gits:scripts/gk17_ref_anchor_check.py | 4 |


### W3_KERT_ASSETS（Wave 3 KERT 知识资产换版）— 19 行

| 目录（前 3 段） | 行数 |
|---|---|
| kert:examples/bank-front-knowledge-maps/90_control | 19 |


## 4. 同名候选（全部列出，附机械证明与回源证据）

本轮**无**满足机械证明的同名候选行。

这不是「没有同名」，而是「**没有一条弱面命中能达到可证明的唯一解析**」：WI-A2 扫描已把可判同名的 2690 处路由到 `HOMONYM_REQUIRES_SOURCE_CHECK`（未进入净义务 1052 行）；净义务里剩下的弱面命中（本仓惯用测试/DTO 面）大多与本体包**同文件共存**，例如 `apps/api/src/test/.../HumanGateControllerTest.java:8` 同时 `import com.gien.gits.ontology.*;`，裸名解析不唯一 ⇒ 只能落待回源。

**同名候选 ≠ 已排除**：它们只是「不计入迁移义务」，Wave 2 逐条回源仍可推翻。

## 5. 待回源项与处置建议

待回源共 361 行，按「回源只需一步确认」程度再分两档：

| 优先级档 | 行数 | 含义 |
|---|---|---|
| **P0** 裸名精确解析到本体/领域模型包 | 65 | `import <本体/领域包>.<Term>;` 精确命中（Java 模型层耦合）⇒ 只需确认该类是否随四层拆分改名/换 IRI |
| **P1** 其余待回源 | 361 | 无本体包解析证据、也无同名证明 ⇒ 需逐条读判用法 |


> **P0 是优先级信号，不是判定**：本引擎刻意不据此直接判 `TRUE_OBLIGATION`（派工单强信号清单未含此形态；是否升级由 TL 裁定）。P0 行按包分布：

| 本体/领域模型包 | 行数 |
|---|---|
| `com.gien.gits.ontology` | 55 |
| `com.gien.gits.action.domain` | 6 |
| `com.gien.gits.ontology.domain` | 4 |


P0 样例（回源起点）：

| 证据（`文件:行`） |
|---|
| `gits:apps/api/src/main/java/com/gien/gits/api/controller/ClaimController.java:15` |
| `gits:apps/api/src/main/java/com/gien/gits/api/controller/CommitmentController.java:5` |
| `gits:apps/api/src/main/java/com/gien/gits/api/controller/CustomerContextController.java:9` |
| `gits:apps/api/src/main/java/com/gien/gits/api/controller/EngagementClaimController.java:6` |
| `gits:apps/api/src/main/java/com/gien/gits/api/controller/EngagementJourneyController.java:21` |
| `gits:apps/api/src/main/java/com/gien/gits/api/controller/EvaluationController.java:16` |


待回源行按目录分布（全量，前 20）：

| 目录（前 3 段） | 待回源行数 |
|---|---|
| gits:apps/api/src | 134 |
| gits:scenario/execute/src | 36 |
| kert:examples/product-recommendation-assets/03_core | 9 |
| kert:examples/bank-front-skills/bank-front-report-assembler | 7 |
| kert:examples/bank-front-skills/bank-front-supply-chain-graph | 7 |
| kert:examples/gits_adapter/curl | 7 |
| kert:examples/bank-front-skills/bank-front-commitment-script | 6 |
| kert:examples/bank-front-skills/bank-front-fact-reconciliation | 6 |
| gits:modules/human-action/src | 5 |
| kert:examples/bank-front-skills/bank-front-kyc-gap-check | 5 |
| kert:examples/bank-front-skills/bank-front-product-recommendation | 5 |
| kert:skills/product-recommendation/rules | 5 |
| kert:skills/service-proposal/templates | 5 |
| kert:skills/product-recommendation/contracts | 4 |
| kert:skills/service-proposal/industry-frameworks | 4 |
| gits:modules/context-evidence/src | 3 |
| gits:modules/evaluation/src | 3 |
| gits:scripts/hermes_to_seed.py | 3 |
| gits:specs/openapi/product-recommendation.openapi.json | 3 |
| kert:examples/gits_adapter/README.md | 3 |


处置建议（**次序 = 回源 ROI**）：

1. **P0 行（本体包耦合）**：先回源这一档，多数只需确认 `com.gien.gits.ontology.*` 的 Java 模型类是否随四层拆分改名/换 IRI ⇒ 可批量定论（这批是本轮最有信息量的发现）。
2. `apps/api/src` 其余非本体端口文件（控制器/DTO/service）：逐条读判该术语是「本体类/属性消费」还是「Java 领域模型同名」；判据同 WI-A2 报告 §4 抽样 2（类型来源是 API 合同还是本体）。
3. `scripts/*`：门禁/生成器脚本内的术语多为**字面量断言**，按「是否驱动受控制品」逐条判定。
4. `specs/*` 其余（`openapi`/`data`/`product-recommendation`/`actions`/`evidence`）：按合同登记关系判定（是否将被本体拆分引用的 schema/字段）。
5. KERT `examples/*`、`skills/*`：按 L2 元模型消费面判定（需 KERT 侧回源，`INDEX_STALE(144)`）。

## 6. 门禁与变异复验

- 门禁：`python3 scripts/onto1_obligation_triage.py --gate`（G1 输入锚定/ G2 对账闭合/ G3 强信号面 100% 有判定 / G4 证据可回源 / G5 弱面反一刀切 / G6 Wave 合法性 / G7 产物与复算一致 / G8 无占位）。
- 变异复验：`--selftest` M0 对照 / M1 强信号注入必须检出 / M2 弱面真义务（无证据与有证据）必须 FAIL / M3 删强信号判定必须 FAIL / M4 真值函数短路必须 FAIL / M5 输入缺失必须 FAIL / M6 证据不可回源必须 FAIL / M8 本体包通配导入存在时禁判同名 / **M9 本体包耦合 ⇒ 升格真义务(W3) + 机械证据双标签** / **M9b-1 开关回退 ⇒ 回落 NEEDS（回退有效）/ M9b-2 剥掉 `PROOF:IMPORT_LINE` ⇒ 弱面 G5 必须 FAIL / M9b-3 全部 P0 行包名改为不存在 ⇒ 逐行 G5 命中数须 == 行数（覆盖全 tier）**（D-12 反例）。逐条输出见 HANDOFF 与 TL 记账日志。

## 7. 诚实声明（**不得援引为已完成的事**）

1. 本报告**不声称**消费者影响分析已关闭：它把 1052 行压到三层，**待回源的 361 行仍未确认**，既不能当义务执行、也不得算已排除；
2. `TRUE_OBLIGATION` 是「必须跟随迁移」的**判定**，不是「已确认本体消费」的**结论**（Wave 2 回源可推翻，尤其强路径面内的裸术语命中）；
3. 弱信号面的同名判定是**候选**：证明只到「该名在此文件解析到 API 合同/库列」这一层，不等于该文件与本体毫无关系；本轮该档为 0 行，**不等于**「净义务里没有同名」——只是没有一条达到可证明的唯一解析（详见 §4）；
4. 第 5 节的 P0/P1 是**回源优先级**，不是判定；P0（65 行）是否升级为真义务 **由 TL 裁定**，本引擎不自行升格（口径 I-6）；
5. 本报告**未**执行 `make generate`、**未**改 `specs/**`/`generated/**`/`docs/dd/**`、**未**写 KERT 仓、**未**签任何门禁（登记由 TL 执行）；
6. KERT 侧结论一律回源到 `文件:行`（`INDEX_STALE(144)`，不得据索引外推）。
7. `TRUE_OBLIGATION` 里只有内容级证据那一档（156 行）是「文件正文自证」；其余 470 行依据是路径规则，Wave 2 应优先抽检。

> **风险提示**：真义务 691 行 > `PLAN-NEXT.md` §1 A1 的 400 行阈值 ⇒ 触发「立即回写 `evidence/WBS-RESTIMATE.md` 并在 `ORCHESTRATOR.md §5` 新增风险项」条款（本文件写域外，建议由 TL 执行）。

## 8. 与 WI-A2 扫描报告的关系

- 输入锚点：`loops/ONTO1-ontology-split/evidence/WI-A2-消费者扫描报告.md` §3（1038 FOLLOW_MIGRATION + 14 CONTROL_PLANE_REQUIRED）；
- 本报告不替代 §3 清单，而是给它加**第三维（判定 + 证据）**；扫描报告的 §4 诚实性声明继续有效；
- 扫描报告 §4 已完成 3 类抽样证伪（`customerId` 库列 / 前端 `Customer` DTO / `AC-004` 号段）；本轮把前两类**机器化为全量规则**（H1 库列 snake_case / H3 前端 SDK 类型导入），实测**在 1052 行净义务内零命中** —— 因为这三类命中在扫描阶段已被路由到 `HOMONYM_REQUIRES_SOURCE_CHECK`（2690 处）与 `EXEMPT_NON_ONTOLOGY_HOMONYM`，**未进入净义务**。这反过来解释了「同名候选 = 0」：净义务集合的构成本身已不含可机械证明的同名形态。
