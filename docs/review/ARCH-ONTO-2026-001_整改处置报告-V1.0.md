# ARCH-ONTO-2026-001 整改处置报告 V1.0

| 项 | 值 |
|---|---|
| 对象 | `docs/review/ARCH-ONTO-2026-001_架构委员会评审报告_V1.0.md`（RETURN_TO_HLD，3 BLOCKER / 10 MAJOR / 3 MINOR / 10 关闭条件） |
| **状态** | **SUPERSEDED（2026-09-20 复审意见 INSUFFICIENT_EVIDENCE）**：由复审包内 `02-整改处置报告-V2.0.md` 取代（`docs/review/ARCH-ONTO-2026-001-rereview-package/`，含状态口径修正与全量证据）；本报告 V1.0 的「9/10 已关闭」表述作废，以 V2.0 的诚实汇总为准 |
| 整改载体 | `docs/architecture/ONTOLOGY-SPLIT-DESIGN-V2.0-REVIEW.md`（下称 V2.0） |
| 日期 | 2026-09-20 |
| 处置人 | 全局架构师 |
| 状态定义 | **CLOSED-DESIGN** = 设计层已关闭，待委员会复审确认；**BLOCKED-EXTERNAL** = 依赖外部输入（标准文本/Owner 裁定/域名批准），已发起；**DEFERRED-WORK** = 属委员会允许的复审前分析工作，已排入 Wave -1 |

---

## 一、缺陷逐条处置（16 项）

| ID | 等级 | 发现（摘要） | 处置 | 证据位置 | 状态 |
|---|---|---|---|---|---|
| B-01 | BLOCKER | 「A/B/C 任一 ⇒ 公共」算法把消费关系等同共同所有权 | **采纳**。废止旧算法；采用委员会四条公共层准入条件；术语分四层 + SKOS 词表 | V2.0 §2.2、§3.1、§4 | CLOSED-DESIGN |
| B-02 | BLOCKER | 客户/法人/集团/产品实例权威错写为 GITS/KERT | **采纳**。正式 A-Box Owner = 银行源系统/数据平台；GITS/KERT 仅授权投影；SIM 临时模拟权威声明（含退出条件、责任人） | V2.0 §3.2、§4.2、附录 A | CLOSED-DESIGN（A-Box Owner 签署 = BLOCKED-EXTERNAL ④） |
| B-03 | BLOCKER | 设计批准/实施/QA/激活混为一个 APPROVED | **采纳**。四态状态机；委员会只批 `DESIGN_APPROVED`；新决议页（附件二） | V2.0 §10；本报告附件二 | CLOSED-DESIGN |
| M-01 | MAJOR | 「权威循环」证据不足且自相矛盾 | **采纳**。论断撤回；改六列权威表 + 发布依赖分析；Product 归属改由准入四条件论证 | V2.0 §2.1、附录 B | CLOSED-DESIGN |
| M-02 | MAJOR | 未读正式条款即声称全量继承 | **采纳**。统一降级为「参照对齐」；采用委员会给定声明文字（逐字）；文件更名 `REFERENCE-ALIGNMENT.md`；R1~R9 重定性为内部工程控制 | V2.0 §8 | 表述层 CLOSED-DESIGN；条款级矩阵 = BLOCKED-EXTERNAL ① |
| M-03 | MAJOR | 「显式豁免」承接零实例与 40 悬空引用 | **采纳**。验证状态模型五态；豁免永不满足激活门禁；40 引用须分类处置（有效待补/错误/作废），不得永久豁免 | V2.0 §5、§6.1、§6.2 | CLOSED-DESIGN（Owner 分类裁定 = BLOCKED-EXTERNAL ②） |
| M-04 | MAJOR | 沿用 GITS 命名空间与中立治理冲突 | **采纳**。中立持久 IRI + 旧 IRI `LEGACY` + 兼容映射 + 退役窗口 + 碰撞检查；根域不预填，待两 Owner 批准 | V2.0 §7 | CLOSED-DESIGN（根域批准 = BLOCKED-EXTERNAL ③） |
| M-05 | MAJOR | 硬编码/三套命名排除在迁移范围外 | **采纳**。命名统一仍可后续立项，但**全量消费者扫描 + 命中/处置表 + 回归**纳入 Wave 2/3 退出门禁；初版清单见附件三 | V2.0 §7(7)、§11；附件三 | CLOSED-DESIGN（全量扫描 = DEFERRED-WORK，Wave -1） |
| M-06 | MAJOR | OWL 类/词表/执行合同未区分 | **采纳**。TaskType→SKOS `TaskTypeScheme`；ActivationContract/Capability 等→JSON Schema/LinkML 注册表；OWL 仅用于需推理概念 | V2.0 §3.1、§4.4 | CLOSED-DESIGN |
| M-07 | MAJOR | 门禁偏文件语法，缺语义质量 | **采纳**。六类 CQ 验收矩阵（查询+正例+负例+预期+Owner+变异复验） | V2.0 §6.6 | CLOSED-DESIGN（夹具设计 = DEFERRED-WORK） |
| M-08 | MAJOR | 证据未区分事实与作者判断 | **采纳**。证据三级标注（VERIFIED/SYSTEM_OBSERVATION/EXPERT_JUDGMENT）+ 摘要哈希 + 复现命令；基线计数降级为系统观察 | V2.0 附录 C | CLOSED-DESIGN（复审包重标 = DEFERRED-WORK） |
| M-09 | MAJOR | 「只增不改」过简 | **采纳**。major/minor/patch 兼容矩阵 + 弃用期 + 迁移映射 + 回滚 + 变更测试；新增约束可判 major | V2.0 §6.5 | CLOSED-DESIGN |
| M-10 | MAJOR | 7.5 人日承诺失真 | **采纳**。撤回工时承诺，仅留量级提示；WBS+依赖+缓冲重估列入复审前允许工作 | V2.0 §11；V1.2 落地计划已标注暂停 | CLOSED-DESIGN（重估 = DEFERRED-WORK） |
| m-01 | MINOR | 目标总量未计新增类 | **采纳**。统一计数：基线 32 全映射 → 目标 45（19+8+12+6），13 净新增 | V2.0 §4.5 | CLOSED-DESIGN |
| m-02 | MINOR | PROVENANCE 写 authorityRepo=Leibniz-KERT | **采纳**。改 `authorityEntity`（公共语义权威实体）+ `hostingRepo` 双字段 | V2.0 §0-16 | CLOSED-DESIGN |
| m-03 | MINOR | Wave 0「零风险」过度 | **采纳**。改低风险；Wave 0 检查表（输入锚点 + 失败条件）列入计划 V2.0 重写 | V2.0 §11 | CLOSED-DESIGN |

## 二、十项关闭条件状态（评审报告 §8）

| # | 条件 | 状态 | 说明 |
|---|---|---|---|
| 1 | 逐术语权威矩阵 | **CLOSED-DESIGN** | V2.0 附录 A（45 项）；机读 22 字段版随复审包 |
| 2 | 四层目标模型 | **CLOSED-DESIGN** | V2.0 §3/§4；词表单列 |
| 3 | 业务真相边界纠正 | **CLOSED-DESIGN**（Owner 签署 BLOCKED-EXTERNAL） | V2.0 §3.2、§4.2；SIM 临时权威声明模板已含退出条件 |
| 4 | Product 模式闭合 | **CLOSED-DESIGN**（40 引用分类 BLOCKED-EXTERNAL） | V2.0 §5；describesProduct 已建模 |
| 5 | 命名空间 ADR | **CLOSED-DESIGN**（根域批准 BLOCKED-EXTERNAL） | V2.0 §7 框架完整（映射/等价规则/窗口/退役/碰撞） |
| 6 | 标准适用性矩阵 | **BLOCKED-EXTERNAL**（唯一未关闭项） | 表述已合规降级 + 矩阵框架就绪；正式文本获取中，获取后 1 个工作日内可完成逐条标注 |
| 7 | 验证状态模型 | **CLOSED-DESIGN** | V2.0 §6.1 五态；豁免规则明确 |
| 8 | 消费者影响清单 | **CLOSED-DESIGN + DEFERRED-WORK** | 要求已纳入 Wave 2/3 门禁；初版清单附件三；全量扫描排 Wave -1 |
| 9 | 语义验收矩阵 | **CLOSED-DESIGN**（夹具 DEFERRED-WORK） | V2.0 §6.6 六 CQ 全覆盖（身份/有效期/来源/产品卡引用/能力可见可执行/动作回执） |
| 10 | 新决议页 | **CLOSED-DESIGN** | 附件二 |

**自评**：9/10 条件设计层关闭；条件 6 依赖正式标准文本（外部采购/借阅流程，非技术阻塞）。建议复审形式：**书面复审**即可（变更均为评审报告指定方向，无新增争议点）。

## 三、复审前工作计划（Wave -1，委员会 §9 允许范围）

| 项 | 产出 | 前置 |
|---|---|---|
| 三仓/三制品基线 + 完整哈希 | 基线清单 v2 | 无 |
| 全量消费者扫描（硬编码 ID/旧 IRI/旧文件名/生成目标/plan hash/钉值方） | 消费者影响清单正式版 | 双仓只读 |
| 正式标准文本获取 + 条款适用性矩阵 | `REFERENCE-ALIGNMENT.md` 条款版 | 文本获取（外部） |
| 命名空间 ADR 起草 + 新旧 IRI 映射表 | ADR 送审稿 | 根域批准（外部） |
| CQ 夹具设计（正/负例/预期） | 夹具包 | 无 |
| WBS 重估 | 计划 V2.0 工期章 | 无 |

## 附件二：复审决议页文字（替代送审包 08 页）

> **裁定 1（命名空间）**：批准「机构控制的中立持久 IRI + 旧 gits: IRI 转 LEGACY 兼容迁移」方向；具体根域由语义架构 Owner 与域名 Owner 批准后回填 ADR。
> **裁定 2（Product）**：批准 `ProductOffering` 入公共业务语义核心；产品身份 A-Box Owner 为产品主数据/数据产品（SIM 阶段为 Owner 批准的临时模拟权威，含退出条件）；KERT 权威维护知识卡/版本/解读/规则/证据；40 悬空引用按「有效待补/错误/作废」分类处置，不得永久豁免。
> **裁定 3（模块形态）**：批准独立、受保护的语义契约库形态；初始迁移期可用中性工作区制作候选包，满足独立 Owner/三方评审/零依赖/独立构建发布/不随 KERT 节奏变更五条件前不得标记公共权威版本。
> **决议 4（总体）**：□ 批准设计基线（`DESIGN_APPROVED`）并开放实施入口 □ 附条件批准 □ 退回。**本决议不构成实现完成、QA 通过、Owner 激活或生产可用证明**；`IMPLEMENTED`/`QA_PASS`/`OWNER_ACTIVATED` 另设门禁。

## 附件三：消费者影响清单（初版，SYSTEM_OBSERVATION，待 Wave -1 全量扫描）

| 类别 | 已知命中（勘探发现） | 处置要求 |
|---|---|---|
| KERT 硬编码地图 ID | `skills.py:1005-1170`（7 个字面量 mapId）；`skills.py:272-283`（技能注册表）；`sp15_skill.py:60-63`；`service_proposal.py:30` | Wave 3 退出门禁：全部转为控制面读取或登记豁免 |
| KERT 硬编码 KI 清单 | `customer_knowledge.py:21-27`；供应链路径 `KI-FRONT-001/002/003` 未接计划门禁 | 同上 |
| 命名三套 | bank-front-\* / skill-customer-\* / SP-\*；SKILL_ID_RE 放宽处（`knowledge_map.py:55-60`） | 影响扫描登记；统一命名后续立项 |
| GITS 消费链 | `KnowledgeArchitectureConfig.java:167-171` → `JenaOntologyAdapter` → `DefaultActivationPlanner.versions.ontology` | 换向 + plan hash 子块验证 |
| 钉值方 | KERT `ontology_reference.json`、`PROVENANCE.json`、`ontology_assets.py` role 枚举 | 重钉 + role 扩展 |
| 生成目标 | `generated/semantic/gits-core.*`；CONTRACT_INDEX `CTR-SEM-001/002`（:646-650 消费者） | 拆条登记 + 独立目标 |
| 旧 IRI | 全量 `gits:` 引用（`owl:imports`、实例文件 `products.ttl:1` 前缀、R2RML 映射） | LEGACY 映射 + 碰撞检查 |
| 残留表述 | KERT `ontology_reference.py:1`、`knowledge_map.py:30`、`knowledge_source.py:64`「依据 D3-A」 | 改写为现行决策 |
