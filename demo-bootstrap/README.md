# GITS + KERT 演示环境数据包与重建脚本

把本机的**测试 / 验证 / 演示数据**盘点、导出，并可在另一台开发机上**一键重建演示环境**。

- 导出：`./export_demo_data.sh`（源机执行，产物在 `bundle/`，当前 **931 个文件 / 72M**）
- 重建：`./init_demo_env.sh --bundle <数据包目录>`（目标机执行）

---

## 1. 快速开始

**源机（导出数据）**
```bash
cd /home/szf/dev/gits-cbanking/demo-bootstrap
./export_demo_data.sh                 # 完整导出到 ./bundle
./export_demo_data.sh --tarball       # 额外打包 gits-kert-demo-bundle-<日期>.tar.gz
./export_demo_data.sh --slim          # 精简：剔除 90_control/jobs 历史执行结果（省 ~6.6M）
```

**目标机（重建环境）**
```bash
git clone <gits-cbanking> && git clone <Leibniz-KERT>   # 两仓需在同一父目录下
cd gits-cbanking/demo-bootstrap
./init_demo_env.sh --bundle /path/to/bundle
```

两仓路径可用环境变量覆盖：`GITS_ROOT` / `KERT_ROOT`。

---

## 2. 数据资产总览（盘点结果）

### 2.1 KERT（Leibniz-KERT）

| 数据资产 | 规模 | 是否入库 git | 说明 |
|---|---|---|---|
| `bank_front_ws/` 工作区 | 369 文件 / 13M | **否（gitignored）** | 五层结构：`01_raw`（空）/ `02_work` 候选 / `03_core` 权威知识源 / `04_serve` 投影层 / `90_control` 控制面 |
| ├ `03_core/customer/version=2026.09.07.1/` | 58 文件 / 268K | 否 | 19 实体 + 17 关系 + 21 片段，权威知识源 |
| ├ `04_serve/customer_knowledge/version=.../` | 6 parquet + graph / 5.4M | 否 | **可确定性重建**的投影层 |
| └ `90_control/` | 约 51 文件 + 48 个 JOB 目录 / 7.1M | 否 | `catalog`（7 份知识地图）、`schema/route_policy.json`、`decisions`（36 条）、`jobs` |
| `data/product_knowledge_graph.kuzu` | 31M | **否（gitignored）** | Kuzu 产品知识图库，SP-15 原型；**`src/` 下无代码运行时读取**，可由脚本重建 |
| `examples/bank-front-analytics/cb_analytics.duckdb` | 13M | **否（gitignored）** | DuckDB 分析库 7 张表；**设了 `KERT_ANALYTICS_DUCKDB` 但库缺失 ⇒ KERT 启动失败** |
| `examples/bank-front-analytics/seed/*.csv` | 7 文件 / 6.1M | 是 | DuckDB 造数输入；**上游生成器 `scripts/gen_seed_data.py` 本仓缺失，必须随包带走** |
| `examples/product_demo/inputs/` | 3 文件 / 16K | 是 | product.parquet + 产品手册/政策 md |
| `examples/output/` | 11 文件 / 2.1M | 是 | 演示产出：CRM 主档、访前报告、供应链图谱 HTML |
| `90_control/runtime/runtime.db` SQLite | — | — | **本机不存在**（worker 未启用持久化）；目标机设 `KERT_RUNTIME_STORE_ENABLED=true` 后自动建库 |
| LightRAG / 向量数据 | — | — | 外部服务，零落盘；本仓唯一向量落盘是 `vectors.parquet`（21 行 × 64 维，确定性哈希嵌入） |

**投影层 6 个 parquet 明细**（`version=2026.09.07.1`，由 `03_core` 经 `ProjectionBuilder` 生成，确定性可重建）

| 文件 | 行数 | 说明 |
|---|---|---|
| `entities.parquet` | 19 | 客户/对手方实体（含 22 个 `x_*` 透传字段） |
| `relations.parquet` | 17 | 供应链/股权关系，保留溯源字段 |
| `segments.parquet` | 21 | 3 客户 × 7 条 KI 片段 |
| `vectors.parquet` | 21 | 64 维确定性哈希嵌入，无需外部模型 |
| `statements.parquet` | 0 | 空表（源目录不存在） |
| `rules.parquet` | 0 | 空表（源目录不存在） |
| `graph`（Kuzu） | 19 节点 / 17 边 | 由 entities+relations 构建，`kuzu_builder.py` |

### 2.2 GITS（gits-cbanking）

| 数据资产 | 规模 | 说明 |
|---|---|---|
| **关系数据库** | — | **H2 内存库** `jdbc:h2:mem:gitskno`，无落盘文件；每次启动由 Flyway + seed 重建 |
| Flyway 迁移脚本 | 45 文件 / 272K | **H2 24 个（V001–V024）、MySQL 21 个** |
| `scenario/seed/` 场景种子包 | 285 文件 / 2.6M | 20 个子目录：主数据/银行数据/知识资产/交互/UI 状态/API fixture/GK-KE 仿真集 |
| `specs/knowledge-architecture/` | 171 文件 / 1.1M | **启动时由 `KnowledgeSnapshotLoader` 全量读进内存**，是运行时数据不是文档 |
| `specs/product-knowledge/` | 28 文件 / 352K | `product-taxonomy.yaml` 是产品中心分类骨架**权威源**，缺失 ⇒ 端点 503 |
| `specs/data/` | 9 文件 / 3.0M | `oracle-seed-claims` 2505 条等，仅 `MechanismE2eIT` 读取 |

**Flyway 种子脚本**（灌溉演示业务数据，顺序敏感）

| 脚本 | 内容 |
|---|---|
| V014 | 华东精工经营闭环：1 经营案例 + 3 承诺 + 5 任务 + 3 商机 |
| V016 | 5 人工门禁 + 3 CRM 写回 + 5 审计追踪 |
| V017 | 3 机会信号 + 2 KYC 缺口档案 |
| V018 | 客户主档 `CUST-CORP-0001/0002/0003`（一切业务数据的外键根） |
| V021 | 12 条对公产品知识版本（6 个产品域） |
| V022 | `CUST-CORP-0002~0006` 经营案例 + 12 商机 |
| V023 | **演示主客户 `CUST-CORP-0003`** 补全 + 商机信号 |

---

## 3. 目录结构

```
demo-bootstrap/
├── README.md                    本文档
├── export_demo_data.sh          源机导出（生成 bundle/ + MANIFEST.json）
├── init_demo_env.sh             目标机一键重建（编排以下步骤）
├── lib/common.sh                路径约定、日志、校验公共库
├── steps/
│   ├── 00-prereq.sh             环境前置检查（两仓、Python 依赖、工具链）
│   ├── 10-restore-kert-workspace.sh  恢复 KERT 工作区（restore / regen）
│   ├── 20-build-kert-graph.sh        Kuzu 产品知识图库
│   ├── 30-build-analytics.sh         DuckDB 分析库（含造数 CSV 补齐）
│   ├── 40-verify-gits-data.sh        GITS 数据校验（含 manifest sha256 逐文件比对）
│   └── 50-smoke.sh                   冒烟：输出数据资产状态总表
└── bundle/                      导出产物（931 文件 / 72M）
    ├── MANIFEST.json            数据清单 + 每项 sha256
    ├── kert/                    bank_front_ws、kuzu、duckdb、seed CSV、demo 输入/产出
    └── gits/                    scenario-seed、db-migration、knowledge-architecture、
                                 product-knowledge、specs-data
```

---

## 4. 恢复策略：restore vs regen

| 策略 | 触发 | 做法 | 适用 |
|---|---|---|---|
| **restore**（默认） | bundle 中有对应数据 | 从 bundle 拷回 | 与源机逐字节一致，演示效果可复现；**推荐** |
| **regen** | `--regen` 或 bundle 缺数据 | 调用 KERT 脚本从源重新生成 | 不依赖数据包，可验证生成链路；版本目录日期会变 |

regen 依赖的源命令（脚本已封装）：
```bash
kert init --workspace <ws> --force
kert provision -w <ws> -s examples/bank-front-knowledge-maps --init
python scripts/seed_customer_knowledge.py -w <ws>
python scripts/graph/init_product_knowledge_graph.py
python scripts/build_analytics_duckdb.py
```

---

## 5. 已知红线与注意事项

1. **MySQL 方言缺 V014 / V015 / V016**（H2 有 24 个脚本，MySQL 只有 21 个）。
   若目标机用 MySQL，演示数据会缺经营案例、承诺、任务、商机、人工门禁、审计追踪。
2. **GITS 存在两套客户 ID**：`scenario/seed` 的 JSON 用 `CUST-001`，Flyway 与硬编码分支用 `CUST-CORP-0001`。迁移脚本需显式对齐。
3. **`CUST-CORP-0004~0006` 的 customer 行只在 Java 硬编码分支插入**。若设置 `SCENARIO_DATA_ROOT` 走 V1.1 文件分支，这 3 家客户主档不会落库，经营案例/商机将指向不存在的客户。
4. **`gits.product-center.section-dir` 与 `gits.product-knowledge.snapshot-dir` 默认空** ⇒ 产品中心章节/产品解读走**受控失败 503**，绝不本地兜底。要演示产品章节需指向 KERT 侧投影目录。
5. **KERT `route_policy.json` 缺失 ⇒ `defaultDecision=DENY` ⇒ 所有技能被拒**。步骤 10 已断言该文件存在。
6. **`examples/bank-front-analytics/seed/*.csv` 的上游生成器本仓缺失**，CSV 必须随包带走，否则无法 regen DuckDB。
7. **`90_control/jobs/JOB-SKILL-*/result.json`**（45 个 × 130–150KB）是历史执行结果，不影响运行，`--slim` 可剔除。

---

## 6. 服务启动（数据就绪后）

```bash
# KERT 技能服务（GITS 默认指向 8107）
cd Leibniz-KERT
KERT_PROFILE=dev KERT_REPO_ROOT=$PWD \
KERT_SKILL_PACKAGES=$PWD/examples/bank-front-skills \
  .venv/bin/python scripts/serve_skill_service.py --port 8107 --host 127.0.0.1 \
  --workspace $PWD/bank_front_ws

# GITS 后端（H2 内存库，Flyway V001–V024 自动建表 + 灌种子）
cd gits-cbanking && mvn -q -pl apps/api -am spring-boot:run

# GITS 前端
cd gits-cbanking/frontend && npm ci && npm run dev
```

演示模式关键开关（`apps/api/src/main/resources/application.yaml`）：
`gits.seed.enabled=true`、`engagement.llm.mode=mock`、`engagement.crm.mode=logging`、
`gits.product-center.is-demo=true`。

---

## 7. 校验

`init_demo_env.sh` 结束时输出数据资产状态总表；`40-verify-gits-data.sh` 会按
`scenario/seed/manifest.json` 对 **256 个文件逐文件比对 sha256**，报告缺失与不符。

---

## 8. 已实测验证（2026-10-13）

| 验证项 | 方法 | 结果 |
|---|---|---|
| 导出完整性 | `export_demo_data.sh` | 931 文件 / 72M，MANIFEST 12 项全部登记 |
| tar 包完整性 | `tar -tzf` | 1109 条目，MANIFEST / kuzu / duckdb / route_policy 均在 |
| seed 包摘要 | 按 `manifest.json` 逐文件 sha256 | **256 文件，缺失 0，不符 0** |
| **regen 链路**（init→provision→seed） | 在 `/tmp` 临时工作区实跑 | init 建 13 目录；provision 产出 12 份控制面；seed 生成投影层，**Kuzu 指纹 `f4adfb4c…` 与本机一致** |
| regen vs 本机差异 | 文件数对比 | 186 vs 369，差异全部是 `90_control/jobs` 历史执行痕迹；**投影层 9 个文件完全一致** |
| restore 可恢复性 | bundle → `/tmp` 解包 | 369 文件，五层结构 + 关键文件齐全 |

**实测发现的缺陷（已在脚本中修复）**：`src/kert/cli/main.py` 没有
`if __name__ == "__main__": app()` 块，且 `kert` 未安装进 venv，
导致 `python -m kert.cli.main` **静默无操作**（不报错也不建目录）。
脚本改用 `python -c "from kert.cli.main import app; app()"` 函数调用（`lib/common.sh: kert_cli`）。
