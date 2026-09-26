# ONTO1｜下一步工作计划（W-1.5 就绪加固）

| 项 | 值 |
|---|---|
| 编制 | 全局 Tech Lead，2026-09-20（复核后编制） |
| 事实基线（编制时实测） | 门禁 **26 个 = 25 pass / 1 fail**（fail = `wi_a4_namespace_collision`，B-1）；`loop-guard` PASS；孤儿证据日志 **0**；红线制品零改动 |
| 当前门禁位置 | `RETURN_TO_HLD`（有效）⇒ **Wave 0 及以后一律禁止** |
| 本计划性质 | 等待期工作编排：**不做进度表演**，只做两类事——① 消除 Wave 0+ 的**就绪风险**；② 提高已有结论的**可信度** |
| 出口 | 全部工作项绿 + 板面无新 fail ⇒ 更新 `NEXT_SESSION.md`；若 A1 发现真义务暴增 ⇒ 回写 `evidence/WBS-RESTIMATE.md` |

---

## 0. 为什么不"等就算了"

Wave -1 的交付已到只读边界，但**Wave 2 的硬前置里还有一件没做完、且完全不受外部签署阻塞**：
`consumer-scan-obligations.csv` 的 **1038 行 `FOLLOW_MIGRATION` 仍是候选义务**（词法级扫描的产物）。
若等到 `DESIGN_APPROVED` 才动手，Wave 2 会在第一天就卡在这 1038 行上。

另有一类"到点就来不及做"的事：G-1 达成瞬间需要核对输入锚点（复审包哈希、基线哈希、映射草案、ADR 签署件）。现在把失败条件变成红灯，比到点再发现不符要便宜得多。

---

## 1. 战线 A：等待期可立即开工（3 项，按优先级）

### A1｜WI-A2 义务回源确认（**最高优先，纯只读**）

**问题**：1052 行净义务是**词法命中**的产物（`gits:`/术语名/ID 模式），其中已抽样 3 类被证伪为同名（`customerId` 库列、前端 OpenAPI DTO、`AC-004` 账号号段）。**未确认的 1038 行既不能当义务执行，也不能算已排除。**

**三层判定法（可机器化第一遍，人工只处理中间层）**：

| 信号 | 判据 | 第一遍处理 |
|---|---|---|
| **强** | 文件含**本体 IRI 字面量**（`gientech.com/gits/kno/`、`gits.bank.example/ontology/core#`）或 `owl:imports`/SPARQL/RDF 型语句，或位于**已确认消费面**（`modules/operational-ontology`、`adapters/semantic-jena`、`adapters/knowledge-filesystem`、`apps/api` 本体端口与规划器、`specs/semantic`、`specs/knowledge-architecture`、`specs/gk-ke`、`kert/src`、`kert/.../90_control`） | **判真义务**（待 Wave 2/3 执行） |
| **中** | 文件只出现裸术语名，但位于**合同/映射/物化链路**附近（`specs/*`、`scripts/*`、`scenarios`、KERT `examples/*`） | **逐条回源**（人工/会话） |
| **弱** | 文件只出现裸术语名且位于 DTO/UI/测试/日志面（`frontend/*`、`tests/*`、`adapters/persistence-relational`、`evidence/*`） | **判同名候选**（登记，不计义务；给出证伪依据或"待确认"） |

**优先面（占 59%）**：`apps/api` 229 · `specs/knowledge-architecture` 153 · `specs/gk-ke` 114 · `modules/operational-ontology` 80 · `kert/src` 38。

**产出**：
- `evidence/obligation-triage.csv`：文件 / 目录层 / 信号等级 / 判定（真义务·同名·豁免）/ 依据（`文件:行`）/ 责任 Wave；
- 净义务收敛报告（1038 → 真义务 N，附 N 的构成与依据强度分布）。

**DoD（缺一不可）**：
1. 全部**强信号**文件 100% 有判定（无"待判"）；
2. **弱信号**文件**不得**被判"真义务"而无 `文件:行` 依据（反向亦然）——防"一刀切"；
3. 变异复验：注入一个含本体 IRI 的文件 ⇒ 必须被判**强信号**；删依据 ⇒ 必须 FAIL；
4. 门禁 `wi_a2_obligation_triage`（+selftest）绿。

**风险与缓解**：若真义务数量远超预期（例如 >400），⇒ 立即回写 `WBS-RESTIMATE.md` 并在 `ORCHESTRATOR.md §5` 新增风险项（**不隐瞒量级变化**）。

---

### A2｜Wave 0 就绪度预检门禁化（**低成本、防"到点卡住"**）

**问题**：G-1 达成后才核对 Wave 0 输入锚点，若发现不符（哈希漂移、映射草案过期、ADR 未签）会白白损失窗口。

**产出**：`scripts/onto1_wave0_readiness.py`（`--gate` / `--selftest`），逐项给出 `READY` / `NOT_READY(<原因>)`：
复审包 01~14 哈希一致 · 基线 `705578d6…` 32/34/1 · `attribution-45-v2.csv` · 处置表零 `PENDING_TRIAGE` · D3 签署件存在性 · `LOOP.yaml.gate_state` 已离开 `RETURN_TO_HLD`（**这一项在 G-1 前必然 NOT_READY，属设计如此**）。

**DoD**：缺任一输入 ⇒ 门禁 FAIL（fail-closed）；`--selftest` 注入"哈希漂移/缺签署件"⇒ 必须 FAIL。

---

### A3｜两处门禁小修（**消除已登记的噪声与自述不一致**）

| 项 | 内容 | 依据 |
|---|---|---|
| B-4 | C-4 断言**范围收窄**为受控钉值文件（排除本 Loop 清单类产物） | `TL-DECISIONS-W-1.md` **D-2** |
| B-4b | 修 `onto1_namespace_collision_check.py` **头部自述与行为不一致**：头部写「C-4 可判定 → PASS（4 个钉值）」，实现已含 `C-4_PIN_FILE_UNFROZEN`（`:264`）会 FAIL ⇒ 头部须改为与行为一致（**否则读者会以为 C-4 通过**） | 本轮实测 |
| B-6 | 参照对齐守卫放行"**规则陈述行**"（或把 `loops/**` 纳入白名单），使红线规则可以正常书写，不必靠改措辞规避 | `TL-DECISIONS-W-1.md` **D-3** |

**DoD**：三项各自的门禁重跑，并在 `FAILURES.md` 对应条目追加"根因/变更/重跑结果"；C-2 的真实 FAIL **不因此转绿**（预期仍 fail）。

---

### 备选（低优先或需 Owner 授权）

| 项 | 何时做 | 阻塞 |
|---|---|---|
| 索引刷新（`INDEX_STALE(144)`） | 需 Owner 批准预算与时间窗 | 约 0.3M tokens（增量口径）/ 全量约 3.7M |
| O-D4-2 出口 B 的映射合同草案 | 待 C-2-c 授权 | Owner |
| CQ 夹具**执行**脚本骨架 | 现在做收益低（D2/D4 未签，CQ1/2/3 不可评） | 建议留到 Wave 4 前 |

---

## 2. 战线 B：Owner 动作（**只挡在人类手上**，已备 3 分钟操作卡）

| # | 动作 | 依据文件 |
|---|---|---|
| B-1 | 复审送审 5 项（指定评审人 / 批准发函 / 交付 / 设期限 / 回收签署页） | `docs/dispatch/ONTO1-送审Owner操作卡-V1.0.md` |
| B-2 | 任命 **公共语义 Owner**（+裁定词表 Owner 是否兼任） | `memory/OWNER_REQUESTS.md` §A |
| B-3 | 任命 **Integration Contract Owner** | 同上 |
| B-4 | 明确 **KERT 写权限归属**（Wave 3 需改 KERT 侧） | 同上 / D-7 |
| B-5 | **O-D4-2 出口裁定**（A 吸收 / B 并存+映射 / C 撤回） | `docs/dispatch/ONTO1-O-D4-2-差异补充决议草案-V1.0.md` |
| B-6 | D1~D4 各域 Owner 召集与截止（建议 2026-10-09 同批） | `docs/dispatch/ONTO1-D{1,2,4}-*` |

---

## 3. 战线 C：触发式预案（**到点即动，不临场想**）

| 触发 | 24 小时内动作 | 谁 |
|---|---|---|
| 复审结论到达 | ① 按《结论回收与门禁更新预案》受理判定；② 更新 `LOOP.yaml.gate_state` + `ORCHESTRATOR.md §0`；③ 通知全部角色；④ 判定 G-1 条件；⑤ 若退回 ⇒ 记 `FAILURES.md` 并按退回条目重排波次 | TL |
| **G-1 达成** | ① 跑 `onto1_wave0_readiness.py --gate` 并确认 **exit 0**（D-9 触发义务）；② **登记 `wi_a2_wave0_readiness` 门禁**并把 `--precheck` 语义更新为全项/标注冗余；③ 跑 `--precheck` 作回归基线；④ 启动 Wave 0（骨架冻结、基线 v2 入 EVIDENCE、检查表）；⑤ 更新 `wave: W0`、Baton | TL |
| **D3 签署**（同时触发） | ① **翻转 R5 判据**为"签署件存在 **且** 根域已填 **且** 非占位值"（现行判据届时会误报 NOT_READY）；② **回填 `D3_SIGNED_PATTERNS`** 实际签署件命名（否则 fail-closed 误红）→ 见 `memory/handoffs/TL-AUDIT-W15-PKG-A2.md` T-1 | TL + 语义架构 Owner |
| 角色任命到达 | ① 把 `handoffs/PSO-01-*` / `ICO-01-*` 移交为**就职基线**；② 启动 Wave 1（五条件）；③ 词表 Owner 裁定并入 Wave 1 | TL + 新 Owner |
| D3 签署 | ① 填 `namespaces.json` 根域（**首次写入**，须合同先行）；② `C-1b` 由 `NOT_EVALUATED` 转可评；③ 修 C-2 两处前缀冲突 ⇒ 碰撞门禁转绿；④ Wave 2 前置齐 | TL + 语义架构 Owner |
| D2 签署 | ① 生成**受控**候选映射（走 `CONTRACT_INDEX` → `make generate`）；② 补正负夹具与目标数断言；③ CQ3 从 `NOT_EVALUATED` 出列（注意 `mutuallyExclusiveWith` 零实例仍需夹具） | TL |
| D4 签署 | ① 投影合同进入受控（`specs/` → `CONTRACT_INDEX` → `generate`，执行方 = **Integration Contract Owner**）；② CQ1/CQ2 出列；③ SIM 台账启动 | TL + ICO |
| O-D4-2 裁定 | 按所选出口执行：A ⇒ 双侧联签 + GK-KE 全量回归；B ⇒ 起草映射合同 + 一致性门禁；C ⇒ `scheme` 编码规则 + CQ1 跨层查询方案 | TL |

---

## 4. 等待期红线（违反即 STOP 写 `BLOCKED.md`）

- **不预做** Wave 2 动作：不拆分本体、不迁移 IRI、不建 `namespaces.json`、不建 Shape、不改 `CONTRACT_INDEX`；
- 不改 `specs/**`、`generated/**`、`docs/dd/**`（封版）；
- **不写 KERT 仓**；不代签任何 Owner/委员会文书；不标 `DESIGN_APPROVED`/`ACTIVE`；
- 不把 AI 生成结论直接当**事实**：每条结论须带 `文件:行` 或哈希。

---

## 5. 批次定义与预估

| 批次 | 内容 | 性质 | 预估（量级） | 出口 |
|---|---|---|---|---|
| **W-1.5 就绪加固** | A1 + A2 + A3 | 只读分析 + 门禁加固 | A1 视分层而定（强信号面数百文件）；A2 ≤0.5 人日；A3 ≤0.5 人日 | 板面无新 fail + A1 分层报告落盘 |
| Wave 0 | 冻结与骨架 | 实施 | 0.5~1 人日 + 缓冲 | G0 |
| Wave 1+ | 见 `evidence/WBS-RESTIMATE.md` | 实施 | 待 G-1 | — |

> A1 的工期**不做承诺**（M-10）：它取决于"中信号层"的真实规模，第一遍机器分层后立即回写量级。

---

## 6. 需要 Owner 现在决策的 3 件事

| # | 决策 | 为什么需要你 | TL 建议 |
|---|---|---|---|
| 1 | 是否批准开工 **W-1.5 就绪加固**（尤其 A1） | 工作量大且属只读分析，但**不触任何红线**；也意味着推进的是"确定性工作"而非表演 | **批准**（A1 是 Wave 2 的真实前置） |
| 2 | 是否批准**索引刷新**（KERT 漂移 144 提交） | 涉及 LLM token 预算与时间窗；刷新前不得声称掌握全局设计 | 建议**批准并给窗口**（否则该限制会一路带到 Wave 2） |
| 3 | **O-D4-2 出口**选择（或授权代理） | 属实质语义冲突，只有 Owner/契约方能裁 | 建议 `B 过渡 → A 目标`；不建议 C |

> 三项之外的一切（送审 5 项、两个角色任命、D1~D4）**都不需要我再准备文书**，只差人的签字与发送。
