# GK17-ontology-unified-map｜Orchestrator tick log（append-only）

## Tick 0｜INITIALIZED

- Time: `2026-09-14T16:13:27.572292+00:00`
- Baton: `tech_lead / W0`
- State: `planned`

## Tick 1｜PLANNED（长程编排落盘）

- Time: `2026-09-15`
- Actor: `tech_lead`
- State: `planned` → `in_progress`
- 动作：
  - 建立 Loop `GK17-ontology-unified-map`（holder=tech_lead）
  - 落盘长程编排 `docs/dispatch/GK17-ontology-unified-map-长程编排-V1.0.md`（W0–W8 × WP × 派工 × 文件所有权 × 停止条件）
  - 确立**第一原则**：并行读 + 串行写（依据 GK16 T-24 实测：门禁并发互相污染产生假 FAIL）
  - 登记 5 项停止条件（仅这 5 种才上报人工）
- 上游判据：`docs/architecture/GK-KE-统一地图承担者论证-V1.0.md` 的 V1 + V2/V3/V4
- 本 Tick **未执行任何门禁、未修改任何合同或实现**
- 下一动作：W0 基线快照（串行门禁）→ W1 本体扩展（合同先行，写串行）

## Tick 2｜DISPATCHED（并行只读侦察）

- Time: `2026-09-15`
- Actor: `tech_lead`
- 动作：**并行**派工 2 个**只读**侦察代理（`code-explorer`），**均不写盘** ⇒ 无写冲突风险
  - 代理 A：`modules/operational-ontology` 全量领域对象清点 → 本体类清单（含标识字段的真实名）
  - 代理 B：ID 空间锚定清单（`ASSET-/SP-/AC-/RP-/KM-/KD-/KI-/KE-/SIM-CAP-`）+ 既有可复用校验器
- 产出：`evidence/W1-INPUTS.md`（由 TL 落盘，代理未写盘）
- 关键发现：
  - **`KM-` 无独立 registry，现有校验器不核对地图间引用** ⇒ W5.1（引用锚定门禁）的主目标
  - **`KD-` 无前缀契约、无注册、无校验**；**`SIM-CAP-` GK-KE 侧无前缀契约** ⇒ 两处缺口
  - 设计点名的 **账户 / 产品 / 文档 / 能力** 在 GITS 侧**无对应 Java 类** ⇒ 须按"域引用类"模式处理，**不得发明字段**
  - 既有 `scripts/validate_knowledge_architecture.py` 应被 W5.1 **复用**（避免"两份可独立修改的定义"，违反约束①）
- 并发纪律执行情况：两个代理**纯读**；本轮**未跑门禁、未改合同** ⇒ 单写者规则未被破坏
- 下一动作：W0 基线快照（串行门禁）→ W1 按 WP1.1→WP1.4 串行扩本体

## Tick 3｜W0 COMPLETE（基线钉死）

- Time: `2026-09-15`
- Actor: `tech_lead`
- 动作：串行采集 9 项基线 → `evidence/W0-BASELINE.md`
- 结果：**generate / check(22-23) / run_gates(INTEGRITY 干净) / ontology_load(1-0) / backend(600-0-0-4) / frontend(vue-tsc 0、vitest 342) / loop-guard PASS / instances 59-59** —— 全绿
- **既有红灯（已钉死，非本 Loop 引入、不归本 Loop 收口）**：
  - `semantic-consumption` = READINESS NOT MET（独立判定，TL 不得代判）
  - `gate-injection-tests` = INCONCLUSIVE（不得计入通过）
  - `contract-check` 不检"已实现未登记合同"（`FAIL-2026-09-14-01` 已登记）
- W0 **ACCEPT**（判据：Loop 合规 PASS + 基线落盘）✅
- 下一动作：**W1**（WP1.1→WP1.4 串行扩本体，合同先行）

## Tick 4｜W1 ITER 1（WP1.1 + WP1.3 + WP1.4）

- Time: `2026-09-15`
- Actor: `tech_lead`（单写者独占 `specs/semantic/`）
- 动作：**先改双权威源**（`gits-core.owl.ttl` +8 类/+14 属性；`gits-core.linkml.yaml` +8 类），
  再 `make generate` → `make check` → `MechanismE2eIT`，**全部串行**，经 `record_gate.py` 落证
- 门禁：`contract_generate` / `contract_check` / `gk_ke_gates` / `ontology_load` / `security_check` / `backend_test`
  = **6 项 pass**；`frontend_test` = **fail**
- **`frontend_test` 失败根因**：环境 safe-delete 守卫拦截 `npm ci` 的 538 文件批量删除
  （`SAFE_DELETE_BULK_CONFIRM_REQUIRED`）⇒ 分类 `ENVIRONMENT_LIMITATION`，**非产品缺陷**
  - 处置：**保持 fail，不弱化门禁**；已记 `FAILURES.md`；两条出路（环境放行 / 治理批准拆门禁）待裁定
  - 影响：**不阻塞 W1**（W1 判据为合同类）；**阻塞 W8**（`exit_criteria.dev` 要求全 implementation 门禁通过）
- 独立产物：`docs/architecture/GK17-WP1.3-产品关系权威归属裁定-V1.0.md`
- 未完成：**WP1.2 系统既有对象（15 类，标识字段已实测）**；`Account`/`Document` 待裁定权威物理源（**不得发明字段**）
- 下一动作：W1 ITER 2（WP1.2）；随后 W1 ACCEPT → 放行 W2/W3/W5

## Tick 5｜W1 ITER 2 + W1 ACCEPT

- Time: `2026-09-15`
- Actor: `tech_lead`
- 动作：**先去重核对，再落盘**
  - 去重实测：`ControlledAction` ≡ 既有 `gits:Action`；`ActionReceipt` ≡ 既有 `gits:Receipt`
    ⇒ **不新建**（同类重复同样违反约束①）
  - 新增 10 类：Opportunity / OpportunitySignal / Commitment / KycGapProfile / HumanGate /
    PolicyRule / ExternalEvent / InteractionExtension / AuditTraceEntry / RelationshipReport
    （标识字段全部实测取自 record）+ 10 个关系
- **规模变化：本体类 9 → 32；OWL object property 5 → 34；系统 30+ 领域对象基本全覆盖**
- 门禁：`contract_generate` / `contract_check`(22-23, INTEGRITY 空) / `gk_ke_gates` / `ontology_load`(1-0) /
  `security_check` / `backend_test`(BUILD SUCCESS, 合同变更后重跑) = **6 项重新落证 pass**；
  `frontend_test` = **fail**（环境限制，保持 fail）
- **W1 ACCEPT**：判据全部满足（generate PASS + check PASS 且 INTEGRITY 空 + Jena 装载 PASS +
  新类进 SHACL + 全部 `record_gate` 落证）✅
- 待裁定（**不阻塞 W2/W3/W5**）：`Account` / `Document` 的权威物理源 —— GITS 侧无系统类（实测零命中）
- 阻塞 W8（非 W1）：`frontend_test` 的环境限制须裁定 (a)/(b)
- 下一动作：放行 **W2（本体进入路由）/ W3（结构化→图）/ W5（硬约束门禁）**；W3 与 W5 可并行

## Tick 6｜W3 ITER 1（WP3.1 完成，WP3.2 阻塞）+ W5 并行派工

- Time: `2026-09-15`
- Actor: `tech_lead`（W3 单写者）
- **W5 并行派工**（依编排第一原则"并行读 + 串行写"）：
  - `w5-ref-anchor` → WP5.1 `scripts/gk17_ref_anchor_check.py`（独占）
  - `w5-triple-consistency` → WP5.2 `scripts/gk17_triple_consistency_check.py`（独占）
  - 两者均被明确禁止跑 `make`/`run_gates.py`/`mvn`、禁止 `git commit`
- **WP3.1 完成**：`scripts/gk17_prodcard_to_rdf.py` + `instances/product/{products.ttl,UNRESOLVED.json}`
  - 个体 **13**；关系实例 **0**；**重复投影逐字节一致** `sha256=e70bbe45…`
  - **非空转证明**：临时 id-map 实测产出 **24 条关系实例**（演示映射已删，权威态重生成）
  - `make check` exit 0 / 22-23（新增制品未使门禁转红）
- **WP3.1 重大发现**：产品卡 12 个被引用的 product_id **全部是符号名**（`SETTLEMENT_ACCOUNT` …），
  与卡身份空间 `PROD-*` **无一相等** ⇒ **40 处引用 100% 悬空**。
  且 `CASH_MANAGEMENT` 同时是 `product_family` 编码与被引用的"配套产品" ⇒ **身份空间冲突**。
  按 WP1.3 裁定 **fail-closed**（strict exit 2），未静默丢弃，未以未裁定口径污染 A-Box。
- **WP3.2 阻塞（降级）**：同一实体「法人」在本仓有**两套互不兼容的 `legal_entity` 定义**
  （`V003` 迁移 vs `scenario/seed` 场景包），且场景包自述 "canonical data is file-first"、
  迁移脚本非权威源。选哪套 = **数据模型权威裁定**（停止条件 #2），**TL 不单方选定**。
  同类问题见 `credit_facility` / `commitment`。**不阻塞 W5**。
- 待裁定清单（并入 Owner 待签）：① 产品卡引用空间缺陷（(a) 卡内改 `PROD-*` / (b) 身份映射入册 /
  (c) 承认符号名不是产品）；② `legal_entity` 等字段口径以运营库还是 file-first SSOT 为准
- 下一动作：收 W5 两门禁 → TL **串行**执行变异自证（变异前 PASS / 变异后 FAIL / 恢复 PASS）→ W5 ACCEPT

## Tick 7｜W5 ITER 1（WP5.1 pass；WP5.2 门禁自曝空转 → fail 记账转回作者）

- Time: `2026-09-15`
- Actor: `tech_lead`（门禁执行者，串行）
- **WP5.1 `ref_anchor_check` = PASS**（新提升为正式门禁）
  - 覆盖 7 个 ID 空间（map/domain/asset/skill/activationContract/routePolicy/taskType），扫描 4 张地图
  - **变异自证：6 个变异全部被捕获**（`SELFTEST RESULT: PASS (6 mutations)`），每个变异
    BEFORE → 注入 → FAIL（附违规项）→ 恢复 → PASS，且被测原文件 **sha256 逐字节复原**（自证）
  - **诚实报告缺口**：`KD-*` 无独立锚点来源 ⇒ `soundness=NOT_COUNTED_AS_PASS_ASSERTION`（不计入通过）
- **TL 独立测量（不采信作者自述）**：修正我自己的 grep 错误后确认 ——
  `specs/knowledge-architecture/assets/**` 有 **21 个真实 `assetId` 锚点**（front matter 是单行 JSON），
  地图引用的 5 个 `ASSET-*` **全部真锚定**；`AC-*`（activations/）与 `RP-*`（routes/）**真锚定**；
  而 `KM-*` / `KD-*` **无独立登记源**（`MapVersion.json` 里只有 `SIM-MAP-FINANCE` 夹具）。
  ⇒ 已排除"全树 grep 造成假 PASS"的空转形态。
- **WP5.2 `triple_consistency_check` = FAIL**（exit 1）—— **根因是该门禁自身断言空转**
  - 其内置变异探针（往本体副本追加 `gits:prod_cm_001 gits:requiresProduct gits:prod_set_001 .`）
    **未被 D1 检出**；作者据此**自曝 noop 并报 FAIL**，**未**以"不一致项合计 0"报绿 ✅
  - D3（mapRef 文件不存在）/ D4（悬空引用）已 OK；原文件 sha256 逐字节复原
  - 已记 `FAILURES.md`（`GATE_NOOP`，**先记账后修**，原命令不改），并按**单写者规则**
    交回文件作者修复（第 1/5 次），附完整原始输出与"不得自行放宽判定边界"约束
- **`gk17_prodcard_projection` = PASS**（个体 13；`determinism: IDENTICAL`；悬空逐条落盘）
- 门禁总表：**9 pass / 2 fail**（`frontend_test` 环境限制；`triple_consistency_check` 待作者修复）
- 下一动作：收作者修复 → TL 串行按原命令重跑 → **WP5.3 变异回归**（逐门禁自证矩阵）→ W5 ACCEPT

## Tick 8｜WP5.1 验收通过 +（发现#5）修掉一处合同错误指引

- Time: `2026-09-15`
- Actor: `tech_lead`
- **WP5.1 `ref_anchor_check` 验收 PASS**：TL 串行独立复现作者三条命令，结果一致
  （基线 PASS / `--selftest` **6/6 变异全捕获** / 4 个被测原文件 **sha256 全部 SAME**）
- **TL 裁决**：批准作者"KD-* 诚实清单"口径，**不改为硬 FAIL** ——
  与其教条一致（`INCONCLUSIVE ≠ 通过`）；KD-* 的问题是**无权威源可校验**而非引用错，
  改硬 FAIL 会让门禁**永久红**，永久红会被当噪音忽略 ⇒ 那才是真的失去防线
- **修掉一处合同错误指引（本 Tick 最高价值产出）**：
  作者报告暴露本体 `gits:Asset` 注释声称"资产登记于 `registry/AssetVersion.json`"，
  实测该文件**只有 4 条 `SIM-ASSET-*` 夹具**；真实锚点是 `assets/**/*.md` 的 `assetId`（21 个）。
  ⇒ 任何按注释去找锚点的人会**全量假 FAIL**。已修正注释并注明 registry 只含夹具。
  修后 `make generate` PASS、`make check` exit 0 / 22-23；受影响的 3 道门禁**重落证**
- **作者报的 6 项既有缺口逐条独立复核，全部为真**（详见 `memory/waves/W5-ITER.md`）
  - 其中**发现 #4 KD 命名空间混淆**（`elements/knowledge-items-index.json` 用 `KD-01/02/08`）
    记为**后续对齐陷阱**：按 `KD-` 前缀全局 grep 会撞上
  - **发现 #6** `Capability.json` 的 `probeStatusEnum` 含枚举外值 `SUPERSEDED` ⇒ 记档待裁定
- **挂 `run_gates.py` 的决定：本轮不做，留 W8**（`run_gates.py` 被多 Loop 共用，改动会外溢）
- 门禁总表：**9 pass / 2 fail**（`frontend_test` 环境限制；`triple_consistency_check` 待作者修）
- 下一动作：等 `w5-triple-consistency` 修 D1 → TL 串行按**原命令**重跑 → WP5.3 变异回归 → W5 ACCEPT

## Tick 9｜WP5.2 空转根治（六处缺陷）+ 门禁升至 9 pass / 1 fail

- Time: `2026-09-15`
- Actor: `tech_lead`（作者已停止逾 2 小时 ⇒ **所有权回归 TL**）
- **事件**：修好 D1 后我**差点接受该门禁** —— 直到读了输出里一直在打印的一行：
  `ontology stats : 0 classes / 0 object properties / 0 datatype properties`（实际 32/34/1）、
  `projection : 0 个个体`（实际 13）⇒ **两边都读空，D1–D4 全部空转**，它 PASS 是因为**什么都没解析**
- **自我批评（升格为纪律）**：门禁 PASS 前必须核对**输入基数**；只跑变异负例不够 ——
  变异只证明"我改的那一处"能触发，基数才证明"其余各处"有物可查。**我第一遍没读那一行数字。**
- **根治六处**：① 主语边界含 `.` ⇒ `S P O .` 被静默丢弃；② `a <T>` 留在主语里 ⇒
  四个取数函数 + D2 全匹配不到 `p=="type"`（**全局空转主因**）；③ `classes()` 语义错 +
  **未定义自由变量 `t`**（因内层循环从不执行而长期未被求值，错误被掩盖）；
  ④ `strip_comments` 把 `<...rdf-syntax-ns#>` 的 `#` 当注释 ⇒ 产生 `subject='@prefix'` 垃圾语句
  并**吞掉后续真实语句**；⑤ `individuals` 判据对投影文件恒为空；
  ⑥ **D4 逻辑自证**（把每个宾语当"存在" ⇒ 构造上不可能触发）
- **重跑（原命令未改）**：`32 classes / 34 object properties / 1 datatype properties`、
  `13 个个体`、`不一致项 0`、`PASS (变异已捕获，断言非空转)`、`EXIT=0`
  ⇒ **输入基数与我在 W1/W3.1 的独立实测值逐项相等**
- **四个检测各自非空转自证**：D1 捕获（0→1，附行号）；D2 真检出 13 项；新增**基数断言** FAIL；
  D4 真检出 1 项；不回归对比（旧版）**新增 2 条 / 丢失 0 条**
- **残留**：D2/D4 探针未内置到 `--selftest`（W5 收口前必办）；**D4 有能无力**
  （`products.ttl` 现 0 条对象引用 ⇒ 当前数据触发不到，与 Owner 待签第 1 项直接相关）
- **门禁总表**：**9 pass / 1 fail**（仅 `frontend_test` 环境限制）
- 下一动作：**WP5.3 变异回归**（逐门禁自证矩阵）→ **W5 ACCEPT**

## Tick 10｜WP5.3 变异回归（复用唯一机制）+ 门禁升至 10 pass / 1 fail

- Time: `2026-09-15`
- Actor: `tech_lead`
- **先行纪律检查（约束①）**：派工表原写"新建 `scripts/gk17_mutation_regression.py`"，
  但动手前查到仓内**已有** `scripts/gate_injection_tests.py` —— **它就是变异机制**
  （自述"对每个门禁注入一个真实缺陷，要求它失败……18 个门禁 0 个有负例"）
  ⇒ **不新造第二套**，改为把 GK17 两道门禁**接入这一套**
- **接入方式（最小侵入）**：`LOOP_GATE_CMDS` 命令回退表 + `_gate_cmd` 回退分支 +
  2 条 `INJECTIONS` + 2 个**精确注入器**（对 `.md` 追加文本改不到 front matter JSON，
  属"测试无效"，按 FAIL-49 教训处理）+ 同步 `_assert_precise_identity()`
- **不登记进 `run_gates.py` 的理由**：会改动 `make check` 的门禁数量与结果，
  而 `LOOP.yaml` 的 `contract_check` 通过条件**写作"22/23"** ⇒ 登记后该文字即失效，
  并外溢到其他 Loop/执行者 ⇒ 属收口期协调变更，**W8 二选一**（登记并改文案 / 删回退表）
- **结果**：`OK gk17-ref-anchor`、`OK gk17-triple-consistency`；
  **注入 18 → 20 项全部被检出 / 0 崩溃 / 0 空转 / 0 未确立**；运行后仓库干净；
  `make check` **exit 0 / 22-23 未变** ⇒ **零外溢已证实**
- **必须说清的限定**：脚本总判定仍是 `INCONCLUSIVE`（另有 3 个**非 GK17** 门禁缺负例证据，
  属 W0 既有基线）。故 `gk17_mutation_regression` 的通过条件**被限定为**
  「GK17 两道在 OK 列表且 0 崩溃/0 未检出/0 未确立」，**不**宣称 `run_gates` 整体通过；
  该 INCONCLUSIVE **不归本 Loop 收口**（已写入 `LOOP.yaml` 的 `pass_condition` 原文）
- **残余**：D2/D4 的**专门**探针仍只在 TL 的外部临时根执行过，未内置到 `--selftest` ⇒ **W8 必办**
- **门禁总表**：**10 pass / 1 fail**（仅 `frontend_test` 环境限制）
- 下一动作：**W5 ACCEPT** → 放行 W2（本体进入路由）与 W6（V1–V4 实验）

## Tick 11｜W5 ACCEPT

- Time: `2026-09-15`
- Actor: `tech_lead`
- **判据核验（逐门禁自证：变异前 PASS / 变异后 FAIL / 恢复 PASS）**：

| 门禁 | 变异前 | 变异后 | 恢复 | 结果 |
|---|---|---|---|---|
| `ref_anchor_check` | PASS | **FAIL**（6/6 变异各自被捕获，附 ID 空间+字段+原因） | **PASS** | ✅ |
| `triple_consistency_check` | PASS（不一致项 0） | **FAIL**（D1 捕获；D2 真检出 13 项；D4 真检出 1 项；基数断言触发） | **PASS**（= 基线） | ✅ |
| `gk17_prodcard_projection` | 个体 13 | — | 重复投影 **逐字节一致** `sha256=e70bbe45…`；非空转证明产出 24 条关系 | ✅ |
| `gk17_mutation_regression` | — | 20 项注入**全部被检出**，0 崩溃 / 0 空转 / 0 未确立 | 仓库干净（`finally` 还原 + 自动回滚 1 个副作用产物） | ✅ |

- **W5 ACCEPT** ✅（WP5.1 / WP5.2 / WP5.3 全部完成且各自自证）
- 门禁总表：**10 pass / 1 fail**（`frontend_test` = 环境 safe-delete 守卫阻断 `npm ci`，非产品缺陷，阻塞 W8）
- **未计入通过者（不得含糊）**：
  - `gate-injection-tests` 总判定 `INCONCLUSIVE`（3 个**非 GK17** 门禁缺负例，属 W0 既有基线）
  - `semantic-consumption` = READINESS NOT MET（独立判定，TL 不代判）
  - `KD-*` 引用空间无独立锚点（已标 `NOT_COUNTED_AS_PASS_ASSERTION`）
- **W8 必办**：① D2/D4 专门探针内置到 `--selftest`；② `run_gates.py` 登记二选一（连带改 `LOOP.yaml` 文案）；
  ③ `frontend_test` 环境裁定；④ D4「有能无力」（需 Owner 裁定产品卡引用空间后才有真实输入）
- **下一动作**：放行 **W2（本体真实进入知识路由）** 与 **W6（V1–V4 实验）**

## Tick 12｜产品卡引用空间裁定（Owner 授权）+ 放行 W2

- Time: `2026-09-15`
- Actor: `tech_lead`（**Owner 授权出裁定**："同意裁定产品卡引用空间，进行下一步"）
- 产物：`docs/architecture/GK17-产品卡引用空间裁定-V1.0.md`
- **裁定要点**：
  1. 三个关系字段的**合法取值空间 = `PROD-*`**（**收紧**，非放宽）——字段名、位置与 WP1.3 裁定都要求它是产品；
  2. 现状 **12 个符号不是产品关系实例**，而是**混合性质的关联引用**（族编码 / 账户 / 工具 / 未覆盖产品）
     ⇒ 当它们是产品关系实例是**范畴错误**，不是数据缺失；
  3. **投影保持 fail-closed**；定性完成前**产出 0 条关系实例是正确结果，不是缺陷**；
     **D4「有能无力」记为已知并接受**，不算缺陷；
  4. **TL 不发明映射** —— 只出**候选**清单（依卡自身的 `name`/`product_family`），
     **相似不等于同一**；权威定性归**产品 Owner**。
- **候选定性（TL 依证据推，非权威）**：
  - 名称层面强对应 **5 个**（`SETTLEMENT_ACCOUNT`→`PROD-SET-001`、`CASH_POOL`→`PROD-CM-001`、
    `WORKING_CAPITAL_LOAN`→`PROD-FIN-001`、`CROSS_BORDER_RMB_SETTLEMENT`→`PROD-CB-001`、
    `BANK_ACCEPTANCE_DRAFT`→`PROD-TF-001`）——**即使全成立也只覆盖 40 处引用的一部分**
  - 命名空间冲突 1 个（`CASH_MANAGEMENT` 与 `product_family` 编码相同 ⇒ 疑为**产品族**）
  - 命名层面就不是产品 2 个（`..._TOOL`、`..._ACCOUNT` ⇒ 疑为**工具/账户**）
  - 本卡集未覆盖 4 个（`CORPORATE_E_BANK` / `FX_FORWARD` / `DISCOUNT_SERVICE` / `FINANCIAL_ADVISORY`）
- **对下游的影响（已写清，不含糊）**：V2/V3/V4 **不受影响**（分别施加在本体/地图/本体上）；
  **V1 可能减弱**（若需产品前置/配套参与，当前无实例 ⇒ 证据须明说该缺口）；
  **WP7.1 受阻**（前置/互斥/配套须标"待产品 Owner 定性"）
- **授权边界声明**：本件是"项目 Owner **授权 TL 出裁定**"，**不是** Owner 对某一具体取值的批准；
  亦**不是** ADR。产品 Owner 的定性与本件候选不一致时，**以产品 Owner 为准**。
- 下一动作：**W2（本体真实进入知识路由）**

## Tick 13｜W2 ITER 1：WP2.1 端口 + Jena 实现（+ 门禁环境问题分离验证）

- Time: `2026-09-15`
- Actor: `tech_lead`
- **产物（纯新增，未改任何既有文件）**：
  - `modules/semantic-runtime/.../semantic/OntologyPort.java`（端口 + 结果态 + 快照 + `evidence()`）
  - `adapters/semantic-jena/.../jena/JenaOntologyAdapter.java`（读真实文件、按内容算版本、按实体计数）
  - `adapters/semantic-jena/src/test/.../JenaOntologyAdapterTest.java`（7 用例）
- **关键设计**：**fail-closed 且不静默降级** —— 失败**显式返回**而非抛异常
  （不可达 → `CODE_MISSING`；空/语法错/模型为空 → `CODE_MALFORMED`）；
  **版本由内容 SHA-256 派生** ⇒ 本体一变版本必变（**判据 V2 能被机械保障的前提**）；
  T-Box/A-Box 判定**复用 Jena 词汇表**，SHACL 仍归既有适配器，**未新造第二套**；
  `evidence()` 输出**可复核的一行依据**（版本+四类计数+来源），不是"已加载"这种空话
- **验证（防空转）**：`Tests run: 7, Failures: 0, Errors: 0, Skipped: 0`，
  7 个用例**全部真实执行**（已核对 surefire 用例明细）。其中
  `loadsRealOntologyWithMeasuredCounts` **断言真实本体读数 = 实测基线 32/34/1/0**
  ⇒ 解析若静默失效会**当场失败**，不靠夹具缺失"通过"
- **门禁 `backend_test` = FAIL（exit 2）**：根因 = `make backend-test` 走 `./mvnw verify`，
  而 OWASP `dependency-check` 需**联网**拉 RetireJS，端点不可达 ⇒
  `gits-kno-api` / `gits-kno-worker` **被 SKIPPED（测试根本没跑）**。
  **已记 `FAILURES.md`，仍记为 FAIL，未转为通过。**
- **分离验证（关键证据）**：改用 `./mvnw test`（不进 `verify`）⇒ **BUILD SUCCESS**，
  全模块测试通过（api `600/0/0/4`、另一模块 `52`、worker `22`），含新增的 `7/0/0/0`
  ⇒ **WP2.1 未破坏任何测试；该红完全来自外部网络**
- **附带 finding（交 W8）**：`make backend-test` 把单元测试与**联网拉漏洞库**耦合在同一入口
  ⇒ 网络抖动即变红，且红时模块 SKIPPED（**读不出任何代码信息**）—— 与本 Loop 在 W5 的教训同族。
  建议三选一（**不单方定**）：离线缓存 feed / 拆两道门禁 / 显式允许跳过并记录
- 门禁总表：**9 pass / 2 fail**（`frontend_test` + `backend_test`，**两者均为环境**，共同阻塞 W8）
- 下一动作：**WP2.2**（规划器消费 `OntologyPort`；本体不可达 ⇒ `PlanDecision.Deny`）+ **WP2.3**（`planHash` 纳入本体版本）

## Tick 14｜W2 ITER 2：WP2.2 + WP2.3（本体真实进入路由；判据 V2 由构造保障）

- Time: `2026-09-15`
- Actor: `tech_lead`（路由负责人）
- 契约先行（**顺序未颠倒**）：先改黄金/合同 → `make generate` → `make check` → 再改实现 → 再跑门禁

### 三条缺口的关闭

| # | 原缺口（W2-PLAN 实测定位） | 关闭方式 |
|---|---|---|
| ① | 本体从未被加载（`ONTOLOGY_VERSION` 硬编码占位串） | 规划器注入 `OntologyPort`，**每次规划真实加载**；占位串已删除 |
| ② | `planHash` 对本体内容**不敏感**（判据 V2 构造上不成立） | `deterministicContent(...)` 纳入本体版本 ⇒ 内容变 ⇒ 版本变 ⇒ 哈希必变 |
| ③ | 计划里**无字段能证明本体被读过** | `trace.ontologyEvidence` = 版本 + 四类计数 + 来源（可复核，非"已加载"空话） |

### 合同变更（先改权威源）

- `specs/knowledge-architecture/schemas/activation-plan.schema.json`：`trace` 新增**可选**属性 `ontologyEvidence`。
  **未列入 `required`** 的理由：黄金计划的 `trace.planHash` 本就是 `GOLDEN_PLAN_HASH_NOT_RUNTIME`
  （**非**运行时样本），强制必填会让非运行时样本失效；而运行时计划由规划器**一律**填入，
  **不存在**缺依据的运行计划。
- 两个黄金：`versions.ontology` 由 `"CTR-SEM-001/002@CURRENT_BASE"` 改为
  **`"CTR-SEM-002@sha256:705578d6324abd0c"`**（= `specs/semantic/gits-core.owl.ttl` 内容 SHA-256 前 16 位）。
  取证单一：该文件正是 `CTR-SEM-002` 的 `authority_source`（`CONTRACT_INDEX.yaml`）。
- `make generate` **PASS** —— `generated/manifest.json` 仅 `CTR-PLAN-001` 与
  `knowledge-architecture/activation-plan.schema.json` 两条哈希变化，**无旁路漂移**。
- `make check` **PASS（exit 0）** —— **22/23 通过，INTEGRITY FAILURES 为空**（与 W0 基线一致）。
  **两点必须如实声明，均不得计为通过**：① `gate-injection-tests` = **INCONCLUSIVE（无法判定）**
  （原文："门禁认领 25/23"，环境不具备验证条件）；② `semantic-consumption` = **READINESS NOT MET**
  （就绪度未达标，**不计入门禁失败**，属既有基线项，非本轮引入）。

### 设计裁定（两条，均写进代码注释，供独立复核）

1. **本体加载位置**：放在**请求级护栏之后、路由解析之前**。理由：本体是**四条 routeMode 的共同前置**，
   先加载可保证"本体不可达"**不依赖** route/合同/地图是否恰好可用 —— **不给任何部分 credit**。
2. **evidence 入不入 `planHash`**：**不入**。`evidence()` 含**来源路径**（环境相关），入哈希会使
   同一份本体在不同机器上哈希不同 ⇒ 破坏可重放性。**只有本体版本（内容派生）入哈希**。
   —— 该裁定有专门**守护用例**（见负例 2 末条）。

### 负例（两条，各自「变异前 PASS / 变异后 FAIL / 恢复 PASS」）

**负例 1｜本体不可达 ⇒ `Deny`（fail-closed）**

- 用例：`deniesWhenOntologyMissingInsteadOfPlanningWithoutIt`、
  `deniesWhenOntologyMalformedInsteadOfPlanningWithoutIt`（`DefaultActivationPlannerTest`）。
  拒绝码 = 端口 `failureCode()`（`ONTOLOGY_MISSING` / `ONTOLOGY_MALFORMED`），消息带 `failureReason()`；
  **不是**抛异常，**也不是**继续出计划。
- **M1 变异**（把 fail-closed 守卫换成"静默降级为占位快照"，即**复现历史缺陷**）：
  `Tests run: 18, Failures: 2` —— 两条用例均以
  `expected: <PlanDecision.Deny> but was: <PlanDecision.AllowPlan>` 变红 ⇒ **捕获"静默降级"**。
  恢复后 `18/0/0/0`。
- 源码 sha256 变异前后一致：`83e3b300e5e5ffb4c28c3cb38450d785fa8d871ecfa73d2839cfc3b18789398d`

**负例 2｜V2：改本体内容 ⇒ `planHash` 必变**

- 模块级：`planHashChangesWithOntologyVersionAndIsStableForSameVersion`（版本变 ⇒ 哈希必变；同版本 ⇒ 可重放）
- **端到端（真实文件 + 真实 Jena 解析）**：
  `DefaultActivationPlannerFilesystemIT.planHashChangesWhenOntologyContentChangesAndReturnsWhenRestored`
  —— 把 `gits-core.owl.ttl` 复制到 `@TempDir`（**临时副本，不动权威源**），追加
  `gits:gk17V2Probe a owl:Class .`（32 类 → 33 类），断言：
  ① 版本**必变**（**反空转前置**：先证明变异真的改了本体读数）② `planHash` **必变**
  ③ 恢复副本 ⇒ 版本与 `planHash` **必变回基线**（可重放）。
  该 IT 用**真实** `JenaOntologyAdapter` + 真实 filesystem readers，非夹具：
  `realOntologyIsLoadedAndEvidencedInPlanTrace` 另断言真实读数 **32/34/1/0**。
- **M2 变异**（从 `deterministicContent` 移除 `ontologyVersion`）：模块级 `Failures: 1`、
  端到端 `Failures: 1`，均为 `本体(内容)变而 planHash 未变 ⇒ 判据 V2 在构造上不成立` ⇒ **捕获**。
  恢复后模块 `18/0/0/0`、端到端 `5/0/0/0`。
- **守护用例**（防"哈希被环境字段污染"）：
  `planHashIgnoresOntologySourcePathSoPlansStayReplayableAcrossMachines`
  —— 先断言两处不同来源路径的 `evidence` **确实不同**（**反空转**），再断言 `planHash` **相同**。

### 自伤回归（已记账，已收敛）

改 `KnowledgeArchitectureConfig.activationPlanner(...)` 签名（+1 参数）时，
`apps/api` 的 `KnowledgeArchitectureConfigTest.plannerWired` 仍按 4 参调用 ⇒ 测试源码编译失败，
`./mvnw test` 一度 `Errors: 1`（api 600），worker 被 SKIPPED。
**已按 `record_before_fix` 先记 `FAILURES.md`（`20260915T044040Z`）再修**：不改命令、不放宽断言，
并把该处**弱断言 `isNotNull()` 加强**为"**真能读本体**"（版本前缀 + 两类计数 > 0 + 来源后缀）。
按**原命令**重跑 ⇒ `BUILD SUCCESS`（api `601/0/0/4`、worker `22/0/0/0`）。
**教训**：改公共签名前必须同时 grep「构造点」**与**「装配方法调用点」——
本轮只 grep 了前者（`new DefaultActivationPlanner(`），因此漏掉后者。

### 门禁结果

| 门禁 | 结果 |
|---|---|
| `contract_generate`（`make generate`） | **PASS** |
| `contract_check`（`make check`） | **PASS**（22/23，INTEGRITY FAILURES 空） |
| `ontology_load`（`MechanismE2eIT`） | **PASS**（`1/0/0/0`，**已核 surefire 明细**，非空转） |
| `./mvnw test`（测试面分离验证） | **PASS**（api `601/0/0/4`、worker `22/0/0/0`，15 模块全 SUCCESS） |

> `backend_test`（`make backend-test`）**仍为环境红**（OWASP 需联网拉 RetireJS），本轮**未重跑**，维持既有记录与 W8 裁定项。
> 门禁**未通过 `record_gate.py` 落 `EVIDENCE.json`** —— 该文件属 Loop 记忆**单写者**，本轮有其他执行者并行提交，
> 为避免并发写冲突，只在本 tick 与 `W2-ITER.md` 落证，`EVIDENCE.json` 的登记留给**持有 baton 的编排者**。

### 附带 finding（交 W8 / 治理，本 Loop 不擅改）

`STATE.json` 的 `wave_state` 里 **`W5` 键出现两次**（`"accepted"` 与 `"not_started"`）。
JSON 后键覆盖前键 ⇒ **实际读数是 `W5=not_started`**，与 `current_phase`（`W5_accepted`）**自相矛盾**。
本轮已修正为 `W5=accepted`（并保留 `W4=not_started`）。
—— 与 W5 的教训同族：**记录本身静默失真，比红更危险**。

- 非声明：本轮**不**声称 W2 ACCEPT，**不**代表 `QA_PASS` / `PRODUCTION_READY`；
  `evidence/gk-ke-chain-trace/trace.json` 的既有噪声已 `git checkout` 还原，未入库。
- 下一动作：**W2 待 ACCEPT**（独立 QA / Owner）；**W6 已放行**（V1–V4 实验）

## Tick 15｜W6 ITER 1：V1–V4 实验与证据（V1 链路可复核；V2/V3/V4 全部有变异对照）

- Time: `2026-09-15`｜Actor: `tech_lead`｜BASE_HEAD: `a1e183b`
- PLAN 先写后做：`memory/waves/W6-PLAN.md`；证据包：`evidence/GK17-W6-V1-V4-证据包.md`；ITER：`W6-ITER.md`

### 结论（含**未达标**与**待裁定**，不粉饰）

| 判据 | 结论 |
|---|---|
| **V1** | **链路可复核＝成立**（原始输出含判据点名的 `planHash` / `versions.ontology` / **路由理由**）；**含 1 处覆盖度缺口** |
| **V2** | **机制成立且有变异对照**；**语义强度弱**（本体语义未驱动选择） |
| **V3** | **成立**（检出 + 6 变异自证）；锚定空间为既有权威 ID 空间（非 A-Box） |
| **V4** | **成立**（检出 + 内置 D1 变异对照 + 注入矩阵覆盖） |

### V1（五步全实测，驱动常驻 `./mvnw test`）

```
① mode=ONTOLOGY_THEN_MAP contract=AC-PREVISIT-001 priority=20
   reason="先锁定客户事实和缺口，再定向加载文档知识"        ← 判据点名的"路由理由"
② ontology=CTR-SEM-002@sha256:705578d6324abd0c  classes=32 objectProps=34 datatypeProps=1 individuals=0
③ selectedAssets=9  semanticQueries=5  ruleChecks=4  skills=[SP-02,SP-05,SP-15,SP-10]
④ skill-customer-previsit-report → SKILL_ERROR（KERT_REQUIRED，策略性 fail-closed）
   对照 gk17-v1-port-probe → isOk=true（端口机制可用 ⇒ 是策略拒绝，不是端口故障）
⑤ planHash=a2413b72e01d7430  versions={KM-GITS-ROOT@0.1.0, RP-CORP-RM-001@0.1.0,
                                       AC-PREVISIT-001@0.1.0, CTR-SEM-002@sha256:705578d6324abd0c}
```

### V2（只改本体、不动地图；四变体 + 源码变异对照）

| 变体 | 本体版本尾 | 类数 | `planHash` |
|---|---|---|---|
| 基线 | `…705578d6324abd0c` | 32 | `a2413b72e01d7430` |
| 变异 A（新增类） | `…66be74f34e6c3f41` | 33 | **`6906980bcbb3d79c`** |
| 变异 B（加互斥关系＝判据字面例） | `…06096dc29b50ba7d` | 32 | **`da83ce9db2994477`** |
| 恢复 | `…705578d6324abd0c` | 32 | `a2413b72e01d7430` |

地图指纹 `mapFingerprintUnchanged=true`（`22ded46cde92b218`）⇒「不动地图」前提成立。
**源码变异对照**：移除 `deterministicContent` 的本体版本 ⇒ V2 驱动 **FAIL**（`Failures: 1`）；恢复后 PASS，planner sha256 复原 `83e3b300…`。

### V3 / V4

- **V3** `gk17_ref_anchor_check.py`：基线 `violations=0`；`--selftest` **6 个变异逐个 FAIL**、`[restored] PASS`
  （含判据字面形状 `fake_assetRef` → `NO_ANCHOR_IN_AUTHORITATIVE_SOURCE`，**给出文件**）。
- **V4** `gk17_triple_consistency_check.py`：基线 D1–D4 全 `OK`、不一致项 0；内置变异把 D1 由 0→1
  **被捕获并给出行号 `gits-core.owl.ttl:367`**，撤销后恢复基线。
- 第二重对照 `scripts/gate_injection_tests.py`（= `gk17_mutation_regression` 的实际命令）：
  **20 项注入全部被检出**，含 `gk17-ref-anchor` / `gk17-triple-consistency`；
  但 `__GATE_VERDICT__=INCONCLUSIVE`（**3 个门禁未取得负例证据**）⇒ **不计为通过**。

### ⚠ 三处**待 ACCEPT 裁定**（本 Loop 不自行裁定）

1. **V1**：②"本体查实体/关系"只到 **T-Box 加载 + 查询声明**（`individuals=0`；`SemanticQueryPort` 在 `apps/api` **未装配**，实测 grep 无命中 ⇒ 实体级查询**未执行**）⇒ 是否影响 V1 通过；
2. **V2**：本体**语义**未驱动 `selectedAssets`/`ruleChecks`/`skills`（只有版本入哈希）⇒ 若 ACCEPT 要求语义驱动则**未达标**（**绊线断言**已把限制钉成可执行，防声明腐化）；
3. **V3**：锚定空间 = 既有权威 ID 空间（`KM/KD/ASSET/SP/AC/RP` + `entrypoints.tasks` 对齐本体 `gits:TaskType`），**不是** A-Box 个体锚定 ⇒ 是否视为通过。

### 本轮实测到的**门禁可复现性缺陷**（已记 `FAILURES.md` `20260915T073300Z`，已收敛）

V1 驱动首次运行撞到：`ontology_load` 的**文档化命令**因 `~/.m2` 里 `semantic-runtime`/`semantic-jena`
是 **WP2.1 之前**的旧快照而 `testCompile` 失败（旧 jar 实测**不含** `OntologyPort`）。
**且该命令只在 `testCompile` 失败、`default-compile` 无错** ⇒ 主类靠**增量编译跳过** ⇒
**上一次"PASS"是靠陈旧 `target/` 达成的**（"门禁 PASS ≠ 正确"的又一实例）。
**处置**：遵守"不许改命令" ⇒ **不改 `LOOP.yaml`**，按既有前提重装工件（`-Ddependency-check.skip=true`
仅用于该**构建卫生**动作、非跑门禁，已显式记录），**按原命令**重跑 ⇒ **PASS**（`1/0/0/0`）。

- 门禁：`make check` PASS（exit 0，22/23，INTEGRITY FAILURES 空；其中 `gate-injection-tests` **INCONCLUSIVE**、
  `semantic-consumption` **READINESS NOT MET**，**两项均不得计为通过**）
- 非声明：W6 **尚未 ACCEPT**；**不是** `QA_PASS`，**不代表** `PRODUCTION_READY`；
  **不**声称真实 dsh/KERT 已接通、**不**声称 A-Box 查询可用、**不**声称本体已"参与"选择；
  未代签任何 Owner 决议。
- 建议 W8 新增两项：① 为**模块级门禁**登记**前置条件**（本地仓库新鲜度 / 先 `install`）；
  ② 修 `LOOP.yaml` 与编排表的**命令口径不一致**（`gk17_mutation_regression` 编排表写
  `scripts/gk17_mutation_regression.py`，实际命令是 `scripts/gate_injection_tests.py`，前者**不存在**）。
- 下一动作：**W6 待 ACCEPT**（三处裁定见上）；W7（产品可见化）与 W8（收口）仍待其他角色。

## Tick 16｜WP8.1 预做：W2+W6 独立 QA 判定包（把"待判定"变成"可判定"）

- Time: `2026-09-15`｜Actor: `tech_lead`｜HEAD: `527291c`
- 判断：当前**瓶颈是判定而非实现** —— W2 与 W6 均已交付待 ACCEPT，而两者判定权都不在 TL 手上
  （`ROLE_BOARD`：`independent_qa.responsibility = gate_review_and_V1_V4_verdict`，`status = unassigned_must_be_separate_session`）。
  TL 能做且被允许做的，是把判据/证据/复核命令/限制/问题**摆到桌面**，**不代签**。

### 产出

`evidence/INDEPENDENT_QA_PACKAGE-W2-W6.md`（唯一入口）：

| 章节 | 内容 |
|---|---|
| §0 复核前置 | **模块级门禁依赖 `~/.m2` 新鲜度**（否则撞假红，实测根因见 `FAILURES.md` `20260915T073300Z`）；门禁须**串行**；还原 `trace.json` 噪声 |
| §1 变更集快照 | commit / `DefaultActivationPlanner` sha256 / 本体 sha256 / `versions.ontology` 口径 |
| §2 W2 判定清单 | 5 条（含两条设计裁定的守护用例） |
| §3 W6 判定清单 | V1–V4 逐条：**判据原文 / 证据 / 复核命令 / 期望 / 已知限制** |
| §4 待裁定问题 | **Q1–Q6**（编号化，便于逐条签署） |
| §5 变异复核配方 | M1（移除 fail-closed 守卫）/ M3（移除本体版本）可复制粘贴、含**还原与 sha256 校验** ⇒ QA 可独立复现"非空转" |
| §6 复核命令速查 | 含**不得计为通过**项（`gate-injection-tests` INCONCLUSIVE、`semantic-consumption` READINESS NOT MET、两道环境红） |
| §7 非声明 | 供判定方核对 TL 未越过哪些线 |

### 发布前**逐条核验**（避免把没验过的话写进判定包）

| 核验项 | 结果 |
|---|---|
| `git grep -n "CURRENT_BASE"`（判定 W2-3） | **修正了一处不准确断言**：不加过滤时有 **1 处命中**，在 `OntologyPort.java:10` 的 **javadoc 历史说明**（非生效取值）。已把判定口径改为"**生效**代码/合同/黄金零命中"，并给出精确命令；实测该命令 **hits=0** |
| `DefaultActivationPlanner` sha256 | `83e3b300…`（与包内一致） |
| `specs/semantic/gits-core.owl.ttl` sha256 | `705578d6324abd0c…`（与包内一致） |
| 两个黄金的 `versions.ontology` | `CTR-SEM-002@sha256:705578d6324abd0c`（一致） |
| 各用例期望计数 | `DefaultActivationPlannerTest 18`、`FilesystemIT 5`、`V1PrevisitChainTest 1`、`V2OntologyOnlyChangeTest 1`、`MechanismE2eIT 1`、`./mvnw test` api **603/0/0/4**、worker **22/0/0/0**（均取自 surefire 报告） |

### 顺带产出的**裁定线索**（**不是**结论，供判定方参考）

`Q3`（V2 语义强度）提示：编排表中「前置/互斥/配套 + 准入」的**语义消费**属 **WP7.1（产品负责人）** 交付面
（`docs/dispatch/GK17-ontology-unified-map-长程编排-V1.0.md`）。即 V2 的"机制成立、语义未消费"
**可能**是预期读法（语义消费归 W7），但**裁定权在 QA/Owner**。

### 非声明

- 本包**不是** `QA_PASS`；TL **未**代签；`STATE.status` 保持 `in_progress`、baton 保持 `tech_lead`
  （**不**改为 `ready_for_independent_qa`，以免在无独立 QA 会话时制造"已交判定"的假象）；
- TL **未**修改 `gate_owner` 独占的门禁脚本、`LOOP.yaml` 门禁命令、封版制品、他人并发改动；
- 门禁未落 `EVIDENCE.json`（单写者 + 并发提交），登记留持 baton 的编排者。
- 下一动作：**等待独立 QA**（入口 `evidence/INDEPENDENT_QA_PACKAGE-W2-W6.md`）；
  W8 必办 6 项已登记到 `NEXT_SESSION.md`。


