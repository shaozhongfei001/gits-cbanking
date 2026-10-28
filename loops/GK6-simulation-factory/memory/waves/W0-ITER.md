# W0｜Iteration log（append-only）

由 `scripts/record_gate.py` 追加实际attempt、命令、退出码、证据hash和下一动作。没有实际执行不得登记PASS。

## Attempt 1｜20260910T150410Z

- Gate: `contract_check`
- Command: `make generate && make check`
- Exit: `0`
- Evidence: `loops/GK6-simulation-factory/evidence/contract_check-20260910T150410Z.log`
- SHA256: `6db14820bf55424b6cc77039050eeb3f4273e4c599f4499aee8592261eeb1752`

## Attempt 1｜20260910T150940Z

- Gate: `vendor_factory`
- Command: `python3 tools/gk-ke-simulation/build_simulation.py`
- Exit: `0`
- Evidence: `loops/GK6-simulation-factory/evidence/vendor_factory-20260910T150940Z.log`
- SHA256: `622aa8934377baa87b1b7242b4073a5bb020099b2166e6e68a63205255c3eef6`

## Attempt 1｜20260910T150944Z

- Gate: `validate_dataset`
- Command: `python3 tools/gk-ke-simulation/validate_package.py`
- Exit: `0`
- Evidence: `loops/GK6-simulation-factory/evidence/validate_dataset-20260910T150944Z.log`
- SHA256: `52c0306c64dd87ab91400d79006e6371ba4bfe16743389a4fb9c196df9bf5b2d`

## Attempt 1｜20260910T150958Z

- Gate: `isolation_oracle`
- Command: `python3 -m unittest tests.tooling.test_gk_ke_simulation -v`
- Exit: `1`
- Evidence: `loops/GK6-simulation-factory/evidence/isolation_oracle-20260910T150958Z.log`
- SHA256: `28947578ec67fd511178eabdb78e78e50f2798894d2400d45b33d36241aa7a24`

## Attempt 2｜20260910T152259Z

- Gate: `isolation_oracle`
- Command: `python3 -m unittest tests.tooling.test_gk_ke_simulation -v`
- Exit: `0`
- Evidence: `loops/GK6-simulation-factory/evidence/isolation_oracle-20260910T152259Z.log`
- SHA256: `853e144b373665f632c1dfb7f8c0e58574148744d56d9f55329f3bb704c80aeb`

## Attempt 1｜20260910T152312Z

- Gate: `tooling_test`
- Command: `make tooling-test`
- Exit: `0`
- Evidence: `loops/GK6-simulation-factory/evidence/tooling_test-20260910T152312Z.log`
- SHA256: `bcf804f5cab7f4133cced5575d7aca658b13cd0b10c04e4d1305cccd55e12172`

## Attempt 1｜20260910T152320Z

- Gate: `security_check`
- Command: `make security-check`
- Exit: `0`
- Evidence: `loops/GK6-simulation-factory/evidence/security_check-20260910T152320Z.log`
- SHA256: `12ba5a504732177551e4f86fcc195b70dd7b320e449a2f421a46ec2dec215610`
