# DKWS 文件目录型数据知识服务模拟平台

按 `specs/文件目录型数据知识服务模拟平台_详细需求与详细设计_V1.0.md`（`DKWS-SPEC-001`）
实现的**可运行的**文件目录型数据知识服务模拟平台。

> 当前版本：`0.1.0` · 状态：**可运行演示**（simulation mode）
> 关联 Loop：`loops/P24-dkws-platform`

## 设计要点

- **五层工作区**：`01_raw` / `02_work` / `03_core` / `04_serve` / `90_control`
- **契约化 Markdown**：每个文件 = YAML frontmatter（结构化字段）+ 固定标题正文
- **schema 合同注册**：`dkws/schemas.py` 注册 §9 全部 20+ 文件类型，`dkws/contract.py`
  提供 frontmatter 解析、字段类型化、枚举/必填/条件/默认、DSL 受限校验、标题校验
- **确定性**：同输入同输出（稳定切片、投影幂等重建、逻辑哈希）
- **人工责任边界**：系统禁止为 OWNER/INDEPENDENT_QA 自动生成批准决定
- **只读生成物**：工作区生成物只读；返回路径一律工作区相对路径，不承载宿主绝对路径

## 快速开始

```bash
# 无需额外依赖（stdlib + click + pyyaml，pyarrow/fastapi 为可选项）
PYTHONPATH=src python -m dkws --help

# 1) 初始化工作区
PYTHONPATH=src python -m dkws init ./demo-ws

# 2) 接入原始数据
PYTHONPATH=src python -m dkws --root ./demo-ws ingest \
    --source ./some_dir --domain knowledge --idempotency-key demo-1

# 3) 文档登记 + 规范化切片
PYTHONPATH=src python -m dkws --root ./demo-ws docs DOC-1 \
    --source ./doc.md --domain knowledge

# 4) 生成知识候选、检测冲突、记录人工审核决定
PYTHONPATH=src python -m dkws --root ./demo-ws knowledge.candidate --domain knowledge
PYTHONPATH=src python -m dkws --root ./demo-ws knowledge.decide --decision-id DC-1 \
    --object-ref ENT-x --object-ref STMT-y --decision APPROVE \
    --decided-by alice --role OWNER

# 5) 发布 + CURRENT
PYTHONPATH=src python -m dkws --root ./demo-ws publish --domain knowledge --approval DC-1

# 6) 投影 + 服务查询
PYTHONPATH=src python -m dkws --root ./demo-ws projection.build --service svc \
    --domain knowledge --version 1.0.0
PYTHONPATH=src python -m dkws --root ./demo-ws service.query --domain knowledge
```

## 测试

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

覆盖：契约校验（合法通过/非法拒绝）、工作区、状态机、接入/幂等、切片、知识候选/冲突/审核、
发布/回滚、投影可重建、服务 JSON 通则、安全（路径穿越/敏感日志）、性能、E2E 黄金场景。

## 目录

```
src/dkws/
  contract.py    契约化 Markdown 框架（frontmatter/schema/DSL/标题）
  schemas.py     全部文件类型 Schema 注册
  state.py       任务/知识资产/发布状态机
  workspace.py   五层工作区 + meta + 路径安全
  hashing.py     SHA-256
  logging.py     结构化日志 + 敏感信息脱敏
  mdio.py        契约化 MD 读写（原子）
  ingest.py      raw 接入流水线（P2）
  docs.py        文档规范化 + 稳定切片（P4）
  knowledge.py   候选/冲突/审核决定（P5）
  publish.py     发布 + Release + CURRENT + 回滚（P6）
  projection.py  Parquet/CSV/图/规则投影（P7）
  service.py     CLI 服务：query/search/rule（P8）
  http_api.py    可选 HTTP API（P8，需 fastapi）
  cli.py         命令行入口
  trace.py       需求ID -> 验收矩阵（P0）
tests/
  test_contract.py / test_pipeline.py / test_projection.py
  test_e2e.py / test_security_perf.py / test_seeds.py
seeds/           合法 + 非法样例（scripts/make_seeds.py 生成）
scripts/make_seeds.py
```

## 约定

- 生成物只读、不承载宿主绝对路径、SHA-256 哈希、确定性重建。
- HTTP/Parquet 为可选项，未安装时自动降级 CSV / 明确报错。
- 本平台为**模拟/演示**（simulation），不写生产、不迁移、不连真实 RAG/GraphDB/向量库。