# Owner Decision｜P24-dkws-supplychain 不合入 main（存档保留）

| 字段 | 值 |
|---|---|
| Decision ID | OD-P24-NO-MERGE-2026-10-28 |
| Date | 2026-10-28 |
| Role | HUMAN_OWNER（会话确认：选方案 A 存档，不合入） |
| Recorded by | Tech Lead |
| Branch | `feature/P24-dkws-supplychain` @ `c0e19da742c435bf53633ddbeb8c1f2edfd92786` |
| main 归集末提交 | `2feb6f55b7d446ffc3c9b49ec00c38dfcbc6f84d` |
| Production ready | NO |
| Frozen | NO |
| UAT pass | NO |

## 决定

1. **P24 不合入 `main`。** 分支作为历史存档保留，已在 GitHub 可访问（`feature/P24-dkws-supplychain`）。
2. **分支内容零改动。** 不 rebase、不清理历史、不删除误入库的 `frontend/dist`。
3. **本轮 `main` 归集范围到此为止**：`GK-KE-L6` → `GK-KE-L1` → `GK-KE-L0-contract` 三个分支已合入并推送；`P24` 是唯一未合入项，且为**有意**保留。

## 事实依据

分支规模与分叉（`main...origin/feature/P24-dkws-supplychain`）：

| 项 | 值 |
|---|---|
| 独有提交 | 27（2026-08-21 ~ 2026-08-25） |
| 改动量 | 522 files changed, 80938 insertions(+), 4884 deletions(-) |
| 冲突文件 | **74** |
| 冲突类型 | 34 add/add ｜ 35 content ｜ 5 modify/delete |

冲突目录分布：

| 目录 | 冲突数 |
|---|---|
| `apps`（后端） | 45 |
| `frontend/src`（源码） | 17 |
| `adapters` | 3 |
| `generated` | 2 |
| `diagrams` | 2 |
| `specs`（合同） | 1 |
| `frontend/dist`（构建产物） | 1 |
| `frontend/package-lock.json` | 1 |
| `.gitignore` / `.github` | 1 / 1 |

> 注：早前口头汇报的"225 冲突"为统计口径错误，把 `git merge-tree` 的说明行一并计入；**正确值为 74**，以本文为准。

## 判定理由

1. **34 个 `add/add` 是决定性信号**：同一批能力在 `main` 与 `P24` 上被**各自独立实现**（如 `apps/api/.../adapter/skill/` 下的 Dsh 系列适配器、`SupplyChainGraphService` 等）。这不是"选哪一侧"的技术问题，而是"重复实现保留哪一份"的**产品裁决**，需 Owner 明确方向后才能动。
2. **时间序劣势**：P24（2026-08）早于 `main` 上的 V8.1 前端重构与 recover 分支收口，17 个前端冲突多指向已被 V8.1 替代的组件，机械合并会引入回退。
3. **`specs` 合同冲突 1 个**：按 API First，合同是 SSOT，须先定合同再谈实现，不能放在批量合并里顺带解决。
4. **成本与收益不匹配**：74 个冲突逐个人工裁决 + 每批验证（`make check` / 后端测试 / 前端 `check`），而该方向是否仍是当前产品目标尚未确认。

## 已执行动作

- `git push github origin/feature/P24-dkws-supplychain:refs/heads/feature/P24-dkws-supplychain` → 分支已上 GitHub，与迁移 bundle 内容一致（同为 `c0e19da`）。
- 本轮 `main` 归集（均已推送）：
  - `2899b28` merge `GK-KE-L6`（0 冲突，纯新增 `tools/gk-ke-simulation` + Loop 证据）
  - `26c1a1a` merge `GK-KE-L1`（1 冲突：`modules/knowledge-architecture/pom.xml` 取依赖并集，模块测试 100 passed / 0 failed）
  - `992b0af` merge `GK-KE-L0-contract`（3 冲突：NVD 文档取分支版、两个 e2e spec 取 main 版并补 `installApiMocks`）
  - `2feb6f5` fix：`navConfig.ts` 补齐 `monitors` 领域键（main 既有红灯，`vue-tsc` TS2322）

## 明确未批准 / 未做

- 不合入 `main`；不在 `main` 上恢复 P24 的供应链图谱 / 服务方案能力。
- 不改写 P24 分支历史（故 `frontend/dist` 产物保留在历史中）。
- `UAT_PASS` / `FROZEN` / `PRODUCTION_READY` 均未签署。

## 恢复条件与路径

若"供应链图谱 / DKWS 服务方案"重新成为产品目标，按下面两条路径之一重启，**不要**直接整体 merge：

- **方案 B（整体合入，分三批）**：① 基建/治理（`.gitignore`、`.github`、`diagrams`、`docs`、`loops`）→ ② 先定 `specs` 合同冲突，再处理 `apps`/`adapters`（34 个 add/add 逐个按"取 main / 取 P24 / 真合并"三选一）→ ③ 前端 17 个。每批独立验证。
  - 前置动作：先在 P24 分支上 `git rm -r --cached frontend/dist`。
- **方案 C（折中移植）**：仅抽取 `main` 确实缺失的能力，以新分支手工 cherry-pick，不做整体合并。

## 复现命令

```bash
git merge-tree --write-tree --name-only main origin/feature/P24-dkws-supplychain | tail -n +2 \
  | grep -v '^$' | grep -v 'Auto-merging\|CONFLICT'      # 74 个冲突文件
git rev-list --left-right --count main...origin/feature/P24-dkws-supplychain   # 315 / 27
```

## 关联遗留项（不在本决策范围，另行裁决）

1. `main` 上存在 **5 个失败单测**（`navConfig.spec.ts` ×1、`naiveTheme.spec.ts` ×2、`MeetingCaptureView.spec.ts` ×2，450 passed / 5 failed），均为 `18c34b6` 之后既有红灯，**非**本轮合并引入。Owner 决定**暂不处理**，待人工测试后再定。
2. 其中 `navConfig` 一条与 `2feb6f5` 同源：「分析」组单测期望 3 项、实际 4 项（多出"指标监视器"）。**是否移除指标监视器菜单**待人工测试后裁决——若保留则改单测期望为 4 项，若移除则同步回退 `navConfig.ts:6` 的 `monitors` 键与 `:77` 导航项、`:108` 路由判定。
