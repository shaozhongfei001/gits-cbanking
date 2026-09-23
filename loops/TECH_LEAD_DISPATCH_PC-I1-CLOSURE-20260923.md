# TL 派工与编排 · PC-i1 收口 + 跨路并行（2026-09-23）

```text
DISPATCH_ID = TL-DISPATCH-PC-I1-CLOSURE-20260923
ISSUED_BY   = tech_lead（planning_review 角色；依 Owner 2026-09-23 的 6 项决定）
SCOPE       = PC-i1 正式签署 · QA-4 归属 · ROLE_BOARD · PI-1（W-3）· 仓库/环境诊断 · PC-i1 剩余内容（W1-g 遗留 → I2–I4）
基线        = gits-cbanking @ c5cb6fd（交棒前）→ 交棒提交见下；KERT @ 65b96df
RED LINE    = ① 未授权不改门禁/证据 ② BLOCKED 不得记 pass ③ implementation actor 不得签 QA_PASS
              ④ 同一文件域**单写者**（避免并发改同一仓）⑤ 交棒后 TL 不再 record_gate（脚本要求 status=in_progress）
```

## 0. Wave 0（**已执行完毕** · TL 串行 · 无并行）

| # | 动作 | 结果 |
|---|---|---|
| 0.1 | **QA-4 归属裁定 = 入仓** | `scripts/record_gate.py` 入仓（`c5cb6fd`）。理由：`loop_guard.py` 的分纪元读取端已入仓，回退会造成两脚本不自洽；且该机制已被正当使用（`--revision-note` 开 `Revision epoch 1`，理由入 `W0-ITER.md`）；独立 QA 已复核未使 loop 变绿 |
| 0.2 | **交棒 + 状态提升** | `ROLE_BOARD.baton.holder` 与 `NEXT_SESSION.holder` → `independent_qa`；`STATE.status=ready_for_independent_qa`、`qa_actor=independent_qa`；校验：`loop-guard --loop` **PASS**、实例 **69/69 合规**、6/6 门禁 pass、`independent_qa` 仍 **pending**（未代签） |
| 0.3 | **W-3 回源完成**（`F-PC-i1-03` 结清） | 7 张卡的 `product_family_name` **均在卡片第 6 行**：`PROD-SET-001/002`（`settlement/version=2026.09.01.1/…`）· `PROD-TF-001/002`（`trade-finance/version=2026.09.01.1/…`）· `PROD-FIN-001/002/003`（`financing/version=2026.08.31.1/…`） |

## 1. 角色（role → 职责 → 写入面）

| 角色 | 职责 | 允许写入面 |
|---|---|---|
| `tech_lead`（本 dispatch 发起人） | 编排/交棒/契约与设计裁决/回源/收口；**不写实现** | `loops/**` 派工与记录、`docs/dispatch/**` |
| `independent_qa` | 正式签署（`qa_attest.py`）、独立复核 | `EVIDENCE.json.independent_qa` + 自己的报告（仓内 `evidence/`） |
| `kert_pilot` | W-3 族名收敛（KERT 侧） | `Leibniz-KERT` 仓（`03_core/**` 产品卡 + 受控链路产物） |
| `env_pilot` | 仓库/环境诊断与就绪（DIAG-1/2/3/5） | 环境变量、`.ua/`（不入 git）、仓外临时区；**不改 loop 受控文件** |
| `repo_curator` | 未跟踪/已修改文件甄别（DIAG-4，**只读**） | 仅新增清单/建议（不改、不删、不提交他人文件） |
| `feature_pilot` | PC-i1 剩余内容（W1-g 遗留 → I2–I4） | `frontend/src/**`、`frontend/e2e/**`、`apps/api/**`（按各自 loop 的 scope） |

## 2. Wave 1（**真并行 3 路** · 写入面互不相交）

| 路 | 角色 | 任务 | 判据/产物 | 依赖 |
|---|---|---|---|---|
| `1A` | `independent_qa` | **正式签署**：`python3 scripts/qa_attest.py --loop PC-i1-chapter-inheritance --actor independent_qa --session <新会话名> --decision pass\|reject --evidence <仓内报告>` | 报告落仓内；`--actor` ≠ `tech_lead` | Wave 0.2 已完成（前置自检通过） |
| `1B` | `env_pilot` | DIAG-1 `semantic-consumption`（READINESS NOT MET 诊断）· DIAG-2 `gate-injection-tests`（INCONCLUSIVE 缺什么条件）· DIAG-3 analytics 环境（`KERT_ANALYTICS_DUCKDB` 配置与 4 条 BLOCKED 用例复验）· DIAG-5 `.ua` 索引刷新（`INDEX_STALE(58)`） | 每项：具名结论 + 证据；**只诊断/环境**，判据不改 | 无（与 1A/1C 独立） |
| `1C` | `repo_curator` | DIAG-4：**418 未跟踪 / 36 已修改**甄别归类（他人未完成件、构建产物、可忽略件…） | 清单 + 建议（**不清理、不提交**） | 无 |

**并行约束（防"签署对象漂移"）**：`1A` 进行期间，`1B`/`1C` **不得**改 `loops/PC-i1-chapter-inheritance/**` 与 `frontend/src/**`（可写环境、`.ua/`、仓外、其自身的分析产物）。若 `1A` 判 **reject** ⇒ 按协议回 `in_progress` → 修复 → 重走门禁 → 再交棒。

## 3. Wave 2（**1 串行 + 1 可并行**）

| 路 | 角色 | 任务 | 串行/并行判定 |
|---|---|---|---|
| `2A` | `kert_pilot` | **PI-1 · W-3 族名收敛**：把 7 张卡第 6 行 `product_family_name` 对齐 Owner 裁决 OQ-B 的族名 —— `结算服务→结算`（SET-001/002）· `贸易融资→贸易金融`（TF-001/002）· `流动资金融资→融资`（FIN-001/002/003）；**走受控链路**（不得手改绕过解读链路）；跨页比对（`/api/v1/product-center/products` ↔ `/api/v1/product-knowledge/cards`）**0 不一致**；族数 6/13 不变 | **串行（KERT 单写者）**；写入面 = KERT 仓 |
| `2B` | `feature_pilot` | **W1-g 遗留**：12 章**事实等价逐条比对**（P38 每节文本 ↔ 新版呈现；判定"事实是否等价/是否丢细节"） | **与 2A 可并行**（低耦合：2A 只改 front matter 族名，不影响章节正文）；报告须注明**基线提交** |

## 4. Wave 3（**严格串行** · 依赖 Wave 2 与各 loop 定义）

| 路 | 角色 | 任务 | 说明 |
|---|---|---|---|
| `3A` | `tech_lead` 先出 LOOP 定义 → `feature_pilot` 实施 | **I2（依据原文/证据链）→ I3 → I4** | **串行**：同一文件域（前端+后端）、I3/I4 依赖 I2 的契约与数据；**每个阶段结束**须 `record_gate` + 独立 QA 复核（新 loop ⇒ 先定 scope/gates/exit，再开工） |

## 5. 需 Owner 动作（唯一硬阻塞点）

- **把 `loops/PC-i1-chapter-inheritance/FORMAL-QA-ATTEST-提示词.md` 发给新会话**（`1A` 必须由非 implementation actor 执行；TL 不可代签）。
- 其余 5 项均已派发，无 Owner 阻塞；`2A`（KERT 侧写入）已获你 2026-09-23 授权。

## 6. 本轮未做（防误读）

- 未启动常驻后台智能体：本仓纪律为**单写者 + 交接档 + 角色切换**（`senior-workflow` / PC1-GOV-01 教训），并发写同一仓会破坏证据链；故以"路（wave）"编排而非空转代理。
- 未改 `specs/` 受控源、P38 冻结文件；未交他人未完成文件入仓。
