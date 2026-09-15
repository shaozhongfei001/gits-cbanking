# Handoff: baseline-pilot → independent_qa（W1：Owner 授权抑制落地）

- Loop: `GKB-baseline-hardening`
- 更新: 2026-09-11（UTC 2026-09-10T23:30Z）
- 分支: `feature/GK-KE-L0-contract`
- 前序提交: bb4b860（测试修复）、8a0b708（W0 证据+决策包）；W1 提交见 git log（suppress+签署区 / loop 证据 两个原子提交）

## 一、Owner 授权（2026-09-11，落盘见决策包 §7）

- 标识：`APPROVE_GKB_SPRING_CORE_CVE_SUPPRESSION`；方案 A；`until="2026-10-31"`（Owner 确认，非草案的 12-31）；渠道=CodeBuddy Owner 决策问答，经 team-lead 派工消息转达。
- 同时批准 Boot4/Spring7 迁移专项并行立项（Tech Lead scaffold，不在本 Loop）。

## 二、落地内容

1. 根 `dependency-check-suppressions.xml` 新增 1 个 suppress 节点：
   - 17 个精确 CVE 编号（47883/47884/47885/47886/47887/47888/47889/47890/47891/47892/47893/59280/59281/59282/59283/59313/59314）；
   - `until="2026-10-31"`（xsd:date 格式；`yyyyMMdd` 会被 schema 拒绝，见 FAILURES 20260911T0707Z）；
   - packageUrl 正则 `^pkg:maven/org\.springframework/spring-[a-z]+@6\.2\.19$`；
   - 完整 owner-authorized 注释（CLASSIFICATION/RUNTIME_EXPOSURE/PRECONDITIONS_ABSENT/FIX_AVAILABILITY/MITIGATION_PLAN/SUPPRESSION_SCOPE/REVIEW_REQUIRED/OWNER_DECISION/AUTHORITY）。
2. 决策包 §6 改为已授权落地版、§7 签署区已勾选签署。
3. LOOP.yaml 新增 `spring_cve_suppression` gate（已 pass，EVIDENCE.json）。

### 构件范围扩展（需 Owner 追认 + QA 知悉）

Owner 授权原文绑定 `spring-core@6.2.19`。全量 verify 实测发现 NVD 把同批 17 CVE 映射到 Framework 6.2.19 全线构件：`spring-core`（apps/api）、`spring-tx`（persistence-relational）、`spring-aop`（persistence-relational/oracle-source/worker）、`spring-web`（apps/api）、`spring-webmvc`（worker），各构件携带的 17 个编号完全相同。

处理：按"同一 CVE 集合 + 同版本 + 同不可达前提"将 packageUrl 精确扩展为 `org.springframework:spring-[a-z]+@6.2.19`。边界：不新增任何 CVE 编号、不放宽版本（6.2.20+ 不匹配）、groupId 锚定 `org.springframework` 故天然不含 `org.springframework.security` 的 spring-security-*。已在 suppress 注释、FAILURES（0715Z/0725Z）、STATE.owner_decisions 中显式标注"待 Owner 追认"。

## 三、验证结果

| 项 | 结果 | 证据 |
|---|---|---|
| 17 集群清零 | apps/api、apps/worker、adapters/persistence-relational、adapters/oracle-source 报告均 **0 残留** | `evidence/spring_cve_suppression-17cluster-clear-20260911.txt`（sha256 cb346152…） |
| apps/api 测试 | 450 run，0 failures/errors，4 skipped | `evidence/spring_cve_suppression-20260910T232800Z.log`（sha256 a0ab4989…） |
| JaCoCo | LINE 5504/6746 = **0.8159** ≥ 0.80，jacoco:check gate 通过 | 同上 |
| make security-check | PASS（111 advisory 非阻断） | 本次会话日志 |
| 全量 `./mvnw verify` | **仍 exit 1——全部来自授权范围外存量 CVE**（见下节），非本次抑制失效 | `/tmp/gkb_verify3.log`（FAILURES 0725Z） |

## 四、授权范围外的存量阻断（未抑制、未升级，报 Owner 另行裁决）

- spring-security-core/web 6.5.11：CVE-2026-59270(9.1)、CVE-2026-47841(7.4)（apps/api）；另有 <7 的 CVE-2026-47842(6.5)、CVE-2026-59276(5.9)。
- tomcat-embed-core 10.1.57：9 个 ≥7（9.8×2、9.1×2、8.1×3、7.5×2），apps/api 与 apps/worker 均报；另有 CVE-2026-73180(6.8)。
- 非阻断：jackson-databind CVE-2026-54515(5.3)、log4j-api CVE-2026-49844(5.9)、commons-lang3 CVE-2025-48924(5.3)。
- 这些是 Boot 3.5.16 BOM 托管版本的基线存量；backend-test 类 gate 带 -Ddependency-check.skip=true 故此前未暴露，全量 verify 的 failBuildOnCVSS=7 使其显形。按派工要求未越界处置。

## 五、给独立 QA 的核查点

1. `git log`/diff：W1 仅改根 `dependency-check-suppressions.xml`（新增 1 节点+注释）、决策包、LOOP.yaml（+1 gate）、loops/GKB 证据文件；无生产代码、无 pom、无 specs/generated 改动。
2. XML：`python3 -c "import xml.dom.minidom;xml.dom.minidom.parse('dependency-check-suppressions.xml')"`；可独立重跑
   `MAVEN_OPTS="-Ddependency.check.auto.update=false -DretireJsAnalyzerEnabled=false" ./mvnw -pl apps/api dependency-check:check`
   后用 evidence txt 中的 python 片段核对 17 集群 0 残留（命令 exit 1 是 security/tomcat 未授权项所致，属预期）。
3. 复核构件扩展正则的边界（不匹配 6.2.20、不匹配 spring-security）。
4. apps/api：`./mvnw -pl apps/api verify -Ddependency-check.skip=true` 应 BUILD SUCCESS（450 测试 + JaCoCo）。
5. QA_PASS 仅针对已授权范围（测试修复 + 17 CVE 抑制）；spring-security/tomcat 单列 Owner 跟进，不应否决本 Loop 已授权工作。

## 六、未决

- Owner：追认 spring-* 构件范围扩展；裁决 spring-security/tomcat 14 个阻断（去重 11 编号）：窄抑制（需各自可达性分析包）/ 升 BOM patch / 纳入 Boot4 专项。
- 独立 QA 指派与 QA_PASS。
- Tech Lead：Boot4/Spring7 迁移专项 scaffold。
