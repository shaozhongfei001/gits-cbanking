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
