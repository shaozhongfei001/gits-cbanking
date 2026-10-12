# W0｜Iteration log（append-only）

由 `scripts/record_gate.py` 追加实际attempt、命令、退出码、证据hash和下一动作。没有实际执行不得登记PASS。

## Attempt 1｜20260911T182343Z

- Gate: `contract_generate`
- Command: `make generate`
- Exit: `0`
- Evidence: `loops/GK3-l1-2-simulation-source/evidence/contract_generate-20260911T182343Z.log`
- SHA256: `048ab7c55cfbb3c6707b7212288bd84d678861d4abb19a7eca16fbb7a71803b8`

## Attempt 1｜20260911T182344Z

- Gate: `contract_check`
- Command: `make check`
- Exit: `0`
- Evidence: `loops/GK3-l1-2-simulation-source/evidence/contract_check-20260911T182344Z.log`
- SHA256: `55219a6f7d13f17671131ed905d5adc07be683517f11c42152995b964516677d`

## Attempt 1｜20260911T182345Z

- Gate: `security_check`
- Command: `make security-check`
- Exit: `0`
- Evidence: `loops/GK3-l1-2-simulation-source/evidence/security_check-20260911T182345Z.log`
- SHA256: `fc9f8abee1a86eaf0f6e0700a9a018f202bf3db7193f60222f02c90ed3dbe4e8`

## Attempt 1｜20260911T182346Z

- Gate: `gk_ke_examples`
- Command: `python3 scripts/gk_ke_contract_examples.py`
- Exit: `0`
- Evidence: `loops/GK3-l1-2-simulation-source/evidence/gk_ke_examples-20260911T182346Z.log`
- SHA256: `2b19441f59a6819bada8b85d409add1bcf6ecf7764298e3aefd9b84d29417c4f`

## Attempt 1｜20260911T182346Z

- Gate: `l1_2_simulation_tests`
- Command: `python3 scripts/gk_ke_l1_2_simulation_tests.py`
- Exit: `0`
- Evidence: `loops/GK3-l1-2-simulation-source/evidence/l1_2_simulation_tests-20260911T182346Z.log`
- SHA256: `061e587b7212ff8c937a25d16cfbf934b5e3da22471b139b8e59ca6f5568e9ea`

## Attempt 1｜20260911T182349Z

- Gate: `gk_ke_g2_definitions`
- Command: `python3 scripts/gk_ke_g2_definitions_check.py`
- Exit: `0`
- Evidence: `loops/GK3-l1-2-simulation-source/evidence/gk_ke_g2_definitions-20260911T182349Z.log`
- SHA256: `6ee99d2184c6046d17fc71fea074ae454a38c12ea83bdb06af0fd692316f987f`
