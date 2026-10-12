# ONTO1｜W-1.5 派工记录（TL → 多角色）

| 项 | 值 |
|---|---|
| 批次 | **W-1.5 就绪加固**（只读分析 + 门禁加固；**不进 Wave 0**） |
| 派工时间 | 2026-09-20（team `onto1-w15`） |
| 调度规程 | `memory/W-1.5-ORCHESTRATION.md` |
| TL | `main`（编排、裁定、门禁记账、审计、Baton） |
| 当前门禁 | `RETURN_TO_HLD`（有效）→ 本批次不改变门禁位置 |

## 1. 派工表

| PKG | 成员 | 模式 | 目标 | 写域（**不重叠**） | 登记建议（由 TL 执行记账） |
|---|---|---|---|---|---|
| **PKG-A1** | `pilot-a1` | acceptEdits | 1052 行候选义务 → 真义务/同名/待判 三层收敛 | `scripts/onto1_obligation_triage.py`、`evidence/obligation-*`、`evidence/PKG-A1-*` | `wi_a2_obligation_triage`(+`_selftest`) |
| **PKG-A2** | `pilot-a2` | acceptEdits | Wave 0 输入锚点预检门禁化（R1~R8） | `scripts/onto1_wave0_readiness.py`、`evidence/wave0-readiness-*` | `wi_a2_wave0_readiness`(+`_selftest`)，**当前期望 fail**（R6/R7 未满足） |
| **PKG-A3** | `pilot-a3` | acceptEdits | D-2（C-4 收窄）/ F2（头部自述不一致）/ D-3（放行规则陈述行） | 两个既有门禁脚本、`evidence/a3fix-*` | 复用 `wi_a4_namespace_collision`、`wi_a3_reference_alignment`（重跑） |
| **AUDIT** | `qa-w15` | acceptEdits（**只写 1 个报告文件**） | 独立审计三包：复算 + 回源抽样 + 反例构造 + 红线扫描 | `memory/handoffs/INDEPENDENT-QA-W15-*.md` | **不得签 QA_PASS** |

**权界重申**：TL 单写者文件（`LOOP.yaml`/`EVIDENCE.json`/`EVIDENCE.md`/`STATE.json`/`FAILURES.md`/`memory/{ROLE_BOARD,NEXT_SESSION,ORCHESTRATOR,PLAN-NEXT,INDEX_BASIS,TL-DECISIONS-*}`）**只有 TL 能写**；pilot 只提交"登记建议"。

## 2. TL 审计排程（每个 PKG 交回后执行 AU-1~AU-7）

| 序 | 动作 | 工具/命令 | 判据 |
|---|---|---|---|
| AU-1 | 交付物存在性 + 哈希 | `python3 scripts/onto1_pkg_audit.py --pkg PKG-A<n>` | 声明的每个路径存在且哈希一致（接受 `path @ hash` 与表格两种形态） |
| **AU-1b** | **Loop 记录里"声明的哈希" vs 实测**（F-2 类别，原 AU-1 会漏过） | `python3 scripts/onto1_pkg_audit.py --declared` | 声明哈希与实测不符 ⇒ 判 finding（已实测有牙齿：注入 `.ttl` 错误声明 ⇒ `mismatch=1`） |
| **AU-5m** | **mtime 兜底**（`loops/ONTO1-ontology-split/` 整体未跟踪 ⇒ `git status` 看不见逐文件改动） | `python3 scripts/onto1_pkg_audit.py --recent <分钟>` | 列出窗口内被改文件，人工比对写域表 |
| AU-2 | **复跑门禁**（不采信 pilot 日志） | TL 亲自执行 pilot 声明的 `--gate` / `--selftest`（**执行前先人工审阅命令文本**） | exit 与声明一致 |
| AU-3 | 回源抽样 ≥3 条 | TL 手工核对 `文件:行` | 1 条不成立 ⇒ 退回 |
| AU-4 | 变异有效性复核 ≥1 条 | 手工注入 ⇒ FAIL / 恢复 ⇒ PASS | 不成立 ⇒ 退回 |
| AU-5 | 红线扫描 | `onto1_pkg_audit.py --redlines` + `git status --porcelain` | 写域外零改动、KERT 零写入 |
| AU-6 | 记账 | `scripts/record_gate.py`（**按真实退出码**）+ `loop_guard` + `onto1_evidence_board_check` | 板面一致、孤儿日志 0 |
| AU-7 | 落盘 | `memory/handoffs/TL-AUDIT-W15-<PKG>.md`；不通过 ⇒ **先记 `FAILURES.md`** | 审计结论可复核 |

**退回机制**：同一 PKG 退回 ≥2 次 ⇒ TL 接管并写 `memory/BLOCKED.md`。

## 3. 已知排程缺陷（TL 主动登记，不隐瞒）

| # | 缺陷 | 影响 | 处置 |
|---|---|---|---|
| S-1 | `qa-w15` 与三个 pilot **同时启动** ⇒ QA 很可能在 pilot 交回前就出报告 | QA 首轮结论大概率是 `NOT_ACCEPTED（产物未就绪）` | **pilot 全部交回后由 TL 重新派 QA 复核**（同一成员重跑，或另派），首轮报告保留作审计轨迹 |
| S-2 | 三 pilot 并行写 script 文件，若都改 `evidence/` 下同名文件会冲突 | 写域已按前缀隔离（`obligation-*` / `wave0-readiness-*` / `a3fix-*`） | 已缓解；TL 在 AU-5 复核 |
| S-3 | PKG-A3 要先改 `scripts/onto1_namespace_collision_check.py`，而该脚本的门禁当前为 `fail` | 改后**仍应 fail**（C-2 未修）；若改后转绿 ⇒ 说明断言被放松 ⇒ **判 NOT_ACCEPTED** | 写入 AU 判据（见下） |

**AU 判据补充（A3 专用）**：`wi_a4_namespace_collision` 改动后**必须仍 exit=2**；若转 0 ⇒ 直接判 `NOT_ACCEPTED` 并记 `FAILURES.md`（因为唯一能让它转绿的前提是 C-2 两处真实冲突被修，而那属 Wave 3）。

**S-4（TL 派工单缺陷，由 D-10 认定）**：PKG-A2 派工单写"单改 R7 ⇒ `--gate` 转 PASS"。该要求隐含"单锚点满足 ⇒ 全项满足"的**错误前提**；pilot 拒绝照做（照做必须摘除 R6 = 拆红灯），改实现 M3a/M3b/M3c 分解断言。**TL 接受偏离并认定原派工单该条为缺陷**。流程修正已写入 `memory/W-1.5-ORCHESTRATION.md` §5 末。

## 3.1 审核进度

| PKG | 审核结论 | 板面变化 | 审计报告 |
|---|---|---|---|
| PKG-A2 | **ACCEPT_WITH_CONDITIONS**（D-9/D-10 + 3 项触发动作 T-1~T-3） | +2 门禁（均 pass）⇒ 28 门禁 = 27 pass / 1 fail | `memory/handoffs/TL-AUDIT-W15-PKG-A2.md` |
| PKG-A3 | **NOT_ACCEPTED（退回，7 条条件）→ 预验 C1~C4 已到位**（仪器 `wi_w15_a3_acceptance` **8/8** @ `collision=8c18b5b3` / `refalign=4d706978`）；**C5~C7 未完成**（计数口径 / M12 夹具确认 / 冻结复交 + 日志自证 revision + 回执表）⇒ **记账条件仍未满足**，两个既有门禁的登记证据仍属陈旧 | **+1 门禁**（`wi_w15_a3_acceptance` pass）⇒ 板面 **31 = 30 pass / 1 fail** | `memory/handoffs/TL-AUDIT-W15-PKG-A3.md`（§10 追加预验） |
| PKG-A1 | **ACCEPT**（AU-1 哈希逐字相符且冻结稳定；AU-2 双绿；AU-3 回源抽样通过；AU-4 TL 自建 MU-1~MU-3 全被具名拦下、还原后 CSV 哈希逐字回到 `81e5ebc4`）；4 项裁定 I-1/I-2/I-6/阈值 | 见右 | `memory/handoffs/TL-AUDIT-W15-PKG-A1.md` |
| **PKG-A1b** | **已完成（TL 代实现，`pilot-a1` 已下线 ⇒ 角色偏离已登记）**：I-6 升格 65 行 ⇒ **真义务 691 / 待回源 361**（`W3_CONSUMER_SWITCH` 381）；`--gate` 0 · `--selftest` **14/14**（M9 断言随裁定更新 + D-12 反例 M9b-1 回退 / M9b-2 弱面剥证据 / **M9b-3 全 P0 改包名 ⇒ 命中数 == 行数**）；新哈希 脚本 `a2be4df3` / CSV `58671a90` / summary `346f057a` / 报告 `28f4d74b`。**⚠️ 经 QA 第三轮判 BLOCKER 后修复**：原先"标签二次校验"是**死代码**（覆盖 0/65），且 TL 报告中曾据其作**不实表述** ⇒ `W15TL-09`；该块已移入循环并加 M9b-3 回归（退化复现 ⇒ FAIL，修复 ⇒ PASS） | **重跑重记 A1 两门禁**（板面仍 31 = 30 pass / 1 fail） | `memory/handoffs/TL-AUDIT-W15-PKG-A1.md` §8 |

## 4. 批次出口（与 `W-1.5-ORCHESTRATION.md` §6 一致）

1. 三包通过 TL 审计；2. 板面无**新增未说明** fail（A3 保留 C-2 的真实 fail 属预期）；3. `NEXT_SESSION.md`/`ORCHESTRATOR.md §7` 更新；4. A1 若真义务暴增 ⇒ 回写 `evidence/WBS-RESTIMATE.md`；5. QA 复核报告落盘（**不记 QA_PASS**）。
