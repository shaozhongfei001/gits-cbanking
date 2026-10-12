# GK17 · WP8.0-d PLAN｜修 D1/D2 绕过盲区（W8 必办⑧）

> 编写：`tech_lead`｜`2026-09-17`｜BASE_HEAD：`71169042`（工作区 dirty，以 sha256 为准）
> 触发：独立 QA 报告 §3.7（`evidence/INDEPENDENT_QA-W2-W6-independent-qa.md`）
> 性质：**修 fail-open**（`FAILURES.md` `20260916T121500Z`｜`GATE_FAIL_OPEN_BLINDSPOT`）
> 前置纪律：`record_before_fix`（已记账）→ 本 PLAN → 改码 → **判定逻辑变异复验** → 重落证

---

## 1. 要修的三个绕过（QA 实测 E1/E2/E5，TL 已读源码确认）

| # | 位置 | 缺陷 | 绕过写法 |
|---|---|---|---|
| **E1/E2（D1）** | `:300-315` `is_tbox_statement()`；由 `:322` 生效 | 语句只要含 `a owl:Class`（或 `owl:ObjectProperty`）即**整条**被当作 T-Box ⇒ `relation_instances()` 跳过 | `gits:X a owl:Class ; gits:requiresProduct gits:Y .` |
| **E5（D2）** | `:619` `if not o.startswith("gits:"): continue` | **全 IRI** 写法被整段跳过 —— 而全 IRI 与 `gits:` 前缀是**同一条 RDF 语句的合法等价写法** | `gits:X a <…#NoSuchClass> .` |

---

## 2. 修法（**只收紧，不放宽**）

### 2.1 D1：取消"整条语句"豁免

删掉 `relation_instances()` 里的 `if self.is_tbox_statement(st): continue`。

**论证（为什么删了不会误报）**：T-Box 声明里受控谓词只出现在**主语**位置，从不出现在**谓词**位置 ——

```turtle
gits:requiresProduct a owl:ObjectProperty ;   # 谓词 = type / rdfs:label / rdfs:domain / rdfs:range
  rdfs:label "requires product"@en .          # 受控谓词是【主语】，不是谓词
```

⇒ 只要**按谓词**判定，T-Box 声明天然命中 0 条，**不需要**任何整条豁免。
原豁免的唯一实际效果就是**压掉真阳性**。故**不保留任何豁免**（不引入新的窄豁免 —— 窄豁免会变成下一个盲区）。

**保留 `is_tbox_statement()` 方法本身**（可供后续使用者阅读其语义），但**不再用于**受控谓词判定，并加注释说明原因。

### 2.2 D2：按**局部名**归一化后比对

```python
onto_locals = { term_local_name(c) for c in ontology.classes() }   # gits:Product -> Product
...
if p != "type":                       continue
if is_standard_vocab_ref(o):          continue   # rdf/rdfs/owl/xsd/prov ⇒ 不受 D2 约束
local = term_local_name(o)
if local is None:                     continue
if local in onto_locals:              continue
⇒ finding
```

`term_local_name` 覆盖三种等价写法：`gits:Product` / `<…#Product>` / `<…/Product>`。

### 2.3 ⚠ 修法**故意不**做的一件事（必须写明）

**D2 不做命名空间解析，只比局部名。** 因为 TL 本轮实测到一条**更严重的、独立的**缺陷：

| 侧 | 声明 |
|---|---|
| 本体 `specs/semantic/gits-core.owl.ttl:1` | `@prefix gits: <https://gientech.com/gits/kno/>` |
| 投影 `products.ttl:1`（由 `scripts/gk17_prodcard_to_rdf.py:31` 写出） | `@prefix gits: <https://gits.bank.example/ontology/core#>` |

⇒ **同一前缀、两个命名空间**。IRI 层面 `gits:Product` ≠ `gits:Product`，**A-Box 与 T-Box 不连通**。
⇒ 若把 D2 改为"按命名空间解析"，基线会**立刻整体转红**（13 个个体全部"类型不在本体"）——
那是**语义正确**但在当前状态下会**打破基线 PASS**，且修复要改 `products.ttl`（哈希变化）+ 重跑投影门禁
⇒ 属 **Owner / 产品 Owner 级裁定**（哪个命名空间承载个体），**不在本 PLAN 擅改范围**。

**本 PLAN 的处置**：① 该缺陷**单独记账**；② D2 保持局部名比口径，并把该局限**写进 docstring**；
③ 在 docstring 中明确"**本门禁不做 IRI 级命名空间解析，这是已知且已登记的局限**"。

---

## 3. 新增内置探针（3 条，防盲区**再次**静默存在）

| 探针 | 施加于 | 注入 | 期望 |
|---|---|---|---|
| **E1** | 本体临时副本 | `gits:gk17_e1_probe a owl:Class ; gits:requiresProduct gits:prod_set_001 .` | **D1 计数 > 基线** |
| **E2** | 本体临时副本 | 同上但 `a owl:ObjectProperty` | **D1 计数 > 基线** |
| **E5** | 投影**内存**副本 | `gits:gk17_e5_probe a <https://gits.bank.example/ontology/core#GK17_NO_SUCH_CLASS_E5> .` | **D2 计数 > 基线** |

三条均须满足：期望项**严格增加**；**交叉项不误触发**；撤销回基线；真实文件 sha256 未变。

## 4. 验收命令（原命令，不改一字）

```bash
python3 scripts/gk17_triple_consistency_check.py            # 期望 exit 0，且 E1/E2/E5 三条探针均"已捕获"
python3 scripts/gk17_triple_consistency_check.py --json     # 期望 counts 全 0、vacuity []
python3 scripts/gate_injection_tests.py                     # 期望 gk17-triple-consistency 仍在 OK 列表
python3 scripts/record_gate.py --loop GK17-ontology-unified-map \
        --gate triple_consistency_check --actor tech_lead --actor-role implementation
```

**判定逻辑变异复验**（同 Tick 17 口径，必做）：把三条新探针的"已捕获/交叉项干净"判定分别改成恒假 ⇒ 门禁**必须各自转红**；
且真实脚本 sha256 前后一致。

## 5. 停止条件 / 非声明

- 沿用本 Loop 5 条停止条件，不新增；
- 本 PLAN **不**声称 D1/D2 已被修复 —— **修复完成后**才可声称，且须附复验证据；
- **不**改 `products.ttl`、**不**改本体命名空间（属待裁定项）；
- 本 PLAN 的产出**不构成** `QA_PASS`，**不代表** `PRODUCTION_READY`。
