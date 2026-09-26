# 独立 QA 报告（第三轮）｜ONTO1 W-1.5 就绪加固

| 项 | 值 |
|---|---|
| QA actor | `qa-w15r`（独立复算，**不采信 TL 报告**，含 TL 的审计报告与派工结论） |
| 日期 | 2026-09-21 |
| 工作目录 | `/home/szf/dev/gits-cbanking`（**只读**；KERT 仓零写入） |
| 写域 | 本文件（唯一写入） |
| 复验对象 | PKG-A1 / PKG-A1b（TL 代实现）· PKG-A2 · PKG-A3 · 红线与板面 |
| **结论** | **NOT_ACCEPTED**（见 §1） |

**开工声明（三行）**

```
[索引] INDEX_STALE(gits 索引 .ua/meta.json commit=7116904 @ 2026-09-15T17:48Z；本 Loop 期间 HEAD 已大幅前进；KERT 侧一律只读、未取索引)
[索引] 候选影响面: scripts/onto1_{obligation_triage,namespace_collision_check,reference_alignment_check,w15_acceptance,gate_log,evidence_board_check}.py · loops/ONTO1-ontology-split/{EVIDENCE.json,FAILURES.md,memory/TL-DECISIONS-W-1.md} · evidence/obligation-triage.csv
[回源] scripts/onto1_obligation_triage.py:757-773（G5 标签校验缩进）· onto1_namespace_collision_check.py:535-553（输入存在性闸门）· :425-439（REQUIRED_PINS 文件存在性）· onto1_reference_alignment_check.py:288-296（classify_line）· evidence/obligation-triage.csv:68 起 65 行 P0
```

---

## 1. 结论

**NOT_ACCEPTED。** 逐项：

| 组 | 结论 | 关键依据 |
|---|---|---|
| **R1** TL 代实现的 PKG-A1b（I-6 升格） | **事实层通过 + 一处 BLOCKER 级空转** | 691/361、381、65/65 回源全部复现成立（§2.1）；但 **G5 的 `RESOLVES_TO_ONTOLOGY_PKG` 标签二次校验是死代码**，对 65 行 P0 **覆盖 0/65**（§2.3），而 TL 审计报告 §8.1 明文声称该二次校验存在（§2.4） |
| **R2** 四个陈旧门禁重记 | **通过** | 5/5 日志含 `# artifact=<脚本>@<sha256>` 且**等于磁盘实测**（§3） |
| **R3** A3 的 C1~C4 独立复现 | **通过** | 四例在我自建沙箱全部复现；验收仪器的判定函数经我加控制组验证**无假阳性**（§4） |
| **R4** 红线与板面 | **通过（含 2 项板面卫生发现）** | 受控目录 0 改动、KERT 今日零写入、四门禁全 PASS、板面 31=30/1（§5） |

**不得记 `QA_PASS` / `DEV_SELF_CHECK_PASS`**：本 Loop 存在**已知未关闭 fail**（`wi_a4_namespace_collision` exit=2，C-2 两处真实前缀冲突未修，属 Wave 3），`ready_for_independent_qa` 硬约束未满足；本报告亦**不构成**任何门禁签署。

---

## 2. R1｜PKG-A1b（I-6 升格）独立复算

### 2.1 计数口径与逐条回源（**成立**）

命令与实测（原始输出摘录）：

```
$ sha256sum scripts/onto1_obligation_triage.py loops/ONTO1-ontology-split/evidence/obligation-triage.csv ...
f3603a24ee86f5ee3cdc16d3fc4d885de87a8bd4577bd61b1d14cc5c66b0dc10  scripts/onto1_obligation_triage.py
58671a908bae8d7dd533e0aee7fbc6146f49eef983c3574e92367e2f8576b547  .../obligation-triage.csv
f7dd5d4b93ba0aacafb9859fb7229cb0b20f30f7f37de6ba13ab962cefce4190  .../obligation-triage-summary.json
d93488c2a00e28c0ea3fa56e7742d5cb075e82b7961d9831a070b1215cbc8576  .../PKG-A1-义务收敛报告.md
```

与 TL 交接声明（脚本 `f3603a24` / CSV `58671a90` / summary `f7dd5d4b` / 报告 `d93488c2`）**逐字一致**。

| 断言 | TL 声明 | 我实测 | 判定 |
|---|---|---|---|
| 真义务 / 待回源 / 合计 | 691 / 361 / 1052 | `Counter({'TRUE_OBLIGATION': 691, 'NEEDS_SOURCE_CHECK': 361})`，CSV 1052 数据行 | ✅ |
| 真义务按 Wave | `W3_CONSUMER_SWITCH 381` / `W2_SPLIT 291` / `W3_KERT_ASSETS 19` | `{'W3_CONSUMER_SWITCH': 381, 'PENDING_SOURCE_CHECK': 361, 'W2_SPLIT': 291, 'W3_KERT_ASSETS': 19}` | ✅ |
| P0 行数 | 65 | 65 | ✅ |
| P0 全部带 `PROOF:IMPORT_LINE` | 65/65 | 65/65 | ✅ |
| P0 包分布 | `ontology 55 / action.domain 6 / ontology.domain 4` | 同 | ✅ |
| 对照口径 | 626/426（开关回退） | 626 条 TRUE 行不带 P0 标签（691−65=626） | ✅ |
| `--gate` | exit 0 | `PASS`，exit=0 | ✅ |
| `--selftest` | 13/13 | `[selftest] 13/13 用例符合预期`，exit=0 | ✅ |

**逐条回源（≥8 条要求，我做了全量 65/65）**：对每条 P0 行，解析 `evidence` 的 `repo:path:line`，实测该行是否**恰为** `import <pkg>.<Class>;` 且 `<pkg>` == 标签值、`<Class>` ∈ 该行 `tokens`：

```
P0 total: 65
P0 by pkg: Counter({'com.gien.gits.ontology': 55, 'com.gien.gits.action.domain': 6, 'com.gien.gits.ontology.domain': 4})
P0 by tier: Counter({'MEDIUM': 36, 'WEAK': 29})
verified OK: 65 / 65
bad: 0

=== SAMPLE 10 P0 rows (file:line -> actual content) ===
gits:apps/api/src/main/java/com/gien/gits/api/controller/ClaimController.java:15  | tier=MEDIUM | pkg=com.gien.gits.ontology
    L15: import com.gien.gits.ontology.Claim;
gits:.../CommitmentController.java:5  -> L5: import com.gien.gits.ontology.Commitment;
gits:.../CustomerContextController.java:9 -> L9: import com.gien.gits.ontology.Customer;
gits:.../EngagementClaimController.java:6 -> L6: import com.gien.gits.ontology.Claim;
gits:.../EngagementJourneyController.java:21 -> L21: import com.gien.gits.ontology.KycGapProfile;
gits:.../EvaluationController.java:16 -> L16: import com.gien.gits.ontology.Claim;
gits:.../ExternalEventController.java:4 -> L4: import com.gien.gits.ontology.ExternalEvent;
gits:.../HumanGateController.java:10 -> L10: import com.gien.gits.ontology.HumanGate;
gits:.../InteractionController.java:16 -> L16: import com.gien.gits.ontology.Interaction;
gits:.../InteractionsV1Controller.java:6 -> L6: import com.gien.gits.ontology.Interaction;
```

⇒ **标签不是装饰：65/65 的 `文件:行` 确为对应包的精确 import 行。** 抽样要求已超额满足。

### 2.2 我自建的变异（**全部被拦下，且可还原**）

仓库 CSV **零改动**（全程只读；变异写 `/tmp/qa-w15r/`，经 `run_checks(out_csv=副本)` 驱动）：

| 变异 | 我的期望 | 实测（原始输出） | 判定 |
|---|---|---|---|
| MU-0 对照（真实 CSV） | 0 finding | `findings = 0 []` | ✅ |
| **MU-Q1** 某 P0 行 `responsible_wave := W9_BOGUS` | G6 FAIL | `G6 [disk] true obligation without actionable wave: …ClaimController.java:15 wave=W9_BOGUS` + `G7 csv row 69 drifted…`（2 finding） | ✅ |
| **MU-Q2** 某 P0 行 `evidence` 改到第 14 行（非 import 行，实测内容 `'/**'`） | G4/G5 FAIL | `G4 [disk] evidence does not verify at source: …CommitmentController.java:14 -> '/**'` + G7 | ✅ |
| **MU-Q2b** 某 P0 行标签改为不存在的包 `com.gien.gits.BOGUS` | 期望 G5 标签校验 FAIL | **仅 `G7 csv row 73 drifted from recomputation`；G5 = 0 命中**（见 §2.3，此处已现异常） | ❌ 见 §2.3 |
| **还原核验** | CSV 哈希逐字回到变异前 | `repo CSV sha256 after mutations = 58671a908bae8d7dd533e0aee7fbc6146f49eef983c3574e92367e2f8576b547 | == baseline: True`；`restored findings = 0` | ✅ |

⇒ G4/G6/G7 有牙齿；**但 G5 的标签校验对非末行失效**（下一步深挖）。

### 2.3 BLOCKER｜G5「标签二次校验」是**空转断言**（覆盖 0/65）

**(a) 定位（回源）**：`scripts/onto1_obligation_triage.py` 的 `row_level()` 内，G5 的标签校验块**缩进为 8 空格**，与该函数内 `for r in target:`（亦 8 空格）**同级** ⇒ 它**在循环之外**，只对 `target` 的**最后一个元素**求值（依赖 Python 泄漏的循环变量 `r`）：

```
  744 ind= 8 | # G5
  745 ind= 8 | for r in target:
  746 ind=12 | if r.get("tier") == TIER_WEAK and r.get("disposition") == DISPO_TRUE:
  ...
  754 ind=12 | if r.get("tier") == TIER_WEAK and r.get("disposition") == DISPO_HOMONYM \
  757 ind= 8 | # RESOLVES_TO_ONTOLOGY_PKG 是一个**可复核**的标签：证据行必须是"该 token 从该包精确导入"
  758 ind= 8 | sig = str(r.get("signal", ""))          <-- 出循环了
  759 ind= 8 | if "RESOLVES_TO_ONTOLOGY_PKG:" in sig:
  ...
  772 ind=12 | if not ok:
  773 ind=16 | out.append(f"G5 [{label}] ontology-pkg resolve label without import evidence: {ev}")
```

**(b) 决定性对照实验**（同一行、同样篡改标签，只改它在 CSV 中的**位置**）：

| 实验 | 篡改行的位置 | G5 标签校验命中次数 |
|---|---|---|
| 中间行（`p0idx[2]` / `p0idx[0]` / 把该行移到**最前**） | 非末行 | **0** |
| 把该行移到 **CSV 最后一行** | 末行 | **1**：`G5 [disk] ontology-pkg resolve label without import evidence: …EngagementClaimController.java:6` |

**(c) 真实数据上该块**完全惰性**：CSV 第 1053 行（最后一行）是

```
最后一行 = kert src/kert/infrastructure/runtime_store.py
   disposition = TRUE_OBLIGATION | signal = STRONG_CONTENT:SPARQL_QUERY
   是 P0 行吗 = False
```

⇒ 真实仓上该块扫描的是**非 P0 行**，`if "RESOLVES_TO_ONTOLOGY_PKG:" in sig` 恒为假 ⇒ **一次都不执行**。

**(d) 全量证明**：把**全部 65 条** P0 行的标签改成不存在的包：

```
把全部 65 条 P0 行的 RESOLVES_TO_ONTOLOGY_PKG 标签改成不存在的包 com.gien.gits.BOGUS：
  总 findings = 1
  G5『ontology-pkg resolve label without import evidence』命中 = 0
  G7『drifted from recomputation』命中 = 1
```

⇒ **65/65 行的包名标签不受任何 G5 断言保护**；唯一兜底是 G7（磁盘 CSV 与本次复算逐行比对）。G7 能拦住"CSV 被改"（因为复算值不同），但**拦不住"代码与 CSV 一致地写错"**——这正是该二次校验存在的理由，而它没在工作。

### 2.4 与 TL 报告的**不符**（必须指出）

- `memory/handoffs/TL-AUDIT-W15-PKG-A1.md:84` 明文：
  「**G5 例外**：`tier==WEAK ∧ TRUE` 仅在**同时**含这两种标记时放行（**该证据还须通过既有"精确导入该包"二次校验**）。」
  ⇒ 实测该二次校验对 65 行 P0 **不生效**（0/65）。**TL 的 §8.1 描述与实现不符。**
- 该审计报告 §8.2 自称"这不是'为过门禁而改断言'"——就 `--gate` 的通过性而言成立，但**被援引为安全机制的那条断言实际是死代码**，与"假绿/空转"同族（本 Loop 已登记 6 次同类：`FAIL-2026-09-20-*` 的 `W15TL-04`、GK-KE 的 `FAIL-2026-09-12-02` 等）。

### 2.5 `--selftest` 的 M9b-1 / M9b-2 是真断言（**不是装饰**）——但存在"因夹具行序而通过"的成分

逐条读码 + 实跑结论：

- **M9b-1**（`:1491-1502`）：`globals()["RULING_I6_UPGRADE_P0"] = False` → 重跑 `triage()` → 断言夹具行 `CustomerModelDto` 落回 `NEEDS_SOURCE_CHECK` 且保留 `RESOLVES_TO_ONTOLOGY_PKG:com.gien.gits.ontology`。实跑输出：
  `PASS  M9b-1 开关回退 ⇒ 回落 NEEDS + P0 标签（回退有效）  (NEEDS_SOURCE_CHECK / WEAK_PATH:R-WEAK-PATH-EXT-DTO|PROOF:NONE|RESOLVES_TO_ONTOLOGY_PKG:com.gien.gits.ontology)`
  ⇒ **真断言，会 FAIL 对应场景**（若实现不读开关则 dispose 仍为 TRUE，断言不成立）。**非装饰。**
- **M9b-2**（`:1504-1517`）：剥掉 `PROOF:IMPORT_LINE|` 后断言 `any("G5" in x for x in f9b)`；实跑 `(2 finding(s))`。
  ⚠️ 我复算其**触发来源**：该夹具行 `tier=WEAK`，命中的是**循环内**的 G5 弱面反一刀切断言（`:746-753`），**不是** §2.3 那个死掉的标签块。因此 M9b-2 **通过是因为夹具行恰好排在最后一行**——把它移到非末行，标签块不会兜住（§2.3 实验）。这与 `FAIL-2026-09-20-W15TL-04`（"变异用例落在输入域之外"）同族的**测试方法缺陷**：断言看似覆盖，实际只覆盖末元素。

### 2.6 D-12 判定：「I-6 升格是否属于放宽」+ 反例是否充分

- **属于放宽**：它把 65 行从 `NEEDS_SOURCE_CHECK` 移入 `TRUE_OBLIGATION`，即**放宽了**原先 P0⇒待回源 的判定。TL 自己按 D-12 声明为"放宽型"（`TL-AUDIT-W15-PKG-A1.md:100`），**方向正确**。
- **反例充分性：部分成立（WEAK 半边成立，MEDIUM 半边缺失）**。我实测：对真实 CSV 剥掉**全部 65 行**的 `PROOF:IMPORT_LINE`：

```
=== 实验D：剥掉全部 PROOF:IMPORT_LINE（真实仓 65 行）===
findings: 30   Counter({'G5 [disk]': 29, 'G7 csv': 1})
```

29 条 G5 全部来自 `tier==WEAK` 的 29 行；**另 36 行 tier=MEDIUM 的升格没有任何"不得放行"断言**（G5 弱面断言按设计只作用于 WEAK；本该覆盖它们的标签块已死）。⇒ **D-12 的"放宽必须自带不得放行反例"只满足了 29/65（44.6%）**。

### 2.7 包语义回源（供 Wave 2 抽检参考，非判据）

按 TL §8.3 要求核对三个包的实际归属（`grep -rl "^package <pkg>;"`）：

| 包 | 行数 | 实际所在模块（回源） |
|---|---|---|
| `com.gien.gits.ontology` | 55 | `modules/operational-ontology/**`（含 43 个 java 文件） |
| `com.gien.gits.ontology.domain` | 4 | `modules/operational-ontology/src/main/java/com/gien/gits/ontology/domain/`（Opportunity / ProductKnowledgeVersion / EvidenceVersionLink / InteractionExtension） |
| `com.gien.gits.action.domain` | 6 | **`modules/human-action/**`**（Task / RecordingConsent；`action/port/TaskRepository.java`） |

⇒ 其中 **6/65（9.2%）解析到的包不属于 L1 本体模块**，而属 `human-action` 领域模型。I-6 的理由"显式 import 是对**本体模型**的代码级耦合"对这 6 行**是推断而非证据**。TL §8.3 已如实列出该包分布，故非隐瞒；但 **Wave 2 必须把这 6 行作为"包语义可能无关"的首批抽检对象**（判据：`modules/human-action` 是否在四层拆分的命名空间迁移范围内）。

---

## 3. R2｜四个陈旧门禁的重记核对（**通过**）

核对对象 = `EVIDENCE.json` 的 `evidence_file` → 日志是否含 `# artifact=<脚本>@<sha256>`，且该 sha256 **等于磁盘实测**：

| 门禁 | evidence_file | 日志内嵌 | 磁盘实测 | 结论 |
|---|---|---|---|---|
| `wi_a4_namespace_collision` (exit 2) | `…collision-20260920T155915Z.log` | `…collision_check.py@8c18b5b3adc767e5 sha256=8c18b5b3adc767e5…` | `8c18b5b3adc767e5` | ✅ 相符 |
| `wi_a4_namespace_collision_selftest` (0) | 同上 `…_selftest-…155915Z.log` | 同 | 同 | ✅ |
| `wi_a3_reference_alignment` (0) | `…reference_alignment-20260920T155915Z.log` | `…alignment_check.py@4d706978a0fab7f2 sha256=4d706978a0fab7f2…` | `4d706978a0fab7f2` | ✅ |
| `wi_a3_reference_alignment_selftest` (0) | `…_selftest-…155916Z.log` | 同 | 同 | ✅ |
| `wi_w15_a3_acceptance` (0) | `…wi_w15_a3_acceptance-…154613Z.log` | `…w15_acceptance.py@4fb2b1e687c0c420 sha256=…` | `4fb2b1e687c0c420` | ✅ |
| （附）`wi_a2_obligation_triage`(+`_selftest`) | `…160118Z / …160119Z.log` | `…triage.py@f3603a24ee86f5ee sha256=…` | `f3603a24ee86f5ee` | ✅ |

补充独立核对（**31 个门禁全量**）：脚本比对 `EVIDENCE.json.output_sha256` 与磁盘日志文件实际 sha256 ⇒

```
EVIDENCE.json 门禁数 = 31
output_sha256 实测一致 = 31 ；不一致 = 0 ；证据文件缺失 = 0
状态分布: Counter({'pass': 30, 'fail': 1})
exit 非 0 的门禁: {'wi_a4_namespace_collision': 2}
```

用例数与声明一致：`collision --selftest` 日志含 **26 条**用例记录（`:6-:31`）；`refalign --selftest` 为 `selftest: 16/16 符合预期`；collision `--gate` 输出 `[C-2] FAIL（实测 2 / 登记 2 / 未登记 0 / 陈旧 0）`、失败项**仅** C-2a/C-2b。

**两项必须写出的更正/提示（不隐藏）**：

1. **`TL-AUDIT-W15-PKG-A3.md:107` 与制品不符**：该处称"本轮 2 个既有门禁的登记证据仍属**陈旧**（生成于 A3 改动前），**未**被刷新"。但实测两份登记日志**内嵌哈希 = 当前冻结 revision**（`8c18b5b3` / `4d706978`），时间戳亦与 `EVIDENCE.json.executed_at`（`2026-09-20T15:59:15Z`）吻合（日志 mtime 为 `2026-09-20 23:59:15 +0800`，即同一时刻的本地表示）。⇒ **就"证据-制品绑定"这一条而言，登记证据并不陈旧**；相反，是**该审计报告的这句话没有随制品更新**。（此更正方向对 TL 有利，但我如实记录。）
2. **A3 自己的 `a3fix-after-*` 交付日志从未重发**：4 份 `a3fix-after-wi_*.log` 仍停留在旧 revision（`refalign` 那份为 `candidates=157 allowed=78 allowed[rule_statement]=0`，而登记版为 `candidates=159 allowed=80 allowed[rule_statement]=1`），且**既未登记也未入白名单**（见 §5.3）。⇒ C7 的字面要求（"重发 after 日志"）未完成；其实质目标由 `wi_*` 155915 版登记日志达成。

---

## 4. R3｜A3 的 C1~C4 独立复现（**通过**）

**在我自己的沙箱**（`/tmp/qa-w15r/sb`，**自包含侧车**：`--pins/--scan-pins/--registry/--manifest/--signature` 全部指向沙箱内副本，比验收仪器更严——仪器仍读真实仓侧车）运行；夹具/产物**只写 `/tmp/qa-w15r/`，不进入被扫仓库**（D-13）。

### 4.1 C1/C2｜缺输入必须具名 FAIL 且不得崩溃

| 用例 | 期望 | 实测（原始输出摘录） | 判定 |
|---|---|---|---|
| A 对照 | exit 2、C-4 PASS 4/4、仅 C-2 FAIL、无 Traceback | `[C-4] PASS（声明 4 个：受控 1 / D-2 范围外 3；必需钉值 allow-list 4/4…）`；`[C-2] FAIL（实测 2 / 登记 2 / 未登记 0 / 陈旧 0）`；`EXIT=2` | ✅ |
| B 删【受控】必需钉值**文件** `specs/semantic/gits-core.owl.ttl` | 具名 `C-4_REQUIRED_PIN_MISSING`，无 Traceback | `[输入] 必需钉值文件缺失 ⇒ **未进入任何解析**（fail-closed，A3-1/A3-2）：['specs/semantic/gits-core.owl.ttl']`；`onto1-namespace-collision: FAIL: C-4: C-4_REQUIRED_PIN_MISSING 必需钉值**文件**不存在…`；`EXIT=2`；**无 Traceback** | ✅ |
| C 删【范围外】必需钉值**文件** `…/evidence/consumer-scan-summary.csv` | 同样具名 FAIL（QA E3 的原意） | 同上形态，路径为 `loops/ONTO1-ontology-split/evidence/consumer-scan-summary.csv`；`EXIT=2` | ✅ |
| D 还原对照 | C-4 回到 PASS（非永久红） | `[C-4] PASS（…必需钉值 allow-list 4/4…）`，`EXIT=2`（仍因真实 C-2 而阻断） | ✅ |

回源：`onto1_namespace_collision_check.py:425-439`（`elif not (root / path).is_file():` ⇒ `C-4_REQUIRED_PIN_MISSING`）与 `:535-553`（"输入存在性闸门"，在任何解析之前提前返回、形状完整、不抛异常）。`W15A3-02` 与 `W15A3-03` 两条旧缺陷**确已关闭**。

> 观察（非缺陷）：用例 B/C 会**提前返回**，因此输出中不再出现 C-1a/C-2/C-3 行（`[C-2] FAIL` 的真实阻断在本轮被"缺输入"掩盖）。退出码仍为 2 ⇒ **不是假绿**，但报告信息量下降，建议记账时注明。

### 4.2 C3/C4｜参照对齐守卫的收紧是否生效

夹具（5 个文件，声称句**运行期拼接**、只写 `/tmp/qa-w15r/rf/`）：`x2` 普通声称、`x3` 声称 + 主题词「词表」、`x4` 标题含「门禁」+ 其下声称、`x5` 对照标题、`z-innocent` 无命中控制组。实跑（完整输出摘录）：

```
verdict: FAIL
counter: files=5 filenames=0 candidates=4 allowed=0 registered_legacy_hits=0 unreadable=0
allowed[rule_statement]=0
allowed_by_reason: {}
finding: CONTENT_WORDING_UNALLOWED {"file": "/tmp/qa-w15r/rf/x2-plain-claim.md", "line": 3, ...}
finding: CONTENT_WORDING_UNALLOWED {"file": "/tmp/qa-w15r/rf/x3-claim-with-topicword.md", "line": 3, ...}
finding: CONTENT_WORDING_UNALLOWED {"file": "/tmp/qa-w15r/rf/x4-heading-with-negchar.md", "line": 3, ...}
finding: CONTENT_WORDING_UNALLOWED {"file": "/tmp/qa-w15r/rf/x5-heading-control.md", "line": 3, ...}
（z-innocent.md 未出现在任何 finding 中）
```

| 用例 | 期望 | 实测 | 判定 |
|---|---|---|---|
| Q1b｜声称 + 主题词（旧 `W15A3-04` 的漏检通道） | 必须判违规、不得被 `rule_statement` 放行 | `x3…md` 命中 `CONTENT_WORDING_UNALLOWED`；`allowed[rule_statement]=0` | ✅ 已关闭 |
| R1a｜标题含「门禁」的章节 + 其下声称 | 必须判违规（不得整节放行） | `x4…md` 命中 `CONTENT_WORDING_UNALLOWED` | ✅ 已关闭 |
| 对照 `x2` / `x5` | 判违规 | 均判违规 | ✅ |
| **控制组 `z-innocent`（我加的）** | **不得出现在 finding 中** | 未出现 | ✅ 验收仪器的 `violated(name) = name in out` **在此配置下无假阳性** |

回源：`:158` `HEADING_NEG_MARKERS = NEG_MARKERS − {"禁","驳"}`；`:288-291`（标题锚点走词级）、`:299-311`（`is_rule_statement` 三条件，`CLAIM_CONSTRUCTION_RE` 优先 ⇒ 声称行永不放行）。

> 残余（与 TL/A3 声明一致的已知面）：本守卫是**词法级 + 结构窗口**，非语义判定；把声称写在否定条款旁或把主题词与声称写进同一"恒不放行"形态之外时仍有漏检空间，`allowed_by_reason` 计数是唯一可审计入口。

---

## 5. R4｜红线与板面

### 5.1 红线（**通过**）

| 检查 | 命令 | 实测 |
|---|---|---|
| 受控目录零改动 | `git status --porcelain -- generated/ specs/ docs/dd/` | **空**（=0） |
| 无 `git add` 痕迹 | `git diff --cached --name-only` | **空** |
| KERT 侧零写入 | `find /home/szf/dev/Leibniz-KERT -newermt "2026-09-21 00:00" -type f -not -path "./.git/*"` | **空** |
| KERT ONTO1 相关件 mtime 未变 | `stat` | `ONTOLOGY-SPLIT-DESIGN-V1.1-REVIEW.md` = `2026-09-20 16:28:09`（sha256 `279f850804ca2a91`，与 `FAIL-2026-09-20-W15INT-03` 登记值一致）；`V1.0.md` = `09-20 14:48:57`；`ADR-018` = `09-20 14:49:01`；`src/kert/domain/ontology_reference.py` = `09-16 18:18:46` |

### 5.2 门禁四连（**全 PASS**）

```
$ python3 scripts/loop_guard.py --loop ONTO1-ontology-split
loop-guard: PASS                                    exit=0
$ python3 scripts/onto1_evidence_board_check.py --gate
[E1] evidence dir ok; gates=31
[E2] gate-like logs=55 registered=31 allowlisted=25 orphan=0
[E3] registered evidence files present=31/31
onto1-evidence-board: PASS                          exit=0
$ make memory-check LOOP=ONTO1-ontology-split
loop-guard: PASS                                    exit=0
$ make evidence-check LOOP=ONTO1-ontology-split
loop-guard: PASS                                    exit=0
```

板面：`EVIDENCE.json.gates` = **31 项**（30 pass / 1 fail），唯一 fail = `wi_a4_namespace_collision`（exit 2）；`LOOP.yaml` gates 同为 31，`status=in_progress`；`independent_qa = {"status": "pending", "actor": null, "session": null, "attested_at": null, "evidence_file": null, "evidence_sha256": null}` ⇒ **未被任何人预填**（我的交付未写入该字段）。

### 5.3 白名单抽查（**无 MAJOR；2 项板面卫生发现**）

`evidence/non-gate-log-allowlist.json` 19 条规则 / 命中 **25** 个日志。逐步核验：

1. **未发现"用白名单掩盖新产物"导致结论翻转的情形**：25 条中时间戳晚于同门禁登记证据者仅 2 条，逐条回源后：
   - `index_status-20260920T141948Z.log`（比登记版 `…132340Z` 更晚）：内容 `ua_index_gate: PASS (nodes=5106, drift={'merge-meta.json': 0, 'meta.json': 0})` 与登记版**逐字同结论** ⇒ 白名单理由（"复跑结果一致（drift 0）"）**经实测成立**。
   - `wi_a4_iri_mapping_selftest-20260920T145542Z.log`：**它本身就是已登记证据文件**（被通配 `wi_a4_iri_mapping_selftest-20260920T*.log` 一并吞入）⇒ 白名单与登记集合**重叠 1 个**（`E2` 的 `31+25−1=55` 即此重叠）。
2. **发现 A（MINOR）**：上述通配过宽 ⇒ "登记证据"同时被当作"白名单逃生口"。逃生口应只覆盖未登记项；建议把该条改为精确文件名或排除登记集合。
3. **发现 B（MEDIUM，与 `FAIL-2026-09-20-W15INT-01` 同族）**：`E2` 的"形如门禁日志"判定是**文件名前缀** `wi_`/`contract_`/`security_`/`index_`（`scripts/onto1_evidence_board_check.py:10-11`、`gate_like` 按 basename 前缀筛）。因此以下 **6 份"已执行但未登记"的日志落在板面视野之外**（`orphan=0`，但也**未被登记、未被白名单**）：

   | 文件 | mtime | 性质（回源） |
   |---|---|---|
   | `a3fix-after-wi_a4_namespace_collision-gate.log` | 09-20 23:29:33 | PKG-A3 交付的 after 证据，`[C-2] FAIL（实测 2…）`（结论同登记版） |
   | `a3fix-after-wi_a4_namespace_collision-selftest.log` | 09-20 23:29:33 | 25 行 **旧 revision**（23 用例）版本 |
   | `a3fix-after-wi_a3_reference_alignment-gate.log` | 09-20 23:30:19 | `verdict: PASS … candidates=157 allowed=78 allowed[rule_statement]=0`（**N-1 收紧前**） |
   | `a3fix-after-wi_a3_reference_alignment-selftest.log` | 09-20 23:29:35 | 16 行 **12 用例**旧版本 |
   | `wave0-readiness-20260920T1520Z.log` | 09-20 23:18:51 | `onto1_wave0_readiness.py --gate` 的 honest run log（D-9 决定**不登记**该门禁） |
   | `review-submission-zip-dryrun-20260920T1415Z.log` | 09-20 22:16:17 | `zip -r -X /tmp/onto1-submit-dryrun.zip`，自述"仅写 /tmp" |

   **方向保守**（无一隐藏了新 FAIL：两份 after-gate 的结论与登记版一致或为被取代的旧 revision；`wave0` 的 R6/R7 未满足已在 D-9 声明的五处登记）。但**该类别恰是 `W15INT-01` 的原始缺陷类**（"执行了但未登记"的孤儿证据）⇒ **盲区未完全封闭**。建议：`E2` 改为按"日志内容含 `COMMAND=`/`EXIT_CODE=` 或 `# exit_code=` 且未被登记"识别（而非仅按文件名前缀），或把上述 6 份按规则登记/白名单。

---

## 6. 我认为**尚未关闭**的项（逐条给复验判据）

| # | 项 | 状态 | 复验判据（可复算） |
|---|---|---|---|
| **U-1** | **G5 标签二次校验空转（BLOCKER）** | **未关闭** | ① 对任意**非末行** P0 行把 `RESOLVES_TO_ONTOLOGY_PKG:` 改成不存在的包 ⇒ 复跑须出现 `G5 … ontology-pkg resolve label without import evidence`（现为 0 命中）；② 全部 65 行同样篡改 ⇒ 须出现 ≥65 命中（现为 0）；③ 修好后重跑 `--gate`/`--selftest` 并**作为新 revision 重发**（D-11）。修法：把 `onto1_obligation_triage.py:757-773` **缩进进 `for r in target:`** 并补 M9b-3 变异"非末行的标签被篡改 ⇒ G5 FAIL"。 |
| **U-2** | **D-12 反例只覆盖 WEAK 半边（29/65）** | **未关闭** | 对 36 行 MEDIUM-tier 升格行，剥掉 `PROOF:IMPORT_LINE` ⇒ 现无任何 G5 命中（实测只有 29 条 WEAK 面命中）。修好后须给出 MEDIUM 面的"不得放行"反例并配变异。 |
| **U-3** | **TL 审计 §8.1 的机制描述与实现不符** | **未关闭** | `TL-AUDIT-W15-PKG-A1.md:84` 的"二次校验"表述须按 U-1 落地结果**改写或撤回**（诚实性要求，非措辞问题）。 |
| **U-4** | `wi_a4_namespace_collision` 的 **C-2 两处真实前缀冲突** | **未关闭（Wave 3）** | `python3 scripts/onto1_namespace_collision_check.py --gate` 现 `exit=2`：`C-2a prefix=gits;namespaces=…`、`C-2b localname=Product;namespace=…` 的 evidence 分别落在 `specs/data/customer-source-mapping.r2rml.ttl:2`、`specs/knowledge-architecture/instances/product/products.ttl:1/10/15`。**在此 fail 消除前不得记 `QA_PASS`。** |
| **U-5** | PKG-A3 的 **C5/C6/C7**（计数口径 / M12 夹具顺序 / 冻结复交+回执表） | 实质部分被 §3 覆盖，**字面未完成** | ① `a3fix-after-*` 4 份日志须按 D-11 用 `scripts/onto1_gate_log.py` **重发**（含 `# artifact=`）或明确作废并登记；② collision 脚本头部的"19 变异+4 对照"字样须改为实测 **26 条记录**；③ refalign 头部"14 项"须改为 **16/16**。 |
| **U-6** | 板面 **E2 孤儿检测盲区**（文件名前缀制） | **未关闭** | 见 §5.3 发现 B 的 6 份文件；建议改判据或逐条登记。 |
| **U-7** | 白名单通配吞掉已登记证据（重叠 1） | **未关闭（MINOR）** | `wi_a4_iri_mapping_selftest-20260920T*.log` 收敛为精确名后，`E2` 应报 `registered=31 / allowlisted=24 / gate-like=55 / orphan=0`。 |
| **U-8** | **P0 中 6 行解析到 `modules/human-action`**（`com.gien.gits.action.domain`） | **Wave 2 抽检义务** | 判据：该模块是否在四层拆分的命名空间/包结构迁移范围内。TL §8.3 的"优先抽检 P0 前 5 行"应**同时**覆盖这 6 行（现前 5 行全为 `com.gien.gits.ontology`，覆盖不到 `action.domain`）。 |
| **U-9** | `TL-AUDIT-W15-PKG-A3.md:107` 的"陈旧"表述与制品不符 | **未关闭（文档一致性）** | 见 §3 提示 1。 |
| **U-10** | KERT 仓 3 个 ONTO1 相关写入的**归属待追认** | **未关闭** | `FAIL-2026-09-20-W15INT-03` + D-7：本报告仅复核"我开工前后零写入"（§5.1），**未**追认历史写入；归 KERT 维护方 / Owner。 |

---

## 7. 非声明

1. **不构成 `QA_PASS` / `DEV_SELF_CHECK_PASS`**：本 Loop 有已知未关闭 fail（U-4），且发现 BLOCKER 级空转（U-1）。本报告不改变任何门禁状态、未调用 `record_gate.py`、未改 `EVIDENCE.json`/`LOOP.yaml`/`STATE.json`/`FAILURES.md`。
2. **不覆盖 Wave 0/1/2+**：结论仅及 W-1.5 就绪加固批次的四个 PKG 与红线板面。
3. **不代表 Owner 批准**：不代签任何 Owner 权限事项（根域取值、权威确认、激活、签署）。
4. **不认定 KERT 侧任何文件的正确性**：仅复核"本轮零写入"。
5. **本报告的复算绑定上列哈希**：`onto1_obligation_triage.py = f3603a24ee86f5ee…`、`obligation-triage.csv = 58671a908bae8d7d…`、`onto1_namespace_collision_check.py = 8c18b5b3adc767e5…`、`onto1_reference_alignment_check.py = 4d706978a0fab7f2…`、`onto1_w15_acceptance.py = 4fb2b1e687c0c420…`。被测制品若在该哈希之后变更，本报告结论**自动失效**，须按 D-11 重发重验。
6. 我**未**修改仓库既有文件、**未** `git add`、**未**写 KERT；唯一写入为本文件；变异夹具只在 `/tmp/qa-w15r/`（扫描面之外）。

---

## 8. 我**未能**验证的部分（如实列出，不含糊）

| # | 未验证项 | 原因 / 边界 |
|---|---|---|
| N-1 | **W-1.5 批次的整体时序真实顺序** | TL 文档里的时间戳混用了 `Z` 标注与本地 `+0800`（例：A3 审计标 `2026-09-20T23:36Z` 而日志 mtime 为本地 `23:59:15 +0800`）。我只以**文件 mtime + 日志内嵌哈希**为事实，**不**据文档时间戳推断先后。§3 提示 1 的"陈旧与否"结论只依赖 hash/mtime 事实，不依赖时序推断。 |
| N-2 | **`--report` 全量重生成的一致性** | 按纪律未运行 `--report`（它会重写 CSV/summary/报告 ⇒ 改交付物）。故 `obligation-triage-summary.json` 与报告中的计数我只做了**读值比对**（与 CSV 复算一致），**未**做"重生成后逐字相等"验证。可复算判据：`--report` 后 CSV 的 `generated_at` 与 summary 会变（属可变哈希制品），须比对 `reconciliation`/`by_tier`/`true_by_wave` 三段。 |
| N-3 | **PKG-A2 的 wave0 就绪预检** | 不在我的复验范围（派工为 R1~R4）；仅确认其登记门禁 `wi_a2_wave0_readiness_precheck`(+`_selftest`) 的 `output_sha256` 与日志相符。 |
| N-4 | **`iri-mapping-draft.csv` 的 87 行内容正确性** | 仅确认其作为 C-1b 输入存在、且 collidion 判定为 `具体 IRI 0 / 占位 87`；未逐行核对术语↔IRI 映射语义（属 WI-A4 范围，且 D3 未签 ⇒ 无从判定根域）。 |
| N-5 | **`com.gien.gits.action.domain` 在四层拆分中的真实归属** | 仅回源到"该包位于 `modules/human-action`"（§2.7）。是否随 L1 命名空间迁移，取决于尚未签署的拆分设计范围 ⇒ **不能由我判定**，已转为 U-8 抽检义务。 |
| N-6 | **`make check` / Maven / 覆盖率类门禁** | 本轮未跑（非 R1~R4 要求，且耗时/需网络），故**不**对其状态作任何断言。 |
| N-7 | **被取代历史日志的"逐条取证必要性"** | 我核对了"是否按规则登记"，但**未**判定各条白名单理由的**必要性**（例如是否所有历史 attempt 都必须留证）——那是 TL 的记账权域。 |

---

**报告哈希**：本文件生成后由 TL 侧自行复算（我不自证自身哈希；如需请 `sha256sum loops/ONTO1-ontology-split/memory/handoffs/INDEPENDENT-QA-W15R-2026-09-21.md`）。

---
---

# 第四轮复验（2026-09-21，TL 修复后回归）

| 项 | 值 |
|---|---|
| 复验人 | `qa-w15r`（同前，独立复算） |
| 复验基线 | `scripts/onto1_obligation_triage.py = a2be4df33ddc2ad3bdcd0efafda26d13a39524f779680ad0589d422bd1076f27`（TL 声明 `a2be4df33ddc2ad3` ✅）· `obligation-triage.csv = 58671a908bae8d7d…`（**未变**）· `onto1_evidence_board_check.py = 1f7227633acb6076abb3015e1374e4dd448fc3a2871649e9b24ad1e8ec117655` · `non-gate-log-allowlist.json = 535f41502e68e6c111e983957bc04c0ad42c521e4e6a9988f5f723c6de48c51f` |
| **结论** | **BLOCKER 已关闭；新增 1 项 MAJOR（本轮重记的 2 个板面门禁日志缺 D-11 自证行）；总体仍 NOT_ACCEPTED**（理由见 R4-① 与 R4-④） |

## R1（四轮）① 我的决定性变异复跑 ⇒ **65/65**（BLOCKER 已关闭）

命令（沙箱 `/tmp/qa-w15r/r4-*.csv`，仓库 CSV **零改动**）：

| 变异 | 期望 | 实测（原始输出） | 判定 |
|---|---|---|---|
| **全部 65 行** `RESOLVES_TO_ONTOLOGY_PKG:` → `com.bogus.pkg` | G5 命中 == 65 | `(a) 全部 65 行标签改 com.bogus.pkg ⇒ 总 findings=66 | G5标签命中=65 | 期望=65 | 通过=True`；命中分布 `Counter({'G5 [disk]': 65, 'G7 csv': 1})` | ✅ **关闭** |
| **单条【非末行】**（CSV 行 `row#71` = `CustomerContextController.java:9`，`tier=MEDIUM`）改标签 | G5 命中 == 1 | `(b) 单条【非末行】(row#71) 改标签 ⇒ G5标签命中=1 | 期望=1 | 通过=True` | ✅ **U-2 实质关闭** |
| 对照（真实 CSV） | 0 finding | `findings = 0`；`仓库 CSV 哈希 = 58671a908bae8d7d` | ✅ |

⇒ 与第三轮同一条变异（当时 **0 命中**）对比：**G5 逐行校验现在真的在跑**。
⇒ **U-2（D-12 反例只覆盖 WEAK 半边）判定：实质关闭**。修后该块条件挂在 `signal` 标签上、**与 tier 无关**；上表 (b) 命中的正是一行 **tier=MEDIUM**（65 行中 36 行为 MEDIUM），故 36 个 MEDIUM 升格行**已进入覆盖面**，不再只靠弱面断言。

回源：`scripts/onto1_obligation_triage.py:765-781` 现为 **12/16 空格缩进**（在 `for r in target:` 之内）；`--gate` **exit 0**（0 finding）；`--selftest` **14/14**。

## R1（四轮）② M9b-3 的夹具 P0 行**确不在末位**（有区分度）

`fixture_rows` 顺序（回源 `scripts/onto1_obligation_triage.py:1332-1368`）：

| 序 | 行 | 说明 |
|---|---|---|
| … | … | 前 7 行（contract.ttl / tool.py / MapDto×2 / Plain.java / OntologyAwareDto / README.md） |
| **8** | `apps/api/src/main/java/x/dto/CustomerModelDto.java`（`:1362-1364`） | **P0 行（M9）**；注释 `:1360-1361` 明写"**刻意放在 M8 之前**：使 P0 行**不落在 `target` 末位**" |
| **9（末位）** | `apps/api/src/main/java/x/dto/WildcardImportDto.java`（`:1366-1368`） | M8；**非 P0** |

⇒ 末位不是 P0 行 ✅。**我另做退化副本反证**（在 `/tmp/qa-w15r/degen/` 复制脚本，把 `:765-781` 整体左移 4 空格以复现"出循环"的死代码）：

```
真实 G5 块区间（1-based）：765 .. 781
  首行: '            sig = str(r.get("signal", ""))'
  末行: '                    out.append(f"G5 [{label}] ontology-pkg resolve label without import evidence: {ev}")'
  已左移 4 空格（仅该块）=> 退化副本
=== 退化副本 --selftest ===
[selftest] FAIL  M9b-3 全部 P0 行包名改为不存在 ⇒ 逐行 G5 命中数须 == 行数（覆盖全 tier）  (touched=1 G5hits=0)
[selftest] 13/14 用例符合预期
```

⇒ **与 TL 声明逐字一致（13/14、`touched=1 G5hits=0`）** ⇒ M9b-3 **有真实区分度**，不是装饰。
（我未能验证"退化副本 `--gate` 仍 exit 0"：副本位于 `/tmp`，脚本 `ROOT=parents[1]` 解析到 `/tmp/qa-w15r` ⇒ G1 fail-closed 退出 2。这是路径效应、非结论；不构成对 TL 的指控，仅声明我未测该项。）

**残留加固建议（非阻塞，N-8）**：M9b-3 的区分度**依赖夹具行序**——若将来有人把 P0 夹具行移回末位，M9b-3 会在死代码下重新"通过"。建议在 selftest 内**显式断言该行的 index < len(fixture_rows)-1**（或让夹具含 ≥2 个 P0 行），把"行序前提"也变成断言。判据：注入"把 P0 行移到末位"的元变异 ⇒ 该断言必须 FAIL。

## R2~R3（四轮）③ 证据板改造：M4 / M5 / M5b 与 **E5 收窄**（独立复现，**可接受**）

**代码回源**（`scripts/onto1_evidence_board_check.py`）：
- `:83` `gate_like = logs`（原为 `GATE_LOG_RE` 前缀制；`GATE_LOG_RE` 保留仅用于 M4 的"旧逻辑不可见"断言）⇒ **E2 覆盖 `evidence/**/*.log` 全量**；
- `:99-102` E5：`any(allowlisted(name,{pat:""}) and any(ch in pat for ch in "*?[") for pat in allow)` ⇒ **仅含通配的条目判负**；
- `:155-167` M4、`:169-178` M5、`:180-189` M5b。

**我自己的 5 组探针**（不采信其 selftest；`check()` 直调，tmp 沙箱）：

| 探针 | 期望 | 实测 | 判定 |
|---|---|---|---|
| 通配 `wi_g1-*.log` 覆盖已登记 `wi_g1-1.log` | E5 命中 | `['E5 allowlist glob swallows registered evidence file: wi_g1-1.log']` | ✅ |
| 精确名 `wi_g1-1.log` 覆盖已登记文件 | E5 不命中（容忍） | `[]` | ✅ 与 TL 声明一致 |
| 无关精确名 `wi_g1-1.log.bak` | E5 不命中 | `[]` | ✅ |
| 全量通配 `*` | E5 命中 | `['E5 ... wi_g1-1.log']` | ✅ |
| **通配只匹配"非登记"日志** `wi_other-*.log`（**我新造的边界**） | E5 **不得**误伤 | `[]` | ✅ 无假阳性 |

另外独立复现 M4 的区分度：`GATE_LOG_RE.match("a3fix-after-x.log") is None` ⇒ `legacy_blind=True`，且 E2 确实拦下该日志（`[E2 orphan evidence log … a3fix-after-x.log]`）⇒ **M4 真在测"前缀制 → 全量制"的差别**，不是空转。
M5b 的边界（精确名重合容忍）我也复现为 `[]`（无 E5），确认与代码语义一致。

**E5 收窄是否可接受？—— 我判：可接受，不判负。** 理由与判据（TL 明确要求我挑战此条）：

1. **被禁的是危险的那一半**：通配条目的危害是"匹配到**未预见**的未来文件"（可扩展逃生口）；E5 对它判负，且有回归用例 M5 / 全量通配 `*` 亦有牙齿（我实测命中）。
2. **被容忍的那一半是可见且当前无效的**：精确名是**显式、逐条、带 reason、经 TL 复核**的一行；且**当前真实 Loop 的重叠为 0**——我实测 `日志=70 登记=31 白名单命中=39 重叠=0 孤儿=0`，即**没有任何一条豁免当前处于生效状态**。容忍只在"重记窗口内的瞬态"才有意义。
3. **反事实**：若 E5 按字面"任何条目都不得覆盖登记文件"，则任何门禁（不止板面）在其旧日志仍被登记、又被入白名单的那个窗口内都不可判定 ⇒ 板面门禁**无法重记**（TL 已实证 3 次 `fail`，见 `FAIL-2026-09-20-W15TL-10`）。迫使操作者只能二选一：伪造日志（更坏）或撤掉门禁（最坏）。
4. **因此我提出的是"监控判据"而不是"改法"**（判据可复算）：**任意静态时刻**（非重记窗口）下必须 `registered ∩ allowlisted == 0`。我本轮实测为 0；若将来 >0 且**没有**对应的 W15TL-10 类中间态声明 ⇒ 才判 MAJOR。当前**不构成**缺陷。
5. 若 TL 仍想收紧，唯一我认可的替代是**引入 in-flight 标记**（重记前写入待记门禁 id，板面门禁据标记容忍其自身旧日志），从而把"精确名容忍"整条删掉——但这属机制升级，**不是本轮必须**。

**U-6 / U-7 判定：关闭。** `E2` 全量覆盖（`[E2] evidence logs=70 registered=31 allowlisted=39 orphan=0`）；白名单 **39 条全为精确名、含通配的规则数 = 0**（我实测 `仍含通配的规则: []`）；`与登记集重叠的白名单条目: []`。第三轮的 6 份"不可见日志"（`a3fix-after-*`×4、`wave0-readiness-*`、`review-submission-zip-dryrun-*`）已**逐条带理由入册**，我复核其理由与实际内容一致（例：`a3fix-after-wi_a3_reference_alignment-gate.log` 理由称 `candidates=157/allowed=78/rule_statement=0`，与日志实测逐字一致）。

## R4（四轮）④ 我的逐条判断是否仍成立

| 原判 | 第四轮复验 | 结论 |
|---|---|---|
| **U-4** `wi_a4_namespace_collision` 仍 fail（C-2 两处真实前缀冲突） | 复跑 `python3 scripts/onto1_namespace_collision_check.py --gate` ⇒ `[C-2] FAIL（实测 2 / 登记 2 / 未登记 0 / 陈旧 0）`、`onto1-namespace-collision: FAIL（2 项）⇒ 阻断发布`；`EVIDENCE.json` 中 `wi_a4_namespace_collision` 仍是**唯一**非 pass 门禁（exit 2）；`[C-4] PASS（必需钉值 allow-list 4/4）` | **仍成立** ⇒ 不得记 `QA_PASS` |
| **U-5 / C5**（计数口径统一） | **部分完成**：`onto1_namespace_collision_check.py:63-64` 已同步为"**21 条变异 + 5 条对照 … 共 26 项**"（与 selftest 实测 26 条记录一致 ✅）；**但** `onto1_reference_alignment_check.py:15` 仍写"`--selftest` 共 **14** 项（对照 3 … 变异 11）"，而 `SELFTEST_CASES` 实测为 **16** 条（新增 M14/M15），实测输出 `selftest: 16/16 符合预期` ⇒ **未同步**。另：白名单理由（`non-gate-log-allowlist.json:140`）称板面 selftest"现为 5 用例"，实测该项现为 **7** 条 PASS（M0/M1/M2/M4/M5/M5b/M3）。 | **部分未关闭** |
| **U-5 / C7**（冻结复交 + 日志自证 revision） | `a3fix-after-*.log` **4 份全部 `# artifact=` 计数 = 0**（未重发）；TL 已在白名单逐条写明"**未随最终 revision 重发**（A3 已下线 ⇒ C7 **字面未完成**）"、"被取代的旧 revision（… 登记版为 159/80/1）⇒ C7 字面未完成的现场证据" ⇒ **判据从"隐瞒"变为"已声明的未完成"**，但**事实未变**。 | **字面仍成立**（已如实登记） |
| **U-8**（`action.domain` 6 行） | 已在按包分层抽样的义务中说明；我第三轮回源的"该包位于 `modules/human-action`"不变 | **仍成立（转 Wave 2 抽检义务）** |
| **U-9**（A3 报 §10.2 文档不一致） | `TL-AUDIT-W15-PKG-A1.md:85` 已就地加 `⚠️ TL 更正`（承认 §8.1 表述与实现不符、由 QA 判 BLOCKER、已修 + M9b-3）；`FAILURES.md` 新增 `W15TL-09/10/11`（`:394 / :405 / :412`）**均已落盘**（含"更严重的第二层"自认：以引用既有防线为由批准自己的放宽型改动 → 归为最危险类别） | **已处置** |
| **U-10**（KERT 3 个历史写入归属） | TL 接受为待追认项；我本轮仍未对 KERT 内容作判断 | **仍成立** |

## R4（四轮）⑤ 板面 / 日志自证哈希 —— **不是"0 不一致"那么简单（新增 MAJOR）**

**命题 A（TL 的提问）**：有自证行的日志，其哈希是否与磁盘一致？

```
含 # artifact= 自证行: 7 / 31
含自证行者中，哈希与磁盘不符: 0
```

⇒ **7/7 一致、0 不符** ✅。这 7 份 = 经 `onto1_gate_log.py` 包装器生成的（`wi_a4_namespace_collision`(+`_selftest`)、`wi_a3_reference_alignment`(+`_selftest`)、`wi_w15_a3_acceptance`、`wi_a2_obligation_triage`(+`_selftest`)）；A1 两份内嵌 `a2be4df33ddc2ad3` **等于磁盘** ✅。

**命题 B（我必须补的一点）**：**24/31 登记日志完全没有自证行**。逐条分类：

- **22 份**生成于 **D-11 之前**（executed_at ≤ `2026-09-20T15:22Z`；例 `contract_check`/`index_status`/`security_check`/`wi_a1_*`/`wi_a2_consumer_scan`/`wi_a4_iri_mapping*`/`wi_a5_*`/`wi_a6_*`/`wi_review_package_*`/`wi_zip_manifest_verify`/`wi_a2_wave0_readiness_*`）⇒ 属 `T-6` 已声明的**祖父条款**（"既有 Wave -1 门禁…其 revision 以 `executed_at` + §1 哈希表佐证"）⇒ **可接受**。
- **2 份**（**MAJOR**）：`wi_evidence_board_check`（`executed_at = 2026-09-20T16:10:25Z`）与 `wi_evidence_board_check_selftest`（`16:10:34Z`）—— **本轮刚重记**，属 D-11 第 2 条明确覆盖的"新建或重跑"对象，但其日志
  ```
  COMMAND=python3 scripts/onto1_evidence_board_check.py --gate
  EXIT_CODE=0
  STDOUT
  [E1] evidence dir ok; gates=31
  ...
  ```
  **既无 `# artifact=` 也无 `# command=` 行**（`grep -c 'artifact='` = **0**），即**未套用包装器** ⇒ **revision 不可自证**。（`output_sha256` 只能证明"该日志文件未被改"，**不能**证明"它测的是哪一版脚本"。）

⇒ **结论**：TL 的说法"板面两门禁均已重记，日志自证 revision"在**这两份上不成立**。这与 TL 自己的 `W15TL-10`（自指重记陷阱）有关，但**因果不同**：陷阱解释的是"为何会出现三次 `fail` 中间态"，**不**解释"为何最终重记不用包装器"。**我未找到任何已落盘的豁免声明**覆盖这两份（`W-1.5-ORCHESTRATION.md` §5 / T-6 只豁免"D-11 之前"的门禁）。

**判据（二选一即可关闭）**：
1. 以 `python3 scripts/onto1_gate_log.py scripts/onto1_evidence_board_check.py --gate`（及 `--selftest`）**重记**这两门禁，日志出现 `# artifact=scripts/onto1_evidence_board_check.py@<sha256>` 且等于磁盘；或
2. 若自指结构使其**技术上不可行**，则在 `W-1.5-ORCHESTRATION.md` §5 或 `TL-DECISIONS-W-1.md` **显式登记豁免**并附可复核证据（例：`record_gate.py` 在命令运行期已创建日志文件 ⇒ 板面 E2 必然看到自身孤儿 —— 需给出该行为的 `文件:行` 或一次可复现的失败输出）。

> **我未能验证的部分（如实声明）**：我**没有**实验条件判定判据 2 是否成立——验证它需要实际执行 `record_gate.py`（会写 `EVIDENCE.json` 与新日志），**超出我的只读写域**。因此我不断言"本可套用包装器"，只断言"当前两份日志缺自证行、且无可见豁免"。

## 第四轮结论

| 项 | 状态 |
|---|---|
| **U-1**（G5 空转 BLOCKER） | ✅ **关闭**（65/65；M9b-3 有区分度；退化副本 13/14 反证） |
| **U-2**（D-12 反例仅 WEAK 半边） | ✅ **实质关闭**（逐行校验与 tier 无关；MEDIUM 行实测命中） |
| **U-3**（§8.1 表述） | ✅ **已就地更正** + `W15TL-09` 落盘 |
| **U-6 / U-7**（E2 前缀制盲区 / 白名单通配重叠） | ✅ **关闭**（E2 全量 70 份、orphan 0；39 条全精确名、重叠 0；M4/M5/M5b 我独立复现有效） |
| **E5 收窄** | ⚠️ **可接受（我判不构成缺陷）**；附加监控判据：静态时刻 `registered ∩ allowlisted` 必须为 0（现为 0） |
| **U-4**（C-2 两处真实冲突） | ❌ **未关闭**（Wave 3） |
| **U-5**（C5/C7） | ⚠️ **部分未关闭**：C5 在 `onto1_reference_alignment_check.py:15` 仍写 14（实际 16）、白名单理由中板面 selftest 计数 5（实际 7）；C7 字面未完成（`a3fix-after-*` 4 份 `# artifact=` = 0），已如实登记 |
| **U-8 / U-9 / U-10** | 转 Wave 2 抽检义务 / 已处置 / 待追认 |
| **U-11（新增 MAJOR）** | ❌ **本轮重记的 2 个板面门禁日志缺 D-11 自证行**（22 份为 T-6 祖父条款可接受） |
| **N-8（新增，非阻塞）** | M9b-3 的区分度依赖夹具行序，建议把"P0 行非末位"也变成断言 |

**总判定：仍为 `NOT_ACCEPTED`。** 三条独立理由：① `wi_a4_namespace_collision` 仍是唯一 fail（C-2 未修，Wave 3），`ready_for_independent_qa` 硬约束未满足；② U-11 为 MAJOR（证据-制品绑定缺口，2/31）；③ U-5 的 C5 存在未同步的计数口径（属"假绿"同族的书写口径问题，虽不影响退出码）。

**红线复检（本轮，`not-accept` 不变）**：`git status --porcelain -- generated/ specs/ docs/dd/` = 空；无暂存；`loop_guard` / `onto1_evidence_board_check --gate` / `make memory-check` / `make evidence-check` **全 PASS**；`independent_qa` 仍 `{"status":"pending","actor":null,…}`（我未预填，TL 亦未预填）；本轮我的写入仅本文件（追加），KERT 零写入。

**非声明**：本追加节同样**不构成** `QA_PASS` / `DEV_SELF_CHECK_PASS`；不覆盖 Wave 0+；不代表 Owner 批准；不判定 KERT 侧内容。**未验证**（除上引 N-8 与 `record_gate.py` 行为外）：`--report` 全量重生成（未跑；但本轮 summary 内容我已核对：`true_obligation=691 / needs=361 / sum=1052 / closed=True`、`W2_SPLIT 291 / W3_CONSUMER_SWITCH 381 / W3_KERT_ASSETS 19`，与 CSV 一致）；`make check` / Maven 类门禁（未跑，不作断言）。

---
---

# 第五轮复验（2026-09-21，U-11 / D-14 / N-8 / C5 回归）

| 项 | 值 |
|---|---|
| 复验人 | `qa-w15r`（同前，独立复算；**不采信 TL 自述**） |
| 复验基线 | `onto1_obligation_triage.py = cb1da55dbee150f6…` · `onto1_reference_alignment_check.py = 917df73b42554a7d…` · `onto1_evidence_board_check.py = 1f7227633acb6076…` · `non-gate-log-allowlist.json = 2127f14d317df650…` · `obligation-triage.csv = 58671a908bae8d7d…`（**仍未变**） |
| **结论** | **U-11 / N-8 / C5 全部关闭**；**新增 1 项 MEDIUM（U-12）**；总判定仍 `NOT_ACCEPTED`（剩 C-2 属 Wave 3 + U-12 + C7 字面） |

## 5.1 ① U-11 关闭判据（**通过，且我用制品时间而非文档时间戳判定分界**）

**(a) 抽查板面两门禁日志的自证行 == 磁盘**：

```
  [OK] wi_evidence_board_check              wi_evidence_board_check-20260920T161548Z.log  @1f7227633acb6076
  [OK] wi_evidence_board_check_selftest     wi_evidence_board_check_selftest-20260920T161548Z.log  @1f7227633acb6076
磁盘实测 scripts/onto1_evidence_board_check.py = 1f7227633acb6076
```

**(b) 全量结论"D-11 之后缺自证 = 0"——我复核成立**。做法：取**最早一份含自证行的日志**的 `executed_at` 作为 D-11 生效下界（`2026-09-20T15:46:13Z`，即 `wi_w15_a3_acceptance`，也就是包装器首次被使用的时刻），再检查全部无自证行者是否**严格早于**它：

```
含自证行 9 / 缺 22 ；自证行者中哈希与磁盘不符: 0
earliest_wrapper = 2026-09-20T15:46:13.322663+00:00
无自证行的 22 份，其 executed_at 最大值 = 2026-09-20T15:22:14.286523+00:00（wi_a2_wave0_readiness_selftest）
  ⇒ 22/22 全部严格早于 earliest_wrapper
D-11 之后仍缺自证的门禁数 = 0
```

⇒ **TL 的"9 份含自证、0 不符；22 份全在 D-11 之前；D-11 之后缺自证 = 0"三条我逐条复现成立** ✅（分界不依赖 TL 文档里混用的 `Z` 标注）。

## 5.2 ② D-14（`max_attempts_per_gate` 5 → 8）—— **可接受（一次性语义修正），附 3 项硬条件**

**先确认机制前提属实**（回源 `scripts/record_gate.py:60-63`）：

```python
iter_log = loop / "memory/waves/W0-ITER.md"
attempts = iter_log.read_text(encoding="utf-8").count(f"Gate: `{args.gate}`")
max_attempts = int(spec.get("repair_policy", {}).get("max_attempts_per_gate", 0))
if max_attempts < 1 or attempts >= max_attempts:
    raise ValueError(f"gate attempt budget exhausted: {attempts}/{max_attempts}")
```

⇒ 计数 = `W0-ITER.md` 中 ``Gate: `<id>` `` 的出现次数，预算取自 `LOOP.yaml.repair_policy.max_attempts_per_gate`。**"revision 变更后重记"与"修复尝试"在计数上不可区分**是**真实机制缺陷**，不是借口。`LOOP.yaml:271` 现为 `"max_attempts_per_gate": 8` ✅。

**我判可接受**，理由：① 上限仍是**有限**的（非无限重试）；② 调高**不削弱任何断言**——它是调度参数、不是判据，且这些门禁是**确定性**的（同输入同结果 ⇒ 不存在"重试到偶然变绿"的通道；唯一的非确定性来自记录过程本身，而过程绿我已独立复跑确认）；③ 配套义务可执行且我抽查成立（见下）；④ 替代方案（把 5 保持不动）会让"日志哈希 ≠ 磁盘"这一**更严重**的状态长期存在——两害相权。

**硬条件（不满足则我改判 MAJOR）**：

- **U-12（新增，MEDIUM）规范性文档未同步 ⇒ "自愈耗尽"的定义域现在有两个数值**。全 Loop `max_attempts` 扫描：

  | 位置 | 现值 | 判定 |
  |---|---|---|
  | `LOOP.yaml:271` | `8` | ✅ 已改 |
  | `memory/TL-DECISIONS-W-1.md:75`（D-14） | `5 → 8`（含理由与义务） | ✅ |
  | `memory/W-1.5-ORCHESTRATION.md:99`（T-6） | `5 → 8` | ✅ |
  | **`memory/PROTOCOL.md:34`** | 「（**=5**，由 `scripts/record_gate.py` 计数）」 | ❌ **未同步** |
  | **`memory/W-1.5-ORCHESTRATION.md:47`** | 「**max_attempts = 5**（单门禁）；超限 ⇒ pilot 写 `BLOCKED.md` 并停止」 | ❌ **未同步，且与同文件 :99 自相矛盾** |
  | `memory/handoffs/ICO-01-集成契约Owner候选准备包.md:83` | 「最多 **5** 次…`max_attempts_per_gate = 5`」 | ❌ 未同步（交付物） |

  影响不是措辞：`PROTOCOL.md:34` 的"自愈耗尽"是**五类硬阻塞之一**的定义，`W-1.5-ORCHESTRATION.md:47` 是限流纪律的**规范条文**。两者与 `LOOP.yaml` 不一致 ⇒ 执行者按哪一条行动会产生不同行为（读 :47 会提前停并写 `BLOCKED.md`，读 `LOOP.yaml` 会用 8）。**判据**：上述三处改为 8（或在原地加 `D-14` 注并指明 `LOOP.yaml` 为准），再 `grep -rn 'max_attempts' loops/ONTO1-ontology-split/` ⇒ 规范类条文只出现 **8**。
- **不得把"再调高"当常规解法**。当前预算消耗（`W0-ITER.md` 的 ``Gate: `<id>` `` 计数 / 上限 8）：`wi_evidence_board_check` **7/8**、`…_selftest` **7/8**、`wi_a2_obligation_triage`(+`_selftest`) **6/8**、`wi_a3_reference_alignment` **5/8**、`…_selftest` **4/8**、`wi_a4_namespace_collision` **2/8**。⇒ **板面两门禁只剩 1 次**；下一次制品 revision 变动若需重记即会再次触顶。**判据**：若再次触顶，出口必须是①落地 `--repair` / `--refresh-after-revision` 的意图区分，或②走 ADR 级决定；**再次调高上限即判 MAJOR**（否则"绑住就抬高"会把这条控制彻底抵消）。
- 保留 D-14 已写义务且我抽查成立：每次尝试由工具自动登记（`W0-ITER.md` 现含本轮 `wi_evidence_board_check*` / `wi_a2_obligation_triage*` / `wi_a3_reference_alignment*` 的重记记录）· **未编辑 `W0-ITER.md` 重置计数**（未发现历史缺失/重排）· 重记原因已写入 `FAILURES.md` / `TL-DECISIONS-W-1.md`。
- **附带复核（正面）**：`record_gate.py` 因非 0 退出自动落账的 **9 条**条目**一条未删**，逐条由 `PENDING_ROOT_CAUSE` 重标为 `PROCESS_DEFECT_FIXED（原自动记账为 PENDING_ROOT_CAUSE）`，且每条带 `校核（TL…）` 行——我实测 `^## 20260920T` 段 = 9、`校核（TL` = 9、无"无校核"残留 ✅（append-only 纪律保住）。

## 5.3 ③ N-8 / M9c —— **关闭（我自建元变异复现）**

`onto1_obligation_triage.py:1555-1565` 新增 M9c 前置断言；正常运行：

```
[selftest] PASS  M9c 前置：P0 夹具行**不落在末位**（M9b-3 区分度的前提）  (p0_index=[7] total=9)
[selftest] 15/15 用例符合预期
```

**我自建元变异**（复制脚本到 `/tmp/qa-w15r/n8/`，把 `fixture_rows` 内 M9 块与 M8 块**整体交换**，使 P0 行落末位；回源 `:1359-1368`）：

```
fixture_rows 区间 = 1330 .. 1369    M9 块 = 1361..1364 | M8 块 = 1365..1368
交换后顺序末位 = apps/api/src/main/java/x/dto/CustomerModelDto.java
=== 元变异 selftest ===
[selftest] PASS  M9b-3 …  (touched=1 G5hits=1)
[selftest] FAIL  M9c 前置：P0 夹具行**不落在末位**  (p0_index=[8] total=9)
[selftest] 14/15 用例符合预期          meta-mutation exit=2
```

⇒ 与 TL 声明（`p0_index=[8]`、14/15）逐字一致 ✅。
**我补一点推理（该元变异单独看会误解）**：此元变异下 **M9b-3 仍 PASS**（因为真值代码已修，逐行校验与位置无关），只有 M9c 失败。这恰说明 **(M9c + M9b-3) 是一对**：M9b-3 抓"缩进出循环"的死代码（前提是 P0 行非末位），M9c 抓"前提被破坏"。二者合起来才封闭"**死代码 ∧ P0 行在末位**"这一组合漏洞——单独任一条都不够。**N-8 关闭。**

## 5.4 ④ C5 两处计数 —— **关闭（逐项核对，非只看文字）**

1. `onto1_reference_alignment_check.py:16-17` 现写「`--selftest` 共 **16 项**（对照 4：M0 基线 / M6 文本到手 / M10 规则陈述放行并断言计数 / M15 词级否定标题语境放行；变异 12：M1~M5、M7~M9、M11~M14）」。
   我逐项核对代码：`SELFTEST_CASES` 实际 **16** 条（`grep -cE '^    \("M[0-9]+'` = 16，列出的标识为 M0~M15）⇒ 对照恰为 M0/M6/M10/M15 四项、变异恰为其余 12 项 ⇒ **数目与归属均正确** ✅
2. `non-gate-log-allowlist.json:140` 现写「…现为 **7 用例**（M0~M5、M5b）」。我实跑 `--selftest` 得 **7 条 PASS**（M0/M1/M2/M4/M5/M5b/M3）⇒ 口径正确 ✅

## 5.5 ⑤ 板面 / logs 自证哈希 —— **本轮"0 不一致"成立**

| 检查 | 实测 |
|---|---|
| 含自证行的门禁日志 | **9 份，9/9 哈希 == 磁盘，0 不符**（A1 `@cb1da55dbee150f6`、refalign `@917df73b42554a7d`、板面 `@1f7227633acb6076`、collision `@8c18b5b3adc767e5`、验收仪器 `@4fb2b1e687c0c420`） |
| D-11 之后缺自证 | **0**（22 份无自证者全部早于包装器首次使用时刻 `15:46:13Z`） |
| `EVIDENCE.json` 全量 | 门禁 **31**，`output_sha256` 与磁盘日志文件哈希 **31/31 相符**、0 不一致、0 缺失 |
| 唯一非 pass 门禁 | `wi_a4_namespace_collision`（exit 2） |

**并且我的 E5 监控判据（第四轮给出的约束）在本轮新白名单上复检通过**：

```
白名单规则=50 含通配规则=0 -> []
日志=81 登记=31 白名单命中=50 孤儿=0 ；未登记且未入册=[]
**registered ∩ allowlisted = 0**
```

⇒ 无生效豁免、无通配、无孤儿；板面 15 份相关日志逐条为"已登记 2（`161548`）+ 已入册 13"，无隐藏项（含预算触顶的 `161536Z` FAIL attempt，亦已入册且落 `FAILURES.md`）。

## 第五轮结论与未关闭清单

| 项 | 状态 |
|---|---|
| **U-1 / U-2 / U-3 / U-6 / U-7 / U-11 / N-8 / C5** | ✅ **全部关闭**（本轮新关：U-11、N-8、C5） |
| **E5 收窄** | ⚠️ 可接受；监控判据（静态 `registered ∩ allowlisted == 0`）本轮实测 **0** ⇒ 未触发 |
| **U-4**（C-2 两处真实前缀冲突） | ❌ **未关闭**（Wave 3）：`[C-2] FAIL（实测 2 / 登记 2 / 未登记 0 / 陈旧 0）`、`FAIL（2 项）⇒ 阻断发布` |
| **U-5 / C7** | ⚠️ 字面未完成：`a3fix-after-*.log` 4 份 `# artifact=` = **0**（作者已下线，已如实入册） |
| **U-12（新增，MEDIUM）** | ❌ `max_attempts` 规范性条文漂移（`PROTOCOL.md:34` = 5、`W-1.5-ORCHESTRATION.md:47` = 5 且与 :99 自相矛盾、`ICO-01-…md:83` = 5） |
| **U-8 / U-10** | 转 Wave 2 抽包抽样义务 / 待追认 |

**总判定：仍 `NOT_ACCEPTED`。** 剩三条：① `wi_a4_namespace_collision` 仍是唯一 fail（C-2 未修，`ready_for_independent_qa` 硬约束未满足）⇒ **不得记 `QA_PASS`**；② **U-12**（控制定义漂移，MEDIUM）；③ C7 字面未完成（已登记）。

**红线与板面复检（本轮）**：`git status --porcelain -- generated/ specs/ docs/dd/` = 空；无暂存；KERT 今日零写入；`loop_guard` / `onto1_evidence_board_check --gate` / `make memory-check` / `make evidence-check` **全 PASS**；`independent_qa` 仍 `{"status":"pending","actor":null,…}`（我未预填）；本轮我的写入仅本文件（追加）。

**非声明**：本节同样**不构成** `QA_PASS` / `DEV_SELF_CHECK_PASS`；不覆盖 Wave 0+；不代表 Owner 批准；不判定 KERT 侧内容。**未验证**：`record_gate.py` 的写入行为（我无写权限，故未实验"自指结构是否使套用包装器不可行"——本轮已不需要该判据，TL 走了重记路线且我复核通过）；`--report` 全量重生成（未跑）；`make check` / Maven 类门禁（未跑，不作断言）。

---
---

# 第六轮｜**定向确认**（2026-09-21，仅两条判据）

| 项 | 值 |
|---|---|
| 复验人 | `qa-w15r`（TL 要求"只做一次定向确认，不必再全量"） |
| 复验基线 | `LOOP.yaml` `max_attempts_per_gate=8` · `memory/PROTOCOL.md` · `memory/W-1.5-ORCHESTRATION.md` · `memory/TL-DECISIONS-W-1.md`（D-15）· `memory/waves/W0-ITER.md` · `EVIDENCE.json` |
| **结论** | **判据2（D-15）通过；判据1（U-12 关闭）不通过——仍有 2 处规范类裸 5**；且**其中一半归我方判据口径过窄**（如下） |

## 6.1 判据 1：`max_attempts_per_gate` 扫描 —— **窄口径过、实质口径不过**

**(a) TL 给的判据（窄口径）——通过**：

```
$ grep -rn 'max_attempts_per_gate' loops/ONTO1-ontology-split/ --exclude-dir=waves | grep -v INDEPENDENT-QA-W15R
  LOOP.yaml:271:    "max_attempts_per_gate": 8,
  memory/PROTOCOL.md:34:…（**=8** … 该上限于 2026-09-21 由 D-14 自 5 调整为 8 … 权威值一律以 LOOP.yaml 为准）
  memory/handoffs/ICO-01-…md:83:…同一门禁**最多 8 次**…`max_attempts_per_gate = 8`，**2026-09-21 由 D-14 自 5 调整**…
  memory/TL-DECISIONS-W-1.md:71/81/85（D-14/D-15 正文，"由 5 调整为 8" 的历史陈述）
```

⇒ 配置键层面**只剩 8**；D-14/D-15 正文出现的 5 是**变更记录本身的必要内容**，不构成漂移 ✅。

**(b) 实质判据（"规范类文本中的上限叙述只出现 8"）——不通过**。用宽口径扫"上限叙述"（regex：`最多N次 | attempt ≤/<= N | （N 次）`）：

```
  memory/PROTOCOL.md:14    ……失败自动先写 FAILURES.md和ITER；最多5次，之后置`blocked`。
  memory/W-1.5-ORCHESTRATION.md:32    PLAN ──▶ ITER(attempt ≤ 5) ──▶ 自审 ──▶ … ──▶ 板面更新
  memory/handoffs/ICO-01-…md:83       ……最多 8 次……= 8……（已改）
```

| # | 位置 | 现状 | 与谁矛盾 |
|---|---|---|---|
| **U-12a** | **`memory/PROTOCOL.md:14`** | 「…**最多5次**，之后置 `blocked`」 | **同文件 `:34` 就写 `=8`** ⇒ **同一节内自相矛盾**（`:14` 是 §迭代 的流程句，`:34` 是五类硬阻塞定义） |
| **U-12b** | **`memory/W-1.5-ORCHESTRATION.md:32`** | 流程图「ITER(**attempt ≤ 5**)」 | 同文件 `:47` 写 `= 8` ⇒ 自相矛盾 |

另注：TL 表中列为"已修"的 **`W-1.5-ORCHESTRATION.md:52`（"（5 次）"）**，我按**内容**复查该行现为"自愈阶梯"（不含 5），全文件按宽口径也搜不到"（5 次）"——即**无法确认该处被改过**；结合 `:32` 仍为 `≤ 5`，实际"共 4 处"应更正为**已改 3 处 + 漏 2 处（`:14`、`:32`）**。请 TL 以**内容检索**而非行号复核。

**责任划分（我如实自认一半）**：我第五轮给的判据写的是 `grep -rn 'max_attempts'`——**只覆盖"配置键"口径，未覆盖"上限叙述"口径**；TL 严格照该判据执行（并额外用 `max_attempts_per_gate` 扫了一遍），因此这两处残留是**判据口径缺陷**导致的必然盲区。这与本 Loop 已登记的 `S-4` / `W15TL-05` **同族**（"我给的规格不足 ⇒ 产出必然有盲区"）。

**可执行的宽判据（请照此复核，一条命令）**：

```
grep -rnE '最多[ ]?[0-9]+[ ]?次|attempt[ ]?[≤<=]+[ ]?[0-9]+|[（(][ ]?[0-9]+[ ]?次[）)]' \
  loops/ONTO1-ontology-split/memory/ loops/ONTO1-ontology-split/*.md loops/ONTO1-ontology-split/*.json \
  | grep -v 'D-14' | grep -v 'INDEPENDENT-QA-W15R'
```
**期望**：规范类文本（`PROTOCOL.md` / `W-1.5-ORCHESTRATION.md` / `ICO-01-…md` / `ORCHESTRATOR.md` / `NEXT_SESSION.md` / `STATE.json`）**不出现除 8 以外的上限数值**；`waves/`（历史产出）与 D-14/D-15 正文（变更记录）除外。
**实测（本轮）**：仍命中 `PROTOCOL.md:14` 的 `最多5次` 与 `W-1.5-ORCHESTRATION.md:32` 的 `attempt ≤ 5` ⇒ **U-12 未关闭**。

## 6.2 判据 2：D-15 记录在案 + 消耗公示 —— **通过**

**(a) D-15 条文（回源 `memory/TL-DECISIONS-W-1.md:69-77`）**：明确写出

- 「**再触顶时，出口只能是**：① 落地 `record_gate.py` 的 `--repair` / `--refresh-after-revision` **意图区分**（共享工具，改动前须评估对其它 Loop 的影响并留痕）；或 ② 走 **ADR 级决定**。**再次单纯上调上限即判 MAJOR**——理由：该控制一旦"绑住就抬高"，即被"抵消"。」✅
- 第 3 条：接受我的 E5 监控判据「任意静态时刻 `registered ∩ allowlisted == 0`；`>0` 且无 W15TL-10 类中间态声明 ⇒ MAJOR」✅
- 第 4 条（给下一 holder）：改脚本必须重记、**重记前先查预算**、预算尽即走 ①/②，"不得先重记再说" ✅

**(b) 消耗公示与实际计数逐条比对 —— 8/8 一致**：

| 门禁 | D-15 公示 | 我实测（`Gate: \`<id>\`` / 8） | 判定 |
|---|---|---|---|
| `wi_evidence_board_check` | 7 | **7**/8 | ✅ |
| `wi_evidence_board_check_selftest` | 7 | **7**/8 | ✅ |
| `wi_a2_obligation_triage` | 6 | **6**/8 | ✅ |
| `wi_a2_obligation_triage_selftest` | 6 | **6**/8 | ✅ |
| `wi_a3_reference_alignment` | 5 | **5**/8 | ✅ |
| `wi_a3_reference_alignment_selftest` | 4 | **4**/8 | ✅ |
| `wi_a4_namespace_collision` | 2 | **2**/8 | ✅ |
| `wi_w15_a3_acceptance` | 1 | **1**/8 | ✅ |

**(c) "本次 U-12 的文档同步不触发任何重记" —— 核验成立**：
- `evidence/*.log` 总数 **81**（与第五轮相同，未新增日志）；
- `EVIDENCE.json` 中 `wi_a3_reference_alignment` = `…161535Z.log` / `…161536Z.log`、板面 = `…161548Z.log`、collision = `…155915Z.log`、acceptance = `…154613Z.log` —— **与第五轮完全一致**；
- 预算计数与第五轮逐项相同（board 7/7、triage 6/6、refalign 5/4、collision 2）⇒ **文档同步确实零消耗** ✅

## 6.3 第六轮结论

| 项 | 状态 |
|---|---|
| **判据 2（D-15）** | ✅ **通过**（条文明确 + 公示 8/8 属实 + 零预算消耗） |
| **判据 1（U-12）** | ❌ **未关闭**：`PROTOCOL.md:14`「最多5次」、`W-1.5-ORCHESTRATION.md:32`「attempt ≤ 5」（各与其同文件他处 8 自相矛盾）；**判据口径缺陷一半归 QA**，已给出宽判据 |
| U-11 / N-8 / C5 / U-1 / U-2 / U-6 / U-7 | ✅ 维持关闭 |
| **U-4**（C-2，Wave 3）· **U-5/C7** 字面 · U-8 / U-10 | ❌/⚠️ 状态不变 |

**总判定：仍 `NOT_ACCEPTED`。** 剩三条：C-2（`[C-2] FAIL（实测 2）`，`RETURN_TO_HLD` 有效期内不得动 `specs/` 权威制品）· **U-12（2 处规范类裸 5）** · C7 字面（`a3fix-after-*` 4 份无自证行，已如实入册）。

**定向确认的边界声明**：本轮我**只**跑了上述两条判据（按 TL 要求不做全量）；未重跑门禁四连、未复算 CSV/哈希。故本节**不更新**第五轮的红线与板面结论——第五轮的 `loop_guard` / `evidence-board` / `memory-check` / `evidence-check` 全 PASS、受控目录 0、KERT 零写入、`independent_qa` 仍 `pending/actor=null` 仍为最新有效记录。

---
---

# 第七轮｜**最终定向确认 + 批次收束核验**（2026-09-21）

| 项 | 值 |
|---|---|
| 复验人 | `qa-w15r`（TL 要求"最后一次定向确认"，仅两条命令 + 收束核验） |
| **结论** | **U-12 关闭 · D-16 在案 · 收束声明核验通过；本批仍 `NOT_ACCEPTED`（不得记 `QA_PASS`）** |

## 7.1 判据 1：U-12 关闭 —— **通过（规范类零残留）**

宽口径复扫 `grep -rnE '最多[ ]?[0-9]+[ ]?次|attempt[ ]?[≤<=]+[ ]?[0-9]+|[（(][ ]?[0-9]+[ ]?次[）)]' loops/ONTO1-ontology-split/ --exclude-dir=waves`，命中按类归因：

| 类别 | 命中数 | 判定 |
|---|---|---|
| `memory/handoffs/INDEPENDENT-QA-W15R-…md`（**我的报告**，D-16 §2 明列排除） | 9 | 合理命中（报告引文） |
| `FAILURES.md`（**变更记录本身**） | 4 | 合理命中 |
| `memory/TL-DECISIONS-W-1.md`（D-16 事实段**引述缺陷原文**） | 2 | 合理命中 |
| `STATE.json:10`（状态叙述**引述缺陷原文**） | 1 | 合理命中（属"变更记录/引文"类，非规范条文） |
| **`memory/PROTOCOL.md:14`** | **1** | **规范条文，已修为 8** |
| **`memory/W-1.5-ORCHESTRATION.md:32`** | **1** | **规范条文，已修为 8** |
| **`memory/handoffs/ICO-01-…md:83`** | **1** | **规范条文，已修为 8** |

⇒ 三份规范条文各**只剩 1 处命中且其值均为 8**；**无任何裸 5**。逐条复查：

```
memory/PROTOCOL.md:14        ……**最多 8 次**（2026-09-21 由 D-14 自 5 调整，D-15 规定不得再上调；**权威值以 LOOP.yaml…为准**），之后置 blocked。
memory/W-1.5-ORCHESTRATION.md:32   PLAN ──▶ ITER(attempt ≤ 8，见 D-14/D-15) ──▶ 自审 ──▶ … ──▶ 板面更新
memory/W-1.5-ORCHESTRATION.md:53   ……自愈耗尽（**现 8 次**，见上 D-14）/ 安全隐患。
memory/handoffs/ICO-01-…md:83      ……同一门禁**最多 8 次**……= 8，**2026-09-21 由 D-14 自 5 调整**……
```

**白名单两处良性命中已消**：`non-gate-log-allowlist.json:24/:28` 的「（2 次）」已改为「（**由通配展开为 2 条精确名**）」⇒ 不再匹配上限叙述模式，且**计量对象写明**（符合 D-16 §3）✅

> **我对自己第六轮一处判断的更正（诚实）**：我第六轮写「无法确认 `W-1.5-ORCHESTRATION.md:52` 被改过」。TL 在 `W15TL-13 §13.1` 说明该行因插入段落**下移为 `:53`**；本轮按**内容**复查确认 `:53` 现为「自愈耗尽（**现 8 次**，见上 D-14）」⇒ **TL 该处确已修，是我用快照行号判断造成的误判**。这正是 D-16 §4（禁行号定稿）的正面例证，也再次说明我第五轮给的判据口径过窄是共同成因。

## 7.2 判据 2：D-16 在案 —— **通过（五要素齐备）**

回源 `memory/TL-DECISIONS-W-1.md:69-79`（D-16）：

| D-16 要求 | 条文位置 | 判定 |
|---|---|---|
| ① 权威值/常量变更的验收判据**必须是宽口径内容检索**（除配置键外须覆盖叙述形态，如 `最多N次`/`attempt ≤ N`/`（N 次）`/`上限为 N`） | `:75` | ✅ 明文 |
| ② **显式排除并声明三类合理命中**：历史产出（`memory/waves/**`、旧日志）· 变更记录本身（D-14/D-15、`FAILURES.md`、QA 报告）· 计量对象不同的数字 | `:76` | ✅ 明文 |
| ③ **数字必须写明计量对象** | `:77` | ✅ 明文 |
| ④ **禁止用行号复核定稿**，一律以内容检索为准 | `:78` | ✅ 明文 |
| ⑤ **执行者不得以"判据是他人给的"免责**：判据不足时先补判据再宣称通过（并记载同类代价第 3 次 `S-4`→`W15TL-05`→U-12） | `:79` | ✅ 明文 |

另：`FAILURES.md` `W15TL-13` 标题仍为"四处"，但已追加 **§13.1 更正**「我修了 4 处（含 `:52`→`:53`）·**漏了 2 处**（`:14`、`:32`）」⇒ **"实际漂移 6 处（修 4 漏 2）"已落盘** ✅（append-only，原条未覆盖）。

## 7.3 收束声明核验 —— **通过**

| TL 的收束声明 | 我的实测 | 判定 |
|---|---|---|
| **本次 U-12 修复零消耗（未触发任何重记）** | `evidence/*.log` 总数仍 **81**（与第六轮相同）；`EVIDENCE.json` 中 triage=`161534`、refalign=`161535/161536`、板面=`161548`、collision=`155915`、acceptance=`154613` **与第六轮逐字相同** | ✅ |
| **脚本 revision 未变** | `onto1_obligation_triage.py= cb1da55dbee150f6` · `onto1_reference_alignment_check.py= 917df73b42554a7d` · `onto1_evidence_board_check.py= 1f7227633acb6076` · `onto1_gate_log.py= 5d081ea04802a64e`（与第六轮一致） | ✅ |
| **board / board_selftest 仍各 7/8** | 实测 `7/8` · `7/8`（triage 6/8 · refalign 5/8 · collision 2/8 · acceptance 1/8 亦一致） | ✅ |
| **`independent_qa` 保持 `pending`/`actor=null`，不代签** | `{"status":"pending","actor":null,"session":null,"attested_at":null,"evidence_file":null,"evidence_sha256":null}` | ✅ |

## 7.4 本批收束后的最终判定（我方结论）

**总判定：`NOT_ACCEPTED`（批次出口硬约束未满足）——本批不得记 `QA_PASS`。**

未关闭项（我逐条复核与 TL 收束声明一致，均为**非 Wave -1 可动**）：

| # | 项 | 复验判据（可复算） |
|---|---|---|
| ① | **C-2 两处真实前缀冲突**（Wave 3；`RETURN_TO_HLD` 有效期内不得改 `specs/` 权威制品） | `python3 scripts/onto1_namespace_collision_check.py --gate` ⇒ `[C-2] FAIL（实测 2 / 登记 2 / 未登记 0 / 陈旧 0）`、`FAIL（2 项）⇒ 阻断发布`；`EVIDENCE.json` 中 `wi_a4_namespace_collision` 为**唯一**非 pass |
| ② | **C7 字面未完成**（A3 已下线） | `grep -c 'artifact=' loops/ONTO1-ontology-split/evidence/a3fix-after-*.log` ⇒ 4 份全为 **0** |
| ③ | **U-8**：`action.domain` 6 行（实位于 `modules/human-action`）耦合为**推断** | Wave 2 **按包抽样**（55/6/4 每包 ≥3 行），判据 = 该模块是否在四层拆分的命名空间迁移范围内 |
| ④ | **U-10**：KERT 历史写入归属待追认 | 我只复核"本轮零写入"；归 KERT 维护方 / Owner |

**已关闭（六轮累计）**：U-1（G5 死代码 BLOCKER）· U-2 · U-3 · U-6 · U-7 · U-11（D-11 面状缺口 MAJOR）· **U-12** · N-8 · C5 · 判据 D-14/D-15/D-16 的受理与落盘。

**本轮红线复核（我自己的写入后必检）**：本轮我只跑了上述判据命令，**未产生仓库写入**（写入仅本报告文件的追加）。**自伤复检**：`refalign --gate` 在追加后仍 `verdict: PASS`（`files=4612 filenames=2 candidates=159 allowed=80 registered_legacy_hits=81 unreadable=0`，`allowed[rule_statement]=1` ⇒ **零新增命中**）；`memory-check` PASS；`evidence-board --gate` PASS；受控目录 `generated/ specs/ docs/dd/` 0 改动；KERT 今日零写入；日志总数 81 未变。

**非声明**：本节同样**不构成** `QA_PASS` / `DEV_SELF_CHECK_PASS`；不覆盖 Wave 0+；不代表 Owner 批准；不判定 KERT 侧内容；未跑 `--report` 全量重生成与 Maven 类门禁（不作断言）。
