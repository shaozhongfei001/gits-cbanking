# W0｜Iteration log（append-only）

由 `scripts/record_gate.py` 追加实际attempt、命令、退出码、证据hash和下一动作。没有实际执行不得登记PASS。

## Attempt 1｜20260911T182646Z

- Gate: `contract_generate`
- Command: `make generate`
- Exit: `0`
- Evidence: `loops/GK5-l2-1-semantic-query/evidence/contract_generate-20260911T182646Z.log`
- SHA256: `048ab7c55cfbb3c6707b7212288bd84d678861d4abb19a7eca16fbb7a71803b8`

## Attempt 1｜20260911T182646Z

- Gate: `contract_check`
- Command: `make check`
- Exit: `0`
- Evidence: `loops/GK5-l2-1-semantic-query/evidence/contract_check-20260911T182646Z.log`
- SHA256: `55219a6f7d13f17671131ed905d5adc07be683517f11c42152995b964516677d`

## Attempt 1｜20260911T182648Z

- Gate: `security_check`
- Command: `make security-check`
- Exit: `0`
- Evidence: `loops/GK5-l2-1-semantic-query/evidence/security_check-20260911T182648Z.log`
- SHA256: `fc9f8abee1a86eaf0f6e0700a9a018f202bf3db7193f60222f02c90ed3dbe4e8`

## Attempt 1｜20260911T182648Z

- Gate: `gk_ke_examples`
- Command: `python3 scripts/gk_ke_contract_examples.py`
- Exit: `0`
- Evidence: `loops/GK5-l2-1-semantic-query/evidence/gk_ke_examples-20260911T182648Z.log`
- SHA256: `2b19441f59a6819bada8b85d409add1bcf6ecf7764298e3aefd9b84d29417c4f`

## Attempt 1｜20260911T182649Z

- Gate: `gk_ke_openapi_lint`
- Command: `python3 scripts/gk_ke_openapi_contract_tests.py`
- Exit: `0`
- Evidence: `loops/GK5-l2-1-semantic-query/evidence/gk_ke_openapi_lint-20260911T182649Z.log`
- SHA256: `237156c1be19e35854dd88438c5d24cf462b9e342c967bbe1a8666ee9246bf1a`

## Attempt 1｜20260911T182649Z

- Gate: `l2_1_semantic_query_tests`
- Command: `python3 scripts/gk_ke_l2_1_semantic_query_tests.py`
- Exit: `0`
- Evidence: `loops/GK5-l2-1-semantic-query/evidence/l2_1_semantic_query_tests-20260911T182649Z.log`
- SHA256: `610becd48019e4183fad2709ef1d101c63c4ee1939b2c4b561e9de5fc456938b`

## Attempt 2｜20260911T182706Z

- Gate: `l2_1_semantic_query_tests`
- Command: `python3 scripts/gk_ke_l2_1_semantic_query_tests.py`
- Exit: `0`
- Evidence: `loops/GK5-l2-1-semantic-query/evidence/l2_1_semantic_query_tests-20260911T182706Z.log`
- SHA256: `e941d56a0b9f5d903fa701caa8088bee4e87e13958bb2ade4587812550624d77`
