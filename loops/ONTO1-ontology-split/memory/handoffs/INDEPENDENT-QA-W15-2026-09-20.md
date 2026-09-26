# INDEPENDENT-QA-W15｜ONTO1 W-1.5 独立审计报告（首轮）

| 项 | 值 |
|---|---|
| 审计人 | `qa-w15`（Independent QA，**非**开发角色延伸） |
| 审计对象 | PKG-A1 / PKG-A2 / PKG-A3（W-1.5 就绪加固） |
| 审计依据 | `memory/W-1.5-ORCHESTRATION.md`（§4 AU-1~AU-7，本报告判据**严于**该规格）、`memory/DISPATCH-W-1.5.md`、`memory/TL-DECISIONS-W-1.md`（D-2/D-3）、`memory/PLAN-NEXT.md` |
| 快照时刻 | `2026-09-20T15:19:09Z`（+0800 23:19） |
| 仓 / HEAD | `gits-cbanking` @ `784657f55a6f5eae1dc7d4ae699cf30c49c0c296`（分支 `recover/PI-ARCH-product-catalog`）；KERT @ `922a674d3385a803704bc900d4f8ca21523276ed` |
| 本报告权限 | **只写本文件**；未改任何实现/脚本/证据/TL 单写者文件；未写 KERT |

---

## 1. 结论

> **`NOT_ACCEPTED（产物未就绪）`**

三个 PKG **均未达到可审计状态**（无可核对的 HANDOFF、无登记建议、无门禁执行记录）。本结论**不是**对 pilot 交付质量的判定——**没有交付物可判**；它是"审计前置条件不满足"的判定。

| PKG | 交付状态（快照时刻实测） | 逐包结论 |
|---|---|---|
| **PKG-A1** | **零交付**：无 `scripts/onto1_obligation_triage.py`、无 `evidence/obligation-*`、无 `memory/waves/PKG-A1-PLAN.md`、无 `memory/handoffs/PKG-A1-*` | `NOT_ACCEPTED（未交付）` |
| **PKG-A2** | **在飞**：`memory/waves/PKG-A2-PLAN.md`（23:17）、`scripts/onto1_wave0_readiness.py`（23:18）已落盘；**缺** `memory/waves/PKG-A2-ITER.md`、`evidence/wave0-readiness-*`、`memory/handoffs/PKG-A2-*` | `NOT_ACCEPTED（在飞，未交回）` |
| **PKG-A3** | **零交付**：两个目标脚本 `scripts/onto1_namespace_collision_check.py`（mtime 22:24）、`scripts/onto1_reference_alignment_check.py`（mtime 22:23）**均早于本批次派工（23:15）**⇒ 未被改动；无 `evidence/a3fix-*`、无 PLAN、无 HANDOFF | `NOT_ACCEPTED（未交付）` |

**根因（非 pilot 过失，属编排缺陷）**：`DISPATCH-W-1.5.md` §3 **S-1 已主动登记**"`qa-w15` 与三个 pilot 同时启动 ⇒ QA 很可能在 pilot 交回前就出报告"。本报告即该预期形态。按 S-1 处置：**pilot 全部交回后须由 TL 重新派 QA 复核**，本报告保留作审计轨迹。

---

## 2. 审计范围与方法

| # | 动作 | 方法 | 是否可执行 |
|---|---|---|---|
| AU-1 | 交付物存在性 + 哈希 | `find` / `ls -la --time-style=full-iso` / 全仓 `grep -rIl`；哈希 `sha256sum` | ✅ 已执行（结果=不存在） |
| AU-2 | **复跑门禁** | 亲自执行 `--gate` / `--selftest`，记录**真实 exit**（不采信 pilot 日志） | ✅ 对**存量**门禁已执行；对 A1/A2 的新门禁**无对象可跑**（脚本不存在 / 在飞） |
| AU-3 | 回源抽样 | 手工核对 `文件:行`（见 §3.4，共 9 条，覆盖强/中/弱三层） | ✅ 已执行 |
| AU-4 | 变异有效性 | 手工注入变异 ⇒ 期望 FAIL；恢复 ⇒ 期望 PASS（**在 `/tmp` 内完成，未动仓内文件**） | ✅ 已执行 3 项（§4） |
| AU-5 | 红线扫描 | `git status --porcelain` 比对写域表；KERT 独立 `git status` + `find -newermt` | ✅ 已执行 |
| AU-6 | 记账 | `onto1_evidence_board_check.py --gate`（孤儿日志） | ✅ 已执行（记账本身属 TL，QA 不代记） |
| AU-7 | 落盘 | 本文件 | ✅ |

**对 TL 审计规格的加严（本报告额外要求）**：

1. **AU-1 加严**：不仅核对 HANDOFF 声明的路径，还要核对**声明哈希与实测哈希**——本轮即由此发现 `EVIDENCE.md:74` 哈希陈旧（§3.3 F-2，AU-1 原判据会漏过）。
2. **AU-2 加严**：除比对 exit，还须比对**逐项结果行**（如 `[C-4] FAIL`），因为同一 exit=2 可由不同子项造成（本轮 FAILURES 口径争议即源于此，§3.3 F-4）。
3. **AU-4 加严**：变异须覆盖"**断言范围被收窄**"这一方向（原规格只要求"注入 ⇒ FAIL"，覆盖不了"删检查项 ⇒ 仍 PASS"的假绿）。§4 E3 即为该方向的反例。
4. **AU-5 加严**：`loops/ONTO1-ontology-split/` 整体为未跟踪目录，`git status` **看不见目录内部**的逐文件改动 ⇒ 必须辅以 mtime 与内容哈希。

---

## 3. 逐包发现

### 3.1 PKG-A1 — 零交付

```
$ find . -iname "*PKG-A1*" -o -iname "*obligation-triage*" -o -iname "*onto1_obligation_triage*"
（无输出）
$ ls scripts/onto1_obligation_triage.py
ls: 无法访问 'scripts/onto1_obligation_triage.py': 没有那个文件或目录        → exit 2
$ grep -rIl "obligation-triage" . | grep -v node_modules
./.codebuddy/teams/99845736d49249b98b8907284fddb03e/onto1-w15/config.json   ← 仅派工文本
./loops/ONTO1-ontology-split/memory/PLAN-NEXT.md                            ← 仅计划文本
./loops/ONTO1-ontology-split/memory/W-1.5-ORCHESTRATION.md                   ← 仅规程文本
./loops/ONTO1-ontology-split/memory/DISPATCH-W-1.5.md                       ← 仅派工文本
./scripts/onto1_pkg_audit.py                                                ← 仅 TL 审计工具的 SCOPE 白名单
```

**缺失清单（`DISPATCH-W-1.5.md:15` 声明项逐条核对）**：

| 声明交付物 | 存在性 |
|---|---|
| `scripts/onto1_obligation_triage.py` | ✗ 不存在 |
| `evidence/obligation-triage.csv`（`PLAN-NEXT.md:40`） | ✗ 不存在 |
| `evidence/obligation-triage.json`（同上） | ✗ 不存在 |
| 净义务收敛报告（`PLAN-NEXT.md:41`） | ✗ 不存在 |
| `memory/waves/PKG-A1-PLAN.md` / `-ITER.md`（`W-1.5-ORCHESTRATION.md:40-41`） | ✗ 不存在 |
| `memory/handoffs/PKG-A1-HANDOFF.md`（`:43`） | ✗ 不存在 |
| 登记建议 `wi_a2_obligation_triage(+_selftest)`（`:74`） | ✗ 无（无从复跑） |

⇒ **AU-2/AU-3/AU-4 对本包不可执行**。**不代做**（`.codebuddy` 写域外禁止）。

### 3.2 PKG-A2 — 在飞，未交回

```
$ ls -la --time-style=full-iso scripts/onto1_wave0_readiness.py
-rw-rw-r-- 1 szf szf 29998 2026-09-20 23:18:42 scripts/onto1_wave0_readiness.py   ← 存在（在飞产物）
$ ls loops/ONTO1-ontology-split/evidence/ | grep -i wave0
（无输出）                                   ← 无任何证据产物
$ ls loops/ONTO1-ontology-split/memory/handoffs/PKG-A2-*
ls: 无法访问 ...: 没有那个文件或目录        → exit 2（无 HANDOFF）
```

**已存在**：`memory/waves/PKG-A2-PLAN.md`（5505B，23:17）。**PLAN 质量初判（仅结构，未审计实现）**：该 PLAN §5 明确识别了"**本门禁当前本来就 FAIL ⇒ 变异后 exit==2 是恒真断言**"这一空转陷阱，并约定 **一律断言到条目级**（`items["R1"].status == NOT_READY`）而不靠全局退出码凑数（`PKG-A2-PLAN.md:57-59`）；§3 区分 `--gate`（含 R6/R7，期望 exit 2）与 `--precheck`（除 R6/R7，期望 exit 0），并把"把 `--gate` 换成 `--precheck` 来变绿"列为**反模式**（`:44-45`）。**该设计方向正确**。

**缺失清单**：`PKG-A2-ITER.md`、`evidence/wave0-readiness-*`、`memory/handoffs/PKG-A2-HANDOFF.md`、登记建议、`--gate` / `--precheck` / `--selftest` 的真实执行记录。

⇒ **AU-2 不可执行**（无登记建议即无"声明的命令"可比对；且我在快照时刻跑它=审计在飞产物，无意义）。**不代跑**。

### 3.3 PKG-A3 — 零交付（但暴露 4 项**存量**实质缺陷，须计入 A3 的验收条件）

**A3 未交付的直接证据**：

```
$ ls -la --time-style=full-iso scripts/onto1_namespace_collision_check.py scripts/onto1_reference_alignment_check.py
-rw-rw-r-- 1 szf szf 38763 2026-09-20 22:24 scripts/onto1_namespace_collision_check.py
-rw-rw-r-- 1 szf szf 28610 2026-09-20 22:23 scripts/onto1_reference_alignment_check.py
```

两脚本 mtime **22:23/22:24**，均**早于** `DISPATCH-W-1.5.md` 落盘时间（23:15）⇒ 派工后**未被触碰**。基线哈希（供 TL 复核改动）：

```
$ sha256sum scripts/onto1_namespace_collision_check.py scripts/onto1_reference_alignment_check.py
3e54c8c835a1f257dc60656d94206d7bc58d4dab4ff4c77bc3162ed7927a34e9  onto1_namespace_collision_check.py
f53489f3d0bd4ae5bb3ed796a090589bd6345fc0b26391514fe9f71f8c4c0bc5  onto1_reference_alignment_check.py
```

**存量门禁真实复跑（AU-2，命令 + exit 逐条）**：

| 命令 | 真实 exit | 结果 |
|---|---|---|
| `python3 scripts/onto1_namespace_collision_check.py --gate` | **2** | `[C-2] FAIL（实测 2 / 登记 2 / 未登记 0 / 陈旧 0）`；`[C-4] FAIL（钉值 4 个）`；`C-1b NOT_EVALUATED`；`FAIL（4 项）⇒ 阻断发布` |
| `python3 scripts/onto1_namespace_collision_check.py --selftest` | **0** | `16/16`（M0/M1~M13/M-元/M0b 全 `PASS`） |
| `python3 scripts/onto1_reference_alignment_check.py --gate` | **0** | `OK` |
| `python3 scripts/onto1_reference_alignment_check.py --selftest` | **0** | `10/10 符合预期` |
| `python3 scripts/onto1_evidence_board_check.py --gate` | **0** | `gates=26`；`gate-like logs=44 registered=26 allowlisted=19 orphan=0`；`registered evidence files present=26/26` |
| `python3 scripts/onto1_evidence_board_check.py --selftest` | **0** | `M0/M1/M2/M3` 全符合预期 |

**与 `EVIDENCE.json` 机读板一致性**：26 门禁 = `{'pass': 25, 'fail': 1}`，唯一 fail = `wi_a4_namespace_collision`（`status=fail, exit=2`）。复跑结果**与板面一致**，无差异 ⇒ **AU-2 对存量门禁 PASS**。

**F-1（MAJOR，A3 的 B-4/D-2 未实现之实证）**：C-4 仍把"清单类工具产物"当钉值文件。

```
[S-1] C-4 钉值文件自冻结 FAIL 两项（实测）：
  C-4_PIN_FILE_UNFROZEN ... baseline-v2-manifest.json cac187a7624247a2
  C-4_PIN_FILE_UNFROZEN ... consumer-scan-manifest.json 45475058b3050fc1
```
判据：`TL-DECISIONS-W-1.md:33-37`（D-2）明确把 `baseline-v2-manifest.json`、`consumer-scan-manifest.json` 列为**不包含**的清单类产物。⇒ **D-2 收窄未实现**。

**F-2（MAJOR，新发现｜AU-1 加严项）**：`EVIDENCE.md` 声明的"独立冻结记录"哈希**与实测不符**。

```
$ sed -n '74p' loops/ONTO1-ontology-split/EVIDENCE.md
| `evidence/consumer-scan-manifest.json` | 扫描清单与哈希（**同时是 C-4 钉值文件**） |
  `sha256 310bb2306492a78c…`；**本行即其独立冻结记录**（供碰撞检查 C-4b 判定） |
$ sha256sum loops/ONTO1-ontology-split/evidence/consumer-scan-manifest.json
45475058b3050fc1adb409f88f57c86fcfb64ffa2a3891b67f53abdd20772f16   ← 实测
```
`310bb2306492a78c` 是**再生成前**的旧值（可回源：`evidence/wi_a4_namespace_collision-20260920T142432Z.log:14` 记录旧哈希；`…-145542Z.log:21` 记录现值 `45475058b3050fc1`）。⇒ 该"冻结记录"**自述即已失效**；对照 `EVIDENCE.md:71`（`baseline-v2-manifest.json` 声明 `cac187a7624247a2`）与实测 `cac187a7624247a2` **一致**，说明问题是 `:74` 未随再生成更新，而非口径问题。

**F-3（MAJOR，新发现｜机制性）**："自冻结"记录所在位置**不在门禁扫描根内**。

```
$ awk 'NR==299' scripts/onto1_namespace_collision_check.py
    freeze_root = freeze_root or (root / "loops/ONTO1-ontology-split/evidence")
```
`frozen_in()` 使用 `freeze_root.rglob("*")`（`:282`）。而 `EVIDENCE.md` 位于 **Loop 根目录**（`loops/ONTO1-ontology-split/EVIDENCE.md`），**不在** `loops/ONTO1-ontology-split/evidence/` 之下 ⇒ **即使 F-2 的哈希正确，该记录也不会被 C-4b 看到**。复现：C-4b 对两文件持续报 `PIN_FILE_UNFROZEN`。全仓 `grep -rIln "cac187a7624247a2"` 仅命中两处历史日志与该 `EVIDENCE.md` ⇒ `consumer-scan-manifest.json` **在任何位置都没有独立冻结记录**。
⇒ D-2 的正解应是"**把该文件排除出 C-4 范围**"而非"补冻结记录"；若 A3 选择补记录，则须同时解决"记录位置不在扫描根内"。

**F-4（MAJOR，表述/证据不一致，须 TL 澄清口径）**：`FAILURES.md` 的 `C-4 转 PASS` 与其引用的证据日志冲突。

```
$ grep -n "重跑结果" loops/ONTO1-ontology-split/FAILURES.md   → :162
   "… `--gate` **FAIL exit 2**（`C-2` 实测 2 处冲突未修 … `C-4` 转 PASS）；"
$ awk 'NR==10' loops/ONTO1-ontology-split/evidence/wi_a4_namespace_collision-20260920T142432Z.log
   [C-4] FAIL（钉值 4 个；含自引用与钉值文件自冻结）        ← 该条目自己引用的日志
$ awk 'NR==13' loops/ONTO1-ontology-split/evidence/wi_a4_namespace_collision-20260920T145542Z.log
   [C-4] FAIL（钉值 4 个；含自引用与钉值文件自冻结）        ← 当前登记证据
```
两次 attempt 的 C-4 **均为 FAIL**。按 D-1 第 2 条（"门禁按真实退出码记账，禁止把 fail 改写成 inconclusive/pass"，`TL-DECISIONS-W-1.md:20-22`），"C-4 转 PASS"这一表述**与自身引用证据不符**。可能的善意解释是"C-4 的**内容钉值项**（4 个）全部 PASS，但 C-4 整体仍 FAIL"——若如此，须在 `FAILURES.md` 改为可复核的子项口径。**我不断言动机，只报告不可复现性。**

**F-5（MINOR，B-4b 未实现之实证）**：头部自述与行为不一致**仍然存在**（且比 PLAN-NEXT 描述的多一处）。

| 位置 | 自述 | 实测 |
|---|---|---|
| `scripts/onto1_namespace_collision_check.py:13` | `C-4 钉值一致 … **可判定 → PASS**（4 个钉值）` | `[C-4] FAIL（钉值 4 个…）` |
| 同文件 `:34` | `--selftest 在 /tmp 沙箱树上做 **9 条变异 + 2 条对照**` | 实跑 **16** 条（M0/M1~M13/M-元/M0b） |
| 同文件 `:35` | `（沙箱全绿 / 真实仓 **INCOMPLETE**）` | 真实仓 = **FAIL(exit 2)**，非 INCOMPLETE |
⇒ `PLAN-NEXT.md:69` 只登记了 `:13` 一处（B-4b），**漏了 `:34`/`:35` 两处**；A3 的验收须覆盖这三处。

**F-6（MAJOR，A3 的 D-2 过渡义务未履行）**：D-2 要求"在收窄实现前，门禁输出须**显式标注** C-4 两条为已知误报（**声明而非隐藏**）"（`TL-DECISIONS-W-1.md:40`）。

```
$ grep -n "误报\|KNOWN_FALSE\|known_false" scripts/onto1_namespace_collision_check.py
（无输出 → exit 1，0 匹配）
```
实际输出为 `onto1-namespace-collision: FAIL: C-4: C-4_PIN_FILE_UNFROZEN …`，**无任何"已知误报"标注**。⇒ 该过渡义务**未履行**——这正是"死线前最便宜、且不受外部阻塞"的一项，却在派工后被跳。

### 3.4 回源抽样明细表（AU-3，9 条，覆盖强/中/弱三层）

> 说明：PKG-A1 要求"≥5 条且覆盖强/中/弱三层"，但因 **A1 零交付**，无 pilot 判定可抽。故本表抽检的是**三包共同依赖的基线事实与被引用的 `文件:行`**（这些正是 A1/A2/A3 判定链的地基；其中 F-2 一条即判为不成立）。

| # | 层 | 被核结论 | 回源 | 实测 | 判定 |
|---|---|---|---|---|---|
| S-1 | 强 | C-2a：`gits:` 双绑定（旧端） | `specs/semantic/gits-core.owl.ttl:1` | `@prefix gits: <https://gientech.com/gits/kno/> .` | ✅ 成立 |
| S-2 | 强 | C-2a：`gits:` 双绑定（第二处） | `specs/knowledge-architecture/instances/product/products.ttl:1` | `@prefix gits: <https://gits.bank.example/ontology/core#> .` | ✅ 成立 |
| S-3 | 强 | C-2a：第三处触发文件 | `specs/data/customer-source-mapping.r2rml.ttl:2` | `@prefix gits: <https://gientech.com/gits/kno/> .` | ✅ 成立 |
| S-4 | 强 | C-2b：`gits:Product` 同名不同 IRI | `…/products.ttl:10` 与 `:15` | 两行均为 `a gits:Product ;` | ✅ 成立 |
| S-5 | 中 | C-4b 行号引用（`PLAN-NEXT.md:69` B-4b 引 `:264`） | `scripts/onto1_namespace_collision_check.py:264` | `failures.append(f"C-4_PIN_FILE_UNFROZEN …` | ✅ 成立 |
| S-6 | 中 | freeze 扫描根 | 同文件 `:299` | `freeze_root = freeze_root or (root / "loops/ONTO1-ontology-split/evidence")` | ✅ 成立（并据此得 F-3） |
| S-7 | 中 | C-1a 旧端术语数 67 | `--gate` 输出 | `旧端术语 67`；`C-1a PASS`（32 类+34 对象属性+1 数据属性） | ✅ 成立 |
| S-8 | 弱 | `PENDING_TRIAGE = 0`（`WI-A2-消费者扫描报告.md:43`） | `evidence/consumer-scan-dispositions.json:436/:443` | 两处 `PENDING_TRIAGE` 均为 **catch-all 规则定义**（`R-CATCHALL-GITS`/`R-CATCHALL-KERT`，`action="待分类"`），**非命中行**；`consumer-scan-manifest.json:16` `pending_triage: 0` | ✅ 成立（未发现"把 PENDING 包装为通过"） |
| S-9 | 弱 | `EVIDENCE.md:74` 哈希冻结记录 | `EVIDENCE.md:74` vs `sha256sum` | 声明 `310bb2306492a78c…` ≠ 实测 `45475058b3050fc1` | ❌ **不成立** ⇒ F-2 |

**AU-3 结论**：9 条中 **8 条成立、1 条不成立**。按 TL 规格"有 1 条不成立 ⇒ 退回"，**该不成立项的回退对象是 TL 单写者文件 `EVIDENCE.md`**（非 pilot 交付物），故不作"退回 pilot"处理，**转为条件项 C-2**（§6）。

---

## 4. 反例构造结果（QA 本职：尝试证伪 pilot 结论）

### 4.1 A1 / A2 的反例 — **不可构造（对象不存在）**

- A1 反例要求"找一条被判 `HOMONYM_CANDIDATE` 但实际是本体制约消费点的文件"或"判 `TRUE_OBLIGATION` 却只含裸术语名的文件"——**无 `obligation-triage.csv` 即无判定集合**，不可构造。
- A2 反例要求"检查 R6/R7 是否被做成可跳过""`--precheck` 是否把 R1/R2 也放过"——**在飞产物无门禁执行记录**；我只能指出：`PKG-A2-PLAN.md:44-45` **已显式把"删 R6/R7 或改用 `--precheck` 变绿"列为反模式并写入不做清单**，故该反例方向在**设计层已被预置防线**；但**设计 ≠ 实现**，交回后必须以**变异**验证（见 C-5）。

### 4.2 A3 反例 — **已构造并复现（方法全在 `/tmp`，未动仓内任何文件）**

驱动脚本：`/tmp/qa15/drive.py`（读取 `--gate --json` 输出的 JSON 段，逐项打印 `checks["C-4"]`）。

**E1 对照（真实钉值）**
```
exit=2  C-4.status=FAIL  content_entries=4
  baseline/pass  attribution/pass  hits/pass  summary/pass  self_reference/pass
  freeze:baseline-v2-manifest.json/FAIL   freeze:consumer-scan-manifest.json/FAIL
```

**E2 变异（篡改一个**受控**钉值的期望哈希）⇒ 必须 FAIL**
```
$ cp evidence/baseline-v2-manifest.json /tmp/qa15/pins-tampered.json   # 将 baseline.sha256 置 000…0
exit=2  C-4.status=FAIL  content_entries=4
  baseline/FAIL (expected=0000000000000000, actual=705578d6324abd0c)
  C-4 failures: C-4 baseline 钉值漂移：gits-core.owl.ttl 705578d6324abd0c != 0000000000000000
```
⇒ **C-4 内容钉值断言有牙齿（非空转）**。恢复（不改仓、E1 即恢复态）⇒ 该子项 PASS。**AU-4 PASS**。

**E3 反例：断言范围收窄 ⇒ 未被拦下（**这正是任务书指定的 A3 反例方向**）**
```
$ cat /tmp/qa15/pins-narrowed.json   # 仅保留 attribution：删去 baseline/hits/summary 三项必需钉值
exit=2  C-4.status=FAIL  content_entries=3
  attribution/pass  hits/pass  summary/pass  self_reference/pass
  C-4 failures: 仅 freeze 两项（与本反例无关）
  ⇒ 内容层 **0 失败**
```
**结论**：把**受控制品 `specs/semantic/gits-core.owl.ttl` 从必需钉值集合中静默移除**后，C-4 **未产生任何内容层失败**。根因在 `check_c4` 的收尾判据：
```
$ awk 'NR==272' scripts/onto1_namespace_collision_check.py
    status = "FAIL" if failures else ("PASS" if entries else "FAIL")
```
非空转下限仅为"`entries` 非空（≥1）"，**没有"必需钉值 allow-list"**。⇒

> **判**：这是 **MAJOR（缺防线）**。它不构成本轮对 pilot 的判负（A3 未交付），但**必须成为 A3 的硬验收条件**：D-2 收窄**只能减"清单类产物"，绝不能减"受控制品"**；且须补一条断言——"必需钉值集合缺失任一项 ⇒ FAIL"，并配对应变异（删必需钉值 ⇒ 必须 FAIL）。否则"收窄"会成为新的假绿通道。

**E4（F-3 的独立复现）**：以 `--pins` 指向 `/tmp` 副本时，`freeze:` 记录随之转移到 `/tmp` 文件名上（`freeze:pins-tampered.json`），**证明 freeze 判定完全绑定于"被传入的 pins 文件自身"的位置**，与 F-3 的判断（记录位置决定可见性）互为印证。

### 4.3 D-3 / F3「`rule_statement` 放行」反例 — **对象不存在，故不构成 BLOCKER**

任务书要求"检查 F3 的 `rule_statement` 放行是否可被**真实符合性声称**利用（若可 ⇒ BLOCKER）"。

```
$ grep -n "rule_statement\|元陈述" scripts/onto1_reference_alignment_check.py
（无输出 → exit 1，0 匹配）
```
⇒ D-3 的长期项（"放行规则陈述行"）**未实现**；当前防线仍是"**文件级 `gb_scope` × 行级词表 + 行内/表格行/最近标题/父键否定标记放行**"（`onto1_reference_alignment_check.py:397` `classify_line(line, idx, lines)`）。因此**没有可被利用的 `rule_statement` 通道**，本项**不判 BLOCKER**。

但须记录**残余风险**（该脚本头部 `:19-21` 已如实自述"精度上限"）：**声称若紧邻否定标记仍可漏检**。故 A3 实现 D-3 时，其 `rule_statement` 放行**必须**附：
- 收紧语用（只放行**元陈述关键词**所在行：`注入`/`变异`/`禁用`/`词表`/`必须被判 FAIL` 等），**不得**用"目录白名单（`loops/**`）整体放行"——否则 `loops/**` 内任何真实符合性声称都可借道通过，**那就是 BLOCKER**；
- 一条反例变异：**在 `loops/**` 内写入一句不带否定标记的真实符合性声称 ⇒ 必须 FAIL**。当前 selftest 的 M2/M7 只覆盖"非 `loops/**`"与"去否定标记"两态，**覆盖不到"目录白名单被滥用"**。

---

## 5. 红线与诚实性

### 5.1 红线扫描（AU-5）

**写域比对**（依据 `DISPATCH-W-1.5.md:13-18` 写域表）：

```
$ git status --porcelain | grep -i -e onto1 -e obligation -e wave0 -e a3fix
?? loops/ONTO1-ontology-split/                    ← 整个 Loop 目录未跟踪（内部改动 git 不可见）
?? scripts/onto1_wave0_readiness.py               ← 属 PKG-A2 写域 ✅
?? scripts/onto1_obligation_triage.py             ←（无，A1 未写）
?? scripts/onto1_namespace_collision_check.py     ← 未改（mtime 22:24 < 派工 23:15）✅
?? scripts/onto1_reference_alignment_check.py     ← 未改（mtime 22:23 < 派工 23:15）✅
```

| 判据 | 结果 |
|---|---|
| 本批次写域**外**文件是否被改 | **未发现**（快照时刻 pilot 仅落 2 个文件，均在其写域内） |
| TL 单写者文件是否被 pilot 改 | **未发现**（`LOOP.yaml` 23:02 / `EVIDENCE.json` 23:02 / `EVIDENCE.md` 23:03 / `STATE.json` 22:57 / `FAILURES.md` 22:55 / `ROLE_BOARD.yaml` 22:25 / `NEXT_SESSION.md` 23:12 / `TL-DECISIONS-W-1.md` 22:56 —— 均早于派工 23:15，改动者应为 TL） |
| `specs/**` / `generated/**` / `docs/dd/**` | 本批次**未改**（`git status --porcelain` 无对应项） |
| `git add .` | 未发生（`git status` 仍全为 ` M` / `??`，无暂存区内容） |
| **KERT 是否被写** | **未写**。`find /home/szf/dev/Leibniz-KERT -newermt "2026-09-20 23:00" -type f` → **无输出**；KERT 最新 ONTO1 相关 mtime = `ONTOLOGY-SPLIT-DESIGN-V1.1-REVIEW.md` **16:28**，属**派工前既有事实**（已登记 `FAILURES.md` FAIL-2026-09-20-06 / `TL-DECISIONS D-7`） |
| **QA 自身**是否越权 | 未改任何仓内文件；所有变异实验仅在 `/tmp/qa15/**`；`--gate` 复跑为只读（已核：`wi-a3-reference-wording-registry.json` mtime 保持 **22:22:38**，未被我的 23:16 复跑触碰） |

### 5.2 诚实性检查

| 检查项 | 方法 | 结果 |
|---|---|---|
| 是否有 `fail` 被写成 `inconclusive`/`pass` | `EVIDENCE.json` 机读板状态直读 | ✅ 未发现：26 门禁 `{'pass':25,'fail':1}`，唯一 fail 如实记 `status=fail, exit=2` |
| `NOT_EVALUATED` 是否被包装为通过 | 复跑输出直读 | ✅ 未发现：`C-1b NOT_EVALUATED` 明写"**不得计为通过**"；`C-3` 空转显式声明"**不计为覆盖**" |
| 空转断言是否被算作覆盖 | `--selftest` 逐项 + 元变异 | ✅ 未发现：含 `M-元`（把 C-3 判定替换为恒 PASS ⇒ 证明 M4 真在测 C-3）、`M10`（全豁免假绿）、`M13`（未判定≠通过）；reference_alignment 有 `NOOP_SUSPECT_*` 三条空转下限（`:420-428`） |
| `PENDING_*` 是否非零 | `grep -rIno "PENDING_[A-Z_]*"` + 语义核对 | ✅ 实际数据 `pending_triage: 0`；14 处 `PENDING_TRIAGE` 全为**规则定义/文档陈述/历史失败登记文本**，无命中行（见 S-8） |
| 门禁型日志**孤儿** | `python3 scripts/onto1_evidence_board_check.py --gate` → **exit 0** | ✅ `orphan=0`、`registered evidence files present=26/26`；19 份白名单项**逐条带 reason**（`non-gate-log-allowlist.json:5-57`），规则本身写明"白名单是逃生口，逃生口必须可见" |
| 门禁证据文件是否真实存在 | 同上 E3 | ✅ 26/26 |
| 是否已签 `QA_PASS` | `EVIDENCE.json.independent_qa` | ✅ `status=pending, actor=None, session=None, evidence_sha256=None` ⇒ **无人代签**，符合本批次禁令 |

**诚实性发现（2 项，均须 TL 处置）**：

- **H-1（MINOR，可追溯性）**：`FAILURES.md` 存在**失败编号重复**，使"已登记"不可唯一回指：
  - `FAIL-2026-09-20-04` 出现在 `:55`（送审文书触发占位符红线）与 `:169`（证据板不自洽）；
  - `FAIL-2026-09-20-05` 出现在 `:71`（D2 包 G4 回源歧义）与 `:187`（C-4 误报）；
  - `FAIL-2026-09-20-06` 出现在 `:96`（WI-A3 首轮 42 命中）、`:119`（映射草案 R1 空转）、`:196`（KERT 写入）。
  建议重编为唯一序列（如 `-09`/`-10`/`-11`）并在 `NEXT_SESSION.md` B-7 引用处同步。
- **H-2（MAJOR，见 F-4）**：`FAILURES.md:162` 的 "`C-4` 转 PASS" 与其自身引用的两份日志（`142432:10`、`145542:13` 均为 `[C-4] FAIL`）不一致。**按 D-1 纪律须改为可复核的子项口径**（例如"C-4 的 4 个内容钉值项 PASS；C-4 整体仍 FAIL（自冻结 2 项）"），否则该条记录本身成为一处"板面与事实不符"。

**未计入通过、须携带的既有事实（如实转记，非本批次引入）**：`FAILURES.md:214` 声明 `make check` 内嵌 `gk-ke-gates` 就绪度 `22/23`，其中 `semantic-consumption = NOT_MET`、`gate-injection-tests = INCONCLUSIVE`——早于本 Loop，**不得计为通过**。

---

## 6. 阻塞 / 条件清单（可执行）

### 6.1 BLOCKER（阻断本批次"可审计"）

| # | 项 | 证据 | 解除动作（可执行） |
|---|---|---|---|
| **B-1** | **PKG-A1 零交付** | `ls scripts/onto1_obligation_triage.py` → exit 2 | pilot-a1 产出 `memory/waves/PKG-A1-{PLAN,ITER}.md` + 脚本 + `evidence/obligation-*` + `memory/handoffs/PKG-A1-HANDOFF.md`（含**登记建议**：gate id / command / pass_condition / 期望 exit） |
| **B-2** | **PKG-A2 未交回**（在飞） | 无 `evidence/wave0-readiness-*`、无 HANDOFF | 落 `PKG-A2-ITER.md` + `--gate`/`--precheck`/`--selftest` 真实执行记录 + HANDOFF |
| **B-3** | **PKG-A3 零交付** | 两脚本 mtime 22:23/22:24 < 派工 23:15 | pilot-a3 落 `memory/waves/PKG-A3-{PLAN,ITER}.md` + `evidence/a3fix-*`（前后对比） + HANDOFF |

> 三者解除后，按 `DISPATCH-W-1.5.md:40`（S-1）**由 TL 重新派 QA 复核**；本报告不构成对 B-1~B-3 的最终判定。

### 6.2 条件项（可执行；交回时必须一并满足，否则判 `ACCEPT_WITH_CONDITIONS` 以下）

| # | 条件 | 判据来源 | 验证命令/方法 |
|---|---|---|---|
| **C-1** | A3 改后 `wi_a4_namespace_collision --gate` **必须仍 exit=2**；若转 0 ⇒ **直接 `NOT_ACCEPTED`** | `DISPATCH-W-1.5.md:44`（S-3） | `python3 scripts/onto1_namespace_collision_check.py --gate; echo $?` ⇒ 期望 `2`；同时核 `[C-2] FAIL` 仍在 |
| **C-2** | 修 `EVIDENCE.md:74` 陈旧哈希（`310bb2306492a78c` → 实测 `45475058b3050fc1`）**或**删除该行的"独立冻结记录"声明 | 本报告 F-2 | `sha256sum evidence/consumer-scan-manifest.json` 与 `EVIDENCE.md:74` 比对 |
| **C-3** | 明确 `EVIDENCE.md` 是否属 C-4b 扫描根；若以"补冻结记录"实现 D-2，则记录**必须落在 `loops/ONTO1-ontology-split/evidence/` 之内** | 本报告 F-3（`:299` + `:282` rglob） | 改后 `--gate` 的 `C-4` 子项应显示对应 `freeze:*` PASS，或该项已被**显式**移出范围 |
| **C-4** | **D-2 收窄不得越界**：须新增"必需钉值 allow-list"断言——`specs/semantic/gits-core.owl.ttl`、`evidence/attribution-45-v2.csv`、`hits`、`summary` 任一缺失 ⇒ **FAIL**；并补变异"删必需钉值 ⇒ FAIL" | 本报告 §4.2 E3（MAJOR） | 复跑 E3：`--pins` 只留 1 项时必须 **FAIL**（当前为"内容层 0 失败"，即不合格） |
| **C-5** | A2 交回后，QA 须以**条目级变异**复验 `--precheck` **不会**放过 R1/R2（即：篡改 R1 → `--precheck` 也必须 `NOT_READY`）；且"删 R6/R7"或"`--gate`→`--precheck`"不被接受为变绿手段 | `PKG-A2-PLAN.md:44-45,63-69` | 在 A2 的 `--selftest` 输出中核对是否存在 **M1/M2a/M2b** 且断言到 `items["R1"]/items["R2"]` |
| **C-6** | A3 实现 D-3 时，`rule_statement` 放行**不得**退化为"`loops/**` 目录整体白名单"；须补反例变异："`loops/**` 内**不带否定标记**的真实符合性声称 ⇒ 必须 FAIL" | 本报告 §4.3 | 在 A3 的 `--selftest` 中核对新增变异名与断言 |
| **C-7** | 修 `onto1_namespace_collision_check.py` 头部**三处**自述（`:13` C-4 判据、`:34` 变异条数、`:35` 真实仓结果），不止 `:13` | 本报告 F-5 | 改后 `--gate`/`--selftest` 实测输出与头部逐字一致 |
| **C-8** | 履行 D-2 **过渡义务**：收窄实现前，门禁输出须**显式标注** C-4 两条为已知误报 | `TL-DECISIONS-W-1.md:40`；本报告 F-6 | `grep -n 误报 scripts/onto1_namespace_collision_check.py` 应 >0，或直接完成 C-3/C-4 使该项消失 |
| **C-9** | `FAILURES.md:162` 的 "C-4 转 PASS" 改为可复核子项口径 | 本报告 F-4 / H-2 / D-1 | 复核文字与 `wi_a4_namespace_collision-20260920T145542Z.log:13` 一致 |
| **C-10** | `FAILURES.md` 失败编号去重（04/05/06 各重复 2~3 次） | 本报告 H-1 | 全文件 ID 唯一，且 `NEXT_SESSION.md:96` 引用可唯一解析 |

---

## 7. 非声明

**本报告明确不主张以下任何一项：**

1. **不构成 `QA_PASS`**，也不构成 `DEV_SELF_CHECK_PASS`；`EVIDENCE.json.independent_qa` 保持 `pending / actor=null`（实测）。本 Loop 仍有已知 fail（`wi_a4_namespace_collision`，exit=2），`ready_for_independent_qa` 的硬约束（实现类门禁全 pass）未满足，**本批次无 QA_PASS 权限**（`W-1.5-ORCHESTRATION.md:20`、`:85`）。
2. **不覆盖 Wave 2 及以后**（本体拆分、消费入口切换、正式重钉、注册表/SKOS、国标条款级对齐），亦不覆盖 Wave 0 与 Wave 1。
3. **不覆盖三个 PKG 的实现质量**——本轮**无交付物可审**；§3.3 的 F-1~F-6 全部是**存量（派工前既有）**缺陷的实证，**不得**读作 pilot 交付的缺陷。
4. **未使用索引外推**：KERT 侧 `INDEX_STALE(144)`（`STATE.json:98`）未刷新，故**所有 KERT 结论均来自直接读取与 `文件:行`**，未使用 `.ua/` 派生视图；本报告不含任何 KERT 内部设计与依赖推断。
5. **未判定归属**：KERT 3 文件写入（`FAILURES.md` FAIL-2026-09-20-06）**归属未确认**，本报告仅复述"派工后（23:00 起）KERT 零写入"这一**可复现事实**，不推断历史写入者。
6. **未做性能/安全/依赖审计**（不在 W-1.5 scope）；`make check` / `make security-check` / `make index-status` 未由本 QA 执行（属 TL 记账项），本报告不代跑、不代记。
7. **未修改任何文件**：仅创建本文件；所有变异实验位于 `/tmp/qa15/**`，已核 `--gate` 复跑为只读。

---

## 8. 审计轨迹（供复核）

| 时刻(+0800) | 动作 | 结果 |
|---|---|---|
| 23:16 | 初次存在性扫描 | `memory/waves/` 仅 3 个既有文件 ⇒ 三包均未交付 |
| 23:16 | 复跑 6 个存量门禁 | exit 2 / 0 / 0 / 0 / 0 / 0（见 §3.3 表） |
| 23:16 | `/tmp` 变异实验 E1/E2/E3 | E3 暴露"收窄过度不可检出" |
| 23:17 | 复扫 | `PKG-A2-PLAN.md` **出现**（pilot-a2 开始落盘） |
| 23:18 | 复扫 | `scripts/onto1_wave0_readiness.py` **出现** |
| 23:19:09 | **最终快照** | A1 = 零交付；A2 = 在飞（PLAN + 脚本，无 ITER/HANDOFF/证据）；A3 = 零交付；KERT 零写入 |

**复现本报告的最小命令集**

```bash
# AU-1 存在性
ls scripts/onto1_obligation_triage.py scripts/onto1_wave0_readiness.py
ls loops/ONTO1-ontology-split/memory/waves/ loops/ONTO1-ontology-split/memory/handoffs/
ls loops/ONTO1-ontology-split/evidence/ | grep -E '^(obligation|wave0|a3fix|PKG-A)'
# AU-2 复跑（只读）
python3 scripts/onto1_namespace_collision_check.py --gate; echo $?              # 2
python3 scripts/onto1_namespace_collision_check.py --selftest; echo $?          # 0 (16/16)
python3 scripts/onto1_reference_alignment_check.py --gate; echo $?              # 0
python3 scripts/onto1_reference_alignment_check.py --selftest; echo $?          # 0 (10/10)
python3 scripts/onto1_evidence_board_check.py --gate; echo $?                   # 0 (orphan=0)
# AU-3 回源
awk 'NR==1' specs/semantic/gits-core.owl.ttl
awk 'NR==1||NR==10||NR==15' specs/knowledge-architecture/instances/product/products.ttl
awk 'NR==2' specs/data/customer-source-mapping.r2rml.ttl
awk 'NR==264||NR==272||NR==299' scripts/onto1_namespace_collision_check.py
sha256sum loops/ONTO1-ontology-split/evidence/consumer-scan-manifest.json   # 45475058… ≠ EVIDENCE.md:74 的 310bb230…
# AU-5 红线
git status --porcelain | grep -i onto1
find /home/szf/dev/Leibniz-KERT -path '*/.git' -prune -o -newermt '2026-09-20 23:00' -type f -print   # 空
```

---

*本报告由 `qa-w15` 独立完成，未采信任何 pilot 自述；所有结论均附命令 + exit + `文件:行`。*

---
---

# 第二轮复核（PKG-A3 交回后）

> §1~§8 为**首轮**（产物未就绪）记录，保留不动。本节为 `pilot-a3` 交回后的独立复核。索引：**第二轮结论见 §9.1**。

## 9. 第二轮：PKG-A3 独立复核

| 项 | 值 |
|---|---|
| 触发 | `pilot-a3` 交回通知（本 QA **未采信其自述**，逐项独立复算） |
| 审计快照 | `2026-09-20T15:28:20Z`（+0800 23:28:20） |
| 被审字节 | `scripts/onto1_namespace_collision_check.py` = **`ea67e4e9f10177b2…`**（审计期内已变动 3 次，见 §9.4）<br>`scripts/onto1_reference_alignment_check.py` = `6e774460c5571ce3…`（= HANDOFF 声明值，**未变**）<br>`memory/handoffs/PKG-A3-HANDOFF.md` = `04f2edb56e260e8b…` |
| A1 / A2 状态 | A1 = **仍在飞**（无 `PKG-A1-HANDOFF.md`，暂不判）；A2 = 已交回且 TL 已出 `TL-AUDIT-W15-PKG-A2.md`（本 QA 仅做轻量复核，见 §9.5） |

### 9.1 结论：`NOT_ACCEPTED`

**PKG-A3 = `NOT_ACCEPTED`**，理由 3 条 BLOCKER + 1 条 MAJOR（均附可复现命令）：

| # | 级别 | 一句话 |
|---|---|---|
| **Q-1** | **BLOCKER** | D-3 的 `rule_statement` 放行可被**真实符合性声称**利用 ⇒ A3 **新引入**一条漏检通道（实证 X3） |
| **Q-2** | **BLOCKER** | **交付集合不自洽**：HANDOFF 声明哈希 `32130eea…` ≠ 审计时磁盘 `ea67e4e9…`；`a3fix-after-*.log`（23:25）产自旧字节 ⇒ 证据链与制品脱钩 |
| **Q-3** | **BLOCKER** | 审计期内**观测到 `--selftest` 未捕获异常**（`FileNotFoundError`，exit=1）⇒ 所交付状态曾不能通过自身门禁 |
| **Q-4** | **MAJOR** | `section_heading_negation` 单字 `禁` 子串匹配（R-1）⇒ 标题含"门禁"的文书放行其下真实声称（实证 X4/X5）；A3 已**如实登记**且声明不擅改（行为变更需 TL 裁定）⇒ 保留为**待裁项**，不得静默 |

**另一面（必须并列声明，避免只记缺陷）**：A3 对**首轮条件 C-1/C-3/C-4/C-8** 的落实是**真实且可复现的**（§9.3 逐条）。

### 9.2 AU-1~AU-5 执行结果（命令 + exit）

| 动作 | 结果 |
|---|---|
| **AU-1** 哈希 | **审计开始时 9/9 一致**（`32130eea…`/`6e774460…`/`b9c9717c…`/`5e28fa64…`/`e64c2a5e…`/`a87e829b…`/`30ecf84d…`/`c8c72577…`/`c173be93…` 与 HANDOFF §1 **逐字相符**）；**随后失效**：`onto1_namespace_collision_check.py` 于 23:28 起被继续改写（32130eea → 37d1b149 → ea67e4e9）⇒ 见 Q-2 |
| **AU-2** 复跑 | 对 `32130eea` 版本：`--gate` **exit=2**（失败项**仅 C-2 ×2**）；`--selftest` **exit=0 / 19 项**；`reference --gate` **exit=0**（`allowed[rule_statement]=0`，`allowed_by_reason={ancestor_key_negation:1, same_line_negation:58, section_heading_negation:2, table_row_negation:9}`）；`reference --selftest` **exit=0 / 12/12** —— **与 HANDOFF §2 四项声明全部一致**，且 `evidence/a3fix-after-wi_a4_namespace_collision-gate.log` 与我的复跑输出**逐行一致** ✓<br>对 `37d1b149` 版本：`--gate` **exit=2**（仍仅 C-2）✓ 但 `--selftest` **exit=1 + Traceback**（Q-3） |
| **AU-3** 回源 | 见 §9.6 表（9 条，8 成立 / 1 不成立） |
| **AU-4** 变异 | **E3-redo**（删掉唯一受控钉值）⇒ `C-4_REQUIRED_PIN_MISSING` + `C-4_NO_CONTROLLED_PIN` FAIL ✓（首轮"收窄过度不可检出"的缺口**已补**）；**X2/X5**（真实声称）⇒ `CONTENT_WORDING_UNALLOWED` ✓；**X3/X4** ⇒ 声称被放行 ✗（Q-1/Q-4） |
| **AU-5** 红线 | 见 §9.7 |

### 9.3 首轮条件的关闭情况（逐条）

| 首轮条件 | 状态 | 证据 |
|---|---|---|
| C-1「A3 改后 `--gate` 必须仍 exit=2」 | ✅ **满足** | `--gate` exit=2，失败项仅 `C-2`；`[C-2] FAIL（实测 2 / 登记 2 / 未登记 0 / 陈旧 0）` |
| C-2「修 `EVIDENCE.md` 陈旧哈希」 | ✅ **关闭（TL 执行）** | `EVIDENCE.md:88` 已改为「**重新生成的工具产物，不是钉值文件**…不得在此登记『冻结哈希』」；TL 另记 `FAILURES.md` `FAIL-2026-09-20-W15TL-02` |
| C-3「冻结记录是否在扫描根内」 | ✅ **由 TL 以 `FAIL-2026-09-20-W15TL-03` 记账** | 新版门禁输出显式打印「冻结记录扫描根（作用域声明；根外的记录不可见）：`loops/ONTO1-ontology-split/evidence`」 |
| C-4「必需钉值 allow-list；删必需钉值 ⇒ FAIL」 | ✅ **满足（超出要求）** | `--gate` 打印「必需钉值 allow-list **4/4**」；我的 E3-redo 反例得 `C-4_REQUIRED_PIN_MISSING 必需钉值未出现在声明集合中（D-2 收窄不得减必需钉值）：specs/semantic/gits-core.owl.ttl` |
| C-5「A2 `--precheck` 不放过 R1/R2」 | ✅ **验证为真** | `onto1_wave0_readiness.py:416-417` `precheck_pass = all(... if key not in EXTERNAL_HELD_ITEMS)` ⇒ 仅排除 R6/R7，R1/R2 **在内**；`EXTERNAL_HELD_ITEMS` 语义见 `:58`；selftest 含 **M1**（篡改复审包 01 ⇒ `R1 NOT_READY`）与 **M4b**（`NOT_READY` 恰为 `['R6','R7']`）⇒ 反例**未成立**（A2 无此缺陷） |
| C-6「D-3 不得退化为 `loops/**` 白名单；须补反例变异」 | ⚠️ **半满足** | 未用目录白名单 ✓（`META_STATEMENT_MARKERS` 逐关键词，`:107-114`；注释 `:106` 明写不采用该做法）；**但未补**"真实声称**含**元陈述关键词 ⇒ 必须 FAIL"的变异 ⇒ 正是 Q-1 未被拦住的原因。`--selftest` 的 M11 只覆盖"**不含**关键词的真实声称"（`:690-691`、夹具 `:569-573`） |
| C-7「头部三处自述与实测一致」 | ⚠️ **半满足** | `:13` C-4 判据已改（**F2 修复** ✓）；`:35` 真实仓由 `INCOMPLETE` 改为 `FAIL` ✓；**但计数仍不一致**：`32130eea` 版 `:50` 写「**16 条变异 + 2 条对照**」，实跑 **19 项 = 16 变异 + 3 对照**（多出 `M12 对照`）；`a3fix-00-BEFORE-AFTER.md:42` 的枚举「M0~M14 + M13b + M-元 + M0b」同样漏列 `M12 对照`。新版 `:63` 改称「19 条变异 + 4 条对照」——与实跑口径**又不同**，须以实跑为准统一 |
| C-8「D-2 过渡义务：显式标注已知误报」 | ✅ **关闭** | 新版输出逐条打印「载体自冻结豁免（D-2 清单类产物；**原 `FAIL-2026-09-20-05` 的 `C-4_PIN_FILE_UNFROZEN` 已知误报项**）」×2 |
| C-9「`FAILURES.md:162`『C-4 转 PASS』改口径」 | ✅ **关闭（TL 执行）** | `FAILURES.md:191` 增 ⚠️**TL 更正（由 `qa-w15` F-4 触发）**，给出可复核子项口径「`C-4a` = PASS；`C-4b` = FAIL；门禁整体 FAIL」并回源两份日志行号 |
| C-10「`FAILURES.md` 编号去重」 | ⚠️ **半满足** | 已加**去重引用别名**（`FAIL-2026-09-20-W15INT-01/02/03`、`W15A2-01` 等）；**但标题编号仍重复**：`FAIL-2026-09-20-04`（`:83`,`:200`）、`-05`（`:99`,`:218`）、`-06`（`:124`,`:147`,`:227`）、`-07`（`:169`,`:243`） |

### 9.4 审计期内制品变动（可审计性）

```
$ ls -la --time-style=full-iso scripts/onto1_namespace_collision_check.py
-rw-rw-r-- 1 szf szf 59738 2026-09-20 23:28:00 scripts/onto1_namespace_collision_check.py
$ sha256sum scripts/onto1_namespace_collision_check.py
23:26 → 32130eeafec51badd7767ac4b8e115a8b3d47983ab8ef01cfea713cba07540d5   （= HANDOFF 声明值）
23:28:07 → 37d1b1495ceb70fab1a95ed37501b0c854e5990f508c30311d128ca4af22e75e
23:28:20 → ea67e4e9f10177b2c1471ab7fc9594d0fab126995ccc65bdef9b208413d050e5
```
`memory/handoffs/PKG-A3-HANDOFF.md`（23:25:42）与 `evidence/a3fix-*`（23:24~23:25）**早于全部后续改动** ⇒ 其声明的哈希与日志**均不对应审计时字节**。
**不作动机推断**（推测为 A3 在收到首轮/自身发现后继续迭代）。但按仓规「**未落盘 = 不存在**」与 AU-1 判据，**交付集合自洽性**是审计前置条件，故 Q-2 成立。
另：`LOOP.yaml`/`EVIDENCE.json`/`TL-DECISIONS-W-1.md`/`NEXT_SESSION.md` 在同窗口（23:22）被写，**已确认为 TL 所写**——`TL-DECISIONS-W-1.md` 新增 **D-9**（`wi_a2_wave0_readiness` 不登记为 Loop 门禁）与 **D-10**（接受 PKG-A2 偏离），并出现 `memory/handoffs/TL-AUDIT-W15-PKG-A2.md`（23:22:28）⇒ 与 A3 的 23:24 起产物**时序可区分**，**无证据表明 A3 越权写 TL 文件**。

### 9.5 A2 轻量复核（A2 不在本轮 FAIL 清单内）

```
$ python3 scripts/onto1_wave0_readiness.py --gate      → exit=2  （R6/R7 NOT_READY，其余 6 项 READY）
$ python3 scripts/onto1_wave0_readiness.py --precheck  → exit=0  （除 R6/R7 全 READY）
$ python3 scripts/onto1_wave0_readiness.py --selftest  → exit=0  （M4/M4b/M1/M2a/M2b/M3a/M3b/M3c/M3d/M5/M6×6 全 PASS）
```
其中 **M3a+M3b+M3c 三条合起来**证明 R6/R7 各自有牙齿（单改任一项都不变绿，两项齐备才 `--gate` PASS）——正是首轮 §4.1 要求的"条目级变异"，**A2 做到了**。**未发现**"R6/R7 被做成可跳过"或"`--precheck` 放过 R1/R2"。

### 9.6 回源抽样明细表（AU-3，9 条）

| # | 层 | 结论 | 回源 | 实测 | 判定 |
|---|---|---|---|---|---|
| T-1 | 强 | F2 已修：C-4 头部判据不再写"PASS" | `onto1_namespace_collision_check.py:13` | `**可判定；钉值漂移 / 受控载体未冻结 / 范围未裁决 ⇒ FAIL**` | ✅ |
| T-2 | 强 | D-2 收窄范围由集中常量定义 | 同 `:114-133` | `CONTROLLED_PIN_PREFIXES=(specs/semantic/, specs/CONTRACT_INDEX.yaml)`；`CONTROLLED_PIN_SUFFIXES=(/90_control/schema/ontology_reference.json, /90_control/ontology/PROVENANCE.json)`；`LIST_ARTIFACT_PREFIXES=(…)` | ✅ 与 D-2 四项列举**逐条对应** |
| T-3 | 强 | `rule_statement` 必须是"行级、最后判定" | 同 `:228-245` | `same_line_negation`→`table_row_negation`→`section_heading_negation`→`ancestor_key_negation`→`rule_statement`（**最后**，作用面=`line`） | ✅ 排序正确（但这恰是 Q-1 的载体） |
| T-4 | 强 | 元陈述关键词是**子串**匹配 | `onto1_reference_alignment_check.py:107-114` + `:243` | `"词表"` 等 6 词；判定 `if any(m in line for m in META_STATEMENT_MARKERS)` | ✅（**成因**，见 X3） |
| T-5 | 中 | R-1 成因：`禁` 为单字标记 | 同 `:87-96` | `NEG_MARKERS` 首位即 `"禁"`；标题判定 `:207` `any(m in lines[j] …)` | ✅（**成因**，见 X4） |
| T-6 | 中 | C-4 新增 fail-closed 面 | `onto1_namespace_collision_check.py:412,429` | `C-4_PIN_SCOPE_UNCLASSIFIED` / `C-4_NO_CONTROLLED_PIN` 落 `failures` | ✅ |
| T-7 | 中 | M12 已按 D-2 口径调整且**保留**、并加 restore 对照 | 同 `:914,922` | `M12 对照：补独立冻结记录 ⇒ PASS（restore ⇒ PASS）` | ✅ 未删除断言 |
| T-8 | 弱 | A2 `--precheck` 语义只排除 R6/R7 | `onto1_wave0_readiness.py:416-417` | `if key not in EXTERNAL_HELD_ITEMS` | ✅ |
| T-9 | 弱 | `EVIDENCE.md` 首轮陈旧哈希已纠正 | `EVIDENCE.md:88` | 「…不是钉值文件…不得在此登记『冻结哈希』（登记即陈旧：见 FAILURES.md FAIL-2026-09-20-W15TL-01/02）」 | ✅ |

**AU-3 结论**：9 条 **全部成立**（T-4/T-5 为"成因类"回源，用于定位 Q-1/Q-4）。较首轮（8/9）改善。

### 9.7 反例构造结果（QA 本职；全部在 `/tmp` 内，未动仓内任何文件）

端到端驱动：`/tmp/qa15/refrun.py`（以 `--root /tmp/qa15/ref` 指向自建夹具，并显式传入仓内 `--registry/--skeleton/--matrix/--status`；`--min-files 1 --min-candidates 1 --min-allowed 0`）。
> **读数说明**：各例均含 15 条 `REGISTRY_ENTRY_MISSING` / `NOOP_SUSPECT_LOW_CANDIDATES`，那是**我的夹具根**不含仓内注册表所列文件所致的**夹具噪声**，与本判定无关；判据只看 **`CONTENT_WORDING_UNALLOWED` 是否出现** 与 **`allowed_by_reason`**。

| 例 | 夹具内容 | 探针结果 | 判定 |
|---|---|---|---|
| **X1** 清洁对照 | 仅内部规范，无 GB 声称 | 无 `CONTENT_WORDING_UNALLOWED` | 对照基线 ✓ |
| **X2** 真实声称 | `本设计符合 GB/T 48000.3-2026 的全部要求。` | **有** `CONTENT_WORDING_UNALLOWED`，`allowed_by_reason={}` | 守卫有效 ✓ |
| **X3** 真实声称 + 元陈述关键词 | `本设计符合 GB/T 48000.3-2026 的全部要求，术语按词表统一。` | **无** `CONTENT_WORDING_UNALLOWED`；`allowed_by_reason={'rule_statement': 1}` | ❌ **Q-1 BLOCKER 成立** |
| **X4** 真实声称 + 标题含"禁" | 标题 `# 门禁规则说明` + 同上真实声称 | **无** `CONTENT_WORDING_UNALLOWED`；`allowed_by_reason={'section_heading_negation': 1}` | ❌ **Q-4 MAJOR 成立（R-1 独立复现）** |
| **X5** X4 对照（标题无"禁"） | 标题 `# 规则说明` + 同一真实声称 | **有** `CONTENT_WORDING_UNALLOWED` | 反例**已被隔离到标题子串** ✓ |

**E3-redo（首轮反例的复验）**：删掉唯一受控钉值 ⇒ `C-4_REQUIRED_PIN_MISSING` + `C-4_NO_CONTROLLED_PIN` 双 FAIL ⇒ **首轮 C-4 缺口已封闭** ✓。

**Q-1 的成因（回源到行）**：`META_STATEMENT_MARKERS` 含 `"词表"` 这类**主题词**（`:107-114`），而放行判定是**纯子串**（`:243`）；`truth()` 对 `gb_scope` 文件里的命中行调用它（`:397` 附近）⇒ **一句真实声称只要顺带提到"词表/变异/注入"即被当作"规则陈述行"放行**。
**A3 对此的防护缺口**：`--selftest` 的 M10（正向，`_mutate_add_rule_statement`）与 M11（反向，`_mutate_claim_adjacent_to_rule_statement`）**都不覆盖"声称行自身含关键词"**（`:688-691`）。⇒ 断言集合存在**盲区**，与 GK 系列"假绿"同源。
**建议最小修复**（不改变 D-3 主旨，不属于"删规则"）：① 放行前要求该行**同时**不含正向声称动词（`符合`/`满足`/`达到`/`已通过`），或 ② 要求 ≥2 个**不同**元陈述关键词，或 ③ 把 `"词表"` 等宽词收紧为 `"禁用词表"`/`"词表本身的引用"` 形态，或 ④ 要求元陈述放行**必须与判定语义共现**（`FAIL`/`放行`/`判定`）；并**补一条变异**：`真实声称行内含单个元陈述关键词 ⇒ 必须 FAIL`。

### 9.8 红线与诚实性（AU-5）

| 判据 | 结果 |
|---|---|
| A3 写域外是否被改 | **未发现**。A3 实际写入：2 个脚本 + `evidence/a3fix-*`(5) + `memory/waves/PKG-A3-{PLAN,ITER}.md` + `memory/handoffs/PKG-A3-HANDOFF.md`，**全部落在** `DISPATCH-W-1.5.md:17` 与 `onto1_pkg_audit.py` `SCOPES["PKG-A3"]` 之内 |
| TL 单写者文件 | 23:22~23:27 的写入**归属 TL**（`TL-DECISIONS-W-1.md` 新增 D-9/D-10；`TL-AUDIT-W15-PKG-A2.md` 同窗口）⇒ **无 A3 越权证据** |
| `specs/**` / `generated/**` / `docs/dd/**` | `find specs generated docs/dd -newermt "2026-09-20 23:20" -type f` → **空** ✓ |
| 他人交付物 | `baseline-v2-manifest.json`(22:53:44)、`consumer-scan-manifest.json`(22:53:45)、`non-gate-log-allowlist.json`(22:58:37) mtime **均未被 A3 触碰** ✓；哈希仍为 `cac187a7624247a2` / `45475058b3050fc1` ✓ |
| **KERT** | `find /home/szf/dev/Leibniz-KERT -newermt "2026-09-20 23:20" -type f` → **空** ⇒ **零写入** ✓ |
| `git add .` | 未发生（`git status --porcelain` 无暂存项）✓ |
| 断言是否被删除/弱化 | **未删除**：`--selftest` 16 → **19** 项（新增 M13/M13b，原 M13 顺延 M14，M12 调整后**保留**并加 restore 对照）；`reference --selftest` 10 → **12/12** ✓ |
| `fail` 是否被改写为 `inconclusive` | **未发现**：`--gate` exit=2 且 `C-2` 真实 FAIL 原样保留；`EVIDENCE.json` = 28 门禁 / **27 pass / 1 fail**，唯一 fail = `wi_a4_namespace_collision` ✓ |
| 空转是否被计为覆盖 | **未发现**：C-4 载体自冻结空转**逐次显式声明**「受控载体 0 个，**空转不计为覆盖**」；C-3 空转照旧声明 ✓ |
| 真实仓计数是否被冒充为覆盖 | **未发现**：`allowed[rule_statement]=0` 由 `a3fix-00-BEFORE-AFTER.md:66-68` **主动声明**"不是靠真实仓计数冒充"，改由 M10 证明 ✓（**诚实**） |
| 证据板孤儿 | `python3 scripts/onto1_evidence_board_check.py --gate` → exit=0，`gates=28`，`orphan=0`，`registered evidence files present=28/28` ✓ |
| `independent_qa` | `EVIDENCE.json.independent_qa` = `status=pending, actor=null` ⇒ **无人代签** ✓ |
| **新增诚实性问题** | **H-3（MAJOR，即 Q-2）**：HANDOFF/日志与磁盘字节脱钩（§9.4）。**H-4（MINOR，即 C-7 残差）**：头部/对照文档的变异-对照计数与实跑不一致（2 vs 3 对照；枚举漏列 `M12 对照`）。**H-5（MAJOR，即 Q-3）**：`--selftest` 在 `37d1b149` 上以未捕获异常退出 1 —— 若该状态被记为"selftest 通过"即构成假绿；本轮**未观察到**此类记账（板面 `wi_a4_namespace_collision_selftest` 仍为旧 `pass`，属**陈旧证据**，须在冻结后重记） |

### 9.9 条件清单（交回并**冻结**后须逐条满足）

| # | 条件 | 验证方法 |
|---|---|---|
| **N-1** | 关闭 Q-1：`rule_statement` 放行**不得**被真实声称利用；按 §9.7 末段任一方案收紧，并**新增变异**「真实声称行内含单个元陈述关键词 ⇒ 必须 FAIL」 | `reference --selftest` 报告中出现该新用例且 expect=FAIL；再复跑 X3 ⇒ 必须出现 `CONTENT_WORDING_UNALLOWED` |
| **N-2** | 让交付集合自洽：**冻结**脚本（停止改动）→ 重跑全部 4 个门禁 → 重生成 `a3fix-after-*` 与 HANDOFF 哈希表，使「声明的哈希 == 磁盘」且「日志 == 当前字节」 | `sha256sum` 三项与 HANDOFF §1 逐字一致；`diff <(复跑输出) <(日志)` 为空（忽略首行 `COMMAND=`） |
| **N-3** | 修 `--selftest` 异常：`M12 对照` 的夹具 `specs/semantic/pins.json` 在哈希前**未创建**（`Traceback … line 934 → sha256(m12b_pins)`），须先写后哈希，并确保全程 exit=0 | `--selftest` **exit=0**、无 Traceback、用例数自洽 |
| **N-4** | 统一计数口径：头部/`a3fix-00-BEFORE-AFTER.md` 的"变异/对照"条数 == `--selftest` 实跑条数（现为 16 变异 + 3 对照 = 19 项；`37d1b149` 版自称「19 变异 + 4 对照」与实跑不符） | 逐字比对头部行、文档表、实跑输出三者 |
| **N-5** | R-1（`禁` 子串）**要么修**（词级匹配）**要么由 TL 书面裁定"接受该残余"**并登记责任人/期限；不得以"不在本包范围"结案 | TL 裁定落 `TL-DECISIONS-*`；或改后 `--selftest` 增"标题含`门禁`不放行其下声称"用例且真实仓 `section_heading_negation` 计数变化被复核 |
| **N-6** | 冻结后由 TL 重新 `record_gate.py` 记账（QA 不代记），并把 `wi_a4_namespace_collision_selftest` 的**陈旧证据**刷新 | `EVIDENCE.json` 中该门禁证据哈希 == 冻结后重跑产物 |

### 9.10 非声明（第二轮）

1. **不构成 `QA_PASS`**：`independent_qa` 保持 `pending/actor=null`（实测）；本 Loop 仍有已知 fail（`wi_a4_namespace_collision`，exit=2），`ready_for_independent_qa` 硬约束未满足，**本批次无 QA_PASS 权限**。
2. **不覆盖** Wave 0/1/2+；不评 A1（仍在飞，无可审对象）；A2 仅**轻量复核**（§9.5），未按 AU-1~AU-7 全量审计（其 HANDOFF/TL 审计另行存在）。
3. **本报告绑定字节**：结论对应 §9 表头所列哈希。因制品在审计期内持续变动，**Q-2 本身即是结论的一部分**——若 A3 随后冻结并重交，须按 N-1~N-6 重跑，**不得以本报告或首轮报告替代**。
4. **不推断动机**：Q-2/Q-3 只陈述可复现事实（哈希/时间/异常），不对"为何未冻结"作归因。
5. **未使用索引外推**：KERT 侧 `INDEX_STALE(144)` 未刷新，所有 KERT 结论来自直接读取与 `文件:行`。
6. **未修改任何文件**：本轮仅追加本报告；全部反例夹具与驱动脚本位于 `/tmp/qa15/**`（`refrun.py`、`pins-*.json`）。
7. **框架性说明**：§9.7 中 `REGISTRY_ENTRY_MISSING` / `NOOP_SUSPECT_LOW_CANDIDATES` 系我在 `/tmp` 自建根扫描时**不携带仓内注册表所列文件**的夹具噪声，已按此读数口径排除；本报告不据此对守卫作任何判定。

### 9.11 最终快照复验（`2026-09-20T15:29:06Z`，**本节修正 §9.1 的 Q-3 状态**）

审计期间制品持续变动，为免结论失焦，在**最新字节**上重做关键判定：

| 制品 | 审计期哈希轨迹（`sha256sum`） | 与 HANDOFF 的关系 |
|---|---|---|
| `onto1_namespace_collision_check.py` | `32130eea…`(23:22) → `37d1b149…`(23:28:07) → `ea67e4e9…`(23:28:20) → **`c5f7b6717f57c662…`(23:29:00)** | **不一致**（HANDOFF 声明 `32130eea…`） |
| `onto1_reference_alignment_check.py` | `6e774460…`(23:23) → **`f6ef74f3767289b5…`(23:28:39)** | **不一致**（HANDOFF 声明 `6e774460…`） |
| `memory/handoffs/PKG-A3-HANDOFF.md` | `04f2edb56e260e8b…`（23:25:42 后**未再更新**） | — |
| `evidence/a3fix-*.{md,log}` | 23:24:35 ~ 23:25:16 后**未再更新** | **陈旧**（对应 23:25 之前的字节） |

**Q-3 状态修正**：`--selftest` 的 `FileNotFoundError`（`M12 对照` 夹具 `pins.json` 未先创建）**仅存在于 `37d1b149`**；在最新 `c5f7b671` 上 `--selftest` 已 **exit=0**（含新增 `M15 删除必需钉值（范围外/消费命中）⇒ C-4_REQUIRED_PIN_MISSING FAIL（**QA 反例 E3**）`、`M15 对照 restore⇒PASS`、`M15b 删除受控必需钉值 ⇒ FAIL`）。⇒ **Q-3 由 BLOCKER 降级为"历史观测（已消除）"**，但**保留为 Q-2 的佐证**：它证明"交付时点存在不能自洽的中间态"，而 HANDOFF 与日志并未随之更新。
**Q-1 / Q-4 在最新字节上仍成立**：`f6ef74f3767289b5…` 上复跑 X3 ⇒ 仍 `allowed_by_reason={'rule_statement': 1}` 且**无** `CONTENT_WORDING_UNALLOWED`；X4 ⇒ 仍 `allowed_by_reason={'section_heading_negation': 1}`。
**对 A3 的正面认定（须并列记录）**：新增的 `reference --selftest` **M12「`loops/**` 内的真实声称（不是目录白名单）⇒ 仍 FAIL」**（13/13，exit=0）正面回应了首轮 C-6 的一半；`collision --selftest` 的 `M15/M15b` 明确标注依据"**QA 反例 E3**"，即**首轮 C-4 条件已被采纳并固化为变异**。
**最终判定不变**：**PKG-A3 = `NOT_ACCEPTED`** —— 未闭合项 = **Q-1（BLOCKER，`rule_statement` 可被真实声称利用）**、**Q-2（BLOCKER，交付集合不自洽／未冻结）**、**Q-4（MAJOR，R-1 待裁）**；闭合项 = Q-3（历史）/ C-1 / C-2 / C-3 / C-4 / C-5 / C-8 / C-9。解除条件见 §9.9（N-1~N-6），其中 **N-2「先冻结再重交」是复验的前置**。

---

# 第三轮：TL 裁定受理、重定级，与 PKG-A1 / PKG-A2 独立复核

## 10. 快照纪律（按 TL §五 要求执行）

**快照时刻 `2026-09-20T15:29:52Z`（+0800 23:29:52）**，逐文件 `sha256 + mtime`：

| 文件 | sha256(前16) | mtime(+0800) |
|---|---|---|
| `scripts/onto1_namespace_collision_check.py` | `c5f7b6717f57c662` | 23:29:00 |
| `scripts/onto1_reference_alignment_check.py` | `f6ef74f3767289b5` | 23:28:39 |
| `scripts/onto1_wave0_readiness.py` | `285bada36ca55de5` | 23:18:42 |
| `scripts/onto1_obligation_triage.py` | `1982a9ec2017df97` | 23:26:36 |
| `memory/handoffs/PKG-A1-HANDOFF.md` | `4a9f0ceb34a8b1ac` | 23:28:10 |
| `memory/handoffs/PKG-A2-HANDOFF.md` | `e7dbe872d65e5d63` | 23:19:30 |
| `memory/handoffs/PKG-A3-HANDOFF.md` | `04f2edb56e260e8b` | 23:25:42 |
| `evidence/obligation-triage.csv` | `81e5ebc414df576c` | 23:28:04 |
| `evidence/obligation-triage-summary.json` | `325910baeac0a402` | 23:28:04 |
| `evidence/PKG-A1-义务收敛报告.md` | `89428f094a2af351` | 23:28:04 |
| `evidence/wave0-readiness-20260920T1520Z.log` | `4d67e70be5ec1e4b` | 23:19 |

**在飞标注（按 TL §五.2，不判缺陷，给出前后哈希）**：
- `onto1_namespace_collision_check.py`：`32130eea…`(23:22) → `37d1b149…`(23:28:07) → `ea67e4e9…`(23:28:20) → **`c5f7b671…`(23:29:00，已稳定)** ⇒ **在飞**
- `onto1_reference_alignment_check.py`：`6e774460…`(23:23) → **`f6ef74f3767289b5…`(23:28:39，已稳定)** ⇒ **在飞**
- `PKG-A3-HANDOFF.md`：**未随脚本更新**（仍为 23:25:42 的 `04f2edb5…`）

## 11. TL 裁定受理与重定级

**一致（无异议）**：F-2、F-3、F-4、H-1 我已独立复核你的处置并确认有效——
- F-2：`EVIDENCE.md:88` 已改为「不是钉值文件…不得在此登记『冻结哈希』（登记即陈旧：见 `FAILURES.md` FAIL-2026-09-20-W15TL-01/02）」✓
- F-4：`FAILURES.md:191` 的 ⚠️**TL 更正**给出可复核子项口径（`C-4a` PASS / `C-4b` FAIL / 整体 FAIL）并回源两份日志行号 ✓
- H-1：去重引用别名（`W15INT-01/02/03`、`W15A2-01`、`W15TL-0x`）+ 顶部「编号登记与去重规则」表已落 ✓（标题编号仍重复，但历史不改+别名可解析，我接受该取舍）

**接受你的重定级**：

| 我原判 | 你的裁定 | 我的处理 |
|---|---|---|
| F-1 / F-5 `:13` | 快照与 A3 编辑窗口重叠 ⇒ 不计入 A3 | **接受**。补充说明：这两条在**首轮**即被登记为"**存量**缺陷（非 pilot 之过）"，第二轮 §9.3 也**已记为已满足**（T-1）⇒ 我方从未把它们计入对 A3 的判负，口径一致 |
| **Q-2**（交付集合不自洽） | 在飞 ⇒ 不判缺陷 | **接受并重定级为「在飞」**（前后哈希见 §10）。但**保留为 N-2 重交前置**：交付包的 `HANDOFF 哈希 == 冻结字节` 是 AU-1 的定义，不是缺陷判定 |
| **Q-3**（selftest 崩溃） | 在飞 | **接受**（我此前已降级为历史观测：`37d1b149` 崩溃 → `c5f7b671` 已 exit=0） |
| **B-2**（A2 在飞） | 已交回并通过 TL 审计 | **接受**；我另出独立复核（§12.2），结论与你的 `ACCEPT_WITH_CONDITIONS` 一致 |

**⚠️ 未被你裁定的两项（我不能默认关闭，须显式提请）**：

| # | 项 | 状态 | 说明 |
|---|---|---|---|
| **Q-1** | `rule_statement` 放行可被**真实符合性声称**利用 | **TL 未回应** | 在**当前冻结字节 `f6ef74f3767289b5`** 上**仍复现**（本轮 15:29:52 复跑）：X2 有 `CONTENT_WORDING_UNALLOWED`；**X3（真实声称 + 「，术语按词表统一。」）无该 finding、`allowed_by_reason={'rule_statement':1}`**。成因已回源：`META_STATEMENT_MARKERS`(`:107-114`) 含 `"词表"` 等主题词 + 纯子串判定(`:243`)。⇒ 这是**红线守卫上的新漏检通道**，若不裁定，它会以"已交付、门禁绿"的形态静默留存（正是 GK 系列的头号教训）。**版本稳健性**：X3 在 `6e774460`(23:23) / `f6ef74f3767289b5`(23:28:39) / **`9f6267ca15545408`(23:31:24 最新)** 三个版本上**均复现** ⇒ 排除"测了旧版本"的抗辩 |
| **Q-4** | R-1（单字 `"禁"` 子串放行） | **TL 未裁定** | X4/X5 已独立复现（§9.7）。A3 已如实登记并声明"行为变更需 TL 裁定"⇒ 请裁定「修（词级匹配）」或「书面接受该残余 + 登记责任/期限」 |

> 说明：我在第二轮把 Q-1 定为 **BLOCKER** 的依据是**首轮预先登记的判据**（§4.3：「检查 F3 的 `rule_statement` 放行是否可被真实符合性声称利用（若可 ⇒ BLOCKER）」）。若你更倾向将其定为"可审计的精度上限"（因放行**留计数**、且 M11 已测'不含关键词'），请**出具裁定文本**——但请注意：**计数只在有人去看时才有用**，而该通道的触发条件（提到"词表"）在本仓语境下**极易无心触发**，故我保留 BLOCKER 评级直到有裁定。

## 12. PKG-A1 / PKG-A2 独立复核（本 QA 自算，不采信 TL 报告）

### 12.1 PKG-A1 — 结论 **`ACCEPT_WITH_CONDITIONS`**

| 动作 | 命令 | 结果 |
|---|---|---|
| **AU-1** | `sha256sum scripts/onto1_obligation_triage.py evidence/obligation-triage.csv evidence/obligation-triage-summary.json evidence/PKG-A1-义务收敛报告.md` | **4/4 与 HANDOFF 声明逐字一致**（`1982a9ec…`/`81e5ebc4…`/`325910ba…`/`89428f09…`）✓ |
| **AU-2** | `--gate` / `--selftest` | **exit=0 / exit=0（11/11）**，与 HANDOFF 一致 ✓（**未**执行 `--report`，以免改写哈希） |
| **AU-3a** | 独立复算 CSV（`csv.DictReader`）+ 与 `summary.json` 对账 | **1052 行**；`TRUE=626 / HOMONYM=0 / NEEDS=426`，**和=1052** ✓；`tier = STRONG 626 / MEDIUM 329 / WEAK 97` ✓；`true_by_wave = W2_SPLIT 291 / W3_CONSUMER_SWITCH 316 / W3_KERT_ASSETS 19` **与 summary 完全一致** ✓；`alternatives = {97, 329}` ✓ ⇒ **算术全部可复现** |
| **AU-3b** | 独立复算 P0 声明 | rationale 含"P0"且 `disposition=NEEDS_SOURCE_CHECK` 共 **65 行**，按包 `com.gien.gits.ontology` **55** / `.ontology.domain` **4** / `.action.domain` **6** ⇒ **与 HANDOFF 的 65 = 55+6+4 逐数一致** ✓（另有 3 行 `TRUE_OBLIGATION` 也出现该串，属我初筛口径差异，HANDOFF 无误） |
| **AU-3c** | **全量**回源核对 626 条 `TRUE_OBLIGATION` 的 `evidence` 列 | `626/626` 行号在范围内 ✓；但 **104 行（16.6%）的 `evidence` 行内不含 rationale 所命名的术语** ⇒ **见下方 MAJOR** |
| **AU-5** | `git status --porcelain` + mtime | A1 只写 `scripts/onto1_obligation_triage.py` 与 `evidence/{obligation-*,PKG-A1-*}`、`memory/waves/PKG-A1-*`、`memory/handoffs/PKG-A1-*` ⇒ **写域内**；`specs/**`·`generated/**`·`docs/dd/**` 未改；KERT 零写入 ✓ |

**MAJOR-1（A1 唯一实质缺陷）｜证据列与"命中术语"脱钩，影响 16.6% 的 TRUE 行**

- **现象（可复现）**：`evidence` 指向第 1 行（`@prefix` 行），而 rationale 写「命中术语 `Product@L10`」——该行并无 `Product`。同型 104 行。首 3 例：
  - `gits:specs/knowledge-architecture/instances/product/products.ttl:1` ↔「命中术语 `Product@L10`」；该行实际 = `@prefix gits: <https://gits.bank.example/ontology/core#> .`
  - `kert:src/kert/application/skills.py:963` ↔「`KM-CORP-RM-MEETING@L1039`」；该行实际 = `"planHash": decision.plan_hash, …`
  - `gits:adapters/semantic-jena/src/main/java/…/JenaOntologyAdapter.java:31` ↔「`CTR-SEM-002@L50`」
- **机制（回源到行）**：`scripts/onto1_obligation_triage.py:466` `line = content_hit[1]`（内容命中行）而 `:471` 的 rationale **恒用 `evidence_lines[0]`**（`f"…命中术语 {evidence_lines[0][0]}@L{evidence_lines[0][1]}"`）⇒ 当 `content_hit ≠ evidence_lines[0]` 时，**同一行 CSV 的两个字段描述不同的 token/行**。仅路径面行（`:469`）二者才一致——这解释了为何 104 行**全部**是 `STRONG_CONTENT`。
- **与声明的冲突**：HANDOFF §3 的 G4 写「该行可回源复核（含行号越界、**行内无 token** ⇒ FAIL）」。按该字面，这 104 行应判 FAIL，但 G4 **exit 0** ⇒ 二者必有一不实：要么 G4 实际只校验"evidence 行含**该 pattern 的字面**"，要么 G4 有盲区。
- **影响**：`TRUE_OBLIGATION` 正是 Wave 2 的执行清单；照 `evidence` 列回源的执行者会读到**不含该术语的行**（`PLAN-NEXT.md:49` 亦要求"每条结论须带 `文件:行`"）。
- **建议（可执行，任选其一，但须选明）**：① 让 `evidence` 取自 `evidence_lines[0]`（与 rationale 同源，最小改动）；或 ② 拆分字段：`evidence`（该 pattern 字面所在行）+ `term_line`（命中术语所在行），并把 G4 的 `pass_condition` 改为可复核的精确表述；③ 补一条变异 **「把某 TRUE 行证据行号 +1 ⇒ G4 必须 FAIL」**（HANDOFF §8 自己也建议了这条，我复算找到多个可用靶点，如 `FilesystemActivationContractReader.java:3 → +1 行才含术语`）。
- **不判 BLOCKER 的理由**：判定本身（TRUE/NEEDS 分类）不因该缺陷改变，且 1052/626/0/426、Wave 归类、P0 计数**全部经我独立复算无误**；受损的是"证据可回源"的**呈现精度**。但因 `TRUE` 行是执行清单，故列 MAJOR 而非 MINOR。

**A1 条件**：C-A1-1 修 §12.1 的 MAJOR-1（选 ①②之一 + 补 ③ 的变异）；C-A1-2 HANDOFF §6.1 已正确上报"真义务 626 > 400 阈值 ⇒ 须回写 `evidence/WBS-RESTIMATE.md` 与 `ORCHESTRATOR.md §5`"，该两文件在 A1 写域外 ⇒ **请 TL 执行**（这是 A1 主动上报的诚实项，非缺陷）；C-A1-3 口径 I-1/I-2/I-6 待你裁定（I-6 = P0 65 行是否升格，升格则 TRUE 626→691）。

### 12.2 PKG-A2 — 结论 **`ACCEPT_WITH_CONDITIONS`（与 TL 一致）**

| 动作 | 命令 | 结果 |
|---|---|---|
| **AU-1** | `sha256sum` 三件 | `285bada36ca55de5…` / `0c6b7498531957c5…` / `4d67e70be5ec1e4b…` ⇒ **与 HANDOFF §1 逐字一致** ✓ |
| **AU-2** | `--gate` / `--precheck` / `--selftest` | **2 / 0 / 0** ⇒ 与 HANDOFF 一致 ✓ |
| **AU-3** | 独立复算 R2/R3/R4 | R2 `sha256=705578d6324abd0c`（与 C-4 的 baseline 钉值一致 ✓）；R3 归属矩阵 87 行（`customer-scan` 无关）；R4 `consumer-scan-obligations.csv` 1052 行、`summary` 中 `PENDING_TRIAGE=0`（我已在首轮逐条核过 §3.4 S-8）✓ |
| **AU-4** | 读源码验证"条目级断言"而非 exit 码凑数 | `PKG-A2-PLAN.md:57-59` 与 selftest 输出一致：**M1**（篡改复审包 ⇒ `items["R1"]=NOT_READY`）、**M2a/M2b**（R2 哈希/计数）、**M3a/M3b**（R6/R7 各自有牙齿）、**M3c**（齐备 ⇒ PASS，证明**非永久红**）、**M3d**（无签署标记不算签署件）、**M5**、**M6×6**（缺输入 fail-closed）、**M4/M4b**（真实仓 NOT_READY 恰为 `['R6','R7']`）⇒ **非空转** ✓ |
| **AU-4 反例（我本职）** | 「R6/R7 是否被做成可跳过 / `--precheck` 是否放过 R1/R2」 | **未成立**：`onto1_wave0_readiness.py:416-417` `precheck_pass = all(... if key not in EXTERNAL_HELD_ITEMS)` ⇒ 仅排除 R6/R7；M1/M2a/M2b 断言落在 `items["R1"]/["R2"]` 上 ✓ |
| **AU-5** | 红线 | 写域内；`specs/generated/docs.dd` 未改；KERT 零写入；未 `git add` ✓ |

**A2 条件（与 TL 的 T-1/T-2/T-3、D-9 触发义务一致，我不另加）**：C-A2-1 D3 签署时 R5 判据须翻转并回填 `D3_SIGNED_PATTERNS`（否则 fail-closed 误红）；C-A2-2 G-1 达成后 24h 内跑 `--gate`、登记 `wi_a2_wave0_readiness`、更新 `--precheck` 语义；C-A2-3 R6/R7 之外出现 NOT_READY ⇒ 按真实漂移处理。
**我接受 D-9（`--gate` 不登记）与 D-10（接受 M3 拆分）**：理由同 TL（常红项诱发红灯疲劳；多锚点门禁的正确变异设计就是"每锚点独立有牙齿 + 齐备可转绿"）。**但须强调 D-9 的诚实性前提**：`--gate` 的 exit 2 与唯二 NOT_READY（R6/R7）必须在**五处**（审计报告/`wave0-readiness-gate.json`/`EVIDENCE.md`/`NEXT_SESSION.md`/`PLAN-NEXT.md`）持续可见——**其中任一处消失即须恢复登记**，否则"不登记"会退化为"看不见的红灯"。

## 13. 第三轮总判定

| PKG | 判定 | 未闭合项 |
|---|---|---|
| **PKG-A1** | `ACCEPT_WITH_CONDITIONS` | MAJOR-1（证据列与命中术语脱钩 104/626，`onto1_obligation_triage.py:466/:471`）+ C-A1-2/3（TL 动作与口径裁定） |
| **PKG-A2** | `ACCEPT_WITH_CONDITIONS` | 仅 TL 侧触发条件（T-1/T-2/T-3）；**无 pilot 缺陷** |
| **PKG-A3** | `NOT_ACCEPTED` | **Q-1（BLOCKER，TL 未裁定）**、**Q-4/R-1（MAJOR，TL 未裁定）**；Q-2/Q-3 已按在飞纪律**不计缺陷**，但 **N-2（冻结后 HANDOFF 必须与字节一致）** 仍是重交前置 |

## 14. 非声明（第三轮）

1. **三者均不构成 `QA_PASS`**：`EVIDENCE.json.independent_qa` 仍 `pending/actor=null`；本 Loop 唯一已知 fail（`wi_a4_namespace_collision`）仍是 fail ⇒ `ready_for_independent_qa` 硬约束未满足，本批次无 QA_PASS 权限。
2. **不覆盖** Wave 0/1/2+；不裁定 I-1/I-2/I-6、D-9 触发义务、R-1 修复方式（口径/治理归 TL/Owner）。
3. **不采信** TL 的 `TL-AUDIT-W15-PKG-A2.md`——§12.2 是我**自算**结果（我读其报告仅供比对条件清单，AU-1/AU-2/AU-3/AU-4 均自跑）。
4. **未修改任何文件**：仅追加本报告；A1 的 626 行全量回源核对、X1~X5 反例、E3-redo 均在 `/tmp` 或纯读取完成，未写仓内任何文件（`--report` 刻意未执行）。
5. **回源纪律**：所有结论附 `文件:行`；KERT 侧 `INDEX_STALE(144)` 未刷新，未使用索引外推。
