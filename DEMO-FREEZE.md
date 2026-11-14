# DEMO-FREEZE — 演示环境冻结基线

> 冻结时间：2026-09-27
> 冻结目的：客户演示用稳定环境

## 1. 代码基线

| 仓库 | 分支 | Commit | 说明 |
|------|------|--------|------|
| gits-cbanking | `main` = `github/main` | 以 `git log -1` 为准 | GITS 主仓库；演示就绪批次已入库 |
| Leibniz-KERT | `main` = `github/main` | 以 `git log -1` 为准 | KERT 知识工程服务；演示就绪批次已入库 |

> 两仓均直连 `github/main`，无 PR 流程；演示前用 `git status -sb` 确认无 ahead/behind 且工作区干净。

## 2. 服务拓扑

| 服务 | 端口 | 健康端点 | 说明 |
|------|------|----------|------|
| GITS Frontend (Vite) | :15173 | `GET /` | Vue3 SPA |
| GITS API (Spring Boot) | :18080 | `GET /actuator/health` | 后端 API |
| KERT Skill Service | :8107 | `GET /v1/health` | 知识技能服务 |
| LightRAG (可选) | :9621 | `GET /health` | RAG 检索增强；装在 `/home/szf/dev/lightrag`（自带 `.venv` + `start.sh`），冷启动约 50s |

## 3. 启动命令（唯一入口）

```bash
cd /home/szf/dev/gits-cbanking

bash scripts/demo-startup.sh check        # 预检，不启动
bash scripts/demo-startup.sh up           # 一条命令起：全栈含 LightRAG
bash scripts/demo-startup.sh down         # 一条命令停：全栈含 LightRAG
bash scripts/demo-startup.sh status       # 端口/HTTP/PID 表格 + READY / NOT READY
bash scripts/demo-startup.sh status --quick   # 只看端口/PID（不跑冒烟，输出 NOT READY）
bash scripts/demo-startup.sh smoke        # 16 端点全栈验证
bash scripts/demo-smoke.sh               # 18 场景冒烟
bash scripts/demo-smoke.sh --json        # 同上，JSON 输出

# 变体
bash scripts/demo-startup.sh up --no-lightrag           # 不启不停 LightRAG
bash scripts/demo-startup.sh down --no-lightrag         # 停全栈但保留 :9621
bash scripts/demo-startup.sh restart                   # 等价于 up：先 stop_stack 再完整启动
```

**「是否可演示」自检命令**：`bash scripts/demo-startup.sh status`，最后一行输出 `READY` 或 `NOT READY`。
判定口径：4 个端口（15173 / 18080 / 8107 / 9621）HTTP 全为 200，**且** 18 场景冒烟 0 FAIL
（`demo-smoke.sh` 的退出码即 FAIL 数；S14 的 WARN 不计 FAIL）。当前基线：`17 PASS / 0 FAIL / 1 WARN` ⇒ `READY`。

**restart 语义（已确认）**：`up` 与 `restart` 走 `case` 的同一分支，`restart` 一定先执行
`stop_stack` 再完整启动，**不会**在 15173 上直接重启服务；因此不会残留僵尸进程占用端口。

**日志与 PID（固定路径，不再按时间戳新建目录）**：

| 项 | 路径 | 说明 |
|----|------|------|
| 日志目录 | `logs/demo/` | 固定；每次 `up` 覆盖同名文件；已加入 `.gitignore` |
| 服务日志 | `logs/demo/{lightrag,kert,gits-api,gits-fe}.log` | 按服务分文件 |
| 冒烟日志 | `logs/demo/smoke-last.log` | 每次 `status` 的判定依据 |
| PID 文件 | `logs/demo/pids/{lightrag,kert,gits-api,gits-fe}.pid` | 启动时按监听端口登记真实服务 PID |

停止时只按 PID 文件读取 PID，终止该 PID 所在的进程组（`setsid` 组，可一并带走 vite/esbuild 子进程）；
PID 文件缺失或过期时按监听端口精确反查 PID。**不再使用 `pkill -f` 模式匹配**，避免误杀同名进程。

**前提**：`~/.bashrc` 中需有 `DASHSCOPE_API_KEY`（LightRAG 启动依赖，缺失 `start.sh` 会拒绝启动）；
GITS 侧密钥从 `.lr-kert.local.env` 自动加载（已 gitignore）。

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
| S12 | 建议书生成 | `POST /api/v14/proposals` | PASS（真实 LLM 逐章约 30.2s；同 requestId 命中 KERT 幂等约 3s） |
| S13 | 访前准备 | `POST /api/v1/engagement/journey/{id}/prepare-previsit` | PASS（异步 60s+，演示前提前触发） |
| S14 | KYC洞察 | `GET /api/v1/engagement/kyc/{id}/insights` | **WARN / 404**（端点未实现，前端须降级） |
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
| LightRAG 模型依赖阿里百炼 | 未设 `DASHSCOPE_API_KEY` 时 `start.sh` 拒绝启动，检索层不可用（KERT 降级） | 密钥取 `~/.bashrc` 的 `DASHSCOPE_API_KEY`（不落盘），LLM/Embedding 均走 `dashscope` 兼容端点 |
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

- [ ] `bash scripts/demo-startup.sh check` 通过
- [ ] `bash scripts/demo-startup.sh up` 全栈启动（`up` 自带 `stop_stack`，无需先手工 down）
- [ ] `bash scripts/demo-startup.sh status` 末行输出 `READY`（4 端口 200 + 冒烟 0 FAIL）
- [ ] `bash scripts/demo-smoke.sh` 17 PASS / 0 FAIL / 1 WARN（WARN 仅 S14）
- [ ] 浏览器访问 `http://127.0.0.1:15173`，主要页面有真实数据、无「待接入」空壳
- [ ] 如需 LLM 功能，确认 `.lr-kert.local.env` 与 `DASHSCOPE_API_KEY` 有效
- [ ] 两仓 `git status -sb` 均为 `## main...github/main`，无 ahead/behind、工作区干净
- [ ] 演示结束 `bash scripts/demo-startup.sh down`；下次 `up` 即可复现，无需清理 /tmp 日志

## 9. E2E 浏览器验证与截图证据

```bash
cd /home/szf/dev/gits-cbanking/frontend
QA_EVIDENCE_DIR=test-results/demo-20261114 npx playwright test e2e/uat
QA_EVIDENCE_DIR=test-results/demo-20261114 npx playwright test e2e/qa-e2e-acceptance.spec.ts
QA_EVIDENCE_DIR=test-results/demo-20261114 npx playwright test        # 全量
```

- `playwright.config.ts` 的 `baseURL` / `webServer` 统一到演示端口 **15173**，并注入
  `VITE_API_PROXY_TARGET=18080`、`VITE_KERT_PROXY_TARGET=8107`；`reuseExistingServer` 复用演示栈，
  避免「测的和演的」不一致。全局仍是 `screenshot: 'only-on-failure'`。
- 每场景截图由 `e2e/uat/_harness.ts` 的 `inspectRoute` 显式产出 `fullPage` PNG，
  与 `qa-e2e-acceptance.spec.ts` 共用 `QA_EVIDENCE_DIR` 约定，不另造第二套目录。

| 证据 | 路径 | 数量 |
|------|------|------|
| 演示路由逐场景截图 | `frontend/test-results/demo-20261114/routes/<routeId>.png` | 58 |
| 逐场景元数据清单（real / synthetic 标注、API 调用、可见文本） | `frontend/test-results/demo-20261114/routes/<routeId>.json` | 58 |
| 主验收 A/B/D/E/G 组截图与报告 | `frontend/test-results/demo-20261114/*.png`、`e2e-results.json` | 19 |
| 产品中心多宽度截图 | `frontend/test-results/pc1/*.png` | 3 |
| 截图路径总清单（含 real / synthetic 标注） | `frontend/test-results/demo-20261114/MANIFEST.md` | 80 张 PNG |
| HTML / JSON 报告 | `frontend/playwright-report/` | — |

以上目录均被 `.gitignore` 忽略，**不提交 PNG / 报告 / 日志**。
`synthetic` 路由是故意构造的非法 ID 降级证据，截图按 `dataKind` 明确标注，不冒充真实业务数据。

KERT 侧无 Playwright，补跑 pytest（浏览器画面由 GITS 前端 `/kert-api` 代理嵌入）：

```bash
cd /home/szf/dev/Leibniz-KERT
KERT_BASE_URL=http://127.0.0.1:8107 GITS_BASE_URL=http://127.0.0.1:18080 \
GITS_FRONTEND_URL=http://127.0.0.1:15173 E2E_REQUIRE_SERVICES=1 \
  .venv/bin/python -m pytest tests/e2e -q
```
