# GK1 独立 QA 报告 — 结论：退回 Feature Pilot（CONTRACT CONFORMANCE DEFECTS）

- Loop: GK1-registry-map-core（CR-02，验收 T05/T06/T07/T20）
- QA 角色: independent_qa（gk1-qa-manual；Tech Lead 显式切换角色后执行，独立于实现者）
- 复核对象 HEAD: 5e140d6（基线 c7017b1）
- 日期: 2026-09-10
- 说明: 两个异步 QA agent（gk1-qa / gk1-qa2）因环境不稳定中途终止，未产出结论；本报告由独立 QA 角色亲自重跑与核查，非实现者自签。

## 1. 已独立验证通过

- 模块全量测试重跑（`-pl modules/knowledge-architecture -am test -Ddependency-check.skip=true`）：**Tests run: 67, Failures: 0, Errors: 0, Skipped: 0，BUILD SUCCESS**。
- 注册中心：ID+版本精确解析、语义版本 resolveLatest（1.10.0>1.2.0）、重复登记拒绝、多维过滤、null 拒绝（RegistryCoreTest 5 项，断言真实）。
- 依赖闭包：传递闭包拓扑序+去重、叶子闭包、缺依赖/根缺失抛 AssetNotFoundException（DependencyClosureTest 4 项）。
- 规范化与 planHash：PlanHashGoldenTest 6 项——Java 规范化 JSON 与 Python 黄金字节逐字节一致、SHA-256 一致、planHash 自引用字段不入载荷、篡改即变、缺 hash verify=false。质量高。
- T07 秘密资产：SecretLeakTest 验证安全投影不含 contentRef/contentHash/ownerSystem、拒绝即不投影（非脱敏对象）；RegistryPermissionFilter/AccessDecision/ScopeMatch 共 10 项。
- 合同纪律：`git diff --stat c7017b1 HEAD -- specs generated` 为空，未改受控合同；未实现 T17（L2）与 REST（L3），边界正确。
- backend_test 降级独立确认：GK1 仅改 modules/knowledge-architecture + loops；spring-core 6.2.19 CVE 与 apps/api EngagementJourneyControllerTest 切片缺 mock 确为基线 c7017b1 存量，已隔离到 GKB-baseline-hardening（测试切片已由 GKB 修复，spring CVE 决策包待 Owner 裁决）。**残留风险：基线 spring-core CVE 在 Owner 裁决前，全量 make backend-test 仍红；与 GK1 代码无关。**

## 2. 必须修复的合同/验收偏差（退回项）

### Q1（阻断 T20）DAG 校验未按边关系类型区分，relatedTo 导航环会被误判为执行环
- 证据：`KnowledgeMapDagValidator.adjacency()` 对 `map.edges()` **全部边**建邻接表，`validateAcyclic()` 对全图做三色环检测，未读取任何关系类型。
- 合同：C02 §4.2「地图可以有环，如 relatedTo；可执行依赖子图必须是 DAG」；验收 T20「dependsOn 构成循环→拒绝；relatedTo 导航环不误判为执行环」。
- L0 schema `KnowledgeMap.edges[].relation` 枚举 = `requires|optional|uses|dependsOn|covers|relatedTo`。
- 现状测试 `KnowledgeMapDagTest` 只用 `new MapEdge(from,to,"DEPENDS_ON")`，**没有任何 relatedTo/covers 导航环用例**，因此 T20 后半句未被验证；当前实现遇到 relatedTo 环会错误拒绝。
- 修复要求：仅对执行依赖关系（dependsOn；按合同语义 requires/uses 是否纳入执行子图需在代码注释与测试中明确）构图做 DAG；covers/relatedTo 等导航关系不参与执行环检测；补「relatedTo/covers 成环但校验通过」负例。

### Q2（阻断合同一致性）地图模型字段名/枚举与 L0 schema 漂移
- 证据：
  - `MapEdge` 实现为 `record MapEdge(String from,String to,String type)`，注释称 type 取值 `DEPENDS_ON/ROUTES_TO`；schema 实际字段是 `edgeId/from/to/relation/reason/designDecisionRef`，relation 枚举 `requires|optional|uses|dependsOn|covers|relatedTo`。实现发明了 schema 不存在的 `type` 字段与 `ROUTES_TO` 枚举。
  - `KnowledgeMapRecord` 用 `entryNodeIds`，schema 为 `entryNodes`；缺 schema 的 `releaseId`、`taskTypes`、`routePolicyRef`、`contractVersion`、`simulationOnly`；节点 `MapNode` 缺 schema 的 `nodeType`（枚举 Task/KnowledgeDomain/Asset/Capability）。
- 违反：工作区总则「禁止在实现代码中发明合同未定义的字段」「DTO/字段必须与合同一致」。
- 修复要求：地图相关 record 与 CTR-GKKE-005 KnowledgeMap schema 字段名/枚举对齐（additionalProperties=false，反序列化必须能吃下合同样例）；用 schema 正例做反序列化测试。

### Q3（阻断 T06）合同错误码未落地
- 证据：全 gkke 主代码 grep 不到 `DEPENDENCY_UNRESOLVED` / `CAPABILITY_NOT_REGISTERED`；现状用 `AssetNotFoundException` / `DependencyCycleException` / `MapValidationException` 等 Java 异常，未携带合同错误码。
- 合同：C02「引用断裂返回 DEPENDENCY_UNRESOLVED；未注册能力返回 CAPABILITY_NOT_REGISTERED；资产失效 ASSET_NOT_AVAILABLE；路由歧义 ROUTE_AMBIGUOUS」。验收 T06 期望负例结果为 `DEPENDENCY_UNRESOLVED`。
- 修复要求：领域异常携带稳定错误码（至少 DEPENDENCY_UNRESOLVED、CAPABILITY_NOT_REGISTERED；ASSET_NOT_AVAILABLE/ROUTE_AMBIGUOUS 可留 L2 但错误码体系先建好），测试断言错误码字符串而非仅异常类型。

## 3. 修复边界（给 Feature Pilot）

- 仅在 modules/knowledge-architecture 的 gkke 包内修复 + 增补测试/测试资源；仍 reuse_only，不得改 specs/ 与 generated/。
- 修 Q2 时以 `specs/gk-ke/v1/schemas/KnowledgeMap.schema.json` 为唯一准绳；可新增该 schema 的正例资源做反序列化对齐测试。
- 修复后重跑本报告 §1 的模块全量命令，67+ 测试全绿，并新增覆盖 Q1/Q2/Q3 的用例。
- 不要求重跑 dependency-check（基线问题归 GKB）。

## 4. 结论

**不予 QA_PASS，退回 gk1-pilot-resume 修复 Q1/Q2/Q3。** 修复提交后重新申请独立 QA。
