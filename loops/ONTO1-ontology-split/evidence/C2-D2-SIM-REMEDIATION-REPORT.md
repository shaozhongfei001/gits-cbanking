# C-2 / D2 / D3 · SIM 整改实施报告（2026-09-21）

**授权**：Owner 最终决议 2026-09-21（签署主体：项目 Owner 邵钟飞）—— 一、二、三、四、五各条
**执行状态登记**：`OWNER_AUTHORIZED_SIM_REMEDIATION_AND_IMPLEMENTATION`（写入 `LOOP.yaml.gate_state.execution_state`）
**不代表**：架构委员会批准 · 正式设计基线生效 · 对外发布/生产激活 · 资产 `ACTIVE`

---

## 1. C-2 命名空间冲突 —— 已修复

### 1.1 修复方式（按决议二，**未采用**原方案 A/B）

`specs/knowledge-architecture/instances/product/products.ttl` 采用**术语与实例命名空间分离**：

```turtle
@prefix gits: <https://gientech.com/gits/kno/> .      # T-Box 命名空间（类定义处）
@prefix prod: <https://gits.bank.example/ontology/core#> .   # 既有 A-Box 实例命名空间
prod:prod_cb_001 a gits:Product ;  ...
```

- **13 个实例**（全部，非 2 个）的 subject 由 `gits:` 改为 `prod:`；**实例 IRI 逐字不变**（`prod:` 与原 `gits:` 绑同一命名空间）。
- 类型断言保持 `a gits:Product` ⇒ 现解析为 T-Box 中**已声明**的 `https://gientech.com/gits/kno/Product`。
- **未**引入 `owl:equivalentClass`（约束 3）；**未**改动 `gits-core.owl.ttl`（哈希与 git HEAD 一致：`705578d6324abd0c…`）。

### 1.2 前后 SHA-256

| 制品 | SHA-256（前） | SHA-256（后） |
|---|---|---|
| `products.ttl` | `e70bbe45bebcca2ebc3c…` | `b8875c169695fe8e5258…` |
| 副本留档 | `evidence/c2-before-products.ttl` | `evidence/c2-after-products.ttl` |
| `gits-core.owl.ttl` | `705578d6324abd0c1bd2…` | **不变**（未触碰 T-Box） |

### 1.3 验收（`scripts/onto1_c2_fix_verify.py`）

- `--gate` **7/7 PASS**：①两 TTL 可解析 ②13 实例 IRI 集合修复前后**逐字相同** ③13 实例类型全部命中 T-Box 已声明 `owl:Class` ④`Product` 确为 `owl:Class` ⑤错误类 IRI `.../core#Product` 被实例引用次数 = **0** ⑥`equivalentClass` = 0 ⑦前缀绑定正确。
- `--selftest` **6/6 PASS**：M1 类型改回错误类 ⇒ V3+V5；M2 实例 IRI 漂移 ⇒ V2；M3 未声明类 ⇒ V3；M4 注入 `equivalentClass` ⇒ V6；M5 还原 ⇒ 7/7。

### 1.4 门禁结果变化（如实）

`wi_a4_namespace_collision`：**由 fail（exit 2，C-2 两处真实冲突）→ INCOMPLETE（exit 3）**。
C-2 **实测 0 处**；剩余未判定项为 **`C-1b`（需 D3 签署根域后才可计算新旧 IRI 交集）** ⇒ 工具按设计判 `INCOMPLETE`，**按 D-1 如实记 `fail`、不得计为通过**（不是缺陷未修，是待 D3）。
登记表 `namespace-known-defects.json`：`defects` 清空（修复项移入 `repaired` 供审计追溯；修复后不清登记会被判**陈旧登记**）。

### 1.5 受影响消费者扫描结果（**可复算制品**）

> **仪器**：`python3 scripts/onto1_c2_consumer_scan.py --gate`（7/7）· `--selftest`（6/6）
> **制品**：`evidence/c2-consumer-scan.json`（含前后 SHA-256、逐文件分类、回归日志索引）
> **门禁**：`wi_c2_consumer_scan`(+selftest)

| 判定 | 结果 |
|---|---|
| 13 实例 IRI 修复前后 | **逐字相同**（13/13） |
| 错误类 IRI 的 **RDF 断言** | **0 处**（字面提及 7 个文件，仅 DOC+LOG，已逐条列明） |
| **破坏性引用**（RDF 把 `gits:` 绑到术语命名空间却用 `prod_`） | **0** |
| 运行时消费者（CODE）破坏性改写需求 | **0**（逐条列明） |
| 扫描幂等 | 两次结果一致 |



| 引用面 | 结果 |
|---|---|
| **Java / 运行时代码引用 A-Box 实例 IRI** | **0 处**（`grep -rn "gits.bank.example" --include=*.java` 为空） |
| `apps/api/.../V2OntologyOnlyChangeTest.java` | 其 `gits:prod_set_001` 字面量注入的是 **`gits-core.owl.ttl` 副本**（T-Box），与本次改动**无关、不受影响**（已核） |
| `scripts/gk17_triple_consistency_check.py` / `scripts/onto1_d2_normalization_pack.py` | 仅**读取**，已核对：D2 包对 `products.ttl` 的**行号引用已按 +4 偏移更新**（11→15 / 21→25 / 36→40 / 56→60 / 66→70），并**重新生成 D2 包**使 `products.ttl` 哈希刷为 `b8875c16…` |
| `docs/**`（设计/决策文书） | 仅描述性引用，无解析依赖 |
| 全仓 `gits:prod_*` 命中 | 24 个文件，**无一为运行时消费者**（其余为文档/脚本/日志） |

---

## 2. D2 产品关系分流 —— 已实施（28 已解析 / 12 隔离）

登记表：`evidence/product-alias-resolution.json`（计数**由源数据算出**，非硬编码）

| 已批准别名 | 目标产品 | 关系数 |
|---|---|---|
| `SETTLEMENT_ACCOUNT` | `prod:prod_set_001` | 24 |
| `CASH_POOL` | `prod:prod_cm_001` | 1 |
| `WORKING_CAPITAL_LOAN` | `prod:prod_fin_001` | 1 |
| `CROSS_BORDER_RMB_SETTLEMENT` | `prod:prod_cb_001` | 1 |
| `BANK_ACCEPTANCE_DRAFT` | `prod:prod_tf_001` | 1 |
| **合计** | | **28 = `RESOLVED_BY_OWNER_APPROVED_ALIAS`** |

**12 条保持 `QUARANTINED_UNRESOLVED`**：`CORPORATE_E_BANK` 5 · `CASH_MANAGEMENT` 2 · `RECEIVABLE_LEDGER_TOOL` 1 · `ORDER_RECEIVABLE_CLOSED_ACCOUNT` 1 · `FX_FORWARD` 1 · `FINANCIAL_ADVISORY` 1 · `DISCOUNT_SERVICE` 1。

**已落实的约束**：`CASH_MANAGEMENT` **保持隔离**（不映射为"现金池"）· 无虚构产品卡（5 目标全部对应 KERT 真实卡，13 张卡齐）· 隔离项**0 处**写入正式 A-Box · **CQ3 只报"28 已解析 / 12 隔离"**，`cq3_status` 已改为 `PARTIAL`，禁词（全量通过/全部解析/全部关闭）由门禁拦截。

检查器 `scripts/onto1_product_relation_resolution.py`：`--gate` **7/7 PASS**，`--selftest` **6/6 PASS**（M1 映射 `CASH_MANAGEMENT` ⇒ G1+G2+G5；M2 目标虚构 ⇒ G2+G4；M3 隔离别名写入 A-Box ⇒ G3；M4 CQ3 声称全量通过 ⇒ G6；M5 计数篡改 ⇒ G1；M6 还原且 A-Box 逐字节未变）。

> **口径声明**：本次只做**SIM 通道**的登记与投影准备（`sim_only=true`、`formal_abox_write=false`），**未**把 28 条写入正式 A-Box。若要写入，请给一句"批准写入 A-Box"即可执行。

---

## 3. D3 —— 临时 SIM 口径已登记

`LOOP.yaml.gate_state.provisional_sim_legacy_namespace`：两个命名空间统一登记为 **`PROVISIONAL_SIM_LEGACY_NAMESPACE`**（允许 SIM 开发/测试/迁移验证；不代表正式根域批准；不构成永久解析与持久性承诺；不得用于对外发布或生产契约；D3 须在**对外发布 / Wave 2 命名空间切换 / 生产激活前**完成）。⇒ **D3 不再阻塞当前 SIM 开发**。

---

## 4. 回归日志（均经 `record_gate.py` 登记，可复核）

`wi_c2_fix_verify` · `wi_c2_fix_verify_selftest` · `wi_d2_relation_resolution` · `wi_d2_relation_resolution_selftest` · `wi_a4_namespace_collision`（exit 3）· `wi_a4_namespace_collision_selftest` · `wi_w15_a3_acceptance`（8/8）· `wi_a3_reference_alignment`（+selftest）· `wi_a5_d2_pack`（+selftest，包哈希已刷）——文件名含时间戳，见 `EVIDENCE.json`。

**板面**：**35 门禁 = 34 pass / 1 fail**（唯一 fail = `wi_a4_namespace_collision`，语义 = `INCOMPLETE`/待 D3）。`loop-guard` PASS · `onto1-evidence-board` PASS · `make memory-check`/`evidence-check` PASS。

---

## 5. 仍然存在的真实技术阻塞（**只列技术，不列流程**）

| # | 阻塞 | 影响 | 需要的动作 |
|---|---|---|---|
| **B-1** | `scripts/gk17_prodcard_to_rdf.py:31,37` 仍按**旧口径**生成（`gits:` → A-Box 命名空间、`gits:prod_*`） | **若重新生成 `products.ttl`，C-2 会复现** | 该脚本属 **GK17 Loop** 产物（跨写域）⇒ 需你指派 GK17 侧同步（1 行前缀 + subject 前缀，改法同本报告 §1.1）。**我未擅自改** |
| **B-2** | D3 正式根域未批 | 新 IRI 前缀无法定稿；碰撞门禁 `C-1b` 无法判定（当前 `INCOMPLETE`） | 域名 Owner 联签（外部动作） |
| **B-3** | 12 条关系引用无产品归属 | 只能隔离，不能投影 | 逐条裁定（外部动作）；**不得**强行映射 |

> 另：`CASH_MANAGEMENT` 尤其需注意——它可能是**产品类别/能力概念**，不是产品实例（决议已明确禁止映射为"现金池"）。

---

## 6. 本轮我的操作事故（如实披露）

**`FAIL-2026-09-21-W15TL-16`**：我在清理 `evidence-board` 孤儿日志时**误读白名单键名**（用 `path`，实为 `file`）⇒ 白名单未生效，**一次性删除 53 个日志**（含 A3 的 `a3fix-after-*.log` 与 zip 预演证据）。
**处置**：从冻结沙箱副本**逐字恢复 32 件**；其余 **21 件**为我自己的重复 attempt 日志（已被当前登记日志取代）**永久丢失**，白名单条目已保留并标 `LOST_IN_INCIDENT_20260921` + `superseded_by`。
**加固**：新增 **D-14**（先 dry-run 后删除 · 白名单按 `file` 键 · 孤儿首选"登记或加白" · 删除前留副本）。**未影响任何门禁判定**。

---

## 7. 非声明

本报告不构成 `ARCHITECTURE_COMMITTEE_APPROVED`、不构成 `QA_PASS`、不代表正式设计基线生效或生产可用；`independent_qa` 仍为 `pending/actor=null`；12 条隔离关系未被分类；本次兼容修复**不得**解释为 V2 目标本体全部落地，`gits:Product` 也**不得**被当作 V2 目标模型的最终 `ProductOffering`（须走显式迁移清单）。

---

## 8. 第二轮执行（Owner 决议 2026-09-21「开发与正式批准分开」）

| 项 | 结果 |
|---|---|
| **① 生成器修复** | ✅ `scripts/gk17_prodcard_to_rdf.py` 改为**配置驱动**（`projection-config.json` v1.0.0）；命名空间分离 `gits:`→术语 / `prod:`→实例；GK17 门禁已重跑 **pass** |
| **② 重新生成稳定性** | ✅ 删除手修件后由生成器重生，**连续两次字节一致**：`e1b6e09e57d5834aa8c9b33ad016d91a5e59295480ade5ba55bba843f107c514`；C-2 验收 **7/7**；13 实例 IRI 未迁移；错误类引用 **0** |
| **③ D2 SIM 投影** | ✅ 28 条 → `specs/knowledge-architecture/instances/product/sim/product-relations.SIM.ttl`（`simulationOnly=true`；逐条溯源 源卡/字段/卡哈希/Owner 决议标识；**幂等**；别名表全部来自版本化配置）；**12 条 0 处进入**（含 `CASH_MANAGEMENT`）；正式关系发布 `NOT_AUTHORIZED` |
| **④ 门禁三态** | ✅ 报告层改为 `PASS=40 / FAIL=0 / PENDING_EXTERNAL_AUTHORITY=1 / PRODUCTION_ACTIVATION=BLOCKED`；`EVIDENCE.json` 用 schema 合法值 `inconclusive`（工具仍 exit 3），**不计 FAIL** |
| **⑤ 日志事故闭环** | ✅ 编号改为 **`W15TL-16`**（原 `W15TL-15` 属 O-12 正则缺陷，**未改写**）；证据包 `evidence/log-incident-W15TL-16.json`（53 删 / 32 恢复含 sha256 与来源 / 21 标 `LOST_SUPERSEDED_EVIDENCE` + 替代证据 / **门禁不依赖丢失文件**声明）；新增 `scripts/onto1_log_hygiene.py`（干跑→白名单→备份→删除 四闸，反例 5/5） |
| **⑥ 剩余真实阻塞** | B-2 **D3 正式根域未联签**（仅阻塞：正式 IRI 发布 / 持久解析承诺 / 外部消费者契约 / 生产激活）；B-3 **12 条关系无产品归属**（继续隔离） |

**新增门禁（均 pass）**：`wi_c2_generator_check`(+selftest) · `wi_d2_sim_projection`(+selftest) · `wi_log_hygiene`(+selftest)。

**非声明**：C-2 关闭 ≠ 架构委员会批准；SIM 投影 ≠ 正式 A-Box 生效；`PROVISIONAL_SIM_LEGACY_NAMESPACE` ≠ 正式根域；D3 未签**不是** SIM 代码缺陷。
