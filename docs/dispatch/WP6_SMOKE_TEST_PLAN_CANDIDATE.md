# WP6 联调冒烟计划（GITS ↔ DKWS 产品推荐三段式）

> 任务编号：WP6-5（GITS 联调冒烟准备）
> 交付类型：CANDIDATE 准备件（只新增本文与 `scripts/product-recommendation-smoke.sh`，不改动任何既有文件）
> 配套脚本：`scripts/product-recommendation-smoke.sh`

```text
STATUS=CANDIDATE
FROZEN=NO
IMPLEMENTED=NO
REAL_E2E_PASS=NO
```

---

## 0. 目的与边界

本计划用于 WP6 联调冒烟：在 **GITS（8080）与 DKWS（8106）两端均启动后**，验证产品推荐三段式（`createRun → 轮询 → stages → HG-D01 人工决定`）的跨服务契约贯通，以及 fail-closed / 幂等两条关键不变量。

**本任务是准备件，不实际启动任何服务。** 冒烟执行时两端需由联调负责人手工启动（见 §2），脚本不做任何启动动作。

**范围纪律**：以下端点状态以当前工作树为准，如实标注，不虚报“已实现”：

| 端点 | 契约权威 | 当前落地状态 |
|---|---|---|
| `POST /api/v1/product-recommendation-runs`（createRun） | `specs/openapi/product-recommendation.openapi.json`（CTR-PR-API-001，`status=CANDIDATE`） | **REST 控制器尚未接线**（应用服务 `ProductRecommendationApplicationService.createRun` 已落地，仅缺 HTTP 暴露） |
| `GET /api/v1/product-recommendation-runs/{runId}` | 同上 | 未接线 |
| `GET /api/v1/product-recommendation-runs/{runId}/stages` | 同上 | 未接线 |
| `GET /api/v1/product-recommendation-runs/{runId}/versions/{versionId}` | 同上 | 未接线 |
| `POST /api/v1/product-recommendation-runs/{runId}/retry` | 同上 | 未接线 |
| `POST /api/v1/human-gates/{gateId}/decide`（HG-D01） | `HumanGateController` + `ProductRecommendationHumanGateService` | **已接线**（`IMPLEMENTED`，WP5-2） |

> 因此冒烟脚本按 **契约（OpenAPI + 前端 `frontend/src/api/productRecommendation.ts` + HG-D01 已接线控制器）** 编写 curl 序列。`createRun/getRun/getStages` 的 REST 控制器接线完成后即可直接执行；接线完成前，脚本会以明确的 `SKIP`/`FAIL` 判定暴露该缺口，不伪装通过。

---

## 1. 验证目标

| 编号 | 目标 | 对应用例 |
|---|---|---|
| T1 | 两端健康检查贯通，`dsh.base-url` 指向正确 | §4.1 |
| T2 | `createRun → 轮询 → PROPOSAL_READY → GET stages` 全链路贯通 | §4.2 |
| T3 | HG-D01 人工决定（APPROVE）经结构化 payload 落决定并推进业务状态 | §4.3 |
| T4 | DKWS 停服时 run=`FAILED_CLOSED`，前端受控空态（INV-07 fail-closed） | §4.4 |
| T5 | 同 `Idempotency-Key` 重放返回同一 run，不重复调用 KERT | §4.5 |

---

## 2. 前置条件

### 2.1 DKWS 启动（8106）

| 项 | 值 |
|---|---|
| 地址 | `http://127.0.0.1:8106`（同机；跨机用内网 IP，**禁止把 DHCP 地址写进 GITS 配置**） |
| 启动方式 | `~/dev/Leibniz-KERT`：`.venv/bin/python scripts/serve_skill_service.py --port 8106 [--workspace <工作区>]`（默认工作区 `bank_front_ws`，脚本 `--port` 缺省 8100，联调固定 8106） |
| 健康检查 | `GET /api/skill/health`（返回 `status ∈ ok/degraded` 与 `skills[]`）；`GET /v1/health`；`GET /livez`；`GET /readyz` |
| 执行端点 | `POST /api/skill/execute`；异步轮询 `GET /v1/jobs/{jobId}` |
| 认证 | 请求头 `X-API-Key`（HTTP 头大小写不敏感）；dev 模式 `DKWS_AUTH_ENABLED=false` 可省略，prod 强制 |

### 2.2 GITS 启动（8080）

| 项 | 值 |
|---|---|
| 地址 | `http://127.0.0.1:8080` |
| 启动方式 | 二选一：`docker compose -f compose.local.yaml up -d`（api:8080 + mysql + worker:8090 + nginx:80，profile `local`）；或本地 `./mvnw -pl apps/api spring-boot:run`（默认 `application.yaml`，H2 内存库） |
| 健康检查 | `GET /actuator/health`（`{"status":"UP",...}`；`/actuator/health`、`/actuator/info` 免认证） |
| `dsh.base-url` | `application.yaml` 默认 `http://127.0.0.1:8106`，环境变量 `DSH_BASE_URL` 覆盖；空值 fail-closed（`FallbackSkillExecutionAdapter` 禁止本地补数） |

### 2.3 API Key 配置

| 端 | 配置键 | 请求头 | 联调默认 |
|---|---|---|---|
| GITS | `engagement.security.api-key`（`application-local.yaml` 为空 = 认证关闭） | `X-API-KEY` | 本地开发可省略；启用后除 `/actuator/health`、`/actuator/info` 外必须携带 |
| DKWS | `DKWS_API_KEYS` / `DKWS_AUTH_ENABLED`（`DKWS_AUTH_HEADER` 默认 `X-API-Key`） | `X-API-Key` | dev 可省略；prod 强制（密钥 ≥16 字符） |

脚本用环境变量 `GITS_API_KEY` / `DSH_API_KEY` 注入，未设置则不携带对应头。

### 2.4 工具

`curl`、`jq`（1.6+）、`uuidgen`（可选，脚本用 `$RANDOM` 兜底）。

---

## 3. 通过判据总览

- 每条用例给出“通过判据”（PASS 条件）与“失败判据”（FAIL 条件）。
- 冒烟整体 PASS 当且仅当 **全部 5 条用例 PASS**。
- 任何 KERT 失败码（`KERT_*`，见 `DKWS_GITS_CONTRACT_DIFF.md` §5）不得被脚本当作成功；缺失断言一律 FAIL，不跳过断言。

---

## 4. 用例

### 4.1 用例 1：两端健康检查

| 项 | 内容 |
|---|---|
| 步骤 | `GET $DSH_BASE_URL/api/skill/health`；`GET $GITS_BASE_URL/actuator/health` |
| 断言 | DKWS：HTTP 200 且 `.status ∈ {ok, degraded}`；GITS：HTTP 200 且 `.status == "UP"` |
| 通过判据 | 两端均 200 且断言成立 |
| 失败判据 | 任一端非 200 / 断言失败（DKWS 不可达 → 先修 DKWS，再跑其余用例） |
| 负责人 | 联调负责人（环境） |

### 4.2 用例 2：createRun → 轮询至方案就绪 → GET stages

| 项 | 内容 |
|---|---|
| 步骤 | ① `POST $GITS_BASE_URL/api/v1/product-recommendation-runs`（头 `Idempotency-Key` + `X-API-KEY`(可选)，体见下方）→ 取 `runId`；② 轮询 `GET .../product-recommendation-runs/{runId}` 至终态/超时；③ `GET .../product-recommendation-runs/{runId}/stages` |
| 请求体 | `{"customerId":"CUST-SMOKE-001","journeyId":"JOURNEY-SMOKE-001","needVersionIds":["NEEDV-SMOKE-001"],"recommendationObjective":"补充流动资金与跨境结算方案","requestedProductDomains":["FINANCING","SETTLEMENT"],"asOf":"<ISO-8601>"}` |
| 断言 | ① HTTP 200，`runId` 非空，`status` 合法（12 值枚举）；② 终态 ∈ `{AWAITING_HUMAN, PROPOSAL_READY}`（`PROPOSAL_READY` 为瞬态，`AWAITING_HUMAN` 是持久落点，二者均视为“方案就绪”），`currentVersionId` 非空；③ `GET stages` HTTP 200，`.runId == runId`，`.status` 与 run 一致 |
| 通过判据 | 三步全部成立，且轮询未超时（`dsh.async-poll-timeout-ms`=180000 内） |
| 失败判据 | ① 非 200 / 缺 runId；② 轮询超时或终态 ∈ `{FAILED_CLOSED, HELD, STALE_REQUIRES_RERUN}`；③ stages 404 或 `.runId` 不匹配 |
| 负责人 | 后端工程师（GITS 侧）+ 联调负责人（KERT 侧） |

> 说明：`stages` 组合视图的数组字段（`eligibilityResults/fitResults/portfolioCandidates/needProfile/unknowns/conflicts`）对齐 `ProductRecommendationStageResult`（OpenAPI）。KERT 侧 `data.result` = `ProductRecommendationResult`（8 个必填字段：`schemaVersion/runId/productKnowledgeSnapshotRef/ruleExecutionRef/evidenceBundleId/contentHash/traceId/generatedAt`，见 `skill-execute-api-contract-vNext.md` §4.1），GITS 侧据此固化 `ProductRecommendationProposalVersion`。

### 4.3 用例 3：HG-D01 人工决定（APPROVE）

| 项 | 内容 |
|---|---|
| 步骤 | `POST $GITS_BASE_URL/api/v1/human-gates/HG-D01/decide`，体见下方 |
| 请求体 | `{"runId":"<runId>","proposalVersionId":"<currentVersionId>","expectedVersion":"<currentVersionId>","decision":"APPROVE","actorId":"RM-SMOKE-001","actorRole":"RELATIONSHIP_MANAGER"}` |
| 断言 | HTTP 200；返回体含 `.decision == "APPROVE"`、`.runId == runId`、`.proposalVersionId == currentVersionId`；随后 `GET .../{runId}` 的 `status ∈ {APPROVED}` |
| 通过判据 | 决定落库 + run 业务状态推进为 `APPROVED` |
| 失败判据 | 非 200（409 版本过期 / 403 权限 / 422 前置失败 / 400 校验失败）或 run 未推进 |
| 负责人 | 后端工程师（GITS 侧） |

> 语义映射（`RecommendationExceptionHandler`）：`RecommendationVersionConflictException` → 409（If-Match/ETag 过期）；`PERMISSION_DENIED` → 403；其余前置失败 → 422。`decision ∈ {APPROVE, MODIFY, REJECT, HOLD}`；`REJECT/HOLD` 必须携带 `reason`；`MODIFY` 必须携带 `modifications`。

### 4.4 用例 4：DKWS 停服 → run=FAILED_CLOSED + 前端受控空态

| 项 | 内容 |
|---|---|
| 前置 | 联调负责人先 **手工停止 DKWS**（`kill <pid>` 或 `docker compose stop`），GITS 保持运行 |
| 步骤 | ① 换新 `Idempotency-Key`，`POST .../product-recommendation-runs`（同一请求体模板）；② 轮询 `GET .../{runId}` 至终态/超时；③ 前端打开 `ProductRecommendationWorkspace` 验证空态 |
| 断言 | ① createRun 成功建 run（HTTP 200，run 已落库）；② 轮询终态 == `FAILED_CLOSED`（KERT 不可达 → `SkillExecutionException` → `onKertFailure("KERT_INTERNAL_ERROR")` → `FAILED_CLOSED`，不本地补数）；③ 前端不崩溃，渲染 `data-testid="kert-unreachable"` 受控空态（文案：受控失败空态 INV-07 fail-closed） |
| 通过判据 | run=`FAILED_CLOSED` 且前端受控空态（`isKertUnreachable` 命中：无响应或上游 502/503/504） |
| 失败判据 | run 卡在中间态 / 落到 `HELD` 之外的乐观态 / 前端抛未捕获异常或渲染本地“推荐结果” |
| 负责人 | 联调负责人（停服）+ 前端工程师（空态）+ 后端工程师（FAILED_CLOSED） |

> 脚本默认不覆盖用例 4 的停服动作（脚本“不自动启动/不自动停止服务”）。脚本提供 `FAIL_CLOSED=1` 模式：在 DKWS **已由人工停止** 后执行，只验证 ①②（后端 FAILED_CLOSED）；③ 前端空态由前端工程师浏览器手工验证。

### 4.5 用例 5：同 Idempotency-Key 重放返回同 run

| 项 | 内容 |
|---|---|
| 步骤 | 用与用例 2 相同的 `Idempotency-Key` **再次** `POST .../product-recommendation-runs`（体可完全相同或仅 `asOf` 相同） |
| 断言 | HTTP 200；`.runId` 与首次返回 **完全相等**；`.idempotencyKey` 与首次一致；KERT 侧不产生第二次执行（GITS `createRun` 幂等命中 `findRunByIdempotencyKey` 直接返回） |
| 通过判据 | 两次 `runId` 相等，无重复 KERT 调用 |
| 失败判据 | 返回不同 `runId` / 409 语义误用 / 触发第二次 KERT 执行 |
| 负责人 | 后端工程师（GITS 侧） |

> 幂等范围（`product-recommendation-run.schema.json`）：`caller + customerId + journeyId/operatingCaseId + objectiveHash + asOf + Idempotency-Key`。

---

## 5. 失败回滚与清理

冒烟为**只读 + 新建业务数据**，无外部写回（不写 CRM、不触发授信/定价/审批），清理以“标记 + 重启”为主：

1. **冒烟数据清理（可选）**：删除/标记本轮测试 run（`customerId=CUST-SMOKE-001` 相关 `ProductRecommendationRun` 与 `RecommendationHumanDecision` 记录）。本地 H2 内存库重启即清空；MySQL profile 由联调负责人用 SQL 清理，**禁止**删除非 `CUST-SMOKE-*` 前缀数据。
2. **DKWS 回滚**：用例 4 后若需恢复，重新 `serve_skill_service.py --port 8106`；等待 `GET /api/skill/health` 返回 `ok` 再继续。
3. **GITS 回滚**：异常时查 `apps/api` 日志（`/tmp/gits-demo.log` 或容器日志），按需重启；`dsh.base-url` 配置错误时以 `DSH_BASE_URL` 覆盖重启。
4. **不执行任何** `git checkout` / `stash` / 回滚基线或他人文件的动作。

---

## 6. 负责人

| 角色 | 职责 |
|---|---|
| 联调负责人 | 环境起停（DKWS 8106 / GITS 8080）、API Key 配置、用例 4 停服/恢复、失败上报 |
| 后端工程师（GITS） | createRun/stages/HG-D01/幂等/FAILED_CLOSED 的后端断言与修复 |
| 前端工程师（GITS） | 前端受控空态（INV-07 fail-closed）验证 |
| 测试负责人 | 记录 `testEvidence`（命令 + 结果），判定整体 PASS/FAIL |

---

## 7. 契约与实现引用（取证来源）

- GITS：`compose.local.yaml`、`apps/api/src/main/resources/application.yaml`（`dsh.base-url`）、`application-local.yaml`、`apps/api/.../HumanGateController.java`、`ProductRecommendationApplicationService.java`、`ProductRecommendationHumanGateService.java`、`RecommendationExceptionHandler.java`、`ApiKeyAuthenticationFilter.java`、`specs/openapi/product-recommendation.openapi.json`、`specs/CONTRACT_INDEX.yaml`、`frontend/src/api/productRecommendation.ts`、`frontend/src/stores/useProductRecommendationStore.ts`、`frontend/src/views/ProductRecommendationWorkspace.vue`
- DKWS：`docs/integration/DKWS_GITS_CONTRACT_DIFF.md`、`docs/integration/DKWS_GITS_STATE_MAPPING_CANDIDATE.md`、`docs/DEPLOYMENT.md`、`docs/skill-execute-api-contract-vNext.md`、`scripts/serve_skill_service.py`、`deploy/smoke_test.sh`

---

## 8. 状态块（重申）

```text
STATUS=CANDIDATE
FROZEN=NO
IMPLEMENTED=NO
REAL_E2E_PASS=NO
```

本计划与脚本均为**候选准备件**，未冻结、未在真实两端联调中执行。允许的下一步：在 `createRun/getRun/getStages` REST 控制器接线完成后，由联调负责人按 §2 启动两端，执行 `scripts/product-recommendation-smoke.sh` 并回填 §6 的 `testEvidence`。
