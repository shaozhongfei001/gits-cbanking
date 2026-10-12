# W0｜Iteration log（append-only）

由 `scripts/record_gate.py` 追加实际attempt、命令、退出码、证据hash和下一动作。没有实际执行不得登记PASS。

## Attempt 1｜20260911T183426Z

- Gate: `contract_generate`
- Command: `make generate`
- Exit: `0`
- Evidence: `loops/GK12-l6-runtime-acceptance/evidence/contract_generate-20260911T183426Z.log`
- SHA256: `048ab7c55cfbb3c6707b7212288bd84d678861d4abb19a7eca16fbb7a71803b8`

## Attempt 1｜20260911T183427Z

- Gate: `contract_check`
- Command: `make check`
- Exit: `0`
- Evidence: `loops/GK12-l6-runtime-acceptance/evidence/contract_check-20260911T183427Z.log`
- SHA256: `55219a6f7d13f17671131ed905d5adc07be683517f11c42152995b964516677d`

## Attempt 1｜20260911T183428Z

- Gate: `security_check`
- Command: `make security-check`
- Exit: `0`
- Evidence: `loops/GK12-l6-runtime-acceptance/evidence/security_check-20260911T183428Z.log`
- SHA256: `fc9f8abee1a86eaf0f6e0700a9a018f202bf3db7193f60222f02c90ed3dbe4e8`

## Attempt 1｜20260911T183429Z

- Gate: `gk_ke_examples`
- Command: `python3 scripts/gk_ke_contract_examples.py`
- Exit: `0`
- Evidence: `loops/GK12-l6-runtime-acceptance/evidence/gk_ke_examples-20260911T183429Z.log`
- SHA256: `2b19441f59a6819bada8b85d409add1bcf6ecf7764298e3aefd9b84d29417c4f`

## Attempt 1｜20260911T183429Z

- Gate: `gk_ke_openapi_lint`
- Command: `python3 scripts/gk_ke_openapi_contract_tests.py`
- Exit: `0`
- Evidence: `loops/GK12-l6-runtime-acceptance/evidence/gk_ke_openapi_lint-20260911T183429Z.log`
- SHA256: `237156c1be19e35854dd88438c5d24cf462b9e342c967bbe1a8666ee9246bf1a`

## Attempt 1｜20260911T183429Z

- Gate: `l6_runtime_acceptance_tests`
- Command: `python3 scripts/gk_ke_l6_runtime_acceptance_tests.py`
- Exit: `0`
- Evidence: `loops/GK12-l6-runtime-acceptance/evidence/l6_runtime_acceptance_tests-20260911T183429Z.log`
- SHA256: `e23360eea419a94bde70a15e095ea4b7aaae9186ec70b0d93438977ccc06f69c`
