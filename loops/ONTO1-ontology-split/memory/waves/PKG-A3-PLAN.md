# PKG-A3｜PLAN（两处门禁小修：F1 / F2 / F3）

| 项 | 值 |
|---|---|
| 批次 | W-1.5 就绪加固（只读加固；**不进 Wave 0**） |
| 负责人 | Feature Pilot `pilot-a3` |
| 授权依据 | `memory/TL-DECISIONS-W-1.md` **D-2**（C-4 收窄）、**D-3**（元陈述放行）；`memory/PLAN-NEXT.md` §A3（B-4 / B-4b / B-6）；`FAILURES.md` FAIL-2026-09-20-05 |
| 门禁 | `wi_a4_namespace_collision` / `wi_a4_namespace_collision_selftest`、`wi_a3_reference_alignment` / `wi_a3_reference_alignment_selftest`（均为复用重跑，不新增门禁 id） |
| max_attempts | 5（单门禁） |

## 目标（三项，不扩大范围）

| # | 目标 | 依据 | 判据 |
|---|---|---|---|
| F1 | C-4 断言范围收窄为**受控钉值文件**；把"清单类工具产物不再被判钉值"做成可复算行为 | D-2 | 真实仓 `--gate` 仍 exit=2（C-2 真实 FAIL 保留）且 **C-4 噪声 FAIL 消失**；`--selftest` 含新变异 M13（放回扫描集 ⇒ FAIL）且 M12 已同步调整（未删除） |
| F2 | 碰撞脚本头部自述与实现一致（C-4 不是"可判定 → PASS"） | 本轮实测（`C-4_PIN_FILE_UNFROZEN`） | 头部 C-4 行写明"漂移/受控载体未冻结 ⇒ FAIL"并注明 D-2 适用范围 |
| F3 | 参照对齐守卫放行"**规则陈述行**"，且放行留计数、不扩散到制品中的声称 | D-3 | `--gate` exit=0；输出含 `allowed[rule_statement]=N`；`--selftest` 含"真实符合性声称（无元陈述关键词，与规则行同文件相邻）⇒ 仍 FAIL" |

## 失败条件（任一即 FAIL，先记 FAILURES 再修）

1. `python3 scripts/onto1_namespace_collision_check.py --gate` 整体 **不再 FAIL**（C-2 两处真实冲突被"顺手"放过）⇒ 视为越权改判；
2. 真实仓 C-4 仍报 `C-4_PIN_FILE_UNFROZEN` 噪声（收窄未生效）；
3. `--selftest` 任一门禁出现 `[FAIL]`，或新增变异"恒绿"（把清单类产物放回扫描集却仍 PASS）；
4. 为过门禁而**删除**任何断言 / 变异用例 / 硬编码冻结值（`FROZEN_01_12` 类型）/ 放松 C-2；
5. 参照对齐守卫把**制品中的真实声称**误放行（放行扩散）。

## 不做清单（本包不碰）

- 不改 `specs/**`、`generated/**`、`docs/dd/**`；不写 KERT 仓；不改 TL 单写者文件（`LOOP.yaml`、`EVIDENCE.json`、`EVIDENCE.md`、`STATE.json`、`FAILURES.md`、`memory/{ROLE_BOARD,NEXT_SESSION,ORCHESTRATOR,PLAN-NEXT,W-1.5-ORCHESTRATION,INDEX_BASIS,TL-DECISIONS-*}`）；
- 不改 `evidence/baseline-v2-manifest.json`、`evidence/consumer-scan-manifest.json`、`evidence/non-gate-log-allowlist.json`（非本包写域，且为他人交付物）；
- 不新增门禁 id、不据真实退出码自行记账（只提交"登记建议"，由 TL 执行 `record_gate.py`）；
- 不修 C-2 两处真实前缀冲突（属 Wave 3）；
- 不把 `loops/**` 整体加进守卫白名单（D-3 选择的是"元陈述关键词放行"，不是路径豁免）。

## 交付物

1. `scripts/onto1_namespace_collision_check.py`（F1 + F2）；
2. `scripts/onto1_reference_alignment_check.py`（F3）；
3. `loops/ONTO1-ontology-split/evidence/a3fix-{before,after}-*.log`（前后对比实测）；
4. `memory/waves/PKG-A3-ITER.md`、`memory/handoffs/PKG-A3-HANDOFF.md`（含登记建议）。

## 判定范围常量（F1 预声明，便于 TL 审计"未被悄悄放大/放松"）

- **受控**（D-2）：`specs/semantic/**`、`specs/CONTRACT_INDEX.yaml`、`**/90_control/schema/ontology_reference.json`、`**/90_control/ontology/PROVENANCE.json`
- **范围外**（D-2 排除的清单类工具产物）：`loops/**`、`evidence/**`
- **其余**：范围未裁决 ⇒ **fail-closed FAIL**（不得静默略过）
- 空转防护：受控条目为 0 ⇒ **FAIL**（收窄不得收窄到空）
