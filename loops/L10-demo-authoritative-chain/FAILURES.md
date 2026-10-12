# L10 FAILURES

> Loop: `L10-demo-authoritative-chain`（PI-ARCH-IMPLEMENTATION-01 / 阶段 B）
> 建立: 2026-09-06 · 分级 `BLOCKER` / `MAJOR` / `MINOR` / `OBSERVATION`

本文件只记录 L10 **新发现或承继**的缺陷。PI-0 / L03 缺陷状态见各自 Loop 的 FAILURES。

---

## F-L10-01 · MAJOR · OPEN（承继，早于本施工）

**标题**：`make check` 失败，涉及 `CTR-PR-API-001`

**来源**：L00 首次真实执行 `make check` 时发现（EXIT=2），早于 L10 施工，非本 Loop 引入。

**证据**：`specs/CONTRACT_INDEX.yaml:382` 登记 `CTR-PR-API-001`（`openapi_paths`，
`authority_source: specs/openapi/product-recommendation.openapi.json`，`status: CANDIDATE`，
`generated: []`）。

**影响**：`make check`（合同/生成物/Loop 模板/安全基线）整体非零退出，
阻断任何依赖 `make check` 的 CI 结论；但不阻断 `specs/product-knowledge/check_all.py`
专题门禁（本 Loop 8/8 PASS）。

**Owner**：`integration_contract_owner`（CONTRACT_INDEX 登记的 owner 角色）

**本 Loop 处置**：**不修复**（超出 L10 scope，且改动触及跨专题既有契约）。
仅登记，供 L31/集成阶段承接。**不因本项回退 L10 结论，也不把它算作 L10 门禁失败**。

---

## F-L10-02 · MAJOR · RESOLVED（本 Loop 红测发现）

**标题**：DEMO 标记检查被正文中对字段名的引用文本骗过，构成"假安全"

**发现时机**：W3 红测（把 front matter 的 `provenance_state: DEMO` 改为 `VERIFIED` 后复跑门禁）

**证据**：首版检查为 `"provenance_state: DEMO" in head`，而 DEMO 文件正文的声明段落里
含有 `` `provenance_state: DEMO` `` 引用文本。注入后仅字节数/hash 两项报错，
front matter 检查仍 PASS —— 门禁看似有效实则无力拦截冒充。

**修复**：改为只解析 YAML front matter（首个 `---` 分隔块），并用
`^provenance_state:\s*DEMO\s*$` 行级匹配。

**验证**：注入后 3 项 FAIL（含 front matter 项）；还原后 67/67 PASS。

**教训**：与 L03 W8「反例必须被拒」同源 —— 门禁的有效性只能由红测证明，不能由代码自证。

---

## O-L10-01 · OBSERVATION · OPEN

**标题**：`CTR-PK-RLS-001`（Release）未定义 `provenanceState` 字段

**影响**：红线要求"demo Release 必须打 `provenance_state=DEMO` 不冒充真实"，
但 Release 合同当前无该字段可供承载。`INV-EVS-10` 已在证据侧表达约束，
Release 侧无字段则门禁无法校验。

**处置**：本 Loop 不修改 RLS-001（避免 L13 二次返工）。**L13 施工前必须补**
Release 级 `provenanceState` 字段与对应不变式（建议 `INV-RLS-08`）。

**Owner**：Contract Owner（Gate A2 复核）

---

## O-L10-02 · OBSERVATION · OPEN

**标题**：SourceVersion / Fragment 缺少 JSON Schema 合同，仅由 V023 表列定义

**影响**：EVS-002 引用 `sourceVersionId` / `fragmentId`，但这两个对象本身没有 schema 合同，
引用链在合同层不闭合；本 Loop 以 `migration-candidates/V023` 的
`pk_source_version` / `pk_fragment` 列作为**唯一字段真值**，未发明任何字段。

**处置**：登记为合同缺口，建议 L11 前由 Contract Owner 裁决是否补
`CTR-PK-SVD-001` / `CTR-PK-FRG-001`。本 Loop 不新建合同，避免越权与范围蔓延。

---

## 承继缺陷状态（本 Loop 未改变）

| ID | 状态 | 说明 |
|---|---|---|
| F-L00-07 | **BLOCKED_ON_OWNER** | 真实权威材料缺口 **27/28**，DEMO 3 份**不抵扣**，仍未解除 |
| F-L00-02 | OPEN | 待独立 QA 复核 |
| F-L00-09 | OPEN | 解析鲁棒性，需真实材料，属 L10+ 排期 |
| F-L03-03 | OPEN | 3 张 FALSE_PLAUSIBLE 卡待 OQ-E 终裁 |

---

## 内建已知冲突（演示数据，非缺陷）

`SRC-CM-001` 第十条（主账户最低留存 **50 万元**）与 `SRC-CM-003` 第六条
（集团现金池主账户最低留存 **100 万元**）构成 `VALUE_MISMATCH`。
**由 L10 故意保留**，作为 L12 冲突检测与 ConflictCase 编译的实证样本。
已在源登记表 §5.8 与 EVIDENCE.md 显式声明，**不得事后静默修正**。
