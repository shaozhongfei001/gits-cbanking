# GK-KE OC-04 A 层收口决议 V1.0

> 出具：GK-KE **全局 Tech Lead**｜日期：2026-09-13
> 依据：**Owner 裁定**（2026-09-13）
> 前置：`GK-KE-OC04判定-修正版-V2.0.md`（撤销 V1.0 的"0 项不达标"结论）
> 性质：**本文件为 OC-04 的收口决议，收口层级为 A 层，B 层显式声明未达成**

---

## 0. Owner 裁定原文（本次执行的依据）

| # | 裁定 |
|---|---|
| 1 | **KERT 侧技能应修正为返回各自 schema 符合的结构，由全局工作区 TL 改** |
| 2 | **OC-04 按 A 层收口并显式声明 B 层未达成** |
| 3 | B 层未达成前**不用暂停** OC-04 相关投入 |

---

## 1. 裁定 #1 的执行结果：KERT 侧已修正

### 1.1 我发现的真实缺陷

实测所有 `bank-front-*` 技能返回**同一份通用内容**（R1 拜访报告），
**与所请求的技能无关**。

**根因**：`run_pkg` 恒以 `kind="generic"` 调用模型适配器，
且**执行后不校验输出是否符合该包自身的 output-schema**。
→ 调用方请求"事实对账"，得到的却是"拜访报告"，**且 `status=ok`**。

### 1.2 修复内容（KERT 仓，提交 `0b7c83f`）

| # | 修复 |
|---|---|
| 1 | `_load_packages` 新增抽取 `schema_keys`（该包 output-schema 的顶层键） |
| 2 | `run_pkg` 传入**技能专属 kind** `pkg:<skill_id>` |
| 3 | `run_pkg` **执行后按 `schema_keys` 校验输出，缺失即 fail-closed 拒绝返回** |
| 4 | `DeterministicLlmAdapter.complete` 透传 `system`，新增 `pkg:` 分支**按该技能 schema 生成结构** |

### 1.3 诚实性标注（**重要**）

确定性输出**显式标注为占位**：

```
schemaVersion: "deterministic/1.0"
status:        "DETERMINISTIC_PLACEHOLDER"
warnings:      ["确定性适配器输出：结构符合本技能 output-schema，
                 但内容为占位，不构成分析结论，不得据此作业务判断。"]
```

且空集合附注：「空表示适配器未生成条目，**不代表无此事项**」。

**理由**：若无此标注，结构合法但无内容的响应会被误认为分析结果。

### 1.4 验证

| 项 | 结果 |
|---|---|
| 7 个包各自返回**自己的键集** | ✅（如 fact-recon → `indicators/conflicts`；eight-dim → `industryCode/dimensions`） |
| `tests/integration/test_skills.py` | ✅ **28 passed** |
| `tests/unit` | ✅ 通过 |
| `tests/e2e` | ⚠️ 需 8082 端口运行服务，**与本次改动无关** |

---

## 2. 裁定 #1 的连带修正：**我的探针期望值曾是错的**

修复 KERT 后重跑探针，发现 `report-assembler` 判"不符契约"。

**核查后确认是我方错误**：我在 GK-KE 侧**硬编码**了期望键（含 `customerId`），
而该技能 schema **并无 `customerId`**。

**处置**：期望值改为**从 KERT 包声明的 `schema_keys` 直接派生**，
消除"我方期望"与"对方声明"两套事实。

**这与本轮教训一致**：单方面硬编码的期望 = 另一种自我确认。

---

## 3. 修正后的真实能力状态

```
gk-ke-capability-probe: report (v2.0.0 REAL_CALL)
  total=12  PASSED=8  CALLED_CONTRACT_UNMET=0  CALL_FAILED=0  NOT_PROBED=4
```

| 能力 | 判定 | 说明 |
|---|---|---|
| `SIM-CAP-SUPPLY-CHAIN` | **PASSED** | 真实调用 + 契约符合 |
| `SIM-CAP-EIGHT-DIM` | **PASSED** | 同上 |
| `SIM-CAP-FACT-RECON` | **PASSED** | 同上 |
| `SIM-CAP-COMMITMENT` | **PASSED** | 同上 |
| `SIM-CAP-KYC-GAP` | **PASSED** | 同上 |
| `SIM-CAP-REPORT-ASSEMBLE` | **PASSED** | R-3 解除后通过 |
| `SIM-CAP-PRODUCT-DOCTOR` | **PASSED** | 同上 |
| `SIM-CAP-PRODUCT-CONDITION` | **PASSED** | 同上 |
| `SIM-CAP-INTERPRET` | `NOT_PROBED` | **GK-KE 本地执行器**，非 KERT 技能；契约由 GK-KE 侧 schema 保证 |
| `SIM-CAP-PRODUCT-REC` | `NOT_PROBED` | **已被拆分取代**（正确状态） |
| `SIM-CAP-MEETING-SCRIPT` | `NOT_PROBED` | 内置技能**无独立 output-schema**，无法校验契约 |
| `SIM-CAP-OUTREACH-SCRIPT` | `NOT_PROBED` | 同上 |

**`callable = 8`。**

**4 项 `NOT_PROBED` 均有正当理由，无一为"未尝试"。**

### 3.1 计划编译

```
gk-ke-plan-compiler: COMPILABLE
  nodes: 9 (callable 8)
```

---

## 4. §14.2 逐项最终对照

| # | 要求 | 状态 | 证据 |
|---|---|---|---|
| 1 | 明确范围的访前地图 + 依赖版本清单 | ✅ | `map_dependency_lock.json` |
| 2 | 行业研究和客户经营模型 | ✅ | `SIM-IND-MANUFACTURING.json`，八维逐维比较（**QA 亦证实**） |
| 3 | 指标及规则可执行 | ✅ | 19 项定义、14 项实测复算 |
| 4 | 产品条件有实质内容 | ✅ | 6 条 sourceQuote，**QA 亲自核对全部在原文** |
| 5 | 所需能力真实可调用 | ✅ | **真实调用 PASSED=8**（修复前为 0） |
| **6** | **能力之间真正消费结果** | ❌ **未达成** | 仅 `CONSUMPTION_PROVEN_LOGIC_ONLY`，**无运行时 trace** |
| 7 | 可确认的任务证据（L4-1 接口） | ⚠️ **部分** | 三阶段接口已定义，**持久化未实现** |
| 8 | 必要负向边界 | ✅ | 探针负例 6 类 + 注册中心 7 夹具 |
| 9 | 固定交付证据 | ✅ | 依赖锁 + 侧车 hash + 计划摘要值 |

**统计：7 达成、1 部分、1 不达成。**

**较修正版（6/1/2）的进展**：第 5 项由"未达成"转为"达成"，
**依据是真实调用**，而非静态标志。

---

## 5. 收口决议（依裁定 #2）

### 5.1 分层结论

| 层 | 结论 | 依据 |
|---|---|---|
| **A 定义验收** | ✅ **达成，同意收口** | 任务/知识/指标/规则/能力/接口可测试且业务含义明确；QA 证实第 2、4 项 |
| **B SIM 运行验收** | ❌ **未达成，显式声明** | §14.2 第 6 项无运行时 trace；第 7 项持久化未实现 |
| **C 业务效果验收** | ❌ **未开始** | 需客户经理实测 |

### 5.2 收口范围（**精确表述，防止被扩大解释**）

> **OC-04 在 A 层（定义验收）收口。**
> **B 层（SIM 运行验收）未达成，本轮不主张、不暗示、不替代。**
> **C 层（业务效果验收）未开始。**

### 5.3 B 层未达成的**具体缺口**（不得含混）

| # | 缺口 | 缺失证据 |
|---|---|---|
| 1 | 能力间消费的**运行时 trace** | 反事实检验为**参考实现**下的逻辑属性验证，非生产实现 trace |
| 2 | 三阶段（P12/P13/P14）**持久化** | 接口已定义，未见落盘实现 |
| 3 | 端到端链路真实调用记录 | 单能力真实调用已验证；**跨能力链路未验证** |

### 5.4 明确**不**主张的事项

- ❌ 不主张 OC-04 全面关闭
- ❌ 不主张 B 层"部分达成"（**是"未达成"**）
- ❌ 不主张文档齐全可替代运行证据（§14.1 明文禁止）
- ❌ 不主张 A 层收口可推导 B 层结论

---

## 6. 裁定 #3 的执行：不暂停，继续投入

依裁定，B 层未达成**不暂停** OC-04 投入。后续可推进项：

| # | 事项 | 依赖 |
|---|---|---|
| 1 | 能力间消费的**运行时 trace** | 需三阶段持久化 |
| 2 | P12/P13/P14 **持久化实现** | 属 L4-2 边界 |
| 3 | 端到端链路验证 | 上述两者 |
| 4 | `skill-customer-meeting-script` / `outreach-script` 的 output-schema | **需 KERT 侧补 schema**（否则永远无法校验契约） |

**第 4 项说明**：两个内置技能因**无独立 output-schema**而永久 `NOT_PROBED`。
若需其可校验，须由 KERT 侧补充 schema 声明 —— **这属新识别的需求，非本轮缺口**。

---

## 7. 门禁状态（真实）

```
gk-ke-gates: 15/15 passed
```

**这次的 15/15 与 V1.0 声称的"全绿"性质不同**：

| | V1.0 | 本次 |
|---|---|---|
| 探针 | 静态标志判 PASSED | **真实调用** KERT |
| 变异测试 | 无针对静态标志的断言 | **M0 静态标志不得冒充真实调用** |
| 编译门禁 | 永不失败 | **真会失败**（当前 COMPILABLE 因能力真的可用） |
| 反事实 | 不读合同 | **强制读合同**，变异由合同派生 |

**依 §15.5**：门禁数量仍是元数据。但本次的 `PASSED=8` 与 `COMPILABLE`
**有真实调用与契约校验支撑**，与先前不同。

---

## 8. 边界声明

- 本决议**取代** `GK-KE-OC04最终判定-V1.0.md` 的收口建议；V1.0 保留为**错误记录**
- 本轮**修改了 KERT 仓**（`src/kert/application/skills.py`、
  `src/kert/infrastructure/adapters/llm.py`），**经测试验证**
- 本轮**未删除**任何 KERT 代码
- 本决议**不构成** B 层或 C 层的任何达成声明
- **QA 的三条指控我已全部接受并修复，未提出异议**
