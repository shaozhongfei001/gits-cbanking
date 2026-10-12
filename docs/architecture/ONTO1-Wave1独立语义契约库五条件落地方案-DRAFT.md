# ONTO1｜Wave 1 独立语义契约库 · 五条件落地方案（DRAFT）

| 项 | 值 |
|---|---|
| 文档性质 | **DRAFT 方案草案**——候任公共语义 Owner 任职技术准备产出；**待 Owner 签署**后方可作为 Wave 1 执行依据 |
| 对应 WI | 执行计划 §4 `WI-1-1`（申请独立受保护仓库）/ `WI-1-2`（库骨架）/ `WI-1-3`（迁移期安排）；验收 = **ACTIVE 五条件**（委员会裁定 3） |
| 依据 | 设计 `ONTOLOGY-SPLIT-DESIGN-V2.0-REVIEW.md` §3.1/§7；执行计划 `docs/dispatch/ONTO-SPLIT-本体四层落地执行计划-V2.0.md` §4/§5；`ADR-ONTO1-namespace-neutral-iri-DRAFT.md` §3 U-4/§5.4 |
| 前置门禁 | **G-1**（`DESIGN_APPROVED` + WI-A2/A4/A6 + D3 签署）**且** Owner 已任命公共语义 Owner / Integration Contract Owner（当前两者均为 `UNASSIGNED_GAP`） |
| 当前状态 | **未开工**（Wave 1 阻塞中）；本方案只是「开工即可执行」的设计稿，**未创建任何仓库、未发布任何 IRI、未标 `ACTIVE`** |
| 状态词纪律 | 库与制品状态一律 `CANDIDATE`；`ACTIVE` 只能由 G5 五条件核验后由 Owner 记录 |

---

## 0. 边界与前提

### 0.1 本方案**不做**

| # | 不做 | 说明 |
|---|---|---|
| N-1 | 不创建/不申请仓库 | WI-1-1 的「申请」动作需 Owner 权限（组织级），本角色只出方案 |
| N-2 | 不填根域 | `namespaces.json` 根域字段保持空；U-1 未签（见 `ONTO1-命名空间ADR联签意见-DRAFT.md` §1） |
| N-3 | 不标 `ACTIVE` / 不发布公共权威版本 | 五条件全满足前，候选包一律 `CANDIDATE` |
| N-4 | 不拆分本体、不改消费入口 | 属 Wave 2/3 |
| N-5 | 不写 KERT 仓 | 本环境 KERT 只读 |

### 0.2 库的定位（一句话）

> 承载 **L1 企业公共业务语义核心** 的**独立发布单元**：其术语定义、版本线、发布流水线、评审规则**均不隶属** GITS/KERT 任一方；GITS/KERT 仅以**单向钉值消费方**身份引用其版本化制品。

---

## 1. 库命名与命名空间（不含根域）

| 项 | 建议 | 说明 |
|---|---|---|
| 库短名（internal code name） | **建议中性、不含系统名、不含业务线代号**；候选（待 Owner 选）：`semantic-contract`、`public-semantics`、`semantic-core` | **不得**含 `gits`/`kert` 词根（否则与「防单系统私有化」自相矛盾） |
| 库 IRI 命名空间 | `{NS-L1}` / `{NS-L2}` / `{NS-L3}` / `{NS-L4}`（ADR §4 四段式） | 根域待 U-1；**本库自身命名空间 ≠ 库短名**，两者解耦 |
| 库内目录（建议） | `l1/`（本体+Shape+词表）、`rules/`（建模规则）、`schemas/`（L4 对照）、`evidence/`（门禁报告与哈希）、`ci/` | 目录结构不承载权威语义，仅工程组织 |

> **本方案所有 IRI 一律写作 `PENDING:{NS-L1}#…`**；本文件不出现任何具体域名。

---

## 2. 五条件逐条落地方案

> 每条件给出：**目标**｜**落地机制**｜**可核验证据（命令/文件）**｜**失败具名码**｜**变异用例**（证明判据非空转）。

### 条件 ① 独立 Owner / 独立版本线 / 独立访问控制 / 独立发布流水线

| 项 | 内容 |
|---|---|
| 目标 | 库的一切治理与工程要素都不依赖 GITS/KERT 的任一方 |
| 落地机制 | (a) `CODEOWNERS` 中库根与 `l1/**` 的 Owner 为**公共语义 Owner**（具名角色，非团队名）；(b) 独立 `VERSION`（语义化版本 MAJOR.MINOR.PATCH，见 §6）；(c) 独立权限组（读写权仅授予公共语义 Owner + 指定协作者；GITS/KERT 默认**只读消费**）；(d) 独立 CI/发布流水线（见 §5），不触发、不被触发于双仓流水线 |
| 可核验证据 | `CODEOWNERS` 文本 + 权限清单导出 + `VERSION` 文件 + CI 配置文件（独立于双仓） |
| 失败具名码 | `SCC_OWNER_NOT_INDEPENDENT`（库根 Owner 非公共语义 Owner）、`SCC_NO_INDEPENDENT_VERSION`、`SCC_PERMISSION_LEAK`（双仓持有写权而未登记）、`SCC_PIPELINE_COUPLED` |
| 变异用例 | ① 把库根 Owner 改为某系统团队 ⇒ FAIL；② 在 CI 中加入依赖双仓流水线的 job ⇒ FAIL；③ 给消费方授予写权而无登记 ⇒ FAIL；④ 原样 ⇒ PASS |

### 条件 ② GITS / KERT / 数据平台 **三方评审规则**（CODEOWNERS 或等效）

| 项 | 内容 |
|---|---|
| 目标 | 公共层变更不得由任一方单方决定 |
| 落地机制 | 变更分级评审矩阵（见 §7）：`patch` 单签；`minor` 公共语义 Owner + 受影响层 Owner；`major` **三方会签**（GITS / KERT / 数据平台）+ 弃用期；**禁止自审**（提交者不得是唯一批准人）；「等效机制」若不用 `CODEOWNERS`，须提供等效的可审计记录（评审单据 + 签署留痕） |
| 可核验证据 | 评审矩阵文件 + 近 N 次变更的批准人记录（含提交者 vs 批准人可比对） |
| 失败具名码 | `SCC_REVIEW_SINGLE_PARTY`（major 变更仅一方批准）、`SCC_SELF_APPROVAL`（提交者自批）、`SCC_REVIEW_RECORD_MISSING` |
| 变异用例 | ① major 变更只填一方批准 ⇒ FAIL；② 提交者与批准人同一 ⇒ FAIL；③ 删除评审记录 ⇒ FAIL；④ 原样 ⇒ PASS |

### 条件 ③ **零 `kert.*` / GITS 运行代码依赖**

| 项 | 内容 |
|---|---|
| 目标 | 库可被任何一方独立消费；不 import、不依赖、不在构建期拉取任一侧运行代码 |
| 落地机制 | 允许/禁止清单（§4）：允许 = OWL/SHACL/SKOS/JSON Schema/LinkML 源 + 通用 RDF 工具链（rdflib/pyshacl 等开源库）+ 本库脚本；禁止 = `kert.*` 任何模块、GITS Java 模块（`modules/**`、`adapters/**`）、双仓私服构件、双仓生成的中间产物 |
| 可核验证据 | 依赖白名单扫描（`rg` 规则 + 依赖清单比对）+ 构建日志（可离线构建）+ import 图（无指向双仓） |
| 失败具名码 | `SCC_RUNTIME_DEP_ON_KERT`、`SCC_RUNTIME_DEP_ON_GITS`、`SCC_PRIVATE_ARTIFACT_DEP`、`SCC_BUILD_REQUIRES_SIBLING_REPO` |
| 变异用例 | ① 在库脚本中 `import kert.foo` ⇒ FAIL；② 依赖清单引入 GITS 私服 artifact ⇒ FAIL；③ 构建要求先 clone 兄弟仓 ⇒ FAIL；④ 原样 ⇒ PASS |
| 注 | 引用 L2/L4 **制品**（发布包 + 哈希）不属于运行代码依赖 —— 但 L1 库**不得** import 下游层，故实际反向引用亦禁（单向：下游钉上游） |

### 条件 ④ 可**独立构建 / 解析 / 验证 / 发布**

| 项 | 内容 |
|---|---|
| 目标 | 在无 GITS/KERT 参与的环境下，从零完成构建→解析→验证→发布 |
| 落地机制 | 流水线四阶段（§5），每阶段一条命令、可离线执行、结果可哈希；验证阶段对规则给绿/红（**允许红**，WI-1-2 明确） |
| 可核验证据 | 四阶段命令与退出码 + 制品哈希 + 在**干净环境**（无兄弟仓、无网络可选）中的执行记录 |
| 失败具名码 | `SCC_BUILD_FAIL`、`SCC_PARSE_FAIL`、`SCC_VERIFY_NOT_RUN`、`SCC_PUBLISH_WITHOUT_HASH` |
| 变异用例 | ① 删除根域声明外的必需文件（如 `VERSION`）⇒ 构建 FAIL；② 故意注入一处 IRI 白名单违规 ⇒ 验证 RED（不是异常退出）；③ 发布缺哈希 ⇒ FAIL；④ 原样 ⇒ 四阶段全绿 |

### 条件 ⑤ **不随 KERT 发布节奏变更**

| 项 | 内容 |
|---|---|
| 目标 | KERT 的发布事件（或停发）不改变本库的版本号、窗口计时与发布时机 |
| 落地机制 | (a) 库发布**触发条件**仅为本库变更（见 §6.2），明确**不含**「KERT 发布」；(b) U-3 窗口以**契约库发布周期**计量（见联签意见 §2.3）；(c) 库 CI 不订阅双仓 webhook；(d) 两侧消费升级由消费方按弃用期自行排期 |
| 可核验证据 | 触发条件清单 + CI 触发源清单（无跨仓 webhook）+ 版本历史（版本号序列不被打断、不因 KERT 事件跳号） |
| 失败具名码 | `SCC_RELEASE_TRIGGERED_BY_KERT`、`SCC_VERSION_COUPLED_TO_KERT`、`SCC_CI_CROSS_REPO_HOOK` |
| 变异用例 | ① 给 CI 加 KERT webhook 触发 ⇒ FAIL；② 在 CHANGELOG 中写入「与 KERT x.y 同步发布」作为强制规则 ⇒ FAIL；③ 原样 ⇒ PASS |

### 2.6 五条件 → 验收证据对照（供 G5 核验，见 §9）

| 条件 | 证据类型 | 判据 | 记录位置 |
|---|---|---|---|
| ① | 配置/权限/版本文件 | 四要素齐备且主体独立 | `evidence/g5/cond-1/` |
| ② | 评审矩阵 + 批准记录 | 无单方决定、无自审 | `evidence/g5/cond-2/` |
| ③ | 依赖扫描 + 构建日志 | 零运行代码依赖、可离线构建 | `evidence/g5/cond-3/` |
| ④ | 四阶段执行记录 + 哈希 | 干净环境可复现 | `evidence/g5/cond-4/` |
| ⑤ | 触发清单 + 版本历史 | 无跨仓耦合 | `evidence/g5/cond-5/` |

---

## 3. 库骨架文件清单（WI-1-2 落地形态）

| 文件 | 内容要点 | 归属条件 | 状态词 |
|---|---|---|---|
| `README.md` | 库定位、角色声明（本体供应方 / 集成方 / 用户三方角色划分）、`authorityEntity` + `hostingRepo` 双字段说明、**不含根域** | ①③⑤ | `CANDIDATE` |
| `MODELING-RULES.md` | **内部规则 / 参照对齐**名义的 R1~R9 修订版（内容草案见 `ONTO1-L1-建模规则R1-R9修订版-DRAFT.md`） | ②③ | `CANDIDATE` |
| `REFERENCE-ALIGNMENT.md` | 参照对齐矩阵（条款版**待 D1 正式文本**；到手前只留空表与判据栏位）；**禁 `CONFORMANCE` 文件名** | ② | `CANDIDATE` |
| `namespaces.json` | 前缀白名单；**根域字段留空**，待 U-1 签署后填 | ① | `CANDIDATE` |
| `VERSION` | 语义化版本（MAJOR.MINOR.PATCH） | ①⑤ | `CANDIDATE` |
| `CHANGELOG.md` | 变更记录 + 级别（patch/minor/major）+ 兼容性判定依据 | ①② | `CANDIDATE` |
| `PROVENANCE.json` | 逐件 `sha256` + `authorityEntity` + `hostingRepo`（**分列且非同一值**） | ①③④ | `CANDIDATE` |
| `CODEOWNERS`（或等效评审记录模板） | 库根 + `l1/**` = 公共语义 Owner；评审矩阵引用 | ①② | `CANDIDATE` |
| `ci/`（流水线定义） | 四阶段（§5）；触发源仅本库 | ①④⑤ | `CANDIDATE` |
| `l1/` | L1 本体源（Turtle）+ Shape 源 + 词表占位；**Wave 1 可为最小可构建骨架**（不含最终 8 类拆分，拆分属 Wave 2） | ③④ | `CANDIDATE` |

**Wave 1 骨架的「最小可构建」口径建议**：能把上述文件全部解析/校验（允许规则红），并产出 `REFERENCE-ALIGNMENT-REPORT.md`（内容可为「全部未通过 + 原因」）。**骨架 ≠ 权威制品**：Wave 1 结束时 L1 本体仍不发布。

---

## 4. 零依赖边界：允许 / 禁止清单（条件 ③ 判定基准）

| 类别 | 允许 | 禁止 |
|---|---|---|
| 语义源 | OWL 2（Turtle）、SHACL、SKOS、JSON Schema、LinkML | 从双仓抽取的 Java/Python 源文件作为「事实来源」 |
| 工具链 | 通用开源 RDF 校验工具（rdflib / pyshacl / 标准 JSON Schema 校验器）；版本钉在库内 | 双仓私服构件、双仓内部工具包 |
| 数据 | 受控测试夹具（含 `simulationOnly` 标记的 SIM 夹具）、具名负例 | 双仓生产数据库导出、客户真实数据 |
| 脚本 | 库内脚本（构建/校验/碰撞检查/报告生成） | 直接调用 GITS/KERT 服务或 CLI 的脚本 |
| 制品引用 | **下游层**（L2/L4）可以制品+哈希方式钉 L1 版本 | **L1 库反向引用下游层**（方向必须单向） |
| 构建 | 需可离线/可缓存构建 | 需先构建兄弟仓、需访问内网仅双仓可达的资源 |

**检测实现建议**：`scripts/scc_zero_dep_check.py`——① `rg` 规则（`import kert`、`from kert`、`com.gien.gits`、双仓 artifactId、`../Leibniz-KERT` 相对路径）；② 依赖清单白名单比对；③ 构建沙箱（无兄弟仓）试跑。三条任一命中 ⇒ FAIL（fail-closed）。

---

## 5. 独立流水线四阶段（可独立构建 / 解析 / 验证 / 发布）

| 阶段 | 命令（建议） | 产出 | 失败动作 |
|---|---|---|---|
| 1 构建 | `make scc-build` | 制品（Turtle + 导出 + 版本号注入） | FAIL ⇒ 阻断后续 |
| 2 解析 | `make scc-parse` | 解析报告（三元组数/类数/属性数/前缀清单） | FAIL ⇒ 阻断后续 |
| 3 验证 | `make scc-verify` | `REFERENCE-ALIGNMENT-REPORT.md`（R1~R9 逐条绿/红 + 豁免登记）；**允许红**（Wave 1 验收即为此） | 红 ⇒ 不阻断 Wave 1，但阻断发布 |
| 4 发布 | `make scc-release` | 内容寻址包（manifest + 逐件 `sha256`）+ `PROVENANCE.json` 更新 + 版本 tag | 任一哈希不一致 ⇒ **具名漂移拒绝**，不发布 |

**发布门（硬）**：条件 ①②③④⑤ 的证据齐备 + 验证阶段非红 + `authorityEntity`/`hostingRepo` 已填且非混同 + 根域已签（U-1）。**根域未签 ⇒ 发布门永不开（Stage 4 禁跑）**。

**Wave 1 结束时的可交付**：阶段 1~3 可跑（阶段 3 允许红）、阶段 4 未执行（无根域）——这与 WI-1-2 的「`make conformance` 可跑（允许红）」一致。

---

## 6. 独立版本线（条件 ①⑤）

### 6.1 版本号规则

`MAJOR.MINOR.PATCH`，与复审包 `07-兼容性矩阵-major-minor-patch.md` 对齐：

- `PATCH`：注释/标签/示例完善；
- `MINOR`：只增且不改既有约束，或放宽约束；
- `MAJOR`：删项/改名/收窄/新增可能推翻既有结论的约束/转制品类型/IRI 变更（含弃用期 + 映射 + 回滚）。

### 6.2 触发条件（穷举，条件 ⑤ 的判定依据）

| 触发 | 是否触发本库发布 |
|---|---|
| 库内 L1/L2/L4 制品或规则变更 | ✅ 是 |
| 库内工具链/CI 变更（不影响制品内容） | ✅ 是（PATCH，制品哈希不变时记明） |
| **KERT 发布 / KERT 版本升级** | ❌ **否** |
| GITS 发布 / GITS 版本升级 | ❌ **否** |
| 数据平台接入变化 | ❌ 否（仅可能触发 SIM 声明退出条件跟踪，非本库版本） |
| 消费方需求变化 | ❌ 否（消费方按自身排期钉值） |

### 6.3 「不随 KERT 节奏」的可核验断言（建议写入 CI）

1. CI 触发源清单不含任何跨仓 webhook/事件（`SCC_CI_CROSS_REPO_HOOK`）；
2. 版本历史中不得出现「因 KERT 发布而同步发布」的条目（`SCC_VERSION_COUPLED_TO_KERT`）；
3. 允许 KERT **滞后**于本库（消费方自行排期），且不得因此阻塞本库发布。

---

## 7. 三方评审规则（条件 ②）

### 7.1 评审矩阵（建议）

| 变更级别 | 批准方 | 记录要求 |
|---|---|---|
| `patch` | 公共语义 Owner（单签） | CHANGELOG 条目 |
| `minor` | 公共语义 Owner + 受影响层 T-Box Owner | CHANGELOG + 批准记录（含具名） |
| `major` | **三方会签**：GITS Owner / KERT（Knowledge）Owner / 数据平台代表 + 公共语义 Owner | 变更预测表 + 旧夹具回归 + 影响面分析 + 弃用期计划 + 回滚预案 |
| 规则（R1~R9）名义/定性变更 | 公共语义 Owner + Owner 批准 | 见 R-rules 稿 §5 |

### 7.2 防自审（硬）

- 提交者**不得**是唯一批准人；
- `major` 变更的三方会签**缺一即不可合并**（不得以「默认通过」「超时视为同意」代替）；
- 若某方在期限内未响应，记录为「**未响应**」而非「同意」，并在报告中显式保留（不得静默记为通过）。

### 7.3 等效机制的可审计性（不用 `CODEOWNERS` 时）

须提供：评审单据模板 + 具名签署栏 + 存放路径 + 索引（可按变更号检索）。等效机制须**证明**能达到 `CODEOWNERS` 的强制力（不可绕过），否则应回到 `CODEOWNERS`。

---

## 8. 迁移期安排（WI-1-3）

| 项 | 安排 |
|---|---|
| 候选包制作地点 | **中性工作区**（本仓库 `docs/`/`loops/` 下的草稿区或独立临时目录）；**不得**直接落在 GITS/KERT 任一方的制品路径 |
| 状态登记 | 库与全部制品状态 = `CANDIDATE`；**五条件全满足前禁止标公共权威 `ACTIVE`** |
| 与 Wave 2 的接口 | Wave 2 的拆分产物（L1 本体源 + Shape + 映射）进入本库；`CTR-SEM-003` 登记须有**独立 generated 目标**（合同先行链路） |
| 与 Wave 3 的接口 | 双侧换消费时，库须已具备可发布状态与解析机制（U-2 选型 + 根域 U-1） |
| 回滚 | 库未发布 ⇒ 无消费方受影响；首次发布后回滚 = 消费方重钉上一版 `versionIRI` + 哈希 |

---

## 9. G5｜ACTIVE 五条件核验清单模板（由独立 QA 复核，Owner 记录）

| # | 核验项 | 证据 | 结论（待填） |
|---|---|---|---|
| ①-1 | 库根 Owner = 公共语义 Owner（具名） | `CODEOWNERS` | ☐ |
| ①-2 | 独立版本线（`VERSION` + 版本历史） | `VERSION`/CHANGELOG | ☐ |
| ①-3 | 独立访问控制（双仓只读） | 权限导出 | ☐ |
| ①-4 | 独立发布流水线（无跨仓触发） | CI 配置 | ☐ |
| ②-1 | 三方评审规则成文且可审计 | 评审矩阵 + 记录 | ☐ |
| ②-2 | 无自审、无单方决定（抽查近 N 次变更） | 批准记录 | ☐ |
| ③-1 | 零 `kert.*` 依赖 | 扫描日志 | ☐ |
| ③-2 | 零 GITS 运行代码依赖 | 扫描日志 | ☐ |
| ③-3 | 无兄弟仓即可构建 | 沙箱构建日志 | ☐ |
| ④-1 | 可独立构建 | 阶段 1 日志 | ☐ |
| ④-2 | 可独立解析 | 阶段 2 日志 | ☐ |
| ④-3 | 可独立验证（含红/绿与豁免登记） | 阶段 3 报告 | ☐ |
| ④-4 | 可独立发布（演练产物哈希） | 阶段 4 日志 | ☐ |
| ⑤-1 | 触发条件清单不含 KERT/GITS 事件 | 清单 | ☐ |
| ⑤-2 | 版本历史无跨仓耦合条目 | 版本历史 | ☐ |
| ⑤-3 | U-3 窗口以契约库发布周期计量 | ADR（U-3 签署件） | ☐ |
| 附 | 五条件**逐条**签署记录（不得以「整体满足」代替逐条） | 本表 | ☐ |

> 纪律：核验由**独立 QA** 执行（禁开发自签）；`ACTIVE` 由 **Owner** 记录。本表是模板，**当前全部为空**。

---

## 10. 待决项与阻塞

| # | 待决/阻塞 | 归属 | 影响 |
|---|---|---|---|
| B-1 | 公共语义 Owner / Integration Contract Owner **未任命** | Owner | **Wave 1 不能开工**（本方案无法进入执行） |
| B-2 | G-1 未达（`DESIGN_APPROVED` 未回） | 委员会（书面复审） | Wave 0 及以后全程阻塞 |
| B-3 | U-1 根域未签 | D3 双 Owner | 发布门永不开；`namespaces.json` 留空 |
| B-4 | U-2 解析机制未定 | 域名 Owner + 平台 | 条件④「可解析」的判据未定 |
| B-5 | 库短名未定（是否允许含业务域词） | Owner | 影响 README/仓库申请材料 |
| B-6 | 库的组织内建制（团队/权限组/流水线资源） | Owner / 平台 | 条件① 的落地资源 |
| B-7 | 命令名 `make conformance` 是否改名 | Owner/TL | 见 R-rules 稿 §6 Q-1 |

---

## 11. 非声明

- 本方案**未创建**任何仓库、**未发布**任何 IRI、**未**标 `ACTIVE`、**未**修改 `specs/`、`generated/`、`CONTRACT_INDEX.yaml`；
- 本方案不构成 `DESIGN_APPROVED`；不代表公共语义 Owner 已任命；
- 不含任何国标条款级声称或 `CONFORMANCE` 字样；目标报告名一律 `REFERENCE-ALIGNMENT-REPORT.md`；
- 全部命令名为建议名，实际以 Wave 1 落地的 Makefile/CI 为准。
