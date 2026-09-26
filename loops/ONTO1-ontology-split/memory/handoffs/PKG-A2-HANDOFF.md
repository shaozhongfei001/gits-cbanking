# PKG-A2 HANDOFF — Wave 0 输入锚点就绪预检门禁化

| 项 | 值 |
|---|---|
| PKG | **A2**（W-1.5 就绪加固） |
| 负责人 | `pilot-a2`（Feature Pilot） |
| 状态 | **DONE**（三模式实测完成；等待 TL 审核 AU-1~AU-7 + 记账） |
| 日期 | 2026-09-20 |
| 依据 | `memory/W-1.5-ORCHESTRATION.md` §5 PKG-A2（`:75`）、`memory/PLAN-NEXT.md` §1 A2（`:53-60`）、`memory/waves/W0-PLAN.md:15-23`、执行计划 V2.0 §2 G-1（`:56`）/§3 Wave 0（`:58-62`） |

---

## 1. 交付物与哈希

| # | 文件 | sha256（前 16） | 性质 |
|---|---|---|---|
| 1 | `scripts/onto1_wave0_readiness.py` | `285bada36ca55de5` | 门禁脚本（单一真值函数 + fail-closed + 变异复验） |
| 2 | `loops/ONTO1-ontology-split/evidence/wave0-readiness-gate.json` | `0c6b7498531957c5` | 机读逐项结果（`--gate --report` 产出） |
| 3 | `loops/ONTO1-ontology-split/evidence/wave0-readiness-20260920T1520Z.log` | `4d67e70be5ec1e4b` | 三模式原始输出 + 逐条 exit（诚实运行日志） |
| 4 | `memory/waves/PKG-A2-PLAN.md` | — | PLAN（目标/门禁/失败条件/变异设计/不做清单） |
| 5 | `memory/waves/PKG-A2-ITER.md` | — | ITER（3 个 attempt，2 个真实自愈） |
| 6 | 本文件 `memory/handoffs/PKG-A2-HANDOFF.md` | — | HANDOFF |

命令：

```
python3 scripts/onto1_wave0_readiness.py --gate       # G-1 是否已满足
python3 scripts/onto1_wave0_readiness.py --precheck   # 等待期自查（除 R6/R7 外）
python3 scripts/onto1_wave0_readiness.py --selftest   # 变异复验
python3 scripts/onto1_wave0_readiness.py --gate --report <path.json>
```

## 2. 门禁实测（**原始输出，未加工**）

| 模式 | exit | 语义 | 期望 | 一致 |
|---|---|---|---|---|
| `--gate` | **2** | 「G-1 是否已满足」R1~R8 全 READY 才 0 | **G-1 未达成时期望 fail(2)** | ✅ |
| `--precheck` | **0** | 「除 R6/R7 外全部 READY？」 | 现在期望 PASS(0) | ✅ |
| `--selftest` | **0** | 16 条条目级变异/对照断言 | 期望 PASS(0) | ✅ |
| `scripts/onto1_evidence_board_check.py --gate` | **0** | 新证据未产生孤儿日志（E2 orphan=0） | PASS | ✅ |

### 2.1 逐项结果（`--gate`，2026-09-20 23:18 CST）

| # | 锚点 | 结果 | 回源依据 |
|---|---|---|---|
| R1 | 复审包 01~14 哈希 | **READY** | `docs/review/ARCH-ONTO-2026-001-rereview-package/MANIFEST.md:17-30` 14 行登记项，逐件 sha256 复算一致（14/14） |
| R2 | 基线本体哈希与计数 | **READY** | `specs/semantic/gits-core.owl.ttl` sha256=`705578d6324abd0c…`；rdflib 6.1.1 解析计数 Class=32 / ObjectProperty=34 / DatatypeProperty=1 |
| R3 | 四层归属矩阵 | **READY** | `loops/ONTO1-ontology-split/evidence/attribution-45-v2.csv` 87 行；按 `概念类型` 列复算 OWL类=39 / SKOS概念体系=1 / Schema对象*=5（合计 45） |
| R4 | 消费者处置表 | **READY** | `evidence/consumer-scan-obligations.csv` 1052 行；`evidence/consumer-scan-summary.csv` 1406 行中 `PENDING_TRIAGE = 0` |
| R5 | 命名空间 ADR 草案 | **READY** | `docs/architecture/ADR-ONTO1-namespace-neutral-iri-DRAFT.md:12`；状态字段解析值 = `PROPOSED`；无 `NS-L1..L4` 被赋具体 `http(s)://`；占位符 `{NS-L1}` 仍在（`:48`） |
| R6 | D3 签署件 | **NOT_READY(D3 unsigned)** | **设计如此**——G-1 硬前置之一（执行计划 §2 `:56` ③ / `LOOP.yaml:77`）。`docs/architecture/*ADR-ONTO1*` 下无任何带签署标记的载体（唯一文件是 `-DRAFT.md`） |
| R7 | 门禁位置 | **NOT_READY(still RETURN_TO_HLD)** | `loops/ONTO1-ontology-split/LOOP.yaml:19` `gate_state.current = "RETURN_TO_HLD"` |
| R8 | 基线提交记录 | **READY** | `loops/ONTO1-ontology-split/STATE.json` `baseline_commit = 71169042227ce86f870cea81b50f77bf985ffe7f`（非 `PENDING_FIRST_COMMIT`） |

**唯二 NOT_READY 恰为 R6/R7**（`--selftest` M4b 显式断言这一点），未见任何意料之外的锚点漂移。

### 2.2 变异复验（`--selftest`，16 条断言全 PASS）

| 变异 | 断言（**条目级，非 exit 码**） |
|---|---|
| M1 | 篡改复审包 `01` ⇒ `items["R1"]=NOT_READY`（原因含 MANIFEST drift） |
| M2a | 基线 TTL 内容变形 ⇒ `items["R2"]=NOT_READY`（sha256 prefix drift） |
| M2b | 预期计数改 1（TTL 原样）⇒ `items["R2"]=NOT_READY`（count mismatch `(32,1)`）——隔离证明计数断言有牙齿 |
| M3a | 仅置 `DESIGN_APPROVED` ⇒ R7 READY / **R6 仍 NOT_READY** ⇒ gate FAIL ⇒ **R6 有牙齿** |
| M3b | 仅造 D3 签署件 ⇒ R6 READY / **R7 仍 NOT_READY** ⇒ gate FAIL ⇒ **R7 有牙齿** |
| M3c | 签署件 + `DESIGN_APPROVED` ⇒ **全项 READY ⇒ gate PASS**（`residual={}`）——门禁非永久红 |
| M3d | 改名冒充"签署件"但无签署标记 ⇒ `R6 NOT_READY`（fail-closed） |
| M5 | 预填正式根域 `NS-L1: https://…` ⇒ `R5 NOT_READY` |
| M6 ×6 | R1/R3/R4/R5/R7 输入缺失、R8 = `PENDING_FIRST_COMMIT` ⇒ 全部 `NOT_READY`（**不得跳过**） |
| M4/M4b | 对照：真实仓库 ⇒ `--gate` FAIL / `--precheck` PASS，且 NOT_READY 恰为 `['R6','R7']` |

## 3. 登记建议（TL 执行 `record_gate.py`；**pilot 不记账**）

> **记账口径必须先看**：本门禁 `--gate` 现在**真实 exit = 2**。按 D-1 红测记账规则，必须记为
> **fail 并如实写明原因（R6/R7 未满足，设计如此）**，**禁止**改写为 `inconclusive` 或用
> `--precheck` 冒充 `--gate`（否则就是 W-1.5 §3 明令禁止的"把 fail 包装为通过"）。
> 建议同时登记 `--precheck` 与 `--selftest` 两个**当前为 pass** 的条目，使板面能区分
> "等待期确定性锚点全绿"与"G-1 未达成的预期红"。

```yaml
- id: wi_a2_wave0_readiness
  owner_kind: implementation
  command: python3 scripts/onto1_wave0_readiness.py --gate
  expected_exit: 2            # 记录值 = fail（当前实测 exit 2）
  pass_condition: >
    Wave 0 输入锚点 R1~R8 全部 READY ⇒ exit 0。**G-1 未达成时期望 fail（exit 2）**：
    R6（D3 签署件未签）/ R7（LOOP.yaml.gate_state.current 仍 RETURN_TO_HLD）在 G-1 前
    必然 NOT_READY，属设计如此，不是缺陷；其余锚点（R1~R5/R8）此时必须 READY，
    若其中任一 NOT_READY 则说明出现真实漂移。G-1 达成后（签署件落地 + gate_state 离开
    RETURN_TO_HLD）本门禁应转 exit 0。

- id: wi_a2_wave0_readiness_precheck
  owner_kind: implementation
  command: python3 scripts/onto1_wave0_readiness.py --precheck
  expected_exit: 0            # 记录值 = pass（当前实测 exit 0）
  pass_condition: >
    除 R6/R7 外的确定性锚点（R1 复审包 14/14 哈希、R2 基线 705578d6…/32-34-1、
    R3 归属矩阵 39/1/5、R4 处置表 PENDING_TRIAGE=0、R5 ADR 未预填根域、R8 基线提交非
    PENDING_FIRST_COMMIT）全部 READY ⇒ exit 0。用于等待期回归：任一锚点漂移即转 fail。

- id: wi_a2_wave0_readiness_selftest
  owner_kind: implementation
  command: python3 scripts/onto1_wave0_readiness.py --selftest
  expected_exit: 0            # 记录值 = pass（当前实测 exit 0）
  pass_condition: >
    16 条**条目级**变异/对照断言全 PASS ⇒ exit 0：M1 篡改复审包件、M2a/M2b 基线哈希与计数、
    M3a/M3b 分别证明 R6/R7 不被对方掩护通过、M3c 条件齐备时 gate 可转 PASS、
    M3d 无签署标记不计为签署件、M5 预填根域被拦、M6 六类缺输入 fail-closed。
    断言一律锚定 items["Rx"].status，**不得**用"门禁本就 FAIL ⇒ exit==2"的恒真断言充数
    （GK 系列 6 次空转的同一根因）。
```

`evidence_file` 建议：`loops/ONTO1-ontology-split/evidence/wave0-readiness-20260920T1520Z.log`。

## 4. 未决与风险（**如实声明，不隐瞒**）

1. **M3 与派工单字面表述的偏离**（已在 ITER 记录）：派工单写「单改 R7 ⇒ `--gate` 转 PASS」。
   实测单改 R7 后 gate 仍 FAIL，因为 R6 是独立锚点。若强行满足该字面要求，必须把 R6 从全项
   判据中摘除——即拆红灯，违反 PLAN §6。故实现为 M3a/M3b/M3c 三条分解断言，
   M3c 证明"条件齐备时确实转 PASS"。**请 TL 裁定此偏离是否接受**；若要求严格字面实现，
   请指出 R6 应如何从 `--gate` 的全项语义中排除（我不自行决定）。
2. **R5 的语义会随 D3 签署翻转**：R5 现在检查"草案存在且未预填根域"（WI-A4 纪律）。
   D3 签署后根域**应当**被填入，届时 R5 会转 NOT_READY。这是**预期的时间窗翻转**，
   不是漂移。建议 D3 签署时同步把 R5 判据改为"签署件存在且根域已填 + 非占位值"，
   或在 ADR 定稿时以具名 supersede 处理（属 TL/语义架构 Owner 决定，本包不预判）。
3. **R6 的"签署件"载体集合是先验枚举的**：`ADR-ONTO1-namespace-neutral-iri.md`（去 DRAFT）/
   `*ADR-ONTO1*签署*` / `*ADR-ONTO1*SIGNED*` / `*ONTO1-D3*签署*`，且必须含签署标记
   （`签署人`/`签署日期`/`SIGNED`/`Signature`/`signed by`）。如果实际签署件落到别的命名，
   门禁会 fail-closed（宁红不假绿）。建议 D3 签署时把实际文件名回填进 `D3_SIGNED_PATTERNS`。
4. **`--gate` 的"全项语义"是否包含 R7**：若 TL 认为 Wave 0 的开工判据只应看外部锚点
   （R1~R6/R8）而 R7 属于 TL 的记账动作，则 `--gate` 与 `--precheck` 的边界需重定义。
   本包按派工单原样实现为"R1~R8 全项"，未擅自收窄。
5. `STATE.json`（23:17:43）与 `memory/ROLE_BOARD.yaml`（23:17:14）在本包作业窗口内被改动——
   **是 TL 并发写入，非本包**：脚本唯一的写路径是 `--report <path>`（本包只写过
   `evidence/wave0-readiness-gate.json`），无任何代码路径触碰 LOOP.yaml/STATE.json/EVIDENCE*。

## 5. 红线声明（AU-5 可核）

本包**未**改动：`LOOP.yaml` / `STATE.json` / `EVIDENCE.json` / `EVIDENCE.md` / `FAILURES.md` /
`memory/{ROLE_BOARD,NEXT_SESSION,ORCHESTRATOR,PLAN-NEXT,W-1.5-ORCHESTRATION}` 等 TL 单写者文件；
`specs/**` / `generated/**` / `docs/dd/**`；KERT 仓（只读）。未 `git add`，未 commit，未 push。

**未做**（防"顺手把红灯拆掉"）：未修改 `LOOP.yaml` 抬高门禁位置、未创建/伪造 D3 签署件、
未预填 ADR 根域、未删除或弱化 R6/R7 判别、未把 `--gate` 的 fail 包装为 pass。

`scripts/onto1_review_package_check.py` 按要求**只读参考、未改**。

## 6. 自审（三件套）

| DoD | 状态 |
|---|---|
| 单一真值函数 | ✅ `readiness(cfg)`；`--gate`/`--precheck`/`--selftest` 全部派生，无第二套判据 |
| fail-closed | ✅ 缺输入/不可解析/rdflib 缺失/无签署标记 一律 NOT_READY，M6 六类实证 |
| 变异复验 | ✅ 16 条条目级断言全 PASS（**非空转**：条目级断言 + M4b 唯二 NOT_READY 断言） |
| 无 TODO/占位 | ✅ 无 TODO/FIXME/pass 占位；未填根域，未伪造签署件 |
| HANDOFF 含登记建议 | ✅ §3（含"G-1 未达成时期望 fail"口径与被拒的包装路径） |
