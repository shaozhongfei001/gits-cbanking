# spring-core 6.2.19 CVE 集群 Owner 决策包

- Loop: `GKB-baseline-hardening`
- 编制: baseline-pilot（implementation actor），2026-09-11
- 状态: **待 Owner 裁决（A/B/C 三选一）**。本包仅为决策材料，未落地任何豁免或版本变更。
- 红线声明: 编制者未修改 `dependency-check-suppressions.xml`，未修改任何 `pom.xml` 的 spring 版本。

## 1. 事实摘要

| 项 | 值 |
|---|---|
| 受扫描组件 | `org.springframework:spring-core:6.2.19`（apps/api 运行时 classpath） |
| 版本来源 | Spring Boot `3.5.16` BOM 托管（根 pom parent，未手工覆盖 spring 版本） |
| Web 栈 | Servlet + Spring MVC + 内嵌 Tomcat 10（`spring-boot-starter-web` / `spring-boot-starter-tomcat`），**无 WebFlux、无 RSocket、无 Jetty、无 WebSocket** |
| CVE 数量 | **17**（NVD，dependency-check 12.1.0，failBuildOnCVSS=7 → 构建阻断） |
| CVSS≥7 | 11 个（5×9.8 CRITICAL、1×9.1 CRITICAL、5×7.5 HIGH）；<7 共 6 个 |
| 披露日 | 全部为 **2026-08-20**（Spring Security Advisories 同日批量发布；NVD 本地库 2026-09-10 同步） |
| 扫描数据新鲜度 | NVD API Last Modified `2026-09-10T15:29:55Z`；报告生成 `2026-09-10T16:31:55Z` |
| 报告文件 | `apps/api/target/dependency-check-report.json`（805 KB，17 条均挂在 spring-core-6.2.19.jar） |
| 复现命令 | `MAVEN_OPTS=-Ddependency-check.auto.update=false ./mvnw -pl apps/api dependency-check:check` → exit 1（CVSS≥7 fail-closed） |

## 2. 17 个 CVE 清单

CVSS 取自 dependency-check 报告（NVD cvssv3 baseScore）；置信度均为 NVD 对 CPE `spring-core` 的**直接组件匹配（HIGH，非传递/文件名猜测）**；披露日均为 2026-08-20（Spring 官方公告 history: "2026-08-20 initial vulnerability report published"）。修复边界对所有 17 个一致：**7.0.9（OSS）/ 7.0.8.1、6.2.20、6.1.29、6.0.31、5.3.50（Enterprise Support Only）**。

| # | CVE | CVSS | 严重度 | 漏洞要点 | 本项目可达性结论 |
|---|---|---:|---|---|---|
| 1 | CVE-2026-47883 | 6.1 | MEDIUM | `UrlHandlerFilter` 宽泛模式开放重定向（MVC+WebFlux 变体） | **不可达**：代码中无 `UrlHandlerFilter` 使用（grep 0 命中），无自定义重定向 Filter |
| 2 | CVE-2026-47884 | 9.8 | CRITICAL | `XsltView` 路径限制不当 → SSRF/RCE；前提：`/**` 映射触发视图渲染且未显式指定视图名 | **不可达**：纯 `@RestController` JSON API，无 `@Controller` 视图渲染、无 XSLT 模板、无 `XsltView`（grep 0 命中，resources 下无 .xsl/.xhtml） |
| 3 | CVE-2026-47885 | 7.5 | HIGH | WebFlux `PartEventHttpMessageReader` 在 maxInMemorySize=-1 时不强制 maxPartSize | **不可达**：无 WebFlux 依赖（pom grep 0 命中），无 multipart/`@RequestPart`/`PartEvent` 端点 |
| 4 | CVE-2026-47886 | 7.5 | HIGH | 用户可控 SpEL 表达式中 `^` 对 BigDecimal/BigInteger 大指数 → DoS | **不可达**：无 `SpelExpressionParser`/`ExpressionParser` 编程式 SpEL 求值；仅有静态 `@Value("${...}")` 配置占位符（配置文件常量，非用户输入） |
| 5 | CVE-2026-47887 | 6.1 | MEDIUM | MVC `UrlFileNameViewController` 行尾映射且无 prefix → 开放重定向 | **不可达**：无 `UrlFileNameViewController` 使用（grep 0 命中），无视图控制器注册 |
| 6 | CVE-2026-47888 | 7.5 | HIGH | RSocket 畸形 SETUP 帧内存泄漏 | **不可达**：无 RSocket 依赖/`@MessageMapping`（pom+java grep 0 命中） |
| 7 | CVE-2026-47889 | 7.5 | HIGH | WebFlux on Jetty 12 Core 响应 cookie 丢失 sameSite | **不可达**：无 WebFlux、无 Jetty（内嵌容器为 Tomcat，pom grep jetty 0 命中） |
| 8 | CVE-2026-47890 | 9.8 | CRITICAL | MVC/WebFlux SSE + view fragments 流损坏 | **不可达**：无 SSE（`SseEmitter`/`ServerSentEvent`/`text/event-stream` grep 0 命中）、无视图片段 |
| 9 | CVE-2026-47891 | 9.8 | CRITICAL | WebFlux Aalto XML 解析不强制 maxInMemorySize | **不可达**：无 WebFlux、无 Aalto、无 XML 请求体端点（API 全部 JSON） |
| 10 | CVE-2026-47892 | 9.8 | CRITICAL | WebFlux 函数式端点部署于 DispatcherServlet 时 pre-flight header predicate 绕过 | **不可达**：无 WebFlux、无函数式端点（`RouterFunction` grep 0 命中）；CORS 走 Spring Security 配置 |
| 11 | CVE-2026-47893 | 7.5 | HIGH | WebFlux WebSocket 异常 reason 回显请求头 → 敏感信息泄露 | **不可达**：无 WebFlux、无 WebSocket 端点 |
| 12 | CVE-2026-59280 | 4.3 | MEDIUM | FreeMarker `SpringTemplateLoader` + 不可信视图名 → 路径遍历 | **不可达**：无 FreeMarker 依赖/配置（pom grep 0 命中）、无 .ftl 模板、无视图名返回 |
| 13 | CVE-2026-59281 | 6.1 | MEDIUM | 数据绑定 Errors + HTML 转义下无参 getFieldErrors → 反射型 XSS | **不可达**：无表单绑定（`@InitBinder`/`WebDataBinder`/`@ModelAttribute` grep 0 命中）、无服务端 HTML 渲染（纯 JSON API + 独立 Vue 前端） |
| 14 | CVE-2026-59282 | 7.5 | HIGH | 数据绑定对用户提供属性路径 → DoS | **不可达**：无表单/命令对象数据绑定；入参全部为 `@RequestBody` JSON 反序列化（19 处，Jackson），不走 WebDataBinder property-path 机制 |
| 15 | CVE-2026-59283 | 9.1 | CRITICAL | `SimpleEvaluationContext` SpEL 在表达式编译器激活时安全守卫绕过（+类加载无限增长） | **不可达**：无编程式 SpEL 求值，未设置 `spring.expression.compiler.mode`（grep 0 命中，默认 OFF） |
| 16 | CVE-2026-59313 | 9.8 | CRITICAL | MVC 函数式 Web（RouterFunction + SSE 纯文本）流损坏 | **不可达**：无 `RouterFunction`、无 SSE（grep 0 命中） |
| 17 | CVE-2026-59314 | 3.7 | LOW | 不可信输入构造 Content-Disposition → HTTP response splitting（恶意文件名） | **不可达**：无文件下载/上传端点（`MultipartFile`/`ContentDisposition` grep 0 命中），无代码以用户输入构造 Content-Disposition 头 |

### 可达性分析方法与证据

- 依赖面：`grep -rn 'spring-boot-starter-webflux|spring-webflux|rsocket|jetty|freemarker' --include=pom.xml` → 0 命中；`dependency:list` 确认 apps/api 仅含 spring-boot-starter-web(tomcat)、spring-security、actuator、jdbc、json。
- 代码面（`apps modules adapters scenario`，排除 target）：`UrlHandlerFilter|XsltView|UrlFileNameViewController|SseEmitter|ServerSentEvent|RouterFunction|PartEvent|RSocket|WebSocket|@MessageMapping|MultipartFile|@RequestPart|ContentDisposition|@InitBinder|WebDataBinder|@ModelAttribute|SpelExpressionParser|SimpleEvaluationContext` → 全部 0 命中。
- 配置面：无 `spring.expression.compiler.mode`、无 multipart 自定义配置、无模板引擎配置；actuator 仅暴露 `health,info,metrics,prometheus`（prod 为 health,info,prometheus）。
- 架构面：后端为无状态 JSON REST API（`@RestController` + `@RequestBody` Jackson），无服务端视图/HTML/表单；前端为独立 Vue3 SPA。17 个 CVE 的利用前提（WebFlux / RSocket / Jetty12 / XSLT 视图 / FreeMarker / SSE 函数式端点 / 用户可控 SpEL / 表单数据绑定 / 文件头注入）在本部署形态均不存在。
- 残留风险（诚实声明）：① 结论基于当前代码库静态核查，未来若引入 WebFlux、multipart、SpEL 求值或视图渲染需重新评估；② dependency-check 按 CPE 组件匹配，无法判定调用路径，"不可达"是工程判断而非扫描器结论；③ 6 个 <7 的 CVE 不阻断构建但同样未修复。

## 3. 修复版本可得性证据（2026-09-11 实测 Maven Central + Spring 官方公告）

| 版本线 | 修复版本 | Maven Central OSS 可得性 | 证据 |
|---|---|---|---|
| 7.0.x | **7.0.9** | **可得（OSS 唯一修复路径）** | `https://repo1.maven.org/maven2/org/springframework/spring-core/7.0.9/` 存在；Spring 公告标注 OSS |
| 7.0.x | 7.0.8.1 | 不可得（Enterprise Support Only） | Spring 公告标注 |
| 6.2.x（当前线） | **6.2.20** | **不可得（Enterprise Support Only）** | Central `.../spring-core/6.2.20/spring-core-6.2.20.pom` → **HTTP 404**（实测）；metadata 中 6.2.x 最新 GA=6.2.19 |
| 6.1.x | 6.1.29 | 不可得（Enterprise Support Only） | Central 6.1.x 最新 GA=6.1.21，**仍落在受影响范围 6.1.0–6.1.28 内**，降级 6.1.x 无安全收益 |
| 6.0.x / 5.3.x / 5.2.x | 6.0.31 / 5.3.50 / 5.2.26 | 不可得（Enterprise Support Only） | Spring 公告标注 |
| Spring Boot | 当前 3.5.16（Framework 6.2.19）；Boot 4.0.x→Framework 7.0.x，Boot 4.1.1 已在 Central | Boot 3.5.x 线无 OSS Framework 修复；要拿 7.0.9 必须升 Boot 4.x | Central spring-boot metadata：4.0.6–4.0.8、4.1.0、4.1.1 已发布 |

官方公告（抽查 CVE-2026-47884 / 47883 / 59283 / 59313，修复矩阵完全一致）："Affected: 7.0.0-7.0.8, 6.2.0-6.2.19, 6.1.0-6.1.28 …；Fixed: 7.0.9 (OSS), 6.2.20/6.1.29/… (Enterprise Support Only)"，且均称"升级即可，无需其他缓解"。

## 4. 三方案利弊

### 方案 A：窄抑制（精确 17 CVE + `until` 到期日），暂不升级

- 做法：Owner 书面授权后，在 `dependency-check-suppressions.xml` 增加一个精确绑定 `spring-core@6.2.19` + 17 个 CVE 编号的 suppress 节点，带 `until="2026-12-31"`（建议），注释字段沿用 P20 owner-authorized 格式（CLASSIFICATION / RUNTIME_EXPOSURE / PRECONDITIONS_ABSENT / OWNER_DECISION / AUTHORITY / REVIEW_DATE）。
- 利：① 立即解除构建阻断，GKB/GK1 等 Loop 的 backend-test 恢复绿色；② 与项目既有 P20/P22 豁免治理一致，可审计、有到期日；③ 17 项经逐项核查在当前架构均不可达，残余风险低；④ 零代码/零运行时变更，无回归面。
- 弊：① 抑制是风险接受而非消除，依赖"不可达"判断的持续有效性；② 需登记到期复核，防止技术债永久化；③ 审计上需向 Owner/安全方说明"组件有 CVE 但路径不可达"。
- 适用：当前（Boot 3.5.x 线无 OSS 补丁、升 Boot 4 代价大）最务实。

### 方案 B：等待 6.2.x OSS 修复版本（6.2.20 GA）后升级

- 做法：不改任何文件，持续跟踪 Maven Central；一旦 6.2.20（或 Boot 3.5.x 携带修复 Framework 的 BOM）在 OSS 发布，升 BOM 版本并解除阻断。
- 利：真正消除组件漏洞，不承担豁免风险，升级面小（同 6.2.x patch + Boot 3.5.x patch）。
- 弊：① **6.2.20 已被 VMware/Broadcom 明确划为 Enterprise Support Only，OSS 渠道可能永远不发布**——等待可能无限期；② 等待期内 `make verify`/backend-test 持续被 fail-closed 阻断，所有 Loop 受阻；③ 无确定 ETA，无法排期。
- 适用：Owner 持有 Spring Enterprise 合同（可直接获取 6.2.20），或愿在阻断期内全部 Loop 停摆。

### 方案 C：升级 Spring Boot 4.x（Framework 7.0.9）

- 做法：parent 升 Spring Boot 4.1.x（Framework 7.0.9），全量回归 + 第三方依赖兼容性验证（Jakarta 基线、Spring Security 7、配置属性迁移、MyBatis Spring Boot 3.0.4 / spring-modulith 1.4.12 / Jena 等兼容性）。
- 利：唯一在 OSS 渠道**真正修复全部 17 CVE** 的路径，且一次性跨越到新主线。
- 弊：① 大版本迁移（Boot 3.5→4.x、Framework 6.2→7.0、Security 6→7），非补丁升级；② 需独立专项 Loop 做兼容性矩阵与全量 E2E，工作量与回归风险显著；③ 可能被迫同步升级 MyBatis starter、Modulith 等生态组件；④ 不适合在"基线加固"Loop 内顺带完成。
- 适用：Owner 决策排期一个专门的 Boot4 迁移 Loop（建议中期规划）。

## 5. 建议（编制者推荐，供 Owner 裁决）

**推荐方案 A（窄抑制 + until 2026-12-31）作为即时措施，并并行立项方案 C（Boot 4 迁移专项）作为根治路径；方案 B 仅在 Owner 持有 Spring Enterprise 支持合同时改为首选。**

理由：
1. 17 个 CVE 经逐项静态核查，利用前提（WebFlux/RSocket/Jetty12/XSLT/FreeMarker/SSE/用户 SpEL/表单绑定/文件头）在本项目 Servlet+JSON 架构下全部不存在，当前实际暴露风险低；
2. 当前 Boot 3.5.x OSS 线无 Framework 修复（6.2.20 企业专属，实测 Central 404），方案 B 无确定 ETA 且阻断期不可接受；
3. 方案 C 是正确根治方向但工作量属于专项迁移，不应在基线加固 Loop 内仓促进行；
4. 方案 A 与仓库 P20/P22 既有 owner-authorized 豁免治理一致，精确绑定 + until 到期保证风险接受可审计、可回收。

到期/触发复核条件（建议写入豁免注释）：2026-12-31 到期；或以下任一先发生时立即复核——(a) 引入 WebFlux/multipart/SpEL 求值/服务端视图；(b) Boot 3.5.x OSS 线发布携带修复 Framework 的 BOM；(c) Boot4 迁移 Loop 完成。

## 6. 可直接采用的抑制 XML 草案（**草案，未落地**；需 Owner 书面授权后由实施角色写入 `dependency-check-suppressions.xml`）

```xml
  <!--
    spring-core 6.2.19 CVE 集群窄抑制（CLASSIFICATION=VULNERABLE_CODE_PATH_NOT_REACHABLE）
    AFFECTED_COMPONENT=org.springframework:spring-core@6.2.19（Spring Boot 3.5.16 BOM 托管）
    CVE_SCOPE=下列 17 个 CVE only（2026-08-20 Spring Security Advisories 同批披露），精确绑定，无宽泛正则：
      CVE-2026-47883(6.1) CVE-2026-47884(9.8) CVE-2026-47885(7.5) CVE-2026-47886(7.5)
      CVE-2026-47887(6.1) CVE-2026-47888(7.5) CVE-2026-47889(7.5) CVE-2026-47890(9.8)
      CVE-2026-47891(9.8) CVE-2026-47892(9.8) CVE-2026-47893(7.5) CVE-2026-59280(4.3)
      CVE-2026-59281(6.1) CVE-2026-59282(7.5) CVE-2026-59283(9.1) CVE-2026-59313(9.8)
      CVE-2026-59314(3.7)
    RUNTIME_STACK=Servlet + Spring MVC + 内嵌 Tomcat（spring-boot-starter-web），纯 @RestController JSON API
    PRECONDITIONS_ABSENT（逐项 grep 核查，0 命中）：
      - 无 spring-webflux / RSocket / Jetty12 / WebSocket 依赖与端点
      - 无 XsltView / FreeMarker / 任何服务端视图渲染（无 @Controller、无 .xsl/.ftl 模板）
      - 无 SSE（SseEmitter/ServerSentEvent/text-event-stream）、无 RouterFunction 函数式端点
      - 无编程式 SpEL 求值（仅静态 @Value 配置占位符），spring.expression.compiler.mode 未设置
      - 无表单数据绑定（@InitBinder/WebDataBinder/@ModelAttribute），入参全为 @RequestBody JSON(Jackson)
      - 无 multipart 文件上传/下载，无用户输入构造 Content-Disposition
    FIX_AVAILABILITY=OSS 无 6.2.x 修复：6.2.20 为 Enterprise Support Only（Maven Central 实测 404，
      6.2.x OSS 最新 GA=6.2.19）；唯一 OSS 修复为 Framework 7.0.9，需 Spring Boot 4.x 专项迁移。
    MITIGATION_PLAN=2026-12-31 到期复核；触发提前复核：引入上述任一攻击面 / Boot 3.5.x OSS 发布修复 BOM /
      Boot4 迁移 Loop 完成。根治路径见 loops/GKB-baseline-hardening/evidence/SPRING_CORE_CVE_DECISION.md 方案 C。
    SUPPRESSION_SCOPE=spring-core@6.2.19 下列 17 CVE only，不抑制 spring-core 其它版本或其它 CVE
    REVIEW_REQUIRED=YES，REVIEW_DATE=2026-09-11
    OWNER_DECISION=PENDING_OWNER_AUTHORIZATION（Owner 批准后替换为正式决策标识，如 APPROVE_GKB_SPRING_CORE_CVE_SUPPRESSION）
    AUTHORITY=Spring Security Advisories https://spring.io/security/cve-2026-47884 等 17 篇（2026-08-20）；
      Maven Central maven-metadata（2026-09-11 实测）；dependency-check 12.1.0 报告 apps/api/target/dependency-check-report.json
  -->
  <suppress until="20261231">
    <packageUrl regex="true">^pkg:maven/org\.springframework/spring-core@6\.2\.19$</packageUrl>
    <cve>CVE-2026-47883</cve>
    <cve>CVE-2026-47884</cve>
    <cve>CVE-2026-47885</cve>
    <cve>CVE-2026-47886</cve>
    <cve>CVE-2026-47887</cve>
    <cve>CVE-2026-47888</cve>
    <cve>CVE-2026-47889</cve>
    <cve>CVE-2026-47890</cve>
    <cve>CVE-2026-47891</cve>
    <cve>CVE-2026-47892</cve>
    <cve>CVE-2026-47893</cve>
    <cve>CVE-2026-59280</cve>
    <cve>CVE-2026-59281</cve>
    <cve>CVE-2026-59282</cve>
    <cve>CVE-2026-59283</cve>
    <cve>CVE-2026-59313</cve>
    <cve>CVE-2026-59314</cve>
  </suppress>
```

注：`until` 属性格式为 `yyyyMMdd`（dependency-check 12.x 规范）；若 Owner 希望同时覆盖其它模块（worker/scenario 等）classpath 上的同一组件，packageUrl 正则可保持 `@6\.2\.19$` 精确版本不变而天然覆盖所有模块——但建议批准后先跑一次全量 `verify` 确认各模块报告均不再报这 17 项。

## 7. 附：决策签署区（Owner 填写）

- [ ] 方案 A 批准（请给出正式 OWNER_DECISION 标识与 until 日期确认）
- [ ] 方案 B（持有 Enterprise 合同 / 接受等待与阻断）
- [ ] 方案 C（批准 Boot4 迁移专项 Loop 排期）
- Owner: ____________ 日期: ________ 书面授权位置: ________
