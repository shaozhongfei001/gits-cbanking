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
