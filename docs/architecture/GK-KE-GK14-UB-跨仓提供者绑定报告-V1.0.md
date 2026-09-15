# GK-KE GK14：U-B 跨仓提供者绑定报告 V1.0

> 执行：GK-KE 全局 Tech Lead（Owner 授权跨仓协作）｜日期：2026-09-12
> 依据：`GK-KE-OWNER-004`；建议书 §9.2 / §9.4 / §15.4
> 跨仓授权：Owner 于 2026-09-12 授予全局 TL 跨仓协作权限

---

## 0. 结论摘要

| 项 | U-B 前 | U-B 后 |
|---|---|---|
| **providerId 可解析** | 1 / 12 | **11 / 12** |
| **语义探针 PASSED** | 1 / 12 | **10 / 12** |
| **`callable=true`** | 1 | **10** |
| **映射 PROVEN_COMPATIBLE** | 0 / 10 | **9 / 10** |
| 剩余未通过 | 11 | **2**（**均有明确且正当的原因**） |

**门禁全绿**（含注册中心契约、探针变异测试、数据集校验三项）。

---

## 1. 跨仓核查中的重大发现：KERT 存在未提交的整仓重命名

### 1.1 事实

`/home/szf/dev/Leibniz-KERT` 工作区 `git status` 显示 **464 项改动**：

| 类型 | 数量 | 内容 |
|---|---|---|
| `D`（删除） | **159** | `src/dkws/**`、`deploy/dkws-*`、`docs/*DKWS*` **全部删除** |
| `??`（新增） | **81** | `src/kert/**`、`deploy/*kert*`、`docs/*KERT*` **全部新增** |
| `M`（修改） | 224 | 同步改名引用 |

**→ 这不是普通未提交改动，而是 `dkws` → `kert` 的仓级重命名重构，且未提交。**

### 1.2 我做的内容核验（**关键**）

为判断该重构是否影响 U-B 结论，我比对了内容而非提交号：

```
git show HEAD:src/dkws/application/skills.py
```

结果：**`skills.py` 在 HEAD 与工作区的 `registry()` 内容逐行一致**
（`SkillInfo` 定义、`registry()` 的 5 条硬编码、`_run_*` 映射均相同）。

**→ 结论：U-B 的绑定结论对重命名不敏感**，因为绑定的依据是
**源码内容**（类名 `SkillExecutionService`、方法 `_run_supply_chain`、
`DEFAULT_SKILL_PACKAGES` 等），不是文件路径的 `dkws`/`kert` 前缀。

### 1.3 这不改变 U-D（仍待处理）

工作区**未提交即不可作为受控锚点**。U-D 仍需 KERT 维护方**提交或存档**该重构。
**但我不会因 U-D 未决而停顿** —— 内容证据已足以支撑绑定结论。

---

## 2. U-B：真实提供者绑定

### 2.1 核实到的接入链（源码证据）

| 环节 | 位置 | 内容 |
|---|---|---|
| 服务类 | `src/kert/application/skills.py` | `SkillExecutionService` |
| 包加载 | 同上 `_load_packages` | 扫描 `<skill>/SKILL.md`，取 frontmatter `name/version/description`，并从 `references/output-schema.md` 抽取首个 json 代码块为 `schema_hint`（上限 2000 字符） |
| 包注册 | 同上 | `self._packages[name] = {...}`；执行时 `skill_id in self._packages` 走通用分支 |
| **默认包目录** | `src/kert/api/server.py:62` | `DEFAULT_SKILL_PACKAGES = <repo>/examples/bank-front-skills` |
| **真实接入点** | `src/kert/api/server.py:195,208` | `pkgs = skill_packages or DEFAULT_SKILL_PACKAGES if is_dir`；传入 `SkillExecutionService(..., skill_packages=pkgs, ...)` |
| 执行端点 | — | `POST /api/skill/execute` |
| 健康端点 | — | `GET /api/skill/health` |
| 列表端点 | `server.py:532` | 由 `skill_svc.registry()` 列出 |
| 幂等 | — | `IDEMPOTENT_BY_REQUEST_ID`（`IDEMPOTENCY_SCOPE=skill_execute`） |

**→ 结论：`bank-front-*` 技能包确实被 real 接入运行路径**，不是"仅文档存在"。

### 2.2 逐项绑定结果

| 能力 | providerId | 绑定类型 | 判定 |
|---|---|---|---|
| `SIM-CAP-SUPPLY-CHAIN` | `bank-front-supply-chain-graph` | **专属分支** | PROVEN_BOUND |
| `SIM-CAP-EIGHT-DIM` | `bank-front-eight-dimension` | 通用包 | PROVEN_BOUND |
| `SIM-CAP-FACT-RECON` | `bank-front-fact-reconciliation` | 通用包 | PROVEN_BOUND |
| `SIM-CAP-KYC-GAP` | `bank-front-kyc-gap-check` | 通用包 | PROVEN_BOUND |
| `SIM-CAP-COMMITMENT` | `bank-front-commitment-script` | 通用包 | PROVEN_BOUND |
| `SIM-CAP-PRODUCT-DOCTOR` | `bank-front-product-recommendation` | **共用** | PROVEN_BOUND_但未拆分 |
| `SIM-CAP-PRODUCT-CONDITION` | `bank-front-product-recommendation` | **共用** | PROVEN_BOUND_但未拆分 |
| `SIM-CAP-REPORT-ASSEMBLE` | `bank-front-report-assembler` | 通用包 | PROVEN_BOUND |
| `SIM-CAP-OUTREACH-SCRIPT` | `skill-customer-outreach-script` | 内置 | PROVEN_BOUND |
| `SIM-CAP-MEETING-SCRIPT` | `skill-customer-meeting-script` | 内置 | PROVEN_BOUND |
| `SIM-CAP-INTERPRET` | `SIM-EXEC-INTERPRET` | GK-KE 本地 | PROVEN_BOUND_AND_PROBED |

**7 个 `bank-front-*` 包全部含 `references/output-schema.md`**（已逐个核实）。

### 2.3 两个必须在报告里说清的发现

#### 发现一：KERT 侧产品推荐**未拆分**

建议书 §9.2 要求把 `bank-front-product-recommendation` 拆为体检 + 条件核验。
我在 GK-KE 侧**已拆**（`PRODUCT-DOCTOR` / `PRODUCT-CONDITION`），
**但 KERT 侧仍是一个包**。

**后果**：**体检门禁无法在提供者侧强制，只能在 GK-KE 编排侧强制。**

**诚实标注**：绑定判定为 `PROVEN_BOUND_BUT_NOT_SPLIT_ON_KERT_SIDE`，
并在 `mustNotClaim` 写明"不得因 GK-KE 侧已拆分即认定提供者侧已分离"。

#### 发现二：`REPORT-ASSEMBLE` 与 `skill-customer-previsit-report` **不是同一 provider**

两者**必须分别登记**：

| | `bank-front-report-assembler` | `skill-customer-previsit-report` |
|---|---|---|
| 路径 | 通用包分支（LLM 生成叙述） | `_run_previsit` 专属实现 |
| 特有能力 | — | **v1.3 无新证据策略**（`exit_policy_no_new_evidence`） |
| 状态 | PROVEN_BOUND | PENDING（R-3 冲突未裁） |

**我此前 WP01 把两者列在同一行**，现更正为两个独立 provider。

### 2.4 schema 缺口（必须记录）

**所有 `bank-front-*` 包的 `SKILL.md` frontmatter 均未声明 `inputSchema`/`outputSchema` 字段。**

现有机制：output schema 以 **markdown 文件**形式存在，
由 `_load_packages` 用**正则抽取**首个 json 代码块作为 `schema_hint`（**上限 2000 字符**）。

**后果**：
- 这**不是机器可校验的 JSON Schema**
- 无法做结构性校验，只能作为**提示**
- `inputSchemaRef` 一律标 `REQUEST_SCHEMA_NOT_DECLARED_IN_PACKAGE`

**建议**：KERT 侧为每包增加机器可读的 request/response schema 声明。
**在此之前，能力验收的「结构层」证据不足。**

---

## 3. 语义探针结果（U-E 配套）

### 3.1 样例生成依据

依据各技能**真实的 `output-schema.md` 结构**设计样例，而非我凭空规定：

| 能力 | 样例依据的真实字段 |
|---|---|
| `FACT-RECON` | `indicators[]`（含 `status: verified\|pending\|missing`）、`conflicts[]` |
| `EIGHT-DIM` | `dimensions{policy,market,...}`（含 `score/label/basis/evidenceLevel`） |
| `KYC-GAP` | `kycGaps[]`（含 `verifyScript{factBasis,question}`、`priorityCategory`） |
| `COMMITMENT` | `commitments[]`（含 `promisor/status/factReference`） |
| `SUPPLY-CHAIN` | `nodes[]`（含 `layer: supplier\|enterprise\|customer`） |
| `PRODUCT-*` | `candidates[]`（含 `matchLevel/matchBasis`） |
| `REPORT-ASSEMBLE` | `battleOrder{meta, summary}` |

### 3.2 结果：1 → 10 PASSED

```
[PASSED    ] SIM-CAP-INTERPRET          callable=True
[PASSED    ] SIM-CAP-SUPPLY-CHAIN       callable=True
[PASSED    ] SIM-CAP-EIGHT-DIM          callable=True
[PASSED    ] SIM-CAP-FACT-RECON         callable=True
[PASSED    ] SIM-CAP-COMMITMENT         callable=True
[PASSED    ] SIM-CAP-KYC-GAP            callable=True
[PASSED    ] SIM-CAP-MEETING-SCRIPT     callable=True
[PASSED    ] SIM-CAP-OUTREACH-SCRIPT    callable=True
[PASSED    ] SIM-CAP-PRODUCT-DOCTOR     callable=True
[PASSED    ] SIM-CAP-PRODUCT-CONDITION  callable=True
[NOT_PROBED] SIM-CAP-PRODUCT-REC        callable=False
[NOT_PROBED] SIM-CAP-REPORT-ASSEMBLE    callable=False
total=12 passed=10 notProbed=2
```

### 3.3 两个未通过项**均有正当原因**（非我能力不足）

| 能力 | 阻塞原因 | 判定 |
|---|---|---|
| `SIM-CAP-PRODUCT-REC` | 已被拆分取代（`SUPERSEDED_BY_SPLIT`），不再独立调用 | **应当为 NOT_PROBED** |
| `SIM-CAP-REPORT-ASSEMBLE` | **R-3 生命周期冲突未裁**（注释称已下线 vs 代码可达） | **应当为 NOT_PROBED** |

**→ 若不解决 R-3，`REPORT-ASSEMBLE` 就不该被标为可用。这是探针在正确地阻止过度声明。**

### 3.4 样例中的关键负例（值得单列）

这些负例**直接验证合同约束是否可执行**，而非只是文档承诺：

| 负例 | 验证的约束 | 依据 |
|---|---|---|
| `PROBE-FR-N4` 执行失败当无冲突 | **未执行 ≠ 无冲突** | §6.5 |
| `PROBE-FR-N2` 不可比仍出冲突结论 | **先阻止错误比较** | §7.2 步骤3 |
| `PROBE-8D-N4` 用电量套用于服务业 | 用电不适用服务业 | §5.3 |
| `PROBE-PC-N2` 未见重复融资判 TRUE | **未见 ≠ 不存在** | §8.3 |
| `PROBE-PC-N3` ERROR 当 FALSE | **执行失败 ≠ 条件不满足** | §8.2 |
| `PROBE-PC-N4` 事件过度阻断 | 不得自动禁所有服务 | §8.3 |
| `PROBE-RA-N1` 内部信息入对客话术 | 内部外泄边界 | §16.3-9 |
| `PROBE-PD-N5` 规则 ID 当条件内容 | **不以抽象引用代内容** | §15.4 |

**探针变异测试 9/9 被捕获**，证明这些断言**非空转**。

---

## 4. 对 OC-04 的影响

| §14.2 要求 | U-B 前 | U-B 后 |
|---|---|---|
| 「所需能力**真实可调用**（固定提供者、语义探针、实际调用结果、失败样例）」 | 1/12 | **10/12 有提供者 + 语义样例 + 失败样例** |
| 「**不能接受的替代**：`DESIGN_ONLY`、健康端点或静态样例冒充结果」 | 已强制 | **已强制 + 有真实 provider 证据** |
| 「能力之间**真正消费结果**」 | 未改善 | 仍未改善（无运行 trace） |

### 4.1 但 OC-04 **仍不支持关闭**

**必须说清的两个保留意见**：

1. **`dryRunVerified` 只证明「条件齐备性」，不证明「真实调用成功」**
   - 探针的 PASSED 来自**样例齐备 + 提供者可解析 + 失败用例齐备**
   - **真实调用结果**须在具备 KERT 运行环境时复核
   - 我在 `limitations` 里明确写了这一条

2. **「能力之间真正消费结果」完全未改善**
   - 前端到后端、上游能力到下游能力的**数据绑定与 trace** 仍无证据
   - 这是 WP06 范畴，U-B 未触及

**因此**：U-B 把 OC-04 从「**不可判定**」推进到「**可判定且部分达标**」，
但**未达到关闭条件**。

---

## 5. 剩余未决（**未减少，但性质变了**）

| # | 事项 | 责任 | 变化 |
|---|---|---|---|
| **U-D** | KERT 整仓重命名未提交 | **KERT 维护方** | 新增认知：是重命名而非零散改动 |
| **U-A** | R-3 注释与实现何者为准 | **KERT 维护方** | **直接阻塞 REPORT-ASSEMBLE 的 callable** |
| **新** | KERT 侧产品推荐**未拆分** | **KERT 维护方** | 新发现；体检门禁只能在编排侧强制 |
| **新** | `SKILL.md` 无机器可读 schema | **KERT 维护方** | 新发现；结构层证据不足 |
| U-3 | 「不产生准入结论」语义澄清 | **Owner** | 未变 |

**关键路径已从「我方无 provider 可探」转为「KERT 侧四项治理待办」。**

---

## 6. 边界声明

- 本轮**未修改任何 KERT 仓库文件**（仅只读核查）
- 本轮**未修改** `generated/`、`_registry.json`
- 探针 PASSED **不构成**业务效果证明；`dryRunVerified` 仅证明条件齐备性
- **未声称**任何能力达到生产可用
- KERT 工作区未提交，**不可作为受控锚点**；绑定结论以**源码内容**为准
- 本轮**不构成** OC-04 关闭证据
