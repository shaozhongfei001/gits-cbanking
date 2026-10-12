# GK17 长程无人值守编排 · V1.0

> **Loop**：`GK17-ontology-unified-map`｜**holder**：`tech_lead`｜**基线**：`79fbf38`
> **授权**：Owner 2026-09-15「建立长程无人值守任务，拆分派工多智能体并行、串行完成，每个 Wave 采用 loop engineering」
> **上游**：`docs/architecture/GK-KE-统一地图承担者论证-V1.0.md`（含 V1–V4 判据）
> **模式**：loop engineering —— **PLAN → ITER（max 5）→ 红测 → ACCEPT**；无红测不得 ACCEPT

---

## 0. 编排的第一原则（**来自本仓实测，不是惯例**）

> ### 并行读 + 串行写

**依据（GK16 `FAILURES.md` T-24，我本人实测）**：把 `run_gates.py`、`gate_injection_tests.py`、`chain_trace.py`
并发执行会互相污染 `evidence/gk-ke-chain-trace/trace.json` 与 `gates.txt`，
产生**假 FAIL**（曾出现 exit=1、假的"2 项完整性失败"、假的"合同正例被改"）。
串行重跑后异常全部消失。

⇒ **本 Loop 强制约束**：

| 类别 | 是否可并行 | 说明 |
|---|---|---|
| 只读检索 / 清点 / 起草 | ✅ 可多智能体并行 | 不写盘或只写各自独占的新文件 |
| **`make generate` / `make check` / `run_gates.py` / Maven 测试** | ❌ **必须串行** | 单写者独占执行 |
| **合同源 `specs/semantic/`、`specs/knowledge-architecture/`、`generated/`** | ❌ **单写者独占** | 同一时刻只能一个智能体改 |
| **Loop 记忆（STATE / ROLE_BOARD / ORCHESTRATOR / NEXT_SESSION）** | ❌ **只有 TL 写** | 避免并发覆盖 |
| 互不重叠的新文件（脚本 / 文档 / 导出器） | ✅ 可并行 | 见 §2 文件所有权 |

### 0.1 门禁前置条件（**执行任何门禁前必读**，2026-09-16 增补）

> 依据：`loops/GK17-ontology-unified-map/FAILURES.md` `20260915T073300Z`。
> 不满足前置条件会撞**假红**（红点读不出任何代码信息），并被误记为产品缺陷。

| # | 前置条件 | 命令 / 判据 | 不满足的后果（实测） |
|---|---|---|---|
| **P1** | **本地仓库工件新鲜** | `./mvnw -q -Ddependency-check.skip=true install` 先装一遍 | `LOOP.yaml.gates.ontology_load` 的文档化命令**不带 `-am`** ⇒ 模块依赖解析到 `~/.m2` **旧快照**；实测旧 jar **不含** `OntologyPort` ⇒ `testCompile` 失败、`default-compile` 无错 ⇒ 上次的"PASS"是**靠陈旧 `target/` 达成的** |
| **P2** | **测试面用 `./mvnw test`，不用 `verify`** | `./mvnw --batch-mode --no-transfer-progress test` | `make backend-test` 走 `verify`，OWASP `dependency-check` 需**联网**拉 RetireJS；**间歇性超时**时模块被 **SKIPPED（测试根本没跑）** ⇒ 该红读不出代码信息。<br>⚠ 口径（Tick 19 更正）：是**间歇性**（本 Loop evidence 有 1 次全绿、N 次红），**不是**确定性"不可达" |
| **P3** | **门禁串行执行** | 同一时刻只跑一个 | `run_gates.py` / `gate_injection_tests.py` / `chain_trace.py` 并发会互相污染 `evidence/gk-ke-chain-trace/trace.json` 与 `gates.txt` ⇒ **假 FAIL**（GK16 T-24 实测） |
| **P4** | **跑门禁后还原噪声文件** | `git checkout -- evidence/gk-ke-chain-trace/trace.json` | 该文件每次跑门禁都被重写；不还原会污染提交 |
| **P5** | **断言前核对输入基数** | 见 `gk17_triple_consistency_check.py` 的 `inputCardinality` / `vacuity` | 本仓已有 **6 个 Loop 首报全绿实为空转**的前例（本体 32/34 被读成 0/0 而门禁报 PASS） |

**跨会话注意**：2026-09-14 夜发现**另一执行者**在同一工作区提交（`82b70b4`，Dockerfile 守卫）。
双方均按显式路径提交、互不纳入。**本 Loop 只写 §1 的 include 范围**，冲突时以本 Loop 的 Loop.yaml 为准。

---

## 1. Wave 总表

| Wave | 目标 | 依赖 | 并行度 | ACCEPT 判据 | max_attempts |
|---|---|---|---|---|---|
| **W0** | 开工与基线 | — | 串行 | Loop 合规（`loop-guard` PASS）+ **基线快照落盘**（记录既有红灯，防"把既有问题算到本 Loop"） | 5 |
| **W1** | 本体扩到设计范围（合同先行） | W0 | **写串行**（调研并行） | `make generate` PASS + `make check` PASS + `MechanismE2eIT` PASS + 新类进 SHACL | 5 |
| **W2** | 本体真实进入知识路由 | W1 | 串行（同模块） | 路由裁决**带本体依据**并写入 plan trace；本体不可达 ⇒ **fail-closed**；负例通过 | 5 |
| **W3** | 结构化知识 → 图（A-Box） | W1 | WP3.1 / WP3.2 可并行 | 个体数可度量；重复投影**逐字节一致** | 5 |
| **W4** | 非结构化知识 → 图 | W1+W3 | 串行 | 候选断言**只落 CANDIDATE**；负例：DEMO 冒充权威 ⇒ **拒绝** | 5 |
| **W5** | 三条硬约束的机械防线 | W1 | WP5.1 / WP5.2 可并行 | **变异前 PASS / 变异后 FAIL / 恢复 PASS**（每门禁各自自证） | 5 |
| **W6** | V1–V4 实验与证据 | W2+W3+W4+W5 | 串行（同证据目录） | V1 链路可复核 + **V2/V3/V4 反例全部有变异对照** | 5 |
| **W7** | 产品可见化 | W2+W3 | 后端串行、清单并行 | 浏览器**实测截图** + `vue-tsc` 0 错误 | 5 |
| **W8** | 收口 | 全部 | 串行 | `make memory-check` / `make evidence-check` PASS；QA 包就绪 | 5 |

### Wave 级 ACCEPT 的硬要求（loop engineering）

1. 每个 WP 先写 **PLAN**（`memory/waves/Wx-PLAN.md`），再执行；
2. 每次执行经 `scripts/record_gate.py` 落证，失败**先写 `FAILURES.md` 再修**；
3. **新增门禁必须附变异负例**（本仓硬约束 #2/#3）：不做负例的门禁视为**未完成**；
4. 断言"全绿"之前必须问一句：**它会不会因为夹具缺失而空转？**（本仓已有 6 个 Loop 首报全绿实为空转的前例）

---

## 2. 工作包 × 派工 × 文件所有权

> **所有权规则**：一个 WP 的文件路径**只能有一个写者**。跨 WP 的文件冲突由 TL 串行化。

### W1 · 本体扩展到设计范围（合同先行）

| WP | 内容 | 写者 | **独占路径** | 产出 |
|---|---|---|---|---|
| **WP1.1** | 设计点名对象类：**公司 / 集团 / 账户 / 产品 / 文档** | 本体负责人 | `specs/semantic/gits-core.*` | 类 + 标识 + 关系 |
| **WP1.2** | 系统既有对象类：承诺 / 机会 / KYC缺口 / 人工门禁 / 外部事件 / 交易 / 规则 / 授信 | 同上（**串行合并**） | 同上 | 同上 |
| **WP1.3** | 产品关系谓词语义 + **权威归属裁定**（约束①） | TL 裁定 + 本体负责人落盘 | `specs/semantic/` + `docs/architecture/` | 裁定记录 |
| **WP1.4** | ID 空间补全（Capability / Task 等） | 本体负责人 | `specs/semantic/` | 类定义 |

> **WP1.3 的裁定内容（TL 已定，待落盘）**：
> **"关系类型"的权威 = 本体**（谓词语义：`gits:requires` / `gits:mutuallyExclusiveWith` / `gits:complements`）；
> **"关系实例"的权威 = 产品卡**（产品 Owner 维护）；
> **投影方向单向**：产品卡 → 本体个体。**本体不得反向承载产品关系实例，地图不得复述关系。**

### W2 · 本体进入路由

| WP | 内容 | 写者 | 独占路径 | 产出 |
|---|---|---|---|---|
| **WP2.1** | `OntologyPort` + Jena 实现（读 T-Box + A-Box，fail-closed） | 路由负责人 | `modules/semantic-runtime/`, `adapters/semantic-jena/` | 端口 + 适配器 + 单测 |
| **WP2.2** | routeMode 四路径消费 `versions.ontology` | 路由负责人 | `modules/knowledge-architecture/` | 裁决带本体依据 |
| **WP2.3** | `planHash` 纳入本体版本（可回放） | 同上 | 同上 | 计划字段 + 负例 |

### W3 / W4 · 两类知识进图

| WP | 内容 | 写者 | 独占路径 | 产出 |
|---|---|---|---|---|
| **WP3.1** | 产品卡 front matter → RDF（确定性；含前置/互斥/配套） | 导出负责人 | `scripts/gk17_prodcard_to_rdf.py`, `specs/knowledge-architecture/instances/product/` | 个体 + 复算校验 |
| **WP3.2** | 事实对象（客户/集团/账户）→ RDF | 导出负责人（串行） | `specs/knowledge-architecture/instances/fact/` | 个体 |
| **WP4.1** | `.DEMO.md` / 证据片段 → **候选断言**个体 | 非结构化负责人 | `scripts/gk17_evidence_to_abox.py`, `instances/candidate/` | 候选个体 |
| **WP4.2** | 门禁：候选不得冒充事实 | 校验负责人 | `scripts/gk17_candidate_guard.py` | 门禁 + 负例 |

### W5 · 三条硬约束的机械防线

| WP | 内容 | 写者 | 独占路径 | 产出 |
|---|---|---|---|---|
| **WP5.1** | **引用锚定**：地图引用本体不存在的个体 ⇒ **拒绝**（V3） | 校验负责人 | `scripts/gk17_ref_anchor_check.py` | 门禁 + 变异负例 |
| **WP5.2** | **三处一致性**：地图 / 本体 / 投影不一致 ⇒ **检出**（V4） | 校验负责人 | `scripts/gk17_triple_consistency_check.py` | 门禁 + 变异负例 |
| **WP5.3** | 本 Loop 全部新增门禁的**变异回归** | 校验负责人 | `scripts/gate_injection_tests.py`（**复用仓内既有唯一机制**，不新造第二套） | 变异矩阵 |

### W6 / W7 / W8

| WP | 内容 | 写者 | 独占路径 |
|---|---|---|---|
| **WP6.1** | V1：`PRE_VISIT_PREPARATION`（`ONTOLOGY_THEN_MAP`）完整链证据 | TL | `loops/GK17-.../evidence/` |
| **WP6.2** | V2 / V3 / V4 反例 + 变异前后对照 | TL | 同上 |
| **WP7.1** | 产品解读 / 产品推荐展示"前置/互斥/配套 + 准入"（**合同先行**） | 产品负责人 | `apps/api/.../productknowledge/`, `frontend/src/` |
| **WP7.2** | 人工测试清单更新 + 浏览器截图 | 产品负责人 | `docs/governance/GITS-Bank-人工测试清单-*.md` |
| **WP8.1** | 证据包 + 独立 QA 包 | TL | `evidence/` |
| **WP8.2** | Owner 待签清单（ADR 是否推进 Accepted） | TL | `memory/` |

---

## 3. 角色与派工

| 角色 | 谁 | 可写 | 禁止 |
|---|---|---|---|
| **Tech Lead** | 本会话（全局 TL） | 合同裁定、W5/W6/W8、Loop 记忆、门禁执行 | 不代签 QA_PASS；不改判据内容 |
| **本体负责人** | 子智能体（**串行独占** `specs/semantic/`） | W1 全部 | 不得在本体承载产品关系**实例** |
| **路由负责人** | 子智能体 | W2 | 不得绕过 fail-closed |
| **导出负责人** | 子智能体 | W3 | 不得写合同源 |
| **校验负责人** | 子智能体 | W5 | 新增门禁必须附变异负例 |
| **产品负责人** | 子智能体 | W7 | 合同先行，不得发明字段 |
| **独立 QA** | **另一独立会话** | 只读 + 判定 | TL 不得代签 |

**派工提示词约定**（沿用本仓 Loop 短提示词规范）：
```text
你是 <角色>，做 GK17 的 <WP 编号>。写者独占 <路径>。共享记忆按仓库规则自动开场/收工。
只做该 WP；完成后 STOP，并在 ORCHESTRATOR 记 tick。
```

---

## 4. 停止条件（**仅这 5 种才上报人工**）

1. **缺凭据**（外部数据/凭据不可得）；
2. **需求冲突**（Owner 口径与设计原文矛盾且不可自决）；
3. **方向性变更**（命题本身改变）；
4. **自愈耗尽**（同一门禁 5 次仍红）；
5. **安全隐患**（可能导致生产写回 / 凭据泄露）。

其余问题按 **自愈 → 降级 → 回退** 自行处理，不中断。

---

## 5. 本 Loop 明确**不做**的事

- 不改 `docs/dd/gk-ke-contract/` 封版制品；
- 不手工编辑 `generated/`；
- 不解除 `_public_reference` 的 `VERIFICATION_ONLY` 红线（需 Owner 签字）；
- 不启用隔离资产（Oracle / Ossie）；
- 不做生产写回、不做 LightRAG 启用（`abc_comparison` 已判未启用）；
- **不代签**任何 `QA_PASS` / Owner 决议；
- 不把 `INCONCLUSIVE` 计入通过。

---

## 6. 进度台账

见 `loops/GK17-ontology-unified-map/memory/ORCHESTRATOR.md`（append-only，每次 tick 一条）。
