# TL 审计报告｜W-1.5 PKG-A1（义务回源确认）

| 项 | 值 |
|---|---|
| 审计人 | 全局 Tech Lead（main） |
| 被审包 | PKG-A1 / `pilot-a1` |
| 审计时间 | 2026-09-20T23:50Z |
| **结论** | **ACCEPT**（2 门禁已登记；4 项裁定见 §7；1 项后续小包 PKG-A1b） |

---

## 1. AU-1 交付物哈希（**通过，且冻结稳定**）

| 制品 | 声明 | TL 实测 | 判定 |
|---|---|---|---|
| `scripts/onto1_obligation_triage.py` | `1982a9ec…` | `1982a9ec2017df97` | ✅ 逐字一致 |
| `evidence/obligation-triage.csv` | `81e5ebc4…` | `81e5ebc414df576c` | ✅ |
| `evidence/obligation-triage-summary.json` | `325910ba…` | `325910baeac0a402` | ✅ |
| `evidence/PKG-A1-义务收敛报告.md` | `89428f09…` | `89428f094a2af351` | ✅ |

**两次取样间隔 4 秒哈希不变**（对照 PKG-A3 的 `W15A3-01` 脱钩问题：A1 **未复发**，交付后未再改动）。

## 2. AU-2 复跑门禁（TL 亲自）

| 模式 | TL 实测 | 声明 | 判定 |
|---|---|---|---|
| `--gate` | **exit=0**（G1~G8 全绿） | 0 | ✅ |
| `--selftest` | **exit=0，11/11 用例符合预期** | 11/11 | ✅ |

## 3. AU-3 回源抽查（通过）

1. **对账闭合**：磁盘 CSV `TRUE_OBLIGATION=626 / NEEDS_SOURCE_CHECK=426 / 合计 1052` ✅ 与其声明一致；`tier`: STRONG 626 / MEDIUM 329 / WEAK 97 ✅。
2. **Wave 归属**：`W3_CONSUMER_SWITCH=316 / W2_SPLIT=291 / W3_KERT_ASSETS=19` ✅。
3. **证据可回源（抽样 8 条带行号）**：文件均存在、行号均在范围内；内容级信号逐条吻合，例：
   - `kert/src/kert/domain/knowledge_source.py:73` ← 行内含 ``planHash``（信号 `STRONG_CONTENT:PLAN_HASH`）
   - `specs/knowledge-architecture/schemas/knowledge-map.schema.json:3` ← 行内含 `gientech.com/gits/kno/...`（`IRI_GIENTECH`）
   - `scripts/gk17_prodcard_to_rdf.py:31` ← 行内含 `https://gits.bank.example/ontology/core#`（`IRI_BANK_EXAMPLE`）
   - `modules/operational-ontology/.../port/CustomerRepository.java:3` ← `import com.gien.gits.ontology.Customer;`
   > **TL 自我更正**：首轮我用"信号标签文本 vs 行文本"做自动比对，误得"8/8 文不对"——`signal` 列是**规则标签**（如 `STRONG_PATH:R-…`）而非行内文本，是我的判据写错；逐条人工回源后**全部吻合**。撤回该质疑。
4. **争议项「派工单弱面前缀在本批 0 行」**：严格 `path.startswith` 复核 `frontend/ tests/ adapters/persistence-relational/ evidence/ loops/` **全为 0** ✅ 声明属实（我最初按"任意路径段"匹配得到的 5 行实为 `specs/.../tests/`、`specs/evidence/`，非顶层前缀）。
5. **P0 标签**：`RESOLVES_TO_ONTOLOGY_PKG = 65` ✅ 与声明一致。

## 4. AU-4 独立变异（TL 自建，**全部被具名拦下**）

| 变异 | 实测 |
|---|---|
| MU-0 对照 | `exit=0` |
| MU-1 删 1 行 TRUE | `exit=2` + `G2 reconciliation not closed: 625/0/426 sum=1051 baseline=1052` + `G7 row count drift` ✅ |
| MU-2 证据行号改 999999 | `exit=2` + `G4 evidence line out of range` + `G7 drifted from recomputation` ✅ |
| MU-3 Wave 改 `W9_BOGUS` | `exit=2` + `G6 true obligation without actionable wave` ✅ |
| MU-4 还原对照 | `exit=0`，CSV 哈希**逐字回到** `81e5ebc414df576c` ✅ |

⇒ 其 F-4 修正（磁盘 + 复算**双向**）**有牙齿**；`G7` 在所有变异中同步触发，证明它不是装饰。

## 5. AU-5 红线

`git status --porcelain -- generated/ specs/ docs/dd/` = **0**；KERT 侧 `ontology_reference.py` mtime 仍为 **2026-09-16 18:18**（远早于本包窗口）；未见越写 TL 单写者文件、未 `git add`、未代签任何门禁。

## 6. AU-6 记账（2 门禁已登记）

| gate id | 命令 | exit | 状态 |
|---|---|---|---|
| `wi_a2_obligation_triage` | `python3 scripts/onto1_gate_log.py scripts/onto1_obligation_triage.py --gate` | **0** | pass |
| `wi_a2_obligation_triage_selftest` | 同上 `--selftest` | **0** | pass |

板面 **30 门禁 = 29 pass / 1 fail**（唯一 fail = `wi_a4_namespace_collision`，C-2 真实冲突）；`loop-guard: PASS`、`onto1-evidence-board: PASS`。
日志已按 **D-11** 自证 revision（`# artifact=scripts/onto1_obligation_triage.py@1982a9ec2017df97 sha256=…`）。

## 7. TL 裁定（4 项，A1 上报的"需你裁定/执行"清单）

| # | 议题 | **裁定** |
|---|---|---|
| **I-6** | 65 行 P0（裸名精确解析到本体/领域模型包）是否升格 | **升格为 TRUE_OBLIGATION / Wave=W3_CONSUMER_SWITCH**（fail-closed 方向：显式 `import com.gien.gits.ontology.<类>` 是对本体模型的**代码级耦合**，四层拆分若改命名空间/包结构，消费面必须跟随）。**附加硬条件**：① 保留 `PROOF:IMPORT_LINE` + `RESOLVES_TO_ONTOLOGY_PKG` 标签；② Wave 2 抽检**必须优先覆盖这 65 行的前 5 行**，逐一确认包语义（防"同名包无关"）；③ 若抽检推翻，按证据回退并留痕。⇒ 真义务 **626 → 691**，待回源 426 → 361 |
| **I-2** | 同名口径（严格 H2 vs tier=WEAK 即同名） | **采纳 A1 主口径（严格 H2，同名=0，含义为"无**可证明**者"）**；把替代口径（同名 97 / 待回源 329）**作为敏感性分析保留**于报告，并要求 Wave 2 抽检时**优先抽 WEAK 面**（同名风险最高区）。删除"文件自述来自 OpenAPI 合同"这一过宽证明（其 F-5）**予以背书**——过宽证明会误排真消费面，是更危险的错 |
| **I-1** | 弱面并入 `**/src/test/**`、`**/dto/**` | **接受**；并要求如实声明"派工单列举前缀在本批 0 命中"（已声明 ✅） |
| **阈值** | 真义务 > 400 行 | **触发**：已回写 `evidence/WBS-RESTIMATE.md` 并在 `W-1.5-ORCHESTRATION.md` §5 新增风险项（见 TL 当日动作） |

## 8. 后续小包 **PKG-A1b**（1 项）

### 8.1 状态：**已完成（2026-09-21T00:58Z，由 TL 代实现）**

> **角色偏离登记（如实）**：原认领人 `pilot-a1` 所属 team `onto1-w15` **已结束/不可寻址**，而 `STATE.json.implementation_actor = tech_lead` ⇒ **由 TL 以实现角色代做**。QA 独立性不受影响（第三方复验仍待 QA 第三轮）。

**实现（`scripts/onto1_obligation_triage.py`）**：新增集中开关 `RULING_I6_UPGRADE_P0 = True` 与 `P0_IMPORT_PROOF = "PROOF:IMPORT_LINE"`；两处 P0 分支（弱面 / 中信号面）在**机械导入证据**成立时升格为 `TRUE_OBLIGATION` + `WAVE_W3`（`W3_CONSUMER_SWITCH`），**保留** `RESOLVES_TO_ONTOLOGY_PKG:<pkg>` 并**新增** `PROOF:IMPORT_LINE`；证据取该 `import` 行。**G5 例外**：`tier==WEAK ∧ TRUE` 仅在**同时**含这两种标记时放行。
> **⚠️ TL 更正（2026-09-21T01:20Z，`FAIL-2026-09-20-W15TL-09`）**：本报告原写「该证据还须通过既有『精确导入该包』二次校验」，**该表述与实现不符**——那段校验当时**缩进出循环、是死代码**（对 65 行 P0 覆盖 **0/65**；TL 用"把 65 行包名全改成不存在的包 ⇒ 命中 0"实证）。由 `qa-w15r` 第三轮判为 BLOCKER。**已修复**：该块移入循环（逐行、覆盖全 tier），并新增 **M9b-3**「全部 P0 行改包名 ⇒ 命中数须 == 行数」回归断言（夹具中 P0 行移到非末位；退化副本复现死代码 ⇒ M9b-3 **FAIL**，修复版 **14/14**）。**这类"以引用既有防线为由批准放宽"的自证链断裂，已按最危险类别记账。**

**结果（TL 实测）**：

| 项 | 值 |
|---|---|
| 真义务 / 待回源 / 合计 | **691 / 361 / 1052**（对账闭合；升格前 626 / 426 作为对照保留） |
| 真义务按 Wave | `W3_CONSUMER_SWITCH 381`（= 316 + 65）· `W2_SPLIT 291` · `W3_KERT_ASSETS 19` |
| P0 行 | **65 行全部升格**，且 **65/65** 带 `PROOF:IMPORT_LINE` |
| `--gate` | **exit 0**（G1~G8 全绿） |
| `--selftest` | **exit 0，13/13**（原 11/11；**M9 断言随裁定更新**为"升格真义务(W3) + 双标签"，并**新增两条 D-12 反例**：**M9b-1 开关回退 ⇒ 回落 NEEDS**（证明可回退）、**M9b-2 剥掉 `PROOF:IMPORT_LINE` 而保留 P0 标签 ⇒ G5 必须 FAIL**（证明例外是**条件性**的，不是"弱面判 TRUE 一律放行"）） |
| 新哈希（交付时实测） | 脚本 `f3603a24ee86f5ee` · CSV `58671a908bae8d7d` · summary `f7dd5d4b93ba0aac` · 报告 `d93488c2a00e28c0` |
| 门禁记账 | `wi_a2_obligation_triage` / `_selftest` **已按新输入重跑重记**（日志自证 revision） |

### 8.2 对照 M9 断言更新的**透明声明**

M9 原断言"P0 ⇒ 待回源"被裁定 I-6 **取代**。本次是**放宽型**改动（把 65 行从"待回源"移入"真义务"），因此按 **D-12** 强制配套反例（上表 M9b-1/M9b-2），并有 TL 侧独立变异（MU-4：剥掉 P0 标签 ⇒ G5 FAIL）。**这不是"为过门禁而改断言"，而是"裁定落地后断言必须跟随"**；原 626/426 口径与 11/11 版本的日志均已**按白名单保留为历史 attempt**（取证链完整）。

### 8.3 下发给 Wave 2 的硬义务

**必须按包抽检 P0 面**（`com.gien.gits.ontology` 55 / `com.gien.gits.action.domain` 6 / `…ontology.domain` 4），**每个包至少抽 3 行**逐一确认包语义；若抽检推翻 ⇒ **按证据回退**（开关置 False 即回到 626/426）并留痕。
> **TL 更正（2026-09-21T01:20Z，采纳 `qa-w15r` U-8）**：原写"优先抽检前 5 行"，但 65 行的包分布为 **55/6/4**，前 5 行**必然全部落在 55 那一包里** ⇒ 覆盖不到另外 10 行；且 **6 行解析到 `com.gien.gits.action.domain`（实际模块为 `modules/human-action`，并非 L1 本体模块）**，对这 6 行而言"对本体模型的代码级耦合"是**推断而非事实**，必须**优先单独确认**。按包分层抽样是本次修正后的硬性口径。

## 9. 非声明

不构成 `QA_PASS`/`DEV_SELF_CHECK_PASS`（本 Loop 仍有已知 fail）；不覆盖 Wave 0/1/2+；未对 KERT 侧做任何判断；本报告结论绑定 §1 的**实测哈希**。
