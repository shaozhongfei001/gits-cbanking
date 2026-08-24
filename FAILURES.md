# FAILURES.md

## Mapper XML Record 适配修复 — E2E 验证失败记录

**验证日期**: 2026-08-12
**验证角色**: E2E Owner
**分支**: feature/v11-frontend-depth-remediation

---

### F-1: FactReconciliationCaseMapper.xml 引用不存在的内部类 [BLOCKER]

**严重程度**: BLOCKER — 阻断所有集成测试

**文件**: `adapters/persistence-relational/src/main/resources/mapper/foundation/ontology/FactReconciliationCaseMapper.xml`

**行号**: 21

**现状**:
```xml
<arg column="status" javaType="com.gien.gits.ontology.FactReconciliationCase$ReconciliationStatus"/>
```

**期望**:
```xml
<arg column="status" javaType="com.gien.gits.ontology.ReconciliationStatus"/>
```

**原因**: `ReconciliationStatus` 是顶级枚举类 (`com.gien.gits.ontology.ReconciliationStatus`)，不是 `FactReconciliationCase` 的内部类。

**影响**: MyBatis 解析 Mapper XML 失败 → SqlSessionFactory 创建失败 → 所有 43 个集成测试 ERROR。

---

### F-2: 6 个 Mapper XML 的 INSERT 语句中 Instant 字段缺少 InstantTypeHandler [MINOR]

**严重程度**: MINOR — H2 兼容模式下可能不阻塞，但与项目规范不一致

**规范要求**: 所有 `java.time.Instant` 字段在 INSERT/UPDATE 中必须指定 `typeHandler=com.gien.gits.adapter.persistence.common.typehandler.InstantTypeHandler`

| 文件 | 缺失字段 |
|------|----------|
| `RelationshipReportMapper.xml` | `createdAt`, `updatedAt` |
| `ProductKnowledgeCardMapper.xml` | `createdAt` |
| `BankRelationshipSnapshotMapper.xml` | `createdAt` |
| `FactReconciliationCaseMapper.xml` | `createdAt`, `updatedAt` |
| `CreditFacilityMapper.xml` | `createdAt`, `updatedAt` |
| `TransactionRecordMapper.xml` | `createdAt` |
| `GroupRelationshipMapper.xml` | `createdAt` |

**注意**: `OpportunityMapper.xml` 的 `expectedCloseDate` 是 `String` 类型，不需要 InstantTypeHandler（已排除）。

---

## 验证通过项

| 检查项 | 结果 |
|--------|------|
| 编译 + 单元测试 (persistence-relational -am) | ✅ 19 tests, 0 failures |
| 所有 33 个 Mapper XML 使用 `<constructor>` 模式 | ✅ 无残留 `<result property=...>` |
| PrevisitReportContentMapper productSchemes typeHandler 一致性 | ✅ resultMap 和 INSERT 均使用 ProductSchemeListTypeHandler |
| 其他 `$` 内部类引用 (17 处) | ✅ 全部为真实内部类/枚举 |
| 已有 INSERT 中 InstantTypeHandler 覆盖 | ✅ 大部分 Mapper 已正确添加 |

---

## 退回建议

退回至 Feature Pilot 修复 F-1 (BLOCKER) 和 F-2 (MINOR) 后重新验证。

---

## SP-20 服务建议书内容为空 — 联调失败记录

**验证日期**: 2026-08-24
**验证角色**: E2E Owner（GITS 侧联调对账）
**分支**: feature/P24-dkws-supplychain

### FAIL-2026-08-24-01: 前端传参 context 非完整 ContextPackage，DKWS 校验失败 → 空建议书 [BLOCKER]

**严重程度**: BLOCKER — SP-20 前端页面生成建议书内容为空，用户可见

**现象**: 前端 `ServiceProposalView` 点击"生成建议书"后，页面显示建议书内容为空（`(空)`）。

**根因链**（经直打 DKWS 确认）:
1. 前端 `ServiceProposalView.vue` 的 `generate()` 只传 `context = {enterpriseData: {customerId}, customerVersionLabel: "内部"}`，不是 SP-20 契约要求的完整 ContextPackage（缺顶层 `customerId/customerName/industry` 等必填字段）。
2. 后端 `ServiceProposalService.generate()` 原样透传调用方 context，无补齐逻辑。
3. DKWS SP-20 在 validate 阶段失败：`SKILL_EXECUTION_FAILED: ContextPackage 缺失字段: ['customerId', 'customerName', 'industry']`（增量探测确认最小必填集 = customerId + customerName + industry + enterpriseData）。
4. GITS `ServiceProposalService` 收到 `skill_error` → `ok=false` → 返回 `ServiceProposal.empty()` → 前端显示空内容。

**证据**:
- 复现：前端等价 payload（context 仅 2 字段）经 `/api/v14/proposals` → SUCCESS 但 `content` 空、0 引用、2.74s 秒回（未走真实生成）。
- 直打 DKWS job `JOB-SKILL-20260823-014`：errors=`ContextPackage 缺失字段: ['customerId', 'customerName', 'industry']`。
- 对照：完整 ContextPackage → 10,569 字 / 75 引用（正常）。
- 最小必填集验证：`JOB-SKILL-20260823-016` 带 `{customerId, customerName, industry, enterpriseData}` → 校验通过，真实生成 12,003 字 / 52 引用。

**修复方向**: 后端 `ServiceProposalService` 仅凭 `customerId` 从客户主数据（`CustomerContextService`）组装/补齐 ContextPackage 必填字段（customerId/customerName/industry/enterpriseData），调用方 context 已含完整必填集时透传。前端无需感知 ContextPackage 细节。

**修复与验证**（2026-08-24，Feature Pilot 完成 → E2E 回归通过）:
- 代码修复：`ServiceProposalService` 新增 `CustomerContextService` 依赖，`buildContext()` 在调用方 context 缺必填字段时凭 `customerId` 组装 `customerId/customerName/industry/enterpriseData`（数据源：`Customer` 主档、`CreditFacility`、`BankRelationshipSnapshot`、`TransactionRecord`）；`EngagementConfig` 同步装配。
- 单元测试：`ServiceProposalServiceTest` 3/3 通过（补齐必填集 / 已完整透传 / 空 customerId）。
- 回归验证：`./mvnw package -pl apps/api` BUILD SUCCESS → 重启 8082（pid 3694945，health=200）→ 前端等价 payload（context 仅 2 字段）POST `/api/v14/proposals` → `status=SUCCESS`，建议书正文完整生成（含企业概况/经营现状/信用金融等章节），不再为空。**FAIL-2026-08-24-01 已关闭。**

### FAIL-2026-08-24-02: 旧 jar classpath 不完整导致全接口 500（环境问题，已由重启解决）

**严重程度**: HIGH（用户可见，全接口受影响）

**现象**: 前端"启动客户旅程"返回 `status code 500`。

**根因**: 旧进程（pid 2143504）运行的是 02:24 打包的不完整 jar，运行期 `Servlet.service()` 抛 `Filter execution threw an exception`，根因 `java.lang.ClassNotFoundException: org.springframework.util.LinkedCaseInsensitiveMap$KeySet`（以及 `org.apache.catalina.util.RequestUtil`、`org.springframework.boot.web.server.GracefulShutdownCallback` 等）——classpath 缺 Spring/Tomcat 内部类，任何经过 Filter 的请求均 500，非业务代码缺陷。

**处置**: 精确 PID 重启加载 03:22 打包的完整 jar（BUILD SUCCESS，67654540 B）→ 新进程（pid 3694945）`POST /api/v1/engagement/journey/start {"customerId":"CUST-CORP-0001"}` 返回 **201**（journeyId/operatingCaseId/phase=INSIGHT_ANALYSIS），500 消除。**已关闭（环境类，非代码回归）。**

### FAIL-2026-08-24-03: ServiceProposalView 前端 v-model 绑定错误导致无法生成建议书

**严重程度**: BLOCKER（用户无法操作页面）

**现象**: 输入客户 ID 后点击"生成建议书"无任何请求发出，页面提示"请先输入客户ID"（虽然输入框有值）。

**根因**: `frontend/src/views/ServiceProposalView.vue` 第 12 行 `v-model="customerId"` 绑定到 Vue 默认 prop `modelValue`，但 Naive UI 的 `n-input` 绑定 prop 是 `value`（需 `v-model:value`）。项目其他页面均用 `v-model:value`，本页漏写 → v-model 永不同步 → `generate()` 中 `if (!customerId.value)` 恒命中。同页还漏 import 全部 `n-*` 组件（仅 `useMessage`），导致 `Failed to resolve component` 警告（组件未渲染）。

**修复**: 
- `v-model="customerId"` → `v-model:value="customerId"`（对齐项目其他页面）。
- 补 import `NTag, NInput, NButton, NAlert, NCard, NTabPane, NTabs, NTable, NEmpty`。

**验证**: lint 0 错误、`vue-tsc --noEmit` 通过；Playwright E2E（`/home/szf/env/my-playwright/tests/sp20-service-proposal.spec.ts`）全流程通过（1 passed，1.1m）：POST `/api/v14/proposals` → 200，建议书正文完整（内部版 13,000+ 字，含"综合金融服务建议书"/"华东精工装备"），对客版 tab 可切换。**已关闭。**
