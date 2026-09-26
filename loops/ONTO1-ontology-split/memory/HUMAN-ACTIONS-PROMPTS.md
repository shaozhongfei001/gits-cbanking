# 待人类不变：派工提示词（逐项独立窗口可直接粘贴）

> 编制：全局 TL，2026-09-21｜**这些事项我无权代办**（不签署 / 不批准激活 / 不单人置 `ACTIVE` / 不充当独立 QA / 不把建议写成权威事实）。
> 每个代码块**整段粘贴**到独立会话即可。当前事实基线：门禁 **84 = 83 pass / 1 inconclusive**（`wi_a4_namespace_collision` exit 3，`C-1b` 待 D3）· `gate_state.current = RETURN_TO_HLD` · Wave 0+ `BLOCKED` · `independent_qa = report_received（非 QA_PASS）` · `generated/` 改动 0 · 基线 `705578d6324abd0c`。

---

## 待人类-1｜**四条断点出口选择（A/B/C）**（Owner，或授权 PSO/数据 Owner）

> **进展（2026-09-21，按建议办）**：Owner 指示「按建议办」⇒ 已按 **出口 A × 4 + 先清单后执行** 预置收口清单 `evidence/prep/BREAKPOINT-EXECUTION-CHECKLIST-OPTION-A.md`，并**补出 4 份全量逐文件 CSV** （`A/B-1..B-4-*-option-A-FULL.csv`，281 / 100 / 355 / 66 行，含逐条签字位）。
> **仍请你签**：在该清单 §3 逐断点签「清单已核，准予执行」——**缺签即不得开工**（出口选择权始终在你）。

```text
角色：项目 Owner（或你授权的 PSO / 数据 Owner）
事项：为四条命名断点各选一个出口。这是**语义与命名裁定**，不是技术选择，我不代选。

材料（已备，只读）：
- loops/ONTO1-ontology-split/evidence/prep/breakpoint-advisory/README.md      ← 索引
- loops/ONTO1-ontology-split/evidence/prep/breakpoint-advisory/B-1..B-4.md    ← 每条一页（事实/正则/排除清单/三出口）
- loops/ONTO1-ontology-split/evidence/prep/BREAKPOINT-OPTION-COMPARISON.md    ← 三出口**沙箱真跑**对比
- loops/ONTO1-ontology-split/evidence/prep/breakpoint-execution-pack/{A,B,C}/ ← 选定后即可执行的 12 份包

四条断点与实测影响（**两套口径并列，勿混用**；差异来源见 FAIL-2026-09-21-W15TL-21）：
  口径①**消费者面** = 已排除"扫描器自身产物 / 工具配置"命中 —— `breakpoint-advisory/B-1..B-4.md` 与执行包、三出口对比表**均用此口径**；
  口径②**原始扫描** = 未排除上述命中 —— `sim-rehearsal-report.json` 的 `consumer_hits_exact`、`SIM-REHEARSAL-BREAKPOINTS.md` 用此口径。
  两者差 = 被排除的扫描器自产/工具配置命中数（逐条可复算）。
  B-1 `Customer` → `CustomerRole`      ①675 / ②779（差 104） / 会被盲替换误伤 3872 处（含 customerId）
  B-2 `Product`  → `ProductOffering`   ①288 / ②332（差  44） / 误伤 598 处（含 ProductKnowledgeCard）
  B-3 `Skill`    → `SkillDefinition`   ①1398 / ②1467（差 69） / 误伤 21 处（含 referencesSkill）
  B-4 `Asset`    → `AssetDefinition`   ①148 / ②184（差  36） / 误伤 442 处（含 referencesAsset）
  **执行/待确认口径以①为准**（执行包逐条：675 / 288 / 1398 / 148）

三个出口（沙箱演练实测）：
  A 显式清单改名：549 处改写 · **0 脏值** · 相邻名保持（需逐条人工清单，不得批处理）
  B 保留原名 + 并存：旧名保留 1284 处 · **等价关系 0**（新名以注解/别名并入，禁 equivalentClass）
  C 延后：零改动，登记待裁（涉及该术语的 Wave 2/3 项不得开工）

请回复（每断点一个字母）：B-1=A/B/C ｜ B-2=A/B/C ｜ B-3=A/B/C ｜ B-4=A/B/C
（若选 A 或 B，请一并说明是否要求"先出逐文件清单再执行"。）

边界：未裁定前，涉及这四个术语的 Wave 2/3 项**不得开工**；其余同类项不受影响。
```

---

## 待人类-2｜**D3 正式根域联签**（Owner + 域名/基础设施 Owner）

> **进展（2026-09-21，按建议办）**：已按建议补出**一页纸** `evidence/prep/D3-CANDIDATE-ROOT-DOMAIN-ONEPAGER.md` —— 四候选（`ROOT-A/B/C/D`）一句话差别 + 六维浓缩 + 联签人清单 + **你只需先答 Q1/Q2/Q3/Q8**。本项**不阻塞** SIM 侧开发（现以 `PROVISIONAL_SIM_LEGACY_NAMESPACE` 运行）。

```text
角色：项目 Owner 与 域名/基础设施 Owner（双签）
事项：正式根域联签。当前两命名空间临时统一登记为 PROVISIONAL_SIM_LEGACY_NAMESPACE，
      **不构成永久解析与持久性承诺**；未签前仅阻塞"对外发布 / 持久解析承诺 / 外部消费者契约 / 生产激活"，
      并卡住碰撞门禁的未判定项 C-1b（`wi_a4_namespace_collision` 显示 INCOMPLETE，非缺陷未修）。

输入：
- loops/ONTO1-ontology-split/memory/handoffs/ONTO1-W-1-D3-决策包-HANDOFF.md
- loops/ONTO1-ontology-split/memory/handoffs/ONTO1-W-1-D3-决策包-HANDOFF.md（签署件命名口径见其中说明）

签署后自动触发（我已写好预案）：
① `C-1b` 由 NOT_EVALUATED 转可评；② 填 namespaces.json 根域；③ 正式 IRI 发布窗口开启；
④ Wave 2 命名空间切换前置齐（但仍需其他门禁）。

边界：签名与用印由你们完成；我只在签署后执行登记与重跑，**不代签**。
```

---

## 待人类-3｜**12 条关系归属裁定**（Owner 或产品/数据 Owner）

> **进展（2026-09-21，按建议办）**：已按建议补出**归属确认单** `evidence/prep/RELATION-ATTRIBUTION-CONFIRMATION-SHEET.md` —— 12 条逐条 `card[field] -> 别名`；分 **A 栏 8 条（3 别名，建议转业务确认）** 与 **B 栏 4 条（建议确认继续隔离）**；并给出**最省方案**：7 个别名一次性全部「确认继续隔离」（零沟通成本、零推定风险）。**未勾选者一律维持隔离**（安全默认）。

```text
角色：项目 Owner（或你指定的产品/数据 Owner）
事项：D2 分流后仍有 **12 条关系引用无产品归属**（7 个别名），须裁定归属或书面确认继续隔离：
  CORPORATE_E_BANK 5 · CASH_MANAGEMENT 2 · RECEIVABLE_LEDGER_TOOL 1 ·
  ORDER_RECEIVABLE_CLOSED_ACCOUNT 1 · FX_FORWARD 1 · FINANCIAL_ADVISORY 1 · DISCOUNT_SERVICE 1

材料：loops/ONTO1-ontology-split/evidence/product-alias-resolution.json（含每条 relation 的 card/field/value）

硬约束（我不推定）：
- **不得**把 `CASH_MANAGEMENT` 擅自映射成"现金池"（可能是产品类别或能力概念）；
- **不得**虚构不存在的产品卡；**不得**为凑数强行映射；
- CQ3 只能报告"28 条已解析、12 条隔离"。

请回复：逐条给出"目标产品 ID"或"确认继续隔离"。
```

---

## 待人类-4｜**KERT 写权限归属**

```text
角色：项目 Owner（决定权限归属）
事项：确认 KERT 仓的写权限归谁（KERT 维护方执行 / 授权本程序执行）。

材料（草案已备，**未发出、未写入 KERT**）：
- loops/ONTO1-ontology-split/evidence/prep/KERT-REGISTRATION-REQUEST-DRAFT.md（8 条非 IRI 目标 + 退役项 + 履行前置）
- loops/ONTO1-ontology-split/evidence/prep/L2-KERT-PATCH-PLAN.md（逐条补丁方案）
- loops/ONTO1-ontology-split/evidence/prep/kert-change-proposal.json（KERT 义务规模 86：src/kert 50 · examples 33 · specs 3）

请回复：① 受理方（KERT 维护方 / 本程序）；② 是否批准发出 KERT-REGISTRATION-REQUEST-DRAFT。
边界：KERT 仓近 1 日写入 = 0（可核）；合入权在 KERT 维护方。
```

---

## 待人类-5｜~~O-D4-2 出口裁定~~ ⇒ **已裁决，不再待办**（依据 O-08）

> **去重标注（2026-09-21 收口）**：本项已被 **O-08** 覆盖 —— `memory/OWNER-DECISIONS-2026-09-21-LANDING.md` §一 O-08：「C-2 / O-D4-2：选 **『B 过渡 → A 目标』**（`APPROVED`）」；`memory/OWNER_REQUESTS.md §E` 同载。
> **故本项从待办移除**，仅保留原文以备考（**勿重复向 Owner 索取**）。原提问如下：

```text
角色：项目 Owner（或授权契约方）
材料：docs/dispatch/ONTO1-O-D4-2-差异补充决议草案-V1.0.md
影响：决定 CQ1/CQ2 能否出列、映射合同是否起草、以及 scheme 编码规则方向。
请回复：A / B / C（或授权某人代裁）。
```

---

## 待人类-6｜**索引刷新窗口批准**（token 预算）

> **口径更正（2026-09-21，按建议办后核查）**：仓内**没有**索引刷新的 `make` 目标 —— `make` 只提供 `index-status`（红线门禁）与 `index-gate-tests`（变异复验）；`scripts/` 下亦无刷新脚本（只有 `ua_index_gate.py` / `check_ci_contract_index_wired.py` / `check_contract_index_refs.py` 等门禁件）。故刷新入口在 **IDE 侧（工作区索引）**，**我在仓内无命令可代跑**。若你要刷：请在 IDE 对 KERT 工作区触发，或**告诉我确切入口**，我按你给的入口执行（**不自行猜测命令**）。

```text
角色：项目 Owner
事项：批准索引刷新。**口径更正（2026-09-21 收口）**：`INDEX_STALE(144)` **仅指 KERT 侧**；
      gits 侧本轮实测 `make index-status` ⇒ `WARN`，**drift = 6**（阈值内，收工声明 STALE(6)）。
      即：若不刷新 KERT 索引，代价是 KERT 结构外推**不可用**（KERT 结论须回源直读），
      **不等于**需要全量 3.7M tokens。增量口径约 0.3M tokens；全量口径仅在你要求 gits 全量重建时才适用。
请明确：只刷 KERT / 只刷 gits / 两者都刷 / 维持不刷新；并给窗口时段。
请回复：批准 + 窗口时段（或维持不刷新）。
```

---

## 待人类-7｜**QA 第二轮复验**（独立会话；与实现者不同主体）

```text
角色：ONTO1 独立 QA（**第二轮**）。**独立性硬条件（三条同时满足）**：① 非实现方；② **非本汇报方**（前任 holder 执行会话）；③ **非临时兼任 PSO/ICO 者**。不采信 TL 与本汇报方的任何结论。
写域（唯一）：loops/ONTO1-ontology-split/memory/handoffs/INDEPENDENT-QA-W3R2-<日期>.md
只读：全仓 + /home/szf/dev/Leibniz-KERT（**KERT 零写入**）
清单：**一律以 `memory/handoffs/TL-ADJUDICATION-QA-W3-2026-09-21.md §三` 为准**（F-1~F-12 修复复核）；其中 F-1 的期望值以「与 `EVIDENCE.json.gates` 一致」为准（**当前 83 pass / 0 fail / 1 pending / 共 84**，已非清单所写的 61/0/1/62）。

第一轮结论（已收纳）：10 项中 3 ACCEPT / 6 ACCEPT_WITH_CONDITIONS / 1 NOT_ACCEPTED（项 9 = 断言强度声明）。
逐条裁定与修复：loops/ONTO1-ontology-split/memory/handoffs/TL-ADJUDICATION-QA-W3-2026-09-21.md（含 §三 复验清单）

第二轮请**只做**对 F-1~F-12 修复的独立复核（不重复第一轮已通过项），重点：
① A-1 的 A5 是否真独立复算（应显示"独立复算 53 行/188 处/0 违例"，勿读台账字段）；
② 位移落点是否指向代码行（`gk17_prodcard_to_rdf.py:33→37 / :35→39`）；
③ A-4/L3 的边界判据是否已**派生**（非字面量），真实路径反例 N7/N8/P6 是否真能失败；
④ A-4 的 M5 是否显式标注"**不计为覆盖**"（无 IRI needle 可搜）；
⑤ A-13/A-14/A-15/A-16/A-17 新增门禁的判据是否有「恒真/同义反复」（QA-W3R2 已证实我确有此病并已修；N-6 更正：原写 A-18 系误引，仓内无该门禁）；
⑥ 迁移器 A-13 的硬守卫是否真拒绝（目标出沙箱 / 手改 specs / 沙箱设在仓内）；
⑦ 红线：generated/ 改动 0、基线 705578d6324abd0c、KERT 零写入、演练占位命名空间未发布。
⑧ **本轮（判据强度自审）5 处修复**的复核：`onto1_c2_consumer_scan` G6 恒真占位已删 / `onto1_construction_plan` P3 空集 / `onto1_migration_runner` M4·M5 空集 / `onto1_kert_registration_request` Z5 改实测派生；
⑨ 逐条**挑战** `evidence/prep/check-strength-audit.json` 内 **13 条「已复核」白名单**的理由是否成立（理由系 TL 自写 ⇒ **必须由外部挑战**；工具 `python3 scripts/onto1_check_strength_audit.py --scan`，预期输出 0 条未复核候选）；
⑩ A-15 新增**全量逐文件 CSV**（281/100/355/66）与执行包 MD 摘要（前 40 行）的口数一致性。

出口：逐项 ACCEPT / ACCEPT_WITH_CONDITIONS / NOT_ACCEPTED + 你亲自执行的命令与原始输出。
禁令：**不得**记 `QA_PASS`（板面仍有 1 inconclusive，C-1b 待 D3）；不得代签任何文书；不得改任何制品。
```

---

## 待人类-8｜**委员会签署页（仅在你要走委员会口径时）**

> **⚠ 两个隐藏前置（2026-09-21 收口补登，见 `memory/OWNER_REQUESTS.md §C-3`）**：
> ① 冻结包内 `14` 哈希 `df2933d1e183b9d50e98d784…` ⇒ **填名会破包自洽**；② 该页沿用**旧角色名**。
> 请先定：**手写填入** 还是 **TL 重发 V1.2 包**；以及 **补 ≥3 位独立具名评审** 还是 **维持 `OWNER_REVIEW`**。

```text
角色：架构评审组（四位**具名独立**评审各签自己那份）
判据工具：python3 scripts/onto1_signature_verify.py --verify <签署页.md>
  · 四席分别具名且已签 ⇒ ARCHITECTURE_COMMITTEE_ELIGIBLE（**仍须 V1~V9 全过**）
  · 四席同一自然人 ⇒ OWNER_REVIEW_ONLY，**禁记** ARCHITECTURE_COMMITTEE_APPROVED
禁令（Owner 决议第 4 条）：六项技术结论**不得**由 Owner 在发函前预填或代勾；
秘书处（TL）只分发汇总校验，**不投票、不代签**。
提示：若只记 `OWNER_REVIEW`，则 Wave 0 解锁条件（"委员会有效签署页 14 返回并通过 V1~V9"）不成立 —— 这是设计如此。
```


---

## 待人类-9｜**QA 第三轮：定向覆盖 13 个「未审仪器」**（独立会话）

> **已执行（2026-09-22）**：报告 `memory/handoffs/INDEPENDENT-QA-W3R3-2026-09-22.md`（882 行，sha256 `88481e7c0c1e28d0…`，TL 逐字核验）；处置见 `memory/handoffs/TL-ADJUDICATION-QA-W3R3-2026-09-22.md`。
> **本槽位已用尽**（结论：6 HAS_DEAD_PATH + 7 SOUND，其中 4 条已修、3 条具名未修）；下一轮见 **待人类-10**。

> **为什么单列一轮**：QA 第二轮否决 ⑨ 后，我把自审仪升到 v2 并**如实声明覆盖边界**——
> **13 个仪器用「违规清单 / 退出码 / print」形态判定，不在检查表模型内 ⇒ 本审器从未审过它们**；
> 其中 **11 个承载着 20 个已登记门禁**（含 `wi_a4_namespace_collision`）。
> 我**不**自建第二分析器（等于又当选手），故交独立 QA 第三轮。
> 台账（可复现）：`evidence/prep/check-strength-coverage-gap.json`

```text
角色：ONTO1 独立 QA（**第三轮**，定向覆盖）。独立性硬条件（三条同时满足）：① 非实现方；② 非本汇报方；③ 非临时兼任 PSO/ICO 者。
写域（唯一）：loops/ONTO1-ontology-split/memory/handoffs/INDEPENDENT-QA-W3R3-<日期>.md
只读：全仓 + /home/szf/dev/Leibniz-KERT（**KERT 零写入**）
不采信 TL 的任何结论（含本提示词里的所有数字）。

## 范围：**只做**这 13 个仪器的「判定是否可能失败」分析（违规点分析视角）

先读 `evidence/prep/check-strength-coverage-gap.json`（含每个仪器承载的门禁与判定形态）。
工作清单（★ = 承载已登记门禁，优先）：
★ onto1_attribution_rebuild.py       门禁 2 ｜ wi_a1_baseline, wi_a1_attribution_selftest
★ onto1_cq_fixtures.py               门禁 2 ｜ wi_a6_cq_fixtures, wi_a6_cq_fixtures_selftest
★ onto1_d2_normalization_pack.py     门禁 2 ｜ wi_a5_d2_pack, wi_a5_d2_pack_selftest
★ onto1_d4_pack.py                   门禁 2 ｜ wi_a5_d4_pack, wi_a5_d4_pack_selftest
★ onto1_evidence_board_check.py      门禁 2 ｜ wi_evidence_board_check, wi_evidence_board_check_selftest
★ onto1_namespace_collision_check.py 门禁 2 ｜ wi_a4_namespace_collision, wi_a4_namespace_collision_selftest
★ onto1_product_refs_probe.py        门禁 2 ｜ wi_a5_product_refs, wi_a5_product_refs_selftest
★ onto1_reference_alignment_check.py 门禁 2 ｜ wi_a3_reference_alignment, wi_a3_reference_alignment_selftest
★ onto1_review_package_check.py      门禁 2 ｜ wi_review_package_integrity, wi_review_package_selftest
★ onto1_consumer_scan_tests.py       门禁 1 ｜ wi_a2_scan_mutation
★ onto1_w15_acceptance.py            门禁 1 ｜ wi_w15_a3_acceptance
  onto1_check_strength_audit.py      门禁 0 ｜ （无门禁，但为守卫/工具）
  onto1_pkg_audit.py                 门禁 0 ｜ （无门禁，但为守卫/工具）

**为什么是"违规点分析"而非"检查表分析"**：这些仪器不写 `(名称, 条件, 说明)` 三元组，而是
`findings.append({"code":…})` 收集违规 / `return 2` 表达失败 / `print("PASS/FAIL")`。
所以要看的是：**每条"失败路径"的触发条件是否可达**，而不是逐条判据读表达式。

## 每个仪器请回答四问（都要命令 + 原始输出）

1. **失败路径清单**：该仪器有哪些"能判 FAIL"的出口（违规码 / 退出码 / 打印分支）？逐一列出。
2. **可达性**：每条失败路径的触发条件，**在真实制品上是否可能为真**？
   存在"恒不触发"（⇒ 该仪器实际永不 FAIL）或"恒触发"（⇒ 永远红，等于没有判别力）的路径吗？
3. **构造性实验（关键手段）**：对任何"我怀疑它不可能失败"的判据，**必须**做实验证明——
   照 QA 第二轮对 A5 的做法：把该判据依赖的关键函数/字段**恒置为两个极端值**，
   看该判据是否**在两个极端下都 PASS**（都 PASS ⇒ 证明它不可能 FAIL）。
   请在报告里给出你改了什么（**只在临时副本或内存里改，不得动仓内制品**）与两侧结果。
4. **自检覆盖**：该仪器自带的 `--selftest` 是否覆盖了它在第 1 问列出的**每条**失败路径？
   未被任何用例覆盖的失败路径，请点名（这正是 QA 第二轮 N-1 的形态：判据死了，自检 5/5 也没发现）。

## 另外两项（低优先，可与上表并行）

5. 观察项复核（我未并入白名单，留给你判）：
   · `onto1_c2_generator_check.py:57` G0（`except` 里 append False —— 属 fail-closed 结论还是死路径？）
   · `onto1_sim_projection.py:142` G4（文本存在性校验 —— 是否等价于"读自我声明"？）
6. 我自审 v2 的**新结论**是否可信：`--scan` 现报 `226 条可审判据 / 15 候选 / 13 未审`。
   请抽 3 个仪器验证其抽取是否**无漏无假**（尤其：2 元组 / dict 式 / 字符串式 / 预计算变量四类是否真被抽到）。

## 出口（逐仪器）

`SOUND`（失败路径可达且自检覆盖）／`HAS_DEAD_PATH`（存在不可能失败或永红的路径，**必须附构造性实验**）／
`NOT_AUDITABLE`（我方法不足，说明为什么）——每条附你亲自执行的命令与原始输出。

## 禁令

**不得**记 `QA_PASS`（板面仍有 1 inconclusive，C-1b 待 D3）；不得改任何制品（含我的报告与脚本）；
不得代签；KERT 零写入。**不要重复** QA 第二轮已完成项（F-1~F-12、⑤⑧⑨⑩、N-1~N-6 均已在
`memory/handoffs/TL-ADJUDICATION-QA-W3R2-2026-09-21.md` 处置完毕）。
```

---

## 待人类-10｜**QA 第四轮：复核本轮修复 + 第二类覆盖缺口 + 三项未修判定**（独立会话）

> 为什么单列一轮：QA-3 修完的 4 条**尚无独立复核**（我自己跑的复跑不构成独立复核）；且 QA-3 指出审器对**两种判定形态**无识别能力，属**第二类覆盖缺口**；另有我**具名未修**的 3 条需独立判定。

```text
角色：ONTO1 独立 QA（**第四轮**）。独立性硬条件（三条同时满足）：① 非实现方；② 非本汇报方；③ 非临时兼任 PSO/ICO 者。
写域（唯一）：loops/ONTO1-ontology-split/memory/handoffs/INDEPENDENT-QA-W3R4-<日期>.md
只读：全仓 + /home/szf/dev/Leibniz-KERT（**KERT 零写入**）；**实验一律在临时副本或内存里做，不得动仓内制品**。
不采信 TL 的任何结论（含本提示词里的所有数字，请自己复算）。

## A. 复核 TL 本轮（QA-3 受理）的修复是否**真成立**（逐项做构造性实验）

1) **S-1 位移容忍的三向判别力**（`scripts/onto1_d2_normalization_pack.py` 的 `verify_ref`）：
   (a) **只位移**（在产品卡/ttl 前插两行使内容整体下移，但不改内容）⇒ 必须 PASS 且 gate 打印「位移已记账」；
   (b) 从被引用文件里**删掉某锚点的期望内容** ⇒ 必须 FAIL，且失败语为 `line content lost`；
   (c) 把某锚点的期望内容**复制成两份**（造成歧义）⇒ 必须 FAIL，且失败语为 `ambiguous anchor`。
   **(b)(c) 是本次新增的判别力证明，务必亲自做**（QA-3 的 S-1 只证明了原判据会红，未证明新判据能区分三类）。
2) `scripts/onto1_cq_fixtures.py`：把盘上 6 份夹具**复制到临时目录后篡改** ⇒ `gate(tmp, write=False)` 必须 FAIL；
   且 gate 运行**不得改写**该目录内容；确认**唯一**重生成入口是 `--build`。
3) `scripts/onto1_sim_projection.py`：篡改**盘上 SIM 制品副本** ⇒ `run_checks` 必须**只有 G8** 失败（失败语含 `SIM_ARTIFACT_DRIFT`）。
4) `scripts/onto1_d2_normalization_pack.py` G8：从 build 出的 pack 里**去掉 `prohibited_actions` 中的 R-6 项** ⇒ G8 必须 FAIL；
   再把声明截短到 <40 字 ⇒ G8 必须 FAIL。
5) `scripts/onto1_check_strength_audit.py`：自审 v2 现报 `227 条可审判据 / 14 候选 / 13 未审`（请复算核对）；
   确认 `--strict` 在 high 候选或未审存在时 **exit 2**；确认 `onto1_c2_generator_check.py:57` G0 的**误报已消除**（不应再作为 TAUTOLOGY_CONST 出现）。
6) **验 TL 没有把 FAIL 换口径**：`wi_a5_d2_pack` 的重记必须是**复算通过**——请自己跑 gate，并独立核对
   `EVIDENCE.json` 里该门的 `output_sha256` 与证据日志首行 `# artifact=` 是否一致。

## B. 第二类覆盖缺口审计（新范围）

QA-3 已指出：自审仪**不认识**两种判定形态——(i) **下标赋值 dict**（如 `report["checks"]["C-1b"] = {...}`）、
(ii) **`failures.append("字符串")`**。请在全仓 **45 个 `onto1_*.py`** 中把这两类**判定点**逐点找出来，
对每点用**违规点分析**审：该点是否**可达**、是否**可能 FAIL**、是否被该仪器的 `--selftest` 覆盖。
产出点位清单（`文件:行`）+ 逐点结论。

## C. 对 TL 三条「具名未修」给**独立判定**（只判、不改）

1) `scripts/onto1_namespace_collision_check.py:446-480` **C-4b 死防线**：真实布局下 `freeze_subjects` 恒为 0
   （两「车」都在 `loops/**`）⇒ 唯一防线恒不触发。请判定：应改**检测口径**，还是"无检测对象时应判 `NOT_EVALUATED`（不得给绿）"？
   并说明哪一条更贴合仓库既有 doctrine（R4：**空转 = 失败**）。
2) `scripts/onto1_product_refs_probe.py:102`（`raise`）与 `:196`（`failures.append("P1 …")`）：P1 是否**永不可达**？
   若把 P1 处理移到 `raise` 之前，**退出语义**会否改变？给最小实验。
3) `scripts/onto1_pkg_audit.py:105-110` **AU-5 恒红**（"Owner 已授权 SIM 整改"状态下）+ `recent_changes()` 恒 `[]`：
   是否需要引入**授权维 / 时间维**？请给**≥2 个候选口径与各自代价**——**不要给结论**，结论归 Owner。

## 不要重复（已结论）

QA-2 全部（F-1~F-12 · ⑤⑧⑨⑩ · N-1~N-6，见 `TL-ADJUDICATION-QA-W3R2-2026-09-21.md`）；
QA-3 全部（13 仪器的 SOUND/死路径判定、S-1 机理，见 `TL-ADJUDICATION-QA-W3R3-2026-09-22.md`）。

## 环境事实（供起步；**不许照抄**）

板面 84 = 83 pass / 1 inconclusive（`wi_a4_namespace_collision`，C-1b 待 D3）· `current = RETURN_TO_HLD` ·
`QA_PASS` 未记录 · 自审 v2 = 227/14/13 · `parallel_allowed` 已预登记 `qa-w3r4`。

## 出口

A 块：逐项 `ACCEPT` / `ACCEPT_WITH_CONDITIONS` / `NOT_ACCEPTED`；B 块：逐点 `SOUND` / `HAS_DEAD_PATH` / `NOT_AUDITABLE`；
C 块：判定 + 候选口径与代价。**每条附你亲自执行的命令与原始输出。**

## 禁令

**不得**记 `QA_PASS`；不得改任何制品（含 TL 的脚本与报告）；不得代签；KERT 零写入；
实验只在**临时副本或内存**内做（QA-3 的做法可参照：`write=False` / `out_dir=/tmp` 等价入口）。
```

---

## 待人类-11｜**未授权 / 空转该判什么：AU-5 与空转子检查的统一口径**（Owner）

> 来源：QA 第四轮 C-3（只给候选口径与代价，**不给结论**）+ C-1 的同一语义轴。
> **TL 不单方定口径**（涉及"授权范围的书写与签认方式"）。

```text
角色：项目 Owner（口径裁定）
事项：两条相反偏差必须用**同一个口径**决定 ——
  (a) **空转给绿**：`namespace_collision_check` C-4b 的冻结域在真实布局下恒为空（已由 TL 改为「空转 ⇒ INCOMPLETE exit 3，永不 0」）；
  (b) **授权后恒红**：`pkg_audit` AU-5 在「Owner 已授权 SIM 整改」状态下恒红（实测 `--redlines` exit=2）；
      `recent_changes()` 恒 `[]`（mtime 不可归因，QA 有实测证据）。

QA 给出的候选口径（各自带代价，见报告 §4.3）：
  AU-5：① 引入**授权维**（授权引用台账，逐条指向 Owner 决定）② 引入**时间维**（授权生效日之后豁免）
        ③ **目录分级**（哪些目录在授权内/外）④ **三值输出**（PASS/FAIL/NOT_EVALUATED，授权内=NOT_EVALUATED 而非 PASS）
  recent_changes()：① 仅披露不判据 ② mtime 入判据（代价：mtime 不可归因）③ 改走 git（可归因但需权限与稳定性）

请回复：选择口径编号（可组合），并给出「授权范围的书写格式」与「谁签认」。
约束：本口径将同时用于 `board_expression` 是否新增 `NOT_EVALUATED` 分列；一旦定下，TL 按此统一落地并重记相关门禁。
```
---

## 附：以上事项**都不阻塞**的已完成工作（不需要你决策）

C-2 修复与消费者扫描 · D2 分流（28/12） · D3 临时口径 · A-1~A-16 全部 SIM 侧交付（含 462 条批次演练、三出口对比、迁移器骨架、施工清单、执行包、KERT 请求草案）——
均在 `loops/ONTO1-ontology-split/evidence/prep/` 与 `evidence/` 下，可复算、可审计；**门禁值一律未提升**。

## 待人类-12｜**检索层启用三前提（LightRAG）**（Owner / KERT 侧 / PC8 tech_lead 分头）

一句话：检索层「服务 + 索引 + 端点」**已实测可用**（`HTTP 200`，可召回实体/关系/出处），但**启用三前提全部未满足**
⇒ 现在**不得**声称任何业务「已接入 LightRAG 召回」。

- **可复算**：`python3 scripts/onto1_retrieval_layer_diag.py --scan` ⇒ 现为 `OK 2 · DEFECT 3 · CONTRADICTION 1`
- **落地包**：`loops/ONTO1-ontology-split/evidence/prep/RETRIEVAL-LAYER-ENABLEMENT-PACK.md`
- **制品**：`loops/ONTO1-ontology-split/evidence/prep/retrieval-layer-diag.json`（`gateCandidate=false`）

| # | 前提 | 现状（实测） | 归属 | 需要你做什么 |
|---|---|---|---|---|
| ① | **真实模型** | `LLM_MODEL=mock`（CI 假模型 `:9630`）⇒ 抽取层非真实能力 | **Owner** | 决定是否换真实模型（成本/合规），或明确「长期保持 mock ⇒ 检索层永久标记为试验，不得作业务结论依据」 |
| ② | **`simulationOnly` 派生** | 响应为**字面量** `False`（KERT `src/kert/api/server.py:755`），与 `experiment_config.json` 的 `true` **相反**，索引内容含 `isDemo: true` | **KERT 侧** | 受理修复（改为派生 + 配置/响应/L6 口径三处同值 + 反例夹具）；**GITS 侧不改** |
| ③ | **契约先行 + 消费后接** | 端点未进合同（`specs/` 零命中）⇒ PC8 三门禁 `contract_generate`/`contract_check`/`unified_gate` **均 pending**；GITS 侧 `apps/api/src`、`frontend/src` **零引用** | **PC8 tech_lead** → 产品解读场景实现方 | 推进 `make generate` / `make check` / `check_all.py` 与消费侧接入（含不可达时的缓存/离线路径） |

**口径陷阱（请勿误用）**：PC8 统一门禁 `python3 specs/product-knowledge/check_all.py --gits-only` 现为 `PASS 5 · FAIL 0 · SKIP 6`，但它**不检查新端点是否进合同**
⇒「统一门禁绿」**不等于**「端点已进合同」，不得替代 `contract_check`。

**我不做（不因授权而变）**：不改 KERT（**零写入**）· 不跑 `make generate`（写 `generated/`，我 scope 内只读）· 不登记 PC8 门禁 · 不代 Owner 决定换模型 · 不代签。

**三方移交单（含各自执行单/补丁提案/验收判据）**：`loops/ONTO1-ontology-split/evidence/prep/RETRIEVAL-ENABLEMENT-3WAY-HANDOFF.md`

**追查补记（应要求追到底）**：`KERT 今日写入 104 件` 已逐件归因，**全部非我方**、最晚本地 `15:15`（早于本轮 8 小时）——
3 件 Python 导入缓存（`src/kert/**/__pycache__`）· 4 件 **API 触发的一次成功 skill 作业**（`JOB-SKILL-20260923-016`，`COMPLETED`，28.2s）· 97 件 **按声明安装的 duckdb**（`pyproject.toml:28` 已声明，`INSTALLER: pip`）。
⇒ **口径更正**：此后不得笼统说「KERT 今日零写入」；正确说法是「**本轮零写入**；今日 104 件为非我方」。
**追查副产**：另发现 3 处口径漂移 + 1 处同仓矛盾（索引位置 `ADR-017` 声明 `/home/szf/dev/lightrag/rag_storage` vs 运行实例 `/tmp/lightrag-storage` · M7「不引入 LightRAG」已被 Owner `D-31` 推翻但正文未加指针 · `sim_bank_front.py` 规定仿真须标 `true` 而 `server.py:755` 写死 `False`），详见移交单 §0.2。

**② 最新状态（2026-09-23）**：**已在你的授权下落地** —— KERT `src/kert/api/server.py` 新增派生函数（只读出处产物的 `provenanceState`，守 CR-5 边界 5「不得取自检索」）+ 夹具 6 例；单元 6 passed、真实工作区端到端 `200` 且 `simulationOnly=True`、强变异 4 条反例可捕获；**未 commit**（KERT Rule 10）。
已了结两件：(a) **已重启 KERT 技能服务**（授权内，只重启 KERT；精确复制原 env 113 项 + 覆盖 3 项）⇒ 运行态生效、诊断仪 `D7=OK`、返回 `provenanceState=DEMO`/`simulationOnly=True`；
(b) **已按你裁定增设 `provenanceState`**（与 `simulationOnly` 同源派生；取值域取契约 enum `VERIFIED`/`DEMO`）——并修掉我首版误用 `PRODUCTION`/`AUTHORITATIVE` 的口径错误。
**仍缺**：① 真实模型选型（`evidence/prep/RETRIEVAL-MODEL-SWITCH-ONEPAGER.md`：Ollama **可用**，建议方案 A＝`qwen3:8b` + `all-minilm:l6-v2`，**零下载**）；② PC8 侧端点进合同与三项门禁。

**① 已授权并已执行**（见上）。**② 仍缺**：真实 LLM/embedding 的 `host/model/key/合规口径`（凭据与成本必须你给，我不自接）。

**已同步进「产品解读重构」场景提示词**（`evidence/prep/PROMPT-PRODUCT-REINTERPRET-MANAGER.md` §5/§6/§8/§9）：
「检索层可预留消费位，但当前 `lightragEnabled=false`、LLM 为 mock、`simulationOnly` 不可信 ⇒ **不得声称已接入**。」
