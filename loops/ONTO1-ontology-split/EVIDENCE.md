# ONTO1-ontology-split｜Evidence index

机器可判定的唯一证据板为 `EVIDENCE.json`。本文件只提供人类导航，不复制状态。

- 命令日志：`evidence/`
- 失败记录：`FAILURES.md`
- 波次迭代：`memory/waves/`
- 独立QA：必须由非implementation actor写入 `EVIDENCE.json.independent_qa`

---

## 1. 门禁账（三态表达：**PASS=83 · FAIL=0 · PENDING_EXTERNAL_AUTHORITY=1** · PRODUCTION_ACTIVATION=BLOCKED；共 84）

> **二次更正（2026-09-21 收口，`FAIL-2026-09-21-W15TL-22`）**：本节表头曾由 `PASS=40/共 41` 改为 `PASS=81/共 82`，但**当时 `EVIDENCE.json.board_expression` 已为 83/0/1/84**（A-17 入册后）⇒ 更正后**仍与权威字段不一致**。现已改为 **83/0/1/84** 并逐字对齐 `board_expression`。**教训**：更正数字前必须**重读**权威字段，不得沿用上一会话的快照。
> **更正（2026-09-21，`FAIL-2026-09-21-W15TL-21`）**：本节表头原停留 `PASS=40 / 共 41`，与权威字段 `EVIDENCE.json.board_expression`
> （`PASS=81 · FAIL=0 · PENDING_EXTERNAL_AUTHORITY=1 · total=82`，`derived_from=EVIDENCE.json.gates`）不一致。
> 唯一权威为 `EVIDENCE.json`；本节数字按该字段复写，`INCOMPLETE`（exit 3）计 `PENDING_EXTERNAL_AUTHORITY`，不计 FAIL。

> **唯一未通过项（不得隐藏）**：`wi_a4_namespace_collision` = **fail**（exit 2）。
> 原因：**仅 C-2 实测 2 处真实前缀冲突未修**（`gits:` 双绑定 + `gits:Product` 同名不同 IRI），属 **Wave 3 修复项**。
> **C-4 已按 D-2 收窄并通过**（受控范围 = `specs/semantic/**` + `specs/CONTRACT_INDEX.yaml`；清单类工具产物范围外并逐条登记）：输出为
> `[C-4] PASS（声明 4 个：受控 1 / D-2 范围外 3 / 未裁决 0；必需钉值 allow-list 4/4；载体自冻结：受控载体 0 个，**空转不计为覆盖**）`。
> **但 C-4 尚未完全关闭**（TL 沙箱实证）：删**声明**⇒具名 FAIL ✅；删**文件**⇒崩溃或漏判 ❌ —— 见 `FAILURES.md` `W15A3-02/W15A3-03`，条件 C1/C2 交 `pilot-a3`。
> 按 D-1 红测记账规则：如实记 `fail`，**禁止**改写为 `inconclusive`；该 fail 已列入 `NEXT_SESSION.md` §未关闭阻断项 B-1。
> 另需声明：`C-1b` = `NOT_EVALUATED`、`C-3` = **空转通过（不计为覆盖）**。

> **2026-09-21 二轮更新（Owner 决议：开发与正式批准分开）**：
> ① **C-2 = `CLOSED`**（生成器根因已关闭：命名空间分离**配置驱动**；连续两次生成字节一致；验收 7/7；13 实例 IRI 未迁移）。
> ② **D2 = 28 条 `SIM_PROJECTED_BY_OWNER_APPROVED_ALIAS` / 12 条 `QUARANTINED_UNRESOLVED`；正式关系发布 `NOT_AUTHORIZED`**（SIM 投影文件：`specs/knowledge-architecture/instances/product/sim/product-relations.SIM.ttl`）。
> ③ **板面三态**：`INCOMPLETE`（exit 3）**不计 FAIL**，计 `PENDING_EXTERNAL_AUTHORITY`；`FAIL=0`。
> ④ 新增门禁：`wi_c2_generator_check`(+selftest) / `wi_d2_sim_projection`(+selftest)。

> **2026-09-21 波 1/2 完成（SIM 整改第一轮）**：新增 6 类门禁 —— `wi_a2_disposition`(8/8) · `wi_a3_closeout`(8/8) ·
> `wi_a4_sim_migration_verify`(7/7) · `wi_a5_l3_load_fixture`(6/6) · `wi_a5_l2_patch_plan`(4/4) · `wi_a7_signature_verify`(5/5)，
> 均配 selftest（反例 7/7·6/6·7/7·6/6·—·5/5）。板面 **62 = 61 pass / 1 inconclusive**。
> 实施报告：`evidence/SIM-R1-WAVE12-REPORT.md`；波 3 派工提示词：`memory/DISPATCH-WAVE3-PROMPTS.md`。
> 新增纪律 **D-19**（门禁预算按 revision 纪元计数）。
>
> **独立 QA（波 3）复核结论（2026-09-21）**：10 项中 **9 项 ACCEPT/ACCEPT_WITH_CONDITIONS，1 项 NOT_ACCEPTED**（断言强度声明）；
> **12 条发现全部被 TL 接受并修复**（裁定书 `memory/handoffs/TL-ADJUDICATION-QA-W3-2026-09-21.md`）。
> **`QA_PASS` 未记录、也不得记录**（板面仍 1 inconclusive + `RETURN_TO_HLD` + 项 9 待第二轮）。
>
> **SIM 侧下一步已完成（A-8 全量 / A-9 / A-10）**：板面 **70 = 69 pass / 1 inconclusive**；B6+B8 **242 条沙箱演练全真改写**，**149 个文件含盲替换风险已跳过**；L1 **8 类**候选模型（等价 0、候选占位命名空间、未写 specs）；四条断点裁定材料就绪（**未裁定前相关 Wave 2/3 项不得开工**）。（板面仍 1 inconclusive + `RETURN_TO_HLD` + 项 9 待第二轮）。
> **SIM 侧第二轮亦完成（A-11 / A-12 / A-13）**：板面 **76 = 75 pass / 1 inconclusive**；B2+B4+B7+B8 **462 条**沙箱全演练（真改写 462，盲替换风险跳过 230）；断点三出口对比 12 格真跑（A：549 处/0 脏值 · B：旧名保留 1284/无等价 · C：零改动）；迁移器骨架四通道固化（默认 dry-run、沙箱必须在仓外、禁手改 specs·generated，端到端真改写 262 文件而仓内零写入）。

> **QA 第四轮受理（2026-09-22）**：报告 `INDEPENDENT-QA-W3R4-2026-09-22.md` @213105df192d4b5d（635 行）逐字核验； A 块 **3 ACCEPT / 3 条件接受 / 0 否决**；B 块 205 点位认领（**审器加固：可见面 0→286 点**，B-i3 被构造实验反证， B-i4/B-i5 补反例 M6/M7，B-i6 查明为入口形态不符）；C-1/C-2 已修、**C-3 升级 Owner（待人类-11，与 C-1 同轴）**； 14 门禁重记并统一改走 `onto1_gate_log.py`（自证行 23/84，位置=STDOUT 段首行）； `independent_qa` 更新至第 4 轮（含报告哈希，**qa_pass_recorded=false**）；`qa-w3r4` 登记 done。 板面 **84 = 81 pass / 2 fail / 1 inconclusive**（2 fail = `wi_d2_relation_resolution`(+st) 待重构）。
> **QA 第三轮受理（2026-09-22）**：13 仪器 = **6 死路径 + 7 SOUND**；最重为 **S-1 板面可信性事件** （D2 包实测 FAIL 而板面记 pass，根因 C-2 重生成致锚点 **+2 位移**）⇒ 已修锚点 + 位移容忍（记账）+ G8 结构断言； 另修 cq_fixtures（假绿+写回）/ sim_projection（门禁不读盘）/ 自审仪 `--strict`；**3 条未修具名登记** （C-4b / P1 / AU-5）。6 门禁开新纪元重记，板面**不变 83/0/1/84**。
> **QA 第二轮受理（2026-09-21）**：8 ACCEPT + 1 条件接受 + **2 NOT_ACCEPTED（均成立，已修）**；A5 去「构造性同义反复」（改行级独立 + 双侧对照 + 非空转，+A9）；自审仪升 v2（**覆盖率 fail-closed**，诚实输出 226 条/15 候选/**13 未审**）；**N-1（高）已登记门禁含 1 条死判据**已修并连带清出 21 件陈旧白名单。10 门禁重记（直接通过），板面**不变 83/0/1/84**。
> **采纳「按建议办」批次（2026-09-21）**：补四份文书（D3 一页纸 / 12 条归属确认单 / 出口 A 收口清单 / 派工提示词 5 处更新）+ A-15 补**全量逐文件 CSV**（281/100/355/66）；自审仪**不登记为门禁**（D-20）⇒ 改批次纪律 + 交 QA 外部挑战；索引刷新**仓内无命令**（口径已更正）。板面**不变 83/0/1/84**。
> **判据强度自审批次（2026-09-21）**：45 个仪器 AST 级判据扫描；首轮 71 条候选 → 收敛 34 条 → **真缺陷 5 处已修**（恒真占位 / 三处空集恒真 / 声明式改实测派生）；**13 条已复核白名单（理由留档）**，现报 **0 条未复核候选**；受影响 8 个门禁已按 D-19 重记，板面**不变 83/0/1/84**。
> 失败账 `W15TL-23`（同类第 3 次）。**提请 Owner**：是否把自审仪登记为新门禁。
> **SIM 侧第三轮完成（A-14 / A-15 / A-16）**：板面 **82 = 81 pass / 1 inconclusive**；施工清单 **462 行**（须显式清单 230 / 仅命名空间迁移 223 / 受限改名 9）；断点三出口执行包 **12 份**（选定即可执行）；KERT 登记请求草案（**DRAFT_NOT_SENT**，未写入 KERT）。
> **待人类 8 项提示词**：`memory/HUMAN-ACTIONS-PROMPTS.md`。

> **2026-09-21 更新（Owner 授权 C-2 修复 + D2 分流后）**：
> ① **C-2 已修复** —— 命名空间分离（`gits:`→T-Box、新增 `prod:`→A-Box），13 个产品实例 IRI **未迁移**；登记表 `namespace-known-defects.json` 的 `defects` 已清空（修复项移入 `repaired`）。
> ② 唯一未通过项 `wi_a4_namespace_collision` 的语义**已从"缺陷 FAIL(exit 2)"变为 `INCOMPLETE`（exit 3）**：C-2 实测 0 处，剩余未判定项为 **`C-1b`（需 D3 签署根域）**；按 D-1 **如实记 fail，不得计为通过**。
> ③ 新增 4 个门禁：`wi_c2_fix_verify`(+selftest) / `wi_d2_relation_resolution`(+selftest)；执行状态 = `OWNER_AUTHORIZED_SIM_REMEDIATION_AND_IMPLEMENTATION`。
> ④ 实施报告：`evidence/C2-D2-SIM-REMEDIATION-REPORT.md`。

| Gate | 命令 | 退出码 | 证据 |
|---|---|---|---|
| `wi_a1_baseline` | `python3 scripts/onto1_attribution_rebuild.py --gate` | 0 | `evidence/wi_a1_baseline-20260920T132334Z.log` |
| `wi_a1_attribution_selftest` | `python3 scripts/onto1_attribution_rebuild.py --selftest` | 0 | `evidence/wi_a1_attribution_selftest-20260920T132334Z.log` |
| `wi_a2_consumer_scan` | `python3 scripts/onto1_consumer_scan.py --gate` | 0 | `evidence/wi_a2_consumer_scan-20260920T132334Z.log` |
| `wi_a2_scan_mutation` | `python3 scripts/onto1_consumer_scan_tests.py` | 0 | `evidence/wi_a2_scan_mutation-20260920T132335Z.log` |
| `wi_a2_obligation_triage` | `python3 scripts/onto1_gate_log.py scripts/onto1_obligation_triage.py --gate` | 0 | `evidence/wi_a2_obligation_triage-20260920T153327Z.log`（**日志自证 revision**：`# artifact=…onto1_obligation_triage.py@1982a9ec2017df97`） |
| `wi_a2_obligation_triage_selftest` | `python3 scripts/onto1_gate_log.py scripts/onto1_obligation_triage.py --selftest` | 0 | `evidence/wi_a2_obligation_triage_selftest-20260920T153327Z.log`（11/11 用例符合预期） |
| `wi_c2_fix_verify` | `python3 scripts/onto1_c2_fix_verify.py --gate` | 0 | C-2 验收 **7/7**（13 实例 IRI 未迁移 · 类型命中 T-Box 已声明类 · 错误类引用 0 · 无 equivalentClass） |
| `wi_c2_fix_verify_selftest` | `python3 scripts/onto1_c2_fix_verify.py --selftest` | 0 | **6/6**（4 反例 + 还原对照） |
| `wi_d2_relation_resolution` | `python3 scripts/onto1_product_relation_resolution.py --gate` | 0 | D2 分流 **7/7**（28 已解析 / 12 隔离 · 隔离 0 处进 A-Box · CQ3 只报 28-12） |
| `wi_d2_relation_resolution_selftest` | `python3 scripts/onto1_product_relation_resolution.py --selftest` | 0 | **6/6**（含"隔离写入 A-Box"与"CQ3 越权声称"反例） |
| `wi_a5_product_refs` | `python3 scripts/onto1_product_refs_probe.py --gate` | 0 | `evidence/wi_a5_product_refs-20260920T134317Z.log` |
| `wi_a5_product_refs_selftest` | `python3 scripts/onto1_product_refs_probe.py --selftest` | 0 | `evidence/wi_a5_product_refs_selftest-20260920T134317Z.log` |
| `wi_a6_cq_fixtures` | `python3 scripts/onto1_cq_fixtures.py --gate` | 0 | `evidence/wi_a6_cq_fixtures-20260920T134418Z.log` |
| `wi_a5_d4_pack` | `python3 scripts/onto1_d4_pack.py --gate` | 0 | `evidence/wi_a5_d4_pack-20260920T142226Z.log`（Attempt 1；`f39fef87…`） |
| `wi_a5_d4_pack_selftest` | `python3 scripts/onto1_d4_pack.py --selftest` | 0 | `evidence/wi_a5_d4_pack_selftest-20260920T142228Z.log`（Attempt 1；`ed19925c…`；M1~M9 全拦下、M0 对照通过） |
| `wi_a6_cq_fixtures_selftest` | `python3 scripts/onto1_cq_fixtures.py --selftest` | 0 | `evidence/wi_a6_cq_fixtures_selftest-20260920T134418Z.log` |
| `wi_review_package_integrity` | `python3 scripts/onto1_review_package_check.py --gate` | 0 | `evidence/wi_review_package_integrity-20260920T141501Z.log`（Attempt 2；`23e0bf34…`） |
| `wi_review_package_selftest` | `python3 scripts/onto1_review_package_check.py --selftest` | 0 | `evidence/wi_review_package_selftest-20260920T141504Z.log`（Attempt 2；`0f5f502c…`；M1/M2 拦下、M0 对照通过） |
| `contract_check` | `make check` | 0 | `evidence/contract_check-20260920T132346Z.log` |
| `security_check` | `make security-check` | 0 | `evidence/security_check-20260920T132343Z.log` |
| `index_status` | `make index-status` | 0 | `evidence/index_status-20260920T132340Z.log` |
| `wi_a3_reference_alignment` | `python3 scripts/onto1_reference_alignment_check.py --gate` | 0 | `evidence/wi_a3_reference_alignment-*.log`（**曾被自身措辞误判 ⇒ D-3 改写后 pass**） |
| `wi_a3_reference_alignment_selftest` | `python3 scripts/onto1_reference_alignment_check.py --selftest` | 0 | 同上 |
| `wi_a4_iri_mapping` | `python3 scripts/onto1_iri_mapping_draft.py --gate` | 0 | `evidence/wi_a4_iri_mapping-20260920T145541Z.log` |
| `wi_a4_iri_mapping_selftest` | `python3 scripts/onto1_iri_mapping_draft.py --selftest` | 0 | 同上 |
| **`wi_a4_namespace_collision`** | `python3 scripts/onto1_namespace_collision_check.py --gate` | **2（fail）** | `evidence/wi_a4_namespace_collision-20260920T145542Z.log` |
| `wi_a4_namespace_collision_selftest` | `python3 scripts/onto1_namespace_collision_check.py --selftest` | 0 | `evidence/wi_a4_namespace_collision_selftest-*.log`（16/16） |
| `wi_a5_d2_pack` | `python3 scripts/onto1_d2_normalization_pack.py --gate` | 0 | `evidence/wi_a5_d2_pack-20260920T145542Z.log` |
| `wi_a5_d2_pack_selftest` | `python3 scripts/onto1_d2_normalization_pack.py --selftest` | 0 | 同上 |

**登记说明（TL 集成会话）**：以上 8 个门禁原先**只执行未接线**（留有 17 份脚本自留日志但不在证据板内 ⇒ 板面曾显示"全绿"），
已按 `memory/TL-DECISIONS-W-1.md` D-1 登记并**按真实退出码记账**。记账规则与盲区加固见 `memory/ORCHESTRATOR.md §7`。

| Gate | 命令 | 退出码 | 证据 |
|---|---|---|---|
| `wi_evidence_board_check` | `python3 scripts/onto1_evidence_board_check.py --gate` | 0 | `evidence/wi_evidence_board_check-*.log`（**孤儿日志 = 0**，43 份门禁型日志 / 25 已登记 / 19 白名单） |
| `wi_evidence_board_check_selftest` | `python3 scripts/onto1_evidence_board_check.py --selftest` | 0 | 同上（M1 注入未登记日志 ⇒ FAIL、M2 删除已登记证据 ⇒ FAIL、M3 对照 ⇒ PASS） |

> 这两道门禁是**本轮最大盲区的固化措施**：`loop-guard` 只比对 `LOOP.yaml` ↔ `EVIDENCE.json` 两个集合，
> **看不见集合外的执行结果**。本门禁补上第三维（evidence 目录），使"执行了但没登记"不再可能静默存在。

| Gate | 命令 | 退出码 | 证据 |
|---|---|---|---|
| `wi_zip_manifest_verify` | `python3 scripts/onto1_zip_manifest_verify.py --dryrun` | 0 | `evidence/wi_zip_manifest_verify-*.log`（预演包 15 成员 `missing=0/extra=0/mismatch=0`；篡改成员 ⇒ 判 FAIL 可检出） |

> 这道门禁把"**发出的包 == 受检的包**"从口头承诺变成可执行证明：委员会拿到 zip、项目侧冻结仓内文件，
> 两者若脱钩双方都不会察觉。现已绑定，并证明该绑定**有牙齿**（篡改可检出）。

| Gate | 命令 | 退出码 | 证据 |
|---|---|---|---|
| `wi_a2_wave0_readiness_precheck` | `python3 scripts/onto1_wave0_readiness.py --precheck` | 0 | `evidence/wi_a2_wave0_readiness_precheck-*.log`（PKG-A2 交付；TL 审计 AU-1~AU-4 通过） |
| `wi_a2_wave0_readiness_selftest` | `python3 scripts/onto1_wave0_readiness.py --selftest` | 0 | 同上（16 条条目级断言） |

> **必须如实声明（D-9）**：同一脚本的 `--gate` 模式（"G-1 是否已满足"）**当前实测 exit = 2**——
> 唯二 NOT_READY 为 **R6（D3 签署件未签）** 与 **R7（`LOOP.yaml.gate_state.current` 仍 `RETURN_TO_HLD`）**，
> **属设计如此**（G-1 硬前置）。按 TL 裁定 **D-9** 该模式**不登记为门禁**（避免无回归价值的常红项诱发红灯疲劳），
> 改为 **G-1 触发义务**：G-1 达成后 24h 内必须跑 `--gate` 确认 exit 0 并登记该门禁。
> 该事实同时登记于 `memory/handoffs/TL-AUDIT-W15-PKG-A2.md`、`evidence/wave0-readiness-gate.json`、
> `memory/NEXT_SESSION.md`、`memory/PLAN-NEXT.md`。

## 2. 关键制品与哈希

| 制品 | 说明 | 哈希/值 |
|---|---|---|
| `specs/semantic/gits-core.owl.ttl` | 基线本体（全程只读） | `sha256 705578d6324abd0c1bd2bd670e6f3c0ffd8e04c358d0134246c89a3acfc38d00`；rdflib 复现 32 类 / 34 对象属性 / 1 数据属性 / 255 三元组 |
| `docs/review/ARCH-ONTO-2026-001-rereview-package/*` | 复审包 12 文件 | **12/12 与 MANIFEST 钉值逐字一致**（含 03 CSV `6ace07b8…`、12 账本 `f284e9fd…`） |
| `evidence/attribution-45-v2.csv` | 45 项四层归属矩阵（22 字段 + 3 列归属） | `sha256 05ec849e57a163a5…` |
| `evidence/baseline-v2-manifest.json` | 基线 v2 清单（**同时是 C-4 钉值文件**） | `sha256 cac187a7624247a2…`；**本行即其独立冻结记录**（供碰撞检查 C-4b 判定，防"改钉值即可通过"） |
| `evidence/consumer-scan-hits.jsonl` | 命中清单（机读） | `sha256 a16369224b80456a…`（26690 行） |
| `evidence/consumer-scan-summary.csv` | 命中汇总（repo×category×disposition×token） | 见 `consumer-scan-manifest.json` |
| `evidence/consumer-scan-obligations.csv` | **净迁移义务清单（file 级 1052 行）** | 见 `consumer-scan-manifest.json` |
| `evidence/consumer-scan-dispositions.json` | 处置规则表（58 条规则 + 处置词汇） | 见文件 |
| `evidence/consumer-scan-manifest.json` | 扫描清单（**重新生成的工具产物，不是钉值文件**） | 该文件每次运行重生成（含 `generated_at`）⇒ **不得作为钉值文件、不得在此登记"冻结哈希"**（登记即陈旧：见 `FAILURES.md` FAIL-2026-09-20-W15TL-01/02）。需要比对其内容时以**当次运行的实测哈希**为准，或改用内容级稳定口径（如 `consumer-scan-hits.jsonl` 的行数与内容哈希在**同一批次内**的一致性）。 |
| `evidence/review-submission-zip-dryrun-20260920T1415Z.log` | 重打包预演：解包 16 项（1 目录 + 15 件 = MANIFEST + 01~14）；**仅写 `/tmp`，仓库无 zip 制品** | 见文件 |

## 2c. D4 决策包（包名 `W-1/D4-pack`，2026-09-20）

| 制品 | 说明 | 哈希/位置 |
|---|---|---|
| `docs/dispatch/ONTO1-D4-决策包-V1.0.md` | 决策包正文：L1 八类逐项确认表 / `SourceIdentifier` 六必填 + 具名拒绝 / 投影合同七要素草案 / SIM 三载体建议 + 四退出台账 / CQ1·CQ2 依赖 / O-D4-1~7 / 签署区（空白） | `docs/dispatch/` |
| `loops/ONTO1-ontology-split/evidence/d4-l1-authority-candidates.csv` | 机读清单 32 行（8 术语 × 2~3 权威候选 + ≥1 禁止项 / 1 存放位置） | `sha256 8547d72b5247081c…` |
| `loops/ONTO1-ontology-split/evidence/d4-pack.json` | 机读包（非声明 / 字段表 / 拒绝规则 / 合同草案 / SIM 台账 / CQ 依赖 / 待决项 / 红线自证） | `sha256 7568800a97c96c94…` |
| `loops/ONTO1-ontology-split/evidence/d4-pack-manifest.json` | 冻结机读底座哈希（门禁 C10 强制） | 见文件 |
| `memory/handoffs/ONTO1-W-1-D4-pack-HANDOFF.md` | 包级一页交接 | `memory/handoffs/` |

> **不生效声明**：投影合同 `NOT_EFFECTIVE`（无生效日期/签署人）；SIM 声明 `NOT_EFFECTIVE`（台账 `TRACKING_NOT_STARTED`）；CQ1/CQ2 = `NOT_EVALUATED`。**签署全在数据 Owner + 业务 Owner 手上，TL 未代签。**

## 2b. 复审轮送审程序包（包名 `W-1/review-submission`，2026-09-20）

| 制品 | 说明 | 位置 |
|---|---|---|
| 送审操作清单 V1.0 | 送达待填位、交付方式（zip + 打包自证）、期限 2026-10-09、回收路径、发出前红线 | `memory/handoffs/ONTO1-W-1-送审操作清单-V1.0.md` |
| 结论回收与门禁更新预案 V1.0 | 受理有效性判定（fail-closed）+ 三形态（A `DESIGN_APPROVED` / B `PASS_WITH_REQUIRED_CHANGES` / C 继续退回）24h 动作清单 | `memory/handoffs/ONTO1-W-1-结论回收与门禁更新预案-V1.0.md` |
| 包级交接 | 交付物/证据/接手动作/未做事项/风险 | `memory/handoffs/ONTO1-W-1-review-submission-HANDOFF.md` |

> 送审程序**不改变门禁**：`RETURN_TO_HLD` 仍有效；未收到签署件前 Wave 0 及以后零动作。发包、签署均为 Owner / 委员会动作（`memory/OWNER_REQUESTS.md §C-1-a~e`）。

## 2c. P-1 候任公共语义 Owner 准备包（包名 `W1-prep/P-1-public-semantic-owner`，2026-09-20）

**性质**：角色能力准备（**DRAFT，零签署权、零执行**）。**不作为任何门禁证据**，不得计入 PASS。

| 制品 | 说明 | 位置 |
|---|---|---|
| L1 八类术语定义稿 DRAFT | 8 类 × 22 字段；IRI 全为 `PENDING:{NS-L1}#X`，无任何正式根域；附录 A 机读 CSV 12 行（8 类 + 4 属性） | `docs/architecture/ONTO1-L1-八类术语定义稿-DRAFT.md` |
| R1~R9 修订版 DRAFT | **内部规则 / 参照对齐**名义（§0 禁用清单：禁 `CONFORMANCE` 字样与国标符合性表述）；逐条含判据/失败具名码/变异用例 | `docs/architecture/ONTO1-L1-建模规则R1-R9修订版-DRAFT.md` |
| 命名空间 ADR 联签意见 DRAFT | U-1（根域，我方为输入方）/ U-3（窗口长度，我方为决策 Owner）/ U-4（`authorityEntity`·`hostingRepo`）**只给选项与建议、不给结论**；含联签前置 P-1~P-6、复核 V-1~V-8、不建议项 N-1~N-7 | `docs/architecture/ONTO1-命名空间ADR联签意见-DRAFT.md` |
| Wave 1 五条件落地方案 DRAFT | 五条件逐条（机制/可核验证据/失败具名码/变异用例）+ 库骨架文件清单 + 零依赖白名单 + 四阶段流水线 + 独立版本线 + 三方评审矩阵 + G5 核验模板 | `docs/architecture/ONTO1-Wave1独立语义契约库五条件落地方案-DRAFT.md` |
| CQ1/CQ2 履职准备 DRAFT | fail-closed 具名拒绝码（CQ1 7 条 / CQ2 6 条 / 通用 5 条）+ 目标数断言四组数字与判定表 + 现有夹具逐字段复核与修订建议 | `docs/architecture/ONTO1-CQ1-CQ2履职准备-DRAFT.md` |
| 包级交接 | 交付物 / 新增回源结论 / 5 项待裁 / 未做声明 / 下一 holder 动作 | `memory/handoffs/PSO-01-公共语义Owner候选准备包.md` |

**本包新增的回源结论（`文件:行`）**：

| # | 结论 | 回源 |
|---|---|---|
| 1 | `memberOfGroup` 实测 domain = `LegalEntity`（矩阵目标放宽为 `Party`，属扩大值域）；`connectsFrom/To` 实测 range = `LegalEntity` | `specs/semantic/gits-core.owl.ttl:151-155`、`:163-173` |
| 2 | `gits:Customer` = 域引用类（映射 EDWCRM `A_ZHCX_CUST_BASE`）；`gits:customerId` 为 DatatypeProperty（退役对象） | `specs/semantic/gits-core.owl.ttl:22-24`、`:27-30` |
| 3 | `Customer` 的 8 属性实测值 | `specs/semantic/gits-core.linkml.yaml:25-36` |
| 4 | **`playedBy` 全仓无本体/代码实据**，仅命中矩阵文书两行 ⇒ 若登记为命名属性则计数 36→37，与既有口径不自洽（待裁 O-2） | `docs/review/…/03-逐术语权威矩阵-22字段.csv:5`、`evidence/attribution-45-v2.csv:5` |
| 5 | **`range 改指 CustomerRole` 实测 5 条**，而设计 §4.1 写作「4 条」⇒ 设计文字与机读矩阵不一致（待裁 O-4） | `grep -c "改指" evidence/attribution-45-v2.csv` → `5` |
| 6 | `Product` 本体注释仍写「权威物理源为 KERT 产品卡」，与设计 B-02 纠正口径不一致（注释未改写，待裁 O-1） | `specs/semantic/gits-core.owl.ttl:127-129` |

**如实声明**：本包**未**产生任何门禁记录、**未**运行 `make generate`、**未**修改 `specs/semantic/`·`generated/`·`CONTRACT_INDEX.yaml`·`evidence/cq-fixtures/*.json`·封版 `docs/dd/`；**未**标 `ACTIVE`/`FROZEN`/`DESIGN_APPROVED`；**未**发布任何 IRI；**未**代签；KERT 仓只读未写。

**收工校验**（2026-09-20T14:20Z）：`make memory-check LOOP=ONTO1-ontology-split` → **PASS**；`make evidence-check LOOP=ONTO1-ontology-split` → **PASS**；`make index-status` → **PASS**（`nodes=5106, drift 0`，日志 `evidence/index_status-20260920T141948Z.log`）。`git diff --cached` 为空（**未** `git add`）。

## 2d. P-4 D2 决策包（包名 `W-1/D2-pack`，2026-09-20T14:21Z）

**性质**：**决策输入（DECISION_INPUT_ONLY）**，由 `product-ref-normalization-analyst` 产出；
**不注册为 Loop 门禁**（`LOOP.yaml.gates` / `EVIDENCE.json.gates` 未变，未走 `record_gate.py`），
**不得计入任何 PASS**。**裁定权在产品 Owner。**

| 制品 | 说明 | 位置 |
|---|---|---|
| D2 决策包 V1.0 | 事实复核 + 12 行最小勾选表 + 逐取值证据卡（候选映射/证据强度/回源/反证）+ 交叉验证 + 零实例 + 影响面 + 两个一次性放行措辞 + 签署区 | `docs/dispatch/ONTO1-D2-产品Owner决策包-V1.0.md` |
| 机读决策包 | 40 处引用（逐条含行号）· 12 取值（候选 + 强度 + 回源）· 账户关系位 12 处 · 零实例 · 三场景矩阵 · 6 项待裁问题 | `evidence/d2-normalization-pack.json`（`24c6e24ccb58ad82…`） |
| 勾选表 / 逐卡片明细 / 交叉验证表 | 决策包 §2 同源表；40 行展开版；精确同形 + 邻近语义命中 | `evidence/d2-{checklist-table,per-card-detail,cross-vocab}.md` |
| 生成器 + 自检 | `--gate` G1~G8（计数 / 零实例 / 候选齐备 / **逐条回源校验 78 条** / 强度与反证 / 不发明产品 / 三场景禁 PASS / 非裁定声明与 R-6）· `--selftest` M0~M5 | `scripts/onto1_d2_normalization_pack.py` |
| 命令日志 | `gate` exit 0（`c946bf2998fd1786…`）· `selftest` exit 0（`63fc855292db3038…`） | `evidence/wi_a5_d2_pack-20260920T142117Z.log`、`…_selftest-…log` |
| 包级交接 | 交付物 / 新回源结论 11 条 / 未做声明 / 接手动作 / 自伤与自纠 | `memory/handoffs/ONTO1-W-1-D2-decision-pack-HANDOFF.md` |

**本包新增回源结论（`文件:行`，全部经机器校验）**：

| # | 结论 | 回源 |
|---|---|---|
| 1 | 卡片正文 §6 给出每个悬空 token 的**中文语义名**（此前各裁定件均未引用）⇒ 5 个取值升级为"三处逐字一致"的强证据 | `KERT:CM-001.md:65`、`CM-003.md:65`、`CB-002.md:65`、`TF-002.md:65` 等 13 处 |
| 2 | `SETTLEMENT_ACCOUNT` 跨三槽位（产品位 / 账户关系位 / 能力特性位），账户关系位有可执行消费者 | `KERT:CM-001.md:26`、`src/kert/application/product_recommendation/eligibility.py:547,552`、`scripts/product_recommendation_golden_benchmark.py:8`；`GITS:V021__corporate_product_knowledge_seed.sql:44` |
| 3 | `SETTLEMENT_ACCOUNT` 的第二身份候选：GITS PI-0 种子有「对公结算账户」产品行（≠ `PROD-SET-001`「单位结算账户」） | `GITS:…V021__corporate_product_knowledge_seed.sql:42` |
| 4 | `CORPORATE_E_BANK` 跨仓身份冲突：GITS 分类基线为**品类**（`has_products:false`）vs PI-0 种子为**产品行** | `GITS:specs/product-knowledge/product-taxonomy.yaml:197-198`、`GITS:…V021…:51` |
| 5 | GITS 分类基线中与 4 个取值同物不同形的品类（资金池 / 流动资金 / 跨境结算 / 承兑工具） | `GITS:product-taxonomy.yaml:167-168,239-240,221-222,203-204` |
| 6 | 另 3 个取值在 GITS 侧是品类（外汇服务 / 票据贴现 / 财务顾问） | `GITS:product-taxonomy.yaml:229-230,215-216,265-266` |
| 7 | 13 张卡 front matter **行号同构**（19/20/26/27/28/30）⇒ 后续按行号核对可复用 | `KERT:CM-001.md:19-30` 等 |
| 8 | 正文互斥叙述仅 **4 处**，且 front matter `mutex_product_ids` **13/13 空** ⇒ 零实例成立（叙述不得充当实例） | `KERT:FIN-001.md:75`、`FIN-002.md:73`、`FIN-003.md:73`、`SET-001.md:64` |

**如实声明**：本包**未**代签、**未**改 `LOOP.yaml` / `EVIDENCE.json` / `Makefile`、**未**改产品卡与 `products.ttl`（KERT 只读）、
**未**改 `specs/`·`generated/`·`CONTRACT_INDEX.yaml`·封版 `docs/dd/`·`evidence/cq-fixtures/*.json`、
**未**标三场景 `PASS`、**未**关闭 R-6、**未**把 SIM / GITS 种子数据当企业权威、**未** `git add`。

**自伤与自纠**：`FAIL-2026-09-20-05`（已闭合）—— 语义命中条目缺仓根 ⇒ 自检 `G4` 一次拦下 13 条"看似齐备"的回源；
修正仓根推断后 `[G4] 78 条，问题 0`，`--gate` G1~G8 与 `--selftest` M0~M5 全 PASS。

**收工校验**（2026-09-20T14:2xZ）：`make memory-check LOOP=ONTO1-ontology-split` → **PASS**；
`make evidence-check LOOP=ONTO1-ontology-split` → **PASS**；`make index-status` → **PASS**（详见 §2d 续记）。

## 2e. P-3 D3 决策包（包名 `W-1/D3-pack`，2026-09-20T14:2xZ）

**性质**：**决策包（DECISION_PACK_ONLY）**，由 `semantic-namespace-analyst` 产出（tech_lead 委托的分析子角色，**未认领 baton、未记任何门禁**）。
**不注册为 Loop 门禁**（`LOOP.yaml.gates` / `EVIDENCE.json.gates` 未变，未走 `record_gate.py`），**不得计入任何 PASS**。**裁定权在语义架构 Owner + 域名 Owner。**

| 制品 | 说明 | 位置 / 哈希 |
|---|---|---|
| D3 决策包 DRAFT | 事实基线 9 条（逐条回源）+ D3-Q1~Q8 + **根域三类方案六维权衡**（ROOT-A/B/C/D，**不填字面量**）+ 解析机制三方案与 **fail-closed F1~F7** + 逐术语映射草案 + 双发布窗口/退役门 **P-1~P-11 参数化 + W1~W7 判定式** + 实测 + 最小填空板 | `docs/architecture/ONTOLOGY-SPLIT-D3-决策包-命名空间与解析机制-DRAFT.md` |
| 逐术语映射草案（机读 87 行 / 迁移域 67） | 关系分布 `RETAINED 32 / AUTHORITY_MOVED 4 / REMODELED 23 / TRANSFORMED 7 / DEPRECATED 1 / 新增 20`；`R1~R5` 红线内建 | `evidence/iri-mapping-draft.csv`（`sha256 cbf9c24d9e2eed1c…`）、`iri-mapping-draft-summary.json` |
| 命名空间修复义务登记 | 2 项真实前缀缺陷（C-2a/C-2b），逐项含 Owner 与**解除条件**；**登记 ≠ 豁免，登记不会使 C-2 转绿** | `evidence/namespace-known-defects.json` |
| 生成器 + 自检 | `--gate` `R1~R5` 全绿 · `--selftest` M1~M5 全拦 + M0 对照 | `scripts/onto1_iri_mapping_draft.py` |
| 碰撞检查原型 + 自检 | `--gate` C-1a/C-1b/C-2/C-3/C-4 · `--selftest` **16 条用例全符合预期**（含元变异 `M-元` 与"全豁免假绿" `M10`） | `scripts/onto1_namespace_collision_check.py` |
| 命令日志 | 见下表 | `evidence/wi_a4_*.log` |
| 包级交接 | 交付物 / 回源结论 / 两项自伤与自纠 / 待裁 5 项 / 接口对齐项 | `memory/handoffs/ONTO1-W-1-D3-决策包-HANDOFF.md` |

| 命令 | 退出码 | 含义 | 证据日志 |
|---|---|---|---|
| `python3 scripts/onto1_iri_mapping_draft.py --gate` | **0** | `R1~R5` 全绿 | `evidence/wi_a4_iri_mapping_gate-20260920T142432Z.log` |
| `python3 scripts/onto1_iri_mapping_draft.py --selftest` | **0** | M1~M5 拦下 + M0 对照 | `evidence/wi_a4_iri_mapping_selftest-20260920T142432Z.log` |
| `python3 scripts/onto1_namespace_collision_check.py --gate` | **2 FAIL** | **当前阻断发布**：C-2 实测 2 处冲突未修（ADR §5.4「必须先修」）+ C-1b `NOT_EVALUATED` | `evidence/wi_a4_namespace_collision-20260920T142432Z.log` |
| `python3 scripts/onto1_namespace_collision_check.py --selftest` | **0** | 16 条用例（M0/M0b 对照 + M1~M13 + M-元）全符合预期 | `evidence/wi_a4_namespace_collision_selftest-20260920T142432Z.log` |

**本包新增回源结论（`文件:行`）**：

| # | 结论 | 回源 |
|---|---|---|
| 1 | 旧命名空间由脚本**从本体读取**（未硬编码）：`https://gientech.com/gits/kno/`；旧端术语 67 = 32 类 + 34 对象属性 + 1 数据属性 | `specs/semantic/gits-core.owl.ttl:1`、`scripts/onto1_namespace_collision_check.py` `C-1a` |
| 2 | 本体**无 `owl:versionIRI`、无 `owl:imports`** ⇒ C-3（单版本闭包）当前**空转**，不得计为覆盖 | `specs/semantic/gits-core.owl.ttl`（全文件） |
| 3 | C-2 实测 **2 处**：C-2a 前缀双绑定、C-2b 同名不同 IRI（`gits:Product`） | `products.ttl:1`、`:10`、`:15`；`customer-source-mapping.r2rml.ttl:2` |
| 4 | `namespaces.json` **全仓不存在**（`find` 无命中）⇒ 碰撞检查的输入源只能取自映射草案，不能取自该文件 | 仓根 `find . -name namespaces.json` |

**如实声明**：本包**未**代签、**未**改 `LOOP.yaml` / `EVIDENCE.json` / `generated/` / `specs/**` / `CONTRACT_INDEX.yaml` / 封版 `docs/dd/` / `evidence/cq-fixtures/*.json`、
**未**发布任何 IRI、**未**重钉、**未**退役旧 IRI、**未**标 `DESIGN_APPROVED`、**未**把任何根域字面量写入任何制品、**未** `git add`；KERT 仓只读未写。

**自伤与自纠（2 项，均已闭合）**：`FAIL-2026-09-20-06`（映射草案 `R1` 在净新增行上空转，变异 `M3` 未被捕获 ⇒ 去掉"净新增即跳过"豁免后拦下）；
`FAIL-2026-09-20-07`（碰撞检查 v1 的"登记制"与并行交付的《碰撞检查脚本需求规格》冲突 —— 登记曾可使 C-2 转绿，属"全豁免假绿"；已按规格改为"冲突存在即 FAIL，登记仅记录修复义务"）。

**接口对齐待裁（TL）**：本包原型与 `docs/architecture/ONTO1-碰撞检查脚本需求规格-DRAFT.md` 存在 3 处接口差异（脚本命名/退出码语义 `0·2·3` vs `0·1`/输入源 `namespaces.json` vs 映射草案），详见决策包 §10。

## 3. 必须如实声明的事实（不得计为通过）

1. `make check` 内嵌 `gk-ke-gates` 就绪度：**22/23 通过**，其中 `semantic-consumption = NOT_MET`（FAIL）、`gate-injection-tests = INCONCLUSIVE`。
   - **与本 Loop 无关**（GK 程序既有事实），但按纪律 **"无法判定 ≠ 通过"**，不得在汇报中计为通过；`contract_check` 门禁自身退出码为 0 且不把就绪度计入失败。
2. **`INDEX_STALE(144)`（KERT）**：索引 @64f6f87 → KERT HEAD 922a674d，漂移 144 提交（>50 阈值）。本会话未刷新索引，**未声称掌握全局设计**；所有 KERT 结论均为直接读取/全文扫描并带 `文件:行`。
3. 消费者扫描是**词法级**：26690 命中中大多数为同名候选（`HOMONYM_REQUIRES_SOURCE_CHECK` 2690），**词法命中 ≠ 迁移义务**；`FOLLOW_MIGRATION` 1038 行为**候选**义务，Wave 2 前须逐条回源。
4. 本会话**未**执行 `make generate`、**未**改动 `generated/`、**未**改动 `specs/semantic/`、**未**改动 `CONTRACT_INDEX.yaml`、**未**改动封版 `docs/dd/`。

## 4. 待 Owner / 外部签署（未完成，设计如此）

见 `memory/OWNER_REQUESTS.md`：角色任命 2 项、D1~D4 外部依赖 4 项；送审侧 5 项（§C-1-a ~ §C-1-e，全在人类手上）。

## 5. 本轮程序性失败（已闭合，如实登记）

| 记录 | 内容 | 状态 |
|---|---|---|
| `FAIL-2026-09-20-04` | 新增送审程序文书（`INDEX_BASIS.md`）把 `loop_guard` 禁止的三类字面量**原样写进正文** ⇒ `make memory-check` FAIL（exit 2） | **已闭合**：改写为描述性表述 + 全目录 grep 无命中；`memory-check` / `evidence-check` / 包门禁三绿复跑通过 |

> 正面结论：该失败由收工校验**即时拦下**，说明占位符门禁**非空转**。未走 `record_gate.py`（不属任何 LOOP gate），`EVIDENCE.json` 未被改写。

---

## 独立 QA（**不得以本索引代替**）

- 机器可判定字段：`EVIDENCE.json.independent_qa` —— **当前 `status=pending` / `actor=null`**（**无人代签**；本 Loop 的 QA 结论**不构成 `QA_PASS`**）。
- 第一轮（`qa-w15`）：`memory/handoffs/INDEPENDENT-QA-W15-2026-09-20.md`，结论 **NOT_ACCEPTED**。
- 第二~七轮（`qa-w15r`）：`memory/handoffs/INDEPENDENT-QA-W15R-2026-09-21.md`，逐轮追加，**总判定 `NOT_ACCEPTED`**。
  关闭项：U-1（G5 死代码 BLOCKER）· U-2 · U-6（E2 前缀制盲区）· U-7（白名单通配吞登记证据）· **U-11（D-11 点状落地，MAJOR）** · **U-12（权威值条文漂移，宽口径判据）** · N-8 · C5 计数口径。
  未关闭：**C-2**（Wave 3）· **C7 字面**（A3 已下线）· U-8（Wave 2 按包抽样）· U-10（KERT 归属待追认）。
- 判据（每轮 QA 复算）：含自证行日志哈希 == 磁盘（现 **9/9，0 不符**）· **D-11 之后缺自证 = 0** · 孤儿日志 = **0** · `registered ∩ allowlisted = 0` · 受控目录零改动 · KERT 零写入。
