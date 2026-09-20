# PC0-product-center-baseline｜Next Session Baton

| 字段 | 值 |
|---|---|
| **Updated** | `2026-09-20T15:25:00+00:00` |
| **holder** | `tech_lead` |
| **packet** | `PC0-product-center-baseline` |
| **wave** | `W1`（T0-4..T0-11 合同设计） |
| **index_basis** | `memory/INDEX_BASIS.md`（TL/架构角色必填：`INDEX_FRESH` / `INDEX_STALE(n)` / `INDEX_ABSENT`） |
| **do_not_start** | QA_PASS、REAL_E2E_PASS、BUSINESS_SIGNED、P38 任何改动 |

## 已完成（W0 + T0-2/T0-3，证据见 EVIDENCE.md）

- OD-PI-06 分级提交（`00d17ca` e2e 修复 / `8d8c79b` vite 代理 / `784657f` 第一轮交付物 V1.2 含决策登记）
- 菜单「产品中心」（知识与治理组，domain=`product-center`）+ 路由 `/product-center/:productId?` + PC0 骨架页
- 测试基线：AppSidebar 12→13、ProductCenterView.spec（2）、experience-shell e2e 菜单清单
- 验证：vue-tsc 0 错误；vitest 344/344；playwright experience-shell 4/4

## 下一会话任务（T0-4..T0-11，按 `docs/dispatch/PI-ROUND1-需求准入与影响分析-V1.0.md` §10.1）

1. T0-4 契约设计：14 端点 OpenAPI（`specs/product-center/`）+ 18 类对象 schema（含 6+1 态枚举、SalesBoundary、ComparisonSet 禁字段清单）
2. T0-5 合同登记：`specs/CONTRACT_INDEX.yaml` 追加 `CTR-PK-CENTER-*`（独立 generated 目标）
3. T0-6 迁移设计：12 张 `pk_*` 表从 `specs/product-knowledge/migration-candidates/` 迁入 `adapters/persistence-relational/.../{h2,mysql}`
4. T0-7 DEMO/生产隔离方案；T0-8 错误码映射；T0-9 枚举映射落地（§11.5）+ 逐态变异测试
5. 门禁：`make generate` → `make check` → `make security-check`（串行执行；跑后 `git checkout -- evidence/gk-ke-chain-trace/trace.json` 还原噪声文件）

## 准入约束

- OD-PI-03 映射表在合同登记时提交 Owner 背书；背书前不得进入 PC2
- P38（route/view/api/测试）全程冻结；`git add` 只用显式路径
