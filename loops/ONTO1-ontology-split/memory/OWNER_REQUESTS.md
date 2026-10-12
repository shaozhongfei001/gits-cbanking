# ONTO1-ontology-split｜Owner 待办与外部依赖登记

> TL 不得代签。本文件是**请求登记**，不是决议记录；每项状态变化须回写本文件并在 `EVIDENCE.md` 记账。
>
> **📌 面向 Owner 的单一入口（2026-09-21 新增）**：`docs/dispatch/ONTO1-Owner审核总清单与证据包-V1.0.md`
> —— 把本文件全部待审项收敛为**一份可执行清单**，每项含**背景（为什么现在需要）+ 证据（可复核文件/哈希/门禁）+ 判据 + 回执模板**，并按"能解开什么"排序。
> 本文件仍是**权威登记**；两者冲突时**以本文件为准**。

## A. 角色任命请求（阻塞 Wave 1）

| # | 请求 | 为什么阻塞 | 请求日期 | 目标日期 | 未任命期间禁止动作 |
|---|---|---|---|---|---|
| A-1 | 任命 **公共语义 Owner** | L1 定义发布、命名空间 ADR 联签、CQ1/CQ2 责任 Owner（设计 §3.1、§7） | 2026-09-20 | **Wave 1 开工前** | 独立语义契约库不得标 `ACTIVE`；L1 术语不得发布；ADR 不得签署 |
| A-2 | 任命 **Integration Contract Owner** | L4 注册表、CQ4/CQ5、三方评审召集（设计 §3.1、§6.6） | 2026-09-20 | **Wave 1 开工前** | L4 Schema/SKOS 不得发布；CQ4/CQ5 不得标 `PASS` |

**另需裁定**：词表 Owner（`TaskTypeScheme` SKOS）是否由公共语义 Owner 兼任。

## B. 外部依赖 D1~D4（复审意见 §4.2 四要素版）

> 权威来源：`docs/review/ARCH-ONTO-2026-001-rereview-package/11-外部依赖登记表.md`。以下为 TL 侧执行状态，**不改写原登记**。

| # | 依赖 | 决策 Owner | 已提交对象 | 请求/目标日期 | 未决期间禁止动作 | 解除证据 | 本会话状态 |
|---|---|---|---|---|---|---|---|
| **D1** | GB/T 48000.3-2026 正式标准文本 | 项目标准管理员 + 公共语义 Owner（接收） | 《国标正式文本获取申请》（复审包 10 号 T1） | 2026-09-20 / **2026-10-09** | 任何国标符合性声明；`REFERENCE-ALIGNMENT.md` 条款版发布；把国标对齐纳入设计基线；使用 `CONFORMANCE` 文件名 | 文本获取记录 + 条款矩阵文件 SHA-256 + 公共语义 Owner 签署 + 委员会单独复审（T2~T4） | **未到手**（跟催中，见 WI-A3） |
| **D2** | 产品关系 40 处悬空引用分类 | 产品 Owner | 《Product 模式闭合与悬空引用处置请求》+ SIM 临时模拟权威声明草案 | 2026-09-20 / **激活门禁前** | `requiresProduct`/`complementsProduct`/`mutuallyExclusiveWith` 三场景标 `PASS`；以 `WAIVED_FOR_DEVELOPMENT` 充当激活依据；SIM 登记表静默升级为企业权威 | 产品 Owner 签署的分类处置清单（逐条：有效待补/错误引用/作废）+ 非零正负夹具 + 目标计数执行记录 | **请求函今日发出**（`docs/dispatch/ONTO1-D2-产品Owner请求函.md`） |
| **D3** | 中立 IRI 根域与解析端点 | 语义架构 Owner + 基础设施/域名 Owner（联合批准） | 命名空间 ADR 框架（设计 §7）+ 本轮 ADR 草案 | 2026-09-20 / **Wave 2 开工前** | 发布任何新中立 IRI；生产重钉；把 `bank.example` 或任何占位值写入正式制品；旧 IRI 退役 | 双 Owner 签署的 ADR（含根域）+ 解析机制可解析测试记录 + 新旧 IRI 碰撞检查脚本绿 | **ADR 草案已出**（`docs/architecture/ADR-ONTO1-namespace-neutral-iri-DRAFT.md`，未预填根域） |
| **D4** | 客户/法人/集团源系统 A-Box 权威确认 | 数据 Owner + 业务 Owner（会签） | 权威责任矩阵（设计 §3.2）+ 03 号 A-Box Owner 列 + SIM 临时模拟权威声明草案 + **D4 决策包 V1.0**（`docs/dispatch/ONTO1-D4-决策包-V1.0.md`） | 2026-09-20 / **Wave 3 前（投影合同生效前）** | 把 GITS 运营库或 KERT workspace 登记为客户/法人/集团/产品身份正式权威；投影/血缘合同生效；`CustomerRole`/`GroupMembership` 场景标 `PASS` | 数据 Owner 签署的权威矩阵确认 + 授权投影合同（带来源、时点、版本）文件哈希；或 SIM 临时模拟权威声明签署件 | **请求函已发出；决策包已就绪**（`W-1/D4-pack`，门禁 `wi_a5_d4_pack` PASS）。待数据 Owner 裁定 + 业务 Owner 会签，见下方 §B-4 |

### B-4. D4 决策包（`W-1/D4-pack`）待 Owner 动作（**全在人类手上**）

> 包位置：`docs/dispatch/ONTO1-D4-决策包-V1.0.md`（机读 `evidence/d4-l1-authority-candidates.csv` + `d4-pack.json`）。TL 侧技术准备已到边界，**不得代签**。

| # | 动作 | 为什么只有 Owner 能做 | 落盘位置 |
|---|---|---|---|
| B-4-a | 八类逐项**确认或改**（每项给出「最终具名系统」） | 数据 Owner 权威归口；`Party`/`Organization` 类级取值不可执行，须落为分型级（O-D4-1） | 包 §1 各表勾选 + §8 签署区 |
| B-4-b | **集团族具名**（`EnterpriseGroup`/`GroupMembership` 的登记源系统） | 仓内零具名源系统、零源合同（O-D4-7）；不接受留空占位 | 包 §1.5/§1.6 |
| B-4-c | 批准 `SourceIdentifier` 六必填字段设计 + 具名拒绝 `MISSING_SOURCE_IDENTIFIER` | 授权依据（`authorizationBasis`）形式须由数据 Owner 定义（O-D4-4） | 包 §2 + §8 |
| B-4-d | 批准**授权投影合同**（批准 ≠ 生效；生效在 Wave 3） | 只有数据 Owner + 业务 Owner 可授权投影 | 包 §3 + §8 |
| B-4-e | 路径选择：**直接签正式权威矩阵** 或 **先签 SIM 临时声明**（正式接入后补确认） | 试点期无正式接口，属 Owner 决策 | 包 §4.1 + §8 |
| B-4-f | 圈定 SIM 三载体路径（产品身份部分由产品 Owner 圈定） | `D2` 产品 Owner 并行；客户/法人/集团部分属 D4 | 包 §4.1 |
| B-4-g | 给出**投影时效（freshness）阈值** | 否则 `PROJECTION_STALE` 为空转（O-D4-5） | 包 §3 要素 2 |
| B-4-h | 裁定 O-D4-2（与 GK-KE `core.ExternalIdentifier` 是否归一） | 跨包语义一致性，须由语义/数据 Owner 裁定 | 包 §6 |

**未签期间的自我约束（已执行）**：投影合同不生效；`CustomerRole`/`GroupMembership` 场景与 CQ1/CQ2 保持 `NOT_EVALUATED`；不把 GITS 运营库或 KERT workspace 登记为正式权威；不代签；SIM 台账 `ledger_status` 不提前启动。

## C. 委员会 / 书面复审（唯一能解 Wave 0 的卡点）

| # | 请求 | 状态 | 到达后动作 |
|---|---|---|---|
| C-1 | 书面复审结论（`DESIGN_APPROVED` 或 `PASS_WITH_REQUIRED_CHANGES`，上限不含 GB/T 条款级对齐） | **缺口已定位并补齐**（2026-09-20）：复审包 12 文件哈希 12/12 与 MANIFEST 一致，但**缺"送审函"与"决议签署页"**（旧送审包两件已随 `RETURN_TO_HLD` 归档、裁定项已被推翻）⇒ 委员会无可签署载体，结论无法返回。已增补 `13-送审函-书面复审.md` + `14-书面复审决议签署页.md`，MANIFEST 升 **V1.1**（01~12 内容零改动、哈希逐字一致，可复算） | 收到签署决议后：1) 更新 `LOOP.yaml.gate_state` 与 `memory/ORCHESTRATOR.md §0`；2) 通知全部角色；3) 按决议填写 `G-1` 条件判定；4) 若仍退回则记 `FAILURES.md` 并重排波次 |

### C-1 具体待办（Owner 侧，5 项，全在人类手上）

> **已压缩为 3 分钟操作版**：`docs/dispatch/ONTO1-送审Owner操作卡-V1.0.md`（填 4 名 / 勾 6 框 / 跑 3 条命令，
> 含「发出的包 == 受检的包」自证命令与红线三条）。下表为同样的动作，附"为什么只有 Owner 能做"。

| # | 动作 | 为什么只有 Owner 能做 | 落盘位置 |
|---|---|---|---|
| C-1-a | **指定本轮评审人与渠道**（委员名单 / 主席 / 秘书处汇总人） | 组织权限 | `14` 签署表的姓名栏 |
| C-1-b | **批准并发出送审函**（13） | 对外发文权限 | `13` 末页签署区 + 发送回执 |
| C-1-c | **交付包给委员**（自含，无需访问代码仓） | 分发权限 | 命令见操作卡第 3 步；包与冻结件一致性由 `wi_zip_manifest_verify` 判定 |
| C-1-d | **设定期限并催办**（建议 2026-10-09） | 对委员会的时间要求 | `13` §四 |
| C-1-e | **收回签署页（14）并交回项目侧** | 结论传递 | `docs/review/` 归档 + 通知 TL |

> **项目侧已自我约束**：未收到正式签署前保持 `RETURN_TO_HLD`，不启动 Wave 0 及以后任何动作；
> 已新增门禁 `wi_review_package_integrity`（冻结 01~12 哈希）+ `wi_zip_manifest_verify`（绑定发出的包与受检的包），
> 防"包被静默改动"与"发出的包≠受检的包"两种失真。

### C-2 新增待办：O-D4-2 **差异补充决议**（属实质语义冲突，须 Owner/契约方裁定）

| # | 动作 | 说明 |
|---|---|---|
| C-2-a | 裁定两套外部标识模型的出口 | **出口 A** 吸收 / **出口 B** 并存+映射 / **出口 C** 撤回 `SourceIdentifier`；草案见 `docs/dispatch/ONTO1-O-D4-2-差异补充决议草案-V1.0.md`（含字段级冲突表与三出口影响对比） |
| C-2-b | 若选 A/C：决定是否开放 GK-KE 回归窗口 | A/C 必然改动 GK-KE 已登记件（L1-1 包 + 6 个 neg 夹具），须协调窗口 |
| C-2-c | 若选 B：授权起草映射合同 | 映射合同登记于 L4 注册表；**未落地映射与一致性门禁前，B 不视为可用** |

> **TL 建议（非裁定）**：`B 过渡 → A 目标`；不建议 C（`objectType` 语义损失会把已知歧义制度化）。
> **未决期间禁止动作**：不得在 `specs/` 或 L4 注册表登记 `SourceIdentifier`；CQ1 保持 `NOT_EVALUATED`（本条为追加阻塞）。

### C-1 送审程序状态（2026-09-20 更新，包 `W-1/review-submission`）

**项目侧已把"可做的程序"做到边界，剩下 5 项全在人类手上**：

| 项 | 状态 | 证据 |
|---|---|---|
| 包自洽（01~12 冻结 12/12 + 13/14 齐备 + MANIFEST 自洽） | **PASS** | `wi_review_package_integrity`（Attempt 2，`evidence/wi_review_package_integrity-20260920T141501Z.log`） |
| 门禁有牙齿（静默改 01 / 删 14 ⇒ FAIL） | **PASS** | `wi_review_package_selftest`（Attempt 2，`evidence/wi_review_package_selftest-20260920T141504Z.log`） |
| 重打包预演（zip 含 13/14，共 15 件） | **PASS**（仅 `/tmp`，仓库无 zip） | `evidence/review-submission-zip-dryrun-20260920T1415Z.log` |
| 《送审操作清单》V1.0 | 已落盘 | `memory/handoffs/ONTO1-W-1-送审操作清单-V1.0.md` |
| 《结论回收与门禁更新预案》V1.0（三形态 24h 动作） | 已落盘 | `memory/handoffs/ONTO1-W-1-结论回收与门禁更新预案-V1.0.md` |
| **批准发出 / 收回签署件** | **未做（仅 Owner 可做）** | 本文件 §C-1-a ~ §C-1-e |

> **发出前的硬条件**（清单 §3）：重打包后必须自证「发出的包 == 受检的包」（`diff` 两份 `sha256sum` 清单 ⇒ `SENT_PACKAGE_IDENTICAL`），并在发出前重跑 `python3 scripts/onto1_review_package_check.py --gate`。
> **收到后的第一步**：按预案 §1 做有效性判定（V1~V9 共九项，fail-closed）；判 `INVALID_RETURN` 的签署件**不得**用来更新门禁。

### C-3 新增待办：签署页 `14` 的两个**隐藏前置**（2026-09-21 收口时补登）

> 来源：`memory/ROLE_BOARD.yaml → review_panel.outstanding_technical_items`（原先**只存在该字段**，未进本清单与操作卡）

| # | 前置 | 事实（可复算） | 待 Owner 决定 |
|---|---|---|---|
| C-3-a | **评审独立性** | 现四席具名均为同一自然人（`ROLE_BOARD.review_panel.composition_facts.single_natural_person_panel = true`，`distinct_named_reviewers = 1`）⇒ 依决议第 4/6 条**只能记 `OWNER_REVIEW`** | **补 ≥3 位真正独立具名评审**，还是**维持 `OWNER_REVIEW`** |
| C-3-b | **签署页在冻结包内** | `docs/review/ARCH-ONTO-2026-001-rereview-package/14-书面复审决议签署页.md` 哈希 `df2933d1e183b9d50e98d784…`，**与包内 MANIFEST 登记逐字一致** ⇒ **填入姓名即改哈希、破坏包自洽**（`wi_review_package_integrity` / `wi_zip_manifest_verify`） | 姓名**手写填入**（包不动），还是由 TL **重发 V1.2 包**（新哈希 + 重跑 integrity/zip 自证） |
| C-3-c | **角色名不一致** | 冻结包 `14` 签署表沿用旧角色名（`架构委员（语义/本体）` 等）；决议第 5 条的四角色名为（主席 / 本体语义架构 / 数据治理 / 集成架构）。操作卡签署表**已是新名** | 若要统一 ⇒ 同样需重发包（同 C-3-b） |

**共同边界**：以上三项**均不阻塞 SIM 开发**；只决定能否声明 `ARCHITECTURE_COMMITTEE_APPROVED` 与正式基线生效。

## D. TL 已做且**不需**再申请的既有授权

- 统一命名、种子本体对齐等 8 项后续工作不属本 Loop，仅在 `SHARED_MEMORY.md §3` 登记归属建议；
- 「范围不变的客观落实」不重复申请同名决定（沿用 GK 程序裁定口径）。

---

## E. Owner 决议落地状态（2026-09-21）—— **本节为状态更新，不改写上文原登记**

**决议来源**：`docs/dispatch/ONTO1-Owner决议建议与授权边界-V1.0.md`（人类 Owner 于 2026-09-21 会话确认采用 O-01~O-13；**该文件 §四 签署栏仍留空**）。
**落地台账**：`memory/OWNER-DECISIONS-2026-09-21-LANDING.md`。

| 原登记项 | 状态变化 |
|---|---|
| A-1 / A-2 角色任命 | **`APPROVED`（临时 `INTERIM`）**：PSO 与 ICO 由**项目 Owner**临时兼任（O-02/O-03）；**本人不得充当独立 QA**；作为实现作者时不得单人批准合并；任期至正式任命或 `OWNER_ACTIVATED`（较早者） |
| 词表 Owner 兼任 | **`APPROVED`**：**双责任、单语义 Owner**（O-04；语义以 PSO 受控词表版本为准） |
| C-1 书面复审 | **`APPROVED`：批准发起**（O-01）；目标回收 **2026-10-09**；评审组四角色，秘书处/TL **只分发汇总、不投票不代签**；**Wave 0 仍须等有效签署页 14 过V1~V9 共九项校验** |
| D1 | **`APPROVED`**：批准获取与条款级**参照对齐**，**继续移出设计基线**（O-09） |
| D2 | **`RETURNED_FOR_ITEMIZED_PRODUCT_DECISION`**：40 处全部 `QUARANTINED_UNRESOLVED`（O-06）；解除须产品 Owner 逐条三分类 |
| D3 | **`APPROVED_WITH_CONDITIONS`**：批准**政策**、**不批准根域字面量**；Wave 2 继续阻塞（O-05） |
| D4 | **`APPROVED_WITH_CONDITIONS`**：选 **SIM 临时权威路线**（3 具名载体 + 六必填 + freshness）；合同**仍 `NOT_EFFECTIVE`**（O-07） |
| D-4 / D-5 | **`APPROVED` 维持保守**：不得批量 `equivalentClass`；`exactMatch` 默认不批准；单项放行须差异表 + 回归 + PSO 决议（O-10） |
| D-7 | **`APPROVED_WITH_CONDITIONS`**：原则追认"指针化收敛"，**须具名三文件 + 哈希 + 来源 + 维护方书面确认**后解除"KERT 零新增写入"（O-11） |
| O-D4-2（C-2） | **`APPROVED`**：**"B 过渡 → A 目标"**（O-08）；L4 须登记映射合同 + 字段完备性门禁；**C-2 未关闭前 CQ1 不得 `PASS`** |
| refalign 守卫 | **`APPROVED_WITH_REQUIRED_CHANGES`**：只作**临时发文语法守卫**；须整改单字误报 / 可读审计证据 / `exit=0` 假绿（O-12） |
| 项目门禁 | **不变：`RETURN_TO_HLD`**（O-13）；Wave 0~3 · CQ3 激活 · `OWNER_ACTIVATED` **全部 `BLOCKED`** |
| `independent_qa` | **保持不变：`pending` / `actor=null`**（**不代签**） |
