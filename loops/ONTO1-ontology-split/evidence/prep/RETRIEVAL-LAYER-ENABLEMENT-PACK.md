# 检索层启用落地包（LightRAG）—— 三前提 · 实测 · 归属 · 我提供物 · 我不做

> 依据：`evidence/prep/retrieval-layer-diag.json`（诊断仪**实测**，跨仓**只读**）· KERT `docs/adr/ADR-017-lightrag-retrieval-store.md` · PC8·CR-5 · L6 验收口径
> 作者：ONTO1 loop（TL 写域）；**本包不含任何对 KERT 的写入提案的执行**，只做移交与判据定义。

## 0. 一句话结论

检索层「**服务 + 索引 + 端点**」已实测可用（`HTTP 200`，可召回实体/关系/出处），但**启用三前提全部未满足**。
⇒ **当前任何业务都不得声称「已接入 LightRAG 召回」**；正确状态是 `DESIGN_ONLY` 或「未接入」。

## 1. 现状实测（可复算，命令一行）

复算命令：`python3 scripts/onto1_retrieval_layer_diag.py --scan`
（只读跨仓：不写 KERT、不 publish/retract/不建索引；`gateCandidate=false`）

| 断言 | 判定 | 实测证据 |
|---|---|---|
| **D2** 实例健康 | **OK** | `127.0.0.1:9621/health` → `status=healthy`、`core_version=1.5.7`、`workspace_available=true`、`pipeline_busy=false` |
| **D3** 派生检索端点可召回 | **OK** | `POST :8107/v1/retrieval/query` → `HTTP 200`、`evidenceClass=DERIVED_RETRIEVAL`、`entities 31 / relations 53 / citations 10`、首条出处 docId `04_serve__product-center__PROD-FIN-002.json` |
| **D1** `simulationOnly` 是否派生 | **DEFECT** | 端点响应为**字面量** `False`（KERT `src/kert/api/server.py:755`）⇒ 恒等，与权威配置可相反 |
| **D4** 底层模型 | **DEFECT** | 进程 env `LLM_MODEL=mock`、`LLM_BINDING_HOST=http://127.0.0.1:9630/v1` + `scripts/ci/lightrag_mock_llm.py` ⇒ **CI 假模型** |
| **D6** 端点是否进合同 | **DEFECT** | `specs/` 内 `retrieval/query` **零命中** ⇒ 未进合同 |
| **D5** 口径一致性 | **CONTRADICTION** | 验收口径 `lightragEnabled=false`（`evidence/L6/DEPLOYMENT.lock.json`、`evidence/L6/操作说明-L6.md`）**并存于**运行中的实例与端点；且 `experiment_config.json` 声明 `simulationOnly: true` 与 D1 的 `False` **相反** |

**另需披露的口径陷阱**：PC8 统一门禁 `python3 specs/product-knowledge/check_all.py --gits-only` 现为 `PASS 5 · FAIL 0 · SKIP 6`，但它**不检查新端点是否进合同**
⇒ **「统一门禁绿」≠「端点已进合同」**，不得用它替代 `contract_check`。

**索引内容（灌注面）**：`/tmp/lightrag-storage/` 内 `full_docs 26` / `text_chunks 145`，26 篇均为 `04_serve__interpretation__PROD-*.json` 与 `04_serve/product-center/*`（KERT 产物，带 ADR-017 出处头 + sha256）；实体/关系描述里可见 `isDemo: true`。

## 2. 三前提逐项：缺口 · 归属 · 我提供物 · 我明确不做

### 前提 ① 真实模型（换掉 mock LLM）
| 项 | 内容 |
|---|---|
| 缺口 | `LLM_MODEL=mock` + mock 服务 `:9630` ⇒ 实体/关系抽取为假模型产物；**结论不可当作真实检索能力** |
| 归属 | **Owner 决定**（真实模型的成本/合规/数据出境口径），非技术经理、非 TL |
| 我提供物 | 本包 §1 D4 判据 + 诊断仪（`--scan` 复算）；「做完了」判据＝`D4=OK` 且 `D3` 仍 `OK` |
| 我不做 | 不接外部模型、不申请/存放任何凭据、不改 KERT 实例配置（**KERT 零写入**） |

### 前提 ② `simulationOnly` 必须派生且与权威配置一致
| 项 | 内容 |
|---|---|
| 缺口 | 响应字段为字面量 `False`（`server.py:755`），而权威配置 `simulationOnly: true`、索引内容含 `isDemo: true` ⇒ **模拟数据可能被下游当真实** |
| 归属 | **KERT 侧**（`src/kert/api/server.py` 属 KERT 仓）；GITS 侧**不得代改**（跨仓零直读） |
| 修复建议（供 KERT 侧参考，**非我方执行**） | 把该字段改为**派生**（如由实例/索引的模拟标记或调用方显式入参决定），并让 `experiment_config.json`、端点响应、L6 口径**三者同值**；加反例夹具：① 模拟源 ⇒ 必须 `true`；② 真实源 ⇒ 必须 `false`；③ 缺省源 ⇒ 具名拒绝而非 `false` |
| 我提供物 | 诊断仪 D1（AST 检测字面量）＋ D5（口径矛盾）；「做完了」判据＝`D1=OK` 且 `D5` 不再 `CONTRADICTION` |
| 我不做 | 不改 KERT 任何文件（含不加注释、不动夹具） |

### 前提 ③ 契约先行 + 消费后接
| 项 | 内容 |
|---|---|
| 缺口 | 端点未进合同（`specs/` 零命中）⇒ PC8 三门禁 `contract_generate` / `contract_check` / `unified_gate` **均 pending**；GITS 侧 `apps/api/src`、`frontend/src` **零引用** |
| 归属 | **PC8 的 `implementation_actor`（tech_lead）**：跑 `make generate`（写 `generated/`）→ `make check` → `python3 specs/product-knowledge/check_all.py`；GITS 消费侧接入属**产品解读场景**实现方 |
| 我提供物 | 只读诊断（D6）与口径提示；**不跑 PC8 门禁、不登记 PC8 板面**（非我 loop 写域） |
| 我不做 | 不跑 `make generate`（写 `generated/`，我 scope 内只读）· 不改 PC8 的 `LOOP.yaml`/`STATE.json`/`EVIDENCE.json`/`FAILURES.md` · 不代签 |

## 3. 启用后的验收判据（三步全绿才可称「已启用」）

```
[ ] D4 = OK    （真实模型；非 mock）
[ ] D1 = OK    （simulationOnly 派生）
[ ] D5 ≠ CONTRADICTION（端点响应 / experiment_config / L6 口径三者同值）
[ ] D6 = OK    （端点已进合同）
[ ] PC8 三门禁 pass（contract_generate · contract_check · unified_gate）
[ ] GITS 消费方接入且有缓存/离线路径（不因检索层不可达而中断）
```
任一未满足 ⇒ 报 `DESIGN_ONLY` / 未接入；**不得**报「已生效」。

## 4. 交棒对象（三处，别混）

| 前提 | 交棒对象 | 交棒物 |
|---|---|---|
| ① 真实模型 | **Owner** | 本包 §2-① + 成本/合规决定位 |
| ② `simulationOnly` | **KERT 侧维护方** | 本包 §2-② + 诊断仪 D1/D5 判据 |
| ③ 契约与消费 | **PC8 tech_lead** → 再**产品解读场景实现方** | 本包 §2-③ + `retrieval-layer-diag.json` |

## 5. 与提示词的衔接

面向「产品解读重构」场景技术经理的约束已写入
`evidence/prep/PROMPT-PRODUCT-REINTERPRET-MANAGER.md`（§5 落位与现状 · §6 三前提 · §8 勾选 · §9 归属）——
**该场景只消费、不启用检索层**。

## 6. 新仪器判据强度自陈（D-20 纪律：新增仪器须附自审结果 + 逐条理由）

**自审结果**（`python3 scripts/onto1_check_strength_audit.py`）：仪器总数 46、可审判据 229、候选 14（13 `NOT_AUDITED` + 1 `DECLARED_ONLY`）。
本诊断仪：**抽到 1 条**（`STATE_WRITE::counts[...]`，非薄弱模式）· **不在候选清单** · **不属未审仪器**。
⚠ **覆盖缺口如实披露**：自审仅抽到 1 条，而本仪实有 **6 组判定**（D1~D6）——成因与 QA 第二轮指出的自审仪局限一致（判据条件**预计算为变量**、`dict` 下标赋值不在其审查域）。故按 D-20 由我在此**逐条自陈**：

| 断言 | 条件形态 | 是否可能恒真/空转 | 反例能否真失败 |
|---|---|---|---|
| D1 | `isinstance(val, ast.Constant)` | 否（两分支互斥且都有实例） | ✅ 若 KERT 改为派生表达式 ⇒ 判 `OK`；现状字面量 ⇒ 判 `DEFECT`（已实测 DEFECT） |
| D2 | `doc.get("status") == "healthy"` | 否 | ✅ 实例停 ⇒ `UNREACHABLE`；返回非 healthy ⇒ `DEFECT` |
| D3 | `status != 200` 先判，再取 `citations` | 否 | ✅ 实测为 `OK` 且带真实 `citations 10` |
| D4 | `(model == "mock") or bool(host and "9630" in host)` | 否（或运算，两侧均可独立触发） | ✅ 实测 `DEFECT`；换真实模型后应转 `OK` |
| D5 | `"CONTRADICTION" if lock is False else "OK"` | 否（`is False` 严判，非 `falsy`） | ✅ 实测 `CONTRADICTION`（`lightragEnabled=false`） |
| D6 | `"OK" if hits else "DEFECT"` | **否，且方向为 fail-closed** | ✅ 空集判 `DEFECT`（**不是**空转给绿）；实测 `DEFECT` |

**结论**：6 条判据**无恒真、无同义反复、无空转给绿**（其中 D6 在空集时判缺陷，方向安全）。

**D-20 追加（2026-09-23，新增 D7）**：加 `D7` 判据——`源码已派生（D1=OK）` 且 `运行态仍返回 False` ⇒ **`STALE_DEPLOYMENT`**。
判据强度：两条件 AND，两侧都可独立触发；实测在**已修源码 + 未重启实例**下**真的触发**（非恒假）⇒ 能把「消费方误以为已修好」变成机器可见状态。
同前，自审对本仪仍只抽到 1 条（变量预计算 + `dict` 下标不在其审查域），故仍由本表逐条自陈。

**D7 转录记录（2026-09-23）**：重启 KERT 技能服务后，`D7` 由 `STALE_DEPLOYMENT` **转录为 `OK`** ⇒ 该判据**双向可用**（既能报陈旧、也能确认生效）。
**我不主张把它登记为门禁**（`gateCandidate=false`）：它读跨仓实现细节，登记会变成「用别仓实现当本仓通过条件」，与 P3 精神相左；本仪定位为**诊断与留痕**。

