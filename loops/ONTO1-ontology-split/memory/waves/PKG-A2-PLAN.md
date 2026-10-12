# PKG-A2｜PLAN — Wave 0 输入锚点就绪预检门禁化

| 项 | 值 |
|---|---|
| PKG | **A2**（W-1.5 就绪加固，战线 A 第 2 项，`memory/PLAN-NEXT.md` §1 A2） |
| 负责人 | `pilot-a2`（Feature Pilot）；baton 仍属 `tech_lead`，本包 `parallel_allowed: [feature_pilot]`（`ROLE_BOARD.yaml:12`） |
| 依据 | `memory/W-1.5-ORCHESTRATION.md` §2/§5、`memory/PLAN-NEXT.md:53-60`、`docs/dispatch/ONTO-SPLIT-本体四层落地执行计划-V2.0.md` §2 G-1（`:56`）+ §3 Wave 0（`:58-62`）、`memory/waves/W0-PLAN.md:15-23` |
| 性质 | 只读分析 + 门禁加固；**不进 Wave 0**（`LOOP.yaml.gate_state.current = RETURN_TO_HLD`，`:19`） |
| 编制 | 2026-09-20 |

---

## 1. 目标

把 `W0-PLAN.md:15-23` 那张"W0 开工前必须核对的输入锚点"表从**文档陈述**变成**可执行红灯**。

问题（TL 原话 `PLAN-NEXT.md:55`）：G-1 达成后才核对 Wave 0 输入锚点，若发现不符（哈希漂移、映射草案过期、ADR 未签）会白白损失窗口。`W0-PLAN.md` 已声明失败条件为 "STOP"，但**没有门禁执行它**——即"失败条件是措辞，不是红灯"。

## 2. 门禁定义

- 命令：`python3 scripts/onto1_wave0_readiness.py --gate`
- 单一真值函数：`readiness(cfg) -> Report`；`--gate` / `--precheck` / `--selftest` 全部由它派生。
- 逐项输出 `READY` / `NOT_READY(<原因>)`：

| # | 锚点 | 判据 | 当前实测 |
|---|---|---|---|
| R1 | 复审包 01~14 | 逐件 sha256 与 `MANIFEST.md` 一致（14/14） | READY |
| R2 | 基线本体 | `specs/semantic/gits-core.owl.ttl` sha256 前缀 `705578d6324abd0c` 且 rdflib 计数 = 32/34/1 | READY |
| R3 | 四层归属矩阵 | `evidence/attribution-45-v2.csv` 存在且 45 资产分口径 39/1/5 可复算 | READY |
| R4 | 消费者处置表 | `evidence/consumer-scan-obligations.csv` 存在且 summary 中 `PENDING_TRIAGE = 0` | READY |
| R5 | 命名空间 ADR | `docs/architecture/ADR-ONTO1-namespace-neutral-iri-DRAFT.md` 存在且**未预填正式根域** | READY |
| R6 | D3 签署件 | **不存在** ⇒ `NOT_READY(D3 unsigned)`（**设计如此**，G-1 硬前置） | NOT_READY |
| R7 | 门禁位置 | `LOOP.yaml.gate_state.current` 已离开 `RETURN_TO_HLD` | NOT_READY |
| R8 | 基线提交记录 | `STATE.json.baseline_commit` 非 `PENDING_FIRST_COMMIT` | READY |

## 3. 两种模式（**语义必须区分，否则会被误读为"全绿"**）

| 模式 | 语义 | 期望退出码（现在） |
|---|---|---|
| `--gate` | 「**G-1 是否已满足**」= R1~R8 全 READY | **exit 2（FAIL）** —— R6/R7 未满足；逐项列出原因 |
| `--precheck` | 「**除 R6/R7 外**全部 READY？」（等待期自查） | **exit 0（PASS）** |
| `--selftest` | 变异复验 | exit 0（4 条变异 + 1 对照全符合预期） |

> **反模式警告**：任何把 R6/R7 从门禁中删掉、或把 `--gate` 换成 `--precheck` 来"变绿"的做法，
> 都是把红灯拆掉而不是把风险消除。本 PLAN 明确列入"不做清单"。

## 4. 失败条件（fail-closed）

1. 任一输入缺失 / 不可解析（MANIFEST 少登记、TTL 缺失、CSV 缺列、LOOP.yaml 不可解析、STATE.json 不可解析）⇒ 对应项 `NOT_READY`，**不跳过**；
2. rdflib 不可用 ⇒ R2 `NOT_READY(rdflib unavailable)`，**不降级为"跳过计数"**；
3. R5 出现正式根域（`NS-L1..L4` 被赋具体 `http(s)://` 值）或草案自称已 `ACCEPTED` ⇒ `NOT_READY`；
4. R6 候选签署件存在但**无签署标记**（`签署人`/`签署日期`/`SIGNED`/`Signature`）⇒ 不计为签署件（fail-closed）；
5. `--gate` 只要有 1 项 `NOT_READY` 即 exit 2。

## 5. 变异复验设计（`--selftest`，**必须非空转**）

> 关键：**本门禁当前本来就 FAIL**（R6/R7）。因此"变异后 exit==2"是**恒真断言**——正是 GK 系列
> 反复踩到的"假绿"形态（`memory/ORCHESTRATOR.md` 记录的 6 次空转）。故本 selftest **一律断言
> 到条目级**（`items["R1"].status == NOT_READY`），不断言全局退出码来凑数。

| 变异 | 注入 | 断言 |
|---|---|---|
| M1 | 沙箱内篡改 R1 一个复审包文件 | `items["R1"] = NOT_READY` 且原因含 DRIFT |
| M2a | 沙箱内改写基线 TTL 内容（计数塌为 1 类） | `items["R2"] = NOT_READY` |
| M2b | 预期计数被改为 1（TTL 原样） | `items["R2"] = NOT_READY`（隔离"计数断言有牙齿"） |
| M3a | 仅把 `gate_state.current` 置 `DESIGN_APPROVED`（R6 仍缺签署件） | `items["R7"] = READY` **且** `items["R6"] = NOT_READY` ⇒ `--gate` 仍 exit 2（证明 R6 有牙齿） |
| M3b | 仅造 D3 签署件（`gate_state` 仍 `RETURN_TO_HLD`） | `items["R6"] = READY` **且** `items["R7"] = NOT_READY` ⇒ `--gate` 仍 exit 2 |
| M3c | 造签署件 **+** `gate_state = DESIGN_APPROVED` | `--gate == PASS(exit 0)`（证明 R7 的变更确实能翻盘，即"有牙齿"） |
| M4 | 对照：真实仓库原样 | `--gate` exit 2 **且** `--precheck` exit 0 |

M3a/M3b/M3c 三条合起来才构成"R6/R7 各自有牙齿"的完整证明：单改任一项都不会变绿，两项齐备才变绿。

## 6. 不做清单

- 不改 `LOOP.yaml` / `STATE.json` / `EVIDENCE*.{md,json}` / `FAILURES.md` / `memory/*` 其它（TL 单写者）；
- 不改 `specs/**`、`generated/**`、`docs/dd/**`；不写 KERT 仓；不 `git add .`；
- 不"顺手"补 D3 签署件、不预填根域、不发布 IRI、不标 `DESIGN_APPROVED`；
- 不弱化 R6/R7 断言以换取绿灯；不把 `--gate` 的 FAIL 说成"通过"。
