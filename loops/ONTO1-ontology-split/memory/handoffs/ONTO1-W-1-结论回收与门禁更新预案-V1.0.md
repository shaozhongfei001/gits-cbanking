# ONTO1｜复审结论回收与门禁更新预案 V1.0（三形态 24 小时动作清单）

> 本预案**不构成结论、不预设倾向**：它只回答"**收到委员会签署件后 24 小时内做什么**"。未收到签署件前，本预案不启动。
> 配套文件：《送审操作清单》V1.0（`ONTO1-W-1-SUBMIT-01`）——负责"把结论送出去"；本预案负责"把结论接回来并落门禁"。

| 项 | 值 |
|---|---|
| 文档编号 / 版本 | `ONTO1-W-1-VERDICT-01` / V1.0 |
| 编制角色 | `architect-review-liaison`（程序与文书；不含技术判断） |
| 日期 | 2026-09-20 |
| 触发条件 | TL 收到经秘书处汇总、且通过 §1 有效性判定的**已签署 `14-书面复审决议签署页.md`** |
| 未触发时状态 | `RETURN_TO_HLD` 有效；**Wave 0 及以后全部禁止**；预案不启动、不预支 |
| 授权边界 | 结论**只有委员会能给**；TL 只做「登记、传播、门禁落位」，**不得解释结论、不得拔高结论强度、不得替 Owner 签署** |
| 时钟定义 | 「24 小时」= 自 TL 收到汇总件起 **1 个工作日内**（与 `14` 末页「结论传出后 1 个工作日内」一致） |

---

## 0. 总则

1. **先受理、后动作**：任何状态更新都必须在 §1 判定为 `ACCEPTED` 之后。
2. **不升级**：`PASS_WITH_REQUIRED_CHANGES` 绝不写成 `DESIGN_APPROVED`；不得自创 `DESIGN_APPROVED_WITH_CONDITIONS` 之类中间态（状态词汇以 `LOOP.yaml.gate_state` 与执行计划 §0 为准）。
3. **方向认可 ≠ 文本核验**（复审意见 §二原话）：即便委员会再次书面认可整改方向，也不得据此自行解除 `RETURN_TO_HLD`。
4. **未闭合 ≠ 已关闭**：任何条件、依赖、豁免都不得被"改写状态"洗白（`WAIVED_FOR_DEVELOPMENT` 永不满足激活门禁）。

---

## 1. 受理与有效性判定（T+0~2h，fail-closed）

> **口径说明（2026-09-21）**：本预案现行 **V1~V9 共九项**——**V1~V7 为原七项**；**V8（评审独立性）与 V9（不得提前提升门禁）依 Owner 2026-09-21 最终决议第 4、6、7 条新增**，性质为**仅加严**（不放松任何原有检查）。

| # | 检查项 | 不通过 ⇒ |
|---|---|---|
| V1 | 决议 1 **恰好**勾选一项 | 未勾 / 多勾 ⇒ `INVALID_RETURN` |
| V2 | 选第 2 项 ⇒ `1a` 必要条件非空 | 空白 ⇒ `INVALID_RETURN` |
| V3 | 选第 3 项 ⇒ `1b` 退回理由非空且含**文件号/条款** | 空白 / 仅方向性表述 ⇒ `INVALID_RETURN` |
| V4 | 决议 4 选「有条件」⇒ 未关闭项表非空 | 空白 ⇒ `INVALID_RETURN` |
| V5 | 决议 5/6 选「要求修改/补充」⇒ 列明项非空 | 空白 ⇒ `INVALID_RETURN` |
| V6 | 签署表含 **主席 + 秘书处汇总人** 签字与日期 | 缺任一位 / 缺日期 ⇒ `INVALID_RETURN` |
| V7 | 知悉确认三项已勾 | 未勾 ⇒ 记 `OBSERVATION`（不阻断，要求补勾） |
| **V8** | **评审独立性**（Owner 2026-09-21 最终决议第 4、6 条）：六项技术结论是否由**具名评审组**（主席 / 本体语义架构 / 数据治理 / 集成架构）**分别确认**；Owner 是否**仅签自己对应的角色意见** | 由 Owner 预填/代勾、或仅 Owner 单方签署 ⇒ **不得**记 `ARCHITECTURE_COMMITTEE_APPROVED`，**只能**记 `OWNER_REVIEW`，并退回补正 |
| **V9** | **不得提前提升门禁**（第 7 条）：申请提升的理由须为**有效签署页 + V1~V8 全过**；自检通过 / `refalign exit=0` / Owner 发函**均不构成**理由 | 以非签署理由申请提升 ⇒ 拒绝并记 `OBSERVATION`（门禁零动作） |

- `ACCEPTED` ⇒ 进入 §2/§3/§4 对应形态；
- `INVALID_RETURN` ⇒ 退回秘书处补正，**门禁零动作**（`LOOP.yaml`/`STATE.json`/`NEXT_SESSION.md` 均不动），并在本 Loop `FAILURES.md` 记一条程序性记录（先记后办）。

**受理即归档**（三形态共同第一步）：
1. 归档至 `docs/review/ARCH-ONTO-2026-001_委员会书面复审决议_V1.0-<YYYYMMDD签署>.md`（或同名 `.pdf`）；
2. 计算 `sha256`，写 `loops/ONTO1-ontology-split/evidence/review-submission-verdict.json`；
3. 追加 `EVIDENCE.md`；**归档件此后只读**。

---

## 2. 形态 A：`DESIGN_APPROVED`（24h 动作）

| 时点 | 动作 | 落位 | 闭合判据 |
|---|---|---|---|
| T+0~2h | 受理 + 有效性判定 + 归档 + 哈希记账 | §1 | `ACCEPTED`；`review-submission-verdict.json` 存在 |
| T+2~4h | `gate_state.current = DESIGN_APPROVED`；`target` 闭合；`forbidden_now` 收敛为「跳过门禁 / 手改 `generated/` / 逾越 D1~D4 未决禁止动作」 | `LOOP.yaml` | 状态机位置与决议 1 勾选一致 |
| T+4~6h | 更新 `STATE.json.next_action`、`ROLE_BOARD.yaml.updated_at`、`NEXT_SESSION.md` | 四个状态载体 | `NEXT_SESSION` holder 与 `ROLE_BOARD.baton.holder` 一致（guard 硬校验） |
| T+6~10h | 状态机位置 + `G-1` 条件①判定 + 五态纪律不变 | `memory/ORCHESTRATOR.md §0/§2`、`SHARED_MEMORY.md §1` | 与执行计划 §0 表一致 |
| T+10~16h | 若决议 4/5/6 附条件 ⇒ 建条件台账 | `memory/CHANGE_REQUESTS.md` | 每条含「决议项 / 原文要求 / 责任角色 / 证据 / 闭合判据 / 阻塞波次 / 状态」 |
| T+16~24h | 通知全部角色；复跑 `make memory-check` + `make evidence-check`；向 Owner 报告「Wave 0 可开工」 | 通知记录 + 门禁日志 | 两门禁 PASS |

**Wave 许可判定（A 形态，批准 ≠ 各波都能开工）**

| 波次 | 是否可开工 | 仍需 |
|---|---|---|
| Wave 0（冻结与 Loop 骨架） | **可开工**（0.5~1d） | RI 锚点核对；失败即 STOP 写 `BLOCKED` |
| Wave 1（独立语义契约库） | **仍阻塞** | 公共语义 Owner + Integration Contract Owner 任命（`OWNER_REQUESTS.md §A`） |
| Wave 2（四层拆分） | **仍阻塞** | D3 签署（硬前置）；WI-A2 处置表（已达成） |
| Wave 3（双侧换消费） | **仍阻塞** | Wave 2 + D4 |
| Wave 4/5、G6 | **仍阻塞** | 前序波次 |

**A 形态禁止**：把 `DESIGN_APPROVED` 表述为实现完成 / QA 通过 / Owner 激活 / 生产可用（决议 3）；签发任何国标符合性表述或使用 `CONFORMANCE` 文件名（决议 2）。

---

## 3. 形态 B：`PASS_WITH_REQUIRED_CHANGES`（24h 动作）

| 时点 | 动作 | 落位 |
|---|---|---|
| T+0~2h | 受理 + 归档 + 哈希记账（同 §1） | §1 |
| T+2~4h | `gate_state.current = PASS_WITH_REQUIRED_CHANGES`（**不得**写 `DESIGN_APPROVED`） | `LOOP.yaml` |
| T+4~8h | 逐条登记必要条件（`1a` + 决议 4 未关闭项 + 决议 5/6 要求补充项） | `memory/CHANGE_REQUESTS.md` |
| T+8~12h | 判定 `G-1` 条件①：**满足**（执行计划 §2 明示「或 `PASS_WITH_REQUIRED_CHANGES` 且条件已登记」），但**按条件落点收紧波次** | `ORCHESTRATOR.md §2` |
| T+12~18h | 判定是否需**重发快照**（见下） | `docs/review/` + `MANIFEST.md` |
| T+18~24h | 通知全部角色；复跑 memory/evidence check；向 Owner 报告「可开工范围 + 未闭合条件」 | 通知记录 + 门禁日志 |

**条件台账最小字段**（`memory/CHANGE_REQUESTS.md`）：

| 序 | 决议项 / 原文要求 | 落点文件 | 责任角色 | 证据要求 | 闭合判据 | 阻塞波次 | 状态 |
|---|---|---|---|---|---|---|---|

**波次收紧规则**
- 条件**不涉及**设计内容 ⇒ Wave 0 可开工；
- 条件落到某波 ⇒ **该波不得开工**（例如条件要求补消费者扫描 ⇒ Wave 2/3 禁）；
- 涉及 D1（国标）⇒ 维持「已移出本次基线」，**禁止**恢复条款级对齐或符合性表述。

**重发快照判定（关键）**
- 条件触及 `01`~`14` 任一件内容 ⇒ 必须升 **V1.2** 送审包：重发快照 + 重算哈希 + `MANIFEST` 记版本沿革，并就差异再次送审（或按 Owner 裁定）；
- **禁止**直接改 `01`~`12` 后顺手改 MANIFEST 哈希 —— 门禁 `[R1]` 会 FAIL（这正是它存在的理由）；
- 条件不触及包内容（仅项目侧执行要求）⇒ 不升版，但须在 `MANIFEST.md` 记「条件登记沿革」指向 `CHANGE_REQUESTS.md`。

---

## 4. 形态 C：继续 `RETURN_TO_HLD`（24h 动作）

| 时点 | 动作 | 落位 |
|---|---|---|
| T+0~2h | 受理 + 归档 + 哈希记账（退回**也是正式结论**，必须记账） | §1 |
| T+2~4h | **先记后改**：追加 `FAIL-<日期>-NN｜书面复审退回`，含 `1b` 理由原文与指向的文件号/条款 | `FAILURES.md` |
| T+4~10h | 逐条把退回理由回源到 `文件:行`，形成「理由 → 证据 → 拟修订方式 → 证据要求」 | `memory/CHANGE_REQUESTS.md`（退回段） |
| T+10~14h | `gate_state` **保持** `RETURN_TO_HLD`；`forbidden_now` 一条不减 | `LOOP.yaml` |
| T+14~20h | 判定是否需重发快照（见下） | `docs/review/` |
| T+20~24h | 通知全部角色；复跑 memory/evidence check；向 Owner 报告「阻塞原因 + 最小解卡动作」 | 通知记录 + 门禁日志 |

**重发快照判定**
- 退回理由涉及 `01`~`12` 内容 ⇒ 升 `V1.2`：重发快照 + 重算哈希 + MANIFEST 版本沿革；
  **下一轮的送审函（13）与签署页（14）必须按新轮次更新**（轮次编号、前序文书、日期），**不得**原样复用被退回轮次的 13/14；
- 仅缺件/程序性问题（如缺附件、送达不完整）⇒ 跑 `python3 scripts/onto1_review_package_check.py --gate` 定位；补齐后原样再送，不升版，但须在 `MANIFEST.md` 记「程序性补正」；
- **无论哪种**：`RETURN_TO_HLD` 期间 Wave 0 及以后零动作；Wave -1 只读工作继续（WI-A3 跟催、WI-A2 残留回源、WI-A4/A5 待签署）。

---

## 5. 三形态对照速查

| 维度 | A `DESIGN_APPROVED` | B `PASS_WITH_REQUIRED_CHANGES` | C 继续退回 |
|---|---|---|---|
| `gate_state.current` | `DESIGN_APPROVED` | `PASS_WITH_REQUIRED_CHANGES` | `RETURN_TO_HLD`（**不变**） |
| Wave 0 | 可开工 | 可开工（条件不涉 Wave 0 时） | 禁 |
| Wave 1 | 待两名 Owner 任命 | 同 A（+ 条件闭合） | 禁 |
| Wave 2 / 3 | 待 D3 / D4 | 由条件落点决定 | 禁 |
| 需重发快照升 V1.2 | 仅当条件触及包内容 | 同 A | 视理由（内容类 ⇒ 是；程序类 ⇒ 否） |
| 计 `FAILURES.md` | 否 | 否（记 `CHANGE_REQUESTS.md`） | **是** |
| 条件台账 | 有（若附条件） | **必有** | 有（退回理由回源） |
| 24h 必做 | §6 五件 | §6 五件 + 条件台账 | §6 五件 + 退回理由回源 |

---

## 6. 全形态通用 24h 必做（五件，缺一不可）

1. **归档 + 记账**：签署件落 `docs/review/`，`sha256` 写 `evidence/review-submission-verdict.json` + `EVIDENCE.md`；
2. **四载体状态一致**：`LOOP.yaml.gate_state`、`STATE.json`、`ROLE_BOARD.yaml`、`NEXT_SESSION.md`（后两者 holder 必须一致，guard 硬校验）；
3. **通知全部角色**：Feature Pilot、独立 QA、公共语义 Owner、Integration Contract Owner、Knowledge/KERT Owner、GITS Owner、D1~D4 各决策方（清单见执行计划 §1）；
4. **门禁复跑**：`make memory-check LOOP=ONTO1-ontology-split` + `make evidence-check LOOP=ONTO1-ontology-split`，结果记 `EVIDENCE.md`；
5. **包漂移声明**：重跑 `python3 scripts/onto1_review_package_check.py --gate`；涉及包内容改动时必须升版重发（禁静默）。

---

## 7. 禁止清单（三形态通用，逐条可判）

- 不得代替委员会解释结论、不得拔高结论强度、不得自创状态词汇；
- 不得替 Owner 签署或补签任何栏位；
- **未收到签署件不得预支任何形态的动作**（含"先按 A 开工，等签了再补"这类变通）；
- 不得把签署件当"技术正确性证明"（委员会只对**提交物与状态**负责）；
- 不得因结论到达而取消 D1~D4 的「未决期间禁止动作」；
- 不得跳过「合同先行」（Wave 2 起：`CONTRACT_INDEX` 登记 → `make generate` → `make check`）；
- 不得手改 `generated/`；不得 `git add .`；
- 不得把 `WAIVED_FOR_DEVELOPMENT` / `NOT_EVALUATED` 当通过（五态纪律）。

---

## 8. 预案有效期与失效

| 项 | 值 |
|---|---|
| 生效 | 本预案落盘即生效（作为「收到后动作」的既定程序） |
| 失效/待命 | 若 **2026-10-09** 未收到任何回执 ⇒ 形态未定：仅执行「包未漂移」巡检 + 登记 `OVERDUE`，**不执行** §2/§3/§4 任一形态 |
| 修订 | 结论形态或组织流程变化 ⇒ 升 V1.1，并在 `MANIFEST.md`/`EVIDENCE.md` 记沿革 |
| 声明 | 本预案**不构成结论、不预设倾向**；它只回答"收到结论后 24 小时内做什么" |
