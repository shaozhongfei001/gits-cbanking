# 独立 QA 报告（第三轮 / W3R3 定向覆盖）— ONTO1-ontology-split

> 范围：**只做** 13 个「违规清单 + 退出码 / print」形态仪器的**失败路径可达性分析**（违规点分析视角），
> 每个仪器回答四问（失败路径清单 / 可达性 / 构造性实验 / 自检覆盖），另加 2 项观察与 1 项自审仪抽查。
> 原则：**不采信 TL 的任何结论（含派工提示词里的全部数字）**；下列每条结论均由**我本人执行命令**取得，原始输出照录。

## 0. 开工声明

```text
actor       = independent_qa（第三轮 / W3R3 定向覆盖）
独立性三条件 = ① 非实现方（本轮零实现、零制品改动，除本报告）
              ② 非本汇报方（未参与 TL 的任何审计/裁定会话，凡引用均回源复算）
              ③ 非临时兼任 PSO/ICO 者（PSO/ICO interim holder = 项目 Owner 邵钟飞，本人非该二角色）
写域（唯一） = loops/ONTO1-ontology-split/memory/handoffs/INDEPENDENT-QA-W3R3-2026-09-22.md
只读        = /home/szf/dev/gits-cbanking 全仓 + /home/szf/dev/Leibniz-KERT（**KERT 零写入**）
仓库        = /home/szf/dev/gits-cbanking ｜ 分支 recover/PI-ARCH-product-catalog
HEAD        = f1a9fdd2afd089d3232d846d626289c3aa297ee5
索引新鲜度   = gits: STATE.json 记 INDEX_FRESH@71169042（与本 HEAD 不符 ⇒ **我按原码直接读取，未用索引外推**）
             KERT: INDEX_STALE(144)（本报告对 KERT 只读、只读入，未推断）
```

**Baton 观察（登记项，非停工项）**：`ROLE_BOARD.baton.holder = tech_lead`；`parallel_allowed` 含 `qa-w3r2`，
**不含字面 `qa-w3r3`**。本轮我只写 1 个新文件（与 TL 单写者文件零交集）；请下一 holder 把 `qa-w3r3` 补登记。

## 1. 结论总表

| # | 仪器 | 承载门禁 | 出口判定 | 一句话 |
|---|---|---|---|---|
| 1 | `onto1_attribution_rebuild.py` | 2 | **SOUND** | A2/A3/A4/A5/A6/A7 可达；**A1 被前置哈希闸门遮蔽（近似死路径，观察项）**；未覆盖 A1/A5/A6/三条 RuntimeError |
| 2 | `onto1_cq_fixtures.py` | 2 | **HAS_DEAD_PATH** | **`--gate` 先按常量重生成 6 份夹具再校验 ⇒ Q1~Q5 在真实制品上永不可达**（两极端实验均为 exit 0） |
| 3 | `onto1_d2_normalization_pack.py` | 2 | **HAS_DEAD_PATH** | **G8 恒真（构造性实验）**；**且当前实测 `--gate` FAIL（exit 2）/`--selftest` FAIL（M0+M1）**——板面仍记 pass |
| 4 | `onto1_d4_pack.py` | 2 | **SOUND** | C1~C11 全部可达（M1~M9 覆盖 8 条）；未覆盖 C1/C4/C10/C11/崩溃路径 |
| 5 | `onto1_evidence_board_check.py` | 2 | **SOUND** | E1~E5 全部可达（已实测）；未覆盖 E1（2 分支）/E4/白名单 schema |
| 6 | `onto1_namespace_collision_check.py` | 2 | **HAS_DEAD_PATH** | **C-4b「载体自冻结」在真实布局下 `freeze_subjects` 恒为 0 ⇒ 恒不触发，且"改钉值即可通过"防线不存在（已用篡改实验证明）**；C-3 空转（输出已声明） |
| 7 | `onto1_product_refs_probe.py` | 2 | **HAS_DEAD_PATH** | **P1 分支位于 `probe()` 抛错之后 ⇒ 永不可达**（P2/P3 可达） |
| 8 | `onto1_reference_alignment_check.py` | 2 | **SOUND** | 内置必败变异（自控）+ 空转下限提供真牙齿；约 24 条失败码中自检覆盖 9 条 |
| 9 | `onto1_review_package_check.py` | 2 | **SOUND** | R1/R2/R3 可达；R3 四条子失败与"目录缺失"早退未覆盖 |
| 10 | `onto1_consumer_scan_tests.py` | 1 | **SOUND** | 19/19，锚定规则/期望命中/净义务/处置完成度，非空转 |
| 11 | `onto1_w15_acceptance.py` | 1 | **SOUND** | 8/8；`violated()` 的"文件名出现"代理**经两极端实验证明有判别力**（非恒真） |
| 12 | `onto1_check_strength_audit.py` | 0 | **HAS_DEAD_PATH** | **`main()` 所有分支 `return 0` ⇒ 无任何 FAIL 出口**；作为报告器可用（D-20 未登记门禁），作为仪器无判别力 |
| 13 | `onto1_pkg_audit.py` | 0 | **HAS_DEAD_PATH** | **AU-5 红线在"Owner 已授权 SIM 整改"的当前状态下实测永红（2 findings / exit 2），且无时间维或豁免维 ⇒ 不可分辨**；`recent_changes()` 恒 `return []` |

**观察项**：`onto1_c2_generator_check.py:57` G0 = **fail-closed 具名出口（可达，非死路径）**，但**被自审仪误报为 `TAUTOLOGY_CONST`（high）**；
`onto1_sim_projection.py:142` G4 = **两条文本合取项恒真 + 另两条读配置自述 + `out` 形参未被引用 ⇒ 等价于「读自我声明」**。

**问题 6（自审仪 v2 可信度）**：`226 / 15 / 13` 三个数字**逐字复现**；但「四类形态真被抽到」**部分不成立**——
`下标赋值 dict`（`report["checks"]["C-1b"]={...}`）与 `failures.append("字符串")` **均未作为判据被审**（只登记 `STRING_NOTE`）；
且发现 **1 条确凿假报**（G0）与 **1 类假计数**（数据元组被登记为 `STRING_NOTE`）。

**总体**：**6 HAS_DEAD_PATH + 7 SOUND**；**1 条注册门禁的当前实测红（`wi_a5_d2_pack`，见 §2.3）**。
**不得记 `QA_PASS`**（板面仍有 1 inconclusive + 本次新增实测红 + 6 条死路径未修）。

---

## 2. 逐仪器四问（命令 / 退出码 / 原始输出）

### 2.1 `onto1_attribution_rebuild.py`（★ 门禁 2：`wi_a1_baseline` / `wi_a1_attribution_selftest`）→ SOUND

**Q1 失败路径清单**（源码：`validate()` A1~A7 + `gate()` 的 3 条 `RuntimeError`）：
`A1` 基线计数 ≠32/34/1 · `A2` 45≠39+1+5 · `A3` 8/12/19 或 36 属性或 5 字段或 1 退役 · `A4` 基线类无去向/未覆盖/重复 termId ·
`A5` 基线对象属性无去向 · `A6` 数据属性未退役 · `A7` 占位根域 · `RuntimeError`（种子缺失 / 基线缺失 / 基线 sha 前缀漂移）
——全部收敛为 `print(FAIL)` + `return 2`。

**Q2 可达性**：

```text
$ python3 -c "...；sys.exit(m.gate(write=False))"
A1 baseline sha256=705578d6324abd0c counts={'owl_class': 32, 'owl_object_property': 34, 'owl_datatype_property': 1}
A2 model assets=45 (39 OWL / 1 SKOS / 5 Schema) rows=87
onto1-attribution: PASS                     EXIT=0
```

| 路径 | 可达？ | 依据 |
|---|---|---|
| A2 / A3 / A4 | **可达** | `--selftest` M1 实测同时触发 A2+A3+A4（见 Q4 输出） |
| A7 | **可达** | M3 实测触发 |
| A5 / A6 | 可达（未被任何用例触发，但由种子行数直接派生） | 代码 `:222-231`；删一条对象属性行即触发 |
| **A1** | **实际不可达（遮蔽型近似死路径）** | A1 要触发必须先通过 `load_baseline()` 的 `sha.startswith("705578d6324abd0c")`；同一份字节被 rdflib 解析出的计数若变化，sha 必然变化 ⇒ 走 `RuntimeError` 分支（同样 exit 2）。⇒ A1 仅在 32-bit 前缀碰撞下才可能独立触发 |
| RuntimeError 3 条 | **可达** | 种子/基线缺失为真实文件系统事件 |

> **判定**：仪器整体**能 FAIL**（不含 A1 亦可），故非「永不 FAIL」；但 **A1 作为独立判据名存实亡**——登记文案「基线哈希与计数 32/34/1 一致」的**计数一半永不生效**。

**Q3 构造性实验**：无需（未声称恒真）；M1~M3 本身就是真实变异。

**Q4 自检覆盖**：

```text
$ python3 scripts/onto1_attribution_rebuild.py --selftest
PASS  M1 删除基线类 OperatingCase 映射行 ⇒ FAIL  exit=2
      stderr: A2 model assets = 44 != 45 / A2 split = 38 OWL / A3 layer split = 8/12/18 / A4 baseline classes without target: ['OperatingCase']
PASS  M2 Task 改成 Schema 对象 ⇒ A2 分口径 FAIL  exit=2   （触发 A2+A3）
PASS  M3 权威 IRI 用 bank.example 占位根域 ⇒ A7 FAIL  exit=2（触发 A2+A3+A7）
PASS  M0 对照：未变异种子 ⇒ PASS  exit=0
onto1-attribution-selftest: PASS            EXIT=0
```

- 覆盖到的判据：**A2 / A3 / A4 / A7**；未覆盖：**A1 / A5 / A6 / 三条 RuntimeError**。
- **附带缺陷（判据级归属缺失）**：M1~M3 的断言只有 `ok = code == 2`（`:331`），**不校验是"哪条判据"拦下的**。
  M1 一次性触发 4 条判据 ⇒ 若 A4 死了而 A2 仍在，M1 照样 PASS。这与同一 Loop 已确立的
  「必须被**指定判据本尊**捕获」（`wi_a2_disposition_selftest` 的口径）不一致，属**弱于既有标准**。

### 2.2 `onto1_cq_fixtures.py`（★ 门禁 2：`wi_a6_cq_fixtures` / `wi_a6_cq_fixtures_selftest`）→ **HAS_DEAD_PATH**

**Q1 失败路径清单**：`Q1` 缺夹具文件 · `Q2` 六要素缺失/空 · `Q3` 设计阶段标 PASS · `Q4` D2/D4 阻塞项非 NOT_EVALUATED ·
`Q5` 缺否定式断言（negative / mutation）；全部 `print(FAIL)` + `return 2`。

**Q2 可达性**：**全部不可达。** 关键在 `gate()`（`:159-163`）：

```text
def gate(out_dir=None, write=True):
    target = out_dir or OUT_DIR
    if write:                 # ← 默认 True
        write_fixtures(target)   # ← 先用脚本内常量 CQ_DEFINITIONS 覆盖 6 份夹具
    failures = validate(target)  # ← 再校验"刚被自己写出来的东西"
```

`validate()` 读的是**同一次运行刚由常量生成的产物**；而 `CQ_DEFINITIONS` 的 6 条定义**按构造**满足
REQUIRED_KEYS / 非 PASS / NOT_EVALUATED / 非空 negative+mutation ⇒ **Q1~Q5 不可能为真**。

**Q3 构造性实验（两极端）**：

```text
$ python3 /tmp/qa3/probe_cq.py            # 只在 /tmp 临时目录操作
步骤1 生成: ['CQ1.json', 'CQ2.json', 'CQ3.json', 'CQ4.json', 'CQ5.json', 'CQ6.json']
极端1 盘上破坏后 validate(tmp) = ['Q2 CQ1 missing/empty field: negative', 'Q2 CQ1 missing/empty field: mutation',
                                 'Q3 CQ1 must not claim PASS during design phase'] ... 共 33 条
极端1 盘上被破坏后立刻跑 --gate(等价) exit = 0
极端1 跑完后盘上 CQ3 的 status/negative = NOT_EVALUATED '卡指向已退役版本 / 悬空 product_id（40 处悬空引用样本）⇒ 具名提示 `DANGLING_PRODUCT_REF`'
[Q1] fixtures=6 …  onto1-cq-fixtures: PASS
极端2 干净夹具 --gate(等价) exit = 0
结论：两个极端下 --gate 判定 = 0 / 0
```

**我改了什么**（全部在 `/tmp`，仓内零改动）：把 6 份**盘上**夹具全部改成最坏形态（`status=PASS` + 清空 `negative`/`mutation`），
随即调用与 `--gate` 等价的 `gate(out_dir=tmp)`。结果：`validate()` 报 **33 条违规**，而 `gate()` **判 PASS（exit 0）**，
并且**把 33 条违规全部覆盖回常量形态**（`CQ3.status` 变回 `NOT_EVALUATED`、`negative` 复原）。
⇒ **「判定与被判对象同源」的极端形态：判据不但恒真，还主动擦除证据。**

**Q4 自检覆盖**：`--selftest` M1/M2/M3 直接调用 `validate(tmp)`（**绕过 gate 的写回**）⇒ 覆盖 Q3/Q4、Q2/Q5、Q1；
**但对"`--gate` 永不可能 FAIL"这一点零覆盖**（自检 5 个 PASS 与门禁的可判别性无关）。
⇒ 与 QA 第二轮 N-1 同型（**"判据死了，自检 3/3 也没发现"**），但更彻底：不是某条判据死了，而是**整机的 5 条失败路径都死了**。

**附注（安全）**：`gate()` 默认 `write=True` ⇒ 任何人跑一次 `--gate` 都会**重写 6 份登记证据文件**，把人工改写静默擦除。

### 2.3 `onto1_d2_normalization_pack.py`（★ 门禁 2）→ **HAS_DEAD_PATH ＋ 当前实测 FAIL**

**Q1 失败路径清单**：`G1` 计数（40=12+28/12 取值/13 卡）· `G2` 零实例事实 · `G3` 候选行齐备 · `G4` 回源位置校验 ·
`G5` 证据强度/反证 · `G6` 候选越界身份空间 · `G7` 三场景全 NOT_EVALUATED · `G8` 非裁定声明与 R-6 保留；
全部 `print(FAIL)` + `failures.append` + `return 2`。

**Q2 可达性（含重大事实）**：**G4 当前在真实制品上为 FAIL，且不是偶发。**

```text
$ python3 -c "...；sys.exit(m.gate(out_dir=Path('/tmp/qa3-out-d2')))"     # out_dir 指 /tmp，避免改写仓内制品
[G1] occurrences=40 by_field={'prerequisite_product_ids': 12, 'mutex_product_ids': 0, 'complementary_products': 28} distinct=12 cards=13 ⇒ PASS
[G2] mutex_product_ids empty 13/13，正文互斥叙述 4 处 ⇒ PASS（零实例 ⇒ NOT_EVALUATED，不得包装为通过）
[G3] 候选行齐备：12 行，缺行 [] ⇒ PASS
[G4] 回源位置校验：78 条（含语义命中），问题 5 ⇒ FAIL
[G5] 证据强度 / 反证齐备：问题 0 ⇒ PASS
[G6] PROD-* 候选落在身份空间（13 个）：越界 [] ⇒ PASS
[G7] 三场景状态 {'requiresProduct': 'NOT_EVALUATED', …} ⇒ PASS
[G8] 非裁定声明与 R-6 保留 ⇒ PASS
     - SETTLEMENT_ACCOUNT / PROD-SET-001: line content mismatch: …products.ttl:60 expected '单位结算账户'
     - CASH_POOL / PROD-CM-001:        line content mismatch: …products.ttl:25 expected '现金池'
     - WORKING_CAPITAL_LOAN / PROD-FIN-001: …products.ttl:40 expected '流动资金贷款'
     - CROSS_BORDER_RMB_SETTLEMENT / PROD-CB-001: …products.ttl:15 expected '跨境人民币结算'
     - BANK_ACCEPTANCE_DRAFT / PROD-TF-001: …products.ttl:70 expected '银行承兑汇票'
onto1-d2-pack: FAIL: G4 evidence refs failed: [...]        EXIT=2
```

**独立复算（第二次执行，不经 gate）**：

```text
$ python3 -c "...m.build_pack(); m.verify_all_refs(m.CANDIDATES, m.SEMANTIC_HITS)"
独立复算 verify_all_refs 问题数 = 5
   （同上 5 条）
```

**根因（回源，非推测）**——**行号整体位移 −2**：

```text
$ grep -n "跨境人民币结算\|现金池\|流动资金贷款\|单位结算账户\|银行承兑汇票" specs/.../products.ttl
13:  rdfs:label "跨境人民币结算" ;       （期望 15 → 差 −2）
23:  rdfs:label "现金池" ;               （期望 25 → 差 −2）
38:  rdfs:label "流动资金贷款" ;          （期望 40 → 差 −2）
58:  rdfs:label "单位结算账户" ;          （期望 60 → 差 −2）
68:  rdfs:label "银行承兑汇票" ;          （期望 70 → 差 −2）
$ sed -n '15p;25p;40p;60p;70p' specs/.../products.ttl     ⇒ 五行全部为 "  a gits:Product ;"
```

⇒ C-2 修复**重新生成** `products.ttl`（`@prefix` 分隔行减少 2 行）后，D2 决策包里**逐条以"行内容+行号"锚定的回源证据**
全部位移 −2 ⇒ G4 判 FAIL。

**时间线（`stat`，本机 +0800）**：

```text
2026-09-21 12:33:15  evidence/d2-normalization-pack.json（与 wi_a5_d2_pack-20260921T043315Z.log）
2026-09-21 21:41:45  specs/knowledge-architecture/instances/product/products.ttl   ← 晚 9 小时
EVIDENCE.json：wi_a5_d2_pack status=pass executed_at=2026-09-21T04:33:15Z  （UTC）
              wi_c2_fix_verify      executed_at=2026-09-21T05:05:47Z
板面：gates=84  Counter({'pass': 83, 'inconclusive': 1})   board_expression PASS=83 FAIL=0 total=84
全仓 grep：FAILURES.md / EVIDENCE.md / ORCHESTRATOR.md 中**无任何**"d2 门禁在 C-2 重生成后失效"的登记
```

⇒ **注册门禁 `wi_a5_d2_pack` 在板面上仍为 `pass`，但在当前树上实测 FAIL（exit 2）；`--selftest` 亦 FAIL**（见 Q4）。
按 `LOOP.yaml.gate_state.board_expression_rule`，`FAIL` 不得计入 `PENDING_EXTERNAL_AUTHORITY`（那是 `exit 3` 的口径），
故该 gate 若按真实退出码重记，应为 **fail**，板面应从「83 pass / 0 fail / 1 pending」变为 **至少 81 pass / 2 fail**（含 selftest 则 81/3）。

**G8 恒真（构造性实验）**：

```text
$ python3 /tmp/qa3/probe_d2b.py
盘上（新构建）含 'R-6' 的字段：
    /no_ruling_declaration :: 本包不含裁定：…不关闭 R-6 风险登记…
    /prohibited_actions[5] :: 关闭 R-6 风险登记
极端1 删除 prohibited_actions（含唯一的 R-6 保留项）后 G8 = True
极端2 声明字段是 build_pack() 内的**硬编码字符串** ⇒ 恒非空 ⇒ 第1合取项恒真
```

`G8`（源码 `:1053-1057`）= `bool(pack["no_ruling_declaration"]) and "R-6" in json.dumps(pack)`：
- 第 1 合取项：`build_pack()` `:828-832` **硬编码非空字符串** ⇒ 恒真；
- 第 2 合取项：**该声明文本自身含 "R-6"** ⇒ **自我满足**，与"R-6 保留"是否真的在案无关。

两条极端实验（删掉唯一的 R-6 保留项 / 声明字段空）证明：**删掉 R-6 保留声明，G8 仍 PASS**
⇒ 判据文案里的「R-6 保留」**从未被校验**（与 QA 第二轮 A5「同源」同型，此处更纯：**自指**）。

**盘上制品 ≠ 当前构建（新鲜度）**：

```text
$ python3 -c "...diff(json.load(盘上), build_pack())"
VAL /inputs/gits_commit      disk= 9a6dec78046172cd60cb8032f4419905e1958515 | mem= f1a9fdd2afd089d3232d846d626289c3aa297ee5
VAL /inputs/products_ttl/sha256 disk= b8875c169695fe8e52584bc1b97622987a9b09b0c0c7772b6921ea471570 | mem= e1b6e09e…
```

⇒ `--gate`（默认 `write=True`）会**改写** 3 份制品并改变其哈希；**我因此改用 `out_dir=/tmp` 运行，未触碰仓内制品**。

**Q4 自检覆盖**：

```text
$ python3 scripts/onto1_d2_normalization_pack.py --selftest
…
PASS  M4 卡集不全（1 张卡 / 3 处引用）⇒ 门禁 FAIL  exit=2
PASS  M5 三场景标 PASS ⇒ 门禁 FAIL  exit=2
…
PASS  M0 真实产品卡 ⇒ 自检 PASS  exit=0        ← **现为 FAIL**
PASS  M1 候选回源篡改 + 语义命中行号越界 ⇒ 被拦下（2 条）
onto1-d2-pack-selftest: FAIL ['M0', 'M1']      EXIT=2
```

- **M0 现为 FAIL**（真实包已不 PASS）——自检**如实暴露了**门禁的红，这一点是好的；
- **M1 因绝对计数（`len(problems) == 2`）而连带 FAIL**：基线不干净时"变异被拦下"的断言失真
  ⇒ **变异用例的断言用了绝对数而非增量**，属可移植性缺陷（本日实测暴露）；
- 覆盖：G3/G4/G5/G6/G7/G1（M4）/G7（M5）；**未覆盖 G2 / G8**，且 **M1 的 5 条既有问题与其 2 条变异无法区分**。

### 2.4 `onto1_d4_pack.py`（★ 门禁 2）→ SOUND

**Q1**：`C1` L1 八类集合 · `C2` Owner 非空/禁权威/CARRIER 自述 · `C3` 候选数 2~3 + 证据 + kind 合法 · `C4` EXCLUDED + PROHIBITED ·
`C5` 证据回源（文件存在） · `C6` 六必填 + 具名拒绝码/fail_closed/≥6 子码/≥4 禁止行为/必含「静默补默认值」 ·
`C7` NOT_EFFECTIVE + 无生效日期/签署人 + 七要素 + ≥5 漂移码 + ≥4 失效条件 · `C8` 三载体 + 四退出条件 + 台账未启动 ·
`C9` CQ1/CQ2 NOT_EVALUATED + 包内无 PASS + 正文无 PASS 表格 · `C10` manifest 哈希 · `C11` 正文关键声明。

**Q2 可达性**：

```text
$ python3 scripts/onto1_d4_pack.py --gate
[C1] terms=8 rows=32
[C6] source_identifier required=['sourceSystem','objectType','originalId','validFrom','extractedAt','authorizationBasis']
[C7] projection_contract=NOT_EFFECTIVE effective_from=None
[C8] sim_declaration=NOT_EFFECTIVE exit_conditions=4 ledger=TRACKING_NOT_STARTED
[C9] CQ1=NOT_EVALUATED CQ2=NOT_EVALUATED
onto1-d4-pack: PASS        EXIT=0
```

C1~C11 全部由**真实制品**（CSV/JSON/正文）派生：C3/C5 依赖候选与文件存在性、C8/C9 依赖包内状态、C10 依赖哈希漂移、
C11 依赖正文关键词 ⇒ **均可为真**（假值均由人为改动触发，属正常判据）。

**Q3 构造性实验**：无需（无恒真声称）。另实测**崩溃路径**（属 D-11「崩溃 ≠ FAIL」）：

```text
$ python3 -c "...d4.gate(d4.EVID/d4.CSV_NAME, <畸形 json>)"
抛未捕获异常 ⇒ JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 3
```

`gate()` `:329-337` 的打印块用 `pack['source_identifier']` 等**直接下标** ⇒ 机读包缺键即 KeyError/JSONDecodeError（exit 1），
**不是具名 FAIL**；`check()` 内部虽 `.get()` 安全，但崩溃发生在返回前。**该路径无自检用例**。

**Q4 自检覆盖**：

```text
$ python3 scripts/onto1_d4_pack.py --selftest
PASS  M4 投影合同填生效日期 ⇒ FAIL      PASS  M5 候选缺证据 ⇒ FAIL     PASS  M6 证据不可回源 ⇒ FAIL
PASS  M7 集团候选只剩 1 个 ⇒ FAIL       PASS  M8 SIM 退出条件少一条 ⇒ FAIL  PASS  M9 声明未生效却启动台账 ⇒ FAIL
… onto1-d4-pack: PASS  PASS  M0 对照：真实决策包 ⇒ PASS  exit=0
onto1-d4-pack-selftest: PASS            EXIT=0
```

覆盖 9（含 M1/M2/M3 在截断输出之外）；**未覆盖**：`C1`、`C4`、`C10`、`C11`、`C2-CARRIER` 分支、
`C6` 的 subcodes/forbidden_behaviors 两条、以及上条崩溃路径。断言方式为 **needle 级**（`expect_fail(..., "C2 LegalEntity")`）⇒ 优于"只看退出码"。

### 2.5 `onto1_evidence_board_check.py`（★ 门禁 2）→ SOUND

**Q1**：`E1` 目录/文件缺失（2 分支，**早退**） · `E2` 孤儿日志 · `E3` 已登记证据文件缺失 · `E5` 白名单通配吞掉已登记证据 ·
`E4` 白名单文件存在但条目为空 · `load_allowlist` 的 2 类 `RuntimeError`（缺 `allow` 数组 / 条目缺 file·reason）。

**Q2 可达性（全部实测可达）**：

```text
$ python3 /tmp/qa3/probe_board.py
[1] E1 目录缺失 ⇒ ['E1 evidence dir missing: /tmp/…/nope']
[2] E1 EVIDENCE.json 缺失 ⇒ ['E1 EVIDENCE.json missing: /tmp/…/nope.json']
[3] check(EVIDENCE_DIR=仓内, allowlist=空表) ⇒ ['E4 allowlist file exists but contains no entry']
    （同次：E2 evidence logs=116 registered=84 allowlisted=0 orphan=32 ⇒ E2 亦可达）
[4] 白名单条目缺 reason ⇒ RuntimeError: allowlist entry lacks file/reason: {'file': 'a.log'}
```

```text
$ python3 scripts/onto1_evidence_board_check.py --gate
[E1] evidence dir ok; gates=84
[E2] evidence logs=116 registered=84 allowlisted=32 orphan=0
[E3] registered evidence files present=84/84
onto1-evidence-board: PASS          EXIT=0
```

**Q3 构造性实验**：无需（无恒真声称）。**无「恒不触发」路径**：E2/E3/E5 由 M1/M2/M4/M5 实测触发，E1/E4 由上表实测触发。

**Q4 自检覆盖**：

```text
$ python3 scripts/onto1_evidence_board_check.py --selftest
PASS M0 / PASS M1（E2 孤儿）/ PASS M2（E3 缺失）/ PASS M4（无前缀日志 ⇒ E2）/ PASS M5（E5 通配）/ PASS M5b（精确名容忍）/ PASS M3（真实 Loop exit 0）
onto1-evidence-board-selftest: PASS    EXIT=0
```

**未覆盖**：`E1`（2 分支）、`E4`、`load_allowlist` 的 2 类 `RuntimeError`。
**附带观察（非缺陷）**：`GATE_LOG_RE` 现仅被 M4 用作"旧前缀逻辑不可见"的对照断言；`gate_like = logs`（`:83`）已全量纳入 `*.log` ⇒ E2 无前缀盲区（QA 第二轮 U-6 的修复已实证生效）。

### 2.6 `onto1_namespace_collision_check.py`（★ 门禁 2，现 inconclusive）→ **HAS_DEAD_PATH**

**Q1 失败路径清单**（`fail()` 全部入口）：`C-4_REQUIRED_PIN_MISSING`（**输入存在性闸门**，早退；与 allow-list 声明/文件两条） ·
`PLACEHOLDER_ROOT_REJECTED` · `D3_SIGNATURE_REQUIRED` · `C-1b` 不互斥 · `C-1a` 旧端集合 ≠67 · `C-2`（实测碰撞 / 全登记 / 未登记 / 陈旧 / 缺 Owner） ·
`C-2_ALL_CONFLICTS_REGISTERED_NOT_EXEMPTED` · `C-3` 多 versionIRI · `C-4` 受控漂移 / `C-4_PIN_SCOPE_UNCLASSIFIED` / `C-4_NO_CONTROLLED_PIN` /
`C-4_PIN_FILE_UNFROZEN` / `C-4_SELF_REFERENCE`；另有 `run()` 兜底的 `SETUP:`（未识别新 IRI 形态 / manifest 缺失）；
退出码 `2`=FAIL、`3`=INCOMPLETE、`0`=PASS。

**Q2 可达性（真实制品）**：

```text
$ python3 scripts/onto1_namespace_collision_check.py --gate
[根] …（legacy namespace = https://gientech.com/gits/kno/ @ specs/semantic/gits-core.owl.ttl:1；旧端术语 67）
[新] 清单行 87  具体 IRI 0  占位 87  根域 未定  D3 签署件=False
[C-1a] PASS   [C-1b] NOT_EVALUATED   [C-2] PASS（实测 0 / 登记 0 / 未登记 0 / 陈旧 0）
[C-3] PASS（closure 内 0 个 owl:versionIRI ⇒ 单版本约束**空转**，不计为覆盖）
[C-4] PASS（声明 4 个：受控 1 / D-2 范围外 3 / 未裁决 0；必需钉值 allow-list 4/4；载体自冻结：受控载体 0 个，**空转不计为覆盖**）
onto1-namespace-collision: INCOMPLETE      EXIT=3
```

- `C-3`：**当前空转 PASS**（`version_iri_total==0`）—— 输出与文档**均已显式声明**「不计为覆盖」，属**已声明的空转**，不构成本轮新发现。
- **`C-4_PIN_FILE_UNFROZEN`：在真实布局下结构性恒不触发**（本轮决定性发现，见 Q3）。
- `PLACEHOLDER_ROOT_REJECTED` / `D3_SIGNATURE_REQUIRED` 当前因 `roots=[]`（无具体 IRI）而不触发，但**可达**（M8/M9 实测；D3 一经填根域即进入射程）。

**Q3 构造性实验：C-4b 在真实布局恒不触发，且"改钉值即可通过"防线不存在**

```text
$ python3 /tmp/qa3/probe_collision.py          # 全程在 /tmp 的仓副本内，仓内零改动
[对照]   未篡改副本 ：            result=INCOMPLETE exit=3 C-4=PASS 受控载体=0 空转=['pin_sidecar_freeze'] 受控条目=1 范围外=3
[极端1]  仅篡改被钉制品：          result=FAIL exit=2      C-4=FAIL 受控载体=0
         C-4失败=['C-4: C-4 baseline 钉值漂移：gits-core.owl.ttl 7c407bcd94d6922c != 705578d6324abd0c']
[极端2]  篡改制品 + 同步改写侧车钉值：result=INCOMPLETE exit=3 C-4=PASS 受控载体=0 C-4失败=[]
判定：C-4b（受控载体自冻结）在真实布局下 freeze_subjects 恒为 0 ⇒ 该防线不参与判定；篡改 + 改钉值后 C-4 = PASS
（仓内 DEFAULT_PINS / DEFAULT_SCAN_PINS 均位于 loops/** ⇒ 永远被判 list_artifact）
```

**我改了什么**：在 `/tmp/qa3-root` 的仓副本内 ① 给 `specs/semantic/gits-core.owl.ttl` 追加一行注释（篡改被钉制品）；
② 再把副本侧车 `baseline-v2-manifest.json` 的 `baseline.sha256` 改成新哈希（"改钉值"）。
两极端结果：**只篡改 ⇒ C-4 FAIL（钉值比对在制度上有效）；篡改＋改钉值 ⇒ C-4 转 PASS**。

**机理（回源）**：`check_c4()` `:451-452` 的 `controlled_sidecars = [p for p in sidecars if pin_scope(root,p)=="controlled"]`；
而 `pin_scope()` `:336-338` 把 `loops/**`、`evidence/**` 判为 `list_artifact`；仓内两个侧车都在
`loops/ONTO1-ontology-split/evidence/` ⇒ **`controlled_sidecars` 恒空 ⇒ `for sidecar in controlled_sidecars:` 循环体永不执行**
⇒ `C-4_PIN_FILE_UNFROZEN` 在真实制品上**不可能出现**（只有 sandbox 里把侧车放进 `specs/semantic/` 的 M12/M12b/M13 才触发）。

> **判定**：这是**已声明的空转**（输出明写「载体自冻结：受控载体 0 个，空转不计为覆盖」），
> 但**未声明的后果**是：该子检查是"**改钉值即可通过**"（规格 §4.4）的**唯一防线**，而它在真实布局下**永不生效**，
> 且**攻击面已被本实验实证可绕过**。⇒ 判 `HAS_DEAD_PATH`（恒不触发 + 后果具安全性质）。

**Q4 自检覆盖**：

```text
$ timeout 900 python3 scripts/onto1_namespace_collision_check.py --selftest
PASS M0 / M1(C-1b) / M2(C-2) / M3(C-2 陈旧) / M4(C-3) / M-元（证明 M4 真在测 C-3）/ M5(C-4 漂移) / M6(C-2 登记缺失)
PASS M7(C-1a) / M8(D3_SIGNATURE_REQUIRED) / M9(PLACEHOLDER_ROOT_REJECTED) / M10(C-2 全登记) / M11(C-4_SELF_REFERENCE)
PASS M12(C-4_PIN_FILE_UNFROZEN) / M12 对照 / M12b（扫描根之外）/ M13（取消收窄）/ M13b(C-4_NO_CONTROLLED_PIN)
PASS M15 / M15 对照 / M15b / M15c / M15c 对照 / M15d（输入闸门）/ M14(INCOMPLETE) / M0b（真实仓 ≠ PASS）
onto1-namespace-collision-selftest: PASS          EXIT=0
```

**26/26 属实**（含 `M-元` 元变异，能证明 M4 真在测 C-3；含 3 条 `restore ⇒ PASS`；含 2 条真实仓对照）。
**未覆盖的失败路径**：`C-4_PIN_SCOPE_UNCLASSIFIED`（无任何用例）、"受控制品缺失（非必需钉值）"、
`SETUP:` 兜底（未识别新 IRI 形态 / manifest 缺失）、`C-2` 登记表 `defects` 非数组。

### 2.7 `onto1_product_refs_probe.py`（★ 门禁 2）→ **HAS_DEAD_PATH**

**Q1**：`P1` cards<1 · `P2` 三个产品引用字段未在任何卡 front matter 出现 · `P3` 悬空引用 = 0；
另有 `probe()` 的 `RuntimeError`（无产品卡）→ `gate()` 早退 `return 2`。

**Q2 可达性**：**P1 不可达**（被前置 `RuntimeError` 完全遮蔽），P2/P3 可达。

**Q3 构造性实验**：

```text
$ python3 /tmp/qa3/probe_others.py
[1] onto1_product_refs_probe.py：P1（cards<1）是否可达？
onto1-product-refs: FAIL: no product cards found under /tmp/qa3-pr-…/empty     ← 走 RuntimeError 分支
  无卡片时 exit = 2（若 P1 可达，应打印 [P1] cards=0 且 stderr 含 'P1 no product cards'）
  probe() 无卡片 ⇒ RuntimeError: no product cards found under …
  ⇒ gate() 第 192 行已 return 2，第 195-196 行的 P1 分支永不可达
```

源码回源：`probe()` `:101-102` `if not cards: raise RuntimeError(...)`；`gate()` `:188-196`
先 `try/except → return 2`，`if summary["cards"] < 1: failures.append("P1 no product cards")` **永不执行**。
⇒ 登记文案 `P1 必须找到产品卡，否则 FAIL（不得"0 卡片也算绿"）` 的**具名判据是死代码**；
"无卡片 ⇒ FAIL"仍成立（由 RuntimeError 承担），故**仪器整体仍能 FAIL**，但 **P1 这个判据名是装饰**。

**真实制品输出（当前）**：

```text
$ python3 -c "...m.gate(out_dir=Path('/tmp/qa3-out-pr'))"
[P1] cards=13 product_ids=13 references=40
[P2] by_field={'prerequisite_product_ids': 12, 'complementary_products': 28} declared=['complementary_products','mutex_product_ids','prerequisite_product_ids']
[P3] by_resolution={'UNKNOWN_TOKEN': 38, 'SCHEME_MISMATCH_OTHER_VOCAB': 2} dangling=40
[P5] 零实例关系（⇒ 对应 SHACL 场景 = NOT_EVALUATED，不得包装为通过）：['mutex_product_ids']
onto1-product-refs: PASS          EXIT=0
```

**Q4 自检覆盖**：

```text
$ python3 scripts/onto1_product_refs_probe.py --selftest
PASS M1 已解析 ID 必须判 RESOLVED_PRODUCT_ID
PASS M2 悬空/跨词表取值必须被区分  {'SETTLEMENT_ACCOUNT':'UNKNOWN_TOKEN','CORPORATE_E_BANK':'SCHEME_MISMATCH_OTHER_VOCAB'}
PASS M3 无产品卡 ⇒ 门禁 FAIL  exit=2        ← 实测走的仍是 RuntimeError 路径，**未覆盖 P1**
PASS M0 对照：真实产品卡 ⇒ PASS  exit=0
onto1-product-refs-selftest: PASS
```

未覆盖：**P1（死）、P2、P3**。
**附带（副作用）**：`write_report()` `:148-150` 在传 `out_dir` 时**改写模块级 `OUT_DIR`** ⇒ `--selftest` 的 M3 会把全局
指向临时目录，使随后的 M0 也写进临时目录（本轮实测 M0 打印 `inventory=loops/…`，未造成仓内写入，但顺序耦合脆弱）。

### 2.8 `onto1_reference_alignment_check.py`（★ 门禁 2）→ SOUND

**Q1 失败码清单**（`findings.append({"code":...})`）：`REGISTRY_MISSING/UNREADABLE/SHAPE_INVALID/ENTRY_INCOMPLETE/ENTRY_MISSING/ENTRY_DRIFT` ·
`MATRIX_MISSING/EMPTY_FILE/HEADER_MISMATCH` · `CLAUSE_ROWS_BEFORE_TEXT` · `SKELETON_MISSING/NAME_INVALID/VERBATIM_SCOPE_MISSING/COLUMN_MISSING/CLAUSE_ROW_BEFORE_TEXT` ·
`TEXT_STATUS_MISSING/UNREADABLE/FIELD_INVALID/TEXT_OBTAINED_WITHOUT_RECEIPT` · `FILENAME_CONFORMANCE_HARD/UNREGISTERED` · `CONTENT_WORDING_UNALLOWED` ·
`UNREADABLE_TEXT_FILE` · `ROOT_MISSING` · **`SELF_CONTROL_FAILED`** · `NOOP_SUSPECT_LOW_FILE_COUNT/LOW_CANDIDATES/LOW_ALLOWED`；退出码 `1`=FAIL、`0`=PASS。

**Q2 可达性（真实仓）**：

```text
$ python3 scripts/onto1_reference_alignment_check.py --gate          （尾部）
allowed[rule_statement]=5
allowed_by_reason: {"ancestor_key_negation":5,"rule_statement":5,"same_line_negation":142,"section_heading_negation":2,"table_row_negation":25}
note: 守恒量：script_sha256=ac7ced83f466e349 fileset_sha256=2b285de8ce7e2122 files=4933 candidates=260 allowed=181 violations=0
note: 内置必败变异（自控）：按预期判违规 —— 合成声称：被候选正则命中=True；放行原因=None（⇒ 判违规，符合预期）
OK
```

- **内置必败变异**（`run_self_control()` `:231-241`）在**每次门禁报告固定输出**：即使真实仓 0 违规，也强制证明"检测器在线"
  ⇒ 这是本 Loop 内**唯一自带的"判据死亡检测"**，属正面实践（与 QA 第二轮 F-2/F-5 的失败形态正相反）。
- **空转下限**（`NOOP_SUSPECT_*`，`:596-604`）使"文件数/候选数/放行数任一下限不达即 FAIL"可达（当前 4933/260/181 远超下限）。

**Q3 构造性实验**：无需（无恒真声称）。**注**：真实仓 `candidates=260 / allowed=181 / violations=0` 的组合在**数值上**只能靠自控变异兜底，
但 `run_self_control()` 已把该兜底固化为**固定输出 + `SELF_CONTROL_FAILED`**，故不构成死路径。

**Q4 自检覆盖（16/16 实测）**：

```text
$ python3 scripts/onto1_reference_alignment_check.py --selftest
[ok] M0 对照 PASS  [ok] M1 FILENAME_CONFORMANCE_HARD  [ok] M2 CONTENT_WORDING_UNALLOWED  [ok] M3 CLAUSE_ROWS_BEFORE_TEXT
[ok] M4 SKELETON_VERBATIM_SCOPE_MISSING  [ok] M5 MATRIX_MISSING  [ok] M6 文本到手 PASS  [ok] M7 CONTENT_WORDING_UNALLOWED
[ok] M8 FILENAME_CONFORMANCE_UNREGISTERED  [ok] M9 REGISTRY_ENTRY_DRIFT  [ok] M10 rule_statement 放行+计数
[ok] M11/M12/M13/M14 均 CONTENT_WORDING_UNALLOWED  [ok] M15 section_heading_negation 放行
selftest: 16/16 符合预期  selftest: OK          EXIT=0
```

覆盖 9 个失败码（含 QA 第二轮 X3/X4 的反例 M13/M14）；**未覆盖**：`MATRIX_EMPTY_FILE`、`MATRIX_HEADER_MISMATCH`、`TEXT_STATUS_*`（4 条）、
`SKELETON_MISSING/NAME_INVALID/COLUMN_MISSING/CLAUSE_ROW_BEFORE_TEXT`、`REGISTRY_MISSING/UNREADABLE/SHAPE_INVALID/ENTRY_INCOMPLETE/ENTRY_MISSING`、
`ROOT_MISSING`、`UNREADABLE_TEXT_FILE`、`NOOP_SUSPECT_*`（3 条）、`SELF_CONTROL_FAILED`。
**已实证可达但无自检用例的例子**：`REGISTRY_ENTRY_MISSING`（本轮 w15 实验里一次触发 15 条）。
**断言粒度**：用例判 `verdict` 级（PASS/FAIL）+ M10/M15 附计数断言 ⇒ 与 §2.1 的"只看退出码"相比略强，但仍**不校验具体 code**。

### 2.9 `onto1_review_package_check.py`（★ 门禁 2）→ SOUND

**Q1**：`R1` 冻结件缺失/漂移 · `R2` 可签署载体缺失 · `R3` MANIFEST 缺失 / 登记 <14 / 登记项无文件 / 哈希不符；
另有 `PACKAGE` 目录缺失的早退（`:55-57`）。

**Q2 可达性**：

```text
$ python3 scripts/onto1_review_package_check.py --gate
[R1] frozen 01~12 一致 12/12
[R2] signable carriers ['13-送审函-书面复审.md', '14-书面复审决议签署页.md']
[R3] MANIFEST 登记 14 件；自洽校验完毕
onto1-review-package: PASS          EXIT=0
```

R1 由**硬编码冻结哈希**（`:26-39`）与磁盘比对 ⇒ 可达（任何改动即 FAIL）；R2/R3 由文件存在性与 MANIFEST 逐项哈希派生 ⇒ 可达。

**Q3 构造性实验**：无需（无恒真声称；M1/M2 本身即真实文件系统变异）。

**Q4 自检覆盖**：

```text
$ python3 scripts/onto1_review_package_check.py --selftest
PASS  M1 静默改动 01 ⇒ 门禁 FAIL  exit=2   （stderr: R1 frozen file DRIFTED + R3 manifest hash mismatch）
PASS  M2 删除决议签署页 ⇒ 门禁 FAIL  exit=2（stderr: R2 missing signable carrier + R3 manifest entry has no file）
PASS  M0 对照：原样包 ⇒ PASS  exit=0
onto1-review-package-selftest: PASS
```

覆盖 R1、R2（并**顺带**触发了 R3 的两条子失败）；**未覆盖**：`R3 MANIFEST.md missing`、`R3 登记 <14`、
"目录缺失"早退；断言只有 `code == 2`（未校验 codename）；**无 `try/except`** ⇒ MANIFEST 非 UTF-8 会崩溃（D-11 口径未覆盖）。

### 2.10 `onto1_consumer_scan_tests.py`（★ 门禁 1：`wi_a2_scan_mutation`）→ SOUND

**Q1**：19 条用例（T01~T05b 检出能力 / T06 无规则匹配 / T07 基线计数 / T08 基线哈希 / T09 单仓期望命中 / T10 全豁免 / T11 全 PENDING / T12 对照），
任一条 `record(..., False)` ⇒ `return 2`。

**Q2/Q3 可达性**：

```text
$ python3 scripts/onto1_consumer_scan_tests.py
PASS T01~T05b（12 条合成根检出）  PASS T06 无规则匹配⇒exit=2  PASS T07 基线类计数 31≠32⇒FAIL
PASS T08 基线哈希漂移⇒FAIL（76d38e02… != expected prefix）  PASS T09 单仓缓存⇒exit=2
PASS T10 全部豁免化⇒exit=2  PASS T11 全 PENDING⇒exit=2  PASS T12 对照：正式规则+正式缓存⇒PASS exit=0
onto1-consumer-scan-tests: 19/19 passed        EXIT=0
```

- T01~T05b 断言的是**集合成员关系**（`("owl_class","OperatingCase") in tokens`）⇒ 真检出能力检验；
- T07/T08 在 **in-process 调真函数并期望 `RuntimeError`**（非看退出码）⇒ 有牙齿；
- T06/T09/T10/T11/T12 走**子进程**并要求 `returncode != 0` **且**输出含门禁锚点（`A4`/`A3`/`A6`/`A4b`）⇒ 有锚定；
  弱点是**子串出现在合并输出中即算命中**（若崩溃信息里恰好含 `A3` 会误判为"已拦下"——当前无此形态，属残余风险而非实证缺陷）。

**Q4 自检覆盖**：本仪器**自身即变异矩阵**，无 `--selftest` ⇒ 不存在"自检未覆盖自身失败路径"的问题；
但**它自身无对照性自举**（没有"若我把 scanner 换成恒 FAIL 版本，T12 必须红"的元变异 ⇒ 与 §2.6 的 `M-元` 相比少一层保险）。

### 2.11 `onto1_w15_acceptance.py`（★ 门禁 1：`wi_w15_a3_acceptance`）→ SOUND

**Q1**：8 条用例（A/B/C/D 四组碰撞检查 + Q1a/Q1b/R1a/R1b 四组参照对齐），任一 `case.ok=False` ⇒ `return 2`；
另有"被测脚本缺失"早退。

**Q2/Q3 可达性 + 构造性实验（`violated()` 是否有判别力）**：

```text
$ python3 scripts/onto1_w15_acceptance.py
  OK  A  对照：真实副本（C-2 已修）        实测=exit=3 C-2_PASS=True C-4_PASS=True INCOMPLETE=True crash=False
  OK  B  删受控钉值文件                    实测=exit=2 具名FAIL=True crash=False
  OK  C  删范围外钉值文件                  实测=exit=2 具名FAIL=True C-4=FAIL
  OK  D  还原对照                          实测=exit=3 C-4_PASS=True
  OK  Q1a 对照（不含关键词的真实声称 X2）    实测=exit=1 判违规=True
  OK  Q1b **含主题词的真实声称 X3**         实测=exit=1 判违规=True
  OK  R1a 标题含「门禁」+ 其下真实声称 X4    实测=exit=1 判违规=True
  OK  R1b 对照：普通标题 + 同一声称 X5       实测=exit=1 判违规=True
onto1-w15-acceptance: PASS（8/8 符合预期）      EXIT=0
```

D3 组用 `violated(name) = name in out`（**"文件名出现在输出中"**）作代理。我构造两极端（`/tmp` 夹具，仓内零改动）：

```text
$ python3 /tmp/qa3/probe_w15.py
[极端1 仅放行（无违规）] exit=1  文件名出现在输出中 = False
      counter: files=1 filenames=0 candidates=1 allowed=1 registered_legacy_hits=0
      allowed_by_reason: {"rule_statement": 1}
      finding: CONTENT_WORDING_UNALLOWED 首次出现在极端2，极端1 无此 finding
[极端2 仅违规]        exit=1  文件名出现在输出中 = True
      counter: candidates=1 allowed=0 violations=1
      finding: CONTENT_WORDING_UNALLOWED {"source_ref": "/tmp/…/only-violation.md", …}
```

⇒ **`violated()` 有判别力（N 极=不可见、正例=可见），不是恒真**。这一点重要：该仪器调用被测脚本时
`--root`/`--min-*` 变了但 **registry/skeleton/matrix 仍指向真实仓路径**，导致 15 条 `REGISTRY_ENTRY_MISSING`
**与 4 条用例无关地存在** ⇒ 若它改用"退出码=FAIL"来判定，8 条用例会**全恒真**；改用"文件名出现"恰好避开了这个陷阱。

**Q4 自检覆盖**：本仪器**无 `--selftest`**（它自身即"反例 + 对照"集合）；缺陷方向已被 4 条对照（A/D/Q1a/R1b）覆盖。

### 2.12 `onto1_check_strength_audit.py`（门禁 0 / D-20 明确未登记为门禁）→ **HAS_DEAD_PATH**

**Q1 失败路径清单：没有。** `main()` 的**全部三条分支 `return 0`**：

```text
$ python3 /tmp/qa3/probe_others.py
[2] onto1_check_strength_audit.py 的出口码
  main() 中出现的 return 形式 = ['return 0']
  ⇒ 无任何 `return 2` / 非零判定出口（该仪器不可能判 FAIL）
```

**Q2 可达性**：不存在 FAIL 出口 ⇒ **"判定是否可能失败" = 否**（`--freeze` 也是 `return 0`）。
作为**报告器**这是可接受的（D-20 已明确不登记为门禁），但必须如实标注：**它不能表达失败**，
若将来有人把它接进门禁或把它当"通过"依据，则必然假绿。

**Q3 构造性实验**：`main()` 三条分支逐一静态确认 `return 0`（上）；另见问题 6（它的**输出本身有假报**，见 §4）。

**Q4 自检覆盖**：无 `--selftest`；**它自己的抽取正确性并未被任何用例检验**——本轮我用 §4 的方法补做了抽查。
（另注：`scripts/README` 无；`--freeze` 写 `check-strength-review-hashes.json`，我未运行 `--freeze`，避免动仓内文件。）

### 2.13 `onto1_pkg_audit.py`（门禁 0）→ **HAS_DEAD_PATH**

**Q1 失败路径清单**：`AU-1` handoff 缺失 / 无哈希声明 / 制品缺失 / 哈希不符 · `AU-5 RED LINE` 受控制品被动 / 超范围产物 / KERT ONTO1 写入 ·
`AU-6b` 证据板不一致 · `AU-1b` 记录声明哈希不符；任一 ⇒ `return 2`。`--recent`（AU-5m）**只打印**。

**Q2 可达性（当前实测：红）**：

```text
$ python3 scripts/onto1_pkg_audit.py --redlines
[AU-5] controlled/LERT redlines: 2 finding(s)
onto1-pkg-audit: FINDING: AU-5 RED LINE: controlled artifacts touched:
    ['specs/…/UNRESOLVED.json','specs/…/products.ttl','docs/dd/ONTO1_…复核…_20260921.md',
     'specs/…/projection-config.json','specs/…/sim/']
onto1-pkg-audit: FINDING: AU-5 KERT writes related to ONTO1:
    ['?? docs/architecture/ONTOLOGY-SPLIT-DESIGN-V1.0.md','?? docs/architecture/ONTOLOGY-SPLIT-DESIGN-V1.1-REVIEW.md']
onto1-pkg-audit: NOT_ACCEPTED（见上）      EXIT=2
```

- `redlines()` `:126-129` 把 `git status` 中任何 `specs/*` 脏项判为红线 ⇒ 而 `specs/**` 的改动**正是 Owner 2026-09-21 明确授权的 C-2/D2 SIM 整改**（`LOOP.yaml.gate_state.owner_authorization_20260921.allowed_not_blocked` 列有「C-2 修复 / 28 条关系的 SIM 投影 / 12 条关系的隔离处理」）。
  ⇒ **该判据无"授权/时间/范围"维**，在**已被授权的工作状态下必然红**，无可分辨性。
- `recent_changes()` `:192-207` **无条件 `return []`**，且调用处 `:242` **丢弃返回值** ⇒ 它作为"兜底检测"永远不产生 finding（纯打印）。
- KERT 侧判断只看**文件名含 ONTO**（`:133`）⇒ 对"历史未追认写入"与"当前新写入"**不可区分**（该二者在 B-7 里是不同处置）。

**Q3 构造性实验**：即上面的实跑（当前状态即红）。**另**：把 `--pkg ALL` 会连带 `board()`/`declared_hashes()`，我未运行（避免扩大读面）。

**Q4 自检覆盖**：**无 `--selftest`**；AU-1/AU-5/AU-1b 三条路径均无对照用例（唯一"对照"是 `--list-scopes` 的静态打印）。

---

## 3. 观察项复核（派工提示词 item 5）

### 3.1 `onto1_c2_generator_check.py:57` G0 → **fail-closed 具名出口（可达），不是死路径；但被自审仪误报为恒真**

源码 `:53-58`（注意：**不是 `except` 块，是 `if rc1 != 0 or rc2 != 0:` 的块内**）：

```text
rc1, out1 = _generate(d1, config); rc2, out2 = _generate(d2, config)
if rc1 != 0 or rc2 != 0:
    rows.append(("G0", False, f"生成失败 rc1={rc1} rc2={rc2}：…"))
    return rows
```

构造性实验（配置缺失 ⇒ 生成器 fail-closed exit 3）：

```text
$ python3 /tmp/qa3/probe_others.py
[4] 观察项1：onto1_c2_generator_check.py:57 G0 是否 fail-closed 且可达
  配置缺失时 run_checks 返回 = [('G0', False, '生成失败 rc1=3 rc2=3：INPUT ERROR: 投影配置缺失：/nonexistent-config.json')]
  ⇒ G0 为 FAIL 且短路返回 ⇒ 判 STILL OPEN / exit 2（fail-closed）
```

**结论**：G0 = **fail-closed 具名失败出口**，**可达**（同一 `_generate` 在 G7 里已被实测返回 3），
`cmd_gate()` 会把 `G0` 计入 `bad` 并 `return 2` ⇒ **判定"STILL OPEN"**，语义正确。
**它不是死路径**；但**自审仪把它标成 `TAUTOLOGY_CONST`（high）**，因为其"分支结论"豁免只覆盖
`except` 体与 `if.orelse` 体（`extract_in_func()` `:127-133`），**不覆盖 `if` 体** ⇒ **确凿假报**（详见 §4）。

### 3.2 `onto1_sim_projection.py:142` G4 → **等价于「读自我声明」，且两条文本合取项恒真**

源码 `:139-143`：

```text
ok4 = ('sim:simulationOnly true' in t1 and "NOT_AUTHORIZED" in t1
       and cfg.get("simulationOnly") is True
       and str(cfg.get("formalRelationRelease")) == "NOT_AUTHORIZED")
```

构造性实验（把配置改成相反的极端）：

```text
$ python3 /tmp/qa3/probe_others.py
[5] 观察项2：onto1_sim_projection.py G4 的文本存在性合取项是否为恒真
  配置 simulationOnly=False / release=AUTHORIZED 时：
    'sim:simulationOnly true' in 文本 = True
    'NOT_AUTHORIZED' in 文本        = True
  ⇒ 两个文本合取项与配置无关（由 build() 第 75/104 行常量字符串保证）
```

**结论**：
1. 第 1、2 合取项**恒真** —— `build()` `:104` **无条件**写入 `{inst:PREFIX}:SIM-PROJECTION sim:simulationOnly true .`；
   `:75` 的 header 注释**无条件**写入 `formalRelationRelease=NOT_AUTHORIZED`（M2 之所以仍能 FAIL，靠的是 `cfg` 那两条）；
2. 第 3、4 合取项读的是**构建输入配置**（`cfg`）⇒ **等价于「读自我声明」**，不是从投影内容推导；
3. **更强的观察**：`run_checks(config, out, tmp)` 的 **`out` 形参从未被引用**（见下），
   即 `--gate` **从不读盘上制品** `specs/…/product-relations.SIM.ttl`，`G1~G7` 全部作用在本次新建的 `/tmp/*.ttl` 上。

```text
$ sed -n '125,170p' scripts/onto1_sim_projection.py | grep -n "\bout\b"
1:def run_checks(config: Path, out: Path, tmp: Path) -> list[tuple[str, bool, str]]:   ← 仅出现在签名行
(上面若无输出 ⇒ out 未被引用)
```

**判定**：G4 = **部分死条件（2/4 恒真）+ 其余读自述** ⇒ 属 `HAS_DEAD_PATH` 形态；
（自审仪对该行标 `DECLARED_ONLY`，方向正确，但**未**指出"文本存在性恒真"与"`out` 形参未接线"两点。）

---

## 4. 问题 6：自审仪 v2 的 `226 / 15 / 13` 是否可信？（抽 3 个仪器 + 四形态复现）

### 4.1 三个数字逐字复现 ✅

```text
$ python3 /tmp/qa3/probe_audit.py
[A] scan() 复算：仪器 45 ｜可审判据 226 ｜候选 15 ｜未审 13
    by_flag = {'NOT_AUDITED': 13, 'TAUTOLOGY_CONST': 1, 'DECLARED_ONLY': 1}
    未审仪器 = ['onto1_attribution_rebuild.py','onto1_check_strength_audit.py','onto1_consumer_scan_tests.py',
                'onto1_cq_fixtures.py','onto1_d2_normalization_pack.py','onto1_d4_pack.py',
                'onto1_evidence_board_check.py','onto1_namespace_collision_check.py','onto1_pkg_audit.py',
                'onto1_product_refs_probe.py','onto1_reference_alignment_check.py','onto1_review_package_check.py',
                'onto1_w15_acceptance.py']
```

- **13 未审 = 本轮派工清单的 13 个仪器**（与 `evidence/prep/check-strength-coverage-gap.json` 的 `instruments` 集合**完全一致**）
  ⇒ 覆盖缺口声明**自洽**，没有"声称覆盖而实际未覆盖"的第三个集合。
- 15 候选 = **13 NOT_AUDITED + 1 `TAUTOLOGY_CONST` + 1 `DECLARED_ONLY`**
  ⇒ **"15 候选"里 87% 是"未审"**；把它读成"待复核的具体可疑判据"会误导。

### 4.2 抽样核对（2 元组 / dict 式 / 字符串式 / 预计算变量）

```text
$ python3 /tmp/qa3/probe_audit.py
[B] 抽样核对（脚本抽取数 vs 我人工点数）
  onto1_log_hygiene.py: checks_total=4 auditable=4 not_audited=False
      - H1 白名单按 `file` 键可读 [] | resolved=False | ("H1 …", len(allow) > 0),
      - H2 无任何已登记文件被标为删除候选 [] | … | ("H2 …", not [r for r in cand …])
      - H3 无任何白名单文件被标为删除候选 [] | … 
      - H4 白名单在案文件确实存在且白名单非空（QA-W3R2 N-1 修复：原 `or True`…）[] | … | len(allow) > 0 and all((EV_DIR / f).is_file() for f in allow…)
  onto1_namespace_collision_check.py: checks_total=2 auditable=0 not_audited=True
      - hits ['MUTANT_SCOPE','STRING_NOTE'] | for label, key_file, key_hash in (("hits","hits_file","hits_file…   ← **数据元组被误当判据**
      - summary ['MUTANT_SCOPE','STRING_NOTE'] | ("summary","summary_file","summary_sha256")):
  onto1_d4_pack.py: checks_total=0 auditable=0 not_audited=True
  onto1_breakpoint_execution_pack.py: checks_total=6 auditable=6 not_audited=False
      - X1 … X2 … X3 … X4 … X5 … X6 …
```

- ✅ **2 元组真被抽到**：`onto1_log_hygiene.py` 的 `H1~H4` 四条（QA 第二轮曾报 0 条）现**全部抽出**，且 **H4 已显示 `len(allow) > 0 and all(...)`**
  ⇒ **QA 第二轮 N-1 所指的 `or True` 修复在抽取结果中可见**。
- ⚠️ **字符串式 ≠ 被审**：`onto1_d4_pack.py`（全部用 `failures.append("C1 …")`）`checks_total=0`；
  `reference_alignment_check.py` 同型。抽取器把 `failures.append("字符串")` 记为 `STRING_NOTE` 并**排除出 `auditable`**
  ⇒ 该类仪器**必然落 `NOT_AUDITED`**（这正是 13 未审的主要成因）。
- ✅ **预计算变量真被回溯源表达式**：`resolved=True`，`expr` 显示 `ok_files = all((ROOT / n).is_file() for n in names)`
  （`breakpoint_execution_pack` 的 X2/X3/X4/X5 均如此）⇒ **QA 第二轮 N-4「审查域不含条件变量赋值」已被修复**。

### 4.3 合成源码四形态复现（决定性）

```text
$ python3 /tmp/qa3/probe_audit.py
[C] 抽取器对四种判定形态的最小复现（合成源码）
  抽取到的判据名 = ['A 二元组判据', 'B 三元组判据', 'C 列表内 dict 判据']
    A 二元组判据      [] | resolved=True | ok_files = all((ROOT / n).is_file() for n in names)
    B 三元组判据      [] | resolved=False| tup3 = [("B 三元组判据", ok_files and True, "说明")]
    C 列表内 dict 判据 [] | resolved=True | ok_files = all((ROOT / n).is_file() for n in names)
  2 元组             抽到 = True
  3 元组             抽到 = True
  dict（列表内）        抽到 = True
  dict（下标赋值）       抽到 = False     ← report["checks"]["D"] = {"status": "PASS" if …}
  failures.append 字符串 抽到 = False
```

**逐条裁决「四类是否真被抽到」**：

| 形态 | 声明 | 我的复现 | 裁决 |
|---|---|---|---|
| 2 元组 `("名", cond)` | 覆盖 | `True`（log_hygiene H1~H4） | ✅ **成立**（修好了 Q2 的 1 号成因） |
| 3 元组 `("名", cond, "说明")` | 覆盖 | `True` | ✅ 成立 |
| dict 式 | 覆盖 | **列表/元组内的 dict = True；`x[k] = {...}` 下标赋值 = False** | ⚠️ **部分不成立**（`onto1_namespace_collision_check.py:596-641` 正是下标赋值形态 ⇒ 承载登记门禁的 C-1..C-4 判定**整机仍不可见**） |
| 字符串式 `failures.append("…")` | 覆盖 | 仅登记 `STRING_NOTE`，**不计入 `auditable`** | ⚠️ **不等于"被审"**（"抽到"仅指被记录；判据本体仍未被审） |
| 预计算变量 `ok = <expr>` | 覆盖 | `True`（`resolved=True`，回溯源表达式） | ✅ 成立（修好了 Q2 的 4 号成因） |

### 4.4 两类「假」（假报 / 假计数）

**(a) 确凿假报：`onto1_c2_generator_check.py:57` G0 → `TAUTOLOGY_CONST`（high）**

我已独立证明 G0 是**可达的 fail-closed 具名出口**（§3.1 实验）⇒ 该 high 级报项**为假**。
成因：`extract_in_func()` 的分支结论豁免只收集 `ExceptHandler.body` 与 `If.orelse`（`:127-133`），**漏了 `If.body`**；
G0 正位于 `if` 体内。⇒ **自审仪的"high 候选"不可直接采信**（本轮 2 条非 `NOT_AUDITED` 候选中，1 条即此项）。

**(b) 假计数：数据元组被登记为判据**

```text
$ python3 -c "…统计 check-strength-audit.json…"
STRING_NOTE（被识别为"记录非判据"）条数= 15
    ('onto1_migration_worklist.py','B2','(("B2","L1_L2_语义规格层"), ("B4","L3_运行本体"), …')   ← 批次表数据
    ('onto1_migration_worklist.py','B4', …)  ('B7', …)  ('B8', …)
    ('onto1_review_package_build.py','onto1_class_reconciliation','pairs = [("onto1_class_reconciliation","wi_class_reconcilia…')  ← 门禁—脚本对照表
    ('…build.py','onto1_construction_plan', …) ('onto1_l1_prep', …) ('onto1_c2_generator_check', …) ('onto1_c2_fix_verify', …) ('onto1_sim_projection', …)
```

这 15 条**都不是判据**（批次表/门禁对照表的**数据元组**），被 `STRING_NOTE` 规则兜住、排除出 `auditable`（故 226 未失真），
但 `checks_total` 被抬高（如 collision 的 `checks_total=2` **全部**是数据元组）⇒ **`checks_total` 不能当"判据条数"读**。

### 4.5 问题 6 裁决

| 项 | 裁决 |
|---|---|
| `226 条可审判据` | **数字可复现**；因 `STRING_NOTE` 15 条被排除、且分支结论误删风险存在，**"226"的语义是"抽到且非字符串常量"**，不等于"226 条都值得看" |
| `15 候选` | **数字可复现**，但 **13/15 是"未审"占位**、1/15 是**假报**（G0）⇒ 该数字**不可作为"本 Loop 判据已体检"的依据** |
| `13 未审` | **诚实且自洽**（= 本轮 13 仪器 = 覆盖缺口清单）⇒ 这是 v2 相对 v1 的**实质进步**，应予采信 |
| 「四类形态真被抽到」 | **部分不成立**（下标赋值 dict / 字符串式两类**未作为判据被审**）⇒ 该声明需改为「抽到 2 元组 / 3 元组 / 列表内 dict / 预计算变量；下标赋值 dict 与 `failures.append` 字符串仅登记」 |

---

## 5. 本轮新发现（我亲自复现；按严重度排序）

| # | 级别 | 发现 | 证据 |
|---|---|---|---|
| **S-1** | **高（阻塞板面可信性）** | **注册门禁 `wi_a5_d2_pack` 在当前树实测 FAIL（exit 2），`wi_a5_d2_pack_selftest` 实测 FAIL（M0+M1）；板面仍记 `pass`（83/0/1）** | §2.3 两次独立执行 + `verify_all_refs` 独立复算=5 条 + `stat` 时间线（制品 12:33 / products.ttl 21:41）+ 全仓 grep 无登记 |
| **S-2** | 高 | `onto1_cq_fixtures.py` 的 `--gate` **先按常量重生成 6 份夹具再校验** ⇒ Q1~Q5 **五条失败路径在真实制品上永不可达**，且 `--gate` 会**静默擦除**人工改动 | §2.2 两极端实验（33 条违规 → gate 仍 PASS 并把破坏写回） |
| **S-3** | 高 | `onto1_namespace_collision_check.py` 的 `C-4_PIN_FILE_UNFROZEN` 在真实布局下**恒不触发**（`controlled_sidecars` 恒空），而它是"**改钉值即可通过**"的唯一防线 ⇒ **篡改制品＋改钉值后 C-4 转 PASS** | §2.6 攻防实验（对照 C-4=PASS/受控载体=0 → 篡改 FAIL → 篡改+改钉值 PASS） |
| **S-4** | 中 | `onto1_d2_normalization_pack.py` 的 **G8 恒真**（第 1 合取项硬编码、第 2 合取项自指）⇒ 「R-6 保留」从未被校验 | §2.3 删除唯一的 R-6 保留项后 G8 仍 PASS |
| **S-5** | 中 | `onto1_product_refs_probe.py` 的 **P1 判据是死代码**（被 `probe()` 的 `RuntimeError` 遮蔽） | §2.7 无卡片路径实测未进入 P1 |
| **S-6** | 中 | `onto1_pkg_audit.py` 的 **AU-5 红线在"Owner 已授权 SIM 整改"状态下实测永红（exit 2）且不可分辨**；`recent_changes()` 恒 `return []` | §2.13 原始输出 |
| **S-7** | 中 | `onto1_check_strength_audit.py` **无任何 FAIL 出口**（`main()` 全分支 `return 0`） | §2.12 |
| **S-8** | 中 | 自审仪**假报**（G0→`TAUTOLOGY_CONST`）与**假计数**（15 条数据元组被登记为判据）；`下标赋值 dict`/`字符串式` **未作为判据被审** | §4.3 §4.4 |
| **S-9** | 低-中 | `onto1_attribution_rebuild.py` 的 **A1 被前置哈希闸门遮蔽**（近似死路径）；且三条变异只断言 `exit == 2`，**无判据级归属** | §2.1 |
| **S-10** | 低 | `onto1_d2_normalization_pack.py` 的 **M1 用绝对计数**（`len(problems)==2`）⇒ 基线不干净时连带 FAIL（本日实测 M1 红） | §2.3 Q4 |
| **S-11** | 低 | `onto1_d4_pack.py` `gate()` 打印块用**直接下标** ⇒ 畸形机读包**崩溃**（JSONDecodeError/KeyError）而非具名 FAIL（D-11 口径） | §2.4 |
| **S-12** | 低 | `onto1_product_refs_probe.py` `write_report()` **改写模块级 `OUT_DIR`** ⇒ `--selftest` 的用例间存在顺序耦合 | §2.7 Q4 附注 |
| **S-13** | 低 | `onto1_sim_projection.py` 的 `run_checks(config, out, tmp)` 的 **`out` 形参从未被引用** ⇒ `--gate` 不读盘上 SIM 制品；G4 两条文本合取项恒真 | §3.2 |

---

## 6. 我这一轮的副作用（自证无漂移）

```text
$ find loops/ONTO1-ontology-split scripts specs generated docs/dd -type f | sort | xargs sha256sum  （开工/收工两次）
diff /tmp/qa3-before-sha.txt /tmp/qa3-after-sha.txt
  → 仅 scripts/__pycache__/*.pyc 变动（Python 字节码缓存，**非制品、git 不跟踪**）
$ diff /tmp/qa3-before-status.txt /tmp/qa3-after-status.txt
  → **完全一致（0 新增/删除/修改）**
```

如实披露：
1. 为运行实验导入模块，Python 再生成了 `scripts/__pycache__/*.pyc`（gitignore、非制品）；**受控与登记制品 0 漂移**（git status 逐字一致）。
2. 所有会写制品的门禁我**改用只读等价入口**（`gate(write=False)` / `gate(out_dir=/tmp)`），**未触碰仓内制品**（尤其
   `d2-normalization-pack.json` 与当前构建**不一致**，若直跑注册命令会改写它——已避开）。
3. **未运行** `onto1_gate_log.py` 包装器（会新增/改写 `evidence/*.log`，进而影响证据板门禁与 `output_sha256`）。
4. **未运行** `onto1_check_strength_audit.py --scan/--freeze` 的写盘路径（改为 in-process 调 `scan()`，只读）。
5. 未运行 `onto1_a3_closeout.py --build`、未跑 `make generate`（Wave -1 只读）、未改 `specs/**`/`generated/**`/任何脚本。
6. **KERT 零写入**（本轮对 `/home/szf/dev/Leibniz-KERT` 只有读取；`probe_collision.py` 的副本全部落在 `/tmp/qa3-root`）。
7. 临时实验脚本全部落 `/tmp/qa3/`（`probe_cq.py` / `probe_d2.py` / `probe_d2b.py` / `probe_others.py` / `probe_board.py` / `probe_audit.py` / `probe_collision.py` / `probe_w15.py`），**未入仓**。

---

## 7. 关于 `QA_PASS`

**我不得、也未记录 `QA_PASS`。** 客观理由（非我裁量）：

1. 板面仍有 **1 项 `inconclusive`**（`wi_a4_namespace_collision`，exit 3，`C-1b` 待 D3 签署根域）——**未判定 ≠ 通过**；
2. **本轮新增实测**：`wi_a5_d2_pack` 与 `wi_a5_d2_pack_selftest` 在当前树上为 **FAIL（exit 2）**，与板面 `pass` 冲突（**S-1**）：
   按 `board_expression_rule`，`FAIL` 不得解释为 `PENDING_EXTERNAL_AUTHORITY`；
3. `LOOP.yaml.gate_state.current` 仍为 **`RETURN_TO_HLD`**；Wave 0 及以后仍 `BLOCKED`；
4. 本轮判 **6 条 `HAS_DEAD_PATH`**（S-2/S-3/S-4/S-5/S-7/S-6），其中 **S-2（整机 5 条失败路径失效）与 S-3（防线恒不触发且可绕过）**具实质意义；
5. 自审仪的 **`15 候选`不可采信**（13 条是"未审"占位、1 条 G0 为假报）⇒ 「判据已体检」的叙事不成立。

**给下一 holder 的建议（均为建议，非结论，且我未执行任何修改）**：
① **重跑并重记** `wi_a5_d2_pack`（+selftest）：先按 C-2 后的 `products.ttl` 重锚（或改用"标签唯一性"而非"行号+行内容"锚定），再重记；同时核对该类
   「行号绑定证据」是否还影响其他门禁（同类风险面：任何把 `文件:行` 写进判据的仪器）；
② `onto1_cq_fixtures.py`：把 `--gate` 拆成**只读校验入口**（`write=False`）+ 独立 `--build`；`Q1~Q5` 必须有"盘上制品被改动 ⇒ FAIL"的用例（否则登记证据可被静默擦除）；
③ `onto1_namespace_collision_check.py`：要么把**真实侧车**纳入 `controlled`（例如在 `specs/semantic/` 侧留受控钉值载体），要么把 C-4b 的**空转声明升级为"防线缺失"告警**（现文案只说"不计为覆盖"）；
④ `onto1_d2_normalization_pack.py` G8：把「R-6 保留」改为**对独立字段**的断言（如 `prohibited_actions` 必须含该项），不得用声明文本自我满足；M1 改增量断言（`delta == 2`）；
⑤ `onto1_product_refs_probe.py` P1 / `onto1_check_strength_audit.py` 无出口 / `onto1_pkg_audit.py` AU-5：分别改"可达判据 / 加退出码 / 加授权维或时间维"；
⑥ 自审仪：`extract_in_func()` 的 branch 豁免补 `If.body`；白名单/计数报告区分 `checks_total`（含数据元组）与 `auditable_total`；把"下标赋值 dict"与"字符串式"两类显式标为**未覆盖**而非"已覆盖"。

---

## 8. 未覆盖 / 边界声明

- 本轮**只做**派工清单的 13 个仪器的**失败路径可达性**（四问）+ 2 项观察 + 问题 6 抽查；
  **未重复** QA 第二轮已完成项（F-1~F-12、⑤⑧⑨⑩、N-1~N-6）。
- **未做**：`docs/**` 与 KERT 侧文档的语义正确性；A-1~A-17 其余仪器的判据强度；`wi_a2_disposition`/`wi_a3_closeout`/`wi_c2_*`/`wi_l1_prep`/`wi_a8~a17` 仪器的违规点分析；
  前端与后端运行期行为；外部依赖（D1/D2/D3/D4、KERT 写权限、委员会签署页）。
- **未改判**既有 84 门禁的 `status`（**S-1 的红是我实测的原始结论，是否重记由 holder 决定**；我未触碰 `EVIDENCE.json`）。
- 与 `specs/**` 冲突时以 `specs/**` 为准；本报告引用均给 `文件:行` 或 sha256。
- 派工提示词中「门禁 2 / 门禁 1 / 门禁 0」与 `check-strength-coverage-gap.json` 的 `gate_count` 我**已逐项比对一致**（13 仪器 / 20 个登记门禁）。

---

**报告完** ｜ 生成者：`independent_qa`（第三轮 / W3R3 定向覆盖）｜ 唯一写域：本文件 ｜ 未记 `QA_PASS`、未代签、未改任何制品、KERT 零写入
