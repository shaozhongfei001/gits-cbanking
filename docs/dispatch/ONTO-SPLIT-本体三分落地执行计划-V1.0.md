# ONTO-SPLIT 本体三分落地执行计划 V1.0（TL 执行版）

| 项 | 值 |
|---|---|
| 文档性质 | 落地执行计划（Dispatch），交 Tech Lead 编排执行 |
| **当前状态** | **SUPERSEDED**：三层模型已被委员会退回（RETURN_TO_HLD），由 `ONTO-SPLIT-本体四层落地执行计划-V2.0.md`（四层模型 + Wave -1 分析阶段 + 状态机门禁）取代 |
| 设计权威 | `docs/architecture/ONTO-SPLIT-DESIGN-V1.2-REVIEW.md`（ARCH-ONTO-2026-001，下称「V1.2 设计」） |
| 日期 | 2026-09-20 |
| 建议 Loop ID | `ONTO1-ontology-split`（新建，独立于 GK17/GK-KE 系列） |
| 建议分支 | `loop/ONTO1-ontology-split`（双仓同名分支：gits-cbanking + Leibniz-KERT） |
| 总工期 | 约 7.5 人日（量级估算，非承诺）+ 评审/QA 等待 |
| 前置硬条件 | 架构委员会对 V1.2 §11 三项裁定完成（本计划按推荐口径编写：命名空间沿用 / `Product` 入公共 / repo 内目录）；**未裁定前仅可执行 Wave 0 的 WI-00-1/2** |

---

## 0. 执行总则（TL 必读）

1. **角色纪律**：TL 编排 + 记录 DEV_SELF_CHECK；Feature Pilot 实施；**独立 QA 记录 QA_PASS（开发角色禁止自签）**；Owner/委员会裁定与激活。Baton 流转：`tech_lead → feature_pilot → independent_qa → owner_review`，每 Wave 一交接，落 `memory/NEXT_SESSION.md` + `ROLE_BOARD.yaml`。
2. **合同先行（P4）**：任何制品变更前先改 `specs/CONTRACT_INDEX.yaml` 登记 → `make generate` → `make check` → 再写实现。**禁止手改 `generated/`**。
3. **防"假绿"（本仓血泪教训）**：所有否定式断言门禁（拒绝、白名单、vacuous）必须满足三件套——**单一真值函数 + fail-closed（缺夹具即失败）+ 变异复验（mutate→FAIL / restore→PASS）**。每个门禁脚本配正例+负例夹具，每个 Wave 收工跑变异回归。
4. **证据纪律**：结论回源 `文件:行`；每 Wave 收工更新 `loops/ONTO1-ontology-split/EVIDENCE.md` + `STATE.json`；失败先记 `FAILURES.md` 再修复；**禁止 `git add .`**；`docs/dd/` 下未跟踪文件勿误纳。
5. **双仓变更同步**：同一 Wave 的 GITS/KERT 两侧提交必须同窗口完成（先钉新值、后切消费、旧钉值保留只读一个窗口期）。
6. **停止条件（任一即 STOP，写 `memory/BLOCKED.md`）**：① 委员会裁定与本计划假设冲突；② IRI 集合比对出现非预期差异；③ `make check` 漂移无法当日修复；④ KERT 仓写权限/协作方阻塞；⑤ 发现 32 类基线计数与实测不符（说明基线已漂移，须重锚）。

---

## 1. Baton 与交付物总览

| Wave | 内容 | 执行 | 工期 | 关键交付物 | 门禁 |
|---|---|---|---|---|---|
| 0 | 冻结与建表 | TL | 0.5d | 基线清单 + Loop 骨架 + 国标原文复核 | G0 |
| 1 | 公共模块骨架 | FP | 1d | KERT `public-ontology/` 全结构 + 共审配置 | G1 |
| 2 | 三分本体（IRI 不变） | FP | 2d | 三份 OWL/LinkML 源 + 三份生成 SHACL | G2 |
| 3 | 双侧换消费 + 命名空间修复 | FP | 2d | 双仓消费切换 + vacuous 消除/豁免登记 | G3 |
| 4 | 门禁与符合性 | FP→QA | 1.5d | R1~R9 符合性脚本 + CI + 影响面分析 | G4 |
| 5 | 剥离演练 | TL | 0.5d | subtree split 演练记录 + 零依赖证明 | G5 |
| — | 独立 QA + 委员会冻结 | QA/Owner | — | QA_PASS + V2.0 APPROVED | G6 |

---

## 2. Wave 0｜冻结与建表（TL，0.5d）

> 本 Wave 不依赖委员会裁定，可立即执行（WI-00-3 除外）。

| WI | 动作 | 验收 |
|---|---|---|
| WI-00-1 | 记录基线：rdflib 解析 `specs/semantic/gits-core.owl.ttl`，导出类/属性清单 CSV（32 类 / 34 对象属性 / 1 数据属性），记 `sha256:705578d6324a…` 全文哈希；按 V1.2 附录 A 生成机读三分表 `loops/ONTO1-ontology-split/baseline/attribution.csv`（类名,归属,判据） | 计数 = 32/34/1；三分表 19+2+11 核算通过；**核实 V1.2 附录 C-4 两口径**（28+14+55 vs ~104+53）并写结论 |
| WI-00-2 | 获取 GB/T 48000.3-2026 **正式文本**，逐条复核 V1.2 §7.3 R1~R9 映射，产出条款对照表；同步核实 GB/T 48000.1/42131/45628/42777/45288.1 引用信息 | 对照表落 `baseline/gbt48000-3-clause-map.md`；不一致处标黄待委员会知悉 |
| WI-00-3 | 建 Loop：`loops/ONTO1-ontology-split/{LOOP.yaml,STATE.json,EVIDENCE.md,memory/}`；scope 锁定 V1.2 §4~§6，exit criteria = G0~G6；写清**不做事清单**（V1.2 §13 八项后续工作不在本 Loop） | `loop_guard` 通过；holder=tech_lead |

**G0 判据**：基线文件齐备且计数自洽；`git status` 干净提交；开工声明含 INDEX_FRESH/STALE 声明。

---

## 3. Wave 1｜建公共模块骨架（FP，1d）· KERT 仓

| WI | 动作 | 验收 |
|---|---|---|
| WI-01-1 | 在 KERT 仓根建 `public-ontology/`（V1.2 §6.3 结构）：`README.md`（含 GB/T 42131 角色声明：供应方=本模块/集成方=GITS·KERT/用户=业务）、`MODELING-RULES.md`（R1~R9 全文）、`ONTOLOGY-CONFORMANCE.md`（适用边界 + 继承/不继承声明 + 豁免登记表空表）、`VERSION`(0.1.0)、`CHANGELOG.md`、`namespaces.json`（前缀 + ID 空间白名单：公共 ID 仅 KM-\*/AC-\*/ASSET-\*/SP-\*/PROD-\* 及客户域；**显式排除 KERT 私有 KS-\*/HG-\*/SQ-\***）、`src/`（空骨架 IRI）、`build/export-jsonld.py`、`Makefile`、`PROVENANCE.json` | 目录与 V1.2 §6.3 逐项一致；`namespaces.json` 含私有 ID 排除段 |
| WI-01-2 | KERT `.github/CODEOWNERS`（或等效）登记：`/public-ontology/` 须 GITS 侧 + KERT 侧 Owner 双签 | 配置生效（提一个测试 PR 验证双签拦截，或用分支保护规则截图存证） |
| WI-01-3 | `public-ontology/Makefile` 实现 `make conformance` 入口（调 R1~R9 脚本，此时脚本可为 stub） | `make conformance` 可跑（允许红），退出码非零即红 |

**G1 判据**：骨架齐备；共审生效；conformance 可执行。Baton 交 `feature_pilot` 续 Wave 2（同角色可连续持棒，但须落 NEXT_SESSION）。

---

## 4. Wave 2｜拆分三份本体（FP，2d）· 双仓，IRI 保持不变

> **顺序铁律（P4）**：先登记合同 → 改源 → generate → check → 验证。

| WI | 动作 | 验收 |
|---|---|---|
| WI-02-1 | GITS `specs/CONTRACT_INDEX.yaml`：新增 `CTR-SEM-003`（公共本体，kind=owl，**独立 generated 目标** `generated/semantic/public-kno.*`，不得复用/覆盖 `gits-core.*` 目标）；收窄 `CTR-SEM-002` 描述为「GITS 运营本体」 | `make generate` 成功；`make check` 无漂移；新旧 generated 制品并存 |
| WI-02-2 | 拆分源文件（**禁手改 generated/**）：① 从 `specs/semantic/gits-core.linkml.yaml` + `gits-core.owl.ttl` 抽 11 类+9 属性+`customerId` → KERT `public-ontology/src/public-kno.owl.ttl`（+ LinkML 源）；② 抽 2 类+6 属性 → KERT `kert-product-knowledge.owl.ttl`（建议落 `public-ontology/` 之外的 KERT 域位置，如 `src/kert/domain/ontology/` 或 `specs/`，由 TL 定）；③ 余 19 类+19 属性 → GITS `specs/semantic/gits-operational.owl.ttl`（**保留 `gits-core.owl.ttl` 原文件至 Wave 3 切换完成，只读**） | 每类带 R7 元数据（label/comment/定义来源/ID 空间/权威源/生命周期） |
| WI-02-3 | 写校验脚本 `scripts/onto_split_check.py`：① 三份 TTL 的 IRI 集合并集 == 基线 IRI 集合（**集合相等，无一变更**）；② 计数 = 11+2+19 类 / 9+6+19 属性 / 1 数据属性；③ 无重复 IRI；fail-closed | 脚本绿；**变异复验**：手工改一个 IRI → 脚本必须 FAIL；恢复 → PASS（记录于 EVIDENCE） |
| WI-02-4 | `make generate` 产出三份 SHACL（32 → 11/2/19）；写 Shape↔类一致性检查（每类一份 NodeShape，类清单↔Shape 清单集合相等） | 三份 Shape 计数正确；一致性检查绿 |

**G2 判据**：IRI 集合相等 + 计数自洽 + generate/check 全绿 + 变异复验记录。**风险预案**：若 `make generate` 因登记格式问题失败，先查 `scripts/contract_pipeline.py` 登记驱动的字段要求（硬要求 OpenAPI 3.1.1 之类的格式约束曾有先例），修复记 FAILURES.md。

---

## 5. Wave 3｜双侧换消费 + 命名空间修复（FP，2d）· 原子变更窗口

> **窗口纪律**：先钉新值 → 再切消费 → 旧钉值保留只读 ≥1 个验证周期；本 Wave 与 Wave 2 的合并在同一变更窗口内完成（V1.2 §10）。

| WI | 动作 | 验收 |
|---|---|---|
| WI-03-1 | **KERT 侧**：`examples/bank-front-knowledge-maps/90_control/ontology/` 改放「公共模块副本 + KERT 本体」+ 新 `PROVENANCE.json`（逐件 sha256）；`90_control/schema/ontology_reference.json` 改 `authorityRepo: Leibniz-KERT`、`authoritySource: public-ontology/src/public-kno.owl.ttl`；`src/kert/domain/ontology_assets.py` 的 role 枚举从 4 扩为（OWL→PUBLIC / KERT / GITS-EXTERNAL 等新角色集，保持旧值兼容读取一个窗口期） | KERT 侧物化链路（`ontology_materialize.py`）跑通；漂移用例绿（改一字节 → 具名拒绝 `ONTOLOGY_ASSET_DRIFT`） |
| WI-03-2 | **GITS 侧**：`specs/semantic/gits-core.owl.ttl` 切换为 `gits-operational.owl.ttl` + `owl:imports` 公共模块（本地副本放 `specs/semantic/imported/public-kno.owl.ttl` + 钉 **versionIRI**，R9）；`apps/api/.../KnowledgeArchitectureConfig.java:167-171` 改指向；验证消费链 `JenaOntologyAdapter` → `DefaultActivationPlanner.versions.ontology` 的本体版本子块正确进入 plan hash | `make backend-test` 绿；启动后跑一次 ActivationPlan，plan hash 中 ontology 字段 = 新钉值 |
| WI-03-3 | **命名空间修复**：`specs/knowledge-architecture/instances/product/products.ttl:1` 前缀 `https://gits.bank.example/ontology/core#` → 与本体一致（`https://gientech.com/gits/kno/`）；重跑 SHACL 实例校验 | `targetedInstances` > 0；`vacuous` 消失；`gk17_triple_consistency_check.py` 相关断言转绿。**例外**：产品关系三属性（`requiresProduct`/`complementsProduct`/`mutuallyExclusiveWith`）实例仍为 0 条（40 处悬空引用待产品 Owner）→ 在 `ONTOLOGY-CONFORMANCE.md` **豁免登记表**显式登记（原因/责任人/解除条件），不得静默放行（R-6） |
| WI-03-4 | **D3-A 残留收口**：KERT `ontology_reference.py:1`、`knowledge_map.py:30`、`knowledge_source.py:64` 的「依据 D3-A」表述改为 D-31/V1.2 设计；同步检查 `ontology_provision.py` 注释 | grep `D3-A` 在 src/ 下零命中（docs/adr 历史文档除外，禁止改历史） |

**G3 判据**：双侧启动成功 + 漂移用例绿 + vacuous 消失或全部显式豁免 + D3-A 残留清零 + plan hash 含新钉值。

---

## 6. Wave 4｜门禁与符合性（FP 实施 → QA 验证，1.5d）

| WI | 动作 | 验收 |
|---|---|---|
| WI-04-1 | 实现 `public-ontology/build/conformance.py`：R1~R9 逐条检查，每条**失败具名**（`ONTOLOGY_NS_VIOLATION` / `ONTOLOGY_MISSING_METADATA` / `ONTOLOGY_SERIALIZATION_GAP` / `ONTOLOGY_VACUOUS_SHACL` / `ONTOLOGY_AXIOM_GAP` / `ONTOLOGY_BREAKING_CHANGE` / `ONTOLOGY_METADATA_INCOMPLETE` / `ONTOLOGY_PROVENANCE_GAP` / `ONTOLOGY_UNPINNED_IMPORT`）；产出 `CONFORMANCE-REPORT.md`（命令 + 哈希 + 豁免登记表） | R1~R9 全绿或具名豁免；报告钉入 PROVENANCE |
| WI-04-2 | **跨域引用白名单门禁** `scripts/onto_crossref_check.py`：GITS/KERT 本体中出现的外部类引用必须 ∈ 公共模块类清单；fail-closed | 正例绿；**变异**：在 GITS 本体加一条对 KERT 私有类的引用 → FAIL；恢复 → PASS |
| WI-04-3 | **变更影响面分析** `scripts/onto_impact_analysis.py`：输入本体文件 diff，输出受影响钉值方清单（哪些 `ontology_reference.json`/PROVENANCE/`KnowledgeArchitectureConfig` 钉值失效）+ 受影响 plan hash 范围 + 重钉清单 | 对一次模拟变更输出正确清单（用基线 vs 三分后做回归样本） |
| WI-04-4 | CI 接入（双仓 workflow）；`vacuous=true` 处理策略从「静默绿」改为「具名失败或豁免登记」（KERT `ontology_materialize.py` 血缘输出侧同步改） | CI 红绿可演示；vacuous 负例（构造空实例集）→ 具名失败 |
| WI-04-5 | **全量变异回归**：对 G2/G3/G4 全部否定式门禁跑 mutate→FAIL/restore→PASS 矩阵 | 变异矩阵 100% 被捕获，落 `EVIDENCE.md`（本 Loop 核心可执行证据） |

**G4 判据**：R1~R9 报告钉值 + 白名单门禁 + 影响面分析 + CI 全绿 + 变异矩阵全捕获。

---

## 7. Wave 5｜剥离演练（TL，0.5d）· KERT 仓

| WI | 动作 | 验收 |
|---|---|---|
| WI-05-1 | 演练 `git subtree split -P public-ontology -b public-ontology-export`（在临时 clone 上操作，**不动主仓**）；对导出树逐文件哈希比对 | 导出树与源目录哈希一致；命令与产物哈希落 EVIDENCE |
| WI-05-2 | 零依赖证明：grep `public-ontology/` 全目录无 `kert.*` import、无相对路径越界引用（`../src/` 等）；`make -C public-ontology export-jsonld` 独立可跑 | 证明脚本绿；剥离可行性结论落 V2.0 冻结材料 |

**G5 判据**：模块可独立打包。Baton 交 `independent_qa`。

---

## 8. G6｜独立 QA 与冻结

1. **独立 QA**（session 命名 `qa-onto1-001`）：复核 G0~G5 全部证据 + 变异矩阵有效性（抽查 mutate 用例非空转）+ 三份 TTL 独立复算计数 + 双仓 `git log` 原子性；记录 QA_PASS 或退回。
2. **Owner/委员会**：确认 V1.2 §11 三项裁定执行无偏差 → 冻结设计为 **V2.0（APPROVED）**；GK17 `FAILURES.md` 中 `NAMESPACE_MISMATCH_SILENTLY_GREEN` 项关闭；`ADR-018` 残留状态说明更新（仅追加指针，不改历史）。
3. **Loop 关闭**：`STATE.json` status=closed（holder=owner_review）；`memory/NEXT_SESSION.md` 写明 §13 后续工作八项的归属建议。

---

## 9. 回滚预案

| 场景 | 回滚动作 |
|---|---|
| Wave 2 后发现问题 | 三份新 TTL 全部保留（增量文件，无破坏）；`CONTRACT_INDEX` 登记回退一条提交即可；旧 `gits-core.owl.ttl` 从未被改，天然回滚点 |
| Wave 3 切换后失配 | 旧钉值窗口期内：`ontology_reference.json` / `KnowledgeArchitectureConfig` 指回旧值（git revert 单提交）；KERT `90_control/ontology/` 旧副本窗口期内未删，直接恢复 |
| 任何不可修复态 | 双仓 `git revert` 至 Wave 0 基线提交（哈希已录 EVIDENCE）；基线 `sha256:705578d6324a…` 为最终锚 |

## 10. 关键依赖与关键路径

- **关键路径**：WI-02-1（合同登记）→ WI-02-2（拆分）→ WI-03-1/2（双仓切换，可并行但同窗口）→ WI-04-5（变异回归）→ G6。
- **外部依赖**：① 委员会三项裁定（阻塞 Wave 1+）；② GB/T 48000.3 正式文本（阻塞 WI-00-2 与 R1~R9 条款级定稿，不阻塞骨架）；③ KERT 仓写权限与 KERT 维护方协作（WI-01/03 在 KERT 仓）；④ 产品 Owner 对 40 处悬空引用的裁定（不阻塞本 Loop，R-6 走豁免登记）。
- **环境注意**：Python ≥3.12 建议；`make generate/check` 需本地 Maven 与 contract_pipeline 依赖可用；dependency-check 离线参数沿用既有约定。

## 11. TL 开工检查单（Day 1）

```
[ ] git status 干净；双仓分支 loop/ONTO1-ontology-split 已建
[ ] Loop 骨架存在；baton=tech_lead；NEXT_SESSION 已写
[ ] 基线 sha256:705578d6324a… 已录；attribution.csv 计数 19+2+11=32
[ ] 索引新鲜度已声明（INDEX_FRESH / INDEX_STALE(n)）
[ ] 委员会裁定状态已确认（未裁定 → 只做 WI-00-1/2）
[ ] FAILURES.md / EVIDENCE.md 已初始化
[开工] Loop: ONTO1-ontology-split, 角色: tech_lead, Baton: tech_lead, Gate: G0
```

---

> 本计划与 V1.2 设计为**执行-设计配对文档**：任何设计口径冲突以 V1.2（冻结后为 V2.0）为准；计划执行中发现的的设计缺陷须回写 V1.2 修订记录，不得只在代码里绕开。
