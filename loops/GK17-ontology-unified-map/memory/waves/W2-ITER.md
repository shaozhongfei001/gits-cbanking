# W2｜ITER 记录

## ITER 1｜WP2.1 `OntologyPort` + Jena 实现（2026-09-15）

### 产出

| 文件 | 内容 |
|---|---|
| `modules/semantic-runtime/.../semantic/OntologyPort.java` | 端口 + `OntologyLoadResult`（成功/两种失败态）+ `OntologySnapshot`（含 `evidence()`） |
| `adapters/semantic-jena/.../jena/JenaOntologyAdapter.java` | Jena 实现：读真实文件、按内容算版本、按实体计数 |
| `adapters/semantic-jena/src/test/.../JenaOntologyAdapterTest.java` | 7 个用例（含**防空转**断言与失败态） |

### 设计要点（**fail-closed，且不静默降级**）

- **不抛异常**，把失败**显式返回**，由调用方据此拒绝：
  - 文件不可达 / 读不到 → `CODE_MISSING`
  - 空文件 / 语法错 / 解析成功但模型为空 → `CODE_MALFORMED`
- **版本由内容 SHA-256 派生**：`<contractRef>@sha256:<16hex>`
  ⇒ 本体内容一变版本即变 —— 这是判据 **V2** 能被机械保障的前提；
- T-Box/A-Box 判定**复用 Jena 词汇表**（`owl:Class` / `ObjectProperty` / `DatatypeProperty`），
  与本体写法一致，**未另立第二套判定**；SHACL 校验**仍归** `JenaSemanticRepositoryAdapter`，本类不重复实现；
- `OntologySnapshot.evidence()` 输出**可复核的一行依据**
  （版本 + 四类计数 + 来源），而不是"已加载"这种空话。

### 验证（防空转是重点）

```
Tests run: 7, Failures: 0, Errors: 0, Skipped: 0
```

7 个用例**全部真实执行**（已核对 surefire 报告里的用例明细，不是"没跑也算过"）：

| 用例 | 断言 |
|---|---|
| `loadsRealOntologyWithMeasuredCounts` | **读真实 `specs/semantic/gits-core.owl.ttl`，读数必须等于实测基线 32 / 34 / 1 / 0** ⇒ 解析若静默失效会**当场失败**，不靠夹具缺失"通过" |
| `loadsSmallOntologyAndCountsEntities` | 内联本体：2 类 / 1 对象属性 / 1 数据类型属性 / 1 个体（`a owl:Ontology` 等 schema 声明**不计**为个体） |
| `missingFileIsFailClosedNotSilent` | 不可达 ⇒ `CODE_MISSING`，且失败原因**含文件名** |
| `nullPathIsFailClosed` | null 路径 ⇒ `CODE_MISSING`（不 NPE） |
| `emptyFileIsMalformedNotMissingAndNotLoaded` | 空文件 ⇒ `CODE_MALFORMED`，**不得**判为加载成功 |
| `unparseableTurtleIsFailClosedNotCrash` | 语法错 ⇒ `CODE_MALFORMED`，**不抛栈**（抛栈只证明无输入防御，不证明有判定） |
| `versionIsDeterministicForSameContentAndChangesWithContent` | 同内容 ⇒ **同版本**（可重放）；内容变 ⇒ **版本必变**（V2 依赖此性质） |

### 未完成

- **WP2.2**：把 `OntologyPort` 接进 `DefaultActivationPlanner`，使 `versions.ontology` 为真实值、
  裁决带本体依据写入 plan trace、**本体不可达 ⇒ `PlanDecision.Deny`（fail-closed）**；
- **WP2.3**：`deterministicContent()` 纳入本体版本（`planHash` 因此对本体内容敏感）；
- **黄金用例更新**：`AP-PREVISIT-GOLDEN.json` / `AP-FACT-RECON-GOLDEN.json` 的 `versions.ontology`
  需从占位串改为真实值（**合同先行**：先改黄金，再改实现，再跑门禁）；
- **依赖边**：`modules/knowledge-architecture` 目前**零依赖**（只定义自己的端口）；
  接线后需要新增 `knowledge-architecture → semantic-runtime` 一条依赖（无环）。

### 非声明

- 本 ITER **不**声称"本体已进入路由" —— 端口与适配器已就绪，但**规划器尚未消费它**（WP2.2）；
- 本 ITER **未**改动任何既有文件（纯新增），故未触及其他模块；
- 本 ITER **未**修改 `specs/`（黄金用例的改动属 WP2.3，走合同先行）。

---

## ITER 1｜门禁结果（2026-09-15）

| 门禁 | 结果 |
|---|---|
| `backend_test` | **FAIL（exit 2）** —— 见 `FAILURES.md`，根因 **OWASP `dependency-check` 需联网拉 RetireJS 而该端点不可达**，`gits-kno-api`/`gits-kno-worker` **被 SKIPPED（测试根本没跑）** |

**分离验证（关键）**：`make backend-test` 的第一步是 `./mvnw verify`，而 `dependency-check` 绑在 `verify`。
改用 **`./mvnw test`**（不触发 `verify`）单独验证测试面 ⇒ **BUILD SUCCESS，全模块测试通过**
（api `600/0/0/4`、另一模块 `52/0/0/0`、worker `22/0/0/0`），含本 ITER 新增的
`JenaOntologyAdapterTest`（`7/0/0/0`）。

⇒ **结论：WP2.1 未破坏任何测试；`backend_test` 的红完全来自外部网络。**
**该红仍记为 FAIL，不转为通过。**

### 附带 finding（交 W8 提治理）

`make backend-test` 把"单元测试"与"**联网拉取 OWASP 漏洞库**"耦合在同一入口
⇒ 网络抖动即可让门禁变红，且红时模块是 SKIPPED 的（**这个红读不出任何代码信息**）。
与本 Loop 在 W5 学到的教训同族：**会因外部原因变红的门禁容易被当噪音忽略**。
建议三选一（**不单方定**）：离线缓存 feed / 拆成两道门禁 / 显式允许跳过并记录。

⇒ 连同 `frontend_test`，`exit_criteria.dev` 的"全部 implementation 门禁通过"**当前无法达成**，须收口前裁定。

---

# ITER 2｜WP2.2 + WP2.3：本体真实进入路由（2026-09-15）

> ITER 1 的"未完成"清单（WP2.2 / WP2.3 / 黄金更新 / 依赖边）**本轮全部关闭**。

## 产出

| 文件 | 内容 |
|---|---|
| `modules/knowledge-architecture/pom.xml` | 新增依赖边 `knowledge-architecture → semantic-runtime`（**无环**；只依赖端口模块，不依赖任何适配器） |
| `modules/knowledge-architecture/.../ActivationPlan.java` | `Trace` 增加第 4 分量 `ontologyEvidence`；保留 3 参构造供**非运行时样本**使用 |
| `modules/knowledge-architecture/.../plan/DefaultActivationPlanner.java` | 注入 `OntologyPort`；**真实加载**本体；不可达/不可解析 ⇒ `Deny`；版本入 `versions.ontology`；依据入 `trace.ontologyEvidence`；版本入 `planHash` |
| `apps/api/.../config/KnowledgeArchitectureConfig.java` | 装配 `OntologyPort`（`JenaOntologyAdapter`，合同 `CTR-SEM-002`，配置项 `gits.semantic.ontology`）；本体路径**刻意不在装配期 fail-closed**（否则走不到"规划期 Deny"这条要求的行为） |
| `specs/knowledge-architecture/schemas/activation-plan.schema.json` | `trace.ontologyEvidence`（**可选**，理由见 Tick 14） |
| `specs/knowledge-architecture/examples/AP-*-GOLDEN.json` | `versions.ontology` → `CTR-SEM-002@sha256:705578d6324abd0c` |
| `modules/knowledge-architecture/src/test/.../DefaultActivationPlannerTest.java` | +5 用例（13 → **18**） |
| `adapters/knowledge-filesystem/.../DefaultActivationPlannerFilesystemIT.java` | +2 用例（3 → **5**），改用**真实** `JenaOntologyAdapter`（该模块 pom 增 `semantic-jena` **test** 作用域） |
| `apps/api/src/test/.../KnowledgeArchitectureConfigTest.java` | 修自伤回归；并把弱断言加强为"真能读本体" |

## 合同先行（顺序）

`黄金/schema 改` → `make generate`（PASS）→ `make check`（PASS exit 0，**22/23**，INTEGRITY FAILURES 空）→ `实现` → `门禁`。

> **如实声明（不得计为通过）**：`make check` 的 22/23 中有两项**不是**通过 ——
> `gate-injection-tests` = **INCONCLUSIVE（无法判定）**、`semantic-consumption` = **READINESS NOT MET**。
> 两者均为**既有基线项**（与 W0 一致），非本轮引入；`INCONCLUSIVE ≠ 通过`。

## 验证

```
DefaultActivationPlannerTest               Tests run: 18, Failures: 0, Errors: 0
DefaultActivationPlannerFilesystemIT       Tests run:  5, Failures: 0, Errors: 0
MechanismE2eIT（ontology_load）            Tests run:  1, Failures: 0, Errors: 0
./mvnw test                                 api 601/0/0/4、worker 22/0/0/0，15 模块全 SUCCESS
```

**全部用例明细已核对 surefire 报告**（不是"没跑也算过"）。端到端 IT 另断言**真实本体读数 32/34/1/0**。

## 负例与变异自证

| 负例 | 变异 | 变异后 | 恢复后 |
|---|---|---|---|
| ① 本体不可达 ⇒ `Deny` | 守卫换成"静默降级为占位快照" | **FAIL 2 条**（`expected: <Deny> but was: <AllowPlan>`） | **PASS** |
| ② 改本体内容 ⇒ `planHash` 必变 | 从 `deterministicContent` 移除 `ontologyVersion` | **FAIL 模块 1 条 + 端到端 1 条** | **PASS** |

两条负例均带**反空转前置**：负例 ① 先断言拒绝码与消息；负例 ② 先断言"变异确实改变了本体读数"
（32 类 → 33 类）再断言哈希变化，避免"哈希变了但原因不明"。

## 未完成 / 非声明

- **W2 尚未 ACCEPT**（需独立 QA / Owner）；本 ITER **不**代表 `QA_PASS` / `PRODUCTION_READY`；
- `backend_test` 仍为**环境红**（OWASP 联网），本轮未重跑，维持 `FAILURES.md` 既有记录；
- 门禁**未**经 `record_gate.py` 落 `EVIDENCE.json`（Loop 记忆单写者，避免与并行执行者冲突），留给持 baton 的编排者；
- `evidence/gk-ke-chain-trace/trace.json` 的既有噪声已 `git checkout` 还原。
