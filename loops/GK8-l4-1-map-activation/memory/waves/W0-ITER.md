# W0｜Iteration log（append-only）

由 `scripts/record_gate.py` 追加实际attempt、命令、退出码、证据hash和下一动作。没有实际执行不得登记PASS。

## Attempt 1｜20260911T183007Z

- Gate: `contract_generate`
- Command: `make generate`
- Exit: `0`
- Evidence: `loops/GK8-l4-1-map-activation/evidence/contract_generate-20260911T183007Z.log`
- SHA256: `048ab7c55cfbb3c6707b7212288bd84d678861d4abb19a7eca16fbb7a71803b8`

## Attempt 1｜20260911T183007Z

- Gate: `contract_check`
- Command: `make check`
- Exit: `0`
- Evidence: `loops/GK8-l4-1-map-activation/evidence/contract_check-20260911T183007Z.log`
- SHA256: `55219a6f7d13f17671131ed905d5adc07be683517f11c42152995b964516677d`

## Attempt 1｜20260911T183009Z

- Gate: `security_check`
- Command: `make security-check`
- Exit: `0`
- Evidence: `loops/GK8-l4-1-map-activation/evidence/security_check-20260911T183009Z.log`
- SHA256: `fc9f8abee1a86eaf0f6e0700a9a018f202bf3db7193f60222f02c90ed3dbe4e8`

## Attempt 1｜20260911T183010Z

- Gate: `gk_ke_examples`
- Command: `python3 scripts/gk_ke_contract_examples.py`
- Exit: `0`
- Evidence: `loops/GK8-l4-1-map-activation/evidence/gk_ke_examples-20260911T183010Z.log`
- SHA256: `2b19441f59a6819bada8b85d409add1bcf6ecf7764298e3aefd9b84d29417c4f`

## Attempt 1｜20260911T183010Z

- Gate: `gk_ke_openapi_lint`
- Command: `python3 scripts/gk_ke_openapi_contract_tests.py`
- Exit: `0`
- Evidence: `loops/GK8-l4-1-map-activation/evidence/gk_ke_openapi_lint-20260911T183010Z.log`
- SHA256: `237156c1be19e35854dd88438c5d24cf462b9e342c967bbe1a8666ee9246bf1a`

## Attempt 1｜20260911T183010Z

- Gate: `l4_1_map_activation_tests`
- Command: `python3 scripts/gk_ke_l4_1_map_activation_tests.py`
- Exit: `0`
- Evidence: `loops/GK8-l4-1-map-activation/evidence/l4_1_map_activation_tests-20260911T183010Z.log`
- SHA256: `8fcf569989ca5c98b778e8822004c124477d0d2148744a72c6011fca9acba688`

## Attempt 1｜20260911T183013Z

- Gate: `gk_ke_hash`
- Command: `./mvnw -q -pl modules/knowledge-architecture test -Dtest=CanonicalHashGoldenTest`
- Exit: `0`
- Evidence: `loops/GK8-l4-1-map-activation/evidence/gk_ke_hash-20260911T183013Z.log`
- SHA256: `bd167c094a5106e60556bfa7a815bd222d0dd40edd78d98796e664cd10f6132d`
