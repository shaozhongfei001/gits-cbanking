# ONTO1-ontology-split｜编排表（Tech Lead）

## 0. 门禁位置（每日开工先核对）

```
FOR_REVIEW ──书面复审──▶ DESIGN_APPROVED ──Wave0~5──▶ IMPLEMENTED ──独立QA──▶ QA_PASS ──Owner──▶ OWNER_ACTIVATED
   ▲ 当前位置（复审已提交，结论未达；RETURN_TO_HLD 仍有效）
```

- 现在允许：**Wave -1 全部**（只读盘点、消费者扫描、标准核对、夹具设计、ADR 起草、WBS 重估、Owner 请求提交）。
- 现在禁止：标 `DESIGN_APPROVED`/`FROZEN`；拆分权威本体；切换消费入口；正式重钉；候选公共模块标 `ACTIVE`；签发国标符合性声明；把初版影响清单当全量分析；把 D1~D4 未决项当已关闭。
- **送审程序（包 `W-1/review-submission`，2026-09-20）**：13/14 齐备 + `wi_review_package_integrity` PASS（变异复验 PASS）+ 《送审操作清单》/《结论回收与门禁更新预案》已落 `memory/handoffs/`。**发出与签署仍远在 Owner / 委员会手上**（`OWNER_REQUESTS.md §C-1-a~e`）；结论回收后按预案三形态（A/B/C）**先受理判定再落门禁**，24h 内完成五件通用动作。**送审程序本身不改变门禁**。

## 1. 波次编排

| 波次 | 内容 | 状态 | 前置 |
|---|---|---|---|
| **Wave -1** | WI-A1 基线 v2 / WI-A2 消费者全量扫描 / WI-A3 D1 标准矩阵 / WI-A4 命名空间 ADR / WI-A5 D2·D4 请求 / WI-A6 CQ 夹具 / WI-A7 WBS 重估 / 送审程序包 | **进行中**（WI-A1/A2/A4/A5/A6/A7 本轮交付；送审程序包就绪待 Owner 发出；WI-A3 待文本） | 无 |
| **W-1.5 就绪加固** | WI-A2 义务回源确认（1038 行候选→真义务收敛）、Wave 0 就绪预检门禁化、两处门禁小修（D-2/D-3 + 头部自述不一致） | **可立即开工（等待期，只读）** | 无（不受外部签署阻塞）—— 详见 `memory/PLAN-NEXT.md` |
| Wave 0 | 冻结与 Loop 骨架、基线锁定进 EVIDENCE | 未开工 | **G-1** |
| Wave 1 | 独立语义契约库设立（五条件） | 未开工 | **G-1 + 公共语义 Owner 任命** |
| Wave 2 | 四层拆分（合同先行；D3 硬前置；WI-A2 处置表为退出门禁） | 未开工 | `DESIGN_APPROVED` + D3 签署 + WI-A2 |
| Wave 3 | 双侧换消费 + 原子窗口 | 未开工 | Wave 2 + D4 |
| Wave 4 | 门禁与符合性（内部规则，无国标声称）+ 六 CQ 执行 | 未开工 | Wave 3 |
| Wave 5 | 契约库 ACTIVE 核验与发布演练 | 未开工 | Wave 4 |
| G6 | IMPLEMENTED → QA_PASS → OWNER_ACTIVATED | 未开工 | Wave 5 + 独立 QA（禁自签） |

## 2. G-1（进入 Wave 0 的前置门）当前状态

| 条件 | 状态 |
|---|---|
| 书面复审结论 = `DESIGN_APPROVED` 或 `PASS_WITH_REQUIRED_CHANGES` 且条件已登记 | **未达**（送审程序包 `W-1/review-submission` 已就绪待 Owner 发出；结论未回） |
| WI-A2 完成 | **达成**（扫描 + 处置表 100% + 变异复验全绿） |
| WI-A4 完成 | **部分**（ADR 草案已出；D3 未签，根域未定） |
| WI-A6 完成 | **达成（设计层）**（6 CQ 夹具设计机读化；执行属 Wave 4） |
| D3 签署（Wave 2 硬前置） | 未签 |
| D2 / D4 已提交 | **已提交**（请求函今日发出；签署前场景保持 `NOT_EVALUATED`） |

## 3. 并发纪律

- **并行读 + 串行写**：`make generate`/`make check`/Maven 测试/门禁脚本必须串行。
- 单写者路径：`loops/ONTO1-ontology-split/{STATE.json,EVIDENCE.json,LOOP.yaml}`、`memory/{ROLE_BOARD.yaml,NEXT_SESSION.md,ORCHESTRATOR.md,INDEX_BASIS.md}`、`evidence/consumer-scan-*`、`evidence/attribution-45-v2.csv`。
- 本工作区有其他执行者并发提交 ⇒ **只用显式路径 `git add`**；`docs/dd/` 下未跟踪文件勿纳入。

## 4. 防假绿三件套（本 Loop 已落地）

| 门禁 | 单一真值函数 | fail-closed | 变异复验 |
|---|---|---|---|
| `wi_a2_consumer_scan` | `scan()` + `classify()` | 基线哈希/计数不符、无规则匹配、`PENDING_TRIAGE` 非零、期望命中缺失 ⇒ 一律 FAIL | `wi_a2_scan_mutation`（19 用例，含单仓缓存 ⇒ FAIL、全豁免 ⇒ FAIL、全 PENDING ⇒ FAIL、对照 ⇒ PASS） |
| `wi_a1_baseline` | `build()` + `validate()` | 基线哈希/计数、分口径计数、层归属、基线与属性覆盖、占位根域 | `wi_a1_attribution_selftest`（M1 删映射行 / M2 改制品口径 / M3 占位根域 ⇒ FAIL；M0 对照 ⇒ PASS） |
| `wi_a4_namespace_collision` | `C-1..C-4` 单一判定 | 输入缺失 ⇒ 退出码 3；**未决 ≠ 通过**（C-1b `NOT_EVALUATED` 不当 pass）；**C-4 已按 D-2 收窄**（受控 = `specs/semantic/**` + `specs/CONTRACT_INDEX.yaml`）；`REQUIRED_PINS` allow-list 4 项；收窄到空 ⇒ `C-4_NO_CONTROLLED_PIN` FAIL | `--selftest` **23/23**（含元变异、全豁免、自引用、钉值未冻结、未判定≠通过、D-2 收窄回退、受控条目 0、删必需钉值、真实仓 FAIL 对照）。**当前为 `fail`（仅 C-2 两处真实冲突）** |  |
| `wi_a4_iri_mapping` | 映射草案计数/分布复算 | 新旧端计数、语义关系分布不可复算即 FAIL | `--selftest`（D3 未签期间不得出现具体新 IRI） |  |
| `wi_a3_reference_alignment` | 词表 × 否定标记判定 + `rule_statement` 放行（**联合判定**） | 触犯词表且无否定标记 ⇒ FAIL；**放行不得被真实符合性声称利用**（Q-1/C4）；输出须含 `allowed[...]` 与 `allowed_by_reason{...}` 逐原因计数 | `--selftest` 12 项 + **必补**「真实声称行含单个关键词 ⇒ FAIL」「标题含『门禁』⇒ 不得放行其下声称」。**当前 `fail` 面：Q-1 未修** |  |
| `wi_a2_obligation_triage` | `triage()/triage_row()` 单一真值 | 输入缺失、判据不可回源、弱面被判 TRUE、同名无机械证明、Wave 非法 ⇒ 一律 FAIL | 11/11（M1~M9 + M0）；**TL 独立变异 MU-1~MU-3 均被具名拦下、还原后 CSV 哈希逐字回到 `81e5ebc4`** |  |
| `wi_a5_d2_pack` / `wi_a5_d4_pack` | 决策包自洽复算 | 引用数/取值不可复算、或改动产品卡与本体即 FAIL | 各自 `--selftest`（M1~M9 + M0 对照） |  |

## 5. 风险与阻塞登记

| # | 风险/阻塞 | 等级 | 处置 |
|---|---|---|---|
| R-1 | 书面复审继续退回 ⇒ Wave 0+ 长期阻塞 | 高 | 只读产出继续推进；结论到达即更新 `LOOP.yaml.gate_state` |
| R-2 | 公共语义 Owner / Integration Contract Owner 未任命 ⇒ Wave 1 不开工 | 高 | `memory/OWNER_REQUESTS.md` 已提交任命请求 |
| R-3 | `INDEX_STALE(144)`（KERT） | 中 | 本会话所有 KERT 结论回源到 `文件:行`，未用索引外推；刷新登记为下一动作 |
| R-4 | D3 根域未签 ⇒ Wave 2 阻塞（`R-D3`） | 高 | ADR 草案提前送审；占位 IRI 禁入正式制品 |
| R-5 | D2 未签 ⇒ CQ3 三场景硬阻塞 | 高 | 请求函已发；激活门禁硬阻塞设计（不依赖豁免） |
| R-6 | D4 未签 ⇒ 投影合同不生效（CQ1/CQ2 与 5 条 range 改指核验一并阻塞） | 中 | **决策包已就绪**：`docs/dispatch/ONTO1-D4-决策包-V1.0.md`（八类候选 + 最小字段 + 合同草案 + SIM 载体建议 + 退出台账），门禁 `wi_a5_d4_pack` PASS；SIM 临时权威声明含退出条件，先签声明后补确认。**7 项待决 O-D4-1~7** 见包 §6 |
| R-7 | 消费者扫描为**词法级**，`FOLLOW_MIGRATION` 1038 行为候选义务 | 中 | Wave 2 前逐条回源确认；已抽样 2 项证伪同名（见 WI-A2 报告 §4） |
| **R-8** | **回源工作量远超原估**：PKG-A1 实测真义务 **626**，TL 裁定 I-6 升格 65 行后为 **691** > 原阈值 400 | **高** | 已回写 `evidence/WBS-RESTIMATE.md` §6（W3-3「3 人日+2 缓冲」作废，须按"每条 5~15 分钟"分档重算）；**WEAK 面 97 行列为最高风险区，Wave 2 必须优先抽检**；KERT 侧 65 行待写入许可 |
| **R-9** | **"放行类"规则天生带盲区**：D-3 的 `rule_statement` 放行被真实声称利用（Q-1，`W15A3-04`）；D-2 的 C-4 收窄留下"删文件不判"残余（`W15A3-02`） | **高** | 新增 **D-12 派工纪律**：凡放行/白名单/豁免/收窄，**必须同时给出"不得放行"反例清单**，且反例各配一条变异（本轮两次代价：`S-4` + Q-1） |
| **R-10** | **证据与制品脱钩**（交付后仍在改 ⇒ 日志对不上 revision） | 中 | **D-11** 交付纪律（post-DONE 冻结 / 日志自证 revision / 审计前确认哈希稳定）+ 新工具 `scripts/onto1_gate_log.py`（哈希自证 + 退出码透传 + 缺失 fail-closed，已自测） |
| **R-11** | `wi_a4_namespace_collision_selftest` 与 `wi_a3_reference_alignment` 的**登记证据生成于 A3 改动前** ⇒ 属陈旧证据 | 中 | **T-4**：A3 冻结复交后由 TL 重跑重记（QA N-6 同项） |

## 6. 后续八项工作（**不在本 Loop scope**，仅登记归属建议）

统一命名（bank-front-*/skill-customer-*/SP-*）、种子本体与多来源本体对齐、Kuzu/LightRAG 投影与本体对齐、产品主数据权威落位、知识地图版本演进……（完整清单见落地计划与本 Loop `SHARED_MEMORY.md` §不做事清单）。

## 7. 未关闭阻断项与门禁盲区（2026-09-20 TL 集成会话新增）

### 7.1 板面终态（**2026-09-21T02:15Z 更新** —— W-1.5 批次收束）

门禁 **84 个 = 83 pass / 1 PENDING_EXTERNAL_AUTHORITY**（2026-09-21 收口更新；原记「31 = 30 pass / 1 fail」已陈旧）；唯一非 pass = `wi_a4_namespace_collision`（`exit=3` / `INCOMPLETE`，未判定项 `C-1b` 待 **D3**；**非**「C-2 未修」——C-2 已于本轮修复，见 `evidence/SIM-R1-WAVE12-REPORT.md`）。
裁定与**红测记账规则**见 `memory/TL-DECISIONS-W-1.md`（**D-1 ~ D-19**；其中 D-18/D-19 为改号条目）；阻断项清单见 `memory/NEXT_SESSION.md` §未关闭阻断项（B-1~B-7）。

**W-1.5 批次（team `onto1-w15` / `onto1-w15r`）结论**：

| 包 | 结论 | 备注 |
|---|---|---|
| PKG-A1 | **ACCEPT** + **PKG-A1b 已完成**（TL 代实现） | 真义务 **691 / 待回源 361**；`--selftest` 15/15 |
| PKG-A2 | **ACCEPT_WITH_CONDITIONS** | T-1~T-3 待 D3 签署 / G-1 |
| PKG-A3 | **NOT_ACCEPTED**（C1~C4 已到位、C5/C6 已闭环、**C7 字面未完成**） | 作者已下线 ⇒ 转交接；四个反例已固化为门禁 `wi_w15_a3_acceptance` |
| 独立 QA | **NOT_ACCEPTED**（第三~七轮，共关闭 U-1/U-2/U-6/U-7/U-11/U-12/N-8/C5） | **本批不得记 `QA_PASS`**；`independent_qa` 状态为 **`report_received`（非 `QA_PASS`）**，`qa_pass_recorded=false` （QA 波 3 报告已收；第二轮待派，见 `HUMAN-ACTIONS-PROMPTS.md 待人类-7`） |

**本批新增纪律**：D-11（交付与证据绑定）· D-12（放行类须附反例清单）· D-13（受限词表书写纪律）· D-14（重记与修复尝试的预算语义）· D-15（**禁止再加码上限**）· **D-16（权威值变更须用宽口径内容检索判据）**。
**本批新增工具**：`scripts/onto1_gate_log.py`（日志自证 revision + 退出码透传）· `scripts/onto1_w15_acceptance.py`（T-4 验收仪器，8 用例）· `scripts/onto1_pkg_audit.py`。

### 7.2 本轮暴露的门禁盲区（下一 holder 必须带走的教训）

| # | 盲区 | 表现 | 加固方向 |
|---|---|---|---|
| G-1 | **`loop-guard` 看不见孤儿证据日志** | 4 组检查（8 个门禁名）曾执行并留下 17 份日志但未接线 ⇒ 板面显示"15/15 全绿"，而其中一组实为 FAIL | **已固化**：新增门禁 `wi_evidence_board_check`（+selftest）——`evidence/*.log` 中的门禁型日志必须等于"已登记证据 ∪ 带理由白名单"，**孤儿 = 0**；白名单每条强制带 reason |
| G-2 | 词表守卫**不区分"禁令"与"声称"** | 我方门禁描述（元陈述）被误判为违规 | 放行"规则陈述行"或把 `loops/**` 纳入白名单（D-3）；**禁止靠删规则过门禁** |
| G-3 | 断言**范围过宽**把工具产物当钉值 | C-4 对清单类 manifest 误报 ⇒ 每次重跑即噪声 FAIL | 收窄为受控钉值文件（D-2） |
| G-4 | **"空转通过"** | `C-3` 因本体无 `owl:versionIRI`/`owl:imports` 而空转；**不得计为覆盖** | 空转必须标注并计入"未覆盖" |
| **G-5** | **断言缩进错误 = 死代码**（QA U-1 BLOCKER） | G5「本体包标签二次校验」缩进在 `for` 之外 ⇒ 只判末元素；真实仓末行非 P0 ⇒ 对 65 行 P0 **覆盖 0/65**（TL 实证：65 行改包名 ⇒ 命中 0） | 移入循环 + **M9b-3**「全部 P0 改包名 ⇒ 命中数 == 行数」+ 夹具 P0 行**非末位** + **M9c** 钉住该前提（元变异移末位 ⇒ FAIL） |
| **G-6** | **孤立证据日志的"前缀制"盲区**（QA U-6） | `E2` 只认 `wi_/contract_/…` 前缀 ⇒ `a3fix-after-*.log` 等 6 份已执行日志**不可见**（方向保守但属盲区） | E2 改为覆盖 `evidence/` 下**全部 `*.log`** + **M4** 回归用例（无前缀日志必须被拦，并断言旧正则看不见它） |
| **G-7** | **白名单通配吞掉已登记证据**（QA U-7） | 通配 `…_selftest-20260920T*.log` 覆盖到自己的登记证据 ⇒ E2 统计自相矛盾（31+25−1） | 通配**一律收敛为精确名** + 新增 **E5**（仅**通配**条目判负；精确名重合属重记瞬态）+ **M5/M5b** |
| **G-8** | **D-11 落地"点状而非面状"**（QA U-11 MAJOR） | 只给**新建**门禁套包装器，漏改"**重跑**"的既有门禁 ⇒ 2 份日志缺 `# artifact=` 自证行 | 全部重跑门禁套包装器；判据：**D-11 之后缺自证 = 0**（现 9 份自证 / 0 不符 / 22 份全在 D-11 前） |
| **G-9** | **自指重记陷阱**（`W15TL-10`） | 板面 `selftest` 的 M3 **自检整个 Loop** ⇒ 重记时旧日志必处中间态，连续 3 次被**如实记为 fail** | 操作顺序：**重记板面门禁前，把两个板面门禁的当前日志一并入白名单**；中间态日志留证 |
| **G-10** | **权威值变更后未做宽口径内容检索**（QA U-12） | `max_attempts` 5→8 后仍有 2 处叙述残留（`PROTOCOL.md:14`、`ORCHESTRATION.md:32`），**与同文件的 8 自相矛盾** ⇒ 执行者行为分叉 | **D-16**：宽口径内容检索（覆盖 `最多N次`/`attempt ≤ N`/`（N 次）`）+ 三类合理命中显式排除 + 数字须写计量对象 + **禁行号定稿** + 不得以他人判据免责 |
| **G-11** | **尝试预算与"重记"不可区分**（`W15TL-12`） | `record_gate` 以 `W0-ITER.md` 出现次数计尝试 ⇒ revision 变更后的重记被当作修复尝试，触顶后**无法产出与 revision 一致的自证日志** | **D-14**（上限 5→8，有限、不改写历史）+ **D-15**（**禁止再加码**；出口只能是 ①工具意图区分 或 ②ADR 级决定）。**消耗公示（/8）**：board 7 · board_selftest 7 · triage 6 · refalign 5 · collision 2 · acceptance 1 |

> 四条盲区指向同一纪律：**绿证的价值取决于"它有没有可能变红"**。无法变红的断言、看不见的日志、过宽的断言范围，是"假绿"的三种形态；第四种是**空转**。

### 7.3 集成会话的隔离结论（并发写者）

本工作区存在**其它写者**（KERT 侧 3 个文件在本窗口被写入，归属未确认，见 D-7）。
⇒ 单写者路径（§3）**必须**继续遵守；且**不得**用 mtime/文件存在性推断归属或改动来源，一律以哈希与回源为准。
