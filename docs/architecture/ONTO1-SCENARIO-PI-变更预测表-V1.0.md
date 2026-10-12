# 产品解读重构｜本体变更预测表 V1.0（R6）

| 项 | 值 |
|---|---|
| 文档性质 | **预测件（DESIGN_ONLY）**——未实施、未执行任何门禁；**不是**变更批准 |
| 依据 | `ONTO1-L1-建模规则R1-R9修订版-DRAFT.md` R6｜`ONTOLOGY-SPLIT-DESIGN-V2.0-REVIEW.md` §6.5｜复审包 `07-兼容性矩阵-major-minor-patch.md` |
| 复合变更原则 | **取最高级别**；**「只增」不自动等于 minor**；词表变更与 Schema 变更单列 |
| 当前门禁 | `RETURN_TO_HLD` 有效 ⇒ 本表**全部条目的"必须动作"均未执行** |
| 非声明 | 不含国标条款级判定；不声称 `DESIGN_APPROVED`；未改 `specs/`、未改 `generated/` |

> **修订记录（V1.0 → V1.1，2026-09-21）**：初稿 C-08 与回归表引用了复审期快照（"前缀错配现状"）与失效判据脚本，自检回源后按当日实测修正；C-06 补充 SIM 投影的机械证据。**教训**：复审期文书的"现状"列不是现状。

---

## 1. 变更清单与级别判定

| ID | 变更 | 制品层 | 级别 | 判据（为何不是更低级） | 必须动作 |
|---|---|---|---|---|---|
| **C-01** | 新增类 `ProductInterpretation`（解读） | L2 | `minor` | 纯新增类，不改既有约束 | CHANGELOG + 版本号 minor 递增；旧钉值仍有效 |
| **C-02** | 新增类 `RuleBundle`（规则包） | L2 | `minor` | 同上 | 同上 |
| **C-03** | 新增属性 `interprets`（`ProductInterpretation → ProductOffering`）、`rulesFor`（`RuleBundle → ProductOffering`） | L2 | `minor` | 新增属性（只增）；**但**引入对 L1 的跨层引用 ⇒ 触发 R9 钉值要求（项目加严），非标准强制 | CHANGELOG + `owl:imports` 钉 L1 `versionIRI` + 消费侧同时校验内容哈希 |
| **C-04** | 新增属性 `describesProduct`（`ProductKnowledgeCard → ProductOffering`） | L2 | `minor` | 只增；V2.0 §4.3 已定（知识卡指向产品身份，**不以知识卡替代产品主数据**） | 同 C-03 |
| **C-05** | L2 既有 6 条产品关系属性（`cardOfProduct`/`versionOfProduct`/`supersedesVersion`/`requiresProduct`/`complementsProduct`/`mutuallyExclusiveWith`）**range 改指** L1 `ProductOffering` | L2 | **`major`迁移** | range **变更**（非单纯放宽）+ 跨层重构 + 与 L1 IRI 迁移并发 ⇒ **复合变更取最高** | 新 `versionIRI` + 弃用期（≥1 发布周期双发布）+ `oldIRI→newIRI` 迁移映射 + 回滚预案 + **双侧 Owner 批准** |
| **C-06** | 产品关系的**语义与实例权威维持现状**（类型权威在 L2，实例权威在产品卡 front matter） | L2/产品卡 | **`no-op`（明确不做的变更）** | 实现期不得误改（WP1.3 §2/§3）；**已有机械证据**：`UNRESOLVED.json` 登记 `relationTypeAuthority=ontology`、`relationInstanceAuthority=product cards`；`projection-config.json` 把产品卡 3 个 front matter 字段单向映射到 `requiresProduct`/`mutuallyExclusiveWith`/`complementsProduct`；`sim/product-relations.SIM.ttl` 为**单向生成产物**（勿手工编辑） | CHANGELOG 显式登记「未变更」，防被当作遗漏；SIM 投影 `formalRelationRelease=NOT_AUTHORIZED`（不得据此声称关系已正式发布） |
| **C-07** | L1 `Product → ProductOffering` 改名 + IRI 迁移 | L1 | **`major`** | 删项/改名 + IRI 变更 | **`NOT_EXECUTED`**：属 **B-2 断点**，出口清单（100 文件/288 命中）**未签** ⇒ 不得执行 |
| **C-08** | 实例层命名空间整改（原 `products.ttl:1` 同前缀双命名空间 → **C-2**） | 实例层 | **`major`（IRI 变更）** | IRI 变更 | **已部分执行（当日实测）**：术语/实例**分前缀**已落地（`gits:` 术语 / `prod:` 实例），原 `ONTOLOGY_PREFIX_COLLISION` 消除 ⇒ 该部分记为 **`DONE_IN_WORKSPACE`（非本场景提交）**；**残留**：实例命名空间仍为占位根域 `https://gits.bank.example/ontology/core#` ⇒ 正式 IRI 与解析承诺仍 **`BLOCKED`（D3 未签）**；**仍不得**创建 `namespaces.json`、不得填正式根域 |
| **C-09** | L2 其余新增类（`KnowledgeItem`/`Segment`/`KnowledgeSource`/`AssetDefinition`/`EvidenceBundle`/`Projection`）与改名类（`KnowledgeMapDefinition`/`SkillDefinition`） | L2 | `minor`（新增）/ `major`（改名） | 同上分类 | **本场景范围外**：由全局 ONTO1 编排；本表仅登记以免重复与误合并 |
| **C-10** | L4 合同 `CTR-PKC-API-001` / `CTR-PKC-DOM-001` | L4 | **`no-op`** | 不含 `owl:imports`、不钉本体哈希 ⇒ 不受 IRI 迁移影响 | 仅补说明（影响面分析 R-6）：产品身份口径登记，`productId` 值域不变 |
| **C-11** | 文档说明：`specs/product-center/README.md` 增补「产品身份 = L1 `ProductOffering`」 | L4/文档 | `patch` | 文档/说明完善，不动语义 | CHANGELOG；旧钉值有效 |

---

## 2. 旧夹具回归证明（**当前状态：DESIGN_ONLY**）

> 纪律：**变更未实施 ⇒ 无法提供"变更后旧夹具该通过仍通过、该失败仍失败"的执行证据**。本节给方案与基线，**不得**填任何 `PASS`。

### 2.1 可用夹具基线（实测存在）

| 夹具/门禁 | 位置 | 现状 |
|---|---|---|
| CQ1–CQ6 夹具 | `loops/ONTO1-ontology-split/evidence/cq-fixtures/CQ{1..6}.json` | 全部 `status=NOT_EVALUATED`（含外部阻塞 D2/D4 登记） |
| 消费者扫描 | `loops/ONTO1-ontology-split/evidence/consumer-scan-manifest.json` | `total_hits=26690`、`net_obligations=1052`、`orphan=0` |
| 45 项归属矩阵 | `loops/ONTO1-ontology-split/evidence/attribution-45-v2.csv` | 机读底座（哈希钉值） |
| 本体级一致性 | `scripts/gk17_triple_consistency_check.py` | `targetedInstances=0`、`vacuous=true`（**判据须按 R4 改为空转=失败**） |
| 变异回归（既有范式） | `scripts/gk_ke_mutation_regression.py`、`scripts/gate_selftest.py` | 10/10 被捕获（GK-KE 范式，可作本场景变异门禁模板） |

### 2.2 每条变更的回归对照表（Wave 2/3 收工必须逐条填实测）

| 变更 | 回归夹具 | 期望「变更前」 | 期望「变更后」 | 变异用例（必须被捕获） | 当前状态 |
|---|---|---|---|---|---|
| C-01/C-02 新增类 | `onto_split_check.py` 集合比对 + Shape 清单同步 | 类清单无该项 | 集合 = 11+2+19 与基线**并集相等**（无一变更） | 手工改一个 IRI ⇒ FAIL | `DESIGN_ONLY` |
| C-03/C-04 新增属性 | 同上（属性集合比对）+ `onto_crossref_check.py` | 属性清单无该项 | 属性计数自洽（36 条 OWL 对象属性口径） | 在 GITS 本体加一条对 KERT 私有类的引用 ⇒ FAIL | `DESIGN_ONLY` |
| C-05 range 改指 | CQ3 夹具 + range 断言 | `ProductKnowledgeCard` range 旧值 | range = L1 `ProductOffering` | 把 range 改回旧值 ⇒ FAIL | `DESIGN_ONLY` |
| C-07 L1 改名 | 全量消费者扫描（S1~S5）+ 影响面脚本 | 288 命中 | 命中 100% 处置（转控制面/跟随迁移/豁免/立项） | 消费者清单漏一项 ⇒ FAIL | `NOT_EXECUTED`（断点未签） |
| C-08 命名空间整改 | `scripts/onto1_namespace_collision_check.py`（`vacuous=versions_total==0`，`:308-309`） | C-2 前：同前缀双命名空间 | 术语/实例前缀分置且各自 1:1；closure 单版本且非空（否则 `vacuous` 计为**不计覆盖**） | 构造同前缀双命名空间 / 构造 0 个 `versionIRI` 的 closure ⇒ **均须 FAIL 或记为不计覆盖** | **部分 DONE**（前缀分置已落地）；正式 IRI 仍 `BLOCKED`（D3） |
| C-10/C-11 L4/文档 | `make check`（合同制品完整性）+ 场景合同测试 | 绿（PC0 实测） | **保持绿**（不受本体拆分影响） | 篡改 `generated/` ⇒ FAIL | `DESIGN_ONLY`（待变更后重跑） |

**收敛条件**：全部行状态不得为 `DESIGN_ONLY`；届时须附「命令 + 退出码 + 夹具命中数」原始输出。

---

## 3. 回滚可执行性验证（**当前状态：DESIGN_ONLY**）

| 场景 | 回滚动作 | 可执行性依据 | 验证状态 |
|---|---|---|---|
| Wave 2 后（拆分件已在，消费未切） | 三份新制品为**增量文件**，无破坏；`CONTRACT_INDEX` 回退**一条提交**即可 | 旧件 `gits-core.owl.ttl` **从未被改**（只读保留至 Wave 3）⇒ 天然回滚点 | `DESIGN_ONLY`（未实施） |
| Wave 3 后（消费已切，窗口期内） | `ontology_reference.json` / `KnowledgeArchitectureConfig` 指回旧值（单提交 revert）；KERT 旧副本窗口期内**未删**，直接恢复 | 窗口纪律：旧钉值保留只读 ≥1 验证周期 | `DESIGN_ONLY` |
| 不可修复态 | 双仓 revert 至 Wave 0 基线提交（哈希已录） | 最终锚 = `sha256:705578d6324abd0c…` | `DESIGN_ONLY` |
| 本场景 L4 | 无需回滚（C-10 为 no-op） | PC0 制品与本体无哈希耦合 | 已可判定 |

**回滚演练归属**：Wave 5「剥离演练」已含 subtree split + 零依赖证明（执行计划 V2.0 §6）；本场景额外要求：**至少一次真实 revert 演练**（在临时 clone 上）并落 EVIDENCE，方能从 `DESIGN_ONLY` 升级。

---

## 4. 级别判定的不自洽项（登记，不由实现负责人裁决）

| # | 冲突 | 出处 | 影响 |
|---|---|---|---|
| Q-1 | 「range 放宽 = minor」与「复合变更取最高 = major」在 `connectsFrom/To`、`memberOfGroup` 上打架 | `ONTO1-L1-八类术语定义稿-DRAFT.md` §3.3/§3.5 O-3/O-5 vs 复审包 07 号 §1 | 决定 C-05 类变更的流程与批准人数 |
| Q-2 | 设计 §4.1 写「4 条 range 改指 `CustomerRole`」，机读矩阵实测 **5 条**（另 `opportunityForProduct` 1 条指向 `ProductOffering`，合计 6 条） | 定义稿 §3.4 O-4 | Wave 2 断言口径（4 vs 6） |
| Q-3 | `playedBy` 未登记为新属性 ⇒ 36 条属性计数可能应为 37 | 定义稿 §3.2 O-2 | 计数断言自洽性（**不影响**本场景 C-03） |

> 本场景 **不自行取舍**；在 Q-1/Q-2 结论落定前，C-05 具备 `major` 流程所需的全部文件，但**不得**据此启动实施。

---

## 5. 复现命令

```bash
# 夹具现状（应全部 NOT_EVALUATED；若被标 PASS 即为违规）
for f in loops/ONTO1-ontology-split/evidence/cq-fixtures/CQ*.json; do
  python3 -c "import json,sys;d=json.load(open('$f'));print(d['id'], d['status'])"
done

# 基线锚与消费者净义务
sha256sum specs/semantic/gits-core.owl.ttl
python3 -c "import json;d=json.load(open('loops/ONTO1-ontology-split/evidence/consumer-scan-manifest.json'));print(d['baseline_sha256'], d['net_obligations'])"

# 本场景 L4 不受影响的自证（合同制品与本体无 import 关系）
grep -c '"\$ref"' generated/openapi/product-center.normalized.json
grep -rn "owl:imports" specs/product-center/ || echo 'no ontology import in L4 contracts (as expected)'
```
