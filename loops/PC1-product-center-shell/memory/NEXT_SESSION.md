# PC1-product-center-shell｜Next Session Baton

| 字段 | 值 |
|---|---|
| **Updated** | `2026-09-22T05:05:00+00:00` |
| **holder** | `tech_lead` |
| **packet** | `PC1-product-center-shell` |
| **wave** | `PC1 收工 → PC2 待启` |
| **index_basis** | 本轮新增文件为主 + 复用既有 `ProductCardCatalogService`（回源 `文件:行` 已记 EVIDENCE） |
| **do_not_start** | QA_PASS、P38 任何改动、`specs/semantic/*`、`generated/` 手改、未获授权的 KERT 仓 push/merge |

## 已完成（PC1：环境条 + 三栏 + 13 产品目录 + 首屏 + 八章导航）

- 后端：新包 `com.gien.gits.api.productcenter`，3 个只读端点 + 受控失败矩阵；**未改 P38 任何文件**
- 契约：`SOURCES_UNAVAILABLE` 先登记后实现；`make generate`/`make check` PASS；消费者测试 6/6 变异 PASS
- 前端：`api/productCenter.ts` + 6 个组件 + 三栏视图；vue-tsc 0 错；vitest **357/357**；e2e **2/2**（真实后端）
- 证据：`evidence/`（三门禁日志）+ `evidence/pc1-screenshots/`（1680/1440/1280）

## 下一会话任务（PC2，按需求 §十一 Loop 2）

1. **KERT Release 接入**：把详情里的「产品卡镜像 DRAFT」换成已发布受控版本（`publishedVersionId` + `evidenceSnapshotId` + `knowledgeAsOf`），否则 13 产品永远显示「无有效版本」
2. **核心解读四章**：60 秒读懂（补 `solves/isNot/nearestDifference`）、核心条款（8 条款 + 7 态确定性 + 逐条证据）、适用边界（典型/不适用/禁止 + 三类前提）、办理流程（6 步 + 例外 + 人工责任点）
3. **搜索端点** PI-FR-005/006（产品名/别名/条款/材料/流程/制度题名 + 权限过滤 + 定位到章节）
4. **权限过滤** PI-FR-014（当前目录为全量；需身份服务）
5. 浏览位置恢复持久化（PI-FR-029 后半）+ <1180px 受控抽屉

## 准入约束（本轮已遵守，PC2 继续）

- 只用显式路径 `git add`；不碰 GK17/ONTO1 在飞未跟踪文件；`make generate/check` 跑后还原 `evidence/gk-ke-chain-trace/trace.json`
- 组件**不得**硬编码业务文案/条款/证据/完整度（需求 02 §八）；缺口显示「待核验」而非空白
- 否定式断言必须做变异复验（本轮合同测试已做，6/6）
- 运行态：后端 8088（`--gits.product-knowledge.card-dir=<KERT 03_core>`）、前端 5173（`VITE_API_PROXY_TARGET=http://127.0.0.1:8088`）
