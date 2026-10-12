# GKB-baseline-hardening｜Next Session Baton

| 字段 | 值 |
|---|---|
| **Updated** | `2026-09-10T23:30:00+00:00` |
| **holder** | `baseline-pilot` |
| **packet** | `GKB-baseline-hardening` |
| **wave** | `W1`（Owner 授权方案 A 已落地，待独立 QA） |
| **do_not_start** | QA_PASS（仅独立 QA 可记录）、REAL_E2E_PASS、BUSINESS_SIGNED；未经 Owner 授权不得抑制 spring-security/tomcat 存量 CVE、不得改 pom 版本 |

## 上一波完成情况（baseline-pilot，2026-09-11）

- Owner 书面授权 `APPROVE_GKB_SPRING_CORE_CVE_SUPPRESSION`（方案 A，until=2026-10-31，渠道=CodeBuddy Owner 决策问答），并批准 Boot4/Spring7 迁移专项并行立项。
- 抑制已落地根 `dependency-check-suppressions.xml`：17 个精确 CVE 编号 + packageUrl `^pkg:maven/org\.springframework/spring-[a-z]+@6\.2\.19$`（实施时发现 NVD 把同批 CVE 映射到 spring-core/tx/web/aop/webmvc 全线构件，从授权原文 spring-core 精确扩展，不新增 CVE、不放宽版本、不含 spring-security，待 Owner 追认）。
- 验证：4 个模块（apps/api、apps/worker、adapters/persistence-relational、adapters/oracle-source）dependency-check 报告中 17 集群**零残留**（证据 `evidence/spring_cve_suppression-17cluster-clear-20260911.txt`）；apps/api verify（跳 dependency-check）BUILD SUCCESS，450 测试全绿，JaCoCo LINE 0.8159 ≥ 0.80；`make security-check` PASS。
- gate `spring_cve_suppression`=pass（EVIDENCE.json，output_sha256 a0ab4989…）。
- 全量 `./mvnw verify` 仍 exit 1，阻断项全部是 **Owner 授权范围外的存量 CVE**（未抑制、未升级，保持显式可见）：spring-security-core/web 6.5.11 的 CVE-2026-59270(9.1)/CVE-2026-47841(7.4)，tomcat-embed-core 10.1.57 的 9 个 ≥7（9.8×2、9.1×2、8.1×3、7.5×2）。已报 team-lead 转 Owner 裁决。

## 下一 holder 待办

1. **独立 QA**：复核测试切片修复（bb4b860）与抑制落地（本次提交）；独立重跑 17 集群清零检查与 apps/api verify；记录 QA_PASS 到 `EVIDENCE.json.independent_qa`。
2. **Owner（并行，不阻塞 QA 对已授权范围的复核）**：对 spring-security/tomcat 14 个阻断 CVE（去重后 11 个编号）裁决（窄抑制/升级版本/Boot4 专项内消化）；追认 spring-* 构件范围扩展。
3. Tech Lead：scaffold Boot4/Spring7 迁移专项 Loop。

短提示词：你是独立 QA。先读 `memory/handoffs/baseline-pilot.md`、`evidence/SPRING_CORE_CVE_DECISION.md` §6/§7 与 `evidence/spring_cve_suppression-17cluster-clear-20260911.txt`；已授权范围（测试修复 + 17 CVE 抑制）可独立复核签 QA_PASS；spring-security/tomcat 是授权外事项，不要因此否决本 Loop 已授权工作，单列 Owner 跟进。
