# L2｜KERT 元模型适配补丁方案（候选材料）

> 状态：`CANDIDATE_NOT_EFFECTIVE（**不涉及任何写入**；合入权在 KERT 维护方）`｜依据：`Owner 决议 2026-09-21（准备项 5）`｜**本方案不涉及任何写入**，合入权在 KERT 维护方

## 1. 义务规模（只读统计）

- 总义务：**86**

  - `src/kert`：50
  - `examples/bank-front-knowledge-maps`：33
  - `specs/kert-openapi-v1.yaml`：3
  - W3_CONSUMER_SWITCH：64
  - W3_KERT_ASSETS：19
  - W2_SPLIT：3

## 2. 候选变更（逐条含依据与前置）

| # | 目标 | 变更 | 依据 | 所需前置 |
|---|---|---|---|---|
| 1 | `90_control/ontology/` | 改放「L1 副本 + L2 本体」 | 执行计划 §84 | KERT 维护方写权限 |
| 2 | `ontology_reference.json` | → `authorityEntity`（公共语义实体）+ 新钉值 | 执行计划 §84 | KERT 维护方 |
| 3 | `ontology_assets.py` | role 扩：PUBLIC / KERT / GITS-EXTERNAL | 执行计划 §84 | KERT 维护方 |
| 4 | `物化链路` | 重跑，**校验先于产出** | 执行计划 §84 | KERT 维护方 |

## 3. 验证材料

- 只读证据快照：待改文件清单 + sha256（供维护方比对）
- 物化链路：**校验先于产出**（先跑校验，再产出；校验红则不产出）
- KERT 侧消费者扫描：64 项 W3_CONSUMER_SWITCH 的引用面清单

## 4. 阻塞与写入声明

- 阻塞：`['KERT 维护方写权限（未确认）']`
- 写入声明：{"statement": "本轮**未对 KERT 侧做任何写入**（只读分析 + 补丁方案 + 验证材料）", "verified_by": "git 状态（KERT 仓）与文件 mtime 快照", "kert_root": "/home/szf/dev/Leibniz-KERT"}

## 5. 边界（不得越过）

- **不得**写入 KERT 仓（本环境只读）；
- **不得**发布新 IRI（D3 未签）；
- 合入须由 **KERT 维护方**执行，并**校验先于产出**。
