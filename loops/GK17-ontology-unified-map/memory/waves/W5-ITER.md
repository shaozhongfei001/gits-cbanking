# W5｜ITER 记录

## ITER 1｜WP5.1 / WP5.2 / WP5.3-前置（2026-09-15）

### 并发执行

| 写者 | WP | 独占文件 | 纪律 |
|---|---|---|---|
| `w5-ref-anchor` | WP5.1 | `scripts/gk17_ref_anchor_check.py` | 禁跑 make/run_gates/mvn、禁 commit（已遵守：`git status` 仅 `??`，无 M/A） |
| `w5-triple-consistency` | WP5.2 | `scripts/gk17_triple_consistency_check.py` | 同上 |
| `tech_lead` | 门禁执行 + 验证 | — | **串行**执行，不采信作者自述 |

### WP5.1 `ref_anchor_check` = **PASS** ✅

覆盖 **7 个 ID 空间**、4 张地图。锚点一律**复用既有权威**（未另造第二套定义）：

| ID 空间 | 锚点来源（权威） | 数量 |
|---|---|---|
| `KM-*` | `maps/**/*.md` 的 `mapId` | 4 |
| `KD-*` | 资产 manifest 的 `domain` ∪ 各图 `domains[].domainId` | 3 |
| `ASSET-*` | `assets/**/*.md` front matter 的 `assetId` | **21** |
| `SP-*` | `skills/*.json` 的 `skillId` | 5 |
| `AC-*` | `activations/*.json` 的 `contractId` | 3 |
| `RP-*` | `routes/*.json` 的 `policyId` | 1 |
| TaskType | 本体 `gits:TaskType` ∪ activations/routes 的 `taskType` | 5 |

**变异自证（6/6 全部被捕获）**：`fake_assetRef` / `fake_skillRef` / `fake_activationContractRef` /
`fake_taskRef` / `fake_domainRef` / `fake_mapRef` —— 每个都 `BEFORE → 注入 → FAIL（附 ID 空间+字段+原因）→ 恢复 → PASS`，
且**被测 4 个原文件 sha256 全部 SAME**（自证未污染权威源），临时目录已清理。
另有端到端 fail-closed 验证（独立 `--root` 副本注入 2 个假引用 ⇒ exit 2，逐条打印）。

**诚实缺口（不计入 PASS 断言）**：`KD-*` 无独立锚点来源 ——
`selfDeclaredOnly=['KD-CORP-RM-PREVISIT','KD-CORP-RM-RECON']`（只有父图自声明），
`soundness=NOT_COUNTED_AS_PASS_ASSERTION`。

**TL 裁决**：批准"诚实清单"口径，**不改成硬 FAIL** ——
理由与本仓教条一致（`INCONCLUSIVE ≠ 通过`）。KD-* 的问题是**无权威源可校验**，不是**引用错**；
改硬 FAIL 会让门禁**永久红**，永久红的门禁会被当噪音忽略，那才是真的失去防线。

### WP5.2 `triple_consistency_check` = **FAIL**（门禁自曝空转）

见 `FAILURES.md` 的 `GATE_NOOP` 条目。**作者自曝**并判 FAIL，**未**以"不一致项 0"报绿。
D3（mapRef 文件不存在）/D4（悬空引用）已 OK；原本体 sha256 逐字节复原。
已按单写者规则交回作者修复（第 1/5 次）。

### TL 独立复核（**不采信自述**）：作者报的 6 项既有缺口，逐条实测

| # | 发现 | 实测结论 | 处置 |
|---|---|---|---|
| 1 | 既有 `validate_knowledge_architecture.py` 不校验 `domainId`/`mapRef`/`entrypoints.tasks` | **真**（正是 WP5.1 补上的三项：`mapRef=3`、`taskType=10`、`domain=3`） | 记档 |
| 2 | `KM-*` 无独立 registry（`MapVersion.json` 只有 `SIM-MAP-FINANCE`） | **真** | 记档 |
| 3 | `KD-*` 无独立锚点来源 | **真** | 按"诚实清单"保留 |
| 4 | **KD 命名空间混淆**：`elements/knowledge-items-index.json` 用 `KD-01/KD-02/KD-08` | **真**（实测取值集合） | 记档为**后续对齐陷阱**（按 KD- 前缀全局 grep 会撞上） |
| 5 | `registry/AssetVersion.json` 只含 4 条 `SIM-ASSET-*`；而**本体 `gits:Asset` 注释声称资产登记于该文件** | **真** | ⚠️ **已修**（见下） |
| 6 | `Capability.json` 的 `probeStatusEnum` 有枚举外值 `SUPERSEDED` | **真** | 记档待裁定（扩枚举 vs 改值属合同变更，不由本 Loop 单方改） |

### ⚠️ 本 ITER 修掉的一处**合同错误指引**（发现 #5，价值最高）

WP5.1 的作者报告直接暴露了**本体注释指错登记处**：

```
修正前： gits:Asset ... "ID 空间 ASSET-*；登记于 specs/knowledge-architecture/registry/AssetVersion.json。"
实测：   registry/AssetVersion.json 只有 SIM-ASSET-P001 / SIM-ASSET-METRIC / SIM-ASSET-RESTRICTED / SIM-ASSET-CAS-CONFLICT
真实锚点：specs/knowledge-architecture/assets/**/*.md 的 front matter assetId（21 个）
```

⇒ 任何按本体注释去 registry 找资产锚点的人都会**全量假 FAIL**。已修正为指向 `assets/` manifest，
并显式注明 registry 只含夹具。修后 `make generate` PASS、`make check` exit 0 / **22-23**。
（对照：`gits:Skill` 的注释"登记于 `specs/knowledge-architecture/skills/`"是**对的**，未动。）

### 门禁总表（**9 pass / 2 fail**）

| pass | `contract_generate` · `contract_check`(22-23) · `gk_ke_gates` · `ontology_load` · `security_check` · `backend_test` · **`ref_anchor_check`** · **`gk17_prodcard_projection`** · （`contract_generate`/`contract_check`/`ref_anchor_check` 已因合同变更**重落证**） |
|---|---|
| **fail** | `frontend_test`（环境限制）· **`triple_consistency_check`**（门禁空转，待作者修） |

### 关于"挂进 `run_gates.py`"

**本轮不做，留到 W8**。理由：`run_gates.py` 是 `make check` 的组成部分、被多个 Loop 共用，
改动会外溢到其他 actor 的验证面。本 Loop 门禁先以 `record_gate.py` 独立落证；
是否并入 `make check` 属**收口期决策**，W8 时连同说明提交。

### 非声明

- WP5.1 的 PASS **不等于**"所有 ID 空间都有权威锚点"—— `KD-*` 的缺口已如实标注且**未计入通过**；
- WP5.2 **尚未通过**，不得以"不一致项 0"计入任何通过口径；
- 本 ITER **未**把任何既有红灯转绿：`frontend_test` 仍 fail、`semantic-consumption` 仍 READINESS NOT MET。
