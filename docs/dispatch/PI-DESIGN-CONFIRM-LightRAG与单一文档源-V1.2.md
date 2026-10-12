# 设计确认 V1.2（更正 V1.1；PC8 登记；造数落位的合同前提）

```text
提交人：tech_lead（TL）｜ 时间：2026-09-22
输入：Owner 2026-09-22 —— ①「PC8 = 新增阶段 = 文档→LightRAG→解读链路」（OD-PI-13）
                        ② KERT 写入许可：按 L-A 落造数区（本地提交、不 push，OD-PI-09）
                        ③ 造数落位 = L-A；C-2 派生层确认
状态：**本件更正 V1.1 的 4 条断言**（§0）；给出造数生效的**合同前提**（§3）与施工步序（§4）
```

## 0. 本件更正 V1.1（我自己的错误，不修改 V1.1 原文，按 F 记录）

| # | V1.1 的断言 | 事实 | 证据 |
|---|---|---|---|
| `C-1` | 「造数落 `01_raw/_sim/` 即可」（L-A） | ❌ **不可实施**：`sourcePath` 机器强制前缀只有两个 ⇒ `_sim/` 下**任何文件都无法被 EvidenceRef 引用**（schema 直接拒） | `specs/product-knowledge/evidence-ref.schema.json:84` `pattern: "^01_raw/(_authoritative\|_public_reference)/"` |
| `C-2` | 「TL 把产品文档灌进 LightRAG」 | ⚠ **受白名单限制**：数据出口只允许 `03_core`/`04_serve`，`01_raw/**` 一律 **`LIGHTRAG_ARTIFACT_REFUSED`** | `src/kert/application/services.py:49` `EGRESS_ROOTS=("03_core","04_serve")`、`:76-78`；ADR-017「数据出口」① |
| `C-3` | 「S-1 第 4 项 = 新增 `POST /v1/retrieval/query`」 | 事实：**KERT 无 LightRAG 的 HTTP 出口**（`retrieve_via_lightrag` 仅在 service 层 `services.py:554`）；既有 `/v1/search`、`/v1/data/query`、`/v1/graph/query` 是**确定性检索面**（Kùzu+Parquet），**不是** LightRAG | `src/kert/api/server.py:616-646`（handler 调 `svc.search`/`svc.data_query`），全文无 lightrag 引用 |
| `C-4` | 「`_authoritative/` = 1 份 PDF + 1 份 DEMO 源」 | ❌ 实际 = 1 份 PDF + **3 份 `SRC-CM-00X.DEMO.md`** | `git ls-files examples/product-recommendation-assets/01_raw/` |

⚠ **`_authoritative/README.md` 的"当前状态"仍只登记 `REG-CM-001`**，那 3 份 DEMO 源**未在登记表出现**（登记与实体不一致）。

## 1. 三决策登记

| 编号 | 决策 | 状态 |
|---|---|---|
| `OD-PI-13` | **`PC8` = 新增阶段**：造数 + 灌入 LightRAG + 索引重建判断 + 检索出口；**不动 `PC0`–`PC7`**；与 `PC6` 全量验收并列 | `OWNER_DECIDED` 2026-09-22 |
| `L-1` | 造数落位 = **`L-A′`**（第三区 `01_raw/_sim/`；见 §3 前提） | `OWNER_DECIDED`（L-A）→ **TL 更正为 L-A′**，待 §3 批准 |
| `C-2` | LightRAG 为**派生检索层**：只做定位与召回，**字段值仍来自受控知识版本**（ADR-017「不是事实源」） | `OWNER_DECIDED` 2026-09-22 |

## 2. 新发现的既有风险（`F-KERT-01`，与本任务无关但被顺带发现）

`01_raw/_authoritative/` 的语义是「**产品卡字段的唯一合法 EvidenceRef 来源**；**可支撑产品卡转 `ACTIVE` + `FROZEN=YES`**」（`_authoritative/README.md`）；
而该目录下**已提交跟踪** 3 份 `SRC-CM-00X.DEMO.md`（DEMO 造数）。
⇒ **一旦被产品卡引用，DEMO 造数即可把产品卡推向 `ACTIVE`**，与 SIM 硬约束（造数不得支撑 ACTIVE）直接冲突。

**建议**：把这 3 份迁入第三区 `_sim/`（或降级为 `_public_reference/`），门禁上明确「DEMO/SIM ⇒ 永久 `CANDIDATE`」。**本件不动 KERT 既有文件**，仅登记。

## 3. 造数生效的合同前提（请 Owner 一次批准）

**核心事实：造数要能"生效"（被产品卡/解读引用），必须先扩 `sourcePath` 前缀 —— 这是本链路真正的第一块砖。**

| 编号 | 变更 | 精确落点（最小 diff） | 影响面 |
|---|---|---|---|
| `CR-1` | `sourcePath` 前缀增第三区；`usage` 枚举增 `SIMULATED` | `specs/product-knowledge/evidence-ref.schema.json:84` `pattern` ⇒ `^01_raw/(_authoritative\|_public_reference\|_sim)/`；`:176` `enum` ⇒ `["AUTHORITATIVE","VERIFICATION_ONLY","SIMULATED"]`；`usageRule`（`:25-42`）增第三轨；`gateRule` 增「引用 `SIMULATED` 的产品卡**永久 `CANDIDATE`**」 | gits 合同；需 `make generate` + `make check` + `CONTRACT_INDEX` 登记 |
| `CR-2` | path↔usage 一致性门禁同步 | schema 自述「**由 PI-1 G1-5 门禁代码校验，本 schema 不做机器强制**」（`:42 knownGap`）⇒ 门禁代码须加第三区映射 | gits 门禁代码 + 测试 |
| `CR-3` | KERT 侧第三区语义登记 | `examples/product-recommendation-assets/01_raw/source-registry.md` §1 双区 ⇒ 三区；`01_raw/_sim/README.md`（本件已落，见 §5） | KERT `01_raw`（**目标路径当前零改动**，已核） |
| `CR-4` | ADR-017 出口白名单 | **默认不动**（`EGRESS_ROOTS` 保持 `03_core`/`04_serve`）⇒ 索引内容来自 `03_core`/`04_serve` 产物。若要把 **SIM 原文本体**灌入索引，须**另立 ADR 变更**（Owner 批准 + 改出口测试） | KERT `src/`；⚠ `docs/adr/ADR-017-*.md` 当前**有他人在飞改动**，我不动 |
| `CR-5` | 新增检索 HTTP 出口（把既有 service 暴露） | KERT `src/kert/api/server.py` 增 `POST /v1/retrieval/query` ⇒ 调 `retrieve_via_lightrag`（**纯新增**，不改既有端点）；响应含 `filePath`（由 `artifact_file_source` 编码、`parse_artifact_file_source` 可回译）、`chunkId`、`evidenceClass`、`simulationOnly`；不可达 ⇒ 既有三码 fail-closed | KERT 服务端 + v2 candidate 登记 + 消费方（gits 解读） |

**不可让步项**（沿用既有纪律）：① 检索失败**禁止空结果**（`LIGHTRAG_UNAVAILABLE`/`LIGHTRAG_HTTP_ERROR`/`LIGHTRAG_RESPONSE_INVALID`）；② 字段值**不得**来自检索结果；③ 造数**绝不**写入 taxonomy / `CONTRACTS_INDEX` / 产品卡 HardRule 字段。

## 4. PC8 施工步序（合同先行）

```text
8-1 合同变更：CR-1 + CR-2 + CR-3（含门禁与测试）
8-2 造数：SIM 原始产品文档集（按 §5 规范 + 模板），登记进 source-registry
8-3 结构化：SIM 源 → 03_core 产物（既有 pipeline）
8-4 灌入：既有受控通道发布 03_core/04_serve（白名单不动，即 CR-4 默认）
8-5 检索出口：CR-5 端点 + 出处回译（docId/chunkId 入解读）
8-6 索引重建：清单与判据固化
```

**索引重建判据（引 ADR-017 实测口径，不拔高）**：清空 ⇒ 用**同一文档集**重灌 ⇒ **覆盖与出处一致**
（6 个 query×mode 的出处集合 Jaccard = 1.00，出处全集相同）；**不主张**逐字/逐实体一致
（实体集不稳定：实测 J = 0.36/0.13/0.23；`naive` 模式才完全一致）。
操作与回退凭据见 ADR-017「⑧ 清空-重建」。

## 5. 本件已落 / 未落

| 项 | 状态 |
|---|---|
| KERT `01_raw/_sim/README.md` + `_TEMPLATE.SIM.md` | ✅ 已落（**仅新增文件**；未改任何既有文件） |
| KERT 既有文件（`source-registry.md`/`ADR-017`/`src/**`） | ❌ 未动（前者待 `CR-3` 批准；后者有他人在飞） |
| 造数正文（SIM 原始产品文档 13 份） | ⏸ 待 `CR-1` 批准（否则造了也引用不了） |
| gits 合同 `evidence-ref.schema.json` | ❌ 未动（双轨→三轨属 Owner 级裁决，待批） |

## 6. 请 Owner 裁一条（其余我按默认执行）

**批准 `CR-1`+`CR-2`+`CR-3`（新增第三轨 `SIMULATED`）吗？**
- **批准** ⇒ 我按 §4 步序开工，造数正文随即批量落；`CR-4` 保持默认（白名单不动）。
- **不批准** ⇒ 替代方案 `L-A″`：造数改用既有 `_public_reference/`（`usage: VERIFICATION_ONLY`，**零合同变更**，效果同为"永久 `CANDIDATE`"），代价是语义上把"我们造的"与"公开资料"混在一区。

## 7. 边界

未改 gits 受控合同、未改 KERT 既有文件、未灌入任何文档到 LightRAG、未动 `specs/`；
本件不构成验收、激活或生产可用结论。
