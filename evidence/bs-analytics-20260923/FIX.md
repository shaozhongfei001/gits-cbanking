# 经营分析模块「全部分析不可用」修复记录 · 2026-09-23

## 一、现象（改前实测，4/4 页）

| 页面 | 页面 HTTP | analytics 接口 | 页面提示（**如实**） |
|---|---|---|---|
`/analytics/operating-metrics` | 200 | **503**（metrics/orgs/dimensions/periods） | 「无法连接 KERT 分析服务（/kert-api 代理 → 8107）。请先启动：`KERT_ANALYTICS_DUCKDB=…`」 |
`/analytics/monitors` | 200 | **503** | 同上 |
`/analytics/segments` | 200 | **503** | 同上 |
`/analytics/combo-query` | 200 | **503** | 同上 |

⇒ **前端无缺陷**（页面可开、错误文案具名且给出修法），失败在**后端 KERT 分析服务不可用**。

## 二、根因（两条，均已实测）

1. **KERT `.venv` 缺 `duckdb`**：`pyproject.toml:28` 声明 `duckdb>=1.0`，但 **`requirements-lock.txt` 未含**（声明/锁不一致）⇒ 带 `KERT_ANALYTICS_DUCKDB` 起服时进程直接退出（`ModuleNotFoundError`）。
2. **8107 未配置 `KERT_ANALYTICS_DUCKDB`**：`src/kert/application/skills.py:850` 在未配置或库不存在时返回 **`ANALYTICS_UNAVAILABLE`**；`scripts/serve_analytics_api.py:22` 为 fail-closed 必须显式设置。

演示库**本就存在**：`Leibniz-KERT/examples/bank-front-analytics/cb_analytics.duckdb`（13.1 MB）⇒ 不是缺数据。

## 三、处置（环境侧，未改任何仓库文件）

```bash
# ① 补依赖（按 pyproject 声明）
cd /home/szf/dev/Leibniz-KERT && .venv/bin/pip install 'duckdb>=1.0'      # 实装 duckdb 1.5.5

# ② 带 DuckDB 重启 8107（保留原有 env）
KERT_PROFILE=dev KERT_REPO_ROOT=$PWD \
KERT_SKILL_PACKAGES=$PWD/examples/bank-front-skills \
KERT_LIGHTRAG_URL=http://127.0.0.1:9621 KERT_LIGHTRAG_API_KEY=ci-retrieval-key \
KERT_ANALYTICS_DUCKDB=$PWD/examples/bank-front-analytics/cb_analytics.duckdb \
nohup .venv/bin/python scripts/serve_skill_service.py --port 8107 --host 127.0.0.1 \
  --workspace $PWD/bank_front_ws > /tmp/kert-8107-analytics.log 2>&1 &
```

## 四、验证（改后）

| 项 | 结果 |
|---|---|
`/v1/analytics/{screens,orgs,periods,dimensions}` | **200**（改前 503） |
四页正文 | **渲染真实数据**（如机构表「泉州分行」、行业「居民服务和其他服务业 476,255.71」、客群「居民服务和其他服务业 4615.3」） |
`frontend/e2e/analytics.spec.ts` | **5 passed**（改前 4 条 BLOCKED + 1 passed） |
演示库安全 | `analytics_store.py:193` 以 `duckdb.connect(str(path), read_only=self._read_only)` 打开 ⇒ **不写演示库** |

## 五、durability（**必须知悉**）

本修复含**环境态**：8107 若被**不带 `KERT_ANALYTICS_DUCKDB`** 地重启，四条分析会**再次 503**。建议的持久化（属 KERT 维护方）：
1. 把 `duckdb` 补进 **`requirements-lock.txt`**（消除声明/锁不一致）；
2. 在 KERT 的标准启动脚本/Compose 中**默认导出** `KERT_ANALYTICS_DUCKDB`（或提供 `make serve-analytics`）；
3. 在 `docs/` 写一条"分析能力前置"的启动说明（本次手册即 §三）。
