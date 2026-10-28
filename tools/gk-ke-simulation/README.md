# gk-ke-simulation（CR-07 模拟数据工厂）

自包含的离线模拟银行数据工厂，对应合同 CR-07《模拟数据合同》与验收 T30–T33。
本包为候选实现的受控搬迁（vendored），来源：
`GK-KE-CONTRACT-V1.0/`（`tools/build_simulation.py`、`tools/validate_package.py`、
`simulation/`、`schemas/`、`examples/`）。

## 边界

- 纯离线、确定性；不调用任何模型、不访问网络、不写真实数据库。
- 全部产物 `simulationOnly=true`，合成 ID 一律 `SIM-` 前缀。
- `simulation/oracles/` 是独立评测真值，禁止进入任何检索语料。
- 固定种子（`seed_scenarios.json`、`source_catalog.json`、`documents/`）为人工创作输入；
  派生产物（`tables/`、`graph/`、`oracles/`、`dataset_manifest.json`）由工厂重写。

## 用法（从仓库根执行）

```bash
python3 tools/gk-ke-simulation/build_simulation.py      # 确定性重写派生产物
python3 tools/gk-ke-simulation/validate_package.py      # 离线自检（T30/T31）
```

自检报告写入 `reports/package_self_check.json`（不入库）。
依赖：Python 3.10+、`jsonschema`（仅校验器使用）。

## 与候选包的差异

1. 包根由候选的 `parents[1]` 校正为脚本所在目录，搬迁后层级自包含。
2. 自检报告由候选的 `acceptance/package_self_check.json` 改写到包内 `reports/`。
3. 删除仓库级 `CONTRACT_INDEX.json` 合同文档哈希检查（该检查由 GITS 仓库 `make check` 承担）。
4. `examples/` 作为本地校验夹具一并 vendored（`registry_snapshot.json` 的 `contentRef`
   与 schema 正/负例检查依赖它）；不修改任何固定种子。
