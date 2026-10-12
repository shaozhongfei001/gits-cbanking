# PKG-A2｜ITER — Wave 0 输入锚点就绪预检门禁化

> 每个 attempt = 命令 + exit + 输出摘要。禁改后不回填（自愈过程如实保留）。
> 交付物：`scripts/onto1_wave0_readiness.py`

---

## Attempt 1（2026-09-20 23:15 CST）

**命令**

```
python3 scripts/onto1_wave0_readiness.py --gate ; echo exit=$?
python3 scripts/onto1_wave0_readiness.py --precheck ; echo exit=$?
```

**exit**：`--gate = 2`（符合预期） / `--precheck = 2`（**不符预期，应 0**）

**输出摘要**

```
R1 READY  R2 READY  R3 READY  R4 READY
R5 NOT_READY(draft self-declared ACCEPTED while unsigned)   ← 误判
R6 NOT_READY(D3 unsigned)     ← 设计如此
R7 NOT_READY(still RETURN_TO_HLD)  ← 设计如此
R8 READY
onto1-wave0-readiness[gate]: FAIL     exit=2
onto1-wave0-readiness[precheck]: FAIL exit=2
```

**根因（真实缺陷，非环境问题）**：R5 的"草案自称已批准"判据写成了全文包含匹配
`D3_RATIFIED_MARKER in text`。而 `ADR-ONTO1-namespace-neutral-iri-DRAFT.md:9` 的状态行是

```
| 状态 | `PROPOSED`（语义架构 Owner 与域名 Owner 签署前不得转为 `ACCEPTED`） |
```

正文里出现 `ACCEPTED` 是为了**声明禁止**转入该状态，属纪律陈述而非状态声明。
全文包含匹配把"禁止事项"读成了"已发生事项" ⇒ 假阳性，`--precheck` 被自身误判卡住。

**修复**：新增 `declared_adr_status()` / `is_adr_ratified()`，**只解析状态字段的值**
（表格行 `| 状态 | X |` 或行内 `状态: X`），取首个标识符判等，不做全文包含匹配。
R5、R6 两处判据同步改用该函数。

**教训（本项目反复出现的形态）**：否定式纪律（"不得转为 X"）与状态断言共用同一个词面时，
包含匹配必然把纪律读成事实。与本 Loop `FAILURES.md` 记录的 `NAMESPACE_MISMATCH_SILENTLY_GREEN`
同类：**判据必须锚定字段/路径，不能锚定词面**。

---

## Attempt 2（2026-09-20 23:17 CST）

**命令**

```
python3 scripts/onto1_wave0_readiness.py --gate ; echo exit=$?
python3 scripts/onto1_wave0_readiness.py --precheck ; echo exit=$?
python3 scripts/onto1_wave0_readiness.py --selftest ; echo exit=$?
```

**exit**：`--gate = 2` ✅ / `--precheck = 0` ✅ / `--selftest = 1`（**崩溃**）

**输出摘要**

```
PASS  M4 对照：真实仓库 ⇒ --gate FAIL / --precheck PASS
PASS  M4b 对照：NOT_READY 恰为 ['R6','R7']
Traceback ... ValueError: '/tmp/onto1-wave0-readiness-selftest-xxxx/pkg/MANIFEST.md'
            is not in the subpath of '/home/szf/dev/gits-cbanking'
```

**根因**：证据串用 `path.relative_to(cfg.root)` 拼装；selftest 的沙箱路径在 `/tmp` 下，
不在 `cfg.root` 之下 ⇒ `ValueError`。这是 selftest 自身的设计缺陷（沙箱与根目录不同源）。

**修复**：新增 `rel(path, root)`（`relative_to` 失败退回绝对路径），8 处调用点全量替换。

---

## Attempt 3（2026-09-20 23:18 CST）— PASS

补强 DoD「**缺任一输入 ⇒ 门禁 FAIL（fail-closed）**」的实证：新增 M6，对 R1/R3/R4/R5/R7/R8
六类"输入缺失 / `PENDING_FIRST_COMMIT`"逐一断言必须 `NOT_READY`（不得"跳过"）。

**命令**

```
python3 scripts/onto1_wave0_readiness.py --gate       ; echo exit=$?
python3 scripts/onto1_wave0_readiness.py --precheck   ; echo exit=$?
python3 scripts/onto1_wave0_readiness.py --selftest   ; echo exit=$?
python3 scripts/onto1_evidence_board_check.py --gate  ; echo exit=$?
```

**exit**：`--gate = 2` ✅（期望 FAIL） / `--precheck = 0` ✅ / `--selftest = 0` ✅ / 证据板 = 0 ✅

**输出摘要（16 条断言全 PASS）**

```
PASS  M4  对照：真实仓库 ⇒ --gate FAIL / --precheck PASS (gate_pass=False, precheck_pass=True)
PASS  M4b 对照：NOT_READY 恰为 ['R6','R7']（防止"别处也坏了却当成设计如此"）
PASS  M1  篡改复审包 01 ⇒ R1 NOT_READY（MANIFEST drift DRIFT=['01-主设计-V2.0-复审快照.md(...)']）
PASS  M2a 基线 TTL 变形 ⇒ R2 NOT_READY（sha256 prefix drift e94792e1… != 705578d6…）
PASS  M2b 预期计数改 1（TTL 原样）⇒ R2 NOT_READY（count mismatch {'owl_class': (32, 1)}）
PASS  M3a 仅置 DESIGN_APPROVED ⇒ R7 READY / R6 NOT_READY ⇒ R6 有牙齿
PASS  M3b 仅造 D3 签署件 ⇒ R6 READY / R7 NOT_READY ⇒ R7 有牙齿
PASS  M3c 签署件 + DESIGN_APPROVED ⇒ --gate 转 PASS（residual={}）
PASS  M3d 改名冒充无签署标记 ⇒ R6 NOT_READY（fail-closed）
PASS  M5  预填正式根域 ⇒ R5 NOT_READY（formal root domain ALREADY FILLED）
PASS  M6  ×6：R1/R3/R4/R5/R7 缺输入、R8 PENDING_FIRST_COMMIT ⇒ 全 NOT_READY
onto1-wave0-readiness-selftest: PASS
```

**证据**

- `evidence/wave0-readiness-20260920T1520Z.log`（三模式原始输出 + 逐条 exit）
- `evidence/wave0-readiness-gate.json`（机读逐项结果）
- script sha256 = `285bada36ca55de53317f09088deef7a75f1053b3e09fdf886759e0bf0f03dee`

---

## 关于「M3 单改 R7 为什么 gate 不转 PASS」的说明（**不是弱化断言**）

派工单写的是「③ 把 R7 人为置为 `DESIGN_APPROVED` ⇒ `--gate` 转 PASS（证明 R7 有牙齿）」。
实测发现：单独改 R7 时 `--gate` **仍 FAIL**，因为 R6（D3 签署件）是**独立锚点**，
G-1 的两个硬前置（书面复审结论 + D3 签署）不是一个变量。若强行让"只改 R7 ⇒ PASS"成立，
就必须在实现里把 R6 从全项判据中摘出去——那正是**拆红灯**，与 PLAN §6 不做清单冲突。

故拆成三条并如实记账：

| 变异 | 断言 | 证明 |
|---|---|---|
| M3a | 仅 R7 改 ⇒ R7 READY、R6 仍 NOT_READY ⇒ gate FAIL | R6 有牙齿（不被 R7 掩护通过） |
| M3b | 仅 R6 满足 ⇒ R6 READY、R7 仍 NOT_READY ⇒ gate FAIL | R7 有牙齿（不被 R6 掩护通过） |
| M3c | R6 + R7 齐备 ⇒ 全项 READY ⇒ gate PASS | **G-1 语义可被真正满足，门禁不是永久红** |

M3c 是"R7（及 R6）有牙齿"的等价且更强的证明：门禁**能**在条件齐备时转绿，
说明它的 FAIL 来自真判据而非写死。该偏离已在 HANDOFF「未决与风险」中显式声明。
