# W0｜PLAN（开工与基线）

## Goal

建立可收敛的基线：**在本 Loop 动手之前，把仓库的既有真实状态钉死**，
避免把既有红灯算成本 Loop 的失败，也避免把本 Loop 的改动误判为既有问题。

## 步骤

| # | 动作 | 命令 | 判据 |
|---|---|---|---|
| W0-1 | 环境与 Baton | `git status --porcelain` / `git rev-parse --short HEAD` | 工作区干净；holder=tech_lead |
| W0-2 | 合同生成基线 | `make generate` | exit 0 |
| W0-3 | 门禁基线 | `make check`；`python3 scripts/run_gates.py` | 记录 22/23、1 INCONCLUSIVE、`semantic-consumption` NOT_MET **作为既有状态** |
| W0-4 | 后端基线 | `make backend-test` 或 `./mvnw -pl apps/api -am test -DskipITs` | 记录 600/0/0/4 |
| W0-5 | 前端基线 | `make frontend-test` 或 `npx vue-tsc --noEmit` + `npx vitest --run` | 记录 0 错误 / 342 通过 |
| W0-6 | Loop 合规 | `make memory-check LOOP=GK17-ontology-unified-map`；`make evidence-check LOOP=...` | PASS |
| W0-7 | 基线落盘 | 写入 `evidence/W0-BASELINE.md` | 含每条命令的原始输出摘要 |

## 并行策略

**全部串行**（门禁互斥）。W0 期间不派并行写者。

## 非声明

- 本 Wave **不产生**任何功能改动；
- 基线中的既有红灯（`semantic-consumption` NOT_MET、`gate-injection-tests` INCONCLUSIVE）
  **不因本 Loop 而改变**，也不由本 Loop 负责收口。
