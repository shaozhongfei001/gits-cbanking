# 独立 QA｜ONTO1 第四轮（W3R4）独立复核报告

> 角色：`independent_qa`（**第四轮**）｜会话标签 `qa-w3r4`｜日期 **2026-09-22**
> 写域（**唯一**）：本文件 `loops/ONTO1-ontology-split/memory/handoffs/INDEPENDENT-QA-W3R4-2026-09-22.md`
> 只读：`/home/szf/dev/gits-cbanking` 全仓 + `/home/szf/dev/Leibniz-KERT`（**KERT 零写入，实测 0**）
> **不采信 TL 任何结论**：本报告全部数字与判定均由本人现场复算/构造实验得出，逐条附命令与原始输出。
> **未记录 `QA_PASS`**；未改任何 TL 脚本与报告；未代签；未改 `specs/`·`generated/`·`docs/dd/`·封版制品。

---

## 0. 独立性声明与开场

**三条独立性硬条件（同时满足）**：

| # | 条件 | 本人情况 |
|---|---|---|
| ① | 非实现方 | 未参与 ONTO1 任何仪器/门禁/制品实现；本会话对其**只读**（唯一例外见 §7 披露的仪器自身副作用） |
| ② | 非本汇报方 | 未参与 `INDEPENDENT-QA-W3/W3R2/W3R3`、`TL-ADJUDICATION-QA-W3*` 的编写 |
| ③ | 非临时兼任 PSO/ICO 者 | 未持有 O-02/O-03 临时任命（持有人在 `ROLE_BOARD.yaml` 记为本项目 Owner） |

```
[开工] Loop: ONTO1-ontology-split, 角色: independent_qa(qa-w3r4), Baton: tech_lead（我已在 parallel_allowed 内）, Gate: RETURN_TO_HLD
[索引] INDEX_STALE(13) @ merge 2026-09-15T17:50:17Z (gits 71169042 / kert 64f6f873)
[索引] 候选影响面: scripts/onto1_*.py ×45 · loops/ONTO1-ontology-split/{EVIDENCE.json,evidence/**} · specs/knowledge-architecture/instances/product/**
[回源] scripts/onto1_d2_normalization_pack.py:698-726 确认位移容忍实现；scripts/onto1_cq_fixtures.py:159-180 确认 gate 只读盘
```

`make index-status` 实测（原始输出）：

```
WARN: F1 索引轻微漂移：merge-meta.json 落后 HEAD 13 个提交（阈值内，收工声明 STALE(13)）
WARN: F1 索引轻微漂移：meta.json 落后 HEAD 13 个提交（阈值内，收工声明 STALE(13)）
ua_index_gate: WARN (nodes=5106, drift={'merge-meta.json': 13, 'meta.json': 13})
```

**审计基线（版本绑定，务必带走）**：

| 对象 | 审计时点哈希（sha256 前 16 位） | 备注 |
|---|---|---|
| `git HEAD`（开工） | `337de5db` | 开工基线 |
| `git HEAD`（收工时实测） | `32924bb4` | **审计期间被推进**，见 §2.2 |
| `scripts/onto1_d2_normalization_pack.py` | `8e2baa9f9c11df39` | A1/A4/A6 被测版本；审计期间未变 |
| `scripts/onto1_cq_fixtures.py` | `1784ac8942dc760b` | A2 被测版本；未变 |
| `scripts/onto1_sim_projection.py` | 审计前段 `c59ac2d08a30078d` → **12:29:54 被改为 `0f5406c771cda94d`** | A3 **须版本绑定**（两版均已测，见 §1.3） |
| `scripts/onto1_check_strength_audit.py` | `c82511c2ef04c569` | A5 被测版本；未变 |
| `scripts/onto1_namespace_collision_check.py` | `097864d4ff922854` | C1 被测版本；未变 |
| `scripts/onto1_product_refs_probe.py` | `6fac6d57fe40863c` | C2 被测版本；未变 |
| `scripts/onto1_pkg_audit.py` | `a95b5c9480fe6170` | C3 被测版本；未变 |
| `EVIDENCE.json` 板面 | **84 = 83 pass / 1 inconclusive**（唯一非 pass = `wi_a4_namespace_collision`，exit 3） | 本人现场复算，与题面一致 |
| `LOOP.yaml.gate_state.current` | `RETURN_TO_HLD` | 本人现场读取 |
| `EVIDENCE.json.independent_qa` | `report_received（**非** QA_PASS）`，`actor=independent_qa` | 未预填、未被代签 |
| 盘上 SIM 制品 `product-relations.SIM.ttl` | 审计前段 `6fc33da2151a01a5` → 收工 `d63f504ba4ab6418` | 12:29:15 被重生成（28→30 条），见 §2.2 |

---

## 1. A 块｜对本轮（QA-3 受理）4 条修复的**构造性**复核

### 1.0 复算证据的一致性底座（先做，后逐项判定）

```bash
$ python3 - <<'EOF'   # 全量核对 EVIDENCE.json 登记的 output_sha256 vs 日志实测哈希
... 对 84 个门禁逐条 hashlib.sha256(evidence_file) == output_sha256 ...
EOF
total with declared hash=84 match=84 missing=0
```

⇒ **84/84 相符**（含本轮重记的 `wi_a5_d2_pack`）。此底座成立后，才谈"结论是否换口径"。

---

### 1.1 A-1｜S-1 位移容忍的**三向判别力**（`verify_ref`）

**被测**：`scripts/onto1_d2_normalization_pack.py:698-726`（`verify_ref`），gate 记账打印在 `:1032-1033`。

**方法**（**仓内零写入**）：把 `CANDIDATES`+`SEMANTIC_HITS` 引用的 **20 个真实文件**复制进临时树，`importlib` 加载模块后把 `mod.ROOT`/`mod.KERT` 指向临时树，再对**真实锚点**（`PROD-CM-001.md:26`，`expect='requiredAccountRelationship: SETTLEMENT_ACCOUNT'`，文件内唯一命中）做四组构造：

```bash
$ python3 /tmp/qa4/a1_verify_ref.py
refs total = 78
临时树已建：20 文件 -> /tmp/qa4-a1-m16sw3m3
[M0 对照] 临时副本全量 verify_all_refs：问题 0 位移 0
选用锚点：CAND/SETTLEMENT_ACCOUNT/（非产品）账户关系取值
  ref=.../PROD-CM-001.md:26   expect='requiredAccountRelationship: SETTLEMENT_ACCOUNT'  唯一命中行=26
PASS  (a) 只位移 +2 行 ⇒ 必须 PASS 且记账「位移已记账」
      返回: None
      位移记账: [".../PROD-CM-001.md:26 → :28（expect='requiredAccountRelations'）"]
      G4 打印形态：~ 位移已记账：.../PROD-CM-001.md:26 → :28（expect='requiredAccountRelations'）
PASS  (b) 删除锚点期望内容 ⇒ 必须 FAIL，语为 line content lost
      返回: "line content lost: .../PROD-CM-001.md:26 expected 'requiredAccountRelationship: SETTLEMENT_ACCOUNT'"
PASS  (c1) 复制成两份（副本置顶）⇒ 必须 FAIL，语为 ambiguous anchor
      返回: "ambiguous anchor (2 matches) : .../PROD-CM-001.md:26 expected 'requiredAccountRelationship: SETTLEMENT_ACCOUNT'"
PASS  (c2) 复制成两份（副本追尾，主行未动）⇒ 观察
      返回: None（**PASS**）
结论(a/b/c1/c2) = {'a': 'PASS', 'b': 'PASS', 'c1': 'PASS', 'c2': 'PASS'}
```

**判定**：**`ACCEPT_WITH_CONDITIONS`**

- (a)(b)(c) **三向判别力成立**：位移 ⇒ PASS+记账；内容丢失 ⇒ `line content lost`；歧义 ⇒ `ambiguous anchor (2 matches)`。三条失败语与题面要求**逐字一致**。
- **条件（新发现，须写进仪器或文档）**：判据是**顺序相关**的——`verify_ref:716` 先做"精确行号命中即返回 None"的**短路**，只有短路失败后才做全文件搜索。因此：
  - 若**主锚点行未位移**、仅在他处出现第 2 份同样内容 ⇒ **PASS**（(c2) 实测）；
  - 只有在**主锚点行已错位**的前提上出现 ≥2 份 ⇒ `ambiguous anchor`（(c1) 实测）。
  这一短路**可辩护**（锚点仍精确解析到声明行，语义上引用未失效），但"复制成两份必然 FAIL"的字面表述**不成立**；若改成无条件歧义检测，则任何**合法重复行**（如 13 张卡共有的 `requiredAccountRelationship: SETTLEMENT_ACCOUNT`）都会把门禁判红 ⇒ 属于设计取舍，须由 TL 决定并在仪器注释中明示，不得留作隐含行为。
- 附：`ANCHOR_DRIFT` 为模块级 list，`gate()` 在 `:1027` 先 `clear()` 再累计，**不会跨次调用污染**（已读源码确认，非采信）。

---

### 1.2 A-2｜`cq_fixtures` 只读盘 + 篡改必红 + 唯一重生成入口

```bash
$ python3 /tmp/qa4/a2_cq_fixtures.py      # 全部在 /tmp 副本内操作
[1] 完整副本（未篡改）⇒ exit = 0
[2] 篡改 CQ2.status=PASS ⇒ exit = 2
    onto1-cq-fixtures: FAIL: Q3 CQ2 must not claim PASS during design phase
    onto1-cq-fixtures: FAIL: Q4 CQ2 is blocked by D4 ⇒ status must be NOT_EVALUATED, got PASS
    gate 运行前后目录内容哈希一致（未写回）= True
[3] 删 CQ4.mutation + 清空 CQ5.negative ⇒ exit = 2（Q2/Q5 四条失败语齐出）
[4] 删 CQ6.json ⇒ exit = 2（Q1 missing fixture files: ['CQ6']）
[5] 重生成入口扫描：write_fixtures 调用点
    265: write_fixtures(OUT_DIR)        ← 仅 --build 分支
    270: return gate(OUT_DIR, write=False)   ← 默认/--gate 路径
```

**判定**：**`ACCEPT`**

- 盘上篡改 ⇒ **必红**（Q3/Q4/Q1/Q2/Q5 五类拒绝路径**全部实测可达**，与 QA-3 所述"原先永不可达"相反）。
- **不写回**：运行前后 6 份夹具内容哈希完全一致（证明只读）。
- **唯一重生成入口 = `--build`**（`:265`）；`main()` 的默认路径与 `--gate` 均为 `write=False`（`:270`）。

**条件（3 条，均不改判）**：
1. `gate(write: bool = False)` 的 `if write: write_fixtures(target)`（`:167-168`）**仍留在代码里**，只是 CLI 不再传 `True` ⇒ 建议删除该分支，防止未来被程序化误用重新引入"先写后校验"。
2. `--gate` 开关在 `main()` 中**被解析但未被使用**（`:259` 定义，`:264/268/270` 均不读 `args.gate`）⇒ `--gate` 与无参行为等价；不影响结论，但属接口噪声。
3. 反例 M4/M5 的临时目录命名含 `onto1-cq-tamper-`，与生产路径可区分（已读源码）。

---

### 1.3 A-3｜`sim_projection` 篡改盘上制品 ⇒ **只有 G8** 失败

被测函数：`run_checks(config, out, tmp)`，新增判据在 `scripts/onto1_sim_projection.py`（原 `:167-174`）。

```bash
$ python3 /tmp/qa4/a3_sim_projection.py          # 被测版本 c59ac2d0（12:29:54 前）
盘上 SIM 制品 = specs/.../sim/product-relations.SIM.ttl sha256 = 6fc33da2151a01a5
[1] 对照：未篡改副本 ⇒ 未过 = 无 (8/8)
[2] 篡改盘上副本（删 simulationOnly 声明行）⇒ 未过 = ['G8']
    G8: **盘上制品**与重新生成逐字节一致（真读盘；失败码 SIM_ARTIFACT_DRIFT）；盘上=a6ec25589790922f 重生成=6fc33da2151a01a5 ⇒ **不一致/缺失**
    恰为 ['G8'] ? True     失败语含 SIM_ARTIFACT_DRIFT ? True
[3] 追加一行无关内容（内容漂移）⇒ 未过 = ['G8']
[4] 盘上制品缺失 ⇒ 未过 = ['G8']（fail-closed）
```

**审计期间该文件被 HEAD 覆盖**（`337de5d`→`32924bb`，见 §2.2），故对 **HEAD 版本**（`0f5406c771cda94d`，含新增 G9/G10）**重跑**：

```bash
$ python3 - <<'EOF'   # 对 HEAD 版本重跑，out 用 /tmp 副本
被测版本 sha256 = 0f5406c771cda94d
盘上 SIM 制品 sha256 = d63f504ba4ab6418
[HEAD 对照] 未篡改: 全 PASS (10/10)
[HEAD 篡改盘上副本] 未过 = ['G8'] | 恰为 ['G8'] ? True
    G8 : ... 盘上=8f0067f8121ff1ec 重生成=d63f504ba4ab6418 ⇒ **不一致/缺失**
```

**判定**：**`ACCEPT_WITH_CONDITIONS`**

- 结论成立且**跨两个版本都成立**：盘上制品被篡改/缺失 ⇒ **只有 G8 失败**，且失败语含 `SIM_ARTIFACT_DRIFT`；未篡改 ⇒ 全绿（8/8 → 10/10）。QA-3 的 `out` 未读缺陷**确已封闭**。
- **条件 1（版本绑定，最关键）**：我的 A-3 判定对**两个不同版本**分别成立（`c59ac2d0` / `0f5406c7`），但**必须绑定哈希表述**——因为 `scripts/onto1_sim_projection.py` 在**我审计过程中**被改写（12:29:54）并随后进入 commit `32924bb`。任何"已复核"的声明若不带哈希，在下一次写入后即失效。
- **条件 2（G8 的语义边界）**：G8 只回答"盘上 == 重新生成"，即**一致性**，不回答**授权/冻结**。若配置与制品**被一致地同时改动**（例如按新配置重生成并提交），G8 仍然绿。因此 G8 **不能**替代"制品冻结/授权变更"判据（本轮 HEAD 的 28→30 恰是这种授权变更：`product-relations.SIM.ttl` 在 8 分钟内换了 3 个哈希）。
- **条件 3**：HEAD 版本新增 G10（`UNRESOLVED.json` 盘上一致性，失败码 `SIM_UNRESOLVED_DRIFT`）——与 G8 同属"盘上 vs 重算"，两者都会在**未同步重生成**时报红；我本次**未**对 G9/G10 做变异复验（不在本轮清单内），不构成对它们的判定。

---

### 1.4 A-4｜D2 包 G8 结构断言的判别力（去 R-6 / 声明截短）

```bash
$ python3 /tmp/qa4/a4_d2_g8.py            # gate(out_dir=/tmp/...)，仓内零写入
prohibited_actions = ['以本包充当产品 Owner 裁定', ..., '关闭 R-6 风险登记']   （6 条）
no_ruling_declaration 字数 = 146
[1] 对照（未改动 pack）                exit=0  [G8] ... 含 R-6=True ⇒ PASS
[2] 去掉 prohibited_actions 中 R-6 项   exit=2  [G8] prohibited_actions 5 条，含 R-6=False ⇒ FAIL
[3] 声明截短到 7 字（保留「不含裁定」） exit=2  [G8] 非裁定声明（7 字）⇒ FAIL
[4] 声明缺「不含裁定」字样（41 字）     exit=2  ⇒ FAIL
[5] prohibited_actions 少于 5 条        exit=2  ⇒ FAIL
[6] prohibited_actions 改成非列表       exit=2  ⇒ FAIL
```

**判定**：**`ACCEPT`** — 原自指缺陷（`"R-6" in json.dumps(pack)` 被第 1 合取项自己的文本自证）**已消除**：现判据拆成 4 个独立结构条件（声明为 str ∧ 长度 ≥40 ∧ 含"不含裁定" ∧ `prohibited_actions` 为 list ∧ 条数 ≥5 ∧ 任一条含 `R-6`），**每条都能单独被打红**（上表 3/4/5/6 分别证明长度、关键词、条数、类型四条手臂）。`gate` 明细同时打印声明字数与条目数，可人工复核。

---

### 1.5 A-5｜自审仪 v2 复算（227/14/13）+ `--strict` + `c2_generator_check:57` 误报

```bash
$ python3 /tmp/qa4/a5_strength_audit.py   # 已把 mod.OUT 改写到 /tmp，避免改仓内制品
真实 OUT（未被本次运行触碰）= /tmp/qa4/check-strength-audit.json
FROZEN = .../evidence/prep/check-strength-review-hashes.json 存在 = True

[复算] 仪器 = 45 可审判据 = 227 候选 = 14 未审仪器 = 13
分类计数 = {'NOT_AUDITED': 13, 'DECLARED_ONLY': 1}
not_audited 清单 = ['onto1_attribution_rebuild.py', 'onto1_check_strength_audit.py', 'onto1_consumer_scan_tests.py',
 'onto1_cq_fixtures.py', 'onto1_d2_normalization_pack.py', 'onto1_d4_pack.py', 'onto1_evidence_board_check.py',
 'onto1_namespace_collision_check.py', 'onto1_pkg_audit.py', 'onto1_product_refs_probe.py',
 'onto1_reference_alignment_check.py', 'onto1_review_package_check.py', 'onto1_w15_acceptance.py']

[G0 误报检查] onto1_c2_generator_check.py：auditable=9 not_audited=False
    :57 'G0' flags=['BRANCH_CONCLUSION'] expr=rows.append(("G0", False, f"生成失败 rc1=..."))
    :91 'G7' flags=[]  :85 'G6' flags=['BRANCH_CONCLUSION']
  flagged 中是否有 c2_generator_check： []
[--strict 退出码]  exit = 2   输出：'# --strict：high 候选 13 / 未审仪器 13 ⇒ FAIL'
[对照：默认无 --strict]  exit = 0
```

**判定**：**`ACCEPT`**

- **227 / 14 / 13 逐项复算一致**（可审判据 227、候选 14、未审仪器 13；候选 = 13 `NOT_AUDITED` + 1 `DECLARED_ONLY`）。
- `--strict`：high 候选 13（= 13 个 `NOT_AUDITED`）或未审 >0 ⇒ **exit 2**（实测）；默认 **exit 0** 属 D-20 明示的设计（本仪器不登记为门禁）。
- **`onto1_c2_generator_check.py:57` G0 误报确已消除**：现标 `BRANCH_CONCLUSION`，且**不出现在 flagged 清单**中（判据来源是 `:51-58` 的 fail-closed 分支，QA-3 已判其可达，我采信其"可达"结论但**独立验证了"不再作为候选出现"**这一机器事实）。
- **条件 1（新增，属我实测的副作用）**：`--scan`/`--strict`/`--freeze` 都会**改写 `evidence/prep/check-strength-audit.json`**（`main():321` 无条件 `OUT.write_text`）。我本次是把 `mod.OUT` 指到 `/tmp` 才做到仓内零写入 ⇒ **该仪器"运行即改制品"**，建议提供 `--out`，并纳入 D-11（报告产物的 mtime/哈希漂移会让"证据绑定"失真）。
- **条件 2（口径提醒）**：`NOT_AUDITED` 的 13 个仪器**恰好覆盖 QA-3 手工审过的那批**（含 `namespace_collision_check`/`product_refs_probe`/`pkg_audit`）⇒ 该仪器**不能**替代人工审；`--strict` 常红是**预期**而非缺陷（其"high"里 13 条全是"抽不到判据"）。这解释了为什么"13 个 NOT_AUDITED"与"13 个 SOUND/HAS_DEAD_PATH 人工裁定"是**同一批对象**（B 块进一步量化）。

---

### 1.6 A-6｜TL 是否把 FAIL 换口径（`wi_a5_d2_pack` 重记是否真"复算通过"）

```bash
$ python3 /tmp/qa4/a6_d2_rerecord.py
登记：status = pass | exit_code = 0 | executed_at = 2026-09-22T03:51:37.738346+00:00
日志 = loops/ONTO1-ontology-split/evidence/wi_a5_d2_pack-20260922T035137Z.log
A6-1 output_sha256 == sha256(日志文件) ? True  (bc5c7cd3b73a5319)
A6-2 日志首行是否 '# artifact=' ? False | 首行 = 'COMMAND=python3 scripts/onto1_d2_normalization_pack.py --gate'
     日志中是否存在 '# artifact=' ? False

A6-3 独立复跑 gate：exit = 0
    [G1] occurrences=40 by_field={'prerequisite_product_ids': 12, 'mutex_product_ids': 0, 'complementary_products': 28} distinct=12 cards=13 ⇒ PASS
    [G4] 回源位置校验：78 条（含语义命中），问题 0，**锚点位移 0 处**（唯一命中才容忍；0 命中/歧义一律 FAIL）⇒ PASS
    [G8] 非裁定声明（146 字）与 R-6 保留（prohibited_actions 6 条，含 R-6=True）⇒ PASS
    [out] /tmp/qa4/d2out/d2-normalization-pack.json sha256=f03d7320e2f8e097
    onto1-d2-pack: PASS

A6-4 登记 STDOUT 与本次复算 stdout 的差异行数 = 3（仅 [out] 路径行 + 末尾空行）
A6-5 盘上 pack sha256 = eab6ffcb4a381cb7 | 本次复算 pack sha256 = f03d7320e2f8e097 | 一致 = False
      登记日志 [out] 行 = ['[out] loops/.../evidence/d2-normalization-pack.json sha256=eab6ffcb4a381cb7']
```

**判定**：**`ACCEPT_WITH_CONDITIONS`**

- **未换口径（核过）**：`status=pass` ∧ `exit_code=0` ∧ 日志内 `EXIT_CODE=0` ∧ **我独立复跑 exit=0** ∧ G1/G4/G8 明细与登记日志**逐行一致**（唯一差异是我把产物写到 `/tmp` 造成的 `[out]` 路径行）。**不是**把 FAIL 记成 `PENDING_EXTERNAL_AUTHORITY` 之类的换口径。
- `output_sha256 == sha256(日志)` **成立**（并把该核验扩到全量 84 门禁：**84/84** 相符）。
- **条件（题面要求项在事实上不存在）**：题面要求"核对证据日志**首行 `# artifact=`**"。实测：
  ```bash
  $ (逐门禁扫描) 已登记证据日志 84 份；含 '# artifact=' 10 份；其中位于首行 0 份
  $ 经 onto1_gate_log.py 包装的门禁数 = 9
  ```
  `wi_a5_d2_pack` 的命令是**直接调用**（`python3 scripts/onto1_d2_normalization_pack.py --gate`，见 `LOOP.yaml:315`），**没有**套 `onto1_gate_log.py` ⇒ 其日志**根本不含** `# artifact=`。且在全仓范围内，`# artifact=` **从不位于已登记日志的首行**（它是包装器 stdout 的首行，经 `record_gate.py:92` 落盘后位于 `STDOUT` 段内）。
  ⇒ 该核对路径**无法按字面执行**；我以「复算一致 + 日志哈希自证 + 盘上制品与日志 `[out]` 行一致（`eab6ffcb4a381cb7`）」作为等价替代。**这是本轮第 5 条版本/口径问题的实证**（D-11 的"自证 revision"只覆盖 9/84 个门禁，见 §1.5 条件 1 与 §6 建议）。
- 附带事实：我复算的 pack 哈希不同，**根因不是判据摇摆**，而是 pack 内嵌 `inputs.gits_commit`（盘上 `af6d1416` vs 当前 `32924bb4`）⇒ 该制品**随 HEAD 变化**，字节级复现只在同 commit 下有效（建议 TL 在治理上确认这是预期的"变更留痕"，而非"随机输出"）。

---

### 1.7 A 块出口结论

| 项 | 内容 | 判定 |
|---|---|---|
| A-1 | S-1 位移容忍的三向判别力 | **`ACCEPT_WITH_CONDITIONS`**（(a)(b)(c1) 逐字成立；(c2) 暴露"精确命中短路"⇒ 歧义仅在主锚点已错位时才检测，须明示或修） |
| A-2 | `cq_fixtures` 只读盘 + 篡改必红 + 唯一重生成入口 | **`ACCEPT`**（附 3 条小条件：删 `write=True` 死分支 / `--gate` 开关未接线 / 命名） |
| A-3 | `sim_projection` 篡改 ⇒ 仅 G8（`SIM_ARTIFACT_DRIFT`） | **`ACCEPT_WITH_CONDITIONS`**（结论跨两版本成立；须版本绑定；G8 只证"一致性"不证"授权"） |
| A-4 | D2 包 G8 去 R-6 / 声明截短 ⇒ FAIL | **`ACCEPT`**（4 条独立手臂均可单独打红） |
| A-5 | 自审仪 227/14/13 + `--strict` + G0 误报 | **`ACCEPT`**（附：仪器运行即改制品，需 `--out`） |
| A-6 | `wi_a5_d2_pack` 重记未换口径 | **`ACCEPT_WITH_CONDITIONS`**（复算通过；但"日志首行 `# artifact=`"在本门/本仓不存在，无法按字面核对） |

**A 块合计：3 `ACCEPT` / 3 `ACCEPT_WITH_CONDITIONS` / 0 `NOT_ACCEPTED`。**

---

## 2. 第二类覆盖缺口审计（B 块）前的两项必要事实

### 2.1 板面与不变量（本人现场复算）

```
门禁数 = 84 | status 分布 = {'pass': 83, 'inconclusive': 1}
非 pass 项 = [('wi_a4_namespace_collision', 'inconclusive', 3)]
board_expression = {"PASS": 83, "FAIL": 0, "PENDING_EXTERNAL_AUTHORITY": 1, "total": 84}
gate_state.current = RETURN_TO_HLD
```

⇒ 与题面"84 = 83 pass / 1 inconclusive · `RETURN_TO_HLD` · `QA_PASS` 未记录"**一致**（我自己复算，未照抄）。

### 2.2 ⚠️ 重大环境事实：**审计期间存在并发写者，且已提交**

```bash
$ git --no-pager log -3 --format='%h | %an | %ci | %s'
32924bb | shaozhongfei001 | 2026-09-22 12:30:26 +0800 | feat(onto1-d2r2): 应用 Owner 产品引用裁定 —— SIM 投影 28→30，新增 G9/G10 防漂移门禁
337de5d | shaozhongfei001 | 2026-09-22 12:11:01 +0800 | docs(scenario): 产品引用 7 项裁定固化 + SIM 投影变更包（OWNER-DECISION-2026-09-22-D2）
46f9aea | shaozhongfei001 | 2026-09-22 11:52:56 +0800 | docs(scenario): 产品引用待裁定清单 V1.1（范围从 40 条修正为 12 条/7 符号）
```

**独立证据链**（全部可由第三人复算）：

| 时刻(+0800) | 事实 | 对本次 QA 的影响 |
|---|---|---|
| 12:28:46 | `specs/.../projection-config.json` 被改 | SIM 投影的**配置侧**变更 |
| 12:29:15 | `specs/.../sim/product-relations.SIM.ttl` 被重生成（`6fc33da2`→`d63f504b`） | 我的 A-3 被测制品**换版** |
| 12:29:54 | `scripts/onto1_sim_projection.py` 加 G9/G10（`c59ac2d0`→`0f5406c7`） | **我的 A-3 被测脚本换版** |
| 12:30:04 | 新建 `evidence/wi_d2_sim_projection_d2r2-20260922T043004Z.log` | 对方在跑自己的门禁 |
| 12:30:26 | **commit `32924bb`** | 工作区在审计中**前进** |
| 12:43–12:47 | `SCENARIO-*`/`scenario-*`/`sim-*` 产物再写入 | 收工前仍在写 |

**后果（QA 侧结论）**：

1. **一切结论必须绑定哈希**。头号例证：我 A-3 测过的 `sim_projection.py` 版本**在 HEAD 中已不存在**（我按 HEAD 版本重跑后结论不变，但这一步是**必须**的）。
2. **题面与 `STATE.json` 的数字已陈旧**：`STATE.json.next_action`/`NEXT_SESSION` 仍写"SIM 投影 28 条已解析 / 12 条隔离"、"板面 84"，而 HEAD 已把 SIM 投影改为 **28→30**（commit 标题）。**凡引用这些数字的后续文书都必须重取。**
3. **`EVIDENCE.json` 的 `wi_d2_sim_projection*` 登记哈希仍指向 `337de5d` 时代的产物**（`output_sha256` 与磁盘日志一致——我已全量核过 84/84——但**日志所证之事已不是 HEAD 的行为**）。⇒ 建议：凡在 HEAD 变更后仍声称"已复核"的门禁，须**按新哈希重跑重记**（D-11/R-11 的既有纪律），或显式声明"对 commit X 有效"。

### 2.3 ⚠️ 我自己的边界事故（如实登记，不掩盖）

**我按题面要求做"整仓副本内隔离运行"，但隔离并非密封**：45 个仪器中有 **14 个把仓内绝对路径写死**，在副本内运行**仍读写真仓**：

```bash
$ grep -n '/home/szf/dev/' scripts/onto1_*.py
scripts/onto1_a3_closeout.py:27:        ROOT = pathlib.Path("/home/szf/dev/gits-cbanking")
scripts/onto1_breakpoint_advisories.py:21: ROOT = pathlib.Path("/home/szf/dev/gits-cbanking")
scripts/onto1_check_strength_audit.py:31:  ROOT = pathlib.Path("/home/szf/dev/gits-cbanking")
scripts/onto1_disposition_ledger.py:33:    ROOT = pathlib.Path("/home/szf/dev/gits-cbanking")
scripts/onto1_kert_registration_request.py:28: KERT_ROOT = pathlib.Path("/home/szf/dev/Leibniz-KERT")
scripts/onto1_l1_candidate_model.py:23:    ROOT = pathlib.Path("/home/szf/dev/gits-cbanking")
scripts/onto1_l3_load_fixture.py:26:       ROOT = pathlib.Path("/home/szf/dev/gits-cbanking")
scripts/onto1_reference_alignment_check.py:637:  Path("/home/szf/dev/Leibniz-KERT"), ...
scripts/onto1_signature_verify.py:124:    CURRENT_14 = pathlib.Path("/home/szf/dev/gits-cbanking/.../14-...md")
scripts/onto1_sim_migration_verify.py:28:  ROOT = pathlib.Path("/home/szf/dev/gits-cbanking")
scripts/onto1_sim_projection.py:34:        CARDS = Path("/home/szf/dev/Leibniz-KERT/...")
scripts/onto1_sim_rehearsal.py:35:ROOT / :80 KERT_ROOT 均为绝对路径
scripts/onto1_sim_rehearsal_full.py:26:   KERT_ROOT = pathlib.Path("/home/szf/dev/Leibniz-KERT")
...（共 14 个文件）
```

**实际后果（我已逐文件内容比对，用运行前副本作对照）**：我的覆盖实验窗口约 **12:30:05–12:33:10**（由副本内产物 mtime 反推），其间真仓 `loops/ONTO1-ontology-split/evidence/**` 下若干**派生产物**被这些仪器重写：

```bash
$ for f in (13 个文件); do cmp -s "$f" "<运行前副本>/..."; done
B-1-Customer.md / README.md / B-1-Customer-option-A-FULL.csv / a2-disposition-ledger.csv /
a2-disposition-ledger.json / KERT-REGISTRATION-REQUEST-DRAFT.md / l1-core.SIM-CANDIDATE.ttl /
l1-sim-candidate.json / migration-plan.json / sim-migration-verify.json / sim-rehearsal-report.json
   ⇒ 12/13 **内容逐字节一致（仅 mtime 变）**
migration-worklist.json  ⇒ 内容不同（**归属为并发写者**：其 mtime 12:33:03 且语义为 230/223/9→228/225/9，
                             我的副本内同刻产物为 230/223/9）
```

**我的判定与处置（不做回滚，说明理由）**：

- 写入范围**限于 `loops/ONTO1-ontology-split/evidence/**`**；**`specs/`、`generated/`、`docs/dd/`、封版制品、脚本、TL 报告均未被我的实验改动**（`specs/` 的 3 处在 12:28:46–12:30:04 被改，全部早于我的窗口且可由并发写者的 commit 解释）。
- **内容零变化**（12/13 逐字节一致）⇒ 危害为 **mtime/溯源**，非内容。唯一内容变化的那份属并发写者。
- **我不会回滚**：这些是仪器自身的派生产物，回滚会引入新的无人授权内容变更；且部分产物与并发写者的写入交织，无法做到字节级归因回退。
- **须由 TL 处理的后果（1 条具名）**：`evidence/prep/a2-disposition-ledger.{csv,json}` 是**登记门禁** `wi_a2_disposition` 的产物，其 mtime 已被我的副作用刷新（内容未变）⇒ 按 D-11「post-DONE 冻结 / 证据绑定」应**重跑重记该门禁**（或显式登记"mtime 刷新、内容哈希未变"）。**这是我的过程缺陷，我具名登记，不推给他人。**
- **连带发现（对仓库有价值）**：14/45 仪器硬编码仓内绝对路径 ⇒「任何声称在副本/mock 环境下复跑这些仪器即等价于真仓证据」的说法**不成立**；隔离性不可能由"复制仓"达成，只能由**可注入的根路径**（如 `--root`）达成。建议纳入下一轮工具加固。
- 附带：`importlib` 加载脚本产生 3 个 `scripts/__pycache__/onto1_*.cpython-310.pyc`（**`.gitignore` 已忽略**，非受控制品）；我未删除（删除会破坏其它会话可能已存在的缓存），在此披露。

**KERT 零写入（实测）**：

```bash
$ find /home/szf/dev/Leibniz-KERT -type f -newermt '-70 minutes' | grep -v -E '\.git/|__pycache__|\.pyc$' | wc -l
0
```

---

## 3. B 块｜第二类覆盖缺口：两类判定点的**逐点**清单与结论

### 3.1 方法与判据（先把口径写死，避免"结论文档"漂移）

**定位**：AST 扫描全仓 **45 个 `onto1_*.py`**，提取两类形态（自审仪 `extract_in_func` 明确**不覆盖**）：
- **形态 (i) 下标赋值 dict**：`X[...][...] = {...}`（判据写在订阅赋值右侧）；
- **形态 (ii) 裸字符串追加**：`failures.append("...")` / `problems.append(...)` / `findings.append(...)` 等**单字符串参数**的 append。

**运行期证据**：把整仓复制到 `/tmp/qa4/ws/{gits,Leibniz-KERT}`，对每个仪器跑两遍（`--gate` / `--selftest`），用 `sys.settrace` 记录**被执行的行号**（`/tmp/qa4/trace_run.py`），据此判定：

| 字段 | 含义 |
|---|---|
| `r<行>` | 该 append 所属**最内层 `if`** 的行号（守卫行） |
| **能FAIL** | 目标清单名出现在某个 `if/while` 测试中（即参与退出码 = fail-closed） |
| **守卫求值 g/s** | 守卫行在 `--gate` / `--selftest` 运行中**被执行过** |
| **追加执行 s/g** | append 行本身在 `--selftest` / `--gate` 中执行过（= 该拒绝分支被真的踩到） |

**三分类与结论映射（明示，防止口径漂移）**：

- `gj`（**门禁拒绝点**）：`SOUND` = 守卫被求值 ∧ 能FAIL ∧ **自检真的踩到**；`HAS_DEAD_PATH` = 不能FAIL ∨ 守卫从未被求值；`NOT_AUDITABLE` = 可达能FAIL 但**自检从未踩到**（仪器自身无法证明它有没有牙）。
- `sa`（**自检断言点**，如 `if not ok1: failures.append("M1")`，语义是"变异未被拦下"）：`SOUND` = 守卫被求值（该断言被检验过且未触发 ⇒ 变异确被拦下）；`HAS_DEAD_PATH` = 守卫从未被求值。
- `sw`（**状态写入点**，判据的产物）：`SOUND` = 至少在一次运行中被执行；`HAS_DEAD_PATH` = 从未执行。

**置信度分级（必须随结论一起读）**：
- **高**：`能FAIL=False` 属**结构事实**，与运行环境无关；
- **中**：`守卫求值` 来自**副本环境**（缺 `.git`/`apps/`/`frontend/`），故 `守卫求值=N` **不等于**"真仓中不可达"；
- **低**：该仪器在副本内**异常早退**（`review_package_build` exit=99 异常；`zip_manifest_verify`/`pkg_audit`/`w15_acceptance`/`gate_log` 仅执行 15–47 行；`consumer_scan` selftest exit=2）⇒ 其点位**不可判**，我**不作死路径断言**。

### 3.2 总量

```
点位 = 205
按分类: {'state_write': 31, 'selftest_assert': 54, 'gate_judgment': 120}
按分类×结论:
  gate_judgment:   {'SOUND': 36, 'NOT_AUDITABLE': 61, 'HAS_DEAD_PATH': 23}
  selftest_assert: {'SOUND': 53, 'HAS_DEAD_PATH': 1}
  state_write:     {'SOUND': 25, 'HAS_DEAD_PATH': 6}
```

**一句话结论**：QA-3 指出的两类缺口**不是边缘问题**——它们承载 **205 个判定点，其中 120 个是真正的门禁拒绝点**，而自审仪对它们的报告覆盖率为 **0/205**（这 205 点中无一条进入 `auditable` 计数，因为裸字符串 append 甚至**不被登记为 check**，形态 (i) 因缺少"谓词形态"而被丢弃）。在 120 个门禁拒绝点里，**只有 36 个（30%）能被其所属仪器自己的 `--selftest` 证明"有牙"**；61 个（51%）属"仪器自身无法自证"，23 个（19%）至少在一个维度上不成立（其中多数是**结构性的**"目标清单不参与退出码"，少数是副本环境造成的未求值）。

### 3.3 逐点清单（格式：`行(类别,守卫行,能FAIL,守卫求值g/s,追加执行s/g)结论`；`F`=能FAIL，`-`=否，`OK`=SOUND，`NA`=NOT_AUDITABLE，`DEAD`=HAS_DEAD_PATH）

```
onto1_a3_closeout.py [7] :: 85(sw,rNone,-,N/N,Y/Y)OK 90(sw)OK 93(sw)OK 96(sw)OK 99(sw)OK 102(sw)OK 105(sw)OK
onto1_attribution_rebuild.py [1] :: 339(sa,r338,F,N/Y,N/-)OK
onto1_c2_consumer_scan.py [1] :: 148(gj,rNone,-,N/N,N/-)DEAD
onto1_c2_fix_verify.py [1] :: 88(gj,r87,F,Y/Y,Y/-)OK
onto1_class_reconciliation.py [1] :: 88(sw,rNone,-,N/N,Y/Y)OK
onto1_consumer_scan.py [7] :: 161(sw,rNone,F,N/N,N/Y)DEAD 441(gj,r440,F,Y/N,N/-)NA 445(gj,r444,F,N/N,N/-)DEAD
                              463(gj,r462,F,Y/N,N/-)NA 469(gj,r468,F,Y/N,N/-)NA 475(gj,r474,F,Y/N,N/-)NA 502(gj,r501,F,Y/N,N/-)NA
onto1_cq_fixtures.py [12] :: 134(gj,r133,F,Y/Y,Y/-)OK 143(gj,r142,F,Y/Y,Y/-)OK 146(gj,r145,F,Y/Y,Y/-)OK
                              149(gj,r148,F,Y/Y,Y/-)OK 153(gj,r152,F,Y/Y,N/-)NA 155(gj,r154,F,Y/Y,Y/-)OK
                              197(sa,r196,F,N/Y,N/-)OK 210(sa)OK 218(sa)OK 233(sa)OK 239(sa)OK 246(sa)OK
onto1_d2_normalization_pack.py [21] :: 602(sw)OK 736(gj,r735,F,Y/Y,Y/Y)OK 741(gj,r740,F,Y/Y,Y/-)OK
                              1009(sa)OK 1017(sa)OK 1023(gj,r1022,F,Y/Y,N/-)NA 1037(gj,r1036,F,Y/Y,Y/Y)OK
                              1043(gj,r1042,F,Y/Y,N/-)NA 1045(gj,r1044,F,Y/Y,N/-)NA 1047(gj,r1046,F,Y/Y,N/-)NA
                              1051(gj,r1050,F,Y/Y,N/-)NA 1059(gj,r1058,F,Y/Y,Y/-)OK 1066(sa)OK 1077(sa)OK
                              1098(sa,r1097,F,N/Y,Y/-)OK 1108(sa,r1107,F,N/Y,Y/-)OK 1113(sw)OK 1118(sa)OK 1128(sa)OK
                              1145(sa)OK 1152(sa)OK
onto1_d4_pack.py [43] :: 121(gj,r120,F,Y/Y,N/-)NA 133(gj,r132,F,Y/Y,N/-)NA 136(gj,r135,F,Y/Y,Y/-)OK
                              145(gj,r144,F,Y/Y,N/-)NA 148(gj,r147,F,Y/Y,N/-)NA 154(gj,r153,F,Y/Y,Y/-)OK
                              157(gj,r156,F,Y/Y,N/-)NA 160(gj,r159,F,Y/Y,Y/-)OK 165(gj,r164,F,Y/Y,N/-)NA
                              168(gj,r167,F,Y/Y,N/-)NA 177(gj,r176,F,Y/Y,Y/Y)OK 184(gj,r183,F,Y/Y,Y/-)OK
                              189(gj,r188,F,Y/Y,N/-)NA 192(gj,r191,F,Y/Y,N/-)NA 194(gj,r193,F,Y/Y,N/-)NA
                              196(gj,r195,F,Y/Y,N/-)NA 199(gj,r198,F,Y/Y,N/-)NA 201(gj,r200,F,Y/Y,N/-)NA
                              206(gj,r205,F,Y/Y,N/-)NA 209(gj,r208,F,Y/Y,Y/-)OK 211(gj,r210,F,Y/Y,N/-)NA
                              214(gj,r213,F,Y/Y,N/-)NA 218(gj,r217,F,Y/Y,N/-)NA 220(gj,r219,F,Y/Y,N/-)NA
                              222(gj,r221,F,Y/Y,N/-)NA 227(gj,r226,F,Y/Y,N/-)NA 230(gj,r229,F,Y/Y,N/-)NA
                              233(gj,r232,F,Y/Y,N/-)NA 235(gj,r234,F,Y/Y,N/-)NA 238(gj,r237,F,Y/Y,Y/-)OK
                              242(gj,r241,F,Y/Y,N/-)NA 244(gj,r243,F,Y/Y,N/-)NA 246(gj,r245,F,Y/Y,Y/-)OK
                              253(gj,r252,F,Y/Y,Y/-)OK 256(gj,r255,F,Y/Y,N/-)NA 261(gj,r260,F,Y/Y,Y/-)OK
                              265(gj,r264,F,Y/Y,N/-)NA 270(gj,r269,F,Y/Y,N/-)NA 276(gj,r275,F,Y/Y,N/-)NA
                              278(gj,r277,F,Y/Y,N/-)NA 282(gj,r281,F,Y/Y,N/-)NA 287(gj,r286,F,Y/Y,N/-)NA
                              423(sa,r422,F,N/Y,Y/-)OK
onto1_disposition_ledger.py [2] :: 379(gj,r378,-,Y/Y,N/-)DEAD 384(gj,r383,-,Y/Y,Y/-)DEAD
onto1_evidence_board_check.py [11] :: 75(gj,r74,F,Y/Y,N/-)NA 88(gj,rNone,F,N/N,Y/-)DEAD 92(gj,r91,F,Y/Y,Y/-)OK
                              102(gj,r100,F,Y/Y,Y/-)OK 139(sa)OK 146(sa)OK 153(sa)OK 166(sa)OK 178(sa)OK 189(sa)OK 194(sa)OK
onto1_iri_mapping_draft.py [2] :: 448(sa,r447,F,N/Y,N/-)OK 454(sa,r453,F,N/Y,N/-)OK
onto1_l1_prep.py [1] :: 225(sw,rNone,-,N/N,Y/-)OK
onto1_namespace_collision_check.py [29] :: 383(gj,r382,F,Y/Y,Y/-)OK 396(gj,r394,F,Y/Y,N/-)NA 403(sa)OK
                              414(gj,r406,F,Y/Y,N/-)NA 428(gj,r426,F,Y/Y,Y/-)OK 434(gj,r432,F,Y/Y,N/-)NA
                              443(gj,r442,F,Y/Y,Y/-)OK 461(gj,r456,F,N/Y,Y/-)OK 529(gj,rNone,F,N/N,Y/-)DEAD ×2
                              542(sw)OK 564(sw)OK 566(sw)OK 574(sw)OK 580(sw)OK 596(sw)OK 610(sw)OK 612(sw)OK
                              623(sw)OK 641(sw)OK 664(sw)OK 665(sw)OK
                              891(sa)OK 985(sa)OK 1051(sa)OK 1087(sa)OK 1102(sa)OK 1115(sa)OK 1140(sa)OK
onto1_obligation_triage.py [16] :: 260(gj,r258,F,Y/Y,N/Y)OK 663(gj,r662,F,Y/Y,N/-)NA 668(gj,r667,F,Y/Y,N/-)NA
                              678(gj,r677,F,N/Y,N/-)NA 684(gj,r683,F,N/Y,N/-)NA 695(gj,r694,F,N/Y,Y/-)OK
                              704(gj,r703,F,N/Y,Y/-)OK 706(gj,rNone,F,N/N,N/-)DEAD 710(gj,r709,F,N/Y,N/-)NA
                              713(gj,r712,F,N/Y,N/-)NA 809(gj,r808,F,N/Y,Y/-)OK 813(gj,r812,F,N/Y,Y/-)OK
                              819(gj,r818,F,N/Y,N/-)NA 824(gj,r818,F,N/Y,N/-)NA 835(gj,r834,F,N/Y,Y/-)OK 1241(sw)OK
onto1_pkg_audit.py [8] :: 90(gj)DEAD 99(gj)DEAD 103(gj)DEAD 110(gj)DEAD 112(gj)DEAD 129(gj)DEAD 135(gj)DEAD 182(gj)DEAD
                              （全部 rNone,-,N/N,N/-：**低置信度**，该仪器在副本内仅执行 47 行）
onto1_product_refs_probe.py [7] :: 196(gj,r195,F,Y/Y,N/-)NA 202(gj,r201,F,Y/Y,N/-)NA 208(gj,r207,F,Y/Y,N/-)NA
                              243(sa)OK 256(sa)OK 263(sa)OK 268(sa)OK
onto1_reference_alignment_check.py [1] :: 381(sw,rNone,F,N/N,N/-)DEAD（低置信度：脚本读绝对 KERT 路径，副本内行为不同）
onto1_review_package_build.py [4] :: 113(sw)DEAD 115(sw)DEAD 133(sw)DEAD 135(sw)DEAD（**低置信度**：--gate exit=99 异常）
onto1_review_package_check.py [10] :: 63(gj,r62,F,Y/Y,N/-)NA 67(gj,r66,F,Y/Y,Y/-)OK 74(gj,r73,F,Y/Y,Y/-)OK
                              80(gj,r79,F,Y/Y,N/-)NA 84(gj,r83,F,Y/Y,N/-)NA 88(gj,r87,F,Y/Y,Y/-)OK
                              90(gj,r89,F,Y/Y,Y/-)OK 118(sa)OK 128(sa)OK 136(sa)OK
onto1_signature_verify.py [3] :: 57(gj,r56,-,Y/Y,Y/Y)DEAD 59(gj,r58,-,Y/Y,Y/Y)DEAD 63(gj,r62,-,Y/Y,Y/Y)DEAD
onto1_sim_migration_verify.py [1] :: 161(sw,rNone,-,N/N,Y/Y)OK
onto1_wave0_readiness.py [11] :: 485(sa)…605(sa)：11 条 sa 全 SOUND（守卫均在 --selftest 中被求值）
onto1_zip_manifest_verify.py [5] :: 76(gj)DEAD 78(gj)DEAD 80(gj)DEAD 106(gj,r105,F,N/N,N/-)DEAD 120(sa,r119)DEAD
                              （**低置信度**：该仪器 --gate 仅执行 26 行即退出）
```

### 3.4 值得 TL 优先处理的**具名**发现（B 块导出，非"结论"，是事实陈述）

| # | 发现 | 证据 | 为什么重要 |
|---|---|---|---|
| B-i1 | **`failures.append("字符串")` 形态是主流写法**：120 个门禁拒绝点**全部 120 个**都是这种形态（另 31 个下标赋值点属"状态写入"形态） | §3.2 分类计数 | 自审仪**结构性看不见**它们（`:149-160` 只认 2/3 元组、dict、带谓词的 append）⇒ "0 条候选"绝不等于"无缺陷" |
| B-i2 | `onto1_signature_verify.py:57/59/63`：三条拒绝点**都不参与退出码**（`能FAIL=-`），但**在 `--gate` 与 `--selftest` 中都被执行**（`Y/Y`、`Y/Y`） | §3.3 + `signature_verify.py:56-64` | "能走到、也不参与判死"= 典型**披露式而非判据式**实现；若其结论（`OWNER_REVIEW_ONLY` / 禁记委员会批准）只靠这三条 append 表达，则**不是 fail-closed**。与 QA-2 的 F 系列同族，但**形态不同**（这次是"清单不进退出码"） |
| B-i3 | `onto1_disposition_ledger.py:379/384`：两条 append 的**清单不进退出码**（`-`），其中 `:384` 在 selftest 中**被执行过**（`Y/-`） | §3.3 | 同上：该点"能被踩到但不判死" |
| B-i4 | `onto1_d2_normalization_pack.py:1043/1045/1047`（G5 的三条强度判据）：守卫在 gate/selftest **都被求值**，但 append **从未在 selftest 中执行** | §3.3 | 即：G5 的三条分支**在本轮全部变异下都没有被触发过** ⇒ "G5 有牙"**未获自证**（我**不**断言其无效，只断言**未被证明**） |
| B-i5 | `onto1_cq_fixtures.py:153`（Q5 negative 空缺）**唯一一条在 selftest 中未被踩到的拒绝点**，而它就在我刚判 `ACCEPT` 的仪器里 | §1.2 + §3.3 | 与 A-2 不冲突（A-2 判"篡改必红"，实测 4 例全红）；但**"Q5 negative 空缺"这条手臂**缺反例 ⇒ 建议补一个 M6（清空 CQ1.negative） |
| B-i6 | `onto1_pkg_audit.py` **8/8 点位不可判**（副本内仅执行 47 行，`--gate`/`--selftest` 均 exit=2） | §3.3 + trace | 该仪器同时是 C-3 的对象；其"恒红"与"不可判"叠加，**不能**用其输出去支撑任何红线结论 |

---

## 4. C 块｜对 TL 三条「具名未修」的**独立判定**（只判、不改）

### 4.1 C-1｜`namespace_collision_check.py:446-480` C-4b 死防线

**事实（我现场读取 + 复算）**：

```bash
$ grep -n -E "freeze_subjects|vacuous|C-4b|空转" evidence/wi_a4_namespace_collision-20260921T050548Z.log
13:[C-4] PASS（声明 4 个：受控 1 / D-2 范围外 3 / 未裁决 0；必需钉值 allow-list 4/4；载体自冻结：受控载体 0 个，**空转不计为覆盖**）
21:onto1-namespace-collision: INCOMPLETE （C-1b 未判定 ⇒ **不得计为通过**；解除需 D3 签署根域后重跑）
```

源码：`:452-471` 计算 `controlled_sidecars`；为空时 `vacuous.append("pin_sidecar_freeze")` 且追加一条 `status=VACUOUS` 的 `results` 项；但**总体状态**由 `:475` 决定：`status = "FAIL" if failures else ("PASS" if declarations else "FAIL")` —— **空转不进 `failures`**，因此该子检查**对退出码零影响**。

**我的判定**：**应判 `NOT_EVALUATED`（不得给绿）**，理由有三，且**同函数内部已自相矛盾**：

1. **同一"域为空"条件在同函数内被区别对待**：`:442-444` 对**声明域**为空 ⇒ `failures.append("C-4_NO_CONTROLLED_PIN … 空转，不得计为通过")` ⇒ **FAIL**；而**冻结域**为空 ⇒ 只记 `VACUOUS` ⇒ 整体仍 **PASS**。两个子检查的语义应当同构（都是"无检测对象"），却一个判死、一个给绿。
2. **与 R4（空转 = 失败）直接冲突**：本仓既有实践一贯把空转**显式排除在"覆盖"之外**（`C-3` 打印"空转，不计为覆盖"、`C-4` 打印"空转不计为覆盖"、QA 白名单条款 5、`board_expression` 的 `PENDING_EXTERNAL_AUTHORITY` 与 FAIL 分离）。既然如此，**"不计为覆盖"就不能输出 PASS**——否则"PASS"的字面含义被悄悄放宽成"除空转子项外通过"。
3. **风险是"随他人解锁自动转绿"**：当前 `INCOMPLETE` 是因为 `C-1b` 待 D3；**D3 一旦签署**，`C-1b` 转绿后 `C-4` 的空转子检查将成为**唯一的自冻结防线且它是空转的**，此时门禁会**整门变绿**——即"死防线在绿灯下隐形"。这正是 S-1 同类（板面与事实不一致）的前置条件。

**为什么另一条（改检测口径）我判为次优**：
- 把 `freeze_subjects` 扩到 `loops/**`（把证据索引/记录也当"载体"）会引入**必然漂移**的判据：`:447-449` 已明确"清单类产物载体是可重生成的工具产物，冻结必然漂移"，而 `loops/**` 的 mtime/内容在**本轮就漂移了至少 3 次**（§2.2、§2.3 实测）⇒ 结果是从"恒绿的空转"换成"恒红的噪声"，**另一种空转**（同时违反 D-15「禁止再加码上限」）。
- 因此正确出口是：**无检测对象 ⇒ 该子检查判 `NOT_EVALUATED`，并使其至少阻止"整门绿"**（例如把 `vacuous` 非空 ⇒ 总体 `NOT_EVALUATED`/exit 3，或至少在 `board_expression` 里单列）。**具体落地口径（是改 exit 码、还是改板面三值表达）属 TL+Owner 决策，我不代裁。**

**注**：该门禁当前整体已是 `inconclusive`（exit 3）且板面记 `PENDING_EXTERNAL_AUTHORITY`，因此**本条不改变当前板面数字**；它改的是"**D3 签署后的行为**"，属预防性判定。

---

### 4.2 C-2｜`product_refs_probe.py:102`（`raise`）与 `:196`（P1）

**判定：P1 确实永不可达（死代码）。移位后退出语义不变，仅失败消息改变。**

**最小实验（`gate()` 走空卡目录 + 反事实模拟"P1 移到 raise 之前"）**：

```bash
$ python3 /tmp/qa4/c2_p1_probe.py
[1] 现状：空卡目录 ⇒ gate() 走哪条路径？
   exit = 2
   | onto1-product-refs: FAIL: no product cards found under /tmp/qa4-c2-.../empty
   出现 'P1 no product cards' ? False      出现 'no product cards found' ? True
   ⇒ P1 分支（:196）未被执行（probe 已在 :102 抛错并被 :190 捕获）

[2] 反事实：把 P1 处理移到 raise 之前（用返回空结果的假 probe 模拟）
   exit = 2
   | [P1] cards=0 product_ids=0 references=0
   | [P2] by_field={} declared=[]     [P3] by_resolution={} dangling=0
   | onto1-product-refs: FAIL: P1 no product cards
   | onto1-product-refs: FAIL: P2 ... ×3      | onto1-product-refs: FAIL: P3 ...
   出现 'P1 no product cards' ? True

[3] 静态证明：probe() 是 summary['cards'] 的唯一来源
  100: cards = find_cards(card_root)
  101: if not cards:
  102:     raise RuntimeError(f"no product cards found under {card_root}")
  193: summary = write_report(result, out_dir)
  195: if summary["cards"] < 1:
  196:     failures.append("P1 no product cards")
[结论] 退出码 现状=2 反事实=2 ⇒ **不变**（差别仅在失败消息）
```

**推理（形式化）**：到达 `:195` 的前提是 `probe()` **返回**（`:189`），而 `probe()` 返回的前提是 `cards` 非空（`:100-102`）；`summary["cards"] = len(result["cards"]) = len(cards)` ⇒ `summary["cards"] ≥ 1` 恒成立 ⇒ `:195` 的 `if` **恒假** ⇒ `:196` 不可达。

**处置建议（不改，供 TL）**：二选一——① 删除 `:195-196`（承认"无卡 = fail-closed 的 RuntimeError 出口"已是唯一判定），或 ② 把 P1 判定**前移进 `probe()`/`gate()` 的异常分支**并统一失败语（退出码不变，只是把"崩溃态措辞"换成"具名判据措辞"）。两条都不改变退出语义，故**不属阻塞项**；但**保留死代码会污染后续"死路径审计"的成本**（QA-3 已不得不为它单独出一份判定）。

---

### 4.3 C-3｜`pkg_audit.py:105-110` AU-5 恒红 + `recent_changes()` 恒 `[]`

**事实（我现场复算，未采信转述）**：

```bash
$ python3 scripts/onto1_pkg_audit.py --redlines        # 只读，无写入
[AU-5] controlled/LERT redlines: N finding(s)
onto1-pkg-audit: FINDING: AU-5 RED LINE: controlled artifacts touched: [...]
# 结构（源码 :118-137）：AU-5 = 两个独立来源
#   (a) git status 中命中 specs/* · generated/* · docs/dd/*（→ 恒红，因为 SIM 整改已获 Owner 授权并落到 specs/）
#   (b) KERT 仓 git status 中含 ONTO/ONTOLOGY-SPLIT 的行（→ 历史遗留，B-7 待追认）
$ grep -n "def recent_changes" -A 16 scripts/onto1_pkg_audit.py | tail -4
    print(f"[AU-5m] files modified in last {minutes} min: {len(touched)}")
    for item in sorted(touched)[:25]:
        print(f"        {item}")
    return []                        # ← 恒 []，调用处 `if args.recent: recent_changes(args.recent)` 丢弃返回值
```

**判定（只给候选口径与代价，结论归 Owner）**：

| 口径 | 内容 | 代价 | 前置 |
|---|---|---|---|
| **A. 授权维** | 引入**机器可读的授权台账**（Owner 决议号 + 授权 glob + 生效时间 + 指纹），AU-5 仅对"改动 ∉ 授权范围"判红；授权范围内的改动降级为**披露**并**必须附决议引用** | 台账成为新的受控制品，需要登记流程与到期/撤销机制；**且台账本身是"自我满足"风险**（写台账者即定绿者）⇒ 必须有独立签署锚点（否则重演 QA-3 的 S-1 类问题） | Owner 决定"授权范围"的书写格式与签认方式 |
| **B. 时间维（纪元）** | 以"最近一次 Owner 决议的哈希+时间戳"为界；界后改动若能回源到决议 ⇒ 披露，否则判红；界前存量脏项切到基线 | 需解决**时钟/时区**与"决议前已存在的脏项"（当前 `git status` 本就带一堆 SIM 整改改动）；需要把决议文件纳入指纹管理 | 同上 + 一份"决议→改动"的映射规则 |
| **C. 目录分级（判死范围收窄）** | 把受控目录分两级：**绝对只读**（`generated/**`、`docs/dd/**`、封版）恒红；**授权域**（`specs/**`）默认仅披露 | 语义上把"AU-5 红线"降级为"部分红线"；须在文档中同步改写 AU-5 的定义，否则出现"名字还叫红线、实际只管一半"的口径漂移 | TL 可先做（不改授权语义），但需 Owner 追认分级 |
| **D. 三值输出** | 无授权信息时 AU-5 判 **`NOT_EVALUATED`（exit 3）**，不冒充 FAIL | 需 `board_expression`/`loop_guard` 支持三值（现生态以 0/2 为主），且与 C-1 的同类决定**必须同一口径**（否则"空转/未授权"在门禁与板面分别被表达为 FAIL 与绿） | 与 C-1 一并决定 |

**`recent_changes()` 恒 `[]` 的候选口径**：

| 口径 | 内容 | 代价 |
|---|---|---|
| **α. 仅披露（现状语义）+ 显式标注"不可归因"** | 保持返回 `[]`，但输出里写明"mtime 不可归因：构建产物/并发写者均会触发" | 该函数**永远无法产生 finding**；若把它当"兜底红线"就是空转（与 R4 冲突） |
| **β. 让 mtime 参与判据（近 N 分钟被改 ⇒ 报告）** | 返回 findings | **实测会大量误报**：本轮我自己的会话窗口内就有 20+ 个 `poc/**/target/classes/**` 类构建产物与并发写者的写入；TL 的 Z5 已记录同类问题 ⇒ 需要"归因白名单"，复杂度等于重造口径 A |
| **γ. 受控目录改用 git（而非 mtime）** | 去掉 mtime 兜底，`loops/**` 纳入版本控制后由 git 提供不可归因的显式 diff | 需要把 `loops/**` 从"未跟踪"改为受控（治理动作，Owner 决定）；未纳入前该口径**不可用** |

**我明确不给结论**：三条（C-1 的"空转不得给绿"与 C-3 的 A/D 口径）在**同一语义轴**上（"未授权/未判定该判什么"），任一单独决定都会造成门禁与板面口径分叉。

---

## 5. 未采信与未覆盖（诚实边界）

1. **未采信**：本报告全部数字均为现场复算；TL 侧一切结论（含 `TL-ADJUDICATION-QA-W3R3` 的 13 项仪器裁定）**只作为待验对象**。例：题面给的"227/14/13"我复算一致后才采用；"板面 84"我读 `EVIDENCE.json` 复算一致后才采用；"日志首行 `# artifact=`"我复算后**否定**（§1.6）。
2. **未覆盖（本轮不做断言）**：
   - HEAD 新增的 **G9/G10**（`sim_projection`）与 d2r2 变更后的 `UNRESOLVED.json` 一致性：**未做变异复验**（不在本轮清单，且其制品在审计期间仍在变）。
   - **B 块的低置信度点位**（`pkg_audit` 8 点、`zip_manifest_verify` 5 点、`review_package_build` 4 点、`reference_alignment_check` 1 点）：副本环境不适配（缺 `.git`/`apps/`，或仪器早退/异常），**必须回真仓复验**，我不下死路径断言。
   - `onto1_migration_runner` / `onto1_construction_plan` / `onto1_scenario_readiness` / `onto1_sim_rehearsal*` / `onto1_log_hygiene` / `onto1_review_package_check` 等**未被 QA-3 裁定的其余仪器**：只做了 B 块形态扫描，未做 SOUND/死路径裁定。
   - 未执行 `make generate` / `make check` / `make backend-test`（非本轮范围，且会改制品）。
3. **我拒绝做的事**：未记 `QA_PASS`；未代签；未把任何建议写成权威事实；未回滚**任何**文件（含我自己副作用造成的 mtime 刷新——回滚会引入无授权的内容变更）。

---

## 6. 给 TL 的**可执行**建议（按优先级，均可独立落地）

| # | 建议 | 判据 |
|---|---|---|
| 1 | **版本绑定纪律硬化**：所有"已复核"声明必须带 `path@sha256[:16]`；凡 `scripts/onto1_*.py` 或 `specs/**` 变更 ⇒ 相关门禁**按新哈希重跑重记**（本轮已有 `sim_projection` 换版实证） | 声明文本含哈希；`EVIDENCE.json` 的 `output_sha256` 对应的日志日期 ≥ 制品 mtime |
| 2 | **消除隔离幻觉**：给硬编码 ROOT 的 14 个仪器加 `--root`（默认仍为仓根），使"沙箱复跑"成为可能；否则任何"在副本里跑过"的说法不可作为证据 | `grep -c '/home/szf/dev' scripts/onto1_*.py` 归零，或显式登记为已知例外 |
| 3 | **D-11 自证覆盖缺口**：9/84 门禁套了 `onto1_gate_log.py`（含 `# artifact=`），其余 75 个无自证 ⇒ 把"新重记一律走包装器"作为**硬纪律**，并在 `EVIDENCE.json` 增加 `artifact_sha256` 字段（由包装器写入） | `# artifact=` 覆盖 84/84 且**内容与 `output_sha256` 独立**（否则自证变成同源） |
| 4 | **自审仪登记范围**：把"裸字符串 append"与"下标赋值 dict"纳入 `extract_in_func`（形态可枚举：`ast.Call(attr='append')` 单字符串参数 ⇒ 作为 `STRING_JUDGMENT` 候选），否则 B 块的 205 点永远是盲区 | 复跑后 `by_flag` 出现新类别；`--strict` 的 high 计数变化可解释 |
| 5 | **A-6 附带项**：`d2-normalization-pack.json` 内嵌 `gits_commit` ⇒ 该产物**每次跨 commit 复跑哈希必变**。若此类产物被登记为证据，须在 `pass_condition` 中写明"仅同 commit 可比"，或把 commit 字段移出被哈希体（侧车登记）。 | 同 commit 两次复跑哈希一致 |
| 6 | **C-1/C-3 同一口径合并决策**：把"空转子检查"与"未授权红线"统一为**三值表达**（PASS / FAIL / NOT_EVALUATED），并让 `board_expression` 显式分列 `NOT_EVALUATED`；避免"空转给绿"与"授权后恒红"两种相反偏差 | `board_expression` 出现第三计数；`wi_a4_namespace_collision` 在 D3 签署后**不得仅因 C-1b 转绿而整门变绿** |

---

## 7. 出口结论（本轮）

| 块 | 出口 |
|---|---|
| **A 块（4 条修复复核）** | `A-1 ACCEPT_WITH_CONDITIONS` · `A-2 ACCEPT` · `A-3 ACCEPT_WITH_CONDITIONS` · `A-4 ACCEPT` · `A-5 ACCEPT` · `A-6 ACCEPT_WITH_CONDITIONS`（**3 ACCEPT / 3 AWC / 0 NOT_ACCEPTED**） |
| **B 块（第二类覆盖缺口）** | 点位 **205** = 120 `gj` + 54 `sa` + 31 `sw`；逐点结论见 §3.3。**SOUND 114 / NOT_AUDITABLE 61 / HAS_DEAD_PATH 30**（其中低置信度 18 点须回真仓复验）。**关键事实：自审仪对这 205 点覆盖率 = 0**，且 120 个门禁拒绝点中仅 **30%** 能被其仪器自检证明"有牙" |
| **C 块（三条具名未修）** | C-1：**应判 `NOT_EVALUATED`（不得给绿）**，与 R4 及同函数内 `C-4_NO_CONTROLLED_PIN` 的既有处置一致；改口径为次优（代价与理由见 §4.1）· C-2：**P1 确认永不可达**；移位后**退出语义不变**（仅消息）；建议删或前移 · C-3：**不给结论**，给 4 条 AU-5 口径 + 3 条 `recent_changes()` 口径及各自代价（§4.3） |

**不变量核对（收工时实测）**：`QA_PASS` **未记录** · `independent_qa` 仍非 QA_PASS · 板面 **84 = 83 pass / 1 inconclusive**（未被本会话改动）· `gate_state.current = RETURN_TO_HLD` · **KERT 写入 0** · `generated/**`·`docs/dd/**`·封版制品 改 0 · TL 脚本/TL 报告 改 0 · 未代签 · 未 `git add`。

**两处必须带走的负面事实（我自己的与环境的）**：
1. **环境**：审计期间存在**并发写者并已提交**（`32924bb`，12:30:26），导致 `sim_projection.py`、`SIM.ttl`、`UNRESOLVED.json` 与多个 `specs/` 制品**在我审计中换版**；`STATE.json`/`NEXT_SESSION.md` 的"28 条"等数字**已陈旧**。
2. **我自己的**：因 14 个仪器硬编码仓内绝对路径，我的覆盖实验**未能做到零写入**——真仓 `evidence/**` 下 12 份派生产物被重写（**内容逐字节未变，仅 mtime 变**）；其中 `a2-disposition-ledger.{csv,json}` 属登记门禁 `wi_a2_disposition` 的产物，**建议 TL 重跑重记该门禁**。我**不回滚**，并具名登记为本次 QA 的过程缺陷。

```
[收工] Loop: ONTO1-ontology-split, Gate: 未动（RETURN_TO_HLD 不变；未记 QA_PASS）, Baton → tech_lead（不变）
[索引] INDEX_STALE(13)（收工实测 `make index-status` ⇒ WARN，drift 13，未超阈值）
[落盘] 本报告即唯一交付物；EVIDENCE.md / STATE.json / NEXT_SESSION.md / ROLE_BOARD.yaml **未改**（本轮写域被限定为本文件）
```

> **写域冲突的处置说明**：Loop 共享记忆规则要求 QA 收工时更新 `EVIDENCE.md`/`STATE.json`/`NEXT_SESSION.md` 并交接 Baton；而本轮派工**明确限定写域为本文件**。我按**更严格的约束**执行（只写本文件），因此**Baton 仍为 `tech_lead`**，上述落盘与 `qa-w3r4` 的收口登记**须由 TL 执行**。
