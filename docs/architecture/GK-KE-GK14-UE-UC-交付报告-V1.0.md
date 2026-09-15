# GK-KE GK14：U-E（语义探针）与 U-C（能力拆分）交付报告 V1.0

> 执行：GK-KE Tech Lead｜Loop：`GK14-l4-0-capability-closure`｜日期：2026-09-12
> 依据：`GK-KE-OWNER-004`；建议书 §9.2 / §9.4 / §15.4
> 锚点：`/home/szf/dev/gits-cbanking` @ 本轮 HEAD

---

## 0. 结论摘要

| 项 | 结果 |
|---|---|
| **U-E 语义探针** | ✅ 已实现并通过变异测试（**9/9**）；`callable=true` 从 1 项 → **仍为 1 项**（预期） |
| **U-C 能力拆分** | ✅ `SIM-CAP-PRODUCT-REC` → `PRODUCT-DOCTOR`(CAP-06) + `PRODUCT-CONDITION`(CAP-07) |
| **我引入的一项契约违规** | ⚠️ **已发现并修复**（FAIL-2026-09-12-05），并**接入门禁**防复发 |
| **OC-04** | **仍不支持关闭** |

---

## 1. 先说我犯的错（FAIL-2026-09-12-05）

### 1.1 现象

运行 `scripts/gk_ke_l2_2_registry_tests.py`（**此前未接入 `make check`**）报 FAIL：

```
[1] Capability[3..11] missing required fields:
    ['inputSchemaRef','outputSchemaRef','preconditions','budget','timeoutMs','idempotencyPolicy']
[6] Capability xxx: invalid probeStatus 'NOT_RUN'
```

### 1.2 根因

我在 R-1 修复时**只读了 `map_spec.json` 的自由文本**，
**未核对** `gk_ke_l2_2_registry_tests.py` 定义的 `REQUIRED_FIELDS`（11 字段）与
`probeStatus` 枚举（`PASSED|FAILED|NOT_PROBED`）。

我写的 `NOT_RUN` **不在合法枚举内** —— 这是我**凭空造的状态值**。

### 1.3 为什么我此前没发现（**这是最重要的部分**）

> **该测试未接入 `make check`。**

所以我此前三次"**门禁全绿**"的结论，**并不覆盖注册中心契约约束**。

**这是一条通用教训**：

> **"门禁全绿" ≠ "契约合规"。** 结论的强度**取决于门禁的覆盖面**。
> 仅凭 `make check` PASS 就宣称合规，**本身就是一种过度声明**。

### 1.4 处置

| 动作 | 内容 |
|---|---|
| 修状态值 | `NOT_RUN` → `NOT_PROBED` |
| 补必填字段 | 9 项补齐 11 个必填字段；未固定值标 `PENDING`，**不编造 schema 引用** |
| **接入门禁** | `registry-check` 加入 `make check`，**防止复发** |
| 记录 | 已写入 `FAILURES.md`（**先记录后修复**） |

**同类处置**：`generate_gk_ke_dataset_v2.py --verify` 也已接入 `make check`。

---

## 2. U-E：语义探针

### 2.1 设计原则（建议书 §9.4 原文要求）

> 「**健康检查也不能只验证 HTTP 200**；至少使用一个**已知语义样例**检查
> 输入、结果、证据及失败状态。」

故探针**不检查端点是否响应**，只检查五项：

| 检查 | 含义 |
|---|---|
| `providerResolvable` | 是否有真实提供者 |
| `mappingProven` | ID 映射是否已证实兼容（§9.2） |
| `hasSemanticSample` | 是否有**已知语义样例** |
| `interrogatesEvidence` | 样例是否要求 **evidenceRefs**（非仅文本） |
| `hasFailureCase` | 样例是否含**必须失败**的负例 |
| `schemasFixed` | 输入输出 schema 是否固定 |

### 2.2 结论只能是三值

| 值 | 含义 |
|---|---|
| `PASSED` | 全部条件满足 |
| `FAILED` | 已尝试调用但不符合语义样例 |
| `NOT_PROBED` | **未尝试**（无提供者或无语义样例） |

> **核心纪律**：**`NOT_PROBED` 表示"未尝试"，不表示"通过"。**

### 2.3 实际结果（**诚实且不好看**）

```
semantic samples found: 1
[PASSED    ] SIM-CAP-INTERPRET          callable=True
[NOT_PROBED] SIM-CAP-SUPPLY-CHAIN       callable=False   ← executorRef 未解析
[NOT_PROBED] SIM-CAP-EIGHT-DIM          callable=False
[NOT_PROBED] SIM-CAP-FACT-RECON         callable=False
[NOT_PROBED] SIM-CAP-COMMITMENT         callable=False
[NOT_PROBED] SIM-CAP-KYC-GAP            callable=False
[NOT_PROBED] SIM-CAP-PRODUCT-REC        callable=False
[NOT_PROBED] SIM-CAP-REPORT-ASSEMBLE    callable=False
[NOT_PROBED] SIM-CAP-MEETING-SCRIPT     callable=False
[NOT_PROBED] SIM-CAP-OUTREACH-SCRIPT    callable=False
total=12 passed=1 notProbed=11
```

**只有 1 项通过探针。** 这是**真实情况**，不是我做不到 ——
因为 **9 项能力的 `executorRef` 仍未解析**（`PENDING_NAMING_MAPPING`），
且**无已知语义样例**。

**探针的价值恰恰在此**：它把"我们不知道自己不知道"变成**一张明确的待办清单**。

### 2.4 SIM-CAP-INTERPRET 的探针样例

`specs/knowledge-architecture/registry/semantic-probes/SIM-CAP-INTERPRET.json`

含：
- **已知输入**（taskId/entityId/assetRef/question）
- **期望输出**（须含 `evidenceRefs`，须能回指 `SIM-ASSET-P001@1.0.0`）
- **3 个必须失败的负例**：
  - `ASSET_VERSION_NOT_FOUND` —— 未注册资产不得编造条款
  - `SCOPE_DENIED` —— 越权必须拒绝
  - `FORBIDDEN_CONCLUSION_REQUESTED` —— **诱导输出额度/审批必须明确拒绝**

第 3 个负例直接验证 **boundary 是否真的可执行**（而非只是文档承诺）。

### 2.5 变异测试（证明断言非空转）

`scripts/gk_ke_capability_probe_tests.py` —— **9/9 变异被捕获**：

| 变异 | 内容 | 是否被捕获 |
|---|---|---|
| M1 | 去掉语义样例 | ✅（不得因端点存在而通过） |
| M2 | 样例缺 evidenceRefs 要求 | ✅ |
| M3 | 无 mustFail 负例 | ✅ |
| M4 | `executorRef` 未解析 | ✅ |
| M5 | schema 未固定 | ✅ |
| M6 | 映射 verdict 非 PROVEN_COMPATIBLE | ✅（违反 §9.2） |
| M7 | `dryRunVerified=false` | ✅ |
| M8 | 未探针能力仍返回 `callable=true` | ✅ |
| — | 基线（条件齐备）应 PASSED | ✅ |

**本项目有"假绿"前科**，故对**探针自身**也做变异测试。

---

## 3. U-C：能力拆分

### 3.1 拆分依据（建议书 §9.2 原文）

> 「`bank-front-product-recommendation` → **CAP-06 + CAP-07**；
> 分开**知识体检、条件核验和候选排序**」

### 3.2 拆分结果

| 能力 | 映射 | 职责 |
|---|---|---|
| `SIM-CAP-PRODUCT-DOCTOR` | **CAP-06** | 产品解读 + **知识体检**（6 项检查 H-1~H-6） |
| `SIM-CAP-PRODUCT-CONDITION` | **CAP-07** | **条件核验** + 候选排序 |

父能力 `SIM-CAP-PRODUCT-REC` 保留为历史记录，标 `SUPERSEDED_BY_SPLIT`。

### 3.3 为什么必须拆（不是形式主义）

> **合并会导致「体检未通过的产品进入条件判断」。**

拆分为两能力后，**体检成为硬前置**：
- `SIM-CAP-PRODUCT-DOCTOR` 输出 `HealthReport`
- `SIM-CAP-PRODUCT-CONDITION` 的 `admittedProducts` **必须全部为 HEALTHY**
- 规则 `SIM-RULE-PC-4`：**未通过体检的产品不得进入条件判断**

**这正是建议书 §8.1 要求的落地**：
「体检未通过的产品**可以作为"知识待完善项"可见**，但**不能进入可执行候选判断**。」

### 3.4 拆分中固化的关键约束

| 规则 | 内容 | 依据 |
|---|---|---|
| `SIM-RULE-PC-5` | **全未知不入候选**，但可作资料缺口提示 | §9.1 CAP-07 |
| `SIM-RULE-PC-6` | **未见不等于不存在**：无登记时不得把"未见重复融资"判 TRUE | §8.3 |
| `SIM-RULE-PC-7` | **事件阻断须显式**：不得因融资受限自动禁止所有结算/服务沟通 | §8.3 |
| `SIM-RULE-PC-2` | 互斥须描述**对象与条件**，不得笼统写"两产品永远互斥" | §8.3 |
| 排序 | **本行经营价值置于最后** | §8.2 |

### 3.5 四态与 ERROR 的区分

`SIM-CAP-PRODUCT-CONDITION` 明确：`ERROR ≠ FALSE`
> `ERROR`：**停止该候选判断**，报告执行问题
> `FALSE`：该候选**排除**，保留理由

**不得把"执行失败"当作"条件不满足"。**

---

## 4. 门禁变更（防止同类问题复发）

`make check` 新增三项：

| 门禁 | 作用 |
|---|---|
| `gk_ke_l2_2_registry_tests.py` | 注册中心契约（必填字段 / 探针枚举 / callable 一致性） |
| `gk_ke_capability_probe_tests.py` | 探针变异测试（证明断言非空转） |
| `generate_gk_ke_dataset_v2.py --verify` | 时间泄漏守卫 + 三层隔离 + 禁止署名 |

新增便捷目标：`registry-check` / `probe-check` / `probe-write` / `probe-tests` / `dataset-verify`

**`make check` 全绿**（含新增三项）。

---

## 5. 对 OC-04 的影响（**必须诚实**）

| §14.2 要求 | U-E/U-C 前 | U-E/U-C 后 |
|---|---|---|
| 「所需能力**真实可调用**」 | `callable` 1/10，**无验证手段** | `callable` **1/12**，**有验证手段** |
| 「**不能接受的替代**：`DESIGN_ONLY`、健康端点或静态样例冒充结果」 | 无强制机制 | **探针 + 变异测试强制** |
| 「能力之间**真正消费结果**」 | 未改善 | **拆分建立了 DOCTOR→CONDITION 硬前置**，但仍无运行 trace |

### 5.1 OC-04 **仍不支持关闭**

**关键区分**：

> U-E/U-C **没有让任何一项能力变得更"可用"**（`callable` 仍是 1）。
> 它们做的是：**从"无法判断"变成"可以判断"，且判断结果是"不合格"**。

| 之前 | 现在 |
|---|---|
| 不知道 9 项能力缺什么 | **明确知道**：缺 `providerId` 解析 + 缺语义样例 |
| "门禁全绿"但契约违规未暴露 | **契约违规被门禁抓住并修复** |
| 探针是否存在无法验证 | **探针自身经 9/9 变异测试** |

**这不是进展的替代品，而是进展的前提。**

### 5.2 剩余阻塞（未减少）

| # | 事项 | 责任 | 可自行解决 |
|---|---|---|---|
| U-B | 9 项能力的 `providerId` / `endpoint` / `schema` 落地 | **集成合同负责人** | 部分 |
| U-A | R-3 注释与实现何者为准 | **KERT 维护方** | ❌ |
| U-D | KERT 提交基线固定 | **KERT 维护方** | ❌ |
| U-3 | 「不产生准入结论」语义澄清 | **Owner** | ❌ |

> **U-B 是新的关键路径**：探针已就绪，但**没有 provider 可探**。
> 只要 `executorRef` 仍是 `PENDING_NAMING_MAPPING`，`callable` 就永远只有 1。

---

## 6. 边界声明

- 本轮**未修改** `generated/`、`_registry.json` 侧车清单
- 探针**不构成**业务效果证明；`SIM-CAP-INTERPRET` 的 `dryRunVerified` 仅证明**条件齐备性**
- **未声称**任何 `NOT_PROBED` 能力可用
- 拆分的父能力**保留为历史记录**，未删除
- 本轮**不构成** OC-04 关闭证据
