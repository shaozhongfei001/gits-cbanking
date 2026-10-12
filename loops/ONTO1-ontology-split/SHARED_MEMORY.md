# ONTO1-ontology-split｜共享记忆（Loop 级）

| 项 | 值 |
|---|---|
| Loop ID | `ONTO1-ontology-split` |
| 模式 | longhaul |
| 唯一权威 | `docs/dispatch/ONTO-SPLIT-本体四层落地执行计划-V2.0.md`（执行）+ `docs/architecture/ONTOLOGY-SPLIT-DESIGN-V2.0-REVIEW.md`（设计） |
| 证据配对 | `docs/review/ARCH-ONTO-2026-001-rereview-package/MANIFEST.md`（哈希钉值） |
| 当前波次 | `W-1.5`（就绪加固：只读分析 + 门禁加固；**不进 Wave 0**） |
| 当前门禁 | `RETURN_TO_HLD` 有效；目标 `DESIGN_APPROVED` |
| 板面（2026-09-21 收工） | 30 门禁 = **29 pass / 1 fail**（唯一 fail = `wi_a4_namespace_collision`，**仅 C-2**）；`loop-guard`/`evidence-board` PASS；`independent_qa` = pending（**无人代签**） |
| 本批三包结论 | PKG-A1 **ACCEPT**（+ PKG-A1b 升格 65 行）· PKG-A2 **ACCEPT_WITH_CONDITIONS** · PKG-A3 **NOT_ACCEPTED**（7 条）· QA 二轮 **NOT_ACCEPTED**（Q-1/Q-2/Q-4 已裁定） |
| 新增纪律（必读） | **D-11** 交付与证据绑定（post-DONE 冻结 / 日志自证 revision / 审计前确认哈希稳定 / 崩溃≠FAIL）· **D-12** 放行类要求必须附"不得放行"反例清单 · **D-3 补丁**（`rule_statement` 改联合判定） |

## 1. 状态机与许可（每日核对，详见 `LOOP.yaml.gate_state`）

`FOR_REVIEW → DESIGN_APPROVED → IMPLEMENTED → QA_PASS → OWNER_ACTIVATED`

- 委员会**只批**设计基线；`IMPLEMENTED` 由 TL 记 `DEV_SELF_CHECK_PASS`；`QA_PASS` **只可由独立 QA** 记录；`OWNER_ACTIVATED` **只可由 Owner** 记录（禁止代签）。

## 2. 五态验证纪律（`06-验证状态模型与状态跃迁表`）

`PASS / FAIL / NOT_EVALUATED / DESIGN_ONLY / WAIVED_FOR_DEVELOPMENT`

- 豁免**永不**满足激活门禁；`WAIVED → PASS` 必须经复验，禁直接改写。
- 无生产实例 ⇒ `NOT_EVALUATED`，不得包装成"0 目标 0 违规"的通过。

## 3. 不做事清单（本 Loop 明确不做）

1. 统一命名（`bank-front-*` / `skill-customer-*` / `SP-*`）——后续立项；
2. 种子本体与多来源本体对齐——后续立项；
3. 产品主数据权威决策——产品 Owner（D2）；
4. 客户/法人/集团 A-Box 权威决策——数据 Owner（D4）；
5. 中立 IRI 根域决定——语义架构 Owner + 域名 Owner（D3）；
6. 国标条款级对齐——D1，已移出本次设计基线（禁止任何符合性表述、禁 `CONFORMANCE` 文件名）；
7. KERT 仓写入——本环境只读，需 Owner 授权；
8. 生产启用、重钉、隔离资产（Oracle/Ossie）启用。

## 4. 红线

- 合同先行：先登记 `CONTRACT_INDEX`（独立 `generated` 目标）→ `make generate` → `make check` → 再实现；**禁手改 `generated/`**。
- 失败先记 `FAILURES.md` 再修；**禁 `git add .`**（`docs/dd/` 下有未跟踪文件）。
- 结论必须回源 `文件:行`；未落盘结论 = 不存在。
- 双仓同窗口变更：**先钉后切**，旧值只读 ≥1 验证周期。
- 索引只是 DERIVED 派生视图：不得入库、不得进 Gate 判定、不得作为 ADR 依据。

## 5. 开场 / 收工动作

- 开场：`git status` → `LOOP.yaml`/`STATE.json`/`EVIDENCE.md` → `memory/NEXT_SESSION.md` + `ROLE_BOARD.yaml` 确认 Baton → `specs/CONTRACT_INDEX.yaml` + `specs/BASELINE_INDEX.yaml` → 输出三行开工声明（含 `[索引]`/`[回源]`）。
- 收工：更新 `EVIDENCE.md`/`STATE.json` → 交接 `NEXT_SESSION.md` + `ROLE_BOARD.yaml` → `make memory-check LOOP=ONTO1-ontology-split` 与 `make evidence-check LOOP=ONTO1-ontology-split` → 输出收工声明。
- 阻塞与自愈：可自行解决的技术/环境问题按**阶梯协议**（自愈 → 降级 → 回退）自主处理，**不要停工询问**；仅四类硬阻塞（缺凭据 / 需求冲突 / 方向性变更 / 安全隐患）+ 第五类自愈耗尽（同 Gate 5 次失败）才写 `memory/BLOCKED.md` 并停止。完整规程（停机四件动作 + 红线）见 `memory/PROTOCOL.md`「阻塞与自愈」节。

## 6. 入口索引

- 执行计划：`docs/dispatch/ONTO-SPLIT-本体四层落地执行计划-V2.0.md`
- 编排表：`memory/ORCHESTRATOR.md`
- 索引依据：`memory/INDEX_BASIS.md`
- Owner 待办：`memory/OWNER_REQUESTS.md`
- 波次迭代：`memory/waves/`
- 失败记录：`FAILURES.md`
