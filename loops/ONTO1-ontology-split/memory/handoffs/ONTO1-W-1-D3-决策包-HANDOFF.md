# ONTO1｜W-1 / D3 决策包（`W-1/D3-pack`）一页交接

| 项 | 值 |
|---|---|
| 包名 | `W-1/D3-pack`（D3 决策包 + 可执行原型） |
| 产出角色 | `semantic-namespace-analyst`（tech_lead 委托的分析子角色；**未认领 baton、未记任何门禁、未代签**） |
| 时间 | 2026-09-20T14:2xZ |
| Baton | 始终在 `tech_lead`；本包结束后 **Baton → `tech_lead`** |
| 性质 | **决策包（DECISION_PACK_ONLY）**——只给选项、权衡、可判定性与参数建议；**不选、不填、不发布** |
| 接手第一动作 | 读 `docs/architecture/ONTOLOGY-SPLIT-D3-决策包-命名空间与解析机制-DRAFT.md` **§10 接口对齐**（本包与并行需求规格有 3 处差异需裁定） |

## 1. 交付物

| # | 交付物 | 位置 | 状态 |
|---|---|---|---|
| 1 | D3 决策包 DRAFT（§0 红线 / §1 事实基线 / §2 D3-Q1~Q8 / §3 根域三类方案六维权衡 / §4 解析机制 + fail-closed F1~F7 / §5 映射草案 / §6 窗口与退役门 P-1~P-11 + W1~W7 / §7 实测 / §8 填空板 / §9 非声明 / §10 接口对齐） | `docs/architecture/ONTOLOGY-SPLIT-D3-决策包-命名空间与解析机制-DRAFT.md` | DRAFT |
| 2 | 逐术语映射草案（87 行 / 迁移域 67） | `loops/ONTO1-ontology-split/evidence/iri-mapping-draft.csv`（`cbf9c24d9e2eed1c…`） | DRAFT |
| 3 | 映射草案摘要（计数 + 红线 + 前置） | `evidence/iri-mapping-draft-summary.json` | DRAFT |
| 4 | 命名空间修复义务登记（2 项，含 Owner 与解除条件） | `evidence/namespace-known-defects.json` | 有效 |
| 5 | 映射草案生成器 + `R1~R5` 自检 | `scripts/onto1_iri_mapping_draft.py` | PASS |
| 6 | 碰撞检查原型 `C-1~C-4` + 16 条变异/对照 | `scripts/onto1_namespace_collision_check.py` | `--gate` **FAIL（阻断发布）**、`--selftest` PASS |
| 7 | 本交接页 | `memory/handoffs/ONTO1-W-1-D3-决策包-HANDOFF.md` | — |

命令日志：`evidence/wi_a4_iri_mapping_gate-20260920T142432Z.log`、`…_selftest-…log`、
`evidence/wi_a4_namespace_collision-20260920T142432Z.log`、`…_selftest-…log`。
（v1 的 `…-20260920T142053Z.log` 记录的是被修正前的行为，**已作废但保留溯源**，见 `FAIL-2026-09-20-07`。）

## 2. 本轮新增可复用回源结论（`文件:行`）

| # | 结论 | 回源 |
|---|---|---|
| 1 | 旧命名空间由脚本**从本体读取**（未硬编码）：`https://gientech.com/gits/kno/`；旧端术语 **67** = 32 类 + 34 对象属性 + 1 数据属性 | `specs/semantic/gits-core.owl.ttl:1`；`scripts/onto1_namespace_collision_check.py` `C-1a`；`--gate` 输出 |
| 2 | 本体**无 `owl:versionIRI`、无 `owl:imports`** ⇒ `C-3`（单版本闭包）当前**空转**，不得计为覆盖 | `specs/semantic/gits-core.owl.ttl`（全文件无该两谓词） |
| 3 | 前缀缺陷实测 **2 处**：`C-2a` 前缀双绑定、`C-2b` 同名不同 IRI（`gits:Product`） | `products.ttl:1`、`:10`、`:15`；`customer-source-mapping.r2rml.ttl:2` |
| 4 | **`namespaces.json` 全仓不存在** ⇒ 碰撞检查输入只能取自映射草案；该文件属 D3 决策物，本轮**不得创建** | `find . -name namespaces.json` → 无命中 |
| 5 | 语义关系分布（机读复算）：`RETAINED 32 / AUTHORITY_MOVED 4 / REMODELED 23 / TRANSFORMED 7 / DEPRECATED 1 / 新增 20` | `evidence/iri-mapping-draft-summary.json` |
| 6 | `RETAINED_AUTHORITY_MOVED` 实测 **4 项**（层迁移但短名与域值域未变）：`LegalEntity`、`ProductKnowledgeCard`、`ProductKnowledgeVersion`、`supersedesVersion` | `evidence/iri-mapping-draft.csv` |

## 3. 必须先看的三条硬事实

1. **碰撞检查当前 `FAIL`（阻断发布）**：2 处真实前缀冲突未修（`ADR-ONTO1 §5.4`「必须先修」）。
   ⇒ **D3 解除证据中的"新旧 IRI 碰撞检查脚本绿"当前不可能取得。**
2. **`C-1b` 是 `NOT_EVALUATED`，不是 PASS**：D3 未签 ⇒ 根域未定 ⇒ 新旧集合交集无从计算。
   脚本以退出码 `3` 单独表达"未判定"，并固定打印"**不得计为通过**"。
3. **登记 ≠ 豁免**：2 处冲突已登记修复义务，但登记**不会**使 `C-2` 转绿；"全部冲突均已登记"本身也判 FAIL。

## 4. 待裁定（**全部在人类/Owner 手上，TL 未代签**）

| # | 待裁 | 对象 | 落在哪 |
|---|---|---|---|
| A-1 | 根域类别（`ROOT-A/B/C/D`）、根域字面量、归属治理、解析机制、持久性承诺 | 语义架构 Owner + 域名 Owner | 决策包 §3、§4、§8 填空板 |
| A-2 | 窗口与退役门参数 `P-1~P-11`（含冻结期、回滚演练、参数落地位置） | 公共语义 Owner（待任命） | 决策包 §6 |
| A-3 | `J-1`「权威层迁移是否算语义变更」（决定 4 项能否用 `equivalentClass`） | TL | 决策包 §5.3 |
| A-4 | `J-2` 是否存在可升级为 SKOS `exactMatch` 的 `REMODELED` 项 | 公共语义 Owner | 决策包 §5.3 |
| A-5 | 接口差异 3 处：**脚本命名 / 退出码语义（`0·2·3` vs `0·1`）/ 输入源（映射草案 vs `namespaces.json`）** | TL + 候任 Integration Contract Owner | 决策包 §10.2 |
| A-6 | 是否把 `wi_a4_*` 登记为 Loop 门禁（本包**有意未接线**） | TL | 决策包 §10.1 末行 |

## 5. 未做事项（如实声明）

**未**代签、**未**记 `DEV_SELF_CHECK_PASS`/`QA_PASS`、**未**改 `LOOP.yaml` / `EVIDENCE.json` / `Makefile`、
**未**执行 `make generate`、**未**改 `generated/` / `specs/**` / 本体与 A-Box 制品 / `CONTRACT_INDEX.yaml` / 封版 `docs/dd/` / `evidence/cq-fixtures/*.json`、
**未**发布任何 IRI、**未**重钉、**未**退役旧 IRI、**未**标 `DESIGN_APPROVED`/`ACTIVE`/`FROZEN`、
**未**把任何根域字面量写入任何制品、**未** `git add`；KERT 仓只读未写。

## 6. 风险与边界

| # | 风险 | 说明 |
|---|---|---|
| R-1 | 两个原型并存 | 若候任 Integration Contract Owner 按需求规格另实现 `onto1_iri_collision_check.py`，将出现两个同职责脚本 ⇒ 必须先按 §10.2 裁定命名与归属 |
| R-2 | `C-3` 空转 | 当前无 `owl:versionIRI` ⇒ 单版本约束无覆盖面；补齐 version 声明后才具备真实约束力 |
| R-3 | `C-4b` 冻结形式较弱 | 冻结记录写在 `EVIDENCE.md`（人可改）。更强的形态是签名清单/受控清单，建议纳入 L4 注册表治理（`P-10`） |
| R-4 | 映射草案依赖上游证据 | 若 `evidence/attribution-45-v2.csv` 变更，须重跑 `--gate`（`R3` 计数锚定会立即报警） |
| R-5 | 词法解析边界 | 前缀扫描限 `specs/**/*.ttl`，**未**覆盖 JSON-LD / R2RML / SPARQL 前缀源（决策包 §10.3 已登记） |
