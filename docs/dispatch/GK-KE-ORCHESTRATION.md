# GK-KE L1–L14 长程无人值守编排计划（Tech Lead SSOT）

> 本文件是 GK-KE 交付波次的编排索引。权威顺序：已批准需求/基线 > ADR+合同注册表 > 本编排 + 各 Loop LOOP.yaml > 实现代码。
> 候选合同包：`/home/szf/dev/gits-kert-docs/dd/GK-KE-CONTRACT-V1.0/`（CR-01..CR-10，验收 T01..T50）。
> 基线：`c7017b1`。团队：`gk-ke-delivery`。

## 0. 已完成

| Loop | 合同 | 内容 | 状态 |
|---|---|---|---|
| GK0-contract-activation | CR-01 | gk-ke/v1 14 schema（CTR-GKKE-001..014）+ CanonicalHash + 正负例 | 5 gate pass，ready_for_independent_qa |

## 1. 波次与依赖（依据 L0-1 §6 切分）

| 波次 | Loop / worktree | 合同 | 验收 | 依赖 | 状态 |
|---|---|---|---|---|---|
| **W1 并行** | GK1-registry-map-core @ `/home/szf/dev/gk-wt-L1` (feature/GK-KE-L1) | CR-02 | T05,T06,T07,T20 | L0 | **in_progress**（gk1-pilot，b27b1de 脚手架） |
| **W1 并行** | GK6-simulation-factory @ `/home/szf/dev/gk-wt-L6` (feature/GK-KE-L6) | CR-07 | T30–T33 | L0 | **in_progress**（gk6-pilot，d12a6a8 脚手架） |
| W2 | GK2-router-resolver（建议名） | CR-02/03 | T08–T13,T17 | L1 | planned |
| W2 | GK7-llm-rewrite | CR-08 | T34–T37 | L6 | planned |
| W3 | GK3-activation-api | CR-04 | T14–T16,T18,T19 | L2 | planned |
| W3 | GK8-llm-eval | CR-08 | T38,T39 | L7 | planned |
| W4 | GK4-llm-claim | CR-05 | T21–T25 | L3 | planned |
| W4 | GK9-llm-claim-eval | CR-05/08 | T40–T42 | L4,L8 | planned |
| W5 | GK5-human-control | CR-06 | T26–T29 | L4 | planned |
| W6 | GK10-demo-e2e | CR-09/10 | T43–T50 | L5,L9 | planned |

> 注：L10–L14 目录名为旧 PI-ARCH 占位，与 GK-KE 无关；GK-KE 批次统一用 `GKx-` 前缀。
> 集成点：L1/L6 在独立 worktree 分支并行；W2 起需先把 feature/GK-KE-L1 合入集成分支再派生，避免 L2/L3 与 L6 长期分叉。合并顺序与冲突裁决由 Tech Lead 在 W1 收口时处理。

## 2. 合同决策原则

- W1（L1/L6）：`reuse_only`，不改 `specs/`、`generated/`。
- 后续 Loop 若需新增/变更合同（如服务级 OpenAPI、CR-05 Claim schema 细化），必须先改 `specs/` 权威源 → `make generate` → `make check` → 再实现，并在 CONTRACT_INDEX 登记；由 Tech Lead 审批，Feature Pilot 不得自行改合同。

## 3. 无人值守纪律

- 每个 Loop：PLAN → 逐 gate ITER（max 5）→ 全绿 → 独立 QA 记录 QA_PASS（dev 不得自签）。
- 失败先写该 Loop `FAILURES.md` 再修；硬阻塞写 `memory/BLOCKED.md` 并 STOP 上报。
- 禁止 `git add .`；禁止改 `generated/`；禁止启用隔离资产。
- 环境：Java 21、Maven 离线 `MAVEN_OPTS=-Ddependency.check.auto.update=false`、Node ≥22、系统 python3（3.10）。

## 4. W1 收口检查清单（Tech Lead）

- [ ] GK1 7 gate 全绿 + 独立 QA
- [ ] GK6 6 gate 全绿 + 独立 QA
- [ ] 两分支分别可独立 `make check`/`make backend-test`/`make tooling-test`
- [ ] 制定 L1→集成分支合并与 L2/L7 派生方案
