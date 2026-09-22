# PC1-product-center-shell｜Evidence index

机器可判定的唯一证据板为 `EVIDENCE.json`。本文件只提供人类导航 + 本轮执行记录。

- 命令日志：`evidence/`
- 三档宽度截图：`evidence/pc1-product-center/`（仓库根 evidence 目录；**不得**放在本 Loop 内 —— `loop_guard` 会对 Loop 目录做 UTF-8 全量读取，二进制会使其 FAIL）
- 失败记录：`FAILURES.md`

---

## 0. 交付范围（Loop PC1：页面骨架与目录）

按 `docs/dispatch/PI-ROUND1-需求准入与影响分析-V1.0.md` §7 分 Loop 计划，PC1 = 环境条 + 三栏布局 + 产品目录 + 产品首屏 + 章节导航 + 1680/1440/1280 基线。

**数据来源**：`CTR-PKC-API-001`（PC0 已登记的两个合同），PC1 首次实现其中 3 个只读端点。

## 1. 后端（新包，未改 P38 任何文件）

| 文件 | 作用 |
|---|---|
| `apps/api/.../productcenter/ProductCenterCatalogService.java` | 分类骨架（`CTR-PK-TAX-001`）只读解析 + 产品卡目录（复用 `ProductCardCatalogService`）联接 |
| `ProductCenterController.java` | `GET /api/v1/product-center/{families,products,products/{productId}}` + 受控失败矩阵 |
| `ProductCenterFamily/ProductCenterProductEntry/ProductCenterVersionSummary/ProductCenterSummary/ProductCenterDetail/ProductCenterErrorResponse.java` | 合同类型（逐项对齐 `Pkc*`） |
| `ProductNotFoundException / NoPublishedVersionException / ProductCenterSourceUnavailableException.java` | 受控失败：`PRODUCT_NOT_FOUND` / `NO_PUBLISHED_VERSION` / `SOURCES_UNAVAILABLE` |
| `application.yaml` | 新增 `gits.product-center.{taxonomy-path,environment,is-demo,enabled}` |

**契约先行**：`SOURCES_UNAVAILABLE` 先加进 `specs/product-center/product-center-api.openapi.json`（`PkcError.code`）与消费者测试白名单，再实现。

| # | 命令 | 结果 |
|---|---|---|
| E-01 | `make generate` | **PASS** |
| E-02 | `make check` | **PASS**（INCONCLUSIVE=`gate-injection-tests` 既有基线项，**不计为通过**）；门禁噪声 `evidence/gk-ke-chain-trace/trace.json` 已还原 |
| E-03 | `python3 scripts/pkc_contract_tests.py` / `--self-test` | **PASS / PASS**（6/6 变异被捕获） |
| E-04 | `./mvnw -o -pl apps/api -Dtest=ProductCenterCatalogServiceTest test` | **Tests run: 10, Failures: 0** |
| E-05 | `curl /api/v1/product-center/families` | **6 族**（现金管理/结算/贸易金融/跨境金融/融资/投资银行），计数与 taxonomy `existing_card_count` 一致 |
| E-06 | `curl /api/v1/product-center/products` | **13 产品**（受控分类法全集，非演示子集） |
| E-07 | `curl ".../products?keyword=透支"` | 命中 1 条（法人账户透支） |
| E-08 | `curl /products/PROD-CM-003` | 返回真实产品卡摘要（一句话定义/能力标签）+ `version.status=DRAFT` + `knowledgeAsOf=null` + 章节集合为空 |
| E-09 | 受控失败矩阵 | `PROD-XX-999`→404 `PRODUCT_NOT_FOUND`；`CM-003`→400 `BAD_REQUEST` |
| E-10 | `./mvnw -q -o -DskipTests package` | exit=0（jar 67879062 bytes） |

## 2. 前端

| 文件 | 作用 |
|---|---|
| `src/api/productCenter.ts` | 三端点客户端（类型逐项对齐合同 + `extractErrorCode`） |
| `src/components/product-center/ProductEnvironmentBanner.vue` | 环境条：DEMO 标识 + 基准日（缺失=「基准日待维护」）+ 筛选 + 身份缺口说明 |
| `.../ProductCatalog.vue` | 左栏：族展开/收起、选中态、无有效版本标记、待维护计数 |
| `.../ProductHero.vue` | 首屏：名称/编号/族/发布状态/标签/四个字段（缺失=待核验）+ 3 个受控操作（禁用并标注 PC5）+ 固定边界语句 |
| `.../ProductSectionNav.vue` | 章节导航：吸顶 + 滚动同步（IntersectionObserver）+ hash 深链接 + 键盘可达 |
| `.../ProductChapterStack.vue` | 八章：OVERVIEW 按契约渲染，其余 7 章显示**具名未接入状态**（契约对象 + 计划批次） |
| `.../ProductGovernancePanel.vue` | 右栏：版本/基准日/生效日/复审日/审核记录 + 治理与证据（PC4 待接入）+ 助手禁用说明 + 页面边界 |
| `.../sections.ts` | 八章键/顺序唯一登记处（`PkcSectionKey`） |
| `src/views/ProductCenterView.vue` | 三栏壳 + 受控状态机（加载/错误/无有效版本/未选择） |

| # | 命令 | 结果 |
|---|---|---|
| E-11 | `npm run check`（vue-tsc） | **0 错误** |
| E-12 | `npx vitest run` | **65 文件 / 357 用例全 PASS**（含新增 PC1 用例 5 项） |
| E-13 | `npx playwright test e2e/product-center-pc1.spec.ts`（真实后端 8088） | **2 passed** |
| E-14 | 三档截图 | `evidence/pc1-product-center/product-center-{1680,1440,1280}.png`（fullPage；仓库根 evidence 目录） |

## 3. 本轮发现并修复的缺陷（先记账后修）

| # | 缺陷 | 性质 | 处置 |
|---|---|---|---|
| F-1 | `NO_PUBLISHED_VERSION` 落入通用错误分支 ⇒ 「暂无有效版本」受控状态**永不渲染** | **真实 UI 缺陷**（AT-009 会被破坏），由单测捕获 | 在 `detailErrorMessage` 中显式排除该码，交由专用分支渲染；单测转绿 |
| F-2 | 后端测试夹具能力词含「透支」⇒ 关键词断言被夹具污染（expected 1, got 2） | 夹具缺陷（非产品缺陷） | 夹具改为不含被断言词；10/10 转绿 |
| F-3 | 测试选择器 `[data-section-key=OVERVIEW]` 同时命中导航链接与章节 | 测试缺陷 | 选择器限定 `[data-testid="pc-chapter"]` |
| F-4 | 视图初稿含两个 `<script setup>` 块（语法错误） | 自伤，提交前自查修正 | 重写为单一 script 块 |

## 4. 诚实声明（未实现 / 未验证项，不得当作已完成）

| 项 | 状态 |
|---|---|
| 已发布受控知识版本 | **不存在**（13 产品 `hasPublishedVersion=false`）⇒ 详情版本为**产品卡镜像 `DRAFT`**，页面显示「未发布受控版本」；KERT Release 接入属 PC2 |
| 八章内容（条款/边界/流程/材料/价格/协议/比较/FAQ） | **未接入**（7/8 章显示具名未接入状态，无示意数据） |
| 全局搜索范围 | PC1 仅支持**产品名/编号/能力词**筛选；条款、材料、流程、制度题名搜索（PI-FR-005/006）属 PC2 |
| 权限与审计 | **未接入**（无 RBAC、无审计事件）；目录过滤当前为全量，`PI-FR-014` 权限过滤待 PC2 身份服务 |
| 身份/岗位展示 | **未接入**（界面显式标注「身份服务未接入（PC2）」） |
| 收藏 / 下载 / 提纲 / 助手 | **未实现**（按钮禁用并标注 PC5；助手 `enabled=false`） |
| 完整度与缺口、证据列表、责任人 | **未接入**（右栏具名标注 PC4） |
| 浏览位置恢复持久化 | **未实现**（PI-FR-029 的持久化部分属 PC2；hash 深链接已可用） |
| <1180px 抽屉交互 | 当前为**全宽侧板**（字段不消失）；受控抽屉交互属 PC2 |
| 独立 QA | **未申请**（开发角色禁止自签） |

## 5. 复现命令

```bash
# 后端
./mvnw -o -pl apps/api -Dtest=ProductCenterCatalogServiceTest test
./mvnw -q -o -DskipTests package
java -jar apps/api/target/gits-kno-api-0.1.0-SNAPSHOT.jar --server.port=8088 \
  --gits.product-knowledge.card-dir=/home/szf/dev/Leibniz-KERT/examples/product-recommendation-assets/03_core

# 前端
cd frontend && VITE_API_PROXY_TARGET=http://127.0.0.1:8088 npm run dev -- --host 127.0.0.1 --port 5173
npx vitest run
npx playwright test e2e/product-center-pc1.spec.ts --output=/tmp/pw-pc1

# 合同
python3 scripts/pkc_contract_tests.py --self-test
make generate && make check
```
