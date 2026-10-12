# 检索层启用 · 三方移交单（Owner ① / KERT 侧 ② / PC8 tech_lead ③）

> 来源：`PROMPT-PRODUCT-REINTERPRET-MANAGER.md`（场景约束）· `RETRIEVAL-LAYER-ENABLEMENT-PACK.md`（三前提）· `retrieval-layer-diag.json`（实测，`gateCandidate=false`）
> 作者：ONTO1 loop（TL 写域）。**本单不代表任何执行的完成**，只做移交与判据定义；KERT 侧与 PC8 侧的执行须按其各自治理流程。

---

## 0. 追查记录（应 Owner 要求，追到底）

### 0.1 「KERT 今日写入 104 件」归因 —— **全部非我方，全部早于本轮 8 小时**

口径：本轮动作时段为**本地 2026-09-23 23:21~23:22**（UTC 15:21~15:22）；本地 `23:00` 之后 KERT **零写入**。

| 类 | 件数 | 路径/证据 | mtime（本地） | 归因 |
|---|---|---|---|---|
| A. Python 导入缓存 | 3 | `src/kert/**/__pycache__/*.pyc`（`operational_analytics.cpython-312`、`analytics_store.cpython-312`、`server.cpython-310`） | 12:26:42 ~ 12:27:25 | KERT 服务/组件被导入运行 |
| B. skill 作业产物 | 4 | `bank_front_ws/90_control/jobs/JOB-SKILL-20260923-016/`（`result.json` 151 KB、`STATUS.md`、`RUN_REPORT.md`、`logs/2026-09-23/…016.log`） | 15:13:29 | **API 触发的一次成功 skill 作业**：`job_type: SKILL`、`status: COMPLETED`、`requested_by: api`、`idempotency_key: REQ-SP20-0f5e7102…`、`duration 28212 ms`、`error 0` |
| C. 依赖同步安装 | 97 | `.venv/lib/python3.12/site-packages/duckdb*`、`_duckdb*`、`adbc_driver_duckdb*`（`INSTALLER: pip`） | 15:15:06 | `pyproject.toml:28` **已声明** `duckdb>=1.0` ⇒ **按声明安装**，非手工塞包 |

**结论**：104 件＝KERT 侧自身开发/运行活动（服务导入 · 一次技能作业 · 依赖同步）；**本轮我方对 KERT 的写入 = 0**。
**披露纪律**：此后**不得**再笼统宣称「KERT 今日零写入」——正确口径是「**本轮零写入**；今日有 104 件**非我方**写入」。

### 0.2 追查副产：三处口径漂移 / 一处同仓矛盾（均已定位，**我未代改**）

| # | 发现 | 证据 | 处置归属 |
|---|---|---|---|
| P-1 | **索引位置与 ADR 声明不符** | `ADR-017` §边界 载索引在 `/home/szf/dev/lightrag/rag_storage`（该路径确实存在）；但**运行实例**（`:9621`）进程 env `WORKING_DIR=/tmp/lightrag-storage`，且实测召回命中的正是该处内容 | KERT 侧（须澄清以哪个为准；两者均在**工作区之外** ⇒ ADR「工作区外」判据本身仍成立） |
| P-2 | **历史基线不可再用** | ADR-017 载「清空前 662 节点 / 784 边（2026-09-16）」；现索引为 **26 篇** `04_serve__interpretation__PROD-*.json` + `04_serve/product-center/*`（`full_docs 26` / `text_chunks 145`） | KERT 侧（引用基线时须注明版本） |
| P-3 | **M7 文档结论已被推翻但正文未加指针** | `KERT_PENDING_OWNER_DECISION_M7_EVOLUTION_V1.0.md`（2026-09-15）裁定 **D2-A＝不引入 LightRAG**，并写「**不得**在后续汇报中被读作『LightRAG 已实现』」；而 `ADR-017`（2026-09-16，APPROVED）第 5 行原件载：**Owner 2026-09-16 明示「要 lightRAG」（D-31，推翻 D2-A/D3-A）** | KERT 侧（建议在 M7 文档加「已被 D-31 推翻」指针，防只读单篇者得反结论） |
| P-4 | **同仓自相矛盾（`simulationOnly`）** | `src/kert/infrastructure/adapters/sim_bank_front.py:17`「每份输出均带 `simulationOnly: true` 与 warnings 声明，防止被误读为真实分析」（`:55`/`:193` 亦为 `True`）；而 `src/kert/api/server.py:755` 对派生检索写死 `False` | KERT 侧（= 下述 ②） |

> **治理时序澄清（重要，非缺陷）**：LightRAG 的**当前有效口径是 ADR-017（APPROVED）**——Owner `D-31` 已推翻 M7 的「不引入」。故接入**有 ADR 授权**，不是未授权接入。
> **同时**：ADR-017 的「非声明」段明确 **「不代表 LightRAG 检索结果可作业务结论或事实来源」** ⇒ 这正是给场景技术经理的 §6 约束的原始依据。

---

## A. ① Owner：**换真实模型**（执行单）

**现状（实测）**：`:9621` 实例 env 为 `LLM_BINDING=openai` / `LLM_BINDING_HOST=http://127.0.0.1:9630/v1` / `LLM_MODEL=mock` / `LLM_BINDING_API_KEY=ci-dummy`；**embedding 亦指向同一 mock**（`EMBEDDING_BINDING_HOST=http://127.0.0.1:9630/v1`），另有进程 `scripts/ci/lightrag_mock_llm.py 9630`。

**需 Owner 提供（缺一无法执行）**：
1. 真实 **LLM** 的 `binding / host / model / key`（以及是否允许出境）；
2. 真实 **embedding** 的 `binding / host / model / key`；
3. 成本与配额口径；4. 是否允许以本项目语料调用该模型（合规）。

**执行依赖（技术关键，勿漏）**：**embedding 变更 ⇒ 既有向量索引不可复用** ⇒ 必须**清空 ⇒ 重灌 ⇒ 核对覆盖与出处一致**（ADR-017 已就有一条对应判据）；重建期须 **fail-closed**（禁空结果冒充成功）。

**验收判据**：诊断仪 `D4 = OK` **且** `D3` 仍 `OK`（端点仍可召回且带可回译出处）；重建后 `citations` 出处哈希与 KERT 产物一致。

**归口**：改的是 **KERT 实例 env**（非本仓）⇒ 我**不改**（KERT 零写入）；我只提供判据与复算命令。

---

## B. ② KERT 侧：**`simulationOnly` 改派生**（修复请求单 + 补丁提案 + 反例夹具）

> **状态（2026-09-23）：✅ 已在 Owner 授权下落地**（范围限本项 + 其夹具）。以下为**执行记录**，原提案保留在后文供评审。

### B.0 执行记录（可复算）

| 项 | 内容 |
|---|---|
| 改动 | `src/kert/api/server.py`（+58 行：新增 `derive_simulation_only` + 端点取值 + 注释）· `tests/integration/test_retrieval_endpoint.py`（+23/-4：断言改为**独立复算**，避免同义反复）· **新增** `tests/unit/test_retrieval_simulation_flag.py`（6 例：DEMO⇒True / PRODUCTION⇒False / 无证据⇒True / 缺字段⇒True / 混源⇒True / 边界5 抗污染） |
| 派生规则 | **只读出处回译到的 KERT 产物**顶层 `provenanceState`，按契约 enum 判定（`VERIFIED` 为真实，其余及取值不足一律 `DEMO`）；**不读** lightRAG 返回值任何字段（守 CR-5 边界第 5 条「字段值不得取自检索」） |
| 验证 | 单元 **6 passed** · 集成 **2 passed / 1 skipped** · **真实工作区端到端** `HTTP 200` 且 `simulationOnly=True`（与独立复算一致）· **强变异**（整函数退回字面量）⇒ **4 条反例失败**、末行变异 ⇒ 2 条 fail-closed 反例失败 ⇒ 恢复后 6 passed |
| 备份/回滚 | `/tmp/kert-server-py.bak`（改前原文件）· `/tmp/kert-it.bak`（改前测试）· `/tmp/kert-server-good.py`（最终态）。回滚＝把第 1 个覆盖回 `src/kert/api/server.py` 并删新增测试 |
| 未做 | **未 commit / 未 push**（KERT `AGENTS.md` 强制 Rule 10：无 Owner 授权不得自动 push/merge）；KERT 工作树另有 20+ 项 `M`/`??` **非我方**改动，未触碰 |
| ✅ 运行态 | **已生效**（2026-09-23 获授权重启）：`:8107` 已重启（精确复制原进程 env 113 项 + 覆盖 3 项；**只重启 KERT**，未动前端/后端）⇒ `analytics=200`、`retrieval/query=200` 且返回 **`provenanceState=DEMO` / `simulationOnly=True`**；诊断仪 **D7 转录 `OK`** |
| ✅ 字段口径（Owner 已裁：按设计增设） | 响应已增 **`provenanceState`**，与 `simulationOnly` **同源派生**（`DEMO ⇒ True`），取值域取契约 enum **`VERIFIED`/`DEMO`**（`specs/product-knowledge/product-knowledge-release.schema.json`，与 `INV-RLS-09` 同向） |
| ✅ 我的口径错误已修 | 首版误用 `PRODUCTION`/`AUTHORITATIVE`（**不在契约取值域内**）⇒ 会把 `VERIFIED` 错判为模拟；已改为按 enum 判定，并加**越界值 ⇒ `DEMO`** 反例 |
| 仍在（非本授权） | PC8 侧：端点进合同 + 三项门禁（`contract_generate`/`contract_check`/`unified_gate` 仍 `pending`）· Owner 侧：真实模型选型（见 `RETRIEVAL-MODEL-SWITCH-ONEPAGER.md`） |


### B.1 缺陷（具名）
`src/kert/api/server.py:755` 响应 dict 内 `"simulationOnly": False` 为**字面量**；与 `adapters/sim_bank_front.py:17` 的「仿真输出必须 `true`」**相反**，与 `specs/knowledge-architecture/lightrag/experiment_config.json` 的 `simulationOnly: true` **相反**，且索引内实体/关系描述含 `isDemo: true`。

### B.2 补丁提案（**供 KERT 侧参考，我方不执行**；三选一由其 ADR/规程定）
- **方案 1（推荐：由内容派生，保守方向）**：该值派生自**被检索内容的来源标记**；混源时返回 `true`（宁可多标仿真，不可漏标）。
- **方案 2（由调用方声明）**：`RetrievalQueryRequest` 增 `simulation_only: bool | None`；**缺省时具名拒绝**，不默认 `false`。
- **方案 3（删字段）**：不建议——CR-5 已冻结「响应带该字段」。

（示意，**不是可直接应用的 patch**）
```python
# 现状
"evidenceClass": "DERIVED_RETRIEVAL",
"simulationOnly": False,                      # ← 字面量，恒等

# 方案 1 示意
"evidenceClass": "DERIVED_RETRIEVAL",
"simulationOnly": _derive_simulation_flag(r),  # ← 由被检索内容来源派生；混源 ⇒ True
```

### B.3 反例夹具（3 条，须由**判据本尊**捕获）
1. 索引含仿真标记（`isDemo: true`）⇒ 断言 `simulationOnly is True`；
2. 索引为真实源 ⇒ 断言 `simulationOnly is False`；
3. **来源未声明** ⇒ 断言**具名拒绝**（**不得**默认 `False`）。

### B.4 三处同值（配置 · 响应 · 验收）
`experiment_config.json` / 端点响应 / L6 口径（`evidence/L6/DEPLOYMENT.lock.json`、`操作说明-L6.md`）**必须同值**；并加指针说明「本字段由何派生」。

### B.5 验收判据
诊断仪 `D1 = OK`（不再为字面量）**且** `D5 ≠ CONTRADICTION`（口径不再互相矛盾）。

**归口**：代码在 **KERT 仓**（`src/kert/api/server.py`）⇒ 我方**不改**（KERT 零写入红线；且「KERT 写权限」仍在待人类清单内）。

---

## C. ③ PC8 tech_lead：**门禁推进 + 消费侧接入**（清单）

**现状（实测）**：`specs/` 内 `retrieval/query` **零命中** ⇒ 端点**未进合同**；PC8 三门禁 `contract_generate` / `contract_check` / `unified_gate` **全 `pending`**；GITS 侧 `apps/api/src`、`frontend/src` **零引用**。
**口径陷阱**：`python3 specs/product-knowledge/check_all.py --gits-only` 现为 `PASS 5 · FAIL 0 · SKIP 6`，但它**不检查端点是否进合同** ⇒ **不得**用它替代 `contract_check`。

**推进顺序（依赖在前）**：
1. 端点进合同（v1/v2 归口 + 出处字段 + fail-closed 三码）；
2. `make generate` → `make check` → `python3 specs/product-knowledge/check_all.py`（**注意 `make generate` 会写 `generated/`**）；
3. 消费侧接入（产品解读场景），**须含检索层不可达时的缓存/离线路径**（不得因检索层故障中断业务）。

**我方边界**：`make generate` 写 `generated/`，而 ONTO1 的 `scope` 内 `generated/` 为**只读** ⇒ **我不跑**；PC8 板面（`LOOP.yaml`/`STATE.json`/`EVIDENCE.json`/`FAILURES.md`）属其 `implementation_actor` 写域 ⇒ **我不登记、不代签**。

---

## D. 若要我从「移交」变为「执行」，需要你两句话

1. **【② 的唯一钥匙】** 「**授权我改 KERT 仓**（范围限 `src/kert/api/server.py` 的 `simulationOnly` 派生 + 其夹具）」——若授权，我仍会**先出逐行补丁供你过目**再落，并遵守 KERT 仓自身的 ADR/门禁（不绕过其 QA）。
2. **【① 的输入】** 真实 LLM/embedding 的 `host / model / key / 合规口径`（这属**凭据与成本**，必须你给，我不自接）。

> 在你给出这两句之前，本单的执行主体仍是：① **Owner** ② **KERT 侧** ③ **PC8 tech_lead**；我方交付物为**判据 + 移交 + 留痕**（诊断仪可随时复算）。
