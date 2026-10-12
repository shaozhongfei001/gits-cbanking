# 设计确认 V1.1（Supersedes V1.0 的未决项）

```text
提交人：tech_lead（TL）｜ 时间：2026-09-22
输入：Owner 2026-09-22 对三问的答复 ——
     ① PC8「是你定义的，我理解是在 KERT 全仓」
     ② 「同一份原始产品文档」= **01_raw（权威原文）**
     ③ 「TL 派工智能体通过提前造数（造原始产品文档）把产品文档灌进 LightRAG、索引重建由 TL 判断负责」
状态：**两项确认 + 一项必须澄清（造数落位与权威性）**；PC8 事实结论见 §1
```

## 1. PC8：全仓检索结论 = `NOT_FOUND`

**结论：PC8 在 KERT 仓、KERT git 全历史、gits 仓均无定义；它不是本 TL 定义的标识。**

| 检索范围 | 命令 | 结果 |
|---|---|---|
| KERT 全文件类型（含 py/toml/csv/txt/sql） | `grep -rniE "\bPC-?0?8\b" .` | 命中 **2 个文件，均为第三方二进制**：`.venv/.../playwright/driver/node`、`.venv/.../pyarrow/libarrow.so.2500` ⇒ **误报**，非 KERT 内容 |
| KERT 文件名 | `find . -iname "*pc*8*"` | 仅 `.venv/.../pcg/pcg_uint128.hpp`（pyarrow 自带）⇒ **误报** |
| KERT 提交信息 | `git log --all --grep="PC8" -i` | **0** |
| KERT 全历史内容（含已删除） | `git log --all -S"PC8"` | 仅 `4a4991e`（initial baseline）；`git grep -l "PC8" 4a4991e` **无输出** ⇒ 命中来自**二进制**，非文本定义 |
| KERT 分支 | `git branch -a \| grep -iE "pc\|phase"` | **0** |
| gits 全仓 | `grep -rn "PC8" docs/ specs/ loops/` | **0** |

**本 TL 实际定义的阶段序列（`OD-PI-07`，`TL_DECIDED` 2026-09-20）是 `PC0`–`PC7`：**

| Loop | 目标 | 估算 |
|---|---|---:|
| PC0 | 基线与契约（菜单/路由/骨架；14 端点合同登记；DEMO 隔离方案） | 5–7 人日 |
| PC1 | 页面骨架与目录（环境条/三栏/目录/首屏/章节导航/三档基线） | 6–8 |
| PC2 | 核心产品解读（60 秒读懂、核心条款表、适用边界、三类前提、办理流程与例外） | 8–10 |
| PC3 | 材料、价格与协议（三类材料、价格构成、可说/不可承诺、敏感价格分级） | 7–9 |
| PC4 | 比较、FAQ 与知识治理 | 6–8 |
| PC5 | 下载、生成、助手与审计 | 7–9 |
| PC6 | 全量验收（`PI-AT-001`–`086`、性能、安全、E2E、独立 QA） | 8–12 |

关键路径：`PC0 → PC1 → PC2 →（PC3 ∥ PC4）→ PC5 → PC6`。
`PC7` **只出现在命名范围**（`OD-PI-07`）中，**未赋内容**；`PC8` 从未出现。

**三种可能，请你点一个（我不替你定）：**

| 选项 | 含义 |
|---|---|
| `P-A` | 你按"第 8 个阶段"计数（0 基编号）⇒ 指 **PC7**（命名范围内、内容未赋） |
| `P-B` | 你指 **PC6（全量验收）之后的下一阶段**（即新增一个 PC7/PC8 用于"文档→LightRAG→解读"链路改造） |
| `P-C` | 另有出处（别的仓/别的命名），请给路径，我按原文对齐 |

> 在 `P-A`/`P-B`/`P-C` 判定前，**"新需求与 PC8 使用同一份原始文档"这条前提无法落成可验收条件**（因为找不到对手方）。

## 2. 已确认：共享层 = `01_raw`（权威原文）

| 项 | 结论 |
|---|---|
| `D-1` 文档层级 | ✅ **确认**：`01_raw`（权威原文）为两链路共享的原始文档层 |
| 现状事实 | `01_raw/_authoritative/` 现有 **`REG-CM-001.pdf`（92 KB）+ `SRC-CM-001.DEMO.md`**；**27 个源 `PENDING_SOURCE`**；`01_raw/_public_reference/` 有 `PUB-PRICE-001/002.pdf`（`VERIFICATION_ONLY`，`PUB-PRICE-002` `unknownFieldRate=0.76`） |
| 与结构化层的关系 | `03_core` 产品卡为**结构化层**；两链路共享"同一份文件树"须以**哈希清单**固定（`D-2` 仍待补：版本 + sha256 清单） |

## 3. 已确认 + **一处必须澄清**：TL 造数与灌入

### 3.1 已确认（Owner 授权）

| 项 | 结论 |
|---|---|
| 造数主体 | **TL 派工智能体**（提前造原始产品文档） |
| 灌入主体 | **TL**（把产品文档灌进 LightRAG） |
| 索引重建 | **由 TL 判断负责** |
| 跨仓许可 | `OD-PI-09` 已授权进入 KERT 仓（**本地提交、不 push/merge**） |

### 3.2 ⚠ 必须澄清：造数产物**落在哪个目录**（否则会冒充权威）

**冲突点**：`01_raw/_authoritative/` 的语义是"**权威原文**"（现仅 1 份真实上传 PDF + 1 份 DEMO 源）。
而 Owner 2026-09-21 登记的 **SIM 硬约束 `S-1`** 明确：造数**必须**分类为 SIM
（`simulationOnly=true` / `isDemo=true` / `evidenceClass=SAMPLE_EVIDENCE`），**绝不**写入产品卡字段、taxonomy、`CONTRACTS_INDEX`。

⇒ **若把造数文档直接放进 `_authoritative/`，它会行使"权威原文"的身份**，与 `S-1` 及"不得把 DEMO 当真实制度"（Owner 2026-09-22）直接冲突。

| 选项 | 做法 | 我的建议 |
|---|---|---|
| `L-A`（推荐） | 造数落 `01_raw/_sim/`（新建），文件名带 `SIM-` 前缀 + `simulationOnly` 元数据；`_authoritative/` **只放真实上传件** | ✅ 语义清晰，不污染权威目录 |
| `L-B` | 落 `01_raw/_authoritative/sim/` 子目录 | ⚠ 仍处权威目录之下，易被误读 |
| `L-C` | 落 `_authoritative/` 根，靠文件名区分 | ❌ 不建议（语义污染） |

**另需一句确认（`C-2` 派生层定位）**：LightRAG 只提供**召回与出处**，产品解读的**字段值仍来自受控知识版本**（ADR-017：LightRAG「不是事实源」；抽掉索引不影响任何产物）。若你同意，我按此写入合同提案。

## 4. 链路设计（供确认，实施前不改任何受控源）

```text
① 造数（TL，SIM 标记）                 → 01_raw/_sim/SIM-*.md（按 L-A）
② 灌入 LightRAG（TL）                  → docId = 相对路径编码（沿用既有惯例，如
                                          04_serve__...__version=...__NAME.md 的形式）
③ 检索（KERT 侧）                      → POST /query/data 返回 实体 + 关系 + 出处
④ 出处入解读（GITS 侧）                → 证据定位字段 docId + chunkId
⑤ 字段值                              → 仍来自受控知识版本（审核后的 Release），
                                          检索只做"定位与召回"，不做取值
```

| 环节 | 契约/端点 | 归属 | 状态 |
|---|---|---|---|
| 造数产物 | 无（文件树） | TL（`OD-PI-09`） | 待落位定论（§3.2） |
| 灌入 | LightRAG 侧 API（`/documents` 类）+ KERT `publish_artifact` | TL | ADR-017 已实现客户端；**灌入责任**刚由 Owner 明确 |
| 检索 | `POST /query/data` | KERT | 已实现（ADR-017） |
| **对外检索端点** | **尚无**（KERT 对外仅有 `knowledge-maps`/`routing`） | KERT + 合同 Owner | **需新增合同**（S-1 第 4 项） |
| 出处字段 | `docId` / `chunkId` | `CTR-PK-INT-001` + 新版出口 | **待合同 Owner 批准** |

**索引重建判据（TL 负责）**：① 造数集 hash 清单变更 ⇒ 重建；② 文档删除/替换 ⇒ 重建；③ 每次重建后核对"覆盖与出处一致"（ADR-017 ①「可重建性」口径，不主张逐字一致）；④ 重建期间检索不可用 ⇒ 沿用 `LIGHTRAG_*` 三码 **fail-closed，禁止空结果**。

## 5. S-1 第 4 项提案要点（待一次签全 4 项）

| 项 | 内容 |
|---|---|
| 新增端点 | KERT 侧对外检索端点（建议 `POST /v1/retrieval/query`，**纯新增**，不改既有 1.5.0） |
| 响应字段 | `docId`、`chunkId`、`excerpt`、`evidenceClass`（含 `SAMPLE_EVIDENCE`）、`simulationOnly` |
| 消费方 | 新版产品解读（`CTR-PKC-API-001` 出口暴露 `evidenceRef { docId, chunkId }`） |
| 兼容 | 只增不删；检索不可用时解读页**显式提示"出处不可用"**，不得静默降级为空证据 |
| 验收用例 | ① 出处可复算（`docId`+`chunkId` 能定位回原文）；② 检索不可用 ⇒ fail-closed；③ SIM 文档的出处必须携带 `simulationOnly`；④ 字段值**不得**由检索结果直接产生 |

## 6. 未决清单（本轮结束时的真实状态）

| 编号 | 待办 | 归属 |
|---|---|---|
| `P8-1` | **PC8 指向哪个阶段**（`P-A`/`P-B`/`P-C`） | Owner |
| `L-1` | 造数落位（`L-A`/`L-B`/`L-C`） | Owner |
| `C-2` | LightRAG 为派生层（字段值不来自检索）确认 | Owner |
| `D-2` | 共享文档集的**版本 + sha256 清单**规则 | TL 出草案 → Owner 确认 |
| `S-1` | 合同 4 项一次签 | 合同 Owner |
| `S-3` | 同业来源（B/SIM）启用需产品+合规确认 | 产品 Owner + 合规 |

## 7. 边界（不变）

未改 `specs/`、P38 受控文件、KERT 制品；未灌入任何文档到 LightRAG（等 `L-1` 与 `C-2` 定论）；
本件不构成验收、激活或生产可用结论。
