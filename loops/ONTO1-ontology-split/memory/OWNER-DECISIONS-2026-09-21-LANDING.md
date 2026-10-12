# ONTO1｜**Owner 决议落地台账**（O-01 ~ O-13）

| 项 | 值 |
|---|---|
| 决议来源 | `docs/dispatch/ONTO1-Owner决议建议与授权边界-V1.0.md` |
| 输入 SHA-256（被审对象） | `846f10bb5099d52ac5b91be8d663cd5ff97bb886d2786839bf0a3aa38da6c5e1` |
| 确认形态 | **人类 Owner 于 2026-09-21 会话中确认采用 O-01~O-13**（**文件 §四 的签署栏仍留空**；正式签署件如另出，以签署件为准、本台账随之更新） |
| 落地日期 | 2026-09-21 |
| 落地角色 | TL（AI，`implementation_actor=tech_lead`） |
| **项目门禁** | **`RETURN_TO_HLD` 不变**；`DESIGN_APPROVED=NO` · `WAVE_0_STARTED=NO` · `INDEPENDENT_QA=PENDING/actor=null` |
| **红线** | **不自签、不代签、不把本台账扩写为 `DESIGN_APPROVED`/`QA_PASS`/生产权威/正式银行口径**；SIM 只对**模拟试点**有效 |

> **落地纪律**：本台账只执行决议原文（§五 允许的 6 类动作 + O-12 要求的守卫整改）。任何超出此范围的"顺手推进"都属越界，**不做**。

---

## 一、逐项落地状态（13 项）

| # | Owner 结论 | **立即生效范围（TL 已落地）** | **仍阻塞 / 待人类或外部** |
|---|---|---|---|
| **O-01** | 批准发起书面复审（`APPROVED_WITH_CONDITIONS`），**≠ 复审通过** | ① 采用 13 号送审函 + 14 号签署页 + V1.1 自含包**发起**；② 目标回收日 **2026-10-09**；③ 落地"发出前硬条件"（重打包 → 双清单比对 ⇒ `SENT_PACKAGE_IDENTICAL` → `wi_review_package_integrity` exit=0）并归档；④ V1~V9 共九项有效性检查清单就位；⑤ **评审组四角色**（主席 / 本体语义架构 / 数据治理 / 集成架构，秘书处仅分发汇总、**不投票不代签**）写入送审操作卡 | **具名评审人与渠道**须人类 Owner 填入；**签署页 14 返回并过V1~V9 共九项校验**前，`Wave 0` 保持 `BLOCKED`；任何委员提出未关闭 BLOCKER ⇒ 维持 `RETURN_TO_HLD` |
| **O-02** | 任命 Public Semantic Owner（**临时**） | 角色板写入 `INTERIM`：授权范围 = L1 候选定义/术语准入/兼容性裁定 · ADR 语义侧联签 · CQ1/CQ2 语义验收 · D-4/D-5 逐项映射判断；**任期**至正式任命或 `OWNER_ACTIVATED`（较早者） | **限制**：不得代委员会 / 域名 Owner / Data Owner / 产品 Owner / **独立 QA**；**不得独自把候选资产标 `ACTIVE`** |
| **O-03** | 任命 Integration Contract Owner（**临时**） | 角色板写入 `INTERIM`：L4 注册表 · JSON Schema/LinkML 合同 · 版本兼容政策 · 三方评审召集 · CQ4/CQ5 合同验收 | **隔离**：可与 O-02 同一人，但**逻辑职责/决策记录/制品版本必须分开**；**本人不得充当独立 QA**；**作为实现作者时不得单人批准合并** |
| **O-04** | 词表 Owner 采用"**双责任、单语义 Owner**" | 登记：PSO 管 `TaskTypeScheme` **含义/层级/代码弃用/映射**；ICO 管**序列化与消费约束**；**语义冲突以 PSO 的受控词表版本为准，接口不得反向改写词义** | 无新增阻塞 |
| **O-05** | D3：**批准政策，不批准根域字面量**；Wave 2 继续阻塞 | 记录 6 条强制政策（中立 HTTPS 域 / ontology IRI 稳定 + version IRI 指向不可变版本 / 解析端点支持内容协商 / 旧 `gits:` 标 `LEGACY` 走显式映射与退役窗口 / `latest` 仅导航**禁止作生产钉值**、生产必须固定 version IRI + 内容哈希 / **禁止 `bank.example` 等占位进入正式制品**）；ADR 采用"建议结构仅作**模板**"口径 | **真实根域 + DNS/HTTPS 控制 + 解析机制 + 持久性承诺**须语义架构 Owner 与域名/基础设施 Owner **联签**；**Wave 2 保持 `BLOCKED`** |
| **O-06** | D2：`RETURNED_FOR_ITEMIZED_PRODUCT_DECISION`，**不替产品 Owner 猜测** | 40 处关系**全部**置 `QUARANTINED_UNRESOLVED`（落地台账 §二 + 隔离登记表）；**不进入 ACTIVE 关系图**、不参与推荐/资格判断/GraphRAG 事实回答；**CQ3 保持 `NOT_EVALUATED`**；可另建**明确标识为 SIM** 的正负夹具验证引擎（夹具通过 ≠ 40 条内容获批） | **产品 Owner 按逐条证据完成三分类**后方可解除内容阻塞（有意保留的 **P1** 阻塞） |
| **O-07** | D4：选 **SIM 临时声明**路线（`APPROVED_WITH_CONDITIONS`） | SIM 声明写入 3 个临时权威数据产品：**`SIM-CUSTOMER-MASTER`**（Party/Organization/LegalEntity/CustomerRole）· **`SIM-GROUP-REGISTRY`**（EnterpriseGroup/GroupMembership）· **`SIM-PRODUCT-CATALOG`**（ProductOffering，**关系仍受 O-06 隔离**）；`SourceIdentifier` **六必填**（`sourceSystemId`/`sourceObjectType`/`sourceRecordId`/`sourceVersion`/`observedAt`/`authorizationBasis`），缺失 ⇒ 具名拒绝 `MISSING_SOURCE_IDENTIFIER`；`effectiveFrom/effectiveTo` **不塞入** SourceIdentifier；freshness **相对 `scenarioAsOf`**（Party/CustomerRole 24h · Organization/LegalEntity 7d · EnterpriseGroup/GroupMembership 7d · ProductOffering 24h）；合同 `simulationOnly=true`、**无生产写回、无正式银行权威声明** | 投影合同**仍 `NOT_EFFECTIVE`**：生效前须 **Schema 校验 + 正负夹具 + 来源/时点/版本校验 + 独立 QA**；**生产数据 Owner 对真实银行源系统的正式确认**仍缺（不可由 SIM 外推） |
| **O-08** | C-2 / O-D4-2：选 **"B 过渡 → A 目标"**（`APPROVED`） | 登记过渡期规则：L1 `SourceIdentifier` 与 `core.ExternalIdentifier` **并存**；**L4 登记显式映射合同 + 字段完备性门禁**；缺 `sourceVersion`/`observedAt`/`authorizationBasis` 的旧记录**只能标 `PARTIAL_MAPPING`**，不得伪装完整映射；**C-2 碰撞未关闭前 CQ1 不得标 `PASS`**；目标态定义（`core.ExternalIdentifier` 升级为集成序列化/兼容视图并**逐步退役**）登记为演进方向 | **进入目标态前**必须开放 **GK-KE 回归窗口**并通过旧消费者兼容测试；映射合同与一致性门禁**未落地前 B 不视为可用** |
| **O-09** | D1：**批准获取与条款级参照对齐**，**继续移出设计基线**（`APPROVED`） | 目标日 **2026-10-09**；标准管理员获取、PSO 接收；**未形成条款矩阵前不发布** `REFERENCE-ALIGNMENT.md` 条款版；**不得使用"符合/认证/全量继承"表述**，**不得使用 `CONFORMANCE` 文件名**；D1 **不阻塞**书面复审与 Wave -1 | 文本到手 + 条款矩阵 + 单独复审（**T2~T4**） |
| **O-10** | D-4 / D-5：**维持保守策略**（`APPROVED`） | 登记 5 条：① `RETAINED_AUTHORITY_MOVED` **不得批量**赋 `owl:equivalentClass`；② `REMODELED` **默认不得**赋 SKOS `exactMatch`；③ **权威主体改变既不证明等价也不证明不等价**，是否等价**必须逐项**比较定义/外延/约束/身份规则/时间语义；④ 证据不足时用**项目迁移状态**表达，**不用强语义映射掩盖不确定性**；⑤ **任何单项放行**须有**术语差异表 + 回归结果 + PSO 决议** | 逐项放行须由 **PSO（INTERIM）** 决议并留证 |
| **O-11** | D-7：**原则上追认**"指针化收敛"（`APPROVED_WITH_CONDITIONS`） | 登记 4 条件：① 三文件**必须具名 + 当前哈希 + 历史来源**；② 历史内容**只读保留**，**不静默删除/改写 Git 历史**；③ 新版本**只维护指针/映射**，不复制第二份可编辑真相；④ **KERT 维护方书面确认后**才解除"KERT 零新增写入"限制 | **未提供三文件清单与签署回执前，本项不视为执行完成**（文件清单见 `memory/TL-DECISIONS-W-1.md` D-7 与 `evidence/` 记录） |
| **O-12** | refalign：`APPROVED_WITH_REQUIRED_CHANGES`（**只作临时发文语法守卫**，不作永久语义真相门禁） | **已整改三项**（详见 §三）：① **单字误报**（否定识别改**词级/行首动词**规则）；② **可读审计证据**（由 `sha256\|len` 改为 `sourceRef + file_sha256 + line/object id + 脱敏摘要`）；③ **防"零候选/exit=0 假绿"**（固定守恒量 + **内置必败变异**）；并登记**重记触发条件** | **不批准其为永久语义真相门禁**；`exit=0` **只证明本次未命中违规**，**不代表**委员会或独立 QA 通过 |
| **O-13** | 维持 `RETURN_TO_HLD`，**不修改项目门禁** | 写入 Wave 解锁表：`Wave -1` 允许继续（只读/决策包/夹具/计划，**不改权威制品**）；`Wave 0` `BLOCKED`（等签署页 14 + V1~V9 共九项校验）；`Wave 1` `BLOCKED`（Wave 0 + O-02/O-03 人类确认生效）；`Wave 2` `BLOCKED`（D3 真实根域双 Owner 联签）；`Wave 3` `BLOCKED`（SIM/投影合同签署 + QA；C-2 映射与回归关闭）；`CQ3/产品关系激活` `BLOCKED`（D2 逐条分类 + 非零正负夹具）；`OWNER_ACTIVATED` `BLOCKED` | 以上解锁条件**全部为外部/人类动作** |

---

## 二、O-06 隔离实施（40 处产品关系）

| 项 | 内容 |
|---|---|
| 立即状态 | **全部 40 处** = `QUARANTINED_UNRESOLVED`（**不赋予**"有效待补/错误/作废"任何最终语义） |
| 证据与登记 | 机读隔离登记表：`loops/ONTO1-ontology-split/evidence/product-relations-quarantine.json`（含逐条 `prerequisiteProduct`/`complementaryProduct` 拆分计数、来源清单指针、隔离理由、解除条件） |
| 消费禁令（立即） | 不进入 ACTIVE 关系图；**不参与**推荐 / 资格判断 / GraphRAG 事实回答 |
| CQ3 | **保持 `NOT_EVALUATED`**（门禁 `wi_a6_cq_fixtures` 已断言"设计阶段无 PASS"） |
| 允许的 SIM 活动 | 可另建**明确标识为 SIM** 的正负夹具以验证引擎；**夹具通过 ≠ 40 条内容获批** |
| 解除条件 | 产品 Owner 按**逐条证据**完成三分类（有效待补 / 错误引用 / 作废）+ 非零正负夹具 + 目标计数执行记录 |

---

## 三、O-12 守卫整改（`scripts/onto1_reference_alignment_check.py`）

| 要求 | 整改 |
|---|---|
| ① 单字误报（"禁止常用单字"导致账本无法忠实引用历史原文） | 否定识别改为**行首动词式**规则（`未/不/无` + 动词/名词，**词级**），并把单字从**标题锚点**标记中排除（沿用 R-1 修复）；**账本引用**改由"描述 + 可读证据"承载 |
| ② `sha256\|len` 不可读 | 违规证据固定输出 **`sourceRef`（相对路径）+ `file_sha256` + `line`/object id + 脱敏摘要**（触发词以 `▮` 掩码，**避免报告自身成为违规源**） |
| ③ `exit=0` 假绿 / 零候选 | `--gate` 每次报告固定：**受检文件集哈希** · **脚本版本** · **候选数** · **允许数** · **违规数** · **一条内置必败变异**（合成声称必须被判违规；否则 `SELF_CONTROL_FAILED` ⇒ FAIL） |
| ④ 重记触发条件（替代"每次内容变化都重记"） | **必须重记**：脚本变更 / 受检文件集变化 / 候选数异常下降 / 出现新增违规；**可不重记**：普通内容增长且上述守恒量正常（此时须声明"已 ad-hoc 复验 exit=0 / 0 违规"及时间） |
| ⑤ 定位 | 本守卫**只作发文前语法守卫**；**不得**被引作语义真相或独立 QA 结论 |

---

## 四、TL 未做（**明确不做**，防越界）

- **不**把本台账或 Owner 确认扩写为 `DESIGN_APPROVED` / `QA_PASS` / 生产权威 / 正式银行口径；
- **不**填任何具名评审人、**不**发函、**不**收回签署页（人类动作）；
- **不**为 O-06 的产品关系**编造分类**；**不**为 O-05 **虚构根域**；**不**把 SIM 外推为生产权威；
- **不**改 `specs/`、`generated/`、`docs/dd/` 权威制品（Wave -1 只读边界不变）；
- **不**在 `EVIDENCE.json.independent_qa` 写入任何值（保持 `pending/actor=null`）；
- **不**把 refalign 的 `exit=0` 表述为"通过"以外的东西（**它只证明本次未命中违规**）。

---

## 五、非声明

1. 本台账是**执行记录**，不是 Owner 决议本身；决议文本以 `ONTO1-Owner决议建议与授权边界-V1.0.md` 为准；
2. 文件 §四 的**签署栏仍留空**；若人类 Owner 另行出具签署件，以签署件为准并更新本台账；
3. 本台账**不构成** `DESIGN_APPROVED` / `QA_PASS` / 生产授权 / 银行正式口径；
4. GB/T 相关仅作**参照对齐**用途，**不含**且**不得引申为**符合性表述；
5. 与 `OWNER_REQUESTS.md`、复审包 11 号或 `specs/` 冲突时，**以后者为准**。

### 三.1 O-12 验收证据（2026-09-21T03:15Z，TL 实测）

| 验收项 | 方法（沙箱夹具，`--root` 指向临时目录） | 结果 |
|---|---|---|
| ① **单字误报修复** | 三种写法：`- 未签发…` / `- **未**签发…` / `- **不发布**…`（均含受限词表触发词 + 文件级 gb_scope） | **三种全部放行**：`allowed_by_reason` 计 `line_start_negation=2` + `same_line_negation=1` |
| ② **声称构造优先否决**（防新盲区） | 同一文件写「本设计不〔符合〕GB/T … 的全部要求。」 | **仍判违规** ✅（行首否定**不得**放行声称构造） |
| ③ **对照** | 「本设计〔符合〕GB/T … 的全部要求。」 | **判违规** ✅ |
| ④ **可读审计证据** | 违规 finding 字段 = `source_ref` + `file_sha256` + `line` + `object_id` + `line_sha256` + `excerpt_redacted` | 样例：`object_id=b-claim-construction.md#L5`；`excerpt='本设计不▮▮▮▮▮▮▮ 48000.3-2026 的全部要求。'`（**可读 + 触发词掩码**） |
| ⑤ **守恒量 + 内置必败变异** | `--gate` 报告固定输出 | `守恒量：script_sha256=… fileset_sha256=… files=4614 candidates=165 allowed=86 violations=0`；`内置必败变异（自控）：按预期判违规` |

**过程诚实**：① 的首版实现**漏掉**「否定字后紧跟强调符（`**`）」的写法 ⇒ 首次验收即被判 `CONTENT_WORDING_UNALLOWED`（**是验收测试抓出来的，不是我自查发现的**）；修正为 `(?:\*\*|__)?` 后通过。**记入 `FAILURES.md`**。

**重记（O-12 ④ 要求的触发条件）**：脚本变更 ⇒ `wi_a3_reference_alignment`（`…165523Z`，exit 0）与 `…_selftest`（`…165525Z`，exit 0）**已重记**；被取代的两份旧日志按白名单留证。
**预算消耗公示（/8）**：`wi_a3_reference_alignment` **7/8** · `…_selftest` **5/8**（D-15：**不得**再靠上调上限解决）。

**未做（O-12 明确不批准的）**：**不**把本守卫升格为永久语义真相门禁；**不**用其 `exit=0` 表述为"通过"以外的含义（它只证明本次未命中违规）。

---

## 六、O-01 发出前硬条件：**TL 侧预检结果**（2026-09-21T03:30Z）

| 检查 | 命令 | 结果 |
|---|---|---|
| 包自洽（14 件登记 + 冻结件一致） | `python3 scripts/onto1_review_package_check.py --gate` | **PASS**（`ONTO1-review-package: PASS`；MANIFEST 登记 14 件，自洽校验完毕） |
| 重打包预演 + 篡改可检出 | `python3 scripts/onto1_zip_manifest_verify.py --dryrun` | **PASS**（`zip members=15 / repo expected=15 / missing=0 / extra=0`；`M1 篡改包内成员 ⇒ 必须被判 FAIL` 命中，证明有牙齿） |

> **注意**：以上为**预检**，**不等于**已发出。按 O-01，更新门禁的前置是四件同时成立：
> **`SENT_PACKAGE_IDENTICAL`** ∧ 包检查 `exit=0` ∧ **签署页 14 有效** ∧ **无未关闭 BLOCKER**。
> 其中"发出后自证一致"须在**真实发出**时按操作卡第 3 步生成两份 `sha256sum` 清单并 `diff`；**签署页为人类动作**。

**仍待人类（O-01）**：填入具名评审人/主席/秘书处与渠道 → 批准发出 13 → 交付包 → 设期限（目标回收 **2026-10-09**）→ **收回签署页 14**。

---

## 七、角色口径 **已由 Owner 最终决议裁定**（2026-09-21，签署主体：项目 Owner 邵钟飞）

> 本节原为"待 Owner 一句话确认"；**Owner 最终决议已生效**，现按裁定收敛如下（**只改角色与流程表达，不改决议语义**）。

| 项 | 裁定 |
|---|---|
| **PSO / ICO 正式 holder** | **保持「项目 Owner（邵钟飞）」，`status=interim`** —— **不得**改为 TL / AI / Agent 正式持有（第 1 条） |
| **TL / Agent 身份** | **delegated technical executor** + **review secretariat / technical advisor**（第 2 条） |
| **TL / Agent 可做** | 技术准备 · 证据登记 · 材料汇总 · 裁定建议 |
| **TL / Agent 不得做（五项）** | ① 代替 Owner 或委员会签署；② 批准契约激活；③ **单人**将候选资产提升为 `ACTIVE`；④ 充当独立 QA；⑤ 将**建议结论**登记为**正式权威事实** |
| **PSO / ICO 隔离** | 同一人可临时兼任，但**职责逻辑隔离**：PSO 定词义/本体/词表/语义版本；ICO 定接口表达/版本绑定/兼容性/消费者契约；**ICO 不得反向改写 PSO 已批准的语义**（第 3 条） |
| **评审独立性** | 六项技术结论**必须由具名评审组分别确认**；**不得** Owner 发函前预填或代勾；Owner 兼任评审时**只签自己那份**（第 4、6 条） |
| **记录口径** | 未形成独立评审与有效签署 ⇒ **只能记 `OWNER_REVIEW`**，**不得**记 `ARCHITECTURE_COMMITTEE_APPROVED`（第 6 条） |
| **状态** | `RETURN_TO_HLD` · Wave 0+ `BLOCKED` · `independent_qa=pending/actor=null` · C-2 未关闭；**不得**因自检 / `refalign exit=0` / Owner 发函提前提升门禁（第 7 条） |

**同步落盘位置**：`memory/ROLE_BOARD.yaml`（`tech_lead.identity`/`must_not`、`review_panel`、`review_record_rules`）· `memory/TL-DECISIONS-W-1.md` **D-17 补丁** · `docs/dispatch/ONTO1-送审Owner操作卡-V1.0.md` · 本台账。

---

## 八、Owner 最终决议 **第 8 条执行台账**（角色与流程措辞统一，2026-09-21）

**执行范围声明**：本台账**只改角色与流程表达**；**Owner 决议原文语义未改写**（`docs/dispatch/ONTO1-Owner决议建议与授权边界-V1.0.md` **未被修改**）。

### 8.1 逐文件检查结果

| 文件 | 冲突/待统一项 | 处置 |
|---|---|---|
| `memory/ROLE_BOARD.yaml` | 缺 Agent 身份定义与禁止项；评审组与记录口径未登记 | **新增** `tech_lead.identity`（delegated technical executor + review secretariat/advisor）+ `may`/`must_not`（五项）；PSO/ICO 补 `holder_fixed_by`（不得改为 TL/AI/Agent）+ `decides`/`logical_separation`；**新增** `review_panel`（四角色 + 秘书处不投票不代签）与 `review_record_rules`（`OWNER_REVIEW` vs `ARCHITECTURE_COMMITTEE_APPROVED` + 不得提前提门禁） |
| `memory/TL-DECISIONS-W-1.md` | D-17 未含 Agent 身份/五项禁止/评审独立性/记录口径 | **追加 D-17 补丁（8 条）**，逐条对应决议第 1~8 条 |
| `docs/dispatch/ONTO1-送审Owner操作卡-V1.0.md` | **★ 实质冲突**：原写「若你就是评审方…第 1~2 步可合并为你本人直接勾选 `14`」——**与决议第 4/6 条直接冲突**；签署表角色名与决议不一致 | **删除该"合并/直接勾选"条款**，改为强制约束（须具名评审组分别确认 · 不得预填/代勾 · Owner 兼任时只签自己那份 · 否则只记 `OWNER_REVIEW`）；签署表角色名对齐为**主席 / 本体语义架构 / 数据治理 / 集成架构 + 秘书处（TL）**；"发出"行明确**由 Owner 批准并发出**、分发可由秘书处执行 |
| `docs/dispatch/ONTO1-Owner审核总清单与证据包-V1.0.md` | §1.4 缺评审独立性与记录口径 | 追加三条（评审独立性 / 记录口径 / **不得因自检或 Owner 发函提前提门禁**） |
| `memory/handoffs/ONTO1-W-1-结论回收与门禁更新预案-V1.0.md` | 有效性判定仅 V1~V7，未含独立性与提前提升 | **新增 V8（评审独立性）· V9（不得提前提升门禁）**，并注明"仅加严、不放松"，口径统一为 **V1~V9 共九项** |
| `memory/OWNER_REQUESTS.md` · `review-submission-HANDOFF.md` · `LOOP.yaml` · 本台账 | "七项校验"表述与 V8/V9 不一致 | 统一为 **V1~V9 共九项**；`LOOP.yaml.gate_state` 增 `owner_final_resolution_20260921` 摘要（**`current` 仍 `RETURN_TO_HLD`**） |

### 8.2 我自己的过程缺陷（如实记录）

操作卡里"Owner 可合并第 1~2 步、直接勾选 `14`"这句**是我早前起草时写的**，它给了"Owner 自签即视为委员会结论"的口子——**正是决议第 4/6 条要堵的那个口子**。本次按决议删除。教训：**流程文书里凡涉及"谁能签、签什么"的便利性写法，必须先问"它是否制造了代签路径"**。

### 8.3 决议第 8 条要求的检查结果（全绿）

```
loop-guard: PASS · onto1-evidence-board: PASS · make memory-check PASS · make evidence-check PASS
refalign --gate: OK（exit=0，我方文书未新增违规）
wi_a2_obligation_triage --gate: PASS
受控目录 generated/ specs/ docs/dd/ 改动 = 0
```

### 8.4 状态确认（决议第 7 条，**未提前提升**）

| 项 | 值 |
|---|---|
| 项目门禁 | **`RETURN_TO_HLD`**（`LOOP.yaml.gate_state.current` 未变） |
| Wave 0 及后续 | **全部 `BLOCKED`**（`wave_unlock` 未改，仅 wave_0 表述更新为 V1~V9） |
| `independent_qa` | **`pending` / `actor=null`**（未代签） |
| C-2 / `wi_a4_namespace_collision` | **仍 `fail`（exit 2，唯一 fail）**，未关闭 |
| 板面 | 31 门禁 = 30 pass / 1 fail（结论未变） |

---

## 九、评审角色任命登记（Owner 指令：四席具名均为「邵钟飞」，2026-09-21）

### 9.1 已登记（`memory/ROLE_BOARD.yaml` → `review_panel`）

| 角色 | 具名 |
|---|---|
| 委员会主席 | **邵钟飞** |
| 本体语义架构委员 | **邵钟飞** |
| 数据治理委员 | **邵钟飞** |
| 集成架构委员 | **邵钟飞** |
| 秘书处（汇总人） | TL（仅分发/汇总/校验；**不投票、不代签**） |

### 9.2 我必须以技术顾问身份点明的事实与后果（**不是拒绝登记，是如实标注等级**）

- **事实**：四席由**同一自然人**具名 ⇒ `distinct_named_reviewers = 1`、`independent_review_roles_formed = False`。
  议事规则上"四个席位"已填满，但**席位的独立性在事实上不成立**——决议第 4 条所要求的"由具名评审组**分别**确认"，其**前提是不同评审主体的独立意见**。
- **依决议第 6 条的后果**：＊未形成规定的独立评审角色和有效签署结果 ⇒ **只能记录为 `OWNER_REVIEW`**，**不得记录为 `ARCHITECTURE_COMMITTEE_APPROVED`**。＊
  ⇒ 本项目解锁条件（`wave_0` = "委员会有效签署页 14 返回并通过 V1~V9"）中的 **V8（评审独立性）不通过** ⇒ **Wave 0、Wave 1 及其后仍为 `BLOCKED`**。
- **注意与第 3 条的区别**：决议**明确允许** PSO/ICO **由同一人临时兼任**（前提是职责逻辑隔离）；但**评审角色**的独立性是**第 4/6 条的硬要求**，两者不可类推——前者可同人，后者需要独立评审主体才能产生委员会级结论。

### 9.3 我**没有**做的事（红线自检）

1. **未改动 14 号签署页**（哈希仍 `df2933d1e183b9d50e98d784…`，与包内 MANIFEST 登记一致）——它在冻结包内，填名会**破坏包自洽**（`wi_review_package_integrity` / `wi_zip_manifest_verify`）；
2. **未预填、未代勾**六项技术结论（第 4 条禁止）；
3. **未改动门禁**（`gate_state.current` 仍 `RETURN_TO_HLD`；`wave_0` 仍 `BLOCKED`）；
4. **未替任何人签署**（第 2 条五项禁止之一）。

### 9.4 三条可选路径（**需 Owner 指定，我按指定执行**）

| 路径 | 内容 | 技术后果 | 备注 |
|---|---|---|---|
| **A（现指令的直读）** | 维持四席同一人 ⇒ 结论按 **`OWNER_REVIEW`** 归档 | **不构成委员会批准** ⇒ **Wave 0 仍 BLOCKED**；若要据此推进，须由 **Owner 以自身权限书面改写 `wave_0` 解锁条件**（**我不代改**） | 14 号姓名在**签发/签署时手写填入**，包不动 |
| **B（推荐，可走委员会口径）** | 你保留**实际担任**的席位，其余三席**补具名独立人** | 可产出 `ARCHITECTURE_COMMITTEE_APPROVED`（仍须 V1~V9 全过） | 若需**预印姓名**，我重发 **V1.2** 包（新哈希 + 重跑 integrity/zip 自证） |
| **C（只你签你那份 + 其余另定）** | 先只签你实际担任的角色，其余席位待定 | 结论不完整 ⇒ **门禁零动作**，等待补齐 | 与决议第 6 条完全一致 |

> 三路径共同点：**六项技术结论仍须评审后分别确认**（不得发函前预填）；**板面、门禁、`independent_qa`、C-2 状态均不变**。
