# BLOCKED — GK1-registry-map-core

- **报告时间**: 2026-09-10T16:05Z
- **报告角色**: gk1-pilot-resume（implementation_actor）
- **阻断 Gate**: backend_test（G5）
- **阻断类型**: 安全隐患（存量高危 CVE，无已发布修复版，dev 角色无权豁免）

## 已完成（5/7 gate PASS）

| Gate | 状态 | 说明 |
|------|------|------|
| contract_check | PASS | 合同只读校验 |
| registry_core | PASS | 14 测试：注册/不可变/语义版本/过滤/发布快照/依赖闭包 |
| map_dag_validate | PASS | 8 测试：入口/边端点/环检测/可达子图 |
| permission_filter | PASS | 12 测试：scope 匹配/决议短路/投影不泄密 |
| plan_canonical_hash | PASS | 13 测试：含 Python 黄金字节跨语言对齐 |
| backend_test | **BLOCKED** | 见下 |
| security_check | PASS | secret-scan / sensitive-permissions / oracle-guard 全 PASS |

实现代码全部在 `modules/knowledge-architecture` 下新增 `com.gien.gits.knowledge.gkke`
包（registry/map/permission/plan + model），未改 specs/generated/pom 受控文件。

## 阻断详情

### 阻断 1（硬阻塞）：spring-core 6.2.19 命中 17 个 CVE≥7，无 GA 修复版

- `make backend-test` → dependency-check:check（failBuildOnCVSS=7, failOnError=true）
  在 `adapters/persistence-relational` 失败：spring-core-6.2.19.jar（Spring Boot 3.5.16 BOM）
  命中 6 CRITICAL + 9 HIGH + 1 MEDIUM + 1 LOW（confidence=HIGH）。
- 存量问题：基线 c7017b1 即如此；CVE 发布于 2026-08-27，NVD 本地库 2026-09-10 更新后纳入。
- 无修复版：NVD 修复边界 6.2.20；Maven Central 最新 GA = 6.2.19；
  6.2.20-SNAPSHOT（2026-06-08 构建）早于 CVE，不含修复。
- 可达性：14/17 个 CVE 需 WebFlux/RSocket/XsltView/FreeMarker/SpEL 编译器等本项目
  不具备的条件（servlet MVC 栈，已 grep 验证），但 fail-closed 扫描不区分可达性。
- 详见 `FAILURES.md` FAIL-2026-09-10-02。

### 阻断 2（存量，旁路记录）：apps/api EngagementJourneyControllerTest 4 errors

- `@WebMvcTest` 切片缺 `CustomerJourneyRepository` bean；基线 c7017b1 干净 worktree
  复现同一失败，非本 Loop 引入。详见 FAIL-2026-09-10-03。

## 已执行的自愈/降级

1. RetireJS 离线下载超时 → `-DretireJsAnalyzerEnabled=false`（纯 Java 项目，
   NVD analyzer + guard 保持启用），已解决（FAIL-2026-09-10-01）。
2. 升级 spring-core：联网确认无 GA 修复版，SNAPSHOT 不含修复 → 不可行。
3. 全量 verify `-Ddependency-check.skip=true` 旁路验证：除存量 4 errors 外，
   全部模块编译/测试通过，本 Loop 代码无回归。

## 请求 Owner/Tech Lead 决策（三选一）

1. **授权窄抑制**：在 `dependency-check-suppressions.xml` 按 CVE 逐条抑制
   （带 until 过期时间，6.2.20 GA 后移除），参照 P20 owner-authorized 先例；
2. **等待修复版**：6.2.20 GA 发布后升级 Spring Boot BOM，再重跑 backend_test；
3. **其它修复路径**（如 Owner 指定内部补丁仓库/可达性分析豁免流程）。

决策前 backend_test 无法变绿，Loop 保持 in_dev，不交接 independent_qa。
