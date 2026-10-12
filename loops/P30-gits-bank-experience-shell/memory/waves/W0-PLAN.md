# W0｜Plan

## Goal

Feature Pilot 按 LOOP.yaml 门禁实现 Experience Shell 与 P01–P03 只读切片；Tech Lead 本波只做规划与派工。

## Gates

以 `LOOP.yaml.gates` 为唯一命令源；禁止复制后漂移。

## Constraints

- `AUTHORITY_SOURCE_CHANGE=NO`
- P03 分层写回禁用
- 测试 ID 执行前保持 PLANNED，执行后写证据，不得口头 PASS
