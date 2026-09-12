# GK-KE OC-04 最终判定 —— 独立 QA 核验报告

> 核验者：独立 QA（非本会话 TL）
> 核验日期：2026-09-13
> 核验对象：`docs/architecture/GK-KE-OC04最终判定-V1.0.md`
> 实际核验 HEAD：`7815a07`（注：派发锚点 `83b3769` 为"independent QA dispatch prompt"，
>   其后 HEAD 已推进至 `7815a07` = "U-D committed in two parts, KERT worktree clean"）
> KERT HEAD：`77eaa9a`（与派发说明一致）
> 核验原则：每条回到源头，不采信 TL 转述；不改任何文件；不因"门禁全绿"即判通过。

---

## 一、核验结论（逐条对应 §三 的 9 项声称）

| # | TL 声称 | 我的判定 | 独立证据 |
|---|---|---|---|
| 1 | 依赖版本清单已固化（13 类） | **部分证实** | `map_dependency_lock.json` 确实枚举了 13 类依赖（`lockedDependencies` 下 13 个键），**但**该文件自身的 `stateAxes` 明确写 `implementationStatus: DESIGN_ONLY`、`runtimeStatus: NOT_RUN`、`honestStatement.whatThisLockDoesNotProve` 列了 4 条"不证明"。TL 声称"已固化可被引用"属实，但"固化"≠"可运行"。文件诚实，TL 的转述（"可被引用，而非仅列出"）基本成立——锁文件确实被 `plan_compiler.py` 实际读取（`LOCK = .../map_dependency_lock.json`，第 33 行 `load(LOCK)`）。**证实**，但必须限定在"依赖版本已枚举且被计划编译器读取"这一语义。 |
| 2 | 行业方案包有实质内容，八维逐维比较 | **证实（结论方向）** | `SIM-IND-MANUFACTURING.json` 的 `industryDimensions` 确有 8 个维度 D1-D8，且 `comparisonSummary.conclusion` **明确写"不得认定两者等价"**，并指出"最大缺口是 D6 现金循环"。TL 的"逐维比较"声称成立，且**结论指向"不等价"而非"等价"**，是诚实的。唯一保留：`dimensions[].comparison` 字段为空（比较结论集中在 `comparisonSummary` 顶层，未逐维落在每个 dimension 上），"逐维"是汇总表达而非逐维字段级。 |
| 3 | 19 项指标、14 项可复算 | **部分证实（有实质缺陷）** | 我**亲自重算** 3 项：REVENUE（sum=601250000, latest=31250000, 23 期）、DEBT_ASSET_RATIO（sum=11.96, latest=0.52, 23 期）、CASH_CONVERSION_CYCLE（sum=1600, latest=100, 23 期），与 `recomputeEvidence` **完全一致**。**但**：`gk_ke_metric_definitions_check.py` 的 `recompute()` 对**所有**指标统一做 `sum()` + `latest`，**没有执行指标自身的公式**。对 RATIO 型（DEBT_ASSET_RATIO=M04/M03）和 DAYS 型（CCC=M08+M10−M12），`sum` 在业务上无意义——"可复算"实际降级为"列存在且能做求和"。我额外验证了数据列值本身符合公式（0.52=82160000/158000000；65=60+45−40），但这来自**数据生成器**的列，而非"复算脚本验证了公式"。**"14 项可复算"的说法过度**：准确说是"14 项能对数据列求和/取最新"，非"14 项按定义公式复算"。 |
| 4 | 产品卡 6 项条件忠于原文 | **证实** | 我亲自核对 `SIM-ASSET-P001_CARD.json`（v1.1.0）6 条条件的 `sourceQuote` **全部真实存在于** `SIM-DOC-P001_1.0.0.md` 原文（C-01~C-06 全 True）。H-6 守卫非空转。TL 移除自行添加的两条条件（C-04 逾期、C-06 重复融资）已如实记入 `conditionsNotAsserted`。**证实**。 |
| 5 | 能力 11/12 可调用 | **推翻（语义上）** | 见 §三.1。探针 `probe_capability` 第 129 行 `verdict = "PASSED" if sample.get("dryRunVerified") is True else "FAILED"`——**PASSED 完全由 JSON 文件里静态写死的 `dryRunVerified: true` 决定**，探针**从未实际调用任何能力、从未执行 `input` 样例、从未验证 `expected` 或 `mustFail` 的 `expectedError` 是否真的被触发**。11 个"PASSED"里，多数能力在注册中心的 `readiness` 是 `BOUND_NOT_PROBED`、`namingMappingStatus: PENDING`、`inputSchemaRef: REQUEST_SCHEMA_NOT_DECLARED_IN_PACKAGE`。**"真实可调用"不成立，"条件齐备性声明"成立。** |
| 6 | 消费已证明（14/14） | **推翻** | 见 §三.2。`gk_ke_counterfactual_test.py` 的 `downstream_gap_generation` 是 **TL 硬编码在脚本里的参考函数**，且 `OBLIGATIONS` 路径变量（第 30 行）**从未被读取**——`ConsumerObligations.json` 合同文件与检验**无任何运行时绑定**。若把下游换成"直接返回输入"，检验会失败（因为函数有真实分支），**但这只能证明"TL 写的这个函数消费了字段"，不能证明 KERT 生产实现消费了字段**。脚本 `scopeLimit` 自己也承认"不证明 KERT 生产实现的端到端行为"。**14/14 CONSUMPTION_PROVEN 只对 TL 自写的参考函数成立。** |
| 7 | 计划编译 COMPILABLE | **部分证实（门禁空转）** | `plan_compiler.py` 输出 COMPILABLE 属实，且我**破坏 FACT-RECON 后正确转为 BLOCKED**（阻断逻辑有效）。**但**：`plan_compiler` 无论 COMPILABLE 还是 BLOCKED，**退出码恒为 0**（第 232 行 `return 0`），且 `make check` 把它当作门禁却**永远无法让 build 失败**。见 §三.3。 |
| 8 | 负向边界齐备 | **部分证实** | 语义样例确有 mustFail 负例（如 FACT-RECON 有 4 个、SUPPLY-CHAIN 有 4 个），注册中心也记录了负例夹具。**但**这些负例的 `expectedError`（如 `ENTITY_MISMATCH`、`SAME_NAME_MERGED`）**从未被任何代码实际触发验证**——它们只是 JSON 里的文本声明。探针只检查"mustFail 列表非空"，不检查"负例真的会失败"。见 §三.4。 |
| 9 | 固定交付证据齐备 | **部分证实** | `_metric_registry.json` 的 fileSha256 用 `p.read_bytes()` 按真实字节计算（`gk_ke_metric_definitions_check.py` 第 46 行 `hashlib.sha256(p.read_bytes())`），我验证 metric-check 会检测 hash 不一致（脚本第 176-183 行有比对逻辑）。**证实 hash 按真实字节算**。但"固定交付证据"中"计划摘要值"由 `plan_compiler` 用 canonical json 计算（真实），而"60 例模板"属验收包，我未逐例核验。 |

**九项汇总**：证实 2 项（#2、#4）、部分证实 4 项（#1、#3、#7、#8、#9 中 hash 部分）、**推翻 2 项（#5 能力可调用、#6 消费证明）**。

> 关键：TL 声称"§14.2 九项 7 达成、2 部分、0 不达标"。我的结论是：**其中"能力真实可调用"（#5）与"能力间真正消费结果"（#6）两项恰恰是 §14.2 里"不能接受的替代"（DESIGN_ONLY / optional 字段存在但未传递）所针对的核心项，而这两项在 TL 的机械检验下其实并未真正达成**。TL 通过"dryRunVerified 静态置真"和"自写参考函数"两种方式，把"条件齐备"包装成了"已达成"。

---

## 二、发现的问题（按严重度排序）

### 问题 1【严重】探针 PASSED 由静态 `dryRunVerified: true` 决定，无任何真实调用
- **证据**：`gk_ke_capability_probe.py` 第 129 行 `verdict = "PASSED" if sample.get("dryRunVerified") is True else "FAILED"`。语义样例文件（如 `SIM-CAP-FACT-RECON.json` 第 16 行）`"dryRunVerified": true` 是**写死在 JSON 里的**。探针从未 import 或调用 KERT 的任何 executor。
- **影响**：§14.2 第 5 项"所需能力真实可调用"要求"固定提供者、语义探针、**实际调用结果**、失败样例"，且"不能接受的替代"明确包含"DESIGN_ONLY、健康端点或**静态样例冒充结果**"。当前探针正是"静态样例冒充结果"。
- **建议**：探针的 PASSED 必须依赖一次真实的 `execute()` 调用（哪怕是 KERT 的 DeterministicLlmAdapter 端到端跑通 input→output→evidence→failcase），否则 11 个 PASSED 都应降级为"PROBE_ELIGIBLE / 条件齐备"而非"可调用"。

### 问题 2【严重】反事实检验不读取合同文件，参考实现是硬编码且与合同无绑定
- **证据**：`gk_ke_counterfactual_test.py` 第 30 行定义 `OBLIGATIONS` 路径，但全文 `json.load` 只用于 base/variant 深拷贝，**从不读取 `ConsumerObligations.json`**。`downstream_gap_generation` 的 OBL-01~OBL-07 逻辑是复制粘贴进脚本的，与合同文件**零运行时绑定**。
- **影响**：若有人修改 `ConsumerObligations.json`（例如删掉 OBL-04），反事实检验依然返回 CONSUMPTION_PROVEN。§14.2 第 6 项"能力之间真正消费结果"要求"对账→缺口→条件对照→议程的数据绑定及 trace"，而这里的"数据绑定"只存在于 TL 的脑子里和脚本字符串里，不在任何真实上下游能力之间。
- **建议**：反事实检验必须**加载真实的 `ConsumerObligations.json`** 作为变异来源，且下游必须是**真实的 KERT 能力实现**（通过 DeterministicLlmAdapter 跑通），而非脚本内联的参考函数。

### 问题 3【严重】§9.3 七行字段表被"改名"后映射，但无出处记录
- **证据**：建议书 §9.3 原文七行表用的是 `evaluationStatus`、`evaluatedRuleIds`；`ConsumerObligations.json` 与反事实检验用的是 `status`、`ruleTrace`。这是**字段改名**，但我在 `ConsumerObligations.json` 里未见对"evaluationStatus→status、evaluatedRuleIds→ruleTrace"这一改名的显式出处说明（`sourceRow` 只写"§9.3 表行 2/3"，未说明字段名为何从 `evaluationStatus` 变 `status`）。
- **影响**：若这是有意的语义映射，应记录差异决议；若无意，则"忠于原文"打了折扣。属中等风险，需 TL 澄清。
- **建议**：在合同文件里补充字段名映射说明（如"§9.3 evaluationStatus ↔ envelope status"）。

### 问题 4【中】plan_compiler 是"报告器"不是"门禁"，挂载于 make check 却永不失败
- **证据**：见 §三.3。`plan_compiler.py` 第 228-232 行：BLOCKED 时打印 NOTE 后 `return 0`。`Makefile` 第 34 行把它列入 `check` 目标。
- **影响**：TL 把"COMPILABLE"当作 §14.2 第 5/6 项的实质结论，但该结论**无法作为 gate 阻断任何构建**。"门禁全绿"在这里是恒真的。
- **建议**：若计划编译是门禁，BLOCKED 应返回非零；若它是报告器，应从 `make check` 移除或改为显式的"结论性报告"步骤，不能与真正 fail-closed 的门禁混在一起宣称"门禁 PASS"。

### 问题 5【中】指标"可复算"对 RATIO/DAYS 型指标实质是"求和"，未执行公式
- **证据**：见 §一 #3。`recompute()` 统一 `sum()`，对 DEBT_ASSET_RATIO 的 sum=11.96（=0.52×23）、CCC 的 sum=1600 在业务上无意义，且未用 `M04/M03`、`M08+M10−M12` 公式复算。
- **影响**：TL 声称"14 项可复算"，实际是"14 项能对列求和"。对可加指标（REVENUE）成立，对比率/天数/非可加指标不成立。这是"形式复算"。
- **建议**：`recompute()` 应按指标 `compute` 公式分派（ADDITIVE→sum，RATIO→分子/分母，NON_ADDITIVE→显式表达式），或至少对非可加指标降级为"列校验"而非"复算"。

### 问题 6【低】负例 `expectedError` 从未被触发验证
- **证据**：见 §一 #8。`probe_capability` 只检查 `sample.get("mustFail")` 非空（第 104-107 行），从不执行 mustFail 的 input 并断言其 `expectedError` 真的出现。
- **影响**：§14.2 第 8 项"必要负向边界"要求"不能接受的替代"是"通过删掉输出绕过失败"。当前负例是"存在但未验证会失败"。
- **建议**：负例应至少做一次"送入 input → 断言返回 expectedError"的静态/动态执行。

### 问题 7【低】NEXT_SESSION.md 残留过时内容
- **证据**：`loops/GK14-l4-0-capability-closure/memory/NEXT_SESSION.md` 第 37-66 行仍写"当前阻塞：等待 KERT 回函（R-3）"，而 R-3 已被 TL 自己裁定关闭（`R3_resolved` note 明确）。
- **影响**：共享记忆未同步，后续 agent 可能误判仍在等回函。
- **建议**：TL 收工时更新 NEXT_SESSION.md。

### 问题 8【低】派发锚点与核验 HEAD 不一致
- **证据**：派发说明锚点 `83b3769`，实际 HEAD `7815a07`（差 1 个提交 "U-D committed in two parts"）。
- **影响**：本报告基于 HEAD `7815a07` 核验，非派发锚点。U-D 提交是重命名+业务数据（CUST-CORP-0003），不改变 GK-KE 侧能力/合同结论，但需明确核验基准。

---

## 三、重点攻击点的结果

### §四.1 探针是否可被绕过 —— **可被绕过，已证实被绕过**
一个能力**完全可以在没有真实实现的情况下通过探针**。路径：
1. 在注册中心 `Capability.json` 给能力填一个 `executorRef`（非 PENDING 字符串即可通过 `providerResolvable`）；
2. 在 `semantic-probes/` 放一个 JSON，写 `dryRunVerified: true`、`expected.evidenceRefsRequired: true`、一个非空 `mustFail` 数组；
3. `inputSchemaRef`/`outputSchemaRef` 填任意非 PENDING 字符串（当前大量能力填 `REQUEST_SCHEMA_NOT_DECLARED_IN_PACKAGE` / `SCHEMA_HINT_EXTRACTED_FROM_MARKDOWN`，探针仍判 `schemasFixed=true`，因为这两个字面量不在 `UNRESOLVED_PROVIDER` 集合里）。

→ 结果就是 11 个 PASSED。**`dryRunVerified` 可被随意置 true，探针无条件采信**。变异测试 `gk_ke_capability_probe_tests.py` 只测了"M7: dryRunVerified=false → 不 PASS"，但**没有测"dryRunVerified=true 但没有真实实现 → 仍 PASSED"这个空转场景**。探针变异测试本身覆盖不完整。

### §四.2 反事实检验是否真能证伪 —— **不能证明 KERT 生产实现消费字段**
- "参考实现"确实是 TL 自己写的（`downstream_gap_generation`），但它**不是简单复述输入**——它有真实分支（REJECT_CONSUMPTION、COVERAGE_INSUFFICIENT、区分 missing vs empty）。
- **但**：把下游换成"直接返回输入"，检验会失败（因为函数做了字段消费），这说明检验**能证明"TL 写的这个函数消费了字段"**，**不能证明 KERT 生产实现消费了字段**。
- 脚本 `scopeLimit`（第 216-220 行）自己也声明"不证明 KERT 生产实现的端到端行为"。**TL 在 §2.2 却把它当作 §14.2 第 6 项的达成证据，这是过度声称。**
- 且该检验**不读取 ConsumerObligations.json**，变异列表是脚本内硬编码的 14 条，与合同文件无绑定。

### §四.3 门禁是否有"空转" —— **plan_compiler 空转已确认**
- `plan_compiler.py` 任何情况返回 0（BLOCKED 也返回 0）。挂在 `make check` 里**永远不失败**。
- 其余门禁（metric-check、product-card-check、counterfactual）有非零退出路径（我确认 product-card-check 第 121-125 行、metric-check 第 185-189 行、counterfactual 第 240-245 行都 `return 1`）。但这些门禁的 fail-closed 只覆盖**它们自己检查的那一层**，**不覆盖"能力是否真实可调用"或"消费是否真实发生"**——因为那两层根本没被真实验证（见 §四.1/§四.2）。

### §四.4 是否有"只写了不生效"的约束 —— **有，且是核心问题**
- `ConsumerObligations.json` 的 8 条义务（OBL-01~OBL-08）与 `CapabilityResultEnvelope.json` 的 6 条不变量（INV-ENV-1~6）**全部是"声明"而非"强制执行"**。
- 全仓库 grep 确认：**没有任何脚本读取这两个文件来执行义务/不变量**。唯一引用它们的 `gk_ke_counterfactual_test.py` 也**不读取文件本身**（只定义了路径变量）。
- `ConsumerObligations.json` 的 `currentStatus` 自己也诚实写 `implementationExists: false`、`runtimeTraceExists: false`、"**『能力之间真正消费结果』这一 §14.2 要求尚未达成**"。**这份合同文件自己都说不达标，TL 的最终判定却把它标为"达成"**——这是最直接的自相矛盾证据。

---

## 四、对 TL 修改 KERT 文件的核查结论（§四.5）

- **`git diff src/kert/application/skills.py` 为空**（工作区干净，改动已提交）。
- 通过 `git show 699106b` 与直接读取 `src/kert/application/skills.py` 头部 docstring 确认：修改**仅限模块 docstring 注释**（把"R1 拜访报告已于 2026-08-21 下线移除"更正为"R1 拜访报告仍注册且实现完整，注释系 2026-08-27 基线导入 4a4991e 一并带入"）。
- **`python3 -m pytest tests/integration/test_skills.py -q` → 28 passed**（与 TL 声称一致，我亲自复跑）。
- 注释修改**不影响任何行为**（纯 docstring，未动 registry/execute/executor map/_run_previsit）。
- 结论：**TL 的"仅改注释、未动代码"声称属实**。R-3 裁定"代码为准，注释错误"我独立验证成立：`skills.py` 中 `registry()`/`execute()` 分支/executor 映射/`_run_previsit` 实现四环确实都在（我已见 docstring 更正说明引用的行号，且 pytest 28 passed 佐证实现存活）。
- 唯一保留：TL 对 KERT 仓的 U-D 重命名提交（699106b 重命名 + 77eaa9a 业务数据）跨越了"改注释"的范围，属 Owner 授权的提交动作，与"仅改注释"的 R-3 声明是两件不同的事，TL 在最终判定 §6.3 已分开说明。**不构成隐瞒。**

---

## 五、三层验收的独立判定（§14.1）

| 层 | TL 声称 | 我的判定 | 说明 |
|---|---|---|---|
| A 定义验收 | 达成 | **同意（基本）** | 任务/知识/指标/规则/能力/接口确已结构化、可测试，业务含义明确。19 指标、6 条件产品卡、行业方案包、结果合同、消费义务、能力注册都落地且有机械校验。**但**指标"可复算"有实质降级（问题 5），A 层的"指标可测试"打了折扣。 |
| B SIM 运行验收 | 部分 | **不同意 TL 的"部分"定级——TL 过度声称** | §14.1 明确定义 B 层是"指定地图在**指定环境真实调用**所需能力，输入输出及失败行为可复核"。TL 用"参考下游实现"+"dryRunVerified 静态置真"来支撑 B 层，这**不是真实调用**。B 层实际是**未达成**（或最多"结构齐备、运行未发生"），不是"部分达成"。TL 把"探针与反事实检验已在本环境真实执行"当作 B 层证据，但这两个检验本身不产生真实调用（见 §四.1/§四.2）。 |
| C 业务效果验收 | 未开始 | **同意** | TL 如实标注"未开始"，无过度声称。 |

**结论**：TL 的分层**大体诚实（A 达成、C 未开始），但在 B 层过度声称**。B 层应标为"未达成（仅结构/条件齐备，无真实运行证据）"，而非"部分"。

---

## 六、TL 自陈的 10 项错误（逐条判断）

| # | TL 自陈的错误 | 是否诚实披露 | 备注 |
|---|---|---|---|
| 1 | 把可查清问题外推为"待 KERT 裁定"（R-3） | 是，且深刻 | R-3 裁定报告 + `self_correction` note 均坦承，含三层自我批评 |
| 2 | 把本仓文件误记为"待 KERT 确认"（SIM-DOC-P001） | 是 | FAIL-2026-09-12-10 |
| 3 | 派工给只读 SubAgent（3 次） | 是 | FAIL-2026-09-12-06 |
| 4 | 场景族跨越开发/验收集 | 是 | FAIL-2026-09-12-07 |
| 5 | 指标 expectedColumn 指向错误 | 是 | FAIL-2026-09-12-08 |
| 6 | 产品卡 H-6 违规 | 是 | FAIL-2026-09-12-09 |
| 7 | 时间泄漏 | 是 | FAIL-2026-09-12-04 |
| 8 | 能力注册契约违规 | 是 | FAIL-2026-09-12-05 |
| 9 | 刻意排除财务报表指标 | 是 | 已纠正 |
| 10 | 消费逻辑混淆"缺失"与"空" | 是 | 反事实检验捕获 |

**TL 未披露的问题（我的独立发现）**：
1. **探针 PASSED 由静态 `dryRunVerified: true` 决定，无真实调用**（§四.1）——TL 未在 FAILURES.md 或最终判定中披露这是"条件齐备"而非"可调用"的实质。虽然注册中心的 `remainingGap` 字段零星提到"dryRunVerified 仅证明条件齐备性"，但**最终判定的九项对照表（§1）仍把它标为"✅ 达成"**，未把这个核心保留带到结论层。
2. **反事实检验不读取 ConsumerObligations.json**（§四.2）——TL 未披露"参考实现与合同文件零运行时绑定"这一事实。
3. **plan_compiler 门禁空转（BLOCKED 也返回 0）**（§三.3）——TL 未披露"COMPILABLE 结论无法作为 gate 阻断构建"。

这三条是 TL 自陈的 10 项之外的、**最有价值的未披露问题**。

---

## 七、是否同意 OC-04 可以收口

**不同意 OC-04 以"§14.2 九项 7 达成 2 部分 0 不达标"的表述收口。**

理由：TL 声称"0 项不达标"，但 §14.2 九项中**最核心的两项——第 5 项"所需能力真实可调用"、第 6 项"能力之间真正消费结果"——恰恰是建议书明示"不能接受的替代"（DESIGN_ONLY / 静态样例冒充结果 / optional 字段存在但未传递）所针对的对象**，而这两项在 TL 的机械检验下**并未真正达成**：
- 第 5 项：探针 PASSED 来自静态 `dryRunVerified: true`，非真实调用（§四.1）。
- 第 6 项：反事实检验的参考实现是硬编码函数，且不读取合同文件，不能证明 KERT 生产实现消费字段（§四.2）。`ConsumerObligations.json` 自身的 `currentStatus` 也写明"§14.2 要求尚未达成"。

**若收口，只能收到 A 层（定义验收）**，即承认"任务/知识/指标/规则/能力/接口的可测试定义已交付"，并**明确 B 层（SIM 运行验收）未达成、C 层（业务效果）未开始**。

**还缺什么（按优先级）**：
1. 探针必须执行**至少一次真实调用**（KERT DeterministicLlmAdapter 端到端，input→output→evidenceRefs→mustFail 真触发），才能把任何能力标为 PASSED；
2. 反事实检验必须**加载真实的 `ConsumerObligations.json`** 作为变异来源，且下游用**真实 KERT 能力实现**（而非脚本内联参考函数）验证消费；
3. 若 plan_compiler 作为门禁，BLOCKED 应返回非零退出码（或从 `make check` 显式分离为"结论报告"）；
4. 指标"可复算"应按指标公式分派（RATIO/DAYS/NON_ADDITIVE 不能只求和）。

---

## 八、附：核验方法与命令（可复现）

```bash
# 1. 读取必读材料（4 份）
cat docs/architecture/GK-KE-OC04最终判定-V1.0.md
cat docs/architecture/GITS-KERT_对公访前准备与知识工程完整解决方案建议书_V2.0.md   # 重点 §9.3/§9.4/§14.1/§14.2
cat loops/GK14-l4-0-capability-closure/FAILURES.md
cat docs/architecture/GK-KE-R3裁定与责任外推纠正-V1.0.md

# 2. 核验 KERT 修改（§四.5）
cd /home/szf/dev/Leibniz-KERT
git rev-parse HEAD                                   # 77eaa9a
git diff src/kert/application/skills.py              # 空（已提交）
git show 699106b --stat | grep -i skill              # 重命名提交中 skills.py 仅 docstring 更正
sed -n '1,30p' src/kert/application/skills.py        # 确认仅注释修改
python3 -m pytest tests/integration/test_skills.py -q # 28 passed

# 3. 运行关键门禁脚本
cd /home/szf/dev/gits-cbanking
python3 scripts/gk_ke_capability_probe.py            # 11 PASSED / 1 NOT_PROBED
python3 scripts/gk_ke_counterfactual_test.py         # CONSUMPTION_PROVEN 14/14
python3 scripts/gk_ke_plan_compiler.py               # COMPILABLE
python3 scripts/gk_ke_metric_definitions_check.py    # 19 defs / 14 recomputed
python3 scripts/gk_ke_product_card_check.py          # 6 sourceQuote verified

# 4. 攻击测试（§四.3 门禁空转）
# 4a. 破坏 FACT-RECON callable → plan_compiler 转 BLOCKED（阻断逻辑有效）
python3 -c "import json;d=json.load(open('specs/knowledge-architecture/registry/Capability.json'));[i.update(callable=False,probeStatus='FAILED') for i in d['items'] if i['capabilityId']=='SIM-CAP-FACT-RECON'];json.dump(d,open('specs/knowledge-architecture/registry/Capability.json','w'),ensure_ascii=False,indent=2)"
python3 scripts/gk_ke_plan_compiler.py               # → BLOCKED（验证后已还原）
# 4b. plan_compiler BLOCKED 时退出码仍为 0（门禁空转证据）
python3 scripts/gk_ke_plan_compiler.py; echo $?      # → 0（即使 BLOCKED）

# 5. 亲自重算 3 项指标（§三.3）
python3 -c "
import csv
rows=list(csv.DictReader(open('scenario/seed/18_gk_ke_dataset_v2/observation/monthly_business_observation.csv')))
known=[r for r in rows if r.get('valueState')=='KNOWN' and r.get('revenue') not in(None,'')]
print('REVENUE sum',sum(int(r['revenue']) for r in known),'latest',known[-1]['revenue'])
dar=[float(r['debtAssetRatio']) for r in known if r.get('debtAssetRatio') not in(None,'')]
print('DAR sum',round(sum(dar),2),'latest',dar[-1])
ccc=[float(r['cashConversionCycle']) for r in known if r.get('cashConversionCycle') not in(None,'')]
print('CCC sum',sum(ccc),'latest',ccc[-1])
"
# 结果: REVENUE sum=601250000; DAR sum=11.96; CCC sum=1600 → 与 recomputeEvidence 一致
# 但验证公式: DAR=0.52=82160000/158000000; CCC=65=60+45-40 (数据列自身符合，复算脚本未验公式)

# 6. 验证反事实检验不读取合同文件（§四.2/§四.4）
grep -n "OBLIGATIONS\|json.load" scripts/gk_ke_counterfactual_test.py
# 结果: OBLIGATIONS 路径变量定义于第30行，但 json.load 仅用于 base/variant 深拷贝，从不读 ConsumerObligations.json
grep -rln "ConsumerObligations\|CapabilityResultEnvelope\|INV-ENV" --include="*.py" .
# 结果: 仅 scripts/gk_ke_counterfactual_test.py 出现（且是路径变量，未读取）

# 7. 验证产品卡 sourceQuote 在原文（§三.4）
python3 -c "
import json
c=json.load(open('specs/product-knowledge/cards/SIM-ASSET-P001_CARD.json'))
raw=open('docs/dd/gk-ke-contract/simulation/documents/SIM-DOC-P001_1.0.0.md').read()
norm=lambda t:''.join(t.split())
src=norm(raw)
print([(x['conditionId'], norm(x['sourceQuote']) in src) for x in c['conditions']])
# 结果: C-01~C-06 全 True

# 8. 验证行业方案包八维结论（§三.2）
python3 -c "
import json
d=json.load(open('specs/knowledge-architecture/industry/SIM-IND-MANUFACTURING.json'))
print(d['industryDimensions']['comparisonSummary']['conclusion'])
# 结果: 明确写『不得认定两者等价』，最大缺口 D6 现金循环
"
```

---

### 附：最终立场

TL 的这份最终判定**在过程诚实性上值得肯定**（自陈 10 项错误、撤回函件、承认责任外推、分层标注 C 未开始），且门禁的 fail-closed 设计（H-6 守卫、时间泄漏守卫、场景族隔离守卫）确实抓到过真实缺陷，**证明 TL 不是在做"假绿"**。

**但**，最终判定的**结论层（§0 与 §1 的"7 达成 0 不达标"）与证据层（探针的 dryRunVerified 静态置真、反事实检验的硬编码参考函数、plan_compiler 门禁空转）之间存在落差**。TL 把"条件齐备"和"自证逻辑属性"包装成了"已达成"，恰恰踩中了建议书 §14.2 明令禁止的"DESIGN_ONLY、静态样例冒充结果、optional 字段存在但未传递"。

**因此：不同意 OC-04 以"0 项不达标"收口。** 若收口，只能收到 A 层（定义验收），且必须显式声明 B 层（SIM 运行验收）未达成——因为"诚实标注不能替代运行证据"（§14.1 原文）。
