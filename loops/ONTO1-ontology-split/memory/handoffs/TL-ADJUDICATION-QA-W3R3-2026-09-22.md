# TL 裁定｜QA 第三轮（W3R3：定向覆盖 13 个未审仪器）结果处置

> 受理：全局 TL（`tech_lead`）｜2026-09-22
> 被裁对象：`memory/handoffs/INDEPENDENT-QA-W3R3-2026-09-22.md`
> **SHA-256 核验**：声明 `88481e7c0c1e28d0…` ↔ 实测 `88481e7c0c1e28d07bc5adb9767cf719adcd8d56f7cb939a62956628008e4067`（882 行）**逐字一致**
> **我方立场**：本轮 QA 报出的最重一条不是"某判据弱"，而是"**板面说的和仓里跑的不一样**"——按板面可信性问题处理，不按口径问题搪塞。

---

## 一、逐仪器裁定（13 个：6 HAS_DEAD_PATH + 7 SOUND）

| 仪器 | QA 结论 | TL 裁定 | 处置 |
|---|---|---|---|
| `onto1_cq_fixtures` | HAS_DEAD_PATH | **成立**（比转述更严重：不只失败路径不可达，还会**把破坏写回**） | **已修**（见 §三.1） |
| `onto1_d2_normalization_pack` | HAS_DEAD_PATH | **成立**（且连带 **S-1 板面事件**） | **已修**（见 §二、§三.2） |
| `onto1_namespace_collision_check` | HAS_DEAD_PATH（C-4b 恒不触发） | **成立** | **未修**，具名登记（见 §四） |
| `onto1_product_refs_probe` | HAS_DEAD_PATH（P1 死代码） | **成立** | **未修**，具名登记 |
| `onto1_check_strength_audit` | HAS_DEAD_PATH（main 全分支 return 0） | **成立**（且属**设计如此**，但未明说） | **已修**：新增 `--strict`（high 候选或未审仪器 ⇒ exit 2）；默认 0 保留并由 D-20 明示 |
| `onto1_pkg_audit` | HAS_DEAD_PATH（AU-5 恒红 + `recent_changes()` 恒 `[]`） | **成立** | **未修**，具名登记 |
| `attribution_rebuild` / `d4_pack` / `evidence_board` / `refalign` / `review_package` / `consumer_scan_tests` / `w15_acceptance` | SOUND | 采纳（失败路径可达） | 无 |

## 二、S-1（高，板面可信性）：机理、独立复现与修法

**事实**：`wi_a5_d2_pack` 在受理时**实测 FAIL（exit 2）**，而其 `--selftest` 也 FAIL；`EVIDENCE.json` 仍记 `pass`（板面 83/0/1）。

**我的独立复现（未采信转述）**：以 `out_dir=/tmp` 安全复跑 ⇒ `[G4] 回源位置校验：78 条，问题 5 ⇒ FAIL`，
5 条全部是 `…/products.ttl:<行>` 的 `line content mismatch`；期望内容在文件中的**真实行号**实测为
**58 / 23 / 38 / 13 / 68**，而源码锚点写的是 **60 / 25 / 40 / 15 / 70** ⇒ **恰好 +2 位移**，
与 C-2 修复重生成 `products.ttl`（该文件行数减少 2）一致。

**判据为何没兜住（设计缺口）**：`verify_ref()` 只做"精确行号 + 内容包含"校验，
一旦制品经**授权变更**重生成，锚点必然错位，且**没有任何位移告警机制** ⇒ 门禁静默变红、板面静默留绿。

**修法（两层，均已落地）**：
1. **锚点按实测更新**（58/23/38/13/68）；
2. **位移容忍必须可判据化**：精确行号不命中时，在文件内按内容搜索——
   **恰好唯一命中 ⇒ 记为位移并强制记账（gate 打印"位移已记账"）**；**0 命中（内容丢失）或 ≥2 命中（锚点歧义）⇒ 一律 FAIL**。
   ⇒ 既容忍授权重生成，又**不允许静默容忍**，且内容一旦真丢必红。

**复跑**：`gate` **rc=0（PASS）**、`--selftest` PASS。

**板面处置（关键）**：`EVIDENCE.json` 里那条 `pass` 是**修复前的旧记录**，当时不成立。
已按 **D-19** 以 revision 说明重记 `wi_a5_d2_pack`(+selftest)，并把本次事件记入 `FAILURES`。
**未**把它解释为 `PENDING_EXTERNAL_AUTHORITY`（与 `board_expression_rule` 一致：FAIL 不得换口径）。

## 三、6 条死路径：已修 3 条

### 3.1 `onto1_cq_fixtures`（**假绿 + 写回破坏**）
- **机理**：`gate()` 首行 `if write: write_fixtures(target)` —— **先按常量重生成 6 份夹具，再校验自己刚写出的内容**
  ⇒ Q1~Q5 五条失败路径**永不可达**；且盘上任何篡改会被**覆盖写回**（QA 两极端实验：盘上 33 条违规 ⇒ gate 仍 PASS 且写回）。
- **修法**：gate **默认只读盘**（`write=False`）；重生成改为**独立动作** `--build`；主入口接线 `gate(OUT_DIR, write=False)`。
- **新增反例（证明有牙）**：**M4** 盘上篡改 CQ2 状态 ⇒ gate 必须 FAIL（实测 `exit=2`）；**M5** gate 不得写回（篡改内容保持原样）。
- **复跑**：`--gate` PASS、`--selftest` PASS（含 M4/M5）。

### 3.2 `onto1_d2_normalization_pack` G8（自指恒真）
- **机理**：`ok8 = bool(pack["no_ruling_declaration"]) and "R-6" in json.dumps(pack)`——
  而 `"R-6"` 正出现在**第 1 合取项自己的文本**里（"不关闭 R-6 风险登记"）⇒ 第 2 项由第 1 项自证。
- **修法**：改为**结构断言**：声明 ≥40 字且含"不含裁定" + `prohibited_actions` 是列表且 ≥5 条且**其中一条含 R-6**。
- **复跑**：G8 PASS（明细打印声明字数与条目数，可核）。

### 3.3 `onto1_sim_projection`（门禁**不读盘**）
- **机理**：`run_checks(config, out, tmp)` 的 `out` 参数**从未被引用** ⇒ 门禁只校验"临时目录里刚生成的"，
  对**盘上发布的 SIM 制品**被篡改**无判别力**；G4 的两条合取项由 `build()` 常量派生（属声明一致性）。
- **修法**：新增 **G8 盘上制品与重新生成逐字节一致**（先实测：盘上制品与重新生成 sha256 相同、且无时间依赖 ⇒ 字节比较有效）；
  G4 在明细中**明确标注"声明一致性，不作独立事实证据"**。
- **有牙证明**：篡改副本实验 ⇒ 只有 G8 失败（`SIM_ARTIFACT_DRIFT`）⇒ 门禁真读盘。
- **复跑**：`--gate` **8/8 PASS**、`--selftest` PASS。
- **附带**：我一度把限定语写进**判据名**，破坏了该仪器 `--selftest` 的精确匹配（3/4）——**我引入的回归，已在同一轮内修掉**
  （判据名还原为 `G4`/`G8` + 自检期望改**前缀匹配**），此过程如实记录。

## 四、未修的 3 条（**具名登记，不冒充已修**）

| 仪器 | 缺陷 | 为何不即修 | 建议承接 |
|---|---|---|---|
| `onto1_namespace_collision_check` | **C-4b 死防线**：真实布局下 `freeze_subjects` 恒为 0（两"车"都在 `loops/**`）⇒ 唯一"载体自冻结"防线永不触发；QA 攻防实验：篡改制品 + 改钉值后 **C-4 转 PASS** | 修法涉及**"如何认定冻结"的设计决定**（是改检测口径、还是把无检测对象时判 `NOT_EVALUATED`），不即兴发明 | 下一任 holder 或 QA 复审；注意该门禁**本身已为 `inconclusive`** |
| `onto1_product_refs_probe` | P1 位于 `probe()` **抛错之后** ⇒ 死代码 | 需确认移动后不改变退出语义（小修） | 下一批机械修 |
| `onto1_pkg_audit` | **AU-5 恒红**（"Owner 已授权 SIM 整改"状态下 2 findings/exit 2，无授权维/时间维）；`recent_changes()` 恒 `return []` | 需引入**授权维**（授权引用台账）与**时间窗**口径，属工具设计变更 | 需 Owner 决定口径后再改 |

## 五、观察项 5 与问题 6 的处置

- **`c2_generator_check.py:57 G0`**：QA 判为 **fail-closed 具名出口且可达**（配置缺失 rc=3 实测）⇒ **不是死路径**，
  是我自审仪的**误报**（分支豁免漏 `If.body`）⇒ **已修审器**（候选 15→14，误报消除）。
- **`sim_projection.py:142 G4`**：QA 判"两条合取项由常量恒真、等价于读自我声明"⇒ 采纳，**已标注其性质**；`out` 未读问题见 §三.3。
- **审器 v2 的覆盖复核**：QA 逐字复现 `226/15/13`；2 元组 / 3 元组 / 列表内 dict / 预计算变量**确被抽到**；
  但**下标赋值 dict**（`report["checks"]["C-1b"] = {...}`）与 **`failures.append("字符串")`** 仍**未作为判据被审**
  ⇒ 属**第二类覆盖缺口**，与既有的 13 个 `NOT_AUDITED` 并列，**如实计入未覆盖**。

## 六、记录与红线（受理后）

```
重记：wi_a5_d2_pack(+st) · wi_a6_cq_fixtures(+st) · wi_d2_sim_projection(+st)  —— 全部**开新纪元**重记并 exit 0（D-19）
板面：84 = 83 pass / 1 PENDING_EXTERNAL_AUTHORITY（不变；唯一非 pass = wi_a4_namespace_collision，C-1b 待 D3）
角色板：qa-w3r3 已登记入 parallel_allowed（QA 请求，属 TL 写域）
QA 报告：受理前后哈希一致（未改一个字节）
红线：generated/ 0 改动 · 基线 T-Box 未动 · KERT 近 1 日写入 0 · 未记 QA_PASS · 未代签 · 未把 FAIL 换口径
```

## 七、遗留清单（具名）

1. **未修 3 条**：C-4b 死防线 · P1 死代码 · AU-5 恒红（见 §四）；
2. **覆盖缺口两类**：13 个 `NOT_AUDITED`（违规清单/退出码形态）+ 审器未识别的两种形态（下标赋值 dict / `failures.append("字符串")`）；
3. **自审仪不登记为门禁**（D-20 不变）；批次纪律继续：仪器改动必须附自审结果（本轮已附，`--strict` 可作批次入口）。
