# GK-KE OC-04 第二轮独立 QA 核验报告

> 核验者：独立 QA（第二轮，非本会话 TL）
> 核验日期：2026-09-13
> 核验对象：TL 对第一轮三条指控的修复 + Owner 三条裁定的执行 + A 层收口决议
> 实际核验 HEAD：`8c8ec1c`（派发锚点 `5e46cb5` 之后 +1 提交 "re-review dispatch prompt"）
> KERT HEAD：`0b7c83f`（与派发说明一致）
> 核验原则：每条回到源头复现；破坏性验证后一律恢复；不因"门禁全绿"即判通过。

---

## 一、修复核验结论（逐条对应 §二 的 7 项 + §三 的 3 条裁定）

### §二 修复项

| # | TL 声称的修复 | 判定 | 独立证据 |
|---|---|---|---|
| 1 | 探针改为真实调用 KERT | **证实** | 读 `gk_ke_capability_probe.py` v2.0.0：`real_call()` 真正调用 `svc.execute(skill_id, req_id, payload)`；`build_service()` 真实 import 并构造 `SkillExecutionService`。**破坏性验证**：破坏 KERT `_load_packages` 的 `schema_keys` 抽取（置空）后，探针从 `PASSED=8` **骤降为 `PASSED=0, NOT_PROBED=12`**。证明探针真实依赖 KERT 侧 schema，非自欺。 |
| 2 | 反事实检验强制读合同 | **证实** | 读 `gk_ke_counterfactual_test.py` v2.0.0：第 178 行 `json.loads(OBLIGATIONS.read_text())` 真实读取合同；变异由 `obligations[].upstreamFields` 派生（第 196-198 行）。**破坏性验证**：从 `ConsumerObligations.json` 删掉 OBL-07 后，变异数从 12 → 11（OBL-07 的 `requiredQuestions` 变异消失），证明合同被真实读取、变异真实派生。且结论已改名为 `CONSUMPTION_PROVEN_LOGIC_ONLY`，明确标注"**不得**据此声称 §14.2 第 6 项达成"。 |
| 3 | 编译门禁 BLOCKED → 返回 1 | **证实** | 读 `gk_ke_plan_compiler.py` 第 229-236 行：BLOCKED 时打印 stderr 后 `return 1`。**破坏性验证**：临时把 FACT-RECON `callable=false`，plan_compiler 转 BLOCKED 且 `exit=1`。 |
| 4 | KERT 侧技能返回各自 schema 结构 | **证实** | KERT 提交 `0b7c83f`；`skills.py` `_load_packages`（第 164-184 行）抽取 `schema_keys`，`run_pkg`（第 565-572 行）执行后按 `schema_keys` fail-closed 校验。探针 8 个 PASSED 各自返回不同键集（fact-recon → indicators/conflicts 等）。 |
| 5 | 期望值改为从 KERT schema 派生 | **证实** | `gk_ke_capability_probe.py` `expected_keys_from_kert()`（第 59-76 行）从 `svc._packages[provider]["schema_keys"]` 读取，**不再是 GK-KE 侧硬编码**。TL 自陈"硬编码 customerId 而 report-assembler 无该键"的错误，已通过派生消除。 |
| 6 | 门禁套件跑完再汇总 | **证实** | `run_gates.py` 第 78-90 行逐项 `subprocess.run` 并汇总，**不因单个失败中断**。实测跑出 15 项结果表。`make check` 已改为调用 `run_gates.py`。 |
| 7 | 探针变异测试含 M0/M9 | **证实** | `gk_ke_capability_probe_tests.py` 含 M0（第 110-115 行：dryRunVerified=true 但无服务 → 不得 PASSED）与 M9（第 145-151 行：调用成功但输出不符契约 → 须 CALLED_CONTRACT_UNMET）。实测 10/10 变异通过。**变异验证**：把探针 `svc is None` 分支注入为 `verdict="PASSED"`，M0 正确转 FAIL。 |

### §三 Owner 三条裁定的执行

| # | 裁定 | 执行到位？ | 独立证据 |
|---|---|---|---|
| 1 | KERT 技能返回各自 schema 结构，由全局 TL 改 | **到位** | KERT `0b7c83f` 实修；pytest 28 passed（我复跑）。 |
| 2 | OC-04 按 A 层收口并显式声明 B 层未达成 | **到位（见 §三 专门复核）** | `GK-KE-OC04-A层收口决议-V1.0.md` §5.1 明确 B 层"❌ 未达成，显式声明"；§5.3 列出 3 个具体缺口；§5.4 列 4 项"不主张"。**未用"部分达成"弱化。** |
| 3 | B 层未达成前不暂停投入 | **到位** | 决议 §6 列出 4 项后续推进事项，含"meeting/outreach 需 KERT 补 schema"的新识别需求。 |

---

## 二、六个攻击点的结果

### §四.1 探针是否真的调用 KERT —— **真的调用，证实**
破坏性验证（见 §一 #1）：破坏 KERT `schema_keys` 抽取后 `PASSED=8 → 0`。探针的 PASSED 依赖 KERT 侧真实声明的 schema 与真实 `execute()` 调用，不再是静态 `dryRunVerified`。

### §四.2 反事实是否真读合同 —— **真读，证实**
破坏性验证（见 §一 #2）：删 OBL-07 后变异 12 → 11。且脚本诚实声明下游为**参考实现**，结论为 `CONSUMPTION_PROVEN_LOGIC_ONLY`，**明确标注不得据此声称 §14.2 第 6 项达成**——这正是第一轮指控的核心，TL 已如实纠正。

### §四.3 编译门禁是否真会失败 —— **真会失败，证实**
破坏性验证（见 §一 #3）：FACT-RECON 置 false 后 BLOCKED 且 `exit=1`。第一轮的"门禁空转"已消除。

### §四.4 KERT 侧修复是否真的修好行为 —— **真的修好，证实，但有一个诚实性权衡需指出**
- 独立验证结构：`_load_packages` 抽取 `schema_keys`、`run_pkg` fail-closed 校验、确定性适配器 `_sample_package` 按 schema 生成带 `DETERMINISTIC_PLACEHOLDER` 标注的输出。各技能返回各自键集，不再是统一 R1 报告。
- pytest 28 passed（我复跑）。
- **关于"会不会破坏真实 LLM 场景"**：`run_pkg` 的 fail-closed 校验对真实 LLM 与确定性适配器一视同仁——真实 LLM 若输出缺 schema 键也会被 `ValueError` 拒绝。这是**收紧而非放宽**，符合 §14.2"不得静默降级"，但**存在"真实 LLM 输出略有偏差即整体失败"的工程风险**。这不算"为通过而努力"，反而是"为诚实而收紧"。TL 未在决议中充分讨论此权衡，属**可改进项**，非缺陷。

### §四.5 期望值是否真从 KERT 派生 —— **真派生，证实**
`expected_keys_from_kert` 从 `svc._packages[provider]["schema_keys"]` 读取（第 59-76 行），消除了 GK-KE 侧硬编码。TL 自陈"硬编码 customerId"的错误已修复。

### §四.6 M0 是否真能防住静态标志冒充 —— **真能防住，证实**
变异验证（见 §一 #7）：把探针 `svc is None` 分支注入 `verdict="PASSED"` 后，M0 断言正确转 FAIL。M0 非空转。

---

## 三、A 层收口的复核（§五.1）

读 `docs/architecture/GK-KE-OC04-A层收口决议-V1.0.md`：

| 检查点 | 结果 |
|---|---|
| A 层收口表述是否精确 | **精确**。§5.2 明确"OC-04 在 A 层（定义验收）收口。B 层未达成，本轮不主张、不暗示、不替代。C 层未开始。" |
| B 层是否明确写"未达成"（非"部分达成"） | **明确写"未达成"**。§5.1 B 层"❌ 未达成，显式声明"；§5.4 明列"❌ 不主张 B 层'部分达成'（是'未达成'）"。 |
| 是否列出 B 层具体缺口 | **是，3 项具体**：① 能力间消费运行时 trace 缺失；② 三阶段持久化未实现；③ 端到端链路未验证。 |
| 是否有"不主张事项"清单 | **是，4 项**：不主张全面关闭、不主张 B 层部分达成、不主张文档替代运行证据、不主张 A 层推导 B 层。 |

**结论**：A 层收口决议的表述精确、B 层明确"未达成"（未弱化为"部分达成"）、有具体缺口清单与"不主张事项"清单，**防止了扩大解释**。TL 对裁定 2 的执行到位，未用模糊表述变相弱化。

---

## 四、TL 披露完整性与"为通过而努力"的检查（§五.2）

### 4.1 披露完整性 —— 完整，且超过预期

TL 在 FAILURES.md 新增 `FAIL-2026-09-13-11`，**完整接受三条指控**，并诚实记录了"修复前的真实结果"：
- 探针 PASSED 从声称 11/12 → 修复前实测 **0**（8 CALLED_CONTRACT_UNMET + 1 CALL_FAILED + 3 NOT_PROBED）
- 消费证明从"14/14 达成"→ 合同驱动首跑 PARTIAL（3 项未消费）
- 计划编译 COMPILABLE → BLOCKED
- 门禁从"全绿"→ 14/15（1 项 READINESS NOT MET）

**并自陈了深层的第 4 个发现**：KERT 对所有 `bank-front-*` 技能返回同一个通用结构，不符合任何技能自身的 output-schema——这是一个**第一轮 QA 也未直接指出、TL 自行发现并修复的更深缺陷**。这条披露**超出 QA 要求的范围**，说明 TL 不是在应付核验。

### 4.2 "为通过而努力"的痕迹排查 —— 未发现

我重点排查了三处最可能"为通过而放宽"的地方：

1. **枚举扩展**（`gk_ke_l2_2_registry_tests.py` 9 行改动）：`probeStatus` 合法值从 `{PASSED,FAILED,NOT_PROBED}` 扩展为加入 `CALLED_CONTRACT_UNMET`/`CALL_FAILED`。这是**配合探针 v2 新枚举的正确同步**，且两个新值**都不是 PASSED**（`callable` 守卫 `probe != "PASSED" and callable → fail` 保持不变）。**不是放宽。**

2. **探针 v2 的 PASSED 判定**：从"静态 dryRunVerified"改为"真实调用 + schema 校验"，是**收紧**而非放宽。且 8 个 PASSED 都有 `REAL_CALL_VIA_KERT_SkillExecutionService` 的 method 标注。

3. **反事实结论降级**：从 `CONSUMPTION_PROVEN` 降为 `CONSUMPTION_PROVEN_LOGIC_ONLY`，并显式声明"不得据此声称 §14.2 第 6 项达成"。这是**主动降级**，不是为通过而抬高。

**未发现删除断言、放宽阈值、调整判据以刚好通过的行为。**

### 4.3 我发现的 TL 未披露/可改进问题（最有价值的产出）

1. **【低-中】§14.2 第 3 项"指标可复算"的实质降级仍未解决**（承自第一轮，本轮未改）。`gk_ke_metric_definitions_check.py` 的 `recompute()` 仍对所有指标统一 `sum()`，对 RATIO 型（DEBT_ASSET_RATIO）和 DAYS 型（CASH_CONVERSION_CYCLE）指标，"复算"实际是"对数据列求和"，未执行指标自身公式。TL 在 A 层收口决议 §4 第 3 项仍写"19 项定义、14 项实测复算"，**未对这个实质降级做任何标注**。这属于 A 层"指标可测试"的一个未闭合小缺口，建议在 A 层收口中补一句诚实限定。

2. **【低】fail-closed 在真实 LLM 场景的工程风险未讨论**（见 §四.4）。`run_pkg` 对真实 LLM 输出缺 schema 键即 `ValueError` 拒绝，这在真实模型返回略有偏差时会导致整体失败。TL 未在决议中权衡此点。属可改进项，非缺陷。

3. **【信息】`run_gates.py` 中 `capability-probe`/`counterfactual-test`/`plan-compiler` 被归为 `readiness` 类别**，与 `integrity` 分开，并在输出中提示"就绪度未达成≠制品损坏"。这是**正确的分层**，但需注意：`make check`（= run_gates）现在**把 readiness 未达成也算作整体失败**（`return 1 if failed else 0`，`failed` 含 readiness）。这意味着**将来 B 层 trace 缺失时，若某个 readiness 门禁因诚实报告"未达成"而返回非零，`make check` 会整体失败**——这与"诚实报告 vs 门禁失败"的语义需要 TL 在未来明确界定，避免"为让 make check 通过而把未达成改成达成"的倒逼。这是一个**前瞻性风险提示**，非当前缺陷。

---

## 五、当前真实状态（我自己复现的数字，非 TL 转述）

| 项 | 我复现的值 |
|---|---|
| 探针 | `PASSED=8 / 12`，`CALLED_CONTRACT_UNMET=0`，`CALL_FAILED=0`，`NOT_PROBED=4` |
| callable | `8`（8 个 PASSED 能力） |
| plan-compiler | `COMPILABLE`（exit=0），`nodes=9 (callable 8)` |
| 反事实 | `CONSUMPTION_PROVEN_LOGIC_ONLY`，变异 12/12 消费，明确"不得据此声称 §14.2 第 6 项达成" |
| 门禁套件 | `15/15 passed`（run_gates 逐项汇总，非首败即停） |
| §14.2 | 7 达成 / 1 部分（第 7 项 L4-1 接口）/ 1 不达成（第 6 项消费 trace） |
| KERT pytest | `28 passed` |

复现命令与 TL 声称的"8/12、COMPILABLE、15/15、7/1/1"完全一致。

---

## 六、是否同意 A 层收口

**同意 OC-04 在 A 层（定义验收）收口。**

理由：
1. 第一轮的三条指控**全部真实修复**，且经破坏性验证证实（非又一层的自我确认）：
   - 探针真实调用 KERT（破坏 schema_keys → PASSED 归零）；
   - 反事实强制读合同（删 OBL-07 → 变异减少）；
   - 编译门禁真会失败（破坏 callable → BLOCKED + exit=1）。
2. TL 完整披露了修复前的真实状态（探针 0、BLOCKED、14/15），并**额外发现并修复了第一轮 QA 未指出的更深缺陷**（KERT 对所有技能返回同一通用结构）。
3. B 层被**精确、显式**地标注为"未达成"，未用"部分达成"弱化，且有具体缺口清单与"不主张事项"清单。
4. 未发现"为通过而放宽校验、删除断言、调整阈值"的痕迹；相反，探针判定收紧、反事实结论主动降级。

**收口边界（必须一并成立）**：
- 仅 A 层收口；B 层（SIM 运行验收）**未达成**（§14.2 第 6 项无运行时 trace、第 7 项持久化未实现），C 层未开始。
- 两条**可改进项**（不阻塞 A 层收口，但建议 TL 记录）：
  1. §14.2 第 3 项"指标可复算"对 RATIO/DAYS 型指标仍是"求和"而非"按公式复算"，应在 A 层收口中补诚实限定；
  2. `make check`（run_gates）把 readiness 未达成也计入整体失败，将来 B 层 trace 缺失时可能倒逼"为让 make check 通过而把未达成改成达成"，需提前界定"诚实报告"与"门禁失败"的语义边界。

---

## 七、附：核验命令与原始输出

```bash
# 1. 锚点确认
cd /home/szf/dev/gits-cbanking && git rev-parse HEAD        # 8c8ec1c
cd /home/szf/dev/Leibniz-KERT && git rev-parse HEAD         # 0b7c83f

# 2. 复现探针 / 反事实 / 编译 / 门禁
python3 scripts/gk_ke_capability_probe.py
#   → PASSED=8 CALLED_CONTRACT_UNMET=0 CALL_FAILED=0 NOT_PROBED=4
python3 scripts/gk_ke_counterfactual_test.py
#   → CONSUMPTION_PROVEN_LOGIC_ONLY，变异 12/12，"不得据此声称 §14.2 第 6 项达成"
python3 scripts/gk_ke_plan_compiler.py; echo "exit=$?"
#   → COMPILABLE exit=0
python3 scripts/run_gates.py
#   → 15/15 passed

# 3. 破坏性验证 §四.3（破坏后恢复）
python3 -c "import json;d=json.load(open('specs/knowledge-architecture/registry/Capability.json'));[i.update(callable=False,probeStatus='NOT_PROBED') for i in d['items'] if i['capabilityId']=='SIM-CAP-FACT-RECON'];json.dump(d,open('specs/knowledge-architecture/registry/Capability.json','w'),ensure_ascii=False,indent=2)"
python3 scripts/gk_ke_plan_compiler.py; echo "exit=$?"
#   → BLOCKED exit=1（已还原）

# 4. 破坏性验证 §四.2（删 OBL-07 后恢复）
#   → 变异 12→11，证明合同被真实读取

# 5. 破坏性验证 §四.1（破坏 KERT schema_keys 后恢复）
#   cp src/kert/application/skills.py /tmp/skills.py.bak
#   注入：schema_keys 抽取恒为空
#   重跑探针 → PASSED=8 → 0（NOT_PROBED=12）
#   cp /tmp/skills.py.bak src/kert/application/skills.py  # 恢复，git diff 为空

# 6. 变异验证 §四.6（注入 svc=None 判 PASSED 后恢复）
#   → M0 断言正确转 FAIL

# 7. KERT 测试
cd /home/szf/dev/Leibniz-KERT && python3 -m pytest tests/integration/test_skills.py -q
#   → 28 passed
```

---

## 最终立场

**第一轮的否决是正确且有效的，TL 的修复是真实的、经破坏性验证证实的，而非又一层自我确认。**

TL 本轮的表现值得肯定：完整接受三条指控、诚实披露修复前真实状态（探针 0、BLOCKED）、**额外发现并修复了第一轮 QA 未指出的更深缺陷**（KERT 返回同一通用结构）、主动把反事实结论降级为 `LOGIC_ONLY` 并明确不得据此声称达成。未发现"为通过而放宽校验"的痕迹。

**因此：同意 OC-04 在 A 层收口，B 层明确未达成。** 附两条不阻塞收口的可改进项（指标复算的实质降级、readiness 门禁与"诚实报告"的语义边界）。
