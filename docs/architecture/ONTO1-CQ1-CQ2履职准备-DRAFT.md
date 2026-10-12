# ONTO1｜CQ1 / CQ2 履职准备：fail-closed 具名拒绝码与目标数断言口径（DRAFT）

| 项 | 值 |
|---|---|
| 文档性质 | **DRAFT 准备稿**——候任公共语义 Owner 任职技术准备产出；**待 Owner 签署**（其中拒绝码表需与 Integration Contract Owner / 独立 QA 共认） |
| 我的角色 | **候任**公共语义 Owner（未任命）。设计 §6.6 指定 **CQ1 / CQ2 的责任 Owner = 公共语义 Owner** |
| 执行时机 | **Wave 4**（夹具执行需实现存在）；本轮仅设计层，**不得标 `PASS`** |
| 输入 | `loops/ONTO1-ontology-split/evidence/cq-fixtures/CQ1.json`、`CQ2.json`；`evidence/CQ-FIXTURES-DESIGN.md`；复审包 `08-CQ语义验收矩阵.md`、`06-验证状态模型与状态跃迁表.md`；设计 V2.0 §6.1/§6.2/§6.6 |
| 当前状态 | CQ1 / CQ2 = `NOT_EVALUATED`，外部阻塞 **D4**（数据 Owner 未签） |

---

## 1. 职责边界（先说清什么不是我做的）

| 事项 | 归谁 | 说明 |
|---|---|---|
| 定义 CQ1/CQ2 的术语语义与拒绝规则 | **公共语义 Owner（我，待任命）** | 本稿即为该职责的产出 |
| 提供 A-Box 权威实例 / 授权投影 | 数据 Owner（**D4**） | 未签署前 CQ 只能 `NOT_EVALUATED` |
| 夹具**执行** | Wave 4 执行方（实现存在后） | 本轮无实现，执行不可发生 |
| 记录 `PASS` | **独立 QA** | 开发/设计角色**禁止自签** |
| 记录 `WAIVED_FOR_DEVELOPMENT` | Owner（带解除条件与到期日） | 豁免**永不**满足激活门禁 |
| `SourceIdentifier` 字段最终取值 | 数据 Owner（D4）为签署方；公共语义 Owner 出字段草案 | 字段建议见 `ONTO1-L1-八类术语定义稿-DRAFT.md` §2.8 |

---

## 2. 现有夹具复核（CQ1 / CQ2 逐字段）

### 2.1 CQ1 现状（`evidence/cq-fixtures/CQ1.json`）

| 字段 | 现值 | 复核结论 |
|---|---|---|
| `question` | 某法人何时、依据哪个源系统成为客户？ | ✅ 与设计 §6.6 一致 |
| `validates` | `CustomerRole + SourceIdentifier`（L1） | ✅ 与设计 §4.2 一致 |
| `query` | 按 LegalEntity 查 CustomerRole 及其 SourceIdentifier | ✅ 可执行形态；**建议**补查询语言（SPARQL/图查询/API）字段，便于执行期不复用歧义 |
| `positive` | 法人 LE-001 经 `SourceIdentifier{EDWCRM, Customer, C001, 2026-01-05}` 关联 `CR-001` | ⚠️ 字段名与设计口径对齐；**但** LE-001 / CR-001 / EDWCRM 均为 SIM 值，须随夹具显式标 `simulationOnly=true` |
| `negative` | 无 `SourceIdentifier` ⇒ 摄取拒绝（fail-closed） | ⚠️ 「摄取」与「查询」两个动作混在一条负例里；**建议**拆为两条（摄取拒绝 + 查询拒绝），拒绝码不同 |
| `expected` | 正例返回时点 + 来源；负例具名拒绝 `MISSING_SOURCE_IDENTIFIER` | ⚠️ 只有 1 个拒绝码；**建议**按 §3 表补全，并加 `targetCount` 口径（§5） |
| `mutation` | 删除 `sourceSystem` ⇒ 必须 FAIL | ⚠️ 表述为「必须 FAIL」指向不明（夹具 FAIL 还是门禁 FAIL）；**建议**改为「变异检出：注入后负例断言必须命中 `SOURCE_SYSTEM_EMPTY`」 |
| `owner` / `status` / `gate` / `external_blocker` | 公共语义 Owner（待任命）/ `NOT_EVALUATED` / Wave 4 · 需 D4 / D4 | ✅ 合规 |
| `schema` | `onto1_cq_fixture/v1` | ✅ 与 `CQ-FIXTURES-DESIGN.md` 一致 |

### 2.2 CQ2 现状（`evidence/cq-fixtures/CQ2.json`）

| 字段 | 现值 | 复核结论 |
|---|---|---|
| `question` / `validates` | 集团成员关系在指定业务日是否有效，来源是什么？/ `GroupMembership` | ✅ 一致 |
| `query` | 按（fromEntity, toEntity, 业务日 D）查有效 GroupMembership 及来源 | ✅；**建议**补「业务日」的时区与边界口径（含/不含 `validTo` 当日） |
| `positive` | M-001（2025-06-01~2026-12-31，来源=集团登记系统），D=2026-09-20 ⇒ 有效 | ✅ |
| `negative` | 同一对实体在 D=2027-01-01 查询 ⇒ 无效（过期不得返回有效） | ⚠️ **只覆盖「过期」一种失败**；缺「无有效期声明」「来源缺失」「同日多活跃关系」等负例（§3） |
| `expected` | 正例返回有效+来源；负例返回无效且不带「有效」标记 | ⚠️ **缺具名拒绝码**（当前负例只说「返回无效」，未规定码）；**必须**补 `MEMBERSHIP_EXPIRED` |
| `mutation` | 把 `validTo` 改到查询日之后 ⇒ 负例翻正必须被检测为变更 | ⚠️ 语义可执行；**建议**明确「检出」= 变异用例期望 FAIL 且原负例断言命中 |
| `owner` / `status` / `gate` / `external_blocker` / `schema` | 同 CQ1 | ✅ |

> **共性缺口（CQ1/CQ2 都有）**：① 无 `targetCount` 口径（设计 §6.2 要求记「期望目标数 vs 实际目标数」）；② 负例拒绝**未闭合到枚举码**（只有 1 个码）；③ SIM 标记未写；④ 查询语言未写。

---

## 3. fail-closed 具名拒绝码（本稿核心）

### 3.1 命名规范（建议全库统一）

```
<DOMAIN>_<CONDITION>
```
- 全大写 + 下划线；`DOMAIN` ∈ {`SOURCE_IDENTIFIER`, `GROUP_MEMBERSHIP`, `FIXTURE`, `GATE`, `EXTERNAL`}；
- 码必须**闭合枚举**并登记在本文件（§3.2/§3.3）；出现未登记码 ⇒ 门禁按 FAIL 处理（fail-closed，不得当作新码自动接受）。

### 3.2 CQ1 拒绝码表

| # | 拒绝码 | 触发条件 | 拒绝动作 | 现状 |
|---|---|---|---|---|
| 1 | `MISSING_SOURCE_IDENTIFIER` | 实例无任何 `SourceIdentifier` 关联 | 拒绝摄取 + 拒绝返回该实例 | ✅ 已在夹具 |
| 2 | `SOURCE_SYSTEM_EMPTY` | `SourceIdentifier.sourceSystem` 缺失或空串 | 拒绝摄取 | ➕ 建议新增（对应现有 `mutation`） |
| 3 | `ORIGINAL_ID_EMPTY` | `originalId` 缺失或空串 | 拒绝摄取 | ➕ 建议新增 |
| 4 | `IDENTIFIER_INTERVAL_INVALID` | `validFrom > validTo`，或 `validFrom` 缺失 | 拒绝摄取 | ➕ 建议新增 |
| 5 | `IDENTIFIER_NOT_EFFECTIVE_ON_DATE` | 查询日不在任何 `SourceIdentifier` 生效区间内 | **拒绝**（不得返回「无来源」的空结果） | ➕ 建议新增 |
| 6 | `IDENTIFIER_AMBIGUOUS` | 同一主体在同一来源系统下有多个同时生效的 `originalId`，查询未指定消歧依据 | 拒绝（要求消歧输入） | ➕ 建议新增 |
| 7 | `CUSTOMER_ROLE_UNANCHORED` | `CustomerRole` 存在但无任何可追溯主体关联（既无 `playedBy` 关系亦无主体锚定） | 拒绝（**受 O-2 未决项约束**，见 `ONTO1-L1-八类术语定义稿-DRAFT.md` §3.2） | ➕ 建议新增（**待 O-2 裁定后才可生效**） |

### 3.3 CQ2 拒绝码表

| # | 拒绝码 | 触发条件 | 拒绝动作 | 现状 |
|---|---|---|---|---|
| 1 | `MEMBERSHIP_EXPIRED` | 查询业务日 > `validTo` | 返回「无效」，且**不得**带「有效」标记 | ➕ 建议新增（对应现有负例） |
| 2 | `MISSING_VALIDITY_WINDOW` | `validFrom` 或 `validTo` 缺失（有效期强制） | 拒绝摄取 + 拒绝返回 | ➕ 建议新增 |
| 3 | `VALIDITY_WINDOW_INVALID` | `validFrom > validTo` | 拒绝摄取 | ➕ 建议新增 |
| 4 | `SOURCE_DECLARATION_MISSING` | `GroupMembership` 无来源声明（来源系统/来源文书缺失） | 拒绝（来源是 CQ2 的必答项） | ➕ 建议新增 |
| 5 | `MEMBERSHIP_BOUNDARY_UNDECIDABLE` | 查询业务日恰在 `validTo` 当日，且未声明边界口径（含/不含当日） | 拒绝并要求明确口径 | ➕ 建议新增（**须先定口径**，见 §9 Q-2） |
| 6 | `DUPLICATE_ACTIVE_MEMBERSHIP` | 同一 (fromEntity, toEntity) 在同一业务日存在多条活跃成员关系且无法区分（关系类型/来源相同） | 拒绝（不得静默取其一） | ➕ 建议新增 |

### 3.4 通用（非 CQ 特有）拒绝码 — 门禁/夹具层

| # | 拒绝码 | 触发条件 | 归属 |
|---|---|---|---|
| 1 | `FIXTURE_MISSING` | 夹具文件缺失或六要素不全 | 门禁（`wi_a6_cq_fixtures` 家族） |
| 2 | `FIXTURE_UNDECLARED_REJECT_CODE` | 断言出现 §3.2/§3.3 未登记的拒绝码 | 门禁（fail-closed） |
| 3 | `QUERY_TARGET_SET_EMPTY` | 实际目标数 = 0 | 执行期：**不得给绿** ⇒ 记 `NOT_EVALUATED`（无实例）或 `DESIGN_ONLY`（无实现） |
| 4 | `EXTERNAL_BLOCKER_ACTIVE` | D4（或 D2）未签而尝试执行/记 PASS | 执行期门禁（硬拦） |
| 5 | `QUERY_SILENT_EMPTY_RESULT` | 查询返回空集但无具名拒绝码 | 执行期门禁（**本条是 fail-closed 的核心**） |

### 3.5 拒绝语义三条硬规则

1. **具名**：任何拒绝必须带 §3 表中的码；**返回空集/空对象而无声明的拒绝 = 门禁 FAIL**（`QUERY_SILENT_EMPTY_RESULT`）；
2. **不降级**：拒绝必须是终态，**不得**以「部分结果 + 警告」代替（禁止 partial 降级）；
3. **不新增即失败**：断言中出现未登记码 ⇒ FAIL（防止实现方自造码绕过校验）。

---

## 4. 目标数断言口径（设计 §6.2 落地）

### 4.1 必记四组数字

| 数字 | 定义 | 期望 |
|---|---|---|
| `expectedTargets` | 该查询**应命中**的目标数（夹具声明，设计期写死） | > 0；= 0 ⇒ 夹具无效 |
| `actualTargets` | 执行时**实际**命中的目标数 | 应等于 `expectedTargets` |
| `positiveHits` / `negativeHits` | 正例/负例命中数 | 各自 **≥1**（缺任一 ⇒ 夹具不合格） |
| `mutationCaught` | 变异用例检出数 / 变异用例总数 | **= 1.0**（全检出；< 1 ⇒ 断言空转） |

### 4.2 判定表

| 组合 | 判定 | 说明 |
|---|---|---|
| `actualTargets = 0`（无实例/无实现） | `NOT_EVALUATED` 或 `DESIGN_ONLY` | **不得**记 PASS；**不得**表述为「0 目标 0 违规即通过」 |
| `actualTargets > 0` 且 `positiveHits ≥1`、`negativeHits ≥1`、`mutationCaught = 1.0`、无未登记码 | 可提交独立 QA 复核 → `PASS` | **只有独立 QA 可记 `PASS`** |
| `mutationCaught < 1.0` | `FAIL`（断言空转） | 先记 `FAILURES.md` 再修（本仓库既有防假绿纪律） |
| `expectedTargets = 0` | 夹具不合格（设计缺陷） | 须回设计层重写夹具 |

### 4.3 CQ1 / CQ2 的建议目标数声明（待 D4 签署后由执行方填实际值）

| CQ | expectedTargets（建议形态） | 说明 |
|---|---|---|
| CQ1 | ≥1（正例：1 个 `CustomerRole` + ≥1 个 `SourceIdentifier`）；负例 ≥4（对应 §3.2 的 4 类可执行拒绝） | 建议先以受控夹具（SIM + `simulationOnly=true`）满足 D4 前的开发需要 |
| CQ2 | ≥2（正例 1 有效 + 1 因过期无效）；负例 ≥4（对应 §3.3） | 「边界日」负例依赖 §9 Q-2 口径确定后启用 |

---

## 5. 五态与激活门禁（不得越线）

| 规则 | 出处 | 本轮遵守方式 |
|---|---|---|
| 设计阶段任何 CQ **不得 `PASS`** | `CQ-FIXTURES-DESIGN.md` §2 纪律 | CQ1/CQ2 保持 `NOT_EVALUATED` |
| `NOT_EVALUATED` / `DESIGN_ONLY` **不满足激活门禁** | 设计 §6.1；复审包 06 号 §3 | 不得把本轮准备冒充为激活证据 |
| `WAIVED_FOR_DEVELOPMENT` **永不**满足激活门禁 | 设计 §6.1 | 即便 Owner 批豁免，激活时仍须真实 `PASS` |
| D4 未签 ⇒ CQ1/CQ2 不得进入可执行态 | 设计 §3.2；`OWNER_REQUESTS.md` D4 行 | 本轮只写规则与口径 |
| `PASS` 只可由独立 QA 记录 | 仓库红线 | 我（候任 PSO）不记任何 `PASS` |

---

## 6. 对现有夹具的修订**建议**（不落地，仅建议）

> 以下为 JSON 片段式建议，供 Wave 4 前的夹具维护者参考。**本稿不修改 `evidence/cq-fixtures/*.json`**（该目录归 TL 单写者路径，见 `memory/ORCHESTRATOR.md` §3）。落地须由 TL 执行并记 `FAILURES/EVIDENCE`。

### 6.1 CQ1 建议新增字段

```json
{
  "queryLanguage": "SPARQL | graph-query | api-call   ← 待定，建议 SPARQL",
  "simulationOnly": true,
  "negativeCases": [
    {"code": "MISSING_SOURCE_IDENTIFIER",      "action": "ingest-reject"},
    {"code": "SOURCE_SYSTEM_EMPTY",            "action": "ingest-reject"},
    {"code": "ORIGINAL_ID_EMPTY",              "action": "ingest-reject"},
    {"code": "IDENTIFIER_INTERVAL_INVALID",    "action": "ingest-reject"},
    {"code": "IDENTIFIER_NOT_EFFECTIVE_ON_DATE","action": "query-reject"},
    {"code": "IDENTIFIER_AMBIGUOUS",           "action": "query-reject"}
  ],
  "targetCounts": {"expectedTargets": 1, "positiveHits": 1, "negativeHits": 6, "mutationCaughtRatio": 1.0},
  "mutationCases": [
    {"mutate": "删除 SourceIdentifier.sourceSystem", "expect": "SOURCE_SYSTEM_EMPTY 命中"}
  ]
}
```

### 6.2 CQ2 建议新增字段

```json
{
  "queryLanguage": "SPARQL | graph-query | api-call",
  "businessDayBoundary": "待定（含 validTo 当日 / 不含当日） ← 见 §9 Q-2",
  "timezone": "待定（建议固定，并在夹具中显式声明）",
  "simulationOnly": true,
  "negativeCases": [
    {"code": "MEMBERSHIP_EXPIRED",              "action": "return-invalid"},
    {"code": "MISSING_VALIDITY_WINDOW",         "action": "ingest-reject"},
    {"code": "VALIDITY_WINDOW_INVALID",         "action": "ingest-reject"},
    {"code": "SOURCE_DECLARATION_MISSING",      "action": "ingest-reject"},
    {"code": "MEMBERSHIP_BOUNDARY_UNDECIDABLE", "action": "query-reject"},
    {"code": "DUPLICATE_ACTIVE_MEMBERSHIP",     "action": "query-reject"}
  ],
  "targetCounts": {"expectedTargets": 2, "positiveHits": 1, "negativeHits": 6, "mutationCaughtRatio": 1.0},
  "mutationCases": [
    {"mutate": "把 validTo 改到查询日之后", "expect": "MEMBERSHIP_EXPIRED 断言不得命中 ⇒ 变异检出"}
  ]
}
```

### 6.3 与既有门禁的一致性核查

`scripts/onto1_cq_fixtures.py --gate` 要求「六要素完整 + 每 CQ 具备否定式断言 + 设计阶段无 PASS」。上述建议字段为**追加**，不破坏六要素；但**追加字段是否纳入门禁校验**需 TL 决定（见 §9 Q-4），否则新口径会停留在文档层而非门禁层。

---

## 7. 我的履职前置条件（缺一即无法真正履职）

| # | 前置 | 归属 | 说明 |
|---|---|---|---|
| R-1 | 公共语义 Owner **正式任命** | Owner | 未任命前本稿只是技术准备 |
| R-2 | **D4 签署**（A-Box 权威确认 + 授权投影合同） | 数据 Owner + 业务 Owner | 未签 ⇒ CQ1/CQ2 只能 `NOT_EVALUATED` |
| R-3 | 拒绝码表由三方共认（我 + Integration Contract Owner + 独立 QA） | 三方 | 否则执行期码表解释不一 |
| R-4 | `SourceIdentifier` 字段集冻结（至少 `sourceSystem`/`objectType`/`originalId`/`validFrom` 四项必填） | 我（草案）+ D4（签署） | 拒绝码 1~4 依赖字段集 |
| R-5 | 边界日与时区口径（CQ2） | 我（建议）+ D4（确认） | 拒绝码 `MEMBERSHIP_BOUNDARY_UNDECIDABLE` 依赖此 |
| R-6 | 执行环境（Wave 4 实现 + 夹具执行器） | TL / Feature Pilot | 未到 Wave 4 不执行 |

---

## 8. 待决项（我不单方决定）

| # | 待决 | 决策 Owner | 影响 |
|---|---|---|---|
| Q-1 | `playedBy` 是否为命名属性（O-2） | 设计 Owner | 决定 CQ1 拒绝码 `CUSTOMER_ROLE_UNANCHORED` 是否可用 |
| Q-2 | 业务日边界口径（`validTo` 当日是否算有效）与时区 | 公共语义 Owner（建议）+ 数据 Owner（确认） | 决定 CQ2 边界负例、`MEMBERSHIP_BOUNDARY_UNDECIDABLE` 的判定 |
| Q-3 | 「来源声明」在 CQ2 中的最小充分集（来源系统？来源文书？来源时间？） | 公共语义 Owner + 数据 Owner | 决定 `SOURCE_DECLARATION_MISSING` 的判据 |
| Q-4 | 建议字段（`targetCounts`/`mutationCases`/拒绝码枚举）是否纳入 `onto1_cq_fixtures.py --gate` | TL | 不纳入 ⇒ 口径只停在文档层（易空转） |
| Q-5 | 拒绝码是否与 L4 注册表的错误码体系统一命名空间 | Integration Contract Owner | 决定跨 CQ（CQ1~CQ6）码表是否需要统一前缀 |
| Q-6 | `QUERY_SILENT_EMPTY_RESULT` 由谁实现（查询侧 or 门禁侧） | TL + 执行方 | 决定 fail-closed 的拦截点 |

---

## 9. 非声明

- 本稿**未**修改 `evidence/cq-fixtures/CQ1.json` / `CQ2.json`，**未**改任何门禁脚本，**未**标任何 `PASS`；
- CQ1/CQ2 当前状态仍为 `NOT_EVALUATED`，外部阻塞 **D4**；
- 本稿不构成 `DESIGN_APPROVED`、不代表公共语义 Owner 已任命；
- 与设计 V2.0 / 复审包冲突时以设计与复审包为准；不含国标条款级声称或 `CONFORMANCE` 字样。
