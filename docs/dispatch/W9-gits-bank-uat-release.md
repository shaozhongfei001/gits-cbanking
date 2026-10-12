# W9 Dispatch｜GITS Bank UX UAT / 发布 / 冻结（人类 Owner）

```text
DISPATCH_ID=W9-GITS-BANK-UAT-RELEASE
STATUS=OWNER_UAT_FAIL
OWNER_DECISION=OD-GITS-BANK-UX-W9A-FAIL-2026-08-26
WORKING_BRANCH=feature/P30-gits-bank-experience-shell
DEPENDS_ON=P30…P37 qa_pass
CONTRACT_CHANGE=NOT_AUTHORIZED
AUTHORITY_SOURCE_CHANGE=NO
UAT_SCOPE=W9-A
UAT_PASS=NO
FROZEN=NO
PRODUCTION_READY=NO
COMMIT=797f3ebd4a15422d844e0def08526916359d0e12
```

本波不是 Feature Loop。Tech Lead 只准备验收包与范围分叉；**不得**由开发、Tech Lead 或 Independent QA 签署 `UAT_PASS` / `FROZEN` / `PRODUCTION_READY`。`qa_pass` ≠ UAT。

## 已交付（可验收）

Experience Shell + 页面 P01–P44 的 **C0 复用或 C2 降级壳**。适用工程 SIT 已由 Independent QA 复跑（P37 session `iqa-p37-20260825T175104Z`）。矩阵：`loops/P37-gits-bank-sit-gates/evidence/SIT_MATRIX.md`。

明确未交付、不得在本波记 PASS：

- 正式 Need / ServicePlan 写（CCC-003）
- 建议书 G0–G5 阶段机与真写（CCC-004）
- AccountPlan / 对客交付包 / 价值口径真对象（CCC-006/007）
- 移动离线缓存、撤权、冲突同步（CCC-009）
- 264 / 224 / 44/44 全量完成

## Owner 必须先勾选范围

| 选项 | 验收对象 | 能否现在开 UAT | 能否冻结为「V3.2 已实现」 |
|---|---|---|---|
| **W9-A**（推荐默认） | 已交付的导航壳、C0 查询、C2 禁用/降级说明 | 可以 | **否**。最多冻结「C2 体验壳候选」 |
| **W9-B** | V3.2 设计中的正式对象与真写 | **不可以**。先 CC2 + 独立合同 Loop | 在合同 Loop 与独立 QA 之后再开第二轮 UAT |

**Owner 已于 2026-08-26 勾选 W9-A**（`OD-GITS-BANK-UX-W9A-2026-08-26`）。未勾选不得签署 UAT。勾选 W9-B 却没有合同源变更，视为范围错误，退回。

### Tech Lead 建议

对本波选 **W9-A**。C3 另开合同 Loop 的利弊见下文；**不要把 C3 当作本 W9 的前置**，也不要在本冻结里宣称正式 Need / G0–G5 / AccountPlan。

若产品目标是「按 V3.2 图做完」，把 W9-A 当作中期体验验收，C3 走后续 CCB 变更，不要混签。

## C3 另开合同 Loop：利弊（给 Owner）

C3 候选登记：`docs/governance/contract-candidates/CCC-GITS-BANK-20260825-INDEX.md`（9 条，状态均为 REVIEW；`AUTHORITY_SOURCE_CHANGE=NO`）。

### 另开的好处

1. **不发明对象。** Need ≠ Claim，G0–G5 ≠ 静态文案，AccountPlan ≠ Task。合同 Loop 先改 authority source 再 `make generate`，才允许 Feature 实现真写。
2. **和已交付壳解耦。** P30–P37 的 `qa_pass` 不因合同评审被推翻；W9-A 可以先验收「壳是否可导航、降级是否诚实」。
3. **变更可回滚、可审计。** 走 CC2 / CCB，而不是在 UAT 现场改 OpenAPI。
4. **可按对象族切开。** 九条 CCC 不是同一风险：Need 是经营语义；G0–G5 是阶段机；移动缓存是安全/越权。分开 Loop 失败面更小。
5. **避免把 C2 按钮悄悄改成可写。** 没有合同 Loop 却「为了 UAT 把禁用打开」，会污染领域语义并无法回归。

### 另开的坏处 / 成本

1. **周期长。** 顺序是 CC2 签署 → 改合同源 → generate/check → 消费者 → 实现 → 独立 QA → 再一轮 UAT。不是改几个 Vue 页。
2. **碰受保护 GITS—DKES 边界。** 当前 Owner 决定仍是「候选可评审、源不可改」。未签 CC2 就开实现 Loop 是越权。
3. **九条一起开会失控。** 一个 mega Contract Loop 会把 Need、建议书工厂、离线缓存绑在同一门禁，任一 blocker 卡住全部。
4. **若先冻结再改合同，冻结后每条都是 CCB 变更。** 这是治理成本，不是 bug；若 Owner 想一次冻成 V3.2 全量，应推迟冻结而不是跳过合同。
5. **UAT 角色会看到「按钮是灰的」。** 客户经理可能判「没做完」。W9-A 必须把降级说明写进脚本，否则会被误判为缺陷。

### 建议切法（若以后开，而不是现在）

不要开一个「C3 全能 Loop」。按依赖：

| 优先 | Candidate | 原因 |
|---|---|---|
| 1 | CCC-003 Need / ServicePlan | 经营闭环「Need 先于产品」；没有它，建议书工厂仍是空壳 |
| 2 | CCC-004 G0–G5 | 建议书真写；依赖 Need 语义 |
| 3 | CCC-007 AccountPlan / 价值 | 持续经营；不能用 Task 顶替 |
| 4 | CCC-009 移动缓存 | 单独安全 ADR；不要和 Need 绑在一起 |
| 5 | 其余 001/002/005/006/008 | 写回与交付包，按业务优先级排队 |

每条：CC2 签署后才 `make new-loop`，且 `CONTRACT_INDEX` 变更先于实现。

## W9-A 人类验收清单（Owner / 客户经理）

环境：`feature/P30-gits-bank-experience-shell` 已推远程；对照 commit 填入下表。

| # | 检查 | Owner | Tech Lead 陪跑 |
|---|---|---|---|
| 1 | 左导航可进入 P01–P44 对应路由；对象头/页签不丢上下文 | ☐ | **PASS** 44/44（`docs/dispatch/W9-A_ESCORT_LOG.md`） |
| 2 | C0 页（工作台、客户查询、互动、承诺、审批、审计等）数据来自既有 API，不是静态假对象 | ☐ | 陪跑使用 SIT mock；本机 `8080` 未起，**不能**代替活后端 |
| 3 | C2 页主动作禁用，文案说明原因与解除路径（合同未批准），没有可点的假写 | ☐ | **PASS**（有 `gated-action` 的页均 disabled + 原因/解除路径） |
| 4 | 未把灰按钮当成缺陷而要求现场改合同 | ☑ 已由 OD-W9A 接受 | — |
| 5 | 同意本签署 **不是** 264 PASS、**不是** 44/44 功能完成、**不是** 生产发布 | ☑ 已由 OD-W9A 接受 | — |
| 6 | 发布/回滚/监控/培训：本波 **未** 交付，不得勾选 PRODUCTION_READY | ☑ 已由 OD-W9A 接受 | — |

签署区（仅人类 Owner；Agent 不得代填 `UAT_PASS`）：

```text
UAT_SCOPE=W9-A
UAT_PASS=NO
FROZEN=NO
PRODUCTION_READY=NO
OWNER_NAME=HUMAN_OWNER
DATE=2026-08-26
COMMIT=797f3ebd4a15422d844e0def08526916359d0e12
NOTES=人工测试不通过：左导航/菜单逻辑/配色与 V3.2 设计图不符；点选「互动对象」GET /api/v1/interactions 500。见 OD-GITS-BANK-UX-W9A-FAIL-2026-08-26。
```

## 本波明确不做

- 改 `specs/openapi/` / `CONTRACT_INDEX.yaml` / `generated/`
- 新建 C3 Feature Loop 或把 CCC 状态改成 APPROVED
- 灰度、超护、生产 Runbook（规划 P10 全量；无 Owner 环境授权则保持未做）
- `git` 合并入 `main`（需另一次 Owner 指示）
