# Handoff｜P-2 Integration Contract Owner（候任）技术准备包

| 项 | 值 |
|---|---|
| 交接方向 | 候任 Integration Contract Owner（**未任命**，`ROLE_BOARD.integration_contract_owner = UNASSIGNED_GAP`） → **tech_lead** |
| 交接日期 | 2026-09-20 |
| Loop | `ONTO1-ontology-split`，Wave `W-1`（只读分析），Gate `W1-prep` |
| 工作量类型 | 纯草稿 / 零执行：**未跑** `make generate`、**未**改 `specs/`（含 `CONTRACT_INDEX.yaml`）、**未**改 `generated/`、**未**标 `ACTIVE/FROZEN/DESIGN_APPROVED`、**未**发布 IRI、**未**代签 |
| 索引新鲜度 | gits `INDEX_FRESH@71169042`；KERT `INDEX_STALE(144)` ⇒ 本轮**未**用索引对 KERT 结构外推，所有结论回源 `文件:行` |

## 1. 交付物（5 件 DRAFT）

| # | 文件 | 内容 | 对应任务 |
|---|---|---|---|
| 1 | `docs/architecture/ONTO1-L4-注册表治理设计-DRAFT.md` | 6 个治理对象（5 Schema + 1 SKOS）**最小字段集** + 最小性判据 + 版本语义 + 发布状态机 + 授权模型 + **既有 62 条合同的重叠分析** + 待裁 T-1~T-6 | 任务 1 |
| 2 | `docs/architecture/ONTO1-CTR-SEM-拆条登记草案-DRAFT.md` | `CTR-SEM-003/004/005` 草案 + 收窄 `CTR-SEM-002` 草案 + 构建工具硬约束 P-1~P-7 + 裁清单 K-1~K-6/R-2/R-3 | 任务 2 |
| 3 | `docs/governance/ONTO1-三方评审召集规则-DRAFT.md` | 三方定义与资格 + 10 条触发条件 + **否决权边界** + 六步流程 + 时限/法定人数/`ABSTAIN` 效力 + 决议最小字段 + CODEOWNERS 骨架 | 任务 3 |
| 4 | `docs/architecture/ONTO1-CQ5-四态原因码与负例设计-DRAFT.md` | **判定全序（短路优先级）** + 5 码表 + 12 条负例（N1~N12）+ 9 条变异（M0~M8）+ 门禁空转防线 | 任务 4 |
| 5 | `docs/architecture/ONTO1-碰撞检查脚本需求规格-DRAFT.md` | C-1~C-4 判据/真值函数/失败动作/边界 + CLI 契约 + 15 条变异矩阵 + 退役门联动范围声明 | 任务 5 |

**佐证**：任务 5 与 `ONTO1-命名空间ADR联签意见-DRAFT.md` 的 **P-3**（联签前置，脚本原型责任归 ICO）**V-3** 对应；任务 3 与 `ONTO1-Wave1独立语义契约库五条件落地方案-DRAFT.md` §7.1（分级矩阵，失败码 `SCC_REVIEW_SINGLE_PARTY`/`SCC_SELF_APPROVAL`/`SCC_REVIEW_RECORD_MISSING`）**分工不冲突**（见该文 §7.1）。

## 2. 本轮新增的**可复用回源结论**（供下一 holder 免于重复通读）

| # | 结论 | 回源 |
|---|---|---|
| 1 | **`CTR-SEM-001` 的源也是跨层混合制品**：`gits-core.linkml.yaml` 含 **32 类**，L1(`Customer`:25 / `Product`:179)、L2、L3(`OperatingCase`:12)、L4(`TaskType`:124) 全混 ⇒ 执行计划 §5.1 只写"新增 003/004/005 + 收窄 002"是**漏项**，会出现"OWL 已分层、LinkML 仍混层"的半拆分 | `specs/semantic/gits-core.linkml.yaml:11`（classes 块） |
| 2 | **`turtle` kind 不产出 `generated`**：`contract_pipeline.py` 对 turtle 只做校验（`:242-243`），生成分支集合（`:252-275`）**不含 turtle** ⇒ `CTR-SEM-002` 的 `generated: []` 是**正确**设计，不是遗漏；给它声明目标会造成 `make check` 漂移 | `scripts/contract_pipeline.py:242-243`、`:252-275` |
| 3 | **kind → generated 基数硬约束**：`json_schema`/`openapi`… **恰好 1** 个目标（`:253-255`）；`linkml_subset` **恰好 2** 个（`:263-269`）；`kind` 受支持集合无 `skos`（`:249`） | `scripts/contract_pipeline.py:249`、`:253-269` |
| 4 | **登记六键必填**且 `owner`/`consumers` 非空；`authority_source` 必须存在且**拒占位值** | `scripts/contract_pipeline.py:199-204`、`:215-217` |
| 5 | **`authority_source` 全部是 GITS 仓内相对路径**（62 条逐条核对，无跨仓先例）⇒ L2（KERT 仓）**没有登记格式**，需裁定 R-2 | `specs/CONTRACT_INDEX.yaml`（62 条） |
| 6 | **既有登记已覆盖 L4 语义**：`CTR-ACTIVATION-001`（activation-contract.schema.json）、`CTR-GKKE-017`（gk-ke Capability.schema.json）⇒ 直接新建 5 Schema 会造成**同一语义两处登记** | `specs/CONTRACT_INDEX.yaml:307`、`:943` |
| 7 | **全仓 `specs/` 零 `skos:` 使用** ⇒ SKOS 为全新制品类型；`gits:TaskType` 现为 owl:Class，`hasTaskType` 为对象属性 | `grep -rl "skos:" specs/` 无输出；`specs/semantic/gits-core.owl.ttl:65`、`:81`、`:84` |
| 8 | **`AC-` 前缀已被占用**：activation-contract 的 `contractId` pattern `^AC-[A-Z0-9-]+$`；且 GK-KE 已裁定 AC ID **不得复用为 planId**（pattern `^(?!AC[-_]).+$`） | `specs/knowledge-architecture/schemas/activation-contract.schema.json:10`；`specs/gk-ke/v1/schemas/ActivationPlan.schema.json`（`planId`） |
| 9 | **`probeStatus`/`callable` 只在实例文件、不在 schema**：`CTR-GKKE-017` 的 13 项 required 不含二者，但 `registry/Capability.json` 的 `callableRule` 依赖 `probeStatus` ⇒ CQ5 会读到 schema 不承认的字段 | `specs/gk-ke/v1/schemas/Capability.schema.json`（required）；`specs/knowledge-architecture/registry/Capability.json`（`probeStatusEnum`/`callableRule`） |
| 10 | **口径不一致（需 TL 校准）**：消费者净义务实测 **1052 数据行**（`wc -l` = 1053 含表头），而 `memory/NEXT_SESSION.md:33` 写"1068 行" | `loops/ONTO1-ontology-split/evidence/consumer-scan-obligations.csv`；`memory/NEXT_SESSION.md:33` vs `EVIDENCE.md` §2 |

## 3. 待裁项（**须 TL / 委员会 / Owner 裁定，候任 ICO 不得单方决定**）

| 来源 | 编号 | 待裁 |
|---|---|---|
| L4 设计 | T-1 | `ContractVersion` 用 JSON Schema（本稿）还是原设计的 LinkML |
| L4 设计 | T-2 | `publicationStatus` 归 `ActivationContract` 还是 `ContractVersion` |
| L4 设计 | T-3 | `probeStatus`/`callable` 的权威位置 |
| L4 设计 | T-4 | 词表 Owner 是否由公共语义 Owner 兼任 |
| L4 设计 | T-5 | `EPB-*`/`CSB-*`/`TT-*` 前缀是否接受 |
| L4 设计 | T-6 | L4 与 `CTR-ACTIVATION-001`/`CTR-GKKE-017` 的**归并**（扩既有 / 新建+superseded / 分工） |
| 拆条 | K-1 | L1 的 kind 与 generated（倾向 K-1b `linkml_subset`） |
| 拆条 | K-2 | 收窄后 `CTR-SEM-002.owner` 是否改 `gits_owner` |
| 拆条 | **K-3** | 是否追加处理 **`CTR-SEM-001` 拆条**（防半拆分，见 §2-1） |
| 拆条 | K-4 | `consumers` 扩容是否需逐条回源确认 |
| 拆条 | K-5 | L4 号段与拆分数（S-1 需 5~6 个号） |
| 拆条 | R-2 | 跨仓 `authority_source` 形态（倾向 R-2a 钉定副本 + `authorityEntity`/`hostingRepo` 双字段） |
| 拆条 | R-3 | SKOS 是否有 `kind`（倾向 R-3b 新增 kind，**独立派工**，不塞进 Wave 2） |
| CQ5 | D-1 | `UNKNOWN_REASON` 是否单列并**回写夹具 `expected`**（夹具现为 `DESIGN_ONLY`，改动成本低） |
| CQ5 | D-5 | CQ5 判定服务的查询形态（API 调用 vs 离线判定） |
| 碰撞检查 | R-1 | C-1 是否加严"新旧命名空间必须不同"（防平凡通过），并回写 ADR §5.4 |
| 碰撞检查 | R-4 | 无 `owl:versionIRI` 的制品按 FAIL 还是具名豁免 |
| 三方评审 | — | 代表**姓名与授权书**、CODEOWNERS 名单、决议 ID 编号规则 |

## 4. 未决 / 未做（诚实声明）

- **未任命**：本人（候任 ICO）**没有任何**签署权，5 件全部 DRAFT；L4 注册表、CQ4/CQ5、三方评审召集均因角色缺口阻塞（`OWNER_REQUESTS.md` A-2）；
- **未执行**：CQ4/CQ5 夹具**未运行**（Wave 4），状态仍 `DESIGN_ONLY`；碰撞检查脚本**未实现**；无任何门禁接线；
- **未触碰**：`specs/`（含 `CONTRACT_INDEX.yaml`）、`generated/`、`evidence/cq-fixtures/*.json`（TL 单写者路径）、`docs/dd/`（封版）、`LOOP.yaml`/`STATE.json`/`EVIDENCE.json`/`memory/{ROLE_BOARD.yaml,NEXT_SESSION.md,ORCHESTRATOR.md,INDEX_BASIS.md}`（TL 单写者路径）；
- **KERT 仓**：本环境只读，本轮**未**读取亦未写入；
- **Baton 诚实性**：本轮开工时 baton holder = `tech_lead`，`parallel_allowed = ["feature_pilot"]`，**候任 ICO 不在 parallel 名单**。本轮按"候选角色准备包"性质执行（只读 + 新增 DRAFT 文稿，零执行、零单写者路径写入），未越界；**若 TL 认为仍需严格 baton 授权，请补具名授权或把本包并入既有候选准备流程**。

## 5. 下一 holder（tech_lead）建议动作

1. **最优先**：裁定 **K-3**（`CTR-SEM-001` 是否同批拆条）——这是本轮发现的**计划漏项**，若不带入 Wave 2，会产出"半拆分"中间态；
2. 把 T-1~T-6 / K-1~K-6 / R-1~R-3 / D-1 / D-5 并入 **Wave 2 前置清单**，并在到达时逐条回写设计 V2.0 或 ADR（**不得在实现里绕开**）；
3. 5 件 DRAFT 归档进 `EVIDENCE.md`（只作"候选角色准备包"证据，**不得**计入任何门禁 PASS）；
4. 校准 §2-10 的口径不一致（1052 vs 1068）；
5. 角色任命到达后：把 5 件移交新任 ICO 作为就职基线，并在 `ROLE_BOARD` 把 `integration_contract_owner` 由 `UNASSIGNED_GAP` 改为实体；
6. 若 Wave 2 获准开工：**先把 K-3/K-5/K-6/R-2/R-3 关闭**（否则合同登记无法落笔），再执行"合同先行 → 一次 `make generate` → `make check`"。

## 6. 作业规程（人类 Owner 本会话指令；落盘以防"未落盘 = 不存在"）

| 项 | 规定 |
|---|---|
| **硬阻塞才停** | 仅当问题属 **① 缺凭据 ② 需求冲突 ③ 方向性变更 ④ 安全隐患** 四类之一，且**无法自行解决**时：写 `memory/BLOCKED.md` 并**停止** |
| **其余一律自愈** | 按本 Loop 阶梯协议自主处理（`memory/PROTOCOL.md` §迭代：Plan → Build → Measure → Learn，同一门禁**最多 8 次**，之后置 `blocked`；`LOOP.yaml.repair_policy.max_attempts_per_gate = 8`，**2026-09-21 由 `TL-DECISIONS-W-1.md` D-14 自 5 调整**——权威值以 `LOOP.yaml` 为准） |
| **不得停工询问** | 可自愈问题不得中断等待人类输入 |
| **落盘纪律** | 自愈过程与结论仍须留痕（`FAILURES.md` 先记后修、EVIDENCE 记账），"未落盘结论 = 不存在" |

> 归属说明：本规程源自人类 Owner 本会话指令。若 TL 认为应**Loop 级生效**，请并入 `memory/ORCHESTRATOR.md`（TL 单写者路径，本包不代写）。

## 7. 硬阻塞四类**实检结论**（本轮：**无一类成立** ⇒ 不写 `BLOCKED.md`）

| 类别 | 是否存在 | 实检依据 | 处置 |
|---|---|---|---|
| ① 缺凭据 | **否** | 本轮**零执行、零签名、零外部调用**：未跑 `make generate`/Maven/CI，无 API Key/密码/证书需求。角色任命（`OWNER_REQUESTS.md` A-2）与 D3 根域属**决策等待**，非"凭据缺失"，且不阻止只读草稿 | 不写 BLOCKED；已登记为待裁项 |
| ② 需求冲突 | **存在，但均为文档级且已具名登记，不构成硬阻塞** | 已定位 5 处：<br>(a) `NEXT_SESSION.md:33` "1068 行" vs 实测 **1052** 数据行（`consumer-scan-obligations.csv`，`wc -l`=1053 含表头）⇒ §2-10<br>(b) 设计 §4.4 写 `ContractVersion` 用 LinkML，但工具链下不成立 ⇒ 裁项 **T-1**<br>(c) 执行计划 §5.1 未列 `CTR-SEM-001` 拆条（同源跨层混合制品）⇒ 裁项 **K-3**、§2-1<br>(d) ADR §5.4 的 C-1 字面判据存在平凡通过漏洞 ⇒ 裁项 **R-1**<br>(e) 设计 §2.1 "4 条 range 改指" vs 机读矩阵 5 条（PSO-01 已登记 **O-4**） | 一律以"**草案 + 具名待裁定**"处理，回写责任归 TL/Wave 2 前置；**不阻断当前 scope**；设计侧改动按 workspace 规则"不得在代码里绕开" |
| ③ 方向性变更 | **否** | 本轮 scope 无变化；未收到任何改变四层模型/波次/裁定 3 的新指示 | — |
| ④ 安全隐患 | **否** | 5 件 DRAFT **不含**任何密钥/口令/内网地址；未新增攻击面；未放开 `.understandignore` 凭据排除段；未启用隔离资产（Oracle/Ossie） | — |

**自愈项遗留**：**无**。本轮所有可自愈问题（口径回源、路径存在性、kind 约束推导、锚点核对）均已在会话内自愈并通过回源验证；未自愈的均为**须人类裁定**的项（登记于 §3），不属"可自愈"范畴，故**不停工、不写 BLOCKED**。

**唯一授权类疑问（显式上报，不自行判定为硬阻塞）**：`memory/PROTOCOL.md:5` 规定"holder 不匹配时停止"，而本轮 baton holder = `tech_lead`、`parallel_allowed = ["feature_pilot"]`，候任 ICO **不在名单**（详见 §4 末条）。本轮按"**人类 Owner 明确指示 + Loop 内既有同类先例（`PSO-01-公共语义Owner候选准备包.md`，同为候任角色在 tech_lead 持棒期出纯草稿包）**"处理，未越界（零执行、未写任何单写者路径）。**若人类 Owner 认为应严格按 PROTOCOL 停机**，请一句话指示，本轮改按四类①处理（写 `BLOCKED.md` 并待补具名 baton 授权）。

**为何本轮不写 `BLOCKED.md`**：`BLOCKED.md` 在共享记忆中具**治理含义**（表示 Loop 停机待外部解除）。四类均不成立而写入，会制造**假阻塞记录**，误导后续 holder 与门禁判读。按纪律"无法判定 ≠ 通过"，同理"未阻塞 ≠ 阻塞"。

---

**红线复核**：本包未标 `DESIGN_APPROVED`/`ACTIVE`/`FROZEN`；未改 `specs/`（含 `CONTRACT_INDEX.yaml`）与 `generated/`；未执行 `make generate`；未发布 IRI；未代签；未 `git add .`；KERT 仓只读；**未写 `BLOCKED.md`**（四类实检均不成立）。

**[收工] Loop: ONTO1-ontology-split, Gate: W1-prep, Baton → tech_lead**
