# W0｜Iteration log（append-only）

由 `scripts/record_gate.py` 追加实际attempt、命令、退出码、证据hash和下一动作。没有实际执行不得登记PASS。

## Attempt 1｜20260910T162648Z

- Gate: `repro_baseline`
- Command: `./mvnw --batch-mode --no-transfer-progress -pl apps/api -am test -Dtest=EngagementJourneyControllerTest -Ddependency-check.skip=true`
- Exit: `1`
- Evidence: `loops/GKB-baseline-hardening/evidence/repro_baseline-20260910T162648Z.log`
- SHA256: `35ac18da6b303a344edb103cf916c0fbbac4f2ca4edf79a90cf1ee13f8c95c33`

## Attempt 2｜20260910T162825Z

- Gate: `repro_baseline`
- Command: `./mvnw --batch-mode --no-transfer-progress -pl apps/api -am test -Dtest=EngagementJourneyControllerTest -Dsurefire.failIfNoSpecifiedTests=false -Ddependency-check.skip=true`
- Exit: `1`
- Evidence: `loops/GKB-baseline-hardening/evidence/repro_baseline-20260910T162825Z.log`
- SHA256: `3b9cd6a7783daea8078bb1fe9e018c788612bcf70fcc17b0b0ff5879b6069db4`

## Attempt 1｜20260910T162957Z

- Gate: `fix_test_slice`
- Command: `./mvnw --batch-mode --no-transfer-progress -pl apps/api -am test -Dtest=EngagementJourneyControllerTest -Dsurefire.failIfNoSpecifiedTests=false -Ddependency-check.skip=true`
- Exit: `0`
- Evidence: `loops/GKB-baseline-hardening/evidence/fix_test_slice-20260910T162957Z.log`
- SHA256: `ee79c52bfb6d40310d83c403c6cdf78a77f28fc4b6362fbcdcddd82a828ebab0`

## Attempt 1｜20260910T163012Z

- Gate: `apps_api_regression`
- Command: `./mvnw --batch-mode --no-transfer-progress -pl apps/api -am test -Ddependency-check.skip=true`
- Exit: `0`
- Evidence: `loops/GKB-baseline-hardening/evidence/apps_api_regression-20260910T163012Z.log`
- SHA256: `0565d89b1df86d722d3eb7eeec10d32b7fbad6314042f8ab6fb213160a14abdf`

## Attempt 1｜20260910T163844Z

- Gate: `spring_cve_decision_package`
- Command: `test -s loops/GKB-baseline-hardening/evidence/SPRING_CORE_CVE_DECISION.md`
- Exit: `0`
- Evidence: `loops/GKB-baseline-hardening/evidence/spring_cve_decision_package-20260910T163844Z.log`
- SHA256: `ade49f90061899414168c314a21265be5bf25ef5c8e34828e7568aee0cbb5927`

## Attempt 1｜20260910T163850Z

- Gate: `security_check`
- Command: `make security-check`
- Exit: `0`
- Evidence: `loops/GKB-baseline-hardening/evidence/security_check-20260910T163850Z.log`
- SHA256: `7c03997f0064499301ea053b5a7fb24b63749f4572ee1038098861dffa7e8a1f`
