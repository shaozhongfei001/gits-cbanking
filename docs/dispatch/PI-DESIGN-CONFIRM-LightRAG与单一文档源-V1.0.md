# 设计确认：单一原始产品文档源 + 文档经 LightRAG 进入产品解读

```text
提交人：tech_lead（TL）｜ 时间：2026-09-22
触发：Owner 提出开工前提——① 新需求与 PC8 使用**相同的原始产品文档**；② 新需求下产品文档应**进入 LightRAG**，再进入产品解读功能
结论：**有条件确认**（4 项条件见 §5）；其中 1 项会改变已提交的合同提案集合，**故 S-1 的契约文本变更应先扩充再签**
```

## 1. 我方核到的现状（全部实测，非推断）

| 项 | 事实 | 证据 |
|---|---|---|
| LightRAG 是否已存在 | **是**。KERT 已接入外部 LightRAG server | `Leibniz-KERT/docs/adr/ADR-017-lightrag-retrieval-store.md`（状态 **APPROVED**，Owner 2026-09-16 裁定"按建议"） |
| 形态 | **形态 (i)**：外部只读接入；索引位于 KERT 工作区**之外**（`/home/szf/dev/lightrag/rag_storage`）；连接参数 `KERT_LIGHTRAG_URL` / `KERT_LIGHTRAG_API_KEY` / `KERT_LIGHTRAG_TIMEOUT`；embedding 走 Ollama `11434` | ADR-017「决策」「边界」 |
| 调用方式 | `POST /query/data` 取**实体 + 关系 + 出处**；实现 `src/kert/infrastructure/lightrag_client.py` + `KnowledgeService.retrieve_via_lightrag`；另有 `publish_artifact` / `retract_artifact`（数据出口） | ADR-017「实现」 |
| **角色定位（关键）** | **不是事实源**：KERT **只读**消费，**不写回** `01_raw`/`02_work`/`03_core`/`04_serve`；**知识权威源仍是文件树**（"文件目录为权威源"原则未变）；索引是**派生物**，整体丢弃不影响任何 KERT 产物 | ADR-017「边界」「论证」 |
| 失败语义 | 不可达/超时 ⇒ `LIGHTRAG_UNAVAILABLE`；非 2xx ⇒ `LIGHTRAG_HTTP_ERROR`；形状不符 ⇒ `LIGHTRAG_RESPONSE_INVALID`；**禁止返回空结果**（不静默） | ADR-017「边界」 |
| 现规模 | 清空后由 KERT 产物重灌：**5 篇文档 / 78 节点 / 86 边**（ADR-017 实测） | 同上「① 可重建性」 |
| 运行痕迹 | 真实运行日志（KG 重建、chunk flush、文档删除、storage finalize、uvicorn 启停），最后活动 **2026-09-17** | `Leibniz-KERT/lightrag.log` |
| KERT 对外端点现状 | 已有 `GET /v1/knowledge-maps`、`GET /v1/knowledge-maps/{mapId}`、`POST /v1/routing/plan`（合同 `1.4.0 → 1.5.0` 纯新增）；**未发现**对外的 LightRAG 检索端点 | `Leibniz-KERT/evidence/m7-3/EVIDENCE-ROUTING-API.md` |
| **PC8** | **两个仓库零命中**（`grep -rn "PC8"` 在 gits 的 `docs/ specs/ loops/`、KERT 全仓、`gits-kert-docs`、`deliverables` 均无定义；唯一命中是无关的 SIM 规则 ID `SIM-RULE-PC-8`）。我方既有 Loop 序列为 `PC0`/`PC1`/`PC-i1` | 检索命令与结果见 §6 |

## 2. 对前提 ①「新需求与 PC8 使用相同的原始产品文档」

**确认：赞成，但需补 3 项定义，否则必然漂移。**

| # | 必须明确的定义 | 为什么（现状证据） |
|---|---|---|
| `D-1` | **"原始产品文档"的具体集合与层级**：是 `01_raw`（权威原文，现 27 源 `PENDING_SOURCE`）还是 `03_core/*/product-cards/PROD-*.md`（13 张产品卡，`CANDIDATE`）？ | 现状两条链分别读不同层：产品解读读**产品卡**；权威材料在 `01_raw` 且大多未入库 |
| `D-2` | **版本与一致性校验**：同一文档集合的版本号 + `sha256` 清单，两条链路（新需求 / PC8）**必须以同一清单为输入** | 现状：产品卡按 `version=YYYY.MM.DD.N` 目录分版；缺跨链路一致性校验 |
| `D-3` | **唯一写入入口**：谁把文档写入 LightRAG（KERT 侧 `publish_artifact`？还是文档 Owner？），以及**索引重建的责任与频率** | ADR-017 已有 `publish_artifact`/`retract_artifact`，但未定义产品文档的灌入责任人 |

**建议**：以 **`01_raw` 为权威原文层、`03_core` 产品卡为结构化层**，两者构成"同一份文件树"；两链路共享 `D-1/D-2/D-3` 的定义与哈希清单。

## 3. 对前提 ②「产品文档进入 LightRAG，然后进入产品解读功能」

**确认：方向可行，但必须锁死 LightRAG 的角色，否则与现行架构原则冲突。**

| 项 | 必须成立的表述 | 依据 |
|---|---|---|
| 角色 | LightRAG = **检索与出处层（派生物，DERIVED）**；**产品解读的字段值仍来自受控知识版本**（审核后的 Release）；LightRAG 只提供**召回与出处定位** | ADR-017「不是事实源」「抽掉它不影响任何产物」 |
| 禁止 | **不得**把 LightRAG 当作字段值来源或权威依据（否则触发 KERT-SPEC-001 §6.3 与 ADR-017 边界） | 同上 |
| 证据定位升级 | 现 `locatorHint` 为文本（如"第十条"）；接入 LightRAG 后应携带**可复算的出处标识**（`docId` + `chunkId`），与 §5-③ 的字段一并设计 | ADR-017：`/query/data` 返回"实体 + 关系 + **出处**" |
| 失败语义 | 检索不可用 ⇒ 沿用 `LIGHTRAG_*` 三码；**禁止静默返回空结果**（解读页应显式提示"出处不可用"而非装作无证据） | ADR-017「边界」 |
| DEMO/SIM 一致性 | 进 LightRAG 的文档同样受 DEMO/SIM 约束 ⇒ 检索结果必须携带来源级别；**不得**因"来自 LightRAG"而显得更权威 | Owner 2026-09-22「DEMO 标识保留、无豁免」；`specs/product-center/README.md` §6.5 |
| 与现有两条读取链关系 | 形成三条链：①卡详情（`CTR-API-001`）②解读三视图（`CTR-PK-INT-001`）③**检索/出处（新增，待定义）**；职责边界须写入合同说明 | R2 `05_合同端点与版本快照映射.md` |

## 4. 对已提交材料的影响（必须先说清，避免白签）

| 影响项 | 说明 |
|---|---|
| **`S-1` 合同提案需扩充** | R2 提交的是**3 项**提案（DEMO 字段 / 版本快照字段 / 路径前缀订正）。本前提成立将**新增第 4 项**：**LightRAG 检索消费 + 出处字段（`docId`/`chunkId`）**，并且第 2 项（`evidence_snapshot_id`）的语义应与出处字段**一并设计** ⇒ **建议 S-1 暂缓契约文本变更，先扩充为 4 项一次签**，否则签完即改 |
| **`I4` 设计顺序** | `I4`（证据可执行）原计划绑定版本/快照字段；现应与 LightRAG 出处字段**合并设计**。`I3`（承接 Release 三视图）**不依赖** LightRAG，可先行 |
| **`PC-i1` 不受影响** | 逐章继承只读产品卡原文，不依赖 LightRAG ⇒ 可继续按已定义 scope 开工（实现仍须 `feature_pilot` 单独上下文） |
| **测试追踪** | 需在 `08_逐项测试追踪表` 增补：检索不可用时的 fail-closed 用例、出处可复算用例、DEMO 来源级别用例 |

## 5. 我方确认的结论（有条件确认）

**确认这两条设计前提，条件如下（4 项，缺一不可）：**

| # | 条件 |
|---|---|
| `C-1` | **补齐 `PC8` 定义**（范围 / 归属仓 / Loop ID / Owner）。当前两仓**零命中**，无法据以做一致性设计 |
| `C-2` | **锁定 LightRAG 的派生层定位**：字段值只来自受控知识版本；LightRAG 仅提供召回与出处；不得作为权威依据 |
| `C-3` | **`S-1` 扩充为 4 项后再签**（新增 LightRAG 检索消费 + 出处字段；第 2 项与出处字段一并设计） |
| `C-4` | **补齐 `D-1`/`D-2`/`D-3`**：原始文档集合与层级、版本+哈希清单、唯一写入入口与索引重建责任 |

满足 `C-1`~`C-4` 后，我将把 ③检索链写入合同提案并提交合同 Owner；在此之前**不改 `specs/`**。

## 6. 检索证据（可复算）

```bash
# LightRAG 在 KERT 的落地
grep -rln "lightrag" /home/szf/dev/Leibniz-KERT --include=*.py --include=*.md | head
head -60 /home/szf/dev/Leibniz-KERT/docs/adr/ADR-017-lightrag-retrieval-store.md
tail -20 /home/szf/dev/Leibniz-KERT/lightrag.log

# PC8 检索（两仓 + 文档仓 + 交付目录均零命中）
grep -rn "PC8" /home/szf/dev/gits-cbanking/docs /home/szf/dev/gits-cbanking/specs /home/szf/dev/gits-cbanking/loops \
             /home/szf/dev/gits-kert-docs /home/szf/deliverables --include=*.md --include=*.yaml --include=*.json
# ⇒ 唯一命中：specs/knowledge-architecture/capabilities/SIM-CAP-PRODUCT-CONDITION.json:117 "SIM-RULE-PC-8"（无关）

# 我方既有产品中心 Loop
ls -d /home/szf/dev/gits-cbanking/loops/PC*
# ⇒ PC0-product-center-baseline / PC1-product-center-shell / PC-i1-chapter-inheritance
```

## 7. 我方不做的推定

- **不**推定 PC8 的含义（不给它编范围）；
- **不**把 LightRAG 写成"事实源"或"权威源"；
- **不**在 `C-1`~`C-4` 满足前修改 `specs/`、合同或实现；
- **不**声称本确认件构成任何验收或激活结论。
