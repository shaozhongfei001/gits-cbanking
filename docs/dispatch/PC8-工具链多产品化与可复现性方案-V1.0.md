# PC8 · 工具链多产品化与可复现性方案 V1.0

```text
提交人：tech_lead（TL）｜ 时间：2026-09-22
归属批次：loops/PC8-tools-byproduct（W1 关键路径，实施角色 tech_lead）
本件性质：**方案先行**（未改一行代码）。按该批次派工卡「先方案后改码」执行。
触发：规划 W2「13 卡 × 7 类产物 = 84 单元」时实测发现，障碍**不是** 4 个常量，而是结构性单族实现。
```

## 1. 实测事实（全部 `文件:行`）

### 1.1 单产品硬编码（4 处）

| 文件:行 | 内容 |
|---|---|
| `tools/l11_extract_evidence_spans.py:73` | `PRODUCT_ID = "PROD-CM-001"` |
| `tools/l12_detect_conflicts.py:46` | 同上（产物文件名与 `productId` 均由它派生） |
| `tools/l13_apply_decisions.py:40` | 同上 |
| `tools/l13_publish_release.py:52` | 同上（`04_serve/interpretation/{PRODUCT_ID}.json`、`rule-packages/{PRODUCT_ID}.*` 硬写） |

### 1.2 **单族硬编码**（比 1.1 更根本）

`tools/l11_extract_evidence_spans.py:112-119`：

```python
def load_policy_fields():
    """从 CTR-PK-FLD-001 的 CASH_MANAGEMENT 正例读取七字段策略。"""
    doc = json.loads(POLICY.read_text(encoding="utf-8"))
    for ex in doc.get("examples", []):
        if ex.get("productFamily") == "CASH_MANAGEMENT":   # ← 族名写死
            return ex
```

⇒ 无论换什么 `PRODUCT_ID`，取到的**永远是现金管理族的 7 个字段**。

### 1.3 字段策略实例缺口（**W2 的真正拦路石**，`F-PC8-03`）

`specs/product-knowledge/field-policy.schema.json` 的 `examples` 实测仅 **2 条**：

| 实例 | 族 | 字段数 | `ownerApproved` |
|---|---|---:|---|
| `FLD-CASH_MANAGEMENT-001` | CASH_MANAGEMENT | 7 | `false` |
| `FLD-SETTLEMENT-999` | SETTLEMENT | 1 | `false` |

而产品卡分布 **6 个族 / 13 张卡**：CASH_MANAGEMENT 3 · FINANCING 3 · SETTLEMENT 2 · TRADE_FINANCE 2 · CROSS_BORDER 2 · INVESTMENT_BANKING 1。

⇒ **5 个族（FINANCING / TRADE_FINANCE / CROSS_BORDER / INVESTMENT_BANKING 及 SETTLEMENT 的完整字段集）没有可用字段策略实例**。
⇒ 这属**合同候选面**（`CTR-PK-FLD-001`），不是 KERT 侧工具能自行补齐的东西 —— 必须走 gits 受控合同流程。

### 1.4 版本范围常量与产品卡实际目录**全都不一致**（`F-PC8-02`）

- 常量：`tools/l11_extract_evidence_spans.py:74` → `PRODUCT_VERSION_SCOPE = "version=2026.09.06.1"`
- 实际卡目录：`cash-management` / `cross-border` / `settlement` / `trade-finance` / `investment-banking` = `version=2026.09.01.1`；`financing` = `version=2026.08.31.1`
- ⇒ 断言里的 `productVersionScope` **与任何一张卡的目录版本都不匹配**（非空但错的引用）。
- 相关未决：`load_policy_fields` 返回的实例里 `productFamily` 是族、而 `l11` 把它当"产品级策略"用；`SETTLEMENT` 实例 `policyId` 后缀 `-999` 形态与其他不同，疑为**反例/占位**（需合同 Owner 确认其定位）。

### 1.5 非确定性：摄入时间取 wall clock（`F-PC8-01`）

`tools/l10_build_source_versions.py:154` → `ingested = now_cst()`；`build_one`（`:119-121`）用它生成 SV 标识：

```python
date_part = ingested.strftime("%Y%m%d")
sv_id = f"SV-{sid_key(source_id)}-{date_part}-{bytes_sha[:8]}"
```

且 `ingestedAt` / `generatedAt` / `runId` 均含该时间 ⇒

1. **同日重跑**：SV 文件名不变、内容变（`ingestedAt` 变）⇒ **字节不一致**；
2. **跨日重跑**：SV 文件名变 ⇒ **新件产生 + 旧件残留**（当前无清理逻辑）。

### 1.6 门禁强制"无陈旧件"

`tools/check_l10_sources.py:74-77`：

```python
sv_files = sorted(p for p in SV_DIR.glob("SV-*.json"))
check("SourceVersion 文件数 == manifest 声明", len(sv_files) == len(man.get("sourceVersions", [])))
```

⇒ 只要留下跨日旧件，L10 门禁必然 FAIL。**因此重跑必须是"幂等重建"**（清理后全量重生成），这与 ADR-017「清空 ⇒ 同集重灌 ⇒ 核对覆盖与出处一致」的重建口径**同构**。

### 1.7 既有产物覆盖（重跑前的基线）

`02_work/`：source-versions 3 · fragments 3 · evidence-spans 4 · assertions 1 · candidate-cards 1 · conflicts 1 · reports 1；
`04_serve/`：interpretation 1 · rule-packages 1 · releases 1 —— **全部仅 PROD-CM-001（源级仅 CM 三源）**。

---

## 2. 结论：W2 的工作量与归属（不是"改常量"）

| # | 工作项 | 类型 | 归属 | 前置 |
|---|---|---|---|---|
| `T1` | `--product` / `--all` 参数化（4 脚本），默认值保持 `PROD-CM-001` ⇒ 既有行为不变 | 工程 | KERT `tools/` | 无 |
| `T2` | 去掉族名硬编码：按族选策略实例；**找不到即 fail-closed 退出非零并列出缺失族**（不得默认回落到 CASH_MANAGEMENT） | 工程 | KERT `tools/` | `T3` |
| `T3` | 为缺实例的族补**字段策略实例**（合同候选） | **合同面** | gits `specs/product-knowledge/` | 合同 Owner / 门禁 |
| `T4` | `productVersionScope` 由产品卡目录名派生，删除常量 | 工程 | KERT `tools/` | 无 |
| `T5` | 可复现：新增 `--run-date YYYY-MM-DD`（或 `SOURCE_DATE_EPOCH`），默认仍取 `now`（向后兼容） | 工程 | KERT `tools/` | 无 |
| `T6` | 幂等重建：重跑前清理 `02_work/source-versions/SV-*.json` 与 `02_work/fragments/*.fragments.json`（**仅这两类**），并在提交信息留痕 | 工程（有破坏性） | KERT `tools/` | `T5` |

**关键判断**：`T3` 不在 KERT 工具链里能解决 —— 只要 5 个族没有字段策略实例，跑 13 卡只会产出"全 UNKNOWN"的空壳，**看起来在干活，其实不产生可用断言**。故 `T3` 是 W2 的真前置。

---

## 2.1 新增 Owner 级阻塞 `B-5`：字段策略未批准 ⇒ 断言强制 UNKNOWN

`tools/l11_extract_evidence_spans.py:218`：

```python
if spec.get("ownerDecisionRequired") and not policy.get("ownerApproved", False):
    matched = []          # ⇒ knowledgeState 一律 UNKNOWN
```

实测：`CASH_MANAGEMENT` 实例 `ownerApproved=false`，且 **1/7** 字段带 `ownerDecisionRequired` ⇒ 该字段断言被强制 UNKNOWN；
既有 `02_work/assertions/PROD-CM-001.assertions.json` 的 18 条断言中确有 **3 条 UNKNOWN**，`policyOwnerApproved: false`。

⇒ **即使补齐 5 族实例，未获 Owner 批准前，带 `ownerDecisionRequired` 的字段仍是 UNKNOWN。** 这不是缺陷，是设计上的"未批准不得取值"。
⇒ 请 Owner 明确：**批准 `CTR-PK-FLD-001` 实例（逐族）**，或**确认长期保持 UNKNOWN 口径**（则该字段在解读页只能显示"未核验"）。

---

## 3. 最小 diff 设计（伪代码级，实施时逐条留证）

```python
# T1+T4：常量 → 可覆写（默认值不变，保证 PROD-CM-001 行为字节级不变）
DEFAULT_PRODUCT_ID = "PROD-CM-001"
PRODUCT_ID = DEFAULT_PRODUCT_ID            # 模块级，保持既有引用点不动

def resolve_version_scope(product_id, cards_root):   # T4
    ...  # 从 03_core/*/version=<x>/product-cards/{product_id}.md 派生 "version=<x>"

def main():
    global PRODUCT_ID, PRODUCT_VERSION_SCOPE
    ap.add_argument("--product", default=DEFAULT_PRODUCT_ID)
    ap.add_argument("--all", action="store_true")
    targets = discover_products(cards_root) if args.all else [args.product]
    for pid in targets:                     # --all ⇒ 逐产品调用同一核心函数
        PRODUCT_ID = pid
        PRODUCT_VERSION_SCOPE = resolve_version_scope(pid, cards_root)
        run_core_for_product(pid)           # main 主体抽成函数，逻辑零改动

# T2：族策略选择（fail-closed）
def load_policy_fields(family):
    for ex in doc.get("examples", []):
        if ex.get("productFamily") == family:
            return ex
    raise SystemExit(f"FAIL | 无 {family} 字段策略实例（CTR-PK-FLD-001）—— 拒绝回落默认族")
```

## 4. 可复算判据（字节不变性，只写做得到的）

| 判据 | 命令/方法 | 通过条件 |
|---|---|---|
| `J1` 固定时钟可复现 | `--run-date 2026-09-22` 连跑两次，比对 `02_work/source-versions/*.json` + `02_work/fragments/*.json` 的 `sha256sum` | **逐字节一致** |
| `J2` 无陈旧件 | `python3 tools/check_l10_sources.py` | 全 PASS（SV 文件数 == manifest 声明） |
| `J3` 语义不变 | 固定 run-date 下，`PROD-CM-001` 的 assertions / candidate-card / conflicts 与现库比对 | 差异**逐项列出并说明**（不主张无条件一致） |
| `J4` 覆盖完整 | `--all` 后统计 `02_work` 各目录产品数 | 7 类产物 × 13 卡齐备，或缺 `T3` 时**显式标注未覆盖族** |
| `**不主张**` | 无 `--run-date` 的 `now` 重跑一致 | **做不到就不写进判据** |

## 5. 施工顺序与回退

```
T5（可复现）→ T6（幂等重建）→ T1+T4（参数化）→ T2（族 fail-closed）→【T3 合同面，并行推进】→ 全链跑 13 卡 → gates
```

- `T1`/`T4`/`T5` 属**纯参数化**（默认路径行为不变）⇒ 出问题可回退到默认参数；
- `T6` **有破坏性**（删 `02_work` 两类产物）⇒ 执行前先落一份 `02_work` 快照（目录级备份）；**不删**其他目录；
- `T3` 属合同面 ⇒ 走候选与门禁，**不直接改 schema 的 examples 绕过流程**。

## 6. gate 映射（批次 `PC8-tools-byproduct` 的验收）

| gate（`LOOP.yaml`） | 命令 | 与本方案的关系 |
|---|---|---|
| `contract_check` | `make check` | `T3` 合同面变更后必须仍绿 |
| `unified_gate` | `python3 specs/product-knowledge/check_all.py` | 含 KERT L10–L13 六项门禁 ⇒ `J2`/`J4` 的机器判定 |
| `l13_release` | `check_l13_release.py` | 13 卡 Release/投影结构合法性 |

## 7. 边界（本件做了什么、没做什么）

- **未改一行代码**；未跑 `l10`（避免在幂等重建口径确定前产生 17 个 SV + 跨日旧件残留）；
- 未改 `specs/` 任何合同与实例；未改 `EGRESS_ROOTS`；未灌入任何文档；
- 未删任何既有产物。KERT 工作区他人在飞改动**零夹带**。
