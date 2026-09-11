# GK-KE L0-2 条件 G2：KERT 维护方确认函

> 发出方：GK-KE 交付 Tech Lead（主仓 `/home/szf/dev/gits-cbanking`）｜日期：2026-09-12
> 收件方：**KERT 维护方**（`/home/szf/dev/Leibniz-KERT`，分支 `feature/PI-ARCH-L10-L13`，HEAD `3b6640b993f4834d36833fa0bc3005d73768b594`）
> 依据：`GK-KE-OWNER-002` §5 条件 **G2「来源与转换绑定」**（"完成 §3 五条逐项核对与 **KERT 提供方确认**"）
> 用途：G2 关闭后，OC-01 方可关闭，ACT-01 方可生效（当前**均未关闭/未生效**）
> 性质：**确认函**。已由 TL 预填权威源实测证据，**请 KERT 维护方逐条确认或纠正**。

---

## 0. 背景（一句话）

GK-KE L0-2 契约激活需要把主仓 5 个既有知识架构对象的身份/版本映射到 SIM 命名空间的候选交换对象。
Owner 已签署 `GK-KE-OWNER-002`，规定这 5 条映射须**逐条核对并由 KERT 提供方确认**后才可见效。
TL 已完成能自行完成的核对；下列 4 条须 KERT 侧确认。

---

## 1. 请确认的问题（4 条，均附 TL 预填证据）

### Q1｜映射 3：`ASSET-KNOW-PRODUCT-CARDS` 的对象粒度

**决议 §3 要求**：KERT 侧先确认来源对象是「集合 / 入口 / 单卡」，据此决定取一张还是规定选取规则。

**TL 预填证据（来自 KERT 仓实测）**：

| 观察 | 位置 | 含义 |
|---|---|---|
| `product_cards = {p.get("productId"): p for p in products if isinstance(p, dict) and p.get("productId")}` | `src/kert/application/product_recommendation/sp15_skill.py:874-877` | KERT 内部把产品卡组织为 **`{productId: card}` 的键控集合（map）** |
| `products = raw.get("products") or raw.get("productCards") or []` | `sp15_skill.py:347` | 输入本身是**列表（多张）** |
| `_card(product_cards, product_id)` → `product_cards.get(product_id)` | `portfolio.py:222-225` | 按 productId **单卡检索** |
| 卡片必须含 `productId` + `productVersion`，且必须有 `owner` 与 `source` | `eligibility.py:270-285` | 缺任一 → `PRODUCT_CARD_INVALID` / `PRODUCT_CARD_INCOMPLETE`，`fail_closed=True` |

**TL 建议判定**：`ASSET-KNOW-PRODUCT-CARDS` 是**集合（collection）**，不是单卡。
故映射到 `SIM-ASSET-P001`（单张 SIM 卡）**不能声称一对一**，应登记为「**按明确规则从集合中选取/构造一张 SIM 卡**」。

**请 KERT 维护方回答**：
- [ ] 确认「集合」判定
- [ ] 确认选取规则（取哪一张？按什么条件？）
- [ ] 或纠正为「入口 / 单卡」并说明依据

---

### Q2｜映射 5：`RP-CORP-RM-001` 的策略细节与目标内容 hash

**决议 §3 要求**：绑定策略内容与确定性验证；不接受"仅改名即等价"。

**TL 预填证据（来自主仓权威源实测）**：

`specs/knowledge-architecture/routes/RP-CORP-RM-001.json`：

```json
{
  "schemaVersion": "1.0.0",
  "policyId": "RP-CORP-RM-001",
  "version": "0.1.0",
  "defaultMode": "MAP_FIRST",
  "defaultDecision": "DENY_UNMAPPED_TASK",
  "rules": [
    {"priority": 10, "taskType": "FACT_RECONCILIATION_30M", "mode": "ONTOLOGY_FIRST",     "activationContractRef": "AC-FACT-RECONCILIATION-001"},
    {"priority": 20, "taskType": "PRE_VISIT_PREPARATION",  "mode": "ONTOLOGY_THEN_MAP",  "activationContractRef": "AC-PREVISIT-001"},
    {"priority": 30, "taskType": "MARKET_SIGNAL_DISCOVERY","mode": "MAP_THEN_ONTOLOGY",  "activationContractRef": "AC-NOT-IN-P20"},
    {"priority": 40, "taskType": "REPORT_GENERATION",      "mode": "MAP_FIRST",          "activationContractRef": "AC-NOT-IN-P20"}
  ]
}
```

**已具备**：源策略版本 `0.1.0`、匹配条件（`taskType`）、优先级（10/20/30/40）、歧义处理（`DENY_UNMAPPED_TASK`，默认拒绝）。

**KERT 侧实测**：`RP-CORP-RM-001` 在 KERT 仓 **零命中**；KERT 文档
`docs/architecture/KERT_PRODUCTION_EVOLUTION_PLAN_V2_CANDIDATE.md:83` 与
`docs/dd/KERT_independent_architecture_review_2026-08-26_V1.0.md:397,401,694` 均将
**`KnowledgeMap Registry / RoutePolicy / ActivationPlan` 列为"应增加但当前缺失"**。

**请 KERT 维护方回答**：
- [ ] `SIM-ROUTE-001` 是否**已被 KERT 认领**？若是，给出其权威源路径 + 内容 SHA-256
- [ ] 若不认领，是否接受「映射 5 暂缓，维持 `pending_owner_confirmation` 且禁止参与运行时」
- [ ] 确认目标策略**不扩大**用途或客户范围

---

### Q3｜映射 2：`KM-CORP-RM-PREVISIT` → `SIM-MAP-FINANCE` 的适用条件

**决议 §3 要求**：明确适用条件、必需节点、参数、依赖对齐；限访前融资场景投影。

**TL 预填证据（两侧实测）**：

| 侧 | 观察 | 位置 |
|---|---|---|
| 主仓（源） | `mapId=KM-CORP-RM-PREVISIT`，`version=0.1.0`，`mapType=TASK`，`status=VALIDATION`，`tasks=["PRE_VISIT_PREPARATION"]`，`activationContractRefs=["AC-PREVISIT-001"]`，`routePolicyRef="RP-CORP-RM-001"`，`defaultPolicy=DENY`，`maxInitialTokens=2000` | `specs/knowledge-architecture/maps/corporate-rm/previsit-preparation.md:2` |
| KERT（消费方） | **确实消费**该地图：`self._trace_knowledge_map(trace, "KM-CORP-RM-PREVISIT", "PRE_VISIT_PREPARATION")` | `src/kert/application/skills.py:637` |
| KERT（消费方） | 同源轨迹：`"进入知识地图 KM-CORP-RM-PREVISIT，任务 PRE_VISIT_PREPARATION"` | `docs/v13-return-to-gits.md:104` |
| KERT（目标侧） | **无 `SIM-MAP-FINANCE` 任何证据**（零命中） | — |

**TL 建议判定**：映射 2 的**源侧消费关系已获 KERT 实证**（这是五条中最有依据的一条）；
但目标 `SIM-MAP-FINANCE` 是**主仓单方候选**，KERT 未认领。

**请 KERT 维护方回答**：
- [ ] 确认 KERT 对 `KM-CORP-RM-PREVISIT` + `PRE_VISIT_PREPARATION` 的消费关系
- [ ] `SIM-MAP-FINANCE` 是否由 KERT 认领为投影目标？若是，给出必需节点/参数/依赖对齐
- [ ] 确认投影**限** SIM-C001 / SIM-O01 / `INTERPRETATION` 用途

---

### Q4｜映射 4：`AC-PREVISIT-001` → `ActivationPlan` 的编译依赖关系

**决议 §3 要求**：接受「前置约束 / 来源引用」；**不接受**设计契约直接转成运行计划或复用 ID 作 `planId`。

**TL 预填证据（两侧实测）**：

| 侧 | 观察 | 位置 |
|---|---|---|
| 主仓（源） | `specs/knowledge-architecture/activations/AC-PREVISIT-001.json` 存在，`contractId="AC-PREVISIT-001"`；同目录另有 `AC-FACT-RECONCILIATION-001.json`、`AC-PRODUCT-RECOMMEND-001.json` | 实测 |
| 主仓（关联） | 地图通过 `activationContractRefs` 引用 AC（**引用关系**，非 ID 复用） | `previsit-preparation.md:2` |
| KERT（实测） | `AC-PREVISIT-001` 在 KERT 仓**未出现为代码常量**；KERT 侧使用 `activationContract: AC-PRODUCT-RECOMMEND-001`（`SP-15` skill front matter） | `docs/governance/KERT_GATE0_EVIDENCE_PACK_CANDIDATE.md:244`、`docs/skill-execute-api-contract-vNext.md:92,112` |
| KERT（实测） | `ActivationPlan` 在 KERT 侧亦被列为**"应增加但当前缺失"** | `docs/dd/KERT_independent_architecture_review_2026-08-26_V1.0.md:397,694` |

**TL 建议判定**：`AC-PREVISIT-001` 与 `ActivationPlan` 的关系应为**「编译依赖 / 前置约束」**：
AC 是设计期契约，`ActivationPlan` 是运行期确定性产物。主仓已按此实现
（`ActivationPlan` 由固化 TaskContext + 地图发布版本 + 路由策略 + 依赖版本 + 授权**确定性生成**，
**未复用 `AC-` 前缀作为 `planId`**，**未向闭集 Schema 加字段**）。

**请 KERT 维护方回答**：
- [ ] 确认「编译依赖 / 前置约束」判定
- [ ] 确认**不复用** `AC-` ID 作为 `planId`
- [ ] 确认 KERT 是否接受 `ActivationPlan` 为运行期对象（当前 KERT 文档列为缺失）

---

## 2. 请 KERT 维护方提供的最小交付物

| 交付物 | 用途 |
|---|---|
| 4 个问题（Q1–Q4）的逐条确认/纠正 | 关闭 G2 |
| 对 `SIM-MAP-FINANCE`、`SIM-ASSET-P001`、`SIM-ROUTE-001` 的**认领或否弃**声明 | 决定是否缩权激活 |
| 被认领对象的内容 **SHA-256** | 绑定确定性验证（§3 要求） |
| 确认人 + 确认时间 + 所依据的 KERT 提交 hash | 可追溯 |

**提交方式建议**：在 KERT 仓新建 `docs/integration/L0-2_G2_MAPPING_CONFIRMATION.md`，
或直接在 `GK-KE-OWNER-002` 决议下追加**补充差异决议**。

---

## 3. 重要提醒（避免误引）

KERT 仓内 `docs/integration/KERT_GITS_STATE_MAPPING_CANDIDATE.md` 是 **GITS↔KERT 产品推荐状态映射（WP1-3）**，
与 L0-2 五条**换对象映射**属不同范畴，且其自述：

```
status: CANDIDATE
FROZEN: NO
IMPLEMENTED: NO
```

**不得**将其引用为 L0-2 五条映射的确认证据。若 KERT 认为该文档确实覆盖 L0-2 映射，请**明确说明覆盖范围与理由**。

---

## 4. 当前状态（本函发出时）

| 项 | 状态 |
|---|---|
| Owner 决议 `GK-KE-OWNER-002` | 已签署（5× `APPROVED_WITH_CONDITIONS`） |
| G1 版本与制品绑定 | ✅ 关闭 |
| G3 交换对象对应 | ✅ 关闭 |
| G4 受影响范围复核 | ✅ 关闭（独立 QA `qa-gk1-g4-001`） |
| **G2 来源与转换绑定** | ⏳ **本函待复** |
| OC-01 | ⛔ 未关闭（依赖 G2） |
| ACT-01 | ⛔ 未生效（依赖 G1–G4） |
| Loop `GK1-l0-2-contract-activation` | 保持 `qa_pass`，**未退出** |
| `CTR-GKKE-API-001` | 保持 `CONTRACT_CANDIDATE`，**未改 APPROVED** |

**Owner 已选择方案 A（等待 KERT 答复）**，未选择缩权激活。
