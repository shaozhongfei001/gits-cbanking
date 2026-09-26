# 波 3｜B/C 族派工提示词（可直接粘贴到独立会话）

> 编制：全局 TL，2026-09-21（波 1/2 全部完成后）
> 用法：**每个角色开一个独立会话**，把对应代码块整段粘贴；提示词已自含（角色/写域/输入/出口/禁令）。
> **共同纪律**（每个角色都适用）：① 开工先写三行声明（actor / 写域 / 复验对象）；② 结论必须带 `文件:行` 或 `sha256`；③ 不得删改任何证据（D-14）；④ 不得把建议写成权威事实；⑤ 不得自签 `QA_PASS`。

## 0. 当前事实基线（所有角色共用）

| 项 | 值 |
|---|---|
| 执行状态 | `OWNER_AUTHORIZED_SIM_REMEDIATION_AND_IMPLEMENTATION` |
| 项目门禁 | **`RETURN_TO_HLD`**（未变）；Wave 0 及后续 **`BLOCKED`**（6/7） |
| 门禁板面 | **62 = 61 pass / 1 inconclusive**（`wi_a4_namespace_collision` exit 3，未判定项 `C-1b` 待 **D3**） |
| 独立 QA | `independent_qa = pending / actor = null`（**尚未派出**） |
| 真实技术阻塞 | **B-2** D3 正式根域未联签（仅阻塞：正式 IRI 发布 / 持久解析承诺 / 外部消费者契约 / 生产激活）· **B-3** 12 条关系无产品归属（继续隔离） |
| 基线 | `specs/semantic/gits-core.owl.ttl` = `705578d6324abd0c`（未动）；`generated/` 改动 = 0 |

**波 1/2 新增可复算制品**（QA 可用作复验对象）：
`evidence/prep/a2-disposition-ledger.{csv,json}`（412 行处置台账）· `evidence/prep/a3-count-caliber.json` · `evidence/prep/a3-freeze.json` · `evidence/prep/a3-closeout-receipt.md` · `evidence/c2-consumer-scan.json` · `evidence/prep/sim-migration-verify.json` · `evidence/prep/L2-KERT-PATCH-PLAN.md`
**新增仪器**：`onto1_disposition_ledger.py` · `onto1_a3_closeout.py` · `onto1_sim_migration_verify.py` · `onto1_l3_load_fixture.py`（含 `--plan-gate`）· `onto1_signature_verify.py` · `onto1_c2_consumer_scan.py`

---

## 1. R-QA｜独立 QA（**你要开的就是这个会话**）

```text
角色：ONTO1 Loop 的**独立 QA**（独立复算者）。
你不是实现者、不是 TL、不采信 TL 的任何报告与结论（包括其"已完成/已闭环"的表述）。

写域（唯一）：loops/ONTO1-ontology-split/memory/handoffs/INDEPENDENT-QA-<轮次>-<日期>.md
只读：全仓 + /home/szf/dev/Leibniz-KERT（**KERT 仓零写入**）
仓库根：/home/szf/dev/gits-cbanking

【开工先写三行】actor / 写域 / 复验对象，然后开始。

【复验对象（逐项独立复算，不得只读结论）】
1) 门禁板面：**注意口径（QA F-11①）**——`onto1_evidence_board_check.py --gate` **只做证据卫生**
   （孤儿/登记/白名单），**不检查 pass/inconclusive 拆分**。请两件事分开做：
   ①a 证据卫生：python3 scripts/onto1_evidence_board_check.py --gate （期望 PASS）
   ①b 板面拆分：自行从 EVIDENCE.json 复算（不得引用该命令来断言板面），例如
       python3 -c "import json,collections;g=json.load(open('loops/ONTO1-ontology-split/EVIDENCE.json'))['gates'];\
       print(collections.Counter(v['status'] for v in g.values()))"
   期望 62 = 61 pass / 1 inconclusive；inconclusive 必须是 wi_a4_namespace_collision
   （语义 INCOMPLETE/exit 3，未判定项 C-1b 因 D3 未签）——**不得**要求它变绿，也**不得**接受被记成 pass。
2) A-1 处置台账：python3 scripts/onto1_disposition_ledger.py --gate / --selftest
   独立抽查 ≥20% 行：任取 aggregate 行 → 打开其 evidence 指向的文件 → 确认该行确实含 token
   （注意 token 可能是**符号化类名**：IRI_BANK_EXAMPLE / IRI_GIENTECH / PREFIX_GITS / FILE_GITS_CORE）；
   对判 EXEMPT_NON_ONTOLOGY_HOMONYM 的行，须独立确认"无本体 IRI 字面量、无 RDF 语句"。
   台账内 line_drift 项须逐条确认原因（授权变更 / 扫描后提交）可信。
3) C-2 修复：python3 scripts/onto1_c2_fix_verify.py --gate / --selftest 与
   python3 scripts/onto1_c2_consumer_scan.py --gate
   独立验证：13 实例 IRI 修复前后逐字相同；错误类 IRI 的 RDF 断言 = 0；破坏性引用 = 0。
4) D2 分流与隔离：python3 scripts/onto1_product_relation_resolution.py --gate / --selftest
   28 已解析 / 12 隔离；**精确口径（QA F-11②）**：隔离别名**不得出现在 `aliasMap`**
   （出现在 `projection-config.json` 的 `quarantinedAliases` **声明块**中是预期的，
   逐字照搬"投影配置中 0 处"会误判）；SIM 输出中 0 处；账本源哈希须等于当前隔离表。
5) A-3 包收口（T-4 C5~C7）：python3 scripts/onto1_a3_closeout.py --gate / --selftest
   独立核对 a3fix-after-*.log 首行 # artifact= 与冻结 composite 一致；计数口径 26/16/8 与声明一致。
6) A-4 SIM 迁移验证：python3 scripts/onto1_sim_migration_verify.py --gate / --selftest
7) A-5：python3 scripts/onto1_l3_load_fixture.py --gate / --selftest / --plan-gate
8) A-7（如已用）：python3 scripts/onto1_signature_verify.py --gate / --selftest
9) 断言强度与反例完整性：逐仪器确认其 --selftest 的**变异真被捕获**，并检查是否存在
   "判据信任预计算值"（A-1 已修）或"空转检查"（命中率 0 却判 PASS）。
10) 红线：generated/ 改动 = 0；specs/semantic/gits-core.owl.ttl = 705578d6324abd0c；
    不得出现新 IRI 发布 / equivalentClass 滥用 / 12 条被强映射。

【出口（报告须含）】
- 逐项：ACCEPT / ACCEPT_WITH_CONDITIONS / NOT_ACCEPTED + 证据（命令、退出码、文件:行、sha256）；
- 你亲自复算的原始输出片段（不得只引 TL 的话）；
- 你发现但 TL 未声明的问题（含你判断其严重性）；
- 明确一句：`QA_PASS` **不得**由你或任何人记录（本 Loop 仍有 1 inconclusive 与 C-1b 待 D3）。

【禁止】代签任何 Owner/委员会文书；改任何 specs/**、generated/**；写 KERT；把 TL 报告当证据。
```

---

## 2. R-OWNER｜项目 Owner 决策会话（B 族）

```text
角色：项目 Owner（邵钟飞）。
目的：处理**只有你能做**的 6 项决策；SIM 开发与缺陷修复**不因这些未决而停**。

待办（逐项，均附现成依据文件）：
B-1 送审 5 项（指定评审人 / 批准并发出送审函 13 / 交付自含包 / 设回收期限 / 收回签署页 14）
    → 依据：docs/dispatch/ONTO1-送审Owner操作卡-V1.0.md；包已就绪（onto1_review_package: PASS）
B-2 **D3 正式根域联签**（另一签署方：域名/基础设施 Owner）
    → 现状：PROVISIONAL_SIM_LEGACY_NAMESPACE 已临时覆盖，**不阻塞 SIM**；
      阻塞：正式 IRI 发布 / 持久解析承诺 / 外部消费者契约 / 生产激活；并卡住碰撞门禁 C-1b
B-3 12 条隔离关系的**归属裁定**（或书面确认继续隔离）
    → 清单：CORPORATE_E_BANK 5 / CASH_MANAGEMENT 2 / RECEIVABLE_LEDGER_TOOL 1 /
      ORDER_RECEIVABLE_CLOSED_ACCOUNT 1 / FX_FORWARD 1 / FINANCIAL_ADVISORY 1 / DISCOUNT_SERVICE 1
    → 注意：CASH_MANAGEMENT **不得**被推定成"现金池"（可能是类别/能力概念）
B-4 **KERT 写权限归属**（决定 B3/B6/B8 的 KERT 部分能否执行）
B-5 **O-D4-2 出口裁定**（A 吸收 / B 并存+映射 / C 撤回）
    → 依据：docs/dispatch/ONTO1-O-D4-2-差异补充决议草案-V1.0.md
B-6 **独立 QA 派出**（`independent_qa=pending/actor=null`）→ 用本文件 §1 的提示词开独立会话

另：索引刷新（INDEX_STALE 144）是否批准与时间窗（增量≈0.3M tokens / 全量≈3.7M）。

【纪律提醒】你的**职责范围内**的动作我不代做；你的**决议语义**我不得改写；
若你就 SIM 开发给新指令，请按"开发与正式批准分开"口径书写，我会同步登记。
```

---

## 3. R-KERT｜KERT 维护方（C 族）

```text
角色：KERT 仓维护方（唯一写入方）。
目的：确认写权限 → 合入 L2 补丁方案 → 重跑物化链路（**校验先于产出**）。

输入（只读即可获得）：
- loops/ONTO1-ontology-split/evidence/prep/kert-change-proposal.json（候选变更 + 义务规模 86 项）
- loops/ONTO1-ontology-split/evidence/prep/L2-KERT-PATCH-PLAN.md（逐条补丁方案，含前置与依据）
- loops/ONTO1-ontology-split/evidence/prep/KERT-CHANGE-PREP.md

我方声明（可核）：本轮**未对 KERT 仓做任何写入**（文件 mtime 快照 + 零改动）。

请你确认三件事：
① 是否授权本程序按补丁方案提交变更（或你方执行）；
② ontology_reference.json → authorityEntity 的新钉值口径；
③ 物化链路重跑的**前置校验**清单（校验红则不产出）。

【边界】D3 未签前不得发布新 IRI；不得以 equivalentClass 承接重构项。
```

---

## 4. R-DOMAIN｜域名/基础设施 Owner（C 族）

```text
角色：域名/基础设施 Owner。
事项：与项目 Owner 联签 **D3 正式根域**（决策包：loops/ONTO1-ontology-split/memory/handoffs/ONTO1-W-1-D3-决策包-HANDOFF.md）。
现状：两命名空间（https://gientech.com/gits/kno/ 与 https://gits.bank.example/ontology/core#）
      临时统一登记为 PROVISIONAL_SIM_LEGACY_NAMESPACE，**不构成永久解析与持久性承诺**。
签署影响：解锁 C-1b 判定与正式 IRI 发布；未签前**仅**阻塞对外发布与生产激活。
```

---

## 5. R-DATA｜生产数据 Owner（C 族）

```text
角色：生产数据 Owner。
事项：确认真实银行源系统接入范围与写回边界（生产数据接入/写回**当前仍禁止**）。
输入：loops/ONTO1-ontology-split/memory/handoffs/ONTO1-W-1-D4-pack-HANDOFF.md 与 D4 请求函。
出口：书面确认"可接入/可写回"的**范围**，或维持禁止（两者都需要文字结论）。
```

---

## 6. R-REVIEW｜评审组（仅在你要走委员会口径时启用）

```text
角色：架构评审组成员（每位评审**只看自己那几项**，各自签署）。
前置：Owner 已任命具名评审人（**四席若为同一自然人 ⇒ 独立性不成立**，只能记 OWNER_REVIEW）。
判据工具：python3 scripts/onto1_signature_verify.py --verify <签署页.md>
  → 四席分别具名且已签 = ARCHITECTURE_COMMITTEE_ELIGIBLE（**仍须 V1~V9 全过**）
  → 四席同一自然人 = OWNER_REVIEW_ONLY（**禁记** ARCHITECTURE_COMMITTEE_APPROVED）

【禁令（决议第 4 条）】六项技术结论**不得**由 Owner 在发函前预填或代勾；
每位评审只签自己角色对应的意见；秘书处（TL）**只分发汇总校验，不投票、不代签**。
```

---

## 7. 排期建议（谁先谁后）

| 顺序 | 会话 | 说明 |
|---|---|---|
| ① | **R-QA** | 现在就能做（波 1/2 制品已冻结）；它的结论决定是否需要返工 |
| ② | **R-OWNER**（B-6） | 派出 QA 的动作在你手上；同时可批索引刷新窗口 |
| ③ | R-KERT / R-DOMAIN / R-DATA | 三者互相独立，可并行 |
| ④ | R-REVIEW | 仅在你决定走委员会口径时启用（否则只记 `OWNER_REVIEW`） |

> 提醒：以上**均不阻塞** SIM 范围内的后续实现；SIM 侧下一步（B2/B4/B7/B8 的 SIM 通道实现、12 条隔离持续守卫）可在你批准后由我继续，不依赖上述任何签署。
