# L13 FAILURES

> Loop: `L13-release-interpretation-api` · 建立 2026-09-06

---

## F-L10-01 · MAJOR · **RESOLVED（本 Loop 修复）**

**标题**：`make check` / `make generate` 失败，报 `CTR-PR-API-001: exactly one normalized target required`

**来源**：L00 首次真实执行发现，早于 L10 施工。L13 需要 `make generate` 产出解读端点制品，
该缺陷成为**直接阻塞**，故在本 Loop 定位并修复。

**根因（两层）**：
1. **合同登记缺陷**：15 条 CANDIDATE 合同（`CTR-PR-*` 6 条 + `CTR-PK-*` 8 条 + `CTR-PK-TAX-001`）
   在 `specs/CONTRACT_INDEX.yaml` 中 `generated: []`，而生成管线要求
   `kind ∈ {openapi, openapi_paths, asyncapi, json_schema, source_contract_instance}` 必须
   有且仅有 1 个 normalized 目标。此前从未有人真正跑通 `make generate`，故一直未被发现。
2. **管线能力缺口**：`CTR-PK-TAX-001` 的 `kind=yaml_taxonomy` 不在支持列表内。

**修复**：
- 15 条合同按 `generated/<specs 子目录>/<文件名>` 约定补齐目标；
- `contract_pipeline.py` 增加 `yaml_taxonomy` 分支（YAML 加载 + `domains`/`families` 校验 + 写目标）；
- `CTR-PK-INT-001` 的 OpenAPI 版本由 3.0.3 升为 3.1.1（管线要求）。

**验证**：
```
contract-generate: PASS
generated/openapi/gits-kno-api.normalized.json：paths 53 → 54（含新解读端点）
```

**遗留**：`make check` 的 `contract-check` 已 PASS，但整体仍在下一步失败（见 F-L13-01）。

---

## F-L13-01 · BLOCKER · **RESOLVED**（既有，非本 Loop 引入；2026-09-07 Owner 选路径 A 后修复）

**标题**：`make check` 在 `knowledge-architecture-check` 失败：`SP-15.json: unknown asset dependency ASSET-KNOW-PRODUCT-RULES`

**证据**：`specs/knowledge-architecture/skills/SP-15.json` 与
`activations/AC-PRODUCT-RECOMMEND-001.json` 均引用 `ASSET-KNOW-PRODUCT-RULES`，
但 `specs/knowledge-architecture/assets/` 下无该资产定义（目录下无任何 json 定义文件）。

**是否本 Loop 引入**：否。该依赖早于本计划存在；此前 `make check` 在 `contract-check`
阶段即失败，从未执行到本步骤，故首次暴露。

**处置**：**不擅自修补** —— 资产注册表属 `knowledge_architecture_owner` 域，
擅自新增资产定义会改变 P22/P23 的资产图与激活链路，超出 L10–L13 scope。
登记为 BLOCKER，交 Owner / 独立 QA 裁决：
  - 选项 A：注册 `ASSET-KNOW-PRODUCT-RULES` 资产（需定义其规范与来源）；
  - 选项 B：从 SP-15 依赖清单移除（若规则包改由 KERT Release 承载）。

---

## O-L13-01 · OBSERVATION · OPEN

**标题**：解读 API 当前对 PROD-CM-001 返回 404 而非 200

**说明**：Release 为 DRAFT（未获 Owner 签署），按 INV-CNF-02 / 红线，
未发布知识**不得**呈现，故 404 `PRODUCT_KNOWLEDGE_NOT_PUBLISHED` 是**正确行为**，非缺陷。

**解除路径**：Owner 签署决策 → `python3 tools/l13_publish_release.py --decisions <file>`
→ Release 转 PUBLISHED → API 返回 200。
注意：即使发布，`interpretationReady` 仍受 3 个 HARD 阻断约束（L12），
需 Owner 先裁决冲突与 UNKNOWN 字段方可变为 true。

---
---

# 独立 QA（E2E Owner）真实端到端验收 · 2026-09-07

> 方法：真实启动 `apps/api`（`spring-boot:run`） + 真实 HTTP 调用，非代码审阅。
> 实例 A：`--server.port=8087 --gits.product-knowledge.snapshot-dir=<KERT 真实 04_serve/interpretation>`（S1–S7 / S11 / S12）
> 实例 B：`--server.port=8088 --gits.product-knowledge.snapshot-dir=/tmp/e2e-l13/snap`（S8–S10 受控失败，临时目录，不污染已发布投影）
> 投影完整性校验：验收后 `PROD-CM-001.json` md5 = `6da49bb4a7b235d21883c0ed4c773ec5`，与验收前一致；`git status` 对 `04_serve/` 无改动。
> 原始证据：`loops/L13-release-interpretation-api/evidence/e2e-2026-09-07/`
> **结论：`REAL_E2E_PASS = NO`（S8 未通过）。未记录 `QA_PASS`。**

---

## F-L13-02 · MAJOR · **OPEN**（本轮 E2E 发现）

**标题**：快照目录不可达时受控失败被降级为 404，未按行为矩阵返回 503 `FAILED_CLOSED`

**场景**：S8

**复现**：
```
# 实例 B 指向 /tmp/e2e-l13/snap，随后 rm -rf 该目录
GET /api/v1/product-knowledge/PROD-CM-001/interpretation?view=ELIGIBILITY&purpose=INTERPRETATION
```

**期望**：`503` + `code=FAILED_CLOSED`，且响应体不含任何本地兜底结论

**实际**：
```json
{"status":404,"error":"Not Found","code":"PRODUCT_KNOWLEDGE_NOT_PUBLISHED",
 "message":"PROD-CM-001 无已发布 Release（legacy sample 卡不可消费）",
 "path":"/api/v1/product-knowledge/PROD-CM-001/interpretation",
 "timestamp":"2026-09-06T16:06:10.387468980Z"}
```

**部分通过**：受控失败语义守住了 —— 响应体未出现 `fields` / `displayValue` / `knowledgeState` / `50 万元` / `bundleHash` 任一本地兜底令牌（`leakedTokens=[]`）。**未违反「禁止本地兜底」红线。**

**根因**：`KertReleaseSnapshotAdapter.load()` 仅以 `Files.isRegularFile(file)` 判定。
「快照目录不存在 / 不可读」与「目录存在但该产品无投影」走同一分支，均返回 `Optional.empty()`，
控制器统一映射 404；只有 `snapshot-dir` 为空串、或 JSON 解析失败才抛 `KnowledgeSourceUnavailableException`（503）。

**影响**：语义混淆。`404` 的语义是「已确认该产品无已发布 Release」，而源不可达时系统**无法确认任何事**。
调用方/运维无法区分「确实没有」与「知识源暂时不可用」，可观测性受损；告警与重试策略会误判。
不产生错误结论（fail-safe），故定 MAJOR 而非 BLOCKER。

**为何 961 单测未捕获**：`ProductInterpretationControllerTest#knowledgeSourceUnavailableReturns503FailedClosed`
直接 stub Port 抛异常，**未覆盖 Adapter 层「目录缺失」路径**；6 项测试全部为控制器层 stub，无适配器集成测试。

**处置建议（E2E Owner 不改实现，退 Feature Pilot）**：
区分 `Files.isDirectory(snapshotDir)` 不可读/不存在（→ 503 `FAILED_CLOSED`）与文件缺失（→ 404），
并补一条 Adapter 级集成测试锁定该分叉。

---

## F-L13-03 · MAJOR · **OPEN**（本轮 E2E 发现）

**标题**：`view` / `purpose` 未做合同枚举校验，非法 `view` 返回 200 且响应体携带合同外枚举值

**场景**：额外探针（合同合规）

**实际**：
```
GET ...?view=BOGUS&purpose=INTERPRETATION
→ 200 {"productId":"PROD-CM-001","releaseId":"RLS-2026.09.06.1","bundleHash":"8e99d770…",
       "view":"BOGUS","purpose":"INTERPRETATION","isStale":false,"fields":[],"generatedAt":"…"}

GET ...?view=ELIGIBILITY&purpose=BOGUS
→ 422 {"code":"PURPOSE_NOT_ALLOWED","message":"Release RLS-2026.09.06.1 不允许用于 BOGUS 用途",…}
```

**违反**：`CTR-PK-INT-001` 中 `parameters.view.enum` 与 `InterpretationResponse.view.enum`
均为 `["OVERVIEW","ELIGIBILITY","PRICING"]`；响应体出现 `"view":"BOGUS"` 直接违反响应 schema 枚举。

**影响**：`view` 拼写错误时静默返回空字段数组。与本 API「禁止留白猜测」的设计目标相悖 ——
前端按四态规范渲染为空态而非报错，用户看到「无字段」而非「请求有误」。
`purpose=BOGUS` 落到 422 属 fail-closed（无害），但错误码语义错误：非法枚举值应为 `400 BAD_REQUEST`，
`PURPOSE_NOT_ALLOWED` 在合同中语义是「仅候选或公开轨知识」。

**处置建议**：`normalizeEnum` 增加白名单校验，非法值抛 `400 BAD_REQUEST`。

---

## F-L13-04 · MINOR · **OPEN**（本轮 E2E 发现）

**标题**：缺少必填 query 参数时返回非统一错误结构

**实际**：
```
GET /api/v1/product-knowledge/PROD-CM-001/interpretation        # 不带 view/purpose
→ 400 {"errorCode":"INVALID_ARGUMENT",
       "message":"Required request parameter 'view' for method parameter type String is not present",
       "timestamp":"2026-09-06T16:04:04.660283676Z"}
```

**违反**：后端兜底规范 §2 —— 错误响应须含 `status` / `error` / `message` / `path` / `timestamp`；
本响应缺 `status` / `error` / `code` / `path` 四字段，且字段命名风格（`errorCode`）与全局不一致
（该路径走 Spring 默认参数绑定异常，未被本控制器或全局 `@ExceptionHandler` 覆盖）。

**说明**：S11 的三个用例（422/404/400 业务错误码路径）**全部 PASS**，本项仅影响框架级参数绑定错误。

---

## F-L13-05 · MINOR · **OPEN**（合同缺口）

**标题**：`CTR-PK-INT-001` 未定义 `400` 响应，而实现实际返回 400

**证据**：`specs/product-knowledge/interpretation-api.openapi.json` 的
`paths./api/v1/product-knowledge/{productId}/interpretation.get.responses` 仅有
`["200","404","409","422","503"]`，无 `400`。

**冲突**：S7（非法 productId）期望 400，实现也确实返回 400，属**实现正确、合同缺失**。
违反 API-First：端点行为未被合同覆盖。

**处置建议**：Tech Lead 在 `CTR-PK-INT-001` 增补 `400` + `ErrorResponse`，
并在 `ErrorResponse.code` 枚举中补 `BAD_REQUEST`（当前枚举仅 5 项，不含 `BAD_REQUEST`，
而实现实际使用该码 → 亦违反自身 schema）。

---

## F-L13-06 · MINOR · **OPEN**（KERT 侧投影数据质量，非 GITS 实现缺陷）

**标题**：投影 `evidenceSummaries` 存在重复条目 —— 9 条实为 4 个去重 evidenceId

**证据**（`04_serve/interpretation/PROD-CM-001.json` → `views.ELIGIBILITY[1].evidenceSummaries`）：
```
EVS-SRCCM001-7d3f83e8 ×3   EVS-SRCCM001-b92956e2 ×2
EVS-SRCCM001-b8dc5f5f ×2   EVS-SRCCM003-4302d512 ×2   （total=9, distinct=4）
```

**影响**：GITS 原样透传，前端回链列表会重复渲染同一条证据 2–3 次；
不影响可追溯性（S12 全量回链校验仍 PASS）。

**归属**：KERT 投影生成环节（`04_serve/interpretation/PROD-CM-001.json`），非 GITS 控制器引入。

---

## O-L13-03 · OBSERVATION · **OPEN**

**标题**：`SUPPORTED` 字段携带 `conflictId`，且其证据集中含相反数值原文

**证据**：
```json
{"fieldPath":"eligibility.minAccountBalance","knowledgeState":"SUPPORTED",
 "displayValue":"50 万元","conflictId":"CNF-PRODCM001-757c6c3b",
 "evidenceSummaries":[ … 9 条 … 其中 EVS-SRCCM003-4302d512（SRC-CM-003 第六条）
   原文为「集团现金池主账户每日最低留存余额为人民币 100 万元，高于单一客户现金池标准…」]}
```

**说明**：Owner 裁决 `DEC-20260906-11111111` 已采纳 50 万元，保留冲突证据具备可追溯价值 —— 可能是预期行为。
但 `CTR-PK-INT-001` 未定义不变式约束「`SUPPORTED` 是否允许携带 `conflictId` / 含相反数值证据」，
前端也无法从 schema 判断该字段是否应同时展示冲突提示。

**建议**：Tech Lead 在 `CTR-PK-INT-001` 增补不变式明确该组合为预期或禁止；在明确前不作为缺陷计。

---

## 本轮 E2E 通过项摘要（供对照，未单独立条）

S1 / S2 / S3 / S4 / S5 / S6 / S7 / S9 / S10 / S11 / S12 / S13 / S14 全部 PASS。
UI 层 E2E：**NOT_APPLICABLE** —— `frontend/src` 内无任何代码调用
`/api/v1/product-knowledge/{productId}/interpretation`（`v11.ts` 中的 `/product-knowledge/*` 为版本列表/详情，
与本端点无关），本计划未改前端，无 UI 对象可验。

---

## 修复波次（2026-09-07 · Feature Pilot 承接，E2E 退办后）

> 角色说明：本环境可用 subagent 仅 `code-explorer`（只读），无写权限的施工 agent。
> 按红线「E2E Owner 不得改实现」，由 Feature Pilot 波次承接实现修改，
> 复核结果**仍需独立 QA 复审**，dev 侧不自签 QA_PASS、不改写 REAL_E2E_PASS。

### F-L13-02 · MAJOR · **RESOLVED**

**根因**：`KertReleaseSnapshotAdapter.load()` 只判 `Files.isRegularFile(file)`，
「目录不存在」与「产品无投影」同分支返回 `Optional.empty()` → 统一 404。

**修复**：目录为 null / 非目录 / 不可读 → 抛 `KnowledgeSourceUnavailableException`（503）；
目录可达但产品文件缺失 → `Optional.empty()`（404）；解析失败仍 503。

**补测**：新增 `KertReleaseSnapshotAdapterTest`（5 项，真实文件系统）：
目录缺失、未配置、文件缺失、JSON 损坏、正常加载。
此前 503 用例只在控制器层 stub Port，结构性覆盖不到目录分支 —— 正是 E2E 指出的漏网点。

**验证**：S8 由 404 → **503 FAILED_CLOSED**，且响应体无 `fields/displayValue/knowledgeState/bundleHash/50 万元` 泄漏。

### F-L13-03 · MAJOR · **RESOLVED**

**修复**：`view` / `purpose` 增加合同枚举白名单，非法取值 → 400 `BAD_REQUEST`。
新增 S15-view / S15-purpose 两项测试。

**验证**：`view=BOGUS` → 400（此前 200 + 空 fields）；`purpose=BOGUS` → 400（此前 422 错码）。

### F-L13-04 · MINOR · **RESOLVED**

**修复**：Controller 增加 `@ExceptionHandler(MissingServletRequestParameterException)`，
返回含 `status/error/code/message/path/timestamp` 的统一错误体。

**验证**：缺 `purpose` → 400 `BAD_REQUEST`，六字段齐备（S16）。

### F-L13-05 · MINOR · **RESOLVED**

**修复（合同先行）**：`CTR-PK-INT-001` 与主 OpenAPI 均补 400 响应；
`ErrorResponse.code` / `ProductKnowledgeErrorResponse.code` 枚举补 `BAD_REQUEST`；`make generate` PASS。

### F-L13-06 · MINOR · **RESOLVED**

**根因**：投影生成遍历该字段**全部**断言的证据（CONFLICT 与 SUPPORTED 叠加），
9 条摘要实为 4 个去重 evidenceId。

**修复**：投影只取「当前有效断言」（状态优先级取末端）的证据，并按 evidenceId 去重。

**验证**：`minAccountBalance` 摘要 9 → **1 条**（采信证据），无重复（S17）。
代价：被否决的相反证据（100 万元）不再出现在该字段下 —— 与「SUPPORTED 只由采信证据支撑」一致，
冲突溯源由 `conflictId` 承担（见 O-L13-03）。

### O-L13-03 · OBSERVATION · 保留 OPEN

SUPPORTED 字段携带 `conflictId` 且历史证据集含相反数值。合同未定义该不变式。
本轮**不擅自增加约束**，交 Contract Owner 裁决：是否要求 `SUPPORTED` 断言清空 `conflictId`。

### 复核数据（dev 侧自测，非 QA 结论）

```
场景集 20/20 PASS（含 S8=503、S15/S16 新增）
统一门禁 11/11 · 后端 968 tests / 0 failure（基线 955 + 新增 13）
后端测试数：961 → 968
```

---
---

# 独立 QA 复审结论（2026-09-07 · session `qa-l13-e2e-2026-09-07-002`）

> 复审基线：GITS `feature/PI-ARCH-L10-L13` @ `972756c` · KERT @ `0a3a51d`
> 方法：真实 `spring-boot:run` 双实例 + 真实 HTTP 调用（实例 A `:8087` 真实投影；实例 B `:8088` 临时目录受控失败）
> **结论：`REAL_E2E_PASS = YES`，记录 `QA_PASS`。**

## 复审判定汇总

| # | 场景 | 判定 | 实际响应要点 |
|---|---|---|---|
| S8 | 快照目录不存在 | **PASS** | `503` `{"code":"FAILED_CLOSED","message":"KERT 解读快照目录不可达: /tmp/e2e-l13/snap"}`；`leakedTokens=[]` |
| S8b | 目录存在但 `chmod 000` | **PASS** | `503 FAILED_CLOSED`（复审新增变体，非 dev 自测范围） |
| S8c | 路径指向普通文件 | **PASS** | `503 FAILED_CLOSED`（复审新增变体） |
| S8r | 目录可达但产品无投影 | **PASS** | `404 PRODUCT_KNOWLEDGE_NOT_PUBLISHED` —— **404 与 503 已正确分离，未因修复而误伤** |
| S15 | `view=BOGUS` | **PASS** | `400 BAD_REQUEST`「view 取值非法: BOGUS（允许 PRICING/ELIGIBILITY/OVERVIEW）」 |
| S15 | `purpose=BOGUS` | **PASS** | `400 BAD_REQUEST`（此前 422 `PURPOSE_NOT_ALLOWED` 错码） |
| S16 | 缺 `purpose` | **PASS** | `400`，六字段 `status/error/code/message/path/timestamp` 齐备（`missing=[]`）；缺 `view`、两者皆缺同样齐备 |
| S17 | 证据去重 | **PASS** | `minAccountBalance` 摘要 `total=1 / distinct=1 / duplicated=false`（此前 9/4） |
| S1–S7 | 主链路回归 | **PASS** | 三视图 200（`fields` 为 array，2/3/1 项）；`SUPPORTED` + `"50 万元"` + `第十条` 回链且原文可定位；三字段 `UNKNOWN` 不补值；无 `CANDIDATE`；`422`/`404`/`400` |
| S9 / S10 | 损坏 / stale | **PASS** | `503 FAILED_CLOSED` / `409 RELEASE_STALE` |
| S11 | 错误六字段 | **PASS** | 5 类错误响应（422/404/400×3）`missing=[]` |
| S12 | 证据回链 | **PASS** | 1/1 命中 `SRC-CM-001.evidence-spans.json`，五字段逐项一致 |
| S13 | 统一门禁 | **PASS** | `PASS 11 · FAIL 0 · SKIP 0` |
| S14 | 后端回归 | **PASS** | `968 tests / 0 failure / 0 error / 4 skipped`（apps 585 + modules 224 + adapters 92 + scenario 67） |
| UI | 前端 E2E | **NOT_APPLICABLE** | `frontend/src` 仍无代码调用本端点（`v11.ts` 的 `/product-knowledge/*` 为版本列表/详情），本计划未改前端 |

## F-L13-02 · MAJOR → **RESOLVED（独立 QA 验证通过）**

`KertReleaseSnapshotAdapter.load()` 新增 `!Files.isDirectory(snapshotDir) || !Files.isReadable(snapshotDir)` 分支 → 抛 `KnowledgeSourceUnavailableException`。
复审除原 S8 外，另注入两个 dev 自测未覆盖的变体（`chmod 000`、路径指向普通文件），均得 `503 FAILED_CLOSED`；
并反向验证「目录可达但产品无投影」仍为 `404`，确认修复未把两类语义重新合并。
结构性漏网已补：`KertReleaseSnapshotAdapterTest`（5 项，真实文件系统 `@TempDir`）覆盖目录缺失/未配置/文件缺失/损坏/正常加载。

## F-L13-03 · MAJOR → **RESOLVED（独立 QA 验证通过）**

`normalizeEnum` 增白名单 `ALLOWED_VIEWS` / `ALLOWED_PURPOSES`，非法取值 → `400 BAD_REQUEST`。
`view=BOGUS` 由「200 + 空 fields + 响应体携带合同外枚举值」修正为 400；`purpose=BOGUS` 由 422 错码修正为 400。

## F-L13-04 · MINOR → **RESOLVED（独立 QA 验证通过）**

新增 `@ExceptionHandler(MissingServletRequestParameterException)` → 统一错误体。
缺 `purpose` / 缺 `view` / 两者皆缺三种组合均为 `400` 且六字段齐备。

## F-L13-05 · MINOR → **RESOLVED（独立 QA 验证通过）**

`CTR-PK-INT-001` 响应码由 `["200","404","409","422","503"]` 扩为 `["200","400","404","409","422","503"]`；
`ErrorResponse.code` 枚举补 `BAD_REQUEST`。实现与合同的 400 缺口闭合。

## F-L13-06 · MINOR → **RESOLVED（独立 QA 验证通过）**

KERT 侧投影只取当前有效断言的证据并按 `evidenceId` 去重：`9 条 / 4 去重` → `1 条 / 1 去重`。
投影文件 md5 `6da49bb4…` → `1ed0685f…`（KERT @ `0a3a51d`，已重新发布），复审后 md5 未再变动。

## O-L13-03 · OBSERVATION · **保留 OPEN**

`SUPPORTED` 仍携带 `conflictId=CNF-PRODCM001-757c6c3b`（投影中该字段 `conflictId` 非空且 `knowledgeState=SUPPORTED`）。
合同未定义该不变式，按裁决交 Contract Owner，本轮不作为缺陷计，**不阻断 QA_PASS**。
附带影响已确认：去重后被否决的相反证据（SRC-CM-003「100 万元」）不再出现在该字段下，
冲突溯源改由 `conflictId` 承担 —— 与「SUPPORTED 只由采信证据支撑」一致，但需在合同裁决时一并确认。

---

## F-L13-01 复核（2026-09-07 · Tech Lead）

**调查结论**：不是"漏注册一个资产"这么简单。

- 资产清单来自 `specs/knowledge-architecture/assets/**/*.md`，**恰好 20 份**，
  其中 `knowledge-rules/` 下只有 visit-sop / evidence-policy / kyc-question-library /
  customer-ontology / product-cards / claim-reconciliation —— **无产品规则**；
- 校验写死 `exactly 20 P20 asset manifests` ⇒ 新增第 21 份必须同时改常量，
  即改动 P20 受控资产集基线；
- 资产清单必填 `governance.owner/classification/permissionInherit/allowedActions`
  与 `evidence` 三项全 true —— **尚未建设的资产无法诚实填写**；
- 直接删依赖会让契约声称"产品适配不需要产品规则"，属**掩盖缺口**，不予采用。

**同一缺口的另一处投影**：L13 Release 的 `rulePackageHash = SHA-256("RULEPACKAGE:EMPTY")`
是占位值 —— 产品规则包同样未建设。两者是同一缺口在两个体系中的表达。

**裁决**：不在本计划内擅自新增 P20 资产，也不删依赖。写
`docs/adr/ADR-PK-PRODUCT-RULES-ASSET.md`，给出两条解除路径：

| 路径 | 动作 | 建议 |
|---|---|---|
| A 建设资产 | 新增 `assets/knowledge-rules/product-rules.md` + 常量 20→21 + KERT 规则包落地 | **建议采用**（SP-15 是 RULE_MODEL，规则是必要输入） |
| B 撤回声明 | 从 SP-15 / AC-PRODUCT-RECOMMEND-001 移除该依赖并复核 implementationType | 仅在规则改由 KERT Release 独载时采用 |

**影响边界**：仅阻断 `make check` 的 `knowledge-architecture-check` 步骤（CI 绿灯）。
PI-ARCH 交付不受影响 —— 统一门禁 11/11、E2E S1–S17 全 PASS、演示可用。

## O-L13-03 裁决（2026-09-07 · Tech Lead）

**问题**：SUPPORTED 断言携带 `conflictId`，且其证据集历史曾含被否决的相反数值原文。

**裁决**：**保留 conflictId 作为溯源**，但强制"裁决一致性" —— 采信结论必须能追溯到
正是哪一条 Owner 决策解决了那个冲突，且不得混入被否决证据。

新增 **`INV-ASM-09`**（已进入 `CTR-PK-ASM-001` 的 `x-invariants`）：
```
SUPPORTED 断言可保留 conflictId 作为冲突溯源，但该冲突必须 status=RESOLVED
且 resolution.decisionId == 本断言 reviewDecisionId；
且 evidenceIds 只含采信证据，不得含被否决证据
```

落地：
- `invariants.py` / `check_invariants.py`：谓词 + 正反例（103/103，51 条）
- KERT `check_l12_conflicts.py`：对真实数据校验冲突存在/已裁决/决策 ID 一致/无被否决证据交集
  （门禁 23/23 PASS）

理由：清空 conflictId 会丢失"这个字段曾经打架、由谁裁决"的信息，
对审计场景是资产而非负担；真正该管住的是**采信证据集合的纯净性**。

---

## F-L13-01 修复（2026-09-07 · Owner 选定路径 A）

| 步骤 | 内容 |
|---|---|
| 1 | 新增 `specs/knowledge-architecture/assets/knowledge-rules/product-rules.md`<br>（`ASSET-KNOW-PRODUCT-RULES`，`KNOWLEDGE_RULE` 类，governance/evidence 必填项齐全） |
| 2 | `validate_knowledge_architecture.py`：资产基线 `exactly 20` → `21` |
| 3 | KERT 新增 `04_serve/rule-packages/PROD-CM-001.rule-package.json`<br>`status=NOT_BUILT` / `rules=[]` / `failurePolicy=FAIL_CLOSED` |
| 4 | `l13_publish_release.py`：`rulePackageHash` 由 `SHA-256("RULEPACKAGE:EMPTY")` 常量<br>改为**规则包文件的真实内容哈希**（已核验不再是 EMPTY 占位） |
| 5 | Release 重新签发（bundle 变更） |

**顺带修掉的同源基线不同步**：`unexpected P20 activation set` ——
`IN_SCOPE_CONTRACTS` 缺 `AC-PRODUCT-RECOMMEND-001`（该文件早已存在未被登记）。
补入后 `knowledge-architecture-check` 转 PASS。

**诚实边界**：规则包**内容仍为空**（`NOT_BUILT`）。本次修的是"资产从未注册"与
"哈希是写死常量"两件事 —— 让"规则未建设"显式可见且可追溯，
**不是**宣称规则已生效。规则内容须由产品管理部与风险部共同签署后方可置 `BUILT`。

**验证**：
```
make check                        → EXIT=0
  contract-check PASS · knowledge-architecture-check PASS（assets=21）
  loop-guard PASS · secret-scan PASS · enum-consistency PASS
  semantic-rule-gate PASS（SHACL / Schema JSON / DMN / LinkML）
python3 specs/product-knowledge/check_all.py → 11/11 PASS
KERT L12=0 · L13=0
```
未改动任何 Java 代码，未重跑后端测试。
