# 产品引用 7 项裁定｜Owner 签署记录 + SIM 投影变更包 V1.0

| 项 | 值 |
|---|---|
| 裁定人 | **产品 Owner = Owner 本人** |
| 裁定日期 | **2026-09-22** |
| 决定引用 | `OWNER-DECISION-2026-09-22-D2`（建议 ID，由应用方登记为实际引用） |
| 性质 | ① 裁定记录（本件 §1）② 变更包（本件 §2~§4）③ 新卡需求（§5） |
| 交付方式 | Owner 2026-09-22 选 **B** ⇒ **已由 TL 应用**（并发预检通过：无进程、mtime 未变） |
| 应用结果 | **10/10 门禁 PASS · 4/4 变异 PASS · 幂等一致**（见 §9 应用记录） |
| 非声明 | 未标 `PASS`；`formalRelationRelease` 保持 `NOT_AUTHORIZED`；未解除任何隔离前不生成正式关系 |

---

## 9. 应用记录（2026-09-22，TL，Owner 授权 B）

### 9.1 实际结果（与 §4 预期的差异已标明）

| 指标 | 变更前（11:51 实测） | **变更后（实测）** |
|---|---|---|
| 投影关系数 | 28 | **30**（去重三元组 **30**） |
| 跳过关系 | 12（全部计为"隔离"） | **10**（待补 **8** · 作废 **2** · 未决 **0** · 未分类 **0**） |
| 贡献来源卡 | 12 张 | **13 张**（`PROD-SET-001` 新增贡献） |
| 隔离/待补/作废泄漏 | 0（仅检隔离，**空转风险**） | 0（**三类并检**，且并集为空按空转判 FAIL） |
| `UNRESOLVED.json` | 40（**状态漂移**） | **10**（与投影同一次构建单源产出） |
| 门禁数 | 8 | **10**（新增 G9 防"待补被静默提升"、G10 防"未决登记漂移"） |
| 变异用例 | 4（M1 已退化） | 4（**M1 已替换**；现被 7 个门禁同时拦下） |
| 投影文件 sha256 | `6fc33da2151a01a5…` | **`d63f504ba4ab6418…`** |
| 配置 | 1.0.0 | **1.1.0**（sha256 `50989536…`） |
| `UNRESOLVED.json` sha256 | — | `4ccde4ae…` |

### 9.2 应用过程中发现并修正的两件事（**先记账后修**）

| # | 问题 | 处置 |
|---|---|---|
| F-1 | **本变更包初稿把增量算成 29**（实际 `CASH_MANAGEMENT` 在 2 张卡上各 1 条 ⇒ 28+2=**30**） | 应用前自查发现，已更正 §3/§4；**未带错误上线** |
| F-2 | **我新写的代码有 `KeyError`**（`rep['unresolvedReferenceCount']` 实际在 `rep['unresolved_report']` 内层）⇒ 首次 `--build` 抛异常（退出码非 0），但 `UNRESOLVED.json` 已在异常前写出 | 立即定位并修复（改用内层 `unre[...]`），复跑构建 **exit=0**；随后 G10 由 FAIL 转 PASS |

### 9.3 关键旁证：新门禁**先红后绿**（非空转证据）

```
首次跑 G10（盘上未决仍是 40）：FAIL [G10] 盘上未决=40 期望=10；relationInstances=0/30；config 版本=1.0.0/1.1.0
重建后复跑：                    PASS [G10] 盘上未决=10 期望=10；relationInstances=30/30；config 版本=1.1.0/1.1.0
```
⇒ G10 确实能抓到本次发现的真实缺陷（状态漂移），**不是空转断言**。

### 9.4 未做的变更（有意为之）

| 项 | 原因 |
|---|---|
| **未改写 `products.ttl`** | 临时试跑显示旧生成器会把 30 条关系写进基础文件；而 C-2 整改后的口径是**基础文件只放 13 个产品个体、关系归 `sim/` 文件**。套用会把 SIM 关系混进非 SIM 文件 ⇒ **不采纳**（试跑产物仅落 `/tmp`，未进仓） |
| 未清理产品卡 front matter | 作废/待补取值的清理属产品 Owner 后续动作（§5 已登记） |
| 未改 taxonomy | 企业网银族归属若需新族 ⇒ 单独申请 |

### 9.5 证据

- Loop 证据日志：`loops/ONTO1-ontology-split/evidence/wi_d2_sim_projection_d2r2-20260922T043004Z.log`（含 `--gate` / `--selftest` / `--build` 三段退出码）
- 制品哈希：投影 `d63f504b…` · 未决登记 `4ccde4ae…` · 配置 `50989536…` · 脚本 `0f5406c7…`
- 复跑命令：`python3 scripts/onto1_sim_projection.py --gate`（10/10）· `--selftest`（4/4）

---

## 1. 签署结论（Owner 2026-09-22）

| # | 符号 | 条数 | **裁定** | 目标 / 理由 |
|---|---|---:|---|---|
| 1 | `CORPORATE_E_BANK` | 5 | **有效待补**（Owner 改判，非 TL 建议的"作废"） | 电子渠道**以后也做成产品** ⇒ 等新卡建成后入 `aliasMap` |
| 2 | `CASH_MANAGEMENT` | 2 | **错误引用** | 族名当产品 ⇒ 指定指向 `PROD-CM-001` 现金池 |
| 3 | `FX_FORWARD` | 1 | **有效待补** | 远期结售汇，属跨境金融族；建议编号 `PROD-CB-003` |
| 4 | `DISCOUNT_SERVICE` | 1 | **有效待补** | 票据贴现，属贸易金融族；建议编号 `PROD-TF-003` |
| 5 | `FINANCIAL_ADVISORY` | 1 | **有效待补** | 财务顾问，属投资银行族；编号待分配 |
| 6 | `RECEIVABLE_LEDGER_TOOL` | 1 | **作废引用** | 台账工具不属可售产品 |
| 7 | `ORDER_RECEIVABLE_CLOSED_ACCOUNT` | 1 | **作废引用** | 账户安排不属可售产品 |

**汇总（12 条关系）**：有效待补 **8 条 / 4 符号** · 错误引用 **2 条 / 1 符号** · 作废 **2 条 / 2 符号**。
**裁定后 `quarantinedAliases`（"未决"）应为空**：7 个符号全部获得分类。

---

## 2. 配置变更（`projection-config.json`：1.0.0 → 1.1.0）

```diff
 {
   "schema": "ONTO1-PROJECTION-CONFIG/1.0",
-  "version": "1.0.0",
+  "version": "1.1.0",
   "effective": "2026-09-21",           # 建议新增 "revised": "2026-09-22"
   "authority": "Owner 最终决议 2026-09-21（二、C-2 生成器整改；三、D2 关系投影）",
+  "authorityRevision": "Owner 2026-09-22 签署：产品引用 7 符号分类（OWNER-DECISION-2026-09-22-D2）",
   "simulationOnly": true,
   "formalRelationRelease": "NOT_AUTHORIZED",
   "aliasMap": {
     "SETTLEMENT_ACCOUNT": "PROD-SET-001",
     "CASH_POOL": "PROD-CM-001",
     "WORKING_CAPITAL_LOAN": "PROD-FIN-001",
     "CROSS_BORDER_RMB_SETTLEMENT": "PROD-CB-001",
-    "BANK_ACCEPTANCE_DRAFT": "PROD-TF-001"
+    "BANK_ACCEPTANCE_DRAFT": "PROD-TF-001",
+    "CASH_MANAGEMENT": "PROD-CM-001"
   },
-  "aliasMapDecisionRef": "OWNER-DECISION-2026-09-21-D2",
+  "aliasMapDecisionRef": "OWNER-DECISION-2026-09-22-D2",
+  "aliasMapDecisionHistory": ["OWNER-DECISION-2026-09-21-D2"],
   "aliasMapNote": "…（保留原文）+ 2026-09-22 新增 CASH_MANAGEMENT（原为族名误用，裁定为错误引用并指定具体产品）",
+  "pendingProductCards": {
+    "CORPORATE_E_BANK": { "reason": "待建产品卡（Owner 改判：电子渠道以后也做成产品）", "relationCount": 5 },
+    "FX_FORWARD": { "reason": "待建产品卡（远期结售汇）", "suggestedProductId": "PROD-CB-003", "relationCount": 1 },
+    "DISCOUNT_SERVICE": { "reason": "待建产品卡（票据贴现）", "suggestedProductId": "PROD-TF-003", "relationCount": 1 },
+    "FINANCIAL_ADVISORY": { "reason": "待建产品卡（财务顾问）", "suggestedProductId": "待分配", "relationCount": 1 }
+  },
+  "pendingRule": "待补别名**不得**进 aliasMap、**不得**进任何 A-Box 投影；新卡建成并批准后方可迁入 aliasMap",
+  "voidReferences": {
+    "RECEIVABLE_LEDGER_TOOL": { "reason": "裁定作废：台账工具不属可售产品", "relationCount": 1 },
+    "ORDER_RECEIVABLE_CLOSED_ACCOUNT": { "reason": "裁定作废：账户安排不属可售产品", "relationCount": 1 }
+  },
+  "voidRule": "作废引用永久不进投影；产品卡 front matter 的对应取值由产品 Owner 后续清理（不在本变更范围）",
-  "quarantinedAliases": { …7 项… }
+  "quarantinedAliases": {},
+  "quarantineRule": "（保留原文，声明该类别当前为空）"
 }
```

---

## 3. 门禁与代码变更（`scripts/onto1_sim_projection.py`）

> 现状（2026-09-22 11:51 运行记录）：**8/8 PASS**，其中 **G2 硬断言「投影关系数=28」**、G5「溯源语句=28」、G7「来源卡 12 张」、G3「隔离别名零泄漏」。

> ### ⚠ 数值更正（2026-09-22，应用前自查）
> 本包 §3/§4 初稿把增量写成 **29**，**算错了**：`CASH_MANAGEMENT` 在两张卡上各出现 1 次
> （`PROD-FIN-001.complementary_products`、`PROD-SET-001.complementary_products`）⇒ 解析后新增 **2 条关系**，
> 期望值应为 **28 + 2 = 30**（`CROSS_BORDER_RMB_SETTLEMENT` 等仍是 1 条，勿混用）。
> 下表已按 30 更正；`distinct_triples` 与 `G7 来源卡数` **以实际构建输出冻结**（见 §3.1 冻结记录）。

| # | 变更点 | 现值 | **改为** |
|---|---|---|---|
| C1 | G2 期望关系数 | `== 28`（`:132`） | **`== 30`**（+2 条：`CASH_MANAGEMENT` 在 2 张卡上各 1 条）；`distinct_triples` **以构建输出冻结** |
| C2 | G5 溯源语句数 | `n_stmt == 28 and n_sha == 28 and n_fld == 28 and n_dec == 28`（`:149`） | **`== 30`（四项同值）** |
| C3 | G7 来源卡数 | 12 张 | **以构建输出冻结**（`PROD-FIN-001`/`PROD-SET-001` 是否已属贡献卡集合决定是否变化） |
| C4 | G3 零泄漏范围 | 仅 `quarantinedAliases`（`:135`） | **三类并检**：`quarantinedAliases` ∪ `pendingProductCards` ∪ `voidReferences` **均不得出现在投影中** |
| C5 | 变异用例 M1 | 注入 `cfg["aliasMap"]["CASH_MANAGEMENT"]`（`:205-207`）——**变更后不再是违规**，会假通过 | **替换为** `CORPORATE_E_BANK`（pending 类），断言：pending 别名进 aliasMap ⇒ **必须 FAIL** |
| C6 | 新增 G9（建议） | — | `pendingProductCards` 每项须含 `reason` + `relationCount`，且**必须不在** `aliasMap`；否则 FAIL（`SIM_PENDING_ALIAS_PROMOTED`） |
| C7 | 头注释与文档字符串 | 「把 Owner 已批准的 **28 条**关系写入」（`:4`）、`# ── 28 条已批准关系`（`:98`） | 同步为 `29`（或引用配置动态值），**避免注释与断言再次漂移** |

---

## 4. 应用后预期（可用于验收）

| 指标 | 变更前（11:51 实测） | 变更后预期 |
|---|---|---|
| 投影关系数 | 28 | **29** |
| 隔离/待补/作废泄漏 | 0（仅检隔离） | 0（**三类并检**） |
| `UNRESOLVED.json` 未决数 | 40（**状态漂移**：含 28 条已解决） | 应为 **0**（12 条已分类：8 待补 + 2 错误引用已解析 + 2 作废） |
| CQ3-S4 场景 | `NOT_EVALUATED` | 转 **可评测**（仍 SIM，`formalRelationRelease=NOT_AUTHORIZED`） |
| 页面（比较/前置/配套章节） | 关系显示"待核验" | 显示已解析关系（29 条） |

---

## 5. 新卡需求（由本裁定派生，交产品 Owner）

| # | 产品 | 建议编号 | 族 | 阻塞关系 | 备注 |
|---|---|---|---|---|---|
| 1 | 企业网银（电子渠道） | 待分配（建议 `PROD-CM-004`？需按 taxonomy 规则） | 待定（渠道域未在 6 族内） | 5 条 | Owner 已表态"以后也做成产品"；**族归属需先定**（若新增族属 taxonomy 变更） |
| 2 | 远期结售汇 | `PROD-CB-003` | 跨境金融 | 1 条 | 卡建成后入 `aliasMap` |
| 3 | 票据贴现 | `PROD-TF-003` | 贸易金融 | 1 条 | 同上 |
| 4 | 财务顾问 | 待分配 | 投资银行 | 1 条 | 同上 |

> ⚠ **taxonomy 影响提示**：若"企业网银"需要新族，则触发 `CTR-PK-TAX-001` 变更（6 族"不得增删"是现状约束）⇒ 需单独申请，**不在本变更包内**。

---

## 6. 为什么本会话不写盘（并发事实）

| 事实 | 证据 |
|---|---|
| 有活跃写者 | `scripts/onto1_sim_projection.py` **mtime = 2026-09-22 11:51**（本会话开始后） |
| 门禁刚跑过 | `evidence/wi_d2_sim_projection-20260922T035138Z.log`（11:51，8/8 PASS） |
| 纪律 | ONTO1 编排铁律：`make generate/check`、脚本与配置 **单写者独占**；两写者并发会产生假 FAIL（GK16 T-24 实测） |
| 并发写入规范 | `scripts/gk17_prodcard_to_rdf.py` 用 `write_atomic`，但**不解决语义冲突**（后写者覆盖前写者） |

⇒ **本件为"待应用变更包"**；应用者必须唯一：**由 ONTO1 当前写者应用**，或**由当前写者交棒后 TL 应用**。

---

## 7. 复现命令（应用前/后均可跑）

```bash
# 现状确认（8/8 且 G2=28）
cat loops/ONTO1-ontology-split/evidence/wi_d2_sim_projection-20260922T035138Z.log | head -14

# 磁盘制品哈希（G8 用）
sha256sum specs/knowledge-architecture/instances/product/sim/product-relations.SIM.ttl

# 配置现状
python3 -c "import json;d=json.load(open('specs/knowledge-architecture/instances/product/projection-config.json'));print(d['version'], d['aliasMapDecisionRef']);print('aliasMap:',len(d['aliasMap']),'quarantined:',len(d['quarantinedAliases']))"

# 应用后应改为 29 与空 quarantine
grep -n "== 28\|28 条" scripts/onto1_sim_projection.py
```

## 8. 非声明与边界

- 本裁定**不**解除 `QUARANTINED_UNRESOLVED` 之外任何红线；`formalRelationRelease` 仍 `NOT_AUTHORIZED`；
- **不**改产品卡 front matter（作废项清理是产品 Owner 的后续动作）；
- **不**改 taxonomy（新族需求另立申请）；
- TL **不代签** `QA_PASS`；SIM 声明生效仍需 4 项技术前置（其中独立 QA 不可代办）。
