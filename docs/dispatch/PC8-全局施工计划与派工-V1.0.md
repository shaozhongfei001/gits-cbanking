# PC8 · 全局施工计划与派工 V1.0

```text
提交人：tech_lead（全局 TL）｜ 时间：2026-09-22
PC8 定义：文档 → LightRAG → 解读 链路（OD-PI-13，不动 PC0–PC7）
本件性质：TL 规划 + 已实际派发（非提案）。派工的机器可读唯一源 = loops/<loop_id>/LOOP.yaml
方法论：loop engineering v2.0（loops/_template 协议；每批次 = 受控 loop 实例 + 可执行 gate + 独立 QA）
```

> **本件不含时间承诺**。节拍以「门禁绿否」为唯一刻度（无日历依据，不编工期）。

---

## 1. 剩余工作量盘点（全部带仓库证据）

### 1.1 源材料轨

| 项 | 现状（实测） | 剩余 | 证据 |
|---|---|---|---|
| 真实监管源 `REG-*` | **9 份 AVAILABLE** | `REG-CB-001` 指名未果 1 项；`REG-FIN-002` 待 Owner 裁定（`D-R2`） | `source-registry.md` §5 汇总；`docs/dispatch/PC8-REG监管法规取证与裁定台账-V1.0.md` |
| 真实缺口 | 权威区 28 = **19 PENDING + 9 AVAILABLE** | 19 份为 **Owner 上传义务**（非 TL 可闭合） | 同上 |
| DEMO 造数 `SRC-*` | **11/17 份**（CM 3 + 跨族 3 + FIN 3 + SET 2） | **6 份**：`B4` TF 3 · `B5` CB 2 · `B6` IB 1 | `registry §5.8`；门禁 `EXPECTED_DEMO = 11` |
| REG 台账 | V1.0 **已过时**（记 6 AVAILABLE / 21 PENDING / 94/94） | 更正为 9 / 19 / **131/131** | 台账 §1 计数行 vs 实测门禁输出 |

### 1.2 流水线轨（**真正的关键路径**）

**实测硬事实**：`tools/l1{1,2,3}_*.py` 把产品写死为常量 —— 不是配置。

| 文件:行 | 内容 |
|---|---|
| `tools/l11_extract_evidence_spans.py:73` | `PRODUCT_ID = "PROD-CM-001"` |
| `tools/l12_detect_conflicts.py:46` | 同上（且输出路径全部写成 `PROD-CM-001.*`） |
| `tools/l13_apply_decisions.py:40` | 同上 |
| `tools/l13_publish_release.py:52` | 同上（`04_serve/interpretation/PROD-CM-001.json` 亦硬写） |

**产物覆盖缺口（13 张产品卡）**：

| 产物类别 | 已存在 | 待生成 | 目录 |
|---|---:|---:|---|
| source-versions（源级） | 3（仅 CM 三源） | 8 源待跑 | `02_work/source-versions/` |
| fragments（源级） | 3 | 8 | `02_work/fragments/` |
| evidence-spans（源级） | 4 | 7 | `02_work/evidence-spans/` |
| assertions（卡级） | 1 | **12** | `02_work/assertions/` |
| candidate-cards（卡级） | 1 | **12** | `02_work/candidate-cards/` |
| conflicts（卡级） | 1 | **12** | `02_work/conflicts/` |
| health reports（卡级） | 1 | **12** | `02_work/reports/` |
| interpretation（卡级） | 1 | **12** | `04_serve/interpretation/` |
| rule-packages（卡级） | 1 | **12** | `04_serve/rule-packages/` |
| releases（卡级） | 1 | **12** | `04_serve/releases/` |

⇒ **卡级待生成产物单元 = 7 类 × 12 卡 = 84 个**（这是 PC8 的主体工程量，而不是造数）。

### 1.3 检索与消费轨

| 项 | 现状 | 剩余 |
|---|---|---|
| LightRAG HTTP 出口 | **不存在**（`retrieve_via_lightrag` 仅 service 层；`server.py` 无 lightrag 引用） | 新增 `POST /v1/retrieval/query`（`CR-5`） |
| 灌入白名单 | `EGRESS_ROOTS=("03_core","04_serve")`（`services.py:49`） | 在白名单内灌入（`01_raw/**` 一律 REFUSED） |
| 索引重建 | ADR-017 §8 已有基线/回退凭据 | 按判据实跑一次并留证 |
| 解读页 8 章 | `check_interpretation_api.py` + `interpretation-api.openapi.json` 已在 | 13 卡 × 8 章联调 + 出处回填 |
| `90_control/decisions/` | **未物化** ⇒ Release 只能 `DRAFT`、`publishedAt=null` | Owner 签署决策文件（`B-2`） |

---

## 2. 波次串并行编排（DAG）

```
W1（三路并行，互不阻塞）
 ├─ PC8-src-batch-b4b6     [feature_pilot]  造数 6 份 + 登记
 ├─ PC8-tools-byproduct    [tech_lead]      去硬编码 + 13 卡跑通 l10→l13   ← 关键路径
 └─ PC8-reg-cb001-naming   [tech_lead]      REG-CB-001 指名 + 台账 V1.1
        │
        ├──► W2（合流点）源集齐 × 工具就绪 ⇒ 跑全链，产物 84 单元批量生成
        │        门禁：check_all（gits 4 + KERT 6）全绿
        │
        ├──► W3（Owner 签署，阻塞非技术）
        │        B-2 90_control/decisions/signed.json ⇒ Release PUBLISHED / RECOMMENDATION 判定
        │
        └──► W4  PC8-retrieval-endpoint  [tech_lead]  CR-5 端点 + 灌入 + 索引重建
                 门禁：make generate / make check / check_all
                     │
                     └──► W5  PC8-interpretation-e2e  [feature_pilot]  8 章联调 + 出处回填
                              门禁：check_interpretation_api + check_all
                                  │
                                  └──► 独立 QA（每 loop 的 independent_qa，非 self-attest）
```

**并行收益**：W1 三路无相互依赖 ⇒ 可同时开工；W2 之前**不得**启动 W4/W5（无 Release 产物可灌、无 interpretation 可联调）。

---

## 3. 派工（已实际创建，非纸面）

每批次均已用 `scripts/new_loop.py` 落地并过 `scripts/loop_guard.py`（**逐 loop PASS**）：

| loop_id | 角色（实施） | 波次 | gates（唯一命令源 = `LOOP.yaml`） | 依赖 |
|---|---|---|---|---|
| `PC8-src-batch-b4b6` | `feature_pilot` | W1 | `registry_consistency` · `unified_gate` | 无 |
| `PC8-tools-byproduct` | `tech_lead` | W1 | `contract_check` · `unified_gate` · `l13_release` | 跑全链需造数完成 |
| `PC8-reg-cb001-naming` | `tech_lead` | W1 | `registry_consistency` · `unified_gate` | 无 |
| `PC8-retrieval-endpoint` | `tech_lead` | W4 | `contract_generate` · `contract_check` · `unified_gate` | `tools-byproduct` |
| `PC8-interpretation-e2e` | `feature_pilot` | W5 | `interpretation_api` · `unified_gate` | `byproduct` + `retrieval` |

**gate 命令（绝对可执行，与 `specs/product-knowledge/check_all.py:28` 既有 KERT 路径约定一致）**：

```
registry_consistency : python3 /home/szf/dev/Leibniz-KERT/examples/product-recommendation-assets/tools/check_registry_consistency.py
l13_release          : python3 /home/szf/dev/Leibniz-KERT/examples/product-recommendation-assets/tools/check_l13_release.py
unified_gate         : python3 specs/product-knowledge/check_all.py
contract_check       : make check
contract_generate    : make generate
interpretation_api   : python3 specs/product-knowledge/check_interpretation_api.py
```

**每批次的留证纪律（协议强制，非建议）**：gate 标 `pass` 必须同时具备 `exit_code=0` + `actor` + `actor_role` + `executed_at` + `evidence_file`（须在该 loop 的 `evidence/` 下）+ 与文件实测一致的 `output_sha256`；**`manual:` 类 gate 永远不得声称 pass**。失败如实记 `fail` 并留证据 —— 比伪造 pass 有价值。

派工卡正文落在各批次 `loops/<id>/memory/waves/W0-PLAN.md`（含目标/交付物/完成判据/边界/起手第一动作）。

---

## 4. 阻塞项（不属技术可实现，须 Owner 拍）

| # | 阻塞 | 影响面 | 我的建议 |
|---|---|---|---|
| `B-1` | `CR-5` 合同签署（新增检索端点） | W4/W5 全部 | 签（纯新增，不动既有面） |
| `B-2` | `90_control/decisions/signed.json` 未签署 | Release 恒为 `DRAFT`、`publishedAt=null`、`RECOMMENDATION` 不可用 | 出决策文件模板，由 Owner 签 |
| `B-3` | `D-R2`：`REG-FIN-002` 条件性（是否涉线上化放款） | 该 source_id 入库与否 | 业务口径判定；否则登记「不适用+理由」，**不删行** |
| `B-4` | 真实源 19 份上传义务 | `19/28` 缺口、字段长期「未核验」 | 不属 TL 可闭合；DEMO 轨不抵扣 |

---

## 5. 验收矩阵

| 层 | 命令 | 现状基线 | 目标 |
|---|---|---|---|
| 源登记 | `check_registry_consistency.py` | **131/131 PASS** | 随 B4–B6 增至 17 源全绿 |
| 合同（gits） | `make check` / `check_all.py` gits 4 项 | 绿 | 保持绿（CR-5 后重新生成） |
| 流水线（KERT） | `check_l10/l11/l12/l13_*.py` | 仅 CM 系通过 | 13 卡逐卡通过 |
| 解读 API | `check_interpretation_api.py` | 绿 | 13 卡响应合法 |
| loop 合规 | `scripts/loop_guard.py` | **68/68 合规** | 保持 0 违规（本次新增 5 批次未破基线） |
| 独立 QA | 每 loop `independent_qa` block | pending | 5 次独立复核 |

**fail-closed 红线（沿用 ADR-017，不新造）**：索引重建期检索不可用 ⇒ 返回 `LIGHTRAG_*` 三码，**禁止返回空结果冒充成功**；LightRAG 是派生检索层，**字段值不得取自检索**。

---

## 6. 立即动作（TL 侧，不等 Owner）

1. `PC8-src-batch-b4b6` 已开工：B4 三份（对齐 `REG-TF-001/002/003` 分工，行内制度只写操作与授权）；
2. `PC8-tools-byproduct` 起手：出「硬编码点清单 + 参数化最小 diff + 字节不变性对照方案」，**先方案后改码**；
3. `PC8-reg-cb001-naming` 起手：判定能否取得逐字全文的官方承载，取不到即如实记 `blocked`。

## 7. 边界

未改任何合同 schema / 不变式 / `EGRESS_ROOTS`；未灌入任何文档；未生成任何流水线产物（`02_work`、`04_serve` 保持仅 CM 系既有件）；KD 工作区在飞改动零夹带。

---

## 8. 签署登记（append-only）

| 时间 | 事项 | 签署人 | 处置 | 影响 |
|---|---|---|---|---|
| `2026-09-22T09:28:35+00:00` | **`CR-5` 新增检索出口（`POST /v1/retrieval/query`）** | Owner | **批准** | 解除 `B-1`；`PC8-retrieval-endpoint` 由 `blocked` 转可开工（W4 设计/实现可并行前置） |

**批准范围内的口径冻结（TL 执行，越界即回问）**：
1. **纯新增**：不动既有 `/v1/search`、`/v1/data/query`、`/v1/entities/*`、`/v1/evidence/*` 的语义与响应；
2. 响应必须带**可回译出处**（`docId`/`chunkId`）与 `evidenceClass` / `simulationOnly`；
3. **fail-closed**：索引不可用 ⇒ 返回 `LIGHTRAG_*` 三码，**禁止空结果冒充成功**；
4. **不扩 `EGRESS_ROOTS`**（`CR-4` 仍未动）；`01_raw/**` 一律 `LIGHTRAG_ARTIFACT_REFUSED`；
5. LightRAG 保持**派生检索层**：字段值不得取自检索。

**仍未解除**：`B-2`（`90_control/decisions` 签署 ⇒ Release 仍 `DRAFT`）、`B-3`（`D-R2`）、`B-4`（真实源 19 份）。
