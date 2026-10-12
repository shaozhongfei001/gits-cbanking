# WP1-1 合同核验候选（GITS 合同 lint/diff 与自洽核验）

```text
文档编号   = WP1_CONTRACT_VERIFICATION_CANDIDATE
角色       = GITS/QA
任务       = WP1-1（GITS 合同核验；只核验，不改动任何契约文件）
批次       = GITS-WP1（见 WP0-WP1 派工清单）
状态       = CANDIDATE
FROZEN     = NO
IMPLEMENTED = NO
形成日期   = 2026-08-31
取证 HEAD  = aea4d8b21d26bb748d84b69ec9bb5908500aa28e（branch feature/P30-gits-bank-experience-shell）
权威依据   = 三段式落地方案 V1.0 + 产品解读与推荐交接总册 V1.1 + 本体智能体交接总册 V1.0（§4.2 命名）
核验对象   = step 3 已落地 SDD 产品推荐契约（当前暂存于 stash@{0}，见 §0）
```

> 本文件只做核验取证，输出 PASS/FAIL 矩阵与修复建议，**不修改任何契约文件**、不 `git stash pop`、不写 `generated/`。所有结论均以命令实测证据为准。

---

## 0. 取证方法与关键前提（先取证，再下结论）

**关键前提**：step 3 已落地的 SDD 产品推荐契约当前**不在工作树**，而是被 WP0-1（基线治理）任务为"工作树隔离"整体执行 `git stash push -u` 暂存于 `stash@{0}`。证据见 `docs/governance/WP0_BASELINE_STATUS_CANDIDATE.md` §5（"暂存他任务未提交工作 … 保留不销毁、可 git stash pop 复原"）。

实测工作树与 stash 的差异：

| 对象 | 工作树（当前 HEAD） | stash@{0}（step 3 落地态） |
|---|---|---|
| `specs/CONTRACT_INDEX.yaml` | 无 `CTR-PR-*`（`grep -c "CTR-PR-"` = 0），与 HEAD 一致 | +72 行，含 7 条 `CTR-PR-*` 登记 |
| `specs/knowledge-architecture/skills/SP-15.json` | `v1.1.0-p20`（旧版） | `v2.0.0-candidate`（落地版） |
| `specs/product-recommendation/`（6 schema + README） | **不存在** | 存在（未跟踪文件） |
| `specs/openapi/product-recommendation.openapi.json` | **不存在** | 存在（未跟踪文件） |
| `specs/knowledge-architecture/activations/AC-PRODUCT-RECOMMEND-001.json` | **不存在** | 存在（未跟踪文件） |

**取证方式（只读，不改动仓库）**：以 `stash@{0}` 中的落地态为准，用 `git show stash@{0}:<tracked>` 与 `git show stash@{0}^3:<untracked>` 将 16 个契约文件只读抽取到 `/tmp/wp1-verify/`（临时目录，仓库外），并复制工作树中的两个参考 schema（`skill-descriptor.schema.json`、`activation-contract.schema.json`，两者为 tracked 且未改动）到同一临时目录后执行校验。

`stash@{0}` 落地态文件清单（`git stash show --include-untracked --stat`）：

```text
specs/CONTRACT_INDEX.yaml                                          (+72)  tracked
specs/knowledge-architecture/skills/SP-15.json                     (+10-5) tracked
specs/product-recommendation/README.md                             (untracked)
specs/product-recommendation/eligibility-result.schema.json        (untracked)
specs/product-recommendation/portfolio-candidate.schema.json       (untracked)
specs/product-recommendation/product-fit-result.schema.json        (untracked)
specs/product-recommendation/product-recommendation-run.schema.json(untracked)
specs/product-recommendation/recommendation-human-decision.schema.json (untracked)
specs/product-recommendation/recommendation-result.schema.json     (untracked)
specs/knowledge-architecture/activations/AC-PRODUCT-RECOMMEND-001.json (untracked)
specs/openapi/product-recommendation.openapi.json                  (untracked)
adapters/.../db/migration/{h2,mysql}/V020__product_recommendation.sql (untracked)
docs/adr/ADR-PR-CANDIDATES.md                                      (untracked)
docs/*.pdf / *.pptx                                                (untracked，与本任务无关)
```

---

## 1. 核验矩阵（a–e）

> 结论：**a=PASS、b=FAIL、c=PASS、d=PASS、e=FAIL**（其中 b 与 e 均为一子项 PASS、一子项 FAIL 的部分失败）。

### (a) JSON 合法性 —— **PASS（9/9）**

逐文件 `python3 -m json.tool <file>` 全部通过：

| # | 文件（落地态 /tmp/wp1-verify 路径） | 结果 | 证据命令 |
|---|---|---|---|
| 1 | `specs/product-recommendation/eligibility-result.schema.json` | PASS | `python3 -m json.tool` |
| 2 | `specs/product-recommendation/portfolio-candidate.schema.json` | PASS | 同上 |
| 3 | `specs/product-recommendation/product-fit-result.schema.json` | PASS | 同上 |
| 4 | `specs/product-recommendation/product-recommendation-run.schema.json` | PASS | 同上 |
| 5 | `specs/product-recommendation/recommendation-human-decision.schema.json` | PASS | 同上 |
| 6 | `specs/product-recommendation/recommendation-result.schema.json` | PASS | 同上 |
| 7 | `specs/openapi/product-recommendation.openapi.json` | PASS | 同上 |
| 8 | `specs/knowledge-architecture/skills/SP-15.json`（落地 v2.0.0-candidate） | PASS | 同上 |
| 9 | `specs/knowledge-architecture/activations/AC-PRODUCT-RECOMMEND-001.json` | PASS | 同上 |

附加：6 个 schema 文件本身作为 draft 2020-12 JSON Schema，经 `check_schema` 自检均合法（`validator_for(...).check_schema` 全部 PASS）。

### (b) CONTRACT_INDEX.yaml 合法 JSON + CTR-PR-* authority_source 指向实际文件 —— **FAIL**

**b1（JSON 合法）**：PASS。`python3 -m json.tool specs/CONTRACT_INDEX.yaml`（落地态）通过；该文件扩展名为 `.yaml` 但内容为合法 JSON。

**b2（authority_source 指向实际存在的文件）**：FAIL。7 条 `CTR-PR-*` 登记及其 `authority_source` 目标**仅存在于 `stash@{0}`**，在**当前工作树全部不存在**（`test -f` 均为 ABSENT）：

| id | authority_source | 工作树 | stash@{0}^3 |
|---|---|---|---|
| CTR-PR-API-001 | `specs/openapi/product-recommendation.openapi.json` | ABSENT | PRESENT |
| CTR-PR-RUN-001 | `specs/product-recommendation/product-recommendation-run.schema.json` | ABSENT | PRESENT |
| CTR-PR-ELIG-001 | `specs/product-recommendation/eligibility-result.schema.json` | ABSENT | PRESENT |
| CTR-PR-FIT-001 | `specs/product-recommendation/product-fit-result.schema.json` | ABSENT | PRESENT |
| CTR-PR-PORT-001 | `specs/product-recommendation/portfolio-candidate.schema.json` | ABSENT | PRESENT |
| CTR-PR-RES-001 | `specs/product-recommendation/recommendation-result.schema.json` | ABSENT | PRESENT |
| CTR-PR-DEC-001 | `specs/product-recommendation/recommendation-human-decision.schema.json` | ABSENT | PRESENT |

证据命令：`grep -c "CTR-PR-" specs/CONTRACT_INDEX.yaml`（工作树 = 0）；`git cat-file -e "stash@{0}^3:<path>"`（7 条均存在）；`test -f <path>`（7 条均不存在）。

**说明**：工作树 `specs/CONTRACT_INDEX.yaml` 尚未登记任何 `CTR-PR-*`（登记只在 stash 里），因此"specs/CONTRACT_INDEX.yaml 已 CTR-PR-* 登记"在仓库当前可见状态不成立。这不影响对 stash 内落地态内容本身的判读，但会阻断 WP1-3/WP1-4/WP1-5 直接读取这些文件。

**修复建议**：由 Tech Lead/MAIN 裁决恢复方式后复验（本 QA 任务不执行）。可选：
- 整体恢复：`git stash pop stash@{0}`（会连带恢复 `docs/*.pdf/.pptx` 等无关文件，需确认工作树干净、无冲突）；
- 或选择性恢复落地契约：`git checkout stash@{0} -- specs/CONTRACT_INDEX.yaml specs/knowledge-architecture/skills/SP-15.json` + `git checkout stash@{0}^3 -- specs/product-recommendation/ specs/openapi/product-recommendation.openapi.json specs/knowledge-architecture/activations/AC-PRODUCT-RECOMMEND-001.json`。
恢复后复跑 b2，`test -f` 应全为 PRESENT。

### (c) SP-15.json 满足 skill-descriptor.schema.json required —— **PASS**

以落地态 `SP-15.json`（v2.0.0-candidate）为核验对象，用 `jsonschema.Draft202012Validator(skill-descriptor.schema.json).validate(SP-15.json)` 通过：schema 的 14 个 `required`（`schemaVersion/skillId/name/version/owner/status/implementationType/inputs/outputs/assetDependencies/semanticDependencies/ruleDependencies/humanGatePolicy/sideEffectPolicy`）全部存在，枚举 `status=VALIDATION`、`implementationType=RULE_MODEL`、`humanGatePolicy=REQUIRED`、`sideEffectPolicy=PROPOSE_ONLY` 均在合法集合内，`skillId=SP-15` 匹配 `^SP-[A-Z0-9-]+$`，且无额外字段（`additionalProperties:false` 满足）。

> 附注：工作树现存 `SP-15.json` 仍为旧版 `v1.1.0-p20`（inputs/outputs/ruleDependencies 与落地版不同），结构上同样通过 schema，但**不是** step 3 落地版本——印证 §0 的"落地态在 stash、工作树未落地"。

### (d) AC-PRODUCT-RECOMMEND-001.json 满足 activation-contract.schema.json required 且无 extra —— **PASS**

以落地态 `AC-PRODUCT-RECOMMEND-001.json` 为对象，`Draft202012Validator` 校验通过：schema 的 13 个 `required`（`schemaVersion/contractId/version/taskType/routeMode/preconditions/activations/semanticQueries/ruleChecks/skills/context/humanGates/failurePolicy`）全部存在；顶层 `additionalProperties:false` 生效，实测顶层键集合与 schema `properties` 完全一致、无 extra 字段；嵌套约束亦满足（`preconditions.requiredInputs/requiredRoles/permissionDecisionRequired`、每个 `activations[]` 的 `assetId/required/purpose/sequence`、`context.maxTokens/priorityOrder/trimPolicy` 齐全；`routeMode=ONTOLOGY_THEN_MAP`、`failurePolicy=FAIL_CLOSED`、`trimPolicy=CONTRACT_PRIORITY` 均在枚举内；`contractId` 匹配 `^AC-[A-Z0-9-]+$`）。

证据命令：`Draft202012Validator(activation-contract.schema.json).validate(AC-PRODUCT-RECOMMEND-001.json)`；`set(ac.keys()) - set(schema["properties"].keys())` = 空集。

### (e) 命名一致性 —— **FAIL**

**e1（不应把 `RecommendationProposalVersion` 旧名当主名）**：FAIL。

- 权威口径（README 落地态 §1、§唯一权威链）明确主名为 `ProductRecommendationProposalVersion`；《本体智能体交接总册》§4.2 将 `RecommendationProposalVersion` 定为"旧技术别名"、`ProductRecommendationProposalVersion` 为"业务首选名"。
- 但 `specs/openapi/product-recommendation.openapi.json` 将旧名用作**主 schema 名**：第 79 行 `$ref: "#/components/schemas/RecommendationProposalVersion"`、第 161 行 `"RecommendationProposalVersion": {...}` 定义组件。这使旧名成为 OpenAPI 契约中的唯一/主命名，违背"不应把旧名当主名"。
- 另：`specs/product-recommendation/` 的 6 个 schema 中没有独立的 proposal-version 对象 schema（该对象仅内联在 openapi），README §6 文件清单也未列该对象文件。

**修复建议**：在 `product-recommendation.openapi.json` 中将 schema 名与 $ref 从 `RecommendationProposalVersion` 改为 `ProductRecommendationProposalVersion`；若契约已冻结不能改机器名，则按《交接总册》§4.2 备用方案：保留机器名 `RecommendationProposalVersion`，但在该组件显式声明业务首选名 `ProductRecommendationProposalVersion`（如 `title` 或 `x-business-preferred-name`）+ `x-deprecated-alias: RecommendationProposalVersion` + 弃用/迁移候选标注，并补齐独立 `product-recommendation-proposal-version.schema.json`。

**e2（`RecommendationHumanDecision` 记录对象 vs `RecommendationDecision` 枚举）**：PASS。

- `recommendation-human-decision.schema.json`：`title: "RecommendationHumanDecision"`（记录对象，含 gateId/runId/proposalVersionId/decision/modifications/reason/actorId/decidedAt）；`$defs.RecommendationDecision`（枚举 `APPROVE/MODIFY/REJECT/HOLD`）；记录对象的 `decision` 字段 `$ref: "#/$defs/RecommendationDecision"` 正确指向枚举。
- README 落地态 §1 明确"`RecommendationHumanDecision` 是人工决定的记录对象；`RecommendationDecision` 是其决策值枚举（APPROVE/MODIFY/REJECT/HOLD），两者不混用"。两处一致，未发现混用。

---

## 2. 修复建议汇总（FAIL 项）

| 项 | 结论 | 可执行修复建议 |
|---|---|---|
| b2 | FAIL | Tech Lead/MAIN 裁决恢复 stash@{0} 落地契约到工作树（`git stash pop` 或选择性 `git checkout stash@{0}[^3] -- <paths>`，见 §(b)），恢复后复跑 `test -f` + 重读 CONTRACT_INDEX.yaml。 |
| e1 | FAIL | openapi 组件名与 $ref 由 `RecommendationProposalVersion` → `ProductRecommendationProposalVersion`；或冻结前提下用 `x-business-preferred-name`/弃用别名标注，并补齐独立 proposal-version schema。 |

---

## 3. 补充自洽发现（不计入 a–e 判分，供 Tech Lead 参考）

- **S1 落地态不在工作树（根因）**：step 3 契约整体在 `stash@{0}`，工作树仍为 step 3 前状态。这是 b2 失败及后续 WP1 子任务无法直接读文件的总根源。建议在 WP1 派发前先解决（见 §2 b2）。
- **S2 `product-fit-result.schema.json` 的 `$id` 与文件名 basename 不一致**：文件名为 `product-fit-result.schema.json`，但 `$id` 为 `.../fit-result.schema.json`（无 `product-` 前缀）。`recommendation-result.schema.json` 的 `fitResults` 项 `$ref` 用的是 `$id`（`fit-result.schema.json`），故按 `$id` 解析可命中；但若契约注册表按物理文件名解析，则会失配。建议统一 `$id` 与文件名（其余 5 个 schema 的 `$id` 与文件名一致，仅此一处不一致）。
- **S3 openapi 阶段视图 schema 过宽**：`ProductRecommendationStageResult` 中 `eligibilityResults/fitResults/portfolioCandidates/needProfile` 用 `{type:object, additionalProperties:true}` 松散定义，未 `$ref` 独立 schema，存在契约漂移风险（openapi 是权威入口，宜 `$ref` 权威 schema）。
- **S4 openapi 内联 `RecommendationProposalVersion` 而非独立 schema**：见 §(e)e1，建议为该对象单列 schema 文件并纳入 README §6 文件清单。

---

## 4. 纪律与边界自证

- 交付物状态：`CANDIDATE / FROZEN=NO / IMPLEMENTED=NO`（本文件头部已声明）。
- 本任务**仅新增本文件** `docs/dispatch/WP1_CONTRACT_VERIFICATION_CANDIDATE.md`；未修改、未 `git stash pop`、未写 `generated/`、未改任何契约文件（`specs/**`、openapi、SP-15、AC、CONTRACT_INDEX 均未动）。
- 校验临时抽取目录为仓库外的 `/tmp/wp1-verify/`，仅作只读核验用途；仓库工作树、`stash@{0}`、`specs/knowledge-architecture/schemas/` 参考 schema 均未被改动。
- 校验用工具：`python3 -m json.tool`、`jsonschema 4.19.2`（`Draft202012Validator` + `check_schema`）、`git show`/`git cat-file`/`git diff`/`grep`。

## 5. 版本记录

| 版本 | 日期 | 说明 | 作者 |
|---|---|---|---|
| CANDIDATE | 2026-08-31 | 取证（stash 落地态）+ a–e PASS/FAIL 矩阵 + 修复建议 + 补充自洽发现 | GITS/QA (WP1-1) |
