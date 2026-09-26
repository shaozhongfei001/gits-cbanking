# ONTO-SPLIT 本体四层落地执行计划 V2.0（全局 TL 执行版）

| 项 | 值 |
|---|---|
| 文档性质 | 落地执行计划（Dispatch），交全局 Tech Lead 编排执行 |
| 取代 | `ONTO-SPLIT-本体三分落地执行计划-V1.0.md`（SUPERSEDED：三层模型已被四层取代） |
| 设计权威 | `docs/architecture/ONTOLOGY-SPLIT-DESIGN-V2.0-REVIEW.md` + 复审包 `docs/review/ARCH-ONTO-2026-001-rereview-package/`（MANIFEST 钉值） |
| 门禁现状 | `RETURN_TO_HLD` 仍有效；书面复审已提交，目标 `DESIGN_APPROVED`（上限 `PASS_WITH_REQUIRED_CHANGES`，不含 GB/T 条款级对齐） |
| **执行边界** | **Wave -1 现在即可执行**（委员会 §7 明确允许的只读分析）；**Wave 0 及以后必须等 `DESIGN_APPROVED`**；`IMPLEMENTED`/`QA_PASS`/`OWNER_ACTIVATED` 各设独立门禁 |
| 建议 Loop ID | `ONTO1-ontology-split`（scope 更新为四层模型） |
| 建议分支 | `loop/ONTO1-ontology-split`（双仓同名；独立语义契约库另议，Wave 1） |
| 工期 | **不做承诺**（M-10）：本计划给出 WBS 结构与依赖；人日重估为 Wave -1 的 WI-A7 产出 |

---

## 0. 状态机与执行许可（TL 每日开工前核对）

```
FOR_REVIEW ──书面复审──▶ DESIGN_APPROVED ──Wave0~5──▶ IMPLEMENTED ──独立QA──▶ QA_PASS ──Owner──▶ OWNER_ACTIVATED
   ▲ 当前位置（复审中）
```

| 阶段 | 允许 | 禁止（委员会 §7 原话） |
|---|---|---|
| 现在（复审前） | Wave -1 全部：只读盘点、消费者扫描、标准核对、夹具设计、ADR 起草、WBS 重估、Owner 请求提交 | 标 DESIGN_APPROVED/FROZEN；拆分权威本体；切换消费入口；正式重钉；候选公共模块标 ACTIVE；签发国标符合性声明；把初版影响清单当全量分析；把 Owner 未决项当已关闭 |
| DESIGN_APPROVED 后 | Wave 0~5 | 跳过门禁；手改 generated/；逾越 D1~D4 未决禁止动作（复审包 11 号） |
| QA_PASS 后 | Owner 激活评审 | 开发角色自签 QA_PASS |
| OWNER_ACTIVATED | 生产启用 | — |

## 1. 角色编制（TL 首要动作：Owner 角色缺口必须先于 Wave 0 补齐）

| 角色 | 职责 | 现状 |
|---|---|---|
| 全局 Tech Lead | 编排、Baton、DEV_SELF_CHECK、证据纪律 | 已任命（接收本计划者） |
| **公共语义 Owner** | L1 定义发布、命名空间 ADR 联签 | **待 Owner 任命（缺口，阻塞 Wave 1）** |
| **Integration Contract Owner** | L4 注册表、CQ4/CQ5、三方评审召集 | **待任命（缺口）** |
| 词表 Owner | SKOS 词表（TaskTypeScheme） | 可由公共语义 Owner 兼任（待裁定） |
| Knowledge/KERT Owner | L2 元模型、CQ3 | KERT 维护方（需确认写权限与协作接口） |
| GITS Owner / Business Process Owner | L3 运行本体、CQ6 | 可由 GITS 侧资深兼任 |
| Feature Pilot | 实施 | 按 Loop 派工 |
| 独立 QA | QA_PASS、变异矩阵复核 | **必须独立于开发** |
| 外部决策方 | 产品 Owner（D2）、域名 Owner（D3）、数据 Owner（D4）、标准管理员（D1） | 见复审包 11 号登记表 |

## 2. Wave -1｜分析阶段（现在可执行；全部只读，不改权威制品）

| WI | 动作 | 产出与验收 | 依赖 |
|---|---|---|---|
| WI-A1 基线 v2 | 三仓/三制品完整哈希固定；rdflib 复现 32/34/1（复审包 12 号 §2 脚本）；按四层模型重导 `attribution.csv`（45 项机读映射，以复审包 03 号为种子） | 基线清单 v2（哈希全量）；复现输出 = 32/34/1 | 无 |
| WI-A2 消费者全量扫描 | 执行复审包 09 号 S1~S5：双仓扫描 32 类名/34 属性/`gits:` 前缀/ID 模式/文件名引用 → 命中清单 → 处置表（转控制面/跟随迁移/豁免/后续立项）→ 重钉清单 → 扫描脚本变异复验 | **命中/处置表 100% 处置 + 变异记录**；此产出是 Wave 2/3 退出门禁，**未完成则 Wave 2 禁止开工** | WI-A1 |
| WI-A3 标准矩阵（D1） | 跟催标准文本获取（目标 2026-10-09）；到手后 1 个工作日内完成条款适用性矩阵（适用/不适用+理由/项目加严/证据）→ `REFERENCE-ALIGNMENT.md` 条款版 → 单独复审（T2~T4） | 条款矩阵 + 文件哈希 + 公共语义 Owner 签署；**到手前禁止任何国标符合性表述** | D1（外部） |
| WI-A4 命名空间 ADR（D3） | ADR 成稿送双 Owner：中立持久根域、解析机制（303/离线+哈希）、oldIRI→newIRI 逐术语映射（等价规则按复审包 04-D）、LEGACY 双发布窗口、退役门、碰撞检查脚本 | 双 Owner 签署 ADR + 解析测试绿 + 碰撞检查绿；**未签前禁止发布新 IRI/重钉** | D3（外部） |
| WI-A5 Owner 请求（D2/D4） | 向产品 Owner 提交 40 悬空引用分类请求（有效待补/错误/作废）+ SIM 临时模拟权威声明草案；向数据 Owner 提交权威矩阵确认 + 投影合同草案 | 两件签署件；**未签前 CQ3/CQ1/CQ2 保持 NOT_EVALUATED，禁止标 PASS** | D2/D4（外部） |
| WI-A6 CQ 夹具包 | 按复审包 08 号设计 6 CQ ×（查询 + 正例 + 负例 + 预期 + 变异用例）机读夹具 | 夹具包 + 每 CQ 变异用例设计；进 EVIDENCE | WI-A1 |
| WI-A7 WBS 重估 | 基于 WI-A2 扫描结果重估 Wave 0~5 人日（含三仓变更、Owner 等待缓冲） | 工期表（责任人/前置/缓冲），回填本计划 §8 | WI-A2 |

**G-1（进入 Wave 0 的前置门）**：① 书面复审结论 = `DESIGN_APPROVED`（或 `PASS_WITH_REQUIRED_CHANGES` 且条件已登记）；② WI-A2/A4/A6 完成；③ D3 签署（Wave 2 硬前置）、D2/D4 已提交（激活前可后补签署，但场景保持 NOT_EVALUATED）。

## 3. Wave 0｜冻结与 Loop 骨架（DESIGN_APPROVED 后，0.5~1d，低风险）

- Loop 骨架：`loops/ONTO1-ontology-split/`（scope=四层模型，exit=G0~G6+状态机；**不做事清单** = 统一命名、种子本体对齐等后续项）；
- 基线 v2 锁定进 EVIDENCE；Wave 0 检查表（输入锚点：复审包 MANIFEST 哈希、attribution.csv、ADR 签署件；失败条件：IRI 差异、计数不符、扫描缺漏）；
- ⚠️ m-03 纪律：**低风险非零风险**——锚点核对失败即 STOP 写 BLOCKED。

## 4. Wave 1｜独立语义契约库设立（裁定 3）

| WI | 动作 | 验收（ACTIVE 五条件，委员会裁定 3） |
|---|---|---|
| WI-1-1 | 申请独立受保护仓库（语义契约库）：独立 Owner、版本线、访问控制、发布流水线 | ① 独立 Owner/版本/流水线/权限 ② GITS/KERT/数据平台三方评审规则（CODEOWNERS 或等效） ③ 零 `kert.*`/GITS 运行代码依赖 ④ 可独立构建/解析/验证/发布 ⑤ 不随 KERT 发布节奏变更 |
| WI-1-2 | 库骨架：`README`（GB/T 42131 角色声明）、`MODELING-RULES.md`（内部规则 R1~R9 修订版）、`REFERENCE-ALIGNMENT.md`（参照对齐版，**禁用 CONFORMANCE 字样**）、`namespaces.json`（D3 签署后填根域）、`VERSION`/`CHANGELOG`/`PROVENANCE.json`（`authorityEntity` + `hostingRepo` 双字段，m-02） | 骨架可构建；`make conformance` 可跑（允许红） |
| WI-1-3 | 迁移期安排：候选包在中性工作区制作；**五条件全满足前禁止标公共权威 ACTIVE 版本** | 状态登记：候选（CANDIDATE） |

## 5. Wave 2｜四层拆分（合同先行；D3 签署为硬前置；WI-A2 处置表为退出门禁）

1. **合同登记**：`CONTRACT_INDEX` 新增/拆条——`CTR-SEM-003`（L1 公共核心）、`CTR-SEM-004`（L2 KERT 元模型）、`CTR-SEM-005`（L4 注册表 Schema/SKOS）；各配**独立 generated 目标**；收窄 `CTR-SEM-002`（L3）。→ `make generate` → `make check`。
2. **拆分**：基线 32 类按复审包 04 号映射执行（保留 19 / 迁移重构 10 / 转制品 3 / 退役 0）；13 净新增按 03 号矩阵建模；属性按 04-C（36 OWL 对象属性 + 5 Schema 字段 + 1 退役）。
3. **IRI 迁移**：按 ADR 执行 oldIRI→newIRI；旧 `gits:` 置 LEGACY 只读、双发布窗口开启；碰撞检查（新旧 IRI 集合交集为空）。
4. **校验**：`onto_split_check.py`——① 基线 32 项映射覆盖率 100%（无遗漏无重复）；② 分口径计数 = 39 OWL + 1 SKOS + 5 Schema；③ 等价关系使用合规（重构项**禁止** equivalentClass）；④ **变异复验**：改一处 IRI/删一条映射 ⇒ FAIL，恢复 ⇒ PASS。
5. **Shape 场景化**：按验证场景（发布/摄取/运行）建 Shape，废止「每类一 Shape」；SHACL 由源模型生成，禁手改。

**G2**：映射覆盖 100% + 计数分口径自洽 + generate/check 绿 + 变异记录 + 处置表全处置。

## 6. Wave 3｜双侧换消费 + 原子窗口

- **KERT**：`90_control/ontology/` 改放「L1 副本 + L2 本体」；`ontology_reference.json` → `authorityEntity`（公共语义实体）+ 新钉值；`ontology_assets.py` role 扩（PUBLIC/KERT/GITS-EXTERNAL）；物化链路重跑（校验先于产出）。
- **GITS**：`gits-core.owl.ttl` → `gits-operational.owl.ttl` + `owl:imports` L1（本地副本 + **钉 versionIRI + 内容哈希**，项目加严）；`KnowledgeArchitectureConfig:167` → `JenaOntologyAdapter` → `DefaultActivationPlanner.versions.ontology` 逐环验证 plan hash 子块。
- **修复**：`products.ttl:1` 前缀对齐（解 vacuous）；D3-A 残留 3 处改写；硬编码按 WI-A2 处置表逐条处理（转控制面/豁免登记）。
- **窗口纪律**：先钉新值 → 后切消费 → 旧值只读 ≥1 验证周期；import closure 单版本检查。
- **G3**：双侧启动 + 漂移用例绿 + vacuous 消除（目标数 > 0）或 NOT_EVALUATED 登记 + 处置表零遗留 + plan hash 含新钉值。

## 7. Wave 4｜门禁与符合性（内部规则，无国标声称）

- `make conformance`（内部规则 R1~R9 修订版）：唯一 IRI/前缀白名单、R2 头元数据、Turtle+JSON-LD、场景化 Shape 覆盖、公理、**兼容性测试（07 号矩阵：旧夹具行为预测一致）**、R7 元数据、PROVENANCE + 影响面分析、versionIRI 钉值 + import closure 单版本——**输出文件一律用 REFERENCE-ALIGNMENT/内部规则名义，禁止 CONFORMANCE/国标符合性字样**。
- **六 CQ 执行**：WI-A6 夹具包上线；目标数/命中数按五态模型记录；CQ3 受 D2 硬阻塞（未签署前 NOT_EVALUATED）。
- **五态纪律接线**：WAIVED 到期检查脚本；激活门禁拒绝 WAIVED/NOT_EVALUATED。
- **全量变异回归**：所有否定式门禁 mutate→FAIL/restore→PASS 矩阵 100% 捕获。
- **G4**：内部规则全绿（或具名 NOT_EVALUATED 登记）+ 6 CQ 执行记录 + 变异矩阵 + CI 接入。

## 8. Wave 5｜契约库 ACTIVE 核验与发布演练

- ACTIVE 五条件逐条核验（WI-1-1 验收项）+ 独立打包演练（构建/解析/验证/发布全链路）+ 双仓消费方式不变验证；
- **G5**：五条件签署核验记录 + 演练产物哈希。
- **工期回填**：WI-A7 重估结果在此节更新（本版不填人日）。

## 9. G6｜IMPLEMENTED → QA_PASS → OWNER_ACTIVATED

1. **IMPLEMENTED**：G0~G5 全绿 + 证据链完整（TL 记录 DEV_SELF_CHECK_PASS）。
2. **QA_PASS**：独立 QA（session `qa-onto1-00x`）复核：32→45 映射独立复算、变异矩阵抽查非空转、6 CQ 重跑、双仓 git log 原子性、五态记录合规。**开发角色禁止自签**。
3. **OWNER_ACTIVATED**：按 Owner 分域激活——公共语义 Owner（L1）、Knowledge Owner（L2）、GITS Owner（L3）、Integration Contract Owner（L4）；**硬阻塞**：D2 签署前 CQ3 三场景不得激活（NOT_EVALUATED 不满足激活标准，06 号文件 §3）；D4 签署前投影合同不生效；SIM 临时权威声明的退出条件纳入跟踪台账。
4. Loop 关闭：GK17 `NAMESPACE_MISMATCH_SILENTLY_GREEN` 关闭；ADR-018 残留追加指针（不改历史）；后续工作八项归属建议落 NEXT_SESSION。

## 10. 回滚预案

| 场景 | 动作 |
|---|---|
| Wave 2 后 | 新制品均为增量；CONTRACT_INDEX 单提交 revert；基线 `gits-core.owl.ttl` 全程只读未改 |
| Wave 3 窗口内 | 旧钉值保留期：配置/钉值文件 git revert 单提交即回；KERT 旧副本窗口期内未删 |
| 任何不可修复态 | 双仓 revert 至 Wave 0 基线提交（哈希在 EVIDENCE）；基线 `sha256:705578d6324abd0c…` 为最终锚 |

## 11. 风险登记（V2.0 版）

| # | 风险 | 等级 | 缓解 |
|---|---|---|---|
| R-D3 | 根域/ADR 未按时签署 → Wave 2 阻塞 | 高 | WI-A4 提前送审；占位 IRI 禁止入正式制品；阻塞即 STOP 写 BLOCKED |
| R-D2 | 产品 Owner 分类延迟 → CQ3/激活阻塞 | 高 | 草案先行（WI-A5）；激活门禁硬阻塞设计（不依赖豁免） |
| R-D4 | 数据 Owner 确认延迟 → 投影合同阻塞 | 中 | SIM 临时权威声明含退出条件，先签声明后补确认 |
| R-D1 | 标准文本延迟 → 条款矩阵延后 | 低（已移出基线） | T2~T4 单独门禁，不阻塞主链路 |
| R-SCAN | 消费者扫描漏项 → 拆分后旧引用残留 | 高 | WI-A2 变异复验 + Wave 2/3 退出门禁双保险 |
| R-PRIV | 公共层私有化 | 中（裁定 3 已结构性消解大半） | 独立契约库五条件 + 三方评审 + authorityEntity/hostingRepo 分离 |
| R-OWNER | 新 Owner 角色任命延迟 | 高 | §1 缺口清单先行；未任命前 Wave 1 不开工 |

## 12. TL Day-1 开工检查单（现在即可执行）

```
[ ] 确认门禁状态：RETURN_TO_HLD 有效 → 只排 Wave -1；复审结论到达后更新
[ ] 双仓 git status 干净；建 loop/ONTO1-ontology-split 分支（只读分析可先在 worktree）
[ ] Loop 骨架 loops/ONTO1-ontology-split/ 建立；baton=tech_lead；不做事清单已写
[ ] WI-A1 启动：基线哈希 + rdflib 复现 32/34/1 + attribution.csv（以复审包 03 号为种子）
[ ] WI-A5 发出：D2 产品 Owner / D4 数据 Owner 请求函（附 SIM 临时权威声明草案）
[ ] WI-A4 启动：命名空间 ADR 起草（不预填根域）
[ ] WI-A3 跟催：标准文本获取（目标 2026-10-09）；期间零国标符合性表述
[ ] 角色缺口上报：公共语义 Owner / Integration Contract Owner 任命请求
[开工] Loop: ONTO1-ontology-split, 阶段: Wave -1(只读分析), Baton: tech_lead, Gate: G-1 前置
```

---

> 本计划与设计 V2.0、复审包为执行-设计-证据三配对文档：口径冲突以设计 V2.0（DESIGN_APPROVED 后为基线）为准；执行中发现的设计缺陷回写设计修订，不得在代码里绕开。
