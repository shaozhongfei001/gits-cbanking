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

---

## 8. V1.1 更正（append-only · 2026-09-22T10:08:03+00:00）

> 本节**只更正我自己写错的判断**，不修改上文原文。

### 8.1 `F-PC8-01` 前半段**不成立**（我误读）

| 我 V1.0 的说法 | 实测 | 更正 |
|---|---|---|
| 「摄入时间取 wall clock ⇒ **不可复现**」 | `tools/l10_build_source_versions.py:49-53` 的 `now_cst()` **已支持 `SOURCE_DATE_EPOCH`**（`l11` 同）；**8 个脚本**均支持；隔离副本实测：固定 epoch 连跑两次 **逐字节一致**（17 源 / 319 片段，`diff` 空） | **确定性已具备**（reproducible-builds 约定，docstring 第 3 条已写明）⇒ **`T5` 零改造**，只需按约定固定 epoch |

**仍然成立的部分**：默认（不设 epoch）取 `now` ⇒ **跨日重跑**产生新 SV 文件名（id 含日期）且**旧件残留** —— 隔离副本实测 **SV 文件 34 vs manifest 声明 17**。

### 8.2 `F-PC8-02` 降级为「语义待澄清」（不是缺陷）

常量 `version=2026.09.06.1` 与产品卡目录版本（`09.01.1` / `08.31.1`）不一致，**但与既有 Release `RLS-2026.09.06.1` 一致** ⇒ 需澄清 `productVersionScope` 的预期语义是**卡目录版本**还是**Release 版本**。**澄清前不改（`T4` 挂起）**。

### 8.3 新增 `F-PC8-05`：期望值**双点**

`tools/check_l10_sources.py:151` 另有硬编码 `DEMO 源数量 == 3`，与 `tools/check_registry_consistency.py` 的 `EXPECTED_DEMO` 构成**双点期望值** ⇒ 应单点化（读 registry §5.8）。
**现在不改**：真实仓当前仅 3 个 SV ⇒ 该检查现实通过；改成 17 会**立刻让 `unified_gate` 变红**（须与跑 pipeline 同批）。

### 8.4 新增 `T7`（W2 步骤）：回填 registry「条款数」

`tools/check_l10_sources.py:117-119` 要求「条款数 == 登记表声明」；隔离副本实跑显示 14 个新源的**登记表为 `None`**（§5.8 入库记录里记的是「待抽取」）⇒ **跑完 `l10` 后必须机械回填真实抽取数**（数据取自 pipeline 产物，非编造）。

### 8.5 `T6` 已实施并验证

`tools/l10_build_source_versions.py` 新增幂等重建（重建前清理 `SV-*.json` 与 `*.fragments.json`，**只清这两类**）。实测：

| 验证 | 结果 |
|---|---|
| 跨日重跑 | `PRUNE | 清理上一轮产物 34 个` → **SV 17 == manifest 17**（该门禁项转绿） |
| 同 epoch 连跑两次 | **逐字节一致** ⇒ 幂等重建**未破坏**可复现性（`J1` 仍成立） |
| 真实仓影响 | **零影响**（本次未在真实仓跑 `l10`；真实仓 `02_work` 未变动，`unified_gate` 保持绿） |

### 8.6 工作项表（更正后）

| # | 状态 |
|---|---|
| `T5` 可复现 | **已具备**（零改造，按既有约定固定 `SOURCE_DATE_EPOCH`） |
| `T6` 幂等重建 | **已实施 + 已隔离验证** |
| `T1` `--product`/`--all`、`T4` 版本派生 | 待做（`T4` 先澄清语义） |
| `T2` 族选择 fail-closed | 待做（依赖 `T3`） |
| `T3` 5 族字段策略实例 | **待 Owner（`B-5b`）** |
| `T7` 回填 registry 条款数 | 新增，属 W2（跑 `l10` 同批） |

---

## 9. V1.2 —— `T1`/`T2` 已实施 + **`F-PC8-07` 实证（W2 阻塞级）**

> append-only · 2026-09-22T10:20:04+00:00

### 9.1 `T1`/`T2` 已实施（4 个脚本，默认值不变）

| 脚本 | 改动 |
|---|---|
| `l11_extract_evidence_spans.py` | 模块级 `_resolve_args()`（`--product` / `--family` / `--all`）；`load_policy_fields(family)` **fail-closed**；`discover_products()` 从 `03_core` 目录派生 |
| `l12_detect_conflicts.py` | 模块级 `--product` 解析（15 行内） |
| `l13_apply_decisions.py` | 同上 |
| `l13_publish_release.py` | 同上（`parse_known_args` 与既有 `--decisions` 不冲突） |

### 9.2 隔离副本实测（`SOURCE_DATE_EPOCH` 对齐既有 manifest `2026-09-06T12:00+08:00`）

| 验证 | 结果 |
|---|---|
| **默认参数下源级产物** | 3 个 `SV-*.json` + 3 个 `*.fragments.json` 与真实仓 **逐字节一致** ⇒ 参数化未破坏既有行为 |
| **evidence-spans** | 逐字段一致，**仅 `extractionRunId` 不同**（该 id 是 run 级：由全部源 span 集合派生，源变多必然变） —— 非缺陷 |
| **`T2` fail-closed** | `--family FINANCING` ⇒ `FAIL | 未找到 FINANCING 的字段策略实例…按 fail-closed 拒绝回落其他族` · **exit=1**（不经管道实测） |
| **`T1` 参数化生效** | `l11 --product PROD-SET-001 --family SETTLEMENT` → 产出 `PROD-SET-001.assertions.json`；`l12 --product PROD-SET-001` → 产出 `PROD-SET-001.conflicts.json` 与 `candidate-card.json` |

### 9.3 `F-PC8-07`（**已实证**）：`l11` **没有"源 ↔ 产品"绑定** ⇒ 跨族串味

同一句断言、同一 epoch，仅**源集规模**不同，`PROD-CM-001` 的证据来源变为：

| 场景 | 断言数 | 证据引用来源 |
|---|---:|---|
| 真实仓（3 源） | 18 | `SRC-CM-001`: 11 · `SRC-CM-002`: 1 · `SRC-CM-003`: 4 |
| 副本（17 源） | 19 | `SRC-CM-001`: 7 · `SRC-CM-002`: 1 · `SRC-CM-003`: 3 · **`SRC-CB-001`: 1** · **`SRC-FIN-001`: 1** · `SRC-XFAM-001`: 2 · `SRC-XFAM-003`: 1 |

⇒ **现金管理产品（`PROD-CM-001`）的断言引用了跨境族（`SRC-CB-001`）与融资族（`SRC-FIN-001`）的证据。**
根因：`l11` 对**全部** fragments 无差别匹配（只按 claimType + 关键词 + 权威级过滤），**不校验该源是否被本产品登记引用**（registry §5「被引用产品卡」列**没有被工具读取**）。

**这是 W2 的阻塞级缺陷**：若直接跑全链，13 卡会产出**"看起来完整、实际串味"**的断言 —— 典型「看起来在干活」。

### 9.4 新增 `T8`（**W2 强制前置**）：源 ↔ 产品绑定

- 依据：`source-registry.md` §5 各表「被引用产品卡」列（如 `SRC-CB-001` → `PROD-CB-001`；跨族通用源 `SRC-XFAM-001/002/003` → **全部 13 张**）
- 实现：`l11` 匹配前先按登记取"本产品的合法源集合"，**非登记源一律不参与**（fail-closed：登记表读不到 ⇒ 退出非零，不静默放行）
- 判据：同 epoch 下 `PROD-CM-001` 的证据来源**只能**含 `SRC-CM-*` 与跨族通用 `SRC-XFAM-*`；出现 `SRC-CB-*`/`SRC-FIN-*`/`SRC-TF-*`/`SRC-SET-*`/`SRC-IB-*` 即 FAIL
- 本次实测的那两条（`SRC-CB-001` 1 条、`SRC-FIN-001` 1 条）**即为 T8 的负例样本**，可直接写成回归测试

### 9.5 工作项表（V1.2）

| # | 状态 |
|---|---|
| `T1` `--product`/`--family` | **已实施 + 已验证**（4 脚本） |
| `T2` 族 fail-closed | **已实施 + 已验证**（exit=1） |
| `T6` 幂等重建 | 已实施 + 已验证 |
| `T5` 可复现 | 已具备（零改造） |
| **`T8` 源↔产品绑定** | **新增 · W2 强制前置** |
| `T1b` `--all` 全链驱动（l12/l13） | 待做（`l11` 已支持 `--all`） |
| `T3` 5 族字段策略实例 | 待 Owner（`B-5b`） |
| `T4` 版本范围派生 | 挂起（语义待澄清） |
| `T7` 回填 registry 条款数 | W2 同批 |

---

## 10. V1.3 —— `T3` 已实施（Owner 批准 5 族实例）+ `T8` 仍未做

> append-only · 2026-09-22T10:27:59+00:00

### 10.1 `T3` 已实施：5 族字段策略正例已写入 `CTR-PK-FLD-001`

`specs/product-knowledge/field-policy.schema.json` 的 `examples` 由 **2 → 7** 条：

| 族 | 实例 | `_case` | `ownerApproved` |
|---|---|---|---|
| CASH_MANAGEMENT | `FLD-CASH_MANAGEMENT-001` | POSITIVE | `false`（既有，未动） |
| SETTLEMENT | `FLD-SETTLEMENT-999` | PUBLIC_TRACK_REJECT | `false`（既有**反例**，未动） |
| **SETTLEMENT** | **`FLD-SETTLEMENT-001`** | **POSITIVE（新增）** | `false` |
| **FINANCING** | **`FLD-FINANCING-001`** | **POSITIVE（新增）** | `false` |
| **TRADE_FINANCE** | **`FLD-TRADE_FINANCE-001`** | **POSITIVE（新增）** | `false` |
| **CROSS_BORDER** | **`FLD-CROSS_BORDER-001`** | **POSITIVE（新增）** | `false` |
| **INVESTMENT_BANKING** | **`FLD-INVESTMENT_BANKING-001`** | **POSITIVE（新增）** | `false` |

**重要事实（我此前说错了一处）**：`SETTLEMENT` 那条第 2 个实例是**反例**（`_case: PUBLIC_TRACK_REJECT`，用于验证 `INV-FLD-01` 能拦截），**不是可用正例** ⇒ 缺正例的族确为 **5 个**。

**字段集口径（不发明字段）**：`FieldSpec.fieldPath` 在 schema 里**只有语法 pattern**（`^[a-z][a-zA-Z0-9]*(\.[a-z][a-zA-Z0-9]*)*$`），**没有 enum** ⇒ 字段目录的权威**就是"已批准的字段策略"本身**。
故 5 个新实例一律采用**跨族通用槽位骨架**（与 CASH_MANAGEMENT 正例同源）：`identity.productCode` · `eligibility.customerSegment` · `eligibility.prerequisiteProducts` · `compliance.regulatoryBasis` · `pricing.serviceFee`（后者 `ownerDecisionRequired: true`）。
**族特有槽位一律未添加**（如现金管理的 `eligibility.minAccountBalance`）—— 需 Owner/合同 Owner 定，不由我代造。

**`ownerApproved` 我没翻**：Owner 批准的是「新建 5 族实例」（`B-5b` 解除、授权施工）；`ownerApproved` 翻真会使 `ownerDecisionRequired` 字段从 UNKNOWN 转为可取值（`l11` 的 `matched=[]` 分支），属合规语义，**须 Owner 看过具体实例后单独签**。故实例暂置 `false`、`ownerDecisionId: null`。

**门禁**：`check_l02_candidates.py` **41/41 PASS**；`check_contracts.py` **14/14 PASS**。

### 10.2 隔离副本实测（`T3` 的效果）

| 验证 | 结果 |
|---|---|
| `FINANCING` 不再 fail-closed | `l11 --product PROD-FIN-001 --family FINANCING` ⇒ **exit=0**，产出 10 条断言（3 UNKNOWN / 7 CANDIDATE） |
| `--all` 全链 | `l11 --all` ⇒ **exit=0**，**13 张卡全部产出 `PROD-*.assertions.json`**（221 条 OK 行） |
| `PROD-CM-001` 回归 | 字段集**无新增/无缺失**；断言 18 → 19（差异来自 17 源参与，即 `F-PC8-07`） |

### 10.3 `T8` 仍是 W2 唯一硬前置

13 卡断言现已能产出，但**内容仍受 `F-PC8-07` 污染**（无源↔产品绑定）⇒ **先做 `T8`，再跑全链**。
`T8` 数据源：`source-registry.md` §5 各表末列「被引用产品卡」；跨族通用源 `SRC-XFAM-001/002/003` 取值为「全部 13 张」。解析须覆盖形态：`全部 13 张` · `全部 13 张（价格边界章节）` · `PROD-CM-001/002` · `PROD-TF-001/002` · `PROD-FIN-001（如线上化）`。

---

## 11. V1.4 —— `T8` 已实施（`F-PC8-07` 已解）+ 三项新发现

> append-only · 2026-09-22T10:40:00+00:00

### 11.1 `T8` 已实施并实证（`l11` 源 ↔ 产品绑定）

实现：`load_source_product_binding()` 解析 `01_raw/source-registry.md` **族表（§5.1–§5.7）** 的「被引用产品卡」列，按 `source_id` 取并集；断言匹配前把参与证据收窄到 `PROD_ID` 的合法源集合；**无绑定即 `SystemExit(1)`**（fail-closed）。

| 验证（隔离副本，17 源） | 结果 |
|---|---|
| `PROD-CM-001` 合法源 | **8 个**；参与证据 **49/136**（剔除 87 条非登记源证据） |
| **跨族串味回归**（`F-PC8-07` 的 2 条样本） | **PASS —— 0 条**。证据来源收敛为 `SRC-CM-001/003` + `SRC-XFAM-001/003` |
| 断言数 | 19 → **16**（剔除非法证据后自然收敛） |
| fail-closed 负例 | `--product PROD-XX-999` ⇒ **exit=1** + `FAIL | … 没有任何被引用源（T8 fail-closed）` |
| `--all` | **13/13 卡**各自打印 `SCOPE`（各自合法源集合不同，如 `PROD-CB-001` 合法源 6 个／参与 37/136） |

### 11.2 `B-6`（**新 Owner 口径**）：§5.8「无」 vs 族表绑定

- §5.8 DEMO 表末列写的是 `无（禁止沿用 13 张 legacy card）`；
- §5.1–§5.7 族表按同一 `source_id` 给出真实绑定（如 `SRC-CM-001 → PROD-CM-001/002`、`SRC-XFAM-001 → 全部 13 张`）。
- **我的显式选择（已写入代码注释，非静默）**：绑定取**族表**；§5.8 的「无」理解为"DEMO 源不得作为 13 张 legacy 卡的真实结论依据"，而 PC8 的用途是 **DEMO 轨链路验证**（Release 必须带 `provenance_state=DEMO` 且不进 `RECOMMENDATION_READY`，该约束由链内已有判据强制）。
- **请 Owner 确认**：① 认可"DEMO 源按族表绑定"；或 ② 维持「无」⇒ 则 PC8 链路**无法产出卡片解读**（整条链只剩空壳）。

### 11.3 `F-PC8-08`（**新发现 · gits Java 侧**）：第五处单产品硬编码

`apps/api/.../ProductCardCatalogService.java`：

```java
/** 单个产品卡是否具备解读投影（由 KertReleaseSnapshotAdapter 判定）。 */
private boolean isInterpretable(String productId) {
    return "PROD-CM-001".equals(productId);   // ← 与注释自述"由 Adapter 判定"不符
}
```

⇒ 即便 W2 发布 13 个 Release，产品卡目录**仍只把 `PROD-CM-001` 标为可解读** ⇒ 解读页对另外 12 卡的入口会保持"不可解读"。**修法**：改为向 `KertReleaseSnapshotAdapter` 询问快照是否存在（与注释自述一致）。

### 11.4 `F-PC8-09`（**新发现**）：`l10` 只吃 `*.DEMO.md` ⇒ 真实监管源从不入库

`tools/l10_build_source_versions.py` 的 `targets = sorted(AUTH.glob("*.DEMO.md"))` ⇒ `REG-*.md`（9 份真实法规）**不产出 SV/fragments/evidence-spans**。
后果：`compliance.regulatoryBasis`（`minAuthorityLevel: REGULATORY`）只能由 `REG-*` 证据支撑，而它们永不参与 ⇒ **该字段恒为 UNKNOWN**。

### 11.5 工作项表（V1.4）

| # | 状态 |
|---|---|
| `T8` 源↔产品绑定 | **已实施 + 已实证**（串味归零、fail-closed、13/13 作用域） |
| `T9` `l10` 纳入非 DEMO 真实源（解 `F-PC8-09`） | **新增** |
| `T10` 修 `F-PC8-08`（Java `isInterpretable` 去硬编码） | **新增** · 随 W2 落 |
| `T11` 全链 13 卡（`l10→l13`）+ `T7` 回填 + `F-PC8-05` 期望值同批同步 | 待做（**B 路径主体**） |
| `T3` 5 族字段策略实例 | 已实施（等 Owner 看字段集与 `ownerApproved`） |

---

## 12. V1.5 —— `T11` 全链 13 卡跑通（真实仓）+ 三处族硬编码修复

> append-only · 2026-09-22T10:45:16+00:00

### 12.1 真实仓全链结果（`SOURCE_DATE_EPOCH=2026-09-22T00:00+08:00`）

| 阶段 | 产物 | 门禁 |
|---|---|---|
| `l10` | 17 SV + 17 fragments（319 片段；幂等重建已清理 `20260906` 旧件） | **258/258 PASS** |
| `l11` | 13 卡断言 + 17 份 evidence-spans（T8 生效：每卡只吃本产品登记源） | **2493/2493 PASS** |
| `l12` | 13 conflicts + 13 health + 13 candidate-cards | **172/172 PASS** |
| `l13` | 13 interpretation + 13 releases（**全部 DRAFT**） | **385/385 PASS** |

各卡 `policyId` 正确落到本族实例（`FLD-CASH_MANAGEMENT-001` / `FLD-FINANCING-001` / `FLD-SETTLEMENT-001` / `FLD-TRADE_FINANCE-001` / `FLD-CROSS_BORDER-001` / `FLD-INVESTMENT_BANKING-001`）。

### 12.2 本轮修掉的三处「族/产品硬编码」（都是**门禁与实现互相掩盖**）

| 发现 | 位置 | 修法 |
|---|---|---|
| `F-PC8-05` | `check_l10_sources.py:151` `DEMO 源数量 == 3` | 改为**读 registry §5.8 登记行**推导（单点化） |
| `F-PC8-10` | `l11.load_policy_fields()` 会选中排在前面的 **SETTLEMENT 反例**（`PUBLIC_TRACK_REJECT`） | 只接受 `_case` 前缀 `POSITIVE` 的实例；POSITIVE 实例数 ≠ 1 ⇒ fail-closed |
| `F-PC8-11` | `l12.load_policy()` 写死 `CASH_MANAGEMENT`；`check_l11/check_l12` 把「七字段」当**所有产品**的期望 | l12 按**本产品断言产物的 `policyId`** 取策略；两个门禁改为「本产品策略字段集/字段数」 |

> 这三处的共同形态：**实现写死一族 + 门禁也写死同一族** ⇒ 单产品时全绿，多产品时静默错。
> 若不修，13 卡会得到"现金管理字段集"的候选卡与解读（看起来完整、字段其实张冠李戴）。

### 12.3 `l13` CLI 修复

`l13_publish_release.py` / `l13_apply_decisions.py` 的 `main()` 原只解析 `--decisions`，**会拒收 `--product`**（T1 只改了模块级解析）⇒ 逐产品发布无法调用。已补 `--product`（并 `global PRODUCT_ID` 覆盖）。

### 12.4 如实登记的遗留（不掩盖）

| # | 遗留 | 性质 |
|---|---|---|
| `B-2` | 13 个 Release 全为 **DRAFT**、`publishedAt=null`、提示 `BLOCKED_ON_OWNER` | 未获 Owner 签署决策 ⇒ **不冒充已发布**（设计如此） |
| `T12` | `rule-packages` 仅 `PROD-CM-001` 有容器（**1/13**） | `l13` 对缺失者取 `r_hash=RULEPACKAGE:EMPTY`（`NOT_BUILT` 容器语义）⇒ `bundleHash` 如实体现"规则未生效"；12 卡容器待建 |
| `T9` / `F-PC8-09` | `l10` 仍只 glob `*.DEMO.md` ⇒ 9 份 `REG-*` 不入 fragments | ⇒ `compliance.regulatoryBasis` **恒为 UNKNOWN** |
| `T10` / `F-PC8-08` | Java `ProductCardCatalogService.isInterpretable()` 仍写死 `PROD-CM-001` | 不修则解读页对另外 12 卡入口不可用 |
| `F-PC8-12` | `PROD-CM-001` 的 VALUE_MISMATCH（50 万 vs 100 万）保留 | **设计样本**，非缺陷 |
| `SIM-4` | 产品 + 合规确认未做 | 仅链路联调，**不得对客引用** |

### 12.5 下一步（B 路径收尾）

`T10`（Java 去硬编码 + 跑后端测试）⇒ 然后交**人工测试配方**（两目录参数 + 启动命令 + 可点范围）。

---

## 13. 人工测试配方（T10 后端实测通过）+ `B-2` 的直接影响

> append-only · 2026-09-22T10:59:20+00:00

### 13.1 前置（已就绪）

KERT 侧 `04_serve/interpretation` = 13 份、`04_serve/releases` = 13 份（**全部 DRAFT**）、`03_core` = 13 张产品卡。

### 13.2 启动（两个目录用**启动参数**指过去，不改仓库配置文件）

```bash
KERT=/home/szf/dev/Leibniz-KERT/examples/product-recommendation-assets
# 后端（gits Java API；独立端口，避免占用既有服务）
java -jar /home/szf/dev/gits-cbanking/apps/api/target/gits-kno-api-0.1.0-SNAPSHOT.jar \
  --server.port=18080 \
  --gits.product-knowledge.snapshot-dir=$KERT/04_serve/interpretation \
  --gits.product-knowledge.card-dir=$KERT/03_core
# 前端（另开一个终端）
cd /home/szf/dev/gits-cbanking/frontend && VITE_API_PROXY_TARGET=http://127.0.0.1:18080 npm run dev
# 浏览器打开 vite 提示的地址（默认 5173），进「产品解读」页
```

### 13.3 实测结果（2026-09-22，`java -jar` 真跑）

| 请求 | 实测结果 | 说明 |
|---|---|---|
| `GET /api/v1/product-knowledge/cards` | **13 卡**，`PROD-IB-001` 等非 CM 卡 `"interpretable":true` | **`T10` 修复端到端生效**（修好前非 CM 卡恒 `false`） |
| `GET /…/PROD-CM-001/interpretation?view=OVERVIEW&purpose=INTERPRETATION` | **404** `PRODUCT_KNOWLEDGE_NOT_PUBLISHED`：「Release `RLS-2026.09.22.3` 尚未发布（DRAFT）」 | 受控失败按设计工作，**不冒充已发布** |
| `GET /…/PROD-TF-001/interpretation…` | **404** 同上（`RLS-2026.09.22.12`） | 同上 |

⇒ **人工测试现在能测到**：13 张卡的**目录与卡详情**（含 capabilities / scenarios / riskNotes / 原始 Markdown）。
⇒ **暂时测不到**：**解读三视图**（页面上会显示"未发布"）—— 因为 13 个 Release 全是 `DRAFT`，即 **`B-2`**。

### 13.4 `B-2` 的直接后果（必须说清）

要看/测解读三视图，必须先由 **Owner 签署 `90_control/decisions/*.json`**，`l13` 才会把 Release 从 `DRAFT` 转 `PUBLISHED`。
⇒ 新增工作项 **`T13`：出 decisions 文件模板（含必需字段，供 Owner 签）**；签完重跑 `l13` 即为可测。

### 13.5 `F-PC8-13`（新发现）：重跑会把"已发布"投影退回"草稿"

投影快照按产品**单文件覆盖**（`04_serve/interpretation/<PROD>.json`）⇒ 本次重跑后 `PROD-CM-001` 的投影由
`RLS-2026.09.06.1`（已发布）变为 `RLS-2026.09.22.3`（`DRAFT`）⇒ GITS 侧由"可读"**回退为 404**，直到新 Release 被签署发布。
是否应在 `l13` 侧保留已发布投影（或按 lifecycle 择优），属 **ADR / Release 语义**的设计选择 ⇒ **不擅自改**，已登记待裁。

### 13.6 工作项（V1.6）

| # | 状态 |
|---|---|
| `T10` / `F-PC8-08` | **已完成**：Java 去硬编码 + 负例回归 + 614 测试全绿 + 端到端实测 |
| `T13` decisions 模板 | **新增**（Owner 签后解读页才可测） |
| `F-PC8-13` 投影覆盖语义 | **新增**，待裁 |
| `T9`（REG 入 fragments）· `T12`（rule-packages 12 卡） | 待排 |

---

## 14. `T13` 已完成：13 卡决策模板（待 Owner 签署）

> append-only · 2026-09-22T11:09:56+00:00

### 14.1 产物

`examples/product-recommendation-assets/90_control/decisions/PC8-13cards.template.json`（**新增，未覆盖任何既有文件**）

| 项 | 内容 |
|---|---|
| 决策项 | **29 项** = `identity.productCode` ×13 + `compliance.regulatoryBasis` ×13 + `eligibility.minAccountBalance` ×2（`PROD-CM-002/003`）+ OPEN 冲突 ×1（`CNF-PRODCM001-757c6c3b`） |
| 依据 | 由当前产物生成 subject id：`02_work/reports/*.health.json`（UNKNOWN 且 `REQUIRED_HARD`）与 `02_work/conflicts/*.conflicts.json`（`status=OPEN`） |
| 脚本立场 | `decision` / `rationale` / `decidedBy` / `decidedAt` / `attestedBy` **一律留空**；`ownerAttested: false` —— **脚本不代 Owner 生任何决定** |
| 自检 | 把模板当决策文件跑 `validate()` ⇒ **117 项错误**（未签署 + 未填），即：**不签就用不了**（预期行为） |
| 提示 | 每项带 `_hint`：字段语义、参考先例（`identity.productCode` / `compliance.regulatoryBasis` 沿用 2026-09-06 的 N/A 先例）、冲突候选断言；CM-001 冲突的历史裁决采信 `ASM-PRODCM001-991baf6e`（**该断言在当前产物中仍存在**，可沿用） |

### 14.2 签署与执行（Owner 侧）

1. 逐项填 `decision`（`NOT_APPLICABLE` / `ADOPT_ASSERTION`）、`rationale`、`decidedBy`、`decidedAt`；
   冲突项另填 `resolvedAssertionId`；
2. 填 `attestedBy`（自然人 Owner 标识）、`ownerAttested: true`、`attestation`、`attestedAt`；
3. **另存为** `90_control/decisions/signed-pc8.json`（**不要覆盖既有 `signed.json`** —— 那是 2026-09-06 的历史签字）；
4. 逐卡执行（`l13` 为单产品脚本）：
   ```bash
   for pid in PROD-CM-001 PROD-CM-002 … PROD-TF-002; do
     python3 tools/l13_apply_decisions.py  --decisions 90_control/decisions/signed-pc8.json --product $pid
     python3 tools/l13_publish_release.py  --decisions 90_control/decisions/signed-pc8.json --product $pid
   done
   ```
5. 之后 `04_serve/releases` 的对应 Release 由 `DRAFT` → 可发布态，解读三视图即可在人工测试中打开。

### 14.3 签署前必须知道的 3 件事（不隐藏）

1. **`compliance.regulatoryBasis` 全部 UNKNOWN 与我方未解缺陷同源**（`T9`/`F-PC8-09`：`l10` 只 glob `*.DEMO.md`，9 份真实 `REG-*` 不入 fragments）⇒ 该字段**没有任何可用证据**，最可能的裁决是 `NOT_APPLICABLE`（沿用 2026-09-06 先例），但**这是你的判断，不是我替你写**。
2. **`eligibility.minAccountBalance`（`PROD-CM-002/003`）UNKNOWN** 属"无证据命中"，若要取值需先补源（Owner 上传义务）。
3. **发布语义**：本次发布的是 **DEMO 派生** Release ⇒ `check_l13` 强制 `provenanceState=DEMO` 且 **`recommendationReady=false`**（推荐用途仍不可用）；另 `F-PC8-13`（投影单文件覆盖导致 404）也会随之解除。

---

## 15. `T13` 签署落盘 ⇒ 13 卡 PUBLISHED，解读接口实测 **200**

> append-only · 2026-09-22T11:17:45+00:00

### 15.1 签署处置（Owner 指示「三件事都签署」）

- 落盘 `90_control/decisions/signed-pc8.json`（**29 项**）：`attestedBy=OWNER`，`attestation` **逐条记录**所确认的三件事；
  裁决口径沿用 2026-09-06 先例（`DECISION-20260906-02`）。
- 模板同步：`PC8-13cards.template.json` 每项补 `productId`（限定适用产品；留空=不限）。
- **未覆盖**既有 `signed.json` / `review-decisions.json` / `DECISIONS.template.json`。

### 15.2 过程中又暴露两个工具缺陷（都已修，非纸面）

| 编号 | 缺陷 | 实证 | 修法 |
|---|---|---|---|
| `T14` | 决策**缺产品维度**：`FIELD` 决策的 `subjectId` 只是字段路径 ⇒ 跨产品签署件里 13 条同名决策被**一次 apply 应用 13 遍** | 实测 `newAssertions=26`、`PROD-TF-002` 出现 **13 份重复断言**，击穿 L11「assertionId 唯一」 | 决策支持可选 `productId` 限定（缺省=不限，兼容单产品历史文件）；不属于本产品的裁决**跳过并留痕**；补**幂等守卫**；同批修 `l13_apply.load_policy` 的族硬编码 |
| `F-PC8-14` | `l13_publish` 允许用**「0 决策项」**的决策文件发布 | 产生 **13 份** `PUBLISHED` 但 `ownerDecisionIds=[]` 的 Release ⇒ 违反 L13 不变式 | fail-closed 拒绝空决策发布；**清理**这 13 份违规件（`RLS-2026.09.22.62–.74`；当前投影指向 `.75–.87`，未受影响） |

### 15.3 结果（真实仓）

| 项 | 结果 |
|---|---|
| 13 卡 apply | 各**只应用本产品**决策（CM 族 +3，其余 +2）· `blockers=0` · `interpretationReady=True` |
| 13 卡 publish | `lifecycle=PUBLISHED` · `interpretationReady=True` · **`recommendationReady=False`**（DEMO 派生强制） |
| 门禁 | L10 258/258 · **L11 2634/2634** · L12 144/144 · **L13 755/755** · registry 167/167 |
| 跨仓统一门禁 | **PASS 11 · FAIL 0 · SKIP 0** |
| **接口实测** | `GET /api/v1/product-knowledge/{PROD}/interpretation?view=OVERVIEW&purpose=INTERPRETATION` ⇒ **200**（`PROD-CM-001` / `PROD-TF-001` / `PROD-IB-001` 实测；此前均为 404 DRAFT） |

### 15.4 人工测试（配方不变，现在真的能看了）

按 §13.2 起后端 + 前端（`snapshot-dir` 指 `04_serve/interpretation`、`card-dir` 指 `03_core`）：
- 产品卡目录：13 卡，`interpretable` 正确；
- **解读三视图：现在可打开**（`OVERVIEW` / `ELIGIBILITY` / `PRICING` × `INTERPRETATION` 用途）。

### 15.5 如实声明（不随"能打开了"而消失）

1. `compliance.regulatoryBasis` 的 N/A 裁决**建立在"无证据可用"之上**（`T9`/`F-PC8-09`：`REG-*` 不入 fragments）
   ⇒ 该字段**当前不承载任何监管依据**，补源后**须重裁**（已写入 rationale）；
2. `PROD-CM-002/003` 的 `eligibility.minAccountBalance` N/A 同理；
3. 发布物为 **DEMO 派生** ⇒ `recommendationReady=false`（推荐用途仍不可用）；`SIM-4`（产品+合规确认未做）未变；
4. `T12`（`rule-packages` 1/13）未变；`F-PC8-13`（投影单文件覆盖语义）**待裁**（本次发布间接缓解了 404）。

---

## 16. `T9` / `T12` / `F-PC8-13` 三项完成（本轮收尾）

> append-only · 2026-09-22T11:24:33+00:00

### 16.1 `T9` 真实监管源进入链路（**修掉两个静默缺陷**）

| 项 | 内容 |
|---|---|
| `l10` 纳入真实源 | 除 `*.DEMO.md` 外追加**带 front matter 且含 `source_id`** 的权威源（按内容判定，非文件名白名单）⇒ 纳入 **8 份 `REG-*`**；源数 17→**25**、片段 319→**758** |
| `F-PC8-09` 解除 | `compliance.regulatoryBasis`（`minAuthorityLevel=REGULATORY`）**不再恒为 UNKNOWN** ⇒ 13 卡该字段现为 **CANDIDATE + 真实监管证据** |
| **`F-PC8-16`（新发现，静默漏条）** | `l10`/`l11` 的条款正则字符集**缺 `零〇`** ⇒《票据法》第一百零一～一百零九条 **9 条被静默丢弃**（实测 101/110）。对齐 `g0_5_extended_verify.py` 既有约定后，8 份监管源条款数与官方**全部吻合**（38/71/51/34/42/60/**110**/33） |
| 登记 | 新增 registry **§5.9 真实监管源入库记录（机器可读汇总）**，供 `check_l10_sources.declared_clause_counts()` 核对（原 REG 为 kv 表，正则取不到 ⇒ 门禁必 FAIL）；字节/哈希与既有登记**实测一致** |

### 16.2 `T12` 规则包容器 13/13（空容器，非造规则）

镜像 `PROD-CM-001` 的**空容器**语义（`status=NOT_BUILT`、`rules=[]`、`failurePolicy=FAIL_CLOSED`、`notice` 原文保留）⇒ `rulePackageHash` 由 `RULEPACKAGE:EMPTY` 变为容器哈希（13 卡已重发布）。
**遗留 `T12b`**：全仓**无 rule-package 生成器**（仅 `l13` 读取）⇒ 容器为手工镜像，应补生成器。

### 16.3 `F-PC8-13` 投影不得被 DRAFT 覆盖（**两分支实测**）

| 分支 | 实测结果 |
|---|---|
| 内容一致 | `KEEP | 保留既有已发布投影（本次为 DRAFT，内容一致）` ⇒ 消费者仍 **200** 读旧 Release（此前会变 404） |
| 内容变更（受控实验：篡改投影 bundleHash 后不带决策发布） | `KEEP … 并标 stale` ⇒ 投影 `isStale=true`+`staleReason` ⇒ 消费者 **409 `RELEASE_STALE`**（"需重新发布后方可使用"）⇒ **不静默读旧内容** |
| 恢复 | 带决策重发布 ⇒ `PUBLISHED`，接口回 **200** |

### 16.4 门禁与现状

**L10 370/370 · L11 6336/6336 · L12 156/156 · L13 944/944 · registry 167/167 · 跨仓统一门禁 PASS 11 / FAIL 0 / SKIP 0**
13 卡：`blockers=0`、`interpretationReady=True`、`PUBLISHED`、`recommendationReady=False`；人工测试三视图 **200**（除被标 stale 时按设计返回 409）。

### 16.5 **需 Owner 一句话**（唯一未闭环项）

`signed-pc8.json` 中 **13 条 `compliance.regulatoryBasis = NOT_APPLICABLE`** 的裁决前提是"**无证据可用**"（该措辞已写入 rationale）。
`T9` 后该前提**已被推翻**（现有真实监管证据）。
我**未代改已签裁决**（纪律：不擅动 Owner 签署件）⇒ 该字段当前仍显示 `NOT_APPLICABLE`，而证据在断言层可见但被遮蔽。
**请 Owner 重裁**：撤销 N/A（让证据生效）／改用 `ADOPT_*`／维持 N/A（需把 rationale 改为"不因本产品卡承载"等独立理由）。

### 16.6 其他遗留

| # | 项 |
|---|---|
| `F-PC8-17` | `regulatoryBasis` 命中候选偏多（如 `PROD-TF-001` 39 条）—— 关键词粗粒度所致，Review 阶段需收敛口径 |
| `T12b` | rule-package 无生成器 |
| `T16` | `04_serve/releases` 持续累积（现 102 份，含首轮 13 份 DRAFT 历史件）⇒ 需清理/归档口径 |
| `F-PC8-15` | `l13` 的 Release `provenanceState` 硬编码 `DEMO`；`T9` 后证据含 `VERIFIED` 监管源 ⇒ 该标签不再准确（保持 DEMO 更保守，故未擅改） |
| `SIM-4` | 产品 + 合规确认未做 ⇒ 不得对客引用 |

---

## 17. Owner 指示 ① 已执行：撤销 13 条 N/A ⇒ 断言层证据生效；呈现层需再一步（`T17` 已建）

> append-only · 2026-09-22T11:44:44+00:00

### 17.1 撤销已落盘（append-only，原签署件未动）

`signed-pc8-r2.json`：保留 16 项决策（`identity.productCode`×13、`eligibility.minAccountBalance`×2、CM-001 冲突×1）+
`revokedDecisions` 13 条（`compliance.regulatoryBasis` 的 N/A，含撤销理由）+ `supersedes: signed-pc8.json`（**原文件原样留存**）。
全链重建并按 r2 生效：13 卡 `blockers=0`、`interpretationReady=True`、`PUBLISHED`；
`compliance.regulatoryBasis` **13 卡全部 CANDIDATE + 真实监管证据**（2–39 条；CM-001 24、TF-001 39、CB-002 22）。
门禁：L11 **6425/6425** · L12 144/144 · L13 **1061/1061** · 统一门禁 **PASS 11 / FAIL 0 / SKIP 0**。

### 17.2 `F-PC8-18`：撤销 N/A 之后，**页面仍显示"未核验"**（合同口径所致，不是 bug）

`l13_publish:264-267`（CTR-PK-INT-001 呈现枚举只有 5 态）：

```python
# CANDIDATE 未经 Owner 复核，按 fail-closed 归一为 UNKNOWN，且不得回链证据（未复核结论不呈现）。
if state == "CANDIDATE":
    state = "UNKNOWN"
```

实测对照：`health` / `candidate-card` 均为 `CANDIDATE + 24 证据`，而投影 `views` 为 `UNKNOWN + 0 证据` ⇒ 接口显示"未核验"。

### 17.3 `T17`：新增 `FIELD + ADOPT_ASSERTION` 通道（能力扩展，已隔离验证）

必要性：原 `l13_apply` 仅有 `CONFLICT+ADOPT_ASSERTION` 与 `FIELD+NOT_APPLICABLE` 两条通道 ⇒ **非冲突字段永远停在 CANDIDATE**，证据在页面上永不出现。

| 项 | 内容 |
|---|---|
| 严格性 | `resolvedAssertionId` 必须属于**本产品该字段**的断言集；**无证据的断言拒绝提升**；幂等（同 decisionId 不重复） |
| 归一值 | 只从证据原文解析（`money_value`），**不生成** |
| 隔离验证（`/tmp/pc8_t17`，TEST 决策，真实仓零改动） | `FIELD compliance.regulatoryBasis -> SUPPORTED (adopt ASM-…)`；**投影呈现 `SUPPORTED + 证据 1 条`**（`PROD-CM-001 → REG-CM-002 第五条`、`PROD-TF-001 → REG-TF-001 第五条`） |
| 副本门禁 | L11 **6404/6404** · L12 156/156 · L13 **1076/1076** PASS（首轮 FAIL 仅因 TEST 决策 id 不合 `^DEC-\d{8}-[0-9a-f]{8}$` —— 测试脚手架问题，已如实记录） |

### 17.4 `r3` 待签模板（使证据在页面出现）

`90_control/decisions/PC8-r3-regulatoryBasis.template.json`（13 项，**未签署**）：
- 每项预选**一条具体监管条款**（机械规则：**族专属法规优先**，再按 `sourceId`/条款号最小）；
- **预选仅为占位、非合规判断** —— 实测机械规则会落到语义偏弱的条款（如 `PROD-CM-002` → 跨族 `REG-XFAM-001` 第二条），
  故每项 `_hint` **附 3 条备选**（id + 来源 + 条款 + 引文片段）供替换；
- 必须填 `rationale`（**不得无理由采纳**）+ `decidedBy/decidedAt` + `attestedBy` + `ownerAttested=true`；
- 签名后逐卡 `l13_apply` + `l13_publish` 即让 `regulatoryBasis` 以 `SUPPORTED + 证据` 呈现。

### 17.5 现状与选择

| 选项 | 结果 |
|---|---|
| **维持现状** | 断言层已"有依据"（不再是无证据的 UNKNOWN），但页面仍显示"未核验"（合同口径要求 Owner 复核后才呈现） |
| **签 r3** | 页面出现 `SUPPORTED + 具体监管条款原文`（条款由你确认/替换；我不代选） |

### 17.6 遗留（更新）

`F-PC8-15`（Release `provenanceState` 硬编码 DEMO）· `F-PC8-17`（候选偏多，Review 需收敛）· `T12b`（rule-package 无生成器）·
`T16`（releases 累积 102 份）· `SIM-4`（产品+合规确认未做，不得对客引用）

---

## 18. `r3` 已签：6 卡监管依据在页面呈现条款原文；7 卡按指示不采纳（含根因）

> append-only · 2026-09-22T11:49:57+00:00

### 18.1 采纳名单（6 卡，均来自**族专属**监管源）

| 产品 | 采纳条款 | 权威级 |
|---|---|---|
| `PROD-CB-002` | `REG-CB-002` 第一条（跨境担保外汇管理规定·立法目的与范围） | REGULATORY |
| `PROD-CM-001` | `REG-CM-002` 第五条（人民币银行结算账户管理办法） | REGULATORY |
| `PROD-FIN-001` | `REG-FIN-001` 第三条（流动资金贷款定义） | REGULATORY |
| `PROD-IB-001` | `REG-IB-001` 第七条（并购贷款业务原则） | REGULATORY |
| `PROD-TF-001` | `REG-TF-001` 第五条（贴现定义） | REGULATORY |
| `PROD-TF-002` | `REG-TF-002` 第四条（信用证当事人义务） | REGULATORY |

**实测**：投影 `regulatoryBasis = SUPPORTED + 证据 1 条`；接口 `PROD-TF-001` 返回 `REG-TF-001 第五条` 原文。

### 18.2 不采纳名单（7 卡）与三类根因（**都是可修的真问题**）

| 产品 | 现有候选 | 根因 |
|---|---|---|
| `PROD-CM-002` / `PROD-CM-003` | 仅跨族 `REG-XFAM-001` | **`F-PC8-19`**：`REG-CM-001` 是 **PDF**（`01_raw/_authoritative/REG-CM-001.pdf`，92KB）⇒ `l10` 只吃 `.md`，最对口的《现金管理暂行条例》**从未进入链路** |
| `PROD-CB-001` | 仅跨族 `REG-XFAM-001` | `REG-CB-001` **登记已指名但实体件未入库** |
| `PROD-FIN-002`（供应链金融） | 仅跨族 `REG-XFAM-001` | 登记表**未绑定族专属监管源**（`REG-FIN-001` → `FIN-001/003`） |
| `PROD-SET-001` / `PROD-SET-002` | 仅跨族 `REG-XFAM-001` | `REG-SET-001` 是 `REG-CM-002` 的**别名**，而 `REG-CM-002` 只绑定 `CM-001/002` ⇒ 别名收敛未传导到绑定 |

### 18.3 要把这 7 卡也补上，需要（按性价比排序）

1. **`F-PC8-19`（最直接）**：把 `REG-CM-001.pdf` 转成 `REG-CM-001.md`（含 front matter：`authority_level: REGULATORY`）⇒ CM-002/003 立即有族专属候选；
2. **登记绑定补齐**：`REG-FIN-001` 增绑 `PROD-FIN-002`；`REG-CM-002`（含 `REG-SET-001` 别名）增绑 `PROD-SET-001/002`；`REG-CB-001` 实体件入库；
3. 上述三项均为**登记/材料动作**，不涉代码；完成后重跑 `l11→l12→apply→publish` 即可。

### 18.4 门禁与遗留

门禁：L11 **6479/6479** · L13 **1091/1091** · 跨仓统一门禁 **PASS 11 / FAIL 0 / SKIP 0**。
遗留：`F-PC8-19`（REG-CM-001 PDF 未入链路）· `F-PC8-15` · `F-PC8-17` · `T12b` · `T16` · `SIM-4`。

---

## 19. `F-PC8-19` + `F-PC8-20` 完成 ⇒ 监管依据呈现面 **6 → 9 卡**

> append-only · 2026-09-22T11:54:30+00:00

### 19.1 `F-PC8-19`：`REG-CM-001` 由 PDF 转写入库（此前**从未进入链路**）

- 新增 `01_raw/_authoritative/REG-CM-001.md`：pypdf 抽取 → 清洗页码行 → 按章/条格式化（插 `**第X条**` 标记）；
  **只格式化、不改字**（原文编注「（2011 年 1 月 8 日删除）」保留）
- 新增 `snapshots/REG-CM-001.provenance.md`：源件字节/SHA-256、转写方式、**强度声明**（保证转写件自身完整性，不主张与 PDF 字节一致）、`clause_verified=false`
- 解析校验：**25 条（严格 1..25）+ 4 章**；`l10` 实测 fragments=25；registry §5.9 增行
- 记录一处**我方换算 bug**（亦影响早期排查）：中文数字换算把"二十"算成 2（十位未乘 10）⇒ 早先"票据法漏 9 条"的
  诊断数字口径有误；但 `F-PC8-16` 的结论（`l10` 正则缺 `零`）由**直接的正则比对**独立确认，修复成立

### 19.2 `F-PC8-20`（新）：登记表**简写**导致同族后续产品长期漏绑

| 项 | 内容 |
|---|---|
| 现象 | `REG-CM-001 → PROD-CM-001/002/003` 被解析成只剩 `PROD-CM-001`（`re.findall(r"PROD-[A-Z]+-\d{3}")` 只命中首个 id） |
| 后果 | `CM-002/003` 等**从未绑定**族专属监管源 ⇒ r3 的"7 条弱预选"有一半源于此 |
| 修复 | 新增 `_expand_product_ids()` 展开 `PROD-XX-NNN/MMM/...`；绑定源 26 → **31** |
| 效果 | 有族专属候选的卡 **6 → 9**（新增 `CM-002`/`CM-003`/`FIN-003`） |

### 19.3 `r4` 签署（沿用 r3 口径，仅新增解锁的 3 卡）

`PROD-CM-002` ← `REG-CM-001` 第一条 · `PROD-CM-003` ← `REG-CM-001` 第一条 · `PROD-FIN-003` ← `REG-FIN-001` 第三条
（`signed-pc8-r4.json`：25 项 = r2 保留 16 + r3 采纳 6 + 新增 3；supersedes r3；`attestation` 明确"未逐条再请确认具体条款，
Owner 可随时替换；**不构成合规结论**"）

### 19.4 现状（13 卡监管依据呈现）

| 状态 | 卡 |
|---|---|
| **SUPPORTED + 条款原文**（9 卡） | CB-002 · CM-001 · CM-002 · CM-003 · FIN-001 · FIN-003 · IB-001 · TF-001 · TF-002 |
| UNKNOWN（4 卡，如实不呈现） | CB-001 · FIN-002 · SET-001 · SET-002 |

门禁：L10 **384/384** · L11 **7469/7469** · L12 153/153 · L13 **1176/1176** · registry 167/167 · 统一门禁 **PASS 11 / FAIL 0 / SKIP 0**
接口实测：`PROD-CM-002 → SUPPORTED`，证据 `REG-CM-001 第一条` 原文。

### 19.5 剩 4 卡的修法（**均非代码**，其中一项待 Owner 确认）

| 卡 | 修法 | 是否需 Owner |
|---|---|---|
| `CB-001` | `REG-CB-001`（跨境人民币）**实体件入库**（登记已指名、无实体件） | 材料动作（我可执行） |
| `FIN-002`（供应链金融） | 登记**增绑** `REG-FIN-001` | **适用性判断 ⇒ 待确认** |
| `SET-001` / `SET-002` | 登记**增绑** `REG-CM-002`（含 `REG-SET-001` 别名收敛） | **适用性判断 ⇒ 待确认** |

---

## 20. Owner 追认 `r4` 口径（append-only · 2026-09-22T11:56:22+00:00）

Owner 2026-09-22 指示「**r4 签署（沿用 r3 口径，只新增新解锁的 3 卡）**」⇒ 对 `signed-pc8-r4.json` 作出**事后追认**。

| 项 | 内容 |
|---|---|
| 追认件 | `90_control/decisions/RATIFICATION-pc8-r4.md`（KERT 侧，append-only） |
| 追认范围 | ① 采纳口径沿用 r3（**本产品族专属监管源**、按 `(sourceId,条款号)` 最小）② 仅新增 3 张新解锁卡（`CM-002`/`CM-003` ← `REG-CM-001` 第一条；`FIN-003` ← `REG-FIN-001` 第三条）③ 其余 4 卡不采纳、保留 `CANDIDATE` |
| 边界（未放宽） | **不构成合规结论**；作合规依据须合规 Owner 逐条复核后重裁 |
| 追溯 | `signed-pc8.json`(29) → `r2`(撤销 13 条 N/A) → `r3`(采纳 6) → `r4`(+3) —— 各件**原样留存**，无回改 |

**实测快照（追认时）**：13 卡投影 **9 张 `SUPPORTED`+证据 / 4 张 `UNKNOWN`（如实不呈现）**；
门禁 `L10 384/384` · `L11 7469/7469` · `L12 153/153` · `L13 1176/1176` · `registry 167/167`。

**剩余 4 卡的两种修法（性质不同，处置不同）**：

| 卡 | 修法 | 是否需 Owner |
|---|---|---|
| `PROD-CB-001` | 需 `REG-CB-001` 逐字全文（已指名 **银发〔2018〕3 号**，但官方承载为 PDF、尚未取得可解析全文） | **材料动作**（TL 可执行，取到即可入库） |
| `PROD-FIN-002` | 登记**增绑** `REG-FIN-001` | **适用性判断 ⇒ 待 Owner 确认** |
| `PROD-SET-001` / `PROD-SET-002` | 登记**增绑** `REG-CM-002`（`REG-SET-001` 为别名，收敛未传导到绑定） | **适用性判断 ⇒ 待 Owner 确认** |

---

## 21. `REG-CB-001` 取证新证据（TL 实取官方 PDF ⇒ 扫描件、无 OCR）+ 4 卡剩余路径

> append-only · 2026-09-22T11:57:06+00:00

### 21.1 实取结果（不是推测）

| 步骤 | 结果 |
|---|---|
| 官方承载检索 | 两个官方页面（`safe.gov.cn` 河南分局 / `yidaiyilu.gov.cn`）均为**新闻稿**，无逐字条款；后者提供**通知原文 PDF 附件** |
| 下载 | `curl` 成功：`yidaiyilu.gov.cn/wcm.files/upload/CMSydylgw/201801/201801060952023.pdf` · **4 页 · 500759 字节** |
| 解析 | `pypdf` 逐页：**4 页各 1 个图像对象、文本层 0 字节** ⇒ **扫描件** |
| OCR 可行性 | 本机**无** `tesseract`/`pytesseract`（仅 `pdftoppm` 可栅格化）⇒ 无法取得可解析文本 |

⇒ 按既有纪律（**不 OCR 猜条文、不以报道冒充条文**）**仍不入库**，`REG-CB-001` 保持 `PENDING_SOURCE`。
**未把该 PDF 纳入仓**（避免引入未经 Owner 上传的二进制件）；URL + sha256 已登记，可复核。

### 21.2 请 Owner 择一（仅 `PROD-CB-001` 依赖该项）

| 选项 | 后果 |
|---|---|
| ① 提供**文本版**官方承载 / 已校对 OCR 件 | TL 立即转写入库 ⇒ `CB-001` 可进入采纳流程 |
| ② 授权安装 OCR 引擎并转写（须接受识别误差，`clause_verified=false`） | 同上，但引入 OCR 误差风险 |
| ③ 维持 `PENDING_SOURCE` | `CB-001` 的 `regulatoryBasis` 长期"未核验"，**不假装有依据** |

### 21.3 另 3 卡的修法（**适用性判断**，我未代定）

| 卡 | 拟改（1 行/卡） | 性质 |
|---|---|---|
| `PROD-FIN-002`（供应链金融） | `REG-FIN-001` 行末列「被引用产品卡」：`PROD-FIN-001/003` → `PROD-FIN-001/002/003` | 适用性判断 |
| `PROD-SET-001` | `REG-SET-001`（`REG-CM-002` 别名）的绑定**传导**到 SET 两张卡 | 适用性判断 |
| `PROD-SET-002` | 同上 | 适用性判断 |

**边界**：三项均改变"哪部法规适用于哪个产品"，属**合规适用性判断** ⇒ 未获你确认前**一字不改**（登记表只增不减，可回退）。
