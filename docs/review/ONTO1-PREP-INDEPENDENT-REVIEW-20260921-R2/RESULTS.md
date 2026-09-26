# 结果口径（三项分开陈述）

## 1. 作者自检通过（author self-check passed）
- 门禁（作者运行）：**PASS=48 · FAIL=0 · PENDING_EXTERNAL_AUTHORITY=1**（共 49）
- 本轮复核相关新增自检（作者运行，均 exit 0）：`onto1_class_reconciliation --gate 7/7 + selftest 3/3`；
  `onto1_construction_plan --gate 6/6 + selftest 3/3`；`onto1_l1_prep --gate 5/5 + selftest 3/3`；
  `onto1_c2_generator_check 7/7 + 4/4`；`onto1_c2_fix_verify 7/7 + 6/6`；`onto1_sim_projection 7/7 + 4/4`；
  `onto1_log_hygiene 4 闸 + 5/5`。
- **声明**：以上均为**作者自检**，不构成独立复核结论。

## 2. 独立复核待做（independent review pending）
- `independent_qa` = **pending** / actor = **None**（**无人代签**）。
- 本包用途：供**项目 Owner 的架构顾问**独立复核两项疑点（L1 32/8 类、条款作用域）与证据可复现性。
- 未做：未由第三方复跑脚本、未由委员会签署、未做 QA_PASS。

## 3. 正式分仓未完成（formal split NOT done）
- **拆分施工执行量 = 0 / 691**（真义务 691：W2_SPLIT 291 · W3_CONSUMER_SWITCH 381 · W3_KERT_ASSETS 19）。
- `wave_0..3` 仍 `BLOCKED`；`PRODUCTION_ACTIVATION` = **BLOCKED**；C-2 = CLOSED（仅命名空间兼容项）。
- 已完成者仅为 **Wave -1 就绪**（清单/门禁/候选/骨架/扫描）与 **SIM 范围整改**。
- **门禁通过数 ≠ 实施完成度**：请勿以 PASS 数替代上述完成度判断。

## 4. 计数单位与重叠性（供评审人复算）

| 计数 | 单位 | 说明 |
|---|---|---|
| **691** | 义务**条数**（`obligation-triage.csv` 中 `disposition=TRUE_OBLIGATION`） | 每条含 `repo,path,tier,signal,rationale,evidence` |
| **499** | **唯一 (repo, path) 文件数** | 由 691 条义务**去重文件**得到 ⇒ 691 是"条"口径，499 是"文件"口径 |
| **364** | 引用**项**数（`RESOLVES_LOCAL_OR_PROVISIONAL_CURIE 332` + `…_IRI 32`） | 单位 = **「文件 × 去重后的引用形式」对**，跨文件累加；**不是唯一 IRI 数** |
| **125** | 同上（`KNOWN_EXTERNAL_CURIE 89` + `KNOWN_EXTERNAL_IRI 36`） | 通用词汇，不需迁移 |
| **64** | 同上（`OTHER_PREFIX_CURIE`） | 未知前缀；**含非 RDF 语境误匹配**，需逐条真伪判定 |
| **34** | 同上（`UNMAPPED_APP_IRI`） | 未映射应用 IRI，迁移期逐条裁决 |
| **325** | **导入语句条数**（`CODE_IMPORT_ONTOLOGY_PKG`） | Java `import com.gien.gits.ontology.*`；**非包名去重** |

**重叠性**：单一引用按判定顺序**只落一类**（EXTERNAL → LOCAL → UNMAPPED；CURIE: local → external → other）⇒ 六类**互不重叠**。
唯一例外：**Java 导入**与 CURIE/IRI 是**不同维度**，同一文件可同时计数（报告时请分开看）。
复算命令：`python3 scripts/onto1_l1_prep.py --migration`（输出 `evidence/prep/consumer-migration-coverage.json`）。
