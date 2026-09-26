# TL 审计报告｜W-1.5 PKG-A2（Wave 0 就绪预检门禁化）

| 项 | 值 |
|---|---|
| 审计人 | 全局 Tech Lead（main） |
| 被审包 | PKG-A2 / `pilot-a2` |
| 审计时间 | 2026-09-20T23:40Z |
| 审计规格 | `memory/W-1.5-ORCHESTRATION.md` §4（AU-1~AU-7） |
| **结论** | **ACCEPT_WITH_CONDITIONS**（交付成立；2 项后续触发动作 + 1 项裁定被采纳为流程修正） |

---

## 1. AU-1 交付物存在性 + 哈希

| 项 | 结果 |
|---|---|
| 仪器 | `python3 scripts/onto1_pkg_audit.py --pkg PKG-A2` |
| 首轮 | **NOT_ACCEPTED** —— 但根因是**TL 仪器口径过窄**（只认 `path @ hash`，不认 handoff 的表格形态）⇒ 记 `FAILURES.md` **FAIL-2026-09-20-09**（TL 自伤），修仪器后复跑 |
| 复跑 | `declared=2 failures=0` ⇒ **ACCEPTED**（脚本 `285bada3…`、`wave0-readiness-gate.json` `0c6b7498…` 与实际一致） |
| 未给哈希的交付物 | PLAN/ITER/HANDOFF 三件流程文档标 `—` —— **可接受**（非制品类）；仪器规则已相应写明 |

## 2. AU-2 复跑门禁（TL 亲自执行，不采信 pilot 日志）

| 模式 | TL 实测 exit | pilot 声明 | 一致 |
|---|---|---|---|
| `--gate` | **2** | 2（期望 fail） | ✅ |
| `--precheck` | **0** | 0 | ✅ |
| `--selftest` | **0** | 0 | ✅ |

**命令安全性审阅**（执行前）：`rg 'subprocess|os.system|eval|exec|__import__'` ⇒ **无命中**；唯一写路径为 `--report <path>`。⇒ 可安全执行。

## 3. AU-3 独立回源抽样（TL 自算，不经过 pilot 脚本）

| # | pilot 结论 | TL 独立复算 | 判定 |
|---|---|---|---|
| 1 | R2 基线 `705578d6324abd0c…`，计数 32/34/1 | `sha256=705578d6324abd0c`；rdflib `32 34 1` | ✅ 成立 |
| 2 | R3 归属矩阵 87 行，39 OWL/1 SKOS/5 Schema = 45 | 逐列复算：`87 / 39 / 1 / 5 / 合计 45` | ✅ 成立 |
| 3 | R4 `obligations=1052` 且 `PENDING_TRIAGE=0` | `summary 1406 行 / PENDING_TRIAGE 计 0`；`obligations 1052 行` | ✅ 成立 |
| 4 | R5 ADR 未预填根域、占位仍在 | 正则 `NS-L[1-4]\s*[:=]\s*https?://` ⇒ 无命中；`{NS-L1}` 出现 1 次 | ✅ 成立 |
| 5 | R8 `baseline_commit=71169042…` | 读取实值一致 | ✅ 成立 |

**抽样结论**：5/5 成立，**未发现不成立项**。

## 4. AU-4 变异有效性复核（独立沙箱，不碰仓库）

在 `/tmp/a2root` 复制脚本与锚点副本后独立注入：

| 变异 | 期望 | 实测 |
|---|---|---|
| M-A 沙箱对照 | `--precheck` exit 0 | exit **0** ✅（证明副本忠实） |
| M-B 向基线 TTL 追加一字节 | R2 `NOT_READY` + precheck FAIL | `R2 NOT_READY(sha256 prefix drift: 6e0e69da… != 705578d6…)`，exit **2** ✅ |
| M-C 篡改 MANIFEST 中 01 的哈希 | R1 `NOT_READY` + precheck FAIL | `R1 NOT_READY(MANIFEST drift: DRIFT=['01-…(d2c16784!=00000000)'])`，exit **2** ✅ |
| M-D 未恢复即复跑 | 仍 exit 2 | **2** ✅（无自动"自愈"假象） |

⇒ **断言有牙齿且 fail-closed**；非空转。

## 5. AU-5 红线扫描

| 项 | 结果 |
|---|---|
| 受控制品（`specs/**`/`generated/**`/`docs/dd/**`） | **零改动** |
| TL 单写者文件是否被 pilot 写 | **否**；pilot 亦如实说明窗口内 `STATE.json`/`ROLE_BOARD.yaml` 的改动是 **TL 并发写入**（与我方操作时间吻合，采信） |
| KERT 仓 | 无本包写入（既有 3 文件问题为 **D-7**，与本包无关） |

## 6. AU-6 记账

| 门禁 | 命令 | 实测 exit | 记录状态 |
|---|---|---|---|
| `wi_a2_wave0_readiness_precheck` | `… --precheck` | 0 | **pass** |
| `wi_a2_wave0_readiness_selftest` | `… --selftest` | 0 | **pass** |
| `wi_a2_wave0_readiness`（`--gate`） | `… --gate` | **2** | **未登记**（见 §7 D-9） |

记账后板面：**28 门禁 = 27 pass / 1 fail**（唯一 fail 仍为 `wi_a4_namespace_collision`）；孤儿证据日志 0；`loop-guard` PASS。

## 7. TL 裁定

### D-9｜`--gate` **不登记**为 Loop 门禁，改为 **G-1 触发义务**

- **裁定**：登记 `--precheck`（等待期回归门禁）与 `--selftest`；**`--gate` 暂不登记**。
- **理由**：`--gate` 的语义是"**G-1 是否已满足**"——一个**外部前提**，不是回归断言。在 G-1 前它**必然** exit 2（R6 D3 未签 / R7 gate_state 仍在 `RETURN_TO_HLD`）。若登记，板面会出现一个持续数周、**无回归价值**的常红项 ⇒ 诱发"红灯疲劳"（红项一多，真红项被忽略）。且按 **D-1**，`fail` 必须附"具名修复动作 + 责任 Wave"，而本项的"修复"是**外部签署**，会把"预期待满足"误报成"缺陷待修"。
- **诚实性保证（不隐藏红灯）**：`--gate` 当前 exit 2 及其**唯二** NOT_READY（R6/R7）已在 ① 本审计报告 ② `evidence/wave0-readiness-gate.json` ③ `EVIDENCE.md` 声明区 ④ `NEXT_SESSION.md` ⑤ `PLAN-NEXT.md` 五处显式登记。
- **触发义务（写进预案）**：**G-1 达成后 24 小时内**必须 ① 跑 `--gate` 并确认 exit 0；② 登记 `wi_a2_wave0_readiness`；③ 把 `--precheck` 的语义更新为"全项"或标注为冗余。
- **被否决的替代方案**（留痕）：用 `--precheck` 冒充 `--gate` —— **明确禁止**（pilot 亦主动拒绝该路径，判断正确）。

### D-10｜接受 pilot 对派工单的偏离（M3 拆分），并承认**派工单本身有缺陷**

- pilot 未按派工单字面"单改 R7 ⇒ `--gate` 转 PASS"实现，改为 **M3a（仅改 R7 ⇒ R6 仍拦）/ M3b（仅造 D3 签署件 ⇒ R7 仍拦）/ M3c（R6+R7 齐备 ⇒ 全项 READY ⇒ PASS）** 三条分解断言，理由是"字面实现必须把 R6 从全项判据中摘除 = 拆红灯"。
- **TL 裁定：接受，并认定原派工单该条为缺陷**（记 `DISPATCH-W-1.5.md` **S-4**）。
  **理由**：我原要求隐含了"单锚点满足 ⇒ 全项满足"的错误前提；**多锚点门禁的正确变异设计是"每个锚点各自独立有牙齿" + "条件齐备时可转绿"**，pilot 的分解恰好覆盖这两点，比我原来的字面要求更强（M3c 证明门禁**非永久红**）。
- **流程修正**：`W-1.5-ORCHESTRATION.md` 增补一条——**派工单若给出具体变异设计，必须经 pilot 反查"该变异是否与门禁语义自洽"；不自洽时 pilot 应拒绝照做并回报，而非拆断言**。

## 8. 后续触发动作（condition，非缺陷）

| # | 触发 | 动作 | 责任 |
|---|---|---|---|
| T-1 | **D3 签署** | R5 判据翻转为"签署件存在 **且** 根域已填 **且** 非占位值"（现行判据届时会误报 NOT_READY）；同步**回填 `D3_SIGNED_PATTERNS`**（实际签署件命名可能与先验枚举不同 ⇒ 否则 fail-closed 误红） | TL + 语义架构 Owner |
| T-2 | **G-1 达成** | 见 D-9 触发义务（跑 `--gate`、登记门禁、更新 precheck 语义） | TL |
| T-3 | R6/R7 之外出现 NOT_READY | 视为**真实漂移**，按 `FAILURES.md` 记录并阻断 Wave 0 启动 | TL |

## 9. 非声明

- 本报告**不构成 `QA_PASS`**（Loop 仍有已知 fail，`ready_for_independent_qa` 未满足）；独立复核由 `qa-w15` 另出报告。
- 本报告**未**验证 PKG-A2 之外的任何包；未对 Wave 0 是否应启动作判断（那取决于 G-1）。
- 本报告的 TL 自算结果（AU-3/AU-4）为 **TL 复核**，不是独立第三方复核。
