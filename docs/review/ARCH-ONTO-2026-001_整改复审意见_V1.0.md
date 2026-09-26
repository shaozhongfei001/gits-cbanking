# ARCH-ONTO-2026-001 整改复审意见 V1.0

| 项 | 内容 |
|---|---|
| 复审对象 | `ARCH-ONTO-2026-001_整改处置报告-V1.0.md` |
| 报告 SHA-256 | `07a90be2d3a8332f796d54da836a5d31ad838301c85aa9baefa2bcaf3263d665` |
| 被引用主设计 | `ONTOLOGY-SPLIT-DESIGN-V2.0-REVIEW.md` |
| 复审日期 | 2026-09-20 |
| 复审角色 | 架构委员会架构师 |
| 原门禁 | `RETURN_TO_HLD` |

```text
GATE_DECISION=INSUFFICIENT_EVIDENCE
REVIEW_OBJECT=ARCH-ONTO-2026-001 整改关闭申请
TARGET_TRANSITION=RETURN_TO_HLD → DESIGN_APPROVED / PASS_FOR_OWNER_REVIEW
SUBSTANTIVE_REVIEW=PARTIAL
REMEDIATION_DIRECTION_REVIEW=COMPLETE
PRIMARY_ARTIFACT_VERIFICATION=NOT_STARTED
BASELINE_STATE=RETURNED
FROZEN=NO
```

## 一、复审结论

整改方向与架构委员会原意见高度一致，未发现新的原则性争议；采用四层模型、纠正业务真相边界、撤回“权威循环”、区分 OWL/SKOS/执行合同、将国标降级为参照对齐、拆分设计/实现/QA/激活状态，均是正确处置方向。

但本次不能确认“整改关闭”，门禁结论为 **`INSUFFICIENT_EVIDENCE`**。原因不是整改方向错误，而是本次只提供了 80 行的处置索引，16 项整改证据几乎全部指向未随复审材料提供、且无法定位的 `ONTOLOGY-SPLIT-DESIGN-V2.0-REVIEW.md`。委员会不能根据作者自述把 `CLOSED-DESIGN` 自动转写为委员会确认关闭。

因此：

- 原 `RETURN_TO_HLD` 继续有效；
- 不批准 `DESIGN_APPROVED`；
- 不开放本体拆分、消费者切换、重钉和正式发布；
- Wave -1 的只读盘点、标准核对、夹具设计、ADR 起草和 WBS 重估可以继续；
- 资料补齐后适合采用书面复审，无需重新举行完整方案讨论。

## 二、整改方向评价

| 范围 | 方向判断 | 说明 |
|---|---|---|
| B-01 四层重构 | 认可 | 公共业务语义、KERT 知识元模型、GITS 运行本体、集成契约注册表与 SKOS 分离，修复了原公共层过宽问题。 |
| B-02 真相边界 | 认可 | 银行源系统/数据平台承担客户、法人、集团、产品身份 A-Box 权威，符合项目总边界。 |
| B-03 状态机 | 认可 | `DESIGN_APPROVED → IMPLEMENTED → QA_PASS → OWNER_ACTIVATED` 清除了状态夸大。 |
| M-01 权威循环 | 认可 | 撤回原论断，改用六列权威与发布依赖分析，理论上正确。 |
| M-02 标准定位 | 认可 | “参照对齐”与内部工程控制分离，避免虚假符合性。 |
| M-03 验证状态 | 认可 | 豁免不满足激活门禁，零实例不再包装成通过。 |
| M-04 中立 IRI | 认可 | 中立命名空间、LEGACY 映射、退役窗口是正确迁移模式。 |
| M-05 消费者影响 | 认可但未完成 | 把全量扫描纳入退出门禁正确；初版清单不能替代正式扫描。 |
| M-06 制品分工 | 认可 | TaskType→SKOS、执行合同→JSON Schema/LinkML，符合治理对象差异。 |
| M-07 语义质量 | 认可但待证 | 六类 CQ 方向正确，仍需正文矩阵和正负夹具证据。 |
| M-08 证据分级 | 认可但待证 | 需看到重标后的证据账本、哈希和复现命令。 |
| M-09 兼容性 | 认可但待证 | 需审阅 major/minor/patch 判定矩阵及例外。 |
| M-10 工期 | 认可 | 撤回 7.5 人日承诺并重估是正确处理。 |

以上“认可”仅表示整改方案方向符合委员会意见，不等于相应设计文本已被核验。

## 三、十项关闭条件的复审状态

| # | 关闭条件 | 处置报告自评 | 委员会本轮验证状态 | 判断依据 |
|---|---|---|---|---|
| 1 | 逐术语权威矩阵 | CLOSED-DESIGN | `INSUFFICIENT_EVIDENCE` | V2.0 附录 A 和所称 22 字段机读文件均未提交。 |
| 2 | 四层目标模型 | CLOSED-DESIGN | `INSUFFICIENT_EVIDENCE` | 仅有数量和分类摘要，无法核对 32→45 的逐项映射及互斥性。 |
| 3 | 业务真相边界 | CLOSED-DESIGN + Owner 阻塞 | `PARTIAL / OWNER_PENDING` | 原则已纠正，但具体源系统、数据产品、ID 和 Data Owner 尚未确认。 |
| 4 | Product 模式闭合 | CLOSED-DESIGN + Owner 阻塞 | `PARTIAL / OWNER_PENDING` | 模式方向合理；40 个悬空引用尚未分类，不能称“闭合”。 |
| 5 | 命名空间 ADR | CLOSED-DESIGN + 根域阻塞 | `PARTIAL / DECISION_PENDING` | 框架可接受；根域、权威解析端点和批准记录未形成。 |
| 6 | 标准适用性矩阵 | BLOCKED-EXTERNAL | `OPEN` | 条款级矩阵明确未完成。 |
| 7 | 验证状态模型 | CLOSED-DESIGN | `INSUFFICIENT_EVIDENCE` | V2.0 §6.1 未提交，无法核对五态定义、跃迁和门禁逻辑。 |
| 8 | 消费者影响清单 | CLOSED-DESIGN + DEFERRED | `OPEN / DEFERRED-WORK` | 附件三明确标注“初版、待全量扫描”；不满足原关闭条件。 |
| 9 | 语义验收矩阵 | CLOSED-DESIGN + 夹具延后 | `PARTIAL / DEFERRED-WORK` | 六个 CQ 名称可见，但查询、正例、负例、预期结果和 Owner 未提供。 |
| 10 | 新决议页 | CLOSED-DESIGN | `VERIFIED_IN_REPORT` | 附件二可直接检查，且正确区分了四个状态。 |

基于本轮实际可检查材料，不能表述为“9/10 已关闭”。更准确的状态是：

- 1/10 可直接核验完成（条件 10）；
- 4/10 方向部分完成或等待 Owner/后续设计证据（条件 3、4、5、9）；
- 2/10 明确仍在工作中（条件 6、8）；
- 3/10 因主设计或附件缺失而证据不足（条件 1、2、7）。

这只是“复审证据状态”，不否认实际仓库中可能已经完成相应内容。

## 四、处置报告自身需要修正的状态问题

### 4.1 `CLOSED-DESIGN` 不能同时带有未完成的关闭证据

条件 8 写为 `CLOSED-DESIGN + DEFERRED-WORK`，但原关闭条件要求的是消费者影响清单，而报告明确承认全量扫描尚未完成。此项应改为 `IN_PROGRESS` 或 `EVIDENCE_PENDING`。

条件 9 若只完成 CQ 标题、夹具和查询仍待设计，也只能标记 `PARTIAL`。条件 3、4、5 可标记“架构方向关闭、权威决定待定”，但不得将具体映射或正式发布状态标为关闭。

### 4.2 `BLOCKED-EXTERNAL` 必须说明阻塞权威和解除证据

外部依赖不是天然免责项。每项至少应登记：

- 决策 Owner；
- 已提交的决策对象和版本；
- 请求日期与目标日期；
- 未决期间禁止的动作；
- 解除阻塞所需签署或文件哈希。

正式标准文本、产品 Owner、域名 Owner、Data Owner 应分别登记，不使用一个笼统状态覆盖。

### 4.3 45 项计数需要重新说明口径

报告写“19+8+12+6=45”，但 L4 的 6 项被定义为 JSON Schema/LinkML 注册表对象，不再是 OWL 类。因此应分别给出：

- OWL 类数量；
- SKOS ConceptScheme/Concept 数量；
- 集成契约 Schema 数量；
- 原 32 个 OWL 类的保留、迁移、重构、退役和映射结果。

不能把不同制品类型简单相加后称为“45 个本体类”或“45 项同口径目标”。

## 五、补充复审包的最小要求

请提交一个自含复审包，委员会仍无需访问代码仓库。最少包含：

1. `ONTOLOGY-SPLIT-DESIGN-V2.0-REVIEW.md` 正文；
2. 本整改处置报告的修订版；
3. 45 项逐术语、22 字段权威矩阵机读文件；
4. 32 基线项到目标制品的逐项映射表，区分 OWL/SKOS/Schema；
5. 六列权威与发布依赖表；
6. 五态验证模型与状态跃迁表；
7. major/minor/patch 兼容性矩阵；
8. 六个 competency questions 的查询、正例、负例、预期结果和 Owner；
9. 消费者影响清单正式版，或明确标为复审后实施前门禁而不声称关闭；
10. `REFERENCE-ALIGNMENT.md` 条款矩阵，或正式将国标条款级对齐移出本次 `DESIGN_APPROVED` 范围；
11. 外部依赖登记表；
12. `MANIFEST`：文件名、版本、SHA-256、状态、取代关系和权威顺序。

若标准全文仍未获得，可选择以下两条路线之一：

- **严格关闭路线**：完成条款级矩阵后申请 `PASS_FOR_OWNER_REVIEW`；
- **缩小批准范围路线**：将 GB/T 条款级对齐明确移出本次设计基线，仅批准 GK-KE 内部建模规范，门禁最多为 `PASS_WITH_REQUIRED_CHANGES`，且禁止任何国标符合性声明。

## 六、书面复审是否可行

**可行。** 当前整改没有引入新的业务范围，也没有推翻委员会已给方向。补齐第五节的自含材料后，书面复审重点只需完成：

1. 逐项核对 16 个缺陷的“原文修改—关闭证据”；
2. 核对 32→目标资产的口径与映射；
3. 核对状态、外部依赖和禁止动作；
4. 形成 `PASS_FOR_OWNER_REVIEW`、`PASS_WITH_REQUIRED_CHANGES` 或继续退回的正式结论。

## 七、下一步允许与禁止事项

### 允许

- 继续 Wave -1 的只读分析；
- 完成消费者扫描、CQ 夹具设计、标准矩阵、命名空间 ADR 和 WBS；
- 补齐自含复审包并提交书面复审。

### 禁止

- 将 V2.0 标记为 `DESIGN_APPROVED` 或 FROZEN；
- 启动本体拆分、消费切换、正式重钉；
- 把初版影响清单当作全量影响分析；
- 将 Owner 未决项或 `BLOCKED-EXTERNAL` 当作已关闭；
- 宣称实现完成、QA 通过、Owner 激活、生产可用或符合 GB/T 48000.3-2026。

---

**复审意见**：整改方向通过预审，整改关闭证据不足。补齐自含复审包后，可直接进入书面实质复审，无需重新解释原方案背景。
