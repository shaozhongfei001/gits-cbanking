# 检索层换模型一页纸（LightRAG · Ollama 可行性确认 + 建议）

> 问题：真实 LLM/embedding 是否指 LightRAG 所需模型？LightRAG 是否自带 Ollama 小模型？
> 结论：**能用，且本机已具备一切条件**。本文给出确认依据、方案对比与我的推荐；**执行需你点头**（换模型会停实例 + 重建索引）。

## 1. 确认（实测，非推测）

| 问题 | 事实 | 证据 |
|---|---|---|
| 是不是指 LightRAG 所需的模型？ | **是，且是两个模型**：**LLM**（索引期做实体/关系抽取、查询期提关键词）+ **Embedding**（向量检索） | 当前实例 env：`LLM_MODEL=mock` + `EMBEDDING_MODEL=mock-embed` + **`EMBEDDING_DIM=64`**（假向量） |
| LightRAG 是否"自带"Ollama 小模型？ | **不是"自带模型"**，而是**原生支持 Ollama 作为 binding**（模型要本机自己装） | 包 `lightrag_hku-1.5.7`；`lightrag/llm/binding_options.py:625` = `ollama_embedding`、`:656` = `ollama_llm` |
| 本机能不能用？ | **能**：Ollama 已装并在跑（`:11434` 监听），且已有可用模型 | `ollama list`：`all-minilm:l6-v2`（45 MB，embedding）、`qwen3:8b`（5.2 GB）、`gemma4:12b-it-qat`（7.2 GB） |
| 硬件够不够？ | 够：**20 核 / 62 GB 内存（20 GB 可用）/ RTX 3060 6 GB 显存** | 显存是唯一约束 ⇒ 一次只放一个 8B 量化模型 |

> 注：当前 `:9630` 是 `scripts/ci/lightrag_mock_llm.py`（CI 假模型），`EMBEDDING_DIM=64` 是伪装维；**换真实模型后维度变化，索引必须重建**。

## 2. 方案对比（三选一）

| 方案 | LLM | Embedding | 优点 | 代价 |
|---|---|---|---|---|
| **A（推荐，先跑通）** | `qwen3:8b` | `all-minilm:l6-v2` | **零下载**（都已在本地）；5.2 GB 显存可控；中文 LLM 尚可 | all-minilm 维度仅 384 ⇒ 检索召回偏弱 |
| **B（质量优先）** | `qwen3:8b` | `bge-m3`（需下载 ≈1.2 GB） | 多语言/中文强，LightRAG 社区常用组合 | 需联网下载；维 1024 ⇒ 索引更大、重建更慢 |
| **C（最轻但慢）** | `gemma4:12b-it-qat` | `all-minilm:l6-v2` | 模型已在本地 | 7.2 GB **超过 6 GB 显存** ⇒ 落 CPU，抽取很慢 |

**我的推荐：A** —— 先用零下载组合把"真实模型端到端"跑通并测出质量基线，再决定是否升 B（bge-m3）。理由是：先把链路与判据立起来，比一次性上最优模型更能定位问题。

## 3. 执行时会动的 env（当前无 `.env` 文件，由启动环境传入）

```text
LLM_BINDING=ollama                         # 现为 openai（指向 :9630 mock）
LLM_BINDING_HOST=http://127.0.0.1:11434
LLM_MODEL=qwen3:8b                         # 现为 mock
EMBEDDING_BINDING=ollama                   # 现为 openai
EMBEDDING_BINDING_HOST=http://127.0.0.1:11434
EMBEDDING_MODEL=all-minilm:l6-v2           # 现为 mock-embed
EMBEDDING_DIM=384                          # 现为 64 ⇒ **维度变了，旧索引不可用**
WORKING_DIR=/tmp/lightrag-storage-v2       # 新目录：避免与旧维索引混用
LIGHTRAG_API_KEY=ci-retrieval-key          # KERT→LightRAG 的键（KERT 侧环境需一致）
```

## 4. 三个必须同时考虑的影响

1. **索引必须清空重建**：`EMBEDDING_DIM` 由 64 → 384（或 1024）⇒ 旧向量库不可复用。ADR-017 已有对应判据（清空 ⇒ 同集重灌 ⇒ 核对覆盖与出处一致）。
2. **重建期检索不可用**：重建期间 `POST /v1/retrieval/query` 会**具名失败**（fail-closed，不会返回错结果），KERT 消费方须有缓存/离线路径。规模：现索引 **26 篇**文档；单篇要走 LLM 抽取，按 CPU/GPU 分配不同，**量级约 10~40 分钟**。
3. **质量与合规的口径（不要拔高）**：全本地、**零数据出境**（合规最简）；但**小模型 + DEMO 语料**的检索结果**仍不得作业务结论**——ADR-017 的「非声明」段明确「不代表 LightRAG 检索结果可作业务结论或事实来源」。

## 5. 方案 A 实测记录（2026-09-23，已执行 → **卡死 → 已回滚**）

按 ADR-017「⑧ 清空-重建」顺序执行：备份（`cp -a`，`diff -rq` **0 差异**）⇒ 停服 ⇒ 起新实例
（`OLLAMA_LLM_THINK=false` + `LLM_TIMEOUT=600` + `WORKING_DIR=/tmp/lightrag-storage-v2`）⇒ 灌入 39 篇。

| 观测 | 结果 |
|---|---|
| Ollama embedding | ✅ `all-minilm:l6-v2` 返回 **384 维**、加载 GPU |
| `think=false` 是否生效 | ✅ 实例日志 `Ollama LLM Options: {'think': False}`（extract/keyword/query/vlm 全生效）⇒ **0 篇失败**（调参前是 3 篇 `httpx.ReadTimeout`） |
| 空库确认 | ✅ 文档数 0（新目录） |
| 灌入吞吐 | ❌ **25 分钟 `processed = 0`**，流水线**卡死**：`cur_batch` 与 `latest_message` 连续 4 分钟完全不变 |
| 根因 | `qwen3:8b` 占 **6.0 GB**、本机显存 **6 GB**（日志 `18%/82% CPU/GPU` ⇒ 部分 CPU offload）；叠加 Ollama **`keep_alive=5m`** ⇒ 模型被反复卸载/重载（观测到 `Stopping...`） |
| 处置 | **回滚**：停新实例 ⇒ 用旧 env 起原实例 ⇒ 26 篇 `processed` 全恢复 ⇒ KERT 检索 `200`/`DEMO`/`entities 31` ⇒ **服务未留半截状态** |
| 回退凭证 | 旧索引备份 `/tmp/lightrag-storage.bak-TL-20260923`（12 M / 12 文件，`diff -rq` 0 差异）；新目录 `/tmp/lightrag-storage-v2` 保留待用 |

**结论：方案 A（8B）在本机 6 GB 显存下吞吐不可行**——可用（不报错）但**不实用**（数十分钟到数小时且易卡）。

## 6. 已裁定：**不可用** —— IDE（CodeBuddy）会话的大模型（2026-09-24）

提问：能否用 IDE 会话所用的云端大模型给 LightRAG 当 LLM？
**裁定：不能。** 三层理由（均已核实）：

1. **拿不到端点（事实）**：环境内 CodeBuddy 变量只有 `SESSION_ID` / `EH_AFFINITY` / `EH_ROLE` /
   `NODE_BIN` / `SAFE_DELETE_*` / `COPILOT_INTERNET_ENVIRONMENT` / `TOOL_CALL_ID`，
   **无任何模型 API 端点或凭据**；也无 `OPENAI_*` / `ANTHROPIC_*` / `AZURE_*` 等端点变量。
   IDE 的模型在 IDE 进程内经其自有鉴权通道使用，**不向终端/其他进程暴露**。
2. **架构上会成为"不可重建的外部依赖"**：检索层若依赖 IDE 会话 ⇒ 会话结束/IDE 关闭/额度变化即失效，
   与 ADR-017「LightRAG 是**可重建的派生层**」及本项目一路在守的 **fail-closed / 可复现 / 可审计** 直接冲突。
3. **合规属 Owner 权限**：把 KERT 产品解读内容发往 IDE 平台云端＝**数据出本机并交由外部处理**，
   需 Owner 明确批准；TL **不自行决定**，也不翻 IDE 登录态/凭据转给业务组件。

**但提问切中了要害——这个方向是对的**：把 **LLM 移出本机**确实能绕开 6 GB 显存瓶颈
（本地只留 embedding `all-minilm:l6-v2`，仅 45 MB，几无显存压力）。
正确载体是**项目/企业自有的模型服务**，而非 IDE 会话。

> 技术补充：IDE 会话模型通常是 chat/LLM，**不提供 embedding 端点** ⇒ 即使能接，
> embedding 仍须来自本地或另一服务。**LLM 外移 + embedding 本地**是可行组合。

**合规等价方案**（你提供，我即刻执行）：
```text
LLM_BINDING=openai
LLM_BINDING_HOST=<你给的 OpenAI 兼容端点>
LLM_MODEL=<模型名>
LLM_BINDING_API_KEY=<你给的凭据>
EMBEDDING_BINDING=ollama            # 本地，45 MB，无压力
EMBEDDING_MODEL=all-minilm:l6-v2
```
前置：① 端点与凭据；② **书面确认允许本项目 DEMO 数据发往该服务**（合规批准）。

## 7. 修订后的建议（请选一项）

| 选项 | 做法 | 说明 |
|---|---|---|
| **① 推荐** | 下载 **4B 级** LLM（`qwen3:4b` 或 `gemma3:4b`，≈2~3 GB） | 显存宽裕（≈3 GB < 6 GB）⇒ 无 offload、`keep_alive` 压力小 ⇒ 预计**数倍提速**；**需联网下载** |
| ② | 保留 `qwen3:8b`，设 **`OLLAMA_KEEP_ALIVE=-1`**（模型常驻）+ `LLM_TIMEOUT` 加大 | 消除反复加载开销，但单篇仍慢；灌入仍需数十分钟 |
| ③ | 缩小灌入范围（只灌 `04_serve/interpretation` 13 篇，而非 39 篇） | 时间约 ÷3；代价是 `rule-packages` 不入索引 |
| ④ | **不换模型**，维持 mock | 检索链路可用、判据完备；但**实体/关系是假模型抽取** ⇒ 检索质量**不可作能力证明**（须如实声明） |

**当前状态＝选项 ④**（已回滚），且诊断仪 `D4` 仍是 `DEFECT`：如实反映了"模型仍是 mock"。

## 8. 我的建议动作顺序（等你一声）

```text
[ ] 1. 你选 A / B / C（或指定其他 Ollama 模型）
[ ] 2. 我停 LightRAG 实例 → 用新 env 起（新 WORKING_DIR）
[ ] 3. 我按 ADR-017 判据重建索引：清空 → 同集重灌 → 核对覆盖与出处一致
[ ] 4. 我跑诊断仪：期望 D4（LLM=mock）转录 OK、D3 仍 OK
[ ] 5. 若质量不满意 ⇒ 再评估升 bge-m3（方案 B）
```

**注意 D4 的判定口径**：诊断仪现在把 `LLM_MODEL=mock` 或 host 指向 `:9630` 判为 DEFECT。换成 Ollama 后应转 `OK`；若你把模型都换成真实 Ollama 而 D4 仍报 DEFECT，说明 host/model 口径没落对，我会先查再报。

**风险与回滚**：旧实例 env 已备份（`/proc/<pid>/environ` 快照，见交接单）；回滚＝用旧 env 起回 `WORKING_DIR=/tmp/lightrag-storage`（旧索引仍在，未被删除）。
