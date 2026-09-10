# NEXT SESSION｜GK1-registry-map-core

| 字段 | 值 |
|---|---|
| **holder** | `gk1-pilot-resume` |
| **wave** | `W0` |
| **gate** | `backend_test`（attempt 3 失败，剩 2 次） |
| **state** | `blocked`（安全硬阻塞，等待 Owner 决策，见 `memory/BLOCKED.md`） |

> Baton 名义 holder 为 `gk1-pilot-resume`（loop_guard 要求 blocked 状态 holder=implementation_actor）；
> 实际等待 Owner 对 spring-core CVE 处置三选一拍板，决策后由 gk1-pilot-resume 继续 attempt 4。

## 阻塞（必读 memory/BLOCKED.md）

`backend_test` 的 OWASP dependency-check（CVSS≥7 阻断）命中存量 `spring-core 6.2.19`
（Spring Boot 3.5.16 BOM）的 12 个真实 CVE-2026-*（7.5–9.8，2026-08-20/27 发布）。
- 6.2.x 修复版 6.2.20 为 Spring 企业支持专属（Maven Central 404）；OSS 修复需 7.0.9（= Boot 4 大版本迁移）。
- 与本 Loop 无关（本 Loop 仅加 test scope jackson-databind；主仓同版本）。
- 12 个漏洞路径在本代码库均不可达（纯 servlet MVC + Tomcat + JSON，无 WebFlux/RSocket/SSE/XsltView/用户 SpEL/表单绑定）。

## Owner 三选一

- A（推荐）：书面授权在 `dependency-check-suppressions.xml` 加 12 条抑制（注明不可达+无 OSS 修复+技术债跟进 Boot4），参照 P20 Tomcat 先例。
- B：提供 Spring 企业仓库坐标/凭据，pin spring-framework BOM 6.2.20。
- C：批准 Boot 4 / Spring 7.0.9 大版本迁移（单开 Loop）。

## Owner 决策后（gk1-pilot-resume 继续）

1. 方案 A：加抑制 → `export MAVEN_OPTS="-Ddependency.check.auto.update=false -DretireJsAnalyzerEnabled=false"` →
   `python3 scripts/record_gate.py --loop GK1-registry-map-core --gate backend_test --actor gk1-pilot-resume --actor-role implementation`（attempt 4）。
2. backend_test 绿后收工：STATE→ready_for_independent_qa、baton→independent_qa、
   写 handoff、`python3 scripts/loop_guard.py --loop GK1-registry-map-core --memory-only`、
   显式 git add + commit（`feat(GK1): registry+map core CR-02 T05/T06/T07/T20`，footer `Loop: GK1-registry-map-core`）。

## 已完成（6/7 gate）

contract_check / registry_core / map_dag_validate / permission_filter / plan_canonical_hash（前任 gk1-pilot）；
security_check（gk1-pilot-resume，PASS）。gkke 14 测试类 63 项单测在 attempt 3 全绿。

## 边界

reuse_only：禁改 `specs/` 与 `generated/`；禁实现 T17/REST；禁 `git add .`；禁自签 QA_PASS。
