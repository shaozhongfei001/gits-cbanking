# GK17 · W8 预做 PLAN（W8 正式开工前的未被阻塞项）

> 编写：`tech_lead`｜时间：`2026-09-16`｜BASE_HEAD：`71169042`
> 授权：Owner「推进 GK17」（承接 `NEXT_SESSION.md` §C「TL 拥有，未被阻塞的可在 W8 正式开工前预做」）
> 依据纪律：`docs/dispatch/GK17-ontology-unified-map-长程编排-V1.0.md` §0 并行读 + 串行写、
> `loops/GK17-ontology-unified-map/memory/NEXT_SESSION.md` §纪律四条

---

## 0. 本轮判定：瓶颈是"判定"，不是"实现"

`STATE.json` 与 `NEXT_SESSION.md` 一致：**W2 与 W6 均已交付、待 ACCEPT**，
而两者的判定权**都不在 TL 手上**（`ROLE_BOARD.yaml`：`independent_qa.status = unassigned_must_be_separate_session`）。

⇒ **本轮不做任何"代签"**。只做两类事：

| 类别 | 内容 | 是否被阻塞 |
|---|---|---|
| **A. 等待判定** | W2 / W6 的 ACCEPT；Q1–Q6 签署 | ❌ 阻塞（须独立 QA / Owner） |
| **B. W8 必办项预做** | 下 §1 的 WP8.0-a / -b / -c | ✅ 不被阻塞（TL 独占路径） |

---

## 1. 本轮工作包（W8 必办项的一条子集）

来源：`NEXT_SESSION.md` §C 的 6 条必办清单。本轮取其中**不依赖任何裁定**的 3 条。

| WP | 内容 | 独占路径 | 判据（可机械复核） |
|---|---|---|---|
| **WP8.0-a** | **D2 / D4 专门探针内置**到 `gk17_triple_consistency_check.py` 的变异自检（原仅在 TL 外部临时根执行过，未内置） | `scripts/gk17_triple_consistency_check.py` | ① 基线仍 PASS；② D2 探针使 D2 计数**严格增加**；③ D4 探针使 D4 计数**严格增加**；④ 交叉项不得被误触发；⑤ 真实投影文件**逐字节不变**；⑥ 恢复后回到基线 |
| **WP8.0-b** | **修命令口径不一致**：编排表 §WP5.3 与 `ROLE_BOARD.gate_owner.exclusive_paths` 写 `scripts/gk17_mutation_regression.py`（**实测不存在**），实际命令是 `scripts/gate_injection_tests.py` | `docs/dispatch/`、`loops/GK17-.../memory/ROLE_BOARD.yaml` | `git grep -n gk17_mutation_regression.py` ⇒ 0 命中（不含历史记录文件） |
| **WP8.0-c** | **为模块级门禁登记前置条件**（`~/.m2` 新鲜度 / 先 `install`；测试面用 `./mvnw test` 而非 `verify`） | `docs/dispatch/` | 编排表含可复制的"前置条件"节，且与 `FAILURES.md` `20260915T073300Z` 一致 |

**本轮明确不做**（保留给 W8 正式开工，理由见右）：

| 未做项 | 理由 |
|---|---|
| `run_gates.py` 登记 GK17 门禁（二选一） | 会改动 `make check` 的门禁数量，**外溢到其他 Loop / 执行者**，且 `LOOP.yaml.contract_check` 通过条件写作「22/23」需同步改文案 ⇒ 属**收口期协调变更**（Tick 10 已定：留 W8） |
| `frontend_test` / `backend_test` 两道环境红处置 | **须治理 / Owner 裁定**，TL 不擅改门禁构成 |
| 修 `ROLE_BOARD.yaml` 的角色 status / `baton.wave`（静默失真） | ✅ **本轮一并做**（属 §2 记忆保真，见下） |

---

## 2. 附带修正：Loop 记忆静默失真（与 W5/STATE 同族，TL 独占路径）

实测到的失真（2026-09-16）：

| # | 位置 | 现状 | 实际 | 危害 |
|---|---|---|---|---|
| 1 | `ROLE_BOARD.yaml` `baton.wave` | `"W0"` | W1/W5 已 ACCEPT、W2 已实现待 ACCEPT | 读表者以为还在 W0 |
| 2 | `ROLE_BOARD.yaml` `roles.*.status` | `waiting_on_W1` ×3 | W1 已 ACCEPT | 误判依赖未解锁 |
| 3 | `ROLE_BOARD.yaml` `gate_owner.exclusive_paths` | 含不存在的 `scripts/gk17_mutation_regression.py` | 实为 `scripts/gate_injection_tests.py` | 按表去找文件 ⇒ **全量假 FAIL**（同 `gits:Asset` 注释事故） |
| 4 | `STATE.json` `completed_gates` | `[]` | 10 项 implementation 门禁已落证 | 与 `current_phase` 矛盾 |
| 5 | `STATE.json` `wave_state.W6` | `in_progress` | W6 已交付待 ACCEPT（`gates_pending_wave` 未登记） | pending gate 未落 `EVIDENCE.json` |

> 纪律依据：Tick 14「**记录本身静默失真，比红更危险**」。
> 本轮**只修事实性失真**，**不**改任何 wave 的接受状态（ACCEPT 权不在 TL）。

---

## 3. WP8.0-a 设计（先设计后编码）

### 3.1 现状（实测）

`run_mutation_selftest()` 只对 **D1** 做变异：往本体**临时副本**追加
`gits:prod_cm_001 gits:requiresProduct gits:prod_set_001 .` ⇒ 要求 D1 计数增加。
**D2 / D4 无内置探针** —— 而本仓硬约束是「不做负例的门禁视为未完成」。

### 3.2 已知约束：**D4 当前"有能无力"**

`specs/knowledge-architecture/instances/product/products.ttl` 实测 115 行、13 个个体，
全部语句为 `a gits:Product` + `rdfs:label` / `rdfs:comment`（字面量）。
⇒ **对象引用 0 条** ⇒ 真实数据**触发不到 D4**。
（成因：产品卡 40 处引用 100% 悬空 ⇒ 按 WP1.3 裁定 fail-closed 产出 0 条关系实例。见 Tick 12 / `GK17-产品卡引用空间裁定-V1.0.md`。）

⇒ 探针**不能**依赖真实数据触发，必须在**内存中的投影副本**上注入。

### 3.3 探针设计（两条，各自独立归因）

| 探针 | 注入（追加到投影**副本文本**） | 期望 | 期望不触发 |
|---|---|---|---|
| **P-D2** | `gits:gk17_d2_probe a gits:GK17_NO_SUCH_CLASS_D2 .` | D2 计数 **+1** | D4 不变（`p == "type"` 被 D4 跳过） |
| **P-D4** | `gits:gk17_d4_probe gits:requiresProduct gits:gk17_no_such_individual .` | D4 计数 **+1** | D2 不变（无 `type` 语句）；D1 不变（注入在**投影**，D1 只看本体） |

**安全性**：
- 注入只存在于 **Python 字符串**，**不写任何文件**；
- 仍**额外**断言全部真实投影文件 sha256 未变（强于"没写文件"的声明）；
- 每个探针各自 `变异前 / 变异后 / 恢复` 三点对照，缺一即 FAIL。

### 3.4 诚实性设计（防空转 / 防假绿）

| 情形 | 处理 |
|---|---|
| 投影缺失 | `probed=false`，`reason=PROJECTION_ABSENT` ⇒ **不计入通过**（与既有 `--allow-empty-projection` 的 `SKIPPED` 口径一致，不新增行为） |
| 投影存在但探针未跑 | **FAIL**（硬约束：不做负例 = 未完成） |
| 探针跑通但计数**未增加** | **FAIL**（断言空转，宁红不假绿） |
| 交叉项被误触发 | **FAIL**（探针不精确 ⇒ 归因不可信） |

### 3.5 验收命令（原命令，不改一字）

```bash
python3 scripts/gk17_triple_consistency_check.py            # 期望 exit 0 / PASS
python3 scripts/gk17_triple_consistency_check.py --json     # 期望 见 mutation.projectionProbes 两条 probed=true
python3 scripts/gate_injection_tests.py                     # 期望 OK gk17-triple-consistency 仍在 OK 列表
```

---

## 4. 停止条件（沿用本 Loop 5 条，不新增）

缺凭据 / 需求冲突 / 方向性变更 / 自愈耗尽（同一门禁 5 次仍红）/ 安全隐患。

## 5. 非声明（本轮不做）

- **不**声称 W8 ACCEPT；**不**代表 `QA_PASS` / `PRODUCTION_READY`；
- **不**代签任何 Owner 决议；**不**把 `INCONCLUSIVE` 计入通过；
- **不**改 W2 / W6 的待 ACCEPT 状态；
- **不**改 `run_gates.py` 门禁构成、`LOOP.yaml` 门禁命令、封版制品。
