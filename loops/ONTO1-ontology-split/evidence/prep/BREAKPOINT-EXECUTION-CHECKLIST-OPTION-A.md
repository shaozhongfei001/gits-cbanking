# 四条断点｜**出口 A 收口清单**（先清单后执行；**逐断点签字后方可开工**）

> 依据：Owner 指示「**按建议办**」（2026-09-21）＝ 出口 **A × 4** + **要求"先出逐文件清单再执行"**。
> 编制：全局 TL｜**本文件不构成执行授权**：须 Owner 在 §3 逐断点签字后，实现者方可开工。
> 口径权威：`evidence/prep/breakpoint-option-comparison.json`（演练实测）· `breakpoint-execution-pack/README.md`（文件数）· `consumer-scan-hits.jsonl`（逐处命中）。

---

## 1. 先声明三套口径（**并列，勿混用**；差异来源见 `FAIL-2026-09-21-W15TL-21`）

| 口径 | 含义 | 数值 | 用在哪 |
|---|---|---|---|
| ① **待改文件数** | 排除"扫描器自身产物 / 工具配置"后的文件数 | **802** = 281+100+355+66 | **执行范围**（全量 CSV 行数与此一致） |
| ② **待确认命中（消费者面）** | 同①口径下的逐处命中 | **2509** = 675+288+1398+148 | 工作量的"上限估计"（含须排除的相邻名） |
| ③ **沙箱演练实改** | 在沙箱样本上**真跑**出口 A 后实际改写处数 | **549** = 187+157+93+112，**脏值 0**，相邻名保持 **True** | 证明出口 A **可执行且不污染相邻名** |

> 另有"原始扫描"口径（未排除扫描器自产/工具配置）见 `sim-rehearsal-report.json.consumer_hits_exact`，
> **不用于执行**，仅备溯源。**执行与验收一律以①②③为准。**

## 2. 逐断点事实（全部机读可复算）

| 断点 | 旧 ⇒ 新 | 受限配方 | 必须排除的相邻名（完整） | 文件 | 命中② | 演练实改③ |
|---|---|---|---|---|---|---|
| **B-1** | `Customer` ⇒ `CustomerRole` | `(?<![A-Za-z0-9_])Customer(?![A-Za-z0-9_])` | `customerId` · `gateOfCustomer` · `ofCustomer` · `opportunityOfCustomer` · `profileOfCustomer` · `refersToCustomer` | **281** | 675 | 187 |
| **B-2** | `Product` ⇒ `ProductOffering` | `(?<![A-Za-z0-9_])Product(?![A-Za-z0-9_])` | `ProductKnowledgeCard` · `ProductKnowledgeVersion` · `cardOfProduct` · `complementsProduct` · `opportunityForProduct` · `requiresProduct` · `versionOfProduct` | **100** | 288 | 157 |
| **B-3** | `Skill` ⇒ `SkillDefinition` | `(?<![A-Za-z0-9_])Skill(?![A-Za-z0-9_])` | `referencesSkill` | **355** | 1398 | 93 |
| **B-4** | `Asset` ⇒ `AssetDefinition` | `(?<![A-Za-z0-9_])Asset(?![A-Za-z0-9_])` | `ASSET` · `referencesAsset` | **66** | 148 | 112 |

**全量逐文件清单（含逐条签字位）**——执行时**以此为准**（MD 执行包只嵌前 40 行，仅属摘要）：

- `breakpoint-execution-pack/A/B-1-Customer-option-A-FULL.csv`（281 行）
- `breakpoint-execution-pack/A/B-2-Product-option-A-FULL.csv`（100 行）
- `breakpoint-execution-pack/A/B-3-Skill-option-A-FULL.csv`（355 行）
- `breakpoint-execution-pack/A/B-4-Asset-option-A-FULL.csv`（66 行）

> CSV 列：`# / file / hits / action / 受限配方 / 已核（签字）/ 日期`。`action` 对 `generated/**` 一律标注
> **"随 make generate 重生成（禁手改）"**，其余为"受限改名（逐处）"。

## 3. 签字位（**缺签即不得开工**）

```
B-1  Customer ⇒ CustomerRole      [ ] 清单已核，准予执行      签字：__________ 日期：______
B-2  Product  ⇒ ProductOffering   [ ] 清单已核，准予执行      签字：__________ 日期：______
B-3  Skill    ⇒ SkillDefinition   [ ] 清单已核，准予执行      签字：__________ 日期：______
B-4  Asset    ⇒ AssetDefinition   [ ] 清单已核，准予执行      签字：__________ 日期：______

[ ] 我要求：执行前**先提交**全量 CSV 的"待确认行"（hits ≥ 阈值的文件）由我二次确认
    阈值：______（留空＝默认 0，即全量逐条）
```

## 4. 执行顺序（**建议**，先小后大以验证流程与守卫）

```
B-2 (100 文件) → B-4 (66 文件) → B-1 (281 文件) → B-3 (355 文件)
```

**理由**：先用 **B-4（66 文件、112 处）** 与 **B-2（100 文件、157 处）** 跑通全链路（改名 → `make generate` → 守卫 → 记账），
再上 B-1/B-3 两个大断点；**B-3 的 `Skill` 是高歧义名（1398 命中、排除清单仅 1 项）⇒ 放最后**，此时流程已验证。

> 若你要求"一次只做一个断点、做完报你再做下一个"，也请在此勾选：
> `[ ] 逐断点串行，每完成一个断点停下报我` `[ ] 允许按上述顺序连续执行`

## 5. 前置（开工前必须为绿；任一未绿即不得开工）

| # | 前置 | 判据 |
|---|---|---|
| 1 | 基线冻结 | `specs/semantic/gits-core.owl.ttl` = `705578d6324abd0c…`（未动） |
| 2 | 沙箱结论在册 | `breakpoint-option-comparison.json` `option_A.dirty_values = 0` 且 `adjacent_preserved = true`（4/4） |
| 3 | `generated/` 禁手改 | 执行中**只**通过 `make generate` 触达 `generated/**`（`git status -- generated/` 执行前须为 0） |
| 4 | 全量清单已出 | 4 份 `*-option-A-FULL.csv` 均存在且行数 = 281/100/355/66 |
| 5 | 守卫基线绿 | `loop_guard` · `onto1_evidence_board_check --gate` · `onto1_reference_alignment_check --gate` · `make memory-check` · `make evidence-check` 全 PASS |

## 6. 后置（**每断点完成即做**，不得攒到最后）

1. `make generate` 重生成 `generated/**`，**不得手改**；
2. 跑 §5 第 5 行的全部守卫；
3. 更新 `evidence/prep/migration-worklist.csv` 对应条目的 `handling` 状态（由"须显式清单后再改"→ 已执行）；
4. **逐断点记账**（`record_gate`），并在全量 CSV 内逐行补签字与日期；
5. 若任一守卫红 ⇒ **立即停止后续断点**，不得"先改完再修"。

## 7. 禁项（**出口 A 的硬边界**）

- **禁批处理**：必须逐文件、逐处按受限配方改名（这是出口 A 与"盲替换"的唯一区别）；
- **禁** `equivalentClass` / `equivalentProperty`（D-16 口径，任何出口下都禁）；
- **禁**把本清单当作"已授权"——**无 §3 签字即不得开工**；
- **禁**在本轮顺手做 B/C 出口的任何事（三出口互斥，不得混用）；
- **未签字的断点**：涉及该术语的 Wave 2/3 项**不得开工**。

**边界**：本文件由 TL 编制，**不代表 Owner 已选出口**；出口选择权在 Owner / PSO / 数据 Owner。
