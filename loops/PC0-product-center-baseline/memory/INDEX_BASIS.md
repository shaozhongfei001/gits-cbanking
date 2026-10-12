# INDEX_BASIS — PC0-product-center-baseline

## 开工声明（2026-09-20）

```
[索引] INDEX_FRESH @ merge 2026-09-15T17:50:17Z (gits 7116904 / kert 64f6f873)
[索引] 候选影响面: frontend/src/layouts/navConfig.ts, frontend/src/router/index.ts,
       frontend/src/views/ProductCenterView.vue(新), frontend/src/components/shell/__tests__/AppSidebar.spec.ts,
       frontend/e2e/experience-shell.spec.ts
[回源] 见下表
```

## 本批次回源结论（L4 回源，索引仅提供候选）

| # | 事实 | 回源 |
|---|---|---|
| 1 | 「知识与治理」组现有 2 项；「产品解读与知识」→ `/product-knowledge/interpretation`，domain=`evidence` | `frontend/src/layouts/navConfig.ts:51-55` |
| 2 | 侧栏高亮按 `domain` 等值匹配 ⇒ 新菜单复用 `evidence` 会双高亮，必须新增独立 domain | `frontend/src/components/shell/AppSidebar.vue:109,113` |
| 3 | 导航项数量断言 `toHaveLength(12)`（OD-PI-02 批准改 13） | `frontend/src/components/shell/__tests__/AppSidebar.spec.ts:62` |
| 4 | HEAD 上 e2e 断言为旧菜单名（必红），未提交改动是修复 | `git show HEAD:frontend/e2e/experience-shell.spec.ts:18,23` vs `navConfig.ts:35,53` |
| 5 | 既有解读 API 白名单 `^PROD-[A-Z]+-[0-9]{3}$` / view 3 态 / purpose 2 态 | `apps/api/.../productknowledge/ProductInterpretationController.java:33-38` |
| 6 | 版本对象无 status/knowledge_as_of/next_review_at（15 字段清单） | `modules/operational-ontology/.../domain/ProductKnowledgeVersion.java:10-25` |
| 7 | 12 张 `pk_*` 表仅在候选迁移目录，未落地 | `specs/product-knowledge/migration-candidates/h2/V023__product_knowledge_objects.sql` |
| 8 | 法人账户透支已登记：`PROD-CM-003` / family `CASH_MANAGEMENT` | `specs/product-knowledge/product-taxonomy.yaml:307` |
| 9 | 参考原型 8 section / 硬编码 5 族 / 4 个 DEMO 证据编号 / 无推荐性元素 | `reference/法人账户透支_产品解读页面_参考实现.html` data-srcdoc 解码实测 |
| 10 | 本仓无 Tailwind；设计令牌在 theme.css（无 `--product-*`、无 1700/246/310） | `frontend/src/assets/styles/theme.css:7-123`；`package.json:29-40` |

## 收工更新（2026-09-20）

- 上表 1–4 已通过本批次代码与测试落地验证（13 项菜单 / 独立 domain / e2e 4 passed）
- 索引基线 commit `7116904`；本批次新增 commit 见 EVIDENCE.md（E-01..E-03 及 PC0 代码提交）
- 索引新鲜度：开工 INDEX_FRESH；本批次改动均为前端追加，未触及 `specs/`、`modules/`、`adapters/`、`apps/` 结构 ⇒ 索引仍可代表设计全貌
