# 包级交接｜`W-1/D2-pack`（D2 产品关系 40 处悬引用的归一化决策包）

| 字段 | 值 |
|---|---|
| **包名** | `W-1/D2-pack` |
| **执行角色** | `product-ref-normalization-analyst`（P-4；**分析，不裁定**） |
| **交付时间** | 2026-09-20T14:21Z |
| **Baton** | holder 保持 `tech_lead`（本包未改变 Baton；`STATE.implementation_actor` = `tech_lead` 不变） |
| **数据锚点** | KERT `922a674d`（**只读**）· GITS `71169042` |
| **门禁状态** | `LOOP.yaml.gates` / `EVIDENCE.json.gates` **未变**（本包不注册新门禁） |
| **通道** | Wave -1 只读分析；`gate_state` 仍为 `RETURN_TO_HLD`（**未**改动） |

---

## 1. 交付物清单

| # | 交付物 | 位置 | 说明 |
|---|---|---|---|
| 1 | **决策包（含最小勾选表）** | `docs/dispatch/ONTO1-D2-产品Owner决策包-V1.0.md` | 事实复核 + 12 行勾选表 + 逐取值证据卡 + 交叉验证 + 零实例 + 影响面 + 两个一次性放行措辞 + 签署区 |
| 2 | 机读决策包 | `loops/ONTO1-ontology-split/evidence/d2-normalization-pack.json` | 40 处引用（含行号）· 12 取值（候选 + 强度 + 回源）· 账户关系位 · 零实例 · 场景矩阵 · 待裁问题 |
| 3 | 勾选表（逐字同源） | `evidence/d2-checklist-table.md` | 决策包 §2 表格的来源文件 |
| 4 | 逐卡片明细 | `evidence/d2-per-card-detail.md` | 40 行展开版（取值 × 卡片 × 字段 × 行号 × 关系） |
| 5 | 交叉验证表 | `evidence/d2-cross-vocab.md` | A 精确同形命中 + B 邻近/语义命中 |
| 6 | 生成器与自检 | `scripts/onto1_d2_normalization_pack.py` | `--gate` G1~G8；`--selftest` M0~M5 |
| 7 | 日志 | `evidence/wi_a5_d2_pack-20260920T142117Z.log`、`wi_a5_d2_pack_selftest-20260920T142117Z.log` | gate exit 0 / selftest exit 0 |

哈希：`d2-normalization-pack.json` `24c6e24ccb58ad82` · `d2-checklist-table.md` `04df69e1a02ed32f` ·
`d2-per-card-detail.md` `06455d5f1978d25a` · `d2-cross-vocab.md` `dc12bf8e2fdba3a0` ·
gate log `c946bf2998fd1786` · selftest log `63fc855292db3038`（sha256 前 16）。

---

## 2. 本批新增的可复用结论（带 `文件:行`，供下一 holder 免于重复通读）

| # | 结论（事实） | 回源 |
|---|---|---|
| 1 | 40 处引用 = 前置 **12** + 配套 **28** + 互斥 **0**；13 张卡；12 个唯一取值；**逐卡片行号已落盘** | `evidence/d2-normalization-pack.json`（`occurrences[]`） |
| 2 | 13 张卡 front matter 字段**行号同构**：`prerequisite_product_ids:19`、`mutex_product_ids:20`、`requiredAccountRelationship:26`、`capabilities:27`、`applicable_scenarios:28`、`complementary_products:30` | `KERT:CM-001.md:19-30`（13 张同构） |
| 3 | **卡片正文 §6 给出了每个悬空 token 的中文语义名**（前置/配套/互斥/替代产品），是本包候选映射的**决定性证据**，此前各裁定件均未引用 | `KERT:CM-001.md:64-65`、`CM-002.md:65`、`CM-003.md:65`、`CB-001.md:66`、`CB-002.md:65`、`FIN-001.md:77`、`FIN-002.md:72,75`、`FIN-003.md:75`、`IB-001.md:66`、`SET-001.md:65`、`SET-002.md:66`、`TF-001.md:66`、`TF-002.md:65` |
| 4 | `SETTLEMENT_ACCOUNT` 是**跨槽位 token**：产品位 24 处 + 账户关系位 **12 处**（后者不计入 40）；在账户关系位有**可执行消费者**（与客户账户关系事实比对），并有测试夹具自洽 | `KERT:CM-001.md:26`、`src/kert/application/product_recommendation/eligibility.py:547,552`、`scripts/product_recommendation_golden_benchmark.py:8`、`tests/integration/test_sp15_contract_conformance.py:155` |
| 5 | `SETTLEMENT_ACCOUNT` 的**第二身份候选**在 GITS 侧：PI-0 种子有名为「对公结算账户」的产品行（与 `PROD-SET-001`「单位结算账户」不同名） | `GITS:adapters/persistence-relational/.../h2/V021__corporate_product_knowledge_seed.sql:42` |
| 6 | `CORPORATE_E_BANK` = 企业网银，5 处引用与 5 张卡正文**一一对应**；但 GITS 分类基线把它列为**品类**（`has_products:false`）、GITS PI-0 种子却登记为**产品行** ⇒ **跨仓身份冲突**（须 Owner 对齐） | `KERT:CM-001.md:65`、`SET-001.md:65`；`GITS:specs/product-knowledge/product-taxonomy.yaml:197-198`；`GITS:V021…:51` |
| 7 | `CASH_MANAGEMENT` = 产品族编码（3 成员），且族中文名「现金管理」= 两处正文配套名 ⇒ 族名写到产品位 | `KERT:CM-001.md:5-6`、`FIN-001.md:77`、`SET-001.md:65`；`GITS:product-taxonomy.yaml:68-69` |
| 8 | GITS 分类基线里另有一批**同物不同形**的品类，直接关系 4 个取值的定性：`CM_CASH_POOLING`（资金池）、`FIN_WORKING_CAPITAL`（流动资金）、`CB_CROSS_BORDER_SETTLEMENT`（跨境结算）、`TF_ACCEPTANCE_INSTRUMENT`（承兑工具） | `GITS:product-taxonomy.yaml:167-168,239-240,221-222,203-204` |
| 9 | GITS 侧把「外汇服务 / 票据贴现 / 财务顾问」列为**品类**（`has_products:false`），且 PI-0 种子另有「外汇避险（远期结售汇）」产品行 | `GITS:product-taxonomy.yaml:229-230,215-216,265-266`；`GITS:V021…:108` |
| 10 | `mutex_product_ids` **13/13 空**；卡正文仅有 **4 处叙述性**互斥描述（其中 `SET-001` 为"无"）⇒ 零实例 | 每卡 `:20`；`KERT:FIN-001.md:75`、`FIN-002.md:73`、`FIN-003.md:73`、`SET-001.md:64` |
| 11 | `RECEIVABLE_LEDGER_TOOL` / `ORDER_RECEIVABLE_CLOSED_ACCOUNT` 的性质由**同字段混入合同/账户**进一步佐证 | `KERT:FIN-002.md:72,75`、`FIN-003.md:75` |

---

## 3. 未做声明（红线自查）

- **未**代替产品 Owner 裁定：所有 `candidates` / `suggested_classification` 明确标注为"分析员建议"；包内不含"已裁定"式结论；
- **未**修改产品卡与 `products.ttl`（KERT 仓全程只读，未写入；卡片 sha256 已随包记录，可核验未变）；
- **未**修改 `specs/`、`generated/`、`CONTRACT_INDEX.yaml`、`docs/dd/` 封版制品、`evidence/cq-fixtures/*.json`；
- **未**把三场景标 `PASS`（三场景均 `NOT_EVALUATED`，且 `--gate` G7 会拦住任何 `PASS`）；
- **未**关闭 R-6；**未**把 SIM / GITS 种子数据当企业权威；
- **未**新建"权威映射表"（映射先定性后入册，GK17 §1.3）；
- **未**注册新 Loop 门禁，**未**改 `Makefile`；**未** `git add`（工作区仅新增未跟踪文件）。

---

## 4. 接手动作

**Owner 侧（人类，阻塞项）**

1. 按决策包 §2 勾选 12 行（或直接采用 §7 的选项 α / β 措辞）；
2. 指定「有效待补」项的补齐方式（Owner 提供 `PROD-*` 映射表 / 由本 Loop 生成候选再确认）；
3. 一并处理决策包 §3.1 的衍生问题：**若判 `SETTLEMENT_ACCOUNT` 为账户关系，是否需要新增关系类型**（属 TL + 语义架构，合同先行）。

**TL 侧（本 Loop 内，可立即做）**

1. 把决策包作为《D2 请求函》的**附件**一并送达（请求函签署区保持原样，未改已发出文书）；
2. 裁定到达后：按勾选结果生成**受控候选映射**（此时才可入册，走合同先行 + `CONTRACT_INDEX.yaml`），
   并为 `requiresProduct` / `complementsProduct` 补**正负夹具 + 目标数断言**；
3. `mutuallyExclusiveWith` **不因** D2 签署即可评：仍需实例或受控夹具才能从 `NOT_EVALUATED` 迁出（决策包 §4）；
4. KERT 侧任何"更正/补卡"须由产品 Owner 在 KERT 维护方执行（本环境只读）。

---

## 5. 本批自伤与自纠

- `FAIL-2026-09-20-05`（已闭合）：`SEMANTIC_HITS` 中 `card.*` 条目缺仓根 ⇒ G4 一次性拦下 **13 条**看似齐备、
  实际指不到的回源。修复后 `[G4] 78 条，问题 0`；`--gate` G1~G8 全 PASS；`--selftest` M0~M5 全 PASS。
  正面结论：**"逐条回源必须真实存在且行内容匹配"这条断言有牙齿**。
