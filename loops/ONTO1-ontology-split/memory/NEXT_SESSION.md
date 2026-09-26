# ONTO1-ontology-split｜Next Session Baton

| 字段 | 值 |
|---|---|
| **Updated** | `2026-09-20T23:10:00+00:00`（TL：集成复验后编制下一步工作计划） |
| **下一步计划** | **`memory/PLAN-NEXT.md`**（W-1.5 就绪加固：A1 WI-A2 义务回源确认 / A2 Wave 0 就绪预检 / A3 门禁小修；+ 触发式预案 + 需 Owner 决策 3 项）——**接手第一件事就是读它** |
| **holder** | `tech_lead` |
| **packet** | `ONTO1-ontology-split` |
| **wave** | `W-1`（只读分析；Wave 0 及以后须 `DESIGN_APPROVED`） |
| **index_basis** | `memory/INDEX_BASIS.md` → gits `INDEX_FRESH` @71169042（0 drift）；**KERT `INDEX_STALE(144)`** |
| **do_not_start** | QA_PASS、REAL_E2E_PASS、BUSINESS_SIGNED、DESIGN_APPROVED、本体拆分、消费切换、正式重钉 |

短提示词：你是 `tech_lead`。读本 Loop 共享记忆与 `docs/dispatch/ONTO-SPLIT-本体四层落地执行计划-V2.0.md`，继续 Wave -1，只读，不得越界。

### TL 集成复验结论（2026-09-20，7 会话收工后）

- **落盘核验**：P-0~P-6 声称的交付**均已落盘**（D2/D3/D4 决策包、D1 申请件+空矩阵、P-1 五件 DRAFT、送审程序件、机读产物与脚本）；**未落盘 = 不存在的原则已核过**，无"口头交付"。
- **板面终态**：门禁 **31 个 = 30 pass / 1 fail**；唯一 fail = `wi_a4_namespace_collision`（**仅 C-2 两处真实前缀冲突**，**已知阻断**，见下"未关闭阻断项"）。`loop-guard` PASS；孤儿证据日志 = **0**（新增 `wi_evidence_board_check` 固化）。
- **W-1.5 状态（2026-09-21 收工）**：`pilot-a1`（A1）✅ **ACCEPT** → 已派 **PKG-A1b**（升格 65 行）；`pilot-a2`（A2）✅ ACCEPT_WITH_CONDITIONS（触发 T-1~T-3）；`pilot-a3`（A3）❌ **NOT_ACCEPTED（合并 7 条 C1~C7）**；`qa-w15` 第二轮 ❌ **NOT_ACCEPTED（Q-1/Q-2 BLOCKER + Q-4 MAJOR，已逐条裁定）**。审计报告：`memory/handoffs/TL-AUDIT-W15-PKG-{A1,A2,A3}.md`。
- **待办触发（T-1）**：**D3 签署时**必须同步 ① 把 R5 判据翻转为"签署件存在且根域已填且非占位值"；② 回填 `D3_SIGNED_PATTERNS`（实际签署件命名可能与先验枚举不同 ⇒ 否则 fail-closed 误红）。
- **本轮追加交付（TL 集成会话）**：
  1. `docs/dispatch/ONTO1-送审Owner操作卡-V1.0.md` —— 3 分钟操作版（填 4 名 / 勾 6 框 / 跑 3 条命令），把最硬卡点压成可执行三步；
  2. `docs/dispatch/ONTO1-O-D4-2-差异补充决议草案-V1.0.md` —— 两套外部标识模型的**字段级冲突定性** + 三出口（A 吸收 / B 并存+映射 / C 撤回）对比 + 建议路径 `B 过渡 → A 目标`；
  3. `scripts/onto1_zip_manifest_verify.py` + 门禁 `wi_zip_manifest_verify` —— 把"**发出的包 == 受检的包**"做成可执行证明（含篡改变异，已实测可检出）。
- **本轮新发现**：① `loop-guard` **看不见孤儿证据日志**（4 组检查曾执行未接线）⇒ 已按 D-1 接线并加固；② 参照对齐守卫存在"元陈述误判"⇒ D-3；③ C-4 对清单类产物误报 ⇒ D-2；④ **O-D4-2 为实质语义冲突** ⇒ D-8 升级差异决议。
- **裁定记录**：`memory/TL-DECISIONS-W-1.md`（D-1~D-8）。**下一 holder 第一件事就是读它。**

## 已交付（本会话，Wave -1）

| WI | 交付物 | 门禁 |
|---|---|---|
| Loop 骨架 | `loops/ONTO1-ontology-split/`（含不做事清单、角色板、索引依据、Owner 请求） | `memory-check` / `evidence-check` |
| WI-A1 | `scripts/onto1_attribution_rebuild.py` → `evidence/attribution-45-v2.csv` + `evidence/baseline-v2-manifest.json` | `wi_a1_baseline` PASS / `wi_a1_attribution_selftest` PASS |
| WI-A2 | `scripts/onto1_consumer_scan.py` + `_tests.py` + `evidence/consumer-scan-*.{jsonl,csv,json}` + 处置规则表 | `wi_a2_consumer_scan` PASS / `wi_a2_scan_mutation` PASS |
| WI-A2 报告 | `evidence/WI-A2-消费者扫描报告.md` | — |
| WI-A4 | `docs/architecture/ADR-ONTO1-namespace-neutral-iri-DRAFT.md`（**未预填根域**） | 待 D3 双 Owner 签署 |
| WI-A5 | `docs/dispatch/ONTO1-D2-产品Owner请求函.md`、`docs/dispatch/ONTO1-D4-数据Owner请求函.md`、`docs/architecture/ONTO1-SIM临时模拟权威声明草案.md` | 待签署（**今日已发出**） |
| WI-A6 | `evidence/CQ-FIXTURES-DESIGN.md` + `evidence/cq-fixtures/*.json` | 设计基线（夹具执行属 Wave 4） |
| WI-A7 | `evidence/WBS-RESTIMATE.md` | — |
| 基线锚定 | `contract_check` / `security_check` / `index_status` 三绿（日志在 `evidence/`） | PASS |

---

## W-1.5 批次收工记录（2026-09-20T23:55Z ~ 2026-09-21T00:05Z）

### 1. 本轮 TL 动作（全部已落盘）

| 动作 | 结果 |
|---|---|
| 审计 PKG-A3 | **NOT_ACCEPTED**（7 条条件）⇒ `memory/handoffs/TL-AUDIT-W15-PKG-A3.md` |
| 审计 PKG-A1 | **ACCEPT** + 4 项裁定（I-1/I-2/I-6/阈值）⇒ `memory/handoffs/TL-AUDIT-W15-PKG-A1.md` |
| 登记 A1 两门禁 | `wi_a2_obligation_triage` / `_selftest` ⇒ 板面 **30 = 29 pass / 1 fail** |
| 裁定 QA 第二轮 | Q-1 **修**（BLOCKER，主因是我 D-3 措辞）/ Q-4 **修** / Q-2 接受且记我主因 / N-6 归我 |
| 新纪律 | **D-11**（交付与证据绑定）· **D-12**（放行类要求必须附"不得放行"反例清单）· **D-3 补丁**（放行改**联合判定**，主题词移出标记表） |
| 新工具 | `scripts/onto1_gate_log.py`（哈希自证 + 退出码透传 + 缺失 fail-closed；自测 正例 0 / 反例透传 2 / 缺失 2） |
| 回写 | `evidence/WBS-RESTIMATE.md` §6（626 > 400 触发；升格后 691/361）、`memory/ORCHESTRATOR.md` §4/§5（+R-8~R-11）、`EVIDENCE.md`、`STATE.json`、本文件 |
| 失败账本 | `FAILURES.md` +4 条：`W15A3-02`（allow-list 只查声明）/ `W15A3-03`（缺钉值文件崩溃）/ `W15A3-04`（**D-3 漏检通道，主因在我**）/ `W15TL-05`（派工缺证据绑定要求）/ `W15TL-06`（哈希自证与守卫冲突）/ `W15TL-07`（TL 记账残留孤儿日志，已清理） |

### 2. 未完成项（下一会话**从这里开始**）

> **团队状态**：W-1.5 的 team `onto1-w15` **已结束**（`pilot-a1`/`pilot-a2`/`pilot-a3`/`qa-w15` 均不可寻址）⇒ 下列 T-4/T-5/QA 第三轮**转为下一 holder 的交接事项**，需重新组队或由新 holder 直接执行。

| # | 事项 | 负责 | 判据 |
|---|---|---|---|
| **T-4** | A3 **预验已通过**：仪器 `scripts/onto1_w15_acceptance.py` **8/8**（@ `collision=8c18b5b3` / `refalign=4d706978`，两次取样稳定）⇒ **C1~C4 到位**。**仍缺 C5~C7**：计数口径统一 / M12 夹具确认 / **冻结复交 + 日志自证 revision + 回执表**。完成后：以冻结哈希重跑仪器 + **重跑重记** `wi_a4_namespace_collision_selftest`（26 条用例）与 `wi_a3_reference_alignment`（`selftest 16/16`）的**陈旧证据**（R-11） | 新 holder（或重派 pilot） | 冻结 revision 下仪器 8/8 + 日志首行含 `# artifact=` + 重记后板面结论不变 |
| **T-5** | ✅ **已完成（2026-09-21T00:58Z，TL 代实现）**：I-6 升格 65 行 ⇒ 真义务 **691** / 待回源 **361**（`W3_CONSUMER_SWITCH` 381）；`--gate` 0 · `--selftest` **13/13**（M9 断言随裁定更新 + 新增 M9b-1 回退 / M9b-2 剥证据两条 **D-12 反例**）；新哈希 脚本 `f3603a24` / CSV `58671a90` / summary `f7dd5d4b` / 报告 `d93488c2`；A1 两门禁**已重跑重记**（日志自证 revision）。**下发给 Wave 2 的硬义务**：P0 面前 5 行必须优先抽检，推翻则置 `RULING_I6_UPGRADE_P0=False` 回退 | —（已闭环） | `memory/handoffs/TL-AUDIT-W15-PKG-A1.md` §8 |
| **QA 第三轮** | 独立 QA 重派（绑定 A1b/A3 复交后的**冻结哈希**）；QA 二轮自有结论亦为 NOT_ACCEPTED | TL 派发 | **不得记 `QA_PASS`**（Loop 仍有已知 fail） |
| **T-1~T-3** | A2 触发项（D3 签署时翻转 R5 判据 + 回填 `D3_SIGNED_PATTERNS`；G-1 达成触发；R6/R7 外 NOT_READY 视为漂移阻断 Wave 0） | TL + Owner | 见 `TL-AUDIT-W15-PKG-A2.md` |
| **T-6** | D-11 工具化：**新建或重跑**门禁一律套 `onto1_gate_log.py`（已用于 `wi_w15_a3_acceptance` 与 A1 两门禁）；既有 Wave -1 门禁按 Δ（`EVIDENCE.json.executed_at` + 制品哈希表）佐证 | TL | 新日志首行含 `# artifact=` |
| **T-7** | 新增纪律 **D-13 书写约束**已立（`FAIL-2026-09-20-W15TL-08`）：受限词表下**不得逐字引用禁句**（文档用方括号/省略，脚本运行期拼接，夹具只写临时目录） | 全体 | 新文书/夹具不再产生自伤违规 |

### 3. 如实声明（**不得计为通过**）

1. `wi_a4_namespace_collision` 仍 **fail**（exit 2）⇒ **Wave 2/3 退出门禁未满足**；
2. **C-4 只是收窄后 PASS**，其"删文件"路径**未封闭且会崩溃**（已交 A3，条件 C1/C2）；
3. **D-3 的 `rule_statement` 放行当前仍是漏检通道**（Q-1 未修）⇒ 该门禁的"合规表述零出现"结论**当前不可完全采信**；
4. `independent_qa` 仍 `pending`/`actor=null`（**无人代签**）；QA 二轮自身结论为 NOT_ACCEPTED；
5. 板面 29 个 pass 中，**`C-1b` = NOT_EVALUATED、`C-3` = 空转**（已在输出显式声明，不计为覆盖）；
6. TL 本轮新增 2 个脚本（`onto1_gate_log.py` 及此前 `onto1_pkg_audit.py` 等）⇒ **代码事实索引对 gits 侧转 `INDEX_STALE`**，刷新登记见 `memory/INDEX_BASIS.md`。
| **包 `W-1/review-submission`** | 送审程序包三件（操作清单 / 回收与门禁更新预案 / 包级 handoff）落 `memory/handoffs/`；重打包预演 16 项（仅 `/tmp`） | `wi_review_package_integrity` PASS（Attempt 2）/ `wi_review_package_selftest` PASS（Attempt 2） |
| **包 `W1-prep`（P-1 候任公共语义 Owner）** | 5 件 DRAFT 落 `docs/architecture/`：L1 八类术语定义稿（22 字段）/ R1~R9 修订版（内部规则·参照对齐名义）/ 命名空间 ADR 联签意见（U-1·U-3·U-4 选项与建议，不给结论）/ Wave 1 独立契约库五条件落地方案 / CQ1·CQ2 履职准备（拒绝码 + 目标数口径）；handoff：`memory/handoffs/PSO-01-公共语义Owner候选准备包.md` | **零执行**：未跑 generate、未改 `specs/`·`generated/`·`CONTRACT_INDEX`、未标 ACTIVE、未发布 IRI、未代签 |
| **包 `W-1/D2-pack`（P-4 D2 决策包）** | 决策包 `docs/dispatch/ONTO1-D2-产品Owner决策包-V1.0.md`（12 行最小勾选表 + 逐取值证据卡 + 交叉验证 + 零实例 + 两个一次性放行措辞）；机读 `evidence/d2-normalization-pack.json`（`24c6e24ccb58ad82`）+ `d2-{checklist-table,per-card-detail,cross-vocab}.md`；生成器 `scripts/onto1_d2_normalization_pack.py`；handoff：`memory/handoffs/ONTO1-W-1-D2-decision-pack-HANDOFF.md` | **非 Loop 门禁**（`LOOP.yaml`/`EVIDENCE.json` gates 未变）：`--gate` G1~G8 全 PASS（78 条回源 0 问题）/ `--selftest` M0~M5 全 PASS |
| **包 `W-1/D4-pack`（P-5 D4 决策包）** | 决策包 `docs/dispatch/ONTO1-D4-决策包-V1.0.md`：L1 八类逐术语确认表（每项 2~3 权威候选 + 禁止项 + `文件:行` 依据）/ `SourceIdentifier` 六必填 + `MISSING_SOURCE_IDENTIFIER` fail-closed / 授权投影合同草案（七要素，**NOT_EFFECTIVE**）/ SIM §2.2 三载体建议填法 + §2.3 四退出台账项 / CQ1·CQ2 A-Box 依赖说明 / 新增待决 **O-D4-1~7**；机读 `evidence/d4-l1-authority-candidates.csv`（32 行）+ `d4-pack.json` + `d4-pack-manifest.json`；门禁 `scripts/onto1_d4_pack.py`；handoff：`memory/handoffs/ONTO1-W-1-D4-pack-HANDOFF.md` | **已登记 Loop 门禁**：`wi_a5_d4_pack` PASS（Attempt 1）/ `wi_a5_d4_pack_selftest` PASS（Attempt 1，M1~M9 全拦下 + M0 对照） |

| **包 `W-1/D3-pack`（P-3 D3 决策包）** | 决策包 `docs/architecture/ONTOLOGY-SPLIT-D3-决策包-命名空间与解析机制-DRAFT.md`：D3-Q1~Q8 + **根域三类方案六维权衡**（ROOT-A 企业自有域 / ROOT-B 组织中立持久域 / ROOT-C 受控离线命名空间 + ROOT-D 混合变体，**不填字面量、不推荐**）+ 解析机制三方案与 **fail-closed F1~F7** + 逐术语映射草案（**87 行 / 迁移域 67**：`RETAINED 32`·`AUTHORITY_MOVED 4`·`REMODELED 23`·`TRANSFORMED 7`·`DEPRECATED 1`·新增 20）+ 双发布窗口与退役门 **P-1~P-11 + W1~W7** + §10 接口对齐；机读 `evidence/iri-mapping-draft.csv`（`cbf9c24d9e2eed1c`）+ `iri-mapping-draft-summary.json` + `namespace-known-defects.json`；脚本 `scripts/onto1_iri_mapping_draft.py`、`scripts/onto1_namespace_collision_check.py`；handoff：`memory/handoffs/ONTO1-W-1-D3-决策包-HANDOFF.md` | **非 Loop 门禁**（gates 未变）：映射草案 `--gate` PASS / `--selftest` 5/5；**碰撞检查 `--gate` FAIL(2) ⇒ 阻断发布**（C-2 两处真实前缀冲突未修）/ `--selftest` **16/16**（含元变异 M-元、全豁免 M10、自引用 M11、钉值未冻结 M12、未判定≠通过 M13、真实仓 FAIL 对照 M0b） |

## 下一步（按优先级）

1. **等**书面复审结论 → 到达即按《结论回收与门禁更新预案》V1.0（`memory/handoffs/ONTO1-W-1-结论回收与门禁更新预案-V1.0.md`）**先受理判定、再更新** `LOOP.yaml.gate_state` 与本文档，并通知全部角色（计划 §0）。
   - **发出前**：Owner 按《送审操作清单》V1.0（`memory/handoffs/ONTO1-W-1-送审操作清单-V1.0.md`）填送达位、重打包 zip（含 13/14）、自证「发出的包 == 受检的包」，建议期限 **2026-10-09**；
   - **红线**：TL 不得代发函、不得代签（`13` 末页 / `14` 签署表）；未收到签署件前**保持 `RETURN_TO_HLD`，Wave 0 及以后零动作**。
2. **角色缺口上报**（阻塞 Wave 1）：公共语义 Owner、Integration Contract Owner 任命请求见 `memory/OWNER_REQUESTS.md`。
   - 公共语义 Owner 侧**能力包已就绪**（P-1，5 件 DRAFT + handoff）；任命后可直接移交为就职基线。
   - **待裁 5 项（PSO 不得单方决定，建议并入 Wave 2 前置清单）**：O-1 `Product` 本体注释口径改写；O-2 `playedBy` 三选一（登记为第 37 条属性 / 匿名限制 / 从矩阵删括注）；O-3「放宽约束(minor)」与「IRI 迁移(major)」并发的级别判定；O-4 设计 §4.1「4 条 range 改指」vs 矩阵「5 条」；O-5 `memberOfGroup` domain 放宽为 `Party` 后隐式约束是否由 SHACL 补回（需 D4）。
   - 另有：规则稿 Q-1（`make conformance` 命令名是否改名）、CQ 稿 Q-2（业务日边界/时区）、Q-4（新字段是否入 `onto1_cq_fixtures.py --gate`）。
3. **WI-A3**：D1 标准文本跟催（目标 2026-10-09）；到手前**零国标符合性表述**、`REFERENCE-ALIGNMENT.md` 条款版不得发布。
4. **WI-A2 残留**：`obligations` 1068 行中 `FOLLOW_MIGRATION` 为候选义务，Wave 2 前须逐条回源确认（词法扫描 ≠ 语义确认，见报告 §4）。
5. **索引刷新**（`INDEX_STALE(144)`）：KERT 漂移 144 提交，超过阈值。刷新需 `/home/szf/ua-harness/ua_run.py`（本机 harness，全量约 3.7M tokens）或会话生成增量驱动。**刷新前不得声称掌握全局设计**；本会话所有 KERT 结论均来自直接读取 + 全文扫描（带 `文件:行`），未使用索引外推。
6. **D2（40 处悬空引用）**：决策包已就绪（`docs/dispatch/ONTO1-D2-产品Owner决策包-V1.0.md`，可勾选状态）。
   - **待产品 Owner**：逐行勾选 12 行（或采用包内 §7 选项 α / β 措辞）；并回答衍生问题——若 `SETTLEMENT_ACCOUNT` 判为账户关系，
     "前置是账户"是否需要**新增关系类型**（属 TL + 语义架构，合同先行）。
   - **TL 侧**：把决策包作为请求函**附件**送达（不修改已发出文书）；裁定到达后才可生成受控候选映射（走合同先行 + `CONTRACT_INDEX.yaml`），并补正负夹具与目标数断言。
   - **红线**：签署前 `requiresProduct`/`complementsProduct`/`mutuallyExclusiveWith` 三场景保持 `NOT_EVALUATED`（激活门禁硬阻塞）；
     且 `mutuallyExclusiveWith` **零实例**（13/13 空）⇒ 即使 D2 签署也**不**自动可评，仍需实例或受控夹具；**不得**用"0 目标 0 违规"包装为通过。
7. **D4（A-Box 权威）**：决策包已就绪（`docs/dispatch/ONTO1-D4-决策包-V1.0.md`，可勾选状态）。
   - **待数据 Owner + 业务 Owner 会签**：① 八类逐项确认或改（每项给出「最终具名系统」）；② `SourceIdentifier` 六必填批准；③ 授权投影合同批准（批准≠生效）；④ 路径选择（直接签正式矩阵 **或** 先签 SIM 临时声明，载体见包 §4.1）。
   - **产品身份部分同步交产品 Owner（D2）**：D4 侧只需确认否定命题「产品身份 A-Box ≠ KERT 产品卡」。
   - **TL 侧**：把决策包作为请求函**附件**送达（不修改已发出文书）；签署件到达后按包 §8 受理并回填；合同草案进入受控须走 `specs/` → `CONTRACT_INDEX.yaml` → `make generate`（执行方 = Integration Contract Owner，**未任命**）。
   - **红线**：签署前投影合同**不生效**、`CustomerRole`/`GroupMembership` 场景与 CQ1/CQ2 保持 `NOT_EVALUATED`；**不得**把 GITS 运营库或 KERT workspace 登记为正式权威；**不得**代签；SIM `ledger_status` 不得提前启动（门禁 C8 拦下）。
   - **待裁 7 项（O-D4-1~7，见包 §6）**：其中 O-D4-1（`Party`/`Organization` 类级取值不可执行）、O-D4-2（与 GK-KE `core.ExternalIdentifier` 未对齐）、O-D4-3（CQ 夹具已隐式预置来源）为 MAJOR；O-D4-7（集团族零具名源系统）须由数据 Owner 具名。

## D3-pack 待裁 6 项（A-1~A-6，全部在人类/Owner/TL 手上，分析角色未代答）

| # | 待裁 | 谁裁 | 依据 |
|---|---|---|---|
| A-1 | 根域类别（`ROOT-A/B/C/D`）、根域字面量、归属治理、解析机制、**持久性承诺** | 语义架构 Owner + 域名 Owner | D3 决策包 §3 / §4 / §8 |
| A-2 | 窗口与退役门参数 `P-1~P-11`（含冻结期 ≥14 天、回滚演练、参数落地到 L4 注册表） | 公共语义 Owner（**待任命**） | D3 决策包 §6 |
| A-3 | `J-1`「权威层迁移是否算语义变更」⇒ 决定 4 项 `RETAINED_AUTHORITY_MOVED` 能否用 `equivalentClass`（默认不放行） | TL | **✅ 已裁 D-4：不放行**（一律 `closeMatch` + `AUTHORITY_MOVED`） |
| A-4 | `J-2` 是否存在可升级为 SKOS `exactMatch` 的 `REMODELED` 项（当前一律 `closeMatch`，`exactMatch` = NOT_GRANTED） | 公共语义 Owner | **✅ 已裁 D-5：维持 NOT_GRANTED**（放行权属待任命的公共语义 Owner） |
| A-5 | **接口差异 3 处**：脚本命名（本包 `onto1_namespace_collision_check.py` vs 需求规格提案 `onto1_iri_collision_check.py`）/ 退出码语义（`0·2·3` vs `0·1`）/ 输入源（映射草案 vs `namespaces.json`） | TL + 候任 Integration Contract Owner | **✅ 已裁 D-6**（以实现为准 / 保留语义化三值 / 未签期间用映射草案 + 缺输入 fail-closed） |
| A-6 | 是否把 `wi_a4_*` 登记为 Loop 门禁（本包**有意未接线**；且当前 `--gate` 为 FAIL，登记前须先确定"红测如何记账"） | TL | **✅ 已裁 D-1 并执行**：4 组（8 个）门禁已登记；红测按真实退出码记账、**禁止 fail→inconclusive**；当前碰撞门禁记 `fail` |

> **必须先看的三条硬事实**：① 碰撞检查当前 **FAIL ⇒ 阻断发布**（两处真实前缀冲突未修，`ADR-ONTO1 §5.4`「必须先修」）；
> ② `C-1b` 为 **`NOT_EVALUATED`**（D3 未签 ⇒ 根域未定）⇒ D3 解除证据中的"碰撞检查绿"**当前不可得**；
> ③ **登记 ≠ 豁免**（2 处冲突已登记修复义务，但登记不会使 `C-2` 转绿，"全部冲突均已登记"本身也判 FAIL）。

## 未关闭阻断项（**必须带走**，不得静默消失）

| # | 阻断项 | 当前状态 | 修复责任 Wave | 证据 |
|---|---|---|---|---|
| B-1 | **两处真实前缀冲突未修**（`gits:` 双绑定 + `gits:Product` 同名不同 IRI） | `wi_a4_namespace_collision` = **fail**(exit 2) | **Wave 3**（`products.ttl:1/:10/:15`） | `evidence/wi_a4_namespace_collision-*.log`；`ADR-ONTO1 §5.4`「必须先修」 |
| B-2 | `C-1b` 集合互斥 = **NOT_EVALUATED**（D3 未签 ⇒ 无具体新 IRI） | 未决 | D3 签署后 | 同上 |
| B-3 | `C-3` import closure 单版本 = **空转通过**（本体无 `owl:versionIRI`/`owl:imports`） | 空转，**不计为覆盖** | Wave 2（引入 versionIRI 后才有真值） | D3 决策包 §7.3-4 |
| B-4 | `C-4` 对清单类产物的**已知误报** | 待收窄实现（D-2） | 下一 holder（小改动） | `FAILURES.md` FAIL-2026-09-20-05 |
| B-5 | **O-D4-2 实质语义冲突**：GK-KE `core.ExternalIdentifier` vs ONTO1 `SourceIdentifier` | 已升级**差异补充决议**（D-8） | Owner/契约方裁定 | `specs/gk-ke/v1/examples/l1-1/positive/SemanticPackage.json:178`；`attribution-45-v2.csv:9` |
| B-6 | 参照对齐守卫的"元陈述误判" | 已用措辞规避；长期放行规则待做（D-3） | 下一 holder | `FAILURES.md` FAIL-2026-09-20-04 关联；`LOOP.yaml` 原 165 行 |
| B-7 | KERT 仓 3 文件写入**归属未确认** | 登记待追认，**不回滚**（D-7） | KERT 维护方 / Owner | `FAILURES.md` FAIL-2026-09-20-06 |

> `loop-guard` **看不到**孤儿证据日志（只比对 LOOP↔EVIDENCE 两集合）⇒ 下一 holder 收工前请手工核对
> "`evidence/*.log` 中是否有未登记门禁"；已建议把该检查固化（见 D-1 第 3 点）。

## 已知边界（不得越界）

- 本环境 `Leibniz-KERT` 仓**只读**；Wave 3 的「L1 副本 + L2 本体」改动需 KERT 维护方执行或 Owner 授权写权限。
  - **补充（TL 集成会话，D-7）**：本窗口内实测 KERT 侧有 3 个 ONTO1 相关文件被写入（其中 `ONTOLOGY-SPLIT-DESIGN-V1.1-REVIEW.md` 已被改写为**指针**、自述权威收敛至 GITS 仓）。**归属未确认**，已登记待追认、**不回滚**。⇒ 在本工作区**存在其它写者**的前提下：ONTO1 的结论一律以**哈希与回源**为准，**不得**用 mtime/文件存在性推断归属；KERT 侧未追认前不再新增 ONTO1 相关写入。
- `docs/dd/` 下有未跟踪文件（`REVIEW.zip`、`GITS-KERT_*.md`），**禁 `git add .`**。
- 本次未执行 `make generate`（Wave -1 只读）；`generated/` 未改。
- **阻塞规程**：可自愈问题按阶梯协议（自愈 → 降级 → 回退）自主处理，**不停工询问**；仅四类硬阻塞（缺凭据 / 需求冲突 / 方向性变更 / 安全隐患）+ 自愈耗尽才写 `memory/BLOCKED.md` 并停止（规程见 `memory/PROTOCOL.md`）。**当前无 BLOCKED 事项**（不预建占位文件）。

---

## QA 第三轮结论与修复（2026-09-21T01:25Z）

**QA 第三轮（`qa-w15r`）结论 = NOT_ACCEPTED**，报告 `memory/handoffs/INDEPENDENT-QA-W15R-2026-09-21.md`（sha256 `3283122d2287f636…`）。
- **通过**：R2（5/5 日志自证哈希 == 磁盘；全量 31 门禁 `output_sha256` 31/31 相符）· R3（四例在其**自建自包含沙箱**复现，且加控制组排除仪器假阳性）· R4（红线 0、KERT 零写入、板面 31=30/1、`independent_qa` 未被预填）· R1 事实层（691/361、P0 65/65 逐条回源 `import` 行，bad=0；自建 3 变异 + 还原哈希逐字回到 `58671a90`）。
- **BLOCKER**：`G5` 的「`RESOLVES_TO_ONTOLOGY_PKG` 标签二次校验」**缩进出循环 = 死代码**，对 65 行 P0 覆盖 **0/65**（TL 以"65 行包名全改不存在 ⇒ 命中 0、仅剩 1 条 G7"独立实证）。**并暴露 TL 自证链断裂**：审计报告曾以"引用既有二次校验"为由批准放宽，而该防线是死的。
- **已修**：块移入循环（逐行、覆盖全 tier）＋ **M9b-3**（命中数 == 行数）＋ 夹具 P0 行移至非末位；退化副本 ⇒ M9b-3 FAIL（13/14），修复版 **14/14**、`--gate` 0。
- **其余闭环**：U-6 E2 覆盖全部 `*.log`（63→67）＋ M4；U-7 白名单通配收敛精确名 ＋ E5/M5/M5b；U-8 按包分层抽样（55/6/4；6 行 `action.domain` 属 `modules/human-action`，**须单独确认**）；U-9 文档更正。
- **新记账**：`W15TL-09`（死代码 + 自证链断裂）· `W15TL-10`（板面**自指重记陷阱**：重记前须把两个板面门禁的当前日志一并入白名单）· `W15TL-11`（E2 前缀制盲区）。
- **仍未关闭**：U-4 C-2（Wave 3）· U-5 A3 侧 C5/C7 字面未完成（作者已下线）· U-10 KERT 历史写入归属待追认 · **QA 第四轮复验**（已请求）。

---

## W-1.5 批次收束（2026-09-21T02:15Z）

**结论**：PKG-A1 = **ACCEPT**（+ PKG-A1b 完成）· PKG-A2 = **ACCEPT_WITH_CONDITIONS** · PKG-A3 = **NOT_ACCEPTED**（C7 字面未完成，作者已下线）· 独立 QA（`qa-w15r` 第二~七轮）= **NOT_ACCEPTED**（共关闭 U-1/U-2/U-6/U-7/U-11/U-12/N-8/C5；对收束声明逐条核验通过）。

**板面**：31 门禁 = **30 pass / 1 fail**（唯一 fail = `wi_a4_namespace_collision`，仅 C-2，属 Wave 3）。
**自证纪律**：含自证行日志 **9/9 哈希 == 磁盘、0 不符**；**D-11 之后缺自证 = 0**（22 份无自证全部早于 `earliest_wrapper = 2026-09-20T15:46:13Z`）；孤儿日志 0；`registered ∩ allowlisted == 0`。

**本批新增纪律（下一 holder 必读，均在 `memory/TL-DECISIONS-W-1.md`）**：
D-11 交付与证据绑定（post-DONE 冻结 / 日志自证 revision / 审计前确认哈希稳定 / **崩溃 ≠ FAIL**）· D-12 放行类须附"不得放行"反例 · D-13 受限词表书写纪律 · D-14 重记与修复尝试的预算语义 · **D-15 禁止再加码上限**（出口只能是 ①工具意图区分 或 ②ADR 级决定）· **D-16 权威值变更须用宽口径内容检索判据**。

**盲区账**：`memory/ORCHESTRATOR.md` §7.2 的 **G-1 ~ G-11**（新增 G-5 死代码断言 / G-6 E2 前缀制 / G-7 白名单通配 / G-8 D-11 点状落地 / G-9 自指重记陷阱 / G-10 权威值残留 / G-11 预算语义）。

**未关闭项（非 Wave -1 可动）**：
① **C-2**（Wave 3；`RETURN_TO_HLD` 有效期内**不得**改 `specs/` 权威制品）——判据 `scripts/onto1_namespace_collision_check.py --gate` ⇒ `[C-2] FAIL（实测 2）`；
② **C7 字面**（`grep -c 'artifact=' evidence/a3fix-after-*.log` ⇒ 4 份全 0）；
③ **U-8**（`com.gien.gits.action.domain` 6 行实位于 `modules/human-action`，Wave 2 **按包抽样** 55/6/4 每包 ≥3 行）；
④ **U-10**（KERT 历史写入归属待追认）。

**下一 holder 起手三件事**：1) 读本文件 + `TL-DECISIONS-W-1.md`（D-1~D-16）+ `ORCHESTRATOR.md` §7；2) 核对 `EVIDENCE.json` 与板面（**31 门禁、唯一 fail = collision**）；3) **按 D-15 先查板面门禁预算（board / board_selftest 各剩 1 次）**，再决定是否需要重记。

**门禁位置未变**：`RETURN_TO_HLD` 仍有效 ⇒ **Wave 0 及以后禁止开工**；本文档全部动作为 **Wave -1（只读分析 + 门禁加固）**。

### 2026-09-21T02:30Z｜新增 Owner 面向交付物

- **`docs/dispatch/ONTO1-Owner审核总清单与证据包-V1.0.md`**：把 `OWNER_REQUESTS.md` 全部待审项收敛为单一入口，每项含 **背景 + 证据（文件/哈希/门禁）+ 判据 + 回执模板**，按"能解开什么"排序（P0 复审结论 + 角色任命 → P1 D3/D2/D4 → P2 D1/O-D4-2/追认项 → P3）。附：给不同 Owner 的阅读顺序、材料清单（已就绪 vs 待 Owner 产出）、§9 未决期间项目侧**已执行**的自我约束清单、§10 非声明。
- 归档：`memory/OWNER_REQUESTS.md` 顶部已加入该包的**导航指针**（权威登记仍以 `OWNER_REQUESTS.md` 为准）。
- **过程中触发一次 D-13 同类复发**（`W15TL-14`）：新文书以单字「未」表达红线承诺 ⇒ 守卫判违规（`refalign --gate` exit=1）⇒ 改为表内标记（`不发布`/`禁用`）后 **exit=0、0 违规**；并**连带重记** `wi_a3_reference_alignment`（旧日志入白名单留证），使登记证据绑定当前时点（`candidates=164 / allowed=85`）。

---

## Owner 决议 O-01~O-13 落地（2026-09-21T03:25Z）

**决议文本**：`docs/dispatch/ONTO1-Owner决议建议与授权边界-V1.0.md`（人类 Owner 会话确认采用；**该文件 §四 签署栏仍留空**）
**落地台账**：`memory/OWNER-DECISIONS-2026-09-21-LANDING.md`（逐项：生效范围 / TL 已做 / 仍阻塞 / 证据 / 非声明）

**已落地（记录项）**：O-01 批准发起书面复审（目标 2026-10-09；四角色评审、秘书处不投票不代签）· O-02/O-03 临时任命 PSO/ICO（`INTERIM`，**不得兼任独立 QA**）· O-04 词表 Owner 双责任单语义 Owner · O-05 D3 只批政策不批根域 · **O-06 40 处产品关系全部 `QUARANTINED_UNRESOLVED`**（`evidence/product-relations-quarantine.json`）· **O-07 D4 选 SIM 路线**（3 具名载体 + 六必填 + freshness 相对 `scenarioAsOf`；合同仍 `NOT_EFFECTIVE`）· **O-08 O-D4-2 选 B 过渡 → A 目标** · O-09 D1 批准获取但移出设计基线 · O-10 维持保守映射政策 · O-11 D-7 原则追认（须三文件具名 + 哈希 + 来源 + 维护方确认）· **O-12 refalign 整改已完成**（三项 + 验收证据见台账 §三.1）· O-13 Wave 解锁表写入 `LOOP.yaml.gate_state`。

**项目门禁不变**：`RETURN_TO_HLD`；`DESIGN_APPROVED=NO` · `WAVE_0_STARTED=NO` · `independent_qa=pending/actor=null`。

**仍待人类/外部（唯一通路）**：① 填入具名评审人并发函、收回签署页 14；② 域名/基础设施 Owner 根域联签；③ 产品 Owner 逐条分类 40 处；④ KERT 维护方确认三文件；⑤ **独立 QA 派出**；⑥ 生产数据 Owner 对真实银行源系统的确认。

---

## 下一步路线图（Owner 最终决议 2026-09-21 生效后）

**唯一解锁通路（别无他径）**：`有效签署页 14` → 过 **V1~V9** → `DESIGN_APPROVED` → Wave 0 解阻 → D3 联签 → D2 分类 → …… → `OWNER_ACTIVATED`。
**凡未走完本通路者，门禁一律不动**（不得因自检、`refalign exit=0`、Owner 发函而提升）。

### P0 —— 只有 Owner 能做（我做不了，也不代做）

| # | 动作 | 现状 | 出口 |
|---|---|---|---|
| P0-1 | **任命并登记四个评审角色**（主席 / 本体语义架构 / 数据治理 / 集成架构） | `ROLE_BOARD.review_panel.status = TO_BE_APPOINTED`（名字栏空） | `review_panel.status → APPOINTED` + 具名 |
| P0-2 | **批准并发出送审函（13）** + 交付自含包 | 包已就绪（`onto1_review_package: PASS`，MANIFEST 14 件，13/14 可签署载体齐备） | 发函回执 |
| P0-3 | **明确回收期限并催办**（建议 2026-10-09） | `13` §四 待填 | 期限入 `13` |
| P0-4 | **接收并登记有效签署页 14**（评审组**分别**签署） | 空 | 归档 `docs/review/` |
| P0-5 | **依有效结论决定后续门禁动作** | 待 | `gate_state` 更新（或退回） |

### P1 —— 我（delegated technical executor）可立即做，不越五项禁止

| # | 动作 | 为什么现在能做 | 判据 |
|---|---|---|---|
| P1-1 | **发函前硬条件复演**：重打包 → 双清单 `diff` ⇒ `SENT_PACKAGE_IDENTICAL` → `onto1_review_package_check.py --gate` | 纯技术准备，产物只落 `/tmp`，**不动已发制品** | 两份 sha256 清单逐字一致 + `exit=0` |
| P1-2 | **把 V8/V9 工具化**：签署页校验器（四角色**分别**签署才可判 `ARCHITECTURE_COMMITTEE_APPROVED`；仅 Owner 单签 ⇒ `OWNER_REVIEW`；非签署理由申请提升 ⇒ 拒） | 属"裁定建议 + 判据准备"，**不签署、不裁决** | selftest 含**反例**（单签 ⇒ 不得判委员会）（**D-12**） |
| P1-3 | **自含材料与回执模板就绪化**：操作卡 / 总清单 / 回执模板按四角色分工重排（已按决议对齐，补"每位评审只看自己那几项"的分工索引） | 材料汇总 | 四角色各自不超 1 页 |
| P1-4 | **W-1.5 遗留收口（T-4 余项 C5~C7）**：计数口径统一 · M12 夹具确认 · **冻结复交 + 日志自证 revision**；完成后**重跑重记** `wi_a4_namespace_collision_selftest` 与 `wi_a3_reference_alignment`（**陈旧证据**，R-11） | 原 `pilot-a3` 团队已结束 ⇒ 需**新 holder 或重派 pilot** | 冻结哈希下仪器 8/8 + 日志含 `# artifact=` + 重记后板面结论不变 |
| P1-5 | **QA 第三轮重派**（须绑定冻结哈希；**不得记 `QA_PASS`**） | 需**新建团队**（原成员已不可寻址） | QA 报告绑定哈希，结论独立 |

### P2 —— 外部卡点（我只能登记与跟催）

`D3 根域双 Owner 联签` · `D2 产品 Owner 40 处逐条分类`（现全 `QUARANTINED_UNRESOLVED`）· `KERT 维护方确认三文件` · `生产数据 Owner 确认真实银行源系统` · `独立 QA 派出`（`independent_qa=pending/actor=null`）· `D1 国标正式文本获取`（WI-A3，目标 2026-10-09，**移出设计基线**）。
> 注：**A-1/A-2（PSO/ICO 任命）** 已由 Owner 临时兼任（`INTERIM`）满足**名义**要求；但 Wave 1 仍须 `O-02/O-03` **人类确认生效**，不得据此开工。

### P3 —— 签署页到达后的三分支（条件性，预案 §1~§4 已就绪）

1. `ACCEPTED + DESIGN_APPROVED` ⇒ 更新 `LOOP.yaml.gate_state` + `ORCHESTRATOR.md §0` → 通知全部角色 → 填 `G-1` → 按序解阻 Wave 0/1；
2. `ACCEPTED + PASS_WITH_REQUIRED_CHANGES` ⇒ 记未关闭项表 → 修设计 → **Wave 0 仍不开**；
3. `RETURN_TO_HLD` ⇒ 记 `FAILURES.md` → 重排波次 → 保持只读；
   另：`INVALID_RETURN`（任一 V1~V9 不过）⇒ **退回补正 + 门禁零动作** + 程序性记录（先记后办）。

### 不变量（每一轮都要核）

`RETURN_TO_HLD` · Wave 0 及后续 `BLOCKED` · `independent_qa=pending/actor=null` · C-2 / `wi_a4_namespace_collision` 未关闭（板面 **31 = 30 pass / 1 fail**）· 受控目录 `generated/ specs/ docs/dd/` 零改动 · 基线 `gits-core.owl.ttl` 哈希 `705578d6324abd0c` · 我不签署、不批准激活、不单人置 `ACTIVE`、不充当独立 QA、不把建议写成权威事实。

---

## 实施进度更新（2026-09-21T05:10Z，Owner 决议「开发与正式批准分开」后）

**执行状态**：`OWNER_AUTHORIZED_SIM_REMEDIATION_AND_IMPLEMENTATION`（`LOOP.yaml.gate_state.execution_state`）

| 项 | 状态 | 证据 |
|---|---|---|
| **C-2 命名空间冲突** | ✅ **已修复**（术语/实例命名空间分离；**13 实例 IRI 未迁移**；未引入 `equivalentClass`；T-Box 未动） | `wi_c2_fix_verify` 7/7 + selftest 6/6；前后哈希 `e70bbe45…`→`b8875c16…` |
| **D2 产品关系分流** | ✅ **已实施**：**28 已解析 / 12 隔离**（`CASH_MANAGEMENT` 未映射）；CQ3 只报 28-12 | `wi_d2_relation_resolution` 7/7 + selftest 6/6；`evidence/product-alias-resolution.json` |
| **D3 根域** | ✅ 临时口径已登记：`PROVISIONAL_SIM_LEGACY_NAMESPACE`（不再阻塞 SIM 开发） | `LOOP.yaml.gate_state.provisional_sim_legacy_namespace` |
| 板面 | **35 门禁 = 34 pass / 1 fail**（唯一 fail = `wi_a4_namespace_collision`，语义 **INCOMPLETE/exit 3**，C-1b 待 D3） | `EVIDENCE.md` §1 |
| 实施报告 | `evidence/C2-D2-SIM-REMEDIATION-REPORT.md` | — |

**上述「下一步路线图」的 P0-1~P0-5 仍然有效，但其适用范围已收窄**：它们现在只决定**能否声明 `ARCHITECTURE_COMMITTEE_APPROVED` / 正式设计基线生效 / 对外发布 / 生产激活**，**不再阻塞 SIM 开发、缺陷修复、自动化测试与迁移验证**。

**剩余真实技术阻塞（3 条）**：

1. **B-1** `scripts/gk17_prodcard_to_rdf.py:31,37` 仍按旧口径生成 `products.ttl` ⇒ **重新生成会复现 C-2**。该脚本属 **GK17 Loop 产物（跨写域）**，需指派 GK17 侧同步（改法与 `C2-D2-SIM-REMEDIATION-REPORT.md` §1.1 一致）；**TL 未擅自改**。
2. **B-2** D3 正式根域未联签 ⇒ 新 IRI 前缀无法定稿、碰撞门禁 `C-1b` 无法判定（当前 `INCOMPLETE`）。
3. **B-3** 12 条关系引用无产品归属 ⇒ 只能隔离（**不得**强行映射；`CASH_MANAGEMENT` 可能是产品类别/能力概念）。

**事故披露**：`FAIL-2026-09-21-W15TL-15` —— 我清理孤儿日志时误读白名单键名（`path` vs `file`），**误删 53 件白名单证据**；已从冻结沙箱副本逐字恢复 **32 件**，其余 **21 件**（我自己的重复 attempt 日志，已被当前登记日志取代）永久丢失。新增 **D-14** 纪律：先 dry-run 后删除 · 白名单按 `file` 键 · 孤儿首选"登记或加白" · 删除前留副本。

---

## 第二轮 Owner 决议执行（2026-09-21T05:10Z，开发/正式批准分开）

- **C-2 = `CLOSED`**：生成器 `scripts/gk17_prodcard_to_rdf.py` **配置驱动**整改完成（`projection-config.json` v1.0.0）；删除手修件后重生，**两次生成字节一致**（`e1b6e09e…`），验收 7/7，13 实例 IRI 未迁移；GK17 门禁已重跑 pass。
- **D2 = 28 条 SIM 投影 / 12 条隔离**：`specs/knowledge-architecture/instances/product/sim/product-relations.SIM.ttl`（`simulationOnly=true` + 逐条溯源 + 幂等 + 配置驱动别名表）；正式关系发布 `NOT_AUTHORIZED`。
- **板面三态**：`PASS=40 · FAIL=0 · PENDING_EXTERNAL_AUTHORITY=1 · PRODUCTION_ACTIVATION=BLOCKED`（`inconclusive` 不计 FAIL）。
- **事故闭环**：编号 **`W15TL-16`**；证据包 `evidence/log-incident-W15TL-16.json`；新工具 `scripts/onto1_log_hygiene.py`（四闸 + 反例 5/5）。
- **剩余真实阻塞**：D3 正式根域联签（只阻塞对外发布/持久解析/外部契约/生产激活）· 12 条关系无产品归属。

---

## 独立架构复核与 R2 重封（2026-09-21）

复核件：`docs/dd/ONTO1_准备包独立架构复核_20260921.md`（架构顾问；**不代替独立 QA 签署**）

| 发现 | 处理结果 |
|---|---|
| F-01 制品保留「处置率 100%」 | ✅ 生成源数据驱动 + 新门禁 P7；制品已重生成 |
| F-02 自检只比脚本常量 | ✅ 改解析受控源；**设计表/映射表/归属矩阵各一处真实变异均触发 FAIL** |
| F-03 入口引 V1.2 且称 32 类为 L1 候选 | ✅ 改引 V2.0 §4.2 + 明示「来源盘点(32) ≠ L1 候选(8)」 |
| F-04 48 项 vs 封包 45 项 | ✅ **同快照重封 R2**（48/0/1/共 49 三处一致）；旧包留档；门禁改名去歧义 |
| F-05 扫描/KERT 归因不可独立确认 | ✅ 原始 `consumer-scan-hits.jsonl` + 扫描脚本入包；改名 **KERT 差异观察（归因未核实）** |

**R2 包**：`docs/review/ONTO1-PREP-INDEPENDENT-REVIEW-20260921-R2.tar.gz`
SHA-256 `83a3c08a3586116c57ba7888b7b6984c4d3680cc712e153bacb22b510169d995`
**旧包（历史快照）**：`ONTO1-PREP-INDEPENDENT-REVIEW-20260921.tar.gz`，SHA-256 `700e2b373eaa393b…`

**边界（F-05）**：扫描覆盖率与逐条处置完整性需在有双仓源码环境复算；KERT 归因需本轮开始时的 KERT 工作区哈希快照方可闭合。
**状态**：`RETURN_TO_HLD` · Wave 0–3 `BLOCKED` · 正式拆分 **0/691** · `independent_qa` **pending**。

---

## SIM 整改第一轮（波 1/波 2）完成记录（2026-09-21，无人值守执行）

- **板面**：62 = **61 pass / 1 inconclusive**（唯一 inconclusive = `wi_a4_namespace_collision` exit 3，`C-1b` 待 D3）。
- **A-1**：`wi_a2_disposition` 8/8 + 反例 7/7；412 行终局处置 = `FOLLOW_MIGRATION` 336 / `EXEMPT_NON_ONTOLOGY_HOMONYM` 53 / `CONTROL_PLANE_REQUIRED` 20 / `CLOSED_BY_OWNER_DECISION` 3；台账 `evidence/prep/a2-disposition-ledger.{csv,json}`。
- **A-2**：`wi_a3_closeout` 8/8 + 反例 6/6；冻结 composite `a18719778d261448`；四份 `a3fix-after-*.log` 首行 `# artifact=`；两处陈旧证据重记（含 D-15 开启 `Revision epoch 1`）。
- **A-3**：`wi_d2_relation_resolution` **11/11** + 反例 **10/10**（G8/G9/G10/G11 新增；修掉仪器内一处计数口径 bug）。
- **A-4**：`wi_a4_sim_migration_verify` 7/7 + 反例 7/7；`evidence/prep/sim-migration-verify.json`。
- **A-5**：`wi_a5_l2_patch_plan` 4/4 · `wi_a5_l3_load_fixture` 6/6 + 反例 6/6；`evidence/prep/L2-KERT-PATCH-PLAN.md`。
- **A-6**：GK17 `ref_anchor_check` / `triple_consistency_check` 重记；GK17 板面 11 = 9 pass / 2 fail（两 fail 为既有 `backend_test`/`frontend_test`，日志日期 2026-09-15，与本次变更无关）。
- **A-7**：`wi_a7_signature_verify` 5/5 + 反例 5/5（四席同一自然人 ⇒ `OWNER_REVIEW_ONLY` 且禁记委员会批准）。
- **波 3**：`memory/DISPATCH-WAVE3-PROMPTS.md`（各角色可直接粘贴的派工提示词）。
- **纪律**：新增 **D-19**；路径事故（误写工作区外）已清理。

---

## 独立 QA（波 3）结果与 TL 逐条裁定（2026-09-21）

- **QA 报告**：`memory/handoffs/INDEPENDENT-QA-W3-2026-09-21.md`（10 项：3 ACCEPT / 6 ACCEPT_WITH_CONDITIONS / 1 NOT_ACCEPTED）。
- **NOT_ACCEPTED 项**：项 9「断言强度声明」——F-2/F-3/F-4/F-5 四处判据在**真实路径恒真**。
- **TL 裁定书**：`memory/handoffs/TL-ADJUDICATION-QA-W3-2026-09-21.md`（12 条发现**全部接受**，逐条处置 + 复算命令）。
- **已修要点**：派生取代字面量（L6/M6/M7/G7）· A5 独立复算（53 行/188 处/0 违例，与 QA 数字一致）· M5 显式不计为覆盖 ·
  P4 死逻辑修正 + 真实路径反例 · 位移落点改非注释非 docstring 行（`:37`/`:39`）· `board_expression` 复算 ·
  纪律改号 **D-18/D-19** · 备份入仓 `evidence/archive/a3closeout-backup/`。
- **失败账**：`FAIL-2026-09-21-W15TL-19`（恒真判据）· `W15TL-20`（治理与文书类）。
- **QA_PASS 未记录**：板面 1 inconclusive（C-1b 待 D3）+ `RETURN_TO_HLD` + 项 9 待第二轮。
- **下一步**：QA 第二轮复验（清单见裁定书 §三）。

---

## A-8｜SIM 通道演练场（2026-09-21，下一步 SIM 侧实现）

**动机**：A-4 只做『判读』（哪些文件引用旧命名空间），**没有真跑一次切换**。本轮把它推进为可执行演练。

| 项 | 数值 |
|---|---|
| 迁移行分类 | **同名保留 51 · 改名 7 · 非 IRI 目标（REGISTRY/SCHEMA-FIELD/SKOS）8 · 退役 1**（合计 67） |
| 改名类消费者命中 | **7049 处** |
| **盲替换会误伤的命中** | **4933 处**（`Customer`⊂`customerId` 3872 · `Product`⊂`ProductKnowledgeCard` 598 · `Asset`⊂`referencesAsset` 442 · `Skill`⊂`referencesSkill` 21） |
| 沙箱演练 | 真改写 **12** 个真实文件；`generated/**` **1** 个按派生口径跳过；演练后 TTL **全可解析**；**退役项一处未换** |

**四通道迁移配方**：① 同名 ⇒ 仅 IRI 级替换（可机械化）；② 改名 ⇒ **逐条显式清单 + 词边界受限替换**，有盲替换风险者**不得批处理**；
③ 退役 ⇒ `deprecated` + `dcterms:isReplacedBy`，保留只读期，**不得改名**；④ 非 IRI 目标 ⇒ 走各自登记机制。

**制品**：`evidence/prep/sim-rehearsal-report.json` · 断点清单 `evidence/prep/SIM-REHEARSAL-BREAKPOINTS.md`
**门禁**：`wi_a8_sim_rehearsal` **8/8** + `--selftest` **4/4**（含真实路径反例 R1/R2/R3）
**边界**：演练占位命名空间 `https://rehearsal.sim.local/ns-l1#` **永不发布**；仓内制品零改动；`generated/` 改动 0。


---

## A-8 全量 / A-9 / A-10（2026-09-21，Owner 指令「全做」）

### A-8 全量演练（B6+B8 242 条，沙箱）
| 指标 | 值 |
|---|---|
| 清单来源 | `construction_plan.batch_of` 逐条复算（**非 3 条样本**） |
| 条目 | **242**（gits 172 · kert 70）——KERT 侧**仅读入沙箱，零写入** |
| 真改写 | **242 / 242**（IRI 级 15 · 受限改名 36） |
| **盲替换风险 → 跳过未盲改** | **149 个文件（62%）** |
| 演练后 TTL 解析 | **全部成功（0 失败）** |
| 退役项违例 | **0** |
**制品**：`evidence/prep/sim-rehearsal-full-b6b8.json`　**门禁**：`wi_a8_sim_rehearsal_full` 7/7 + `--selftest` 7/7

### A-9 L1 SIM 候选模型（8 类）
- 候选 **8 类**（基线 5 + 新增 3），**equivalentClass/Property = 0**；
- 命名空间为**候选占位** `https://rehearsal.sim.local/ns-l1#`（**永不发布**，D3 未签）；
- 制品仅置 `evidence/prep/l1-sim-candidate/l1-core.SIM-CANDIDATE.ttl`（**未写 `specs/`**）；
- **32 ≠ 8 口径分列记录**（来源盘点 32 类 ≠ L1 候选 8 类）。
**门禁**：`wi_a9_l1_candidate` 7/7 + `--selftest` 6/6

### A-10 断点裁定材料（4 条）
> **口径更正（2026-09-21，`FAIL-2026-09-21-W15TL-21`）**：下表列的是 A-8 的**原始扫描口径**（`sim-rehearsal-report.json.consumer_hits_exact`，**未排除**扫描器自产/工具配置）。
> advisory 与执行包用的是**消费者面口径**（已排除）：`675 / 288 / 1398 / 148`，排除量 `104 / 44 / 69 / 36`（两套数逐条相加闭合）。
> **引用时必须写明口径**；执行/待确认以消费者面口径为准。

| 断点 | 旧 ⇒ 新 | 原始扫描命中（A-8 口径） | 消费者面命中（advisory/执行包口径） | 会被误伤 | 文件数 |
|---|---|---|---|---|---|
| B-1 | `Customer` ⇒ `CustomerRole` | 779 | 675 | 3872 | 287 |
| B-2 | `Product` ⇒ `ProductOffering` | 332 | 288 | 598 | 103 |
| B-3 | `Skill` ⇒ `SkillDefinition` | 1467 | 1398 | 21 | 358 |
| B-4 | `Asset` ⇒ `AssetDefinition` | 184 | 148 | 442 | 72 |

每页含：事实（**已排除扫描器自产与工具配置**命中）· 受限替换正则 · **完整排除清单** · 三个出口（A 显式清单改名 / B 并存 / C 延后）· **不构成裁定**声明。
**制品**：`evidence/prep/breakpoint-advisory/`（README 索引 + B-1~B-4）　**门禁**：`wi_a10_breakpoint_advisory` 5/5 + `--selftest` 5/5

### 过程缺陷（如实）
1. 我 `write_to_file`/patch 时**先写文件后校验**，一度把 `onto1_sim_rehearsal.py` 写成语法错误（已修复并复核全部模式）；
2. A-8 基础脚本与独立脚本**双实现** ⇒ 已删除基础脚本内的 `cmd_full`，保留唯一实现（避免 QA F-2 同类隐患）；
3. A-10 首版判据含笔误关键词与"每题 ≥3 条排除名"的臆断 ⇒ 已改为**完整性**判据。


---

## A-11 / A-12 / A-13（2026-09-21，Owner 指令「全做」）

### A-11 SIM 合格批次全演练（B2/B4/B7/B8 = 462 条，沙箱）
| 批次 | 条目 |
|---|---|
| B2 L1/L2 语义规格层 | 135 |
| B4 L3 运行本体 | 106 |
| B7 导入级耦合 | 65 |
| B8 内容级重绑 | 156 |
| **合计** | **462**（gits 430 · kert 32 —— KERT 侧仅读入沙箱） |

真改写 **462/462** · TTL 全可解析 · 退役 0 违例 · **盲替换风险文件跳过 230 个** · IRI 级 15 · 受限改名 33。
制品 `evidence/prep/sim-rehearsal-sim4.json`；门禁 `wi_a11_sim_rehearsal_sim4` **8/8** + 反例 **6/6**。

### A-12 断点三出口对比（12 格，沙箱真跑）
| 出口 | 实测 | 判定要点 |
|---|---|---|
| **A 显式清单改名** | 549 处改写 · **0 脏值** · 相邻名保持 | 受限正则（词边界 + 前后不邻接标识符字符）有效 |
| **B 保留原名 + 并存** | 旧名保留 1284 处 · **等价关系 = 0** | 新名以注解/别名并入，不得 `equivalentClass` |
| **C 延后** | 零改动 | 仅登记待裁项 |

制品 `evidence/prep/breakpoint-option-comparison.json` + `BREAKPOINT-OPTION-COMPARISON.md`；
门禁 `wi_a12_breakpoint_option_rehearsal` **8/8** + 反例 **9/9**（K7/K8 为真实路径）。
**本表不选出口**——选择权在 Owner / PSO / 数据 Owner。

### A-13 迁移器骨架（四通道，默认 dry-run）
- 通道：`SAME_NAME 51` · `RENAME 7`（**可自动 3 / 须显式清单 4 blocked**）· `NON_IRI_TARGET 8` · `RETIRE 1`；
- **硬约束**：默认 dry-run；写入须 `--apply --sandbox <仓外目录>`；**沙箱设在仓内即拒绝**；禁手改 `specs/`·`generated/`；永不发布 IRI；永不写 KERT；
- **端到端实测**：沙箱内真改写 **262** 文件、**仓内零写入**；越权 apply（沙箱设仓内）**被拒绝**。
制品 `evidence/prep/migration-plan.json`；门禁 `wi_a13_migration_runner` **9/9** + 反例 **11/11**（含 R1~R5 真实路径/端到端）。

### 过程缺陷（如实，本轮 4 条）
1. A-13 `apply` 曾取 `by_old` 自报告行（该行无 `auto_applicable`）⇒ **恒走 skip 分支、0 改写是假象**；已改为取自迁移计划，实测真改写 262 文件；
2. A-12 的 K7 反例选样错误（`Customer`/`customerId` 大小写不同，无法证明朴素替换会产脏值）⇒ 改用 `Asset`⊂`referencesAsset`；
3. A-12/A-8 沙箱副本继承只读权限 ⇒ 统一 `chmod 0o644`（**原件不动**）；
4. A-13 `guard_target` 只按绝对路径判断 ⇒ 沙箱内 `specs/` 未被拦；已改为按**逻辑仓相对路径**判定，并新增"沙箱不得设在仓内"的硬守卫（R3）。


---

## A-14 / A-15 / A-16（2026-09-21，可选工作全部完成）

### A-14 Wave 2/3 施工清单（462 行）
| 处理口径 | 行数 |
|---|---|
| 含盲替换风险术语 ⇒ **须显式清单后再改** | **230** |
| 无术语命中（仅随命名空间迁移） | 223 |
| 受限改名（词边界）+ IRI 级替换 | 9 |

制品 `evidence/prep/migration-worklist.{csv,md,json}`；门禁 `wi_a14_migration_worklist` **6/6** + 反例 **8/8**。

### A-15 断点三出口执行包（12 份）
`evidence/prep/breakpoint-execution-pack/{A,B,C}/`（每条断点 × 每出口一份）+ `README.md` 索引。
出口 A 含**完整排除清单**与待改文件表；出口 B 含并存清单并明示**禁等价**；出口 C 为待裁登记。
门禁 `wi_a15_breakpoint_execution_pack` **6/6** + 反例 **6/6**。

### A-16 KERT 登记请求草案
`evidence/prep/KERT-REGISTRATION-REQUEST-DRAFT.md`：8 条非 IRI 目标 + 1 条退役项 + 写权限前置 + 校验先于产出；
标注 **DRAFT_NOT_SENT**（未发出、未写入 KERT）。门禁 `wi_a16_kert_registration_request` **6/6** + 反例 **6/6**。

### 待人类（8 项，提示词：`memory/HUMAN-ACTIONS-PROMPTS.md`）
① 四条断点出口选择（A/B/C）② D3 根域联签 ③ 12 条关系归属 ④ KERT 写权限 ⑤ O-D4-2 出口 ⑥ 索引刷新窗口 ⑦ QA 第二轮复验 ⑧ 委员会签署页。

### 过程缺陷（如实）
- A-14 selftest 我**未先跑就登记**，首次记录为 fail；且抓到两处自己的判据缺陷：W3 在字典为空时**恒真**、W6 是 `>= 0` **同义反复** ⇒ 已修为"非空且计数为正"/"项数与原因记录一致"，并补 V6/V7 反例（现 8/8）；失败记录已按修正后重记。
- A-15 的 `checks` 对缺失文件未容错 ⇒ 反例 Y4 触发崩溃；已加空串兜底（现 6/6）。


---

## A-17｜业务场景开发就绪包（2026-09-21）

**回答**：**可以开发业务场景（SIM 环境）**——开发/联调/自动化测试/迁移验证不再等签署页或委员会。

**三件交付**
1. `evidence/prep/SCENARIO-DEV-BOUNDARY-CARD.md`：结论 + **五条禁令** + 实测撞点 + 就绪底座（13 产品实例 / 28 条 SIM 关系 / seed V1.1 / execute 模块 / 既有 e2e / 462 行施工清单）。
2. `evidence/prep/scenario-term-layer-rehearsal.{json,diff}`：**术语解析层沙箱预演** —— 2 文件 4 行改占位符 `${GITS_KNO_NS}` + 配置注入；Java 结构校验通过、DMN XML 可解析、**隔离别名一处未改**、**仓内零改动**。
3. `evidence/prep/SCENARIO-QUARANTINE-HITS.md`：`CASH_MANAGEMENT` **3 文件 7 处**，代码级佐证其**作类别/产品族**使用 ⇒ **不应映射为产品实例**（待 `待人类-3` 裁定）。

**实测撞点**：`Skill` 81 文件 · `Customer` 73 · `Product` 16 · `GroupRelationship` 3 · `KnowledgeMap` 1（未裁定断点术语 ⇒ **延用现行名**）；隔离别名仅 `CASH_MANAGEMENT`（7 处）；已批准别名 0 引用 ⇒ **产品关系不阻塞场景**。

**门禁**：`wi_a17_scenario_readiness` **7/7** + 反例 **9/9**（含 U7/U8 真实路径）。

**审 diff 时发现的细节**：`claim-reconciliation.dmn:2` 的 `namespace="https://gientech.com/gits/kno/dmn"` 是 **DMN 自己的命名空间**（非本体 IRI）⇒ 解析层应为它单独设一个配置键（如 `GITS_KNO_DMN_NS`），不要与本体命名空间混用一个键。

**过程缺陷（如实）**：S5 判据找错键名、U7 把"未触碰"误写成"不得出现"、S1/S6 一度只读文件不看台账（"判据与声明脱钩"的老毛病）⇒ 均已修正并补一致性判据。


---

## 批次受理与收口（2026-09-21，incoming TL）

**开场**：`git branch = recover/PI-ARCH-product-catalog` · `HEAD = 9a6dec78046172cd60cb8032f4419905e1958515` ·
索引新鲜度 = **gits STALE(6) / KERT STALE(144)**（`make index-status` ⇒ WARN）。

| 项 | 结论 | 我执行的命令（原始输出要点） |
|---|---|---|
| **T1** | **已办**：四组加法**4/4 闭合**；双口径并列已在位；A-8 制品未改（门禁日志 `output_sha256` 与磁盘一致） | `python3 /tmp/t1_verify.py`（逐文件定位数字行 + 哈希比对） |
| **T2** | **已办**：补登 `OWNER_REQUESTS.md §C-3` + 操作卡警示块（含冻结包哈希 `df2933d1…` 与 MANIFEST 登记一致的实证） | `sha256sum …/14-…md` · `grep 14-… MANIFEST.md` |
| **T3** | **已办**：组合覆盖确认（三种组合全部**禁记**委员会批准）；观察：旧角色名组合降级为 `INCOMPLETE`（非 `OWNER_REVIEW_ONLY`），但禁记性质不变 | `onto1_signature_verify.py --verify` ×3（现行 14 号 / 新名同人 / 旧名同人） |
| **T4** | **已办去重**：待人类-5 由 **O-08** 覆盖，已标注依据并从待办移除 | 读 `OWNER-DECISIONS-2026-09-21-LANDING.md §一 O-08` |
| **T5** | **已办**：待人类-6 更正为 **KERT 侧专属**，gits 实测 `drift=6`，避免误批全量 3.7M | `make index-status`（WARN, drift={'merge-meta.json': 6, 'meta.json': 6}） |
| **T6** | **已办**：QA 第二轮约束收紧（三条独立性硬条件 + 写域 + 清单以裁定书 §三 为准 + F-1 期望改『与 gates 一致』） | 编辑 `HUMAN-ACTIONS-PROMPTS.md 待人类-7` · `TL-ADJUDICATION §三` |
| **T7** | **已办**：`EVIDENCE.md`(83/0/1/84) · `ORCHESTRATOR §7.1` · `INDEX_BASIS` 实测新鲜度 · `STATE.json` · `ROLE_BOARD.yaml` · 守卫复跑 | `make memory-check` / `make evidence-check` / `loop_guard.py` |

**本批次发现的额外问题（已记账）**：`FAIL-2026-09-21-W15TL-22`（**更正后的数字仍是陈旧快照** + 导航件陈旧，W15TL-21 同类**复发**）
⇒ 处置：三处口径改为实测值；改进建议（未立纪律）：**更正数字前必须重读权威字段并记录读取时刻**。
另：**6 条未根因自动失败全部闭环**（经 `/tmp` 日志卫生备份复原：`prep_package_build` 4 条 = 包目录不完整（缺 `MANIFEST.sha256`/`SOURCE/`）+ 1 条 `P4 KERT 零写入交集非空`；`wi_a14_migration_worklist_selftest` 1 条 = `V5` 恒真缺陷，已修并重记）。

**红线核对（收口时实测）**：板面 **84 = 83 pass / 1 pending（不变）** · `current = RETURN_TO_HLD`（不变）· `generated/` 改动 **0** ·
基线 `gits-core.owl.ttl = 705578d6324abd0c`（不变）· KERT 近 1 日写入 **0** · **本批次未新增门禁** · 未代签/未代裁/未置 ACTIVE/未记 `QA_PASS`。


---

## 判据强度自审批次（2026-09-21，继续改进）

**动因**：QA 抓到 4 处判据恒真（F-2/F-3/F-4/F-5）、我自己在 A-14 又被抓 2 处 ⇒ 与其等 QA 再抓，先自审。

**新增工具（非门禁）**：`scripts/onto1_check_strength_audit.py` → 制品 `evidence/prep/check-strength-audit.json`。
AST 提取全部 `(名称, 条件, 说明)` 三元组，标五类薄弱模式：`TAUTOLOGY_CONST` · `TAUTOLOGY_CMP` · `EMPTY_ALL` · `DECLARED_ONLY` · `MUTANT_SCOPE`；带 **13 条已复核白名单（理由留档）**。

**首轮 71 条候选 → 收敛 34 条 → 真缺陷 5 处**（其余为审器自身假阳性或已复核派生值）

| # | 仪器 | 缺陷 | 修法 | 复跑 |
|---|---|---|---|---|
| 1 | `onto1_c2_consumer_scan` | G6 扫描幂等为 `True` 占位（只调 `checks()` 即假绿） | **删除占位**，幂等仅由 gate 计算后插入 | 7/7 |
| 2 | `onto1_construction_plan` | P3 空集恒真 | 改为**恰 4 项且全部 NOT_EFFECTIVE** | 7/7 |
| 3/4 | `onto1_migration_runner` | M4/M5 空集恒真（fail-safe 引入 `.get(..., [])` 时埋下） | 改为**非空且逐条合规**（RENAME=7 / RETIRE=1） | 9/9 + 11/11 |
| 5 | `onto1_kert_registration_request` | Z5 写死 `False`（声明式） | 改**实测派生**（今日写入 + 发出标记）；滚动 24h 与工作树脏项**仅披露** | 6/6 + 6/6 |

**审器自身假阳性（已修）**：`0 in (True, False)` 为真（应按 bool 类型判）· 数据元组被误识别为判据（应要求**谓词形态**）· 变异体范围过窄（应比对**判据函数整体源码**）· 分支结论字面量（同名判据同函数内既有 True 又有 False ⇒ 属 if/else 结论）。

**Z5 副作用（真失败，已查明）**：滚动 24h 命中 23 件，全部是 `poc/**/target/classes/**` 构建产物（mtime 2026-09-20 23:57，早于本批次）；KERT 工作树 80 项既有改动（归属不可区分）⇒ 定口径为「判据 = 日历日写入 0；其余仅披露」。

**提请 Owner**：是否把自审仪登记为新门禁（我未自行登记）。


---

## 采纳批次（2026-09-21「按建议办」）

| # | 采纳项 | 我的动作 | 交付物 |
|---|---|---|---|
| 0 | 自审仪**不登记为门禁** | 立 **D-20**：改批次纪律 + 交 QA 外部挑战白名单 | `memory/TL-DECISIONS-W-1.md` D-20 |
| 1 | 断点出口 A×4 + **先清单后执行** | 预置收口清单（**逐断点签字位**，未签不得开工） | `evidence/prep/BREAKPOINT-EXECUTION-CHECKLIST-OPTION-A.md` |
| 1b | —（工具补强） | 生成器补 **全量逐文件 CSV**（281/100/355/66，含逐条签字位） | `breakpoint-execution-pack/A/*-option-A-FULL.csv` |
| 2 | D3 一页纸 | 四候选 + 六维浓缩 + 联签人 + 只需答 Q1/Q2/Q3/Q8 | `evidence/prep/D3-CANDIDATE-ROOT-DOMAIN-ONEPAGER.md` |
| 3 | 12 条归属确认单 | 逐条 card/field/value + A 栏 8 条 / B 栏 4 条 + **最省方案** | `evidence/prep/RELATION-ATTRIBUTION-CONFIRMATION-SHEET.md` |
| 4 | KERT 先不发出 | 无新文书（草案已备，A-16） | — |
| 6 | 索引只刷 KERT 增量 | **核查后改口径**：仓内无刷新命令 ⇒ 入口在 IDE 侧 | `memory/HUMAN-ACTIONS-PROMPTS.md` 待人类-6 |
| 7 | QA 第二轮派出 | 清单补 3 条（本轮 5 处修复 / **挑战 13 条白名单理由** / A-15 全量 CSV 口数一致） | `memory/HUMAN-ACTIONS-PROMPTS.md` 待人类-7 |
| 8 | 委员会签署页暂缓 | 无动作（等 D3） | — |

**未代办的（明确不在我权限内）**：四条断点出口的**语义选择**（清单待签）· 12 条归属的**裁定**（确认单待勾）· D3 根域**字面量与联签** · KERT 请求**发出** · 索引**刷新**。


---

## QA 第二轮受理批次（2026-09-21）

**裁定文书**：`memory/handoffs/TL-ADJUDICATION-QA-W3R2-2026-09-21.md`（含每一项的现场核验与复跑证据）

| QA 项 | 裁定 | 我的处置 | 复跑 |
|---|---|---|---|
| F-5 / ① | **NOT_ACCEPTED（接受）** | A5 去同源：行级独立 + 双侧对照 + 非空转；新增 A9 | 9/9 + 9/9 |
| ⑨ | **NOT_ACCEPTED（接受）** | 审器 v2：覆盖 fail-closed + 多形态抽取 + 哈希冻结白名单 | 226 条 / 15 候选 / 13 未审 |
| ⑤ | 条件接受 | X2~X5 加非空守卫 + 明细派生（N-3） | 6/6 + 6/6 |
| 其余 10 项 | ACCEPT | 无（F-1/F-2/F-3/F-4/F-6/F-7~F-12/⑥/⑦/⑧/⑩） | — |
| N-1（高） | 新发现 | H4 去恒真 ⇒ **暴露 21 件陈旧白名单**（已剪除+留历史） | PASS + 5/5 |
| N-2/N-3/N-5/N-6 | 新发现 | 逐条修（死子句 / 空过滤 / 缺件具名拒绝 / 误引门禁） | 见裁定文书 |

**两类"我治不了"的东西，已具名登记**：① 审器射程外的 13 个仪器（违规清单+退出码形态）；② 21 件陈旧白名单的删除痕迹（无备份 ⇒ 不可归因）。
**机制升级**：台账 selftest 断言从「至少一项 FAIL」改为「**必须被指定判据本尊捕获**」——这条能防住本轮同类的复发。

---

## QA 第三轮受理批次（2026-09-22）

**裁定文书**：`memory/handoffs/TL-ADJUDICATION-QA-W3R3-2026-09-22.md`

| 仪器 | QA | 处置 |
|---|---|---|
| `cq_fixtures` | HAS_DEAD_PATH | **已修**：gate 只读盘 + `--build` 独立重生成 + 反例 M4/M5 |
| `d2_normalization_pack` | HAS_DEAD_PATH | **已修**：锚点 + 位移容忍（记账）+ G8 结构断言；**含 S-1 板面事件** |
| `sim_projection` | （G4 观察项） | **已修**：新增 G8 盘上逐字节一致性；G4 标注为声明一致性 |
| `check_strength_audit` | HAS_DEAD_PATH | **已修**：新增 `--strict`（默认 0 由 D-20 明示） |
| `namespace_collision_check` | HAS_DEAD_PATH | **未修，具名登记**（C-4b 需设计决定） |
| `product_refs_probe` | HAS_DEAD_PATH | **未修，具名登记**（P1 死代码） |
| `pkg_audit` | HAS_DEAD_PATH | **未修，具名登记**（AU-5 需授权维口径） |
| 其余 7 个 | SOUND | 无 |

**S-1**：`wi_a5_d2_pack` 实测 FAIL 而板面记 pass ⇒ 已按 D-19 重记；**未**换口径。

---

## 口径传播 + QA-W3R4 受理批次（2026-09-22）

**裁定文书**：`memory/handoffs/TL-ADJUDICATION-QA-W3R4-2026-09-22.md`（含板面止谎全过程）

| 项 | 结果 |
|---|---|
| 板面 | **81 pass / 2 fail / 1 inconclusive**（止谎后从 77/6/1 修复而来） |
| 已修 | a3 声明表 · l3 三类并检+30 · d2 A-1 明示 · collision 空转不得给绿 · product_refs P1 · record_gate exit3⇒inconclusive |
| 待重构 | `wi_d2_relation_resolution`(+st)：输入模型失效，须配置驱动重构（**不靠改常数**） |
| 待 Owner | C-3 AU-5 口径四选一；D2 重构归谁 |

**教训（本轮两次自引回归）**：① 判据名混入限定语会破坏自检精确匹配；② 把"显式行钉定"的容忍语义改成"全局唯一"会造成真实树批量假红 —— **先跑真实树，再定语义**。

---

## QA-W3R4 受理批次（2026-09-22）

- 报告：`loops/ONTO1-ontology-split/memory/handoffs/INDEPENDENT-QA-W3R4-2026-09-22.md` ｜ sha256 `213105df192d4b5d…` ｜ 635 行 ｜ 裁定：`TL-ADJUDICATION-QA-W3R4-2026-09-22.md`
- A 块：3 ACCEPT / 3 AWC / 0 NOT_ACCEPTED；A-1 **明示语义**（我一度改成全局唯一 ⇒ 真实树 26 条假红，已回退）
- B 块：205 点位认领；**审器加固**（裸 append + 下标赋值）⇒ 可见面 0→286 点、可审判据 229、未审 13；
  B-i2 披露式（结论已由退出码判据表达）· **B-i3 被构造实验反证**（M3⇒A5⇒exit 2）· B-i4/B-i5 补 M6/M7 · B-i6 = argparse 入口不符
- C 块：C-1 已修（空转 ⇒ INCOMPLETE；未扩冻结口径）· C-2 已修 · **C-3 升级 Owner（与 C-1 同一语义轴）**
- 重记：14 门禁，**统一走 `onto1_gate_log.py`**（自证行 20/84；位置=STDOUT 段首行，非文件首行）
- 板面：**84 = 81 pass / 2 fail / 1 inconclusive**；2 fail = `wi_d2_relation_resolution`(+st) 待重构

