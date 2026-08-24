# W0｜Iteration log（append-only）

由 `scripts/record_gate.py` 追加实际attempt、命令、退出码、证据hash和下一动作。没有实际执行不得登记PASS。

## Attempt 1｜20260822T141952Z

- Gate: `unit_product`
- Command: `./mvnw -pl apps/api -am -Dsurefire.failIfNoSpecifiedTests=false -Dtest=ProductMatchingServiceTest,FallbackSkillExecutionAdapterTest test`
- Exit: `0`
- Evidence: `loops/P29-gits-product-skill/evidence/unit_product-20260822T141952Z.log`
- SHA256: `d9d8bb2b50b355d3e60dabe6a21ce9e7569c78a9e1607a34f9527a60d73ea404`

## Attempt 1｜20260822T142014Z

- Gate: `security_check`
- Command: `make security-check`
- Exit: `0`
- Evidence: `loops/P29-gits-product-skill/evidence/security_check-20260822T142014Z.log`
- SHA256: `464459f1233737b4a4127e3875f0d5290059f3a42f0d5230c4e098bd9e4bc96f`

## Attempt 1｜20260822T142100Z

- Gate: `cov_operating_view` (not in LOOP.yaml; optional Feature Pilot)
- Command: `npx vitest run src/views/__tests__/CustomerOperatingView.spec.ts`
- Exit: `0`
- Note: 4/0；empty matchProducts → KI-FRONT-006 hint

## Attempt 1｜20260822T142200Z

- Gate: `e2e_product_matching` (not in LOOP.yaml; optional Feature Pilot)
- Command: `./mvnw -pl apps/api -am -Dsurefire.failIfNoSpecifiedTests=false -Dtest=EngagementScenarioE2eIT#productMatchingBasedOnTransactions test`
- Exit: `0`
- Note: AT-009 identity-only；empty list OK when Skill down

