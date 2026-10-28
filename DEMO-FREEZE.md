# DEMO-FREEZE — 演示环境冻结基线

> 冻结时间：2026-09-27
> 冻结目的：客户演示用稳定环境

## 1. 代码基线

| 仓库 | 分支 | Commit | 说明 |
|------|------|--------|------|
| gits-cbanking | `recover/PI-ARCH-product-catalog` | `bfd4e9b` | GITS 主仓库 |
| Leibniz-KERT | `feature/m7-3-knowledge-map-route` | (当前) | KERT 知识工程服务 |

## 2. 服务拓扑

| 服务 | 端口 | 健康端点 | 说明 |
|------|------|----------|------|
| GITS Frontend (Vite) | :15173 | `GET /` | Vue3 SPA |
| GITS API (Spring Boot) | :18080 | `GET /actuator/health` | 后端 API |
| KERT Skill Service | :8107 | `GET /v1/health` | 知识技能服务 |
| LightRAG (可选) | :9621 | `GET /health` | RAG 检索增强；装在 `/home/szf/dev/lightrag`（自带 `.venv` + `start.sh`），冷启动约 50s |

## 3. 启动命令

```bash
# 标准启动（不含 LightRAG）
scripts/demo-startup.sh up --no-lightrag

# 含 LightRAG
scripts/demo-startup.sh up

# 停止
scripts/demo-startup.sh down

# 状态检查
scripts/demo-startup.sh status

# 冒烟验证
scripts/demo-smoke.sh
```

## 4. 冒烟验证结果（18 场景）

| ID | 场景 | 端点 | 期望状态 |
|----|------|------|----------|
| S1 | 经营旅程列表 | `GET /api/v1/engagement/journey` | PASS |
| S2 | 旅程详情 | `GET /api/v1/engagement/journey/{id}` | PASS |
| S3 | 客户查询 | `GET /api/v1/engagement/customer?rmId=RM-001` | PASS |
| S4 | 产品中心 | `GET /api/v1/product-center/products` | PASS |
| S5 | 产品知识卡 | `GET /api/v1/product-knowledge/cards/PROD-CM-003` | PASS |
| S6 | 门禁列表 | `GET /api/v1/human-gates?status=PENDING` | PASS |
| S7 | CRM回写命令 | `GET /api/v1/crm/writeback-commands` | PASS |
| S8 | KERT Analytics | `GET /v1/analytics/screens` | PASS |
| S9 | KERT 经营指标 | `GET /v1/analytics/metrics?screen=operating-customer&dim=INDUSTRY&orgId=350200&period=201012` | PASS |
| S10 | KERT 知识地图 | `GET /v1/knowledge-maps` | PASS |
| S11 | 前端页面 | `GET http://host:15173/` | PASS |
| S12 | 建议书生成 | `POST /api/v14/proposals` | WARN (LLM不可用时503) |
| S13 | 访前准备 | `POST /api/v1/engagement/journey/{id}/prepare-previsit` | WARN (异步60s+) |
| S14 | KYC洞察 | `GET /api/v1/engagement/kyc/{id}/insights` | WARN (端点未实现) |
| S15 | 前端→API代理 | `GET http://host:15173/api/v1/engagement/journey` | PASS |
| S16 | 前端→KERT代理 | `GET http://host:15173/kert-api/v1/health` | PASS |
| S17 | KERT 趋势 | `GET /v1/analytics/trend?...` | PASS |
| S18 | KERT 可用期间 | `GET /v1/analytics/periods` | PASS |

## 5. 已知限制

| 限制 | 影响 | 缓解措施 |
|------|------|----------|
| LLM 端点需 API Key | 建议书生成/访前准备可能 503 | `.lr-kert.local.env` 配置 Key；KERT 回退确定性适配器 |
| 访前准备耗时长 | 60s+ 异步轮询 | 演示时提前触发，或用已有数据 |
| KYC insights 端点未实现 | 返回 404 | 前端不调用此端点，无影响 |
| 5 个 OpenAPI 端点无映射 | customer-journeys/knowledge-rules/operating-cases/products/versions/kyc-insights | 前端不调用，无影响 |
| KERT Analytics orgId 格式 | 必须用数字编码(如350200) | 启动脚本已内置正确参数 |
| KERT Analytics period 格式 | 必须用 YYYYMM(如201012) | 启动脚本已内置正确参数 |
| LightRAG 依赖本机 Ollama | 缺 Ollama 或 `all-minilm:l6-v2` 时 embedding 失败 | 先 `ollama serve`；模型清单见 `ollama list` |
| LightRAG 为派生检索层 | 其字段值不得作业务字段来源（ADR-017） | 检索结果只作辅证，业务值仍取 KERT/GITS 权威源 |

## 6. 种子数据

| 数据类型 | 数量 | 关键 ID |
|----------|------|---------|
| 经营旅程 | 4 条 | `a1b2c3d4-e5f6-7890-abcd-000000000001~4` |
| 客户 | 4 家 | `CUST-CORP-0001~4` |
| 产品 | 13 种 | `PROD-CM-001~013` 等 |
| Claims | 3 条 | `c1a1b2c3-d4e5-f678-90ab-cd0000000001~3` |
| 门禁 | 若干 | PENDING 状态 |
| DuckDB 分析数据 | 2010-2011 | orgId=350200~350500 |

## 7. 环境变量

```bash
# 必需
JAVA_HOME     → Java 21
NODE_VERSION  → ≥22
KERT_PYTHON   → .venv/bin/python (3.12+)

# 可选（影响 LLM 功能）
LR_KERT_LLM_API_KEY     → KERT LLM API Key
KERT_LIGHTRAG_API_KEY   → KERT→LightRAG API Key
LR_LLM_API_KEY          → LightRAG LLM API Key
```

## 8. 演示前检查清单

- [ ] `scripts/demo-startup.sh check` 通过
- [ ] `scripts/demo-startup.sh up --no-lightrag` 全栈启动
- [ ] `scripts/demo-smoke.sh` 15+ PASS
- [ ] 浏览器访问 `http://127.0.0.1:15173` 页面正常
- [ ] 如需 LLM 功能，确认 `.lr-kert.local.env` 中 API Key 有效
