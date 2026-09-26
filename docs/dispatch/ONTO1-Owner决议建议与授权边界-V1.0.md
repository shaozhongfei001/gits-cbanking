# ONTO1 本体四层拆分｜Owner 决议建议与授权边界 V1.0

| 项 | 内容 |
|---|---|
| 审阅对象 | `ONTO1-Owner审核总清单与证据包-V1.0.md` |
| 输入 SHA-256 | `846f10bb5099d52ac5b91be8d663cd5ff97bb886d2786839bf0a3aa38da6c5e1` |
| 决策角色 | 项目 Owner 的个人本体论解决方案顾问 |
| 形成日期 | 2026-09-20 |
| 文书性质 | Owner 决议建议稿；经人类 Owner 明确确认后生效 |

```text
DECISION_PACKAGE_STATUS=READY_FOR_HUMAN_OWNER_CONFIRMATION
PROJECT_GATE=RETURN_TO_HLD
DESIGN_APPROVED=NO
WAVE_0_STARTED=NO
INDEPENDENT_QA=PENDING
INDEPENDENT_QA_ACTOR=NULL
KNOWN_GATE_RESULT=30_PASS_1_FAIL
KNOWN_FAIL=wi_a4_namespace_collision/C-2
```

## 一、Owner 总体决定

不作“一揽子全部批准”。采用以下原则：

1. 可以安全启动且不会制造未经授权权威事实的事项，立即批准；
2. 可以先确定架构方向、但仍需外部 Owner 或逐条证据的事项，附条件批准；
3. 涉及产品语义真实性、正式根域、正式银行源系统或委员会签署的事项，不凭项目摘要代签；
4. 自检通过不等于独立 QA，通过 30 项门禁也不改变当前 `RETURN_TO_HLD`；
5. SIM 决策只对模拟试点有效，不得外推为银行正式口径、生产权威或生产写回许可。

本建议稿形成 13 项 Owner 决定。人类 Owner 确认后，可立即生效的范围是：书面复审发起授权、两个临时 Owner 任命、SIM 临时权威路线、外部标识模型演进路线、保守映射政策和 Wave -1 治理政策。Wave 0 仍须等待委员会有效签署页。

## 二、逐项决议

### O-01｜C-1-a~e 委员会书面复审

**结论：`APPROVED_WITH_CONDITIONS`。批准发起书面复审，但不等于复审通过。**

批准内容：

- 批准使用 13 号送审函、14 号决议签署页和 V1.1 自含包发起书面复审；
- 批准目标回收日为 **2026-10-09**；
- 批准秘书处按结论回收预案进行七项有效性检查；
- 只有 `SENT_PACKAGE_IDENTICAL`、包检查 exit=0、签署页有效且无未关闭 BLOCKER，才能更新门禁。

评审组成采用四个角色，不虚构具体姓名：

| 角色 | 最低职责 |
|---|---|
| 委员会主席 | 主持门禁、确认结论与生效范围 |
| 本体/语义架构委员 | 核对四层归属、IRI、映射与语义兼容性 |
| 数据治理委员 | 核对 A-Box 权威、SourceIdentifier、投影和时点 |
| 集成架构委员 | 核对 L4 合同、消费者影响和迁移/回滚 |
| 秘书处/TL | 仅分发、汇总和校验，不投票、不代签 |

生效条件：人类 Owner 填入具名人员和渠道；至少主席与两名领域委员形成有效意见；任何委员提出未关闭 BLOCKER 时维持 `RETURN_TO_HLD`。

### O-02｜A-1 公共语义 Owner 任命

**结论：`APPROVED`。由项目 Owner（邵钟飞）临时兼任 Public Semantic Owner。**

授权范围：

- L1 公共业务语义核心候选定义、术语准入和兼容性裁定；
- 命名空间 ADR 的语义侧联签；
- CQ1/CQ2 的语义验收责任；
- D-4/D-5 的逐项映射判断。

限制：不得以该身份代替委员会、域名 Owner、Data Owner、产品 Owner或独立 QA；不得独自把候选资产标记为 `ACTIVE`。任期至正式角色任命或本项目 `OWNER_ACTIVATED`，以较早者为准。

### O-03｜A-2 Integration Contract Owner 任命

**结论：`APPROVED`。由项目 Owner（邵钟飞）临时兼任 Integration Contract Owner。**

授权范围：L4 注册表、JSON Schema/LinkML 合同、版本兼容政策、三方评审召集、CQ4/CQ5 合同验收。

隔离要求：同一人可以在试点期临时承担 A-1/A-2，但逻辑职责、决策记录和制品版本必须分开；本人不得充当独立 QA，也不得在自己作为实现作者时单人批准合并。

### O-04｜TaskTypeScheme 词表 Owner

**结论：`APPROVED`。采用“双责任、单语义 Owner”模式。**

- Public Semantic Owner 负责 `TaskTypeScheme` 的含义、层级、代码弃用和映射；
- Integration Contract Owner 负责在注册表、Schema 和运行接口中的序列化与消费约束；
- 语义冲突以 Public Semantic Owner 的受控词表版本为准，接口不得反向改写词义。

### O-05｜D3 中立 IRI 根域与解析端点

**结论：`APPROVED_WITH_CONDITIONS`。批准政策，不批准具体根域字面量。Wave 2 继续阻塞。**

批准的强制政策：

- 使用机构控制、与 GITS/KERT/仓库/供应商无关的 HTTPS 中立域；
- ontology IRI 稳定，version IRI 指向不可变版本；
- 解析端点支持人类说明与 Turtle/JSON-LD 内容协商；
- 旧 `gits:` IRI 标记 `LEGACY`，通过显式映射和退役窗口迁移；
- `latest` 可作导航，不得作为生产钉值；生产消费必须固定 version IRI 与内容哈希；
- 禁止 `bank.example` 等占位值进入正式制品。

建议结构仅作 ADR 模板，不构成域名批准：

```text
ontology IRI: https://ontology.<approved-enterprise-domain>/gk-ke/core
version IRI:  https://ontology.<approved-enterprise-domain>/gk-ke/core/v/<semver>
term base:    https://ontology.<approved-enterprise-domain>/gk-ke/core/term/
```

解除阻塞仍需语义架构 Owner 与域名/基础设施 Owner 对真实根域、DNS/HTTPS 控制、解析机制和持久性承诺联签。

### O-06｜D2 产品关系 40 处悬空引用

**结论：`RETURNED_FOR_ITEMIZED_PRODUCT_DECISION`。不代替产品 Owner 猜测。**

立即生效的安全处置：

- 40 处关系全部进入 `QUARANTINED_UNRESOLVED` 生命周期状态，不赋予“有效待补/错误/作废”任何最终语义；
- 不进入 ACTIVE 产品关系图，不参与推荐、资格判断或 GraphRAG 事实回答；
- CQ3 保持 `NOT_EVALUATED`；
- 可以另建明确标识为 SIM 的正负夹具验证引擎，但夹具通过不等于 40 条内容获批；
- 产品 Owner 必须按逐条证据完成三分类后，才可解除内容阻塞。

这是有意保留的 P1 阻塞，不以推进速度换取错误产品事实。

### O-07｜D4 A-Box 权威与 SIM 临时路线

**结论：`APPROVED_WITH_CONDITIONS`。选择“先签 SIM 临时声明”，不直接签生产正式矩阵。**

批准以下临时模拟权威，仅供本试点：

| 对象 | SIM 临时权威数据产品 | 说明 |
|---|---|---|
| Party / Organization / LegalEntity / CustomerRole | `SIM-CUSTOMER-MASTER` | 模拟客户与主体身份快照 |
| EnterpriseGroup / GroupMembership | `SIM-GROUP-REGISTRY` | 模拟集团身份和带有效期成员关系 |
| ProductOffering | `SIM-PRODUCT-CATALOG` | 模拟产品身份；产品关系仍受 O-06 隔离 |
| SourceIdentifier | 随上述三个数据产品生成 | 只表达来源标识与授权，不另建业务真相 |

`SourceIdentifier` 批准六个必填字段：

1. `sourceSystemId`
2. `sourceObjectType`
3. `sourceRecordId`
4. `sourceVersion`
5. `observedAt`
6. `authorizationBasis`

对象或关系的 `effectiveFrom/effectiveTo` 属业务有效期，不塞入 SourceIdentifier 替代业务时间语义。缺少任一必填字段时具名拒绝 `MISSING_SOURCE_IDENTIFIER`。

投影 freshness 在 SIM 中相对 `scenarioAsOf` 判断，不以机器当前时间破坏可重复测试：

| 对象 | 最大允许年龄 |
|---|---:|
| Party / CustomerRole | 24 小时 |
| Organization / LegalEntity | 7 天 |
| EnterpriseGroup / GroupMembership | 7 天 |
| ProductOffering | 24 小时 |

投影合同授权范围为 `simulationOnly=true`、无生产写回、无正式银行权威声明。合同只有在 Schema 校验、正负夹具、来源/时点/版本校验和独立 QA 完成后才能生效；当前仍为 `NOT_EFFECTIVE`。

### O-08｜C-2 / O-D4-2 外部标识模型出口

**结论：`APPROVED`，选择“B 过渡 → A 目标”。**

过渡期：

- L1 `SourceIdentifier` 与既有 `core.ExternalIdentifier` 暂时并存；
- L4 登记显式映射合同和字段完备性门禁；
- 缺少 `sourceVersion`、`observedAt` 或 `authorizationBasis` 的旧记录只能标记为 `PARTIAL_MAPPING`，不得伪装为完整映射；
- C-2 碰撞未关闭前，CQ1 不得标 `PASS`。

目标态：L1 `SourceIdentifier` 是公共语义定义；`core.ExternalIdentifier` 升级为该定义的集成序列化/兼容视图并逐步退役，不再维持两套独立语义。进入目标态前必须开放 GK-KE 回归窗口并通过旧消费者兼容测试。

### O-09｜D1 GB/T 48000.3-2026 正式文本

**结论：`APPROVED`。批准获取和条款级参照对齐，但继续移出本次设计基线。**

- 目标日期保留 2026-10-09；
- 文本由标准管理员获取，Public Semantic Owner 接收；
- 未形成条款矩阵前，不发布 `REFERENCE-ALIGNMENT.md` 条款版；
- 不得使用“符合、认证、全量继承”等表述，也不得使用 `CONFORMANCE` 文件名；
- D1 不阻塞当前书面复审和 Wave -1。

### O-10｜D-4 / D-5 语义映射政策

**结论：`APPROVED`。维持保守策略。**

- `RETAINED_AUTHORITY_MOVED` 不得批量赋予 `owl:equivalentClass`；
- `REMODELED` 默认不得赋予 SKOS `exactMatch`；
- 权威主体改变本身既不能证明等价，也不能证明不等价；是否等价必须逐项比较定义、外延、约束、身份规则和时间语义；
- 证据不足时使用项目迁移状态表达，不用强语义映射掩盖不确定性；
- 任何单项放行必须有术语差异表、回归结果和 Public Semantic Owner 决议。

### O-11｜D-7 KERT 三文件历史写入

**结论：`APPROVED_WITH_CONDITIONS`。原则上追认“指针化收敛”。**

条件：

- 三个文件必须具名、给出当前哈希和历史来源；
- 历史内容只读保留，不静默删除或改写 Git 历史；
- 新版本只维护到权威制品的版本化指针/映射，不复制第二份可编辑真相；
- KERT 维护方书面确认后才解除“KERT 零新增写入”限制。

未提供三文件清单与签署回执前，本项不视为执行完成。

### O-12｜D-13 与 D-15.5：refalign 守卫和快照语义

**结论：`APPROVED_WITH_REQUIRED_CHANGES`。允许继续作为发文前语法守卫，不批准其成为永久语义真相门禁。**

对 D-13 的决定：

- 使用受控状态标记代替自由文本红线承诺是正确方向；
- 但禁止常用单字、导致 FAILURES 账本无法忠实引用历史原文，说明当前规则误报过高；
- `sha256|len` 只能证明某段字节存在，不能单独替代可读审计证据；必须同时保存 `sourceRef + commit/file hash + line/object ID + 脱敏摘要`；
- 后续应支持代码块、引用块和证据区的受控豁免，同时继续阻断发布性声明。

对 D-15.5 的决定：

- 内容变化导致 candidates/allowed 计数变化，本身不构成不一致，这一判断成立；
- 但只看 exit=0 会产生“零候选假绿”，不得作为唯一判断；
- 每次门禁报告至少固定：受检文件集哈希、脚本版本、候选数、允许数、违规数和一条必败变异用例；
- 脚本变更、受检文件集变化、候选数异常下降、出现新增违规时必须重记；普通内容增长且上述守恒量正常时可不重记基线计数。

当前 `refalign exit=0` 只证明本次自检没有命中违规，不代表架构委员会或独立 QA 通过。

### O-13｜当前门禁与 Wave 解锁

**结论：维持 `RETURN_TO_HLD`，不修改项目门禁。**

| Wave | 当前决定 | 真正解锁条件 |
|---|---|---|
| Wave -1 | 允许继续 | 只读分析、决策包、夹具与计划，不改权威制品 |
| Wave 0 | `BLOCKED` | 委员会有效签署页 14 返回并通过七项校验 |
| Wave 1 | `BLOCKED` | Wave 0 通过 + O-02/O-03 人类确认生效 |
| Wave 2 | `BLOCKED` | D3 真实根域与解析端点双 Owner 联签 |
| Wave 3 | `BLOCKED` | SIM 声明/投影合同签署并满足 QA；C-2 映射与回归关闭 |
| CQ3/产品关系激活 | `BLOCKED` | D2 逐条产品 Owner 分类 + 非零正负夹具 |
| OWNER_ACTIVATED | `BLOCKED` | 实现、独立 QA、全部必要 Owner 决议和激活签署 |

## 三、目前仍不能由本建议稿代替的签署

以下项目必须由具名人类角色或外部委员会产生权威事实：

1. 委员会评审人姓名、主席、签署页与正式结论；
2. 域名/基础设施 Owner 对真实根域、DNS、HTTPS 和持久性承诺的批准；
3. 产品 Owner 对 40 处关系引用的逐条内容判断；
4. KERT 维护方对三文件清单和指针化处置的确认；
5. 独立 QA 的 actor、会话、范围和结果；
6. 生产数据 Owner 对真实银行源系统、授权投影和 freshness 的正式确认；
7. 最终 `OWNER_ACTIVATED` 签署。

## 四、Owner 一次性确认文本

人类 Owner 如同意本建议，可使用以下文字形成正式回执：

> 我以项目 Owner 身份确认采用《ONTO1-Owner决议建议与授权边界-V1.0》中的 O-01 至 O-13。书面复审发起、临时角色任命、SIM 临时权威路线、O-D4-2“B 过渡→A 目标”、保守语义映射和守卫整改要求自签署日起生效。当前项目门禁继续保持 `RETURN_TO_HLD`；本确认不构成委员会复审通过、正式根域批准、40 条产品关系认定、独立 QA 通过、生产数据授权或 `OWNER_ACTIVATED`。
>
> 签署人：________　角色：项目 Owner　日期：________

## 五、TL 回写要求

收到人类 Owner 确认后，TL 仅可：

1. 把 O-02/O-03 写入角色板并标明 `INTERIM` 与职责隔离；
2. 把 O-04、O-08、O-10、O-12 登记为 Owner 决策；
3. 把 O-07 写入 SIM 声明和 D4 决策包，但保持 `NOT_EFFECTIVE`；
4. 发起 O-01 书面复审并归档发送/回收证据；
5. 保持 D2、D3、Wave 0~3、独立 QA 和激活门禁的真实阻塞状态；
6. 不得把本建议稿或 Owner 确认扩写为 `DESIGN_APPROVED`、`QA_PASS`、生产权威或正式银行口径。

---

**顾问判断**：Owner 侧已经具备“安全发起复审”和“建立临时治理责任”的条件，但尚不具备解除所有内容权威、命名空间和外部签署阻塞的条件。最合理的选择是分层授权，而不是为了让 Wave 前进而一次性代签所有未决事项。
