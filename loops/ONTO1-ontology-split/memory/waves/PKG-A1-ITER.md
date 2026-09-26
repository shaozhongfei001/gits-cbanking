# PKG-A1｜ITER（每次 attempt 的命令 + exit + 输出摘要）

> 记账规则：**按真实退出码**记录，不把 fail 写成 inconclusive。门禁 attempt 上限 5。
> 本包 `--gate` 在真实数据上**从未失败**（Attempt 1 即 PASS）；下表的 F-1~F-3 是**开发期自审**发现的
> 实现缺陷（首次 `--gate` 之前），F-4~F-6 是门禁 PASS 后**口径/范围**修订（每次重跑复验）。

## 开工声明（GOV-CFI-001）

```text
[索引] INDEX_FRESH @ merge 2026-09-15T17:50:17Z (gits 71169042 / kert 64f6f873)；KERT 侧 INDEX_STALE(144)
[索引] 候选影响面: apps/api · specs/knowledge-architecture · specs/gk-ke · modules/operational-ontology · kert/src（占 59%）+ 其余 specimens
[回源] specs/knowledge-architecture/instances/product/products.ttl:1 确认 gits: 前缀与本体前缀不一致（IRI_BANK_EXAMPLE）
[回源] apps/api/src/main/java/com/gien/gits/api/controller/ClaimController.java:15 确认 `import com.gien.gits.ontology.Claim;`（本体模型层耦合）
[回源] apps/api/src/main/java/com/gien/gits/api/dto/ClaimResponse.java:8-9 确认 DTO 自述「领域 ontology.Claim 为 statement 型 / OpenAPI Claim 为 content 型」⇒ 不可据此判同名
[回源] apps/api/src/test/java/com/gien/gits/api/controller/HumanGateControllerTest.java:8 确认存在 `import com.gien.gits.ontology.*;` ⇒ 裸名解析不唯一
```

## 1. 门禁执行记录（真实数据）

| # | 命令 | exit | 输出摘要 |
|---|---|---|---|
| A-1 | `python3 scripts/onto1_obligation_triage.py --report` | 0 | `rows=1052 true=626 homonym=0 needs=426 sum=1052 closed=True`；`csv sha256=81e5ebc414df576c…` |
| A-2 | `python3 scripts/onto1_obligation_triage.py --gate` | **0** | PASS：G1 输入锚定 / G2 对账闭合 / G3 强面判定 / G4 证据可回源 / G5 弱面反一刀切 / G6 Wave 合法 / G7 产物一致 / G8 无占位 |
| A-3 | `python3 scripts/onto1_obligation_triage.py --selftest` | **0** | 11/11 用例符合预期（M0 对照 + M1/M2a/M2b/M3/M4/M5/M6/M8/M9 变异 + M7 恢复对照） |

> **未在本包写门禁日志**（`evidence/*.log`）：`wi_evidence_board_check` 当前 PASS，若我先落
> `wi_a2_obligation_triage-*.log` 而门禁尚未登记，会**产生孤儿日志 ⇒ 板面转 fail**。故按
> `EVIDENCE.json` 既有惯例，日志由 TL 在 `record_gate.py` 记账时生成（AU-2 也要 TL 亲自复跑）。

## 2. 开发期自审发现的缺陷（F-1~F-3，首次 --gate 之前）

| # | 现象 | 根因 | 变更 | 复验 |
|---|---|---|---|---|
| F-1 | `SyntaxError: invalid syntax` @ `render_report` | 报告文案里把中文引号写成 ASCII `"`，把字符串切断 | 统一改中文书名/引号 `「」`（4 处） | `ast.parse` OK |
| F-2 | `ValueError: ... is not in the subpath of ...`（夹具目录） | 摘要里 `relative_to(ROOT)` 对仓外夹具路径不成立 | 增 `_rel()`（仓外原样返回） | 夹具 M0 PASS |
| F-3 | M0 对照 FAIL：`G3 no path-level strong hit` + `G7 true_by_wave drifted` | ① 夹具缺"仅路径强信号"样本；② `dirs_sorted` 是 tuple，JSON 往返后变 list ⇒ 比较永远不等 | ① 夹具补 `specs/gk-ke/v1/README.md`（无 IRI 的裸术语）；② `dirs_sorted` 统一转 list-of-list | 9/9 → 11/11 |

## 3. 门禁 PASS 后的口径修订（F-4~F-6，每次重跑）

| # | 问题（自审发现） | 判断 | 变更 | 复验（exit） |
|---|---|---|---|---|
| F-4 | 首版 M2a/M2b/M6 变异**没被拦住**：行级断言只跑"复算结果"，而 CSV 才是交付物 ⇒ 改 CSV 不影响 G4/G5 | **门禁单向校验 = 空转风险** | `run_checks` 重构为**双向**：行级断言跑 `computed` 与 `disk` 各一遍，G7 再做逐行一致性；M4 短路由 G3[computed] 捕获 | `--selftest` 10/11 → 11/11；`--gate` 0 |
| F-5 | 同名证明过宽：① 只要出现 `import <dto>.<Xxx>TokenXxx` 就判同名；② 只要同行有 `OpenAPI` 就判同名（H4） | **过宽 = 会误把真消费面排除**：`ClaimResponse` 自述"同时携带两种语义字段"；`HumanGateControllerTest` 同文件 `import com.gien.gits.ontology.*;` ⇒ 裸名解析不唯一 | 删 H4；H2 收紧为「按简单名精确导入 + 来源包 ∈ {dto,contract,api,model} + **无**本体/领域包同名或通配导入」；新增 M8 断言 | `--selftest` 11/11；同名候选 6 → **0**；`--gate` 0 |
| F-6 | 收紧后弱面 97 行全部落 `NEEDS`，但其中一批裸名**精确解析到 `com.gien.gits.ontology.*`**（样本 `ClaimController.java:15`）——这是"回源只差一步"的行，直接混在 426 行待回源里会丢失信息 | **不升格为执法判定**（派工单强信号清单未含此形态），但可作**优先级标签** | 新增 `RESOLVES_TO_ONTOLOGY_PKG:<pkg>` 子标签（证据 = 该导入行，G5 可复核）+ 摘要 `needs_priority` + 报告 §5 分档 + M9 断言 | `--selftest` 11/11；P0=65 / P1=361；`--gate` 0 |

## 4. 关键中间观测（供审计对照）

| 观测 | 值 | 说明 |
|---|---|---|
| 义务行 / 唯一源文件 | 1052 / 731（合计 4.5 MB） | 全部源文件在磁盘存在（0 missing，G1 断言） |
| 弱信号面（I-1 口径） | 97 行 | 82 `apps/api/src` + 7 `scenario/execute/src` + 其余 8；其中 7 行同文件有本体包**通配**导入 |
| 弱信号面（`--strict-weak-surface`，即派工单列举前缀） | **0 行** | 严格口径下 tier WEAK→0，**判定计数不变（626/0/426）** ⇒ I-1 扩展只影响 tier 标签与 G5 保护范围 |
| 替代口径（tier 即判同名） | 同名 97 / 待回源 329 | 见 `summary.alternatives`，供 TL 裁定口径 I-2 |
| 强内容信号文件数 | 83 | IRI/OWL/SPARQL/planHash/gits-core 等 |
| `(repo,path,category)` 唯一性 | 1051/1052 | 有 1 处同键不同 token（`kert src/kert/application/skills.py` id_pattern），故输入身份键取 (repo,path,category,tokens,lines,rule_id) 并断言唯一 |
