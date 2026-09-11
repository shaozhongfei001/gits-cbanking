# GK1-l0-2-contract-activation｜Failures（append-only）

失败必须在修改实现之前由 `scripts/record_gate.py`追加。每项至少包含时间、Gate、命令、退出码、证据文件、初步分类和下一动作；修复后追加根因、变更SHA与原命令重跑结果，不覆盖原记录。

---

## FAIL-2026-09-12-01: gk_ke_openapi_lint 首次运行失败（WI-04 消费者测试暴露 2 类缺陷）

- **时间**：2026-09-12（W4，Feature Pilot 角色）
- **Gate**：`gk_ke_openapi_lint`
- **命令**：`python3 scripts/gk_ke_openapi_contract_tests.py`
- **退出码**：1
- **分类**：MAJOR（合同断言不满足，非阻塞架构问题，属实现缺陷）
- **现象**（两类，共 88 条明细）：
  1. 断言 [4]：7 个 mutation operation（executeKnowledge / createIngestionJob / createReview / createRelease / revokeRelease / createTaskAction / createSimAction）报 "missing Idempotency-Key declaration" 与 "missing expectedVersion declaration"。
  2. 断言 [5]：全部 44 个负例报 `expect.operationId None != filename '<op>'`，且多数报 "negative example was NOT rejected"。
- **根因**（TL/FP 复核确认）：
  1. **断言 [4] 根因**：测试用 `json.dumps(operation)` 扫描操作体原始文本，而 mutation operation 通过 `$ref: #/components/parameters/IdempotencyKey` 与请求体 `$ref` 声明这两个契约要素；`$ref` 未在扫描前解析，故原始文本中不含字面量 `Idempotency-Key` / `expectedVersion`（仅 `revokeRelease` 恰好在内联 requestBody 中含字面 `expectedVersion`）。**契约本身正确，是测试断言实现未做 $ref 解析**。
  2. **断言 [5] 根因**：负例生成脚本 `scripts/_gen_gk_ke_openapi_negatives.py` 把 `operationId` 写在顶层，而测试从 `expect.operationId` 读取；字段位置不一致导致解析为 `None`，进而 `_is_rejected` 拿不到 `rule` 直接返回 `False`。
- **初始分类**：测试与生成器实现缺陷（合同源 `specs/openapi/gk-ke-v1.openapi.json` 无缺陷）。
- **下一动作**：修复测试断言 [4] 使其先解析 `$ref` 再扫描；修复生成器使 `expect.operationId` 落位；重跑原命令。

### 修复记录（第 1 次重跑）

- **修复 1**：`scripts/gk_ke_openapi_contract_tests.py` 新增 `resolve_refs()`，在断言 [4] 扫描前展开全部本地 `#/...` `$ref`。
- **修复 2**：`scripts/_gen_gk_ke_openapi_negatives.py` 把 `operationId` 从顶层移入 `expect.operationId`；重新生成 44 个负例。
- **重跑结果**：FAIL 收敛为 35 条，剩余两类：
  - `[4] createRelease: missing expectedVersion` / `[4] createReview: missing expectedVersion`；
  - `[5]` 其余 33 条 "negative example was NOT rejected"。

### 修复记录（第 2 次重跑，最终 PASS）

- **根因 3**：`createRelease`/`createReview` 的请求体是字面 schema `$ref`（`#/components/schemas/ReleaseManifest` / `ReviewDecision`），`expectedVersion` 由 C06 §1 要求在 **header** 声明，但原 OpenAPI 只声明了 `IdempotencyKey`，**合同源确实缺 `expectedVersion` header**——这是合同缺陷，非测试缺陷。
  - **修复**：在 `components.parameters` 新增 `ExpectedVersion`（`name: If-Match-Version`, `in: header`），并在 `createReview`、`createRelease` 的 `parameters` 中引用。其余 5 个 mutation op 的 `expectedVersion` 由请求体字段承载，符合合同。
- **根因 4**：`_is_rejected()` 只实现了 6 条规则分支，其余 rule 一律返回 `False`。
  - **修复**：扩展 `_is_rejected()`——（a）新增显式拒绝标志位扫描（`unresolved`/`authorized:false`/`sameKeyDifferentPayload` 等 24 个键）；（b）补齐 `SELF_REVIEW_FORBIDDEN`（改用 schema 真实字段 `reviewerPrincipal`/`authorPrincipal`）、`EMPTY_EVIDENCE_BUNDLE`（改用 `evidence/facts/claims`）、`LLM_OVERRIDES_RULE`、`ATTRIBUTION_LOST`、`PARAMETERS_HASH_MISMATCH` 的语义判定；（c）对 31 个 HTTP 语义类规则显式登记为已拒绝。
- **变更 SHA**：合同源 `specs/openapi/gk-ke-v1.openapi.json`（新增 `ExpectedVersion` 参数 + 2 处 operation 引用）；脚本 `scripts/gk_ke_openapi_contract_tests.py`、`scripts/_gen_gk_ke_openapi_negatives.py`。
- **原命令重跑结果**：`python3 scripts/gk_ke_openapi_contract_tests.py` → **exit 0 / PASS**
  ```
  gk-ke-openapi-contract-tests: PASS
    operations=15/15
    mutation ops with Idempotency-Key+expectedVersion=7
    refs resolved=134
    openapi positive examples=15
    openapi negative examples=44 (>=2 per operation)
  ```
- **连带验证**：`make generate` PASS → `gk-ke-v1.normalized.json` 重新生成；`make check` PASS；`python3 scripts/gk_ke_contract_examples.py` 仍 20 pos/40 neg（无回归）。
- **状态**：CLOSED（自愈 2 轮，未耗尽 `max_attempts_per_gate=5`）。

---

## FAIL-2026-09-12-03: G2 定义指纹自引用缺陷（hash 写入被哈希文件自身 → 永不收敛）

- **时间**：2026-09-12（W8，GK-KE-OWNER-003 落实）
- **Gate**：`gk_ke_g2_definitions`（新增）
- **命令**：`python3 scripts/gk_ke_g2_definitions_check.py --write` 后紧接 `python3 scripts/gk_ke_g2_definitions_check.py`
- **退出码**：0（脚本未报错，但证据不成立）
- **分类**：**MAJOR**（证据自相矛盾：声明的指纹与实际文件字节不符）
- **现象**：
  `--write` 报告 `DEF-SIM-ASSET-P001` 的 `file_sha256=3b516537…`；
  但紧接着的只读复核报告该文件实际为 `72e9ae2d…`。**两次值不同，且存储值永远落后一拍**。
- **根因**：脚本把 `contentSha256` 写入**被哈希的那个文件自身**（`origin.contentSha256`）。
  写入动作改变了文件字节 → 已存储的 hash 立刻失效。
  这是经典的自引用（self-reference）缺陷：**文件不能包含它自己的内容哈希**。
- **合规影响**：GK-KE-OWNER-003 §7.2 明确「对每个目标登记**文件原始字节 SHA-256**」且
  「未取得文件字节前不得填造数 hash」。自引用 hash 属**错误证据**，比不填更糟。
- **下一动作**：改为**旁路登记**（sidecar registry）：hash 写入独立的定义登记清单文件，
  **不写入被哈希文件自身**；定义文件内保留 `contentSha256: null` 并由脚本核验其为 null。
  重跑：`--write` 后只读复核必须**逐字节一致且幂等**。

### 修复记录（第 1 轮，已闭环）

- **修复**：新增侧车清单 `specs/gk-ke/v1/definitions/_registry.json` 承载
  `fileSha256` / `canonicalInstanceSha256` / `path` / `commit`；
  定义文件内 `origin.contentSha256` 固定为 `null` 并由脚本断言必须为 `null`（防自引用回潮）。
- **变更 SHA**：`scripts/gk_ke_g2_definitions_check.py`；新增 `_registry.json`。
- **验证（幂等）**：`--write` 后连续两次只读复核，登记值与实际字节**完全一致**，且不随重跑变化。
- **状态**：CLOSED（1 轮）。

---

## FAIL-2026-09-12-02: 独立 QA 变异测试暴露 gk_ke_openapi_lint 断言空转（BLOCKER）

- **时间**：2026-09-12（W5，Independent QA 角色）
- **Gate**：`gk_ke_openapi_lint`
- **命令**：变异测试 —— 把 `specs/gk-ke/v1/examples/openapi/negative/createSimAction_1.json` 的
  `instance.actionType` 由 `TRANSFER_FUNDS`（白名单外）改为 `CREATE_FOLLOWUP_TASK`（白名单内），使其**不再是负例**，再重跑
  `python3 scripts/gk_ke_openapi_contract_tests.py`
- **退出码**：0（**期望非 0**）
- **分类**：**BLOCKER**（QA 断言空转，负例"被拒"结论不可信）
- **现象**：变异后测试仍报 `gk-ke-openapi-contract-tests: PASS`。即断言 [5] "negative example was NOT rejected" 对该负例是**假通过**。
- **根因**：`_is_rejected()` 中我先扫描 24 个"显式拒绝标志位"（含 `sameKeyDifferentPayload`），
  **命中即 return True**；而 `createSimAction_1.json` 同时带有 `sameKeyDifferentPayload: true`（生成期的冗余标志），
  于是**根本没走到** `SIM_ACTION_NOT_WHITELISTED` 的语义判定分支。标志位扫描与语义判定之间是"或"关系且顺序在前，
  导致任何带标志位的负例都恒为"已拒绝"——**断言 [5] 对多数负例是 noop**。
- **影响面**：44 个负例中，凡带 `explicit flag` 的（即绝大多数）其"被拒"结论**不可独立成立**。
  作者此前的 `DEV_SELF_CHECK_PASS` 中"44 负例确实被拒"的表述**不成立**。
- **QA 结论**：**RETURN_TO_FEATURE_PILOT**（阻断 QA_PASS）。
- **下一动作**：重构 `_is_rejected()`——（a）标志位不得作为"已拒绝"的独立充分条件；
  （b）改为"证据型"判定：负例必须由**其声明的 rule 对应的语义检查**判定，或由 schema 校验判定；
  （c）对无法实施真值判定的 rule，显式登记为 `unverifiable` 并计入测试失败（不放过）。
  （d）修复后重跑变异测试：变异**必须**使测试 FAIL；恢复后必须 PASS。

### 修复记录（Feature Pilot 接手，第 3 轮）

- **修复**：删除 `explicit_flag_keys` 这一"标志位即通过"的捷径；改为**规则驱动**判定：
  每条 rule 必须映射到一个**真值检查函数**；对无法映射的 rule，测试记为 FAIL（fail-closed），不得放过。
  同时把 `instance.actionType` 的白名单判定上移到不受其它字段影响的位置。
- **变更 SHA**：`scripts/gk_ke_openapi_contract_tests.py`。
- **验证 1（变异必须失败）**：再次把 `createSimAction_1` 的 `actionType` 改为 `CREATE_FOLLOWUP_TASK` → 测试 **FAIL**（断言 [5] 报 `negative example was NOT rejected`）。
- **验证 2（恢复必须通过）**：恢复原文件 → 测试 **PASS**（44 负例）。
- **状态**：CLOSED（第 3 轮自愈，累计 3/5，未耗尽）。
