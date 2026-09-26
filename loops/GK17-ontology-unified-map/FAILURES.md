# GK17-ontology-unified-map｜Failures（append-only）

失败必须在修改实现之前由 `scripts/record_gate.py`追加。每项至少包含时间、Gate、命令、退出码、证据文件、初步分类和下一动作；修复后追加根因、变更SHA与原命令重跑结果，不覆盖原记录。

## 20260915T002544Z｜frontend_test

- Command: `make frontend-test`
- Exit: `2`
- Evidence: `loops/GK17-ontology-unified-map/evidence/frontend_test-20260915T002544Z.log`
- Classification: `PENDING_ROOT_CAUSE`
- Next: diagnose, record root cause, fix, rerun the original gate.

### 根因（已定位，2026-09-15）

`make frontend-test` 的第一步是 `npm ci`（锁文件一致性安装），它会**清空并重建 `frontend/node_modules`**。
本环境的**沙箱批量删除守卫**拦截了该操作：

```
npm error [safe-delete][SAFE_DELETE_BULK_CONFIRM_REQUIRED]
  {"count":538,"threshold":500,"scope":"turn",
   "targets":["/home/szf/dev/gits-cbanking/frontend/node_modules/@css-render"],"targetCount":1}
```

- **分类**：`ENVIRONMENT_LIMITATION`（**非产品缺陷、非本 Loop 引入**）
- **证据**：`evidence/frontend_test-20260915T002544Z.log`（含完整 STDERR）
- **代码相关性**：W1 仅改动 `specs/semantic/` 与 `generated/semantic/`，**与前端无交集**；
  W0 基线已实测前端为绿（`npx vue-tsc --noEmit` = 0 错误；`npx vitest --run` = 63 文件 / 342 通过）

### 处置（**不擅自弱化门禁**）

1. **本条目保持 fail 状态**：`npm ci` 确实未执行成功 ⇒ **不得记为 pass**；
2. 不在本 Loop 内把 gate 命令改成"跳过 `npm ci` 的等价物" —— 那会移除门禁四项职责中的
   「锁文件安装」一项，属**门禁弱化**，须走治理决策而**非 TL 自行处置**；
3. 记录两个候选出路，**待 Owner/TL 治理裁定**：
   - **(a) 环境侧**：为本 Loop 的验证放行 `npm ci` 的删除额度（或改用 `npm install --prefer-offline` 等不触发阈值的等价安装）；
   - **(b) 门禁侧**：经批准后把 `frontend_test` 拆为「安装」与「类型+测试」两道，前者标注环境前置条件；
4. **对 W1 的影响**：**无**。W1 的 ACCEPT 判据为
   「`make generate` + `make check` + `MechanismE2eIT` + 新类进 SHACL」，全部已 pass；
5. **对 W8 的影响**：`LOOP.yaml.exit_criteria.dev` 要求"全部 implementation 门禁通过"，
   ⇒ 本条**阻塞 W8 收口**，须在 W8 之前裁定 (a)/(b)。
- Next: 记录根因（已完成）；等治理裁定 (a)/(b) 后按原命令重跑，并在本文件追加重跑结果（不覆盖本记录）。

## 20260915T013349Z｜triple_consistency_check

- Command: `python3 scripts/gk17_triple_consistency_check.py`
- Exit: `1`
- Evidence: `loops/GK17-ontology-unified-map/evidence/triple_consistency_check-20260915T013349Z.log`
- Classification: `PENDING_ROOT_CAUSE`
- Next: diagnose, record root cause, fix, rerun the original gate.

### 根因（已定位，2026-09-15）——**门禁自身的断言空转，非数据问题**

WP5.2 的 D1（"本体承载产品关系实例 ⇒ 检出"，判据 V4）**未被其自身的变异探针触发**：

```
  变异目标（仅副本）   : specs/semantic/gits-core.owl.ttl （原始 sha256=1229874d...）
  变异前 D1 计数       : 0
  追加的三元组         : gits:prod_cm_001 gits:requiresProduct gits:prod_set_001 .
  变异后 D1 计数       : 0          ← 变异未被识别
  变异被捕获           : False
  原文件逐字节复原     : True
```

- **分类**：`GATE_NOOP`（**门禁实现缺陷**，不是被测数据缺陷）
- **性质**：**该门禁作者自曝空转**，并据此报 `FAIL` 而**未**以"不一致项合计 0"报绿 ——
  符合本 Loop "断言全绿前必须自问会不会因夹具缺失而空转"的纪律
- **触发条件**：本体里三个产品关系谓词**当前只有 T-Box 声明**（`gits:requiresProduct a owl:ObjectProperty`），
  没有任何个体三元组；D1 的检测器对"谓词被当数据用"的**语法形态**覆盖不足
  （疑似只识别声明块内形态，未识别 `<个体> gits:requiresProduct <个体> .`）

### 处置

1. **记录在修之前**（本条目即记录），**原命令不得改动**；
2. 按**单写者规则**交回该文件作者（`w5-triple-consistency`）修复，已附完整原始输出、
   已确认事实与"不得自行放宽判定边界"的约束；
3. **反空转探针保留**（T-Box 声明不得被误报）—— 修 D1 不得引入过检；
4. 修复后按**原命令**重跑，并在本文件**追加**重跑结果（不覆盖本记录）；
5. `repair_policy.max_attempts_per_gate = 5`，当前第 **1** 次。

### 影响

- **阻塞 W5 ACCEPT**（W5 判据要求"每门禁各自自证：变异前 PASS / 变异后 FAIL / 恢复 PASS"）；
- **阻塞 W6/V4**（V4 反例依赖本门禁的检出能力）；
- **不阻塞** `ref_anchor_check`（WP5.1 已 **pass**，6 个变异全部被捕获）、
  `gk17_prodcard_projection`（**pass**）。
- Next: 作者修复 D1 → TL 串行按原命令重跑 → 追加重跑结果。

### 追加重跑结果（2026-09-15，TL 接手，第 2/5 次）

**作者已停止**（文件 mtime 停在 `09:33:05`，至 `11:36` 无活动，未接修复指令）
⇒ 按单写者失效处置：**所有权回归 TL**，由 TL 在本文件上继续修复。

**D1 已修好**（根因 + 修法）：

`_parse_chunk` 以「第一个 `;` **或 `.`**」为界取主语。多行声明块靠 `;` 截断主语因而一直正常；
但**单谓词三元组 `S P O .` 没有 `;`** ⇒ `.` 成了边界，谓词与宾语被吞进主语，
`pairs` 为空，语句在 `if st.pairs:` 处被**静默丢弃**。修法：主语边界**只取 `;`**，
无 `;` 时主语只占 1 个 token。
- 实测：变异三元组从「不可见」变为**被检出**（`0 → 1`，附行号 367 与裁定依据原文）
- **附带修复一处真缺陷**：`gits-core.owl.ttl:12` 的 `gits:OperatingCase a owl:Class .` 是**真语句**，
  旧解析器把它丢了 ⇒ `gits:OperatingCase` 从未进入本体类集合
- 不回归验证（用 `git show HEAD` 取旧版对比）：**新增 2 条 / 丢失 0 条**

---

## 20260915T033xxxZ｜triple_consistency_check（**第二次失败·更严重**）

- Command: `python3 scripts/gk17_triple_consistency_check.py`（原命令，未改）
- Exit: `0`（**报 PASS，但该 PASS 不可信**）
- Evidence: 见本条目下方逐字输出
- Classification: `GATE_VACUOUS`（**门禁全局空转**）

### 现象（逐字输出）

```
ontology stats  : 0 classes / 0 object properties / 0 datatype properties
projection      : 1 个 RDF 文件 / 0 个个体
                  · specs/knowledge-architecture/instances/product/products.ttl
  [D1] 本体承载关系实例（WP1.3 裁定）                     OK
  [D2] 投影个体类型不是本体类                            OK
  [D3] 地图 mapRef 指向的文件不存在                     OK
  [D4] 投影个体悬空引用                               OK
不一致项合计：0
gk17-triple-consistency-check: PASS (不一致项 0；变异已捕获，断言非空转)
```

### 根因（两条，均已定位到代码）

1. **本体侧读空**：`TurtleDoc.classes()`（源码 ~238 行）实现为
   `{t for st in ... for (p,o,_ln) in st.pairs if p == "type" and o.startswith("gits:")}` ——
   ① `t` 是**未定义的自由变量**；② 真实多行声明块的 `a owl:Class` **被吞进 `subject` 字符串**，
   `pairs` 里**根本没有 `type`** ⇒ 该推导式**恒为空集**。
   实测：本体 32 类 / 34 对象属性 / 1 数据类型属性，门禁读到 **0 / 0 / 0**。
2. **投影侧读空**：`instances/product/products.ttl`（W3.1 产出，**13 个 `gits:Product` 个体**）
   被门禁读作 **0 个个体** ⇒ D2（投影类型比对）与 D4（悬空引用）**无物可比**。

⇒ **D1–D4 全部空转**。它报 PASS，是因为**它什么都没解析**，不是因为没发现问题。

### 自我批评（必须记）

- 我在修复 D1 后看到 `变异被捕获: True` 就准备**接受该门禁** —— 那是**只验证了自己改的那一处**，
  没有核对**输入侧的锚定数字**（`0 classes / 0 individuals`）。
  这个数字在输出里**一直是打印的**，我第一遍**没读**。
- 这正是本仓已有前例的形态（"6 个 Loop 首报全绿实为空转"）。
  ⇒ **教训升格为纪律**：门禁 PASS 前必须核对**输入基数**，只跑变异不够。

### 处置

1. 本条**记为 FAIL**；`EVIDENCE.json` 中 `triple_consistency_check` **不得**记 pass；
2. **修三处**（仍在本文件，TL 为写者）：
   - (a) `classes()` / `object_properties()` / datatype 属性：修正取值来源
     （多行块需从 `subject` 尾部解析 `a owl:Class` / `a owl:ObjectProperty`，并处理 `a`↔`type`）；
   - (b) 投影解析：查清为何 0 个体（`products.ttl` 是合法 Turtle，含 `a gits:Product` 与 `;` 续行）；
   - (c) **加输入基数断言（anti-vacuity precondition）**：本体非空却解析出 0 类、
     或投影文件非空却解析出 0 个体 ⇒ **直接 FAIL**，不得继续报 OK；
3. **D2/D4 也各加一个变异探针**（当前只有 D1 有）；只测 D1 会再次漏掉 D2/D4 的空转；
4. `repair_policy.max_attempts_per_gate = 5`，本门禁当前第 **2** 次。
- Next: 修复 (a)(b)(c) → 按**原命令**重跑 → 核对**输入基数非零**且 D2/D4 变异各自被捕获 → 追加结果。

### 追加重跑结果（2026-09-15，第 2/5 次 → **已收敛**）

**修了四处**（全部在 `scripts/gk17_triple_consistency_check.py`，原命令未改）：

| # | 缺陷 | 修法 |
|---|---|---|
| 1 | `_parse_chunk` 以 `;` **或 `.`** 为界取主语 ⇒ 单谓词三元组 `S P O .` 的主语吞掉谓词与宾语、pairs 为空、语句被静默丢弃 | 主语边界**只取 `;`**；无 `;` 时主语占 1 token（第 1 次修复） |
| 2 | `a <T>` 被留在主语里（`subject="gits:X a owl:Class"`）⇒ `classes()`/`object_properties()`/`datatype_properties()`/`declared_predicates()`/D2 全部匹配不到 `p=="type"` | 在 `_parse_chunk` 把 `a <T>` **取出并规范化为 `("type", T)`**；单谓词形态同理归一 `a`→`type` |
| 3 | `classes()` 语义错误（取"object 以 `gits:` 开头的 type"），且含**未定义自由变量 `t`**（因内层循环从不执行而未被求值，错误被掩盖） | 改为"本体声明的类 = `a owl:Class` 的主语"；`t`→`o` |
| 4 | `strip_comments` 把 `<...rdf-syntax-ns#>` 里的 `#` 当注释切断 ⇒ `@prefix` 行不再以 `.` 结尾、被并入后续块 ⇒ 产生 `subject='@prefix'` 垃圾语句且**吞掉紧随其后的真实语句** | `strip_comments` 增加 `<IRI>` 状态，IRI 内的 `#` 不再截断 |
| 5 | `individuals` 判据要求"谓词/宾语属于**本文件**声明的资源"，而投影文件只写个体、类声明在本体里 ⇒ 一个个体都识别不出 | 改为"主语被非 schema 类实例化" |
| 6 | **D4 逻辑自证**：把投影里每个**宾语**都计入"已知个体集" ⇒ 任何引用都自动"存在" ⇒ **构造上不可能触发** | 只把**主语**（被定义者）计入；本体宾语另行计入 |

**重跑结果（原命令 `python3 scripts/gk17_triple_consistency_check.py`）**：

```
ontology stats  : 32 classes / 34 object properties / 1 datatype properties
projection      : 1 个 RDF 文件 / 13 个个体
  [D1] OK  [D2] OK  [D3] OK  [D4] OK
不一致项合计：0
gk17-triple-consistency-check: PASS (不一致项 0；变异已捕获，断言非空转)
EXIT=0
```

**关键：输入基数已与 TL 在 W1/W3.1 的独立实测值逐项相等**
（本体 32 类 / 34 对象属性 / 1 数据类型属性；投影 13 个体）⇒ 不再是空转。

**各检测的"非空转"证明（变异测试，TL 执行）**：

| 检测 | 变异 | 结果 |
|---|---|---|
| D1 | 往本体副本追加 `gits:prod_cm_001 gits:requiresProduct gits:prod_set_001 .` | **捕获**（0→1，附行号 367 与裁定原文） |
| D2 | 临时根把 `a owl:Class` 改成 `a owl:Klass` | **真检出 13 项** |
| **新增基数断言** | 同上 | **FAIL**：`输入基数断言失败（anti-vacuity）：本体有语句但解析出 0 个类 ⇒ 解析器失效` |
| D4 | 临时根注入 `gits:gk17_d4_probe ... gits:requiresProduct gits:gk17_no_such_individual .` | **真检出 1 项** |
| 不回归 | `git show HEAD` 取旧版对比 | 新增 2 条 / **丢失 0 条** |

**残留（如实登记，未修）**：

1. **D2/D4 的变异探针尚未内置到 `--selftest`**（当前只有 D1 内置）。上面两条是我在**外部临时根**上执行的，
   命令已逐字记录于上表，可复现；但门禁自身的 `SELFTEST RESULT` 仍只覆盖 D1 ⇒ **记为 W5 收口前必办**；
2. **D4 在当前数据下"有能无力"**：`products.ttl` 现在 **0 条对象引用**
   （因 W3 发现的产品卡引用空间缺陷，40 处引用 100% 悬空、未写入 A-Box）
   ⇒ D4 的**能力**已由变异证明，但**当前数据触发不到**。
   这与 Owner 待签第 1 项（产品卡引用空间）直接相关：**该项不裁定，D4 就没有真实输入**。

- Classification: `GATE_VACUOUS` → **已修并自证**（第 2/5 次内收敛）
- Next: W5 收口前把 D2/D4 探针内置；其余见 `memory/waves/W5-ITER.md` 残余项。

## 20260915T035533Z｜backend_test

- Command: `make backend-test`
- Exit: `2`
- Evidence: `loops/GK17-ontology-unified-map/evidence/backend_test-20260915T035533Z.log`
- Classification: `PENDING_ROOT_CAUSE`
- Next: diagnose, record root cause, fix, rerun the original gate.

### 根因（已定位，2026-09-15）——**网络导致的瞬时失败，非本 Loop 改动**

```
[ERROR] Failed to execute goal org.owasp:dependency-check-maven:12.1.0:check (default)
        on project gits-knowledge-engineering: ... One or more exceptions occurred during analysis:
[ERROR]   UpdateException: Failed to initialize the RetireJS repo
[ERROR]     caused by DownloadFailedException: Download failed, unable to copy
              'https://raw.githubusercontent.com/Retirejs/retire.js/master/repository/jsrepository.json'
[ERROR]     caused by SocketTimeoutException: Read timed out
[ERROR]   NoDataException: No documents exist
[INFO] gits-kno-api ....................................... SKIPPED
[INFO] gits-kno-worker .................................... SKIPPED
```

- **分类**：`ENVIRONMENT_LIMITATION`（**网络**），且是**瞬时**而非永久 ——
  同一门禁在本 Loop **Tick 5 与 Tick 8 曾两次 `BUILD SUCCESS`**
- **触发点不在测试**：`dependency-check` 挂在聚合工程上，**先于模块构建**失败；
  `gits-kno-api` / `gits-kno-worker` 被 **SKIPPED** ⇒ **模块测试根本没跑到**
- **与 WP2.1 的关系**：**无**。WP2.1 是纯新增（1 接口 + 1 适配器 + 1 测试），未改任何既有文件；
  其单测在同一会话内已独立通过（`Tests run: 7, Failures: 0, Errors: 0`）
- **门禁自身的观察（记为 finding，非本 Loop 缺陷）**：
  `make backend-test` 把"单元测试"与"OWASP 联网拉取漏洞库"耦合在同一入口
  ⇒ **网络抖动即可让该门禁变红**。一个会因网络原因变红的门禁，容易被当成噪音忽略 ——
  这与本 Loop 在 W5 学到的教训同族。**建议 W8 一并提治理**（拆开关卡 / 固定 feed / 离线缓存），
  但**本 Loop 不擅自改门禁构成**。

### 处置

1. **如实记为 FAIL**，不改命令；
2. **按原命令重跑**（瞬时失败，须验证是否为真缺陷）；
3. 重跑结果**追加**于下，不覆盖本记录。

### 重跑结果（2026-09-15，第 2 次，**仍未通过**）

按原命令 `make backend-test` 重跑 ⇒ **exit 2，同一根因**（`UpdateException: Failed to initialize the RetireJS repo`，
`knowledge-filesystem` / `gits-kno-api` / `gits-kno-worker` 全部 **SKIPPED**）。

⇒ **不是一次网络抖动，而是该 feed 端点当前不可达**（同一门禁在本 Loop Tick 5、Tick 8 曾两次 `BUILD SUCCESS`
⇒ 当时可用）。**仍记为 FAIL，不转为通过。**

### 分离验证：**证明与本 Loop 改动无关**（关键证据）

`make backend-test` 第一步是 `./mvnw verify`，而 `dependency-check-maven` 绑在 **`verify` 阶段**
（`pom.xml` 第 120–131 行）。故改用 **`./mvnw test`**（不进 `verify`、不拉漏洞库）单独验证测试面：

```
$ ./mvnw --batch-mode --no-transfer-progress test
[INFO] Tests run: 600, Failures: 0, Errors: 0, Skipped: 4      ← api
[INFO] Tests run:  52, Failures: 0, Errors: 0, Skipped: 0
[INFO] Tests run:  22, Failures: 0, Errors: 0, Skipped: 0      ← worker
[INFO] BUILD SUCCESS
exit=0
```

⇒ **全模块测试通过**，含 WP2.1 新增的 `JenaOntologyAdapterTest`（`7/0/0/0`）。
**结论：WP2.1 未破坏任何测试；`backend_test` 的红完全来自 OWASP 联网。**

### 门禁自身的缺陷（**记为 finding，交 W8 提治理，本 Loop 不擅改**）

`make backend-test` 把"**单元测试**"与"**联网拉取 OWASP 漏洞库**"**耦合在同一入口**：

```79:82:Makefile
backend-test: backend-deps-check ## Java 21/Maven真实编译和测试
	@test -x $(MVNW) || { echo "FAIL: $(MVNW) missing or not executable"; exit 2; }
	@$(MVNW) --batch-mode --no-transfer-progress verify
	@$(PYTHON) scripts/dependency-check-guard.py --search-root .
```

⇒ **网络抖动即可让该门禁变红**，且红的时候**模块是 SKIPPED 的**（测试根本没跑），
所以这个红**既不代表代码有问题，也无法从中读出任何代码信息**。
一个会因外部网络原因变红的门禁，容易被当成噪音忽略 —— 与本 Loop 在 W5 学到的教训同族。

**建议 W8 提治理**（三选一，**不由本 Loop 单方定**）：
(a) 把漏洞库固定为离线缓存；(b) 拆成"测试"与"漏洞扫描"两道门禁；(c) 允许 `-Ddependency-check.skip` 并显式记录跳过。

- Classification: `ENVIRONMENT_LIMITATION`（网络，外部依赖）
- 对 W8 的影响：连同 `frontend_test` 一起，使 `exit_criteria.dev` 的"全部 implementation 门禁通过"**无法达成**，
  须在收口前裁定。
- Next: 待网络恢复后按原命令重跑并追加结果（不覆盖本记录）。恢复前**不得**把本门禁读作通过。

## 20260915T035854Z｜backend_test

- Command: `make backend-test`
- Exit: `2`
- Evidence: `loops/GK17-ontology-unified-map/evidence/backend_test-20260915T035854Z.log`
- Classification: `PENDING_ROOT_CAUSE`
- Next: diagnose, record root cause, fix, rerun the original gate.

## 20260915T044040Z｜backend_test 的测试面（`./mvnw test`，W2 / WP2.2 自伤回归）

- Command: `./mvnw --batch-mode --no-transfer-progress test`
- Exit: `1`
- Evidence: `loops/GK17-ontology-unified-map/evidence/backend_test-20260915T044040Z-PREFIX.log`
- record_before_fix: **true**（本条先写，再修）

### 现象（逐字）

```
[ERROR] Errors:
[ERROR]   KnowledgeArchitectureConfigTest.plannerWired:30  Unresolved compilation problem:
	The method activationPlanner(RoutePolicyEvaluatorPort, ActivationContractPort, AssetCatalogPort,
	 KnowledgeMapPort, OntologyPort) in the type KnowledgeArchitectureConfig is not applicable for the
	 arguments (RoutePolicyEvaluatorPort, ActivationContractPort, AssetCatalogPort, KnowledgeMapPort)
[ERROR] Tests run: 600, Failures: 0, Errors: 1, Skipped: 4
[INFO] BUILD FAILURE      → gits-kno-worker SKIPPED
```

### 根因（**本 Loop 本次改动引起**，如实记）

WP2.2 要求"规划器注入 `OntologyPort`、真实加载本体"，因此 `DefaultActivationPlanner` 增加第 6 个构造参数
（**刻意设为必填**：可选参数正是"没有本体也能出计划"的降级口子），连带
`KnowledgeArchitectureConfig.activationPlanner(...)` 增加第 5 个参数。
而 `apps/api/src/test/.../KnowledgeArchitectureConfigTest.plannerWired` 仍按 4 参数调用 ⇒ 测试源码编译失败。

**自我批评**：改动前我只 grep 了 `new DefaultActivationPlanner(` 的**构造点**，
**漏了 config 方法本身的调用点**。改公共签名前必须同时 grep「构造点」与「装配方法调用点」。

### 处置（遵守"不许弱化门禁"）

- **不改断言、不改命令、不放宽边界**；
- 只给该测试补上 `ontologyPort` 参数，并**同时加强**它：
  原断言仅为 `isNotNull()`（装配即可通过，属弱断言），补为「端口装配成功 **且** 能真实读到本体
  （版本非空、四类计数非全 0）」—— 让该测试从"能装配"升级为"真能读本体"。
- 其余 599 个 api 测试与全部模块测试**全绿**，红点唯一。

- Classification: `REGRESSION_BY_OWN_CHANGE`
- Next: 按**原命令** `./mvnw test` 重跑，结果**追加**于下（不覆盖本记录）。

### 追加重跑结果（2026-09-15，第 2 次｜**已收敛**）

- Command: `./mvnw --batch-mode --no-transfer-progress test`（**原命令，未改一个字**）
- Exit: `0`
- Evidence: `loops/GK17-ontology-unified-map/evidence/backend_test-20260915T044137Z-POSTFIX.log`

```
[INFO] Tests run: 601, Failures: 0, Errors: 0, Skipped: 4      ← api（601 = 600 + 新增 ontologyPortLoadsRealOntology）
[INFO] Tests run:  22, Failures: 0, Errors: 0, Skipped: 0      ← worker
[INFO] BUILD SUCCESS        （全 15 个模块 SUCCESS，gits-kno-worker 不再 SKIPPED）
```

**收敛证据**：同一命令由 `Errors: 1` → `Errors: 0`；红点唯一且已定位到本 Loop 自身改动 ⇒ 确为自伤回归，已修。

## 20260915T073300Z｜`ontology_load` 门禁的**文档化命令**因 `~/.m2` 过期快照失败（W2 / WP2.2 引入）

- Command: `./mvnw -q -pl apps/api test -Dtest=MechanismE2eIT -DskipITs=false`（`LOOP.yaml.gates.ontology_load` 原文）
- Exit: `1`（本轮**首次**以 W6 的 V1 驱动间接撞到；直接复现见下）
- Evidence: `loops/GK17-ontology-unified-map/evidence/gk17-v1-20260915T073300Z.log`
- record_before_fix: **true**（本条先写，再修）

### 现象（逐字）

```
[ERROR] .../apps/api/src/test/java/com/gien/gits/api/config/KnowledgeArchitectureConfigTest.java:[6,30] 找不到符号
  符号:   类 OntologyPort
  位置: 程序包 com.gien.gits.semantic
[ERROR] .../apps/api/src/test/java/com/gien/gits/api/e2e/V1PrevisitChainTest.java:[15,34] 找不到符号
  符号:   类 JenaOntologyAdapter
  位置: 程序包 com.gien.gits.adapter.jena
[ERROR] 5 errors
```

### 根因（已定位到底层工件，非猜测）

`-pl apps/api`（**不带 `-am`**）会把模块依赖解析到**本地仓库**的已安装工件，而不是反应堆。实测本地仓库里的是：

```
~/.m2/repository/com/gien/gits/semantic-runtime/0.1.0-SNAPSHOT/semantic-runtime-0.1.0-SNAPSHOT.jar
  时间戳 = 2026-09-01 09:53:45        ← 早于 WP2.1（`OntologyPort` 是 WP2.1 新增）
  unzip -l 里 grep -i Ontology ⇒ 无任何命中（该 jar 根本不含 OntologyPort）
```

⇒ **`apps/api` 的模块级构建依赖"`semantic-runtime` 已按当前源码安装到 `~/.m2`"这一环境前提**，
而该前提当前**不成立**（快照落后于源码）。

**为何是本次引入**：WP2.1 只新增了 `modules/semantic-runtime/` 与 `adapters/semantic-jena/`，**未触碰 `apps/api`**，
故门禁当时可过（实测 exit 0、`1/0/0/0`）。**WP2.2 让 `apps/api` 的 `KnowledgeArchitectureConfig` 与其测试
引用了 `OntologyPort`** ⇒ 从此该门禁命令对"过期快照"不再容忍。

**性质**：不是代码缺陷，是**门禁可复现性**缺陷 —— 一条文档化命令能否复现，取决于一个**未被任何门禁校验**的
环境前提（`~/.m2` 新鲜度）。与本 Loop"门禁静默失真"的教训同族：**它红的时候给出的信息是"环境"，而不是"代码"**。

### 处置（**不改命令** —— 遵守"不许弱化门禁 / 不得改命令"）

- **不**修改 `LOOP.yaml` 的 `ontology_load.command`（加 `-am` 会改动门禁命令，被明确禁止）；
- 按该命令**既有**的环境前提修复：把 `semantic-runtime` / `knowledge-architecture` 按**当前源码**重装到本地仓库；
- 随后**按原命令**重跑门禁，结果追加于下。

- Classification: `GATE_REPRODUCIBILITY_GAP`（环境前提未受校验）
- Next: 重装工件 → 按原命令重跑 `ontology_load` → 追加结果（不覆盖）。
- ⚠ 建议 W8 提治理：为模块级门禁登记**前置条件**（如"需先 `./mvnw install -DskipTests`"），
  或在门禁脚本内显式检测本地仓库新鲜度。**本 Loop 不擅改命令，故仅登记。**

### 追加重跑结果（2026-09-15，第 2 次｜**已收敛**）

见下一节 `20260915T0739xxZ`（重装工件后的原命令复跑）。

---

## 20260916T121500Z｜**TL 声明与落盘不符**：ORCHESTRATOR 称所有权回归"已同步写入 `ROLE_BOARD.yaml`"，实际未写

- 发现者：**独立 QA（对抗性复核）** —— `evidence/INDEPENDENT_QA-W2-W6-independent-qa.md` §4 第 1 条
- 证据：`ORCHESTRATOR.md:530` 原文「⇒ 本项所有权**显式回归 TL**，已同步写入 `ROLE_BOARD.yaml`。」
  vs 实测 `grep -n "回归\|ownership" ROLE_BOARD.yaml` ⇒ **`gate_owner` 段无任何回归记录**，
  `gate_owner.exclusive_paths` **仍然**把 `scripts/gk17_triple_consistency_check.py` 列为 `gate_owner` 独占。
- 性质：**`ORCHESTRATOR` 叙述完成度 > `ROLE_BOARD` 落盘完成度** ⇒ 即本 Loop 反复对抗的
  「**记录静默失真**」形态（Tick 14「`W5` 键重复」、Tick 17「`completed_gates: []`」同族）。
  TL **声明了一件没做的事**。
- record_before_fix: **true**（本条先写，再修）
- 处置：① 在 `ROLE_BOARD.yaml` 的 `gate_owner` 段**真正写入** `ownership_overrides`；
  ② 在 `ORCHESTRATOR.md:530` **就地标注**该句与事实不符并指向 Tick 19（**不删历史**）；
  ③ 记为「**声明 ≠ 落盘**」教训，纳入 Tick 19 非声明。
- Classification: `DECLARATION_NOT_LANDED`
- 状态：**已收敛**（见 Tick 19）

## 20260916T121500Z｜门禁汇总行把 `INCONCLUSIVE` 计入分子：「`22/23`」与**同一句括注**自相矛盾

- 发现者：独立 QA（同上，§4 第 2 条）
- 证据（TL 独立复现）：`python3 scripts/run_gates.py` 实测输出

```
gk-ke-gates: 22/23 通过（其中 1 项**无法判定**，不计入通过），耗时 5.1s
  READINESS NOT MET:  ['semantic-consumption']
    其中**无法判定（INCONCLUSIVE）**：['gate-injection-tests']
    INCONCLUSIVE ≠ 通过；它表示当前环境不具备验证条件。
```

- 根因：`scripts/run_gates.py:213` 的分子 `len(results) - len(failed)`，
  而 `failed` 只含 `FAIL`/`BLOCKED`（`:200`）**不含 `INCONCLUSIVE`**；
  同句括注却写"其中 1 项无法判定，**不计入通过**" ⇒ **分子与括注互相矛盾**。
- 真实口径：`[PASS]=21` / `[FAIL]=1`（readiness）/ `[INCONCLUSIVE]=1` / 总数 `23`
  ⇒ **真 PASS = 21/23**，不是 22/23。
- ⚠ **放大后果**：TL 在本 Loop 多份文书里把「`make check` 22/23」当作通过数字引用
  （`LOOP.yaml.contract_check.pass_condition`、`NEXT_SESSION.md`、QA 包 §6）⇒
  **一处工具措辞缺陷被传播成多处"通过"叙述**。
- record_before_fix: **true**
- 处置：① 本 Loop 内所有**由 TL 撰写的**文书改为准确口径（`21 真 PASS + 1 INCONCLUSIVE + 1 READINESS NOT MET`）；
  ② **不**改 `run_gates.py`（**全 Loop 共用工具**，改动外溢 ⇒ 见 Tick 10 同理由）⇒ 登记为待治理项；
  ③ **不**改 `LOOP.yaml.contract_check.pass_condition`（属"判据内容"，`tech_lead` 的 `forbidden` 之一）⇒
  记为 W8 收口必须处理的**文案与事实对齐**项。
- Classification: `METRIC_CLAUSE_SELF_CONTRADICTION`
- 状态：本 Loop 文书**已收敛**；工具侧**待治理**

## 20260916T121500Z｜**D1 / D2 各存在一条已证实的绕过盲区（fail-open）**

- 发现者：独立 QA（同上，§3.7）—— **这是 TL 未要求、且 TL 自己也没发现的缺陷**
- 证据（TL 独立核验源码，确认成立）：

| # | 位置 | 缺陷 | 绕过写法 |
|---|---|---|---|
| **盲区 1（D1）** | `scripts/gk17_triple_consistency_check.py:300-315` `is_tbox_statement()`；由 `:322` `continue` 生效 | 语句只要含 `a owl:Class`（或 `owl:ObjectProperty` 等）即被**整条判定为 T-Box** ⇒ `relation_instances()` 跳过 | `gits:X a owl:Class ; gits:requiresProduct gits:Y .` ⇒ **D1 计数仍为 0** |
| **盲区 2（D2）** | 同文件 `:619` `if not o.startswith("gits:"): continue` | **全 IRI 形式**的类型被整段跳过；而全 IRI 与 `gits:` 前缀是**同一条 RDF 语句的合法等价写法** | `gits:X a <https://gits.bank.example/ontology/core#NoSuchClass> .` ⇒ **D2 计数仍为 0** |

- **严重度**：D1 = 中（需刻意构造）；**D2 = 中高**，因为投影文件 `products.ttl` **已在用**该前缀
  （`@prefix gits: <https://gits.bank.example/ontology/core#> .`），任何改用全 IRI 输出的工具链
  会让 **D2 整体失效**（fail-open）。
- **诚实边界（QA 的措辞我采纳）**：这**不**使当前基线 PASS 变成假绿（基线 `products.ttl` 与本体**确无**违规，
  `vacuity=[]`、四项计数为 0 均为真）。它削弱的是 **V4「必须检出」的强度** ——
  该硬约束**不是绝对的**，存在已证实的反例。
- record_before_fix: **true**
- 处置：① 登记为 **W8 必办**（新增）；
  ② 修法已明确（QA 建议 + TL 复核）：**D1** 在豁免前先断言该语句**不含三个受控关系谓词**；
  **D2** 把全 IRI 与 `gits:` 前缀**规范化到同一命名空间**再比对；
  **并把 E1/E2/E5 三个绕过写法加入门禁自身的变异自检**，否则盲区会**再次静默存在**；
  ③ 修复须附**判定逻辑变异复验**（同 Tick 17 口径）。
- Classification: `GATE_FAIL_OPEN_BLINDSPOT`
- 状态：**已记账，待修**（含在 W8 必办）

## 20260916T121500Z｜**"OWASP 端点不可达"措辞过强**：实为**间歇性超时**，本 Loop evidence 中**有一次全绿**

- 发现者：独立 QA（同上，QA 报告 §4 第 7 条）
- **QA 的指控**：`NEXT_SESSION.md` / QA 包 §6 / 裁定 §4.1 称 `backend_test` 因"OWASP **端点不可达**"而红。
  但本 Loop 自己的 evidence 里就有一次**全绿**。
- **TL 独立核验（两步，均已实测）**：

**第 1 步：确认"有一次全绿"属实**

```
$ ls -la loops/GK17-ontology-unified-map/evidence/backend_test-20260915T002338Z.log
                   510583  9月 15 08:25
$ grep -E "BUILD SUCCESS|Analysis Complete|dependency-check-guard: all" <该日志>
4115:[INFO] BUILD SUCCESS
4082:[INFO] Analysis Complete (0 seconds)
4135:dependency-check-guard: all 15 report(s) PASS
$ grep -c "SKIPPED" <该日志>
0
```

⇒ 该次 `make backend-test`：**BUILD SUCCESS / 0 模块 SKIPPED / dependency-check 完整执行并产出报告 / 15 个模块报告全 PASS**。
**该门禁在本环境是可以绿的。**

**第 2 步：本次重试（2026-09-16）仍红，且报错同型**

```
$ make backend-test        # evidence/backend_test-20260916T134510Z-W8-RETRY.log
EXIT=2
 39: org.owasp.dependencycheck.data.update.exception.UpdateException: Failed to initialize the RetireJS repo
174-187: operational-ontology … gits-kno-worker  SKIPPED（14 处）
189:[INFO] BUILD FAILURE
198:[ERROR] NoDataException: No documents exist
```

- **正确口径**：`backend_test` 的红是 **RetireJS 端点间歇性超时**（与端点可用性**时间相关**），
  **不是**确定性的"环境不可达"。证据形态：**1 次全绿 + N 次红**。
- ⚠ **但这不改变本次结论**：本次重试**仍红** ⇒ `make backend-test` **仍不得计为通过**，
  W8 的 `exit_criteria.dev`（全 implementation 门禁通过）**仍未满足**。
- **对 W8 阻塞理由的修正**：理由③由"环境不可达"改为"**依赖外部网络的间歇性超时**"。
  ⇒ 另立 `GK18-test-gate-decoupling` 的**必要性不降反升**：**间歇性红比确定性红更坏** ——
  确定性红会被修，间歇性红会被当噪音忽略，而它红时**测试根本没跑**（本次 14 个模块 SKIPPED）。
- record_before_fix: **true**
- 处置：① 本 Loop 全部文书把"端点不可达"改为"间歇性超时"并附该次全绿证据；
  ② W8 收口前**带重试/预热缓存**再跑一次，据实定性；
  ③ **不得**因"曾经绿过"而把本次红计为通过 —— **两者都要写**。
- Classification: `ENVIRONMENT_CLAIM_OVERSTATED`（间歇性被写成确定性）
- 状态：**已收敛（措辞已改，红仍记账）**

## 20260917T010000Z｜**同一前缀、两个命名空间**：A-Box 与 T-Box 在 IRI 层面**不连通**

- 发现者：**TL**（在修 WP8.0-d 的 D2 盲区时，为决定"按命名空间还是按局部名比对"而实测发现）
  —— **独立 QA 与我此前的复核都没有发现它**（QA 的 §3.7 静态文本注入不会暴露此类问题）
- 证据（可复制复核）：

| 侧 | 位置 | 声明 |
|---|---|---|
| 本体 | `specs/semantic/gits-core.owl.ttl:1` | `@prefix gits: <https://gientech.com/gits/kno/>` |
| 投影 | `specs/knowledge-architecture/instances/product/products.ttl:1` | `@prefix gits: <https://gits.bank.example/ontology/core#>` |
| 投影发生器 | `scripts/gk17_prodcard_to_rdf.py:31` | `GITS = "https://gits.bank.example/ontology/core#"` |

```
ontology   gits:Product = https://gientech.com/gits/kno/Product
projection gits:Product = https://gits.bank.example/ontology/core#Product
IRI 相同?  False
```

- **后果**：在 IRI 层面，`products.ttl` 里 13 个个体的类型断言**指向一个本体未声明的类**
  ⇒ **A-Box 与 T-Box 不连通**。任何真实 RDF/OWL 消费者（含 W2 已装配的 Jena 路径）
  都不会把投影个体认作本体 `gits:Product` 的实例。
  ⇒ 这**不影响** V2/V3/V4 的既有判定（那三条不消费 A-Box），但**直接命中** V1 的 ②
  （"本体查实体/关系"）与将来 W3.2/W4 的 A-Box 交付 —— 即使装了 `SemanticQueryPort`，
  查出来的也会是"两个互不相干的命名空间"。
- **为什么没有门禁发现**：`triple_consistency_check` 的 D2 与 `ref_anchor_check` **都是文本级**，
  按**局部名**（`gits:Product` == `gits:Product`）比对 ⇒ 文本相同、语义不同，**门禁全绿**。
  这与本 Loop 反复对抗的"**同词两义 / 静默漂移**"是同一族（对照统一地图承担者论证附录 A.2）。
- **为什么 TL 不擅改**：修它要动 `products.ttl`（哈希变化 ⇒ 使 QA 的冻结靶标失效）
  + 改投影器命名空间 + 重跑 `gk17_prodcard_projection`，且要先裁定
  **"个体应归哪个命名空间"**（是统一到本体命名空间？还是本体侧另立 SIM 命名空间？
  还是显式登记两空间之间的 `owl:sameAs`/映射？）—— 属 **Owner / 语义架构 Owner 级裁定**
  （停止条件 #2 需求冲突 / 方向性变更），**不在 WP8.0-d 的 scope 内**。
- record_before_fix: **true**
- 处置：① **本缺陷单独记账**；② `term_local_name()` 的 docstring 写明
  "本门禁**只比局部名、不做 IRI 级命名空间解析**，这是**已知且已登记的局限**"
  —— 否则下一位读者会以为 D2 做了命名空间校验；
  ③ **列为 Owner 待裁定项**（与"产品卡引用空间"并列）；④ 修复后须**重跑投影门禁 + 重新冻结靶标**。
- Classification: `NAMESPACE_MISMATCH_SILENTLY_GREEN`
- 状态：**已记账，待 Owner 裁定**（TL 不擅改）
