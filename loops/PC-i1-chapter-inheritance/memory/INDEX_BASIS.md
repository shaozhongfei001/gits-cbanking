# PC-i1-chapter-inheritance｜索引依据（代码事实索引与检索底座）

> 流程依据：`docs/governance/CODE-FACT-INDEX-PROCESS.md`（GOV-CFI-001）
> 约束：索引是 **DERIVED 派生视图**，只给线索；下表"回源结论"必须带 `文件:行` 才可被引用。
> 本轮用途：承接 **独立 E2E QA（2026-09-22）** 的三项裁决，把裁决与影响面**回源**落盘。

| 项 | 值 |
|---|---|
| **索引版本** | `.ua/merge-meta.json` @ `2026-09-15T17:50:17Z`（gits @`7116904` / kert @`64f6f87`；merged 5106 节点 / 4235 边 / 54 层） |
| **新鲜度声明** | **`INDEX_STALE(51)`** —— gits HEAD `fdd2bdb` 落后索引基线 **51 个提交**（阈值 50），本轮**已按 §C5 声明**；故本轮所有事实**逐条回源**，不采信索引结论 |
| **门禁** | `make index-status` → **`WARN`**（F1 索引过期 ×2：`merge-meta.json`/`meta.json` 各落后 51；红线 R1–R3 未触发） |
| **裁决来源** | `frontend/test-results/qa-20260922-1430/REPORT.md`（QA 总判 FAIL；含 trace / HAR / 逐章 JSON）；被 QA 基线 = 分支 `recover/PI-ARCH-product-catalog`，前端 `15173` → 后端 `18080` |

> 命名去歧义（**必读**）：QA 报告内部缺陷号与本文件所在 loop/契约的既有编号**撞号**。
> - QA-`D-1`（5 章空壳）↔ 本文档 `本-1`
> - QA-`D-2`（族名漂移 7 例）↔ 契约 `CTR-PK-TAX-001` 的**已知差异 D-1**（同一问题，**非新发现**）
> - QA-`D-3`（期望值过期）↔ 本文档 `本-2`

---

## 本轮裁决（TL 回源，2026-09-22）

### 本-1 ·【P0 · 成立】产品中心 5 章"有数据但渲染空白"（QA-D-1）

| 项 | 内容 |
|---|---|
| 结论 | **确认为产品缺陷**（非环境项、非测试侧），阻塞发布，**属本 loop scope** |
| 根因（回源） | `frontend/src/components/product-center/ProductChapterStack.vue:106` 为 `v-else-if="!hasPayload(section.key)"`（「待接入」分支），而组件**只有** `:70` 的 `v-if="section.key === 'OVERVIEW'"` 一个正文分支 ⇒ `hasPayload===true` 且非 `OVERVIEW` 的章节**两个分支都不命中**（全文件仅 3 处分支指令：`:64` n-tag、`:70` v-if、`:106` v-else-if，**无 `v-else`**） |
| 违反口径（回源） | 组件自陈口径 `ProductChapterStack.vue:4-11`（"有契约数据的章节按契约渲染；无契约数据的章节显示具名未接入状态"）与 loop objective「不得留空占位、不得以示意内容填充」 |
| 影响面（TL 复测，扩大 QA 单点样本） | **13/13 产品 × 5 章**（`TERMS`/`FIT`/`PROCESS`/`MATERIALS`/`COMPARE`）在 `GET /api/v1/product-center/products/{id}` 上**均有数据**，页面上均**无正文且无「待接入」标签**；正确处于具名未接入的仅 `PRICING`（`待接入 PC3`）/`FAQ`（`待接入 PC4`）2 章。QA 单点样本（`PROD-CM-003`）与本复测一致 |
| 形状来源（**不是缺口**） | 章节形状**已有受控契约**：`specs/product-center/product-center-api.openapi.json:368/401/414/426/461/511`（`PkcTerm`/`PkcBoundary`/`PkcPrerequisite`/`PkcProcessStep`/`PkcMaterialGroup`/`PkcComparisonSet`），detail 响应映射见同文件 `:713-716` |
| 前端待补（回源） | `frontend/src/api/productCenter.ts:108-117` 把 `terms`/`boundaries`/`processSteps`/`materialGroups`/`pricingItems`/`faqs` 定为 `unknown[]`、`comparison` 为 `unknown \| null` ⇒ 渲染分支落地时必须先按契约类型收窄（属本 loop scope 内文件） |
| 判据（机械可验） | QA `B4`/`E1` 的**逐章二选一**规则：有数据 ⇒ 该章正文非空且含接口该章首条内容；无数据 ⇒ 该章存在具名「待接入 <批次>」 |
| 证据 | `b4-per-chapter.json`、`e1-pending.json`、`shot-b4.png`、`raw-qa-all/**/trace.zip`；TL 复测：`18080` 逐 13 产品实测 |

### 本-2 ·【P0 · 成立】既有验收期望值过期（QA-D-3）—— **禁止 7→2**

| 项 | 内容 |
|---|---|
| 结论 | **"期望值过期"与"产品缺陷"同时成立**（不是二选一）；**禁止**以 `7 → 2` 让用例转绿 |
| 期望值过期（回源） | `frontend/e2e/product-center-pc1.spec.ts:53` 硬编码 `pc-chapter-pending = 7`；后端现仅 2 章真未接入（`pricingItems=0`、`faqs=0`）⇒ 常量 `7` 已不成立 |
| **产品缺陷并存** | 另 5 章并非"已接入"，而是 `本-1` 的空壳 ⇒ 若仅改常量，等于**把 5 个空壳锁进"通过"**（把缺陷固化为期望） |
| 同源单测（回源） | `frontend/src/views/__tests__/ProductCenterView.spec.ts:213` 同源断言（同样硬编码 `7`），须同步 |
| 正确改法（TL 裁决） | 断言**改语义、不改数字**：逐章判定「有数据 ⇒ 正文非空且与接口一致 / 无数据 ⇒ 具名 `待接入 <批次>`」，覆盖 8 章全量；**不得**弱化为 `toBeVisible`/`toHaveCount(8)`/加 `waitForTimeout` |
| 顺序约束 | 必须 **`本-1` 先修、`本-2` 后改**（同批交付）；否则新断言必然红 |
| 判据（机械可验） | 两处用例改为逐章二选一后全绿，且 `git diff` 中**不存在** `7` → `2` 这类常量替换 |

### 本-3 ·【成立 · 不阻塞 · 非新发现】跨页产品族名不一致 7 例（QA-D-2）

| 项 | 内容 |
|---|---|
| 结论 | **成立，但非新缺陷**：权威名**已由 Owner 裁决 OQ-B 确定**，且该差异**已登记在册、已有落点** ⇒ 不新增 PC-i1 工作，转派 PI-1 |
| 权威名（回源） | `specs/product-knowledge/product-taxonomy.yaml:19-26`（`CTR-PK-TAX-001` 已知差异 D-1）：产品卡 front matter 的 `product_family_name` 为「结算服务 / 贸易融资 / 流动资金融资」，与 **Owner 裁决 OQ-B 的族名「结算 / 贸易金融 / 融资」不一致**；"本文件以**裁决名**为准，**产品卡侧对齐放 PI-1**" |
| 判定 | ⇒ 权威 = **产品中心侧**（`CTR-PKC-API-001`，即 QA 实测的 `结算/贸易金融/融资`）；**漂移侧 = 解读页/产品卡（KERT `03_core` front matter）** |
| 为何不派本 loop（回源） | `loops/PC-i1-chapter-inheritance/LOOP.yaml` `scope.exclude` 明列「`frontend/src/views/ProductInterpretationView.vue`（P38 冻结）」「`apps/api/.../productknowledge/`（P38 冻结）」「`specs/` 受控源」「**Leibniz-KERT 制品**」⇒ 修正点全在排除面内 |
| 影响面（回源 QA 实测） | 7 张：`PROD-SET-001/002`（结算 vs 结算服务）、`PROD-TF-001/002`（贸易金融 vs 贸易融资）、`PROD-FIN-001/002/003`（融资 vs 流动资金融资）；**仅显示名**不同，族集合与族数一致（6 族），产品归属不变 |
| 严重度 | **维持 QA 的 P1**（用户可见），**不阻塞发布**；TL 不降级、不撤项，仅更正"归属与落点" |
| 禁止做法 | **不得**在前端硬编码族名别名映射（会造成第三份命名，违反 `CTR-PK-TAX-001` 权威关系） |
| 证据 | `d1-cross-page.json`、`shot-d1.png`；契约侧：`product-taxonomy.yaml:19-26`、`:65`（"6 实体族 + 1 预留位，不得增删"） |

---

## 候选影响面（来自索引 L0/L1/L2，**未回源前不得作为事实**）

| # | 候选对象（模块 / 文件 / 类） | 索引来源 | 回源结论（`文件:行`） | 判定 |
|---|---|---|---|---|
| 1 | 产品中心章节栈（前端组件） | `file:` 级候选（`.ua` 前端 4024 节点） | `frontend/src/components/product-center/ProductChapterStack.vue:70`、`:106`（无 `v-else` 正文分支） | **受影响（根因）** |
| 2 | 章节常量与命名映射 | `file:` 级候选 | `frontend/src/components/product-center/sections.ts:9-16`（8 章清册）、`:28-37`（`SECTION_CONTRACT_OBJECTS`）、`:40-49`（`SECTION_PLANNED_LOOP`） | 受影响（渲染分支取此映射） |
| 3 | 前端产品中心 API 类型 | `file:` 级候选 | `frontend/src/api/productCenter.ts:108-117`（章节字段现为 `unknown[]` / `unknown \| null`） | 受影响（须按契约收窄） |
| 4 | 章节形状契约 | 索引**不含** `specs/` 字段级解析 ⇒ 索引答不了 | `specs/product-center/product-center-api.openapi.json:368/401/414/426/461/511`、`:713-716` | **权威已备（不是缺口）** |
| 5 | 后端投影装配 | `layer:`/`file:` 候选 | `apps/api/src/main/java/com/gien/gits/api/productcenter/ProductCenterCatalogService.java:216-219`、`:258-263`；`ProductCenterSectionProjectionAdapter` | **不受影响**（数据已正确投影） |
| 6 | 既有验收期望值 | 索引**不含**测试断言语义 ⇒ 索引答不了 | `frontend/e2e/product-center-pc1.spec.ts:53`、`frontend/src/views/__tests__/ProductCenterView.spec.ts:213` | 受影响（同 `本-2`） |
| 7 | 族名权威 | 索引**不含** `specs/` 语义 ⇒ 索引答不了 | `specs/product-knowledge/product-taxonomy.yaml:19-26`、`:65` | 权威已定（转 PI-1） |
| 8 | 解读页/产品卡（漂移侧） | 跨仓边 = 0 ⇒ 索引答不了 | KERT `examples/product-recommendation-assets/03_core/*/product-cards/PROD-*.md` front matter（本次未回源到单卡行号，**F-PC-i1-03 待补**） | 受影响但**出本 loop scope** |

## 索引未覆盖、必须回源的盲区（本轮实际踩到的）

| # | 问题 | 索引为何答不了 | 回源位置（`文件:行`） |
|---|---|---|---|
| 1 | 章节正文为何不渲染 | 无 `.vue` 结构抽取（模板分支指令不在图里） | `ProductChapterStack.vue:70`、`:106` |
| 2 | 章节载荷的可渲染形状 | `specs/` 未做字段级解析 | `specs/product-center/product-center-api.openapi.json:368-530` |
| 3 | 族名权威与已知差异 | `specs/` 语义未入库；且无跨仓边（KERT 产品卡） | `specs/product-knowledge/product-taxonomy.yaml:19-26` |
| 4 | 验收期望值过期与否 | 索引不索引测试断言意图 | `frontend/e2e/product-center-pc1.spec.ts:53`；`ProductCenterView.spec.ts:213` |
| 5 | 影响面是否为全产品 | 索引无「接口字段 × 页面渲染」映射 | TL 对 `18080` 逐 13 产品实测（13/13 命中） |

## 本批次新增的可复用结论（供下一 holder 免于重复通读源码）

| # | 结论 | 出处（`文件:行`） | 落地位置 |
|---|---|---|---|
| 1 | 章节栈只有 `OVERVIEW` 正文分支 + 通用「待接入」分支，**缺 `v-else` 正文分支**；这是 5 章空壳的**唯一**根因（数据侧已就绪） | `ProductChapterStack.vue:70`、`:106` | 派工单 `W-1` |
| 2 | `hasPayload` 判定：`summary`/`comparison` 非 null、其余为**数组非空** | `ProductChapterStack.vue:31-46` | `W-1` 的实现与断言共用 |
| 3 | 章节形状**已有权威契约**（`Pkc*`），无需新造；前端仅缺类型收窄 | `product-center-api.openapi.json:368-530`；`productCenter.ts:108-117` | `W-1` |
| 4 | 族名权威 = 产品中心侧「结算/贸易金融/融资」；漂移侧在 KERT 产品卡 front matter，落点 **PI-1** | `product-taxonomy.yaml:19-26` | 派工单 `W-3`（转派，未授权） |
| 5 | 现行 8 章中 `PRICING`/`FAQ` 的「待接入」是**正确行为**（`pricingItems=0`、`faqs=0`），不得因修 `W-1` 而被一并改成空白 | `b4-per-chapter.json`；`sections.ts:40-49` | `W-1` 的"不得回归"约束 |
| 6 | `*.live.spec.ts` 默认常量已过期（`8082`/`8106` ≠ 现行 `18080`/`8107`）；**覆盖后 12/12 PASS** ⇒ 属脚手架漂移，非链路失效 | `REPORT.md` §三 D-4、`f2b-live-with-env-override.txt` | 未裁决（另派） |

## 非声明

- 本文件是**派生线索 + 回源结论**的记录，不是权威职责定义；与 `specs/` 冲突时以 `specs/` 为准。
- 本文件**不构成 `QA_PASS`**，不作为 Gate/ADR 依据（GOV-CFI-001 §C3）。
- 本文件**不授权任何人开工**：工作项与授权状态以派工单 `DISPATCH-2026-09-22-QA-裁决与派工.md` 为准。
- QA 报告中的 `BLOCKED` 项（`D-6` 环境未就绪 4 条、`F2` 裸跑 9 条未运行）**一律仍记 BLOCKED**，不得因本文件改写为 pass。


---

## W-1 / W-2 执行结果（回源 · 2026-09-22T14:59:39+00:00）

| 项 | 事实（含文件与证据） |
|---|---|
| **W-1 实现** | `ProductChapterStack.vue` 新增 **`v-else` 正文分支**（位于 `:106` 的「待接入」分支之后）：`TERMS`/`FIT`/`PROCESS`/`MATERIALS`/`COMPARE` 各按契约字段渲染；「已渲染正文」的统一锚点为 `data-testid="pc-chapter-body"`（含 OVERVIEW） |
| W-1 附带修正 | `FIT` 的 `hasPayload` 由「仅 `boundaries`」扩为 **`boundaries ∪ prerequisites`** —— 否则「有前置条件、无典型场景」会被错报「未接入」（反向不诚实） |
| **W-1 类型** | `frontend/src/api/productCenter.ts` 新增 `PkcTerm`/`PkcBoundary`/`PkcPrerequisite`/`PkcProcessStep`/`PkcMaterialGroup`/`PkcMaterialItem`/`PkcComparisonSet`/`PkcEvidenceRef`/`PkcCertaintyType`，逐项对齐 `specs/product-center/product-center-api.openapi.json:368/401/414/426/461/511`；`comparison.dimensions/rows` 在合同中为 `array<object>` ⇒ 按**实测响应形状**收窄并注明（不声称合同已定义） |
| **W-2 断言改写** | `frontend/e2e/product-center-pc1.spec.ts`（原 `:53`）与 `frontend/src/views/__tests__/ProductCenterView.spec.ts`（原 `:213`）→ **逐章二选一**：有数据 ⇒ `pc-chapter-body` 可见 + 正文非空 + `pc-chapter-pending` 为 0；无数据 ⇒ 反之。（原常量断言 `7` 已删除） |
| W-2 约束核实 | `git diff` 确认**不存在 `7 → 2` 常量替换**；断言**未弱化**（无 `toBeVisible` 顶替、无 `waitForTimeout`） |
| W-2 新增用例 | 单测新增「有契约数据的章节必须渲染正文（W-1 回归）」：夹具故意与既有相反（5 章有数据）⇒ 直接锁住 QA-D-1 的反面 |
| **端到端证据** | 逐章 JSON + 3 产品整页截图：`frontend/test-results/pc-i1-w1/evidence/evidence.json` —— `PROD-CM-003`/`PROD-SET-001`/`PROD-FIN-003` **各 8 章 0 违规**；`TERMS` 内容抽查 `present=true`（值 = 接口 `terms[0].businessDefinition`） |
| **QA 判据复跑** | `B3/B4/B5/B6/E1/G1` + `product-center-pc1`（QA 的 F3 项）⇒ **7/7 PASS**（其中 `B4`/`E1` 此前为 **P0 FAIL**） |
| **门禁（以 `EVIDENCE.json` 为准）** | `contract_generate` **pass** · `security_check` **pass** · `frontend_typecheck` **pass** · `frontend_unit` **fail** · `e2e_parity` **fail** · `contract_check` **fail** —— 后三者根因/等价复跑见 `FAILURES.md`，**一律未改为 pass** |
| 本轮新踩到的盲区（可复用） | ① `record_gate.py` 在**仓库根**执行门禁 ⇒ `npx --prefix frontend …` **不改变 cwd**：vitest 会把 `frontend/e2e/*.spec.ts` 当单测收集（实测 75 failed），且依赖 cwd 的用例报 `ENOENT`；② 基线 `playwright.config.ts` 的 webServer 起 5173，其 vite 代理默认 `8080`（401）≠ 运行中的 `18080` ⇒ 门禁命令须注入 `VITE_API_PROXY_TARGET` 或改用 QA 配置 |
| **未开工** | P38 12 章落位、C6/C9/C11 独立可见、同产品对照三判定 —— 本次**未动**（loop 目标远未完成） |


## 本轮新增判据/工具冲突（回源 · 2026-09-22T15:00:40+00:00）

| # | 事实 | 出处（`文件:行`） | 影响 |
|---|---|---|---|
| 1 | 门禁原始输出被写入 `loop/evidence/`，而 loop 占位符扫描覆盖 loop 内**所有**文件 ⇒ 失败日志中的 Vue 源码 `{ { }}` 被误判为"未解析占位符" | `scripts/record_gate.py:89-93`；`scripts/loop_guard.py:88-110`；命中位置 `loops/PC-i1-chapter-inheritance/evidence/frontend_unit-20260922T145816Z.log:556` | `loop-guard` **FAIL**（未豁免、未修改门禁）；`make check` 的 `loop-guard`/`loop-instances` 受影响 |
| 2 | 判别依据（非真占位符）：命中 **1** 处；通过的等价日志命中 **0**；loop 内其他文件命中 **0** | 同上 + `evidence/frontend_unit-equiv-20260922T145854Z.log` | 结论：**工具口径冲突**，非本 loop 内容缺陷 |
| 3 | 建议修法（**待授权**）：`R-1` 扫描跳过 `evidence/**`；`R-2` 日志改落 `frontend/test-results/gates/**` | — | 二者都不触碰证据内容与门禁判据强度 |
