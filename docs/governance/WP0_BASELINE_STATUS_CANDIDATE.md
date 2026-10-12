# WP0-1 基线与状态治理候选（V2.0 受控输入索引候选 + 状态冲突登记）

```text
文档编号   = WP0_BASELINE_STATUS_CANDIDATE
角色       = GITS/MAIN
任务       = WP0-1（GITS/MAIN 基线与状态治理）
批次       = GITS-WP0（见 docs/dispatch 派工清单 WP0-1）
状态       = CANDIDATE
FROZEN     = NO
IMPLEMENTED = NO
形成日期   = 2026-08-31
权威依据   = 三段式落地方案 V1.0 + 产品解读与推荐交接总册 V1.1 + 本体智能体交接总册 V1.0
取证 HEAD  = aea4d8b21d26bb748d84b69ec9bb5908500aa28e
```

> 本文件是基线状态治理的**候选登记**，不宣称任何冻结、实施、联调或生产结论。它只登记取证结果、候选索引、冲突与关闭条件。最终裁决权在 MAIN/Owner。

---

## 0. 取证结果（先取证，再下结论）

本轮读取以下权威来源与仓库现状，作为全部结论的证据：

| # | 文件/来源 | 关键内容 |
|---|---|---|
| 1 | `specs/BASELINE_INDEX.yaml` | `governance.freeze_state = FROZEN_2026_08_06`；`inputs[]` 当前仅有 V1.0 期 6 项输入，**无任何 V2.0 条目** |
| 2 | `README.md` 顶部状态块 | `STATUS=DEV_PACKAGE_CANDIDATE`；`PRODUCTION_READY=NO`；`FROZEN=NO` |
| 3 | `docs/governance/STATUS.md` | `PACKAGE_STATE=FROZEN_DELIVERY_PACKAGE`；`FROZEN=YES_2026_08_06_CUSTOMER_SIGNED`；`PRODUCTION_READY=P18_PROD_CONFIG_AND_VERIFY_SCRIPT_READY` |
| 4 | `docs/baseline/PRODUCT-BASELINE-V1.0.md` | 头部「状态：已冻结（客户方于 2026-08-06 签字确认）」；M19 产品知识解读智能体被标为 `DEFERRED` |
| 5 | `docs/baseline/` 目录 | 仅含 `PRODUCT-BASELINE-V1.0.md`，**不存在** `PRODUCT-BASELINE-V2.0.md` |
| 6 | 三段式落地方案 V1.0 | V2.0 业务需求基线「已正式批准」；PB-V2.0-R1「8 个产品族、48 项能力，`HUMAN_APPROVED / APPROVED_WITHOUT_FREEZE`」；BLK-02 要求「MAIN 发布 V2.0 受控输入索引，并明确旧文件仅作历史参考」 |
| 7 | 产品解读与推荐交接总册 V1.1 | 输入优先级第 1、2 位为 V2.0 业务需求基线、PB-V2.0-R1；「仓库旧版 `PRODUCT-BASELINE-V1.0.md` 中 M19 被标为 `DEFERRED`，与 V2.0 一期优先级冲突，该旧状态不得回流」 |
| 8 | 本体智能体交接总册 V1.0 | 「V2.0 基线状态不能由本体智能体在仓库中自行补写；必须由 MAIN/Owner 发布受控输入索引或提供对应文件和签署证据」；BLK-01「README 与治理状态的 FROZEN 冲突」、BLK-02「V2.0 业务/产品基线未在主分支可见」 |

**一句话结论**：V2.0 业务需求基线 + PB-V2.0-R1 尚未以「受控输入索引」形式进入本仓库；仓库内 FROZEN/状态字段存在多来源冲突（README 与 STATUS.md 不一致）；旧版 `PRODUCT-BASELINE-V1.0.md` 的 M19=DEFERRED 与 V2.0 一期范围冲突。

---

## 1. (a) V2.0 受控输入索引候选（外部受控输入，需 MAIN/Owner 发布）

> **治理红线**：以下两条是**外部受控输入**，其权威版本、文件与签署证据均不在本仓库。仓库内**不得自行补写** V2.0 索引条目、不得伪造 `PRODUCT-BASELINE-V2.0.md`、不得将下述状态升级为 `FROZEN`。必须由 MAIN/Owner 发布受控输入索引（或提供对应文件与签署证据）后，方可回填到 `specs/BASELINE_INDEX.yaml`。

| # | 受控输入（候选） | 标题/内容 | 权威来源 | 权威状态 | 处置（候选） |
|---|---|---|---|---|---|
| 1 | V2.0 业务需求基线（候选 ID 建议 `REQ-GITS-V2.0-20260831`，非权威） | 2026-08-31 正式批准的《飞-银行对公知识工程与岗位智能体》V2.0 业务需求基线 | 三段式 V1.0 §0/§1.2；交接总册 V1.1 §1.1 | 已正式批准；当前唯一有效需求基线，优先于仓库旧版产品文件 | 外部受控输入；待 MAIN/Owner 发布受控索引 + 提供文件/签署证据；仓库内不得自行补写 |
| 2 | `PB-V2.0-R1` | 8 个产品族、48 项产品能力 | 三段式 V1.0 §1.2；交接总册 V1.1 §1.1 | `HUMAN_APPROVED / APPROVED_WITHOUT_FREEZE`（`FROZEN=NO`） | 外部受控输入；不在本仓库重新定义产品清单；待 Owner 发布受控索引 + 签署证据 |

**候选索引字段建议**（供 MAIN/Owner 发布时参考，本文件不落地为权威）：`id / title / authority_file / sha256 / owner_decision / state / effective_from`。

**明确禁止**：
- 禁止由 GITS/MAIN 或任何智能体在仓库内自行补写 V2.0 基线状态或文件；
- 禁止用旧 `PRODUCT-BASELINE-V1.0.md` 冒充新 V2.0 业务需求基线；
- 禁止将 `APPROVED_WITHOUT_FREEZE` 或 `HUMAN_APPROVED` 表述为 `FROZEN`。

---

## 2. (b) 旧版产品基线 `docs/baseline/PRODUCT-BASELINE-V1.0.md` 历史地位声明

- **地位**：仅作**历史参考**，记录 2026-08-06 客户签字冻结的 V1.0 首期交付基线（4 领域、22 模块、206 项功能候选；FROZEN 10 模块 / DEFERRED 12 模块）。它在**不与 V2.0 一期冲突**的前提下继续作为 V1.0 历史档案保留，不再作为 V2.0 一期施工顺序的权威依据。
- **已知冲突点**：该文件将 **M19 产品知识解读智能体** 标为 `DEFERRED`；但 V2.0 一期范围已纳入产品解读（交接总册 V1.1 明确「该旧状态不得回流」）。因此 M19=DEFERRED 的旧结论**必须声明失效**，仅作 V1.0 历史状态，不得回流到 V2.0 开发顺序。
- **处置（候选）**：在 MAIN/Owner 发布 V2.0 受控输入索引时，同时出具「V1.0 历史地位声明」，并以索引条目标注 `HISTORICAL_REFERENCE_ONLY`；未获 Owner 裁决前，本任务**不改动**该文件。

---

## 3. (c) STATUS_SOURCE_CONFLICT 登记

### 3.1 头条冲突：`FROZEN` 字段不一致（README vs STATUS.md）

| 来源 | 文件 | 字段 | 值 |
|---|---|---|---|
| 来源 A | `README.md`（顶部状态块） | `FROZEN` | `NO` |
| 来源 B | `docs/governance/STATUS.md` | `FROZEN` | `YES_2026_08_06_CUSTOMER_SIGNED` |

**结论：不一致（CONFLICT）**。

### 3.2 两个来源的完整字段比对

| 概念 | README.md 字段/值 | STATUS.md 字段/值 | 是否一致 |
|---|---|---|---|
| 包标识 | `PACKAGE_ID=GITS-KNO-DEV-PACKAGE-V0.1` | `PACKAGE_ID=GITS-KNO-DEV-PACKAGE-V0.1` | 一致 |
| 框架标识 | `FRAMEWORK=GITS-SDD-FRAMEWORK-V0.2` | `FRAMEWORK_ID=GITS-SDD-FRAMEWORK-V0.2` | 值一致，字段名不一致 |
| 包状态 | `STATUS=DEV_PACKAGE_CANDIDATE` | `PACKAGE_STATE=FROZEN_DELIVERY_PACKAGE` | **冲突** |
| QA 状态 | `QA_GATE=PENDING_INDEPENDENT_QA` | `INDEPENDENT_QA=REGRESSION_SUITE_READY_PENDING_EXECUTION` | **冲突**（字段名+语义不一致） |
| 生产就绪 | `PRODUCTION_READY=NO` | `PRODUCTION_READY=P18_PROD_CONFIG_AND_VERIFY_SCRIPT_READY` | **冲突** |
| 冻结状态 | `FROZEN=NO` | `FROZEN=YES_2026_08_06_CUSTOMER_SIGNED` | **冲突（头条）** |

### 3.3 补充来源（同概念、第三/第四来源）

| 来源 | 文件 | 字段 | 值 | 备注 |
|---|---|---|---|---|
| 来源 C | `specs/BASELINE_INDEX.yaml` | `governance.freeze_state` | `FROZEN_2026_08_06` | 与 STATUS.md 方向一致，与 README 冲突 |
| 来源 D | `docs/baseline/PRODUCT-BASELINE-V1.0.md` | 头部「状态」 | `已冻结（客户方于 2026-08-06 签字确认）` | 与 STATUS.md 方向一致，与 README 冲突 |

### 3.4 成因（取证推断，非结论）

- `README.md` 的 `FROZEN=NO / STATUS=DEV_PACKAGE_CANDIDATE / PRODUCTION_READY=NO` 未随 2026-08-06 的冻结签字（STATUS.md 变更）同步更新，属**陈旧状态**。
- `docs/governance/STATUS.md` 记录 `FROZEN=YES_2026_08_06_CUSTOMER_SIGNED`，但后续 2026-08-25/26 又持续追加未冻结的 UX 输入，其 `FROZEN=YES` 与「仍在追加非冻结输入」的现状是否仍成立，需 Owner 复核。

### 3.5 建议裁决动作

1. **Owner 指定当前基线状态与权威来源**（对应 BLK-01 关闭条件）：
   - 建议以 `docs/governance/STATUS.md` 为**状态治理 SSOT**，并明确 `README.md` 顶部状态块仅作入口摘要、必须随 STATUS.md 同步（或改为「见 STATUS.md」指针）；
   - 若 Owner 确认 2026-08-06 冻结仍有效 → 将 `README.md` 同步为 `FROZEN=YES_2026_08_06_CUSTOMER_SIGNED`；
   - 若 Owner 确认首期冻结已被 V2.0 一期范围取代 → 明确将 `FROZEN` 降级并说明依据，同时说明 `APPROVED_WITHOUT_FREEZE` 的产品基线尚待签署。
2. 统一字段名：`STATUS` vs `PACKAGE_STATE`、`QA_GATE` vs `INDEPENDENT_QA`、`FRAMEWORK` vs `FRAMEWORK_ID` 二选一，避免同名不同义。
3. 上述裁决完成前，本仓库任何实现/契约文件**不得**依赖 `FROZEN` 单一取值推进施工结论。

---

## 4. (d) 关闭条件清单

本候选（WP0-1）视为关闭，需全部满足：

| # | 关闭条件 | 责任方 | 判据 |
|---|---|---|---|
| C-1 | 指定当前基线状态与权威来源 | Owner | 出具 OD（Owner Decision），明确 `FROZEN` 当前取值与唯一权威来源文件 |
| C-2 | 发布 V2.0 受控输入索引 | MAIN/Owner | 在 `specs/BASELINE_INDEX.yaml`（或等价受控索引）登记 V2.0 业务需求基线与 `PB-V2.0-R1`，附文件与 sha256/签署证据 |
| C-3 | 声明 V1.0 历史地位 | MAIN/Owner | 明确 `PRODUCT-BASELINE-V1.0.md` 仅历史参考；M19=DEFERRED 旧结论声明失效、不得回流 |
| C-4 | 消除 README vs STATUS.md 状态冲突 | GITS/MAIN（经 Owner 批准） | README 状态块与 STATUS.md 字段名+取值收敛一致（或 README 改为指针） |
| C-5 | 冻结状态与产品基线状态分述 | Owner | 区分「工程交付冻结（V1.0）」与「产品基线（V2.0 `APPROVED_WITHOUT_FREEZE`）」，不在单一 `FROZEN` 字段混义 |

**未关闭前**：本仓库不得将 V2.0 基线、产品基线状态、或 `FROZEN` 任一字段用于宣布「已冻结 / 已实施 / 已联调 / 生产就绪」。

---

## 5. 纪律、边界与工作树隔离（WP0-1 自证）

- 交付物状态：`CANDIDATE / FROZEN=NO / IMPLEMENTED=NO`（本文件头部已声明）。
- WP0-1 交付物**仅新增本文件**；不改动 `specs/BASELINE_INDEX.yaml`、`README.md`、`docs/governance/STATUS.md`、`docs/baseline/PRODUCT-BASELINE-V1.0.md` 等任何受控/既有文件；未写入 `generated/`，未补写 V2.0 索引文件。
- **工作树隔离（本次修复）**：取证时工作树存在与本任务无关的未提交变更（属 step 3 及其他在途任务），为满足「仅新增本文件」的隔离要求，已按 Tech Lead 意见执行并自证：
  1. **还原被误删文件** `git checkout -- docs/dd/`：恢复 11 个被误删的历史设计/证据文件（含 `BASELINE_INDEX.yaml` 引用的 `GITS_Bank_UX功能重构_全周期施工与最终交付规划_V1.0_20260825.zip` 权威文件）。
  2. **暂存他任务未提交工作** `git stash push -u`：将 step 3 已落地 SDD 契约的未提交改动（`specs/CONTRACT_INDEX.yaml` 的 7 条 `CTR-PR-*` 登记、`specs/knowledge-architecture/skills/SP-15.json`）及无关未跟踪文件（`specs/product-recommendation/`、`AC-PRODUCT-RECOMMEND-001.json`、`product-recommendation.openapi.json`、`V020__product_recommendation.sql`、`docs/adr/ADR-PR-CANDIDATES.md`、`docs/*.pdf/.pptx`）整体暂存到 `stash@{0}`，**保留不销毁、可 `git stash pop` 复原**。
  3. **复验**：`git status -s` 在上述动作后为空；新增本文件后应仅剩 `?? docs/governance/WP0_BASELINE_STATUS_CANDIDATE.md` 一行。
- **修正说明**：前一版本文件曾声称「未改动 `specs/CONTRACT_INDEX.yaml`」，但当时该文件在工作树中实为 `M`（+72 行），陈述与仓库事实不符。本版改为如实记录取证时的工作树状态与本任务执行的隔离动作，不再作与仓库事实相悖的声明。

## 6. 版本记录（本候选）

| 版本 | 日期 | 说明 | 作者 |
|---|---|---|---|
| CANDIDATE | 2026-08-31 | 取证 + V2.0 受控输入索引候选 + V1.0 历史地位 + STATUS_SOURCE_CONFLICT + 关闭条件 + 工作树隔离自证 | GITS/MAIN (WP0-1) |
