# GK-KE WP01：三仓锚点、旧新对象及 ID 映射对照表 V1.0

> 执行：GK-KE Tech Lead（WP01 责任方）｜日期：2026-09-12
> 依据：GITS–KERT 建议书 V2.0 §9.2 / §15.4（已获 `GK-KE-OWNER-004` 批准为 Owner 决定）
> §9.2 原文要求：`legacyId → canonicalCapabilityId → providerId → version → endpoint → schema`
> §9.2 原文禁止：「文档存在、包可以加载、代码有同名字符串，**都不是实际语义兼容的充分证据**」

---

## 1. 三仓锚点（已锁定）

| 仓 | 路径 | 锚点 | 状态 |
|---|---|---|---|
| **GK-KE** | `/home/szf/dev/gits-cbanking` | `5c91ec348e8a74d81ed80a09cb49a76373b15fde` | 分支 `feature/GK-KE-L0-contract` |
| **KERT** | `/home/szf/dev/Leibniz-KERT` | `3b6640b993f4834d36833fa0bc3005d73768b594` | **工作区大量未提交改动** |
| **建议书** | `docs/architecture/GITS-KERT_…建议书_V2.0.md` | SHA-256 `2553e816e2c33a9fb1d07a1d16141807fa0a6a69e66164f20b344c76a21fc8df` | 已入库 |

### 1.1 KERT 锚点风险（必须记录）

`Leibniz-KERT` 工作区 `git status` 显示**大量 `M`（modified）**，含
`.github/workflows/ci.yml`、`ADR.md`、`.gitignore` 等。

→ **结论**：KERT 当前**工作区不可作为受控锚点**。
本文所有 KERT 侧事实均取自**只读读取**，并标注其为「工作区状态」而非「提交状态」。
**在 WP05 消费前，必须先固定 KERT 提交基线或确认工作区差异已被批准。**

---

## 2. 文档侧：7 个技能的真实身份（已核实）

`/home/szf/dev/Leibniz-KERT/examples/bank-front-skills/` 下 7 个目录，
每个含 `SKILL.md` + `references/` + `assets/`。

**重要发现**：每个 SKILL.md 的 frontmatter 含**正式技能编号 `SK-FRONT-00x`**，
且**与目录名编号不一致**（例如 `bank-front-commitment-script` 是 `SK-FRONT-005`，
`bank-front-report-assembler` 是 `SK-FRONT-001`）。**不得按目录名顺序推定编号。**

| 目录名（legacyId） | frontmatter `name` | **正式编号** | display_name | version | 绑定知识/数据 | 输出规范 |
|---|---|---|---|---|---|---|
| `bank-front-supply-chain-graph` | 同目录名 | **SK-FRONT-002** | 供应链图谱分析 | v1.0.0 | T-CORE-001 + T-EXT-001 | SK-FRONT-002 输出规范（nodes+edges+interpretation） |
| `bank-front-eight-dimension` | 同目录名 | **SK-FRONT-003** | 八维研判 | v1.0.0 | **T-MARKET-001 市场慧眼** | 八维评分+综合结论 |
| `bank-front-fact-reconciliation` | 同目录名 | **SK-FRONT-004** | 事实对账与冲突检测 | v1.0.0 | 行内变动指标 + 外部工商产业 | 指标列表+冲突清单（含"待核实"） |
| `bank-front-commitment-script` | 同目录名 | **SK-FRONT-005** | 承诺话术生成 | v1.0.0 | 历史沟通记录 | 承诺事项卡片 |
| `bank-front-kyc-gap-check` | 同目录名 | **SK-FRONT-006** | KYC 缺口核验 | v1.0.0 | 事实对账冲突/行业信号 | KYC 缺口卡片 |
| `bank-front-product-recommendation` | 同目录名 | **SK-FRONT-007** | 产品组合推荐 | v1.0.0 | KYC 痛点+沟通记录+市场慧眼 | **SK-FRONT-007 输出规范** |
| `bank-front-report-assembler` | 同目录名 | **SK-FRONT-001** | 访前报告组装 | v1.0.0 | 七模块汇总 | KI-FRONT-007 渲染模板 |

**共同属性**（7 个全部一致）：`author: yang.yuan@gientech.com`、
`department: BFSI1_BUSS-BFSI1_BUSS_R&D`、`version: v1.0.0`、`usage_scope: 仅云端使用`。

**可调用性事实**：`SKILL.md` frontmatter **未含** `endpoint`、`inputSchema`、`outputSchema` 字段。
输出规范以**独立 md 文档**形式存在于 `references/output-schema.md`（须逐个核实是否存在）。

---

## 3. 代码侧：实际注册的 Skill（已核实）

来源：`/home/szf/dev/Leibniz-KERT/src/kert/application/skills.py`（工作区状态）

`SkillExecutionService.registry()` 硬编码（第 167–171 行）：

| skillId | 名称 | version | 说明 |
|---|---|---|---|
| `skill-customer-outreach-script` | 外联脚本 | `1.0.0` | |
| `skill-customer-meeting-script` | 会面脚本 | `1.0.0` | |
| `skill-customer-previsit-report` | R1 拜访报告 | `1.0.0` | 文件注释称 **2026-08-21 已下线移除**，但**仍在 registry 中** |
| `SP-20` | 对公客户服务建议书生成 | `1.0.0` | |
| `SP-21` | 交互记忆抽取 | `1.0.0` | |

条件注册（第 178–180 行）：
| skillId | 名称 | version | 条件 |
|---|---|---|---|
| `SP-15` | 产品适配与综合方案 | `2.0.0-candidate` | 需工作区 |
| 外部包动态加载 | 取自 `SKILL.md` frontmatter | 默认 `1.0.0` | 传入 `skill_packages` 时 |

**运行时契约**（第 6 行注释 + 第 34 行）：
- 统一执行契约：`requestId / status(ok|skill_error) / data / assemblyTrace / modelCalls`
- HTTP 端点：`POST /api/skill/execute`、`GET /api/skill/health`（由 `api/server.py` 暴露）
- 幂等作用域：`skill_execute`
- 技能资产目录：`skills/customer-engagement/`
- 外部包加载要求：`<skill>/SKILL.md` + `references/output-schema.md`（第 151 行）

### 3.1 命名分裂（已证实）

| 侧 | 命名规范 | 例 |
|---|---|---|
| 文档（`examples/bank-front-skills/`） | `bank-front-*` + 正式编号 `SK-FRONT-00x` | `bank-front-fact-reconciliation` / `SK-FRONT-004` |
| 代码（`skills.py` registry） | `skill-customer-*` | `skill-customer-outreach-script` |
| 代码（外部包） | 取自 frontmatter `name` | `bank-front-supply-chain-graph`（可加载） |

→ **三套命名并存**。`bank-front-*` 与 `skill-customer-*` **无字符串对应关系**，
**必须建立显式映射，不得推定兼容**。

---

## 4. GK-KE 侧：能力资产（已核实）

### 4.1 设计文件（`specs/knowledge-architecture/capabilities/`，4 个）

| capabilityId | rules | failureBehavior | negatives | `kertSide` |
|---|---|---|---|---|
| `SIM-CAP-EIGHT-DIM` | 3 | 4 | 3 | `DESIGN_ONLY` |
| `SIM-CAP-FACT-RECON` | 4 | 4 | 5 | `DESIGN_ONLY` |
| `SIM-CAP-KYC-GAP` | 5 | 4 | 4 | `DESIGN_ONLY` |
| `SIM-CAP-PRODUCT-REC` | 6 | 6 | 5 | `DESIGN_ONLY` |

### 4.2 注册中心（`specs/knowledge-architecture/registry/Capability.json`）

**仅注册 1 项**：`SIM-CAP-INTERPRET`（`probeStatus: PASSED`，`callable: true`）。

### 4.3 地图引用（`activation/map_spec.json`，`mapId=SIM-MAP-FINANCE` v2.0.0）

- `capabilities.items`（7 项）：`SIM-CAP-SUPPLY-CHAIN`、`SIM-CAP-EIGHT-DIM`、
  `SIM-CAP-FACT-RECON`、`SIM-CAP-COMMITMENT`、`SIM-CAP-KYC-GAP`、
  `SIM-CAP-PRODUCT-REC`、`SIM-CAP-REPORT-ASSEMBLE`
- `capabilities.additionalImplemented`（2 项）：`SIM-CAP-MEETING-SCRIPT`、`SIM-CAP-OUTREACH-SCRIPT`

**关键差异**：地图引用 9 个能力，注册中心仅 1 个，设计文件仅 4 个。
→ **三者不闭合**，此为本 WP 最重要的结构性发现之一。

### 4.4 指标资产

`specs/gk-ke/v1/definitions/` 下**仅 1 项指标**：
`SIM.METRIC.CUSTOMER_AVG_DEPOSIT@1.0.0`，**`status: CANDIDATE`**。
（建议书要求 M01–M30 + I01–I12 共 42 项 → 缺口 41 项）

### 4.5 规则资产

**无独立 RuleSpec 文件**。规则以**内联数组**分散于：
- `activation/map_spec.json`：`SIM-XC-1~4`（4 条交叉验证，**仅方向无阈值**）、
  `SIM-RULE-KYC-VERIFY`、`SIM-RULE-PRODUCT-ADMISSION`
- `capabilities/SIM-CAP-EIGHT-DIM.json`：`SIM-RULE-8D-1~3`
- `capabilities/SIM-CAP-FACT-RECON.json`：`SIM-RULE-FR-1~4`
- `capabilities/SIM-CAP-KYC-GAP.json`：`SIM-RULE-KYC-1~5`
- `capabilities/SIM-CAP-PRODUCT-REC.json`：`SIM-RULE-PR-1~6`
- `closed-loop/closed_loop_run.json`：`SIM-RULE-TERM-12M`、`SIM-RULE-PURPOSE-VERIFY`

### 4.6 产品知识

- `specs/product-knowledge/`（19 文件）：有 schema（evidence-ref/span、field-assertion、
  field-policy、conflict-case、release 等）+ `invariants.py` 校验 + API openapi
- `specs/product-recommendation/`（13 文件）：有 eligibility-result、product-fit-result、
  portfolio-candidate、recommendation-human-decision 等 schema + 4 夹具
- **`ProductCard` 无独立文件**；`specs/gk-ke/v1/definitions/SIM-ASSET-P001.json`
  仅以 `productCardKnowledge` 字段引用

→ **有 schema 无内容**：建议书 §8.1/§8.3 要求的条款原文、条件矩阵、
互斥对象、TRUE/FALSE/UNKNOWN 示例**均缺失**。

---

## 5. 映射表（§9.2 要求的 6 列 + 判定与证据）

**判定取值**：`已证实兼容` / `待核` / `已证实不兼容` / `无对应`

### 5.1 文档侧 7 技能 → GK-KE 能力

| legacyId | canonicalCapabilityId | providerId | version | endpoint | schema | 判定 | 证据 |
|---|---|---|---|---|---|---|---|
| `bank-front-report-assembler`<br>（SK-FRONT-001） | `SIM-CAP-REPORT-ASSEMBLE` | **待核** | `v1.0.0`（文档） | **待核** | KI-FRONT-007 渲染模板 | **待核** | 仅名称语义相近；未见 providerId 绑定 |
| `bank-front-supply-chain-graph`<br>（SK-FRONT-002） | `SIM-CAP-SUPPLY-CHAIN` | **待核** | `v1.0.0` | **待核** | `references/output-schema.md` | **待核** | 建议书 §9.2 要求"对齐关系类型、查询边界、证据和实际提供者" |
| `bank-front-eight-dimension`<br>（SK-FRONT-003） | `SIM-CAP-EIGHT-DIM` | **待核** | `v1.0.0` | **待核** | 八维评分+综合结论 | **待核** | 建议书 §5.2 明确要求"**新建候选版本并逐维比较**"；我方 `KI-FRONT-002` 八维**尚未比对** |
| `bank-front-fact-reconciliation`<br>（SK-FRONT-004） | `SIM-CAP-FACT-RECON` | **待核** | `v1.0.0` | **待核** | 指标列表+冲突清单 | **待核** | 需增加比较前提、信号分类、窗口与规则执行结果 |
| `bank-front-commitment-script`<br>（SK-FRONT-005） | `SIM-CAP-COMMITMENT` | **待核** | `v1.0.0` | **待核** | 承诺事项卡片 | **待核** | 需分开历史承诺/沟通问题/新行动建议 |
| `bank-front-kyc-gap-check`<br>（SK-FRONT-006） | `SIM-CAP-KYC-GAP` | **待核** | `v1.0.0` | **待核** | KYC 缺口卡片 | **待核** | 须避免冒充法定反洗钱 KYC 完成（建议书 §9.2） |
| `bank-front-product-recommendation`<br>（SK-FRONT-007） | **需拆分** → `SIM-CAP-PRODUCT-REC` | **待核** | `v1.0.0` | **待核** | SK-FRONT-007 输出规范 | **待核** | 建议书 §9.2 要求拆为 CAP-06（知识体检）+ CAP-07（条件核验） |

### 5.2 代码侧 skill → GK-KE 能力

| legacyId | canonicalCapabilityId | providerId | version | endpoint | schema | 判定 | 证据 |
|---|---|---|---|---|---|---|---|
| `skill-customer-outreach-script` | `SIM-CAP-OUTREACH-SCRIPT` | **待核** | `1.0.0` | `POST /api/skill/execute` | 统一契约 | **待核** | 仅 registry 字符串；未与 `bank-front-*` 建立对应 |
| `skill-customer-meeting-script` | `SIM-CAP-MEETING-SCRIPT` | **待核** | `1.0.0` | `POST /api/skill/execute` | 统一契约 | **待核** | 同上 |
| `skill-customer-previsit-report` | **待定** | **待核** | `1.0.0` | `POST /api/skill/execute` | 统一契约 | **已证实存在生命周期矛盾** | 注释称 **2026-08-21 已下线**，但**仍在 registry**（第 169 行）——**须确认是否为僵尸注册** |
| `SP-15` | **无对应** | — | `2.0.0-candidate` | 同上 | — | **无对应** | 不在 7 技能范围内 |
| `SP-20` / `SP-21` | **无对应** | — | `1.0.0` | 同上 | — | **无对应** | 不在 7 技能范围内 |

### 5.3 建议书 CAP-01–CAP-10 → GK-KE 现状

| 建议书能力 | GK-KE 现有对应 | providerId | 判定 |
|---|---|---|---|
| CAP-01 客户与事实装配 | **无**（GITS 侧） | **待核** | **无对应** |
| CAP-02 行业研判 | `SIM-CAP-EIGHT-DIM` | 待核 | **待核** |
| CAP-03 供应链与关系 | `SIM-CAP-SUPPLY-CHAIN` | 待核 | **待核** |
| CAP-04 事实对账与信号 | `SIM-CAP-FACT-RECON` | 待核 | **待核** |
| CAP-05 业务信息缺口 | `SIM-CAP-KYC-GAP` | 待核 | **待核** |
| CAP-06 产品解读与知识体检 | **需从 `SIM-CAP-PRODUCT-REC` 拆分** | 待核 | **待核** |
| CAP-07 产品条件与候选 | **需从 `SIM-CAP-PRODUCT-REC` 拆分** | 待核 | **待核** |
| CAP-08 拜访议程与承诺整理 | `SIM-CAP-COMMITMENT` | 待核 | **待核** |
| CAP-09 证据锁定与报告 | `SIM-CAP-REPORT-ASSEMBLE` + `SIM-CAP-INTERPRET` | 待核 | **待核** |
| CAP-10 模拟跟进 | **无**（GITS 侧，归 L4-2） | — | **无对应** |

**结论：无一项达到"已证实兼容"。** 全部为 `待核` 或 `无对应`。

---

## 6. 数据源对照

| 数据源 ID | 含义 | 在文档中出现位置 | GK-KE 侧定义 |
|---|---|---|---|
| `T-CORE-001` | 行内核心系统 | 7 技能 SKILL.md 中 4 处引用 | **待核** |
| `T-EXT-001` | 外部工商/产业数据 | 同上 | **待核** |
| `T-MARKET-001` | 市场慧眼智能体 | `bank-front-eight-dimension`、`bank-front-product-recommendation` | **待核** |

**注意**（建议书 §5.1 末段原文）：
> 「"市场慧眼智能体"一类系统是知识提供者或上游能力，其回答仍须带来源和时间。
> **不能因为来源是另一个 Agent 就视为权威研究结果。**」

→ `T-MARKET-001` **不得**作为无条件的行业事实来源。

---

## 7. 发现的不一致与风险清单

| # | 风险 | 影响 | 严重度 |
|---|---|---|---|
| **R-1** | **能力三者不闭合**：地图引用 9 个 / 注册中心仅 1 个 / 设计文件仅 4 个 | 建议书 §14.2 要求"所需能力真实可调用"**无法达标** | **阻塞** |
| **R-2** | **三套命名并存**（`bank-front-*` / `SK-FRONT-00x` / `skill-customer-*`） | 映射错误将导致调用错能力 | **阻塞** |
| **R-3** | `skill-customer-previsit-report` 注释称已下线但**仍在 registry** | 僵尸注册，可能被误认为可用 | **阻塞** |
| **R-4** | SKILL.md **无 endpoint / inputSchema / outputSchema** 字段 | 无法自动化验证可调用性；输出规范为独立 md，需逐个核实 | 高 |
| **R-5** | 文档编号与目录名不一致（如 `commitment-script`=SK-FRONT-005、`report-assembler`=SK-FRONT-001） | 按目录序推定编号**会出错** | 中 |
| **R-6** | KERT 工作区大量未提交改动 | 锚点不唯一，证据可复现性受损 | 高 |
| **R-7** | 指标仅 1 项（缺口 41 项），且 `CANDIDATE` | 建议书要求"指标及规则可执行"**无法达标** | **阻塞** |
| **R-8** | 无 `ProductCard`，产品条件无实质内容 | 建议书要求"产品条件有实质内容"**无法达标** | **阻塞** |
| **R-9** | 无独立 `RuleSpec`，规则内联且**无阈值/窗口** | 建议书 §7.2 的 13 字段 RuleSpec 无法满足 | **阻塞** |
| **R-10** | `T-MARKET-001` 被当作权威来源使用 | 违反建议书 §5.1 末段 | 中 |

---

## 8. 禁止的推定（本 WP 的核心输出）

以下**一律不得**直接采用，必须经显式核实：

1. **禁止**按名称推定 `bank-front-X` ↔ `SIM-CAP-Y` 兼容
2. **禁止**推定 `skill-customer-*` 与 `bank-front-*` 是同一能力的两个名字
3. **禁止**按目录名顺序推定 `SK-FRONT-00x` 编号
4. **禁止**因 `SKILL.md` 存在即认定技能可调用（建议书 §9.2）
5. **禁止**因 `skills.py` registry 含字符串即认定实现已存在
6. **禁止**因 `SKILL.md` frontmatter 有 `version` 即认定有版本化契约（实际无 endpoint/schema 字段）
7. **禁止**因 `T-MARKET-001` 是"智能体"即视其输出为权威研究结果
8. **禁止**因目录名/字符串**未出现**于本表即认定能力缺失（本表只覆盖已知范围）
9. **禁止**因 `bank-front-supply-chain-graph` 可被包加载即认定多跳图能力已实现
   （建议书 §9.1：「不能声称已经实现多跳图能力」）
10. **禁止**把 `SIM-MAP-FINANCE.json` 中的 `status=VALIDATION` 当作本图自身状态
    （该值属上游 `KM-CORP-RM-PREVISIT@0.1.0`）

---

## 9. WP01 完成度自评（对照建议书 §15.4）

| 要求 | 状态 |
|---|---|
| 一页任务范围 | ✅ 见 `GK-KE-第一批范围与差异表-V1.0.md` §3 |
| 三仓锚点 | ✅ 本文件 §1（含 KERT 风险提示） |
| 旧新对象及消费者对照 | ✅ 本文件 §5（判定全部为 `待核`/`无对应`，**符合"无同名自动兼容"要求**） |
| 既有受保护合同有差异说明 | ⚠️ **部分**：已识别 R-1/R-2/R-3/R-9 共 4 项结构性差异；C01–C08 逐条差异待 Wave 2 |

**WP01 结论**：**完成定义达成**（无"同名自动兼容"；受保护合同差异已说明）。
但**产出的关键结论是"无一项已证实兼容"** —— 这意味着 Wave 3（WP05 能力与地图）
**开工前必须补齐 R-1/R-2/R-3**，否则将违反建议书 §15.4「WP05 必须消费 WP02–WP04 固定版本」的硬门禁。

---

## 10. 边界声明

- 本 WP **未修改**任何 `specs/`、`generated/`、合同或 KERT 文件
- 本文件的 `待核` 判定**不是**负面结论，而是**"证据不足，不得采信"**
- KERT 侧事实取自**工作区**（非提交），其可复现性待 R-6 解决后重核
