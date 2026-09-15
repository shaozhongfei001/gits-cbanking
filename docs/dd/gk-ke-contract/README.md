# GK-KE-CONTRACT-V1.0 使用说明

本包是 GITS—KERT 知识工程系统群的项目契约与模拟数据交付，包含总契约、8 份分合同、14 份 JSON Schema、14 个正例、28 个 Schema 负例、36 项系统验收计划，以及固定场景造数与离线校验工具。

从 `00_项目总契约.md` 开始，依次阅读 contracts/C01–C08。`CONTRACT_INDEX.json` 是本包索引，不能覆盖现有项目 `CONTRACT_INDEX.yaml`。所有 Schema 使用 `gk-ke/v1` 候选命名空间，当前模拟交换剖面要求 simulationOnly=true。

## 状态与可用范围

这是可审阅、可拆分开发的设计合同；没有实施银行服务、GITS/KERT UI、Kuzu 或 LightRAG 集成。正例表示交换对象结构合法，有些是模拟审核/发布状态夹具，不表示已获得真实审核或能力运行探针通过。正式合同正文比最小交换 Schema 的覆盖面更广，Schema 合法只是前置检查；接入时需 L0 补全映射、传输包络、身份授权和服务验证。

模拟能力 `SIM-CAP-INTERPRET` 的 productionProbePassed=false、status=SIMULATED_CONTRACT_ONLY；只能用于合同/离线验证，不得让正式执行器把“示例存在”当作“能力 ready”。真实发布门禁还必须检查运行探针、领域认定、签名权限、时态及全部 C03 条件。本包示例中的 APPROVED/PUBLISHED 均有 simulationOnly=true，真实批准状态为 NOT_PERFORMED。

## 运行环境

Python 3.10+；使用独立虚拟环境，不向系统 Python 安装依赖。数据生成只使用标准库；Schema 验证依赖 jsonschema==4.25.1。首次安装需要包源访问，可在开发环境缓存依赖后离线安装。

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r tools/requirements.txt
.venv/bin/python tools/validate_package.py
```

如需重建固定模拟数据及候选样例，在包根目录执行：

```bash
.venv/bin/python tools/build_simulation.py
.venv/bin/python tools/validate_package.py
.venv/bin/python tools/gk_ke_contract_examples.py
.venv/bin/python tools/verify_simulation.py
```

- `build_simulation.py`：重建固定模拟数据（账务/余额/图/文档 hash），可复现。
- `validate_package.py`：125+ 项离线自检（Schema 正负例、跨对象、数据 hash、**MANIFEST 顶层自校验**）。
- `gk_ke_contract_examples.py`：20 正例 / 40 负例 Schema 对拍。
- `verify_simulation.py`：独立复算（账务恒等式、引用闭包、C001 日均、C002 跨币种拒绝）。

> 说明：本包 Schema 以仓库权威源 `specs/gk-ke/v1/` 为准（20 Schema）。`build_contract_examples.py` 是 V1.0 时期仅覆盖 14 Schema 的历史生成器，已废弃，不再作为本版本的再生成入口。重新生成后原交付 MANIFEST 不再代表新版本，需重新封包并记录新版本。

## 数据与检验

`simulation/seed_scenarios.json` 及 documents 为本次助手编写的固定虚构内容，构建脚本没有再调用云模型。程序派生主外键、交易、借贷分录、每日余额、图关系和校验 hash。未用真实客户姓名、账户号码或真实政策。

`simulation/oracles/` 为受测模型禁止读取的测试真值目录。日均独立公式与逐日余额复算相互校验；产业关系/业务标签仍需专家验证，不能因模型自评而宣称金融业务真值。

`acceptance/package_self_check.json` 是本次实际离线作者自检；`acceptance/验收矩阵.csv` 是待开发/待测试的系统验收计划。自检条目含文件哈希、Schema 与有限跨对象校验，不等同于相同数量的独立系统测试。

## 哈希剖面

原文/文件哈希：SHA-256 原始字节。结构化合同 payloadHash、planHash 与 release artifactRefs.hash：JSON 键递归按字典序排列、UTF-8、ensure_ascii=false、紧凑分隔符；输入字符串要求 NFC，数组按合同语义顺序；数值金额一律字符串，不允许 NaN/Infinity。此为本包局部规范，未声明 RFC 8785 合规。跨 Java/Python 实现必须保存黄金规范化字节并做同值测试。

planHash 排除 planId 和 planHash，自身其余字段均纳入；现有合同如使用另一规范必须经适配对齐。Release 的审批 hash 只针对 payload，签名/审批引用在外层，避免自引用循环。

## 交付边界

用户指定的 Kuzu 0.11.3 仅为模拟候选，未下载安装；LightRAG 未锁定实际 Spike 版本，不提供未经测试的安装命令或性能结论。正式实现请从 C08 的 L0 开始，保留原合同和门禁。
