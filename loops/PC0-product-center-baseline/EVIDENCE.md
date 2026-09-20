# PC0-product-center-baseline｜Evidence index

机器可判定的唯一证据板为 `EVIDENCE.json`。本文件只提供人类导航，不复制状态。

- 命令日志：`evidence/`
- 失败记录：`FAILURES.md`
- 波次迭代：`memory/waves/`
- 独立QA：必须由非implementation actor写入 `EVIDENCE.json.independent_qa`

## W0 / T0-2 / T0-3 执行记录（2026-09-20，TL）

前置决策（Owner 2026-09-20 确认，登记于 `docs/dispatch/PI-ROUND1-需求准入与影响分析-V1.0.md` §11）：
OD-PI-01/02/04/05/06/08/09 已决；OD-PI-03 为 TL 受控假设（§11.5 映射表）。

| # | 动作 | 命令 | 结果 |
|---|---|---|---|
| E-01 | OD-PI-06 步骤1：e2e 红测修复入库 | `git commit`（显式路径 e2e×2） | `00d17ca` |
| E-02 | OD-PI-06 步骤2：vite 代理端口可配入库 | `git commit`（显式路径） | `8d8c79b` |
| E-03 | 第一轮交付物入库（含决策登记） | `git commit`（显式路径） | `784657f` |
| E-04 | Loop 创建 | `.venv/bin/python scripts/new_loop.py --loop-id PC0-product-center-baseline --holder tech_lead` | loops/PC0-product-center-baseline |
| E-05 | T0-2 菜单/路由/骨架最小追加 | 编辑 `navConfig.ts`（domain 类型 + item + 映射分支）、`router/index.ts`（`/product-center/:productId?`）、新增 `views/ProductCenterView.vue` | 见提交 |
| E-06 | T0-3 测试基线 | `AppSidebar.spec.ts` 12→13（OD-PI-02 已批）+「产品中心」断言；新增 `ProductCenterView.spec.ts`（2 用例）；`experience-shell.spec.ts` 菜单清单 +「产品中心」 | 见提交 |
| E-07 | 前端类型检查 | `npm run check`（vue-tsc --noEmit） | exit=0，0 错误 |
| E-08 | 前端单测 | `npx vitest run` | **64 文件 / 344 用例全 PASS**（含 ProductCenterView 2、AppSidebar 6、routes 13） |
| E-09 | 壳层 e2e | `npx playwright test e2e/experience-shell.spec.ts --output=/tmp/pw-pc0` | **4 passed**（13 项菜单含「产品中心」） |
| E-10 | 浏览器实测 | IDE preview 打开 `http://localhost:5173/product-center` | 骨架页渲染，菜单高亮唯一 |

红线自查（本 Loop 收工）：
- P38 相关文件零改动：`views/ProductInterpretationView.vue`、`api/productKnowledge.ts`、P38 两条路由 —— 均 diff 为空；
- 未使用 `git add .`，全部显式路径；
- 工作区其余约 179 项他人/他 Loop 未提交改动未触碰；
- 浏览器验证：菜单「产品中心」与「产品解读与知识」高亮互斥（不同 domain）。
