# ONTO1｜CQ5 四态可区分：原因码表与负例设计（DRAFT）

| 项 | 值 |
|---|---|
| 文档性质 | **DRAFT（草稿）**——候任 Integration Contract Owner 任职技术准备产出 |
| 状态 | `DRAFT` / `DESIGN_ONLY`（**不得标 `PASS`**） |
| 责任 Owner | Integration Contract Owner（**待任命**） |
| 夹具基线 | `loops/ONTO1-ontology-split/evidence/cq-fixtures/CQ5.json`（`schema: onto1_cq_fixture/v1`，`status: DESIGN_ONLY`） |
| 依据 | 设计 §6.6（CQ5 行）、复审包 `08-CQ语义验收矩阵.md`、`06-验证状态模型与状态跃迁表.md` §1/§3、`07-兼容性矩阵-major-minor-patch.md` |
| 执行时机 | **Wave 4**（需实现存在）；本轮只做设计 |

> **红线声明**：本文不实现、不接线、不标 `PASS`；本轮**未改动** `specs/CONTRACT_INDEX.yaml` 与 `generated/`。

---

## 0. CQ5 原文与验收要求（回源）

- **能力问题**：某能力**可见但不可执行**时，原因是未发布、无端点、无授权还是版本不兼容？（设计 §6.6）
- **夹具 `expected`（逐字）**：每种场景返回可区分原因码 `NOT_PUBLISHED` / `NO_ENDPOINT` / `UNAUTHORIZED` / `VERSION_INCOMPATIBLE`（`cq-fixtures/CQ5.json`）
- **夹具 `negative`（逐字）**：四种原因混报为单一「不可用」⇒ FAIL
- **夹具 `mutation`（逐字）**：删除 EndpointBinding ⇒ 原因必须从 OK 变为 NO_ENDPOINT

**验收物（设计 §6.6 末段）**：查询 + 正例夹具 + 负例夹具 + 预期结果 + **变异复验记录**；且"仅类数量守恒不能证明语义覆盖"。

---

## 1. 问题的本质：四态**可能同时成立**，所以必须定全序

「可见但不可执行」的四个原因**不是互斥条件**。反例：

| 场景 | 同时成立的原因 |
|---|---|
| 能力 `DRAFT` 且未绑端点 | `NOT_PUBLISHED` ∧ `NO_ENDPOINT` |
| 端点存在但消费者授权过期且钉定版本已出兼容集 | `UNAUTHORIZED` ∧ `VERSION_INCOMPATIBLE` |
| 未发布、无端点、无授权、版本不兼容 | 四态**全成立** |

**因此**："四态可区分"**不能**靠"检查四个布尔量"实现——那必然产生混报（正是 CQ5 的 negative 要罚的行为）。必须定义**判定全序（短路优先级）**，并规定"只输出一个 `primaryReason`"。

> 若不定义优先级，"随机取一个真原因"在逻辑上也是"正确的四态之一"，测试无法判 FAIL ⇒ **假绿风险极高**。这是本设计最重要的一点。

---

## 2. 判定全序（短路优先级，唯一权威顺序）

```
第 0 步：输入完备性        → 缺对象记录 ⇒ UNKNOWN_REASON（fail-closed，见 §3.5）
第 1 步：发布状态          → status ∉ PUBLISHED   ⇒ NOT_PUBLISHED     （短路）
第 2 步：端点绑定          → 无有效 EndpointBinding ⇒ NO_ENDPOINT       （短路）
第 3 步：消费者授权        → 未授权/过期/范围不足  ⇒ UNAUTHORIZED       （短路）
第 4 步：版本兼容          → version ∉ compatibleSet ⇒ VERSION_INCOMPATIBLE（短路）
第 5 步：全部通过          → OK（executable = true）
```

**顺序的语义理由**（不是随意排的）：

| 顺序 | 理由 |
|---|---|
| 发布 先于 端点 | 未发布的东西**不该有**端点讨论（讨论端点会掩盖"根本不该被消费"这一更强原因） |
| 端点 先于 授权 | 授权是"给谁用"，端点是"有没有得用"；无端点时授权无意义 |
| 授权 先于 版本 | 无权限者**不应**获知版本兼容信息（也防信息泄露：不兼容细节对未授权方不可见） |
| 版本 最后 | 只有前三关都过，版本才有判定意义 |

**输出契约**：

```json
{
  "capabilityId": "…",
  "capabilityVersion": "x.y.z",
  "executable": false,
  "primaryReason": "NO_ENDPOINT",
  "allSatisfiedReasons": ["NOT_PUBLISHED", "NO_ENDPOINT"],
  "reasonDetail": { …字段级证据… },
  "evaluatedAt": "2026-…",
  "registryVersion": "…",
  "schema": "onto1_cq5_reason/v1"
}
```

**规则**：
- `primaryReason` **必须**是 §2 全序下**第一个**成立的原因（可机器复算）；
- `allSatisfiedReasons` 可列出全部成立原因（**信息性**，不参与判定）——允许它存在是为了**可审计**，但**禁止**用它的内容作为 `primaryReason`；
- `executable` 只能是布尔；`primaryReason = OK` ⇔ `executable = true`；
- **禁止**任何"多值并列"或"未分类"的 `primaryReason`（例：`UNAVAILABLE`、`MULTIPLE`、`OTHER` 一律非法）。

---

## 3. 原因码表（机读可判定）

### 3.1 `NOT_PUBLISHED`

| 项 | 内容 |
|---|---|
| 含义 | 能力对象存在（"可见"来自注册表可被查询），但其发布状态不构成"可供消费" |
| 触发（机读） | `CapabilityPublication.publicationStatus ∈ {DRAFT, REVIEW, WITHDRAWN, RETIRED}` |
| 边界 | `DEPRECATED` **不**触发本码（弃用期内仍可消费，见 §3.4） |
| 期望详情 | `reasonDetail.publicationStatus` = 实际值 |
| 禁止 | 把"对象不存在"报成本码（那是 `UNKNOWN_REASON` / 404，不是"未发布"） |
| 依据 | L4 设计 §4 发布状态机；夹具 `positive` ① `status=DRAFT` |

### 3.2 `NO_ENDPOINT`

| 项 | 内容 |
|---|---|
| 含义 | 已发布，但**没有可用端点绑定** |
| 触发（机读，任一） | ① 无 `EndpointBinding` 记录；② `bindingStatus ≠ BOUND`；③ `endpointRef` 为空串或**占位值**（`localhost`/`example.com`/`TBD`）；④ `resolutionMode = OFFLINE_CONTENT_ADDRESSED` 但 `contentHash` 缺失；⑤ 跨仓端点缺 `crossRepoAuthorization` 依据 |
| 边界 | **不得**因"端点返回 5xx"报本码（那是运行时不可用，属另一问题域，须另立码，见 §6 待裁定 D-2） |
| 期望详情 | `reasonDetail.endpointBindingId`（可空）、`reasonDetail.bindingStatus`、`reasonDetail.failedCheck`（哪一条触发） |
| 依据 | L4 设计 §3.3；夹具 `mutation`：删除 EndpointBinding ⇒ `OK → NO_ENDPOINT` |

### 3.3 `UNAUTHORIZED`

| 项 | 内容 |
|---|---|
| 含义 | 已发布、有端点，但**该消费者无权消费** |
| 触发（机读，任一） | ① 无 `ConsumerBinding`；② `bindingStatus ∈ {SUSPENDED, REVOKED, EXPIRED}`；③ `validTo < evaluatedAt`（过期）；④ `authorizedScopes` **为空数组**（空 ≠ 全权）；⑤ 请求 scope ∉ `authorizedScopes`；⑥ `grantedBy` 缺失（无授权来源） |
| 边界 | **过期**属本码（授权域），**不属**版本域；不得因"过期"报 `VERSION_INCOMPATIBLE` |
| 期望详情 | `reasonDetail.consumerBindingId`、`reasonDetail.failedCheck`（如 `SCOPE_NOT_GRANTED` / `EXPIRED`）、`reasonDetail.requiredScope` |
| 依据 | L4 设计 §3.4；夹具 `positive` ③"ConsumerBinding 缺失/过期" |

### 3.4 `VERSION_INCOMPATIBLE`

| 项 | 内容 |
|---|---|
| 含义 | 已发布、有端点、有授权，但请求/钉定版本不在兼容集 |
| 触发（机读，任一） | ① 请求版本 ∉ `ContractVersion.compatibleSet`；② `compatibleSet` 缺失或为空（**fail-closed**：不得解释为"无限制"）；③ `ContractVersion.compatibilityLevel = major` 但缺 `compatibleSet`；④ 消费者钉定版本已 `DEPRECATED` 且 `sunsetAt < evaluatedAt` |
| 边界 | `DEPRECATED` **未过** `sunsetAt` ⇒ **允许消费**，不得报本码（07 号 §3 弃用期语义） |
| 期望详情 | `reasonDetail.requestedVersion`、`reasonDetail.compatibleSet`、`reasonDetail.contractVersionId` |
| 依据 | 07 号 §1/§3；夹具 `positive` ④"版本 ∉ 兼容集" |

### 3.5 `UNKNOWN_REASON`（fail-closed 兜底，**不是第五态语义**）

| 项 | 内容 |
|---|---|
| 含义 | **无法判定**（输入缺失/畸形） |
| 触发 | 缺必填判定输入（如缺 `ContractVersion` 记录本身）；字段类型非法；注册表版本不可解析 |
| 输出约束 | `executable` **必须** `false`；`primaryReason = UNKNOWN_REASON`；`reasonDetail.missingInputs[]` 非空 |
| 禁止 | ① 报 `OK`；② 报 `NOT_EVALUATED` 当作通过（`NOT_EVALUATED` 是**验证状态**，不是 CQ5 的判定结果——**两套词汇不得混用**）；③ 静默降级为文本比对（ADR §5.3 fail-closed 纪律） |
| 依据 | ADR §5.3"不可解析时 fail-closed，不得静默降级"；06 号 §3 |

**注**：`UNKNOWN_REASON` 是**第 0 步**的产物，与四态不在同一层；它存在的作用是**保证没有"什么都不成立就返回 OK"的漏洞**。

### 3.6 正例基线 `OK`

| 项 | 内容 |
|---|---|
| 触发 | 四步全通，且 `evaluatedAt` 落在所有 `validFrom/validTo` 区间内 |
| 输出 | `executable: true`，`primaryReason: "OK"`，`allSatisfiedReasons: []` |

---

## 4. 负例设计（**每一条都必须能被门禁判 FAIL**）

> 纪律：负例必须**否定式**（断言"必须 FAIL / 必须不出现某输出"），不能只断言"返回了某个码"。
> 每条负例须配：`id` / `given`（注入的坏情况）/ `mustFailIf`（判定式）/ `mutationOf`（从哪个正例变异而来）。

| # | 负例 | 注入 | 判定式（fail-closed） | 依据 |
|---|---|---|---|---|
| N1 | **四态混报** | 构造"未发布 + 无端点 + 无授权 + 版本不兼容" | 若 `primaryReason ∉ 四码单值` 或 输出"不可用/不可执行/UNKNOWN 之外的空泛结论" ⇒ FAIL | 夹具 `negative` 逐字 |
| N2 | **优先级倒置** | 未发布且无端点，但实现按"版本先判"短路 | `primaryReason != NOT_PUBLISHED` ⇒ FAIL | §2 全序 |
| N3 | **空泛兜底** | 全部检查实现为 `try/except → "UNAVAILABLE"` | 出现 §2 合法集之外的码 ⇒ FAIL | §3.5 禁止 ①② |
| N4 | **缺输入判 OK** | 删除 `ContractVersion` 记录 | `executable != false` 或 `primaryReason != UNKNOWN_REASON` ⇒ FAIL | §3.5 |
| N5 | **空授权=全权** | `authorizedScopes: []` + `bindingStatus: ACTIVE` | `primaryReason != UNAUTHORIZED` ⇒ FAIL | §3.3 ④ |
| N6 | **占位端点算绑定** | `endpointRef: "http://localhost:8080"` / `""` | `primaryReason != NO_ENDPOINT` ⇒ FAIL | §3.2 ③ |
| N7 | **过期授权报版本错** | `validTo` 已过 + 版本也不兼容 | `primaryReason != UNAUTHORIZED` ⇒ FAIL | §3.3 边界 |
| N8 | **弃用期误判** | `DEPRECATED` 且 `sunsetAt` 在未来 + 版本在兼容集内 | `primaryReason != OK` ⇒ FAIL | §3.4 边界 |
| N9 | **兼容集缺失当无限制** | 删 `compatibleSet` | `primaryReason != VERSION_INCOMPATIBLE` ⇒ FAIL | §3.4 ② ③ |
| N10 | **未发布却可执行** | `publicationStatus=DRAFT` + `callable=true` | `executable != false` ⇒ FAIL | registry `Capability.json` `callableRule`（"IMPLEMENTED ≠ callable"） |
| N11 | **多值并列** | 输出 `primaryReason: ["NO_ENDPOINT","UNAUTHORIZED"]` | 类型非 string ⇒ FAIL | §2 输出契约 |
| N12 | **用 allSatisfiedReasons 决定结果** | 故意让 `allSatisfiedReasons[0]` 与全序首项不同 | `primaryReason != 全序首项` ⇒ FAIL | §2 规则 |

**防假绿要求**：负例集必须包含**至少一条"实现看起来正常但语义错"的用例**（N2/N7/N8 即此类）——只测"非法输入被拒"的负例不足以证明四态可区分（GK-KE 程序"假绿"教训：全部夹具为正例时，拒绝分支从不进入，否定式断言恒真）。

---

## 5. 变异用例设计（对齐夹具 `mutation` 字段）

| # | 变异 | 期望 | 说明 |
|---|---|---|---|
| M0 | 不动（对照：完整四对象且状态良好） | **PASS**（`OK`） | 无对照的变异矩阵不算证据 |
| M1 | 删除 `EndpointBinding` 记录 | `OK → NO_ENDPOINT` | **夹具 `mutation` 逐字要求** |
| M2 | `publicationStatus: PUBLISHED → DRAFT` | `OK → NOT_PUBLISHED` | — |
| M3 | `ConsumerBinding.validTo` 改为过去 | `OK → UNAUTHORIZED` | — |
| M4 | `compatibleSet` 移除当前版本 | `OK → VERSION_INCOMPATIBLE` | — |
| M5 | 同时施加 M1+M3+M4 | `OK → NO_ENDPOINT`（全序首项） | 验优先级 |
| M6 | 同时施加 M2+M1 | `OK → NOT_PUBLISHED` | 验优先级 |
| M7 | 删除 `reasonDetail.failedCheck` | FAIL（证据字段缺失，无法归因） | 防"只给码不给证据" |
| M8 | 把判定实现替换为"始终返回 OK" | FAIL（M1~M6 全部失去判别力） | **元变异**：证明门禁不是空转 |

**变异复验纪律（计划 §7、07 号 §4）**：每条 `mutate → 必须 FAIL`、`restore → 必须 PASS`，且**记录实际输出**（不是只记"绿/红"）。

---

## 6. 待裁定

| # | 待裁定 | 影响 | 建议 |
|---|---|---|---|
| D-1 | `UNKNOWN_REASON` 是否单列（超出夹具四码） | 夹具 `expected` 只列四码；但无兜底 = 有空转漏洞 | 单列，并**回写夹具** `expected` 补第 5 码（须 TL 同意；夹具当前 `DESIGN_ONLY`，改动成本低） |
| D-2 | 运行时不可用（端点 5xx / 超时）是否入本码集 | 属运行健康域，非绑定治理域 | **不入**；另立码（如 `ENDPOINT_UNHEALTHY`）或归运维，须具名 |
| D-3 | `allSatisfiedReasons` 是否输出 | 有利于审计，但增加"被误用作判定"的风险 | 输出，但门禁增加 N12 负例 |
| D-4 | 判定输入是否包含"权限裁决结果"（`permissionDecisionRequired`） | `ActivationContract.preconditions` 已含此字段 | 纳入，映射到 `UNAUTHORIZED.requiredScope` |
| D-5 | CQ5 判定服务的**查询形态**（API 调用 vs 注册表离线判定） | 夹具 `query` 写"按能力 ID 取四对象状态"；实现未定 | Wave 4 前定；本轮不实现 |

---

## 7. 门禁需求（提案，**不接线**）

| 门禁 | 判定 |
|---|---|
| `cq5_reason_code_check` | ① 四码 + `UNKNOWN_REASON` + `OK` 均为字符串单值；② §2 全序可机器复算；③ 每条负例 N1~N12 在注入后 FAIL；④ 无 `MULTIPLE/UNAVAILABLE/OTHER` 等非法码 |
| `cq5_mutation_regression` | M0 PASS + M1~M8 全部 mutate→FAIL / restore→PASS；M8 元变异证明非空转 |
| `cq5_fixture_honesty` | 门禁**不得**读取夹具的 `status` 字段来判断是否通过（GK-KE `FAIL-2026-09-12-02` 教训：用生成期标志位短路 ⇒ 变异不被捕获）；判定须**由规则驱动**（读四对象 → 复算全序 → 比对期望码） |

---

## 8. 变更记录

| 版本 | 日期 | 变更 | 作者 |
|---|---|---|---|
| DRAFT-v0.1 | 2026-09-20 | 初稿 | 候任 Integration Contract Owner（AI 起草） |

> 草稿，签字权在人类 Owner。
