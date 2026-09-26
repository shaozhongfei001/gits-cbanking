# Handoff｜P-1 公共语义 Owner（候任）技术准备包

| 项 | 值 |
|---|---|
| 交接方向 | 候任公共语义 Owner（**未任命**，`ROLE_BOARD.public_semantics_owner = UNASSIGNED_GAP`） → **tech_lead** |
| 交接日期 | 2026-09-20 |
| Loop | `ONTO1-ontology-split`，Wave `W-1`（只读分析），Gate `W1-prep` |
| 工作量类型 | 纯草稿 / 零执行：**未跑任何** `make generate`、**未**改 `specs/`、`generated/`、`CONTRACT_INDEX.yaml`、**未**标 `ACTIVE/FROZEN/DESIGN_APPROVED`、**未**发布任何 IRI、**未**代签 |

## 1. 交付物（5 件 DRAFT，均在 `docs/architecture/`）

| # | 文件 | 内容 | 对应任务 |
|---|---|---|---|
| 1 | `ONTO1-L1-八类术语定义稿-DRAFT.md` | 8 类 × 22 字段齐全；IRI 全为 `PENDING:{NS-L1}#X`；附录 A 机读 CSV（12 行 = 8 类 + 4 属性） | 任务 1 |
| 2 | `ONTO1-L1-建模规则R1-R9修订版-DRAFT.md` | R1~R9 修订版（**内部规则 / 参照对齐**名义；§0 禁用清单禁 `CONFORMANCE` 与国标符合性表述） | 任务 2 |
| 3 | `ONTO1-命名空间ADR联签意见-DRAFT.md` | U-1/U-3/U-4 选项与建议（**不给结论**）+ 联签前置 P-1~P-6 + 复核 V-1~V-8 + 不建议项 N-1~N-7 | 任务 3 |
| 4 | `ONTO1-Wave1独立语义契约库五条件落地方案-DRAFT.md` | 五条件逐条（机制/证据/失败码/变异用例）+ 骨架文件清单 + 零依赖白名单 + 四阶段流水线 + 版本线 + 三方评审 + G5 核验模板 | 任务 4 |
| 5 | `ONTO1-CQ1-CQ2履职准备-DRAFT.md` | fail-closed 具名拒绝码（CQ1 7 条 / CQ2 6 条 / 通用 5 条）+ 目标数断言四组数字与判定表 + 现有夹具复核与修订建议 | 任务 5 |

## 2. 本轮新增的**可复用回源结论**（供下一 holder 免于重复通读）

| # | 结论 | 回源 |
|---|---|---|
| 1 | `gits:Customer` domain reference + `customerId` 数据属性（退役对象）实测存在 | `specs/semantic/gits-core.owl.ttl:22-24`、`:27-30` |
| 2 | `memberOfGroup` domain 实为 **`LegalEntity`**、`connectsFrom/To` range 实为 **`LegalEntity`**（矩阵目标放宽为 `Party` ⇒ 属**扩大值域**） | `specs/semantic/gits-core.owl.ttl:151-155`、`:163-173` |
| 3 | `Customer` 的 8 个属性（`customer_id`/`cust_name`/`cust_code`/`cert_no`/`cust_type`/`cust_status`/`region`/`brid`） | `specs/semantic/gits-core.linkml.yaml:25-36` |
| 4 | **`playedBy` 全仓仅命中矩阵文书两行，无本体/代码实据** ⇒ 若需命名属性则计数 36→37，与既有口径不自洽 | `rg -n "playedBy"` → `03-逐术语权威矩阵-22字段.csv:5`、`attribution-45-v2.csv:5` |
| 5 | **`range 改指 CustomerRole` 实测 5 条**（`gateOfCustomer`/`ofCustomer`/`opportunityOfCustomer`/`profileOfCustomer`/`refersToCustomer`），另 1 条 `opportunityForProduct`→`ProductOffering`；**设计 §4.1 写「4 条」与矩阵不一致** | `grep -c "改指" evidence/attribution-45-v2.csv` → `5` |
| 6 | `Product` 基线注释仍写「权威物理源为 KERT 产品卡」，与设计 B-02 纠正口径不一致（注释尚未改写） | `specs/semantic/gits-core.owl.ttl:127-129` |

## 3. 五个待裁项（**须 TL / 委员会 / Owner 裁定，PSO 不得单方决定**）

| # | 待裁 | 出处 |
|---|---|---|
| O-1 | `Product` 本体注释口径改写（并入 Wave 2 注释改写清单） | 术语稿 §3.1 |
| O-2 | `playedBy` 三选一：登记为第 37 条属性 / 用匿名限制不新增命名属性 / 从矩阵删除括注 | 术语稿 §3.2 |
| O-3 | 「放宽约束（minor）」与「IRI 迁移/改名（major）」并发时的级别判定（07 号矩阵与矩阵登记不自洽） | 术语稿 §3.3、规则稿 Q-2 |
| O-4 | 设计 §4.1「4 条 range 改指」vs 矩阵「5 条」——建议以机读矩阵为准并回写设计 | 术语稿 §3.4 |
| O-5 | `memberOfGroup` domain 放宽为 `Party` 后，「集团关系仅连法人」的隐式约束是否由 SHACL 补回 —— 需 D4 表态 | 术语稿 §3.5 |

另：规则稿 Q-1（命令名 `make conformance` 是否改名）、CQ 稿 Q-2（业务日边界/时区）、Q-4（新字段是否入门禁）亦待裁。

## 4. 未决/未做（诚实声明）

- **未任命**：本人（候任 PSO）**没有**任何签署权，5 件全部为 DRAFT；Wave 1 仍因角色缺口阻塞（`OWNER_REQUESTS.md` A-1）；
- **未执行**：CQ1/CQ2 夹具**未运行**（Wave 4），状态仍 `NOT_EVALUATED`（D4 阻塞）；`REFERENCE-ALIGNMENT-REPORT.md` **未产出**（属 Wave 1/4）；
- **未触碰**：`specs/semantic/`、`generated/`、`specs/CONTRACT_INDEX.yaml`、`evidence/cq-fixtures/*.json`（后者为 TL 单写者路径）、`docs/dd/`（封版）；
- **KERT 仓**：本环境只读，本轮**未**读取亦未写入；
- **索引**：gits `INDEX_FRESH@71169042`；KERT `INDEX_STALE(144)` ⇒ 本轮**未**用索引对 KERT 结构做外推，所有结论均回源 `文件:行`。

## 5. 下一 holder（tech_lead）建议动作

1. 把 §3 的 O-1~O-5 并入 Wave 2 前置清单（其中 O-2/O-4 建议先提设计修订，勿在实现里绕开）；
2. 5 件 DRAFT 归档进 `EVIDENCE.md`（只作「候选角色准备包」证据，**不得**计入任何门禁 PASS）；
3. 角色任命到达后：把 5 件移交新任 PSO 作为就职基线，并在 `ROLE_BOARD` 把 `public_semantics_owner` 由 `UNASSIGNED_GAP` 改为实体；
4. 若 Wave 1 获准开工：先把方案稿 §10 的 B-1~B-7 逐条关闭（角色/根域/解析/库短名/建制/命令名）。

---

**红线复核**：本包未标 `DESIGN_APPROVED`/`ACTIVE`/`FROZEN`；未发布新 IRI；未代签；未改 `specs/semantic/`、`generated/`、`CONTRACT_INDEX`；KERT 仓只读；未用 `git add .`。
