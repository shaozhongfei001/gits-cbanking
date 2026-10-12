# ONTO1｜IRI 碰撞检查脚本需求规格（C-1~C-4）与变异用例设计（DRAFT）

| 项 | 值 |
|---|---|
| 文档性质 | **DRAFT（草稿）**——候任 Integration Contract Owner 任职技术准备产出；**只出规格，不实现** |
| 状态 | `DRAFT` / `NOT_IMPLEMENTED` |
| 提案脚本名 | `scripts/onto1_iri_collision_check.py`（配套 `scripts/onto1_iri_collision_tests.py`） |
| 依据 | `docs/architecture/ADR-ONTO1-namespace-neutral-iri-DRAFT.md` §5.2（退役门）、§5.3（解析）、**§5.4（C-1~C-4）**；设计 §6.4；执行计划 §5.1、§6；ADR §9 批准路径第 4 步（"碰撞检查脚本实现 + 绿证"，签署方含 Integration Contract Owner） |
| 前置（硬） | **D3 双 Owner 签署根域**。根域未签 ⇒ 脚本**必须 FAIL（无输入即红）**，不得"缺输入就跳过" |
| 现状反例 | 见 §1.2（三个真实样本，逐条回源） |
| 外部对应条目 | `docs/architecture/ONTO1-命名空间ADR联签意见-DRAFT.md` 的 **P-3**（联签前置：脚本可执行 + 变异复验绿，**脚本原型责任归 Integration Contract Owner**）与 **V-3**（复核项）——本文即该前置的**规格载体** |

> **红线声明**：本轮不实现脚本、不接线、不改任何制品；不标 `ACTIVE`；不代签。

---

## 1. 问题域

### 1.1 为什么需要脚本（而非人工检查）

ADR §5.4 的 C-1~C-4 是**发布阻断条件**（"阻断发布"/"具名漂移拒绝"）。人工检查存在三个不可接受的问题：
1. **不可复算**：无法证明"检查过"；
2. **不可变异**：无法证明"检查有牙齿"（GK-KE 程序"假绿"教训）；
3. **不可执法**：`make check` 类门禁无法读取人工结论。

### 1.2 真实现状反例（本脚本存在的直接原因）

| 样本 | 回源（文件:行） | 问题 |
|---|---|---|
| 前缀 `gits:` 指向 A 命名空间 | `specs/semantic/gits-core.owl.ttl:1` → `https://gientech.com/gits/kno/` | 与下一条**同前缀不同命名空间** |
| 前缀 `gits:` 指向 B 命名空间 | `specs/knowledge-architecture/instances/product/products.ttl:1` → `https://gits.bank.example/ontology/core#` | ⇒ C-2 违反；且造成 T-Box/A-Box **IRI 层不连通**、`vacuous=true` |
| 前缀 `gits:` 指向 A 命名空间（第三处） | `specs/data/customer-source-mapping.r2rml.ttl:2` → `https://gientech.com/gits/kno/` | 说明该错配**不止一处**，须全仓扫描 |

ADR §5.4 明确：**此缺陷必须先修**（否则新 IRI 迁移会叠加一层错配）。

---

## 2. 总体设计约束（沿用本 Loop 已验证的模式）

必须复用 ONTO1 已有的**防假绿三件套**（见 `loops/ONTO1-ontology-split/memory/ORCHESTRATOR.md` §4、`scripts/onto1_consumer_scan.py` 文件头注释）：

| # | 要求 | 具体含义 |
|---|---|---|
| **A** | **单一真值函数** | 所有判定只由一个 `detect_*()` 产出；`--report` 与 `--gate` 共用同一实现（不得"报告一套、门禁一套"） |
| **B** | **fail-closed** | 任何输入缺失/不可解析/清单为空 ⇒ **FAIL**，绝不"缺夹具即跳过"（GK-KE `FAIL-2026-09-12-02` 教训：生成期标志位短路 ⇒ 变异不被捕获 ⇒ 假绿） |
| **C** | **变异复验** | 每条规则配 `mutate → 必须 FAIL` / `restore → 必须 PASS`；含**元变异**（把判定替换为恒真 ⇒ 必须被 M-元 捕获） |
| **D** | **期望值锚定** | 用 §1.2 的已知反例做锚点，扫描**必须检出**；检不出 ⇒ FAIL（而非"0 命中即绿"） |

**判定驱动方式**：门禁**不得**读取某个"检查通过"标志位来决定结果；必须**由规则复算**（读制品 → 构建集合/映射 → 断言）。

---

## 3. 接口契约（提案）

### 3.1 CLI

| 命令 | 作用 | 退出码 |
|---|---|---|
| `python3 scripts/onto1_iri_collision_check.py --gate` | 执行 C-1~C-4，任一 FAIL ⇒ 非 0 | 0 / 1 |
| `python3 scripts/onto1_iri_collision_check.py --report` | 输出机读报告 + 人类摘要（不判门禁） | 0 |
| `python3 scripts/onto1_iri_collision_check.py --selftest` | 跑 §7 变异矩阵 | 0（全符合预期）/ 1 |
| `--out-dir <path>` | 证据输出目录（默认 `loops/ONTO1-ontology-split/evidence/`） | — |

### 3.2 输入

| 输入 | 形态 | 缺失时 |
|---|---|---|
| `namespaces.json`（ADR §4 的 `{NS-L1..NS-L4}` 映射） | 机读 | **FAIL**（根域未签 ⇒ D3 未完成，不得继续） |
| oldIRI→newIRI 映射表（ADR §5.1 三分法 + 映射状态） | 机读 CSV/JSON | **FAIL** |
| 旧/新 IRI 清单（从 TTL/JSON-LD/R2RML 解析所得） | 由脚本 `rdflib` 解析生成 | **FAIL** |
| import 入口清单（显式登记的 closure 起点） | 机读 | **FAIL**（不得自动"全仓闭包"，会误报） |
| 钉值文件（侧车形态，见 C-4） | 机读 | **FAIL** |

**占位值规则**：`namespaces.json` 中出现 `bank.example`、`example.com`、`localhost`、`TBD`、空串等 ⇒ **FAIL**（沿用 `scripts/contract_pipeline.py:217` `reject_placeholders` 同型纪律；ADR §12 纪律声明逐字要求）。

### 3.3 输出（机读）

```json
{
  "schema": "onto1_iri_collision_report/v1",
  "generatedAt": "…",
  "inputs": {"namespaces": {"path": "…", "sha256": "…"}, "pins": {"sha256": "…"}},
  "checks": [
    {"id": "C-1", "verdict": "PASS|FAIL", "detail": {…}, "evidence": ["file:line", "…"]},
    {"id": "C-2", "verdict": "…", "detail": {"prefixToNamespaces": {…}, "conflicts": [{"prefix":"gits","namespaces":["…","…"],"sites":["specs/…:1"]}]}},
    {"id": "C-3", "verdict": "…", "detail": {"closures": [{"entry": "…", "series": "…", "versions": ["…"]}]}},
    {"id": "C-4", "verdict": "…", "detail": {"mismatches": [{"artifact": "…", "declared": "…", "actual": "…"}]}}
  ],
  "anchors": {"expectedDetections": 3, "detected": 3},
  "verdict": "PASS|FAIL"
}
```

**报告铁律**：`checks[].evidence` 必须是 `文件:行`（可回源），不得只给结论（对齐 GOV-CFI-001 的 C2 回源纪律）。

---

## 4. 四条检查的详细规格

### 4.1 C-1 集合互斥

| 项 | 规格 |
|---|---|
| 判据（ADR §5.4 逐字） | `set(oldIRI) ∩ set(newIRI) == ∅` |
| 真值函数 | `detect_c1(old_iris, new_iris) -> Collisions` |
| 细则 1（**防空转**） | 额外断言 `newNamespace != oldNamespace`。**否则**：若新旧前缀相同而无共同元素，C-1 会"平凡通过"（集合交集为空但迁移毫无意义）⇒ 必须 FAIL。此细则是对 ADR 字面判据的**必要加严**，须 Owner 确认（§8 待裁定 R-1） |
| 细则 2 | 比较对象是**逐术语**的 old/new 集合，不是"全仓所有 IRI 的并集"（否则新 IRI 必然与自身冲突） |
| 细则 3 | LEGACY 区（已退役但保留记录）**不计入** new 集合 |
| 失败动作 | **阻断发布** |
| 变异 | `M-C1-1`：把某条 new IRI 改为其 old IRI 原值 ⇒ FAIL；`M-C1-2`：新旧命名空间相同 ⇒ FAIL；`M-C1-3`：把 new 集合留空 ⇒ FAIL（fail-closed，空集与任何集合交集都为空，是天然假绿漏洞） |

### 4.2 C-2 前缀唯一

| 项 | 规格 |
|---|---|
| 判据 | 同一短前缀不得指向两个命名空间 |
| 真值函数 | `detect_c2(sites) -> Conflicts`；`sites` = 扫描所得的 `(file, line, prefix, namespaceIRI)` |
| 扫描范围 | 仓库内 `@prefix` 声明（Turtle/TTL）、JSON-LD `@context`、R2RML 前缀、SPARQL `PREFIX` |
| 豁免 | 需**具名豁免登记**（文件:行 + 理由 + 责任 Owner + 到期日），且：**首次修复前豁免不得掩盖 C-2**（ADR §5.4 明确"必须先修"）；**全豁免 ⇒ FAIL**（与 WI-A2 "全豁免 ⇒ FAIL"同型纪律） |
| 排除 | `.git`、`node_modules`、`target`、`__pycache__`、`.ua`、生成物（`generated/` 若为生成产物则单独判定）——须显式登记排除清单，**不得**用宽泛 glob 悄悄排除 |
| 失败动作 | **阻断发布（修前缀）** |
| 变异 | `M-C2-1`：把 `products.ttl:1` 改回 `gientech.com/gits/kno/`（消除冲突）⇒ PASS；再改回 `gits.bank.example` ⇒ FAIL（**双向**验证有牙齿）；`M-C2-2`：把冲突文件加入豁免清单并全豁免 ⇒ FAIL |

**现状锚点**：`specs/knowledge-architecture/instances/product/products.ttl:1` vs `specs/semantic/gits-core.owl.ttl:1` 必须被检出（§2-D）。

### 4.3 C-3 import closure 单版本

| 项 | 规格 |
|---|---|
| 判据（ADR §5.4 逐字 + 设计 §6.4） | import closure 内同一 ontology series 不得出现两个 `versionIRI` |
| 真值函数 | `detect_c3(entries) -> Violations` |
| series 判定 | 由 `owl:versionIRI` + `dcterms:isVersionOf` / 命名约定去版本号得到 series 根；若无法判定 series ⇒ **FAIL**（不得"判不出就跳过"） |
| closure 起点 | **必须**用显式登记的入口清单；入口清单为空 ⇒ **FAIL** |
| 失败动作 | **阻断发布** |
| 变异 | `M-C3-1`：让 closure 同时 import `x@1.0.0` 与 `x@1.1.0` ⇒ FAIL；`M-C3-2`：清空入口清单 ⇒ FAIL（防空转）；`M-C3-3`：只 import 一个版本 ⇒ PASS（对照） |

### 4.4 C-4 钉值一致

| 项 | 规格 |
|---|---|
| 判据 | 制品内容哈希 == 钉值文件声明哈希 |
| 真值函数 | `detect_c4(pins) -> Mismatches` |
| 失败动作 | **具名漂移拒绝**（报告须给出 artifact / declared / actual 三值） |
| **结构性约束（历史教训固化）** | 钉值**必须侧车登记**：`contentHash` **不得**写入被哈希的制品自身。反例：GK-KE 程序 `FAIL-2026-09-12-03` —— 把 `contentSha256` 写进被哈希文件自身 ⇒ **永不收敛**。本脚本须**主动检测**"钉值文件是否是其所哈希制品的子集/同一文件" ⇒ 是则 FAIL |
| 另一约束 | 钉值文件自身也须有哈希（或纳入版本控制 + 内容冻结），否则"改钉值即可让 C-4 通过" ⇒ 假绿。检测：钉值文件必须被**独立的冻结记录**（如 `evidence/` 清单哈希）覆盖 |
| 变异 | `M-C4-1`：改制品 1 字节 ⇒ FAIL；`M-C4-2`：改钉值以匹配被改动制品 ⇒ FAIL（证明钉值文件自身受冻结保护）；`M-C4-3`：把钉值写回被哈希文件 ⇒ FAIL（自引用检测）；`M-C4-4`：不动 ⇒ PASS（对照） |

---

## 5. 退役门联动（ADR §5.2，脚本须能支撑而非替代）

ADR §5.2 的退役门四条中，本脚本负责 **第 2、3 条**（"新旧 IRI 碰撞检查绿"、"import closure 单版本"）；**第 1 条**（WI-A2 处置表 100% 关闭或具名豁免）与**第 4 条**（双侧 Owner 签署）为**人工/其他门禁**责任。

**脚本禁止**：不得把"本脚本绿"表述为"退役门通过"（防越权声明）。报告中须固定输出：

```
refirement_gate_scope: ["C-2 碰撞检查", "C-3 import closure 单版本"]
not_covered: ["WI-A2 处置表关闭", "双侧 Owner 签署"]
```

---

## 6. 与 ADR 批准路径的对应（ADR §9）

| ADR §9 步 | 动作 | 签署方 | 本规格的作用 |
|---|---|---|---|
| 2 | 填根域与解析机制（U-1/U-2） | 语义架构 Owner + 域名 Owner | 解锁本脚本的**输入** |
| 3 | 确认 L1/L2/L4 命名规则与产权字段（U-4） | 公共语义 Owner（待任命） | 锁定 §4.1 的 `NS-L*` 语义 |
| **4** | **碰撞检查脚本实现 + 绿证** | **Integration Contract Owner（待任命）+ TL** | **本规格即第 4 步的输入** |
| 5 | ADR 转 `ACCEPTED` | 双 Owner 联签 | 本脚本绿证是依据之一 |

**因此**：本脚本是 ADR 定稿的**前置**，但脚本**不能先于 U-1/U-2 正常运行**（无根域 ⇒ FAIL）。这不矛盾：**脚本可以先实现并以"FAIL（缺根域）"为正确行为**，这本身就是 fail-closed 的证明。

---

## 7. 变异用例矩阵（`--selftest`，提案）

| # | 变异 | 期望 | 捕获的假绿类型 |
|---|---|---|---|
| M-0 | 全对照（无变异） | `--gate` PASS / `--selftest` 全符合 | 基线 |
| M-C1-1 | new IRI 同于 old IRI | C-1 FAIL | 直接违反 |
| M-C1-2 | 新旧命名空间相同 | C-1 FAIL | **平凡通过**（ADR 字面判据的漏洞） |
| M-C1-3 | new IRI 集合为空 | C-1 FAIL | **空集假绿** |
| M-C2-1 | 消除 `products.ttl:1` 冲突 → 再还原 | 消除⇒PASS；还原⇒FAIL | 单向验证不足 |
| M-C2-2 | 冲突项全豁免 | C-2 FAIL | **全豁免假绿** |
| M-C2-3 | 把冲突文件加入宽泛排除 glob | C-2 FAIL | 悄悄排除假绿 |
| M-C3-1 | closure 含同 series 两版本 | C-3 FAIL | 直接违反 |
| M-C3-2 | 入口清单为空 | C-3 FAIL | **空输入假绿** |
| M-C3-3 | 单版本 closure | C-3 PASS | 对照 |
| M-C4-1 | 改制品 1 字节 | C-4 FAIL | 直接违反 |
| M-C4-2 | 同步改钉值以匹配 | C-4 FAIL | **改标准以通过测试** |
| M-C4-3 | 钉值写回被哈希文件 | C-4 FAIL（自引用检测） | **指纹自引用**（GK-KE FAIL-2026-09-12-03） |
| M-元 | 把 `verdict` 判定替换为恒 `PASS` | M-C1-1..M-C4-3 全部失去判别力 ⇒ 元变异被捕获 | **门禁空转**（GK-KE FAIL-2026-09-12-02） |
| M-输入 | 删 `namespaces.json` | FAIL（不得跳过） | **缺夹具即绿** |

**通过标准**：`M-0` 全绿 + 其余每条 `mutate → FAIL` / `restore → PASS`，且**记录实际输出文本**（不记"绿/红"）。

---

## 8. 待裁定与风险

| # | 项 | 说明 | 建议 |
|---|---|---|---|
| R-1 | C-1 的"新旧命名空间必须不同"是否作为**判据的一部分** | ADR §5.4 只写了集合交集为空；但仅按字面判据存在平凡通过漏洞（M-C1-2） | 加严，并**回写 ADR §5.4**（属客观落实，非范围扩大） |
| R-2 | C-2 的豁免机制上线顺序 | ADR §5.4 要求"必须先修"，但修复（改 `products.ttl:1`）属 Wave 3 动作 | 脚本先上线且对冲突**不豁免**（红），修复后转绿；禁止"先豁免后修" |
| R-3 | 扫描范围是否含 `generated/` | 生成物由源决定，扫描会产生重复计数 | 默认排除并在报告中显式声明（不得静默） |
| R-4 | series 判定规则的精确形态 | `owl:versionIRI` 是 MAY（设计 §6.4），部分制品可能没有 | 无 `versionIRI` ⇒ 按 FAIL 处理（fail-closed）或具名豁免；须裁定 |
| R-5 | 脚本工具依赖（`rdflib`）可用性 | WI-A1 已用 `rdflib` 复现 32/34/1，环境可用（回源：`evidence/WI-A2-消费者扫描报告.md` 与 WI-A1 门禁日志） | 沿用 |
| R-6 | 脚本名/门禁 ID 的最终命名 | 提案名可能与 TL 既有约定冲突 | 提交 TL 批准 |

---

## 9. 门禁接线建议（提案，**不接线**）

| 门禁 ID（提案） | 命令（提案） | 阶段 |
|---|---|---|
| `iri_collision_check` | `python3 scripts/onto1_iri_collision_check.py --gate` | Wave 2（IRI 迁移）+ Wave 3（退役门） |
| `iri_collision_selftest` | `python3 scripts/onto1_iri_collision_tests.py` | 与上同批 |
| `iri_collision_anchor` | 内嵌于 `--gate`：§1.2 三处真实反例必须被检出 | 防"0 命中即绿" |

**接线前置**：D3 签署 + Integration Contract Owner 任命 + K-裁定（`docs/architecture/ONTO1-CTR-SEM-拆条登记草案-DRAFT.md` §7）。

---

## 10. 变更记录

| 版本 | 日期 | 变更 | 作者 |
|---|---|---|---|
| DRAFT-v0.1 | 2026-09-20 | 初稿（仅需求规格，未实现） | 候任 Integration Contract Owner（AI 起草） |

> 草稿，签字权在人类 Owner。
