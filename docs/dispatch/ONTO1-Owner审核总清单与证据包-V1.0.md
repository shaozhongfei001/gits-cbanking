# ONTO1 本体四层拆分｜**Owner 审核总清单与证据包 V1.0**

> **用途**：把散落在 `OWNER_REQUESTS.md`、派工件与决策包里的**全部 Owner 待审项**收敛成**一份可执行清单**，每项附**背景（为什么现在需要）+ 证据（可直接复核的文件/哈希/门禁）+ 判据（什么算完成）**。
> **本文件不构成任何批准**，也不代表项目侧可代替 Owner 做决定；所有签署栏均为空。
> **状态口径**：门禁 `RETURN_TO_HLD` 仍有效；状态机位于 `FOR_REVIEW`；**迁移进度 0/4 个状态门**（`DESIGN_APPROVED` → `IMPLEMENTED` → `QA_PASS` → `OWNER_ACTIVATED`）。
> **生成时间**：2026-09-21；**依据**：`loops/ONTO1-ontology-split/memory/OWNER_REQUESTS.md`（权威登记）+ `memory/TL-DECISIONS-W-1.md`（D-1~D-16）+ `docs/dispatch/ONTO-SPLIT-本体四层落地执行计划-V2.0.md`。

---

## 0. 一页总览（**按"能解开什么"排序**）

| 级别 | 编号 | 事项 | Owner | 类型 | 解开什么 | 时限 |
|---|---|---|---|---|---|---|
| **P0** | **C-1-a~e** | 指定评审人与渠道 → 批准发出送审函（13）→ 交付包 → 设期限 → **收回签署页（14）** | 项目侧决策 Owner | 批准 + 对外发文 | **唯一能解 Wave 0 的卡点** | 建议 **2026-10-09** |
| **P0** | **A-1 / A-2** | 任命 **公共语义 Owner** / **Integration Contract Owner**（另裁定词表 Owner 是否兼任） | 组织/项目 Owner | 任命 | **Wave 1 开工** | Wave 0 前 |
| **P1** | **D3** | 批准**中立 IRI 根域**与解析端点（ADR 联签） | 语义架构 Owner + 域名/基础设施 Owner | 联合批准 | Wave 2（拆分落地） | Wave 2 前 |
| **P1** | **D2** | 产品关系 **40 处悬空引用**分类处置（逐条） | 产品 Owner | 裁定 | **CQ3 三场景硬阻塞** | 激活门禁前 |
| **P1** | **D4** | 客户/法人/集团 A-Box **权威确认** + 授权投影合同（**8 项子决定**，见 §3.3） | 数据 Owner + 业务 Owner | 会签 | Wave 3（投影/血缘合同生效） | Wave 3 前 |
| **P2** | **C-2-a~c** | **O-D4-2**：两套外部标识模型的出口选择（A 吸收 / B 并存+映射 / C 撤回） | Owner + 契约方 | 裁定 | CQ1（追加阻塞） | 与 D4 同步 |
| **P2** | **D1** | GB/T 48000.3-2026 **正式文本获取**（用途：**参照对齐**，非符合性） | 项目标准管理员 + 公共语义 Owner（接收） | 获取 + 接收 | 条款级对齐（**已移出本次基线**） | 目标 **2026-10-09** |
| **P2** | **追认 D-4 / D-5** | ① 权威层迁移项**不得**用 `equivalentClass` 批量放行；② `REMODELED → exactMatch` 维持 `NOT_GRANTED`，**任命后逐项裁定** | 公共语义 Owner | 追认/逐项裁定 | L1 语义契约发布 | 任命后 |
| **P3** | **追认 D-7** | KERT 仓 **3 个文件**历史写入的归属裁定（是否追认"指针化收敛"） | KERT 维护方 / Owner | 追认 | KERT 侧协作前提 | — |
| **P3** | **D-6 / 未裁定清单** | 接口差异 3 处已裁定待知悉；**根域字面量、解析机制、持久性承诺、窗口与退役门参数 P-1~P-11、`extraMatch`、激活签署**均未裁定 | 见各项 | 裁定 | 各对应 Wave | 各 Wave 前 |

**给不同 Owner 的阅读顺序**：项目/组织 Owner → §2 + §1；语义架构 + 域名 Owner → §3.2（D3）、§4；产品 Owner → §3.1（D2）；数据 + 业务 Owner → §3.3（D4 八项）+ §5（O-D4-2）；公共语义 Owner（候任）→ §2.1、§4.3、§4.4；委员会 → §1。

---

## 1. 委员会书面复审（**唯一能解 Wave 0**）

### 1.1 背景（为什么卡在这里）
设计提交后委员会判 **`RETURN_TO_HLD`**（3 BLOCKER / 10 MAJOR / 3 MINOR），书面复审**已提交**并已按意见补齐证据。但复审轮原先**没有"送审函"与"决议签署页"**——旧送审包的两件已随 `RETURN_TO_HLD` 归档，且其裁定项（三层拆分 / 沿用 `gits:` 前缀 / Product 归 KERT）**已被委员会推翻**，不可复用 ⇒ **委员会无可签署载体，结论无法返回**。已增补 `13`/`14`，使委员会具备可签署决议载体。

### 1.2 需要 Owner 做的 5 件事（全在人类手上）

| # | 动作 | 为什么只有 Owner 能做 | 落盘位置 |
|---|---|---|---|
| C-1-a | 指定本轮**评审人与渠道**（委员名单 / 主席 / 秘书处汇总人） | 组织权限 | `14` 签署表姓名栏 |
| C-1-b | **批准并发出送审函** | 对外发文权限 | `13` 末页签署区 + 发送回执 |
| C-1-c | **交付包给委员**（包自含，无需访问代码仓） | 分发权限 | 操作卡第 3 步 |
| C-1-d | **设定期限并催办** | 对委员会的时间要求 | `13` §四 |
| C-1-e | **收回签署页（14）并交回项目侧** | 结论传递 | `docs/review/` 归档 + 通知 TL |

**3 分钟操作版**（填 4 名 / 勾 6 框 / 跑 3 条命令）：`docs/dispatch/ONTO1-送审Owner操作卡-V1.0.md`。

### 1.3 证据（可直接复核）

| 证据 | 值 |
|---|---|
| 包清单与冻结哈希 | `docs/review/ARCH-ONTO-2026-001-rereview-package/MANIFEST.md`（**V1.1**；**01~12 内容零改动、哈希与 V1.0 逐字一致**） |
| 送审函（13） | `13-送审函-书面复审.md`，`sha256:964a546c86e5cf80633a0b75e733d227c22a618a23d36cd13709b1145d20a4ef` |
| 决议签署页（14） | `14-书面复审决议签署页.md`，`sha256:df2933d1e183b9d50e98d784ab7f1c342a589b7e558f5202780f71601eb826c8` |
| 包自洽门禁 | `wi_review_package_integrity` **PASS**（Attempt 2）· `wi_review_package_selftest` **PASS**（变异：静默改 01 / 删 14 ⇒ FAIL） |
| 「发出的包 == 受检的包」 | `wi_zip_manifest_verify` **PASS**（含篡改变异；重打包后须自证 `SENT_PACKAGE_IDENTICAL`） |
| 重打包预演 | `evidence/review-submission-zip-dryrun-20260920T1415Z.log`（zip 含 13/14 共 15 件，仅落 `/tmp`） |

### 1.4 判据与收到之后的动作
- **发出前硬条件**：重打包 → `diff` 两份 `sha256sum` 清单 ⇒ `SENT_PACKAGE_IDENTICAL` → 再跑 `python3 scripts/onto1_review_package_check.py --gate`（期望 exit 0）。
- **收到后第一步**：按 `memory/handoffs/ONTO1-W-1-结论回收与门禁更新预案-V1.0.md` §1 做**V1~V9 共九项有效性判定**（fail-closed）；判 `INVALID_RETURN` 的签署件**不得**用于更新门禁。
- **有效结论到达后**：更新 `LOOP.yaml.gate_state` 与 `ORCHESTRATOR.md §0` → 通知全部角色 → 填 `G-1` 条件判定 → 若仍退回则记 `FAILURES.md` 并重排波次。
- **评审独立性（Owner 2026-09-21 最终决议第 4、6 条）**：六项技术结论**必须由具名评审组（主席 / 本体语义架构 / 数据治理 / 集成架构）完成评审后分别确认**；**不得**由项目 Owner 在发函前**预填或代勾**；Owner 若兼任其中一个评审角色，**只能签署自己对应的角色意见**。
- **记录口径（不得混用）**：未形成规定的独立评审角色与有效签署结果时，**只能记录为 `OWNER_REVIEW`**，**不得**记录为 `ARCHITECTURE_COMMITTEE_APPROVED`。
- **不得提前提升门禁**：自检通过、`refalign exit=0` 或 Owner 发函**均不构成**门禁提升理由；提升只依**有效签署页 + V1~V9 校验**。

> **红线**：**严禁任何国标符合性表述**；条款级对齐**已移出本次基线**；文件名禁用 `CONFORMANCE`（用 `REFERENCE-ALIGNMENT`）。

---

## 2. 角色任命（阻塞 Wave 1）

### 2.1 A-1 公共语义 Owner / A-2 Integration Contract Owner

| # | 请求 | 为什么阻塞 | 未任命期间**禁止动作** |
|---|---|---|---|
| A-1 | 任命 **公共语义 Owner** | L1 定义发布、命名空间 ADR 联签、CQ1/CQ2 责任 Owner | 独立语义契约库不得标 `ACTIVE`；L1 术语不得发布；ADR 不得签署 |
| A-2 | 任命 **Integration Contract Owner** | L4 注册表、CQ4/CQ5、三方评审召集 | L4 Schema / SKOS 不得发布；CQ4/CQ5 不得标 `PASS` |

**另需裁定**：词表 Owner（`TaskTypeScheme` SKOS）**是否由公共语义 Owner 兼任**。

**背景材料（候任人选已备）**：

| 角色 | 候选准备包 | 内容 |
|---|---|---|
| 公共语义 Owner | `loops/ONTO1-ontology-split/memory/handoffs/PSO-01-公共语义Owner候选准备包.md` | L1 八类术语定义稿、建模规则 R1~R9、ADR 联签意见、Wave 1 独立语义契约库五条件落地方案、CQ1/CQ2 履职准备 |
| Integration Contract Owner | `…/ICO-01-集成契约Owner候选准备包.md` | L4 注册表边界、CQ4/CQ5 履职准备、三方评审召集方式 |

**回执方式**：在 `OWNER_REQUESTS.md` §A 标注任命结果与生效日期；TL 回写 `ROLE_BOARD.yaml`。

---

## 3. 外部依赖 D1~D4（复审意见 §4.2 四要素版）

> 权威来源：`docs/review/ARCH-ONTO-2026-001-rereview-package/11-外部依赖登记表.md`。以下为**执行状态**，**不改写原登记**。

### 3.1 D2｜产品关系 40 处悬空引用分类（产品 Owner）

- **背景**：产品卡中有 40 处关系引用（12 `prerequisiteProduct` + 28 `complementaryProduct`，共 12 个不同取值）**指向不存在的产品**；且 `Product` 已按委员会裁定重构为 **`ProductOffering`** 入**公共层**，**产品主数据权威不默认 KERT 产品卡** ⇒ 谁有权判定"哪些引用有效"，只有产品 Owner 能定。
- **需要 Owner 做**：**逐条**给出分类处置（**有效待补 / 错误引用 / 作废**）+ 非零正负夹具 + 目标计数执行记录。
- **证据**：`docs/dispatch/ONTO1-D2-产品Owner请求函.md` · `docs/dispatch/ONTO1-D2-产品Owner决策包-V1.0.md` · 探测门禁 `wi_a5_product_refs` **PASS**（悬空引用逐条落盘机读清单）。
- **不做会怎样**：`requiresProduct` / `complementsProduct` / `mutuallyExclusiveWith` **三场景硬阻塞**，**CQ3 不得标 `PASS`**；且 **不得** 用 `WAIVED_FOR_DEVELOPMENT` 充当激活依据（豁免永不满足激活门禁）。
- **回执**：产品 Owner 签署的分类处置清单（逐条）。

### 3.2 D3｜中立 IRI 根域与解析端点（语义架构 Owner + 域名/基础设施 Owner 联合批准）

- **背景**：委员会裁定命名空间走**中立持久 IRI**、旧 `gits:` 转 **LEGACY 兼容迁移**；但**根域取值属 Owner 权限**，TL **刻意未预填**（ADR 草案留空）。同时存在 **C-2 两处真实前缀冲突**（`gits:` 双绑定 + `gits:Product` 同名不同 IRI）**未修**，属 Wave 3；在根域确定前，**发布任何新中立 IRI 或生产重钉都是越界**。
- **需要 Owner 做**：双 Owner 签署 **ADR（含根域）** + 解析机制可解析测试记录。
- **证据**：`docs/architecture/ADR-ONTO1-namespace-neutral-iri-DRAFT.md`（**未预填根域**）· `wi_a4_iri_mapping` **PASS**（映射草案 87 行 / 迁移域 67；D3 未签期间**不得**出现具体新 IRI）· 碰撞检查 `wi_a4_namespace_collision` **FAIL（仅 C-2）**——即"重钉未做"的直接证据 · `evidence/namespace-known-defects.json`（缺陷登记，含解除条件）。
- **不做会怎样**：**Wave 2 不得开工**；新 IRI 不得发布；旧 IRI 不得退役。
- **回执**：双 Owner 签署的 ADR（含根域字面量 + 解析机制 + 持久性承诺）。

### 3.3 D4｜客户/法人/集团 A-Box 权威确认（数据 Owner + 业务 Owner 会签）

- **背景**：GITS 运营库与 KERT workspace **都不是**客户/法人/集团身份**正式权威**；投影合同与血缘在权威确认前**不得生效**。试点期无正式接口 ⇒ 需 Owner 选择"直接签正式矩阵"或"先签 SIM 临时声明"。
- **需要 Owner 做的 8 项**（包 §8 签署区）：

| # | 动作 | 约束 |
|---|---|---|
| B-4-a | 八类逐项**确认或改**（每项给出最终具名系统） | `Party`/`Organization` 类级取值不可执行，须落为**分型级**（O-D4-1） |
| B-4-b | **集团族具名**（`EnterpriseGroup`/`GroupMembership` 登记源） | 仓内**零具名源系统、零源合同**（O-D4-7）；**不接受留空占位** |
| B-4-c | 批准 `SourceIdentifier` **六必填字段** + 具名拒绝 `MISSING_SOURCE_IDENTIFIER` | 授权依据（`authorizationBasis`）形式须由数据 Owner 定义（O-D4-4） |
| B-4-d | 批准**授权投影合同**（**批准 ≠ 生效**；生效在 Wave 3） | 仅数据 Owner + 业务 Owner 可授权投影 |
| B-4-e | 路径选择：**直接签正式矩阵** 或 **先签 SIM 临时声明** | 试点期无正式接口 |
| B-4-f | 圈定 **SIM 三载体**路径（产品身份部分由产品 Owner 圈定） | 与 D2 并行 |
| B-4-g | 给出**投影时效（freshness）阈值** | 否则 `PROJECTION_STALE` 门禁**空转**（O-D4-5） |
| B-4-h | 裁定 **O-D4-2**（与 GK-KE `core.ExternalIdentifier` 是否归一） | 见 §5 |

- **证据**：`docs/dispatch/ONTO1-D4-决策包-V1.0.md`（八类候选 + 最小字段 + 合同草案 + SIM 载体建议 + 退出台账）· 机读 `evidence/d4-l1-authority-candidates.csv` + `d4-pack.json` · 门禁 `wi_a5_d4_pack` **PASS** + `wi_a5_d4_pack_selftest`（九条变异：A-Box 登记为运营库 / 删必填 / CQ 标 PASS / 合同填生效日期 / 候选缺证据 / 证据不可回源 / 候选仅剩一个 / 退出条件少一条 / 声明未生效却启动台账 ⇒ 均被拦下）· `docs/dispatch/ONTO1-D4-数据Owner请求函.md` · `docs/architecture/ONTO1-SIM临时模拟权威声明草案.md`（**NOT_EFFECTIVE**：三载体 + 四退出条件，台账未启动）。
- **不做会怎样**：投影/血缘合同不生效；`CustomerRole`/`GroupMembership` 场景与 **CQ1/CQ2 保持 `NOT_EVALUATED`**。
- **回执**：签署的权威矩阵确认（或 SIM 临时声明签署件）+ 授权投影合同（带来源、时点、版本）文件哈希。

### 3.4 D1｜GB/T 48000.3-2026 正式标准文本（项目标准管理员 + 公共语义 Owner 接收）

- **背景**：委员会走**缩小批准范围路线**——**条款级对齐移出本次基线**，因此本项**不阻塞**当前 Wave，但**文本到手前任何"符合性"表述都禁止**（含文件名）。
- **需要 Owner 做**：获取正式文本并交付公共语义 Owner 接收（文本获取记录）。
- **证据**：`docs/dispatch/ONTO1-D1-国标正式文本获取申请-DRAFT.md` · 参照对齐守卫门禁 `wi_a3_reference_alignment` **PASS**（当前 `allowed[rule_statement]=1`、`candidates=159`；**"真实标准对齐声称"恒不放行**——含主题词或标题语境的声称同样 FAIL）。
- **时限**：目标 **2026-10-09**。
- **不做会怎样**：`REFERENCE-ALIGNMENT.md` **条款版不得发布**；不得把国标对齐纳入设计基线。

---

## 4. 需 Owner **追认/裁定**的 TL 技术裁定

> 依据：`memory/TL-DECISIONS-W-1.md`。TL 只对**Loop 内技术事项**裁定；以下各项**属 Owner 权限**，TL 仅登记与执行"未决期间禁止动作"。

| # | 事项 | TL 已做的技术认定 | 需 Owner 做什么 | 未决期间禁止动作 |
|---|---|---|---|---|
| **D-4** | 4 项 `RETAINED_AUTHORITY_MOVED`（`LegalEntity`、`ProductKnowledgeCard`、`ProductKnowledgeVersion`、`supersedesVersion`）能否用 `equivalentClass` 批量放行 | **不放行**（迁移改变了六列权威中的"定义 Owner""实例事实 Owner"，消费者据此判断"谁裁决"的行为会变） | 若认为存在"确实只是物理搬家"的个案，须**逐项**提交差异说明并由**公共语义 Owner 放行**（**不得批量**） | 不得批量放行；不得据此改 L1 契约 |
| **D-5** | 是否有 `REMODELED` 项可升级为 SKOS `exactMatch`（J-2/A-4） | **维持 `NOT_GRANTED`** | 任命后由**公共语义 Owner 逐项裁定**并留证 | 不得因"看起来很接近"而放行 |
| **D-7** | KERT 仓 **3 个文件**的历史写入归属与处置 | **不预设归因，登记待追认** | KERT 维护方 / Owner 裁定是否追认"指针化收敛" | 未追认前 **KERT 侧不再新增与 ONTO1 相关写入** |
| **D-8 / O-D4-2** | 两套外部标识模型（`core.ExternalIdentifier` vs `SourceIdentifier`） | 升级为**差异补充决议**；TL 建议 `B 过渡 → A 目标`（**非裁定**） | **Owner/契约方选出口**（详见 §5） | 不得在 `specs/` 或 L4 注册表登记 `SourceIdentifier`；CQ1 保持 `NOT_EVALUATED` |
| 未裁定·根域 | 根域类别与字面量、解析机制、持久性承诺（A-1） | **刻意不预填** | 语义架构 Owner + 域名 Owner（同 **D3**） | 不得写入占位值（`bank.example` 等） |
| 未裁定·窗口 | 窗口与退役门参数 **P-1~P-11**（A-2） | 任命前**维持默认** | 公共语义 Owner（任命后） | 不得据默认值发布 |
| 未裁定·其它 | O-D4-1 / O-D4-3 / O-D4-7 等 D4 待裁项；`extraMatch`；根域；权威；**激活签署** | 见 D4 决策包 §6 | 数据 Owner + 业务 Owner / 对应 Owner | **禁止代签** |

---

## 5. O-D4-2 差异补充决议（**会被制度化的一处语义冲突**）

- **背景**：GITS 侧要引入 `SourceIdentifier`（含 `authorizationBasis` 等六必填字段），而 GK-KE 侧已有 `core.ExternalIdentifier`。两者**字段级冲突**（`objectType` 等）若不裁定，会在 L4 注册表里**并存两套"外部标识"语义**。
- **需要 Owner 选出口**：

| 出口 | 含义 | 影响 |
|---|---|---|
| **A 吸收** | 一套模型吸收另一套 | 必然改动 GK-KE 已登记件（L1-1 包 + 6 个 neg 夹具）⇒ 需**开放回归窗口** |
| **B 并存 + 映射** | 两套并存并登记映射合同 | 映射合同登记于 L4；**未落地映射与一致性门禁前，B 不视为可用** |
| **C 撤回** | 撤回 `SourceIdentifier` | `objectType` **语义损失**，会把已知歧义**制度化**（TL 不建议） |

- **证据**：`docs/dispatch/ONTO1-O-D4-2-差异补充决议草案-V1.0.md`（**字段级冲突表 + 三出口影响对比 + 建议路径 `B 过渡 → A 目标`**）。
- **判据**：签署的出口选择 + （若 A/C）GK-KE 回归窗口决定 + （若 B）映射合同授权。

---

## 6. 证据索引（复核用）

| 类别 | 位置 |
|---|---|
| Owner 待办权威登记 | `loops/ONTO1-ontology-split/memory/OWNER_REQUESTS.md` |
| TL 技术裁定（D-1~D-16，含"未裁定留给 Owner"清单） | `…/memory/TL-DECISIONS-W-1.md`（**§附** 明列未裁定事项） |
| 执行计划（状态机 / Wave -1 许可 / 禁止动作） | `docs/dispatch/ONTO-SPLIT-本体四层落地执行计划-V2.0.md` §0、§12 |
| 设计权威（四层模型 / 六列权威 / 五态验证） | `docs/architecture/ONTOLOGY-SPLIT-DESIGN-V2.0-REVIEW.md` |
| 委员会退回意见与整改复审意见 | `docs/review/ARCH-ONTO-2026-001_架构委员会评审报告_V1.0.md`、`…_整改复审意见_V1.0.md` |
| 复审包（01~12 冻结 + 13/14 + 哈希） | `docs/review/ARCH-ONTO-2026-001-rereview-package/MANIFEST.md`（**V1.1**） |
| 门禁账（31 项，**唯一 fail = C-2**） | `loops/ONTO1-ontology-split/EVIDENCE.json` + `evidence/*.log`（含自证哈希 9 份） |
| 未关闭阻断项 / 批次收束 | `…/memory/NEXT_SESSION.md`、`…/memory/ORCHESTRATOR.md` §7 |
| 盲区账（防假绿经验） | `…/memory/ORCHESTRATOR.md` §7.2（**G-1~G-11**） |

---

## 7. 材料清单：**已就绪** vs **待 Owner 产出**

**已就绪（项目侧，可直接取用）**
送审函 13 · 决议签署页 14 · 3 分钟操作卡 · 结论回收预案 · 公共语义/集成契约 Owner 候选准备包 ×2 · D2 请求函 + 决策包 · D4 请求函 + 决策包 + 机读候选表 · O-D4-2 差异补充决议草案 · SIM 临时模拟权威声明草案 · D1 文本获取申请 · ADR 草案（未填根域）· 门禁 31 项与全部日志 · 45 项四层归属矩阵 · 消费者扫描与 691 行真义务清单。

**待 Owner 产出（项目侧不得代签）**
① 签署的书面复审决议（14）② 两个角色任命 + 词表 Owner 兼任裁定 ③ D2 逐条分类处置清单 ④ D3 双 Owner 签署 ADR（含根域）⑤ D4 权威矩阵确认（或 SIM 临时声明）＋ 授权投影合同 ＋ freshness 阈值 ⑥ O-D4-2 出口选择 ⑦ D1 文本获取记录 ⑧ D-4/D-5/D-7 的追认或逐项裁定。

---

## 8. 回执模板（每项一份，TL 回写登记）

```
事项编号：            （如 D2 / D3 / D4-B-4-a / O-D4-2 / C-1-b）
决定内容：            （明确写"批准/驳回/选择某出口/具名某系统"）
生效条件与日期：
附件（签署件文件名 + sha256）：
知悉的禁止动作：       （该项对应的"未决期间禁止动作"）
签署人 / 角色 / 日期：
```

---

## 9. 未决期间项目侧**已执行**的自我约束（供 Owner 核对）

- 未启动 Wave 0 及以后任何动作；`LOOP.yaml.gate_state` 保持 `RETURN_TO_HLD`；
- **未**标 `DESIGN_APPROVED`/`FROZEN`；**未**拆分权威本体；**未**切换消费入口；**未**正式重钉；
- **未**把任何占位根域（`bank.example` 等）写入正式制品；**未**发布任何新中立 IRI；
- **未**把 GITS 运营库或 KERT workspace 登记为正式权威；投影合同**未生效**；SIM 台账 `ledger_status` **未启动**；
- **不发布**任何国标**符合性**表述（红线：该类措辞及文件名一律禁用）；**不使用** `CONFORMANCE` 文件名；
- `CustomerRole`/`GroupMembership` 场景与 **CQ1/CQ2/CQ3 保持 `NOT_EVALUATED`**；`WAIVED_FOR_DEVELOPMENT` **未**用作激活依据；
- **未**代签任何门禁；`EVIDENCE.json.independent_qa` 仍 `pending/actor=null`；
- 受控目录（`generated/` `specs/` `docs/dd/`）**零改动**；KERT 仓**零写入**；共享本体哈希未漂移（`705578d6324abd0c`）。

---

## 10. 非声明

1. 本文件是**待审项归纳与证据索引**，**不是**批准、不是决议、**不构成任何 Owner 意见**；
2. 不含、也不得引申为**国标符合性表述**；GB/T 相关仅作**参照对齐**用途；
3. 本文件不构成 `QA_PASS` / `DEV_SELF_CHECK_PASS`；本 Loop 仍有已知 fail（**C-2**，属 Wave 3）；
4. 各项"时限"来自计划与 `OWNER_REQUESTS.md`，**非对 Owner 的工期承诺**；
5. 若本文件与 `OWNER_REQUESTS.md`、复审包 11 号或 `specs/` 冲突，**以后者为准**。
